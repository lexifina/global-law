S = {'cc': 'RO', 'fam': 'Corporate', 'doc': '# RO 2025: Impozit pe profit (1200) and withholding on payments abroad\n\nSource: Codul fiscal art. 17 as in force on 2025-03-01, the copy kept by the 1.x model (`ro/law/art-017_2025-03-01.txt`, a Global law record read before the MCP stop, pointing to legislatie.just.ro DetaliiDocument/171282); sha256 in `law/SHA256SUMS`.\n* art. 17: "Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%"\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Impozit pe profit",\n    sched := Schedule.flat 1600 }\n\ndef citStatute : String := "Codul fiscal (Legea nr. 227/2015) art. 17 (16 %)"\n', 'families': [('1200 Impozit pe profit', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['RO 1200: art. 17 as in force 2025-03-01 (unchanged since 2016)'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 16000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 160000'], 'taxes': [{'oecd': '1200', 'tax': 'Impozit pe profit', 'statute': 'Codul fiscal (Legea nr. 227/2015) art. 17 (16 %)', 'dated': 'art. 17 as in force 2025-03-01 (unchanged since 2016)', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['impozitul pe veniturile microîntreprinderilor (art. 47-56: 1 % / 3 % of turnover, mandatory under the conditions) not modelled', 'minimum turnover tax (art. 18^3, 1 % for turnover over 50 M€) not modelled', 'withholding (art. 224) not read']}]}

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

# ---- pass 10 (R1 Europe, 2026-11-21): vehicle taxes, conditional withholding, remaining withholding (tools/p10_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
p10_rows(S)
p6_finish(S)
