import KrTax.Incentive

/-!
# The 장려금 산정표 against the statute's formulas (FINDINGS F3, F4)

STA §100의5⑤ and §100의29② make the banded tables of 시행령 별표 11 / 11의2 the law; §100의5① and §100의29① give the
formulas. The tables follow one rule, recovered here and checked on every cell by the kernel (`decide`): a cell is the
formula's largest value on its row `[이상, 미만)`, rounded up to the 1,000 won, and nil ("-") when that is under
15,000 won (the amount §100의7③ treats as nil). The exceptions are exactly F3's 40 cells.
-/

namespace KrTax
open TaxKernel

set_option maxRecDepth 200000

/-- The table's rule for a row `[lo, hi)` of a continuous piecewise-linear formula `f` (exact fractions): the larger
of the values at the row's two ends, rounded up to 1,000 won; 0 under 15,000. -/
def ruleOf (f : Int → Int × Int) (lo hi : Int) : Int :=
  let a := f lo
  let b := f hi
  let v := if a.1 * b.2 ≥ b.1 * a.2 then a else b
  if v.1 < 15000 * v.2 then 0 else ceilDiv v.1 (1000 * v.2) * 1000

def eitcCell (r : Int × Int × Int × Int × Int) (k : Nat) : Int :=
  if k = 0 then r.2.2.1 else if k = 1 then r.2.2.2.1 else r.2.2.2.2

/-- A cell agrees with the rule ("해당 없음" cells, -1, are not amounts). -/
def eitcCellOk (k : Nat) (r : Int × Int × Int × Int × Int) : Bool :=
  eitcCell r k == -1 || eitcCell r k == ruleOf (eitcFormula k) r.1 r.2.1

/-- 단독가구 and 맞벌이 가구: all 447 rows follow the rule. -/
theorem eitc_single_dual_follow_rule : eitcRows.all (fun r => eitcCellOk 0 r && eitcCellOk 2 r) = true := by
  decide

/-- 홑벌이 가구: 42 cells do not follow the rule. 40 are the rows below 4,000,000 won, each printing the 단독가구 amount
instead; the other 2 are the rows the table splits at 21,770,000 and 21,881,900 won (where the 단독 amount crosses
30,000 and 15,000): there the 홑벌이 cell repeats the amount of the whole 100,000-won row, while the 맞벌이 cell is
recomputed (F3). -/
theorem eitc_one_earner_exceptions :
    (eitcRows.filter (fun r => !eitcCellOk 1 r)).length = 42 ∧
    ((eitcRows.filter (fun r => !eitcCellOk 1 r)).filter
      (fun r => decide (r.2.1 ≤ 4000000) && eitcCell r 1 == eitcCell r 0)).length = 40 ∧
    ((eitcRows.filter (fun r => !eitcCellOk 1 r)).map (·.1)).drop 40 = [21770000, 21881900] := by decide

/-- …and in each of them the table pays more than the formula's rule (by 1,000 to 21,000 won). -/
theorem eitc_one_earner_table_higher :
    (eitcRows.filter (fun r => !eitcCellOk 1 r)).all
      (fun r => decide (eitcCell r 1 > ruleOf (eitcFormula 1) r.1 r.2.1) &&
                decide (eitcCell r 1 - ruleOf (eitcFormula 1) r.1 r.2.1 ≤ 21000)) = true := by decide

/-- The largest gap: 총급여액 등 of 3,900,000-3,999,999 won, 1,650,000 in the table, 1,629,000 by the rule. -/
theorem eitc_one_earner_gap_max : eitcTable 1 3950000 = 1650000 ∧ ruleOf (eitcFormula 1) 3900000 4000000 = 1629000 := by
  decide

def ctcCellOk (k : Nat) (r : Int × Int × Int × Int) : Bool :=
  let c := if k = 1 then r.2.2.1 else r.2.2.2
  c == -1 || c == ruleOf (ctcFormula k) r.1 r.2.1

/-- 자녀장려금: every cell of both columns follows the rule. -/
theorem ctc_follows_rule : ctcRows.all (fun r => ctcCellOk 1 r && ctcCellOk 2 r) = true := by decide

/-- F4: the last row ends at 69,999,990 won; from there to 69,999,999 no row applies and the amount is nil, though
§100의28①2 admits any total income "7천만원 미만". -/
theorem ctc_table_gap :
    ctcTable 1 69999989 = 506000 ∧ ctcTable 1 69999990 = 0 ∧ ctcTable 2 69999999 = 0 := by decide

/-- The tables are the rows' union without gaps or overlaps up to their last row (contiguous). -/
def contiguous : List (Int × Int) → Bool
  | a :: b :: rest => a.2 == b.1 && contiguous (b :: rest)
  | _ => true
theorem eitc_contiguous : contiguous (eitcRows.map fun r => (r.1, r.2.1)) = true := by decide
theorem ctc_contiguous : contiguous (ctcRows.map fun r => (r.1, r.2.1)) = true := by decide

end KrTax
