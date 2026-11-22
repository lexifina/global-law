S = {'cc': 'DK', 'fam': 'Corporate', 'doc': '# DK 2025: Selskabsskat (1200) and withholding on payments abroad\n\nSource: Bekendtgørelse af selskabsskatteloven, LBK nr 279 af 13/03/2025 (retsinformation ELI XML `eli/lta/2025/279/xml`, `dk/law/sel_lbk2025_279.xml`; in force from March 2025 until LBK nr 984 af 15/10/2026); sha256 in `law/SHA256SUMS`.\n* § 17, stk. 1: "Indkomstskatten for de i § 1, stk. 1, nr. 1-2 i og 3 a-5 b ... nævnte selskaber og foreninger m.v. (selskabsskatten) beregnes af den skattepligtige indkomst og udgør 22 pct."\n* § 13, stk. 1, nr. 2: "Udbytte, som de i § 1 ... nævnte selskaber ... modtager ... Dette gælder dog kun udbytter af datterselskabsaktier og koncernselskabsaktier, jf. aktieavancebeskatningslovens §§ 4 A og 4 B" (datterselskabsaktier: at least 10 %)\n* § 12, stk. 2: losses in full up to "et grundbeløb på 15,9 mio. kr. (2010-niveau)", the rest in 60 pct. of the excess; the grundbeløb is indexed (personskattelovens § 20) and its 2025 amount is not in the act\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Selskabsskat",\n    sched := Schedule.flat 2200,\n    participationBp := 10000,\n    participationMinBp := 1000 }\n\ndef citStatute : String := "Selskabsskatteloven (LBK nr 279 af 13/03/2025) § 17, stk. 1 (22 pct.), § 13, stk. 1, nr. 2 (udbytte af datterselskabsaktier)"\n', 'families': [('1200 Selskabsskat', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['DK 1200: LBK nr 279 af 13/03/2025'], 'unsupported': [('g.entity == .company && g.company.lossesForward > 0', 'DK § 12, stk. 2 loss cap (indexed grundbeløb + 60 %) not applied: losses offset in full'), ('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 22000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 220000', 'cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 1000 } == 600000', 'cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 999 } == 1000000'], 'taxes': [{'oecd': '1200', 'tax': 'Selskabsskat', 'statute': 'Selskabsskatteloven (LBK nr 279 af 13/03/2025) § 17, stk. 1 (22 pct.), § 13, stk. 1, nr. 2 (udbytte af datterselskabsaktier)', 'dated': 'LBK nr 279 af 13/03/2025', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['loss cap of § 12, stk. 2 (indexed grundbeløb, 60 %) not applied: losses are offset in full', 'koncernselskabsaktier (ABL § 4 B) not separated', 'tillægsselskabsskat (kulbrinte) out of scope']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'retsinformation.dk returns script shells', 'unsupported': ['would unlock: the LBK texts via the retsinformation ELI XML']}]}

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
