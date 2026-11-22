S = {'cc': 'MT', 'fam': 'Social', 'families': [], 'doc': "# MT 2025: Social family not reached (grade C)\n\n* 2200 Employer social contributions and payroll taxes (Social Security Act Cap. 318 (Class 1, employer 10 %)): tried not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts); would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)\n", 'notes': [], 'unsupported': [('(g.entity == .company && g.company.payroll > 0) || g.household.adults.any (fun a => 0 < a.wages)', '2200 Employer social contributions and payroll taxes: not modelled (grade C: not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts))')], 'guards': [], 'taxes': [{'oecd': '2200', 'tax': 'Employer social contributions and payroll taxes', 'statute': 'Social Security Act Cap. 318 (Class 1, employer 10 %)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts)', 'unsupported': ["would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)"]}]}

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
