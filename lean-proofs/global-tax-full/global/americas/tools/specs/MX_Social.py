S = dict(cc="MX", fam="Social",
doc=r'''# Mexico 2025: employer IMSS quotas (2200); retiro, cesantía y vejez and INFONAVIT listed as non-tax

Source: Ley del Seguro Social (Cámara de Diputados PDF, Wayback capture 2025-06; `mx/law/LSS.pdf`), with the 2025 UMA of
the 1.x model (`MxTax.umaDaily` = 113.14 pesos, INEGI DOF 10-01-2025). Grade A.
* **art. 106 fr. I** "una cuota diaria patronal equivalente al trece punto nueve por ciento" of one daily UMA per insured,
  raised by **transitorio décimo noveno** "sesenta y cinco centésimas de punto porcentual" each 1 July 1998-2007: 20.40 %;
  **fr. II** employer "seis por ciento" on the SBC above three UMA, reduced "cuarenta y nueve centésimas de punto
  porcentual" a year 1998-2007: 1.10 %.
* **art. 107 fr. I**: prestaciones en dinero, the employer pays "el setenta por ciento" of 1 %: 0.70 %.
* **art. 25**: gastos médicos de pensionados, "al patrón pagar el uno punto cero cinco por ciento".
* **art. 147**: invalidez y vida, "los patrones ... el uno punto setenta y cinco por ciento".
* **arts. 211, 212**: guarderías y prestaciones sociales "uno por ciento", paid "íntegramente" by the employer.
* **art. 73**: riesgos de trabajo, first registration "Clase I 0.54355" (prima media; later years by the employer's own
  claims experience: flagged).
* **art. 28**: SBC capped at 25 UMA. A year of 365 days at the 2025 UMA (January's 2024 UMA ignored: flagged).
* The OECD books retiro, cesantía en edad avanzada y vejez (art. 168: AFORE individual accounts) and the 5 % INFONAVIT
  contribution as non-tax compulsory payments: not charged (as in the 1.x model's `Imss.oecdSsc`).''',
lean=r'''
/-- 2025 UMA, centavos a day (1.x model). -/
def uma : Int := MxTax.umaDaily

/-- Annual SBC in centavos: wages capped at 25 UMA a day (art. 28). -/
def sbc (w : Int) : Int := min (pos w * 100) (25 * uma * 365)

/-- Employer rates on the SBC, per 10,000,000: dinero 0.70, pensionados 1.05, invalidez 1.75, guarderías 1.00,
riesgos de trabajo class I 0.54355 (%). -/
def rateSbc : Int := 70000 + 105000 + 175000 + 100000 + 54355

/-- Employer IMSS quotas in pesos for an annual wage `w` (down). -/
def employerImss (w : Int) : Int :=
  if w ≤ 0 then 0 else
  let fija := 2040 * uma * 365                       -- ticks of 1/10,000 centavo
  let excess := 110 * pos (sbc w - 3 * uma * 365)    -- same unit
  let rest := divR .down (sbc w * rateSbc) 1000      -- 1/10,000 centavo
  divR .down (fija + excess + rest) 1000000

def sscF : Family :=
  { name := "2200 IMSS employer quotas", covers := [.sscEmployer],
    run := fun _ g _ =>
      if g.entity == .company then
        [charge .sscEmployer "IMSS cuotas patronales" g.company.payroll id (fun _ => payrollAmount employerImss g.company)
          (event := "payroll") (level := .social) (bearer := .entity) (statute := "LSS arts. 25, 73, 106 (transitorio 19o), 107, 147, 211")]
      else
        (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
          charge .sscEmployer "IMSS cuotas patronales" a.wages id employerImss (event := s!"adult {i + 1}") (level := .social)
            (bearer := .employer) (statute := "LSS arts. 25, 73, 106 (transitorio 19o: 20.40 % of UMA + 1.10 % above 3 UMA), 107, 147, 211") }
''',
families="[sscF]",
unsupported=[["g.household.adults.any (·.wages > 0) || g.entity == .company", "IMSS employer quotas: riesgos de trabajo at the class I prima media (0.54355 %); 365 days at the 2025 UMA; employer payment of the worker's quota at the minimum wage (art. 36) not added; retiro, cesantía y vejez (art. 168) and INFONAVIT 5 % are non-tax compulsory payments (OECD): not charged; state payroll tax (ISN) not modelled"]],
guards=["uma == 11314",
        "-- 120,000 pesos a year: 20.40 % x 113.14 x 365 = 8,424.40; SBC rates 5.04355 % x 120,000 = 6,052.26; no excess",
        "employerImss 120000 == 14476",
        "-- 2,000,000 pesos: SBC capped at 25 UMA (1,032,402.50)",
        "employerImss 2000000 == 70487",
        "employerImss 0 == 0"],
taxes=[dict(oecd="2200", tax="IMSS cuotas patronales", statute="Ley del Seguro Social arts. 25, 28, 73, 106 (transitorio décimo noveno), 107, 147, 211, 212", dated="LSS consolidation (Cámara de Diputados) archived 2025-06; UMA 2025 from the 1.x model", grade="A", package="P4", kernel_parts=["charge"], unsupported=["riesgos de trabajo at class I prima media", "art. 36 minimum-wage worker quota"]),
 dict(oecd="2200", tax="Retiro, cesantía en edad avanzada y vejez; INFONAVIT", statute="LSS art. 168; Ley del INFONAVIT art. 29", grade="A", status="not levied", package="P4", kernel_parts=[], unsupported=["individual-account contributions: non-tax compulsory payments in the OECD classification"])])

