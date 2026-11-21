import TaxKernel.World

/-!
# Republic of the Congo: IRPP with the family quotient, Code général des impôts tome I (finances.gouv.cg,
"CGI Tome I.pdf", posted 2021-03-28, `cg/law/cgi_tome1.pdf`), and the social-security rates of the 2025 finance law,
tax year 2025

* art. 4: "Chaque chef de famille est imposable tant en raison de ses revenus personnels que de ceux de sa femme ...
  La femme mariée fait l'objet d'une imposition distincte : 1° Lorsqu'elle est bénéficiaire des revenus salariaux
  uniquement; en ce cas, elle est considérée comme mariée sans enfants".
* art. 40: deduct "1° Les retenues faites par l'employeur en vue de la constitution des pensions ... dans la limite de
  6 % des appointements ; 2° Les retenues faites au titre de la sécurité sociale".
* art. 41: "une déduction de 20 % est appliquée au montant net".
* art. 89: "le revenu imposable, arrondi au millier de franc inférieur, est divisé en un certain nombre de parts ...
  L'impôt brut est égal au produit de la cotisation ainsi obtenue par le nombre de parts".
* art. 91: parts 1 / married 2 / single with one child 2 / + "une demi-part par enfant à charge ... jusqu'à un maximum
  de 6,5 parts".
* art. 93: children under 21 (25 if students).
* art. 95 I: "1% à la fraction de revenu n'excédant pas 200.000 francs, 15% ... entre 200.001 et 800.000 francs, 30%
  ... entre 800.001 et 2.500.000 francs, 45% ... entre 2.500.001 et 8.000.000 de francs, 50% à la fraction au dessus de
  8.000.000 de francs. Lorsque le revenu global du contribuable est inférieur à 265.000 francs, la cotisation n'est pas
  mise en recouvrement."
* Loi n° 47-2024 du 30 décembre 2024 portant loi de finances pour l'année 2025 (JO spécial 2024-15, sgg.cg), article
  neuvième: CNSS "cotisations de l'employé : 4,55%"; caisse d'assurance maladie universelle (CAMU) "cotisations de
  l'employé : 2,27%". (No ceiling is stated there; the CNSS ceiling is fixed elsewhere and was not reached.)
Finance laws checked for changes to arts. 4, 39-41, 89-95: LF 2022 (Loi 51-2021), LF 2023 (Loi 77-2022), LF 2024
(Loi 39-2023), LF 2025 (Loi 47-2024): none found (grep of the JO texts; PROGRESS.md). Amendments before 2022 that the
2021 posting might not carry were not checked: access B.
-/

namespace CgTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 95 I. -/
def sched : Schedule := Schedule.ofList [(0, 100), (200000, 1500), (800000, 3000), (2500000, 4500), (8000000, 5000)]
def deduction : Int := 2000        -- art. 41
def floorGlobal : Int := 265000    -- art. 95 I last sentence
def cnssRate : Int := 455          -- LF 2025 art. 9
def camuRate : Int := 227          -- LF 2025 art. 9

/-- art. 91: half-parts of a married taxpayer (`married`) or a single one with `kids` children, at most 13 (6.5 parts). -/
def halfParts (married : Bool) (kids : Nat) : Int :=
  let k : Int := kids
  min 13 (if married then 4 + k else if k = 0 then 2 else 4 + (k - 1))

def perPart (q : Int) : Int := sched.tax Rule.unitDown q

/-- arts. 89, 95: tax on a taxable income `r` (before rounding) with `n2` half-parts; not collected below 265 000. -/
def irpp (n2 r : Int) : Int :=
  let r := toMultiple .down 1000 r
  if r < floorGlobal then 0 else quotient perPart n2 r

structure Person where
  social : Int
  taxable : Int
  deriving Repr

def person (w pension : Int) : Person :=
  let w := pos w
  let social := pct cnssRate w + pct camuRate w
  let net := pos (w + pos pension - social)
  { social := social, taxable := pos (net - pct deduction net) }

def out (c : Canon) : Out :=
  let kids := c.childrenUnder 21
  let ps := c.adults.map fun a => person a.wages a.pension
  let p1 := ps.headD { social := 0, taxable := 0 }
  let social := sumInts (ps.map (·.social))
  -- art. 4 1°: the wife (second adult) with wage income only is assessed separately as "mariée sans enfants"
  let wifeSeparate := c.married && c.adults.length = 2 &&
    (match c.adults[1]? with | some a => a.wages > 0 && a.selfEmployment = 0 | none => false)
  let tax :=
    if c.married && c.adults.length = 2 then
      if wifeSeparate then
        irpp (halfParts true kids) p1.taxable + irpp (halfParts true 0) (ps.getD 1 p1).taxable
      else irpp (halfParts true kids) (sumInts (ps.map (·.taxable)))
    else
      sumInts ((ps.zip (List.range ps.length)).map fun (p, i) => irpp (halfParts false (if i = 0 then kids else 0)) p.taxable)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employment not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 then ["capital income (IRVM, credited against IRPP: art. 89) not modelled"] else []) ++
    (if c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["rental income and capital gains not modelled"] else [])
  Out.make c "CG" "XAF" tax (employeeSocial := social)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "wifeAssessedSeparately" (if wifeSeparate then 1 else 0),
      Out.dStr "note" "IRPP: wages less CNSS 4.55 % and CAMU 2.27 % (LF 2025 art. 9), less 20 % (art. 41), rounded to 1 000, family quotient (art. 91, max 6.5 parts), art. 95 bands 1/15/30/45/50 %, nothing collected below 265 000; a married woman with wage income only is assessed separately with 2 parts (art. 4 1°)"])
    (unsupported := unsup ++ ["the second adult of a married couple is taken as the wife for art. 4 1°",
      "no CNSS ceiling applied (not in the finance law; the ceiling text was not reached)",
      "taxe d'occupation des locaux (TOL) withheld with the IRPP: not modelled (CGI tome II not read)"])

def country : Country := { code := "CG", name := "Republic of the Congo (IRPP quotient)", currency := "XAF", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: single, wages 3 000 000: social 136 500 + 68 100 = 204 600; net 2 795 400; less 20 % (559 080) =
   2 236 320 -> 2 236 000; one part: 2 000 + 90 000 + 30 % x 1 436 000 = 522 800. -/
#guard (out { id := "g", adults := [{ wages := 3000000 }] }).incomeTax = 522800
/- The 265 000 threshold is all-or-nothing: 264 999 of taxable income pays nothing, 265 000 pays 2 000 + 9 750. -/
#guard irpp 2 264999 = 0 ∧ irpp 2 265000 = 11750

end CgTax
