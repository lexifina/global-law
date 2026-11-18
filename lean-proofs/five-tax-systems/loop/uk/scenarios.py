"""Recreate the catalogued UK techniques (CATALOGUE.md ids) with the extended Lean model. Each scenario: the household
without and with the technique, the tax burden (ukrun.burden: income tax less relief at source + CGT + employee NI
- child benefit net of HICBC) and the saving. Economic differences (pension credits, employer NI, outlays) are in
`value_*` where they matter. Output: runs/scenarios.json and a markdown table on stdout."""
import os
import json, sys
sys.path.insert(0, os.path.expanduser('~/cmp/loop/uk'))
from ukrun import hh, run, burden, parts

P = lambda **k: k
S = []
def add(i, title, h0, h1, note=''):
    S.append((i, title, h0, h1, note))

add('C01', 'Salary sacrifice of £25,140 into pension at £125,140 (allowance taper)',
    hh([P(employment=125140)], False), hh([P(employment=100000)], False),
    'with: employer pays the £25,140 into the pension (ITEPA s. 308); no Class 1 on it')
add('C02', 'Relief-at-source contribution £25,140 gross at £125,140',
    hh([P(employment=125140)], False), hh([P(employment=125140, rasGross=25140)], False),
    'member pays £20,112; burden counts the £5,028 added at source as a reduction')
add('C03', 'Salary sacrifice of £20,000 to escape the HICBC (2 children, £80,000)',
    hh([P(employment=80000)], False, 2), hh([P(employment=60000)], False, 2))
add('C04', 'RAS contribution £2,000 restores the £1,000 PSA (wages £52,000, interest £1,000)',
    hh([P(employment=52000, interest=1000)], False), hh([P(employment=52000, interest=1000, rasGross=2000)], False))
add('C05a', 'RAS contribution £10,000 and CGT for a basic-rate taxpayer (wages £40,000, gains £30,000)',
    hh([P(employment=40000, gains=30000)], False), hh([P(employment=40000, gains=30000, rasGross=10000)], False),
    's. 192(4): no higher rate chargeable apart from s. 192, so no band extension (UK FINDINGS F2b)')
add('C05b', 'Gift Aid £8,000 paid (£10,000 gross) and CGT, same person',
    hh([P(employment=40000, gains=30000)], False), hh([P(employment=40000, gains=30000, giftAid=8000)], False),
    's. 414(2)(b) extends the band unconditionally; TCGA s. 1J reads the unused band')
add('C06', 'Net pay vs relief at source: earner on £11,000 contributing £1,000 gross',
    hh([P(employment=11000, bik=-1000)], False), hh([P(employment=11000, rasGross=1000)], False),
    'without = net pay (deducted from pay, nothing to relieve below the PA); with = RAS (£200 added)')
add('C07', 'Non-earner pays £2,880 into a pension, credited £3,600 (FA 2004 s. 190(2)-(3))',
    hh([P()], False), hh([P(rasGross=3600)], False))
add('C08', 'Gift Aid £8,000 by a higher-rate donor (wages £70,000)',
    hh([P(employment=70000)], False), hh([P(employment=70000, giftAid=8000)], False))
add('C09a', 'Gift Aid £8,000 in the allowance taper (wages £110,000)',
    hh([P(employment=110000)], False), hh([P(employment=110000, giftAid=8000)], False))
add('C09b', 'Gift Aid £8,000 in the HICBC band (wages £70,000, 3 children)',
    hh([P(employment=70000)], False, 3), hh([P(employment=70000, giftAid=8000)], False, 3))
add('C11', 'Marriage allowance (A no income, B £40,000)',
    hh([P(), P(employment=40000)], married=False), hh([P(), P(employment=40000)], married=True))
add('C12', 'Move £6k interest + £6k dividends from the earner (A £90,000) to the non-earning spouse',
    hh([P(employment=90000, interest=6000, dividends=6000), P()]),
    hh([P(employment=90000), P(interest=6000, dividends=6000)]))
