import PlTax.Withholding

/-!
# Kernel-checked facts about named households (FINDINGS.md F-numbers)

Each fact is proved by `decide` (the kernel evaluates the model; no `native_decide`). `netOf` = gross − income tax −
employee contributions + benefits, whole złoty.
-/

namespace PlTax

def netOf (h : Household) : Int :=
  let r := compute h
  (h.adults.foldl (fun a p => a + p.wages + p.se + p.pension) 0) - r.incomeTax - r.employeeSocial + r.benefits

/-! ## F3 The one-child income limit (art. 27f ust. 2 pkt 1, 112 000 / 56 000 zł since 2013) is a notch -/

def oneChild (w : Int) : Household := { adults := [{ wages := w }], children := [5] }
def oneChildCouple (w : Int) : Household := { adults := [{ wages := w }, { wages := 0 }], married := true, children := [5] }

/-- One more złoty of salary (133 271 → 133 272 zł; art. 27f ust. 2a income crosses 112 000 zł) costs a single parent
1 112 zł of net income: the whole relief for the year. -/
theorem oneChild_notch : netOf (oneChild 133271) - netOf (oneChild 133272) = 1112 := by decide
theorem oneChildCouple_notch : netOf (oneChildCouple 133271) - netOf (oneChildCouple 133272) = 1112 := by decide
/-- The salary must rise by 1 632 zł (to 134 903 zł) before net income is back where it was: a band of 1 632 zł in
which the effective marginal rate exceeds 100 %. -/
theorem oneChild_band : netOf (oneChild 134902) < netOf (oneChild 133271) ∧
    netOf (oneChild 133271) ≤ netOf (oneChild 134903) := by decide

/-! ## F4 Ryczałt health contribution bands (Zdrowotna art. 81 ust. 2e) are notches -/

def rycz (x : Int) : Household := { adults := [{ se := x, regime := .ryczalt }] }
/-- A ryczałt taxpayer on the standard ZUS whose revenue after social contributions crosses 60 000 zł (revenue
79 758 zł) pays 3 694 zł more health contribution for one more złoty, 3 472 zł net of the 50 % deduction. -/
theorem rycz60_notch : netOf (rycz 79757) - netOf (rycz 79758) = 3472 := by decide
theorem rycz60_health : (compute (rycz 79758)).employeeSocial - (compute (rycz 79757)).employeeSocial = 3694 := by decide
/-- Crossing 300 000 zł (revenue 319 758 zł): 7 386 zł more health contribution, 6 942 zł net. -/
theorem rycz300_notch : netOf (rycz 319757) - netOf (rycz 319758) = 6942 := by decide

/-! ## F5 A spouse's flat-rate business blocks joint filing for both (art. 6 ust. 8) -/

def couple (r : Regime) : Household := { adults := [{ wages := 300000 }, { se := 40000, regime := r }], married := true }
/-- A 300 000 zł earner married to a 40 000 zł sole trader: the trader's choice of liniowy instead of the scale costs
the couple 24 449 zł of net income (the splitting gain is lost on the 300 000 zł). -/
theorem flatSpouse_cost : netOf (couple .skala) - netOf (couple .liniowy) = 24449 := by decide

/-! ## F6 Joint filing with a non-earning spouse: the maximum gain, 27 600 zł, on a 300 000 zł salary -/

theorem joint_gain_300k :
    (compute { adults := [{ wages := 300000 }, { wages := 0 }], married := true, filing := "separate" }).incomeTax -
    (compute { adults := [{ wages := 300000 }, { wages := 0 }], married := true }).incomeTax = 27600 := by decide

/-! ## F7 B2B instead of employment at the same amount (200 000 zł) -/

theorem b2b_200k : netOf { adults := [{ se := 200000, regime := .ryczalt }] } - netOf { adults := [{ wages := 200000 }] }
    = 18022 := by decide

