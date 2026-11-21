import DKTax.Household

/-!
# Theorems (no `sorry`)

1. The parameters are the statute's formula: every 2025 amount is its 2010 grundbeløb regulated by PSL § 20, and the
   same formula reproduces Skatteministeriet's printed 2026 table (12 amounts) — table = formula.
2. Kernel parts instantiated: topskat and aktieindkomst schedules (monotone, convex, no jump, marginal rate = band
   rate), the børne- og ungeydelse and grøn check tapers (well formed, never rising with income, the exact
   2 pct. / 7,5 pct. withdrawal).
3. Danish claims: the skatteloft caps bundskat + topskat + kommuneskat at 52,07 % on personal income and at 42 % on
   positive nettokapitalindkomst for every municipal rate up to the cap (PSL § 19); in København it binds only
   on capital income (topskat on capital 6,49 %, on personal income the full 15 %); the beskæftigelsesfradrag never
   exceeds its cap and reaches it exactly from a base of 452.029 kr.; the transfer of a spouse's unused
   personfradrag never raises tax (§ 10, stk. 3); a larger aktieindkomst threshold (the spouse's transfer,
   § 8 a, stk. 4) never raises the aktieindkomstskat.
-/

namespace DKTax.Theorems
open DKTax TaxKernel

/-! ## 1. Table = formula -/

theorem params2025_regulated :
    p2025.topThreshold = 611800 ∧ p2025.kapGrund = 52400 ∧ p2025.pf = 51600 ∧ p2025.aktieLimit = 67500 ∧
    p2025.bfCap = 55600 ∧ p2025.enligCap = 48300 ∧ p2025.jobStart = 224500 ∧ p2025.jobCap = 2900 ∧
    p2025.pensCap = 83800 ∧ p2025.ratepenCap = 65500 ∧ p2025.giftCap = 19000 ∧ p2025.buyTaperStart = 917000 ∧
    p2025.gcStart = 475300 := by decide

/-- Skatteministeriet's 2026 tables (personskatteloven, ligningsloven, børne- og ungeydelsesloven pages, svmn.dk,
read 2026-11-19) print: mellemskat 641.200, topskat 777.900, toptopskat 2.592.700, kapital 55.000, personfradrag
54.100, aktieindkomst 79.400, beskæftigelsesfradrag 63.300, enlige forsørgere 50.600, job 235.200 / 3.100,
ekstra pension 87.800, BUY-aftrapning 961.100. PSL § 20 with reguleringstal 137,3 gives every one of them. -/
theorem skm2026_table_eq_formula :
    reg 1373 467000 = 641200 ∧ reg 1373 566500 = 777900 ∧ reg 1373 1888300 = 2592700 ∧
    reg 1373 40000 = 55000 ∧ reg 1373 39350 = 54100 ∧ reg 1373 57800 = 79400 ∧ reg 1373 46100 = 63300 ∧
    reg 1373 36800 = 50600 ∧ reg 1373 171300 = 235200 ∧ reg 1373 2200 = 3100 ∧ reg 1373 63900 = 87800 ∧
    reg 1373 700000 = 961100 := by decide

/-- The 2018-2024 table (Skatteministeriet, "Centrale beløbsgrænser i skattelovgivningen 2018-2024") for 2024:
topskat 588.900, kapital 50.500, personfradrag 49.700, aktieindkomst 61.000, beskæftigelsesfradrag 45.100,
enlige forsørgere 25.300, jobfradrag 216.100 / 2.800, ekstra pension 80.600, BUY-aftrapning 882.700. -/
theorem skm2024_table_eq_formula :
    p2024.topThreshold = 588900 ∧ p2024.kapGrund = 50500 ∧ p2024.pf = 49700 ∧ p2024.aktieLimit = 61000 ∧
    p2024.bfCap = 45100 ∧ p2024.enligCap = 25300 ∧ p2024.jobStart = 216100 ∧ p2024.jobCap = 2800 ∧
    p2024.pensCap = 80600 ∧ p2024.buyTaperStart = 882700 := by decide

/-! ## 2. Kernel parts -/

theorem top_progressive : (topSched p2025).progressive = true := by decide
theorem top_mono : Monotone' (topSched p2025).ticks := Schedule.ticks_mono_of_progressive _ top_progressive
theorem top_convex : Convex (topSched p2025).ticks := Schedule.ticks_convex _ top_progressive
theorem top_no_jump {x y : Int} (h : x ≤ y) :
    (topSched p2025).ticks y - (topSched p2025).ticks x ≤ (topSched p2025).maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ top_progressive h).2
