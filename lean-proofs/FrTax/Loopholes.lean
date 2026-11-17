import FrTax.Liquidation

/-!
# Loopholes: surprising outcomes of the rules as written (LOOPHOLES.md)

Each theorem states a finding of the loophole hunt about the model's own functions (`tableTax`, `cdhr`,
`compute`). Three kinds of proof:

* **`decide`** (kernel evaluation, no extra axiom) for statements about the scale functions on concrete numbers,
  including statements over every integer of a range (`allIn`, kernel-checked with `decide +kernel`).
* **`omega`** for the general statement about the CDHR (every household, every amount).
* **`native_decide`** for statements about whole returns (`compute` on a `Decl`). A `Decl` holds its boxes in a
  `Std.HashMap String Int`, and `String.hash` is opaque to the kernel, so the kernel cannot evaluate `compute`;
  these are checked by compiled evaluation, which adds an axiom (`#print axioms` below names it).

"Burden" is what the household pays on the return: net income tax (refunds negative), CEHR, CDHR, social levies
assessed on the return and the micro-entrepreneurs' flat levy (as harness/loop_lib.py).
Every concrete household here was also run through Mlang (the DGFiP's M code) and the DGFiP's production
simulator (runs/loop/sim.jsonl): same amounts paid or refunded.
-/

namespace FrTax.Loophole

open FrTax

/-- `f R` holds for every integer `R` in `[lo, lo + n)`. -/
def allIn (lo : Int) : Nat → (Int → Bool) → Bool
  | 0, _ => true
  | n + 1, f => f lo && allIn (lo + 1) n f

/-- A return from its boxes. -/
def mk (y : Nat) (l : List (String × Int)) : Decl := { year := y, boxes := Std.HashMap.ofList l }

/-- What the household pays on the return (refunds negative). -/
def burden (p : Params) (d : Decl) : Int :=
  let r := compute p d
  r.net + r.cehr + r.cdhr + r.social + flatLevyPaid d

/-! ## 1. A gift that pays for itself (art. 200 with the 61 € threshold of art. 1657, 1 bis)

Reductions come off before the 61 € test (BOI-IR-LIQ-20-20-40 § 60), so a household whose tax after the décote is
`t` between 61 € and 239 € can give `giftNeeded t` euros to an aid organisation (75 %, art. 200, 1 ter), bring the
tax under 61 € and pay nothing: the gift is always smaller than the tax it removes. -/

/-- The smallest gift at 75 % that brings a tax of `t` under 61 €. -/
def giftNeeded (t : Int) : Int := (4 * (t - 60)) / 3

theorem gift_cheaper_than_tax :
    allIn 61 179 (fun t => decide (giftNeeded t < t) && decide (t - pct 7500 (giftNeeded t) < 61)) = true := by
  decide +kernel

/-- The 2025 case: a single person with a 19 600 € salary (taxable income 17 640 €) owes 67 €; a 9 € gift gives a
7 € reduction, the tax falls to 60 € and is not collected. Scale part. -/
theorem gift_pays_2025_scale : tableTax p2025 0 4 17640 = 67 ∧ pct 7500 9 = 7 ∧ 67 - 7 < 61 := by decide

/-- The same household, whole return. Production simulator: 67 € to pay; with the gift "Impôt sur le revenu net
60 €", nothing to pay. -/
theorem gift_pays_2025 :
    burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("1AJ", 19600)]) = 67 ∧
    burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("1AJ", 19600), ("7UD", 9)]) = 0 := by
  native_decide

/-! ## 2. Refundable credits pay the uncollected tax (art. 199 sexdecies with art. 1657, 1 bis)

A tax under 61 € is not collected, but a credit is first imputed on it and only the excess is refunded
(BOI-IR-LIQ-20-20-40 § 90). A single person with a 19 500 € salary owes 54 €, not collected; 2 000 € of home help
earns a 1 000 € credit but a refund of 946 €. With a 15 000 € salary (no tax) the refund is 1 000 €. -/
theorem credit_pays_uncollected_tax_2025 :
    burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("1AJ", 19500)]) = 0 ∧
    burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("1AJ", 19500), ("7DB", 2000)]) = -946 ∧
    burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("1AJ", 15000), ("7DB", 2000)]) = -1000 := by
  native_decide

