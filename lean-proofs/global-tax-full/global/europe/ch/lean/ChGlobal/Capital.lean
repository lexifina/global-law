import ChGlobal.Pit

/-!
# Switzerland 2025: private capital gains (1100) are exempt from the federal income tax

Source: DBG SR 642.11, fedlex consolidation 2025-01-01 (`ch/law/dbg_20250101.html`).
* **DBG Art. 16 (3)**: "Die Kapitalgewinne aus der Veräusserung von Privatvermögen sind steuerfrei."
Gains on private real estate are taxed by the cantons (Grundstückgewinnsteuer, StHG Art. 12): not modelled.
-/

namespace ChGlobal.Capital
open TaxKernel TaxKernel.Global

def charges (g : CanonGlobal) : List Charge :=
  if g.entity == .company || g.disposals.isEmpty then [] else
  let movable := g.disposals.filter fun d => !d.kind.isRealEstate
  if movable.isEmpty then [] else
  [charge .pit "Direkte Bundessteuer auf private Kapitalgewinne" (isum (movable.map (·.gain))) (fun _ => 0) (fun _ => 0)
     (event := "disposals (private wealth)") (statute := "DBG Art. 16 (3): steuerfrei")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 private Kapitalgewinne (steuerfrei)", covers := [],
     run := fun args g prev =>
       charges g }]

def absent : List Absent :=
  []

def notes : List String := ["CH 1100: private gains exempt federally (DBG Art. 16 (3))"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (fun d => d.kind.isRealEstate) then ["Grundstückgewinnsteuer (cantonal, StHG Art. 12; Zürich StG §§ 216 ff.) not modelled"] else [])
  ++ (if !g.disposals.isEmpty then ["professional securities trading (gains as self-employment income) not considered"] else [])

#guard (charges { id := "x", household := { id := "x" }, disposals := [{ kind := .listedShares, proceeds := 5000, cost := 1000 }] }).map (·.due) == [0]

end ChGlobal.Capital
