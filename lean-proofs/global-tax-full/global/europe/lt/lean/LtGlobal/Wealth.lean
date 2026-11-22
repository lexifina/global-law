import LtGlobal.Pit

/-!
# LT 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Paveldimo turto mokesčio įstatymas (5 % / 10 %)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, LT, Individual - Other taxes, accessed  (live page; `law/pwc_indother_wb2025.txt`): net wealth tax: none (live page reviewed 2026) (PwC WWTS Individual - Other taxes,  (live page))


## 4300 Paveldimo turto mokestis (pass 6)
Source: PwC Worldwide Tax Summaries, Lithuania, Individual - Other taxes, accessed 2026-11-21 (live page; `law/pwc_indother_live.txt`).
* exempt: spouse, children, parents, guardians, grandparents, grandchildren, siblings; taxable value ≤ EUR 3 000
* rate 5 % (value ≤ EUR 150 000), 10 % (above; taken as a whole-amount slab)
* gift tax: none (gifts are PIT income, 1100)
-/

namespace LtGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- Paveldimo turto mokesčio įstatymas (5 % to EUR 150 000, 10 % above; close relatives exempt; up to EUR 3 000 untaxed) -/
def p6pavClass : Relation → Nat
  | _ => 0
def p6pav : InheritanceTax :=
  { name := "Paveldimo turto mokestis", classOf := p6pavClass,   classes := [{ allowance := 0, slab := [(3000, 0), (150000, 500)], slabTop := 1000 }],   exemptRelations := [.spouse, .child, .parent, .grandchild, .sibling], lookbackYears := 0,   exemptValue := fun t => if t.kind == .gift then pos t.statutoryValue else 0 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Paveldimo turto mokestis", covers := [.estate],
     run := fun args g prev =>
       p6pav.charges g.transfers "Paveldimo turto mokesčio įstatymas (5 % to EUR 150 000, 10 % above; close relatives exempt; up to EUR 3 000 untaxed)" }]

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none (live page reviewed 2026)" }]

def notes : List String := ["LT 4300 Paveldimo turto mokestis: PwC WWTS Individual - Other taxes, 2026-11-21 (live page) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty then ["4300 live page reviewed 2026: the 2025 rules are taken as the same; the slab reading (whole value at 10 % above EUR 150 000) is the B source's wording, the Act was not read"] else [])

#guard p6pav.tax { kind := .inheritance, value := 100000, relation := .spouse } == 0
#guard p6pav.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 0
#guard p6pav.tax { kind := .inheritance, value := 100000, relation := .child } == 0
#guard p6pav.tax { kind := .inheritance, value := 1000000, relation := .child } == 0
#guard p6pav.tax { kind := .inheritance, value := 100000, relation := .sibling } == 0
#guard p6pav.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 0
#guard p6pav.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 5000
#guard p6pav.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 100000
#guard p6pav.tax { kind := .gift, value := 1000000, relation := .unrelated } == 0

end LtGlobal.Wealth
