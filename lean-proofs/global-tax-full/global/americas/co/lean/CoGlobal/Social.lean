import CoGlobal.Pit

/-!
# Colombia 2025: employer pension, health and ARL contributions (2200); parafiscales (3000)

Sources: Ley 100 de 1993 (Secretaría del Senado, basedoc, fetched 2026-11-21; `co/law/ley_0100_1993*.html`); Estatuto
Tributario art. 114-1 (local ET copy, `co/law/et/`); SMMLV 2025 of the 1.x model (`CoTax.smmlv2025` = 1,423,500).
* **Ley 100 art. 20** (Ley 797 de 2003 art. 7): "La tasa de cotización continuará en el 13.5%" + 1 % (2004) + 0.5 %
  (2005) + 0.5 % (2006), and "a partir del 1o. de enero del año 2008, el Gobierno Nacional podrá incrementar en un (1%)
  punto adicional" (exercised by Decreto 4982 de 2007, not read: 16 %); "Los empleadores pagarán el 75% de la
  cotización total": 12 %. Base: the monthly wage, not below one SMMLV nor above 25 SMMLV (art. 18). Grade B (the decree).
* **Ley 100 art. 204** (Ley 1122 de 2007 art. 10): health "12,5% ... La cotización a cargo del empleador será del 8.5%".
* **ET art. 114-1** (Ley 1819 de 2016 art. 65): companies that declare income tax are "exoneradas del pago de los
  aportes parafiscales a favor del SENA, del ICBF y las cotizaciones al Régimen Contributivo de Salud ... correspondientes
  a los trabajadores que devenguen ... menos de diez (10) salarios mínimos": employer health is charged only on wages of
  10 SMMLV a month or more (the employer read as such a company: flagged).
* The OECD (Taxing Wages, Colombia) books the pension and health contributions as non-tax compulsory payments (most
  go to private funds); they are charged here as 2200 with that note.
* **ARL** (riesgos laborales): Decreto 1772 de 1994 **art. 13** (compiled as Decreto 1072 de 2015 art. 2.2.4.3.5), table of
  cotizaciones: "I 0.348% 0.522% 0.696%" (minimum, initial, maximum for risk class I); the employer pays it on the IBC
  (art. 18 base). Applied at class I, valor inicial 0.522 % (office work): flagged.
* **Parafiscales** (pass 5; texts fetched 2026-11-21): **Ley 21 de 1982 art. 12** (Colpensiones normograma): the
  contributions of "empleadores del sector privado, tendrán la siguiente destinación: 1. El cuatro por ciento (4%) para
  proveer el pago de subsidio familiar. 2. El dos por ciento (2%) para el Servicio Nacional de Aprendizaje (SENA)";
  **Ley 89 de 1988 art. 1** (ICBF PDF): ICBF contributions "se aumentan al tres por ciento (3%) del valor de la nómina
  mensual de salarios". Base: the monthly payroll (Ley 21 art. 17), no floor or cap. ET art. 114-1 exonerates SENA and
  ICBF (not the Caja) for workers earning less than 10 SMMLV: SENA + ICBF 5 % only from 10 SMMLV a month. Booked as 3000
  (payroll taxes) by their nature (OECD Revenue Statistics treatment not checked).
-/

namespace CoGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon CoGlobal

def smmlv : Int := CoTax.smmlv2025

/-- Monthly contribution base (art. 18): the monthly wage between 1 and 25 SMMLV (0 when there is no wage). -/
def ibc (w : Int) : Int := if w ≤ 0 then 0 else max smmlv (min (pos w / 12) (25 * smmlv))

/-- Employer pension, 12 % (75 % of 16 %), a year (pesos, down). -/
def pensionEmp (w : Int) : Int := divR .down (12 * 1200 * ibc w) 10000

/-- Employer health, 8.5 %, only where the monthly wage is at least 10 SMMLV (ET art. 114-1). -/
def healthEmp (w : Int) : Int := if pos w / 12 ≥ 10 * smmlv then divR .down (850 * 12 * ibc w) 10000 else 0

/-- ARL, risk class I valor inicial 0.522 % of the IBC (Decreto 1772/1994 art. 13), a year. -/
def arlEmp (w : Int) : Int := divR .down (12 * 522 * ibc w) 100000

