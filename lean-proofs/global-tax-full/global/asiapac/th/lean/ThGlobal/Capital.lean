import ThGlobal.Pit

/-!
# Thailand 2025: final withholding on interest and dividends, specific business tax on share sales (1100, 4400)
(B: Revenue Code text not read this session.) s. 50 (2): interest 15 % final, dividends 10 % final (election; aggregation
with the s. 47 bis credit is the 1.x line's); listed-share gains exempt (MR 126 cl. 2 (23)). Royal Decree No. 764 (B.E.
2565): specific business tax on SET share sales 0.1 % + local 10 % of it = 0.11 % (from 2024).
-/

namespace ThGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "Withholding on interest (15 % final)" i.amount pos (fun b => divR .down (1500 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "Revenue Code s. 50 (2)"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "Withholding on dividends (10 % final)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "Revenue Code s. 50 (2) (e)")) }

def fam1 : Family :=
  { name := "4400 securities transaction tax", covers := [.transactions],
    run := fun _ g _ => 
      ((g.disposals.zipIdx.filter fun (d, _) => [.listedShares].contains d.kind).map fun (d, k) =>
        charge .transactions "Specific business tax on share sales (0.11 %)" d.proceeds pos (fun b => divR .down (11 * b) BP) (event := s!"disposal {k + 1}") (statute := "Revenue Code s. 91/2; Royal Decree No. 764")) }

def families : List Family := [fam0, fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .interest, amount := 100000 }] } []).map (·.due) == [15000]
#guard (fam1.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 1000000, cost := 1 }] } []).map (·.due) == [1100]

end ThGlobal.Capital
