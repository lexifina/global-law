import EcGlobal.Pit

/-!
# Ecuador 2025: employer IESS contribution (2200)

Source: IESS Resolución C.D. 515 (30 Mar 2016; IESS compilation "texto histórico ilustrativo", held by the 1.x builder
`world/B12-latin-america/ec/law/w5/iess_resolucion_CD515_2016.pdf`), **Disposición Transitoria Primera**, private-sector
dependent workers: "Total Aportes 9,45 (personal) 11,15 (patronal) 20,60" (pensiones 0.10, salud 9.06, riesgos del
trabajo 0.20, desempleo 1.00, Seguro Social Campesino 0.35, gastos de administración 0.44). The 1.x model charges the
personal 9.45 % from the same table. Grade B: later C.D. resolutions were not checked; the décimo tercero and cuarto
sueldos are outside the IESS base but the 1.x wage is not split (applied to the whole wage).
-/

namespace EcGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon EcGlobal

def iess : Contribution := { name := "IESS aporte patronal", sched := Schedule.flat 1115 }
def fam1 : Family := employerFamily "2200 IESS employer contribution" [iess] "IESS Resolución C.D. 515 Disposición Transitoria Primera: aporte patronal 11.15 %" (inBp := 10000) (oecd := .sscEmployer) (level := .social)

def families : List Family := [fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "IESS employer 11.15 % (C.D. 515) on the whole wage (décimo tercero/cuarto not split out; later C.D. resolutions not checked)"

#guard iess.amount 1000000 == 111500

end EcGlobal.Social
