import FrTax.Penalties
import FrTax.Liquidation

/-!
Penalty study runner: `lake env lean --run harness/pen_eval.lean < cases > out`. One case per line, `;`-separated:
* `I;id;base;sy;sm;ey;em;relief` (relief none|l62|spontaneous): interest from the first of (sy,sm) to the end of (ey,em)
* `IR;id;base;n;ey;em;relief`: income-tax interest for income n, start 1 July n+1
* `S;id;t0;r1:t1,r2:t2,...`: art. 1729 A strata (tax after each layer, in the order given)
* `L;id;tax;globalRate;total;r:inc,...`: art. 1728, 4 split
* `W;id;lateRate;tLate;tAdd;rate1729`: art. 1729 A, 2
* `M;id;rate;rights`: one majoration
* `T;id;insufficiency;baseAfter;deliberate(0/1)`: art. 1727, II, 4 tolerance (1 = no interest)
* `G;id;due;paid`: art. 1729 G modulation (rate in 1/100 %, majoration)
* `P;id;unpaid;ry;rm;rd;current(0/1);py;pm;pd`: art. 1730
* `X;id;year;BOX=V,...;rate:BOX=V,...|rate:BOX=V,...;ey;em;relief`: whole case with the tax model: declared return,
  reassessment layers (each adds its boxes), proposition month; prints the net tax after each layer, the
  majorations by art. 1729 A, the interest on the total increase.
-/

open FrTax FrTax.Penalties

def toI (s : String) : Option Int := s.trimAscii.toString.toInt?

def relief : String → Relief
  | "l62" => .l62 | "spontaneous" => .spontaneous | _ => .none

def pairs (s : String) : List (Int × Int) :=
  (s.splitOn ",").filterMap fun kv => match kv.splitOn ":" with
    | [a, b] => do some ((← toI a), (← toI b))
    | _ => none

def boxes (year : Nat) (s : String) : Decl :=
  let ps := (s.splitOn ",").filterMap fun kv => match kv.splitOn "=" with
    | [k, v] => (toI v).map fun n => (k.trimAscii.toString, n)
    | _ => none
  { year, boxes := ps.foldl (fun m (k, v) => m.insert k v) {} }

def addBoxes (d : Decl) (s : String) : Decl :=
  (s.splitOn ",").foldl (fun d kv => match kv.splitOn "=" with
    | [k, v] => match toI v with
      | some n => let k := k.trimAscii.toString; { d with boxes := d.boxes.insert k (d.get k + n) }
      | none => d
    | _ => d) d

