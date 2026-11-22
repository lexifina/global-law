import LvTax.Params

/-!
# Latvia 2025: the household computation (IIN, VSAOI, solidarity tax, family benefit)

Individual assessment (IIN 3. panta 1. daļa: the tax unit is the resident person; no joint return). Per person:

1. **Income at progressive rates** `G` (15. panta 2. daļa): wages + self-employment profit (general regime) +
   pension. Capital income (15. panta 5. daļa, 25,5 %), rent without a registered business (15(6)(3), 10 %) and
   dividends exempt under 9. panta 1. daļas 2.1 punkts are taxed apart.
2. **Deductions** `D` (3. panta 2. daļa): attaisnotie izdevumi (10. pants: own VSAOI and solidarity tax, less the
   IIN share of the solidarity tax under 10(1.10); donations and medical/education within 10(1.3); private pension
   within 10(1.9)), the neapliekamais minimums (12. pants, 510 euro a month; 1 000 for a pensioner) and the
   dependants' relief (13. pants, 250 euro a month per dependant).
3. **Tax** = 25,5 % / 33 % schedule on `G` minus 25,5 % of `min D G` (`iinTicks`): 3. panta 2.4 daļa takes the
   deductions from the income up to the maximum object first, and 15. panta 15. daļa reduces the tax for the part
   above by "atskaitījumu summu ... reizinot ar nodokļa likmi 25,5 procentu apmērā". Up to deductions of 105 300
   euro this is the kernel's allowance-given-at-the-lowest-rates (`taxAfterLowBand`, as BE CIR 92 art. 131).
4. **3 % additional rate** (15.1 pants) on all income above 200 000 euro, exempt dividends included.
5. **VSAOI** 10,5 % on wages up to 105 300 euro and the same rate above it as solidarity tax (only the employer is
   refunded: Solidaritātes nodokļa likums 6.2(3)); self-employed 31,07 % / 10 % (VSAOI 14.1 pants).
6. **Ģimenes valsts pabalsts** (VSPL 6. pants) per family by the number of children aged 1-15 (to 19 at school).

