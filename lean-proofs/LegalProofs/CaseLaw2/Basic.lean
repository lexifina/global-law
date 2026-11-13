/-!
# caselaw-lean-2: basic vocabulary

Dates, the graded scale of precedential `Force`, and the enumerations of `SCHEMA.md`. Every enumeration has a parser
from its schema string that returns `none` for anything else (no silent defaults, DESIGN D5); a field the data leaves
open is an `Option` in the model, and every rule that fills an unknown says so in its justification path
(`RuleId.assume*`).

Doctrine ids (`F1`, `E1`, `H1`, `S-CA`, …) refer to `caselaw-lean-2/research/doctrine.md`.
-/

namespace CaseLaw2

/-- A day as `yyyymmdd`. -/
scoped notation "Date" => Nat

/-- The Erie date (doctrine E1): *Erie R.R. v. Tompkins*, decided 25 April 1938. -/
def erieDate : Date := 19380425
/-- F11(b): the Federal Circuit's exclusive patent appellate jurisdiction begins (1 Oct 1982). -/
def fedCirDate : Date := 19821001
/-- The Judicial Code of 1948 (28 U.S.C. § 46(c), in force 1 Sept 1948) gave every court of appeals the en banc
procedure; before it a panel had no en banc court to go to (hunt H3b; *Textile Mills*, 314 U.S. 326 (1941), had
allowed it). -/
def enBancStatuteDate : Date := 19480901

/-- Open-ended upper date. -/
def forever : Date := 99999999

/-! ## Force (doctrine §0.2, §9 item 10) -/

/-- Precedential force, weakest first. -/
inductive Force where
  | none | notCitable | citableNoWeight | persuasive | persuasiveStrong | bindingAbsentConflict | binding
  deriving Repr, DecidableEq, Inhabited

namespace Force

def rank : Force → Nat
  | none => 0 | notCitable => 1 | citableNoWeight => 2 | persuasive => 3 | persuasiveStrong => 4
  | bindingAbsentConflict => 5 | binding => 6

theorem rank_inj {a b : Force} (h : a.rank = b.rank) : a = b := by
  cases a <;> cases b <;> simp_all [rank]

instance : LE Force := ⟨fun a b => a.rank ≤ b.rank⟩
instance (a b : Force) : Decidable (a ≤ b) := inferInstanceAs (Decidable (a.rank ≤ b.rank))
instance : LT Force := ⟨fun a b => a.rank < b.rank⟩
instance (a b : Force) : Decidable (a < b) := inferInstanceAs (Decidable (a.rank < b.rank))

def max (a b : Force) : Force := if a.rank ≤ b.rank then b else a
def min (a b : Force) : Force := if a.rank ≤ b.rank then a else b

@[simp] theorem rank_max (a b : Force) : (max a b).rank = Max.max a.rank b.rank := by
  unfold max; split <;> omega
@[simp] theorem rank_min (a b : Force) : (min a b).rank = Min.min a.rank b.rank := by
  unfold min; split <;> omega

theorem le_binding (a : Force) : a.rank ≤ binding.rank := by cases a <;> decide

/-- Binding, in the strict sense used by the theorems. -/
def isBinding (f : Force) : Bool := f == binding

def ofString? : String → Option Force
  | "binding" => some binding | "bindingAbsentConflict" => some bindingAbsentConflict
  | "persuasiveStrong" => some persuasiveStrong | "persuasive" => some persuasive
  | "citableNoWeight" => some citableNoWeight | "notCitable" => some notCitable | "none" => some none
  | _ => Option.none

def toString : Force → String
  | none => "none" | notCitable => "notCitable" | citableNoWeight => "citableNoWeight"
  | persuasive => "persuasive" | persuasiveStrong => "persuasiveStrong"
  | bindingAbsentConflict => "bindingAbsentConflict" | binding => "binding"

instance : ToString Force := ⟨toString⟩

end Force

/-! ## Courts, decisions and issues -/

inductive Tier where
  | last | appellate | bap | trial | special | appDivTrial
  deriving Repr, DecidableEq, Inhabited

/-- Rank within a system (higher reviews lower). -/
def Tier.rank : Tier → Nat
  | .last => 3 | .appellate => 2 | .appDivTrial => 1 | .bap => 1 | .trial => 0 | .special => 0

def Tier.ofString? : String → Option Tier
  | "L" => some .last | "A" => some .appellate | "B" => some .bap | "T" => some .trial | "S" => some .special
  | "D" => some .appDivTrial | _ => none

/-- Trial-level courts (doctrine F13, §4.4): district, state trial, special and bankruptcy courts. -/
def Tier.trialLike : Tier → Bool
  | .trial | .special | .bap | .appDivTrial => true
  | _ => false

inductive LastResortFor where
  | all | civil | criminal | notLast
  deriving Repr, DecidableEq, Inhabited

def LastResortFor.ofString? : String → Option LastResortFor
  | "all" => some .all | "civil" => some .civil | "criminal" => some .criminal | "-" => some .notLast | _ => none

