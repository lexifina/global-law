import MtTax.Theorems

/-! # Malta: each finding of FINDINGS.md as a Lean statement on concrete households (by `decide` / `native_decide`) -/

namespace MtTax
open TaxKernel

/-- A one-line household builder. -/
def hh (adults : List Adult) (married : Bool := false) (kids : List Nat := []) (dividends : Int := 0) : Canon :=
  { id := "f", adults, married, children := kids.map fun a => { age := a }, dividends }

/-! ## F1 (statute-fault): art. 12(1)(c)(iii) dividend thresholds left at the YA 2025 band points -/

/-- A single owner with €17,000 salary and a €3,250 net dividend (gross €5,000) from his unlisted company, declared:
€2,500 of the gross is below the €19,500 "relevant threshold", so it is taxed at 25 % with the 35 % credit
refunded: €600 of income tax instead of €850 without the dividend (a €250 refund of company tax). Had the threshold
followed the YA 2026 table's 25 % band (€16,000), the whole dividend would be exempt and nothing refunded. -/
theorem f1_refund_below_stale_threshold :
    incomeTax (hh [{ age := 40, wages := 17000 }] (dividends := 3250))
      { dividendsDeclared := true, unlisted := true } = 600 ∧
    incomeTax (hh [{ age := 40, wages := 17000 }] (dividends := 3250)) {} = 850 := by native_decide

/-- The stale thresholds sit inside the YA 2026 25 % band (single 16,000-60,000, married 23,000-60,000, parent
17,500-60,000): the marginal rate there is 25 %, so each euro of gross dividend below them earns a 10-cent refund. -/
theorem f1_thresholds_inside_25pct_band :
    singleSched.rate (divThresholdSingle - 1) = 2500 ∧ marriedSched.rate (divThresholdMarried - 1) = 2500 ∧
    parentSched.rate (divThresholdParent - 1) = 2500 := by decide

/-! ## F2 (statute-fault, next year): Act III of 2026, parent with one child, "subtracting €10,270" -/

/-- One euro more at €60,000 costs €5.35 (535 cents): the 35 % formula is €5 above the 25 % one at the joint. -/
theorem f2_parent1_2027_jump : parent1YA2027 60001 - parent1YA2027 60000 = 535 := by decide
/-- With €10,275 the table would be continuous: 25 % × 60,000 − 4,275 = 35 % × 60,000 − 10,275. -/
theorem f2_continuous_with_10275 : 25 * 60000 - 427500 = 35 * 60000 - 1027500 := by decide

/-! ## F3 (historical): the YA 2025 tables (income 2024) had notches that YA 2026 removed -/

theorem f3_single_2025_notch : singleYA2025 19501 - singleYA2025 19500 = 9025 := by decide
theorem f3_married_2025_notch : marriedYA2025 28701 - marriedYA2025 28700 = 12025 := by decide
theorem f3_parent_2025_notch : parentYA2025 21201 - parentYA2025 21200 = 10525 := by decide

/-! ## F4 (statute drafting): "exceeds X but is less than Y" / "exceeds Y" leaves Y without a formula -/

/-- At each uncovered point both neighbouring formulas give the same tax, so the gap costs nothing. -/
theorem f4_gaps_harmless :
    (15 * 16000 - 180000 = 25 * 16000 - 340000) ∧ (25 * 60000 - 340000 = 35 * 60000 - 940000) ∧
    (15 * 23000 - 225000 = 25 * 23000 - 455000) ∧ (25 * 60000 - 455000 = 35 * 60000 - 1055000) ∧
    (15 * 17500 - 195000 = 25 * 17500 - 370000) ∧ (25 * 60000 - 370000 = 35 * 60000 - 970000) := by decide

/-! ## F5 (gov-error): L.N. 10 of 2025, Tenth Schedule Part I, categories C and D as printed -/

