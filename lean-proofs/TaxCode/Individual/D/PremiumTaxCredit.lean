import TaxCode.Individual.D.Basic

/-!
# §36B Premium tax credit, tax year 2025 (and the 2026 rule)

Source: 26 U.S.C. §36B (OLRC 119-138).

**2025.** §36B(b)(3)(A)(iii) ("Temporary percentages for 2021 through 2025", Pub. L. 117-2 §9661 as extended by Pub.
L. 117-169 §12001): for taxable years beginning before January 1, 2026 the applicable percentage table is
"Up to 150.0 percent 0.0 0.0; 150.0–200.0: 0.0 → 2.0; 200.0–250.0: 2.0 → 4.0; 250.0–300.0: 4.0 → 6.0; 300.0–400.0:
6.0 → 8.5; 400.0 percent and higher 8.5 8.5", sliding "on a sliding scale in a linear manner", and §36B(c)(1)(E)
applies §36B(c)(1)(A) "without regard to 'but does not exceed 400 percent'". Household income is compared with the
poverty line "most recently published ... as of the 1st day of the regular enrollment period" (§36B(d)(3)(B)): for
2025 coverage, the 2024 guidelines (Form 8962 instructions (2025) Table 1-1: $15,060 for one person, $5,380 for each
additional person, 48 states and D.C.).

The excess-advance-payment cap of §36B(f)(2)(B) still applies for 2025 (Pub. L. 119-21 §71305 removes it for
taxable years beginning after December 31, 2025); its 2025 amounts are in Rev. Proc. 2024-40 §3.07.

