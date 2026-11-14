import LegalProofs.CaseLaw2.Run

/-!
# Fuzz: the runner's `main` over many case dirs in one interpreter process (tools/caselaw2/fuzz)

`FUZZ_LIST=<file of case dirs> FUZZ_EDGES=<edges dir> lake env lean tools/caselaw2/fuzz/RunBatch.lean`

Runs `CaseLaw2.Run.main [dir, edges, 0, 1, dir/runner, 1000, 20261112]` for each dir, exactly the arguments
`run_lean.sh` passes to one shard, and writes the exit code (or the exception) to `dir/runner/rc.txt`. Each case is
announced on stderr first, so a `PANIC` message there is attributed to the case before it. This is the
interpreted path `run_lean.sh` falls back to when Windows Application Control blocks the compiled `caselaw2.exe`.
-/

#eval show IO Unit from do
  let list ← IO.FS.readFile ((← IO.getEnv "FUZZ_LIST").getD "")
  let edges := (← IO.getEnv "FUZZ_EDGES").getD ""
  for d in list.splitOn "\n" do
    if d.isEmpty then continue
    IO.eprintln s!"CASE {d}"
    -- FUZZ_OUTNAME (round 5): the output folder's name, so that two runners can read the same case dir
    let out := System.FilePath.mk d / ((← IO.getEnv "FUZZ_OUTNAME").getD "runner")
    IO.FS.createDirAll out
    let rc ← try
        let r ← CaseLaw2.Run.main [d, edges, "0", "1", out.toString, "1000", "20261112"]
        pure s!"{r}"
      catch e => pure s!"EXCEPTION {e}"
    IO.FS.writeFile (out / "rc.txt") rc
