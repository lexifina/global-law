import MeGlobal.Pit

/-!
# ME 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Zakon o porezu na promet nepokretnosti (3 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Zakon o porezu na nepokretnosti (Podgorica)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4100 Recurrent property tax (pass 6 note, grade C)**: Zakon o porezu na nepokretnosti (Podgorica): porez na nepokretnosti: 0,25-1 % of market value as each municipality sets; Podgorica decision not read (pass 6 note (PwC WWTS 2025 captures on disk))

* **4400 Real-estate transfer and stamp duties (pass 6 note, grade C)**: Zakon o porezu na promet nepokretnosti (3 %): porez na promet nepokretnosti: progressive 3-6 % on market value; the band limits are not in the B source and the act was not read (pass 6 note (PwC WWTS 2025 captures on disk))


## 4400 Porez na promet nepokretnosti (pass 6)
Source: Službeni list Crne Gore 28/2023; read from lexifina/montenegro-law `zakon/2023/333502` (commit 4995845c3, in force 1.1.2024).
* čl. 11 (28/2023): 3 % up to 150 000 EUR; 4 500 EUR + 5 % on the excess above 150 000; 22 000 EUR + 6 % on the excess above 500 000
* Hand check: purchase of 200 000: 4 500 + 2 500 = 7 000
-/

namespace MeGlobal.Property
open TaxKernel TaxKernel.Global

/-- Zakon o porezu na promet nepokretnosti čl. 11 (redakcija Sl. list CG 28/2023, od 1.1.2024) -/
def p6meTransfer : TransferDuty := { name := "Porez na promet nepokretnosti", sched := Schedule.ofList [(0, 300), (150000, 500), (500000, 600)], kinds := [.home, .realEstate, .land] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Porez na promet nepokretnosti", covers := [.transactions],
     run := fun args g prev =>
       p6meTransfer.charges g.purchases "Zakon o porezu na promet nepokretnosti čl. 11 (redakcija Sl. list CG 28/2023, od 1.1.2024)" }]

def absent : List Absent :=
  []

def notes : List String := ["ME 4400 Porez na promet nepokretnosti: law as published with amendment 28/2023 in force from 1.1.2024; next amendments 33/2026 and 132/2026 (2026): text in force all of 2025 (via lexifina/montenegro-law) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 the first-order heirs' and other exemptions (čl. 6-7) not applied"] else [])

#guard p6meTransfer.amount { kind := .home, price := 200000 } == 7000
#guard p6meTransfer.amount { kind := .home, price := 2000000 } == 112000
#guard p6meTransfer.amount { kind := .vehicle, price := 100000 } == 0

end MeGlobal.Property
