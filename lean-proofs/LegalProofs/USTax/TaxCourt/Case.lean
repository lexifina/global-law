import LegalProofs.USTax.TaxCourt.Return
import Lean.Data.Json

/-!
# Encoding a Tax Court case

A `Case` is a citation, a tax year and the court's findings:
* `facts` — the return as the court finds it should have been (income, ages, the people claimed, ...);
* `status` — findings on marital status and the household, when filing status is in issue: the corrected return then
  uses the status `determineStatus` allows, starting from the one in `facts.filing` (the one claimed);
* `asFiled` (the return as filed, recomputed) or `taxShown` (the tax shown, net of refundable credits) — for the
  deficiency and the penalties;
* `sfrTax` — the tax on a substitute for return (§6020(b)), net of refundable credits: §6651(g) treats it as the
  return filed by the taxpayer for §6651(a)(2) (and so for the §6651(c)(1) offset), so when present the additions use it
  as the tax shown, while the deficiency still uses `taxShown` / `asFiled` (0 for a non-filer);
* `tieBreakers` — competing claimants for a child (§152(c)(4)); a child lost to someone else is dropped from
  `facts.dependents` automatically (matched by name);
* `accuracy` — §6662 findings; `lateness` — §6651 findings;
* `expected` — the figures and holdings stated in the opinion, which `decideCase` compares with its own.

`decideCase` returns, for each issue, the outcome and the reasons, and a list of checks against `expected`.

Every field has a default, and the JSON reader fills in missing fields with defaults (`FromJson` instances below), so
an encoding gives only what the opinion finds. Dates are "YYYY-MM-DD" strings.
-/

namespace Legal.USTax.TaxCourt
open Lean

structure TieBreakIssue where
  child : String := ""
  /-- The name, in `claimants`, of the taxpayer before the court. -/
  taxpayer : String := ""
  claimants : List Claimant := []
  deriving Repr, Inhabited

/-- A figure or holding stated in the opinion. `item` is one of the keys listed in `Outcome.values`. -/
structure Expectation where
  item : String := ""
  value : Option Int := none
  flag : Option Bool := none
  text : Option String := none
  note : String := ""
  deriving Repr, Inhabited

/-- §6654 findings (`Extra.estimatedTaxAddition`); the current-year tax and withholding default to the corrected
return's net tax and withholding. -/
structure EstimatedPayment where
  date : Date := ⟨2000, 1, 1⟩
  amount : Int := 0
  deriving Repr, Inhabited

structure EstimatedIssue where
  currentTax : Option Int := none
  withholding : Option Int := none
  priorTax : Option Int := none
  priorAGI : Int := 0
  priorNoLiability : Bool := false
  payments : List EstimatedPayment := []
  dueDates : Option (List Date) := none
  requiredInstallments : Option (List Int) := none
  deriving Repr, Inhabited

structure Case where
  citation : String := ""
  taxYear : Nat := 0
  note : String := ""
  facts : ReturnFacts := {}
  status : Option StatusFacts := none
  asFiled : Option ReturnFacts := none
  taxShown : Option Int := none
  /-- §6651(g): the tax on the substitute for return, used as the tax shown for §6651(a)(1)–(2), (c)(1). -/
  sfrTax : Option Int := none
  tieBreakers : List TieBreakIssue := []
  accuracy : Option AccuracyFacts := none
  lateness : Option LateFacts := none
  /-- §6654 addition for failure to pay estimated tax. -/
  estimated : Option EstimatedIssue := none
  expected : List Expectation := []
  deriving Repr, Inhabited

/-! ## Outcomes -/

structure DependentOutcome where
  name : String
  qualifyingChild : Bool
  qualifyingChildFailures : List String
  qualifyingRelative : Bool
  qualifyingRelativeFailures : List String
  dependent : Bool
  ctcChild : Bool
  eicChild : Bool
  hohQualifyingPerson : Bool
  deriving Repr, Inhabited

