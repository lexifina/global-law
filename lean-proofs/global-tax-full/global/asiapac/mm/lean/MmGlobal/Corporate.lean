import MmGlobal.Pit

/-!
# Myanmar 2025-26: income tax on companies (1200)

Union Tax Law 2025 and the Income Tax Law 1974: not on the build server (B from the IRD tables).
* Companies 22 %. Withholding on non-residents (MOPF notification): not reached (C).
-/

namespace MmGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Income tax on companies",
    sched := Schedule.flat 2200 }

def citStatute : String := "Income Tax Law 1974 s. 14; Union Tax Law 2025"

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute] }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard cit.citTax { profit := 1000000 } == 220000

end MmGlobal.Corporate
