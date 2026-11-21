import TaxKernel.World

/-!
# Saudi Arabia 2025: wages are not "activity" under the Income Tax Law; GOSI annuities for Saudi employees

Sources (Bureau of Experts, laws.boe.gov.sa: the site refuses connections from both our hosts; the pages were read in
their Internet Archive copies, the route Global law itself uses for the Saudi corpus; `sa/law/`):
* Income Tax Law (Royal Decree M/1 of 15/1/1425 H; BOE page 23576008-…, archived 2024-02-21):
  art. 1 "النشاط : النشاط التجاري بكل صوره أو المهني أو الحرفي أو أي نشاط آخر مشابه ، يقصد منه تحقيق الربح ويشمل
  استخدام المال المنقول وغير المنقول"; art. 2 persons subject to tax: "(ب) الشخص الطبيعي المقيم غير السعودي الذي
  يمارس النشاط في المملكة" (and companies, non-residents, gas and oil). Employment for a wage is not "activity", and
  a Saudi natural person is not a person subject to tax: no tax on wages. A non-Saudi's professional or rental
  activity is taxable (not modelled: `unsupported`).
* Social Insurance Law (Royal Decree M/33 of 3/9/1421 H; BOE page 8ff3cd90-…, archived 2024-04-23):
  art. 4(2) the annuities branch applies compulsorily "على جميع العُمال السعوديين"; art. 18(2)(a) annuities 18 %,
  "يدفع صاحِب العمل (9%) تسعة في المائة، و (9%) تسعة في المائة يدفعُها المُشترِك"; art. 19(1)(b) "يكون الحد الأعلى
  للأجر الخاضِع للاشتِراك (45.000) خمسة وأربعين ألف ريال شهرياً"; art. 18(1) occupational hazards 2 % paid by the
  employer (all workers).
* Unemployment Insurance Law (SANED; BOE page c331efa7-…, archived 2024-05-24): art. 7 as amended by Royal Decree
  M/160 of 11/11/1441 H: the rate is set "بقرار من مجلس الشؤون الاقتصادية والتنمية ... بنسبة لا تزيد على (2%) ... ولا
  تقل عن (0.5%)", half paid by the insured. The CEDA decision itself was not reached (BOE refuses both hosts); W5 pattern A
  (2026-11-20) takes the rate in force from GOSI, the insurer (official secondary): GOSI SANED guide (PDF of 5 June
  2023, gosi.gov.sa/GOSIOnline/saned_2023, `sa/law/w5/`), "كم هي نسبة الاشتراك في ساند؟ ... 0.75 % من المشترك ... 0.75 %
  من صاحب العمل". SANED covers Saudi workers; its contribution wage is the Social Insurance Law's (art. 19 (1)(b)
  ceiling 45,000 a month). Not deductible from anything (no tax on wages). Input `"w5Contrib": false` drops it.
* Zakat: the Zakat Collection Law (BOE page 25fed59a-…) was located but not read; no provision levying zakat on wages
  was found (FINDINGS).

Model: a Saudi employee insured under the 1421 H law (registered before the later law for new entrants, which was not
found in the accessible archive: `"saInsuredFrom": "new"` → `unsupported`). Contract wage = contribution wage
(basic wage plus housing allowance per the regulations). Non-Saudis: no employee contribution.
-/

namespace SaTax
open TaxKernel

def nationality (c : Canon) : String := (c.str? "nationality").getD "national"

def ceiling : Int := 45000 * 12
def annuities : Contribution := Contribution.flatCapped "annuities" 900 ceiling   -- art. 18(2)(a), 19(1)(b)

/-- Unemployment Insurance Law art. 7 (M/160) with the rate GOSI publishes: employee 0.75 % (75 bp), on the SIL
contribution wage capped at 45,000 a month. -/
def saned : Contribution := Contribution.flatCapped "SANED" 75 ceiling

#guard saned.amount 120000 = 900      -- 10,000 a month: 75 a month
#guard saned.amount 600000 = 4050     -- capped at 45,000 a month: 337.50 a month

def out (c : Canon) : Out :=
  let w5 := (c.bool? "w5Contrib").getD true
  let nat := nationality c
  let newLaw := c.str? "saInsuredFrom" = some "new"
  let ann := if nat = "national" ∧ ¬ newLaw then sumInts (c.adults.map fun a => annuities.amount a.wages) else 0
  let san := if w5 ∧ nat = "national" then sumInts (c.adults.map fun a => saned.amount a.wages) else 0
  let wageEarners := c.adults.any (fun a => a.wages > 0)
  let se := c.adults.any (fun a => a.selfEmployment > 0)
  let uns :=
    (if nat = "national" ∧ wageEarners ∧ ¬ w5 then
      ["SANED unemployment insurance switched off (w5Contrib = false)"] else [])
    ++ (if newLaw ∧ nat = "national" then ["insured under the later social insurance law for new entrants: text not accessible, not modelled"] else [])
    ++ (if nat ≠ "national" ∧ (se ∨ c.rentalIncome > 0) then
      ["non-Saudi resident's activity (professional, rental) is taxable under Income Tax Law art. 2(b): not modelled"] else [])
    ++ (if nat = "gcc" then ["GCC national: annuities follow the home state's law, not modelled"] else [])
  Out.make c "SA" "SAR" 0 (employeeSocial := ann + san)
    (detail := [Out.d "annuities" ann, Out.d "saned" san, Out.dStr "nationality" nat,
      Out.dStr "note" "no tax on wages: Income Tax Law art. 1-2 (activity = trade/profession for profit; Saudi natural persons not subject); SIL 1421 art. 18-19: 9 % up to 45,000 a month; SANED 0.75 % (UI Law art. 7, GOSI rate)"])
    (unsupported := uns)

def country : Country :=
  { code := "SA", name := "Saudi Arabia (Saudi employee, 1421 H Social Insurance Law)", currency := "SAR",
    year := "2025", compute := out }

end SaTax
