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
