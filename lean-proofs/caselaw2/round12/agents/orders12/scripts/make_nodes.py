"""Write round11/data_orders nodes.tsv + text/<id>.txt (FORMAT.md) from parse_jnl.py entries.jsonl.

Usage: python -I make_nodes.py <entries.jsonl> <sources.tsv> <out_dir> [<existing nodes.tsv to keep stable>]
Node classes: gvr, vacated, reversed, affirmed, granted_remanded, order_vacated; calendar ranges below.
If an existing nodes.tsv is given, its rows are kept first in their order (ids never reused) and new ids appended.
Also writes counts.tsv (entries per year per class over the ranges) and opinion_entries.tsv (entries printed under
Opinion(s) headings in the ranges; not nodes: the corpus holds the Court's opinions).
"""
import sys, os, json, re, collections, unicodedata, hashlib

NODE_CLASSES = ('gvr', 'vacated', 'reversed', 'affirmed', 'granted_remanded', 'order_vacated')
RANGES = (('20060301', '20091231'), ('20200701', '20251231'))


def in_range(d):
    return bool(d) and any(a <= d <= b for a, b in RANGES)


def clean(s):
    s = unicodedata.normalize('NFC', s).replace('\t', ' ').replace('\r', ' ').replace('\n', ' ').replace('\f', ' ')
    return re.sub(r' {2,}', ' ', s).strip()


def main():
    ent_path, src_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    old = sys.argv[4] if len(sys.argv) > 4 else None
    srcnames = set()
    for line in open(src_path, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) >= 6 and p[5]:
            srcnames.add(p[5])
    rows = [json.loads(l) for l in open(ent_path, encoding='utf-8')]
    ordinal = collections.Counter()
    for r in rows:
        ordinal[r['date']] += 1
        r['ord'] = ordinal[r['date']]
        r['id'] = 'jn%s_%03d' % (r['date'], r['ord'])
    ids = [r['id'] for r in rows if r['date']]
    assert len(ids) == len(set(ids)), 'duplicate ids'
    os.makedirs(os.path.join(out, 'text'), exist_ok=True)
    nodes = [r for r in rows if r['cls'] in NODE_CLASSES and in_range(r['date'])]
    nodes.sort(key=lambda r: (r['date'], r['ord']))
    kept = []
    if old and os.path.exists(old):
        kept = [l.rstrip('\n') for l in open(old, encoding='utf-8')][1:]
    kept_ids = set(l.split('\t')[0] for l in kept)
    lines = list(kept)
    n_new = 0
    for r in nodes:
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
        if lid in kept_ids:
            if open(tp, 'rb').read() != data:
                print('WARN text differs for kept id', lid, '(kept old file)')
            continue
        if os.path.exists(tp) and open(tp, 'rb').read() != data:
            raise SystemExit('refusing to change existing text ' + tp)
        with open(tp, 'wb') as f:
            f.write(data)
        row = [lid, ';'.join(r['dockets']) or '-', r['date'], clean(r['caption']) or '-',
               clean(r['disp']) or r['cls'], list_file, '%d-%d' % (r['first'], r['last'])]
        row = [x if x else '-' for x in row]
        assert all('\t' not in x for x in row)
        lines.append('\t'.join(row))
        n_new += 1
    with open(os.path.join(out, 'nodes.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('local_id\tdocket\tdate\tcaption\tdisposition\tlist_file\tline_span\n')
        for l in lines:
            f.write(l + '\n')
    # counts over the ranges (all entries), and node classes
    c = collections.Counter()
    courts = collections.defaultdict(collections.Counter)
    for r in rows:
        if not in_range(r['date']):
            continue
        y = r['date'][:4]
        c[(y, r['cls'])] += 1
        if r['cls'] in NODE_CLASSES:
            ct = r['court']
            kind = ('federal_circuit' if re.search(r'Court of Appeals for the', ct) else
                    'federal_district' if re.search(r'District Court', ct) else
                    'state' if ct != '-' else 'none')
            courts[y][kind] += 1
    classes = ['gvr', 'vacated', 'order_vacated', 'granted_remanded', 'reversed', 'affirmed', 'cert_denied',
               'dismissed', 'opinion', 'other']
    years = sorted(set(y for y, _ in c))
    with open(os.path.join(out, 'counts.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('year\t' + '\t'.join(classes) + '\tall_entries\tnodes\tnode_court_federal_circuit\t'
                'node_court_federal_district\tnode_court_state\tnode_court_none\n')
        for y in years:
            vals = [c[(y, k)] for k in classes]
            f.write('\t'.join([y] + [str(v) for v in vals] + [str(sum(vals)),
                    str(sum(c[(y, k)] for k in NODE_CLASSES))] +
                    [str(courts[y][k]) for k in ('federal_circuit', 'federal_district', 'state', 'none')]) + '\n')
    with open(os.path.join(out, 'opinion_entries.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('local_id\tdocket\tdate\tsection\tcaption\tlist_file\tline_span\n')
        for r in rows:
            if r['cls'] == 'opinion' and in_range(r['date']):
                f.write('\t'.join([r['id'], ';'.join(r['dockets']) or '-', r['date'], clean(r['section']),
                                   clean(r['caption']) or '-', r['journal'] + '.pdf',
                                   '%d-%d' % (r['first'], r['last'])]) + '\n')
    print('nodes', len(lines), 'new', n_new)


if __name__ == '__main__':
    main()
