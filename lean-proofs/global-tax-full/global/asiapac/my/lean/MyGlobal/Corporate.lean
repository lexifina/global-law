import MyGlobal.Pit

/-!
# Malaysia YA 2025: income tax on companies and withholding (1200)

Income Tax Act 1967 (Act 53): lom.agc.gov.my did not serve the reprint to the build server; rates from LHDN tables (B).
* **Sch. 1 Part I para. 2**: 24 %; **para. 2A** (SME: paid-up ≤ RM 2.5 m, gross income ≤ RM 50 m; flag `sme`): 15 % on
  the first RM 150,000, 17 % on the next RM 450,000, 24 % above.
* **s. 109**: interest 15 %, royalties 10 %; **s. 109B**: services 10 % to non-residents; dividends single-tier, not taxed.
-/

namespace MyGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat 2400 }

def citStatute : String := "ITA 1967 Sch. 1 Part I para. 2, 2A"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .interest, rateBp := 1500, statute := "ITA s. 109" },
      { kind := .royalty, rateBp := 1000, statute := "ITA s. 109" },
      { kind := .services, rateBp := 1000, statute := "ITA s. 109B" },
      { kind := .dividend, rateBp := 0, statute := "ITA 1967 s. 108: a company paying or crediting a dividend shall not deduct tax from it; Sch. 6 para. 12B: such dividends exempt (reprint as at 1 Nov 2023)" }] }

def citSme : CorpRegime := { name := "Income tax on companies (SME)", sched := Schedule.ofList [(0, 1500), (150000, 1700), (600000, 2400)] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["SME rates (para. 2A) only through `citSme` (flag not routed), petroleum income tax (38 %) and the global minimum tax not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 240000
#guard citSme.citTax { profit := 1000000 } == 22500 + 76500 + 96000
#guard wht.amount { kind := .interest, amount := 1000 } == 150
#guard wht.amount { kind := .royalty, amount := 1000 } == 100
#guard wht.amount { kind := .services, amount := 1000 } == 100
#guard wht.amount { kind := .dividend, amount := 1000 } == 0

end MyGlobal.Corporate
