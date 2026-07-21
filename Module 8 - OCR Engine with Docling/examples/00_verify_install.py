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
