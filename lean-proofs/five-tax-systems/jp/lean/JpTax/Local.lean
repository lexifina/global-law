import JpTax.Tax

/-!
# 個人住民税 (地方税法): 所得割, 調整控除, 均等割, 森林環境税

The 住民税 on 2025 income is the 令和8年度 tax, assessed in 2026 on "前年の所得" (地方税法第32条第1項, 第313条第1項)
and paid from June 2026 (special collection from pay) — computed here on 2025 income, under 地方税法 as in force for
令和8年度 (e-Gov revision 325AC0000000226_20260525_506AC0000000052, text as of 2026-06-01). A resident of Tokyo's 23
special wards pays 都民税 (道府県民税, 第23条 ff., applied to 都 by 第734条) and 特別区民税 (市町村民税, 第292条 ff.) at
the standard rates (標準税率): 所得割 4 % + 6 %, 均等割 1,000 + 3,000 yen; with 森林環境税 1,000 yen (森林環境税及び
森林環境譲与税に関する法律第5条), a national tax assessed and collected with the 均等割 (同法第7条).

Income is computed "所得税法...の計算の例により" (第32条第2項, 第313条第2項), so the 総所得金額 and 合計所得金額 are those
of the income tax; the deductions and their amounts are the local tax's own (第34条, 第314条の2).
-/

namespace JpTax

/-! ## 所得控除 (第34条 / 第314条の2) -/

/-- **第314条の2第2項**: 基礎控除 430,000 yen up to a 合計所得金額 of 24,000,000 yen, 290,000 to 24,500,000, 150,000 to
25,000,000 ("前年の合計所得金額が二千五百万円以下である所得割の納税義務者"); unchanged by the 令和7年度 reform. -/
def kisoLocal (g : Int) : Int :=
  if g ≤ 24000000 then 430000
  else if g ≤ 24500000 then 290000
  else if g ≤ 25000000 then 150000
  else 0

/-- **第314条の2第1項第10号**: 配偶者控除 330,000 yen (老人控除対象配偶者 380,000) up to 9,000,000 yen of the claimant's
合計所得金額, 220,000 (260,000) to 9,500,000, 110,000 (130,000) to 10,000,000. 同一生計配偶者 (第292条第1項第7号):
"前年の合計所得金額が五十八万円以下". -/
def haigushaLocal (g s : Int) (spouseOld : Bool) : Int :=
  if s ≤ douitsuLimit ∧ g ≤ 10000000 then
    if g ≤ 9000000 then (if spouseOld then 380000 else 330000)
    else if g ≤ 9500000 then (if spouseOld then 260000 else 220000)
    else (if spouseOld then 130000 else 110000)
  else 0

/-- **第314条の2第1項第10号の2イ**: "（１）前年の合計所得金額が百万円以下である配偶者 / 三十三万円"; "（２）百万円を超え
百三十万円以下 / 三十八万円から...九十三万一円を超える部分の金額（...）を控除した金額"; "（３）百三十万円を超える配偶者 /
三万円". -/
def tokubetsuBaseLocal (s : Int) : Int :=
  if s ≤ 1000000 then 330000
  else if s ≤ 1300000 then 380000 - step5 (s - 930001)
  else 30000

/-- **第314条の2第1項第10号の2**: 配偶者特別控除 (住民税), the ロ and ハ fractions "一万円未満の端数がある場合には、これを
切り上げた金額". -/
def tokubetsuLocal (g s : Int) : Int :=
  if douitsuLimit < s ∧ s ≤ 1330000 ∧ g ≤ 10000000 then
    let b := tokubetsuBaseLocal s
    if g ≤ 9000000 then b
    else if g ≤ 9500000 then cdiv (2 * b) 30000 * 10000
    else cdiv b 30000 * 10000
  else 0

/-- **第314条の2第1項第11号**: 扶養控除 "各控除対象扶養親族につき三十三万円（その者が特定扶養親族である場合には四十五万円、
その者が老人扶養親族である場合には三十八万円）". -/
def fuyoLocal (d : Relative) : Int :=
  if d.kojoTaisho then (if d.tokutei then 450000 else if d.rojin then 380000 else 330000) else 0

