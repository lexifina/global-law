import InGlobal.Pit

/-!
# India 2025 (Maharashtra, Mumbai): stamp duty on conveyances (4400); Mumbai property tax not reached
(B.) Maharashtra Stamp Act (Bom. LX of 1958) Schedule I art. 25 (b): 5 % of the market value, plus 1 % metro cess in Mumbai
(Maharashtra Stamp (Amendment) Act 2021-22): 6 %. Registration fee (1 %, max Rs 30,000) is a fee. BMC property tax (capital
value system, MMC Act 1888 s. 154): C.
-/

namespace InGlobal.Property
open TaxKernel TaxKernel.Global

def duty0 : TransferDuty :=
  { name := "Stamp duty + metro cess (Mumbai 6 %)", sched := Schedule.flat 600, higherOfAssessed := true, kinds := [.home, .realEstate, .land] }

def fam0 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "Maharashtra Stamp Act Sch. I art. 25 (b); metro cess" (level := .state) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard duty0.amount { kind := .home, price := 10000000 } == 600000

end InGlobal.Property
