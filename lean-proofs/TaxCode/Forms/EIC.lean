import TaxCode.Individual.D.EarnedIncome
import TaxCode.Forms.EICTableData

/-!
# The 2025 EIC Table (as printed), EIC Worksheet A, the investment-income test and the separated-spouse rule,
# against §32

Form text: the 2025 EIC Table in Publication 1040 (2025) (irs.gov/pub/irs-pdf/i1040tt.pdf), parsed by
`tools/forms/parse_eic_table.py` into `EICTableData` (1,374 rows × 8 columns; the 8 starred cells and their
footnotes as `splits`); 2025 Instructions for Form 1040, line 27a: Step 1 question 5, Step 2 ("Investment Income"),
Worksheet A—2025 EIC, "Special rule for separated spouses"; Publication 596 (2025) repeats the separated-spouse text.

Statute: §32(a)–(b), (d)(2), (f), (i), via `TaxCode.Individual.D.EarnedIncome` (2025 amounts, Rev. Proc. 2024-40
§3.06). `D.eicScaled` is the statute's credit in 1/10000 dollar.

Method for the table: a row check at the row's ends and at the formula's two kinks (clamped into the row), proved
sound once from the shape of §32(a) (rising, flat, falling; the earned income amount is below the phase-out amount
in every column), then evaluated by the kernel (`decide +kernel`).
-/

namespace TaxCode.Forms.EIC
open TaxCode.Individual TaxCode.Individual.D

/-! ## The printed table -/

/-- Column `c`: 0–3 = single/HOH/QSS (and, "★", MFS separated spouses) with 0, 1, 2, 3+ children; 4–7 = MFJ. -/
def kidsOf (c : Nat) : Nat := c % 4
def jointOf (c : Nat) : Bool := decide (4 ≤ c)

/-- The printed column as bands `[lo, hi)` with a credit, a starred cell becoming two bands from its footnote:
"at least $X but less than $Y ... your credit is $Z"; "$Y or more ... you can't take the credit". -/
def colBands (c : Nat) : List (Int × Int × Int) :=
  rows.flatMap fun (lo, hi, vs) =>
    let v := vs.getD c 0
    if v = -1 then
      match splits.find? (fun s => s.1 = c ∧ s.2.1 = lo) with
      | some (_, _, co, z) => [(lo, co, z), (co, hi, 0)]
      | none => [(lo, hi, 0)]
    else [(lo, hi, v)]

def find? : List (Int × Int × Int) → Int → Option (Int × Int × Int)
  | [], _ => none
  | r :: rs, x => if r.1 ≤ x ∧ x < r.2.1 then some r else find? rs x

/-- EIC Worksheet A lines 2 and 5: "Look up the amount ... in the EIC Table". Amounts not in the table (below $1, or at
or above the last line) give no credit. -/
def tableAmt (c : Nat) (x : Int) : Int := ((find? (colBands c) x).map (·.2.2)).getD 0

theorem find?_spec : ∀ (rs : List (Int × Int × Int)) (x : Int) (r : Int × Int × Int),
    find? rs x = some r → r ∈ rs ∧ r.1 ≤ x ∧ x < r.2.1
  | [], _, _, h => by simp [find?] at h
  | s :: rs, x, r, h => by
    unfold find? at h
    split at h
    · cases h; exact ⟨List.mem_cons_self .., by omega, by omega⟩
    · have := find?_spec rs x r h; exact ⟨List.mem_cons_of_mem _ this.1, this.2⟩

theorem find?_none_of_all_lt (rs : List (Int × Int × Int)) (x : Int) (h : rs.all (fun r => decide (r.2.1 ≤ x)) = true) :
    find? rs x = none := by
  induction rs with
  | nil => rfl
  | cons r rs ih =>
    simp only [List.all_cons, Bool.and_eq_true, decide_eq_true_eq] at h
    unfold find?; rw [if_neg (by omega)]; exact ih h.2

/-! ## The statute, per column -/

def P (c : Nat) : EicParams := eicParams (kidsOf c)
def thrOf (c : Nat) : Int := (P c).thr (jointOf c)

