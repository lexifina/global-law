import JpTax.Income
import JpTax.Beppyo5Data

/-!
# 別表第五: the closed form equals the statute's table on every yen

`beppyo5Rows` holds the 1,175 rows of 所得税法 別表第五 between 1,900,000 and 6,600,000 yen, machine-extracted from the
e-Gov XML. `kyuyoShotoku` is the closed form (the row's lower end × 70 % − 80,000 yen, or × 80 % − 440,000 yen). The
kernel checks every row at both ends; monotonicity then gives every yen in between.
-/

namespace JpTax

/-- The rows tile [1,900,000, 6,600,000) without gaps. -/
theorem beppyo5_rows_count : beppyo5Chunks.length = 47 ∧ (beppyo5Chunks.map List.length).sum = 1175 := by
  simp only [beppyo5Chunks, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil, List.length_cons,
    List.length_nil]
  simp only [beppyo5Chunk0, beppyo5Chunk46, List.length_cons, List.length_nil]
  decide

/-- **The closed form is the table**: for every row (以上 `lo`, 未満 `hi`, value `v`) of 別表第五 and every salary `w`
in the row, `kyuyoShotoku w = v`. -/
theorem beppyo5_eq_table (lo hi v : Int) (hrow : (lo, hi, v) ∈ beppyo5Rows) (w : Int) (h1 : lo ≤ w) (h2 : w < hi) :
    kyuyoShotoku w = v := by
  have hall := beppyo5Rows_ok
  rw [List.all_eq_true] at hall
  have hr := hall (lo, hi, v) hrow
  simp only [beppyo5RowOk, Bool.and_eq_true, beq_iff_eq] at hr
  obtain ⟨⟨hlo, hhi⟩, _⟩ := hr
  exact const_of_mono_ends kyuyoShotoku (fun a b h => kyuyoShotoku_mono h) lo (hi - 1) v w hlo hhi h1 (by omega)

/-- The rows of the table below 1,900,000 yen, copied: "６５１，０００円未満 | ０" and "６５１，０００ | １，９００，０００ |
給与等の金額から６５０，０００円を控除した金額". -/
theorem beppyo5_low (w : Int) :
    (w < 651000 → kyuyoShotoku w = 0) ∧ (651000 ≤ w → w < 1900000 → kyuyoShotoku w = w - 650000) := by
  unfold kyuyoShotoku
  constructor
  · intro h; simp [h]
  · intro h1 h2
    have : ¬ w < 651000 := by omega
    simp [this, h2]

/-- **The 4,000-yen steps.** Inside a row the 給与所得 does not move; at the start of each row it jumps by 2,800 yen
(below 3,600,000) or 3,200 yen (from 3,600,000 to 6,600,000): one more yen of salary at 1,903,999 → 1,904,000 adds
2,800 yen of income. -/
theorem beppyo5_step (k : Int) (h1 : 476 ≤ k) (h2 : k < 1650) :
    kyuyoShotoku (4000 * k) - kyuyoShotoku (4000 * k - 1) = (if k ≤ 900 then 2800 else 3200) ∧
    kyuyoShotoku (4000 * k + 3999) = kyuyoShotoku (4000 * k) := by
  unfold kyuyoShotoku
  constructor <;> (repeat (first | split | omega))

/-- The first step (at 1,900,000 yen the table joins the "給与等の金額から650,000円" rows without a jump), and the step at
6,600,000 yen where the formula of 第28条第3項 takes over. -/
theorem beppyo5_joins :
    kyuyoShotoku 1899999 = 1249999 ∧ kyuyoShotoku 1900000 = 1250000 ∧ kyuyoShotoku 1903999 = 1250000 ∧
    kyuyoShotoku 6599999 = 4836800 ∧ kyuyoShotoku 6600000 = 4840000 := by decide

end JpTax
