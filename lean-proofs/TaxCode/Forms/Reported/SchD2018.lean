import TaxCode.Individual.C.Schedule

/-!
# The 2018 Schedule D Tax Worksheet, original (Dec. 2018) and corrected (May 2019), against §1(h) as of 2018

Reported: IRS, "Error in Tax Calculation in Schedule D Tax Worksheet (Form 1040)" (irs.gov/forms-pubs, archived
2019-08-23): "The tax calculation did not work correctly with the new TCJA regular tax rates and brackets for certain
Schedule D filers who had 28% rate gain ... on line 18 of Schedule D or unrecaptured section 1250 gain ... on line 19
of Schedule D. ... We corrected the Schedule D Tax Worksheet ... by renumbering line 18 as line 18a, adding new lines
18b and 18c, and updating the text on line 19". "The correction results in a lower regular tax for most affected
taxpayers, and a higher regular tax for a small number".

Form text: 2018 Instructions for Schedule D (Form 1040), Schedule D Tax Worksheet, pp. D-16–D-17.
* ORIGINAL (PDF created 2018-12-21; web.archive.org snapshot 20190130142321 of irs.gov/pub/irs-pdf/i1040sd.pdf):
  "18. Subtract line 10 from line 1. If zero or less, enter -0-"; "19. Enter the larger of line 17 or line 18".
* CORRECTED (PDF created 2019-05-15; snapshot 20190527161307; same text in irs.gov/pub/irs-prior/i1040sd--2018.pdf):
  "18a. Subtract line 10 from line 1. If zero or less, enter -0-"; "b. Enter the smaller of line 1 or $157,500
  ($315,000 if married filing jointly or qualifying widow(er))"; "c. Enter the smaller of line 14 or line 18b";
  "19. Enter the larger of line 18a or line 18c".
All other lines (1–17, 20–45) are word for word the same in both.

Statute (2018, as amended by Pub. L. 115-97): §1(h)(1)(A)–(F); §1(j)(5)(A) substitutes the maximum zero rate amount in
(B)(i) and the maximum 15-percent rate amount in (C)(ii)(I) but leaves (A)(ii)(I) "the amount of taxable income taxed
at a rate below 25 percent", which under the §1(j)(2) 2018 tables is taxable income up to the top of the 24% bracket,
$157,500 (single, head of household, separate) or $315,000 (joint, surviving spouse). §1(j)(5)(B) 2018 amounts:
$38,600 / $77,200 / $51,700 and $425,800 / $479,000 / $239,500 / $452,400; §1(j)(3)(A): no adjustment in 2018.

Method. Original line 19 = max(line 17, line 18) = max(line 18, min(line 14, min(line 1, $38,600 ...))): the
original worksheet is the corrected one with the 0% ceiling where "rate below 25 percent" belongs. So both are
instances of one worksheet `w45 i (l19gen i t)` and one statute `statuteTax i t`, proved equal for every `t` between the
0% ceiling and the 15% ceiling (`ws_eq`). Corrected = statute (`t` = top of 24%); original = the statute misread
with `t` = 0% ceiling; the gap is then a statute-side comparison.

