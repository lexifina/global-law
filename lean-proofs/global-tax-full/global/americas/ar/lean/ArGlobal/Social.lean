import ArGlobal.Pit

/-!
# Argentina 2025: employer contributions to the national social security subsystems (2200); obra social and ART grade C

Source: Ley 27.541 (Ley de Solidaridad Social y Reactivación Productiva), texto actualizado, InfoLEG (fetched 2026-11-21;
`ar/law/ley27541_texact.htm`). Grade A.
* **art. 19**: the employer contributions to INSSJP (ley 19.032), Fondo Nacional de Empleo (24.013), SIPA (24.241) and
  Asignaciones Familiares (24.714): "a) Veinte con cuarenta centésimos (20,40%) para los empleadores pertenecientes al
  sector privado cuya actividad principal encuadre en el sector 'Servicios' o en el sector 'Comercio' ... siempre que sus
  ventas totales anuales superen ... empresa mediana tramo 2 ...; b) Dieciocho por ciento (18%) para los restantes
  empleadores pertenecientes al sector privado". The employer's sector and size are not in the line: 18 % (flagged).
* **art. 22**: "se detraerá mensualmente, por cada uno de los trabajadores, un importe de pesos siete mil tres con
  sesenta y ocho centavos ($ 7.003,68)", and 50 % of it from each semi-annual SAC installment: 13 x 7,003.68 =
  91,047.84 a year when the annual wage includes the SAC (read so). No ceiling applies to employer contributions.

Obra social (added in pass 3): Ley 23.660 (Obras Sociales), texto actualizado InfoLEG (`ar/law/ley23660_texact.htm`,
fetched 2026-11-21) **art. 16 a)**: "Una contribución a cargo del empleador equivalente al seis por ciento (6%) de la
remuneración de los trabajadores que presten servicios en relación de dependencia". Charged on the whole wage (SAC
included), without the art. 22 detracción of Ley 27.541 (which applies to the art. 19 contributions). Grade A. The ART
(riesgos del trabajo) premium is a private insurance price, not a tax: not modelled.
-/

namespace ArGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon ArGlobal

/-- Annual deduction (centavos): 12 months + 2 x 50 % on the SAC installments = 13 x $7,003.68. -/
def detraccion : Int := 13 * 700368

/-- Employer contributions, 18 % of the annual wage less the art. 22 deduction (pesos, down). -/
def employerAr (w : Int) : Int := if w ≤ 0 then 0 else divR .down (1800 * pos (pos w * 100 - detraccion)) (BP * 100)

def sscF : Family :=
  { name := "2200 contribuciones patronales (SIPA, INSSJP, FNE, asignaciones familiares)", covers := [.sscEmployer],
    run := fun _ g _ =>
      if g.entity == .company then
        [charge .sscEmployer "Contribuciones patronales" g.company.payroll id (fun _ => payrollAmount employerAr g.company)
          (event := "payroll") (level := .social) (bearer := .entity) (statute := "Ley 27.541 arts. 19 b) (18 %), 22")]
      else
        (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
          charge .sscEmployer "Contribuciones patronales" a.wages id employerAr (event := s!"adult {i + 1}") (level := .social)
            (bearer := .employer) (statute := "Ley 27.541 art. 19 b) 18 %; art. 22 detracción $7.003,68 por mes (x 13 con el SAC)") }


/-- Ley 23.660 art. 16 a): "Una contribución a cargo del empleador equivalente al seis por ciento (6%) de la
remuneración de los trabajadores que presten servicios en relación de dependencia". -/
def obraSocial : Contribution := { name := "Obra social (contribución del empleador)", sched := Schedule.flat 600 }
def osF : Family := employerFamily "2200 obra social (employer)" [obraSocial] "Ley 23.660 art. 16 a): 6 % de la remuneración (texto actualizado, InfoLEG)"

def families : List Family := [sscF, osF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "employer contributions at 18 % (art. 19 b)); 20.40 % for large services/commerce employers (art. 19 a)) not applied; the annual wage read as including the SAC; obra social (ley 23.660) and ART premiums not modelled"
  ++ when (g.household.adults.any (·.wages > 0) || g.entity == .company) "obra social employer contribution 6 % on the whole wage (no detracción, no ceiling); the ART premium (insurance price) is not modelled"

#guard detraccion == 9104784
#guard employerAr 0 == 0
#guard employerAr 10000000 == 1783611
#guard obraSocial.amount 1000000 == 60000

end ArGlobal.Social
