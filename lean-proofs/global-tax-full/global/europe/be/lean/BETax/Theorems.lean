import BETax.Basic

/-!
# Belgium: the kernel's generic theorems instantiated, and country-specific properties

No `sorry`. Concrete facts are checked by `decide` (kernel evaluation of the same definitions the exe runs).
-/

namespace BETax
open TaxKernel

/-! ## Art. 130 and art. 134 tariffs -/

theorem art130_progressive : art130.progressive = true := by decide
theorem art134_progressive : art134.progressive = true := by decide
theorem art130_mono : Monotone' art130.ticks := Schedule.ticks_mono_of_progressive _ art130_progressive
theorem art130_convex : Convex art130.ticks := Schedule.ticks_convex _ art130_progressive
theorem art134_convex : Convex art134.ticks := Schedule.ticks_convex _ art134_progressive
theorem art130_no_jump {x y : Int} (h : x ≤ y) : art130.ticks y - art130.ticks x ≤ art130.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ art130_progressive h).2
theorem art130_le_top {x : Int} (h : 0 ≤ x) : art130.ticks x ≤ 5000 * x := by
  have := Schedule.ticks_le_maxRate_mul _ art130_progressive h
  have e : art130.maxRate = 5000 := by decide
  rwa [e] at this
theorem art130_marginal (x : Int) : art130.ticks (x + 1) - art130.ticks x = art130.rate x := Schedule.ticks_succ _ x
/-- Splitting would never cost more than separate assessment under art. 130 (Belgium does not split; the quotient
conjugal is a capped partial transfer, see `quotient_sum`). -/
theorem art130_split_ok (a b : Int) : splitting art130.ticks a b ≤ separate art130.ticks a b :=
  splitting_le_separate _ art130_convex art130_mono a b

/-- The two tariffs: on the slice 11.460-16.320 EUR the art. 130 tariff charges 25 % while the exempt sum is valued
at 30 % (art. 134 § 2 keeps the pre-2017 tariff). For every income `x` in that slice the exempt-sum tariff exceeds
the income tariff by exactly 5 % of `x − 11.460`. The kernel's `lowBandReduction` (one schedule for both) does not
fit Belgium: kernel gap. -/
theorem exempt_tariff_gap {x : Int} (h1 : 1146000 ≤ x) (h2 : x ≤ 1632000) :
    art134.ticks x - art130.ticks x = 500 * (x - 1146000) := by
  simp only [art134, art130, Schedule.ofList, Schedule.ticks, List.map, bandsTicks, pos]
  omega

/-! ## The official worked example (SPF Finances, "Taux d'imposition", année de revenus 2025): Jean, single, taxable
38.000 EUR: 4.080 + 4.992 + 4.140 = 13.212; exempt 10.910 × 25 % = 2.727,50; tax 10.484,50. -/

theorem jean_basic : schedTax art130 3800000 = 1321200 := by decide
theorem jean_exempt : schedTax art134 exemptBase = 272750 := by decide
theorem jean_tax : taxAfterExempt 3800000 { nonchild := exemptBase, child := 0 } = 1048450 := by decide

/-! ## Quotient conjugal (art. 87-88) -/

theorem quotient_sum (a b : Int) :
    (attributeIncome a b quotientPct quotientCap).1 + (attributeIncome a b quotientPct quotientCap).2 = a + b :=
  attributeIncome_sum a b quotientPct quotientCap
theorem quotient_le_cap (a b : Int) : attributedAmount a b quotientPct quotientCap ≤ 1346000 := by
  have := (attributedAmount_bounds a b quotientPct quotientCap).2
  simp only [quotientCap, pos] at this ⊢; omega

/-! ## Regional and municipal -/

/-- Brussels ordinance 15.12.2014 art. 2: centimes = [100/(100 − f)] × [99,5 − (100 − f)], "arrondi au millième
supérieur", f = 24,957 (AR 19.12.2017): in thousandths of a percent this is 32.591. -/
theorem bxl_centimes_formula :
    ceilDiv (100000 * (99500 - (100000 - autonomyPcm))) (100000 - autonomyPcm) = brusselsCentimesPcm := by decide

