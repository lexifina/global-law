S = {'cc': 'BE', 'fam': 'Corporate', 'doc': '# BE 2025: Impôt des sociétés (1200) and withholding on payments abroad\n\nSource: Loi du 25 décembre 2017 portant réforme de l\'impôt des sociétés (MB 29.12.2017, numac 2017014414), eTaamb (etaamb.openjustice.be, `be/law/loi20171225_reforme_isoc_n2017014414.html`); sha256 in `law/SHA256SUMS`.\n* art. 54, 1°: "Art. 215. Le taux de l\'impôt des sociétés est fixé à 29 p.c. Pour les sociétés qui ... sont considérées comme des petites sociétés, le taux de l\'impôt sur la première tranche de 0 à 100 000 euros est toutefois fixé à 20 p.c."\n* art. 54, 3°: "dans l\'alinéa 1er, remplacé par le 1°, les mots \\"29 p.c.\\" sont remplacés par les mots \\"25 p.c.\\""\n* art. 86 B2: "Les articles ... 54, 3° ... entrent en vigueur le 1er janvier 2020 et sont applicables à partir de l\'exercice d\'imposition 2021"\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Impôt des sociétés",\n    sched := Schedule.flat 2500 }\n\ndef citStatute : String := "CIR 92 art. 215, al. 1 (25 p.c.), as replaced by the Loi du 25 décembre 2017 art. 54, 1° and 3° (in force for exercice d\'imposition 2021 onwards, art. 86 B2)"\n', 'families': [('1200 Impôt des sociétés', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ["BE 1200: amending act of 25.12.2017 read (25 % from exercice d'imposition 2021); the consolidated CIR 92 text as in force in 2025 not reached (later amendments of art. 215 not checked)"], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 25000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 250000'], 'taxes': [{'oecd': '1200', 'tax': 'Impôt des sociétés', 'statute': "CIR 92 art. 215, al. 1 (25 p.c.), as replaced by the Loi du 25 décembre 2017 art. 54, 1° and 3° (in force for exercice d'imposition 2021 onwards, art. 86 B2)", 'dated': "amending act of 25.12.2017 read (25 % from exercice d'imposition 2021); the consolidated CIR 92 text as in force in 2025 not reached (later amendments of art. 215 not checked)", 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['read from the amending act of 2017, not from the 2025 consolidated CIR 92', "PME rate 20 p.c. on the first 100 000 EUR (art. 215, al. 2; petite société under the Code des sociétés art. 15 and the al. 3 conditions, e.g. a director's remuneration) not applied", 'minimum taxable base (art. 207, al. 5-7 loss and deduction caps) and the Pillar Two minimum tax not modelled']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': "the 1.x model's Fisconet copies cover PIT articles only; ejustice answered HTTP 500", 'unsupported': ['would unlock: CIR 92 art. 215, 216 (Fisconet) as in force for assessment year 2026']}]}

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
