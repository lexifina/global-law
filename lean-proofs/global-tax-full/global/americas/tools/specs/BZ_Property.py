S = {'cc': 'BZ', 'fam': 'Property', 'doc': '# BZ 2025: Property family — no dated statute text reached (grade C)\n\n* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.', 'families': '[]', 'taxes': [{'oecd': '4300', 'tax': 'Inheritance, gift and wealth taxes', 'statute': 'registry: none levied (not cited from a text)', 'grade': 'C', 'status': 'unsupported', 'package': 'P6', 'kernel_parts': [], 'tried': 'no statute read', 'unsupported': ['would unlock: a text showing the abolition or absence']}, {'oecd': '4200', 'tax': 'Net wealth tax', 'statute': 'Belize Tax Service (bts.gov.bz): list of taxes administered; consolidated laws index', 'dated': 'Wayback copy dated 2025; pass 13, 2026-11-21', 'grade': 'A', 'status': 'not levied', 'package': 'P6', 'kernel_parts': ['Absent'], 'why': "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Belize Tax Service (bts.gov.bz) list of the taxes it administers, `bz/law/bts_home_2025-01-25.*` (Wayback 2025-01-25), names: General Sales Tax, Business & Income Tax, Employee Income Tax, Contract Tax Withholding; consolidated index: lexifina/belize-law@43dfad3b11af `laws.csv` (`bz/law/lexifina_bz_laws_index.csv`: Revised Edition 2020 and Acts 2021-2026): the revenue Acts are Caps. 48 Customs and Excise Duties, 50 Departure Tax, 55 Income and Business Tax, 58 Land Tax, 60 Produce Export Duties, 63 General Sales Tax, 64 Stamp Duties, 64.01 Environmental Tax, 278.01 Cruise Ship Passenger Tax, and their amending Acts; none of them is a recurrent tax on net wealth."}], 'unsupported': [['true', 'Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed']], 'absent': [['wealth', "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Belize Tax Service (bts.gov.bz) list of the taxes it administers, `bz/law/bts_home_2025-01-25.*` (Wayback 2025-01-25), names: General Sales Tax, Business & Income Tax, Employee Income Tax, Contract Tax Withholding; consolidated index: lexifina/belize-law@43dfad3b11af `laws.csv` (`bz/law/lexifina_bz_laws_index.csv`: Revised Edition 2020 and Acts 2021-2026): the revenue Acts are Caps. 48 Customs and Excise Duties, 50 Departure Tax, 55 Income and Business Tax, 58 Land Tax, 60 Produce Export Duties, 63 General Sales Tax, 64 Stamp Duties, 64.01 Environmental Tax, 278.01 Cruise Ship Passenger Tax, and their amending Acts; none of them is a recurrent tax on net wealth."]]}

# ---- gap pass 2 (2026-11-22): 4300 not levied (OECD Revenue Statistics, Guide §52) ----
_why43 = 'Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Belize (DSD_REV_LAC@DF_REVBLZ v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/BLZ.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published.'
for _t in S['taxes']:
    if str(_t.get('oecd')) == '4300' and _t.get('grade') == 'C':
        _t.update(status='not levied', grade='B', kernel_parts=['Absent'], why=_why43,
                  statute='none: no estate, inheritance or gift tax (OECD Revenue Statistics table, heading 4300 = 0 in 2021-2024)',
                  dated='OECD Revenue Statistics detailed table for Belize (DSD_REV_LAC@DF_REVBLZ v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/BLZ.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line' + '; 2025 not yet published',
                  evidence=['OECD Revenue Statistics detailed table for Belize (DSD_REV_LAC@DF_REVBLZ v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/BLZ.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line'], gap_pass2='2026-11-22 approach 2 (OECD Revenue Statistics: absence, grade B)')
        _t.pop('tried', None); _t.pop('unsupported', None)
        break
else:
    raise SystemExit('BZ: no C 4300 row')
S.setdefault('absent', []).append(['estate', _why43])
_u43 = 'Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed'
if 'unsupported_expr' in S:
    _f1 = '(if true then ["' + _u43 + '"] else []) ++ '; _f2 = '["' + _u43 + '"] ++ '
    _ue = S['unsupported_expr']; assert _f1 in _ue or _f2 in _ue
    S['unsupported_expr'] = _ue.replace(_f1, '', 1) if _f1 in _ue else _ue.replace(_f2, '', 1)
else:
    _n = len(S['unsupported']); S['unsupported'] = [u for u in S['unsupported'] if u[1] != _u43]
    assert len(S['unsupported']) == _n - 1
S['doc'] += "\n\n**4300 (gap pass 2, 2026-11-22)**: not levied (grade B): " + _why43


