import Compare.Us

/-!
# The 1.x US exe as `cmptax us` runs it (from cmp/compare/lean/Compare/Main.lean, the `us` branch only)

`legacyMain args` prints, for each input line, exactly what `cmptax us` prints: the US output line or the same
error line. The French branch of `cmptax` is not part of this project.
-/

open Lean Compare

def usRunOne (line : String) : String :=
  match Json.parse line with
  | .error e => Json.compress (Json.mkObj [("error", Json.str s!"bad JSON: {e}")])
  | .ok j =>
    match parseCanon j with
    | .error e => Json.compress (Json.mkObj [("error", Json.str e)])
    | .ok c => Json.compress (Us.out c).toJson

partial def usLoop (h : IO.FS.Stream) (o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then o.putStrLn (usRunOne t)
  usLoop h o

def legacyMain (_ : List String) : IO UInt32 := do
  usLoop (← IO.getStdin) (← IO.getStdout)
  return 0
