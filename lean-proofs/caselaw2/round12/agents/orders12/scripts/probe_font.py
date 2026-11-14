"""Print a page's font dicts, encoding differences and ToUnicode entries for f / fi codes.
python -I probe_font.py <pdf> <page>"""
import sys, re
import pymupdf
doc = pymupdf.open(sys.argv[1]); pg = doc[int(sys.argv[2])]
for f in pg.get_fonts():
    x = f[0]
    print('FONT', f)
    obj = doc.xref_object(x)
    print(obj[:600])
    t = doc.xref_get_key(x, 'ToUnicode')
    print('ToUnicode', t)
    if t[0] == 'xref':
        tx = int(t[1].split()[0])
        s = doc.xref_stream(tx).decode('latin-1')
        print(s[:1500])
    e = doc.xref_get_key(x, 'Encoding')
    print('Encoding', e)
    if e[0] == 'xref':
        print(doc.xref_object(int(e[1].split()[0]))[:1500])
