import LegalProofs.CaseLaw2.Events
import LegalProofs.CaseLaw2.Spec.RuleId
import LegalProofs.CaseLaw2.Spec.Authority

/-!
# Spec: status of a holding on two dates (doctrine §5, §6, §7, §8.2 steps 1, 4, 5; §9 item 25)

`statusOf L rec x k t u`: the status of issue `k` of decision `x` as known on date `t` (asOf), for conduct on date `u`.
It is three-valued (DESIGN D5): `neg n` (a negative event admitted), `good` (none admitted), `unknown r` (an admitted
event that may or may not reach this issue, or a rule the tables leave open).

Each admitted event compiles to an `Effect`: what it imposes, from when (`start`), until when (`lapse`: revival T3,
reinstatement, review dismissed), on which issues (`scope`), for which conduct (`conductFrom`: prospective overruling
TM2, supersession AB1). Status is a **fold of a join over the effects**; the join takes the more severe status, so
status does not depend on the order of the events (`status_perm`, `same_day_events_commute`).
-/

namespace CaseLaw2.Spec
open CaseLaw2

/-! ## Status values -/

/-- Negative states, least severe first. -/
inductive Neg where
  | reviewPending | superseded | abrogated | overruled | reversed | depublished | vacated | withdrawn
  deriving Repr, DecidableEq, Inhabited

def Neg.idx : Neg → Nat
  | .reviewPending => 0 | .superseded => 1 | .abrogated => 2 | .overruled => 3 | .reversed => 4
  | .depublished => 5 | .vacated => 6 | .withdrawn => 7

/-- Why a status is unknown. -/
inductive Unk where
  | partialScope | enBancRuleUnknown
  /-- an explicit overruling-type treatment whose power the data leave open: a court epoch is unknown, or the
  target's issue domain is unknown and the candidate domains disagree (D5; D4 triage, DIFFTEST.md) -/
  | powerUnknown
  /-- round 5 (DESIGN5 §2.3): a later court with power has said the decision was overruled by an earlier decision
  that did not say so itself; this is the status between that earlier decision and the later court's statement -/
  | recognisedLater
  deriving Repr, DecidableEq, Inhabited

def Unk.idx : Unk → Nat
  | .partialScope => 0 | .enBancRuleUnknown => 1 | .powerUnknown => 2 | .recognisedLater => 3

inductive Status where
  | good | unknown (r : Unk) | neg (n : Neg)
  deriving Repr, DecidableEq, Inhabited

def Status.rank : Status → Nat
  | .good => 0
  | .unknown r => 1 + r.idx
  | .neg n => 10 + n.idx

theorem Status.rank_inj {a b : Status} (h : a.rank = b.rank) : a = b := by
  rcases a with _ | r | n <;> rcases b with _ | r' | n' <;>
    (try cases r) <;> (try cases r') <;> (try cases n) <;> (try cases n') <;>
    simp_all [rank, Neg.idx, Unk.idx]

/-- The more severe of two statuses. -/
def Status.join (a b : Status) : Status := if a.rank ≤ b.rank then b else a

@[simp] theorem Status.rank_join (a b : Status) : (a.join b).rank = max a.rank b.rank := by
  unfold join; split <;> omega

theorem Status.join_comm (a b : Status) : a.join b = b.join a :=
  Status.rank_inj (by simp; omega)

theorem Status.join_assoc (a b c : Status) : (a.join b).join c = a.join (b.join c) := by
  unfold join
  split <;> split <;> (try split) <;> (try split) <;> first | rfl | (apply Status.rank_inj; simp_all; omega) | omega

@[simp] theorem Status.join_good (a : Status) : a.join .good = a := by
  unfold join; cases a <;> simp [rank]

@[simp] theorem Status.good_join (a : Status) : Status.good.join a = a := by
  unfold join; simp [rank]

theorem Status.rank_zero_iff (a : Status) : a.rank = 0 ↔ a = .good := by
  cases a <;> simp [rank] <;> omega

theorem Status.isNeg_iff (a : Status) : 10 ≤ a.rank ↔ ∃ n, a = .neg n := by
  cases a with
  | good => simp [rank]
  | unknown r => cases r <;> simp [rank, Unk.idx]
  | neg n => simp [rank]

