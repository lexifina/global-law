import MtTax.Params

/-!
# Malta YA 2026: the computation

* Unit (ITA art. 49): a married couple living together is charged as one, on the married table (art. 56(1)(a)).
  The responsible spouse may elect (art. 50) "that the tax on the chargeable income in respect of such income
  derived by the other spouse be computed separately": each spouse's income from employment, trade and pension is
  then charged on art. 56(1)(b) (single, or parent where "a parent maintained under his or her custody a child");
  all other income (interest declared, rent, dividends declared) "shall be aggregated with the total income of the
  spouse having the higher income" (art. 50(1) proviso). Input field `mtSeparate` (default false).
* Unmarried adult: single table; with a child ≤ 18 the parent table; a lone parent who meets art. 56(1)(b)
  proviso (a)/(b) (sole custody, sole children's-allowance beneficiary, no maintenance from and not living with the
  other parent) gets the married table. Default: a one-adult household with a child meets them (field
  `mtLoneParentConditions`, default true). Two unmarried adults: each alone; parent table each if children.
* Investment income: interest 15 % final (art. 33) unless `mtInterestDeclared`; dividends from listed Maltese
  shares carry 35 % company tax (art. 56(6), 59) and are not declared by default (no further tax); with
  `mtDividendsDeclared` the gross (net / 0.65) is charged and the 35 % credit set off and refunded (art. 31,
  ITMA art. 48; art. 12(1)(c)(iii) exemption does not apply to listed holdings under 0.5 %: its proviso).
  Gains on listed shares: not chargeable (art. 5(6)(b)). Rent: normal rates by default; `mtRentFinal` = 15 % of
  gross, final (art. 31D).
* Part-time work (art. 90A, S.L. 123.39): field `mtPartTime1` / `mtPartTime2` = the part of that adult's wages
  that is registered part-time work; 10 % final up to €10,000, the rest at normal rates; only if the adult has
  other employment or pension income (or, married, the spouse does: art. 90A(9)).
* Credits: personal retirement scheme 25 % of contributions, max €750 per person (S.L. 123.163 r. 8),
  `pensionContributions` split equally between spouses.
* Class One (employees) and Class Two (self-occupied) contributions: weekly, SSA Tenth Schedule; Children's
  Allowance: SSA art. 76, Fourteenth Schedule Part VI, children under 16, household income net of contributions.
-/

namespace MtTax
open TaxKernel

/-- Which art. 56(1) table. -/
inductive Table where
  | married | single | parent
  deriving Repr, DecidableEq, Inhabited

def Table.name : Table → String
  | .married => "married (art. 56(1)(a))"
  | .single => "single (art. 56(1)(b))"
  | .parent => "parent (art. 56(1)(b) last proviso)"

def Table.sched : Table → Schedule
  | .married => marriedSched
  | .single => singleSched
  | .parent => parentSched

def Table.divThreshold : Table → Int
  | .married => divThresholdMarried
  | .single => divThresholdSingle
  | .parent => divThresholdParent

/-- Tax in cents on chargeable income `x` (whole euros) by a table: ticks are euro × bp, 1 cent = 100 ticks. -/
def taxCents (t : Table) (x : Int) : Int := t.sched.ticks (pos x) / 100

/-- Tax in cents for income year `y`: YA 2026 tables from income 2025; for income 2022-2024 (YA 2023-2025) the
pre-Act IX of 2025 tables (`marriedYA2025`, `singleYA2025`, `parentYA2025`, Params). -/
def taxCentsY (y : Nat) (t : Table) (x : Int) : Int :=
  if y ≥ 2025 then taxCents t x
  else match t with
    | .married => marriedYA2025 (pos x)
    | .single => singleYA2025 (pos x)
    | .parent => parentYA2025 (pos x)

/-- Cents to whole euros, nearest (art. 56(19)(b)). -/
def toEuro (cents : Int) : Int := divR .halfUp cents 100

/-! ## Class One and Class Two contributions (cents a week, then a year of 52 contribution weeks in 2025) -/

