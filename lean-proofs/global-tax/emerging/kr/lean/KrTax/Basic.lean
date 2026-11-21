import TaxKernel

/-!
# Korea (대한민국), tax year 2025 (귀속 2025, calendar year): sources, units, parameters

Every amount is a whole number of won (`Int`); rates are basis points (`TaxKernel.BP = 10000`) or exact fractions.
Texts are the official ones of 법제처 국가법령정보센터 (law.go.kr), in the version that governs 2025 income
(fetched 2026-11-19 into `~/cmp20/emerging/kr/refs/lawgo/`, script `scripts/lawgo.py`):

* ITA  = 소득세법, 법률 제20615호 (2024-12-31), in force 2025-01-01: https://www.law.go.kr/법령/소득세법/(20615)
* ITAD = 소득세법 시행령, 대통령령 제35349호 (2025-02-28): https://www.law.go.kr/법령/소득세법시행령/(35349)
* STA  = 조세특례제한법, 법률 제21138호 (2025-11-11; 근로·자녀장려금 for 2025 income are claimed in May 2026 under
  this text): https://www.law.go.kr/법령/조세특례제한법/(21138)
* STAD = 조세특례제한법 시행령, 대통령령 제36127호 (2026-02-27; its 별표 11 / 11의2 산정표 apply to claims made
  from 2025 / 2024 on): https://www.law.go.kr/법령/조세특례제한법시행령/(36127)
* LTA  = 지방세법, 법률 제20630호 (2024-12-31), in force 2025-01-01: https://www.law.go.kr/법령/지방세법/(20630)
* NHID = 국민건강보험법 시행령, 대통령령 제35446호 (2025-04-15); LTCD = 노인장기요양보험법 시행령 제35043호
  (2024-12-03); EIPD = 고용보험 및 산업재해보상보험의 보험료징수 등에 관한 법률 시행령 (current); NPA = 국민연금법
  법률 제20584호 (2024-12-20); CAA = 아동수당법 법률 제19455호 (2023-06-13).

The Global law corpus `south-korea/national/acts/ls-001565` (소득세법) holds the current consolidated text only and
drops the statute's tables (they are images on law.go.kr); the tables here are read from law.go.kr's image `alt`
text and checked against the images where the alt text is defective (FINDINGS F2).
-/

namespace KrTax
open TaxKernel

/-- `a * n / d` rounded down (원 미만 절사), for `d > 0`. -/
def mulDiv (a n d : Int) : Int := a * n / d

/-- `x` rounded up to a multiple of `u` (`u > 0`). -/
def ceilTo (u x : Int) : Int := ceilDiv x u * u

/-- `x` rounded down to a multiple of `u` (`u > 0`). -/
def floorTo (u x : Int) : Int := x / u * u

/-! ## 소득세법 (ITA) -/

/-- ITA §47①: 근로소득공제 on 총급여액, as rates on slices: "500만원 이하 총급여액의 100분의 70", "350만원 + 500만원을
초과하는 금액의 100분의 40", "750만원 + 1천500만원을 초과하는 금액의 100분의 15", "1천200만원 + 4천500만원을 초과하는
금액의 100분의 5", "1천475만원 + 1억원을 초과하는 금액의 100분의 2". -/
def earnedDedSched : Schedule :=
  Schedule.ofList [(0, 7000), (5000000, 4000), (15000000, 1500), (45000000, 500), (100000000, 200)]

/-- ITA §47① 단서: "공제액이 2천만원을 초과하는 경우에는 2천만원을 공제한다". -/
def earnedDedCap : Int := 20000000

/-- ITA §47의2①: 연금소득공제 on 총연금액: "350만원 이하 총연금액", "350만원 + 350만원을 초과하는 금액의 100분의 40",
"490만원 + 700만원을 초과하는 금액의 100분의 20", "630만원 + 1400만원을 초과하는 금액의 100분의 10"; 단서 cap 900만원. -/
def pensionDedSched : Schedule :=
  Schedule.ofList [(0, 10000), (3500000, 4000), (7000000, 2000), (14000000, 1000)]
