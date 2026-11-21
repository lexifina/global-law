import TaxKernel.World

/-!
# Angola: Imposto sobre os Rendimentos do Trabalho (IRT), Grupo A, and the employee's social-security contribution, 2025

Access tier B (rescue pass 2): every text is the Diário da República as hosted by lex.ao (a private, free database of
Angolan legislation that serves the gazette scans as PDFs; host cited; not an official publisher), read by OCR
(tesseract `por`) and on the page images. sha256 of each file in `ao/law/rescue2/SHA256SUMS`.
* Código do IRT, Lei n.º 18/14 de 22 de Outubro (`lei-n-o-18-14-de-22-de-outubro.pdf`), art. 7.º n.º 2: the Group A
  base is the global pay "a) Dedução à retribuição global das contribuições obrigatórias para a Segurança Social;
  b) Dedução das componentes remuneratórias não sujeitas ou isentas"; art. 10.º n.º 1 (as amended): the tax on Group A
  income is settled monthly by the payer "pela aplicação da tabela de taxas a que se refere o n.º 1 do artigo 16.º".
* Lei n.º 28/20 de 22 de Julho (DR I Série n.º 109), art. 2.º (new art. 16.º n.º 3: "À matéria colectável dos Grupos
  B e C não sujeita à retenção na fonte aplica-se a taxa de 25%") and art. 3.º (table replaced; in force 30 days after
  publication). That 2020 table is superseded for 2025 by:
* Lei n.º 18/24 de 30 de Dezembro (Orçamento Geral do Estado 2025; DR I Série n.º 247, pp. 13782-), art. 20.º n.º 3:
  "Estão isentos de IRT os rendimentos auferidos até ao limite de Kz: 100.000,00 (cem mil Kwanzas), nos termos da
  tabela anexa ao presente Diploma", and Anexo I "a que se refere o n.º 3 do artigo 20.º", headed "TABELA DO IRT
  (Proposta)" (DR p. 13798, read on the page image; the OCR could not read it). The law "entra em vigor a 1 de Janeiro
  de 2025". Monthly rows (Kz): up to 100 000 exempt; 100 001-150 000: parcela fixa "-", 13,0 % "excesso de 100 001";
  150 001-200 000: 12 500, 16,0 %, excesso de 150 001; 200 001-300 000: 31 250, 18,0 %, 200 001; 300 001-500 000:
  49 250, 19,0 %, 300 001; 500 001-1 000 000: 87 250, 20,0 %, 500 001; 1 000 001-1 500 000: 187 249, 21,0 %,
  1 000 001; 1 500 001-2 000 000: 292 249, 22,0 %, 1 500 001; 2 000 001-2 500 000: 402 249, 23,0 %, 2 000 001;
  2 500 001-5 000 000: 517 249, 24,0 %, 2 500 001; 5 000 001-10 000 000: 1 117 249, 24,5 %, 5 000 001; acima de
  10 000 001: 2 342 248, 25,0 %, 10 000 001. (The OGE 2024, Lei n.º 15/23, carries the same art. 20.º n.º 3 wording;
  the OGE 2026, Lei n.º 14/25, raises the exemption to Kz 150 000 from 2026.)
* Decreto Presidencial n.º 227/18 de 27 de Setembro (Protecção Social Obrigatória), art. 12.º: "A taxa contributiva é
  fixada em 8% para a Entidade Empregadora e 3% para o trabalhador"; art. 13.º: the base is the gross pay
  ("remuneração ilíquida"); no ceiling in the articles read (lex.ao text; later amendments not checked).
Household mapping: `wages` = a year's Group A pay paid evenly over 12 months (`perPeriod 12`); INSS 3 % deducted before
the table (art. 7.º n.º 2 a)); `selfEmployment` = the Group B taxable amount (after the cost deduction of art. 8.º),
taxed at 25 % (art. 16.º n.º 3). Rounding: none printed; the table's fractions are dropped (whole kwanzas, down).
The table's "excesso de" column is read literally (excess over 100 001, not 100 000).
-/

namespace AoTax
open TaxKernel

/-- One row of the Anexo I table: lower bound, parcela fixa, rate (bp), "excesso de". -/
structure Row where
  lo : Int
  fixed : Int
  rate : Int
  base : Int

