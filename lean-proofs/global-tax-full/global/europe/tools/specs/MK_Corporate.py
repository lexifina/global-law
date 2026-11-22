S = {'cc': 'MK', 'fam': 'Corporate', 'doc': '# MK 2025: Данок на добивка (1200) and withholding on payments abroad\n\nSource: PwC Worldwide Tax Summaries, North Macedonia, Corporate - Taxes on corporate income, accessed 2025-05-21 (Wayback capture; `mk/law/pwc_cit_wb2025.html`); Corporate - Withholding taxes, accessed 2025-05-14 (Wayback capture; `mk/law/pwc_wht_wb2025.html`); sha256 in `law/SHA256SUMS`.\n* CIT 10 % (PwC page reviewed 18 February 2025)\n* WHT 10 % on listed income paid abroad (dividends, interest, royalties, ...)\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Данок на добивка",\n    sched := Schedule.flat 1000 }\n\ndef wht : Wht :=\n  { name := "withholding tax on payments abroad", rules := [\n    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "Закон за данокот на добивка: 10 % (PwC 2025)" },\n    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "10 % (PwC 2025)" },\n    { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "10 % (PwC 2025)" }] }\n\ndef citStatute : String := "Закон за данокот на добивка (10 %)"\n', 'families': [('1200 Данок на добивка', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])\n       ++ (if g.entity == .company then wht.charges g.company else [])')], 'notes': ['MK 1200: PwC, last reviewed 18 February 2025'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 10000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 100000', 'wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 10000', 'wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 10000', 'wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 10000'], 'taxes': [{'oecd': '1200', 'tax': 'Данок на добивка', 'statute': 'Закон за данокот на добивка (10 %)', 'dated': 'PwC, last reviewed 18 February 2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ["the act's own text not reached (secondary host)", 'simplified regime (1 % of income between MKD 3 and 6 million, optional) not modelled']}, {'oecd': '1200', 'tax': 'withholding tax on payments abroad', 'statute': 'Закон за данокот на добивка: 10 % (PwC 2025); 10 % (PwC 2025); 10 % (PwC 2025)', 'dated': 'PwC, last reviewed 18 February 2025', 'grade': 'B', 'kernel_parts': ['Wht'], 'unsupported': ['treaty rates out of scope (statutory, treaty-free)']}]}

# ---- pass 8 (R1 Europe, 2026-11-21): withholding under kernel 2.3.0, P5/P6 gaps, P7 surcharges, carry-overs (tools/p8_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
p8_rows(S)
p6_finish(S)

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
