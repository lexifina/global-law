# pass 8 rows (R1 Europe, 2026-11-21): kernel 2.3.0 withholding (cited rates and zeros), P5/P6 gaps, P7 surcharges,
# carry-overs. exec'd by the spec after p6lib.py and p7_rows.py (helpers p6_*, _drop, _q, _tax, _doc, pwc).
# Statute rows quote or cite the act read (grade A); PwC rows (grade B) state facts only, with the provenance line.

def _pwh8(cc, name="pwc_wht_wb2025"):
    return pwc(cc, name, "Corporate - Withholding taxes")


def _first8(rules, kind, toc, stake):
    for r in rules:
        k, bp, tc, st = r[:4]
        ms = r[4] if len(r) > 4 else 0
        if k == kind and (tc is None or tc == toc) and ms <= stake:
            return bp
    return None


def _w8(S, key, name, rules, title, dated, grade, src, facts, uns=(), remaining=None, replace_absent=False, solz=False):
    """1200 withholding on payments abroad (pass 8, kernel 2.3.0): a Wht family of its own holding only the kinds no
    earlier family computes. rules = [(kind, rateBp, toCompany None/True/False, statute[, minStakeBp])], most specific
    first (first match). A 0 rate is a cited statutory zero (a covered 0). remaining = kinds still unread (their grade-C
    entry is kept, renamed); [] drops the grade-C withholding entries. solz: the DE Solidaritätszuschlag (5,5 % of each
    withheld amount) as a second withheld charge on the same payment."""
    if S.get("fam") != "Corporate":
        return
    S.setdefault("families", []); S.setdefault("notes", []); S.setdefault("guards", []); S.setdefault("unsupported", [])
    S["lean"] = S.get("lean") or ""
    tcl = lambda tc: "none" if tc is None else ("some true" if tc else "some false")
    rl = ",\n    ".join(f"{{ kind := .{r[0]}, toCompany := {tcl(r[2])}, minStakeBp := {r[4] if len(r) > 4 else 0}, rateBp := {r[1]}, statute := {_q(r[3])} }}" for r in rules)
    S["lean"] += f"\n/-- {title} -/\ndef p8{key} : Wht :=\n  {{ name := {_q(name)}, rules := [\n    {rl}] }}\n"
    S["families"].append((f"1200 {name} (pass 8)", [".cit"], f"(if g.entity == .company then p8{key}.charges g.company else [])"))
    if solz:
        S["lean"] += (f"/-- SolZG § 3 (1) Nr. 5-6, § 4: 5,5 % of the Kapitalertragsteuer / Abzugsteuer withheld -/\n"
                      f"def p8{key}SolZ (co : Company) : List Charge :=\n"
                      f"  (co.paymentsAbroad.zipIdx.filter fun (p, _) => p8{key}.amount p > 0).map fun (p, i) =>\n"
                      f"    charge (if p.toCompany then .cit else .pit) \"Solidaritätszuschlag (Abzugsteuern)\" (p8{key}.amount p) id\n"
                      f"      (fun x => divR .down (550 * x) BP) (event := s!\"payment {{i + 1}} ({{p.kind.name}})\") (bearer := .withheld)\n"
                      f"      (statute := \"SolZG § 3 (1) Nr. 5 und 6, § 4 Satz 1 (5,5 %)\")\n")
        S["families"].append((f"1200 Solidaritätszuschlag on withholding (pass 8)", [".cit"], f"(if g.entity == .company then p8{key}SolZ g.company else [])"))
    seen = set()
    for r in rules:
        k, tc, ms = r[0], r[2], (r[4] if len(r) > 4 else 0)
        for toc in ([True, False] if tc is None else [tc]):
            if (k, toc, ms) in seen:
                continue
            seen.add((k, toc, ms))
            v = _first8(rules, k, toc, ms)
            S["guards"].append(f"p8{key}.amount {{ kind := .{k}, amount := 100000, toCompany := {'true' if toc else 'false'}, stakeBp := {ms} }} == {v * 100000 // 10000}")
            if solz and v:
                S["guards"].append(f"(p8{key}SolZ {{ paymentsAbroad := [{{ kind := .{k}, amount := 100000, toCompany := {'true' if toc else 'false'}, stakeBp := {ms} }}] }}).map (·.due) == [{550 * (v * 100000 // 10000) // 10000}]")
    S["unsupported"] += [(c, "1200 withholding: " + t) for c, t in uns]
    if replace_absent:
        S["taxes"] = [t for t in S["taxes"] if not (str(t.get("oecd")) == "1200" and t.get("status") == "absent" and "ithholding" in t.get("tax", ""))]
    if remaining is not None:
        cs = [t for t in S["taxes"] if t.get("grade") == "C" and "ithholding" in t.get("tax", "")]
        S["taxes"] = [t for t in S["taxes"] if t not in cs]
        S["unsupported"] = [u for u in S["unsupported"] if not ("ithholding" in u[1] and "grade C" in u[1])]
        if remaining:
            S["taxes"].append({"oecd": "1200", "tax": "Withholding on " + ", ".join(remaining) + " paid abroad", "statute": "not read", "dated": "",
                               "grade": "C", "status": "unsupported", "kernel_parts": [],
                               "tried": "pass 8: no statute or official/secondary source on disk states the rule for these kinds",
                               "unsupported": ["kernel 2.3.0 lists each such payment as \"no rule read (grade C)\""]})
    kinds = sorted({r[0] for r in rules})
    zeros = sorted({r[0] for r in rules if r[1] == 0})
    S["notes"].append(f"{S['cc']} 1200 withholding pass 8 ({', '.join(kinds)}): {dated} (grade {grade})")
    S["taxes"].append({"oecd": "1200", "tax": f"{name} ({', '.join(kinds)})", "statute": title, "dated": dated, "grade": grade,
                       "kernel_parts": ["Wht"] + (["WhtRule.zero (cited)"] if zeros else []) + (["SolZ on the withheld amount"] if solz else []),
                       "unsupported": [t for _, t in uns] + ["treaty rates and EU directives out of scope (statutory, treaty-free)"]})
    S["doc"] += f"\n\n## 1200 {name}: {', '.join(kinds)} (pass 8, grade {grade})\nSource: {src}.\n" + "".join(f"* {x}\n" for x in facts)


def _pay8(kind):
    return f"g.entity == .company && g.company.paymentsAbroad.any (·.kind == .{kind})"


def _pay8i(kind):
    return f"g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .{kind} && !p.toCompany)"


