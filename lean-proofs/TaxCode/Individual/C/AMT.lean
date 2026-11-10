import TaxCode.Individual.C.CapitalGains

/-!
# §§55–59: the alternative minimum tax for individuals, tax year 2025

§55(a): the AMT is "the excess (if any) of (1) the tentative minimum tax … over (2) the regular tax".
§55(b)(1)(A): tentative minimum tax = 26% of the taxable excess up to $175,000 (indexed: $239,100 for 2025, $119,550
married filing separately, §55(b)(1)(C)) plus 28% above. §55(b)(1)(B): taxable excess = AMTI over the exemption amount.
§55(b)(1)(D): AMTI = taxable income with the §56/§58 adjustments plus §57 preferences.
§55(d)(1) as modified by (d)(4)(A)(i) and indexed: exemption $137,000 joint/surviving spouse, $88,100 unmarried,
$68,500 married filing separately. §55(d)(2) and (d)(4)(A)(ii): reduced by **25%** of AMTI over $1,252,700 (joint) or
$626,350 (others). All 2025 amounts: Rev. Proc. 2024-40 §2.11 (pp. 10–11).

**Which phase-out rate applies to 2025.** The OLRC text (release point 119-138) of §55(d)(4)(A)(ii)(IV) reads "by
substituting '50 percent' for '25 percent'", and (d)(4)(B) indexes the $1,000,000 for years after 2025; but Pub. L. 119-21
§70107(d) applies those amendments "to taxable years beginning after December 31, 2025". For 2025 the rate is 25% and
the thresholds are the old indexed ones (FINDINGS.md, F7). The 2025 Instructions for Form 6251 agree (Exemption
Worksheet line 5: "Multiply line 4 by 25% (0.25)").

**Adjustments modelled** (the ones the household model supports): §56(b)(1)(A)(ii) no deduction for state and local
taxes (Form 6251 line 2a: Schedule A line 7); §56(b)(1)(D) no standard deduction (line 2a, non-itemizers) and no
deduction under §151 — which includes the 2025 Act's §151(d)(5)(C) senior deduction (Form 6251 line 1b starts from taxable
income before Schedule 1-A line 37). Not modelled: everything else in §§56–58 (ISOs, depreciation, private-activity
bond interest, NOLs, the AMT foreign tax credit, §53 credit).

**Units.** Exact: AMTI-derived amounts are kept in sixteenths of a dollar (the 25% phase-out of a 25%-based MFS
add-back stays exact), tentative minimum tax in 1/1600 dollar (rate in percent × sixteenths); the final figure is
rounded half up to whole dollars.
-/

namespace TaxCode.Individual.C
open TaxCode.Individual

/-- §55(d)(1)(A)–(C) exemption amount, 2025 (Rev. Proc. 2024-40 §2.11). -/
def amtExemption : Filing → Int
  | .mfj | .qss => 137000
  | .mfs => 68500
  | .single | .hoh => 88100

