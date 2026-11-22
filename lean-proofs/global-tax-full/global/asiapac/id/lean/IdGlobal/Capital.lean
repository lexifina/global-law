import IdGlobal.Pit

/-!
# Indonesia 2025: final taxes on interest, dividends, share and property sales (1100)
(B: the PPs were not read this session.) UU PPh Pasal 4 (2) final taxes: deposit interest 20 % (PP 131/2000); Pasal 17 (2c):
dividends to residents 10 % final (exempt if reinvested, Pasal 4 (3) f); PP 41/1994 jo. PP 14/1997: 0.1 % of the gross value
of listed-share sales (`saleF`, booked 1100: it is a final income tax); PP 34/2016: 2.5 % of the gross value of land and
building transfers (`propF`).
-/

namespace IdGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "PPh final bunga deposito (20 %)" i.amount pos (fun b => divR .down (2000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "UU PPh Pasal 4 (2) a; PP 131/2000"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "PPh final dividen (10 %)" i.amount pos (fun b => divR .down (1000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "UU PPh Pasal 17 (2c)")) }

def saleF : Family :=
  { name := "1100 PPh final penjualan saham di bursa (0.1 %)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.disposals.zipIdx.filter fun (d, _) => [.listedShares].contains d.kind).map fun (d, i) =>
        charge .pit "PPh final penjualan saham di bursa (0.1 %)" d.proceeds pos (fun b => divR .down (10 * b) BP) (event := s!"disposal {i + 1}") (statute := "PP 41/1994 jo. PP 14/1997") }
def propF : Family :=
  { name := "1100 PPh final pengalihan tanah dan bangunan (2.5 %)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.disposals.zipIdx.filter fun (d, _) => [.home, .realEstate, .land].contains d.kind).map fun (d, i) =>
        charge .pit "PPh final pengalihan tanah dan bangunan (2.5 %)" d.proceeds pos (fun b => divR .down (250 * b) BP) (event := s!"disposal {i + 1}") (statute := "PP 34/2016 Pasal 2") }

def families : List Family := [fam0, saleF, propF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.incomes.any (fun i => i.kind == .dividend) then ["dividend exemption on reinvestment (Pasal 4 (3) f) not modelled"] else [])
  ++ (if g.disposals.any (fun d => d.kind == .unlistedShares) then ["unlisted share gains (ordinary Pasal 17 rates) left to the 1.x line"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .interest, amount := 100000 }] } []).map (·.due) == [20000]
#guard (saleF.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 1000000, cost := 1 }] } []).map (·.due) == [1000]

end IdGlobal.Capital
