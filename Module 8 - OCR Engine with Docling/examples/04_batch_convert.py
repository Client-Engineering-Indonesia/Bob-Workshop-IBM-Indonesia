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