/-- §55(d)(2) threshold at which the exemption starts to phase out, 2025 (Rev. Proc. 2024-40 §2.11 "Threshold Phaseout
Amount"): $1,252,700 joint/surviving spouse; $626,350 unmarried and married filing separately. -/
def amtThreshold : Filing → Int
  | .mfj | .qss => 1252700
  | .mfs | .single | .hoh => 626350

/-- §55(b)(1)(A)/(C): the taxable excess above which 28% applies, 2025 (Rev. Proc. 2024-40 §2.11). -/
def amtBreak : Filing → Int
  | .mfs => 119550
  | _ => 239100

/-- The AMTI at which the exemption reaches zero ("the minimum amount of such income … for which the exemption amount
… is zero", §55(d)(2) last sentence): threshold + exemption ÷ 25%. -/
def amtZeroPoint (f : Filing) : Int := amtThreshold f + 4 * amtExemption f

/-- §55(b)(1)(D), §56(b)(1)(A)(ii), §56(b)(1)(D): AMTI in whole dollars, before the MFS add-back. `saltDeducted` is
the state and local tax actually deducted on Schedule A (zero for non-itemizers); `stdDeduction` the standard
deduction claimed (zero for itemizers); `seniorDeduction` the §151(d)(5)(C) senior deduction (Schedule 1-A line 37). -/
def amtiBase (taxableIncome saltDeducted stdDeduction seniorDeduction : Int) : Int :=
  taxableIncome + saltDeducted + stdDeduction + seniorDeduction

/-- §55(d)(2) last sentence, married filing separately: AMTI "shall be increased by the lesser of (i) 25 percent of the
excess of [AMTI] over the minimum amount … for which the exemption amount … is zero, or (ii) such exemption amount".
In sixteenths. -/
def mfsAddBackQ (f : Filing) (amti : Int) : Int :=
  if f = .mfs then min (4 * max 0 (amti - amtZeroPoint f)) (16 * amtExemption f) else 0

/-- AMTI in sixteenths of a dollar, after the MFS add-back. -/
def amtiQ (f : Filing) (amti : Int) : Int := 16 * amti + mfsAddBackQ f amti

/-- §55(d)(1)–(2): the exemption "reduced (but not below zero) by … 25 percent of the amount by which the [AMTI]
exceeds" the threshold. In sixteenths. -/
def exemptionQ (f : Filing) (aQ : Int) : Int :=
  max 0 (16 * amtExemption f - max 0 (aQ - 16 * amtThreshold f) / 4)

/-- §55(b)(1)(B): taxable excess = AMTI over the exemption. In sixteenths. -/
def taxableExcessQ (f : Filing) (amti : Int) : Int :=
  let a := amtiQ f amti
  max 0 (a - exemptionQ f a)

/-- §55(b)(1)(A): 26% up to the break, 28% above, on an amount in sixteenths; result in 1/1600 dollar. -/
def rate2628 (f : Filing) (xQ : Int) : Int :=
  26 * min xQ (16 * amtBreak f) + 28 * max 0 (xQ - 16 * amtBreak f)

/-- §55(b)(3): with net capital gain `g` (= adjusted net capital gain; no unrecaptured §1250 gain), the first-sentence
amount "shall not exceed" (A) the 26/28% tax on the taxable excess reduced by the gain, plus (B) 0% of the gain up to
"the excess described in section 1(h)(1)(B)", (C) 15% up to "the excess described in section 1(h)(1)(C)(ii)", (D)
20% of the rest. (E) (25% of the remaining taxable excess) is zero here. The (B) and (C)(ii) excesses are the
*regular-tax* ones, computed from taxable income `ti`, not from the taxable excess. Since §55(b)(3)(B) points at
"the excess described in section 1(h)(1)(B)", it must be the same number `split` uses for the regular tax, where
"taxable income reduced by the adjusted net capital gain" is floored at zero (`s.ordinary`); 2025 Form 6251 line 20
likewise takes line 5 of the Qualified Dividends and Capital Gain Tax Worksheet ("If zero or less, enter -0-").
(Review fix: this used the unfloored `ti - g`, which put all of a gain exceeding taxable income in the 0% band.) -/
def tmtCapGainQ (f : Filing) (teQ ti g : Int) : Int :=
  let s := split f ti g
  let gainQ := min (16 * max 0 g) teQ                       -- "adjusted net capital gain (or, if less, taxable excess)"
  let aQ := teQ - gainQ                                       -- (A): taxable excess reduced by the net capital gain
  let exB := max 0 (min ti (maxZeroRate f) - s.ordinary)      -- §1(h)(1)(B): (B)(i) over (B)(ii), as in `split`
  let bQ := min gainQ (16 * exB)
  let exC := max 0 (min ti (max15Rate f) - (s.ordinary + s.zero))  -- §1(h)(1)(C)(ii)
  let cQ := min (gainQ - bQ) (16 * exC)
  let dQ := gainQ - bQ - cQ
  rate2628 f aQ + 15 * cQ + 20 * dQ

/-- Tentative minimum tax in 1/1600 dollar (§55(b)(1)(A) first sentence, capped by §55(b)(3) if there is a gain). -/
def tmtQ (f : Filing) (amti ti g : Int) : Int :=
  let te := taxableExcessQ f amti
  if 0 < g then min (rate2628 f te) (tmtCapGainQ f te ti g) else rate2628 f te

/-- Tentative minimum tax in whole dollars (rounded half up). -/
def tentativeMinimumTax (f : Filing) (amti ti g : Int) : Int := roundDollar (tmtQ f amti ti g) 1600

/-- **§55(a) AMT** for a household: `taxableIncome` (Form 1040 line 15), the add-backs the household model has
(`saltDeducted`, `stdDeduction`, `seniorDeduction`), `qualDivAndLtcg` (for §55(b)(3)) and the `regularTax` it is
compared with (§55(c): regular tax liability; pass `regularTax f ti g` from `CapitalGains`). AGI is not needed: no
2025 AMT rule for individuals reads it once the SALT deduction (whose cap depends on MAGI) is given. -/
def amt (f : Filing) (taxableIncome saltDeducted stdDeduction seniorDeduction qualDivAndLtcg regularTax : Int) : Int :=
  let amti := amtiBase taxableIncome saltDeducted stdDeduction seniorDeduction
  max 0 (tentativeMinimumTax f amti taxableIncome qualDivAndLtcg - regularTax)

/-- The household-level entry point: regular tax from §1(h)/the worksheet, AMT on top. -/
def amtForReturn (f : Filing) (taxableIncome saltDeducted stdDeduction seniorDeduction qualDivAndLtcg : Int) : Int :=
  amt f taxableIncome saltDeducted stdDeduction seniorDeduction qualDivAndLtcg
    (regularTax f taxableIncome qualDivAndLtcg)

/-! ## Tests: Rev. Proc. 2024-40 §2.11 and the 2025 Instructions for Form 6251 -/

/-- Rev. Proc. 2024-40 §2.11 "Complete Phaseout Amount": $1,800,700 joint, $978,750 unmarried, $900,350 separate —
each is threshold + 4 × exemption (25% phase-out). The 2025 Form 6251 Exemption Worksheet repeats them. -/
theorem zero_points : amtZeroPoint .mfj = 1800700 ∧ amtZeroPoint .single = 978750 ∧ amtZeroPoint .hoh = 978750 ∧
    amtZeroPoint .mfs = 900350 := by decide

/-- Form 6251 instructions (2025), line 4: married filing separately with line 4 of $920,350 "becomes $925,350"; at
$1,174,350 or more the add-back is the full $68,500. -/
theorem mfs_addback_example : amtiQ .mfs 920350 = 16 * 925350 ∧ amtiQ .mfs 1174350 = 16 * (1174350 + 68500) ∧
    amtiQ .mfs 2000000 = 16 * (2000000 + 68500) := by decide

/-- Form 6251 instructions (2025), line 7: above $239,100 "multiply line 3 by 28% (0.28) and subtract $4,782 ($2,391 if
married filing separately)". -/
theorem line7_shortcut (f : Filing) (x : Int) (h : 16 * amtBreak f ≤ x) :
    rate2628 f x = 28 * x - 1600 * (if f = .mfs then 2391 else 4782) := by
  cases f <;> simp only [rate2628, amtBreak, reduceCtorEq, ↓reduceIte] at h ⊢ <;> omega

/-- Exemption Worksheet (2025 Form 6251 instructions): single, AMTI $700,000 → exemption $88,100 − 25% × $73,650 =
$69,687.50; taxable excess $630,312.50; TMT = 28% × that − $4,782 = $171,705.50 → $171,706. -/
theorem exemption_worksheet_example :
    exemptionQ .single (16 * 700000) = 16 * 69687 + 8 ∧ tentativeMinimumTax .single 700000 700000 0 = 171706 := by
  decide

/-! ## Marginal rates of the tentative minimum tax -/

/-- Tentative minimum tax on ordinary AMTI (no capital gain), in 1/1600 dollar. -/
def tmtOrdQ (f : Filing) (amti : Int) : Int := rate2628 f (taxableExcessQ f amti)

/-- **Every marginal AMT rate in 2025 is 0%, 26%, 28% or 35%** (416, 448, 560 in 1/1600 dollar per dollar), for every
filing status and every AMTI. In particular the 2025 phase-out (25%) only ever overlaps the 28% band — the 26% band ends
($327,200 single, $376,100 joint, $188,050 separate) long before the phase-out starts — so 26% × 1.25 = 32.5% never
occurs, and the maximum is 28% × 1.25 = 35%. -/
theorem tmt_marginal (f : Filing) (x : Int) (hx : 0 ≤ x) :
    let d := tmtOrdQ f (x + 1) - tmtOrdQ f x
    d = 0 ∨ d = 416 ∨ d = 448 ∨ d = 560 := by
  cases f <;>
  · simp only [tmtOrdQ, rate2628, taxableExcessQ, amtiQ, mfsAddBackQ, exemptionQ, amtZeroPoint, amtExemption,
      amtThreshold, amtBreak]
    simp
    omega

/-- The 35% is reached (single, AMTI $700,000, inside the phase-out). -/
theorem tmt_35_single : tmtOrdQ .single 700001 - tmtOrdQ .single 700000 = 560 := by decide

/-- …and for married filing separately it continues past the zero point through the add-back (AMTI $1,000,000). -/
theorem tmt_35_mfs_addback : tmtOrdQ .mfs 1000001 - tmtOrdQ .mfs 1000000 = 560 ∧
    tmtOrdQ .mfs 1174351 - tmtOrdQ .mfs 1174350 = 448 := by decide

/-! ## Where the AMT cannot bite -/

/-- The largest add-back (SALT + standard deduction + senior deduction) for which no taxable income at all produces
an AMT, per status (computed: the regular tax at the top of the 24% bracket against the TMT there). -/
def amtSafeAddBack : Filing → Int
  | .single => 45411
  | .hoh => 38723
  | .mfj | .qss => 46614
  | .mfs => 23307

theorem tableTax_nonneg (f : Filing) (ti : Int) : 0 ≤ tableTax f ti := by
  have hok := Sched.dbl_ok _ (sched_ok f)
  have : 0 ≤ midpoint2 ti := by unfold midpoint2; repeat' split <;> omega
  have := (Sched.lipschitz _ hok 0 (midpoint2 ti) (Int.le_refl _) this).1
  have h0 : (sched f).dbl.cents 0 = 0 := by simp [Sched.cents]
  unfold tableTax roundDollar
  omega

/-- The exact comparison behind `amt_unreachable`: below the safe add-back, the TMT never exceeds the schedule tax,
and under $100,000 it is either zero or at least $11 below it. -/
theorem tmt_le_schedule (f : Filing) (ti A : Int) (ht : 0 ≤ ti) (hA : 0 ≤ A) (hA' : A ≤ amtSafeAddBack f) :
    tmtOrdQ f (ti + A) ≤ 16 * scheduleCents f ti ∧
      (ti < 100000 → tmtOrdQ f (ti + A) = 0 ∨ tmtOrdQ f (ti + A) + 17600 ≤ 16 * scheduleCents f ti) := by
  cases f <;>
  · simp only [tmtOrdQ, rate2628, taxableExcessQ, amtiQ, mfsAddBackQ, exemptionQ, amtZeroPoint, amtExemption,
      amtThreshold, amtBreak, amtSafeAddBack, scheduleCents, sched, Sched.cents,
      single2025, mfj2025, mfs2025, hoh2025] at *
    simp only [reduceCtorEq, if_false, if_true, Int.add_zero] at *
    repeat' split
    all_goals omega

/-- **The AMT is mechanically unreachable for the household model's add-backs below the safe amount**: for every
taxable income, with no capital gain and SALT + standard + senior add-backs of at most $45,411 (single), $38,723 (head
of household), $46,614 (joint) or $23,307 (separate), the AMT is zero. -/
theorem amt_unreachable (f : Filing) (ti salt std senior : Int) (ht : 0 ≤ ti) (h1 : 0 ≤ salt) (h2 : 0 ≤ std)
    (h3 : 0 ≤ senior) (hA : salt + std + senior ≤ amtSafeAddBack f) :
    amtForReturn f ti salt std senior 0 = 0 := by
  have key := tmt_le_schedule f ti (salt + std + senior) ht (by omega) hA
  have hreg : regularTax f ti 0 = line16Tax f ti := by simp [regularTax]
  have hamti : amtiBase ti salt std senior = ti + (salt + std + senior) := by unfold amtiBase; omega
  have htmt : tmtQ f (ti + (salt + std + senior)) ti 0 = tmtOrdQ f (ti + (salt + std + senior)) := by
    simp [tmtQ, tmtOrdQ]
  unfold amtForReturn amt tentativeMinimumTax
  simp only
  rw [hreg, hamti, htmt]
  have hnn := tableTax_nonneg f ti
  unfold line16Tax
  split
  · rename_i hlt
    have hn := line16Tax_near f ti ht
    unfold line16Tax at hn
    rw [if_pos hlt] at hn
    rcases key.2 hlt with h0 | h0
    · rw [h0]; unfold roundDollar; omega
    · unfold scheduleTax roundDollar at *; omega
  · unfold scheduleTax roundDollar
    have := key.1
    omega

/-- **Corollaries.** (i) A non-itemizer's add-back is the standard deduction plus at most $6,000 per spouse of senior
deduction; that is always below the safe amount (single $15,750 + $6,000 = $21,750; joint $31,500 + $12,000 = $43,500;
head of household $23,625 + $6,000 = $29,625; separate filers cannot take the senior deduction), so **a household that
takes the standard deduction and has no other preference never owes AMT**. (ii) An itemizer's SALT deduction is capped
at $40,000 ($20,000 separate) for 2025 (§164(b)(6)–(7)): below the safe amount for single, joint and
separate filers. -/
theorem standard_deduction_no_amt :
    15750 + 6000 ≤ amtSafeAddBack .single ∧ 31500 + 12000 ≤ amtSafeAddBack .mfj ∧
      31500 + 12000 ≤ amtSafeAddBack .qss ∧ 23625 + 6000 ≤ amtSafeAddBack .hoh ∧
      15750 ≤ amtSafeAddBack .mfs ∧
      40000 ≤ amtSafeAddBack .single ∧ 40000 ≤ amtSafeAddBack .mfj ∧ 20000 ≤ amtSafeAddBack .mfs := by decide

/-- **But a head of household who itemizes can owe AMT on the SALT add-back alone**: $40,000 > $38,723. At taxable
income $197,300 (top of the 24% bracket) with $40,000 of SALT deducted, AMT is $332. -/
theorem hoh_salt_amt : amtForReturn .hoh 197300 40000 0 0 0 = 332 := by decide

/-- The safe amounts are tight (to within rounding): a few dollars more and the AMT appears at the top of the 24%
bracket. -/
theorem safe_tight :
    0 < amtForReturn .single 197300 45414 0 0 0 ∧ 0 < amtForReturn .mfj 394600 46617 0 0 0 ∧
      0 < amtForReturn .hoh 197300 38726 0 0 0 ∧ 0 < amtForReturn .mfs 197300 23310 0 0 0 := by decide

/-- A single itemizer aged 65+ can reach the AMT with SALT plus the senior deduction ($40,000 + $6,000 > $45,411) only
where the senior deduction survives its phase-out (MAGI under $175,000); at taxable income $160,000, AMT is $0, so the
corner is real but narrow: e.g. at $197,300 with the full $6,000 (not available at that MAGI) it would be $153. -/
theorem single_senior_corner : amtForReturn .single 160000 40000 0 6000 0 = 0 ∧
    amtForReturn .single 197300 40000 0 6000 0 = 153 := by decide

/-! ## Capital gains inside the AMT -/

/-- §55(b)(3) keeps the 0/15/20% rates: with gain, the TMT is never more than without the gain cap. -/
theorem tmt_capgain_le (f : Filing) (amti ti g : Int) : tmtQ f amti ti g ≤ tmtOrdQ f amti := by
  unfold tmtQ tmtOrdQ
  simp only
  split <;> omega

/-- In the exemption phase-out, a dollar of long-term gain taxed at 20% also removes 25 cents of exemption, taxed at
28%: the TMT marginal rate on that gain is 27% (single, taxable income $700,000 of which $100,000 gain, $10,000 SALT). -/
theorem gain_rate_in_phaseout :
    tmtQ .single 710001 700001 100001 - tmtQ .single 710000 700000 100000 = 16 * 27 := by decide

/-- (Review.) **`amt_unreachable` needs its "no capital gain" hypothesis**: a single filer who takes the standard
deduction, with $197,300 of ordinary taxable income and $1,000,000 of long-term gain, owes $15,194 of AMT (and $11,099
even with no add-back at all): the gain pushes AMTI past the $978,750 zero point, so the ordinary part loses the whole
exemption and is taxed at 28% instead of the regular 10–24%. -/
theorem gains_amt_reachable :
    amtForReturn .single 1197300 0 15750 0 1000000 = 15194 ∧ amtForReturn .single 1197300 0 0 0 1000000 = 11099 := by
  decide

/-- (Review.) Gain larger than taxable income: the 0% band in §55(b)(3)(B) is the regular-tax one ($48,350 single),
not taxable income plus the excess gain. Taxable income $100,000, gain $200,000, AMTI $140,000: taxable excess $51,900,
of which $48,350 at 0% and $3,550 at 15% = $532.50 (in 1/1600 dollar). -/
theorem tmt_gain_over_ti : tmtQ .single 140000 100000 200000 = 1600 * 53250 / 100 := by decide

end TaxCode.Individual.C
