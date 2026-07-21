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