/-- **第314条の2第1項第12号**: 特定親族特別控除 (住民税): "イ 前年の合計所得金額が九十五万円以下である特定親族 / 四十五万円";
ロ to 1,150,000 the same formula as the income tax; ハ 60,000; ニ 30,000. -/
def tokuteiShinzokuLocal (d : Relative) : Int :=
  if 19 ≤ d.age ∧ d.age < 23 ∧ 580000 < d.income ∧ d.income ≤ 1230000 then
    if d.income ≤ 950000 then 450000
    else if d.income ≤ 1150000 then 630000 - step10 (2 * (d.income - 840001))
    else if d.income ≤ 1200000 then 60000
    else 30000
  else 0

/-- **第314条の2第1項第8号の2**: ひとり親控除 300,000 yen. -/
def hitorioyaLocal (single : Bool) (g : Int) : Int := if single && decide (g ≤ 5000000) then 300000 else 0

/-! ## 調整控除 (第37条 / 第314条の6) -/

/-- Who the taxpayer is, for the table of 第37条第1号イ / 第314条の6第1号イ ("人的控除額の差"). -/
structure ChoseiFacts where
  g : Int                  -- 合計所得金額
  spouseKojo : Bool        -- has a 控除対象配偶者
  spouseOld : Bool         -- ... who is a 老人控除対象配偶者
  spouseSpecialIncome : Option Int  -- a 配偶者特別控除 spouse and that spouse's 合計所得金額
  fuyoIppan : Int          -- 控除対象扶養親族 other than 特定 and 老人
  fuyoTokutei : Int
  fuyoRojin : Int
  hitorioyaFather : Bool   -- (3): "ひとり親で政令で定めるもの" = 父 (施行令第7条の16の2第1項, 第48条の7の2第1項)
  hitorioyaMother : Bool   -- (4): 母 (同条第2項)
  deriving Repr, Inhabited

/-- The sum of the table's amounts, with the base 50,000 yen ("五万円に...を合算した金額を加算した金額"). Rows (6)
控除対象配偶者 5万 (4万 over 9,000,000, 2万 over 9,500,000) or 10万 (6万, 3万) for an older spouse; (7) a 配偶者特別控除
spouse "前年の合計所得金額が五十五万円未満である者に限る": 5万 (4万, 2万), or 3万 (2万, 1万) from 50万; (8) 一般 5万,
特定 18万, 老人 10万; (3) ひとり親 (父) 1万; (4) ひとり親 (母) 5万. Rows (1), (2), (5), (9) (disability, students,
co-resident parents) are not modelled. -/
def choseiH (f : ChoseiFacts) : Int :=
  let tier : Int → Int → Int → Int := fun a b c =>
    if f.g ≤ 9000000 then a else if f.g ≤ 9500000 then b else c
  let spouse : Int :=
    if f.spouseKojo then (if f.spouseOld then tier 100000 60000 30000 else tier 50000 40000 20000)
    else match f.spouseSpecialIncome with
      | some s => if s < 550000 ∧ f.g ≤ 10000000 then
                    (if s ≥ 500000 then tier 30000 20000 10000 else tier 50000 40000 20000)
                  else 0
      | none => 0
  50000 + spouse + 50000 * f.fuyoIppan + 180000 * f.fuyoTokutei + 100000 * f.fuyoRojin +
    (if f.hitorioyaFather then 10000 else 0) + (if f.hitorioyaMother then 50000 else 0)

/-- **第37条 (2 %) / 第314条の6 (3 %)**, in hundredths of the rate base: "合計課税所得金額が二百万円以下である場合 / 次に
掲げる金額のうちいずれか少ない金額" (イ the table sum, ロ the 合計課税所得金額); "二百万円を超える場合 / イに掲げる金額から
ロ（合計課税所得金額から二百万円を控除した金額）を控除した金額（当該金額が五万円を下回る場合には、五万円とする。）". Only
for "前年の合計所得金額が二千五百万円以下". Returns the base to which 2 % and 3 % apply. -/
def choseiBase (f : ChoseiFacts) (taxable : Int) : Int :=
  if f.g > 25000000 then 0
  else if taxable ≤ 2000000 then min (choseiH f) (pos taxable)
  else max 50000 (choseiH f - (taxable - 2000000))

/-! ## 非課税 (第24条の5, 第295条; 附則第3条の3; 施行令第47条の3) -/

