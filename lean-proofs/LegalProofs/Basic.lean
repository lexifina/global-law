/-!
# Basic model

A deliberately small model of law over time, enough to state the vulnerabilities in `../vulnerabilities/` as theorems.

* A **date** is a natural number written `YYYYMMDD`. For valid calendar dates, numeric order is calendar order, so
  `20200901 ≤ d` reads "on or after 1 September 2020".
* A **provision** is its text as a function of the date: `some text` while it is in force, `none` before it exists and
  after it is repealed (a "(weggefallen)" / "Repealed" placeholder is `none`).
* The legal rules each case relies on (no fine without an existing statutory duty, no binding rule before publication,
  a time-limited rule binds only within its period) are written as definitions, so every theorem below says exactly
  which rule it depends on. Changing a rule changes the definition, and Lean shows which proofs break.
-/

namespace Legal

/-- A date written as `YYYYMMDD` (a plain natural number, so arithmetic tactics apply directly). -/
notation "Date" => Nat

/-- A provision: its text on each date, `none` when it does not exist (not yet enacted, repealed, or never enacted). -/
abbrev Provision := Date → Option String

/-- A provision is in force on `d` when it has text on `d`. -/
def inForce (p : Provision) (d : Date) : Bool := (p d).isSome

/-- A provision that was in force up to the day before `repealedOn` and has been only a placeholder since. -/
def repealedFrom (p : Provision) (repealedOn : Date) : Prop := ∀ d, repealedOn ≤ d → p d = none

/-- A provision that never existed on any date (e.g. a section that a lapsed bill was meant to insert). -/
def neverEnacted (p : Provision) : Prop := ∀ d, p d = none

/-! ## Rule 1: a blanket fine needs an existing duty

A fine provision that defines the offence by pointing at a duty elsewhere ("contrary to § 12(2)") can only be applied
on dates when the duty it points at exists (Basic Law art. 103(2), Administrative Offences Act § 3; BVerfG 2 BvL 1/12).
Courts may not fill the gap by analogy, so the reference is read literally. -/

/-- A fine (or charge) that is triggered by breaching the duty in another provision. -/
structure BlanketRule where
  rule : Provision      -- the fine / charge provision itself
  pointsAt : Provision  -- the provision it names

/-- The rule can be applied on `d` only if it and the provision it names are both in force on `d`. -/
def BlanketRule.applicable (b : BlanketRule) (d : Date) : Bool := inForce b.rule d && inForce b.pointsAt d

/-- **The dead-reference schema.** If the provision a blanket rule points at is repealed from date `r`, the rule
cannot be applied on any date from `r` on, whatever the rule's own text says. -/
theorem dead_reference (b : BlanketRule) (r : Date) (h : repealedFrom b.pointsAt r) :
    ∀ d, r ≤ d → b.applicable d = false := by
  intro d hd
  simp [BlanketRule.applicable, inForce, h d hd]

/-- **The phantom-reference schema.** If the provision named was never enacted, the rule can never be applied. -/
theorem phantom_reference (b : BlanketRule) (h : neverEnacted b.pointsAt) :
    ∀ d, b.applicable d = false := by
  intro d
  simp [BlanketRule.applicable, inForce, h d]

/-! ## Rule 2: no binding rule before publication

A generally binding rule binds from the later of its stated commencement date and its publication date
(Netherlands: Constitution art. 88; Criminal Code art. 1(1); ECHR art. 7 for penalties). -/

/-- A rule with a stated commencement date and a publication date. -/
structure Enactment where
  statedFrom : Date
  publishedOn : Date

/-- The date the rule actually binds from. -/
def Enactment.binds (e : Enactment) (d : Date) : Bool := decide (e.statedFrom ≤ d) && decide (e.publishedOn ≤ d)

/-- **The pre-publication schema.** On days after the stated commencement but before publication, the rule's own text
says it applies, yet it does not bind. -/
theorem prepublication_window (e : Enactment) :
    ∀ d, e.statedFrom ≤ d → d < e.publishedOn → e.binds d = false := by
  intro d _ h2
  have : ¬ e.publishedOn ≤ d := by omega
  simp [Enactment.binds, this]

/-! ## Rule 3: a time-limited rule binds only within its period

A rule that runs "until" a date stops on that date; a later extension binds from its own commencement unless it says it
is retroactive. -/

/-- A time-limited rule and the extension that renewed it. -/
structure Extension where
  endsOn : Date       -- the original end date ("bis zum 31. Dezember 2025")
  extendedFrom : Date -- when the extension took effect
  newUntil : Date     -- the new end date

/-- The rule binds on `d` if `d` is within the original period or within the extended period. -/
def Extension.binds (x : Extension) (d : Date) : Bool :=
  decide (d ≤ x.endsOn) || (decide (x.extendedFrom ≤ d) && decide (d ≤ x.newUntil))

/-- **The empty-period schema.** Between the old end date and the extension's commencement, the rule does not bind. -/
theorem empty_period (x : Extension) :
    ∀ d, x.endsOn < d → d < x.extendedFrom → x.binds d = false := by
  intro d h1 h2
  have a : ¬ d ≤ x.endsOn := by omega
  have b : ¬ x.extendedFrom ≤ d := by omega
  simp [Extension.binds, a, b]

end Legal
