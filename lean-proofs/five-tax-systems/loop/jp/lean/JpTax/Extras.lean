import JpTax.Tax
import JpTax.Social

/-!
# Additions for the loophole catalogue (`~/cmp/loop/jp`): deductions and credits the base model leaves out

Each definition copies one provision (texts in `~/cmp/loop/jp/law/*.txt`, extracted from the e-Gov XML of
`~/cmp/jp/law`: 所得税法 and 措置法 as of 2025-12-31, 地方税法 as of 2026-06-01).
-/

namespace JpTax

/-! ## Income -/

/-- **措置法第25条の2第3項** (65万円: e-Tax filing or 優良な電子帳簿; 55万円 otherwise, 第1項 10万円 for simple books):
"六十五万円と...所得の金額の合計額...とのいずれか低い金額" — the claim, at most the 事業所得. -/
def aoiroKojo (claim business : Int) : Int := min (pos claim) (pos business)

/-! ## 所得控除 -/

/-- **第73条第1項**: 医療費控除 = paid medical costs "の合計額がその居住者のその年分の総所得金額、退職所得金額及び山林所得
金額の合計額の百分の五に相当する金額（当該金額が十万円を超える場合には、十万円）を超える場合" the excess, "二百万円を限度".
`medical` is net of insurance reimbursements. -/
def iryohiKojo (medical total : Int) : Int :=
  min 2000000 (pos (medical - min 100000 (pos total * 5 / 100)))

/-- **措置法第41条の17第1項** (セルフメディケーション税制, the alternative to 第73条): 特定一般用医薬品等購入費 "の合計額が
一万二千円を超えるときは、その超える部分の金額（当該金額が八万八千円を超える場合には、八万八千円）". -/
def selfMedKojo (otc : Int) : Int := min 88000 (pos (otc - 12000))

/-- **第76条第1項第1号イ〜ニ** (新生命保険料; the same scale for 介護医療 第2項 and 新個人年金 第3項): 20,000 以下 the amount,
40,000 以下 half + 10,000, 80,000 以下 a quarter + 20,000, above 40,000. (NTA: fractions of a yen rounded up.) -/
def lifeOne (x : Int) : Int :=
  let x := pos x
  if x ≤ 20000 then x else if x ≤ 40000 then cdiv x 2 + 10000
  else if x ≤ 80000 then cdiv x 4 + 20000 else 40000

/-- **第76条第4項**: the three amounts together at most 120,000 yen. `xs` = [一般, 介護医療, 個人年金] (new contracts). -/
def lifeKojo (xs : List Int) : Int := min 120000 (xs.foldl (fun a x => a + lifeOne x) 0)

/-- **地方税法第314条の2第1項第5号** (住民税): 12,000 以下 the amount, 32,000 以下 half + 6,000, 56,000 以下 a quarter +
14,000, above 28,000; 第8項 (the three together) at most 70,000. -/
def lifeOneLocal (x : Int) : Int :=
  let x := pos x
  if x ≤ 12000 then x else if x ≤ 32000 then cdiv x 2 + 6000
  else if x ≤ 56000 then cdiv x 4 + 14000 else 28000

def lifeLocal (xs : List Int) : Int := min 70000 (xs.foldl (fun a x => a + lifeOneLocal x) 0)

/-- **第77条第1項** 地震保険料控除: the premiums, at most 50,000 yen; 住民税 (第314条の2第1項第5号の3) half, at most 25,000. -/
def jishinKojo (x : Int) : Int := min 50000 (pos x)
def jishinLocal (x : Int) : Int := min 25000 (pos x / 2)

/-- **第80条** with 第2条第1項第30号: 寡婦控除 270,000 yen (合計所得金額 at most 5,000,000; not a ひとり親); 住民税
(第314条の2第1項第8号) 260,000. -/
def kafuKojo (widow : Bool) (g : Int) : Int := if widow && decide (g ≤ 5000000) then 270000 else 0
def kafuLocal (widow : Bool) (g : Int) : Int := if widow && decide (g ≤ 5000000) then 260000 else 0

