import TaxKernel.World

/-!
# Trinidad and Tobago: income tax, health surcharge and National Insurance of a resident employee, year of income 2025

Sources (Global law corpus `trinidad-and-tobago/national/acts`, read from laws.gov.tt consolidations; files in `tt/law/`):
* Income Tax Act Chap. 75:01, consolidation of 2025-06-03 (laws.gov.tt; notes to Act No. 15 of 2024, in force
  14 October 2024; the year of income is the calendar year, s. 79 instalments "31st March, 30th June, 30th September and
  31st December ... in each year of income").
  - s. 18 (Act 21 of 2022, in force 1 January 2023): "an individual to whom section 17 applies ... is entitled to a
    personal allowance of ninety thousand dollars".
  - s. 8(1)(k): exempt "the income of any resident individual where the total income does not exceed sixty thousand
    dollars for a year of income".
  - s. 27(1)(d), s. 31(1)(c): an insured person under the National Insurance Act "shall be allowed a deduction of
    seventy per cent of the annual amount of the contribution so paid"; s. 28(15): deductions under s. 27(1)(c)-(e),
    s. 31(1) and s. 28 "limited to an aggregate amount of sixty thousand dollars".
  - s. 48: "tax at the rates set forth in Part I of the Third Schedule". Third Schedule Part I para. 1: "(a)
    twenty-five cents for every dollar up to $1,000,000 of chargeable income; and (b) thirty cents for every dollar that
    exceeds $1,000,000". Para. 2 (resident persons other than companies): "(a) does not exceed $5,000, no tax shall be
    charged; (b) exceeds $5,000, but does not exceed $5,500, the tax payable shall be limited to 49.5 per cent of the
    amount by which the chargeable income exceeds $5,000; (c) exceeds $5,000, but does not exceed $6,000, the tax
    payable shall be reduced by 50 per cent; (d) exceeds $6,000, but does not exceed $7,000, the tax payable shall be
    limited to $280 plus 31.2 per cent of the amount by which the chargeable income exceeds $6,000; (e) exceeds $7,000,
    but does not exceed $8,000, the tax payable shall be reduced by 20 per cent; (f) exceeds $8,000, but does not exceed
    $8,500, the tax payable shall be limited to $736 plus 59.8 per cent of the amount by which the chargeable income
    exceeds $8,000" (amended to "10 of 2016 and 16 of 2021"; FINDINGS F1: the relief no longer fits the rates).
* Health Surcharge Act Chap. 75:05 (consolidation 2023-10-24, Act 10 of 2021) s. 3(1)-(4): payable by "every employed
  person who pays or is liable to pay contribution under the National Insurance Act" and by individuals who must file a
  return, not under 16 or 60 and over; "(a) employed persons whose monthly emoluments are more than $469.99 or whose
  weekly emoluments are more than $109.00 $8.25 per week. All other employed persons $4.80 per week".
* National Insurance Act Chap. 32:01 (laws.gov.tt consolidation of 2025-01-08, `nis_32-01_118843.pdf`): s. 20(2)(a)(iv)
  uninsurable employment: remuneration "less than ... two hundred dollars per week from 5th September 2016"; s. 38(1)
  contributions of an employed person "who has attained the age of sixteen years but has not yet attained the age of
  sixty-five years" paid partly by the employee; s. 41(1)-(2)(i): based on "the assumed average weekly earnings of the
  earnings class into which such employed person falls", "(i) in Table A9 are effective from 5th September 2016";
  Second Schedule Table A9 "Earnings Class and Contributions from 5th September 2016 (Based on a contribution rate of
  13.2%)": employee's weekly contribution by weekly earnings class (below). 2025 has 52 Mondays (contribution weeks).
-/

namespace TtTax
open TaxKernel

/-- Third Schedule Part I para. 1 (whole dollars of chargeable income). -/
def sched : Schedule := Schedule.ofList [(0, 2500), (1000000, 3000)]

/-- Tax in cents on chargeable income `x` (whole dollars) with the para. 2 relief for resident individuals. -/
def taxCents (x : Int) : Int :=
  let t := sched.ticks x / 100                      -- cents (ticks = dollars x bp; 1 cent = 100 ticks)
  if x ≤ 5000 then 0
  else if x ≤ 5500 then min (t / 2) (divR .down (4950 * (x - 5000)) 100)     -- (b) and (c) both apply
  else if x ≤ 6000 then t / 2                                                   -- (c)
  else if x ≤ 7000 then min t (28000 + divR .down (3120 * (x - 6000)) 100)     -- (d)
  else if x ≤ 8000 then divR .down (t * 8) 10                                  -- (e)
  else if x ≤ 8500 then min t (73600 + divR .down (5980 * (x - 8000)) 100)     -- (f)
  else t

