import MyGlobal.Pit
import TaxKernel.Global2

/-!
# Malaysia 2025: service tax (Act 807) on basket services; sales tax (Act 806) and excise not modelled

Source: Service Tax (Rate of Tax) (Amendment) Order 2024, P.U. (A) 64 (Attorney General's Chambers; Royal Malaysian
Customs MySST page "SST Orders", `mysst.customs.gov.my/wp-content/uploads/2025/03/PERINTAH-CUKAI-PERKHIDMATAN-KADAR-CUKAI-PINDAAN-2024.pdf`,
fetched 2026-11-21; `my/law/my_service_tax_rate_amendment_order_2024.pdf`, sha256 in `SHA256SUMS`), made under Service Tax
Act 2018 [Act 807] s. 10 (2), in force from 1 March 2024:
* **para. 2 (a)**: in para. 3 (a) of the Service Tax (Rate of Tax) Order 2018 [P.U. (A) 213/2018] "enam peratus" is
  replaced by "… lapan peratus" (8 %) for taxable services other than food and beverage, telecommunications, parking and
  logistics;
* **para. 2 (c)**: new para. 3 (c): for "perkhidmatan penyediaan makanan dan minuman, perkhidmatan telekomunikasi,
  perkhidmatan penyediaan tempat letak kenderaan atau perkhidmatan logistik, enam peratus" (6 %).
Basket: restaurants 6 %, communication 6 %, hotels 8 % (`reduced` = 6 %, `standard` = 8 %); goods are outside service
tax (they bear the single-stage sales tax at manufacture or import, Act 806, not modelled).
Which services are taxable is fixed by the First Schedule to the Service Tax Regulations 2018 (as widened from 1 July 2025),
not read: restaurants are taxable only above the operator threshold there, and fee-based financial services, rental and
other services added on 1 July 2025 are not modelled (flagged). Grade B.

**Session 12 (year in force).** Service Tax (Rate of Tax) (Amendment) Order 2025, **P.U. (A) 173** (Federal Gazette 9 June
2025; para. 1 (2): in force 1 July 2025; MySST "SST Orders", Internet Archive 2026-01-22,
`my/law/my_service_tax_rate_amendment_order_2025_pua173_wb20260122.pdf`) replaces para. 3 of P.U. (A) 213/2018: (1) 8 % on
all taxable services; (2) (a) 6 % for the new First Schedule: 1-4 food and beverage, 5-6 telecommunications, 7 parking,
8 logistics, 9-11 health care, traditional and allied health, 12 construction work, 13 education; (b) Second Schedule
fixed amounts (credit cards RM 25 a card). The modelled services keep their rates across 1 July 2025: restaurants 6 %,
communication 6 %, hotels (accommodation) 8 % (no split). The scope widening (Service Tax Regulations First Schedule, from
1 July 2025: rental, fee-based financial services, private health and education with their exclusions) is not read:
flagged, grade B.

**Motor vehicle licence fee (LKM, 5200, session 10, grade B)**: JPJ guideline on the LKM rates for Peninsular Malaysia,
Sabah and Sarawak as amended after Budget 2009 (official; listed on JPJ's LKM page throughout 2025). Peninsular Malaysia,
petrol or diesel: **private saloon cars of individuals (code AB)**: flat RM 20 (to 1,000 cc), 55 (to 1,200), 70 (to
1,400), 90 (to 1,600); above 1,600 cc a base plus a rate per cc above the band floor: RM 200 + 0.40 (to 1,800), 280 + 0.50
(to 2,000), 380 + 1.00 (to 2,500), 880 + 2.50 (to 3,000), 2,130 + 4.50 (above). **Company-owned saloons (AC)**: RM 20, 110,
140, 180; above 1,600 cc 400 + 0.80, 560 + 1.00, 760 + 3.00, 2,260 + 7.50, 6,010 + 13.50. **Motorcycles above 150 cc**:
RM 30 (to 200 cc), 50 (to 250), 180 (to 500), 250 (to 800), 350 (above); 150 cc and below "kept at the existing rate"
(not stated: C). Reading: a vehicle of kind "car" is a saloon; the entity kind picks AB or AC; Peninsular rates
(Sabah, Sarawak, Langkawi and Pangkor differ); electric vehicles (separate kW guideline) not modelled.
-/

namespace MyGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Service tax", standard := 800, reduced := 600,
    classOf := fun gd => match gd with
      | .restaurants | .communication => .reduced
      | .food | .nonAlcoholic | .beer | .wine | .spirits | .cigarettes | .tobaccoOther | .clothing | .rent | .water | .electricity | .gas | .petrol | .diesel | .heatingOil | .medicines | .health | .transport | .recreation | .books | .newspapers | .education | .financial | .insurance | .other => .exempt
      | _ => .standard }

