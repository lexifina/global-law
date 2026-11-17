"""Pile of Law: inventory of IRS written determinations and Chief Counsel memos (counts, dates, URL naming).
Amounts are redacted in this dataset ("dollar_figure"): used for counts, dates and citations only."""
import lzma, json, os, re, collections
D = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cache/huggingface.co/datasets/pile-of-law/pile-of-law/resolve/main/data/')
out = {}
for name in ('taxrulings', 'irs_legal_advice_memos'):
    recs = []
    for split in ('train', 'validation'):
        with lzma.open(D + '%s.%s.jsonl.xz' % (split, name), 'rt') as f:
            for line in f:
                r = json.loads(line); r.pop('text', None) if False else None
                recs.append({k: (v if k != 'text' else len(v)) for k, v in r.items()})
    keys = collections.Counter(k for r in recs for k in r)
    dirs = collections.Counter(); pat = collections.Counter(); ex = collections.defaultdict(list); years = collections.Counter()
    for r in recs:
        u = r.get('url') or ''
        m = re.search(r'/pub/(irs-[a-z]+)/([^/?#]+)$', u)
        d = m.group(1) if m else re.sub(r'https?://[^/]+', '', u)[:40]
        dirs[d] += 1
        if m:
            shape = re.sub(r'\d', '9', m.group(2)); pat[(d, shape)] += 1
            if len(ex[(d, shape)]) < 2: ex[(d, shape)].append(m.group(2))
        ts = str(r.get('created_timestamp') or '')
        years[ts[:4] if ts[:4].isdigit() else ts[-4:]] += 1
    out[name] = dict(n=len(recs), keys=dict(keys), dirs=dict(dirs), shapes={'%s %s' % k: v for k, v in pat.most_common(40)},
                     examples={'%s %s' % k: v for k, v in ex.items()}, years=dict(sorted(years.items())))
    print(name, len(recs), dict(keys)); print(' dirs', dirs.most_common(10)); print(' shapes', pat.most_common(15)); print(' examples', dict(list(ex.items())[:15])); print(' years', sorted(years.items())[:40])
json.dump(out, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/wd/pile_inventory.json'), 'w'), indent=1)
