import MxTax.Household

/-!
# Theorems for all inputs (no `sorry`, no `native_decide`)

* The published tarifas (LISR arts. 96 and 152, RMF Anexo 8) against the kernel's band schedules with the same
  rates: within −3.87 / +0.34 centavos (annual) and −0.89 / +0.09 centavos (monthly) for every income
  (`tarifa152_vs_bands`, `tarifa96_vs_bands`); the band schedules are progressive, so monotone, convex and without
  jumps (kernel theorems); the published annual tarifa itself is *not* monotone (`tarifa152_drop`): one centavo
  more income at 1,503,902.46 lowers the tax by 1.52 centavos; it is monotone up to 4.21 centavos.
* The subsidio para el empleo cliff (`subsidy_cliff`), the deduction caps of art. 151 (`don_le_caps`, `ppr_le_cap`),
  the annual tax is never negative (`isr_nonneg`), RESICO's single-rate notches (`resico_notch_300k`) and its
  ceiling (`resico_le_250bp`), equal division between spouses never costs more on the band schedule
  (`split_ok`).
-/

namespace MxTax
open TaxKernel

/-- The kernel band schedule with the annual tarifa's rates (band `lo` = límite inferior − 0.01). -/
def sched152 : Schedule := Schedule.ofList (tarifa152.map fun r => (r.li - 1, r.rate))
/-- The same for the monthly tarifa of art. 96. -/
def sched96 : Schedule := Schedule.ofList (tarifa96.map fun r => (r.li - 1, r.rate))

theorem sched152_progressive : sched152.progressive = true := by decide
theorem sched96_progressive : sched96.progressive = true := by decide
theorem sched152_mono : Monotone' sched152.ticks := Schedule.ticks_mono_of_progressive _ sched152_progressive
theorem sched152_convex : Convex sched152.ticks := Schedule.ticks_convex _ sched152_progressive
theorem sched96_mono : Monotone' sched96.ticks := Schedule.ticks_mono_of_progressive _ sched96_progressive
theorem sched152_no_jump {x y : Int} (h : x ≤ y) : sched152.ticks y - sched152.ticks x ≤ 3500 * (y - x) := by
  have := (Schedule.ticks_lipschitz_of_progressive _ sched152_progressive h).2
  have e : sched152.maxRate = 3500 := by decide
  rwa [e] at this
/-- Mexico taxes individuals separately; on the band schedule, equal division of a couple's income never costs more
than any other division (kernel `splitting_le_separate`): the motive for shifting income to a spouse. -/
theorem split_ok (a b : Int) : splitting sched152.ticks a b ≤ separate sched152.ticks a b :=
  splitting_le_separate _ sched152_convex sched152_mono a b

set_option linter.deprecated false in
set_option maxHeartbeats 4000000 in
/-- **The annual tarifa is the band schedule to within −3.87 / +0.34 centavos**, for every income (ticks). -/
theorem tarifa152_vs_bands (x : Int) :
    -38696 ≤ tarifaTicks tarifa152 x - sched152.ticks x ∧ tarifaTicks tarifa152 x - sched152.ticks x ≤ 3376 := by
  have hc : x < 1 ∨ (1 ≤ x ∧ x < 895250) ∨ (895250 ≤ x ∧ x < 7598456) ∨ (7598456 ≤ x ∧ x < 13353608) ∨
      (13353608 ≤ x ∧ x < 15522981) ∨ (15522981 ≤ x ∧ x < 18585258) ∨ (18585258 ≤ x ∧ x < 37483789) ∨
      (37483789 ≤ x ∧ x < 59079600) ∨ (59079600 ≤ x ∧ x < 112792685) ∨ (112792685 ≤ x ∧ x < 150390247) ∨
      (150390247 ≤ x ∧ x < 451170738) ∨ 451170738 ≤ x := by omega
  simp only [tarifaTicks, tarifa152, sched152, Schedule.ticks, Schedule.ofList, List.map, bandsTicks, pos, BP]
  rcases hc with h|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|h
  all_goals
    simp (disch := omega) only [Int.min_eq_left, Int.min_eq_right, Int.max_eq_left, Int.max_eq_right,
      if_pos, if_neg]
    try omega

