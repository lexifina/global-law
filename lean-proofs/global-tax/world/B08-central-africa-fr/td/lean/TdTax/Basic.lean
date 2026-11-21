import TaxKernel.World

/-!
# Chad: IRPP on wages ("impôt sur les revenus du travail"), tax year 2025

Sources (archived copies of dgi.td, the tax directorate's site, which now answers 403/suspended; files in `td/law/`):
* Loi de finances 2023 (dgi.td/docs/lf/LF2023.pdf, archived 2023-05-27; scanned, OCR `lf2023.ocr61-88.txt`, numbers
  checked against the page images), art. 36: from 1 January 2023 the CGI's article 1 reads: "I- Il est établi un impôt
  annuel sur le revenu des personnes physiques ... assis d'une part sur les revenus du travail et d'autre part sur les
  revenus du capital. II- Constituent les Revenus du Travail : 1° Traitements, salaires, indemnités, émoluments et rentes
  viagères ... IV- Le calcul de l'Impôt sur les Revenus du Travail se fait par application du Barème progressif ...
  0 à 800 000 : 0% ; 800 001 à 6 000 000 : 10,5% ; 6 000 001 à 7 500 000 : 15% ; 7 500 001 à 9 000 000 : 20% ;
  9 000 001 à 12 000 000 : 25% ; Plus de 12 000 000 : 30% (Le reste sans changement)". The unchanged V reads "Le calcul
  de l'Impôt sur les Revenus du Capital se fait par application du taux de 20% au revenu net de chaque catégorie."
* Loi de finances 2025 (archived 2025-04-06, scanned, OCR `lf2025.ocr.txt`): no change to art. 1; art. 116 no longer
  refers to "the tarif fixé par l'article 115" (the old quotient tariff); art. 82 and 90 (capital income withholding,
  plus-values 18 %) amended. LF 2024 circular (archived 2024-02-16): Prélèvement pour la Sécurité Alimentaire (PSA)
  "Le tarif du PSA est de 400 FCFA et s'applique sur l'ensemble des traitements et salaires" (monthly; official
  secondary: the LF 2024 text itself was archived truncated).
* The wage base: the current CGI was not reached (only the 2016 edition is archived). CGI 2016 art. 47 I (deduct
  "les retenues faites par l'employeur en vue de la constitution des pensions ... dans la limite de 3.5 % des
  appointements, ainsi que les retenues effectuées au titre de la sécurité sociale") and art. 48 I ("une déduction de
  40 % est appliquée au montant net") are applied, flagged in `unsupported`. The 2016 family quotient (arts. 109-111,
  tariff art. 115) is not applied: art. 1 IV as rewritten taxes the work income on the barème directly and LF 2025
  dropped art. 116's reference to the art. 115 tariff.
Employee CNPS contributions: rate not reached; optional input `cnpsEmployee` (annual household total), 0 by default.
-/

namespace TdTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- CGI art. 1 IV as rewritten by LF 2023 art. 36. -/
def sched : Schedule := Schedule.ofList [(0, 0), (800000, 1050), (6000000, 1500), (7500000, 2000), (9000000, 2500), (12000000, 3000)]
def deduction : Int := 4000      -- CGI 2016 art. 48 I (assumed unchanged)
def capitalRate : Int := 2000    -- CGI art. 1 V
def psaMonth : Int := 400        -- LF 2024 (circular 001)

structure Person where
  taxable : Int
  tax : Int
  deriving Repr

def person (w pension soc : Int) : Person :=
  let net := pos (pos w + pos pension - soc)
  let taxable := toMultiple .down 1000 (pos (net - pct deduction net))
  { taxable := taxable, tax := sched.tax Rule.unitDown taxable }

def out (c : Canon) : Out :=
  let soc := (c.int? "cnpsEmployee").getD 0
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
  let ps := (c.adults.zip (List.range n)).map fun (a, i) => person a.wages a.pension (share i)
  let wageTax := sumInts (ps.map (·.tax))
  let capTax := pct capitalRate (pos c.interest + pos c.dividends)
  let psa := 12 * psaMonth * (c.adults.filter (·.wages > 0)).length
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employment (revenus du travail: BIC/BNC) not modelled"] else []) ++
    (if c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["rental income and capital gains (art. 1 V 20 %, plus-values art. 90) not modelled"] else []) ++
    (if soc = 0 then ["employee CNPS contribution not modelled (rate not reached): give cnpsEmployee to deduct it"] else [])
  Out.make c "TD" "XAF" (wageTax + capTax) (surtaxes := [("PSA", psa)]) (employeeSocial := soc)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "irppTravail" wageTax, Out.d "irppCapital" capTax,
      Out.dStr "note" "Revenus du travail: wages less social contributions and 40 % (CGI 2016 arts. 47-48), barème art. 1 IV (LF 2023): 0/10.5/15/20/25/30 %; capital income 20 % (art. 1 V); PSA 400 FCFA a month"])
    (unsupported := unsup ++ ["the wage base (40 % deduction, pension cap 3.5 %) is the CGI 2016 rule: the current CGI's art. 9-II, which art. 1 IV cites, was not reached",
      "no family quotient: the 2016 arts. 109-111 are taken as superseded by the 2023 art. 1 IV (not verified against a current CGI)"])

def country : Country := { code := "TD", name := "Chad (IRPP revenus du travail)", currency := "XAF", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: gross 6 000 000: less 40 % = 3 600 000; 10.5 % x 2 800 000 = 294 000. -/
#guard (person 6000000 0 0).tax = 294000
/- gross 30 000 000: 18 000 000: 546 000 + 225 000 + 300 000 + 750 000 + 30 % x 6 000 000 = 3 621 000. -/
#guard (person 30000000 0 0).tax = 3621000

end TdTax
