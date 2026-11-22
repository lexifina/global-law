S = dict(cc="JP", family_name="5111 消費税・地方消費税, 5121 揮発油税・地方揮発油税・軽油引取税・たばこ税・酒税",
doc=r'''# Japan 2025: consumption tax and local consumption tax (5111), excises (5121)

Sources: e-Gov 法令API v2, each act as in force on 2025-07-01 (`asof=2025-07-01`; revision ids in the saved files
`jp/law/egov/*_2025-07-01.xml`, sha256 in `jp/law/egov/SHA256SUMS`).
* **消費税法 第29条**: 一 standard "百分の七・八"; 二 軽減対象課税資産の譲渡等 "百分の六・二四". **別表第一** 一 飲食料品 (food other
  than 酒類; dining in and catering excluded), 二 newspapers published twice a week or more under subscription.
  **第9条 (1)**: exemption of an enterprise whose 基準期間 taxable sales are "千万円以下". **第6条 + 別表第二**: no tax on
  三 interest and insurance premiums, 六 medical care under the health insurance acts, 十一 school education, 十三
  residential letting.
* **地方税法 第72条の83**: "地方消費税の税率は、七十八分の二十二とする" (of the national tax: 2.2 % and 1.76 %; together 10 % and
  8 %). The basket VAT is booked as 消費税 (78 %, central) and 地方消費税 (22 %, state).
* **租税特別措置法 第88条の8 (1)**: per kl of gasoline "揮発油税にあつては四万八千六百円 … 地方揮発油税にあつては五千二百円".
* **地方税法 附則第12条の2の8**: 軽油引取税 "当分の間、一キロリットルにつき、三万二千百円".
* **たばこ税法 第11条 (1)** "千本につき六千八百二円"; **地方税法 第74条の5** (道府県) "千本につき千七十円"; **第468条** (市町村)
  "千本につき六千五百五十二円".
* **酒税法 第23条 (1)** per kl: 二 醸造酒類 (wine) 十万円; 三 蒸留酒類 二十万円, from 21 degrees plus 一万円 per degree above 20;
  **(3)** whisky, brandy and spirits under 37 degrees 三十七万円. Beer (発泡性酒類): the 2025 rate is a transitional rate
  in the supplementary provisions of the 2017 amending act, which e-Gov does not hold: not modelled.''',
extra_lean=r'''def vat : Vat :=
  { name := "消費税及び地方消費税", standard := 1000, reduced := 800, threshold := 10000000,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .newspapers => .reduced
      | .rent | .health | .education | .financial | .insurance => .exempt
      | _ => .standard }

/-- 消費税 is 78 % of the combined rate (7.8 / 10 and 6.24 / 8); 地方消費税 the rest. -/
def national (x : Int) : Int := divR .down (x * 78) 100

def vatStatute : String := "消費税法 第29条, 別表第一, 第6条・別表第二, 第9条; 地方税法 第72条の83 (78分の22)"

def basketCharges (g : CanonGlobal) : List Charge :=
  if g.consumption.isEmpty then [] else
  let total := vat.basket g.consumption
  let base := isum (g.consumption.map (·.amount))
  [charge .vat "消費税" base id (fun _ => national total) (event := "basket") (bearer := .consumer) (statute := vatStatute),
   charge .vat "地方消費税" base id (fun _ => total - national total) (event := "basket") (level := .state)
     (bearer := .consumer) (statute := "地方税法 第72条の83")]

def businessCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company && !g.company.sales.isEmpty then
    let n := vat.net g.company
    let base := isum (g.company.sales.map (·.net))
    [charge .vat "消費税" base id (fun _ => national n) (event := "supplies") (bearer := .consumer) (statute := vatStatute),
     charge .vat "地方消費税" base id (fun _ => n - national n) (event := "supplies") (level := .state) (bearer := .consumer)
       (statute := "地方税法 第72条の83")]
  else []

/-- 酒税 per kl on distilled liquor (酒税法 第23条 (1) 三, (3)): whisky/brandy/spirits under 37 degrees 370 000. -/
def spiritsPerKl (abvBp : Int) : Int :=
  let deg := abvBp / 100
  if deg < 21 then 200000 else if deg < 37 then 370000 else 200000 + 10000 * (deg - 20)

def excise : Excise :=
  { rates := [
      { good := .petrol, name := "揮発油税", perUnitNum := 48600, perUnitDen := 1000, statute := "租税特別措置法 第88条の8 (1) (48 600円/kl)" },
      { good := .diesel, name := "軽油引取税", perUnitNum := 32100, perUnitDen := 1000, statute := "地方税法 附則第12条の2の8 (32 100円/kl)" },
      { good := .cigarettes, name := "たばこ税（国）", perUnitNum := 6802, perUnitDen := 1000, statute := "たばこ税法 第11条 (1) (千本につき6 802円)" },
      { good := .wine, name := "酒税（醸造酒類）", perUnitNum := 100000, perUnitDen := 1000, statute := "酒税法 第23条 (1) 二 (10万円/kl)" }] }

def extraCharges (xs : List Spend) : List Charge :=
  (xs.filter (·.good == .petrol)).map (fun s => charge .excise "地方揮発油税" s.quantity id (fun q => divR .down (q * 5200) 1000000)
      (event := "petrol") (bearer := .consumer) (statute := "租税特別措置法 第88条の8 (1) (5 200円/kl)"))
  ++ (xs.filter (·.good == .cigarettes)).flatMap (fun s =>
      [charge .excise "道府県たばこ税" s.quantity id (fun q => divR .down (q * 1070) 1000000) (event := "cigarettes") (level := .state)
         (bearer := .consumer) (statute := "地方税法 第74条の5 (千本につき1 070円)"),
       charge .excise "市町村たばこ税" s.quantity id (fun q => divR .down (q * 6552) 1000000) (event := "cigarettes") (level := .local)
         (bearer := .consumer) (statute := "地方税法 第468条 (千本につき6 552円)")])
  ++ (xs.filter (·.good == .spirits)).map (fun s => charge .excise "酒税（蒸留酒類）" s.quantity id
        (fun q => divR .down (q * spiritsPerKl s.abvBp) 1000000) (event := "spirits") (bearer := .consumer)
        (statute := "酒税法 第23条 (1) 三, (3)"))''',
extra_run=["basketCharges g", "businessCharges g", "excise.charges g.consumption", "extraCharges g.consumption"],
extra_covers=[".vat", ".excise"],
notes=["JP 5111/5121: e-Gov texts as in force 2025-07-01"],
unsupported=[[["beer"], "酒税 on beer (発泡性酒類): the 2025 transitional rate is in the 2017 amending act's supplementary provisions (not in e-Gov): not modelled"],
  [["spirits"], "distilled liquor: whisky/brandy/spirits rate assumed below 37 degrees (shochu at the general 蒸留酒類 rate is not distinguished)"],
  [["restaurants"], "restaurant meals at 10 % (dining in); take-away food is in `food` (8 %)"],
  [["medicines"], "medicines at 10 % (over the counter); prescriptions under health insurance belong to `health` (exempt)"]],
guards=["vat.embedded { good := .clothing, amount := 1100 } == 100", "vat.embedded { good := .food, amount := 1080 } == 80",
  "(basketCharges { id := \"x\", household := { id := \"x\" }, consumption := [{ good := .clothing, amount := 110000 }] }).map (·.due) == [7800, 2200]",
  "vat.net { turnover := 10000000, sales := [{ good := .other, net := 10000000 }] } == 0",
  "excise.duty { good := .petrol, amount := 17500, quantity := 100000 } == 4860",
  "(extraCharges [{ good := .cigarettes, amount := 600, quantity := 20000 }]).map (·.due) == [21, 131]",
  "spiritsPerKl 4000 == 400000", "spiritsPerKl 2500 == 370000", "spiritsPerKl 1500 == 200000"],
taxes=[{"oecd":"5111","tax":"消費税・地方消費税","statute":"消費税法 第6条, 第9条, 第29条, 別表第一, 別表第二; 地方税法 第72条の83","dated":"e-Gov asof 2025-07-01 (revision 363AC0000000108_20250620)","grade":"A","kernel_parts":["Vat"],"unsupported":["simplified taxation (簡易課税), the 2割特例 for invoice registrants","invoice-registrant exemption limits"]},
 {"oecd":"5121","tax":"揮発油税・地方揮発油税・軽油引取税・たばこ税 (国・道府県・市町村)・酒税 (wine, spirits)","statute":"租特法 第88条の8; 地方税法 附則第12条の2の8, 第74条の5, 第468条; たばこ税法 第11条; 酒税法 第23条","dated":"e-Gov asof 2025-07-01","grade":"A","kernel_parts":["Excise","charge"],"unsupported":["beer and other sparkling liquor (transitional rate not in e-Gov)","石油石炭税, 航空機燃料税, 自動車重量税 (5200)"]}])

