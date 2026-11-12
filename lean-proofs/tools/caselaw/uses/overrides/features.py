"""Decision-text evidence for selected candidate rows: how the decision uses the section, and whether the words the law
rewrote are words the decision quoted.

    python features.py <rows file (cand_rows subset)> <out tsv>

Per row: interp (interpretive cue words near the citation), qin (quoted phrases of 3+ words found in the cited words as
the court read them), qstruck (of those, phrases no longer in the rewritten words), struck (5-word runs of the cited words that the
law struck or replaced, so no longer in the new words, that appear anywhere in the decision), ins_only (the law only added words), oldlen, newlen."""
import collections, difflib, os, re, subprocess, sys, threading
sys.path.insert(0, os.path.expanduser('~/Documents/global-law-lean/lean-proofs/tools/caselaw'))
from usc_encode import blocks, norm
W = os.path.expanduser('~/Documents/us-caselaw-lean-work'); REPOS = os.path.expanduser('~/Documents/us-caselaw-repos')
vers = collections.defaultdict(list)
for i, l in enumerate(open(f'{W}/usc/versions.tsv', encoding='utf-8')):
    f = l.rstrip('\n').split('\t'); vers[f[0]].append((int(f[4]), i, f[5]))
for p in vers: vers[p].sort(key=lambda v: (v[0], v[1]))
class Batch:
    def __init__(self, args):
        self.p = subprocess.Popen(args + ['cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    def get(self, ref):
        self.p.stdin.write((ref + '\n').encode()); self.p.stdin.flush()
        h = self.p.stdout.readline().split()
        if len(h) < 3 or h[1] == b'missing': return ''
        d = self.p.stdout.read(int(h[2])); self.p.stdout.read(1)
        return d.decode('utf-8', 'replace')
usc = Batch(['git', '--git-dir', f'{W}/usc-full.git'])
repos = {}
def dec_text(repo, path):
    if repo not in repos: repos[repo] = Batch(['git', '-C', f'{REPOS}/{repo}'])
    t = repos[repo].get(f'HEAD:{path}')
    i = t.find('\n---', 3)
    return t[i + 4:] if t.startswith('---') and i > 0 else t
def simp(s):
    return re.sub(r'\s+', ' ', re.sub(r"[^a-z0-9 ]", ' ', norm(s).lower())).strip()
blobcache = {}
def blob(sha):
    if sha not in blobcache:
        if len(blobcache) > 4000: blobcache.clear()
        blobcache[sha] = usc.get(sha) if sha else ''
    return blobcache[sha]
diffcache = {}
def subdiff(path, sub, k0, k1):
    key = (path, sub, k0, k1)
    if key in diffcache: return diffcache[key]
    vs = vers[path]; t0, t1 = blob(vs[k0][2]), blob(vs[k1][2])
    b0, b1 = blocks(t0), blocks(t1)
    if sub and (sub in b0 or sub in b1):
        o, n = b0.get(sub, ''), b1.get(sub, '')
    else:
        o, n = t0, t1
    a, b = simp(o).split(), simp(n).split()
    # struck: 5-word runs of the old words that no longer occur in the new words (set difference, not an alignment)
    g1 = {' '.join(b[k:k + 5]) for k in range(max(1, len(b) - 4))}
    struck = [g for g in (' '.join(a[k:k + 5]) for k in range(max(1, len(a) - 4))) if g not in g1]
    ins_only = not struck
    r = (' ' + ' '.join(a) + ' ', ' ' + ' '.join(b) + ' ', set(struck), ins_only)
    if len(diffcache) > 20000: diffcache.clear()
    diffcache[key] = r
    return r
INTERP = re.compile(r'interpret|constru|meaning of|plain (?:language|meaning|text)|ambigu|legislative history|statutory text|'
                    r'text of the statute|congress intended|intent of congress|we hold|we conclude|textual|the word ["“]|the phrase ["“]|the term ["“]', re.I)
QUOTE = re.compile(r'[“"]([^”"]{12,400})[”"]')
def main(inp, out):
    rows = [l.rstrip('\n').split('\t') for l in open(inp, encoding='utf-8')]
    rows.sort(key=lambda r: (r[16], r[17]))
    last = None; text = low = ''
    with open(out, 'w', encoding='utf-8', newline='\n') as fo:
        for n, r in enumerate(rows):
            rid, t, s, sub, k0, k1, repo, path = r[0], r[4], r[5], r[6], int(r[13]), int(r[14]), r[16], r[17]
            if (repo, path) != last:
                text = dec_text(repo, path); low = ' ' + simp(text) + ' '; last = (repo, path)
                quotes = [simp(q) for q in QUOTE.findall(text)]
                quotes = [q for q in quotes if len(q.split()) >= 3]
            old, new, struck, ins_only = subdiff(f'title-{t}/{s}.md', sub, k0, k1)
            # interpretive cues within 1,500 characters of a mention of the section
            ms = [m.start() for m in re.finditer(r'(?<![\w.])' + re.escape(s) + r'(?![\w-])', text)][:60]
            interp = sum(len(INTERP.findall(text[max(0, k - 1500):k + 1500])) for k in ms[:20])
            qin = [q for q in quotes if f' {q} ' in old]
            qst = [q for q in qin if f' {q} ' not in new]
            sh = sum(1 for g in struck if f' {g} ' in low)
            fo.write(f'{rid}\t{len(ms)}\t{interp}\t{len(qin)}\t{len(qst)}\t{sh}\t{len(struck)}\t{int(ins_only)}\t{len(old.split())}\t{len(new.split())}\t{(qst[0] if qst else "")[:200]}\n')
            if n % 5000 == 0: print(n, flush=True)
if __name__ == '__main__':
    main(*sys.argv[1:])
