S = {'cc': 'CH', 'fam': 'Property', 'families': [], 'doc': "# CH 2025: Property family not reached (grade C)\n\n* 4400 Real-estate transfer and stamp duties (kantonale Handänderungssteuer (Bern/Genf); Stempelabgaben StG Art. 13-16 (Umsatzabgabe)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)\n* 4100 Recurrent property tax (kantonale Liegenschaftssteuer): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)\n", 'notes': [], 'unsupported': [('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)'), ('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)')], 'guards': [], 'taxes': [{'oecd': '4400', 'tax': 'Real-estate transfer and stamp duties', 'statute': 'kantonale Handänderungssteuer (Bern/Genf); Stempelabgaben StG Art. 13-16 (Umsatzabgabe)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act's 2025 rate articles (and the reference region's rate where regional)"]}, {'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'kantonale Liegenschaftssteuer', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act and the reference municipality's 2025 rate (registry choice)"]}]}

# ---- pass 18 (R1 Europe, 2026-11-21): item-5 leftovers, audit, GR ENFIA, vehicles (tools/p18_rows.py) ----
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
p18_rows(S)
p6_finish(S)
