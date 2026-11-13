import LegalProofs.CaseLaw2.Holdings
import LegalProofs.CaseLaw2.Spec.RuleId

/-!
# Spec: precedential force and the power to change status

A readable default tree (Catala style): each `if` is a rule or a named exception, and each leaf returns the force
with the `RuleId` it rests on. Read next to doctrine.md §§1–4 and §9 items 22–24.

* `relation L S x dom q`: the force the court-at-the-time `S` of precedent `x` has on the bound court `q.dst` at the
  question date `q.t`, on issue domain `dom`, before any cap. The tree is: H1 self → F1 SCOTUS → by domain (state law:
  E1/Erie both directions; federal law: E3) → the federal hierarchy (F7, F11, F12, F13) or the state hierarchy (H1, H2,
  horizontal rule §4.1 H, trial scope §4.1 V, §4.4).
* `force L x h promoted q`: `relation`, raised by adoption (F10, F11, H3, *M.A.P.*), then capped by publication (F9),
  form (F5, F6, memorandum) and the holding's role (F6 *Marks*). `none` when the court's epoch on the decision's date
  is unknown: the third value (DESIGN D5).
* `canChangeStatus L b x dom`: whether decision `b` has power to change the status of `x` on `dom` (§9 item 23).
-/

namespace CaseLaw2.Spec
open CaseLaw2

/-- The question: the bound court at the question date. -/
structure Query where
  dst : CourtEpoch
  /-- the bound decision's unit (or its court's) -/
  dstUnit : Option Nat
  /-- the circuit that binds a trial-level court; the Tax Court's appeal venue (*Golsen*, F12) -/
  dstCircuit : Nat
  /-- TRAP 41.3: the transferor court of the bound decision -/
  dstTransferFrom : Option Nat := none
  t : Date
  deriving Repr, Inhabited

