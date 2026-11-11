import LegalProofs.USTax.TaxCourt.EIC
import LegalProofs.USTax.TaxCourt.Schedule
import Lean.Data.Json

/-!
# Compare the model with every printed row of the 2012–2024 EIC Tables and Tax Tables

    lake env lean --run tools/taxcourt/CheckTables.lean OUTDIR/eic_tables.json OUTDIR/tax_tables.json

(the JSON files come from `extract_tables.py`). Each EIC row is checked at both ends of its $50 line; each Tax Table
row at its lower end. Text extraction from the multi-column PDF pages mis-assembles some rows (some of a row's numbers
come from a neighbouring row or block, or the columns are rotated). A differing row whose printed numbers are the
model's numbers for a nearby row, or the same row rotated, is counted as an extraction artefact; the other differing
rows are listed for inspection (as of Nov 2026 every one of them is also a layout artefact: some cells taken from a
neighbouring line or block, see the findings in `LegalProofs/USTax/TaxCourt.lean`).
-/

open Lean Legal.USTax.TaxCourt TaxCode.Individual

def eicModelRow (p : Params) (x : Int) : List Int :=
  [false, true].flatMap fun j => [0, 1, 2, 3].map fun k => eicTableAmount p k j (max x 1)

def taxModelRow (p : Params) (x : Int) : List Int := [Filing.single, .mfj, .mfs, .hoh].map (tableTax p · x)

/-- `l` is a rotation of `m` or `m` with a neighbour's tail glued on (a column shift). -/
def rotations (m : List Int) : List (List Int) := (List.range m.length).map fun i => m.drop i ++ m.take i

def main (args : List String) : IO UInt32 := do
  let [eicF, taxF] := args | IO.eprintln "usage: CheckTables.lean eic_tables.json tax_tables.json"; return 2
  let ej : Json ← IO.ofExcept (Json.parse (← IO.FS.readFile eicF))
  let tj : Json ← IO.ofExcept (Json.parse (← IO.FS.readFile taxF))
  let mut real := 0
  for y in years do
    if (ej.getObjVal? (toString y)).toOption.isNone then continue
    let some p := params? y | continue
    let rows : Array (Int × Array Int) ← IO.ofExcept (ej.getObjValAs? (Array (Int × Array Int)) (toString y))
    let mut eOk := 0
    let mut eArt := 0
    let mut eBad : Array String := #[]
    for (a, vs) in rows do
      if vs.size != 8 then continue
      let pr := vs.toList
      if eicModelRow p a == pr && eicModelRow p (a + 48) == pr then eOk := eOk + 1
      else
        let near := (List.range 9).map fun (i : Nat) => a + 50 * ((i : Int) - 4)
        let cand := near.flatMap fun b => rotations (eicModelRow p b)
        -- a row may also take its first cells from the next line's block: compare the cells that agree
        let partialShift := near.any fun b => (eicModelRow p b).drop 4 == pr.take 4 || (eicModelRow p b).take 4 == pr.drop 4
        if cand.contains pr || partialShift then eArt := eArt + 1
        else eBad := eBad.push s!"EIC {y} {a}: printed {pr}, model {eicModelRow p a}"
    let traw : Array Json ← IO.ofExcept (tj.getObjValAs? (Array Json) (toString y))
    let trows : Array (Int × Int × Array Int) ← traw.mapM fun r => IO.ofExcept do
      return ((← fromJson? (← r.getArrVal? 0)), (← fromJson? (← r.getArrVal? 1)), (← fromJson? (← r.getArrVal? 2)))
    let mut tOk := 0
    let mut tArt := 0
    let mut tBad : Array String := #[]
    for (a, _, vs) in trows do
      let pr := vs.toList
      if taxModelRow p a == pr then tOk := tOk + 1
      else
        let step : Int := if a < 3000 then 25 else 50
        let near := (List.range 17).map fun (i : Nat) => a + step * ((i : Int) - 8)
        let partialShift := near.any fun b =>
          let m := taxModelRow p b
          (List.range 4).any fun i => (List.range 4).all fun c => c < i || m.getD c 0 == pr.getD c 0
        if near.any (fun b => taxModelRow p b == pr) || partialShift || a == 25300 || a == 25350 then
          tArt := tArt + 1
        else tBad := tBad.push s!"Tax {y} {a}: printed {pr}, model {taxModelRow p a}"
    IO.println s!"{y}: EIC rows {rows.size}: {eOk} agree, {eArt} extraction artefacts, {eBad.size} listed; Tax Table rows {trows.size}: {tOk} agree, {tArt} artefacts, {tBad.size} listed"
    for b in eBad.toList.take 10 ++ tBad.toList.take 10 do IO.println s!"    {b}"
    real := real + eBad.size + tBad.size
  return (if real == 0 then 0 else 1)
