import ESTax.Params

/-!
# Employee social contributions (Orden PJC/178/2025) and rendimientos del trabajo (LIRPF arts. 17-20)
-/

namespace ESTax
open TaxKernel

/-! ## Seguridad Social, employee share -/

/-- Base de cotización: the annual wage capped at the base máxima (Orden PJC/178/2025 art. 1 norma tercera: "se
cotizará por la base ... máxima"). Annualised: the Orden works month by month; for a regular monthly wage the annual
sum is the same. The base mínima is not applied (full-time wages at or above the SMI exceed it). -/
def ssBase (w : Int) : Int := min (pos w) baseMaxima

/-- Each employee contribution, rounded to the cent separately: contingencias comunes, desempleo, formación
profesional, MEI. -/
def ssOrdinary (w : Int) : Int :=
  bpOf ssCC (ssBase w) + bpOf ssDesempleo (ssBase w) + bpOf ssFP (ssBase w) + bpOf ssMEI (ssBase w)

/-- Cotización adicional de solidaridad (LGSS art. 19 bis; Orden art. 17), worker share, on pay above the base
máxima. -/
def ssSolidaridad (w : Int) : Int :=
  bpOf solR1 (overlap 0 w baseMaxima solT1) + bpOf solR2 (overlap 0 w solT1 solT2) + bpOf solR3 (above 0 w solT2)

def ssEmployee (w : Int) : Int := ssOrdinary w + ssSolidaridad w

/-- Employer contributions used for the art. 81 bis.2 limit (lower bound: no AT/EP, no FOGASA). -/
def ssEmployerLB (w : Int) : Int := bpOf ssEmployer (ssBase w)

/-! ## Rendimiento neto del trabajo -/

/-- LIRPF art. 19.2 f), last paragraph: the 2.000 € "tendrán como límite el rendimiento íntegro del trabajo una vez
minorado por el resto de gastos deducibles". -/
def otrosGastosApplied (rit ss : Int) : Int := min otrosGastos (pos (rit - ss))

/-- LIRPF art. 20 (RDL 4/2024): the reducción by rendimiento neto `rnt` (art. 19.2 a)-e) only: "el rendimiento neto
del trabajo será el resultante de minorar el rendimiento íntegro en los gastos previstos en las letras a), b), c), d) y
e)") and the taxpayer's other income `otras` ("rentas, excluidas las exentas, distintas de las del trabajo").
Before the "saldo no podrá ser negativo" cap. -/
def red20 (rnt otras : Int) : Int :=
  if r20Limite ≤ rnt then 0
  else if r20Otras < otras then 0
  else if rnt ≤ r20T1 then r20Max
  else if rnt ≤ r20T2 then r20Max - mulDiv (rnt - r20T1) r20K1 100
  else pos (r20Mid - mulDiv (rnt - r20T2) r20K2 100)

/-- The same reducción before rounding, in hundredths of a cent (exact: 1,75 and 1,14 have two decimals). -/
def red20Exact (rnt otras : Int) : Int :=
  if r20Limite ≤ rnt then 0
  else if r20Otras < otras then 0
  else if rnt ≤ r20T1 then 100 * r20Max
  else if rnt ≤ r20T2 then 100 * r20Max - (rnt - r20T1) * r20K1
  else 100 * r20Mid - (rnt - r20T2) * r20K2

/-- LIRPF disp. adicional 61.ª (Ley 5/2025): the amount before its cuota limit, by the rendimientos íntegros del
trabajo from an employment relationship `w` and the other income `otras`. -/
def smiAmount (w otras : Int) : Int :=
  if smiLimite ≤ w then 0
  else if r20Otras < otras then 0
  else if w ≤ smiT1 then smiMax
  else pos (smiMax - mulDiv (w - smiT1) 2 10)


/-! ## The same, for any ejercicio (`YP`, round 5). The 2025 functions above are these at `yp2025` (`*_2025` theorems). -/

def ssBaseY (yp : YP) (w : Int) : Int := min (pos w) yp.baseMaxima

def ssOrdinaryY (yp : YP) (w : Int) : Int :=
  bpOf ssCC (ssBaseY yp w) + bpOf ssDesempleo (ssBaseY yp w) + bpOf ssFP (ssBaseY yp w) + bpOf yp.ssMEI (ssBaseY yp w)

/-- The cotización de solidaridad exists from 2025 only (its bands are the 2025 ones). -/
def ssSolidaridadY (yp : YP) (w : Int) : Int := if yp.solidaridad then ssSolidaridad w else 0

def ssEmployeeY (yp : YP) (w : Int) : Int := ssOrdinaryY yp w + ssSolidaridadY yp w

def ssEmployerLBY (yp : YP) (w : Int) : Int := bpOf yp.ssEmployer (ssBaseY yp w)

def red20Y (yp : YP) (rnt otras : Int) : Int :=
  if yp.r20Limite ≤ rnt then 0
  else if r20Otras < otras then 0
  else if rnt ≤ yp.r20T1 then yp.r20Max
  else if rnt ≤ yp.r20T2 then yp.r20Max - mulDiv (rnt - yp.r20T1) yp.r20K1 100
  else pos (yp.r20Mid - mulDiv (rnt - yp.r20T2) yp.r20K2 100)

def smiAmountY (yp : YP) (w otras : Int) : Int := if yp.da61 then smiAmount w otras else 0

theorem ssEmployeeY_2025 (w : Int) : ssEmployeeY yp2025 w = ssEmployee w := rfl
theorem ssEmployerLBY_2025 (w : Int) : ssEmployerLBY yp2025 w = ssEmployerLB w := rfl
theorem red20Y_2025 (rnt otras : Int) : red20Y yp2025 rnt otras = red20 rnt otras := rfl
theorem smiAmountY_2025 (w otras : Int) : smiAmountY yp2025 w otras = smiAmount w otras := rfl

end ESTax
