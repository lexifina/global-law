"""(The title-26 history records most sections only from the 1994 edition, dated 1995-01-04: a section first seen
then is not "added later".) Code citations in the Cumulative Bulletins 1987-1995 (items split on their headings in reading-order text) against the
US Code history (title-26 files; first commit 1986): a section cited in a volume of year Y that (a) was deleted before
1 Jan Y and is not in the Code again by then, or (b) first appears after 31 Dec Y. -> src/govinfo/cb_cites.json"""
import os, re, glob, json, subprocess, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); U = os.path.expanduser(os.environ.get('USC_HISTORY', '~/united-states-law'))
log = subprocess.run(['git', '-C', U, 'log', '--reverse', '--format=@%ad', '--date=short', '--name-status', '--', 'title-26/'], capture_output=True, text=True).stdout
ev = collections.defaultdict(list); d = None
for l in log.splitlines():
    if l.startswith('@'): d = l[1:]; continue
    p = l.split('\t')
    if len(p) >= 2 and p[-1].startswith('title-26/') and p[-1].endswith('.md'):
        ev[os.path.basename(p[-1])[:-3]].append((d, p[0][0]))
def present(s, date):
    st = False; seen = False
    for dd, k in ev.get(s, []):
        if dd > date: break
        seen = True; st = k != 'D'
    return st, seen
HEAD = re.compile(r'^\s*(Rev\. ?Rul\.|Rev\. ?Proc\.|T\. ?D\.|Notice|Announcement)\s*(\d[\d–-]*)\s*$', re.M)
CITE = re.compile(r'(?:§§? ?|\b[Ss]ections? )(\d{1,4}[A-Z]{0,2})(?=\(|\s|,|\.(?!\d))')
res = collections.Counter(); flags = []
for f in sorted(glob.glob(H + '/src/govinfo/raw/19[89]*_*.txt')):
    y = int(os.path.basename(f)[:4])
    if not 1987 <= y <= 1995: continue
    t = open(f, errors='replace').read()
    hs = list(HEAD.finditer(t)); res['items'] += len(hs)
    date_end = '%d-12-31' % y; date_start = '%d-01-01' % y
    for i, h in enumerate(hs):
        body = t[h.start(): hs[i + 1].start() if i + 1 < len(hs) else len(t)]
        flat = ' '.join(body.split())
        for m in CITE.finditer(flat):
            s = m.group(1); res['cites'] += 1
            ctx = flat[max(0, m.start() - 90): m.end() + 70]
            if re.search(r'(?i)former|repeal|1939|1954 Code|prior to (its )?amendment|U\.S\.C|ERISA|Act of|Public Law|Pub\. L', ctx): res['context_skip'] += 1; continue
            if re.match(r'\s+of\s+(?!the (Internal Revenue )?Code)', flat[m.end(): m.end() + 30]): continue
            now, seen = present(s, date_end)
            if not seen:
                if s in ev and ev[s][0][0] > '1995-01-04': flags.append(dict(kind='added_later', vol=y, item=h.group(1) + ' ' + h.group(2), sec=s, first=ev[s][0][0], ctx=ctx))
                else: res['never_in_code'] += 1
            elif not now and not present(s, date_start)[0]:
                flags.append(dict(kind='deleted_before', vol=y, item=h.group(1) + ' ' + h.group(2), sec=s, ctx=ctx))
res['flags'] = len(flags)
json.dump(dict(summary=res, flags=flags), open(H + '/src/govinfo/cb_cites.json', 'w'), indent=0)
print(dict(res)); print(collections.Counter((x['kind'], x['sec']) for x in flags).most_common(25))