/-! ## 税額控除 (所得税) -/

/-- **措置法第41条第1項** (居住年 2024–2025, 住宅借入金等特別控除): "住宅借入金等の金額の合計額（...借入限度額を超える場合に
は、当該借入限度額）の百分の〇・七に相当する金額（...百円未満の端数があるときは、これを切り捨てる。）"; only for a 合計所得
金額 of at most 20,000,000 yen. The 借入限度額 (第41条第10項 ff.) depends on the dwelling and is an input. -/
def jutakuCredit (balance limit g : Int) : Int :=
  if g ≤ 20000000 then trunc100 (min (pos balance) (pos limit) * 7 / 1000) else 0

/-- **措置法第41条の18の3第1項** (公益社団法人・認定NPO法人等への寄附, 税額控除 chosen instead of 第78条): 40 % of the
donation (at most 40 % of total income less the deductible donations) above "二千円（...所得控除対象寄附金の額がある場合
には、二千円から当該所得控除対象寄附金の額を控除した残額）", "百円未満の端数があるときは、これを切り捨てる", capped at "その年分
の所得税の額の百分の二十五" (also cut to 100 yen). -/
def npoCredit (npo deductible total taxBefore : Int) : Int :=
  let base := min (pos npo) (pos (pos total * 4 / 10 - pos deductible))
  let thr := pos (2000 - pos deductible)
  min (trunc100 (pos (base - thr) * 40 / 100)) (trunc100 (pos taxBefore * 25 / 100))

/-! ## 住民税 credits: 寄附金税額控除 (ふるさと納税), 申告特例控除 (ワンストップ), 住宅借入金等特別税額控除 -/

/-- **地方税法第314条の7第11項第1号の表** as replaced by **附則第5条の6第2項** (令和20年度まで): the rate (in thousandths of a
percent) on the excess over 2,000 yen, by the 課税総所得金額 less the 人的控除差調整額: "百分の八十四・八九五", "七十九・七九",
"六十九・五八", "六十六・五一七", "五十六・三〇七", "四十九・一六", "四十四・〇五五"; 第2号: below zero "百分の九十". -/
def tokureiRate (x : Int) : Int :=
  if x < 0 then 90000
  else if x ≤ 1950000 then 84895 else if x ≤ 3300000 then 79790 else if x ≤ 6950000 then 69580
  else if x ≤ 9000000 then 66517 else if x ≤ 18000000 then 56307 else if x ≤ 40000000 then 49160 else 44055

/-- **附則第7条の2第2項・第5項** as replaced by **附則第7条の3**: the 申告特例控除額 (ワンストップ特例) is the 特例控除額 times
"八十四・八九五分の五・一〇五" (195万円以下), "七十九・七九分の十・二一", "六十九・五八分の二十・四二", "六十六・五一七分の二十三・
四八三", "五十六・三〇七分の三十三・六九三" (9,000,000 yen and above). The table has no row for a negative amount: such an
amount is "百九十五万円以下". Returns (numerator, denominator). -/
def shinkokuRatio (x : Int) : Int × Int :=
  if x ≤ 1950000 then (5105, 84895) else if x ≤ 3300000 then (10210, 79790)
  else if x ≤ 6950000 then (20420, 69580) else if x ≤ 9000000 then (23483, 66517) else (33693, 56307)

structure DonationIn where
  furusato : Int        -- 特例控除対象寄附金 (都道府県等 designated by the 総務大臣: ふるさと納税)
  oneStop : Bool        -- 寄附金税額控除に係る申告特例 (no 確定申告): adds the 申告特例控除額, no 所得税 deduction
  total : Int           -- 総所得金額等 (for the 30 % cap)
  base : Int            -- 住民税 課税総所得金額 (第314条の3第2項)
  jintekiSa : Int       -- 第314条の6第1号イ amount (人的控除額の差, with its 50,000 base)
  kisoIT : Int          -- 所得税 基礎控除 (第86条 with 措置法第41条の16の2)
  deriving Repr, Inhabited

