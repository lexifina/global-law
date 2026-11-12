import LegalProofs.USCaseLaw.Overrides

/-!
# Runner: override candidates over every citation

    lake env lean --run LegalProofs/USCaseLaw/RunOverrides.lean <in.tsv> <window years> <out.tsv>

Each input row: row id, the day decided, the evidence flag (0/1, read outside Lean: the law or its committee report
names the decision, or the decision quoted the words the law struck), then the section's versions in order, each
`day,law,text,sub` as for `RunStatuteText.lean`.
Each output row: row id, the day of the first rewrite of the cited words (0 if none), whether a law made it (0/1), the
day of the first rewriting law (0 if none), override candidate (0/1).
-/

open Legal.USCaseLaw

def clean (s : String) : String := String.ofList (s.toList.filter (fun c => c != '\r' && c != ' ' && c != '\n'))

def parseV (s : String) : SVersion :=
  match (s.splitOn ",").toArray.map (·.toNat!) with
  | #[d, l, x, y] => ⟨d, l == 1, x, y⟩
  | _ => ⟨0, false, 0, 0⟩

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, years, out] =>
    let y := years.toNat!
    let s ← IO.FS.readFile inp
    let o ← IO.FS.Handle.mk out .write
    let mut n := 0
    let mut rw := 0
    let mut byLaw := 0
    let mut inWin := 0
    let mut cand := 0
    for l in s.splitOn "\n" do
      if l.isEmpty then continue
      let f := (l.splitOn "\t").toArray.map clean
      let d := f[1]!.toNat!
      let e := f[2]! == "1"
      let h : List SVersion := (f.toList.drop 3).map parseV
      let r := firstRewrite h d
      let fl := firstRewritingLaw h d
      let c := overrideCandidate h d y e
      n := n + 1
      if r.isSome then rw := rw + 1
      if fl.isSome then byLaw := byLaw + 1
      if overrideCandidate h d y true then inWin := inWin + 1
      if c then cand := cand + 1
      let b (x : Bool) := if x then 1 else 0
      o.putStrLn s!"{f[0]!}\t{(r.map (·.from_)).getD 0}\t{b fl.isSome}\t{(fl.map (·.from_)).getD 0}\t{b c}"
    IO.println s!"{n} citations; words rewritten since {rw}; first rewrite by a law {byLaw}; within {y} years {inWin}; override candidates (with evidence) {cand}"
    return 0
  | _ => IO.eprintln "usage: RunOverrides.lean <in.tsv> <window years> <out.tsv>"; return 2
