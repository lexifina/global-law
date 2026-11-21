import TaxKernel.World
import TaxKernel.Tariff

/-!
# Guinea-Bissau: Imposto Profissional (IP), 2025

Access tier B (rescue pass 3, 2026-11-20). Statute text: the Código do Imposto Profissional (CIP, Decreto n.º 23/83,
de 6 de Agosto) as consolidated by the Direcção-Geral das Contribuições e Impostos on the Ministry of Finance's tax
portal Kontaktu: "Código do Imposto Profissional (Atualizado até 31-01-2021 e LGT de 2022)"
(`https://kontaktu.mef.gw/legislation`, read 2026-11-20; saved `gw/law/rescue3/kontaktu_legislation_2026-11-20.html`,
section extracted to `cip_section_extracted.md`). Each amended paragraph carries its dated note.
**Version: law as of 31 January 2021 (Lei n.º 1/2021, OGE 2021) plus the LGT of 2022.** Why B and not A: the enacted
budget laws for 2022-2025 were not reached. The Ministry's own budget documents (mef.gw, "Proposta OGE2023", "Proposta
OGE24", "Proposta OGE25", and the OGE 2026) list the tax laws they amend: none amends CIP art. 27 for 2023-2025 (the
OGE 2026, December 2025, amends CIP art. 1 and adds art. 27-A, both from 2026).

* art. 1 (Lei 9/2013 art. 19): the IP "incide sobre os rendimentos do trabalho, em dinheiro ou espécie" (dependent work,
  services, liberal professions). art. 2 (Lei 9/2013): not income: c) "As pensões de reforma e aposentação de valor igual
  ou inferior a 200.000 Fcfa mensais".
* art. 18(1): employers deduct from every payment "o imposto profissional correspondente às mesmas remunerações,
  calculado pela aplicação à respectiva importância das taxas previstas no artigo 27º".
* art. 27(1) (Lei 1/2021 art. 10), employees, monthly column (annual = 12x): 0-41.667 1 % (parcela 0); 41.668-83.333
  6 % (2.083); 83.334-208.333 8 % (3.750); 208.334-300.000 10 % (7.917); 300.001-400.500 12 % (13.917);
  400.501-750.000 14 % (37.947); 750.001-1.100.000 16 % (52.947); 1.100.001-1.500.000 18 % (74.947); superior a
  1.500.000 20 % (104.947). Annual parcelas printed: 0; 24.996; 45.000; 95.004; 167.004; 455.364; 635.364; 899.364;
  1.259.363.
* art. 27(2) (Lei 8/2020 art. 17, Lei 1/2021 art. 17), self-employed and author's rights, annual column:
  0-2.199.996 10 %; 2.199.997-9.999.996 20 % (parcela 220.000); superior a 9.999.996 25 % (720.000).
* art. 27(3): "As percentagens indicadas na coluna B ... representam taxas marginais, sendo cada uma delas válida dentro
  dos limites do correspondente escalão ... As importâncias da coluna C são valores a abater ao resultado obtido da
  aplicação da taxa sobre o valor do rendimento auferido". art. 28 (1983): "As taxas ... aplicam-se apenas ao rendimento
  que excede o escalão máximo tributado pela taxa anterior."

The two sentences of art. 27(3) agree up to 400.500 a month and then part: the printed parcela of the 14 % row
(37.947) is the one a 6-point step would give (13.917 + 6 % x 400.500), as in the struck 2020 table's 18 % row, not
the 2-point step to 14 % (21.927). Modelled: the printed table (rate on the whole income less the parcela: the
specific, later text that employers apply under art. 18); the marginal reading is `ipMarginalMonth`, reported in
`detail` for comparison.

Household mapping: `wages` = gross annual pay, paid in 12 equal monthly payments (the last takes the remainder);
`pension` = annual pension (art. 2(c) monthly test on pension/12; above it the whole pension under art. 27(1): a
reading); `selfEmployment` = annual taxable income of art. 13 under the art. 27(2) annual column. Rounding: not
printed; whole francs down. Unsupported: INSS contributions, the Imposto de Democracia (Lei 1/2021 art. 14, text not
reached), the Imposto Complementar (CIP art. 10 refers to it; code not reached), capital and property income taxes.
-/

namespace GwTax
open TaxKernel

/-- CIP art. 27(1) (Lei 1/2021 art. 10): monthly column; rate (bp) on the whole income less the printed monthly parcela. -/
def ipRows : List SubRow :=
  [⟨0, 100, 0⟩, ⟨41668, 600, 2083⟩, ⟨83334, 800, 3750⟩, ⟨208334, 1000, 7917⟩, ⟨300001, 1200, 13917⟩,
   ⟨400501, 1400, 37947⟩, ⟨750001, 1600, 52947⟩, ⟨1100001, 1800, 74947⟩, ⟨1500001, 2000, 104947⟩]

/-- Printed annual parcelas of art. 27(1) (column "Parcela a abater (XOF) Anual (P.A.A)"). -/
def ipAnnualParcelas : List Int := [0, 24996, 45000, 95004, 167004, 455364, 635364, 899364, 1259363]

/-- art. 27(3) first sentence / art. 28: the same rates read as marginal rates on the bands of column A. -/
def ipMarginal : Schedule := Schedule.ofList
  [(0, 100), (41667, 600), (83333, 800), (208333, 1000), (300000, 1200), (400500, 1400), (750000, 1600),
   (1100000, 1800), (1500000, 2000)]

