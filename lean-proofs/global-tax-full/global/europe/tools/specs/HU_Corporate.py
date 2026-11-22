S = {'cc': 'HU', 'fam': 'Corporate', 'doc': '# HU 2025: Társasági adó (1200) and withholding on payments abroad\n\nSource: 1996. évi LXXXI. törvény, net.jogtar.hu (Wolters Kluwer, private publisher of the consolidated text), `hu/law/tao.html`; sha256 in `law/SHA256SUMS`.\n* III. Fejezet A társasági adó mértéke, 19. §: "A társasági adó mértéke 9 százalék. A társasági adó a pozitív adóalap ..."\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Társasági adó",\n    sched := Schedule.flat 900 }\n\ndef citStatute : String := "1996. évi LXXXI. törvény a társasági adóról és az osztalékadóról 19. § (9 százalék)"\n', 'families': [('1200 Társasági adó', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['HU 1200: consolidated text (jogtar), current at fetch (2026-11)'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 9000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 90000'], 'taxes': [{'oecd': '1200', 'tax': 'Társasági adó', 'statute': '1996. évi LXXXI. törvény a társasági adóról és az osztalékadóról 19. § (9 százalék)', 'dated': 'consolidated text (jogtar), current at fetch (2026-11)', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['helyi iparűzési adó (local business tax, up to 2 % of the net turnover base, Htv.) not modelled', 'loss carry-forward limit (50 % of the base, 17. §) not modelled', 'Pillar Two top-up (2023. évi LXXXI.) not modelled']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P2 pass (net.jogtar.hu would serve the consolidated text)', 'unsupported': ['would unlock: 1996. évi LXXXI. törvény 19. § and Htv. 39. §']}]}

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

# ---- pass 9 (R1 Europe, 2026-11-21): remaining withholding, carry-overs, B -> A, P5/P6 (tools/p9_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
p9_rows(S)
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
