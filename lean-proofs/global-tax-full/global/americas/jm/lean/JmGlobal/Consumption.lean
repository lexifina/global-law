import JmGlobal.Pit
import TaxKernel.Global2

/-!
# Jamaica 2025: General Consumption Tax (5111); Special Consumption Tax grade C

Sources (Tax Administration Jamaica, fetched 2026-11-21; `jm/law/`, ARCHIVE_INDEX.tsv): the TAJ GCT guide
(`taj_gct1.html`): "History of the standard rate: ... June 2012 16.5% | April 2020 15.0%"; "Effective April 1,2025,
that value of supply is $15,000,000 over a 12-month period" (registration threshold); "telephone services, telephone
instrument and telephone cards which are taxed at twenty five percent (25%); and tourism services which are taxed at ten
percent (10%)"; GCT return Form 4A "amended 03.06.2025" (standard-rate and other-rate lines); TAJ "List of zero rated
and exempt items as per General Consumption Tax (GCT) Act" (December 2020, extracted from Part II of the First Schedule
and the Third Schedule "updated to the year 2020"). The GCT Act itself (laws.moj.gov.jm 503) was not reached: grade B
(official administrative texts, dated).
* Standard rate 15 % (from April 2020, TAJ history table); tourism services 10 %; telephone services 25 %.
* **First Schedule Part II (zero rated)** item 45: "The first 150 kilowatt hours in any month of supply of electricity
  services to residential customers for private and domestic use".
* **Third Schedule (exempt)**, goods: raw foodstuff, cornmeal and counter flour, "Bread, bulla and water crackers",
  "Rice", baking flour, unprocessed produce, List Four drugs; services: "Transportation of people within Jamaica, except
  tour services", "The rental of residential property used for residential purposes only", medical, dental, nursing
  services, education in an approved institution, "health insurance and life assurance but does not include group health
  insurance", "The supply of water (excluding bottled water) to the public", financial services.
* Processed food, fuel, books and newspapers carry the standard rate (no relief listed); the special consumption tax on
  fuel, alcohol and tobacco is not modelled.

**Customs (gap pass, kernel 2.8.0 `TariffRule`)**: Jamaica's integrated tariff (CARICOM CET with national lines; JCA, HS 2022) in force on 1 Jan 2025 (version effective 25 Sep 2024) and still the same on the lines used in the version effective 6 Oct 2025: import duty (ID) plus the 0.5 % environmental levy (ENVL), both ad valorem on the CIF value, booked together; CARICOM-origin goods pay no import duty (the levy remains). GCT is charged on the duty-inclusive value (`dutyInVatBase`).
-/

namespace JmGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon JmGlobal

def vat : Vat :=
  { name := "General Consumption Tax", standard := 1500, reduced := 1000, reduced2 := 2500, threshold := 15000000,
    classOf := fun gd => match gd with
      | .food | .water | .medicines | .health | .education | .transport | .rent | .insurance | .financial => .exempt
      | .hotels => .reduced
      | .communication => .reduced2
      | _ => .standard }

def vatStatute : String := "GCT Act: standard 15 % from April 2020 (TAJ rate history); tourism 10 %, telephone 25 %; First Schedule Part II item 45; Third Schedule (TAJ list 12/2020); registration threshold J$15,000,000 from 1 April 2025"

def vatF : Family := vatFamily "General Consumption Tax" vat vatStatute .vat .central

/-! ## 5123 customs import duties (kernel 2.8.0 `TariffRule`; gap pass 2026-11-21) -/

