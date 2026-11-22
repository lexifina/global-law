S = {'cc': 'HR', 'fam': 'Corporate', 'doc': '# HR 2025: Porez na dobit (1200) and withholding on payments abroad\n\nSource: Narodne novine (official gazette) amending acts NN 138/2020 and NN 114/2023 (`hr/law/nn2020_138_2627_dobit.html`, `nn2023_114_1613_dobit.html`); the article\'s full wording from the unofficial consolidated text of zakon.hr (to NN 53/26; zakon.hr refuses scripts, read through a research agent), no official consolidation; sha256 in `law/SHA256SUMS`.\n* čl. 28 st. 1 (consolidated): "Porez na dobit plaća se na utvrđenu poreznu osnovicu po stopi: 1. 10% ako su u poreznom razdoblju ostvareni prihodi do 1.000.000,00 eura, ili 2. 18% ako su u poreznom razdoblju ostvareni prihodi jednaki ili veći od 1.000.000,00 eura."\n* NN 114/2023: "U članku 28. stavku 1. točki 1. riječi: »995.421,06 eura« zamjenjuju se riječima: 1.000.000,00 eura«. U točki 2. riječi: »995.421,06 eura« zamjenjuju se riječima: »1.000.000,00 eura«."\n* NN 138/2020: "U članku 28. točki 1. riječi: »12%« zamjenjuju se riječima: »10%«."\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Porez na dobit",\n    sched := Schedule.flat 1800,\n    smallTurnover := 999999,\n    smallSched := Schedule.flat 1000 }\n\ndef citStatute : String := "Zakon o porezu na dobit čl. 28 st. 1 (10 % if revenue below 1.000.000,00 eura, 18 % otherwise); NN 138/2020 (12 -> 10 %), NN 114/2023 čl. 8 (threshold 1.000.000,00 eura from 1.1.2024)"\n', 'families': [('1200 Porez na dobit', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['HR 1200: NN 114/2023 (tax periods from 1.1.2024); full article via the unofficial consolidation'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 18000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 180000', 'cit.citTax { profit := 100000, turnover := 999999 } == 10000', 'cit.citTax { profit := 100000, turnover := 1000000 } == 18000'], 'taxes': [{'oecd': '1200', 'tax': 'Porez na dobit', 'statute': 'Zakon o porezu na dobit čl. 28 st. 1 (10 % if revenue below 1.000.000,00 eura, 18 % otherwise); NN 138/2020 (12 -> 10 %), NN 114/2023 čl. 8 (threshold 1.000.000,00 eura from 1.1.2024)', 'dated': 'NN 114/2023 (tax periods from 1.1.2024); full article via the unofficial consolidation', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['the 18 % wording itself read only in the unofficial consolidation (the 2016 act setting it not fetched)', 'loss carry-forward (5 years, čl. 17) not modelled']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'zakon.hr 403; no 2025 Internet Archive capture', 'unsupported': ['would unlock: the profit tax law consolidated as in force 2025 (NN 114/23)']}]}

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
