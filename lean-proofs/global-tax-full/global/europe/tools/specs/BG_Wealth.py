S = {'cc': 'BG', 'fam': 'Wealth', 'families': [], 'doc': "# BG 2025: Wealth family not reached (grade C)\n\n* 4300 Inheritance and gift tax (ЗМДТ чл. 36-37 (данък върху наследствата, 0,4-6,6 %), чл. 44 (дарения)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)\n* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)\n", 'notes': [], 'unsupported': [('!g.transfers.isEmpty || !g.assets.isEmpty', '4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)'), ('!g.transfers.isEmpty || !g.assets.isEmpty', '4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)')], 'guards': [], 'taxes': [{'oecd': '4300', 'tax': 'Inheritance and gift tax', 'statute': 'ЗМДТ чл. 36-37 (данък върху наследствата, 0,4-6,6 %), чл. 44 (дарения)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)"]}, {'oecd': '4200', 'tax': 'Net wealth tax', 'statute': 'none recorded', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)"]}]}

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
p6_finish(S)

# ---- pass 14 (R1 Europe, 2026-11-21): P6, withholding notes, vehicles (tools/p14_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
p14_rows(S)
p6_finish(S)