set_option linter.deprecated false in
set_option maxHeartbeats 4000000 in
/-- **The monthly tarifa is the band schedule to within −0.89 / +0.09 centavos**, for every income (ticks). -/
theorem tarifa96_vs_bands (x : Int) :
    -8904 ≤ tarifaTicks tarifa96 x - sched96.ticks x ∧ tarifaTicks tarifa96 x - sched96.ticks x ≤ 896 := by
  have hc : x < 1 ∨ (1 ≤ x ∧ x < 74605) ∨ (74605 ≤ x ∧ x < 633206) ∨ (633206 ≤ x ∧ x < 1112802) ∨
      (1112802 ≤ x ∧ x < 1293583) ∨ (1293583 ≤ x ∧ x < 1548772) ∨ (1548772 ≤ x ∧ x < 3123650) ∨
      (3123650 ≤ x ∧ x < 4923301) ∨ (4923301 ≤ x ∧ x < 9399391) ∨ (9399391 ≤ x ∧ x < 12532521) ∨
      (12532521 ≤ x ∧ x < 37597562) ∨ 37597562 ≤ x := by omega
  simp only [tarifaTicks, tarifa96, sched96, Schedule.ticks, Schedule.ofList, List.map, bandsTicks, pos, BP]
  rcases hc with h|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|⟨h1,h2⟩|h
  all_goals
    simp (disch := omega) only [Int.min_eq_left, Int.min_eq_right, Int.max_eq_left, Int.max_eq_right,
      if_pos, if_neg]
    try omega

/-- **The published annual tarifa is not monotone**: at 1,503,902.46 → 1,503,902.47 the tax falls by 1.52
centavos (the cuota fija 392,294.17 is below the tax of the row below at its upper limit, 392,294.1852). -/
theorem tarifa152_drop : tarifaTicks tarifa152 150390247 - tarifaTicks tarifa152 150390246 = -15200 := by decide

