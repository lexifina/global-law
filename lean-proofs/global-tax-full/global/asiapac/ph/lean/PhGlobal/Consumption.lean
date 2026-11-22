import PhGlobal.Pit
import TaxKernel.Global2

/-!
# Philippines 2025: value-added tax (5111) and excise on motor fuels (5121)

Source: Republic Act No. 10963 (TRAIN Law, 2017), official signed copy (`cmp20/world/B03-asia-east-se/ph/law/ra10963.pdf`,
OCR in `ph/law/train/p*.txt`, sha256 in `SHA256SUMS`), amending the NIRC of 1997:
* **NIRC Sec. 106 (A)** (as amended by RA 10963 s. 31): "a value-added tax equivalent to twelve percent (12%) of the gross
  selling price"; Sec. 108 the same on services.
* **Sec. 109 (1) (BB)**: exempt where "the gross annual sales and/or receipts do not exceed the amount of Three million
  pesos (P3,000,000)"; (AA) drugs for diabetes, high cholesterol and hypertension.
* **Sec. 148** (RA 10963 s. 43), "Effective January 1, 2020": (f) "Unleaded premium gasoline, per liter of volume capacity,
  Ten pesos (P10.00)"; (i) "Diesel fuel oil … per liter of volume capacity, Six pesos (P6.00)".
The other Sec. 109 (1) exemptions (agricultural food in its original state, hospital and education services, residential
lease up to P15,000 a month) are applied from the structure of the Code but their pages were not read (flagged).

**Motor Vehicle User's Charge (5200, session 9, grade A)**: Republic Act No. 8794 (2000): **s. 2** the MVUC, in lieu of the
registration fee and the private motor vehicle tax, "collected from and paid by the owner of the motor vehicle"; **s. 3 (b)**
base rates plus 100 % from the fourth year of the Act onwards (a private passenger car registered before the Act pays the
EO 43 tax plus 100 %, s. 3 (a): not modelled): private passenger cars by gross vehicle weight up to 1,600 kg P800, more
than 1,600 to 2,300 kg P1,800, more than 2,300 kg P4,000 (so P1,600, P3,600, P8,000 a year); motorcycles without sidecar
P120 (P240). The President may adjust the rates by the CPI at most once every five years: no adjustment order was located
(flag). Reading: the vehicle's `"massKg"` is taken as its GVW; cars first registered from 2001; SUVs (+15 % on utility
vehicles) and utility vehicles not modelled.
-/

namespace PhGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value-added tax", standard := 1200, threshold := 3000000,
    classOf := fun gd => match gd with
      | .food | .health | .education | .rent | .financial | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "NIRC Sec. 106 (A), 108 (12 %), Sec. 109 (1) (BB) (P3,000,000), as amended by RA 10963"

def excise : Excise :=
  { rates := [
      { good := .petrol, name := "Excise tax (unleaded premium gasoline)", perUnitNum := 10, statute := "NIRC Sec. 148 (f) as amended by RA 10963 (P10.00 per liter from 2020)" },
      { good := .diesel, name := "Excise tax (diesel fuel oil)", perUnitNum := 6, statute := "NIRC Sec. 148 (i) as amended by RA 10963 (P6.00 per liter from 2020)" }] }



def phMvucSt : String := "RA 8794 ss. 2, 3 (b) (base rate plus 100 % from the fourth year): "

def phMvuc : List VehicleTax :=
  [{ name := "Motor Vehicle User's Charge (private car, GVW up to 1,600 kg)", kinds := ["car"], regFrom := 2001,
     when := [(.massKg, -1, 1600)], fixed := 1600, proRata := false, statute := phMvucSt ++ "P800 + 100 % = P1,600" },
   { name := "Motor Vehicle User's Charge (private car, GVW 1,601-2,300 kg)", kinds := ["car"], regFrom := 2001,
     when := [(.massKg, 1600, 2300)], fixed := 3600, proRata := false, statute := phMvucSt ++ "P1,800 + 100 % = P3,600" },
   { name := "Motor Vehicle User's Charge (private car, GVW above 2,300 kg)", kinds := ["car"], regFrom := 2001,
     when := [(.massKg, 2300, VehicleTax.noBound)], fixed := 8000, proRata := false, statute := phMvucSt ++ "P4,000 + 100 % = P8,000" },
   { name := "Motor Vehicle User's Charge (motorcycle without sidecar)", kinds := ["motorcycle"],
     fixed := 240, proRata := false, statute := phMvucSt ++ "motorcycles without sidecar P120 + 100 % = P240" }]

def families : List Family :=
  [{ name := "5111 VAT, 5121 excise on fuels", covers := [.vat, .excise, .useOfGoods],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ vehicleTaxCharges phMvuc g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["PH 5111/5121: NIRC as amended by RA 10963 (TRAIN)", "PH 5200: Motor Vehicle User's Charge (RA 8794 s. 3 (b)) by gross vehicle weight via kernel VehicleTax"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise on tobacco (RA 11346, RA 11467) and alcohol (RA 11467) not read: not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food || s.good == .health || s.good == .education || s.good == .rent) then ["Sec. 109 (1) exemptions other than (AA), (BB) taken from the Code's structure (pages not read)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .financial || s.good == .insurance) then ["banks and insurers pay percentage taxes (Secs. 121-123), not modelled"] else [])
  ++ vehicleTaxUnknown "MVUC" phMvuc g
  ++ vehicleTaxUnmatched "MVUC" phMvuc g
  ++ (if g.vehicles.isEmpty then [] else ["MVUC: the vehicle's massKg read as its gross vehicle weight; cars registered before 2001 (RA 8794 s. 3 (a): EO 43 tax + 100 %), utility vehicles, SUVs and vehicles for hire not modelled; no CPI adjustment order located"])

#guard vat.embedded { good := .clothing, amount := 1120 } == 120
#guard vat.net { turnover := 3000000, sales := [{ good := .other, net := 3000000 }] } == 0
#guard excise.duty { good := .petrol, amount := 6000, quantity := 100000 } == 1000
#guard excise.duty { good := .diesel, amount := 6000, quantity := 100000 } == 600
#guard phMvuc.length == 4
#guard (phMvuc.map (·.fixed)) == [1600, 3600, 8000, 240]

end PhGlobal.Consumption
