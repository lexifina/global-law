import JpTax.Deductions

/-!
# The rate (所得税法第89条), 配当控除 (第92条), 復興特別所得税

Amounts in hundredths of a yen where the statute's percentages need them; the 課税総所得金額 is a multiple of
1,000 yen (国税通則法第118条第1項), so the tax on it is always a whole number of yen.
-/

namespace JpTax

/-- One slice of 第89条第1項: `rate` per cent of the part of `t` above `lo` and up to `hi`, in hundredths of a yen. -/
def slice (rate lo hi t : Int) : Int := rate * pos (min t hi - lo)

/-- **第89条第1項**: "課税総所得金額...をそれぞれ次の表の上欄に掲げる金額に区分してそれぞれの金額に同表の下欄に掲げる
税率を乗じて計算した金額を合計した金額":
百九十五万円以下 5 %; 百九十五万円を超え三百三十万円以下 10 %; 三百三十万円を超え六百九十五万円以下 20 %;
六百九十五万円を超え九百万円以下 23 %; 九百万円を超え千八百万円以下 33 %; 千八百万円を超え四千万円以下 40 %;
四千万円を超える金額 45 %. In hundredths of a yen. -/
def tax89c (t : Int) : Int :=
  slice 5 0 1950000 t + slice 10 1950000 3300000 t + slice 20 3300000 6950000 t +
  slice 23 6950000 9000000 t + slice 33 9000000 18000000 t + slice 40 18000000 40000000 t +
  45 * pos (t - 40000000)

/-- 第89条 in yen (exact whenever `t` is a whole number of 100 yen, a fortiori of 1,000 yen). -/
def tax89 (t : Int) : Int := tax89c t / 100

/-- The NTA's 速算表 (令和7年分 年末調整のしかた p.55; タックスアンサー No.2260): `t × rate − 控除額`, in hundredths:
5 % (0); 10 % − 97,500; 20 % − 427,500; 23 % − 636,000; 33 % − 1,536,000; 40 % − 2,796,000; 45 % − 4,796,000. -/
def quick (t : Int) : Int :=
  if t ≤ 0 then 0
  else if t ≤ 1950000 then 5 * t
  else if t ≤ 3300000 then 10 * t - 9750000
  else if t ≤ 6950000 then 20 * t - 42750000
  else if t ≤ 9000000 then 23 * t - 63600000
  else if t ≤ 18000000 then 33 * t - 153600000
  else if t ≤ 40000000 then 40 * t - 279600000
  else 45 * t - 479600000

/-! ## 配当控除 (第92条) -/

/-- **第92条第1項** for 剰余金の配当等 (dividends of domestic companies; no 証券投資信託), in hundredths of a yen:
第1号イ "当該配当所得の金額に百分の十" when the 課税総所得金額 `t` is at most 10,000,000 yen; 第3号イ otherwise:
"当該課税総所得金額から千万円...を控除した金額に達するまでの金額については百分の五を、その他の金額については百分の十". -/
def haitoKojo100 (t d : Int) : Int :=
  let d := pos d
  if t ≤ 10000000 then 10 * d
  else
    let low := min d (t - 10000000)
    5 * low + 10 * (d - low)

