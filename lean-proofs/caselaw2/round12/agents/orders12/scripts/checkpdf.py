"""Compare PDF page counts / sha256 with converted text. python -I checkpdf.py <txtdir> <pdf>..."""
import sys, os, hashlib
import pymupdf
td = sys.argv[1]
for p in sys.argv[2:]:
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    d = pymupdf.open(p); n = d.page_count; d.close()
    t = os.path.join(td, os.path.splitext(os.path.basename(p))[0] + '.txt')
    s = open(t, encoding='utf-8').read()
    print(os.path.basename(p), h[:16], n, 'pages; txt pages', s.count('\n\f\n') + 1, 'chars', len(s))
