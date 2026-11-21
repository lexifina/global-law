import TaxKernel.World

/-!
# Mozambique: IRPS on employment income (final monthly withholding), 2025

Access tier B: the statute is reached (Lei n.º 20/2013, de 23 de Setembro, Boletim da República I Série n.º 76, which
amends the Código do IRPS approved by Lei n.º 33/2007; archived copy of the Autoridade Tributária's own file,
web.archive.org/web/20150410191725id_/http://www.at.gov.mz/por/content/download/1385/10635/version/1/file/Lei+nº+20-2013-IRPS.pdf.pdf,
sha256 in `mz/law/SHA256SUMS`; the annex table read on the page image), but no amendment after 2013 was reached or
ruled out (the AT's current site is a script shell; parlamento.mz answers a script loader; Global law's Mozambique
corpus holds only the Constitution, the Commercial Code and the Labour Law).
* Art. 5 of Lei 20/2013: "A presente Lei entra em vigor a 1 de Janeiro de 2014 e aplica-se aos rendimentos de 2014 e
  seguintes."
* CIRPS art. 65 n.º 5 (as amended): "A retenção na fonte do imposto relativo aos rendimentos de trabalho dependente é
  efectuada a título definitivo." So for wages the annual tax is the sum of the monthly withholdings.
* Art. 65-A n.º 1-2: withholding "nos termos da tabela anexa"; "A retenção do IRPS é igual à soma entre o valor do IRPS
  constante da tabela correspondente ao intervalo em que se enquadram as remunerações mensalmente pagas ... e o
  resultado da aplicação dos coeficientes que lhes correspondam ao valor da diferença entre essas remunerações e o
  valor mínimo do intervalo".
* Anexo (art. 65-A): rows "Até 20.249,99 -"; "De 20.250,00 até 20.749,99: 0,00 - - - - | 0,10"; "20.750: 50,00
  0,00 - - - | 0,10"; "21.000: 75,00 25,00 0,00 - - | 0,10"; "21.250: 100,00 50,00 25,00 0,00 - | 0.10"; "21.750: 150,00
  100,00 75,00 50,00 0,00 | 0,10"; "22.250: 200,00 150,00 125,00 100,00 50,00 | 0,15"; "32.750: 1.775,00 1.725,00
  1.700,00 1.675,00 1.625,00 | 0,20"; "60.750: 7.375,00 7.325,00 7.300,00 7.275,00 7.225,00 | 0,25"; "144.750 até
  diante: 28.375,00 28325,00 28.300,00 27.275,00 28.225,00 | 0,32". Nota: "O sinal (-) significa que não há impostos
  a reter e nem se aplica o coeficiente. O (0,00) significa que apenas se aplica o coeficiente." The five value
  columns are "por número de dependentes"; their headings are blank in the gazette (read as 0, 1, 2, 3, 4 or more).
* Art. 56 n.º 1: "Não é tributado o rendimento colectável anual inferior ou igual 225.000,00 MT"; art. 60 n.º 1:
  deductions from the tax "1.800,00MT por cada sujeito passivo", dependants 600 / 900 / 1.200 / 1.800 MT (these govern
  the annual assessment of other income, which the model does not compute).
Computed in centavos and rounded to whole meticais at the end. Unit: individual; children are dependants of the first
adult (at most 4 count). Non-employment income is not modelled.
W5 pattern A (2026-11-20): the worker's INSS contribution, 3 % of remuneration (no ceiling), is reported and not
deducted. Rate: the INSS page "Taxa contributiva TCO" (inss.gov.mz, fetched 2026-11-20; official secondary): "A taxa
contributiva descontada ao beneficiário (trabalhador) é de 3% valor, taxa que juntamente com os 4% comparticipados
pela entidade empregador perfazem 7% do valor que é descontado e canalizado mensalmente ao INSS". The Regulamento da
Segurança Social Obrigatória (Decreto 51/2017, republished by Decreto 56/2024 de 30 de Julho, BR I Série n.º 147,
INSS copy; `mz/law/w5/`) art. 14 (1): "As contribuições são calculadas pela aplicação da taxa sobre as remunerações
consideradas como base de incidência"; art. 15: the rate is fixed and revised "por diploma conjunto dos Ministros"
(that diploma was not reached). Not deducted from the IRPS base: the AT's "As 100 questões mais frequentes sobre o
CIRPS" (2015, in `mz/law/`), q. 25: "Aos rendimentos do trabalho dependente, não há dedução a fazer, nos termos do
artigo 29, ou seja, o rendimento bruto é igual ao colectável" (official secondary; art. 29 itself in the Lei 33/2007
text not reached). `"w5Contrib": false` restores the pre-W5 model.
-/

namespace MzTax
open TaxKernel

/-- One row: lower limit (MT), values by number of dependants 0..4 (`none` = "-"), coefficient in bp. -/
structure Row where
  lo : Int
  vals : List (Option Int)
  coef : Int

