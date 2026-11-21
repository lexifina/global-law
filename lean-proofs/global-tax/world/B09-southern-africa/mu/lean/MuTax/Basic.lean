import TaxKernel.World

/-!
# Mauritius: income tax, Fair Share Contribution and CSG social contribution, income year 1 July 2025 - 30 June 2026

Access tier A. Sources (Mauritius Revenue Authority, mra.mu/download/, fetched 2026-11-20, sha256 in `mu/law/SHA256SUMS`):
Income Tax Act 1995 consolidated up to Finance Act 2026 (ITAConsolidated.pdf; the endnotes print every earlier wording
with its effective income year), Finance (Miscellaneous Provisions) Act 2025, Act No. 18 of 2025 (Government Gazette
No. 66 of 9 August 2025), Finance Act 2026, Social Contribution and Social Benefits Act 2021 (Act 14 of 2021, as amended
to 14/26).
* Finance Act 2025 s. 26 (y): "in the First Schedule, by repealing Part I and replacing it by the following Part —
  First 500,000 rupees 0 per cent; Next 500,000 rupees 10 per cent; Remainder 20 per cent"; ITA endnote 1052: "FA 2025
  ... deemed to have come into operation in respect of the income year commencing on 1 July 2025"; FA 2026 replaced it
  (0/10/20/35 with "Next 11 million rupees 20") only from the income year commencing on 1 July 2026.
* ITA s. 16C (1)-(3) (Fair Share Contribution): "every individual whose Fair Share Contribution income threshold exceeds
  12 million rupees ... calculated at the rate of 15 per cent of the leviable income in excess of 12 million rupees ...
  payable with respect to income derived by the individual for the income year commencing on 1 July 2025"; s. 16B:
  threshold = net income + dividends from resident companies; leviable income = chargeable income + those dividends.
* ITA s. 27 (2), (5) and Third Schedule Part I para 1 (from FA 2023): deduction for dependents "One dependent 110,000;
  Two dependents 190,000; Three dependents 275,000; Four or more dependents 355,000"; s. 27 (4): where a person claims a
  dependent child "the spouse of that person shall not claim in that income year any deduction in respect of dependent
  child". (The model gives the children to the first adult; a spouse with net income of 110 000 or less is that
  adult's first dependent.)
* Second Schedule Part II Sub-Part B item 1: exempt "Dividends — (a) paid by a company resident in Mauritius".
* Social Contribution and Social Benefits Act 2021 s. 4 (1) (a)-(b) and First Schedule Part II "50,000 rupees": a
  participant earning "in a month, remuneration not exceeding" Rs 50 000 pays "1.5 per cent of that remuneration";
  above it "3 per cent of that remuneration" (whole remuneration: a notch).
W5 pattern A (2026-11-20): National Savings Fund employee contribution. **National Savings Fund Act 1995** (MRA
consolidation, amended to 18/25; `mu/law/w5/`) s. 5 (2): the employer of an employee referred to in item 2 (a) and (c)
of the First Schedule "shall, at the time of paying to the employee his basic wage or salary for any period, deduct
therefrom one per cent of the basic wage or salary"; s. 5 (3): where the remuneration "does not exceed 3,000 rupees"
in a month, no deduction is made and Government pays the employee's contribution; First Schedule: contributions
"rounded to the nearest rupee"; s. 2: "basic wage or salary" ... "shall not exceed the maximum basic wage or salary as
specified in the Fifth Schedule to the National Pensions Act"; **National Pensions Act 1976** (MRA consolidation,
amended to 14/26) Fifth Schedule (a): "in respect of a monthly pay period, the insurable wage or salary of the insured
person not exceeding 18,740 rupees" (last replaced by reg 3 of GN 268 of 2021 w.e.f. 1 July 2019; no later replacement
in the consolidation's notes). Not deductible: the ITA has no deduction for an employee's NSF contribution (s. 27D /
27DC refer to NSF contributions only for an employer of household employees or carers). Monthly: 1 % of min(wage,
18,740), nearest rupee, nil at or below 3,000; 12 equal months. `"w5Contrib": false` restores the pre-W5 model.
Unit: individual (s. 4; spouses separate). Rupees, rounded down.
-/

namespace MuTax
open TaxKernel

