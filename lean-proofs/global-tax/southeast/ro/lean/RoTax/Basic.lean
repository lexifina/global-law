import RoTax.Wage

/-!
# Romania 2025: the household (contract `~/cmp/shared/CONTRACT.md`)

Unit: the individual (no joint return in Romania). Wages: art. 78 monthly final tax (`Wage.lean`). Pensions: art. 100-101
monthly, CASS on the excess over 3.000 lei from August 2025 (art. 157^6). Investment income: final 10 % withholding on
interest and dividends (art. 97 alin. (1), (2), (7)), 1 % on long-held securities sold through a Romanian intermediary
(art. 97 alin. (8^1)), rents 10 % of 80 % (art. 84 alin. (3)), CASS on these in bands of 6/12/24 minimum wages (art.
170 alin. (2)-(4)). Independent activities (sistem real, art. 68): CAS on 12/24 minimum wages (art. 148), CASS on the
net income capped at 60 minimum wages and topped up to 6 (art. 170 alin. (1), art. 174 alin. (6)-(7)), tax 10 % of the
net income after CAS and CASS (art. 118 alin. (2) lit. b)). Child allowance: Legea nr. 61/1993.

Household mapping (stated choices):
* investment income and rents are split equally between two adults (`half1`/`half2`); `"roInvestOwner": "adult1"`
  puts all of it on the first adult;
* both parents count every minor child as a dependant (art. 77 alin. (6)); a spouse is a dependant of the other when
  her or his own monthly income (all kinds, art. 77 alin. (5)) is at most 20 % of the minimum wage;
* the 100 lei per child in education (art. 77 alin. (10) lit. b)) goes to the parent for whom it saves more tax (the
  law lets the parents choose, alin. (12)); children aged `roSchoolMinAge` (default 3, kindergarten) to 17 count;
* the contractual base salary equals the gross wage unless `"roBaseWage"` (monthly lei) is given: with
  `"roBaseWage": 4050` a wage of up to 4.300 lei a month receives the 300 lei of OUG nr. 156/2024;
* `"roDividendYear"`: 2024 (8 %), 2025 (default, 10 %) or 2026 (16 %), the year the dividend is distributed;
  `"roGains"`: `"long"` (default, 1 %), `"short"` (3 %) or `"foreign"` (10 % of the net gain, non-resident broker).
-/

namespace RoTax
open TaxKernel

structure Person where
  age : Nat := 40
  wages : Int := 0
  se : Int := 0
  pension : Int := 0
  interest : Int := 0
  dividends : Int := 0
  gains : Int := 0
  rent : Int := 0
  deriving Repr, Inhabited

def Person.monthlyIncome (p : Person) : Int :=
  (p.wages + p.se + p.pension + p.interest + p.dividends + p.gains + p.rent) / 12

structure Opts where
  divRate : Int := dividendRate2025
  gainRate : Int := gainRateLong
  baseWage : Option Int := none
  schoolMinAge : Nat := 3
  mw : Int := minWage2025
  /-- tax year (2022-2025): the wage law of each month (`lawFor`) and the child allowance -/
  year : Nat := 2025
  /-- `--eurostat` (convention, NOT statute): Eurostat earn_net ESMS 3.4, "Income tax and social security
  contributions parameters refer to the beginning of the fiscal year, i.e. changes occurring later during the year are
  ignored" (tests/data/_methodology/earn_net_esms.htm, sha256 89ab2734...): every month of wages under the law of
  January; pensions without the art. 157^6 CASS that starts in August 2025. The child allowance does not vary within
  ages 6-11 (2-18 band), so ESMS 3.4's "most generous" family-allowance rule changes nothing. -/
  es : Bool := false
  /-- `--euromod` (convention, NOT statute; round 15): EUROMOD's legislative parameters are those in force on 30 June
  of the policy year ("Legislative parameters of the tax system are referred in EM to 30 June": EUROMOD "Nowcasting
  prices" note, Feb 2025, sections 1.3-1.4, sha256 64eb954e350abd1c...; tests/convention_policy.json). The RO country
  report on file (Y16, 2022-2025) states no other treatment for these items. Every month of wages under the law of June
  (2023: 3.000 lei and 200 lei, the October 2023 minimum wage ignored; 2024: 3.300 lei and 200 lei, the July 2024
  minimum wage and 300 lei ignored); pensions without the art. 157^6 CASS that starts in August 2025. -/
  em : Bool := false
  deriving Repr, Inhabited

structure PersonOut where
  wage : WageYear := {}
  pensionCass : Int := 0
  pensionTax : Int := 0
  invTax : Int := 0
  rentTax : Int := 0
  invCassIncome : Int := 0
  invCass : Int := 0
  pfaCas : Int := 0
  pfaCass : Int := 0
  pfaTax : Int := 0
  deriving Repr, Inhabited

def PersonOut.tax (o : PersonOut) : Int := o.wage.tax + o.pensionTax + o.invTax + o.rentTax + o.pfaTax
def PersonOut.social (o : PersonOut) : Int :=
  o.wage.cas + o.wage.cass + o.pensionCass + o.invCass + o.pfaCas + o.pfaCass

/-- art. 170 alin. (3): CASS base for income from art. 155 lit. c)-h): 0, 6, 12 or 24 minimum wages. -/
def invCassBase (mw inc : Int) : Int :=
  if 24 * mw ≤ inc then 24 * mw else if 12 * mw ≤ inc then 12 * mw else if 6 * mw ≤ inc then 6 * mw else 0

