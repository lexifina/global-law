"""IRC sections cited in the current IRM ("IRC 6651", "IRC 6651(a)(1)") that are absent from current Title 26."""
import re, os, glob, json, subprocess, collections
U = os.path.expanduser(os.environ.get('USC_HISTORY', '~/united-states-law'))
have = {os.path.basename(f)[:-3] for f in glob.glob(U + '/title-26/*.md')}
cite = re.compile(r'\bIRC (?:§ ?)?(\d{1,4}[A-Z]{0,2})(?=[\s(,.;:)]|$)')
hits = collections.defaultdict(list); nf = nc = 0
for f in sorted(glob.glob(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/irm/txt/*.txt'))):
    nf += 1; t = open(f).read()
    for m in cite.finditer(t):
        nc += 1
        if m.group(1) not in have:
            hits[m.group(1)].append((os.path.basename(f), t[max(0, m.start()-100): m.end()+80].replace('\n', ' ')))
res = {}
for s, L in sorted(hits.items(), key=lambda kv: -len(kv[1])):
    log = subprocess.run(['git', '-C', U, 'log', '-1', '--diff-filter=D', '--format=%ad|%an', '--date=short', '--', 'title-26/%s.md' % s], capture_output=True, text=True).stdout.strip()
    res[s] = dict(n=len(L), pages=len({x[0] for x in L}), deleted=log, examples=L[:3])
json.dump(dict(pages=nf, cites=nc, missing=res), open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/irm/xref.json'), 'w'), indent=1)
print('IRM pages', nf, 'IRC citations', nc, 'absent sections', len(res), 'citations', sum(v['n'] for v in res.values()), 'with repeal commit', sum(1 for v in res.values() if v['deleted']))
for s, v in list(res.items())[:15]: print(s, v['n'], v['pages'], v['deleted'], '|', v['examples'][0][1][:150])
