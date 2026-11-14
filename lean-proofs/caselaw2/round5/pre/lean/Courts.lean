import LegalProofs.CaseLaw2.Basic

/-!
# caselaw-lean-2: courts as dated epochs, succession, adoption, and the parameter tables

* A court's identity is a timeline (doctrine §0.2 item 5, §9 item 5): one `CourtEpoch` per period with its own tier.
  The Court of Appeals of Kentucky is the court of last resort to 1975 and an intermediate court from 1976; the
  model reads a precedent's court **at the precedent's date** and the bound court **at the question date**.
* `Succession` (H3, TM5) and `Adoption` (F10, F11, *M.A.P. v. Ryan*, SCR 1.030(8)(a)) are data rows.
* `Rules` is the abstract parameter structure (§9 items 13–19). Every theorem quantifies over all `Rules`; the tables
  instantiate it twice (`firm`: S/L rows only; `all`: with U rows), so no U row is ever a premise (DESIGN D2).
* `Lookups` is the interface the Spec reads the data through. `Env.lookups` is its list-based (specification)
  implementation; `Exec/Env.lean` gives the hash-indexed one and proves them equal.
-/

namespace CaseLaw2

structure CourtEpoch where
  court : Nat
  dateFrom : Date
  dateTo : Date
  system : Nat
  tier : Tier
  lastResortFor : LastResortFor
  circuit : Nat
  /-- District/division/department within an intermediate system. -/
  unit : Option Nat
  firm : Bool
  deriving Repr, DecidableEq, Inhabited

def CourtEpoch.scotus (e : CourtEpoch) : Bool := e.system == 0 && e.tier == .last
def CourtEpoch.federal (e : CourtEpoch) : Bool := e.system == 0
/-- The court's home domain: what it decides when the issue is not extracted (doctrine §8.2, anonymous issue). -/
def CourtEpoch.home (e : CourtEpoch) : Domain := if e.system = 0 then .federalGeneral else .stateLaw e.system

inductive SuccessionKind where
  | rename | replace | split | absorb
  deriving Repr, DecidableEq, Inhabited

def SuccessionKind.ofString? : String → Option SuccessionKind
  | "rename" => some .rename | "replace" => some .replace | "split" => some .split | "absorb" => some .absorb
  | _ => none

structure Succession where
  old : Nat
  new : Nat
  date : Date
  kind : SuccessionKind
  firm : Bool
  deriving Repr, DecidableEq, Inhabited

/-- The adoption notation at the end of a commission or commissioner opinion (doctrine H4, §3.2 Texas; the optional
`commission.tsv`): "Opinion adopted" (and the equivalent "Opinion approved", "adopted as the opinion of the court"),
"Holding approved", "Judgment adopted". `other` = a notation the data could not classify (unknown, D5). A decision
with no `commission.tsv` row has notation `none`. -/
inductive Notation where
  | opinionAdopted | holdingApproved | judgmentAdopted | other
  deriving Repr, DecidableEq, Inhabited

def Notation.ofString? : String → Option Notation
  | "opinionAdopted" | "opinionApproved" | "adoptedAsOpinionOfCourt" => some .opinionAdopted
  | "holdingApproved" => some .holdingApproved
  | "judgmentAdopted" | "judgmentApproved" => some .judgmentAdopted
  | "other" => some .other
  | _ => none

/-- Which decisions of the source court an adoption takes. `unitB`: decisions of the former Fifth Circuit's Unit B,
which the data marks as unit `2` (DEVIATIONS.md). The commission filters (H4) take the source's decisions by their
adoption notation: `noNotation` (adoption.tsv `none`) takes those with no notation row, and those whose notation the
data could not classify (`other`): an adoption that is not shown is no adoption (H4; DEVIATIONS 63). -/
inductive AdoptFilter where
  | all | unitB | opinionAdopted | holdingApproved | judgmentAdopted | noNotation
  deriving Repr, DecidableEq, Inhabited

