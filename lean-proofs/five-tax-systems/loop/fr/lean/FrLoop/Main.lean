import FrLoop.Extra

/-! `frloop`: as `frtax`, with an optional fourth field of additions,
`id;year;BOX=V,...;PIN=..,PME=..,GIR=..,MAL=..,PC=..,EXC=..` (see `FrLoop.Extra`). Prints the `frtax` keys. -/

open FrTax FrLoop

-- copied from FrTax/Main.lean (which declares `main` and cannot be imported)
def parseDecl (year : Nat) (s : String) : Decl :=
  let pairs := (s.splitOn ",").filterMap fun kv =>
    match kv.splitOn "=" with
    | [k, v] => (v.trimAscii.toString.toInt?).map fun n => (k.trimAscii.toString, n)
    | _ => none
  { year, boxes := pairs.foldl (fun m (k, v) => m.insert k v) {} }

def fmtParts (q : Int) : String :=
  let w := q / 4
  match q % 4 with
  | 0 => s!"{w}" | 1 => s!"{w}.25" | 2 => s!"{w}.5" | _ => s!"{w}.75"

def parseExtra (s : String) : Extra :=
  (s.splitOn ",").foldl (fun e kv =>
    match kv.splitOn "=" with
    | [k, v] =>
      let n := (v.trimAscii.toString.toInt?).getD 0
      match k.trimAscii.toString with
      | "PIN" => { e with pinel := n } | "PME" => { e with pme := n } | "GIR" => { e with girardin := n }
      | "MAL" => { e with malraux := n } | "PC" => { e with pcCapital := n } | "EXC" => { e with exc := n }
      | _ => e
    | _ => e) {}

def runX (line : String) : Option String := do
  let (id, y, bx, ex) ← match line.splitOn ";" with
    | [a, b, c] => some (a, b, c, "")
    | [a, b, c, e] => some (a, b, c, e)
    | _ => none
  let year ← y.trimAscii.toString.toNat?
  let p ← paramsFor year
  let d := parseDecl year bx
  let r := computeX p d (parseExtra ex)
  some s!"{id};NBPT={fmtParts r.quarters};RNG={r.rng};RNI={r.rni};IDRS={r.capped.tax};IDEC={r.decote};ITRED={r.reductions};CITOT={r.credits};PFU={r.flat};IDRS4={r.capped.tax - r.decote};IAVCR={r.beforeCredits};IMPNET={r.net};REVKIRE={r.rfr};PSNET={r.social};CHRAPRES={r.cehr};CDHR={r.cdhr}"

partial def loopX (h o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  o.putStrLn ((runX line.trimAscii.toString).getD s!"ERR;{line.trimAscii.toString}")
  loopX h o

def main : IO Unit := do loopX (← IO.getStdin) (← IO.getStdout)
