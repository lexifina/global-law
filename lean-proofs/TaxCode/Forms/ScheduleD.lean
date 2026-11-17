import TaxCode.Individual.C.CapitalGains

/-!
# Schedule D Tax Worksheet and the Qualified Dividends and Capital Gain Tax Worksheet (2025) against §1(h)

Form text: 2025 Instructions for Schedule D (Form 1040), "Schedule D Tax Worksheet" lines 1–47 (pp. 15–16);
2025 Instructions for Form 1040, "Qualified Dividends and Capital Gain Tax Worksheet—Line 16" (modelled line by line
in `C.qdcg`, whose amounts $48,350/$96,700/$64,750 and $533,400/$300,000/$600,050/$566,700 are the ones printed on
lines 6 and 13; the Schedule D Tax Worksheet prints the same amounts on lines 15 and 26 and $197,300/$394,600/$197,300
on line 19).

Statute: §1(h)(1)(A)–(F), (3) adjusted net capital gain, (4) 28-percent rate gain, (6) unrecaptured §1250 gain,
(11) qualified dividends; §1(j)(5)(A) substitutes "below the maximum zero rate amount" in (B)(i) and "below the
maximum 15-percent rate amount" in (C)(ii)(I) — but NOT in (A)(ii)(I), which still reads "taxed at a rate below 25
percent", i.e. up to the top of the 24% bracket ($197,300 single/separate/head of household, $394,600 joint: Rev.
Proc. 2024-40 Tables 1–4). The existing model (`C.split`) has no 25%/28% gain; this file adds it.

Domain: no Form 4952 election (worksheet lines 3–5 zero, so lines 5 and 8 are 0); amounts ≥ 0. "Figure the tax"
(lines 44, 46) is taken at the exact §1(j) schedule in cents; the Tax Table's own effect (+$6.00/−$4.78 per lookup
under $100,000) is proved in `TaxTable.lean`.