/-- Lei n.º 18/24, Anexo I (monthly Kz). -/
def table : List Row :=
  [⟨0, 0, 0, 0⟩, ⟨100001, 0, 1300, 100001⟩, ⟨150001, 12500, 1600, 150001⟩, ⟨200001, 31250, 1800, 200001⟩,
   ⟨300001, 49250, 1900, 300001⟩, ⟨500001, 87250, 2000, 500001⟩, ⟨1000001, 187249, 2100, 1000001⟩,
   ⟨1500001, 292249, 2200, 1500001⟩, ⟨2000001, 402249, 2300, 2000001⟩, ⟨2500001, 517249, 2400, 2500001⟩,
   ⟨5000001, 1117249, 2450, 5000001⟩, ⟨10000001, 2342248, 2500, 10000001⟩]

/-- The row that holds the monthly base `x` (the last row whose lower bound is ≤ x). -/
def rowFor (x : Int) : Row := (table.filter (fun r => r.lo ≤ x)).getLast?.getD ⟨0, 0, 0, 0⟩

/-- Monthly IRT on a monthly taxable base (whole kwanzas, down). -/
def monthTax (x : Int) : Int :=
  let r := rowFor x
  r.fixed + pos (x - r.base) * r.rate / BP

/-- Decreto Presidencial 227/18 art. 12.º: employee rate 3 %. -/
def inssRate : Int := 300
def inss (m : Int) : Int := pos m * inssRate / BP

/-- Group A: the month's tax on pay less INSS (art. 7.º n.º 2). -/
def monthIRT (m : Int) : Int := monthTax (pos (m - inss m))
def yearIRT (wages : Int) : Int := perPeriod 12 monthIRT wages
def yearINSS (wages : Int) : Int := perPeriod 12 inss wages

/-- Lei 28/20 art. 16.º n.º 3: Groups B and C not under withholding, 25 %. -/
def groupBTax (x : Int) : Int := pos x * 25 / 100

-- The table's own figures (Anexo I): each parcela fixa against the row below it.
-- Rows 4-12 continue (to within a kwanza: the "excesso de 100 001" offsets drop a fraction per row):
#guard monthTax 300000 = 49249 ∧ monthTax 300001 = 49250
#guard monthTax 1000000 = 187249 ∧ monthTax 1000001 = 187249
#guard monthTax 10000000 = 2342248 ∧ monthTax 10000001 = 2342248
-- Rows 2-3 and 3-4 do not: the parcela fixa jumps by 6,001 Kz at 150,001 and 10,751 Kz at 200,001 (statute notches).
#guard monthTax 150000 = 6499 ∧ monthTax 150001 = 12500
#guard monthTax 200000 = 20499 ∧ monthTax 200001 = 31250
#guard monthTax 100000 = 0 ∧ monthTax 100001 = 0

def out (c : Canon) : Out :=
  let irt := sumInts (c.adults.map fun a => yearIRT a.wages)
  let ss := sumInts (c.adults.map fun a => yearINSS a.wages)
  let gb := sumInts (c.adults.map fun a => groupBTax a.selfEmployment)
  Out.make c "AO" "AOA" (irt + gb)
    (employeeSocial := ss)
    (detail := [Out.d "irtGrupoA" irt, Out.d "irtGrupoB" gb, Out.d "inssTrabalhador" ss,
      Out.dStr "note" "CIRT (Lei 18/14) arts. 7, 10, 16 as amended by Lei 28/20; table: Lei 18/24 (OGE 2025) art. 20 n.º 3 + Anexo I; INSS 3 % (Decreto Presidencial 227/18 art. 12); individual taxation; monthly table on annual / 12"])
    (unsupported :=
      (if c.interest ≠ 0 ∨ c.dividends ≠ 0 ∨ c.capitalGains ≠ 0 then ["investment income (Imposto sobre a Aplicação de Capitais): not modelled"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rental income (Imposto Predial): not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: treatment under the CIRT not read"] else []))

def country : Country := { code := "AO", name := "Angola", currency := "AOA", year := "2025", compute := out }

end AoTax
