import PaGlobal.Pit

/-!
# Panama 2025: employer CSS quota (2200)

Source: Ley 462 de 18 de marzo de 2025 (Gaceta Oficial Digital 30238, page 51 held by the 1.x builder, OCR
`world/B12-latin-america/pa/law/w5/gaceta_30238_p51_art84_ocr.txt`) **art. 84**, replacing **Ley 51 de 2005 art. 101**:
"2. La cuota pagada por los empleadores, la cual será: a. A partir de la entrada en vigencia de la presente Ley y hasta
el 28 de febrero de 2027, el equivalente a 13.25 % de los sueldos que paguen a sus empleados" (14.25 % from 1 March
2027, 15.25 % from 1 March 2029). The employee quota of the same article, 9.75 %, is the 1.x model's.
Applied to the whole annual wage for the whole of 2025. Grade B: the vigencia article of Ley 462 and the employer rate
in force before it (January to mid-March 2025) were not read; the "contribución especial" of 10.75 % on the thirteenth
month (same article, para. 4), the riesgos profesionales premium (by risk class) and the Seguro Educativo (Decreto de
Gabinete 168 de 1971) are not modelled.

**Pass 9 (2026-11-21):** Ley 462 art. 244 (whole G.O. 30238 OCR'd, `p9/work/pa/ley462_gaceta30238.ocr.txt`): "Esta Ley comenzará a regir desde su promulgación" (18 Mar 2025). The employer rate before it was not read: 13.25 % still applied to the whole year (B).

**Pass 13 (2026-11-21): 2025 split at 18 March.** The text in force from 1 January to 17 March 2025 is Ley 51 de 2005
art. 101 (2) (d) as consolidated by the CSS ("Edición actualizada y comentada a febrero de 2024", Wayback 2026-02-02,
`pa/law/ley51_2005_css_version_2024.*`): "d. A partir del 1 de enero de 2013, el equivalente a doce punto veinticinco
(12.25%) de los sueldos que paguen a sus empleados". Amendment check: the CSS Texto Único (G.O. 30284-B of 22 May 2025,
`pa/law/ley51_2005_texto_unico_go_2025-05-22.*`) lists the reforming laws as Ley 2 de 2007, Ley 70 de 2011, Ley 45 de 2017,
Ley 419 de 2024 (1 Feb 2024, already in the February 2024 edition) and Ley 462 de 2025: no law changed art. 101 between the
2024 edition and Ley 462. Ley 462 art. 84 (now art. 96 (2) (a) of the Texto Único: 13.25 % "a partir de la entrada en
vigencia de la presente Ley") applies from promulgation, 18 March 2025 (art. 244). The annual wage is split by days:
1 Jan-17 Mar = 76 days at 12.25 %, 18 Mar-31 Dec = 289 days at 13.25 % (an undated annual wage; the quota is due on the
salaries paid in each month).
-/

namespace PaGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon PaGlobal

def css : Contribution := { name := "CSS cuota patronal", sched := Schedule.flat 1325 }
def cssOld : Contribution := { name := "CSS cuota patronal (1 Jan-17 Mar 2025, 12.25 %)", sched := Schedule.flat 1225 }
def cssNew : Contribution := { name := "CSS cuota patronal (18 Mar-31 Dec 2025, 13.25 %)", sched := Schedule.flat 1325 }

/-- The part of a 2025 annual wage earned in a window of `d` days (76 + 289 = 365). -/
def dayPart (d w : Int) : Int := divR .down (pos w * d) 365

/-- `employerFamily` with one day window per contribution. -/
def splitFamily (fname statute : String) (parts : List (Contribution × Int)) : Family :=
  { name := fname, covers := [.sscEmployer],
    run := fun _ g _ =>
      if g.entity == .company then
        parts.map fun (c, d) => charge .sscEmployer c.name g.company.payroll id
          (fun _ => payrollAmount (fun w => c.amount (dayPart d w)) g.company)
          (event := "payroll") (level := .social) (bearer := .entity) (statute := statute)
      else
        (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).flatMap fun (a, i) =>
          parts.map fun (c, d) => charge .sscEmployer c.name a.wages (dayPart d) (fun b => c.amount b)
            (event := s!"adult {i + 1}") (level := .social) (bearer := .employer) (statute := statute) }

def fam1 : Family := splitFamily "2200 CSS employer quota"
  "Ley 51 de 2005 art. 101 (2) (d): 12.25 % of salaries to 17 Mar 2025; art. 101 (2) (a) as replaced by Ley 462 de 2025 art. 84 (in force 18 Mar 2025, art. 244): 13.25 %; annual wage split by days 76/289"
  [(cssOld, 76), (cssNew, 289)]

def families : List Family := [fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "CSS employer quota: the annual wage is split by days (76 at 12.25 %, 289 at 13.25 %), not by the salaries actually paid in each month; thirteenth-month special contribution 10.75 % (art. 101 (4)), riesgos profesionales and Seguro Educativo not modelled"

#guard css.amount 1000000 == 132500
#guard dayPart 76 36500000 == 7600000
#guard dayPart 289 36500000 == 28900000
#guard cssOld.amount 7600000 == 931000
#guard cssNew.amount 28900000 == 3829250

end PaGlobal.Social