Negative intermediate amounts. §1(h)(1) subtracts without a floor in (A)(i), (A)(ii)(II), (B)(ii) and (C)(ii)
("reduced by", "the excess of" without "(if any)"); the worksheet floors every such line at zero ("If zero or less,
enter -0-"). `statute` below takes the floors (the conventional reading); `literal` keeps the raw differences, and
`literal_differs` shows the two readings diverge whenever the gain exceeds taxable income (see FINDINGS).
-/

namespace TaxCode.Forms.ScheduleD
open TaxCode.Individual TaxCode.Individual.C

structure Inputs where
  filing : Filing
  ti : Int        -- Form 1040 line 15
  qd : Int        -- qualified dividends (Form 1040 line 3a)
  ncg0 : Int      -- net capital gain without qualified dividends: smaller of Schedule D lines 15 and 16
  r28 : Int       -- 28-percent rate gain (Schedule D line 18)
  u1250 : Int     -- unrecaptured section 1250 gain (Schedule D line 19)
  deriving Repr

/-- §1(j)(2) top of the 24% bracket: "taxed at a rate below 25 percent" (worksheet line 19). -/
def top24 : Filing → Int
  | .mfj | .qss => 394600
  | _ => 197300

/-! ## The worksheet, line by line -/

section Worksheet
variable (i : Inputs)

def w1 : Int := i.ti
def w2 : Int := i.qd
/-- Lines 3–5 (Form 4952 lines 4g, 4e): no election, line 5 = 0. Line 6: "Subtract line 5 from line 2. If zero or
less, enter -0-". -/
def w6 : Int := max 0 (w2 i - 0)
/-- Line 7: "Enter the smaller of line 15 or line 16 of Schedule D". -/
def w7 : Int := i.ncg0
/-- Lines 8–9: "Subtract line 8 from line 7. If zero or less, enter -0-" (line 8 = 0). -/
def w9 : Int := max 0 (w7 i - 0)
/-- Line 10: "Add lines 6 and 9". -/
def w10 : Int := w6 i + w9 i
/-- Line 11: "Add lines 18 and 19 of Schedule D". -/
def w11 : Int := i.r28 + i.u1250
/-- Line 12: "Enter the smaller of line 9 or line 11". -/
def w12 : Int := min (w9 i) (w11 i)
/-- Line 13: "Subtract line 12 from line 10". -/
def w13 : Int := w10 i - w12 i
/-- Line 14: "Subtract line 13 from line 1. If zero or less, enter -0-". -/
def w14 : Int := max 0 (w1 i - w13 i)
/-- Line 15: $48,350 / $96,700 / $64,750. -/
def w15 : Int := maxZeroRate i.filing
/-- Line 16: "Enter the smaller of line 1 or line 15". -/
def w16 : Int := min (w1 i) (w15 i)
/-- Line 17: "Enter the smaller of line 14 or line 16". -/
def w17 : Int := min (w14 i) (w16 i)
/-- Line 18: "Subtract line 10 from line 1. If zero or less, enter -0-". -/
def w18 : Int := max 0 (w1 i - w10 i)
/-- Line 19: "Enter the smaller of line 1 or: $197,300 ...; $394,600 ...; $197,300 if head of household". -/
def w19 : Int := min (w1 i) (top24 i.filing)
/-- Line 20: "Enter the smaller of line 14 or line 19". -/
def w20 : Int := min (w14 i) (w19 i)
/-- Line 21: "Enter the larger of line 18 or line 20". -/
def w21 : Int := max (w18 i) (w20 i)
/-- Line 22: "Subtract line 17 from line 16. This amount is taxed at 0%". -/
def w22 : Int := w16 i - w17 i
/-- Line 23: "Enter the smaller of line 1 or line 13". -/
def w23 : Int := min (w1 i) (w13 i)
/-- Line 24: "Enter the amount from line 22". -/
def w24 : Int := w22 i
/-- Line 25: "Subtract line 24 from line 23. If zero or less, enter -0-". -/
def w25 : Int := max 0 (w23 i - w24 i)
/-- Line 26: $533,400 / $300,000 / $600,050 / $566,700. -/
def w26 : Int := max15Rate i.filing
/-- Line 27: "Enter the smaller of line 1 or line 26". -/
def w27 : Int := min (w1 i) (w26 i)
/-- Line 28: "Add lines 21 and 22". -/
def w28 : Int := w21 i + w22 i
/-- Line 29: "Subtract line 28 from line 27. If zero or less, enter -0-". -/
def w29 : Int := max 0 (w27 i - w28 i)
/-- Line 30: "Enter the smaller of line 25 or line 29". -/
def w30 : Int := min (w25 i) (w29 i)
/-- Line 32: "Add lines 24 and 30". -/
def w32 : Int := w24 i + w30 i
/-- Line 33: "Subtract line 32 from line 23" (skipped, i.e. zero, "If lines 1 and 32 are the same"). -/
def w33 : Int := if w1 i = w32 i then 0 else w23 i - w32 i
/-- Line 35: "Enter the smaller of line 9 above or Schedule D, line 19" (lines 35–40 skipped if line 19 is zero). -/
def w35 : Int := min (w9 i) i.u1250
/-- Line 36: "Add lines 10 and 21". -/
def w36 : Int := w10 i + w21 i
/-- Line 38: "Subtract line 37 [= line 1] from line 36. If zero or less, enter -0-". -/
def w38 : Int := max 0 (w36 i - w1 i)
/-- Line 39: "Subtract line 38 from line 35. If zero or less, enter -0-". -/
def w39 : Int := if i.u1250 = 0 ∨ w1 i = w32 i then 0 else max 0 (w35 i - w38 i)
/-- Lines 41–42: "Add lines 21, 22, 30, 33, and 39"; "Subtract line 41 from line 1" (skipped if Schedule D line 18
is zero). -/
def w42 : Int := if i.r28 = 0 ∨ w1 i = w32 i then 0 else w1 i - (w21 i + w22 i + w30 i + w33 i + w39 i)
/-- Line 45 in cents: lines 31 (15%), 34 (20%), 40 (25%), 43 (28%) and 44 (tax on line 21). -/
def w45 : Int := 15 * w30 i + 20 * w33 i + 25 * w39 i + 28 * w42 i + scheduleCents i.filing (w21 i)
/-- Line 46: the tax on line 1. Line 47: "Enter the smaller of line 45 or line 46". -/
def w47 : Int := min (w45 i) (scheduleCents i.filing (w1 i))

end Worksheet

/-! ## The statute -/

section Statute
variable (i : Inputs)

/-- §1(h)(11): net capital gain includes qualified dividend income. -/
def ncg : Int := i.ncg0 + i.qd
/-- §1(h)(3): adjusted net capital gain = NCG (without (11)) reduced, not below zero, by unrecaptured §1250 gain and
28-percent rate gain, plus qualified dividends. -/
def ancg : Int := max 0 (i.ncg0 - (i.u1250 + i.r28)) + i.qd
/-- The gain "(or, if less, taxable income)". -/
def gainCap : Int := min (ancg i) i.ti
/-- (A): "the greater of (i) taxable income reduced by the net capital gain; or (ii) the lesser of (I) the amount of
taxable income taxed at a rate below 25 percent; or (II) taxable income reduced by the adjusted net capital gain"
(differences floored at zero). -/
def amtA : Int := max (max 0 (i.ti - ncg i)) (min (min i.ti (top24 i.filing)) (max 0 (i.ti - ancg i)))
/-- (B): 0% on "so much of the [gain] as does not exceed the excess (if any) of (i) [taxable income below the maximum
zero rate amount] over (ii) the taxable income reduced by the adjusted net capital gain". -/
def amtB : Int := min (gainCap i) (max 0 (min i.ti (maxZeroRate i.filing) - max 0 (i.ti - ancg i)))
/-- (C): 15% of "the lesser of (i) so much of the [gain] as exceeds [(B)'s amount], or (ii) the excess of (I) [taxable
income below the maximum 15-percent rate amount] over (II) the sum of the amounts [under (A) and (B)]". -/
def amtC : Int := min (gainCap i - amtB i) (max 0 (min i.ti (max15Rate i.filing) - (amtA i + amtB i)))
/-- (D): 20% of "the [gain] in excess of the sum of the amounts [under (B) and (C)]". -/
def amtD : Int := gainCap i - amtB i - amtC i
/-- (E): 25% of "the excess (if any) of (i) the unrecaptured section 1250 gain (or, if less, the net capital gain
(determined without regard to paragraph (11))), over (ii) the excess (if any) of (I) [(A)'s amount] plus the net
capital gain, over (II) taxable income". -/
def amtE : Int := max 0 (min i.u1250 i.ncg0 - max 0 (amtA i + ncg i - i.ti))
/-- (F): 28% of "the amount of taxable income in excess of the sum of the amounts [under (A)–(E)]". -/
def amtF : Int := max 0 (i.ti - (amtA i + amtB i + amtC i + amtD i + amtE i))
/-- The §1(h)(1) sum, cents. -/
def capSum : Int :=
  scheduleCents i.filing (amtA i) + 15 * amtC i + 20 * amtD i + 25 * amtE i + 28 * amtF i
/-- §1(h)(1): "the tax imposed by this section ... shall not exceed the sum". -/
def statuteTax : Int := if 0 < ncg i then min (scheduleCents i.filing i.ti) (capSum i) else scheduleCents i.filing i.ti

end Statute

/-! ## Worksheet = statute -/

theorem rates_ok (f : Filing) : 0 < maxZeroRate f ∧ maxZeroRate f ≤ top24 f ∧ top24 f ≤ max15Rate f := by
  cases f <;> decide

section Proofs
variable (i : Inputs) (ht : 0 ≤ i.ti) (hq : 0 ≤ i.qd) (hn : 0 ≤ i.ncg0) (hr : 0 ≤ i.r28) (hu : 0 ≤ i.u1250)

include ht hn hq in
/-- Line 13 is the adjusted net capital gain. -/
theorem L13 : w13 i = ancg i := by
  unfold w13 w12 w11 w10 w9 w7 w6 w2 ancg; omega

include ht hn hq in
theorem L10 : w10 i = ncg i := by unfold w10 w9 w7 w6 w2 ncg; omega

include ht hn hq in
/-- Line 21 is the amount of §1(h)(1)(A). -/
theorem L21 : w21 i = amtA i := by
  unfold w21 w20 w19 w18 w14 w1; rw [L13 i ht hq hn, L10 i ht hq hn]; unfold amtA; omega

include ht hn hq in
/-- Line 22 is the amount of (B). -/
theorem L22 : w22 i = amtB i := by
  have : 0 ≤ ancg i := by unfold ancg; omega
  unfold w22 w17 w16 w15 w14 w1; rw [L13 i ht hq hn]; unfold amtB gainCap; omega

include ht hn hq in
/-- Line 30 is the amount of (C). -/
theorem L30 : w30 i = amtC i := by
  have : 0 ≤ ancg i := by unfold ancg; omega
  have := rates_ok i.filing
  have hA : 0 ≤ amtA i := by unfold amtA; omega
  have hB : amtB i ≤ min (ancg i) i.ti ∧ 0 ≤ amtB i ∧ amtB i ≤ min i.ti (maxZeroRate i.filing) := by
    unfold amtB gainCap; omega
  unfold w30 w29 w28 w27 w26 w25 w24 w23 w1; rw [L13 i ht hq hn, L21 i ht hq hn, L22 i ht hq hn]
  unfold amtC gainCap; omega

include ht hn hq in
theorem L32 : w32 i = amtB i + amtC i := by unfold w32 w24; rw [L22 i ht hq hn, L30 i ht hq hn]

include ht hn hq in
/-- Line 33 is the amount of (D) (when not skipped). -/
theorem L33 (h : w1 i ≠ w32 i) : w33 i = amtD i := by
  unfold w33; rw [if_neg h]; unfold w23 w1; rw [L13 i ht hq hn, L32 i ht hq hn]; unfold amtD gainCap; omega

include ht hn hq in
/-- Line 39 is the amount of (E) (when not skipped). -/
theorem L39 (hu0 : i.u1250 ≠ 0) (h : w1 i ≠ w32 i) : w39 i = amtE i := by
  unfold w39; rw [if_neg (by omega)]; unfold w35 w38 w36 w9 w7 w1
  rw [L10 i ht hq hn, L21 i ht hq hn]; unfold amtE; omega

include ht hq hn hr hu in
/-- Bookkeeping facts about the statute's amounts. -/
theorem facts :
    0 ≤ amtA i ∧ i.ti - ncg i ≤ amtA i ∧ 0 ≤ amtB i ∧ 0 ≤ amtC i ∧ amtB i + amtC i ≤ gainCap i ∧ 0 ≤ gainCap i ∧
    gainCap i = min (ancg i) i.ti ∧ amtA i + gainCap i ≤ i.ti ∧
    ncg i - ancg i = min i.ncg0 (i.u1250 + i.r28) ∧ 0 ≤ ancg i ∧
    amtD i = gainCap i - amtB i - amtC i ∧
    amtE i = max 0 (min i.u1250 i.ncg0 - max 0 (amtA i + ncg i - i.ti)) ∧
    amtF i = max 0 (i.ti - (amtA i + amtB i + amtC i + amtD i + amtE i)) := by
  have := rates_ok i.filing
  have hg : gainCap i = min (ancg i) i.ti := rfl
  have hAn : ncg i - ancg i = min i.ncg0 (i.u1250 + i.r28) := by unfold ncg ancg; omega
  have ha0 : 0 ≤ ancg i := by unfold ancg; omega
  have hA : 0 ≤ amtA i ∧ amtA i + gainCap i ≤ i.ti ∧ i.ti - ncg i ≤ amtA i := by
    unfold amtA; rw [hg]; generalize ancg i = X at *; generalize ncg i = N at *; omega
  have hBC : 0 ≤ amtB i ∧ 0 ≤ amtC i ∧ amtB i + amtC i ≤ gainCap i := by
    unfold amtC amtB; rw [hg]; generalize amtA i = A at *; generalize ancg i = X at *; omega
  exact ⟨hA.1, hA.2.2, hBC.1, hBC.2.1, hBC.2.2, by rw [hg]; omega, hg, hA.2.1, hAn, ha0, rfl, rfl, rfl⟩

include ht hq hn hr hu in
/-- The "skip" instructions lose nothing: when line 1 = line 32, the statute's (D), (E), (F) amounts are zero. -/
theorem skip_ok (h : w1 i = w32 i) : amtD i = 0 ∧ amtE i = 0 ∧ amtF i = 0 := by
  have F := facts i ht hq hn hr hu
  rw [L32 i ht hq hn] at h; unfold w1 at h
  obtain ⟨h1, h1', h2, h3, h4, h5, h6, h7, h8, h9, hD, hE, hF⟩ := F
  rw [hF, hE, hD]
  generalize amtA i = A at *; generalize amtB i = B at *; generalize amtC i = C at *
  generalize gainCap i = G at *; generalize ancg i = X at *; generalize ncg i = N at *
  refine ⟨?_, ?_, ?_⟩ <;> omega

include ht hq hn hr hu in
/-- Line 42 (28% gain) is the statute's (F) amount, including when the worksheet skips it. -/
theorem L42 : w42 i = amtF i := by
  have F := facts i ht hq hn hr hu
  obtain ⟨h1, h1', h2, h3, h4, h5, h6, h7, h8, h9, hD, hE, hF⟩ := F
  unfold w42
  by_cases hs : i.r28 = 0 ∨ w1 i = w32 i
  · rw [if_pos hs]
    rcases hs with hs | hs
    · rw [hF, hD, hE]; rw [hs] at h8
      generalize amtA i = A at *; generalize amtB i = B at *; generalize amtC i = C at *
      generalize gainCap i = G at *; generalize ancg i = X at *; generalize ncg i = N at *
      omega
    · exact (skip_ok i ht hq hn hr hu hs).2.2.symm
  · rw [if_neg hs]
    have hs' : w1 i ≠ w32 i := fun h => hs (Or.inr h)
    have e39 : w39 i = amtE i := by
      by_cases hu0 : i.u1250 = 0
      · unfold w39; rw [if_pos (Or.inl hu0), hE, hu0]; omega
      · exact L39 i ht hq hn hu0 hs'
    rw [L21 i ht hq hn, L22 i ht hq hn, L30 i ht hq hn, L33 i ht hq hn hs', e39, hF, hD, hE]; unfold w1
    generalize amtA i = A at *; generalize amtB i = B at *; generalize amtC i = C at *
    generalize gainCap i = G at *; generalize ancg i = X at *; generalize ncg i = N at *
    omega

include ht hq hn hr hu in
/-- **Line 45 is the §1(h)(1) sum and line 47 the §1(h) tax, for all inputs ≥ 0** (exact schedule in place of the
Tax Table): the worksheet computes (A) on line 21, (B) on 22, (C) on 30, (D) on 33, (E) on 39 and (F) on 42. -/
theorem w47_eq_statute (hg : 0 < ncg i) : w47 i = statuteTax i := by
  unfold w47 statuteTax capSum w45
  rw [if_pos hg, L21 i ht hq hn, L30 i ht hq hn, L42 i ht hq hn hr hu]
  by_cases h132 : w1 i = w32 i
  · have ⟨d0, e0, f0⟩ := skip_ok i ht hq hn hr hu h132
    have a : w33 i = 0 := by unfold w33; rw [if_pos h132]
    have b : w39 i = 0 := by unfold w39; rw [if_pos (Or.inr h132)]
    rw [a, b, d0, e0]; unfold w1; omega
  · have e39 : w39 i = amtE i := by
      by_cases hu0 : i.u1250 = 0
      · unfold w39; rw [if_pos (Or.inl hu0)]; unfold amtE; rw [hu0]; omega
      · exact L39 i ht hq hn hu0 h132
    rw [L33 i ht hq hn h132, e39]; unfold w1; omega

end Proofs

/-- **§1(h)(1) "shall not exceed"**: line 47 is never more than the ordinary tax on taxable income (line 46). -/
theorem w47_le (j : Inputs) : w47 j ≤ scheduleCents j.filing j.ti := by unfold w47 w1; omega

/-- With no 25%/28% gain the Schedule D Tax Worksheet's amounts are the Qualified Dividends and Capital Gain Tax
Worksheet's (`C.qdcg`, lines 5, 9, 17): the two worksheets agree. -/
theorem schD_eq_qdcg (i : Inputs) (ht : 0 ≤ i.ti) (hq : 0 ≤ i.qd) (hn : 0 ≤ i.ncg0) (hr : i.r28 = 0)
    (hu : i.u1250 = 0) :
    w21 i = (qdcg i.filing i.ti (i.qd + i.ncg0)).l5 ∧ w22 i = (qdcg i.filing i.ti (i.qd + i.ncg0)).l9 ∧
    w30 i = (qdcg i.filing i.ti (i.qd + i.ncg0)).l17 := by
  have := rates_ok i.filing
  rw [L21 i ht hq hn, L22 i ht hq hn, L30 i ht hq hn]
  simp only [qdcg]
  unfold amtC amtB amtA gainCap ancg ncg; rw [hr, hu]
  omega

/-! ## The literal reading with negative amounts -/

/-- §1(h)(1)(B) read literally, with "(ii) the taxable income reduced by the adjusted net capital gain" allowed to
be negative (no "(if any)" or "but not below zero" on it): the 0% amount. -/
def literalB (i : Inputs) : Int :=
  min (gainCap i) (max 0 (min i.ti (maxZeroRate i.filing) - (i.ti - ancg i)))

/-- **When the gain exceeds taxable income, the literal (B) amount is larger than the worksheet's 0% amount** (line
22): a single filer whose income is $70,000 of qualified dividends, taxable income $54,250 after the $15,750
standard deduction. Literal (B): $54,250 at 0% (the whole taxable income); worksheet line 22: $48,350 at 0% and $5,900
at 15% ($885). -/
theorem literal_differs :
    literalB ⟨.single, 54250, 70000, 0, 0, 0⟩ = 54250 ∧ w22 ⟨.single, 54250, 70000, 0, 0, 0⟩ = 48350 ∧
    w30 ⟨.single, 54250, 70000, 0, 0, 0⟩ = 5900 ∧ w47 ⟨.single, 54250, 70000, 0, 0, 0⟩ = 88500 := by decide

/-- The literal (B) and line 22 agree whenever the adjusted net capital gain does not exceed taxable income ... -/
theorem literalB_eq (i : Inputs) (ht : 0 ≤ i.ti) (hn : 0 ≤ i.ncg0) (hq : 0 ≤ i.qd) (h : ancg i ≤ i.ti) : literalB i = w22 i := by
  rw [L22 i ht hq hn]; unfold literalB amtB gainCap; omega

/-- ... and otherwise the literal 0% amount exceeds line 22 by exactly `min (gain − TI, TI − ceiling)` (ceiling =
$48,350 / $96,700 / $64,750; zero when taxable income is under the ceiling). 15% of it is the literal reading's
saving: at most 15% of (TI − ceiling), and nothing when TI is under the ceiling. -/
theorem literalB_excess (i : Inputs) (hn : 0 ≤ i.ncg0) (hq : 0 ≤ i.qd) (ht : 0 ≤ i.ti) (h : i.ti < ancg i) :
    literalB i - w22 i = min (ancg i - i.ti) (max 0 (i.ti - maxZeroRate i.filing)) := by
  have := rates_ok i.filing
  rw [L22 i ht hq hn]; unfold literalB amtB gainCap
  omega

end TaxCode.Forms.ScheduleD

#print axioms TaxCode.Forms.ScheduleD.w47_eq_statute
#print axioms TaxCode.Forms.ScheduleD.w47_le
#print axioms TaxCode.Forms.ScheduleD.schD_eq_qdcg
#print axioms TaxCode.Forms.ScheduleD.literalB_excess
