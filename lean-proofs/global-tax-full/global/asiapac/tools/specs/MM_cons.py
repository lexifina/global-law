S = dict(cc="MM", family_name="5112 Commercial tax",
doc=r'''# Myanmar 2025: commercial tax (5112); specific goods tax not modelled

Source: Union Taxation Law, 2025 (State Administration Council Law No. 6/2025 of 31 March 2025, in force 1 April 2025,
s. 1 (b)), English version on ird.gov.mm (`storage/laws/6892fa8676198-6-2025The Union Taxation Law,.pdf`;
`mm/law/mm_utl2025.pdf`), which sets the schedules of the Commercial Tax Law (1990) under its s. 6 (s. 14); the
Commercial Tax Law English version (`mm/law/mm_ctl_en.pdf`). sha256 in `SHA256SUMS`.
* **s. 14 (b), (c), (e)**: commercial tax 5 % on the sale proceeds of goods produced and sold, on the landed value of
  imports, on trading, and on the receipts of services other than (d)-(i).
* **s. 14 (a)** goods not taxed: 1-10 rice, wheat, pulses, vegetables, fruit, fresh fish, meat and eggs, cooking oils,
  sugar, milk and dairy, fish sauce and dried fish; 21 textbooks, books, magazines, journals and newspapers;
  22, 25 traditional and FDA-registered medicines.
* **s. 14 (d)** services not taxed: 10 public transportation; 12 education; 14 healthcare (except body fitness);
  18 life insurance; 21 monetary services of banks; (h) hotel and tourism services 3 %; (f) (ii) internet 15 %.
* **s. 15 (b)**: no commercial tax unless sale proceeds or service receipts exceed 50 million kyats in a financial year:
  threshold 50 000 000.
* January to March 2025 fall under the Union Taxation Law 2024 (not read): the 2025 schedules are applied to the
  whole calendar year.
* Commercial tax is booked under 5112 (the family rewrites the VAT helper's charge to `.salesTax`).''',
vat=dict(oecd="5112", name="Commercial tax", standard=500, reduced=300, threshold=50000000, statute="Union Taxation Law 2025 s. 14 (b)-(e), (h) (5 %, hotels 3 %), s. 15 (b) (50 million kyats); Commercial Tax Law 1990 s. 6",
  classes={"food":"exempt","books":"exempt","newspapers":"exempt","medicines":"exempt","health":"exempt","education":"exempt","transport":"exempt","financial":"exempt","hotels":"reduced"}),
notes=["MM 5112: Union Taxation Law 2025 (SAC Law No. 6/2025) s. 14-15, schedules of the Commercial Tax Law; in force 1 April 2025"],
unsupported=[[["food"],"basic foods listed in UTL 2025 s. 14 (a) 1-10 are not taxed; processed food not listed is taxed at 5 %: food modelled as not taxed"],
 [["communication"],"internet service is taxed at 15 % and SIM cards at 20,000 kyats each (UTL 2025 s. 14 (f)); communication is modelled at 5 %"],
 [["insurance"],"only life insurance is not taxed (UTL 2025 s. 14 (d) 18); insurance is modelled at 5 %"],
 [["transport"],"public transportation is not taxed (UTL 2025 s. 14 (d) 10); applied to the whole class"],
 ["*","January-March 2025 are governed by the Union Taxation Law 2024 (not read): the 2025 schedules are applied to the whole year"],
 [["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel"],"specific goods tax (UTL 2025 s. 11: per-stick and per-litre rates chosen by retail price tier) not modelled: the kernel has no price-tier selection"]],
extra_run=[],
guards=["vat.embedded { good := .clothing, amount := 1050 } == 50","vat.embedded { good := .hotels, amount := 1030 } == 30","vat.embedded { good := .food, amount := 1050 } == 0","vat.net { turnover := 50000000, sales := [{ good := .other, net := 50000000 }] } == 0"],
taxes=[{"oecd":"5112","tax":"Commercial tax (5 %; hotels and tourism 3 %)","statute":"Union Taxation Law, 2025 (SAC Law No. 6/2025) ss. 14-15; Commercial Tax Law 1990 s. 6","dated":"in force 1 April 2025 (s. 1 (b)); January-March 2025 under the Union Taxation Law 2024 (not read)","grade":"A","kernel_parts":["Vat"],"unsupported":["internet 15 % and SIM card charge not separated","Jan-Mar 2025 law not read"]},
 {"oecd":"5121","tax":"Specific goods tax","statute":"Specific Goods Tax Law 2016; Union Taxation Law 2025 s. 11 (price-tiered rates)","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["read: UTL 2025 s. 11 (cigarettes 14/27/30 kyats per stick by pack price tier, liquor 261-6,320 kyats per litre by price tier, beer 60 %, wine 210-5,160 kyats per litre by tier, tobacco 60 %); would unlock: a kernel rule selecting the rate by the retail unit price (KERNEL_REQUESTS.md R3-S4-1)"]}])

# ---- R3 session 6 (2026-11-21): specific goods tax by price tier under kernel 2.4.0 (ExciseRule minUnitPrice /
# maxUnitPrice, KERNEL_REQUESTS R3-S4-1 done). Union Taxation Law 2025 s. 11 (mm/law/mm_utl2025.pdf, English text
# of SAC Law No. 6/2025). Pre-change copy: tools/bak6/MM_cons.py.
S["imports"] = ["TaxKernel.Global2"]
S["family_name"] = "5112 Commercial tax; 5121 specific goods tax"
S["doc"] = S["doc"].replace("; specific goods tax not modelled", "; specific goods tax (5121)") + r'''

**Specific goods tax (session 6, grade A; kernel 2.4.0 price tiers)**: Union Taxation Law 2025 s. 11 (in force
1 April 2025): (a) the tax is charged on the factory sale price (domestic goods) or the landed value (imports). Table:
cigarettes 14 kyats per stick up to a sale price of 800 kyats for a pack of 20, 27 kyats for 801-1,100, 30 kyats for
1,101 and above (item 1); tobacco 60 % (2); cigars and pipe tobacco 80 % (5, 6); liquor per litre by the price per litre in
13 tiers from 261 kyats (400-2,200) to 6,320 kyats (26,401-28,600), 60 % of the price above 28,600 (8); beer 60 % (9);
wine 210 kyats (1-2,000) to 5,160 kyats (24,501-28,600) per litre in 12 tiers, 50 % above 28,600 (10).
The tier price and the ad valorem base are taken as the household's price before the specific goods tax and the 5 %
commercial tax (`priceBase := .beforeTax`, `vatBp := 500`): the factory price or landed value is not in the basket and
the distribution margin stays in it (flagged). Spirits are taken as liquor (item 8).'''
S["extra_lean"] = r'''/-- Union Taxation Law 2025 s. 11 table: price tiers `minUnitPrice < price ≤ maxUnitPrice` (kyats per pack of 20 for
cigarettes, per litre otherwise), on the price before this tax and the 5 % commercial tax. -/
def mmSgt : List ExciseRule :=
  let st (item : String) : String := s!"Union Taxation Law 2025 (SAC Law No. 6/2025) s. 11 (a) table item {item}"
  let cig (lo hi r : Int) (it : String) : ExciseRule :=
    { good := .cigarettes, name := "Specific goods tax (cigarettes)", perUnitNum := r, priceQty := 20000,
      minUnitPrice := lo, maxUnitPrice := hi, priceBase := .beforeTax, vatBp := 500, statute := st it }
  let tier (g : Good) (nm it : String) (lo hi r : Int) : ExciseRule :=
    { good := g, name := nm, perUnitNum := r, minUnitPrice := lo, maxUnitPrice := hi, priceBase := .beforeTax,
      vatBp := 500, statute := st it }
  let top (g : Good) (nm it : String) (lo bp : Int) : ExciseRule :=
    { good := g, name := nm, adValoremBp := bp, valueBase := .beforeTax, minUnitPrice := lo, priceBase := .beforeTax,
      vatBp := 500, statute := st it }
  let liq := [(399, 2200, 261), (2200, 4200, 686), (4200, 6600, 1172), (6600, 8800, 1646), (8800, 11000, 2138),
    (11000, 13200, 2632), (13200, 15400, 3125), (15400, 17600, 3619), (17600, 19800, 4113), (19800, 22000, 4607),
    (22000, 24200, 5101), (24200, 26400, 5799), (26400, 28600, 6320)]
  let wine := [(0, 2000, 210), (2000, 3500, 510), (3500, 5000, 810), (5000, 6500, 1147), (6500, 8000, 1635),
    (8000, 10000, 2085), (10000, 12000, 2521), (12000, 14000, 2985), (14000, 17500, 3435), (17500, 21000, 3960),
    (21000, 24500, 4560), (24500, 28600, 5160)]
  [cig (-1) 800 14 "1 (a)", cig 800 1100 27 "1 (b)", cig 1100 (-1) 30 "1 (c)"]
  ++ liq.map (fun (lo, hi, r) => tier .spirits "Specific goods tax (liquor)" "8 (a)-(m)" lo hi r)
  ++ [top .spirits "Specific goods tax (liquor)" "8 (n)" 28600 6000]
  ++ wine.map (fun (lo, hi, r) => tier .wine "Specific goods tax (wine)" "10 (a)-(l)" lo hi r)
  ++ [top .wine "Specific goods tax (wine)" "10 (m)" 28600 5000,
      { good := .beer, name := "Specific goods tax (beer)", adValoremBp := 6000, valueBase := .beforeTax, vatBp := 500,
        statute := st "9" }]'''
S["extra_run"] = S.get("extra_run", []) + ["exciseRuleCharges mmSgt g"]
S["extra_covers"] = S.get("extra_covers", []) + [".excise"]
S["unsupported"] = [u for u in S["unsupported"] if "specific goods tax" not in u[1].lower()] + [
 [["cigarettes", "spirits", "wine", "beer"], "specific goods tax: the tier price and ad valorem base are the factory sale price or landed value (UTL 2025 s. 11 (a)); the household's price before the tax and the 5 % commercial tax is used (distribution margin included); January-March 2025 (UTL 2024, not read) take the 2025 table"],
 [["spirits"], "spirits taken as liquor (item 8); liquor priced below 400 kyats per litre has no tier"],
 [["tobaccoOther"], "specific goods tax on tobacco 60 %, cheroots 2 kyats each, cigars and pipe tobacco 80 % (items 2-6): the class mixes them: not modelled"]]
S["guards"] = S["guards"] + ["mmSgt.length == 31",
 "(mmSgt.filter (fun e => e.appliesTo 2025 { good := .cigarettes, amount := 1000, quantity := 20000 } {})).map (·.perUnitNum) == [14]",
 "(mmSgt.filter (fun e => e.appliesTo 2025 { good := .cigarettes, amount := 2000, quantity := 20000 } {})).map (·.perUnitNum) == [30]"]
S["notes"] = S["notes"] + ["MM 5121: Union Taxation Law 2025 s. 11 specific goods tax by price tier (kernel 2.4.0 ExciseRule tiers)"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "5121"] + [
 {"oecd": "5121", "tax": "Specific goods tax (cigarettes 14/27/30 kyats per stick by pack price; liquor and wine per litre by price tier; beer 60 %)",
  "statute": "Union Taxation Law 2025 (SAC Law No. 6/2025) s. 11; Specific Goods Tax Law 2016 s. 6",
  "dated": "in force 1 April 2025 (s. 1 (b)); January-March 2025 under the Union Taxation Law 2024 (not read): the 2025 table applied to the whole year",
  "grade": "A", "kernel_parts": ["ExciseRule (2.4.0 price tiers)"],
  "unsupported": ["tier price taken before tax from the household price (factory price / landed value not in the basket)", "other tobacco items not modelled"]}]

# ---- R3 session 10 (2026-11-21): FT reviewer 6 item 1: January-March 2025 under the Union Taxation Law 2024.
# UTL 2024 (SAC Law No. 23/2024 of 29 March 2024, in force 1 April 2024, s. 1 (b)), English version on ird.gov.mm
# (`storage/laws/6749809ce9bdb-UTL_2024_(eng).pdf`, found through the site's search endpoint `/search/suggestions`;
# mm/law/mm_utl2024_en.pdf); its only amendment, SAC Law No. 54/2024 (1 Oct 2024 - 31 Mar 2025), changes the gold
# entries of s. 14 only (mm/law/mm_utl2024_amend.pdf). UTL 2025 (SAC Law No. 6/2025) is in force from 1 April 2025.
# s. 11 (a) table, UTL 2024: cigarettes 13 / 26 / 29 kyats per stick (pack of 20 up to 800, 801-1,100, 1,101 and above);
# liquor 237 kyats (400-2,000 per litre) to 5,745 kyats (22,001-24,000) in 13 tiers, 60 % above 24,000 (item 8);
# beer 60 % (9); wine 176 kyats (1-1,400) to 4,532 kyats (19,101-22,100) in 12 tiers, 50 % above 22,100 (10).
# The 2025 rules get validFrom 2025-04-01, the 2024 rules validTo 2025-04-01 (undated lines: share of the year by days).
S["doc"] = S["doc"] + r'''

**January-March 2025 (session 10)**: Union Taxation Law 2024 (SAC Law No. 23/2024, in force 1 April 2024, s. 1 (b);
amended only for gold by SAC Law No. 54/2024) s. 11 (a) table: cigarettes 13 / 26 / 29 kyats per stick by the same pack
price tiers (item 1); liquor per litre from 237 kyats (400-2,000) to 5,745 kyats (22,001-24,000) in 13 tiers, 60 % above
24,000 (item 8); beer 60 % (item 9); wine from 176 kyats (1-1,400) to 4,532 kyats (19,101-22,100) in 12 tiers, 50 % above
22,100 (item 10). The 2024 table runs to 31 March 2025 and the 2025 table from 1 April 2025 (UTL 2025 s. 1 (b)); a line
with no date is split by days (90/365 and 275/365).'''
S["extra_lean"] = S["extra_lean"] + r'''

/-- Union Taxation Law 2024 (SAC Law No. 23/2024) s. 11 (a) table, in force to 31 March 2025 (UTL 2025 from 1 April). -/
def mmSgt24 : List ExciseRule :=
  let st (item : String) : String := s!"Union Taxation Law 2024 (SAC Law No. 23/2024) s. 11 (a) table item {item} (to 31 March 2025)"
  let cig (lo hi r : Int) (it : String) : ExciseRule :=
    { good := .cigarettes, name := "Specific goods tax (cigarettes)", perUnitNum := r, priceQty := 20000,
      minUnitPrice := lo, maxUnitPrice := hi, priceBase := .beforeTax, vatBp := 500, statute := st it, validTo := "2025-04-01" }
  let tier (g : Good) (nm it : String) (lo hi r : Int) : ExciseRule :=
    { good := g, name := nm, perUnitNum := r, minUnitPrice := lo, maxUnitPrice := hi, priceBase := .beforeTax,
      vatBp := 500, statute := st it, validTo := "2025-04-01" }
  let top (g : Good) (nm it : String) (lo bp : Int) : ExciseRule :=
    { good := g, name := nm, adValoremBp := bp, valueBase := .beforeTax, minUnitPrice := lo, priceBase := .beforeTax,
      vatBp := 500, statute := st it, validTo := "2025-04-01" }
  let liq := [(399, 2000, 237), (2000, 3600, 624), (3600, 5400, 1065), (5400, 7200, 1496), (7200, 9000, 1944),
    (9000, 10800, 2393), (10800, 12600, 2841), (12600, 14400, 3290), (14400, 16200, 3739), (16200, 18000, 4188),
    (18000, 20000, 4637), (20000, 22000, 5272), (22000, 24000, 5745)]
  let wine := [(0, 1400, 176), (1400, 2600, 440), (2600, 4100, 737), (4100, 5600, 1067), (5600, 7100, 1397),
    (7100, 8600, 1727), (8600, 10100, 2057), (10100, 11600, 2387), (11600, 13100, 2717), (13100, 16100, 3212),
    (16100, 19100, 3872), (19100, 22100, 4532)]
  [cig (-1) 800 13 "1 (a)", cig 800 1100 26 "1 (b)", cig 1100 (-1) 29 "1 (c)"]
  ++ liq.map (fun (lo, hi, r) => tier .spirits "Specific goods tax (liquor)" "8 (a)-(m)" lo hi r)
  ++ [top .spirits "Specific goods tax (liquor)" "8 (n)" 24000 6000]
  ++ wine.map (fun (lo, hi, r) => tier .wine "Specific goods tax (wine)" "10 (a)-(l)" lo hi r)
  ++ [top .wine "Specific goods tax (wine)" "10 (m)" 22100 5000,
      { good := .beer, name := "Specific goods tax (beer)", adValoremBp := 6000, valueBase := .beforeTax, vatBp := 500,
        statute := st "9", validTo := "2025-04-01" }]

/-- The UTL 2025 table from 1 April 2025 (UTL 2025 s. 1 (b)). -/
def mmSgt25 : List ExciseRule := mmSgt.map fun e => { e with validFrom := "2025-04-01", statute := e.statute ++ " (from 1 April 2025)" }'''
S["extra_run"] = [("exciseRuleCharges (mmSgt24 ++ mmSgt25) g" if r == "exciseRuleCharges mmSgt g" else r) for r in S["extra_run"]]
S["unsupported"] = [[u[0], u[1].replace("; January-March 2025 (UTL 2024, not read) take the 2025 table", "")] for u in S["unsupported"]]
S["guards"] = S["guards"] + ["mmSgt24.length == 31",
 "(mmSgt24.filter (fun e => e.appliesTo 2025 { good := .cigarettes, amount := 1000, quantity := 20000 } {})).map (·.perUnitNum) == [13]",
 "(mmSgt24.filter (fun e => e.appliesTo 2025 { good := .cigarettes, amount := 2000, quantity := 20000 } {})).map (·.perUnitNum) == [29]"]
S["notes"] = S["notes"] + ["MM 5121 (session 10): Union Taxation Law 2024 s. 11 table to 31 March 2025, UTL 2025 from 1 April 2025 (ExciseRule date windows)"]
for t in S["taxes"]:
    if t["oecd"] == "5121":
        t.update(tax="Specific goods tax (cigarettes 13/26/29 kyats per stick to 31 Mar 2025, 14/27/30 from 1 Apr 2025; liquor and wine per litre by price tier; beer 60 %)",
                 statute="Union Taxation Law 2024 (SAC Law No. 23/2024) s. 11 (to 31 March 2025); Union Taxation Law 2025 (SAC Law No. 6/2025) s. 11 (from 1 April 2025); Specific Goods Tax Law 2016 s. 6",
                 dated="two periods: UTL 2024 (in force 1 April 2024, s. 1 (b); SAC Law 54/2024 amends s. 14 gold only) to 31 March 2025; UTL 2025 from 1 April 2025 (s. 1 (b)); undated lines split by days",
                 kernel_parts=["ExciseRule (2.4.0 price tiers, date windows)"])

# ---- R3 session 10 (2026-11-21): commercial tax January-March 2025: UTL 2024 s. 14 (b), (c), (e) 5 %, (h) hotels 3 %,
# s. 15 (b) 50 million kyats (mm/law/mm_utl2024_en.pdf): the rates and threshold modelled are the same in both Laws.
S["unsupported"] = [u for u in S["unsupported"] if not (u[0] == "*" and "Union Taxation Law 2024" in u[1])]
for t in S["taxes"]:
    if t["oecd"] == "5112":
        t["dated"] = "UTL 2024 (SAC Law No. 23/2024) ss. 14 (b), (c), (e), (h), 15 (b) to 31 March 2025 and UTL 2025 ss. 14-15 from 1 April 2025 (s. 1 (b)): the same 5 % / 3 % rates and 50 million kyat threshold"
        t["statute"] = t["statute"] + "; Union Taxation Law 2024 (SAC Law No. 23/2024) ss. 14 (b), (c), (e), (h), 15 (b) (to 31 March 2025)"
S["doc"] = S["doc"].replace("Union Taxation Law 2024 (not read)", "Union Taxation Law 2024 (read in session 10, see the end)") + r'''
Commercial tax January-March 2025: UTL 2024 s. 14 (b), (c), (e) 5 %, (h) hotel and tourism services 3 %, s. 15 (b)
threshold 50 million kyats: the modelled rates and threshold are the same as in UTL 2025.'''
