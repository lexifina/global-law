import RsGlobal.Pit

/-!
# RS 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Zakon o porezima na imovinu (porez na nasleđe i poklon)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)


## 4300 Porez na nasleđe i poklon (pass 6)
Source: Zakon o porezima na imovinu (Sl. glasnik RS 26/2001 ... 94/2024), consolidated text, paragraf.rs, fetched 2026-11-21 (`rs/law/zpi.txt`).
* čl. 19: second order of succession "po stopi od 1,5%"; third and further order or not related "po stopi od 2,5%"
* čl. 21: not paid by "1) naslednik prvog naslednog reda, supružnik i roditelj ostavioca, odnosno poklonoprimac prvog naslednog reda i supružnik poklonodavca"; 5)-5a) foundations and endowments for public-benefit purposes
-/

namespace RsGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- Zakon o porezima na imovinu čl. 19 (second order of succession 1,5 %; third and further, unrelated 2,5 %), čl. 21 tač. 1) and 5)-5a) (first order, spouse, parent and public-benefit foundations exempt) -/
def p6naslClass : Relation → Nat
  | .sibling => 0
  | .nieceNephew => 0
  | .otherRelative => 1
  | .unrelated => 1
  | _ => 1
def p6nasl : InheritanceTax :=
  { name := "Porez na nasleđe i poklon", classOf := p6naslClass,   classes := [{ allowance := 0, sched := Schedule.flat 150 },   { allowance := 0, sched := Schedule.flat 250 }],   exemptRelations := [.spouse, .child, .grandchild, .parent, .charity], lookbackYears := 0 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4300 Porez na nasleđe i poklon", covers := [.estate],
     run := fun args g prev =>
       p6nasl.charges g.transfers "Zakon o porezima na imovinu čl. 19 (second order of succession 1,5 %; third and further, unrelated 2,5 %), čl. 21 tač. 1) and 5)-5a) (first order, spouse, parent and public-benefit foundations exempt)" }]

def absent : List Absent :=
  []

def notes : List String := ["RS 4300 Porez na nasleđe i poklon: consolidated to Sl. glasnik RS 94/2024 (paragraf.rs) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)"] else [])
  ++ (if !g.transfers.isEmpty then ["4300 čl. 21 tač. 2)-3) (second-order heir: farm assets or one flat after a year in the same household) and the other exemptions not applied; the base is market value less debts (čl. 14: the input value stands in); a parent's gift is taxed at 1,5 % (only the deceased's parent is exempt), taken as exempt here"] else [])

#guard p6nasl.tax { kind := .inheritance, value := 100000, relation := .spouse } == 0
#guard p6nasl.tax { kind := .inheritance, value := 1000000, relation := .spouse } == 0
#guard p6nasl.tax { kind := .inheritance, value := 100000, relation := .child } == 0
#guard p6nasl.tax { kind := .inheritance, value := 1000000, relation := .child } == 0
#guard p6nasl.tax { kind := .inheritance, value := 100000, relation := .sibling } == 1500
#guard p6nasl.tax { kind := .inheritance, value := 1000000, relation := .sibling } == 15000
#guard p6nasl.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 2500
#guard p6nasl.tax { kind := .inheritance, value := 1000000, relation := .unrelated } == 25000

end RsGlobal.Wealth
