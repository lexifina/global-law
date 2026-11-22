S = {'cc': 'BG', 'fam': 'Corporate', 'doc': '# BG 2025: Корпоративен данък (1200) and withholding on payments abroad\n\nSource: Закон за корпоративното подоходно облагане, lex.bg (private publisher of the consolidated text with the amendment notes), `bg/law/zkpo.html`; sha256 in `law/SHA256SUMS`.\n* чл. 20: "Данъчната ставка на корпоративния данък е 10 на сто."\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Корпоративен данък",\n    sched := Schedule.flat 1000 }\n\ndef citStatute : String := "Закон за корпоративното подоходно облагане чл. 20 (10 на сто)"\n', 'families': [('1200 Корпоративен данък', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['BG 1200: lex.bg current text (2026-11); чл. 20 has no amendment note'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 10000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 100000'], 'taxes': [{'oecd': '1200', 'tax': 'Корпоративен данък', 'statute': 'Закон за корпоративното подоходно облагане чл. 20 (10 на сто)', 'dated': 'lex.bg current text (2026-11); чл. 20 has no amendment note', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['loss carry-forward (5 years, чл. 70) not modelled', 'withholding on dividends to non-residents (чл. 194, 5 %) not read']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': "the 1.x model's ciela copy of ЗКПО is not in its law folder (listed name only); lex.bg not fetched in this pass", 'unsupported': ['would unlock: ЗКПО on lex.bg with its amendment notes']}]}

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
