/-
  Retirement-plan and HSA limits for 2025 and 2026, recomputed from the statute.

  Published values: Notice 2025-67 ("2026 Amounts Relating to Retirement Plans and IRAs") states each 2026 amount
  and the 2025 amount it replaces (the 2025 amounts are those of Notice 2024-80); Rev. Proc. 2024-25 (HSA, 2025);
  Rev. Proc. 2025-19 (HSA, 2026). Texts: https://www.irs.gov/pub/irs-drop/{n-24-80,n-25-67,rp-24-25,rp-25-19}.pdf.

  Three indexing methods occur:
  * §415(d): CPI-U (not chained) for the calendar quarter ending September 30 of the preceding year over the base
    quarter, "adjustment procedures ... similar to" Social Security Act §215(i)(2)(A); increases rounded DOWN
    ($5,000 for §415(b)(1)(A) and anything adjusted "in the same manner" unless it says otherwise (§415(d)(4)(A)),
    $1,000 for §415(c)(1)(A), $500 for §402(g), §414(v)(2), §457(e)(15), §408(p)).
  * §1(f)(3) (C-CPI-U, 12 months ending August 31): §219(b)(5), §219(g)(8), §408A(c)(3)(D), §25B(b)(3).
  * §223(g): §1(f)(3) with §1(f)(4) read with "March 31" for "August 31"; increases rounded to the nearest $50.
-/
import TaxCode.Indexing.CPI
namespace TaxCode.Indexing.Retirement
open TaxCode.Indexing

set_option maxRecDepth 100000

/-! ## §415(d) quarterly CPI-U method -/

/-- CPI-U sum for July–September of year y (the quarter "beginning July 1" = "ending September 30"). -/
def q3 (y : Nat) : Nat := (cpiu.get? y 7).getD 0 + (cpiu.get? y 8).getD 0 + (cpiu.get? y 9).getD 0

/-- base increased by base × (Q3(cy-1)/Q3(baseYear) - 1), increase rounded down to a multiple of m -/
def adj415 (base baseYear cy m : Nat) : Nat := adjustND base (q3 (cy - 1)) (q3 baseYear) (.incDown m)

/-- (name, base, base quarter year, rounding, published 2025, published 2026) -/
def items415 : List (String × Nat × Nat × Nat × Nat × Nat) := [
  ("§415(b)(1)(A) defined benefit limit, base Q3 2001, $5,000",         160000, 2001, 5000, 280000, 290000),
  ("§415(c)(1)(A) defined contribution limit, base Q3 2001, $1,000",     40000, 2001, 1000, 70000, 72000),
  ("§402(g)(1)(B),(4) elective deferrals, base Q3 2005, $500",           15000, 2005, 500, 23500, 24500),
  ("§457(e)(15) governmental/tax-exempt deferrals, base Q3 2005, $500",  15000, 2005, 500, 23500, 24500),
  ("§414(v)(2)(B)(i),(C)(i) catch-up age 50+, base Q3 2005, $500",        5000, 2005, 500, 7500, 8000),
  ("§414(v)(2)(B)(ii),(C)(i) SIMPLE catch-up, base Q3 2005, $500",        2500, 2005, 500, 3500, 4000),
  ("§401(a)(17) compensation limit, base Q3 2001, $5,000",              200000, 2001, 5000, 350000, 360000),
  ("§414(q)(1)(B) highly compensated, base quarter ending 30 Sep 1996, $5,000 (§415(d)(4)(A))", 80000, 1996, 5000, 160000, 160000),
  ("§408(p)(2)(E)(i)(III),(iii)(I) SIMPLE deferral, base Q3 2004, $500",  10000, 2004, 500, 16500, 17000),
  ("§414(v)(7)(A),(E) Roth catch-up wage threshold, base Q3 2023, $5,000", 145000, 2023, 5000, 145000, 150000),
  ("§416(i)(1)(A)(i) key employee, base Q3 2001, $5,000",               130000, 2001, 5000, 230000, 235000)]

theorem limits415_2025 : items415.all (fun it => adj415 it.2.1 it.2.2.1 2025 it.2.2.2.1 == it.2.2.2.2.1) = true := by decide
theorem limits415_2026 : items415.all (fun it => adj415 it.2.1 it.2.2.1 2026 it.2.2.2.1 == it.2.2.2.2.2) = true := by decide

