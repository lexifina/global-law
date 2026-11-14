import LegalProofs.CaseLaw2.Holdings

/-!
# caselaw-lean-2: events (doctrine §5.1, §6, §7)

Two families kept apart (§5.1): **same-case history** (`HEvent`: reversed, vacated, withdrawn, depublished, en banc
grant, review granted, Texas writ notations, …) and **later-case treatment** (`TEvent`: overruled, disapproved,
receded from, abrogated, superseded, and the soft kinds that never change status), plus **supersession by enactment**
(`SEvent`, from `supersessions.tsv` joined to `lawchanges.tsv`).

Only *admitted* rows reach the status layer: a history or treatment row is admitted by the certificate checker
(`Certificate.lean`), which includes the power check (`canChangeStatus`); a treatment must also be `explicit` (§9 item
26). The `Record` holds the admitted rows.
-/

namespace CaseLaw2

/-- Which issues of the target an event reaches. `someIssue`: some issue, unknown which (`partialUnknown`,
`otherGrounds`, history scope `unknown`). -/
inductive Scope where
  | all | issues (ks : List Nat) | someIssue
  /-- some issue among `ks` (or ⊤), unknown which: a `someIssue` event narrowed to the holdings the treating court
  has power over (D4 triage) -/
  | someOf (ks : List Nat)
  deriving Repr, DecidableEq, Inhabited

inductive HKind where
  | affirmed | reversed | vacated | modified | remanded | certDenied | reviewGranted | reviewDismissed
  | depublished | withdrawn | substitutedBy | rehearingEnBancGranted | reinstated | writRefused | other
  deriving Repr, DecidableEq, Inhabited

def HKind.ofString? : String → Option HKind
  | "affirmed" => some .affirmed | "reversed" => some .reversed | "vacated" => some .vacated
  | "modified" => some .modified | "remanded" => some .remanded | "certDenied" => some .certDenied
  | "reviewGranted" => some .reviewGranted | "reviewDismissed" => some .reviewDismissed
  | "depublished" => some .depublished | "withdrawn" => some .withdrawn | "substitutedBy" => some .substitutedBy
  | "rehearingEnBancGranted" => some .rehearingEnBancGranted | "reinstated" => some .reinstated
  | "writRefused" => some .writRefused | "other" => some .other | _ => none

inductive TKind where
  | overruled | disapproved | recededFrom | abrogated | supersededByEnactment
  | limited | questioned | criticized | distinguished | followed | declinedToFollow
  deriving Repr, DecidableEq, Inhabited

def TKind.ofString? : String → Option TKind
  | "overruled" => some .overruled | "disapproved" => some .disapproved | "recededFrom" => some .recededFrom
  | "abrogated" => some .abrogated | "supersededByEnactment" => some .supersededByEnactment
  | "limited" => some .limited | "questioned" => some .questioned | "criticized" => some .criticized
  | "distinguished" => some .distinguished | "followed" => some .followed
  | "declinedToFollow" => some .declinedToFollow | _ => none

/-- §5.1B: the kinds that can change status. -/
def TKind.changesStatus : TKind → Bool
  | .overruled | .disapproved | .recededFrom | .abrogated => true
  | _ => false

/-- TM2 (*Sunburst*). -/
inductive Temporal where
  | retroactive | prospectiveFrom (d : Date) | pureProspective | unknown
  deriving Repr, DecidableEq, Inhabited

def Temporal.ofString? (s : String) : Option Temporal :=
  match s with
  | "retroactive" => some .retroactive | "pureProspective" => some .pureProspective | "unknown" => some .unknown
  | _ =>
    -- digits only (FB-L6: `String.toNat?` also accepts `_` separators)
    let d := (s.drop 16).toString
    if s.startsWith "prospectiveFrom:" && !d.isEmpty && d.all Char.isDigit then d.toNat?.map .prospectiveFrom
    else none

/-- A same-case history event. -/
structure HEvent where
  id : Nat
  target : Nat
  by_ : Option Nat
  date : Date
  kind : HKind
  scope : Scope
  /-- S-TX-3, for a `writRefused` row: the notation is one that promotes (a Texas civil "writ ref'd" before 1 Sept
  1997 or "pet. ref'd" after, by the civil court of last resort; not "n.r.e.", a denial, a dismissal or a criminal
  PDR refusal). The runner reads it from the certified quote (`Run.writPromotes`). -/
  promotes : Bool := true
  deriving Repr, DecidableEq, Inhabited

/-- Round 5 (DESIGN5 §2): a later decision W of a court with power over the target states, in a certified majority
sentence, that the target was overruled by the row's by-decision Y. The runner fills it only when the recognised
check (`Cert.checkRecognised`) passes. -/
structure Recog where
  /-- the recognising decision W -/
  witness : Nat
  /-- date(W) -/
  date : Date
  /-- W's court has power to overrule the target (`canChangeStatus`, on every domain the issue could have) -/
  power : Bool
  deriving Repr, DecidableEq, Inhabited

/-- A later-case treatment. -/
structure TEvent where
  id : Nat
  by_ : Nat
  target : Nat
  date : Date
  kind : TKind
  scope : Scope
  temporal : Temporal
  explicit : Bool
  /-- `false`: admitted without verified power (`okUnverifiedBy`): its effect is `unknown powerUnknown`, not
  negative (D5) -/
  powerKnown : Bool := true
  /-- round 5: the recognition of an implicit row (`explicit = false`) by a later court with power; `none` on every
  explicit row and on a witness row that is only "at risk" -/
  recog : Option Recog := none
  deriving Repr, DecidableEq, Inhabited

/-- A supersession by enactment (§7), joined to its law change. -/
structure SEvent where
  id : Nat
  target : Nat
  /-- the issues it reaches (§7 AB1: issue-limited). The runner reads an issue key as `issues [k]`, and `-` as the
  target's holdings on the amended block (`someIssue` when none is known) -/
  scope : Scope
  enacted : Date
  effective : Date
  retroactiveTo : Option Date
  explicit : Bool
  deriving Repr, DecidableEq, Inhabited

/-- The admitted events and the decisions they refer to. -/
structure Record where
  dec : Nat → Option Decision
  hist : List HEvent
  treat : List TEvent
  supers : List SEvent

end CaseLaw2
