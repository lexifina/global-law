# T7: independent arithmetic, written from the statute text (26 U.S.C. 1(j), 63, 68, 164(b)(6)-(7), 170(b)(1)(I), 55-56),
# not from the Lean. Exact fractions, rounded down to dollars only at the tax.
from fractions import Fraction as F
import json

JOINT = [(24800, 10), (100800, 12), (211400, 22), (403550, 24), (512450, 32), (768700, 35)]   # Rev. Proc. 2025-32, 2026
SEP   = [(12400, 10), (50400, 12), (105700, 22), (201775, 24), (256225, 32), (384350, 35)]
STD = {'joint': 32200, 'sep': 16100}
ALA, THR, FLOOR = 40400, 505000, 10000            # 164(b)(7)(A)(ii), (B)(ii)(II), (B)(iii)

def tax(ti, table):
    t, lo = F(0), 0
    for hi, r in table:
        if ti > lo: t += (min(ti, hi) - lo) * F(r, 100)
        lo = hi
    if ti > lo: t += (ti - lo) * F(37, 100)
    return t

def salt_limit(status, magi, reading):
    if status == 'joint':
        return max(FLOOR, ALA - F(30, 100) * max(0, magi - THR))
    excess = max(0, magi - F(THR, 2))             # "(half the threshold amount in the case of a married individual filing a separate return)"
    if reading == 'literal':                      # (7)(B)(i) reduces the ALA, (iii) floors the ALA at $10,000, (6)(B) allows half the ALA
        return max(FLOOR, ALA - F(30, 100) * excess) / 2
    if reading == 'irs':                          # worksheet: $20,200 less 30% of the excess, not below $5,000
        return max(F(FLOOR, 2), F(ALA, 2) - F(30, 100) * excess)
    if reading == 'halve_first_floor_10000':      # third reading: reduce the halved amount, clause (iii) floor as written
        return max(FLOOR, F(ALA, 2) - F(30, 100) * excess)

def ret(status, agi, salt, mortgage, gifts, reading, itemize=True):
    table = JOINT if status == 'joint' else SEP
    if itemize:
        s = min(salt, salt_limit(status, agi, reading))
        g = max(0, min(gifts, F(60, 100) * agi) - F(5, 1000) * agi)          # 170(b)(1)(G), (I)
        item = s + mortgage + g
        start37 = table[-1][0]
        cut = F(2, 37) * max(0, min(item, agi - item + item - start37))      # 68(a)
        ti = agi - item + cut
    else:
        s = 0
        ti = agi - STD[status] - min(gifts, 2000 if status == 'joint' else 1000)   # 63(c), 170(p)
    t = tax(ti, table)
    # 55(b), (d) for 2026 (Rev. Proc. 2025-32): exemption $140,200 joint / $70,100 separate, phase-out from $1,000,000 / $500,000,
    # 28% above $244,500 / $122,250 of the excess; 56(b)(1)(A)(ii): no deduction for taxes
    ex, brk = (140200, 244500) if status == 'joint' else (70100, 122250)
    amti = ti + (s if itemize else STD[status])
    base = max(0, amti - ex)
    tmt = F(26, 100) * min(base, brk) + F(28, 100) * max(0, base - brk)
    return dict(salt=float(s), taxable=float(ti), tax=int(t), amt_excess=float(max(0, tmt - t)), tmt=int(tmt))

W, ST, PROP, INST, MORT, GIFT = 300000, 19000, 16000, 6000, 18000, 8000
out = {}
j_item = ret('joint', 2 * W, 2 * ST + PROP + INST, MORT, GIFT, 'irs')
j_std = ret('joint', 2 * W, 0, 0, GIFT, 'irs', itemize=False)
base_year = min(j_item['tax'], j_std['tax'])
out['baseline_two_years'] = 2 * base_year
out['joint_itemized'] = j_item
for reading in ('literal', 'irs', 'halve_first_floor_10000'):
    a = ret('sep', W, ST + PROP + INST, MORT, GIFT, reading)      # A pays the household items (the model's allocation)
    b = ret('sep', W, ST, 0, 0, reading)
    a2 = ret('sep', W, ST + (PROP + INST) / 2, MORT / 2, GIFT / 2, reading)   # strict: joint funds, each spouse half
    out[reading] = dict(A=a, B=b, two_years=2 * (a['tax'] + b['tax']), gain=2 * base_year - 2 * (a['tax'] + b['tax']),
                        gain_if_payments_split_equally=2 * base_year - 4 * a2['tax'],
                        amt_excess=a['amt_excess'] + b['amt_excess'])
print(json.dumps(out, indent=1))
# sweep: where the literal reading pays, equal earners, SALT above every cap
print('MAGI each | joint cap | literal each | IRS each | third each')
for m in (252500, 280000, 300000, 303167, 325000, 353834, 400000):
    print(m, float(salt_limit('joint', 2 * m, '')), float(salt_limit('sep', m, 'literal')), float(salt_limit('sep', m, 'irs')),
          float(salt_limit('sep', m, 'halve_first_floor_10000')))
