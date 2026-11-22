# pass 7 rows (R1 Europe, 2026-11-21): P5/P6 gaps and carry-overs. exec'd by the spec after p6lib.py (helpers p6_*).
# A row is applied only to the spec that holds a grade-C entry for its code (`_has`). Statute rows quote the act read;
# PwC rows (B) state facts only, in short form, with the provenance line of p6lib.pwc().

def _has7(S, o):
    return any(str(t.get("oecd")) == o and t.get("grade") == "C" for t in S["taxes"])


def _pw7(cc, page="Individual - Other taxes", name="pwc_indother_wb2025"):
    return pwc(cc, name, page)


def _pwd7(cc, name="pwc_indother_wb2025", page="Individual - Other taxes"):
    p = _pw7(cc, page, name)
    return "PwC WWTS " + page + ", " + p.split(", accessed ")[1].split(" (")[0] + " (" + p.split(" (")[-1].split(";")[0] + ")"


# ---------------------------------------------------------------- 4400 transfer duties
def _fi7(S):
    if S["cc"] != "FI" or not _has7(S, "4400"):
        return
    p6_transfer(S, "vvl", "Varainsiirtovero (kiinteistö)", [(0, 300)],
                "Varainsiirtoverolaki 931/1996 6 § 1 mom. (3 % of the price, L 1185/2023 from 1.1.2024); 20 § 1 mom. (1,5 % on securities)",
                "Finlex ajantasa, Wayback capture 2025-06-25 (`fi/law/vvl_wb2025.txt`)", "A",
                "Varainsiirtoverolaki 931/1996, Finlex ajantasalainsäädäntö, Wayback capture 2025-06-25 (`fi/law/vvl_wb2025.txt`)",
                ["6 § 1 mom.: \"Kiinteistön luovutuksessa vero on kolme prosenttia kauppahinnasta tai muun vastikkeen arvosta.\" (21.12.2023/1185, in force 1.1.2024; before: 4 prosenttia)",
                 "20 § 1 mom.: \"Arvopaperin luovutuksessa vero on 1,5 prosenttia kauppahinnasta tai muun vastikkeen arvosta.\" (1185/2023; before: 1,6); 3 mom. (2,0 % for housing-company shares) amended by 1185/2023",
                 "11 § (ensiasunnon verovapaus) repealed by 1185/2023"],
                kinds=("realEstate", "land", "home"),
                uns=[("g.purchases.any (·.kind == .home)", "a home bought as housing-company shares (asunto-osake) bears 1,5 % (20 §), a detached house 3 % (6 §): the input does not say which; 3 % applied"),
                     ("g.purchases.any (·.firstHome)", "no first-home exemption: 11 § repealed from 1.1.2024 (L 1185/2023)")])


def _mt7(S):
    if S["cc"] != "MT" or not _has7(S, "4400"):
        return
    st = "Duty on Documents and Transfers Act (Cap. 364) art. 32 (1) (EUR 5 per EUR 100 of the higher of price and value); art. 32 (4) (a) (EUR 3.50 per EUR 100 on the first EUR 200 000 for the buyer's sole ordinary residence)"
    src = "Cap. 364, legislation.mt consolidated PDF (amendments to Act XXX of 2025), fetched 2026-11-21 (`mt/law/cap364.pdf`)"
    q = ["art. 32 (1): \"a duty of five euro (5.00) for every one hundred euro (100) or part thereof of the amount or value of the consideration for the transfer of such thing or of the value of such thing, whichever is the higher\"",
         "art. 32 (4) (a): for a person acquiring property \"for the purpose of establishing therein or constructing thereon his sole, ordinary residence\", duty \"in respect of the first two hundred thousand euro (€200,000) ... shall be charged at the rate of three euro and fifty cents (€3.50) per one hundred euro (€100) or part thereof\""]
    p6_transfer(S, "dodh", "Duty on documents and transfers (sole residence)", [(0, 350), (200000, 500)], st,
                "legislation.mt, Cap. 364 as amended to Act XXX of 2025", "A", src, q, kinds=("home",),
                uns=[("g.purchases.any (·.kind == .home)", "a home is taken as the buyer's sole ordinary residence (art. 32 (4)); the first-time buyer exemption on the first EUR 200 000 (subsidiary legislation, transfers to 31.12.2025) is not applied; the per-EUR 100 rounding up and the higher-of-value base are not applied (the price stands in)")])
    p6_transfer(S, "dod", "Duty on documents and transfers", [(0, 500)], st,
                "legislation.mt, Cap. 364 as amended to Act XXX of 2025", "A", src, q[:1], kinds=("realEstate", "land"),
                uns=[("g.purchases.any (fun p => p.kind == .realEstate || p.kind == .land)", "base: the higher of price and value (the price stands in); duty on shares (art. 47-50) not modelled")])


