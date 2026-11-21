import BjTax.Params

/-!
# Benin 2025: impôt sur les traitements et salaires (ITS) with the ORTB levy, IRCM, IRF

The ITS (arts. 119-129) is withheld monthly on gross pay with no family allowance of any kind: the 2021 code has no
charges-de-famille reduction (a feature: the household's size never changes the ITS). The year is twelve equal months;
the ORTB levy is added in March (1 000 F) and June (3 000 F, waived when the month's pay is within the first band).
Pensions are not listed among the incomes subject to the ITS (art. 119): reading, not taxed. W5 pattern A (2026-11-20): the
employee CNSS pension contribution, 3,6 % of all remuneration, is reported (`employeeSocial`) and not deducted: the
ITS base is the gross pay (art. 122 1): "Le salaire mensuel imposable inclut les montants bruts ..."; arts. 120 and
124 exclude no employee contribution). Source: the CNSS page "Procédure de recouvrement des cotisations" (cnss.bj,
fetched 2026-11-20; official secondary: the décret fixing the rates under the Code de sécurité sociale 2003 art. 24 2)
was not reached): "L'assiette de cotisation est l'ensemble des rémunérations perçues par le travailleur ... Pension :
10 % dont : 6.4 % à la charge de l'employeur 3.6 % à la charge du salarié". No ceiling. `"w5Contrib": false` restores
the pre-W5 model.
-/

namespace BjTax
open TaxKernel

def months : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
def monthOf (annual : Int) (m : Int) : Int := annual * m / 12 - annual * (m - 1) / 12

def monthTax (g : Int) : Int := divR .down (monthly.ticks (pos g)) BP

/-- Art. 125 2): the ORTB levy of month `m` on pay `g` (only when pay is due that month). -/
def ortb (m g : Int) : Int :=
  if g ≤ 0 then 0 else if m == 3 then ortbMarch else if m == 6 then (if g ≤ firstBand then 0 else ortbJune) else 0

def itsYear (w : Int) : Int := sumInts (months.map fun m => monthTax (monthOf w m))

/-- W5 pattern A: CNSS pension, salarié 3,6 % of all remuneration (CNSS page), no ceiling. -/
def cnssSalBp : Int := 360
def cnssYear (w : Int) : Int := divR .down (pos w * cnssSalBp) BP
#guard 640 + cnssSalBp = 1000 ∧ cnssYear 1000000 = 36000
def ortbYear (w : Int) : Int := sumInts (months.map fun m => ortb m (monthOf w m))

def out (c : Canon) : Out :=
  let ws := c.adults.map (·.wages)
  let w5 := (c.bool? "w5Contrib").getD true
  let es := if w5 then sumInts (ws.map cnssYear) else 0
  let its := sumInts (ws.map itsYear)
  let levy := sumInts (ws.map ortbYear)
  let ircm := divR .down (pos c.dividends * dividendRate + pos c.interest * interestRate) BP
  let irf := if c.rentalIncome > 0 then divR .down (c.rentalIncome * irfRate) BP + irfOrtb else 0
  let unsup :=
    ["lois de finances 2024 and 2025 not reached: amounts are the CGI 2023 edition's",
     (if w5 then "employeeSocial: CNSS salarié 3,6 % (CNSS page, official secondary), not deducted from the ITS (art. 122)" else "employeeSocial: CNSS employee contribution not modelled (rate not read)")] ++
    (if c.adults.any (·.pension != 0) then ["pension: not among the incomes subject to ITS (art. 119); not taxed (reading)"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: 5 % on share disposals (art. 86 1)) not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: IBA not modelled"] else [])
  Out.make c "BJ" "XOF" (its + ircm + irf) (surtaxes := [("ORTB", levy)]) (employeeSocial := es)
    (detail := [Out.d "cnssEmployee" es, Out.d "its" its, Out.d "ortb" levy, Out.d "ircm" ircm, Out.d "irf" irf,
                Out.d "taxableIncome" (sumInts (ws.map pos)),
                Out.dStr "note" "CGI 2021-15 (édition 2023): monthly ITS on gross pay art. 125 (0/10/15/19/30 %), ORTB 1 000 + 3 000; IRCM 10 % / 15 %; IRF 12 % + 4 000"])
    (unsupported := unsup)

def country : Country :=
  { code := "BJ", name := "Benin (ITS, ORTB, IRCM, IRF)", currency := "XOF", year := "2025", compute := out }

end BjTax
