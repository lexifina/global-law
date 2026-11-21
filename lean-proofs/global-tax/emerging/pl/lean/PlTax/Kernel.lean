/-!
# Generic parts (local stand-in for the shared `TaxKernel`)

`~/cmp20/kernel` (Lake project `TaxKernel`) did not exist when this model was started, so the generic parts the Polish
model needs are written here once, with their theorems, and listed as `kernel_gaps` in `results/summary.json`:

* `pos`, `rhu`, `pctGr`, `zl`: positive part, half-up division, basis points of an amount in grosze, and the
  Ordynacja podatkowa's rounding to whole złoty (art. 63 § 1: "końcówki kwot wynoszące mniej niż 50 groszy pomija się,
  a końcówki kwot wynoszące 50 i więcej groszy podwyższa się do pełnych złotych").
* `Band` / `schedRaw`: a progressive schedule as a list of bands (lower bound, optional upper bound, rate in basis
  points), with monotonicity for any list of non-negative rates.
* `capped`: a contribution base with a ceiling (social insurance).

Amounts are `Int` grosze unless a name ends in `Zl`; `/` on `Int` is floor division for positive divisors.
-/

namespace PlTax

/-- The positive part `max 0 x`. -/
def pos (x : Int) : Int := max 0 x

/-- `n / d` rounded half up (for `n ≥ 0`, `d > 0`). -/
def rhu (n d : Int) : Int := (2 * n + d) / (2 * d)

/-- `bp` basis points of `g` grosze, rounded half up to the grosz (ZUS and payroll practice; grosze are the unit of
every contribution). -/
def pctGr (g bp : Int) : Int := rhu (g * bp) 10000

/-- Ordynacja podatkowa art. 63 § 1 (Dz.U. 1997 nr 137 poz. 926; https://api.sejm.gov.pl/eli/acts/DU/2015/1649):
grosze to whole złoty, 50 gr and more up. A negative amount (a refund) is rounded the same way on its magnitude. -/
def zl (g : Int) : Int := if 0 ≤ g then rhu g 100 else - rhu (-g) 100

/-- A contribution base with a ceiling. -/
def capped (x cap : Int) : Int := min x cap

/-- One band of a progressive schedule: from `lo` to `hi` (none = no top) at `rate` basis points. -/
structure Band where
  lo : Int
  hi : Option Int
  rate : Int
  deriving Repr

/-- The part of `b` that falls in the band. -/
def Band.width (bd : Band) (b : Int) : Int :=
  match bd.hi with
  | none => pos (b - bd.lo)
  | some h => pos (min b h - bd.lo)

/-- The schedule's tax in (unit × basis points): `Σ rate × width`. -/
def schedRaw : List Band → Int → Int
  | [], _ => 0
  | bd :: rest, b => bd.rate * bd.width b + schedRaw rest b

theorem pos_nonneg (x : Int) : 0 ≤ pos x := by unfold pos; omega
theorem pos_mono {a b : Int} (h : a ≤ b) : pos a ≤ pos b := by unfold pos; omega

theorem rhu_mono {a b : Int} (d : Int) (hd : 0 < d) (h : a ≤ b) : rhu a d ≤ rhu b d := by
  unfold rhu; exact Int.ediv_le_ediv (by omega) (by omega)

theorem rhu_nonneg {a : Int} (d : Int) (hd : 0 < d) (h : 0 ≤ a) : 0 ≤ rhu a d := by
  unfold rhu; exact Int.ediv_nonneg (by omega) (by omega)

theorem pctGr_mono {a b : Int} (bp : Int) (hbp : 0 ≤ bp) (h : a ≤ b) : pctGr a bp ≤ pctGr b bp := by
  unfold pctGr
  apply rhu_mono 10000 (by decide)
  exact Int.mul_le_mul_of_nonneg_right h hbp

theorem zl_mono {a b : Int} (h : a ≤ b) : zl a ≤ zl b := by
  unfold zl rhu; split <;> split <;> omega

theorem width_mono (bd : Band) {a b : Int} (h : a ≤ b) : bd.width a ≤ bd.width b := by
  rcases bd with ⟨lo, hi, r⟩
  cases hi with
  | none => simp only [Band.width, pos]; omega
  | some x => simp only [Band.width, pos]; omega

/-- **Any schedule with non-negative rates is monotone.** -/
theorem schedRaw_mono (bs : List Band) (hr : ∀ bd ∈ bs, 0 ≤ bd.rate) {a b : Int} (h : a ≤ b) :
    schedRaw bs a ≤ schedRaw bs b := by
  induction bs with
  | nil => simp [schedRaw]
  | cons bd rest ih =>
    simp only [schedRaw]
    have h1 := width_mono bd h
    have h2 : 0 ≤ bd.rate := hr bd (by simp)
    have h3 := ih (fun x hx => hr x (by simp [hx]))
    have := Int.mul_le_mul_of_nonneg_left h1 h2
    omega

end PlTax
