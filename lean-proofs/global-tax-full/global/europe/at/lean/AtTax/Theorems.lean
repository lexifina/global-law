import AtTax.Household

/-!
# Austria 2025: proofs (kernel theorems instantiated, statute claims, notches)

No `sorry`. Concrete notch statements are evaluated by the kernel (`decide`).
-/

namespace AtTax
open TaxKernel

/-! ## § 33 Abs. 1 tariff: the kernel's generic theorems -/

theorem tariff_progressive : tariff.progressive = true := by decide
theorem tariff_mono : Monotone' tariff.ticks := Schedule.ticks_mono_of_progressive _ tariff_progressive
theorem tariff_convex : Convex tariff.ticks := Schedule.ticks_convex _ tariff_progressive
theorem tariff_no_jump {x y : Int} (h : x ≤ y) : tariff.ticks y - tariff.ticks x ≤ tariff.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ tariff_progressive h).2
theorem tariff_maxRate : tariff.maxRate = 5500 := by decide
theorem tariff_le_top {x : Int} (h : 0 ≤ x) : tariff.ticks x ≤ 5500 * x := by
  have := Schedule.ticks_le_maxRate_mul _ tariff_progressive h
  rwa [tariff_maxRate] at this
theorem tariff_zero : tariff.ticks 0 = 0 := by decide
/-- The tax on 13 308 € is nil: the zero band (Grundfreibetrag built into the tariff). -/
theorem tariff_zero_band : tariff.ticks 1330800 = 0 := by decide
/-- Marginal rates are the bands' (`Schedule.ticks_succ`): 48 % at 70 000 €, 55 % above one million. -/
theorem tariff_rate_48 : tariff.rate 7000000 = 4800 := by decide
theorem tariff_rate_55 : tariff.rate 100000000 = 5500 := by decide
theorem tariff_marginal (x : Int) : tariff.ticks (x + 1) - tariff.ticks x = tariff.rate x := Schedule.ticks_succ _ x
/-- Austria assesses individuals. Were a couple assessed jointly on the tariff without splitting, it would never pay
less than two separate assessments (kernel `separate_le_joint`): individual assessment has no marriage penalty. -/
theorem individual_le_joint {a b : Int} (ha : 0 ≤ a) (hb : 0 ≤ b) :
    separate tariff.ticks a b ≤ joint tariff.ticks a b :=
  separate_le_joint _ tariff_convex tariff_zero ha hb
/-- …and splitting (not Austrian law) would never cost more than separate assessment. -/
theorem split_ok (a b : Int) : splitting tariff.ticks a b ≤ separate tariff.ticks a b :=
  splitting_le_separate _ tariff_convex tariff_mono a b

/-! ## § 67 Abs. 1: the 13th/14th salary -/

theorem sz_progressive : szSchedule.progressive = true := by decide
theorem sz_mono : Monotone' szSchedule.ticks := Schedule.ticks_mono_of_progressive _ sz_progressive
/-- 0 % on the first 620 €, then 6 % up to 25 000 € of Bemessungsgrundlage. -/
theorem sz_free : szSchedule.ticks 62000 = 0 := by decide
theorem sz_rate_6 : szSchedule.rate 1000000 = 600 := by decide
/-- The 13th and 14th salary of an average worker (2 × 4 503,86 €: the OECD AW of 63 053,95 € / 14, in cents) after SV: 411 € of tax,
an average rate of 4,6 % on them against 9 252 € (21 %) on the 12 monthly salaries (OECD S100, reproduced). -/
theorem sz_aw : szTax 900772 747010 = 41101 := by decide
/-- § 41 Abs. 4 read as the model does (Freigrenze on the gross Bezüge): no notch at the Freigrenze for an employee,
whose Bemessungsgrundlage after 17,07 % SV is below the 2 447 € where the 30 % glide starts. -/
theorem sz_no_notch_assessed : szTax 257001 213100 = 0 := by decide
/-- Withholding (§ 67 Abs. 1 without § 41 Abs. 4): one cent above the Freigrenze, 90,66 € of Lohnsteuer (refunded in
the Veranlagung). -/
theorem sz_notch_withheld : szTaxWh 257000 213100 = 0 ∧ szTaxWh 257001 213100 = 9066 := by decide

/-! ## Absetzbeträge: tapers (§ 33 Abs. 5 Z 3, Abs. 6) -/

theorem zuschlag_wf : zuschlag.WellFormed := by unfold Taper.WellFormed zuschlag; decide
theorem zuschlag_antitone {x y : Int} (h : x ≤ y) : zuschlag.amount y ≤ zuschlag.amount x :=
  Taper.amount_antitone _ zuschlag_wf h
theorem zuschlag_full : zuschlag.amount 1942400 = 79000 := by decide
theorem zuschlag_gone : zuschlag.amount zuschlagEnd = 0 := by decide
theorem zuschlag_bandEnd : zuschlag.bandEnd = zuschlagEnd := by decide
/-- Inside the band 10 319 € more Einkommen removes exactly the 790 € (kernel `Taper.amount_step`): a 7,66 % add-on to
the 20/30 % tariff rate. -/
theorem zuschlag_step {e : Int} (hs : 1942400 ≤ e) (hin : 0 < zuschlag.amount (e + 1031900)) :
    zuschlag.amount (e + 1031900) = zuschlag.amount e - 79000 :=
  Taper.amount_step zuschlag zuschlag_wf hs hin

