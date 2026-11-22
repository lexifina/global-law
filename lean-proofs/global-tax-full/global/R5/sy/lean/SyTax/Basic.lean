import TaxKernel.World2

/-!
# Syria: tax on wages and salaries (ضريبة الرواتب والأجور), 2025

Access tier B (rescue pass 3). Law as of 1 September 2023 (Legislative Decree 30/2023) with the minimum exempt amount
of 2025 taken from the Minister of Finance's statements (official secondary). A new income-tax law for 2026 was
announced in 2025 (SANA, 16 July and 6 September 2025); it is not this year's law.

Texts read:
* Law No. 24 of 2003 on Income Tax (parliament.gov.sy text, WIPO Lex details/20751, `sy/law/rescue3/sy025ar.pdf`):
  art. 66 (who is taxed), art. 67 (exemptions: (ب) the armed forces, internal security and firemen; (هـ) "معاشات
  التقاعد ... وتعويضات التسريح" pensions and end-of-service pay), art. 70 (net income = gross less "(1) قيمة
  الاشتراكات المقتطعة من رواتب وأجور العاملين لقاء الاشتراك في نظام التأمينات الاجتماعية", (2) expense
  allowances, (3) representation allowances), art. 71 (part months), art. 73 ("المكلف الذي تتناوله أحكام الأبواب
  الأول ... والرابع ... لا يستفيد من الحد الأدنى المعفى إلا مرة واحدة ويمكنه اختيار الحد الأكثر ملاءمة له").
* Executive Instructions of Law 24/2003 (Ministry of Finance; WIPO Lex details/20767, `sy029ar.pdf`), on arts. 68-69:
  the exempt minimum "ينزل من الشريحة الأولى" (is deducted from the first band) and the worked examples: a monthly
  wage of 10,000 pays 290 (not insured) or 241 → 250 (insured: "حسم التأمينات الاجتماعية بواقع /7%/ من راتبه
  الشهري"); 40,000 pays 4,530 (not insured) or 3,970 (insured). The bands are measured on the whole net monthly
  income; the exempt minimum takes the first lira of it. Checked below with `#guard` on the 2003 table.
* Legislative Decree No. 24 of 2020 (WIPO Lex details/20783, `sy030ar.pdf`): arts. 68-69 as of 1 November 2020
  (4-18 %, exempt 50,000 a month). Superseded.
* **Legislative Decree No. 30 of 2023** (Damascus, 28 August 2023), text as published by the Ministry of
  Agriculture and Agrarian Reform (moaar.gov.sy attachment DOC-20230828-WA0025-TqMkQ3.pdf, Internet Archive capture
  20260513013715, sha256 7db503f7…; `sy/law/rescue3/ld30_2023_moaar.pdf`):
  - art. 19 (new art. 68): "أ. يحدد معدل الضريبة على دخل الرواتب والأجور بما في ذلك إضافات الدفاع الوطني ورسوم
    المدارس وحصة البلدية والمساهمة النقدية في دعم التنمية المستدامة على النحو الآتي: 5% ... بين الحد الأدنى المعفى
    و/250,000/ ل.س؛ 7% ... بين 250,001 و450,000؛ 9% ... بين 450,001 و650,000؛ 11% ... بين 650,001 و850,000؛
    13% ... بين 850,001 و1,100,000؛ 15% ... الذي يتجاوز /1,100,000/ ل.س. ب. ... بنسبة 5% عن كل دفعة مقطوعة."
  - art. 20 (new art. 69): "ينزل من الدخل الصافي الشهري حد أدنى معفى من الضريبة يعادل الحد الأدنى العام للأجور
    المحدد للعاملين بالقطاع العام."
  - art. 4 (new art. 16(a)): business profits of natural persons 10 % to 10,000,000, 14 % to 30,000,000, 18 % to
    100,000,000, 22 % to 500,000,000, 25 % above; art. 8 (new art. 20(a)): 3,000,000 a year exempt; art. 29(a): from
    the 2024 accounts.
  - art. 17(b): taxes are rounded "إلى الـ /100/ ل.س المئة ليرة سورية الأعلى" (up to the next 100).
  - art. 29(b): arts. 19-21 apply from the first month after issue (September 2023).
* The 2025 minimum exempt amount (= the public-sector general minimum wage, art. 69 as amended), official secondary:
  SANA, 20 July 2025 (sana.sy/economy/2257453): the Minister of Finance "أصدر ... تعميماً حدد بموجبه الحد الأدنى
  المعفى من ضريبة الدخل على الرواتب والأجور، بعد الزيادة الأخيرة عليها، بمبلغ وقدره 837 ألف ليرة" and "تم رفع
  الحد الأدنى ... من 279 ألف ليرة سورية إلى 837 ألف ليرة سورية", for the salaries paid to the end of 2025. The
  increase is Decree 102 of 19 June 2025 (200 % on public pay; SANA 6 July 2025, sana.sy/locals/2249611), applied
  from July 2025 (SANA 23 June 2025, sana.sy/locals/2235824). The circular itself and the 2024 decree fixing the
  279,000 minimum wage were not reached (279,000 is the Minister's rounded figure).

Household mapping (one year = 12 equal monthly payments of `wages / 12`, first `wages % 12` months one lira more):
January-June at the 279,000 exempt minimum, July-December at 837,000. Each adult is taxed alone (the tax has no
family relief). Employee social insurance: 7 % of the monthly wage, from the Ministry's worked examples (dated with the
2003 instructions; the 2025 rate in the social-insurance law was not reached), deducted under art. 70; whole liras
down. Pensions are exempt (art. 67(هـ)). `selfEmployment` = annual net profit of a natural person taxed on real
profits (art. 16(a)), with the art. 20 exempt minimum; art. 73: one exempt minimum only, the cheaper choice.
Dividends, interest (tax on movable capital income), rents and lump-sum payments are not modelled.
-/

namespace SyTax
open TaxKernel

/-- LD 30/2023 art. 19 (Law 24/2003 art. 68(a)), monthly SYP. The first band starts at 0: the exempt minimum is
taken off the bottom (Executive Instructions on art. 69: "ينزل من الشريحة الأولى"). -/
def wageSched : Schedule := Schedule.ofList
  [(0, 500), (250000, 700), (450000, 900), (650000, 1100), (850000, 1300), (1100000, 1500)]

/-- Art. 69 as amended by LD 30/2023 art. 20 = the public-sector minimum wage: 279,000 to June 2025, 837,000 from July
2025 (Minister of Finance, SANA 20 July 2025; official secondary). -/
def exemptH1 : Int := 279000
def exemptH2 : Int := 837000
def exemptOfMonth (i : Nat) : Int := if i < 6 then exemptH1 else exemptH2

/-- LD 30/2023 art. 17(b): taxes are rounded up to the next 100 SYP. -/
def round100 (ticks : Int) : Int := (Rule.upTo 100).ofTicks ticks

/-- Monthly tax on net monthly income `net` with exempt minimum `e` (arts. 68-69). -/
def monthTaxWith (s : Schedule) (e net : Int) : Int :=
  round100 (exemptTaxOf s.ticks e (pos net))
def monthTax (e net : Int) : Int := monthTaxWith wageSched e net

/-- Employee social insurance deducted under art. 70 (7 % of the monthly wage; Executive Instructions example). -/
def siRate : Int := 7
def socialMonth (gross : Int) : Int := pos gross * siRate / 100

/-- Split an annual amount into 12 months (the first `annual % 12` get one lira more) and sum `f i month`. -/
def overYear (f : Nat → Int → Int) (annual : Int) : Int :=
  let q := annual / 12
  let r := (annual % 12).toNat
  (List.range 12).foldl (fun acc i => acc + f i (q + if i < r then 1 else 0)) 0

/-- Annual wage tax; `withExempt = false` when the art. 73 exempt minimum is used on business profits instead. -/
def wageTax (withExempt : Bool) (annual : Int) : Int :=
  if annual ≤ 0 then 0 else
  overYear (fun i m => monthTax (if withExempt then exemptOfMonth i else 0) (m - socialMonth m)) annual
def wageSocial (annual : Int) : Int := if annual ≤ 0 then 0 else overYear (fun _ m => socialMonth m) annual

/-- LD 30/2023 art. 4 (Law 24/2003 art. 16(a)) and art. 8 (art. 20(a)): annual business profits of a natural person. -/
def bizSched : Schedule := Schedule.ofList
  [(0, 1000), (10000000, 1400), (30000000, 1800), (100000000, 2200), (500000000, 2500)]
def bizExempt : Int := 3000000
def bizTax (withExempt : Bool) (p : Int) : Int :=
  round100 (exemptTaxOf bizSched.ticks (if withExempt then bizExempt else 0) (pos p))

/-- Art. 73: one exempt minimum when both chapters apply, the cheaper choice. -/
def personTax (a : Adult) : Int × Int × Bool :=
  if a.selfEmployment ≤ 0 then (wageTax true a.wages, 0, true)
  else if a.wages ≤ 0 then (0, bizTax true a.selfEmployment, false)
  else
    let o1 := (wageTax true a.wages, bizTax false a.selfEmployment)
    let o2 := (wageTax false a.wages, bizTax true a.selfEmployment)
    if o1.1 + o1.2 ≤ o2.1 + o2.2 then (o1.1, o1.2, true) else (o2.1, o2.2, false)

-- The Executive Instructions' worked examples on the 2003 table (art. 68: 5/7/9/11/13/20 %, art. 69: 5,000 exempt;
-- art. 58 then rounded up to 10 SYP): the method (exempt taken off the first band) reproduces them exactly.
def sched2003 : Schedule := Schedule.ofList
  [(0, 500), (8000, 700), (12000, 900), (16000, 1100), (20000, 1300), (30000, 2000)]
#guard exemptTaxOf sched2003.ticks 5000 10000 = 290 * BP
#guard exemptTaxOf sched2003.ticks 5000 9300 = 241 * BP
#guard (Rule.upTo 10).ofTicks (exemptTaxOf sched2003.ticks 5000 9300) = 250
#guard exemptTaxOf sched2003.ticks 5000 40000 = 4530 * BP
#guard exemptTaxOf sched2003.ticks 5000 37200 = 3970 * BP
#guard exemptTaxOf sched2003.ticks 5000 37400 = 4010 * BP
-- LD 30/2023 art. 19: at the top edge 1,100,000 the table is the sum of the printed band widths x rates.
#guard wageSched.ticks 1100000 =
  (250000 * 5 + 200000 * 7 + 200000 * 9 + 200000 * 11 + 250000 * 13) * 100
-- the 2025 exempt minimum swallows whole bands: at 837,000 the first taxed lira is in the 11 % band ...
#guard monthTax exemptH2 837000 = 0 ∧ monthTax exemptH2 850000 = 1500
-- ... and at 279,000 in the 7 % band (the 5 % band is gone in 2025).
#guard monthTax exemptH1 279000 = 0 ∧ monthTax exemptH1 450000 = 12000
-- LD 30/2023 art. 17(b): one lira of tax is rounded up to 100.
#guard monthTax exemptH2 837010 = 100
-- art. 20: business profits, 3,000,000 exempt; at 10,000,000 the tax is 10 % of 7,000,000.
#guard bizTax true 3000000 = 0 ∧ bizTax true 10000000 = 700000

structure Res where
  wage : Int
  biz : Int
  social : Int
  exemptOnWages : List Bool

def household (c : Canon) : Res :=
  let rs := c.adults.map personTax
  ⟨sumInts (rs.map (·.1)), sumInts (rs.map (·.2.1)), sumInts (c.adults.map fun a => wageSocial a.wages),
   rs.map (·.2.2)⟩

def out (c : Canon) : Out :=
  let r := household c
  Out.make c "SY" "SYP" (r.wage + r.biz)
    (employeeSocial := r.social)
    (detail := [Out.d "salaryTax" r.wage, Out.d "businessProfitsTax" r.biz, Out.d "socialInsurance7pct" r.social,
      Out.d "exemptMinimumJanJun" exemptH1, Out.d "exemptMinimumJulDec" exemptH2,
      Out.dStr "note" "Law 24/2003 arts. 66-73 as amended by LD 30/2023 arts. 4, 8, 17, 19-20; exempt minimum 279,000 / 837,000 a month (Minister of Finance, SANA 20 Jul 2025, official secondary); monthly tax rounded up to 100"])
    (unsupported := ["2025 exempt minimum from the Minister of Finance's statement (SANA), not from the circular or the minimum-wage decree (official secondary)",
      "employee social insurance taken at 7 % (Ministry worked example, 2003 instructions); the 2025 rate and any ceiling not verified"] ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: exempt (art. 67(هـ)); no tax computed"] else []) ++
      (if c.dividends ≠ 0 ∨ c.interest ≠ 0 then ["dividends / interest (tax on movable capital income): not modelled"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rental income (real-estate taxes): not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: not modelled"] else []))

def country : Country := { code := "SY", name := "Syria", currency := "SYP", year := "2025", compute := out }

theorem wageSched_progressive : wageSched.progressive = true := by decide
theorem bizSched_progressive : bizSched.progressive = true := by decide

end SyTax
