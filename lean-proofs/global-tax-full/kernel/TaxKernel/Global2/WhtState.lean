import TaxKernel.Global

/-!
# TaxKernel.Global2.WhtState (2.4.0, 2026-11-21): withholding rates that depend on the recipient's state

R1 Europe pass 8: NL Wet bronbelasting 2021 and NO skatteloven § 10-80 (only to related low-tax states), LV UIN 5. p. (6)
and SI ZDDPO-2 čl. 70 (low-tax lists), CZ § 36 (1) c) and SK § 43 (1) c) (35 % to non-treaty or non-cooperative
states), FR CGI 182 B III (75 %), ES TRLIRNR art. 25.1 a) (19 % EU/EEA against 24 %), HR čl. 31.

**The recipient facts** (`PaymentX`, optional, read from the payment record in `company.paymentsAbroad`; `Payment` is
unchanged): `"recipientState"` (ISO 3166 alpha-2, `""` = not given) and the flags `"lowTax"`, `"nonCooperative"`,
`"euEea"`, `"treaty"` (`true`/`false`; absent = not given). `paymentsX g` pairs each payment with them.

**The rules** (`StateRule`): a 2.0 `WhtRule` (kind, recipient type, stake, rate, statute) and `tests`, all of which must
hold: `.inStates ["AE", …]`, `.notInStates […]` (the model's statutory list, read on `recipientState`), `.lowTax b`,
`.nonCooperative b`, `.euEea b`, `.treaty b` (read on the flags). **Every conditional rule says what happens when a fact
it reads is not given** (`ifUnknown`, no default):
* `.general`: the rule is not applied; the next matching rule (normally the general rate) is, and `StateWht.notes` lists
  the payment: the conditional rate was not tested (never a silent conditional rate, never a silent general one);
* `.presume`: the rule applies, as the statute presumes it until the recipient shows otherwise; the charge's statute
  ends with `presumedNote`;
* `.gradeC`: no rate; the payment books the 2.0 placeholder, which `computeGlobal` drops and lists as grade C (2.3.0,
  `WhtRead`), and `StateWht.notes` names the missing facts.
A test whose fact is given decides as written; a rule with no tests is unconditional (`StateRule.plain`).

`StateWht` (`name`, `rules`, `round`) books one charge per payment exactly as the 2.0 `Wht.chargeOf` (heading by the
recipient's type, event `payment <i> (<kind>)`, bearer withheld): `StateWht.ofWht w` (plain rules) books **the same
charge as `w`** for every payment, whatever the recipient facts (`ofWht_chargeOf`, `ofWht_charges`), so a model that
switches changes no output until it adds conditional rules. A payment without recipient facts never gets a conditional
rate except through `.presume`, which its statute shows (`whtPick_noFacts`).

Theorems: `StateRule.check_plain`, `whtPick_ofWht`, `StateWht.ofWht_chargeOf`, `StateWht.ofWht_charges`, `StateTest.eval_noFacts`,
`StateRule.check_noFacts`, `whtPick_noFacts`,
`paymentsX_fst`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-! ## The recipient facts -/

structure PaymentX where
  /-- ISO 3166 alpha-2 code of the recipient's state of residence; `""`: not given -/
  recipientState : String := ""
  lowTax : Option Bool := none
  nonCooperative : Option Bool := none
  euEea : Option Bool := none
  treaty : Option Bool := none
  deriving Repr, Inhabited, BEq

def optBoolField (j : Json) (k : String) : Option Bool :=
  match j.getObjVal? k with
  | .ok (.bool b) => some b
  | _ => none

def PaymentX.ofJson (j : Json) : PaymentX :=
  { recipientState := strField j "recipientState", lowTax := optBoolField j "lowTax",
    nonCooperative := optBoolField j "nonCooperative", euEea := optBoolField j "euEea", treaty := optBoolField j "treaty" }

/-- The recipient facts of payment `i` (0-based) of the company line. -/
def paymentXOf (g : CanonGlobal) (i : Nat) : PaymentX :=
  let cj := match g.raw.getObjVal? "company" with | .ok c => c | .error _ => Json.null
  PaymentX.ofJson ((arrField cj "paymentsAbroad").toList.getD i Json.null)

/-- Each payment abroad with its recipient facts (the order of `g.company.paymentsAbroad`). -/
def paymentsX (g : CanonGlobal) : List (Payment × PaymentX) :=
  g.company.paymentsAbroad.zipIdx.map fun (p, i) => (p, paymentXOf g i)

theorem paymentsX_fst (g : CanonGlobal) : (paymentsX g).map Prod.fst = g.company.paymentsAbroad := by
  simp [paymentsX, List.map_map, Function.comp_def]

/-! ## Conditional rules -/

inductive StateTest where
  | inStates (codes : List String)
  | notInStates (codes : List String)
  | lowTax (b : Bool)
  | nonCooperative (b : Bool)
  | euEea (b : Bool)
  | treaty (b : Bool)
  deriving Repr, Inhabited, BEq

namespace StateTest

/-- `some` the test's value when its fact is given, `none` when not. -/
def eval : StateTest → PaymentX → Option Bool
  | .inStates cs, x => if x.recipientState == "" then none else some (cs.contains x.recipientState)
  | .notInStates cs, x => if x.recipientState == "" then none else some (!cs.contains x.recipientState)
  | .lowTax b, x => x.lowTax.map (· == b)
  | .nonCooperative b, x => x.nonCooperative.map (· == b)
  | .euEea b, x => x.euEea.map (· == b)
  | .treaty b, x => x.treaty.map (· == b)

/-- The fact the test reads. -/
def fact : StateTest → String
  | .inStates _ | .notInStates _ => "recipientState" | .lowTax _ => "lowTax"
  | .nonCooperative _ => "nonCooperative" | .euEea _ => "euEea" | .treaty _ => "treaty"

end StateTest

/-- What a conditional rule does when a fact it reads is not given. -/
inductive StateUnknown where
  /-- not applied: the next matching rule is, and the payment is noted -/
  | general
  /-- applied, as the statute presumes; the charge's statute says so -/
  | presume
  /-- no rate: grade C -/
  | gradeC
  deriving Repr, DecidableEq, Inhabited, BEq

structure StateRule where
  rule : WhtRule
  /-- every test must hold -/
  tests : List StateTest := []
  /-- what an absent fact means (no default: every rule says it) -/
  ifUnknown : StateUnknown
  deriving Repr, Inhabited

/-- An unconditional rule. -/
def StateRule.plain (r : WhtRule) : StateRule := { rule := r, ifUnknown := .general }

/-- `some true`: every test holds; `some false`: a given fact fails one; `none`: no test fails but a fact is missing. -/
def StateRule.check (r : StateRule) (x : PaymentX) : Option Bool :=
  let vs := r.tests.map (·.eval x)
  if vs.any (· == some false) then some false else if vs.all (· == some true) then some true else none

def StateRule.missing (r : StateRule) (x : PaymentX) : List String :=
  ((r.tests.filter fun t => (t.eval x).isNone).map (·.fact)).eraseDups

theorem StateRule.check_plain (r : WhtRule) (x : PaymentX) : (StateRule.plain r).check x = some true := by
  simp [StateRule.plain, StateRule.check]

/-- The rule chosen for a payment. -/
inductive WhtPick where
  | rule (r : WhtRule) (presumed : Bool)
  | gradeC
  | none
  deriving Repr, Inhabited

/-- The first matching rule whose tests hold (`.presume` on a missing fact: applied; `.gradeC`: stop), with the
`.general` rules passed over for a missing fact. -/
def whtPick (p : Payment) (x : PaymentX) : List StateRule → WhtPick × List StateRule
  | [] => (.none, [])
  | r :: rs =>
    if !r.rule.matches p then whtPick p x rs else
    match r.check x with
    | some true => (.rule r.rule false, [])
    | some false => whtPick p x rs
    | none =>
      match r.ifUnknown with
      | .general => let q := whtPick p x rs; (q.1, r :: q.2)
      | .presume => (.rule r.rule true, [])
      | .gradeC => (.gradeC, [])

/-- The note a presumed rate's statute carries. -/
def presumedNote : String := " (recipient's state not given: applied as the statute presumes)"

structure StateWht where
  name : String := "withholding tax"
  rules : List StateRule
  round : Rule := {}
  deriving Repr, Inhabited

namespace StateWht

def ofWht (w : Wht) : StateWht := { name := w.name, rules := w.rules.map StateRule.plain, round := w.round }

/-- The charge for payment `p` (index `i`), as the 2.0 `Wht.chargeOf`; no rate: the 2.0 placeholder. -/
def chargeOf (w : StateWht) (p : Payment) (x : PaymentX) (i : Nat) : Charge :=
  let (st, amt) : String × Int := match (whtPick p x w.rules).1 with
    | .rule r pres => (if pres then r.statute ++ presumedNote else r.statute, w.round.ofTicks (r.rateBp * pos p.amount))
    | _ => (noWhtRule, 0)
  charge (if p.toCompany then .cit else .pit) w.name p.amount id (fun _ => amt)
    (event := s!"payment {i + 1} ({p.kind.name})") (bearer := .withheld) (statute := st)

def charges (w : StateWht) (g : CanonGlobal) : List Charge :=
  g.company.paymentsAbroad.zipIdx.map fun (p, i) => w.chargeOf p (paymentXOf g i) i

/-- For `unsupported`: each payment for which a conditional rate was passed over or no rate could be chosen because a
recipient fact is not given (not grade-C lines: the booked rate, or `WhtRead`'s grade-C line, stands). -/
def notes (w : StateWht) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  g.company.paymentsAbroad.zipIdx.flatMap fun (p, i) =>
    let x := paymentXOf g i
    let q := whtPick p x w.rules
    let hd := s!"{(if p.toCompany then Oecd.cit else Oecd.pit).code} withholding on payment {i + 1} ({p.kind.name})"
    (q.2.map fun r =>
      s!"{hd}: conditional rate {r.rule.rateBp} bp ({r.rule.statute}) not tested: {", ".intercalate (r.missing x)} not given; "
        ++ (match q.1 with
            | .rule r' _ => s!"{r'.rateBp} bp booked ({r'.statute})"
            | _ => "no other rate"))
    ++ (match q.1 with
        | .gradeC =>
          let rs := (w.rules.filter fun r => r.rule.matches p && (r.check x).isNone && r.ifUnknown == .gradeC).take 1
          rs.map fun r => s!"{hd}: the rate depends on {", ".intercalate (r.missing x)}, not given ({r.rule.statute})"
        | _ => [])

/-- The withholding as a family (company entities only). -/
def family (w : StateWht) (covers : List Oecd := [.cit]) : Family :=
  { name := w.name, covers, run := fun _ g _ => if g.entity == .company then w.charges g else [] }

end StateWht

/-! ## Theorems -/

theorem whtPick_ofWht (p : Payment) (x : PaymentX) (rs : List WhtRule) :
    whtPick p x (rs.map StateRule.plain)
      = ((match rs.find? (·.matches p) with | some r => WhtPick.rule r false | none => WhtPick.none), []) := by
  induction rs with
  | nil => rfl
  | cons r rs ih =>
    have e : (StateRule.plain r).rule = r := rfl
    simp only [List.map_cons, whtPick, e, StateRule.check_plain]
    by_cases h : r.matches p = true
    · simp [h, List.find?]
    · simp only [Bool.not_eq_true] at h
      simp [h, ih, List.find?]

/-- **A 2.0 `Wht` as plain rules books the same charge for every payment, whatever its recipient facts.** -/
theorem StateWht.ofWht_chargeOf (w : Wht) (p : Payment) (x : PaymentX) (i : Nat) :
    (StateWht.ofWht w).chargeOf p x i = w.chargeOf p i := by
  simp only [StateWht.chargeOf, StateWht.ofWht, whtPick_ofWht, Wht.chargeOf, Wht.amount, Wht.ruleFor]
  cases w.rules.find? (·.matches p) <;> rfl

theorem StateWht.ofWht_charges (w : Wht) (g : CanonGlobal) : (StateWht.ofWht w).charges g = w.charges g.company := by
  simp only [StateWht.charges, Wht.charges]
  apply List.map_congr_left
  intro ⟨p, i⟩ _
  exact StateWht.ofWht_chargeOf w p _ i

theorem StateTest.eval_noFacts (t : StateTest) : t.eval {} = none := by cases t <;> rfl

/-- With no recipient fact given, a conditional rule neither holds nor fails: its `ifUnknown` decides. -/
theorem StateRule.check_noFacts (r : StateRule) (h : r.tests ≠ []) : r.check {} = none := by
  obtain ⟨t, ts, ht⟩ := List.exists_cons_of_ne_nil h
  simp [StateRule.check, StateTest.eval_noFacts, ht]

/-- **No fact given, no silent conditional rate**: for a payment without recipient facts, a rate chosen without the
`presumedNote` is always that of an unconditional rule. -/
theorem whtPick_noFacts (p : Payment) (rs : List StateRule) (r : WhtRule) (h : (whtPick p {} rs).1 = .rule r false) :
    ∃ s ∈ rs, s.rule = r ∧ s.tests = [] := by
  induction rs with
  | nil => simp [whtPick] at h
  | cons s rs ih =>
    have up : (whtPick p {} rs).1 = .rule r false → ∃ t ∈ s :: rs, t.rule = r ∧ t.tests = [] := fun h' => by
      obtain ⟨t, ht, h1, h2⟩ := ih h'; exact ⟨t, by simp [ht], h1, h2⟩
    by_cases hm : s.rule.matches p = true
    · by_cases ht : s.tests = []
      · have hc : s.check {} = some true := by simp [StateRule.check, ht]
        simp only [whtPick, hm, hc, Bool.not_true, Bool.false_eq_true, ↓reduceIte, WhtPick.rule.injEq] at h
        exact ⟨s, by simp, h.1, ht⟩
      · have hc := StateRule.check_noFacts s ht
        simp only [whtPick, hm, hc, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
        cases hu : s.ifUnknown <;> simp only [hu, WhtPick.rule.injEq] at h
        · exact up h
        · simp at h
        · cases h
    · simp only [Bool.not_eq_true] at hm
      simp only [whtPick, hm, Bool.not_false, ↓reduceIte] at h
      exact up h

end TaxKernel.Global
