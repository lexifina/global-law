"""Show the glyph trace around a word on one page. python -I probe_lig2.py <pdf> <page> <word>"""
import sys
import pymupdf
doc = pymupdf.open(sys.argv[1]); pg = doc[int(sys.argv[2])]; w = sys.argv[3]
for sp in pg.get_texttrace():
    s = ''.join(chr(c[0]) for c in sp['chars'])
    i = s.find(w)
    if i >= 0:
        seg = sp['chars'][max(0, i - 3): i + len(w) + 3]
        print(sp['font'], sp['size'], [(chr(c[0]), c[1], round(c[2][0], 1)) for c in seg])
print(pg.get_fonts())
