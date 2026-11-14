"""Measure what the ligature repair changes: entries (class, dockets, caption, court, disposition words, node decision)
and node texts of an existing data_orders folder.

python -I lig_measure.py <old entries.jsonl> <new entries.jsonl> <data_orders dir (round 11)> <out dir>
Entries are matched by (journal, first line, last line). Node texts are rebuilt from the new entries exactly as
make_nodes.py / append_nodes.py build them and compared with the existing text files (sha1).
Writes <out>/entry_changes.tsv, <out>/node_changes.tsv (local id, old sha1, new sha1, what changed), <out>/summary.txt.
"""
import sys, os, json, re, hashlib, collections, unicodedata

NODE_CLASSES = ('gvr', 'vacated', 'order_vacated', 'granted_remanded', 'affirmed', 'reversed')


def clean(s):
    s = unicodedata.normalize('NFC', s).replace('\t', ' ').replace('\r', ' ').replace('\n', ' ').replace('\f', ' ')
    return re.sub(r' {2,}', ' ', s).strip()


def load(p):
    rows = [json.loads(l) for l in open(p, encoding='utf-8')]
    ordinal = collections.Counter()
    for r in rows:
        ordinal[r['date']] += 1
        r['id'] = 'jn%s_%03d' % (r['date'], ordinal[r['date']])
    return rows


def node_text(r):
    t = [clean(r['datehead'])]
    if r['section'] != '-':
        t.append(clean(r['section']))
    t += [clean(c) for c in r['caplines'] if clean(c)]
    if clean(r['body']):
        t.append(clean(r['body']))
    return ('\n'.join(t) + '\n').encode('utf-8')


def words(a, b):
    """the words that differ between two texts (old -> new)"""
    wa, wb = re.findall(r'\S+', a), re.findall(r'\S+', b)
    if len(wa) != len(wb):
        return 'word count %d->%d' % (len(wa), len(wb))
    d = ['%s->%s' % (x, y) for x, y in zip(wa, wb) if x != y]
    return ' '.join(d)


def main():
    old, new = load(sys.argv[1]), load(sys.argv[2])
    dorders, out = sys.argv[3], sys.argv[4]
    os.makedirs(out, exist_ok=True)
    assert len(old) == len(new)
    fields = ('cls', 'dockets', 'caption', 'court', 'disp', 'id')
    ch = collections.Counter()
    by_journal = collections.Counter()
    ent_lines = []
    newmap = {}
    for a, b in zip(old, new):
        assert (a['journal'], a['first'], a['last']) == (b['journal'], b['first'], b['last'])
        newmap[a['id']] = b
        diff = [f for f in fields if a[f] != b[f]]
        if a['caplines'] != b['caplines'] or a['body'] != b['body']:
            diff.append('text')
        if not diff:
            continue
        for f in diff:
            ch[f] += 1
        by_journal[a['journal']] += 1
        isnode_a, isnode_b = a['cls'] in NODE_CLASSES, b['cls'] in NODE_CLASSES
        if isnode_a != isnode_b:
            ch['node_class_flip'] += 1
        ent_lines.append([a['journal'], '%d-%d' % (a['first'], a['last']), a['id'], ','.join(diff), a['cls'], b['cls'],
                          words(a['caption'], b['caption']) or '-'])
    with open(os.path.join(out, 'entry_changes.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('journal\tline_span\tentry_id\tfields_changed\told_class\tnew_class\tcaption_words_changed\n')
        for l in ent_lines:
            f.write('\t'.join(l) + '\n')
    # nodes
    nl = [l.rstrip('\n').split('\t') for l in open(os.path.join(dorders, 'nodes.tsv'), encoding='utf-8')][1:]
    node_lines = []
    nch = collections.Counter()
    caps = []
    for row in nl:
        lid = row[0]
        oldb = open(os.path.join(dorders, 'text', lid + '.txt'), 'rb').read()
        r = newmap[lid]
        newb = node_text(r)
        if oldb == newb:
            continue
        what = []
        if clean(r['caption']) != row[3]:
            what.append('caption')
            caps.append((lid, words(row[3], clean(r['caption']))))
        if (clean(r['disp']) or r['cls']) != row[4]:
            what.append('disposition_words')
        if r['cls'] not in NODE_CLASSES:
            what.append('class_now_' + r['cls'])
        what.append('text: ' + words(oldb.decode('utf-8'), newb.decode('utf-8')))
        for w in what[:-1]:
            nch[w] += 1
        nch['text'] += 1
        node_lines.append([lid, hashlib.sha1(oldb).hexdigest(), hashlib.sha1(newb).hexdigest(), '; '.join(what)])
    with open(os.path.join(out, 'node_changes.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('local_id\told_sha1\tnew_sha1\twhat_changed\n')
        for l in node_lines:
            f.write('\t'.join(l) + '\n')
    with open(os.path.join(out, 'summary.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('entries changed: %d of %d\n' % (len(ent_lines), len(old)))
        f.write('fields: %s\n' % dict(ch))
        f.write('by journal: %s\n' % dict(by_journal))
        f.write('nodes (of %d) whose text changes: %d; %s\n' % (len(nl), len(node_lines), dict(nch)))
        for lid, w in caps:
            f.write('caption %s %s\n' % (lid, w))
    print(open(os.path.join(out, 'summary.txt'), encoding='utf-8').read())


if __name__ == '__main__':
    main()
