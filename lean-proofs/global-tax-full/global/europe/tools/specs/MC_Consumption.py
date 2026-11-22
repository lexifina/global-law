S = {'cc': 'MC', 'fam': 'Consumption', 'families': [], 'doc': "# MC 2025: Consumption family not reached (grade C)\n\n* 5111 VAT (Code des taxes (TVA, art. A. 1 ff.)): tried legimonaco.mc not captured by the Internet Archive; would unlock: the Code des taxes text in force 2025 (legimonaco.mc)\n* 5121 Excise duties (French excise regime applied by convention (CIBS, Légifrance blocked)): tried not reached in the P1 pass; would unlock: the excise act's 2025 rate articles\n", 'notes': [], 'unsupported': [('!g.consumption.isEmpty || g.entity == .company', '5111 VAT: not modelled (grade C: legimonaco.mc not captured by the Internet Archive)'), ('!g.consumption.isEmpty || g.entity == .company', '5121 Excise duties: not modelled (grade C: not reached in the P1 pass)')], 'guards': [], 'taxes': [{'oecd': '5111', 'tax': 'VAT', 'statute': 'Code des taxes (TVA, art. A. 1 ff.)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'legimonaco.mc not captured by the Internet Archive', 'unsupported': ['would unlock: the Code des taxes text in force 2025 (legimonaco.mc)']}, {'oecd': '5121', 'tax': 'Excise duties', 'statute': 'French excise regime applied by convention (CIBS, Légifrance blocked)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not reached in the P1 pass', 'unsupported': ["would unlock: the excise act's 2025 rate articles"]}]}

# ---- pass 9 (R1 Europe, 2026-11-21): remaining withholding, carry-overs, B -> A, P5/P6 (tools/p9_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
p9_rows(S)
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
