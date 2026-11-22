import CuGlobal.Pit

/-!
# Cuba 2025: Contribución a la Seguridad Social (2200), Impuesto por la Utilización de la Fuerza de Trabajo (3000)

Source: Ley 174 (2025 budget, GOC-2024-O127, 30/12/2024) with Ley 113.
* **art. 19.1**: "Se establece, para el ejercicio fiscal 2025, el catorce por ciento (14 %) como tipo impositivo de la
  Contribución a la Seguridad Social, exigible a las entidades y a los actores económicos no estatales … que empleen a
  los beneficiarios del régimen general" (base: Ley 113 art. 289, the wages paid).
* **art. 91**: "Se establece para el Impuesto por la Utilización de la Fuerza de Trabajo el cinco por ciento (5 %)
  como tipo impositivo para el año 2025" (Ley 113 art. 228: base the wages paid); art. 92 exempts agricultural
  cooperatives and state enterprises for farm staff (not modelled).
-/

namespace CuGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon CuGlobal

def css : Contribution := { name := "Contribución a la Seguridad Social", sched := Schedule.flat 1400 }
def fuerza : PayrollTax := { name := "Impuesto por la Utilización de la Fuerza de Trabajo", rateBp := 500 }
def sscF : Family := employerFamily "2200 Contribución a la Seguridad Social" [css] "Ley 174 (2025) art. 19.1 (14 %); Ley 113 art. 289"
def payF : Family := payrollFamily "3000 Impuesto por la Utilización de la Fuerza de Trabajo" fuerza "Ley 174 (2025) art. 91 (5 %); Ley 113 art. 228"

def families : List Family := [sscF, payF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0)) "employers with a differentiated regime (Ley 174 art. 19.3, Ley 118, Mariel) and the art. 92 exemptions not modelled"

#guard css.amount 100000 == 14000
#guard fuerza.amount 100000 == 5000

end CuGlobal.Social
