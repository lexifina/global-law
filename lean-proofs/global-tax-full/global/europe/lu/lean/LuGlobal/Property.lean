import LuGlobal.Pit

/-!
# LU 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Loi du 7 août 1920 (droits d'enregistrement 6 % + transcription 1 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (impôt foncier (Luxembourg-ville)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Droits d'enregistrement et de transcription (immeubles) (pass 6)
Source: PwC Worldwide Tax Summaries, Luxembourg, Corporate - Other taxes, accessed 2025-08-03 (Wayback capture; `law/pwc_corpother_wb2025.txt`).
* sales of Luxembourg real estate: proportional registration duty including the transcription tax, 7 % in all; Luxembourg City adds a 3 % surtax
-/

namespace LuGlobal.Property
open TaxKernel TaxKernel.Global

/-- droits d'enregistrement et de transcription on sales of Luxembourg real estate: 7 % in all (acts not read) -/
def p6enr : TransferDuty := { name := "Droits d'enregistrement et de transcription (immeubles)", sched := Schedule.flat 700, kinds := [.home, .realEstate, .land] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Droits d'enregistrement et de transcription (immeubles)", covers := [.transactions],
     run := fun args g prev =>
       p6enr.charges g.purchases "droits d'enregistrement et de transcription on sales of Luxembourg real estate: 7 % in all (acts not read)" }]

def absent : List Absent :=
  []

def notes : List String := ["LU 4400 Droits d'enregistrement et de transcription (immeubles): 2025-08-03 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 Luxembourg City surtax (3 %) not applied; the Bëllegen Akt credit on a buyer's own home and the base (higher of price and value) not read"] else [])

#guard p6enr.amount { kind := .home, price := 200000 } == 14000
#guard p6enr.amount { kind := .home, price := 2000000 } == 140000
#guard p6enr.amount { kind := .vehicle, price := 100000 } == 0

end LuGlobal.Property