def pensionDedCap : Int := 9000000

/-- ITA §50①: 기본공제 "1명당 연 150만원". -/
def basicDed : Int := 1500000
/-- ITA §50①2, 3: a spouse / dependant qualifies with 소득금액 합계액 "100만원 이하" or "총급여액 500만원 이하의 근로소득만". -/
def depIncomeLimit : Int := 1000000
def depWageLimit : Int := 5000000
/-- ITA §50①3나: 직계비속 "20세 이하". -/
def childMaxAge : Nat := 20
/-- ITA §51①1: 경로우대자 (70세 이상) "1명당 연 100만원"; ①6: 한부모 "연 100만원"; ①3: 부녀자 "연 50만원". -/
def elderlyDed : Int := 1000000
def singleParentDed : Int := 1000000
def womanDed : Int := 500000

/-- ITA §55①: 종합소득세율 (8 brackets, 6 % to 45 %). The table image reads "3억8,406만원 + (10억원을 초과하는 금액의
45퍼센트)" for the top row; law.go.kr's text (alt) of the same image drops "3억8,406만원 +" (FINDINGS F2). -/
def natSched : Schedule :=
  Schedule.ofList [(0, 600), (14000000, 1500), (50000000, 2400), (88000000, 3500), (150000000, 3800),
    (300000000, 4000), (500000000, 4200), (1000000000, 4500)]

/-- LTA §92①: 개인지방소득세 표준세율, "과세표준의 1천분의 6" … "3천840만6천원 + (10억원을 초과하는 금액의
1천분의 45)": the national schedule at one tenth. Seoul has not used §92② (±50 %). -/
def localSched : Schedule :=
  Schedule.ofList [(0, 60), (14000000, 150), (50000000, 240), (88000000, 350), (150000000, 380),
    (300000000, 400), (500000000, 420), (1000000000, 450)]

/-- ITA §59①: 근로소득세액공제 "130만원 이하: 산출세액의 100분의 55; 130만원 초과: 71만5천원 + 130만원을 초과하는
금액의 100분의 30" (as rates on slices of the 근로소득 산출세액). -/
def earnedCreditSched : Schedule := Schedule.ofList [(0, 5500), (1300000, 3000)]

/-- ITA §59② (limit by 총급여액): "3천 300만원 이하: 74만원"; "3천300만원 초과 7천만원 이하: 74만원 - [(총급여액 -
3천 300만원) × 8/1000] … 66만원보다 적은 경우에는 66만원"; "7천만원 초과 1억2천만원 이하: 66만원 - [(총급여액 -
7천만원) × 1/2] … 50만원"; "1억2천만원을 초과: 50만원 - [(총급여액 - 1억2천만원) × 1/2] … 20만원". -/
def earnedCreditLimit (w : Int) : Int :=
  if w ≤ 33000000 then 740000
  else if w ≤ 70000000 then max 660000 (740000 - mulDiv (w - 33000000) 8 1000)
  else if w ≤ 120000000 then max 500000 (660000 - (w - 70000000) / 2)
  else max 200000 (500000 - (w - 120000000) / 2)

/-- ITA §59의2① (as amended by 법률 제20615호): 자녀세액공제 for 공제대상자녀 "8세 이상": "1명인 경우: 연 25만원",
"2명인 경우: 연 55만원", "3명 이상인 경우: 연 55만원과 2명을 초과하는 1명당 연 40만원". -/
def childCredit (n : Nat) : Int :=
  if n = 0 then 0 else if n = 1 then 250000 else 550000 + 400000 * ((n : Int) - 2)
def childCreditMinAge : Nat := 8

/-- ITA §59의2③: 출산·입양 공제 "첫째인 경우: 연 30만원", "둘째: 연 50만원", "셋째 이상: 연 70만원". -/
def birthCredit (order : Nat) : Int := if order ≤ 1 then 300000 else if order = 2 then 500000 else 700000