Elections and options read from the input line (extension fields; defaults in brackets):
* `"lvSeRegime"`: `"general"` | `"micro"` (mikrouzņēmumu nodoklis, 25 % of turnover; the contract's
  selfEmployment is read as turnover) | `"royalty"` (author's royalties, PN 163-171, 25 % final) [general];
* `"childrenInEducation"`: children 16-19 at school (benefit) and 18-23 in education (relief) [true];
* `"lvPensioner"`: grant the pensioner's minimum without pension income [false];
* `"lvSeMonths"`: the number of months (1-12) in which the self-employment profit is received, evenly [12].
The dependants' relief is given to whichever parent makes the family's tax lowest (13. panta 1. daļas 1. punkts:
"vienam no apgādniekiem"): every split of the children is tried.
-/

namespace LvTax
open TaxKernel

/-- Ticks (cents × bp) to cents, half up (the declaration works to the cent). -/
def cents (t : Int) : Int := divR .halfUp t BP
/-- Cents to whole euros, half up (the contract's unit; not a statutory rounding). -/
def toEur (c : Int) : Int := divR .halfUp c 100

/-- One person's inputs, in cents. `regime`: 0 general, 1 micro-enterprise tax, 2 royalty regime. -/
structure Person where
  wages : Int := 0
  se : Int := 0
  pension : Int := 0
  pensioner : Bool := false
  interest : Int := 0
  gains : Int := 0
  rent : Int := 0
  divs : Int := 0
  donations : Int := 0
  pensionContrib : Int := 0
  regime : Nat := 0
  seMonths : Nat := 12
  year : Nat := 2025
  deriving Repr, Inhabited

/-- One person's results, in cents. -/
structure Res where
  gross15 : Int := 0
  deductions : Int := 0
  taxable : Int := 0
  iin : Int := 0
  capTax : Int := 0
  rentTax : Int := 0
  surtax : Int := 0
  micro : Int := 0
  royaltyIin : Int := 0
  vsaoi : Int := 0
  solid : Int := 0
  seSoc : Int := 0
  royaltySoc : Int := 0
  deriving Repr, Inhabited

/-- Employee VSAOI up to the maximum object (VSAOI 14(1), 14(5), 18(1), 20(2)). -/
def eeVsaoi (rate w : Int) : Int := cents ((Contribution.flatCapped "VSAOI" rate maxObject).ticks (pos w))
/-- The employee's share of the solidarity tax on wages above the maximum object (Solidaritātes nodokļa likums
3. pants, 6.2 panta 1. un 3. daļa: the rate stays the contribution rate for the employee; only the employer is
refunded). -/
def eeSolid (rate w : Int) : Int := cents (rate * pos (w - maxObject))
/-- IIN 10. panta 1.10 daļa: the deductible contributions are reduced by the IIN share of the solidarity tax
(10 percentage points of its object, Solidaritātes nodokļa likums 8.1 panta 3. punkts). -/
def solidIinPart (w : Int) : Int := cents (solidIinShare * pos (w - maxObject))

/-- Self-employed VSAOI (VSAOI 14.1 pants, a monthly test), the year's profit `se` received evenly in `n` months
(1-12): in a month with income below the minimum wage 10 % of the income; in a month at or above it 31,07 % of the
minimum wage (the lowest object the person may choose) and 10 % of the rest. -/
def seVsaoiMonths (n : Nat) (se : Int) : Int :=
  let k : Int := max 1 (min 12 (n : Int))
  if k * minWage ≤ se then cents (seFullRate * (k * minWage) + sePensionRate * (se - k * minWage))
  else cents (sePensionRate * pos se)

/-- The default: profit received evenly over the 12 months. -/
def seVsaoi (se : Int) : Int := seVsaoiMonths 12 se

/-- IIN at the progressive rates (ticks) on income `g` with deductions `d`: the 25,5 / 33 % schedule on the income,
less 25,5 % of the deductions (never below 0). 3. panta 2.4 daļa takes the deductions from the income up to the
maximum object first; 15. panta 15. daļa: the part above is taxed at 33 % "bet aprēķināto nodokļa apmēru samazina
par nodokli, kurš aprēķināts, atskaitījumu summu, kas pārsniedz ... maksimālo apmēru, reizinot ar nodokļa likmi
25,5 procentu apmērā". So every euro of deduction is worth 25,5 %, whatever the income: for `d ≤ 105 300` this is
the kernel's `taxAfterLowBand` (`Theorems.iin_eq_lowband`). -/
def iinTicks (d g : Int) : Int := pos (iinSched.ticks g - wageRate * min (pos d) (pos g))

/-- The same for any year 2022-2025 (2022-2024: the 20 / 23 / 31 % schedule less 20 % of the deductions). -/
def iinTicksY (y : Nat) (d g : Int) : Int := pos ((schedFor y).ticks g - lowRateFor y * min (pos d) (pos g))

def eeVsaoiY (y : Nat) (rate w : Int) : Int := cents ((Contribution.flatCapped "VSAOI" rate (maxObjectFor y)).ticks (pos w))
def eeSolidY (y : Nat) (rate w : Int) : Int := cents (rate * pos (w - maxObjectFor y))
def solidIinPartY (y : Nat) (w : Int) : Int := cents (solidIinShare * pos (w - maxObjectFor y))

/-- The person's tax with `reliefs` (cents a year: dependants and non-working spouse, 13. pants). -/
def personRes (p : Person) (reliefs : Int) : Res :=
  let seGen := if p.regime = 0 then pos p.se else 0
  let g := pos p.wages + seGen + pos p.pension
  let pens := p.pension > 0 || p.pensioner
  let rate := if pens then eeRatePensioner else eeRate
  let vs := eeVsaoiY p.year rate p.wages
  let so := eeSolidY p.year rate p.wages
  let ss := if p.regime = 0 then seVsaoiMonths p.seMonths seGen else 0
  let contribs := vs + so - solidIinPartY p.year p.wages + ss
  let ntm := if pens then ntmPensionerFor p.year else ntmFor p.year (g + pos p.interest + pos p.gains + pos p.rent)
  let don := min (pos p.donations) (min donationCap (cents (donationPct * pos (g - contribs))))
  let pc := min (pos p.pensionContrib) (min pensionCap (cents (pensionPct * g)))
  let d := contribs + don + pc + ntm + pos reliefs
  let iin := cents (iinTicksY p.year d g)
  let capTax := cents (capitalRateFor p.year * pos (p.interest + p.gains))
  let rentTax := cents (rentRate * pos p.rent)
  let micro := if p.regime = 1 then cents (microRate * pos p.se) else 0
  let roy := if p.regime = 2 then cents (royaltyRate * pos p.se) else 0
  let roySoc := cents (royaltySocialShare * roy)
  let base := g + pos p.interest + pos p.gains + pos p.rent + pos p.divs
  let sur := if hasSurtax p.year then cents (surtax.ticks base) else 0
  { gross15 := g, deductions := d, taxable := pos (g - d), iin, capTax, rentTax, surtax := sur, micro,
    royaltyIin := roy - roySoc, vsaoi := vs, solid := so, seSoc := ss, royaltySoc := roySoc }

/-- All the person's income taxes (cents): IIN at progressive, capital and rent rates, the IIN part of the
royalty regime, the 3 % additional rate and the micro-enterprise tax. -/
def Res.taxes (r : Res) : Int := r.iin + r.capTax + r.rentTax + r.royaltyIin + r.surtax + r.micro
/-- All the person's contributions (cents). -/
def Res.social (r : Res) : Int := r.vsaoi + r.solid + r.seSoc + r.royaltySoc

/-- Monthly withholding on wages (IIN 15. panta 3. daļa, 12. panta 1. daļa, 13. panta 1.2 daļa, 10. panta 2. daļa:
the month's own contributions are deducted), salary paid in 12 equal months, tax book at this employer. -/
def withheld (w : Int) (ntmM : Int) (reliefsYear : Int) : Int :=
  let wm := divR .halfUp (pos w) 12
  let ssm := cents (eeRate * wm)
  12 * cents (wageRate * pos (wm - ssm - ntmM - divR .down (pos reliefsYear) 12))

def regimeOf (c : Canon) : Nat :=
  match c.str? "lvSeRegime" with
  | some "micro" => 1
  | some "royalty" => 2
  | _ => 0

def inEdu (c : Canon) : Bool := (c.bool? "childrenInEducation").getD true

/-- VSPL 6. panta 2. daļa: a child aged 1 to 15, or 16 to 19 at a general or vocational school. -/
def benefitChild (edu : Bool) (age : Nat) : Bool := (1 ≤ age && age < 16) || (edu && 16 ≤ age && age < 20)
/-- IIN 13. panta 1. daļas 1. punkts a), b): a minor child, or a child in education up to 24. -/
def reliefChild (edu : Bool) (age : Nat) : Bool := age < 18 || (edu && 18 ≤ age && age < 24)