def sched : Schedule := Schedule.ofList [(0, 0), (500000, 1000), (1000000, 2000)]
def fscThreshold : Int := 12000000
def fscRate : Int := 1500

/-- Third Schedule Part I para 1: deduction by number of dependents. -/
def depDeduction (n : Nat) : Int :=
  match n with
  | 0 => 0 | 1 => 110000 | 2 => 190000 | 3 => 275000 | _ => 355000

/-- s. 4 (1) (a)-(b) SCSBA: monthly CSG employee contribution. -/
def csgMonthly (m : Int) : Int :=
  if m ≤ 50000 then divR .down (150 * pos m) BP else divR .down (300 * m) BP

#guard csgMonthly 50000 = 750 ∧ csgMonthly 50001 = 1500

/-- W5 pattern A: NSF Act s. 5 (2)-(3), First Schedule item 2 (c): 1 % of the basic wage, at most the NPA Fifth
Schedule 18,740 a month, nil at or below 3,000 (Government pays), rounded to the nearest rupee. -/
def nsfMaxWage : Int := 18740
def nsfMonthly (m : Int) : Int :=
  if m ≤ 3000 then 0 else divR .halfUp (min m nsfMaxWage) 100
#guard nsfMonthly 3000 = 0 ∧ nsfMonthly 3001 = 30 ∧ nsfMonthly 18740 = 187 ∧ nsfMonthly 100000 = 187

def personTax (ti : Int) : Int := sched.tax Rule.unitDown (pos ti)

def fsc (net leviable : Int) : Int :=
  if net > fscThreshold then divR .down (fscRate * pos (leviable - fscThreshold)) BP else 0

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let nets := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    pos (a.wages + a.selfEmployment + a.pension + share c.rentalIncome i + share c.interest i - share c.pensionContributions i)
  let net2 : Int := match nets with | [_, b] => b | _ => 0
  -- first adult: children, plus the spouse as a dependent when the spouse's net income is at most 110 000 (s. 27 (5) (a))
  let spouseDep : Nat := if c.isCouple && decide (net2 ≤ 110000) then 1 else 0
  let deps (i : Nat) : Nat := if i = 0 then c.nChildren + spouseDep else 0
  let rows := (nets.zip (List.range nets.length)).map fun (net, i) =>
    let ti := pos (net - depDeduction (deps i))
    let dv := share c.dividends i
    (net, ti, personTax ti, fsc (net + dv) (ti + dv))
  let it := sumInts (rows.map fun r => r.2.2.1)
  let f := sumInts (rows.map fun r => r.2.2.2)
  let csg := sumInts (c.adults.map fun a => 12 * csgMonthly (divR .down a.wages 12))
  let w5 := (c.bool? "w5Contrib").getD true
  let nsf := if w5 then sumInts (c.adults.map fun a => 12 * nsfMonthly (divR .down a.wages 12)) else 0
  Out.make c "MU" "MUR" it (surtaxes := [("FairShareContribution", f)]) (employeeSocial := csg + nsf)
    (detail := [Out.d "taxableIncome" (sumInts (rows.map fun r => r.2.1)), Out.d "taxBeforeCredits" it,
      Out.dStr "note" "ITA 1995 First Schedule Part I as replaced by FA 2025 (income year 2025-26); s. 16C FSC; Third Schedule dependents; SCSBA 2021 s. 4 CSG"])
    (unsupported := (if c.capitalGains ≠ 0 then ["capital gains: not taxed as income except as the Act provides; not modelled"] else []) ++
      (if c.pensionContributions ≠ 0 then ["pension contributions deducted in full: the relief limits were not read"] else []) ++
      [if w5 then "National Savings Fund 1 % (NSF Act s. 5 (2), NPA Fifth Schedule 18,740 cap) on wages, not deducted; 'basic wage' (allowances excluded) taken as the whole wage" else "National Savings Fund contribution not read", "dependent child additional deduction for tertiary studies (para 2) not modelled",
       "a spouse who is the first adult's dependent: their own net income is deemed the claimant's (s. 27 (6)) is not applied"])

def country : Country := { code := "MU", name := "Mauritius (income year 2025-26)", currency := "MUR", year := "2025-26", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end MuTax
