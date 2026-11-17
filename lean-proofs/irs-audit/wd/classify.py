"""Classify the sampled written determinations (PLR / TAM / CCA) and count those stating a statutory dollar amount,
rate or threshold that could be checked against the Code."""
import os, json, subprocess, re, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); P = json.load(open(H + '/wd/probe.json'))
out = {}; kinds = collections.Counter(); per_week = {}
for wk, nums in P.items():
    per_week[wk] = len(nums)
    for n in nums:
        f = H + '/cache/www.irs.gov/pub/irs-wd/%s.pdf' % n
        t = subprocess.run(['pdftotext', '-l', '3', f, '-'], capture_output=True, text=True).stdout
        head = t[:3000]
        if re.search(r'Technical Advice Memorandum|TECHNICAL ADVICE MEMORANDUM', head): k = 'TAM'
        elif re.search(r'Office of Chief Counsel|CHIEF COUNSEL', head) and re.search(r'MEMORANDUM|Memorandum', head) and not re.search(r'Dear ', head): k = 'CCA'
        elif re.search(r'Dear |This letter responds|This is in reply', t): k = 'PLR'
        else: k = 'other' if t.strip() else 'scanned'
        kinds[k] += 1
        claims = len(re.findall(r'section \d+[A-Za-z]?\([a-z0-9]+\)[^.]{0,120}?\$[\d,]{3,}', t))
        out[n] = dict(kind=k, statutory_amount_mentions=claims)
weeks = len(P); total = sum(per_week.values())
res = dict(weeks=per_week, kinds=dict(kinds), docs=total, mean_per_week=total / max(weeks, 1),
           est_per_year={y: round(52 * sum(v for k, v in per_week.items() if k.startswith(str(y))) / 4) for y in (2000, 2010, 2020, 2025)},
           with_amount_mentions=sum(1 for v in out.values() if v['statutory_amount_mentions']), docs_detail=out)
json.dump(res, open(H + '/wd/classified.json', 'w'), indent=1)
print({k: v for k, v in res.items() if k != 'docs_detail'})