def _rs7(S):
    if S["cc"] != "RS":
        return
    src = "Zakon o porezima na imovinu (Sl. glasnik RS 26/2001 ... 94/2024), consolidated text, paragraf.rs, fetched 2026-11-21 (`rs/law/zpi.txt`)"
    if _has7(S, "4400"):
        _drop(S, "4400")
        st = "Zakon o porezima na imovinu čl. 25 st. 1 (the seller pays), čl. 27 (contract price, not below market value), čl. 30 (2,5 %)"
        S["lean"] += ("\n/-- " + st + " -/\n"
                      "def p7prenos (d : Disposal) : Int := if d.kind.isRealEstate then divR .down (250 * pos d.proceeds) 10000 else 0\n"
                      "def p7prenosCharges (ds : List Disposal) : List Charge :=\n  (ds.zipIdx.filter fun (d, _) => d.kind.isRealEstate).map fun (d, i) =>\n"
                      "    charge .transactions \"Porez na prenos apsolutnih prava\" d.proceeds (fun v => v) (fun _ => p7prenos d)\n"
                      "      (event := s!\"disposal {i + 1}\") (statute := " + _q(st) + ")\n")
        S["families"].append(("4400 Porez na prenos apsolutnih prava (seller)", [".transactions"], "p7prenosCharges g.disposals"))
        S["guards"] += ["p7prenos { kind := .realEstate, proceeds := 200000, cost := 0 } == 5000",
                        "p7prenos { kind := .home, proceeds := 1000000, cost := 900000 } == 25000",
                        "p7prenos { kind := .listedShares, proceeds := 200000, cost := 0 } == 0"]
        S["unsupported"] += [("g.disposals.any (·.kind.isRealEstate)", "4400 prenos: the base is the contract price unless below market value (čl. 27: proceeds stand in); exemptions of čl. 31 (contribution to capital, life-maintenance contracts) and the first-home buyer refund not modelled"),
                             ("!g.purchases.isEmpty", "4400 prenos: the buyer pays nothing (čl. 25 st. 1: the seller is the taxpayer, charged on the household's disposals); used motor vehicles (čl. 23 st. 1 tač. 4a, buyer) not modelled")]
        S["notes"].append("RS 4400: Zakon o porezima na imovinu čl. 25, 27, 30, consolidated to Sl. glasnik 94/2024 (A)")
        S["taxes"].append({"oecd": "4400", "tax": "Porez na prenos apsolutnih prava", "statute": st, "dated": "consolidated to Sl. glasnik RS 94/2024 (paragraf.rs)",
                           "grade": "A", "kernel_parts": ["charge on Disposal (seller-borne)"], "unsupported": ["market-value floor on the base", "čl. 31 exemptions", "used vehicles"]})
        _doc(S, "4400 Porez na prenos apsolutnih prava", src,
             ["čl. 25 st. 1: \"Obveznik poreza na prenos apsolutnih prava je prodavac, odnosno prenosilac prava\"",
              "čl. 27 st. 1: \"Osnovica poreza na prenos apsolutnih prava je ugovorena cena u trenutku nastanka poreske obaveze, ukoliko nije niža od tržišne vrednosti\"",
              "čl. 30: \"Stopa poreza na prenos apsolutnih prava iznosi 2,5%.\""])
    if _has7(S, "4300"):
        p6_inherit(S, "nasl", "Porez na nasleđe i poklon", [(0, [(0, 150)]), (0, [(0, 250)])],
                   dict(sibling=0, nieceNephew=0, otherRelative=1, unrelated=1),
                   "Zakon o porezima na imovinu čl. 19 (second order of succession 1,5 %; third and further, unrelated 2,5 %), čl. 21 tač. 1) and 5)-5a) (first order, spouse, parent and public-benefit foundations exempt)",
                   "consolidated to Sl. glasnik RS 94/2024 (paragraf.rs)", "A", src,
                   ["čl. 19: second order of succession \"po stopi od 1,5%\"; third and further order or not related \"po stopi od 2,5%\"",
                    "čl. 21: not paid by \"1) naslednik prvog naslednog reda, supružnik i roditelj ostavioca, odnosno poklonoprimac prvog naslednog reda i supružnik poklonodavca\"; 5)-5a) foundations and endowments for public-benefit purposes"],
                   exempt=("spouse", "child", "grandchild", "parent", "charity"),
                   uns=[("!g.transfers.isEmpty", "čl. 21 tač. 2)-3) (second-order heir: farm assets or one flat after a year in the same household) and the other exemptions not applied; the base is market value less debts (čl. 14: the input value stands in); a parent's gift is taxed at 1,5 % (only the deceased's parent is exempt), taken as exempt here")])


