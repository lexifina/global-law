import SiGlobal.Pit

/-!
# SI 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Zakon o davku na promet nepremičnin (2 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (nadomestilo za uporabo stavbnega zemljišča (Ljubljana)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Davek na promet nepremičnin (pass 6)
Source: PwC Worldwide Tax Summaries, Slovenia, Corporate - Other taxes, accessed 2025-06-23 (Wayback capture; `law/pwc_corpother_wb2025.txt`).
* real estate transfer tax 2 %: transfers and finance leases of real estate; not where VAT is charged
-/

namespace SiGlobal.Property
open TaxKernel TaxKernel.Global

/-- Zakon o davku na promet nepremičnin (ZDPN-2) (2 %; not where VAT is charged) -/
def p6prom : TransferDuty := { name := "Davek na promet nepremičnin", sched := Schedule.flat 200, kinds := [.home, .realEstate, .land] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Davek na promet nepremičnin", covers := [.transactions],
     run := fun args g prev =>
       p6prom.charges g.purchases "Zakon o davku na promet nepremičnin (ZDPN-2) (2 %; not where VAT is charged)" }]

def absent : List Absent :=
  []

def notes : List String := ["SI 4400 Davek na promet nepremičnin: PwC WWTS Corporate - Other taxes, 2025-06-23 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 new buildings sold under VAT (first supply) are outside the tax (not separated)"] else [])

#guard p6prom.amount { kind := .home, price := 200000 } == 4000
#guard p6prom.amount { kind := .home, price := 2000000 } == 40000
#guard p6prom.amount { kind := .vehicle, price := 100000 } == 0

end SiGlobal.Property
