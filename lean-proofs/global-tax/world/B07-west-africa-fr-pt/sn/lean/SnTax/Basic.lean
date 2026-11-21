import SnTax.Params

/-!
# Senegal 2025: impôt sur le revenu (IR), TRIMF, final withholdings on investment income

Unit: the individual. Art. 59 1.: "Chaque contribuable est soumis à l'impôt sur le revenu en raison de ses revenus
personnels"; spouses are taxed separately. The family enters only through the number of parts of art. 174 2., which
sets a *reduction of the tax* (art. 174 1.), not an income quotient: the registry's "family-quotient" description is
corrected here (the parts choose a row of a rate/minimum/maximum table).

Parts (art. 174 2.-4.): single, divorced or widowed without child 1; married without child 1,5; each dependent child
gives "de façon égale, une demi-part au profit de chacun des parents disposants de revenus"; "Dans la mesure où un seul
conjoint dispose de revenus imposables, il lui est attribué une demi-part supplémentaire"; at most 5 parts. Reading:
the table's "Marié" row applies to each married spouse who files, and the extra half-part of 3. is added to it (a
married sole earner without children has 2 parts). Cohabiting unmarried partners are two single taxpayers; children go
to each parent with income (last sentence of 174 2.).

Investment income: dividends 10 % and bank interest 8 % are final withholdings (arts. 203 2. a), 209); rents are
net revenus fonciers (gross less 30 %, art. 68 c)) added to the global income (art. 54 II), or, as an election, the CGF
of arts. 74-78. Employee social contributions (IPRES, IPM) are not modelled: no accessible text (`unsupported`).
-/

namespace SnTax
open TaxKernel

/-- Art. 168 b): net taxable wage after the 30 % flat deduction capped at 900 000 F. -/
def wageNet (w : Int) : Int :=
  if w ≤ 0 then 0 else w - min (w * wageAbatRate / BP) wageAbatCap

/-- Art. 164 1.: pensions after the 40 % deduction, at least 1 800 000 F (never more than the pension). -/
def pensionNet (p : Int) : Int :=
  if p ≤ 0 then 0 else pos (p - max (p * pensionAbatRate / BP) pensionAbatMin)

/-- Art. 66-68: net rental income = gross less the 30 % flat deduction (other charges of art. 68 a), b), d) are not in
the contract). A deficit is carried forward (art. 69), not set against other income: floored at 0 here. -/
def rentalNet (r : Int) : Int :=
  if r ≤ 0 then 0 else r - r * rentalAbatRate / BP

/-- Art. 78: the contribution globale foncière on the gross annual rent (elected under art. 75, at most 30 M). -/
def cgf (r : Int) : Int :=
  if r ≤ 0 then 0 else
  let t := if r ≤ 12000000 then r / 12 else if r ≤ 18000000 then r * 15 / 120 else r * 2 / 12
  max t cgfMin

/-- Art. 173 1.: income rounded down to the thousand. -/
def roundIncome (x : Int) : Int := toMultiple .down incomeRounding (pos x)

/-- Art. 173 1.: the tax of the barème on the rounded income (exact in francs: thousands × whole percent). -/
def grossTax (taxable : Int) : Int := divR .down (sched.ticks (roundIncome taxable)) BP

/-- Art. 174 1.: the family reduction for `n2` half-parts (rate × tax, between the row's minimum and maximum, never
more than the tax). Reading: the rate × tax product is rounded down to the franc. -/
def reduction (n2 tax : Int) : Int :=
  match redTable.find? (fun r => r.1 == min n2 maxHalfParts) with
  | some (_, r, mn, mx) => min tax (clamp mn mx (tax * r / BP))
  | none => 0

/-- Art. 173-174: the IR of one taxpayer with `n2` half-parts; art. 174 1. caps it at 43 % of the taxable income. -/
def irTax (n2 taxable : Int) : Int :=
  let ti := roundIncome taxable
  let t := grossTax ti
  min (t - reduction n2 t) (ti * taxCapRate / BP)

/-- Art. 282: the TRIMF of one beneficiary of wages or pensions, by gross income band. -/
def trimf (gross : Int) : Int :=
  match trimfTable.find? (fun r => gross ≥ r.1) with
  | some (_, a) => a
  | none => 900

