import TaxKernel.World

/-!
# Madagascar: impôt sur les revenus salariaux et assimilés (IRSA), Code des impôts "mis à jour suivant la LFI 2025"
(impots.mg, Codes et Manuels, "CDI _ LFI 2025.pdf", fetched from a second machine 2026-11-20; `mg/law/cdi_lfi2025.pdf`),
tax year 2025

* art. 01.03.09: deductions: "1° Les retenues ... en vue de la constitution de pensions ou de retraite, dans la limite
  de 10p.100 du montant brut"; "2° ... cotisation ouvrière due à une organisation sanitaire ... dans la limite de 2p.100
  du salaire brut".
* art. 01.03.11: "La base imposable mensuelle ou mensualisée est calculée par l'employeur".
* art. 01.03.16: "la base ... arrondie à la centaine d'Ariary inférieure ... le montant de l'impôt à payer est égal à
  la somme des résultats de chaque tranche sans toutefois être inférieur à Ar 3000. A. Droit commun - jusqu'à
  Ar 350 000 : 0p.100 ; - ... de Ar 350 001 à Ar 400 000 : 5p.100 ; - ... de Ar 400 001 à Ar 500 000 : 10p.100 ; - ...
  de Ar 500 001 à Ar 600 000 : 15p.100 ; - tranche de revenu supérieure à 600 000 : 20p100."
* art. 01.03.19: "ayant un revenu imposable supérieur à Ar 350 000 ont droit à raison de chaque personne à charge, à
  une réduction d'impôt d'Ar 2 000 par mois ... ne doit pas avoir pour effet de ramener le montant de l'impôt au-dessous
  du minimum"; dependants: children under 21 (25 if students) and dependent ascendants; the reduction goes to the
  spouse who receives the family allowances.
* art. 01.04.04: impôt sur le revenu des capitaux mobiliers (interest) "fixé à 20p.100", "libératoire".
The CDI "LFI 2026" (same folder) adds a 25 % band above Ar 4 000 000 from 2026: the 2025 tariff above is the last
before it. CNaPS / health-organisation employee contributions: rates not reached (cnaps.mg gives none); optional input
`cnapsEmployee` (annual household total, deducted within the 10 % limit), 0 by default.
W5 pattern A (2026-11-20): CNaPS worker contribution 1 % of remuneration up to the art. 37 ceiling. Ceiling: **Code de
prévoyance sociale** (as published by the CNaPS, cnaps.mg document "cps", Internet Archive capture 2023-01-24;
`mg/law/w5/`) art. 37: "Le montant des rémunérations à prendre pour base de calcul des cotisations ne peut être
inférieur au montant des salaires minima réglementaires. Les rémunérations dépassant huit fois la valeur du Salaire
Minimum d'Embauche de la Catégorie M1 du Code du Travail ne sont retenues que pour ce montant." Rate: the CNaPS page
"Taux des cotisations" (capture 2011-05-25): "REGIME EMPLOYEUR TRAVAILLEUR Général 13% 1%" (official secondary: the
arrêté fixing the rates was not reached; no later change found). SME of the régime général in force 1 March 2024 -
28 February 2026: Ar 262 680 a month (CNaPS public SME table `api/public/sme`, capture 2026-10-26, official secondary;
the next value, 300 000 from 1 March 2026, carries "plafondMensuel" 2 400 000 = 8 x 300 000, confirming the 8 x SME
rule). 2025 ceiling: 8 x 262 680 = Ar 2 101 440 a month. Deducted as a pension retention (art. 01.03.09 1°, within
10 %). Not modelled: the SME floor of the base (art. 37 first sentence; the model's annual wage need not be 12 full
months) and the 1 % health-organisation (SMIE) share, which depends on the employer's organisation. Input
`cnapsEmployee`, when given, replaces the statutory amount as before; `"w5Contrib": false` restores the pre-W5 model.
-/

namespace MgTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 01.03.16 A (monthly). -/
def sched : Schedule := Schedule.ofList [(0, 0), (350000, 500), (400000, 1000), (500000, 1500), (600000, 2000)]
def minimum : Int := 3000        -- art. 01.03.16
def perDependant : Int := 2000   -- art. 01.03.19
def depThreshold : Int := 350000 -- art. 01.03.19
def ircmRate : Int := 2000       -- art. 01.04.04

/-- W5 pattern A: CNaPS worker 1 % (CNaPS rate table), on wages up to 8 x SME (CPS art. 37), SME 2025 Ar 262 680. -/
def cnapsWorkerBp : Int := 100
def sme2025 : Int := 262680
def cnapsCeilingMonth : Int := 8 * sme2025
/-- Annual worker contribution on an annual wage paid evenly over 12 months. -/
def cnapsWorker (w : Int) : Int := divR .down (min (pos w) (12 * cnapsCeilingMonth) * cnapsWorkerBp) 10000
#guard cnapsCeilingMonth = 2101440
#guard cnapsWorker 12000000 = 120000 ∧ cnapsWorker 100000000 = 252172

