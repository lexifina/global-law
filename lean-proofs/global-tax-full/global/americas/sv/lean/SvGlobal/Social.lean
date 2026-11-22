import SvGlobal.Pit

/-!
# El Salvador 2025: employer pension contribution (2200); ISSS grade C

Source: Ley Integral del Sistema de Pensiones (D.L. 614 of 20 Dec 2022, D.O. 241 of 21 Dec 2022; SSF-hosted copy,
fetched 2026-11-21) **art. 16**: "La tasa de cotización del Sistema será del dieciséis por ciento (16%) sobre el ingreso
base de cotización, correspondiendo el siete punto veinticinco por ciento (7.25%) al trabajador y el ocho punto setenta
y cinco por ciento (8.75%) al empleador"; **art. 14**: the base is the monthly salary, not below the minimum wage; the
aguinaldo and occasional bonuses are outside it (not split from the 1.x wage). No maximum base in the article.
Not modelled (separate C row): ISSS employer 7.5 % (Reglamento para la Aplicación del Régimen del Seguro Social, not
held) and INSAFORP 1 %.

**Pass 9 (2026-11-21):** INSAFORP modelled (3000, A): Ley de Formación Profesional art. 26 c) (UES consolidation, archived `sv/law/ley_formacion_profesional_ues.*`), "hasta el 1%" of the monthly payroll for private employers with 10 or more workers, taken at 1 % on the whole wage. ISSS stays C: Ley del Seguro Social art. 29 (employer 7.50 %) is read in the ISSS 2019 compilation (Wayback 20220310, archived `sv/law/isss_ley_2019_wb20220310.*`), but its Reglamento art. 3 still shows the colón ceiling (C 700 a month, D.E. 54/1986); the dollar ceiling in force in 2025 was not reached (live compilation 403 on a polite retry).
-/

namespace SvGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon SvGlobal

def afp : Contribution := { name := "Cotización previsional (empleador)", sched := Schedule.flat 875 }
def fam1 : Family := employerFamily "2200 pension contribution (employer)" [afp] "Ley Integral del Sistema de Pensiones art. 16: 8.75 % employer" (inBp := 10000) (oecd := .sscEmployer) (level := .social)

def insaforp : Contribution := { name := "INSAFORP (patrono, 1 %)", sched := Schedule.flat 100 }
def fam2 : Family := employerFamily "3000 INSAFORP" [insaforp] "Ley de Formación Profesional (D.L. 554/1993) art. 26 c): up to 1 % of the monthly payroll, employers of 10 or more workers" (inBp := 10000) (oecd := .payroll) (level := .central)

def families : List Family := [fam1, fam2]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "employer pension 8.75 % (LISP art. 16) on the whole wage (aguinaldo not split); INSAFORP at its 1 % maximum (employer taken as having 10+ workers, not agricultural); ISSS 7.5 % (Ley del Seguro Social art. 29) not modelled: its current ceiling (Reglamento art. 3) not read (lower bound)"

#guard afp.amount 1000000 == 87500
#guard insaforp.amount 1000000 == 10000

end SvGlobal.Social