/-- **附則第3条の3第1項, 第4項** (所得割の非課税): "三十五万円にその者の同一生計配偶者及び扶養親族（年齢十六歳未満の者及び
...控除対象扶養親族に限る。）の数に一を加えた数を乗じて得た金額に十万円を加算した金額（その者が同一生計配偶者又は扶養親族を
有する場合には、当該金額に三十二万円を加算した金額）". -/
def shotokuwariLimit (n : Int) : Int := 350000 * (n + 1) + 100000 + (if n > 0 then 320000 else 0)

/-- **第295条第3項, 施行令第47条の3** (均等割の非課税): the ward's ordinance amount, "基本額" at most 350,000 yen times
(dependants + 1), plus 100,000, plus a "加算額" of at most 210,000 when there are dependants, each scaled by the
生活保護 級地 rate. Tokyo's special wards are 1級地 (rate 1): 350,000 / 210,000, the standard every ward adopts. -/
def kintowariLimit (n : Int) : Int := 350000 * (n + 1) + 100000 + (if n > 0 then 210000 else 0)

/-! ## The local tax of one person -/

structure LocalIn where
  sogo : Int              -- 総所得金額 (= 合計所得金額 here)
  social : Int            -- 社会保険料
  ideco : Int             -- 小規模企業共済等掛金
  personal : Int          -- the personal deductions (配偶者, 扶養, 特定親族, ひとり親) of 第314条の2
  chosei : ChoseiFacts
  n : Int                 -- dependants counted for 非課税 (同一生計配偶者 + 扶養親族 incl. under 16)
  exempt295 : Bool        -- 第295条第1項第2号: ひとり親 (or 寡婦, 障害者, 未成年者) with 合計所得金額 ≤ 1,350,000
  haito : Int             -- dividends taxed with the other income (総合課税), else 0
  declDividends : Int := 0  -- listed-share dividends declared separately (附則第33条の2)
  declGains : Int := 0      -- listed-share gains declared separately (附則第35条の2の2)
  deriving Repr, Inhabited

structure LocalOut where
  deductions : Int
  base : Int              -- 課税総所得金額 (cut to 1,000 yen)
  prefRaw : Int           -- 4 %
  muniRaw : Int           -- 6 %
  choseiPref : Int
  choseiMuni : Int
  sepBase : Int           -- 上場株式等に係る課税譲渡所得等 + 課税配当所得等 (separately declared, after deductions)
  haitoPref1000 : Int     -- 配当控除 (附則第5条), thousandths of a yen (exact)
  haitoMuni1000 : Int
  pref : Int              -- 都民税 所得割, final (cut to 100 yen)
  muni : Int              -- 特別区民税 所得割, final
  kintoPref : Int         -- 均等割 1,000
  kintoMuni : Int         -- 均等割 3,000
  shinrin : Int           -- 森林環境税 1,000
  deriving Repr, Inhabited

/-- **附則第5条第1項, 第3項** (配当控除, 住民税), in thousandths of a yen, exactly: 道府県民税 1.2 %, 市町村民税 1.6 % of the
dividends (the part above 10,000,000 yen of 課税総所得金額: 0.6 % and 0.8 %). -/
def haitoLocal1000 (t d : Int) (pref : Bool) : Int :=
  let d := pos d
  let (hi, lo) : Int × Int := if pref then (12, 6) else (16, 8)
  let over := if t > 10000000 then min d (t - 10000000) else 0
  hi * (d - over) + lo * over

/-- The 所得割 left after the relief of 附則第3条の3第2項・第5項, in yen (floor), computed exactly: `x` and `tot` are the
two 所得割 in thousandths of a yen, `excess` the amount by which the 非課税 limit exceeds 総所得金額等 less the 所得割. The
relief is "当該超える金額に第二号に掲げる額を同号に掲げる額と第三号に掲げる額との合計額で除して得た数値を乗じて得た金額". -/
def afterRelief (x tot excess : Int) : Int :=
  if excess > 0 ∧ tot > 0 then pos (x * tot - excess * x) / (tot * 1000) else pos x / 1000

