"""round12/data_orders base: round 11's nodes (same ids, same order), texts rebuilt from the glyph-aware Journal parse.

python -I build_base.py <round11 data_orders> <new entries.jsonl> <round12 data_orders>
For each round-11 node: the text is rebuilt from the re-parsed entry exactly as make_nodes.py builds it; if it equals
the round-11 file the bytes are copied, else the new text is written, the nodes.tsv caption / disposition columns are
updated from the re-parse (docket, date, list_file, line_span must be unchanged) and a CHANGED.tsv line is written.
"""
import sys, os, json, re, hashlib, collections, unicodedata

NODE_CLASSES = ('gvr', 'vacated', 'order_vacated', 'granted_remanded', 'affirmed', 'reversed')


def clean(s):
    s = unicodedata.normalize('NFC', s).replace('\t', ' ').replace('\r', ' ').replace('\n', ' ').replace('\f', ' ')
    return re.sub(r' {2,}', ' ', s).strip()


def node_text(r):
    t = [clean(r['datehead'])]
    if r['section'] != '-':
        t.append(clean(r['section']))
    t += [clean(c) for c in r['caplines'] if clean(c)]
    if clean(r['body']):
        t.append(clean(r['body']))
    return ('\n'.join(t) + '\n').encode('utf-8')


def words(a, b):
    wa, wb = re.findall(r'\S+', a), re.findall(r'\S+', b)
    if len(wa) != len(wb):
        return 'word count %d->%d' % (len(wa), len(wb))
    c = collections.Counter('%s->%s' % (x, y) for x, y in zip(wa, wb) if x != y)
    return ', '.join('%s%s' % (k, ' x%d' % v if v > 1 else '') for k, v in c.items())


def main():
    r11, ent, out = sys.argv[1:4]
    rows = [json.loads(l) for l in open(ent, encoding='utf-8')]
    ordinal = collections.Counter()
    by_id = {}
    for r in rows:
        ordinal[r['date']] += 1
        r['id'] = 'jn%s_%03d' % (r['date'], ordinal[r['date']])
        by_id[r['id']] = r
    lines = [l.rstrip('\n') for l in open(os.path.join(r11, 'nodes.tsv'), encoding='utf-8')]
    header, old = lines[0], [l.split('\t') for l in lines[1:]]
    os.makedirs(os.path.join(out, 'text'), exist_ok=True)
    new_rows, changed = [], []
    for row in old:
        lid = row[0]
        r = by_id[lid]
        assert r['cls'] in NODE_CLASSES, lid
        assert '%d-%d' % (r['first'], r['last']) == row[6], lid
        assert r['journal'] + '.pdf' == row[5], lid
        assert (';'.join(r['dockets']) or '-') == row[1] and r['date'] == row[2], lid
        oldb = open(os.path.join(r11, 'text', lid + '.txt'), 'rb').read()
        newb = node_text(r)
        tp = os.path.join(out, 'text', lid + '.txt')
        if newb == oldb:
            with open(tp, 'wb') as f:
                f.write(oldb)
            new_rows.append(row)
            continue
        with open(tp, 'wb') as f:
            f.write(newb)
        nrow = list(row)
        nrow[3] = clean(r['caption']) or '-'
        nrow[4] = clean(r['disp']) or r['cls']
        what = []
        if nrow[3] != row[3]:
            what.append('caption')
        if nrow[4] != row[4]:
            what.append('disposition words')
        what.append('ligature repair: ' + words(oldb.decode('utf-8'), newb.decode('utf-8')))
        changed.append([lid, hashlib.sha1(oldb).hexdigest(), hashlib.sha1(newb).hexdigest(), '; '.join(what)])
        new_rows.append(nrow)
    with open(os.path.join(out, 'nodes.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(header + '\n')
        for r in new_rows:
            f.write('\t'.join(r) + '\n')
    with open(os.path.join(out, 'CHANGED.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('local_id\told_sha1\tnew_sha1\twhat_changed\n')
        for c in changed:
            f.write('\t'.join(c) + '\n')
    print('nodes', len(new_rows), 'changed', len(changed))


if __name__ == '__main__':
    main()
