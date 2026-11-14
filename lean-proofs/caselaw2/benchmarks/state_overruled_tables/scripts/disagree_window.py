"""For the sampled misses (work/disagree_<label>.txt X lines), print Y-text windows where an overruling word is near
X's mention.   python -X utf8 disagree_window.py <label>"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
sys.path.insert(0, HERE); import link as L
label = sys.argv[1]
xs = [l.split()[1] for l in open(os.path.join(B, 'work', 'disagree_%s.txt' % label), encoding='utf-8') if l.startswith('X ')]
cases = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open(os.path.join(B, 'results', label + '.cases.tsv'), encoding='utf-8')}
idx = {}
for l in open(os.path.join(B, 'work', 'old_index.tsv'), encoding='utf-8'):
    p = l.rstrip('\n').split('\t'); idx.setdefault(p[1], p)
ys = {}
for x in xs:
    for y in cases[x][6].split(','):
        p = idx[y]; ys[int(y)] = {'node': int(y), 'repo': p[3], 'path': p[7]}
T = L.fetch_texts(list(ys.values()))
KW = re.compile(r'(?i)overrul|disapprov|no longer|not (?:be )?follow|erroneous|reverse the decision|cannot be sustained|not law|abandon|recede|wrong')
for x in xs:
    xi = idx[x]; c = cases[x]
    print('==', x, xi[6], xi[5], '| outcome', c[8])
    v, tk, pg = xi[0].split(' ')
    toks = [w for w in re.findall(r'[A-Za-z]{4,}', xi[5]) if w.lower() not in L.STOP][:2]
    for y in c[6].split(','):
        t = T.get(int(y), '')
        body = t[t.find('\n# '):] if '\n# ' in t else t
        spots = [m.start() for m in re.finditer(r'(?<!\d)' + v + r'\w{0,2}\s+[A-Z][A-Za-z.&\'’ ]{0,25}?,?\s+' + pg + r'(?!\d)', body)]
        for w in toks:
            spots += [m.start() for m in re.finditer(r'\b' + re.escape(w) + r'\b', body)]
        out = []
        for s in sorted(set(spots)):
            win = body[max(0, s - 500):s + 500]
            if KW.search(win):
                out.append(win.replace('\n', ' '))
        print('  Y', y, idx[y][6], idx[y][5], '| mentions', len(set(spots)), '| with overruling word', len(out))
        for w in out[:1]:
            print('    ' + w)
