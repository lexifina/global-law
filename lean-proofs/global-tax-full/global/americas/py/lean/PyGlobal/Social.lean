import PyGlobal.Pit

/-!
# Paraguay 2025: employer IPS contribution (2200)

Source: IPS "Tabla N° 1 de bases mínimas imponibles y porcentajes de aportes al IPS" (Régimen General, Salud +
Jubilación y Pensión), headed Resolución MTESS N° 670/2026, image held by the 1.x builder
(`world/B12-latin-america/py/src/ips_tabla_1786135176.jpg`, OCR): "TRABAJADOR 9% | EMPLEADOR 16,5%". The employee 9 %
is the 1.x model's 2025 rate. The table's footnote quotes the Carta Orgánica: the salary for contributions excludes the
aguinaldo; the 1.x wage is not split, so the whole wage is the base. Grade B (official table dated 2026; Ley 98/1992
not read).
-/

namespace PyGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon PyGlobal

def ips : Contribution := { name := "IPS aporte patronal", sched := Schedule.flat 1650 }
def fam1 : Family := employerFamily "2200 IPS employer contribution" [ips] "IPS Tabla N° 1 (Res. MTESS 670/2026): empleador 16.5 %" (inBp := 10000) (oecd := .sscEmployer) (level := .social)

def families : List Family := [fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "IPS employer 16.5 % on the whole wage (aguinaldo outside the IPS salary, not split); table dated 2026, Ley 98/1992 not read"

#guard ips.amount 1000000 == 165000

end PyGlobal.Social