/-- One month's IRSA on the monthly base `b` (after deductions) with `deps` dependants. -/
def irsaMonth (b : Int) (deps : Nat) : Int :=
  let base := toMultiple .down 100 (pos b)
  let t := sched.tax Rule.unitDown base
  let red := if base > depThreshold then perDependant * (deps : Int) else 0
  max minimum (t - red)

def person (w soc : Int) (deps : Nat) : Int :=
  if w ≤ 0 then 0 else
  let socAllowed := min (pos soc) (pct 1000 w)
  perPeriod 12 (fun m => irsaMonth m deps) (w - socAllowed)

def out (c : Canon) : Out :=
  let deps := c.childrenUnder 21
  let socIn := (c.int? "cnapsEmployee").getD 0
  let w5 := (c.bool? "w5Contrib").getD true
  let useStat := w5 && socIn == 0
  let stat : List Int := c.adults.map (fun a => cnapsWorker a.wages)
  let soc := if useStat then sumInts stat else socIn
  let n := c.adults.length
  /- W5 review pass 2 (sweep P2-6): the household-total employee contribution is allotted to the adults in
  proportion to their wages (each person's own contribution is deducted from that person's income); it was halved, which
  gave a one-earner couple half its deduction. Halves only when nobody has wages. -/
  let socW : List Int := c.adults.map (fun a => pos a.wages)
  let wsumS := sumInts socW
  let socBy (x : Int) (i : Nat) : Int :=
    if n ≤ 1 then x else if wsumS = 0 then (if i = 0 then half1 x else half2 x)
    else if i = 0 then x - divR .down (x * socW.getD 1 0) wsumS else divR .down (x * socW.getD 1 0) wsumS
  let share (i : Nat) : Int := if useStat then stat.getD i 0 else socBy soc i
  -- art. 01.03.19: the reduction goes to one spouse (the one receiving family allowances): taken as the one for
  -- whom it is worth more (an election; elections.json)
  let taxWith (j : Nat) : Int := sumInts ((c.adults.zip (List.range n)).map fun (a, i) => person a.wages (share i) (if i = j then deps else 0))
  let tax := if n = 2 then min (taxWith 0) (taxWith 1) else taxWith 0
  let ircm := pct ircmRate (pos c.interest)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employment (impôt sur les revenus IR) not modelled"] else []) ++
    (if c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["dividends, rental income and capital gains (IR, IRI) not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions: retirement pensions are exempt (art. 01.03.03 2°); not added"] else []) ++
    (if useStat then ["CNaPS worker 1 % up to 8 x SME modelled; the SME floor (CPS art. 37) and the health-organisation (SMIE) worker share are not: give cnapsEmployee for the full total"]
     else if soc = 0 then ["employee CNaPS / health contributions not modelled (rates not reached): give cnapsEmployee"] else [])
  Out.make c "MG" "MGA" (tax + ircm) (employeeSocial := soc)
    (detail := [Out.d "irsa" tax, Out.d "ircm" ircm,
      Out.dStr "note" "IRSA monthly: base rounded down to 100 Ar, bands 0/5/10/15/20 % (350 000/400 000/500 000/600 000), minimum Ar 3 000 a month, Ar 2 000 a month per dependant above 350 000; IRCM 20 % on interest"])
    (unsupported := unsup ++ ["wages paid evenly over 12 months (IRSA is monthly)", "dependants: children under 21 only (students to 25 and ascendants not counted)"])

def country : Country := { code := "MG", name := "Madagascar (IRSA)", currency := "MGA", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: 1 000 000 a month: 2 500 + 10 000 + 15 000 + 80 000 = 107 500; with 2 dependants 103 500. -/
#guard irsaMonth 1000000 0 = 107500 ∧ irsaMonth 1000000 2 = 103500
/- The minimum: no tax on 300 000 a month, but Ar 3 000 is due. -/
#guard irsaMonth 300000 0 = 3000
/- At 350 100 the dependants' reduction starts and is floored by the minimum: 5 + 0 -> 3 000. -/
#guard irsaMonth 350100 1 = 3000

/- The Ar 3 000 minimum swallows the dependants' reduction at low pay: 400 000 a month pays 3 000 with or without
   two children (2 500 - 4 000 < 3 000). -/
#guard irsaMonth 400000 2 = 3000 ∧ irsaMonth 400000 0 = 3000

end MgTax