structure Check where
  item : String
  expected : String
  computed : String
  ok : Bool
  deriving Repr, Inhabited

structure Outcome where
  citation : String
  taxYear : Nat
  errors : List String := []
  filingStatusClaimed : Option Filing := none
  filingStatus : Option Filing := none
  allowedStatuses : List Filing := []
  tieBreakers : List (String × Option String) := []
  dependents : List DependentOutcome := []
  corrected : Option ReturnResult := none
  asFiled : Option ReturnResult := none
  taxShown : Option Int := none
  deficiency : Option Int := none
  earlyDistributions : List EarlyDistResult := []
  accuracy : Option AccuracyOutcome := none
  lateness : Option LateOutcome := none
  estimated : Option Extra.EstOutcome := none
  checks : List Check := []
  /-- §25A: each student's AOTC eligibility. -/
  students : List (String × Bool) := []
  /-- All checks passed. -/
  agrees : Bool := true
  deriving Repr, Inhabited

/-- The figures an `Expectation` can name. -/
def Outcome.intValues (o : Outcome) : List (String × Int) :=
  (match o.corrected with
   | some r => [("agi", r.agi), ("taxableIncome", r.taxableIncome), ("regularTax", r.regularTax),
       ("standardDeduction", r.standardDeduction), ("exemptions", r.exemptions), ("deduction", r.deduction),
       ("taxableSocialSecurity", r.taxableSocialSecurity), ("seTax", r.seTax),
       ("earlyDistributionTax", r.earlyDistributionTax), ("eic", r.eic), ("ctcNonrefundable", r.ctcNonrefundable),
       ("refundableCtc", r.refundableCtc), ("totalTax", r.totalTax), ("netTax", r.netTax),
       ("earnedIncome", r.earnedIncome), ("dependentsCounted", r.dependentsCounted),
       ("excessAdvanceCtc", r.excessAdvanceCtc), ("adjustments", r.adjustments), ("halfSeTax", r.halfSeTax),
       ("totalIncome", r.totalIncome), ("refundableCredits", r.refundableCredits),
       ("nonrefundableCredits", r.nonrefundableCredits), ("iraDeduction", r.iraDeduction),
       ("rolloverIncludible", r.rolloverIncludible), ("hsaIncludible", r.hsaIncludible),
       ("hsaAdditionalTax", r.hsaAdditionalTax), ("gamblingLossDeduction", r.gamblingLossDeduction),
       ("educationNonrefundable", r.educationNonrefundable), ("aotcRefundable", r.aotcRefundable),
       ("educationCredits", r.educationNonrefundable + r.aotcRefundable), ("itemizedDeductions",
         if r.deduction == r.standardDeduction then 0 else r.deduction)]
   | none => []) ++
  (match o.asFiled with
   | some r => [("asFiled.agi", r.agi), ("asFiled.taxableIncome", r.taxableIncome), ("asFiled.tax", r.regularTax),
       ("asFiled.regularTax", r.regularTax), ("asFiled.totalTax", r.totalTax), ("asFiled.netTax", r.netTax),
       ("asFiled.adjustments", r.adjustments), ("asFiled.eic", r.eic)]
   | none => []) ++
  (match o.taxShown with | some t => [("taxShown", t)] | none => []) ++
  (match o.deficiency with | some d => [("deficiency", d)] | none => []) ++
  (match o.accuracy with | some a => [("accuracyPenalty", a.penalty), ("understatement", a.understatement)] | none => []) ++
  (match o.lateness with | some l => [("failureToFile", l.failureToFile), ("failureToPay", l.failureToPay)] | none => []) ++
  (match o.estimated with
   | some e => [("estimatedTaxAddition", e.addition), ("estimatedRequiredAnnual", e.requiredAnnual)]
   | none => []) ++
  (match o.corrected with
   | some r => [("alimonyIncluded", r.alimonyIncluded), ("alimonyDeduction", r.alimonyDeduction),
       ("lapseIncome", r.lapseIncome)] ++
       (match r.ptc with
        | some x => [("householdIncome", x.householdIncome), ("povertyLine", x.povertyLine),
            ("fplPercent", x.fplPercent), ("premiumTaxCredit", x.credit),
            ("excessAdvancePtc", x.excessAdvanceRepayment), ("netPremiumTaxCredit", x.netCredit),
            ("ptcContribution", x.contribution)]
        | none => [])
   | none => [])

