import TaxKernel.World

/-!
# Argentina: impuesto a las ganancias of a resident individual, período fiscal 2025 (employee, fourth category)

Statutes (InfoLEG consolidated texts served by argentina.gob.ar/normativa; files in `ar/law/`):
* Ley de Impuesto a las Ganancias, t.o. Decreto 824/2019 (norma-332890/actualizacion, sha256 60aaf9f0…), as replaced by
  Ley 27.743 (B.O. 08/07/2024): art. 30 (a) "pesos tres millones noventa y un mil treinta y cinco ($ 3.091.035)",
  (b) 1 cónyuge "$ 2.911.135", 2 "$ 1.468.096 por cada hijo … menor de dieciocho (18) años", (c) 2 "Tres coma ocho (3,8)
  veces" (a) for art. 82 (a)-(c) income ("incrementar … en 3,8 veces": 4,8 × (a), checked), plus "la doceava parte del total de deducciones resultantes de la suma de los
  incisos a), b) y c), apartado 2"; last paragraph "Los montos previstos en este artículo se ajustarán semestralmente, a
  partir del año fiscal 2025 … en los meses de enero y julio, por el coeficiente que surja de la variación del IPC";
  art. 94 scale (base amounts) with the same adjustment rule; art. 85 (d) pension contributions and (f) obra social
  contributions deductible.
* ARCA, "Deducciones del artículo 30 … período anual 2025" (official secondary, sha256 da74f460…): "Ganancias no
  imponibles 4.507.505,52; Cónyuge 4.245.166,13; Hijo 2.140.852,77; Deducción Especial [inciso c) apartado 2]
  21.636.026,50" ("Actualización por IPC INDEC, según el artículo 73 de la Ley N° 27.743").
* The 2025 annual art. 94 scale: ARCA's table was not reached. Both articles are adjusted "por el coeficiente" of the
  same IPC rule, so the scale is derived as base × (4.507.505,52 / 3.091.035); `#guard` checks that this single
  coefficient reproduces every other ARCA art. 30 amount to within one peso (derived, flagged).
* Employee contributions: Ley 24.241 art. 11 "aporte personal … once por ciento (11 %)"; Ley 19.032 art. 8 (d) "tres
  por ciento (3%)"; Ley 23.660 art. 16 (b) "tres por ciento (3%)". The maximum contribution base (Ley 24.241 art. 9,
  updated by ANSES) was not reached: no ceiling is applied (flagged; overstated above it).
W5 pattern A (2026-11-20): the SIPA personal contribution (11 %) is computed month by month on wages / 12 capped at
the base imponible máxima of Ley 24.241 art. 9 (texto Ley 26.222) as set by ANSES for each devengado month of 2025:
Res. 1247/2024 (enero 2.910.574,49), 66/2025 (febrero 2.989.160,00), 145/2025 (marzo 3.055.220,44), 179/2025 (abril
3.128.545,73), 211/2025 (mayo 3.245.240,49), 237/2025 (junio 3.335.458,18), 251/2025 (julio 3.385.490,05), 278/2025
(agosto 3.440.334,99), 298/2025 (septiembre 3.505.701,35), 317/2025 (octubre 3.571.608,54), 338/2025 (noviembre
3.645.898), 359/2025 (diciembre 3.731.212,01), each art. 3 (Boletín Oficial, `ar/law/w5/`). The INSSJP 3 % and obra
social 3 % stay on the whole wage (whether art. 9's maximum also binds them was not established here); the minimum
base, the SAC's own cap and the obra social's 1.5 % per extra dependant are not applied. `"w5Contrib": false` restores
the earlier outputs (17 % of all wages).
Unit: individual; children are deducted by one parent (the first adult; art. 30 (b) "el pariente más cercano que tenga
ganancias imponibles"). Money in centavos inside, whole pesos out.
-/

namespace ArTax
open TaxKernel

/-- art. 30 base amounts (Ley 27.743), pesos. -/
def baseMNI : Int := 3091035
/-- ARCA annual 2025 amounts, centavos. -/
def mni : Int := 450750552
def conyuge : Int := 424516613
def hijo : Int := 214085277
def especial2 : Int := 2163602650

/-- The IPC coefficient as ARCA applied it: 2025 amount / base amount (exact rational, centavos per peso). -/
def adj (pesos : Int) : Int := divR .halfUp (pesos * mni) baseMNI

/- One coefficient explains every published art. 30 amount (within one peso = 100 centavos): -/
#guard (adj 2911135 - conyuge).natAbs < 100 ∧ (adj 1468096 - hijo).natAbs < 100 ∧
  (divR .halfUp (48 * mni) 10 - especial2).natAbs < 100

/-- art. 94 scale, base amounts (Ley 27.743): limits in pesos and rates. -/
def baseLimits : List Int := [0, 1200000, 2400000, 3600000, 5400000, 10800000, 16200000, 24300000, 36450000]
def rates : List Int := [500, 900, 1200, 1500, 1900, 2300, 2700, 3100, 3500]
/-- Derived 2025 annual scale in centavos. -/
def sched : Schedule := Schedule.ofList ((baseLimits.map adj).zip rates)

/- The printed fixed sums of the base scale ("60.000,00", "168.000,00", …, "8.803.500,00") are the band sums: -/
def baseSched : Schedule := Schedule.ofList (baseLimits.zip rates)
#guard [(1200000, 60000), (2400000, 168000), (3600000, 312000), (5400000, 582000), (10800000, 1608000),
  (16200000, 2850000), (24300000, 5037000), (36450000, 8803500)].all fun (t, f) => baseSched.ticks t = f * BP

def contribRate : Int := 1700

/-- W5 pattern A: ANSES maximum monthly contribution bases for the devengado months of 2025, centavos. -/
def maxBase2025 : List Int := [291057449, 298916000, 305522044, 312854573, 324524049, 333545818, 338549005, 344033499,
  350570135, 357160854, 364589800, 373121201]
/-- Annual SIPA base (centavos): twelve equal monthly wages, each capped at that month's maximum. -/
def sipaBase (w : Int) : Int := sumInts (maxBase2025.map fun mx => min (pos w / 12) mx)
#guard maxBase2025.length = 12 ∧ sipaBase 1200000000 = 1200000000 ∧ sipaBase 12000000000 = sumInts maxBase2025

def personTax (wages self rental : Int) (married : Bool) (kids : Nat) (w5 : Bool := false) : Int × Int × Int :=
  let w := wages * 100
  let contrib := if w5 then divR .halfUp (1100 * sipaBase w + 600 * pos w) BP else divR .halfUp (contribRate * w) BP
  let net := w - contrib + self * 100 + rental * 100
  let famB := (if married then conyuge else 0) + hijo * kids
  -- art. 30 (c) 2: the special deduction is 'hasta una suma equivalente' to 3.8 x (a) 'cuando se trate de ganancias
  -- netas comprendidas en los incisos a), b) y c) del artículo 82': computed against the employee's own net wages,
  -- not against self-employment or rent (loophole round 2, 2026-11-21: it was the whole amount once wages > 0)
  let esp := if wages > 0 then min especial2 (pos (w - contrib)) else 0
  let twelfth := if wages > 0 then divR .down (mni + famB + esp) 12 else 0
  let ded := mni + famB + esp + twelfth
  let ti := pos (net - ded)
  (sched.tax (Rule.mk .halfUp 1) ti, ti, contrib)

