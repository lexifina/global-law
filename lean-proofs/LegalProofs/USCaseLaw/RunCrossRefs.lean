import LegalProofs.USCaseLaw.CrossRefs

/-!
# Runner: every cross-reference in the US Code, on every day it could change

    lake env lean --run LegalProofs/USCaseLaw/RunCrossRefs.lean <in.tsv> <today yyyymmdd> <out.tsv>

Input (from `tools/caselaw/usc_xrefs.py build`): a line `T <target> <versions>` for each target section, each version
`day,live,paths` (paths space-separated, designations joined by "."; only the paths some reference names, see
`resolvesIn_restrict`), followed by its references, `R <row id> <from day> <path> <referring versions>`, each referring
version `day,makes`. The status is judged from the `from` day (the first day both titles are in the record).

Output per reference: row id, its status on each day it changed (`day:s`, s = a absent, o resolves, d dangles), judged
on the `from` day and on every later day the referring section or the target has a version (by `status_stable`, the
only days it can change), and its status at the end of each year 1995..2026 (one character each, `-` before `from`).
-/

open Legal.USCaseLaw.CrossRefs

def clean (s : String) : String := String.ofList (s.toList.filter (fun c => c != '\r' && c != '\n'))

def parsePath (s : String) : Path := if s.isEmpty then [] else s.splitOn "."

def parseT (s : String) : TVersion :=
  match s.splitOn "," with
  | [d, l, ps] => ⟨d.toNat!, l == "1", (ps.splitOn " ").filter (· ≠ "") |>.map parsePath⟩
  | _ => ⟨0, false, []⟩

def parseR (s : String) : RVersion :=
  match s.splitOn "," with
  | [d, m] => ⟨d.toNat!, m == "1"⟩
  | _ => ⟨0, false⟩

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, today, out] =>
    let now := today.toNat!
    let s ← IO.FS.readFile inp
    let o ← IO.FS.Handle.mk out .write
    let mut tgt : List TVersion := []
    let mut n := 0
    let mut dNow := 0
    let mut live := 0
    for l in s.splitOn "\n" do
      let l := clean l
      if l.isEmpty then continue
      let f := l.splitOn "\t"
      match f with
      | "T" :: _ :: vs => tgt := vs.map parseT
      | ["R", rid, frm, p, svs] =>
        let from_ := frm.toNat!
        let path := parsePath p
        let src := (svs.splitOn ";").map parseR
        let later := (src.map (·.from_) ++ tgt.map (·.from_)).filter (fun d => from_ < d && d ≤ now)
        let days := (from_ :: later).mergeSort.eraseDups
        let mut prev : Option Status := none
        let mut trans : Array String := #[]
        for d in days do
          let st := status src tgt path d
          if prev != some st then
            trans := trans.push s!"{d}:{st.code}"
          prev := some st
        let years := (List.range 32).map (fun i =>
          let y := 1995 + i
          let d := if y == 2026 then now else y * 10000 + 1231
          if d < from_ then '-' else (status src tgt path d).code)
        let stNow := status src tgt path now
        n := n + 1
        if stNow == .dangling then dNow := dNow + 1
        if stNow != .absent then live := live + 1
        o.putStrLn s!"{rid}\t{" ".intercalate trans.toList}\t{String.ofList years}"
      | _ => pure ()
    IO.println s!"{n} references; in force on {now}: {live}, dangling {dNow}"
    return 0
  | _ => IO.eprintln "usage: RunCrossRefs.lean <in.tsv> <today> <out.tsv>"; return 2
