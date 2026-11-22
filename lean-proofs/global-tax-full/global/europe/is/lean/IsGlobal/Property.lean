import IsGlobal.Pit

/-!
# IS 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Lög nr. 138/2013 um stimpilgjald (0,8 % / 1,6 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Lög nr. 4/1995 um tekjustofna sveitarfélaga (fasteignaskattur)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Stimpilgjald (real estate) (pass 6)
Source: PwC Worldwide Tax Summaries, Iceland, Individual - Other taxes, accessed 2026-11-21 (live page; `law/pwc_indother_live.txt`).
* stimpilgjald on real estate deeds: individuals 0,8 % of registered value; first home 0,4 %

* **4100 Recurrent property tax (pass 6 note, grade C)**: Lög nr. 4/1995 um tekjustofna sveitarfélaga (fasteignaskattur): fasteignaskattur set by each municipality; reference municipality's rate not read (pass 6 note (PwC WWTS 2025 captures on disk))
-/

namespace IsGlobal.Property
open TaxKernel TaxKernel.Global

/-- lög nr. 138/2013 um stimpilgjald (0,8 % for individuals; 0,4 % for a first home) -/
def p6stimp : TransferDuty := { name := "Stimpilgjald (real estate)", sched := Schedule.flat 80, kinds := [.home, .realEstate, .land], firstHomeCap := 1000000000000, firstHomeSched := Schedule.flat 40 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Stimpilgjald (real estate)", covers := [.transactions],
     run := fun args g prev =>
       p6stimp.charges g.purchases "lög nr. 138/2013 um stimpilgjald (0,8 % for individuals; 0,4 % for a first home)" }]

def absent : List Absent :=
  []

def notes : List String := ["IS 4400 Stimpilgjald (real estate): PwC WWTS Individual - Other taxes, 2026-11-21 (live page) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 the base is the registered value (fasteignamat): the price stands in; legal persons pay 1,6 % (not separated)"] else [])

#guard p6stimp.amount { kind := .home, price := 200000 } == 1600
#guard p6stimp.amount { kind := .home, price := 2000000 } == 16000
#guard p6stimp.amount { kind := .home, price := 1000000000000, firstHome := true } == 4000000000
#guard p6stimp.amount { kind := .home, price := 1000000000001, firstHome := true } == 8000000000
#guard p6stimp.amount { kind := .vehicle, price := 100000 } == 0

end IsGlobal.Property
