import WsGlobal.Pit

/-!
# Samoa 2025: company tax and non-resident withholding (1200)

Source: Income Tax Act 2012 (`cmp20/world/B14-pacific/ws/law/Income_Tax_Act_2012.txt`), Schedule 1.
* **cl. (2)**: "The rate of income tax applicable to a company is 27%."
* **cl. (4) (b)**: non-resident withholding tax on "interest, a royalty, … management fee, fee for personal (including
  professional) services, or natural resource amount, 15%".
-/

namespace WsGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat 2700 }

def citStatute : String := "Income Tax Act 2012 Sch. 1 cl. (2)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .interest, rateBp := 1500, statute := "ITA 2012 Sch. 1 cl. (4) (b)" },
      { kind := .royalty, rateBp := 1500, statute := "Sch. 1 cl. (4) (b)" },
      { kind := .services, rateBp := 1500, statute := "Sch. 1 cl. (4) (b)" },
      { kind := .dividend, rateBp := 0, statute := "ITA 2012 s. 10 (2): non-resident withholding tax on interest, royalties, insurance premiums, management fees, personal services fees and natural resource amounts only; Sch. 2 Part A (1) (b): a dividend paid by a resident company is exempt income" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard cit.citTax { profit := 1000000 } == 270000
#guard wht.amount { kind := .interest, amount := 1000 } == 150
#guard wht.amount { kind := .royalty, amount := 1000 } == 150
#guard wht.amount { kind := .services, amount := 1000 } == 150
#guard wht.amount { kind := .dividend, amount := 1000 } == 0

end WsGlobal.Corporate
