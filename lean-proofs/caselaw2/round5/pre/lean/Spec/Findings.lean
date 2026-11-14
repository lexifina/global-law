import LegalProofs.CaseLaw2.Spec.Status

/-!
# Spec: findings (doctrine §9 item 27; prior_art §7.1 item 7)

Each finding is a decidable predicate over what the Spec computes for one citation (citing decision `i`, cited `j`)
or one treatment row. None is an error claim: they are counts of conditions a reader of the citing opinion would want
flagged. The runner evaluates them over all 48M citation edges.

* `citesOverruled` (issue-aware: the cited issue's status), `citesVacated`, `citesWithdrawn`, `citesNotCitable`;
* `citesUnpublishedAsBinding`: `i` *follows* an unpublished `j` that does not bind it;
* `appliesSupersededHolding`: two-date: the cited holding was superseded for conduct on the conduct date, and the
  citing decision decides that holding's question (hunt H2); with no conduct date it is never reported, and
  `supersededConductUnknown` (an `atRisk` family) is reported instead;
* `panelDepartsWithoutEnBanc`: a panel (a known panel or division) claims to overrule its own court's precedent
  under a strong rule the court had on both dates (hunt H3b);
* `pluralityTreatedAsBinding`: `i` follows a plurality holding with no *Marks* row;
* `ignoresBindingInUnit` (§9 item 27, "a trial court departs from its own unit, ownUnit rules"): a trial-level state
  court `i` declines to follow (or claims to overrule) a good-law precedent that binds it through its own unit (an
  intermediate court of its unit under an ownUnit trial-scope rule, `VownUnit`; its own appellate division,
  `appDivBinds`), with no power to change it (a panel's departure from its own court is `panelDepartsWithoutEnBanc`);
* `atRisk`: computed, never extracted: an inferred rejection by a court with power, an inferred supersession, or the
  holding cites a decision that a court binding it has since negated; and (§5.2 T1, T2, F14) a soft negative
  treatment (`soft`), a status-changing treatment by a court without power (`claim`, T2), or a later contrary holding
  of a court whose decisions bind the holder (`contraryBinding`, an abrogation candidate, T1(c)).
-/

namespace CaseLaw2.Spec
open CaseLaw2

/-- What the Spec says about one citation. -/
structure CiteFacts where
  /-- status of the cited issue on the citing date, for conduct on the citing date -/
  status : Status
  /-- status for the conduct date (two-date queries); `none`: the conduct date is unknown. SCHEMA carries no
  conduct date for a citing decision, and its own date is not one (hunt H2: 0 of 20 such findings were right) -/
  statusAtConduct : Option Status
  /-- holding-level match (H2): the citing decision decides the cited holding's issue, or an issue on the block of
  the US Code that the superseding law rewrote -/
  holdingMatch : Bool
  /-- the negative effect's source decision binds the citing court -/
  negByBinding : Bool
  /-- the cited decision's publication -/
  pub : Option Publication
  /-- force on the citing court, with its path -/
  force : Option (Force × List RuleId)
  /-- the citing decision has an admitted `followed` treatment of the cited one -/
  followed : Bool
  /-- the cited holding is a plurality holding with no Marks row -/
  pluralityNoMarks : Bool
  deriving Repr, Inhabited

/-- The cited issue is overruled or abrogated on the citing date. Status is not relative to the citing court (§5.1B,
T1: an overruling by a court with power over the target ends its force everywhere), so no binding condition is added
(D4 triage, DIFFTEST.md: v1's "the overruling binds the citing court" condition dropped). -/
def citesOverruled (c : CiteFacts) : Bool :=
  c.status == .neg .overruled || c.status == .neg .abrogated

def citesVacated (c : CiteFacts) : Bool := c.status == .neg .vacated || c.status == .neg .reversed

def citesWithdrawn (c : CiteFacts) : Bool := c.status == .neg .withdrawn

def citesNotCitable (c : CiteFacts) : Bool :=
  c.status == .neg .depublished || (c.force.map (·.1) == some .notCitable)

def citesUnpublishedAsBinding (c : CiteFacts) : Bool :=
  c.followed && (c.pub != some .published && c.pub.isSome) &&
    (match c.force with | some (f, _) => f.rank < Force.bindingAbsentConflict.rank | none => false)

def appliesSupersededHolding (c : CiteFacts) : Bool :=
  c.holdingMatch && c.statusAtConduct == some (.neg .superseded)

/-- `atRisk supersededConductUnknown` (H2): the citing decision decides a holding that a statute superseded, the
supersession is in force for the latest conduct the decision could concern (its own date), and the conduct date is
not known. Low confidence: conduct before the statute's date keeps the old rule (`supersession_prospective`). -/
def supersededConductUnknown (c : CiteFacts) : Bool :=
  c.holdingMatch && c.statusAtConduct.isNone && c.status == .neg .superseded

def pluralityTreatedAsBinding (c : CiteFacts) : Bool := c.followed && c.pluralityNoMarks

/-- What the Spec says about one treatment row by `i` of `j` (admitted or not). -/
structure TreatFacts where
  kind : TKind
  /-- `canChangeStatus i j` -/
  power : Option (Bool × RuleId)
  /-- the treating decision's bench is known to be a panel or a division (H3b: an unknown bench, or an opinion
  circulated to the full court, is not shown to be a panel departure) -/
  panel : Bool
  /-- the treating court had a strong (or within-unit) horizontal rule on the treating date too (H3b: the rule is
  dated; a court is not charged with a rule it did not yet have) -/
  ruleAtDeparture : Bool
  /-- force of `j` on `i`'s court, with its path -/
  force : Option (Force × List RuleId)
  /-- status of `j` on `i`'s date -/
  status : Status
  deriving Repr, Inhabited

def panelDepartsWithoutEnBanc (f : TreatFacts) : Bool :=
  f.kind.changesStatus && f.panel && f.ruleAtDeparture &&
    (match f.power with
     | some (false, r) => r == .strongNeedsEnBanc || r == .withinUnitEnBanc || r == .adoptedEnBanc
     | _ => false)

def ignoresBindingInUnit (f : TreatFacts) : Bool :=
  (f.kind == .declinedToFollow || f.kind.changesStatus) && f.status == .good &&
    (f.power.map (·.1) == some false) &&
    (match f.force with
     | some (.binding, p) => p.contains .VownUnit || p.contains .appDivBinds
     | _ => false)

/-- `atRisk` for one holding. -/
structure RiskFacts where
  /-- an inferred (explicit = 0) status-changing treatment by a court with power -/
  inferredRejection : Bool
  /-- an inferred supersession row (explicit = 0) -/
  inferredSupersession : Bool
  /-- the decision cites a decision negated after it by a court that binds it -/
  citesLaterNegated : Bool
  deriving Repr, Inhabited

def atRisk (r : RiskFacts) : Bool := r.inferredRejection || r.inferredSupersession || r.citesLaterNegated

/-- The negative treatments that never change status (T1: limited, questioned, criticized; and declining to follow,
which by a court without power is a claim at most, T2). `distinguished` and `followed` are not negative. -/
def _root_.CaseLaw2.TKind.softNegative : TKind → Bool
  | .limited | .questioned | .criticized | .declinedToFollow => true
  | _ => false

/-- What the Spec says about one admitted treatment row for the treatment-level `atRisk` families. -/
structure TreatRisk where
  kind : TKind
  /-- power of the treating decision over the target on every domain the issue could have (`none` = unknown) -/
  power : Option Bool
  /-- the target is wholly negative on the treating date (a partial event leaves the rest at risk) -/
  targetNeg : Bool
  deriving Repr, Inhabited

/-- `atRisk soft`: a soft negative treatment of a target that is not already wholly negative. -/
def softRisk (r : TreatRisk) : Bool := r.kind.softNegative && !r.targetNeg

/-- `atRisk claim` (T2): a status-changing treatment by a court shown to lack power: a claim, not a status change. -/
def claimRisk (r : TreatRisk) : Bool := r.kind.changesStatus && r.power == some false && !r.targetNeg

/-- What the Spec says about a holding `x` and a later holding `y` on the same issue (F14, T1(c)). -/
structure ContraryFacts where
  /-- the answers differ -/
  opposite : Bool
  /-- `y` is later than `x` -/
  later : Bool
  /-- `y`'s holding binds `x`'s court (and unit) on `y`'s date -/
  binds : Bool
  /-- `x`'s holding is good law on `y`'s date -/
  holderGood : Bool
  /-- `y`'s holding is good law on its own date -/
  contraryGood : Bool
  deriving Repr, Inhabited

/-- `atRisk contraryBinding`: a later, good-law, contrary holding that binds the holder's court: an abrogation
candidate (T1(c)), never a status change by itself (§9 item 26). -/
def contraryBinding (f : ContraryFacts) : Bool :=
  f.opposite && f.later && f.binds && f.holderGood && f.contraryGood

/-- A claim is only reported when the treating court is shown to lack power (T2). -/
theorem claimRisk_needs_no_power (r : TreatRisk) (h : claimRisk r = true) :
    r.power = some false ∧ r.kind.changesStatus = true := by
  simp only [claimRisk, Bool.and_eq_true, beq_iff_eq] at h
  exact ⟨h.1.2, h.1.1⟩

/-- Soft and claim risks never coincide: a soft kind never changes status. -/
theorem soft_claim_disjoint (r : TreatRisk) : !(softRisk r && claimRisk r) = true := by
  cases hk : r.kind <;> simp [softRisk, claimRisk, TKind.softNegative, TKind.changesStatus, hk]

/-- A contrary-binding risk needs a later holding that binds the holder's court and is good law. -/
theorem contraryBinding_needs_binding (f : ContraryFacts) (h : contraryBinding f = true) :
    f.binds = true ∧ f.later = true ∧ f.contraryGood = true := by
  simp only [contraryBinding, Bool.and_eq_true] at h
  exact ⟨h.1.1.2, h.1.1.1.2, h.2⟩

/-- Hunt H2: a superseded-holding finding needs a known conduct date that the supersession reaches, and a
holding-level match; the citing date alone never gives it. -/
theorem appliesSuperseded_needs_conduct (c : CiteFacts) (h : appliesSupersededHolding c = true) :
    c.statusAtConduct = some (.neg .superseded) ∧ c.holdingMatch = true := by
  simp only [appliesSupersededHolding, Bool.and_eq_true, beq_iff_eq] at h
  exact ⟨h.2, h.1⟩

/-- With an unknown conduct date the finding is never made; the low-confidence family is disjoint from it. -/
theorem conductUnknown_not_finding (c : CiteFacts) (h : c.statusAtConduct = none) :
    appliesSupersededHolding c = false := by
  simp [appliesSupersededHolding, h]

/-- Hunt H3b: a panel departure is reported only for a known panel under a rule the court had when it departed. -/
theorem panelDeparts_needs_panel_and_rule (f : TreatFacts) (h : panelDepartsWithoutEnBanc f = true) :
    f.panel = true ∧ f.ruleAtDeparture = true := by
  simp only [panelDepartsWithoutEnBanc, Bool.and_eq_true] at h
  exact ⟨h.1.1.2, h.1.2⟩

/-- A cited holding that is good law is never reported as overruled, vacated or withdrawn. -/
theorem good_cites_clean (c : CiteFacts) (h : c.status = .good) :
    citesOverruled c = false ∧ citesVacated c = false ∧ citesWithdrawn c = false := by
  simp [citesOverruled, citesVacated, citesWithdrawn, h]

/-- A panel departure is only reported when the power check failed for want of an en banc bench. -/
theorem panelDeparts_needs_enBanc (f : TreatFacts) (h : panelDepartsWithoutEnBanc f = true) :
    ∃ r, f.power = some (false, r) ∧ (r = .strongNeedsEnBanc ∨ r = .withinUnitEnBanc ∨ r = .adoptedEnBanc) := by
  unfold panelDepartsWithoutEnBanc at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨_, hp⟩ := h
  cases hpw : f.power with
  | none => simp [hpw] at hp
  | some pr =>
    obtain ⟨b, r⟩ := pr
    cases b
    · simp only [hpw] at hp
      refine ⟨r, rfl, ?_⟩
      simp only [Bool.or_eq_true, beq_iff_eq] at hp
      rcases hp with (h | h) | h <;> simp [h]
    · simp [hpw] at hp

end CaseLaw2.Spec
