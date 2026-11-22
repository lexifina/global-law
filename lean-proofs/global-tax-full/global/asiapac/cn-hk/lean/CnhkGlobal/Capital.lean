import CnhkGlobal.Pit

/-!
# Hong Kong 2025/26: property tax on rents and stamp duty on stock (1100, 4400)
(B: Cap. 112 and Cap. 117 texts not fetched; IRD/SDO tables.) IRO Part II s. 5: property tax 15 % of the net assessable value
(rent less a 20 % statutory allowance: 12 % of the rent). No tax on dividends, interest or capital gains of individuals.
Stamp Duty Ordinance Sch. 1 head 2 (1): 0.1 % on each side of a stock transfer (from 2023-11-17): the seller's half.
-/

namespace CnhkGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .rent && !i.foreign).map fun (i, k) =>
        charge .pit "Property tax (15 % of 80 % of rent)" i.amount pos (fun b => divR .down (1200 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "IRO Cap. 112 s. 5 (1), s. 5B (20 % allowance)")) }

def fam1 : Family :=
  { name := "4400 securities transaction tax", covers := [.transactions],
    run := fun _ g _ => 
      ((g.disposals.zipIdx.filter fun (d, _) => [.listedShares, .unlistedShares].contains d.kind).map fun (d, k) =>
        charge .transactions "Stamp duty on stock transfers (seller 0.1 %)" d.proceeds pos (fun b => divR .down (10 * b) BP) (event := s!"disposal {k + 1}") (statute := "Stamp Duty Ordinance Cap. 117 Sch. 1 head 2 (1)")) }

def families : List Family := [fam0, fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .rent, amount := 100000 }] } []).map (·.due) == [12000]
#guard (fam1.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 100000, cost := 1 }] } []).map (·.due) == [100]

end CnhkGlobal.Capital
