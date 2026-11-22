S = {'cc': 'SK', 'fam': 'Corporate', 'doc': '# SK 2025: Daň z príjmov právnickej osoby (1200) and withholding on payments abroad\n\nSource: Slov-Lex (official) static consolidation in force from 1 January 2025 of zákon 595/2003 Z. z. o dani z príjmov (`sk/law/dp_20250101.html`); sha256 in `law/SHA256SUMS`.\n* § 15 písm. b): "1a. 10 % pre daňovníka, ktorý dosiahol za zdaňovacie obdobie zdaniteľné príjmy (výnosy) neprevyšujúce sumu 100 000 eur, 1b. 21 % pre daňovníka neuvedeného v bode 1a. alebo bode 1c., 1c. 24 % pre daňovníka, ktorý dosiahol ... prevyšujúce sumu 5 000 000 eur"\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Daň z príjmov právnickej osoby",\n    sched := Schedule.flat 2100,\n    smallTurnover := 100000,\n    smallSched := Schedule.flat 1000 }\n\ndef citStatute : String := "zákon 595/2003 Z. z. § 15 písm. b) bod 1a (10 %), 1b (21 %), 1c (24 %)"\n', 'families': [('1200 Daň z príjmov právnickej osoby', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['SK 1200: Slov-Lex znenie od 1. 1. 2025'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 21000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 210000', 'cit.citTax { profit := 100000, turnover := 100000 } == 10000', 'cit.citTax { profit := 100000, turnover := 100001 } == 21000'], 'taxes': [{'oecd': '1200', 'tax': 'Daň z príjmov právnickej osoby', 'statute': 'zákon 595/2003 Z. z. § 15 písm. b) bod 1a (10 %), 1b (21 %), 1c (24 %)', 'dated': 'Slov-Lex znenie od 1. 1. 2025', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['24 % for revenue over 5 000 000 eur (bod 1c) not applied (21 %)', 'loss carry-forward (§ 30) not modelled', 'withholding (§ 43) not read in this pass']}]}


# ---- FT review (2026-11-21, third pass): § 15 písm. b) bod 1c (24 % above 5 000 000 eur) (ftd_oecd_cit_rates_2025 dev; IMPROVE_FT D2-8) ----
S["doc"] += r'''
## FT review (2026-11-21, third pass): the 24 % band
Same consolidation (`sk/law/dp_20250101.txt`), **§ 15 písm. b) bod 1c.**: "24 % pre daňovníka, ktorý dosiahol za
zdaňovacie obdobie zdaniteľné príjmy (výnosy) prevyšujúce sumu 5 000 000 eur". The model cited 1c but applied 21 %
(1b) to every taxpayer above the 1a threshold. Taxable revenues are read as the company's turnover, as for 1a.
'''
S["lean"] += r'''
/-- § 15 písm. b) bod 1c.: 24 % where taxable revenues exceed 5 000 000 eur (FT review, third pass) -/
def citLarge : CorpRegime :=
  { name := "Daň z príjmov právnickej osoby",
    sched := Schedule.flat 2400 }
'''
S["families"] = [(n, c, e.replace("[cit.citCharge g.company citStatute]",
                                   "[(if g.company.turnover > 5000000 then citLarge else cit).citCharge g.company citStatute]"))
                 for n, c, e in S["families"]]
S["guards"] = S["guards"] + ["citLarge.citTax { profit := 1000000, turnover := 5000001 } == 240000"]

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