/-- Number of half-parts of one taxpayer (art. 174 2.-4.; reading in the module docstring). -/
def halfParts (married soleEarner : Bool) (kids : Int) : Int :=
  let base : Int := if married then 3 else 2
  let extra : Int := if married && soleEarner then 1 else 0
  min maxHalfParts (base + extra + kids)

/-- One adult's income items (whole francs). -/
structure Person where
  wages : Int
  pension : Int
  se : Int
  rentNet : Int
  hasIncome : Bool

def out (c : Canon) : Out :=
  let kids : Int := c.childrenUnder childAgeLimit
  let rentalElect := (c.str? "snRental").getD "ir"
  let useCgf := rentalElect == "cgf" && c.rentalIncome > 0 && c.rentalIncome ≤ cgfLimit
  let rentForIr := if useCgf then 0 else c.rentalIncome
  let n := c.adults.length
  -- rents of a couple split equally between the spouses (reading: joint ownership)
  let rentShare : List Int := if n == 2 then [half1 rentForIr, half2 rentForIr] else [rentForIr]
  let people : List Person := (c.adults.zip rentShare).map fun (a, r) =>
    { wages := a.wages, pension := a.pension, se := a.selfEmployment, rentNet := rentalNet r,
      hasIncome := a.wages > 0 || a.pension > 0 || a.selfEmployment > 0 || r > 0 }
  let earners := people.filter (·.hasIncome)
  let married := c.married && n == 2
  let sole := married && earners.length == 1
  -- art. 55 3. and 5.: household-level deductions claimed by the first adult (reading)
  let p1wages := (c.adults.headD {}).wages
  let volPen := min (pos c.pensionContributions) (p1wages * volPensionCapRate / BP)
  let netIncome (p : Person) : Int := wageNet p.wages + pensionNet p.pension + p.se + p.rentNet
  let taxes := (people.zipIdx).map fun (p, i) =>
    if !p.hasIncome then (0, 0) else
    let ni := netIncome p
    let gift := if i == 0 then min (pos c.charitable) (ni * giftCapRate / BP) else 0
    let ded := if i == 0 then volPen + gift else 0
    let ti := pos (ni - ded)
    -- children: a half-part each to every parent with income (art. 174 2.)
    (irTax (halfParts married sole kids) ti, roundIncome ti)
  let ir := sumInts (taxes.map (·.1))
  let taxable := sumInts (taxes.map (·.2))
  let divT := divR .down (pos c.dividends * dividendRate) BP
  let intT := divR .down (pos c.interest * bankInterestRate) BP
  let cgfT := if useCgf then cgf c.rentalIncome else 0
  -- TRIMF: each beneficiary of wages or pensions; a married earner also pays it for a spouse without income (art. 276)
  let trimfs := people.map fun p =>
    if p.wages > 0 || p.pension > 0 then trimf (p.wages + p.pension) * (if sole then 2 else 1) else 0
  let trimfT := sumInts trimfs
  let unsup :=
    ["employeeSocial: IPRES pension and IPM health contributions not modelled (no accessible text of their rates)"] ++
    (if c.capitalGains != 0 then ["capitalGains: plus-values on securities (art. 173 2., 25 % or declared) not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: taken as net BNC/BIC income at the barème; CGU, réel simplifié (art. 172) and patente not modelled"] else []) ++
    (if c.children.any (fun ch => ch.age ≥ childAgeLimit && ch.age < 25) then ["children 18-24: dependants only if students (art. 177 1.), not expressible; not counted"] else [])
  Out.make c "SN" "XOF" (ir + divT + intT + cgfT) (localIncomeTax := trimfT)
    (detail := [Out.d "irBareme" ir, Out.d "taxableIncome" taxable, Out.d "dividendTax" divT,
                Out.d "interestTax" intT, Out.d "cgf" cgfT, Out.d "trimf" trimfT,
                Out.dStr "note" "CGI 2012-31 (DGID edition Jan. 2025): wages less 30 % (cap 900 000), barème art. 173 on income rounded to 1 000, family reduction art. 174 by parts; TRIMF art. 282 as local tax; dividends 10 % and bank interest 8 % final"])
    (unsupported := unsup)

def country : Country :=
  { code := "SN", name := "Senegal (impôt sur le revenu, TRIMF)", currency := "XOF", year := "2025", compute := out }

end SnTax
