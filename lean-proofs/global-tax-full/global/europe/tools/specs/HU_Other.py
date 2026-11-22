S = {'cc': 'HU', 'fam': 'Other', 'families': [], 'doc': "# HU 2025: Other family not reached (grade C)\n\n* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)\n* 6000 Other taxes recorded by the registry (Helyi iparűzési adó (local business tax on adjusted turnover, up to 2 %); KATA/KIVA small-business regimes; windfall/sector surtaxes (2022-2025)): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row\n", 'notes': [], 'unsupported': [('true', '5200 Taxes on use of goods (motor vehicle taxes): not modelled (grade C: not read in the P7 pass)'), ('true', "6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)")], 'guards': [], 'taxes': [{'oecd': '5200', 'tax': 'Taxes on use of goods (motor vehicle taxes)', 'statute': "the country's motor-vehicle tax act", 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P7 pass', 'unsupported': ['would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)']}, {'oecd': '6000', 'tax': 'Other taxes recorded by the registry', 'statute': 'Helyi iparűzési adó (local business tax on adjusted turnover, up to 2 %); KATA/KIVA small-business regimes; windfall/sector surtaxes (2022-2025)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': "the registry's row (background, not a read text); not modelled", 'unsupported': ['would unlock: the statutes named in the registry row']}]}

# ---- pass 7 (R1 Europe, 2026-11-21): P5/P6 gaps, carry-overs (tools/p6lib.py helpers, tools/p7_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p7_rows.py")).read())
p7_rows(S)
p6_finish(S)

# ---- pass 11 (R1 Europe, 2026-11-21): vehicle taxes, carry-overs, P5/P6, withholding (tools/p11_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
p11_rows(S)
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
