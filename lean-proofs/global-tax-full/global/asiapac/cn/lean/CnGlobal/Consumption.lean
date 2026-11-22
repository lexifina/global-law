import CnGlobal.Pit
import TaxKernel.Global2

/-!
# China 2025: value added tax (5111) and the urban maintenance and construction tax on it (5120); consumption tax on refined oil (5121, session 9)

Sources: 国家法律法规数据库 flk.npc.gov.cn official docx texts (`cn/law/flk/`, sha256 in `SHA256SUMS`). In 2025 VAT is
governed by the **增值税暂行条例** (2017 revision; the VAT Law of 2024-12-25 applies from 2026-01-01, not to 2025):
* **第二条**: goods 17 %, (二) transport, basic telecom, construction, leasing of immovable property, and listed goods
  (grain and other agricultural products, edible oil; tap water, heating, gas; books, newspapers, magazines) 11 %,
  (三) services 6 %, exports 0; "税率的调整，由国务院决定". The 2025 rates 13 % / 9 % / 6 % come from the State Council's
  adjustments (财政部 税务总局 海关总署公告2019年第39号), **not read**: flagged (grade B).
* **第十二条**: small-scale taxpayers 3 % (1 % by notice to 2027, not read); **第十五条** exemptions (agricultural
  producers' own products …), "除前款规定外，增值税的免税、减税项目由国务院规定": the exemptions of education and medical
  services (营改增 rules) are applied but not read (flagged).
* **城市维护建设税法 第二条, 第四条 (一)**: 7 % of the VAT and consumption tax actually paid where the taxpayer is in a city
  district (Beijing urban districts, the R3 reference area).

**消费税 on refined oil (session 9, grade A)**: 消费税暂行条例 第二条 (税目税率表; 调整由国务院决定), 第五条 从量定额 (tax =
quantity × unit amount); 财税〔2015〕11号 (MOF): **汽油 1.52 元/升**, **柴油 1.20 元/升** from 13 January 2015. No later
change to these unit amounts was found (2025 in force: no amending notice located; the 2008 table's 0.20 / 0.10 元/升 is
superseded). Levied on the producer or importer and carried into the retail price (charged here per litre of the basket).
Not modelled: cigarettes (ad valorem on the producer and wholesale prices, plus 0.003 + 0.005 元/支), spirits (20 % on
the producer price + 0.5 元/500 ml), beer (250 / 220 元/吨: the tonne-litre conversion of the 实施细则 not read), wine 10 %
(producer price).
-/

namespace CnGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "增值税", standard := 1300, reduced := 900, reduced2 := 600,
    classOf := fun gd => match gd with
      | .food | .water | .gas | .books | .newspapers | .transport | .rent | .communication => .reduced
      | .financial | .insurance | .restaurants | .hotels | .recreation => .reduced2
      | .education | .health => .exempt
      | _ => .standard }

def vatStatute : String := "增值税暂行条例 第二条 (rates adjusted to 13 % / 9 % / 6 % by 公告2019年第39号, not read), 第十五条"

/-- 城市维护建设税法 第四条 (一): 7 % of the VAT, in a city district. -/
def urbanBp : Int := 700

def basketCharges (g : CanonGlobal) : List Charge :=
  if g.consumption.isEmpty then [] else
  let v := vat.basket g.consumption
  [vat.basketCharge g.consumption vatStatute,
   charge .goodsOther "城市维护建设税" v id (fun x => divR .down (x * urbanBp) BP) (event := "basket") (level := .local)
     (bearer := .consumer) (statute := "城市维护建设税法 第二条, 第四条 (一) (市区 7 %; VAT inside the basket)")]

def businessCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company && !g.company.sales.isEmpty then
    let n := vat.net g.company
    [vat.businessCharge g.company vatStatute,
     charge .goodsOther "城市维护建设税" n id (fun x => divR .down (pos x * urbanBp) BP) (event := "supplies") (level := .local)
       (bearer := .consumer) (statute := "城市维护建设税法 第二条, 第四条 (一) (市区 7 %)")]
  else []

/-- 消费税暂行条例 第二条, 第五条; 财税〔2015〕11号: per litre on refined oil. -/
def cnFuelRules : List ExciseRule :=
  [{ good := .petrol, name := "消费税 (汽油)", perUnitNum := 152, perUnitDen := 100,
     statute := "消费税暂行条例 第二条, 第五条; 财税〔2015〕11号 一: 汽油 1.52 元/升 (from 2015-01-13)" },
   { good := .diesel, name := "消费税 (柴油)", perUnitNum := 120, perUnitDen := 100,
     statute := "消费税暂行条例 第二条, 第五条; 财税〔2015〕11号 二: 柴油 1.20 元/升 (from 2015-01-13)" }]

def cnExciseCharges (g : CanonGlobal) : List Charge := exciseRuleCharges cnFuelRules g (firstOnly := true)

def families : List Family :=
  [{ name := "5111 增值税, 5120 城市维护建设税; 5121 消费税 (成品油)", covers := [.vat, .goodsOther, .excise],
     run := fun _ g _ =>
       basketCharges g
       ++ businessCharges g
       ++ cnExciseCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["CN 5111/5120: 增值税暂行条例 (2017), 城市维护建设税法 (2020); Beijing urban district", "CN 5121: 消费税 on petrol 1.52 and diesel 1.20 元/升 (消费税暂行条例 第二条, 第五条; 财税〔2015〕11号)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["food taken at 9 % (agricultural products, edible oil); processed food is 13 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .communication) then ["telecom taken at 9 % (basic telecom); value-added telecom services are 6 %"] else [])
  ++ (if !g.consumption.isEmpty then ["教育费附加 3 % and 地方教育附加 2 % on VAT are fees, not taxes: not booked"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther) then ["消费税 on tobacco and alcohol not modelled: ad valorem on the producer's (and for cigarettes the wholesaler's) price, not in the basket; beer per tonne (tonne-litre conversion not read)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel) then ["城市维护建设税 on the 消费税 (城市维护建设税法 第二条: VAT and consumption tax paid) not added to its base"] else [])

#guard vat.embedded { good := .clothing, amount := 11300 } == 1300
#guard vat.embedded { good := .food, amount := 10900 } == 900
#guard vat.embedded { good := .restaurants, amount := 10600 } == 600
#guard (basketCharges { id := "x", household := { id := "x" }, consumption := [{ good := .clothing, amount := 113000 }] }).map (·.due) == [13000, 910]
#guard (cnFuelRules.find? (fun e => e.good == .petrol)).map (fun e => e.dutyOn { good := .petrol, amount := 800, quantity := 100000 } {}) == some 152
#guard (cnFuelRules.find? (fun e => e.good == .diesel)).map (fun e => e.dutyOn { good := .diesel, amount := 400, quantity := 50000 } {}) == some 60

end CnGlobal.Consumption
