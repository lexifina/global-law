import TaxKernel.World

/-!
# South Sudan: national personal income tax on wages, Taxation Act 2009 as amended, Financial Act 2024/2025
(tax year 1 July 2024 - 30 June 2025)

Authority: the national Government of the Republic of South Sudan (Juba). The Transitional Constitution 2011 lists
"national personal income tax" (art. 177(b)) and also "state personal income tax" (art. 179(d)) (Global law
`south-sudan/national/acts/constitution`); state taxes are not modelled. Year: the Financial Act for 2025/26 was not
reached (the National Revenue Authority's document server cms.nra.gov.ss answered 502); the latest accessible year,
2024/25, is modelled.

Sources (Internet Archive copies of the National Revenue Authority's uploads; files in `ss/law/`):
* Financial Act 2024/2025 (cms.nra.gov.ss/uploads/Financial_Act_2024_2025_464925c180.pdf, capture 2025-04-01, 165-page
  scan; the 2025-03-17 capture is cut at 5,242,880 bytes; OCR of pp. 1-45, rates checked against the OCR of the
  2023/24 Act's text layer, which prints the same table). s. 4(1): "Personal income tax is charged for the tax year
  2024/2025 on taxable income from wages and entrepreneurial Activities after standard allowable expenses of twenty
  percent (20%) and other expenses such as town rate, ground rate, etc. are deducted." s. 4(2): "the exemption level
  is raised to SSP 20,000 per month ... (a) Taxable incomes less than SSP 20,000 per month are not subject to tax ...
  (b) Taxable incomes ranging from 20,001 but does not exceed SSP 40,000 per month are charged at the rate of five
  percent (5%). (c) ... from SSP 40,001 but does not exceed SSP 57,000 per month ... ten percent (10%). (d) ... from
  SSP 57,001 but does not exceed SSP 90,000 are charged at the rate of fifteen percent (15%). (e) Taxable income from
  SSP 90,001 and above are charged at the rate of twenty percent (20%)." s. 5(2): "Employee pension contribution of up
  to five percent (5%) of gross wages to GRS approved funded pension scheme, shall be deducted from gross income."
* Financial Act 2023/2024 (capture 2025-05-14, text layer): the same s. 4 table, but its s. 4(1) says "charged for the
  tax year 2022/23" (FINDINGS).
Readings (FINDINGS F1, F2): the model applies each rate to the part of monthly taxable income in its bracket (input
`ssSlabReading: true` applies the bracket's rate to the whole monthly income, as the words "Taxable incomes ...
are charged at the rate of" can be read); the 20 % standard allowable expenses are applied to entrepreneurial income
only by default (`standard20OnWages: true` applies them to wages too). The employee pension deduction applies only to
members of a GRS-approved scheme (input `pensionMember: true`; the pension itself is reported).
-/

namespace SsTax
open TaxKernel

/-- Financial Act 2024/2025 s. 4(2), monthly, graduated reading. -/
def sched : Schedule := Schedule.ofList [(0, 0), (20000, 500), (40000, 1000), (57000, 1500), (90000, 2000)]

/-- The slab reading: the rate of the bracket the whole monthly income falls in, on the whole income. -/
def slabRate (m : Int) : Int :=
  if m < 20000 then 0 else if m ≤ 40000 then 500 else if m ≤ 57000 then 1000 else if m ≤ 90000 then 1500 else 2000

def pct (bp x : Int) : Int := divR .down (bp * x) BP

def taxMonth (slab : Bool) (m : Int) : Int :=
  if slab then pct (slabRate (pos m)) (pos m) else sched.tax Rule.unitDown (pos m)

def out (c : Canon) : Out :=
  let slab := (c.bool? "ssSlabReading").getD false
  let std20 := (c.bool? "standard20OnWages").getD false
  let member := (c.bool? "pensionMember").getD false
  let monthBase (m : Int) : Int :=
    let p := if member then pct 500 m else 0
    let s := if std20 then pct 2000 m else 0
    pos (m - p - s)
  let tax := sumInts (c.adults.map fun a => perPeriod 12 (fun m => taxMonth slab (monthBase (pos m))) (pos a.wages))
  let pen := if member then sumInts (c.adults.map fun a => perPeriod 12 (fun m => pct 500 (pos m)) (pos a.wages)) else 0
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["entrepreneurial income not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 then ["rental and investment income (s. 4(2)(f), 20 %) not modelled"] else []) ++
    (if c.capitalGains ≠ 0 || (c.adults.map (·.pension)).any (· ≠ 0) then ["gains and pensions not modelled"] else [])
  Out.make c "SS" "SSP" tax (employeeSocial := pen)
    (detail := [Out.d "pit" tax,
      Out.dStr "reading" ((if slab then "slab" else "graduated") ++ (if std20 then "; 20 % standard expenses on wages" else "")),
      Out.dStr "year" "tax year 2024/25 (1 July 2024 - 30 June 2025), Financial Act 2024/2025",
      Out.dStr "note" "national PIT on monthly wages (s. 4(2)); state personal income taxes not modelled"])
    (unsupported := unsup ++ ["Financial Act 2025/2026 not reached: year 2024/25 modelled", "state personal income tax (Constitution art. 179(d)) not modelled",
      "wages paid evenly over 12 months (monthly brackets)"])

def country : Country := { code := "SS", name := "South Sudan (Taxation Act 2009, Financial Act 2024/25)", currency := "SSP", year := "2024/25", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Graduated reading, hand-computed: 100,000 SSP a month: 1,000 + 1,700 + 4,950 + 2,000 = 9,650. -/
#guard taxMonth false 100000 = 9650
/- The slab reading makes the tax jump at each bracket edge: 40,000 -> 2,000; 40,001 -> 4,000.1 (notch of 2,000). -/
#guard taxMonth true 40000 = 2000 ∧ taxMonth true 40001 = 4000
#guard taxMonth true 90000 = 13500 ∧ taxMonth true 90001 = 18000

end SsTax
