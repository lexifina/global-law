import LegalProofs.USTax.TaxCourt.Params

/-!
# §72(t): the 10% additional tax on early distributions from qualified retirement plans (2012–2024)

§72(t)(1): "the taxpayer's tax ... shall be increased by an amount equal to 10 percent of the portion of such amount
which is includible in gross income"; 25% for a SIMPLE IRA distribution within two years of first participation
(§72(t)(6)). The exceptions modelled, with the years they apply and the plans they reach (§72(t)(3)(A): (2)(A)(v) and
(2)(C) do not apply to IRAs; (2)(D)–(F) apply only to IRAs):

| exception | provision | plans | years | amount |
|---|---|---|---|---|
| age 59½ | (2)(A)(i) | all | all | whole |
| death | (2)(A)(ii) | all | all | whole |
| disability (§72(m)(7)) | (2)(A)(iii) | all | all | whole |
| substantially equal periodic payments | (2)(A)(iv) | all | all | whole |
| separation from service in or after the year of reaching 55 (50 for public safety employees, (10)) | (2)(A)(v) | not IRAs | all | whole |
| IRS levy under §6331 | (2)(A)(vii) | all | all | whole |
| medical expenses over the §213 floor | (2)(B) | all | all | ≤ expenses − 7.5% of AGI (2012), 10% (2013–2016; 7.5% if either spouse 65+), 7.5% (2017–) |
| QDRO | (2)(C) | not IRAs | all | whole |
| health insurance while unemployed | (2)(D) | IRAs | all | ≤ premiums |
| higher education | (2)(E) | IRAs | all | ≤ qualified expenses |
| first-time homebuyer | (2)(F), (8) | IRAs | all | ≤ $10,000 lifetime |
| qualified reservist | (2)(G) | all | all | whole |
| birth or adoption | (2)(H) (SECURE Act §113) | all | 2020– | ≤ $5,000 per child |
| coronavirus-related | CARES Act §2202 | all | 2020 | ≤ $100,000 |
| qualified disaster distributions | various disaster acts; (2)(M) from 2021 | all | as found | as found |
| terminal illness | (2)(L) (SECURE 2.0 §326) | all | 2023– | whole |
| emergency personal expense | (2)(I) (SECURE 2.0 §115) | all | 2024– | ≤ $1,000 |
| domestic abuse victim | (2)(K) (SECURE 2.0 §314) | all | 2024– | ≤ lesser of $10,000 and 50% of the vested balance |

There is no hardship, financial-need or unemployment exception (beyond (2)(D)); the Tax Court routinely so holds.
-/

namespace Legal.USTax.TaxCourt

inductive PlanKind where
  /-- an individual retirement account or annuity (§7701(a)(37)), including SEP-IRAs -/
  | ira
  /-- a SIMPLE IRA (§408(p)) -/
  | simpleIra
  /-- a qualified plan: §401(a) (incl. 401(k)), §403(a)/(b) annuity -/
  | qualifiedPlan
  deriving DecidableEq, Repr, Inhabited

/-- The court's findings about one distribution (or the year's distributions from one kind of plan). -/
structure EarlyDistFacts where
  /-- The portion includible in gross income (after basis, rollovers, conversions are taken out). -/
  amountIncludible : Int := 0
  plan : PlanKind := .ira
  /-- SIMPLE IRA distribution during the 2 years after first participation (§72(t)(6)). -/
  simpleWithinTwoYears : Bool := false
  attained59Half : Bool := false
  death : Bool := false
  /-- Disabled within §72(m)(7): unable to engage in substantial gainful activity, indefinitely. -/
  disabled : Bool := false
  sepp : Bool := false
  /-- Age attained by the end of the year the employee separated from the employer maintaining the plan. -/
  ageInSeparationYear : Option Nat := none
  /-- Qualified public safety employee (§72(t)(10)): age 50 instead of 55. -/
  publicSafetyEmployee : Bool := false
  irsLevy : Bool := false
  qdro : Bool := false
  /-- Medical care expenses paid in the year (§213(d)), unreimbursed. -/
  medicalExpenses : Int := 0
  /-- Health insurance premiums paid after 12 consecutive weeks of unemployment compensation (§72(t)(2)(D)). -/
  unemployedHealthPremiums : Int := 0
  /-- Qualified higher education expenses (§72(t)(7)) paid in the year. -/
  higherEducationExpenses : Int := 0
  /-- Qualified first-time homebuyer acquisition costs (§72(t)(8)). -/
  firstHomeCosts : Int := 0
  /-- Earlier distributions already treated as first-time homebuyer distributions (lifetime $10,000). -/
  firstHomePriorUse : Int := 0
  qualifiedReservist : Bool := false
  birthOrAdoption : Int := 0
  /-- Children born or adopted for whom a §72(t)(2)(H) distribution was made ($5,000 each). -/
  birthOrAdoptionChildren : Nat := 1
  coronavirusRelated : Int := 0
  disasterDistribution : Int := 0
  terminalIllness : Bool := false
  emergencyExpense : Int := 0
  domesticAbuse : Int := 0
  /-- Vested account balance, for the §72(t)(2)(K) cap (lesser of $10,000 or 50%). -/
  vestedBalance : Option Int := none
  deriving Repr, Inhabited

