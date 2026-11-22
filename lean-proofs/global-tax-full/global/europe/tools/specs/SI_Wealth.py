S = {'cc': 'SI', 'fam': 'Wealth', 'families': [], 'doc': "# SI 2025: Wealth family not reached (grade C)\n\n* 4300 Inheritance and gift tax (Zakon o davku na dediščine in darila): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)\n* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)\n", 'notes': [], 'unsupported': [('!g.transfers.isEmpty || !g.assets.isEmpty', '4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)'), ('!g.transfers.isEmpty || !g.assets.isEmpty', '4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)')], 'guards': [], 'taxes': [{'oecd': '4300', 'tax': 'Inheritance and gift tax', 'statute': 'Zakon o davku na dediščine in darila', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)"]}, {'oecd': '4200', 'tax': 'Net wealth tax', 'statute': 'none recorded', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)"]}]}

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
