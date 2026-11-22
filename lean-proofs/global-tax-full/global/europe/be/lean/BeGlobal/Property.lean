import BeGlobal.Pit

/-!
# BE 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Code des droits d'enregistrement (Région de Bruxelles-Capitale, 12,5 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (précompte immobilier (Bruxelles)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Droits d'enregistrement (Région de Bruxelles-Capitale) (pass 6)
Source: PwC Worldwide Tax Summaries, Belgium, Corporate - Other taxes, accessed 2025-05-26 (Wayback capture; `law/pwc_corpother_wb2025.txt`).
* droits d'enregistrement: Brussels / Wallonia 12,5 %, Flanders 12 %; base max(price, market value); real estate outside VAT; family home Flanders 2 %, Wallonia 3 % (from 1.1.2025)
-/

namespace BeGlobal.Property
open TaxKernel TaxKernel.Global

/-- Code des droits d'enregistrement (Bruxelles) art. 44 (12,5 %) -/
def p6enr : TransferDuty := { name := "Droits d'enregistrement (Région de Bruxelles-Capitale)", sched := Schedule.flat 1250, kinds := [.home, .realEstate, .land] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Droits d'enregistrement (Région de Bruxelles-Capitale)", covers := [.transactions],
     run := fun args g prev =>
       p6enr.charges g.purchases "Code des droits d'enregistrement (Bruxelles) art. 44 (12,5 %)" }]

def absent : List Absent :=
  []

def notes : List String := ["BE 4400 Droits d'enregistrement (Région de Bruxelles-Capitale): PwC WWTS Corporate - Other taxes, 2025-05-26 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 Brussels taken as the reference region; the abattement for a sole home and Flemish/Walloon rates not modelled; base = higher of price and market value (the price stands in)"] else [])
  ++ (if g.purchases.any (fun p => p.kind == .listedShares || p.kind == .unlistedShares) then ["4400 Taxe sur les opérations de bourse (Code des droits et taxes divers art. 120 ff.) on a purchase of securities: not modelled (grade C: text not read)"] else [])

#guard p6enr.amount { kind := .home, price := 200000 } == 25000
#guard p6enr.amount { kind := .home, price := 2000000 } == 250000
#guard p6enr.amount { kind := .vehicle, price := 100000 } == 0

end BeGlobal.Property
