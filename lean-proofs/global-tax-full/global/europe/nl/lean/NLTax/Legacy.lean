import NLTax.Household

/-!
# `nltax`: the contract runner (reads canonical households as JSONL on stdin or from a file, writes one output line
each, euros with cents). Options: `--oecd` (the OECD's Taxing Wages conventions: its employee pension contribution
and the exact band sum instead of the statute's table), `--oecd-pension` (only its pension contribution), `--band-sum` (band sum only), `--split-half` (joint items
of partners half each, art. 2.17 lid 3, instead of the best allocation), `--version`.
-/

open Lean NLTax

def optsOf (args : List String) : Opts :=
  { oecd := args.contains "--oecd" || args.contains "--oecd-pension", bandSum := args.contains "--oecd" || args.contains "--band-sum",
    splitHalf := args.contains "--split-half", june30 := args.contains "--june30" }

def lineOut (o : Opts) (t : String) : String :=
  match Json.parse t with
  | .error e => (Json.mkObj [("error", Json.str s!"bad JSON: {e}")]).compress
  | .ok j =>
    match TaxKernel.parseCanon j with
    | .error e => (Json.mkObj [("error", Json.str e)]).compress
    | .ok c => (outJson o c).compress

partial def loop (o : Opts) (h out : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then
    out.putStrLn (lineOut o t)
  loop o h out

def legacyMain (args : List String) : IO UInt32 := do
  if args.contains "--version" then
    IO.println (Json.compress (Json.mkObj [("country", Json.str "NL"), ("name", Json.str "Netherlands"),
      ("currency", Json.str "EUR"), ("year", Json.str "2025"), ("kernel", Json.str TaxKernel.kernelVersion)]))
    return 0
  let o := optsOf args
  let files := args.filter fun a => !a.startsWith "--"
  let input ← match files with
    | p :: _ => do let h ← IO.FS.Handle.mk p .read; pure (IO.FS.Stream.ofHandle h)
    | [] => IO.getStdin
  let out ← IO.getStdout
  loop o input out
  out.flush
  return 0
