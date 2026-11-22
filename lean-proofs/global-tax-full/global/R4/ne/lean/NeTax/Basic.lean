import NeTax.Params

/-!
# Niger 2025: impôt sur les traitements et salaires (ITS), IRCM

Monthly tax (art. 61, 66) on the month's net pay after the art. 60 deductions and the family abatement of art. 64-65
(a percentage of the net income); the year is twelve equal months. Pensions of any kind are exempt (art. 54 4)).
The family charges of a household (at most 7) are shared between spouses by a form they file (art. 65); reading: all
to the higher earner.
W5 pattern A (2026-11-20): the worker's CNSS pension contribution, 5,25 % of pay up to the annual ceiling of
6 000 000 F (500 000 a month on 12 equal months), is reported and deducted first under art. 60 1) (within its 6 %
limit), before the 13 % of art. 60 4) "sur le salaire imposable". Source: the CNSS "Guide de l'employeur" (Décembre
2019; cnss.ne/wp-content/uploads/2021/07/GUIDE-EMPLOYEURS.pdf, fetched 2026-11-20; official secondary: the rate
décret was not reached; `ne/law/w5/`): "11.50 % au titre de la branche des retraites dont 5.25 % à la charge du
travailleur et 6.25 % à la charge de l'employeur"; "Le plafond annuel considéré dans le calcul des cotisations est de
6.000.000 F.CFA. La partie des salaires qui dépasse ce plafond annuel n'est pas prise en compte"; the SMIG floor
(30 047 F a month) is not applied. `"w5Contrib": false` restores the pre-W5 model.
-/

namespace NeTax
open TaxKernel

def months : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
def monthOf (annual : Int) (m : Int) : Int := annual * m / 12 - annual * (m - 1) / 12

/-- Art. 60 (without the pension retention), 64-65, 61: the month's taxable base. -/
def baseMonth (n g : Int) : Int :=
  if g ≤ 0 then 0 else
  let net := g - g * proAbat / BP
  let afterFam := net - net * familyAbat n / BP
  toMultiple .down rounding (pos afterFam)

def itsMonth (n g : Int) : Int := divR .down (monthly.ticks (baseMonth n g)) BP

def itsYear (n w : Int) : Int := sumInts (months.map fun m => itsMonth n (monthOf w m))

/-- W5 pattern A: CNSS worker 5,25 % (retraite) of the month's pay up to 500 000 (6 000 000 a year; CNSS guide 2019). -/
def cnssTravBp : Int := 525
def cnssPlafondMonth : Int := 6000000 / 12
def cnssMonth (g : Int) : Int := divR .down (min (pos g) cnssPlafondMonth * cnssTravBp) BP
/-- Art. 60 1) then 4): the 13 % applies to the pay after the pension retention. -/
def baseMonthR (n g : Int) : Int :=
  if g ≤ 0 then 0 else
  let s := g - cnssMonth g
  let net := s - s * proAbat / BP
  let afterFam := net - net * familyAbat n / BP
  toMultiple .down rounding (pos afterFam)
def itsYearR (n w : Int) : Int := sumInts (months.map fun m => divR .down (monthly.ticks (baseMonthR n (monthOf w m))) BP)
def cnssYear (w : Int) : Int := sumInts (months.map fun m => cnssMonth (monthOf w m))
/- The guide: 11,50 % = 5,25 % + 6,25 %; 5,25 % is within the art. 60 1) 6 % limit; at the ceiling 26 250 a month. -/
#guard cnssTravBp + 625 = 1150 ∧ cnssTravBp ≤ pensionDedCap ∧ cnssMonth 500000 = 26250 ∧ cnssMonth 900000 = 26250

def out (c : Canon) : Out :=
  let kids : Int := min maxChildren (c.children.filter (·.age ≤ childMaxAge)).length
  let married := c.married && c.adults.length == 2
  let ws := c.adults.map (·.wages)
  let top := ws.foldl max 0
  let idxTop := (ws.findIdx? (· == top)).getD 0
  let spouse : Int := if married && ws.any (· ≤ 0) then 1 else 0
  let w5 := (c.bool? "w5Contrib").getD true
  let its := sumInts ((ws.zipIdx).map fun (w, i) =>
    if w ≤ 0 then 0 else (if w5 then itsYearR else itsYear) (if i == idxTop then min 7 (kids + spouse) else 0) w)
  let es := if w5 then sumInts (ws.map cnssYear) else 0
  let divT := divR .down (pos c.dividends * dividendRate) BP
  let intT := divR .down (pos c.interest * bankInterestRate) BP
  let unsup :=
    ["lois de finances 2023 and 2024 not reached: ITS arts. 60-66 in their LF 2022 wording",
     (if w5 then "employeeSocial: CNSS worker 5,25 % up to 6 000 000 a year (CNSS guide 2019, official secondary), deducted (art. 60 1)); SMIG floor not applied" else "employeeSocial: CNSS employee contributions not modelled (rates not read); the art. 60 1) pension deduction is therefore not taken")] ++
    (if c.rentalIncome != 0 then ["rentalIncome: impôt sur les revenus fonciers not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: 7 % on shares (art. 74 nouveau) not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: BIC/BNC not modelled"] else [])
  Out.make c "NE" "XOF" (its + divT + intT) (employeeSocial := es)
    (detail := [Out.d "its" its, Out.d "dividendTax" divT, Out.d "interestTax" intT,
                Out.d "taxableIncome" (sumInts ((ws.zipIdx).map fun (w, i) =>
                  sumInts (months.map fun m => baseMonth (if i == idxTop then min 7 (kids + spouse) else 0) (monthOf w m)))),
                Out.dStr "note" "CGI 2012-37 (MAJ LF 2022) arts. 60-66: monthly ITS, 13 % abattement, family abatement 5-30 %, income rounded to 1 000; LF 2025 IRVM 10 %; IRC 10 % bank deposits"])
    (unsupported := unsup)

def country : Country :=
  { code := "NE", name := "Niger (ITS, IRCM)", currency := "XOF", year := "2025", compute := out }

end NeTax
