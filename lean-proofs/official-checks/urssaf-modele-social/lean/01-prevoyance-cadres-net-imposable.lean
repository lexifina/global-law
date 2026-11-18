/-!
# Net imposable of a cadre, 2025: the employer's compulsory prévoyance (1,50 % of T1) is deductible (CGI art. 83, 1° quater)

Core Lean only, no `sorry`. Amounts are integers in units of 10⁻¹² € (`U`), so every rate is exact.
Pay `g` is a monthly gross in cents. Rates are written per 100 000 (6,90 % = 6 900).

* `law g`: CGI art. 83 — gross pay, plus the employer's health contribution (art. 83, 1° quater, 3rd para.: "ajoutées à la
  rémunération"), plus the employer's other prévoyance contribution (1,50 % T1, ANI du 17 novembre 2017), less the deductible
  social contributions (1°), less the deductible CSG (art. 154 quinquies), less the prévoyance contributions of 1° quater
  (employee's, and the employer's other than health) within the limit of the 4th para.
* `engine g`: the rule `salarié . rémunération . net . imposable . sans déductions` of modele-social 11.1.0
  (règles/salarié/rémunération.publicodes, l. 117-123): net + CSG non déductible + CRDS + `prévoyances . employeur`
  (health AND cadres) + `prévoyances . salarié . non déductible`; the abattements of `net . imposable` are all nil here.
-/

namespace Repro4320

/-- 10⁻¹² € per cent. -/
def cent : Int := 10000000000
/-- `r`/100 000 of `x` cents, in U. -/
def pct (r x : Int) : Int := r * x * 100000
/-- `r`/100 000 of an amount already in U. -/
def pctU (r x : Int) : Int := r * x / 100000

def pss : Int := 392500            -- 3 925 €/mois (arrêté du 19 décembre 2024)
def santeTotal : Int := 4000       -- complémentaire santé, engine default 40 €/mois
def santeEmpl : Int := 2000 * cent -- engine default: 50 % employer
def santeSal : Int := 2000 * cent

def t1 (g : Int) : Int := min g pss
def t2 (g : Int) : Int := max 0 (min g (8 * pss) - pss)
/-- Employee social contributions deductible under CGI art. 83, 1° (CSS D242-4; ANI AGIRC-ARRCO; APEC). -/
def ssc (g : Int) : Int :=
  pct 6900 (t1 g) + pct 400 g + pct 3150 (t1 g) + pct 8640 (t2 g) + pct 860 (t1 g) + pct 1080 (t2 g)
    + (if g > pss then pct 140 (t1 g + t2 g) else 0) + pct 24 (min g (4 * pss))
/-- Employer prévoyance for cadres, 1,50 % of T1. -/
def cadres (g : Int) : Int := pct 1500 (t1 g)
/-- CSG/CRDS base (CSS L136-1-1, L136-2): 98,25 % below 4 PSS, plus the employer's prévoyance contributions. -/
def csgBase (g : Int) : Int := pct 98250 (min g (4 * pss)) + (max 0 (g - 4 * pss)) * cent + santeEmpl + cadres g
def csgDed (g : Int) : Int := pctU 6800 (csgBase g)
def csgNd (g : Int) : Int := pctU 2400 (csgBase g)
def crds (g : Int) : Int := pctU 500 (csgBase g)
def net (g : Int) : Int := g * cent - ssc g - santeSal - csgDed g - csgNd g - crds g

/-- CGI art. 83, 1° quater, 4th para.: 5 % of the PSS + 2 % of gross pay, at most 2 % of 8 PSS. -/
def limit (g : Int) : Int := min (pct 5000 pss + pct 2000 g) (pct 2000 (8 * pss))
def law (g : Int) : Int := g * cent + santeEmpl + cadres g - ssc g - csgDed g - min (santeSal + cadres g) (limit g)

/-- The engine's rule, transcribed. `salarié . non déductible` = employee part above the same limit (0 here). -/
def engine (g : Int) : Int :=
  net g + csgNd g + crds g + (santeEmpl + cadres g) + max 0 (santeSal - limit g)

/-! ## The exact case: 5 000 €/mois brut -/
theorem law_5000 : law 500000 = 4099679 * 1000000000 := by decide
theorem engine_5000 : engine 500000 = 4158554 * 1000000000 := by decide
/-- 58,875 €/mois too much in the engine's net imposable, i.e. 706,50 € a year. -/
theorem gap_5000 : engine 500000 - law 500000 = 58875 * 1000000000 ∧ 12 * 58875 = 706500 := by decide

/-! ## The general rule, for every gross pay from 0 to 8 PSS and beyond -/
/-- The limit never binds with these contributions, at any pay. -/
theorem pool_within_limit (g : Int) (h : 0 ≤ g) : santeSal + cadres g ≤ limit g := by
  unfold santeSal cadres limit pct t1 pss cent; omega
/-- So the engine's figure exceeds the law's by exactly the employer's cadre prévoyance, 1,50 % of min(gross, PSS). -/
theorem gap (g : Int) (h : 0 ≤ g) : engine g - law g = cadres g := by
  have hp := pool_within_limit g h
  have hc : 0 ≤ cadres g := by unfold cadres pct t1 pss; omega
  have h2 : max 0 (santeSal - limit g) = 0 := by omega
  have h3 : min (santeSal + cadres g) (limit g) = santeSal + cadres g := by omega
  unfold engine law net; rw [h2, h3]; omega

end Repro4320