add('C13', 'Bed-and-spouse: half of £20,000 gains transferred (A £90,000, B £10,000)',
    hh([P(employment=90000, gains=20000), P(employment=10000)]),
    hh([P(employment=90000, gains=10000), P(employment=10000, gains=10000)]))
add('C14', 'Starting rate for savings: £18,570 of interest vs the same as wages',
    hh([P(employment=18570)], False), hh([P(interest=18570)], False))
add('C16', 'Dividend allowance: £13,070 of dividends vs the same as wages',
    hh([P(employment=13070)], False), hh([P(dividends=13070)], False))
add('C19', 'ISA: £20,000 at 4 % (£800) sheltered, higher-rate saver with £1,000 other interest',
    hh([P(employment=60000, interest=1800)], False), hh([P(employment=60000, interest=1000)], False))
add('C21', 'CGT exempt amount harvested: £3,000 of gain realised this year (bed-and-ISA / -breakfast)',
    hh([P(employment=60000, gains=3000)], False), hh([P(employment=60000, gains=3000)], False),
    'nil tax now; the same £3,000 realised later on top of other gains costs 24 %: £720 (see extra)')
add('C22', 'Timing: £40,000 of gains realised in a £60,000 year vs a year with no other income',
    hh([P(employment=60000, gains=40000)], False), hh([P(gains=40000)], False),
    'saving net of the income itself: compare CGT only (see extra)')
add('C23', 'EIS £50,000 (30 %), wages £150,000',
    hh([P(employment=150000)], False), hh([P(employment=150000, eis=50000)], False))
add('C24', 'SEIS £50,000 (50 %), wages £150,000',
    hh([P(employment=150000)], False), hh([P(employment=150000, seis=50000)], False))
add('C25', 'VCT £50,000 (30 %), wages £150,000',
    hh([P(employment=150000)], False), hh([P(employment=150000, vct=50000)], False))
add('C26', 'Rent-a-room: £9,000 rent, £1,500 costs (alternative basis £1,500), wages £40,000',
    hh([P(employment=40000, property=7500)], False), hh([P(employment=40000, property=1500)], False))
add('C27a', 'Trading allowance: £3,000 receipts, £200 costs (partial relief), employee on £30,000',
    hh([P(employment=30000, trading=2800)], False), hh([P(employment=30000, trading=2000)], False))
add('C27b', 'Trading allowance: £900 receipts (full relief)',
    hh([P(employment=30000, trading=900)], False), hh([P(employment=30000)], False))
add('C28', 'Property allowance: £2,500 receipts, £100 costs, wages £60,000',
    hh([P(employment=60000, property=2400)], False), hh([P(employment=60000, property=1500)], False))
add('C29', 'Scottish taxpayer (without) vs rest of the UK (with), wages £50,000',
    hh([P(employment=50000)], False, region='scotland'), hh([P(employment=50000)], False))
add('C30', 'Class 4 annual maximum: employee £60,000 with profits £30,000 (with = reg. 100 cap)',
    hh([P(employment=60000, trading=30000)], False), hh([P(employment=60000, trading=30000)], False),
    'without row is replaced by the uncapped figure in extra')
add('C32', 'EV salary sacrifice: £7,000 of £60,000 pay for a £50,000 car (3 % BIK = £1,500)',
    hh([P(employment=60000)], False), hh([P(employment=53000, bik=1500)], False))
add('C33', 'Exempt benefit via sacrifice (cycle to work £1,000), wages £45,000',
    hh([P(employment=45000)], False), hh([P(employment=44000)], False))
add('C34', 'Buy-to-let, £40,000 profit before £20,000 mortgage interest: held by A (£50,000) vs by non-earning B',
    hh([P(employment=50000, property=40000, financeCosts=20000), P()]),
    hh([P(employment=50000), P(property=40000, financeCosts=20000)]))
add('C35', 'Same buy-to-let held jointly 50:50 (s. 836) vs by A',
    hh([P(employment=50000, property=40000, financeCosts=20000), P()]),
    hh([P(employment=50000, property=20000, financeCosts=10000), P(property=20000, financeCosts=10000)]))
