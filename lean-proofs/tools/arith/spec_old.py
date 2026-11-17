"""Item 6: Rev. Procs. 2023-34 (tax year 2024) and 2022-38 (tax year 2023), a subset of the items of spec.py.
Text in force for those years: the versions before Pub. L. 119-21 (every §1(j) amount base 2017; §132(f) base 1998).
Importing this module appends the items to spec.ITEMS."""
from spec import I, ITEMS, BR, STATUS_CITE, P75

add = ITEMS.append
C, Dd = 'rp-23-34', 'rp-22-38'
OLD_BR = {
    2024: {'mfj': [23200, 94300, 201050, 383900, 487450, 731200], 'hoh': [16550, 63100, 100500, 191950, 243700, 609350],
           'single': [11600, 47150, 100525, 191950, 243725, 609350], 'mfs': [11600, 47150, 100525, 191950, 243725, 365600],
           'est': [3100, 11150, 15200]},
    2023: {'mfj': [22000, 89450, 190750, 364200, 462500, 693750], 'hoh': [15700, 59850, 95350, 182100, 231250, 578100],
           'single': [11000, 44725, 95375, 182100, 231250, 578125], 'mfs': [11000, 44725, 95375, 182100, 231250, 346875],
           'est': [2900, 10550, 14450]},
}
OLD = {
    2024: dict(doc=C, cg=dict(z_mfj=94050, z_hoh=63000, z_est=3150, f_mfj=583750, f_hoh=551350, f_single=518900, f_est=15450),
               eic=dict(ei1=12390, ei2=17400, ei0=8260, ph=22720, ph0=10330, phj=29640, phj0=17250, inv=11600),
               amt=dict(ex_mfj=133300, ex_s=85700, ex_est=29900, b28=232600, po_mfj=1218700, po_est=99700), kiddie=9250,
               sd=dict(single=14600, hoh=21900, dmin=1300, dadd=450, aged=1550, aun=1950), transit=315, savbond=(145200, 96800),
               exemption=5050, trust=5000, levy=5000, feie=126500, bea=13610000, gift=(18000, 185000), e2pct=1850000,
               pen=dict(fy=2025, ff=510, a1=330, a1m=3987000, d1A=1329000, e=660, eC=33220, eCc=132500)),
    2023: dict(doc=Dd, cg=dict(z_mfj=89250, z_hoh=59750, z_est=3000, f_mfj=553850, f_hoh=523050, f_single=492300, f_est=14650),
               eic=dict(ei1=11750, ei2=16510, ei0=7840, ph=21560, ph0=9800, phj=28120, phj0=16370, inv=11000),
               amt=dict(ex_mfj=126500, ex_s=81300, ex_est=28400, b28=220700, po_mfj=1156300, po_est=94600), kiddie=8800,
               sd=dict(single=13850, hoh=20800, dmin=1250, dadd=400, aged=1500, aun=1850), transit=300, savbond=(137800, 91850),
               exemption=4700, trust=4700, levy=4700, feie=120000, bea=12920000, gift=(17000, 175000), e2pct=1750000,
               pen=dict(fy=2024, ff=485, a1=310, a1m=3783000, d1A=1261000, e=630, eC=31520, eCc=126000)),
}
OLD_MFS15 = {2024: 291850, 2023: 276900}

