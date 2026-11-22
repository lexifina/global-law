S = {'cc': 'PT', 'fam': 'Corporate', 'doc': '# PT 2025: Imposto sobre o Rendimento das Pessoas Coletivas (1200) and withholding on payments abroad\n\nSource: Lei n.º 45-A/2024 (Orçamento do Estado para 2025), Diário da República PDF kept by the 1.x model (`pt/law/Lei_45_A_2024.pdf`), which restates CIRC art. 87.º; sha256 in `law/SHA256SUMS`.\n* CIRC art. 87.º: "1 - A taxa do IRC é de 20 %, exceto nos casos previstos nos números seguintes. 2 - No caso de sujeitos passivos que ... sejam qualificados como pequena ou média empresa ... a taxa de IRC aplicável aos primeiros 50 000 € de matéria coletável é de 16 %, aplicando-se a taxa prevista no número anterior ao excedente"\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Imposto sobre o Rendimento das Pessoas Coletivas",\n    sched := Schedule.flat 2000,\n    smallTurnover := 50000000,\n    smallSched := Schedule.ofList [(0, 1600), (50000, 2000)] }\n\ndef citStatute : String := "CIRC art. 87.º n.º 1 (20 %), n.º 2 (16 % sobre os primeiros 50 000 €, PME), na redação da Lei n.º 45-A/2024 (OE 2025)"\n', 'families': [('1200 Imposto sobre o Rendimento das Pessoas Coletivas', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['PT 1200: Lei 45-A/2024 (in force 1.1.2025)'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 150000000 } == 20000', 'cit.citTax { profit := 1000000, turnover := 150000000 } == 200000', 'cit.citTax { profit := 100000, turnover := 50000000 } == 18000', 'cit.citTax { profit := 100000, turnover := 50000001 } == 20000'], 'taxes': [{'oecd': '1200', 'tax': 'Imposto sobre o Rendimento das Pessoas Coletivas', 'statute': 'CIRC art. 87.º n.º 1 (20 %), n.º 2 (16 % sobre os primeiros 50 000 €, PME), na redação da Lei n.º 45-A/2024 (OE 2025)', 'dated': 'Lei 45-A/2024 (in force 1.1.2025)', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['SME status (DL 372/2007 annex: < 250 employees and turnover ≤ 50 M€ or balance ≤ 43 M€) approximated by turnover ≤ 50 M€', 'derrama municipal and derrama estadual (art. 87.º-A) not modelled', 'tributação autónoma not modelled', 'withholding (art. 94.º) not read']}]}

# ---- FT review (2026-11-21, second pass): derrama estadual, CIRC art. 87.º-A (ftd_oecd_cit_rates_2025 dev failure) ----
S["doc"] += r'''
## FT review (2026-11-21, second pass): derrama estadual (CIRC art. 87.º-A)
Source: Portal das Finanças, CIRC art. 87.º-A, Wayback capture 2025-04-19
(`web.archive.org/web/20250419222655id_/https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/CIRC_2R/Pages/irc87a.aspx`,
saved as `pt/law/circ87a_2025-04-19.html`; the same wording live in 2026):
* n.º 1: "Sobre a parte do lucro tributável superior a (euro) 1 500 000 ... incidem as taxas adicionais constantes da
  tabela seguinte: (Redação da Lei n.º 114/2017 ...) De mais de 1500 000 até 7 500 000 ... 3; De mais de 7 500 000 até
  35 000 000 ... 5; Superior a 35 000 000 ... 9"; n.º 2 b) (in our words): above EUR 1 500 000 the profit is split into a slice of EUR 6 000 000 at 3 %, a slice of EUR 27 500 000 at 5 % and the rest above EUR 35 000 000 at 9 %
* The base is the *lucro tributável* (before the deduction of tax losses, which gives the matéria coletável): the
  charge's base and relieved base are the profit before losses. A central-government tax (level central).
'''
S["lean"] += r'''
/-- CIRC art. 87.º-A (derrama estadual): 3 % / 5 % / 9 % on the lucro tributável above 1.5 m / 7.5 m / 35 m €. -/
def derramaEstadual : Schedule := Schedule.ofList [(0, 0), (1500000, 300), (7500000, 500), (35000000, 900)]

def derramaStatute : String := "CIRC art. 87.º-A n.º 1, 2 (derrama estadual: 3 % de 1 500 000 a 7 500 000 €, 5 % até 35 000 000 €, 9 % acima; Lei n.º 114/2017)"

def derramaCharge (co : Company) : Charge :=
  charge .cit "Derrama estadual" (cit.beforeLosses co) id (fun b => derramaEstadual.tax {} b) (statute := derramaStatute)
'''
S["families"] = [(n, c, r.replace("[cit.citCharge g.company citStatute]", "[cit.citCharge g.company citStatute, derramaCharge g.company]")) for n, c, r in S["families"]]
S["guards"] += ["(derramaCharge { profit := 1500000 }).due == 0", "(derramaCharge { profit := 7500000 }).due == 180000",
                "(derramaCharge { profit := 35000000 }).due == 1555000", "(derramaCharge { profit := 40000000 }).due == 2005000",
                "(derramaCharge { profit := 40000000, lossesForward := 40000000 }).due == 2005000"]
for _t in S["taxes"]:
    if _t["oecd"] == "1200":
        _t["unsupported"] = [("derrama municipal (Lei 73/2013 art. 18, up to 1,5 %) not modelled" if u.startswith("derrama municipal and derrama estadual") else u) for u in _t["unsupported"]]
S["taxes"].append({"oecd": "1200", "tax": "Derrama estadual", "statute": "CIRC art. 87.º-A n.º 1, 2 (Lei n.º 114/2017)", "dated": "Portal das Finanças CIRC, Wayback 2025-04-19",
                   "grade": "A", "kernel_parts": ["charge", "Schedule"], "unsupported": ["the principal-activity condition (commercial, industrial or agricultural) is taken as met"]})
S["unsupported"] = S["unsupported"] + [("g.entity == .company", "derrama municipal (Lei 73/2013 art. 18, up to 1,5 %) not modelled; derrama estadual: the principal-activity condition (commercial, industrial or agricultural) taken as met")]

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
