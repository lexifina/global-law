import LegalProofs.USTax.Loopholes.Playbook
import LegalProofs.USTax.Loopholes.SALT
import LegalProofs.USTax.Loopholes.ACA

/-!
# Mapping the loopholes

Runs the loophole models over ranges of inputs and writes what it finds to `tools/out/loopholes.json`, for the write-up
and the film. Not part of the build:

    lake env lean LegalProofs/USTax/Loopholes/Search.lean
-/

namespace Legal.USTax.Loopholes.Search
open Legal.USTax Legal.USTax.Loopholes

def jl (xs : List String) : String := "[" ++ ",".intercalate xs ++ "]"
def pair (a b : Nat) : String := s!"[{a},{b}]"

def run : IO Unit := do
  -- 1. GRAT payoff surface: year growth factors from −30% to +60% in 5% steps; heirs' share and gift
  let fs := (List.range 19).map (fun i => 7000 + 500 * i)
  let surf := fs.map (fun f₁ => jl (fs.map (fun f₂ => toString (GRAT.run 100000000 560 f₁ f₂).toHeirs)))
  -- 2. buy-borrow-die over the years: value, debt, heirs if they died that year, sell vs borrow
  let mut life : List String := []
  for y in [0:41] do
    let s := live (sellYear 20000000 700) y founderStart
    let b := live (borrowYear 20000000 700 500) y founderStart
    life := s!"\{\"year\":{y},\"sellValue\":{s.value},\"sellTax\":{s.incomeTax},\"sellHeirs\":{(die s).toHeirs},\"borrowValue\":{b.value},\"debt\":{b.debt},\"borrowHeirs\":{(die b).toHeirs}}" :: life
  -- 3. QSBS: tax on an exit by number of separate taxpayers
  let mut qs : List String := []
  for exit in [50000000, 100000000, 150000000, 300000000, 500000000] do
    let row := (List.range 21).map (fun n => let k := n + 1; QSBS.taxOn (exit / k) 0 * k)
    qs := s!"\{\"exit\":{exit},\"tax\":{jl (row.map toString)}}" :: qs
  -- 4. SALT: effective marginal rate per $1,000 of wages, $300k to $800k
  let salt := (List.range 101).map (fun i => let w := 300000 + 5000 * i
    pair w ((SALT.earner (w + 1000) - SALT.earner w) * 10))
  -- 5. ACA: credit by income, and the return on the IRA dollar that restores it
  let aca := (List.range 81).map (fun i => let m := 70000 + 500 * i; pair m (ACA.credit m))
  let ret := (List.range 35).map (fun i => let w := 84601 + 500 * i; let c := w - 84600
    s!"\{\"wages\":{w},\"ira\":{c},\"credit\":{ACA.credit (ACA.magi w c)}}")
  IO.FS.writeFile "tools/out/loopholes.json" <|
    "{" ++ s!"\"grat\":\{\"factors\":{jl (fs.map toString)},\"heirs\":{jl surf},\"gift\":{GRAT.gift 100000000 560}}," ++
    s!"\"life\":{jl life.reverse},\"qsbs\":{jl qs.reverse},\"salt\":{jl salt},\"aca\":{jl aca},\"acaIra\":{jl ret}," ++
    s!"\"thiel\":\{\"cost\":1700,\"value\":5000000000,\"taxable\":{cashOutTax .taxable 1700 5000000000}}," ++
    s!"\"billion\":\{\"salary\":{Playbook.wageTax 1000000000},\"founder\":{Playbook.founderIncomeTax}}" ++ "}"
  IO.println "wrote tools/out/loopholes.json"

#eval run

end Legal.USTax.Loopholes.Search
