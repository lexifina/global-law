import InGlobal.Pit

/-!
# India 2025-26: income-tax on companies and on non-residents' dividends, interest and royalties (1200)

Income-tax Act 1961 and the Finance Act 2025 (Part I and the First Schedule): rates from the Act as read by the registry
(B; `cmp20/world/B02-g20/in/law/finance_bill_2025.txt` not re-read for this package).
* **s. 115BAA**: domestic companies opting out of exemptions: 22 %, surcharge 10 % of the tax, health and education cess
  4 % of tax + surcharge (25.168 %): `inTax`. Other domestic companies 30 % / 25 % (turnover ≤ Rs 400 crore) + surcharge
  7/12 % not modelled.
* **s. 115A (1) (a)**: foreign companies' dividends, interest and royalties / fees for technical services 20 % + cess 4 %
  (20.8 %; the 2 %/5 % surcharge above Rs 1/10 crore not modelled).
-/

namespace InGlobal.Corporate
open TaxKernel TaxKernel.Global

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 2080, statute := "ITA s. 115A (1) (a) (i), s. 195; cess 4 %" },
      { kind := .interest, rateBp := 2080, statute := "s. 115A (1) (a) (ii)" },
      { kind := .royalty, rateBp := 2080, statute := "s. 115A (1) (b)" },
      { kind := .services, rateBp := 2080, statute := "s. 115A (1) (b) (fees for technical services)" }] }

def cit : CorpRegime := { name := "Income-tax on domestic companies (s. 115BAA)", sched := Schedule.flat 2200 }
/-- s. 115BAA 22 %, surcharge 10 % of it, cess 4 % of tax + surcharge. -/
def inTax (x : Int) : Int := let t := divR .down (2200 * x) BP; let s := t / 10; t + s + (t + s) * 4 / 100
def citIn (co : Company) : Charge :=
  charge .cit "Income-tax (s. 115BAA) + surcharge + cess" (cit.beforeLosses co) (fun _ => cit.taxableProfit co) inTax (statute := "ITA 1961 s. 115BAA (2); Finance Act 2025 (surcharge 10 %, cess 4 %)")

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       wht.charges g.company
       ++ [citIn g.company] }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["companies not opting for s. 115BAA (30 %/25 % + 7/12 % surcharge), s. 115BAB, MAT (s. 115JB) not modelled"] else [])

#guard inTax 1000000 == 251680
#guard wht.amount { kind := .dividend, amount := 1000, toCompany := true } == 208
#guard wht.amount { kind := .interest, amount := 1000, toCompany := true } == 208
#guard wht.amount { kind := .royalty, amount := 1000, toCompany := true } == 208
#guard wht.amount { kind := .services, amount := 1000, toCompany := true } == 208
#guard wht.amount { kind := .dividend, amount := 10000, toCompany := false } == 2080

end InGlobal.Corporate
