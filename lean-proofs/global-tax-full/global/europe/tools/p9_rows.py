# pass 9 rows (R1 Europe, 2026-11-21): the remaining withholding (kernel 2.3.0), carry-overs, B -> A, P5/P6.
# exec'd by the spec after p6lib.py and p8_rows.py (helpers _q, _doc, pwc, _first8, _pay8). Statute rows quote or cite
# the act read (grade A); secondary rows (grade B) state facts only, with their provenance line.


def _wx(S, pfx, label, key, name, rules, title, dated, grade, src, facts, uns=(), remaining=None, drop_uns=()):
    """1200 withholding on payments abroad as a Wht family of its own (same contract as p8 `_w8`): rules =
    [(kind, rateBp, toCompany None/True/False, statute[, minStakeBp])], first match; a 0 rate is a cited statutory zero.
    remaining: kinds still unread (one renamed grade-C entry kept; [] = none left). drop_uns: substrings of earlier
    unsupported lines (model level and per-tax) that this family now answers."""
    if S.get("fam") != "Corporate":
        return
    S.setdefault("families", []); S.setdefault("notes", []); S.setdefault("guards", []); S.setdefault("unsupported", [])
    S["lean"] = S.get("lean") or ""
    tcl = lambda tc: "none" if tc is None else ("some true" if tc else "some false")
    rl = ",\n    ".join(f"{{ kind := .{r[0]}, toCompany := {tcl(r[2])}, minStakeBp := {r[4] if len(r) > 4 else 0}, rateBp := {r[1]}, statute := {_q(r[3])} }}" for r in rules)
    S["lean"] += f"\n/-- {title} -/\ndef {pfx}{key} : Wht :=\n  {{ name := {_q(name)}, rules := [\n    {rl}] }}\n"
    S["families"].append((f"1200 {name} ({label})", [".cit"], f"(if g.entity == .company then {pfx}{key}.charges g.company else [])"))
    seen = set()
    for r in rules:
        k, tc, ms = r[0], r[2], (r[4] if len(r) > 4 else 0)
        for toc in ([True, False] if tc is None else [tc]):
            if (k, toc, ms) in seen:
                continue
            seen.add((k, toc, ms))
            v = _first8(rules, k, toc, ms)
            S["guards"].append(f"{pfx}{key}.amount {{ kind := .{k}, amount := 100000, toCompany := {'true' if toc else 'false'}, stakeBp := {ms} }} == {v * 100000 // 10000}")
    for d in drop_uns:
        S["unsupported"] = [u for u in S["unsupported"] if d not in u[1]]
        for t in S["taxes"]:
            if t.get("unsupported"):
                t["unsupported"] = [x for x in t["unsupported"] if d not in x]
    if remaining is not None:
        cs = [t for t in S["taxes"] if t.get("grade") == "C" and "ithholding" in t.get("tax", "")]
        S["taxes"] = [t for t in S["taxes"] if t not in cs]
        S["unsupported"] = [u for u in S["unsupported"] if not ("ithholding" in u[1] and "grade C" in u[1])]
        if remaining:
            S["taxes"].append({"oecd": "1200", "tax": "Withholding on " + ", ".join(remaining) + " paid abroad", "statute": "not read", "dated": "",
                               "grade": "C", "status": "unsupported", "kernel_parts": [],
                               "tried": f"{label}: no statute or official/secondary source on disk states the rule for these kinds",
                               "unsupported": ["kernel 2.3.0 lists each such payment as \"no rule read (grade C)\""]})
    S["unsupported"] += [(c, "1200 withholding: " + t) for c, t in uns]
    kinds = sorted({r[0] for r in rules})
    rcp = sorted({"companies" if r[2] else "individuals" for r in rules if r[2] is not None}) or ["all recipients"]
    zeros = sorted({r[0] for r in rules if r[1] == 0})
    S["notes"].append(f"{S['cc']} 1200 withholding {label} ({', '.join(kinds)}; {', '.join(rcp)}): {dated} (grade {grade})")
    S["taxes"].append({"oecd": "1200", "tax": f"{name} ({', '.join(kinds)})", "statute": title, "dated": dated, "grade": grade,
                       "kernel_parts": ["Wht"] + (["WhtRule.zero (cited)"] if zeros else []),
                       "unsupported": [t for _, t in uns] + ["treaty rates and EU directives out of scope (statutory, treaty-free)"]})
    S["doc"] += f"\n\n## 1200 {name}: {', '.join(kinds)} ({label}, grade {grade})\nSource: {src}.\n" + "".join(f"* {x}\n" for x in facts)


def _w9(S, key, *a, **k):
    _wx(S, "p9", "pass 9", key, *a, **k)


def _c9(S, tried, unlock):
    """Keep a remaining grade-C withholding entry and record what pass 9 read (the law taxes by return, or the rule is
    conditional on facts the input lacks)."""
    if S.get("fam") != "Corporate":
        return
    for t in S["taxes"]:
        if t.get("grade") == "C" and "ithholding" in t.get("tax", ""):
            t["tried"] = (t.get("tried", "") + "; pass 9: " + tried).lstrip("; ")
            t["unsupported"] = list(t.get("unsupported", [])) + ["would unlock: " + unlock]
    S["doc"] += f"\n\n## 1200 withholding still grade C (pass 9)\n* {tried}\n* would unlock: {unlock}\n"


def _ind9(kind_or_all=None):
    if kind_or_all is None:
        return "g.entity == .company && g.company.paymentsAbroad.any (fun p => !p.toCompany)"
    return f"g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .{kind_or_all} && !p.toCompany)"


def _co9(kind):
    return f"g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .{kind} && p.toCompany)"


def _pw9(cc, name="pwc_wht_wb2025", page="Corporate - Withholding taxes"):
    return pwc(cc, name, page)


def _pwd9(cc, name="pwc_wht_wb2025", page="Corporate - Withholding taxes"):
    return pwc(cc, name, page).split(", accessed ")[1].split(" (")[0]


_IND_GC = "payments to non-resident individuals"   # pass-8 unsupported lines answered by the pass-9 individual rules


