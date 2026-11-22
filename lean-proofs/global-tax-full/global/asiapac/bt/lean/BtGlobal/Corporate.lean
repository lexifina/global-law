import BtGlobal.Pit

/-!
# Bhutan 2025: corporate income tax (1200)

Income Tax Act 2001 (fourth edition, `cmp20/world/B11-south-asia/bt/law/…2001_Fourth-Edition.txt`); the Income Tax Act
2025 comes into force on the 13th day of the 11th month of the Wood Female Snake year (January 2026), so 2025 is under
the 2001 Act. Part I: corporate income tax 30 % (B: rate clause not re-located). TDS on non-residents: not reached (C).
-/

namespace BtGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Corporate income tax",
    sched := Schedule.flat 3000 }

def citStatute : String := "ITA 2001 Part I (corporate income tax)"

def wht : Wht :=
  { name := "Tax deducted at source from persons under limited tax liability (ITA 2001)", rules := [
      { kind := .dividend, rateBp := 1000, statute := "ITA 2001 Part I s. 45.2 (d) (companies under limited tax liability), Part IV s. 13.2 (10 %, final)" },
      { kind := .interest, rateBp := 500, statute := "ITA 2001 Part I s. 45.2 (c), Part IV s. 14.2 (5 %, final)" },
      { kind := .royalty, rateBp := 500, statute := "ITA 2001 Part I s. 45.2 (c), Part IV s. 15.2 (5 %, final)" },
      { kind := .services, rateBp := 300, statute := "ITA 2001 Part I s. 45.2 (b): contractors and consultants 3 % of the contract value; Part IV s. 18.2 (3 %, final)" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard cit.citTax { profit := 1000000 } == 300000
#guard wht.amount { kind := .dividend, amount := 1000 } == 100
#guard wht.amount { kind := .services, amount := 1000 } == 30

end BtGlobal.Corporate
