import TaxCode.Individual.A.AGI

/-!
# Form 8960 (2025), individuals, against §1411

Form text: Form 8960 (2025) lines 1, 2, 5a–5d, 8, 12–17; 2025 Instructions for Form 8960, "Line 5a—Net Gain or Loss
From Disposition of Property" ("combining ... Form 1040 ... line 7a, and Schedule 1 ... line 4") and "Line 13—Modified
Adjusted Gross Income" ("increase your AGI by the excess of the amount excluded from income under section 911(a)(1)
over the amount of any deductions ... or exclusions disallowed under section 911(d)(6)").

Statute: §1411(a)(1), (b), (c)(1)(A)(i), (iii), (d), via `TaxCode.Individual.A.niit` (which has no §1411(d)
add-back; it is added here). Domain: interest, dividends, capital gains, no rents/royalties/passive income, no
deductions properly allocable (Part II lines 9–11 zero).

Line 13 follows §1411(d) exactly (Form 2555 line 42, the §911(a)(1) exclusion, not the housing amounts), unlike the
§24 and §36B add-backs on Schedule 8812 and Form 8962. The one difference is line 5a: Form 1040 line 7a may be a
capital LOSS (up to $3,000, $1,500 separately, §1211(b)), and the form carries it into line 8, while §1411(c)(1)(A)(iii)
counts "net gain" — never below zero.
-/

namespace TaxCode.Forms.Form8960
open TaxCode.Individual TaxCode.Individual.A

structure Inputs where
  filing : Filing
  interest : Int        -- line 1
  dividends : Int       -- line 2
  line7a : Int          -- Form 1040 line 7a: net capital gain, or the loss allowed (at least −$3,000 / −$1,500)
  agi : Int
  feie : Int := 0       -- Form 2555 line 42 (§911(a)(1))
  feieDisallowed : Int := 0  -- deductions/exclusions disallowed under §911(d)(6) for it
  deriving Repr

/-- Line 8 "Total investment income. Combine lines 1, 2, 3, 4c, 5d, 6, and 7" (5d = 5a here); line 12 = line 8 −
line 11 (= 0); line 13 MAGI; line 14 $250,000 / $125,000 / $200,000 ("Qualifying surviving spouse" with joint);
line 15 "If zero or less, enter -0-"; line 16 "smaller of line 12 or line 15"; line 17 "Multiply line 16 by 3.8%".
In tenths of a cent ×… : the tax ×1000. -/
def l17x (i : Inputs) : Int :=
  let l12 := i.interest + i.dividends + i.line7a
  let l13 := i.agi + (i.feie - i.feieDisallowed)
  let l14 := niitThreshold i.filing
  let l15 := max 0 (l13 - l14)
  38 * min l12 l15

/-- §1411(a)(1), (c)(1)(A)(iii) "net gain", (d): 3.8% of the lesser of net investment income and MAGI over the
threshold (×1000). -/
def statx (i : Inputs) : Int :=
  38 * min (max 0 (i.interest + i.dividends + max 0 i.line7a))
    (max 0 (i.agi + (i.feie - i.feieDisallowed) - niitThreshold i.filing))

/-- **Equal for all inputs without a capital loss** (interest and dividends ≥ 0). -/
theorem eq_no_loss (i : Inputs) (h : 0 ≤ i.line7a) (h1 : 0 ≤ i.interest) (h2 : 0 ≤ i.dividends) :
    l17x i = statx i := by
  unfold l17x statx; simp only; omega

/-- **With a capital loss L (−$3,000 ≤ line 7a < 0) the form's tax is lower, by at most 3.8% of L** — $114 at the
$3,000 limit ($57 separately) — and never higher. -/
theorem loss_effect (i : Inputs) (h : i.line7a < 0) (hl : -3000 ≤ i.line7a) (h1 : 0 ≤ i.interest)
    (h2 : 0 ≤ i.dividends) : l17x i ≤ statx i ∧ statx i - l17x i ≤ 38 * (-i.line7a) := by
  unfold l17x statx; simp only; omega

theorem loss_example :
    l17x ⟨.single, 0, 50000, -3000, 300000, 0, 0⟩ = 38 * 47000 ∧
    statx ⟨.single, 0, 50000, -3000, 300000, 0, 0⟩ = 38 * 50000 := by decide

/-- The model (`A.niit`, no §911) is the statute here with no foreign exclusion. -/
theorem statx_matches_model (h : Household) (agi : Int) (hi : 0 ≤ h.taxableInterest) :
    1000 * niit h agi - statx ⟨h.filing, h.taxableInterest, h.ordinaryDividends, h.shortTermGains + h.longTermGains,
      agi, 0, 0⟩ ≤ 500 ∧
    statx ⟨h.filing, h.taxableInterest, h.ordinaryDividends, h.shortTermGains + h.longTermGains, agi, 0, 0⟩
      - 1000 * niit h agi ≤ 500 := by
  unfold niit statx netInvestmentIncome roundDollar; simp only; omega

end TaxCode.Forms.Form8960

#print axioms TaxCode.Forms.Form8960.eq_no_loss
#print axioms TaxCode.Forms.Form8960.loss_effect
