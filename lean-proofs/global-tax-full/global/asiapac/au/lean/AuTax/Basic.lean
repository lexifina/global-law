import TaxKernel

/-!
# Basic arithmetic for the Australian model

Money is held in whole **cents** (`Int`). Rates are in **basis points** (1600 = 16 %, 200 = 2 %). A cents amount
times a rate in basis points is a number of **ticks** (one ten-thousandth of a cent); the statutes compute tax "for
each $1" of taxable income (Income Tax Rates Act 1986 Sch 7 Part I cl 1), so tax on whole dollars at rates in whole
basis points is exact in cents, and ticks are only needed for the Medicare levy shade-in (10 %), the family
reduction (8 %) and the franking gross-up (30/70).

The statutes contain no general rounding rule for the liability. Conventions used here (and named where used):
* taxable income is a whole number of dollars (the return asks for whole dollars; cents are dropped), `wholeDollars`;
* a liability is reported in cents rounded down (`ticksToCents`);
* the PAYG withholding schedule rounds to the nearest dollar, 50 cents up (`roundHalfUpDollar`, Schedule 1).

Kernel (`cmp20/kernel`, TaxKernel 1.0): the rates are a `TaxKernel.Schedule`, the Medicare levy a `TaxKernel.Surcharge`,
LITO the larger of two `TaxKernel.Credit`s, the FTB income tests `TaxKernel.Taper`s (see `Person.lean`,
`Household.lean`). `schedTicks` below is the pre-kernel schedule, kept only because its monotonicity proof is
reused by nothing else; the model no longer calls it.
-/

namespace AuTax

/-- The positive part, `max 0 x`. -/
def pos (x : Int) : Int := max 0 x

/-- Dollars to cents. -/
def aud (d : Int) : Int := 100 * d

/-- Ticks (1/10000 cent) to cents, rounded down. -/
def ticksToCents (t : Int) : Int := t / 10000

/-- Cents rounded down to whole dollars (still in cents). -/
def wholeDollars (c : Int) : Int := (c / 100) * 100

/-- A cents amount times a rate in basis points, rounded down to the cent. -/
def pct (c : Int) (rateBp : Int) : Int := ticksToCents (c * rateBp)

theorem pos_nonneg (x : Int) : 0 ≤ pos x := by unfold pos; omega

theorem pos_mono {a b : Int} (h : a ≤ b) : pos a ≤ pos b := by unfold pos; omega

theorem ticksToCents_mono {a b : Int} (h : a ≤ b) : ticksToCents a ≤ ticksToCents b := by
  unfold ticksToCents; exact Int.ediv_le_ediv (by omega) h

/-! ## A progressive schedule (the kernel's `Schedule`)

A schedule is a list of `(threshold in cents, rate in bp)` in increasing threshold order; the rate applies to the
part of the base above its threshold and up to the next threshold. -/

def schedTicks : List (Int × Int) → Int → Int
  | [], _ => 0
  | [(lo, r)], x => r * pos (x - lo)
  | (lo, r) :: (lo2, r2) :: rest, x => r * pos (min x lo2 - lo) + schedTicks ((lo2, r2) :: rest) x

/-- Every band contributes a non-decreasing amount when the base grows (rates non-negative). -/
def ratesNonneg : List (Int × Int) → Prop
  | [] => True
  | (_, r) :: rest => 0 ≤ r ∧ ratesNonneg rest

theorem schedTicks_mono : ∀ (s : List (Int × Int)), ratesNonneg s → ∀ {x y : Int}, x ≤ y →
    schedTicks s x ≤ schedTicks s y
  | [], _, _, _, _ => by simp [schedTicks]
  | [(lo, r)], h, x, y, hxy => by
    simp only [schedTicks]
    have hr : 0 ≤ r := h.1
    exact Int.mul_le_mul_of_nonneg_left (pos_mono (by omega)) hr
  | (lo, r) :: (lo2, r2) :: rest, h, x, y, hxy => by
    simp only [schedTicks]
    have hr : 0 ≤ r := h.1
    have h1 : r * pos (min x lo2 - lo) ≤ r * pos (min y lo2 - lo) :=
      Int.mul_le_mul_of_nonneg_left (pos_mono (by omega)) hr
    have h2 := schedTicks_mono ((lo2, r2) :: rest) h.2 hxy
    omega

end AuTax
