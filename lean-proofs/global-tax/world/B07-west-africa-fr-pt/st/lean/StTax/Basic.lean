import TaxKernel.World
import TaxKernel.Tariff

/-!
# São Tomé and Príncipe: Imposto sobre o Rendimento de Pessoas Singulares (IRS), 2025

Access tier C (rescue pass 3, 2026-11-20). **Version: law as of the OGE 2025 bill (Proposta de Lei n.º 33/XII/5.ª/2025, Diário da Assembleia Nacional II
série n.º 15, 26 Feb 2025, art. 22: effects from 1 Jan 2025); the enacted OGE 2025 text was not reached.** On the bill
the 2016 table applies (it does not repeat the OGE 2024 30 % band, whose changes lasted only "até a aprovação e
publicação" of the next budget law, OGE 2024 art. 8(14)) and the IERS is kept (bill art. 8(18)). Had the enacted
OGE 2025 kept the 30 % band, the 2025 tax is `irsOn rows2024 ..`, reported in `detail.irsWith2024Band`.

Statute texts (all Diário da República prints or the National Assembly's own diaries):
* Código do IRS, Lei n.º 17/2008, de 31 de Dezembro, as amended and **republished** by Lei n.º 11/2009, de 8 de Outubro
  (Diário da República n.º 68, 8 Oct 2009; the Direcção dos Impostos' download 177, archived copy
  `web.archive.org/web/20220621125449id_/https://impostos.financas.gov.st/index.php/legislacao/leg-tributaria/category/26-irs?download=177:...`;
  text layer). Read: arts. 2-6 (Category A; art. 6(1)(b): pensions "de quantitativo anual inferior ou igual a
  Dbs. 24.000.000,00" exempt), 36 (residence), 38, 40-41 (englobamento of Categories A and B; C and D not englobed),
  44 (Category A deductions: (a) employee INSS contributions, (d) "50% dos rendimentos englobados, provenientes das
  pensões"), 56 (no return for a single employer fully withheld), 66 (table), 67(2) (single-employer pay withheld at
  the art. 66 rates), 69 (15 % liberatory rate on capital income), 74 (personal and family deductions).
* Decreto-Lei n.º 16/2016 (Diário da República n.º 172, 17 Nov 2016, p. 1521, read on the page image): art. 66 table
  rewritten: "Até Dbs. 11.700.000,00 | 0"; "De 11.700.001,00 até 50.000.000,00 | 10% | 1.170.000,00"; "De
  50.000.001,00 até 100.000.000,00 | 13% | 2.670.000,00"; "De 100.000.001,00 até 150.000.000,00 | 15% |
  4.670.000,00"; "De 150.000.001,00 até 240.000.000,00 | 20% | 12.170.000,00"; "Superior à 240.000.001,00 | 25% |
  24.170.000,00" (old dobras; the preamble: no taxpayer just above a band edge may be left with less than one at it).
* Decreto-Lei n.º 10/2019 (Diário da República I série n.º 52, 23 Sep 2019, p. 761, page image): "Fica suspensa a
  aplicação do artigo 74.º do Código do IRS" (no end date): no personal or family deduction.
* OGE 2024 (enacted text: Diário da Assembleia Nacional II série n.º 40, 14 Feb 2024, committee "texto final"; the
  Ministry of Finance's 'OGE2024-APROVADO' file): art. 8(11) "É aditada à tabela do Código do IRS ... um novo escalão
  para rendimento igual ou superior a Dbs. 420.000,00 ..., sujeito à taxa de 30% e a parcela a abater de Dbs.
  45.048,00"; (12) IERS "à taxa de 20%, que incide sobre parte do rendimento disponível que exceder Dbs. 50.000,00
  mensal"; (14) "Todas as alterações constantes na presente Lei manter-se-ão em vigor até a aprovação e publicação da
  Lei do Orçamento Geral do Estado do ano seguinte."
* OGE 2025: Proposta de Lei n.º 33/XII/5.ª/2025 (Diário da Assembleia Nacional II série n.º 15, 26 Feb 2025, pp. 164 ff.; in
  the 5.ª sessão folder of the Assembly's site, which its listing does not link): art. 8(18) "São mantidas as taxas do
  Imposto Especial sobre o Rendimento de Pessoas Singulares (IERS), em 20%, que incide sobre parte do rendimento
  disponível que exceder Dbs: 50.000,00 (cinquenta mil dobras) mensal"; no IRS band, no sunset clause; art. 22
  effects "retroactivamente ... a partir de 1 de Janeiro de 2025". The enacted text: not reached (version gap).

Units: new dobras (STN). The 2016 table is in old dobras; the 2018 redenomination (1 new = 1.000 old; Decreto-Lei
11/2016 and 15/2017, not reached) is applied, as the OGE 2024 itself does when it adds a band at Dbs. 420.000 above
the table's Dbs. 240.000.000 (old) top band. Household mapping: each adult's `wages` + 50 % of a `pension` above the
art. 6(1)(b) limit (+ `selfEmployment` as Category B net profit, Group 1 reading) are englobed and taxed by the art. 66
table (rate on the whole income less the parcela); `dividends` / `interest` at the 15 % liberatory rate. Rounding: not
printed; whole dobras down.
W5 pattern A (2026-11-20): employee INSS 4 % of gross remuneration, deducted from Category A under art. 44(a).
**Regulamentação da Protecção Social Obrigatória (REPSO), Decreto-Lei n.º 19/2022 (DR n.º 53, 15/07/2022) as amended
by Decreto-Lei n.º 25/2022 (DR n.º 101, 30/12/2022)**, INSS consolidated text (inss.gov.st/assets/Leis/Lei_n_19_2022.pdf,
Internet Archive capture 2024-11-11; `st/law/w5/`), art. 101.º 3: "A taxa de contribuição dos trabalhadores e demais
pessoas singulares abrangidas é de 4% e a taxa de contribuição das entidades empregadoras é de 6%"; art. 102.º 1: the
contributions fall on the remuneration "sendo considerado sempre o valor ilíquido e livre de quaisquer descontos"
(no ceiling); art. 102.º 6-7: declared pay is at least the minimum wage (1 UCSS without one), not applied (the model's
annual wage need not be 12 full months). `"w5Contrib": false` restores the pre-W5 model.
-/

namespace StTax
open TaxKernel

/-- CIRS art. 66 as rewritten by DL 16/2016, in new dobras (old amounts / 1.000). -/
def rows2016 : List SubRow :=
  [⟨0, 0, 0⟩, ⟨11700, 1000, 1170⟩, ⟨50000, 1300, 2670⟩, ⟨100000, 1500, 4670⟩, ⟨150000, 2000, 12170⟩,
   ⟨240000, 2500, 24170⟩]
/-- OGE 2024 art. 8(11): the band from Dbs. 420.000 at 30 % less 45.048. -/
def rows2024 : List SubRow := rows2016 ++ [⟨420000, 3000, 45048⟩]
/-- The 2016 table read as marginal bands. -/
def bands2016 : Schedule := Schedule.ofList [(0, 0), (11700, 1000), (50000, 1300), (100000, 1500), (150000, 2000), (240000, 2500)]
def bands2024 : Schedule := Schedule.ofList
  [(0, 0), (11700, 1000), (50000, 1300), (100000, 1500), (150000, 2000), (240000, 2500), (420000, 3000)]
/-- The 2009 table (Lei 11/2009, old dobras), for the record. -/
def rows2009old : List SubRow :=
  [⟨0, 0, 0⟩, ⟨11700001, 1000, 881250⟩, ⟨50000001, 1300, 1380000⟩, ⟨100000001, 1500, 1875000⟩,
   ⟨150000001, 2000, 5625000⟩, ⟨240000001, 2500, 9000000⟩]

def table2025 : List SubRow := rows2016

def irsOn (rows : List SubRow) (x : Int) : Int := if x ≤ 0 then 0 else max 0 ((Rule.downTo 1).ofTicks (subTicks rows x))

/-- art. 6(1)(b) and 44(d): pensions up to 24.000 a year exempt; above, 50 % englobed. -/
def pensionLimit : Int := 24000
def pensionPart (p : Int) : Int := if pos p ≤ pensionLimit then 0 else pos p - pos p / 2

/-- IERS (OGE 2024 art. 8(12), kept by the OGE 2025 bill art. 8(18)): 20 % of monthly disposable income above 50.000; disposable = monthly
englobed income less monthly IRS (reading; the law does not define it). -/
def iers (annualIncome irs : Int) : Int := 12 * (pos ((pos annualIncome - irs) / 12 - 50000) * 20 / 100)

-- The statute's own figures.
-- DL 16/2016: the parcelas make the table equal to its marginal bands (old dobras / 1.000) ...
#guard subAgrees rows2016 bands2016 [0, 11700, 11701, 50000, 50001, 100000, 100001, 150000, 150001, 240000, 240001, 1000000]
-- ... in old dobras exactly: 1.170.000 = 10 % x 11.700.000; 2.670.000 = 1.170.000 + 3 % x 50.000.000; etc.
#guard 11700000 * 10 / 100 = 1170000 ∧ 1170000 + 50000000 * 3 / 100 = 2670000 ∧ 2670000 + 100000000 * 2 / 100 = 4670000
#guard 4670000 + 150000000 * 5 / 100 = 12170000 ∧ 12170000 + 240000000 * 5 / 100 = 24170000
-- Lei 11/2009 (2009-2016): the printed parcelas made the tax jump at each edge: +288.750 old dobras at 11.700.001.
#guard (Rule.downTo 1).ofTicks (subTicks rows2009old 11700001) = 288750
-- OGE 2024: the 30 % band's parcela is 122 short of the 25 % row's (45.170 would be continuous).
#guard 24170 + 420000 * 5 / 100 = 45170
#guard irsOn rows2024 420000 - (420000 * 25 / 100 - 24170) = 122
#guard subAgrees rows2024 bands2024 [419999] ∧ subAgrees rows2024 bands2024 [420000] (tol := 121 * BP) = false
-- art. 6(1)(b) / 44(d): a pension one dobra above 24.000 a year is half englobed.
#guard pensionPart 24000 = 0 ∧ pensionPart 24001 = 12001

/-- W5 pattern A: REPSO art. 101.º 3, the worker's 4 % of gross remuneration (no ceiling). -/
def inssWorkerBp : Int := 400
def inssWorker (w : Int) : Int := pos w * inssWorkerBp / 10000
-- art. 101.º 3: 4 % worker + 6 % employer.
#guard inssWorkerBp + 600 = 1000 ∧ inssWorker 120000 = 4800

def out (c : Canon) : Out :=
  let w5 := (c.bool? "w5Contrib").getD true
  let inssOf (a : Adult) : Int := if w5 then inssWorker a.wages else 0
  let per := c.adults.map fun a =>
    let inc := pos a.wages - inssOf a + pensionPart a.pension + pos a.selfEmployment
    let t := irsOn table2025 inc
    (t, iers inc t)
  let irs := sumInts (per.map Prod.fst)
  let ie := sumInts (per.map Prod.snd)
  let irs24 := sumInts (c.adults.map fun a => irsOn rows2024 (pos a.wages - inssOf a + pensionPart a.pension + pos a.selfEmployment))
  let cap := pos c.dividends * 15 / 100 + pos c.interest * 15 / 100
  Out.make c "ST" "STN" (irs + cap) (surtaxes := [("IERS", ie)])
    (employeeSocial := sumInts (c.adults.map inssOf))
    (detail := [Out.d "irsEnglobamento" irs, Out.d "taxaLiberatoria" cap, Out.d "iers" ie, Out.d "irsWith2024Band" irs24,
      Out.dStr "note" "CIRS (Lei 17/2008 rep. Lei 11/2009) arts. 6, 44, 66 (DL 16/2016), 69; DL 10/2019 (art. 74 suspended); OGE 2024 art. 8(11)-(14); OGE 2025 bill art. 8(18): 2016 table (30 % band not repeated) + IERS"])
    (unsupported := [if w5 then "INSS worker 4 % (REPSO art. 101.º 3) deducted under art. 44(a); minimum contributory wage (art. 102.º 6-7) not applied" else "INSS employee contributions: rate not reached (employeeSocial = 0; not deducted under art. 44(a))",
      "IERS base 'rendimento disponível' is undefined in the law: read as englobed income less IRS",
      "version gap: the enacted OGE 2025 was not reached; modelled on the OGE 2025 bill (2016 table + IERS); with the OGE 2024 30 % band kept see detail.irsWith2024Band"] ++
      (if c.adults.any (fun a => a.selfEmployment ≠ 0) then ["self-employment englobed as Category B Group 1 net profit (Group 2 presumptive rules not modelled)"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rental income (Category B/C rules, Contribuição Predial Urbana): not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains (Category D): not modelled"] else []))

def country : Country := { code := "ST", name := "Sao Tome and Principe", currency := "STN", year := "2025", compute := out }

theorem bands2016_progressive : bands2016.progressive = true := by decide

end StTax