def tariff : TariffRule :=
  { name := "import duty and environmental levy", country := "JM", vatOf := some vat,
    lines := [{ hs := "1006.30", adValoremBp := 2550, statute := "1006.30 (all national lines) ID 25 %; environmental levy 0.5 %" },
      { hs := "2202.10", adValoremBp := 2050, statute := "2202.10.10/.90 ID 20 %; environmental levy 0.5 %" },
      { hs := "2402.20", adValoremBp := 4050, statute := "2402.20.00 ID 40 % (the special consumption tax per stick is an excise, P1); environmental levy 0.5 %" },
      { hs := "4901.99", adValoremBp := 50, statute := "4901.99.10/.90 ID 0; environmental levy 0.5 %" },
      { hs := "6109.10", adValoremBp := 2050, statute := "6109.10.10/.20 ID 20 %; environmental levy 0.5 %" },
      { hs := "6203.42", adValoremBp := 2050, statute := "6203.42 (all national lines) ID 20 %; environmental levy 0.5 %" },
      { hs := "8471.30", adValoremBp := 50, statute := "8471.30.00 ID 0; environmental levy 0.5 %" },
      { hs := "8517.13", adValoremBp := 2050, statute := "8517.13.00 ID 20 %; environmental levy 0.5 %" },
      { hs := "8528.72", adValoremBp := 2050, statute := "8528.72.00.10/.20 ID 20 %; environmental levy 0.5 %" }],
    otherBp := -1,
    preferences := [{ name := "CARICOM (Revised Treaty of Chaguaramas, Chapter Five: no import duty on goods of Community origin; the environmental levy still applies)", partners := ["AG", "BS", "BB", "BZ", "DM", "GD", "GY", "HT", "KN", "LC", "MS", "SR", "TT", "VC"], rateBp := 50, statute := "Revised Treaty of Chaguaramas Chapter Five; JCA tariff ENVL column" }],
    mfnIfOriginUnknown := true,
    statute := "Customs Act and the Customs Tariff (CARICOM CET with Jamaica's national lines) as published by the Jamaica Customs Agency, integrated tariff based on HS 2022 effective 25 Sep 2024 (in force on 1 Jan 2025) and 6 Oct 2025 (the same rates on every line used): columns ID (import duty) and ENVL (environmental levy 0.5 %)" }

def customsF : Family := customsFamily [tariff] "5123 customs import duties (JCA integrated tariff)"

/-- Imported lines whose duty this model cannot settle (grade C lines; the MFN or preferential duty is still shown). -/
def customsFlags (g : CanonGlobal) : List String :=
  (consumptionC g).zipIdx.flatMap fun ((s, x, c), i) =>
    let hs := (hsNormalize c.hsRaw).getD ""
    if !(x.imported || c.origin != "") || tariff.isDomestic c || !tariff.takesGood s.good then [] else
    let o := if c.origin == "" then "not given" else c.origin
    let pre := s!"5120 import duty and environmental levy: line {i + 1} ({s.good.name}), origin {o}, hs {hs}: "
    (if ["DO", "CR", "CU", "CO", "VE"].contains c.origin then [pre ++ "a CARICOM bilateral agreement with this origin may give a lower rate; not modelled, MFN booked (grade C)"] else [])

def customsUnknown (g : CanonGlobal) : List String := tariff.unknown g ++ customsFlags g

/-- A one-household line with the given consumption lines (for the guards). -/
def custLine (lines : String) : CanonGlobal :=
  match Lean.Json.parse ("{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"consumption\":[" ++ lines ++ "]}") with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

def families : List Family := [vatF, customsF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (when (g.consumption.any fun s => s.good == .food) "food: raw foodstuff, bread, rice, flour and cornmeal are exempt; processed food is taxable at 15 % (lower bound)" ++ when (g.consumption.any fun s => s.good == .electricity) "electricity: the first 150 kWh a month to residential customers are zero rated; charged at 15 % on all (upper bound)" ++ when (g.consumption.any fun s => s.good == .medicines) "medicines: only List Four drugs are exempt (lower bound)" ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) "special consumption tax on alcohol, tobacco and petroleum not modelled" ++ when (g.entity == .company) "registration threshold J$15,000,000 from 1 April 2025 applied to the whole year (J$10,000,000 before)") ++ customsUnknown g

#guard vat.embedded { good := .clothing, amount := 1150 } == 150
#guard vat.embedded { good := .hotels, amount := 1100 } == 100
#guard vat.embedded { good := .communication, amount := 1250 } == 250
#guard vat.embedded { good := .rent, amount := 1150 } == 0
#guard vat.threshold == 15000000
-- T-shirts from China: 11 500 / 1,15 = 10 000; / 1,205 = 8 298; 20,5 % = 1 701
#guard (tariff.charges (custLine "{\"good\":\"clothing\",\"amount\":11500,\"hs\":\"6109.10\",\"origin\":\"CN\"}")).map (·.due) == [1701]
-- from Trinidad and Tobago (CARICOM): 10 000 / 1,005 = 9 950; levy 0,5 % = 49
#guard (tariff.charges (custLine "{\"good\":\"clothing\",\"amount\":11500,\"hs\":\"6109.10\",\"origin\":\"TT\"}")).map (·.due) == [49]
-- from the Dominican Republic: MFN booked, flagged
#guard (customsUnknown (custLine "{\"good\":\"clothing\",\"amount\":11500,\"hs\":\"6109.10\",\"origin\":\"DO\"}")).length == 1

end JmGlobal.Consumption
