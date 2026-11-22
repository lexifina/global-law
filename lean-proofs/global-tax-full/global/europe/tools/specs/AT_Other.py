S = {'cc': 'AT', 'fam': 'Other', 'families': [], 'doc': "# AT 2025: Other family not reached (grade C)\n\n* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)\n* 6000 Other taxes recorded by the registry (Kommunalsteuer and Dienstgeberbeitrag recorded under payroll; Stabilitätsabgabe (banks)): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row\n", 'notes': [], 'unsupported': [('true', '5200 Taxes on use of goods (motor vehicle taxes): not modelled (grade C: not read in the P7 pass)'), ('true', "6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)")], 'guards': [], 'taxes': [{'oecd': '5200', 'tax': 'Taxes on use of goods (motor vehicle taxes)', 'statute': "the country's motor-vehicle tax act", 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P7 pass', 'unsupported': ['would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)']}, {'oecd': '6000', 'tax': 'Other taxes recorded by the registry', 'statute': 'Kommunalsteuer and Dienstgeberbeitrag recorded under payroll; Stabilitätsabgabe (banks)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': "the registry's row (background, not a read text); not modelled", 'unsupported': ['would unlock: the statutes named in the registry row']}]}

# ---- pass 7 (R1 Europe, 2026-11-21): P5/P6 gaps, carry-overs (tools/p6lib.py helpers, tools/p7_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p7_rows.py")).read())
p7_rows(S)
p6_finish(S)

# ---- pass 10 (R1 Europe, 2026-11-21): vehicle taxes, conditional withholding, remaining withholding (tools/p10_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
p10_rows(S)
p6_finish(S)

# ---- FT review, sixth pass (FT reviewer 6, 2026-11-21): electric cars owe motorbezogene Versicherungssteuer only from 1 April 2025 ----
# VersStG § 12 (1) Z 35 (at/law/versstg_2025-07-01.txt l. 669-674): § 4 (3), § 5 and § 6 as worded by BGBl. I Nr. 7/2025
# "treten mit Ablauf des 31. März 2025 in Kraft" and apply to insurance periods after 31 March 2025. Fassung vom 31.03.2025
# (ftreview/rv6/fetch/at/versstg_2025-03-31.html, RIS): § 4 (3) Z 6 exempts "Kraftfahrzeuge, die auf Grund ihres Antriebes
# (insbesondere Elektro oder Wasserstoff) einen CO2-Emissionswert von 0 g/km aufweisen"; the combustion-car rates (lit. b:
# 0,62 / 0,66 / 0,75 EUR per kW less 24, min 6,20; post-2020: 0,72 EUR per kW and per g less the yearly deductions) are the
# same in both Fassungen. So the § 6 (1) Z 2 lit. a EV amount is due for 9 of the 12 months of 2025.
_k = 'multiplierBp := 100, statute := "VersStG 1953 § 6 (1) Z 2 lit. a: rein elektrischer Antrieb, kW and own weight"'
assert _k in S["lean"], "FT6: EV rule not found"
S["lean"] = S["lean"].replace(_k, 'multiplierBp := 75, statute := "VersStG 1953 § 6 (1) Z 2 lit. a: rein elektrischer Antrieb, kW and own weight; due from 1 April 2025 only (§ 12 (1) Z 35, BGBl. I Nr. 7/2025; before, § 4 (3) Z 6 exempt): 9/12 of the year"')
S["guards"] += ['((p10atVeh.filter (·.computes 2025 { kind := "car", engineKw := 80, massKg := 2100, fuel := .electric, firstRegYear := 2023 })).head!).amount 2025 { kind := "car", engineKw := 80, massKg := 2100, fuel := .electric, firstRegYear := 2023 } == 335']
S["unsupported"] += [("g.vehicles.any (fun v => v.fuel == .electric)", "5200 motorbezogene Versicherungssteuer: an electric car is taxed from 1 April 2025 only (VersStG § 12 (1) Z 35; exempt before under § 4 (3) Z 6): 9/12 of the annual § 6 (1) Z 2 lit. a amount")]
S["doc"] += "\n* FT review (sixth pass): electric cars owe the motorbezogene Versicherungssteuer from 1 April 2025 only (BGBl. I Nr. 7/2025, § 12 (1) Z 35); 9/12 of the annual amount for 2025.\n"
p6_finish(S)

# ---- pass 15 (R1 Europe, 2026-11-21): publication requests, ENFIA, vehicles, transfers, withholding notes (tools/p15_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
p15_rows(S)
p6_finish(S)

# ---- gap pass (R1 Europe, 2026-11-21): gap-closing pass (tools/pgap_rows.py, tools/gap_rows.json) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p16_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p17_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p18_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/pgap_rows.py")).read())
pgap_rows(S)
p6_finish(S)
