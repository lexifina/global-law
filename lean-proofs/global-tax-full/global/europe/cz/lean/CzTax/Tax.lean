import CzTax.Params

/-!
# Daň z příjmů fyzických osob (ZDP, 2025)

Structure of the statute, as computed here for one poplatník:

1. Dílčí základy daně: § 6 (employment: "Základem daně (dílčím základem daně) jsou příjmy ze závislé činnosti",
   § 6 odst. 12 — gross wage, no deduction), § 7 (self-employment: receipts − expenses, actual or a percentage under
   § 7 odst. 7), § 9 (rent: receipts − 30 % under § 9 odst. 4), § 10 (other income: here the taxable part of share
   sales above the § 4 odst. 3 cap and of pensions above the § 4 odst. 1 písm. g) exemption).
2. § 5 odst. 3: a loss from §§ 7 and 9 reduces only the sum of the §§ 7–10 bases, never the § 6 base.
3. § 15: nezdanitelné části (gifts, mortgage interest, retirement products).
4. § 16 odst. 2: the base after § 15 "zaokrouhleného na celá sta Kč dolů"; 15 % / 23 % above 36 × average wage;
   daňový řád § 146 odst. 1: "Daň se zaokrouhluje na celé koruny nahoru".
5. § 35ba: slevy (poplatník, manžel) down to zero; § 35c: daňové zvýhodnění as sleva, then as bonus (refundable),
   subject to § 35c odst. 3 (≥ 100 Kč) and odst. 4 (příjem § 6 or § 7 ≥ 6 × minimum wage).
-/

namespace CzTax

/-- § 16: the tax on a (rounded) base, exactly in units of 1/100 crown before rounding. -/
def tax16Cents (b : Int) : Int := rateLow / 100 * min (pos b) threshold23 + rateHigh / 100 * pos (b - threshold23)

/-- § 16 + daňový řád § 146: the tax on the base `b` (already rounded to the hundred), rounded up to the crown. -/
def tax16 (b : Int) : Int := cdiv (tax16Cents b) 100

/-- § 16 odst. 1 with the year's threshold `thr` (48× or 36× the průměrná mzda; `YearP.threshold23`). -/
def tax16CentsAt (thr b : Int) : Int := rateLow / 100 * min (pos b) thr + rateHigh / 100 * pos (b - thr)

theorem tax16CentsAt_2025 (b : Int) : tax16CentsAt threshold23 b = tax16Cents b := rfl

/-- § 16 odst. 2: base after nezdanitelné části, "zaokrouhleného na celá sta Kč dolů". -/
def roundBase (x : Int) : Int := floorTo 100 x

/-- § 7 odst. 7: expenses as a percentage of receipts, capped; `ratePct` ∈ {80, 60, 40, 30}. -/
def flatExpenses (receipts ratePct : Int) : Int :=
  min (pos receipts * ratePct / 100) (expenseCap ratePct)

/-- § 9 odst. 4: rent expenses at 30 %, capped at 600 000 Kč. -/
def rentExpenses (rent : Int) : Int := min (pos rent * 30 / 100) rentExpenseCap

/-- § 15 odst. 1: the deductible amount of gifts `g` given the base `b`: only if `g` exceeds 2 % of the base or is at
least 1 000 Kč, and at most 15 % of the base. -/
def giftDeduction (g b : Int) : Int :=
  if g > 0 && (g * 100 > 2 * b || g ≥ giftMinAbs) then min g (pos b * 15 / 100) else 0

/-- § 15 odst. 5–6: retirement products; contributions to penzijní připojištění / DPS `c` a year paid evenly by month:
only the part of each month above 1 700 Kč, at most 48 000 Kč a year. -/
def retirementDeduction (c : Int) : Int := min (pos (c - 12 * dpsMonthlyFloor)) retirementCap

/-- § 15 odst. 3–4: mortgage interest, at most 150 000 Kč. -/
def mortgageDeduction (i : Int) : Int := min (pos i) mortgageCap

/-- What one poplatník brings to the computation. -/
structure TaxIn where
  wages : Int := 0          -- § 6 příjmy (gross)
  seProfit : Int := 0       -- § 7 dílčí základ (receipts − expenses; may be negative)
  seReceipts : Int := 0     -- § 7 příjmy (for the § 35c odst. 4 test)
  rentBase : Int := 0       -- § 9 dílčí základ
  otherBase : Int := 0      -- § 10 dílčí základ (taxable pensions, taxable share sales)
  gifts : Int := 0
  mortgage : Int := 0
  retirement : Int := 0
  spouseCredit : Bool := false
  childCredits : Int := 0   -- sum of § 35c amounts for the children this poplatník claims
  /-- `cztax --oecd` only (convention mode): no § 16 odst. 2 rounding of the base to the hundred and no daňový řád
  § 146 rounding of the tax up to the crown (the tax is rounded half up once); the OECD computes both unrounded. -/
  noRound : Bool := false
  /-- the tax year's § 16 threshold and § 35c odst. 4 income test (defaults: 2025) -/
  thr23 : Int := threshold23
  bonusIncomeMinY : Int := bonusIncomeMin
  /-- § 35bc (2022, 2023 only): sleva za umístění dítěte, applied with the § 35ba slevy (only `--oecd` sets it) -/
  extraSleva : Int := 0
  deriving Repr

structure TaxOut where
  base : Int            -- základ daně (§ 5, § 6–10)
  deductions : Int      -- § 15
  roundedBase : Int     -- § 16 odst. 2
  tax16 : Int
  slevy : Int           -- § 35ba used
  afterSlevy : Int
  childSleva : Int      -- § 35c as sleva
  bonus : Int           -- § 35c daňový bonus paid
  bonusLost : Int       -- zvýhodnění not usable (bonus conditions not met)
  finalTax : Int        -- negative = net bonus
  deriving Repr

/-- § 5 odst. 3: a loss from §§ 7, 9 offsets only the §§ 7–10 bases. -/
def taxBase (t : TaxIn) : Int := pos t.wages + pos (t.seProfit + t.rentBase + t.otherBase)

def computeTax (t : TaxIn) : TaxOut :=
  let base := taxBase t
  let ded := giftDeduction t.gifts base + mortgageDeduction t.mortgage + retirementDeduction t.retirement
  let ded := min ded base
  let rb := if t.noRound then base - ded else roundBase (base - ded)
  let tx := if t.noRound then (tax16CentsAt t.thr23 rb + 50) / 100 else cdiv (tax16CentsAt t.thr23 rb) 100
  let slevyClaim := slevaPoplatnik + (if t.spouseCredit then slevaManzel else 0) + pos t.extraSleva
  let used := creditUsed tx slevyClaim
  let after := tx - used
  let cs := creditUsed after t.childCredits
  let eligible := decide (pos t.wages + pos t.seReceipts ≥ t.bonusIncomeMinY)
  let bonus := refundable after t.childCredits bonusMin eligible
  { base := base, deductions := ded, roundedBase := rb, tax16 := tx, slevy := used, afterSlevy := after,
    childSleva := cs, bonus := bonus, bonusLost := pos t.childCredits - cs - bonus,
    finalTax := after - cs - bonus }

/-! ## Withholding taxes and the corporate tax -/

/-- § 36 odst. 2–3: 15 % withheld on dividends / interest, rounded down to the crown. -/
def withheld (x : Int) : Int := bpFloor (pos x) withholdingRate

/-- § 21 odst. 1: 21 % of the base rounded down to the thousand. -/
def cit (b : Int) : Int := bpFloor (floorTo 1000 b) citRate

end CzTax
