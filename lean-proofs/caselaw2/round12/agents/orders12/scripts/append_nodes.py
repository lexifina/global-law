"""Append order nodes for Journal entries whose docket has no corpus Supreme Court node nearby (lead rule, 06:0x).

Usage: python -I append_nodes.py <entries.jsonl> <sources.tsv> <data_orders dir> <report.tsv>
Rule: every parsed Journal entry with a node class (gvr, vacated, order_vacated, granted_remanded, affirmed, reversed)
that is not already a node, and at least one of whose dockets is not the docket of a corpus court-2906 node dated within
+-10 days of the entry's date, becomes a node. Existing rows and text files are never changed; new rows are appended
after the existing ones, in date order. Corpus side: round-6 cache supreme-court.*.meta.tsv.gz (node, date, docket).
"""
import sys, os, re, json, glob, gzip, datetime, collections, unicodedata

C2 = os.path.expanduser('~/Documents/us-caselaw-lean-work/caselaw-lean-2')
NODE_CLASSES = ('gvr', 'vacated', 'order_vacated', 'granted_remanded', 'affirmed', 'reversed')
WINDOW = 10


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
    srcnames = set()
    for line in open(src_path, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) >= 6 and p[5]:
            srcnames.add(p[5])
    corp = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(C2, 'round6', 'history', 'cache', 'supreme-court.*.meta.tsv.gz'))):
        with gzip.open(p, 'rt', encoding='utf-8', newline='\n') as f:
            for line in f:
                r = line.rstrip('\n').split('\t')
                if len(r) >= 11 and r[4] == '2906' and re.match(r'\d{8}$', r[3]):
                    for k in dkeys(r[5]):
                        corp[k].append(day(r[3]))
    nodes_path = os.path.join(out, 'nodes.tsv')
    existing = [l.rstrip('\n') for l in open(nodes_path, encoding='utf-8')]
    header, old_rows = existing[0], existing[1:]
    old_ids = set(l.split('\t')[0] for l in old_rows)
    rows = [json.loads(l) for l in open(ent_path, encoding='utf-8')]
    ordinal = collections.Counter()
    for r in rows:
        ordinal[r['date']] += 1
        r['id'] = 'jn%s_%03d' % (r['date'], ordinal[r['date']])
        r['ord'] = ordinal[r['date']]
    assert len(set(r['id'] for r in rows)) == len(rows)
    cand = [r for r in rows if r['cls'] in NODE_CLASSES and r['id'] not in old_ids]
    cand.sort(key=lambda r: (r['date'], r['ord']))
    new_lines = []
    report = []
    for r in cand:
        dd = day(r['date'])
        keys = []
        for d in r['dockets']:
            keys += dkeys(d.replace(',Original', ', Orig').replace('Original', 'Orig'))
        if not keys:
            continue
        covered = [k for k in keys if any(abs((x - dd).days) <= WINDOW for x in corp.get(k, []))]
        if len(covered) == len(keys):
            report.append([r['id'], r['date'], r['cls'], ';'.join(r['dockets']), 'covered'])
            continue
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
               clean(r['disp']) or r['cls'], list_file, '%d-%d' % (r['first'], r['last'])]
        row = [x if x else '-' for x in row]
        assert all('\t' not in x for x in row)
        new_lines.append('\t'.join(row))
        report.append([r['id'], r['date'], r['cls'], ';'.join(r['dockets']),
                       'added_partial' if covered else 'added'])
    with open(nodes_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(header + '\n')
        for l in old_rows + new_lines:
            f.write(l + '\n')
    with open(rep, 'w', encoding='utf-8', newline='\n') as f:
        f.write('local_id\tdate\tclass\tdockets\toutcome\n')
        for x in report:
            f.write('\t'.join(x) + '\n')
    print('old', len(old_rows), 'added', len(new_lines), 'candidates covered',
          sum(1 for x in report if x[4] == 'covered'))


if __name__ == '__main__':
    main()
