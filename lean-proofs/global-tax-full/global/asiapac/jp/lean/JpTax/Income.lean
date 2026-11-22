import JpTax.Basic

/-!
# 各種所得の金額: salary, public pensions

所得税法 as in force for 令和7年分 (e-Gov 法令API v2, revision 340AC0000000033_20251218_507AC0000000013: the text as
amended by 所得税法等の一部を改正する法律, 令和7年法律第13号, whose 給与所得控除 and 基礎控除 changes took effect
on 2025-12-01 and apply to the whole of 令和7年分). 租税特別措置法: revision 332AC0000000026_20251231_507AC1000000081.

Until 30 November 2025 the 所得税法 in force had a 550,000 yen minimum 給与所得控除 (第28条第3項第1号:
"収入金額の百分の四十に相当する金額から十万円を控除した残額（当該残額が五十五万円に満たない場合には、五十五万円）");
the text that governs the tax of 2025 is the one in force from 1 December 2025. Both texts are in `law/`.
-/

namespace JpTax

/-! ## 給与所得 (所得税法第28条) -/

/-- **第28条第3項**: 給与所得控除額, in tenths of a yen (the 30 %, 20 % and 10 % slices give tenths).
* 一 "収入金額が百九十万円以下である場合 / 六十五万円" (650,000 yen: the 2025 minimum; 550,000 until 2024);
* 二 "六十五万円と当該収入金額から百九十万円を控除した金額の百分の三十に相当する金額との合計額";
* 三 "百十六万円と ... 三百六十万円を控除した金額の百分の二十";
* 四 "百七十六万円と ... 六百六十万円を控除した金額の百分の十";
* 五 "八百五十万円を超える場合 / 百九十五万円". -/
def kyuyoKojo10 (w : Int) : Int :=
  if w ≤ 1900000 then 6500000
  else if w ≤ 3600000 then 6500000 + 3 * (w - 1900000)
  else if w ≤ 6600000 then 11600000 + 2 * (w - 3600000)
  else if w ≤ 8500000 then 17600000 + (w - 6600000)
  else 19500000

