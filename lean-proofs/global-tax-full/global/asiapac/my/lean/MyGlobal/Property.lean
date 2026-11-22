import MyGlobal.Pit

/-!
# Malaysia 2025 (Kuala Lumpur): stamp duty on property transfers (4400); quit rent and assessment rates not reached
(B.) Stamp Act 1949 First Schedule item 32 (a): 1 % on the first RM 100,000, 2 % on the next RM 400,000, 3 % on the next
RM 500,000, 4 % above RM 1 m; foreign buyers 4 % flat (from 2024). DBKL assessment rates (Local Government Act 1976 s. 127)
and quit rent (National Land Code): C.
-/

namespace MyGlobal.Property
open TaxKernel TaxKernel.Global

def duty0 : TransferDuty :=
  { name := "Stamp duty on transfers (item 32 (a))", sched := (Schedule.ofList [(0, 100), (100000, 200), (500000, 300), (1000000, 400)]), kinds := [.home, .realEstate, .land] }

def fam0 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "Stamp Act 1949 First Schedule item 32 (a)" (level := .central) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.purchases.any (fun p => p.nonResident) then ["foreign buyers' 4 % flat rate not modelled"] else [])

#guard duty0.amount { kind := .home, price := 600000 } == 1000 + 8000 + 3000

end MyGlobal.Property
