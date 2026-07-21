# Module 8 — OCR Engine with Docling: Complete Setup Guide

This guide lets anyone reproduce the full setup from scratch on their own machine.  
You will end up with:

1. **Docling** installed in a local Python virtual environment  
2. **Six Python example scripts** you can run directly  
3. **A custom Bob MCP server** (`docling-mcp`) that auto-scans any document you mention in chat

---

## Prerequisites

| Tool | Minimum version | Check command |
|------|----------------|---------------|
| Python | 3.10 | `python3 --version` |
| Node.js | 18 | `node --version` |
| npm | 9 | `npm --version` |

Install links if missing:
- Python → https://www.python.org/downloads/
- Node.js → https://nodejs.org

---

## Directory layout (end state)

```
Module 8 - OCR Engine with Docling/
├── SETUP_GUIDE.md          ← this file
├── README.md               ← quick-reference
├── requirements.txt
├── .venv/                  ← Python venv with Docling (created in Step 1)
├── examples/
│   ├── 00_verify_install.py
│   ├── 01_convert_pdf.py
│   ├── 02_convert_image_ocr.py
│   ├── 03_convert_docx.py
│   ├── 04_batch_convert.py
│   ├── 05_export_json.py
│   └── 06_cli_demo.sh
└── docling-mcp/            ← Bob MCP server (Node.js/TypeScript)
    ├── package.json
    ├── tsconfig.json
    ├── src/
    │   └── index.ts
    └── build/
        └── index.js        ← compiled output (created in Step 3)
```

> **Adapt paths:** wherever you see `/YOUR/PATH/TO/Module 8 - OCR Engine with Docling`,
> replace it with the actual absolute path on your machine.  
> On macOS/Linux: `pwd` inside the module directory gives you that path.

---

## Step 1 — Install Docling (Python venv)

```bash
# Move into the module directory
cd "Module 8 - OCR Engine with Docling"

# Create the virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# Upgrade pip, then install Docling
pip install --upgrade pip
pip install docling
```

> **Note:** `pip install docling` downloads ~200 MB of ML models on first run.  
> Subsequent runs use the cached models.

### Verify the installation

```bash
python examples/00_verify_install.py
```

Expected output:
```
Python version : 3.x.x ...
Docling version: 2.x.x.x

✅  Docling is installed correctly!
✅  DocumentConverter import OK
```

---

## Step 2 — Python example scripts

All scripts live in `examples/`. Activate the venv first, then run any of them.

```bash
source .venv/bin/activate   # if not already active
```

### `examples/00_verify_install.py`
```python
"""
00_verify_install.py
--------------------
Verify that Docling is correctly installed and print its version.
"""

import sys

print(f"Python version : {sys.version}")

try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        docling_version = version("docling")
    except PackageNotFoundError:
        docling_version = "(version not found)"
    import docling  # noqa: F401
    print(f"Docling version: {docling_version}")
    print("\n✅  Docling is installed correctly!")
except ImportError:
    print("\n❌  Docling is NOT installed.")
    print("    Run: pip install docling")
    sys.exit(1)

# Quick sanity check — import the main converter class
try:
    from docling.document_converter import DocumentConverter  # noqa: F401
    print("✅  DocumentConverter import OK")
except ImportError as e:
    print(f"❌  Import error: {e}")
    sys.exit(1)
```

---

### `examples/01_convert_pdf.py`
```python
"""
01_convert_pdf.py
-----------------
Convert a PDF (local file or URL) to Markdown using the Docling Python API.

Usage:
    python 01_convert_pdf.py
    python 01_convert_pdf.py path/to/document.pdf
    python 01_convert_pdf.py https://arxiv.org/pdf/2408.09869
"""

import sys
from pathlib import Path

from docling.document_converter import DocumentConverter

# ── Source ─────────────────────────────────────────────────────────────────
# Default: the Docling technical report (requires internet)
source = sys.argv[1] if len(sys.argv) > 1 else "https://arxiv.org/pdf/2408.09869"

print(f"Converting: {source}")
print("Please wait — this may take a moment on first run (models are downloaded)...\n")

# ── Convert ────────────────────────────────────────────────────────────────
converter = DocumentConverter()
result = converter.convert(source)

# ── Export to Markdown ─────────────────────────────────────────────────────
markdown = result.document.export_to_markdown()

# Write to file
out_path = Path("output_pdf.md")
out_path.write_text(markdown, encoding="utf-8")

print(f"✅  Conversion complete.")
print(f"    Output saved to: {out_path.resolve()}")
print(f"\n── First 500 characters of output ──────────────────────────────────")
print(markdown[:500])
```

---