def _hr7(S):
    if S["cc"] != "HR" or not _has7(S, "4300"):
        return
    p6_inherit(S, "nasl", "Porez na nasljedstva i darove", [(0, [(0, 400)])], {},
               "Zakon o lokalnim porezima čl. 4 (cash, claims, securities, movables above EUR 6 700 each), čl. 8 (4 %), čl. 9 (spouse, lineal descendants and ascendants, public bodies, religious communities and foundations exempt)",
               "NN 115/2016 (amended NN 101/17, 114/22, 114/23, 152/24: amendments not read; Porezna uprava page fetched 2026-11-21 states 4 % and the EUR 6 700 threshold)", "A",
               "Zakon o lokalnim porezima, Narodne novine 115/2016 (`hr/law/nn2016_115_2524_zlp.txt`); Porezna uprava, Porez na nasljedstva i darove (`hr/law/pu_nasljedstva.txt`)",
               ["čl. 8: \"Porez na nasljedstva i darove plaća se po stopi od 4%.\"",
                "čl. 9: not paid by \"1. bračni drug, potomci i preci koji čine uspravnu liniju te posvojenici i posvojitelji\"; 3. public bodies, religious communities, foundations",
                "čl. 4 (1): charged on cash, claims, securities and movables whose individual market value exceeds the threshold (Porezna uprava 2025: 6.700,00 eura); real estate is outside (porez na promet nekretnina)"],
               exempt=("spouse", "child", "grandchild", "parent", "charity"),
               ev="fun t => min (pos t.statutoryValue) (pos t.homeValue)",
               uns=[("!g.transfers.isEmpty", "real estate is outside this tax (čl. 4): only the transfer's homeValue is excluded, other real estate in the value is taxed here (overstates); movables up to EUR 6 700 each are not separated")])
    S["guards"].append("p6nasl.tax { kind := .inheritance, value := 300000, homeValue := 200000, relation := .sibling } == 4000")


def _purchase_family(S, key, name, fn_lean, st, kinds):
    """a hand-written duty per purchase (fn_lean defines `p7{key} (p : Purchase) : Int`)"""
    S["lean"] += f"\n/-- {st} -/\n" + fn_lean + (
        f"def p7{key}Charges (ps : List Purchase) : List Charge :=\n  (ps.zipIdx.filter fun (p, _) => {kinds}.contains p.kind).map fun (p, i) =>\n"
        f"    charge .transactions {_q(name)} p.price (fun v => v) (fun _ => p7{key} p) (event := s!\"purchase {{i + 1}}\") (statute := {_q(st)})\n")
    S["families"].append((f"4400 {name}", [".transactions"], f"p7{key}Charges g.purchases"))


