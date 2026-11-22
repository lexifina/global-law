import MtGlobal.Pit

/-!
# MT 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Duty on Documents and Transfers Act Cap. 364 (5 %; first-time buyer reliefs)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (no recurrent property tax: absence not yet cited): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Duty on documents and transfers (sole residence) (pass 6)
Source: Cap. 364, legislation.mt consolidated PDF (amendments to Act XXX of 2025), fetched 2026-11-21 (`mt/law/cap364.pdf`).
* art. 32 (1): "a duty of five euro (5.00) for every one hundred euro (100) or part thereof of the amount or value of the consideration for the transfer of such thing or of the value of such thing, whichever is the higher"
* art. 32 (4) (a): for a person acquiring property "for the purpose of establishing therein or constructing thereon his sole, ordinary residence", duty "in respect of the first two hundred thousand euro (€200,000) ... shall be charged at the rate of three euro and fifty cents (€3.50) per one hundred euro (€100) or part thereof"


## 4400 Duty on documents and transfers (pass 6)
Source: Cap. 364, legislation.mt consolidated PDF (amendments to Act XXX of 2025), fetched 2026-11-21 (`mt/law/cap364.pdf`).
* art. 32 (1): "a duty of five euro (5.00) for every one hundred euro (100) or part thereof of the amount or value of the consideration for the transfer of such thing or of the value of such thing, whichever is the higher"
-/

namespace MtGlobal.Property
open TaxKernel TaxKernel.Global

/-- Duty on Documents and Transfers Act (Cap. 364) art. 32 (1) (EUR 5 per EUR 100 of the higher of price and value); art. 32 (4) (a) (EUR 3.50 per EUR 100 on the first EUR 200 000 for the buyer's sole ordinary residence) -/
def p6dodh : TransferDuty := { name := "Duty on documents and transfers (sole residence)", sched := Schedule.ofList [(0, 350), (200000, 500)], kinds := [.home] }

/-- Duty on Documents and Transfers Act (Cap. 364) art. 32 (1) (EUR 5 per EUR 100 of the higher of price and value); art. 32 (4) (a) (EUR 3.50 per EUR 100 on the first EUR 200 000 for the buyer's sole ordinary residence) -/
def p6dod : TransferDuty := { name := "Duty on documents and transfers", sched := Schedule.flat 500, kinds := [.realEstate, .land] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Duty on documents and transfers (sole residence)", covers := [.transactions],
     run := fun args g prev =>
       p6dodh.charges g.purchases "Duty on Documents and Transfers Act (Cap. 364) art. 32 (1) (EUR 5 per EUR 100 of the higher of price and value); art. 32 (4) (a) (EUR 3.50 per EUR 100 on the first EUR 200 000 for the buyer's sole ordinary residence)" },
   { name := "4400 Duty on documents and transfers", covers := [.transactions],
     run := fun args g prev =>
       p6dod.charges g.purchases "Duty on Documents and Transfers Act (Cap. 364) art. 32 (1) (EUR 5 per EUR 100 of the higher of price and value); art. 32 (4) (a) (EUR 3.50 per EUR 100 on the first EUR 200 000 for the buyer's sole ordinary residence)" }]

def absent : List Absent :=
  []

def notes : List String := ["MT 4400 Duty on documents and transfers (sole residence): legislation.mt, Cap. 364 as amended to Act XXX of 2025 (grade A)", "MT 4400 Duty on documents and transfers: legislation.mt, Cap. 364 as amended to Act XXX of 2025 (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if g.purchases.any (fun p => p.kind == .realEstate || p.kind == .land) then ["4400 base: the higher of price and value (the price stands in); duty on shares (art. 47-50) not modelled"] else [])

#guard p6dodh.amount { kind := .home, price := 200000 } == 7000
#guard p6dodh.amount { kind := .home, price := 2000000 } == 97000
#guard p6dodh.amount { kind := .vehicle, price := 100000 } == 0
#guard p6dod.amount { kind := .realEstate, price := 200000 } == 10000
#guard p6dod.amount { kind := .realEstate, price := 2000000 } == 100000
#guard p6dod.amount { kind := .vehicle, price := 100000 } == 0

end MtGlobal.Property
