import FiTax.Params

/-!
# Finland 2025: one person's assessment, provision by provision (cents)

Order of the assessment (TVL):
1. net earned income (puhdas ansiotulo): earned income − tulonhankkimisvähennys (95 §);
2. deductions from net earned income in state *and* municipal taxation (chapter heading before 96 §, "Puhtaasta
   ansiotulosta valtion- ja kunnallisverotuksessa tehtävät vähennykset"): compulsory contributions (96 §),
   eläketulovähennys (100 §), perusvähennys (106 §, "edellä mainittujen vähennysten jälkeen") → taxable earned income,
   the same base for state tax, municipal tax, church tax and the health-care contribution (sairaanhoitomaksu);
   the ansiotulovähennys (105 a §) was repealed by 702/2024 from 2025;
3. state tax by the 2025 scale (Asteikkolaki 701/2024) + eläketulon lisävero (124 § 4 mom);
4. työtulovähennys (125 §) first against the state earned-income tax, the rest against municipal tax,
   sairaanhoitomaksu and church tax "näiden verojen suhteessa";
5. capital income tax 30/34 % (124 § 2 mom); alijäämähyvitys (131-134 §);
6. yleisradiovero (separate act), employee contributions.
Rounding: every tax is computed exactly in cent × basis points and rounded half up to the cent (convention: the
statute does not say; it reproduces the OECD's and Kela's published cents).
-/

namespace FiTax
open TaxKernel

/-- `bp` of `x` cents, rounded half up to the cent. -/
def pctOf (bp x : Int) : Int := divR .halfUp (bp * x) BP

/-- One adult's facts (amounts in cents). -/
structure Person where
  age : Nat := 40
  wages : Int := 0
  selfEmp : Int := 0
  pension : Int := 0
  /-- earned-income part of unlisted dividends (TVL 33 b § 2 mom) -/
  earnedDiv : Int := 0
  /-- net capital income (may be negative: a deficit, TVL 60 §) -/
  capital : Int := 0
  /-- minor children of whom the person is a guardian at the end of the year (TVL 125 § 4 mom) -/
  kids : Nat := 0
  /-- no spouse in the sense of the TVL and sole guardian (doubles the child increase) -/
  sole : Bool := false
  /-- an owner-manager insured under YEL (yrittäjän eläkelaki), not TyEL: no employee TyEL or unemployment
  contribution on the salary (the YEL contribution itself is not modelled) -/
  yel : Bool := false
  deriving Repr, Inhabited

/-- Rates that depend on the municipality and congregation. -/
structure Rates where
  municipal : Int := helsinkiRate
  church : Int := 0
  deriving Repr, Inhabited

/-- Earned income from work (the base of the työtulovähennys, TVL 125 § 1 mom: palkkatulot, other work income,
"ansiotulona verotettavan osingon"). -/
def Person.work (p : Person) : Int := p.wages + p.selfEmp + p.earnedDiv

/-- TVL 95 § 1 mom 1 k: 750 €, at most the wages. -/
def expenseDed (p : Person) : Int := min (pos p.wages) expenseDeduction

/-- Net earned income, puhdas ansiotulo (TVL 30 §; no actual expenses claimed). -/
def netEarned (p : Person) : Int := p.wages - expenseDed p + p.selfEmp + p.pension + p.earnedDiv

/-! ## Employee contributions (deductible, TVL 96 §) -/

/-- A flat employee contribution on the whole base (kernel `Contribution`, no ceiling), rounded half up to the cent. -/
def flatContribution (name : String) (rate : Int) : Contribution :=
  { name, sched := Schedule.flat rate, round := Rule.unitHalfUp }

/-- TyEL employee contribution, 7,15 % (8,65 % at 53-62), on wages; ages 17-67 (insurance obligation from 17,
its end depends on the year of birth: 68 for the cohorts in working age). -/
def tyel (p : Person) : Int :=
  if p.yel || p.age < 17 || p.age ≥ 68 then 0
  else (flatContribution "TyEL" (if 53 ≤ p.age ∧ p.age ≤ 62 then tyelRate53 else tyelRate)).amount p.wages

/-- Employee unemployment insurance contribution 0,59 %, ages 18-64. -/
def unemployment (p : Person) : Int :=
  if p.yel || p.age < 18 || p.age ≥ 65 then 0 else (flatContribution "työttömyysvakuutusmaksu" unemploymentRate).amount p.wages

/-- The daily-allowance base: wages and self-employment income (sairausvakuutuslaki 18:15). -/
def dailyBase (p : Person) : Int := pos p.wages + pos p.selfEmp

/-- Päivärahamaksu 0,84 % of the whole base, nothing below 16 862 €: a kernel `Contribution` with an
all-or-nothing floor (a notch: `Theorems.daily_notch`). -/
def dailyContribution : Contribution :=
  { name := "päivärahamaksu", sched := Schedule.flat dailyAllowanceRate, floor := dailyAllowanceLimit,
    round := Rule.unitHalfUp }

def dailyAllowance (p : Person) : Int := if p.age ≥ 68 then 0 else dailyContribution.amount (dailyBase p)

/-- The deductible contributions of TVL 96 § 1 mom. -/
def contributions (p : Person) : Int := tyel p + unemployment p + dailyAllowance p

/-! ## Deductions from net earned income -/

/-- TVL 100 §: eläketulovähennys = full amount (11 030 €), at most the pension, less 51 % / 19,6 % of the net earned
income above the full amount. -/
def pensionDed (p : Person) : Int :=
  if p.pension ≤ 0 then 0
  else pos (min p.pension pensionDeductionFull - pensionReduction.tax Rule.unitHalfUp (netEarned p))

/-- Income left after the deductions that come before the perusvähennys. -/
def beforeBasic (p : Person) : Int := pos (netEarned p - contributions p - pensionDed p)

/-- TVL 106 §: perusvähennys = min(income, 4 115 − 18 % of the income above 4 115). -/
def basicDed (inc : Int) : Int := min (pos inc) (basicTaper.amount inc)

/-- Taxable earned income (verotettava ansiotulo), the same in state and municipal taxation. -/
def taxableEarned (p : Person) : Int := pos (beforeBasic p - basicDed (beforeBasic p))

/-! ## Taxes before credits -/

/-- State tax on taxable earned income (Asteikkolaki 701/2024). -/
def stateTax (ti : Int) : Int := stateSchedule.tax Rule.unitHalfUp ti

/-- Eläketulon lisävero (TVL 124 § 4 mom): 5,85 % of pension − eläketulovähennys above 47 000 €. -/
def pensionSurtax (p : Person) : Int :=
  pctOf pensionSurtaxRate (pos (p.pension - pensionDed p - pensionSurtaxThreshold))

/-- Municipal tax (TVL 130 §; none if the income is under 10 €). -/
def municipalTax (r : Rates) (ti : Int) : Int := if ti < municipalMinIncome then 0 else pctOf r.municipal ti

/-- Sairaanhoitomaksu: 1,06 % of the taxable earned income, + 0,39 % of the part above the daily-allowance base. -/
def medical (p : Person) (ti : Int) : Int :=
  pctOf medicalRate ti + pctOf medicalExtraRate (pos (ti - dailyBase p))

/-- TVL 125 §: työtulovähennys = min(18 % of work income, 3 225 € + increases) − 2,22 % / 3,44 % of the net earned
income above 24 250 / 42 550 €, never below 0. `age` is the age at the end of 2025: "täyttänyt 65 vuotta ennen
verovuoden alkua" ⇔ age ≥ 66. -/
def workCreditMaxOf (p : Person) : Int :=
  workCreditMax + (if p.age ≥ 66 then workCreditAge65 else 0)
    + workCreditChild * p.kids * (if p.sole then 2 else 1)

def workCredit (p : Person) : Int :=
  pos (min (pctOf workCreditRate (pos p.work)) (workCreditMaxOf p) - workCreditTaper.tax Rule.unitHalfUp (netEarned p))

/-- Capital income tax (TVL 124 § 2 mom). -/
def capitalTax (p : Person) : Int := capitalSchedule.tax Rule.unitHalfUp (pos p.capital)

/-- Yleisradiovero (2 §): 2,5 % of net earned + net capital income above 15 150 €, at most 160 €; from age 18. -/
def yleLevy : Surcharge :=
  { rate := yleRate, exempt := yleThreshold, deduct := yleThreshold, round := Rule.unitHalfUp }

def yleBase (p : Person) : Int := netEarned p + pos p.capital

def yle (p : Person) : Int := if p.age < 18 then 0 else min yleMax (yleLevy.amount (yleBase p))

/-! ## Credits against several taxes -/

/-- The taxes a credit can be set against. -/
structure Taxes where
  state : Int
  municipal : Int
  medical : Int
  church : Int
  deriving Repr, Inhabited, DecidableEq

def Taxes.others (t : Taxes) : Int := t.municipal + t.medical + t.church
def Taxes.total (t : Taxes) : Int := t.state + t.others

/-- Deduct `l` from municipal tax, sairaanhoitomaksu and church tax "näiden verojen suhteessa" (TVL 125 § 1 mom,
133 §), never more than they hold; the cent left by rounding goes to the church tax, then nowhere. -/
def spread (t : Taxes) (l : Int) : Taxes :=
  let tot := t.others
  if tot ≤ 0 then t else
  let l := min (pos l) tot
  let dm := min t.municipal (divR .halfUp (l * t.municipal) tot)
  let dh := min t.medical (divR .halfUp (l * t.medical) tot)
  let dk := min t.church (pos (l - dm - dh))
  { t with municipal := t.municipal - dm, medical := t.medical - dh, church := t.church - dk }

/-- TVL 125 § 1 mom: the work income credit "valtiolle suoritettavasta tuloverosta"; the excess from the other
taxes in proportion. Not refundable: what the four taxes cannot absorb is lost. -/
def applyWorkCredit (t : Taxes) (w : Int) : Taxes :=
  let used := min (pos t.state) (pos w)
  spread { t with state := t.state - used } (pos w - used)

/-- TVL 132-133 §: the deficit credit; at most three quarters from the state earned-income tax alone, the rest from
state, municipal, sairaanhoitomaksu and church tax in proportion. Returns the taxes and the unused credit. -/
def applyDeficit (t : Taxes) (a : Int) : Taxes × Int :=
  let a := pos a
  let first := min (pos t.state) ((3 * a) / 4)
  let t1 := { t with state := t.state - first }
  let rest := a - first
  let tot := pos t1.total
  let r := min rest tot
  if tot = 0 then (t1, rest) else
  let ds := min t1.state (divR .halfUp (r * t1.state) tot)
  (spread { t1 with state := t1.state - ds } (r - ds), rest - r)

/-- Everything one person owes before the deficit credit. -/
structure Stage where
  netEarned : Int
  contributions : Int
  tyel : Int
  unemployment : Int
  daily : Int
  pensionDed : Int
  basicDed : Int
  taxable : Int
  stateBefore : Int
  pensionSurtax : Int
  workCredit : Int
  afterWork : Taxes
  capitalTax : Int
  yle : Int
  deriving Repr, Inhabited

def stage (r : Rates) (p : Person) : Stage :=
  let ti := taxableEarned p
  let s0 := stateTax ti + pensionSurtax p
  let t0 : Taxes := { state := s0, municipal := municipalTax r ti, medical := medical p ti,
                      church := if ti < municipalMinIncome then 0 else pctOf r.church ti }
  let w := workCredit p
  { netEarned := netEarned p, contributions := contributions p, tyel := tyel p, unemployment := unemployment p,
    daily := dailyAllowance p, pensionDed := pensionDed p, basicDed := basicDed (beforeBasic p), taxable := ti,
    stateBefore := s0, pensionSurtax := pensionSurtax p, workCredit := w, afterWork := applyWorkCredit t0 w,
    capitalTax := capitalTax p, yle := yle p }

/-- The deficit credit a person is entitled to (TVL 131 § 1 mom), before any spouse transfer: 30 % of the deficit,
at most 1 400 € + the child increase `inc`. Returns (credit, the uncapped 30 % share). -/
def deficitCredit (p : Person) (inc : Int) : Int × Int :=
  let share := pctOf deficitRate (pos (-p.capital))
  (min share (deficitMax + inc), share)

/-- The child increase of the deficit-credit maximum (131 § 1 mom), for `n` minor children. -/
def deficitChildInc (n : Nat) : Int := if n = 0 then 0 else if n = 1 then deficitChild1 else deficitChild2

/-- A person's final result. -/
structure Result where
  st : Stage
  final : Taxes
  capitalTax : Int
  deficitUsed : Int
  deficitLost : Int
  deriving Repr, Inhabited

/-- State income tax actually payable (earned + capital, after credits). -/
def Result.stateTotal (x : Result) : Int := x.final.state + x.capitalTax
def Result.employee (x : Result) : Int := x.st.contributions + x.final.medical
def Result.local (x : Result) : Int := x.final.municipal + x.final.church

end FiTax