Domain as in `TaxCode/Forms/ScheduleD.lean`: no Form 4952 election (lines 3–5, 8 zero), amounts ≥ 0, net capital gain
> 0, tax at the exact §1(j)(2) schedule in cents (the worksheet's Tax Table use under $100,000 is not modelled).
-/

namespace TaxCode.Forms.Reported.SchD2018
open TaxCode.Individual TaxCode.Individual.C

/-! ## §1(j)(2) 2018 tables and §1(j)(5)(B) 2018 amounts -/

/-- §1(j)(2)(C) unmarried individuals (2018 table, printed in the statute; bases in cents). -/
def single2018 : Sched :=
  ⟨9525, 38700, 82500, 157500, 200000, 500000, 95250, 445350, 1408950, 3208950, 4568950, 15068950⟩
/-- §1(j)(2)(A) joint returns and surviving spouses. -/
def mfj2018 : Sched :=
  ⟨19050, 77400, 165000, 315000, 400000, 600000, 190500, 890700, 2817900, 6417900, 9137900, 16137900⟩
/-- §1(j)(2)(B) heads of households. -/
def hoh2018 : Sched :=
  ⟨13600, 51800, 82500, 157500, 200000, 500000, 136000, 594400, 1269800, 3069800, 4429800, 14929800⟩
/-- §1(j)(2)(D) married filing separately. -/
def mfs2018 : Sched :=
  ⟨9525, 38700, 82500, 157500, 200000, 300000, 95250, 445350, 1408950, 3208950, 4568950, 8068950⟩

def sched18 : Filing → Sched
  | .single => single2018
  | .mfj | .qss => mfj2018
  | .hoh => hoh2018
  | .mfs => mfs2018

/-- Every base amount printed in the four 2018 tables is the exact tax at the top of the row before. -/
theorem sched18_ok (f : Filing) : (sched18 f).Ok := by cases f <;> decide

/-- Tax from the 2018 schedule, cents. -/
def cents18 (f : Filing) (x : Int) : Int := (sched18 f).cents x

/-- §1(j)(5)(B)(i) maximum zero rate amount, 2018. -/
def zero18 : Filing → Int
  | .mfj | .qss => 77200
  | .hoh => 51700
  | .single | .mfs => 38600
/-- §1(j)(5)(B)(ii) maximum 15-percent rate amount, 2018. -/
def fifteen18 : Filing → Int
  | .mfj | .qss => 479000
  | .mfs => 239500
  | .hoh => 452400
  | .single => 425800
/-- "Taxable income taxed at a rate below 25 percent": the top of the 24% row (corrected line 18b). -/
def top24 : Filing → Int
  | .mfj | .qss => 315000
  | _ => 157500

theorem top24_is_e4 (f : Filing) : top24 f = (sched18 f).e4 := by cases f <;> rfl
theorem rates18 (f : Filing) : 0 < zero18 f ∧ zero18 f < (sched18 f).e2 ∧ (sched18 f).e2 ≤ top24 f ∧
    top24 f ≤ fifteen18 f := by cases f <;> decide

structure Inputs where
  filing : Filing
  ti : Int        -- Form 1040 line 10 (2018)
  qd : Int        -- qualified dividends (Form 1040 line 3a)
  ncg0 : Int      -- smaller of Schedule D lines 15 and 16
  r28 : Int       -- 28% rate gain (Schedule D line 18)
  u1250 : Int     -- unrecaptured section 1250 gain (Schedule D line 19)
  deriving Repr, DecidableEq

/-! ## The worksheet (lines common to both versions), line 19 as a parameter `y` -/

section Worksheet
variable (i : Inputs)

def w1 : Int := i.ti
/-- Lines 2–6 (no Form 4952 election): "Subtract line 5 from line 2. If zero or less, enter -0-". -/
def w6 : Int := max 0 (i.qd - 0)
/-- Lines 7–9: "Subtract line 8 from line 7. If zero or less, enter -0-". -/
def w9 : Int := max 0 (i.ncg0 - 0)
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
/-- Line 15: "$38,600 if single or married filing separately; $77,200 if married filing jointly or qualifying
widow(er); or $51,700 if head of household". -/
def w15 : Int := zero18 i.filing
/-- Line 16: "Enter the smaller of line 1 or line 15". -/
def w16 : Int := min (w1 i) (w15 i)
/-- Line 17: "Enter the smaller of line 14 or line 16". -/
def w17 : Int := min (w14 i) (w16 i)
/-- Line 18 (original) = line 18a (corrected): "Subtract line 10 from line 1. If zero or less, enter -0-". -/
def w18 : Int := max 0 (w1 i - w10 i)
/-- Corrected line 18b: "Enter the smaller of line 1 or $157,500 ($315,000 if married filing jointly or qualifying
widow(er))". -/
def w18b : Int := min (w1 i) (top24 i.filing)
/-- Corrected line 18c: "Enter the smaller of line 14 or line 18b". -/
def w18c : Int := min (w14 i) (w18b i)
/-- ORIGINAL line 19: "Enter the larger of line 17 or line 18". -/
def l19orig : Int := max (w17 i) (w18 i)
/-- CORRECTED line 19: "Enter the larger of line 18a or line 18c". -/
def l19corr : Int := max (w18 i) (w18c i)
/-- Both, with the line-18b amount as a parameter `t`. -/
def l19gen (t : Int) : Int := max (w18 i) (min (w14 i) (min (w1 i) t))

/-- Line 20: "Subtract line 17 from line 16. This amount is taxed at 0%". -/
def w20 : Int := w16 i - w17 i
/-- "If lines 1 and 16 are the same, skip lines 21 through 41 and go to line 42." -/
def skip16 : Prop := w1 i = w16 i
instance : Decidable (skip16 i) := by unfold skip16; infer_instance
/-- Line 21: "Enter the smaller of line 1 or line 13". -/
def w21 : Int := min (w1 i) (w13 i)
/-- Line 22: "Enter the amount from line 20". -/
def w22 : Int := w20 i
/-- Line 23: "Subtract line 22 from line 21. If zero or less, enter -0-". -/
def w23 : Int := max 0 (w21 i - w22 i)
/-- Line 24: "$425,800 if single; $239,500 if married filing separately; $479,000 if married filing jointly or
qualifying widow(er); or $452,400 if head of household". -/
def w24 : Int := fifteen18 i.filing
/-- Line 25: "Enter the smaller of line 1 or line 24". -/
def w25 : Int := min (w1 i) (w24 i)