/-- §32(a), one amount looked up (earned income = AGI), in 1/10000 dollar. -/
def fStat (c : Nat) (x : Int) : Int := eicScaled (P c).cp (P c).pp (P c).eia (thrOf c) x x

def clamp (v a b : Int) : Int := max a (min v b)

section Shape
variable (cp pp eia thr : Int) (hcp : 0 ≤ cp) (hpp : 0 ≤ pp)

/-- §32(a) on one amount `y` (earned income = AGI). -/
abbrev F (y : Int) : Int := eicScaled cp pp eia thr y y

include hcp in
theorem F_up (y z : Int) (hyz : y ≤ z) (hz : z ≤ thr) : F cp pp eia thr y ≤ F cp pp eia thr z := by
  have h1 : cp * min y eia ≤ cp * min z eia := Int.mul_le_mul_of_nonneg_left (by omega) hcp
  have hy : pos (max y y - thr) = 0 := by unfold pos; omega
  have hz' : pos (max z z - thr) = 0 := by unfold pos; omega
  simp only [F, eicScaled, hy, hz']
  generalize cp * min y eia = A at *; generalize cp * min z eia = B at *
  unfold pos; omega

include hpp in
theorem F_down (y z : Int) (hy : eia ≤ y) (hyz : y ≤ z) : F cp pp eia thr z ≤ F cp pp eia thr y := by
  have h2 : pp * pos (max y y - thr) ≤ pp * pos (max z z - thr) :=
    Int.mul_le_mul_of_nonneg_left (by unfold pos; omega) hpp
  have e1 : min y eia = eia := by omega
  have e2 : min z eia = eia := by omega
  simp only [F, eicScaled, e1, e2]
  generalize pp * pos (max y y - thr) = A at *; generalize pp * pos (max z z - thr) = B at *
  unfold pos; omega

include hcp hpp in
theorem F_low (a x b : Int) (hax : a ≤ x) (hxb : x ≤ b) :
    min (F cp pp eia thr a) (F cp pp eia thr b) ≤ F cp pp eia thr x := by
  have h1 : cp * min a eia ≤ cp * min x eia := Int.mul_le_mul_of_nonneg_left (by omega) hcp
  have h2 : pp * pos (max x x - thr) ≤ pp * pos (max b b - thr) :=
    Int.mul_le_mul_of_nonneg_left (by unfold pos; omega) hpp
  simp only [F, eicScaled]
  generalize cp * min a eia = A1 at *; generalize cp * min x eia = X1 at *; generalize cp * min b eia = B1 at *
  generalize pp * pos (max a a - thr) = A2 at *; generalize pp * pos (max x x - thr) = X2 at *
  generalize pp * pos (max b b - thr) = B2 at *
  unfold pos; omega

end Shape

/-- **Shape lemma.** For credit/phase-out percentages ≥ 0 with the earned income amount at or below the phase-out
amount, the §32(a) credit on `[a, b]` is at least its smaller end value and at most the largest of its values at the
two ends and at the two kinks clamped into the interval. -/
theorem shape (cp pp eia thr a b x : Int) (hcp : 0 ≤ cp) (hpp : 0 ≤ pp) (hk : eia ≤ thr) (hax : a ≤ x) (hxb : x ≤ b) :
    min (F cp pp eia thr a) (F cp pp eia thr b) ≤ F cp pp eia thr x ∧
      F cp pp eia thr x ≤ max (max (F cp pp eia thr a) (F cp pp eia thr b))
        (max (F cp pp eia thr (clamp eia a b)) (F cp pp eia thr (clamp thr a b))) := by
  refine ⟨F_low cp pp eia thr hcp hpp a x b hax hxb, ?_⟩
  simp only [clamp]
  by_cases h1 : x ≤ eia
  · have := F_up cp pp eia thr hcp x (max a (min eia b)) (by omega) (by omega); omega
  · by_cases h2 : x ≤ thr
    · have := F_down cp pp eia thr hpp (max a (min eia b)) x (by omega) (by omega); omega
    · have := F_down cp pp eia thr hpp (max a (min thr b)) x (by omega) (by omega); omega

theorem params_ok (c : Nat) : 0 ≤ (P c).cp ∧ 0 ≤ (P c).pp ∧ (P c).eia ≤ thrOf c := by
  simp only [P, thrOf, kidsOf, EicParams.thr]
  have h : c % 4 = 0 ∨ c % 4 = 1 ∨ c % 4 = 2 ∨ c % 4 = 3 := by omega
  rcases h with h | h | h | h <;> rw [h] <;> cases jointOf c <;> decide

/-! ## Row check -/

/-- A band passes if the table is at most `over` above and `under` below the statute at every point, judged at the
ends and the clamped kinks (`shape`). -/
def bandOk (c : Nat) (over under : Int) (r : Int × Int × Int) : Bool :=
  let a := r.1; let b := r.2.1 - 1; let v := 10000 * r.2.2
  decide (0 ≤ a) && decide (a ≤ b) &&
  decide (v - min (fStat c a) (fStat c b) ≤ over) &&
  decide (max (max (fStat c a) (fStat c b)) (max (fStat c (clamp (P c).eia a b)) (fStat c (clamp (thrOf c) a b)))
    - v ≤ under)

/-- The bands run without gap from `a` to $68,700 (the table's last "less than"). -/
def chain : Int → List (Int × Int × Int) → Bool
  | a, [] => a == 68700
  | a, r :: rs => r.1 == a && decide (r.1 < r.2.1) && chain r.2.1 rs

theorem chain_find : ∀ (rs : List (Int × Int × Int)) (a x : Int), chain a rs = true → a ≤ x → x < 68700 →
    (find? rs x).isSome
  | [], a, x, h, h1, h2 => by simp [chain] at h; omega
  | r :: rs, a, x, h, h1, h2 => by
    simp only [chain, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at h
    unfold find?
    split
    · rfl
    · exact chain_find rs r.2.1 x h.2 (by omega) h2

/-- Everything the kernel checks for one column. -/
def colOk (c : Nat) (over under : Int) : Bool :=
  chain 1 (colBands c) && (colBands c).all (bandOk c over under) && decide (fStat c 0 = 0) &&
    decide (0 ≤ over) && decide (thrOf c ≤ 68700) && decide (fStat c 68700 ≤ under)

theorem fStat_nonneg (c : Nat) (x : Int) : 0 ≤ fStat c x := eicScaled_bounds _ _ _ _ _ _

/-- Past the phase-out amount the credit only falls. -/
theorem fStat_falls (c : Nat) (y x : Int) (hy : thrOf c ≤ y) (hyx : y ≤ x) : fStat c x ≤ fStat c y := by
  have ⟨hcp, hpp, hk⟩ := params_ok c
  exact F_down _ _ _ _ hpp y x (by omega) hyx

/-- **Soundness**: a column that passes `colOk` is within `over`/`under` of §32(a) at every amount `x ≥ 0`. -/
theorem bounds_of_colOk (c : Nat) (over under : Int) (h : colOk c over under = true) (x : Int) (hx : 0 ≤ x) :
    10000 * tableAmt c x - fStat c x ≤ over ∧ fStat c x - 10000 * tableAmt c x ≤ under := by
  simp only [colOk, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨hch, hall⟩, h0⟩, hov⟩, hthr⟩, htail⟩ := h
  have hfn := fStat_nonneg c x
  cases hf : find? (colBands c) x with
  | some r =>
    have ⟨hm, hlo, hhi⟩ := find?_spec _ x r hf
    have hr := List.all_eq_true.mp hall r hm
    simp only [bandOk, Bool.and_eq_true, decide_eq_true_eq] at hr
    have ⟨hcp, hpp, hk⟩ := params_ok c
    have hs := shape (P c).cp (P c).pp (P c).eia (thrOf c) r.1 (r.2.1 - 1) x hcp hpp hk hlo (by omega)
    simp only [F] at hs
    simp only [tableAmt, hf, Option.map_some, Option.getD_some]
    unfold fStat at *
    omega
  | none =>
    simp only [tableAmt, hf, Option.map_none, Option.getD_none]
    by_cases hlt : x < 68700
    · by_cases h1 : 1 ≤ x
      · have := chain_find _ 1 x hch h1 hlt; rw [hf] at this; simp at this
      · have hx0 : x = 0 := by omega
        have := fStat_nonneg c 68700
        subst hx0; omega
    · have := fStat_falls c 68700 x hthr (by omega)
      omega

/-! ## The exact maxima, per column (1/10000 dollar) -/

/-- Over (table above statute) and under (statute above table) maxima for columns 0–7, from
`tools/forms/eic_extremes.py`; proved below to be bounds and attained. -/
def overMax : Nat → Int
  | 0 | 4 => 25750 | 1 | 5 => 100000 | 2 | 6 => 120000 | _ => 135000
def underMax : Nat → Int
  | 0 => 28900 | 4 => 28800 | 1 | 5 => 76600 | 2 | 6 => 96000 | _ => 110500

theorem col0 : colOk 0 (overMax 0) (underMax 0) = true := by decide +kernel
theorem col1 : colOk 1 (overMax 1) (underMax 1) = true := by decide +kernel
theorem col2 : colOk 2 (overMax 2) (underMax 2) = true := by decide +kernel
theorem col3 : colOk 3 (overMax 3) (underMax 3) = true := by decide +kernel
theorem col4 : colOk 4 (overMax 4) (underMax 4) = true := by decide +kernel
theorem col5 : colOk 5 (overMax 5) (underMax 5) = true := by decide +kernel
theorem col6 : colOk 6 (overMax 6) (underMax 6) = true := by decide +kernel
theorem col7 : colOk 7 (overMax 7) (underMax 7) = true := by decide +kernel

theorem colOk_all (c : Nat) (hc : c < 8) : colOk c (overMax c) (underMax c) = true := by
  match c, hc with
  | 0, _ => exact col0 | 1, _ => exact col1 | 2, _ => exact col2 | 3, _ => exact col3
  | 4, _ => exact col4 | 5, _ => exact col5 | 6, _ => exact col6 | 7, _ => exact col7

/-- **The printed 2025 EIC Table against §32(a), every column, every whole-dollar amount ≥ 0** (one amount looked up,
earned income = AGI): at most $2.575 / $10 / $12 / $13.50 above the statute (0 / 1 / 2 / 3+ children) and at most
$2.89 (single, no child) / $2.88 (joint, no child) / $7.66 / $9.60 / $11.05 below it. -/
theorem table_bounds (c : Nat) (hc : c < 8) (x : Int) (hx : 0 ≤ x) :
    10000 * tableAmt c x - fStat c x ≤ overMax c ∧ fStat c x - 10000 * tableAmt c x ≤ underMax c :=
  bounds_of_colOk c _ _ (colOk_all c hc) x hx

/-- Both bounds are attained in every column. -/
theorem table_bounds_attained :
    10000 * tableAmt 0 8450 - fStat 0 8450 = 25750 ∧ fStat 0 10850 - 10000 * tableAmt 0 10850 = 28900 ∧
    10000 * tableAmt 4 8450 - fStat 4 8450 = 25750 ∧ fStat 4 18300 - 10000 * tableAmt 4 18300 = 28800 ∧
    10000 * tableAmt 1 12700 - fStat 1 12700 = 100000 ∧ fStat 1 49 - 10000 * tableAmt 1 49 = 76600 ∧
    10000 * tableAmt 5 12700 - fStat 5 12700 = 100000 ∧ fStat 5 49 - 10000 * tableAmt 5 49 = 76600 ∧
    10000 * tableAmt 2 17850 - fStat 2 17850 = 120000 ∧ fStat 2 49 - 10000 * tableAmt 2 49 = 96000 ∧
    10000 * tableAmt 6 17850 - fStat 6 17850 = 120000 ∧ fStat 6 49 - 10000 * tableAmt 6 49 = 96000 ∧
    10000 * tableAmt 3 17850 - fStat 3 17850 = 135000 ∧ fStat 3 49 - 10000 * tableAmt 3 49 = 110500 ∧
    10000 * tableAmt 7 17850 - fStat 7 17850 = 135000 ∧ fStat 7 49 - 10000 * tableAmt 7 49 = 110500 := by
  decide +kernel

/-- The printed table agrees with the existing model's reverse-engineered rule `D.eicTable` at both ends of every
band, in every column. -/
theorem printed_eq_model_rule : (List.range 8).all (fun c => (colBands c).all fun r =>
    r.2.2 == eicTable (kidsOf c) (jointOf c) r.1 && r.2.2 == eicTable (kidsOf c) (jointOf c) (r.2.1 - 1)) = true := by
  decide +kernel

/-! ## EIC Worksheet A, line by line -/

/-- Worksheet A—2025 EIC—Line 27a. Line 1: earned income; line 2: "Look up the amount on line 1 ... in the EIC
Table"; line 3: AGI (Form 1040 line 11b); line 4: "Are the amounts on lines 3 and 1 the same? Yes. Skip line 5; enter
the amount from line 2 on line 6"; line 5: "is the amount on line 3 less than $10,620 ($17,730 if married filing
jointly)" [no child] / "$23,350 ($30,470 ...)" [children]: "Yes. ... enter the amount from line 2 on line 6. No. Look
up the amount on line 3 ... enter the smaller amount on line 6". -/
def worksheetA (c : Nat) (earned agi : Int) : Int :=
  let l2 := tableAmt c earned
  if agi = earned then l2
  else if agi < thrOf c then l2
  else min l2 (tableAmt c agi)

/-- **Worksheet A against §32(a)–(b) for all earned income and AGI ≥ 0**: within the same per-column bounds as the
table (the lookup-twice-and-take-the-smaller rule is exactly the statute's "adjusted gross income (or, if greater,
the earned income)", `D.worksheet_rule_exact`). -/
theorem worksheetA_bounds (c : Nat) (hc : c < 8) (e a : Int) (he : 0 ≤ e) (ha : 0 ≤ a) :
    10000 * worksheetA c e a - eicScaled (P c).cp (P c).pp (P c).eia (thrOf c) e a ≤ overMax c ∧
    eicScaled (P c).cp (P c).pp (P c).eia (thrOf c) e a - 10000 * worksheetA c e a ≤ underMax c := by
  have hw : eicScaled (P c).cp (P c).pp (P c).eia (thrOf c) e a =
      if a < thrOf c then eicScaled (P c).cp (P c).pp (P c).eia (thrOf c) e e
      else min (eicScaled (P c).cp (P c).pp (P c).eia (thrOf c) e e)
        (eicScaled (P c).cp (P c).pp (P c).eia (thrOf c) a a) :=
    worksheet_rule_exact (kidsOf c) (jointOf c) e a
  have h1 := table_bounds c hc e he
  have h2 := table_bounds c hc a ha
  unfold fStat at h1 h2
  rw [hw]; unfold worksheetA
  by_cases hea : a = e
  · subst hea; simp only [↓reduceIte]; split <;> omega
  · simp only [hea, ↓reduceIte]; split <;> omega

/-! ## Step 2: investment income (§32(i)) -/

/-- Step 2, question 1: "Add the amounts from Form 1040: Line 2a + Line 2b + Line 3b + Line 7a* (*If line 7a is a
loss, enter -0-)"; question 2: "Is your investment income more than $11,950?" (Line 7a is the net capital gain or
the deductible loss, at most $3,000 — $1,500 if married filing separately.) -/
def investmentIncomeForm (l2a l2b l3b netCapital lossCap : Int) : Int :=
  l2a + l2b + l3b + max 0 (max netCapital (-lossCap))

/-- §32(i)(2)(A), (B), (D) for a filer with no rents, royalties or passive income (Pub. 596 Worksheet 1 covers those):
interest, tax-exempt interest, dividends, capital gain net income (§1222(9), gains over losses if positive). -/
def disqualifiedStat (taxable exempt divs netCapital : Int) : Int := taxable + exempt + divs + pos netCapital

theorem investment_income_eq (l2a l2b l3b n cap : Int) (hcap : 0 ≤ cap) :
    investmentIncomeForm l2a l2b l3b n cap = disqualifiedStat l2b l2a l3b n ∧
    (investmentIncomeForm l2a l2b l3b n cap > 11950 ↔ eicInvestmentLimit < disqualifiedStat l2b l2a l3b n) := by
  unfold investmentIncomeForm disqualifiedStat eicInvestmentLimit pos; omega

/-! ## Separated spouses (§32(d)(2)(B)) -/

/-- The facts that decide whether a married individual not filing jointly is "not treated as married". -/
structure SepFacts where
  married : Bool                 -- §7703(a)
  joint : Bool                   -- files a joint return
  childOverHalf : Bool           -- resides with a qualifying child for more than one-half of the year
  apartLast6 : Bool              -- no common principal place of abode during the last 6 months
  sepMaintenanceDecree : Bool    -- decree of separate maintenance (or written instrument incident to it)
  writtenSepAgreement : Bool     -- written separation agreement
  supportDecree : Bool           -- decree requiring support or maintenance payments (§121(d)(3)(C)(iii))
  legallySeparatedStateLaw : Bool
  sameHouseholdAtEnd : Bool
  deriving DecidableEq, Repr

/-- §32(d)(2)(B)(i)–(iii) with §121(d)(3)(C)(i)–(iii) (OLRC 119-138). -/
def sepStatute (f : SepFacts) : Bool :=
  f.married && !f.joint && f.childOverHalf &&
    (f.apartLast6 ||
      ((f.sepMaintenanceDecree || f.writtenSepAgreement || f.supportDecree) && !f.sameHouseholdAtEnd))

/-- 2025 Instructions for Form 1040, "Special rule for separated spouses" (and Pub. 596, Rule 3): "If you are
married, but not filing a joint return, had a qualifying child who lived with you ... for more than half of 2025,
and either of the following apply: You lived apart from your spouse for the last 6 months of 2025, or You are legally
separated according to your state law under a written separation agreement or a decree of separate maintenance and
you didn't live in the same household as your spouse at the end of 2025." -/
def sepForm (f : SepFacts) : Bool :=
  f.married && !f.joint && f.childOverHalf &&
    (f.apartLast6 ||
      (f.legallySeparatedStateLaw && (f.writtenSepAgreement || f.sepMaintenanceDecree) && !f.sameHouseholdAtEnd))

/-- **The instruction never admits anyone the statute excludes ...** -/
theorem sepForm_le (f : SepFacts) : sepForm f = true → sepStatute f = true := by
  obtain ⟨a, b, c, d, e, g, h, i, j⟩ := f
  cases a <;> cases b <;> cases c <;> cases d <;> cases e <;> cases g <;> cases h <;> cases i <;> cases j <;> decide

/-- **... and excludes exactly these filers**: married, not filing jointly, child more than half the year, sharing
an abode at some time in the last 6 months but not the same household at year end, holding a §121(d)(3)(C)
instrument, and EITHER not legally separated under state law OR holding only a support decree. -/
theorem sep_difference (f : SepFacts) :
    (sepStatute f = true ∧ sepForm f = false) ↔
      (f.married = true ∧ f.joint = false ∧ f.childOverHalf = true ∧ f.apartLast6 = false ∧
        f.sameHouseholdAtEnd = false ∧ (f.sepMaintenanceDecree || f.writtenSepAgreement || f.supportDecree) = true ∧
        (f.legallySeparatedStateLaw && (f.writtenSepAgreement || f.sepMaintenanceDecree)) = false) := by
  obtain ⟨a, b, c, d, e, g, h, i, j⟩ := f
  cases a <;> cases b <;> cases c <;> cases d <;> cases e <;> cases g <;> cases h <;> cases i <;> cases j <;> decide

/-- The excluded filer loses the whole credit: three children, $18,000 earned, written separation agreement, no
state-law legal separation — statute: the 3-child credit, $8,046 by Worksheet A; instruction: $0 (married filing
separately, §32(d)(1)). The loss is at most the 3-child maximum (`D.eicScaled_le_max`). -/
theorem sep_example :
    sepStatute ⟨true, false, true, false, false, true, false, false, false⟩ = true ∧
    sepForm ⟨true, false, true, false, false, true, false, false, false⟩ = false ∧
    worksheetA 3 18000 18000 = 8046 := by decide +kernel

end TaxCode.Forms.EIC

#print axioms TaxCode.Forms.EIC.table_bounds
#print axioms TaxCode.Forms.EIC.table_bounds_attained
#print axioms TaxCode.Forms.EIC.printed_eq_model_rule
#print axioms TaxCode.Forms.EIC.worksheetA_bounds
#print axioms TaxCode.Forms.EIC.investment_income_eq
#print axioms TaxCode.Forms.EIC.sep_difference
