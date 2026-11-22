S = {'cc': 'SM', 'fam': 'Corporate', 'families': [], 'doc': "# SM 2025: Corporate family not reached (grade C)\n\n* 1200 Corporate income tax (Legge 16 dicembre 2013 n. 166 (IGR) art. 81 (17 %)): tried not fetched; Global law (the registry's source) not used (coordinator, 2026-11-21); would unlock: the IGR text with its 2025 wording\n* 1200 Withholding on payments abroad (statutory withholding on dividends, interest, royalties): tried not fetched; Global law (the registry's source) not used (coordinator, 2026-11-21); would unlock: the IGR text with its 2025 wording\n", 'notes': [], 'unsupported': [('g.entity == .company', "1200 Corporate income tax: not modelled (grade C: not fetched; Global law (the registry's source) not used (coordinator, 2026-11-21))"), ('g.entity == .company', "1200 Withholding on payments abroad: not modelled (grade C: not fetched; Global law (the registry's source) not used (coordinator, 2026-11-21))")], 'guards': [], 'taxes': [{'oecd': '1200', 'tax': 'Corporate income tax', 'statute': 'Legge 16 dicembre 2013 n. 166 (IGR) art. 81 (17 %)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': "not fetched; Global law (the registry's source) not used (coordinator, 2026-11-21)", 'unsupported': ['would unlock: the IGR text with its 2025 wording']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': "not fetched; Global law (the registry's source) not used (coordinator, 2026-11-21)", 'unsupported': ['would unlock: the IGR text with its 2025 wording']}]}

# ---- pass 9 (R1 Europe, 2026-11-21): remaining withholding, carry-overs, B -> A, P5/P6 (tools/p9_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
p9_rows(S)
p6_finish(S)

# ---- pass 10 (R1 Europe, 2026-11-21): vehicle taxes, conditional withholding, remaining withholding (tools/p10_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
p10_rows(S)
p6_finish(S)

# ---- pass 12 (R1 Europe, 2026-11-21): vehicle taxes, carry-overs, P5/P6, withholding (tools/p12_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
p12_rows(S)
p6_finish(S)

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
