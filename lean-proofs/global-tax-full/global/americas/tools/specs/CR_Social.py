S = dict(cc="CR", fam="Social",
doc=r'''# Costa Rica 2025: employer CCSS, Banco Popular and LPT contributions (2200); FODESAF, IMAS, INA (3000)

Sources (SINALEVI texts held by the 1.x builder, `world/B01-oecd5/cr/src/sinalevi/`, fetched 2026-11-20 from
sinalevi.go.cr; the CCSS site answers 403 and its Wayback copies hold no rate table):
* Reglamento del Seguro de Salud (Reglamento 7082, ficha 43463, versión 146812) **art. 62 (1) (b)**: "Patronos: 9.25% de
  los salarios de sus trabajadores".
* Reglamento del Seguro de Invalidez, Vejez y Muerte (Reglamento 6898, ficha 26485, versión 148515) **Transitorio XI**
  (a table published as an image, `ivm_trXI_002.jpg`, OCR): "Del 1° de enero del 2023 al 31 de diciembre del [2025] ...
  11,16% ... Patronos: 5,42% ... Trabajadores: 4,17%" (art. 33 gives the final 5.75 % from 2029).
* Ley 4351, Ley Orgánica del Banco Popular (ficha 35582) **art. 5 (a)**: "Un aporte del ½ % mensual sobre las
  remuneraciones, sean salarios o sueldos que deben pagar los patronos".
Base: the monthly salaries; the aguinaldo is not salary (Ley 2412), and the 1.x model's wage is 13 monthly salaries, so
12/13 of the annual wage is in the base (`inBp` 9231). No ceiling. Grade B (the IVM row read from an OCR of the table
image; the other payroll charges collected with the CCSS planilla are not modelled).''',
lean=r'''def sem : Contribution := { name := "CCSS Seguro de Salud (patrono)", sched := Schedule.flat 925 }
def ivm : Contribution := { name := "CCSS Invalidez, Vejez y Muerte (patrono)", sched := Schedule.flat 542 }
def bp : Contribution := { name := "Banco Popular (patrono)", sched := Schedule.flat 50 }
def sscF : Family := employerFamily "2200 CCSS and Banco Popular (employer)" [sem, ivm, bp] "Reglamento Seguro de Salud art. 62 (1) (b) 9.25 %; Reglamento IVM Transitorio XI 5.42 % (2023-2025); Ley 4351 art. 5 (a) 0.5 %; on the 12 monthly salaries" (inBp := 9231)
def fcl : Contribution := { name := "Fondo de Capitalización Laboral (patrono)", sched := Schedule.flat 150 }
def rop : Contribution := { name := "Régimen Obligatorio de Pensiones Complementarias (patrono)", sched := Schedule.flat 300 }
def lptF : Family := employerFamily "2200 Ley de Protección al Trabajador (employer)" [fcl, rop] "Ley 7983 art. 3 (FCL 1.5 %, Ley 9906 de 2020), art. 13 c) (ROP 3 %); on the 12 monthly salaries" (inBp := 9231)
def fodesaf : Contribution := { name := "FODESAF (Asignaciones Familiares)", sched := Schedule.flat 500 }
def imas : Contribution := { name := "IMAS", sched := Schedule.flat 50 }
def ina : Contribution := { name := "INA", sched := Schedule.flat 150 }
def payStatute : String := "Ley 5662 art. 15 b) 5 %; Ley 4760 art. 14 a) 0.5 %; Ley 6868 art. 15 a) 1.5 % (5 or more permanent workers); on the 12 monthly salaries"
def payF : Family :=
  { name := "3000 FODESAF, IMAS and INA (employer)", covers := [.payroll],
    run := fun _ g _ =>
      let cs := if g.entity == .company && 0 < g.company.employees && g.company.employees < 5 then [fodesaf, imas] else [fodesaf, imas, ina]
      if g.entity == .company then
        cs.map fun c => charge .payroll c.name g.company.payroll id (fun _ => payrollAmount (fun w => c.amount (baseShare 9231 w)) g.company)
          (event := "payroll") (bearer := .entity) (statute := payStatute)
      else
        (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).flatMap fun (a, i) =>
          cs.map fun c => charge .payroll c.name a.wages (baseShare 9231) (fun b => c.amount b)
            (event := s!"adult {i + 1}") (bearer := .employer) (statute := payStatute) }''',
families="[sscF, lptF, payF]",
unsupported=[["g.household.adults.any (·.wages > 0) || g.entity == .company", "employer CCSS 9.25 % + 5.42 %, Banco Popular 0.5 %, LPT 1.5 % + 3 %, FODESAF 5 %, IMAS 0.5 %, INA 1.5 % (households: INA applied, employer size unknown); agricultural INA rate, the minimum contribution base and the INS work-risk premium not applied"]],
guards=["sem.amount 120000 == 11100", "ivm.amount 120000 == 6504", "bp.amount 120000 == 600", "baseShare 9231 1300000 == 1200030", "fcl.amount 120000 == 1800", "rop.amount 120000 == 3600", "fodesaf.amount 120000 == 6000", "imas.amount 120000 == 600", "ina.amount 120000 == 1800"],
taxes=[dict(oecd="2200", tax="CCSS Seguro de Salud and IVM, Banco Popular (employer)", statute="Reglamento del Seguro de Salud art. 62; Reglamento IVM Transitorio XI; Ley 4351 art. 5 (a)", dated="SINALEVI versions fetched 2026-11-20 (Transitorio XI row 1 Jan 2023 - 31 Dec 2025)", grade="B", package="P4", kernel_parts=["employerFamily", "Contribution"], unsupported=["minimum contribution base"]),
 dict(oecd="2200", tax="Ley de Protección al Trabajador: FCL and ROP (employer)", statute="Ley 7983 arts. 3, 13 c) (Ley 9906 de 2020)", dated="SINALEVI version 145867 fetched 2026-11-21", grade="A", package="P4", kernel_parts=["employerFamily", "Contribution"]),
 dict(oecd="3000", tax="FODESAF, IMAS and INA (employer)", statute="Ley 5662 art. 15 b); Ley 4760 art. 14 a); Ley 6868 art. 15 a)", dated="SINALEVI versions 150444, 143291, 142854 fetched 2026-11-21", grade="A", package="P4", kernel_parts=["charge", "Contribution"], unsupported=["INA: employer size unknown for households (charged)", "agricultural INA rate"])])
