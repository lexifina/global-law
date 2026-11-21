import ESTax.Household

/-!
# Withholding on wages (RIRPF arts. 80-86, RD 439/2007 as in force in 2025) and the AEAT algorithm

Text: `law/rirpf_withholding.md` (Global law, BOE consolidated; arts. 81, 83, 84, 85, 86 as in force on
2025-06-30: art. 81 and 83.3 d) last changed by RD 142/2024, art. 85 by RD 1039/2022, art. 86 by RD 31/2023).
Referee: the AEAT's published "Algoritmo de cálculo del tipo de retención" (`refs/ALGORITMO_2026.pdf`, the
document the AEAT publishes for payroll software; its 2025 counterpart is no longer online; the 2026 text lists no
change to the general procedure since RD 142/2024).

Scope: one payer, ordinary contract ("GENERAL"), wages only (SITUPER = ACTIVO), no pensión compensatoria or
anualidades, no disability, no housing-loan reduction, resident outside Ceuta/Melilla/La Palma.

The two places where the algorithm fixes something the regulation leaves open are parameters here:
* art. 86.1 "se expresará con dos decimales": the AEAT truncates ("TRUNCAR (TIPO)"); `truncate := false` rounds half up.
* the cuota is computed with all decimals ("Todas las variables ... con el máximo número de decimales"): ticks here.
-/

namespace ESTax
open TaxKernel

/-- RIRPF art. 85.1 1.º (RD 899/2021): "0,00 | 0,00 | 12.450,00 | 19,00 / 12.450,00 | 2.365,50 | 7.750,00 | 24,00 /
20.200,00 | 4.225,50 | 15.000,00 | 30,00 / 35.200,00 | 8.725,50 | 24.800,00 | 37,00 / 60.000,00 | 17.901,50 |
240.000,00 | 45,00 / 300.000,00 | 125.901,50 | En adelante | 47,00". -/
def escalaRetencion : List Row :=
  [⟨0, 0, 1900⟩, ⟨1245000, 236550, 2400⟩, ⟨2020000, 422550, 3000⟩, ⟨3520000, 872550, 3700⟩,
   ⟨6000000, 1790150, 4500⟩, ⟨30000000, 12590150, 4700⟩]

/-- RIRPF art. 81.1 (RD 142/2024): "Límite cuantitativo excluyente de la obligación de retener", by situation (1, 2, 3)
and number of descendants (0, 1, 2 or more). Situation 1 with no descendants does not exist ("–"). -/
def limiteExcluyente (sit : Nat) (nd : Nat) : Option Int :=
  match sit, nd with
  | 1, 0 => none
  | 1, 1 => some (eur 17644)
  | 1, _ => some (eur 18694)
  | 2, 0 => some (eur 17197)
  | 2, 1 => some (eur 18130)
  | 2, _ => some (eur 19262)
  | _, 0 => some (eur 15876)
  | _, 1 => some (eur 16342)
  | _, _ => some (eur 16867)

/-- RIRPF art. 83.3 d): the art. 20 amounts on the rendimiento neto after letters a) and b) only, with no condition on
other income (the payer cannot know it), "sin que dicha reducción pueda ser superior a la cuantía de dicho rendimiento
neto". -/
def red83d (rnt : Int) : Int := min (red20 rnt 0) (pos rnt)

structure WhIn where
  wages : Int
  /-- art. 81.1 situación: 1 single parent with the 84.2 4.º reduction, 2 spouse with rentas ≤ 1.500 €, 3 other -/
  sit : Nat
  /-- descendants giving the mínimo -/
  nd : Nat
  /-- mínimo personal y familiar for withholding (art. 84: descendants by half unless exclusive) -/
  minPF : Int
  deriving Repr, Inhabited

structure WhOut where
  base : Int
  cuotaTicks : Int
  tipoBp : Int        -- tipo de retención in hundredths of a percent (= bp)
  importe : Int       -- cents
  exento : Bool
  deriving Repr, Inhabited

def withholding (w : WhIn) (truncate : Bool := true) : WhOut :=
  let r := w.wages
  let cot := ssEmployee r
  let rnt := pos (r - cot)
  let otros := min otrosGastos rnt
  let red := red83d rnt
  let hijos := if w.nd > 2 then eur 600 else 0         -- art. 83.3 e) "más de dos descendientes ... 600 euros"
  let base := pos (rnt - otros - red - hijos)
  let lim := limiteExcluyente w.sit w.nd
  let exento := match lim with
    | some l => r ≤ l
    | none => false
  if exento || r ≤ 0 then { base, cuotaTicks := 0, tipoBp := 0, importe := 0, exento := true } else
  let c1 := if base ≤ 0 then 0 else tableTicks escalaRetencion base
  let c2 := if w.minPF ≤ 0 then 0 else tableTicks escalaRetencion w.minPF
  let c := pos (c1 - c2)
  -- art. 85.3: total retribución ≤ 35.200 € → cuota ≤ 43 % of the excess over the art. 81 limit
  let c := match lim with
    | some l => if r ≤ eur 35200 then min c (4300 * pos (r - l)) else c
    | none => c
  let tipo := if truncate then c / r else divR .halfUp c r
  { base, cuotaTicks := c, tipoBp := tipo, importe := divR .halfUp (r * tipo) BP, exento := false }

/-- The household's withholding inputs for adult `i` (one payer each). -/
def HH.whIn (h : HH) (i : Nat) : WhIn :=
  let couple := h.n == 2
  let spouseInc := if couple then h.wages.getD (1 - i) 0 + h.pensions.getD (1 - i) 0 + h.selfEmp.getD (1 - i) 0 else 0
  let sit := if !couple && h.kids.length > 0 && h.minors > 0 then 1
    else if couple && h.married && spouseInc ≤ eur 1500 then 2 else 3
  let desc := if couple then half1 h.descEst else h.descEst
  { wages := h.wages.getD i 0, sit, nd := h.kids.length, minPF := minPersonal (h.ages.getD i 40) + desc }

/-- Adult 0's inputs (for theorems). -/
def HH.whIn0 (h : HH) : WhIn := h.whIn 0

end ESTax