# ---------------------------------------------------------------- per country (only kinds left unread by earlier families)
def _wht8(S):
    cc = S["cc"]
    if S.get("fam") != "Corporate":
        return
    if cc == "AT":
        _w8(S, "wht", "Abzugsteuer / KESt on payments abroad",
            [("interest", 0, None, "EStG 1988 § 98 (1) Z 5 lit. b: interest of non-residents is taxable only where KESt was withheld (bank and securities interest), never for non-individuals or residents of states with automatic exchange of information: none on a company's loan interest"),
             ("royalty", 2000, None, "EStG 1988 § 99 (1) Z 3, § 100 (1): Abzugsteuer 20 % on royalties (§ 28 (1) Z 3)"),
             ("services", 2000, None, "EStG 1988 § 99 (1) Z 5, § 100 (1): Abzugsteuer 20 % on commercial or technical consulting carried out in Austria")],
            "EStG 1988 § 98 (1) Z 5 lit. b, § 99 (1) Z 3 and Z 5, § 100 (1)", "RIS Fassung vom 01.07.2025", "A",
            "EStG 1988, RIS Bundesrecht konsolidiert, Fassung vom 01.07.2025 (`at/law/estg_2025-07-01.txt`)",
            ["§ 100 (1): \"Die Abzugsteuer gemäß § 99 beträgt 20%\" (27,5 % only for § 99 (1) Z 6 and 7)",
             "§ 99 (1) Z 3 royalties listed in § 28 (1) Z 3; Z 5 \"Einkünften aus im Inland ausgeübter kaufmännischer oder technischer Beratung\"",
             "§ 98 (1) Z 5 lit. b: interest is limited-liability income only where KESt was withheld; excluded: \"(Stück)Zinsen, die nicht von natürlichen Personen erzielt werden\" and residents of automatic-exchange states"],
            uns=[(_pay8("services"), "services are taken as commercial or technical consulting carried out in Austria (§ 99 (1) Z 5): other services, or consulting done abroad, bear none"),
                 (_pay8("royalty"), "§ 99a exemption for royalties to associated EU companies not applied")],
            remaining=[])
    elif cc == "BG":
        _w8(S, "wht", "Данък при източника (технически услуги)",
            [("services", 1000, None, "ЗКПО чл. 12 (5) т. 4, чл. 195 (1), § 1 т. 9 ДР: fees for technical services (installation, consulting, marketing research) of Bulgarian source, 10 %")],
            "ЗКПО чл. 12 (5) т. 4, чл. 195 (1), § 1 т. 9 ДР; rate 10 % as for the other чл. 195 income", "ЗКПО as on lex.bg (`bg/law/zkpo.txt`); rate: " + _pwh8("BG"), "B",
            "Закон за корпоративното подоходно облагане (`bg/law/zkpo.txt`); " + _pwh8("BG"),
            ["чл. 12 (5) т. 4: \"възнаграждения за технически услуги\" paid by Bulgarian payers are Bulgarian-source income; чл. 195 (1): withheld on such income of foreign legal entities without a place of business",
             "§ 1 т. 9: technical services are installation of tangible assets and services of a consulting nature and market research"],
            uns=[(_pay8("services"), "services are taken as technical services (§ 1 т. 9 ДР); other services bear none")], remaining=[])
    elif cc == "CH":
        _w8(S, "wht2", "Verrechnungssteuer (royalties, services)",
            [("royalty", 0, None, "VStG Art. 4 (1): the objects are income of bonds, shares and similar participations, collective investments and customer deposits: none on royalties"),
             ("services", 0, None, "VStG Art. 4 (1): none on service fees (not an object of the tax)")],
            "VStG Art. 4 (1) (objects of the Verrechnungssteuer)", "SR 642.21, Fassung 01.01.2025 (`ch/law/vstg_20250101.txt`)", "A",
            "Bundesgesetz über die Verrechnungssteuer, fedlex Fassung vom 1. Januar 2025 (`ch/law/vstg_20250101.txt`)",
            ["Art. 4 (1): the Verrechnungssteuer on income from movable capital falls on interest, annuities, profit shares and other income of bonds and similar debt, of shares, GmbH and cooperative shares, of collective investments and of customer deposits with Swiss banks; licence fees and service fees are not listed"],
            uns=[("g.entity == .company && g.company.paymentsAbroad.any (fun p => (p.kind == .royalty || p.kind == .services) && !p.toCompany)", "cantonal source taxes on certain income of non-resident individuals (DBG Art. 91-97: performers, board fees) not read")],
            remaining=[])
    elif cc == "CZ":
        _w8(S, "wht2", "Srážková daň (služby)",
            [("services", 1500, None, "ZDP § 22 odst. 1 písm. c), § 36 odst. 1 písm. a) bod 1: 15 % on services provided in the Czech Republic (commercial, technical and other advisory, management, intermediation)")],
            "ZDP § 22 odst. 1 písm. c), § 36 odst. 1 písm. a) bod 1", "zákon 586/1992 Sb., znění k 1.7.2025 (`cz/law/zdp_zneni-20250701.txt`)", "A",
            "Zákon o daních z příjmů 586/1992 Sb., zákony pro lidi, znění od 1.7.2025 (`cz/law/zdp_zneni-20250701.txt`)",
            ["§ 22 (1) c): Czech-source income of non-residents includes \"příjmy ze služeb ... příjmy z obchodního, technického nebo jiného poradenství, řídicí a zprostředkovatelské činnosti a obdobných činností poskytovaných na území České republiky\"",
             "§ 36 (1) a) 1.: the special rate is 15 % on income under § 22 (1) c); c): 35 % for residents outside the EU/EEA without a treaty or exchange agreement"],
            uns=[(_pay8("services"), "services are taken as provided in the Czech Republic (§ 22 (1) c)); the 35 % rate for non-treaty, non-EU/EEA residents (§ 36 (1) c)) is not applied")], remaining=[])
    elif cc == "ES":
        _w8(S, "wht2", "IRNR retención (servicios)",
            [("services", 2400, None, "TRLIRNR art. 13.1 b), 25.1 a), 31: 24 % on services provided or used in Spain (19 % for EU/EEA residents)")],
            "TRLIRNR (RDLeg. 5/2004) art. 13.1 b), 24.2, 25.1 a), 31", "BOE texto consolidado (`es/law/trlirnr.txt`)", "A",
            "Texto refundido de la Ley del IRNR, BOE consolidado (`es/law/trlirnr.txt`)",
            ["art. 25.1 a): \"Con carácter general el 24 por 100\"; 19 por ciento for residents of another EU/EEA state with effective exchange of information",
             "art. 24.2: for services, technical assistance and installation work the base is income less personnel and material costs"],
            uns=[(_pay8("services"), "services are taken as provided or used in Spain and the recipient outside the EU/EEA (24 %); the art. 24.2 net base and the 19 % EU/EEA rate are not applied")], remaining=[])
    elif cc == "HR":
        _w8(S, "wht2", "Porez po odbitku (usluge)",
            [("services", 0, None, "Zakon o porezu na dobit čl. 31 (NN 114/2023): consulting, market research and audit services bear withholding (25 %) only when paid to EU non-cooperative jurisdictions; none otherwise")],
            "Zakon o porezu na dobit čl. 31 (izmjena NN 114/2023, st. 12)", "NN 114/2023; " + _pwh8("HR").split(", accessed ")[1].split(" (")[0], "B",
            "Zakon o izmjenama Zakona o porezu na dobit, NN 114/2023 (`hr/law/nn2023_114_1613_dobit.txt`); " + _pwh8("HR"),
            ["NN 114/2023 čl. 31 st. 12: 25 % on market research, tax and business consulting and audit services when paid to persons in states listed by the EU as non-cooperative and without a treaty",
             "PwC: these services are within Croatian withholding only in that case"],
            uns=[(_pay8("services"), "services are taken as paid to a cooperative jurisdiction (0); 25 % for EU-listed non-cooperative jurisdictions not applied")], remaining=[])
    elif cc == "LT":
        _w8(S, "wht2", "Pelno mokestis prie šaltinio (paslaugos)",
            [("services", 0, True, "PMĮ 4 str. 4 d. (Lithuanian-source income of foreign entities without a PE: interest, distributed profit, royalties, real estate, copyright compensation, performers and sport, supervisory board): service fees not listed, none")],
            "Pelno mokesčio įstatymas 4 str. 4 d., 5 str. 2 d. 2 p.", "redakcija nuo 2025-01-01 (`lt/law/pmi_ed20250101_wb.txt`)", "A",
            "Pelno mokesčio įstatymas, e-TAR redakcija nuo 2025-01-01 (`lt/law/pmi_ed20250101_wb.txt`)",
            ["4 str. 4 d.: the Lithuanian-source income of a foreign entity not through a PE is listed in items 1-7 (interest; distributed profit; royalties; real estate; copyright compensation; performers and sport; supervisory board fees)",
             "5 str. 2 d. 2 p.: items 3 and 5 at 10 %, items 4, 6 and 7 at 16 %"],
            uns=[(_pay8i("services"), "services paid to non-resident individuals: Gyventojų pajamų mokesčio įstatymas not read (grade C)")], remaining=[])
    elif cc == "PL":
        _w8(S, "wht2", "Zryczałtowany podatek (odsetki, należności licencyjne, usługi)",
            [("interest", 2000, True, "ustawa o CIT art. 21 ust. 1 pkt 1: 20 % on interest"),
             ("royalty", 2000, True, "ustawa o CIT art. 21 ust. 1 pkt 1: 20 % on royalties and know-how"),
             ("services", 2000, True, "ustawa o CIT art. 21 ust. 1 pkt 2a: 20 % on advisory, accounting, market research, legal, advertising, management and control, data processing, recruitment and guarantee services"),
             ("interest", 1900, False, "ustawa o PIT art. 30a ust. 1 pkt 1-2: 19 % on loan and securities interest"),
             ("royalty", 2000, False, "ustawa o PIT art. 29 ust. 1 pkt 1: 20 % on royalties"),
             ("services", 2000, False, "ustawa o PIT art. 29 ust. 1 pkt 5: 20 % on advisory, accounting, market research, legal, advertising, management services")],
            "ustawa o CIT art. 21 ust. 1 pkt 1, 2a; ustawa o PIT art. 29 ust. 1 pkt 1, 5, art. 30a ust. 1 pkt 1-2", "teksty jednolite 2025 (`pl/law/cit_tj2025.txt`, `pl/law/pit_tj2025.txt`)", "A",
            "Ustawa o podatku dochodowym od osób prawnych (t.j. 2025, `pl/law/cit_tj2025.txt`) and od osób fizycznych (t.j. 2025, `pl/law/pit_tj2025.txt`)",
            ["CIT art. 21 ust. 1: interest, royalties (pkt 1) and the listed intangible services (pkt 2a) \"ustala się w wysokości 20 % przychodów\"",
             "PIT art. 29 ust. 1 pkt 1 and 5: \"20 % przychodu\"; art. 30a ust. 1: \"19 % zryczałtowany podatek dochodowy\" on loan interest (pkt 1) and securities interest (pkt 2)"],
            uns=[(_pay8("services"), "services are taken as the intangible services listed in CIT art. 21 ust. 1 pkt 2a / PIT art. 29 ust. 1 pkt 5; other services bear none"),
                 ("g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest || p.kind == .royalty)", "the art. 21 ust. 3 exemption for EU associated companies and the 2 000 000 zł pay-and-refund threshold (art. 26 ust. 2e) not applied")],
            remaining=[])
    elif cc == "UK":
        _w8(S, "wht2", "Income tax deducted at source (dividends, services)",
            [("dividend", 0, None, "ITA 2007 Part 15: no duty to deduct income tax from dividends of companies (Chapter 5 covers only UK public revenue dividends)"),
             ("services", 0, None, "ITA 2007 Part 15: no duty to deduct income tax from service fees (chapters cover interest, building society securities, public revenue dividends, annual payments and royalties, manufactured payments)")],
            "Income Tax Act 2007 Part 15 (Deduction of income tax at source), Chapters 3-18", "legislation.gov.uk contents fetched 2026-11-21 (`uk/law/ita2007_contents.txt`)", "A",
            "Income Tax Act 2007, legislation.gov.uk table of contents (`uk/law/ita2007_contents.txt`); ss. 874, 906 already modelled (`uk/law/ita2007_s874_2025-07-01.txt`)",
            ["Part 15 chapters: 3 yearly interest; 4 building society securities; 5 UK public revenue dividends; 6 annual payments and patent royalties; 7 other intellectual property; 9 manufactured payments; 10 non-commercial payments by companies; 18 other regimes: none on company dividends or service fees"],
            uns=[(_pay8("services"), "the construction industry scheme (FA 2004 ss. 57-77) applies only to construction payments: not modelled")], remaining=[])
    elif cc == "XK":
        _w8(S, "wht2", "Withholding tax (dividends, services)",
            [("dividend", 0, None, "Law on CIT: dividends paid to non-residents bear no withholding (0 %)"),
             ("services", 500, None, "Law on CIT: services provided by non-residents 5 %")],
            "Ligji për tatimin në të ardhurat e korporatave (withholding on non-residents)", _pwh8("XK").split(", accessed ")[1].split(" (")[0], "B", _pwh8("XK"),
            ["non-treaty rates: dividends 0 %, interest 10 %, royalties 10 %; services provided by non-residents 5 %"], remaining=[])
    elif cc == "AL":
        _w8(S, "wht2", "Withholding tax (services)",
            [("services", 1500, None, "Law on income tax: 15 % of the gross fee for technical or managerial services, installation, assembly or supervision")],
            "Ligji për tatimin mbi të ardhurat (withholding on non-residents)", _pwh8("AL", "pwc_wht_live").split(", accessed ")[1].split(" (")[0], "B", _pwh8("AL", "pwc_wht_live"),
            ["15 % of the gross fee for technical or managerial services, installation, assembly or supervision; also on pay to managers and board members"],
            uns=[(_pay8("services"), "services are taken as technical or management services; others not separated")], remaining=[])
    elif cc == "MK":
        _w8(S, "wht2", "Данок по одбивка (технички услуги)",
            [("services", 1000, None, "Закон за данокот на добивка: 10 % on fees for managerial, technical and consulting services")],
            "Закон за данокот на добивка (withholding on non-residents)", _pwh8("MK").split(", accessed ")[1].split(" (")[0], "B", _pwh8("MK"),
            ["10 % on gross income from royalties and from technical services (managerial, technical, consulting)"],
            uns=[(_pay8("services"), "services are taken as managerial, technical or consulting services")], remaining=[])
    elif cc == "RS":
        _w8(S, "wht2", "Porez po odbitku (usluge)",
            [("services", 2000, None, "Zakon o porezu na dobit pravnih lica: 20 % on market research, accounting, audit and legal or business consulting services")],
            "Zakon o porezu na dobit pravnih lica čl. 40 (withholding)", _pwh8("RS").split(", accessed ")[1].split(" (")[0], "B", _pwh8("RS"),
            ["20 % on dividends, royalties, interest and on market research, accounting, audit and legal/business consulting fees; 25 % to tax havens"],
            uns=[(_pay8("services"), "services are taken as the listed consulting/audit services; the 25 % tax-haven rate is not applied")], remaining=[])
    elif cc == "SI":
        _w8(S, "wht2", "Davčni odtegljaj (storitve)",
            [("services", 0, None, "ZDDPO-2 čl. 70: service fees bear withholding only when paid to states with an average CIT rate up to 12,5 % (listed): none otherwise")],
            "ZDDPO-2 čl. 70 (withholding on services)", _pwh8("SI").split(", accessed ")[1].split(" (")[0], "B", _pwh8("SI"),
            ["withholding on services (of a consulting, marketing, administrative, staffing, information or legal kind) only when paid to listed low-tax states (average CIT up to 12,5 %)"],
            uns=[(_pay8("services"), "services are taken as paid to a state not on the low-tax list")], remaining=[])
    elif cc == "UA":
        _w8(S, "wht2", "Податок на доходи нерезидентів (послуги)",
            [("services", 1500, None, "Податковий кодекс п. 141.4.2: 15 % on Ukrainian-source income of non-residents including engineering services")],
            "Податковий кодекс України п. 141.4.1-141.4.2", _pwh8("UA").split(", accessed ")[1].split(" (")[0], "B", _pwh8("UA"),
            ["15 % on passive income and on other payments including engineering services, lease, agency and brokerage fees; 6 % on freight"],
            uns=[(_pay8("services"), "services are taken as engineering services; services outside the list bear none")], remaining=[])
    elif cc == "DE":
        _w8(S, "wht", "Kapitalertragsteuer / Abzugsteuer (§ 50a)",
            [("dividend", 2500, None, "EStG § 43 Abs. 1 Satz 1 Nr. 1, § 43a Abs. 1 Satz 1 Nr. 1: Kapitalertragsteuer 25 %"),
             ("interest", 0, None, "EStG § 49 Abs. 1 Nr. 5 Buchst. c Doppelbuchst. aa: interest of non-residents is German income only when secured on German real estate or ships: none on an unsecured loan"),
             ("royalty", 1500, None, "EStG § 50a Abs. 1 Nr. 3, Abs. 2 Satz 1: Steuerabzug 15 % on royalties"),
             ("services", 0, None, "EStG § 50a Abs. 1: the Steuerabzug covers performances (Nr. 1-2), rights (Nr. 3) and supervisory boards (Nr. 4): none on other service fees")],
            "EStG §§ 43, 43a, 49 Abs. 1 Nr. 5, 50a Abs. 1-2; SolZG §§ 3, 4", "gesetze-im-internet.de, fetched 2026-11-21", "A",
            "EStG §§ 43, 43a, 44a, 49, 50a, gesetze-im-internet.de (`de/law/estg_43.txt` ... `estg_50a.txt`); SolZG § 4 (`de/law/solzg_1995___4.txt`)",
            ["§ 43a (1) Nr. 1: \"25 Prozent des Kapitalertrags\"; § 50a (2): \"Der Steuerabzug beträgt 15 Prozent\" (30 % for supervisory boards)",
             "§ 49 (1) Nr. 5 c aa: interest is domestic income only where the capital is secured on domestic land, rights or registered ships",
             "SolZG § 4: \"Der Solidaritätszuschlag beträgt 5,5 Prozent der Bemessungsgrundlage\""],
            uns=[(_pay8("dividend"), "the refund of two fifths to foreign corporations (§ 44a Abs. 9) and the EU parent-subsidiary exemption (§ 43b) not applied"),
                 (_pay8("royalty"), "the § 50c exemption for EU associated companies not applied")],
            solz=True)
    elif cc == "DK":
        _w8(S, "wht", "Begrænset skattepligt (udbytte, renter, royalty)",
            [("dividend", 2200, True, "selskabsskatteloven § 2, stk. 1, litra c, stk. 4: 22 pct. of dividends"),
             ("interest", 2200, True, "selskabsskatteloven § 2, stk. 1, litra d: 22 pct. on interest on controlled debt", 5001),
             ("interest", 0, True, "selskabsskatteloven § 2, stk. 1, litra d: only interest on controlled debt is taxable: none on other interest"),
             ("royalty", 2200, True, "selskabsskatteloven § 2, stk. 1, litra g: 22 pct. of royalties"),
             ("services", 0, True, "selskabsskatteloven § 2, stk. 1: service fees are not among the items of limited tax liability: none")],
            "selskabsskatteloven § 2, stk. 1, litra c, d, g (rates 22 pct.)", "LBK nr 279 af 13/03/2025 (`dk/law/sel_lbk2025_279.txt`)", "A",
            "Selskabsskatteloven, LBK nr 279 af 13/03/2025, retsinformation.dk (`dk/law/sel_lbk2025_279.txt`)",
            ["§ 2, stk. 1: limited liability on dividends (litra c), interest on controlled debt (litra d) and royalties (litra g); the tax is \"22 pct.\" of the dividends, interest and royalties (15 pct. on dividends where the recipient's state exchanges information, not applied)",
             "controlled debt: the payee controls the payer (skattekontrolloven kap. 4); taken here as a stake above 50 %"],
            uns=[(_pay8("dividend"), "withholding mechanics (kildeskatteloven § 65: 27 % withheld, excess refunded) not read; the 22 pct. tax is booked; the 15 pct. rate and the subsidiary-share exemption not applied"),
                 ("g.entity == .company && g.company.paymentsAbroad.any (fun p => !p.toCompany)", "payments to non-resident individuals (kildeskatteloven § 65 ff.) not read (grade C)")],
            remaining=["payments to individuals"])
    elif cc == "FI":
        _w8(S, "wht", "Lähdevero rajoitetusti verovelvolliselle",
            [("dividend", 2000, True, "lähdeverolaki 3 §, 7 § 1 mom. 2 kohta: 20 % on dividends to a non-resident company"),
             ("dividend", 3000, False, "lähdeverolaki 3 §, 7 § 1 mom. 4 kohta: 30 % on dividends to others"),
             ("interest", 0, None, "tuloverolaki 9 §: a non-resident is not liable on interest on loans from abroad, bonds, deposits and trade receivables: none"),
             ("royalty", 2000, True, "lähdeverolaki 3 §, 7 § 1 mom. 2 kohta: 20 % on royalties to a non-resident company"),
             ("royalty", 3000, False, "lähdeverolaki 7 § 1 mom. 4 kohta: 30 % on royalties to others"),
             ("services", 1300, True, "lähdeverolaki 3 §, 7 § 1 mom. 6 kohta: 13 % on work compensation (työkorvaus) to a company"),
             ("services", 3500, False, "lähdeverolaki 7 § 1 mom. 1 kohta: 35 % on an individual's work compensation")],
            "lähdeverolaki 627/1978 3 §, 7 § 1 mom.; tuloverolaki 1535/1992 9 §", "Finlex, Wayback captures 2025-05-21 / 2025-07-03 (`fi/law/lahdeverolaki_wb2025.txt`, `fi/law/tvl_wb20250703.txt`)", "A",
            "Laki rajoitetusti verovelvollisen tulon ja varallisuuden verottamisesta 627/1978, Finlex, Wayback 2025-05-21 (`fi/law/lahdeverolaki_wb2025.txt`); tuloverolaki 1535/1992 (`fi/law/tvl_wb20250703.txt`)",
            ["7 § 1 mom.: \"2) 20 prosenttia rajoitetusti verovelvolliselle yhteisölle maksettavasta osingosta, korosta ja rojaltista\"; \"4) 30 prosenttia\" to others; \"6) 13 prosenttia yhteisölle ... maksettavasta ... työkorvauksesta\"; \"1) 35 prosenttia\" on an individual's työkorvaus",
             "tuloverolaki 9 §: \"Rajoitetusti verovelvollinen ei ole verovelvollinen täältä saamastaan korkotulosta\" on foreign loans, deposits, bonds and trade receivables"],
            uns=[(_pay8("services"), "services are taken as work done in Finland; the 10 f § release (prepayment register, tax card) is not applied; the 510 €/month deduction on 35 % income not applied"),
                 (_pay8("dividend"), "dividends exempt for EU/treaty parent companies (3 § 4 mom.) not separated")],
            remaining=[])
    elif cc == "FR":
        _w8(S, "wht", "Retenue à la source (art. 182 B)",
            [("royalty", 2500, None, "CGI art. 182 B I b, II (taux de l'art. 219 I, 25 %)"),
             ("services", 2500, None, "CGI art. 182 B I c, II: 25 % on services of any kind provided or used in France")],
            "CGI art. 182 B I b et c, II", "Légifrance, Wayback capture 2024-12-01 (`fr/law/cgi_182B_wb.txt`)", "A",
            "Code général des impôts art. 182 B, Légifrance, Wayback capture 2024-12-01 (`fr/law/cgi_182B_wb.txt`)",
            ["I: withholding on sums paid by a debtor operating in France to persons without a permanent establishment there: b. inventors' and copyright income and products of industrial or commercial property; c. \"Les sommes payées en rémunération des prestations de toute nature fournies ou utilisées en France\"",
             "II: \"Le taux de la retenue est celui prévu au deuxième alinéa du I de l'article 219\" (25 %); III: 75 % for non-cooperative states (not applied)"],
            uns=[(_pay8("services"), "services are taken as provided or used in France"), (_pay8("royalty"), "the art. 182 B exemption for EU associated companies (art. 182 B II bis) not applied")])
        _w8(S, "wht2", "Retenue / prélèvement (dividendes, intérêts)",
            [("dividend", 2500, True, "CGI art. 119 bis 2, art. 219 I: 25 % on dividends to non-resident companies"),
             ("dividend", 1280, False, "CGI art. 187 1-2°: 12,8 % on dividends to non-resident individuals"),
             ("interest", 0, None, "CGI art. 125 A III, art. 119 bis 1: interest paid abroad is exempt, except to non-cooperative states")],
            "CGI art. 119 bis 1-2, 125 A III, 187", _pwh8("FR").split(", accessed ")[1].split(" (")[0], "B",
            _pwh8("FR") + "; CGI art. 125 A, Légifrance Wayback 2024-12-07 (`fr/law/cgi_125A_wb.txt`)",
            ["dividends: 25 % to companies (0 % under the parent-subsidiary rules), 12,8 % to individuals (art. 187)",
             "interest: no withholding since 1 March 2010 except payments to non-cooperative states (art. 125 A III: prélèvement on payments to those states)"],
            remaining=[])
    elif cc == "GR":
        _w8(S, "wht", "Παρακράτηση φόρου (ΚΦΕ άρθρο 64)",
            [("dividend", 500, None, "ν. 4172/2013 (ΚΦΕ) άρθρο 64: dividends 5 %"),
             ("interest", 1500, None, "ΚΦΕ άρθρο 64: interest 15 %"),
             ("royalty", 2000, None, "ΚΦΕ άρθρο 64: royalties 20 %"),
             ("services", 0, True, "ΚΦΕ άρθρο 64: legal entities without a PE in Greece bear no withholding on technical, consulting and management fees"),
             ("services", 2000, False, "ΚΦΕ άρθρο 64: 20 % on fees for technical, management and consulting services")],
            "ν. 4172/2013 (ΚΦΕ) άρθρο 64", _pwh8("GR").split(", accessed ")[1].split(" (")[0], "B", _pwh8("GR"),
            ["rates: 5 % on dividends; 15 % on interest; 20 % on royalties; 20 % on technical, management and consulting fees; non-resident legal entities without a Greek PE are outside the withholding on those fees"],
            remaining=[])
    elif cc == "HU":
        _w8(S, "wht", "Forrásadó (társaságok)",
            [("dividend", 0, True, "Tao. tv.: no withholding on dividends paid to non-individuals"),
             ("interest", 0, True, "Tao. tv.: no withholding on interest paid to non-individuals"),
             ("royalty", 0, True, "Tao. tv.: no withholding on royalties paid to non-individuals"),
             ("services", 0, True, "Tao. tv.: no withholding on service fees paid to non-individuals")],
            "1996. évi LXXXI. törvény (Tao.): no withholding on payments to foreign companies", _pwh8("HU").split(", accessed ")[1].split(" (")[0], "B", _pwh8("HU"),
            ["dividends, interest and royalties paid to a company bear no withholding under domestic law"],
            uns=[("g.entity == .company && g.company.paymentsAbroad.any (fun p => !p.toCompany)", "payments to non-resident individuals (Szja. tv. 15 % on dividends and interest) not read (grade C)")],
            replace_absent=True, remaining=["payments to individuals"])
    elif cc == "IE":
        _w8(S, "wht", "Withholding on payments abroad (DWT, interest, patent royalties)",
            [("dividend", 2500, None, "TCA 1997 s. 172B: dividend withholding tax 25 %"),
             ("interest", 2000, None, "TCA 1997 s. 246 (2): income tax at the standard rate (20 %) deducted from yearly interest paid to a person whose usual place of abode is abroad"),
             ("royalty", 2000, None, "TCA 1997 s. 238: income tax at the standard rate (20 %) deducted from patent royalties"),
             ("services", 0, None, "professional services withholding (TCA Part 18, ch. 1) applies only to payments by public bodies: none on a company's service fees")],
            "TCA 1997 ss. 172B, 238, 246", _pwh8("IE").split(", accessed ")[1].split(" (")[0] + "; Revenue Notes for Guidance (Wayback 2025-10)", "B",
            _pwh8("IE") + "; Revenue TCA Notes for Guidance Part 6 and Part 8 (`ie/law/tca_nfg_part06.txt`, `ie/law/tca_nfg_part08.txt`)",
            ["DWT 25 % on distributions from 1 January 2020; interest: s. 246 obliges companies to deduct tax at the standard rate from annual interest paid abroad; patent royalties 20 %, other royalties none",
             "PSWT (20 %) is deducted only where the payer is a public body (a government department, a state agency or a local authority)"],
            uns=[(_pay8("royalty"), "royalties are taken as patent royalties (s. 238); other royalties bear none"),
                 (_pay8("dividend") + " || " + _pay8("interest"), "the DWT exemptions for EU/treaty companies (s. 172D) and the s. 246 (3) interest exclusions not applied")],
            remaining=[])
    elif cc == "IT":
        _w8(S, "wht", "Ritenuta (lavoro autonomo)",
            [("services", 3000, None, "DPR 600/1973 art. 25 c. 1: ritenuta a titolo d'imposta del 30 % on compensi for lavoro autonomo paid to non-residents, also for services rendered in a business")],
            "DPR 600/1973 art. 25 c. 1", "normattiva vigente 2025-07-01 (`it/law/dpr600_art25.txt`)", "A",
            "DPR 29 settembre 1973 n. 600, normattiva, vigente al 2025-07-01 (`it/law/dpr600_art25.txt`)",
            ["art. 25 c. 1: to non-residents \"deve essere operata una ritenuta a titolo d'imposta nella misura del 30 per cento, anche per le prestazioni effettuate nell'esercizio di imprese\"; excluded: work performed abroad"],
            uns=[(_pay8("services"), "services are taken as professional services performed in Italy (art. 25: none on work performed abroad)")])
        _w8(S, "wht2", "Ritenuta (dividendi, interessi, canoni)",
            [("dividend", 2600, None, "DPR 600/1973 art. 27 c. 3: ritenuta a titolo d'imposta on profits paid to non-residents, 26 %"),
             ("interest", 2600, None, "DPR 600/1973 art. 26 c. 5: ritenuta on interest paid to non-residents, 26 %"),
             ("royalty", 2250, None, "DPR 600/1973 art. 25 c. 4: 30 % on the taxable part (75 %) of royalties")],
            "DPR 600/1973 art. 25 c. 4, 26 c. 5, 27 c. 3 (rate 26 %: D.L. 66/2014 art. 3)", _pwh8("IT").split(", accessed ")[1].split(" (")[0], "B",
            _pwh8("IT") + "; DPR 600/1973 art. 25-27 (`it/law/dpr600_art25.txt` ... `art27.txt`)",
            ["non-treaty rates: dividends 26 %, interest 26 %, royalties 30 % on 75 % of the amount",
             "art. 27 c. 3-ter: 1,20 % on dividends to EU/EEA companies (not applied); the text of art. 26-27 still shows the pre-2014 rates, the 26 % comes from a general provision"],
            remaining=[])
    elif cc == "LI":
        _w8(S, "wht", "Withholding on payments abroad (none levied)",
            [(k, 0, None, "Liechtenstein levies no withholding tax on " + k + " paid abroad (Couponsteuer abolished from 2011)") for k in ("dividend", "interest", "royalty", "services")],
            "SteG (no withholding tax)", _pwh8("LI").split(", accessed ")[1].split(" (")[0], "B", _pwh8("LI"),
            ["no withholding taxes are levied"], replace_absent=True)
    elif cc == "LU":
        _w8(S, "wht", "Retenue à la source (revenus de capitaux)",
            [("dividend", 1500, None, "L.I.R. art. 146 (1) 1., art. 148 (1): retenue 15 % on dividends"),
             ("interest", 0, None, "L.I.R. art. 146 (1) 3.: only profit-sharing bond interest is subject: none on ordinary interest"),
             ("royalty", 0, None, "L.I.R. art. 146, 152: royalties are not among the income subject to retenue: none"),
             ("services", 0, None, "L.I.R. art. 152: retenue only on literary, artistic and sports activities in Luxembourg and directors' fees: none on other service fees")],
            "L.I.R. art. 146, 148, 152", "loi modifiée du 4 décembre 1967, texte coordonné au 1.1.2025 (`lu/law/LIR_2025-01-01.txt`)", "A",
            "Loi concernant l'impôt sur le revenu, texte coordonné 1.1.2025 (`lu/law/LIR_2025-01-01.txt`)",
            ["art. 146 (1): subject to retenue: dividends and profit shares (1., 2.) and interest of bonds carrying a profit-dependent supplement (3.)",
             "art. 148 (1): \"Le taux de la retenue est fixé à 15%\"; art. 152: retenue on literary/artistic and professional sports income of non-residents and on directors' fees"],
            uns=[(_pay8("dividend"), "the art. 147 exemption (parent companies, 10 % / EUR 1,2 m) not applied")], remaining=[])
    elif cc == "LV":
        _w8(S, "wht", "Uzņēmumu ienākuma nodoklis, ko ietur no nerezidentiem",
            [("services", 2000, True, "likums Par uzņēmumu ienākuma nodokli 5. panta 1. daļas 1. punkts: 20 % on management and consultancy services"),
             ("dividend", 0, True, "UIN likums 5. panta 1. daļa: dividends are not among the payments withheld (20 % only to low-tax jurisdictions, 6. daļa): none"),
             ("interest", 0, True, "UIN likums 5. panta 1. daļa: interest not withheld (20 % only to low-tax jurisdictions): none"),
             ("royalty", 0, True, "UIN likums 5. panta 1. daļa: royalties not withheld (20 % only to low-tax jurisdictions): none")],
            "likums Par uzņēmumu ienākuma nodokli 5. pants (1), (5), (6)", "likumi.lv, redakcija 2025-07-01 (`lv/law/uin_2025-07-01.txt`)", "A",
            "Uzņēmumu ienākuma nodokļa likums, likumi.lv redakcija 1.7.2025 (`lv/law/uin_2025-07-01.txt`)",
            ["5. panta 1. daļa: withheld from \"1) atlīdzības par vadības un konsultatīvajiem pakalpojumiem — 20 procenti\"; 2) Latvian real estate 3 %; 4) rent 5 %; 3) payments under (6) and (8)",
             "5. panta 6. daļa: 20 % on all payments and dividends to persons in low-tax or no-tax jurisdictions (not applied)"],
            uns=[(_pay8("services"), "services are taken as management and consultancy services (5. panta 5. daļa)"),
                 ("g.entity == .company && g.company.paymentsAbroad.any (fun p => !p.toCompany)", "payments to non-resident individuals (likums Par IIN) not read (grade C)")],
            remaining=["payments to individuals"])
    elif cc == "MT":
        _w8(S, "wht", "Withholding on payments abroad (interest, royalties)",
            [("interest", 0, None, "Income Tax Act (Cap. 123) art. 12 (1) (c) (i): interest accruing to a person not resident in Malta is exempt"),
             ("royalty", 0, None, "Cap. 123 art. 12 (1) (c) (i): royalties accruing to a person not resident in Malta are exempt")],
            "Income Tax Act (Cap. 123) art. 12 (1) (c) (i)", "legislation.mt consolidated text (`mt/law/cap123.txt`)", "A",
            "Income Tax Act, Cap. 123, legislation.mt (`mt/law/cap123.txt`)",
            ["art. 12 (1): \"There shall be exempt from the tax - ... (c) (i) any interest, discount, premium or royalties accruing to or derived by any person not resident in Malta\" (provisos: PE in Malta, resident owners)"],
            replace_absent=True)
        _w8(S, "wht2", "Withholding on dividends (none)",
            [("dividend", 0, None, "full imputation system: no withholding on dividends paid to non-residents")],
            "Income Tax Act (Cap. 123): full imputation, no tax on distributions", _pwh8("MT").split(", accessed ")[1].split(" (")[0], "B", _pwh8("MT"),
            ["dividends carry no withholding: the company's tax is imputed to the shareholder"], remaining=["services"])
    elif cc == "NO":
        _w8(S, "wht", "Kildeskatt",
            [("dividend", 2500, None, "Stortingets skattevedtak 2025 § 3-5 (2): 25 pst. on dividends to shareholders resident abroad"),
             ("interest", 0, None, "skattevedtak 2025 § 3-5 (5), skatteloven § 2-3 (1) i: interest bears source tax only when paid to a related company in a low-tax state: none otherwise"),
             ("royalty", 0, None, "skattevedtak 2025 § 3-5 (5), skatteloven § 2-3 (1) j: royalties bear source tax only when paid to a related company in a low-tax state: none otherwise"),
             ("services", 0, None, "skattevedtak 2025 §§ 3-5, 3-6: the source taxes are on dividends, interest and royalties to related low-tax companies and foreign artists' fees: none on service fees")],
            "Stortingets skattevedtak for 2025 §§ 3-5, 3-6; skatteloven § 2-3 (1) i, j, §§ 10-80, 10-81", "Lovdata, FOR-2024-12-13-3203 (`no/law/stv_skatt2025.txt`)", "A",
            "Stortingets vedtak om skatt av inntekt og formue mv. for inntektsåret 2025, Lovdata (`no/law/stv_skatt2025.txt`); skatteloven (TOC, `no/law/skatteloven.txt`)",
            ["§ 3-5: \"Av aksjeutbytte som utdeles til aksjonær som er hjemmehørende i utlandet, svares skatt til staten med 25 pst.\"; income under skatteloven §§ 10-80 and 10-81 of taxpayers in § 2-3 (1) i and j: 15 pst.",
             "§ 3-6: 15 pst. on fees to foreign artists"],
            uns=[("g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest || p.kind == .royalty)", "15 pst. on interest and royalties to related companies in low-tax states (skatteloven § 10-82) not applied: the input has no recipient state"),
                 (_pay8("dividend"), "the exemption for EEA companies (skatteloven § 2-38) not applied")],
            remaining=[])
    elif cc == "PT":
        _w8(S, "wht", "Retenção na fonte de IRC (não residentes)",
            [(k, 2500, True, "CIRC art. 94.º n.º 1 " + a + ", n.º 3 b), art. 87.º n.º 4: 25 % (definitive) on " + w)
             for k, a, w in (("dividend", "c)", "dividends"), ("interest", "c)", "interest"), ("royalty", "a)", "royalties"),
                             ("services", "g)", "services performed or used in Portugal"))],
            "CIRC art. 4.º n.º 3 c) 7), art. 87.º n.º 4, art. 94.º n.º 1 a), c), g), n.º 3 b)", "Portal das Finanças, código consolidado fetched 2026-11-21 (`pt/law/irc87.txt`, `irc94.txt`, `irc4.txt`)", "A",
            "Código do IRC art. 4.º, 87.º, 94.º, Portal das Finanças (`pt/law/irc4.txt`, `pt/law/irc87.txt`, `pt/law/irc94.txt`)",
            ["art. 87.º n.º 4: for entities without seat, management or PE in Portugal \"a taxa do IRC é de 25%\"",
             "art. 94.º n.º 1: withholding on industrial/intellectual property income (a), capital income (c) and \"outras prestações de serviços realizados ou utilizados em território português\" (g); n.º 3 b): definitive for non-residents without a PE",
             "art. 4.º n.º 3 c) 7): services performed or used in Portugal, except transport, communications and financial activities"],
            uns=[(_pay8("services"), "services are taken as performed or used in Portugal and not transport, communications or financial"),
                 ("g.entity == .company && g.company.paymentsAbroad.any (fun p => !p.toCompany)", "payments to non-resident individuals (CIRS art. 71.º) not read (grade C)"),
                 ("g.entity == .company && !g.company.paymentsAbroad.isEmpty", "35 % to listed tax havens and the EU directive exemptions not applied")],
            remaining=["payments to individuals"])
    elif cc == "RO":
        _w8(S, "wht", "Impozit pe veniturile nerezidenților",
            [("dividend", 1000, None, "Codul fiscal art. 224 (4): dividends 10 % (2025)"),
             ("interest", 1600, None, "Codul fiscal art. 223, 224 (4): interest 16 %"),
             ("royalty", 1600, None, "Codul fiscal art. 223, 224 (4): royalties 16 %"),
             ("services", 1600, None, "Codul fiscal art. 223 (2): services rendered in Romania and management/consultancy services 16 %")],
            "Codul fiscal art. 223-224", _pwh8("RO").split(", accessed ")[1].split(" (")[0], "B", _pwh8("RO"),
            ["16 % on interest, royalties, services rendered in Romania and management/consultancy services wherever rendered; dividends to non-residents 10 %; 50 % to states without exchange of information (not applied)"],
            uns=[(_pay8("services"), "services are taken as rendered in Romania or management/consultancy")], remaining=[])
    elif cc == "RU":
        _w8(S, "wht", "Налог у источника (иностранные организации)",
            [("dividend", 1500, None, "НК РФ ст. 284 п. 3 пп. 3, ст. 310: dividends 15 %"),
             ("interest", 2000, None, "НК РФ ст. 284 п. 2 пп. 1, ст. 309-310: interest 20 %"),
             ("royalty", 2000, None, "НК РФ ст. 284 п. 2 пп. 1, ст. 309-310: royalties 20 %")],
            "Налоговый кодекс РФ ст. 284, 309, 310", _pwh8("RU").split(", accessed ")[1].split(" (")[0], "B", _pwh8("RU"),
            ["non-treaty rates: dividends 15 %, interest 20 %, royalties 20 %"], remaining=["services"])
    elif cc == "SE":
        _w8(S, "wht", "Kupongskatt",
            [("dividend", 3000, None, "kupongskattelag (1970:624) 5 §: 30 procent of the dividend")],
            "kupongskattelag (1970:624) 5 §", "data.riksdagen.se, fetched 2026-11-21 (`se/law/sfs-1970-624.txt`)", "A",
            "Kupongskattelag (1970:624), data.riksdagen.se (`se/law/sfs-1970-624.txt`)",
            ["5 §: \"Kupongskatt utgår med trettio procent av utdelningen.\""],
            uns=[(_pay8("dividend"), "the exemptions for EU/treaty parent companies (4 §) not applied")])
        _w8(S, "wht2", "Withholding on interest, royalties, services",
            [("interest", 0, None, "no Swedish tax on interest paid to non-resident corporations or individuals"),
             ("services", 0, None, "no Swedish tax on service fees paid to non-residents"),
             ("royalty", 2060, None, "royalties to non-residents are taxed as income of a deemed permanent establishment at 20,6 %")],
            "inkomstskattelagen (deemed PE for royalties; no tax on interest and service fees)", _pwh8("SE").split(", accessed ")[1].split(" (")[0], "B", _pwh8("SE"),
            ["non-treaty: dividends 30 %, royalties 20,6 %; no tax on interest or service fees paid to non-residents"],
            uns=[(_pay8("royalty"), "royalties are assessed on the recipient (deemed PE), not withheld: booked as a withheld charge")], remaining=[])
    elif cc == "SK":
        _w8(S, "wht", "Daň vyberaná zrážkou (úroky, licenčné poplatky)",
            [("interest", 1900, None, "zákon 595/2003 § 43 ods. 1 písm. b), ods. 2: 19 % on interest on loans and credits"),
             ("royalty", 1900, None, "zákon 595/2003 § 16 ods. 1 písm. e) body 1-2, § 43 ods. 1 písm. b), ods. 2: 19 % on royalties"),
             ("dividend", 700, False, "zákon 595/2003 § 43 ods. 1 písm. a), ods. 3 písm. r): 7 % on dividends paid to individuals")],
            "zákon 595/2003 Z.z. § 16 ods. 1 písm. e), § 43 ods. 1-3", "znenie od 1.1.2025 (`sk/law/dp_20250101.txt`)", "A",
            "Zákon o dani z príjmov 595/2003 Z.z., Slov-Lex znenie od 1.1.2025 (`sk/law/dp_20250101.txt`)",
            ["§ 43 (1): \"Daň sa vyberá zrážkou vo výške a) 7 % z príjmov podľa odseku 3 písm. r) a s) ..., b) 19 % z príjmov podľa odsekov 2 a 3 ..., c) 35 %\" to non-cooperative states",
             "§ 43 (2): withheld on income of non-residents under § 16 (1) c) to e) items 1, 2, 4, 10, 12 and on interest from loans and credits"],
            uns=[("g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest || p.kind == .royalty)", "35 % for non-cooperative states and the EU exemption (§ 13 ods. 1 písm. e)) not applied")],
            remaining=["dividends to companies", "services"])
    elif cc == "BE":
        _w8(S, "wht", "Précompte mobilier",
            [("dividend", 3000, None, "CIR 92 art. 269: précompte mobilier 30 % on dividends"),
             ("interest", 3000, None, "CIR 92 art. 269: précompte mobilier 30 % on interest"),
             ("royalty", 3000, None, "CIR 92 art. 269: précompte mobilier 30 % on royalties")],
            "CIR 92 art. 261, 269 (précompte mobilier)", _pwh8("BE").split(", accessed ")[1].split(" (")[0], "B", _pwh8("BE"),
            ["non-treaty rates: dividends 30 %, interest 30 %, royalties and certain rentals 30 %"], remaining=["services"])