def localTax (i : LocalIn) : LocalOut :=
  -- 合計所得金額 and 総所得金額等 include the separately declared listed-share income (附則第33条の2第3項第1号・第5号)
  let decl := pos i.declDividends + pos i.declGains
  let g := i.sogo + decl
  let ded := i.social + i.ideco + i.personal + kisoLocal g
  let base := trunc1000 (i.sogo - ded)
  -- deductions left over after the 総所得金額 come off the separately declared amounts (附則第33条の2第3項第3号: "「総所得
  -- 金額」とあるのは、「総所得金額、...上場株式等に係る配当所得等の金額」"); gains first, as on the 申告書 第三表
  let left := pos (ded - i.sogo)
  let sGain := trunc1000 (pos i.declGains - left)
  let sDiv := trunc1000 (pos i.declDividends - pos (left - pos i.declGains))
  -- 附則第33条の2第1項・第5項 (and 附則第35条の2の2 for gains): 2 % (道府県) and 3 % (市町村) of the separate amounts
  let prefRaw := base * 4 / 100 + (sGain + sDiv) * 2 / 100
  let muniRaw := base * 6 / 100 + (sGain + sDiv) * 3 / 100
  -- 調整控除 (第37条, read by 附則第33条の2第3項第4号) on the 合計課税所得金額 of the ordinary income, from the whole 所得割
  let cb := choseiBase i.chosei base
  let cPref := min prefRaw (cb * 2 / 100)
  let cMuni := min muniRaw (cb * 3 / 100)
  -- 附則第5条 (配当控除): the 1,000万 test on 課税総所得金額 plus 課税配当所得等 (附則第33条の2第3項第4号)
  let hPref := min (haitoLocal1000 (base + sDiv) i.haito true) (1000 * (prefRaw - cPref))
  let hMuni := min (haitoLocal1000 (base + sDiv) i.haito false) (1000 * (muniRaw - cMuni))
  -- 所得割 after 第35条・第37条 (and 附則第5条), in thousandths of a yen
  let p := 1000 * (prefRaw - cPref) - hPref
  let m := 1000 * (muniRaw - cMuni) - hMuni
  -- 附則第3条の3第2項・第5項: when 総所得金額等 − 所得割 would fall under the 非課税 limit, the excess comes off,
  -- shared in proportion to the two 所得割.
  let limit := shotokuwariLimit i.n
  let tot := p + m
  let excess := 1000 * limit - (1000 * g - tot)
  let notTaxed := i.exempt295 || decide (g ≤ limit)
  let pref := if notTaxed then 0 else trunc100 (afterRelief p tot excess)
  let muni := if notTaxed then 0 else trunc100 (afterRelief m tot excess)
  let kinto := !(i.exempt295 || decide (g ≤ kintowariLimit i.n))
  { deductions := ded, base, prefRaw, muniRaw, choseiPref := cPref, choseiMuni := cMuni,
    sepBase := sGain + sDiv, haitoPref1000 := hPref, haitoMuni1000 := hMuni,
    pref, muni,
    kintoPref := if kinto then 1000 else 0, kintoMuni := if kinto then 3000 else 0,
    shinrin := if kinto then 1000 else 0 }

def LocalOut.total (o : LocalOut) : Int := o.pref + o.muni + o.kintoPref + o.kintoMuni + o.shinrin

/-! ## Facts -/

/-- **Row (7) of the 調整控除 table is dead text from 令和8年度.** It applies to a spouse of the 配偶者特別控除 "前年の合計
所得金額が五十五万円未満である者に限る", but since 令和7年法律第13号 the 配偶者特別控除 needs a spouse who is not a
同一生計配偶者, i.e. has more than 580,000 yen (第292条第1項第7号, 第314条の2第1項第10号の2). No spouse satisfies both: the
row was written for the 380,000 / 480,000 yen thresholds and was not moved with them. -/
theorem chosei_row7_dead (s : Int) (h : tokubetsuLocal 0 s ≠ 0) : ¬ s < 550000 := by
  unfold tokubetsuLocal douitsuLimit at h
  intro hs
  have : ¬ (580000 < s ∧ s ≤ 1330000 ∧ (0:Int) ≤ 10000000) := by omega
  simp only [this, ite_false] at h
  exact h rfl

/-- The final 所得割 is never negative. -/
theorem localTax_pref_nonneg (i : LocalIn) : 0 ≤ (localTax i).pref := by
  unfold localTax
  simp only []
  split
  · exact Int.le_refl 0
  · exact trunc100_nonneg _

end JpTax
