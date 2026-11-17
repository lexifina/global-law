import TaxCode.Individual.B.Deductions
import TaxCode.Individual.A.Adjustments

/-!
# Standard deduction (worksheet for dependents, line 12 chart), IRA deduction worksheet, student loan interest
# worksheet (2025 Form 1040 instructions) against §63(c), §219(g), §221(b)

Form text: 2025 Instructions for Form 1040: "Standard Deduction Worksheet for Dependents—Line 12e" (lines 1–4c),
"Standard Deduction Chart for People Who Were Born Before January 2, 1961, or Were Blind" (amounts as printed),
"IRA Deduction Worksheet—Schedule 1, Line 20" (lines 2, 6, 7), "Student Loan Interest Deduction Worksheet—Schedule 1,
Line 21" (lines 1, 5–9).

Statute: §63(c)(2), (5), (7) and (f) (2025: $15,750 / $31,500 / $23,625; dependents $1,350 or earned income + $450;
additional $1,600, $2,000 unmarried — Rev. Proc. 2024-40 as modified by Pub. L. 119-21, the model's
`B.basicStandard`, `B.dependentFloor`, `B.dependentAddOn`, `B.additionalUnit`); §219(g)(2) via `A.phaseReduction`;
§221(b)(2) ($85,000/$170,000 and $15,000/$30,000 for 2025).
-/

namespace TaxCode.Forms.Deductions
open TaxCode.Individual

/-! ## Standard deduction -/

/-- The chart as printed: (filing status, boxes checked, standard deduction). -/
def chart : List (Filing × Int × Int) :=
  [(.single, 1, 17750), (.single, 2, 19750),
   (.mfj, 1, 33100), (.mfj, 2, 34700), (.mfj, 3, 36300), (.mfj, 4, 37900),
   (.qss, 1, 33100), (.qss, 2, 34700),
   (.mfs, 1, 17350), (.mfs, 2, 18950), (.mfs, 3, 20550), (.mfs, 4, 22150),
   (.hoh, 1, 25625), (.hoh, 2, 27625)]

/-- §63(c)(1)–(3), (f): basic plus additional amounts. -/
def stdStatute (f : Filing) (boxes : Int) : Int := B.basicStandard f + boxes * B.additionalUnit f

/-- **Every amount in the printed chart is §63(c) + (f)** (all 14 rows: the QSS rows use the married $1,600, as
§63(f)(3) — "not married and is not a surviving spouse" — requires). -/
theorem chart_eq_statute : chart.all (fun (f, n, v) => v == stdStatute f n) = true := by decide

/-- Standard Deduction Worksheet for Dependents: line 2 "Is your earned income more than $900? Yes. Add $450 to your
earned income. No. Enter $1,350"; line 3 $15,750 / $31,500 / $23,625; line 4a "the smaller of line 2 or line 3";
line 4b boxes × "$1,600 ($2,000 if single or head of household)"; line 4c "Add lines 4a and 4b". -/
def depWorksheet (f : Filing) (earned boxes : Int) : Int :=
  let l2 := if earned > 900 then earned + 450 else 1350
  let l3 := match f with | .single | .mfs => 15750 | .mfj => 31500 | .hoh => 23625 | .qss => 31500
  let l4b := boxes * (match f with | .single | .hoh => 2000 | _ => 1600)
  min l2 l3 + l4b

/-- §63(c)(5): the basic standard deduction of a dependent "shall not exceed the greater of (A) $500 [$1,350 for
2025], or (B) the sum of $250 [$450] and such individual's earned income"; plus (f). -/
def depStatute (f : Filing) (earned boxes : Int) : Int :=
  min (B.basicStandard f) (max B.dependentFloor (B.dependentAddOn + earned)) + boxes * B.additionalUnit f

/-- **The worksheet is §63(c)(5) + (f) for every earned income and box count.** (The worksheet's earned income
footnote also counts taxable scholarships, which §63(c)(5)(B) does not mention; not modelled.) -/
theorem depWorksheet_eq (f : Filing) (e n : Int) : depWorksheet f e n = depStatute f e n := by
  unfold depWorksheet depStatute B.basicStandard B.basicOther B.dependentFloor B.dependentAddOn B.additionalUnit
  cases f <;> simp <;> split <;> omega

/-! ## IRA deduction worksheet, line 7 -/

/-- Line 7: "Multiply lines 6a and 6b by the percentage ... If the result isn't a multiple of $10, increase it to the
next multiple of $10 ... If the result is $200 or more, enter the result. But if it is less than $200, enter $200."
Percentages: 70%/80% (range $10,000), 35%/40% (range $20,000) = limit ÷ range. `l6` = line 2 − line 5 (MAGI below
the end of the range), 0 < l6 < range. -/
def iraL7 (L R l6 : Int) : Int := max 200 ((L * l6 + 10 * R - 1) / (10 * R) * 10)

/-- §219(g)(1)–(2): limit less the reduction "rounded to the next lowest $10", not below $200 before full phase-out.
`e` = MAGI over the applicable dollar amount = range − line 6. -/
def iraStat (L R e : Int) : Int := max 200 (L - A.phaseReduction L e R)

/-- **IRA worksheet line 7 = §219(g)(2) for every MAGI inside the phase-out range, for all four limit/range pairs**
($7,000/$8,000 × $10,000/$20,000): rounding the deduction UP to $10 is rounding the reduction DOWN to $10. -/
theorem iraL7_eq (L R l6 : Int) (hLR : (L = 7000 ∨ L = 8000) ∧ (R = 10000 ∨ R = 20000)) (h0 : 0 < l6) (h1 : l6 < R) :
    iraL7 L R l6 = iraStat L R (R - l6) := by
  unfold iraL7 iraStat A.phaseReduction
  rw [if_neg (by omega)]
  rcases hLR with ⟨hL | hL, hR | hR⟩ <;> subst hL hR <;> omega

/-! ## Student loan interest worksheet -/

/-- Lines 6–9 in ten-thousandths of a dollar: line 7 "Divide line 6 by $15,000 ($30,000 ...). Enter the result as a
decimal (rounded to at least three places). If the result is 1.000 or more, enter 1.000" (three places, half up);
line 8 "Multiply line 1 by line 7"; line 9 "Subtract line 8 from line 1". -/
def sliWorksheet (l1 l6 R : Int) : Int :=
  let d := min 1000 ((2000 * l6 + R) / (2 * R))   -- thousandths
  10000 * l1 - 10 * l1 * d

/-- §221(b)(2)(B) exactly (ten-thousandths, floored): the interest less interest × excess / range, not below zero. -/
def sliStatute (l1 e R : Int) : Int := max 0 (10000 * l1 - 10000 * l1 * min e R / R)

/-- The three-place rounding of line 7 moves the deduction by at most $2,500 × 0.0005 = $1.25 either way (a stated
rounding rule, not a finding; the general bound is not proved here — it is nonlinear in line 1 × line 7). At the
largest rounding step, $2,500 of interest and MAGI $85,000 + $7 (line 7 = 0.000467 → 0.000): the worksheet allows
$2,500.00, the statute $2,498.83. -/
theorem sli_example : sliWorksheet 2500 7 15000 = 25000000 ∧ sliStatute 2500 7 15000 = 24988334 := by decide

end TaxCode.Forms.Deductions

#print axioms TaxCode.Forms.Deductions.chart_eq_statute
#print axioms TaxCode.Forms.Deductions.depWorksheet_eq
#print axioms TaxCode.Forms.Deductions.iraL7_eq