for ty, o in OLD.items():
    doc = o['doc']
    for st, tops in BR.items():
        m = 25 if st in ('single', 'mfs') else 50
        for k, b in enumerate(tops):
            add(I(doc, '3.01', f'br_{st}_{k+1}', f'§{STATUS_CITE[st]}, §1(j)(3)(B) (pre-2025-Act: base 2017), §1(f)(7)', b, 2017, ty,
                  ('inc_down', m), OLD_BR[ty][st][k]))
    for k, b in (('z_mfj', 77200), ('z_hoh', 51700), ('z_est', 2600), ('f_mfj', 479000), ('f_hoh', 452400), ('f_single', 425800), ('f_est', 12700)):
        add(I(doc, '3.03', 'cg_' + k, '§1(j)(5)(B), §1(j)(5)(C)', b, 2017, ty, ('inc_down', 50), o['cg'][k]))
    e = o['eic']
    for k, b in (('ei1', 6330), ('ei2', 8890), ('ei0', 4220), ('ph', 11610), ('ph0', 5280)):
        add(I(doc, '3.06', 'eic_' + k, '§32(b)(2)(A), §32(j)', b, 1995, ty, ('amt_near', 10), e[k]))
    add(I(doc, '3.06', 'eic_phj', '§32(b)(2)(A)+(B), §32(j)', [(11610, 1995), (5000, 2008)], 'parts', ty, ('amt_near', 10), e['phj']))
    add(I(doc, '3.06', 'eic_phj0', '§32(b)(2)(A)+(B), §32(j)', [(5280, 1995), (5000, 2008)], 'parts', ty, ('amt_near', 10), e['phj0']))
    add(I(doc, '3.06', 'eic_inv', '§32(i)(1), §32(j)', 10000, 2020, ty, ('amt_down', 50), e['inv']))
    a = o['amt']
    add(I(doc, '3.11', 'amt_ex_mfj', '§55(d)(4)(A)(i)(I), (d)(4)(B)', 109400, 2017, ty, ('amt_near', 100), a['ex_mfj']))
    add(I(doc, '3.11', 'amt_ex_single', '§55(d)(4)(A)(i)(II), (d)(4)(B)', 70300, 2017, ty, ('amt_near', 100), a['ex_s']))
    add(I(doc, '3.11', 'amt_ex_est', '§55(d)(1)(D), (d)(3)', 22500, 2011, ty, ('amt_near', 100), a['ex_est']))
    add(I(doc, '3.11', 'amt_28', '§55(b)(1)(A), (d)(3)', 175000, 2011, ty, ('amt_near', 100), a['b28']))
    add(I(doc, '3.11', 'amt_po_mfj', '§55(d)(4)(A)(ii)(I), (d)(4)(B)', 1000000, 2017, ty, ('amt_near', 100), a['po_mfj']))
    add(I(doc, '3.11', 'amt_po_est', '§55(d)(2)(C), (d)(3)', 75000, 2011, ty, ('amt_near', 100), a['po_est']))
    add(I(doc, '3.12', 'kiddie_amt', '§59(j)', 5000, 1997, ty, ('inc_near', 50), o['kiddie']))
    s = o['sd']
    add(I(doc, '3.15', 'sd_single', '§63(c)(7) (pre-2025-Act: $12,000, base 2017)', 12000, 2017, ty, ('inc_down', 50), s['single']))
    add(I(doc, '3.15', 'sd_hoh', '§63(c)(7) (pre-2025-Act: $18,000, base 2017)', 18000, 2017, ty, ('inc_down', 50), s['hoh']))
    add(I(doc, '3.15', 'sd_dep_min', '§63(c)(5)(A), (c)(4)', 500, 1987, ty, ('inc_down', 50), s['dmin']))
    add(I(doc, '3.15', 'sd_dep_add', '§63(c)(5)(B), (c)(4)', 250, 1997, ty, ('inc_down', 50), s['dadd']))
    add(I(doc, '3.15', 'sd_aged', '§63(f)(1),(2), (c)(4)', 600, 1987, ty, ('inc_down', 50), s['aged']))
    add(I(doc, '3.15', 'sd_aged_unmarried', '§63(f)(3), (c)(4)', 750, 1987, ty, ('inc_down', 50), s['aun']))
    add(I(doc, '3.17', 'transit', '§132(f)(2)(A), (f)(6) (base 1998 before Pub. L. 119-21)', 175, 1998, ty, ('inc_down', 5), o['transit']))
    add(I(doc, '3.18', 'savbond_joint', '§135(b)(2)', 60000, 1989, ty, ('amt_near', 50), o['savbond'][0]))
    add(I(doc, '3.18', 'savbond_other', '§135(b)(2)', 40000, 1989, ty, ('amt_near', 50), o['savbond'][1]))
    add(I(doc, '3.24', 'exemption', '§151(d)(1),(4)', 2000, 1988, ty, ('inc_down', 50), o['exemption']))
    add(I(doc, '3.35', 'trust_exempt', '§642(b)(2)(C)(iii), §6334(d)(4)(C)', 4150, 2017, ty, ('inc_down', 100), o['trust']))
    add(I(doc, '3.5x', 'levy_wage', '§6334(d)(4)(B),(C)', 4150, 2017, ty, ('inc_down', 100), o['levy']))
    add(I(doc, '3.39', 'feie', '§911(b)(2)(D)', 80000, 2004, ty, ('inc_down', 100), o['feie']))
    add(I(doc, '3.41', 'estate_bea', '§2010(c)(3) (pre-2025-Act: $10,000,000, base 2010)', 10000000, 2010, ty, ('amt_near', 10000), o['bea']))
    add(I(doc, '3.43', 'gift_annual', '§2503(b)', 10000, 1997, ty, ('amt_down', 1000), o['gift'][0]))
    add(I(doc, '3.43', 'gift_spouse', '§2523(i)(2), §2503(b)(2)', 100000, 1997, ty, ('amt_down', 1000), o['gift'][1]))
    add(I(doc, '3.5x', 'estate_2pct', '§6601(j)', 1000000, 1997, ty, ('amt_down', 10000), o['e2pct']))
    p = o['pen']; fy = p['fy']
    add(I(doc, '3.5x', 'p6651', '§6651(a), (j)', 435, 2019, fy, ('amt_down', 5), p['ff']))
    for k, b in (('a1', 250), ('a1m', 3000000), ('d1A', 1000000), ('e', 500), ('eC', 25000), ('eCc', 100000)):
        add(I(doc, '3.5x', 'p6721_' + k, '§6721, §6721(f)', b, 2011, fy, P75, p[k]))
