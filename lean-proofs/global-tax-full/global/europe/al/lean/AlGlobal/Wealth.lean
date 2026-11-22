import AlGlobal.Pit

/-!
# AL 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Ligji për tatimin mbi të ardhurat (dhuratat dhe trashëgimia 15 %)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)


## 4300 Tatimi mbi trashëgiminë dhe dhuratat (pass 6)
Source: PwC Worldwide Tax Summaries, Albania, Individual - Other taxes, accessed 2025-06-13 (Wayback capture; `law/pwc_indother_wb2025.txt`).
* inheritance / gift: 15 %, gross (no cost deduction)
* exempt: legal heirs of 1st and 2nd order; siblings
* exempt thresholds: immovables ALL 5 000 000; movables ALL 1 000 000
-/

namespace AlGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- Ligji për tatimin mbi të ardhurat (15 %; heirs of the first and second order and siblings exempt) -/
def p6trashClass : Relation → Nat
  | _ => 0
def p6trash : InheritanceTax :=
  { name := "Tatimi mbi trashëgiminë dhe dhuratat", classOf := p6trashClass,   classes := [{ allowance := 1000000, sched := Schedule.flat 1500 }],   exemptRelations := [.spouse, .child, .parent, .sibling], lookbackYears := 0 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Tatimi mbi trashëgiminë dhe dhuratat", covers := [.estate],
     run := fun args g prev =>
       p6trash.charges g.transfers "Ligji për tatimin mbi të ardhurat (15 %; heirs of the first and second order and siblings exempt)" }]

def absent : List Absent :=
  []

def notes : List String := ["AL 4300 Tatimi mbi trashëgiminë dhe dhuratat: PwC WWTS Individual - Other taxes, 2025-06-13 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)"] else [])
  ++ (if !g.transfers.isEmpty then ["4300 the ALL 1 000 000 movable-asset threshold is applied to the whole transfer (immovable assets: ALL 5 000 000); grandchildren taken as taxable (the order of heirs is not in the source)"] else [])

#guard p6trash.tax { kind := .inheritance, value := 100000, relation := .spouse } == 0
#guard p6trash.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 0
#guard p6trash.tax { kind := .inheritance, value := 100000, relation := .child } == 0
#guard p6trash.tax { kind := .inheritance, value := 1000000, relation := .child } == 0
#guard p6trash.tax { kind := .inheritance, value := 100000, relation := .sibling } == 0
#guard p6trash.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 0
#guard p6trash.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 0
#guard p6trash.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 0

end AlGlobal.Wealth
