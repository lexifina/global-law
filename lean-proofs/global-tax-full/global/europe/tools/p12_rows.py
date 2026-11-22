# pass 12 rows (R1 Europe, 2026-11-21): P5/P6 (recurrent property, inheritance, wealth absences), VAT carry-overs,
# withholding gaps. exec'd by the spec after p6lib.py, p8_rows.py ... p11_rows.py. Every function is keyed by country
# and family (the block re-runs at every build). Statute rows quote or cite the act read (grade A); official guides B.


def _is(S, cc, fam):
    return S.get("cc") == cc and S.get("fam") == fam


# ---------------------------------------------------------------- P5: recurrent property taxes (4100)
def _prop12(S):
    if _is(S, "DK", "Property") and any(str(t.get("oecd")) == "4100" and t.get("grade") == "C" for t in S["taxes"]):
        st = "Ejendomsskatteloven (lov nr. 678 af 3. juni 2023) § 3, § 13 stk. 2, § 22 stk. 2-4"
        p6_property(S, "dkEvs", "Ejendomsværdiskat", [(0, 51), (9200000, 140)], st,
                    "retsinformation.dk, lov nr. 678 af 3.6.2023 (XML fetched 2026-11-21, `dk/law/ejendomsskattelov_lov2023_678.xml`); "
                    "§ 22 stk. 4: the index that adjusts the 9 200 000 kr. amount is first computed for income year 2026, so 2025 keeps the 2024 level",
                    "A", "Ejendomsskatteloven, lov nr. 678 af 3. juni 2023, retsinformation.dk XML (`dk/law/ejendomsskattelov_lov2023_678.xml`)",
                    ["§ 3 stk. 1: ejendomsværdiskat is paid on owner-occupied dwellings (one dwelling unit; two-unit owner dwellings; farm and forest dwellings)",
                     "§ 13 stk. 2: the base is 80 pct. of the ejendomsværdi assessed for the preceding income year",
                     "§ 22 stk. 2: 5,1 promille of the base up to 9 200 000 kr. (2024 level), 14,0 promille of the base above it",
                     "§ 22 stk. 3-4: the amount is adjusted every second year by an owner-dwelling value index first computed for income year 2026 (2025: 9 200 000 kr.)",
                     "Not modelled: the reductions for dwellings acquired by 1 July 1998 (§§ 23-24: 1,0 and 2,1 promille), the transitional rebate (§ 40 stk. 2, owners under the old rules) and the pensioner reductions"],
                    kinds=("home",), ratio=(4, 5),
                    uns=[("g.assets.any (fun a => a.kind == .home)", "ejendomsværdiskat: the asset's value is taken as the assessed ejendomsværdi of the preceding year; the 1998 reductions (§§ 23-24) and the § 40 rebate are not applied")])
        S["guards"].append("p6dkEvs.amount { kind := .home, value := 15000000 } == 86120")
        p6_note(S, "4100", "Grundskyld", "Ejendomsskatteloven § 1, kapitel 3 (grundskyld: the municipal rate, kommunal grundskyldspromille)",
                "grundskyld is charged at the rate each municipality sets on 80 pct. of the land value; the reference municipality's 2025 rate was not read",
                "lov nr. 678 af 3.6.2023 (retsinformation.dk XML)")

    if _is(S, "PT", "Property") and any(str(t.get("oecd")) == "4100" and t.get("grade") == "C" for t in S["taxes"]):
        st = "Código do IMI art. 112.º n.º 1 c), n.º 5 (redação da Lei n.º 7-A/2016); Município de Lisboa: 0,3 % for 2025"
        p6_property(S, "ptImi", "Imposto municipal sobre imóveis (prédios urbanos, Lisboa)", [(0, 30)], st,
                    "Portal das Finanças, códigos tributários, CIMI art. 112.º (fetched 2026-11-21, `pt/law/cimi112_portal.txt`); Lisbon's rate from the 2025 municipal budget as reported (rr.pt, 29.11.2024: the urban rate stays at 0,3 %)",
                    "B", "CIMI art. 112.º, Portal das Finanças (`pt/law/cimi112_portal.html`); the Lisbon rate from a news report of the Câmara's 2025 budget (the Assembleia Municipal deliberation was not read)",
                    ["art. 112.º n.º 1 c): prédios urbanos, de 0,3 % a 0,45 %; a): prédios rústicos 0,8 %",
                     "art. 112.º n.º 5: the municipal assembly fixes each year's rate within the c) interval, possibly by parish",
                     "Lisboa: 0,3 % (the statutory minimum) for the tax of 2025, with the +30 % for degraded and -30 % for listed buildings (n.º 6-8) not modelled",
                     "Not modelled: the tripled rate for vacant buildings (n.º 3), 7,5 % for owners in listed low-tax jurisdictions (n.º 4), the IMI familiar deduction (art. 112.º-A), the temporary own-home exemption (EBF art. 46.º), the AIMI (art. 135.º-A ff.) and rústicos"],
                    kinds=("home", "realEstate"), level="local",
                    uns=[("g.assets.any (fun a => a.kind == .home || a.kind == .realEstate)", "IMI: the asset's value is taken as the valor patrimonial tributário; the own-home exemption (EBF art. 46.º), the art. 112.º-A family deduction and the AIMI are not applied"),
                         ("g.assets.any (fun a => a.kind == .land)", "IMI on land: rústico (0,8 %) or terreno para construção (urban, 0,3 %) cannot be told apart from the input (grade C)")])


