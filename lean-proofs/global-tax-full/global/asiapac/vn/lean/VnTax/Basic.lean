import TaxKernel.World

/-!
# Viet Nam: personal income tax of resident employees, 2025, and compulsory social insurance

Access tier B. The statute text is the National Assembly Office's consolidated Law on Personal Income Tax
(Văn bản hợp nhất số 103/VBHN-VPQH, 27/08/2025, Official Gazette (Công báo) No. 1283 + 1284 of 11-9-2025;
`vn/law/van-ban-hop-nhat-so-103-vbhn-vpqh-46034.pdf`, sha256 in SHA256SUMS; vbpl.vn answers 403 to scripts and the PIT
law is not in Global law). It consolidates Law 04/2007/QH12 as amended by Laws 26/2012/QH13 and 71/2014/QH13 (and
2024 land laws). Provisions used:
* art. 22 (2) "Biểu thuế lũy tiến từng phần": annual taxable income to 60 million 5 %; 60-120 10 %; 120-216 15 %;
  216-384 20 %; 384-624 25 %; 624-960 30 %; above 960 35 % (monthly: 5 / 10 / 18 / 32 / 52 / 80 million).
* art. 21 (1): taxable income from wages = taxable income less compulsory social, health and unemployment insurance
  contributions and the deductions of arts. 19-20.
* art. 19 (1) (as amended by Law 26/2012 art. 1 (4)): "Mức giảm trừ đối với đối tượng nộp thuế là 9 triệu đồng/tháng
  (108 triệu đồng/năm)"; "mỗi người phụ thuộc là 3,6 triệu đồng/tháng"; when the CPI moves by more than 20 % the
  Standing Committee adjusts these amounts "để áp dụng cho kỳ tính thuế tiếp theo". art. 19 (3) a): dependants include
  minor children; each dependant counted for one taxpayer only.
* art. 4 (7): bank deposit interest exempt; art. 4 (10): pensions paid by the Social Insurance Fund exempt;
  art. 23: dividends ("đầu tư vốn") 5 % flat.
* Law on Social Insurance 41/2024/QH15 art. 33 (1) a) (Global law, in force 2025-07-01): employee "8% tiền lương làm
  căn cứ đóng bảo hiểm xã hội bắt buộc"; art. 31 (1) đ): base capped at 20 x the reference amount.
Not reached: the Standing Committee resolution that adjusted the art. 19 amounts under its CPI clause (not in the
Official Gazette's Standing Committee listing, nor in Global law), the reference amount for the contribution ceiling,
and the health and unemployment insurance rates (their laws were not read): the model uses the statute's
printed 9 / 3.6 million and an uncapped 8 %, and says so in `unsupported` on every wage line.
W5 pattern A (2026-11-20): default social-insurance ceiling = 20 x the reference amount 2,340,000 = 46,800,000 a
month (input `vnSiBaseCapMonthly` still wins; `"w5Contrib": false` restores the uncapped default). Nghị định
73/2024/NĐ-CP (30/6/2024; Government copy datafiles.chinhphu.vn/cpp/files/vbpq/2024/7/73-cp.signed.pdf, image PDF read
page by page, `vn/law/w5/`) Điều 3 khoản 2: "Từ ngày 01 tháng 7 năm 2024, mức lương cơ sở là 2.340.000 đồng/tháng" (no
later change for 2025 was found); Law 41/2024 art. 31 (1) đ) (20 x). The ceiling of Law 58/2014 for January-June 2025
was not re-read (taken as the same 20 x). BHYT (Decree 146/2018 not reached on an official host) and BHTN (Law on
Employment 38/2013 art. 57 not reached) are still not modelled.
Unit: individual; dependants claimed by the higher earner.
-/

namespace VnTax
open TaxKernel

def sched : Schedule := Schedule.ofList [(0, 500), (60000000, 1000), (120000000, 1500), (216000000, 2000),
  (384000000, 2500), (624000000, 3000), (960000000, 3500)]

