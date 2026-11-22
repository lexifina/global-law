import InGlobal.Pit

/-!
# India FY 2025-26: securities transaction tax and the capital gains tax on listed equity (4400, 1100)
(B: rates as amended by the Finance (No. 2) Act 2024, read by the registry.) Finance (No. 2) Act 2004 Chapter VII s. 98:
delivery-based sale of equity shares 0.1 % payable by the seller (and 0.1 % by the buyer). Income-tax Act 1961 s. 111A:
short-term gains on listed equity (STT paid) 20 %; s. 112A: long-term (held > 12 months) 12.5 % of gains above Rs 1.25 lakh
a year; health and education cess 4 % on top (Finance Act 2025). Surcharge on high incomes not modelled.
-/

namespace InGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "4400 securities transaction tax", covers := [.transactions],
    run := fun _ g _ => 
      ((g.disposals.zipIdx.filter fun (d, _) => [.listedShares].contains d.kind).map fun (d, k) =>
        charge .transactions "Securities transaction tax (seller, 0.1 %)" d.proceeds pos (fun b => divR .down (10 * b) BP) (event := s!"disposal {k + 1}") (statute := "Finance (No. 2) Act 2004 s. 98 (b)")) }

/-- s. 111A / 112A on the year's listed-equity gains, cess 4 %. -/
def eqTax (st lt : Int) : Int :=
  let t := divR .down (2000 * pos st) BP + divR .down (1250 * pos (lt - 125000)) BP
  t + t * 4 / 100
def cgF : Family :=
  { name := "1100 capital gains on listed equity (s. 111A, 112A)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      let ds := g.disposals.filter (·.kind == .listedShares)
      if ds.isEmpty then [] else
      let st := isum ((ds.filter fun d => d.heldMonths ≤ 12).map (·.gain))
      let lt := isum ((ds.filter fun d => d.heldMonths > 12).map (·.gain))
      [charge .pit "Tax on listed-equity gains (s. 111A 20 %, s. 112A 12.5 %, cess 4 %)" (st + lt) id (fun _ => eqTax st lt) (statute := "ITA 1961 ss. 111A, 112A (Finance (No. 2) Act 2024); Finance Act 2025 (cess)")] }

def families : List Family := [fam0, cgF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (fun d => d.kind != .listedShares) then ["gains on other assets (s. 112: 12.5 % without indexation after 24 months) left to the 1.x line"] else [])
  ++ (if g.incomes.any (fun i => i.kind == .dividend) then ["dividends are taxed at slab rates (1.x line); TDS s. 194 is a prepayment"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 1000000, cost := 1 }] } []).map (·.due) == [1000]
#guard eqTax 100000 225000 == 33800

end InGlobal.Capital
