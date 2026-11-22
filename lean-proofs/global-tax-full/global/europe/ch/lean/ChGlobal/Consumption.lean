import ChGlobal.Pit

/-!
# Switzerland 2025: Mehrwertsteuer (5111) and the main federal excises (5121)

Sources: fedlex consolidations in force on 1 July 2025 (`ch/law/*.html`, sha256 in `law/SHA256SUMS`, URLs in
`law/ARCHIVE_INDEX.tsv`): MWSTG SR 641.20 (version 2025-03-31), TStG SR 641.31 (2025-01-01), MinöStG SR 641.61
(2025-01-01), AlkV SR 680.11 (2022-01-01, the last consolidation before 2025-07-01), AlkG SR 680 (2024-06-01).
* **MWSTG Art. 25 (1)**: "Die Steuer beträgt 8,1 Prozent (Normalsatz)"; **(2)** "Der reduzierte Steuersatz von 2,6
  Prozent findet Anwendung: a. auf der Lieferung folgender Gegenstände: 1. Wasser in Leitungen, 2. Lebensmittel nach
  dem Lebensmittelgesetz ..., mit Ausnahme alkoholischer Getränke, ... 8. Medikamente, 9. Zeitungen, Zeitschriften,
  Bücher"; **(4)** "Die Steuer auf Beherbergungsleistungen beträgt 3,8 Prozent (Sondersatz)".
* **Art. 21 (2)** exempt: Ziff. 2, 3 hospital and medical treatment, 11 education, 18 insurance, 19 money and capital
  transactions, 21 letting of immovable property. **Art. 10 (2) lit. a**: not liable if "weniger als 100 000 Franken
  Umsatz".
* **MinöStG Art. 12 (1)** and Anhang 1: petrol ("Benzin und seine Fraktionen", Treibstoff) 431.20 Fr., Dieselöl 458.70
  Fr. je 1000 l bei 15 °C; **Art. 12 (2)**: "Der Mineralölsteuerzuschlag beträgt 300 Franken je 1000 l bei 15 °C".
* **TStG** (cigarettes): "Die Steuer beträgt 11,832 Rappen je Stück und 25 Prozent des Kleinhandelspreises, mindestens
  21,210 Rappen je Stück."
* **AlkV Art. 21** (Art. 22 Abs. 1 AlkG): "Die Steuer beträgt 29 Franken je Liter reinen Alkohol."
-/

namespace ChGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Mehrwertsteuer", standard := 810, reduced := 260, reduced2 := 380, threshold := 99999,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .water | .medicines | .books | .newspapers => .reduced
      | .hotels => .reduced2
      | .health | .education | .insurance | .financial | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "MWSTG Art. 25 (1) 8,1 %, (2) 2,6 %, (4) 3,8 %; Art. 21 (2) Ziff. 2, 3, 11, 18, 19, 21; Art. 10 (2) lit. a (< 100 000 Fr.)"

def excise : Excise :=
  { rates := [
      { good := .petrol, name := "Mineralölsteuer + Zuschlag (Benzin)", perUnitNum := 73120, perUnitDen := 100000, statute := "MinöStG Art. 12 (1) Anhang 1 (431.20 Fr.) + Art. 12 (2) (300 Fr.) je 1000 l" },
      { good := .diesel, name := "Mineralölsteuer + Zuschlag (Dieselöl)", perUnitNum := 75870, perUnitDen := 100000, statute := "MinöStG Art. 12 (1) Anhang 1 (458.70 Fr.) + Art. 12 (2) (300 Fr.) je 1000 l" },
      { good := .cigarettes, name := "Tabaksteuer (Zigaretten)", perUnitNum := 11832, perUnitDen := 100000, adValoremBp := 2500, minNum := 21210, minDen := 100000, statute := "TStG: 11,832 Rp./Stück + 25 % des Kleinhandelspreises, mindestens 21,210 Rp./Stück" },
      { good := .spirits, name := "Alkoholsteuer", perUnitNum := 29, onPureAlcohol := true, statute := "AlkV Art. 21 (AlkG Art. 22): 29 Fr. je Liter reinen Alkohol" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 MWST, 5121 MinöSt TSt AlkSt", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["CH 5111/5121: fedlex consolidations in force on 2025-07-01"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .beer) then ["Biersteuer (BStG, by Stammwürze class) not read: not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .restaurants) then ["restaurant meals taken at the standard rate (gastgewerbliche Leistungen; Art. 25 (3) not quoted)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .tobaccoOther || s.good == .heatingOil || s.good == .gas) then ["fine-cut tobacco, cigars, heating oil and gas taxes (incl. CO2-Abgabe) not modelled"] else [])

#guard vat.embedded { good := .clothing, amount := 1081 } == 81
#guard vat.embedded { good := .food, amount := 1026 } == 26
#guard vat.embedded { good := .hotels, amount := 1038 } == 38
#guard vat.net { turnover := 99999, sales := [{ good := .other, net := 99999 }] } == 0
#guard vat.net { turnover := 100000, sales := [{ good := .other, net := 100000 }] } == 8100
#guard excise.duty { good := .petrol, amount := 2000, quantity := 1000000 } == 731
#guard excise.duty { good := .diesel, amount := 2000, quantity := 1000000 } == 758
-- 100 000 cigarettes: the minimum (21 210 Fr.) binds at a retail price of 30 000 Fr. (11 832 + 7 500)
#guard excise.duty { good := .cigarettes, amount := 30000, quantity := 100000000 } == 21210
#guard excise.duty { good := .cigarettes, amount := 60000, quantity := 100000000 } == 11832 + 15000
#guard excise.duty { good := .spirits, amount := 3000, quantity := 100000, abvBp := 4000 } == 1160

end ChGlobal.Consumption