/-- Margins: unrounded 2025 §414(v)(2)(B)(i) catch-up = 7,997.26 and SIMPLE catch-up = 3,998.63 — $2.74 and $1.37
    below the next $500 step; §402(g) = 23,991.79 ($8.21 below $24,000). (cents, truncated) -/
theorem margins_2025 :
    500000 * q3 2024 / q3 2005 = 799726 ∧ 250000 * q3 2024 / q3 2005 = 399863 ∧ 1500000 * q3 2024 / q3 2005 = 2399179 := by decide

/-- §415(b)(1)(B) factor for participants separated before 2026: Q3 2025 / Q3 2024 = 1.02878..., published 1.0288. -/
theorem factor_415b1B : roundNear (10000 * q3 2025) (q3 2024) 1 = 10288 := by decide

/-- SECURE 2.0 amounts set from 2024/2025 figures (§414(v)(2)(B)(iii), (E); §408(p)(2)(E)(ii)) and their indexing
    from base quarter July 1, 2023 (2026): 110% × $3,500 = $3,850 (unchanged 2026); greater of $10,000 or 150% ×
    $7,500 = $11,250; greater of $5,000 or 150% × $3,500 = $5,250; 110% × $16,000 = $17,600 → $18,100 in 2026. -/
theorem secure2_amounts :
    110 * 3500 / 100 = 3850 ∧ adj415 3850 2023 2026 500 = 3850 ∧
    max 10000 (150 * 7500 / 100) = 11250 ∧ max 5000 (150 * 3500 / 100) = 5250 ∧
    110 * 16000 / 100 = 17600 ∧ adj415 17600 2023 2025 500 = 17600 ∧ adj415 17600 2023 2026 500 = 18100 := by decide

/-- §414(v)(2)(C)(i) last sentence indexes the age-60-to-63 amounts after 2025; from base Q3 2024 the 2026 increase
    ($11,250 × 2.88% = $324; $5,250 × 2.88% = $151) is below $500, so both stay. -/
theorem age60_63_2026 : adj415 11250 2024 2026 500 = 11250 ∧ adj415 5250 2024 2026 500 = 5250 := by decide

/-! ## §1(f)(3) C-CPI-U items -/

def adjF (base by_ cy : Nat) (r : Rnd) : Nat :=
  adjust (if cy = 2025 then ccpiu_v2024 else ccpiu_v2025) cpiu ccpiu_latest cpiu base (.year by_) cy r

/-- (name, base, base year, rounding, 2025, 2026) -/
def itemsF : List (String × Nat × Nat × Rnd × Nat × Nat) := [
  ("§219(b)(5)(A),(C)(i),(ii) IRA deductible amount, base 2007, amount down to $500", 5000, 2007, .amtDown 500, 7000, 7500),
  ("§219(b)(5)(B)(ii),(C)(iii) IRA catch-up, base 2022, amount down to $100", 1000, 2022, .amtDown 100, 1000, 1100),
  ("§219(g)(3)(B)(i),(8) active participant, joint, base 2005, nearest $1,000", 80000, 2005, .incNear 1000, 126000, 129000),
  ("§219(g)(3)(B)(ii),(8) active participant, other, base 2005", 50000, 2005, .incNear 1000, 79000, 81000),
  ("§219(g)(7)(A),(8) spouse of active participant, base 2005", 150000, 2005, .incNear 1000, 236000, 242000),
  ("§408A(c)(3)(B)(ii)(I),(D) Roth IRA, joint, base 2005", 150000, 2005, .incNear 1000, 236000, 242000),
  ("§408A(c)(3)(B)(ii)(II),(D) Roth IRA, other, base 2005", 95000, 2005, .incNear 1000, 150000, 153000),
  ("§25B(b)(1)(A),(3) saver's credit 50% tier, joint, base 2005, nearest $500", 30000, 2005, .incNear 500, 47500, 48500),
  ("§25B(b)(1)(B),(3) 20% tier, joint", 32500, 2005, .incNear 500, 51000, 52500),
  ("§25B(b)(1)(C),(3) 10% tier, joint", 50000, 2005, .incNear 500, 79000, 80500)]

theorem limitsF_2025 : itemsF.all (fun it => adjF it.2.1 it.2.2.1 2025 it.2.2.2.1 == it.2.2.2.2.1) = true := by decide
theorem limitsF_2026 : itemsF.all (fun it => adjF it.2.1 it.2.2.1 2026 it.2.2.2.1 == it.2.2.2.2.2) = true := by decide

