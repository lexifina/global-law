import JpTax.Basic
import JpTax.GessakuData

/-!
# Monthly withholding in 2025 (所得税法第185条, 別表第二; 復興財源確保法第28条; 平成24年財務省告示第116号)

Three official instruments give the tax an employer withholds each month from an employee who has filed the
扶養控除等申告書 (甲欄):

1. **所得税法 別表第二** (月額表), the statute's table: 所得税 only.
2. **The NTA's combined 月額表** (「令和7年分 源泉徴収税額表」): 所得税 and 復興特別所得税 together, the table employers use.
3. **The 電算機計算の特例** (平成24年3月31日財務省告示第116号, 令和5年3月31日財務省告示第95号改正, 令和7年分), a formula an
   employer with a computer may use instead of the table.

All three embody the law **before** the 令和7年度 reform (基礎控除 40,000 yen a month = 480,000 a year; a minimum
給与所得控除 of 45,834 yen a month ≈ 550,000 a year; 31,667 yen a month per dependant = 380,000 a year): "令和2年1月以後
「税額」は改正されていません" (NTA, 令和7年分 源泉徴収税額表). The reform reaches employees only at the 年末調整 in December
2025.
-/

namespace JpTax

/-- Rounding to the nearest 10 yen, a half up (告示 別表第四 注: "税額に10円未満の端数があるときは、これを四捨五入"). -/
def round10 (x100000 : Int) : Int := (x100000 + 500000) / 1000000 * 10

/-- The combined table is the statute's table times 102.1 % (復興財源確保法第28条第2項: "百分の二・一の税率"), rounded
to 10 yen. -/
def combinedCell (statute : Int) : Int := round10 (statute * 102100)

def chunkCombinedOk (c : List (Int × Int × List Int × List Int)) : Bool :=
  c.all fun (_, _, st, nta) => (st.map combinedCell) == nta

/-! ## The 告示 formula (令和7年分) -/

/-- 別表第一: 給与所得控除の額 on `a`, the month's pay after social insurance, "１円未満の端数があるときは、これを切り上げ"
(in hundredths of a yen inside). -/
def denshiKyuyoKojo (a : Int) : Int :=
  if a ≤ 135416 then 45834
  else if a ≤ 149999 then cdiv (40 * a - 833300) 100
  else if a ≤ 299999 then cdiv (30 * a + 666700) 100
  else if a ≤ 549999 then cdiv (20 * a + 3666700) 100
  else if a ≤ 708330 then cdiv (10 * a + 9166700) 100
  else 162500

/-- 別表第三: 基礎控除の額. -/
def denshiKiso (a : Int) : Int :=
  if a ≤ 2162499 then 40000 else if a ≤ 2204166 then 26667 else if a ≤ 2245833 then 13334 else 0

/-- 別表第四, in hundred-thousandths of a yen before rounding to 10 yen: 5.105 %; 10.210 % − 8,296; 20.420 % − 36,374;
23.483 % − 54,113; 33.693 % − 130,688; 40.840 % − 237,893; 45.945 % − 408,061. -/
def denshiTax100000 (b : Int) : Int :=
  if b ≤ 162500 then 5105 * b
  else if b ≤ 275000 then 10210 * b - 829600000
  else if b ≤ 579166 then 20420 * b - 3637400000
  else if b ≤ 750000 then 23483 * b - 5411300000
  else if b ≤ 1500000 then 33693 * b - 13068800000
  else if b ≤ 3333333 then 40840 * b - 23789300000
  else 45945 * b - 40806100000

/-- The 告示's monthly withholding for pay `a` (after social insurance) and `n` 扶養親族等 (別表第二: 31,667 yen each). -/
def denshi (a n : Int) : Int :=
  let b := a - denshiKyuyoKojo a - denshiKiso a - 31667 * n
  if b ≤ 0 then 0 else round10 (denshiTax100000 b)

/-- The 告示 formula at a row's midpoint is within `tol` yen of the NTA's printed cell, for every column. -/
def chunkDenshiWithin (tol : Int) (c : List (Int × Int × List Int × List Int)) : Bool :=
  c.all fun (lo, hi, _, nta) =>
    let mid := (lo + hi - 1) / 2
    (List.range 8).all fun (k : Nat) => decide ((denshi mid (k : Int) - nta.getD k 0).natAbs ≤ tol.natAbs)

def chunkDenshiEqual (c : List (Int × Int × List Int × List Int)) : Nat :=
  c.foldl (fun acc (lo, hi, _, nta) =>
    let mid := (lo + hi - 1) / 2
    acc + ((List.range 8).filter fun (k : Nat) => denshi mid (k : Int) == nta.getD k 0).length) 0

