"""Red-team generator: copies Household.lean (never edits it), applies named text patches, appends a harness."""
import sys, pathlib
here = pathlib.Path(__file__).resolve().parent
src = (here.parent.parent / "Household.lean").read_text(encoding="utf-8")
cut = src.index("#eval show IO Unit from do")
base = src[:cut]

def rep(s, old, new, count=1):
    assert s.count(old) == count, (old, s.count(old))
    return s.replace(old, new)

def build(name, refcap, adopt_moves=".adopt 0, .adopt 50, .adopt 100", extra=None, harness=""):
    s = base
    s = rep(s, "namespace Legal.USTax.Hunt.Household", f"namespace Legal.USTax.Hunt.Audit.Household.{name}")
    # instrumentation: per-return cap on the refundable part, and the pieces of the result exposed
    s = rep(s, "  adopt : Nat         -- §23: expenses taken into account (after the §23(b)(1) limit)\n",
            "  adopt : Nat         -- §23: expenses taken into account (after the §23(b)(1) limit)\n  adCap : Nat         -- RED: §23(a)(4) dollar amount available to this return\n")
    s = rep(s, "  net : Int\n  deriving Repr, Inhabited",
            "  net : Int\n  adRef : Nat\n  adNon : Nat\n  adCarry : Nat\n  room : Nat\n  refund : Nat\n  deriving Repr, Inhabited")
    s = rep(s, "let adRef := min 5000 ad", "let adRef := min r.adCap ad")
    s = rep(s, "    net := (tax : Int) - credits }",
            "    net := (tax : Int) - credits,\n    adRef := adRef, adNon := adNon, adCarry := ad - adRef - adNon, room := rem - adNon,\n    refund := e + actc + aRef + adRef + p }")
    s = rep(s, "def soloRet (f : Facts)", refcap + "\n\ndef soloRet (f : Facts)")
    s = rep(s, "    adopt := adoptShare f p w }", "    adopt := adoptShare f p w, adCap := refCap p w }")
    s = rep(s, "    adopt := min f.adoption 17280 }", "    adopt := min f.adoption 17280, adCap := refCapJoint }")
    s = rep(s, ".adopt 0, .adopt 50, .adopt 100]", adopt_moves + "]")
    for old, new in (extra or []):
        s = rep(s, old, new)
    s += HARNESS + harness + f"\nend Legal.USTax.Hunt.Audit.Household.{name}\n"
    (here / f"{name}.lean").write_text(s, encoding="utf-8", newline="\n")

REF_ORIG = """/-- RED: the original rule, $5,000 on every return (§23(a)(4) as encoded). -/
def refCap (_p : Plan) (_w : Who) : Nat := 5000
def refCapJoint : Nat := 5000"""
REF_CLOSED = """/-- RED closed gap: §23(i) extended to (a)(4); the $5,000 is divided like the (b)(1) limit. -/
def refCap (p : Plan) (w : Who) : Nat := 5000 * (if w == .a then p.adoptA else 100 - p.adoptA) / 100
def refCapJoint : Nat := 5000"""
REF_NONE = """/-- RED earlier law: no §23(a)(4) (before Pub. L. 119-21). -/
def refCap (_p : Plan) (_w : Who) : Nat := 0
def refCapJoint : Nat := 0"""