/-- Number of children for whom the family benefit is paid. -/
def nBenefit (c : Canon) : Nat := (c.children.filter fun k => benefitChild (inEdu c) k.age).length
/-- Number of children who give the dependants' relief. -/
def nRelief (c : Canon) : Nat := (c.children.filter fun k => reliefChild (inEdu c) k.age).length

/-- IIN 13. panta 1. daļas 1. punkts l), m), n): a non-working spouse who has in their care a child under 3, or
three or more children (under 18, or to 24 in education) at least one under 7, or five children. -/
def spouseChildTest (c : Canon) : Bool :=
  let ks := c.children.filter fun k => reliefChild (inEdu c) k.age
  c.children.any (fun k => k.age < 3) || (ks.length ≥ 3 && ks.any (fun k => k.age < 7)) || ks.length ≥ 5

/-- A spouse who can be a dependant: married, no wages, self-employment or pension (13. panta 1. daļas
1. punkts: "ja šai personai nav piešķirta pensija"; "nestrādājošu laulāto"; 7. daļa: not registered in business),
own taxable income not above the relief (13. panta 3. un 6. daļa: 3 000 euro a year). -/
def dependentSpouse (c : Canon) (a : Adult) (inv : Int) : Bool :=
  c.married && a.wages == 0 && a.selfEmployment == 0 && a.pension == 0 && inv ≤ depYear && spouseChildTest c

def mkPerson (c : Canon) (a : Adult) (share : Int → Int) : Person :=
  { wages := eur a.wages, se := eur a.selfEmployment, pension := eur a.pension,
    pensioner := (c.bool? "lvPensioner").getD false,
    interest := eur (share c.interest), gains := eur (share c.capitalGains), rent := eur (share c.rentalIncome),
    divs := eur (share c.dividends), donations := eur (share c.charitable),
    pensionContrib := eur (share c.pensionContributions), regime := regimeOf c,
    seMonths := ((c.int? "lvSeMonths").getD 12).toNat, year := c.year }

/-- The persons of the household (investment income and deductible payments split half/half in a couple,
the first adult taking the odd euro: contract). -/
def persons (c : Canon) : List Person :=
  match c.adults with
  | [a] => [mkPerson c a id]
  | a :: b :: _ => [mkPerson c a half1, mkPerson c b half2]
  | [] => []

