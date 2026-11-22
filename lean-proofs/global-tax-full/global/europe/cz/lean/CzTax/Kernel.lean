/-!
# Local stand-in for the shared kernel (`cmp20/kernel`, TaxKernel)

The kernel's API did not exist when this model was written (CONTRACT20: "do not wait for it"). These are the generic
parts the Czech model needs, written once here and listed as `kernel_gaps` in `results/summary.json`:

* `Rounding`: down / up to a unit (`floorTo`, `ceilTo`, `cdiv`), rate in basis points rounded either way.
* `Schedule`: progressive brackets `(threshold, rate in bp)` ascending, applied to whole currency units; the tax is
  returned *exactly* in bp-units (CZK × 10 000) so that each statute can apply its own rounding afterwards.
* `Credit`: a non-refundable credit (capped at the tax) and the refundable remainder, with a minimum payable amount.
* `Social`: a contribution with a yearly ceiling on the base, computed month by month with per-month rounding.

Every amount is a whole number of crowns (`Int`); `/` on `Int` is Euclidean division (the floor, for a positive
divisor).
-/

namespace CzTax

/-- The positive part `max 0 x`. -/
def pos (x : Int) : Int := max 0 x

/-- `a / b` rounded up, for `b > 0` (valid for every integer `a`). -/
def cdiv (a b : Int) : Int := (a + b - 1) / b

/-- Round a non-negative amount down to a multiple of `u` (negative amounts become 0). -/
def floorTo (u x : Int) : Int := pos x / u * u

/-- Round up to a multiple of `u`. -/
def ceilTo (u x : Int) : Int := cdiv x u * u

/-- `x × bp / 10 000` rounded up to the crown. -/
def bpCeil (x bp : Int) : Int := cdiv (x * bp) 10000

/-- `x × bp / 10 000` rounded down to the crown. -/
def bpFloor (x bp : Int) : Int := x * bp / 10000

/-! ## Schedule -/

/-- A progressive schedule: ascending `(threshold, rate in bp)`; the rate applies from its threshold to the next.
The result is the exact tax in units of 1/10 000 crown. -/
def schedBp : List (Int × Int) → Int → Int
  | [], _ => 0
  | [(t, r)], x => r * pos (x - t)
  | (t, r) :: (t2, r2) :: rest, x => r * pos (min x t2 - t) + schedBp ((t2, r2) :: rest) x

/-! ## Credit -/

/-- A non-refundable credit `c` against tax `t`: the part used. -/
def creditUsed (t c : Int) : Int := min (pos t) (pos c)

/-- The refundable remainder of a credit `c` against tax `t`, paid only if it reaches `minPay` and `eligible`. -/
def refundable (t c minPay : Int) (eligible : Bool) : Int :=
  let r := pos c - creditUsed t c
  if eligible && r ≥ minPay then r else 0

/-! ## Social contribution with a yearly ceiling, month by month -/

/-- Split a yearly amount into twelve whole-crown months: eleven equal months and the remainder in December. -/
def monthsOf (y : Int) : List Int :=
  let m := y / 12
  (List.replicate 11 m) ++ [y - 11 * m]

/-- Contribution at `bp` with per-month rounding up, on bases capped so that their running total never exceeds
`cap` (the yearly maximum assessment base). Returns `(contribution, base used)`. -/
def cappedMonthly (bp cap : Int) (months : List Int) : Int × Int :=
  let step := fun (acc : Int × Int) (w : Int) =>
    let used := acc.2
    let b := max 0 (min w (cap - used))
    (acc.1 + bpCeil b bp, used + b)
  months.foldl step (0, 0)

theorem pos_nonneg (x : Int) : 0 ≤ pos x := by unfold pos; omega
theorem pos_mono {a b : Int} (h : a ≤ b) : pos a ≤ pos b := by unfold pos; omega

theorem floorTo100_le (x : Int) (h : 0 ≤ x) : floorTo 100 x ≤ x := by unfold floorTo pos; omega
theorem floorTo100_gt (x : Int) (h : 0 ≤ x) : x < floorTo 100 x + 100 := by unfold floorTo pos; omega
theorem floorTo100_mono {a b : Int} (h : a ≤ b) : floorTo 100 a ≤ floorTo 100 b := by unfold floorTo pos; omega

theorem cdiv_mono {a a' : Int} (b : Int) (hb : 0 < b) (h : a ≤ a') : cdiv a b ≤ cdiv a' b := by
  unfold cdiv; exact Int.ediv_le_ediv hb (by omega)

/-- Rounding up to the crown (division by 100, the § 16 cents): never below, less than one crown above. -/
theorem cdiv100_ge (a : Int) : a ≤ 100 * cdiv a 100 := by unfold cdiv; omega
theorem cdiv100_lt (a : Int) : 100 * cdiv a 100 < a + 100 := by unfold cdiv; omega
theorem cdiv10000_ge (a : Int) : a ≤ 10000 * cdiv a 10000 := by unfold cdiv; omega

/-- The used part of a credit never exceeds the tax, nor the credit. -/
theorem creditUsed_le (t c : Int) : creditUsed t c ≤ pos t ∧ creditUsed t c ≤ pos c := by
  unfold creditUsed; omega

theorem creditUsed_nonneg (t c : Int) : 0 ≤ creditUsed t c := by unfold creditUsed pos; omega

/-- Used part plus refundable part never exceed the credit. -/
theorem credit_total_le (t c m : Int) (e : Bool) : creditUsed t c + refundable t c m e ≤ pos c := by
  unfold refundable
  dsimp only
  have := creditUsed_le t c
  split <;> omega

/-- A schedule with non-negative rates is monotone in the income. -/
theorem schedBp_mono (l : List (Int × Int)) (hr : ∀ p ∈ l, 0 ≤ p.2) {a b : Int} (h : a ≤ b) :
    schedBp l a ≤ schedBp l b := by
  induction l with
  | nil => simp [schedBp]
  | cons p rest ih =>
    obtain ⟨t, r⟩ := p
    have hr0 : 0 ≤ r := hr (t, r) (by simp)
    have hrest : ∀ q ∈ rest, 0 ≤ q.2 := fun q hq => hr q (by simp [hq])
    match rest, ih, hrest with
    | [], _, _ =>
      simp only [schedBp]
      exact Int.mul_le_mul_of_nonneg_left (pos_mono (by omega)) hr0
    | (t2, r2) :: rest', ih', hrest' =>
      simp only [schedBp]
      have h1 : r * pos (min a t2 - t) ≤ r * pos (min b t2 - t) :=
        Int.mul_le_mul_of_nonneg_left (pos_mono (by omega)) hr0
      have h2 := ih' hrest'
      omega

end CzTax
