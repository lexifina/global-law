import Compare.Fr
open Compare.Fr

/-- Reads annual gross pay in euros (one integer per line) and prints the adapter's lines, unchanged, as JSON. -/
def main : IO Unit := do
  let stdin ← IO.getStdin
  let mut line ← stdin.getLine
  while line != "" do
    let s := line.trimAscii.toString
    if let some g := s.toInt? then
      let c := contrib g
      IO.println s!"\{\"g\":{g},\"vplaf\":{c.vieillessePlaf},\"vdeplaf\":{c.vieillesseDeplaf},\"t1\":{c.agircT1},\"t2\":{c.agircT2},\"ceg1\":{c.cegT1},\"ceg2\":{c.cegT2},\"cet\":{c.cet},\"csgBase\":{c.csgBase},\"csgDed\":{c.csgDeductible},\"csgNd\":{c.csgNonDeductible},\"crds\":{c.crds},\"ssc\":{c.ssc},\"csgCrds\":{c.csgCrds},\"taxable\":{taxableSalary g}}"
    line ← stdin.getLine
