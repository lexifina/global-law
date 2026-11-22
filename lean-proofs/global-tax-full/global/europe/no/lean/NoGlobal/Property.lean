import NoGlobal.Pit

/-!
# NO 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Dokumentavgiftsloven (2,5 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Eigedomsskattelova (Oslo)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Dokumentavgift (pass 6)
Source: PwC Worldwide Tax Summaries, Norway, Corporate - Other taxes, accessed 2025-05-15 (Wayback capture; `law/pwc_corpother_wb2025.txt`).
* dokumentavgift 2,5 % of market value on registration of a real estate title transfer

* **4100 Recurrent property tax (pass 6 note, grade C)**: Eigedomsskattelova (Oslo): eiendomsskatt is optional and set by each municipality (homes 1-4 per mille, a basic deduction may apply); Oslo's vedtak not read (pass 6 note (PwC WWTS 2025 captures on disk))
-/

namespace NoGlobal.Property
open TaxKernel TaxKernel.Global

/-- Stortingets vedtak om dokumentavgift (2,5 % of market value) -/
def p6dok : TransferDuty := { name := "Dokumentavgift", sched := Schedule.flat 250, kinds := [.home, .realEstate, .land] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Dokumentavgift", covers := [.transactions],
     run := fun args g prev =>
       p6dok.charges g.purchases "Stortingets vedtak om dokumentavgift (2,5 % of market value)" }]

def absent : List Absent :=
  []

def notes : List String := ["NO 4400 Dokumentavgift: PwC WWTS Corporate - Other taxes, 2025-05-15 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 share transfers and cooperative flats are outside (not separated)"] else [])

#guard p6dok.amount { kind := .home, price := 200000 } == 5000
#guard p6dok.amount { kind := .home, price := 2000000 } == 50000
#guard p6dok.amount { kind := .vehicle, price := 100000 } == 0

end NoGlobal.Property
