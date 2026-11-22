S = {'cc': 'FI', 'fam': 'Capital', 'families': [], 'doc': "# FI 2025: Capital family not reached (grade C)\n\n* 1100 Gains of individuals on shares and property (disposals) (Tuloverolaki 45-50 §): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)\n", 'notes': [], 'unsupported': [('g.entity == .household && !g.disposals.isEmpty', "1100 Gains of individuals on shares and property (disposals): not modelled (grade C: the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed))")], 'guards': [], 'taxes': [{'oecd': '1100', 'tax': 'Gains of individuals on shares and property (disposals)', 'statute': 'Tuloverolaki 45-50 §', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': "the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed)", 'unsupported': ["would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)"]}]}

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
p6_wht_rows(S)
p6_gain_rows(S)
p6_finish(S)
