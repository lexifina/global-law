import TaxKernel.World

/-!
# Gabon: IRPP with the family quotient and the taxe complémentaire sur les traitements et salaires (TCS),
Code général des impôts 2025 (dgi.ga, `ga/law/cgi2025.pdf`, "Code général des impôts 2025"), tax year 2025

* art. 75: "Chaque chef de famille est imposable à l'IRPP, tant en raison de ses bénéfices et revenus personnels que de
  ceux de sa femme et de ses enfants" (joint return of a married couple).
* art. 92 (L.F.2022): base = "montant net des traitements ... après déduction des retenues de cotisations sociales
  obligatoires faites par l'employeur, en vue de la constitution de pensions ou de retraites, du bénéfice de l'assurance
  maladie ...".
* art. 94 (L.F.2024): "les frais professionnels évalués forfaitairement à 20 %, mais limités à 10.000.000 FCFA".
* art. 168: "le revenu imposable, arrondi au millier de francs CFA inférieur, est divisé en parts ... L'impôt brut est
  égal au produit de la cotisation ainsi obtenu par le nombre de parts."
* art. 170: parts: single 1; married, or single/divorced with one child, 2; then "+ une demi-part par enfant à la charge
  du contribuable, dans la limite de six enfants".
* art. 174: per part, "De 0 à 1.500.000 FCFA : 0; De 1.500.001 à 1.920.000 : 5 % x Q - 75.000; ... 1.920.001 à
  2.700.000 : 10 % x Q - 171.000; 2.700.001 à 3.600.000 : 15 % x Q - 306.000; 3.600.001 à 5.160.000 : 20 % x Q -
  486.000; 5.160.001 à 7.500.000 : 25 % x Q - 744.000; 7.500.001 à 11.000.000 : 30 % x Q - 1.119.000; 11.000.001 et
  plus : 35 % x Q - 1.669.000".
* arts. 346-351 TCS: "La part de revenu inférieure ou égale à 150.000 FCFA par mois est exonérée" (art. 347); base =
  the art. 92 net (art. 348); "fixé à 5 %" (art. 349); "déductible du montant brut du revenu" (art. 351).
* art. 109: revenus des capitaux mobiliers: "prélèvement libératoire dont le taux est fixé à 20 %".
CNAMGS (health insurance): cnamgs.ga "Paiement des cotisations" (official page, Internet Archive copy 2025-08-15, same
text on 2026-11-20): "Le plafond mensuel des salaires soumis à cotisation est de 2 500 000 FCFA ... Secteur privé:
(Décret n°0022… art. 38) ... Cotisations salariales : 2%" (official secondary: the decree itself was not reached).
The employee CNSS (pension) rate was not reached: optional input field `cnssEmployee` (annual household total,
deducted per art. 92), 0 by default.
-/

namespace GaTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 174 as printed (rate x Q - subtraction). -/
def rows : List SubRow :=
  [ {lo := 0, rate := 0, subtract := 0}, {lo := 1500001, rate := 500, subtract := 75000},
    {lo := 1920001, rate := 1000, subtract := 171000}, {lo := 2700001, rate := 1500, subtract := 306000},
    {lo := 3600001, rate := 2000, subtract := 486000}, {lo := 5160001, rate := 2500, subtract := 744000},
    {lo := 7500001, rate := 3000, subtract := 1119000}, {lo := 11000001, rate := 3500, subtract := 1669000} ]
/-- The same tariff as bands. -/
def sched : Schedule := Schedule.ofList
  [(0, 0), (1500000, 500), (1920000, 1000), (2700000, 1500), (3600000, 2000), (5160000, 2500), (7500000, 3000), (11000000, 3500)]
/- The printed subtractions are exactly the band tariff (checked at every threshold and between). -/
#guard subAgrees rows sched [0, 1500000, 1500001, 1700000, 1920000, 1920001, 2700000, 2700001, 3600000, 3600001,
  5160000, 5160001, 7500000, 7500001, 11000000, 11000001, 30000000]

def fraisRate : Int := 2000       -- art. 94
def fraisCap : Int := 10000000    -- art. 94
def tcsRate : Int := 500          -- art. 349
def tcsFreeMonth : Int := 150000  -- art. 347
def rcmRate : Int := 2000         -- art. 109
def cnamgsRate : Int := 200       -- CNAMGS page (Décret 0022 art. 38), private sector employee
def cnamgsCapMonth : Int := 2500000

/-- Tax per part on `q` (whole francs). -/
def perPart (q : Int) : Int := sched.tax Rule.unitDown q

/-- art. 170: half-parts. -/
def halfParts (married : Bool) (kids : Nat) : Int :=
  let k : Int := min kids 6
  if married then 4 + k
  else if k = 0 then 2 else 4 + (k - 1)