/-- Anexo of art. 65-A, values in centavos. -/
def table : List Row :=
  [ ⟨2025000, [some 0, none, none, none, none], 1000⟩,
    ⟨2075000, [some 5000, some 0, none, none, none], 1000⟩,
    ⟨2100000, [some 7500, some 2500, some 0, none, none], 1000⟩,
    ⟨2125000, [some 10000, some 5000, some 2500, some 0, none], 1000⟩,
    ⟨2175000, [some 15000, some 10000, some 7500, some 5000, some 0], 1000⟩,
    ⟨2225000, [some 20000, some 15000, some 12500, some 10000, some 5000], 1500⟩,
    ⟨3275000, [some 177500, some 172500, some 170000, some 167500, some 162500], 2000⟩,
    ⟨6075000, [some 737500, some 732500, some 730000, some 727500, some 722500], 2500⟩,
    ⟨14475000, [some 2837500, some 2832500, some 2830000, some 2727500, some 2822500], 3200⟩ ]

/-- The row whose interval holds `m` (centavos): the last row with `lo ≤ m`. -/
def rowFor (m : Int) : Option Row := (table.filter fun r => r.lo ≤ m).getLast?

/-- Monthly withholding in centavos for remuneration `m` (centavos) and `d` dependants. -/
def monthlyCents (m : Int) (d : Nat) : Int :=
  match rowFor m with
  | none => 0
  | some r =>
    match r.vals.getD (min d 4) none with
    | none => 0
    | some v => v + divR .down (r.coef * (m - r.lo)) BP

def monthly (meticais : Int) (d : Nat) : Int := divR .halfUp (monthlyCents (100 * meticais) d) 100

/- Each printed value equals the row above continued by its coefficient (the table is continuous), except dependants
   column 3 of the last row: 7.275,00 + 0,25 x 84.000 = 28.275,00, printed 27.275,00 (FINDINGS F1). -/
def contAt (i : Nat) (d : Nat) : Option Int :=
  match table[i]?, table[i+1]? with
  | some a, some b =>
    match a.vals.getD d none, b.vals.getD d none with
    | some va, some vb => some (va + divR .down (a.coef * (b.lo - a.lo)) BP - vb)
    | _, _ => none
  | _, _ => none
#guard (List.range 4).all fun i => (List.range 5).all fun d => contAt (i + 4) d = some 0 ∨ contAt (i + 4) d = none ∨ (i + 4 = 7 ∧ d = 3)
#guard contAt 7 3 = some 100000
/- So a worker with three dependants pays 1.000 MT a month LESS at 144.750,00 than at 144.749,99. -/
#guard monthly 144749 3 - monthly 144750 3 = 1000

/-- W5 pattern A: INSS worker 3 % of remuneration (INSS page), no ceiling; meticais, rounded down. -/
def inssWorkerBp : Int := 300
def inssWorker (w : Int) : Int := divR .down (pos w * inssWorkerBp) BP
/- The INSS page: 3 % (worker) + 4 % (employer) = 7 %. -/
#guard inssWorkerBp + 400 = 700 ∧ inssWorker 600000 = 18000

def out (c : Canon) : Out :=
  let w5 := (c.bool? "w5Contrib").getD true
  let es := if w5 then sumInts (c.adults.map fun a => inssWorker a.wages) else 0
  let rows := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    let d : Nat := if i = 0 then c.nChildren else 0
    12 * monthly (divR .down a.wages 12) d
  let it := sumInts rows
  Out.make c "MZ" "MZN" it (employeeSocial := es)
    (detail := [Out.d "taxBeforeCredits" it, Out.dStr "note" "CIRPS art. 65-A annex table (Lei 20/2013), final withholding on wages (art. 65 n.º 5), 12 equal months"])
    (unsupported := (if c.interest ≠ 0 ∨ c.dividends ≠ 0 ∨ c.rentalIncome ≠ 0 ∨ c.capitalGains ≠ 0 then ["capital and property income (art. 57 liberatory rates and the art. 54 annual tariff) not modelled"] else []) ++
      (if (c.adults.any fun a => a.selfEmployment ≠ 0 ∨ a.pension ≠ 0) then ["self-employment and pensions: the art. 54 annual tariff of the CIRPS (Lei 33/2007) was not reached"] else []) ++
      ["no amendment of the CIRPS after Lei 20/2013 was reached or ruled out", if w5 then "INSS worker 3 % from the INSS page (official secondary; the joint ministerial diploma fixing it not reached), reported, not deducted (AT FAQ q. 25)" else "INSS employee contributions not reached"])

def country : Country := { code := "MZ", name := "Mozambique (IRPS on wages, 2025)", currency := "MZN", year := "2025", compute := out }

def sched : Schedule := Schedule.ofList [(0, 0), (20250, 1000), (22250, 1500), (32750, 2000), (60750, 2500), (144750, 3200)]
theorem sched_progressive : sched.progressive = true := by decide
/- Column 0 of the table equals this marginal schedule (in meticais) at every row limit. -/
#guard table.all fun r => match r.vals.head? with
  | some (some v) => sched.ticks (r.lo / 100) = v / 100 * BP
  | _ => true

end MzTax
