import JpTax.Income

/-!
# 所得控除 (所得税法第2編第2章第4節; 租税特別措置法第41条の16の2)

Thresholds are on the 合計所得金額 (第2条第1項第30号: "第七十条（純損失の繰越控除）及び第七十一条（雑損失の繰越
控除）の規定を適用しないで計算した場合における第二十二条（課税標準）に規定する総所得金額、退職所得金額及び山林所得金額の
合計額"). The claimant's 合計所得金額 is `g`; a spouse's or relative's is `s`.
-/

namespace JpTax

/-! ## 基礎控除 (第86条; 措置法第41条の16の2) -/

/-- **第86条第1項**: "合計所得金額が二千五百万円以下である居住者" deduct 580,000 yen up to 23,500,000 yen of
合計所得金額 (第1号 "五十八万円"), 480,000 to 24,000,000, 320,000 to 24,500,000, 160,000 to 25,000,000, nothing
above. -/
def kiso86 (g : Int) : Int :=
  if g ≤ 23500000 then 580000
  else if g ≤ 24000000 then 480000
  else if g ≤ 24500000 then 320000
  else if g ≤ 25000000 then 160000
  else 0

/-- **措置法第41条の16の2第1項第1号** (令和7年分及び令和8年分): the addition to 第86条第1項第1号 for a 合計所得金額
of at most 6,550,000 yen: "百三十二万円以下である場合 / 三十七万円", "百三十二万円を超え三百三十六万円以下 / 三十万円",
"三百三十六万円を超え四百八十九万円以下 / 十万円", "四百八十九万円を超える場合 / 五万円". -/
def kisoAddition (g : Int) : Int :=
  if g ≤ 1320000 then 370000
  else if g ≤ 3360000 then 300000
  else if g ≤ 4890000 then 100000
  else 50000

/-- **基礎控除額, 令和7年分**: "合計所得金額...が六百五十五万円...以下である場合における同法第八十六条第二項に規定する
基礎控除の額は、同条第一項の規定にかかわらず、同項第一号に定める金額に...加算した額とする" (措置法第41条の16の2第1項). -/
def kisoKojo (g : Int) : Int :=
  if g ≤ 6550000 then 580000 + kisoAddition g else kiso86 g

/-! ## 配偶者控除, 配偶者特別控除 (第83条, 第83条の2) -/

/-- 第2条第1項第33号: a 同一生計配偶者 has "合計所得金額が五十八万円以下" (48万円 until 30 November 2025). -/
def douitsuLimit : Int := 580000

/-- **第83条第1項**: 配偶者控除 for a 控除対象配偶者 (第2条第1項第33号の2: a 同一生計配偶者 of a resident whose
合計所得金額 is at most 10,000,000 yen): 380,000 yen (480,000 for a 老人控除対象配偶者, aged 70 or more) up to
9,000,000 yen of the claimant's 合計所得金額, 260,000 (320,000) to 9,500,000, 130,000 (160,000) to 10,000,000. -/
def haigushaKojo (g s : Int) (spouseOld : Bool) (lim : Int := douitsuLimit) : Int :=
  if s ≤ lim ∧ g ≤ 10000000 then
    if g ≤ 9000000 then (if spouseOld then 480000 else 380000)
    else if g ≤ 9500000 then (if spouseOld then 320000 else 260000)
    else (if spouseOld then 160000 else 130000)
  else 0

/-- "五万円の整数倍の金額から三万円を控除した金額で当該超える部分の金額に満たないもののうち最も多い金額" (or the amount
itself when it is of that form): the largest `50,000 k − 30,000` not above `x`. -/
def step5 (x : Int) : Int := 50000 * ((x + 30000) / 50000) - 30000

/-- **第83条の2第1項第1号**: the amount for a claimant with at most 9,000,000 yen: イ "合計所得金額が九十五万円以下で
ある配偶者 / 三十八万円"; ロ "九十五万円を超え百三十万円以下である配偶者 / 三十八万円からその配偶者の合計所得金額のうち
九十三万一円を超える部分の金額（...）を控除した金額"; ハ "百三十万円を超える配偶者 / 三万円". -/
def tokubetsuBase (s : Int) : Int :=
  if s ≤ 950000 then 380000
  else if s ≤ 1300000 then 380000 - step5 (s - 930001)
  else 30000

/-- **第83条の2第1項**: 配偶者特別控除, for a spouse "合計所得金額が百三十三万円以下であるもの" who is not a 控除対象配偶者,
of a claimant with at most 10,000,000 yen. 第2号 and 第3号: two thirds and one third of the amount, "当該金額に一万円
未満の端数がある場合には、これを切り上げた金額". 第2項第1号: not both spouses (the caller decides who claims). -/
def haigushaTokubetsu (g s : Int) (lim : Int := douitsuLimit) : Int :=
  if lim < s ∧ s ≤ 1330000 ∧ g ≤ 10000000 then
    let b := tokubetsuBase s
    if g ≤ 9000000 then b
    else if g ≤ 9500000 then cdiv (2 * b) 30000 * 10000
    else cdiv b 30000 * 10000
  else 0

/-! ## 扶養控除, 特定親族特別控除 (第84条, 第84条の2) -/

/-- A relative the claimant may take into account: age on 31 December (第85条第3項) and 合計所得金額. -/
structure Relative where
  age : Int
  income : Int
  /-- the 合計所得金額 limit of a 扶養親族 / 同一生計配偶者 in the year: 580,000 (令和7年分), 480,000 (令和6年分) -/
  lim : Int := 580000
  deriving Repr, Inhabited

/-- 第2条第1項第34号: 扶養親族 = "合計所得金額が五十八万円以下である者" (48万円 until 30 November 2025). -/
def Relative.fuyo (d : Relative) : Bool := decide (d.income ≤ d.lim)

/-- 第2条第1項第34号の2イ: a 控除対象扶養親族 is an 扶養親族 "年齢十六歳以上の者". -/
def Relative.kojoTaisho (d : Relative) : Bool := d.fuyo && decide (d.age ≥ 16)

/-- 第2条第1項第34号の3: 特定扶養親族 "年齢十九歳以上二十三歳未満の者". -/
def Relative.tokutei (d : Relative) : Bool := d.kojoTaisho && decide (19 ≤ d.age ∧ d.age < 23)

/-- 第2条第1項第34号の4: 老人扶養親族 "年齢七十歳以上の者". -/
def Relative.rojin (d : Relative) : Bool := d.kojoTaisho && decide (d.age ≥ 70)

/-- **第84条第1項**: "その控除対象扶養親族一人につき三十八万円（その者が特定扶養親族である場合には六十三万円とし、
その者が老人扶養親族である場合には四十八万円とする。）" (同居老親等 580,000 under 措置法第41条の16 is not modelled: a
household's children are not its parents). -/
def fuyoKojo (d : Relative) : Int :=
  if d.kojoTaisho then (if d.tokutei then 630000 else if d.rojin then 480000 else 380000) else 0

/-- "十万円の整数倍の金額から八万円を控除した金額で当該乗じた金額に満たないもののうち最も多い金額" (or the amount itself):
the largest `100,000 k − 80,000` not above `x`. -/
def step10 (x : Int) : Int := 100000 * ((x + 80000) / 100000) - 80000

/-- **第84条の2第1項** (令和7年法律第13号, new for 令和7年分): 特定親族特別控除 for a relative "年齢十九歳以上二十三歳
未満" who is not a 控除対象扶養親族 and has "合計所得金額が百二十三万円以下": 一 to 850,000 yen "六十三万円"; 二 to
1,150,000 "六十三万円からその特定親族の合計所得金額のうち八十四万一円を超える部分の金額に二を乗じた金額（...）を控除した
金額"; 三 to 1,200,000 "六万円"; 四 above "三万円". -/
def tokuteiShinzokuKojo (d : Relative) : Int :=
  if 19 ≤ d.age ∧ d.age < 23 ∧ 580000 < d.income ∧ d.income ≤ 1230000 then
    if d.income ≤ 850000 then 630000
    else if d.income ≤ 1150000 then 630000 - step10 (2 * (d.income - 840001))
    else if d.income ≤ 1200000 then 60000
    else 30000
  else 0

/-! ## Other deductions modelled -/

/-- **第81条** with 第2条第1項第31号: ひとり親控除 350,000 yen for one "現に婚姻をしていない者" with "その者と生計を一に
する子" and "合計所得金額が五百万円以下" (and no de facto spouse). -/
def hitorioyaKojo (single : Bool) (g : Int) : Int := if single && decide (g ≤ 5000000) then 350000 else 0

/-- **第78条第1項**: 寄附金控除: "その年中に支出した特定寄附金の額の合計額（当該合計額がその者のその年分の総所得金額、
退職所得金額及び山林所得金額の合計額の百分の四十に相当する金額を超える場合には、当該百分の四十に相当する金額）" less
"二千円". -/
def kifukinKojo (donation total : Int) : Int := pos (min donation (pos total * 4 / 10) - 2000)

/-! ## Facts about the step formulas -/

/-- **The 配偶者特別控除 formula of 第83条の2第1項第1号ロ is the familiar 5万円 table**: from a spouse's income of
950,001 yen the amount is 360,000 yen, then 50,000 yen less for each further 50,000 yen of the spouse's income
(rows (950,000, 1,000,000], (1,000,000, 1,050,000], ...). The statute writes this as "the excess over 930,001 yen,
lowered to a number of the form 50,000 k − 30,000". -/
theorem tokubetsuBase_table (s : Int) (h1 : 950000 < s) (h2 : s ≤ 1300000) :
    tokubetsuBase s = 360000 - 50000 * ((s - 950001) / 50000) := by
  unfold tokubetsuBase step5
  have : ¬ s ≤ 950000 := by omega
  simp only [this, ite_false, h2, ite_true]
  omega

/-- Step by step: (950,000, 1,000,000] → 360,000, ..., (1,250,000, 1,300,000] → 60,000. -/
theorem tokubetsuBase_steps :
    tokubetsuBase 950001 = 360000 ∧ tokubetsuBase 1000000 = 360000 ∧
    tokubetsuBase 1000001 = 310000 ∧ tokubetsuBase 1050000 = 310000 ∧
    tokubetsuBase 1050001 = 260000 ∧ tokubetsuBase 1100001 = 210000 ∧
    tokubetsuBase 1150001 = 160000 ∧ tokubetsuBase 1200001 = 110000 ∧
    tokubetsuBase 1250001 = 60000 ∧ tokubetsuBase 1300000 = 60000 ∧
    tokubetsuBase 1300001 = 30000 := by decide

/-- The 特定親族特別控除 formula of 第84条の2第1項第2号 gives 610,000 yen for 850,001–900,000, then 510,000,
410,000, ... 110,000 in steps of 50,000 yen of the relative's income (100,000 of deduction per step). -/
theorem tokuteiShinzoku_steps :
    let k := fun i => tokuteiShinzokuKojo { age := 20, income := i }
    k 580000 = 0 ∧ k 580001 = 630000 ∧ k 850000 = 630000 ∧ k 850001 = 610000 ∧ k 900000 = 610000 ∧
    k 900001 = 510000 ∧ k 950001 = 410000 ∧ k 1000001 = 310000 ∧ k 1050001 = 210000 ∧
    k 1100001 = 110000 ∧ k 1150000 = 110000 ∧ k 1150001 = 60000 ∧ k 1200001 = 30000 ∧
    k 1230000 = 30000 ∧ k 1230001 = 0 := by decide

theorem kisoKojo_values :
    kisoKojo 1320000 = 950000 ∧ kisoKojo 1320001 = 880000 ∧ kisoKojo 3360001 = 680000 ∧
    kisoKojo 4890001 = 630000 ∧ kisoKojo 6550001 = 580000 ∧ kisoKojo 23500001 = 480000 ∧
    kisoKojo 24000001 = 320000 ∧ kisoKojo 24500001 = 160000 ∧ kisoKojo 25000001 = 0 := by decide

/-- 基礎控除 never increases with income. -/
theorem kisoKojo_antitone {a b : Int} (h : a ≤ b) : kisoKojo b ≤ kisoKojo a := by
  unfold kisoKojo kisoAddition kiso86
  repeat (first | split | omega)


/-! ## 令和6年分 (2024; tests round 3)

所得税法 as in force for 令和6年分 (e-Gov revision 340AC0000000033_20240612, `law/shotokuzeiho_2024-12-31.xml`):
* 第86条第1項: "一 その居住者の合計所得金額が二千四百万円以下である場合 四十八万円 二 … 二千四百五十万円以下 … 三十二万円 三 …
  二千五百万円以下 … 十六万円" (no 措置法第41条の16の2 addition: that is 令和7年分 and 令和8年分).
* 第2条第1項第33号 (同一生計配偶者) and 第34号 (扶養親族): "合計所得金額が四十八万円以下".
* No 特定親族特別控除 (第84条の2 was added by 令和7年法律第13号).
地方税法 for 令和7年度 (the 住民税 on 2024 income; revision 325AC0000000226_20250401, `law/chihozeiho_2025-04-01.xml`):
基礎控除 430,000 as above; 同一生計配偶者 and 扶養親族 "四十八万円以下". -/

def kisoKojo2024 (g : Int) : Int :=
  if g ≤ 24000000 then 480000 else if g ≤ 24500000 then 320000 else if g ≤ 25000000 then 160000 else 0

def kisoKojoY (y g : Int) : Int := if 2020 ≤ y ∧ y ≤ 2024 then kisoKojo2024 g else kisoKojo g
def douitsuLimitY (y : Int) : Int := if 2020 ≤ y ∧ y ≤ 2024 then 480000 else douitsuLimit

end JpTax
