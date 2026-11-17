"""Inflation-adjusted items of Rev. Proc. 2024-40 (tax year 2025) and Rev. Proc. 2025-32 (tax year 2026),
each with the statutory base amount, base year and rounding rule read from Title 26 (OLRC release point through
Pub. L. 119-138; for 2025 items the text as it stood before Pub. L. 119-21 where that Act changed it later, from the
OLRC amendment notes).

Fields of an item:
  doc   'rp-24-40' | 'rp-25-32'
  sec   Rev. Proc. section number
  id    short identifier (becomes the Lean name)
  cite  statute subdivision that sets the base amount / the adjustment
  base  base amount (whole dollars, or cents if unit 'c')
  by    base year substituted for "calendar year 2016" in §1(f)(3)(A)(ii)
  cy    calendar year whose cost-of-living adjustment applies (the tax year, or the filing year for penalties)
  rnd   rounding: ('inc_down', m) | ('inc_near', m) | ('amt_down', m) | ('amt_near', m) | ('pen', thr, big, small)
        | ('none',) [no statutory rounding: compared after truncation to whole dollars] | ('fixed',) [no adjustment]
  pub   published amount (same units as base)
  unit  '$' or 'c' (cents)
  note  free text
Derived items (structural checks, e.g. MFS = half of MFJ) are in DERIVED below.
"""

def I(doc, sec, id, cite, base, by, cy, rnd, pub, unit='$', note=''):
    return dict(doc=doc, sec=sec, id=id, cite=cite, base=base, by=by, cy=cy, rnd=rnd, pub=pub, unit=unit, note=note)

A, B = 'rp-24-40', 'rp-25-32'
ITEMS = []
add = ITEMS.append

# ---------------------------------------------------------------- §1(j) rate tables
BR = {  # §1(j)(2) 2018 bracket tops (ends of the 10,12,22,24,32,35% brackets; estates 10,24,35%)
    'mfj': [19050, 77400, 165000, 315000, 400000, 600000],
    'hoh': [13600, 51800, 82500, 157500, 200000, 500000],
    'single': [9525, 38700, 82500, 157500, 200000, 500000],
    'mfs': [9525, 38700, 82500, 157500, 200000, 300000],
    'est': [2550, 9150, 12500],
}
PUB_BR = {
    2025: {'mfj': [23850, 96950, 206700, 394600, 501050, 751600], 'hoh': [17000, 64850, 103350, 197300, 250500, 626350],
           'single': [11925, 48475, 103350, 197300, 250525, 626350], 'mfs': [11925, 48475, 103350, 197300, 250525, 375800],
           'est': [3150, 11450, 15650]},
    2026: {'mfj': [24800, 100800, 211400, 403550, 512450, 768700], 'hoh': [17700, 67450, 105700, 201750, 256200, 640600],
           'single': [12400, 50400, 105700, 201775, 256225, 640600], 'mfs': [12400, 50400, 105700, 201775, 256225, 384350],
           'est': [3300, 11700, 16000]},
}
STATUS_CITE = {'mfj': '1(j)(2)(A)', 'hoh': '1(j)(2)(B)', 'single': '1(j)(2)(C)', 'mfs': '1(j)(2)(D)', 'est': '1(j)(2)(E)'}
for ty, doc, sec in ((2025, A, '2.01'), (2026, B, '4.01')):
    for st, tops in BR.items():
        m = 25 if st in ('single', 'mfs') else 50          # §1(j)(3)(B)(ii), §1(f)(7)(B)
        for k, b in enumerate(tops):
            # §1(j)(3)(B)(i): 2025 (text before Pub. L. 119-21 §70101(b)): every amount uses 2017.
            # 2026: 2017 only for amounts at which a bracket above 12% ends or a bracket above 22% begins.
            if ty == 2025:
                by = 2017
            elif st == 'est':
                by = 2017   # every estate threshold ends the 10/24/35% bracket and begins the 24/35/37% bracket
            else:
                by = 2016 if k <= 1 else 2017
            add(I(doc, sec, f'br_{st}_{k+1}', f'§{STATUS_CITE[st]}, §1(j)(3)(B), §1(f)(7)', b, by, ty, ('inc_down', m),
                  PUB_BR[ty][st][k], note='estate first threshold also begins the 24% bracket' if st == 'est' and k == 0 else ''))

# §1(j)(5) capital gains breakpoints (base year 2017, increase down to $50)
for ty, doc, sec, p in ((2025, A, '2.03', dict(z_mfj=96700, z_hoh=64750, z_est=3250, f_mfj=600050, f_hoh=566700, f_single=533400, f_est=15900)),
                        (2026, B, '4.03', dict(z_mfj=98900, z_hoh=66200, z_est=3300, f_mfj=613700, f_hoh=579600, f_single=545500, f_est=16250))):
    for k, b, c in (('z_mfj', 77200, '1(j)(5)(B)(i)(I)'), ('z_hoh', 51700, '1(j)(5)(B)(i)(II)'), ('z_est', 2600, '1(j)(5)(B)(i)(IV)'),
                    ('f_mfj', 479000, '1(j)(5)(B)(ii)(I)'), ('f_hoh', 452400, '1(j)(5)(B)(ii)(II)'), ('f_single', 425800, '1(j)(5)(B)(ii)(III)'),
                    ('f_est', 12700, '1(j)(5)(B)(ii)(IV)')):
        add(I(doc, sec, 'cg_' + k, '§' + c + ', §1(j)(5)(C)', b, 2017, ty, ('inc_down', 50), p[k]))