### `examples/02_convert_image_ocr.py`
```python
"""
02_convert_image_ocr.py
-----------------------
OCR an image file (PNG, JPEG, TIFF, BMP, WebP) with Docling.

Usage:
    python 02_convert_image_ocr.py path/to/image.png
    python 02_convert_image_ocr.py path/to/scan.tiff
"""

import sys
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

# ── Argument ───────────────────────────────────────────────────────────────
if len(sys.argv) < 2:
    print("Usage: python 02_convert_image_ocr.py <image_path>")
    print("Example: python 02_convert_image_ocr.py sample.png")
    sys.exit(1)

image_path = Path(sys.argv[1])
if not image_path.exists():
    print(f"❌  File not found: {image_path}")
    sys.exit(1)

print(f"OCR processing: {image_path}")

# ── Configure OCR pipeline ─────────────────────────────────────────────────
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True            # Enable OCR
pipeline_options.do_table_structure = True  # Detect tables

converter = DocumentConverter(
    format_options={
        InputFormat.IMAGE: PdfFormatOption(pipeline_options=pipeline_options),
    }
)

# ── Convert ────────────────────────────────────────────────────────────────
result = converter.convert(str(image_path))
markdown = result.document.export_to_markdown()

# ── Output ─────────────────────────────────────────────────────────────────
out_path = image_path.with_suffix(".md")
out_path.write_text(markdown, encoding="utf-8")

print(f"✅  OCR complete.")
print(f"    Output saved to: {out_path.resolve()}")
print(f"\n── Extracted text ───────────────────────────────────────────────────")
print(markdown[:1000] if markdown else "(no text detected)")
```

---

### `examples/03_convert_docx.py`
```python
"""
03_convert_docx.py
------------------
Convert a DOCX, PPTX, or XLSX file to Markdown.

Usage:
    python 03_convert_docx.py path/to/document.docx
    python 03_convert_docx.py path/to/presentation.pptx
    python 03_convert_docx.py path/to/spreadsheet.xlsx
"""

import sys
from pathlib import Path

from docling.document_converter import DocumentConverter

# ── Argument ───────────────────────────────────────────────────────────────
if len(sys.argv) < 2:
    print("Usage: python 03_convert_docx.py <file_path>")
    print("Supported: .docx  .pptx  .xlsx  .odt  .odp  .ods")
    sys.exit(1)

source = Path(sys.argv[1])
if not source.exists():
    print(f"❌  File not found: {source}")
    sys.exit(1)

print(f"Converting: {source}")

# ── Convert ────────────────────────────────────────────────────────────────
converter = DocumentConverter()
result = converter.convert(str(source))

# ── Export ─────────────────────────────────────────────────────────────────
markdown = result.document.export_to_markdown()

out_path = source.with_suffix(".md")
out_path.write_text(markdown, encoding="utf-8")

print(f"✅  Conversion complete.")
print(f"    Output saved to: {out_path.resolve()}")
print(f"\n── First 500 characters ─────────────────────────────────────────────")
print(markdown[:500])
```

---

### `examples/04_batch_convert.py`
```python
"""
04_batch_convert.py
-------------------
Batch-convert all supported documents in a folder to Markdown.

Usage:
    python 04_batch_convert.py path/to/input_folder
    python 04_batch_convert.py path/to/input_folder path/to/output_folder
"""

import sys
from pathlib import Path

from docling.document_converter import DocumentConverter

# ── Supported extensions ───────────────────────────────────────────────────
SUPPORTED = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".png", ".jpg",
             ".jpeg", ".tiff", ".tif", ".bmp", ".webp", ".odt", ".odp", ".ods"}

# ── Arguments ──────────────────────────────────────────────────────────────
if len(sys.argv) < 2:
    print("Usage: python 04_batch_convert.py <input_folder> [output_folder]")
    sys.exit(1)

input_dir = Path(sys.argv[1])
output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else input_dir / "converted"

if not input_dir.is_dir():
    print(f"❌  Not a directory: {input_dir}")
    sys.exit(1)

output_dir.mkdir(parents=True, exist_ok=True)

# ── Collect files ──────────────────────────────────────────────────────────
files = [f for f in input_dir.iterdir() if f.suffix.lower() in SUPPORTED]

if not files:
    print(f"No supported files found in {input_dir}")
    sys.exit(0)

print(f"Found {len(files)} file(s) in {input_dir}")
print(f"Output directory: {output_dir}\n")

# ── Convert ────────────────────────────────────────────────────────────────
converter = DocumentConverter()
success, failed = 0, 0

for i, file in enumerate(files, 1):
    print(f"[{i}/{len(files)}] {file.name} ...", end=" ", flush=True)
    try:
        result = converter.convert(str(file))
        markdown = result.document.export_to_markdown()
        out_file = output_dir / (file.stem + ".md")
        out_file.write_text(markdown, encoding="utf-8")
        print(f"✅  → {out_file.name}")
        success += 1
    except Exception as e:
        print(f"❌  ERROR: {e}")
        failed += 1

print(f"\n── Summary ──────────────────────────────────────────────────────────")
print(f"  Converted : {success}")
print(f"  Failed    : {failed}")
print(f"  Output    : {output_dir.resolve()}")
```

