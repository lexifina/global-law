import PeGlobal.Pit

/-!
# Peru 2025: ESSALUD employer contribution (2200)

Source: Ley 26790, Ley de Modernización de la Seguridad Social en Salud (El Peruano 17 May 1997; leyes.congreso.gob.pe
PDF, OCR `pe/law/ley26790.ocr.txt`). **art. 6 a)**: "El aporte de los trabajadores en actividad ... equivale al 9% de
la remuneración o ingreso. Es de cargo de la entidad empleadora". Grade B (the 1997 text; the later floor of the base at
the minimum wage (RMV) is not applied).
-/

namespace PeGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon PeGlobal

def essalud (w : Int) : Int := divR .down (900 * pos w) BP
def sscF : Family := employerFamily "2200 ESSALUD (employer)" [{ name := "ESSALUD", sched := Schedule.flat 900 }] "Ley 26790 art. 6 a): 9 % of the remuneration, de cargo de la entidad empleadora"

def families : List Family := [sscF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "ESSALUD 9 % on the wage (no minimum base); SCTR and the employer's EPS credit not modelled"

#guard essalud 100000 == 9000

end PeGlobal.Social