/-- art. 148 alin. (2): CAS base for independent activities. -/
def pfaCasBase (mw se : Int) : Int :=
  if casPfaHigh * mw ≤ se then casPfaHigh * mw else if casPfaLow * mw ≤ se then casPfaLow * mw else 0

/-- Investment income and rents of one person: (tax, rent tax, CASS income, CASS). -/
def investment (o : Opts) (p : Person) : Int × Int × Int × Int :=
  let tI := pctOf interestRate (pos p.interest)
  let tD := pctOf o.divRate (pos p.dividends)
  let tG := pctOf o.gainRate (pos p.gains)
  let rentNet := pos p.rent - pctOf rentForfeit (pos p.rent)
  let tR := pctOf taxRate rentNet
  -- art. 170 alin. (4) lit. c), d): interest and dividends "diminuate cu impozitul reținut"
  let inc := (pos p.interest - tI) + (pos p.dividends - tD) + pos p.gains + rentNet
  (tI + tD + tG, tR, inc, pctOf cassRate (invCassBase o.mw inc))

/-- Independent activities in sistem real, net income `se`: (CAS, CASS, tax). `exemptTopUp`: art. 174 alin. (7). -/
def pfa (mw se : Int) (exemptTopUp : Bool) : Int × Int × Int :=
  if se ≤ 0 then (0, 0, 0) else
  let cas := pctOf casRate (pfaCasBase mw se)
  let cassOwn := pctOf cassRate (min se (cassPfaCap * mw))
  let topUp := if exemptTopUp then 0 else pos (pctOf cassRate (cassPfaFloor * mw) - cassOwn)
  -- art. 118 alin. (2) lit. b) and (2^4): CAS and CASS (not the top-up) deducted, at most the net income
  let taxable := pos (se - min se (cas + cassOwn))
  (cas, cassOwn + topUp, pctOf taxRate taxable)

/-- Everything for one person; `deps`, `young`, `school` feed the wage deduction. -/
def personCalc (o : Opts) (p : Person) (deps school : Nat) : PersonOut :=
  let baseOf : Int → Int := fun g => o.baseWage.getD g
  let law : Nat → MonthLaw := if o.year ≥ 2025 then law2025 else lawFor o.year
  let w := wageYear (if o.es then (fun _ => law 1) else if o.em then (fun _ => law 6) else law) p.wages baseOf deps
    (decide (p.age < youngAge))
    (if o.year ≤ 2022 then 0 else school)
  let (pc, pt) := pensionYear p.pension (if o.es || o.em then 13 else pensionCassFirstMonth)
  let (it, rt, ci, cc) := investment o p
  let exempt := decide (cassPfaFloor * o.mw ≤ p.wages) || decide (cassPfaFloor * o.mw ≤ invCassBase o.mw ci)
    || decide (0 < p.pension)
  let (fc, fs, ft) := pfa o.mw p.se exempt
  { wage := w, pensionCass := pc, pensionTax := pt, invTax := it, rentTax := rt, invCassIncome := ci,
    invCass := cc, pfaCas := fc, pfaCass := fs, pfaTax := ft }

/-- Legea nr. 61/1993 art. 3: allowance for one child for a year. -/
def childAllowance (age : Nat) : Int :=
  if age < 2 then 12 * allowanceUnder2 else if age < minorAge then 12 * allowance2to18 else 0

/-- The same for tax year `y` (`allowanceUnder2Y`, `allowance2to18Y`). -/
def childAllowanceY (y age : Nat) : Int :=
  if y ≥ 2025 then childAllowance age else
  if age < 2 then 12 * allowanceUnder2Y y else if age < minorAge then 12 * allowance2to18Y y else 0

def optsOf (c : Canon) : Opts :=
  { divRate := (match c.int? "roDividendYear" with
      | some 2024 => dividendRate2024
      | some 2026 => dividendRate2026
      | some y => dividendRateForYear y.toNat
      | none => dividendRateForYear c.year),
    gainRate := (match c.str? "roGains" with
      | some "short" => gainRateShort
      | some "foreign" => taxRate
      | _ => gainRateLong),
    baseWage := c.int? "roBaseWage",
    schoolMinAge := ((c.int? "roSchoolMinAge").getD 3).toNat,
    year := c.year,
    mw := if c.year ≥ 2025 then minWage2025 else (lawFor c.year 1).mw }