/-- Household result for a given split: adult 1 gets `j` children's reliefs (and the spouse relief `s1`), adult 2
the rest. -/
def splitRes (c : Canon) (j : Nat) : List Res :=
  let k := nRelief c
  match c.adults, persons c with
  | [_], [p] => [personRes p (depYear * k)]
  | a :: b :: _, p :: q :: _ =>
    let invB := half2 c.interest + half2 c.capitalGains + half2 c.rentalIncome
    let invA := half1 c.interest + half1 c.capitalGains + half1 c.rentalIncome
    let s1 := if dependentSpouse c b invB then depYear else 0
    let s2 := if dependentSpouse c a invA then depYear else 0
    [personRes p (depYear * (min j k) + s1), personRes q (depYear * (k - min j k) + s2)]
  | _, _ => []

def totalTaxes (rs : List Res) : Int := sumInts (rs.map Res.taxes)

/-- The split of the children's reliefs that makes the household's income tax lowest (first found on ties). -/
def bestJ (c : Canon) : Nat :=
  if c.adults.length < 2 then nRelief c
  else
    (List.range (nRelief c + 1)).foldl
      (fun best j => if totalTaxes (splitRes c j) < totalTaxes (splitRes c best) then j else best) (nRelief c)

def out (c : Canon) : Out :=
  let j := bestJ c
  let rs := splitRes c j
  let ps := persons c
  let s (f : Res → Int) := sumInts (rs.map f)
  let iinAll := s (fun r => r.iin + r.capTax + r.rentTax + r.royaltyIin)
  let ben := 12 * fvpMonth (nBenefit c)
  let k := nRelief c
  -- withholding comparison for wage earners (detail only)
  let wh := match ps, rs with
    | [p], [_] => withheld p.wages (if p.pension > 0 || p.pensioner then ntmPensioner / 12 else ntmMonth) (depYear * k)
    | p :: q :: _, _ :: _ :: _ =>
      withheld p.wages ntmMonth (depYear * min j k) + withheld q.wages ntmMonth (depYear * (k - min j k))
    | _, _ => 0
  let wageOnly := ps.all (fun p => p.se == 0 && p.pension == 0 && !p.pensioner && p.donations == 0 &&
    p.pensionContrib == 0)
  Out.make c "LV" "EUR" (toEur iinAll)
    (surtaxes := [("additionalRate3pct", toEur (s Res.surtax)), ("microenterpriseTax", toEur (s Res.micro))])
    (employeeSocial := toEur (s Res.social)) (benefits := toEur ben)
    (detail := [Out.d "taxableIncome" (toEur (s Res.taxable)), Out.d "taxBeforeCredits" (toEur (s Res.iin)),
      Out.d "incomeAtProgressiveRates" (toEur (s Res.gross15)), Out.d "deductions" (toEur (s Res.deductions)),
      Out.d "capitalIncomeTax" (toEur (s Res.capTax)), Out.d "rentTax" (toEur (s Res.rentTax)),
      Out.d "employeeVSAOI" (toEur (s Res.vsaoi)), Out.d "solidarityTaxEmployee" (toEur (s Res.solid)),
      Out.d "selfEmployedVSAOI" (toEur (s Res.seSoc)), Out.d "royaltyRegime" (toEur (s (fun r => r.royaltyIin + r.royaltySoc))),
      Out.d "familyBenefit" (toEur ben), Out.d "childrenReliefAdult1" (min j k),
      Out.d "withheldOnWages" (if wageOnly then toEur wh else 0),
      Out.d "annualSettlement" (if wageOnly then toEur (s Res.iin - wh) else 0)])
    (unsupported := ["dividends assumed paid from profit taxed under the UIN likums (9. panta 1. daļas 2.1 punkts: exempt); from low-tax jurisdictions not modelled",
      "self-employment income assumed spread evenly over the months (VSAOI 14.1 pants is monthly); minimum quarterly contributions (VSAOI 20.4 pants) assumed avoided by a planned-income declaration",
      "a working pensioner is read from pension > 0 or lvPensioner (VSAOI 9,25 %); izdienas pensija (9,76 %) and disability reliefs (13. panta 1. daļas 4. punkts) not modelled",
      "medical/education expenses (10. panta 1. daļas 2. punkts) not in the contract; property tax deduction from rent not modelled"]
      ++ (if c.year ≤ 2024 then ["2022-2024: self-employed minimum-wage test, micro and royalty regimes, solidarity-tax IIN share and the withholding detail use the 2025 amounts; 2022 half-year incomes taken as half the year's"] else []))

def country : Country :=
  { code := "LV", name := "Latvia", currency := "EUR", year := "2025", compute := out }

end LvTax