**2026.** The temporary table and (c)(1)(E) lapse: §36B(b)(3)(A)(i)'s table as indexed by Rev. Proc. 2025-25 §3.01
("Less than 133% 2.10% 2.10%; ... 133%–150% 3.14% 4.19%; 150%–200% 4.19% 6.60%; 200%–250% 6.60% 8.44%; 250%–300%
8.44% 9.96%; 300%–400% 9.96% 9.96%"), and eligibility again stops at 400% of the poverty line.

The credit is modelled on an annual basis (Form 8962 line 11: the same plan and benchmark all year; the
monthly sum of §36B(b)(1) then equals the annual figure up to rounding). `B` is the annual benchmark (second
lowest cost silver plan) premium, `P` the annual premium of the plan enrolled in, `F` the poverty line, `h`
household income (§36B(d)(2): MAGI of the taxpayer and of dependents required to file).
-/

namespace TaxCode.Individual.D
open TaxCode.Individual

/-- Form 8962 instructions (2025), Table 1-1: 2024 poverty guidelines, 48 contiguous states and D.C. -/
def fpl2024 (familySize : Nat) : Int := 15060 + 5380 * ((familySize : Int) - 1)

/-! ## 2025: the statute -/

/-- The 2025 applicable percentage, in basis points, multiplied by `F`. The temporary table is one line of slope
4 percentage points per 100% of the poverty line from 150% to 300% (0 → 2 → 4 → 6), then 2.5 points per 100% to
8.5% at 400%, flat after that. As a function of `h`: `max 0 (min (400h − 600F) (250h − 150F) (850F))`. -/
def ptcRate2025 (F h : Int) : Int := max 0 (min (400 * h - 600 * F) (min (250 * h - 150 * F) (850 * F)))

/-- The required contribution `h × rate`, in units of 1/(10000·F) dollar. -/
def ptcContribScaled (F h : Int) : Int := h * ptcRate2025 F h

/-- §36B(b)(2): "the lesser of (A) the monthly premiums ... or (B) the excess (if any) of (i) the adjusted monthly
premium for ... the applicable second lowest cost silver plan ... over (ii) ... the applicable percentage and the
taxpayer's household income" — exactly, in units of 1/(10000·F) dollar, for an applicable taxpayer. -/
def ptcScaled (F B P h : Int) : Int := min (P * (10000 * F)) (pos (B * (10000 * F) - ptcContribScaled F h))

/-- The 2025 credit in whole dollars. §36B(c)(1)(A): an applicable taxpayer's household income "equals or exceeds
100 percent" of the poverty line; (c)(1)(E): no upper limit in 2025. -/
def ptcStatute2025 (F B P h : Int) : Int :=
  if h < F then 0 else min P (pos (B - roundDollar (ptcContribScaled F h) (10000 * F)))

/-! ## 2025: Form 8962 -/

/-- Form 8962 Worksheet 2: household income as a percentage of the poverty line, "drop any numbers after the decimal
point"; "401" if more than 400%. -/
def ptcLine5 (F h : Int) : Int := if 4 * F < h then 401 else 100 * h / F

/-- Form 8962 Table 2 (2025), "Applicable Figure", in basis points: 150 or less 0.0000; then 0.0004 per point to
0.0600 at 300; then 0.0025 per point, rounded to four places (half up), to 0.0850 at 400 or more. -/
def ptcFigure (p : Int) : Int :=
  if p ≤ 150 then 0 else if p ≤ 300 then 4 * (p - 150) else if p < 400 then (1200 + 5 * (p - 300) + 1) / 2 else 850

/-- Form 8962 lines 5–8a and 11 (annual): contribution = household income × applicable figure, "rounded to the
nearest whole dollar"; credit = smaller of the premium and benchmark minus contribution. -/
def ptcForm2025 (F B P h : Int) : Int :=
  if h < F then 0 else min P (pos (B - roundDollar (h * ptcFigure (ptcLine5 F h)) 10000))

/-- Form 8962 (2025), Table 2, transcribed from the instructions: pairs "line 5 percentage, applicable figure ×
10000". -/
def ptcTable2Text : String := "
150 0  151 4  152 8  153 12  154 16  155 20  156 24  157 28  158 32  159 36
160 40  161 44  162 48  163 52  164 56  165 60  166 64  167 68  168 72  169 76
170 80  171 84  172 88  173 92  174 96  175 100  176 104  177 108  178 112  179 116
180 120  181 124  182 128  183 132  184 136  185 140  186 144  187 148  188 152  189 156
190 160  191 164  192 168  193 172  194 176  195 180  196 184  197 188  198 192  199 196
200 200  201 204  202 208  203 212  204 216  205 220  206 224  207 228  208 232  209 236
210 240  211 244  212 248  213 252  214 256  215 260  216 264  217 268  218 272  219 276
220 280  221 284  222 288  223 292  224 296  225 300  226 304  227 308  228 312  229 316
230 320  231 324  232 328  233 332  234 336  235 340  236 344  237 348  238 352  239 356
240 360  241 364  242 368  243 372  244 376  245 380  246 384  247 388  248 392  249 396
250 400  251 404  252 408  253 412  254 416  255 420  256 424  257 428  258 432  259 436
260 440  261 444  262 448  263 452  264 456  265 460  266 464  267 468  268 472  269 476
270 480  271 484  272 488  273 492  274 496  275 500  276 504  277 508  278 512  279 516
280 520  281 524  282 528  283 532  284 536  285 540  286 544  287 548  288 552  289 556
290 560  291 564  292 568  293 572  294 576  295 580  296 584  297 588  298 592  299 596
300 600  301 603  302 605  303 608  304 610  305 613  306 615  307 618  308 620  309 623
310 625  311 628  312 630  313 633  314 635  315 638  316 640  317 643  318 645  319 648
320 650  321 653  322 655  323 658  324 660  325 663  326 665  327 668  328 670  329 673
330 675  331 678  332 680  333 683  334 685  335 688  336 690  337 693  338 695  339 698
340 700  341 703  342 705  343 708  344 710  345 713  346 715  347 718  348 720  349 723
350 725  351 728  352 730  353 733  354 735  355 738  356 740  357 743  358 745  359 748
360 750  361 753  362 755  363 758  364 760  365 763  366 765  367 768  368 770  369 773
370 775  371 778  372 780  373 783  374 785  375 788  376 790  377 793  378 795  379 798
380 800  381 803  382 805  383 808  384 810  385 813  386 815  387 818  388 820  389 823
390 825  391 828  392 830  393 833  394 835  395 838  396 840  397 843  398 845  399 848
400 850"

def pairUp : List Int → List (Int × Int)
  | a :: b :: rest => (a, b) :: pairUp rest
  | _ => []

def ptcTable2 : List (Int × Int) :=
  pairUp (((ptcTable2Text.splitOn "\n").flatMap (·.splitOn " ")).filterMap String.toInt?)

/-! ## 2025: reconciliation -/

/-- §36B(f)(2)(B) (2025 text) and Rev. Proc. 2024-40 §3.07: the cap on the tax increase for excess advance payments,
by household income as a percent of the poverty line; unmarried individuals (other than surviving spouses and heads
of household) get the first column. `none` at 400% or more (no cap). -/
def repaymentCap2025 (unmarried : Bool) (pct : Int) : Option Int :=
  if pct < 200 then some (if unmarried then 375 else 750)
  else if pct < 300 then some (if unmarried then 975 else 1950)
  else if pct < 400 then some (if unmarried then 1625 else 3250)
  else none

/-- §36B(f)(2): the excess of advance payments over the credit is added to tax, capped for 2025. -/
def excessAptcTax2025 (unmarried : Bool) (F h aptc credit : Int) : Int :=
  match repaymentCap2025 unmarried (ptcLine5 F h) with
  | some cap => min (pos (aptc - credit)) cap
  | none => pos (aptc - credit)

/-- 2026: Pub. L. 119-21 §71305 struck the cap; the whole excess is added to tax. -/
def excessAptcTax2026 (aptc credit : Int) : Int := pos (aptc - credit)

/-! ## 2026 -/

/-- The 2026 applicable percentage (Rev. Proc. 2025-25), in basis points × 850·F (850 = 17 × 50 clears the tier
widths), sliding linearly within each tier on the exact percentage `100h/F`. -/
def ptcRate2026 (F h : Int) : Int :=
  if 100 * h < 133 * F then 210 * 850 * F
  else if 100 * h < 150 * F then 314 * 850 * F + 105 * 50 * (100 * h - 133 * F)
  else if 100 * h < 200 * F then 419 * 850 * F + 241 * 17 * (100 * h - 150 * F)
  else if 100 * h < 250 * F then 660 * 850 * F + 184 * 17 * (100 * h - 200 * F)
  else if 100 * h < 300 * F then 844 * 850 * F + 152 * 17 * (100 * h - 250 * F)
  else 996 * 850 * F

/-- The 2026 credit: §36B(c)(1)(A) applicable taxpayer 100%–400% ("does not exceed 400 percent"). -/
def ptc2026 (F B P h : Int) : Int :=
  if h < F ∨ 4 * F < h then 0 else min P (pos (B - roundDollar (h * ptcRate2026 F h) (8500000 * F)))

/-! ## Tests -/

-- Form 8962 instructions (2025), Table 1-1: "1 $15,060", "2 $20,440", ..., "8 $52,720"; "if your family size is 11
-- ... Enter the result of $68,860".
#guard [1, 2, 3, 4, 5, 6, 7, 8].map fpl2024 = [15060, 20440, 25820, 31200, 36580, 41960, 47340, 52720]
#guard fpl2024 11 = 68860
-- Worksheet 2, line 4: "for 0.9984, enter the result as 99; for 1.8565, enter the result as 185; and for 3.997,
-- enter the result as 399." (Household income / poverty line = those ratios, F = $10,000.)
#guard ptcLine5 10000 9984 = 99 ∧ ptcLine5 10000 18565 = 185 ∧ ptcLine5 10000 39970 = 399 ∧ ptcLine5 10000 40001 = 401
-- Table 2, all 251 rows ("150 0.0000" through "400 or more 0.0850").
#guard ptcTable2.length = 251
#guard ptcTable2.all fun (p, v) => ptcFigure p == v
-- Table 2's figure is the statute's 2025 percentage at whole percentages (exact at 150..300; within half a basis
-- point at 301..399).
#guard (List.range 251).all fun i =>
  let p : Int := 150 + i
  let exact := ptcRate2025 100 p    -- F = 100, h = p: rate × 100 in bp
  2 * 100 * ptcFigure p - 2 * exact ≤ 100 ∧ 2 * exact - 2 * 100 * ptcFigure p ≤ 100
-- Table 5 (2025): "Less than 200 ... $375 $750"; "At least 200 but less than 300 ... $975 $1,950"; "At least 300 but
-- less than 400 ... $1,625 $3,250"; "400 or more ... leave line 28 blank".
#guard repaymentCap2025 true 199 = some 375 ∧ repaymentCap2025 false 199 = some 750 ∧
  repaymentCap2025 true 200 = some 975 ∧ repaymentCap2025 false 299 = some 1950 ∧
  repaymentCap2025 true 300 = some 1625 ∧ repaymentCap2025 false 399 = some 3250 ∧ repaymentCap2025 true 400 = none
-- Rev. Proc. 2025-25 §3.01: 2026 initial/final percentages at the tier edges (F = 100, so h = percent).
#guard ptcRate2026 100 132 = 210 * 850 * 100 ∧ ptcRate2026 100 133 = 314 * 850 * 100 ∧
  ptcRate2026 100 150 = 419 * 850 * 100 ∧ ptcRate2026 100 200 = 660 * 850 * 100 ∧
  ptcRate2026 100 250 = 844 * 850 * 100 ∧ ptcRate2026 100 300 = 996 * 850 * 100 ∧ ptcRate2026 100 400 = 996 * 850 * 100
-- ... and the 2026 tiers meet their final percentages at the top of each tier (continuity inside 133%–300%).
#guard 314 * 850 + 105 * 50 * 17 = 419 * 850 ∧ 419 * 850 + 241 * 17 * 50 = 660 * 850 ∧
  660 * 850 + 184 * 17 * 50 = 844 * 850 ∧ 844 * 850 + 152 * 17 * 50 = 996 * 850

/-! ## Properties: 2025 -/

theorem rate2025_step (F h : Int) (hF : 0 < F) :
    0 ≤ ptcRate2025 F (h + 1) - ptcRate2025 F h ∧ ptcRate2025 F (h + 1) - ptcRate2025 F h ≤ 400 := by
  unfold ptcRate2025; omega

/-- The required contribution rises by at most 18.5 cents per dollar of household income, for every poverty line
and income: (rate + income × slope) is at most 6% + 300% × 4% below 300%, and 8.5% + 400% × 2.5% above. -/
theorem contrib2025_step (F h : Int) (hF : 0 < F) (hh : 0 ≤ h) :
    0 ≤ ptcContribScaled F (h + 1) - ptcContribScaled F h ∧
    ptcContribScaled F (h + 1) - ptcContribScaled F h ≤ 1850 * F := by
  have e : ptcContribScaled F (h + 1) - ptcContribScaled F h =
      ptcRate2025 F (h + 1) + h * (ptcRate2025 F (h + 1) - ptcRate2025 F h) := by
    unfold ptcContribScaled; rw [Int.add_mul, Int.one_mul, Int.mul_sub]; omega
  have r1 : ptcRate2025 F (h + 1) ≤ 850 * F := by unfold ptcRate2025; omega
  have r0 : 0 ≤ ptcRate2025 F h := by unfold ptcRate2025; omega
  have hs := rate2025_step F h hF
  have hn : 0 ≤ h * (ptcRate2025 F (h + 1) - ptcRate2025 F h) := Int.mul_nonneg hh hs.1
  rw [e]
  by_cases c4 : 4 * F ≤ h
  · have : ptcRate2025 F (h + 1) - ptcRate2025 F h = 0 := by unfold ptcRate2025; omega
    rw [this, Int.mul_zero]; omega
  · by_cases c3 : 3 * F ≤ h
    · have d : ptcRate2025 F (h + 1) - ptcRate2025 F h ≤ 250 := by unfold ptcRate2025; omega
      have : h * (ptcRate2025 F (h + 1) - ptcRate2025 F h) ≤ (4 * F) * 250 :=
        Int.mul_le_mul (by omega) d hs.1 (by omega)
      omega
    · have r1' : ptcRate2025 F (h + 1) ≤ 600 * F := by unfold ptcRate2025; omega
      have : h * (ptcRate2025 F (h + 1) - ptcRate2025 F h) ≤ (3 * F) * 400 :=
        Int.mul_le_mul (by omega) hs.2 hs.1 (by omega)
      omega

/-- **The 2025 credit is continuous in income (no 400% cliff).** For every poverty line, benchmark, premium and
income, one more dollar of household income lowers the exact credit by between 0 and 18.5 cents. -/
theorem ptc2025_continuous (F B P h : Int) (hF : 0 < F) (hh : 0 ≤ h) :
    0 ≤ ptcScaled F B P h - ptcScaled F B P (h + 1) ∧ ptcScaled F B P h - ptcScaled F B P (h + 1) ≤ 1850 * F := by
  have := contrib2025_step F h hF hh
  unfold ptcScaled pos; omega

/-- Rounding the same quantity: a rise of at most one unit of the divisor moves the rounded value by at most 1. -/
theorem roundDollar_step (x y D : Int) (hD : 0 < D) (h1 : x ≤ y) (h2 : y ≤ x + D) :
    roundDollar x D ≤ roundDollar y D ∧ roundDollar y D ≤ roundDollar x D + 1 := by
  unfold roundDollar
  constructor
  · exact Int.ediv_le_ediv (by omega) (by omega)
  · have : (2 * y + D) / (2 * D) ≤ (2 * x + D + 1 * (2 * D)) / (2 * D) := Int.ediv_le_ediv (by omega) (by omega)
    rw [Int.add_mul_ediv_right _ _ (by omega)] at this
    omega

/-- In whole dollars (above 100% of the poverty line, through and beyond 400%): one more dollar of income never
costs more than one dollar of credit, and never raises it. -/
theorem ptc2025_step (F B P h : Int) (hF : 0 < F) (hh : F ≤ h) :
    ptcStatute2025 F B P h - ptcStatute2025 F B P (h + 1) ≤ 1 ∧
    ptcStatute2025 F B P (h + 1) ≤ ptcStatute2025 F B P h := by
  have hc := contrib2025_step F h hF (by omega)
  have hr := roundDollar_step (ptcContribScaled F h) (ptcContribScaled F (h + 1)) (10000 * F) (by omega) (by omega)
    (by omega)
  unfold ptcStatute2025
  simp only [show ¬ (h < F) by omega, show ¬ (h + 1 < F) by omega, ↓reduceIte]
  unfold pos; omega

/-- The no-cliff statement at 400% itself. -/
theorem ptc2025_no_400_cliff (F B P : Int) (hF : 0 < F) :
    ptcStatute2025 F B P (4 * F) - ptcStatute2025 F B P (4 * F + 1) ≤ 1 :=
  (ptc2025_step F B P (4 * F) hF (by omega)).1

/-- **The 2025 cliff is at 100%.** Below the poverty line there is no credit (§36B(c)(1)(A)); at it the
contribution is zero and the whole benchmark (up to the premium) is paid. (The regulations' exception for advance
payment recipients, Treas. Reg. §1.36B-2(b)(6), and §36B(c)(1)(B) for some lawfully present aliens, soften this for
2025; neither is modelled.) -/
theorem ptc2025_cliff_at_100 (F B P : Int) (hF : 0 < F) :
    ptcStatute2025 F B P (F - 1) = 0 ∧ ptcStatute2025 F B P F = min P (pos B) := by
  have hr : ptcRate2025 F F = 0 := by unfold ptcRate2025; omega
  unfold ptcStatute2025 ptcContribScaled
  rw [hr, Int.mul_zero]
  constructor
  · simp only [show F - 1 < F by omega, ↓reduceIte]
  · simp only [show ¬ (F < F) by omega, ↓reduceIte]
    have : roundDollar 0 (10000 * F) = 0 := by
      unfold roundDollar; exact Int.ediv_eq_zero_of_lt (by omega) (by omega)
    rw [this, Int.sub_zero]

/-- Form 8962 truncates the percentage to a whole number, so its credit has small notches: a family of eight
(poverty line $52,720, benchmark $20,000) loses $64 of credit between household income $158,159 (299%: figure
0.0596) and $158,160 (300%: 0.0600). -/
theorem form_notch_2025 :
    ptcForm2025 52720 20000 30000 158159 - ptcForm2025 52720 20000 30000 158160 = 64 := by decide

/-- ... and differs from the statute's sliding scale: $63 more than the statute at $156,577 (the truncated 296%
understates the percentage), $11 less at $202,972 (the rounded-up four-place figure overstates it). -/
theorem form_vs_statute_2025 :
    ptcForm2025 52720 20000 30000 156577 - ptcStatute2025 52720 20000 30000 156577 = 63 ∧
    ptcStatute2025 52720 20000 30000 202972 - ptcForm2025 52720 20000 30000 202972 = 11 := by decide

