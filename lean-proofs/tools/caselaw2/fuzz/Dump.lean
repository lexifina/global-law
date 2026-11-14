import LegalProofs.CaseLaw2.Data
import LegalProofs.CaseLaw2.Certificate

/-!
# Fuzz dumper: what the Lean glue parsed (tools/caselaw2/fuzz, caselaw-lean-2/FUZZ.md)

`lake env lean --run tools/caselaw2/fuzz/Dump.lean <nodes> <case-dir | @list-file>...` loads each case dir with the runner's own
loaders (`Data.loadTables`, `Data.loadDecisions`) and writes, into `<case-dir>/lean/`:
* `<file>` for every SCHEMA file: the rows it kept, re-serialised column for column (so a second load of `lean/`
  must give the same rows: the round-trip property);
* `treatment_witness.tsv`, `treatment_class.tsv` (optional tables; round 5): the rows kept, when the case has the file;
* `problems.tsv`: file, rows, bad;
* `quotes.tsv`: table, row id, `Cert.quoteOk` (with only the row's own hash), and the window slice the checker
  compares, `Cert.slice (Cert.norm w.text) (start - start0) (stop - start)` (`-` when no window covers).
-/

open CaseLaw2 CaseLaw2.Data CaseLaw2.Tsv Std

def b (x : Bool) : String := if x then "1" else "0"
def certS (c : Data.Cert) : List String := [c.textSha, toString c.start, toString c.stop, c.quote, c.evidence, c.part]
def ppmS (n : Nat) : String :=
  let f := toString (n % 1000000)
  let pad := String.ofList (List.replicate (6 - f.length) '0')
  toString (n / 1000000) ++ "." ++ pad ++ f

/-- An enumeration code back to its string; 255 (a value the schema does not list) as `<255>`, which loads as 255. -/
def val (vals : Array String) (c : UInt8) : String := vals[c.toNat]?.getD "<255>"

def writeRows (p : System.FilePath) (rows : Array (List String)) : IO Unit :=
  IO.FS.writeFile p (String.join (rows.toList.map fun r => "\t".intercalate r ++ "\n"))

def quoteRow (wins : HashMap String (List Cert.Window)) (table id : String) (c : Data.Cert) : String :=
  let inp : Cert.Input :=
    { kind := .treat .followed, textSha := c.textSha, start := c.start, stop := c.stop,
      quote := c.quote, evidence := c.evidence, part := c.part, shas := [c.textSha],
      windows := wins.getD c.textSha [], ordered := true, authority := some true }
  let sl := match Cert.coveringWindow inp with
    | some w => Cert.slice (Cert.norm w.text) (c.start - w.start0) (c.stop - c.start)
    | none => "-"
  s!"{table}\t{id}\t{b (Cert.quoteOk inp)}\t{sl}"

def dumpDir (nodes : Nat) (dir : System.FilePath) : IO Unit := do
  let t ← loadTables dir
  let (d, pd) ← loadDecisions (dir / "decisions2.tsv") nodes (fun _ => true)
  let o := dir / "lean"
  IO.FS.createDirAll o
  writeRows (o / "courts2.tsv") (t.courts.map fun r => [toString r.court, toString r.epochFrom, toString r.epochTo,
    r.name, toString r.system, r.tier, r.lastResortFor, toString r.circuit, toString r.unit, r.src, r.tag])
  writeRows (o / "succession.tsv") (t.succession.map fun r =>
    [toString r.old, toString r.new, toString r.date, r.kind, r.src, r.tag])
  writeRows (o / "adoption.tsv") (t.adoption.map fun r =>
    [toString r.adopter, toString r.source, toString r.upTo, r.filter, r.force, r.src, r.tag])
  writeRows (o / "system_rules.tsv") (t.rules.map fun r =>
    [toString r.system, r.rule, r.value, toString r.dateFrom, toString r.dateTo, r.src, r.tag])
  writeRows (o / "history.tsv") (t.history.map fun r =>
    [r.id, toString r.target, toString r.by_, toString r.date, r.kind, r.scope] ++ certS r.cert ++ [r.src])
  writeRows (o / "treatments.tsv") (t.treatments.map fun r =>
    [r.id, toString r.by_, toString r.target, toString r.date, r.kind, r.scope, r.temporal, b r.explicit] ++
      certS r.cert ++ [r.reader, ppmS r.confidence])
  -- cert_text and holdings_cert_text are concatenated by loadTables; written back as one file
  writeRows (o / "cert_text.tsv") (t.certText.map fun r => [r.textSha, toString r.start0, toString r.stop0, r.window])
  writeRows (o / "issues.tsv") (t.issues.map fun r => [r.key, r.label, r.domain, r.usc, r.question, r.src])
  writeRows (o / "holdings.tsv") (t.holdings.map fun r =>
    [r.id, toString r.node, r.issue, r.proposition, r.answer, r.role] ++ certS r.cert ++ [r.reader, ppmS r.confidence])
  writeRows (o / "marks.tsv") (t.marks.map fun r => [toString r.node, r.issue, r.author, r.proposition, r.src, r.tag])
  writeRows (o / "lawchanges.tsv") (t.lawchanges.map fun r => [r.id, r.law, r.uscBlock, toString r.enacted,
    toString r.effective, toString r.retroactiveTo, r.src])
  writeRows (o / "supersessions.tsv") (t.supersessions.map fun r => [r.id, toString r.target, r.issue, r.lawchange,
    r.evidence, ppmS r.score, b r.explicit, r.src])
  -- the optional tables (round 4 witness rows, round 5 class claims): written only when the case has the file, so
  -- that a second load is in the same mode (`round5` = the class file exists, even empty)
  if ← (dir / "treatment_witness.tsv").pathExists then
    writeRows (o / "treatment_witness.tsv") (t.witness.map fun r => [r.id, toString r.node, r.byEvidence, r.src])
  if t.round5 then
    writeRows (o / "treatment_class.tsv") (t.classes.map fun r => [r.id, r.claim, r.fieldLimit, r.doctrine, r.src])
  let mut dec : Array (List String) := #[]
  for n in [0:nodes] do
    if d.has n then
      dec := dec.push [toString n, toString d.court[n]!, toString d.date[n]!, toString d.unit[n]!,
        val benchValues (d.bench.get! n), val publicationValues (d.publication.get! n), val formValues (d.form.get! n),
        d.sha.getD n "", "-"]
  writeRows (o / "decisions2.tsv") dec
  writeRows (o / "problems.tsv") ((t.problems.push pd).map fun p => [p.file, toString p.rows, toString p.bad])
  let wins : HashMap String (List Cert.Window) := t.certText.foldl (fun m r =>
    m.insert r.textSha ({ start0 := r.start0, stop0 := r.stop0, text := r.window } :: m.getD r.textSha [])) {}
  let q := (t.treatments.map fun r => quoteRow wins "treatments" r.id r.cert) ++
    (t.history.map fun r => quoteRow wins "history" r.id r.cert) ++
    (t.holdings.map fun r => quoteRow wins "holdings" r.id r.cert)
  IO.FS.writeFile (o / "quotes.tsv") (String.join (q.toList.map (· ++ "\n")))

def main (args : List String) : IO UInt32 := do
  match args with
  | n :: args =>
    let nodes := n.toNat!
    -- `@file` stands for the case dirs listed in that file, one per line (long lists overflow a command line)
    let mut dirs : List String := []
    for x in args do
      if x.startsWith "@" then
        dirs := dirs ++ ((← IO.FS.readFile (x.drop 1).toString).splitOn "\n").filter (· ≠ "")
      else dirs := dirs ++ [x]
    for dir in dirs do
      try dumpDir nodes dir
      catch e => IO.eprintln s!"CRASH {dir}: {e}"
    return 0
  | [] => IO.eprintln "usage: Dump.lean <nodes> <case-dir>..."; return 2
