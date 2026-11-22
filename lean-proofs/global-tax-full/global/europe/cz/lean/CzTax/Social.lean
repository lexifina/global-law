import CzTax.Tax

/-!
# Contributions (2025)

Employee (ZPSZ § 7 odst. 1 písm. d), § 15a; ZPVZP § 2, § 3; ZVZP § 9 odst. 2): computed month by month on a wage paid
evenly (the yearly amount split into 11 equal months and a December remainder), each month's premium rounded up
(ZPSZ § 7 odst. 3: "Pojistné se zaokrouhluje na celé koruny směrem nahoru"; ZPVZP § 2 odst. 2 the same). The social
base stops at the yearly ceiling 48 × average wage (§ 15a odst. 1–2). Health has no ceiling; the employee's third is
taken as one third of the rounded total premium, rounded up (payroll convention; the statute says only "z jedné
třetiny zaměstnanec", ZVZP § 9 odst. 2). Below the minimum base (the minimum wage) the employee pays 13,5 % of the
difference (ZPVZP § 3 odst. 10).

OSVČ (ZPSZ § 5b, § 14, § 15a odst. 5–6; ZPVZP § 3a): yearly, on 55 % (pension) / 50 % (health) of the § 7 base, with
the 2025 minimum bases for a hlavní činnost, and for a vedlejší činnost (taken here as: the person is also an
employee) the rozhodná částka of zákon 155/1995 § 10 odst. 2 and the vedlejší minimum; the pension base shares the
48 × average wage ceiling with the employee base (§ 15a odst. 6).

Paušální režim (§ 7a, § 38lk ZDP; ZPSZ § 14 odst. 3; ZPVZP § 3a odst. 5): fixed monthly amounts by band.
-/

namespace CzTax

/-- Employee social security (6,5 % pension + 0,6 % sickness) for a year's wage `w`, with the ceiling. -/
def eeSocial (w : Int) : Int := (cappedMonthly eeSocialRate socialCeiling (monthsOf (pos w))).1

/-- Employee health insurance: one third of the rounded 13,5 % premium each month, plus the 13,5 % on the shortfall
below the minimum base when `minBase` is true (ZPVZP § 3 odst. 10). -/
def eeHealthMonth (minBase : Bool) (w : Int) : Int :=
  let total := bpCeil w healthRate
  let third := cdiv total healthEeDen
  let short := if minBase && w < healthMinBaseEe then bpCeil (healthMinBaseEe - w) healthRate else 0
  third + short

def eeHealth (minBase : Bool) (w : Int) : Int :=
  if w ≤ 0 then 0 else ((monthsOf w).map (eeHealthMonth minBase)).foldl (· + ·) 0

/-- **`cztax --oecd` only (convention mode).** The OECD Taxing Wages arithmetic for Czechia (tests round 1,
`cmp20/improve-emerging/IMPROVE.md`): the employee rates applied once to the annual wage, rounded half up once,
with no month-by-month rounding up (the statute: ZPSZ § 7 odst. 3, ZPVZP § 2 odst. 2, `eeSocial` above). Social:
7,1 % up to the annual ceiling 48 × average wage (§ 15a). -/
def eeSocialOecd (w : Int) : Int := (2 * min (pos w) socialCeiling * eeSocialRate + 10000) / 20000

/-- `--oecd` only: health at one third of 13,5 % (4,5 %) of the annual wage, half up once; the minimum-base top-up
(ZPVZP § 3 odst. 10) on the annual shortfall. -/
def eeHealthOecd (minBase : Bool) (w : Int) : Int :=
  if w ≤ 0 then 0 else
  let third := (2 * w * healthRate + 3 * 10000) / (2 * 3 * 10000)
  let short := if minBase && w < 12 * healthMinBaseEe then bpCeil (12 * healthMinBaseEe - w) healthRate else 0
  third + short

/-! ### Any tax year (tests round 2): the same rules with the year's rate, ceiling and minimum wage (`YearP`) -/

def eeSocialAt (rate ceiling w : Int) : Int := (cappedMonthly rate ceiling (monthsOf (pos w))).1

def eeHealthMonthAt (minWageM : Int) (minBase : Bool) (w : Int) : Int :=
  let total := bpCeil w healthRate
  let third := cdiv total healthEeDen
  let short := if minBase && w < minWageM then bpCeil (minWageM - w) healthRate else 0
  third + short

def eeHealthAt (minWageM : Int) (minBase : Bool) (w : Int) : Int :=
  if w ≤ 0 then 0 else ((monthsOf w).map (eeHealthMonthAt minWageM minBase)).foldl (· + ·) 0

def eeSocialOecdAt (rate ceiling w : Int) : Int := (2 * min (pos w) ceiling * rate + 10000) / 20000

def eeHealthOecdAt (minWageM : Int) (minBase : Bool) (w : Int) : Int :=
  if w ≤ 0 then 0 else
  let third := (2 * w * healthRate + 3 * 10000) / (2 * 3 * 10000)
  let short := if minBase && w < 12 * minWageM then bpCeil (12 * minWageM - w) healthRate else 0
  third + short

theorem eeSocialAt_2025 (w : Int) : eeSocialAt eeSocialRate socialCeiling w = eeSocial w := rfl
theorem eeHealthAt_2025 (b : Bool) (w : Int) : eeHealthAt healthMinBaseEe b w = eeHealth b w := rfl

/-- Employer social security (24,8 %) and employer health (two thirds), for the s.r.o. regime. -/
def erSocial (w : Int) : Int := (cappedMonthly erSocialRate socialCeiling (monthsOf (pos w))).1

def erHealth (w : Int) : Int :=
  if w ≤ 0 then 0 else
  ((monthsOf w).map (fun m => let t := bpCeil m healthRate; t - cdiv t healthEeDen)).foldl (· + ·) 0

/-- OSVČ pension insurance for a year with § 7 base `profit`; `side` = vedlejší činnost; `eeBase` = the employee
base already used against the 48 × average-wage ceiling. -/
def seSocial (profit : Int) (side : Bool) (eeBase : Int) : Int :=
  let share := bpFloor (pos profit) seSocialShare
  let base :=
    if side then (if pos profit ≥ seSideThreshold then max share (12 * seMinBaseSide) else 0)
    else max share (12 * seMinBaseMain)
  let base := min base (pos (socialCeiling - eeBase))
  bpCeil base seSocialRate

/-- OSVČ health insurance: 50 % of the § 7 base, at least 12 × 23 279 Kč unless the person is also an employee
paying at least on the minimum base (ZPVZP § 3a odst. 3 písm. b)). -/
def seHealth (profit : Int) (side : Bool) : Int :=
  let base := pos profit / 2
  let base := if side then base else max base (12 * seHealthMinMonthly)
  bpCeil base healthRate

