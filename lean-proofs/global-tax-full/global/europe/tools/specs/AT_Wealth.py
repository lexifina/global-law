S = {'cc': 'AT', 'fam': 'Wealth', 'families': [], 'doc': "# AT 2025: Wealth family not reached (grade C)\n\n* 4300 Inheritance and gift tax (ErbStG 1955 not applied after 31.7.2008 (VfGH G 54/06): absence not cited from a text): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)\n* 4200 Net wealth tax (Vermögensteuer abolished 1994: absence not cited): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)\n", 'notes': [], 'unsupported': [('!g.transfers.isEmpty || !g.assets.isEmpty', '4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)'), ('!g.transfers.isEmpty || !g.assets.isEmpty', '4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)')], 'guards': [], 'taxes': [{'oecd': '4300', 'tax': 'Inheritance and gift tax', 'statute': 'ErbStG 1955 not applied after 31.7.2008 (VfGH G 54/06): absence not cited from a text', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)"]}, {'oecd': '4200', 'tax': 'Net wealth tax', 'statute': 'Vermögensteuer abolished 1994: absence not cited', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P6 pass', 'unsupported': ["would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)"]}]}

# ---- pass 2 (R1 Europe, 2026-11-21): cited absence ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/absent_p2.py")).read())
cite_absent(S, "4300", "estate", "Erbschafts- und Schenkungssteuer (not levied)", "Erbschafts- und Schenkungssteuergesetz 1955 § 1 (1) Z 1-3, § 34 (1) Z 13 (RIS, Fassung vom 01.07.2025)",
  "§ 1 (1) Z 1 (Erwerb von Todes wegen) \"aufgehoben durch VfGH, BGBl. I Nr. 9/2007\", Z 2 (Schenkungen) \"aufgehoben durch VfGH, BGBl. I Nr. 39/2007\"; for Z 3 \"Abgaben nach diesem Bundesgesetz werden ... für die die Steuerschuld nach dem 31. Juli 2008 entsteht, nicht mehr erhoben (vgl. § 34 Abs. 1 Z 13)\"",
  "RIS Fassung vom 01.07.2025 (at/law/erbstg1955_2025-07-01.html)")

# ---- pass 3 (R1 Europe, 2026-11-21): cited absence (net wealth tax) ----
cite_absent(S, "4200", "wealth", "Vermögensteuer (not levied)", "Steuerreformgesetz 1993, BGBl. Nr. 818/1993, Art. XII (Vermögensteuergesetz 1954 § 25 a)",
  "\"Außerkrafttreten § 25 a. Dieses Gesetz ist auf Sachverhalte nicht mehr anzuwenden, die nach dem 31. Dezember 1993 liegen.\" (BGBl. ausgegeben am 30. November 1993, 300. Stück)",
  "RIS BgblPdf 1993_818_0 (at/law/bgbl1993_818_strefg.pdf)")

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
