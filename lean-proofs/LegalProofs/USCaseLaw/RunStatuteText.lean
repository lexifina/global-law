import LegalProofs.USCaseLaw.StatuteText

/-!
# Runner: what each decision applied, and what the US Code says now

    lake env lean --run LegalProofs/USCaseLaw/RunStatuteText.lean <in.tsv> <today yyyymmdd> <out.tsv>

Each input row: row id, the day decided, then the section's versions in order, each `day,law,text,sub` (law 1 when an
Act made the version, 0 for an edition; text and sub identify the words of the section and of the cited subsection).
Each output row: row id, amended since by a law (0/1), the number of such laws, the day of the first (0 if none), the
section's words differ today (0/1), the cited subsection's words differ today (0/1), and the number of versions since.
-/

open Legal.USCaseLaw

def clean (s : String) : String := String.ofList (s.toList.filter (fun c => c != '\r' && c != ' ' && c != '\n'))

def parseV (s : String) : SVersion :=
  match (s.splitOn ",").toArray.map (·.toNat!) with
  | #[d, l, x, y] => ⟨d, l == 1, x, y⟩
  | _ => ⟨0, false, 0, 0⟩

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, today, out] =>
    let t := today.toNat!
    let s ← IO.FS.readFile inp
    let o ← IO.FS.Handle.mk out .write
    let mut n := 0
    let mut am := 0
    let mut wd := 0
    let mut sd := 0
    for l in s.splitOn "\n" do
      if l.isEmpty then continue
      let f := (l.splitOn "\t").toArray.map clean
      let d := f[1]!.toNat!
      let h : List SVersion := (f.toList.drop 2).map parseV
      let lc := lawChangesBetween h d t
      let a := amendedSince h d t
      let w := wordsDiffer h d t
      let sb := subDiffers h d t
      n := n + 1
      if a then am := am + 1
      if w then wd := wd + 1
      if sb then sd := sd + 1
      let b (x : Bool) := if x then 1 else 0
      o.putStrLn s!"{f[0]!}\t{b a}\t{lc.length}\t{(lc.head?.map (·.from_)).getD 0}\t{b w}\t{b sb}\t{(sChangesBetween h d t).length}"
    IO.println s!"{n} citations; amended since by a law {am}; words differ {wd}; cited subsection differs {sd}"
    return 0
  | _ => IO.eprintln "usage: RunStatuteText.lean <in.tsv> <today> <out.tsv>"; return 2
