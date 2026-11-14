"""Round 5 patch 1: Certificate.lean (modes, recognised checker, operative checker, classes) and Findings.lean."""
import os
LP = r"~\Documents\global-law-lean\lean-proofs\LegalProofs\CaseLaw2"


def rw(p, pairs):
    p = os.path.join(LP, p)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:60], s.count(a))
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="\n").write(s)


rw("Certificate.lean", [
("""inductive Reason where
  | shaUnknown | noWindow | windowHash | quoteMismatch | noCue | disqualified | targetUnresolved | partNotMajority
  | targetLater | noAuthority
  deriving Repr, DecidableEq, Inhabited""",
"""inductive Reason where
  | shaUnknown | noWindow | windowHash | quoteMismatch | noCue | disqualified | targetUnresolved | partNotMajority
  | targetLater | noAuthority
  /-- round 5: an `operativeWords` claim on a row that is not an explicit `disapproved` row -/
  | operativeBadRow
  deriving Repr, DecidableEq, Inhabited

/-- Round 5 (DESIGN5 §2.2, §3.2): how the text checks read a certificate. `plain`: the round-4 checks. `recog`: a
later court's statement that X was overruled by Y (recognition cues and disqualifiers; the names resolve in the
quote itself). `operative`: the court's own operative words other than the terms of art (operative cues, the
round-4 disqualifiers and the operative ones; the target resolves in the quote itself). -/
inductive Mode where
  | plain | recog | operative
  deriving Repr, DecidableEq, Inhabited"""),
("""  citeIndex : Option (Std.HashMap String Nat) := none
  deriving Inhabited

def shaOk""",
"""  citeIndex : Option (Std.HashMap String Nat) := none
  /-- round 5: the text mode (`plain` = round 4) -/
  mode : Mode := .plain
  deriving Inhabited

def shaOk"""),
("""def hasCue (c : Input) : Bool := (cues c.kind).any (hasSub (norm c.quote).toLower)

def disqualified (c : Input) : Bool :=
  let q := (norm c.quote).toLower
  (disqualifiers c.kind).any (fun (a, b) => if b.isEmpty then hasSub q a else hasInOrder q a b)""",
"""/-- The cue phrases the quote is tested against: the kind's (round 4), or the mode's (round 5). -/
def cueList (c : Input) : List String :=
  match c.mode with
  | .plain => cues c.kind
  | .recog => recognisedCues
  | .operative => operativeCues

/-- The disqualifiers the quote is tested against. In `recog` mode a reported history ("overruled by") is the
normal form, so only the recognition disqualifiers apply. -/
def disqList (c : Input) : List (String × String) :=
  match c.mode with
  | .plain => disqualifiers c.kind
  | .recog => recognisedDisqualifiers.map (·, "")
  | .operative => disqualifiers c.kind ++ operativeDisqualifiers.map (·, "")

def hasCue (c : Input) : Bool := (cueList c).any (hasSub (norm c.quote).toLower)

def disqualified (c : Input) : Bool :=
  let q := (norm c.quote).toLower
  (disqList c).any (fun (a, b) => if b.isEmpty then hasSub q a else hasInOrder q a b)"""),
("""  let ctx := (norm c.quote) ++ " " ++ " ".intercalate ((c.windows.filter (usable c)).map fun w => norm w.text)
  if c.selfText then true""",
"""  -- round 5: in `recog` and `operative` mode the name must be in the quote itself
  let ctx := if c.mode == .plain then
      (norm c.quote) ++ " " ++ " ".intercalate ((c.windows.filter (usable c)).map fun w => norm w.text)
    else norm c.quote
  if c.selfText then true"""),
("""  /-- W's court is X's court, or has power to overrule X -/
  standing : Bool
  deriving Inhabited""",
"""  /-- W's court is X's court, or has power to overrule X -/
  standing : Bool
  /-- round 5: the row claims the `recognised` class (`treatment_class.tsv`) -/
  claim : Bool := false
  /-- round 5: W's court has power to overrule X (not mere standing) -/
  power : Bool := false
  /-- round 5: date(X), date(Y) and date(W) are all known -/
  datesKnown : Bool := false
  deriving Inhabited"""),
("""

end CaseLaw2.Cert""",
"""
/-! ## Round 5: recognised overrulings, operative words, classes (DESIGN5.md)

A witness row may claim the `recognised` class: W, a decision of a court that itself has **power** to overrule X,
says in a majority sentence that X was overruled by Y. The claim is checked on top of the round-4 witness checks,
read in `recog` mode (a recognition cue, no recognition disqualifier, X and Y both named in the quote itself), with
W's power and known dates. A claim that fails leaves the row exactly where round 4 put it. -/

/-- The verdict on a witness row in round 5. -/
inductive RResult where
  /-- recognised; `unverifiedBy`: Y's power over X is unknown (the effect is then `unknown powerUnknown`) -/
  | recognised (unverifiedBy : Bool)
  /-- not recognised: the round-4 witness verdict -/
  | witness (r : WResult)
  deriving Repr, DecidableEq, Inhabited

def RResult.toString : RResult → String
  | .recognised false => "okRecognised"
  | .recognised true => "okRecognisedUnverifiedBy"
  | .witness r => r.toString

def RResult.admitted : RResult → Bool
  | .recognised _ => true
  | .witness r => r.admitted

def RResult.isRecognised : RResult → Bool
  | .recognised _ => true
  | .witness _ => false

/-- The evidence naming Y is not the evidence naming X. -/
def distinctEvidence (c : Input) (w : Witness) : Bool :=
  compact (c.evidence.drop 5).toString != compact (w.byEvidence.drop 5).toString

/-- **The recognised checker** (DESIGN5 §2.2). `c` is the row's certificate input in `plain` mode. -/
def checkRecognised (c : Input) (w : Witness) : RResult :=
  if !(w.claim && w.power && w.datesKnown && distinctEvidence c w) then .witness (checkWitness c w)
  else match checkWitness { c with mode := .recog } w with
    | .ok => .recognised false
    | .okUnverifiedBy => .recognised true
    | _ => .witness (checkWitness c w)

/-- **Recognition soundness**: a recognised row made the claim; W has power over X; the three dates are known; the
two names differ; and the row passes every witness check read in `recog` mode: it is `explicit = 0` with a
status-changing kind, W's text passes the text checks (recognition cue, no recognition disqualifier, X named in the
quote, majority part), Y is named in the quote, the dates are ordered X ≤ Y ≤ W, and W has standing. -/
theorem checkRecognised_sound (c : Input) (w : Witness) (h : (checkRecognised c w).isRecognised = true) :
    w.claim = true ∧ w.power = true ∧ w.datesKnown = true ∧ distinctEvidence c w = true ∧
      w.known = true ∧ w.explicit = false ∧ w.changes = true ∧
      (textCheck { c with mode := .recog }).admitted = true ∧ byResolves { c with mode := .recog } w = true ∧
      c.ordered = true ∧ w.witnessOrdered = true ∧ w.standing = true := by
  unfold checkRecognised at h
  by_cases h0 : (w.claim && w.power && w.datesKnown && distinctEvidence c w) = true
  · simp only [h0, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
    have h0' := h0
    simp only [Bool.and_eq_true] at h0'
    obtain ⟨⟨⟨hc, hp⟩, hd⟩, he⟩ := h0'
    have ha : (checkWitness { c with mode := .recog } w).admitted = true := by
      cases hw : checkWitness { c with mode := .recog } w <;> simp_all [RResult.isRecognised, WResult.admitted]
    exact ⟨hc, hp, hd, he, checkWitness_sound _ w ha⟩
  · simp [h0, RResult.isRecognised] at h

/-- **Never without W's power**: a witness row whose W lacks power over X is never recognised. -/
theorem checkRecognised_needs_power (c : Input) (w : Witness) (h : w.power = false) :
    (checkRecognised c w).isRecognised = false := by
  cases hr : (checkRecognised c w).isRecognised with
  | false => rfl
  | true => have := (checkRecognised_sound c w hr).2.1; simp [h] at this

/-- **Fallback**: a row that is not recognised has exactly its round-4 witness verdict. -/
theorem checkRecognised_fallback (c : Input) (w : Witness) (h : (checkRecognised c w).isRecognised = false) :
    checkRecognised c w = .witness (checkWitness c w) := by
  unfold checkRecognised at h ⊢
  by_cases h0 : (w.claim && w.power && w.datesKnown && distinctEvidence c w) = true
  · simp only [h0, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h ⊢
    cases hw : checkWitness { c with mode := .recog } w <;> simp_all [RResult.isRecognised]
  · simp [h0]

/-- **No claim, no change**: without a `recognised` claim the verdict is the round-4 witness verdict. -/
theorem checkRecognised_no_claim (c : Input) (w : Witness) (h : w.claim = false) :
    checkRecognised c w = .witness (checkWitness c w) := by
  simp [checkRecognised, h]

/-- The quote disposes of the case as a whole (DESIGN5 §3.3): it contains a whole-case phrase. -/
def wholeCase (quote : String) : Bool := operativeWhole.any (hasSub (norm quote).toLower)

/-- **The operative-words checker** (DESIGN5 §3.2): an explicit `disapproved` row, checked in `operative` mode. A
failed claim is not admitted (the plain check is not tried). -/
def checkOperative (c : Input) (explicit : Bool) : Result :=
  if !(c.kind == .treat .disapproved && explicit) then .fail .operativeBadRow
  else check { c with mode := .operative }

/-- **Operative-words soundness**: an admitted operative-words row is an explicit `disapproved` row whose quote has
an operative cue and none of the round-4 or operative disqualifiers, names the target in the quote itself, and
passes every other check of `check`. -/
theorem checkOperative_sound (c : Input) (explicit : Bool) (h : (checkOperative c explicit).admitted = true) :
    c.kind = .treat .disapproved ∧ explicit = true ∧ (check { c with mode := .operative }).admitted = true ∧
      hasCue { c with mode := .operative } = true ∧ disqualified { c with mode := .operative } = false ∧
      resolves { c with mode := .operative } = true := by
  unfold checkOperative at h
  by_cases h0 : (c.kind == .treat .disapproved && explicit) = true
  · simp only [h0, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
    have h0' := h0
    simp only [Bool.and_eq_true, beq_iff_eq] at h0'
    have hs := checkCert_sound _ h
    exact ⟨h0'.1, h0'.2, h, hs.2.2.1, hs.2.2.2.1, hs.2.2.2.2.1⟩
  · simp [h0, Result.admitted] at h

/-- The four classes of a status-changing treatments row (DESIGN5 §5), least first. -/
inductive OClass where
  | selfAnnounced | operativeWords | recognised | atRiskWitness
  deriving Repr, DecidableEq, Inhabited

def OClass.idx : OClass → Nat
  | .selfAnnounced => 0 | .operativeWords => 1 | .recognised => 2 | .atRiskWitness => 3

def OClass.toString : OClass → String
  | .selfAnnounced => "selfAnnounced" | .operativeWords => "operativeWords" | .recognised => "recognised"
  | .atRiskWitness => "atRiskWitness"

/-- The quote uses a term of art (overrule, disapprove, recede, abrogate). -/
def selfAnnounced (quote : String) : Bool := selfAnnouncedCues.any (hasSub (norm quote).toLower)

/-- **The class of a row**: recognised (the recognised check passed); otherwise at-risk witness when the row is
not explicit; otherwise by the words of the certified quote. -/
def classOf (explicit recognised : Bool) (quote : String) : OClass :=
  if recognised then .recognised
  else if !explicit then .atRiskWitness
  else if selfAnnounced quote then .selfAnnounced else .operativeWords

/-- A row is classed `recognised` exactly when the recognised check passed. -/
theorem classOf_recognised_iff (explicit recognised : Bool) (quote : String) :
    classOf explicit recognised quote = .recognised ↔ recognised = true := by
  unfold classOf
  cases recognised <;> cases explicit <;> simp <;> split <;> simp

end CaseLaw2.Cert"""),
])

