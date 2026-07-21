#!/usr/bin/env node
/**
 * docling-mcp — Bob MCP server
 *
 * Exposes two tools so that Bob can scan any document with Docling
 * whenever you paste a file path into chat:
 *
 *   scan_document          → returns Markdown (default, human-readable)
 *   scan_document_to_json  → returns structured JSON (DoclingDocument)
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { promisify } from "node:util";
import { z } from "zod";

const execFileAsync = promisify(execFile);

// ── Path to the venv Python that has Docling installed ──────────────────────
const MODULE_DIR =
  new URL(".", import.meta.url).pathname.replace(/docling-mcp\/$/, "") +
  "Module 8 - OCR Engine with Docling";

const VENV_PYTHON =
  process.env.DOCLING_PYTHON ??
  `${MODULE_DIR}/Module 8 - OCR Engine with Docling/.venv/bin/python3`;

// Resolve the actual python path regardless of spacing in directory names
const PYTHON = process.env.DOCLING_PYTHON ?? findPython();

function findPython(): string {
  // The venv lives inside the module directory next to this server
  const serverDir = new URL(".", import.meta.url).pathname;
  // serverDir = …/Module 8 - OCR Engine with Docling/docling-mcp/build/
  const venvPython = serverDir
    .replace(/docling-mcp\/build\/?$/, "")
    .replace(/\/$/, "") + "/.venv/bin/python3";
  return venvPython;
}

// ── Inline Python scripts ───────────────────────────────────────────────────

const CONVERT_TO_MD = `
import sys, warnings
warnings.filterwarnings("ignore")
from docling.document_converter import DocumentConverter
path = sys.argv[1]
converter = DocumentConverter()
result = converter.convert(path)
print(result.document.export_to_markdown())
`;

const CONVERT_TO_JSON = `
import sys, json, warnings
warnings.filterwarnings("ignore")
from docling.document_converter import DocumentConverter
path = sys.argv[1]
converter = DocumentConverter()
result = converter.convert(path)
print(json.dumps(result.document.export_to_dict(), ensure_ascii=False, indent=2))
`;

// ── Helper ──────────────────────────────────────────────────────────────────

async function runDocling(
  script: string,
  docPath: string
): Promise<{ stdout: string; stderr: string }> {
  const python = PYTHON;

  if (!existsSync(python)) {
    throw new Error(
      `Docling Python not found at: ${python}\n` +
        `Set the DOCLING_PYTHON env var to the correct python executable, e.g.:\n` +
        `  export DOCLING_PYTHON=/path/to/.venv/bin/python3`
    );
  }

  return execFileAsync(python, ["-c", script, docPath], {
    maxBuffer: 50 * 1024 * 1024, // 50 MB — large documents can be big
    timeout: 300_000,             // 5 min max
  });
}

// ── Server ──────────────────────────────────────────────────────────────────

const server = new McpServer({
  name: "docling-mcp",
  version: "0.1.0",
});

// Tool 1: scan_document → Markdown
server.tool(
  "scan_document",
  "Scan / convert a document (PDF, DOCX, PPTX, XLSX, image, HTML, EPUB …) " +
    "at the given local file path using Docling and return the full content as Markdown. " +
    "Call this whenever the user mentions or pastes a document file path.",
  {
    path: z
      .string()
      .describe(
        "Absolute or relative path to the document file. " +
          "Supports PDF, DOCX, PPTX, XLSX, PNG, JPEG, TIFF, HTML, EPUB, and more."
      ),
  },
  async ({ path: docPath }) => {
    if (!existsSync(docPath)) {
      return {
        content: [
          {
            type: "text",
            text: `❌ File not found: ${docPath}\nPlease check the path and try again.`,
          },
        ],
        isError: true,
      };
    }

    try {
      const { stdout, stderr } = await runDocling(CONVERT_TO_MD, docPath);
      const warning = stderr ? `\n\n---\n_Docling warnings:_ ${stderr.trim()}` : "";
      return {
        content: [
          {
            type: "text",
            text: stdout.trim() + warning,
          },
        ],
      };
    } catch (error) {
      const msg =
        error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text", text: `❌ Docling error:\n${msg}` }],
        isError: true,
      };
    }
  }
);

// Tool 2: scan_document_to_json → structured JSON
server.tool(
  "scan_document_to_json",
  "Scan a document at the given local file path using Docling and return " +
    "the full structured DoclingDocument as JSON (pages, tables, figures, reading order). " +
    "Use this when you need structured data rather than readable Markdown.",
  {
    path: z
      .string()
      .describe("Absolute or relative path to the document file."),
  },
  async ({ path: docPath }) => {
    if (!existsSync(docPath)) {
      return {
        content: [
          {
            type: "text",
            text: `❌ File not found: ${docPath}`,
          },
        ],
        isError: true,
      };
    }

    try {
      const { stdout, stderr } = await runDocling(CONVERT_TO_JSON, docPath);
      const warning = stderr ? `\n\n// Docling warnings: ${stderr.trim()}` : "";
      return {
        content: [
          {
            type: "text",
            text: stdout.trim() + warning,
          },
        ],
      };
    } catch (error) {
      const msg =
        error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text", text: `❌ Docling error:\n${msg}` }],
        isError: true,
      };
    }
  }
);

// ── Start ───────────────────────────────────────────────────────────────────

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("docling-mcp server running on stdio");
  console.error(`Using Python: ${PYTHON}`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
