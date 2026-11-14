"""Extract text from a PDF with PyMuPDF. Usage: python -I pdftext.py in.pdf out.txt"""
import sys

import fitz  # PyMuPDF

doc = fitz.open(sys.argv[1])
with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as f:
    for i, page in enumerate(doc):
        f.write("\n=== page %d ===\n" % (i + 1))
        f.write(page.get_text())