variable (y : Int)
/-- Line 26: "Add lines 19 and 20". -/
def w26 : Int := y + w20 i
/-- Line 27: "Subtract line 26 from line 25. If zero or less, enter -0-". -/
def w27 : Int := max 0 (w25 i - w26 i y)
/-- Line 28: "Enter the smaller of line 23 or line 27" (skipped after line 20). -/
def w28 : Int := if skip16 i then 0 else min (w23 i) (w27 i y)
/-- Line 30: "Add lines 22 and 28". -/
def w30 : Int := w22 i + w28 i y
/-- "If lines 1 and 30 are the same, skip lines 31 through 41". -/
def skip30 : Prop := w1 i = w30 i y
instance : Decidable (skip30 i y) := by unfold skip30; infer_instance
/-- Line 31: "Subtract line 30 from line 21". -/
def w31 : Int := if skip16 i ∨ skip30 i y then 0 else w21 i - w30 i y
/-- Line 33: "Enter the smaller of line 9 above or Schedule D, line 19". -/
def w33 : Int := min (w9 i) i.u1250
/-- Lines 34–36: "Add lines 10 and 19"; line 35 = line 1; "Subtract line 35 from line 34. If zero or less, enter -0-". -/
def w36 : Int := max 0 (w10 i + y - w1 i)
/-- Line 37: "Subtract line 36 from line 33. If zero or less, enter -0-" (skipped if Schedule D line 19 is zero). -/
def w37 : Int := if i.u1250 = 0 ∨ skip16 i ∨ skip30 i y then 0 else max 0 (w33 i - w36 i y)
/-- Lines 39–40: "Add lines 19, 20, 28, 31, and 37"; "Subtract line 39 from line 1" (skipped if Schedule D line 18 is
zero). -/
def w40 : Int :=
  if i.r28 = 0 ∨ skip16 i ∨ skip30 i y then 0 else w1 i - (y + w20 i + w28 i y + w31 i y + w37 i y)
/-- Line 43 in cents: lines 29 (15% of 28), 32 (20% of 31), 38 (25% of 37), 41 (28% of 40), 42 (tax on line 19). -/
def w43 : Int := 15 * w28 i y + 20 * w31 i y + 25 * w37 i y + 28 * w40 i y + cents18 i.filing y
/-- Line 45: "Enter the smaller of line 43 or line 44" (line 44: tax on line 1). -/
def w45 : Int := min (w43 i y) (cents18 i.filing (w1 i))

end Worksheet

/-- The original worksheet's line 45 and the corrected worksheet's line 45. -/
def original (i : Inputs) : Int := w45 i (l19orig i)
def corrected (i : Inputs) : Int := w45 i (l19corr i)

theorem orig_is_gen (i : Inputs) : l19orig i = l19gen i (zero18 i.filing) := by
  unfold l19orig l19gen w17 w16 w15; omega
theorem corr_is_gen (i : Inputs) : l19corr i = l19gen i (top24 i.filing) := by
  unfold l19corr l19gen w18c w18b; rfl

/-! ## §1(h)(1), with the "rate below 25 percent" amount as a parameter `t` -/

section Statute
variable (i : Inputs) (t : Int)
def ncg : Int := i.ncg0 + i.qd
def ancg : Int := max 0 (i.ncg0 - (i.u1250 + i.r28)) + i.qd
def gainCap : Int := min (ancg i) i.ti
/-- (A) "the greater of (i) taxable income reduced by the net capital gain; or (ii) the lesser of (I) the amount of
taxable income taxed at a rate below 25 percent [`min ti t`]; or (II) taxable income reduced by the adjusted net
capital gain". -/
def amtA : Int := max (max 0 (i.ti - ncg i)) (min (min i.ti t) (max 0 (i.ti - ancg i)))
/-- (B) with §1(j)(5)(A)(i): the maximum zero rate amount. -/
def amtB : Int := min (gainCap i) (max 0 (min i.ti (zero18 i.filing) - max 0 (i.ti - ancg i)))
/-- (C) with §1(j)(5)(A)(ii): the maximum 15-percent rate amount. -/
def amtC : Int := min (gainCap i - amtB i) (max 0 (min i.ti (fifteen18 i.filing) - (amtA i t + amtB i)))
def amtD : Int := gainCap i - amtB i - amtC i t
def amtE : Int := max 0 (min i.u1250 i.ncg0 - max 0 (amtA i t + ncg i - i.ti))
def amtF : Int := max 0 (i.ti - (amtA i t + amtB i + amtC i t + amtD i t + amtE i t))
def capSum : Int :=
  cents18 i.filing (amtA i t) + 15 * amtC i t + 20 * amtD i t + 25 * amtE i t + 28 * amtF i t
def statuteTax : Int :=
  if 0 < ncg i then min (cents18 i.filing i.ti) (capSum i t) else cents18 i.filing i.ti
