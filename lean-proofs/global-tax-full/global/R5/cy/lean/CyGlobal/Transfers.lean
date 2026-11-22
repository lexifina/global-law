import TaxKernel.Global
import R5Common

/-!
# Cyprus 2025: stamp duty on contracts (4400)

Stamp Duty Law 19/1963 (cylaw consolidation, latest amendment 154(Ι)/2019; `law/cy_stamp.html.txt`), First Schedule:
"Αξία Σύμβασης €1 μέχρι €5.000 … μηδέν"; "€5.001 μέχρι €170.000, για κάθε ποσό €1.000 ή μέρος των €1.000 … €1,50";
"πέραν των 170.000, για κάθε ποσό €1.000 ή μέρος των €1.000 … €2 με μέγιστο ποσό χαρτοσήμου €20.000". Applied to
purchase contracts of any asset kind (read as bands: the part of the value in each band, by started thousand).
Land Registry transfer fees (Cap. 219) not read: not modelled.
-/

namespace CyGlobal
open TaxKernel TaxKernel.Global R5Common

def thousandsUp (x : Int) : Int := if x ≤ 0 then 0 else (x + 999) / 1000

def stampDuty (v : Int) : Int :=
  let b1 := thousandsUp (min v 170000 - 5000)
  let b2 := thousandsUp (v - 170000)
  min 20000 (divR .down (150 * b1 + 200 * b2) 100)

def transfers : Family :=
  { name := "4400 χαρτόσημο", covers := [.transactions],
    run := fun _ g _ => g.purchases.zipIdx.map fun (p, i) =>
      charge .transactions "Χαρτόσημο" p.price id stampDuty (event := s!"purchase {i + 1}")
        (statute := "Stamp Duty Law 19/1963 First Schedule (contracts: 0 to €5.000, €1,50 per €1.000 to €170.000, €2 above; max €20.000)") }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.purchases.any (·.kind.isRealEstate) then ["Land Registry transfer fees (Cap. 219) not modelled"] else []

#guard stampDuty 5000 == 0
#guard stampDuty 170000 == 247
#guard stampDuty 300000 == 507
#guard stampDuty 20000000 == 20000

end CyGlobal
