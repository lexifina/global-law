import TaxKernel.World

/-!
# Qatar 2025: wages are outside the Income Tax Law; social insurance contributions of Qatari employees

Sources (Ministry of Justice legislation API, api.moj.gov.qa, the link Global law gives for the Qatar corpus; Al
Meezan; read 2026-11-20; `qa/law/`):
* Law No. 24 of 2018 promulgating the Income Tax Law (`law-2018-24_income_tax.txt`):
  - issuing art. 2 (as amended, published 2022-12-22): the Income Tax Law does not apply to "3- الرواتب والأجور
    والبدلات وما في حكمها";
  - law art. 4 (as amended): exempt "2- الفوائد والعوائد المصرفية المستحقة للأشخاص الطبيعيين"; "4- الأرباح الرأسمالية
    ... التي يحققها أشخاص طبيعيون" (not assets of a taxable activity); "12- الدخل الإجمالي للأشخاص الطبيعيين القطريين
    المقيمين في الدولة"; art. 3(3) income from real estate in the State is State-source income.
  So a non-Qatari's rental income and business income are taxable (rate and computation not read: `unsupported`).
* Law No. 1 of 2022 promulgating the Social Insurance Law (`law-2022-1_social_insurance.txt`; Official Gazette
  No. 7 of 2022, in force six months after publication):
  - art. 1 insured: "كل قطري موظف في القطاع الحكومي أو عامل في القطاع الخاص"; art. 2-3: Qataris aged 18 or more in
    regular permanent employment;
  - art. 11: "يُحسب الاشتراك ... على أساس راتب حساب الاشتراك بما لا يزيد على (100,000) مائة ألف ريال" and
    "1- (7%) سبعة في المائة، تُستقطع من راتب حساب الاشتراك من المؤمّن عليه";
  - art. 12: the housing allowance counts up to 6,000 a month (the contract has no allowance split).
* Cabinet Decision No. 3 of 2025, executive regulations (Global law `qatar/national/acts/cabinet-decision-2025-3`,
  as in force 2025-07-01), art. 16(1): "الحد الأقصى لراتب حساب الاشتراك، (100,000) مائة ألف ريال شهرياً".

Mapping: each adult's wages are the contribution salary (basic + social allowance + housing allowance).
`"nationality"`: `national` (Qatari, default), `expatriate`, `gcc` (GCC nationals: home state's law, `unsupported`).
-/

namespace QaTax
open TaxKernel

def nationality (c : Canon) : String := (c.str? "nationality").getD "national"

def ceiling : Int := 100000 * 12
def pension : Contribution := Contribution.flatCapped "socialInsurance" 700 ceiling   -- art. 11

def personSI (a : Adult) : Int := if a.age < 18 then 0 else pension.amount a.wages

def out (c : Canon) : Out :=
  let nat := nationality c
  let si := if nat = "national" then sumInts (c.adults.map personSI) else 0
  let se := c.adults.any (fun a => a.selfEmployment > 0)
  let uns :=
    (if nat ≠ "national" ∧ (se ∨ c.rentalIncome > 0) then
      ["non-Qatari business or real-estate income is within the Income Tax Law (Law 24/2018 art. 3; art. 4(12) exempts Qataris only): not modelled"] else [])
    ++ (if nat = "gcc" then ["GCC national: social insurance follows the home state's law (Law 4/2007), not modelled"] else [])
  Out.make c "QA" "QAR" 0 (employeeSocial := si)
    (detail := [Out.d "socialInsurance" si, Out.dStr "nationality" nat,
      Out.dStr "note" "wages outside the Income Tax Law (Law 24/2018 issuing art. 2(3)); Law 1/2022 art. 11: 7 % up to 100,000 a month (Qataris)"])
    (unsupported := uns)

def country : Country :=
  { code := "QA", name := "Qatar (Qatari employee)", currency := "QAR", year := "2025", compute := out }

end QaTax