def vatStatute : String := "Service Tax Act 2018 s. 10 (2); Service Tax (Rate of Tax) Order 2018 para. 3 (a), (c) as amended by P.U. (A) 64/2024 (8 %; 6 % food and beverage, telecommunications) from 1 March 2024"



def myLkmSt : String := "JPJ guideline on LKM rates (amended after Budget 2009), Peninsular Malaysia, "

/-- Private saloon cars, petrol / diesel: individual (AB) or company (AC) rates. -/
def myLkmCar (company : Bool) : VehicleTax :=
  { name := if company then "Lesen kenderaan motor (motokar saloon, syarikat)" else "Lesen kenderaan motor (motokar saloon, individu)",
    kinds := ["car"], fuels := [.petrol, .diesel],
    parts := [(.engineCcm,
      if company then { bands := [(0, 20), (1001, 110), (1201, 140), (1401, 180), (1601, 400)],
                        steps := [(1600, 80), (1800, 100), (2000, 300), (2500, 750), (3000, 1350)], den := 100 }
      else { bands := [(0, 20), (1001, 55), (1201, 70), (1401, 90), (1601, 200)],
             steps := [(1600, 40), (1800, 50), (2000, 100), (2500, 250), (3000, 450)], den := 100 })],
    statute := myLkmSt ++ (if company then "1.1.3 (code AC)" else "1.1.2 (code AB)") }

/-- Motorcycles above 150 cc (1.1.1 ii); 150 cc and below: rate not stated (unmatched, C). -/
def myLkmMoto : VehicleTax :=
  { name := "Lesen kenderaan motor (motosikal)", kinds := ["motorcycle"], when := [(.engineCcm, 150, VehicleTax.noBound)],
    parts := [(.engineCcm, { bands := [(151, 30), (201, 50), (251, 180), (501, 250), (801, 350)] })],
    statute := myLkmSt ++ "1.1.1 ii (above 150 cc)" }

def myLkm (g : CanonGlobal) : List VehicleTax := [myLkmCar (g.entity == .company), myLkmMoto]

def families : List Family :=
  [{ name := "5126 Service tax (Act 807)", covers := [.goodsOther, .useOfGoods],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [{ vat.basketCharge g.consumption vatStatute with oecd := .goodsOther }])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [{ vat.businessCharge g.company vatStatute with oecd := .goodsOther }] else [])
       ++ vehicleTaxCharges (myLkm g) g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["MY 5126: service tax 8 % / 6 % (P.U. (A) 64/2024, from 1 March 2024)", "MY 5200: motor vehicle licence fee (LKM) by engine capacity, JPJ guideline (Budget 2009 rates), via kernel VehicleTax"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty then ["sales tax (Sales Tax Act 2018, single-stage at manufacture or import; Sales Tax (Rates of Tax) Order as revised 1 July 2025) not modelled: the basket carries retail prices"] else [])
  ++ (if g.consumption.any (fun s => s.good == .restaurants || s.good == .financial || s.good == .insurance || s.good == .rent || s.good == .health || s.good == .education || s.good == .transport || s.good == .recreation) then ["service tax First Schedule (Service Tax Regulations 2018, widened 1 July 2025) not read: restaurants taxed whatever the operator's turnover; the 2025 additions (fee-based financial services, rental, private health and education for non-citizens) not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel || s.good == .nonAlcoholic) then ["excise (Excise Act 1976, Excise Duties Order 2017 as amended) not modelled"] else [])
  ++ vehicleTaxUnknown "LKM" (myLkm g) g
  ++ vehicleTaxUnmatched "LKM" (myLkm g) g
  ++ (if g.vehicles.isEmpty then [] else ["LKM: Peninsular Malaysia rates (Sabah, Sarawak, Langkawi, Pangkor differ); a car is read as a saloon (other private vehicles, codes AD / AE, have other rates); electric vehicles (kW guideline) and motorcycles of 150 cc or less not modelled"])

#guard vat.embedded { good := .restaurants, amount := 10600 } == 600
#guard vat.embedded { good := .hotels, amount := 10800 } == 800
#guard vat.embedded { good := .food, amount := 10800 } == 0
#guard ((myLkmCar false).parts.map (fun (_, t) => t.amount 1500)) == [90]
#guard ((myLkmCar false).parts.map (fun (_, t) => t.amount 2000)) == [380]
#guard ((myLkmCar false).parts.map (fun (_, t) => t.amount 3500)) == [4380]
#guard ((myLkmCar true).parts.map (fun (_, t) => t.amount 2000)) == [760]

end MyGlobal.Consumption