# ---------------------------------------------------------------- credits
for ty, doc, s, pub in ((2025, A, '2.04', 17280), (2026, B, '4.04', 17670)):
    add(I(doc, s, 'adopt_special', '§23(a)(3), §23(h)', 10000, 2001, ty, ('amt_near', 10), pub))
    add(I(doc, s, 'adopt_limit', '§23(b)(1), §23(h)', 10000, 2001, ty, ('amt_near', 10), pub))
add(I(A, '2.04', 'adopt_phase', '§23(b)(2)(A)(i), §23(h)', 150000, 2001, 2025, ('amt_near', 10), 259190))
add(I(B, '4.04', 'adopt_phase', '§23(b)(2)(A)(i), §23(h)', 150000, 2001, 2026, ('amt_near', 10), 265080))
add(I(B, '4.04', 'adopt_refundable', '§23(a)(4), §23(h)(3)', 5000, 2024, 2026, ('amt_near', 10), 5120))
add(I(A, '2.05', 'ctc_refundable', '§24(h)(5) (pre-2025-Act text), §24(i)', 1400, 2017, 2025, ('inc_down', 100), 1700))
add(I(B, '4.05', 'ctc_refundable', '§24(h)(5), §24(i)(1),(3)', 1400, 2017, 2026, ('inc_down', 100), 1700))
add(I(B, '4.05', 'ctc_max', '§24(h)(2), §24(i)(2),(3)', 2200, 2024, 2026, ('inc_down', 100), 2200))

# §32: earned income amounts and phaseout amounts (base 1995), joint increase $5,000 (base 2008), §32(i) (base 2020)
for ty, doc, s, p in ((2025, A, '2.06', dict(ei1=12730, ei2=17880, ei0=8490, ph=23350, ph0=10620, phj=30470, phj0=17730, inv=11950)),
                      (2026, B, '4.06', dict(ei1=13020, ei2=18290, ei0=8680, ph=23890, ph0=10860, phj=31160, phj0=18140, inv=12200))):
    add(I(doc, s, 'eic_ei1', '§32(b)(2)(A), §32(j)(1)(B)(i), (j)(2)(A)', 6330, 1995, ty, ('amt_near', 10), p['ei1']))
    add(I(doc, s, 'eic_ei2', '§32(b)(2)(A), §32(j)(1)(B)(i), (j)(2)(A)', 8890, 1995, ty, ('amt_near', 10), p['ei2']))
    add(I(doc, s, 'eic_ei0', '§32(b)(2)(A), §32(j)(1)(B)(i), (j)(2)(A)', 4220, 1995, ty, ('amt_near', 10), p['ei0']))
    add(I(doc, s, 'eic_ph', '§32(b)(2)(A), §32(j)(1)(B)(i), (j)(2)(A)', 11610, 1995, ty, ('amt_near', 10), p['ph']))
    add(I(doc, s, 'eic_ph0', '§32(b)(2)(A), §32(j)(1)(B)(i), (j)(2)(A)', 5280, 1995, ty, ('amt_near', 10), p['ph0']))
    add(I(doc, s, 'eic_phj', '§32(b)(2)(A)+(B), §32(j)(1)(B)(i),(ii), (j)(2)(A)', [(11610, 1995), (5000, 2008)], 'parts', ty, ('amt_near', 10), p['phj'],
          note='($11,610 x COLA95) + ($5,000 x COLA08), one rounding'))
    add(I(doc, s, 'eic_phj0', '§32(b)(2)(A)+(B), §32(j)(1)(B)(i),(ii), (j)(2)(A)', [(5280, 1995), (5000, 2008)], 'parts', ty, ('amt_near', 10), p['phj0'],
          note='($5,280 x COLA95) + ($5,000 x COLA08), one rounding'))
    add(I(doc, s, 'eic_inv', '§32(i)(1), §32(j)(1)(B)(iii), (j)(2)(B)', 10000, 2020, ty, ('amt_down', 50), p['inv']))

# ---------------------------------------------------------------- AMT §55
for ty, doc, s, p in ((2025, A, '2.11', dict(ex_mfj=137000, ex_s=88100, ex_est=30700, b28=239100, po_est=102500)),
                      (2026, B, '4.10', dict(ex_mfj=140200, ex_s=90100, ex_est=31400, b28=244500, po_est=104800))):
    add(I(doc, s, 'amt_ex_mfj', '§55(d)(4)(A)(i)(I), §55(d)(4)(B)', 109400, 2017, ty, ('amt_near', 100), p['ex_mfj']))
    add(I(doc, s, 'amt_ex_single', '§55(d)(4)(A)(i)(II), §55(d)(4)(B)', 70300, 2017, ty, ('amt_near', 100), p['ex_s']))
    add(I(doc, s, 'amt_ex_est', '§55(d)(1)(D), §55(d)(3)', 22500, 2011, ty, ('amt_near', 100), p['ex_est']))
    add(I(doc, s, 'amt_28', '§55(b)(1)(A), §55(d)(3)(B)(i)', 175000, 2011, ty, ('amt_near', 100), p['b28']))
    add(I(doc, s, 'amt_po_est', '§55(d)(2)(C) [50% of $150,000], §55(d)(3)(B)(iii)', 75000, 2011, ty, ('amt_near', 100), p['po_est'],
          note='estate threshold = 50% of the §55(d)(2)(A) $150,000, indexed as a dollar amount of (d)(2)'))