---

### `examples/05_export_json.py`
```python
"""
05_export_json.py
-----------------
Convert a document and export it to structured (lossless) JSON.
The JSON captures the full DoclingDocument model: pages, text, tables,
figures, reading order, and more.

Usage:
    python 05_export_json.py path/to/document.pdf
    python 05_export_json.py https://arxiv.org/pdf/2408.09869
"""

import json
import sys
from pathlib import Path

from docling.document_converter import DocumentConverter

# ── Source ─────────────────────────────────────────────────────────────────
source = sys.argv[1] if len(sys.argv) > 1 else "https://arxiv.org/pdf/2408.09869"

print(f"Converting: {source}")
print("Please wait...\n")

# ── Convert ────────────────────────────────────────────────────────────────
converter = DocumentConverter()
result = converter.convert(source)

# ── Export to JSON ─────────────────────────────────────────────────────────
doc_dict = result.document.export_to_dict()

out_path = Path("output_document.json")
with out_path.open("w", encoding="utf-8") as f:
    json.dump(doc_dict, f, indent=2, ensure_ascii=False)

print(f"✅  JSON export complete.")
print(f"    Output saved to: {out_path.resolve()}")

# Show top-level keys
print(f"\n── Top-level keys in DoclingDocument JSON ───────────────────────────")
for key in doc_dict.keys():
    print(f"  {key}")

# Show page count
pages = doc_dict.get("pages", {})
print(f"\n── Pages detected: {len(pages)}")
```

---

### `examples/06_cli_demo.sh`
```bash
#!/usr/bin/env bash
# 06_cli_demo.sh
# ──────────────────────────────────────────────────────────────────────────
# Docling CLI usage examples.
# Make executable: chmod +x 06_cli_demo.sh
# Run:             ./06_cli_demo.sh
# ──────────────────────────────────────────────────────────────────────────

set -euo pipefail

echo "================================================================"
echo "  Docling CLI Demo"
echo "================================================================"
echo ""

# ── 1. Basic conversion — remote PDF → Markdown ───────────────────────────
echo "[1] Converting remote PDF to Markdown..."
docling https://arxiv.org/pdf/2206.01062 --output ./cli_output
echo "    Done. Check ./cli_output/"
echo ""

# ── 2. Specify output format explicitly ───────────────────────────────────
echo "[2] Converting to HTML..."
docling https://arxiv.org/pdf/2206.01062 --to html --output ./cli_output
echo "    Done."
echo ""

# ── 3. VLM pipeline (GraniteDocling model) ────────────────────────────────
# NOTE: Downloads the GraniteDocling model on first run (~1 GB).
# Uncomment the line below to use it.
# echo "[3] Using VLM pipeline with GraniteDocling..."
# docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/2206.01062

# ── 4. Convert a local file ───────────────────────────────────────────────
# Uncomment and set your file path:
# echo "[4] Converting local file..."
# docling path/to/your/document.pdf --output ./cli_output

# ── 5. Show help ──────────────────────────────────────────────────────────
echo "[5] Docling CLI help:"
docling --help
```

---

## Step 3 — Build the Bob MCP server

The MCP server is a small Node.js/TypeScript process that Bob spawns and communicates with.  
It calls the Docling Python venv internally whenever a tool is invoked.

### 3a. Create the project structure

```
docling-mcp/
├── package.json
├── tsconfig.json
└── src/
    └── index.ts
```

### 3b. `docling-mcp/package.json`
```json
{
  "name": "docling-mcp",
  "version": "0.1.0",
  "description": "Bob MCP server — scan any document with Docling and return Markdown or JSON",
  "type": "module",
  "scripts": {
    "build": "tsc && chmod 755 build/index.js",
    "dev": "tsc --watch"
  },
  "bin": {
    "docling-mcp": "./build/index.js"
  },
  "files": [
    "build"
  ],
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.29.0",
    "zod": "^4.4.3"
  },
  "devDependencies": {
    "@types/node": "^26.0.0",
    "typescript": "^7.0.0"
  }
}
```

### 3c. `docling-mcp/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "types": ["node"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

