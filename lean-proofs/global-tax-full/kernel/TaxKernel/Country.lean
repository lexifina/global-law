import TaxKernel.Canon

/-!
# TaxKernel.Country: the interface every country implements, and the contract's runner

A country is a value of `Country`: its code, currency, year and `compute : Canon → Out`. Options from the command
line (e.g. `--separate`, `--region=QC`) reach `computeWith`, which defaults to `compute`.

    def country : TaxKernel.Country :=
      { code := "CA", name := "Canada", currency := "CAD", year := "2025", compute := CaTax.out }
    def main (args : List String) : IO UInt32 := TaxKernel.countryMain country args

`countryMain` reads one canonical household per line from stdin (`cmp/shared/CONTRACT.md`) and writes one
output line per household, in order; a line that cannot be read gives `{"id":…, "error":…}` (the harness treats it
as a failure). `--version` prints the code, year and kernel version; `--help` the usage.

`Out.make` builds an output with every contract field; `Out.d` / `Out.dStr` make `detail` entries.
-/

namespace TaxKernel
open Lean

def kernelVersion : String := "TaxKernel 1.2 (2026-11-19)"

structure Country where
  code : String
  name : String := ""
  currency : String
  year : String := "2025"
  compute : Canon → Out
  computeWith : List String → Canon → Out := fun _ c => compute c

/-- An output line with the contract's fields. -/
def Out.make (c : Canon) (country currency : String) (incomeTax : Int) (surtaxes : List (String × Int) := [])
    (localIncomeTax : Int := 0) (employeeSocial : Int := 0) (benefits : Int := 0)
    (detail : List (String × Json) := []) (unsupported : List String := []) : Out :=
  { id := c.id, country, currency, incomeTax, surtaxes, localIncomeTax, employeeSocial, benefits, detail,
    unsupported }

/-- A detail entry holding an integer. -/
def Out.d (k : String) (v : Int) : String × Json := (k, Lean.toJson v)
/-- A detail entry holding a string. -/
def Out.dStr (k : String) (v : String) : String × Json := (k, Json.str v)
/-- A detail entry holding a boolean. -/
def Out.dBool (k : String) (v : Bool) : String × Json := (k, Json.bool v)

/-- Net income of an output for its household (contract). -/
def Out.netOf (o : Out) (c : Canon) : Int := o.net c.gross

def errorLine (id : String) (e : String) : String :=
  Json.compress (Json.mkObj [("id", Json.str id), ("error", Json.str e)])

def runLine (k : Country) (args : List String) (line : String) : String :=
  match Json.parse line with
  | .error e => errorLine "" s!"bad JSON: {e}"
  | .ok j =>
    match parseCanon j with
    | .error e =>
      let id := match j.getObjVal? "id" with | .ok (.str s) => s | _ => ""
      errorLine id e
    | .ok c => Json.compress (k.computeWith args c).toJson

partial def runLoop (k : Country) (args : List String) (h o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then
    o.putStrLn (runLine k args t)
  runLoop k args h o

/-- The `<cc>tax` executable's `main`. -/
def countryMain (k : Country) (args : List String) : IO UInt32 := do
  if args.contains "--help" then
    IO.println s!"usage: {k.code.toLower}tax [options] < households.jsonl > results.jsonl\n{k.name} {k.year}, {kernelVersion}"
    return 0
  if args.contains "--version" then
    IO.println (Json.compress (Json.mkObj [("country", Json.str k.code), ("name", Json.str k.name),
      ("currency", Json.str k.currency), ("year", Json.str k.year), ("kernel", Json.str kernelVersion)]))
    return 0
  let o ← IO.getStdout
  runLoop k args (← IO.getStdin) o
  o.flush
  return 0

end TaxKernel
