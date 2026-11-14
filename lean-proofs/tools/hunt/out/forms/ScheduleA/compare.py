"""Statute vs form, written separately from each text, compared over grids.
Run: python -I compare.py   (prints differences, writes grid.json)"""
import itertools, json, sys
from fractions import Fraction as F
sys.stdout.reconfigure(encoding='utf-8')
N = 0
diffs = {}
def note(key, inp, s, f):
    d = diffs.setdefault(key, {'n': 0, 'max': 0, 'ex': None})
    d['n'] += 1
    gap = abs(float(f) - float(s))
    if gap > d['max'] or d['ex'] is None:
        d['max'] = gap; d['ex'] = {'input': inp, 'statute': round(float(s), 2), 'form': round(float(f), 2)}

# ---------- 1. SALT, 164(b)(6)-(7) vs Schedule A line 5e worksheet (2025 and 2026 draft face)
SALT = {2025: (40000, 500000), 2026: (40400, 505000)}
def salt_statute(year, salt, agi, excl911_gross, married_separate_return):
    lim, thr = SALT[year]
    magi = agi + excl911_gross                    # (7)(B)(iv): AGI + amount excluded under 911/931/933
    t = F(thr, 2) if married_separate_return else thr       # (7)(B)(i) half the threshold
    ala = max(lim - F(3, 10) * max(0, magi - t), 10000)     # (7)(B)(i),(iii)
    cap = ala / 2 if married_separate_return else ala       # (6)(B) half the applicable limitation amount
    return min(salt, cap)
def salt_form(year, salt, agi, l45, l50, status):
    lim, thr = SALT[year]
    mfs = status == 'MFS'
    if salt <= (5000 if mfs else 10000): return salt        # worksheet line 1
    l4 = agi + l45 + l50                                    # lines 2-4
    l5 = thr // 2 if mfs else thr
    l9 = lim if l4 <= l5 else max(lim - F(3, 10) * (l4 - l5), 10000)
    return min(l9 / 2 if mfs else l9, salt)
for year, salt, agi, l43, l44, l50, status in itertools.product(
        (2025, 2026), (4000, 8000, 15000, 25000, 45000, 80000), range(100000, 700001, 25000),
        (0, 130000), (0, 20000), (0, 15000), ('S', 'MFJ', 'MFS', 'HOH', 'HOH_married_apart')):
    if l43 == 0 and (l44 or l50): continue
    N += 1
    sep = status in ('MFS', 'HOH_married_apart')   # 164(b)(6) has no reference to 7703; literal reading
    s = salt_statute(year, salt, agi, l43, sep)
    f = salt_form(year, salt, agi, l43 - l44, l50, status)
    if s != f:
        key = ('SALT:married living apart filing as head of household' if status == 'HOH_married_apart' and l43 == 0
               else 'SALT:MAGI uses Form 2555 line 45 + line 50' if status != 'HOH_married_apart' else None)
        if key: note(key + (' (form more)' if f > s else ' (statute more)'),
                     dict(year=year, salt=salt, agi=agi, excl=l43, l44=l44, l50=l50, status=status), s, f)

# ---------- 2. Section 68 (2026): statute 2/37; IRS worksheets (Pub. 505 Wks 2-6, Form 8960 worksheet) 5.4%
B37 = {'S': 640600, 'HOH': 640600, 'MFJ': 768700, 'MFS': 384350}
def s68_statute(item, agi, sch1a, qbi, status):
    ti_plus = agi - sch1a - qbi                    # TI without 68, increased by itemized deductions
    return F(2, 37) * min(item, max(0, ti_plus - B37[status]))
def s68_form(item, agi, sch1a, qbi, status):
    l8 = agi - (qbi + sch1a)
    if l8 <= B37[status]: return 0
    return F(54, 1000) * min(item, l8 - B37[status])
for item, agi, sch1a, qbi, status in itertools.product(
        (20000, 60000, 155000, 400000, 1000000), range(300000, 3000001, 100000), (0, 12000), (0, 50000), B37):
    N += 1
    s, f = s68_statute(item, agi, sch1a, qbi, status), s68_form(item, agi, sch1a, qbi, status)
    if abs(s - f) >= 1: note('S68: 5.4% instead of 2/37 (form reduces less)', dict(item=item, agi=agi, status=status), -s, -f)

# ---------- 3. Charitable floor (2026), cash gifts to public charities only: 170(b)(1)(G),(I), (d)(1)
def char_statute(agi, cur, carry):
    lim = F(6, 10) * agi
    otherwise = min(cur + carry, lim)              # carryover is "treated as ... paid in" the year
    return max(0, otherwise - F(5, 1000) * agi)    # (I): the aggregate otherwise allowable, less 0.5%
def char_form(agi, cur, carry):
    # draft Schedule A (2026) face: line 13 = line 6 of a 6-line worksheet on lines 11-12 (as Pub. 505 Wks 2-5:
    # gifts minus 0.5% of AGI); line 14 carryover added afterwards; 60% limit applied as before
    lim = F(6, 10) * agi
    l13 = min(max(0, cur - F(5, 1000) * agi), lim)
    l14 = min(carry, lim - l13)
    return l13 + l14