# ---- gap pass 2 (2026-11-22): 5200 motor vehicle licence duties (Cap. 230 s. 20; Fees and Duties Order) ----
S.setdefault('imports', [])
if 'TaxKernel.Global2' not in S['imports']: S['imports'].append('TaxKernel.Global2')
S['lean'] = (S.get('lean') or '') + '''
/-! ## 5200 motor vehicle licence duties (gap pass 2, 2026-11-22; kernel `VehicleTax`) -/
/-- Motor Vehicles and Road Traffic (Fees and Duties) Order (Cap. 230, S.I. 182 of 2003 as amended by 41 of 2013; Sub. Leg.
R.E. 2020) para. 2 (xix): motor vehicles other than those of (i)-(xviii) (motor cycles, taxis, omnibuses, goods vehicles,
hearses, trailers, tractors): not exceeding 3,000 lbs. tare $135; 3,000-5,000 lbs. $200; 5,000-10,000 lbs. $275; above
10,000 lbs. $325 a year. Tare in kg: 3,000 lb = 1,360.78 kg, 5,000 lb = 2,267.96 kg, 10,000 lb = 4,535.92 kg (whole kg at
or below the limit). -/
def bzLicence : VehicleTax :=
  { name := "Motor vehicle licence duty", kinds := ["car", "stationWagon", "van", "pickup", "pickupSingleCab"],
    parts := [(.massKg, QtyTable.ofCeilings [(1360, 135), (2267, 200), (4535, 275)] 325)], level := .central,
    statute := "Motor Vehicles and Road Traffic Act Cap. 230 s. 20 (1), (2), (4); Motor Vehicles and Road Traffic (Fees and Duties) Order para. 2 (xix) (a)-(d): $135 / $200 / $275 / $325 by tare (3,000 / 5,000 / 10,000 lbs.)" }

/-- The same Order para. 2 (i): motor cycles and tricycles $75 a year. -/
def bzLicenceMc : VehicleTax :=
  { name := "Motor vehicle licence duty", kinds := ["motorcycle"], fixed := 75, level := .central,
    statute := "Motor Vehicles and Road Traffic (Fees and Duties) Order para. 2 (i): motor cycles and tricycles $75" }

def bzVehF : Family := vehicleTaxFamily "Motor vehicle licence duty" [bzLicence, bzLicenceMc]
'''
S['families'] = '[bzVehF]' if S['families'].strip() == '[]' else S['families'].rstrip(']') + ', bzVehF]'
_bzu = ("Motor vehicle licence duty: private cars, station wagons, vans and pick-ups read as para. (xix) vehicles (a pick-up or van "
        "licensed as a goods vehicle pays para. (ix)-(xi) instead); the half rate of registered cane farmers (paras. (xii), (xx)) "
        "and the 3/6/9-month licences of s. 20 (4) (months held stand for the licence period) not modelled")
_bzue = ('(if !g.vehicles.isEmpty then [' + repr(_bzu).replace("'", '"') + '] else [])'
         ' ++ vehicleTaxUnknown "Motor vehicle licence duty" [bzLicence, bzLicenceMc] g'
         ' ++ vehicleTaxUnmatched "Motor vehicle licence duty" [bzLicence, bzLicenceMc] g')
assert not S.get('unsupported'), 'BZ_Property: plain unsupported entries would be lost'
S.pop('unsupported', None)
S['unsupported_expr'] = _bzue
S['guards'] = S.get('guards', []) + [
    '-- 1,200 kg tare = 2,645.5 lbs: not exceeding 3,000 lbs. -> $135',
    'bzLicence.amount 2025 { massKg := 1200 } == 135',
    '-- 1,361 kg = 3,000.5 lbs: above 3,000 lbs. -> $200; 2,267 kg = 4,997.8 lbs -> $200',
    'bzLicence.amount 2025 { massKg := 1361 } == 200', 'bzLicence.amount 2025 { massKg := 2267 } == 200',
    '-- 3,000 kg = 6,613.9 lbs -> $275; 5,000 kg = 11,023 lbs -> $325',
    'bzLicence.amount 2025 { massKg := 3000 } == 275', 'bzLicence.amount 2025 { massKg := 5000 } == 325',
    '-- motor cycle: $75',
    'bzLicenceMc.amount 2025 { kind := "motorcycle" } == 75']
S['taxes'] = [t for t in S['taxes']] + [dict(oecd="5200", tax="Motor vehicle licence duty",
    statute="Motor Vehicles and Road Traffic Act Cap. 230 s. 20 (licence duties prescribed by Order); Motor Vehicles and Road Traffic (Fees and Duties) Order (S.I. 182 of 2003, 41 of 2013) para. 2 (i), (xix)",
    dated="lexifina/belize-law cap/230/20.md and sub/230/8 (Revised Edition 2020, as at 31 December 2020; official source Laws of Belize, agm.gov.bz/laws); no amending Order under s. 20 (2) among the repository's statutory instruments of 2021-2026 (the S.I.s under Cap. 230 of 2023-2026 are regulations under s. 112: electronic devices, seat belts, speed devices, fares); 235 scanned S.I.s of 2020-2026 are not in the repository (data/si-not-built.csv)",
    grade="A", status="modelled", package="P7", kernel_parts=["VehicleTax", "vehicleTaxFamily"],
    unsupported=["goods-vehicle, taxi, omnibus, trailer and tractor rates (paras. (iii)-(xviii))", "cane farmers' half rate", "3/6/9-month licences (s. 20 (4))"],
    gap_pass2="2026-11-22 approach 1 (lexifina law repository) + 5200 vehicles (Interpretative Guide §12, §14: vehicle licences are taxes)")]
S['doc'] += ("\n\n**5200 (gap pass 2, 2026-11-22)**: motor vehicle licence duty, Cap. 230 s. 20 and the Motor Vehicles and Road "
             "Traffic (Fees and Duties) Order para. 2: (xix) other motor vehicles $135 (tare not exceeding 3,000 lbs.), $200 "
             "(to 5,000), $275 (to 10,000), $325 (above); (i) motor cycles $75 (kernel `VehicleTax` on `massKg`). Read in "
             "lexifina/belize-law (R.E. 2020); the MAP's evidence line (s. 96) was off-target.")
