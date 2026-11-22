import ByGlobal.Pit

/-!
# BY 2025: Налог на добавленную стоимость (5111); excises not modelled in this pass

Source: Налоговый кодекс Республики Беларусь, Особенная часть (НК 2009 № 71-З), pravo.by (official) as captured by the Internet Archive on 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`, from the 1.x model's law folder); sha256 in `law/SHA256SUMS`.
* ст. 122 п. 2: "Ставка налога на добавленную стоимость в размере десять (10) процентов устанавливается при: ... 2.2. ввозе ... и (или) реализации продовольственных товаров и товаров для детей" (by the list of the Council of Ministers)
* п. 3: "в размере двадцать (20) процентов"; п. 4: "двадцать пять (25) процентов" (telecommunication services)
-/

namespace ByGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Налог на добавленную стоимость", standard := 2000, reduced := 1000, threshold := 0,
    classOf := fun gd => match gd with
      | .food => .reduced
      | _ => .standard }

def vatStatute : String := "Налоговый кодекс (Особенная часть) ст. 122 п. 2 (10 %), п. 3 (20 %), п. 4 (25 %)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Налог на добавленную стоимость", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["BY 5111: pravo.by via Internet Archive 2025-06-14"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["food at 10 % (ст. 122 п. 2.2: only foods on the Government's list; others 20 %)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .communication) then ["telecommunication services at 20 % (25 % under ст. 122 п. 4 not separated)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exemptions (ст. 118) not read: taken at 20 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Налоговый кодекс ст. 155 and приложение 1) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 12000 } == 2000
#guard vat.embedded { good := .food, amount := 11000 } == 1000

end ByGlobal.Consumption
