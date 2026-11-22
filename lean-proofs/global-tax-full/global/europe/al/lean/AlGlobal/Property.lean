import AlGlobal.Pit

/-!
# AL 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Ligji për taksat vendore (tatimi mbi kalimin e pronës)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (tatimi mbi pasurinë e paluajtshme): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4400 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Albania, Corporate - Other taxes, accessed 2025-08-03 (Wayback capture; `law/pwc_other_wb2025.txt`): stamp duty on sale contracts of land or property: none; notary tax ALL 1 000 per immovable-property contract (not modelled) (PwC WWTS Corporate - Other taxes, 2025-08-03 (Wayback capture))


## 4100 Tatimi mbi ndërtesat (pass 6)
Source: PwC Worldwide Tax Summaries, Albania, Individual - Other taxes, accessed 2025-06-13 (Wayback capture; `law/pwc_indother_wb2025.txt`).
* building tax a year: residential 0,05 %, commercial 0,2 % of value; unfinished construction 30 % of the rate
* land: per ha / m2 by district (not modelled)
-/

namespace AlGlobal.Property
open TaxKernel TaxKernel.Global

/-- Ligji 9632/2006 për sistemin e taksave vendore (buildings: residential 0,05 %, commercial 0,2 % of value) -/
def p6tnd : PropertyTax := { name := "Tatimi mbi ndërtesat", sched := Schedule.flat 5, kinds := [.home, .realEstate] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4100 Tatimi mbi ndërtesat", covers := [.propertyRecurrent],
     run := fun args g prev =>
       p6tnd.charges g.assets "Ligji 9632/2006 për sistemin e taksave vendore (buildings: residential 0,05 %, commercial 0,2 % of value)" (level := .local) }]

def absent : List Absent :=
  [{ oecd := .transactions, why := "stamp duty on sale contracts of land or property: none; notary tax ALL 1 000 per immovable-property contract (not modelled)" }]

def notes : List String := ["AL 4100 Tatimi mbi ndërtesat: PwC WWTS Individual - Other taxes, 2025-06-13 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .realEstate) then ["4100 realEstate taken as residential (0,05 %); commercial buildings bear 0,2 %; land per m2 not modelled"] else [])

#guard p6tnd.amount { kind := .home, value := 10000000 } == 5000
#guard p6tnd.amount { kind := .home, value := 100000000 } == 50000
#guard p6tnd.amount { kind := .realEstate, value := 10000000 } == 5000
#guard p6tnd.amount { kind := .realEstate, value := 100000000 } == 50000
#guard p6tnd.amount { kind := .deposits, value := 100000 } == 0

end AlGlobal.Property