# ---- P7 triage pass (2026-11-21): 3000 Impuesto sobre Nominas (Ciudad de Mexico) ----
S['doc'] += """

**P7 triage pass (2026-11-21): 3000 Impuesto sobre Nóminas (Ciudad de México).** Código Fiscal de la Ciudad de México
(lexifina/mexico-mexico-city-law `codigo/2009/codigo-fiscal`, consolidation to G.O. 19-12-2025, file commit e3f10cd189eb):
* **art. 156**: "Se encuentran obligadas al pago del Impuesto sobre Nóminas, las personas físicas y morales que, en la
  Ciudad de México, realicen erogaciones en dinero o en especie por concepto de remuneración al trabajo personal
  subordinado" (I sueldos y salarios ... V gratificaciones y aguinaldos ...).
* **art. 158** (reformado, G.O. 27 de diciembre de 2024): "se determinará, aplicando la tasa del 4% sobre el monto total de
  las erogaciones realizadas por concepto de remuneraciones al trabajo personal subordinado". The article was not changed
  by the reform of G.O. 19-12-2025, so 4 % applies to all of 2025 (3 % until 2024).
* **art. 157**: exclusions (SAR, INFONAVIT and IMSS contributions, pensions, profit sharing, workers with a disability,
  household workers ...): the canon's wages carry none of them except household workers (not an input).
Households: the adult's employer is taken as located in the Ciudad de México (the model's reference location) and bears
4 % of the wage; companies: 4 % of the payroll. OECD heading 3000 (Guide §47; OECD MX table: "Payroll tax")."""
S['lean'] += """
/-- Código Fiscal CDMX art. 158 (G.O. 27-12-2024): "la tasa del 4% sobre el monto total de las erogaciones". -/
def isn : PayrollTax := { name := "Impuesto sobre Nóminas (Ciudad de México)", rateBp := 400 }

def isnF : Family := payrollFamily "3000 Impuesto sobre Nóminas (Ciudad de México)" isn
  "Código Fiscal de la Ciudad de México arts. 156, 158 (G.O. 27-12-2024): 4 % of the remuneration for subordinated work" (level := .state)
"""
S['families'] = S['families'].rstrip(']') + ', isnF]'
S['unsupported'][0][1] = S['unsupported'][0][1].replace('; state payroll tax (ISN) not modelled', '')
S['unsupported'].append(["g.household.adults.any (·.wages > 0)", "ISN (Código Fiscal CDMX art. 158, 4 %): the adult's employer taken as located in the Ciudad de México; art. 157 exclusions not inputs"])
S['guards'] += ["isn.amount 120000 == 4800", "isn.amount 0 == 0"]
S['taxes'].append(dict(oecd="3000", tax="Impuesto sobre Nóminas (Ciudad de México)",
    statute="Código Fiscal de la Ciudad de México arts. 156, 157, 158 (art. 158 reformado G.O. 27-12-2024: 4 %)",
    dated="lexifina/mexico-mexico-city-law codigo/2009/codigo-fiscal (consolidation to G.O. 19-12-2025; art. 158 last reformed G.O. 27-12-2024, in force for all of 2025)",
    grade="A", package="P7", kernel_parts=["payrollFamily", "PayrollTax"],
    unsupported=["employer taken as located in the Ciudad de México", "art. 157 exclusions (household workers etc.) not inputs"],
    p7_triage="(a) modelled in the P7 triage pass 2026-11-21"))
