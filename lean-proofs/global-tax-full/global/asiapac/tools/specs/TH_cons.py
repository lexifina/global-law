S = dict(cc="TH", family_name="5111 ภาษีมูลค่าเพิ่ม",
doc=r'''# Thailand 2025: value added tax (5111); excise not modelled

Source: Revenue Code, Chapter 4 ss. 80-82 as published by the Revenue Department (rd.go.th/5206.html, current text
with its amendment notes; `th/law/rd/rd_5206.html`, sha256 in `SHA256SUMS`).
* **s. 80**: "ให้ใช้อัตราภาษีร้อยละ 10.0 … อัตราภาษีตามวรรคหนึ่งให้ลดลงได้โดยตราเป็นพระราชกฤษฎีกา"; the reduction to 7 % for 2025 is
  by Royal Decree (renewed yearly to 30 September 2026), not read: the 7 % is flagged (grade B).
* **s. 81 (1)** exempt: (ก)/(ข) unprocessed agricultural and animal products; (ฉ) newspapers, magazines, textbooks;
  (ช) education by schools; (ญ) medical care by hospitals; (ณ) domestic transport; (ต) letting of immovable property.
* **s. 81/1**: small businesses below the Royal Decree amount (at least 600 000 baht a year) are exempt; the decree's
  1 800 000 baht is used (flagged).
Financial services are under the specific business tax (Chapter 5), not VAT: exempt here.''',
vat=dict(name="ภาษีมูลค่าเพิ่ม", standard=700, threshold=1800000, statute="ประมวลรัษฎากร มาตรา 80 (10 %, reduced to 7 % by Royal Decree), มาตรา 81 (1), มาตรา 81/1",
  classes={"food":"exempt","newspapers":"exempt","books":"exempt","education":"exempt","health":"exempt","transport":"exempt","rent":"exempt","financial":"exempt","insurance":"exempt"}),
notes=["TH 5111: Revenue Code ss. 80-81/1 (rd.go.th); 7 % by Royal Decree"],
unsupported=[[["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel"],"excise (Excise Act B.E. 2560, rates by ministerial regulation) and the 10 % local surcharge not modelled"],
 [["financial","insurance"],"specific business tax (Revenue Code Chapter 5) on banking and finance not modelled"],
 [["food"],"food taken as unprocessed agricultural and animal products (exempt); processed food is taxable"]],
guards=["vat.embedded { good := .clothing, amount := 10700 } == 700","vat.embedded { good := .rent, amount := 10700 } == 0","vat.net { turnover := 1800000, sales := [{ good := .other, net := 1800000 }] } == 0"],
taxes=[{"oecd":"5111","tax":"ภาษีมูลค่าเพิ่ม (VAT)","statute":"Revenue Code ss. 80, 81 (1), 81/1","dated":"rd.go.th current text with amendment notes","grade":"B","kernel_parts":["Vat"],"unsupported":["the 2025 Royal Decree (7 %) and the small-business decree (1.8 M baht) not read"]},
 {"oecd":"5121","tax":"ภาษีสรรพสามิต (excise)","statute":"Excise Act B.E. 2560 and ministerial regulations on rates","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["rate regulations not reached; would unlock: excise.go.th rate tables (กฎกระทรวงกำหนดอัตราภาษี) as in force 2025"]}])

# ---- R3 session 8 (2026-11-21): ภาษีสรรพสามิต (excise, 5121), grade A. Pre-change copy: tools/bak8/TH_cons.py.
# Sources: Excise Department law database lawelcs.excise.go.th public JSON API (`/api/api/getlawchildbytypeid?typeid=2082`
# consolidated rate schedule, `typeid=5` ministerial regulations with full texts, `typeid=2` the Excise Act 2560):
# th/law/th_excise_sched_2082.json, th_excise_mr_typeid5.json, th_excise_act_typeid2.json (read 2026-11-21).
S["imports"] = ["TaxKernel.Global2"]
S["family_name"] = "5111 ภาษีมูลค่าเพิ่ม; 5121 ภาษีสรรพสามิต"
S["doc"] = S["doc"].replace("; excise not modelled", "; excise (5121)") + r'''

**ภาษีสรรพสามิต (session 8, grade A)**: พ.ร.บ.ภาษีสรรพสามิต พ.ศ. 2560 มาตรา 5 (rates by ministerial regulation within the
Act's schedule) and **มาตรา 17 (1)**: the ad valorem part is levied on the suggested retail price **excluding VAT**
(`valueBase := .netOfVat`, VAT 7 %); rates from กฎกระทรวงกำหนดพิกัดอัตราภาษีสรรพสามิต พ.ศ. 2560 as amended, read in the
Excise Department's law database (consolidated schedule and the texts of each amending regulation):
* **01.01 petrol** (baht per litre): gasohol E10 5.850 (ฉบับที่ 36, from 1 Feb 2024; restated with the carbon price by
  ฉบับที่ 41 from 29 Mar 2025) and 6.750 from 7 May 2025 (ฉบับที่ 42); benzine (line `"sub": "benzine"`) 6.500 / 7.500;
  E20 (`"sub": "e20"`) 5.200 / 6.000. **01.05 diesel** (1)-(2): 6.440 (ฉบับที่ 38, from 20 Apr 2024; ฉบับที่ 41) and 7.440
  from 7 May 2025 (ฉบับที่ 42).
* **13.01 (1) (ก) beer** 22 % + 430 baht per litre of pure alcohol; **(ข) grape wine and sparkling wine** 5 % + 1 000
  (ฉบับที่ 39, from 23 Feb 2024); **13.02 (2) (ข) 2) distilled spirits** 20 % + 255; **(ก) white spirit** (line `"sub":
  "white"`) 2 % + 155.
* **14.01 (1) cigarettes** (ฉบับที่ 17, from 1 Oct 2021): suggested retail price up to 72 baht a pack 25 % + 1.25 baht a
  stick; above 72 baht 42 % + 1.25 (tier read on the pack of 20 at the line's price, VAT included: the Act's
  "ราคาขายปลีกแนะนำ" is the price to consumers, s. 4).
Not modelled: the surcharge for local government (มาตรา 150: rate by Royal Decree, at most 10 % of the tax; decree not
read) and the earmarked levies on alcohol and tobacco (health promotion, broadcasting, sports, elderly funds: their Acts
not read).'''
S["extra_lean"] = r'''/-- พ.ร.บ.ภาษีสรรพสามิต 2560 มาตรา 17 (1): ad valorem on the retail price net of VAT 7 %. -/
def thRule (g : Good) (sub nm st : String) (adv perNum perDen : Int) (pure : Bool := false) (fr to : String := "") : ExciseRule :=
  { good := g, sub := sub, name := nm, adValoremBp := adv, valueBase := .netOfVat, vatBp := 700,
    perUnitNum := perNum, perUnitDen := perDen, onPureAlcohol := pure, validFrom := fr, validTo := to,
    statute := "พ.ร.บ.ภาษีสรรพสามิต พ.ศ. 2560 มาตรา 5, 17 (1); กฎกระทรวงกำหนดพิกัดอัตราภาษีสรรพสามิต พ.ศ. 2560 " ++ st }

def thFuel (fr to : String) (e10 benz e20 dsl : Int) (reg : String) : List ExciseRule :=
  [thRule .petrol "benzine" "ภาษีสรรพสามิต (น้ำมันเบนซิน)" s!"ประเภทที่ 01.01 (1), {reg}: {benz}/1000 บาทต่อลิตร" 0 benz 1000 false fr to,
   thRule .petrol "e20" "ภาษีสรรพสามิต (แก๊สโซฮอล์ อี 20)" s!"ประเภทที่ 01.01 (4), {reg}: {e20}/1000 บาทต่อลิตร" 0 e20 1000 false fr to,
   thRule .petrol "" "ภาษีสรรพสามิต (แก๊สโซฮอล์ อี 10)" s!"ประเภทที่ 01.01 (3), {reg}: {e10}/1000 บาทต่อลิตร" 0 e10 1000 false fr to,
   thRule .diesel "" "ภาษีสรรพสามิต (น้ำมันดีเซล)" s!"ประเภทที่ 01.05 (1)-(2), {reg}: {dsl}/1000 บาทต่อลิตร" 0 dsl 1000 false fr to]

def thDrinksTobacco : List ExciseRule :=
  [thRule .beer "" "ภาษีสรรพสามิต (เบียร์)" "ประเภทที่ 13.01 (1) (ก) (ฉบับที่ 39): ร้อยละ 22 และ 430 บาทต่อลิตรแห่งแอลกอฮอล์บริสุทธิ์" 2200 430 1 true,
   thRule .wine "" "ภาษีสรรพสามิต (ไวน์)" "ประเภทที่ 13.01 (1) (ข) (ฉบับที่ 39): ร้อยละ 5 และ 1,000 บาทต่อลิตรแห่งแอลกอฮอล์บริสุทธิ์" 500 1000 1 true,
   thRule .spirits "white" "ภาษีสรรพสามิต (สุราขาว)" "ประเภทที่ 13.02 (2) (ก): ร้อยละ 2 และ 155 บาทต่อลิตรแห่งแอลกอฮอล์บริสุทธิ์" 200 155 1 true,
   thRule .spirits "" "ภาษีสรรพสามิต (สุรากลั่น)" "ประเภทที่ 13.02 (2) (ข) 2): ร้อยละ 20 และ 255 บาทต่อลิตรแห่งแอลกอฮอล์บริสุทธิ์" 2000 255 1 true,
   { thRule .cigarettes "" "ภาษีสรรพสามิต (บุหรี่ซิกาแรต)" "ประเภทที่ 14.01 (1) (ก) (ฉบับที่ 17): ราคาขายปลีกแนะนำไม่เกินซองละ 72 บาท ร้อยละ 25 และ 1.25 บาทต่อมวน" 2500 125 100 with
       priceQty := 20000, maxUnitPrice := 72 },
   { thRule .cigarettes "" "ภาษีสรรพสามิต (บุหรี่ซิกาแรต)" "ประเภทที่ 14.01 (1) (ข) (ฉบับที่ 17): ราคาขายปลีกแนะนำเกินซองละ 72 บาท ร้อยละ 42 และ 1.25 บาทต่อมวน" 4200 125 100 with
       priceQty := 20000, minUnitPrice := 72 }]

def thPeriods : List (List ExciseRule) :=
  [thFuel "" "2025-05-07" 5850 6500 5200 6440 "ฉบับที่ 36, 38, 41",
   thFuel "2025-05-07" "" 6750 7500 6000 7440 "ฉบับที่ 42 (from 7 May 2025)",
   thDrinksTobacco]

def thExciseCharges (g : CanonGlobal) : List Charge :=
  thPeriods.flatMap fun rs => exciseRuleCharges rs g (firstOnly := true)'''
S["extra_run"] = S.get("extra_run", []) + ["thExciseCharges g"]
S["extra_covers"] = S.get("extra_covers", []) + [".excise"]
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("excise (Excise Act B.E. 2560")] + [
 [["spirits", "wine", "beer", "cigarettes", "tobaccoOther", "petrol", "diesel"], "the surcharge for local government (Excise Act 2560 s. 150, Royal Decree rate up to 10 % of the excise) and the earmarked health, broadcasting, sports and elderly-fund levies on alcohol and tobacco are not modelled"],
 [["petrol"], "petrol taken as gasohol E10 unless the line has \"sub\": \"benzine\" or \"e20\""],
 [["tobaccoOther"], "excise on cut tobacco and cigars (per gram, items 14.01 (2), (5), (6)) not modelled (no mass rule written)"],
 [["cigarettes"], "the 72-baht tier is read on the line's price per pack of 20 (VAT included); a line without a quantity is in no tier"]]
S["guards"] = S["guards"] + [
 "thPeriods.length == 3",
 "((thPeriods.getD 0 []).find? (fun e => e.good == .petrol && e.sub == \"\")).map (fun e => e.dutyOn { good := .petrol, amount := 3500, quantity := 100000 } {}) == some 585",
 "((thPeriods.getD 1 []).find? (fun e => e.good == .diesel)).map (fun e => e.dutyOn { good := .diesel, amount := 3300, quantity := 100000 } {}) == some 744",
 "(thDrinksTobacco.find? (fun e => e.good == .beer)).map (fun e => e.dutyOn { good := .beer, amount := 107, quantity := 1000, abvBp := 500 } {}) == some 43",
 "((thDrinksTobacco.filter (fun e => e.good == .cigarettes)).getD 1 default).dutyOn { good := .cigarettes, amount := 107, quantity := 20000 } {} == 67"]
S["notes"] = S["notes"] + ["TH 5121: Excise Act 2560 s. 17 (1); กฎกระทรวงกำหนดพิกัดอัตราภาษีสรรพสามิต 2560 as amended (ฉบับที่ 17, 36, 38, 39, 41, 42), Excise Department law database"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "5121"] + [
 {"oecd": "5121", "tax": "ภาษีสรรพสามิต (petrol, diesel, beer, wine, spirits, cigarettes)",
  "statute": "พ.ร.บ.ภาษีสรรพสามิต พ.ศ. 2560 มาตรา 5, 17 (1); กฎกระทรวงกำหนดพิกัดอัตราภาษีสรรพสามิต พ.ศ. 2560 ประเภทที่ 01.01, 01.05, 13.01, 13.02, 14.01 as amended by ฉบับที่ 17, 36, 38, 39, 41, 42",
  "dated": "texts of each amending regulation with their commencement dates (lawelcs.excise.go.th, read 2026-11-21); fuel rates change on 7 May 2025",
  "grade": "A", "kernel_parts": ["ExciseRule"],
  "unsupported": ["local-government surcharge (s. 150, decree up to 10 %) and earmarked fund levies not modelled", "cut tobacco and cigars per gram not modelled"]}]

# ---- R3 session 10 (2026-11-21): annual vehicle tax under the Motor Vehicle Act B.E. 2522 (5200), kernel VehicleTax.
# Source: Department of Land Transport page "การเสียภาษีประจำปี" (yearly-tax, _did=75; dated 9 June 2559 = 2016; Wayback
# 20190717152740, th/law/th_dlt_yearly_tax_wb20190717.html; the same page id is still published in 2024, Wayback
# 20240615230021, but its text is rendered by script and was not read). Official guide, not the Act's schedule: B.
S["imports"] = sorted(set(S.get("imports", []) + ["TaxKernel.Global2"]))
S["doc"] = S["doc"] + r'''

**Annual vehicle tax (5200, session 10, grade B)**: Motor Vehicle Act B.E. 2522 annual tax as set out by the Department of
Land Transport ("annual tax payment" page, dated 9 June 2016): private passenger cars of up to 7 seats by engine capacity,
0.50 baht per cc for the first 600 cc, 1.50 baht per cc from 601 to 1,800 cc, 4.00 baht per cc above 1,800 cc; twice that
for a car of a juristic person other than a hire-purchase lessor; a car registered for 5 years gets 10 % off in its 6th
year, 20 % in the 7th, 30 % in the 8th, 40 % in the 9th, 50 % from the 10th (the tax paid in 2025 is for registration year
2025 − first registration year + 1). Private motorcycles 100 baht each. Not modelled: cars of more than 7 seats, pickups
and trucks (by weight), electric vehicles (by weight, with temporary reductions not read).'''
S["extra_lean"] = S.get("extra_lean", "") + r'''

def thVehSt : String := "Motor Vehicle Act B.E. 2522 annual tax (Department of Land Transport rate page, 2016): "

/-- Private passenger car (up to 7 seats), by cc; × 2 for a juristic person; reduction from the 6th registration year. -/
def thCarTax (company : Bool) : VehicleTax :=
  { name := if company then "ภาษีรถประจำปี (รถยนต์นั่งส่วนบุคคล, นิติบุคคล)" else "ภาษีรถประจำปี (รถยนต์นั่งส่วนบุคคล)",
    kinds := ["car"], fuels := [.petrol, .diesel, .hybrid, .lpg, .cng],
    parts := [(.engineCcm, { steps := [(0, 50), (600, 150), (1800, 400)], den := 100 })],
    ageFactors := [(5, 9000), (6, 8000), (7, 7000), (8, 6000), (9, 5000)],
    multiplierBp := if company then 20000 else 10000,
    statute := thVehSt ++ "first 600 cc 0.50, 601-1,800 cc 1.50, above 1,800 cc 4.00 baht per cc"
      ++ (if company then "; juristic person: twice" else "") ++ "; 6th-10th registration year 10-50 % off" }

def thMotoTax : VehicleTax :=
  { name := "ภาษีรถประจำปี (รถจักรยานยนต์ส่วนบุคคล)", kinds := ["motorcycle"], fixed := 100,
    statute := thVehSt ++ "private motorcycle 100 baht" }

def thVeh (g : CanonGlobal) : List VehicleTax := [thCarTax (g.entity == .company), thMotoTax]'''
S["extra_run"] = S.get("extra_run", []) + ["vehicleTaxCharges (thVeh g) g (firstOnly := true)"]
S["extra_covers"] = S.get("extra_covers", []) + [".useOfGoods"]
S["extra_unsupported"] = S.get("extra_unsupported", []) + [
 "vehicleTaxUnknown \"annual vehicle tax\" (thVeh g) g",
 "vehicleTaxUnmatched \"annual vehicle tax\" (thVeh g) g",
 "(if g.vehicles.isEmpty then [] else [\"annual vehicle tax: a car is read as a private passenger car of up to 7 seats; cars of more than 7 seats, pickups and trucks (by weight) and electric vehicles (by weight, temporary reductions) not modelled\"])"]
S["guards"] = S["guards"] + [
 "((thCarTax false).parts.map (fun (_, t) => t.amount 1500)) == [1650]",
 "((thCarTax false).parts.map (fun (_, t) => t.amount 2400)) == [4500]"]
S["notes"] = S["notes"] + ["TH 5200: annual vehicle tax (Motor Vehicle Act B.E. 2522) by cc via kernel VehicleTax (DLT rate page, B)"]
S["taxes"] = S["taxes"] + [
 {"oecd": "5200", "tax": "ภาษีรถประจำปี (annual vehicle tax): private cars by cc, motorcycles 100 baht",
  "statute": "Motor Vehicle Act B.E. 2522 annual tax; Department of Land Transport rate page (2016)",
  "dated": "DLT page dated 2016-06-09 (Wayback 2019-07-17); page id still published in 2024 (script-rendered, not read); no 2025 change found",
  "grade": "B", "kernel_parts": ["VehicleTax"],
  "unsupported": ["cars above 7 seats, pickups and trucks (weight table)", "electric vehicles", "seats not checked"]}]

# --- R3 session 12 (2026-11-21): year in force: the VAT reduction decrees covering 2025 read (Nos. 790 and 799) ---
S['doc'] = S['doc'].replace("""by Royal Decree (renewed yearly to 30 September 2026), not read: the 7 % is flagged (grade B).""",
"""by Royal Decree: **พระราชกฤษฎีกา ... ว่าด้วยการลดอัตราภาษีมูลค่าเพิ่ม (ฉบับที่ 790) พ.ศ. 2567** (ราชกิจจานุเบกษา เล่ม 141
  ตอนที่ 57 ก, 20 Sep 2024; in force 1 Oct 2024) replaces มาตรา 4 of decree No. 646: "ร้อยละหกจุดสาม" (6.3 %) for liabilities
  from 1 Oct 2017 to 30 Sep 2025; **ฉบับที่ 799 พ.ศ. 2568** (เล่ม 142 ตอนที่ 59 ก, 14 Sep 2025; in force 1 Oct 2025) the same
  6.3 % to 30 Sep 2026 (rd.go.th `fileadmin/user_upload/kormor/newlaw/dc790.pdf`, `dc799.pdf`, read on the page images;
  `th/law/rd/rd_dc790.pdf`, `rd_dc799.pdf`). So 6.3 % all of 2025 (no split); with the local-government VAT of one ninth
  (6.3 % x 1/9 = 0.7 %, not read: registry) the 7 % charged. Grade B (the local share and s. 81/1 decree not read).""")
S['vat'] = dict(S['vat'])
S['vat']['statute'] = "ประมวลรัษฎากร มาตรา 80 (10 %; 6.3 % by พ.ร.ฎ. ฉบับที่ 790 (to 30 Sep 2025) and 799 (1 Oct 2025 - 30 Sep 2026)) + local VAT 1/9 = 7 %, มาตรา 81 (1), มาตรา 81/1"
for _t in S['taxes']:
    if _t['oecd'] == '5111':
        _t['statute'] = "Revenue Code ss. 80, 81 (1), 81/1; Royal Decrees Nos. 790 (B.E. 2567) and 799 (B.E. 2568) on the VAT rate reduction"
        _t['dated'] = ("2025: decree No. 790 (6.3 % to 30 Sep 2025) and No. 799 (6.3 % from 1 Oct 2025 to 30 Sep 2026), Royal Gazette texts "
                       "on rd.go.th: the same rate all year (no split); session 12 year in force")
        _t['unsupported'] = ["local-government VAT share (1/9, 0.7 %) and the small-business decree (1.8 M baht) not read"]
