import GRTax.Theorems

/-! # Findings proved on concrete households (FINDINGS.md F1-F8). Money in cents. -/

namespace GRTax
open TaxKernel

/-- F1 (hidden top rate): above 40,000 € of taxable wages the 44 % band and the art. 16 withdrawal (2 %) stack,
so one more euro costs 46 % until the reduction is gone (50,850 € for a taxpayer without children; 68,000 € with
two children, 91,000 € with four). Proved for every income in the band, without children. -/
theorem hidden_46_band {x : Int} (h1 : eur 40000 ≤ x) (h2 : x + 100 < eur 50850) :
    (scale2020.ticks (x + 100) - BP * (creditTaper 2025 0).amount (x + 100))
      - (scale2020.ticks x - BP * (creditTaper 2025 0).amount x) = 4600 * 100 := by
  have hc : scale2020.ticks (x + (100 : Nat)) - scale2020.ticks x = 4400 * (100 : Nat) := by
    apply Schedule.ticks_const_rate
    intro i hi1 hi2
    simp only [eur] at h1 h2
    simp only [Schedule.rate, scale2020, eur, Schedule.ofList, bandsRate, List.map]
    repeat (first | split | omega)
  have hs : taper0.start ≤ x := by simp only [taper0, eur] at h1 ⊢; omega
  have hin : taper0.floor < taper0.amount (x + taper0.den) := by
    simp only [taper0, Taper.amount, Taper.reduction, divR, pos, eur] at h1 h2 ⊢; omega
  have ha : taper0.amount (x + 100) = taper0.amount x - 2 := Taper.amount_step taper0 taper0_wf hs hin
  rw [taper0_eq]
  simp only [BP]; push_cast at hc; omega

/-- Where the 46 % band ends, by number of children (taxable wages in euros): 12,000 + amount / 2 %. -/
theorem band_ends : (List.range 5).map (fun k => eur 12000 + creditFull 2025 k * 50) =
    [eur 50850, eur 57000, eur 68000, eur 79000, eur 91000] := by decide

/-- A household of two adults as the model sees it: net = wages − EFKA − tax + child benefit (cents). -/
def netPair (married : Bool) (w1 w2 : Int) (kids : Nat) (kidsWith2 : Bool) : Int :=
  let p1 : Person := { wages := w1, kids := if married || !kidsWith2 then kids else 0 }
  let p2 : Person := { wages := w2, kids := if married || kidsWith2 then kids else 0 }
  let k1 := personCalc 2025 p1
  let k2 := personCalc 2025 p2
  let ben := if married then childBenefit 2 kids (benefitIncome p1 k1 + benefitIncome p2 k2)
    else childBenefit 1 kids (if kidsWith2 then benefitIncome p2 k2 else benefitIncome p1 k1)
  w1 + w2 - k1.efka - k2.efka - k1.incomeTax - k2.incomeTax + ben

/-- F5 (child benefit, unmarried parents): a one-earner couple with two children and 23,907 € of wages (0.9 AW).
Married, the benefit is tested on both incomes at weight 1 + 1/2 + 2 × 1/4 (category 3: 672 €). Unmarried, with
the children declared by the parent without income, it is tested on that parent's income alone at the lone-parent
weights (category 1: 1,680 €); the earner loses the children in art. 16 (−343 €). Net gain of not marrying:
665 €. (Lead: whether OPEKA treats cohabiting unmarried parents as a lone-parent family is not settled here.) -/
theorem unmarried_children_gain :
    netPair false (eur 23907) 0 2 true - netPair true (eur 23907) 0 2 true = 66500 := by native_decide

/-- F4 in household terms: a married couple with two children, one earner. 34,629 € gross keeps the 672 €
benefit; 34,631 € loses it (taxable income after EFKA crosses 30,000 €): 2 € more pay, 671 € less net. -/
theorem benefit_notch_household :
    netPair true (eur 34629) 0 2 false - netPair true (eur 34631) 0 2 false > eur 600 := by native_decide

/-- F6 (rent split, known): 30,000 € of gross rent owned by one spouse costs 7,575 € (art. 40 par. 4); owned in
halves, 2 × 2,587.50 = 5,175 €: co-ownership saves 2,400 €. -/
theorem rent_split_gain :
    (rentScale 2025).tax Rule.unitHalfUp (rentNet (eur 30000))
      - 2 * (rentScale 2025).tax Rule.unitHalfUp (rentNet (eur 15000)) = eur 2400 := by native_decide

/-- F7 (art. 5Γ, known): a worker who moves the tax residence to Greece (not resident in 5 of the last 6 years)
pays tax on half the employment income for 7 years: on 80,000 € gross, 22,393.76 € becomes 7,250.76 €. -/
theorem art5G_gain :
    (personCalc 2025 { wages := eur 80000 }).incomeTax = 2239376 ∧
    (personCalc 2025 { wages := eur 80000, art5G := true }).incomeTax = 725076 := by native_decide

/-- F8 (owner-manager, known): 100 € of company profit paid as a dividend bears 22 % CIT (art. 58 par. 1(α))
and 5 % on the 78 € paid out (art. 40 par. 1) = 25.90 €; paid as salary to a single owner at the average wage
it bears 21.79 % employer EFKA on top (OECD 2025 ERCSSC/GEBT) plus 13.37 % employee EFKA and the 28 %
scale rate. -/
theorem dividend_route : eur 22 + (personCalc 2025 { dividends := eur 78 }).divTax = 2590 := by native_decide

/-- F10 (art. 28Α presumed minimum): a sole trader declaring 8,000 € of profit in the tenth year of business is
taxed on 12,320 € × 1.21 = 14,907.20 € (minimum wage lead 880 € × 14, unverified): 1,979.58 € instead of
720 €. -/
theorem art28A_minimum :
    (personCalc 2025 { selfEmp := eur 8000, presumedMin := 1490720 }).incomeTax = 197958 ∧
    (personCalc 2025 { selfEmp := eur 8000 }).incomeTax = 72000 := by native_decide

end GRTax