/-- §25B(b)(2): head of household 75%, others 50% of the (adjusted) joint amounts; Notice 2025-67 figures. -/
theorem saver_credit_shares :
    [47500, 51000, 79000].map (fun x => 3 * x / 4) = [35625, 38250, 59250] ∧
    [48500, 52500, 80500].map (fun x => 3 * x / 4) = [36375, 39375, 60375] ∧
    [47500, 51000, 79000].map (· / 2) = [23750, 25500, 39500] ∧
    [48500, 52500, 80500].map (· / 2) = [24250, 26250, 40250] := by decide

/-- Phase-out ranges: §219(g)(2)(A)(ii) $10,000 ($20,000 joint active participant); §408A(c)(3)(A) $15,000 ($10,000
    joint). Published 2026: $81,000–$91,000; $129,000–$149,000; $242,000–$252,000; Roth $242,000–$252,000 and
    $153,000–$168,000. -/
theorem phaseout_ranges : 81000 + 10000 = 91000 ∧ 129000 + 20000 = 149000 ∧ 242000 + 10000 = 252000 ∧ 153000 + 15000 = 168000 := by decide

/-! ## §223(g) HSA amounts (12 months ending March 31) -/

def monthsMar (y : Nat) : List (Nat × Nat) :=
  [(y-1, 4), (y-1, 5), (y-1, 6), (y-1, 7), (y-1, 8), (y-1, 9), (y-1, 10), (y-1, 11), (y-1, 12), (y, 1), (y, 2), (y, 3)]
def ysumMar (s : Series) (y : Nat) : Nat := (monthsMar y).foldl (fun acc ym => acc + (s.get? ym.1 ym.2).getD 0) 0

/-- §223(g)(1): base years 1997 ((b)(2)) and 2003 ((c)(2)(A)) are before 2016, so
    ratio = C(cy-1)·P(2016) / (P(base)·C(2016)), every 12-month period ending March 31; increase to nearest $50. -/
def adjHSA (C : Series) (base by_ cy : Nat) : Nat :=
  adjustND base (ysumMar C (cy - 1) * ysumMar cpiu 2016) (ysumMar cpiu by_ * ysumMar C 2016) (.incNear 50)

/-- Rev. Proc. 2024-25 (2025): contribution $4,300 / $8,550; HDHP minimum deductible $1,650 / $3,300; out-of-pocket
    $8,300 / $16,600. Rev. Proc. 2025-19 (2026): $4,400 / $8,750; $1,700 / $3,400; $8,500 / $17,000.
    Family HDHP amounts are "twice the dollar amount in subclause (I)" (§223(c)(2)(A)(i)(II), (ii)(II)). -/
theorem hsa_2025 :
    [adjHSA ccpiu_mar_v2024 2250 1997 2025, adjHSA ccpiu_mar_v2024 4500 1997 2025,
     adjHSA ccpiu_mar_v2024 1000 2003 2025, adjHSA ccpiu_mar_v2024 5000 2003 2025] = [4300, 8550, 1650, 8300] ∧
    2 * 1650 = 3300 ∧ 2 * 8300 = 16600 := by decide

theorem hsa_2026 :
    [adjHSA ccpiu_mar_v2025 2250 1997 2026, adjHSA ccpiu_mar_v2025 4500 1997 2026,
     adjHSA ccpiu_mar_v2025 1000 2003 2026, adjHSA ccpiu_mar_v2025 5000 2003 2026] = [4400, 8750, 1700, 8500] ∧
    2 * 1700 = 3400 ∧ 2 * 8500 = 17000 := by decide

/-- The 2025 self-only contribution limit sits $0.30 above a rounding boundary: the exact amount is $4,275.30, so the
    increase ($2,025.30) rounds to $2,050; under $4,275 it would have been $4,250. With the C-CPI-U values as later
    revised (latest BLS values) it is $4,250 (`hsa_2025_latest`): the published figure depends on using the values
    as first published, which is what §1(f)(6)(A) prescribes. -/
theorem hsa_2025_margin :
    225000 * (ysumMar ccpiu_mar_v2024 2024 * ysumMar cpiu 2016) / (ysumMar cpiu 1997 * ysumMar ccpiu_mar_v2024 2016) = 427530 := by decide

theorem hsa_2025_latest : adjHSA ccpiu_latest 2250 1997 2025 = 4250 := by decide

end TaxCode.Indexing.Retirement