/-- One more krone of personal income above 611.800 kr. costs exactly 15 % in topskat (before the skatteloft). -/
theorem top_marginal (x : Int) (h : 611800 ≤ x) : (topSched p2025).ticks (x + 1) - (topSched p2025).ticks x = 1500 := by
  rw [Schedule.ticks_succ]
  simp only [Schedule.rate, topSched, Schedule.flatAbove, bandsRate, p2025, reg, ceilDiv]
  split <;> omega

theorem aktie_progressive : (aktieSched p2025 p2025.aktieLimit).progressive = true := by decide
theorem aktie_mono : Monotone' (aktieSched p2025 p2025.aktieLimit).ticks :=
  Schedule.ticks_mono_of_progressive _ aktie_progressive
theorem aktie_convex : Convex (aktieSched p2025 p2025.aktieLimit).ticks :=
  Schedule.ticks_convex _ aktie_progressive

theorem buyTaper_wf (s : Int) (hs : 0 ≤ s) : (buyTaper p2025 s).WellFormed := by
  unfold Taper.WellFormed buyTaper; exact ⟨by show (0:Int) < 10000; decide, by show (0:Int) ≤ 200; decide, hs, rfl⟩
theorem buy_antitone (s : Int) (hs : 0 ≤ s) {x y : Int} (h : x ≤ y) :
    (buyTaper p2025 s).amount y ≤ (buyTaper p2025 s).amount x :=
  Taper.amount_antitone _ (buyTaper_wf s hs) h
theorem gcTaper_wf (s : Int) (hs : 0 ≤ s) : (gcTaper p2025 s).WellFormed := by
  unfold Taper.WellFormed gcTaper; exact ⟨by show (0:Int) < 10000; decide, by show (0:Int) ≤ 750; decide, hs, rfl⟩
theorem gc_antitone (s : Int) (hs : 0 ≤ s) {x y : Int} (h : x ≤ y) :
    (gcTaper p2025 s).amount y ≤ (gcTaper p2025 s).amount x :=
  Taper.amount_antitone _ (gcTaper_wf s hs) h

/-- § 1 a in the taper band: every 50 kr. of topskat base above 917.000 kr. removes exactly 1 kr. of a parent's
børne- og ungeydelse (2 %), as long as some is left. -/
theorem buy_step (s x : Int) (h1 : 917000 ≤ x) (h2 : (buyTaper p2025 s).amount (x + 50) > 0) :
    (buyTaper p2025 s).amount x - (buyTaper p2025 s).amount (x + 50) = 1 := by
  simp only [buyTaper, Taper.amount, Taper.reduction, divR, pos, p2025, reg, ceilDiv, BP] at *
  omega

/-! ## 3. Danish properties -/

/-- PSL § 19, stk. 1: for every municipal rate up to the ceiling minus bundskat, bundskat + topskat (after the
cut) + kommuneskat never exceed 52,07 % (all in 10⁻⁷). -/
theorem skatteloft_personal (o : Opts) (h0 : 0 ≤ o.munRate7) (h1 : o.munRate7 ≤ (5207 - 1201) * 1000) :
    p2025.bundRate * 1000 + topRate7 p2025 o p2025.skatteloft + o.munRate7 ≤ p2025.skatteloft * 1000 := by
  simp only [topRate7, p2025, pos]; omega

/-- PSL § 19, stk. 2: the same for positive nettokapitalindkomst, at 42 %. -/
theorem skatteloft_capital (o : Opts) (h0 : 0 ≤ o.munRate7) (h1 : o.munRate7 ≤ (4200 - 1201) * 1000) :
    p2025.bundRate * 1000 + topRate7 p2025 o p2025.kapLoft + o.munRate7 ≤ p2025.kapLoft * 1000 := by
  simp only [topRate7, p2025, pos]; omega

def cph : Opts := { munRate7 := 2350000, churchRate7 := 80000 }

/-- København 2025: the skatteloft does not bind on personal income (12,01 + 15 + 23,50 = 50,51 < 52,07) but cuts
topskat on positive nettokapitalindkomst from 15 % to 6,49 % (12,01 + 6,49 + 23,50 = 42). -/
theorem cph_rates : topRate7 p2025 cph p2025.skatteloft = 1500000 ∧ topRate7 p2025 cph p2025.kapLoft = 649000 := by
  decide