def outWith (args : List String) (c : Canon) : Out :=
  let o := { optsOf c with es := args.contains "--eurostat", em := args.contains "--euromod" }
  let allToFirst := c.str? "roInvestOwner" == some "adult1"
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int :=
    if decide (n ≤ 1) || allToFirst then (if i == 0 then x else 0) else (if i == 0 then half1 x else half2 x)
  let persons : List Person := (c.adults.zip (List.range n)).map fun (a, i) =>
    { age := a.age, wages := a.wages, se := a.selfEmployment, pension := a.pension,
      interest := share c.interest i, dividends := share c.dividends i, gains := share c.capitalGains i,
      rent := share c.rentalIncome i }
  let minors := c.childrenUnder minorAge
  let school := (c.children.filter fun k => o.schoolMinAge ≤ k.age ∧ k.age < minorAge).length
  -- dependants of person i: the minor children plus a low-income spouse (art. 77 alin. (5)-(7))
  let depsOf (i : Nat) : Nat :=
    let spouseDep : Bool := (match persons[1 - i]? with
      | some q => n == 2 && c.married && decide (i < 2) &&
          decide (q.monthlyIncome ≤ (if o.year ≤ 2022 then dependantLimit2022 else pctOf dependantPct o.mw))
      | none => false)
    minors + cond spouseDep (1 : Nat) 0
  let runAll (schoolTo : Nat) : List PersonOut :=
    (persons.zip (List.range n)).map fun (p, i) => personCalc o p (depsOf i) (if i == schoolTo then school else 0)
  let optA := runAll 0
  let optB := runAll 1
  let totTax (l : List PersonOut) := sumInts (l.map PersonOut.tax)
  let (res, schoolTo) := if n == 2 && school > 0 && totTax optB < totTax optA then (optB, 1) else (optA, 0)
  let tax := totTax res
  let social := sumInts (res.map PersonOut.social)
  let ben := sumInts (c.children.map fun k => childAllowanceY o.year k.age)
  let get (f : PersonOut → Int) : Int := sumInts (res.map f)
  Out.make c "RO" "RON" tax (employeeSocial := social) (benefits := ben)
    (detail := [Out.d "wageTax" (get fun r => r.wage.tax), Out.d "wageCAS" (get fun r => r.wage.cas),
      Out.d "wageCASS" (get fun r => r.wage.cass), Out.d "personalDeduction" (get fun r => r.wage.ded),
      Out.d "untaxed300" (get fun r => r.wage.untaxed),
      Out.d "pensionTax" (get PersonOut.pensionTax), Out.d "pensionCASS" (get PersonOut.pensionCass),
      Out.d "investmentTax" (get PersonOut.invTax), Out.d "rentTax" (get PersonOut.rentTax),
      Out.d "investmentCASS" (get PersonOut.invCass), Out.d "pfaCAS" (get PersonOut.pfaCas),
      Out.d "pfaCASS" (get PersonOut.pfaCass), Out.d "pfaTax" (get PersonOut.pfaTax),
      Out.d "dependantsAdult1" (depsOf 0), Out.d "schoolChildrenTo" schoolTo,
      Out.d "taxableIncome" (get fun r => r.wage.base),
      Out.dStr "note" "monthly final wage tax (art. 78), each month under its own law (lawFor year month)"])
    (unsupported := ["employer CAM 2.25 % and the employer's part-time CAS/CASS top-up (art. 146 alin. (5^9))",
      "disability (art. 60 pct. 1) and R&D (art. 60 pct. 3) exemptions",
      "meal tickets, holiday vouchers, benefits in kind",
      "voluntary pension/health deductions (art. 78 alin. (2) lit. a) (iii)-(v))",
      "income norms (art. 69), IP income (art. 72-73), second jobs (art. 78 alin. (2) lit. b))",
      "child allowance for disabled children and pupils over 18"] ++
      (if c.year < 2025 then ["tax year " ++ toString c.year ++ ": wages (minimum wage, non-taxable sum, art. 77 deduction), CAS/CASS and the child allowance are year-specific; pensions (art. 100 allowance, no CASS before August 2025), investment and rental CASS bands (with that year's January minimum wage) and PFA rules are the 2025 ones; dividends: 8 % in 2023-2024 (art. 97 alin. (7), OG nr. 16/2022), the 2022 rate is not cited and the 2025 rate is used" ] else []) ++
      (if c.year < 2022 then ["tax year before 2022: computed with the 2022 law"] else []) ++
      (if o.es then ["--eurostat: Eurostat earn_net ESMS 3.4 convention, not statute (January's wage law all year; no pension CASS before the year's start rule)"] else []) ++
      (if o.em then ["--euromod: EUROMOD 30 June convention, not statute (June's wage law all year; no pension CASS from August 2025)"] else []))

def out (c : Canon) : Out := outWith [] c

def country : Country :=
  { code := "RO", name := "Romania", currency := "RON", year := "2025", compute := out, computeWith := outWith }

end RoTax
