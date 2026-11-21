import TaxKernel.World

/-!
# Cuba: Impuesto sobre los Ingresos Personales and Contribución Especial a la Seguridad Social, 2025 (access B)

Sources (Gaceta Oficial de la República de Cuba, gacetaoficial.gob.cu; files in `cu/law/`):
* Ley 113 "Del Sistema Tributario", text "Anotada y Concordada" (G.O. Edición Especial No. 1 de 2021, GOC-2021-152-ES1,
  `goc-2021-es1.pdf`): art. 19 g) "los salarios" are taxable income; art. 20: base = income of the fiscal year less
  "a) el mínimo exento ... c) los tributos pagados, excepto el Impuesto sobre Ingresos Personales"; art. 22 (as
  modified by Decreto-Ley 21/2020): "mínimo exento anual ... treinta y nueve mil ciento veinte pesos cubanos (39 120.00
  CUP)"; art. 26: "la siguiente escala progresiva expresada en CUP: Hasta 10 000.00 15 %; El exceso de 10 000.00 hasta
  20 000.00 20 %; ... 20 000.00 hasta 30 000.00 30 %; ... 30 000.00 hasta 50 000.00 40 %; El exceso de 50 000.00 50 %".
* Ley 174 "Del Presupuesto del Estado para el Año 2025" (G.O. No. 127 Ordinaria de 2024, GOC-2024-713-O127,
  30/12/2024): art. 20.2: Contribución Especial a la Seguridad Social "un cinco por ciento (5 %) por los ingresos de
  hasta quince mil pesos mensuales; por el exceso de quince mil pesos mensuales se aplica un tipo impositivo del diez
  por ciento (10 %)"; art. 67.1: "Aplicar en el año 2025, a los trabajadores de todos los sectores, el pago del
  Impuesto sobre los Ingresos Personales por las remuneraciones salariales"; art. 65: a different 5-50 % scale for
  the 2024 declarations of artists, self-employed and others (not wage earners).
The monthly withholding scale that applies the tax to salaries was not found in these texts (an MFP resolution was not
reached). Reading (documented switch `cuWageTax`): "annual" (default) applies arts. 20, 22 and 26 to wages as the Law
writes them; "none" gives zero income tax on wages.
-/

namespace CuTax
open TaxKernel

/-- Ley 113 art. 26. -/
def sched : Schedule := Schedule.ofList [(0, 1500), (10000, 2000), (20000, 3000), (30000, 4000), (50000, 5000)]

def minimoExento : Int := 39120

/-- Ley 174 art. 20.2: 5 % of monthly income up to 15,000 and 10 % of the excess. -/
def cessMonth (m : Int) : Int := divR .down (500 * min (pos m) 15000 + 1000 * pos (m - 15000)) 10000

structure Person where
  cess : Int
  base : Int
  tax : Int

def person (a : Adult) (annual : Bool) : Person :=
  let w := pos a.wages
  let cess := perPeriod 12 cessMonth w
  let base := pos (w - minimoExento - cess)
  { cess := cess, base := base, tax := if annual then sched.tax Rule.unitDown base else 0 }

def out (c : Canon) : Out :=
  let annual := c.str? "cuWageTax" != some "none"
  let ps := c.adults.map (fun a => person a annual)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employed (trabajadores por cuenta propia): Ley 174 art. 65 scale and quotas not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["other income not modelled"] else [])
  Out.make c "CU" "CUP" (sumInts (ps.map (·.tax))) (employeeSocial := sumInts (ps.map (·.cess)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.base))), Out.d "contribucionEspecial" (sumInts (ps.map (·.cess))),
      Out.dStr "reading" (if annual then "annual: Ley 113 arts. 20, 22, 26 applied to wages" else "none: no income tax on wages"),
      Out.dStr "note" "Contribucion Especial a la Seguridad Social 5 %/10 % at 15,000 a month (Ley 174 art. 20.2), deductible as a tributo (art. 20 c))"])
    (unsupported := unsup ++ ["the monthly withholding scale for salaries (MFP resolution) was not reached: income tax per the reading in detail",
      "wages assumed paid evenly over 12 months"])

def country : Country := { code := "CU", name := "Cuba (Ley 113 Del Sistema Tributario; Ley 174 presupuesto 2025)", currency := "CUP", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard sched.tax Rule.unitDown 50000 = 14500
#guard cessMonth 15000 = 750
#guard cessMonth 20000 = 1250

end CuTax
