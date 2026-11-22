import XkTax.Params

/-!
# Kosovo 2025: annual personal income tax, employee pension contribution

Unit: the individual (05/L-028: each taxpayer's annual gross income). Gross income (neni 7) includes wages, rent,
interest and capital gains; dividends (neni 8 (1) 1.26) and pensions paid by the Government (neni 8 (1) 1.13) are
exempt. The employee's 5 % pension contribution is not taxable (05/L-116 neni 37.2). The withholding on wages (neni 38
(2)) applies the same rate table to the month; for equal monthly pay the annual table and the monthly withholding give
the same tax when the monthly amounts are 1/12 (the model uses the annual table, neni 6).

Household investment income is split equally between two adults (`half1`/`half2`: reading; the law taxes the owner).
-/

namespace XkTax
open TaxKernel

def pension (w : Int) : Int := if w ≤ 0 then 0 else divR .halfUp (w * pensionEmployee) BP

def taxOf (x : Int) : Int := divR .halfUp (schedule.ticks (pos x)) BP

structure Person where
  wage : Int
  contrib : Int
  rentNet : Int
  other : Int
  taxable : Int
  tax : Int

def person (w se rent other : Int) : Person :=
  let p := pension w
  let rn := pos rent - divR .halfUp (pos rent * rentLumpRate) BP
  let taxable := pos (w - p) + se + rn + other
  { wage := w, contrib := p, rentNet := rn, other, taxable, tax := taxOf taxable }

def out (c : Canon) : Out :=
  let n := c.adults.length
  let sh := fun (x : Int) (i : Nat) => if n == 2 then (if i == 0 then half1 x else half2 x) else (if i == 0 then x else 0)
  let ps := (c.adults.zipIdx).map fun (a, i) =>
    person a.wages a.selfEmployment (sh c.rentalIncome i) (sh (c.interest + c.capitalGains) i)
  let tax := sumInts (ps.map (·.tax))
  let unsup :=
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: taken as net income of a business keeping books (neni 33); the presumptive regime for gross up to 50 000 (neni 43) and the self-employed's pension contribution not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: Government pensions are exempt (neni 8 (1) 1.13); pension-fund payments (neni 38 (4)) not modelled"] else []) ++
    (if c.charitable != 0 || c.pensionContributions != 0 then ["charitable/pensionContributions: neni 28 donations and voluntary pension contributions not modelled"] else []) ++
    ["wages below the minimum wage: the pension contribution is due on the minimum wage (04/L-101 neni 6.6); the 2025 minimum wage was not reached, so the model uses the actual wage"]
  Out.make c "XK" "EUR" tax (employeeSocial := sumInts (ps.map (·.contrib)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "pensionContribution" (sumInts (ps.map (·.contrib))),
                Out.d "dividendsExempt" (pos c.dividends),
                Out.dStr "note" "05/L-028 neni 6 as replaced by 08/L-142: 0 % to 3 000, 8 % to 5 400, 10 % above (annual); 5 % employee pension contribution deductible"])
    (unsupported := unsup)

def country : Country :=
  { code := "XK", name := "Kosovo (tatimi në të ardhurat personale, kontributi pensional)", currency := "EUR", year := "2025",
    compute := out }

end XkTax
