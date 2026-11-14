"""counts.tsv over every held Journal year: entries per class (all entries) and nodes per year from nodes.tsv.
python -I counts2.py <entries.jsonl> <nodes.tsv> <out counts.tsv>"""
import sys, json, collections
ent, nodes, out = sys.argv[1:4]
c = collections.Counter()
for l in open(ent, encoding='utf-8'):
    r = json.loads(l)
    c[(r['date'][:4], r['cls'])] += 1
nc = collections.Counter(l.split('\t')[2][:4] for l in list(open(nodes, encoding='utf-8'))[1:])
classes = ['gvr', 'vacated', 'order_vacated', 'granted_remanded', 'reversed', 'affirmed', 'cert_denied', 'dismissed',
           'opinion', 'other']
years = sorted(set(y for y, _ in c))
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write('year\t' + '\t'.join(classes) + '\tall_entries\tnodes_in_nodes_tsv\n')
    for y in years:
        v = [c[(y, k)] for k in classes]
        f.write('\t'.join([y] + [str(x) for x in v] + [str(sum(v)), str(nc[y])]) + '\n')