/-- ITA §59의3①: 연금계좌세액공제 "100분의 12" (100분의 15 when 종합소득금액 ≤ 4천500만원, or 총급여액 ≤ 5천500만원
with wages only); 연금저축 ≤ 600만원 and with 퇴직연금 "연 900만원" in all. -/
def pensionAcctCap : Int := 9000000

/-- ITA §59의4⑨1: 표준세액공제 for an employee who claims no 특별소득공제/특별세액공제/월세세액공제 "연 13만원"; ⑨2가,
나: other residents 12만원 (성실사업자) / 7만원. -/
def stdCreditEmployee : Int := 130000
def stdCreditOther : Int := 70000

/-- ITA §14③6 / §62: 이자소득등의 종합과세기준금액 "2천만원"; §129①1라, ②나: 원천징수세율 "100분의 14". -/
def finThreshold : Int := 20000000
def finRateBp : Int := 1400
/-- ITA §17③ 단서 (Gross-up): "그 배당소득의 100분의 10에 해당하는 금액을 더한 금액". -/
def grossUpBp : Int := 1000

/-! ## 조세특례제한법 (STA) §100의3, §100의5, §100의28, §100의29: income limits -/

/-- STA §100의3①2: 총소득기준금액 단독가구 2천200만원, 홑벌이 3천200만원, 맞벌이 4천400만원. -/
def eitcLimit (kind : Nat) : Int := if kind = 0 then 22000000 else if kind = 1 then 32000000 else 44000000
/-- STA §100의28①2: 자녀장려금 "연간 총소득의 합계액이 7천만원 미만". -/
def ctcLimit : Int := 70000000
/-- STA §100의3⑤2가, 3: 홑벌이 = 배우자의 총급여액 등 "3백만원 미만"; 맞벌이 = each "3백만원 이상". -/
def dualEarnerMin : Int := 3000000
/-- STA §100의4 (부양자녀): "18세 미만". -/
def dependentChildMaxAge : Nat := 17

/-! ## Social insurance (employee share), 2025 -/

/-- NHID §44①: 직장가입자 보험료율 "1만분의 709"; employee half (국민건강보험법 §76①). -/
def healthRateTotal : Int := 709      -- per 10000
/-- LTCD §4: 장기요양보험료율 "100만분의 9,182" of 보수월액 (employee half). -/
def ltcRatePpm : Int := 9182          -- per 1,000,000
/-- EIPD §12①2: 실업급여 보험료율 "1천분의 18"; the employee pays half (보험료징수법 §13①). -/
def empRatePermille : Int := 18
/-- NPA §88③ (법률 제20584호): 사업장가입자 기여금 "기준소득월액의 1천분의 45". -/
def pensionRatePermille : Int := 45
/-- 국민연금법 시행령 §5: 기준소득월액 = 신고 소득월액 "천원 미만을 버린 금액", within 하한액/상한액 published by
보건복지부 고시 「국민연금 기준소득월액 하한액과 상한액」 for July–June: 2024-07 to 2025-06 "하한액 : 390천원", "상한액 :
6,170천원" (보건복지부고시 제2024-6호, 2024. 1. 23., 시행 2024. 7. 1.); 2025-07 to 2026-06 "하한액 : 400천원", "상한액 :
6,370천원" (제2025-24호, 2025. 2. 3., 시행 2025. 7. 1.). Texts from law.go.kr 행정규칙 (hangul address
`행정규칙/국민연금 기준소득월액 하한액과 상한액`, history via `LSW/admRulHstListR.do`, body via `LSW/admRulLsInfoR.do`
admRulSeq 2100000235432 / 2100000254486; `refs/admrul/pension_<seq>.txt`, tests round 8). -/
def pensionFloorH1 : Int := 390000
def pensionCeilH1 : Int := 6170000
def pensionFloorH2 : Int := 400000
def pensionCeilH2 : Int := 6370000

