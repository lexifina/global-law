import CaGlobal.Pit
import TaxKernel.Global2

/-!
# Canada 2025 (Ontario): GST/HST (5111) and fuel and tobacco taxes (5121)

Sources (`ca/law/`): Justice Laws consolidations "current to 2026-10-29" of the **Excise Tax Act** (E-15) and the
**Excise Act, 2001** (E-14.1), read with their previous-version links (s. 165's only earlier version ended in 2007);
Ontario e-Laws API consolidations of the **Gasoline Tax Act** (dateFrom 2025-07-01, "2025, c. 10, Sched. 7"), **Fuel
Tax Act** (dateFrom 2025-07-01) and **Tobacco Tax Act** (dateFrom 2025-06-05).
* **ETA s. 165 (1)** "tax … at the rate of 5%"; **(2)** the participating-province rate, Schedule VIII "Ontario 8%":
  HST 13 % in Ontario; **(3)** zero-rated supplies 0 %: Schedule VI Part III basic groceries, Part I prescription
  drugs; exempt (Schedule V): Part I residential rent, Part II health care, Part III education, Part VI municipal
  water, Part VII financial services.
* **ETA Schedule I** s. 9 (a) "Unleaded gasoline … $0.10 per litre"; s. 9.1 "Diesel fuel … $0.04 per litre".
* **Ontario Gasoline Tax Act s. 2 (1)** "9 cents per litre"; **Fuel Tax Act s. 2 (1) (b)** "9 cents per litre on all
  clear fuel"; **Tobacco Tax Act s. 2 (1)** "11.1 cents on every cigarette and on every gram … of a tobacco product".
* Federal tobacco and alcohol duties (Excise Act, 2001 Schedules 1, 4, 6, beer Schedule) are base amounts "or … the
  adjusted rate" (indexed every 1 April; 2025 amounts in CRA notices, not read): unsupported.

**Customs (gap pass, kernel 2.8.0 `TariffRule`)**: Customs Tariff Schedule as published by the CBSA for 2025 (official tariff table, grade B). MFN lines for the representative goods; each preferential treatment (CUSMA UST/MXT, CETA, CPTPP, UK, Commonwealth Caribbean, the bilateral FTAs) as a `TariffPreference` with the lines on which the Schedule lists it Free (CPTPT 3 % on cigarettes, AUT/NZT 8.5 % and 11 % where listed). The GST/HST is charged on the duty-paid value (Excise Tax Act s. 215), so the duty is in the VAT base.
-/

namespace CaGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon CaGlobal

def vat : Vat :=
  { name := "GST/HST (Ontario)", standard := 1300,
    classOf := fun gd => match gd with
      | .food | .medicines => .zero
      | .rent | .health | .education | .water | .financial | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "Excise Tax Act s. 165 (1) 5 %, (2) and Sched. VIII Ontario 8 %, (3); Sched. V Parts I-III, VI, VII; Sched. VI Parts I, III"

def vatF : Family := vatFamily "GST/HST (Ontario)" vat vatStatute .vat .central

def lines : List ExLine :=
  [{ good := .petrol, name := "Excise tax + Ontario gasoline tax", num := 19, den := 100, statute := "Excise Tax Act Sched. I s. 9 (a) ($0.10/l); Gasoline Tax Act (Ont.) s. 2 (1) (9 cents/l)" },
    { good := .diesel, name := "Excise tax + Ontario fuel tax", num := 13, den := 100, statute := "Excise Tax Act Sched. I s. 9.1 ($0.04/l); Fuel Tax Act (Ont.) s. 2 (1) (b) (9 cents/l)" },
    { good := .cigarettes, name := "Ontario tobacco tax", num := 111, den := 1000, statute := "Tobacco Tax Act (Ont.) s. 2 (1) (11.1 cents per cigarette)" }]

def exciseF : Family :=
  { name := "5121 excises", covers := [.excise],
    run := fun _ g _ => exciseCharges lines g.consumption }

/-! ## 5123 customs import duties (kernel 2.8.0 `TariffRule`; gap pass 2026-11-21) -/

def tariff : TariffRule :=
  { name := "customs duty", country := "CA", vatOf := some vat,
    lines := [{ hs := "1006.30", statute := "1006.30.00 Free" },
      { hs := "2202.10", adValoremBp := 1100, statute := "2202.10.00 11 %" },
      { hs := "2203.00", statute := "2203.00.00 Free" },
      { hs := "2204.21.10", perUnitNum := 187, perUnitDen := 10000, statute := "2204.21.10 (<= 13.7 % vol) 1.87 cents per litre" },
      { hs := "2204.21.21", perUnitNum := 468, perUnitDen := 10000, statute := "2204.21.21 (13.7-14.9 % vol) 4.68 cents per litre" },
      { hs := "2208.30", statute := "2208.30.00 Free" },
      { hs := "2402.20", adValoremBp := 1250, statute := "2402.20.00 12.5 %" },
      { hs := "2710.12.90", statute := "2710.12.90 Free" },
      { hs := "2710.19.99", statute := "2710.19.99 Free" },
      { hs := "3004.90", statute := "3004.90.00 Free" },
      { hs := "4901.99", statute := "4901.99.00 Free" },
      { hs := "6109.10", adValoremBp := 1800, statute := "6109.10.00 18 %" },
      { hs := "6203.42", adValoremBp := 1700, statute := "6203.42.00 17 %" },
      { hs := "8471.30", statute := "8471.30.00 Free" },
      { hs := "8517.13", statute := "8517.13.00 Free" },
      { hs := "8703.23", adValoremBp := 610, statute := "8703.23.00 6.1 %" },
      { hs := "8703.80", adValoremBp := 610, statute := "8703.80.00 6.1 %" }],
    otherBp := -1,
    preferences := [{ name := "UST (CUSMA United States Tariff)", partners := ["US"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, UST column" },
      { name := "MXT (CUSMA Mexico Tariff)", partners := ["MX"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, MXT column" },
      { name := "CT (Chile Tariff)", partners := ["CL"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, CT column" },
      { name := "PT (Peru Tariff)", partners := ["PE"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, PT column" },
      { name := "UKT (United Kingdom Tariff)", partners := ["GB"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, UKT column" },
      { name := "CIAT (Canada-Israel Agreement Tariff)", partners := ["IL"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, CIAT column" },
      { name := "CRT (Costa Rica Tariff)", partners := ["CR"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, CRT column" },
      { name := "IT (Iceland Tariff)", partners := ["IS"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, IT column" },
      { name := "NT (Norway Tariff)", partners := ["NO"], hsOnly := ["2202.10", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, NT column" },
      { name := "SLT (Switzerland-Liechtenstein Tariff)", partners := ["CH", "LI"], hsOnly := ["2202.10", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, SLT column" },
      { name := "COLT (Colombia Tariff)", partners := ["CO"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, COLT column" },
      { name := "JT (Jordan Tariff)", partners := ["JO"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, JT column" },
      { name := "PAT (Panama Tariff)", partners := ["PA"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, PAT column" },
      { name := "HNT (Honduras Tariff)", partners := ["HN"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, HNT column" },
      { name := "KRT (Korea Tariff)", partners := ["KR"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, KRT column" },
      { name := "CEUT (CETA (Canada-European Union Tariff))", partners := ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, CEUT column" },
      { name := "UAT (Ukraine Tariff)", partners := ["UA"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, UAT column" },
      { name := "CCCT (Commonwealth Caribbean Countries Tariff)", partners := ["AG", "AI", "BB", "BM", "BS", "BZ", "DM", "GD", "GY", "JM", "KN", "KY", "LC", "MS", "TC", "TT", "VC", "VG"], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "2402.20", "6109.10", "6203.42", "8703.23", "8703.80"], statute := "Customs Tariff Schedule, CCCT column" },
      { name := "CPTPT (CPTPP Tariff)", partners := ["AU", "BN", "JP", "MY", "NZ", "SG", "VN", "GB", "MX", "CL", "PE"], byHs := [("2402.20", 300)], hsOnly := ["2202.10", "2204.21.10", "2204.21.21", "6109.10", "6203.42", "8703.23", "8703.80", "2402.20"], statute := "Customs Tariff Schedule, CPTPT column" },
      { name := "AUT (Australia Tariff)", partners := ["AU"], byHs := [("2202.10", 850), ("6109.10", 1100)], hsOnly := ["8703.23", "2202.10", "6109.10"], statute := "Customs Tariff Schedule, AUT column" },
      { name := "NZT (New Zealand Tariff)", partners := ["NZ"], byHs := [("2202.10", 850), ("6109.10", 1100)], hsOnly := ["8703.23", "2202.10", "6109.10"], statute := "Customs Tariff Schedule, NZT column" }],
    mfnIfOriginUnknown := true,
    statute := "Customs Tariff (S.C. 1997, c. 36) Schedule, MFN Tariff and preferential tariff treatments (CBSA Customs Tariff 2025, effective 1 January 2025)" }

def customsF : Family := customsFamily [tariff] "5123 customs import duties (Customs Tariff)"

/-- Imported lines whose duty this model cannot settle (grade C lines; the MFN or preferential duty is still shown). -/
def customsFlags (g : CanonGlobal) : List String :=
  (consumptionC g).zipIdx.flatMap fun ((s, x, c), i) =>
    let hs := (hsNormalize c.hsRaw).getD ""
    if !(x.imported || c.origin != "") || tariff.isDomestic c || !tariff.takesGood s.good then [] else
    let o := if c.origin == "" then "not given" else c.origin
    let pre := s!"5120 customs duty: line {i + 1} ({s.good.name}), origin {o}, hs {hs}: "
    (if c.origin == "US" then [pre ++ "United States Surtax Order (2025): a 25 % surtax on listed US goods from 4 March 2025 (most removed from 1 September 2025); the list and the entry date are not read, not computed (grade C)"] else []) ++
    (if c.origin == "CN" && (hs.startsWith "870380" || hs.startsWith "870340" || hs.startsWith "870360" || hs.startsWith "870370") then [pre ++ "China Surtax Order (2024): 100 % surtax on Chinese electric vehicles from 1 October 2024, not computed (grade C)"] else [])

def customsUnknown (g : CanonGlobal) : List String := tariff.unknown g ++ customsFlags g

/-- A one-household line with the given consumption lines (for the guards). -/
def custLine (lines : String) : CanonGlobal :=
  match Lean.Json.parse ("{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"consumption\":[" ++ lines ++ "]}") with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

def families : List Family := [vatF, exciseF, customsF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits) "federal tobacco and alcohol duties (Excise Act, 2001, CPI-adjusted every 1 April) and Ontario beer/wine taxes not read: not charged" ++ when (g.consumption.any fun s => s.good == .petrol || s.good == .diesel || s.good == .gas || s.good == .heatingOil) "federal fuel charge (Greenhouse Gas Pollution Pricing Act; set to nil from 1 April 2025) not read: not charged" ++ when (g.consumption.any fun s => s.good == .books || s.good == .clothing || s.good == .restaurants || s.good == .transport) "Ontario point-of-sale rebates of the 8 % component (books, children's clothing, meals ≤ $4) and the municipal transit exemption not modelled; the GST/HST holiday (14 Dec 2024 - 15 Feb 2025) not modelled" ++ when (g.consumption.any (·.good == .food)) "food read as basic groceries (zero-rated); prepared and snack foods are taxable") ++ customsUnknown g

#guard vat.embedded { good := .clothing, amount := 1130 } == 130
#guard vat.embedded { good := .food, amount := 1130 } == 0
#guard (lines.find? (·.good == .petrol)).get!.duty { good := .petrol, amount := 1500, quantity := 1000000 } == 190
#guard (lines.find? (·.good == .cigarettes)).get!.duty { good := .cigarettes, amount := 15, quantity := 20000 } == 2
-- cotton T-shirts from China (MFN 18 %): 11 300 / 1,13 = 10 000; / 1,18 = 8 474; 18 % = 1 525
#guard (tariff.charges (custLine "{\"good\":\"clothing\",\"amount\":11300,\"hs\":\"6109.10\",\"origin\":\"CN\"}")).map (·.due) == [1525]
-- the same from the United States (UST Free): 0
#guard (tariff.charges (custLine "{\"good\":\"clothing\",\"amount\":11300,\"hs\":\"6109.10\",\"origin\":\"US\"}")).map (·.due) == [0]
-- from Australia: CPTPT Free comes first (AUT 11 % not lower)
#guard (tariff.charges (custLine "{\"good\":\"clothing\",\"amount\":11300,\"hs\":\"6109.10\",\"origin\":\"AU\"}")).map (·.due) == [0]
-- US origin: surtax flag
#guard (customsUnknown (custLine "{\"good\":\"clothing\",\"amount\":11300,\"hs\":\"6109.10\",\"origin\":\"US\"}")).length == 1

end CaGlobal.Consumption
