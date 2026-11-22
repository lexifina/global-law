import WsGlobal.Pit

/-!
# Samoa 2025: value added goods and services tax (5111); excise not modelled

Source: Value Added Goods and Services Tax Act 2015, "official version of this Act as at 31 December 2018" (revision
notes 2016-2018; Ministry for Revenue copy, Wayback 20251130151308 of
`revenue.gov.ws/wp-content/uploads/2022/08/Value-Added-Goods-and-Services-Tax-Act-2015.pdf`; `ws/law/ws_vagst2015.pdf`,
sha256 in `SHA256SUMS`).
* **s. 8 (3)**: "The rate of GST is: (a) for a taxable supply that is a zero-rated supply, zero percent; or (b) in any
  other case, 15%."
* **s. 9 (1) (b), (2)**: registration where taxable supplies in a 12 month period exceed the registration threshold;
  "The registration threshold is at least $130,000." (130 000 tala used).
* **Schedule 2 cl. 1** exempt: (a) financial services; (c) "the supply to passengers of transport services by buses and
  taxis"; (f) carriage of passengers by ships within Samoa.
* **Schedule 3 Part 1 cl. 1** zero-rated: (j) "a supply of educational services"; (k) "a supply of medical goods or
  services provided in hospitals"; (l) "a supply of water"; (o) electricity supplied under the Electric Power
  Corporation Act 1980.
The 2018 revised text is the latest official version reached; the 15 % rate is taken as in force in 2025 (grade B).
-/

namespace WsGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value added goods and services tax", standard := 1500, threshold := 130000,
    classOf := fun gd => match gd with
      | .financial | .transport => .exempt
      | .education | .health | .water | .electricity => .zero
      | _ => .standard }

def vatStatute : String := "VAGST Act 2015 s. 8 (3) (15 %), s. 9 (2) ($130,000), Schedule 2 cl. 1, Schedule 3 Part 1 cl. 1"

def families : List Family :=
  [{ name := "5111 Value Added Goods and Services Tax", covers := [.vat],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["WS 5111: VAGST Act 2015 (official version as at 31 December 2018)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel || s.good == .nonAlcoholic) then ["excise (Excise Tax Rates Act 1984 Schedule, as amended to 2019 and later) not modelled: the 2025 schedule was not reached"] else [])
  ++ (if g.consumption.any (fun s => s.good == .health || s.good == .transport) then ["zero-rating of medical supplies covers hospitals only (Schedule 3 cl. 1 (k)); transport exemption covers buses, taxis and domestic ships only; applied to the whole class"] else [])

#guard vat.embedded { good := .clothing, amount := 1150 } == 150
#guard vat.embedded { good := .water, amount := 1150 } == 0
#guard vat.net { turnover := 130000, sales := [{ good := .other, net := 130000 }] } == 0

end WsGlobal.Consumption
