import TaxKernel.World

/-!
# Burundi: impôt sur le revenu d'emploi (IRE), Loi n° 1/14 du 24 décembre 2020 portant modification de la loi
n° 1/02 du 24 janvier 2013 relative aux impôts sur les revenus, calendar year 2025

Source: obr.bi (Office Burundais des Recettes; the site now fails with an application error), Internet Archive copy
of "Loi_Impôt_sur_le_revenu__24_décembre.pdf" (2025-05-20; scanned; OCR `bi/law/loi_ir_2020.ocr.txt`, the numbers below
checked on the page images).
* art. 21: "le montant des revenus imposables appartenant aux revenus d'emploi et aux revenus locatifs est arrondi au
  millier de francs burundais le plus proche et imposé par tranches selon le tableau suivant : 0 - 1.800.000 : 0% ;
  1.800.001 - 3.600.000 : 20% de la part qui dépasse 1.800 000 ; 3.600.001 et plus : 30% de la part qui dépasse
  3.600 000".
* art. 30 6°: employment income includes "les pensions, les rentes ... suite au départ à la retraite"; art. 32 5°
  excludes the same pensions from the employment income (FINDINGS F2).
* art. 33: deductible: "1° la part salariale des cotisations de retraite ..."; "2° la part salariale des cotisations
  d'assurance-maladie"; "3° les frais de déplacement ne dépassant pas 15% du salaire de base ..."; "4° le loyer ou
  indemnités compensatoires ne dépassant pas 60% du salaire de base"; complementary pension contributions only "à
  hauteur de vingt pour cent (20%) du revenu d'emploi brut".
* Loi de finances 2025/2026 (archived obr.bi copy 2025-07-23; OCR pp. 1-70) restates art. 30 (art. 138, same list) and
  amends art. 122: "Une retenue de quinze pour cent (15%) est pratiquée sur ... 1° les dividendes ... 2° les paiements
  d'intérêts" (art. 139); art. 21 and art. 33 are not amended. The 2024/2025 finance law (January-June 2025) was not
  found in the archive: access B.
Employee INSS / health contributions: rates not reached; optional input `inssEmployee` (annual household total).
Transport and housing allowances (art. 33 3°-4°): optional input `allowances` (annual, per household, taken as within
the 15 % / 60 % limits of the base salary), 0 by default.
-/

namespace BiTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 21. -/
def sched : Schedule := Schedule.ofList [(0, 0), (1800000, 2000), (3600000, 3000)]
def withholdingRate : Int := 1500   -- art. 122 as amended by LF 2025/2026 art. 139

def ire (taxable : Int) : Int := sched.tax Rule.unitDown (toMultiple .halfUp 1000 (pos taxable))

/-- Allowances deductible under art. 33 3°-4°: at most 75 % of the base salary (15 % + 60 %). Here the base salary is
`w - a` when `a` of the gross `w` is paid as allowances. -/
def allowedAllowances (w a : Int) : Int := min (pos a) (pct 7500 (pos (w - pos a)))

def person (w soc allow : Int) : Int := ire (pos w - soc - allowedAllowances w allow)

def out (c : Canon) : Out :=
  let soc := (c.int? "inssEmployee").getD 0
  let allow := (c.int? "allowances").getD 0
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n ≤ 1 then x else if i = 0 then half1 x else half2 x
  /- W5 review pass 2 (sweep P2-6): the household-total employee contribution is allotted to the adults in
  proportion to their wages (each person's own contribution is deducted from that person's income); it was halved, which
  gave a one-earner couple half its deduction. Halves only when nobody has wages. -/
  let socW : List Int := c.adults.map (fun a => pos a.wages)
  let wsumS := sumInts socW
  let socBy (x : Int) (i : Nat) : Int :=
    if n ≤ 1 then x else if wsumS = 0 then (if i = 0 then half1 x else half2 x)
    else if i = 0 then x - divR .down (x * socW.getD 1 0) wsumS else divR .down (x * socW.getD 1 0) wsumS
  let tax := sumInts ((c.adults.zip (List.range n)).map fun (a, i) => person a.wages (socBy soc i) (share allow i))
  let wh := pct withholdingRate (pos c.interest + pos c.dividends)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income not modelled"] else []) ++
    (if c.rentalIncome ≠ 0 then ["rental income (same art. 21 tariff, separate base) not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions: excluded by art. 32 5° (included by art. 30 6°; FINDINGS F2); not taxed"] else []) ++
    (if soc = 0 then ["employee INSS / health contributions not modelled (rates not reached): give inssEmployee"] else [])
  Out.make c "BI" "BIF" (tax + wh) (employeeSocial := soc)
    (detail := [Out.d "ire" tax, Out.d "withholding15" wh,
      Out.dStr "note" "IRE: (wages - employee contributions - transport/housing allowances within 15 %/60 % of base salary) rounded to the nearest 1 000, art. 21: 0 / 20 % / 30 % above 1.8 M / 3.6 M; dividends and interest 15 % withholding (art. 122, LF 2025/2026)"])
    (unsupported := unsup ++ ["the 15 % withholding on interest and dividends is taken as final", "the January-June 2025 finance law (2024/2025) was not reached"])

def country : Country := { code := "BI", name := "Burundi (impôt sur le revenu d'emploi)", currency := "BIF", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: 6 000 000 a year: 20 % x 1 800 000 + 30 % x 2 400 000 = 1 080 000. -/
#guard person 6000000 0 0 = 1080000
/- The same 6 000 000 paid as a base salary of 3 428 572 plus 2 571 428 of housing and transport allowances (75 % of
   the base): taxable 3 428 572 -> 3 429 000: 20 % x 1 629 000 = 325 800. -/
#guard person 6000000 0 2571428 = 325800
/- Rounding to the nearest thousand: 1 800 499 rounds down to 1 800 000 (no tax), 1 800 500 up to 1 801 000 (200). -/
#guard ire 1800499 = 0 ∧ ire 1800500 = 200

end BiTax
