/-!
# Basic arithmetic for the French income tax

Every amount is a whole number of euros (`Int`). The Code général des impôts fixes one rounding rule for
the income tax and repeats it twice:

* CGI art. 193, last paragraph: "le revenu imposable ainsi que les différents éléments ayant concouru à
  sa détermination, sont arrondis à l'euro le plus proche. La fraction d'euro égale à 0,50 est comptée
  pour 1."
* CGI art. 1657, 1: "Les bases de cotisation des impôts directs sont arrondies à l'euro le plus proche ; la
  fraction d'euro égale à 0,50 est comptée pour 1. [...] Les cotisations d'impôts directs de toute nature
  sont arrondies selon les modalités définies au premier alinéa. Il en est de même du montant des
  majorations, réductions et dégrèvements."

So every base, every amount of tax and every reduction is rounded half up to the euro. `rnd n d` is the
exact value `n / d` (with `d > 0`) rounded that way.
-/

namespace FrTax

/-- `n / d` rounded to the nearest euro, a fraction of exactly one half counted as one (CGI art. 193,
art. 1657, 1). Requires `d > 0`; for a negative `n` the half goes up as well (`-2.5 ↦ -2`). -/
def rnd (n d : Int) : Int := (2 * n + d) / (2 * d)

/-- `pct p x`: `p` per cent of `x`, rounded (`p` in hundredths of a per cent, so `pct 4525 x` is 45.25 %). -/
def pct (p x : Int) : Int := rnd (p * x) 10000

/-- The positive part, `max 0 x`. -/
def pos (x : Int) : Int := max 0 x

theorem rnd_exact (k d : Int) (hd : 0 < d) : rnd (k * d) d = k := by
  unfold rnd
  have h : 2 * (k * d) + d = (2 * d) * k + d := by
    rw [Int.mul_comm k d, ← Int.mul_assoc]
  rw [h, Int.add_comm, Int.add_mul_ediv_left _ _ (by omega)]
  have : d / (2 * d) = 0 := Int.ediv_eq_zero_of_lt (by omega) (by omega)
  omega

theorem rnd_mono {a b d : Int} (hd : 0 < d) (h : a ≤ b) : rnd a d ≤ rnd b d := by
  unfold rnd
  exact Int.ediv_le_ediv (by omega) (by omega)

theorem rnd_nonneg {a d : Int} (hd : 0 < d) (h : 0 ≤ a) : 0 ≤ rnd a d := by
  unfold rnd
  exact Int.ediv_nonneg (by omega) (by omega)

end FrTax