end Statute

/-- **§1(h) for 2018**: "taxed at a rate below 25 percent" = up to the top of the 24% bracket. -/
def statute (i : Inputs) : Int := statuteTax i (top24 i.filing)

/-! ## The worksheet computes §1(h)(1) for every admissible `t` -/

section Proofs
variable (i : Inputs) (t : Int) (ht : 0 ≤ i.ti) (hq : 0 ≤ i.qd) (hn : 0 ≤ i.ncg0) (hr : 0 ≤ i.r28)
  (hu : 0 ≤ i.u1250) (hz : zero18 i.filing ≤ t) (hf : t ≤ fifteen18 i.filing)

include hq hn in
theorem L13 : w13 i = ancg i := by unfold w13 w12 w11 w10 w9 w6 ancg; omega
include hq hn in
theorem L10 : w10 i = ncg i := by unfold w10 w9 w6 ncg; omega

include hq hn in
/-- Line 19 (either version, via `t`) is (A). -/
theorem L19 : l19gen i t = amtA i t := by
  unfold l19gen w18 w14 w1; rw [L13 i hq hn, L10 i hq hn]; unfold amtA; omega

include ht hq hn in
/-- Line 20 is (B). -/
theorem L20 : w20 i = amtB i := by
  have : 0 ≤ ancg i := by unfold ancg; omega
  unfold w20 w17 w16 w15 w14 w1; rw [L13 i hq hn]; unfold amtB gainCap; omega

include ht hq hn hr hu hz hf in
theorem facts :
    0 ≤ amtA i t ∧ i.ti - ncg i ≤ amtA i t ∧ 0 ≤ amtB i ∧ 0 ≤ amtC i t ∧ amtB i + amtC i t ≤ gainCap i ∧
    0 ≤ gainCap i ∧ gainCap i = min (ancg i) i.ti ∧ amtA i t + gainCap i ≤ i.ti ∧
    ncg i - ancg i = min i.ncg0 (i.u1250 + i.r28) ∧ 0 ≤ ancg i ∧
    amtD i t = gainCap i - amtB i - amtC i t ∧
    amtE i t = max 0 (min i.u1250 i.ncg0 - max 0 (amtA i t + ncg i - i.ti)) ∧
    amtF i t = max 0 (i.ti - (amtA i t + amtB i + amtC i t + amtD i t + amtE i t)) := by
  have := rates18 i.filing
  have hg : gainCap i = min (ancg i) i.ti := rfl
  have hAn : ncg i - ancg i = min i.ncg0 (i.u1250 + i.r28) := by unfold ncg ancg; omega
  have ha0 : 0 ≤ ancg i := by unfold ancg; omega
  have hA : 0 ≤ amtA i t ∧ amtA i t + gainCap i ≤ i.ti ∧ i.ti - ncg i ≤ amtA i t := by
    unfold amtA; rw [hg]; generalize ancg i = X at *; generalize ncg i = N at *; omega
  have hBC : 0 ≤ amtB i ∧ 0 ≤ amtC i t ∧ amtB i + amtC i t ≤ gainCap i := by
    unfold amtC amtB; rw [hg]; generalize amtA i t = A at *; generalize ancg i = X at *; omega
  exact ⟨hA.1, hA.2.2, hBC.1, hBC.2.1, hBC.2.2, by rw [hg]; omega, hg, hA.2.1, hAn, ha0, rfl, rfl, rfl⟩

include ht hq hn hr hu hz hf in
/-- "If lines 1 and 16 are the same, skip lines 21 through 41": then (C)–(F) are zero. -/
theorem skip16_ok (h : skip16 i) : amtC i t = 0 ∧ amtD i t = 0 ∧ amtE i t = 0 ∧ amtF i t = 0 := by
  have F := facts i t ht hq hn hr hu hz hf
  have := rates18 i.filing
  unfold skip16 w16 w15 w1 at h
  obtain ⟨h1, h1', h2, h3, h4, h5, h6, h7, h8, h9, hD, hE, hF⟩ := F
  have hA : amtA i t = max 0 (i.ti - ancg i) := by
    unfold amtA; generalize ancg i = X at *; generalize ncg i = N at *; omega
  have hB : amtB i = gainCap i := by
    unfold amtB; rw [h6]; generalize ancg i = X at *; omega
  have hC : amtC i t = 0 := by unfold amtC; rw [hB]; omega
  rw [hF, hE, hD, hC, hB]; rw [hA]
  generalize gainCap i = G at *; generalize ancg i = X at *; generalize ncg i = N at *
  refine ⟨rfl, ?_, ?_, ?_⟩ <;> omega

