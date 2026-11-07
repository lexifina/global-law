"""analysis11.json (round 11, every law repo) -> compact per-jurisdiction data for the rose page."""
import json, sys
from datetime import date, timedelta
a = json.load(open(sys.argv[1], encoding='utf-8'))
SUB = {'australia-northern-territory': 'Northern Territory', 'australia-south-australia': 'South Australia',
       'australia-australian-capital-territory': 'Australian Capital Territory', 'canada-ontario': 'Ontario'}
def name(s):
    if s in SUB: return SUB[s]
    return ' '.join(w if w in ('and', 'of', 'the') else w[:1].upper() + w[1:] for w in s.split('-'))
DAYS = [(date(2024, 1, 1) + timedelta(i)).strftime('%m-%d') for i in range(366)]
out = []
for k, v in a.items():
    dec = {}
    for y, n in v['years'].items():
        d = max(int(y) // 10 * 10, 1890)  # 1890 = everything before 1900
        if d <= 2020: dec[d] = dec.get(d, 0) + n
    mk = {w: {} for w in ('parliament', 'executive')}
    for w in mk:
        for y, n in v['maker_years'].get(w, {}).items():
            d = max(int(y) // 10 * 10, 1890)
            if d <= 2020: mk[w][d] = mk[w].get(d, 0) + n
    out.append({
        'id': k, 'name': name(k), 'acts': v['acts'],
        'wd': v['weekday'], 'awd': v['adopt_weekday'], 'mon': v['month'], 'amon': v['adopt_month'],
        'dom': v['dom'], 'doy': [v['doy'].get(d, 0) for d in DAYS], 'lag': v['lag'], 'lagh': v['lag_hist'],
        'dec': [dec.get(d, 0) for d in range(1890, 2030, 10)],
        'par': [mk['parliament'].get(d, 0) for d in range(1890, 2030, 10)],
        'exe': [mk['executive'].get(d, 0) for d in range(1890, 2030, 10)],
        'lagdec': [(lambda x: [x['median'], x['n']] if x and x['median'] >= 0 else None)(v['lag_by_decade'].get(str(d))) for d in range(1890, 2030, 10)],
    })
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8', newline='\n'), separators=(',', ':'), ensure_ascii=False)
print(len(out))
