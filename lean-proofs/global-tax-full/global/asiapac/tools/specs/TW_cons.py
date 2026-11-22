S = dict(cc="TW", family_name="5111 營業稅, 5121 菸酒稅・貨物稅 (油氣類)",
doc=r'''# Taiwan 2025: business tax (VAT, 5111), tobacco and alcohol tax and commodity tax on fuel (5121)

Sources: law.moj.gov.tw (全國法規資料庫) current texts, saved in `tw/law/moj/` (sha256 in `SHA256SUMS`):
* **加值型及非加值型營業稅法** (G0340080, 修正 民國114年05月28日): **第10條** "營業稅稅率…最低不得少於百分之五，最高不得超過百分之十；其
  徵收率，由行政院定之" (the rate in force, 5 %, is the Executive Yuan's: not read here, value flagged B). **第8條** exempt
  三、medical services and drugs of hospitals and clinics; 五、education by schools; 九、newspapers and publications of
  registered publishers. **第11條**: banks' and insurers' core business at 5 % / other financial at 2 % of gross
  receipts (non-value-added business tax, not inside household prices: financial services are taken as exempt).
* **菸酒稅法** (G0330010, 修正 民國114年01月24日): **第7條** 一、紙菸 "每千支徵收新臺幣一千五百九十元"; **第8條** 一（一）啤酒 "每公升
  徵收新臺幣二十六元", 二、蒸餾酒類 "每公升按酒精成分每度徵收新臺幣二點五元".
* **貨物稅條例** (G0340076, 修正 民國114年12月30日; 第10條 unchanged in that amendment): **第10條** 一、汽油 "每公秉徵收新臺幣六千八百三十元",
  二、柴油 "每公秉徵收新臺幣三千九百九十元".''',
vat=dict(name="營業稅 (加值型)", standard=500, statute="加值型及非加值型營業稅法 第10條 (行政院 5 %), 第8條 三、五、九; 第11條",
  classes={"health":"exempt","medicines":"exempt","education":"exempt","newspapers":"exempt","books":"exempt","financial":"exempt","insurance":"exempt"}),
excise=[dict(good="cigarettes", name="菸酒稅 (紙菸)", num=1590, den=1000, statute="菸酒稅法 第7條 一 (每千支1 590元)"),
  dict(good="beer", name="菸酒稅 (啤酒)", num=26, statute="菸酒稅法 第8條 一（一）(每公升26元)"),
  dict(good="spirits", name="菸酒稅 (蒸餾酒類)", num=250, pure=True, statute="菸酒稅法 第8條 二 (每公升每度2.5元)"),
  dict(good="petrol", name="貨物稅 (汽油)", num=6830, den=1000, statute="貨物稅條例 第10條 一 (每公秉6 830元)"),
  dict(good="diesel", name="貨物稅 (柴油)", num=3990, den=1000, statute="貨物稅條例 第10條 二 (每公秉3 990元)")],
notes=["TW 5111/5121: law.moj.gov.tw current texts (amended 2025)"],
unsupported=[[["cigarettes"], "菸品健康福利捐 (Tobacco Hazards Prevention Act) is a surcharge, not modelled"],
  [["wine"], "other brewed alcohol (菸酒稅法 第8條 一（二）, 7元 per degree per litre) needs the line's strength: wine is not modelled"],
  [["rent"], "house rent from individual landlords bears no business tax (not a business): the basket's rent is taken at 5 % only if the landlord is a business"],
  [["food"], "unprocessed agricultural products (第8條) taken at the standard rate"]],
guards=["vat.embedded { good := .clothing, amount := 10500 } == 500","excise.duty { good := .cigarettes, amount := 125, quantity := 20000 } == 31",
  "excise.duty { good := .spirits, amount := 1000, quantity := 1000, abvBp := 4000 } == 100","excise.duty { good := .petrol, amount := 3000, quantity := 100000 } == 683"],
taxes=[{"oecd":"5111","tax":"營業稅 (加值型)","statute":"營業稅法 第8條, 第10條, 第11條","dated":"law.moj.gov.tw current (修正 2025-05-28)","grade":"B","kernel_parts":["Vat"],"unsupported":["the 5 % rate is the Executive Yuan's (not read)","GBRT on financial and small businesses (第11-13條) not modelled"]},
 {"oecd":"5121","tax":"菸酒稅 (cigarettes, beer, spirits), 貨物稅 (petrol, diesel)","statute":"菸酒稅法 第7條, 第8條; 貨物稅條例 第10條","dated":"law.moj.gov.tw current (amended 2025-01-24 / 2025-12-30)","grade":"A","kernel_parts":["Excise"],"unsupported":["wine, other tobacco by weight","commodity tax on other goods (vehicles, appliances)","菸品健康福利捐"]}])
