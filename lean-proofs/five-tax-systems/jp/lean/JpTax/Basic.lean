/-!
# Yen arithmetic

Every amount is a whole number of yen (`Int`); rates are written as exact fractions. `/` on `Int` is
Euclidean division, which for a positive divisor is the floor. The statutes fix these roundings:

* 国税通則法第118条第1項: the 課税標準 of a national tax is cut to the 1,000 yen ("千円未満の端数があるとき、
  又はその全額が千円未満であるときは、その端数金額又はその全額を切り捨てる"); 地方税法第20条の4の2第1項 says
  the same for local taxes.
* 国税通則法第119条第1項 / 地方税法第20条の4の2第3項: a 確定金額 is cut to the 100 yen.
* 復興財源確保法第24条第1項: the 課税標準 of 復興特別所得税 (the 基準所得税額) is cut to the yen; 第2項: the
  確定金額 of 所得税 and 復興特別所得税 is cut to the 100 yen on their sum.
* Employee social-insurance shares withheld from pay (協会けんぽ 保険料額表 令和7年度, note ①): "被保険者負担分の
  端数が50銭以下の場合は切り捨て、50銭を超える場合は切り上げて1円".
-/

namespace JpTax

/-- The positive part, `max 0 x` (a 残額 is never negative). -/
def pos (x : Int) : Int := max 0 x

/-- 国税通則法第118条第1項, 地方税法第20条の4の2第1項: cut to the 1,000 yen; a negative base is nil. -/
def trunc1000 (x : Int) : Int := pos x / 1000 * 1000

/-- 国税通則法第119条第1項, 地方税法第20条の4の2第3項: cut to the 100 yen; a negative amount is nil. -/
def trunc100 (x : Int) : Int := pos x / 100 * 100

/-- `a / b` rounded up, for `b > 0`. -/
def cdiv (a b : Int) : Int := (a + b - 1) / b

/-- `n / d` rounded to the yen with an exact half going down ("50銭以下の場合は切り捨て、50銭を超える場合は切り上げ"),
for `d > 0`. -/
def rhd (n d : Int) : Int := (2 * n + d - 1) / (2 * d)

theorem pos_nonneg (x : Int) : 0 ≤ pos x := by unfold pos; omega
theorem pos_mono {a b : Int} (h : a ≤ b) : pos a ≤ pos b := by unfold pos; omega

theorem trunc1000_mono {a b : Int} (h : a ≤ b) : trunc1000 a ≤ trunc1000 b := by
  unfold trunc1000 pos; omega

theorem trunc1000_le (x : Int) (h : 0 ≤ x) : trunc1000 x ≤ x := by
  unfold trunc1000 pos; omega

theorem trunc1000_gt (x : Int) (h : 0 ≤ x) : x < trunc1000 x + 1000 := by
  unfold trunc1000 pos; omega

theorem trunc1000_nonneg (x : Int) : 0 ≤ trunc1000 x := by
  unfold trunc1000 pos; omega

theorem trunc1000_dvd (x : Int) : trunc1000 x % 1000 = 0 := by
  unfold trunc1000 pos; omega

theorem trunc100_mono {a b : Int} (h : a ≤ b) : trunc100 a ≤ trunc100 b := by
  unfold trunc100 pos; omega

theorem trunc100_le (x : Int) (h : 0 ≤ x) : trunc100 x ≤ x := by
  unfold trunc100 pos; omega

theorem trunc100_nonneg (x : Int) : 0 ≤ trunc100 x := by
  unfold trunc100 pos; omega

theorem cdiv_mono {a a' : Int} (b : Int) (hb : 0 < b) (h : a ≤ a') : cdiv a b ≤ cdiv a' b := by
  unfold cdiv; exact Int.ediv_le_ediv hb (by omega)

/-- A monotone function that takes the same value at both ends of an interval is constant on it. Used to show
that a closed form equals a table row on every yen of the row. -/
theorem const_of_mono_ends (f : Int → Int) (hf : ∀ a b, a ≤ b → f a ≤ f b) (lo hi v w : Int)
    (hlo : f lo = v) (hhi : f hi = v) (h1 : lo ≤ w) (h2 : w ≤ hi) : f w = v := by
  have := hf lo w h1
  have := hf w hi h2
  omega

end JpTax
