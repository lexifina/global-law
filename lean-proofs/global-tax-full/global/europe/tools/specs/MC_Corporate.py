S = {'cc': 'MC', 'fam': 'Corporate', 'families': [], 'doc': '# MC 2025: Corporate family not reached (grade C)\n\n* 1200 Corporate income tax (Impôt sur les bénéfices (Ordonnance souveraine n° 3.152 du 19 mars 1964), 25 %): tried legimonaco.mc not captured; would unlock: the ISB ordinance in force 2025\n* 1200 Withholding on payments abroad (statutory withholding on dividends, interest, royalties): tried legimonaco.mc not captured; would unlock: the ISB ordinance in force 2025\n', 'notes': [], 'unsupported': [('g.entity == .company', '1200 Corporate income tax: not modelled (grade C: legimonaco.mc not captured)'), ('g.entity == .company', '1200 Withholding on payments abroad: not modelled (grade C: legimonaco.mc not captured)')], 'guards': [], 'taxes': [{'oecd': '1200', 'tax': 'Corporate income tax', 'statute': 'Impôt sur les bénéfices (Ordonnance souveraine n° 3.152 du 19 mars 1964), 25 %', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'legimonaco.mc not captured', 'unsupported': ['would unlock: the ISB ordinance in force 2025']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'legimonaco.mc not captured', 'unsupported': ['would unlock: the ISB ordinance in force 2025']}]}

# ---- pass 9 (R1 Europe, 2026-11-21): remaining withholding, carry-overs, B -> A, P5/P6 (tools/p9_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
p9_rows(S)
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
