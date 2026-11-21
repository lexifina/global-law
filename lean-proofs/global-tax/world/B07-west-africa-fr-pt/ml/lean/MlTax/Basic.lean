import MlTax.Params

/-!
# Mali 2025: impôt sur les traitements et salaires (ITS), IRF, IRVM

ITS (arts. 1-13): annual barème on wages and pensions (art. 2 1°: pensions are taxable), less the family reduction of
art. 11 (a percentage of the gross tax), less the two-point reduction of art. 12-A (reading in Params). Each earning
spouse is taxed separately with the married 10 %; the children's 2,5 % each go to the spouse who has them in charge
(reading: the higher earner; the spouses may share the children's rate by request).
W5 pattern A (2026-11-20): employee INPS contributions, assurance vieillesse 3,6 % and AMO 3,06 % of all remuneration
(no ceiling), reported; the 3,6 % pension retention is deducted under CGI art. 7 a) ("Les retenues faites par
l'employeur en vue de la constitution de pensions ou de retraites dans la limite de 4 % des salaires bruts"), the AMO
share is not (not a pension retention). Source: the INPS "Guide du cotisant" (inps.ml, PDF of 10 August 2013,
Internet Archive capture 2021-09-23; official secondary: the rate texts were not reached; `ml/law/w5/`): "Les taux de
cotisations par branche ... L'assurance maladie obligatoire : part de l'employeur 3,50% part du salarié 3,06% ...
Assurance vieillesse : part de l'employeur 3,4% part du salarié 3,6%"; base: Code de prévoyance sociale art. 187
"les cotisations sociales sont assises sur l'ensemble des rémunérations du salarié" (no ceiling stated). Later rate
changes after 2013 were not checked. `"w5Contrib": false` restores the pre-W5 model.
-/

namespace MlTax
open TaxKernel

/-- Family reduction rate of one taxpayer (art. 11). -/
def famRate (married : Bool) (kids : Int) : Int :=
  (if married then marriedRed else 0) + childRed * min kids maxChildren

/-- Art. 9-12-B: annual ITS of one taxpayer. -/
def its (married : Bool) (kids income : Int) : Int :=
  if income ≤ 0 then 0 else
  let t := divR .down (sched.ticks income) BP
  let afterFam := t - divR .down (t * famRate married kids) BP
  pos (afterFam - divR .down (income * twoPoints) BP)

/-- W5 pattern A: INPS salarié, vieillesse 3,6 % and AMO 3,06 % (INPS guide 2013), all remuneration. -/
def inpsVieillesseBp : Int := 360
def amoSalBp : Int := 306
def inpsPension (w : Int) : Int := divR .down (pos w * inpsVieillesseBp) BP
def amoSal (w : Int) : Int := divR .down (pos w * amoSalBp) BP
/- Art. 7 a): the pension retention is deductible up to 4 % of gross pay; 3,6 % is within it. -/
#guard inpsVieillesseBp ≤ 400 ∧ inpsPension 1000000 = 36000 ∧ amoSal 1000000 = 30600

def out (c : Canon) : Out :=
  let w5 := (c.bool? "w5Contrib").getD true
  let kids : Int := c.childrenUnder childAgeLimit
  let married := c.married && c.adults.length == 2
  let inc := c.adults.map fun a => pos a.wages - (if w5 then inpsPension a.wages else 0) + pos a.pension
  let es := if w5 then sumInts (c.adults.map fun a => inpsPension a.wages + amoSal a.wages) else 0
  let top := inc.foldl max 0
  let idxTop := (inc.findIdx? (· == top)).getD 0
  let itsT := sumInts ((inc.zipIdx).map fun (x, i) => its married (if i == idxTop then kids else 0) x)
  let irf := divR .down (toMultiple .down 1000 (pos c.rentalIncome) * irfRate) BP
  let irvm := divR .down (pos c.dividends * dividendRate + pos c.interest * depositInterestRate) BP
  let unsup :=
    ["CGI consolidation of 2017 (DGI online code): lois de finances 2018-2025 not reached; amounts may be stale",
     (if w5 then "employeeSocial: INPS 3,6 % + AMO 3,06 % from the INPS guide (2013, official secondary); 3,6 % deducted (art. 7 a))" else "employeeSocial: INPS and AMO employee contributions not modelled (rates not read); the art. 7 a) pension deduction not taken"),
     "art. 12-A two-point reduction read as 2 % of taxable income (wording ambiguous)"] ++
    (if c.capitalGains != 0 then ["capitalGains: taxe sur les plus-values not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: IBIC/IBNC and the synthetic tax not modelled"] else [])
  Out.make c "ML" "XOF" (itsT + irf + irvm) (employeeSocial := es)
    (detail := [Out.d "its" itsT, Out.d "irf" irf, Out.d "irvm" irvm, Out.d "taxableIncome" (sumInts inc),
                Out.dStr "note" "CGI Mali (DGI online code, 2017 consolidation): ITS art. 10 barème, art. 11 family reduction 10 % + 2,5 % per child, art. 12-A two points; IRF 12 %; IRVM 10 % / 9 %"])
    (unsupported := unsup)

def country : Country :=
  { code := "ML", name := "Mali (ITS, IRF, IRVM)", currency := "XOF", year := "2025", compute := out }

end MlTax
