S = dict(cc="AU", family_name="5111 GST",
doc=r'''# Australia 2025: goods and services tax (5111); excise not modelled

Source: A New Tax System (Goods and Services Tax) Act 1999, compilation C2025C00126 (C94), in force 15 February 2025
- 31 October 2025 (legislation.gov.au epub text; `au/law/fedleg/gst_C94_vol{1,2}.html`, sha256 in `SHA256SUMS`).
* **s. 9-70**: "The amount of GST on a taxable supply is 10% of the value of the taxable supply."
* GST-free: **s. 38-2** "A supply of food is GST-free" (s. 38-3: not food consumed on the premises, hot food,
  Schedule 1 items); **s. 38-7** medical services; **s. 38-85** education courses.
* Input taxed: **s. 40-5** financial supplies; **s. 40-35** residential rent.
* **s. 23-15 (1)**: registration turnover threshold "(a) $50,000; or (b) such higher amount as the regulations
  specify": the regulations' $75,000 is used (value flagged: GST Regulations 2019 not read).''',
vat=dict(name="Goods and services tax", standard=1000, threshold=75000, statute="GST Act 1999 s. 9-70 (10%), ss. 38-2, 38-7, 38-85 (GST-free), ss. 40-5, 40-35 (input taxed), s. 23-15",
  classes={"food":"zero","health":"zero","education":"zero","financial":"exempt","insurance":"exempt","rent":"exempt"}),
notes=["AU 5111: GST Act compilation C94 (15 Feb - 31 Oct 2025)"],
unsupported=[[["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel"],"excise (Excise Tariff Act 1921, CPI-indexed rates) and wine equalisation tax not modelled"],
 [["food"],"food taken as GST-free basic food (s. 38-3 exclusions such as restaurant and hot food go in `restaurants`)"],
 [["insurance"],"insurance taken as an input-taxed financial supply (only life cover is; general insurance is taxable)"]],
guards=["vat.embedded { good := .clothing, amount := 1100 } == 100","vat.embedded { good := .food, amount := 1100 } == 0",
 "vat.proRataBp [{ good := .food, net := 500 }, { good := .financial, net := 500 }] == 5000",
 "vat.net { turnover := 75000, sales := [{ good := .other, net := 75000 }] } == 0"],
taxes=[{"oecd":"5111","tax":"Goods and services tax","statute":"GST Act 1999 ss. 9-70, 23-15, 38-2, 38-3, 38-7, 38-85, 40-5, 40-35","dated":"compilation C94 (15 Feb - 31 Oct 2025)","grade":"B","kernel_parts":["Vat"],"unsupported":["the $75,000 threshold is in the GST Regulations (not read)","GST-free vs taxable food lines beyond s. 38-3"]},
 {"oecd":"5121","tax":"Excise and excise-equivalent customs duty; wine equalisation tax","statute":"Excise Tariff Act 1921; A New Tax System (Wine Equalisation Tax) Act 1999","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["indexed rates (s. 6A CPI indexation, twice yearly) not read; would unlock: the Excise Tariff compilation and the ATO's indexation notices for Feb and Aug 2025"]}])

# ---- R3 session 8 (2026-11-21): excise and excise-equivalent customs duty (5121), ATO rate tables (grade B).
# Pre-change copy: tools/bak8/AU_cons.py. Sources (Internet Archive captures; ato.gov.au answers 403 to scripts):
# au/law/au_ato_fuel_wb20250418.html, au_ato_fuel_wb20251119.html, au_ato_alcohol_wb20250125.html,
# au_ato_alcohol_wb20251208.html, au_ato_tobacco_wb20250212.html, au_ato_tobacco_wb20251118.html.
S["imports"] = ["TaxKernel.Global2"]
S["family_name"] = "5111 GST; 5121 excise"
S["doc"] = S["doc"].replace("; excise not modelled", "; excise and excise-equivalent customs duty (5121)") + r'''

**Excise and excise-equivalent customs duty (session 8, grade B)**: Excise Tariff Act 1921 Schedule items 1-3, 5 and 10,
rates as indexed under ss. 6A-6AA (CPI, February and August; tobacco by AWOTE in March and September), read from the
ATO's published rate tables (Internet Archive captures of ato.gov.au, which answers 403 to scripts). Imported goods bear
customs duty at the same rates (Customs Tariff Act 1995; the ATO tables state the equivalence for tobacco). Periods in 2025:
* **item 10.5 / 10.10 / 10.15** gasoline, diesel, heating oil, $ per litre: 0.506 (5 Aug 2024 - 2 Feb 2025), 0.508
  (3 Feb - 3 Aug 2025), 0.516 (from 4 Aug 2025). Fuel tax credits (business use) are not a household matter.
* **item 1 beer**, $ per litre of alcohol, on the alcohol content above 1.15 % by volume (packaged, container under 8 l):
  1.1 not exceeding 3 %: 52.66 / 52.87 / 53.72; 1.5 and 1.10 above 3 %: 61.32 / 61.57 / 62.56 (same periods as fuel).
* **items 2, 3.2, 3.10** spirits and other excisable beverages, $ per litre of alcohol: 103.89 / 104.31 / 105.98;
  **3.1 brandy** (line field `"sub": "brandy"`): 97.02 / 97.41 / 98.97.
* **item 5.1** cigarettes (stick form, not over 0.8 g of tobacco), $ per stick: 1.36623 (1 Sep 2024 - 28 Feb 2025),
  1.40312 (1 Mar - 31 Aug 2025), 1.49832 (from 1 Sep 2025); **item 5.5** other tobacco, $ per kg of tobacco content:
  2 101.89 / 2 158.65 / 2 397.31 (needs the line's `"massG"`).
* Wine is not an excisable beverage: wine equalisation tax (29 % of the wholesale value, WET Act 1999) is not modelled
  (no wholesale value in the basket).
Each period is evaluated with its own rules (a dated line in its period; an undated line by the period's share of the
year, as `ExciseRule` does). Beer: the line's strength is reduced by 115 bp before the per-litre-of-alcohol rate is
applied (the band limit 3 % becomes 185 bp on the reduced strength).'''
S["extra_lean"] = r'''/-- One rate period of the Excise Tariff Act 1921 Schedule as indexed (ATO tables), rules in `firstOnly` order. -/
def auPeriod (fr to : String) (fuel beerLo beerHi brandy spirits : Int) : List ExciseRule :=
  let st (it : String) := s!"Excise Tariff Act 1921 Schedule item {it} (indexed rate per the ATO table)"
  let f (g : Good) (it : String) : ExciseRule :=
    { good := g, name := "Excise duty (fuel)", perUnitNum := fuel, perUnitDen := 1000, validFrom := fr, validTo := to,
      statute := st it ++ s!": ${fuel}/1000 per litre" }
  let a (g : Good) (sub nm it : String) (r lo hi : Int) : ExciseRule :=
    { good := g, sub := sub, name := nm, perUnitNum := r, perUnitDen := 100, onPureAlcohol := true,
      minAbvBp := lo, maxAbvBp := hi, validFrom := fr, validTo := to,
      statute := st it ++ s!": ${r}/100 per litre of alcohol" }
  [f .petrol "10.5", f .diesel "10.10", f .heatingOil "10.15",
   a .beer "" "Excise duty (beer, alcohol above 1.15 %)" "1.1" beerLo (-1) 185,
   a .beer "" "Excise duty (beer, alcohol above 1.15 %)" "1.5/1.10" beerHi 185 100000,
   a .spirits "brandy" "Excise duty (brandy)" "3.1" brandy (-1) 100000,
   a .spirits "" "Excise duty (spirits)" "3.2/3.10" spirits (-1) 100000]

/-- Item 5: cigarettes per stick (num / 100000) and other tobacco per kg (num / 100) in one tobacco period. -/
def auTobacco (fr to : String) (stick kg : Int) : List ExciseRule :=
  [{ good := .cigarettes, name := "Excise duty (cigarettes)", perUnitNum := stick, perUnitDen := 100000,
     validFrom := fr, validTo := to,
     statute := s!"Excise Tariff Act 1921 Schedule item 5.1 (indexed rate per the ATO table): ${stick}/100000 per stick" },
   { good := .tobaccoOther, name := "Excise duty (tobacco by weight)", perKgNum := kg, perKgDen := 100,
     validFrom := fr, validTo := to,
     statute := s!"Excise Tariff Act 1921 Schedule item 5.5 (indexed rate per the ATO table): ${kg}/100 per kg of tobacco" }]

def auPeriods : List (List ExciseRule) :=
  [auPeriod "" "2025-02-03" 506 5266 6132 9702 10389,
   auPeriod "2025-02-03" "2025-08-04" 508 5287 6157 9741 10431,
   auPeriod "2025-08-04" "" 516 5372 6256 9897 10598,
   auTobacco "" "2025-03-01" 136623 210189,
   auTobacco "2025-03-01" "2025-09-01" 140312 215865,
   auTobacco "2025-09-01" "" 149832 239731]

/-- Beer is taxed on the alcohol above 1.15 % by volume (item 1): the line's strength less 115 bp. -/
def auBeerNet (g : CanonGlobal) : CanonGlobal :=
  { g with consumption := g.consumption.map fun s =>
      if s.good == .beer then { s with abvBp := max 0 (s.abvBp - 115) } else s }

def auExciseCharges (g : CanonGlobal) : List Charge :=
  auPeriods.flatMap fun rs => exciseRuleCharges rs (auBeerNet g) (firstOnly := true)'''
S["extra_run"] = S.get("extra_run", []) + ["auExciseCharges g"]
S["extra_covers"] = S.get("extra_covers", []) + [".excise"]
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("excise (Excise Tariff Act 1921")] + [
 [["wine"], "wine equalisation tax (29 % of the wholesale value, WET Act 1999) not modelled: no wholesale value in the basket"],
 [["tobaccoOther"], "excise on tobacco by weight (item 5.5) needs the line's \"massG\"; a line without it is charged 0"],
 [["beer"], "beer taken as packaged in containers under 8 litres (items 1.1, 1.5, 1.10); draught (kegs over 48 l) rates not applied"],
 [["spirits"], "brandy needs the line field \"sub\": \"brandy\" (item 3.1); other spirits at items 3.2 / 3.10"]]
S["guards"] = S["guards"] + [
 "auPeriods.length == 6",
 "((auPeriods.getD 1 []).find? (fun e => e.good == .petrol)).map (fun e => e.dutyOn { good := .petrol, amount := 200, quantity := 100000 } {}) == some 50",
 "((auPeriods.getD 4 []).find? (fun e => e.good == .cigarettes)).map (fun e => e.dutyOn { good := .cigarettes, amount := 50, quantity := 20000 } {}) == some 28",
 "((auPeriods.getD 1 []).find? (fun e => e.good == .beer && 185 < e.maxAbvBp)).map (fun e => e.dutyOn { good := .beer, amount := 60, quantity := 9000, abvBp := 365 } {}) == some 20",
 "((auPeriods.getD 2 []).find? (fun e => e.good == .spirits && e.sub == \"\")).map (fun e => e.dutyOn { good := .spirits, amount := 60, quantity := 700, abvBp := 4000 } {}) == some 29"]
S["notes"] = S["notes"] + ["AU 5121: Excise Tariff Act 1921 Schedule items 1, 3, 5, 10 at the indexed 2025 rates (ATO tables, 3 periods each); WET not modelled"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "5121"] + [
 {"oecd": "5121", "tax": "Excise and excise-equivalent customs duty (fuel, beer, spirits, tobacco; indexed 2025 rates)",
  "statute": "Excise Tariff Act 1921 Schedule items 1, 2, 3, 5, 10; ss. 6A-6AA indexation; Customs Tariff Act 1995 (equivalent customs duty)",
  "dated": "ATO rate tables for 2025 (fuel and alcohol: 3 Feb and 4 Aug 2025; tobacco: 1 Mar and 1 Sep 2025), Internet Archive captures 2025-01-25 to 2025-12-08",
  "grade": "B", "kernel_parts": ["ExciseRule"],
  "unsupported": ["wine equalisation tax (wholesale value) not modelled", "draught beer rates not applied", "tobacco by weight needs the line's mass"]}]

# ---- R3 session 8 (2026-11-21): NSW motor vehicle registration duty (5200, one-off on registration), kernel VehicleTax.
# Source: Duties Act 1997 (NSW) Chapter 9, text as at 30 Apr 2025 already local (au/law/nsw_duties_wb20250430.txt,
# Internet Archive copy used by FT reviewer 3). Pre-change copy: tools/bak8/AU_cons.py.before_veh.
S["doc"] = S["doc"] + r'''

**NSW motor vehicle registration duty (5200, session 8, grade A)**: Duties Act 1997 (NSW), Chapter 9 (text as at 30 April
2025, `au/law/nsw_duties_wb20250430.txt`): **s. 261** duty on an application to register a vehicle not previously
registered or registered to a new owner; **s. 263** payable by the applicant for registration; **s. 265 (1)** $3 per $100,
or part, of the dutiable value; **(2)** passenger vehicles (up to 9 occupants) with a dutiable value of not less than
$45,000: $1,350 plus $5 per $100, or part, of the value above $45,000; **s. 266** dutiable value = the consideration or the
market value, whichever is greater (the vehicle's `"value"`). Booked once, on a vehicle `"registeredThisYear"`. Cars only
(other vehicle kinds and the s. 267 exemptions not modelled); the annual motor vehicle tax (Motor Vehicles Taxation Act
1988, by tare weight) is not modelled (Act not read: legislation.nsw.gov.au refuses scripts).'''
S["extra_lean"] = S.get("extra_lean", "") + r'''

def auNswVehDuty : List VehicleTax :=
  [{ name := "Motor vehicle registration duty (NSW)", occasion := .registration, kinds := ["car"], level := .state,
     when := [(.value, -1, 44999)], parts := [(.value, { step := 100, steps := [(0, 3)], den := 100 })],
     statute := "Duties Act 1997 (NSW) ss. 261, 263, 265 (1), 266: $3 per $100, or part, of the dutiable value" },
   { name := "Motor vehicle registration duty (NSW)", occasion := .registration, kinds := ["car"], level := .state,
     when := [(.value, 44999, VehicleTax.noBound)], fixed := 1350,
     parts := [(.value, { step := 100, steps := [(45000, 5)], den := 100 })],
     statute := "Duties Act 1997 (NSW) ss. 261, 263, 265 (2), 266: passenger vehicle of $45,000 or more, $1,350 plus $5 per $100, or part, above $45,000" }]'''
S["extra_run"] = S.get("extra_run", []) + ["vehicleTaxCharges auNswVehDuty g"]
S["extra_covers"] = S.get("extra_covers", []) + [".useOfGoods"]
S["extra_unsupported"] = S.get("extra_unsupported", []) + [
 "vehicleTaxUnknown \"NSW registration duty\" auNswVehDuty g",
 "(if g.vehicles.isEmpty then [] else [\"NSW motor vehicle registration duty on cars registered this year only (other kinds and s. 267 exemptions not modelled); the annual motor vehicle weight tax (Motor Vehicles Taxation Act 1988) and registration fees not modelled\"])"]
S["guards"] = S["guards"] + [
 "auNswVehDuty.length == 2",
 "(({ step := 100, steps := [(0, 3)], den := 100 } : QtyTable).amount 30050) == 903",
 "(1350 + ({ step := 100, steps := [(45000, 5)], den := 100 } : QtyTable).amount 50050) == 1605"]
S["notes"] = S["notes"] + ["AU 5200: NSW Duties Act 1997 Ch. 9 motor vehicle registration duty (s. 265) via kernel VehicleTax"]
S["taxes"] = S["taxes"] + [
 {"oecd": "5200", "tax": "Motor vehicle registration duty (NSW; $3 per $100, $5 per $100 above $45,000 for passenger cars)",
  "statute": "Duties Act 1997 (NSW) ss. 261, 263, 265, 266", "dated": "NSW legislation text as at 30 April 2025 (Internet Archive)",
  "grade": "A", "kernel_parts": ["VehicleTax"],
  "unsupported": ["cars only; s. 267 exemptions not applied", "annual motor vehicle weight tax (Motor Vehicles Taxation Act 1988) and registration fees not modelled"]}]