# ---------------------------------------------------------------- 1. withholding still unread after pass 8
def _wht9(S):
    cc = S["cc"]
    if S.get("fam") != "Corporate":
        return
    if cc == "IS":
        _w9(S, "wht", "Tekjuskattur aðila með takmarkaða skattskyldu (afdráttur)",
            [("dividend", 2000, True, "lög nr. 90/2003, 3. gr. 7. tölul., 70. gr. 7. tölul. b-liður: 20% of dividends to legal entities"),
             ("dividend", 2200, False, "lög nr. 90/2003, 3. gr. 7. tölul., 70. gr. 7. tölul. a-liður: 22% of dividends to individuals"),
             ("interest", 1200, None, "lög nr. 90/2003, 3. gr. 8. tölul., 70. gr. 8. tölul. a- og b-liður: 12% of interest"),
             ("royalty", 2200, None, "lög nr. 90/2003, 3. gr. 6. tölul., 70. gr. 6. tölul.: 22% of income from the use of rights, patents and know-how"),
             ("services", 2000, None, "lög nr. 90/2003, 3. gr. 3. tölul., 70. gr. 3. tölul. a- og b-liður: 20% of the payment for services performed in Iceland")],
            "Lög um tekjuskatt nr. 90/2003, 3. gr. 3., 6., 7. og 8. tölul.; 70. gr. 3., 6., 7. og 8. tölul.", "Lagasafn 156b, 1 September 2025 (`is/law/tsl_wb.html`)", "A",
            "Lög um tekjuskatt nr. 90/2003, Lagasafn útgáfa 156b, althingi.is via the Internet Archive (`is/law/tsl_wb.html`)",
            ["3. gr.: limited tax liability on payment for services or activity performed in Iceland (3. tölul.), on income from the use of movables, patents, rights or know-how (6.), on dividends of Icelandic companies (7.) and on interest from Icelandic sources (8.)",
             "70. gr. 3. tölul.: \"a. [20%] af greiðslunni ef um menn er að ræða\"; \"b. [20%] af greiðslunni ef um lögaðila skv. 1. og 2. tölul. 1. mgr. 2. gr. er að ræða\"; c. 37,6% for other legal entities",
             "70. gr. 6. tölul.: 22% af tekjum; 7. tölul.: a. 22% (individuals), b. 20% (legal entities); 8. tölul.: a. 12% (individuals, interest up to 300.000 kr. a year untaxed), b. 12% (legal entities)",
             "bráðabirgðaákvæði LXXVI: 21% / 13% / 38,4% for the operating year 2024 only (assessment 2025); the 2025 rates are those of 70. gr."],
            uns=[(_pay8("services"), "services are taken as performed in Iceland (3. gr. 3. tölul.); recipients other than hf./ehf.-type companies bear 37,6% (70. gr. 3. tölul. c), not separated"),
                 (_ind9("interest"), "the 300.000 kr. annual interest exemption for individuals (70. gr. 8. tölul. a) is not applied"),
                 (_pay8("dividend"), "the dividend deduction for EEA companies (31. gr. 1. mgr. 9. tölul.) is not applied")],
            remaining=[])
    elif cc == "AD":
        _w9(S, "wht", "Impost sobre la renda dels no-residents fiscals (retenció)",
            [("dividend", 0, None, "Llei 94/2010 art. 15 b) (redacció Llei 18/2011): all income from movable capital of art. 13 is exempt: none on dividends"),
             ("interest", 0, None, "Llei 94/2010 art. 15 b) (redacció Llei 18/2011): all income from movable capital of art. 13 is exempt: none on interest"),
             ("royalty", 500, None, "Llei 94/2010 art. 29 c) (redacció Llei 18/2011): cànons 5 per 100"),
             ("services", 1000, None, "Llei 94/2010 art. 10 a), art. 29 a): services used in Andorra, 10 per 100")],
            "Llei 94/2010 de l'impost sobre la renda dels no-residents fiscals art. 10, 13, 15, 29, 34-35 (redacció Llei 18/2011)",
            "BOPA 5/2011 and 80/2011 (later amendments not read)", "B",
            "Llei 94/2010, del 29 de desembre, BOPA núm. 5 (26.1.2011), consellgeneral.ad (`ad/law/llei94_2010.pdf`); Llei 18/2011, BOPA núm. 80 (28.12.2011) (`ad/law/llei18_2011.pdf`)",
            ["art. 29 (Llei 18/2011): \"a) amb caràcter general, el 10 per 100; b) quan es tracti de rendiments derivats d'operacions de reassegurança, l'1,5 per 100\"; c) cànons, \"el 5 per 100\"",
             "art. 15 b) (Llei 18/2011): exempt \"Totes les rendes del capital mobiliari a les quals es refereix l'article 13\" (dividends and interest of Andorran payers)",
             "art. 10 a): services used in Andorra, in particular studies, projects, technical assistance and management support, are income obtained in Andorra; art. 34-35: the payer withholds the tax due",
             "grade B: the 2010 law and its 2011 amendment are read; the 2015 consolidated text and later amendments (Llei 5/2014 IRPF, 2022) are not, so the rates are not confirmed for 2025"],
            uns=[(_pay8("services"), "services are taken as used in Andorra (art. 10 a))")],
            remaining=[])
    elif cc == "SK":
        _w9(S, "wht2", "Daň vyberaná zrážkou (služby, dividendy právnickým osobám)",
            [("services", 1900, None, "zákon 595/2003 § 16 ods. 1 písm. c), § 43 ods. 1 písm. b), ods. 2: 19 % on services provided in Slovakia"),
             ("dividend", 0, True, "zákon 595/2003 § 12 ods. 7 písm. c): a profit share paid to a legal entity is not subject to tax (except to non-cooperative states): none")],
            "zákon 595/2003 Z.z. § 12 ods. 7 písm. c), § 16 ods. 1 písm. c), § 43 ods. 1-2", "znenie od 1.1.2025 (`sk/law/dp_20250101.txt`)", "A",
            "Zákon o dani z príjmov 595/2003 Z.z., Slov-Lex znenie od 1.1.2025 (`sk/law/dp_20250101.txt`)",
            ["§ 16 ods. 1 písm. c): Slovak-source income of non-residents includes services, among them commercial, technical or other advisory, management and intermediation, provided in the territory of the Slovak Republic, even without a permanent establishment",
             "§ 43 ods. 2: the tax on income under § 16 ods. 1 písm. c) to e) items 1, 2, 4, 10 and 12 is collected by withholding; § 43 ods. 1 písm. b): \"19 % z príjmov podľa odsekov 2 a 3\"",
             "§ 12 ods. 7 písm. c): \"Predmetom dane nie je ... podiel na zisku (dividenda)\" of a company, except where paid to or from a taxpayer of a non-cooperative state"],
            uns=[(_pay8("services"), "services are taken as provided in Slovakia (§ 16 ods. 1 písm. c)); 35 % to non-cooperative states (§ 43 ods. 1 písm. c)) not applied"),
                 (_co9("dividend"), "35 % on dividends to legal entities of non-cooperative states not applied")],
            remaining=[])
    elif cc == "BY":
        _w9(S, "wht2", "Налог на доходы иностранных организаций (услуги)",
            [("services", 1500, True, "НК ст. 189 п. 1 пп. 1.12, ст. 192 п. 1 пп. 1.5: 15 % on consulting, accounting, audit, marketing, legal, engineering, management and other listed services")],
            "Налоговый кодекс, Особенная часть, ст. 189 п. 1 пп. 1.12, ст. 192 п. 1 пп. 1.5", "pravo.by via Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`)", "A",
            "Налоговый кодекс Республики Беларусь, Особенная часть, pravo.by via Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`)",
            ["ст. 189 п. 1 пп. 1.12: income of a foreign organisation without a permanent establishment from works and services: 1.12.1 consulting, accounting, audit, marketing, legal, engineering; 1.12.5 management; 1.12.6 staffing; 1.12.10 advertising; 1.12.11 installation and maintenance; 1.12.13 any service to a related party",
             "ст. 192 п. 1 пп. 1.5: \"пятнадцать (15) процентов – по другим доходам, указанным в пункте 1 статьи 189\""],
            uns=[(_co9("services"), "services are taken as one of the kinds listed in ст. 189 п. 1 пп. 1.12 (other services to unrelated parties bear none)"),
                 (_ind9("services"), "services paid to non-resident individuals (подоходный налог, гл. 17) not read (grade C)")],
            remaining=["services to individuals"])
    elif cc == "BA":
        _w9(S, "wht2", "Porez po odbitku (usluge, FBiH)",
            [("services", 1000, True, "Zakon o porezu na dobit FBiH: 10 % withheld on management, technical, educational and consulting service fees paid to non-residents")],
            "Zakon o porezu na dobit Federacije BiH (porez po odbitku)", _pwd9("BA"), "B", _pw9("BA"),
            ["FBiH: tax is withheld at 10 % on fees for management, technical and educational services, market research, tax advice, audit and consulting paid to non-resident legal entities (5 % on dividends; 10 % on interest and royalties)",
             "other service fees are within the tax only when the recipient's state has no treaty with Bosnia and Herzegovina; Republika Srpska and Brčko District each withhold 10 % on their own lists"],
            uns=[(_co9("services"), "services are taken as management, technical or consulting services (other services only for non-treaty residents)"),
                 (_ind9("services"), "services paid to non-resident individuals (porez na dohodak) not read (grade C)")],
            remaining=["services to individuals"])
    elif cc == "ME":
        _w9(S, "wht2", "Porez po odbitku (usluge)",
            [("services", 1500, True, "Zakon o porezu na dobit pravnih lica: 15 % withheld on consulting, market research and audit fees paid to non-residents")],
            "Zakon o porezu na dobit pravnih lica (porez po odbitku)", _pwd9("ME"), "B", _pw9("ME"),
            ["withholding at 15 % covers dividends, interest, royalties and, among services, consulting, market research and audit fees paid to non-residents"],
            uns=[(_co9("services"), "services are taken as consulting, market research or audit services (others bear none)"),
                 (_ind9("services"), "services paid to non-resident individuals (porez na dohodak fizičkih lica) not read (grade C)")],
            remaining=["services to individuals"])
    elif cc == "MD":
        _w9(S, "wht2", "Impozit reținut la sursă (servicii)",
            [("services", 1200, None, "Codul fiscal art. 71, 73: 12 % on other Moldovan-source income of non-residents, services included")],
            "Codul fiscal nr. 1163/1997 art. 71, 73 (non-residents)", _pwd9("MD"), "B", _pw9("MD"),
            ["payments to non-residents: dividends 6 %; all other Moldovan-source income 12 %"],
            uns=[(_pay8("services"), "services are taken as Moldovan-source income (art. 71) taxed at the general 12 % rate")],
            remaining=[])
    elif cc == "NL":
        _w9(S, "wht2", "Geen bronheffing op dienstvergoedingen (lichamen)",
            [("services", 0, True, "Wet Vpb 1969 art. 17 lid 3: the Dutch income of a foreign company is profit of a Dutch enterprise (permanent establishment), an abusive substantial interest or BES profit: none on fees for services")],
            "Wet op de vennootschapsbelasting 1969 art. 17 lid 1-3", "wetten.overheid.nl, geldig op 01-07-2025 (`nl/law/vpb_g2025.txt`)", "A",
            "Wet op de vennootschapsbelasting 1969, wetten.overheid.nl, geldend van 01-01-2025 t/m 31-12-2025 (`nl/law/vpb_g2025.txt`)",
            ["art. 17 lid 1: \"Ten aanzien van buitenlandse belastingplichtigen wordt de belasting geheven naar het belastbare Nederlandse bedrag\"",
             "art. 17 lid 3: the Dutch income is the sum of a. profit of an enterprise carried on with a permanent establishment or representative in the Netherlands, b. income from an abusive substantial interest, c. BES profit; a service fee of a foreign company without a Dutch establishment is none of these",
             "the Wet bronbelasting 2021 reaches interest, royalties and (from 2024) dividends only"],
            uns=[(_co9("services"), "the recipient company is taken to have no permanent establishment in the Netherlands"),
                 (_ind9("services"), "services paid to non-resident individuals: Dutch income from work or other activities (Wet IB 2001 hoofdstuk 7) is taxed by assessment, not withheld; not read (grade C)")],
            remaining=["services to individuals"])
    elif cc == "DK":
        _w9(S, "whti", "Kildeskat, personer (udbytte, renter, royalty, tjenesteydelser)",
            [("dividend", 2700, False, "kildeskatteloven § 2, stk. 1, nr. 6, § 65, stk. 1: udbytteskat 27 pct. of the dividend"),
             ("interest", 0, False, "kildeskatteloven § 2, stk. 1: interest is not among the income of non-resident individuals liable to tax: none"),
             ("royalty", 2200, False, "kildeskatteloven § 2, stk. 1, nr. 8, § 65 C, stk. 1: royaltyskat 22 pct."),
             ("services", 0, False, "kildeskatteloven § 2, stk. 1, nr. 7, stk. 13: fees as adviser or consultant are taxable only for former residents with a share in the management, control or capital of the payer: none otherwise")],
            "kildeskatteloven § 2, stk. 1, nr. 6-8, stk. 13; § 65, stk. 1; § 65 C, stk. 1", "LBK nr 460 af 03/05/2024 (`dk/law/ksl_lbk2024_460.txt`)", "A",
            "Bekendtgørelse af kildeskatteloven, LBK nr 460 af 03/05/2024, retsinformation.dk (`dk/law/ksl_lbk2024_460.txt`)",
            ["§ 65, stk. 1: the distributing company \"skal ... indeholde 27 pct. af det samlede udbytte\" (udbytteskat)",
             "§ 65 C, stk. 1: on royalty to a person or company liable under § 2, stk. 1, nr. 8, or selskabsskatteloven § 2, stk. 1, litra g, the payer \"skal ... indeholde 22 pct. af den samlede royalty\"",
             "§ 2, stk. 1: limited liability of individuals covers work in Denmark (nr. 1-3), a permanent establishment (nr. 4), real property (nr. 5), dividends (nr. 6), adviser fees (nr. 7, limited by stk. 13 to former residents linked to the payer) and royalty (nr. 8); interest is not listed",
             "lov nr. 333 af 9. april 2024 (royalty paid abroad without withholding, in force 1 July 2024) is not incorporated in LBK 460/2024: not read"],
            uns=[(_ind9("dividend"), "27 pct. is the amount withheld; the refund to 15 pct. for residents of information-exchange states is not applied"),
                 (_ind9("services"), "the recipient is taken as never resident in Denmark and without a Danish permanent establishment (§ 2, stk. 1, nr. 4: assessed, not withheld)")],
            remaining=[], drop_uns=[_IND_GC])
    elif cc == "PT":
        _w9(S, "whti", "Retenção na fonte de IRS (não residentes)",
            [("dividend", 2800, False, "CIRS art. 71.º n.º 1 a): taxa liberatória 28 % on capital income obtained in Portugal"),
             ("interest", 2800, False, "CIRS art. 71.º n.º 1 a): taxa liberatória 28 % on capital income obtained in Portugal"),
             ("royalty", 2800, False, "CIRS art. 71.º n.º 1 a): royalties of a holder other than the author are capital income: 28 %"),
             ("services", 2500, False, "CIRS art. 71.º n.º 4 a): taxa liberatória 25 % on business and professional income of non-residents, even from isolated acts")],
            "CIRS art. 71.º n.º 1 a), n.º 4 a)", "Portal das Finanças, código consolidado fetched 2026-11-21 (`pt/law/cirs71.txt`)", "A",
            "Código do IRS art. 71.º, Portal das Finanças (`pt/law/cirs71.txt`)",
            ["n.º 1: \"Estão sujeitos a retenção na fonte a título definitivo, à taxa liberatória de 28 %: a) Os rendimentos de capitais obtidos em território português, por residentes ou não residentes\" paid by entities with organised accounts",
             "n.º 4: \"à taxa liberatória de 25 %\" for non-residents: a) employment income and all business and professional income, even from isolated acts",
             "n.º 17: 35 % on capital income paid to residents of listed low-tax jurisdictions (not applied)"],
            uns=[(_ind9("royalty"), "royalties are taken as received by a holder other than the original author (capital income); an author's royalties are professional income at 25 % (n.º 4 a))"),
                 (_ind9("services"), "services are taken as performed or used in Portugal (CIRS art. 18.º)")],
            remaining=[], drop_uns=[_IND_GC])
    elif cc == "LV":
        _w9(S, "whti", "Iedzīvotāju ienākuma nodoklis, ko ietur no nerezidentiem",
            [("dividend", 0, False, "likums Par IIN 9. panta 1. daļas 2.1 punkts: dividends are not taxable where the company paid UIN on the distributed profit: none"),
             ("interest", 2550, False, "likums Par IIN 3. panta 3. daļas 11. punkts, 15. panta 5. daļa, 17. panta 12. daļa: 25,5 % on interest, withheld at payment"),
             ("royalty", 500, False, "likums Par IIN 3. panta 3. daļas 12. punkta b) apakšpunkts, 15. panta 8. daļa: 5 % on payments for intellectual property other than authors' fees"),
             ("services", 2550, False, "likums Par IIN 3. panta 3. daļas 2. punkts, 15. panta 2. daļas 1. punkts, 17. panta 12. daļa: 25,5 % on income from professional activity for Latvian residents")],
            "likums Par iedzīvotāju ienākuma nodokli 3. panta 3. daļa, 9. panta 1. daļa, 15. panta 2., 5., 8. daļa, 17. panta 12. daļa",
            "likumi.lv, redakcija 2025-07-01 (`lv/law/iin_2025-07-01.txt`)", "A",
            "Likums Par iedzīvotāju ienākuma nodokli, likumi.lv redakcija uz 1.7.2025 (`lv/law/iin_2025-07-01.txt`)",
            ["3. panta 3. daļa: a non-resident's taxable income includes 2) professional activity for Latvian residents in or outside Latvia, 10) dividends unless 9. pants provides otherwise, 11) interest, 12) a) authors' fees and b) payments for other intellectual property",
             "17. panta 12. daļa: on the income in 3. panta 3. daļas 1., 2., 3., 4., ... 10., 11., 12. ... punkts \"nodoklis tiek ieturēts ienākuma izmaksas vietā\"",
             "15. panta 5. daļa: 25,5 % on capital income; 8. daļa: 5 % on 12. punkta b); 7.1 daļa: 25,5 % on authors' fees; 2. daļa: 25,5 % up to the contribution ceiling, 33 % above",
             "9. panta 1. daļas 2.1 punkts: dividends are exempt where UIN was paid on the distributed profit under the Uzņēmumu ienākuma nodokļa likums"],
            uns=[(_ind9("royalty"), "royalties are taken as payments for intellectual property other than authors' fees (authors' fees 25,5 %, 15. panta 7.1 daļa)"),
                 (_ind9("services"), "the 33 % band above the contribution ceiling (15. panta 2. daļas 2. punkts) and the EU/EEA 75 % option are not applied"),
                 (_ind9("dividend"), "dividends are taken as paid from profit on which UIN was paid")],
            remaining=[], drop_uns=[_IND_GC])
    elif cc == "HU":
        _w9(S, "whti", "Személyi jövedelemadó (külföldi magánszemély: osztalék, kamat)",
            [("dividend", 1500, False, "Szja tv. 8. § (1), 66. §: 15 % on dividend income"),
             ("interest", 1500, False, "Szja tv. 8. § (1), 65. §: 15 % on interest income")],
            "1995. évi CXVII. törvény (Szja tv.) 8. § (1), 65. §, 66. §", "Nemzeti Jogtár, hatályos 2026.X.1. (rate unchanged since 2016) (`hu/law/szja.txt`)", "A",
            "1995. évi CXVII. törvény a személyi jövedelemadóról, net.jogtar.hu (`hu/law/szja.txt`)",
            ["8. § (1): \"Az e törvény hatálya alá tartozó jövedelem után az adó mértéke – ha e törvény másként nem rendelkezik – az adóalap 15 százaléka\"; the payer (kifizető) withholds on interest (65. §) and dividends (66. §)",
             "the text read is the version in force from 1 October 2026; the 15 % rate is the one in force in 2025"],
            uns=[(_ind9("interest"), "interest is taken as kamatjövedelem (65. §); interest on a private loan is other income, also 15 % (social contribution tax not applied)"),
                 (_ind9(), "royalties and service fees paid to non-resident individuals (önálló tevékenység: base and source rules) not read (grade C)")],
            remaining=["royalties and services to individuals"], drop_uns=[_IND_GC])
    elif cc == "RU":
        _c9(S, "НК РФ ст. 309 п. 2 (legalacts.ru mirror, ред. 04.08.2026): income of a foreign organisation from works and services in Russia not listed in п. 1 is not taxed at source; п. 1 пп. 9.4 taxes services to a related party (ст. 105.1), its rate and date of entry not read",
            "the rate for ст. 309 п. 1 пп. 9.4 (ст. 284) and a related-party flag on the payment (stake ≥ 25 %); then a 0 rule for the rest")
    elif cc == "BE":
        _c9(S, "no Belgian provision on service fees paid to non-residents is on disk (CIR 92 art. 228 § 3 and the précompte professionnel on non-residents' service income, art. 248, 270)",
            "CIR 92 art. 228 § 3, 248 and 270 (Justel / Fisconetplus text)")
    elif cc == "MT":
        _c9(S, "Cap. 123 read for withholding on payments to non-residents: only investment income (art. 41) and the art. 12 (1) (c) exemptions; a non-resident's Malta-source service income is taxed by return (art. 4), no deduction at source found",
            "the Final Settlement System rules (S.L. 123.13) on payments to non-residents, to confirm that no deduction applies")