def _dk7(S):
    if S["cc"] != "DK" or not _has7(S, "4400"):
        return
    _drop(S, "4400")
    st = "Tinglysningsafgiftsloven (LBK nr 307 af 13/03/2025) § 4 stk. 1 (1.850 kr. og 0,6 pct. af ejerskiftesummen)"
    _purchase_family(S, "tgl", "Tinglysningsafgift (ejerskifte)",
                     "def p7tgl (p : Purchase) : Int :=\n  if [AssetKind.home, .realEstate, .land].contains p.kind then 1850 + divR .down (60 * pos p.price) 10000 else 0\n",
                     st, "[AssetKind.home, .realEstate, .land]")
    S["guards"] += ["p7tgl { kind := .home, price := 2000000 } == 13850", "p7tgl { kind := .land, price := 100 } == 1850",
                    "p7tgl { kind := .vehicle, price := 100000 } == 0"]
    S["unsupported"] += [("!g.purchases.isEmpty", "4400 tinglysningsafgift: the price is taken as the ejerskiftesum (§ 4 stk. 2-3: the public property value where the sale is not at arm's length); the pantebrev fee (§ 5: 1.825 kr. + 1,45 pct.) is not modelled")]
    S["notes"].append("DK 4400: tinglysningsafgiftsloven § 4, LBK 307/2025 (A)")
    S["taxes"].append({"oecd": "4400", "tax": "Tinglysningsafgift (ejerskifte)", "statute": st, "dated": "LBK nr 307 af 13/03/2025, retsinformation.dk (fetched 2026-11-21)",
                       "grade": "A", "kernel_parts": ["charge per Purchase (fixed + rate)"], "unsupported": ["arm's-length rule of § 4 stk. 2-3", "pantebrev fee (§ 5)"]})
    _doc(S, "4400 Tinglysningsafgift", "Lov om afgift af tinglysning af ejendomsret og pant m.v., LBK nr 307 af 13/03/2025, retsinformation.dk ELI XML (`dk/law/tinglysningsafgift_lbk2025_307.txt`)",
         ["§ 4 stk. 1: \"For tinglysning af ejerskifte af fast ejendom eller andele heraf udgør afgiften 1.850 kr. og 0,6 pct. af ejerskiftesummen.\""])


