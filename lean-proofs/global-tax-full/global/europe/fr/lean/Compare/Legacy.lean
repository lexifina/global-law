import Compare.Us
import Compare.Fr

/-!
# `cmptax`: the contract's runner for the United States and France

    cmptax [us|fr|all] < households.jsonl > results.jsonl

Reads one canonical household per line (`cmp/shared/CONTRACT.md`) and writes one result line per household and
country, in the same order (`all`: the US line then the French line). A line that cannot be read gives
`{"id": ..., "error": ...}`.
-/

open Lean Compare

def runOne (which : String) (args : List String) (line : String) : List String :=
  match Json.parse line with
  | .error e => [Json.compress (Json.mkObj [("error", Json.str s!"bad JSON: {e}")])]
  | .ok j =>
    match parseCanon j with
    | .error e => [Json.compress (Json.mkObj [("error", Json.str e)])]
    | .ok c =>
      (if which == "us" || which == "all" then [Json.compress (Us.out c).toJson] else [])
        ++ (if which == "fr" || which == "all" then [Json.compress (Fr.out c args).toJson] else [])

partial def loop (which : String) (args : List String) (h : IO.FS.Stream) (o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then
    for s in runOne which args t do o.putStrLn s
  loop which args h o

def legacyMain (args : List String) : IO UInt32 := do
  let which := args.headD "all"
  if !(["us", "fr", "all"].contains which) then
    IO.eprintln "usage: cmptax [us|fr|all] < households.jsonl"
    return 2
  loop which args (← IO.getStdin) (← IO.getStdout)
  return 0
