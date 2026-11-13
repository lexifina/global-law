import LegalProofs.CaseLaw2.Run

/-!
# Batch driver for the interpreted runner (differential testing)

Windows Application Control may block the compiled `caselaw2.exe`; the interpreter (`lake env lean --run Run.lean`)
then spends ~12 s elaborating `Run.lean` on every call. This file imports the built `Run` module once and runs
`CaseLaw2.Run.main` (the same program, shard 0 of 1) on every universe listed in the file named by the environment
variable `CASELAW2_BATCH`: one line per universe, `<data-dir>\t<edges-dir>\t<out-dir>\t<nodes>\t<asOf>`.

    cd lean-proofs && lake build LegalProofs.CaseLaw2.Run
    CASELAW2_BATCH=list.tsv lake env lean <caselaw-lean-2>/runner/RunBatch.lean

Each universe's exit code is printed as `BATCH <out-dir> <code>`.
-/

#eval show IO Unit from do
  let some list ← IO.getEnv "CASELAW2_BATCH" | IO.println "CASELAW2_BATCH not set"
  let lines := (← IO.FS.readFile list).splitOn "\n" |>.filter (· ≠ "")
  for l in lines do
    match l.splitOn "\t" with
    | [d, e, o, n, a] =>
      let rc ← try CaseLaw2.Run.main [d, e, "0", "1", o, n, a]
        catch err => do IO.eprintln s!"{o}: {err}"; pure 1
      IO.println s!"BATCH\t{o}\t{rc}"
    | _ => IO.println s!"BATCH\tbad line\t{l}"
