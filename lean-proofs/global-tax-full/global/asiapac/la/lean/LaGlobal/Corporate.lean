import LaGlobal.Pit

/-!
# Lao PDR 2025: profit tax (1200)

Law on Income Tax No. 67/NA (2019): not on the build server (the 1.x `rescue` folder only); rate from the registry reading (B).
* Profit tax 20 % (lump-sum regime for small businesses not modelled). Withholding on non-residents: not reached (C).
-/

namespace LaGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Profit tax",
    sched := Schedule.flat 2000 }

def citStatute : String := "Law on Income Tax No. 67/NA (2019)"

def wht : Wht :=
  { name := "Income tax withheld from non-residents (Law on Income Tax 2019)", rules := [
      { kind := .dividend, rateBp := 1000, statute := "Law on Income Tax No. 67/NA (2019) art. 46 (4), art. 49 (2) (10 % of the gross), art. 50 (the payer deducts)" },
      { kind := .interest, rateBp := 1000, statute := "Law on Income Tax No. 67/NA (2019) art. 46 (4), art. 49 (2) (10 % of the gross), art. 50" },
      { kind := .royalty, rateBp := 500, statute := "Law on Income Tax No. 67/NA (2019) art. 46 (5), art. 49 (3) (5 % of the gross: copyrights, patents, trade marks), art. 50" },
      { kind := .services, toCompany := some true, rateBp := 300, statute := "Law on Income Tax No. 67/NA (2019) art. 12 (2) (non-residents without an enterprise in Laos), art. 13 (2), art. 14 (2) (deemed profit 15 % of revenue for commerce and services), art. 15 (20 %), art. 20 (the purchaser declares): 3 % of the gross" },
      { kind := .services, toCompany := some false, rateBp := 1000, statute := "Law on Income Tax No. 67/NA (2019) art. 46 (2) (remuneration of board members, artists, athletes and others), art. 49 (2) (10 %), art. 50" }] }

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
  (if true then ["lump-sum small-business regime and mining rates not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 200000
#guard wht.amount { kind := .services, amount := 1000 } == 30
#guard wht.amount { kind := .royalty, amount := 1000, toCompany := false } == 50

end LaGlobal.Corporate
