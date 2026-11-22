import JpTax.Basic

/-!
# 児童手当 (児童手当法, as amended by 令和6年法律第47号 from October 2024)

Monthly amounts (第6条第3項): "三歳未満児童算定額は一万五千円とし、三歳以上児童算定額は一万円とし、第三子以降算定額は
三万円とする". No income limit (the 所得制限 was abolished from October 2024). A 児童 is one "十八歳に達する日以後の最初の
三月三十一日までの間にある者" (第3条第1項); for the birth order, children up to "二十二歳に達する日以後の最初の三月三十一日"
whom the parent supports also count (第6条第2項第2号, 第三子以降算定額算定対象者).

Convention: a child's age is its age on 31 December 2025 and is taken as its age all year; children aged 0–18 are
支給対象児童, those aged 19–22 count for the order only (they are taken to be supported by the parents). The yearly
amount is 12 months of the monthly amount.
-/

namespace JpTax

/-- **第6条第1項第1号, the table**, by the counts `a` (第三子以降算定額算定対象者: 19–22), `b` (三歳以上支給対象児童) and
`c` (三歳未満支給対象児童). Each row copied from the statute. -/
def teateTable (a b c : Nat) : Int :=
  let u : Int := 15000   -- 三歳未満児童算定額
  let o : Int := 10000   -- 三歳以上児童算定額
  let t : Int := 30000   -- 第三子以降算定額
  if a = 0 then
    if b = 0 then
      (if c = 0 then 0 else if c = 1 then u else u * 2 + t * ((c : Int) - 2))
    else if b = 1 then
      (if c = 0 then o else o + u + t * ((c : Int) - 1))
    else o * 2 + t * ((b : Int) - 2) + t * c
  else if a = 1 then
    if b = 0 then (if c = 0 then 0 else u + t * ((c : Int) - 1))
    else o + t * ((b : Int) - 1) + t * c
  else t * ((b : Int) + c)

/-- The same rule written as birth order: rank the counted children from the oldest; the first two ranks get 10,000
yen (aged 3–18) or 15,000 yen (under 3), the third and later 30,000 yen; ranks held by 19–22-year-olds pay nothing. -/
def teateRank (a b c : Nat) : Int :=
  let bLow : Int := max 0 (min (b : Int) (2 - (a : Int)))
  let cLow : Int := max 0 (min (c : Int) (2 - (a : Int) - (b : Int)))
  10000 * bLow + 30000 * ((b : Int) - bLow) + 15000 * cLow + 30000 * ((c : Int) - cLow)

/-- **The statute's table is the birth-order rule**, for every family. -/
theorem teateTable_eq_rank (a b c : Nat) : teateTable a b c = teateRank a b c := by
  unfold teateTable teateRank
  by_cases ha0 : a = 0
  · subst ha0
    by_cases hb0 : b = 0
    · subst hb0
      by_cases hc0 : c = 0
      · subst hc0; decide
      · by_cases hc1 : c = 1
        · subst hc1; decide
        · simp only [hc0, hc1, ite_false, ite_true]; omega
    · by_cases hb1 : b = 1
      · subst hb1
        by_cases hc0 : c = 0
        · subst hc0; decide
        · simp only [hc0, ite_false, ite_true]; omega
      · simp only [hb0, hb1, ite_false, ite_true]; omega
  · by_cases ha1 : a = 1
    · subst ha1
      by_cases hb0 : b = 0
      · subst hb0
        by_cases hc0 : c = 0
        · subst hc0; decide
        · simp only [hc0, ite_false, ite_true]; omega
      · simp only [hb0, ite_false, ite_true]; omega
    · simp only [ha0, ha1, ite_false]; omega

/-- Monthly amount for children of the given ages (31 December 2025). -/
def teateMonthly (ages : List Int) : Int :=
  let a := (ages.filter (fun x => decide (19 ≤ x ∧ x ≤ 22))).length
  let b := (ages.filter (fun x => decide (3 ≤ x ∧ x ≤ 18))).length
  let c := (ages.filter (fun x => decide (0 ≤ x ∧ x < 3))).length
  teateTable a b c

/-- 児童手当 for 2025: twelve months (第8条第4項 pays them in six instalments). -/
def teateYear (ages : List Int) : Int := 12 * teateMonthly ages

/-! ## 児童扶養手当 (児童扶養手当法, 昭和36年法律第238号, as amended by 令和6年法律第47号 from 2024-11-01)

