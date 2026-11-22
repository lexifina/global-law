import BrGlobal.Pit

/-!
# Brazil 2025: employer social security contribution (2200); RAT and third-party contributions grade C

Source: Lei 8.212/1991, compiled text (planalto.gov.br `l8212cons.htm`, Wayback capture 2025-07-04; `br/law/`).
* **art. 22**: "A contribuição a cargo da empresa, destinada à Seguridade Social ... é de: I - vinte por cento sobre o
  total das remunerações pagas, devidas ou creditadas a qualquer título, durante o mês, aos segurados empregados".
  No ceiling applies to the employer's 20 %. Grade A.
* Not modelled (listed): art. 22 II (RAT/GILRAT 1, 2 or 3 % by risk, times the FAP), the contributions to third parties
  (salário-educação 2.5 %, Sistema S, INCRA), the Simples Nacional and payroll-relief (desoneração, Lei 14.973/2024)
  regimes. FGTS (8 %) is a deposit in the worker's account, not a tax.

Added in pass 3: **RAT/GILRAT**, Lei 8.212 art. 22 II (Lei 9.732/1998 wording; `br/law/l8212cons.txt`): 1 %, 2 % or 3 % by
the accident risk of the employer's main activity; 1 % (leve) is charged, the FAP multiplier (0.5-2, Lei 10.666 art. 10)
is not applied: lower bound, grade B. **Salário-educação**, Lei 9.424/1996 art. 15 (planalto, fetched 2026-11-21;
`br/law/l9424.htm`): 2.5 % of the remuneration of employees, grade A. Sistema S (SENAI/SESI/SENAC/SESC/SEBRAE) and INCRA
depend on the employer's sector and are not modelled.

**P7 triage pass (2026-11-21).** (1) **Re-filed to 3000**: the OECD Brazil table books the salário-educação ("Payroll-based
contribution to education") and the Sistema S ("S System contributions") under **3000**, and the Guide (§40) puts a levy
on payroll that confers no benefit entitlement in 3000 (§47), not 2000: the salário-educação family (Lei 9.424/1996
art. 15, 2.5 %, unchanged) now books under 3000, and the Sistema S / INCRA C entry is filed under 3000.
(2) **2300 contribuinte individual** (lexifina/brazil-law `lei-de-custeio-da-seguridade-social`, Lei 8.212/1991 as
compiled by planalto, latest version in the repository 2026-03-27; art. 21 last changed by Lei 12.470/2011):
* **art. 21**: "A alíquota de contribuição dos segurados contribuinte individual e facultativo será de vinte por cento
  sobre o respectivo salário-de-contribuição" (§ 2: 11 % / 5 % plans on the minimum, by option: not modelled).
* **art. 28 III**: for the contribuinte individual, "a remuneração auferida em uma ou mais empresas ou pelo exercício de
  sua atividade por conta própria, durante o mês, observado o limite máximo a que se refere o § 5º"; **§ 3**: the limite
  mínimo is the salário mínimo; **§ 5**: the limite máximo (2025: R$ 8.157,41, and salário mínimo R$ 1.518,00, both from
  the 1.x model's 2025 INSS table `BrTax.inss`).
Monthly base = self-employment / 12, at least the salário mínimo, at most the teto less the wage month (the employee's
wage fills the teto first); 20 % of it, 12 months.
-/

namespace BrGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon BrGlobal

def inssEmp (w : Int) : Int := divR .down (2000 * pos w) BP
def sscF : Family := employerFamily "2200 contribuição patronal (Lei 8.212 art. 22 I)" [{ name := "Contribuição patronal previdenciária", sched := Schedule.flat 2000 }] "Lei 8.212/1991 art. 22 I: 20 % of the total remuneration (no ceiling)"

/-- Lei 8.212 art. 22 II a): "1% (um por cento) para as empresas em cuja atividade preponderante o risco de acidentes do
trabalho seja considerado leve" (2 % médio, 3 % grave): the lowest band is charged (the employer's activity is not an
input). -/
def rat : Contribution := { name := "RAT/GILRAT (risco leve)", sched := Schedule.flat 100 }
/-- Lei 9.424/1996 art. 15: "O Salário-Educação ... é calculado com base na alíquota de 2,5% (dois e meio por cento)
sobre o total de remunerações pagas ou creditadas ... aos segurados empregados". -/
def salEdu : Contribution := { name := "Salário-educação", sched := Schedule.flat 250 }
def ratF : Family := employerFamily "2200 RAT/GILRAT (Lei 8.212 art. 22 II a))" [rat] "Lei 8.212/1991 art. 22 II a): 1 % (risco leve; 2 % médio, 3 % grave)"
def seF : Family := employerFamily "3000 salário-educação (Lei 9.424 art. 15)" [salEdu] "Lei 9.424/1996 art. 15: 2,5 % sobre o total de remunerações" (oecd := .payroll) (level := .central)
/-- Salário mínimo 2025, centavos a month (the lower limit of the salário-de-contribuição, Lei 8.212 art. 28 § 3; the
first band limit of the 1.x model's 2025 INSS table). -/
def salMin : Int := 151800

/-- Monthly salário-de-contribuição of a contribuinte individual (centavos) for annual self-employment `se` and annual
wages `w` (reais): se / 12, at least the salário mínimo, at most the teto (`BrTax.inss.ceiling`) less the wage month. -/
def ciBase (se w : Int) : Int :=
  min (pos (BrTax.inss.ceiling - divR .down (pos w * 100) 12)) (max (divR .down (pos se * 100) 12) salMin)

/-- Lei 8.212 art. 21: 20 % of the monthly salário-de-contribuição, 12 months (reais, down). -/
def ciAnnual (se w : Int) : Int := if se ≤ 0 then 0 else divR .down (12 * 2000 * ciBase se w) (BP * 100)

def ciF : Family :=
  { name := "2300 contribuinte individual (Lei 8.212 art. 21)", covers := [.sscSelf],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.household.adults.zipIdx.filter fun (a, _) => a.selfEmployment > 0).map fun (a, i) =>
        charge .sscSelf "Contribuição do contribuinte individual (20 %)" a.selfEmployment id (fun se => ciAnnual se a.wages)
          (event := s!"adult {i + 1}") (level := .social)
          (statute := "Lei 8.212/1991 art. 21 (20 %), art. 28 III, § 3 (salário mínimo R$ 1.518,00), § 5 (teto R$ 8.157,41 less the wage month)") }

def families : List Family := [sscF, ratF, seF, ciF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "employer 20 % (art. 22 I), RAT at the 1 % band (FAP not applied) and salário-educação 2.5 % charged; Sistema S and INCRA (sector-dependent) and the Simples Nacional regime not modelled"
  ++ when (g.household.adults.any (·.selfEmployment > 0)) "contribuinte individual: selfEmployment read as the remuneration of 12 equal months; the 11 % / 5 % (MEI) plans (art. 21 § 2), the company's 20 % and 11 % withholding on services to companies (art. 22 III, Lei 10.666 art. 4) and the 13th wage in the teto not modelled"

#guard inssEmp 100000 == 20000
#guard rat.amount 100000 == 1000
#guard salEdu.amount 100000 == 2500
#guard BrTax.inss.ceiling == 815741
#guard ciAnnual 60000 0 == 12000
#guard ciAnnual 200000 0 == 19577
#guard ciAnnual 10000 0 == 3643
#guard ciAnnual 60000 120000 == 0
#guard ciAnnual 60000 60000 == 7577
#guard ciAnnual 0 0 == 0

end BrGlobal.Social
