import LegalProofs.USCaseLaw.Statute

/-!
# Runner: has the statute a decision applied changed since?

    lake env lean --run LegalProofs/USCaseLaw/RunStatutes.lean <in.tsv> <today yyyymmdd> <out.tsv>

Each input row: row id, the day decided, then the days the section's versions came into force (ascending; 0 for the
record's first version). Each output row: row id, whether the section changed since (`changedSince`), the number of
changes, and the day of the first one (0 if none).
-/

open Legal.USCaseLaw

def clean (s : String) : String := String.ofList (s.toList.filter (fun c => c != '\r' && c != ' ' && c != '\n'))

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, today, out] =>
    let t := today.toNat!
    let s ← IO.FS.readFile inp
    let o ← IO.FS.Handle.mk out .write
    let mut n := 0
    let mut changed := 0
    for l in s.splitOn "\n" do
      if l.isEmpty then continue
      let f := (l.splitOn "\t").toArray.map clean
      let d := f[1]!.toNat!
      let h : List Version := (List.range (f.size - 2)).map (fun k => ⟨f[k + 2]!.toNat!, k⟩)
      let c := changesBetween h d t
      let ch := changedSince h d t
      n := n + 1
      if ch then changed := changed + 1
      o.putStrLn s!"{f[0]!}\t{if ch then 1 else 0}\t{c.length}\t{(c.head?.map (·.from_)).getD 0}"
    IO.println s!"{n} decisions applying a section; {changed} sections changed since"
    return 0
  | _ => IO.eprintln "usage: RunStatutes.lean <in.tsv> <today> <out.tsv>"; return 2
