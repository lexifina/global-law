import SbGlobal.Pit

/-!
# Solomon Islands 2025: sales tax on prescribed services and fuel (5112); goods tax and excise not modelled

Source: Sales Tax Act (Cap. 125), Reprint "As in force at: 5 February 2024 … STATUS: CURRENT" (Legislation Act 2023),
published by the Inland Revenue Division (`ird.gov.sb/wp-content/uploads/2025/10/SALE-TAX-ACT-CAP-125.pdf`, fetched
2026-11-21; `sb/law/sb_sales_tax_cap125_2024.pdf`, sha256 in `SHA256SUMS`).
* **s. 3 (1)**: "Every purchaser of prescribed goods or services shall be charged a tax (to be known as "sales tax") …
  computed in such amount or at such percentage of the value thereof as may be prescribed".
* **Schedule One** items 1 "Local and Overseas Telecommunications: 10 cents in the dollar", 2 "Restaurant Services:
  10 cents in the dollar", 12 "Sale of petroleum … 10 cents per litre", 13 "Sale of diesoline … 10 cents per litre".
  Other goods and services are not prescribed (no sales tax).
The tax is charged on the purchaser on top of the price (10 % of the value): the basket amount is taken tax-inclusive.
Goods tax (Cap. 122, Reprint as in force 5 February 2024; Second Schedule as substituted by L.N. 73 of 2019: imported
goods 15 %, prescribed locally manufactured goods 10 %, rice 5 %) is levied on the wholesale sale value (s. 69), which the
basket does not carry: not modelled.
-/

namespace SbGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Sales tax", standard := 1000,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .beer | .wine | .spirits | .cigarettes | .tobaccoOther | .clothing | .rent | .water | .electricity | .gas | .petrol | .diesel | .heatingOil | .medicines | .health | .transport | .recreation | .books | .newspapers | .education | .hotels | .financial | .insurance | .other => .exempt
      | _ => .standard }

def vatStatute : String := "Sales Tax Act (Cap. 125) s. 3 (1), Schedule One items 1-2 (10 cents in the dollar)"

def excise : Excise :=
  { rates := [
      { good := .petrol, name := "Sales tax (petroleum)", perUnitNum := 10, perUnitDen := 100, statute := "Sales Tax Act (Cap. 125) Schedule One item 12 (10 cents per litre)" },
      { good := .diesel, name := "Sales tax (diesoline)", perUnitNum := 10, perUnitDen := 100, statute := "Sales Tax Act (Cap. 125) Schedule One item 13 (10 cents per litre)" }] }

def families : List Family :=
  [{ name := "5112 Sales tax (Cap. 125)", covers := [.salesTax, .excise],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [{ vat.basketCharge g.consumption vatStatute with oecd := .salesTax }])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [{ vat.businessCharge g.company vatStatute with oecd := .salesTax }] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["SB 5112: Sales Tax Act (Cap. 125) reprint as in force 5 February 2024, Schedule One"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty then ["goods tax (Goods Tax Act Cap. 122 s. 69, Second Schedule: imported goods 15 %, local manufactures 10 %, rice 5 %) is charged on the wholesale value, not in the basket: not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .transport || s.good == .recreation || s.good == .other) then ["Schedule One items charged per ticket or on particular services (air tickets $10, sea fares 10 %, movie tickets, professional, accounting, legal, real estate, vehicle hire) not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther) then ["excise (Customs and Excise Act) not modelled"] else [])

#guard vat.embedded { good := .restaurants, amount := 1100 } == 100
#guard vat.embedded { good := .food, amount := 1100 } == 0
#guard excise.duty { good := .petrol, amount := 1500, quantity := 100000 } == 10

end SbGlobal.Consumption