/-- Born on 31 December 1961 or before: 64 or over at the end of 2025 (age taken at 31 December 2025). -/
def bornBy1961 (age : Nat) : Bool := age ≥ 64

/-- Weekly basic wage in cents, "the weekly equivalent", to the nearest cent. -/
def weeklyCents (annual : Int) : Int := divR .halfUp (annual * 100) 52

/-- Tenth Schedule Part I, the employee's weekly Class One contribution (cents). Nothing on no wages or at 65+
(pension age; EUROMOD CR MT §2.6.2 "National Insurance is due from 16 to 65"). -/
def class1Weekly (age : Nat) (wages : Int) : Int :=
  if wages ≤ 0 ∨ age ≥ 65 ∨ age < 16 then 0
  else
    let w := weeklyCents wages
    if w ≤ c1LowWage then (if age < 18 then c1CatA else c1CatB)
    else min (divR .halfUp (w * c1RateBp) 10000) (if bornBy1961 age then c1MaxOld else c1MaxNew)

/-- Part III, Class Two weekly contribution of a self-occupied person (cents), current-year earnings standing in for
the previous year's. A person who also pays Class One pays at most the Class Two maximum in all (simplification). -/
def class2Weekly (age : Nat) (se c1w : Int) : Int :=
  if se ≤ c2Exempt ∨ age ≥ 65 then 0
  else
    let mx := if bornBy1961 age then c2MaxOld else c2MaxNew
    let raw := if se * 100 < c2LowIncomeCents then c2Min
      else min mx (divR .halfUp (se * 100 * c2RateBp) (10000 * 52))
    max 0 (min raw (mx - c1w))

/-- Year-aware Class One (income year `y`): the Tenth Schedule of that year (`ssFor`); born on 31 December 1961 or
before = aged `y - 1961` or more at the end of the year. -/
def class1WeeklyY (y : Nat) (age : Nat) (wages : Int) : Int :=
  let p := ssFor y
  if wages ≤ 0 ∨ age ≥ 65 ∨ age < 16 then 0
  else
    let w := weeklyCents wages
    if w ≤ p.lowWage then (if age < 18 then p.catA else p.catB)
    else min (divR .halfUp (w * c1RateBp) 10000) (if age + 1961 ≥ y then p.maxOld else p.maxNew)

/-- Year-aware Class Two (self-occupied), as `class2Weekly` with that year's Part III. -/
def class2WeeklyY (y : Nat) (age : Nat) (se c1w : Int) : Int :=
  let p := ssFor y
  if se ≤ c2Exempt ∨ age ≥ 65 then 0
  else
    let mx := if age + 1961 ≥ y then p.c2MaxOld else p.c2MaxNew
    let raw := if se * 100 < p.c2Low then p.c2Min
      else min mx (divR .halfUp (se * 100 * c2RateBp) (10000 * 52))
    max 0 (min raw (mx - c1w))

theorem class1WeeklyY_examples :
    class1WeeklyY 2025 40 1 = class1Weekly 40 1 ∧ class1WeeklyY 2025 40 27679 = class1Weekly 40 27679 ∧
    class1WeeklyY 2025 64 30000 = class1Weekly 64 30000 ∧ class1WeeklyY 2025 63 30000 = class1Weekly 63 30000 ∧
    class1WeeklyY 2022 40 1 = 1828 ∧ class1WeeklyY 2022 40 40000 = 4997 ∧ class1WeeklyY 2023 62 40000 = 3928 ∧ class1WeeklyY 2023 61 40000 = 5160 := by
  decide

structure Social where
  c1 : Int
  c2 : Int
  deriving Repr

def social (a : Adult) : Social :=
  let w1 := class1Weekly a.age a.wages
  let w2 := class2Weekly a.age a.selfEmployment w1
  { c1 := toEuro (52 * w1), c2 := toEuro (52 * w2) }

