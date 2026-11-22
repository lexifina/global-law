import SgGlobal.Pit

/-!
# Singapore 2025: property tax on non-residential property and buyer's stamp duty (4100, 4400)
(B: IRAS tables.) Property Tax Act 1960 s. 9: non-residential property 10 % of annual value (`annualValue`); the progressive
owner-occupier and non-owner-occupier residential scales are not modelled (C). Stamp Duties Act 1929 First Schedule art. 3
(a): BSD residential 1 % first S$180,000, 2 % next 180,000, 3 % next 640,000, 4 % next 500,000, 5 % next 1.5 m, 6 % above
S$3 m; ABSD (art. 3 (bf)): citizens' second home 20 %, foreigners 60 % (`additionalHome`, `nonResident`).
-/

namespace SgGlobal.Property
open TaxKernel TaxKernel.Global

def prop0 : PropertyTax :=
  { name := "Property tax (non-residential 10 %)", sched := Schedule.flat 1000, onAnnualValue := true, ratioNum := 1, ratioDen := 1, exempt := 0, kinds := [.realEstate] }

def fam0 : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ => 
      prop0.charges g.assets "Property Tax Act 1960 s. 9 (1)" (level := .central) }

def bsd : TransferDuty :=
  { name := "Buyer's stamp duty + ABSD (residential)", sched := Schedule.ofList [(0, 100), (180000, 200), (360000, 300), (1000000, 400), (1500000, 500), (3000000, 600)],
    additionalBp := 2000, nonResidentBp := 6000, kinds := [.home] }
def bsdF : Family :=
  { name := "4400 buyer's stamp duty", covers := [.transactions],
    run := fun _ g _ => bsd.charges g.purchases "Stamp Duties Act 1929 First Schedule art. 3 (a), (bf)" }

def families : List Family := [fam0, bsdF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .home) then ["residential property tax scales (owner-occupier 0-32 %, others 12-36 %) not modelled"] else [])
  ++ (if g.purchases.any (fun p => p.kind != .home) then ["BSD on non-residential property and stamp duty on shares (0.2 %) not modelled"] else [])

#guard prop0.amount { kind := .realEstate, value := 0, annualValue := 100000 } == 10000
#guard bsd.amount { kind := .home, price := 1000000 } == 1800 + 3600 + 19200

end SgGlobal.Property
