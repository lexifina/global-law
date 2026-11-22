import LkGlobal.Pit

/-!
# Sri Lanka 2025: value added tax (5111), Social Security Contribution Levy (5113); excise not modelled

Source: Value Added Tax Act, No. 14 of 2002, IRD consolidated text "incorporating amendments up to 2025" (26 Dec 2025;
each amendment with its Act and effective date), and the Value Added Tax (Amendment) Act, No. 4 of 2025 (certified
11 Apr 2025) itself (ird.gov.lk `publications/Value Added Tax_Acts/`; `lk/law/lk_vat_cons2025.pdf`,
`lk/law/lk_vat_04_2025.pdf`, sha256 in `SHA256SUMS`).
* **s. 2 (1) (ix)**: "for any taxable period commencing on or after January 1, 2024 at the rate of eighteen per centum
  (of which the tax fraction is 9/59)" (s. 2 (3) of Act 16 of 2024).
* **s. 10 (viii)**: registration where taxable supplies in the twelve months exceed sixty million rupees (or fifteen
  million in a taxable period): threshold 60 000 000.
* **First Schedule Part III** (taxable periods from 1 Jan 2024; Act 32 of 2023, as amended by Act 4 of 2025 s. 14):
  (a) (i) wheat and wheat flour, (iii) prescribed pharmaceuticals, (vi) kerosene; (b) (i) educational services,
  (ii) public passenger transport (not air, water, tourist or taxi), (iii) electricity, (viii) financial services
  (accounts, currency exchange, loans, securities; life insurance only), (ix) healthcare services other than hospital
  room charges, (x) Special Commodity Levy articles, (xii) locally made rice, rice flour and bread, (xiii) unprocessed
  local agricultural and fishing products, (xxv) liquid milk and yoghurt from local fresh milk.
* Residential letting is not in Part III (Part II item (xi) (e) already excluded lease or rent from 1 Jan 2023):
  standard-rated.