/-! ## 3. The 2025 CDHR takes back every reduction and credit it does not list (art. 224, III and IV, A, 2°)

The CDHR is `20 %` of the revenue (smoothed under 330 000 € / 660 000 €) less the income tax, the CEHR and fixed
amounts. Any reduction or credit that lowers the income tax used there (anything art. 224, IV, A, 2° does not add
back: for income 2025, gifts of art. 200, home help, care homes, school fees...) raises the CDHR by as much, as long
as the CDHR stays positive. General statement, every household and amount: -/

/-- The first amount of art. 224, III, 1° after the smoothing of V, as `cdhr` computes it. -/
def cdhrA (d : Decl) (r : Int) : Int :=
  let thr : Int := if d.couple then 500000 else 250000
  let a := pct 2000 r
  if r ≤ (if d.couple then 660000 else 330000) then min a (pct 8250 (r - thr)) else a

theorem cdhr_eq (d : Decl) (rfr x ce : Int) (hy : d.year = 2025) :
    cdhr d rfr x ce = if cdhrBase d rfr ≤ (if d.couple then 500000 else 250000) then 0
      else pos (cdhrA d (cdhrBase d rfr) - (x + ce + (if d.couple then 12500 else 0) + 1500 * dependants d)) := by
  simp only [cdhr, cdhrA, hy, ne_eq, not_true_eq_false, ↓reduceIte]

/-- **Neutralisation.** For income 2025, if a household pays CDHR with income tax `t` and with income tax `t'`, it
pays the same income tax + CDHR in both cases: a reduction or credit that turns `t` into `t'` is worth nothing. -/
theorem cdhr_neutral (d : Decl) (rfr t t' ce : Int) (hy : d.year = 2025)
    (h : 0 < cdhr d rfr t ce) (h' : 0 < cdhr d rfr t' ce) :
    t + cdhr d rfr t ce = t' + cdhr d rfr t' ce := by
  rw [cdhr_eq d rfr t ce hy] at h ⊢
  rw [cdhr_eq d rfr t' ce hy] at h' ⊢
  generalize cdhrA d (cdhrBase d rfr) = A at *
  generalize (if d.couple then (12500 : Int) else 0) = K at *
  generalize 1500 * dependants d = n at *
  by_cases hc : cdhrBase d rfr ≤ (if d.couple then 500000 else 250000)
  · simp only [hc, ↓reduceIte] at h
    omega
  · simp only [hc, ↓reduceIte, pos] at h h' ⊢
    omega

/-- The concrete case (production simulator: 63 525 € to pay in all three; the CDHR line moves from 21 251 € to
26 251 € and 22 815 €). A single person, salary 30 000 €, dividends 300 000 € under the flat tax: 10 000 € of home
help (credit 5 000 €) or 10 000 € of gifts (reduction 1 564 €, within 20 % of taxable income) save nothing. The
scale option (2OP), normally ruinous at this income, saves 1 333 € because the CDHR base leaves out the 40 %
dividend allowance (art. 224, II, 1°). -/
theorem cdhr_payer_2025 :
    let b : List (String × Int) := [("0AC", 1), ("0DA", 1980), ("1AJ", 30000), ("2DC", 300000), ("2BH", 300000)]
    burden p2025 (mk 2025 b) = 63525 ∧
    burden p2025 (mk 2025 (b ++ [("7DB", 10000)])) = 63525 ∧
    burden p2025 (mk 2025 (b ++ [("7UF", 10000)])) = 63525 ∧
    burden p2025 (mk 2025 (b ++ [("2OP", 1)])) = 62192 := by
  native_decide

/-! ## 4. A marginal rate above 100 % (art. 224, V with the social levies), income 2025

In the CDHR's smoothing band the income tax, CEHR and CDHR together take 82.5 % of each extra euro of revenue; on
investment income taxed at the flat rate whose social levies are assessed on the return (10.6 % CSG for income
2025, CRDS 0.5 %, solidarity levy 7.5 %: 18.6 %), each 1 000 € of dividends costs 1 011 €. -/

/-- A single person living on dividends: every 1 000 € step from 298 000 € to 330 000 € costs 1 011 €. -/
theorem emtr_over_100_single_2025 :
    (List.range 32).all (fun i =>
      let D : Int := 298000 + 1000 * (i : Int)
      burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("2DC", D + 1000)])
        - burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("2DC", D)]) = 1011) = true := by
  native_decide