/-- Monthly IP on a monthly payment `m` (printed table; whole francs down; never below 0). -/
def ipMonth (m : Int) : Int := if m ≤ 0 then 0 else max 0 ((Rule.downTo 1).ofTicks (subTicks ipRows m))
def ipMarginalMonth (m : Int) : Int := if m ≤ 0 then 0 else ipMarginal.tax (Rule.downTo 1) m

/-- Twelve equal monthly payments, the last with the remainder. -/
def twelve (f : Int → Int) (annual : Int) : Int :=
  let q := pos annual / 12
  11 * f q + f (pos annual - 11 * q)

def wageTax (w : Int) : Int := twelve ipMonth w

/-- art. 2(c): pensions up to 200.000 FCFA a month are not income; above, the whole pension under art. 27(1). -/
def pensionLimitMonthly : Int := 200000
def pensionTax (p : Int) : Int := if pos p / 12 ≤ pensionLimitMonthly then 0 else twelve ipMonth p

/-- CIP art. 27(2): self-employed and author's rights, annual column. -/
def selfRows : List SubRow := [⟨0, 1000, 0⟩, ⟨2199997, 2000, 220000⟩, ⟨9999997, 2500, 720000⟩]
def selfSchedule : Schedule := Schedule.ofList [(0, 1000), (2199996, 2000), (9999996, 2500)]
def selfTax (x : Int) : Int := if x ≤ 0 then 0 else max 0 ((Rule.downTo 1).ofTicks (subTicks selfRows x))

-- The statute's own figures.
-- art. 27(1): the printed parcelas agree with the marginal bands (within one franc) up to 400.500 a month ...
#guard subAgrees ipRows ipMarginal [1, 41667, 41668, 83333, 83334, 208333, 208334, 300000, 300001, 400500] (tol := BP)
-- ... and not from 400.501: the 14 % row subtracts 16.020 FCFA a month more than the bands give.
#guard subAgrees ipRows ipMarginal [400501] (tol := BP) = false
#guard ipMonth 400500 = 34143 ∧ ipMonth 400501 = 18123
#guard ipMarginalMonth 400501 - ipMonth 400501 = 16020
#guard ipMarginalMonth 2000000 - ipMonth 2000000 = 16020
-- 13.917 + (14 - 12) % x 400.500 = 21.927 would be continuous; the printed 37.947 = 13.917 + 6 % x 400.500.
#guard 13917 + 400500 * 2 / 100 = 21927 ∧ 13917 + 400500 * 6 / 100 = 37947
-- The annual parcelas are twelve times the monthly ones, except the top row (1.259.363 vs 12 x 104.947 = 1.259.364).
#guard ((ipRows.map (fun r => 12 * r.subtract)).zip ipAnnualParcelas).map (fun (a, b) => a - b) = [0, 0, 0, 0, 0, 0, 0, 0, 1]
-- 1 % from the first franc: no exempt band.
#guard ipMonth 41667 = 416 ∧ ipMonth 1 = 0 ∧ ipMonth 100 = 1
-- art. 27(2): the self-employed table is continuous (agrees with its bands within one franc).
#guard subAgrees selfRows selfSchedule [1, 2199996, 2199997, 9999996, 9999997, 20000000] (tol := BP)
#guard selfTax 2199996 = 219999 ∧ selfTax 9999996 = 1779999
-- art. 2(c): a pension one franc a month above 200.000 is taxed in full: 12 x (8 % x 200.001 - 3.750).
#guard pensionTax 2400000 = 0 ∧ pensionTax 2400012 = 12 * 12250

def out (c : Canon) : Out :=
  let w := sumInts (c.adults.map fun a => wageTax a.wages)
  let p := sumInts (c.adults.map fun a => pensionTax a.pension)
  let s := sumInts (c.adults.map fun a => selfTax a.selfEmployment)
  let wMarg := sumInts (c.adults.map fun a => twelve ipMarginalMonth a.wages)
  Out.make c "GW" "XOF" (w + p + s)
    (employeeSocial := 0)
    (detail := [Out.d "ipTrabalhoContaOutrem" w, Out.d "ipPensoes" p, Out.d "ipContaPropria" s,
      Out.d "ipMarginalReadingWages" wMarg,
      Out.dStr "note" "CIP (Decreto 23/83) arts. 1, 2(c), 18, 27, 28 as consolidated by the DGCI to 31-01-2021 (Lei 1/2021) + LGT 2022; printed table (rate x income - parcela)"])
    (unsupported := ["INSS employee contributions: rate text not reached (employeeSocial = 0)",
      "Imposto de Democracia (Lei 1/2021 art. 14, levied with the IP): text not reached",
      "Imposto Complementar (CIP art. 10): code not reached",
      "enacted budget laws 2022-2025 not reached: DGCI consolidation to 31-01-2021 (+ LGT 2022); MEF budget proposals 2023-2025 show no change to CIP art. 27"] ++
      (if c.interest ≠ 0 || c.dividends ≠ 0 then ["capital income (Imposto de Capitais): not modelled"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rental income (Contribuição Predial Urbana): not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: not modelled"] else []))

def country : Country := { code := "GW", name := "Guinea-Bissau", currency := "XOF", year := "2025", compute := out }

theorem marginal_progressive : ipMarginal.progressive = true := by decide
theorem self_progressive : selfSchedule.progressive = true := by decide

end GwTax