add(I(A, '2.11', 'amt_po_mfj', '§55(d)(4)(A)(ii)(I), §55(d)(4)(B)', 1000000, 2017, 2025, ('amt_near', 100), 1252700))
add(I(B, '4.10', 'amt_po_mfj', '§55(d)(4)(A)(ii)(I), §55(d)(4)(B)(i) (indexed only after 2026)', 1000000, None, 2026, ('fixed',), 1000000))

# §59(j) kiddie-tax AMT exemption
add(I(A, '2.12', 'kiddie_amt', '§59(j)(1)(B), §59(j)(2)', 5000, 1997, 2025, ('inc_near', 50), 9550))
add(I(B, '4.11', 'kiddie_amt', '§59(j)(1)(B), §59(j)(2)', 5000, 1997, 2026, ('inc_near', 50), 9750))
# §62(a)(2)(D) educator expenses
add(I(A, '2.13', 'educator', '§62(a)(2)(D), §62(d)(3)', 250, 2014, 2025, ('inc_near', 50), 300))
add(I(B, '4.12', 'educator', '§62(a)(2)(D), §62(d)(3)', 250, 2014, 2026, ('inc_near', 50), 350))

# ---------------------------------------------------------------- standard deduction
add(I(A, '2.15(1)', 'sd_single', '§63(c)(7)(A)(ii), (c)(7)(B)(ii) (pre-2025-Act: $12,000, base 2017)', 12000, 2017, 2025, ('inc_down', 50), 15000))
add(I(A, '2.15(1)', 'sd_hoh', '§63(c)(7)(A)(i), (c)(7)(B)(ii) (pre-2025-Act: $18,000, base 2017)', 18000, 2017, 2025, ('inc_down', 50), 22500))
add(I(B, '3.01', 'sd_single_2025', '§63(c)(7)(A)(ii) as amended (no 2025 adjustment)', 15750, None, 2025, ('fixed',), 15750))
add(I(B, '3.01', 'sd_hoh_2025', '§63(c)(7)(A)(i) as amended (no 2025 adjustment)', 23625, None, 2025, ('fixed',), 23625))
add(I(B, '4.14(1)', 'sd_single', '§63(c)(7)(A)(ii), (c)(7)(B)(ii)', 15750, 2024, 2026, ('inc_down', 50), 16100))
add(I(B, '4.14(1)', 'sd_hoh', '§63(c)(7)(A)(i), (c)(7)(B)(ii)', 23625, 2024, 2026, ('inc_down', 50), 24150))
for ty, doc, s, d1, d2, ab, au in ((2025, A, '2.15', 1350, 450, 1600, 2000), (2026, B, '4.14', 1350, 450, 1650, 2050)):
    add(I(doc, s + '(2)', 'sd_dep_min', '§63(c)(5)(A), §63(c)(4)(B)(i), §1(f)(7)(A)', 500, 1987, ty, ('inc_down', 50), d1))
    add(I(doc, s + '(2)', 'sd_dep_add', '§63(c)(5)(B), §63(c)(4)(B)(ii), §1(f)(7)(A)', 250, 1997, ty, ('inc_down', 50), d2))
    add(I(doc, s + '(3)', 'sd_aged', '§63(f)(1),(2), §63(c)(4)(B)(i), §1(f)(7)(A)', 600, 1987, ty, ('inc_down', 50), ab))
    add(I(doc, s + '(3)', 'sd_aged_unmarried', '§63(f)(3), §63(c)(4)(B)(i), §1(f)(7)(A)', 750, 1987, ty, ('inc_down', 50), au))
    # §1(g)(4)(A)(ii)(I) kiddie-tax amount = §63(c)(5)(A) amount: checked as DERIVED

# ---------------------------------------------------------------- exclusions, fringe benefits
add(I(A, '2.16', 'fsa', '§125(i)(1),(2)', 2500, 2012, 2025, ('inc_down', 50), 3300))
add(I(B, '4.15', 'fsa', '§125(i)(1),(2)', 2500, 2012, 2026, ('inc_down', 50), 3400))
# §132(f)(6)(A)(ii): base year 1998 until Pub. L. 119-21 §70112(b) substituted 1997 (taxable years beginning after 2025)
for ty, doc, s, pub, by in ((2025, A, '2.17', 325, 1998), (2026, B, '4.16', 340, 1997)):
    add(I(doc, s, 'transit', '§132(f)(2)(A), §132(f)(6)', 175, by, ty, ('inc_down', 5), pub))
    add(I(doc, s, 'parking', '§132(f)(2)(B), §132(f)(6)', 175, by, ty, ('inc_down', 5), pub))
