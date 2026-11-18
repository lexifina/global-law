import JpTax.Basic

/-!
# Employee social insurance, calendar 2025 (an ordinary employee in Tokyo)

Simplifications (stated once): wages are paid in 12 equal monthly amounts with no bonus; the 標準報酬月額 is the grade of
that monthly amount (as the 定時決定 would give); premiums are those for the 12 months of 2025 (the accrual basis: the
deduction from the following month's pay is ignored); the employer is a 協会けんぽ member in Tokyo and a 特定適用事業所
(51+ employees), so a part-timer is insured from a monthly wage of 88,000 yen (健康保険法第3条第1項第9号ロ "八万八千円
未満であること" excludes; 厚生年金保険法第12条第5号ロ likewise); 雇用保険 is taken to cover exactly the same people.

* 健康保険法第40条第1項: the 50 grades of 標準報酬月額, 58,000 to 1,390,000 yen.
* 厚生年金保険法第20条第1項 and 厚生年金保険法の標準報酬月額の等級区分の改定等に関する政令 (令和2年政令第246号) 第1条: 32
  grades, 88,000 to 650,000 yen (the statute lists 31; the cabinet order added "第三二級 六五〇、〇〇〇円 六三五、〇〇〇円
  以上" from September 2020).
* 協会けんぽ 東京支部: 健康保険料率 9.98 % (令和6年3月分から), 9.91 % (令和7年3月分から); 介護保険第2号被保険者 (age
  40–64) 11.58 % and 11.50 % including 介護 (1.60 %, 1.59 %) (協会けんぽ, 令和6年度 / 令和7年度保険料額表, r6ippan3.xlsx,
  r7ippan3.xlsx, sheet 東京). The employee pays half (健康保険法第161条第1項).
* 厚生年金保険法第81条第4項: "平成二十九年九月以後の月分 / 千分の百八十三・〇〇", half each (第82条第1項).
* 雇用保険 (労働保険の保険料の徴収等に関する法律第12条第4項, 第5項; 第31条): employee share 6/1000 for wages paid in
  April 2024 – March 2025 and 5.5/1000 from April 2025 (一般の事業).
* Withholding rounding (協会けんぽ 保険料額表 note ①): an exact half yen goes down.
-/

namespace JpTax

/-- 健康保険法第40条第1項: (標準報酬月額, upper bound of 報酬月額, exclusive). The last grade has no upper bound. -/
def kenpoGrades : List (Int × Int) :=
  [(58000, 63000), (68000, 73000), (78000, 83000), (88000, 93000), (98000, 101000), (104000, 107000),
   (110000, 114000), (118000, 122000), (126000, 130000), (134000, 138000), (142000, 146000), (150000, 155000),
   (160000, 165000), (170000, 175000), (180000, 185000), (190000, 195000), (200000, 210000), (220000, 230000),
   (240000, 250000), (260000, 270000), (280000, 290000), (300000, 310000), (320000, 330000), (340000, 350000),
   (360000, 370000), (380000, 395000), (410000, 425000), (440000, 455000), (470000, 485000), (500000, 515000),
   (530000, 545000), (560000, 575000), (590000, 605000), (620000, 635000), (650000, 665000), (680000, 695000),
   (710000, 730000), (750000, 770000), (790000, 810000), (830000, 855000), (880000, 905000), (930000, 955000),
   (980000, 1005000), (1030000, 1055000), (1090000, 1115000), (1150000, 1175000), (1210000, 1235000),
   (1270000, 1295000), (1330000, 1355000)]

def kenpoTop : Int := 1390000

/-- 厚生年金保険法第20条第1項 with 令和2年政令第246号第1条. -/
def kouseiGrades : List (Int × Int) :=
  [(88000, 93000), (98000, 101000), (104000, 107000), (110000, 114000), (118000, 122000), (126000, 130000),
   (134000, 138000), (142000, 146000), (150000, 155000), (160000, 165000), (170000, 175000), (180000, 185000),
   (190000, 195000), (200000, 210000), (220000, 230000), (240000, 250000), (260000, 270000), (280000, 290000),
   (300000, 310000), (320000, 330000), (340000, 350000), (360000, 370000), (380000, 395000), (410000, 425000),
   (440000, 455000), (470000, 485000), (500000, 515000), (530000, 545000), (560000, 575000), (590000, 605000),
   (620000, 635000)]

def kouseiTop : Int := 650000

/-- The grade of an annual wage `w` paid in 12 equal months: the first grade whose upper bound the monthly amount does
not reach ("円未満"), compared in annual terms to avoid fractions. -/
def stdMonthly (grades : List (Int × Int)) (top : Int) (w : Int) : Int :=
  match grades.find? (fun (_, hi) => decide (w < 12 * hi)) with
  | some (std, _) => std
  | none => top

def kenpoStd (w : Int) : Int := stdMonthly kenpoGrades kenpoTop w
def kouseiStd (w : Int) : Int := stdMonthly kouseiGrades kouseiTop w

/-- Insured as an employee: monthly wage at least 88,000 yen (健康保険法第3条第1項第9号ロ). -/
def insuredEmployee (w : Int) : Bool := decide (w ≥ 12 * 88000)

/-- Health (and, for ages 40–64, 介護) rate, in hundred-thousandths, for each month of 2025: January and February are
令和6年度 months (9.98 % / 11.58 %), March to December 令和7年度 (9.91 % / 11.50 %). -/
def healthRate (month : Nat) (kaigo : Bool) : Int :=
  if month ≤ 2 then (if kaigo then 11580 else 9980) else (if kaigo then 11500 else 9910)

/-- 雇用保険 employee rate in hundred-thousandths (1/1000 = 100): 6/1000 to March 2025, 5.5/1000 from April. -/
def koyoRate (month : Nat) : Int := if month ≤ 3 then 600 else 550

structure SocialOut where
  kenpoStd : Int
  kouseiStd : Int
  health : Int      -- 健康保険 (and 介護 when aged 40–64), employee share, year
  pension : Int     -- 厚生年金, employee share, year
  koyo : Int        -- 雇用保険, employee share, year
  deriving Repr, Inhabited

def SocialOut.total (o : SocialOut) : Int := o.health + o.pension + o.koyo

def months : List Nat := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

/-- Pay for month `m` of an annual wage `w` in 12 near-equal whole-yen instalments (the remainder in December). -/
def monthPay (w : Int) (m : Nat) : Int := if m = 12 then w - 11 * (w / 12) else w / 12

/-- The employee contributions of one person for 2025: `w` annual wages, `age` on 31 December 2025 (used for the
whole year). Health insurance up to 74 (from 75 the 後期高齢者医療制度), 介護 40–64 (介護保険法第9条第2号), 厚生年金
under 70 (厚生年金保険法第9条). -/
def social (w age : Int) : SocialOut :=
  if !insuredEmployee w then { kenpoStd := 0, kouseiStd := 0, health := 0, pension := 0, koyo := 0 } else
  let hs := kenpoStd w
  let ps := kouseiStd w
  let kaigo := decide (40 ≤ age ∧ age ≤ 64)
  let health := if age ≥ 75 then 0 else
    months.foldl (fun acc m => acc + rhd (hs * healthRate m kaigo) 200000) 0
  let pension := if age ≥ 70 then 0 else 12 * rhd (ps * 18300) 200000
  let koyo := months.foldl (fun acc m => acc + rhd (monthPay w m * koyoRate m) 100000) 0
  { kenpoStd := hs, kouseiStd := ps, health, pension, koyo }

end JpTax