rw("Spec/Findings.lean", [
("""def citesVacated (c : CiteFacts) : Bool := c.status == .neg .vacated || c.status == .neg .reversed""",
"""/-- Round 5 (DESIGN5 §2.5): the cited decision's status on the citing date is `unknown recognisedLater`: the
citation falls between an overruling that was not announced and its recognition by a later court with power.
Reported as `atRisk … recognisedLater`, never as `citesOverruled`. -/
def citedRecognisedLater (c : CiteFacts) : Bool := c.status == .unknown .recognisedLater

def citesVacated (c : CiteFacts) : Bool := c.status == .neg .vacated || c.status == .neg .reversed"""),
("""/-- A panel departure is only reported when the power check failed for want of an en banc bench. -/""",
"""/-- **Between the overruling and its recognition a citation is at risk, not "cites overruled"** (round 5): a
citation whose cited status is `unknown recognisedLater` is never reported as citing an overruled, vacated or
withdrawn decision. -/
theorem recognisedLater_not_citesOverruled (c : CiteFacts) (h : citedRecognisedLater c = true) :
    citesOverruled c = false ∧ citesVacated c = false ∧ citesWithdrawn c = false := by
  simp only [citedRecognisedLater, beq_iff_eq] at h
  simp [citesOverruled, citesVacated, citesWithdrawn, h]

/-- A panel departure is only reported when the power check failed for want of an en banc bench. -/"""),
])
print("patched")
