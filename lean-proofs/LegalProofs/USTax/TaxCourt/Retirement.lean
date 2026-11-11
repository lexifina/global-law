import LegalProofs.USTax.TaxCourt.Income

/-!
# Retirement and savings items, gambling, and the §86(e) lump-sum election (2012–2024)

* **§219 IRA deduction.** Limit (§219(b)(1), (b)(5)): the lesser of the year's deductible amount (plus the $1,000
  catch-up at 50, §219(b)(5)(B)) and compensation; for a joint return the spouse with less compensation may use the
  couple's combined compensation less the other's deduction (§219(c)). Active participant phase-out (§219(g)): the
  limit is reduced by limit × (MAGI − applicable dollar amount) ÷ range (§219(g)(2)(A)), the reduction "rounded to the
  next lowest $10" (§219(g)(2)(C), i.e. the limit rounded up to $10), and not below $200 until the range is passed
  (§219(g)(2)(B)). The ranges by year are in `iraRange`; a spouse who is not an active participant but whose spouse
  is uses the §219(g)(7) range; married filing separately (living together at any time in the year) $0–$10,000
  (§219(g)(3)(B)(iii)); a separate filer who lived apart all year is treated as unmarried (§219(g)(4)). MAGI is AGI
  figured without the IRA deduction (§219(g)(3)(A)), as Pub. 590-A's worksheet does (taxable social security
  recomputed without the deduction).
* **§408(d)(3) rollover.** A distribution paid into an IRA or plan within 60 days is not includible
  (§408(d)(3)(A)); the 60 days can be waived (§408(d)(3)(I)); an IRA-to-IRA rollover is not allowed if there was another
  within the 1-year period ending on the day of this distribution (§408(d)(3)(B)). Only the amount redeposited is
  excluded.
* **§223(f) HSA distributions.** Not used for qualified medical expenses: includible (§223(f)(2)) and a 20% additional
  tax (§223(f)(4)(A); 10% for years before 2011), not on distributions after death, disability or attaining 65
  (§223(f)(4)(B)–(C)).
* **§165(d) gambling.** Losses from wagering transactions are allowed only to the extent of gains; for 2018–2025 the
  losses include the expenses of carrying on the wagering (§165(d) as amended by Pub. L. 115-97 §11050). For a
  non-professional, an itemized deduction (§67(b)(3)).
* **§86(e) lump-sum election.** Benefits received in the year that are attributable to earlier years can be taxed as if
  received in those years: the taxable amount is the current year's amount figured without them plus, for each earlier
  year, the increase in that year's taxable amount from adding them (Pub. 915 Worksheets 2–4). The taxpayer takes the
  smaller of this and the ordinary computation (§86(e)(1): "if the taxpayer so elects").
-/

namespace Legal.USTax.TaxCourt
open TaxCode.Individual

/-! ## §219 -/

/-- §219(b)(5)(A) deductible amount by year: $5,000 (2012); $5,500 (2013–2018); $6,000 (2019–2022); $6,500 (2023);
$7,000 (2024), as each year's Pub. 590 (2012–2013) / Pub. 590-A (2014–2024) states them ("$X ($Y if you are age 50
or older)"). -/
def iraLimit (y : Nat) : Int :=
  if y ≤ 2012 then 5000 else if y ≤ 2018 then 5500 else if y ≤ 2022 then 6000 else if y == 2023 then 6500 else 7000

/-- §219(g)(3)(B) applicable dollar amounts (start of the range), by year: single or head of household; joint (the
contributor an active participant); joint, the contributor not an active participant but the spouse one
(§219(g)(7)). From Tables 1-2 and 1-3 of the year's Pub. 590 / 590-A (each range $10,000 wide, $20,000 for joint
active participants). -/
def iraStartSingle (y : Nat) : Int :=
  match y with
  | 2012 => 58000 | 2013 => 59000 | 2014 => 60000 | 2015 => 61000 | 2016 => 61000 | 2017 => 62000 | 2018 => 63000
  | 2019 => 64000 | 2020 => 65000 | 2021 => 66000 | 2022 => 68000 | 2023 => 73000 | _ => 77000
def iraStartJoint (y : Nat) : Int :=
  match y with
  | 2012 => 92000 | 2013 => 95000 | 2014 => 96000 | 2015 => 98000 | 2016 => 98000 | 2017 => 99000
  | 2018 => 101000 | 2019 => 103000 | 2020 => 104000 | 2021 => 105000 | 2022 => 109000 | 2023 => 116000
  | _ => 123000
def iraStartSpouseActive (y : Nat) : Int :=
  match y with
  | 2012 => 173000 | 2013 => 178000 | 2014 => 181000 | 2015 => 183000 | 2016 => 184000 | 2017 => 186000
  | 2018 => 189000 | 2019 => 193000 | 2020 => 196000 | 2021 => 198000 | 2022 => 204000 | 2023 => 218000
  | _ => 230000

