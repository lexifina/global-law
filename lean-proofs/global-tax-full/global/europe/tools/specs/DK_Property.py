S = {'cc': 'DK', 'fam': 'Property', 'families': [], 'doc': "# DK 2025: Property family not reached (grade C)\n\n* 4400 Real-estate transfer and stamp duties (Tinglysningsafgiftsloven (0,6 % + fixed fee)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)\n* 4100 Recurrent property tax (Ejendomsskatteloven (grundskyld, ejendomsværdiskat)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)\n", 'notes': [], 'unsupported': [('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)'), ('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)')], 'guards': [], 'taxes': [{'oecd': '4400', 'tax': 'Real-estate transfer and stamp duties', 'statute': 'Tinglysningsafgiftsloven (0,6 % + fixed fee)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act's 2025 rate articles (and the reference region's rate where regional)"]}, {'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'Ejendomsskatteloven (grundskyld, ejendomsværdiskat)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act and the reference municipality's 2025 rate (registry choice)"]}]}

# ---- pass 7 (R1 Europe, 2026-11-21): P5/P6 gaps, carry-overs (tools/p6lib.py helpers, tools/p7_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p7_rows.py")).read())
p7_rows(S)
p6_finish(S)

# ---- pass 12 (R1 Europe, 2026-11-21): vehicle taxes, carry-overs, P5/P6, withholding (tools/p12_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
p12_rows(S)
p6_finish(S)

# ---- pass 13 (R1 Europe, 2026-11-21): VAT, P6, P5, withholding, stacking, vehicles (tools/p13_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
p13_rows(S)
p6_finish(S)

# ---- pass 17 (R1 Europe, 2026-11-21): kernel 2.7.0 items, audit follow-ups (tools/p17_rows.py) ----
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
p17_rows(S)
p6_finish(S)