/-- **The 2025 repayment cliff at 400%.** The credit has no cliff there, but the cap on repaying excess advance
payments does: a single person (poverty line $15,060) who received $5,000 too much repays $1,625 at household income
$60,239 (399%) and all $5,000 at $60,240 (400%). -/
theorem repayment_cliff_2025 :
    excessAptcTax2025 true 15060 60239 8000 3000 = 1625 ∧ excessAptcTax2025 true 15060 60240 8000 3000 = 5000 := by
  decide

/-- The 2025 cap never makes the repayment larger than the excess; 2026 (no cap) repays at least as much. -/
theorem repayment_le (u : Bool) (F h a c : Int) :
    excessAptcTax2025 u F h a c ≤ excessAptcTax2026 a c := by
  unfold excessAptcTax2025 excessAptcTax2026
  split <;> omega

/-! ## Properties: 2026 -/

/-- **The 400% cliff returns in 2026.** With a $15,650 poverty line (single person) and a $12,000 benchmark:
$5,765 of credit at $62,600 (exactly 400%: 9.96% of $62,600 = $6,235), nothing at $62,601. -/
theorem ptc2026_cliff_400 :
    ptc2026 15650 12000 12000 62600 = 5765 ∧ ptc2026 15650 12000 12000 62601 = 0 := by decide

