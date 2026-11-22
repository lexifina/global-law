S = {'cc': 'SI', 'fam': 'Corporate', 'doc': '# SI 2025: Davek od dohodkov pravnih oseb (1200) and withholding on payments abroad\n\nSource: Zakon o obnovi, razvoju in zagotavljanju finančnih sredstev (ZORZFS), Uradni list RS 131/2023, uradni-list.si (official) as captured by the Internet Archive on 2025-04-11 (`si/law/zorzfs_ul131_2023_wb.html`); sha256 in `law/SHA256SUMS`.\n* 64. člen (1): "Ne glede na 60. člen ZDDPO-2 se davek plačuje po stopnji 22 odstotkov od davčne osnove za leta 2024, 2025, 2026, 2027 in 2028."\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Davek od dohodkov pravnih oseb",\n    sched := Schedule.flat 2200 }\n\ndef citStatute : String := "ZORZFS (Uradni list RS 131/2023) 64. člen (1): 22 % for 2024-2028, notwithstanding ZDDPO-2 60. člen"\n', 'families': [('1200 Davek od dohodkov pravnih oseb', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['SI 1200: ZORZFS as published 22.12.2023 (later amendments of 64. člen not checked)'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 22000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 220000'], 'taxes': [{'oecd': '1200', 'tax': 'Davek od dohodkov pravnih oseb', 'statute': 'ZORZFS (Uradni list RS 131/2023) 64. člen (1): 22 % for 2024-2028, notwithstanding ZDDPO-2 60. člen', 'dated': 'ZORZFS as published 22.12.2023 (later amendments of 64. člen not checked)', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['loss offset limit (63 % of the base, ZDDPO-2) and the investment and R&D reliefs not modelled']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'pisrs.si script-only', 'unsupported': ['would unlock: the ZDDPO-2 consolidated text']}]}

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
p6_wht_rows(S)
p6_finish(S)

# ---- pass 8 (R1 Europe, 2026-11-21): withholding under kernel 2.3.0, P5/P6 gaps, P7 surcharges, carry-overs (tools/p8_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
p8_rows(S)
p6_finish(S)

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