/-- art. 168: tax of a household on its rounded taxable income `r` with `n2` half-parts. -/
def irpp (n2 r : Int) : Int := quotient perPart n2 (toMultiple .down 1000 r)

structure Person where
  net : Int
  tcs : Int
  frais : Int
  taxable : Int
  deriving Repr

/-- One earner: wages (and pensions, same category, art. 90) net of the employee contributions `soc`. -/
def cnamgs (w : Int) : Int := perPeriod 12 (fun m => pct cnamgsRate (min m cnamgsCapMonth)) (pos w)

def person (w pension soc : Int) : Person :=
  let net := pos (pos w + pos pension - cnamgs w - soc)
  let tcs := perPeriod 12 (fun m => pct tcsRate (pos (m - tcsFreeMonth))) net
  let afterTcs := pos (net - tcs)
  let frais := min (pct fraisRate afterTcs) fraisCap
  { net := net, tcs := tcs, frais := frais, taxable := pos (afterTcs - frais) }

def out (c : Canon) : Out :=
  let kids := c.childrenUnder 18
  let soc := (c.int? "cnssEmployee").getD 0
  let cnam := sumInts (c.adults.map fun a => cnamgs a.wages)
  let n := c.adults.length
  /- W5 review pass 2 (sweep P2-6): the household-total employee contribution is allotted to the adults in
  proportion to their wages (each person's own contribution is deducted from that person's income); it was halved, which
  gave a one-earner couple half its deduction. Halves only when nobody has wages. -/
  let socW : List Int := c.adults.map (fun a => pos a.wages)
  let wsumS := sumInts socW
  let socBy (x : Int) (i : Nat) : Int :=
    if n ≤ 1 then x else if wsumS = 0 then (if i = 0 then half1 x else half2 x)
    else if i = 0 then x - divR .down (x * socW.getD 1 0) wsumS else divR .down (x * socW.getD 1 0) wsumS
  let socShare (i : Nat) : Int := socBy soc i
  let ps := (c.adults.zip (List.range n)).map fun (a, i) => person a.wages a.pension (socShare i)
  let tcs := sumInts (ps.map (·.tcs))
  let rcm := pct rcmRate (pos c.interest + pos c.dividends)
  let tax :=
    if c.married && n = 2 then irpp (halfParts true kids) (sumInts (ps.map (·.taxable)))
    else
      -- unmarried adults are separate taxpayers; the children go to the first adult (art. 170 single parent)
      sumInts ((ps.zip (List.range n)).map fun (p, i) => irpp (halfParts false (if i = 0 then kids else 0)) p.taxable)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employment (BIC/BNC, impôt minimum forfaitaire art. 175) not modelled"] else []) ++
    (if c.rentalIncome ≠ 0 then ["rental income (revenus fonciers) not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains not modelled"] else []) ++
    (if soc = 0 then ["employee CNSS pension contribution not modelled (rate not reached): give cnssEmployee to deduct it (art. 92); CNAMGS 2 % is modelled"] else [])
  Out.make c "GA" "XAF" (tax + rcm) (surtaxes := [("TCS", tcs)]) (employeeSocial := soc + cnam)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "halfParts" (if c.married && n = 2 then halfParts true kids else halfParts false kids),
      Out.d "irppWages" tax, Out.d "ircm" rcm, Out.d "tcs" tcs,
      Out.dStr "note" "IRPP: (net wage - TCS) less 20 % frais (cap 10 M), rounded to 1 000, family quotient art. 170 (max 6 children), art. 174 tariff; TCS 5 % above 150 000 a month; RCM 20 % libératoire"])
    (unsupported := unsup ++ ["wages paid evenly over 12 months (TCS is monthly)", "children counted: under 18 (art. 172 also counts students up to 28)"])

def country : Country := { code := "GA", name := "Gabon (IRPP quotient + TCS)", currency := "XAF", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed cases. Single, wages 6 000 000: CNAMGS 2 % = 120 000; net 5 880 000; TCS 5 % x (490 000 - 150 000)
   x 12 = 204 000; after TCS 5 676 000; frais 1 135 200; taxable 4 540 800 -> 4 540 000; one part:
   20 % x 4 540 000 - 486 000 = 422 000. -/
#guard (out { id := "g", adults := [{ wages := 6000000 }] }).incomeTax = 422000
/- Married, same wage, no child: two parts of 2 270 000: 10 % x 2 270 000 - 171 000 = 56 000, x 2 = 112 000. -/
#guard (out { id := "g", married := true, adults := [{ wages := 6000000 }, {}] }).incomeTax = 112000
#guard halfParts false 1 = 4 ∧ halfParts true 1 = 5 ∧ halfParts true 9 = 10

end GaTax
