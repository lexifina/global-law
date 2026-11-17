import Penalties
open Pen

/-- Input rows: id \t year \t deficiency-cents \t sec=cents;sec=cents ; output: id \t year \t check \t label. -/
def parseRow (l : String) : Option Row :=
  match l.splitOn "\t" with
  | [id, y, d, ps] =>
    let pens := (ps.splitOn ";").filterMap fun kv =>
      match kv.splitOn "=" with
      | [k, v] => v.toNat?.map (k, ·)
      | _ => none
    match y.toNat?, d.toNat? with
    | some y, some d => some { id := id, year := y, defic := d, pens := pens }
    | _, _ => none
  | _ => none

def main (args : List String) : IO Unit := do
  let ls ← IO.FS.lines (args.headD "rows.tsv")
  let out ← IO.FS.Handle.mk (args.getD 1 "classified.tsv") .write
  let mut n := 0
  for l in ls do
    match parseRow l with
    | none => pure ()
    | some r =>
      n := n + 1
      for (k, v) in classify r do
        out.putStrLn s!"{r.id}\t{r.year}\t{k}\t{v}"
  IO.println s!"rows {n}"
