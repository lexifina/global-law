import KrTax.Out
import KrTax.Withholding

/-- `krtax --wht <monthly wage, won> <공제대상가족 1-11>` (tests round 2: the 근로소득 간이세액표 as a dataset): the monthly
withholding the table's note 1 gives (`KrTax.whtModel .table`, FINDINGS F8) for the table row `[이상, 미만)` that holds the
wage; exit 1 outside the 646 printed rows. Without `--wht`: the contract (households on stdin). -/
def whtCli (w n : Int) : Option Int :=
  match KrTax.whtRows.find? (fun r => decide (r.1 * 1000 ≤ w ∧ w < r.2.1 * 1000)) with
  | some r => some (KrTax.whtModel .table r.1 r.2.1 n)
  | none => none

def main (args : List String) : IO UInt32 := do
  match args with
  | ["--wht", w, n] =>
    match whtCli w.toInt! n.toInt! with
    | some v => IO.println v; return 0
    | none => IO.eprintln "wage outside the 간이세액표 rows"; return 1
  | _ => TaxKernel.countryMain KrTax.country args
