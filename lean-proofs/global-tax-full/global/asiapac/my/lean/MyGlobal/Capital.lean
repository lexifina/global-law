import MyGlobal.Pit

/-!
# Malaysia YA 2025: dividend tax, RPGT, stamp duty on share contracts (1100, 4400)
(B: Act 53, Act 169 and Act 378 texts not machine-reachable.) Finance Act 2024: 2 % on an individual's dividends above
RM 100,000 a year (`divTax`). Real Property Gains Tax Act 1976 Sch. 5 Part I (citizens): disposal within 3 years 30 %, in
the 4th year 20 %, 5th 15 %, from the 6th 0 % (`rpgtRate`). Stamp Act 1949 First Schedule item 31: contract notes for listed
shares 0.1 %, capped at RM 1,000 a contract. Bank interest of individuals exempt (Sch. 6 para. 35).
-/

namespace MyGlobal.Capital
open TaxKernel TaxKernel.Global

def divTax (d : Int) : Int := divR .down (200 * pos (d - 100000)) BP
def rpgtRate (m : Nat) : Int := if m ≤ 36 then 3000 else if m ≤ 48 then 2000 else if m ≤ 60 then 1500 else 0
def capF : Family :=
  { name := "1100 dividend tax and RPGT", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      (let d := isum ((g.incomes.filter fun i => i.kind == .dividend && !i.foreign).map (·.amount))
       if d ≤ 100000 then [] else [charge .pit "Dividend tax (2 % above RM 100,000)" d id divTax (statute := "ITA 1967 s. 4 (c), Sch. 1 (Finance Act 2024)")])
      ++ ((g.disposals.zipIdx.filter fun (d, _) => d.kind.isRealEstate).map fun (d, i) =>
        charge .pit "Real property gains tax" d.gain pos (fun b => divR .down (rpgtRate d.heldMonths * b) BP) (event := s!"disposal {i + 1}") (statute := "RPGT Act 1976 Sch. 5 Part I")) }
def sttF : Family :=
  { name := "4400 stamp duty on share contract notes", covers := [.transactions],
    run := fun _ g _ => (g.disposals.zipIdx.filter fun (d, _) => d.kind == .listedShares).map fun (d, i) =>
      charge .transactions "Stamp duty on contract notes (0.1 %, max RM 1,000)" d.proceeds pos (fun b => min (divR .down (10 * b) BP) 1000) (event := s!"disposal {i + 1}") (statute := "Stamp Act 1949 First Schedule item 31") }

def families : List Family := [capF, sttF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard divTax 150000 == 1000
#guard rpgtRate 40 == 2000
#guard (sttF.run [] { id := "t", household := { id := "t" }, disposals := [{ kind := .listedShares, proceeds := 2000000, cost := 1 }] } []).map (·.due) == [1000]

end MyGlobal.Capital