/-- **第92条第2項** ("当該控除をすべき金額がその年分の所得税額をこえるときは、当該控除をすべき金額は、当該所得税額に
相当する金額とする") and 復興財源確保法第24条第1項 (the 基準所得税額, the 復興特別所得税's 課税標準, cut to the yen):
所得税額 after 配当控除. -/
def afterHaito (tax t d : Int) : Int := (100 * tax - min (haitoKojo100 t d) (100 * tax)) / 100

/-! ## 復興特別所得税 -/

/-- **復興財源確保法第13条**: "基準所得税額に百分の二・一の税率を乗じて計算した金額", for 平成25年から令和19年まで
(第9条第1項); the fraction of a yen cut (確定申告書 第一表 ㊸; 国等の債権債務等の金額の端数計算に関する法律第2条). -/
def fukko (kijun : Int) : Int := pos kijun * 21 / 1000

/-- **復興財源確保法第24条第2項 / 第30条第1項第2号**: 所得税 and 復興特別所得税 are paid as one amount cut to the 100 yen
("これらの確定金額の合計額によって行い、当該合計額に百円未満の端数があるとき...切り捨てる"). For a wage earner settled by
年末調整, the 年調年税額 is exactly this (NTA p.39: "１００円未満の端数は切り捨てます"). -/
def nationalPayable (kijun : Int) : Int := trunc100 (pos kijun + fukko kijun)

/-! ## Properties of the rate -/

theorem slice_mono (rate lo hi : Int) {a b : Int} (hr : 0 ≤ rate) (h : a ≤ b) :
    slice rate lo hi a ≤ slice rate lo hi b := by
  unfold slice
  exact Int.mul_le_mul_of_nonneg_left (pos_mono (by omega)) hr

/-- **第89条 is non-decreasing** in the 課税総所得金額. -/
theorem tax89c_mono {a b : Int} (h : a ≤ b) : tax89c a ≤ tax89c b := by
  unfold tax89c
  have := slice_mono 5 0 1950000 (show (0:Int) ≤ 5 by omega) h
  have := slice_mono 10 1950000 3300000 (show (0:Int) ≤ 10 by omega) h
  have := slice_mono 20 3300000 6950000 (show (0:Int) ≤ 20 by omega) h
  have := slice_mono 23 6950000 9000000 (show (0:Int) ≤ 23 by omega) h
  have := slice_mono 33 9000000 18000000 (show (0:Int) ≤ 33 by omega) h
  have := slice_mono 40 18000000 40000000 (show (0:Int) ≤ 40 by omega) h
  have : 45 * pos (a - 40000000) ≤ 45 * pos (b - 40000000) :=
    Int.mul_le_mul_of_nonneg_left (pos_mono (by omega)) (by omega)
  omega

theorem tax89_mono {a b : Int} (h : a ≤ b) : tax89 a ≤ tax89 b := by
  unfold tax89
  exact Int.ediv_le_ediv (by omega) (tax89c_mono h)

/-- **Continuity of 第89条: the 控除額 formulation equals the bracket sum**, for every amount (not only multiples of
1,000 yen). The 速算表 is the statute's progressive schedule written as one line per bracket; the two agree at every
bracket boundary, so the schedule has no jump. -/
theorem tax89c_eq_quick (t : Int) : tax89c t = quick t := by
  unfold tax89c quick slice pos
  by_cases h0 : t ≤ 0
  · simp only [h0, ite_true]; omega
  · simp only [h0, ite_false]
    by_cases h1 : t ≤ 1950000
    · simp only [h1, ite_true]; omega
    · simp only [h1, ite_false]
      by_cases h2 : t ≤ 3300000
      · simp only [h2, ite_true]; omega
      · simp only [h2, ite_false]
        by_cases h3 : t ≤ 6950000
        · simp only [h3, ite_true]; omega
        · simp only [h3, ite_false]
          by_cases h4 : t ≤ 9000000
          · simp only [h4, ite_true]; omega
          · simp only [h4, ite_false]
            by_cases h5 : t ≤ 18000000
            · simp only [h5, ite_true]; omega
            · simp only [h5, ite_false]
              by_cases h6 : t ≤ 40000000
              · simp only [h6, ite_true]; omega
              · simp only [h6, ite_false]; omega

/-- The marginal rate of 第89条 is between 5 % and 45 % on every step of 1,000 yen above zero. -/
theorem tax89_step (t : Int) (h : 0 ≤ t) (h1 : t % 1000 = 0) :
    50 ≤ tax89 (t + 1000) - tax89 t ∧ tax89 (t + 1000) - tax89 t ≤ 450 := by
  unfold tax89
  rw [tax89c_eq_quick, tax89c_eq_quick]
  unfold quick
  by_cases h0 : t + 1000 ≤ 0
  · omega
  · simp only [h0, ite_false]
    repeat (first | split | omega)

/-- On a multiple of 1,000 yen the tax is a whole number of yen: nothing is lost by `/ 100`. -/
theorem tax89_exact (t : Int) (h : t % 1000 = 0) : tax89c t % 100 = 0 := by
  rw [tax89c_eq_quick]; unfold quick
  repeat (first | split | omega)

/-- The tax is never more than 45 % of the amount. -/
theorem tax89_le (t : Int) (h : 0 ≤ t) : tax89c t ≤ 45 * t := by
  rw [tax89c_eq_quick]; unfold quick
  repeat (first | split | omega)

/-- 復興特別所得税 is non-decreasing in the 基準所得税額. -/
theorem fukko_mono {a b : Int} (h : a ≤ b) : fukko a ≤ fukko b := by
  unfold fukko pos; omega

end JpTax
