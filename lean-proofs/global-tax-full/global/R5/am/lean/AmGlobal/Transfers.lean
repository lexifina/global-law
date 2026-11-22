import TaxKernel.Global
import R5Common

/-!
# Armenia 2025: state duty on the registration of a transfer of immovable property (4400)

Law HO-186 "On State Duty" of 27/12/1997, official English translation on arlis.am (`arlis.am/en/acts/209221`, with
changes to HO-393-N of 08/12/2023, notes on HO-181-N of 2024 and HO-339-N of 2024 (from 01/01/2026); extract
`law/am_state_duty_en_arlis209221.txt`):
* art. 3: the payers are the natural and legal persons making use of the services or actions of art. 7;
* art. 8: the base duty is **AMD 1 000**;
* art. 16(36)(2): state registration of the right based on alienation (purchase and sale, gift, exchange, transfer) of
  an item of immovable property: (a) undeveloped land parcels **20-fold**, (b) constructions of social or industrial
  significance above 200 m² 40-fold, (c) agricultural land parcels the base duty, (d) other immovable property
  **20-fold** of the base duty;
* art. 11(1)(b): notarial certification of a contract alienating immovable property 5-fold (only where the contract is
  certified; not an input: listed, not booked).
Model: a real-estate purchase is charged AMD 20 000 for the registration of the buyer's right (the buyer applies for the
registration of his right: art. 3). Fixed amount, independent of the price. **Grade A** (statute text read; amendments
after 08/12/2023 to art. 16 not in the translation).
-/

namespace AmGlobal
open TaxKernel TaxKernel.Global R5Common

def baseDuty : Int := 1000
def regDuty : Int := 20 * baseDuty

def transfers : Family :=
  { name := "4400 Պետական տուրք (անշարժ գույքի իրավունքի գրանցում)", covers := [.transactions],
    run := fun _ g _ =>
      (g.purchases.zipIdx.filter fun (p, _) => p.kind.isRealEstate).map fun (p, i) =>
        charge .transactions "state duty: registration of the right based on alienation" p.price pos (fun _ => regDuty)
          (event := s!"purchase {i + 1}") (statute := "Law HO-186 on State Duty art. 16(36)(2)(a), (d) (20-fold of the base duty, art. 8: AMD 1 000), art. 3") }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.purchases.any (fun p => p.kind.isRealEstate) then
    ["state duty: agricultural land (1-fold) and social or industrial constructions above 200 m² (40-fold) not distinguished; notarial certification of the contract (art. 11(1)(b), 5-fold) not booked (whether the contract is certified is not an input)"] else []

#guard regDuty == 20000

end AmGlobal
