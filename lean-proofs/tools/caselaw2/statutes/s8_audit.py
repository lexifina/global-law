"""Step 8: blind audit packets for the new evidence strata (same instructions and labels as uses/overrides/audit).

    python s8_audit.py X 20 Y 20 L 10   -> statutes/audit/in_<tag>_<i>.json, key_<tag>.json
  X: lawNames/reportNames on a later rewrite (not the first, or 10-15 years after the decision)
  Y: a reporter cite in the law or report resolved to the decision (linked by section)
  L: laterCourtSays (treatments.tsv rows of kind supersededByEnactment), when that file exists
The packet does not say which stratum an item came from; items of all strata are shuffled together per file.
"""
import collections, csv, difflib, json, os, random, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.expanduser('~/Documents/global-law-lean/lean-proofs/tools/caselaw'))
import common as C
from usc_encode import blocks
csv.field_size_limit(10 ** 9)
REPOS = os.path.expanduser('~/Documents/us-caselaw-repos')
random.seed(20261112)
ev = list(csv.DictReader(open(f'{C.S}/evidence.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
pairs = {(p['nid'], p['law']): p for p in csv.DictReader(open(f'{C.S}/pairs2.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
import s5_score
done = set(s5_score.load_audits())
args = sys.argv[1:]
want = {args[i]: int(args[i + 1]) for i in range(0, len(args), 2)}
pick = {}
strata = {'X': lambda e: e['stratum'] == 'later' and e['evidence'] in ('lawNamesDecision', 'reportNamesDecision'),
          'Y': lambda e: e['stratum'] == 'cite'}
for tag, fn in strata.items():
    if tag not in want: continue
    pool = sorted({(e['nid'], e['law']) for e in ev if fn(e) and (e['nid'], e['law']) not in done})
    for k in random.sample(pool, min(want[tag], len(pool))): pick[k] = tag
vers = collections.defaultdict(list)
for i, l in enumerate(open(f'{C.W}/usc/versions.tsv', encoding='utf-8')):
    f = l.rstrip('\n').split('\t'); vers[f[0]].append((int(f[4]), i, f[5], f[2], f[3]))
for p in vers: vers[p].sort(key=lambda v: (v[0], v[1]))
def blob(sha):
    return subprocess.run(['git', '--git-dir', f'{C.W}/usc-full.git', 'cat-file', '-p', sha], capture_output=True).stdout.decode('utf-8', 'replace') if sha else ''
def words_around(t, s, sub, law, day):
    path = f'title-{t}/{s}.md'; vs = vers.get(path, [])
    k1 = next((k for k, v in enumerate(vs) if v[4] == law), None)
    if k1 is None or k1 == 0: return '', '', []
    w0, w1 = blob(vs[k1 - 1][2]), blob(vs[k1][2])
    if sub:
        b0, b1 = blocks(w0), blocks(w1); w0, w1 = b0.get(sub, w0), b1.get(sub, w1)
    a0, a1 = w0.split(), w1.split(); diff = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a0, a1, autojunk=False).get_opcodes():
        if op != 'equal': diff.append({'before': ' '.join(a0[max(0, i1 - 10):i2 + 10]), 'after': ' '.join(a1[max(0, j1 - 10):j2 + 10])})
    return w0, w1, diff
def dtext(repo_or_jur, path):
    for repo in (repo_or_jur,):
        r = subprocess.run(['git', '-C', f'{REPOS}/{repo}', 'show', f'HEAD:{path}'], capture_output=True)
        if r.returncode == 0: return r.stdout.decode('utf-8', 'replace'), repo
    # nodes.tsv gives the jurisdiction, not the repo: try repos whose name starts with it
    for repo in sorted(os.listdir(REPOS)):
        if repo.startswith(repo_or_jur):
            r = subprocess.run(['git', '-C', f'{REPOS}/{repo}', 'show', f'HEAD:{path}'], capture_output=True)
            if r.returncode == 0: return r.stdout.decode('utf-8', 'replace'), repo
    return '', ''
def context(text, s):
    b0 = text.find('\n---', 3) + 4
    ms = [m.start() for m in re.finditer(r'(?<![\w.])' + re.escape(s) + r'(?![\w-])', text) if m.start() > b0]
    ctx = []
    for k in ms:
        if not ctx or k > ctx[-1][1]: ctx.append((max(0, k - 1200), k + 900))
        if len(ctx) == 4: break
    return ('\n[...]\n'.join(text[a:b] for a, b in ctx) or text[b0:b0 + 5000]), text[b0:b0 + 1500]
def law_amend_passage(lab, t, s):
    L = C.text(lab)
    if not L: return ''
    pat = re.compile(r'\(' + re.escape(t) + r' U\.S\.C\. ?' + re.escape(s) + r'(?![\w\-])')
    ms = list(pat.finditer(L))[:2]
    if not ms:
        ms = list(re.finditer(r'[Ss]ection ' + re.escape(s) + r'(?:\([^)]*\))* of title ' + re.escape(t) + r'\b', L))[:2]
    return '\n[...]\n'.join(L[max(0, m.start() - 300):m.start() + 1800] for m in ms)
out = []
for (nid, law), tag in pick.items():
    p = pairs[(nid, law)]
    b = p['blocks'].split(';')[0]
    m = re.match(r'(\w+):([^(]+)(?:\(([^)]*)\))?', b); t, s, sub = m.group(1), m.group(2), m.group(3) or ''
    w0, w1, diff = words_around(t, s, sub, law, int(p['law_day']))
    text, repo = dtext(p['repo'], p['path'])
    ctx, head = context(text, s)
    out.append({'key': f'{tag}|{nid}|{law}', 'decision': p['name'], 'cite': p['cite'], 'decided': p['decided'], 'court_repo': repo,
                'cited_block': f'{t} U.S.C. § {s}' + (f'({sub})' if sub else ' (whole section)'),
                'all_sections_this_law_rewrote_for_it': p['blocks'],
                'law': f"{law}, in force {p['law_day']}", 'decision_opening': head, 'decision_passages': ctx[:9000],
                'cited_words_before_law': w0[:3000], 'cited_words_after_law': w1[:3000], 'changes': diff[:10],
                'law_text_amending_section': law_amend_passage(law, t, s)[:4500],
                'law_text_naming_a_case': p['law_snip'], 'committee_report_naming_a_case': p['report_snip']})
random.shuffle(out)
key = {}
for n, o in enumerate(out):
    key[f's{n + 1:03d}'] = o.pop('key'); o['id'] = f's{n + 1:03d}'
K = max(1, (len(out) + 9) // 10)
for i in range(K):
    json.dump(out[i::K], open(f'{C.S}/audit/in_S_{i}.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
json.dump(key, open(f'{C.S}/audit/key_S.json', 'w', encoding='utf-8', newline='\n'), indent=1)
print(len(out), K, collections.Counter(v.split('|')[0] for v in key.values()))
