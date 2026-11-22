import VeGlobal.Pit

/-!
# Venezuela 2025: contribución especial para la protección de las pensiones (3000); IVSS, RPE, FAOV, INCES grade C

Sources (`ve/law/`, Gaceta Oficial copies from the Travieso Evans gazette archive, ARCHIVE_INDEX.tsv):
* **Ley de Protección de las Pensiones de Seguridad Social frente al Bloqueo Imperialista** (G.O. 6.806 Ext., 8 May 2024,
  in force on publication): **art. 6** the contribution falls on "personas jurídicas, así como cualesquiera otras
  sociedades de personas ... de carácter privado"; **art. 7** "hasta el quince por ciento (15%) del total de los pagos
  realizados por el contribuyente a las trabajadoras y trabajadores por concepto de salario y bonificaciones de carácter
  no salarial", the base for each worker never below the "ingreso mínimo integral indexado", the President fixes the
  percentage; **art. 10** deductible for ISLR; **art. 11** distinct from the IVSS contributions.
* **Decreto 4.952** (G.O. 42.880, 16 May 2024) **art. 1**: "el nueve por ciento (9%) del total de los pagos realizados por
  el contribuyente a las trabajadoras y trabajadores"; art. 2 exempts enterprises in the Registro Nacional de
  Emprendimientos. No later decree changing the 9 % was found.
Booked as 3000 (a levy on the payroll of private legal persons that gives the worker no entitlement). Charged at 9 % of
the whole wage (salary and non-salary bonuses: the canon has one wage figure), on a company's payroll and on each
adult's wages (the employer is taken to be a private legal person). The floor of the ingreso mínimo integral per worker is
not applied. Not modelled (C row): IVSS employer contributions (Ley del Seguro Social, 9-11 % by risk class to 5 minimum
wages), Régimen Prestacional de Empleo 2 %, FAOV 2 %, INCES 2 %: their texts are not held.

**Pass 9 (2026-11-21):** FAOV read in the 2024 texto único of the Ley del Régimen Prestacional de Vivienda y Hábitat (G.O. 6.805 Ext.; archived `ve/law/go6805_lrpvh_2024.*`) art. 33: 3 % of the salario integral into the worker's individual savings account, two thirds by the employer. A compulsory saving credited to the worker (like Brazil's FGTS) is not a tax in the OECD classification: recorded as a cited non-tax row, not charged. IVSS, RPE and INCES stay C.
-/

namespace VeGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon VeGlobal

def lpp : Contribution := { name := "Contribución especial para la protección de las pensiones", sched := Schedule.flat 900 }

def lppF : Family := employerFamily "3000 contribución especial (Ley de Protección de las Pensiones)" [lpp] "Ley de Protección de las Pensiones de Seguridad Social (G.O. 6.806 Ext., 2024) arts. 6, 7; Decreto 4.952 (G.O. 42.880, 2024) art. 1: 9 %" (oecd := .payroll) (level := .central)

def families : List Family := [lppF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "pension-protection contribution 9 % on the whole wage, employer taken as a private legal person (public employers and registered emprendimientos are outside); per-worker floor (ingreso mínimo integral) not applied; IVSS, RPE and INCES employer contributions not modelled; FAOV 2 % is compulsory saving (outside tax)"

#guard lpp.amount 1000000 == 90000

end VeGlobal.Social
