import TaxCode.Individual.C.Table

/-!
# §1(h): the maximum capital gains rate, and the Qualified Dividends and Capital Gain Tax Worksheet

§1(h)(1): "If a taxpayer has a net capital gain …, the tax imposed by this section … shall not exceed the sum of" (A) the
ordinary tax on the ordinary part, (B) 0% of the gain up to a ceiling, (C) 15% of the next slice, (D) 20% of the rest,
(E) 25% of unrecaptured §1250 gain, (F) 28% of the remainder. §1(j)(5)(A) replaces the old bracket references in (B)(i)
and (C)(ii)(I) with "below the maximum zero rate amount" and "below the maximum 15-percent rate amount", whose 2025
values are Rev. Proc. 2024-40 §2.03 (p. 8). §1(h)(11): "net capital gain" includes qualified dividend income.

The household model has no 28-percent rate gain or unrecaptured §1250 gain, so adjusted net capital gain = net capital
gain = qualified dividends + net long-term gain (as limited by Schedule D lines 15/16), (A)(ii) collapses onto (A)(i),
and (E), (F) are zero. The input `qualDivAndLtcg` is that sum (Form 1040 line 3a plus Schedule D line 15/16 or
line 7a).

Both the statute (`regularCents`, exact cents) and the IRS worksheet (`regularTax`, whole dollars, with the Tax Table)
are modelled; `worksheet_lines_eq` shows the worksheet's 0%/15%/20% amounts are the statute's (B)/(C)/(D) amounts.
-/

namespace TaxCode.Individual.C
open TaxCode.Individual

/-- §1(j)(5)(B)(i) maximum zero rate amount, 2025 (Rev. Proc. 2024-40 §2.03): $96,700 joint/surviving spouse,
$64,750 head of household, $48,350 others (= ½ of the joint amount, §1(j)(5)(B)(i)(III)). -/
def maxZeroRate : Filing → Int
  | .mfj | .qss => 96700
  | .hoh => 64750
  | .single | .mfs => 48350

/-- §1(j)(5)(B)(ii) maximum 15-percent rate amount, 2025 (Rev. Proc. 2024-40 §2.03): $600,050 joint/surviving spouse,
$300,000 married filing separately, $566,700 head of household, $533,400 others. -/
def max15Rate : Filing → Int
  | .mfj | .qss => 600050
  | .mfs => 300000
  | .hoh => 566700
  | .single => 533400

/-- The amounts on which §1(h)(1)(A)–(D) determine tax, for taxable income `ti` and net capital gain `g`. -/
structure Split where
  ordinary : Int   -- (A): taxable income reduced by the net capital gain
  zero : Int       -- (B): taxed at 0%
  fifteen : Int    -- (C): taxed at 15%
  twenty : Int     -- (D): taxed at 20%
  deriving Repr, DecidableEq

/-- §1(h)(1)(A)–(D) with ANCG = NCG = `g` (floored at zero; gains above taxable income count only to taxable income:
"(or, if less, taxable income)"). -/
def split (f : Filing) (ti g : Int) : Split :=
  let g := max 0 g
  let ti := max 0 ti
  let a := max 0 (ti - g)                                   -- (A)(i): taxable income reduced by net capital gain
  let gain := min g ti                                      -- "adjusted net capital gain (or, if less, taxable income)"
  let b := min gain (max 0 (min ti (maxZeroRate f) - a))    -- (B): up to the excess of (B)(i) over (B)(ii)
  let c := min (gain - b) (max 0 (min ti (max15Rate f) - (a + b)))  -- (C): lesser of (C)(i) and (C)(ii)
  ⟨a, b, c, gain - b - c⟩                                   -- (D): the rest of the gain

/-- What `split` produces: the four amounts are non-negative, add up to taxable income, and are the statute's mins. -/
theorem split_facts (f : Filing) (ti g : Int) (ht : 0 ≤ ti) (hg : 0 ≤ g) :
    let s := split f ti g
    0 ≤ s.ordinary ∧ 0 ≤ s.zero ∧ 0 ≤ s.fifteen ∧ 0 ≤ s.twenty ∧
      s.ordinary + s.zero + s.fifteen + s.twenty = ti ∧ s.ordinary = max 0 (ti - g) ∧
      s.zero = min (ti - s.ordinary) (max 0 (min ti (maxZeroRate f) - s.ordinary)) ∧
      s.fifteen = min (ti - s.ordinary - s.zero) (max 0 (min ti (max15Rate f) - (s.ordinary + s.zero))) := by
  simp only [split]
  omega

/-- The §1(h)(1) sum in cents. -/
def capGainSumCents (f : Filing) (ti g : Int) : Int :=
  let s := split f ti g
  scheduleCents f s.ordinary + 15 * s.fifteen + 20 * s.twenty

/-- The tax imposed by §1 in cents: the schedule tax, which "shall not exceed" the §1(h)(1) sum when there is a net
capital gain. -/
def regularCents (f : Filing) (ti g : Int) : Int :=
  if 0 < g then min (scheduleCents f ti) (capGainSumCents f ti g) else scheduleCents f ti

