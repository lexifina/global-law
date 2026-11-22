import MvGlobal.Pit

/-!
# Maldives 2025: income tax on companies and withholding on non-residents (1200)

Income Tax Act (Law 25/2019): the the build server copy is the consolidated text of 2026-08-31 (not the 2025 version) (B).
* Companies: first MVR 500,000 of taxable income 0 %, 15 % above (banks 25 %, not modelled).
* Withholding on non-residents' royalties, interest and fees: 10 %.
-/

namespace MvGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.ofList [(0, 0), (500000, 1500)] }

def citStatute : String := "Income Tax Act (Law 25/2019) (company rates)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 1000, statute := "ITA (Law 25/2019) consolidation 1 (mvlaw.gov.mv 1313, in force 2021-07-20 to 2026-08-30) s. 55 (a) (4): 10 %; s. 12 (a) exempts only dividends to residents" },
      { kind := .interest, rateBp := 1000, statute := "ITA (Law 25/2019) consolidation 1 (mvlaw.gov.mv 1313, in force 2021-07-20 to 2026-08-30) s. 55 (a) (3): 10 % (not on interest to a bank or NBFI accepted by MIRA)" },
      { kind := .royalty, rateBp := 1000, statute := "ITA (Law 25/2019) consolidation 1 (mvlaw.gov.mv 1313, in force 2021-07-20 to 2026-08-30) s. 55 (a) (2): 10 %" },
      { kind := .rent, rateBp := 1000, statute := "ITA (Law 25/2019) consolidation 1 (mvlaw.gov.mv 1313, in force 2021-07-20 to 2026-08-30) s. 55 (a) (1): 10 % on rent of immovable property in the Maldives" },
      { kind := .services, rateBp := 1000, statute := "ITA (Law 25/2019) consolidation 1 (mvlaw.gov.mv 1313, in force 2021-07-20 to 2026-08-30) s. 55 (a) (5): 10 % on technical service fees" }] }

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
  (if true then ["bank rate (25 %) not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 75000
#guard wht.amount { kind := .interest, amount := 1000 } == 100
#guard wht.amount { kind := .royalty, amount := 1000 } == 100
#guard wht.amount { kind := .services, amount := 1000 } == 100
#guard wht.amount { kind := .dividend, amount := 1000 } == 100
#guard wht.amount { kind := .rent, amount := 1000 } == 100

end MvGlobal.Corporate
