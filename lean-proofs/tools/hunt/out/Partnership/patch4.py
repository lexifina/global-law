p='LegalProofs/USTax/Hunt/Partnership.lean'
s=open(p,encoding='utf-8',newline='').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a,s.count(a))
    s=s.replace(a,b)
# 751(b): measure the hot shares after the §707 step
rep("  let hotBefore := hotShares s0 none\n","")
rep("  -- 2. §704(c)(1)(B)\n","  let hotBefore := hotShares s none\n  -- 2. §704(c)(1)(B)\n")
# family
rep("  related : Nat → Nat → Bool\n","  related : Nat → Nat → Bool\n  fam : Nat → Bool := fun p => p < 2   -- the related group whose tax is being minimised\n")
a=s.index("def famTax (s : State)")
b=s.index("def pname")
s=s[:a]+'''def famTax (cfg : Cfg) (s : State) : Int :=
  (List.range s.persons.size).foldl (fun acc i => if cfg.fam i then acc + taxOf s.persons[i]! else acc) 0
def famCash (cfg : Cfg) (s : State) : Int :=
  (List.range s.persons.size).foldl (fun acc i => if cfg.fam i then acc + s.persons[i]!.cash else acc) 0

'''+s[b:]
a=s.index("def famHolds (s : State)")
b=s.index("def showPerson")
s=s[:a]+'''def isFamHolder (cfg : Cfg) (s : State) : Holder → Bool
  | .person p => cfg.fam p
  | .pship => (partners s).all cfg.fam
  | .sold => false

def famHolds (cfg : Cfg) (s : State) (id : Nat) : Bool := s.assets.any (fun a => a.id == id ∧ isFamHolder cfg s a.holder)

/-- Goal 1: X has left the family for cash — sold, or held by an unrelated person — the family (A and B, related)
has at least X's value in new cash in hand, owes nothing through the partnership, and still has Y. -/
def goalOut (cfg : Cfg) (s0 s : State) : Bool :=
  s.assets.any (fun a => a.id == 0 ∧ (a.holder == .sold ∨ match a.holder with | .person p => !cfg.fam p | _ => false)) ∧
  famCash cfg s ≥ famCash cfg s0 + cfg.unit ∧ famHolds cfg s 1 ∧
  (List.range s.persons.size).all (fun i => !cfg.fam i ∨ s.persons[i]!.liab == 0)

/-- Goal 2: the family has nine tenths of X's value in new cash in hand while it still holds both X and Y, directly
or through a partnership in which no unrelated person has capital. -/
def goalCash (cfg : Cfg) (s0 s : State) : Bool :=
  famCash cfg s ≥ famCash cfg s0 + cfg.unit * 9 / 10 ∧ famHolds cfg s 0 ∧ famHolds cfg s 1

/-- Goal 3: every asset has been sold for cash (the cash may still be inside a continuing partnership). -/
def goalSold (s : State) : Bool := s.assets.all (fun a => a.holder == .sold)

'''+s[b:]
a=s.index("def search (label : String)")
b=s.index("/-! ### Positions -/")
s=s[:a]+'''def search (label : String) (cfg : Cfg) (depth : Nat) (s0 : State) (allowed : Move → Bool) (top : Nat := 8) :
    IO Unit := do
  let mut frontier : Array (State × List Move) := #[(s0, [])]
  let mut seen : Std.HashSet State := {}
  seen := seen.insert s0
  let mut hits : Array (Std.HashMap Nat Hit) := #[{}, {}, {}]
  for d in [1:depth + 1] do
    let mut next : Array (State × List Move) := #[]
    for (s, path) in frontier do
      for m in moves cfg s do
        if allowed m then
          match step cfg s m with
          | none => pure ()
          | some s' =>
            if !seen.contains s' then
              seen := seen.insert s'
              let path' := path ++ [m]
              let gs := [goalOut cfg s0 s', goalCash cfg s0 s', goalSold s']
              if gs.any id then
                let oth := totalTax s' - famTax cfg s'
                let h : Hit := ⟨famTax cfg s' + max 0 oth, oth, totalTax (windup s'), s'.year, d, path', s'⟩
                let sig := sigOf path'
                for k in [0:3] do
                  if gs[k]! then
                    if (hits[k]!.get? sig).all (fun o => better h o) then hits := hits.modify k (·.insert sig h)
              if !gs[0]! ∨ !gs[2]! then next := next.push (s', path')
    frontier := next
    IO.println s!"[{label}] depth {d}: {frontier.size} new positions, {seen.size} in all"
  let w0 := windup s0
  let base := totalTax w0
  IO.println s!"[{label}] plain sale of everything: everyone ${base}, family ${famTax cfg w0}"
  let names := ["X sold out of the family for cash, Y kept", "cash in hand, X and Y kept", "every asset sold"]
  for k in [0:3] do
    let all := hits[k]!.toArray
    -- keep a family only if no family using a strict subset of its kinds of move does at least as well
    let minimal := all.filter (fun (sig, h) => !all.any (fun (sig2, o) =>
      sig2 != sig ∧ sig2 &&& sig == sig2 ∧ o.taxNow ≤ h.taxNow ∧ o.taxAll ≤ h.taxAll))
    let arr := (minimal.map (·.2)).qsort better
    IO.println s!"[{label}] == {names[k]!}: {all.size} families of plans, {arr.size} not dominated; best {top} by tax now =="
    for h in arr.toList.take top do describe h
    let arr2 := arr.qsort (fun a b => a.taxAll < b.taxAll ∨ (a.taxAll == b.taxAll ∧ better a b))
    match arr2.toList.head? with
    | some h => if h.taxAll < base then
                  IO.println s!"[{label}] -- lowest tax after everything is sold and wound up --"
                  for h in (arr2.toList.filter (fun h => h.taxAll < base)).take 3 do describe h
    | none => pure ()

'''+s[b:]
# scenarios
a=s.index("#eval search \"S1 X")
b=s.index("end Legal.USTax.Hunt.Partnership")
s=s[:a]+'''/-- An existing partnership, contributions made long ago (year 0; it is now year 8, so the 2- and 7-year clocks
have run). `mk` puts an asset in the partnership as contributed by `p`. -/
def held (id : Nat) (k : Kind) (fmv basis : Int) (p : Nat) : Asset :=
  ⟨id, k, fmv, basis, .pship, some p, some p, 0, fmv - basis, zeroAdj 4⟩
def partner0 (cash outside cap : Int) (nonInv : Bool := true) : Person :=
  ⟨cash, outside, cap, 0, 0, 0, 0, none, none, nonInv⟩

/-- S6. A, B and C are related; D is not. The partnership holds two parcels contributed by A (each 200, basis 20),
Y contributed by B (200, basis 200), Y' contributed by C (200, basis 200) and 200 of cash contributed by D. No basis
difference on any one parcel reaches $250,000; on the two together it does (360). -/
def start6 : State :=
  { year := 8, pcash := 200, elect := false, everNonInv := true, carry := 0,
    assets := #[held 0 .capital 200 20 0, held 1 .capital 200 200 1, held 2 .capital 200 20 0, held 3 .capital 200 200 2],
    persons := #[partner0 0 40 400, partner0 0 200 200, partner0 0 200 200, partner0 0 200 200] }
def cfg6 : Cfg := { unit := 200, debtFin := false, related := fun p q => p < 3 ∧ q < 3 ∧ p != q, fam := fun p => p < 3 }

/-- S6b. The same value in single pieces: A's parcel (400, basis 40), B's Y (400, basis 400), D's cash 200. -/
def start6b : State :=
  { start6 with assets := #[held 0 .capital 400 40 0, held 1 .capital 400 400 1],
                persons := #[partner0 0 40 400, partner0 0 400 400, partner0 0 0 0, partner0 0 200 200] }

/-- S7. An existing partnership of A (X: 1,000, basis 100), B, related to A (Y: 1,000, basis 1,600) and C,
unrelated (marketable securities Z: 1,000, basis 400). D is an outsider with cash. -/
def start7 : State :=
  { year := 8, pcash := 0, elect := false, everNonInv := true, carry := 0,
    assets := #[held 0 .capital 1000 100 0, held 1 .capital 1000 1600 1, held 2 .security 1000 400 2],
    persons := #[partner0 0 100 1000, partner0 0 1600 1000, partner0 0 400 1000 false, person0 2000] }

def simple : Move → Bool
  | .borrow .. => false | .repay .. => false | .buy .. => false | .contribCash .. => false | .sellInt .. => false
  | .contribute .. => false | _ => true

#eval search "S1 X 1000/100, Y 1000/1000" cfg1 6 start1 (fun _ => true) 5
#eval search "S1s X 300/60, Y 300/300" cfg1s 5 start1s (fun _ => true) 3
#eval search "S2 Y built-in loss 1000/1600" cfg1 6 start2 (fun _ => true) 10
#eval search "S3 C holds securities Z 1000/400" cfg1 5 start3 (fun _ => true) 4
#eval search "S4 Y inventory 1000/400" cfg1 6 start4 noD 5
#eval search "S5 as S1, debt-financed exception on" { cfg1 with debtFin := true } 5 start1 noD 3
#eval search "S6 existing partnership, parcels under $250k" cfg6 7 start6 simple 6
#eval search "S6b same, single pieces over $250k" cfg6 5 start6b simple 6
#eval search "S7 existing partnership with loss asset and securities" cfg1 5 start7 (fun _ => true) 8

'''+s[b:]
open(p,'w',encoding='utf-8',newline='').write(s)