theorem gessakuChunk0_combined : chunkCombinedOk gessakuChunk0 = true := by decide
theorem gessakuChunk1_combined : chunkCombinedOk gessakuChunk1 = true := by decide
theorem gessakuChunk2_combined : chunkCombinedOk gessakuChunk2 = true := by decide
theorem gessakuChunk3_combined : chunkCombinedOk gessakuChunk3 = true := by decide
theorem gessakuChunk4_combined : chunkCombinedOk gessakuChunk4 = true := by decide
theorem gessakuChunk5_combined : chunkCombinedOk gessakuChunk5 = true := by decide
theorem gessakuChunk6_combined : chunkCombinedOk gessakuChunk6 = true := by decide
theorem gessakuChunk7_combined : chunkCombinedOk gessakuChunk7 = true := by decide
theorem gessakuChunk8_combined : chunkCombinedOk gessakuChunk8 = true := by decide
theorem gessakuChunk9_combined : chunkCombinedOk gessakuChunk9 = true := by decide
theorem gessakuChunk10_combined : chunkCombinedOk gessakuChunk10 = true := by decide
theorem gessakuChunk11_combined : chunkCombinedOk gessakuChunk11 = true := by decide
theorem gessakuChunk12_combined : chunkCombinedOk gessakuChunk12 = true := by decide

theorem gessakuChunk0_denshi : chunkDenshiWithin 70 gessakuChunk0 = true := by decide
theorem gessakuChunk1_denshi : chunkDenshiWithin 70 gessakuChunk1 = true := by decide
theorem gessakuChunk2_denshi : chunkDenshiWithin 70 gessakuChunk2 = true := by decide
theorem gessakuChunk3_denshi : chunkDenshiWithin 70 gessakuChunk3 = true := by decide
theorem gessakuChunk4_denshi : chunkDenshiWithin 70 gessakuChunk4 = true := by decide
theorem gessakuChunk5_denshi : chunkDenshiWithin 70 gessakuChunk5 = true := by decide
theorem gessakuChunk6_denshi : chunkDenshiWithin 70 gessakuChunk6 = true := by decide
theorem gessakuChunk7_denshi : chunkDenshiWithin 70 gessakuChunk7 = true := by decide
theorem gessakuChunk8_denshi : chunkDenshiWithin 70 gessakuChunk8 = true := by decide
theorem gessakuChunk9_denshi : chunkDenshiWithin 70 gessakuChunk9 = true := by decide
theorem gessakuChunk10_denshi : chunkDenshiWithin 70 gessakuChunk10 = true := by decide
theorem gessakuChunk11_denshi : chunkDenshiWithin 70 gessakuChunk11 = true := by decide
theorem gessakuChunk12_denshi : chunkDenshiWithin 70 gessakuChunk12 = true := by decide

/-- **The NTA's combined 月額表 is the statute's 別表第二 × 102.1 %, rounded to 10 yen**, in all 245 × 8 甲欄 cells from
88,000 to 740,000 yen (each chunk checked by the kernel above). -/
theorem gessaku_combined_all : gessakuChunks.all chunkCombinedOk = true := by
  simp only [gessakuChunks, List.all_cons, List.all_nil, Bool.and_true, gessakuChunk0_combined, gessakuChunk1_combined, gessakuChunk2_combined, gessakuChunk3_combined, gessakuChunk4_combined, gessakuChunk5_combined, gessakuChunk6_combined, gessakuChunk7_combined, gessakuChunk8_combined, gessakuChunk9_combined, gessakuChunk10_combined, gessakuChunk11_combined, gessakuChunk12_combined]

/-- **The 告示 formula, applied at each row's midpoint, is within 70 yen of the printed table in every cell.** -/
theorem gessaku_denshi_within_70 : gessakuChunks.all (chunkDenshiWithin 70) = true := by
  simp only [gessakuChunks, List.all_cons, List.all_nil, Bool.and_true, gessakuChunk0_denshi, gessakuChunk1_denshi, gessakuChunk2_denshi, gessakuChunk3_denshi, gessakuChunk4_denshi, gessakuChunk5_denshi, gessakuChunk6_denshi, gessakuChunk7_denshi, gessakuChunk8_denshi, gessakuChunk9_denshi, gessakuChunk10_denshi, gessakuChunk11_denshi, gessakuChunk12_denshi]

/-- The per-month amounts are the pre-reform annual ones divided by 12. -/
theorem denshi_prereform : 12 * 40000 = 480000 ∧ 12 * 31667 = 380004 ∧ 12 * 45834 = 550008 := by decide

end JpTax
