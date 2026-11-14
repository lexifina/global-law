"""Probe how the dropped 'fi' ligature is encoded: per font, glyph ids that extract as 'f'.
python -I probe_lig.py <pdf> <page_from> <page_to>"""
import sys, collections
import pymupdf
doc = pymupdf.open(sys.argv[1])
a, b = int(sys.argv[2]), int(sys.argv[3])
gl = collections.Counter()
for pno in range(a, b):
    pg = doc[pno]
    for sp in pg.get_texttrace():
        font = sp['font']
        for ch in sp['chars']:
            u, gid = ch[0], ch[1]
            if u in (ord('f'), ord('i'), 0xfb01, 0xfb02, 0xfb00, 0xfb03, 0xfb04) or u < 32:
                gl[(font, hex(u), gid)] += 1
for k, v in sorted(gl.items()):
    print(v, k)
