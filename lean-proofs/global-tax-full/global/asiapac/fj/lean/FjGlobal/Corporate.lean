import FjGlobal.Pit

/-!
# Fiji 2025: company income tax (1200)

Income Tax Act 2015 and the Income Tax (Budget Amendment) Acts (the build server `fj/law/act*_ita_budget.txt`): rate as read by the
registry (B): resident companies 25 % (listed 20 %, flag `listed`). NRWT: not reached in this pass (C).
-/

namespace FjGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- The rate by the company's flags (sector), else the general rate. -/
def rateOf (co : Company) : Int := if co.flags.contains "listed" then 2000 else 2500

def cit (co : Company) : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "Income Tax Act 2015 Schedule (as amended by the 2023 budget)"

def wht : Wht :=
  { name := "Non-resident withholding tax (ITA 2015)", rules := [
      { kind := .dividend, rateBp := 0, statute := "Income Tax (Exempt Income) Regulations 2016 Sch. Part 5 (1): any dividend received is exempt income (Rates Regs 2016 reg 10 (5) (c) repealed)" },
      { kind := .interest, rateBp := 1000, statute := "Income Tax (Rates of Tax and Levies) Regulations 2016 reg 10 (5) (b) (10 %)" },
      { kind := .royalty, rateBp := 1500, statute := "Income Tax (Rates of Tax and Levies) Regulations 2016 reg 10 (5) (a) (15 %)" },
      { kind := .services, rateBp := 1500, statute := "Income Tax (Rates of Tax and Levies) Regulations 2016 reg 10 (5) (a): management fee, fee for professional or other independent services (15 %)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [(cit g.company).citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (cit { profit := 1000000 }).citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .interest, amount := 1000 } == 100
#guard wht.amount { kind := .royalty, amount := 1000 } == 150
#guard wht.amount { kind := .dividend, amount := 1000 } == 0

end FjGlobal.Corporate