# ---------------------------------------------------------------- 2./3. helpers: CIT, VAT, replacing a pass-8 family, C notes
def _cit9(S, key, name, bp, statute, dated, grade, src, facts, uns=(), cond="", lean_extra=""):
    if S.get("fam") != "Corporate" or not any(t.get("grade") == "C" and t.get("tax") == "Corporate income tax" for t in S["taxes"]):
        return
    S.setdefault("families", []); S.setdefault("notes", []); S.setdefault("guards", []); S.setdefault("unsupported", [])
    S["families"] = list(S["families"] or [])
    S["taxes"] = [t for t in S["taxes"] if not (t.get("grade") == "C" and t.get("tax") == "Corporate income tax")]
    S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("1200 Corporate income tax: not modelled")]
    S["lean"] = (S.get("lean") or "") + lean_extra + f"\n/-- {statute} -/\ndef p9{key} : CorpRegime :=\n  {{ name := {_q(name)}, sched := Schedule.flat {bp} }}\n"
    S["families"].append((f"1200 {name} (pass 9)", [".cit"], f"(if g.entity == .company{cond} then [p9{key}.citCharge g.company {_q(statute)}] else [])"))
    S["guards"] += [f"p9{key}.citTax {{ profit := 100000, turnover := 10000000 }} == {bp * 100000 // 10000}",
                    f"p9{key}.citTax {{ profit := 0, turnover := 10000000 }} == 0"]
    S["unsupported"] += list(uns)
    S["notes"].append(f"{S['cc']} 1200 {name} pass 9: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "1200", "tax": name, "statute": statute, "dated": dated, "grade": grade, "kernel_parts": ["CorpRegime"],
                       "unsupported": [t for _, t in uns]})
    S["doc"] += f"\n\n## 1200 {name} (pass 9, grade {grade})\nSource: {src}.\n" + "".join(f"* {x}\n" for x in facts)