# ---------------------------------------------------------------- withholding gaps kept at C with a note (1200)
def _c12(S, cc, tried, unlock):
    if not _is(S, cc, "Corporate"):
        return
    for t in S["taxes"]:
        if t.get("grade") == "C" and "ithholding" in t.get("tax", "") and "pass 12" not in t.get("tried", ""):
            t["tried"] = (t.get("tried", "") + "; pass 12: " + tried).lstrip("; ")
            t["unsupported"] = list(t.get("unsupported", [])) + ["would unlock (pass 12): " + unlock]
    S["doc"] += f"\n\n## 1200 withholding still grade C (pass 12)\n* {tried}\n* would unlock: {unlock}\n"


def _wht12(S):
    _c12(S, "MT", "Cap. 123 (`mt/law/cap123.txt`) re-read: the only deduction at source on a non-resident's fees for services is art. 23 (5) (a), "
         "petroleum Contractors paying non-resident sub-contractors at the art. 56 (13) (b) rate; any other non-resident's Malta-source service "
         "income is charged by return (art. 4), so a generic company deducts nothing",
         "a Commissioner for Tax and Customs guide or the FSS rules (S.L. 123.13) stating that no other deduction applies, to cite the 0 as A")
    _c12(S, "HU", "Szja (`hu/law/szja.txt`, consolidated text with the 2025. évi LIV. törvény amendments) 46.-47. §: on self-employed and royalty "
         "income the Hungarian payer deducts a tax advance (adóelőleg) and the tax is settled by return; the advance base for a non-resident "
         "individual and the treaty relief path were not read clause by clause (the jogtar text interleaves amendment notes)",
         "a clean 2025 text of Szja 46.-49. § and 7. § (cost ratio) or NAV's guide for payments to foreign individuals")


def p12_rows(S):
    for f in (_prop12, _wht12, _recite12):
        f(S)


# ---------------------------------------------------------------- year-in-force re-cites (FT reviewer 6, IMPROVE_FT.md Y-12)
_RECITE12 = {
    ("SM", "Corporate"): "the held testo coordinato of Legge 166/2013 prints the wording in force from the 2026 tax period (L. 141/2025); "
                         "for 2025 art. 148 c. 8 keeps the earlier wording (\"Fino al 31 dicembre 2025\"); the modelled IGR rate and withholding "
                         "rates are the same in both wordings (bank interest under art. 103 c. 2 is 11 % in 2025: not a modelled kind)",
    ("DE", "Other"): "KraftStG § 3d: the held text is the wording after 2025; the exemption of electric cars first registered from 2016 gives "
                     "the same result for 2025",
    ("SE", "Other"): "vägtrafikskattelag 2 kap. 9 a § as worded by Lag 2024:1134 applies from 1 February 2025; January 2025 falls under the "
                     "old first and third paragraphs (one month of the year; not split)",
    ("FR", "Other"): "malus CO2: the 2025 barème applies from 1 March 2025; January and February 2025 registrations fall under the 2024 "
                     "barème (declared, not split; grade B kept)",
}


def _recite12(S):
    k = (S.get("cc"), S.get("fam"))
    if k in _RECITE12 and "year-in-force re-cite (pass 12)" not in S.get("doc", ""):
        S["doc"] += f"\n\n## year-in-force re-cite (pass 12, FT reviewer 6 Y-12)\n* {_RECITE12[k]}\n"
        S.setdefault("notes", []).append(f"{k[0]} year-in-force re-cite (pass 12): {_RECITE12[k][:160]}")
