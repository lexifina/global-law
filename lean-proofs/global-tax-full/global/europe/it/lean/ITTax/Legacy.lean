import ITTax.Household

open Lean TaxKernel

/-- `ittax [--euro] [--rent=cedolare|irpef] < households.jsonl`: contract output lines, money in euros with cents
(`--euro`: whole euros, the kernel's `Country` convention). -/
partial def loop (args : List String) (h o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then
    match Json.parse t with
    | .error e => o.putStrLn (errorLine "" s!"bad JSON: {e}")
    | .ok j =>
      match parseCanon j with
      | .error e => o.putStrLn (errorLine "" e)
      | .ok c =>
        if args.contains "--euro" then o.putStrLn (Json.compress (ITTax.country.computeWith args c).toJson)
        else o.putStrLn (Json.compress (ITTax.toJsonCents (ITTax.out args c)))
  loop args h o

def legacyMain (args : List String) : IO UInt32 := do
  if args.contains "--version" || args.contains "--help" then
    return ← countryMain ITTax.country args
  let o ← IO.getStdout
  loop args (← IO.getStdin) o
  o.flush
  return 0
