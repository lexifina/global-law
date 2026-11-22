import GtGlobal.Pit

/-!
# Guatemala 2025: employer IGSS contributions (2200)

Sources (IGSS Junta Directiva regulations, compilations held by the 1.x builder `world/B12-latin-america/gt/law/w5/`):
* **Acuerdo 410 art. 62 a)** (Enfermedad, Maternidad; rev. 2018): "Los patronos particulares y el Estado como patrono, el
  4 % del total de salarios de sus trabajadores".
* **Acuerdo 1002 art. 46 a)** (Accidentes): "el 3% del total de los salarios de sus trabajadores".
* **Acuerdo 1124 art. 40 a)** (Invalidez, Vejez y Sobrevivencia; rev. 2021): "el 3.67% del total de salarios".
Total 10.67 % with no ceiling, on the whole wage as the 1.x model's employee 4.83 % (aguinaldo and Bono 14 not split).


Pass 6: payroll levies collected with the IGSS (3000):
* **INTECAP**, Ley Orgánica, Decreto 17-72 (text on the UNESCO SITEAL site, `gt/law/intecap_decreto_17-72.pdf`) **art.
  28**: "una tasa patronal que será pagada mensualmente por las empresas y entidades privadas ... sobre la totalidad de las
  planillas de sueldos y salarios"; industry, commerce and services "a partir del 1º de enero de 1974 podrá alcanzar su
  límite máximo del 1.00%" (agricultural firms with under 10 permanent workers exempt; art. 29 non-profits and
  universities exempt). Applied at 1 %. Grade A.
* **IRTRA**, Decreto 1528 art. 12 as amended by Decreto 43-92 (Justia Guatemala summary of the amending decree,
  `gt/law/irtra_decreto_43-92_justia.html`): "un impuesto equivalente al 1%, sobre el monto del sueldo o salario ordinario
  y extraordinario, devengado mensualmente por cada trabajador de las empresas privadas, porcentaje que será calculado
  sobre la totalidad de las planillas". The decree text itself was not read: grade B.
Both on the whole wage (employer taken as a private firm).
-/

namespace GtGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon GtGlobal

def em : Contribution := { name := "IGSS Enfermedad y Maternidad (patrono)", sched := Schedule.flat 400 }
def acc : Contribution := { name := "IGSS Accidentes (patrono)", sched := Schedule.flat 300 }
def ivs : Contribution := { name := "IGSS IVS (patrono)", sched := Schedule.flat 367 }
def fam1 : Family := employerFamily "2200 IGSS employer contributions" [em, acc, ivs] "IGSS Acuerdo 410 art. 62 a) 4 %; Acuerdo 1002 art. 46 a) 3 %; Acuerdo 1124 art. 40 a) 3.67 %" (inBp := 10000) (oecd := .sscEmployer) (level := .social)
def intecap : Contribution := { name := "INTECAP tasa patronal", sched := Schedule.flat 100 }
def irtra : Contribution := { name := "IRTRA (1 %)", sched := Schedule.flat 100 }
def fam2 : Family := employerFamily "3000 INTECAP and IRTRA" [intecap, irtra] "Decreto 17-72 art. 28 (INTECAP 1 %); Decreto 1528 art. 12 as amended by Decreto 43-92 (IRTRA 1 %)" (inBp := 10000) (oecd := .payroll) (level := .central)

def families : List Family := [fam1, fam2]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "IGSS employer 10.67 %, INTECAP 1 % and IRTRA 1 % on the whole wage (aguinaldo/Bono 14 not split; employer taken as a private firm)"

#guard em.amount 1000000 == 40000
#guard acc.amount 1000000 == 30000
#guard ivs.amount 1000000 == 36700
#guard intecap.amount 1000000 == 10000
#guard irtra.amount 1000000 == 10000

end GtGlobal.Social