def _pt7(S):
    if S["cc"] != "PT" or not _has7(S, "4400"):
        return
    _drop(S, "4400")
    st = ("CIMT art. 17.º n.º 1 a), c), d), e) (rates: redação Lei 82/2023 and DL 48-A/2024) with the 2025 limits of Lei 45-A/2024 "
          "art. 100.º (HPP 0/2/5/7/8 % marginal to EUR 648 022, then 6 % / 7,5 % on the whole value; other dwellings from 1 %; rústicos 5 %; other urban 6,5 %)")
    hpp, oth = [(0, 0), (104261, 200), (142618, 500), (194458, 700), (324058, 800)], [(0, 100), (104261, 200), (142618, 500), (194458, 700), (324058, 800)]
    sch = lambda b: "Schedule.ofList [" + ", ".join(f"({a}, {c})" for a, c in b) + "]"
    fn = (f"def p7imtWhole (top : Int) (b : List (Int × Int)) (v : Int) : Int :=\n"
          f"  if v ≤ top then (Schedule.ofList b).tax {{}} v else if v ≤ 1128287 then divR .down (600 * v) 10000 else divR .down (750 * v) 10000\n"
          f"def p7imt (p : Purchase) : Int :=\n  match p.kind with\n"
          f"  | .home => if p.additionalHome then p7imtWhole 621501 [{', '.join(f'({a}, {c})' for a, c in oth)}] p.price\n"
          f"             else p7imtWhole 648022 [{', '.join(f'({a}, {c})' for a, c in hpp)}] p.price\n"
          f"  | .realEstate => divR .down (650 * pos p.price) 10000\n  | .land => divR .down (500 * pos p.price) 10000\n  | _ => 0\n")
    _purchase_family(S, "imt", "Imposto municipal sobre as transmissões onerosas de imóveis (IMT)", fn, st, "[AssetKind.home, .realEstate, .land]")

    def whole(top, b, v):
        return _tax(b, v) if v <= top else (600 * v // 10000 if v <= 1128287 else 750 * v // 10000)
    for v in (100000, 300000, 648022, 700000, 2000000):
        S["guards"].append(f"p7imt {{ kind := .home, price := {v} }} == {whole(648022, hpp, v)}")
    for v in (100000, 300000, 700000):
        S["guards"].append(f"p7imt {{ kind := .home, price := {v}, additionalHome := true }} == {whole(621501, oth, v)}")
    S["guards"] += [f"p7imt {{ kind := .realEstate, price := 1000000 }} == 65000", f"p7imt {{ kind := .land, price := 1000000 }} == 50000",
                    "p7imt { kind := .vehicle, price := 1000000 } == 0"]
    S["unsupported"] += [("g.purchases.any (·.kind == .home)", "4400 IMT: a home is taken as habitação própria e permanente unless additionalHome; IMT Jovem (art. 9.º n.º 2-5, buyers up to 35: table b)) and the 10 % rate for buyers in listed tax havens are not applied; base = the higher of price and VPT (art. 12.º: the price stands in)"),
                         ("!g.purchases.isEmpty", "4400: imposto do selo verba 1.1 (0,8 % on acquisitions of real estate) not read: not modelled")]
    S["notes"].append("PT 4400: CIMT art. 17.º (Portal das Finanças) + Lei 45-A/2024 art. 100.º limits for 2025 (A)")
    S["taxes"].append({"oecd": "4400", "tax": "IMT", "statute": st, "dated": "2025 limits: Lei 45-A/2024 art. 100.º (`pt/law/Lei_45_A_2024.txt`); rates: CIMT art. 17.º, Portal das Finanças consolidated code fetched 2026-11-21 (`pt/law/cimt17_portal.txt`, now showing the 2026 limits of Lei 73-A/2025)",
                       "grade": "A", "kernel_parts": ["charge per Purchase (marginal then whole-value rate)"], "unsupported": ["IMT Jovem", "VPT floor on the base", "imposto do selo verba 1.1"]})
    _doc(S, "4400 IMT", "Código do IMT art. 17.º, Portal das Finanças (`pt/law/cimt17_portal.txt`); Lei n.º 45-A/2024 (OE 2025) art. 100.º (`pt/law/Lei_45_A_2024.txt`)",
         ["art. 17.º n.º 1 a) (HPP): marginal 0 / 2 / 5 / 7 / 8 %, then \"6 (taxa única)\" and \"7,5 (taxa única)\"; 2025 limits (Lei 45-A/2024 art. 100.º): \"Até 104 261\", 142 618, 194 458, 324 058, 648 022, \"Superior a 1 128 287\"",
          "c) other dwellings: from 1 % marginal, limits as a) to 324 058, then 621 501; d) \"Aquisição de prédios rústicos - 5%\"; e) \"Aquisição de outros prédios urbanos e outras aquisições onerosas - 6,5%\""])


# ---------------------------------------------------------------- cited absences and notes
def _abs7(S):
    cc = S["cc"]
    if cc == "LV" and _has7(S, "4300"):
        p6_absent(S, "4300", "Inheritance tax (not levied)",
                  "likums Par iedzīvotāju ienākuma nodokli 9. panta 1. daļas 9. punkts (likumi.lv, current text fetched 2026-11-21, `lv/law/iin.txt`)",
                  "no inheritance tax act; income from an inheritance is exempt from the personal income tax (except royalties paid to heirs and inherited state funded pension capital); gifts fall under the income tax rules (not modelled here)",
                  "likumi.lv current text (provision in force in 2025)", grade="A")
    if cc == "EE" and _has7(S, "4400"):
        p6_absent(S, "4400", "Real estate transfer tax (not levied)", _pw7("EE", "Corporate - Other taxes", "pwc_corpother_live"),
                  "transfer tax: none; state and notary fees only (not modelled)", _pwd7("EE", "pwc_corpother_live", "Corporate - Other taxes"), grade="B")
    if cc == "UK" and _has7(S, "4200"):
        p6_absent(S, "4200", "Net wealth tax (not levied)", _pw7("UK"), "annual tax on individuals' wealth: none", _pwd7("UK"), grade="B")
    if cc == "LI" and _has7(S, "4200"):
        old = [t for t in S["taxes"] if str(t.get("oecd")) == "4200" and t.get("grade") == "C"][0]
        p6_note(S, "4200", "Vermögenssteuer (Sollertrag)",
                "Steuergesetz Art. 5 Abs. 1 (Sollertrag 4 %), Art. 14 Abs. 2 Bst. l (the Sollertrag of the taxable wealth is Erwerb), Art. 6 Abs. 1",
                "the wealth tax is a 4 % notional return (Sollertrag) on the taxable net wealth, added to the Erwerb and taxed with the Erwerbssteuer tariff (no separate wealth rate); the 1.x PIT line carries no wealth, so it is not computed. To model: PIT(Erwerb + 4 % x net wealth) - PIT(Erwerb)",
                "SteG, Lilex consolidated PDF Fassung 01.07.2026 (`li/law/steg_konso.txt`; Art. 5 unchanged in 2025 not checked)")
        _ = old


# ---------------------------------------------------------------- 1200 withholding (kernel 2.3.0: cited zeros count as covered)
def _ee7wht(S):
    if S["cc"] != "EE" or S["fam"] != "Corporate" or not any(t.get("grade") == "C" and "ithholding" in t.get("tax", "") for t in S["taxes"]):
        return
    _drop_wht(S)
    st = {"dividend": "TuMS § 41 (dividends not listed: no withholding; the distributing company pays the § 50 income tax)",
          "interest": "TuMS § 41 p. 4, § 29 (7) (interest withheld only from real-estate fund interest; none on other interest)",
          "royalty": "TuMS § 41 p. 8, § 29 (6) p. 4, § 43 (1) p. 2 (10 %)",
          "services": "TuMS § 41 p. 10, § 29 (3), § 43 (1) p. 2 (10 % on services provided in Estonia)"}
    rules = [("dividend", 0), ("interest", 0), ("royalty", 1000), ("services", 1000)]
    rl = ", ".join(f"{{ kind := .{k}, toCompany := none, minStakeBp := 0, rateBp := {r}, statute := {_q(st[k])} }}" for k, r in rules)
    S["lean"] += ("\n/-- Tulumaksuseadus §§ 29, 41, 43 (withholding on payments to non-residents) -/\ndef p7wht : Wht :=\n"
                  f"  {{ name := \"kinnipeetav tulumaks (mitteresident)\", rules := [{rl}] }}\n")
    S["families"].append(("1200 kinnipeetav tulumaks on payments abroad (pass 7)", [".cit"], "(if g.entity == .company then p7wht.charges g.company else [])"))
    for k, r in rules:
        S["guards"].append(f"p7wht.amount {{ kind := .{k}, amount := 100000, toCompany := true, stakeBp := 0 }} == {r * 100000 // 10000}")
    S["unsupported"] += [("g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services)", "1200 withholding: services are taxed only when provided in Estonia (§ 29 (3)); all are taken as provided in Estonia; payments to a non-cooperative jurisdiction (§ 41 p. 11) not separated")]
    S["notes"].append("EE 1200 withholding: TuMS §§ 29, 41, 43, Riigi Teataja via Wayback 2025-06-13 (A)")
    S["taxes"].append({"oecd": "1200", "tax": "Withholding on payments abroad", "statute": "Tulumaksuseadus § 29, § 41 p. 4, 8, 10, § 43 (1) p. 2 (royalties, services 10 %; dividends, interest 0 %)",
                       "dated": "Riigi Teataja, Wayback capture 2025-06-13 (`ee/law/tums_wb.txt`)", "grade": "A", "kernel_parts": ["Wht", "WhtRule zero (cited)"],
                       "unsupported": ["treaty rates and EU directives out of scope (statutory, treaty-free)", "services provided outside Estonia not separated"]})
    _doc(S, "1200 withholding on payments abroad", "Tulumaksuseadus (TuMS), Riigi Teataja, Wayback capture 2025-06-13 (`ee/law/tums_wb.txt`)",
         ["§ 41: \"Tulumaks peetakse kinni: ... 8) mitteresidendile makstavalt litsentsitasult (§ 29 lõike 6 punkt 4); ... 10) mitteresidendile Eestis osutatud teenuste eest makstavalt tasult (§ 29 lõige 3)\"; dividends are not listed",
          "§ 43 (1): \"2) punktides 8–10 ja punktis 12 nimetatud väljamaksetelt – 10%.\"",
          "§ 41 p. 4 with § 29 (7): interest withheld only where it is taxable under § 29 (7) (funds holding mostly Estonian real estate)"])


# ---------------------------------------------------------------- 1100 (P3) gains, B
def _hr7gains(S):
    if S["cc"] != "HR" or not _has7(S, "1100"):
        return
    p6_gains(S, "cg", "Porez na dohodak od kapitalnih dobitaka", "Zakon o porezu na dohodak (capital gains on financial assets 12 %; exempt after two years of holding)",
             _pwd7("HR", "pwc_indincome_wb2025", "Individual - Income determination"), "B", _pw7("HR", "Individual - Income determination", "pwc_indincome_wb2025"),
             ["capital gains on financial assets disposed of within 2 years of acquisition: 12 %; exempt after 2 years and between spouses / close family"],
             sec=dict(bands=[(0, 1200)], hold=24),
             uns=[("g.disposals.any (·.kind.isRealEstate)", "1100 real estate gains (income from property, taxable within 2 years) not modelled: the B source gives no rate"),
                  ("!g.disposals.isEmpty", "the B source's family-transfer exemption is not applied (disposals are taken as sales to third parties)")])


# ---------------------------------------------------------------- P7 triage (5200 / 6000 grade-C entries; no output change)
_T5200 = ("blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); "
          "kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act")
_T6000 = {
 "AT": "minor here: Kommunalsteuer and Dienstgeberbeitrag are payroll (P4); Stabilitätsabgabe is banks only",
 "BE": "minor here: the securities-account tax is a 4200 item; regional taxes left",
 "CH": "model (small): Kirchensteuer ZH (multiplier of the cantonal simple tax) and Personalsteuer CHF 24",
 "DE": "model (high revenue): Kirchensteuer 8 % / 9 % of the income tax (Land church-tax acts); needs a church-membership input",
 "ES": "model for companies: IAE (TRLRHL arts. 78-91), exempt below EUR 1 m turnover; temporary bank and energy levies sector-only (minor)",
 "FR": "model (high revenue): CFE (CGI art. 1447) and CVAE (art. 1586 ter, being phased out); taxe d'habitation on second homes",
 "HU": "model (high revenue): helyi iparűzési adó up to 2 % of adjusted turnover (Budapest 2 %); KATA/KIVA optional regimes",
 "IT": "minor here: IRAP recorded under CIT (P2); imposta di bollo on documents small",
 "LU": "minor here: taxe d'abonnement concerns funds only",
 "PL": "minor here: bank tax and retail sales tax are sector taxes",
 "PT": "minor here: CESE is an energy-sector levy; derrama estadual is under CIT (P2)",
 "RU": "obsolete placement: transport tax belongs to 5200; mineral extraction tax is sector-only (minor)",
 "SK": "minor here: bank levy is sector-only; licence fees small",
}


def _triage7(S):
    if S["fam"] != "Other":
        return
    for t in S["taxes"]:
        if t.get("grade") != "C" or t.get("triage"):
            continue
        o = str(t.get("oecd"))
        if o == "5200":
            t["triage"] = _T5200
        elif o == "6000":
            t["triage"] = _T6000.get(S["cc"], "minor: no other national tax recorded by the registry; to confirm against the country's list of taxes")
        else:
            continue
        S["doc"] += f"\n* **{o} triage (pass 7)**: {t['triage']}\n"


def p7_rows(S):
    for f in (_fi7, _mt7, _rs7, _hr7, _abs7, _ee7wht, _hr7gains, _triage7, _dk7, _pt7):
        f(S)