for ty, doc, s, j, o in ((2025, A, '2.18', 149250, 99500), (2026, B, '4.17', 152650, 101800)):
    add(I(doc, s, 'savbond_joint', '§135(b)(2)(A),(B),(C)', 60000, 1989, ty, ('amt_near', 50), j))
    add(I(doc, s, 'savbond_other', '§135(b)(2)(A),(B),(C)', 40000, 1989, ty, ('amt_near', 50), o))
for ty, doc, s, a, ph in ((2025, A, '2.19', 17280, 259190), (2026, B, '4.18', 17670, 265080)):
    add(I(doc, s, 'adoptx_special', '§137(a)(2), §137(f)', 10000, 2001, ty, ('amt_near', 10), a))
    add(I(doc, s, 'adoptx_limit', '§137(b)(1), §137(f)', 10000, 2001, ty, ('amt_near', 10), a))
    add(I(doc, s, 'adoptx_phase', '§137(b)(2)(A), §137(f)', 150000, 2001, ty, ('amt_near', 10), ph))

# ---------------------------------------------------------------- bonds, housing
for ty, doc, s, pc, cap in ((2025, A, '2.20', 130, 388780000), (2026, B, '4.19', 135, 397625000)):
    add(I(doc, s, 'pab_percap', '§146(d)(1)(A), §146(d)(2)', 75, 2001, ty, ('inc_near', 5), pc))
    add(I(doc, s, 'pab_floor', '§146(d)(1)(B), §146(d)(2)', 225000000, 2001, ty, ('inc_near', 5000), cap))
add(I(A, '2.21', 'agbond', '§147(c)(2)(A), §147(c)(2)(H)', 450000, 2007, 2025, ('amt_near', 100), 667500))
add(I(B, '4.20', 'agbond', '§147(c)(2)(A), §147(c)(2)(H)', 450000, 2007, 2026, ('amt_near', 100), 682700))
add(I(A, '2.08', 'lihtc_rehab', '§42(e)(3)(A)(ii)(II), §42(e)(3)(D)', 6000, 2008, 2025, ('inc_near', 100), 8500))
add(I(B, '4.07', 'lihtc_rehab', '§42(e)(3)(A)(ii)(II), §42(e)(3)(D)', 6000, 2008, 2026, ('inc_near', 100), 8700))
add(I(A, '2.09', 'lihtc_percap', '§42(h)(3)(C)(ii)(I), §42(h)(3)(H)', 175, 2001, 2025, ('inc_down', 5), 300, unit='c'))
add(I(A, '2.09', 'lihtc_floor', '§42(h)(3)(C)(ii)(II), §42(h)(3)(H)', 2000000, 2001, 2025, ('inc_down', 5000), 3455000))
# 2026: §42(h)(3)(I) multiplies the (H)-adjusted amounts by 1.12 -- handled in DERIVED (needs the (H) amount first)
add(I(B, '4.08', 'lihtc_percap_H', '§42(h)(3)(C)(ii)(I), §42(h)(3)(H) (before the 1.12 of (I))', 175, 2001, 2026, ('inc_down', 5), None, unit='c'))
add(I(B, '4.08', 'lihtc_floor_H', '§42(h)(3)(C)(ii)(II), §42(h)(3)(H) (before the 1.12 of (I))', 2000000, 2001, 2026, ('inc_down', 5000), None))
add(I(A, '2.10', 'sehi_wage', '§45R(d)(3)(B)(ii)', 25000, 2012, 2025, ('none',), 33300, note='statute states no rounding; IRS shows a multiple of $100'))
add(I(B, '4.09', 'sehi_wage', '§45R(d)(3)(B)(ii)', 25000, 2012, 2026, ('none',), 34100, note='statute states no rounding; IRS shows a multiple of $100'))

# ---------------------------------------------------------------- dependents, §179, §179D, §199A
add(I(A, '2.24', 'exemption', '§152(d)(1)(B) via §151(d)(1),(4) read without §151(d)(5)(A) (IRS reading; literally zero), §1(f)(7)(A)', 2000, 1988, 2025, ('inc_down', 50), 5200))
add(I(B, '4.23', 'exemption', '§152(d)(1)(B) via §151(d)(1),(4) read without §151(d)(5)(A) (IRS reading; literally zero), §1(f)(7)(A)', 2000, 1988, 2026, ('inc_down', 50), 5300))
add(I(A, '2.25', 's179_limit', '§179(b)(1) (pre-2025-Act: $1,000,000), §179(b)(6) (base 2017)', 1000000, 2017, 2025, ('inc_near', 10000), 1250000))
add(I(A, '2.25', 's179_phase', '§179(b)(2) (pre-2025-Act: $2,500,000), §179(b)(6) (base 2017)', 2500000, 2017, 2025, ('inc_near', 10000), 3130000))
add(I(A, '2.25', 's179_suv', '§179(b)(5)(A), §179(b)(6)', 25000, 2017, 2025, ('inc_near', 100), 31300))
add(I(B, '3.02', 's179_limit_2025', '§179(b)(1) as amended (2025: no adjustment)', 2500000, None, 2025, ('fixed',), 2500000))
add(I(B, '3.02', 's179_phase_2025', '§179(b)(2) as amended (2025: no adjustment)', 4000000, None, 2025, ('fixed',), 4000000))
add(I(B, '4.24', 's179_limit', '§179(b)(1), §179(b)(6)(A)(ii)(I)', 2500000, 2024, 2026, ('inc_near', 10000), 2560000))
add(I(B, '4.24', 's179_phase', '§179(b)(2), §179(b)(6)(A)(ii)(I)', 4000000, 2024, 2026, ('inc_near', 10000), 4090000))
add(I(B, '4.24', 's179_suv', '§179(b)(5)(A), §179(b)(6)(A)(ii)(II)', 25000, 2017, 2026, ('inc_near', 100), 32000))
for ty, doc, s, p in ((2025, A, '2.26', (58, 116, 2, 290, 581, 12)), (2026, B, '4.25', (59, 119, 2, 297, 594, 12))):
    for (k, b), v in zip((('min', 50), ('max', 100), ('step', 2), ('inc_min', 250), ('inc_max', 500), ('inc_step', 10)), p):
        add(I(doc, s, 's179d_' + k, '§179D(b)(2),(3), §179D(g)', b, 2021, ty, ('inc_near', 1), v, unit='c'))