include ht hq hn hr hu hz hf in
/-- Line 28 is (C) when not skipped. -/
theorem L28 (h16 : ¬ skip16 i) : w28 i (amtA i t) = amtC i t := by
  have F := facts i t ht hq hn hr hu hz hf
  have := rates18 i.filing
  unfold w28; rw [if_neg h16]
  unfold w27 w26 w25 w24 w23 w22 w21 w1; rw [L13 i hq hn, L20 i ht hq hn]
  unfold amtC; rw [F.2.2.2.2.2.2.1]
  have := F.2.2.1; have := F.2.2.2.2.1; have := F.2.2.2.2.2.2.2.1
  generalize amtA i t = A at *; generalize amtB i = B at *; generalize ancg i = X at *
  omega

include ht hq hn hr hu hz hf in
theorem L30 (h16 : ¬ skip16 i) : w30 i (amtA i t) = amtB i + amtC i t := by
  unfold w30 w22; rw [L20 i ht hq hn, L28 i t ht hq hn hr hu hz hf h16]

include ht hq hn hr hu hz hf in
/-- "If lines 1 and 30 are the same, skip lines 31 through 41": then (D)–(F) are zero. -/
theorem skip30_ok (h16 : ¬ skip16 i) (h : skip30 i (amtA i t)) : amtD i t = 0 ∧ amtE i t = 0 ∧ amtF i t = 0 := by
  have F := facts i t ht hq hn hr hu hz hf
  unfold skip30 at h; rw [L30 i t ht hq hn hr hu hz hf h16] at h; unfold w1 at h
  obtain ⟨h1, h1', h2, h3, h4, h5, h6, h7, h8, h9, hD, hE, hF⟩ := F
  rw [hF, hE, hD]
  generalize amtA i t = A at *; generalize amtB i = B at *; generalize amtC i t = C at *
  generalize gainCap i = G at *; generalize ancg i = X at *; generalize ncg i = N at *
  refine ⟨?_, ?_, ?_⟩ <;> omega

include ht hq hn hr hu hz hf in
/-- **Line 45 is the §1(h) tax with "rate below 25 percent" = `t`, for all inputs ≥ 0 with a net capital gain.** -/
theorem ws_eq (hg : 0 < ncg i) : w45 i (l19gen i t) = statuteTax i t := by
  have F := facts i t ht hq hn hr hu hz hf
  obtain ⟨h1, h1', h2, h3, h4, h5, h6, h7, h8, h9, hD, hE, hF⟩ := F
  rw [L19 i t hq hn]
  unfold w45 statuteTax capSum w43; rw [if_pos hg]; unfold w1
  by_cases h16 : skip16 i
  · have ⟨c0, d0, e0, f0⟩ := skip16_ok i t ht hq hn hr hu hz hf h16
    have a28 : w28 i (amtA i t) = 0 := by unfold w28; rw [if_pos h16]
    have a31 : w31 i (amtA i t) = 0 := by unfold w31; rw [if_pos (Or.inl h16)]
    have a37 : w37 i (amtA i t) = 0 := by unfold w37; rw [if_pos (Or.inr (Or.inl h16))]
    have a40 : w40 i (amtA i t) = 0 := by unfold w40; rw [if_pos (Or.inr (Or.inl h16))]
    rw [a28, a31, a37, a40, c0, d0, e0, f0]; omega
  · rw [L28 i t ht hq hn hr hu hz hf h16]
    by_cases h30 : skip30 i (amtA i t)
    · have ⟨d0, e0, f0⟩ := skip30_ok i t ht hq hn hr hu hz hf h16 h30
      have a31 : w31 i (amtA i t) = 0 := by unfold w31; rw [if_pos (Or.inr h30)]
      have a37 : w37 i (amtA i t) = 0 := by unfold w37; rw [if_pos (Or.inr (Or.inr h30))]
      have a40 : w40 i (amtA i t) = 0 := by unfold w40; rw [if_pos (Or.inr (Or.inr h30))]
      rw [a31, a37, a40, d0, e0, f0]; omega
    · have a31 : w31 i (amtA i t) = amtD i t := by
        unfold w31; rw [if_neg (fun h => h.elim h16 h30)]; unfold w21 w1
        rw [L13 i hq hn, L30 i t ht hq hn hr hu hz hf h16, hD, h6]; omega
      have a37 : w37 i (amtA i t) = amtE i t := by
        unfold w37
        by_cases hu0 : i.u1250 = 0
        · rw [if_pos (Or.inl hu0), hE, hu0]; omega
        · rw [if_neg (fun h => h.elim hu0 (fun h => h.elim h16 h30))]; unfold w33 w36 w9 w1; rw [L10 i hq hn, hE]; omega
      have a40 : w40 i (amtA i t) = amtF i t := by
        unfold w40
        by_cases hr0 : i.r28 = 0
        · rw [if_pos (Or.inl hr0), hF, hD, hE]; rw [hr0] at h8
          generalize amtA i t = A at *; generalize amtB i = B at *; generalize amtC i t = C at *
          generalize gainCap i = G at *; generalize ancg i = X at *; generalize ncg i = N at *
          omega
        · rw [if_neg (fun h => h.elim hr0 (fun h => h.elim h16 h30)), a31, a37, L20 i ht hq hn, L28 i t ht hq hn hr hu hz hf h16, hF, hD, hE]; unfold w1
          generalize amtA i t = A at *; generalize amtB i = B at *; generalize amtC i t = C at *
          generalize gainCap i = G at *; generalize ancg i = X at *; generalize ncg i = N at *
          omega
      rw [a31, a37, a40]; omega