structure EarlyDistResult where
  includible : Int
  exempt : Int
  /-- rate in basis points (1000 = 10%, 2500 = 25%) -/
  rateBp : Int
  tax : Int
  exceptions : List String
  deriving Repr, Inhabited

def PlanKind.isIra : PlanKind → Bool
  | .ira | .simpleIra => true
  | .qualifiedPlan => false

/-- §213(a) floor read by §72(t)(2)(B): the year's percentage of AGI (7.5% in 2012); for 2013–2016, 7.5% if the taxpayer or spouse was
65 or older by year end (§213(f) as then in force). -/
def medicalFloor (p : Params) (agi : Int) (someone65 : Bool) : Int :=
  let bp := if 2013 ≤ p.year && p.year ≤ 2016 && someone65 then 750 else p.medicalFloorBp
  roundDollar (pos agi * bp) 10000

/-- `x` capped at `c`, and zero unless positive. -/
def capped (x c : Int) : Int := if x ≤ 0 then 0 else min x c

/-- The exceptions that reach only part of the distribution: the total amount they cover (not below zero) and their
names. -/
def partialExempt (p : Params) (agi : Int) (someone65 : Bool) (f : EarlyDistFacts) : Int × List String :=
  let ira := f.plan.isIra
  let big : Int := 1000000000000
  let parts : List (String × Int) := [
    ("§72(t)(2)(B) medical expenses",
      if f.medicalExpenses ≤ 0 then 0 else pos (f.medicalExpenses - medicalFloor p agi someone65)),
    ("§72(t)(2)(D) health insurance while unemployed", if ira then capped f.unemployedHealthPremiums big else 0),
    ("§72(t)(2)(E) higher education", if ira then capped f.higherEducationExpenses big else 0),
    ("§72(t)(2)(F) first-time homebuyer", if ira then capped f.firstHomeCosts (pos (10000 - f.firstHomePriorUse)) else 0),
    ("§72(t)(2)(H) birth or adoption", if p.year ≥ 2020 then capped f.birthOrAdoption (5000 * (f.birthOrAdoptionChildren : Int)) else 0),
    ("CARES Act §2202 coronavirus-related", if p.year == 2020 then capped f.coronavirusRelated 100000 else 0),
    ("qualified disaster distribution", capped f.disasterDistribution big),
    ("§72(t)(2)(I) emergency personal expense", if p.year ≥ 2024 then capped f.emergencyExpense 1000 else 0),
    ("§72(t)(2)(K) domestic abuse victim", if p.year ≥ 2024 then capped f.domesticAbuse (min 10000 ((f.vestedBalance.map (· / 2)).getD 10000)) else 0)]
  let used := parts.filter (·.2 > 0)
  (pos (used.foldl (fun s e => s + e.2) 0), used.map (·.1))

/-- §72(t)(1) 10%, or §72(t)(6) 25% (basis points). -/
def earlyDistRate (f : EarlyDistFacts) : Int :=
  if f.plan == .simpleIra && f.simpleWithinTwoYears then 2500 else 1000

