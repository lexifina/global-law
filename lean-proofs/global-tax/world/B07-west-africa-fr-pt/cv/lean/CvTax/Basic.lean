import CvTax.Params

/-!
# Cabo Verde 2025: IRPS (englobamento of category A), liberatory taxes on capital and property income

Art. 45.º: on englobamento the tax is: gross income of each category less its specific deductions → collectable
income; less the mínimo de existência; times the art. 46.º rates → colecta; less the deductions of art. 53.º-55.º.
Art. 45.º 2.: "Da soma dos rendimentos colectáveis é subtraído o mínimo de existência, dividindo-se o resultado por
dois, quando se trata de casados dois titulares" (splitting, as Portugal's quociente conjugal): reading, a married
couple subtracts one mínimo per spouse (art. 46.º 2.: "Por cada sujeito passivo") and the tax is twice the tax on half.
The category A specific deductions (art. 28.º 2.: compulsory social-security contributions, union dues): the INPS
quotização is deducted from wages (W5 pattern A, below). Pensions are category A income (art. 57.º 3.).
W5 pattern A (2026-11-20): Portaria Conjunta nº 28/2024 de 16 de julho (B.O. I Série nº 66, 16/07/2024, pp. 1482-1483,
boe.incv.cv; `cv/law/w5/`), art. 2.º 1.: "A taxa global de contribuições é fixada em 24,5% das remunerações devidas
... sendo: a) a quotização a cargo do trabalhador igual à 8,5% da sua remuneração ilíquida"; art. 4.º revokes Portaria
Conjunta 27/2017; art. 5.º in force the day after publication (17/07/2024), so all of 2025. No ceiling or floor in the
Portaria. Deducted under art. 28.º 2. a). Input `"w5Contrib": false` drops it and its deduction.
-/

namespace CvTax
open TaxKernel

def taxOn (x : Int) : Int := divR .down (sched.ticks (pos x)) BP

/-- Art. 45.º-46.º, 54.º: the englobamento tax of a tax unit with `n` taxpayers (1, or 2 married), collectable income
`inc`, `deps` dependants. -/
def irps (n inc deps : Int) : Int :=
  let base := pos (inc - n * minimoExistencia)
  let colecta := if n == 2 then 2 * taxOn (base / 2) else taxOn base
  pos (colecta - min dependantCap (perDependant * deps))

/-- Portaria Conjunta 28/2024 art. 2.º 1. a): worker's quotização 8,5 % of gross remuneration. -/
def inps (w : Int) : Int := divR .down (850 * pos w) BP

#guard inps 1000000 = 85000

def out (c : Canon) : Out :=
  let kids : Int := c.childrenUnder childAgeLimit
  let married := c.married && c.adults.length == 2
  let w5 := (c.bool? "w5Contrib").getD true
  let q (a : Adult) : Int := if w5 then inps a.wages else 0
  let incs := c.adults.map fun a => pos a.wages - q a + pos a.pension
  let catA :=
    if married then irps 2 (sumInts incs) kids
    else sumInts ((incs.zipIdx).map fun (x, i) => if x ≤ 0 then 0 else irps 1 x (if i == 0 then kids else 0))
  let capT := divR .down ((pos c.interest + pos c.dividends) * capitalRate) BP
  let rentT := divR .down (pos c.rentalIncome * rentalRate) BP
  let unsup :=
    ["category A: annual tax by englobamento (art. 45.º); the default liberatory progressive withholding tables (art. 47.º, 70.º-71.º, legislação específica) were not read",
     "budgets 2022-2024 not read for IRPS amendments (OE 2025 read: none)",
     "art. 46.º rates read as band rates (reading A); see FINDINGS for the whole-income reading"] ++
    (if c.capitalGains != 0 then ["capitalGains: category E (1 % / 20 %) not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: category B not modelled"] else [])
  let es := sumInts (c.adults.map q)
  Out.make c "CV" "CVE" (catA + capT + rentT) (employeeSocial := es)
    (detail := [Out.d "inpsEmployee" es, Out.d "irpsCategoryA" catA, Out.d "capitalTax" capT, Out.d "rentalTax" rentT,
                Out.d "taxableIncome" (pos (sumInts incs - (if married then 2 else c.adults.length) * minimoExistencia)),
                Out.dStr "note" "Código do IRPS (Lei 78/VIII/2014, republished by Lei 116/IX/2021): englobamento art. 45-46 (16,5/23,1/27,5 %, mínimo 220 000, married splitting), dependants 5 000 each (max 25 000); cat. D 20 %, cat. C 10 % liberatory"])
    (unsupported := unsup)

def country : Country :=
  { code := "CV", name := "Cabo Verde (IRPS)", currency := "CVE", year := "2025", compute := out }

end CvTax
