import TaxKernel.World

/-!
# Sierra Leone: income tax of a resident individual, Income Tax Act 2000 as amended, year of assessment 2025

Sources (National Revenue Authority "Tax Laws & Regulations" page, nra.gov.sl/tax-laws, files on
webtestcms.nra.gov.sl/uploads/, fetched from the laptop (nra.gov.sl does not answer lean1); files in `sl/law/`):
* Income Tax Act 2000 as amended to Finance Act 2017 (NRA compilation): s. 4(1) and First Schedule Part I "Rates of tax
  applicable to individuals resident in Sierra Leone"; s. 38(2): "An individual's contributions to a complying
  retirement fund shall be allowable to the extent of thirty percent of his employment income".
* Finance Act 2020 (scan, OCR checked against the page image of p. 14), "Come into operation on the 1st day of January,
  2020", s. 21: "The First Schedule to the Income Tax Act, 2000 is amended: (a) by repealing and replacing Part 1 with
  the following: If annual chargeable income is | The tax is | Less or equal to 7,200,000.00 | Nill | >Le7,200,000 but
  up to -Le14,400,000 | 15% | >14,400,000 but up to-21,600,000 | 20% | >21,600,000 but up to-28,800,000 | 25% | >Above
  28,800,000 | 30%". (It replaced the Finance Act 2019 s. 11 table, whose second line printed "Le12,000,0000".)
* Finance Acts 2021, 2022, 2023, 2024, 2025 and 2026 read: none amends Part I of the First Schedule (2023-2025 amend
  Parts II-IV and other sections).
* Redenomination of the Leone Regulations 2024 (S.I. No. 4 of 2024, SierraLII source PDF, Internet Archive capture
  2024-10-07): "redenomination" means converting the existing currency "whereby the face value of bank notes and coins
  is divided by one thousand"; reg. 3(6): "From the appointed date all amounts expressed in the existing currency shall
  automatically be converted into the redenominated currency"; reg. 14: converted amounts rounded to 2 decimals. The
  model therefore works in new leones (SLE): Le 7,200,000 = NLe 7,200. (Reg. 10(3) also says amounts in an Act enacted
  before the appointed date "shall be deemed to be an amount expressed in the redenominated currency": FINDINGS.)
W5 pattern A (2026-11-20): **National Social Security and Insurance Trust Act, 2001 (Act No. 5 of 2001)**
(sierra-leone.org/Laws/2001-5.pdf, scan, OCR; `sl/law/w5/`) s. 25 (1): "Every employer of an establishment shall deduct
from the earnings of every worker in the establishment immediately at the end of each month, a worker's contribution
of an amount equal to 5% of the worker's earnings for that month"; s. 25 (2): employer 10 %; s. 2: "earning" means all
emoluments earned on duty and paid in cash at fixed intervals (allowances included, presents excluded); no ceiling or
floor in the Act; s. 20 (2): "Contributions to the Trust shall be tax deductible" (also within ITA s. 38 (2), 30 %).
Amending Acts after 2001 were not checked. Input `nassitEmployee` (annual, first adult), when given, replaces the
statutory amount as before; `"w5Contrib": false` restores the pre-W5 model.
-/

namespace SlTax
open TaxKernel

/-- First Schedule Part I (Finance Act 2020 s. 21), annual, in new leones (old leones / 1,000). -/
def sched : Schedule := Schedule.ofList [(0, 0), (7200, 1500), (14400, 2000), (21600, 2500), (28800, 3000)]
/-- s. 38(2). -/
def retirementCapPct : Int := 3000

def pct (bp x : Int) : Int := divR .down (bp * x) BP

/-- W5 pattern A: NASSIT Act 2001 s. 25 (1), worker 5 % of earnings (no ceiling). -/
def nassitWorkerBp : Int := 500
def nassitWorker (w : Int) : Int := pct nassitWorkerBp (pos w)
/- s. 25 (1)-(2): 5 % worker + 10 % employer = 15 %, the self-employed rate of s. 25 (4). -/
#guard nassitWorkerBp + 1000 = 1500 ∧ nassitWorker 60000 = 3000

def person (nassit : Int) (a : Adult) : Int × Int :=
  let w := pos a.wages
  let ded := min (pos nassit) (pct retirementCapPct w)
  let ci := pos (w + a.selfEmployment - ded)
  (sched.tax Rule.unitDown ci, ci)

def out (c : Canon) : Out :=
  let nassitIn := (c.int? "nassitEmployee").getD 0
  let w5 := (c.bool? "w5Contrib").getD true
  let useStat := w5 && nassitIn == 0
  let nassitOf (a : Adult) (i : Nat) : Int := if useStat then nassitWorker a.wages else if i = 0 then nassitIn else 0
  let nassit := if useStat then sumInts (c.adults.map fun a => nassitWorker a.wages) else nassitIn
  let ps := c.adults.zip (List.range c.adults.length) |>.map fun (a, i) => person (nassitOf a i) a
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 then ["interest, dividends and rents: withholding rules not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "SL" "SLE" (sumInts (ps.map (·.1))) (employeeSocial := pos nassit)
    (detail := [Out.d "chargeableIncome" (sumInts (ps.map (·.2))),
      Out.dStr "currency" "new leones (SLE); the Act's amounts are in old leones, divided by 1,000 (Redenomination Regulations 2024 reg. 3(6))",
      Out.dStr "note" "individual taxation; First Schedule Part I (Finance Act 2020) on chargeable income"])
    (unsupported := unsup ++ [if useStat then "NASSIT worker 5 % (Act 2001 s. 25 (1)) deducted (s. 20 (2)); amending Acts after 2001 not checked" else "NASSIT employee contribution: Act not reached; input nassitEmployee (annual SLE, first adult) deducted under s. 38(2)",
      "allowances and benefits exemptions of the Act not modelled (gross wage taxed)", "business income taxed on the same scale without business deductions"])

def country : Country := { code := "SL", name := "Sierra Leone (Income Tax Act 2000)", currency := "SLE", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: tax at the top of each band (NLe): 1,080 at 14,400; 2,520 at 21,600; 4,320 at 28,800. -/
#guard sched.tax Rule.unitDown 14400 = 1080 ∧ sched.tax Rule.unitDown 21600 = 2520 ∧ sched.tax Rule.unitDown 28800 = 4320

end SlTax