def Outcome.flagValues (o : Outcome) : List (String × Bool) :=
  (match o.corrected with | some r => [("lumpSumElection", r.lumpSumElection)] | none => []) ++
  o.students.map (fun (n, b) => ("aotcEligible:" ++ n, b)) ++
  (match o.accuracy with
   | some a => [("substantialUnderstatement", a.substantial), ("accuracyPenaltyApplies", a.applies)]
   | none => []) ++
  (match o.filingStatus with
   | some f => [("headOfHousehold", f == .hoh), ("survivingSpouse", f == .qss)]
   | none => []) ++
  o.dependents.flatMap fun d =>
    [("qualifyingChild:" ++ d.name, d.qualifyingChild), ("qualifyingRelative:" ++ d.name, d.qualifyingRelative),
     ("dependent:" ++ d.name, d.dependent), ("ctcChild:" ++ d.name, d.ctcChild), ("eicChild:" ++ d.name, d.eicChild),
     ("hohQualifyingPerson:" ++ d.name, d.hohQualifyingPerson)]

def filingName : Filing → String
  | .single => "single" | .mfj => "mfj" | .mfs => "mfs" | .hoh => "hoh" | .qss => "qss"

def Outcome.textValues (o : Outcome) : List (String × String) :=
  (match o.filingStatus with | some f => [("filingStatus", filingName f)] | none => []) ++
  o.tieBreakers.map fun (c, w) => ("tieBreaker:" ++ c, w.getD "none")

def runCheck (o : Outcome) (e : Expectation) : Check :=
  match e.value, e.flag, e.text with
  | some v, _, _ => match o.intValues.lookup e.item with
    | some c => ⟨e.item, toString v, toString c, c == v⟩
    | none => ⟨e.item, toString v, "(not computed)", false⟩
  | none, some b, _ => match o.flagValues.lookup e.item with
    | some c => ⟨e.item, toString b, toString c, c == b⟩
    | none => ⟨e.item, toString b, "(not computed)", false⟩
  | none, none, some t => match o.textValues.lookup e.item with
    | some c => ⟨e.item, t, c, c == t⟩
    | none => ⟨e.item, t, "(not computed)", false⟩
  | none, none, none => ⟨e.item, "(nothing expected)", "", false⟩

/-! ## Deciding a case -/