/-! ### Contribution weeks in a year (improvement round 3)
SSA (Cap. 318) art. 2: "\"contribution year\" means the period starting from the first Monday in January and ending on
the last Sunday before the first Monday in January of the following year" (`law/cap318_art2.txt`); Class One and
Class Two are weekly contributions (Tenth Schedule, "per week"). A contribution year therefore has 52 or 53 weeks:
53 when the next year's first Monday falls later in January (2024: Monday 1 January 2024 to Sunday 5 January 2025;
also 2018, 2029). Calendar income year `y` is matched with contribution year `y` (they share every Monday but at most
six days). The basic weekly wage stays annual / 52 (`weeklyCents`). -/

/-- Day of the week of 1 January of `y` (0 = Sunday), Gauss's formula. -/
def jan1Dow (y : Nat) : Nat := (1 + 5 * ((y - 1) % 4) + 4 * ((y - 1) % 100) + 6 * ((y - 1) % 400)) % 7
/-- Date in January of the first Monday of `y`. -/
def firstMonday (y : Nat) : Nat := 1 + (8 - jan1Dow y) % 7
def daysIn (y : Nat) : Nat := if (y % 4 = 0 ∧ y % 100 ≠ 0) ∨ y % 400 = 0 then 366 else 365
/-- Weeks in contribution year `y`. -/
def contribWeeks (y : Nat) : Int := ((daysIn y - firstMonday y + firstMonday (y + 1)) / 7 : Nat)

theorem contribWeeks_values :
    firstMonday 2024 = 1 ∧ firstMonday 2025 = 6 ∧ firstMonday 2022 = 3 ∧ firstMonday 2023 = 2 ∧
    contribWeeks 2022 = 52 ∧ contribWeeks 2023 = 52 ∧ contribWeeks 2024 = 53 ∧ contribWeeks 2025 = 52 ∧
    contribWeeks 2026 = 52 ∧ contribWeeks 2018 = 53 := by decide

def socialY (y : Nat) (a : Adult) : Social :=
  let w1 := class1WeeklyY y a.age a.wages
  let w2 := class2WeeklyY y a.age a.selfEmployment w1
  { c1 := toEuro (contribWeeks y * w1), c2 := toEuro (contribWeeks y * w2) }

theorem socialY_2025_c1 (a : Adult) :
    (socialY 2025 a).c1 = toEuro (52 * class1WeeklyY 2025 a.age a.wages) := by
  simp [socialY, show contribWeeks 2025 = 52 by decide]

/-! ## Children's Allowance (cents a year) -/

/-- Per child under 16: 6.5 % of (€27,006.12 − reckonable income, floored at €7,741.12), weekly to the cent, never
below the fixed €8.66 a week. -/
def caWeeklyPerChild (incomeEuro : Int) : Int :=
  let inc := max (incomeEuro * 100) caFloor
  if inc > caThreshold then caFixedWeekly
  else max caFixedWeekly (divR .halfUp ((caThreshold - inc) * caRateBp) (10000 * 52))

def childrenAllowance (nUnder16 : Nat) (incomeEuro : Int) : Int :=
  toEuro (52 * caWeeklyPerChild incomeEuro * nUnder16)

/-- Year-aware Children's Allowance (`caFor`). -/
def caWeeklyPerChildY (y : Nat) (incomeEuro : Int) : Int :=
  let (th, fl, fx) := caFor y
  let inc := max (incomeEuro * 100) fl
  if inc > th then fx
  else max fx (divR .halfUp ((th - inc) * caRateBp) (10000 * 52))

