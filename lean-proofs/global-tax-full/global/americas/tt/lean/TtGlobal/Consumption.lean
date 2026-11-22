import TtGlobal.Pit

/-!
# Trinidad and Tobago 2025: VAT (5111); excise and customs duties (5121) unsupported

Source: Value Added Tax Act, Chap. 75:06, Laws of Trinidad and Tobago (Ministry of the Attorney General and Legal
Affairs, `rgd.legalaffairs.gov.tt/laws2/Alphabetical_List/lawspdfs/75.06.pdf`, fetched 2026-11-21; amendment list up
to Act 17/2016 and LN 2016: later Finance Acts not checked: grade B).
* **s. 7 (1)**: "the rate of twelve and one-half per cent" (Act 1 of 2016).
* **Schedule 1** (exempt services): 1 medical, dental, hospital services; 2 bus and taxi services; 4 education; 6
  "Rental of residential property"; 10 financial services.
* **Schedule 2** (zero-rating): 1 (1) (a) "unprocessed food", rice, flour, milk, bread and the listed staples (the
  basket's food line read as these, flagged); 7 "Water and sewerage services supplied by a public authority"; 8 public
  bus services; 9, 10 prescription and listed over-the-counter medicines.
* Excise duties on alcohol, tobacco and petroleum (Customs Act, Excise (General Provisions) Act Chap. 78:50 and their
  Orders) were not read: unsupported.
-/

namespace TtGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon TtGlobal

def vat : Vat :=
  { name := "Value added tax", standard := 1250,
    classOf := fun gd => match gd with
      | .food | .water | .medicines => .zero
      | .health | .transport | .education | .rent | .financial | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act Chap. 75:06 s. 7 (1) (12.5 %), Sched. 1 items 1, 2, 4, 6, 10, Sched. 2 items 1, 7-10"

def vatF : Family := vatFamily "Value added tax" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) "excise duties (Customs Act; Excise (General Provisions) Act Chap. 78:50 and Orders) not read: not charged"
  ++ when (!g.consumption.isEmpty) "food read as the zero-rated staples of Sched. 2 item 1; other food is at 12.5 %"

#guard vat.embedded { good := .clothing, amount := 1125 } == 125
#guard vat.embedded { good := .food, amount := 1125 } == 0

end TtGlobal.Consumption