inductive Bench where
  | panel | division | enBanc | limitedEnBanc | circulated | conflictPanel | wholeCourt
  deriving Repr, DecidableEq, Inhabited

def Bench.ofString? : String → Option Bench
  | "panel" => some .panel | "division" => some .division | "enBanc" => some .enBanc
  | "limitedEnBanc" => some .limitedEnBanc | "circulated" => some .circulated
  | "conflictPanel" => some .conflictPanel | "wholeCourt" => some .wholeCourt | _ => none

inductive Publication where
  | published | unpublished | table | summaryOrder | memorandum
  deriving Repr, DecidableEq, Inhabited

def Publication.ofString? : String → Option Publication
  | "published" => some .published | "unpublished" => some .unpublished | "table" => some .table
  | "summaryOrder" => some .summaryOrder | "memorandum" => some .memorandum | _ => none

def Publication.toString : Publication → String
  | .published => "published" | .unpublished => "unpublished" | .table => "table"
  | .summaryOrder => "summaryOrder" | .memorandum => "memorandum"

inductive Form where
  | full | perCuriam | summaryAffirmance | equallyDivided | certifiedAnswer | plurality | memorandum
  deriving Repr, DecidableEq, Inhabited

def Form.ofString? : String → Option Form
  | "full" => some .full | "perCuriam" => some .perCuriam | "summaryAffirmance" => some .summaryAffirmance
  | "equallyDivided" => some .equallyDivided | "certifiedAnswer" => some .certifiedAnswer
  | "plurality" => some .plurality | "memorandum" => some .memorandum | _ => none

/-- Issue domains (doctrine §9 item 2). -/
inductive Domain where
  | federalGeneral | federalPatent | federalTax | stateLaw (system : Nat)
  deriving Repr, DecidableEq, Inhabited

def Domain.federal : Domain → Bool
  | .stateLaw _ => false
  | _ => true

def Domain.ofString? (s : String) : Option Domain :=
  match s with
  | "federalGeneral" => some .federalGeneral | "federalPatent" => some .federalPatent
  | "federalTax" => some .federalTax
  | _ => if s.startsWith "stateLaw:" then ((s.drop 9).toString.toNat?).map .stateLaw else none

/-- Opinion role of a holding (SCHEMA holdings.role). -/
inductive Role where
  | majority | plurality | perCuriam
  deriving Repr, DecidableEq, Inhabited

def Role.ofString? : String → Option Role
  | "majority" => some .majority | "plurality" => some .plurality | "perCuriam" => some .perCuriam | _ => none

inductive Answer where
  | yes | no
  deriving Repr, DecidableEq, Inhabited

def Answer.ofString? : String → Option Answer
  | "yes" => some .yes | "no" => some .no | _ => none

/-- Opinion part a certificate's quote sits in. -/
inductive Part where
  | majority | plurality | perCuriam | concurrence | dissent
  deriving Repr, DecidableEq, Inhabited

def Part.ofString? : String → Option Part
  | "majority" => some .majority | "plurality" => some .plurality | "perCuriam" => some .perCuriam
  | "concurrence" => some .concurrence | "dissent" => some .dissent | _ => none

/-- Doctrine tags (doctrine.md §0.1). U rows never enter the `firm` rules. -/
inductive Tag where
  | S | L | U
  deriving Repr, DecidableEq, Inhabited

def Tag.ofString? : String → Option Tag
  | "S" => some .S | "L" => some .L | "U" => some .U | _ => none

/-- A row is firm unless tagged `U` (DESIGN D2: U rows are never premises). An untagged row (`-`, e.g. the v1 court
table, which is data, not a doctrine reading) is firm (D4 real-data triage). -/
def Tag.firmStr (s : String) : Bool := s != "U"

/-- Horizontal stare decisis within a court (doctrine §4.1 H). -/
inductive HRule where
  | strong | soft | none | withinUnitOnly
  deriving Repr, DecidableEq, Inhabited

def HRule.ofString? : String → Option HRule
  | "strong" => some .strong | "soft" => some .soft | "none" => some .none
  | "withinUnitOnly" => some .withinUnitOnly | _ => Option.none

/-- Which intermediate-court decisions bind a trial court (doctrine §4.1 V). -/
inductive TrialScope where
  | statewide | chooseOnConflict | ownUnitThenAny | ownUnitOnly
  deriving Repr, DecidableEq, Inhabited

def TrialScope.ofString? : String → Option TrialScope
  | "statewide" => some .statewide | "statewideChooseOnConflict" => some .chooseOnConflict
  | "ownUnitThenAny" => some .ownUnitThenAny | "ownUnitOnly" => some .ownUnitOnly | _ => none

/-- TSV dates and ids where SCHEMA says `0` = unknown: `0 ↦ none` (DESIGN D5). -/
def optNat (n : Nat) : Option Nat := if n = 0 then none else some n

end CaseLaw2