def _vat9(S, v, dated, grade, src, facts, uns=(), guards=()):
    if S.get("fam") != "Consumption" or not any(str(t.get("oecd")) == "5111" and t.get("grade") == "C" for t in S["taxes"]):
        return
    S.setdefault("notes", []); S.setdefault("guards", []); S.setdefault("unsupported", [])
    S["taxes"] = [t for t in S["taxes"] if not (str(t.get("oecd")) == "5111" and t.get("grade") == "C")]
    S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("5111 VAT: not modelled")]
    S["vat"] = v
    S["families"] = list(S.get("families") or []) + [(f"5111 {v['name']} (pass 9)", [".vat"],
        "(if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])\n       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])")]
    S["guards"] += list(guards)
    S["unsupported"] += list(uns)
    S["notes"].append(f"{S['cc']} 5111 pass 9: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "5111", "tax": v["name"], "statute": v["statute"], "dated": dated, "grade": grade, "kernel_parts": ["Vat"],
                       "unsupported": [t for _, t in uns]})
    S["doc"] += f"\n\n## 5111 {v['name']} (pass 9, grade {grade})\nSource: {src}.\n" + "".join(f"* {x}\n" for x in facts)


def _drop8(S, fam_prefix, tax_prefix, uns_sub=()):
    """Retire a pass-8 family (its Lean def and guards stay, unused by the model) when pass 9 restates it from the statute."""
    S["families"] = [f for f in S.get("families", []) if not f[0].startswith(fam_prefix)]
    S["taxes"] = [t for t in S["taxes"] if not t.get("tax", "").startswith(tax_prefix)]
    for d in uns_sub:
        S["unsupported"] = [u for u in S["unsupported"] if d not in u[1]]
    S["notes"] = [n for n in S.get("notes", []) if not (" pass 8 " in n and "1200 withholding" in n)]


