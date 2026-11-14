"""T7: independent arithmetic, written from the statute text (not from the Lean).

Facts: asset basis 500,000, value 1,500,000 (long-term gain 1,000,000). Top-bracket individual.
Rates read from the Code: s.1(h)(1)(D) 20%; s.1411(a)(1) 3.8% (not for nonresident aliens, s.1411(e)(1));
s.2801(a)(1) = highest s.2001(c) rate = 40%; s.2503(b) amount 19,000 (2025); s.877A(a)(3) 600,000 indexed = 890,000
for 2025 (Form 8854 instructions 2025; 866,000 for 2024; 910,000 for 2026 as reported by practitioner pages).
"""
from fractions import Fraction as F

BASIS, VALUE = 500_000, 1_500_000
GAIN = VALUE - BASIS
LTCG, NIIT, TOP_TRANSFER, ORD = F(20, 100), F(38, 1000), F(40, 100), F(35, 100)
ANNUAL = 19_000


def resident_sale(gain):
    # s.1(h) + s.1411: citizen or resident
    return gain * (LTCG + NIIT)


def exit_tax(gain, exclusion):
    # s.877A(a)(1): all property treated as sold the day before the expatriation date (still a resident that day)
    # s.877A(a)(3): amount includible reduced, not below zero, by the exclusion
    taxed = max(gain - exclusion, 0)
    # s.877A(a)(2) flush: later gain adjusted for gain taken into account "determined without regard to paragraph (3)"
    new_basis = BASIS + gain
    return taxed * (LTCG + NIIT), new_basis


def nra_realty_sale(gain):
    # s.897(a)(1): effectively connected; s.1(h) rate; s.1411(e)(1): no NIIT
    return gain * LTCG


out = {}
out['baseline_resident_sells'] = resident_sale(GAIN)
t, nb = exit_tax(GAIN, 890_000)
later = resident_sale(max(VALUE - nb, 0))
out['plan1_exit_tax'] = t
out['plan1_basis_after'] = nb
out['plan1_later_sale_tax'] = later
out['plan1_total'] = t + later
out['plan1_saving'] = out['baseline_resident_sells'] - out['plan1_total']
out['plan2_certified_leaver_realty'] = nra_realty_sale(GAIN)
out['plan2_uncertified_leaver_realty'] = t + nra_realty_sale(max(VALUE - nb, 0))
out['plan2_saving'] = out['plan2_certified_leaver_realty'] - out['plan2_uncertified_leaver_realty']
# exclusion of the neighbouring years
out['plan1_total_if_2024_exclusion_866000'] = exit_tax(GAIN, 866_000)[0]
out['plan1_total_if_2026_exclusion_910000'] = exit_tax(GAIN, 910_000)[0]
# s.2801(a), (c): US recipient of a gift or bequest from a covered expatriate pays 40% of the value above the
# s.2503(b) amount; switched off only while the expatriate is subject to estate/gift tax as a citizen or resident
# (s.877A(g)(1)(C); Reg. s.28.2801-2(h): domicile)
s2801 = (VALUE - ANNUAL) * TOP_TRANSFER
out['s2801_on_1_5m_to_one_US_person'] = s2801
out['plan1_restated_if_later_leaves_and_gives_to_US_person'] = out['plan1_total'] + s2801
out['plan1_net_vs_baseline_with_2801'] = out['baseline_resident_sells'] - out['plan1_restated_if_later_leaves_and_gives_to_US_person']
out['plan2_restated_with_2801'] = out['plan2_uncertified_leaver_realty'] + s2801
out['plan2_net_vs_certified_with_2801'] = out['plan2_certified_leaver_realty'] - out['plan2_restated_with_2801']
out['plan1_breakeven_covered_transfers_above_annual'] = out['plan1_saving'] / TOP_TRANSFER
out['plan2_breakeven_covered_transfers_above_annual'] = out['plan2_saving'] / TOP_TRANSFER
# s.877A(e)(1): IRA etc. treated as distributed the day before (ordinary income, illustrative 35%)
out['ira_500k_deemed_distribution_tax'] = 500_000 * ORD
out['plan1_total_with_ira_500k'] = out['plan1_total'] + 500_000 * ORD
out['ira_balance_at_which_acceleration_equals_saving'] = out['plan1_saving'] / ORD
# cap on the benefit whatever the portfolio: exclusion x 23.8%
out['max_benefit_of_exclusion_2025'] = 890_000 * (LTCG + NIIT)

for k, v in out.items():
    print(f'{k}: {float(v):,.2f}')

claimed = {'baseline_resident_sells': 238_000, 'plan1_total': 26_180, 'plan2_certified_leaver_realty': 200_000,
           'plan2_uncertified_leaver_realty': 26_180}
ok = all(out[k] == v for k, v in claimed.items())
print('AGREE with the Lean figures' if ok else 'DISAGREE', {k: str(out[k]) for k in claimed})
