import UaGlobal.Pit

/-!
# UA 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Податковий кодекс / державне мито (1 %); ПДФО on the seller): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Податковий кодекс ст. 266 (податок на нерухоме майно, Київ)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Державне мито (real estate sales) (pass 6)
Source: PwC Worldwide Tax Summaries, Ukraine, Corporate - Other taxes, accessed 2025-06-22 (Wayback capture; `law/pwc_corpother_wb2025.txt`).
* державне мито 1 %: real estate sales, commodity-exchange operations

* **4100 Recurrent property tax (pass 6 note, grade C)**: Податковий кодекс ст. 266 (податок на нерухоме майно, Київ): податок на нерухоме майно: per-m2 rates set by local councils (up to 1,5 % of the minimum wage per m2) with a per-dwelling area exemption; Kyiv decision not read (pass 6 note (PwC WWTS 2025 captures on disk))
-/

namespace UaGlobal.Property
open TaxKernel TaxKernel.Global

/-- Декрет КМУ про державне мито (1 % of the sale price of real estate) -/
def p6mito : TransferDuty := { name := "Державне мито (real estate sales)", sched := Schedule.flat 100, kinds := [.home, .realEstate, .land] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Державне мито (real estate sales)", covers := [.transactions],
     run := fun args g prev =>
       p6mito.charges g.purchases "Декрет КМУ про державне мито (1 % of the sale price of real estate)" }]

def absent : List Absent :=
  []

def notes : List String := ["UA 4400 Державне мито (real estate sales): PwC WWTS Corporate - Other taxes, 2025-06-22 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 the 1 % levy to the Pension Fund on real estate purchases (not in the source) not modelled"] else [])

#guard p6mito.amount { kind := .home, price := 200000 } == 2000
#guard p6mito.amount { kind := .home, price := 2000000 } == 20000
#guard p6mito.amount { kind := .vehicle, price := 100000 } == 0

end UaGlobal.Property
