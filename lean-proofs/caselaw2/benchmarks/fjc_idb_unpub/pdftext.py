import sys
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
open(sys.argv[2], "w", encoding="utf-8").write("\n".join((p.extract_text() or "") for p in r.pages))