for agi, cur, carry in itertools.product(range(50000, 2000001, 50000),
                                         (0, 100, 1000, 5000, 20000, 100000, 700000, 1500000), (0, 500, 5000, 50000, 400000)):
    N += 1
    s, f = char_statute(agi, cur, carry), char_form(agi, cur, carry)
    if s != f:
        k = ('CHAR: gifts over the 60% limit, floor taken off gross gifts' if cur > F(6, 10) * agi
             else 'CHAR: carryover added after the floor (current gifts below 0.5% of AGI)' if cur < F(5, 1000) * agi
             else 'CHAR: other')
        note(k + (' (form more)' if f > s else ' (statute more)'), dict(agi=agi, cur=cur, carry=carry), s, f)

# ---------- 4. AMT exemption 2026: 55(d) vs Form 6251 line 4-5 and Exemption Worksheet
def amt_statute(amti, status, flush_rate=F(1, 2)):
    ex = {'S': 90100, 'HOH': 90100, 'MFJ': 140200, 'MFS': 70100}[status]     # (d)(1),(4)(A)(i) indexed
    thr = 1000000 if status == 'MFJ' else 500000                            # (d)(2)(A)-(C) as substituted
    if status == 'MFS':
        zero_at = thr + 2 * ex
        amti = amti + min(flush_rate * max(0, amti - zero_at), ex)          # flush sentence of (d)(2)
    e = max(0, ex - F(1, 2) * max(0, amti - thr))
    return amti - e                                                        # taxable excess
def amt_form(amti, status):
    ex = {'S': 90100, 'HOH': 90100, 'MFJ': 140200, 'MFS': 70100}[status]
    thr = {'S': 500000, 'HOH': 500000, 'MFJ': 1000000, 'MFS': 500000}[status]
    if status == 'MFS' and amti > 640200:
        amti = amti + (70100 if amti >= 780400 else F(1, 2) * (amti - 640200))
    zero = {'S': 680200, 'HOH': 680200, 'MFJ': 1280400, 'MFS': 640200}[status]
    if amti >= zero: return amti
    l6 = max(0, ex - F(1, 2) * max(0, amti - thr))
    return amti - l6
for amti, status in itertools.product(range(100000, 1500001, 5000), ('S', 'HOH', 'MFJ', 'MFS')):
    N += 1
    s, f = amt_statute(amti, status), amt_form(amti, status)
    if s != f: note('AMT: exemption phase-out', dict(amti=amti, status=status), s, f)
    s2 = amt_statute(amti, status, F(1, 4))
    if s2 != f: note('AMT: married-separate add-back if "25 percent" in the flush sentence is not substituted (alternative reading only)',
                     dict(amti=amti, status=status), s2, f)

# ---------- 5. AMTI and section 68 (2026): 56(b)(1)(E) vs Form 6251 lines 1a-2a
def amti_statute(agi, item_before68, taxes, red68, qbi):
    return agi - (item_before68 - taxes) - qbi        # 68 does not apply; taxes not allowed
def amti_form(agi, item_before68, taxes, red68, qbi):
    l14 = (item_before68 - red68) + qbi               # Form 1040 line 12e is Schedule A line 18, after 68
    l1b = agi - l14
    return l1b + taxes                                # line 2a adds Schedule A line 7; no line removes the 68 reduction
for item, agi, status in itertools.product((40000, 100000, 300000, 1000000), range(500000, 3000001, 100000), B37):
    N += 1
    taxes = min(10000, item)
    r = s68_statute(item, agi, 0, 0, status)
    s, f = amti_statute(agi, item, taxes, r, 0), amti_form(agi, item, taxes, r, 0)
    if s != f: note('AMT: section 68 reduction left in AMTI (statute lower AMTI)', dict(item=item, agi=agi, status=status), s, f)

# ---------- 6. Section 1411 vs Form 8960 lines 12-17
def niit_statute(nii, magi, status, apart_7703b=False):
    thr = 250000 if status in ('MFJ', 'QSS') else 125000 if status == 'MFS' else 200000
    return F(38, 1000) * min(max(nii, 0), max(0, magi - thr))
def niit_form(nii, magi, status):
    l14 = {'MFJ': 250000, 'QSS': 250000, 'MFS': 125000, 'S': 200000, 'HOH': 200000}[status]
    return F(38, 1000) * min(max(0, nii), max(0, magi - l14))
for nii, magi, status in itertools.product(range(-20000, 400001, 20000), range(100000, 600001, 12500), ('S', 'HOH', 'MFJ', 'MFS', 'QSS')):
    N += 1
    if niit_statute(nii, magi, status) != niit_form(nii, magi, status): note('NIIT', dict(nii=nii, magi=magi, status=status), niit_statute(nii, magi, status), niit_form(nii, magi, status))

