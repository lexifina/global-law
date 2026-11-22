import LtTax.Params

/-!
# Neapmokestinamasis pajamų dydis (NPD), GPMĮ 20 straipsnis

* 1 d. (annual, "MNPD", by "GMP" = the year's taxable income, 7 d.): "MNPD negali būti didesnis negu 7 500 eurų,
  jeigu ... GMP neviršija minimaliosios mėnesinės algos ... dvylikos dydžių sumos"; then
  "7 500 – 0,42 × (GMP – dvylika minimaliosios mėnesinės algos ...)" up to "23 112 eurų per metus"; above that
  "4 800 – 0,18 × (GMP – 12 × 642)" (2023 text; 2025 amounts in `Params.y2025`).
* 2 d. (monthly, applied by the employer): the same with monthly amounts, on "su darbo santykiais ... susijusios
  pajamos per mėnesį".
* 3 d.: "Jeigu ... apskaičiuotas NPD yra neigiamas, laikoma, kad jis lygus 0".

Each formula is a kernel `Taper` (full, start, num/den). The reduction is rounded down to the cent (the statute does
not say how to round; 0.49 × an amount in cents can leave a fraction of a cent).
-/

namespace LtTax
open TaxKernel

/-- 20 str. 1 d. 2 p.: 12 × NPDmax – c1/100 × (GMP – 12 × MMA) (cents). -/
def t1Y (yp : YP) : Taper := { full := 12 * yp.npdMax, start := 12 * yp.mma, num := yp.c1, den := 100 }
/-- 20 str. 1 d. 3 p.: "4 800 – 0,18 × (GMP – 12 × 642)". -/
def t2Y : Taper := { full := 480000, start := 12 * 64200, num := 18, den := 100 }
/-- 20 str. 2 d. 2 p.: NPDmax – c1/100 × (P – MMA). -/
def t1M (yp : YP) : Taper := { full := yp.npdMax, start := yp.mma, num := yp.c1, den := 100 }
/-- 20 str. 2 d. 3 p.: "400 – 0,18 × (... pajamos – 642)". -/
def t2M : Taper := { full := 40000, start := 64200, num := 18, den := 100 }

/-- The annual NPD exactly as the statute lists its cases. -/
def mnpd (yp : YP) (gmp : Int) : Int :=
  if gmp ≤ 12 * yp.mma then 12 * yp.npdMax
  else if gmp ≤ yp.thrY then (t1Y yp).amount gmp
  else if yp.second then t2Y.amount gmp
  else (t1Y yp).amount gmp

/-- The monthly NPD (employer withholding). -/
def npdMonth (yp : YP) (p : Int) : Int :=
  if p ≤ yp.mma then yp.npdMax
  else if p ≤ yp.thrM then (t1M yp).amount p
  else if yp.second then t2M.amount p
  else (t1M yp).amount p

/-- Where the annual NPD reaches 0 (cents): 12 × 642 + 4 800 / 0,18 = 34 370,67 € (2022-2025). -/
def npdZeroY : Int := 12 * 64200 + (480000 * 100 + 17) / 18

end LtTax
