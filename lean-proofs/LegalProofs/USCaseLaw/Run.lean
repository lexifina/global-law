import LegalProofs.USCaseLaw.Precedent
import Std.Data.HashMap

/-!
# Runner: the precedent checks over all US case law

    lake env lean --run LegalProofs/USCaseLaw/Run.lean <in-dir> <edges-shard.tsv> <out-prefix>

Reads (written by `tools/caselaw/encode.py`):
* `courts.tsv`     court index, system, tier (L/A/T/S), circuit
* `decisions.tsv`  decision id, court index, date (yyyymmdd)
* `acts.tsv`       overruling decision, overruled decision (read from the overruling decision's own words)
* `reports.tsv`    deciding decision, decision it says was overruled, the overruling decision it names (or -1)
* an edges shard   citing decision, cited decision

and writes `<out-prefix>.citations.tsv` (findings per citation), `<out-prefix>.summary.json`; with `reports.tsv`, the
answer Lean gives to each report (`<out-prefix>.reports.tsv`). Every decision uses the definitions of
`Precedent.lean`: `Record.valid`, `binds`, and the `overrulersOn` condition, looked up by target.
-/

open Legal.USCaseLaw Std

def parseTier : String → Tier
  | "L" => .last | "A" => .appellate | "S" => .special | _ => .trial

def readLines (p : System.FilePath) : IO (Array String) := do
  let s ← IO.FS.readFile p
  return (s.splitOn "\n").toArray.filter (· ≠ "")

/-- Drop carriage returns, newlines and spaces. -/
def clean (s : String) : String := String.ofList (s.toList.filter (fun c => c != '\r' && c != ' ' && c != '\n'))

def fieldsNat (l : String) : Array Nat := (l.splitOn "\t").toArray.map (fun x => (clean x).toNat!)

structure World where
  courts : Array Court
  court : Array Nat     -- court index per decision
  date : Array Nat
  events : Array Overruling
  byTarget : HashMap Nat (Array Overruling)

def World.dec (w : World) (i : Nat) : Decision :=
  { id := i, court := w.courts.getD (w.court.getD i 0) default, date := w.date.getD i 0 }

def World.record (w : World) : Record := { dec := w.dec, events := w.events.toList }

/-- The valid overrulings of `x` on or before day `d` (the `Record.overrulersOn` condition, by target). -/
def World.overrulersOn (w : World) (x d : Nat) : Array Overruling :=
  (w.byTarget.getD x #[]).filter (fun e => w.record.valid e && (w.dec e.by_).date ≤ d)

def load (dir : System.FilePath) : IO World := do
  let cl ← readLines (dir / "courts.tsv")
  let courts := cl.map (fun l =>
    let f := (l.splitOn "\t").toArray
    ({ id := f[0]!.toNat!, system := f[1]!.toNat!, tier := parseTier (clean f[2]!), circuit := f[3]!.toNat! } : Court))
  let dl ← readLines (dir / "decisions.tsv")
  let mut court : Array Nat := Array.replicate dl.size 0
  let mut date : Array Nat := Array.replicate dl.size 0
  for l in dl do
    let f := fieldsNat l
    court := court.set! f[0]! f[1]!
    date := date.set! f[0]! f[2]!
  let al ← readLines (dir / "acts.tsv")
  let events := al.map (fun l => let f := fieldsNat l; ({ by_ := f[0]!, target := f[1]! } : Overruling))
  let mut byTarget : HashMap Nat (Array Overruling) := {}
  for e in events do
    byTarget := byTarget.insert e.target ((byTarget.getD e.target #[]).push e)
  return { courts, court, date, events, byTarget }

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir, shard, out] =>
    let w ← load (System.FilePath.mk dir)
    let r := w.record
    -- the overruling acts: valid or not
    let mut invalid := 0
    let mut evLines : Array String := #[]
    for e in w.events do
      let v := r.valid e
      if !v then invalid := invalid + 1
      evLines := evLines.push s!"{e.by_}\t{e.target}\t{if v then 1 else 0}"
    IO.FS.writeFile (out ++ ".acts.tsv") ("\n".intercalate evLines.toList ++ "\n")
    -- citations
    let h ← IO.FS.Handle.mk shard .read
    let o ← IO.FS.Handle.mk (out ++ ".citations.tsv") .write
    let mut n := 0
    let mut later := 0
    let mut overruled := 0
    repeat
      let l ← h.getLine
      if l.isEmpty then break
      let f := fieldsNat l
      let i := f[0]!
      let j := f[1]!
      n := n + 1
      let y := w.dec i
      let x := w.dec j
      if y.date < x.date && x.date != 0 && y.date != 0 then
        later := later + 1
        o.putStrLn s!"later\t{i}\t{j}"
      match (w.overrulersOn j y.date).find? (fun e =>
          (w.dec e.by_).date < y.date && binds (w.dec e.by_).court y.court) with
      | some e =>
        overruled := overruled + 1
        o.putStrLn s!"overruled\t{i}\t{j}\t{e.by_}"
      | none => pure ()
    -- reports (only with the first shard)
    let rp := System.FilePath.mk dir / "reports.tsv"
    let mut rep := 0
    let mut repMatch := 0
    if (← rp.pathExists) && shard.endsWith "00.tsv" then
      let rl ← readLines rp
      let ro ← IO.FS.Handle.mk (out ++ ".reports.tsv") .write
      for l in rl do
        let f := (l.splitOn "\t").toArray
        let z := f[0]!.toNat!
        let x := f[1]!.toNat!
        let named := clean f[2]!
        let ov := w.overrulersOn x (w.dec z).date
        let byIds := ov.map (·.by_)
        let verdict :=
          if ov.isEmpty then "none"
          else if named.isEmpty || named == "-1" then "match"
          else if byIds.contains named.toNat! then "match"
          else "other"
        rep := rep + 1
        if verdict == "match" then repMatch := repMatch + 1
        ro.putStrLn s!"{z}\t{x}\t{named}\t{verdict}\t{",".intercalate (byIds.toList.map toString)}"
    IO.FS.writeFile (out ++ ".summary.json")
      s!"\{\"citations\": {n}, \"cites_later\": {later}, \"cites_overruled\": {overruled}, \"acts\": {w.events.size}, \"acts_invalid\": {invalid}, \"reports\": {rep}, \"reports_match\": {repMatch}}\n"
    IO.println s!"{shard}: {n} citations, {later} later, {overruled} overruled; acts {w.events.size} ({invalid} invalid); reports {repMatch}/{rep}"
    return 0
  | _ => IO.eprintln "usage: Run.lean <in-dir> <edges-shard.tsv> <out-prefix>"; return 2
