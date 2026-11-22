import TaxKernel.Schedule
import TaxKernel.Rounding
import TaxKernel.Unit
import TaxKernel.Canon
import TaxKernel.Country
import TaxKernel.Theorems.Schedule
import TaxKernel.Theorems.Parts

/-!
# Portugal, IRS 2025 (rendimentos de 2025, mainland): parameters, each with its source

Money is `Int` **cents** (the IRS is assessed in euros and cents). Rates are written in the unit the statute
needs: basis points (`bp`, 1/10 000) where the statute's rate has at most two decimals of a percent, and
`pcm` (1/100 000, "per cent mille") for CIRS art. 68 column B, which has three decimals of a percent.

Sources (saved under `../law/`):
* CIRS = Código do IRS (DL 442-A/88). Text: Global law `portugal/national/acts/codigos/codigo-do-irs/` (current
  text, checked against DRE 2026-10-28) and the Autoridade Tributária (AT) site
  https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/cirs_rep/ ; 2025 wording
  reconstructed from the amending laws:
  - Lei n.º 45-A/2024, de 31 de dezembro (Orçamento do Estado 2025), art. on the CIRS (arts 2, 12-B, 25, 53, 68,
    70, 71 ...), https://diariodarepublica.pt/dr/detalhe/lei/45-a-2024 ; AT copy `law/Lei_45_A_2024.pdf`.
  - Lei n.º 55-A/2025, de 22 de julho (art. 68 rates), https://diariodarepublica.pt/dr/detalhe/lei/55-a-2025-925904929 ;
    AT copy `law/Lei_55_A_2025.pdf`.
* IAS 2025 = 522,50 € (Portaria n.º 112/2025/1, art. 2 n.º 3: the subsídio de funeral "€ 261,25 e corresponde a
  50 % do indexante dos apoios sociais (IAS)").
-/

namespace PTTax
open TaxKernel

/-- Euros to cents. -/
def eur (e : Int) : Int := 100 * e

/-- IAS 2025 in cents (Portaria 112/2025/1 art. 2 n.º 3: 261,25 € = 50 % IAS). -/
def ias : Int := 52250

/-! ## CIRS art. 68 (Lei 55-A/2025 art. 2), in force for 2025 income -/

/-- Art. 68 n.º 1 table, one row per escalão: (upper limit in euros, column A "Normal" of the NEXT escalão in pcm,
column B "Média" of this escalão in pcm). Lei 55-A/2025: "Até 8 059 | 12,50 | 12,500", "De mais de 8 059 até
12 160 | 16,00 | 13,680", …, "Superior a 83 696 | 48,00". -/
def art68Rows : List (Int × Int × Int) :=
  [(8059, 16000, 12500), (12160, 21500, 13680), (17233, 24400, 15982), (22306, 31400, 17897),
   (28400, 34900, 20794), (41629, 43100, 25277), (44987, 44600, 26607), (83696, 48000, 34929)]

/-- Column A of the 1st escalão: 12,50 % (pcm). -/
def art68FirstRate : Int := 12500

/-- The same table as a kernel `Schedule` (thresholds in cents, rates in bp): the exact sum over the bands. The
statute does NOT compute this sum; it computes art. 68 n.º 2 with the rounded column B (see `Art68`). -/
def art68Bands : Schedule :=
  Schedule.ofList [(0, 1250), (805900, 1600), (1216000, 2150), (1723300, 2440), (2230600, 3140),
    (2840000, 3490), (4162900, 4310), (4498700, 4460), (8369600, 4800)]

/-- The 2025 schedule as first enacted by Lei 45-A/2024 (OE 2025: thresholds updated, rates unchanged from Lei
33/2024, "[...]" in the amending text) and in force for withholding until Lei 55-A/2025. Kept for the
withholding/timing analysis only. Rates: 13; 16,5; 22; 25; 32; 35,5; 43,5; 45; 48 % (Lei 33/2024 art. 68). -/
def art68BandsOE2025 : Schedule :=
  Schedule.ofList [(0, 1300), (805900, 1650), (1216000, 2200), (1723300, 2500), (2230600, 3200),
    (2840000, 3550), (4162900, 4350), (4498700, 4500), (8369600, 4800)]

/-! ## CIRS art. 68-A taxa adicional de solidariedade (Lei 7-A/2016 wording, unchanged in 2025) -/

/-- "De mais de 80 000 até 250 000 | 2,5", "Superior a 250 000 | 5". -/
def solidarity : Schedule := Schedule.ofList [(0, 0), (8000000, 250), (25000000, 500)]

/-! ## CIRS art. 25 (Lei 45-A/2024): dedução específica of categoria A; art. 53 (pensions, same amount) -/

/-- Art. 25 n.º 1 a): "8,54 vezes o valor do IAS" = 4 462,15 € (8,54 × 522,50 = 4 462,15). -/
def dedEspecifica : Int := 854 * ias / 100

theorem dedEspecifica_val : dedEspecifica = 446215 := by decide

/-! ## CIRS art. 70 mínimo de existência (Lei 24-D/2022, Lei 82/2023, Lei 34/2024; n.º 1 by Lei 45-A/2024) -/

/-- Art. 70 n.º 1 (Lei 45-A/2024): "igual ao maior valor entre 12 180 € e 1,5 × 14 × IAS". -/
def meRef : Int := max (eur 12180) (15 * 14 * ias / 10)

theorem meRef_val : meRef = 1218000 := by decide

/-- Art. 78-B n.º 1: "com o limite global de € 250 para cada sujeito passivo" (Limite despesas gerais, art. 70 n.º 5 c)). -/
def limDespesasGerais : Int := eur 250

