"""Statutory recomputation of inflation-adjusted amounts, 1997-2027 (Rev. Procs), as Lean data + checker."""
import json, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
pub = json.load(open(H + '/indexing/published.json'))
# (key, value index, cite, base, base year, rounding, first TY, last TY)
SPEC = [
 ('pers_exempt', 0, '§151(d)(4) (base 1988), §1(f)(6)(A) increase down to $50', 2000, 1988, 'incDown 50', 1990, 2017),
 ('gift_excl', 0, '§2503(b)(2) (base 1997), amount down to $1,000', 10000, 1997, 'amtDown 1000', 1999, 2027),
 ('s2032A', 0, '§2032A(a)(3) (base 1997), amount down to $10,000', 750000, 1997, 'amtDown 10000', 1999, 2027),
 ('s6601j', 0, '§6601(j)(3) (base 1997), amount down to $10,000', 1000000, 1997, 'amtDown 10000', 1999, 2027),
 ('feie', 0, '§911(b)(2)(D)(ii) (base 2004), increase down to $100', 80000, 2004, 'incDown 100', 2006, 2027),
 ('inv_income', 0, '§32(i)(1), §32(j)(1)(B)(i), (j)(2)(B) ($2,200 base 1995), amount down to $50', 2200, 1995, 'amtDown 50', 1997, 2021),
 ('inv_income', 0, '§32(i)(1) ($10,000, Pub. L. 117-2), §32(j)(1)(B)(iii) (base 2020), amount down to $50', 10000, 2020, 'amtDown 50', 2022, 2027),
 ('aged_blind', 0, '§63(f)(1) $600 (base 1987), §63(c)(4), increase down to $50', 600, 1987, 'incDown 50', 1989, 2027),
 ('aged_blind', 1, '§63(f)(3) $750 (base 1987), §63(c)(4), increase down to $50', 750, 1987, 'incDown 50', 1989, 2027),
 ('dep_std', 0, '§63(c)(5)(A) $500 (base 1987), increase down to $50', 500, 1987, 'incDown 50', 1989, 2027),
 ('dep_std', 1, '§63(c)(5)(B) $250 (base 1997), increase down to $50', 250, 1997, 'incDown 50', 1998, 2027),
 ('trust_exempt', 0, '§642(b)(2)(C)(iii) $4,150 (base 2017), §6334(d)(4)(C) increase down to $100', 4150, 2017, 'incDown 100', 2018, 2027),
 ('levy_wage', 0, '§6334(d)(4)(B),(C) $4,150 (base 2017), increase down to $100', 4150, 2017, 'incDown 100', 2018, 2027),
 ('basic_excl', 0, '§2010(c)(3)(B) $5,000,000 (base 2010), amount to the nearest $10,000', 5000000, 2010, 'amtNear 10000', 2012, 2017),
 ('basic_excl', 0, '§2010(c)(3)(C) $10,000,000 (base 2010), amount to the nearest $10,000', 10000000, 2010, 'amtNear 10000', 2018, 2025),
 ('std_single', 0, '§63(c)(2)(C) $3,000 (base 1987), §1(f)(6)(A) increase down to $50', 3000, 1987, 'incDown 50', 1989, 2017),
 ('std_hoh', -1, '§63(c)(2)(B) $4,400 (base 1987), §1(f)(6)(A) increase down to $50', 4400, 1987, 'incDown 50', 1989, 2017),
 ('std_single', 0, '§63(c)(7)(A)(ii),(B) (Pub. L. 115-97) $12,000 (base 2017), increase down to $50', 12000, 2017, 'incDown 50', 2018, 2024),
 ('std_hoh', -1, '§63(c)(7)(A)(i),(B) (Pub. L. 115-97) $18,000 (base 2017), increase down to $50', 18000, 2017, 'incDown 50', 2018, 2024),
 ('std_single', 0, '§63(c)(7)(A)(ii),(B)(ii) (Pub. L. 119-21) $15,750 (base 2024), increase down to $50', 15750, 2024, 'incDown 50', 2026, 2027),
 ('std_hoh', -1, '§63(c)(7)(A)(i),(B)(ii) (Pub. L. 119-21) $23,625 (base 2024), increase down to $50', 23625, 2024, 'incDown 50', 2026, 2027),
]
VINT = {2018: 'ccpiu_a2017', 2019: 'ccpiu_a2018', 2020: 'ccpiu_a2019', 2021: 'ccpiu_a2020', 2022: 'ccpiu_a2021', 2023: 'ccpiu_v2022', 2024: 'ccpiu_v2023', 2025: 'ccpiu_v2024', 2026: 'ccpiu_v2025', 2027: 'ccpiu_v2026'}
items = []
for key, vi, cite, base, by, rnd, a, b in SPEC:
    for ty in range(max(a, 1997), b + 1):
        if str(ty) not in pub or key not in pub[str(ty)]: continue
        v = pub[str(ty)][key]['v'][vi]
        items.append((key + ('' if vi in (0, -1) else '_%d' % vi), ty, cite, base, by, rnd, v))