**Social Security Contribution Levy** (gap-closing session): Act No. 25 of 2022 and its amending Acts No. 15 of 2023, No. 15
of 2024 and No. 24 of 2025, read in lexifina/sri-lanka-law `act/2022/025`, `act/2023/015`, `act/2024/015`, `act/2025/024`
(official source parliament.lk act details G6262, G6303, G6336, G6407).
* **s. 3 (1)**: 2.5 % of the liable turnover of every taxable person (s. 2: importers, manufacturers, service providers,
  wholesalers and retailers) for every quarter from 1 October 2022. **Second Schedule**: liable turnover = 100 % of
  imports, 85 % of a manufacturer's turnover, 100 % of services (financial services: value addition), 50 % of wholesale
  and retail turnover (25 % for a manufacturer's registered distributor). s. 3 (3): turnover excludes VAT.
* **s. 4 (1) (c)** (Act No. 15 of 2024 s. 2, periods from 1 January 2024): registration once the turnover of four
  consecutive quarters exceeds Rs 60 million; s. 5 (1) (c): cancellation at or below it. Modelled: a company with annual
  turnover above Rs 60 million pays 2.5 % of the share of its turnover set by `company.sector` (manufacturing 85 %,
  commercialTrading 50 %, telecom and tourism 100 %); other or absent sectors are listed (grade C), as are financial
  services (value addition basis) and the First Schedule exemptions (exports, fuel from 1 July 2025 by Act No. 24 of
  2025 s. 2 (2), electricity generation, and others).
* Classification: a multi-stage cumulative turnover tax: OECD 5113 (Interpretative Guide §63), not 5126.
-/

namespace LkGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value added tax", standard := 1800, threshold := 60000000,
    classOf := fun gd => match gd with
      | .food | .medicines | .health | .education | .transport | .electricity | .financial | .heatingOil => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act No. 14 of 2002 s. 2 (1) (ix) (18 %), s. 10 (viii) (Rs 60 million), First Schedule Part III"


/-- `company.sector` (string or array) and `flags`. -/
def sectorsOf (g : CanonGlobal) : List String :=
  (match (g.raw.getObjValD "company").getObjValD "sector" with
   | Lean.Json.str s => [s]
   | Lean.Json.arr a => a.toList.filterMap fun j => match j with | Lean.Json.str s => some s | _ => none
   | _ => []) ++ g.company.flags
/-- SSCL Act No. 25 of 2022 Second Schedule: liable share of turnover (bp) by sector; `none` when the sector is absent or its
share is not read from the company's facts (financial services, exempt or mixed activities). -/
def ssclShareBp (g : CanonGlobal) : Option Int :=
  let s := sectorsOf g
  if s.any (fun x => ["bank", "insurer", "petroleum", "utilities", "shipping", "agriculture", "mining"].contains x) then none
  else if s.contains "manufacturing" then some 8500
  else if s.contains "commercialTrading" then some 5000
  else if s.any (fun x => ["telecom", "tourism"].contains x) then some 10000
  else none
/-- s. 3 (1): 2.5 % of the liable turnover; s. 4 (1) (c), 5 (1) (c): above Rs 60 million a year (from 2024). -/
def ssclCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company || g.company.turnover ≤ 60000000 then [] else
  match ssclShareBp g with
  | none => []
  | some sh =>
    [charge .salesTax "Social Security Contribution Levy (2.5 % of the liable turnover)" g.company.turnover
      (fun t => divR .down (t * sh) BP) (fun b => divR .down (250 * b) BP) (bearer := .entity)
      (statute := s!"Social Security Contribution Levy Act, No. 25 of 2022 s. 3 (1), Second Schedule (liable turnover {sh / 100} %), s. 4 (1) (c) as amended by Act No. 15 of 2024")]

def families : List Family :=
  [{ name := "5111 Value added tax", covers := [.vat, .salesTax],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ ssclCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["LK 5111: VAT Act No. 14 of 2002, IRD consolidation to 2025 + Amendment Act No. 4 of 2025 (rate 18 % from 1 Jan 2024; First Schedule Part III)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["food is modelled as exempt: rice, bread, wheat flour, unprocessed local produce and fish, local liquid milk and Special Commodity Levy articles are exempt (First Schedule Part III (a) (i), (b) (x), (xii), (xiii), (xxv)); processed food is taxable at 18 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .medicines) then ["only pharmaceuticals bought on a physician's prescription (and ayurvedic preparations) are exempt (Part III (a) (iii)-(iv)); applied to the whole class"] else [])
  ++ (if g.consumption.any (fun s => s.good == .transport) then ["public passenger transport other than air, water, tourist and taxi services is exempt (Part III (b) (ii)); applied to the whole class"] else [])
  ++ (if g.consumption.any (fun s => s.good == .insurance) then ["only life, Agrahara and crop/livestock insurance are exempt (Part III (b) (viii) (I)); insurance is modelled as taxable"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel) then ["excise duty (Excise (Special Provisions) Act No. 13 of 1989 and gazetted rates) not modelled"] else [])
  ++ (if g.entity == .company && g.company.turnover > 60000000 && (ssclShareBp g).isNone then ["5113 SSCL: the liable share of turnover (Second Schedule) depends on the activity: company.sector absent or not one of manufacturing, commercialTrading, telecom, tourism (financial services: value addition basis): not booked (grade C)"] else [])
  ++ (if g.entity == .company && g.company.turnover > 60000000 then ["5113 SSCL: First Schedule exemptions (exports, fuel from 1 July 2025, electricity generation, healthcare, education and others) and the 25 % share for registered distributors not applied; imports (100 %) not in the company facts"] else [])

#guard vat.embedded { good := .clothing, amount := 1180 } == 180
#guard vat.embedded { good := .rent, amount := 1180 } == 180
#guard vat.embedded { good := .electricity, amount := 1180 } == 0
#guard vat.net { turnover := 60000000, sales := [{ good := .other, net := 60000000 }] } == 0
#guard (ssclCharges { id := "t", household := { id := "t" }, entity := .company, company := { turnover := 100000000, flags := ["manufacturing"] } }).map (·.due) == [2125000]
#guard (ssclCharges { id := "t", household := { id := "t" }, entity := .company, company := { turnover := 100000000, flags := ["commercialTrading"] } }).map (·.due) == [1250000]
#guard (ssclCharges { id := "t", household := { id := "t" }, entity := .company, company := { turnover := 60000000, flags := ["manufacturing"] } }).length == 0
#guard (ssclCharges { id := "t", household := { id := "t" }, entity := .company, company := { turnover := 100000000 } }).length == 0

end LkGlobal.Consumption
