import HnGlobal.Pit

/-!
# Honduras 2025: employer IHSS contributions (2200); INFOP grade C

Sources (`hn/law/`, ARCHIVE_INDEX.tsv):
* **Decreto 48-2024**, Ley para la Regulación de las Aportaciones y Cotizaciones del IHSS (La Gaceta 36,545, 28 May 2024,
  in force on publication, art. 4): **art. 1** IVM "la tasa de cotización será el tres punto cinco por ciento (3.5%) para
  el empleador, de dos puntos cinco por ciento (2.5%) para el trabajador ... Estos porcentajes se aplicarán sobre los
  techos de cotización vigentes para este régimen"; **art. 2** techos for 2025: IVM L. 11,903.13 and EM L. 11,903.13 (a
  month). Its considerandos record that the Sala Constitucional struck down the whole Ley Marco del Sistema de
  Protección Social (Decreto 56-2015; sentence published 27 Oct 2022).
* **Reglamento de Aplicación de la Ley del Seguro Social** (Acuerdo 193 of 17 Dec 1971, TSC and BVS copies) **art. 28**:
  enfermedad, accidente común, maternidad, accidente de trabajo y enfermedad profesional: "Los patronos ... aportarán una
  cotización equivalente al 5% de los salarios de sus trabajadores" (art. 31: rates may change by Junta Directiva
  agreement; no change found; the EM ceiling of Decreto 48-2024 art. 2 applies).
Each rate on the wage up to 12 x L. 11,903.13 = L. 142,837 a year (whole lempiras, down). The 13th and 14th month
salaries are not split from the wage (the 1.x model does not split them either). Not modelled: INFOP 1 % (Ley del
INFOP, not held: C row); RAP employer 1.5 % (Ley Marco struck down; the RAP is a privately managed individual-account
scheme, not a tax in the OECD sense).

**Pass 9 (2026-11-21):** INFOP 1 % modelled (3000) from the Ley del INFOP y sus reformas (IAIP portal PDF, Wayback 20251202; archived `hn/law/ley_infop_iaip_wb20251202.*`): art. 23 "Las empresas que ocupen cinco (5) o más trabajadores aportarán mensualmente ... el uno por ciento (1%) del monto de los sueldos y salarios devengados" (reworded by Decreto 194-2002 art. 11 to make it deductible), art. 24 the same for firms with capital above L. 20,000. Employer size is not an input: the employer is taken as within them.
-/

namespace HnGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon HnGlobal

/-- 12 x L. 11,903.13 (Decreto 48-2024 art. 2, 2025), whole lempiras down. -/
def techo : Int := 142837

def em : Contribution := Contribution.flatCapped "IHSS Enfermedad y Maternidad (patrono)" 500 techo
def ivm : Contribution := Contribution.flatCapped "IHSS Invalidez, Vejez y Muerte (patrono)" 350 techo

def sscF : Family := employerFamily "2200 IHSS employer contributions" [em, ivm] "Reglamento de Aplicación de la Ley del Seguro Social art. 28 (EM 5 %); Decreto 48-2024 art. 1 (IVM 3.5 %), art. 2 (techos 2025 L. 11,903.13 a month)"

def infop : Contribution := { name := "INFOP (patrono, 1 %)", sched := Schedule.flat 100 }
def infopF : Family := employerFamily "3000 INFOP" [infop] "Ley del INFOP (Decreto 10 de 1972) art. 23 as reformed by Decreto 194-2002 art. 11, art. 24: 1 % of wages earned" (inBp := 10000) (oecd := .payroll) (level := .central)

def families : List Family := [sscF, infopF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "IHSS employer EM 5 % and IVM 3.5 % on the wage up to 12 monthly ceilings (13th/14th month not split); INFOP 1 % on the whole wage (employer taken as having 5+ workers or capital above L. 20,000); RAP 1.5 % treated as non-tax"

#guard em.amount 100000 == 5000
#guard ivm.amount 100000 == 3500
#guard ivm.amount 1000000 == ivm.amount techo
#guard em.amount 1000000 == em.amount techo
#guard infop.amount 1000000 == 10000

end HnGlobal.Social
