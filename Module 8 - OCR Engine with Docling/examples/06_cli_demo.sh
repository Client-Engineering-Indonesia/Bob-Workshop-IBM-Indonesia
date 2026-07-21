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
