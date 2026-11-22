import JpGlobal.Pit

/-!
# Japan 2025: separate taxation of interest, dividends and share gains (1100)
e-Gov asof 2025-07-01 (`jp/law/egov/sozeitokubetsu_…`, `chihozei_…`, `fukko_…`).
* 租特 art. 3 (1): domestic deposit interest "百分の十五の税率" separately; 復興財源確保法 art. 28: + 2.1 % of it (15.315 %);
  地方税法 art. 71-6 (1): 利子割 "百分の五".
* 租特 art. 8-4 (listed dividends, 15 %) and arts. 37-10 / 37-11 (gains on shares, 15 %) + 復興 2.1 %; inhabitants tax 5 %
  (地方税法 附則 33-2, 35-2: not re-read, same 5 %).
Applies to `incomes` items (the 1.x line keeps the household aggregates).
-/

namespace JpGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "所得税 + 復興特別所得税 (利子, 15.315 %)" i.amount pos (fun b => divR .down (15315 * b) 100000) (event := s!"income {k + 1}") (level := .central) (statute := "租特 art. 3 (1); 復興財源確保法 art. 28"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "住民税 利子割 (5 %)" i.amount pos (fun b => divR .down (500 * b) BP) (event := s!"income {k + 1}") (level := .local) (statute := "地方税法 art. 71-6 (1)"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "所得税 + 復興特別所得税 (上場株式等の配当, 15.315 %)" i.amount pos (fun b => divR .down (15315 * b) 100000) (event := s!"income {k + 1}") (level := .central) (statute := "租特 art. 8-4; 復興 art. 28"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "住民税 配当割 (5 %)" i.amount pos (fun b => divR .down (500 * b) BP) (event := s!"income {k + 1}") (level := .local) (statute := "地方税法 art. 71-28 (5 %)")) }

def fam1 : Family :=
  { name := "1100 capital gains", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.disposals.zipIdx.filter fun (d, _) => [.listedShares, .unlistedShares].contains d.kind).map fun (d, k) =>
        charge .pit "所得税 + 復興特別所得税 (株式等の譲渡, 15.315 %)" d.gain pos (fun b => divR .down (15315 * b) 100000) (event := s!"disposal {k + 1}") (level := .central) (statute := "租特 arts. 37-10, 37-11; 復興 art. 28"))
      ++ ((g.disposals.zipIdx.filter fun (d, _) => [.listedShares, .unlistedShares].contains d.kind).map fun (d, k) =>
        charge .pit "住民税 (株式等の譲渡, 5 %)" d.gain pos (fun b => divR .down (500 * b) BP) (event := s!"disposal {k + 1}") (level := .local) (statute := "地方税法 附則 35-2")) }

def families : List Family := [fam0, fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (fun d => d.kind.isRealEstate) then ["land and building gains (租特 31-32: 15 %/30 % + 5 %/9 %) not modelled"] else [])
  ++ (if g.incomes.any (fun i => i.kind == .dividend) then ["dividends treated as listed (source taxation); aggregate taxation with the dividend credit not modelled"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .interest, amount := 100000 }] } []).map (·.due) == [15315, 5000]
#guard (fam1.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 2000000, cost := 1000000 }] } []).map (·.due) == [153150, 50000]

end JpGlobal.Capital
