S = dict(cc="AT", fam="Consumption", imports=["TaxKernel.Global2"],
lean=r"""
/-- BierStG 2022 § 3 (1): 2 EUR per hl and degree Plato (kernel 2.1 `ExciseRule`, line field \"platoBp\"). -/
def beerRule : ExciseRule :=
  { good := .beer, name := "Biersteuer", perPlatoNum := 2, perPlatoDen := 100,
    statute := "BierStG 2022 § 3 (1): 2 EUR je Hektoliter und Grad Plato" }
""",
extra_run=["exciseRuleCharges [beerRule] g"], family_name="5111 USt, 5121 MinSt TabSt AlkSt",
doc=r'''# Austria 2025: Umsatzsteuer (5111) and the main excises (5121)

Sources: RIS, Bundesrecht konsolidiert, "Fassung vom 01.07.2025" (`at/law/*_2025-07-01.html`, sha256 in
`law/SHA256SUMS`, URLs in `law/ARCHIVE_INDEX.tsv`): UStG 1994 (Gesetzesnummer 10004873), Mineralölsteuergesetz 2022
(10004908), Tabaksteuergesetz 2022 (10004877), Alkoholsteuergesetz 2022 (10004876), Biersteuergesetz 2022 (10004874).
* **UStG § 10 (1)**: "Die Steuer beträgt für jeden steuerpflichtigen Umsatz 20% der Bemessungsgrundlage".
  **§ 10 (2)** 10 %: Z 1 lit. a "die Lieferungen ... der in der Anlage 1 aufgezählten Gegenstände" (Anlage 1: food,
  "Wasser (aus Unterposition 2201 90 00)", "Bücher, Broschüren", "Zeitungen und andere periodische Druckschriften",
  "Arzneimittel"), lit. b Restaurationsumsätze with Anlage 1 food and drink; Z 3 lit. a residential letting, lit. c
  "die Beherbergung in eingerichteten Wohn- und Schlafräumen"; "die Beförderung von Personen mit Verkehrsmitteln aller
  Art". **§ 10 (3)** 13 % (theatre, museums, cinema, swimming baths, artists ...).
* Exemptions **§ 6 (1)**: Z 8 lit. a credit and other financial services; Z 9 lit. c "Umsätze aus
  Versicherungsverhältnissen"; Z 11 lit. a private schools; Z 16 letting of land (residential letting taxed at 10 %,
  § 10 (2) Z 3 lit. a); Z 19 "Heilbehandlungen im Bereich der Humanmedizin"; **Z 27** Kleinunternehmer: "die
  Umsatzgrenze von 55 000 Euro (Kleinunternehmergrenze)".
* **MinStG 2022 § 3 (1)**: Z 1 Benzin "mit einem Gehalt an biogenen Stoffen von mindestens 46 l und einem
  Schwefelgehalt von höchstens 10 mg/kg ... 482 Euro; ansonsten 515 Euro" per 1 000 l; Z 4 Gasöle "mindestens 66 l
  ... 397 Euro; ansonsten 425 Euro".
* **TabStG 2022 § 4 (1) Z 1 lit. d**: cigarettes, "wenn die Tabaksteuerschuld nach dem 31. März 2025 entsteht, 32% des
  Kleinverkaufspreises und 83,50 Euro je 1 000 Stück" (lit. c, 1 April 2024 - 31 March 2025: 32 % and 80 Euro).
* **AlkStG 2022 § 2 (1)**: "Die Alkoholsteuer beträgt 1 200 Euro je 100 l A (Regelsatz)"; Weinsteuer and
  Schaumweinsteuer "0 Euro je Hektoliter"; **BierStG 2022 § 3 (1)**: "je Hektoliter Bier 2 € je Grad Plato".
''',
vat=dict(name="Umsatzsteuer", standard=2000, reduced=1000, reduced2=1300, threshold=55000,
  statute="UStG 1994 § 10 (1) 20 %, (2) 10 % (Anlage 1, Restaurationsumsätze, Wohnungsvermietung, Beherbergung, Personenbeförderung), (3) 13 %; § 6 (1) Z 8, 9 lit. c, 11, 16, 19, 27 (55 000 €)",
  classes={"food": "reduced", "water": "reduced", "books": "reduced", "newspapers": "reduced", "medicines": "reduced",
           "rent": "reduced", "hotels": "reduced", "transport": "reduced", "restaurants": "reduced",
           "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt"}),
excise=[dict(good="petrol", name="Mineralölsteuer (Benzin)", num=482, den=1000, statute="MinStG 2022 § 3 (1) Z 1 lit. a: 482 EUR / 1 000 l (≥ 46 l biogenic, ≤ 10 mg/kg S)"),
        dict(good="diesel", name="Mineralölsteuer (Gasöl)", num=397, den=1000, statute="MinStG 2022 § 3 (1) Z 4 lit. a: 397 EUR / 1 000 l (≥ 66 l biogenic, ≤ 10 mg/kg S)"),
        dict(good="cigarettes", name="Tabaksteuer (Zigaretten)", num=835, den=10000, adv=3200, statute="TabStG 2022 § 4 (1) Z 1 lit. d: 32 % of the retail price + 83,50 EUR / 1 000 (from 1 April 2025)"),
        dict(good="spirits", name="Alkoholsteuer", num=12, den=1, pure=True, statute="AlkStG 2022 § 2 (1): 1 200 EUR / 100 l A"),
        dict(good="wine", name="Weinsteuer", num=0, den=1, statute="AlkStG 2022 (Weinsteuer): 0 EUR / hl")],
notes=["AT 5111/5121: RIS consolidated texts as of 2025-07-01"],
unsupported=[("g.consumption.any (fun s => s.good == .beer)", "Biersteuer by the line's \"platoBp\" (degree Plato x 100); a beer line without it bears no Biersteuer"),
  ("g.consumption.any (fun s => s.good == .restaurants)", "restaurants taken at 10 % (§ 10 (2) Z 1 lit. b); drinks outside Anlage 1 (alcohol, most soft drinks) are 20 %"),
  ("g.consumption.any (fun s => s.good == .recreation)", "recreation taken at 20 %; theatre, cinema, museums, swimming baths are 13 % (§ 10 (3))"),
  ("g.consumption.any (fun s => s.good == .cigarettes)", "cigarettes at the rate from 1 April 2025 (Jan-Mar 2025: 32 % + 80 EUR / 1 000)"),
  ("g.consumption.any (fun s => s.good == .tobaccoOther || s.good == .heatingOil || s.good == .gas || s.good == .electricity)", "other tobacco, heating oil, gas and electricity duties not modelled")],
guards=["vat.embedded { good := .clothing, amount := 120 } == 20",
        "vat.embedded { good := .food, amount := 110 } == 10",
        "vat.embedded { good := .financial, amount := 110 } == 0",
        "vat.net { turnover := 55000, sales := [{ good := .other, net := 55000 }] } == 0",
        "vat.net { turnover := 55001, sales := [{ good := .other, net := 55001 }] } == 11000",
        "excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 482",
        "excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 397",
        "excise.duty { good := .cigarettes, amount := 3000, quantity := 10000000 } == 960 + 835",
        "excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 480",
        "-- 100 l of 12 degree Plato beer: 2 EUR x 12 = 24 EUR",
        "beerRule.dutyOn { good := .beer, amount := 300, quantity := 100000 } { platoBp := 1200 } == 24"],
taxes=[{"oecd": "5111", "tax": "Umsatzsteuer", "statute": "UStG 1994 § 10 (1)-(3), Anlage 1; § 6 (1) Z 8, 9 lit. c, 11, 16, 19, 27", "dated": "RIS Fassung vom 01.07.2025", "grade": "A", "kernel_parts": ["Vat"], "unsupported": ["13 % items (§ 10 (3)) not separated from recreation", "restaurant drinks at 20 % not separated", "Anlage 1 item by item"]},
 {"oecd": "5121", "tax": "Mineralölsteuer (petrol, diesel)", "statute": "MinStG 2022 § 3 (1) Z 1, 4", "dated": "RIS Fassung vom 01.07.2025", "grade": "A", "kernel_parts": ["ExciseRate"], "unsupported": ["unblended / high-sulphur rates (515 / 425 €)", "heating oil, LPG, natural gas"]},
 {"oecd": "5121", "tax": "Tabaksteuer (cigarettes)", "statute": "TabStG 2022 § 4 (1) Z 1 lit. c, d", "dated": "RIS Fassung vom 01.07.2025", "grade": "A", "kernel_parts": ["ExciseRate"], "unsupported": ["cigars, fine-cut and other tobacco", "Jan-Mar 2025 rate"]},
 {"oecd": "5121", "tax": "Alkoholsteuer, Weinsteuer", "statute": "AlkStG 2022 § 2 (1) (1 200 €/100 l A); Weinsteuer 0 €/hl", "dated": "RIS Fassung vom 01.07.2025", "grade": "A", "kernel_parts": ["ExciseRate (pure alcohol)"], "unsupported": ["Zwischenerzeugnisse (80 €/hl)", "Schaumwein (0 €/hl) not separated"]},
 {"oecd": "5121", "tax": "Biersteuer", "statute": "BierStG 2022 § 3 (1)", "dated": "RIS Fassung vom 01.07.2025", "grade": "A", "kernel_parts": ["ExciseRule (per degree Plato, kernel 2.1)"], "unsupported": ["small brewery reduced rates (§ 3 (2))"]}])