/-- The design target: federal (reduced) plus Brussels regional tax is 99,5 % of the impôt Etat, to within the
rounding of the centimes: (1 − 24,957 %) × (1 + 32,591 %) ∈ [99,500 %, 99,501 %). -/
theorem bxl_total_share :
    (99500 : Int) * 100000 ≤ (100000 - autonomyPcm) * (100000 + brusselsCentimesPcm) ∧
    (100000 - autonomyPcm) * (100000 + brusselsCentimesPcm) < (99501 : Int) * 100000 := by decide

/-! ## Single parent's additional supplement (art. 133 al. 2-3) -/

/-- Full up to 19.250, nothing from 24.390, linear in between (no notch at either end). -/
theorem spExtra_ends : spExtra 1925000 500000 = 129000 ∧ spExtra 2438999 500000 = 0 ∧ spExtra 2439000 500000 = 0 :=
  by decide
/-- Inside the band every 5.140 EUR of taxable income withdraws 1.290 EUR of exempt sum (25,1 %); valued at the
art. 134 marginal rate (30-40 %) this adds 7,5-10 points to the marginal rate. -/
theorem spExtra_slope : spExtra 2000000 500000 - spExtra 2514000 500000 = 110177 := by decide

/-! ## CSSS (loi 30.03.1994 art. 108) -/

/-- Continuity of the individual scale at every threshold (no notch; within one cent). -/
theorem csss_individual_continuous :
    csssIndividual 2107096 = 12395 ∧ csssIndividual 2107097 = 12395 ∧
    csssIndividual 3734400 = 33550 ∧ csssIndividual 3734401 = 33550 ∧
    csssIndividual 4099726 = 48196 ∧ csssIndividual 4099727 = 48196 ∧
    csssIndividual 6018195 = 73128 ∧ csssIndividual 6018196 = 73128 := by decide
theorem csss_joint_continuous :
    csssJoint 6018195 = 63239 ∧ csssJoint 6018196 = 63239 ∧ csssJoint 8194400 = 73128 := by decide
/-- The household scale: two individually taxed earners with 48.269,16 EUR each pay 2 × 576,47 = 1.152,94; married,
the same household pays 731,28 (joint scale, art. 108 § 1 al. 3): a marriage bonus of 421,66 EUR in the CSSS
alone. -/
theorem csss_marriage_bonus :
    2 * csssIndividual 4826916 - csssJoint (2 * 4826916) = 42166 := by decide

/-! ## Famiris notches -/

/-- At the first ceiling (39.792,84 EUR of household taxable income, February-December 2025 barème) the social
supplement of a two-child couple falls from 2 × 87,04 to 2 × 31,09 a month: 111,90 EUR a month for one euro. -/
theorem famiris_notch_plafond1 :
    famNewMonth famFeb 3979283 [3, 5] false - famNewMonth famFeb 3979284 [3, 5] false = 11190 := by decide
/-- At the second ceiling (57.763,80 EUR) the remaining 2 × 31,09 disappear. -/
theorem famiris_notch_plafond2 :
    famNewMonth famFeb 5776379 [3, 5] false - famNewMonth famFeb 5776380 [3, 5] false = 6218 := by decide

end BETax

/-! ## Owner-manager: the small-company rate condition (CIR 92 art. 215) -/

namespace BETax
open TaxKernel

/-- Art. 215 al. 1-2: "Le taux de l'impôt des sociétés est fixé à 25 %"; small companies: "le taux ... sur la première
tranche de 0 à 100.000 euros est toutefois fixé à 20 %"; al. 3, 4° (version in force for AI 2026): not for companies
that do not pay at least one director "une rémunération ... au moins égale à 25.000 euros" indexed with the art. 178
§ 3 coefficient (IDX 2,0096: 50.240, "arrondi au multiple de 1.000 euros": 50.000), unless the pay is at least the
taxable result. Cents; `profit` = taxable result after the director's pay. -/
def citSme (profit pay : Int) : Int :=
  if pay ≥ 5000000 ∨ pay ≥ profit then pctBp 2000 (min profit 10000000) + pctBp 2500 (pos (profit - 10000000))
  else pctBp 2500 profit

/-- The notch: with 150.000 EUR of profit before the director's pay, paying 50.000 instead of 49.999 EUR lowers the
company's tax by 5.000,25 EUR (one euro more salary, 5.000 EUR less corporate tax). -/
theorem cit_pay_notch :
    citSme (15000000 - 4999900) 4999900 - citSme (15000000 - 5000000) 5000000 = 500025 := by decide

end BETax