/-- §4.1 H, F7: the force of a court's own precedent on itself. -/
def horizontalForce (L : Lookups) (S : CourtEpoch) (x : Decision) (q : Query) : Force × RuleId :=
  match L.rules.horizontal S.court S.system x.date with
  | some .strong => (.binding, .hStrong)
  | some .soft => (.persuasiveStrong, .hSoft)
  | some .none => (.persuasive, .hNone)
  | some .withinUnitOnly =>
    -- the same unit, both unitless included (as `benchRule` reads it for power); a decision the court holds by
    -- adoption (another court's) belongs to no unit of it (D4 triage)
    if (if x.court == S.court then x.unit else none) == q.dstUnit then (.binding, .hWithinUnit)
    else (.persuasive, .hOtherUnit)
  | none => (.persuasiveStrong, .assumeHorizontalSoft)

/-- The federal hierarchy, for a non-SCOTUS federal precedent (F7, F11, F12, F13). -/
def fedHier (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query) : Force × RuleId :=
  match S.tier with
  | .appellate =>
    if dom == .federalPatent && S.circuit == 13 && q.dst.tier.trialLike then (.binding, .F11b)
    else if S.court == q.dst.court then horizontalForce L S x q
    else if q.dst.tier.trialLike && S.circuit != 0 && q.dstCircuit == S.circuit then
      -- F11(b): from 1 Oct 1982 patent appeals go to the Federal Circuit, so a regional circuit's patent law no
      -- longer binds its district courts (D4 triage)
      if dom == .federalPatent && S.circuit != 13 && fedCirDate ≤ q.t then (.persuasive, .F11b)
      else (.binding, .F7circuit)
    else (.persuasive, .F7otherCircuit)
  | .special => if S.court == q.dst.court then (.persuasiveStrong, .F12self) else (.persuasive, .F13)
  | _ => (.persuasive, .F13)

/-- §4.1 V: an intermediate court's decisions in a trial court of its system. -/
def trialScopeForce (L : Lookups) (S : CourtEpoch) (x : Decision) (q : Query) : Force × RuleId :=
  let ownUnit := x.unit.isSome && x.unit == q.dstUnit
  match L.rules.trialScope S.court S.system q.t with
  | some .statewide => (.binding, .Vstatewide)
  | some .chooseOnConflict => (.bindingAbsentConflict, .Vchoose)
  | some .ownUnitThenAny => if ownUnit then (.binding, .VownUnit) else (.bindingAbsentConflict, .VotherUnit)
  | some .ownUnitOnly => if ownUnit then (.binding, .VownUnit) else (.persuasive, .VownUnitOnly)
  | none => (.binding, .assumeStatewide)

/-- The state hierarchy, source and bound court in one system (H1, H2, §4). -/
def stateHier (L : Lookups) (S : CourtEpoch) (x : Decision) (q : Query) : Force × RuleId :=
  match S.tier with
  | .last => if q.dst.tier == .last then (.persuasive, .H2dual) else (.binding, .H1)
  | .appellate =>
    if q.dst.tier == .last then (.persuasive, .lowerToHigher)
    else if S.court == q.dst.court then horizontalForce L S x q
    else if q.dstTransferFrom == some S.court then (.binding, .TXtransfer)
    else if q.dst.tier == .appellate then (.persuasive, .sisterCourt)
    else trialScopeForce L S x q
  | .appDivTrial =>
    if (q.dst.tier == .trial || q.dst.tier == .special) && x.unit.isSome && x.unit == q.dstUnit then
      (.binding, .appDivBinds)
    else (.persuasive, .S44)
  | .special => if S.court == q.dst.court then (.persuasiveStrong, .F12self) else (.persuasive, .S44)
  | _ => (.persuasive, .S44)

/-- The court-to-court relation, before caps. -/
def relation (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query) : Force × RuleId :=
  -- H1: the highest court (or its successor) is not bound by its own precedent
  if S.tier == .last && q.dst.tier == .last && S.system == q.dst.system && L.sameOrSuccessor S.court q.dst.court then
    (.persuasiveStrong, .H1self)
  -- F1: SCOTUS on federal law
  else if S.scotus then (if dom.federal then (.binding, .F1) else (.persuasive, .F1stateLaw))
  else match dom with
  | .stateLaw s =>
    if S.system == 0 then
      if q.dst.system == 0 then
        (if x.date < erieDate then (.persuasive, .E1preErie) else fedHier L S x dom q)
      else (.persuasive, .E1fedOnState)
    else if S.system == s then
      if q.dst.system == 0 then
        if q.t < erieDate then (.persuasive, .E1preErie)
        else match S.tier with
          | .last => (.binding, .E1)
          | .appellate => (.persuasiveStrong, .E1West)
          | _ => (.persuasive, .E1King)
      else if q.dst.system == s then stateHier L S x q
      else (.persuasive, .otherSystem)
    -- another state's law decided by this system's courts: vertical stare decisis still binds the system's own
    -- lower courts (as on federal law, E3/§4.1; D4 triage)
    else if q.dst.system == S.system && S.system != 0 then stateHier L S x q
    else (.persuasive, .otherSystem)
  | _ =>
    if S.system == 0 then
      if q.dst.system == 0 then fedHier L S x dom q
      else if S.tier == .appellate then
        -- E3: a state that follows "the circuit" follows its own circuit (28 U.S.C. § 41), not every circuit
        match L.rules.stateFollowsCircuit q.dst.system q.t with
        | some f => if q.dst.circuit != 0 && q.dst.circuit == S.circuit then (f, .E3table) else (.persuasive, .E3)
        | none => (.persuasive, .E3)
      else (.persuasive, .F13)
    else if q.dst.system == 0 then (.persuasive, .E3stateOnFederal)
    else if q.dst.system == S.system then stateHier L S x q
    else (.persuasive, .otherSystem)

/-- **Divisions of a court of last resort** (hunt H6; *M.A.P. v. Ryan*, 285 A.2d 310 (D.C. 1971)): a court of last
resort with a court-level horizontal row sits in divisions, and a division is bound by the court's precedent as that
row says ("no division of this court will overrule a prior decision of this court"). The court itself, en banc, is
not bound (`relation`'s H1self; `nothing_binds_last_resort`). `none` = no such row: the question is the court's.
The row is keyed by `d`: the precedent's date for the court's own decisions, the question date for decisions it
holds by adoption (they are its law from the adoption on: *M.A.P.* binds the divisions to the D.C. Circuit's
pre-1971 decisions, which no row dated 1971 covers by their own dates). -/
def divisionRelation (L : Lookups) (S : CourtEpoch) (d : Date) (x : Decision) (q : Query) : Option (Force × RuleId) :=
  if S.tier == .last && q.dst.tier == .last && S.court == q.dst.court then
    match L.rules.horizontalCourt S.court d with
    | some .strong => some (.binding, .hStrong)
    | some .soft => some (.persuasiveStrong, .hSoft)
    | some .none => some (.persuasive, .hNone)
    | some .withinUnitOnly =>
      some (if (if x.court == S.court then x.unit else none) == q.dstUnit then (.binding, .hWithinUnit)
            else (.persuasive, .hOtherUnit))
    | none => none
  else none

/-- The relation as it binds the court as it ordinarily sits: a division where the court sits in divisions. -/
def relationDiv (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query) : Force × RuleId :=
  (divisionRelation L S x.date x q).getD (relation L S x dom q)

/-- The adoptions that take decision `x` (F10, F11, H3, *M.A.P.*). -/
def adoptionsOf (L : Lookups) (x : Decision) : List Adoption :=
  (L.adoptionsFrom x.court).filter (fun a => x.date ≤ a.upTo && a.filter.admits x.unit x.commission)

/-- The force through one adoption: `x` read as a decision of the adopter (as it stands at the question date),
capped by the adoption row's force. -/
def adoptedForce (L : Lookups) (x : Decision) (dom : Domain) (q : Query) (a : Adoption) : Force :=
  match L.epochAt a.adopter q.t with
  | some A => Force.min a.force (relation L A x dom q).1
  | none => .none

/-- Publication cap (F9). -/
def pubCap (L : Lookups) (S : CourtEpoch) (x : Decision) : Force × Option RuleId :=
  match x.pub with
  | some .published => (.binding, none)
  | some _ =>
    match L.rules.unpubForce S.court S.system x.date with
    | some f => (f, some .F9table)
    | none => (.persuasive, some .assumeUnpubPersuasive)
  | none => (.binding, some .assumePublished)

/-- Form and role caps (F5, F6, memorandum). -/
def formCap (x : Decision) (h : Holding) : Force × Option RuleId :=
  let fc : Force × Option RuleId :=
    match x.form with
    | some .equallyDivided => (.none, some .F5)
    | some .memorandum => (.persuasive, some .memorandum)
    | some .plurality =>
      -- HD6: force is per part; a holding from a majority (or per curiam) part binds (D4 triage)
      if h.marks then (.binding, some .F6marks)
      else if h.role == some .majority || h.role == some .perCuriam then (.binding, none)
      else (.persuasive, some .F6)
    | some _ => (.binding, none)
    | none => (.binding, some .assumeFullForm)
  match h.role with
  | some .plurality => if h.marks then (Force.min fc.1 .binding, some .F6marks) else (Force.min fc.1 .persuasive, some .F6)
  | _ => fc

/-- The source court at the precedent's date, promoted to last resort by a Texas writ/pet. refused (S-TX-3). -/
def sourceEpoch (L : Lookups) (x : Decision) (promoted : Bool) : Option CourtEpoch :=
  (L.epochAt x.court x.date).map (fun S => if promoted then { S with tier := .last } else S)

/-- **Force** of holding `h` of decision `x` on the court of query `q` (doctrine §8.2 steps 2, 3, 6; status, steps 1,
4, 5, is applied by `Status`). `none` = unknown court epoch. -/
def force (L : Lookups) (x : Decision) (h : Holding) (promoted : Bool) (q : Query) : Option (Force × List RuleId) :=
  match sourceEpoch L x promoted with
  | none => none
  | some S =>
    let dom := h.domain.getD S.home
    let domPath := if h.domain.isNone then [RuleId.assumeHomeDomain] else []
    let promPath := if promoted then [RuleId.TXpromoted] else []
    let (direct, rid) := relation L S x dom q
    let adoptedMax := (adoptionsOf L x).foldl (fun f a => Force.max f (adoptedForce L x dom q a)) .none
    let raised := Force.max direct adoptedMax
    let adoptPath := if direct.rank < adoptedMax.rank then [RuleId.adopted] else []
    let (pc, pr) := pubCap L S x
    let (fc, fr) := formCap x h
    let result := Force.min raised (Force.min pc fc)
    some (result, domPath ++ promPath ++ adoptPath ++ [rid] ++ pr.toList ++ fr.toList)

/-- `adoptedForce`, for the court as it ordinarily sits (`relationDiv`). -/
def adoptedForceDiv (L : Lookups) (x : Decision) (dom : Domain) (q : Query) (a : Adoption) : Force :=
  match L.epochAt a.adopter q.t with
  | some A => Force.min a.force ((divisionRelation L A q.t x q).getD (relation L A x dom q)).1
  | none => .none

/-- **Force on the court as it ordinarily sits** (hunt H6): `force`, with `relationDiv` for `relation`. It differs
from `force` only where the bound court is a court of last resort asking about its own decisions under a court-level
horizontal row (`forceDiv_eq_force`). -/
def forceDiv (L : Lookups) (x : Decision) (h : Holding) (promoted : Bool) (q : Query) : Option (Force × List RuleId) :=
  match sourceEpoch L x promoted with
  | none => none
  | some S =>
    let dom := h.domain.getD S.home
    let domPath := if h.domain.isNone then [RuleId.assumeHomeDomain] else []
    let promPath := if promoted then [RuleId.TXpromoted] else []
    let (direct, rid) := relationDiv L S x dom q
    let adoptedMax := (adoptionsOf L x).foldl (fun f a => Force.max f (adoptedForceDiv L x dom q a)) .none
    let raised := Force.max direct adoptedMax
    let adoptPath := if direct.rank < adoptedMax.rank then [RuleId.adopted] else []
    let (pc, pr) := pubCap L S x
    let (fc, fr) := formCap x h
    let result := Force.min raised (Force.min pc fc)
    some (result, domPath ++ promPath ++ adoptPath ++ [rid] ++ pr.toList ++ fr.toList)

/-! ## Power to change status (§9 item 23; v1 `mayOverrule`, refined) -/

/-- An en banc–equivalent bench (F7 Irons/mini en banc via `circulationEnBanc`, F8, MI conflict panel). -/
def enBancEquiv (L : Lookups) (B : CourtEpoch) (b : Decision) : Bool :=
  match b.bench with
  | some .enBanc | some .limitedEnBanc | some .wholeCourt | some .conflictPanel => true
  | some .circulated => L.rules.circulationEnBanc B.court B.system b.date == some true
  | _ => false

/-- The same court acting on its own precedent. -/
def benchRule (L : Lookups) (X : CourtEpoch) (B : CourtEpoch) (b x : Decision) : Bool × RuleId :=
  match L.rules.horizontal X.court X.system x.date with
  | some .soft | some .none => (true, .sameCourtSoft)
  | some .strong => (enBancEquiv L B b, .strongNeedsEnBanc)
  | some .withinUnitOnly =>
    if x.unit == b.unit then (enBancEquiv L B b, .withinUnitEnBanc) else (false, .otherUnitNoPower)
  | none => (enBancEquiv L B b, .assumeStrongForPower)

/-- A court of last resort acting on its own precedent (hunt H6): free at any bench (H1), unless a court-level
horizontal row says it sits in divisions; then only an en banc–equivalent bench overrules (*M.A.P. v. Ryan*). -/
def lastResortBench (L : Lookups) (X : CourtEpoch) (B : CourtEpoch) (b x : Decision) : Bool × RuleId :=
  if B.court == X.court then
    match L.rules.horizontalCourt X.court x.date with
    | some .soft | some .none => (true, .sameCourtSoft)
    | some .strong => (enBancEquiv L B b, .strongNeedsEnBanc)
    | some .withinUnitOnly =>
      if x.unit == b.unit then (enBancEquiv L B b, .withinUnitEnBanc) else (false, .otherUnitNoPower)
    | none => (true, .lastResortSelf)
  else (true, .lastResortSelf)

/-- A court of last resort acting on a decision it holds by adoption (hunt H6): free at any bench (H1), unless its
court-level horizontal row on the treating date says it sits in divisions (*M.A.P. v. Ryan*: only the court en banc
departs from the adopted D.C. Circuit decisions). An adopted decision belongs to no unit of the adopter. -/
def adoptedLastResortBench (L : Lookups) (B : CourtEpoch) (b : Decision) : Bool × RuleId :=
  match L.rules.horizontalCourt B.court b.date with
  | some .soft | some .none => (true, .sameCourtSoft)
  | some .strong => (enBancEquiv L B b, .adoptedEnBanc)
  | some .withinUnitOnly => if b.unit.isNone then (enBancEquiv L B b, .withinUnitEnBanc) else (false, .otherUnitNoPower)
  | none => (true, .lastResortSelf)

/-- **canChangeStatus**: decision `b` has power over decision `x` on domain `dom` (`none`: the target's domain is
unknown, read as its court's home domain). `none` result = a court epoch is unknown. -/
def canChangeStatus (L : Lookups) (b x : Decision) (dom? : Option Domain) : Option (Bool × RuleId) :=
  match L.epochAt b.court b.date, L.epochAt x.court x.date with
  | some B, some X =>
    let dom := dom?.getD X.home
    some <|
      if b.date < x.date then (false, .cLater)
      else if B.scotus && (dom.federal || X.system == 0) then (true, .F1abrogate)
      -- (a BAP binds no one and changes no status: F13, BAP persuasive; D4 real data)
      else if B.system == X.system && X.tier.rank < B.tier.rank && B.tier != .bap &&
          (!B.federal || B.tier != .appellate || X.circuit == B.circuit ||
            (B.circuit == 13 && dom == .federalPatent)) &&
          (B.tier != .appDivTrial || (b.unit.isSome && b.unit == x.unit)) then (true, .higherCourt)
      else if B.tier == .last && X.tier == .last && B.system == X.system && L.sameOrSuccessor X.court B.court then
        lastResortBench L X B b x
      -- a trial court's (or appellate division's) own decisions have no binding status to change (F13, §4.4)
      else if B.court == X.court && (X.tier == .trial || X.tier == .appDivTrial) then (false, .noPower)
      else if B.court == X.court && X.tier.rank ≤ B.tier.rank then benchRule L X B b x
      -- an adopter may overrule what it adopted only from at least the adopted decision's dated tier (Kentucky
      -- 1976: the new Court of Appeals is bound by, and cannot overrule, the old court of last resort; D4 triage)
      -- the adopter holds the adopted decision as its own (F10, *Bonner*): its own horizontal rule decides the bench
      else if (adoptionsOf L x).any (·.adopter == b.court) && X.tier.rank ≤ B.tier.rank then
        -- (an adopted decision belongs to no unit of the adopter); a court of last resort is free of what it
        -- adopted unless it sits in divisions (H6)
        if B.tier == .last then adoptedLastResortBench L B b
        else (match benchRule L B B b { x with unit := none } with
         | (ok, .strongNeedsEnBanc) => (ok, .adoptedEnBanc)
         | r => r)
      else (false, .noPower)
  | _, _ => none

end CaseLaw2.Spec