def _nl8(S):
    if S["cc"] != "NL":
        return
    _w8(S, "wht", "Bronbelasting (rente, royalty's)",
        [("interest", 0, None, "Wet bronbelasting 2021: interest bears 25,8 % only when paid to a related entity in a low-tax or listed jurisdiction (or in abuse cases): none otherwise"),
         ("royalty", 0, None, "Wet bronbelasting 2021: royalties bear 25,8 % only when paid to a related entity in a low-tax or listed jurisdiction (or in abuse cases): none otherwise")],
        "Wet bronbelasting 2021 (conditional withholding on interest and royalties)", _pwh8("NL").split(", accessed ")[1].split(" (")[0], "B", _pwh8("NL"),
        ["non-treaty: interest and royalties 0 %, or 25,8 % in the conditional cases (related recipient in a low-tax or listed jurisdiction, abuse)"],
        uns=[("g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest || p.kind == .royalty)", "the 25,8 % conditional withholding (related recipient in a low-tax or listed state) not applied: the input has no recipient state")],
        remaining=["services"])


# ---------------------------------------------------------------- P5: LU transfer duty (B)
def _lu8(S):
    if S["cc"] != "LU" or not any(str(t.get("oecd")) == "4400" and t.get("grade") == "C" for t in S["taxes"]):
        return
    p6_transfer(S, "enr", "Droits d'enregistrement et de transcription (immeubles)", [(0, 700)],
                "droits d'enregistrement et de transcription on sales of Luxembourg real estate: 7 % in all (acts not read)",
                pwc("LU", "pwc_corpother_wb2025", "Corporate - Other taxes").split(", accessed ")[1].split(" (")[0], "B",
                pwc("LU", "pwc_corpother_wb2025", "Corporate - Other taxes"),
                ["sales of Luxembourg real estate: proportional registration duty including the transcription tax, 7 % in all; Luxembourg City adds a 3 % surtax"],
                uns=[("!g.purchases.isEmpty", "Luxembourg City surtax (3 %) not applied; the Bëllegen Akt credit on a buyer's own home and the base (higher of price and value) not read")])