Added in tests round 1 (`cmp20/improve-emerging/IMPROVE.md`; the OECD counts it). Texts: e-Gov 法令API v2,
`law/fuyoteate_2025-04-01.xml` (法, revision 20241101) and `law/fuyoteate_rei_2025-01-01.xml` /
`law/fuyoteate_rei_2025-04-01.xml` (施行令, 昭和36年政令第405号, revisions 20241101 (令和6年政令第259号) and 20250401
(令和7年政令第82号)).

* 法第5条第1項: "その額は、一月につき、四万千百円とする", read by 施行令第2条の2 as "四万五千五百円" for the months from
  April 2024 and "四万六千六百九十円" from April 2025; 第2項: "監護等児童のうちの一人以外の監護等児童につきそれぞれ一万七百五十円を
  加算", read as "一万千三十円" from April 2025.
* 法第9条第1項: not paid, wholly or partly, when "前年の所得が ... 政令で定める額以上であるとき", from November to the next
  October. 施行令第2条の4第1項: 690,000 yen plus 380,000 for each 加算対象扶養親族等 (530,000 for a 特定扶養親族等: a
  特定扶養親族 or a 控除対象扶養親族 under 19); 第2項第1号: nothing is paid from 2,080,000 yen plus the same additions;
  第2項第2号: otherwise the 基本額一部支給停止額 plus (監護等児童 − 1) × the 加算額一部支給停止額 is withheld; 第3項・第4項:
  each is the excess over the 第1項 amount times "〇・〇二五" and "〇・〇〇三八五六一" (version 20241101) or "〇・〇二五六六一九" and
  "〇・〇〇三九五六八" (from April 2025), "五円未満の端数があるときはこれを切り捨てるものとし、五円以上十円未満の端数があるときは
  これを十円に切り上げる", "に十円を加えて得た額".
* 施行令第4条第1項: the 所得 is the 住民税 総所得金額 with the 給与所得 (and public-pension 雑所得) reduced by 100,000 yen
  ("十万円を控除して得た金額（当該金額が零を下回る場合には、零とする。）"), less 80,000 yen ("八万円を控除した額").

