S = {'cc': 'NL', 'fam': 'Corporate', 'doc': '# NL 2025: Vennootschapsbelasting (1200) and withholding on payments abroad\n\nSource: wetten.overheid.nl, versions geldend 2025: Wet op de vennootschapsbelasting 1969 (`nl/law/vpb_g2025.html`), Wet op de dividendbelasting 1965 (`nl/law/divbel_g2025.html`); sha256 in `law/SHA256SUMS`.\n* Wet Vpb art. 22: bracket table "€ 200.000 | 19%", above "25,8%"\n* Wet DB art. 5: "De belasting bedraagt 15% van de opbrengst"\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Vennootschapsbelasting",\n    sched := Schedule.ofList [(0, 1900), (200000, 2580)] }\n\ndef wht : Wht :=\n  { name := "Dividendbelasting", rules := [\n    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "Wet op de dividendbelasting 1965 art. 5: 15%" }] }\n\ndef citStatute : String := "Wet Vpb 1969 art. 22 lid 1 (19 % tot € 200.000, 25,8 %)"\n', 'families': [('1200 Vennootschapsbelasting', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])\n       ++ (if g.entity == .company then wht.charges g.company else [])')], 'notes': ['NL 1200: wetten.overheid.nl geldend 2025'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 19000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 244400', 'wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 15000'], 'taxes': [{'oecd': '1200', 'tax': 'Vennootschapsbelasting', 'statute': 'Wet Vpb 1969 art. 22 lid 1 (19 % tot € 200.000, 25,8 %)', 'dated': 'wetten.overheid.nl geldend 2025', 'grade': 'A', 'kernel_parts': ['CorpRegime'], 'unsupported': ['art. 20 loss offset (€ 1 mln + 50 %) not read', 'deelnemingsvrijstelling (art. 13) not modelled', 'art. 15b earnings stripping']}, {'oecd': '1200', 'tax': 'Dividendbelasting', 'statute': 'Wet op de dividendbelasting 1965 art. 5: 15%', 'dated': 'wetten.overheid.nl geldend 2025', 'grade': 'A', 'kernel_parts': ['Wht'], 'unsupported': ['Wet bronbelasting 2021 (interest/royalties to low-tax jurisdictions) not modelled', 'participation exemption for EU parents (art. 4) not modelled']}]}


# ---- FT review (2026-11-21, third pass): Wet Vpb 1969 art. 20 lid 2 (nl_ft_cit_ekwo_grid dev; IMPROVE_FT hand-12) ----
S["doc"] += r"""
## FT review (2026-11-21, third pass): loss offset
Same wetten.overheid.nl text (g=2025-07-01, `nl/law/vpb_g2025.txt`), **art. 20 lid 2**: "Een verlies wordt verrekend met
de belastbare winsten ... van het voorafgaande jaar en de volgende jaren ... Daarbij vindt verrekening in een jaar
slechts plaats tot een bedrag van € 1.000.000 vermeerderd met 50% van de belastbare winst ... van dat jaar nadat die
winst ... is verminderd met een bedrag van € 1.000.000." The model offset losses in full.
"""
S["lean"] = S["lean"].replace("""    sched := Schedule.ofList [(0, 1900), (200000, 2580)] }""", """    sched := Schedule.ofList [(0, 1900), (200000, 2580)],
    lossFull := 1000000, lossExcessBp := 5000 }""", 1)
assert "lossFull := 1000000" in S["lean"]
S["lean"] = S["lean"].replace('def citStatute : String := "Wet Vpb 1969 art. 22 lid 1 (19 % tot € 200.000, 25,8 %)"',
                              'def citStatute : String := "Wet Vpb 1969 art. 22 lid 1 (19 % tot € 200.000, 25,8 %); art. 20 lid 2 (verliesverrekening tot € 1.000.000 + 50 %)"')
S["guards"] = S["guards"] + ["-- art. 20 lid 2: profit 3 m, losses 10 m: offset 1 m + 50 % x 2 m = 2 m; taxable 1 m",
                             "cit.citTax { profit := 3000000, lossesForward := 10000000 } == 244400"]

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