def out (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  -- spouse deduction only if the spouse's own net income does not exceed the art. 30 (a) amount
  let spouseLow (j : Nat) : Bool := match c.adults[j]? with
    | some a => c.married && (a.wages + a.selfEmployment) * 100 ≤ mni
    | none => false
  let w5 := (c.bool? "w5Contrib").getD true
  let rs := (c.adults.zip (List.range n)).map fun (a, i) =>
    personTax a.wages a.selfEmployment (share c.rentalIncome i) (spouseLow (1 - i)) (if i = 0 then c.childrenUnder 18 else 0) w5
  let toP (x : Int) := divR .halfUp x 100
  Out.make c "AR" "ARS" (toP (sumInts (rs.map (·.1)))) (employeeSocial := toP (sumInts (rs.map (·.2.2))))
    (detail := [Out.d "taxableIncome" (toP (sumInts (rs.map (·.2.1))))])
    (unsupported := ["2025 art. 94 scale derived from ARCA's art. 30 amounts with the single IPC coefficient the law prescribes (ARCA's own scale table not reached)",
      (if w5 then "maximum base (Ley 24.241 art. 9, ANSES 2025 monthly values) applied to the 11 % only; INSSJP and obra social 3 % + 3 % on all wages; SAC cap and minimum base not applied" else "maximum contribution base (Ley 24.241 art. 9) not applied: contributions overstated above it"),
      "interest, dividends and capital gains (impuesto cedular, arts. 95-99) not modelled; excluded",
      "pensions (art. 82 (c), specific deduction of 8 haberes mínimos) not modelled",
      "self-employed: deducción especial art. 30 (c) 1 and autonomous contributions not modelled"])

def country : Country := { code := "AR", name := "Argentina (ganancias, cuarta categoría)", currency := "ARS", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Loophole round 2 (2026-11-21), LIG art. 30 (c) 2: one peso of wages no longer brings the 3.8 x special deduction to
self-employment income; an employee whose net wages exceed it keeps the whole amount (as before). Centavos. -/
#guard (personTax 1 20000000 0 false 0 true).2.1 + mni / 12 + 200 ≥ (personTax 0 20000000 0 false 0 true).2.1
#guard let w : Int := 100000000 * 100
  (personTax 100000000 0 0 false 0 true).2.1 =
    pos (w - divR .halfUp (1100 * sipaBase w + 600 * pos w) BP - (mni + especial2 + divR .down (mni + especial2) 12))

end ArTax