def AdoptFilter.ofString? : String → Option AdoptFilter
  | "all" => some .all | "unitB" => some .unitB | "opinionAdopted" => some .opinionAdopted
  | "holdingApproved" => some .holdingApproved | "judgmentAdopted" => some .judgmentAdopted
  | "none" => some .noNotation | _ => none

def AdoptFilter.admits : AdoptFilter → Option Nat → Option Notation → Bool
  | .all, _, _ => true
  | .unitB, u, _ => u == some 2
  | .opinionAdopted, _, n => n == some .opinionAdopted
  | .holdingApproved, _, n => n == some .holdingApproved
  | .judgmentAdopted, _, n => n == some .judgmentAdopted
  | .noNotation, _, n => n == none || n == some .other

structure Adoption where
  adopter : Nat
  source : Nat
  upTo : Date
  filter : AdoptFilter
  force : Force
  firm : Bool
  deriving Repr, DecidableEq, Inhabited

/-- The parameter tables (doctrine §9 items 13–19, plus the approved `reviewGrantedForce`). `none` = no row: every
rule that reads a `none` names the fallback it uses in its justification path. -/
structure Rules where
  /-- §4.1 H, F7; keyed by the *precedent's* date (Michigan 1990). -/
  horizontal : (court system : Nat) → Date → Option HRule
  /-- The court-level horizontal row alone (SCHEMA `system = -court_id`), keyed by the precedent's date. A court of
  last resort that sits in divisions has one (D.C. Court of Appeals, *M.A.P. v. Ryan*): its divisions are bound as
  the row says, though the court itself is not bound by its own precedent (H1; hunt H6). -/
  horizontalCourt : (court : Nat) → Date → Option HRule
  /-- §4.1 V; keyed by the question date. A court-level row (SCHEMA `system = -court_id`) for the intermediate
  court whose decisions are asked about overrides the system row. -/
  trialScope : (court system : Nat) → Date → Option TrialScope
  /-- F9, §4.3 U; keyed by the precedent's date. -/
  unpubForce : (court system : Nat) → Date → Option Force
  /-- E3; keyed by the question date. -/
  stateFollowsCircuit : (system : Nat) → Date → Option Force
  /-- F7 conflicting panels. -/
  firstInTime : (court system : Nat) → Date → Option Bool
  /-- F7 Irons/mini en banc. -/
  circulationEnBanc : (court system : Nat) → Date → Option Bool
  /-- F8. -/
  enBancGrantVacates : (court system : Nat) → Date → Option Bool
  /-- S-CA review granted (2016 rule): the force a published opinion keeps while review is pending. -/
  reviewGrantedForce : (court system : Nat) → Date → Option Force

/-- The empty table: every parameter unknown. -/
def Rules.empty : Rules :=
  { horizontal := fun _ _ _ => none, horizontalCourt := fun _ _ => none, trialScope := fun _ _ _ => none, unpubForce := fun _ _ _ => none,
    stateFollowsCircuit := fun _ _ => none, firstInTime := fun _ _ _ => none,
    circulationEnBanc := fun _ _ _ => none, enBancGrantVacates := fun _ _ _ => none,
    reviewGrantedForce := fun _ _ _ => none }

/-! ## Rule rows → `Rules` -/

/-- A `system_rules.tsv` row: `key` = system, or `-court` for a court-level rule. -/
structure RuleRow where
  key : Int
  rule : String
  value : String
  dateFrom : Date
  dateTo : Date
  firm : Bool
  deriving Repr, Inhabited

def ruleKey (rule : String) (key : Int) : String := rule ++ "|" ++ toString key

