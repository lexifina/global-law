S = {'cc': 'RU', 'fam': 'Corporate', 'doc': '# RU 2025: Налог на прибыль организаций (1200) and withholding on payments abroad\n\nSource: Федеральный закон от 12.07.2024 № 176-ФЗ (text kept by the 1.x model, `ru/law/fz176_2024_clean.txt`), which restates НК РФ ст. 284 п. 1 from 1 January 2025; sha256 in `law/SHA256SUMS`.\n* 176-ФЗ п. 50 (ст. 284): "1. Налоговая ставка устанавливается в размере 25 процентов, если иное не установлено настоящей статьей. При этом: сумма налога, исчисленная по налоговой ставке в размере 7 процентов (8 процентов в 2025 - 2030 годах), зачисляется в федеральный бюджет"\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Налог на прибыль организаций",\n    sched := Schedule.flat 2500 }\n\ndef citStatute : String := "НК РФ ст. 284 п. 1 (25 %; 8 % федеральный бюджет в 2025-2030 годах) в редакции Федерального закона от 12.07.2024 № 176-ФЗ"\n', 'families': [('1200 Налог на прибыль организаций', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['RU 1200: 176-ФЗ amending text (the consolidated НК РФ not read)'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 25000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 250000'], 'taxes': [{'oecd': '1200', 'tax': 'Налог на прибыль организаций', 'statute': 'НК РФ ст. 284 п. 1 (25 %; 8 % федеральный бюджет в 2025-2030 годах) в редакции Федерального закона от 12.07.2024 № 176-ФЗ', 'dated': '176-ФЗ amending text (the consolidated НК РФ not read)', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['the consolidated НК РФ ст. 284 not read (amending law only)', 'loss carry-forward 50 % cap (ст. 283) not modelled', 'withholding (ст. 284 п. 3, ст. 310) not read']}]}

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

# ---- pass 15 (R1 Europe, 2026-11-21): publication requests, ENFIA, vehicles, transfers, withholding notes (tools/p15_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
p15_rows(S)
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