end Proofs

/-- **The corrected 2018 worksheet equals §1(h) for all inputs ≥ 0 with a net capital gain.** -/
theorem corrected_eq_statute (i : Inputs) (ht : 0 ≤ i.ti) (hq : 0 ≤ i.qd) (hn : 0 ≤ i.ncg0) (hr : 0 ≤ i.r28)
    (hu : 0 ≤ i.u1250) (hg : 0 < ncg i) : corrected i = statute i := by
  have := rates18 i.filing
  unfold corrected statute; rw [corr_is_gen]
  exact ws_eq i _ ht hq hn hr hu (by omega) (by omega) hg

/-- **The original 2018 worksheet computes §1(h) with the 0% ceiling in place of "rate below 25 percent".** -/
theorem original_eq_misread (i : Inputs) (ht : 0 ≤ i.ti) (hq : 0 ≤ i.qd) (hn : 0 ≤ i.ncg0) (hr : 0 ≤ i.r28)
    (hu : 0 ≤ i.u1250) (hg : 0 < ncg i) : original i = statuteTax i (zero18 i.filing) := by
  have := rates18 i.filing
  unfold original; rw [orig_is_gen]
  exact ws_eq i _ ht hq hn hr hu (by omega) (by omega) hg

/-! ## Where the original differs -/

/-- **Original line 19 is never above the corrected one, and is strictly below it exactly when** taxable income less
the adjusted net capital gain (line 14) exceeds the 0% ceiling and the corrected (A)(ii) amount
`min(TI − ANCG, top of 24%)` exceeds `max(0, TI − NCG)` (line 18). This needs 28% or §1250 gain (NCG > ANCG); it is the
IRS notice's list (TI over $38,600/$51,700/$77,200, line 15 ≤ line 14, line 18 ≤ $157,500/$315,000) with the
boundary cases, where nothing changes, removed. -/
theorem l19_differs (i : Inputs) (hq : 0 ≤ i.qd) (hn : 0 ≤ i.ncg0) (hr : 0 ≤ i.r28) (hu : 0 ≤ i.u1250) :
    l19orig i ≤ l19corr i ∧
    (l19orig i < l19corr i ↔
      zero18 i.filing < i.ti - ancg i ∧ max 0 (i.ti - ncg i) < min (i.ti - ancg i) (top24 i.filing)) := by
  have := rates18 i.filing
  rw [orig_is_gen, corr_is_gen, L19 i _ hq hn, L19 i _ hq hn]
  have : 0 ≤ ancg i := by unfold ancg; omega
  have : ancg i ≤ ncg i := by unfold ancg ncg; omega
  unfold amtA; generalize ancg i = X at *; generalize ncg i = N at *
  constructor <;> omega

/-- §1(h) amounts at the two values of `t`: what moves when (A) shrinks. -/
theorem cross (i : Inputs) (ht : 0 ≤ i.ti) (hq : 0 ≤ i.qd) (hn : 0 ≤ i.ncg0) (hr : 0 ≤ i.r28) (hu : 0 ≤ i.u1250) :
    let z := zero18 i.filing; let T := top24 i.filing
    amtA i z ≤ amtA i T ∧
    0 ≤ amtC i z - amtC i T ∧ amtC i z - amtC i T ≤ amtA i T - amtA i z ∧
    0 ≤ amtE i z - amtE i T ∧ amtE i z - amtE i T ≤ amtA i T - amtA i z ∧
    amtC i z + amtD i z = amtC i T + amtD i T ∧
    amtA i z + amtB i + amtC i z + amtD i z + amtE i z + amtF i z = i.ti ∧
    amtA i T + amtB i + amtC i T + amtD i T + amtE i T + amtF i T = i.ti ∧
    (amtA i z < amtA i T → zero18 i.filing ≤ amtA i z ∧ amtA i T ≤ top24 i.filing) := by
  intro z T
  have R := rates18 i.filing
  have Fz := facts i z ht hq hn hr hu (Int.le_refl _) (by omega)
  have FT := facts i T ht hq hn hr hu (by omega) (by omega)
  obtain ⟨a1, a1', a2, a3, a4, a5, a6, a7, a8, a9, aD, aE, aF⟩ := Fz
  obtain ⟨b1, b1', b2, b3, b4, b5, b6, b7, b8, b9, bD, bE, bF⟩ := FT
  have hAA : amtA i z ≤ amtA i T ∧ (amtA i z < amtA i T → z ≤ amtA i z ∧ amtA i T ≤ T) := by
    unfold amtA; generalize ancg i = X at *; generalize ncg i = N at *; omega
  have hC : 0 ≤ amtC i z - amtC i T ∧ amtC i z - amtC i T ≤ amtA i T - amtA i z := by
    unfold amtC; generalize amtA i z = Az at *; generalize amtA i T = AT at *; omega
  have hE : 0 ≤ amtE i z - amtE i T ∧ amtE i z - amtE i T ≤ amtA i T - amtA i z := by
    rw [aE, bE]; generalize amtA i z = Az at *; generalize amtA i T = AT at *; omega
  rw [aD, bD, aF, bF, aD, bD]
  generalize amtA i z = Az at *; generalize amtA i T = AT at *; generalize amtC i z = Cz at *
  generalize amtC i T = CT at *; generalize amtE i z = Ez at *; generalize amtE i T = ET at *
  generalize amtB i = B at *; generalize gainCap i = G at *; generalize ancg i = X at *
  generalize ncg i = N at *
  refine ⟨hAA.1, hC.1, hC.2, hE.1, hE.2, by omega, by omega, by omega, hAA.2⟩

