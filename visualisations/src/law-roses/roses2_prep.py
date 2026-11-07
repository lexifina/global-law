"""roses2-scan.json -> compact rows for sections 11-20."""
import json, sys
a = {k: v for k, v in json.load(open(sys.argv[1], encoding='utf-8')).items() if v}
EXTRA = {'united-states', 'uae', 'bosnia'}
prefixes = sorted(set(a) | EXTRA, key=len, reverse=True)
SMALL = ('and', 'of', 'the', 'de', 'del', 'do', 'da', 'dos', 'la', 'y')
def title(s): return ' '.join(w if i and w in SMALL else w[:1].upper() + w[1:] for i, w in enumerate(s.split('-')))
SUBN = {'australia-northern-territory': 'Northern Territory', 'australia-south-australia': 'South Australia', 'canada-ontario': 'Ontario'}
COUNTRY = {'uae': 'UAE', 'bosnia': 'Bosnia', 'united-states': 'US'}
out = []
for k, v in a.items():
    par = next((p for p in prefixes if k.startswith(p + '-')), None)
    if par:
        place = k[len(par) + 1:]
        for suf in ('-city', '-municipal', '-regency'):
            if place.endswith(suf): place = place[: -len(suf)]
        name = f"{title(place)} ({COUNTRY.get(par, title(par))})"
    else:
        name = {'uk': 'United Kingdom'}.get(k, title(k))
    dec = [sum(n for y, n in v['born_dec'].items() if max(1890, int(y)) == d) for d in range(1890, 2030, 10)]
    out.append({'id': k, 'name': name, 'sub': bool(par), 'acts': v['acts'], 'files': v['files'],
                **{f: v[f] for f in ('pub_wd', 'pub_lag', 'ad_pub', 'size', 'mon_new', 'mon_rep', 'rest', 'life', 'since', 'versions')}, 'born': dec})
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8', newline='\n'), separators=(',', ':'), ensure_ascii=False)
print(len(out), sum(not r['sub'] for r in out))
