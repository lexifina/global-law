import AtGlobal.Pit
import TaxKernel.Global2

/-!
# Austria 2025: Umsatzsteuer (5111) and the main excises (5121)

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

## FT review (2026-11-21, third pass): heating oil
Same RIS text (`at/law/minstg_2025-07-01.txt`). **MinStG § 3 (1) Z 5**: "für 1 000 l gekennzeichnetes Gasöl (§ 9) a) mit
einem Schwefelgehalt von höchstens 10 mg/kg, sofern gleichmäßig verteilt, 98 Euro; b) ansonsten 128 Euro". § 9 (1):
gas oil to be supplied at the Z 5 rate must be marked (gekennzeichnetes Gasöl). The household's `heatingOil` is read as
marked gas oil at lit. a (the low-sulphur rate, as for petrol and diesel lit. a).
-/

namespace AtGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Umsatzsteuer", standard := 2000, reduced := 1000, reduced2 := 1300, threshold := 55000,
    classOf := fun gd => match gd with
      | .food | .water | .books | .newspapers | .medicines | .rent | .hotels | .transport | .restaurants => .reduced
      | .health | .education | .financial | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "UStG 1994 § 10 (1) 20 %, (2) 10 % (Anlage 1, Restaurationsumsätze, Wohnungsvermietung, Beherbergung, Personenbeförderung), (3) 13 %; § 6 (1) Z 8, 9 lit. c, 11, 16, 19, 27 (55 000 €)"

def excise : Excise :=
  { rates := [
      { good := .petrol, name := "Mineralölsteuer (Benzin)", perUnitNum := 482, perUnitDen := 1000, statute := "MinStG 2022 § 3 (1) Z 1 lit. a: 482 EUR / 1 000 l (≥ 46 l biogenic, ≤ 10 mg/kg S)" },
      { good := .diesel, name := "Mineralölsteuer (Gasöl)", perUnitNum := 397, perUnitDen := 1000, statute := "MinStG 2022 § 3 (1) Z 4 lit. a: 397 EUR / 1 000 l (≥ 66 l biogenic, ≤ 10 mg/kg S)" },
      { good := .cigarettes, name := "Tabaksteuer (Zigaretten)", perUnitNum := 835, perUnitDen := 10000, adValoremBp := 3200, statute := "TabStG 2022 § 4 (1) Z 1 lit. d: 32 % of the retail price + 83,50 EUR / 1 000 (from 1 April 2025)" },
      { good := .spirits, name := "Alkoholsteuer", perUnitNum := 12, onPureAlcohol := true, statute := "AlkStG 2022 § 2 (1): 1 200 EUR / 100 l A" },
      { good := .wine, name := "Weinsteuer", statute := "AlkStG 2022 (Weinsteuer): 0 EUR / hl" },
      { good := .heatingOil, name := "Mineralölsteuer (gekennzeichnetes Gasöl)", perUnitNum := 98, perUnitDen := 1000, statute := "MinStG 2022 § 3 (1) Z 5 lit. a: 98 EUR / 1 000 l gekennzeichnetes Gasöl (§ 9), ≤ 10 mg/kg S" }] }

/-- BierStG 2022 § 3 (1): 2 EUR per hl and degree Plato (kernel 2.1 `ExciseRule`, line field \"platoBp\"). -/
def beerRule : ExciseRule :=
  { good := .beer, name := "Biersteuer", perPlatoNum := 2, perPlatoDen := 100,
    statute := "BierStG 2022 § 3 (1): 2 EUR je Hektoliter und Grad Plato" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 USt, 5121 MinSt TabSt AlkSt", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ exciseRuleCharges [beerRule] g }]

def absent : List Absent :=
  []

def notes : List String := ["AT 5111/5121: RIS consolidated texts as of 2025-07-01"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .beer) then ["Biersteuer by the line's \"platoBp\" (degree Plato x 100); a beer line without it bears no Biersteuer"] else [])
  ++ (if g.consumption.any (fun s => s.good == .restaurants) then ["restaurants taken at 10 % (§ 10 (2) Z 1 lit. b); drinks outside Anlage 1 (alcohol, most soft drinks) are 20 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .recreation) then ["recreation taken at 20 %; theatre, cinema, museums, swimming baths are 13 % (§ 10 (3))"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes) then ["cigarettes at the rate from 1 April 2025 (Jan-Mar 2025: 32 % + 80 EUR / 1 000)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .tobaccoOther || s.good == .gas || s.good == .electricity) then ["other tobacco, gas and electricity duties not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .heatingOil) then ["heating oil read as gekennzeichnetes Gasöl at MinStG § 3 (1) Z 5 lit. a (≤ 10 mg/kg S, 98 EUR / 1 000 l); lit. b (128 EUR) otherwise"] else [])

#guard vat.embedded { good := .clothing, amount := 120 } == 20
#guard vat.embedded { good := .food, amount := 110 } == 10
#guard vat.embedded { good := .financial, amount := 110 } == 0
#guard vat.net { turnover := 55000, sales := [{ good := .other, net := 55000 }] } == 0
#guard vat.net { turnover := 55001, sales := [{ good := .other, net := 55001 }] } == 11000
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 482
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 397
#guard excise.duty { good := .cigarettes, amount := 3000, quantity := 10000000 } == 960 + 835
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 480
-- 100 l of 12 degree Plato beer: 2 EUR x 12 = 24 EUR
#guard beerRule.dutyOn { good := .beer, amount := 300, quantity := 100000 } { platoBp := 1200 } == 24
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 98

end AtGlobal.Consumption
