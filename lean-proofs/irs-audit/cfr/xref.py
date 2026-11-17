"""Code sections cited by 26 CFR sections in force (eCFR state in src/cfr HEAD) that no longer exist in Title 26."""
import re, os, glob, json, subprocess, collections
C = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/cfr'); U = os.path.expanduser(os.environ.get('USC_HISTORY', '~/united-states-law'))
have = {os.path.basename(f)[:-3] for f in glob.glob(U + '/title-26/*.md')}
cite = re.compile(r'(?<![§.\d])\b[Ss]ections? (\d{1,4}[A-Z]{0,2})(?=[\s(,.;:]|$)(?![^\n]{0,60}?\b(?:of the (?:Internal Revenue Code of 1939|\d{4} Code|Act|Tax Reform Act|Revenue Act|Technical|Social Security|Employee Retirement|Public Health)|of Public Law|of Pub\. L\.|of ERISA|of title|of the Code of 1939))')
hits = collections.defaultdict(list); nfiles = 0; ncites = 0
for f in sorted(glob.glob(C + '/title-26-part-*/*.md')):
    nfiles += 1
    t = open(f, encoding='utf-8').read()
    for m in cite.finditer(t):
        s = m.group(1); ncites += 1
        if s not in have:
            hits[s].append((os.path.relpath(f, C), t[max(0, m.start()-80): m.end()+60].replace('\n', ' ')))
res = {}
for s, L in sorted(hits.items(), key=lambda kv: -len(kv[1])):
    log = subprocess.run(['git', '-C', U, 'log', '-1', '--diff-filter=D', '--format=%ad|%an|%s', '--date=short', '--', 'title-26/%s.md' % s], capture_output=True, text=True).stdout.strip()
    res[s] = dict(n=len(L), files=len({x[0] for x in L}), deleted=log, examples=L[:3])
json.dump(dict(files=nfiles, cites=ncites, missing=res), open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cfr/xref.json'), 'w'), indent=1)
print('CFR section files', nfiles, 'code citations', ncites, 'cited sections absent from current Title 26:', len(res),
      'citations', sum(v['n'] for v in res.values()))
print('with a recorded repeal commit:', sum(1 for v in res.values() if v['deleted']))
for s, v in list(res.items())[:25]: print(s, v['n'], v['files'], v['deleted'][:110])