add(I(A, '2.27', 'qbi_thr', '§199A(e)(2)(A),(B), §1(f)(7)', 157500, 2017, 2025, ('inc_down', 50), 197300))
add(I(A, '2.27', 'qbi_thr_mfs', '§199A(e)(2)(B), §1(f)(7)(B) ($25 for MFS)', 157500, 2017, 2025, ('inc_down', 25), 197300))
add(I(B, '4.26', 'qbi_thr', '§199A(e)(2)(A),(B), §1(f)(7)', 157500, 2017, 2026, ('inc_down', 50), 201750))
add(I(B, '4.26', 'qbi_thr_mfs', '§199A(e)(2)(B), §1(f)(7)(B) ($25 for MFS)', 157500, 2017, 2026, ('inc_down', 25), 201775))

# ---------------------------------------------------------------- MSAs, student loans, accounting
for ty, doc, s, p in ((2025, A, '2.29', (2850, 4300, 5700, 5700, 8550, 10500)), (2026, B, '4.28', (2900, 4400, 5850, 5850, 8750, 10700))):
    for (k, b, c), v in zip((('self_min', 1500, '(c)(2)(A)(i)'), ('self_max', 2250, '(c)(2)(A)(i)'), ('self_oop', 3000, '(c)(2)(A)(iii)(I)'),
                             ('fam_min', 3000, '(c)(2)(A)(ii)'), ('fam_max', 4500, '(c)(2)(A)(ii)'), ('fam_oop', 5500, '(c)(2)(A)(iii)(II)')), p):
        add(I(doc, s, 'msa_' + k, '§220' + c + ', §220(g)', b, 1997, ty, ('inc_near', 50), v))
for ty, doc, s, o, j in ((2025, A, '2.30', 85000, 170000), (2026, B, '4.29', 85000, 175000)):
    add(I(doc, s, 'sli_other', '§221(b)(2)(B)(i)(II), §221(f)', 50000, 2001, ty, ('amt_down', 5000), o))
    add(I(doc, s, 'sli_joint', '§221(b)(2)(B)(i)(II), §221(f)', 100000, 2001, ty, ('amt_down', 5000), j))
add(I(A, '2.31', 'cash_method', '§448(c)(1), §448(c)(4)', 25000000, 2017, 2025, ('amt_near', 1000000), 31000000))
add(I(B, '4.30', 'cash_method', '§448(c)(1), §448(c)(4)', 25000000, 2017, 2026, ('amt_near', 1000000), 32000000))
add(I(A, '2.32', 'ebl', '§461(l)(3)(A)(ii)(II), §461(l)(3)(C) (pre-2025-Act: base 2017)', 250000, 2017, 2025, ('amt_near', 1000), 313000))
add(I(B, '4.31', 'ebl', '§461(l)(3)(A)(ii)(II), §461(l)(3)(C)', 250000, 2024, 2026, ('amt_near', 1000), 256000))
add(I(A, '2.33', 'ag_dues', '§512(d)(1)(B), §512(d)(2)', 100, 1994, 2025, ('none',), 207, note='statute states no rounding'))
add(I(B, '4.32', 'ag_dues', '§512(d)(1)(B), §512(d)(2)', 100, 1994, 2026, ('none',), 212, note='statute states no rounding'))
add(I(A, '2.34(1)', 'low_cost', '§513(h)(2)(A),(C)', 500, 1987, 2025, ('none',), 1360, unit='c', note='statute states no rounding; IRS shows a multiple of 10 cents'))
add(I(B, '4.33(1)', 'low_cost', '§513(h)(2)(A),(C)', 500, 1987, 2026, ('none',), 1390, unit='c', note='statute states no rounding; IRS shows a multiple of 10 cents'))
add(I(A, '2.35', 'trust_exempt', '§642(b)(2)(C)(iii), §6334(d)(4)(C)', 4150, 2017, 2025, ('inc_down', 100), 5100))
add(I(B, '4.35', 'trust_exempt', '§642(b)(2)(C)(iii), §6334(d)(4)(C)', 4150, 2017, 2026, ('inc_down', 100), 5300))
add(I(A, '2.36', 'ins_831b', '§831(b)(2)(A)(i), §831(b)(2)(E)', 2200000, 2013, 2025, ('amt_down', 50000), 2850000))
add(I(B, '4.36', 'ins_831b', '§831(b)(2)(A)(i), §831(b)(2)(E)', 2200000, 2013, 2026, ('amt_down', 50000), 2900000))
add(I(A, '2.37', 'expat_tax', '§877(a)(2)(A) (cross-reference to "subparagraph (B)" read as base year 2003)', 124000, 2003, 2025, ('none',), 206000,
      note='statute states no rounding; IRS shows a multiple of $1,000'))
