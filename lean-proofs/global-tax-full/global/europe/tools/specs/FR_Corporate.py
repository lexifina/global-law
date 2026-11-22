S = {'cc': 'FR', 'fam': 'Corporate', 'doc': '# FR 2025: Impôt sur les sociétés (1200) and withholding on payments abroad\n\nSource: CGI article copies of the 1.x French model (`fr/law/y2025/219.md` version 2026-02-21, `209.md` version 2023-12-31, `216.md` version 2023-12-31; Légifrance blocked); sha256 in `law/SHA256SUMS`.\n* art. 219 I: "Le taux normal de l\'impôt est fixé à 25 %"; b: 15 % up to "42 500 € de bénéfice imposable par période de douze mois" for companies with turnover under "10 000 000" €\n* art. 209 I: losses deductible up to "1 000 000 € majoré de 50 % du montant correspondant au bénéfice imposable dudit exercice excédant ce premier montant"\n* art. 216: the exempt dividends bear a share of costs of "5 % du produit total des participations" (holding ≥ 5 %, art. 145, not read)\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Impôt sur les sociétés",\n    sched := Schedule.flat 2500,\n    smallTurnover := 9999999,\n    smallSched := Schedule.ofList [(0, 1500), (42500, 2500)],\n    lossFull := 1000000,\n    lossExcessBp := 5000,\n    participationBp := 9500,\n    participationMinBp := 500 }\n\ndef citStatute : String := "CGI art. 219 I (25 %; b: 15 % jusqu\'à 42 500 €, CA < 10 M€), art. 209 I (1 000 000 € + 50 %), art. 216 (quote-part 5 %)"\n', 'families': [('1200 Impôt sur les sociétés', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['FR 1200: CGI copies (219 in its 2026-02-21 version; 209, 216 versions in force 2025)'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 29999997 } == 25000', 'cit.citTax { profit := 1000000, turnover := 29999997 } == 250000', 'cit.citTax { profit := 100000, turnover := 9999999 } == 20750', 'cit.citTax { profit := 100000, turnover := 10000000 } == 25000', 'cit.citTax { profit := 3000000, lossesForward := 5000000, turnover := 29999997 } == 250000', 'cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 500 } == 620000', 'cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 499 } == 1000000'], 'taxes': [{'oecd': '1200', 'tax': 'Impôt sur les sociétés', 'statute': "CGI art. 219 I (25 %; b: 15 % jusqu'à 42 500 €, CA < 10 M€), art. 209 I (1 000 000 € + 50 %), art. 216 (quote-part 5 %)", 'dated': 'CGI copies (219 in its 2026-02-21 version; 209, 216 versions in force 2025)', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['art. 219 read in its 2026 version', 'contribution sociale (art. 235 ter ZC) and the 2025 contribution exceptionnelle (LF 2025) not modelled', 'withholding (art. 119 bis, 182 B) not in the local copies: not modelled', 'PME condition of paid-up capital held by individuals not checked']}]}

# ---- pass 8 (R1 Europe, 2026-11-21): withholding under kernel 2.3.0, P5/P6 gaps, P7 surcharges, carry-overs (tools/p8_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
p8_rows(S)
p6_finish(S)

# ---- pass 10 (R1 Europe, 2026-11-21): vehicle taxes, conditional withholding, remaining withholding (tools/p10_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
p10_rows(S)
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