/- The monthly column is the annual column / 12. -/
#guard [60000000, 120000000, 216000000, 384000000, 624000000, 960000000].all fun t => t % 12 = 0

def selfDeduction : Int := 108000000
def dependantDeduction : Int := 12 * 3600000
def siRate : Int := 800
def dividendRate : Int := 500

def si (wages : Int) : Int := divR .down (siRate * pos wages) BP

/-- Art. 19 (1) last paragraph: when the CPI moves by more than 20 % "Ủy ban thường vụ Quốc hội điều chỉnh mức giảm
trừ gia cảnh". The Standing Committee's resolution in force for 2025 was not reached in an official text (vbpl.vn is
script-rendered; Global law holds laws only), so its amounts are optional inputs: `vnSelfDeductionMonthly` and
`vnDependantDeductionMonthly` (VND a month; default the printed 9 / 3.6 million). Law 41/2024 art. 31 (1) đ) caps the
social-insurance base at 20 x the reference amount: optional input `vnSiBaseCapMonthly` (VND a month; default none). -/
structure Params where
  selfMonthly : Int := 9000000
  depMonthly : Int := 3600000
  siCapMonthly : Option Int := none

def siWith (p : Params) (wages : Int) : Int :=
  match p.siCapMonthly with
  | some cap => perPeriod 12 (fun m => divR .down (siRate * min (pos m) cap) BP) wages
  | none => si wages

#guard siWith {} 120000000 = 9600000
#guard siWith { siCapMonthly := some 46800000 } 1200000000 = 12 * 3744000

/-- W5 pattern A: Nghị định 73/2024/NĐ-CP Điều 3 (2): mức lương cơ sở from 1 July 2024. -/
def luongCoSo : Int := 2340000
#guard siWith { siCapMonthly := some (20 * luongCoSo) } 1200000000 = 12 * 3744000

def out (c : Canon) : Out :=
  let idx := List.range c.adults.length
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let top : Nat := match c.adults with
    | [a0, a1] => if a1.wages > a0.wages then 1 else 0
    | _ => 0
  let p : Params := { selfMonthly := (c.int? "vnSelfDeductionMonthly").getD 9000000,
                      depMonthly := (c.int? "vnDependantDeductionMonthly").getD 3600000,
                      siCapMonthly := match c.int? "vnSiBaseCapMonthly" with
                        | some x => some x
                        | none => if (c.bool? "w5Contrib").getD true then some (20 * luongCoSo) else none }
  let rs := (c.adults.zip idx).map fun (a, i) =>
    let deps : Int := if i = top then (c.childrenUnder 18 : Nat) else 0
    let ti := pos (pos a.wages - siWith p a.wages - 12 * p.selfMonthly - 12 * p.depMonthly * deps)
    (sched.tax Rule.unitDown ti, ti)
  let divTax := sumInts (idx.map fun i => divR .down (dividendRate * pos (share c.dividends i)) BP)
  Out.make c "VN" "VND" (sumInts (rs.map (·.1))) (surtaxes := [("dividendTax", divTax)])
    (employeeSocial := sumInts (c.adults.map fun a => siWith p a.wages))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.2))),
      Out.dStr "note" "bank interest and Social-Insurance-Fund pensions exempt (art. 4 (7), (10))"])
    (unsupported := (if c.adults.any (fun a => a.wages > 0) then ["family deductions: the Standing Committee's CPI adjustment (art. 19 (1)) not reached in an official text; statute's printed 9 / 3.6 million used unless vnSelfDeductionMonthly / vnDependantDeductionMonthly are given",
        "health and unemployment insurance contributions not modelled (rates by decree / Law on Employment, not read); the 20 x reference-amount ceiling on social insurance needs vnSiBaseCapMonthly"] else []) ++
      (if c.adults.any (fun a => a.selfEmployment ≠ 0) then ["business income of individuals: presumptive (turnover-based) regime not modelled"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rent: turnover-based tax not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: 0.1 % of proceeds (securities) / 2 % (real estate) need the price"] else []))

def country : Country := { code := "VN", name := "Viet Nam", currency := "VND", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end VnTax
