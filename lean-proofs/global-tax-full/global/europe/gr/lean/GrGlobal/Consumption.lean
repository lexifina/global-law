import GrGlobal.Pit
import TaxKernel.Global2

/-!
# GR 2025: Φόρος προστιθέμενης αξίας (5111); excises not modelled in this pass

Source: ν. 5144/2024 Κύρωση Κώδικα ΦΠΑ, ΦΕΚ Α' 162/11.10.2024 (signed gazette PDF as posted by ΑΑΔΕ, Internet Archive 2025-05-18, `gr/law/kodikas_fpa_n5144_wb20250518.pdf`); sha256 in `law/SHA256SUMS`.
* άρθρο 26: "Ο συντελεστής του ΦΠΑ ορίζεται σε είκοσι τέσσερα τοις εκατό (24%) στη φορολογητέα αξία. Για τα αγαθά και τις υπηρεσίες που περιλαμβάνονται στο Παράρτημα III ... ορίζεται σε δεκατρία τοις εκατό (13%). Για τα αγαθά και τις υπηρεσίες για τα οποία υπάρχει ειδική πρόβλεψη στο Παράρτημα III ... σε έξι τοις εκατό (6%) και σε τέσσερα τοις εκατό (4%) κατά περίπτωση"
* Παράρτημα III Α: 1-32 food items ("4. Κρέατα ...", "6. Γάλα ...", "10. Λαχανικά ..."), "33. Η παράδοση νερού", "35. Η ηλεκτρική ενέργεια ... και το φυσικό αέριο ... έξι τοις εκατό (6%)", 36-37 medicines (6 %), "40. Βιβλία ..." (6 %), newspapers (6 %), "51. Μη αλκοολούχα ποτά"; Β: "2. Η μεταφορά προσώπων", "5. Η διαμονή σε ξενοδοχεία", "9. Η εκμετάλλευση καφενείων, ... εστιατορίων"
* άρθρο 44: small undertakings with supplies in the previous year "αξίας μέχρι δέκα χιλιάδες (10.000) ευρώ"

## FT review (2026-11-21, third pass): natural gas
Same ΦΕΚ Α' 162/11.10.2024 (`gr/law/kodikas_fpa_n5144_wb20250518.txt`), Παράρτημα III item **35**: "Η ηλεκτρική
ενέργεια (Δ.Κ. 2716) και το φυσικό αέριο (Δ.Κ. ΕΧ 2711). Ο συντελεστής του φόρου για τα αγαθά της παρούσας περίπτωσης
ορίζεται σε έξι τοις εκατό (6%)." The model had electricity at 6 % and gas at 24 %.


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), GR excise records for the situation on 1 July 2025 (tobacco 4075, alcohol 4073, energy 4074; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `gr/law/tedb_*.json`).
* TEDB GR manufactured tobacco (1.7.2025): 82.5 EUR per 1 000 cigarettes + 26.0 % of the retail selling price, at least 117.5 EUR per 1 000
* TEDB GR beer (1.7.2025): 5 EUR per hl and degree Plato
* TEDB GR still wine (1.7.2025): 0 EUR per hl of product
* TEDB GR ethyl alcohol (1.7.2025): 2450 EUR per hl of pure alcohol
* TEDB GR energy products (1.7.2025): unleaded petrol 700 EUR per 1 000 l
* TEDB GR energy products (1.7.2025): gas oil used as propellant 410 EUR per 1 000 l
-/

namespace GrGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Φόρος προστιθέμενης αξίας", standard := 2400, reduced := 1300, superReduced := 600, threshold := 10000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .food | .nonAlcoholic | .water | .transport | .hotels | .restaurants => .reduced
      | .electricity | .medicines | .books | .newspapers | .gas => .superReduced
      | _ => .standard }

def vatStatute : String := "Κώδικας ΦΠΑ (ν. 5144/2024, ΦΕΚ Α' 162/11.10.2024) άρθρο 26 (24 %, 13 %, 6 %), Παράρτημα III, άρθρο 44 (10.000 ευρώ)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 33, perUnitDen := 400, adValoremBp := 2600, minNum := 47, minDen := 400, statute := "TEDB GR manufactured tobacco (1.7.2025): 82.5 EUR per 1 000 cigarettes + 26.0 % of the retail selling price, at least 117.5 EUR per 1 000" },
      { good := .wine, name := "Excise duty on still wine", statute := "TEDB GR still wine (1.7.2025): 0 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 49, perUnitDen := 2, onPureAlcohol := true, statute := "TEDB GR ethyl alcohol (1.7.2025): 2450 EUR per hl of pure alcohol" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 7, perUnitDen := 10, statute := "TEDB GR energy products (1.7.2025): unleaded petrol 700 EUR per 1 000 l" },
      { good := .diesel, name := "Excise duty on gas oil used as propellant", perUnitNum := 41, perUnitDen := 100, statute := "TEDB GR energy products (1.7.2025): gas oil used as propellant 410 EUR per 1 000 l" }] }

/-- TEDB GR beer (1.7.2025): 5 EUR per hl and degree Plato (kernel 2.1 `ExciseRule`, line field "platoBp"). -/
def gxBeerRule : ExciseRule :=
  { good := .beer, name := "Excise duty on beer", perPlatoNum := 1, perPlatoDen := 20,   statute := "TEDB GR beer (1.7.2025): 5 EUR per hl and degree Plato" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Φόρος προστιθέμενης αξίας", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ exciseRuleCharges [gxBeerRule] g }]

def absent : List Absent :=
  []

def notes : List String := ["GR 5111: codification ν. 5144/2024 (in force 2025)", "GR 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"] else [])
  ++ (if !g.consumption.isEmpty then ["island rates reduced by 30 % (άρθρο 26 παρ. 4) not modelled; restaurant alcohol and coffee drinks at 24 % not separated"] else [])
  ++ (if g.entity == .company then ["άρθρο 44 threshold as codified in 2024: a 2025 amendment by ν. 5162/2024 not checked"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Εθνικός Τελωνειακός Κώδικας (ν. 2960/2001) άρθρα 73-78, 87, 98 (not read)) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer) then ["5121 Excise duty on beer: charged by the line's \"platoBp\" (degree Plato x 100); a beer line without it bears no beer duty"] else [])
  ++ (if g.consumption.any (fun s => s.good == .heatingOil) then ["5121 GR heating gas oil not charged: seasonal rate (280 EUR 15 October-30 April, 410 otherwise) and the purchase is undated (grade C)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 GR: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12400 } == 2400
#guard vat.embedded { good := .food, amount := 11300 } == 1300
#guard vat.embedded { good := .electricity, amount := 10600 } == 600
#guard vat.net { turnover := 10000, sales := [{ good := .other, net := 10000 }] } == 0
#guard vat.embedded { good := .gas, amount := 106 } == 6
#guard gxBeerRule.dutyOn { good := .beer, amount := 300, quantity := 100000 } { platoBp := 1200 } == 60
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 1382
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 0
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 980
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 700
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 410

end GrGlobal.Consumption