/-- …but it is monotone up to 4.21 centavos (from `tarifa152_vs_bands` and the band schedule's monotonicity). -/
theorem tarifa152_almost_mono {x y : Int} (h : x ≤ y) :
    tarifaTicks tarifa152 x ≤ tarifaTicks tarifa152 y + 42072 := by
  have := tarifa152_vs_bands x
  have := tarifa152_vs_bands y
  have := sched152_mono x y h
  omega

/-- The monthly tax net of the subsidy for a month's base `b` centavos (Feb–Dec). -/
def netMonthly (b : Int) : Int :=
  ticksToCentavos (tarifaTicks tarifa96 b) - (if b ≤ subsidyCap then subsidyMonth 2 else 0)

/-- **The subsidy cliff**: one centavo above 10,171.00 a month costs 474.65 pesos of ISR: SE-2025 art. Segundo,
"no excedan de $10,171.00". -/
theorem subsidy_cliff : netMonthly 1017101 - netMonthly 1017100 = 47465 := by decide
/-- At the cut-off the monthly ISR is 314.86 with the subsidy and 789.51 one centavo above. -/
theorem subsidy_cliff_levels : netMonthly 1017100 = 31486 ∧ netMonthly 1017101 = 78951 := by decide

/-- Art. 151 último párrafo: the donations deducted never exceed 5 annual UMA nor 15 % of total income. -/
theorem don_le_caps (p : PersonIn) (o t d : Int) (g : Bool) :
    (variant p o t d g).don ≤ dedCapUma * (mxYearAll p.wage.yr).umaAnnual ∧
    (variant p o t d g).don ≤ mulDivHU (pos t) dedCapPct BP := by
  simp only [variant]; constructor <;> omega
/-- Art. 151 fr. V: retirement contributions deducted never exceed 5 annual UMA (206,367.60 in 2025; 198,031.80 in 2024; 189,222.00 in 2023). -/
theorem ppr_le_cap (p : PersonIn) (o t d : Int) (g : Bool) : (variant p o t d g).ppr ≤ 20636760 := by
  have hy : (mxYearAll p.wage.yr).umaAnnual ≤ 4127352 := by
    unfold mxYearAll mxYear
    repeat (first | decide | split)
  simp only [variant, pprCapUma]; omega
/-- The annual ISR after the subsidy and the dividend credit is never negative (SE-2024 art. Tercero fr. III;
LISR art. 152: only tax actually paid is refunded). -/
theorem isr_nonneg (p : PersonIn) (o t d : Int) (g : Bool) : 0 ≤ (variant p o t d g).isr := by
  simp only [variant, pos]; omega

/-- **RESICO's single-rate notch** (art. 113-F): revenue of 300,000.01 pays 300.00 pesos more than 300,000.00
(the 1.10 % rate applies to the whole revenue), in ticks. -/
theorem resico_notch_300k : resicoTicks 30000001 - resicoTicks 30000000 = 300000110 := by decide
/-- The other RESICO notches: at 600,000 (+2,400.00), 1,000,000 (+5,000.00), 2,500,000 (+12,500.00). -/
theorem resico_notches :
    resicoTicks 60000001 - resicoTicks 60000000 = 2400000150 ∧
    resicoTicks 100000001 - resicoTicks 100000000 = 5000000200 ∧
    resicoTicks 250000001 - resicoTicks 250000000 = 12500000250 := by decide

/-- Monthly dead zone above the cut-off: pay after ISR at 10,171.00 (9,856.14) is reached again only at 10,703.59:
all pay between 10,171.01 and 10,703.58 a month leaves less after ISR than 10,171.00. -/
theorem subsidy_dead_zone_month :
    1070358 - netMonthly 1070358 < 1017100 - netMonthly 1017100 ∧
    1017100 - netMonthly 1017100 ≤ 1070359 - netMonthly 1070359 := by decide

/-- **The annual subsidy cliff** (SE-2025, wages paid in 12 equal months + aguinaldo in December + prima in July):
an annual wage of 128,380 keeps the subsidy in 11 months (all but December), 128,390 in none: 5,221.15 of
subsidy lost for 10 pesos more pay. -/
theorem subsidy_cliff_annual :
    (({ wages := 128380 } : WageIn).subsidyMonths = 11) ∧ (({ wages := 128390 } : WageIn).subsidyMonths = 0) ∧
    (({ wages := 128380 } : WageIn).subsidyTotal = 522145) ∧ (({ wages := 128390 } : WageIn).subsidyTotal = 0) := by
  decide

/-- **The aguinaldo costs December's subsidy**: from 112,750 a year the taxable aguinaldo lifts December's base
over 10,171 (11 months of subsidy instead of 12); with the same pay and a 30-day aguinaldo it happens at 100,000. -/
theorem december_subsidy_lost :
    (({ wages := 112740 } : WageIn).subsidyMonths = 12) ∧ (({ wages := 112750 } : WageIn).subsidyMonths = 11) ∧
    (({ wages := 100000, aguinaldoDays := 30 } : WageIn).subsidyMonths = 11) := by decide

/-- **LSS art. 36 notch**: a worker at the minimum wage (101,762 a year = 278.80 a day) pays no IMSS quota (the
employer pays it); one peso more a year and the worker pays every quota on the whole wage (2,416.87 a year). -/
theorem imss_minimum_wage_notch :
    (imssOf { wages := 101762 }).total = 0 ∧ (imssOf { wages := 101763 }).total = 241687 := by decide

/-- **RESICO's in-year exit notch** (art. 113-E tercer párrafo, RMF 2025 regla 3.13.5 fr. I): with revenue earned
evenly, 3,818,181.81 keeps all 12 months in RESICO, 3,818,181.82 only 11 (December's profit goes to art. 152). -/
theorem resico_month_notch : resicoMonths 381818181 = 12 ∧ resicoMonths 381818182 = 11 := by decide

/-! ## The tarifa as a kernel `Table` (TaxKernel 1.1): cuotas fijas against the band schedule -/

/-- The annual tarifa's rows as a kernel lookup table: each row `[límite inferior, next límite − 0.01]` with its
cuota fija (centavos) as the value. -/
def cuotas152 : TaxKernel.Table :=
  let rs := tarifa152
  (rs.zip ((rs.drop 1).map (fun r => r.li - 1) ++ [999999999999])).map fun (r, hi) => ⟨r.li, hi, r.cf⟩

/-- The rows tile the income line without gaps or overlaps, and the cuotas fijas rise. -/
theorem cuotas152_contiguous : cuotas152.contiguous = true ∧ cuotas152.valuesMono = true := by decide
/-- Every cuota fija is within 4 centavos of the band schedule's tax at its límite inferior… -/
theorem cuotas152_vs_bands :
    cuotas152.agreesWith (fun x => ticksToCentavos (sched152.ticks x)) (fun r => r.lo) 4 = true := by decide
/-- …but 7 of the 11 are not equal to it to the centavo (the table ≠ formula evidence of F4). -/
theorem cuotas152_disagree :
    (cuotas152.disagreements (fun x => ticksToCentavos (sched152.ticks x)) (fun r => r.lo) 0).length = 7 := by decide

end MxTax
