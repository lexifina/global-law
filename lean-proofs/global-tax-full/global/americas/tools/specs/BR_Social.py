S = {'cc': 'BR', 'fam': 'Social', 'doc': '# Brazil 2025: employer social security contribution (2200); RAT and third-party contributions grade C\n\nSource: Lei 8.212/1991, compiled text (planalto.gov.br `l8212cons.htm`, Wayback capture 2025-07-04; `br/law/`).\n* **art. 22**: "A contribuição a cargo da empresa, destinada à Seguridade Social ... é de: I - vinte por cento sobre o\n  total das remunerações pagas, devidas ou creditadas a qualquer título, durante o mês, aos segurados empregados".\n  No ceiling applies to the employer\'s 20 %. Grade A.\n* Not modelled (listed): art. 22 II (RAT/GILRAT 1, 2 or 3 % by risk, times the FAP), the contributions to third parties\n  (salário-educação 2.5 %, Sistema S, INCRA), the Simples Nacional and payroll-relief (desoneração, Lei 14.973/2024)\n  regimes. FGTS (8 %) is a deposit in the worker\'s account, not a tax.\n\nAdded in pass 3: **RAT/GILRAT**, Lei 8.212 art. 22 II (Lei 9.732/1998 wording; `br/law/l8212cons.txt`): 1 %, 2 % or 3 % by\nthe accident risk of the employer\'s main activity; 1 % (leve) is charged, the FAP multiplier (0.5-2, Lei 10.666 art. 10)\nis not applied: lower bound, grade B. **Salário-educação**, Lei 9.424/1996 art. 15 (planalto, fetched 2026-11-21;\n`br/law/l9424.htm`): 2.5 % of the remuneration of employees, grade A. Sistema S (SENAI/SESI/SENAC/SESC/SEBRAE) and INCRA\ndepend on the employer\'s sector and are not modelled.', 'lean': 'def inssEmp (w : Int) : Int := divR .down (2000 * pos w) BP\ndef sscF : Family := employerFamily "2200 contribuição patronal (Lei 8.212 art. 22 I)" [{ name := "Contribuição patronal previdenciária", sched := Schedule.flat 2000 }] "Lei 8.212/1991 art. 22 I: 20 % of the total remuneration (no ceiling)"\n\n/-- Lei 8.212 art. 22 II a): "1% (um por cento) para as empresas em cuja atividade preponderante o risco de acidentes do\ntrabalho seja considerado leve" (2 % médio, 3 % grave): the lowest band is charged (the employer\'s activity is not an\ninput). -/\ndef rat : Contribution := { name := "RAT/GILRAT (risco leve)", sched := Schedule.flat 100 }\n/-- Lei 9.424/1996 art. 15: "O Salário-Educação ... é calculado com base na alíquota de 2,5% (dois e meio por cento)\nsobre o total de remunerações pagas ou creditadas ... aos segurados empregados". -/\ndef salEdu : Contribution := { name := "Salário-educação", sched := Schedule.flat 250 }\ndef ratF : Family := employerFamily "2200 RAT/GILRAT (Lei 8.212 art. 22 II a))" [rat] "Lei 8.212/1991 art. 22 II a): 1 % (risco leve; 2 % médio, 3 % grave)"\ndef seF : Family := employerFamily "2200 salário-educação (Lei 9.424 art. 15)" [salEdu] "Lei 9.424/1996 art. 15: 2,5 % sobre o total de remunerações"', 'families': '[sscF, ratF, seF]', 'unsupported': [['g.household.adults.any (·.wages > 0) || g.entity == .company', 'employer 20 % (art. 22 I), RAT at the 1 % band (FAP not applied) and salário-educação 2.5 % charged; Sistema S and INCRA (sector-dependent) and the Simples Nacional regime not modelled']], 'guards': ['inssEmp 100000 == 20000', 'rat.amount 100000 == 1000', 'salEdu.amount 100000 == 2500'], 'taxes': [{'oecd': '2200', 'tax': 'Contribuição patronal previdenciária (20 %)', 'statute': 'Lei 8.212/1991 art. 22 I', 'dated': 'planalto compiled text, capture 2025-07-04', 'grade': 'A', 'package': 'P4', 'kernel_parts': ['employerFamily', 'Contribution']}, {'oecd': '2200', 'tax': 'RAT/GILRAT (employer)', 'statute': 'Lei 8.212 art. 22 II a)-c)', 'dated': 'Lei 8.212 compilada (planalto), wording of Lei 9.732/1998', 'grade': 'B', 'package': 'P4', 'kernel_parts': ['employerFamily', 'Contribution'], 'unsupported': ['risk band of the employer (1 % charged)', 'FAP multiplier']}, {'oecd': '2200', 'tax': 'Salário-educação (employer)', 'statute': 'Lei 9.424/1996 art. 15', 'dated': 'planalto compiled text fetched 2026-11-21', 'grade': 'A', 'package': 'P4', 'kernel_parts': ['employerFamily', 'Contribution']}, {'oecd': '2200', 'tax': 'Contributions to third parties: Sistema S, INCRA', 'statute': 'DL 4.048/1942; DL 9.403/1946; Lei 8.029/1990; Lei 2.613/1955', 'grade': 'C', 'status': 'unsupported', 'package': 'P4', 'kernel_parts': [], 'tried': "not fetched (rates depend on the employer's sector, FPAS code)", 'unsupported': ['would unlock: the FPAS table and the Sistema S acts']}]}

