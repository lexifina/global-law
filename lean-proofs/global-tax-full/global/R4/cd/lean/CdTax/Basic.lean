import TaxKernel.World

/-!
# DR Congo: impôt professionnel sur les rémunérations (IPR), Ordonnance-loi n° 69/009 du 10 février 1969 relative
aux impôts cédulaires sur les revenus, as consolidated in the DGI's "Code des impôts mis à jour au 10 juillet 2023"
(dgi.gouv.cd, `cd/law/CODE-DES-IMPOTS-2023.pdf`), calendar year 2025

* art. 47: taxable remunerations (wages, salaries, allowances, pensions "de toute nature"...).
* art. 48 1°-3°: immune: family allowances within the legal rates; statutory old-age pensions; housing allowance "ne
  dépasse 30% du traitement brut", transport within six taxi/bus fares a day, medical costs.
* art. 50: deductible: payments "à des caisses de pension officielles" (employee pension contributions).
* art. 84 (L.F. 18/025, 19/005) §1: "3% ... de 0,00 FC à 1.944.000,00 FC ; 15% ... de 1.944.001,00 FC à 21.600.000,00
  FC ; 30% ... de 21.600.001,00 FC à 43.200.000,00 FC ; 40% pour le surplus"; §2 "En aucun cas, l'impôt total ne peut
  excéder 30% du revenu imposable"; §4 "l'impôt professionnel individuel ... après déduction des charges de famille
  prévues à l'article 89 ... ne peut être inférieur à 2.000 Francs congolais par mois".
* art. 88: incomes "arrondis à la dizaine de Franc congolais inférieure ou supérieure" (nearest 10, 5 down).
* art. 89 (L.F. 19/005): "réduit d'une quotité de 2% pour chacun des membres de la famille à charge ... avec un maximum
  de 9 personnes"; art. 90: dependants = the wife, unmarried children, ascendants in the household.
The IS/IRPP reform (Loi n° 23/053 du 30 novembre 2023, JO numéro spécial 29 décembre 2023; dgi.gouv.cd copy, OCR)
"entre en vigueur après vingt-quatre mois à compter du 31 décembre de l'année de sa promulgation" (art. 153): from
2026, so 2025 is still under the IPR. The 2024 and 2025 finance laws were not reached (the consolidation stops at
10 July 2023): access B. Employee CNSS contribution: rate not reached; optional input `cnssEmployee` (annual
household total, deducted per art. 50).
W5 pattern A (2026-11-20): **Décret n° 18/041 du 24 novembre 2018 fixant les taux de cotisations dues à la CNSS**
(Leganet copy, Internet Archive capture 2020-04-18; `cd/law/w5/`), art. 3: "Le taux des cotisations sociales dues à la
Caisse Nationale de Sécurité Sociale au titre de la branche des pensions est fixé à 10 % réparti comme suit : - 5 % à
charge de l'employeur ; - 5 % à charge du travailleur"; art. 10: the transitional 3,5 % applied only until 1 January
2019; art. 11: in force on signature. Family allowances (art. 2, 6,5 %) and occupational risks (art. 4, 1,5 %) are the
employer's alone (Loi n° 16/009 du 15 juillet 2016 art. 16; art. 18: the pension rate is shared, the worker's part at
most half). No ceiling in the Decree or the Law; Loi 16/009 art. 13 and Decree art. 8: the base is never below the SMIG
(not applied: the model has no SMIG and an annual wage need not be 12 full months). The worker's 5 % is a payment to an
official pension fund, deducted under art. 50. Input `cnssEmployee` (annual household total), when given, replaces the
statutory amount as before; `"w5Contrib": false` restores the pre-W5 model (no contribution unless the input is given).
-/

namespace CdTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 84 §1. -/
def sched : Schedule := Schedule.ofList [(0, 300), (1944000, 1500), (21600000, 3000), (43200000, 4000)]
def capRate : Int := 3000           -- art. 84 §2
def perDependant : Int := 200       -- art. 89 (2 % of the tax)
def maxDependants : Nat := 9        -- art. 89
def minMonth : Int := 2000          -- art. 84 §4

/-- W5 pattern A: Décret 18/041 art. 3, the worker's share of the pensions branch (5 % of remuneration, no ceiling). -/
def cnssWorkerBp : Int := 500
def cnssWorker (w : Int) : Int := divR .down (pos w * cnssWorkerBp) 10000
/- Decree art. 3 prints 10 % = 5 % + 5 %: the worker's half of the pensions branch. -/
#guard cnssWorkerBp * 2 = 1000 ∧ cnssWorker 12000000 = 600000 ∧ cnssWorker (-5) = 0

/-- art. 88: nearest 10 FC, a fraction of 5 FC rounds down. -/
def round10 (x : Int) : Int := 10 * divR .halfDown x 10

/-- Tax on one earner's yearly taxable remuneration `r` with `deps` dependants. -/
def ipr (r : Int) (deps : Nat) : Int :=
  if r ≤ 0 then 0 else
  let r := round10 r
  let t := min (sched.tax Rule.unitHalfUp r) (pct capRate r)
  let d : Int := min deps maxDependants
  let reduced := t - pct (perDependant * d) t
  max (12 * minMonth) reduced

def out (c : Canon) : Out :=
  let socIn := (c.int? "cnssEmployee").getD 0
  let w5 := (c.bool? "w5Contrib").getD true
  let useStat := w5 && socIn == 0
  let stat : List Int := c.adults.map (fun a => cnssWorker a.wages)
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
  -- art. 90: the wife and the children are dependants of the (first) earner
  let deps (i : Nat) : Nat := if i = 0 then c.nChildren + (if c.married && n = 2 then 1 else 0) else 0
  let tax := sumInts ((c.adults.zip (List.range n)).map fun (a, i) => ipr (pos a.wages - share i) (deps i))
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income (impôt professionnel sur les bénéfices) not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["impôt mobilier, impôt sur les revenus locatifs and gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions: statutory old-age pensions are immune (art. 48 2°); not added"] else []) ++
    (if useStat then ["CNSS worker 5 % (Décret 18/041 art. 3) on wages: the SMIG floor of the base (Loi 16/009 art. 13) not applied"]
     else if soc = 0 then ["employee CNSS contribution not modelled (rate not reached): give cnssEmployee to deduct it (art. 50)"] else [])
  Out.make c "CD" "CDF" tax (employeeSocial := soc)
    (detail := [Out.d "ipr" tax,
      Out.dStr "note" "IPR: wages less pension contributions, rounded to 10 FC, art. 84 bands 3/15/30/40 % capped at 30 % of the income, less 2 % per dependant (max 9, art. 89), at least 2 000 FC a month"])
    (unsupported := unsup ++ ["dependants (the wife and all children) are given to the first adult", "housing/transport allowances immune within art. 48 3° limits are not in the household contract",
      "the 2024 and 2025 finance laws were not reached (consolidation to 10 July 2023)"])

def country : Country := { code := "CD", name := "DR Congo (IPR)", currency := "CDF", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: 12 000 000 FC, no dependant: 58 320 + 15 % x 10 056 000 = 1 566 720. With 3 dependants: less 6 %. -/
#guard ipr 12000000 0 = 1566720 ∧ ipr 12000000 3 = 1472717
/- The 30 % cap binds above 77 932 800: at 100 000 000 the tax is 30 000 000, not 9 486 720 + 40 % x 56 800 000. -/
#guard ipr 100000000 0 = 30000000
/- The monthly minimum: 1 000 000 a year would give 30 000, the minimum is 24 000; 600 000 gives 18 000 -> 24 000. -/
#guard ipr 600000 0 = 24000

end CdTax
