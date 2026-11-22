import TaxKernel

/-!
# Toy country "ZZ" (not a real statute): the shape of a country file built from kernel parts

A personal allowance of 12,000 withdrawn by 1/2 above 100,000 (`Taper`), a three-band schedule (`Schedule`), a
5 % surcharge on tax above 1,000 of tax (`Surcharge`), a child credit of 1,000 per child withdrawn at 5 % above
60,000 (`Credit`), employee contributions of 8 % up to a ceiling (`Social`), separate assessment (`Unit`).
-/

namespace ZzTax
open TaxKernel

def allowance : Taper := { full := 12000, start := 100000, num := 1, den := 2 }
def sched : Schedule := Schedule.ofList [(0, 2000), (40000, 4000), (150000, 4500)]
def soli : Surcharge := { rate := 500, exempt := 1000 }
def childCredit (n : Nat) : Credit := { full := 1000 * n, start := 60000, num := 5, den := 100 }
def pension : Contribution := Contribution.flatCapped "pension" 800 90000

/-- One adult's income tax (units). -/
def personTax (inc : Int) : Int :=
  let ti := taxableAfter (allowance.amount inc) inc
  sched.tax Rule.unitDown ti

theorem sched_progressive : sched.progressive = true := by decide

def out (c : Canon) : Out :=
  let incs := c.adults.map fun a => a.wages + a.selfEmployment + a.pension
  let inv := c.interest + c.dividends + c.capitalGains + c.rentalIncome
  -- investment income split equally (contract)
  let incs := match incs with
    | [x] => [x + inv]
    | [x, y] => [x + half1 inv, y + half2 inv]
    | l => l
  let taxes := incs.map personTax
  let it0 := sumInts taxes
  let cc := (childCredit c.nChildren).value 0 (incs.foldl max 0)
  let it := applyCredits it0 [cc] []
  let so := soli.amount it
  let ss := sumInts (c.adults.map fun a => pension.amount a.earnings)
  Out.make c "ZZ" "ZZD" it (surtaxes := [("soli", so)]) (employeeSocial := ss)
    (detail := [Out.d "taxBeforeCredits" it0, Out.d "childCredit" cc])
    (unsupported := ["toy country: not a statute"])

def country : Country := { code := "ZZ", name := "Toy country", currency := "ZZD", compute := out }

end ZzTax
