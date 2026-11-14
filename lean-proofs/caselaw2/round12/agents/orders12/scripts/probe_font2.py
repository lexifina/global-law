"""Find ToUnicode entries mapping to f (0066) or ligatures, and the Encoding Differences names near them.
python -I probe_font2.py <pdf> <font_xref>"""
import sys, re
import pymupdf
doc = pymupdf.open(sys.argv[1]); x = int(sys.argv[2])
t = doc.xref_get_key(x, 'ToUnicode'); tx = int(t[1].split()[0])
s = doc.xref_stream(tx).decode('latin-1')
for m in re.finditer(r'<([0-9A-F]+)>\s*<([0-9A-F]+)>', s):
    if m.group(2) in ('0066', 'FB01', 'FB02', 'FB00', 'FB03', 'FB04', '00660066', '00660069', '0066006C'):
        print('tounicode', m.group(1), m.group(2))
for m in re.finditer(r'<([0-9A-F]+)>\s*<([0-9A-F]+)>\s*<([0-9A-F]+)>', s):
    print('range', m.groups())
e = doc.xref_get_key(x, 'Encoding'); ex = int(e[1].split()[0])
o = doc.xref_object(ex)
print(re.sub(r'\s+', ' ', o)[:3000])