HARNESS = r'''
/-! ## RED harness -/

def isAdopt : Move → Bool
  | .adopt _ => true
  | _ => false

def reach (f : Facts) (ok : Move → Bool) (maxStates : Nat := 60000) : Array Plan := Id.run do
  let d := default f
  let mut seen : Std.HashSet Plan := (Std.HashSet.emptyWithCapacity 1024).insert d
  let mut frontier : Array Plan := #[d]
  let mut all : Array Plan := #[d]
  while !frontier.isEmpty && seen.size < maxStates do
    let mut next : Array Plan := #[]
    for p in frontier do
      for m in (moves f p).filter ok do
        match step f p m with
        | none => pure ()
        | some q =>
          if !seen.contains q then
            seen := seen.insert q
            next := next.push q
            all := all.push q
    frontier := next
  return all

def argmin (ps : Array Plan) (obj : Plan → Int) (d : Plan) : Int × Plan :=
  ps.foldl (fun (b : Int × Plan) p => let t := obj p; if t < b.1 then (t, p) else b) (obj d, d)

def outsOf (f : Facts) (p : Plan) : List Out := (returns f p).map (fun r => compute r.2)

/-- Six years (the year of the adoption and the five carryforward years of §23(c)(2)), same facts and same choices
every year, no new adoption expense: net tax in total, with the carried credit used against the tax left after the
other nonrefundable credits (§23(c)(1)). Also the amount used in each later year. -/
def carryUse (f : Facts) (p : Plan) : List Nat :=
  let y0 := outsOf f p
  let later := outsOf { f with adoption := 0 } p
  let per := (y0.zip later).map (fun (o0, o1) =>
    (List.range 5).foldl (fun (acc : Nat × List Nat) _ =>
      let u := min acc.1 o1.room
      (acc.1 - u, acc.2 ++ [u])) (o0.adCarry, []))
  (List.range 5).map (fun i => sumBy (fun (pr : Nat × List Nat) => pr.2.getD i 0) per)

def lifetime (f : Facts) (p : Plan) : Int :=
  total f p + 5 * total { f with adoption := 0 } p - (sumBy id (carryUse f p) : Nat)

def adoptTotal (f : Facts) (p : Plan) : Nat := sumBy (fun o => o.adRef + o.adNon) (outsOf f p)
def adoptRefund (f : Facts) (p : Plan) : Nat := sumBy (·.adRef) (outsOf f p)
def expired (f : Facts) (p : Plan) : Nat := sumBy (·.adCarry) (outsOf f p) - sumBy id (carryUse f p)

def line (f : Facts) (d p : Plan) : String :=
  s!"[{family d p}] {semi (describe f d p)} | year1 {total f p} | §23 refundable {adoptRefund f p} nonref {adoptTotal f p - adoptRefund f p} | carry used {carryUse f p} expired {expired f p} | six-year {lifetime f p}"
'''
VARIANTS = {}
def variant(fn):
    VARIANTS[fn.__name__] = fn
    return fn

H_BASE = r'''
def report (name : String) (f : Facts) (ok : Move → Bool) : IO Unit := do
  let d := default f
  let ps := reach f ok
  let (t, q) := argmin ps (total f) d
  IO.println s!"-- {name}: {ps.size} plans; default {total f d}; best year1 {t} gain {total f d - t} {line f d q}"
  -- best plan that uses only the adopt choice, and best that does not use it
  let onlyAd := ps.filter (fun p => family d p == "adopt")
  let (ta, qa) := argmin onlyAd (total f) d
  IO.println s!"   adopt only: gain {total f d - ta} {line f d qa}"
  let noAd := ps.filter (fun p => p.adoptA == d.adoptA)
  let (tn, qn) := argmin noAd (total f) d
  IO.println s!"   best without adopt choice: gain {total f d - tn} {line f d qn}"

#eval show IO Unit from do
  let f := h6 false
  let d := default f
  IO.println "T0 reproduction (unmodified rules, all moves)"
  report "H6 unmarried" f (fun _ => true)
  report "H6 married" (h6 true) (fun _ => true)
  IO.println "T3 ablation"
  report "no adopt move" f (fun m => !isAdopt m)
  report "adopt moves only" f isAdopt
  report "no claim" f (fun m => match m with | .claim .. => false | _ => true)
  report "no keep" f (fun m => match m with | .keep _ => false | _ => true)
  report "no pretax/roth/fsa" f (fun m => match m with | .pretax .. => false | .roth .. => false | .fsa .. => false | _ => true)
  report "no fileJoint/fileSeparate/claimElder" f (fun m => match m with | .fileJoint => false | .fileSeparate => false | .claimElder _ => false | _ => true)
  IO.println "single payer comparison (year 1 and six-year)"
  for x in [100, 50, 0] do
    let p := { d with adoptA := x }
    IO.println s!"   A pays {x}%: lawful {lawful f p} {line f d p}"
    showPlan f p
'''
@variant
def RedBase():
    build("RedBase", REF_ORIG, harness=H_BASE)