/-- The value of `rule` for a court on a date: a court-level row first, then a system-level row; within a level the
first row in file order whose date range covers the date. `lookup` gives the rows for a rule key. -/
def ruleValue (lookup : String → List RuleRow) (rule : String) (court system : Nat) (d : Date) : Option String :=
  let pick (k : Int) := ((lookup (ruleKey rule k)).find? (fun r => r.dateFrom ≤ d && d ≤ r.dateTo)).map (·.value)
  match pick (-(court : Int)) with
  | some v => some v
  | none => pick (system : Int)

/-- The value of a court-level row only (`key = -court`). -/
def courtRuleValue (lookup : String → List RuleRow) (rule : String) (court : Nat) (d : Date) : Option String :=
  ((lookup (ruleKey rule (-(court : Int)))).find? (fun r => r.dateFrom ≤ d && d ≤ r.dateTo)).map (·.value)

def parseBool01? : String → Option Bool
  | "1" => some true | "0" => some false | _ => none

/-- `Rules` read through a row lookup. -/
def Rules.ofLookup (lookup : String → List RuleRow) : Rules :=
  let v := ruleValue lookup
  { horizontal := fun c s d => (v "horizontal" c s d).bind HRule.ofString?
    horizontalCourt := fun c d => (courtRuleValue lookup "horizontal" c d).bind HRule.ofString?
    trialScope := fun c s d => (v "trialScope" c s d).bind TrialScope.ofString?
    unpubForce := fun c s d => (v "unpubForce" c s d).bind Force.ofString?
    stateFollowsCircuit := fun s d => (v "stateFollowsCircuit" 0 s d).bind Force.ofString?
    firstInTime := fun c s d => (v "firstInTimeControls" c s d).bind parseBool01?
    circulationEnBanc := fun c s d => (v "circulationCountsAsEnBanc" c s d).bind parseBool01?
    enBancGrantVacates := fun c s d => (v "enBancGrantVacatesPanel" c s d).bind parseBool01?
    reviewGrantedForce := fun c s d => (v "reviewGrantedForce" c s d).bind Force.ofString? }

/-! ## The data environment and its specification lookups -/

structure Env where
  epochs : List CourtEpoch
  successions : List Succession
  adoptions : List Adoption
  rules : List RuleRow

/-- The `firm` environment: only S/L-tagged rows (DESIGN D2). -/
def Env.firm (e : Env) : Env :=
  { epochs := e.epochs.filter (·.firm), successions := e.successions.filter (·.firm),
    adoptions := e.adoptions.filter (·.firm), rules := e.rules.filter (·.firm) }

/-- How the Spec reads the data. -/
structure Lookups where
  epochAt : Nat → Date → Option CourtEpoch
  adoptionsFrom : Nat → List Adoption
  successorsOf : Nat → List Succession
  rules : Rules

def epochCovers (c : Nat) (d : Date) (e : CourtEpoch) : Bool := e.court == c && e.dateFrom ≤ d && d ≤ e.dateTo

/-- Specification lookups: plain list scans. -/
def Env.lookups (e : Env) : Lookups :=
  { epochAt := fun c d => e.epochs.find? (epochCovers c d)
    adoptionsFrom := fun c => e.adoptions.filter (·.source == c)
    successorsOf := fun c => e.successions.filter (·.old == c)
    rules := Rules.ofLookup (fun k => e.rules.filter (fun r => ruleKey r.rule r.key == k)) }

/-- `n` is `o` or a successor of `o` (through at most four succession steps; fuel keeps it structural). -/
def Lookups.succeeds (L : Lookups) : Nat → Nat → Nat → Bool
  | 0, o, n => o == n
  | fuel + 1, o, n => o == n || (L.successorsOf o).any (fun s => L.succeeds fuel s.new n)

def Lookups.sameOrSuccessor (L : Lookups) (o n : Nat) : Bool := L.succeeds 4 o n

theorem Lookups.succeeds_refl (L : Lookups) (f c : Nat) : L.succeeds f c c = true := by
  cases f <;> simp [Lookups.succeeds]

end CaseLaw2
