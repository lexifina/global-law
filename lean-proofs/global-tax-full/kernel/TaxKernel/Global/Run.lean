import TaxKernel.Global.Consumption

/-!
# TaxKernel.Global.Run (2.0.0): the exe speaks both contracts

    def main (args : List String) : IO UInt32 :=
      TaxKernel.Global.globalMain (TaxKernel.worldMain XxTax.country) XxGlobal.model args

* **Without `--global`** the exe is the 1.x exe: `globalMain legacy m args = legacy args` (`globalMain_legacy`), so
  every 1.x output line, `--version` and `--help` are byte-identical.
* **With `--global`** each input line is a `CanonGlobal` (`schema: "global/2.0"`; a 1.x line is read as `ofCanon` of
  its parse, `parseGlobal_legacy`), and each output line is `OutGlobal.toJson`: the 1.x line verbatim under `"pit"`,
  every charge under `"taxes"`, totals by OECD heading, what is not levied (cited) and what is not modelled. The other
  options are passed to the PIT model unchanged (`--global` removed).
-/

namespace TaxKernel.Global
open Lean TaxKernel

def kernelVersionGlobal : String := "TaxKernel 2.0.0 (2026-11-21)"

def globalLine (m : GlobalModel) (args : List String) (line : String) : String :=
  match Json.parse line with
  | .error e => errorLine "" s!"bad JSON: {e}"
  | .ok j =>
    match parseGlobal j with
    | .error e =>
      let id := match j.getObjVal? "id" with | .ok (.str s) => s | _ => ""
      errorLine id e
    | .ok g => Json.compress (m.computeGlobal args g).toJson

partial def globalLoop (m : GlobalModel) (args : List String) (h o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then
    o.putStrLn (globalLine m args t)
  globalLoop m args h o

def globalRun (m : GlobalModel) (args : List String) : IO UInt32 := do
  let rest := args.filter (· != "--global")
  if rest.contains "--version" then
    IO.println (Json.compress (Json.mkObj [("country", Json.str m.code), ("name", Json.str m.name),
      ("currency", Json.str m.currency), ("year", Json.str m.year), ("kernel", Json.str kernelVersionGlobal),
      ("schema", Json.str "global/2.0")]))
    return 0
  let o ← IO.getStdout
  globalLoop m rest (← IO.getStdin) o
  o.flush
  return 0

/-- The exe's `main`: the 1.x `main` unless `--global` is given. -/
def globalMain (legacy : List String → IO UInt32) (m : GlobalModel) (args : List String) : IO UInt32 :=
  if args.contains "--global" then globalRun m args else legacy args

/-- Without `--global` the exe is exactly the 1.x exe. -/
theorem globalMain_legacy (legacy : List String → IO UInt32) (m : GlobalModel) (args : List String)
    (h : args.contains "--global" = false) : globalMain legacy m args = legacy args := by
  unfold globalMain; rw [h]; rfl

end TaxKernel.Global