/-! ## Effects -/

/-- Which lines of authority an effect reaches (hunt H4). After an adoption cut-off a decision is held by several
courts: its own court (the original line) and each adopter (an heir: the Eleventh Circuit holds the old Fifth
Circuit's decisions under *Bonner*). An overruling by one of them changes the status in its own line only. `all`:
every line (history, statutes, SCOTUS, and every decision with no heir). `lines orig reached unreached`: the
original line when `orig`, the adopters in `reached`, and not those in `unreached`. -/
inductive Reach where
  | all
  | lines (orig : Bool) (reached unreached : List Nat)
  deriving Repr, DecidableEq, Inhabited

structure Effect where
  /-- what the event imposes on an issue it reaches (`neg n` or `unknown r`) -/
  eff : Status
  start : Date
  lapse : Option Date
  scope : Scope
  conductFrom : Date
  rule : RuleId
  /-- the event row -/
  src : Nat
  /-- the decision that caused it (`none`: a statute, or a history row whose deciding court is unknown) -/
  actor : Option Nat := none
  /-- the lines of authority it reaches (H4) -/
  reach : Reach := .all
  deriving Repr, DecidableEq, Inhabited

/-- What an event that reaches only part of a decision says about the part it may not reach: `unknown
partialScope` (§8.2 "partiallyNegative": some part is, or may be, changed), whether the event is negative or itself
unknown (D4 triage). -/
def Status.partially : Status → Status
  | .good => .good
  | _ => .unknown .partialScope

/-- In force on question date `t`, for conduct date `u`. -/
def Effect.live (e : Effect) (t u : Date) : Bool :=
  e.start ≤ t && e.lapse.all (fun l => t < l) && e.conductFrom ≤ u

/-- What the effect contributes to issue `k`. A partial event reaches the anonymous issue ⊤ (and, when its scope is
unknown, every issue) only as `unknown partialScope`; an event on named issues does not touch any other named issue
(§5.1B, HD4). -/
def Effect.contrib (e : Effect) (k : Nat) (t u : Date) : Status :=
  if e.live t u then
    match e.scope with
    | .all => e.eff
    | .issues ks => if ks.contains k then e.eff else if k == anonIssue then e.eff.partially else .good
    | .someIssue => e.eff.partially
    | .someOf ks => if k == anonIssue || ks.contains k then e.eff.partially else .good
  else .good

/-- **Status**: the fold of `join` over the effects. -/
def status (effs : List Effect) (k : Nat) (t u : Date) : Status :=
  effs.foldl (fun s e => s.join (e.contrib k t u)) .good

def goodLaw (effs : List Effect) (k : Nat) (t u : Date) : Bool := status effs k t u == .good

/-! ## Status in a line of authority (hunt H4) -/

/-- The effect reaches a court, given which adopters' lines the court is in. A court in a reached adopter's line is
reached; otherwise it reads the decision through the original line, unless it is in the line of an adopter the
effect does not reach. -/
def Effect.reaches (inLine : Nat → Bool) (e : Effect) : Bool :=
  match e.reach with
  | .all => true
  | .lines orig reached unreached => reached.any inLine || (orig && !unreached.any inLine)

/-- The effects that reach a court. -/
def heirEffects (inLine : Nat → Bool) (effs : List Effect) : List Effect := effs.filter (·.reaches inLine)

/-- **Status relative to a court's line of authority**: the status of issue `k` as the effects that reach the
court leave it. -/
def statusFor (inLine : Nat → Bool) (effs : List Effect) (k : Nat) (t u : Date) : Status :=
  status (heirEffects inLine effs) k t u

/-! ## Generic lemmas about the fold (proved once) -/

theorem foldl_join (l : List Effect) (k : Nat) (t u : Date) (s : Status) :
    l.foldl (fun s e => s.join (e.contrib k t u)) s = s.join (status l k t u) := by
  induction l generalizing s with
  | nil => simp [status]
  | cons e l ih =>
    simp only [List.foldl_cons, status]
    rw [ih, ih (Status.good.join _), Status.good_join, Status.join_assoc]

theorem status_cons (e : Effect) (l : List Effect) (k : Nat) (t u : Date) :
    status (e :: l) k t u = (e.contrib k t u).join (status l k t u) := by
  simp only [status, List.foldl_cons, Status.good_join]
  exact foldl_join l k t u _

/-- Status does not depend on the order of the events. -/
theorem status_perm {l₁ l₂ : List Effect} (h : l₁.Perm l₂) (k : Nat) (t u : Date) :
    status l₁ k t u = status l₂ k t u := by
  unfold status
  apply List.Perm.foldl_eq' h
  intro x _ y _ z
  rw [Status.join_assoc, Status.join_comm (x.contrib k t u), ← Status.join_assoc]

/-- Two events (e.g. on one day, on distinct holdings) commute. -/
theorem same_day_events_commute (l₁ l₂ : List Effect) (e₁ e₂ : Effect) (k : Nat) (t u : Date) :
    status (l₁ ++ e₁ :: e₂ :: l₂) k t u = status (l₁ ++ e₂ :: e₁ :: l₂) k t u :=
  status_perm (List.Perm.append_left l₁ (List.Perm.swap e₂ e₁ l₂)) k t u

/-- An effect that contributes nothing leaves the status unchanged. -/
theorem status_cons_good (e : Effect) (l : List Effect) (k : Nat) (t u : Date) (h : e.contrib k t u = .good) :
    status (e :: l) k t u = status l k t u := by
  rw [status_cons, h, Status.good_join]

/-- **Partial events touch only their holdings**: an event on issues `ks` leaves every other named issue as it was. -/
theorem partial_touches_only (e : Effect) (l : List Effect) (k : Nat) (t u : Date) (ks : List Nat)
    (hs : e.scope = .issues ks) (hk : k ∉ ks) (hk0 : k ≠ anonIssue) :
    status (e :: l) k t u = status l k t u := by
  apply status_cons_good
  unfold Effect.contrib
  split
  · rw [hs]
    simp [hk, hk0]
  · rfl

/-- **Prospectivity**: an effect for conduct from `e.conductFrom` (a supersession's effective or retroactive date, or a
prospective overruling) does not reach earlier conduct. -/
theorem prospective_no_effect (e : Effect) (l : List Effect) (k : Nat) (t u : Date) (hu : u < e.conductFrom) :
    status (e :: l) k t u = status l k t u := by
  apply status_cons_good
  have h1 : ¬ e.conductFrom ≤ u := Nat.not_le.mpr hu
  simp [Effect.contrib, Effect.live, h1]

/-- Nor does any effect reach a question date before it starts. -/
theorem before_start_no_effect (e : Effect) (l : List Effect) (k : Nat) (t u : Date) (ht : t < e.start) :
    status (e :: l) k t u = status l k t u := by
  apply status_cons_good
  have h1 : ¬ e.start ≤ t := Nat.not_le.mpr ht
  simp [Effect.contrib, Effect.live, h1]

theorem status_rank_mono_of (l : List Effect) (k : Nat) (t u t' u' : Date)
    (h : ∀ e ∈ l, (e.contrib k t u).rank ≤ (e.contrib k t' u').rank) :
    (status l k t u).rank ≤ (status l k t' u').rank := by
  induction l with
  | nil => simp [status]
  | cons e l ih =>
    rw [status_cons, status_cons]
    simp only [Status.rank_join]
    have := h e (by simp)
    have := ih (fun e he => h e (by simp [he]))
    omega

/-- **Monotonicity** (§9 22(e), generalising v1 `overruledOn_mono`): without lapse (no vacatur, withdrawal or reversal
of an overruling decision, no reinstatement, no dismissal of review), status only worsens as the question date
advances. -/
theorem status_mono (l : List Effect) (k : Nat) (u t t' : Date) (hle : t ≤ t')
    (hnl : ∀ e ∈ l, e.lapse = none) : (status l k t u).rank ≤ (status l k t' u).rank := by
  apply status_rank_mono_of
  intro e he
  unfold Effect.contrib
  have hl := hnl e he
  by_cases h1 : e.live t u = true
  · have h2 : e.live t' u = true := by
      unfold Effect.live at h1 ⊢; rw [hl] at h1 ⊢
      simp only [Option.all_none, Bool.and_true, Bool.and_eq_true, decide_eq_true_eq] at h1 ⊢
      exact ⟨Nat.le_trans h1.1 hle, h1.2⟩
    simp [h1, h2]
  · rw [if_neg h1]; exact Nat.zero_le _

/-- Without lapse, once negative, always negative; and good law on a later date was good law earlier. -/
theorem neg_stays_neg (l : List Effect) (k : Nat) (u t t' : Date) (hle : t ≤ t') (hnl : ∀ e ∈ l, e.lapse = none)
    (n : Neg) (h : status l k t u = .neg n) : ∃ n', status l k t' u = .neg n' := by
  have hm := status_mono l k u t t' hle hnl
  rw [h] at hm
  exact (Status.isNeg_iff _).mp (Nat.le_trans (by simp [Status.rank]) hm)

theorem goodLaw_antitone (l : List Effect) (k : Nat) (u t t' : Date) (hle : t ≤ t') (hnl : ∀ e ∈ l, e.lapse = none)
    (h : goodLaw l k t' u = true) : goodLaw l k t u = true := by
  have hm := status_mono l k u t t' hle hnl
  simp only [goodLaw, beq_iff_eq] at h ⊢
  rw [h] at hm
  exact (Status.rank_zero_iff _).mp (Nat.le_zero.mp hm)

/-- Status only worsens as the conduct date advances (every effect reaches later conduct if it reaches earlier). -/
theorem status_mono_conduct (l : List Effect) (k : Nat) (t u u' : Date) (hle : u ≤ u') :
    (status l k t u).rank ≤ (status l k t u').rank := by
  apply status_rank_mono_of
  intro e _
  unfold Effect.contrib
  by_cases h1 : e.live t u = true
  · have h2 : e.live t u' = true := by
      unfold Effect.live at h1 ⊢
      simp only [Bool.and_eq_true, decide_eq_true_eq] at h1 ⊢
      exact ⟨h1.1, Nat.le_trans h1.2 hle⟩
    simp [h1, h2]
  · rw [if_neg h1]; exact Nat.zero_le _

/-- **Revival refutes unrestricted monotonicity** (T3): an overruling whose overruling decision is later vacated
lapses, and the holding is good law again. The monotonicity theorem's no-lapse hypothesis cannot be dropped. -/
theorem revival_counterexample :
    ∃ (l : List Effect) (k : Nat) (u t t' : Date), t ≤ t' ∧ status l k t u = .neg .overruled ∧
      status l k t' u = .good :=
  ⟨[{ eff := .neg .overruled, start := 19600101, lapse := some 19700101, scope := .all, conductFrom := 0,
      rule := .treatment, src := 1 }], 0, 0, 19650101, 19750101, by decide, by decide, by decide⟩

/-- **Status after an adoption cut-off is per heir** (hunt H4; *Bonner*): an overruling that does not reach an
adopter leaves the status unchanged for every court in that adopter's line (and in no reached adopter's line). The
Fifth Circuit's 1983 en banc overruling of a pre-split decision does not change it in the Eleventh. -/
theorem adopted_status_per_heir (inLine : Nat → Bool) (e : Effect) (l : List Effect) (k : Nat) (t u : Date)
    (orig : Bool) (reached unreached : List Nat) (a : Nat) (hr : e.reach = .lines orig reached unreached)
    (hnr : reached.any inLine = false) (ha : a ∈ unreached) (hin : inLine a = true) :
    statusFor inLine (e :: l) k t u = statusFor inLine l k t u := by
  have hu : unreached.any inLine = true := List.any_eq_true.mpr ⟨a, ha, hin⟩
  have : e.reaches inLine = false := by simp [Effect.reaches, hr, hnr, hu]
  simp [statusFor, heirEffects, List.filter, this]

/-- An heir's own overruling stays in its line: it does not reach a court outside the lines it reaches (the
Eleventh Circuit's en banc overruling of an old Fifth Circuit decision does not change it in the Fifth). -/
theorem heir_overruling_stays_in_line (inLine : Nat → Bool) (e : Effect) (l : List Effect) (k : Nat) (t u : Date)
    (reached unreached : List Nat) (hr : e.reach = .lines false reached unreached)
    (hnr : reached.any inLine = false) : statusFor inLine (e :: l) k t u = statusFor inLine l k t u := by
  have : e.reaches inLine = false := by simp [Effect.reaches, hr, hnr]
  simp [statusFor, heirEffects, List.filter, this]

/-- Where every effect reaches every line (no heir, or only history, statutes and SCOTUS), status does not depend
on the court asking. -/
theorem statusFor_all (inLine : Nat → Bool) (l : List Effect) (k : Nat) (t u : Date)
    (h : ∀ e ∈ l, e.reach = .all) : statusFor inLine l k t u = status l k t u := by
  have : heirEffects inLine l = l := by
    unfold heirEffects
    apply List.filter_eq_self.mpr
    intro e he
    simp [Effect.reaches, h e he]
  simp [statusFor, this]

/-! ## Compiling admitted events to effects -/

def minDate? (l : List Date) : Option Date := l.foldl (fun m d => some (match m with | none => d | some m => min m d)) none

/-- The first date on or after `after` on which decision `b` lapsed: vacated, withdrawn, substituted, depublished, or
reversed, each on every issue (T3, TM3; an en banc grant that vacates the panel reaches here as `vacated`, see
`effectsOf`). A partial event leaves the overruling standing (revival is not automatic, T3; D4 triage). `hist` is
`b`'s history. -/
def lapseOfDecision (hist : List HEvent) (after : Date) : Option Date :=
  minDate? ((hist.filter (fun h => after ≤ h.date && h.scope == .all &&
      (h.kind == .vacated || h.kind == .withdrawn || h.kind == .substitutedBy || h.kind == .depublished ||
       h.kind == .reversed))).map (·.date))

/-- The first reinstatement on or after `after`. -/
def reinstatedAfter (hist : List HEvent) (after : Date) : Option Date :=
  minDate? ((hist.filter (fun h => after ≤ h.date && h.kind == .reinstated)).map (·.date))

/-- The end of a pending review: dismissed, or decided (S-CA (e)(2)). -/
def reviewEnd (hist : List HEvent) (after : Date) : Option Date :=
  minDate? ((hist.filter (fun h => after < h.date &&
      (h.kind == .reviewDismissed || h.kind == .affirmed || h.kind == .reversed || h.kind == .modified))).map (·.date))

/-- The effect of a same-case history event of decision `x`, whose court reads as `X` on its date (§5.1A, F4, F8,
S-CA, TM3). `hist` is `x`'s history. -/
def histEffect (L : Lookups) (X : Option CourtEpoch) (hist : List HEvent) (h : HEvent) : Option Effect :=
  let mk (s : Status) (lapse : Option Date) : Effect :=
    { eff := s, start := h.date, lapse, scope := h.scope, conductFrom := 0, rule := .history, src := h.id,
      actor := h.by_ }
  match h.kind with
  | .reversed => some (mk (.neg .reversed) (reinstatedAfter hist h.date))
  | .vacated => some (mk (.neg .vacated) (reinstatedAfter hist h.date))
  | .withdrawn | .substitutedBy => some (mk (.neg .withdrawn) (reinstatedAfter hist h.date))
  | .depublished => some (mk (.neg .depublished) (reinstatedAfter hist h.date))
  | .rehearingEnBancGranted =>
    match X.bind (fun X => L.rules.enBancGrantVacates X.court X.system h.date) with
    | some true => some (mk (.neg .vacated) (reinstatedAfter hist h.date))
    | some false => none
    | none => some (mk (.unknown .enBancRuleUnknown) (reinstatedAfter hist h.date))
  | .reviewGranted =>
    match X.bind (fun X => L.rules.reviewGrantedForce X.court X.system h.date) with
    | some f => some (mk (.neg (if f.rank ≤ Force.notCitable.rank then .depublished else .reviewPending))
        (minDate? ((reviewEnd hist h.date).toList ++ (reinstatedAfter hist h.date).toList)))
    | none => none
  | _ => none

/-- The conduct dates a treatment reaches (TM2). Unknown → retroactive (*Harper*; recorded in the path). -/
def temporalConductFrom (tm : Temporal) (byDate : Date) : Date :=
  match tm with
  | .retroactive | .unknown => 0
  | .prospectiveFrom d => d
  | .pureProspective => byDate + 1

/-- The effect of an admitted treatment (§5.1B, T1, T3): only explicit status-changing kinds; it lapses when the
treating decision does. `byHist` is the treating decision's history. -/
def treatEffect (byHist : List HEvent) (tr : TEvent) : Option Effect :=
  if tr.explicit && tr.kind.changesStatus then
    some { eff := if tr.powerKnown then .neg (if tr.kind == .abrogated then .abrogated else .overruled)
                  else .unknown .powerUnknown, start := tr.date,
           lapse := lapseOfDecision byHist tr.date, scope := tr.scope,
           conductFrom := temporalConductFrom tr.temporal tr.date,
           rule := (match tr.temporal with | .prospectiveFrom _ | .pureProspective => .prospective | _ => .treatment),
           src := tr.id, actor := some tr.by_ }
  else none

/-- The earlier of two optional dates. -/
def minOpt : Option Date → Option Date → Option Date
  | none, b => b
  | a, none => a
  | some a, some b => some (min a b)

/-- **Recognised overruling** (round 5, DESIGN5 §2.3). A row with `recog = some r` says: a later decision W
(`r.witness`, dated `r.date`) of a court with power over the target states that the target was overruled by the
row's by-decision Y, which did not say so itself (`explicit = false`). Two effects: from date(Y) the status is
`unknown recognisedLater` (the overruling had happened, no court with power had said so); from date(W) it is
negative, attributed to Y. Both lapse when Y does; the second also when W does. There is no revival. `byHist` is
Y's history, `wHist` W's. Without W's power there is no effect at all. -/
def recogEffects (byHist wHist : List HEvent) (tr : TEvent) : List Effect :=
  match tr.recog with
  | none => []
  | some r =>
    if !tr.explicit && tr.kind.changesStatus && r.power && tr.date ≤ r.date then
      let lapseY := lapseOfDecision byHist tr.date
      let neg : Status := if tr.powerKnown then .neg (if tr.kind == .abrogated then .abrogated else .overruled)
                          else .unknown .powerUnknown
      let e1 : Effect :=
        { eff := if tr.powerKnown then .unknown .recognisedLater else .unknown .powerUnknown, start := tr.date,
          lapse := lapseY, scope := tr.scope, conductFrom := temporalConductFrom tr.temporal tr.date,
          rule := .recognised, src := tr.id, actor := some tr.by_ }
      [e1, { e1 with eff := neg, start := r.date, lapse := minOpt lapseY (lapseOfDecision wHist r.date) }]
    else []

/-- Round 5 (DESIGN5 §3.3): the scope of an operative-words row that does not dispose of the case as a whole. Some
issue is reached, unknown which: the target is partly negative, never overruled (`demoted_never_neg`). -/
def demote : Scope → Scope
  | .all => .someIssue
  | .issues ks => .someOf ks
  | s => s

/-- The effect of an explicit supersession by enactment (§7 AB1): known from enactment, reaching conduct from the
retroactive date if any, else from the effective date. -/
def superEffect (s : SEvent) : Option Effect :=
  if s.explicit then
    some { eff := .neg .superseded, start := s.enacted, lapse := none,
           scope := s.scope,
           conductFrom := s.retroactiveTo.getD s.effective, rule := .supersession, src := s.id }
  else none

/-- How the Spec reads a record: events by target. -/
structure EventLookups where
  histOf : Nat → List HEvent
  treatOf : Nat → List TEvent
  supersOf : Nat → List SEvent

/-- Specification lookups: list scans. -/
def recordLookups (r : Record) : EventLookups :=
  { histOf := fun x => r.hist.filter (·.target == x)
    treatOf := fun x => r.treat.filter (·.target == x)
    supersOf := fun x => r.supers.filter (·.target == x) }

/-- A treatment's effects: the effect itself, lapsing when the treating decision does, and, if the treating
decision is reinstated after that lapse, the same effect again from the reinstatement (§5.1 A: "reinstated restores
status"; the overruling it made revives with it) until its next lapse (D4 triage). -/
def treatEffects (byHist : List HEvent) (tr : TEvent) : List Effect :=
  match treatEffect byHist tr with
  | none => []
  | some e =>
    match e.lapse.bind (reinstatedAfter byHist) with
    | some r =>
      let later := byHist.filter (fun h => r ≤ h.date && h.kind != .reinstated)
      e :: ((treatEffect later tr).map (fun e' => { e' with start := r })).toList
    | none => [e]

/-- An en banc grant that vacates the panel opinion under the court's rule (F8) is a vacatur of it: for the lapse of
the overrulings it made (T3), read it as `vacated`. `B` is the overruling decision's court on its date. -/
def vacatingGrants (L : Lookups) (B : Option CourtEpoch) (hist : List HEvent) : List HEvent :=
  hist.map fun h =>
    if h.kind == .rehearingEnBancGranted &&
        B.bind (fun B => L.rules.enBancGrantVacates B.court B.system h.date) == some true
    then { h with kind := .vacated } else h

/-- Tier order for lines of authority (H4): last resort > appellate > BAP, special > appellate division > trial. -/
def _root_.CaseLaw2.Tier.lineRank : Tier → Nat
  | .last => 4 | .appellate => 3 | .bap => 2 | .special => 2 | .appDivTrial => 1 | .trial => 0

/-- The heirs of `x` (H4): the courts that hold it as their own by a binding adoption of its court's decisions up to
a cut-off (*Bonner*, *South Corp.*, *M.A.P.*, successor courts). Persuasive adoptions and notation filters make no
heir. -/
def heirsOf (L : Lookups) (x : Decision) : List Adoption :=
  (adoptionsOf L x).filter fun a =>
    a.force == .binding && a.adopter != x.court && (a.filter == .all || a.filter == .unitB)

/-- The lines a status-changing treatment of `x` by `b` reaches (H4). SCOTUS reaches every line. The original line
is reached by `x`'s own court, a court that replaced it (a succession other than a split), a higher court of its
system, or an adopter once the original court is gone. An heir is reached when it is `b`'s court, when the original
line's overruling came on or before the heir's cut-off (it was adopted as overruled), or when `b`'s court stands
above the heir. -/
def reachOf (L : Lookups) (b x : Decision) : Reach :=
  let hs := heirsOf L x
  if hs.isEmpty then .all
  else match L.epochAt b.court b.date, L.epochAt x.court x.date with
    | some B, some X =>
      if B.scotus then .all
      else
        let orig := b.court == x.court ||
          (L.successorsOf x.court).any (fun s => s.new == b.court && s.kind != .split) ||
          (B.system == X.system && X.tier.lineRank < B.tier.lineRank) ||
          (hs.any (·.adopter == b.court) && (L.epochAt x.court b.date).isNone)
        let hit (a : Adoption) : Bool := a.adopter == b.court || (orig && b.date ≤ a.upTo) ||
          (L.epochAt a.adopter b.date).any (fun A => A.system == B.system && A.tier.lineRank < B.tier.lineRank)
        let reached := (hs.filter hit).map (·.adopter)
        let unreached := (hs.filter (fun a => !hit a)).map (·.adopter)
        if orig && unreached.isEmpty then .all else .lines orig reached unreached
    | _, _ => .all

/-- Decision `c`'s court is in adopter `a`'s line on `c`'s date (H4): it is the adopter, or a court below it (same
system, lower tier; under a federal court of appeals, in its circuit). -/
def inLine (L : Lookups) (c : Decision) (a : Nat) : Bool :=
  match L.epochAt a c.date, L.epochAt c.court c.date with
  | some A, some C =>
    A.court == C.court || (A.system == C.system && C.tier.lineRank < A.tier.lineRank &&
      (!(A.system == 0 && A.tier == .appellate) || C.circuit == A.circuit))
  | _, _ => false

/-- The effects on a cited decision that reach the citing decision `c`'s court (H4). An undated citing decision, or
one whose court is unknown, is reached by every effect (D5: no line is assumed). -/
def effectsFor (L : Lookups) (c : Decision) (effs : List Effect) : List Effect :=
  if c.date == 0 || (L.epochAt c.court c.date).isNone then effs else heirEffects (inLine L c) effs

/-- All effects on decision `x`. -/
def effectsOf (L : Lookups) (E : EventLookups) (dec : Nat → Option Decision) (x : Nat) : List Effect :=
  let X := (dec x).bind (fun d => L.epochAt d.court d.date)
  let hx := E.histOf x
  hx.filterMap (histEffect L X hx) ++
  (E.treatOf x).flatMap (fun tr =>
    let reach := match dec tr.by_, dec x with
      | some b, some xd => reachOf L b xd
      | _, _ => .all
    let byHist := vacatingGrants L ((dec tr.by_).bind (fun d => L.epochAt d.court d.date)) (E.histOf tr.by_)
    -- round 5: a recognised row's effects (none unless `tr.recog` is set); W's history read through W's court
    let wHist := match tr.recog with
      | some r => vacatingGrants L ((dec r.witness).bind (fun d => L.epochAt d.court d.date)) (E.histOf r.witness)
      | none => []
    (treatEffects byHist tr ++ recogEffects byHist wHist tr).map (fun e => { e with reach })) ++
  (E.supersOf x).filterMap superEffect

/-- **Status of issue `k` of decision `x` on question date `t` for conduct date `u`.** -/
def statusOf (L : Lookups) (r : Record) (x k : Nat) (t u : Date) : Status :=
  status (effectsOf L (recordLookups r) r.dec x) k t u

/-- Texas writ/pet. refused on or before `t` promotes `x` (S-TX-3), when the notation is one that promotes (writ era
"writ ref'd", petition era "pet. ref'd", civil only; `HEvent.promotes`). -/
def promotedAt (E : EventLookups) (x : Nat) (t : Date) : Bool :=
  (E.histOf x).any (fun h => h.kind == .writRefused && h.promotes && h.date ≤ t)

/-- The force a status leaves (§8.2 step 1): a cap. -/
def Status.cap : Status → Force
  | .good | .unknown _ => .binding
  | .neg .reviewPending => .persuasive
  | .neg .depublished => .notCitable
  | .neg _ => .none

/-- Soft treatments never change status (§5.2 T1). -/
theorem soft_treatment_no_effect (byHist : List HEvent) (tr : TEvent) (h : tr.kind.changesStatus = false) :
    treatEffect byHist tr = none := by
  simp [treatEffect, h]

/-- Inferred treatments never change status (§9 item 26). -/
theorem inferred_treatment_no_effect (byHist : List HEvent) (tr : TEvent) (h : tr.explicit = false) :
    treatEffect byHist tr = none := by
  simp [treatEffect, h]

/-- **Supersession is prospective** (§7 AB1): conduct before the effective (or retroactive) date keeps the old rule:
the supersession contributes nothing to the status for such conduct. -/
theorem supersession_prospective (s : SEvent) (e : Effect) (he : superEffect s = some e) (l : List Effect)
    (k : Nat) (t u : Date) (hu : u < s.retroactiveTo.getD s.effective) :
    status (e :: l) k t u = status l k t u := by
  unfold superEffect at he
  split at he
  · cases he; exact prospective_no_effect _ l k t u hu
  · cases he

/-- **Partial overruling preserves the other holdings**: an admitted treatment on issues `ks` leaves the status of
every other named issue unchanged. -/
theorem partial_overruling_preserves (byHist : List HEvent) (tr : TEvent) (e : Effect)
    (he : treatEffect byHist tr = some e) (ks : List Nat) (hs : tr.scope = .issues ks) (l : List Effect)
    (k : Nat) (hk : k ∉ ks) (hk0 : k ≠ anonIssue) (t u : Date) :
    status (e :: l) k t u = status l k t u := by
  unfold treatEffect at he
  split at he
  · cases he; exact partial_touches_only _ l k t u ks hs hk hk0
  · cases he

end CaseLaw2.Spec