/-! ## The size of the error -/

/-- The most the original can overcharge: every dollar between the 0% ceiling and the top of the 24% bracket taxed at
28% instead of the ordinary rate: 28% × (top24 − ceiling) − (tax(top24) − tax(ceiling)). In dollars: $5,644 single and
separate, $11,288 joint, $4,858 head of household. -/
def maxOver (f : Filing) : Int :=
  28 * (top24 f - zero18 f) - (cents18 f (top24 f) - cents18 f (zero18 f))
/-- The most the original can undercharge: (tax(top24) − 20% × top24) − (tax(e2) − 20% × e2), e2 = top of the 12%
row ($38,700 / $77,400 / $51,800): $3,876 single and separate, $7,752 joint, $3,614 head of household. -/
def maxUnder (f : Filing) : Int :=
  (cents18 f (top24 f) - 20 * top24 f) - (cents18 f (sched18 f).e2 - 20 * (sched18 f).e2)

theorem maxOver_val : maxOver .single = 564400 ∧ maxOver .mfs = 564400 ∧ maxOver .mfj = 1128800 ∧
    maxOver .qss = 1128800 ∧ maxOver .hoh = 485800 := by decide
theorem maxUnder_val : maxUnder .single = 387600 ∧ maxUnder .mfs = 387600 ∧ maxUnder .mfj = 775200 ∧
    maxUnder .qss = 775200 ∧ maxUnder .hoh = 361400 := by decide

