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
pipeline_options.do_ocr = True           # Enable OCR
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
