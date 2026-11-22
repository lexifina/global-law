import TwGlobal.Pit

/-!
# Taiwan 2025: business tax (VAT, 5111), tobacco and alcohol tax and commodity tax on fuel (5121)

Sources: law.moj.gov.tw (全國法規資料庫) current texts, saved in `tw/law/moj/` (sha256 in `SHA256SUMS`):
* **加值型及非加值型營業稅法** (G0340080, 修正 民國114年05月28日): **第10條** "營業稅稅率…最低不得少於百分之五，最高不得超過百分之十；其
  徵收率，由行政院定之" (the rate in force, 5 %, is the Executive Yuan's: not read here, value flagged B). **第8條** exempt
  三、medical services and drugs of hospitals and clinics; 五、education by schools; 九、newspapers and publications of
  registered publishers. **第11條**: banks' and insurers' core business at 5 % / other financial at 2 % of gross
  receipts (non-value-added business tax, not inside household prices: financial services are taken as exempt).
* **菸酒稅法** (G0330010, 修正 民國114年01月24日): **第7條** 一、紙菸 "每千支徵收新臺幣一千五百九十元"; **第8條** 一（一）啤酒 "每公升
  徵收新臺幣二十六元", 二、蒸餾酒類 "每公升按酒精成分每度徵收新臺幣二點五元".
* **貨物稅條例** (G0340076, 修正 民國114年12月30日; 第10條 unchanged in that amendment): **第10條** 一、汽油 "每公秉徵收新臺幣六千八百三十元",
  二、柴油 "每公秉徵收新臺幣三千九百九十元".
-/

namespace TwGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "營業稅 (加值型)", standard := 500,
    classOf := fun gd => match gd with
      | .health | .medicines | .education | .newspapers | .books | .financial | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "加值型及非加值型營業稅法 第10條 (行政院 5 %), 第8條 三、五、九; 第11條"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "菸酒稅 (紙菸)", perUnitNum := 1590, perUnitDen := 1000, statute := "菸酒稅法 第7條 一 (每千支1 590元)" },
      { good := .beer, name := "菸酒稅 (啤酒)", perUnitNum := 26, statute := "菸酒稅法 第8條 一（一）(每公升26元)" },
      { good := .spirits, name := "菸酒稅 (蒸餾酒類)", perUnitNum := 250, onPureAlcohol := true, statute := "菸酒稅法 第8條 二 (每公升每度2.5元)" },
      { good := .petrol, name := "貨物稅 (汽油)", perUnitNum := 6830, perUnitDen := 1000, statute := "貨物稅條例 第10條 一 (每公秉6 830元)" },
      { good := .diesel, name := "貨物稅 (柴油)", perUnitNum := 3990, perUnitDen := 1000, statute := "貨物稅條例 第10條 二 (每公秉3 990元)" }] }

def families : List Family :=
  [{ name := "5111 營業稅, 5121 菸酒稅・貨物稅 (油氣類)", covers := [.vat, .excise],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["TW 5111/5121: law.moj.gov.tw current texts (amended 2025)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .cigarettes) then ["菸品健康福利捐 (Tobacco Hazards Prevention Act) is a surcharge, not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .wine) then ["other brewed alcohol (菸酒稅法 第8條 一（二）, 7元 per degree per litre) needs the line's strength: wine is not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .rent) then ["house rent from individual landlords bears no business tax (not a business): the basket's rent is taken at 5 % only if the landlord is a business"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food) then ["unprocessed agricultural products (第8條) taken at the standard rate"] else [])

#guard vat.embedded { good := .clothing, amount := 10500 } == 500
#guard excise.duty { good := .cigarettes, amount := 125, quantity := 20000 } == 31
#guard excise.duty { good := .spirits, amount := 1000, quantity := 1000, abvBp := 4000 } == 100
#guard excise.duty { good := .petrol, amount := 3000, quantity := 100000 } == 683

end TwGlobal.Consumption