/-- **Decide the encoded issues.** -/
def decideCase (c : Case) : Outcome :=
  match params? c.taxYear with
  | none => { citation := c.citation, taxYear := c.taxYear, errors := [s!"tax year {c.taxYear} is outside 2012–2024"],
              agrees := false }
  | some p =>
    let winners := c.tieBreakers.map fun t =>
      (t.child, t.taxpayer, (tieBreak (t.claimants.filter (·.qualifies))).map (·.name))
    let lost := (winners.filter fun (_, me, w) => w != some me).map (·.1)
    let deps := c.facts.dependents.map fun x => if lost.contains x.name then { x with lostTieBreaker := true } else x
    let claimed := c.facts.filing
    let st := c.status.getD { canBeClaimedAsDependent := c.facts.canBeClaimedAsDependent }
    let status := match c.status with
      | some s => determineStatus p claimed s deps
      | none => claimed
    let allowed := match c.status with
      | some s => allowedStatuses p s deps
      | none => []
    let facts := { c.facts with dependents := deps, filing := status }
    let corrected := computeReturn p facts
    let shown := c.asFiled.map (computeReturn p)
    let shownNet := match c.taxShown with
      | some t => some t
      | none => shown.map (·.netTax)
    let someone65 := facts.taxpayerAge ≥ 65 || ((status == .mfj || status == .mfs) && facts.spouseAge ≥ 65)
    let depOut := deps.map fun x =>
      { name := x.name, qualifyingChild := qualifyingChild p.year x,
        qualifyingChildFailures := qualifyingChildFailures p.year x,
        qualifyingRelative := qualifyingRelative p x, qualifyingRelativeFailures := qualifyingRelativeFailures p x,
        dependent := isDependent p facts.canBeClaimedAsDependent x,
        ctcChild := ctcQualifyingChild p facts.canBeClaimedAsDependent x &&
          (if p.ctc.ssnForChild then x.hasSSN else x.hasTIN),
        eicChild := eicQualifyingChild p x && x.hasSSN,
        hohQualifyingPerson := hohQualifyingPerson p st x : DependentOutcome }
    let acc := c.accuracy.map fun a => accuracyPenalty p corrected.netTax (shownNet.getD 0) a
    -- §6651(g): a substitute for return is the return for (a)(2); its tax is the tax shown for the additions
    let late := c.lateness.map fun l =>
      lateAdditions p corrected.netTax (c.sfrTax.getD (shownNet.getD corrected.netTax))
        { l with timelyPayments := l.timelyPayments + corrected.payments }
    let o : Outcome :=
      { citation := c.citation, taxYear := c.taxYear,
        errors := (if c.accuracy.isSome && shownNet.isNone then ["§6662 needs asFiled or taxShown"] else []),
        filingStatusClaimed := some claimed, filingStatus := some status, allowedStatuses := allowed,
        tieBreakers := winners.map fun (ch, _, w) => (ch, w),
        dependents := depOut, corrected := some corrected, asFiled := shown, taxShown := shownNet,
        deficiency := shownNet.map (deficiencyOf corrected),
        earlyDistributions := facts.earlyDistributions.map (earlyDistTax p corrected.agi someone65),
        accuracy := acc, lateness := late,
        estimated := c.estimated.map fun e => Extra.estimatedTaxAddition
          { year := c.taxYear, currentTax := e.currentTax.getD corrected.netTax,
            withholding := e.withholding.getD facts.withholding, priorTax := e.priorTax, priorAGI := e.priorAGI,
            mfs := status == .mfs, priorNoLiability := e.priorNoLiability,
            payments := e.payments.map fun x => (x.date, x.amount), dueDates := e.dueDates,
            requiredOverride := e.requiredInstallments },
        students := facts.students.map fun s => (s.name, aotcEligible s) }
    let checks := c.expected.map (runCheck o)
    { o with checks := checks, agrees := checks.all (·.ok) && o.errors.isEmpty }

/-! ## JSON: every input field is optional (defaults filled in) -/

/-- Read a value, filling in the fields the JSON object leaves out from `default`. -/
def fromJsonWithDefaults {α : Type} [Inhabited α] [ToJson α] (parse : Json → Except String α) (j : Json) :
    Except String α :=
  match j with
  | .obj _ => parse (Json.mergeObj (toJson (default : α)) j)
  | _ => parse j

instance : ToJson Date where
  toJson d := Json.str s!"{d.y}-{if d.m < 10 then "0" else ""}{d.m}-{if d.d < 10 then "0" else ""}{d.d}"
instance : FromJson Date where
  fromJson? j := do
    let s ← j.getStr?
    match s.splitOn "-" with
    | [y, m, d] => match y.toInt?, m.toInt?, d.toInt? with
      | some y, some m, some d => return ⟨y, m, d⟩
      | _, _, _ => throw s!"bad date {s}"
    | _ => throw s!"date expected as YYYY-MM-DD, got {s}"

deriving instance ToJson, FromJson for TaxCode.Individual.Filing
deriving instance ToJson, FromJson for Relationship
deriving instance ToJson, FromJson for PlanKind