# ---------------------------------------------------------------- P6: MK inheritance (municipal frame, stays C)
def _mk8(S):
    if S["cc"] != "MK" or not any(str(t.get("oecd")) == "4300" and t.get("grade") == "C" for t in S["taxes"]):
        return
    p6_note(S, "4300", "Данок на наследство и подарок", "Закон за даноците на имот (municipal rates)",
            "first order of succession exempt; second order 2-3 %, third order and unrelated 4-5 %, the rate set by each municipality within the range: the model's municipality and its decision not read",
            pwc("MK").split(", accessed ")[1].split(" (")[0] + " (" + pwc("MK") + ")")


# ---------------------------------------------------------------- P7: DE Kirchensteuer (Berlin, surcharge on the 1.x income tax)
def _de8kist(S):
    if S["cc"] != "DE" or S.get("fam") != "Other" or not any(str(t.get("oecd")) == "6000" and t.get("grade") == "C" for t in S["taxes"]):
        return
    st = "Kirchensteuerbeschluss Erzbistum Berlin 2025 § 2 (1) (9 % der Einkommensteuer; Kirchensteuergesetz Berlin); EStG § 51a Abs. 1-2"
    # The 1.x detax line already computes the Kirchensteuer as a surtax on the income tax (DeTax/Assess.lean `kistBp`,
    # Main.lean `--kist=800|900`; default 0 = not a member): a second charge here would double it. Berlin is 9 %.
    S.setdefault("unsupported", []).append(("g.entity != .company && !(args.any (·.startsWith \"--kist=\"))", "6000 Kirchensteuer: computed by the 1.x model as a surtax only with --kist=900 (Berlin, KiStB § 2 (1)); without it the household is taken as not a member of a church levying it"))
    S["taxes"] = [t for t in S["taxes"] if not (str(t.get("oecd")) == "6000" and t.get("grade") == "C")] + [
        {"oecd": "6000", "tax": "Kirchensteuer (Berlin)", "statute": st, "dated": "Amtsblatt des Erzbistums Berlin 12/2024 (2025 ff.); EStG § 51a (gesetze-im-internet.de, 2026-11-21)",
         "grade": "A", "kernel_parts": ["1.x surtax Kirchensteuer (DeTax.Assess kistBp, option --kist=900 for Berlin)"],
         "unsupported": ["membership is an option of the run (--kist): default not a member", "the other 6000 items (none recorded)"]},
        {"oecd": "6000", "tax": "Other taxes (rest)", "statute": "", "dated": "", "grade": "C", "status": "unsupported", "kernel_parts": [],
         "tried": "pass 8: Kirchensteuer modelled; no other national tax recorded", "unsupported": ["confirm against the list of German taxes"]}]
    S.setdefault("notes", []).append("DE 6000 Kirchensteuer: KiStB Erzbistum Berlin 2025 § 2 (1), EStG § 51a (A)")
    S["doc"] += ("\n\n## Kirchensteuer, Berlin (pass 8, grade A)\nSource: Kirchensteuerbeschluss of the Erzbistum Berlin for 2025 ff., Amtsblatt 12/2024 (`de/law/kistb_erzbistum_berlin_2025.txt`); "
                 "service.berlin.de, Kirchensteuer - Festsetzung (`de/law/service_berlin_kirchensteuer.txt`); EStG § 51a (`de/law/estg_51a.txt`).\n"
                 "* KiStB § 2 (1): the church tax \"beträgt ... 9 Prozent der Einkommensteuer (einschließlich Lohnsteuer, Kapitalertragsteuer), höchstens jedoch 3 Prozent\" of the taxable income (Kappung)\n"
                 "* service.berlin.de: \"Die Kirchensteuer beträgt 9%\"; legal basis Kirchensteuergesetz Berlin\n"
                 "* EStG § 51a (2): the base is the income tax with the child allowances of § 32 (6) in every case\n"
                 "* The pilot's Land is Berlin (Grundsteuer, `DeGlobal/Basic.lean`); the 1.x detax line computes the Kirchensteuer as a surtax on the income tax when run with --kist=900 (9 %, the Berlin rate read here); no second charge is added, the 1.x output is unchanged.\n")


def p8_rows(S):
    for f in (_wht8, _nl8, _lu8, _mk8, _de8kist):
        f(S)
