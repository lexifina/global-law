import TaxKernel.Global
import R5Common

/-!
# Tunisia 2025: TVA (5111); droit de consommation not computed (5121)

Sources (all in `R5/tn/law/`, SHA256SUMS):
* Code de la TVA, DGELF edition "mis à jour au 1er janvier 2022" (`code_tva_2022.pdf`, chaexpert.com mirror):
  art. 7 (19 % on everything not under another rate; 7 % on tableau « B » nouveau; 13 % under art. 7(3) on
  pétrole lampant, gas-oil, fuel-oil (EX 27-10), gaz de pétrole, propane, butane (EX 27-11), domestic low-voltage
  electricity, liberal professions, promoters' dwellings); tableau « A » nouveau (exemptions) I-1 fresh milk, I-18
  books and newspapers, I-41 flour, semolina, bread, couscous, pasta, I-43/44 edible oils, II-12 unfurnished
  residential lettings, II-13 insurance under the taxe unique; tableau « B » nouveau (7 %) I-4 finished
  pharmaceutical products, II-1 doctors, dentists, laboratories, nurses, II-2 transport, II-4 restaurants and cafés
  of the first category, II-6 education and crèches, II-16 hotel undertakings, II-29 fixed telephony / ADSL.
* LF 2023 (Décret-loi 2022-79, JORT 22 Dec 2022, `Decret-loi2022_79_compressed.pdf`) art. 44: third dash of art.
  7(3) (liberal professions, 13 %) repealed: 19 % from 2023; aesthetic medicine taken out of tableau B II-1.
* LF 2024 (Loi 2023-13, `Loi2023_13.pdf`) art. 39: promoters' dwellings stay at 13 % until 1 January 2025.
* LF 2025 (Loi 2024-48 of 9 Dec 2024, JORT n° 149, `Loi2024_48.pdf`) art. 31: domestic low-voltage electricity
  13 % only where monthly consumption exceeds 300 kWh, tableau B n° 30 (7 %) at or below; art. 34(3): pharmaceutical
  inputs leave tableau B I-4 (finished products stay); art. 64: promoters' dwellings to tableau B n° 31 (7 %) up to
  TND 400,000 excl. tax, else 19 %.
Not computed: droit de consommation (Code, part 3; schedules not read), régime forfaitaire for small traders.
-/

namespace TnGlobal
open TaxKernel TaxKernel.Global R5Common

/-- 300 kWh a month, as thousandths of a kWh over a year (`Spend.quantity` is in thousandths). -/
def elecMonthlyCap : Int := 300 * 12 * 1000

/-- Domestic electricity over the 300 kWh/month line (LF 2025 art. 31): only known when a quantity is given. -/
def elecHigh (xs : List Spend) : Bool :=
  isum ((xs.filter (·.good == .electricity)).map (·.quantity)) > elecMonthlyCap

def tvaOf (high : Bool) : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1900, reduced := 700, reduced2 := 1300,
    classOf := fun g => match g with
      | .diesel | .heatingOil => .reduced2
      | .electricity => if high then .reduced2 else .reduced
      | .medicines | .health | .transport | .education | .restaurants | .hotels => .reduced
      | .food | .rent | .books | .newspapers | .insurance => .exempt
      | _ => .standard }

def tva : Vat := tvaOf false

def consumption : Family :=
  { name := "5111 TVA", covers := [.vat],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [(tvaOf (elecHigh g.consumption)).basketCharge g.consumption
          "Code TVA art. 7 (19 %; 13 % art. 7(3) as amended by LF 2023 art. 44 and LF 2025 art. 31, 64), tableaux A and B nouveaux; LF 2025 art. 31 (tableau B n° 30)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
        [tva.businessCharge g.company "Code TVA art. 7, 9 (deduction)"] else []) }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then ["TVA: food taken as exempt (tableau A I-1, I-41, I-43/44: milk, flour, bread, couscous, pasta, edible oils); preserves of tomato, harissa, sardines and sugar are 7 % (tableau B I-5, I-9 bis), other foods 19 %"] else [])
  ++ (if g.consumption.any (·.good == .electricity) && isum ((g.consumption.filter (·.good == .electricity)).map (·.quantity)) == 0 then
    ["TVA on electricity: no kWh given, taken at or below 300 kWh a month (7 %, tableau B n° 30, LF 2025 art. 31)"] else [])
  ++ (if g.consumption.any (·.good == .gas) then ["TVA on gas: the basket good is metered gas (kWh), taken as natural gas at 19 % (art. 7 first paragraph); the 13 % of art. 7(3) covers only petroleum gas, propane and butane (EX 27-11), e.g. bottled LPG"] else [])
  ++ (if g.consumption.any (·.good == .restaurants) then ["TVA on restaurants: 7 % applies to first-category restaurants and cafés (tableau B II-4) and hotel undertakings (II-16); others at 19 % or under the forfait"] else [])
  ++ (if g.consumption.any (·.good == .communication) then ["TVA on communication: 19 %; fixed telephony and ADSL for individuals is 7 % (tableau B II-29)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic) then
    ["droit de consommation (Code TVA, part 3, schedules): not read; not computed"] else [])

#guard tva.embedded { good := .clothing, amount := 11900 } == 1900
#guard tva.embedded { good := .health, amount := 10700 } == 700
#guard tva.embedded { good := .diesel, amount := 11300 } == 1300
#guard (tvaOf true).embedded { good := .electricity, amount := 11300 } == 1300
#guard tva.embedded { good := .electricity, amount := 10700 } == 700
#guard tva.embedded { good := .petrol, amount := 11900 } == 1900
-- metered (natural) gas: 19 %, not the art. 7(3) petroleum-gas rate
#guard tva.embedded { good := .gas, amount := 11900 } == 1900 && (tvaOf true).rateOf .gas == 1900
#guard tva.embedded { good := .rent, amount := 10000 } == 0
#guard elecHigh [{ good := .electricity, amount := 1, quantity := 3600001 }] && !elecHigh [{ good := .electricity, amount := 1, quantity := 3600000 }]

end TnGlobal