# §1(j)(2) rate-table thresholds, 2019-2027 (brackets.json, from each year's Rev. Proc.)
BR = {'mfj': [19050, 77400, 165000, 315000, 400000, 600000], 'hoh': [13600, 51800, 82500, 157500, 200000, 500000],
      'single': [9525, 38700, 82500, 157500, 200000, 500000], 'mfs': [9525, 38700, 82500, 157500, 200000, 300000], 'est': [2550, 9150, 12500]}
brj = json.load(open(H + '/indexing/brackets.json'))
for ty in range(2019, 2028):
    for st, tops in BR.items():
        pubs = brj[str(ty)]['br'].get(st, [])
        if len(pubs) != len(tops): continue
        m = 25 if st in ('single', 'mfs') else 50
        for k, b in enumerate(tops):
            by = 2017 if (ty <= 2025 or st == 'est' or k >= 2) else 2016
            cite = '§1(j)(2) (base %d), §1(j)(3)(B), increase down to $%d%s' % (by, m, ' (Pub. L. 119-21 text)' if ty >= 2026 else ' (Pub. L. 115-97 text)')
            items.append(('br_%s_%d' % (st, k + 1), ty, cite, b, by, 'incDown %d' % m, pubs[k]))

# §55 AMT amounts 2013-2024 (amt.json); §55(d)(4): amounts rounded to the nearest $100
amtj = json.load(open(H + '/indexing/amt.json'))
AMT = [('ex_mfj', 78750, 2011, 2013, 2017, '§55(d)(1)(A)'), ('ex_single', 50600, 2011, 2013, 2017, '§55(d)(1)(B)'),
       ('ex_est', 22500, 2011, 2013, 2024, '§55(d)(1)(D)'), ('bp', 175000, 2011, 2013, 2024, '§55(b)(1)(A)(i)'),
       ('po_mfj', 150000, 2011, 2013, 2017, '§55(d)(3)(A)'), ('po_single', 112500, 2011, 2013, 2017, '§55(d)(3)(B)'),
       ('ex_mfj', 109400, 2017, 2018, 2024, '§55(d)(4)(A)(i)(I)'), ('ex_single', 70300, 2017, 2018, 2024, '§55(d)(4)(A)(i)(II)'),
       ('po_mfj', 1000000, 2017, 2018, 2024, '§55(d)(4)(A)(ii)(I)')]
for k, base, by, a, b, cite in AMT:
    for ty in range(a, b + 1):
        v = amtj.get(str(ty), {}).get('v', {}).get(k)
        if k.startswith('ex_') and ty == 2015: continue   # Rev. Proc. 2015-53 text: the extractor reads the phase-out table here
        if v: items.append(('amt_' + k, ty, cite + ' (base %d), §55(d)(4) amount to the nearest $100' % by, base, by, 'amtNear 100', v))
