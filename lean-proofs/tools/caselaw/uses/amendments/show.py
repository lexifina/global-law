"""Debug: python tools/show.py <law label> <title> <section> [path-prefix]  -> before/after lines with paths."""
import sys
sys.path.insert(0, 'tools')
import record
law, t, s = sys.argv[1], sys.argv[2], sys.argv[3]
pre = sys.argv[4] if len(sys.argv) > 4 else ''
bp, bl = record.load_versions()
p = f'title-{t}/{s}.md'
vs = bp[p]
idx = bl.get(law, {}).get(p, [])
print('versions', [(i, v[2], v[3]) for i, v in enumerate(vs)][-12:], 'law idx', idx)
B = record.Blobs()
if idx:
    for name, i in (('BEFORE', idx[0] - 1), ('AFTER', idx[-1])):
        print('====', name, vs[i][2], vs[i][3])
        for path, text in record.parse_section(B.get(vs[i][4])):
            if path.startswith(pre) or path == '#':
                print(f'{path:20s} | {text[:160]}')