# ---- R3 session 6 (2026-11-21): vehicle taxes under kernel 2.4.0 (5200). 地方税法 as at 2025-07-01 (e-Gov,
# jp/law/egov/chihozei_2025-07-01.*): art. 177-7 (1) 1 ロ 自動車税種別割 (自家用乗用車, standard rates) and art. 463-15 (1)
# 2 ハ (1) (ii) 軽自動車税種別割. Pre-change copy: tools/bak6/JP_cons.py.
S["imports"] = S.get("imports", []) + ["TaxKernel.Global2"]
S["doc"] = S["doc"] + r'''

**Vehicle taxes (5200, session 6, grade A; kernel 2.4.0 `VehicleTax`)**: 地方税法 (as at 2025-07-01, e-Gov):
* **art. 177-7 (1) 1 ロ** 自動車税種別割, private passenger cars, standard rate per year by displacement: up to 1 l
  25,000 yen; 1-1.5 l 30,500; 1.5-2 l 36,000; 2-2.5 l 43,500; 2.5-3 l 50,000; 3-3.5 l 57,000; 3.5-4 l 65,500; 4-4.5 l
  75,500; 4.5-6 l 87,000; above 6 l 110,000 (prefectural; (4): a prefecture may exceed the standard rate up to 1.5 times:
  the prefecture's ordinance rate was not read). Applied to cars first registered from 2020 (the main text's rates;
  cars registered before 1 October 2019 keep the earlier rates of the 2019 amending act's supplementary provisions, not
  read: such cars are listed as unmatched, grade C). Months held: art. 177-10 (monthly for registration after 1 April).
* **art. 463-15 (1) 2 ハ (1) (ii)** 軽自動車税種別割 (municipal), four-wheeled private passenger kei cars (up to 660 cm³):
  10,800 yen a year; applied to kei cars first registered from 2016 (earlier ones: supplementary provisions, not read).
* Electric cars and cars without a displacement: no rule computes them (grade C line).'''
S["extra_lean"] = (S.get("extra_lean", "") + "\n\n" if S.get("extra_lean") else "") + r'''/-- 地方税法 art. 177-7 (1) 1 ロ: 自動車税種別割, private passenger cars, standard rates by displacement (cm³). -/
def jpCarTax : VehicleTax :=
  { name := "自動車税種別割", kinds := ["car"], regFrom := 2020, when := [(.engineCcm, 660, 100000)],
    parts := [(.engineCcm, { bands := [(0, 25000), (1001, 30500), (1501, 36000), (2001, 43500), (2501, 50000),
      (3001, 57000), (3501, 65500), (4001, 75500), (4501, 87000), (6001, 110000)] })],
    level := .state, statute := "地方税法 第177条の7 第1項第1号ロ (自家用乗用車, 標準税率)" }

/-- 地方税法 art. 463-15 (1) 2 ハ (1) (ii): 軽自動車税種別割, four-wheeled private passenger kei cars, 10,800 yen. -/
def jpKeiTax : VehicleTax :=
  { name := "軽自動車税種別割", kinds := ["car"], regFrom := 2016, when := [(.engineCcm, 0, 660)], fixed := 10800,
    proRata := false, level := .local, statute := "地方税法 第463条の15 第1項第2号ハ(1)(ii) (四輪乗用自家用)" }

def jpVehicleTaxes : List VehicleTax := [jpCarTax, jpKeiTax]'''
S["extra_run"] = S["extra_run"] + ["vehicleTaxCharges jpVehicleTaxes g"]
S["extra_covers"] = S.get("extra_covers", []) + [".useOfGoods"]
S["extra_unsupported"] = S.get("extra_unsupported", []) + [
 "vehicleTaxUnknown \"自動車税・軽自動車税種別割\" jpVehicleTaxes g",
 "vehicleTaxUnmatched \"自動車税・軽自動車税種別割\" jpVehicleTaxes g",
 "(if g.vehicles.isEmpty then [] else [\"vehicle taxes at the standard rates of 地方税法 art. 177-7 / 463-15 (the prefecture's or municipality's ordinance rates not read); 自動車重量税 (national, at inspection) and the 環境性能割 on acquisition not modelled\"])"]
S["guards"] = S["guards"] + ["(jpCarTax.parts.head?.map (fun p => p.2.bands.length)) == some 10", "jpKeiTax.fixed == 10800"]
S["notes"] = S["notes"] + ["JP 5200: 地方税法 art. 177-7, 463-15 (standard rates) via kernel 2.4.0 VehicleTax"]
S["taxes"] = S["taxes"] + [
 {"oecd": "5200", "tax": "自動車税種別割 (prefectural) and 軽自動車税種別割 (municipal) on private passenger cars",
  "statute": "地方税法 第177条の7 第1項第1号ロ, 第177条の10, 第463条の15 第1項第2号ハ(1)(ii)",
  "dated": "e-Gov text as at 2025-07-01", "grade": "A", "kernel_parts": ["VehicleTax"],
  "unsupported": ["standard rates (ordinance rates of the prefecture/municipality not read)", "cars registered before 2020 (kei: before 2016) and electric cars not computed (grade C lines)", "自動車重量税 and 環境性能割 not modelled"]}]