add(I(B, '4.37', 'expat_tax', '§877(a)(2)(A) (cross-reference to "subparagraph (B)" read as base year 2003)', 124000, 2003, 2026, ('none',), 211000,
      note='statute states no rounding; IRS shows a multiple of $1,000'))
add(I(A, '2.38', 'expat_excl', '§877A(a)(3)(A), §877A(a)(3)(B)', 600000, 2007, 2025, ('amt_near', 1000), 890000))
add(I(B, '4.38', 'expat_excl', '§877A(a)(3)(A), §877A(a)(3)(B)', 600000, 2007, 2026, ('amt_near', 1000), 910000))
add(I(A, '2.39', 'feie', '§911(b)(2)(D)(i),(ii)', 80000, 2004, 2025, ('inc_down', 100), 130000))
add(I(B, '4.39', 'feie', '§911(b)(2)(D)(i),(ii)', 80000, 2004, 2026, ('inc_down', 100), 132900))
for ty, doc, s, q, c in ((2025, A, '2.40', 7296700, 5211900), (2026, B, '4.40', 7462600, 5330500)):
    add(I(doc, s, 'debt_qualified', '§1274A(b), §1274A(d)(2)', 2800000, 1988, ty, ('inc_near', 100), q))
    add(I(doc, s, 'debt_cash', '§1274A(c)(2)(A), §1274A(d)(2)', 2000000, 1988, ty, ('inc_near', 100), c))

# ---------------------------------------------------------------- estate and gift
add(I(B, '2.14', 'estate_bea', '§2010(c)(3)(A),(B) (indexed only after 2026)', 15000000, None, 2026, ('fixed',), 15000000))
add(I(A, '2.41', 'estate_bea', '§2010(c)(3) (pre-2025-Act: $10,000,000 for 2018-2025, base 2010)', 10000000, 2010, 2025, ('amt_near', 10000), 13990000))
add(I(A, '2.42', 'sp_use', '§2032A(a)(2), §2032A(a)(3)', 750000, 1997, 2025, ('amt_down', 10000), 1420000))
add(I(B, '4.41', 'sp_use', '§2032A(a)(2), §2032A(a)(3)', 750000, 1997, 2026, ('amt_down', 10000), 1460000))
for ty, doc, s, g, sp in ((2025, A, '2.43', 19000, 190000), (2026, B, '4.42', 19000, 194000)):
    add(I(doc, s + '(1)', 'gift_annual', '§2503(b)(1), §2503(b)(2)', 10000, 1997, ty, ('amt_down', 1000), g))
    add(I(doc, s + '(2)', 'gift_spouse', '§2523(i)(2), §2503(b)(2)', 100000, 1997, ty, ('amt_down', 1000), sp,
          note='$100,000 substituted for $10,000 in §2503(b); the (b)(2) adjustment and $1,000 rounding apply to it'))
add(I(B, '4.34', 'able_limit', '§529A(b)(2)(B)(i): §2503(b) amount with base year 1996', 10000, 1996, 2026, ('amt_down', 1000), 20000))
add(I(B, '4.42(3)', 'covered_gift', '§2801(c) (= §2503(b) amount)', 10000, 1997, 2026, ('amt_down', 1000), 19000))

# ---------------------------------------------------------------- excise
add(I(A, '2.44', 'arrow', '§4161(b)(2)(A),(C)', 39, 2004, 2025, ('inc_near', 1), 63, unit='c'))
add(I(B, '4.43', 'arrow', '§4161(b)(2)(A),(C)', 39, 2004, 2026, ('inc_near', 1), 65, unit='c'))
for ty, doc, s, p in ((2025, A, '2.45', (520, 2290, 1140)), (2026, B, '4.44', (530, 2340, 1170))):
    add(I(doc, s, 'air_dom', '§4261(b)(1), §4261(e)(4) (last nonindexed year 2002)', 300, 2001, ty, ('inc_near', 10), p[0], unit='c'))
    add(I(doc, s, 'air_intl', '§4261(c)(1), §4261(e)(4) (last nonindexed year 1998)', 1200, 1997, ty, ('inc_near', 10), p[1], unit='c'))
    add(I(doc, s, 'air_akhi', '§4261(c)(3), §4261(e)(4) (last nonindexed year 1998)', 600, 1997, ty, ('inc_near', 10), p[2], unit='c'))
# §4611: superfund rate 16.4 cents (in tenths of a cent) indexed; published total includes the 9-cent oil spill rate (DERIVED)
add(I(A, '2.46', 'superfund', '§4611(c)(2)(A), §4611(c)(3)', 164, 2022, 2025, ('amt_down', 10), None, unit='m',
      note='amounts in tenths of a cent; rounded down to $0.01'))
add(I(B, '4.45', 'superfund', '§4611(c)(2)(A), §4611(c)(3)', 164, 2022, 2026, ('amt_down', 10), None, unit='m',
      note='amounts in tenths of a cent; rounded down to $0.01'))