/-- Weeks paid in a year (improvement round 6). Table A of the Fourteenth Schedule Part VI is an annual amount ("6.5%
... on difference obtaining between reckonable annual income and" the threshold), paid weekly as a 52nd of it: 52.
Table B, "Fixed Children's Allowance ... €8.66 per week for each such child", is a weekly rate; SSA art. 2 defines the
"benefit year" as "the period starting from the first Monday in January and ending on the last Sunday before the first
Monday in January of the following year", which has 53 weeks in 2024 (`contribWeeks`, same definition). So a child on
the fixed rate gets 53 weekly payments in benefit year 2024; 52 in 2022, 2023 and 2025. -/
def caWeeksPaid (y : Nat) (incomeEuro : Int) : Int :=
  let (_, _, fx) := caFor y
  if caWeeklyPerChildY y incomeEuro = fx then contribWeeks y else 52

def childrenAllowanceY (y : Nat) (nUnder16 : Nat) (incomeEuro : Int) : Int :=
  toEuro (caWeeksPaid y incomeEuro * caWeeklyPerChildY y incomeEuro * nUnder16)

/-- Fourteenth Schedule Part VI note 2 (L.N. 232 of 2023, L.N. 257 of 2023, L.N. 10 of 2025: "An allowance payable to
a household under Table A above, whose annual earnings [2024: income] from employment does not exceed the National
Minimum Wage, may in no case be less than the maximum rate in this Part"). Reading: the household's gross annual
employment earnings against the weekly National Minimum Wage for 18 and over (`nmwWeekly18`) times 52 (the Orders fix
a rate "per week related to a normal working week"; neither the SSA nor the Orders state an annual figure, so a
calendar year's 52 weeks is used); "maximum rate" = the Table A rate at the floor income; Table A applies only when
the reckonable income does not exceed the threshold. -/
def caNmwFloorApplies (y : Nat) (incomeEuro empEarningsEuro : Int) : Bool :=
  let (th, _, _) := caFor y
  match nmwWeekly18 y with
  | some w => decide (incomeEuro * 100 ≤ th) && decide (empEarningsEuro * 100 ≤ 52 * w)
  | none => false

def childrenAllowanceNmw (y : Nat) (nUnder16 : Nat) (incomeEuro empEarningsEuro : Int) : Int :=
  if caNmwFloorApplies y incomeEuro empEarningsEuro then
    toEuro (52 * max (caWeeklyPerChildY y incomeEuro) (caWeeklyPerChildY y 0) * nUnder16)
  else childrenAllowanceY y nUnder16 incomeEuro

/-- Above the minimum wage nothing changes. -/
theorem caNmw_above (y : Nat) (n : Nat) (inc emp : Int) (h : caNmwFloorApplies y inc emp = false) :
    childrenAllowanceNmw y n inc emp = childrenAllowanceY y n inc := by
  simp [childrenAllowanceNmw, h]

theorem nmw_annual_values :
    52 * 18283 = (950716 : Int) ∧ 52 * 19273 = (1002196 : Int) ∧ 52 * 21354 = (1110408 : Int) ∧
    52 * 22178 = (1153256 : Int) := by decide

theorem caWeeksPaid_2025 (inc : Int) : caWeeksPaid 2025 inc = 52 := by
  unfold caWeeksPaid; split <;> simp [show contribWeeks 2025 = 52 by decide]

theorem caY_examples :
    caWeeklyPerChildY 2025 0 = caWeeklyPerChild 0 ∧ caWeeklyPerChildY 2025 30000 = caWeeklyPerChild 30000 ∧
    caWeeklyPerChildY 2025 15000 = caWeeklyPerChild 15000 ∧ caWeeklyPerChildY 2022 30000 = 865 := by decide

/-! ## Income tax -/

/-- A child that makes a parent: "not over 18 years of age" (education to 23 not in the household contract). -/
def qualifyingChildren (c : Canon) : Nat := (c.children.filter (·.age ≤ 18)).length

structure Options where
  separate : Bool := false
  loneParent : Bool := true
  interestDeclared : Bool := false
  dividendsDeclared : Bool := false
  rentFinal : Bool := false
  unlisted : Bool := false
  partTime1 : Int := 0
  partTime2 : Int := 0
  deriving Repr

def options (c : Canon) : Options :=
  { separate := (c.bool? "mtSeparate").getD false
    loneParent := (c.bool? "mtLoneParentConditions").getD true
    interestDeclared := (c.bool? "mtInterestDeclared").getD false
    dividendsDeclared := (c.bool? "mtDividendsDeclared").getD false
    rentFinal := (c.bool? "mtRentFinal").getD false
    unlisted := (c.bool? "mtDividendsUnlisted").getD false
    partTime1 := (c.int? "mtPartTime1").getD 0
    partTime2 := (c.int? "mtPartTime2").getD 0 }

/-- The household's income outside earnings that enters a return (euros), and the flat taxes (cents). -/
structure Other where
  declared : Int        -- interest/rent/gross dividends charged at the normal rates
  divCredit : Int       -- cents: the 35 % imputation credit set off (refundable)
  flatCents : Int       -- cents: final taxes (interest 15 %, rent 15 %)
  interestWht : Int
  rentFinal : Int
  divGross : Int
  deriving Repr

def other (c : Canon) (o : Options) : Other :=
  let iDecl := if o.interestDeclared then c.interest else 0
  let iWht := if o.interestDeclared then 0 else c.interest * interestWhtBp / 100
  let rDecl := if o.rentFinal then 0 else c.rentalIncome
  let rFin := if o.rentFinal then c.rentalIncome * rentFinalBp / 100 else 0
  -- gross dividend = net / (1 − 35 %), to the euro; credit = gross − net (art. 31: dividend "to include tax")
  let dGross := if o.dividendsDeclared then divR .halfUp (c.dividends * 10000) (10000 - companyRateBp) else 0
  let dCred := dGross * 35  -- cents: 35 % of the gross (before the art. 12(1)(c)(iii) split)
  { declared := iDecl + rDecl, divCredit := dCred, flatCents := iWht + rFin,
    interestWht := toEuro iWht, rentFinal := toEuro rFin, divGross := dGross }

/-- Part-time 10 % (art. 90A): the qualifying part of `pt` (capped at €10,000) and the tax on it (cents). -/
def partTime (pt wages pension : Int) (spouseQualifies : Bool) : Int × Int :=
  let pt := clamp 0 wages pt
  let own : Bool := decide (wages - pt > 0) || decide (pension > 0)
  if pt > 0 ∧ (own || spouseQualifies) = true then
    let q := min pt partTimeLimitEmployment
    (q, q * partTimeBp / 100)
  else (0, 0)

/-- Personal retirement scheme credit (euros) for one person's contributions. -/
def prsCredit (contrib : Int) : Int := min prsCap (pos contrib * prsRateBp / 10000)

/-- ITA art. 12(1)(c)(iii): a dividend from a taxed account other than the final tax account, paid to an individual
whose "chargeable income, excluding such dividend, is equal to or exceeds the relevant threshold", is exempt (and
48(1)(a) ITMA: no refund of the tax on an exempt dividend); below the threshold the part that takes chargeable income
above it is exempt. Not for listed holdings under 0.5 % (its proviso): `unlisted` = false. Returns the taxable part
of the gross dividend `g`. -/
def divTaxable (unlisted : Bool) (tb : Table) (ciExcl g : Int) : Int :=
  if !unlisted then g
  else if ciExcl ≥ tb.divThreshold then 0
  else min g (tb.divThreshold - ciExcl)

/-- Non-refundable credits then refundable dividend credit, all in cents. -/
def afterCredits (taxC prsC divC : Int) : Int := pos (taxC - prsC) - divC

structure Result where
  incomeTaxCents : Int
  progressiveCents : Int
  partTimeCents : Int
  chargeable : List Int
  tables : List Table
  prsUsed : Int
  divTaxable : Int := 0
  deriving Repr

/-- One adult's earnings that enter the progressive tables, after removing qualifying part-time income. -/
def earn (a : Adult) (ptq : Int) : Int := a.wages - ptq + a.selfEmployment + a.pension

def compute (c : Canon) (o : Options) : Result :=
  let oth := other c o
  let kids := qualifyingChildren c
  match c.adults with
  | [a, b] =>
    let aq : Bool := decide (a.wages - clamp 0 a.wages o.partTime1 > 0) || decide (a.pension > 0)
    let bq : Bool := decide (b.wages - clamp 0 b.wages o.partTime2 > 0) || decide (b.pension > 0)
    let (q1, t1) := partTime o.partTime1 a.wages a.pension (c.married && bq)
    let (q2, t2) := partTime o.partTime2 b.wages b.pension (c.married && aq)
    let e1 := earn a q1
    let e2 := earn b q2
    let pc1 := prsCredit (half1 c.pensionContributions) * 100
    let pc2 := prsCredit (half2 c.pensionContributions) * 100
    let ptc := t1 + t2
    if c.married && !o.separate then
      let ciX := e1 + e2 + oth.declared
      let dt := divTaxable o.unlisted .married ciX oth.divGross
      let ci := ciX + dt
      let tx := taxCentsY c.year .married ci
      { incomeTaxCents := afterCredits tx (pc1 + pc2) (dt * 35) + oth.flatCents + ptc,
        progressiveCents := tx, partTimeCents := ptc, chargeable := [ci], tables := [.married],
        prsUsed := min (pos tx) (pc1 + pc2), divTaxable := dt }
    else
      -- separate computation (art. 50) or two unmarried adults: each on 56(1)(b); other income with the higher
      -- earner (art. 50(1) proviso; for unmarried adults the contract's investment split would be equal, but the
      -- household totals are attributed the same way so that the two cases compare like with like)
      let tb : Table := if kids > 0 then .parent else .single
      let (cx1, cx2) := if e1 ≥ e2 then (e1 + oth.declared, e2) else (e1, e2 + oth.declared)
      let dt := divTaxable o.unlisted tb (if e1 ≥ e2 then cx1 else cx2) oth.divGross
      let (ci1, ci2) := if e1 ≥ e2 then (cx1 + dt, cx2) else (cx1, cx2 + dt)
      let x1 := taxCentsY c.year tb ci1
      let x2 := taxCentsY c.year tb ci2
      let (d1, d2) := if e1 ≥ e2 then (dt * 35, 0) else (0, dt * 35)
      let r1 := afterCredits x1 pc1 d1
      let r2 := afterCredits x2 pc2 d2
      { incomeTaxCents := r1 + r2 + oth.flatCents + ptc, progressiveCents := x1 + x2, partTimeCents := ptc,
        chargeable := [ci1, ci2], tables := [tb, tb],
        prsUsed := min (pos x1) pc1 + min (pos x2) pc2, divTaxable := dt }
  | a :: _ =>
    let (q1, t1) := partTime o.partTime1 a.wages a.pension false
    let tb : Table := if kids > 0 then (if o.loneParent then .married else .parent) else .single
    let ciX := earn a q1 + oth.declared
    let dt := divTaxable o.unlisted tb ciX oth.divGross
    let ci := ciX + dt
    let tx := taxCentsY c.year tb ci
    let pc := prsCredit c.pensionContributions * 100
    { incomeTaxCents := afterCredits tx pc (dt * 35) + oth.flatCents + t1, progressiveCents := tx,
      partTimeCents := t1, chargeable := [ci], tables := [tb], prsUsed := min (pos tx) pc, divTaxable := dt }
  | [] => { incomeTaxCents := 0, progressiveCents := 0, partTimeCents := 0, chargeable := [], tables := [],
            prsUsed := 0 }

/-- Income tax in euros (rounded once, on the total). -/
def incomeTax (c : Canon) (o : Options) : Int := toEuro (compute c o).incomeTaxCents

/-- `--euromod` (convention, EUROMOD J2.0+, documented; never statute). EUROMOD Country Report Malta 2021-2024
(Vella Magro, Said, Mifsud, ed. Cruces, JRC141187, 2025), § 2.7.1 "Tax unit (tin_mt)":
(a) "EUROMOD modelling: to establish the unit of taxation, EUROMOD optimises between individual and joint taxation in
the case of married couples ... The more advantageous regime (i.e. the one yielding a lower tax liability) is chosen":
married couples get the lower of the joint and the separate computation (statute: joint unless the art. 50 election is
made; `mtSeparate`).
(b) the same section states the married-rate condition for a widowed or separated parent as "The individual was in
receipt of financial assistance in respect of the maintenance of the said child from the other parent", which a
hypothetical household without maintenance does not meet, so the parent computation applies (`mtLoneParentConditions`
false). The statute says "not in receipt" (art. 56(1)(b) proviso (b)(iii); FINDINGS F10(a)): this reproduces
EUROMOD's documented condition, not the law. -/
def euromodOptions (c : Canon) : Options :=
  let o := { options c with loneParent := false }
  if c.married && c.isCouple then
    { o with separate := decide (incomeTax c { o with separate := true } < incomeTax c { o with separate := false }) }
  else o

def outWith (args : List String) (c : Canon) : Out :=
  let o := if args.contains "--euromod" then euromodOptions c else options c
  let r := compute c o
  let oth := other c o
  let ss := c.adults.map (socialY c.year)
  let c1 := sumInts (ss.map (·.c1))
  let c2 := sumInts (ss.map (·.c2))
  let n16 := (c.children.filter (·.age < 16)).length
  let caInc := c.gross - c.dividends + (if o.dividendsDeclared then oth.divGross else c.dividends) - c1 - c2
  let ca := childrenAllowanceNmw c.year n16 caInc (sumInts (c.adults.map (·.wages)))
  let isMarriedCouple := c.married && c.isCouple
  let tJoint := incomeTax c { o with separate := false }
  let tSep := incomeTax c { o with separate := true }
  let couple : List (String × Lean.Json) :=
    if isMarriedCouple then [Out.d "taxJointComputation" tJoint, Out.d "taxSeparateComputation" tSep,
      Out.d "separateSaves" (tJoint - tSep)] else []
  Out.make c "MT" "EUR" (toEuro r.incomeTaxCents) (employeeSocial := c1 + c2) (benefits := ca)
    (detail := [Out.d "taxableIncome" (sumInts r.chargeable),
                Out.d "taxBeforeCredits" (toEuro r.progressiveCents),
                Out.dStr "tables" (String.intercalate "; " (r.tables.map Table.name)),
                Out.d "interestFinalTax" oth.interestWht, Out.d "rentFinalTax" oth.rentFinal,
                Out.d "partTimeTax" (toEuro r.partTimeCents),
                Out.d "dividendGrossDeclared" oth.divGross, Out.d "dividendGrossTaxable" r.divTaxable,
                Out.d "dividendCreditRefundable" (toEuro (r.divTaxable * 35)),
                Out.d "prsCreditUsed" (toEuro r.prsUsed),
                Out.d "class1" c1, Out.d "class2" c2, Out.d "childrensAllowance" ca,
                Out.dBool "separateComputation" (isMarriedCouple && o.separate)] ++ couple)
    (unsupported := (if c.year < 2022 then ["years before 2022 are computed with the 2022 (YA 2023) parameters: not modelled"] else []) ++
      (if c.year < 2025 then ["income " ++ toString c.year ++ " = YA " ++ toString (c.year + 1) ++ ": art. 56(1) tables in force before Act IX of 2025; Tenth and Fourteenth Schedules of the year (L.N. 232 of 2023 for 2022, L.N. 257 of 2023 for 2023, L.N. 10 of 2025 for 2024); dividend thresholds, PRS and part-time rules as in the 2024-06-30 text"]
       else ["basis year 2025 = YA 2026; SSC and Children's Allowance at the Tenth/Fourteenth Schedule in force (L.N. 10 of 2025, 2024 amounts; no 2025 schedule published by 2026-10-06)"]) ++ [
      "Children's Allowance supplement, in-work benefit, COLA additional benefit not modelled",
      "deductions (school/childcare fees, rent expenses), donations, pension exemptions not modelled",
      "capital gains on listed shares not chargeable (art. 5(6)(b))",
      "company tax on dividends (35 %) is not in incomeTax; declared dividends show the refundable credit"])

def out (c : Canon) : Out := outWith [] c

def country : Country :=
  { code := "MT", name := "Malta", currency := "EUR", year := "2025 (YA 2026)", compute := out, computeWith := outWith }

end MtTax
