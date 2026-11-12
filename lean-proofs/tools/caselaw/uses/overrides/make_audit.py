"""Audit packets: a random sample of candidates by kind of evidence, the top of the ranking, and non-candidates as a
baseline. Each packet holds the decision's passages around the cited section, the cited words before and after the
law (with the changes), the law's text where it amends the section and where it names the decision, and the report's
passage naming it. Blind: the packet does not say which stratum an item came from.

    python make_audit.py   -> audit/in_<k>.json, audit/key.json
"""
import collections, csv, difflib, html, json, os, random, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.expanduser('~/Documents/global-law-lean/lean-proofs/tools/caselaw'))
from usc_encode import blocks
import lawtext as LT
W = os.path.expanduser('~/Documents/us-caselaw-lean-work'); O = f'{W}/uses/overrides'; REPOS = os.path.expanduser('~/Documents/us-caselaw-repos')
csv.field_size_limit(10 ** 9)
random.seed(20261112)
pairs = list(csv.DictReader(open(f'{O}/pairs.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
cand = [p for p in pairs if p['evidence'] == '1' and int(p['gap']) <= 120]
by = collections.defaultdict(list)
for p in cand: by[p['kind']].append(p)
pick = {}
def take(lst, n, tag):
    for p in random.sample(lst, min(n, len(lst))):
        pick.setdefault((p['nid'], p['law']), (p, tag))
MODE = sys.argv[1] if len(sys.argv) > 1 else 'rest'
done = set()
if os.path.exists(f'{O}/audit/key_N.json'):
    done = {tuple(v.split('|')[1:]) for v in json.load(open(f'{O}/audit/key_N.json')).values()}
if MODE == 'N':   # every candidate whose law names the decision: a census, not a sample
    for p in by['law names it']: pick[(p['nid'], p['law'])] = (p, 'N')
elif MODE == 'G':  # gold-list overrides among the candidates not yet audited: does the auditor recognise known overrides?
    gold = list(csv.DictReader(open(f'{O}/gold/gold.tsv', encoding='utf-8'), delimiter='	'))
    gk = {(g['us_cite'], g['overriding_law']) for g in gold}
    seen = set()
    for kf in ('key_N.json', 'key_rest.json'):
        seen |= {tuple(v.split('|')[1:]) for v in json.load(open(f'{O}/audit/{kf}')).values()}
    for p in cand:
        if (p['cite'], p['law']) in gk and (p['nid'], p['law']) not in seen: pick[(p['nid'], p['law'])] = (p, 'G')
else:
    take([p for p in by['report names it'] if (p['nid'], p['law']) not in done], 40, 'R')
    qq = [p for p in by['quoted words struck'] if (p['nid'], p['law']) not in done]
    take([p for p in qq if p['tier'] in ('S', 'A')], 25, 'Q')     # courts of appeals and the Supreme Court
    take([p for p in qq if p['tier'] in ('F', 'T')], 20, 'Q')     # district, specialised and state courts
    for p in sorted(cand, key=lambda x: -float(x['score']))[:30]:
        if (p['nid'], p['law']) not in done: pick.setdefault((p['nid'], p['law']), (p, 'T'))
    non = [p for p in pairs if p['evidence'] == '0' and int(p['gap']) <= 120 and p['tier'] in ('S', 'A')]
    take(non, 20, 'B')
crows = {}
for l in open(f'{O}/cand_rows.tsv', encoding='utf-8'):
    f = l.rstrip('\n').split('\t'); crows[f[0]] = f
vers = collections.defaultdict(list)
for i, l in enumerate(open(f'{W}/usc/versions.tsv', encoding='utf-8')):
    f = l.rstrip('\n').split('\t'); vers[f[0]].append((int(f[4]), i, f[5], f[2], f[3]))
for p in vers: vers[p].sort(key=lambda v: (v[0], v[1]))
def blob(sha):
    return subprocess.run(['git', '--git-dir', f'{W}/usc-full.git', 'cat-file', '-p', sha], capture_output=True).stdout.decode('utf-8', 'replace') if sha else ''
def words(path, sub, k):
    t = blob(vers[path][k][2]); b = blocks(t)
    return b.get(sub, t) if sub else t
def law_amend_passage(lab, t, s):
    L = LT.text(lab)
    if not L: return ''
    pat = re.compile(r'\(' + re.escape(t) + r' U\.S\.C\. ?' + re.escape(s) + r'[\s(),a-zA-Z0-9]*\)')
    out = []
    for m in list(pat.finditer(L))[:2]:
        out.append(L[max(0, m.start() - 300):m.start() + 1800])
    return '\n[...]\n'.join(out)
def context(repo, dpath, s):
    text = subprocess.run(['git', '-C', f'{REPOS}/{repo}', 'show', f'HEAD:{dpath}'], capture_output=True).stdout.decode('utf-8', 'replace')
    b0 = text.find('\n---', 3) + 4
    ms = [m.start() for m in re.finditer(r'(?<![\w.])' + re.escape(s) + r'(?![\w-])', text) if m.start() > b0]
    ctx = []
    for k in ms:
        if not ctx or k > ctx[-1][1]:
            ctx.append((max(0, k - 1200), k + 900))
        if len(ctx) == 4: break
    return ('\n[...]\n'.join(text[a:b] for a, b in ctx) or text[b0:b0 + 4000]), text[b0:b0 + 1500]
out = []
for (nid, lab), (p, tag) in pick.items():
    rids = p['rids'].split(',')
    # the citation with the most quoted-and-struck evidence, else the first
    r = crows[rids[0]]
    path = f'title-{r[4]}/{r[5]}.md'; k0, k1 = int(r[13]), int(r[14])
    w0, w1 = words(path, r[6], k0), words(path, r[6], k1)
    a0, a1 = w0.split(), w1.split()
    diff = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a0, a1, autojunk=False).get_opcodes():
        if op != 'equal':
            diff.append({'before': ' '.join(a0[max(0, i1 - 10):i2 + 10]), 'after': ' '.join(a1[max(0, j1 - 10):j2 + 10])})
    ctx, head = context(p['repo'], p['path'], r[5])
    out.append({'key': f'{tag}|{nid}|{lab}', 'decision': p['name'], 'cite': p['cite'], 'decided': p['decided'], 'court_repo': p['repo'],
                'cited_block': f"{r[4]} U.S.C. § {r[5]}" + (f"({r[6]})" if r[6] else ' (whole section)'),
                'all_sections_this_law_rewrote_for_it': p['sections'],
                'law': f"{lab} ({p['title']}), in force {p['law_day']}", 'months_after': p['gap'],
                'decision_opening': head, 'decision_passages': ctx[:9000],
                'cited_words_when_decided': w0[:3000], 'cited_words_after_law': w1[:3000], 'changes': diff[:10],
                'law_text_amending_section': law_amend_passage(lab, r[4], r[5])[:4500],
                'law_text_naming_a_case': p['law_snip'], 'committee_report_naming_a_case': p['report_snip']})
random.shuffle(out)
key = {}
pre = {'N': 'n', 'G': 'g'}.get(MODE, 'o')
for n, o in enumerate(out):
    key[f'{pre}{n + 1:03d}'] = o.pop('key'); o['id'] = f'{pre}{n + 1:03d}'
os.makedirs(f'{O}/audit', exist_ok=True)
K = {'N': 2, 'G': 1}.get(MODE, 5)
for i in range(K):
    json.dump(out[i::K], open(f'{O}/audit/in_{MODE}_{i}.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
json.dump(key, open(f'{O}/audit/key_{MODE}.json', 'w', encoding='utf-8', newline='\n'), indent=1)
print(len(out), collections.Counter(v.split('|')[0] for v in key.values()))