/-- The marginal tax on one more krone of pay for a København employee in the topskat band, not a church member:
8 % AM-bidrag + 92 % × (12,01 + 15 + 23,50) % = 54,4692 % (10⁻⁶). With the average municipality and the OECD's
0,008 pp skatteloft cut this is the OECD's 55,9044 % for S167 (MR_TW_PE). -/
theorem cph_top_marginal_wage : 80000 + 92 * (1201 + 1500 + 2350) = 544692 := by decide

/-- LL § 9 J: the beskæftigelsesfradrag never exceeds its maximum and reaches it from a base of 452.029 kr.
(12,3 % rounded to the nearest krone). -/
theorem bf_le_cap (b : Int) : pctCapped p2025.bfRate b p2025.bfCap ≤ 55600 := by
  simp only [pctCapped, p2025, reg, ceilDiv]; omega
theorem bf_nonneg (b : Int) : 0 ≤ pctCapped p2025.bfRate b p2025.bfCap := by
  simp only [pctCapped, divR, pos, p2025, reg, ceilDiv, BP]; omega
theorem bf_full (b : Int) (h : 452029 ≤ b) : pctCapped p2025.bfRate b p2025.bfCap = 55600 := by
  simp only [pctCapped, divR, pos, p2025, reg, ceilDiv, BP]; omega
theorem bf_not_full (b : Int) (h : b < 452029) : pctCapped p2025.bfRate b p2025.bfCap < 55600 := by
  simp only [pctCapped, divR, pos, p2025, reg, ceilDiv, BP]; omega

/-! ### Reductions never raise tax (the spouse transfers of §§ 10 stk. 3, 11 stk. 4, 13 stk. 2, 8 a stk. 6) -/

theorem take1_spec (t r : Int) (hr : 0 ≤ r) :
    (take1 t r).1 + (r - (take1 t r).2) = t ∧ 0 ≤ (take1 t r).2 ∧ (take1 t r).2 ≤ r := by
  simp only [take1, pos]; omega

theorem absorbStateFirst_spec (v : TaxVec) (r : Int) (hr : 0 ≤ r) :
    (absorbStateFirst v r).1.total + (r - (absorbStateFirst v r).2) = v.total ∧
    0 ≤ (absorbStateFirst v r).2 ∧ (absorbStateFirst v r).2 ≤ r := by
  simp only [absorbStateFirst, TaxVec.total, take1, pos]; omega

theorem absorbLocalFirst_spec (v : TaxVec) (r : Int) (hr : 0 ≤ r) :
    (absorbLocalFirst v r).1.total + (r - (absorbLocalFirst v r).2) = v.total ∧
    0 ≤ (absorbLocalFirst v r).2 ∧ (absorbLocalFirst v r).2 ≤ r := by
  simp only [absorbLocalFirst, TaxVec.total, take1, pos]; omega

theorem absorbState_spec (v : TaxVec) (r : Int) (hr : 0 ≤ r) :
    (absorbState v r).1.total + (r - (absorbState v r).2) = v.total ∧
    0 ≤ (absorbState v r).2 ∧ (absorbState v r).2 ≤ r := by
  simp only [absorbState, TaxVec.total, take1, pos]; omega

/-- PSL § 10, stk. 3: receiving the spouse's unused personfradrag never raises the receiving spouse's taxes, and
lowers them by at most the value transferred. -/
theorem pf_transfer_never_costs (r : PRes) (ls lk : Int) (hs : 0 ≤ ls) (hk : 0 ≤ lk) :
    (stepPfIn r ls lk).final.total ≤ r.final.total ∧
    r.final.total - (stepPfIn r ls lk).final.total ≤ ls + lk := by
  have a := absorbStateFirst_spec r.final ls hs
  have b := absorbLocalFirst_spec (absorbStateFirst r.final ls).1 lk hk
  simp only [stepPfIn]
  omega

/-- PSL § 8 a, stk. 4: a higher progressionsgrænse (e.g. raised by the spouse's unused amount) never raises the
aktieindkomstskat on a positive aktieindkomst. -/
theorem aktie_threshold_transfer (lim lim' x : Int) (h0 : 0 ≤ lim) (h : lim ≤ lim') (hx : 0 ≤ x) :
    (aktieSched p2025 lim').ticks x ≤ (aktieSched p2025 lim).ticks x := by
  simp only [aktieSched, Schedule.ticks, Schedule.ofList, List.map, bandsTicks, pos, p2025]
  omega

end DKTax.Theorems