# ---- FT review (2026-11-21, third pass): heating oil (ftd_ec_oilbulletin_excise_2025 dev; IMPROVE_FT D5-3) ----
S["doc"] += r'''
## FT review (2026-11-21, third pass): heating oil
Same RIS text (`at/law/minstg_2025-07-01.txt`). **MinStG § 3 (1) Z 5**: "für 1 000 l gekennzeichnetes Gasöl (§ 9) a) mit
einem Schwefelgehalt von höchstens 10 mg/kg, sofern gleichmäßig verteilt, 98 Euro; b) ansonsten 128 Euro". § 9 (1):
gas oil to be supplied at the Z 5 rate must be marked (gekennzeichnetes Gasöl). The household's `heatingOil` is read as
marked gas oil at lit. a (the low-sulphur rate, as for petrol and diesel lit. a).
'''
S["excise"] = S["excise"] + [dict(good="heatingOil", name="Mineralölsteuer (gekennzeichnetes Gasöl)", num=98, den=1000,
    statute="MinStG 2022 § 3 (1) Z 5 lit. a: 98 EUR / 1 000 l gekennzeichnetes Gasöl (§ 9), ≤ 10 mg/kg S")]
S["unsupported"] = [((c.replace(" || s.good == .heatingOil", ""), t.replace("other tobacco, heating oil, gas", "other tobacco, gas"))
                     if "heating oil" in t else (c, t)) for c, t in S["unsupported"]] + [
  ("g.consumption.any (fun s => s.good == .heatingOil)", "heating oil read as gekennzeichnetes Gasöl at MinStG § 3 (1) Z 5 lit. a (≤ 10 mg/kg S, 98 EUR / 1 000 l); lit. b (128 EUR) otherwise")]
S["guards"] = S["guards"] + ["excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 98"]
for _t in S["taxes"]:
    if _t.get("tax") == "Mineralölsteuer (petrol, diesel)":
        _t["tax"] = "Mineralölsteuer (petrol, diesel, heating oil)"
        _t["statute"] = "MinStG 2022 § 3 (1) Z 1, 4, 5"
        _t["unsupported"] = ["unblended / high-sulphur rates (515 / 425 / 128 €)", "LPG, natural gas"]