theorem pab_wf : pab.WellFormed := by unfold Taper.WellFormed pab; decide
theorem pabHigh_wf : pabHigh.WellFormed := by unfold Taper.WellFormed pabHigh; decide
theorem pab_gone : pab.amount 3095700 = 0 := by decide
theorem pabHigh_gone : pabHigh.amount 3095700 = 0 := by decide
/-- The erhöhter Pensionistenabsetzbetrag falls by 1 476 € over 6 761 € of pension (21,8 %), on top of the 30 %
band: a 51,8 % marginal income-tax rate on pensions of 24 196-30 957 €, above the 50 % rate of the 103 072 € band. -/
theorem pabHigh_step {e : Int} (hs : 2419600 ≤ e) (hin : 0 < pabHigh.amount (e + 676100)) :
    pabHigh.amount (e + 676100) = pabHigh.amount e - 147600 :=
  Taper.amount_step pabHigh pabHigh_wf hs hin

/-! ## § 39 Abs. 5 Veranlagungsfreibetrag: a 200 % band -/

/-- Between 730 € and 1 460 € of other income, each euro removes one euro of the Freibetrag: taxable income rises by
two euros per euro earned. -/
theorem vfb_band (x : Int) (h1 : 73000 ≤ x) (h2 : x + 1 ≤ 146000) : vfbAmount (x + 1) = vfbAmount x - 1 := by
  simp only [vfbAmount, pos, vfb]
  omega
theorem vfb_full (x : Int) (h0 : 0 ≤ x) (h1 : x ≤ 73000) : vfbAmount x = x := by
  simp only [vfbAmount, pos, vfb]
  omega

/-! ## § 33 Abs. 2 Z 1: the Familienbonus Plus is not refundable -/

/-- "der Familienbonus Plus ist insoweit nicht abzuziehen, als er jene Steuer übersteigt, die auf das … Einkommen
entfällt". -/
theorem fbp_le_tariffTax (b : Base) (cl : Claims) (regel : Bool) (p : PersonIn) :
    (taxOf b cl regel p).fbpUsed ≤ pos (tariffTax b.einkommen (ypOf p.year)) := by
  simp only [taxOf]
  exact Int.min_le_right _ _

/-! ## § 33 Abs. 7 Kindermehrbetrag: literal text vs the BMF's reading -/

/-- Literal reading ("eine Einkommensteuer unter 700 Euro", then 700 € per further child): a family with two
children loses 700,01 € when the tariff tax reaches 700 €. -/
theorem kmb_literal_notch : kmbAmount 2 69999 false = 70001 ∧ kmbAmount 2 70000 false = 0 := by decide
/-- The BMF's reading (700 € per child, "Einkommensteuer unter 1.400 Euro" for two): no notch, 1 € of tax costs at
most 1 € of Kindermehrbetrag. -/
theorem kmb_bmf_lipschitz (n : Nat) (t : Int) : kmbAmount n t true - kmbAmount n (t + 1) true ≤ 1 := by
  unfold kmbAmount
  by_cases h : n = 0
  · simp [h]
  · simp only [h, ↓reduceIte, pos, kmbPerChild]
    omega

/-! ## § 33 Abs. 7 lit. b: the partner cliff (new, NOVEL N1) -/

/-- Two-earner couple, two children, the Familienbeihilfe recipient (second adult) with a tariff tax of 37 €: while
the partner's tariff tax is 1 399,99 € she receives 1 400 − 37 = 1 363 € of Kindermehrbetrag; one cent more of the
partner's tax and nobody receives anything. The household's refund falls by 1 363 € (BMF reading; 700 € steps under
the literal one). -/
theorem kmb_partner_cliff :
    kmbRecipient false 2 true false false 139999 3700 true true = some 1 ∧
    kmbAmount 2 3700 true = 136300 ∧
    kmbRecipient false 2 true false false 140000 3700 true true = none := by decide

/-! ## Social insurance notches (ASVG § 5 Abs. 2, AMPFG § 2a) -/

/-- One cent above the Geringfügigkeitsgrenze (551,10 € a month) the employee owes 83,33 € of contributions: the
month's net pay falls by 83,32 €. -/
theorem geringfuegig_notch : (svMonth 55110).total = 0 ∧ (svMonth 55111).total = 8333 := by decide
/-- AMPFG § 2a: at 2 074,01 € a month the employee's AV rises from 0 to 1 % of the whole base (20,74 €); the same
at 2 262 € (1 → 2 %) and 2 451 € (2 → 2,95 %). Net monthly pay falls when gross pay rises by a cent. -/
theorem av_notches :
    (svMonth 207400).av = 0 ∧ (svMonth 207401).av = 2074 ∧
    (svMonth 226200).av = 2262 ∧ (svMonth 226201).av = 4524 ∧
    (svMonth 245100).av = 4902 ∧ (svMonth 245101).av = 7230 := by decide
theorem av_net_falls : 207401 - (svMonth 207401).total < 207400 - (svMonth 207400).total := by decide
/-- Above the Höchstbeitragsgrundlage (6 450 € a month) contributions are constant. -/
theorem sv_capped (m : Int) (h : hbglMonth ≤ m) : svMonth m = svMonth hbglMonth := by
  have hg : ¬ (m ≤ geringfuegig) := by simp only [hbglMonth, hbglDay, geringfuegig] at *; omega
  have hb : min m hbglMonth = hbglMonth := Int.min_eq_right h
  have hg2 : ¬ (hbglMonth ≤ geringfuegig) := by decide
  simp only [svMonth, yp2025, hg, hg2, hb, if_false, Int.min_self]

/-! ## FLAG § 9a: the Mehrkindzuschlag is all-or-nothing at 55 000 € -/

/-- Three children: one euro of family Einkommen above 55 000 € costs 292,80 € of Mehrkindzuschlag. -/
theorem mkz_notch : familyBenefits [6, 11, 14] false 5500000 - familyBenefits [6, 11, 14] false 5500001 = 29280 := by
  decide

end AtTax