/-- The (start, width) of the phase-out range for one spouse, or `none` if no phase-out applies. -/
def iraRange (y : Nat) (f : Filing) (livedApart active spouseActive : Bool) : Option (Int × Int) :=
  let married := f == .mfj || (f == .mfs && !livedApart)
  if active then
    if f == .mfj then some (iraStartJoint y, 20000)
    else if married then some (0, 10000)
    else some (iraStartSingle y, 10000)
  else if spouseActive && married then
    if f == .mfj then some (iraStartSpouseActive y, 10000) else some (0, 10000)
  else none

/-- §219(g)(2): the limit after the phase-out. -/
def iraPhasedLimit (limit magi : Int) : Option (Int × Int) → Int
  | none => limit
  | some (start, width) =>
    if magi ≤ start then limit
    else if magi ≥ start + width then 0
    else
      let reduction := limit * (magi - start) / width / 10 * 10
      max 200 (limit - reduction)

/-- One individual's IRA facts. -/
structure IraFacts where
  /-- Contributions to traditional IRAs for the year (deductible part claimed). -/
  contribution : Int := 0
  /-- An active participant in an employer plan (§219(g)(5)). -/
  activeParticipant : Bool := false
  deriving Repr, Inhabited

/-- **The §219 deduction** for the taxpayer and spouse. `comp`, `compS`: each one's compensation (§219(f)(1));
`magi`: AGI without the deduction. -/
def iraDeduction (p : Params) (f : Filing) (livedApart : Bool) (age ageS : Nat) (comp compS magi : Int)
    (t s : IraFacts) : Int × Int :=
  let base (a : Nat) := iraLimit p.year + (if a ≥ 50 then 1000 else 0)
  let lim (a : Nat) (mine other : IraFacts) := iraPhasedLimit (base a) magi
    (iraRange p.year f livedApart mine.activeParticipant other.activeParticipant)
  let dT := min (pos t.contribution) (min (lim age t s) (pos comp))
  if f == .mfj then
    let dS := min (pos s.contribution) (min (lim ageS s t) (pos (comp + compS - dT)))
    -- §219(c)(1)(B): the taxpayer may likewise use the spouse's compensation
    let dT' := min (pos t.contribution) (min (lim age t s) (pos (comp + compS - dS)))
    (dT', dS)
  else (dT, 0)

/-! ## §408(d)(3) -/

structure RolloverFacts where
  /-- The distribution (the part otherwise includible). -/
  distribution : Int := 0
  /-- The amount paid into an eligible retirement plan or IRA. -/
  rolledOver : Int := 0
  /-- Days from receipt to the redeposit. -/
  days : Nat := 0
  /-- §408(d)(3)(I) waiver of the 60-day requirement granted (or self-certified and not rejected). -/
  waiverGranted : Bool := false
  /-- An IRA-to-IRA rollover from a distribution received within the 1-year period ending on this distribution's
  date (§408(d)(3)(B)). -/
  priorRolloverWithin12Months : Bool := false
  /-- The distribution is from an IRA (the one-rollover rule reaches only IRA-to-IRA rollovers). -/
  fromIra : Bool := true
  deriving Repr, Inhabited

def rolloverValid (r : RolloverFacts) : Bool :=
  (r.days ≤ 60 || r.waiverGranted) && !(r.fromIra && r.priorRolloverWithin12Months)

/-- The includible part of the distribution. -/
def rolloverIncludible (r : RolloverFacts) : Int :=
  pos r.distribution - (if rolloverValid r then min (pos r.rolledOver) (pos r.distribution) else 0)

/-! ## §223(f) -/

/-- (includible amount, additional tax). -/
def hsaDistribution (year : Nat) (distributions qualifiedExpenses : Int) (exception : Bool) : Int × Int :=
  let inc := pos (distributions - pos qualifiedExpenses)
  (inc, if exception then 0 else pctRound inc (if year ≤ 2010 then 1000 else 2000))

/-! ## §165(d) -/

def gamblingLossDeduction (year : Nat) (winnings losses expenses : Int) : Int :=
  min (pos losses + (if 2018 ≤ year && year ≤ 2025 then pos expenses else 0)) (pos winnings)

/-! ## §86(e) -/

/-- Benefits received in the year for one earlier year, with that year's figures (Pub. 915 Worksheet 2). -/
structure LumpSumFacts where
  year : Nat := 0
  /-- The part of this year's benefits attributable to `year`. -/
  amount : Int := 0
  /-- That year's modified income for §86 (AGI without taxable benefits, plus tax-exempt interest and the other
  §86(b)(2) additions). -/
  priorModifiedIncome : Int := 0
  /-- Benefits received in that year (before this lump sum) and the taxable amount then reported. -/
  priorBenefits : Int := 0
  priorTaxable : Int := 0
  priorFiling : Filing := .single
  priorLivedApart : Bool := false
  deriving Repr, Inhabited

