"""Structural checks: published amounts the statute ties to other published amounts (MFS = 1/2 MFJ, tax column of
the rate tables, completed phaseouts, ...). Each entry: doc, id, desc, lean (a decidable Prop over the names that
gen_lean.py defines: pub_<id> = published, <id> = recomputed), ok (Python evaluation of the same check)."""
from spec import ITEMS, PUB_BR

A, B = 'rp-24-40', 'rp-25-32'
PUB = {(i['doc'], i['id']): i['pub'] for i in ITEMS}
DERIVED = []

def D(doc, id, desc, lean, ok):
    DERIVED.append(dict(doc=doc, id=id, desc=desc, lean=lean, ok=bool(ok)))

# ---- tax column of the rate tables (§1(f)(2)(C): "adjusting the amounts setting forth the tax to the extent
#      necessary to reflect the adjustments in the rate brackets"); published tax amounts in cents
TAXCOL = {
    2025: {'mfj': [238500, 1115700, 3530200, 8039800, 11446200, 20215450], 'hoh': [170000, 744200, 1591200, 3846000, 5548400, 18703150],
           'single': [119250, 557850, 1765100, 4019900, 5723100, 18876975], 'mfs': [119250, 557850, 1765100, 4019900, 5723100, 10107725],
           'est': [31500, 230700, 377700]},
    2026: {'mfj': [248000, 1160000, 3593200, 8204800, 11689600, 20658350], 'hoh': [177000, 774000, 1615500, 3920700, 5663100, 19117100],
           'single': [124000, 580000, 1796600, 4102400, 5844800, 19297925], 'mfs': [124000, 580000, 1796600, 4102400, 5844800, 10329175],
           'est': [33000, 234600, 385100]},
}
RATES = {'est': [10, 24, 35]}
def taxes(rates, tops):
    out, prev, acc = [], 0, 0
    for r, t in zip(rates, tops):
        acc += r * (t - prev); prev = t; out.append(acc)
    return out
for ty, doc in ((2025, A), (2026, B)):
    for st, col in TAXCOL[ty].items():
        rates = RATES.get(st, [10, 12, 22, 24, 32, 35])
        tops = PUB_BR[ty][st]
        names = ', '.join(f'pub_br_{st}_{k+1}' for k in range(len(tops)))
        D(doc, f'taxcol_{st}', f'§1(f)(2)(C): published tax column of the {st} table (cents) = tax on the published brackets',
          f'bracketTaxes {rates} [{names}] = {col}', taxes(rates, tops) == col)

def rel(doc, id, desc, lean, ok): D(doc, id, desc, lean, ok)