### 3d. `docling-mcp/src/index.ts`
```typescript
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

// Resolve the venv python path from the server's own location
const PYTHON = process.env.DOCLING_PYTHON ?? findPython();

function findPython(): string {
  // serverDir = …/Module 8 - OCR Engine with Docling/docling-mcp/build/
  const serverDir = new URL(".", import.meta.url).pathname;
  return (
    serverDir.replace(/docling-mcp\/build\/?$/, "").replace(/\/$/, "") +
    "/.venv/bin/python3"
  );
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
  if (!existsSync(PYTHON)) {
    throw new Error(
      `Docling Python not found at: ${PYTHON}\n` +
        `Set the DOCLING_PYTHON env var to the correct python executable, e.g.:\n` +
        `  export DOCLING_PYTHON=/path/to/.venv/bin/python3`
    );
  }

  return execFileAsync(PYTHON, ["-c", script, docPath], {
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
        content: [{ type: "text", text: stdout.trim() + warning }],
      };
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
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
        content: [{ type: "text", text: `❌ File not found: ${docPath}` }],
        isError: true,
      };
    }

    try {
      const { stdout, stderr } = await runDocling(CONVERT_TO_JSON, docPath);
      const warning = stderr ? `\n\n// Docling warnings: ${stderr.trim()}` : "";
      return {
        content: [{ type: "text", text: stdout.trim() + warning }],
      };
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
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
```

### 3e. Install dependencies and build

```bash
cd docling-mcp
npm install
npm run build
cd ..
```

After this, `docling-mcp/build/index.js` will exist.

---

## Step 4 — Register the MCP server with Bob

Bob's global MCP config lives at:

```
~/.bob/settings/mcp.json        (macOS / Linux)
%APPDATA%\bob\settings\mcp.json (Windows)
```

Open that file and **add the `docling-mcp` entry** inside the `mcpServers` object.  
Replace `/YOUR/PATH/TO` with the absolute path to the module directory on your machine.

```json
{
  "mcpServers": {
    "docling-mcp": {
      "command": "node",
      "args": ["/YOUR/PATH/TO/Module 8 - OCR Engine with Docling/docling-mcp/build/index.js"],
      "env": {
        "DOCLING_PYTHON": "/YOUR/PATH/TO/Module 8 - OCR Engine with Docling/.venv/bin/python3"
      },
      "alwaysAllow": ["scan_document", "scan_document_to_json"],
      "disabled": false
    }
  }
}
```

> If `mcp.json` already has other servers, just add the `"docling-mcp": { … }` block alongside them — do not replace the whole file.

### Find your absolute path

```bash
# macOS / Linux
cd "Module 8 - OCR Engine with Docling"
pwd
# → paste that output into the JSON above
```

### Reload Bob

- Click **⚙️ Settings → MCP** tab — `docling-mcp` should appear as **Connected**
- Or use **Cmd+Shift+P → MCP: Reload Servers**

---

## Step 5 — Use it in Bob chat

Bob will automatically call `scan_document` whenever you paste a file path.

```
/Users/me/Documents/invoice.pdf
```
```
Summarize /Users/me/reports/q3-results.docx
```
```
Extract all tables from /Users/me/scans/form.png
```
```
Give me the JSON structure of /Users/me/slides/deck.pptx
```

No commands needed — Bob detects the file path and calls the tool automatically.

---

## Supported document formats

| Category | Extensions |
|----------|-----------|
| PDF | `.pdf` |
| Word / OpenDocument | `.docx` `.odt` `.rtf` |
| PowerPoint | `.pptx` `.odp` |
| Excel | `.xlsx` `.ods` |
| Images (OCR) | `.png` `.jpg` `.jpeg` `.tiff` `.tif` `.bmp` `.webp` |
| Web | `.html` `.htm` |
| E-book | `.epub` |
| LaTeX | `.tex` |
| Email | `.eml` `.msg` |
| Plain text | `.txt` `.md` |

---

## Troubleshooting

### "File not found" error for the Python executable

The `DOCLING_PYTHON` env var in `mcp.json` is wrong.  
Find the correct path:

```bash
# After activating the venv:
source "Module 8 - OCR Engine with Docling/.venv/bin/activate"
which python3
# → copy this path into mcp.json DOCLING_PYTHON value
```

### "Docling is NOT installed"

The venv was not created or Docling was not installed in it:

```bash
cd "Module 8 - OCR Engine with Docling"
python3 -m venv .venv
source .venv/bin/activate
pip install docling
```

### Build errors for the MCP server

```bash
cd "Module 8 - OCR Engine with Docling/docling-mcp"
rm -rf node_modules build
npm install
npm run build
```

### Bob doesn't call the tool automatically

Check that `alwaysAllow` contains `"scan_document"` and `"scan_document_to_json"` in `mcp.json`, and that `"disabled"` is `false`.

---

## References

- Docling GitHub → https://github.com/docling-project/docling  
- Docling Docs → https://docling-project.github.io/docling/  
- Docling PyPI → https://pypi.org/project/docling/  
- MCP SDK → https://github.com/modelcontextprotocol/typescript-sdk  
- IBM Granite Docling model → https://huggingface.co/ibm-granite/granite-docling-258M