/-- A married couple: every 1 000 € step from 615 000 € to 660 000 € costs 1 011 €. -/
theorem emtr_over_100_couple_2025 :
    (List.range 45).all (fun i =>
      let D : Int := 615000 + 1000 * (i : Int)
      burden p2025 (mk 2025 [("0AM", 1), ("0DA", 1980), ("0DB", 1980), ("2DC", D + 1000)])
        - burden p2025 (mk 2025 [("0AM", 1), ("0DA", 1980), ("0DB", 1980), ("2DC", D)]) = 1011) = true := by
  native_decide

/-- Production simulator on the first step: 97 050 € and 98 061 € to pay. -/
theorem emtr_example_2025 :
    burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("2DC", 300000)]) = 97050 ∧
    burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("2DC", 301000)]) = 98061 := by
  native_decide

/-! ## 5. An adult child: attaching costs more than deducting alimony (art. 6, 3; 196 B; 156, II, 2°)

A married couple with a minor child and a 20-year-old student. Attached, the student brings a half part (3 parts,
capped at 1 807 € per half part, art. 197, I, 2). Not attached, the parents deduct up to 6 855 € of alimony and the
student, taxed alone on it (after the 10 % allowance: 6 169 €), owes nothing. For every taxable income from
176 002 € to 369 999 € (income 2025) attaching costs at least 1 003 € more. -/

theorem student_alone_owes_nothing_2025 : tableTax p2025 0 4 6169 = 0 := by decide

set_option maxHeartbeats 0 in
set_option maxRecDepth 100000 in
/-- Kernel-checked over every integer of [176 002, 200 002). -/
theorem attach_costs_more_kernel_2025 :
    allIn 176002 24000 (fun R => decide (tableTax p2025 4 10 (R - 6855) + 1003 ≤ tableTax p2025 4 12 R)) = true := by
  decide +kernel

/-- The whole band [176 002, 370 000) (compiled evaluation). -/
theorem attach_costs_more_2025 :
    allIn 176002 (370000 - 176002) (fun R => decide (tableTax p2025 4 10 (R - 6855) + 1003 ≤ tableTax p2025 4 12 R)) = true := by
  native_decide

/-- Production simulator, salaries 120 000 € + 80 000 €: attached 37 787 €; alimony 36 783 € + 0 € for the student. -/
theorem attach_example_2025 :
    burden p2025 (mk 2025 [("0AM", 1), ("0DA", 1975), ("0DB", 1975), ("0CF", 1), ("0DJ", 1), ("1AJ", 120000), ("1BJ", 80000)]) = 37787 ∧
    burden p2025 (mk 2025 [("0AM", 1), ("0DA", 1975), ("0DB", 1975), ("0CF", 1), ("6EL", 6855), ("1AJ", 120000), ("1BJ", 80000)]) = 36783 ∧
    burden p2025 (mk 2025 [("0AC", 1), ("0DA", 2005), ("1AO", 6855)]) = 0 := by
  native_decide

/-! ## 6. One more euro, 62 € less tax (art. 197 C rounding with art. 1657, 1 bis), income 2020

A couple with a child, salaries 12 500 € each, micro-entrepreneur services under the flat levy. The effective-rate
tax of art. 197 C is rounded twice (the tax on all income, then the share); one more euro of turnover lowers it by
1 €, from 62 € to 60 €, under the collection threshold. Production simulator: 62 € to pay, then 0 €. -/
theorem one_euro_less_tax_2020 :
    burden p2020 (mk 2020 [("0AM", 1), ("0DA", 1980), ("0DB", 1980), ("0CF", 1), ("1AJ", 12500), ("1BJ", 12500), ("5TB", 35753)]) = 670 ∧
    burden p2020 (mk 2020 [("0AM", 1), ("0DA", 1980), ("0DB", 1980), ("0CF", 1), ("1AJ", 12500), ("1BJ", 12500), ("5TB", 35754)]) = 608 ∧
    (compute p2020 (mk 2020 [("0AM", 1), ("0DA", 1980), ("0DB", 1980), ("0CF", 1), ("1AJ", 12500), ("1BJ", 12500), ("5TB", 35753)])).net = 62 ∧
    (compute p2020 (mk 2020 [("0AM", 1), ("0DA", 1980), ("0DB", 1980), ("0CF", 1), ("1AJ", 12500), ("1BJ", 12500), ("5TB", 35754)])).net = 0 := by
  native_decide