def _ctried(S, fam, oecd, prefix, tried, unlock):
    if S.get("fam") != fam:
        return
    for t in S["taxes"]:
        if str(t.get("oecd")) == oecd and t.get("grade") == "C" and t.get("tax", "").startswith(prefix):
            t["tried"] = (t.get("tried", "") + "; pass 9: " + tried).lstrip("; ")
            t["unsupported"] = [x for x in t.get("unsupported", []) if not x.startswith("would unlock")] + ["would unlock: " + unlock]
    S["doc"] += f"\n\n## {oecd} {prefix} still grade C (pass 9)\n* {tried}\n* would unlock: {unlock}\n"


_MC_SCOPE = """
/-- OS n° 3.152 art. 1 a): the profits tax applies to an industrial or commercial enterprise whose turnover comes for at
least 25 % from operations made outside Monaco (taken here as the exported share of the company's sales). -/
def mcIsbScope (co : Company) : Bool :=
  let tot := co.sales.foldl (fun a s => a + s.net) 0
  let ex := (co.sales.filter (·.exported)).foldl (fun a s => a + s.net) 0
  tot > 0 && 4 * ex ≥ tot
"""


def _carry9(S):
    cc = S["cc"]
    if cc == "AD":
        _cit9(S, "cit", "Impost sobre societats", 1000, "Llei 95/2010 de l'impost sobre societats art. 41.1 (10 per cent)",
              "BOPA 5/2011 (original text; later amendments not read)", "B",
              "Llei 95/2010, del 29 de desembre, de l'impost sobre societats, consellgeneral.ad (`ad/law/llei95_2010.pdf`)",
              ["art. 41.1: \"El tipus general de gravamen per als obligats tributaris d'aquest impost és del 10 per cent\"; art. 41.2: 0 per cent for collective investment undertakings",
               "grade B: the 2010 text is read; the consolidated text in force for 2025 is not"],
              uns=[("g.entity == .company", "the deductions of art. 43-45 (double taxation, job creation and investment) and the special regimes are not applied")])
        _vat9(S, {"name": "Impost general indirecte", "standard": 450, "reduced": 100, "reduced2": 950, "threshold": 0,
                   "statute": "Llei 11/2012 de l'impost general indirecte art. 57 (4,5 %), 58 (1 %), 59 (0 %), 60 (9,5 %)",
                   "classes": {"food": "reduced", "nonAlcoholic": "reduced", "water": "reduced", "books": "reduced", "newspapers": "reduced",
                               "health": "zero", "education": "zero", "financial": "reduced2"}},
              "BOPA 33/2012 (original text; later amendments not read)", "B",
              "Llei 11/2012, del 21 de juny, de l'impost general indirecte, BOPA núm. 33 (18.7.2012), consellgeneral.ad (`ad/law/llei11_2012.pdf`)",
              ["art. 57: \"El tipus de gravamen general és d'un 4,5%\"; art. 58: reduced 1 % on food and non-alcoholic drinks, water, books, newspapers and magazines, private lessons",
               "art. 59: super-reduced 0 % on hospital and health care by public or conventioned providers, social assistance, education by authorised bodies, sport; art. 60: increased 9,5 % on banking and financial services",
               "grade B: the 2012 text is read; later amendments (for instance a 2,5 % special rate) are not"],
              uns=[("g.consumption.any (fun s => s.good == .health || s.good == .education)", "health and education taken at 0 % (art. 59: only when supplied by public, conventioned or authorised providers)"),
                   ("g.consumption.any (fun s => s.good == .insurance || s.good == .rent)", "insurance and residential rent at the general rate: the exemptions article not read"),
                   ("g.entity == .company", "no registration threshold applied (not read)")],
              guards=["vat.embedded { good := .clothing, amount := 10450 } == 450", "vat.embedded { good := .food, amount := 10100 } == 100",
                      "vat.embedded { good := .financial, amount := 10950 } == 950", "vat.embedded { good := .health, amount := 10000 } == 0"])
    elif cc == "SM":
        _cit9(S, "cit", "Imposta generale sui redditi (persone giuridiche)", 1700, "Legge 16 dicembre 2013 n.166 art. 43 c. 1 (17%)",
              "testo coordinato fino alla Legge 22 dicembre 2025 n.158", "A",
              "Legge 16 dicembre 2013 n.166, testo coordinato (senza note), consigliograndeegenerale.sm documento17086436 (`sm/law/igr_166_2013_coord_senzanote.pdf`)",
              ["art. 43 c. 1: \"L'imposta generale sui redditi di cui al presente Titolo III è determinata applicando l'aliquota proporzionale, nella misura del 17%, al reddito imponibile\"",
               "the coordinated text includes amendments to December 2025; the 17 % rate is the one in force throughout 2025"],
              uns=[("g.entity == .company", "new-business reductions (50 % rate cut for the first five periods) and the reinvested-profit relief (art. 61) are not applied")])
        _w9(S, "wht", "Ritenute alla fonte su redditi corrisposti a non residenti",
            [("dividend", 0, True, "Legge 166/2013 art. 103 c. 6: profits paid to persons other than individuals bear no withholding (recipient's declaration that it does not act for an individual)"),
             ("dividend", 500, False, "Legge 166/2013 art. 103 c. 6: ritenuta a titolo d'imposta del 5% on profits paid to individuals"),
             ("interest", 1300, None, "Legge 166/2013 art. 103 c. 1: ritenuta a titolo d'imposta del 13 per cento on capital income"),
             ("services", 2000, None, "Legge 166/2013 art. 102 c. 1: ritenuta a titolo d'imposta del 20 per cento on fees for self-employed or assimilated services paid to non-residents, also when supplied by a business")],
            "Legge 16 dicembre 2013 n.166 art. 5, 102, 103", "testo coordinato fino alla Legge 22 dicembre 2025 n.158", "A",
            "Legge 16 dicembre 2013 n.166, testo coordinato (senza note), consigliograndeegenerale.sm (`sm/law/igr_166_2013_coord_senzanote.pdf`)",
            ["art. 102 c. 1: payers of fees for self-employed or assimilated services \"a soggetti residenti all'estero, anche quando le prestazioni siano effettuate in regime d'impresa, devono operare una ritenuta a titolo d'imposta del 20 per cento\" (3 % for listed artistic, sports and airport/naval services)",
             "art. 103 c. 1: on capital income paid to persons other than San Marino banks and financial companies \"una ritenuta, a titolo d'imposta e con obbligo di rivalsa, del 13 per cento\"; c. 6: profits to individuals 5 %, to others none",
             "art. 5 c. 2 b): royalties paid by residents are San Marino income; no withholding article for them was found (art. 104 c. 5: 10 % on rentals of equipment used in San Marino)"],
            uns=[(_pay8("services"), "services are taken as self-employed or assimilated services (art. 27); the 3 % rate for listed services is not applied"),
                 (_pay8("interest"), "interest is taken as paid by a non-financial company (art. 103 c. 1); bank interest follows c. 2")],
            remaining=["royalties"])
        _ctried(S, "Consumption", "5111", "VAT", "San Marino has no VAT: imports bear the single-stage imposta monofase; its act was not fetched",
                "the imposta monofase law and its rate decrees")
    elif cc == "MC":
        _cit9(S, "cit", "Impôt sur les bénéfices", 2500, "Ordonnance Souveraine n° 3.152 du 19 mars 1964 art. 1 a), art. 21 (25 % from 1.1.2022)",
              "Legimonaco, Internet Archive capture 2026-05-08", "A",
              "Ordonnance Souveraine n° 3.152 du 19 mars 1964 instituant un impôt sur les bénéfices, Legimonaco via the Internet Archive (`mc/law/legimonaco_isb_wb.txt`)",
              ["art. 1: the tax falls on a) enterprises with an industrial or commercial activity in Monaco \"lorsque leur chiffre d'affaires provient à concurrence de 25 % au moins, d'opérations faites ... en dehors du territoire monégasque\", b) companies whose Monaco activity is collecting royalties from patents, trademarks, processes or literary and artistic property",
               "art. 21: \"À compter du 1er janvier 2022, le taux normal est fixé à 25 %\"",
               "a company below the 25 % test owes no profits tax: the model books none for it"],
              uns=[("g.entity == .company", "the 25 % test is read on the exported share of the company's sales; royalty-collecting companies (art. 1 b)) and the option of other companies are not tested")],
              cond=" && mcIsbScope g.company", lean_extra=_MC_SCOPE)
        if S.get("fam") == "Corporate" and "mcIsbScope" in (S.get("lean") or ""):
            S["guards"] += ["mcIsbScope { sales := [{ good := .other, net := 75, exported := false }, { good := .other, net := 25, exported := true }] } == true",
                            "mcIsbScope { sales := [{ good := .other, net := 76, exported := false }, { good := .other, net := 24, exported := true }] } == false"]
        _c9(S, "OS n° 3.152 (profits tax) read: it contains no withholding on payments abroad; no Monegasque text stating the absence of withholding was found",
            "a Monegasque official text listing the taxes levied (Département des Finances) to cite the absence")
        _ctried(S, "Consumption", "5111", "VAT", "Monaco applies French VAT through its own Code des taxes (1963 customs union); the code was not fetched",
                "Code des taxes sur le chiffre d'affaires, rate articles (Legimonaco)")
    elif cc == "VA":
        _c9(S, "no Vatican text on taxation was found on official sites in pass 9", "an official Vatican City State text stating that no income or withholding tax is levied")
    elif cc == "RO":
        if S.get("fam") == "Corporate" and any(f[0].startswith("1200 Impozit pe veniturile nerezidenților (pass 8)") for f in S.get("families", [])):
            _drop8(S, "1200 Impozit pe veniturile nerezidenților (pass 8)", "Impozit pe veniturile nerezidenților", ["services are taken as rendered in Romania"])
            _w9(S, "wht", "Impozit pe veniturile obținute din România de nerezidenți",
                [("dividend", 1000, None, "Codul fiscal art. 223 (1) a), art. 224 (4) b): 10% on dividends (OUG 156/2024, dividends distributed after 1.1.2025)"),
                 ("interest", 1600, None, "Codul fiscal art. 223 (1) b), art. 224 (4) d): 16% on interest from a resident"),
                 ("royalty", 1600, None, "Codul fiscal art. 223 (1) d), art. 224 (4) d): 16% on royalties from a resident"),
                 ("services", 1600, None, "Codul fiscal art. 223 (1) i), k), art. 224 (4) d): 16% on management or consultancy services from a resident and on services performed in Romania")],
                "Legea 227/2015 privind Codul fiscal art. 223 (1), art. 224 (1), (4)", "Internet Archive capture 2025-05-02 of the consolidated Code (`ro/law/cf_wb20250502.txt`)", "A",
                "Codul fiscal (Legea nr. 227/2015), consolidated text via the Internet Archive, 2025-05-02 (`ro/law/cf_wb20250502.txt`)",
                ["art. 224 (1): the tax due by non-residents on income obtained from Romania \"se calculează, se reține, se declară și se plătește la bugetul de stat de către plătitorii de venituri\"",
                 "art. 224 (4): \"b) 10% pentru veniturile din dividende\"; \"d) 16% în cazul oricăror altor venituri impozabile obținute din România\"; c) 50% for payments to accounts in states without an information-exchange instrument (artificial transactions); c^1) 10% for individuals resident in the EU or a treaty state",
                 "art. 223 (1): Romanian-source income includes dividends, interest and royalties from a resident, management or consultancy services from a resident (i) and services performed in Romania except international transport (k)"],
                uns=[(_pay8("services"), "services are taken as management or consultancy services or services performed in Romania (art. 223 (1) i), k))"),
                     (_ind9(), "the 10% rate for individuals resident in the EU or a treaty state (art. 224 (4) c^1)) is not applied: the input does not give the recipient's state"),
                     ("g.entity == .company && !g.company.paymentsAbroad.isEmpty", "the 50% rate (art. 224 (4) c)) and the EU directive exemptions are not applied")])


