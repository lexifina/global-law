S = {'cc': 'SE', 'fam': 'Wealth', 'families': [], 'doc': "# SE 2025: Wealth family not reached (grade C)\n\n* 4300 Inheritance and gift tax (arvsskatt abolished 2005 (not cited)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)\n* 4200 Net wealth tax (förmögenhetsskatt abolished 2007 (not cited)): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)\n", 'notes': [], 'unsupported': [('!g.transfers.isEmpty || !g.assets.isEmpty', '4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)'), ('!g.transfers.isEmpty || !g.assets.isEmpty', '4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)')], 'guards': [], 'taxes': [{'oecd': '4300', 'tax': 'Inheritance and gift tax', 'statute': 'arvsskatt abolished 2005 (not cited)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)"]}, {'oecd': '4200', 'tax': 'Net wealth tax', 'statute': 'förmögenhetsskatt abolished 2007 (not cited)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)"]}]}

# ---- pass 2 (R1 Europe, 2026-11-21): cited absences ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/absent_p2.py")).read())
cite_absent(S, "4200", "wealth", "Statlig förmögenhetsskatt (not levied)", "Lag (1997:323) om statlig förmögenhetsskatt",
  "the act's record at Regeringskansliet/Lagrummet (data.riksdagen.se sfs-1997-323) reads \"Upphävd: 2008-01-01\": no net wealth tax in 2025",
  "data.riksdagen.se record (se/law/sfs-1997-323.html)")
cite_absent(S, "4300", "estate", "Arvsskatt och gåvoskatt (not levied)", "Lag (1941:416) om arvsskatt och gåvoskatt",
  "the act's record at Regeringskansliet/Lagrummet (data.riksdagen.se sfs-1941-416) reads \"Upphävd: 2005-01-01\": no inheritance or gift tax in 2025",
  "data.riksdagen.se record (se/law/sfs-1941-416.html)")

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