/-- Third Schedule para. 1 alone (no para. 2 relief), in cents. -/
def taxCentsPlain (x : Int) : Int := sched.ticks x / 100

/-- National Insurance Act Second Schedule Table A9: (lower bound of weekly earnings in cents, employee's weekly
    contribution in cents), classes I-XVI. -/
def nisA9 : List (Int × Int) :=
  [(20000, 1190), (34000, 1740), (45000, 2330), (61000, 3010), (76000, 3720), (93000, 4510), (112000, 5320),
   (130000, 6140), (149000, 7040), (171000, 7960), (191000, 8910), (214000, 9940), (238000, 11020),
   (263000, 12210), (292000, 13330), (313800, 13810)]

/-- Employee's weekly contribution (cents) for weekly earnings in cents; below $200 a week: uninsurable (s. 20(2)(a)(iv)). -/
def nisWeek (wc : Int) : Int := nisA9.foldl (fun acc r => if wc ≥ r.1 then r.2 else acc) 0

/-- Weeks of contribution in 2025 (Mondays: 1 January 2025 is a Wednesday, 365 days). -/
def weeks : Int := 52

structure Person where
  nis : Int        -- cents
  hs : Int         -- cents
  total : Int
  chargeable : Int
  tax : Int        -- cents

def person (a : Adult) : Person :=
  let w := pos a.wages
  let se := pos a.selfEmployment
  let wc := divR .down (w * 100) weeks                 -- weekly earnings in cents
  let insurable := a.age ≥ 16 && a.age < 65 && wc ≥ 20000
  let nis := if insurable then weeks * nisWeek wc else 0
  let hsAge := a.age ≥ 16 && a.age < 60
  let hsEmp := if hsAge && insurable then weeks * (if wc > 10900 then 825 else 480) else 0
  let hsSelf := if hsAge && !insurable && se > 0 then weeks * (if (w + se) * 100 > 46999 * 12 then 825 else 480) else 0
  let total := w + se
  let nisDed := min 60000 (divR .down (7 * nis) 1000)    -- 70 % of the contribution (cents -> dollars), s. 28(15) cap
  let chargeable := if total ≤ 60000 then 0 else pos (total - 90000 - nisDed)
  { nis := nis, hs := hsEmp + hsSelf, total := total, chargeable := chargeable, tax := taxCents chargeable }

def cents (x : Int) : Int := divR .halfUp x 100

def out (c : Canon) : Out :=
  let ps := c.adults.map person
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then
      ["interest, dividends (withholding, Third Schedule Part II), rents and gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else []) ++
    (if c.pensionContributions ≠ 0 then ["approved pension plan contributions (s. 28) not modelled"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employed: no NIS (employed persons only); business deductions not modelled"] else [])
  Out.make c "TT" "TTD" (cents (sumInts (ps.map (·.tax))))
    (surtaxes := [("healthSurcharge", cents (sumInts (ps.map (·.hs))))])
    (employeeSocial := cents (sumInts (ps.map (·.nis))))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.chargeable))), Out.d "nis" (cents (sumInts (ps.map (·.nis)))),
      Out.dStr "note" "individual taxation; ITA s. 18 allowance 90,000; 70 % of NIS deductible (s. 31(1)(c)); Third Schedule 25/30 % with para. 2 relief; NIS Table A9 weekly classes (52 weeks); health surcharge s. 3(4)"])
    (unsupported := unsup ++ ["wages assumed paid evenly over 52 weeks (NIS classes and health surcharge are weekly)"])

def country : Country := { code := "TT", name := "Trinidad and Tobago (Income Tax Act Chap. 75:01)", currency := "TTD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Third Schedule para. 1: $250,000 at $1,000,000; para. 2 relief points (cents). -/
#guard taxCents 1000000 = 25000000
#guard taxCents 5000 = 0
#guard taxCents 5500 = 24750            -- (b): 49.5 % of 500
#guard taxCents 5501 = 68762            -- (c): half of 1,375.25 (F1: +440 for one dollar)
#guard taxCents 6000 = 75000
#guard taxCents 6001 = 28031            -- (d): tax falls by 469.69 at 6,000 -> 6,001
#guard taxCents 7000 = 59200
#guard taxCents 7001 = 140020           -- (e): +808 for one dollar
#guard taxCents 8000 = 160000
#guard taxCents 8001 = 73659            -- (f): falls by 863
#guard taxCents 8500 = 103500
#guard taxCents 8501 = 212525           -- above para. 2: +1,090 for one dollar
/- NIS Table A9: class I at $200 a week, class XVI from $3,138 a week. -/
#guard nisWeek 19999 = 0
#guard nisWeek 20000 = 1190
#guard nisWeek 313800 = 13810
#guard nisA9.length = 16

end TtTax
