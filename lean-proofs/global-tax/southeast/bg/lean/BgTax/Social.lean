import BgTax.Params

/-!
# Employee and self-insured contributions (КСО, ЗЗО), month by month

КСО чл. 6, ал. 3: contributions of employees are due on "получените, включително начислените и неизплатените, брутни
месечни възнаграждения", capped by the **monthly** maximum insurable income of the ДОО budget act (ЗБДОО 2025 чл. 9:
3 750 лв. in January-March, 4 130 лв. from April). An annual wage is paid as twelve equal monthly wages (the first
`annual % 12` stotinki go one per month to the first months, the kernel's `perPeriod` convention), each fund is
computed on the capped month and rounded half up to the stotinka (payroll convention; the statute fixes no rounding
step for contributions), and the year is the sum. Every fund is a kernel `Contribution` (flat rate, ceiling).

Several insured activities share one ceiling (КСО чл. 6, ал. 11: "върху сбора от осигурителните им доходи, но върху
не повече от максималния месечен размер на осигурителния доход"), employment first.
-/

namespace BgTax
open TaxKernel

/-- Half up to the stotinka. -/
def stRound : Rule := Rule.unitHalfUp

/-- A fund on month `m`: flat rate, the month's ceiling, rounded to the stotinka. -/
def fund (name : String) (rate : Int) (m : Nat) : Contribution :=
  { name, sched := Schedule.flat rate, ceiling := maxInsurable m, round := stRound }

/-- The employee's funds (born after 1959 or before 1960). -/
def eeRates (pre1960 : Bool) : List (String × Int) :=
  [("pension", if pre1960 then eePensionPre1960 else eePension1960), ("gim", eeGim),
   ("unemployment", eeUnemployment), ("upf", if pre1960 then 0 else eeUpf), ("health", eeHealth)]

/-- The monthly wages of an annual amount: twelve equal parts, the remainder to the first months. -/
def monthlyParts (annual : Int) : List (Nat × Int) :=
  months.map fun m => (m, annual / 12 + if (m : Int) < annual % 12 then 1 else 0)

/-- Employee contributions of one month on wage `w` (stotinki). -/
def eeMonth (pre1960 : Bool) (m : Nat) (w : Int) : Int :=
  (eeRates pre1960).foldl (fun a (n, r) => a + (fund n r m).amount w) 0

/-- Employee contributions of the year on an annual wage (stotinki). -/
def eeContrib (pre1960 : Bool) (annual : Int) : Int :=
  (monthlyParts (pos annual)).foldl (fun a (m, w) => a + eeMonth pre1960 m w) 0

/-- Insurable income of the year (the capped monthly wages). -/
def insurableYear (annual : Int) : Int :=
  (monthlyParts (pos annual)).foldl (fun a (m, w) => a + min w (maxInsurable m)) 0

/-- Per-fund detail of the year. -/
def eeDetail (pre1960 : Bool) (annual : Int) : List (String × Int) :=
  (eeRates pre1960).map fun (n, r) =>
    (n, (monthlyParts (pos annual)).foldl (fun a (m, w) => a + (fund n r m).amount w) 0)

/-! ## Self-insured (free profession)

КСО чл. 6, ал. 8: self-insured persons pay "върху месечен осигурителен доход между минималния и максималния месечен
размер"; ал. 9: the final insurable income is the declared taxable income of the activity for the year, "не може да
бъде по-малък от минималния месечен осигурителен доход и по-голям от максималния". The year is taken as a whole
(minimum 12 492 лв., maximum 48 420 лв.), reduced by the room already used by employment (ал. 11). A person already
drawing a pension may choose not to be insured (чл. 4, ал. 6: "се осигуряват по свое желание"): not insured here. -/

def seRates (pre1960 : Bool) : Int := (if pre1960 then sePensionPre1960 else sePension1960)
  + (if pre1960 then 0 else seUpf) + seHealth

/-- The self-insured base of the year: the activity's taxable income clamped to [min, max], within the room left
by employment. -/
def seBase (taxable empInsurable : Int) : Int :=
  if taxable ≤ 0 then 0 else
  min (clamp minSelfInsuredYear maxInsurableYear taxable) (pos (maxInsurableYear - empInsurable))

/-- Self-insured contributions of the year (rounded half up to the stotinka on the year's base). -/
def seContrib (pre1960 : Bool) (base : Int) : Int := stRound.ofTicks (seRates pre1960 * base)

/-! ## Year-dependent versions (2022-2024; `y` ≥ 2025 uses the functions above) -/

def fundY (y : Nat) (name : String) (rate : Int) (m : Nat) : Contribution :=
  { name, sched := Schedule.flat rate, ceiling := maxInsurableY y m, round := stRound }

def eeMonthY (y : Nat) (pre1960 : Bool) (m : Nat) (w : Int) : Int :=
  (eeRates pre1960).foldl (fun a (n, r) => a + (fundY y n r m).amount w) 0

def eeContribY (y : Nat) (pre1960 : Bool) (annual : Int) : Int :=
  (monthlyParts (pos annual)).foldl (fun a (m, w) => a + eeMonthY y pre1960 m w) 0

def insurableYearY (y : Nat) (annual : Int) : Int :=
  (monthlyParts (pos annual)).foldl (fun a (m, w) => a + min w (maxInsurableY y m)) 0

def seBaseY (y : Nat) (taxable empInsurable : Int) : Int :=
  if taxable ≤ 0 then 0 else
  min (clamp (minSelfInsuredYearY y) (maxInsurableYearY y) taxable) (pos (maxInsurableYearY y - empInsurable))

/-! ## Eurostat convention (`--eurostat`, NOT statute): Eurostat earn_net ESMS 3.4 ("Income tax and social security
contributions parameters refer to the beginning of the fiscal year, i.e. changes occurring later during the year are
ignored"; tests/data/_methodology/earn_net_esms.htm, sha256 89ab2734...). The ceiling and the self-insured minimum
of month 0 (January) apply to all twelve months; e.g. 2025: 3 750 лв. all year instead of 4 130 лв. from April. -/

def maxInsurableE (y : Nat) (_m : Nat) : Int := maxInsurableY y 0
def minSelfInsuredE (y : Nat) (_m : Nat) : Int := minSelfInsuredY y 0

def fundE (y : Nat) (name : String) (rate : Int) (m : Nat) : Contribution :=
  { name, sched := Schedule.flat rate, ceiling := maxInsurableE y m, round := stRound }

def eeMonthE (y : Nat) (pre1960 : Bool) (m : Nat) (w : Int) : Int :=
  (eeRates pre1960).foldl (fun a (n, r) => a + (fundE y n r m).amount w) 0

def eeContribE (y : Nat) (pre1960 : Bool) (annual : Int) : Int :=
  (monthlyParts (pos annual)).foldl (fun a (m, w) => a + eeMonthE y pre1960 m w) 0

def insurableYearE (y : Nat) (annual : Int) : Int :=
  (monthlyParts (pos annual)).foldl (fun a (m, w) => a + min w (maxInsurableE y m)) 0

def seBaseE (y : Nat) (taxable empInsurable : Int) : Int :=
  if taxable ≤ 0 then 0 else
  min (clamp (12 * minSelfInsuredE y 0) (12 * maxInsurableE y 0) taxable) (pos (12 * maxInsurableE y 0 - empInsurable))

theorem maxInsurableE_2025 (m : Nat) : maxInsurableE 2025 m = 3750 * LEV := by
  simp [maxInsurableE, maxInsurableY, maxInsurable]

/-! ## EUROMOD convention (`--euromod`, NOT statute; round 15): EUROMOD's legislative parameters are those in force on
30 June of the policy year ("Legislative parameters of the tax system are referred in EM to 30 June": EUROMOD
"Nowcasting prices" note, Feb 2025, sections 1.3-1.4, software/euromod/model/Documentation, sha256 64eb954e350abd1c...;
tests/convention_policy.json "euromod_convention_mode"). No BG country report is available locally, so the general
rule applies. The ceiling and the self-insured minimum of June (month index 5) apply to all twelve months: 2022
3 400 / 710 лв. (ЗБДОО 2022 чл. 9, т. 2, from 1 April), 2023 3 400 / 710 лв. (ЗБДОО 2023 чл. 9, т. 1, to 31 July),
2024 3 750 / 933 лв., 2025 4 130 / 1 077 лв. (ЗБДОО 2025 чл. 9, from 1 April). -/

def maxInsurableJ (y : Nat) (_m : Nat) : Int := maxInsurableY y 5
def minSelfInsuredJ (y : Nat) (_m : Nat) : Int := minSelfInsuredY y 5

def fundJ (y : Nat) (name : String) (rate : Int) (m : Nat) : Contribution :=
  { name, sched := Schedule.flat rate, ceiling := maxInsurableJ y m, round := stRound }

def eeMonthJ (y : Nat) (pre1960 : Bool) (m : Nat) (w : Int) : Int :=
  (eeRates pre1960).foldl (fun a (n, r) => a + (fundJ y n r m).amount w) 0

def eeContribJ (y : Nat) (pre1960 : Bool) (annual : Int) : Int :=
  (monthlyParts (pos annual)).foldl (fun a (m, w) => a + eeMonthJ y pre1960 m w) 0

def insurableYearJ (y : Nat) (annual : Int) : Int :=
  (monthlyParts (pos annual)).foldl (fun a (m, w) => a + min w (maxInsurableJ y m)) 0

def seBaseJ (y : Nat) (taxable empInsurable : Int) : Int :=
  if taxable ≤ 0 then 0 else
  min (clamp (12 * minSelfInsuredJ y 0) (12 * maxInsurableJ y 0) taxable) (pos (12 * maxInsurableJ y 0 - empInsurable))

theorem maxInsurableJ_values (m : Nat) : maxInsurableJ 2022 m = 3400 * LEV ∧ maxInsurableJ 2025 m = 4130 * LEV := by
  simp [maxInsurableJ, maxInsurableY, maxInsurable]

end BgTax
