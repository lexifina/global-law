import BoGlobal.Pit

/-!
# Bolivia 2025: employer contributions (2200) and the housing contribution (3000)

Sources: Ley 065 de Pensiones (APS "texto actualizado a noviembre de 2019", held by the 1.x builder
`world/B12-latin-america/bo/law/w5/aps_ley_065_pensiones_2019.pdf`) and D.S. 778 (Reglamento de contribuciones, same
folder):
* **Ley 065 art. 94 II**: "El Empleador tiene la obligación de realizar el Aporte Patronal Solidario correspondiente al
  tres por ciento (3%) sobre el Total Ganado de sus Asegurados Dependientes".
* **Ley 065 art. 83 a)**: "Prima por Riesgo Profesional, a cargo del Empleador, calculada sobre el Total Ganado"; rate
  1,71 % in the D.S. 778 annex table ("Prima por Riesgo Profesional 1,71 % APLICA" for dependants under 65).
Pass 6 (texts from lexivox.org, `bo/law/`, ARCHIVE_INDEX.tsv):
* **Ley 924 of 15 Apr 1987 art. 3**: "El régimen de enfermedad, maternidad y riesgo profesionales a corto plazo será
  financiado en su totalidad con el aporte patronal del diez por ciento (10%) del total ganado de sus asegurados" (D.S.
  26908 of 2002 repeats it). Booked as 2200 (Caja Nacional de Salud).
* **D.S. 28794 of 12 Jul 2006 art. 3**: "Los aportes del 2% patronal público y privado, destinados a vivienda de interés
  social, continuarán siendo aportados por los empleadores en el mismo porcentaje" (Programa de Vivienda Social y
  Solidaria). Booked as 3000 (a payroll levy that gives the worker no individual benefit).
All on the whole wage (total ganado). Workers aged 65 and over (no risk premium) not distinguished.
-/

namespace BoGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon BoGlobal

def aps : Contribution := { name := "Aporte Patronal Solidario", sched := Schedule.flat 300 }
def rp : Contribution := { name := "Prima por Riesgo Profesional", sched := Schedule.flat 171 }
def fam1 : Family := employerFamily "2200 employer pension contributions (Ley 065)" [aps, rp] "Ley 065 art. 94 II (3 %), art. 83 a) and D.S. 778 annex (1.71 %)" (inBp := 10000) (oecd := .sscEmployer) (level := .social)
def cns : Contribution := { name := "Caja Nacional de Salud (aporte patronal)", sched := Schedule.flat 1000 }
def fam2 : Family := employerFamily "2200 employer health contribution (Ley 924)" [cns] "Ley 924 de 1987 art. 3: aporte patronal 10 % del total ganado" (inBp := 10000) (oecd := .sscEmployer) (level := .social)
def viv : Contribution := { name := "Aporte patronal para vivienda", sched := Schedule.flat 200 }
def fam3 : Family := employerFamily "3000 employer housing contribution (D.S. 28794)" [viv] "D.S. 28794 de 2006 art. 3: aporte patronal 2 %" (inBp := 10000) (oecd := .payroll) (level := .central)

def families : List Family := [fam1, fam2, fam3]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "employer contributions on the whole wage: Aporte Patronal Solidario 3 %, risk premium 1.71 % (workers 65+ not distinguished), health 10 %, housing 2 %"

#guard aps.amount 1000000 == 30000
#guard rp.amount 1000000 == 17100
#guard cns.amount 1000000 == 100000
#guard viv.amount 1000000 == 20000

end BoGlobal.Social