Conventions (stated): the claimant is the unmarried single adult of a household with a child (the household's
`single`, as for the ひとり親控除), a mother unless `jpSingleParentSex` is "M" (both are eligible, 法第4条); 監護等児童 are the
children aged 18 or less on 31 December 2025 (法第3条第1項, as for 児童手当); "前年の所得" is taken to equal the 2025 income
(the contract has one year; 2025's months use the 2023 income until October and the 2024 income from November); paid
for all 12 months, with January–March 2025 under the version 20241101 amounts and April–December under the version
20250401 ones; no maintenance received from the other parent (施行令第4条第1項ただし書), no 法第13条の3 halving, no
public pension (法第13条の2). -/

/-- One fiscal year's amounts: 基本額, 加算額, and the two 施行令第2条の4第3項・第4項 coefficients in units of 10⁻⁷. -/
structure FuyoParams where
  base : Int
  add : Int
  kBase : Int
  kAdd : Int
  /-- 第二加算額 (third and later child) and its coefficient; the 全部支給 and 支給停止 base limits (施行令第2条の4第1項,
  第2項第1号) — before November 2024 a third child had its own smaller amount and the limits were 490,000 / 1,920,000. -/
  add2 : Int
  kAdd2 : Int
  full0 : Int
  stop0 : Int
  deriving Repr

/-- January–March 2025 (施行令 version 20241101): "四万五千五百円", 法 "一万七百五十円", "〇・〇二五", "〇・〇〇三八五六一". -/
def fuyoFY2024 : FuyoParams :=
  { base := 45500, add := 10750, kBase := 250000, kAdd := 38561, add2 := 10750, kAdd2 := 38561, full0 := 690000,
    stop0 := 2080000 }
/-- April–December 2025 (施行令 version 20250401): "四万六千六百九十円", "一万千三十円", "〇・〇二五六六一九",
"〇・〇〇三九五六八". -/
def fuyoFY2025 : FuyoParams :=
  { base := 46690, add := 11030, kBase := 256619, kAdd := 39568, add2 := 11030, kAdd2 := 39568, full0 := 690000,
    stop0 := 2080000 }

/-- January–March 2024 (施行令 version 20230401, `law/fuyoteate_rei_2024-01-01.xml`): "四万四千百四十円", 第一加算額
"一万四百二十円", 第二加算額 "六千二百五十円"; coefficients "〇・〇二三五八〇四", "〇・〇〇三六三六四", "〇・〇〇二一七四八"; limits
"四十九万円" (+ 380,000 a dependant) and "一、九二〇、〇〇〇円" (+ 380,000). -/
def fuyoFY2023 : FuyoParams :=
  { base := 44140, add := 10420, kBase := 235804, kAdd := 36364, add2 := 6250, kAdd2 := 21748, full0 := 490000,
    stop0 := 1920000 }

/-- January–March 2022 (施行令 version in force 2022-01-01, `law/fuyoteate_rei_2022-01-01.xml`): "四万三千百六十円", "一万百九十円",
"六千百十円"; "〇・〇二三〇五五九", "〇・〇〇三五五二四", "〇・〇〇二一二五九"; limits 49万 / 192万. -/
def fuyoFY2021 : FuyoParams :=
  { base := 43160, add := 10190, kBase := 230559, kAdd := 35524, add2 := 6110, kAdd2 := 21259, full0 := 490000,
    stop0 := 1920000 }

/-- April 2022 – March 2023 (version 2022-04-01): "四万三千七十円", "一万百七十円", "六千百円"; "〇・〇二三〇〇七〇",
"〇・〇〇三五四五五", "〇・〇〇二一二五九". -/
def fuyoFY2022 : FuyoParams :=
  { base := 43070, add := 10170, kBase := 230070, kAdd := 35455, add2 := 6100, kAdd2 := 21259, full0 := 490000,
    stop0 := 1920000 }

/-- April–October 2024 (施行令 version 20240401, `law/fuyoteate_rei_2024-04-01.xml`): "四万五千五百円", "一万七百五十円",
"六千四百五十円"; "〇・〇二四三〇〇七", "〇・〇〇三七四八三", "〇・〇〇二二四四八"; the same limits. November–December 2024: the
version 20241101 (`fuyoFY2024`). -/
def fuyoFY2024old : FuyoParams :=
  { base := 45500, add := 10750, kBase := 243007, kAdd := 37483, add2 := 6450, kAdd2 := 22448, full0 := 490000,
    stop0 := 1920000 }

/-- 施行令第2条の4第3項・第4項: the excess `x` times the coefficient `k` (10⁻⁷), to the ten yen (five yen and more up), plus
ten yen. -/
def fuyoStop (x k : Int) : Int := (x * k + 50000000) / 100000000 * 10 + 10

/-- 施行令第2条の4第1項 / 第2項第1号 additions for one 加算対象扶養親族等 aged `a` (children only here). -/
def fuyoAddFor (a : Int) : Int := if 16 ≤ a ∧ a < 23 then 530000 else 380000

def fuyoDepAdd (deps : List Int) : Int := (deps.map fuyoAddFor).foldl (· + ·) 0

/-- One month's 児童扶養手当 for `n` 監護等児童, 所得 `s`, the ages `deps` of the 加算対象扶養親族等. -/
def fuyoMonthly (p : FuyoParams) (n : Nat) (s : Int) (deps : List Int) : Int :=
  if n = 0 then 0 else
  let full := p.full0 + fuyoDepAdd deps
  if s ≥ p.stop0 + fuyoDepAdd deps then 0
  else if s < full then p.base + (if n ≥ 2 then p.add else 0) + p.add2 * ((n : Int) - 2).toNat
  else pos (p.base - fuyoStop (s - full) p.kBase) + (if n ≥ 2 then pos (p.add - fuyoStop (s - full) p.kAdd) else 0)
    + ((n : Int) - 2).toNat * pos (p.add2 - fuyoStop (s - full) p.kAdd2)

/-- 施行令第4条第1項: the 所得 from the 総所得金額 `sogo`, of which `kyuyoNenkin` is 給与所得 + public-pension 雑所得 as they
enter the 総所得金額 and `kyuyoNenkinRaw` the same before the 所得金額調整控除 (第28条第2項, 第35条第2項第1号 amounts). -/
def fuyoShotoku (sogo kyuyoNenkin kyuyoNenkinRaw : Int) : Int :=
  pos (sogo - kyuyoNenkin + pos (kyuyoNenkinRaw - 100000) - 80000)

/-- 児童扶養手当 for 2025: three months at the version 20241101 amounts, nine at the version 20250401 ones. -/
def fuyoYear (n : Nat) (s : Int) (deps : List Int) : Int :=
  3 * fuyoMonthly fuyoFY2024 n s deps + 9 * fuyoMonthly fuyoFY2025 n s deps

/-- The OECD's SP67 single parent (wage 3,821,036 yen, 給与所得 2,616,000 by 別表第五, two children under 16): 所得
2,436,000 yen, 986,000 above the 1,450,000 limit; 27,780 yen a month to March (20,840 + 6,940) and 28,500 from April
(21,380 + 7,120): 339,840 yen for 2025. -/
theorem fuyo_sp67 : fuyoYear 2 (fuyoShotoku 2616000 2616000 2616000) [11, 6] = 339840 := by decide


/-- 児童扶養手当 for 2024: January–March at the 20230401 version, April–October at 20240401, November–December at
20241101 (法第9条: "その年の十一月から翌年の十月まで" with the 20241101 limits). -/
def fuyoYearY (y : Int) (n : Nat) (s : Int) (deps : List Int) : Int :=
  if y = 2022 then 3 * fuyoMonthly fuyoFY2021 n s deps + 9 * fuyoMonthly fuyoFY2022 n s deps
  else if y = 2023 then 3 * fuyoMonthly fuyoFY2022 n s deps + 9 * fuyoMonthly fuyoFY2023 n s deps
  else if y = 2024 then 3 * fuyoMonthly fuyoFY2023 n s deps + 7 * fuyoMonthly fuyoFY2024old n s deps
    + 2 * fuyoMonthly fuyoFY2024 n s deps
  else fuyoYear n s deps

/-! ## 児童手当 for 2024 (tests round 3)

January–September 2024: 児童手当法 as in force 2024-09-01 (revision 20240612, `law/jidoteate_2024-09-01.xml`) 第6条第1項
第1号: 15,000 yen a month for a child under 3, 10,000 for a child from 3 to the end of primary school (15,000 for the third
and later 支給要件児童), 10,000 in lower secondary school; 第5条第1項 with 施行令 (`law/jidoteate_rei_2024-09-01.xml`) 第1条:
not paid when the 所得 is "六百二十二万円 … に当該扶養親族等 … 又は児童一人につき三十八万円を加算した額" or more; then
法附則第2条 (特例給付) "五千円" per child up to the end of lower secondary school while the 所得 is under 施行令第7条
"八百五十八万円" + 380,000 a person; 所得 = 総所得金額 less "八万円" (施行令第3条). October–December 2024: the reformed law
above (`teateMonthly`). Conventions: ages on 31 December 2024 (to 12: primary, 13–15: lower secondary, birth order among
children up to 18), the 所得 of the higher earner equal to the 2024 income, the claimant's 扶養親族等 = the children and a
同一生計配偶者. -/

def teateOldMonthly (ages : List Int) (shotoku deps : Int) (upper : Bool := true) : Int :=
  let kids := ages.filter (fun a => decide (0 ≤ a ∧ a ≤ 18))
  -- birth order among the 支給要件児童: older children first, equal ages by list position
  let rank (a : Int) (idx : Nat) : Nat := (kids.filter (fun b => decide (b > a))).length + ((kids.take idx).filter (fun b => decide (b = a))).length
  let ranked := kids.zipIdx.map (fun (a, idx) => (a, rank a idx))
  let full : Int := (ranked.map fun (a, i) => (
    if a < 3 then 15000 else if a ≤ 12 then (if i ≥ 2 then 15000 else 10000) else if a ≤ 15 then 10000 else 0 : Int)).foldl (· + ·) 0
  let under15 : Int := ((ages.filter (fun a => decide (0 ≤ a ∧ a ≤ 15))).length : Int)
  if shotoku < 6220000 + 380000 * deps then full
  else if !upper ∨ shotoku < 8580000 + 380000 * deps then 5000 * under15
  else 0

def teateYearY (y : Int) (ages : List Int) (shotoku deps : Int) : Int :=
  if y = 2024 then 9 * teateOldMonthly ages shotoku deps + 3 * teateMonthly ages
  -- 2022 (round 6): the 特例給付 had no upper income limit until May 2022 (法附則第2条 as of 2022-05-01,
  -- `law/jidoteate_2022-05-01.xml`: "第五条第一項の規定により児童手当が支給されない者に限る"); the 2022-12-31 version adds
  -- "政令で定める額未満であるものに限る" (施行令第7条 "八百五十八万円"), taken from June 2022
  else if y = 2022 then 5 * teateOldMonthly ages shotoku deps false + 7 * teateOldMonthly ages shotoku deps
  else if y = 2023 then 12 * teateOldMonthly ages shotoku deps
  else teateYear ages

theorem teate2024_example : teateYearY 2024 [6, 11] 4000000 3 = 9 * 20000 + 3 * 20000 := by decide

end JpTax