/-- The taxable amount with the election: the current year without the lump sums, plus each earlier year's increase.
`magi86` is this year's modified income (AGI without §86, plus tax-exempt interest). -/
def lumpSumElectionTaxable (f : Filing) (livedApart : Bool) (benefits magi86 : Int) (ls : List LumpSumFacts) : Int :=
  let earlier := ls.foldl (fun t l => t + pos l.amount) 0
  let now := taxableSocialSecurity f livedApart (pos (benefits - earlier)) magi86
  ls.foldl (fun t l =>
    t + pos (taxableSocialSecurity l.priorFiling l.priorLivedApart (pos l.priorBenefits + pos l.amount)
      l.priorModifiedIncome - l.priorTaxable)) now

/-! ## Tests -/

section
private def py (y : Nat) : Params := (params? y).getD default

-- §219: 2015 single, active participant, MAGI $66,000 (range $61,000–$71,000): $5,500 × 50% = $2,750.
#guard iraDeduction (py 2015) .single false 40 40 66000 0 66000 { contribution := 5500, activeParticipant := true } {}
  = (2750, 0)
-- ... MAGI $70,990: reduction $5,494.50 → $5,490; limit $10 → the $200 minimum.
#guard iraDeduction (py 2015) .single false 40 40 70990 0 70990 { contribution := 5500, activeParticipant := true } {}
  = (200, 0)
-- Not an active participant, no spouse: no phase-out; compensation limits it.
#guard iraDeduction (py 2024) .single false 55 40 5000 0 300000 { contribution := 8000 } {} = (5000, 0)
-- Joint, the taxpayer active (2024 $123,000–$143,000), MAGI $133,000: $7,000 × 50% = $3,500; the spouse (not active,
-- §219(g)(7) $230,000–$240,000) keeps the full $7,000 on the couple's compensation.
#guard iraDeduction (py 2024) .mfj false 45 45 140000 0 133000 { contribution := 7000, activeParticipant := true }
  { contribution := 7000 } = (3500, 7000)
-- Separate return, active participant, living together: $0–$10,000.
#guard iraDeduction (py 2020) .mfs false 40 40 50000 0 5000 { contribution := 6000, activeParticipant := true } {}
  = (3000, 0)

-- §408(d)(3): $20,000 distribution, $15,000 redeposited on day 59: $5,000 includible; on day 61: all of it, unless
-- waived; a second IRA rollover within 12 months: all of it.
#guard rolloverIncludible { distribution := 20000, rolledOver := 15000, days := 59 } = 5000
#guard rolloverIncludible { distribution := 20000, rolledOver := 15000, days := 61 } = 20000
#guard rolloverIncludible { distribution := 20000, rolledOver := 15000, days := 61, waiverGranted := true } = 5000
#guard rolloverIncludible { distribution := 20000, rolledOver := 20000, days := 10, priorRolloverWithin12Months := true }
  = 20000

-- §223(f): $3,000 distributed, $1,000 of medical expenses: $2,000 includible and $400 additional tax.
#guard hsaDistribution 2016 3000 1000 false = (2000, 400) ∧ hsaDistribution 2016 3000 1000 true = (2000, 0)

-- §165(d): losses $9,000 against winnings $5,000: $5,000; 2018 expenses count, 2017 not.
#guard gamblingLossDeduction 2016 5000 9000 0 = 5000 ∧ gamblingLossDeduction 2017 5000 3000 1000 = 3000 ∧
  gamblingLossDeduction 2018 5000 3000 1000 = 4000

-- §86(e): $12,000 received this year of which $8,000 is for last year. Single, modified income $30,000 this year,
-- $20,000 last year (when $4,000 was received, none taxable). Without the election: provisional income
-- $30,000 + $6,000 = $36,000: taxable $4,500 + 85% × $2,000 = $6,200 (capped at 85% × $12,000 = $10,200). With it: this
-- year $4,000 of benefits: $32,000: 50% × $7,000 = $3,500 → min(3,500, 2,000) = $2,000; last year $12,000 of benefits
-- on $20,000: $26,000: 50% × $1,000 = $500. Total $2,500.
#guard taxableSocialSecurity .single false 12000 30000 = 6200
#guard lumpSumElectionTaxable .single false 12000 30000
  [{ year := 2015, amount := 8000, priorModifiedIncome := 20000, priorBenefits := 4000 }] = 2500
end

end Legal.USTax.TaxCourt