/-! ## The worksheet (2025 Instructions for Form 1040, p. 37) -/

/-- The Qualified Dividends and Capital Gain Tax Worksheet—Line 16, line by line. `line1` = Form 1040 line 15
(taxable income); `line4` = lines 2 + 3 (qualified dividends plus the capital gain amount). -/
structure QDCG where
  l1 : Int
  l4 : Int
  l5 : Int
  l6 : Int
  l7 : Int
  l8 : Int
  l9 : Int
  l10 : Int
  l12 : Int
  l13 : Int
  l14 : Int
  l16 : Int
  l17 : Int
  l18 : Int
  l20 : Int
  l21 : Int
  l22 : Int
  l23 : Int
  l24 : Int
  l25 : Int
  deriving Repr

def qdcg (f : Filing) (ti g : Int) : QDCG :=
  let l1 := ti
  let l4 := g
  let l5 := max 0 (l1 - l4)                -- 5. Subtract line 4 from line 1. If zero or less, enter -0-
  let l6 := maxZeroRate f                  -- 6. $48,350 / $96,700 / $64,750
  let l7 := min l1 l6                      -- 7. smaller of line 1 or line 6
  let l8 := min l5 l7                      -- 8. smaller of line 5 or line 7
  let l9 := l7 - l8                        -- 9. Subtract line 8 from line 7. This amount is taxed at 0%
  let l10 := min l1 l4                     -- 10. smaller of line 1 or line 4
  let l12 := l10 - l9                      -- 11–12. line 10 minus line 9
  let l13 := max15Rate f                   -- 13. $533,400 / $300,000 / $600,050 / $566,700
  let l14 := min l1 l13                    -- 14. smaller of line 1 or line 13
  let l16 := max 0 (l14 - (l5 + l9))       -- 15–16. line 14 minus (line 5 + line 9), not below zero
  let l17 := min l12 l16                   -- 17. smaller of line 12 or line 16
  let l18 := roundDollar (15 * l17) 100    -- 18. line 17 × 15% (rounded to whole dollars)
  let l20 := l10 - (l9 + l17)              -- 19–20. line 10 minus (line 9 + line 17)
  let l21 := roundDollar (20 * l20) 100    -- 21. line 20 × 20%
  let l22 := line16Tax f l5                -- 22. tax on line 5 (Tax Table under $100,000, else worksheet)
  let l23 := l18 + l21 + l22               -- 23. lines 18 + 21 + 22
  let l24 := line16Tax f l1                -- 24. tax on line 1
  ⟨l1, l4, l5, l6, l7, l8, l9, l10, l12, l13, l14, l16, l17, l18, l20, l21, l22, l23, l24, min l23 l24⟩

/-- **Regular tax (Form 1040 line 16)** for taxable income `ti` with `qualDivAndLtcg` of qualified dividends and net
capital gain: the worksheet's line 25 when there is any, otherwise the Tax Table / Tax Computation Worksheet. -/
def regularTax (f : Filing) (ti qualDivAndLtcg : Int) : Int :=
  if 0 < qualDivAndLtcg then (qdcg f ti qualDivAndLtcg).l25 else line16Tax f ti

/-- **The worksheet computes the statute's amounts.** For non-negative inputs, worksheet line 5 is §1(h)(1)(A)'s
amount, line 9 is (B)'s, line 17 is (C)'s and line 20 is (D)'s. -/
theorem worksheet_lines_eq (f : Filing) (ti g : Int) (ht : 0 ≤ ti) (hg : 0 ≤ g) :
    let w := qdcg f ti g
    let s := split f ti g
    w.l5 = s.ordinary ∧ w.l9 = s.zero ∧ w.l17 = s.fifteen ∧ w.l20 = s.twenty := by
  have hz : 0 < maxZeroRate f := by cases f <;> decide
  have h15 : maxZeroRate f ≤ max15Rate f := by cases f <;> decide
  simp only [qdcg, split]
  omega

/-! ## Tests -/

-- Worked values computed through the worksheet; the inputs reproduce the 2025 thresholds printed on worksheet lines
-- 6 and 13 (p. 37). No IRS worked example of this worksheet is printed in the 2025 Form 1040 instructions.
/-- All gain, all inside the 0% band: a single filer with $48,350 of qualified dividends and nothing else pays $0. -/
theorem zero_band_single : regularTax .single 48350 48350 = 0 := by decide
/-- One dollar more is taxed at 15% (rounded: $0). The 15% band for a single filer ends at $533,400 (line 13). -/
theorem fifteen_band_single : (split .single 533400 533400).fifteen = 533400 - 48350 ∧
    (split .single 533401 533401).twenty = 1 := by decide
/-- Joint filers: $96,700 of qualified dividends on top of nothing are taxed at 0%, the next dollar at 15%. -/
theorem zero_band_mfj : (split .mfj 96700 96700).zero = 96700 ∧ (split .mfj 96701 96701).fifteen = 1 := by decide
/-- With $60,000 of wages after deductions and $10,000 of qualified dividends, a single filer pays 15% on the
dividends and the ordinary method on the rest: the Tax Table line $50,000–$50,050 gives $5,920 (2025 Tax Table p. 74),
plus 15% of $10,000. -/
theorem mixed_single : regularTax .single 60000 10000 = 5920 + 1500 := by decide

