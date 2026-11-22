S = {'cc': 'BA', 'fam': 'Corporate', 'doc': '# BA 2025: Porez na dobit (Federacija BiH) (1200) and withholding on payments abroad\n\nSource: PwC Worldwide Tax Summaries, Bosnia and Herzegovina, Corporate - Taxes on corporate income, accessed 2026-11-21 (live page reviewed 23 September 2026, no 2025 capture; `ba/law/pwc_cit_live.html`); Corporate - Withholding taxes, accessed 2025-07-18 (Wayback capture; `ba/law/pwc_wht_wb2025.html`); sha256 in `law/SHA256SUMS`.\n* CIT 10 % in each of the Federation of BiH, Republika Srpska and Brčko District\n* WHT (FBiH): dividends 5 %; interest, royalties, other 10 %; Republika Srpska 10 % (PwC page reviewed 6 February 2025)\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Porez na dobit (Federacija BiH)",\n    sched := Schedule.flat 1000 }\n\ndef wht : Wht :=\n  { name := "withholding tax on payments abroad", rules := [\n    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 500, statute := "Zakon o porezu na dobit FBiH: 5 % on dividends (PwC 2025)" },\n    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "10 % (PwC 2025)" },\n    { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "10 % (PwC 2025)" }] }\n\ndef citStatute : String := "Zakon o porezu na dobit (FBiH; also Republika Srpska and Brčko District): 10 %"\n', 'families': [('1200 Porez na dobit (Federacija BiH)', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])\n       ++ (if g.entity == .company then wht.charges g.company else [])')], 'notes': ['BA 1200: PwC (CIT page reviewed 2026: the 10 % in all three entities is long-standing; WHT page reviewed February 2025)'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 10000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 100000', 'wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 5000', 'wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 10000', 'wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 10000'], 'taxes': [{'oecd': '1200', 'tax': 'Porez na dobit (Federacija BiH)', 'statute': 'Zakon o porezu na dobit (FBiH; also Republika Srpska and Brčko District): 10 %', 'dated': 'PwC (CIT page reviewed 2026: the 10 % in all three entities is long-standing; WHT page reviewed February 2025)', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ["the entity acts' own text not reached (secondary host)", "the Federation's rules taken (RS and Brčko also 10 %; RS withholding 10 % on dividends not separated)"]}, {'oecd': '1200', 'tax': 'withholding tax on payments abroad', 'statute': 'Zakon o porezu na dobit FBiH: 5 % on dividends (PwC 2025); 10 % (PwC 2025); 10 % (PwC 2025)', 'dated': 'PwC (CIT page reviewed 2026: the 10 % in all three entities is long-standing; WHT page reviewed February 2025)', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': ['treaty rates out of scope (statutory, treaty-free)']}]}

# ---- pass 9 (R1 Europe, 2026-11-21): remaining withholding, carry-overs, B -> A, P5/P6 (tools/p9_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
p9_rows(S)
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