H_LIFE = r'''
/-- Present value at 4% a year of the six-year net tax (units of 1/10000 dollar, rounded down to dollars). -/
def pv (f : Facts) (p : Plan) : Int :=
  let later := total { f with adoption := 0 } p
  let fs : List Int := [9615, 9246, 8890, 8548, 8219]
  let us := carryUse f p
  let rest := (fs.zip us).foldl (fun (s : Int) (d, u) => s + d * (later - (u : Nat))) 0
  total f p + rest / 10000

def three (name : String) (f : Facts) (obj : Plan → Int) (ps : Array Plan) : IO Unit := do
  let d := default f
  let (t1, q1) := argmin ps obj d
  let (t2, q2) := argmin (ps.filter (fun p => p.adoptA == 0 || p.adoptA == 100)) obj d
  let (t3, q3) := argmin (ps.filter (fun p => p.adoptA == 100)) obj d
  IO.println s!"  objective {name}: default {obj d}"
  IO.println s!"    any split      {t1}: {line f d q1}"
  IO.println s!"    one payer      {t2}: {line f d q2}"
  IO.println s!"    A pays (deflt) {t3}: {line f d q3}"
  IO.println s!"    gain of splitting over the best one-payer plan: {t2 - t1}; over the best plan with A paying: {t3 - t1}; over the default: {obj d - t1}"

def study (name : String) (f : Facts) (ok : Move → Bool) : IO Unit := do
  let ps := reach f ok
  IO.println s!"== {name}: {ps.size} plans"
  three "year 1 (carryforward lost, as the original)" f (total f) ps
  three "six years nominal (carryforward used, §23(c))" f (lifetime f) ps
  three "six years, present value at 4%" f (pv f) ps

#eval show IO Unit from do
  study "H6 unmarried, all moves" (h6 false) (fun _ => true)
  study "H6 unmarried, no retirement moves" (h6 false) (fun m => match m with | .pretax .. => false | .roth .. => false | _ => true)
  study "H6 unmarried, adopt moves only (A keeps child and home)" (h6 false) isAdopt
  study "H6 married" (h6 true) (fun _ => true)
'''
FINE = ", ".join(f".adopt {i}" for i in range(0, 101))
@variant
def RedStrict():
    build("RedStrict", REF_ORIG, adopt_moves=FINE, harness=H_LIFE)
@variant
def RedClosed():
    build("RedClosed", REF_CLOSED, harness=H_BASE.replace("T0 reproduction (unmodified rules, all moves)", "T2 closed gap: (a)(4) added to §23(i)"))
@variant
def RedClosedStrict():
    build("RedClosedStrict", REF_CLOSED, adopt_moves=FINE, harness=H_LIFE)
@variant
def RedOld():
    build("RedOld", REF_NONE, harness=H_BASE.replace("T0 reproduction (unmodified rules, all moves)", "T4 earlier law: no (a)(4)"))
@variant
def RedOldStrict():
    build("RedOldStrict", REF_NONE, adopt_moves=FINE, harness=H_LIFE)


H_FREE = r"""
structure Tally where
  plans : Nat := 0
  consBad : Nat := 0      -- a return whose net is not tax minus its listed credits
  nonrefBad : Nat := 0    -- a return whose net is below minus its refundable credits (nonrefundable credit beyond tax)
  limitBad : Nat := 0     -- household §23 amounts (used + carried) above min(expenses, $17,280)
  paidBad : Nat := 0      -- an adult's §23 amount above what that adult paid
  refBad : Nat := 0       -- refundable §23 above $5,000 on a return
  minTotal : Int := 0
  maxRef : Nat := 0
  maxAd : Nat := 0
  deriving Repr

def audit (f : Facts) : Tally := Id.run do
  let ps := reach f (fun _ => true)
  let mut t : Tally := { minTotal := total f (default f) }
  for p in ps do
    let rs := returns f p
    let os := rs.map (fun r => compute r.2)
    let mut c := t
    c := { c with plans := c.plans + 1 }
    for o in os do
      if o.net != (o.tax : Int) - (sumBy (·.2) o.parts : Nat) then c := { c with consBad := c.consBad + 1 }
      if o.net < - (o.refund : Int) then c := { c with nonrefBad := c.nonrefBad + 1 }
      if o.adRef > 5000 then c := { c with refBad := c.refBad + 1 }
    let adAll := sumBy (fun o => o.adRef + o.adNon + o.adCarry) os
    if adAll > min f.adoption 17280 then c := { c with limitBad := c.limitBad + 1 }
    if !p.joint then
      let oa := compute (soloRet f p .a)
      let ob := compute (soloRet f p .b)
      if oa.adRef + oa.adNon + oa.adCarry > f.adoption * p.adoptA / 100
          || ob.adRef + ob.adNon + ob.adCarry > f.adoption * (100 - p.adoptA) / 100 then
        c := { c with paidBad := c.paidBad + 1 }
    let tot := total f p
    c := { c with minTotal := min c.minTotal tot, maxRef := max c.maxRef (adoptRefund f p),
                  maxAd := max c.maxAd (adoptTotal f p) }
    t := c
  return t

def old (f : Facts) : Facts := { f with a := { f.a with age := 70 }, b := { f.b with age := 70 } }

#eval show IO Unit from do
  IO.println "T5 invariants over every reachable plan, unmodified rules"
  for (n, h) in [("H1", h1), ("H2", h2), ("H3", h3), ("H4", h4), ("H5", h5), ("H6", h6), ("H7", h7), ("H8", h8)] do
    for m in [false, true] do
      IO.println s!"  {n} married={m}: {repr (audit (h m))}"
  IO.println "T5 absurd goals on H6"
  let f := h6 false
  IO.println s!"  no adoption expenses: {repr (audit { f with adoption := 0 })}"
  IO.println s!"  $1,000 of expenses: {repr (audit { f with adoption := 1000 })}"
  IO.println s!"  $3,000 of expenses: {repr (audit { f with adoption := 3000 })}"
  IO.println s!"  $9,000 of expenses: {repr (audit { f with adoption := 9000 })}"
  IO.println s!"  $100,000 of expenses: {repr (audit { f with adoption := 100000 })}"
  IO.println s!"  A has no income: {repr (audit { f with a := adult 0 false false })}"
  IO.println s!"  both have no income: {repr (audit { f with a := adult 0 false false, b := adult 0 false false })}"
  IO.println s!"  both earn $320,000: {repr (audit { f with a := adult 320000 false false, b := adult 320000 false false })}"
  IO.println s!"  married, any filing: {repr (audit (h6 true))}"
  let g : Facts := { old f with kids := [], adoption := 0 }
  IO.println s!"  no child, no adoption, both 70 (no refundable rule applies): {repr (audit g)}"
  let g2 : Facts := { f with kids := [], adoption := 0, a := adult 9000 false false, b := adult 0 false false }
  IO.println s!"  no child, no adoption, age 35, A earns $9,000 (only §32 childless): {repr (audit g2)}"
"""
@variant
def RedFree():
    build("RedFree", REF_ORIG, harness=H_FREE)


