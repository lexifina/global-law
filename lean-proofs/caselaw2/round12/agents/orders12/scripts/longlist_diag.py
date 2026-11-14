"""2005 long lists: for each Journal GVR-class entry of a year, the corpus court-2906 node(s) of its docket within
+-10 days, and how many OTHER docket numbers / captions that node's text prints (a long list = many).

python -I longlist_diag.py <entries.jsonl> <year> <out.tsv> [<h0 cases tsv> (counting only)]
Corpus side: round-6 cache meta (court 2906) + texts via round6/history/r6lib.fetch_texts. The h0 file, if given, is
used only to count how the h0 outcome splits by the long-list measure (node, order_date, sc_dockets, agree columns);
no rule reads it.
"""
import sys, os, re, json, glob, gzip, datetime, collections

C2 = os.path.expanduser('~/Documents/us-caselaw-lean-work/caselaw-lean-2')
sys.path.insert(0, os.path.join(C2, 'round6', 'history'))
import r6lib as L  # noqa: E402

NODE_CLASSES = ('gvr', 'vacated', 'order_vacated', 'granted_remanded', 'affirmed', 'reversed')
DK_RE = re.compile(r'\b\d{2}[-–—‑]\d{1,5}\b|\b\d{2}[AM]\d{1,4}\b')


def dkeys(s):
    s = re.sub(r'[–—‑−]', '-', s or '')
    return re.findall(r'\b\d{2}-\d{1,5}\b|\b\d{2}[AM]\d{1,4}\b|\bD-\d{1,5}\b', s)


def day(d):
    return datetime.date(int(d[:4]), int(d[4:6]), int(d[6:8]))


def main():
    ent, year, outp = sys.argv[1:4]
    years = set(year.split(','))  # one year or a comma list
    lo, hi = str(int(min(years)) - 1), str(int(max(years)) + 1)
    h0 = sys.argv[4] if len(sys.argv) > 4 else None
    corp = {}
    by_dk = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(C2, 'round6', 'history', 'cache', 'supreme-court.*.meta.tsv.gz'))):
        for r in L.meta_rows(p):
            if r[4] == '2906' and re.match(r'\d{8}$', r[3]) and lo <= r[3][:4] <= hi:
                corp[int(r[0])] = r
                for k in dkeys(r[5]):
                    by_dk[k].append(int(r[0]))
    rows = [json.loads(l) for l in open(ent, encoding='utf-8')]
    rows = [r for r in rows if r['date'] and r['date'][:4] in years and r['cls'] in NODE_CLASSES]
    need = set()
    pairs = []
    for r in rows:
        dd = day(r['date'])
        hits = []
        for d in r['dockets']:
            for n in by_dk.get(d, []):
                if abs((day(corp[n][3]) - dd).days) <= 10 and n not in hits:
                    hits.append(n)
        pairs.append((r, hits))
        need.update(hits)
    texts = L.fetch_texts(sorted(need))
    out = []
    for r, hits in pairs:
        own = set(r['dockets'])
        for n in hits or [None]:
            if n is None:
                out.append([r['date'], ';'.join(r['dockets']), r['cls'], '-', '-', '-', '0', '0', '0', '0'])
                continue
            t = texts.get(n, ('', ''))[1] or ''
            dks = set(re.sub(r'[–—‑]', '-', x) for x in DK_RE.findall(t))
            others = dks - own
            vs = len(re.findall(r'\bv\.\s', t))
            out.append([r['date'], ';'.join(r['dockets']), r['cls'], str(n), corp[n][3], corp[n][5] or '-',
                        str(len(t)), str(len(dks)), str(len(others)), str(vs)])
    with open(outp, 'w', encoding='utf-8', newline='\n') as f:
        f.write('date\tdockets\tclass\tnode\tnode_date\tnode_docket_field\ttext_len\tdockets_in_text\t'
                'other_dockets_in_text\tv_count\n')
        for x in out:
            f.write('\t'.join(x) + '\n')
    # summary
    oth = collections.Counter()
    for x in out:
        o = int(x[8])
        b = '0' if o == 0 else '1-2' if o <= 2 else '3-9' if o <= 9 else '10-49' if o <= 49 else '50+'
        oth[(x[0][:4], x[2], b)] += 1
    print('entries', len(pairs), 'with corpus node', sum(1 for _, h in pairs if h), 'pairs', len(out))
    for k in sorted(oth):
        print(' ', k, oth[k])
    if h0:
        # counting only: h0 orders of this year by outcome, against the measure of the corpus node of the docket
        meas = {}
        for x in out:
            for d in x[1].split(';'):
                meas.setdefault((d, x[0]), []).append(int(x[8]))
        c = collections.Counter()
        hd = None
        for line in open(h0, encoding='utf-8'):
            f = line.rstrip('\n').split('\t')
            if hd is None:
                hd = f
                continue
            r = dict(zip(hd, f))
            if r['order_date'][:4] not in years or r['class'] not in ('NEG', 'PART'):
                continue
            ds = [d.strip() for d in r['sc_dockets'].split(',')]
            m = [v for d in ds for v in meas.get((d, r['order_date']), [])]
            b = 'no_journal_entry' if not m else ('long(>=10 other)' if max(m) >= 10 else
                                                  'mid(3-9)' if max(m) >= 3 else 'short(<=2)')
            c[(r['class'], r['sub'], 'agree' if r['agree'] == '1' else 'miss', b)] += 1
        print('h0 (counting only):')
        for k in sorted(c):
            print(' ', k, c[k])


if __name__ == '__main__':
    main()
