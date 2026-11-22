import ToGlobal.Pit

/-!
# Tonga 2025: company tax and non-resident withholding (1200)

Income Tax Act (Cap. 11.05, 2020 revised edition, `to/law/IncomeTaxAct_3.txt`): rates as read by the registry (B): companies
25 %; non-resident withholding 15 % (dividends, interest, royalties, services).
-/

namespace ToGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat 2500 }

def citStatute : String := "Income Tax Act (Cap. 11.05) Schedule"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 1500, statute := "Income Tax Act (Cap. 11.05) (non-resident withholding)" },
      { kind := .interest, rateBp := 1500, statute := "idem" },
      { kind := .royalty, rateBp := 1500, statute := "idem" },
      { kind := .services, rateBp := 1500, statute := "idem" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard cit.citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000 } == 150
#guard wht.amount { kind := .interest, amount := 1000 } == 150
#guard wht.amount { kind := .royalty, amount := 1000 } == 150
#guard wht.amount { kind := .services, amount := 1000 } == 150

end ToGlobal.Corporate
