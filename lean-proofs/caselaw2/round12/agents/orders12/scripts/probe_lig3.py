"""Per (font, gid): which unicode values the glyph extracts as, over the whole PDF; prints gids with >1 value or a
ligature value. python -I probe_lig3.py <pdf>"""
import sys, collections
import pymupdf
doc = pymupdf.open(sys.argv[1])
m = collections.defaultdict(collections.Counter)
for pg in doc:
    for sp in pg.get_texttrace():
        for c in sp['chars']:
            m[(sp['font'], c[1])][c[0]] += 1
for k, cnt in sorted(m.items()):
    if len(cnt) > 1 or any(0xfb00 <= u <= 0xfb06 for u in cnt):
        print(k, {hex(u): v for u, v in cnt.items()})
