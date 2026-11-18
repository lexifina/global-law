/-!
# Arithmetic helpers for the German income tax (VZ 2025)

Amounts are `Int`. The statute counts the tariff in whole euros and rounds *down* twice:

* EStG § 32a (1) Satz 1: "Die tarifliche Einkommensteuer bemisst sich nach dem auf volle Euro abgerundeten zu
  versteuernden Einkommen."
* EStG § 32a (1) Satz 6: "Der sich ergebende Steuerbetrag ist auf den nächsten vollen Euro-Betrag abzurunden."

The surtaxes are counted in cents and also round down:

* SolZG 1995 § 4 Satz 3: "Bruchteile eines Cents bleiben außer Ansatz."

Social contributions are computed in cents (annual amounts here, rounded half up to the cent: SGB IV § 28h ff. and the
Beitragsverfahrensverordnung compute per pay period; see `Social.lean` for the simplification).

`/` on `Int` is Euclidean division: for a positive divisor it is the floor, which is what "abrunden" means for the
non-negative amounts the statute rounds. `cdiv` rounds up, `rndHalf` rounds half up.
-/

namespace LoopDe

/-- The positive part, `max 0 x`. -/
def pos (x : Int) : Int := max 0 x

/-- `a / b` rounded up (for `b > 0`). -/
def cdiv (a b : Int) : Int := -((-a) / b)

/-- `a / b` rounded to the nearest integer, a half rounded up (for `b > 0`). -/
def rndHalf (a b : Int) : Int := (2 * a + b) / (2 * b)

/-- Euros to cents. -/
def ct (e : Int) : Int := 100 * e

/-- Cents to whole euros, rounded down ("auf volle Euro abgerundet"). -/
def euroDown (c : Int) : Int := c / 100

theorem pos_nonneg (x : Int) : 0 ≤ pos x := Int.le_max_left 0 x

theorem pos_mono {a b : Int} (h : a ≤ b) : pos a ≤ pos b := by
  unfold pos; omega

theorem ediv_mono {a b d : Int} (hd : 0 < d) (h : a ≤ b) : a / d ≤ b / d :=
  Int.ediv_le_ediv hd h

/-- Floor division: `d * (a / d) ≤ a < d * (a / d) + d`. -/
theorem ediv_bounds (a d : Int) (hd : 0 < d) : d * (a / d) ≤ a ∧ a < d * (a / d) + d :=
  ⟨Int.mul_ediv_self_le (by omega), Int.lt_mul_ediv_self_add hd⟩

end LoopDe