for ty in range(2013, 2025):
    v = amtj.get(str(ty), {}).get('v', {}).get('po_est')
    if v and v < 200000:   # §55(d)(3)(C): 50% of the indexed $150,000 (estates keep it after 2017, §55(d)(4)(A)(ii)(III)); compared as 2 x published
        items.append(('amt_po_est_x2', ty, '§55(d)(3)(C) 50% of (A) $150,000 (base 2011), nearest $100', 150000, 2011, 'amtNear 100', 2 * v))
# derived: MFJ = 200% of single (2003+), MFS = single (2003+)
derived = []
for ty in range(2003, 2028):
    p = pub.get(str(ty), {})
    if 'std_mfj' in p and 'std_single' in p: derived.append(('std_mfj_200pct', ty, '§63(c)(2)(A)(i): 200% of (C)', p['std_mfj']['v'][0], 2 * p['std_single']['v'][0]))
lines = []
for (k, ty, cite, base, by, rnd, v) in items:
    era = 'cpiu' if ty <= 2017 else VINT[ty]
    lines.append('  ⟨"%s", %d, "%s", %d, %d, .%s, %d, "%s"⟩' % (k, ty, cite.replace('"', "'"), base, by, rnd, v, era))
lean = '''import Audit.Formula
import Audit.CPI
import Audit.Alfred
open TaxCode.Indexing

structure Item where
  key : String
  ty : Nat
  cite : String
  base : Nat
  by_ : Nat
  rnd : Rnd
  pub : Nat
  era : String

/-- CPI-U era (tax years through 2017): §1(f)(3) before Pub. L. 115-97, CPI(Y-1)/CPI(base), 12-month averages to Aug 31. -/
def ratioCPIU (cy b : Nat) : Nat × Nat := (ysum cpiu (cy - 1), ysum cpiu b)

/-- C-CPI-U era: §1(f)(3) as amended; vintage of the August (Y-1) release. 2027: October 2025 never published, so the
    twelve-month average cannot be formed; the eleven published months are averaged (the IRS's evident method). -/
def ratioC (C : Series) (cy b : Nat) : Nat × Nat :=
  if complete C (cy - 1) then ratio C cpiu [] [] (.year b) cy
  else
    let s11 := ysum C (cy - 1)
    if 2016 ≤ b then (s11 * 12, ysum C b * 11) else (s11 * 12 * ysum cpiu 2016, ysum cpiu b * ysum C 2016 * 11)

def vint (e : String) : Series :=
  if e == "ccpiu_a2017" then ccpiu_a2017 else if e == "ccpiu_a2018" then ccpiu_a2018 else if e == "ccpiu_a2019" then ccpiu_a2019
  else if e == "ccpiu_a2020" then ccpiu_a2020 else if e == "ccpiu_a2021" then ccpiu_a2021 else
  if e == "ccpiu_v2022" then ccpiu_v2022 else if e == "ccpiu_v2023" then ccpiu_v2023 else if e == "ccpiu_v2024" then ccpiu_v2024
  else if e == "ccpiu_v2025" then ccpiu_v2025 else ccpiu_v2026

def statute (i : Item) : Nat :=
  let q := if i.era == "cpiu" then ratioCPIU i.ty i.by_ else ratioC (vint i.era) i.ty i.by_
  adjustND i.base q.1 q.2 i.rnd

def items : List Item := [
@@ITEMS@@
]

def main : IO Unit := do
  for i in items do
    let s := statute i
    IO.println s!"{i.key}\t{i.ty}\t{if s == i.pub then "pass" else "FAIL"}\tstatute {s} published {i.pub} ({i.era})\t{i.cite}"
'''
open(H + '/lean/Audit/IndexRun.lean', 'w').write(lean.replace('@@ITEMS@@', ',\n'.join(lines)).replace('\\t', '\t'))
json.dump(derived, open(H + '/indexing/derived.json', 'w'))
print(len(lines), 'items;', len(derived), 'derived')
for d in derived:
    if d[3] != d[4]: print('DERIVED MISMATCH', d)