/-- For every poverty line, benchmark and premium, there is no 2026 credit above 400%. -/
theorem ptc2026_zero_above_400 (F B P h : Int) (hh : 4 * F < h) : ptc2026 F B P h = 0 := by
  unfold ptc2026; simp only [show (h < F ∨ 4 * F < h) from Or.inr hh, ↓reduceIte]

/-- And for every poverty line, at exactly 400% the 2026 credit is the benchmark less 9.96% of income (rounded),
so the cliff is that whole amount. -/
theorem ptc2026_at_400 (F B P : Int) (hF : 0 < F) :
    ptc2026 F B P (4 * F) = min P (pos (B - roundDollar (4 * F * (996 * 850 * F)) (8500000 * F))) := by
  unfold ptc2026 ptcRate2026
  simp only [show ¬ (4 * F < F ∨ 4 * F < 4 * F) by omega, ↓reduceIte]
  simp only [show ¬ (100 * (4 * F) < 133 * F) by omega, show ¬ (100 * (4 * F) < 150 * F) by omega,
    show ¬ (100 * (4 * F) < 200 * F) by omega, show ¬ (100 * (4 * F) < 250 * F) by omega,
    show ¬ (100 * (4 * F) < 300 * F) by omega, ↓reduceIte]

/-- The 2025 rule at the same point: no cliff; $6,679 of credit just above 400% (8.5% of $62,601 = $5,321). -/
theorem ptc2025_same_point : ptcStatute2025 15650 12000 12000 62601 = 6679 := by decide

/-- The 2026 table itself jumps at 133%: 2.10% just below, 3.14% at 133%. With a $15,650 poverty line, $1 more
income (from $20,814 to $20,815) costs $217 of credit. -/
theorem ptc2026_jump_133 :
    ptc2026 15650 12000 12000 20814 - ptc2026 15650 12000 12000 20815 = 217 := by decide

end TaxCode.Individual.D