/-- Caja de compensación 4 % of the payroll (Ley 21/1982 art. 12 (1)), a year. -/
def cajaEmp (w : Int) : Int := divR .down (400 * pos w) 10000

/-- SENA 2 % + ICBF 3 % (Ley 21 art. 12 (2), Ley 89/1988 art. 1), only from 10 SMMLV a month (ET art. 114-1). -/
def senaIcbf (w : Int) : Int := if pos w / 12 ≥ 10 * smmlv then divR .down (500 * pos w) 10000 else 0

def paraF : Family :=
  { name := "3000 aportes parafiscales (Caja, SENA, ICBF)", covers := [.payroll],
    run := fun _ g _ =>
      if g.entity == .company then
        [charge .payroll "Caja de compensación familiar 4 %" g.company.payroll id (fun _ => payrollAmount cajaEmp g.company)
          (event := "payroll") (bearer := .entity) (statute := "Ley 21 de 1982 art. 12 (1)"),
         charge .payroll "SENA 2 % and ICBF 3 %" g.company.payroll id (fun _ => payrollAmount senaIcbf g.company)
          (event := "payroll") (bearer := .entity) (statute := "Ley 21 de 1982 art. 12 (2); Ley 89 de 1988 art. 1; ET art. 114-1")]
      else
        (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).flatMap fun (a, i) =>
          [charge .payroll "Caja de compensación familiar 4 %" a.wages id cajaEmp (event := s!"adult {i + 1}")
             (bearer := .employer) (statute := "Ley 21 de 1982 art. 12 (1)"),
           charge .payroll "SENA 2 % and ICBF 3 %" a.wages id senaIcbf (event := s!"adult {i + 1}")
             (bearer := .employer) (statute := "Ley 21 de 1982 art. 12 (2); Ley 89 de 1988 art. 1; ET art. 114-1 (exonerated below 10 SMMLV)")] }

def sscF : Family :=
  { name := "2200 employer pension and health contributions", covers := [.sscEmployer],
    run := fun _ g _ =>
      if g.entity == .company then
        [charge .sscEmployer "Pension and health (employer)" g.company.payroll id (fun _ => payrollAmount (fun w => pensionEmp w + healthEmp w + arlEmp w) g.company)
          (event := "payroll") (level := .social) (bearer := .entity) (statute := "Ley 100 arts. 18, 20, 204; ET art. 114-1; Decreto 1772/1994 art. 13 (ARL class I)")]
      else
        (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).flatMap fun (a, i) =>
          [charge .sscEmployer "Pension contribution (employer)" a.wages id pensionEmp (event := s!"adult {i + 1}") (level := .social)
             (bearer := .employer) (statute := "Ley 100 art. 20 (75 % of 16 %), art. 18 (1-25 SMMLV)"),
           charge .sscEmployer "Health contribution (employer)" a.wages id healthEmp (event := s!"adult {i + 1}") (level := .social)
             (bearer := .employer) (statute := "Ley 100 art. 204 (8.5 %); ET art. 114-1 (exonerated below 10 SMMLV)"),
           charge .sscEmployer "ARL premium (employer, class I)" a.wages id arlEmp (event := s!"adult {i + 1}") (level := .social)
             (bearer := .employer) (statute := "Decreto 1772 de 1994 art. 13 (Decreto 1072 de 2015 art. 2.2.4.3.5): class I valor inicial 0.522 %")] }

def families : List Family := [sscF, paraF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "employer read as an income-tax-declaring company (ET art. 114-1 exoneration below 10 SMMLV); pension total 16 % per Decreto 4982/2007 (not read); ARL at risk class I (0.522 %); parafiscales on the whole annual wage (Caja 4 % always, SENA + ICBF 5 % from 10 SMMLV a month); OECD books these contributions as non-tax compulsory payments"

#guard smmlv == 1423500
#guard ibc 12000000 == 1423500
#guard ibc 600000000 == 35587500
#guard pensionEmp 24000000 == 2880000
#guard healthEmp 24000000 == 0
#guard healthEmp 240000000 == 1700000 * 12
#guard arlEmp 24000000 == 125280
#guard cajaEmp 24000000 == 960000
#guard senaIcbf 24000000 == 0
#guard senaIcbf 240000000 == 12000000

end CoGlobal.Social
