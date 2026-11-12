import LegalProofs.USCaseLaw.Watch

/-!
# Runner: watch lists over the US Code record

    lake env lean --run LegalProofs/USCaseLaw/RunWatch.lean <in.tsv> <out.tsv>

Each input row: item id, the day watched from, the day read (yyyymmdd), 1 to watch the whole section or 0 for a
subsection, then the section's versions in order, each `day,law,text,sub` (law 1 when an Act made the version; text and
sub identify the words of the section and of the watched subsection, 0 for none).

Each output row: item id, alert (0/1), the number of alerts, the number of edition notices, the history is in date
order (0/1), the words watched read the same on both days (0/1), then one code per version: `A` an alert (a law
changed the words watched), `L` a law in the window that changed only other parts of the section, `N` an edition notice
(an edition changed the words watched), `E` an edition in the window that changed nothing watched, `.` outside the
window.
-/

open Legal.USCaseLaw Legal.USCaseLaw.Watch

def clean (s : String) : String := String.ofList (s.toList.filter (fun c => c != '\r' && c != ' ' && c != '\n'))

def parseV (s : String) : SVersion :=
  match (s.splitOn ",").toArray.map (·.toNat!) with
  | #[d, l, x, y] => ⟨d, l == 1, x, y⟩
  | _ => ⟨0, false, 0, 0⟩

def sortedB : List SVersion → Bool
  | a :: b :: r => a.from_ ≤ b.from_ && sortedB (b :: r)
  | _ => true

def code (whole : Bool) (d t : Nat) (s : SVersion × SVersion) : Char :=
  if isAlert whole d t s then 'A'
  else if isNotice whole d t s then 'N'
  else if inWindow d t s.2 then (if s.2.byLaw then 'L' else 'E')
  else '.'

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, out] =>
    let s ← IO.FS.readFile inp
    let o ← IO.FS.Handle.mk out .write
    let mut n := 0
    let mut na := 0
    for l in s.splitOn "\n" do
      if l.isEmpty then continue
      let f := (l.splitOn "\t").toArray.map clean
      let d := f[1]!.toNat!
      let t := f[2]!.toNat!
      let whole := f[3]! == "1"
      let h : List SVersion := (f.toList.drop 4).map parseV
      let a := alerts whole h d t
      let nt := notices whole h d t
      let same := wordsOn whole h d == wordsOn whole h t
      let codes := String.ofList ((steps origin h).map (code whole d t))
      let b (x : Bool) := if x then 1 else 0
      n := n + 1
      if alert whole h d t then na := na + 1
      o.putStrLn s!"{f[0]!}\t{b (alert whole h d t)}\t{a.length}\t{nt.length}\t{b (sortedB h)}\t{b same}\t{codes}"
    IO.println s!"{n} watched items; {na} with an alert"
    return 0
  | _ => IO.eprintln "usage: RunWatch.lean <in.tsv> <out.tsv>"; return 2