/-- Between the 0% ceiling and the top of the 24% row the ordinary rate is below 28% and (except for the first
$100/$200 of the 12% row) at least 20%: the two schedule facts the bounds need. -/
theorem sched_band (f : Filing) (a b : Int) (ha : zero18 f ≤ a) (hab : a ≤ b) (hb : b ≤ top24 f) :
    28 * (b - a) - (cents18 f b - cents18 f a) ≤ maxOver f ∧
    (cents18 f b - cents18 f a) - 20 * (b - a) ≤ maxUnder f := by
  cases f <;>
    simp only [maxOver, maxUnder, cents18, sched18, zero18, top24, Sched.cents, single2018, mfj2018, hoh2018,
      mfs2018] at * <;>
    (repeat' split) <;> omega

/-- **For every input ≥ 0 with a net capital gain, the original worksheet's tax is at most `maxOver` above and at
most `maxUnder` below the §1(h) tax** (cents; exact schedule). -/
theorem original_gap (i : Inputs) (ht : 0 ≤ i.ti) (hq : 0 ≤ i.qd) (hn : 0 ≤ i.ncg0) (hr : 0 ≤ i.r28)
    (hu : 0 ≤ i.u1250) (hg : 0 < ncg i) :
    original i - statute i ≤ maxOver i.filing ∧ statute i - original i ≤ maxUnder i.filing := by
  have R := rates18 i.filing
  rw [original_eq_misread i ht hq hn hr hu hg]
  have X := cross i ht hq hn hr hu
  simp only at X
  obtain ⟨x1, x2, x3, x4, x5, x6, x7, x8, x9⟩ := X
  have M0 : 0 ≤ maxOver i.filing ∧ 0 ≤ maxUnder i.filing := by cases i.filing <;> decide
  unfold statute statuteTax capSum; rw [if_pos hg, if_pos hg]
  by_cases hlt : amtA i (zero18 i.filing) < amtA i (top24 i.filing)
  · have ⟨y1, y2⟩ := x9 hlt
    have S := sched_band i.filing _ _ y1 (by omega) y2
    generalize cents18 i.filing (amtA i (zero18 i.filing)) = cz at *
    generalize cents18 i.filing (amtA i (top24 i.filing)) = cT at *
    generalize cents18 i.filing i.ti = c at *
    generalize amtA i (zero18 i.filing) = Az at *; generalize amtA i (top24 i.filing) = AT at *
    generalize amtC i (zero18 i.filing) = Cz at *; generalize amtC i (top24 i.filing) = CT at *
    generalize amtD i (zero18 i.filing) = Dz at *; generalize amtD i (top24 i.filing) = DT at *
    generalize amtE i (zero18 i.filing) = Ez at *; generalize amtE i (top24 i.filing) = ET at *
    generalize amtF i (zero18 i.filing) = Fz at *; generalize amtF i (top24 i.filing) = FT at *
    omega
  · have he : amtA i (zero18 i.filing) = amtA i (top24 i.filing) := by omega
    have e1 : amtC i (zero18 i.filing) = amtC i (top24 i.filing) := by omega
    have e2 : amtE i (zero18 i.filing) = amtE i (top24 i.filing) := by omega
    rw [he, e1, e2] at *
    have e3 : amtD i (zero18 i.filing) = amtD i (top24 i.filing) := by omega
    have e4 : amtF i (zero18 i.filing) = amtF i (top24 i.filing) := by omega
    rw [he, e1, e2, e3, e4]; omega

/-! ## Examples (cents) -/

/-- A typical case: single, $100,000 wages, $20,000 collectibles gain (28% rate gain), $30,000 other long-term gain,
$12,000 standard deduction: taxable income $138,000. Statute: (A) = $108,000 (the collectibles gain sits below
$157,500, where rates are under 25%, so it is taxed at ordinary rates), $30,000 at 15%: $24,709.50. Original
worksheet: line 19 = $88,000, the $20,000 at 28%: $25,509.50. Overcharge $800 (4% of the 28% gain). Corrected
worksheet: $24,709.50. (With no 15% gain the line-44 cap hides the error: the plain schedule tax is lower.) -/
def typical : Inputs := ⟨.single, 138000, 0, 50000, 20000, 0⟩
theorem typical_case :
    l19orig typical = 88000 ∧ l19corr typical = 108000 ∧ original typical = 2550950 ∧
    corrected typical = 2470950 ∧ statute typical = 2470950 := by decide

/-- Maximum overcharge attained for each status: ordinary income 0, 28% gain = top of the 24% row, other gain
$42,500 / $80,000 / $40,000 / $40,000. -/
def overS : Inputs := ⟨.single, 200000, 0, 200000, 157500, 0⟩
def overJ : Inputs := ⟨.mfj, 395000, 0, 395000, 315000, 0⟩
def overH : Inputs := ⟨.hoh, 197500, 0, 197500, 157500, 0⟩
def overM : Inputs := ⟨.mfs, 197500, 0, 197500, 157500, 0⟩
theorem over_attained :
    original overS - corrected overS = maxOver .single ∧ corrected overS = statute overS ∧
    original overJ - corrected overJ = maxOver .mfj ∧ original overH - corrected overH = maxOver .hoh ∧
    original overM - corrected overM = maxOver .mfs := by decide

/-- Maximum undercharge attained: ordinary income at the top of the 12% row, unrecaptured §1250 gain = top24 − that,
other gain = 15% ceiling − top of the 12% row + $10,000 (the original lets §1250 gain displace 20% gain into the 15%
band). -/
def underS : Inputs := ⟨.single, 554600, 0, 515900, 0, 118800⟩
def underJ : Inputs := ⟨.mfj, 726600, 0, 649200, 0, 237600⟩
def underH : Inputs := ⟨.hoh, 568100, 0, 516300, 0, 105700⟩
def underM : Inputs := ⟨.mfs, 368300, 0, 329600, 0, 118800⟩
theorem under_attained :
    corrected underS - original underS = maxUnder .single ∧ corrected underS = statute underS ∧
    corrected underJ - original underJ = maxUnder .mfj ∧ corrected underH - original underH = maxUnder .hoh ∧
    corrected underM - original underM = maxUnder .mfs := by decide

end TaxCode.Forms.Reported.SchD2018

#print axioms TaxCode.Forms.Reported.SchD2018.corrected_eq_statute
#print axioms TaxCode.Forms.Reported.SchD2018.original_eq_misread
#print axioms TaxCode.Forms.Reported.SchD2018.l19_differs
#print axioms TaxCode.Forms.Reported.SchD2018.original_gap
#print axioms TaxCode.Forms.Reported.SchD2018.typical_case
#print axioms TaxCode.Forms.Reported.SchD2018.over_attained
#print axioms TaxCode.Forms.Reported.SchD2018.under_attained
