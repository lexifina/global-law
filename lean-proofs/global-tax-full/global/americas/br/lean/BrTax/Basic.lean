import TaxKernel.World

/-!
# Brazil: IRPF ano-calendário 2025 (Declaração de Ajuste Anual) and the employee's INSS contribution

Statutes (Global law `brazil/national/acts`, publisher Planalto; texts as in force on 2025-06-30 unless said):
* Lei 7.713/1988 (the tax on individuals' income), Lei 9.250/1995 arts. 4, 8, 10, 11 (deductions, simplified
  discount, annual tax), Lei 11.482/2007 art. 1 (the monthly tables) and its parágrafo único: "O imposto de renda
  anual devido … será calculado de acordo com tabela progressiva anual correspondente à soma das tabelas progressivas
  mensais vigentes nos meses de cada ano-calendário." Lei 11.482 is not in Global law: read from the archived copy of
  the official Planalto page that Global law itself reads (web.archive.org 20251230020925, sha256 ef54a34c…; Planalto
  refuses scripted requests). Tables in force in 2025: inciso XI (Lei 15.191/2025 wording: "a partir do mês de
  fevereiro do ano-calendário de 2024 até o mês de abril do ano-calendário de 2025") and inciso XII ("a partir do mês
  de maio do ano-calendário de 2025"), the latter also read in Global law `lei-15191-de-2025/art-002.md`.
* INSS: Emenda Constitucional 103/2019 art. 28 (progressive 7,5 / 9 / 12 / 14 % "aplicadas de forma progressiva …
  incidindo cada alíquota sobre a faixa"; § 2 bands readjusted with the RGPS benefits). 2025 bands: INSS's own table
  page "TABELAS VÁLIDAS A PARTIR DA COMPETÊNCIA JANEIRO DE 2025" (official secondary; archived gov.br page of
  2025-06-11, sha256 6d46594b…): "Até 1.518,00 7,5% / De 1.518,01 a 2.793,88 9% / De 2.793,89 até 4.190,83 12% /
  De 4.190,84 até 8.157,41 14%".

Unit: each spouse files his or her own declaration (no compulsory joint filing; dependants claimed once: we give the
children to the spouse for whom the deduction is worth most). Money in centavos inside, whole reais out (half up).
Assumes the year's wages are paid in 12 equal months (the 13º salário, taxed exclusively at source under Lei 7.713
art. 26 / Lei 8.134 art. 16, is not a contract input).
-/

namespace BrTax
open TaxKernel

/-- Lei 11.482 art. 1 XI (Feb 2024 - Apr 2025), centavos: "Até 2.259,20 0 0 / De 2.259,21 até 2.826,65 7,5 169,44 /
De 2.826,66 até 3.751,05 15 381,44 / De 3.751,06 até 4.664,68 22,5 662,77 / Acima de 4.664,68 27,5 896,00". -/
def tableXI : Schedule := Schedule.ofList [(0, 0), (225920, 750), (282665, 1500), (375105, 2250), (466468, 2750)]
/-- Lei 11.482 art. 1 XII (from May 2025; Lei 15.191/2025 art. 2): "Até 2.428,80 0 0 / … 7,5 182,16 / De 2.826,66 até
3.751,05 15 394,16 / De 3.751,06 até 4.664,68 22,5 675,49 / Acima de 4.664,68 27,5 908,73". -/
def tableXII : Schedule := Schedule.ofList [(0, 0), (242880, 750), (282665, 1500), (375105, 2250), (466468, 2750)]

/-- Annual table = the sum of the monthly tables in force in each month (art. 1 parágrafo único): 4 months of XI
(January-April) and 8 of XII (May-December). Thresholds and rates as a band schedule in centavos. -/
def annual : Schedule :=
  Schedule.ofList [(0, 0), (4 * 225920 + 8 * 242880, 750), (12 * 282665, 1500), (12 * 375105, 2250),
    (12 * 466468, 2750)]

/-- The "parcela a deduzir" columns printed in XI and XII agree with the band schedules (checked at the printed
thresholds; the annual parcela is 4 × XI + 8 × XII). -/
def parcela (rate lo ded : Int) (x : Int) : Int := rate * x - ded * BP
/-- within one centavo (the printed parcelas are rounded to the centavo) -/
def near (a b : Int) : Bool := (a - b).natAbs < BP.natAbs
#guard near (tableXI.ticks 300000) (parcela 1500 0 38144 300000)
#guard near (tableXII.ticks 300000) (parcela 1500 0 39416 300000)
#guard near (tableXII.ticks 500000) (parcela 2750 0 90873 500000)
/-- The annual table as the statute sums it: rate × base − the summed "parcela a deduzir" (4 × XI + 8 × XII),
centavos → ticks. This is the tax used (the band form `annual` differs by a few centavos, see `annual_vs_parcela`). -/
def annualParcela (x : Int) : Int :=
  if x ≤ 2846720 then 0
  else if x ≤ 3391980 then 750 * x - (4 * 16944 + 8 * 18216) * BP
  else if x ≤ 4501260 then 1500 * x - (4 * 38144 + 8 * 39416) * BP
  else if x ≤ 5597616 then 2250 * x - (4 * 66277 + 8 * 67549) * BP
  else 2750 * x - (4 * 89600 + 8 * 90873) * BP
/-- The summed parcelas and the band sum differ by less than 7 centavos at sample points (each monthly parcela is
rounded to the centavo; 12 roundings). -/
def within (k a b : Int) : Bool := (a - b).natAbs < (k * BP).natAbs
#guard [3000000, 4000000, 5000000, 6000000, 10000000, 30000000].all fun x => within 7 (annual.ticks x) (annualParcela x)

/-- Lei 9.250 art. 8 II c 9: "R$ 2.275,08 … por dependente … a partir do ano-calendário de 2015" (centavos). -/
def dependent : Int := 227508
/-- Lei 9.250 art. 10: "desconto simplificado … 20% … limitada a … IX - R$ 16.754,34 … a partir do ano-calendário de 2015". -/
def simplifiedPct : Int := 2000
def simplifiedCap : Int := 1675434
/-- Lei 7.713 art. 6 XV (Lei 11.482 art. 2 wording, as later updated by Lei 9.250 art. 4 VI i): pensions from age 65
"R$ 1.903,98 … por mês, a partir do mês de abril do ano-calendário de 2015" exempt (12 months counted here). -/
def pension65 : Int := 12 * 190398

/-- INSS 2025 employee bands (EC 103/2019 art. 28 as readjusted; centavos, monthly). -/
def inss : Contribution :=
  { name := "INSS", sched := Schedule.ofList [(0, 750), (151800, 900), (279388, 1200), (419083, 1400)],
    ceiling := 815741 }

def toReais (cv : Int) : Int := divR .halfUp cv 100

/-- Annual INSS of an employee with `annualWage` reais paid in 12 equal months (centavos, each month rounded half up
to the centavo). -/
def inssAnnual (annualWage : Int) : Int :=
  perPeriod 12 (fun m => (Rule.mk .halfUp 1).ofTicks (inss.ticks m)) (annualWage * 100)

/-- One declaration: taxable income `ti`, INSS paid `prev`, `deps` dependants; the cheaper of the complete
(deductions) and simplified (20 %, capped) forms (art. 10 "poderá optar"). Returns (tax, form) in centavos. -/
def decl (ti prev : Int) (deps : Nat) : Int × Bool :=
  let full := (Rule.mk .halfUp 1).ofTicks (annualParcela (pos (ti - prev - dependent * deps)))
  let simp := (Rule.mk .halfUp 1).ofTicks (annualParcela (pos (ti - min simplifiedCap (divR .down (simplifiedPct * ti) BP))))
  if simp < full then (simp, true) else (full, false)

def taxable (a : Adult) (rentShare : Int) : Int :=
  (a.wages + a.selfEmployment + rentShare) * 100 + pos (a.pension * 100 - (if a.age ≥ 65 then pension65 else 0))

def out (c : Canon) : Out :=
  let n := c.nChildren
  let a1 := c.adult1
  let prev1 := inssAnnual a1.wages
  match c.adult2? with
  | none =>
    let (t, s) := decl (taxable a1 c.rentalIncome) prev1 n
    Out.make c "BR" "BRL" (toReais t) (employeeSocial := toReais prev1)
      (detail := [Out.d "taxableIncome" (toReais (taxable a1 c.rentalIncome)), Out.dStr "form" (if s then "simplificado" else "completo")])
      (unsupported := unsup c)
  | some a2 =>
    let prev2 := inssAnnual a2.wages
    let ti1 := taxable a1 (half1 c.rentalIncome)
    let ti2 := taxable a2 (half2 c.rentalIncome)
    -- children go to the declaration where they save most (each child once: Lei 9.250 art. 35 § 2)
    let optA := (decl ti1 prev1 n).1 + (decl ti2 prev2 0).1
    let optB := (decl ti1 prev1 0).1 + (decl ti2 prev2 n).1
    let t := min optA optB
    Out.make c "BR" "BRL" (toReais t) (employeeSocial := toReais (prev1 + prev2))
      (detail := [Out.d "taxableIncome" (toReais (ti1 + ti2)),
        Out.dStr "dependentsOn" (if optA ≤ optB then "adult1" else "adult2")])
      (unsupported := unsup c)
where
  unsup (c : Canon) : List String :=
    (if c.interest ≠ 0 then ["interest: taxed exclusively at source (Lei 11.033/2004 art. 1, rate by term) - not modelled, not included"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains: taxed separately (ganho de capital) - not modelled"] else []) ++
    (if c.dividends ≠ 0 then ["dividends: exempt in 2025 (Lei 9.249/1995 art. 10) - excluded, not taxed"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employed INSS (contribuinte individual 20%) not modelled; self-employment income taxed in the annual table"] else []) ++
    ["13º salário (exclusive source taxation and separate INSS) not a contract input: wages assumed in 12 equal months",
     "medical, education, alimony, private-pension (PGBL) deductions: no contract input"]

def country : Country := { code := "BR", name := "Brazil (IRPF + INSS)", currency := "BRL", year := "2025", compute := out }

/-- The schedule used by the kernel theorems (annual table, centavos). -/
def sched : Schedule := annual
theorem sched_progressive : sched.progressive = true := by decide

end BrTax