# ---------------------------------------------------------------- procedure
add(I(A, '2.48', 'foreign_gift', '§6039F(a), §6039F(d)', 10000, 1995, 2025, ('none',), 20116, note='statute states no rounding'))
add(I(B, '4.47', 'foreign_gift', '§6039F(a), §6039F(d)', 10000, 1995, 2026, ('none',), 20573, note='statute states no rounding'))
for ty, doc, s, a, b in ((2025, A, '2.49', 1960, 9790), (2026, B, '4.48', 2000, 10010)):
    add(I(doc, s, 'lien_casual', '§6323(b)(4), §6323(i)(4)', 1000, 1996, ty, ('amt_near', 10), a))
    add(I(doc, s, 'lien_mech', '§6323(b)(7), §6323(i)(4)', 5000, 1996, ty, ('amt_near', 10), b))
for ty, doc, s, a, b in ((2025, A, '2.50', 11710, 5860), (2026, B, '4.49', 11980, 5990)):
    add(I(doc, s, 'levy_goods', '§6334(a)(2), §6334(g)', 6250, 1998, ty, ('amt_near', 10), a))
    add(I(doc, s, 'levy_tools', '§6334(a)(3), §6334(g)', 3125, 1998, ty, ('amt_near', 10), b))
add(I(A, '2.51', 'levy_wage', '§6334(d)(4)(B),(C)', 4150, 2017, 2025, ('inc_down', 100), 5100))
add(I(B, '4.50', 'levy_wage', '§6334(d)(4)(B),(C)', 4150, 2017, 2026, ('inc_down', 100), 5300))
add(I(A, '2.52', 'estate_2pct', '§6601(j)(2)(A), §6601(j)(3)', 1000000, 1997, 2025, ('amt_down', 10000), 1900000))
add(I(B, '4.51', 'estate_2pct', '§6601(j)(2)(A), §6601(j)(3)', 1000000, 1997, 2026, ('amt_down', 10000), 1940000))
add(I(A, '2.60', 'passport', '§7345(b)(1)(B), §7345(f)', 50000, 2015, 2025, ('amt_near', 1000), 64000))
add(I(B, '4.60', 'passport', '§7345(b)(1)(B), §7345(f)', 50000, 2015, 2026, ('amt_near', 1000), 66000))
add(I(A, '2.61', 'atty_fee', '§7430(c)(1)(B)(iii)', 125, 1995, 2025, ('amt_near', 10), 250))
add(I(B, '4.61', 'atty_fee', '§7430(c)(1)(B)(iii)', 125, 1995, 2026, ('amt_near', 10), 260))
add(I(A, '2.62', 'ltc_perdiem', '§7702B(d)(4),(5), §213(d)(10)(B)', 175, 'med', 2025, ('inc_near', 10), 420, note='medical care cost adjustment'))
add(I(B, '4.62', 'ltc_perdiem', '§7702B(d)(4),(5), §213(d)(10)(B)', 175, 'med', 2026, ('inc_near', 10), 430, note='medical care cost adjustment'))
for ty, doc, s, p in ((2025, A, '2.28', (480, 900, 1800, 4810, 6020)), (2026, B, '4.27', (500, 930, 1860, 4960, 6200))):
    for (k, b), v in zip((('40', 200), ('50', 375), ('60', 750), ('70', 2000), ('71', 2500)), p):
        add(I(doc, s, 'ltc_prem_' + k, '§213(d)(10)(A),(B)', b, 'med', ty, ('inc_near', 10), v, note='medical care cost adjustment'))
for ty, doc, s, a, b in ((2025, A, '2.63', 6350, 12800), (2026, B, '4.63', 6450, 13100)):
    add(I(doc, s, 'qsehra_self', '§9831(d)(2)(B)(iii), §9831(d)(2)(D)(ii)', 4950, 2015, ty, ('amt_down', 50), a))
    add(I(doc, s, 'qsehra_family', '§9831(d)(2)(B)(iii), §9831(d)(2)(D)(ii)', 10000, 2015, ty, ('amt_down', 50), b))

