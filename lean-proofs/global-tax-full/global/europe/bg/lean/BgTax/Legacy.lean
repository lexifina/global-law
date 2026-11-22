import BgTax

/-! `bgtax`: the kernel's runner, except that money is written in leva with stotinki (the model computes in stotinki,
the kernel's `Out.toJson` would write whole units); copied from the Portuguese model's writer. -/

open TaxKernel Lean

def jLev (c : Int) : Json := Json.num ⟨c, 2⟩

def outJson (o : Out) : Json :=
  Json.mkObj [("id", Json.str o.id), ("country", Json.str o.country), ("currency", Json.str o.currency),
    ("incomeTax", jLev o.incomeTax),
    ("surtaxes", Json.mkObj (o.surtaxes.map fun (k, v) => (k, jLev v))),
    ("localIncomeTax", jLev o.localIncomeTax), ("employeeSocial", jLev o.employeeSocial),
    ("benefits", jLev o.benefits), ("detail", Json.mkObj o.detail),
    ("unsupported", Json.arr (o.unsupported.map Json.str).toArray)]

def runLineBG (args : List String) (line : String) : String :=
  match Json.parse line with
  | .error e => errorLine "" s!"bad JSON: {e}"
  | .ok j =>
    match parseCanon j with
    | .error e =>
      let id := match j.getObjVal? "id" with | .ok (.str s) => s | _ => ""
      errorLine id e
    | .ok c => Json.compress (outJson (BgTax.country.computeWith args c))

partial def loopBG (args : List String) (h o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then
    o.putStrLn (runLineBG args t)
    o.flush
  loopBG args h o

def legacyMain (args : List String) : IO UInt32 := do
  if args.contains "--help" || args.contains "--version" then
    return ← countryMain BgTax.country args
  let o ← IO.getStdout
  loopBG args (← IO.getStdin) o
  return 0