/-- **第37条の2 (道府県 4 %, 2/5) / 第314条の7 (市町村 6 %, 3/5)**, Tokyo special ward (not a 指定都市): returns
(都 credit, 区 credit) in yen (each floored), given the 所得割 after 調整控除 (`prefIncome`, `muniIncome`) for the 20 % cap.
基本控除: "寄附金の額の合計額（当該合計額が前年の総所得金額...の百分の三十に相当する金額を超える場合には、当該百分の三十に
相当する金額）が二千円を超える場合には、その超える金額の百分の六"; 特例控除: rate × (furusato − 2,000) × 3/5, at most "所得割
の額の百分の二十"; the 人的控除差調整額 (第11項第1号) is the 調整控除 table amount plus "基礎控除の額...から四十八万円を控除して
得た額". -/
def donationLocal (d : DonationIn) (prefIncome muniIncome : Int) : Int × Int :=
  if d.furusato ≤ 2000 then (0, 0) else
  let k := min d.furusato (pos d.total * 3 / 10) - 2000
  let basePref := pos k * 4 / 100
  let baseMuni := pos k * 6 / 100
  let x := d.base - (d.jintekiSa + pos (d.kisoIT - 480000))
  let r := tokureiRate x
  let ex := d.furusato - 2000
  -- yen: ex × r / 100,000 × 2/5 (都) and × 3/5 (区)
  let tPref := min (ex * r * 2 / 500000) (pos prefIncome * 20 / 100)
  let tMuni := min (ex * r * 3 / 500000) (pos muniIncome * 20 / 100)
  let (nu, de) := shinkokuRatio x
  let sPref := if d.oneStop then tPref * nu / de else 0
  let sMuni := if d.oneStop then tMuni * nu / de else 0
  (basePref + tPref + sPref, baseMuni + tMuni + sMuni)

/-- **附則第5条の4の2第1項・第5項** (居住年 2009–2025): the part of the 住宅借入金等特別控除 the 所得税 could not absorb, 2/5
to the 都 and 3/5 to the 区, each at most 2 % / 3 % of the 所得税 課税総所得金額 plus "基礎控除の額...から四十八万円を控除して
得た額" and at most 39,000 / 58,500 yen. Returns (都, 区). -/
def jutakuLocal (residual taxableIT kisoIT : Int) : Int × Int :=
  let r := pos residual
  let b := pos taxableIT + pos (kisoIT - 480000)
  (min (r * 2 / 5) (min 39000 (b * 2 / 100)), min (r * 3 / 5) (min 58500 (b * 3 / 100)))

/-! ## Social insurance on a bonus -/

/-- One bonus paid in December on top of the 12 monthly salaries: 健康保険法第45条第1項 (標準賞与額 = the bonus cut to 1,000
yen, "五百七十三万円" a year at most), 厚生年金保険法第24条の4第1項 ("百五十万円" per payment at most), 雇用保険 on the whole
bonus (労働保険徴収法: 賃金総額). Only for an insured employee (the 88,000-yen test of 健康保険法第3条第1項第9号ロ counts
"報酬（...賞与...を除く。）", so a bonus never makes an employee insured). -/
def socialB (w bonus age : Int) : SocialOut :=
  let s := social w age
  if !insuredEmployee w || bonus ≤ 0 then s else
  let std := trunc1000 bonus
  let kaigo := decide (40 ≤ age ∧ age ≤ 64)
  let h := if age ≥ 75 then 0 else rhd (min std 5730000 * healthRate 12 kaigo) 200000
  let p := if age ≥ 70 then 0 else rhd (min std 1500000 * 18300) 200000
  let k := rhd (bonus * koyoRate 12) 100000
  { s with health := s.health + h, pension := s.pension + p, koyo := s.koyo + k }

def zeroSocial : SocialOut := { kenpoStd := 0, kouseiStd := 0, health := 0, pension := 0, koyo := 0 }

end JpTax