# ---------------------------------------------------------------- penalties: cy = calendar year of filing (statute)
P5 = ('pen', 5000, 500, 5)        # §6652(c)(7)(B), §6695(h)(2)
P75 = ('pen', 75000, 500, 10)     # §6721(f)(2), §6722(f)(2)
for fy, doc, s in ((2026, A, '2.'), (2027, B, '4.')):
    pre = s
    n = {A: dict(f6651='53', f6652='54', f6695='55', f6698='56', f6699='57', f6721='58', f6722='59'),
         B: dict(f6651='52', f6652='53', f6695='54', f6698='55', f6699='56', f6721='57', f6722='58')}[doc]
    pub = {2026: dict(ff=525, d1=25, m1=13000, d1l=130, m1l=65000, gr=1309500, mgr=10, mgrm=6500, pi=25, pim=13000, pia=25,
                      t2=10, t2m=6500, si=25, sim=13000, tl=130, tlm=65000, tg=327000, d3=130, m3=65000, d3b=130, m3b=13000,
                      p95=65, p95m=32500, p95f=650, p95g=650, pp=255,
                      a1=340, a1m=4098500, b1=60, b1m=683000, b2=130, b2m=2049000, d1A=1366000, d1B=239000, d1C=683000, e=680, eC=34150, eCc=136500),
           2027: dict(ff=535, d1=25, m1=13000, d1l=130, m1l=66500, gr=1339500, mgr=10, mgrm=6500, pi=25, pim=13000, pia=25,
                      t2=10, t2m=6500, si=25, sim=13000, tl=130, tlm=66500, tg=334500, d3=130, m3=66500, d3b=130, m3b=13000,
                      p95=65, p95m=33000, p95f=665, p95g=665, pp=260,
                      a1=340, a1m=4191500, b1=60, b1m=698500, b2=130, b2m=2095500, d1A=1397000, d1B=244500, d1C=698500, e=690, eC=34930, eCc=139500)}[fy]
    add(I(doc, pre + n['f6651'], 'p6651', '§6651(a) flush, §6651(j)', 435, 2019, fy, ('amt_down', 5), pub['ff']))
    for k, b, c in (('d1', 20, '(c)(1)(A) daily'), ('m1', 10000, '(c)(1)(A) max'), ('d1l', 100, '(c)(1)(A) large-org daily'),
                    ('m1l', 50000, '(c)(1)(A) large-org max'), ('gr', 1000000, '(c)(1)(A) gross receipts'), ('mgr', 10, '(c)(1)(B)(ii) daily'),
                    ('mgrm', 5000, '(c)(1)(B)(ii) max'), ('pi', 20, '(c)(1)(C) daily'), ('pim', 10000, '(c)(1)(C) max'), ('pia', 20, '(c)(1)(D) daily'),
                    ('t2', 10, '(c)(2)(A) daily'), ('t2m', 5000, '(c)(2)(A) max'), ('si', 20, '(c)(2)(C) daily (via (c)(1)(A))'),
                    ('sim', 10000, '(c)(2)(C) max (via (c)(1)(A))'), ('tl', 100, '(c)(2)(C)(ii) daily'), ('tlm', 50000, '(c)(2)(C)(ii) max'),
                    ('tg', 250000, '(c)(2)(C)(ii) gross income'), ('d3', 100, '(c)(3)(A) daily'), ('m3', 50000, '(c)(3)(A) max'),
                    ('d3b', 100, '(c)(3)(B)(ii) daily'), ('m3b', 10000, '(c)(3)(B)(ii) max')):
        add(I(doc, pre + n['f6652'], 'p6652_' + k, '§6652' + c + ', §6652(c)(7)', b, 2013, fy, P5, pub[k]))
    add(I(doc, pre + n['f6695'], 'p6695_ae', '§6695(a)-(e), §6695(h)', 50, 2013, fy, P5, pub['p95']))
    add(I(doc, pre + n['f6695'], 'p6695_ae_max', '§6695(a)-(e) max, §6695(h)', 25000, 2013, fy, P5, pub['p95m']))
    add(I(doc, pre + n['f6695'], 'p6695_f', '§6695(f), §6695(h)', 500, 2013, fy, P5, pub['p95f']))
    add(I(doc, pre + n['f6695'], 'p6695_g', '§6695(g), §6695(h)', 500, 2013, fy, P5, pub['p95g']))
    add(I(doc, pre + n['f6698'], 'p6698', '§6698(b)(1), §6698(e)', 195, 2013, fy, ('amt_down', 5), pub['pp']))
    add(I(doc, pre + n['f6699'], 'p6699', '§6699(b)(1), §6699(e)', 195, 2013, fy, ('amt_down', 5), pub['pp']))
    for sect, sec_n in (('6721', n['f6721']), ('6722', n['f6722'])):
        for k, b, c in (('a1', 250, '(a)(1)'), ('a1m', 3000000, '(a)(1) max'), ('b1', 50, '(b)(1)(A)'), ('b1m', 500000, '(b)(1)(B)'),
                        ('b2', 100, '(b)(2)(A)'), ('b2m', 1500000, '(b)(2)(B)'), ('d1A', 1000000, '(d)(1)(A)'), ('d1B', 175000, '(d)(1)(B)'),
                        ('d1C', 500000, '(d)(1)(C)'), ('e', 500, '(e)(2)')) + ((('eC', 25000, '(e)(2)(C)(i)'), ('eCc', 100000, '(e)(2)(C)(ii)')) if sect == '6721' else ()):
            add(I(doc, pre + sec_n, f'p{sect}_' + k, f'§{sect}{c}, §{sect}(f)', b, 2011, fy, P75, pub[k]))
# §6726 (2025 Act), first indexed for returns filed in 2027, base 2024
for k, b, r, pub in (('daily', 500, ('amt_down', 10), 510), ('max', 10000, ('amt_down', 1000), 10000), ('large_max', 50000, ('amt_down', 1000), 51000),
                     ('assets', 10000000, ('amt_down', 10000), 10230000), ('id_daily', 2500, ('amt_down', 10), 2550),
                     ('id_max', 50000, ('amt_down', 1000), 51000), ('id_large_max', 250000, ('amt_down', 1000), 255000)):
    add(I(B, '4.59', 'p6726_' + k, '§6726(a)-(c), §6726(d)', b, 2024, 2027, r, pub))
