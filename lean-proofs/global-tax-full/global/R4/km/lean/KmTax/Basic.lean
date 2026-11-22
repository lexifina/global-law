import TaxKernel.World

/-!
# Comoros: IRPP on wages, Code général des impôts 2022 (Ministère des Finances, finances.gouv.km
"Comores-CGI-2022.pdf", Internet Archive copy 2022-10-22; `km/law/cgi2022.pdf`), tax year 2025

* art. 57: base = "montant brut des traitements, indemnités, émoluments, salaires, pensions et rentes viagères ainsi que
  de tous les avantages en nature ou en argent".
* art. 59: deduct "a) Les retenues ... en vue de la constitution des pensions ou au titre de la sécurité sociale. b) Les
  versements effectués personnellement par le salarié ... En aucun cas, le total des sommes admises en déduction en vertu
  des dispositions des alinéas a et b ci-dessus ne peut excéder 6 % du montant brut des appointements. c) ... La
  déduction ... des frais professionnels est fixée forfaitairement à 30 % revenu brut après défalcation des retenues
  ou versements visés aux alinéas a et b".
* art. 97: "barème unique progressif : 5 % sur la fraction du revenu compris entre 150.001 et 500.000 FC ; 10 % ...
  entre 500.001 et 1.000.000 FC ; 15 % ... entre 1.000.001 et 1.500.000 FC ; 20 % ... entre 1.500.001 et 2.500.000 FC ;
  25 % ... entre 2.500.001 et 3.500.000 FC ; 30 % sur la fraction du revenu compris entre 3.500.000 FC et plus."
The finance laws for 2023 and 2025 were not reached; the 2024 finance law (Loi n° 23-019/AU, promulgated by décret
n° 23-134/PR; archived finances.gouv.km copy, scanned) is OCR-checked for art. 59/97 changes (PROGRESS.md). Access B.
Employee social contributions: rate not reached; optional input `socialEmployee` (annual household total; deducted
within the 6 % cap).
-/

namespace KmTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 97. -/
def sched : Schedule := Schedule.ofList [(0, 0), (150000, 500), (500000, 1000), (1000000, 1500), (1500000, 2000), (2500000, 2500), (3500000, 3000)]
def socCap : Int := 600      -- art. 59 (6 % of gross)
def frais : Int := 3000      -- art. 59 c)

def person (w soc : Int) : Int × Int :=
  let g := pos w
  let s := min (pos soc) (pct socCap g)
  let afterSoc := pos (g - s)
  let taxable := pos (afterSoc - pct frais afterSoc)
  (taxable, sched.tax Rule.unitDown taxable)

def out (c : Canon) : Out :=
  let soc := (c.int? "socialEmployee").getD 0
  let n := c.adults.length
  /- W5 review pass 2 (sweep P2-6): the household-total employee contribution is allotted to the adults in
  proportion to their wages (each person's own contribution is deducted from that person's income); it was halved, which
  gave a one-earner couple half its deduction. Halves only when nobody has wages. -/
  let socW : List Int := c.adults.map (fun a => pos a.wages)
  let wsumS := sumInts socW
  let socBy (x : Int) (i : Nat) : Int :=
    if n ≤ 1 then x else if wsumS = 0 then (if i = 0 then half1 x else half2 x)
    else if i = 0 then x - divR .down (x * socW.getD 1 0) wsumS else divR .down (x * socW.getD 1 0) wsumS
  let share (i : Nat) : Int := socBy soc i
  let ps := (c.adults.zip (List.range n)).map fun (a, i) => person (a.wages + a.pension) (share i)
  let tax := sumInts (ps.map (·.2))
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income (art. 98 turnover minimum) not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["revenus de valeurs mobilières, rents and gains not modelled"] else []) ++
    (if soc = 0 then ["employee social contributions not modelled (rate not reached): give socialEmployee"] else [])
  Out.make c "KM" "KMF" tax (employeeSocial := soc)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.1))), Out.d "irppWages" tax,
      Out.dStr "note" "IRPP on wages: gross less pension/social deductions (cap 6 %) less 30 % frais (art. 59), art. 97 bands 0/5/10/15/20/25/30 %; individual"])
    (unsupported := unsup ++ ["the 2023 and 2025 finance laws were not reached", "wages and pensions summed per person (art. 57)"])

def country : Country := { code := "KM", name := "Comoros (IRPP)", currency := "KMF", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: 3 000 000 FC gross: taxable 2 100 000; 17 500 + 50 000 + 75 000 + 20 % x 600 000 = 262 500. -/
#guard (person 3000000 0).2 = 262500

end KmTax