# ---------------------------------------------------------------- 5. kernel 2.4.0: annual motor-vehicle taxes (5200)
def _vehtax(S, key, name, lean, ts_name, statute, dated, grade, src, facts, uns, guards, rest):
    """Replace the grade-C 5200 entry by a VehicleTax family (`vehicleTaxCharges <ts> g (firstOnly := true)`), with the
    kernel's grade-C lines for vehicles lacking an attribute or matched by no rule as model-level unsupported entries."""
    if S.get("fam") != "Other" or not any(str(t.get("oecd")) == "5200" and t.get("grade") == "C" for t in S["taxes"]):
        return
    S.setdefault("families", []); S.setdefault("notes", []); S.setdefault("guards", []); S.setdefault("unsupported", [])
    S["families"] = list(S["families"] or [])
    S["imports"] = sorted(set(S.get("imports", []) + ["TaxKernel.Global2"]))
    S["taxes"] = [t for t in S["taxes"] if not (str(t.get("oecd")) == "5200" and t.get("grade") == "C")]
    S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("5200")]
    S["lean"] = (S.get("lean") or "") + lean
    S["families"].append((f"5200 {name} (pass 9)", [".useOfGoods"], f"vehicleTaxCharges {ts_name} g (firstOnly := true)"))
    S["unsupported"] += [(f"!(vehicleTaxUnknown {_q(name)} {ts_name} g).isEmpty", f"5200 {name}: a vehicle lacks an attribute the rate needs (grade C)"),
                         (f"!(vehicleTaxUnmatched {_q(name)} {ts_name} g).isEmpty", f"5200 {name}: a vehicle no rule reaches: {rest} (grade C)")] + list(uns)
    S["guards"] += list(guards)
    S["notes"].append(f"{S['cc']} 5200 {name} pass 9: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "5200", "tax": name, "statute": statute, "dated": dated, "grade": grade,
                       "kernel_parts": ["VehicleTax (2.4.0)", "QtyTable"], "unsupported": [rest] + [t for _, t in uns]})
    S["taxes"].append({"oecd": "5200", "tax": "Other taxes on use of goods (rest)", "statute": "", "dated": "", "grade": "C", "status": "unsupported",
                       "kernel_parts": [], "tried": "pass 9: the main annual vehicle tax is modelled; other 5200 items not read",
                       "unsupported": ["registration taxes, licences and permits other than the one modelled"]})
    S["doc"] += f"\n\n## 5200 {name} (pass 9, kernel 2.4.0, grade {grade})\nSource: {src}.\n" + "".join(f"* {x}\n" for x in facts)


