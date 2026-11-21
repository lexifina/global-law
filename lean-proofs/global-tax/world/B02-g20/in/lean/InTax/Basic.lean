import TaxKernel.World

/-!
# India: income tax of a resident individual, financial year 2025-26 (assessment year 2026-27)

Access tier B. The Income-tax Act, 1961 governs FY 2025-26 (Global law holds only the new Income-tax Act, 2025, in force
from 2026-04-01, which does not apply to this year). Read, all saved in `in/law/` with sha256:
* Finance Bill 2025 (indiabudget.gov.in/budget2025-26/doc/Finance_Bill.pdf, sha256 78458589…), cl. 24: s. 115BAC (1A)
  new clause (iii) "for any previous year relevant to the assessment year beginning on or after the 1st April, 2026 …
  Upto Rs. 4,00,000 Nil; … 4,00,001 to 8,00,000 5 per cent … Above Rs. 24,00,000 30 per cent", and clause (ii) "or
  after" omitted; cl. 20: s. 87A first proviso "seven hundred thousand" → "twelve hundred thousand", "twenty-five
  thousand" → "sixty thousand" (clauses (a) rebate and (b) marginal relief), w.e.f. 1 April 2026.
* Memorandum to the Finance Bill 2025 (memo.pdf, sha256 7b8a4661…) IV: 87A proviso "rebate of income-tax … upto
  Rs.25,000 where the total income does not exceed Rs. 7,00,000 (clause (a)) and marginal relief where the total
  income exceeds (clause (b))"; cess "Health and Education Cess … 4% … inclusive of surcharge".
* Finance (No. 2) Bill 2024 cl. 10 (sha256 f95eed4c…): s. 16 (ia) proviso "where income-tax is computed under clause
  (ii) of sub-section (1A) of section 115BAC … "seventy-five thousand rupees"" (else fifty thousand: memo 2024).
* Income Tax Department, "Salaried Individuals for AY 2026-27" (incometax.gov.in, sha256 5ee84ddc…), official
  secondary for the enacted law: both regimes' slabs by age, surcharge 10 / 15 / 25 % (new) and 37 % (old, above 5
  crore) with marginal relief, 87A old regime "₹ 12,500 … shall not exceed 5,00,000", 80C "Combined deduction limit
  of ₹ 1,50,000".
The enacted Finance Act, 2025 text was not reached (egazette / indiacode are script-only); the Bill clauses agree
with the Department's published AY 2026-27 slabs.

* Rounding (W5 review pass 2, 2026-11-20): Income-tax Act 1961 s. 288A (Act 19 of 1968, w.e.f. 1.4.1969) "The amount of
  total income ... shall be rounded off to the nearest multiple of ten rupees ... if the last figure in that amount is
  five or more, the amount shall be increased to the next higher amount which is a multiple of ten and if the last figure
  is less than five, the amount shall be reduced ..."; s. 288B (Act 29 of 2006, w.e.f. 13.7.2006) "Any amount payable,
  and the amount of refund due, under the provisions of this Act shall be rounded off to the nearest multiple of ten
  rupees" (same rule). Bare-Act text from courtbook.in (incometaxindia.gov.in refused automated fetches), `in/law/w5/`,
  sha256 f76f2e1f… (288A), 964be79e… (288B). The rounding of s. 288B applies to the total payable (income tax +
  surcharge + cess of the person); the difference is booked on `incomeTax`.

Statute lead (FINDINGS F1): s. 16 (ia)'s 75,000 proviso refers to "clause (ii) of sub-section (1A) of section
115BAC", which after the Finance Bill 2025 covers AY 2025-26 only; AY 2026-27 is computed under the new clause (iii).
Read literally the new-regime standard deduction falls back to 50,000. Default here: 75,000 (the Department's
practice); `--sd-literal` gives the literal reading.
-/

namespace InTax
open TaxKernel