/-- The exceptions that reach the whole distribution, by name. -/
def wholeExceptions (p : Params) (f : EarlyDistFacts) : List String :=
  let ira := f.plan.isIra
  let whole : List (String × Bool) := [
    ("§72(t)(2)(A)(i) age 59½", f.attained59Half),
    ("§72(t)(2)(A)(ii) death", f.death),
    ("§72(t)(2)(A)(iii) disability", f.disabled),
    ("§72(t)(2)(A)(iv) substantially equal periodic payments", f.sepp),
    ("§72(t)(2)(A)(v) separation from service after 55", !ira &&
      (f.ageInSeparationYear.map (fun a => decide ((if f.publicSafetyEmployee then 50 else 55) ≤ a))).getD false),
    ("§72(t)(2)(A)(vii) IRS levy", f.irsLevy),
    ("§72(t)(2)(C) QDRO", !ira && f.qdro),
    ("§72(t)(2)(G) qualified reservist", f.qualifiedReservist),
    ("§72(t)(2)(L) terminal illness", p.year ≥ 2023 && f.terminalIllness)]
  (whole.filter (·.2)).map (·.1)

/-- The part of the includible amount an exception covers. -/
def earlyDistExempt (p : Params) (agi : Int) (someone65 : Bool) (f : EarlyDistFacts) : Int :=
  if (wholeExceptions p f).isEmpty then min (pos f.amountIncludible) (partialExempt p agi someone65 f).1
  else pos f.amountIncludible

/-- **The additional tax**: the rate times the includible amount not covered by an exception, rounded. `agi`
(including the distribution) and `someone65` are read only by the medical exception. -/
def earlyDistAmount (p : Params) (agi : Int) (someone65 : Bool) (f : EarlyDistFacts) : Int :=
  pctRound (pos f.amountIncludible - earlyDistExempt p agi someone65 f) (earlyDistRate f)

def earlyDistTax (p : Params) (agi : Int) (someone65 : Bool) (f : EarlyDistFacts) : EarlyDistResult :=
  { includible := pos f.amountIncludible, exempt := earlyDistExempt p agi someone65 f, rateBp := earlyDistRate f,
    tax := earlyDistAmount p agi someone65 f,
    exceptions := if (wholeExceptions p f).isEmpty then (partialExempt p agi someone65 f).2 else wholeExceptions p f }

/-- No exception found. -/
def EarlyDistFacts.noException (f : EarlyDistFacts) : Prop :=
  f.attained59Half = false ∧ f.death = false ∧ f.disabled = false ∧ f.sepp = false ∧ f.ageInSeparationYear = none ∧
  f.irsLevy = false ∧ f.qdro = false ∧ f.qualifiedReservist = false ∧ f.terminalIllness = false ∧
  f.medicalExpenses = 0 ∧ f.unemployedHealthPremiums = 0 ∧ f.higherEducationExpenses = 0 ∧ f.firstHomeCosts = 0 ∧
  f.birthOrAdoption = 0 ∧ f.coronavirusRelated = 0 ∧ f.disasterDistribution = 0 ∧ f.emergencyExpense = 0 ∧
  f.domesticAbuse = 0

/-- **With no exception, the additional tax is 10% of the includible amount** (rounded to the dollar), outside the
SIMPLE two-year rule. -/
theorem partialExempt_none (p : Params) (agi : Int) (s65 : Bool) (f : EarlyDistFacts) (h : f.noException) :
    (partialExempt p agi s65 f).1 = 0 := by
  obtain ⟨-, -, -, -, -, -, -, -, -, h10, h11, h12, h13, h14, h15, h16, h17, h18⟩ := h
  unfold partialExempt capped
  simp [h10, h11, h12, h13, h14, h15, h16, h17, h18, pos]

theorem earlyDistTax_no_exception (p : Params) (agi : Int) (s65 : Bool) (f : EarlyDistFacts)
    (h : f.noException) (hs : f.plan ≠ .simpleIra) :
    (earlyDistTax p agi s65 f).tax = pctRound (pos f.amountIncludible) 1000 := by
  have hz := partialExempt_none p agi s65 f h
  obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9, -⟩ := h
  show earlyDistAmount p agi s65 f = _
  unfold earlyDistAmount earlyDistExempt earlyDistRate wholeExceptions
  simp [h1, h2, h3, h4, h5, h6, h7, h8, h9, hs, hz, pos]
  congr 1; omega