add('C36', 'Pension drawdown: £100,000 in one year (£75,000 taxable) vs one year of £16,760 (£12,570 taxable)',
    hh([P(pension=75000)], False), hh([P(pension=12570)], False), 'phased total in extra')
add('C37', 'Gift to a grandchild: £2,000 interest held by a higher-rate grandparent vs the child',
    hh([P(employment=60000, interest=2000)], False), hh([P(employment=60000)], False), 'child tax in extra')
add('C38', 'Employ the spouse: sole trader £70,000 pays spouse £12,570 (employer NI £1,135.50 deducted)',
    hh([P(trading=70000), P()]), hh([P(trading=70000 - 12570 - 1136), P(employment=12570)]),
    'with: profits reduced by the wage and the employer NI (15 % above £5,000), both deductible')
add('C40', 'Gift Aid keeps a £52,000 recipient basic-rate: marriage allowance (A none, B pays £1,600 Gift Aid)',
    hh([P(), P(employment=52000, giftAid=1600)], married=False), hh([P(), P(employment=52000, giftAid=1600)], married=True))
add('C41', "Blind spouse's unused blind person's allowance transferred (s. 39), B £40,000",
    hh([P(), P(employment=40000)]), hh([P(blind=True), P(employment=40000)]))
add('C42', 'Owner-manager: see owner_manager.py', hh([P()], False), hh([P()], False), 'computed separately')

outs = run([x for s in S for x in (s[2], s[3])])
res = {}
for k, s in enumerate(S):
    o0, o1 = outs[2 * k], outs[2 * k + 1]
    b0, b1 = burden(o0), burden(o1)
    res[s[0]] = dict(id=s[0], title=s[1], burden_without=b0, burden_with=b1, saving=round(b0 - b1, 2),
                     without=parts(o0), with_=parts(o1), note=s[4])
extra = {}
# value of the salary-sacrifice / RAS routes (take-home + pension), same employer cost
extra['C01_value_without'] = round(125140 - res['C01']['burden_without'], 2)
extra['C01_value_with'] = round(100000 + 25140 - res['C01']['burden_with'], 2)
extra['C02_value_with'] = round(125140 - 0.8 * 25140 + 25140 - res['C02']['burden_with'] - 25140 * 0.2, 2)  # RAS credit already in burden
extra['C30_uncapped_class4'] = round(0.06 * (30000 - 12570), 2)
extra['C30_capped_class4'] = round(res['C30']['with_']['ni'] - res['C30']['with_']['ni'] + 0, 2)
yrs = 100000 / 16760
extra['C36_phased_total_tax'] = round(res['C36']['burden_with'] * yrs, 2)
extra['C37_child_tax'] = burden(run([hh([P(age=8, interest=2000)], False)])[0])
g = run([hh([P(employment=60000, gains=6000)], False), hh([P(employment=60000, gains=3000)], False)])
extra['C21_later_cost_of_unharvested_3000'] = round(g[0]['surtaxes'].get('capitalGainsTax', 0) - g[1]['surtaxes'].get('capitalGainsTax', 0), 2)
extra['C22_cgt_without'] = res['C22']['without']['cgt']; extra['C22_cgt_with'] = res['C22']['with_']['cgt']
c = run([hh([P(employment=60000, trading=30000)], False)])[0]['detail']['persons'][0]
extra['C30_model_class1_class4'] = [c['class1'], c['class4']]
json.dump(dict(scenarios=list(res.values()), extra=extra), open(os.path.expanduser('~/cmp/loop/uk/runs/scenarios.json'), 'w'), indent=1)
print('| id | scenario | burden without | with | saving |'); print('|---|---|---|---|---|')
for r in res.values():
    print(f"| {r['id']} | {r['title']} | {r['burden_without']:,.2f} | {r['burden_with']:,.2f} | {r['saving']:,.2f} |")
print(json.dumps(extra))
for i in ('C11', 'C40', 'C34', 'C35', 'C38', 'C41', 'C05a', 'C05b', 'C06', 'C07'):
    print(i, res[i]['without'], res[i]['with_'])
