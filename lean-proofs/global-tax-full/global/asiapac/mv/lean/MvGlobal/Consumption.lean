import MvGlobal.Pit
import TaxKernel.Global2

/-!
# Maldives 2025: goods and services tax (5111); import duties not modelled

Source: Goods and Services Tax Act (Law 10/2011), official Dhivehi consolidation on mvlaw.gov.mv, consolidation 1258
("with the seventh amendment", in force 4 November 2024; the next, 1323, from 31 August 2026), read 2026-11-21
(`mv/law/mv_gst_10-2011_c1258.json`; Schedule 1 is the embedded PDF `mv/law/mv_gst_sch1_2018.pdf`).
* **s. 16 (c)**: GST on goods and services outside the tourism sector at 8 % from 1 January 2023.
* **s. 15 (a)-(b)**: goods and services of licensed resorts, hotels, guesthouses, picnic and private islands, tourist
  vessels, their shops and diving schools, travel agents and domestic air carriers (to non-Maldivians): 16 % from
  1 January 2023 to 30 June 2025 (b) (5), 17 % from 1 July 2025 (b) (6). Modelled as the `hotels` class (DatedVat, two
  periods); other basket classes are not tourism-sector supplies.
* **s. 20** exempt: (a) electricity, (b) water, (c) post, (d) sewerage, (e) education, (f) health services of providers
  registered with the State, (h) medicines sold by registered pharmacies, (j) financial services prescribed by
  regulation, (k) rent of immovable property, (l) international transport, (o) price-controlled housing, (p) day care.
* **s. 22 (a)** zero rate for the basic goods of **Schedule 1** (22 items: rice, sugar, flour, milk, eggs, tea, potatoes,
  onions, fresh fruit and vegetables and others): the basket's food class is mixed and is modelled at 8 % (flagged).
* **s. 51 (a) (1)-(2)**: registration when supplies in the past or next 12 months exceed MVR 1,000,000 (threshold).
-/

namespace MvGlobal.Consumption
open TaxKernel TaxKernel.Global

def vatH1 : Vat :=
  { name := "Goods and services tax (to 30 June 2025)", standard := 800, reduced := 1600, threshold := 1000000,
    classOf := fun gd => match gd with
      | .hotels => .reduced
      | .electricity | .water | .education | .health | .medicines | .financial | .rent => .exempt
      | _ => .standard }

def vat : Vat :=
  { name := "Goods and services tax", standard := 800, reduced := 1700, threshold := 1000000,
    classOf := fun gd => match gd with
      | .hotels => .reduced
      | .electricity | .water | .education | .health | .medicines | .financial | .rent => .exempt
      | _ => .standard }

def vatStatuteH1 : String := "GST Act (Law 10/2011) s. 15 (b) (5) (tourism 16 % to 30 June 2025), s. 16 (c) (8 %), s. 20, s. 22, s. 51; consolidation 1258"
def vatStatute : String := "GST Act (Law 10/2011) s. 15 (b) (6) (tourism 17 % from 1 July 2025), s. 16 (c) (8 %), s. 20, s. 22, s. 51; consolidation 1258"

/-- Kernel 2.1 `DatedVat`: tourism-sector rate 16 % to 30 June 2025, 17 % from 1 July 2025 (s. 15 (b) (5)-(6)). Hand-made
(tools/p6/mv_gst.py): do not regenerate from bulk_cons_c.json. -/
def mvVat : DatedVat :=
  { periods := [{ vat := vatH1, statute := vatStatuteH1 }, { start := "2025-07-01", vat := vat, statute := vatStatute }] }

def families : List Family := [mvVat.family "Goods and services tax (two periods)"]

def absent : List Absent :=
  []

def notes : List String := ["MV 5111: GST Act (Law 10/2011), mvlaw.gov.mv consolidation 1258 (in force 2024-11-04 to 2026-08-30), read 2026-11-21"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["Schedule 1 basic goods (rice, sugar, flour, milk, eggs, tea, potatoes, onions, fresh fruit and vegetables and others) are zero-rated (GST Act s. 22 (a)): the basket's food class is modelled at 8 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .financial) then ["financial services are exempt only as prescribed by the GST Regulation (s. 20 (j)): the regulation was not read; the whole class is exempt"] else [])
  ++ (if g.consumption.any (fun s => s.good == .insurance) then ["insurance: whether it is a prescribed financial service (s. 20 (j)) was not read: taxed at 8 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .transport) then ["only international transport is exempt (s. 20 (l)); domestic transport at 8 % (domestic air carriers selling to non-Maldivians: tourism rate, s. 15 (a) (5), not applied)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .medicines || s.good == .health || s.good == .education) then ["medicines, health and education are exempt when supplied by providers registered with the State (s. 20 (e), (f), (h)): applied to the whole class"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther) then ["import duty on tobacco and alcohol (customs tariff) not modelled"] else [])

#guard vat.embedded { good := .clothing, amount := 10800 } == 800
#guard vat.embedded { good := .hotels, amount := 11700 } == 1700
#guard vatH1.embedded { good := .hotels, amount := 11600 } == 1600
#guard vat.embedded { good := .medicines, amount := 10800 } == 0
#guard vat.embedded { good := .rent, amount := 10800 } == 0
#guard (mvVat.vatOn 2025 "2025-03-01").map (·.reduced) == some 1600
#guard (mvVat.vatOn 2025 "2025-09-01").map (·.reduced) == some 1700

end MvGlobal.Consumption
