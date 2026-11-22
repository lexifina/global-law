import CYTax

/-! `cytax`: the kernel's runner, except that money is written in euros with cents (the model computes in cents;
the kernel's `Out.toJson` writes whole units). Detail fields ending in `_cents` stay in cents (copied from
PT's `PTTax/Main.lean`). Options: `--statute-si` (SI rates as printed in SIL art. 5/12), `--non-dom`. -/

open TaxKernel Lean

def jEur (c : Int) : Json := Json.num ⟨c, 2⟩

def outJson (o : Out) : Json :=
  Json.mkObj [("id", Json.str o.id), ("country", Json.str o.country), ("currency", Json.str o.currency),
    ("incomeTax", jEur o.incomeTax),
    ("surtaxes", Json.mkObj (o.surtaxes.map fun (k, v) => (k, jEur v))),
    ("localIncomeTax", jEur o.localIncomeTax), ("employeeSocial", jEur o.employeeSocial),
    ("benefits", jEur o.benefits), ("detail", Json.mkObj o.detail),
    ("unsupported", Json.arr (o.unsupported.map Json.str).toArray)]

def runLineCY (args : List String) (line : String) : String :=
  match Json.parse line with
  | .error e => errorLine "" s!"bad JSON: {e}"
  | .ok j =>
    match parseCanon j with
    | .error e =>
      let id := match j.getObjVal? "id" with | .ok (.str s) => s | _ => ""
      errorLine id e
    | .ok c => Json.compress (outJson (CYTax.country.computeWith args c))

partial def loopCY (args : List String) (h o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then
    o.putStrLn (runLineCY args t)
    o.flush
  loopCY args h o

def legacyMain (args : List String) : IO UInt32 := do
  if args.contains "--help" || args.contains "--version" then
    return ← countryMain CYTax.country args
  let o ← IO.getStdout
  loopCY args (← IO.getStdin) o
  return 0