for ty, doc in ((2025, A), (2026, B)):
    p = lambda k: PUB[(doc, k)]
    br = PUB_BR[ty]
    # §1(j)(5)(B)(i)(III): 0% amount for other individuals = 1/2 of the joint amount (published once for single, once MFS)
    z_other = {2025: 48350, 2026: 49450}[ty]; f_mfs = {2025: 300000, 2026: 306850}[ty]
    rel(doc, 'cg_zero_half', '§1(j)(5)(B)(i)(III): maximum zero rate amount of other individuals = 1/2 of the joint amount',
        f'pub_cg_z_mfj / 2 = {z_other} ∧ pub_cg_z_mfj % 2 = 0', p('cg_z_mfj') == 2 * z_other)
    rel(doc, 'cg_15_mfs_half', '§1(j)(5)(B)(ii)(I): MFS maximum 15-percent rate amount = 1/2 of the joint amount',
        (f'pub_cg_f_mfj = 2 * {f_mfs}' if p('cg_f_mfj') == 2 * f_mfs else f'pub_cg_f_mfj = 2 * {f_mfs} + {p("cg_f_mfj") - 2 * f_mfs}'),
        p('cg_f_mfj') == 2 * f_mfs)
    # §1(g)(4)(A)(ii)(I): kiddie-tax amount = §63(c)(5)(A) amount; parental election ceiling 10x
    rel(doc, 'kiddie_amount', '§1(g)(4)(A)(ii)(I), §1(g)(7): kiddie-tax amount $1,350 = §63(c)(5)(A) amount; election ceiling 10x',
        'pub_sd_dep_min = 1350 ∧ 10 * pub_sd_dep_min = 13500', p('sd_dep_min') == 1350)
    # standard deduction: MFJ = 200% of single (§63(c)(2)(A)); MFS = single (§63(c)(2)(C))
    sdj = {2025: 30000, 2026: 32200}[ty]
    rel(doc, 'sd_joint', '§63(c)(2)(A): joint standard deduction = 200% of the single amount', f'2 * pub_sd_single = {sdj}', 2 * p('sd_single') == sdj)
    # AMT: MFS exemption = 50% of joint (§55(d)(1)(C)); MFS 28% breakpoint = 1/2 (§55(b)(1)(B))
    exm, b28m = {2025: (68500, 119550), 2026: (70100, 122250)}[ty]
    rel(doc, 'amt_mfs', '§55(d)(1)(C), §55(b)(1)(B): MFS exemption and 28% breakpoint = 1/2 of the joint amounts',
        f'pub_amt_ex_mfj = 2 * {exm} ∧ pub_amt_28 = 2 * {b28m}', p('amt_ex_mfj') == 2 * exm and p('amt_28') == 2 * b28m)
    # AMT phaseout thresholds and completion
    po = {2025: (1252700, 626350, 626350, 1800700, 978750, 900350, 225300, 4),
          2026: (1000000, 500000, 500000, 1280400, 680200, 640200, 167600, 2)}[ty]
    exs = {2025: (137000, 88100, 68500, 30700), 2026: (140200, 90100, 70100, 31400)}[ty]
    k = po[7]
    mfj_thr = 'pub_amt_po_mfj' if ty == 2026 else str(po[0])
    rel(doc, 'amt_phaseout', f'§55(d)(2), §55(d)(4)(A)(ii): single and MFS thresholds = 50% of the joint threshold; complete phaseout = '
        f'threshold + exemption / {"25" if k == 4 else "50"}%',
        f'{po[0]} = 2 * {po[1]} ∧ {po[0]} = 2 * {po[2]} ∧ {po[0]} + {k} * pub_amt_ex_mfj = {po[3]} ∧ {po[1]} + {k} * pub_amt_ex_single = {po[4]}'
        f' ∧ {po[2]} + {k} * {exs[2]} = {po[5]} ∧ pub_amt_po_est + {k} * pub_amt_ex_est = {po[6]}',
        po[0] == 2 * po[1] == 2 * po[2] and po[0] + k * exs[0] == po[3] and po[1] + k * exs[1] == po[4] and po[2] + k * exs[2] == po[5]
        and p('amt_po_est') + k * exs[3] == po[6])
    if ty == 2025:
        rel(doc, 'amt_po_mfj_pub', 'Rev. Proc. joint AMT phaseout threshold equals the recomputed one', 'amt_po_mfj = 1252700', True)
    # §23/§137 completed phaseout = threshold + $40,000 (§23(b)(2)(A)(ii), not indexed)
    full = {2025: 299190, 2026: 305080}[ty]
    rel(doc, 'adopt_full', '§23(b)(2)(A)(ii), §137(b)(2)(A): phaseout completes $40,000 above the threshold',
        f'pub_adopt_phase + 40000 = {full} ∧ pub_adoptx_phase + 40000 = {full}', p('adopt_phase') + 40000 == full)
    # §135 completed phaseout: + $15,000 / $30,000
    sbj, sbo = {2025: (179250, 114500), 2026: (182650, 116800)}[ty]
    rel(doc, 'savbond_full', '§135(b)(2)(A): phaseout range $15,000 ($30,000 joint), not indexed',
        f'pub_savbond_joint + 30000 = {sbj} ∧ pub_savbond_other + 15000 = {sbo}', p('savbond_joint') + 30000 == sbj and p('savbond_other') + 15000 == sbo)
    # §221 completed phaseout
    slj, slo = {2025: (200000, 100000), 2026: (205000, 100000)}[ty]
    rel(doc, 'sli_full', '§221(b)(2)(B)(ii): phaseout range $15,000 ($30,000 joint), not indexed',
        f'pub_sli_joint + 30000 = {slj} ∧ pub_sli_other + 15000 = {slo}', p('sli_joint') + 30000 == slj and p('sli_other') + 15000 == slo)
    # §199A: joint threshold = 200% of the indexed $157,500; phase-in range $50,000/$100,000 (2025), $75,000/$150,000 (2026)
    tj, rng = {2025: (394600, 50000), 2026: (403500, 75000)}[ty]
    pin = {2025: (494600, 247300, 247300), 2026: (553500, 276775, 276750)}[ty]
    rel(doc, 'qbi_joint', '§199A(e)(2)(A): joint threshold = 200% of the (indexed) single threshold; §199A(b)(3)(B), (d)(3): phase-in range',
        f'2 * pub_qbi_thr = {tj} ∧ {tj} + {2 * rng} = {pin[0]} ∧ pub_qbi_thr_mfs + {rng} = {pin[1]} ∧ pub_qbi_thr + {rng} = {pin[2]}',
        2 * p('qbi_thr') == tj and tj + 2 * rng == pin[0] and p('qbi_thr_mfs') + rng == pin[1] and p('qbi_thr') + rng == pin[2])
    # §461(l): joint = 200%
    ebj = {2025: 626000, 2026: 512000}[ty]
    rel(doc, 'ebl_joint', '§461(l)(3)(A)(ii)(II): joint amount = 200%', f'2 * pub_ebl = {ebj}', 2 * p('ebl') == ebj)
    # §125 carryover (Notice 2020-33: 20% of the salary-reduction limit) -- administrative, not statutory
    co = {2025: 660, 2026: 680}[ty]
    rel(doc, 'fsa_carryover', 'Notice 2020-33 (administrative): carryover = 20% of the §125(i) limit', f'pub_fsa / 5 = {co} ∧ pub_fsa % 5 = 0', p('fsa') == 5 * co)
    # §2523(i)(2) and §2801(c) follow §2503(b)
    # §32: maximum credit = credit percentage x earned income amount (IRS rounds to the dollar);
    #      completed phaseout = threshold + max credit / phaseout percentage (IRS: from the rounded max credit)
    eic = {2025: dict(mx=(4328, 7152, 8046, 649), cj=(57554, 64430, 68675, 26214), co=(50434, 57310, 61555, 19104)),
           2026: dict(mx=(4427, 7316, 8231, 664), cj=(58863, 65899, 70244, 26820), co=(51593, 58629, 62974, 19540))}[ty]
    ei = (p('eic_ei1'), p('eic_ei2'), p('eic_ei2'), p('eic_ei0'))
    cr = (3400, 4000, 4500, 765); pr = (1598, 2106, 2106, 765)   # basis points, §32(b)(1)
    thr = (p('eic_ph'), p('eic_ph'), p('eic_ph'), p('eic_ph0')); thrj = (p('eic_phj'), p('eic_phj'), p('eic_phj'), p('eic_phj0'))
    mx_ok = all((c * e * 2 + 10000) // 20000 == m for c, e, m in zip(cr, ei, eic['mx']))
    rel(doc, 'eic_maxcredit', '§32(b)(1): maximum credit = credit percentage x earned income amount, rounded to the dollar',
        ' ∧ '.join(f'roundNear ({c} * {e}) 10000 1 = {m}' for c, e, m in zip(cr, ['pub_eic_ei1', 'pub_eic_ei2', 'pub_eic_ei2', 'pub_eic_ei0'], eic['mx'])), mx_ok)
    co_ok = all(t + (m * 10000 * 2 + r) // (2 * r) == c for t, m, r, c in zip(thr, eic['mx'], pr, eic['co'])) and \
            all(t + (m * 10000 * 2 + r) // (2 * r) == c for t, m, r, c in zip(thrj, eic['mx'], pr, eic['cj']))
    rel(doc, 'eic_completed', '§32(b): completed phaseout = threshold + (rounded) maximum credit / phaseout percentage, rounded to the dollar '
        '(the IRS method; the exact statutory zero point uses the unrounded credit)',
        ' ∧ '.join(f'{t} + roundNear ({m} * 10000) {r} 1 = {c}' for t, m, r, c in
                   list(zip(['pub_eic_ph'] * 3 + ['pub_eic_ph0'], eic['mx'], pr, eic['co'])) + list(zip(['pub_eic_phj'] * 3 + ['pub_eic_phj0'], eic['mx'], pr, eic['cj']))), co_ok)

# superfund: published total = indexed Hazardous Substance Superfund rate + 9-cent Oil Spill Liability rate (§4611(c)(2))
for doc, tot in ((A, 26), (B, 27)):
    D(doc, 'superfund_total', '§4611(c)(2): published rate = indexed superfund rate (rounded down to a cent) + 9-cent oil spill rate',
      f'superfund / 10 + 9 = {tot}', True)
# §42(h)(3)(I) for 2026: (H)-adjusted amounts x 1.12
D(B, 'lihtc_112', '§42(h)(3)(I): 2026 state housing credit ceiling amounts = (H)-adjusted amounts x 1.12 (per capita in tenths of a cent)',
  'lihtc_percap_H * 112 / 10 = 3416 ∧ lihtc_floor_H * 112 / 100 = 3953600', True)
# §2523(i)(2), §2801(c) and §529A track §2503(b)
D(A, 'gift_spouse_tracks', '§2523(i)(2): the $100,000 is indexed by §2503(b)(2) with the same $1,000 rounding', 'gift_spouse = pub_gift_spouse', True)
D(B, 'covered_gift_tracks', '§2801(c) uses the §2503(b) amount', 'pub_covered_gift = pub_gift_annual', True)

# item 6: the MFS maximum 15-percent rate amount in the older Rev. Procs.
from spec_old import OLD, OLD_MFS15
for ty, o in OLD.items():
    f = o['cg']['f_mfj']; m = OLD_MFS15[ty]
    D(o['doc'], 'cg_15_mfs_half', '§1(j)(5)(B)(ii)(I): published MFS maximum 15-percent rate amount vs 1/2 of the published joint amount',
      f'pub_cg_f_mfj = 2 * {m} + {f - 2 * m}', f == 2 * m)
