import BbGlobal.Pit

/-!
# Barbados 2025: Value Added Tax (5111); excise grade C

Sources (bra.gov.bb legislation page, fetched 2026-11-21; `bb/law/`): VAT Act Cap. 87 (L.R.O. 1997, amendments noted to
2008), Amendment Acts 2010-14, 2011-10, 2015-2, 2015-33, 2017-18, 2017-29, 2018-12, 2018-50, 2019-9, 2019-28, 2023-6
(several scanned; OCR). No current consolidation: grade B.
* **s. 7 (2)** as substituted by Act 2011-10: "equal to 17.5 per cent of the value of the supply" (Cap. 87 had 15
  percent). Act 2023-6 inserts s. 7 (14)-(17): domestic electricity 7.5 % up to 250 kWh "deemed to have come into effect
  on the 1st day of August, 2022" and ceasing on 30 September 20[23]; above 250 kWh "17.5 per cent" (confirms the
  standard rate). Act 2015-33: "the tax imposed on the supply of the mobile services of voice, data and text messaging
  is 22 percent" from 1 Jan 2016.
* **First Schedule (zero rated)**: 5A "water or sewerage services by the Barbados Water Authority"; 8 drugs supplied on
  prescription under the Drug Service; 11 educational or scientific literature; 20 listed basic food items; 23 kerosene.
* **Second Schedule (exempt)**: 1 financial services (incl. "a contract of insurance"); 2 (4) dwelling houses and
  residential lets; 3 passenger transport by approved public-service vehicles; 7 medical services; 10 education.
* Hotel accommodation: a reduced rate set as a share of s. 7 (2) by Act 2011-10 and since amended (2018-12 Fourth
  Schedule): the 2025 figure was not confirmed: charged at 17.5 % (upper bound, flagged).
-/

namespace BbGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon BbGlobal

def vat : Vat :=
  { name := "Value Added Tax", standard := 1750,
    classOf := fun gd => match gd with
      | .food | .water | .medicines | .books => .zero
      | .financial | .insurance | .rent | .transport | .health | .education => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act Cap. 87 s. 7 (2) (17.5 %, Act 2011-10); First Sched. items 5A, 8, 11, 20, 23 (zero); Second Sched. items 1, 2 (4), 3, 7, 10 (exempt)"

def vatF : Family := vatFamily "Value Added Tax" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food: only the items listed in the First Schedule item 20 are zero rated; other food 17.5 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .medicines) "medicines: zero rated only when supplied on prescription under the Drug Service (First Sched. item 8)"
  ++ when (g.consumption.any fun s => s.good == .hotels) "hotel accommodation: the reduced hotel rate in force 2025 not confirmed; charged at 17.5 % (upper bound)"
  ++ when (g.consumption.any fun s => s.good == .communication) "mobile voice, data and text are taxed at 22 % (Act 2015-33); communication charged at 17.5 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) "excise tax (Excise Tax Act 2015-32) not modelled"

#guard vat.embedded { good := .clothing, amount := 1175 } == 175
#guard vat.embedded { good := .water, amount := 1175 } == 0
#guard vat.embedded { good := .rent, amount := 1175 } == 0

end BbGlobal.Consumption
