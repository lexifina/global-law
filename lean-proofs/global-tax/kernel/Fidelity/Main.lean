import Fidelity.Uk
import Fidelity.De

/-!
# `kfid`: the kernel re-expressions of the UK and German rules, for the fidelity check

    kfid uk < households.jsonl     -> {"id", "incomeTax_p", "ni_p", "benefits_p", "ma"}            (pence)
    kfid de < cases.jsonl          -> {"id", "tariff", "soli_c", "members": [{"RV_c", ...}]}       (euro / cents)

DE input lines: {"id", "joint": bool, "zvE": euros, "soliBase": the tariff tax that is the Soli base (SolZG § 3 (2)), euros, "members": [{"wages": euros, "kids": n,
"childless": bool}]}.
-/

open Lean TaxKernel

def ukLine (j : Json) : Json :=
  match parseCanon j with
  | .error e => Json.mkObj [("error", Json.str e)]
  | .ok c =>
    let (it, ni, ben, el) := Fidelity.Uk.household c
    Json.mkObj [("id", Json.str c.id), ("incomeTax_p", toJson it), ("ni_p", toJson ni), ("benefits_p", toJson ben),
      ("ma", Json.str el)]

def deLine (j : Json) : Json :=
  let joint := boolField j "joint"
  let zve := intField j "zvE"
  let sb := intField j "soliBase"
  let ms := (arrField j "members").toList.map fun m =>
    let w := intField m "wages"
    let cs := Fidelity.De.contributions (natField m "kids") (boolField m "childless")
    Json.mkObj (cs.map fun c => (c.name ++ "_c", toJson (c.amount (100 * w))))
  let id := match j.getObjVal? "id" with | .ok (.str s) => s | _ => ""
  Json.mkObj [("id", Json.str id), ("tariff", toJson (Fidelity.De.tariff joint zve)),
    ("soli_c", toJson ((Fidelity.De.soli joint).amount (100 * sb))),
    ("members", Json.arr ms.toArray)]

partial def loop (f : Json → Json) (h o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then
    match Json.parse t with
    | .ok j => o.putStrLn (Json.compress (f j))
    | .error e => o.putStrLn (Json.compress (Json.mkObj [("error", Json.str e)]))
  loop f h o

def main (args : List String) : IO UInt32 := do
  let f := if args.headD "uk" == "de" then deLine else ukLine
  loop f (← IO.getStdin) (← IO.getStdout)
  return 0