K_COMMON = r"""
/-! ## T6: through the kernel -/

def runMoves (f : Facts) (p : Plan) : List Move → Option Plan
  | [] => some p
  | m :: ms => match step f p m with
    | some q => runMoves f q ms
    | none => none

def planH6 : Plan := { default (h6 false) with adoptA := 50 }

theorem lawful_pct (f : Facts) (p : Plan) (h : lawful f p = true) : p.adoptA ≤ 100 := by
  simp only [lawful, Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.2.1.2

theorem step_pct (f : Facts) (p q : Plan) (m : Move) (h : step f p m = some q) : q.adoptA ≤ 100 := by
  unfold step at h
  simp only [] at h
  split at h
  · rename_i hl
    cases h
    exact lawful_pct f _ hl
  · cases h

theorem run_pct (f : Facts) : ∀ (ms : List Move) (p q : Plan), p.adoptA ≤ 100 → runMoves f p ms = some q →
    q.adoptA ≤ 100 := by
  intro ms
  induction ms with
  | nil => intro p q hp h; simp only [runMoves] at h; cases h; exact hp
  | cons m ms ih =>
    intro p q _ h
    simp only [runMoves] at h
    split at h
    · rename_i r hs
      exact ih r q (step_pct f p r m hs) h
    · cases h

theorem adRef_le (r : Ret) : (compute r).adRef ≤ r.adCap := Nat.min_le_left _ _

/-- The household's refundable adoption credit, written out per return (the same quantity as `adoptRefund`, which
folds over the list of returns; the kernel overflows its stack proving the two equal for symbolic facts, so the
general statements below are about this form and the equality is checked on H6 by `decide`). -/
def houseRef (f : Facts) (p : Plan) : Nat :=
  if p.joint then (compute (jointRet f p)).adRef
  else (compute (soloRet f p .a)).adRef + (compute (soloRet f p .b)).adRef

theorem houseRef_h6_plan : houseRef (h6 false) planH6 = adoptRefund (h6 false) planH6 := by decide
theorem houseRef_h6_default : houseRef (h6 false) (default (h6 false)) = adoptRefund (h6 false) (default (h6 false)) := by decide
theorem houseRef_h6_married : houseRef (h6 true) (default (h6 true)) = adoptRefund (h6 true) (default (h6 true)) := by decide
"""
K_ORIG = K_COMMON + r"""
-- replay of the plan and the baselines (unmodified rules)
theorem base_unmarried : total (h6 false) (default (h6 false)) = -5799 := by decide
theorem base_married : total (h6 true) (default (h6 true)) = -5000 := by decide
theorem plan_lawful : (step (h6 false) (default (h6 false)) (.adopt 50)).isSome = true := by decide
theorem plan_is_step : (runMoves (h6 false) (default (h6 false)) [.adopt 50]).map (total (h6 false)) = some (-12750) := by decide
theorem plan_total : total (h6 false) planH6 = -12750 := by decide
theorem plan_refundable : adoptRefund (h6 false) planH6 = 10000 := by decide
theorem default_refundable : adoptRefund (h6 false) (default (h6 false)) = 5000 := by decide
theorem bpays_total : total (h6 false) { default (h6 false) with adoptA := 0 } = -7750 := by decide
-- the carryforward: what the original counts as lost
theorem default_six : lifetime (h6 false) (default (h6 false)) = -9794 := by decide
theorem plan_six : lifetime (h6 false) planH6 = -18434 := by decide
theorem bpays_six : lifetime (h6 false) { default (h6 false) with adoptA := 0 } = -21500 := by decide
/-- Over six years the 50/50 plan is $3,066 worse than B simply paying everything. -/
theorem plan_worse_than_one_payer :
    lifetime (h6 false) planH6 - lifetime (h6 false) { default (h6 false) with adoptA := 0 } = 3066 := by decide

/-- All plans, all facts: on separate returns the refundable part is at most $10,000; on a joint return $5,000. -/
theorem ref_le_all (f : Facts) (p : Plan) : houseRef f p ≤ 10000 := by
  have ha : (compute (soloRet f p .a)).adRef ≤ 5000 := adRef_le (soloRet f p .a)
  have hb : (compute (soloRet f p .b)).adRef ≤ 5000 := adRef_le (soloRet f p .b)
  have hj : (compute (jointRet f p)).adRef ≤ 5000 := adRef_le (jointRet f p)
  unfold houseRef
  split <;> omega

#print axioms base_unmarried
#print axioms base_married
#print axioms plan_lawful
#print axioms plan_is_step
#print axioms plan_total
#print axioms plan_refundable
#print axioms default_refundable
#print axioms bpays_total
#print axioms default_six
#print axioms plan_six
#print axioms bpays_six
#print axioms plan_worse_than_one_payer
#print axioms ref_le_all
#print axioms houseRef_h6_plan
#print axioms houseRef_h6_default
#print axioms houseRef_h6_married
#print axioms run_pct
"""
K_CLOSED = K_COMMON + r"""
-- closed gap: (a)(4) added to §23(i)
theorem base_unmarried : total (h6 false) (default (h6 false)) = -5799 := by decide
theorem base_married : total (h6 true) (default (h6 true)) = -5000 := by decide
theorem plan_lawful : (step (h6 false) (default (h6 false)) (.adopt 50)).isSome = true := by decide
theorem plan_total : total (h6 false) planH6 = -7750 := by decide
theorem plan_refundable : adoptRefund (h6 false) planH6 = 5000 := by decide
theorem bpays_total : total (h6 false) { default (h6 false) with adoptA := 0 } = -7750 := by decide

/-- Every plan with a lawful split, any facts: the household's refundable adoption credit is at most $5,000. -/
theorem ref_le_all (f : Facts) (p : Plan) (hp : p.adoptA ≤ 100) : houseRef f p ≤ 5000 := by
  have ha : (compute (soloRet f p .a)).adRef ≤ 5000 * p.adoptA / 100 := adRef_le (soloRet f p .a)
  have hb : (compute (soloRet f p .b)).adRef ≤ 5000 * (100 - p.adoptA) / 100 := adRef_le (soloRet f p .b)
  have hj : (compute (jointRet f p)).adRef ≤ 5000 := adRef_le (jointRet f p)
  unfold houseRef
  split <;> omega

/-- Every sequence of moves from the default, any household: no sequence reaches more than $5,000 refundable, so
none reaches the plan's $10,000. -/
theorem closed_all_sequences (f : Facts) (ms : List Move) (q : Plan)
    (h : runMoves f (default f) ms = some q) : houseRef f q ≤ 5000 :=
  ref_le_all f q (run_pct f ms (default f) q (Nat.le_refl 100) h)

theorem closed_never_plan (f : Facts) (ms : List Move) (q : Plan)
    (h : runMoves f (default f) ms = some q) : houseRef f q ≠ 10000 := by
  have := closed_all_sequences f ms q h
  omega

#print axioms base_unmarried
#print axioms base_married
#print axioms plan_lawful
#print axioms plan_total
#print axioms plan_refundable
#print axioms bpays_total
#print axioms ref_le_all
#print axioms houseRef_h6_plan
#print axioms houseRef_h6_default
#print axioms houseRef_h6_married
#print axioms closed_all_sequences
#print axioms closed_never_plan
"""
@variant
def RedKernel():
    build("RedKernel", REF_ORIG, harness=K_ORIG)
@variant
def RedKernelClosed():
    build("RedKernelClosed", REF_CLOSED, harness=K_CLOSED)

if __name__ == "__main__":
    for n in sys.argv[1:]:
        VARIANTS[n]()
        print("wrote", n)