/-- Art. 70 n.º 5 e): "Limite do 1.º escalão" = 8 059 €. -/
def lim1 : Int := eur 8059

/-- Limite despesas gerais / Taxa 1.º escalão = 250 / 12,5 % = 2 000 € (cents). -/
def meG : Int := limDespesasGerais * 100000 / art68FirstRate

theorem meG_val : meG = 200000 := by decide

/-- Art. 70 n.º 4 a): "2,2 x 14 x IAS multiplicado pelo número de sujeitos passivos" (per SP, cents). -/
def meExclGross : Int := 22 * 14 * ias / 10

theorem meExclGross_val : meExclGross = 1609300 := by decide

/-- Art. 70 n.º 4 b): "superior a 14 x IAS multiplicado pelo número desses sujeitos passivos" (per SP). -/
def meExclLib : Int := 14 * ias

/-! ## CIRS art. 12-B IRS Jovem (Lei 45-A/2024) -/

/-- Art. 12-B n.º 5: "com o limite de 55 vezes o valor do IAS" = 28 737,50 €. -/
def jovemCap : Int := 55 * ias

/-- Art. 12-B n.º 5 a)-d): 100 % (1st year), 75 % (2nd-4th), 50 % (5th-7th), 25 % (8th-10th); in %. -/
def jovemPct (year : Int) : Int :=
  if year = 1 then 100 else if 2 ≤ year ∧ year ≤ 4 then 75 else if 5 ≤ year ∧ year ≤ 7 then 50
  else if 8 ≤ year ∧ year ≤ 10 then 25 else 0

/-- Art. 12-B n.º 1: "que tenha até 35 anos de idade". -/
def jovemMaxAge : Nat := 35

/-! ## CIRS arts 71-72: rates on income not englobed -/

/-- Art. 71 n.º 1: "à taxa liberatória de 28 %" (interest, dividends). bp. -/
def rateLiberatoria : Int := 2800
/-- Art. 72 n.º 1 c): capital gains on shares "à taxa autónoma de 28 %". bp. -/
def rateGains : Int := 2800
/-- Art. 72 n.º 2 (Lei 56/2023): "arrendamento habitacional ... à taxa autónoma de 25 %". bp. -/
def rateRentHousing : Int := 2500
/-- Art. 40-A n.º 1: dividends englobed "considerados em apenas 50 % do seu valor". -/
def dividendEnglobPct : Int := 50

/-! ## CIRS art. 31 n.º 1 b): categoria B, regime simplificado -/

/-- "0,75 aos rendimentos das atividades profissionais especificamente previstas na tabela ... artigo 151.º"
(the model's default for `selfEmployment`). Per cent. -/
def coefProfessional : Int := 75

/-! ## Deductions from the coleta (art. 78-A, 78-B) -/

/-- Art. 78-A n.º 1 a): "Por cada dependente o montante fixo de € 600". -/
def dedDependent : Int := eur 600
/-- Art. 78-A n.º 2 a): "€ 126 por cada dependente ... quando o dependente não ultrapasse três anos de idade". -/
def dedUnder3 : Int := eur 126
/-- Art. 78-A n.º 3 (Lei 24-D/2022): "€ 300 ... para o segundo dependente e seguintes que não ultrapassem seis anos". -/
def dedSecondUnder6 : Int := eur 300
/-- Art. 78-B n.º 1: 35 % up to 250 € per SP; n.º 9 (monoparental): 45 % up to 335 €. -/
def despGeraisRate : Int := 35
def despGeraisRateMono : Int := 45
def despGeraisCapMono : Int := eur 335

/-! ## Segurança Social (Código dos Regimes Contributivos, Lei 110/2009) -/

/-- Art. 53.º: "cabendo 23,75 % à entidade empregadora e 11 % ao trabalhador" (bp). -/
def tsuEmployee : Int := 1100
/-- Art. 168.º n.º 1: "A taxa contributiva a cargo dos trabalhadores independentes é fixada em 21,4 %" (bp). -/
def tsuIndependent : Int := 2140
/-- Art. 162.º n.º 1 a): rendimento relevante "70 % do valor total de prestação de serviços" (per cent). -/
def independentBasePct : Int := 70

/-! ## Abono de família (DL 176/2003; Portaria n.º 112/2025/1, effects from 1 January 2025) -/

/-- DL 176/2003 art. 14 n.º 2-3: escalão limits as multiples of 14 × IAS, in tenths: 0,5; 1; 1,7; 2,5. -/
def abonoLimitsTenths : List Int := [5, 10, 17, 25]

/-- Portaria 112/2025/1 art. 2 n.º 1, monthly amounts (cents) by escalão 1-4: (≤ 36 months, 36-72 months,
> 72 months). "€ 186,87 ... igual ou inferior a 36 meses; € 73,51 ... superior a 36 meses" (1.º); "€ 158,17 /
€ 73,51" (2.º); "€ 129,23 / € 58,05 / € 53,18" (3.º); "€ 86,53 / € 43,81" (4.º, none above 72 months). -/
def abonoMonthly : List (Int × Int × Int) :=
  [(18687, 7351, 7351), (15817, 7351, 7351), (12923, 5805, 5318), (8653, 4381, 0)]

/-- Portaria 112/2025/1 art. 3: majoração for a second titular aged ≤ 36 months, by escalão 1-4: with two
titulares (a) and with more than two (b). -/
def abonoMajTwo : List Int := [6356, 5640, 5318, 3843]
def abonoMajMore : List Int := [10466, 9033, 8391, 5450]

/-- DL 176/2003 art. 14 n.º 4 and Portaria 112/2025/1 art. 4 n.º 1: monoparental "majorado em 50 %". Per cent. -/
def abonoMonoPct : Int := 50

end PTTax
