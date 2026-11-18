"""C42/C43: owner-manager extraction, salary vs dividends (personal side by the Lean model; company side here).
Company side, financial year 2025: corporation tax 19 % up to £50,000, 25 % from £250,000, marginal relief between
(CTA 2010 s. 18A-18E, standard fraction 3/200); secondary Class 1 15 % above the secondary threshold £5,000
(SSCBA 1992 s. 9 as amended by NICA 2025); no Employment Allowance (sole-director company). All profit after
corporation tax is paid out as a dividend. Output: runs/owner_manager.json and a table."""
import os
import json, sys
sys.path.insert(0, os.path.expanduser('~/cmp/loop/uk'))
from ukrun import hh, run, burden

def ct(p):
    if p <= 0: return 0.0
    if p <= 50000: return 0.19 * p
    if p >= 250000: return 0.25 * p
    return 0.25 * p - 3 / 200 * (250000 - p)

def plan(profit, salary, spouse_share=0.0):
    ernic = 0.15 * max(0, salary - 5000)
    taxable = profit - salary - ernic
    div = int(max(0, taxable - ct(taxable)))
    d2 = int(div * spouse_share)
    persons = [dict(employment=salary, dividends=div - d2)] + ([dict(dividends=d2)] if spouse_share else [])
    return hh(persons, married=bool(spouse_share)), salary + div, ernic, ct(taxable)

rows = []
for profit in (30000, 50000, 100000, 150000):
    all_salary = int((profit + 750) / 1.15) if profit > 5000 else profit
    cands = [('all salary', all_salary, 0.0), ('salary £12,570 + dividends', 12570, 0.0),
             ('salary £5,000 + dividends', 5000, 0.0), ('salary £12,570 + dividends 50:50 with non-earning spouse', 12570, 0.5)]
    hs = [plan(profit, s, sh) for (_, s, sh) in cands]
    outs = run([h[0] for h in hs])
    for (name, s, sh), (h, gross, ernic, cort), o in zip(cands, hs, outs):
        b = burden(o)
        rows.append(dict(profit=profit, plan=name, salary=s, employer_ni=round(ernic, 2), corporation_tax=round(cort, 2),
                         personal_tax_ni=b, net=round(gross - b, 2), total_tax=round(ernic + cort + b, 2)))
json.dump(rows, open(os.path.expanduser('~/cmp/loop/uk/runs/owner_manager.json'), 'w'), indent=1)
print('| profit | plan | employer NI | CT | personal IT+NI | net to household | total tax |'); print('|---|---|---|---|---|---|---|')
for r in rows:
    print(f"| {r['profit']:,} | {r['plan']} | {r['employer_ni']:,.2f} | {r['corporation_tax']:,.2f} | {r['personal_tax_ni']:,.2f} | {r['net']:,.2f} | {r['total_tax']:,.2f} |")
