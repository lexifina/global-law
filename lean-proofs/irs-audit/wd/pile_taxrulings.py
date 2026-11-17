import lzma, json, os, re, collections
D = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cache/huggingface.co/datasets/pile-of-law/pile-of-law/resolve/main/data/')
ids = collections.Counter(); yrs = collections.Counter(); kinds = collections.Counter(); n = 0; noid = 0; samples = []
cites = collections.Counter()
for split in ('train', 'validation'):
    with lzma.open(D + '%s.taxrulings.jsonl.xz' % split, 'rt') as f:
        for line in f:
            r = json.loads(line); t = r['text']; n += 1
            if len(samples) < 2: samples.append(t[:400])
            m = re.search(r'(?:Number|Index Number|Release Number|Document Number)\s*:?\s*(\d{7,9})', t[:3000])
            if not m: m = re.search(r'\b((?:19|20)?\d{2}[0-5]\d\d{3})\b', t[:1500])
            if m:
                num = m.group(1); ids[num] += 1
                y = num[:4] if len(num) == 9 else ('19' + num[:2] if num[:2] > '50' else '20' + num[:2]); yrs[y] += 1
            else: noid += 1
            head = t[:4000]
            k = 'TAM' if re.search(r'(?i)technical advice memorandum', head) else 'CCA' if re.search(r'(?i)chief counsel advice|office of chief counsel', head) and not re.search(r'Dear ', head) else 'FSA' if re.search(r'(?i)field service advice', head) else 'PLR' if re.search(r'Dear |This letter responds|This is in reply', head) else 'other'
            kinds[k] += 1
print('records', n, 'with id', n - noid, 'distinct ids', len(ids), 'duplicates', sum(v - 1 for v in ids.values() if v > 1))
print('kinds', dict(kinds)); print('years', sorted(yrs.items()))
for s in samples: print('---', ' '.join(s.split())[:300])
json.dump(dict(records=n, distinct=len(ids), kinds=kinds, years=dict(sorted(yrs.items()))), open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/wd/pile_taxrulings.json'), 'w'), indent=1)
json.dump(sorted(ids), open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/wd/pile_ids.json'), 'w'))