/-- CAA §4① (법률 제19455호, the text in force through 2025): "아동수당은 8세 미만의 아동에게 매월 10만원". -/
def childAllowanceMonthly : Int := 100000
def childAllowanceMaxAge : Nat := 7

/-! ## Tax year 2024 (tests round 2, `~/cmp20/improve-emerging/IMPROVE.md`)

Everything above also governs 2024 income except:
* 소득세법 §59의2① as in force for 2024 (법률 제19933호, efYd 2024-01-01, `refs/lawgo/소득세법_19933.txt`): "1. 1명인
  경우: 연 15만원 2. 2명인 경우: 연 35만원 3. 3명 이상인 경우: 연 35만원과 2명을 초과하는 1명당 연 30만원". (The 2025 amounts
  apply "이 법 시행일이 속하는 과세기간분부터", 법률 제20615호 부칙.)
* 국민연금 기준소득월액 하한액/상한액 for July 2023 – June 2024: 370,000 / 5,900,000 won (보건복지부고시 제2023-46호, 2023. 3. 22.,
  시행 2023. 7. 1.: "하한액 : 370천원", "상한액 : 5,900천원"; admRulSeq 2100000220974, fetched in round 8); July 2024 –
  June 2025: the values above.
* 장려금: 조특법 시행령 (대통령령 제35347호, 2025-02-28) 부칙 제24조: "별표 11 및 별표 11의2의 개정규정은 이 영 시행
  이후 근로장려금 또는 자녀장려금을 신청하는 경우부터 적용한다" — 2024 income is claimed in May 2025, so the tables of
  `IncentiveData` govern it too.
* Unchanged in 2024 (the texts cited above carry the same numbers; their 2024 versions were not fetched): 건강보험
  1만분의 709, 장기요양 100만분의 9,182, 고용보험 1천분의 18, the §55 schedule, §47, §59, 아동수당, 부모급여. -/

def childCreditY (y : Int) (n : Nat) : Int :=
  if y = 2024 then (if n = 0 then 0 else if n = 1 then 150000 else 350000 + 300000 * ((n : Int) - 2))
  else childCredit n

/-- (floor, ceiling) of the 기준소득월액 for January–June and July–December of year `y`. -/
def pensionLimits (y : Int) : (Int × Int) × (Int × Int) :=
  if y = 2024 then ((370000, 5900000), (pensionFloorH1, pensionCeilH1))
  else ((pensionFloorH1, pensionCeilH1), (pensionFloorH2, pensionCeilH2))

theorem childCreditY_2025 (n : Nat) : childCreditY 2025 n = childCredit n := rfl


/-! ## Tax years 2022 and 2023 (tests round 5)

* 소득세법 법률 제18578호 (efYd 2022-01-01, `refs/lawgo/소득세법_18578.*`): §55① table image (flSeq in the html,
  `refs/img/s55_18578_*.bin`): "1,200만원 이하 과세표준의 6퍼센트"; "72만원 + (1,200만원을 초과하는 금액의 15퍼센트)" to
  4,600만원; "582만원 + … 24퍼센트" to 8,800만원; "1,590만원 + … 35퍼센트" to 1억5천만원; "3,760만원 + … 38퍼센트" to 3억원;
  "9,460만원 + … 40퍼센트" to 5억원; "1억7,460만원 + … 42퍼센트" to 10억원; "3억8,460만원 + … 45퍼센트" above. §59②: limits
  74만 / 74만 − 8/1000 (min 66만) / above 7천만원 "66만원 - [(총급여액 - 7천만원) × 1/2] … 50만원" (no 1억2천만원 tier,
  added by the 2022-12-31 amendment). §59의2①: "7세 이상": 15만 / 30만 / 30만 + 30만 per child over two.
* 소득세법 법률 제19196호 (efYd 2023-01-01): §55 as 2024–2025 (1,400만 / 5,000만 bands); §59② as 2024–2025; §59의2①
  "8세 이상": 15만 / 30만 / 30만 + 30만.
