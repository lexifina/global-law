import TaxKernel.World

/-!
# Lebanon: tax on salaries and wages (Decree-Law 144 of 12 June 1959, Title II), 2025

Sources:
* The Ministry of Finance's consolidated Income Tax Law (`finance.gov.lb/en-us/Taxation/LRT/Documents/قانون ضريبة الدخل.pdf`,
  2014 export, sha256 d33fc606841…): arts. 47-59 (structure); art. 50: pension deductions ("المبالغ المحسومة والمدفوعة
  للتقاعد") are deducted; art. 57: an employee who also has Title I income "لا يستفيد الا من التنزيل المنصوص عليه في
  الباب الاول". **Art. 56 is defective in that copy**: "بعد ان ينزل منها لكل شخص من المكلفين إذا كان حاملا لبطاقة المعوق"
  (the deduction itself is missing; FINDINGS F3).
* **Law No. 324 of 12 February 2024 (General Budget 2024)**, the MoF's PDF (`finance.gov.lb/en-us/Finance/BI/ABDP/Documents/Budget 2024.pdf`,
  sha256 732e76670… ; text layer partly broken, read by Arabic OCR and page images):
  art. 47 rewrites art. 58: 2 % up to 360,000,000 LBP; 4 % to 900,000,000; 7 % to 1,800,000,000; 11 % to 3,600,000,000;
  15 % to 7,200,000,000; 20 % to 13,500,000,000; 25 % above;
  art. 49 rewrites art. 31 (Title I family deduction): "مبلغ /450,000,000/ ل.ل." for each natural person, plus
  "/225,000,000/" for a married taxpayer and "/45,000,000/" per dependent child (at most five); when both spouses work
  each takes the single deduction and the children's deduction is shared equally; a wife whose husband does not work
  takes the husband's and the children's deductions.
* The salary deduction is taken to be the art. 31 deduction (art. 57 and the defective art. 56: reading, FINDINGS).
* 2025: the 2025 budget (Official Gazette supplement 11 of March 2025; MoF PDF `Budget 2025.pdf`, outlined text, read by
  OCR, pages 1-40) amends in the Income Tax Law only art. 53 para. 1 (its art. 17: quarterly withholding; pay in
  foreign currency converted at the Banque du Liban rate at each month end); arts. 31 and 58 keep the 2024 wording
  (access B: OCR, and the budget articles past page 40 not read).
Not modelled: NSSF employee contributions; Title I and Title III income. Unit: individual.
-/

namespace LbTax
open TaxKernel

/-- Art. 58 as rewritten by Law 324/2024 art. 47 (bp). -/
def sched : Schedule :=
  Schedule.ofList [(0, 200), (360000000, 400), (900000000, 700), (1800000000, 1100), (3600000000, 1500),
    (7200000000, 2000), (13500000000, 2500)]

def single : Int := 450000000
def married : Int := 225000000
def perChild : Int := 45000000

def taxOn (ti : Int) : Int := sched.tax Rule.unitDown (pos ti)

def out (c : Canon) : Out :=
  let kids := min (c.childrenUnder 18) 5
  let a1 := c.adult1
  let w1 := pos a1.wages
  let (d1, d2, w2) := match c.adult2? with
    | some a2 =>
      let w2 := pos a2.wages
      if w1 > 0 && w2 > 0 then
        (single + perChild * kids / 2, single + perChild * kids - perChild * kids / 2, w2)
      else if w1 > 0 then (single + (if c.married then married else 0) + perChild * kids, 0, 0)
      else (0, single + (if c.married then married else 0) + perChild * kids, w2)
    | none => (single + perChild * kids, 0, 0)
  let t := taxOn (w1 - d1) + taxOn (w2 - d2)
  Out.make c "LB" "LBP" t
    (detail := [Out.d "taxableIncome" (pos (w1 - d1) + pos (w2 - d2)), Out.d "familyDeduction" (d1 + d2)])
    (unsupported := ["NSSF employee contributions and pension deductions (art. 50) not modelled",
      "Title I (profits), Title III (capital income) and rents not modelled",
      "salary family deduction read as the art. 31 deduction (art. 56 defective in the MoF copy)",
      "2025 budget (art. 17 amends art. 53 only, OCR pages 1-40): no change to arts. 31/58 found"])

def country : Country :=
  { code := "LB", name := "Lebanon (Decree-Law 144/1959, salaries; Budget Law 324/2024)", currency := "LBP", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard taxOn 360000000 = 7200000 ∧ taxOn 900000000 = 28800000 ∧ taxOn 13500000000 = 2089800000

end LbTax
