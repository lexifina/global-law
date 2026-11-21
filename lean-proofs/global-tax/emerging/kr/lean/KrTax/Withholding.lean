import KrTax.Person
import KrTax.WithholdingData

/-!
# 근로소득 간이세액표 (소득세법 시행령 별표 2) against the statute (FINDINGS F8)

The table (the monthly withholding of 소득세법 §134①, "간이세액표에 따라") says how it was made (note 1): 근로소득공제,
기본공제 (150만원 × 공제대상가족), the "특별소득공제 및 특별세액공제 중 일부" by the printed formula, 연금보험료공제,
근로소득세액공제 and the rates. `whtModel .table` recovers every cell from that note, applied to the row's midpoint × 12,
with two stale parameters: the 근로소득세액공제 of 소득세법 §59 **as in force in 2014** (법률 제12169호: 55 % of the
산출세액 up to 50만원, 30 % above; limit 66만원 to 총급여 5,500만원, then down to 63만원 and 50만원), not the law since
법률 제13315호 (2015-05-13: 130만원; limits 74만/66만/50만/20만원), and the 국민연금 ceiling of July 2017–June 2018
(기준소득월액 4,490,000원), not 2025's 6,170,000/6,370,000. The 기준소득월액 is the midpoint cut to the 1,000 won
(국민연금법 시행령 §5①); the monthly amount is cut to the 10 won and nil under 1,000 won (소득세법 §86 소액부징수).
The kernel checks all 7,106 cells: 7,098 equal the model, the other 8 are exactly 10 won above it.
`whtModel .statute2025` is the same note-1 computation with the 2025 law; the table is never below it and is above it in
3,790 cells.
-/

namespace KrTax
open TaxKernel

set_option maxRecDepth 200000

inductive WhtLaw | table | statute2025
  deriving DecidableEq

/-- Note 1's "특별소득공제 및 특별세액공제 중 일부", in ticks (won × 10000), for `n` 공제대상가족 and 총급여 `s`. -/
def whtSpecialTicks (n s : Int) : Int :=
  let (b, r1, r3, r4) : Int × Int × Int × Int :=
    if n = 1 then (3100000, 400, 150, 50) else if n = 2 then (3600000, 400, 200, 100) else (5000000, 700, 500, 300)
  let v :=
    if s ≤ 30000000 then b * 10000 + r1 * s
    else if s ≤ 45000000 then b * 10000 + r1 * s - 500 * (s - 30000000)
    else if s ≤ 70000000 then b * 10000 + r3 * s
    else b * 10000 + r4 * s
  v + (if n ≥ 3 then 400 * pos (s - 40000000) else 0)

/-- 근로소득세액공제 limit (won × 10^12). -/
def whtLimitU (law : WhtLaw) (s : Int) : Int :=
  let u : Int := 1000000000000
  match law with
  | .table =>
    if s ≤ 55000000 then 660000 * u
    else if s ≤ 70000000 then max (630000 * u) (660000 * u - (s - 55000000) * u / 2)
    else max (500000 * u) (630000 * u - (s - 70000000) * u / 2)
  | .statute2025 =>
    if s ≤ 33000000 then 740000 * u
    else if s ≤ 70000000 then max (660000 * u) (740000 * u - (s - 33000000) * 8 * u / 1000)
    else if s ≤ 120000000 then max (500000 * u) (660000 * u - (s - 70000000) * u / 2)
    else max (200000 * u) (500000 * u - (s - 120000000) * u / 2)

/-- The national schedule on an amount in ticks (thresholds × 10000): result in won × 10^8. -/
def natSchedTicks : Schedule := natSched.mapLo (· * 10000)