/-- **第28条第2項**: "給与所得の金額は、その年中の給与等の収入金額から給与所得控除額を控除した残額とする" — a 残額,
never negative; a fraction of a yen is cut (NTA, 令和7年分 年末調整のしかた p.36: "１円未満の端数があるときは、これを
切り捨てた金額"; example 7,654,321 円 → 5,788,888 円). -/
def kyuyoFormula (w : Int) : Int := pos ((10 * w - kyuyoKojo10 w) / 10)

/-- **第28条第4項 and 別表第五**: "その年中の給与等の収入金額が六百六十万円未満である場合には、当該給与等に係る給与所得の
金額は、前二項の規定にかかわらず、当該収入金額を別表第五の給与等の金額として、同表により当該金額に応じて求めた同表の給与所得
控除後の給与等の金額に相当する金額とする." The table (別表第五, 令和7年法律第13号) has the rows
* "６５１，０００円未満" → 0;
* "６５１，０００ ～ １，９００，０００" → "給与等の金額から６５０，０００円を控除した金額";
* from 1,900,000 to 6,600,000 yen, rows 4,000 yen wide, each giving the 第3項 result at the row's lower end: 70 % of
  it less 80,000 yen up to 3,600,000, 80 % of it less 440,000 yen up to 6,600,000 (1,175 rows; `Beppyo5Data.lean`
  holds them as published and `beppyo5_eq_table` proves every one).
At and above 6,600,000 yen 第3項 applies directly. -/
def kyuyoShotoku (w : Int) : Int :=
  if w < 651000 then 0
  else if w < 1900000 then w - 650000
  else if w < 3600000 then w / 4000 * 2800 - 80000
  else if w < 6600000 then w / 4000 * 3200 - 440000
  else kyuyoFormula w

/-- A row (以上 `lo`, 未満 `hi`, value `v`) of 別表第五 agrees with `kyuyoShotoku` at its first and last yen and is
4,000 yen wide (checked for every published row in `Beppyo5Data.lean`). -/
def beppyo5RowOk (r : Int × Int × Int) : Bool :=
  kyuyoShotoku r.1 == r.2.2 && kyuyoShotoku (r.2.1 - 1) == r.2.2 && r.2.1 - r.1 == 4000

/-! ## 所得金額調整控除 (租税特別措置法第41条の3の11) -/

/-- **措置法第41条の3の11第1項**: for "給与等の収入金額が八百五十万円を超える居住者で、特別障害者に該当するもの又は年齢
二十三歳未満の扶養親族を有するもの若しくは特別障害者である同一生計配偶者若しくは扶養親族を有するもの": "その年中の給与等の
収入金額（当該給与等の収入金額が千万円を超える場合には、千万円）から八百五十万円を控除した金額の百分の十に相当する金額" comes
off the 給与所得. A fraction of a yen is rounded up (NTA, 年末調整のしかた 令和7年分 p.37: "その端数を切り上げます";
8,765,432 円 → 26,544 円). -/
def adjust1 (w : Int) (eligible : Bool) : Int :=
  if eligible && decide (w > 8500000) then cdiv (min w 10000000 - 8500000) 10 else 0

/-- **措置法第41条の3の11第2項**: a person with both 給与所得控除後の給与等の金額 `g` and 公的年金等に係る雑所得 `n`
whose sum exceeds 100,000 yen deducts "当該給与所得控除後の給与等の金額（...十万円を超える場合には、十万円）及び当該公的
年金等に係る雑所得の金額（...十万円を超える場合には、十万円）の合計額から十万円を控除した残額". -/
def adjust2 (g n : Int) : Int :=
  if g > 0 ∧ n > 0 then pos (min g 100000 + min n 100000 - 100000) else 0

/-! ## 公的年金等に係る雑所得 (所得税法第35条第4項; 措置法第41条の15の3) -/

/-- 第35条第4項第1号ロ: the slices of "公的年金等の収入金額から五十万円を控除した残額" `r`, in hundredths of a yen:
25 % up to 3,600,000 yen; 900,000 yen and 15 % to 7,200,000; 1,440,000 yen and 5 % to 9,500,000; then 1,555,000. -/
def nenkinSlice100 (p : Int) : Int :=
  let r := pos (p - 500000)
  if r ≤ 3600000 then 25 * r
  else if r ≤ 7200000 then 90000000 + 15 * (r - 3600000)
  else if r ≤ 9500000 then 144000000 + 5 * (r - 7200000)
  else 155500000

/-- **第35条第4項 / 措置法第41条の15の3第1項**: 公的年金等控除額, in hundredths of a yen. `other` is the
"公的年金等に係る雑所得以外の合計所得金額"; `over65` is "年齢が六十五歳以上である個人" on 31 December (同条第4項).
The fixed part (イ) is 400,000 / 300,000 / 200,000 yen for `other` up to 10 M / 20 M / above; the floor is
600,000 / 500,000 / 400,000 yen, and for those 65 or over "「六十万円」とあるのは「百十万円」..." 1,100,000 /
1,000,000 / 900,000 yen. -/
def nenkinKojo100 (p other : Int) (over65 : Bool) : Int :=
  let (fixed, floor) : Int × Int :=
    if other ≤ 10000000 then (400000, if over65 then 1100000 else 600000)
    else if other ≤ 20000000 then (300000, if over65 then 1000000 else 500000)
    else (200000, if over65 then 900000 else 400000)
  max (100 * floor) (100 * fixed + nenkinSlice100 p)

/-- **第35条第2項第1号**: "公的年金等の収入金額から公的年金等控除額を控除した残額", the fraction of a yen cut. -/
def nenkinZatsu (p other : Int) (over65 : Bool) : Int :=
  pos ((100 * p - nenkinKojo100 p other over65) / 100)

/-! ## Properties of the salary schedule -/

theorem kyuyoFormula_mono {a b : Int} (h : a ≤ b) : kyuyoFormula a ≤ kyuyoFormula b := by
  unfold kyuyoFormula kyuyoKojo10 pos
  split <;> split <;> omega

/-- **The 給与所得 is non-decreasing in the salary**, table and formula together. -/
theorem kyuyoShotoku_mono {a b : Int} (h : a ≤ b) : kyuyoShotoku a ≤ kyuyoShotoku b := by
  have hf := @kyuyoFormula_mono a b h
  unfold kyuyoShotoku
  have k6600 : kyuyoFormula 6600000 = 4840000 := by decide
  have hfa : 6600000 ≤ a → 4840000 ≤ kyuyoFormula a := fun ha => by
    have := @kyuyoFormula_mono 6600000 a ha; omega
  have hfb : 6600000 ≤ b → 4840000 ≤ kyuyoFormula b := fun hb => by
    have := @kyuyoFormula_mono 6600000 b hb; omega
  split <;> split <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;>
    (try split) <;> (try omega)
  all_goals (first | omega | (have := hfb (by omega); omega) | (have := hfa (by omega); omega))

theorem kyuyoShotoku_nonneg (w : Int) : 0 ≤ kyuyoShotoku w := by
  have := @kyuyoShotoku_mono 0 w
  by_cases h : 0 ≤ w
  · have := this h
    have h0 : kyuyoShotoku 0 = 0 := by decide
    omega
  · unfold kyuyoShotoku; split <;> omega

/-- The table never gives more 給与所得 than the formula of 第28条第3項: the 4,000-yen rows take the row's lower end. -/
theorem kyuyoShotoku_le_formula (w : Int) : kyuyoShotoku w ≤ kyuyoFormula w := by
  unfold kyuyoShotoku kyuyoFormula kyuyoKojo10 pos
  split <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;>
    (try split) <;> omega

/-- And at most one row's step less: below 3,600,000 yen the gap is under 2,800 yen (70 % of 4,000), from there to
6,600,000 under 3,200 yen. -/
theorem formula_sub_table_lt (w : Int) (h : 1900000 ≤ w) (h2 : w < 6600000) :
    kyuyoFormula w - kyuyoShotoku w < (if w < 3600000 then 2800 else 3200) := by
  unfold kyuyoShotoku kyuyoFormula kyuyoKojo10 pos
  split <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;>
    (try split) <;> omega


/-! ## 令和6年分 給与所得 (tests round 3)

第28条第3項 as in force for 令和6年分 (`law/shotokuzeiho_2024-12-31.xml`): "一 … 百八十万円以下である場合 当該収入金額の
百分の四十に相当する金額から十万円を控除した残額（当該残額が五十五万円に満たない場合には、五十五万円） 二 … 三百六十万円以下 …
六十二万円と … 百分の三十 … 三 … 百十六万円と … 百分の二十 … 四 … 百七十六万円と … 百分の十 … 五 … 百九十五万円";
第4項 and 別表第五 of that version (`scripts/b5_2024.py`): "５５１，０００ – １，６１９，０００ 給与等の金額から５５０，０００円を
控除した金額", then the rows (1,619,000, 1,620,000) 1,069,000; (1,620,000, 1,622,000) 1,070,000; (1,622,000, 1,624,000)
1,072,000; (1,624,000, 1,628,000) 1,074,000; from 1,628,000 rows 4,000 yen wide valued 60 % of the lower end + 100,000
up to 1,800,000, then 70 % − 80,000 and 80 % − 440,000 — the 1,175 rows from 1,900,000 are identical to the 令和7年分
table (checked by the script). -/

def kyuyoShotoku2024 (w : Int) : Int :=
  if w < 551000 then 0
  else if w < 1619000 then w - 550000
  else if w < 1620000 then 1069000
  else if w < 1622000 then 1070000
  else if w < 1624000 then 1072000
  else if w < 1628000 then 1074000
  else if w < 1800000 then w / 4000 * 2400 + 100000
  else if w < 3600000 then w / 4000 * 2800 - 80000
  else kyuyoShotoku w

def kyuyoShotokuY (y w : Int) : Int := if 2020 ≤ y ∧ y ≤ 2024 then kyuyoShotoku2024 w else kyuyoShotoku w

/-- `--oecd` for 令和6年分: the 第28条第3項 formula of that year (55 万 minimum, 40 % − 10 万 to 1,800,000). -/
def kyuyoFormula2024 (w : Int) : Int :=
  if w ≤ 1800000 then pos (w - max 550000 (w * 4 / 10 - 100000)) else kyuyoFormula w

theorem kyuyo2024_rows : kyuyoShotoku2024 1628000 = 1076800 ∧ kyuyoShotoku2024 1896000 = 1247200 ∧
    kyuyoShotoku2024 1900000 = 1250000 ∧ kyuyoShotoku2024 1799999 = 1177600 ∧ kyuyoShotoku2024 3600000 = kyuyoShotoku 3600000 := by decide

end JpTax
