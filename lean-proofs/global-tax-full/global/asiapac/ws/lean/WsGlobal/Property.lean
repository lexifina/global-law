import WsGlobal.Pit

/-!
# Samoa 2025: stamp duty on conveyances (4400)

Source: Stamp Duty Ordinance 1932 as consolidated by PacLII (Consolidated and Revised Statutes of Samoa 2007 with the
later amendments noted: Stamp Duty Amendment Act 2012, in force 2 April 2012, replaced item 10 of the Schedule;
Personal Property Securities Act 2016 items 1 and 11), RTF via the Internet Archive (capture 20250117150618 of
`paclii.org/ws/legis/consol_act/sdo1932204.rtf`; `ws/law/ws_sdo1932_paclii_wb20250117.rtf`).
* **s. 3**: the instruments in the Schedule are charged with the duties set opposite them, "due and payable by the persons
  described in the Schedule as being primarily liable".
* **Schedule item 10 (Conveyances)**: "For every conveyance on sale or voluntary conveyance with the following property
  values: (a) less than $50,000: 1% of the property value; (b) $50,000 to less than $100,000: $500 plus 2% of the excess above
  $50,000; (c) $100,000 to less than $200,000: $1,500 plus 3% of the excess above $100,000; (d) $200,000 or more: $4,500 plus
  4% of the excess above $200,000" (a marginal schedule). Exemptions: chattels, conveyances to the Government, security
  conveyances, trustee changes; gifts: gift duty deducted.
* The "person primarily liable" column is blank for item 10 in the consolidation (the 2012 replacement); the duty is booked
  on the purchaser, as for the other transfer items (16 (c), 19: "The transferee"): flagged.
-/

namespace WsGlobal.Property
open TaxKernel TaxKernel.Global

def duty0 : TransferDuty :=
  { name := "Stamp duty on conveyances (Schedule item 10)", sched := (Schedule.ofList [(0, 100), (50000, 200), (100000, 300), (200000, 400)]), kinds := [.home, .realEstate, .land] }

def fam0 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "Stamp Duty Ordinance 1932 s. 3, Schedule item 10 (replaced by the Stamp Duty Amendment Act 2012)" (level := .central) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty then ["conveyance duty booked on the purchaser: the item 10 'person primarily liable' column is blank in the consolidation; voluntary conveyances (gifts, with the gift-duty deduction) and share transfers (item 19, 50 c per $100) not modelled"] else [])

#guard duty0.amount { kind := .home, price := 250000 } == 6500
#guard duty0.amount { kind := .land, price := 40000 } == 400
#guard duty0.amount { kind := .home, price := 75000 } == 1000

end WsGlobal.Property
