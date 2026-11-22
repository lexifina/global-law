S = {'cc': 'SE', 'fam': 'Corporate', 'doc': '# SE 2025: Statlig inkomstskatt för juridiska personer (1200) and withholding on payments abroad\n\nSource: Inkomstskattelag (1999:1229), data.riksdagen.se `sfs-1999-1229.text` (ändrad t.o.m. SFS 2026:1393; `se/law/isl_riksdagen.txt`); sha256 in `law/SHA256SUMS`.\n* 65 kap. 10 §: "För juridiska personer är den statliga inkomstskatten 20,6 procent av den beskattningsbara inkomsten. Lag (2018:1206)."\n* övergångsbestämmelser 2018:1206 p. 11: 21,4 procent for years beginning after 31 December 2018 but before 1 January 2021 (so 20,6 % for 2025)\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Statlig inkomstskatt för juridiska personer",\n    sched := Schedule.flat 2060 }\n\ndef citStatute : String := "Inkomstskattelagen (1999:1229) 65 kap. 10 § (20,6 procent), Lag (2018:1206)"\n', 'families': [('1200 Statlig inkomstskatt för juridiska personer', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['SE 1200: 65 kap. 10 § unchanged since Lag (2018:1206) (in force for years from 2021)'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 20600', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 206000'], 'taxes': [{'oecd': '1200', 'tax': 'Statlig inkomstskatt för juridiska personer', 'statute': 'Inkomstskattelagen (1999:1229) 65 kap. 10 § (20,6 procent), Lag (2018:1206)', 'dated': '65 kap. 10 § unchanged since Lag (2018:1206) (in force for years from 2021)', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['näringsbetingade andelar (24 kap. 13-17 §§: tax-free dividends) not modelled', 'periodiseringsfond (30 kap.) not modelled', 'underskott: no cap, but ownership-change limits (40 kap.) not modelled']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not fetched in the P2 pass (riksdagen data API serves SFS texts)', 'unsupported': ['would unlock: SFS 1999:1229 and 1970:624 texts']}]}

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
