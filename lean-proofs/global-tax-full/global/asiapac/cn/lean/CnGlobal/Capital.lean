import CnGlobal.Pit

/-!
# China 2025: individual income tax on investment income and gains, stamp duty on share sales (1100, 4400)
* 个人所得税法 (2018-08-31) art. 3 (3) (`cmp20/world/B02-g20/cn/law/iit_law_2018.txt`): "利息、股息、红利所得，财产租赁所得，
  财产转让所得和偶然所得，适用比例税率，税率为百分之二十". Deposit interest is exempt from 2008-10-09 (财税〔2008〕132号, B) and
  gains on listed A-shares are not taxed (财税字〔1998〕61号, B): modelled 20 % on dividends (not listed) and on gains from
  unlisted shares and real estate.
* 印花税法 (2021) 税目税率表 证券交易 千分之一 (seller), halved to 0.05 % from 2023-08-28 (财政部 税务总局公告2023年第39号, B).
-/

namespace CnGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "个人所得税 (股息 20 %)" i.amount pos (fun b => divR .down (2000 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "个人所得税法 art. 3 (3)")) }

def fam1 : Family :=
  { name := "1100 capital gains", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.disposals.zipIdx.filter fun (d, _) => [.unlistedShares, .realEstate, .land].contains d.kind).map fun (d, k) =>
        charge .pit "个人所得税 (财产转让所得 20 %)" d.gain pos (fun b => divR .down (2000 * b) BP) (event := s!"disposal {k + 1}") (level := .central) (statute := "个人所得税法 art. 2 (8), art. 3 (3)")) }

def fam2 : Family :=
  { name := "4400 securities transaction tax", covers := [.transactions],
    run := fun _ g _ => 
      ((g.disposals.zipIdx.filter fun (d, _) => [.listedShares].contains d.kind).map fun (d, k) =>
        charge .transactions "印花税 (证券交易, seller 0.05 %)" d.proceeds pos (fun b => divR .down (5 * b) BP) (event := s!"disposal {k + 1}") (statute := "印花税法 (2021) 税目税率表; 公告2023年第39号")) }

def families : List Family := [fam0, fam1, fam2]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.incomes.any (fun i => i.kind == .dividend) then ["listed-company dividends (财税〔2015〕101号: exempt after 1 year, 10 % 1 month-1 year) taken as 20 %"] else [])
  ++ (if g.disposals.any (fun d => d.kind == .home) then ["sale of a home: 20 % of the gain unless the sole home held 5 years (circulars), not modelled"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .dividend, amount := 10000 }] } []).map (·.due) == [2000]
#guard (fam2.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 100000, cost := 90000 }] } []).map (·.due) == [50]

end CnGlobal.Capital
