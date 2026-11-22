import DkGlobal.Pit

/-!
# DK 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Boafgiftsloven (15 % / 25 %)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Denmark, Individual - Other taxes, accessed 2025-05-27 (Wayback capture; `law/pwc_indother_wb2025.txt`): formueskat: abolished from 1997 (PwC WWTS Individual - Other taxes, 2025-05-27 (Wayback capture))


## 4300 Boafgift og tillægsboafgift (pass 6)
Source: PwC Worldwide Tax Summaries, Denmark, Individual - Other taxes, accessed 2025-05-27 (Wayback capture; `law/pwc_indother_wb2025.txt`).
* boafgift 15 %: children and their descendants, stepchildren, parents, 2-year cohabitant; spouse exempt
* tillægsboafgift 25 % on the remainder for other heirs: 15 % + 25 % x 85 % = 36,25 %
* bundfradrag DKK 346 000 (2025, per estate)
-/

namespace DkGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- boafgiftsloven: boafgift 15 %, tillægsboafgift 25 % of the remainder for other heirs; bundfradrag DKK 346 000 (2025) -/
def p6boClass : Relation → Nat
  | .child => 0
  | .grandchild => 0
  | .parent => 0
  | _ => 1
def p6bo : InheritanceTax :=
  { name := "Boafgift og tillægsboafgift", classOf := p6boClass,   classes := [{ allowance := 346000, sched := Schedule.flat 1500 },   { allowance := 346000, sched := Schedule.flat 3625 }],   exemptRelations := [.spouse], lookbackYears := 0,   exemptValue := fun t => if t.kind == .gift then pos t.statutoryValue else 0 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Boafgift og tillægsboafgift", covers := [.estate],
     run := fun args g prev =>
       p6bo.charges g.transfers "boafgiftsloven: boafgift 15 %, tillægsboafgift 25 % of the remainder for other heirs; bundfradrag DKK 346 000 (2025)" }]

def absent : List Absent :=
  [{ oecd := .wealth, why := "formueskat: abolished from 1997" }]

def notes : List String := ["DK 4300 Boafgift og tillægsboafgift: PwC WWTS Individual - Other taxes, 2025-05-27 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty then ["4300 the DKK 346 000 bundfradrag belongs to the estate; it is applied per recipient here; charities and the cohabitant rule not modelled"] else [])
  ++ (if g.transfers.any (·.kind == .gift) then ["4300 gaveafgift (gifts) not modelled"] else [])

#guard p6bo.tax { kind := .inheritance, value := 100000, relation := .spouse } == 0
#guard p6bo.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 0
#guard p6bo.tax { kind := .inheritance, value := 100000, relation := .child } == 0
#guard p6bo.tax { kind := .inheritance, value := 1000000, relation := .child } == 98100
#guard p6bo.tax { kind := .inheritance, value := 100000, relation := .sibling } == 0
#guard p6bo.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 237075
#guard p6bo.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 0
#guard p6bo.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 237075
#guard p6bo.tax { kind := .gift, value := 1000000, relation := .unrelated } == 0

end DkGlobal.Wealth