/-- Flat-levy income that is not taxed still removes the art. 157 bis allowance (tested on the total income for
the effective rate): a disabled single person, salary 25 000 €, one more euro of flat-levy turnover costs 108 €
(income 2023; production simulator 328 € then 436 €). -/
theorem flat_levy_removes_157bis_2023 :
    (compute p2023 (mk 2023 [("0AC", 1), ("0DA", 1980), ("0AP", 1), ("1AJ", 25000), ("5TB", 10341)])).net = 328 ∧
    (compute p2023 (mk 2023 [("0AC", 1), ("0DA", 1980), ("0AP", 1), ("1AJ", 25000), ("5TB", 10342)])).net = 436 := by
  native_decide

/-! ## 7. Marriage and separation -/

/-- Two pensioners with 90 000 € each pay 1 819 € more married than single: the 10 % pension allowance is capped
per household (art. 158, 5, a: 4 439 €), not per pensioner. Production: 39 581 € vs 2 × 18 881 €. -/
theorem pensioners_marriage_penalty_2025 :
    burden p2025 (mk 2025 [("0AM", 1), ("0DA", 1950), ("0DB", 1950), ("1AS", 90000), ("1BS", 90000)])
      - 2 * burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1950), ("1AS", 90000)]) = 1819 := by
  native_decide

/-- Separated parents of two children in shared residence, each living alone (box T), pay 4 257 € less than as a
married couple (salaries 100 000 € and 50 000 €): each return's quarter parts are capped at 4 262 € (art. 197, I,
2, second paragraph) instead of 1 807 € per half part. Production: 23 094 € vs 16 439 € + 2 398 €. -/
theorem separation_bonus_2025 :
    burden p2025 (mk 2025 [("0AM", 1), ("0DA", 1980), ("0DB", 1980), ("0CF", 2), ("1AJ", 100000), ("1BJ", 50000)])
      - burden p2025 (mk 2025 [("0AD", 1), ("0DA", 1980), ("0BT", 1), ("0CH", 2), ("1AJ", 100000)])
      - burden p2025 (mk 2025 [("0AD", 1), ("0DA", 1980), ("0BT", 1), ("0CH", 2), ("1AJ", 50000)]) = 4257 := by
  native_decide

/-! ## 8. Actual expenses that cost more than the allowance (art. 83, 3° with art. 199 quater C) -/

/-- Salary 40 000 €, union dues 400 €, actual expenses 4 200 € (200 € above the 10 % allowance) plus the dues:
claiming them costs 84 € more, because the 66 % union-dues credit is lost to whoever claims actual expenses.
Production: 3 640 € vs 3 724 € (Mlang refuses the second return, anomaly I00101). -/
theorem union_dues_trap_2025 :
    burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("1AJ", 40000), ("7AC", 400)]) = 3640 ∧
    burden p2025 (mk 2025 [("0AC", 1), ("0DA", 1980), ("1AJ", 40000), ("7AC", 400), ("1AK", 4600)]) = 3724 := by
  native_decide

/-! ## Axioms -/
#print axioms gift_cheaper_than_tax
#print axioms gift_pays_2025_scale
#print axioms gift_pays_2025
#print axioms credit_pays_uncollected_tax_2025
#print axioms cdhr_neutral
#print axioms cdhr_payer_2025
#print axioms emtr_over_100_single_2025
#print axioms emtr_over_100_couple_2025
#print axioms emtr_example_2025
#print axioms student_alone_owes_nothing_2025
#print axioms attach_costs_more_kernel_2025
#print axioms attach_costs_more_2025
#print axioms attach_example_2025
#print axioms one_euro_less_tax_2020
#print axioms flat_levy_removes_157bis_2023
#print axioms pensioners_marriage_penalty_2025
#print axioms separation_bonus_2025
#print axioms union_dues_trap_2025

end FrTax.Loophole