_DE_VEH = """
/-- KraftStG § 9 (1) Nr. 2 b, c: 2 EUR (Fremdzündung) per started 100 cm³ -/
def p9deCcmP : QtyTable := { step := 100, steps := [(0, 2)], den := 100 }
/-- KraftStG § 9 (1) Nr. 2 b, c: 9,50 EUR (Selbstzündung) per started 100 cm³ -/
def p9deCcmD : QtyTable := { step := 100, steps := [(0, 950)], den := 10000 }
/-- KraftStG § 9 (1) Nr. 2 c: per g CO2/km above 95: 2,00 / 2,20 / 2,50 / 2,90 / 3,40 / 4,00 EUR -/
def p9deCo2c : QtyTable := { steps := [(95, 200), (115, 220), (135, 250), (155, 290), (175, 340), (195, 400)], den := 100 }
/-- KraftStG § 9 (1) Nr. 2 b: 2 EUR per g CO2/km above the threshold of the year of first registration -/
def p9deCo2b (thr : Int) : QtyTable := { steps := [(thr, 200)], den := 100 }
def p9deCar (fs : List VehicleFuel) (ccm co2 : QtyTable) (f t : Nat) (st : String) : VehicleTax :=
  { name := "Kraftfahrzeugsteuer", kinds := ["car"], fuels := fs, regFrom := f, regTo := t,
    parts := [(.engineCcm, ccm), (.co2GKm, co2)], statute := st }
def p9dePetrol : List VehicleFuel := [.petrol, .lpg, .cng]
def p9deVeh : List VehicleTax :=
  [p9deCar p9dePetrol p9deCcmP p9deCo2c 2021 0 "KraftStG § 9 (1) Nr. 2 c (Fremdzündung)",
   p9deCar [.diesel] p9deCcmD p9deCo2c 2021 0 "KraftStG § 9 (1) Nr. 2 c (Selbstzündung)",
   p9deCar p9dePetrol p9deCcmP (p9deCo2b 95) 2014 2020 "KraftStG § 9 (1) Nr. 2 b cc (Fremdzündung, über 95 g/km)",
   p9deCar [.diesel] p9deCcmD (p9deCo2b 95) 2014 2020 "KraftStG § 9 (1) Nr. 2 b cc (Selbstzündung, über 95 g/km)",
   p9deCar p9dePetrol p9deCcmP (p9deCo2b 110) 2012 2013 "KraftStG § 9 (1) Nr. 2 b bb (Fremdzündung, über 110 g/km)",
   p9deCar [.diesel] p9deCcmD (p9deCo2b 110) 2012 2013 "KraftStG § 9 (1) Nr. 2 b bb (Selbstzündung, über 110 g/km)",
   p9deCar p9dePetrol p9deCcmP (p9deCo2b 120) 2009 2011 "KraftStG § 9 (1) Nr. 2 b aa (Fremdzündung, über 120 g/km)",
   p9deCar [.diesel] p9deCcmD (p9deCo2b 120) 2009 2011 "KraftStG § 9 (1) Nr. 2 b aa (Selbstzündung, über 120 g/km)",
   { name := "Kraftfahrzeugsteuer", kinds := ["car"], fuels := [.electric], regFrom := 2016,
     statute := "KraftStG § 3d (1): Elektrofahrzeuge first registered 18.5.2011-31.12.2030 exempt for ten years (to 31.12.2035 at most)" }]
"""

