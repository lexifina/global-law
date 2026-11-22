import VnGlobal.Pit
import TaxKernel.Global2

/-!
# Vietnam 2025: value added tax (5111); special consumption tax and environmental protection tax (5121, session 9)

Source: Law on VAT No. 48/2024/QH15 (in force 1 July 2025), official consolidated text No. 12/VBHN-VPQH of 06/02/2026
(datafiles.chinhphu.vn, via a second machine route; `vn/law/vat/vbhn12_2026_law48.pdf`, sha256 in `SHA256SUMS`). The
consolidation marks each later amendment with its effective date; provisions changed by Law 149/2025/QH15 from
2026-01-01 are not used.
* **Điều 9 khoản 2**: 5 % on a) clean water, d) unprocessed crop and livestock products, h) medicines and medical devices,
  l) books (other than those of Điều 5 khoản 15); **khoản 3**: 10 % on everything else.
* **Footnote 5 (Nghị quyết số 204/2025/QH15, from 1 July 2025 to 31 December 2026)**: "Giảm 2% thuế suất … khoản 3
  Điều 9 … (còn 8%), trừ … viễn thông, hoạt động tài chính, ngân hàng, chứng khoán, bảo hiểm, kinh doanh bất động sản,
  sản phẩm kim loại, sản phẩm khai khoáng (trừ than), … hàng hóa và dịch vụ chịu thuế tiêu thụ đặc biệt (trừ xăng)".
* **Điều 5** not subject to VAT: 8. life and health insurance, 9. credit services, 10. medical services, 13. teaching.
First half of 2025: the 2008 VAT Law and Resolution 174/2024/QH15 applied; they were not read, and the second-half rules
are applied to the whole year (flagged per entity).
-/

namespace VnGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Thuế giá trị gia tăng", standard := 1000, reduced := 500, reduced2 := 800,
    classOf := fun gd => match gd with
      | .water | .medicines | .books | .newspapers => .reduced
      | .food | .nonAlcoholic | .clothing | .electricity | .gas | .petrol | .diesel | .heatingOil | .transport | .recreation | .restaurants | .hotels | .rent | .other => .reduced2
      | .education | .health | .financial | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "Luật Thuế GTGT 48/2024/QH15 Điều 5, Điều 9 khoản 2-3; Nghị quyết 204/2025/QH15 (8 % from 1 July 2025)"

def vatH1 : Vat := { vat with name := "Thuế giá trị gia tăng (đến 30/6/2025)" }

def vatStatuteH1 : String := "Luật Thuế GTGT 13/2008/QH12 (as amended); Nghị quyết 174/2024/QH15, Nghị định 180/2024/NĐ-CP (8 % from 1 January to 30 June 2025): the second-half classes applied (B, first-half texts not read)"

/-- Kernel 2.1 `DatedVat`: Law 13/2008 with Resolution 174/2024 to 30 June 2025, Law 48/2024 with Resolution 204/2025 from
1 July 2025. Hand-edited: do not regenerate from `tools/specs/VN_cons.py`. -/
def vnVat : DatedVat :=
  { periods := [{ vat := vatH1, statute := vatStatuteH1 }, { start := "2025-07-01", vat := vat, statute := vatStatute }] }

/-! ## R3 session 9: SCT and EPT (5121), grade A
**Thuế tiêu thụ đặc biệt**: Luật 27/2008/QH12 as amended by Laws 70/2014, 71/2014, 106/2016, 03/2022 (official consolidation
**08/VBHN-VPQH**, Công báo 931+932 of 21-12-2022, congbao.chinhphu.vn; `vn/law/sct/vn_vbhn08_2022_sct.pdf`); in force to
31 Dec 2025 (Law 66/2025/QH15 from 1 Jan 2026, consolidation 111/VBHN-VPQH of 2026). **Điều 6**: the base is the selling
price before SCT, environmental protection tax and VAT; **Điều 7** (Biểu thuế, rates in force from 2018/2019): I.1
cigarettes 75 %, I.2 a) spirits from 20° 65 %, b) below 20° 35 %, I.3 beer 65 %, I.8 a) petrol 10 %, b) E5 8 %, c) E10 7 %.
**Thuế bảo vệ môi trường**: Law 57/2010/QH12; **Nghị quyết 60/2024/UBTVQH15** (Công báo 41+42 of 11-01-2025) Điều 1 khoản 1:
from 1 Jan to 31 Dec 2025 petrol except ethanol 2 000 đồng/lít, diesel 1 000 đồng/lít (Nghị quyết 109/2025/UBTVQH15 sets
2026 and repeals it from 1 Jan 2026). Kernel `.beforeTax` base: the basket price net of VAT, less the EPT (as the rule's
specific part), divided by (1 + SCT rate); the SCT charge books only the ad valorem part, the EPT is its own charge.
Flagged: the statute's base is the producer's or importer's price (Điều 6 khoản 1-2), here read from the retail price;
EPT on E5/E10 on the petrol share at the nominal 95 % / 90 %. -/

def sctStatute : String := "Luật Thuế tiêu thụ đặc biệt 27/2008/QH12 (VBHN 08/VBHN-VPQH 2022) Điều 6, Điều 7 Biểu thuế "

def sctRule (g : Good) (sub nm st : String) (bp ept : Int) (minAbv : Int := -1) (maxAbv : Int := 100000) : ExciseRule :=
  ({ good := g, sub := sub, name := nm, adValoremBp := bp, valueBase := .beforeTax, perUnitNum := ept, perUnitDen := 1,
     minAbvBp := minAbv, maxAbvBp := maxAbv, statute := sctStatute ++ st } : ExciseRule).withVat vat