* 장려금: claims made in 2023 (2022 income) and 2024 (2023 income): 조세특례제한법 법률 제19199호 / 제19936호 §100의3①2
  table image (flSeq 110849183, `refs/img/s100_3_110849183.bin`): 단독 2천200만원, 홑벌이 3천200만원, 맞벌이 3천800만원
  (4천400만원 only from claims under 법률 제20617호); §100의28①2 자녀장려금 "4천만원 미만" (제19199호) and "7천만원 미만" (제19936호,
  부칙: "2023년 1월 1일 이후 개시하는 과세기간에 대한 자녀장려금을 환급하는 경우부터"); tables `IncentiveData2023` (대통령령 제33264호,
  부칙 제10조: claims from 2023-01-01) for 2022 income (both) and 2023 income (근로장려금; the 자녀장려금 table of 대통령령 제34263호,
  <개정 2024. 2. 29.>, 부칙 제17조 "2024년 1월 1일 이후 자녀장려금을 신청하는 경우" = the model's current table).
* 국민연금 기준소득월액 (보건복지부 고시, as reported — same standing as the 2024–2025 values): Jul 2021 – Jun 2022
  330,000 / 5,240,000; Jul 2022 – Jun 2023 350,000 / 5,530,000; Jul 2023 – Jun 2024 370,000 / 5,900,000. -/

def natSched2022 : Schedule :=
  Schedule.ofList [(0, 600), (12000000, 1500), (46000000, 2400), (88000000, 3500), (150000000, 3800),
    (300000000, 4000), (500000000, 4200), (1000000000, 4500)]

def natSchedY (y : Int) : Schedule := if y ≤ 2022 then natSched2022 else natSched

def earnedCreditLimitY (y w : Int) : Int :=
  if y ≤ 2022 then
    (if w ≤ 33000000 then 740000
     else if w ≤ 70000000 then max 660000 (740000 - mulDiv (w - 33000000) 8 1000)
     else max 500000 (660000 - (w - 70000000) / 2))
  else earnedCreditLimit w

def childCreditMinAgeY (y : Int) : Nat := if y ≤ 2022 then 7 else childCreditMinAge

def childCreditY2 (y : Int) (n : Nat) : Int :=
  if y = 2022 ∨ y = 2023 then (if n = 0 then 0 else if n = 1 then 150000 else 300000 + 300000 * ((n : Int) - 2))
  else childCreditY y n

/-- (floor, ceiling) of the 기준소득월액 by half-year for 2022–2023, from the 고시 「국민연금 기준소득월액 하한액과 상한액」
(law.go.kr 행정규칙, fetched in round 8): 제2021-96호 (2021. 3. 31., 시행 2021. 7. 1.) "하한액 : 330천원", "상한액 : 5,240천원"
(January–June 2022); 제2022-71호 (2022. 3. 31., 시행 2022. 7. 1.) "350천원" / "5,530천원" (July 2022 – June 2023);
제2023-46호 (2023. 3. 22., 시행 2023. 7. 1.) "370천원" / "5,900천원" (July–December 2023). -/
def pensionLimitsY (y : Int) : (Int × Int) × (Int × Int) :=
  if y = 2022 then ((330000, 5240000), (350000, 5530000))
  else if y = 2023 then ((350000, 5530000), (370000, 5900000))
  else pensionLimits y

/-- §100의3①2 총소득기준금액 by claim law (income year `y`). -/
def eitcLimitY (y : Int) (kind : Nat) : Int :=
  if y = 2022 ∨ y = 2023 then (if kind = 0 then 22000000 else if kind = 1 then 32000000 else 38000000)
  else eitcLimit kind

/-- §100의28①2 자녀장려금 income limit by income year. -/
def ctcLimitY (y : Int) : Int := if y = 2022 then 40000000 else ctcLimit

theorem natSched2022_top : natSched2022.ticks 1000000000 = 3846000000000 := by decide

end KrTax