def run (line : String) : Option String := do
  match line.splitOn ";" with
  | ["I", id, b, sy, sm, ey, em, r] =>
    some s!"{id};INT={interest (← toI b) ⟨← toI sy, ← toI sm, 1⟩ ⟨← toI ey, ← toI em, 1⟩ (relief r)};MONTHS={months ⟨← toI sy, ← toI sm, 1⟩ ⟨← toI ey, ← toI em, 1⟩};RATESUM={rateSum ⟨← toI sy, ← toI sm, 1⟩ ⟨← toI ey, ← toI em, 1⟩}"
  | ["IR", id, b, n, ey, em, r] =>
    let st := irStart (← toI n)
    let en : Date := ⟨← toI ey, ← toI em, 1⟩
    some s!"{id};INT={interest (← toI b) st en (relief r)};MONTHS={months st en};RATESUM={rateSum st en}"
  | ["S", id, t0, ls] =>
    let t0 ← toI t0
    let st := strata t0 (pairs ls)
    some s!"{id};LAYERS={",".intercalate (st.map fun x => s!"{x.1}:{x.2}")};TOTAL={strataTotal t0 (pairs ls)}"
  | ["L", id, tax, g, tot, ls] =>
    some s!"{id};TOTAL={lateSplit (← toI tax) (← toI g) (← toI tot) (pairs ls)}"
  | ["W", id, lr, tl, ta, r9] =>
    some s!"{id};TOTAL={lateWithReassessment (← toI lr) (← toI tl) (← toI ta) (← toI r9)}"
  | ["M", id, r, b] => some s!"{id};MAJO={majo (← toI r) (← toI b)}"
  | ["T", id, i, b, dl] => some s!"{id};TOL={if tolerance (← toI i) (← toI b) ((← toI dl) = 1) then 1 else 0}"
  | ["G", id, due, paid] => some s!"{id};RATE={modulationRate (← toI due) (← toI paid)};MAJO={modulationMajo (← toI due) (← toI paid)}"
  | ["P", id, u, ry, rm, rd, c, py, pm, pd] =>
    some s!"{id};MAJO={latePayment (← toI u) ⟨← toI ry, ← toI rm, ← toI rd⟩ ((← toI c) = 1) ⟨← toI py, ← toI pm, ← toI pd⟩}"
  | ["X", id, y, decl, layers, ey, em, r] =>
    let year ← y.toNat?
    let p ← paramsFor year
    let d0 := boxes year decl
    let t0 := (compute p d0).net
    -- layers in decreasing order of rate (art. 1729 A, 1); stable for equal rates
    let keep := layers.startsWith "="
    let en : Date := ⟨← toI ey, ← toI em, 1⟩
    -- a layer is `RATE[n|l][@YYYYMM]:BOX=V,...`: `n` = no interest on it (mention expresse, art. 1727, II, 1), `l` = rights
    -- from a late return (never under the tolerance of art. 1727, II, 4, which concerns insufficiencies),
    -- `@YYYYMM` = its own stop month (art. 1727, IV, 3 and 4)
    let parseLayer (l : String) : Option (Int × Nat × Date × String) := match l.splitOn ":" with
      | [head, bx] =>
        let (rs, st) := match head.splitOn "@" with
          | [a, b] => (a, some b)
          | _ => (head, none)
        let fl : Nat := if rs.endsWith "n" then 1 else if rs.endsWith "l" then 2 else 0
        let rs := if fl > 0 then (rs.dropEnd 1).toString else rs
        let stop : Date := match st.bind toI with
          | some v => ⟨v / 100, v % 100, 1⟩
          | none => en
        (toI rs).map fun rt => (rt, fl, stop, bx)
      | _ => none
    let ls := ((if keep then (layers.drop 1).toString else layers).splitOn "|").filterMap parseLayer
    let sorted := if keep then ls else ls.foldr (fun x acc =>
      let rec ins (x : Int × Nat × Date × String) : List (Int × Nat × Date × String) → List (Int × Nat × Date × String)
        | [] => [x]
        | y :: ys => if x.1 ≥ y.1 then x :: y :: ys else y :: ins x ys
      ins x acc) []
    let r0 := compute p d0
    let (_, taxes, rnis) := sorted.foldl (fun (d, acc, rn) (rt, _, _, bx) =>
      let d' := addBoxes d bx; let c := compute p d'; (d', acc ++ [(rt, c.net)], rn ++ [c.rni])) (d0, [], [])
    let st := strata t0 taxes
    let tEnd := lastTax t0 taxes
    let inc := tEnd - t0
    let rniEnd := rnis.getLast?.getD r0.rni
    -- art. 1727, II, 4: the insufficiency of the bases, without the layers under a mention expresse
    let incs := (st.zip sorted).map fun ((i, _), (rt, ni, stop, _)) => (i, rt, ni, stop)
    let rniIncs := (List.zip (r0.rni :: rnis) rnis).map fun (a, b) => b - a
    let insuff := ((rniIncs.zip incs).filter (fun (_, (_, _, ni, _)) => ni == 0)).foldl (fun a (x, _) => a + x) 0
    let deliberate := incs.any fun (_, rt, _, _) => rt ≥ 40
    let tol := tolerance insuff rniEnd deliberate
    -- interest: the increments bearing interest, grouped by their stop month, each group rounded once
    let bearing := incs.filter fun (_, _, ni, _) => ni == 2 || (ni == 0 && !tol)
    let stops := bearing.foldl (fun acc (_, _, _, s) => if acc.contains s.mi then acc else acc ++ [s.mi]) []
    let intTotal := stops.foldl (fun a s =>
      let base := bearing.foldl (fun b (i, _, _, st) => if st.mi = s then b + i else b) 0
      a + interest base (irStart year) ⟨s / 12, s % 12 + 1, 1⟩ (relief r)) 0
    some s!"{id};T0={t0};TEND={tEnd};INC={inc};LAYERS={",".intercalate (st.map fun x => s!"{x.1}:{x.2}")};MAJO={strataTotal t0 taxes};MONTHS={months (irStart year) en};INT={intTotal};TOL={if tol then 1 else 0};INSUFF={insuff};RNI={rniEnd}"
  | _ => none

partial def loop (h o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let l := line.trimAscii.toString
  if l.isEmpty || l.startsWith "#" then loop h o else
  o.putStrLn ((run l).getD s!"ERR;{l}")
  loop h o

def main : IO Unit := do loop (← IO.getStdin) (← IO.getStdout)