def sctRules : List ExciseRule :=
  [sctRule .petrol "e5" "Thuế tiêu thụ đặc biệt (xăng E5)" "I.8 b): 8 %" 800 1900,
   sctRule .petrol "e10" "Thuế tiêu thụ đặc biệt (xăng E10)" "I.8 c): 7 %" 700 1800,
   sctRule .petrol "" "Thuế tiêu thụ đặc biệt (xăng)" "I.8 a): 10 %" 1000 2000,
   sctRule .cigarettes "" "Thuế tiêu thụ đặc biệt (thuốc lá điếu)" "I.1 (từ 01/01/2019): 75 %" 7500 0,
   sctRule .beer "" "Thuế tiêu thụ đặc biệt (bia)" "I.3 (từ 01/01/2018): 65 %" 6500 0,
   sctRule .spirits "" "Thuế tiêu thụ đặc biệt (rượu dưới 20 độ)" "I.2 b) (từ 01/01/2018): 35 %" 3500 0 0 1999,
   sctRule .spirits "" "Thuế tiêu thụ đặc biệt (rượu từ 20 độ)" "I.2 a) (từ 01/01/2018): 65 %" 6500 0,
   sctRule .wine "" "Thuế tiêu thụ đặc biệt (rượu từ 20 độ)" "I.2 a) (từ 01/01/2018): 65 %" 6500 0 1999,
   sctRule .wine "" "Thuế tiêu thụ đặc biệt (rượu dưới 20 độ)" "I.2 b) (từ 01/01/2018): 35 %" 3500 0]

/-- The SCT part of a rule only: the EPT in the rule lowers the base (Điều 6) and is charged by `eptRules`. -/
def sctCharge (e : ExciseRule) (year : Nat) (s : Spend) (x : SpendX) : Charge :=
  let sx := e.scaled year s x
  charge .excise e.name sx.1.amount (fun _ => e.value sx.1 sx.2) (fun _ => e.adValorem sx.1 sx.2)
    (event := if x.sub == "" then s.good.name else x.sub) (bearer := .consumer) (statute := e.statute)

def sctCharges (g : CanonGlobal) : List Charge :=
  (consumptionX g).flatMap fun (s, x) => ((sctRules.filter (·.appliesTo g.year s x)).take 1).map (sctCharge · g.year s x)

def eptStatute : String := "Luật Thuế bảo vệ môi trường 57/2010/QH12; Nghị quyết 60/2024/UBTVQH15 Điều 1 khoản 1 (01/01/2025-31/12/2025): "

def eptRules : List ExciseRule :=
  [{ good := .petrol, sub := "e5", name := "Thuế bảo vệ môi trường (xăng E5)", perUnitNum := 1900, statute := eptStatute ++ "xăng, trừ etanol 2.000 đồng/lít on the 95 % petrol share" },
   { good := .petrol, sub := "e10", name := "Thuế bảo vệ môi trường (xăng E10)", perUnitNum := 1800, statute := eptStatute ++ "xăng, trừ etanol 2.000 đồng/lít on the 90 % petrol share" },
   { good := .petrol, name := "Thuế bảo vệ môi trường (xăng)", perUnitNum := 2000, statute := eptStatute ++ "xăng, trừ etanol 2.000 đồng/lít" },
   { good := .diesel, name := "Thuế bảo vệ môi trường (dầu diesel)", perUnitNum := 1000, statute := eptStatute ++ "dầu diesel 1.000 đồng/lít" },
   { good := .heatingOil, name := "Thuế bảo vệ môi trường (dầu hỏa)", perUnitNum := 600, statute := eptStatute ++ "dầu hỏa 600 đồng/lít" }]

def vnExciseCharges (g : CanonGlobal) : List Charge := sctCharges g ++ exciseRuleCharges eptRules g (firstOnly := true)

def families : List Family := [vnVat.family "Thuế giá trị gia tăng (two periods)",
  { name := "5121 Thuế tiêu thụ đặc biệt; thuế bảo vệ môi trường", covers := [.excise], run := fun _ g _ => vnExciseCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["VN 5111: Law 48/2024/QH15 (consolidation 12/VBHN-VPQH) with Resolution 204/2025/QH15; second-half-2025 rules", "VN 5121: SCT Law 27/2008/QH12 (08/VBHN-VPQH) Điều 6-7; EPT Resolution 60/2024/UBTVQH15 (2025)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty then ["first half of 2025 (VAT Law 13/2008 with Resolution 174/2024/QH15): its own period, with the second-half classes (texts not read)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel) then ["special consumption tax read on the retail price net of VAT and EPT (Điều 6: the producer's or importer's selling price); cut tobacco and cigars, cars and other SCT goods not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food) then ["food taken at the reduced 8 % (processed food); unprocessed produce is 5 % (Điều 9 khoản 2 d)"] else [])

#guard vat.embedded { good := .clothing, amount := 10800 } == 800
#guard vat.embedded { good := .beer, amount := 11000 } == 1000
#guard vat.embedded { good := .water, amount := 10500 } == 500
#guard vat.embedded { good := .health, amount := 10500 } == 0

#guard (vnVat.vatOn 2025 "2025-03-01").map (·.reduced2) == some 800
#guard ((sctRules.find? (fun e => e.good == .petrol && e.sub == "")).map (fun e => e.adValorem { good := .petrol, amount := 2100000, quantity := 100000 } {})) == some 158585
#guard ((sctRules.find? (fun e => e.good == .beer)).map (fun e => e.adValorem { good := .beer, amount := 50000, quantity := 1000 } {})) == some 17905
#guard ((eptRules.find? (fun e => e.good == .diesel)).map (fun e => e.dutyOn { good := .diesel, amount := 1000000, quantity := 50000 } {})) == some 50000

end VnGlobal.Consumption
