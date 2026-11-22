import IeGlobal.Pit

/-!
# IE 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Stamp Duties Consolidation Act 1999 Sch. 1 (1 % / 2 % / 6 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Finance (Local Property Tax) Act 2012): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Stamp duty on conveyances (residential property) (pass 6)
Source: Revenue, Notes for Guidance, Stamp Duties Consolidation Act 1999 (2025 edition), Schedules & Appendices, head of charge "CONVEYANCE or TRANSFER on sale" (`ie/law/sdca_nfg2025_schedules.txt`; the revised Act is not on revisedacts.lawreform.ie).
* residential property: 1 % where the consideration does not exceed EUR 1 million, 2 % on the excess up to EUR 1,5 million, 6 % on the excess above EUR 1,5 million
* 3 or more units in an apartment block: 1 % to EUR 1 million, 2 % on the balance; relevant residential units of s. 31E (10 or more houses in 12 months): 15 %
* non-residential property: 7,5 %
* grade B: Revenue's official guide; the Act's Schedule 1 text itself is not on disk


## 4400 Stamp duty on conveyances (non-residential property) (pass 6)
Source: Revenue, Notes for Guidance, Stamp Duties Consolidation Act 1999 (2025 edition), Schedules & Appendices, head of charge "CONVEYANCE or TRANSFER on sale" (`ie/law/sdca_nfg2025_schedules.txt`; the revised Act is not on revisedacts.lawreform.ie).
* land is taken as non-residential property (7,5 %)
-/

namespace IeGlobal.Property
open TaxKernel TaxKernel.Global

/-- SDCA 1999 Sch. 1, CONVEYANCE or TRANSFER on sale: residential property 1 % to EUR 1 000 000, 2 % to EUR 1 500 000, 6 % above -/
def p6ieSdRes : TransferDuty := { name := "Stamp duty on conveyances (residential property)", sched := Schedule.ofList [(0, 100), (1000000, 200), (1500000, 600)], kinds := [.home, .realEstate] }

/-- SDCA 1999 Sch. 1, CONVEYANCE or TRANSFER on sale: non-residential property 7,5 % -/
def p6ieSdNonRes : TransferDuty := { name := "Stamp duty on conveyances (non-residential property)", sched := Schedule.flat 750, kinds := [.land] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Stamp duty on conveyances (residential property)", covers := [.transactions],
     run := fun args g prev =>
       p6ieSdRes.charges g.purchases "SDCA 1999 Sch. 1, CONVEYANCE or TRANSFER on sale: residential property 1 % to EUR 1 000 000, 2 % to EUR 1 500 000, 6 % above" },
   { name := "4400 Stamp duty on conveyances (non-residential property)", covers := [.transactions],
     run := fun args g prev =>
       p6ieSdNonRes.charges g.purchases "SDCA 1999 Sch. 1, CONVEYANCE or TRANSFER on sale: non-residential property 7,5 %" }]

def absent : List Absent :=
  []

def notes : List String := ["IE 4400 Stamp duty on conveyances (residential property): Notes for Guidance 2025 (rates for instruments executed from 2 October 2024, Finance Act 2024 s. 90) (grade B)", "IE 4400 Stamp duty on conveyances (non-residential property): Notes for Guidance 2025 (rates for instruments executed from 2 October 2024, Finance Act 2024 s. 90) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if g.purchases.any (fun p => p.kind == .realEstate) then ["4400 stamp duty: other real estate is taken as residential property (1 / 2 / 6 %); commercial property bears 7,5 %"] else [])
  ++ (if g.purchases.any (fun p => p.kind == .land) then ["4400 stamp duty: land is taken as non-residential (7,5 %); residential land follows the residential rates"] else [])
  ++ (if g.purchases.any (fun p => p.kind == .home || p.kind == .realEstate) then ["4400 stamp duty: the apartment-block rates, the s. 31E 15 % rate, consanguinity relief and the aggregation of linked transactions are not applied"] else [])

#guard p6ieSdRes.amount { kind := .home, price := 200000 } == 2000
#guard p6ieSdRes.amount { kind := .home, price := 2000000 } == 50000
#guard p6ieSdRes.amount { kind := .vehicle, price := 100000 } == 0
#guard p6ieSdNonRes.amount { kind := .land, price := 200000 } == 15000
#guard p6ieSdNonRes.amount { kind := .land, price := 2000000 } == 150000
#guard p6ieSdNonRes.amount { kind := .vehicle, price := 100000 } == 0

end IeGlobal.Property