/-- The monthly withholding the note-1 computation gives for a row `[lo, hi)` (천원) and `n` 공제대상가족. -/
def whtModel (law : WhtLaw) (lo hi n : Int) : Int :=
  let m := (lo + hi) * 500                         -- midpoint, won
  let s := 12 * m
  let edT := min (min (earnedDedSched.ticks s) (earnedDedCap * 10000)) (s * 10000)
  let base := floorTo 1000 m
  let penT := match law with
    | .table => 450 * 12 * min base 4490000
    | .statute2025 => 450 * 6 * (min base pensionCeilH1 + min base pensionCeilH2)
  let tiT := pos (s * 10000 - edT - 1500000 * n * 10000 - penT - whtSpecialTicks n s)
  let calcU := natSchedTicks.ticks tiT * 10000      -- won × 10^12
  let k : Int := (match law with | .table => 500000 | .statute2025 => 1300000) * 1000000000000
  let rawU := (5500 * min calcU k + 3000 * pos (calcU - k)) / 10000
  let a := pos (calcU - min rawU (whtLimitU law s)) / (12 * 1000000000000)
  let a10 := a / 10 * 10
  if a10 < 1000 then 0 else a10

/-- The 8 cells (row 이상 in 천원, 공제대상가족) where the printed table is 10 won above the recovered computation. -/
def whtExceptions : List (Int × Int) :=
  [(2270, 3), (2270, 5), (2520, 4), (2520, 6), (2680, 1), (2700, 5), (2700, 7), (2750, 1)]

def whtCellOk (lo hi : Int) (n : Nat) (v : Int) : Bool :=
  let m := whtModel .table lo hi n
  v == m || (whtExceptions.contains (lo, (n : Int)) && v == m + 10)

def whtRowOk (r : Int × Int × List Int) : Bool :=
  (r.2.2.zipIdx.all fun (v, j) => whtCellOk r.1 r.2.1 (j + 1) v)

def chunk (i : Nat) : List (Int × Int × List Int) := (whtRows.drop (50 * i)).take 50

theorem wht_rows_count : whtRows.length = 646 ∧ whtRows.all (fun r => r.2.2.length == 11) = true := by decide

theorem wht_chunk0 : (chunk 0).all whtRowOk = true := by decide
theorem wht_chunk1 : (chunk 1).all whtRowOk = true := by decide
theorem wht_chunk2 : (chunk 2).all whtRowOk = true := by decide
theorem wht_chunk3 : (chunk 3).all whtRowOk = true := by decide
theorem wht_chunk4 : (chunk 4).all whtRowOk = true := by decide
theorem wht_chunk5 : (chunk 5).all whtRowOk = true := by decide
theorem wht_chunk6 : (chunk 6).all whtRowOk = true := by decide
theorem wht_chunk7 : (chunk 7).all whtRowOk = true := by decide
theorem wht_chunk8 : (chunk 8).all whtRowOk = true := by decide
theorem wht_chunk9 : (chunk 9).all whtRowOk = true := by decide
theorem wht_chunk10 : (chunk 10).all whtRowOk = true := by decide
theorem wht_chunk11 : (chunk 11).all whtRowOk = true := by decide
theorem wht_chunk12 : (chunk 12).all whtRowOk = true := by decide

/-- The exceptions are real (the table is 10 won above the computation there), so the count is exactly 8. -/
theorem wht_exceptions_differ :
    whtExceptions.all (fun (lo, n) =>
      (whtRows.find? (fun r => r.1 == lo)).any (fun r =>
        r.2.2.getD (n.toNat - 1) 0 == whtModel .table lo r.2.1 n + 10)) = true := by decide

/-- One stale parameter at a time, at the OECD's average wage row (4,720–4,740천원, one person): the table's 296,200
won; with the 2025 law 292,080 (4,120 won a month, 49,440 a year, over-withheld). -/
theorem wht_aw_row : whtModel .table 4720 4740 1 = 296200 ∧ whtModel .statute2025 4720 4740 1 = 292080 := by decide

/-- A single earner at 3,000–3,020천원: 74,350 printed vs 61,510 under the 2025 law (12,840 won a month). -/
theorem wht_3m_row : whtModel .table 3000 3020 1 = 74350 ∧ whtModel .statute2025 3000 3020 1 = 61510 := by decide

end KrTax