/-- Paušální režim: the yearly income-tax part and the yearly contributions (social + health) for a band. -/
def pausalYearTax (band : Nat) : Int := 12 * pausalTax band
def pausalYearSocial (band : Nat) : Int :=
  12 * bpCeil (pausalSocialBase band) seSocialRate + 12 * bpCeil (pausalHealthYear band / 12) healthRate

/-- § 2a odst. 5: the receipts limit of each band, given the § 7 odst. 7 expense class of the receipts (80, 60 or
other). -/
def pausalLimit (band : Nat) (ratePct : Int) : Int :=
  if band = 1 then (if ratePct = 80 then 2000000 else if ratePct = 60 then 1500000 else 1000000)
  else if band = 2 then (if ratePct = 80 || ratePct = 60 then 2000000 else 1500000)
  else 2000000

/-- The lowest band whose limit the receipts do not exceed (0 = none). -/
def pausalBandFor (receipts ratePct : Int) : Nat :=
  if receipts ≤ pausalLimit 1 ratePct then 1
  else if receipts ≤ pausalLimit 2 ratePct then 2
  else if receipts ≤ pausalLimit 3 ratePct then 3 else 0

theorem pausal_band1_month : pausalTax 1 + bpCeil (pausalSocialBase 1) seSocialRate
    + bpCeil (pausalHealthYear 1 / 12) healthRate = 8716 := by decide
theorem pausal_band2_month : pausalTax 2 + bpCeil (pausalSocialBase 2) seSocialRate
    + bpCeil (pausalHealthYear 2 / 12) healthRate = 16745 := by decide
theorem pausal_band3_month : pausalTax 3 + bpCeil (pausalSocialBase 3) seSocialRate
    + bpCeil (pausalHealthYear 3 / 12) healthRate = 27139 := by decide

end CzTax
