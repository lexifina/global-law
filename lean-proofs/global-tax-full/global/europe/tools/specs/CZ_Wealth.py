S = {'cc': 'CZ', 'fam': 'Wealth', 'families': [], 'doc': "# CZ 2025: Wealth family not reached (grade C)\n\n* 4300 Inheritance and gift tax (inheritance and gifts in the income tax (ZDP § 4a, § 10); inheritance tax abolished 2014: not cited): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)\n* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)\n", 'notes': [], 'unsupported': [('!g.transfers.isEmpty || !g.assets.isEmpty', '4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)'), ('!g.transfers.isEmpty || !g.assets.isEmpty', '4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)')], 'guards': [], 'taxes': [{'oecd': '4300', 'tax': 'Inheritance and gift tax', 'statute': 'inheritance and gifts in the income tax (ZDP § 4a, § 10); inheritance tax abolished 2014: not cited', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)"]}, {'oecd': '4200', 'tax': 'Net wealth tax', 'statute': 'none recorded', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)"]}]}

# ---- pass 3 (R1 Europe, 2026-11-21): cited absence (inheritance and gift tax) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/absent_p2.py")).read())
cite_absent(S, "4300", "estate", "Daň dědická a daň darovací (not levied)", "zákonné opatření Senátu č. 340/2013 Sb. § 58 bod 1, § 59",
  "\"§ 58 Zrušovací ustanovení Zrušuje se: 1. Zákon č. 357/1992 Sb., o dani dědické, dani darovací a dani z převodu nemovitostí.\"; \"§ 59 Toto zákonné opatření Senátu nabývá účinnosti dnem 1. ledna 2014.\" (gifts have since been taxed as income under zákon č. 586/1992 Sb., not as a 4300 tax)",
  "zakonyprolidi.cz/cs/2013-340, fetched 2026-11-21 (cz/law/zo340_2013.html; Účinnost od 01.01.2014)")

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
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