/-- The tax is never negative and never more than the rate applied to the includible amount. -/
theorem earlyDistTax_bounds (p : Params) (agi : Int) (s65 : Bool) (f : EarlyDistFacts) :
    0 ≤ (earlyDistTax p agi s65 f).tax ∧
    (earlyDistTax p agi s65 f).tax ≤ pctRound (pos f.amountIncludible) (earlyDistRate f) := by
  have h0 : 0 ≤ (partialExempt p agi s65 f).1 := by unfold partialExempt; simp only; exact pos_nonneg _
  show 0 ≤ earlyDistAmount p agi s65 f ∧ earlyDistAmount p agi s65 f ≤ _
  unfold earlyDistAmount earlyDistExempt earlyDistRate
  generalize (partialExempt p agi s65 f).1 = e at h0
  unfold pctRound roundDollar pos
  (repeat' split) <;> omega

/-! ## Tests (Pub. 590-B examples; the rules are the same each year except where dated) -/

section
private def py (y : Nat) : Params := (params? y).getD default

-- $20,000 IRA distribution at 45, no exception: $2,000.
#guard (earlyDistTax (py 2019) 80000 false { amountIncludible := 20000 }).tax = 2000
-- Hardship is no exception; unemployment is no exception for a 401(k) distribution.
#guard (earlyDistTax (py 2022) 50000 false { amountIncludible := 12345, plan := .qualifiedPlan }).tax = 1235
-- Separation from service at 55 shields a 401(k) distribution, but not an IRA distribution.
#guard (earlyDistTax (py 2018) 60000 false { amountIncludible := 30000, plan := .qualifiedPlan, ageInSeparationYear := some 55 }).tax = 0
#guard (earlyDistTax (py 2018) 60000 false { amountIncludible := 30000, plan := .ira, ageInSeparationYear := some 55 }).tax = 3000
-- First-time homebuyer: $25,000 IRA distribution, $40,000 of costs: only $10,000 exempt: $1,500.
#guard (earlyDistTax (py 2021) 70000 false { amountIncludible := 25000, firstHomeCosts := 40000 }).tax = 1500
-- ... from a 401(k): no exception: $2,500.
#guard (earlyDistTax (py 2021) 70000 false { amountIncludible := 25000, plan := .qualifiedPlan, firstHomeCosts := 40000 }).tax
  = 2500
-- Medical: AGI $50,000, expenses $8,000: 2016 floor 10% → $3,000 exempt; 2017 floor 7.5% → $4,250 exempt.
#guard (earlyDistTax (py 2016) 50000 false { amountIncludible := 10000, medicalExpenses := 8000 }).exempt = 3000
#guard (earlyDistTax (py 2016) 50000 true { amountIncludible := 10000, medicalExpenses := 8000 }).exempt = 4250
#guard (earlyDistTax (py 2017) 50000 false { amountIncludible := 10000, medicalExpenses := 8000 }).exempt = 4250
-- SIMPLE IRA in the first two years: 25%.
#guard (earlyDistTax (py 2023) 40000 false { amountIncludible := 8000, plan := .simpleIra, simpleWithinTwoYears := true }).tax
  = 2000
-- Coronavirus-related distributions only in 2020.
#guard (earlyDistTax (py 2020) 40000 false { amountIncludible := 30000, coronavirusRelated := 30000 }).tax = 0
#guard (earlyDistTax (py 2021) 40000 false { amountIncludible := 30000, coronavirusRelated := 30000 }).tax = 3000
-- Birth or adoption from 2020: $5,000 of a $6,000 distribution.
#guard (earlyDistTax (py 2019) 40000 false { amountIncludible := 6000, birthOrAdoption := 5000 }).tax = 600
#guard (earlyDistTax (py 2020) 40000 false { amountIncludible := 6000, birthOrAdoption := 5000 }).tax = 100
-- the $5,000 per child cap applies even if more is claimed
#guard (earlyDistTax (py 2020) 40000 false { amountIncludible := 8000, birthOrAdoption := 8000 }).tax = 300
end

end Legal.USTax.TaxCourt
