S = {'cc': 'EE', 'fam': 'Property', 'families': [], 'doc': "# EE 2025: Property family not reached (grade C)\n\n* 4400 Real-estate transfer and stamp duties (riigilõiv (notary and land register fees)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)\n* 4100 Recurrent property tax (Maamaksuseadus (Tallinn)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)\n", 'notes': [], 'unsupported': [('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)'), ('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)')], 'guards': [], 'taxes': [{'oecd': '4400', 'tax': 'Real-estate transfer and stamp duties', 'statute': 'riigilõiv (notary and land register fees)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act's 2025 rate articles (and the reference region's rate where regional)"]}, {'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'Maamaksuseadus (Tallinn)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act and the reference municipality's 2025 rate (registry choice)"]}]}

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
p6_finish(S)

# ---- pass 7 (R1 Europe, 2026-11-21): P5/P6 gaps, carry-overs (tools/p6lib.py helpers, tools/p7_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p7_rows.py")).read())
p7_rows(S)
p6_finish(S)

# ---- pass 16 (R1 Europe, 2026-11-21): year-in-force audit (tools/p16_rows.py, tools/yif16_rows.json) ----
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
p16_rows(S)
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

# ---- local-tax framework pass (R1 Europe, 2026-11-22): LocalTax with the rate as input (tools/plfw_rows.py, tools/lfw_rows.json) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/plfw_rows.py")).read())
plfw_rows(S)
p6_finish(S)