# ---------- 7. 3101(b)(2), 1401(b)(2), 3201(a) vs Form 8959
def amt_medicare_statute(w, se, rrta, status):
    thr = 250000 if status == 'MFJ' else 125000 if status == 'MFS' else 200000
    t = F(9, 1000) * max(0, w - thr)
    t += F(9, 1000) * max(0, se - max(0, thr - w))      # 1401(b)(2)(B)
    t += F(9, 1000) * max(0, rrta - thr)                # 3201(a), own threshold (Reg. 31.3202-1(g))
    return t
def amt_medicare_form(w, se, rrta, status):
    thr = {'MFJ': 250000, 'MFS': 125000}.get(status, 200000)
    l7 = F(9, 1000) * max(0, w - thr)
    l11 = max(0, thr - w); l13 = F(9, 1000) * max(0, max(se, 0) - l11)
    l17 = F(9, 1000) * max(0, rrta - thr)
    return l7 + l13 + l17
for w, se, rrta, status in itertools.product(range(0, 400001, 25000), range(0, 400001, 25000), (0, 150000, 300000), ('S', 'HOH', 'QSS', 'MFJ', 'MFS')):
    N += 1
    if amt_medicare_statute(w, se, rrta, status) != amt_medicare_form(w, se, rrta, status): note('8959', dict(w=w, se=se, rrta=rrta, status=status), amt_medicare_statute(w, se, rrta, status), amt_medicare_form(w, se, rrta, status))

# ---------- 8. 199A (2026) vs Form 8995 / 8995-A (one trade or business, no SSTB)
TH = {'S': 201750, 'MFS': 201775, 'MFJ': 403500}
def qbi_statute(qbi_active, qbi_passive, w2, ubia, ti, ncg, dpad, status):
    qbi = qbi_active + qbi_passive
    th, rng = TH[status], (150000 if status == 'MFJ' else 75000)
    a = F(1, 5) * max(qbi, 0)
    b = max(F(1, 2) * w2, F(1, 4) * w2 + F(25, 1000) * ubia)
    if ti <= th: comp = a
    elif ti <= th + rng: comp = a - (a - b) * F(ti - th, rng) if b < a else a
    else: comp = min(a, b)
    ded = min(comp, F(1, 5) * max(0, ti - ncg))                    # (a)
    if qbi_active >= 1000: ded = max(ded, 400)                     # (i): floors the subsection (a) deduction only
    g = min(dpad, max(0, ti - ded))                                # (g)(2)(A),(B): a separate deduction
    return ded + g
def qbi_form(qbi_active, qbi_passive, w2, ubia, ti, ncg, dpad, status):
    th, rng = TH[status], (150000 if status == 'MFJ' else 75000)
    minimum = 400 if qbi_active >= 1000 else 0                     # line 16 / line 40
    if ti <= th and dpad == 0:                                     # Form 8995
        l5 = F(1, 5) * max(0, qbi_active + qbi_passive)
        l15 = min(l5, F(1, 5) * max(0, ti - ncg))
        return max(l15, minimum)
    l3 = F(1, 5) * max(0, qbi_active + qbi_passive)                # Form 8995-A
    if ti <= th: l13 = l3
    else:
        l10 = max(F(1, 2) * w2, F(1, 4) * w2 + F(25, 1000) * ubia)
        l11 = min(l3, l10); l12 = 0
        if ti <= th + rng and l10 < l3: l12 = l3 - (l3 - l10) * F(ti - th, rng)
        l13 = max(l11, l12)
    l37 = min(l13, F(1, 5) * max(0, ti - ncg))
    l38 = min(dpad, max(0, ti - l37))
    return max(l37 + l38, minimum)                                 # lines 39-41
for qa, qp, w2, ubia, ti, ncg, dpad, status in itertools.product(
        (0, 900, 1000, 1500, 5000, 100000, 400000), (-5000, 0, 3000), (0, 30000), (0, 200000),
        (0, 300, 1500, 60000, 201750, 240000, 300000, 420000, 600000), (0, 1000, 60000), (0, 250, 2000), TH):
    N += 1
    s, f = qbi_statute(qa, qp, w2, ubia, ti, ncg, dpad, status), qbi_form(qa, qp, w2, ubia, ti, ncg, dpad, status)
    if s != f: note('199A: minimum deduction compared after adding the co-op (g) deduction' + (' (statute more)' if s > f else ' (form more)'),
                    dict(qbi_active=qa, qbi_passive=qp, w2=w2, ubia=ubia, ti=ti, ncg=ncg, dpad=dpad, status=status), s, f)

print('grid points', N)
for k, d in diffs.items(): print(f"{k}\n   cases {d['n']}  largest gap ${d['max']:,.2f}  e.g. {d['ex']}")
json.dump({'grid_points': N, 'diffs': diffs}, open(__file__.replace('compare.py', 'grid.json'), 'w'), indent=1)
