import TaxKernel.World

/-!
# Central African Republic: IRPP on wages, Code général des impôts 2017 "Edition officielle mise à jour 2023/DGID"
(finances.gouv.cf, `cf/law/cgi2023.pdf`), tax year 2025

* art. 36: base = "montant net des traitements, indemnités et émoluments, salaires, pensions et rentes viagères ainsi que
  de tous les avantages en argent et en nature".
* art. 38: "en déduisant du montant brut ... les frais strictement professionnels ... évalués à 30%".
* art. 39: "Sont également déductibles ... les allocations familiales ainsi que les cotisations versées à l'Etat, à la
  Caisse Nationale de Sécurité Sociale (CNSS) ...".
* art. 80: "toute fraction de revenu global net inférieur à 1000 F CFA, est négligée".
* art. 84: revenus des capitaux mobiliers "par application de 15% du montant brut des revenus distribués".
* art. 86: "barème annuel ... au revenu global net, c'est-à-dire déduction faite des cotisations sociales et des
  allocations familiales ainsi que de l'abattement pour frais professionnels fixé forfaitairement à 30%": "0- 378.0000 /
  378.001-1.680.000 / 1.680.001-3.360.000 / 3.360.001-5.040.000 / Superieur à 5.040.000 ; Taux 0% 8% 15% 28% 40%".
  The first limit is printed "378.0000" (sic); the next row starts at 378.001, so the limit is read as 378 000 (FINDINGS F2).
Loi de finances 2025 (finances.gouv.cf, scanned; OCR of pp. 1-60 `lf2025.ocr1-60.txt`): its fiscal articles 9-18 amend
CGI arts. 135 bis 4, 249, 275 bis, 344 and LPF arts. 4, 71, 88, 171, 226, 243: no wage-tax article. The 2024 finance
law was not found on the ministry's site (only the 2024 collectif, OCR checked); see PROGRESS.
Employee CNSS contributions are fixed outside the CGI and were not reached: optional input `cnssEmployee` (annual
household total, deducted per art. 39), 0 by default. The CDS (arts. 237-243, 10 %) is an employer tax: not modelled.
-/

namespace CfTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 86. -/
def sched : Schedule := Schedule.ofList [(0, 0), (378000, 800), (1680000, 1500), (3360000, 2800), (5040000, 4000)]
def fraisRate : Int := 3000   -- art. 38
def rcmRate : Int := 1500     -- art. 84

structure Person where
  frais : Int
  taxable : Int
  tax : Int
  deriving Repr

def person (w pension soc : Int) : Person :=
  let g := pos w + pos pension
  let frais := pct fraisRate g
  let taxable := toMultiple .down 1000 (pos (g - frais - soc))   -- art. 80
  { frais := frais, taxable := taxable, tax := sched.tax Rule.unitDown taxable }

def out (c : Canon) : Out :=
  let soc := (c.int? "cnssEmployee").getD 0
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
  let rcm := pct rcmRate (pos c.dividends + pos c.interest)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employment (art. 81: 30 % with a turnover minimum) not modelled"] else []) ++
    (if c.rentalIncome ≠ 0 then ["rental income not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains not modelled"] else []) ++
    (if soc = 0 then ["employee CNSS contributions not modelled (rates outside the CGI, not reached): give cnssEmployee to deduct them (art. 39)"] else [])
  Out.make c "CF" "XAF" (wageTax + rcm) (employeeSocial := soc)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "irppWages" wageTax, Out.d "ircm" rcm,
      Out.dStr "note" "IRPP on wages: gross less 30 % frais (art. 38) and CNSS (art. 39), rounded down to 1 000 (art. 80), art. 86 bands 0/8/15/28/40 %; RCM 15 % (art. 84); individual assessment"])
    (unsupported := unsup ++ ["interest taxed like distributed income at 15 % (art. 84 names 'revenus distribués'; the interest rule was not read)",
      "the 2024 finance law was not reached (CGI consolidated to 2023; LF 2025 and the 2024 collectif checked)"])

def country : Country := { code := "CF", name := "Central African Republic (IRPP)", currency := "XAF", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: gross 2 400 000: frais 720 000; taxable 1 680 000; 8 % x 1 302 000 = 104 160. -/
#guard (person 2400000 0 0).tax = 104160
/- gross 10 000 000: taxable 7 000 000: 104 160 + 252 000 + 470 400 + 40 % x 1 960 000 = 1 610 560. -/
#guard (person 10000000 0 0).tax = 1610560

end CfTax