/-! ## Properties -/

/-- **§1(h) never raises the tax** (by the statute's own words "shall not exceed"): the statutory tax with gains is at
most the schedule tax on the same taxable income; likewise the worksheet result is at most Form 1040 line 16's
ordinary method. -/
theorem regularCents_le (f : Filing) (ti g : Int) : regularCents f ti g ≤ scheduleCents f ti := by
  unfold regularCents; split <;> omega

theorem regularTax_le (f : Filing) (ti g : Int) : regularTax f ti g ≤ line16Tax f ti := by
  unfold regularTax
  split
  · simp only [qdcg]
    exact Int.min_le_right _ _
  · exact Int.le_refl _

/-- **But the §1(h)(1) sum on its own can exceed the ordinary tax.** The 0% ceiling ($48,350 single) sits $125 below
the top of the 12% bracket ($48,475), so gain in that strip is charged 15% by (C) where ordinary income pays 12%. A
single filer with $48,350 of ordinary income and $125 of qualified dividends: the sum is $3.75 above the schedule tax. -/
theorem capGainSum_exceeds :
    capGainSumCents .single 48475 125 - scheduleCents .single 48475 = 375 ∧
      capGainSumCents .mfj 96950 250 - scheduleCents .mfj 96950 = 750 ∧
      capGainSumCents .hoh 64850 100 - scheduleCents .hoh 64850 = 300 ∧
      capGainSumCents .mfs 48475 125 - scheduleCents .mfs 48475 = 375 := by decide

/-- **…and that is the most it can exceed it**: 3% of the strip between the 0% ceiling and the top of the 12% bracket
($3.75 single and separate, $7.50 joint, $3.00 head of household), for every taxable income and every gain. -/
theorem capGainSum_excess_max (f : Filing) (ti g : Int) (ht : 0 ≤ ti) (hg : 0 ≤ g) :
    capGainSumCents f ti g - scheduleCents f ti ≤ 3 * ((sched f).e2 - maxZeroRate f) := by
  have F := split_facts f ti g ht hg
  unfold capGainSumCents
  generalize split f ti g = s at *
  obtain ⟨a, b, c, d⟩ := s
  simp only at *
  cases f <;>
  · simp only [scheduleCents, sched, Sched.cents, maxZeroRate, max15Rate,
      single2025, mfj2025, mfs2025, hoh2025] at *
    repeat' split
    all_goals omega

/-- **Reclassifying ordinary income as qualified dividends can raise the tax.** Single, $60,000 taxable income: with
$11,600 of qualified dividends the ordinary part is $48,400 (inside the strip); one more dollar of dividends (one less of
wages) moves a dollar from the 12% bracket to the 15% rate, and the statutory tax rises by 3 cents. -/
theorem more_dividends_more_tax :
    regularCents .single 60000 11601 = regularCents .single 60000 11600 + 3 := by decide

/-! ## Statute vs worksheet -/

theorem line16Tax_near (f : Filing) (ti : Int) (h0 : 0 ≤ ti) :
    line16Tax f ti - scheduleTax f ti ≤ 6 ∧ scheduleTax f ti - line16Tax f ti ≤ 5 := by
  unfold line16Tax
  split
  · exact ⟨(table_within_6 f ti h0 (by omega)).1, table_ge_minus5 f ti h0 (by omega)⟩
  · omega

/-- **The worksheet is within $7 of the statute** (rounded to whole dollars) for every taxable income and gain:
the Tax Table's −$5…+$6 on lines 22 and 24 plus half-dollar roundings on lines 18 and 21. -/
theorem qdcg_l25 (f : Filing) (ti g : Int) (ht : 0 ≤ ti) (hg : 0 ≤ g) :
    (qdcg f ti g).l25 =
      min (roundDollar (15 * (split f ti g).fifteen) 100 + roundDollar (20 * (split f ti g).twenty) 100 +
        line16Tax f (split f ti g).ordinary) (line16Tax f ti) := by
  have hw := worksheet_lines_eq f ti g ht hg
  simp only at hw
  obtain ⟨e5, _, e17, e20⟩ := hw
  rw [← e5, ← e17, ← e20]
  rfl

theorem regularTax_near (f : Filing) (ti g : Int) (ht : 0 ≤ ti) (hg : 0 ≤ g) :
    regularTax f ti g - roundDollar (regularCents f ti g) 100 ≤ 7 ∧
      roundDollar (regularCents f ti g) 100 - regularTax f ti g ≤ 7 := by
  have F := split_facts f ti g ht hg
  simp only at F
  have h1 := line16Tax_near f ti ht
  have h5 := line16Tax_near f (split f ti g).ordinary F.1
  unfold regularTax regularCents
  split
  · rw [qdcg_l25 f ti g ht hg]
    simp only [capGainSumCents]
    unfold scheduleTax roundDollar at *
    omega
  · unfold scheduleTax at h1
    omega

end TaxCode.Individual.C