/-- The rows as printed for a person born in 1962 or after (weekly wage in cents): category C "exceeds €213.55 but
does not exceed €523.28" (10 %), the €53.23 row of category D "exceeds €515.99". -/
def lnRowC (w : Int) : Bool := decide (21355 ≤ w ∧ w ≤ 52328)
def lnRowD53 (w : Int) : Bool := decide (w > 51599)

/-- At €516.00 a week both rows apply, at 10 % (€51.60) and at €53.23: €1.63 a week apart, €84.76 a year; from
€523.29 to €532.29 only the flat €53.23 applies although 10 % of the wage is less. -/
theorem f5_overlap : lnRowC 51600 = true ∧ lnRowD53 51600 = true ∧ 5323 - 51600 / 10 = 163 ∧ 52 * 163 = 8476 := by
  decide
theorem f5_gap_for_old_cohort_literal : lnRowC 52329 = false ∧ lnRowD53 52329 = true := by decide

/-! ## F6 (loophole-known): joint computation is the default; separate computation saves up to €8,850 -/

theorem f6_separate_saves_8250 :
    incomeTax (hh [{ wages := 60000 }, { wages := 60000 }] true) {} = 31450 ∧
    incomeTax (hh [{ wages := 60000 }, { wages := 60000 }] true) { separate := true } = 23200 := by native_decide

theorem f6_separate_saves_8850_with_child :
    incomeTax (hh [{ wages := 60000 }, { wages := 60000 }] true [4]) { separate := true } = 22600 := by native_decide

/-- Two parents on €13,000 each pay nothing apart and €1,950 together (the default). -/
theorem f6_low_earners :
    incomeTax (hh [{ wages := 13000 }, { wages := 13000 }] true [4]) {} = 1950 ∧
    incomeTax (hh [{ wages := 13000 }, { wages := 13000 }] true [4]) { separate := true } = 0 := by native_decide

/-! ## F7 (loophole-new? notch): a lone parent loses the married table on any maintenance or on living with the other
parent (art. 56(1)(b) proviso (b)(iii)-(iv)): up to €850 a year -/

theorem f7_lone_parent_cliff :
    incomeTax (hh [{ wages := 23000 }] (kids := [4])) {} = 1200 ∧
    incomeTax (hh [{ wages := 23000 }] (kids := [4])) { loneParent := false } = 2050 := by native_decide

/-- The largest gap between the married and parent tables is €850 (at €23,000 and above). -/
theorem f7_gap_le_850 (x : Int) (h : 0 ≤ x) : parentFormula x - marriedFormula x ≤ 85000 := by
  simp only [parentFormula, marriedFormula, formulaCents]
  repeat' split
  all_goals omega

/-! ## F8 (known design): the Class One minimum is a €1,110 notch at the first euro of wages -/

theorem f8_class1_floor : class1Weekly 40 1 = 2135 ∧ toEuro (52 * 2135) = 1110 := by decide

/-! ## F9 (owner-manager): all-dividend pay avoids Class One on both sides; above €19,500 the art. 12 exemption
makes the 35 % company tax final -/

theorem f9_owner_dividend_declared :
    incomeTax (hh [{ age := 40 }] (dividends := 21364)) { dividendsDeclared := true, unlisted := true } = -5350 :=
  by native_decide

/-! ## Validation against EUROMOD CR MT 2021-2024 (2024 system), computed rather than copied -/

/-- EUROMOD §2.5.4: the weekly rate "cannot exceed the maximum of €24.08" and "cannot be lower than the minimum of
€8.66": the Fourteenth Schedule formula gives both. -/
theorem v_ca_max_min : caWeeklyPerChild 0 = 2408 ∧ caWeeklyPerChild 30000 = 866 := by decide
/-- EUROMOD Table 2.18/2.19: maximum €53.23 a week = 10 % of the €27,679 maximum pensionable income / 52. -/
theorem v_class1_max : class1Weekly 40 27679 = 5323 ∧ class1Weekly 70 0 = 0 ∧ class1Weekly 64 30000 = 4231 := by decide

end MtTax
