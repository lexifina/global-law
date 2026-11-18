import UkTax.PAYE
open UkTax

/-! A whole tax year of equal payments through HMRC's PAYE tax table routine (copied from the UK model).
stdin: `id;per;code;scot;payPence` (per = 12 or 52; code = 1257 (any suffix code number), K475, BR, D0..D3, NT;
scot = 0/1). stdout: `id;totalTaxPence;cappedPeriods` (tax over the year, cumulative basis, 50 % regulatory limit). -/

def parseCode (s : String) : Option PayeCode :=
  if s = "BR" then some .br else if s = "NT" then some .nt
  else if s.startsWith "D" then (s.drop 1).toNat?.map PayeCode.d
  else if s.startsWith "K" then (s.drop 1).toNat?.map PayeCode.kcode
  else s.toNat?.map PayeCode.suffix

def runLine (l : String) : String :=
  match l.splitOn ";" with
  | [id, per, code, scot, pay] =>
    match per.toNat?, parseCode code, pay.toInt? with
    | some per, some c, some p =>
      let ps := (List.range per).map fun i => ({ period := i + 1, pay := p, code := c, scot := scot = "1", w1 := false } : PayePayment)
      let r := payeRun per ps
      let total := r.foldl (fun acc x => acc + x.1) 0
      let capped := (r.zip ps).countP fun (x, q) => x.1 = q.pay * 5000 / 10000 && x.1 > 0
      s!"{id};{total};{capped}"
    | _, _, _ => s!"{id};ERR;0"
  | _ => s!"ERR"

partial def loop (h : IO.FS.Stream) (o : IO.FS.Stream) : IO Unit := do
  let l ← h.getLine
  if l.isEmpty then return
  let t := (l.toList.filter (fun ch => ch != (Char.ofNat 10) && ch != (Char.ofNat 13))).asString
  if !t.isEmpty then o.putStrLn (runLine t)
  loop h o

def main : IO Unit := do loop (← IO.getStdin) (← IO.getStdout)
