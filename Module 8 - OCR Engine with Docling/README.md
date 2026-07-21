# Module 8 — OCR Engine with Docling

> **Docling** is an IBM open-source library that converts documents (PDF, DOCX, PPTX, XLSX, HTML, images, and more) into structured formats ready for Generative AI pipelines.
>
> GitHub: https://github.com/docling-project/docling  
> Docs:   https://docling-project.github.io/docling/

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10 or higher |
| pip | latest recommended |

---

## Installation

### Option A — Virtual environment (recommended)

```bash
# 1. Create and activate the venv bundled in this directory
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 2. Install Docling
pip install docling
```

### Option B — Global / Conda environment

```bash
pip install docling
```

### Optional extras

```bash
# Extras for OCR (EasyOCR or Tesseract backends)
pip install "docling[easyocr]"

# Extras for VLM pipeline (GraniteDocling, etc.)
pip install "docling[vlm]"

# Everything
pip install "docling[all]"
```

---

## Quick verification

```bash
python examples/00_verify_install.py
```

---

## Module examples

| File | Description |
|------|-------------|
| `examples/00_verify_install.py` | Confirm Docling is installed correctly |
| `examples/01_convert_pdf.py` | Convert a PDF → Markdown via Python API |
| `examples/02_convert_image_ocr.py` | OCR an image file (PNG/JPEG/TIFF) |
| `examples/03_convert_docx.py` | Convert a DOCX → Markdown |
| `examples/04_batch_convert.py` | Batch-convert a folder of documents |
| `examples/05_export_json.py` | Export a document to structured JSON |
| `examples/06_cli_demo.sh` | Docling CLI usage examples |

---

## CLI usage (after activation)

```bash
# Convert a remote PDF to Markdown
docling https://arxiv.org/pdf/2206.01062

# Use the VLM pipeline with GraniteDocling
docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/2206.01062

# Convert a local file
docling path/to/document.pdf --output ./output
```

---

## Key concepts

- **DocumentConverter** — main entry point for converting any supported format
- **DoclingDocument** — unified document representation
- **Export formats** — Markdown, HTML, JSON (lossless), DocTags, WebVTT
- **OCR backends** — Tesseract (default), EasyOCR, RapidOCR
- **Pipelines** — `standard` (fast) · `vlm` (accuracy with Visual Language Models)

---

## Integrations

Docling integrates natively with:

- LangChain (`langchain-docling`)
- LlamaIndex (`llama-index-readers-docling`)
- Haystack
- Crew AI
- MCP server for AI agents

---

## References

- [Docling Technical Report (arXiv)](https://arxiv.org/abs/2408.09869)
- [Official Documentation](https://docling-project.github.io/docling/)
- [PyPI Package](https://pypi.org/project/docling/)
- [IBM Granite Docling Model](https://huggingface.co/ibm-granite/granite-docling-258M)