/-- s. 115BAC (1A) (iii) (Finance Bill 2025 cl. 24). -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (400000, 500), (800000, 1000), (1200000, 1500), (1600000, 2000), (2000000, 2500), (2400000, 3000)]
/-- Old regime (Department's AY 2026-27 table): under 60, 60-79, 80+. -/
def oldUnder60 : Schedule := Schedule.ofList [(0, 0), (250000, 500), (500000, 2000), (1000000, 3000)]
def old60 : Schedule := Schedule.ofList [(0, 0), (300000, 500), (500000, 2000), (1000000, 3000)]
def old80 : Schedule := Schedule.ofList [(0, 0), (500000, 2000), (1000000, 3000)]
def oldSched (age : Nat) : Schedule := if age ≥ 80 then old80 else if age ≥ 60 then old60 else oldUnder60

/-- The Department's printed cumulative amounts ("₹ 20,000 + 10% above ₹ 8,00,000", "₹ 1,12,500 + 30% above
₹ 10,00,000", …) equal the band sums. -/
def cumAt (s : Schedule) (x : Int) : Int := s.ticks x / BP
#guard cumAt sched 800000 = 20000 ∧ cumAt sched 1200000 = 60000 ∧ cumAt sched 1600000 = 120000 ∧ cumAt sched 2000000 = 200000 ∧
  cumAt sched 2400000 = 300000
#guard cumAt oldUnder60 1000000 = 112500 ∧ cumAt old60 1000000 = 110000 ∧ cumAt old80 1000000 = 100000

def sdNew : Int := 75000
def sdOld : Int := 50000
def cap80C : Int := 150000

/-- s. 87A: new regime (Finance Bill 2025 cl. 20): up to 60,000 if total income ≤ 12,00,000; above it the rebate is
the excess of the tax over the income above 12,00,000 (marginal relief, clause (b)). Old regime: up to 12,500 if
total income ≤ 5,00,000. -/
def rebateNew (ti tax : Int) : Int :=
  if ti ≤ 1200000 then min tax 60000 else pos (tax - (ti - 1200000))
def rebateOld (ti tax : Int) : Int := if ti ≤ 500000 then min tax 12500 else 0

/-- Surcharge with marginal relief (tax + surcharge may not exceed the tax at the threshold plus the income above it). -/
def surcharge (newRegime : Bool) (f : Int → Int) (ti : Int) : Int :=
  let tax := f ti
  let tiers : List (Int × Int) :=
    [(50000000, if newRegime then 2500 else 3700), (20000000, 2500), (10000000, 1500), (5000000, 1000)]
  match tiers.find? (fun (t, _) => ti > t) with
  | none => 0
  | some (t, r) =>
    let s := divR .down (r * tax) BP
    let prevRate := match tiers.find? (fun (t', _) => t' < t) with | some (_, r') => r' | none => 0
    let atT := f t + divR .down (prevRate * f t) BP
    let cap := atT + (ti - t) - tax
    pos (min s cap)

def cessRate : Int := 400

/-- Tax of one person under a regime (`true` = new): (income tax after rebate, surcharge, cess). -/
def regimeTax (newRegime : Bool) (age : Nat) (ti : Int) : Int × Int × Int :=
  let f : Int → Int := fun x => if newRegime then sched.tax Rule.unitDown (pos x) else (oldSched age).tax Rule.unitDown (pos x)
  let tax := f ti
  let reb := if newRegime then rebateNew ti tax else rebateOld ti tax
  let t1 := pos (tax - reb)
  let sc := surcharge newRegime f ti
  let cess := divR .down (cessRate * (t1 + sc)) BP
  (t1, sc, cess)

/-- s. 288A / 288B: nearest multiple of ten, a last figure of five or more rounds up (amounts are whole rupees here). -/
def round10 (x : Int) : Int := 10 * ((x + 5) / 10)
#guard round10 1234 = 1230 ∧ round10 1235 = 1240 ∧ round10 0 = 0 ∧ round10 1239 = 1240

structure PersonIn where
  age : Nat
  salary : Int     -- wages + pension (head "Salaries")
  business : Int
  other : Int      -- interest + dividends (head "Income from other sources")
  c80 : Int

def personTI (newRegime literal : Bool) (p : PersonIn) : Int :=
  let sd := if newRegime then (if literal then sdOld else sdNew) else sdOld
  let sal := pos (p.salary - min (pos p.salary) sd)
  let ded := if newRegime then 0 else min p.c80 cap80C
  round10 (pos (sal + p.business + p.other - ded))

def personBest (literal : Bool) (p : PersonIn) : Bool × Int × Int × Int × Int :=
  let tn := personTI true literal p
  let to := personTI false literal p
  let r288B (t : Int × Int × Int) : Int × Int × Int :=
    let tot := t.1 + t.2.1 + t.2.2
    (t.1 + (round10 tot - tot), t.2.1, t.2.2)
  let (a, b, c) := r288B (regimeTax true p.age tn)
  let (a', b', c') := r288B (regimeTax false p.age to)
  if a' + b' + c' < a + b + c then (false, to, a', b', c') else (true, tn, a, b, c)

def compute (literal : Bool) (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let ps := (c.adults.zip (List.range n)).map fun (a, i) =>
    ({ age := a.age, salary := a.wages + a.pension, business := a.selfEmployment,
       other := share (c.interest + c.dividends) i, c80 := if i = 0 then c.pensionContributions else 0 } : PersonIn)
  let rs := ps.map (personBest literal)
  let it := sumInts (rs.map fun r => r.2.2.1)
  let sc := sumInts (rs.map fun r => r.2.2.2.1)
  let ce := sumInts (rs.map fun r => r.2.2.2.2)
  Out.make c "IN" "INR" it (surtaxes := [("surcharge", sc), ("healthEducationCess", ce)])
    (detail := [Out.d "taxableIncome" (sumInts (rs.map fun r => r.2.1)),
      Out.dStr "regime" (String.intercalate "," (rs.map fun r => if r.1 then "new(115BAC)" else "old")),
      Out.dStr "standardDeductionNew" (if literal then "50000 (literal s.16(ia))" else "75000")])
    (unsupported := (if c.rentalIncome ≠ 0 then ["house property income (s. 24 deductions) not modelled; rentalIncome ignored"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains (special rates s. 111A/112/112A) not modelled; capitalGains ignored"] else []) ++
      ["employee provident fund (EPF Act 1952 / scheme para. 29) not reached: employeeSocial 0",
       "s. 80TTA/80TTB interest deductions not applied",
       "enacted Finance Act 2025 not reached: Finance Bill clauses + Department tables used (tier B)"])

def out (c : Canon) : Out := compute false c

def country : Country :=
  { code := "IN", name := "India (FY 2025-26, new and old regime)", currency := "INR", year := "2025-26", compute := out,
    computeWith := fun args c => compute (args.contains "--sd-literal") c }

theorem sched_progressive : sched.progressive = true := by decide

/- The rebate's marginal relief: just above 12,00,000 the tax is at most the income above 12,00,000. -/
/- s. 288A / 288B: salary 13,05,433 (new regime): total income 12,30,433 -> 12,30,430; tax 60,000 + 15 % x 30,430
= 64,564.5 -> 64,564 (unit down); 87A marginal relief: rebate 64,564 - 30,430 = 34,134, tax 30,430; cess 1,217;
payable 31,647 -> 31,650. -/
#guard let r := personBest false { age := 40, salary := 1305433, business := 0, other := 0, c80 := 0 }
  r.2.1 = 1230430 ∧ r.2.2.1 + r.2.2.2.1 + r.2.2.2.2 = 31650
#guard (List.range 20).all fun k => let ti := 1200000 + 5000 * (k : Int)
  let t := sched.tax Rule.unitDown ti; t - rebateNew ti t ≤ ti - 1200000

end InTax
