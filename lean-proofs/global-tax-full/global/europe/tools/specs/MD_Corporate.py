S = {'cc': 'MD', 'fam': 'Corporate', 'doc': '# MD 2025: Impozitul pe venit (persoane juridice) (1200) and withholding on payments abroad\n\nSource: PwC Worldwide Tax Summaries, Moldova, Corporate - Taxes on corporate income, accessed 2025-07-08 (Wayback capture; `md/law/pwc_cit_wb2025.html`); legis.md refuses scripts (403), no Wayback copy of the Code; sha256 in `law/SHA256SUMS`.\n* CIT 12 % (PwC page reviewed 2 July 2025); farming enterprises 7 %; optional 4 % regime on aggregated income for SMEs not registered for VAT\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Impozitul pe venit (persoane juridice)",\n    sched := Schedule.flat 1200 }\n\ndef citStatute : String := "Codul fiscal nr. 1163/1997 art. 15 lit. b) (12 %)"\n', 'families': [('1200 Impozitul pe venit (persoane juridice)', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['MD 1200: PwC, last reviewed 2 July 2025'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 12000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 120000'], 'taxes': [{'oecd': '1200', 'tax': 'Impozitul pe venit (persoane juridice)', 'statute': 'Codul fiscal nr. 1163/1997 art. 15 lit. b) (12 %)', 'dated': 'PwC, last reviewed 2 July 2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ["the Code's own text not reached (secondary host)", '4 % regime for small non-VAT companies and 7 % for farming enterprises not modelled']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': "the 1.x model's 2025 Codul fiscal copy is empty; the 2026 copy is not dated 2025", 'unsupported': ['would unlock: Codul fiscal as in force 2025']}]}

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
p6_wht_rows(S)
p6_finish(S)

# ---- pass 9 (R1 Europe, 2026-11-21): remaining withholding, carry-overs, B -> A, P5/P6 (tools/p9_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
p9_rows(S)
p6_finish(S)
