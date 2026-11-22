S = {'cc': 'RS', 'fam': 'Corporate', 'doc': '# RS 2025: Porez na dobit pravnih lica (1200) and withholding on payments abroad\n\nSource: Zakon o porezu na dobit pravnih lica, consolidated text published by Paragraf (private publisher; the official Pravno-informacioni sistem is script-only), `rs/law/pdpl.html`; sha256 in `law/SHA256SUMS`.\n* čl. 39: "Stopa poreza na dobit pravnih lica je proporcionalna i jednoobrazna. Stopa poreza na dobit pravnih lica iznosi 15%."\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Porez na dobit pravnih lica",\n    sched := Schedule.flat 1500 }\n\ndef citStatute : String := "Zakon o porezu na dobit pravnih lica čl. 39 (15 %)"\n', 'families': [('1200 Porez na dobit pravnih lica', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['RS 1200: Paragraf consolidated text, current at fetch (2026-11)'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 15000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 150000'], 'taxes': [{'oecd': '1200', 'tax': 'Porez na dobit pravnih lica', 'statute': 'Zakon o porezu na dobit pravnih lica čl. 39 (15 %)', 'dated': 'Paragraf consolidated text, current at fetch (2026-11)', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['porez na dobit po odbitku (čl. 40, 20 %) not modelled', 'loss carry-forward (5 years) not modelled']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not fetched in the P2 pass (paragraf.rs serves it, private publisher)', 'unsupported': ['would unlock: the consolidated profit tax law']}]}

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