deriving instance ToJson for PersonFacts
deriving instance FromJson for PersonFacts
instance (priority := high) : FromJson PersonFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := PersonFacts))⟩

deriving instance ToJson for StatusFacts
deriving instance FromJson for StatusFacts
instance (priority := high) : FromJson StatusFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := StatusFacts))⟩

deriving instance ToJson for EarlyDistFacts
deriving instance FromJson for EarlyDistFacts
instance (priority := high) : FromJson EarlyDistFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := EarlyDistFacts))⟩

deriving instance ToJson for StudentFacts
deriving instance FromJson for StudentFacts
instance (priority := high) : FromJson StudentFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := StudentFacts))⟩

deriving instance ToJson for IraFacts
deriving instance FromJson for IraFacts
instance (priority := high) : FromJson IraFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := IraFacts))⟩

deriving instance ToJson for RolloverFacts
deriving instance FromJson for RolloverFacts
instance (priority := high) : FromJson RolloverFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := RolloverFacts))⟩

deriving instance ToJson for LumpSumFacts
deriving instance FromJson for LumpSumFacts
instance (priority := high) : FromJson LumpSumFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := LumpSumFacts))⟩

deriving instance ToJson for AlimonyItem
deriving instance FromJson for AlimonyItem
instance (priority := high) : FromJson AlimonyItem :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := AlimonyItem))⟩

deriving instance ToJson for LapseItem
deriving instance FromJson for LapseItem
instance (priority := high) : FromJson LapseItem :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := LapseItem))⟩

deriving instance ToJson for EstimatedPayment
deriving instance FromJson for EstimatedPayment
instance (priority := high) : FromJson EstimatedPayment :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := EstimatedPayment))⟩

deriving instance ToJson for EstimatedIssue
deriving instance FromJson for EstimatedIssue
instance (priority := high) : FromJson EstimatedIssue :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := EstimatedIssue))⟩

deriving instance ToJson for PtcFacts
deriving instance FromJson for PtcFacts
instance (priority := high) : FromJson PtcFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := PtcFacts))⟩

deriving instance ToJson for ReturnFacts
deriving instance FromJson for ReturnFacts
instance (priority := high) : FromJson ReturnFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := ReturnFacts))⟩

deriving instance ToJson for Claimant
deriving instance FromJson for Claimant
instance (priority := high) : FromJson Claimant :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := Claimant))⟩

deriving instance ToJson for TieBreakIssue
deriving instance FromJson for TieBreakIssue
instance (priority := high) : FromJson TieBreakIssue :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := TieBreakIssue))⟩

deriving instance ToJson for AccuracyFacts
deriving instance FromJson for AccuracyFacts
instance (priority := high) : FromJson AccuracyFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := AccuracyFacts))⟩

deriving instance ToJson for LateFacts
deriving instance FromJson for LateFacts
instance (priority := high) : FromJson LateFacts :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := LateFacts))⟩

deriving instance ToJson for Expectation
deriving instance FromJson for Expectation
instance (priority := high) : FromJson Expectation :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := Expectation))⟩

deriving instance ToJson for Case
deriving instance FromJson for Case
instance (priority := high) : FromJson Case :=
  ⟨fromJsonWithDefaults (FromJson.fromJson? (α := Case))⟩

deriving instance ToJson for PtcResult
deriving instance ToJson for ReturnResult
deriving instance ToJson for DependentOutcome
deriving instance ToJson for EarlyDistResult
deriving instance ToJson for AccuracyOutcome
deriving instance ToJson for LateOutcome
deriving instance ToJson for Extra.EstOutcome
deriving instance ToJson for Check
deriving instance ToJson for Outcome

/-- Parse a case from JSON text. -/
def parseCase (s : String) : Except String Case := do
  fromJson? (← Json.parse s)

end Legal.USTax.TaxCourt