/-! ## F8 Under-26: advances withheld exceed the annual tax (art. 32 + PIT-2 in exempt months) -/

theorem young_overwithheld : withheld { age := 24, wages := 125000 } - annualAlone { age := 24, wages := 125000 } = 2641 := by
  decide
/-- With the exemption and the 30 000 zł kwota wolna stacked, a 24-year-old on 120 000 zł pays no income tax. -/
theorem young_120k_no_tax : (compute { adults := [{ age := 24, wages := 120000 }] }).incomeTax = 0 := by decide

/-! ## F9 The child-relief payout makes contributions free at low pay (art. 27f ust. 8–9) -/

/-- A single parent of three on 19 000 zł gets back exactly the contributions paid: income tax = −contributions. -/
theorem relief_refunds_contributions :
    (compute { adults := [{ wages := 19000 }], children := [3, 6, 9] }).incomeTax
      + (compute { adults := [{ wages := 19000 }], children := [3, 6, 9] }).employeeSocial = 0 := by decide

/-! ## F10 Ryczałt income is outside the one-child limit (art. 27f ust. 2a counts art. 27, 30b, 30c income only) -/

def mix (r : Regime) : Household := { adults := [{ se := 300000, regime := r }, { wages := 60000 }], married := true, children := [5] }
theorem ryczalt_keeps_relief : (compute (mix .ryczalt)).relief = 111204 ∧ (compute (mix .liniowy)).relief = 0 := by
  decide

/-! ## F11 Government figures re-derived -/

/-- art. 30c ust. 2b: 2025 liniowy health cap = 11 600 zł (M.P. 2023 poz. 1456) × 260 190 / 234 720 (ceilings of M.P.
2024 poz. 1051 and M.P. 2023 poz. 1342), rounded up to 100 zł = 12 900 zł, the figure in M.P. 2024 poz. 1084. -/
theorem liniowy_cap_formula : (11600 * 260190 + 234720 * 100 - 1) / (234720 * 100) * 100 = 12900 := by decide
/-- IKZE limits (IKE/IKZE act art. 13a ust. 1, 1a: 1,2 and 1,8 × prognozowane wynagrodzenie 8673 zł) = M.P. 2024
poz. 1055: 10 407,60 and 15 611,40 zł. -/
theorem ikze_limits : 12 * 867300 / 10 = ikzeLimit ∧ 18 * 867300 / 10 = ikzeLimitSelf := by decide
/-- Ceiling: 30 × 8673 zł = 260 190 zł (SUS art. 19 ust. 1; M.P. 2024 poz. 1051). -/
theorem ceiling_formula : 30 * 867300 = ceiling := by decide
/-- Health minimum 2025: 9 % of 75 % of 4666 zł, to the grosz = 314,96 zł; ryczałt bands from 8549,18 zł. -/
theorem health_minimum : pctGr (466600 * 75 / 100) 900 = healthMinMonthly := by decide
theorem ryczalt_bands : pctGr (rhu (854918 * 60) 100) 900 = ryczHealth1 ∧ pctGr 854918 900 = ryczHealth2 ∧
    pctGr (rhu (854918 * 180) 100) 900 = ryczHealth3 := by decide

end PlTax

namespace PlTax

/-! ## F16 Timing across the 30× ceiling (SUS art. 19 ust. 1): bunching two years of pay into one pays -/

/-- A single employee paid 260 114 zł in each of two years keeps 7 020 zł less than one paid 365 852 zł and then
154 377 zł (two-year totals 520 229 and 520 228 zł, the harness grid points): above the ceiling emerytalne and rentowe (11,26 %) stop, and the
health base rises less, more than offsetting the extra 32 % band. -/
theorem ceiling_bunching :
    netOf { adults := [{ wages := 365852 }] } + netOf { adults := [{ wages := 154377 }] }
      - 2 * netOf { adults := [{ wages := 260114 }] } = 7020 := by decide

end PlTax
