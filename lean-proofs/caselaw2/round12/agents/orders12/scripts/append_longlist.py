"""Append per-entry Journal nodes for entries whose corpus Supreme Court node is a multi-docket long list (round 12,
step 3; src tag r12:longlist).

Usage: python -I append_longlist.py <entries.jsonl> <sources.tsv> <data_orders dir> <report.tsv> [k_main=10] [k_low=3]
Rule: a parsed Journal entry of a node class (gvr, vacated, order_vacated, granted_remanded, affirmed, reversed) that is
not already a node, every docket of which has a corpus court-2906 node dated within +-10 days (else round 11's rule
already made it a node), and one of whose dockets' corpus nodes within +-10 days lists in its docket field at least k
docket numbers other than the entry's own (the corpus node is one text for a printed list of many cases) becomes a
node. Rows with k >= k_main come first (date order), then rows with k_low <= k < k_main (date order), so the file can
be cut after the first group without moving any node id. nodes.tsv gains the optional 8th column `src`
(`-` = default r11:orderlist for the existing rows; `r12:longlist` for these rows). Existing rows and texts unchanged.
Corpus side: round-6 cache supreme-court.*.meta.tsv.gz (node, date, docket field).
"""
import sys, os, re, json, glob, gzip, datetime, collections, unicodedata

C2 = os.path.expanduser('~/Documents/us-caselaw-lean-work/caselaw-lean-2')
NODE_CLASSES = ('gvr', 'vacated', 'order_vacated', 'granted_remanded', 'affirmed', 'reversed')
WINDOW = 10
SRC = 'r12:longlist'
HEADER = 'local_id\tdocket\tdate\tcaption\tdisposition\tlist_file\tline_span'


def clean(s):
    s = unicodedata.normalize('NFC', s).replace('\t', ' ').replace('\r', ' ').replace('\n', ' ').replace('\f', ' ')
    return re.sub(r' {2,}', ' ', s).strip()


def dkeys(s):
    s = re.sub(r'[–—‑−]', '-', s or '')
    out = re.findall(r'\b\d{2}-\d{1,5}\b|\b\d{2}[AM]\d{1,4}\b|\bD-\d{1,5}\b', s)
    out += ['%sorig' % m for m in re.findall(r'\b(\d{1,3}),? Orig', s)]
    return out


def day(d):
    return datetime.date(int(d[:4]), int(d[4:6]), int(d[6:8]))


def main():
    ent_path, src_path, out, rep = sys.argv[1:5]
    k_main = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    k_low = int(sys.argv[6]) if len(sys.argv) > 6 else 3
    srcnames = set()
    for line in open(src_path, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) >= 6 and p[5]:
            srcnames.add(p[5])
    corp = collections.defaultdict(list)  # docket -> [(date, node, set of field dockets)]
    for p in sorted(glob.glob(os.path.join(C2, 'round6', 'history', 'cache', 'supreme-court.*.meta.tsv.gz'))):
        with gzip.open(p, 'rt', encoding='utf-8', newline='\n') as f:
            for line in f:
                r = line.rstrip('\n').split('\t')
                if len(r) >= 11 and r[4] == '2906' and re.match(r'\d{8}$', r[3]):
                    ks = dkeys(r[5])
                    fs = frozenset(ks)
                    for k in ks:
                        corp[k].append((day(r[3]), r[0], fs))
    nodes_path = os.path.join(out, 'nodes.tsv')
    existing = [l.rstrip('\n') for l in open(nodes_path, encoding='utf-8')]
    header, old_rows = existing[0], existing[1:]
    if header == HEADER:
        old_rows = [l + '\t-' for l in old_rows]
    elif header != HEADER + '\tsrc':
        raise SystemExit('unexpected header')
    old_ids = set(l.split('\t')[0] for l in old_rows)
    rows = [json.loads(l) for l in open(ent_path, encoding='utf-8')]
    ordinal = collections.Counter()
    for r in rows:
        ordinal[r['date']] += 1
        r['ord'] = ordinal[r['date']]
        r['id'] = 'jn%s_%03d' % (r['date'], r['ord'])
    assert len(set(r['id'] for r in rows)) == len(rows)
    cand = [r for r in rows if r['cls'] in NODE_CLASSES and r['id'] not in old_ids]
    cand.sort(key=lambda r: (r['date'], r['ord']))
    tiers = {'main': [], 'low': []}
    report = []
    for r in cand:
        dd = day(r['date'])
        keys = []
        for d in r['dockets']:
            keys += dkeys(d.replace(',Original', ', Orig').replace('Original', 'Orig'))
        if not keys:
            continue
        near = {k: [x for x in corp.get(k, []) if abs((x[0] - dd).days) <= WINDOW] for k in keys}
        if not all(near.values()):
            report.append([r['id'], r['date'], r['cls'], ';'.join(r['dockets']), '-', '-', 'not_covered(r11 rule)'])
            continue
        own = set(keys)
        best, best_node = -1, '-'
        for k, xs in near.items():
            for (_, node, fs) in xs:
                o = len(fs - own)
                if o > best:
                    best, best_node = o, node
        tier = 'main' if best >= k_main else 'low' if best >= k_low else None
        report.append([r['id'], r['date'], r['cls'], ';'.join(r['dockets']), best_node, str(best),
                       {'main': 'added_k%d' % k_main, 'low': 'added_k%d' % k_low, None: 'short_list'}[tier]])
        if tier:
            tiers[tier].append(r)
    new_lines = []
    for tier in ('main', 'low'):
        for r in tiers[tier]:
            lid = r['id']
            list_file = r['journal'] + '.pdf'
            assert list_file in srcnames, list_file
            text_lines = [clean(r['datehead'])]
            if r['section'] != '-':
                text_lines.append(clean(r['section']))
            text_lines += [clean(c) for c in r['caplines'] if clean(c)]
            if clean(r['body']):
                text_lines.append(clean(r['body']))
            data = ('\n'.join(text_lines) + '\n').encode('utf-8')
            tp = os.path.join(out, 'text', lid + '.txt')
            if os.path.exists(tp):
                raise SystemExit('refusing to overwrite ' + tp)
            with open(tp, 'wb') as f:
                f.write(data)
            row = [lid, ';'.join(r['dockets']) or '-', r['date'], clean(r['caption']) or '-',
                   clean(r['disp']) or r['cls'], list_file, '%d-%d' % (r['first'], r['last']), SRC]
            row = [x if x else '-' for x in row]
            assert all('\t' not in x for x in row)
            new_lines.append('\t'.join(row))
    with open(nodes_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(HEADER + '\tsrc\n')
        for l in old_rows + new_lines:
            f.write(l + '\n')
    with open(rep, 'w', encoding='utf-8', newline='\n') as f:
        f.write('local_id\tdate\tclass\tdockets\tcorpus_node\tother_dockets_in_field\toutcome\n')
        for x in report:
            f.write('\t'.join(x) + '\n')
    print('old', len(old_rows), 'added main(k>=%d)' % k_main, len(tiers['main']), 'added low(%d<=k<%d)' % (k_low, k_main),
          len(tiers['low']), 'short lists', sum(1 for x in report if x[6] == 'short_list'))


if __name__ == '__main__':
    main()
