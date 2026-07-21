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