# ---- P7 triage pass (2026-11-21): 3000 re-filing (salario-educacao, Sistema S) and 2300 contribuinte individual ----
S['doc'] += """

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
wage fills the teto first); 20 % of it, 12 months."""
S['lean'] = S['lean'].replace(
    'def seF : Family := employerFamily "2200 salário-educação (Lei 9.424 art. 15)" [salEdu] "Lei 9.424/1996 art. 15: 2,5 % sobre o total de remunerações"',
    'def seF : Family := employerFamily "3000 salário-educação (Lei 9.424 art. 15)" [salEdu] "Lei 9.424/1996 art. 15: 2,5 % sobre o total de remunerações" (oecd := .payroll) (level := .central)')
assert '"3000 salário-educação' in S['lean']
S['lean'] += """
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
"""
S['families'] = S['families'].rstrip(']') + ', ciF]'
S['unsupported'].append(["g.household.adults.any (·.selfEmployment > 0)", "contribuinte individual: selfEmployment read as the remuneration of 12 equal months; the 11 % / 5 % (MEI) plans (art. 21 § 2), the company's 20 % and 11 % withholding on services to companies (art. 22 III, Lei 10.666 art. 4) and the 13th wage in the teto not modelled"])
S['guards'] += ["BrTax.inss.ceiling == 815741", "ciAnnual 60000 0 == 12000", "ciAnnual 200000 0 == 19577", "ciAnnual 10000 0 == 3643",
                "ciAnnual 60000 120000 == 0", "ciAnnual 60000 60000 == 7577", "ciAnnual 0 0 == 0"]
for t in S['taxes']:
    if t['tax'] == 'Salário-educação (employer)':
        t['oecd'] = '3000'; t['refiled_note'] = 'filed under 3000 (was 2200) in the P7 triage pass 2026-11-21: OECD BR table "Payroll-based contribution to education" (3000); Guide §40, §47'
    if t['tax'] == 'Contributions to third parties: Sistema S, INCRA':
        t['oecd'] = '3000'; t['refiled_note'] = 'filed under 3000 (was 2200) in the P7 triage pass 2026-11-21: OECD BR table "S System contributions" (3000); Guide §40, §47'
S['taxes'].append(dict(oecd="2300", tax="Contribuição previdenciária do contribuinte individual (20 %)",
    statute="Lei 8.212/1991 art. 21, art. 28 III, § 3, § 5",
    dated="lexifina/brazil-law lei-de-custeio-da-seguridade-social (art. 21 wording of Lei 12.470/2011, commit 176d47091b; repository versions to 2026-03-27); 2025 teto R$ 8.157,41 and salário mínimo R$ 1.518,00 from the 1.x model (BrTax.inss)",
    grade="A", package="P7", kernel_parts=["Family", "charge"],
    unsupported=["11 % / 5 % (MEI) plans of art. 21 § 2", "services to companies: art. 22 III and Lei 10.666 art. 4 withholding", "13th wage in the teto"],
    p7_triage="(a) modelled in the P7 triage pass 2026-11-21"))
