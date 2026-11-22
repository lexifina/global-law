import IsGlobal.Pit

/-!
# IS 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Lög nr. 14/2004 um erfðafjárskatt (10 %)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, IS, Individual - Other taxes, accessed  (live page; `law/pwc_indother_wb2025.txt`): net wealth tax: none at present (PwC WWTS Individual - Other taxes,  (live page))


## 4300 Erfðafjárskattur (pass 6)
Source: PwC Worldwide Tax Summaries, Iceland, Individual - Other taxes, accessed 2026-11-21 (live page; `law/pwc_indother_live.txt`).
* erfðafjárskattur 10 % of net value; allowance ISK 6 498 129; surviving spouse / cohabitant exempt
* advance inheritance: 10 %, no allowance (not modelled)


## Pass 16 (year in force)
The untaxed first part of an inheritance in 2025 is ISK 6 498 129 (PwC Iceland, Individual - Other taxes, Internet Archive 2025-06-13, `is/law/pwc_indother_wb20250613.txt`); the live page's ISK 6 789 790 (read in pass 6) is the 2026 amount. Rate 10 % unchanged.
-/

namespace IsGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- lög nr. 14/2004 um erfðafjárskatt (10 %; first ISK 6 498 129 untaxed; spouse exempt) -/
def p6erfdClass : Relation → Nat
  | _ => 0
def p6erfd : InheritanceTax :=
  { name := "Erfðafjárskattur", classOf := p6erfdClass,   classes := [{ allowance := 6498129, sched := Schedule.flat 1000 }],   exemptRelations := [.spouse], lookbackYears := 0,   exemptValue := fun t => if t.kind == .gift then pos t.statutoryValue else 0 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Erfðafjárskattur", covers := [.estate],
     run := fun args g prev =>
       p6erfd.charges g.transfers "lög nr. 14/2004 um erfðafjárskatt (10 %; first ISK 6 498 129 untaxed; spouse exempt)" }]

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none at present" }]

def notes : List String := ["IS 4300 Erfðafjárskattur: PwC WWTS Individual - Other taxes, 2026-11-21 (live page) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty then ["4300 the allowance belongs to the estate; applied per recipient here; advance inheritances (10 % without allowance) not separated from gifts"] else [])
  ++ (if g.transfers.any (·.kind == .gift) then ["4300 gifts are income (1100) or advance inheritance: not modelled here"] else [])

#guard p6erfd.tax { kind := .inheritance, value := 100000, relation := .spouse } == 0
#guard p6erfd.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 0
#guard p6erfd.tax { kind := .inheritance, value := 100000, relation := .child } == 0
#guard p6erfd.tax { kind := .inheritance, value := 1000000, relation := .child } == 0
#guard p6erfd.tax { kind := .inheritance, value := 100000, relation := .sibling } == 0
#guard p6erfd.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 0
#guard p6erfd.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 0
#guard p6erfd.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 0
#guard p6erfd.tax { kind := .gift, value := 1000000, relation := .unrelated } == 0
#guard p6erfd.tax { kind := .inheritance, value := 10000000, relation := .child } == 350187

end IsGlobal.Wealth