_UK_VED = """
/-- VERA 1994 Sch. 1 para. 1GC Table 1 (first licence, cars first registered on or after 1 April 2017; licences from 1.4.2025) -/
def p9ukFirst : QtyTable := QtyTable.ofCeilings [(0, 10), (50, 110), (75, 130), (90, 270), (100, 350), (110, 390), (130, 440),
  (150, 540), (170, 1360), (190, 2190), (225, 3300), (255, 4680)] 5490
/-- VERA 1994 Sch. 1 para. 1B table (cars first registered 1 March 2001 - 31 March 2017; licences from 1.4.2025) -/
def p9uk1B : QtyTable := QtyTable.ofCeilings [(100, 20), (110, 20), (120, 35), (130, 165), (140, 195), (150, 215), (165, 265),
  (175, 315), (185, 345), (200, 395), (225, 430), (255, 735)] 760
/-- para. 1B, cars first registered before 23 March 2006: 430 in the last two rows -/
def p9uk1B06 : QtyTable := QtyTable.ofCeilings [(100, 20), (110, 20), (120, 35), (130, 165), (140, 195), (150, 215), (165, 265),
  (175, 315), (185, 345), (200, 395), (225, 430), (255, 430)] 430
def p9ukVed : List VehicleTax :=
  [{ name := "Vehicle excise duty", kinds := ["car"], occasion := .registration, regFrom := 2017,
     parts := [(.co2GKm, p9ukFirst)], statute := "VERA 1994 Sch. 1 para. 1GC (2), Table 1 (first vehicle licence)" },
   { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2020, fixed := 620,
     when := [(.value, 40000, 1000000000000), (.co2GKm, 0, 1000000)],
     statute := "VERA 1994 Sch. 1 para. 1GE (2): £620 where the price exceeds £40,000 and the car is under six years old" },
   { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2017, fixed := 195,
     statute := "VERA 1994 Sch. 1 para. 1GD (1): £195" },
   { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2001, regTo := 2005,
     parts := [(.co2GKm, p9uk1B06)], statute := "VERA 1994 Sch. 1 para. 1B (registered before 23 March 2006)" },
   { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2001, regTo := 2016,
     parts := [(.co2GKm, p9uk1B)], statute := "VERA 1994 Sch. 1 para. 1B" }]
"""


def _veh9(S):
    cc = S["cc"]
    if cc == "DE":
        _vehtax(S, "deveh", "Kraftfahrzeugsteuer", _DE_VEH, "p9deVeh",
                "KraftStG 2002 § 9 (1) Nr. 2 b, c; § 3d (1)", "gesetze-im-internet.de, fetched 2026-11-21", "A",
                "Kraftfahrzeugsteuergesetz 2002 §§ 3d, 9, 11, gesetze-im-internet.de (`de/law/kraftstg_9.txt`, `kraftstg_3d.txt`, `kraftstg_11.txt`)",
                ["§ 9 (1) Nr. 2 c (first registration from 1.1.2021): \"für je 100 Kubikzentimeter Hubraum oder einem Teil davon 2 Euro für Fremdzündungsmotoren und 9,50 Euro für Selbstzündungsmotoren\" plus per g CO2/km above 95: 2,00 EUR to 115, 2,20 to 135, 2,50 to 155, 2,90 to 175, 3,40 to 195, 4,00 above",
                 "§ 9 (1) Nr. 2 b (1.7.2009-31.12.2020): the same cm³ rates plus 2 EUR per g/km above 120 (to 2011), 110 (from 2012), 95 (from 2014)",
                 "§ 3d (1): electric vehicles first registered 18.5.2011-31.12.2030 are exempt for ten years, at most to 31.12.2035",
                 "Germany's motor-vehicle tax is federal; it is modelled for cars, in whole euros, for the months held"],
                [("g.vehicles.any (fun v => v.firstRegYear == 2009)", "5200 Kraftfahrzeugsteuer: a car first registered in 2009 is taken under § 9 (1) Nr. 2 b (only from 1 July 2009; earlier: Nr. 2 a)"),
                 ("g.vehicles.any (fun v => v.fuel == .electric && v.firstRegYear == 2015)", "5200 Kraftfahrzeugsteuer: an electric car of 2015 leaves the § 3d exemption during 2025 (not split)")],
                ["p9deCcmP.amount 1598 == 32", "p9deCcmD.amount 1968 == 190", "p9deCo2c.amount 150 == 121", "p9deCo2c.amount 95 == 0",
                 "(p9deVeh.head!).amount 2025 { kind := \"car\", engineCcm := 1598, co2GKm := 150, fuel := .petrol, firstRegYear := 2022 } == 153",
                 "(p9deVeh[1]!).amount 2025 { kind := \"car\", engineCcm := 1968, co2GKm := 130, fuel := .diesel, firstRegYear := 2023 } == 263",
                 "(p9deVeh[2]!).amount 2025 { kind := \"car\", engineCcm := 1395, co2GKm := 120, fuel := .petrol, firstRegYear := 2016 } == 78"],
                "cars first registered before 2009 (Euro-class rates, § 9 (1) Nr. 2 a), hybrids (engine type not given), electric cars of 2011-2015 (weight rates, § 9 (2)), motorcycles, motor caravans, vans and lorries")
    elif cc == "UK":
        _vehtax(S, "ukved", "Vehicle excise duty", _UK_VED, "p9ukVed",
                "Vehicle Excise and Registration Act 1994 Sch. 1 paras. 1B, 1GC, 1GD, 1GE", "legislation.gov.uk point in time 01/06/2025 (licences from 1.4.2025)", "A",
                "Vehicle Excise and Registration Act 1994, Schedule 1, legislation.gov.uk, point-in-time view as at 01/06/2025 (`uk/law/vera1994_sch1_20250601.txt`)",
                ["para. 1GC: the first licence of a car first registered on or after 1 April 2017 is charged by CO2 (Table 1): 0 g £10, to 50 g £110, to 75 £130, to 90 £270, to 100 £350, to 110 £390, to 130 £440, to 150 £540, to 170 £1,360, to 190 £2,190, to 225 £3,300, to 255 £4,680, above £5,490",
                 "para. 1GD: later licences \"£195\"; para. 1GE: \"£620\" where the price exceeds £40,000 and the car was first registered less than six years before (if registered before 1 April 2025, only with CO2 above 0)",
                 "para. 1B (cars registered 1 March 2001 - 31 March 2017): £20 to 110 g, £35 to 120, £165, £195, £215, £265, £315, £345, £395, £430, £735 (225-255), £760 above; £430 in the last two rows for cars first registered before 23 March 2006"],
                [("g.vehicles.any (fun v => v.fuel == .diesel && v.newReg)", "5200 Vehicle excise duty: a new diesel car is taken as meeting Euro 6d (Table 2 for other diesels not applied)"),
                 ("g.vehicles.any (fun v => v.firstRegYear == 2017 || v.firstRegYear == 2006 || v.firstRegYear == 2001)", "5200 Vehicle excise duty: registration-year boundaries (1 April 2017, 23 March 2006, 1 March 2001) are taken by calendar year"),
                 ("g.vehicles.any (fun v => v.firstRegYear ≥ 2020)", "5200 Vehicle excise duty: the £40,000 supplement is applied to cars first registered from 2020 (six years read by calendar year); the vehicle's value is taken as its list price"),
                 ("g.vehicles.any (fun v => v.firstRegYear ≥ 2020 && v.value < 0)", "5200 Vehicle excise duty: a car first registered from 2020 has no price: the £40,000 supplement (para. 1GE) is not tested and £195 is booked")],
                ["p9ukFirst.amount 0 == 10", "p9ukFirst.amount 120 == 440", "p9ukFirst.amount 256 == 5490", "p9uk1B.amount 150 == 215", "p9uk1B06.amount 260 == 430",
                 "(p9ukVed[2]!).amount 2025 { kind := \"car\", co2GKm := 120, fuel := .petrol, firstRegYear := 2019 } == 195"],
                "cars first registered before March 2001 (engine-size rates, para. 1), motorcycles, vans, lorries and other vehicles")


# ---------------------------------------------------------------- driver
def p9_rows(S):
    for f in (_wht9, _carry9, _veh9):
        f(S)
