import ESTax.Withholding

/-!
# `estax`: contract JSONL in, contract JSONL out (euros with cents)

`estax [--separate|--joint] [file]` reads households (one JSON object per line) from the file or stdin.
Output lines follow `cmp/shared/CONTRACT.md`; money in euros with two decimals (the kernel's `Out` is whole units,
so the line is written here: kernel gap "cents output").
-/

namespace ESTax
open TaxKernel Lean

def jc (c : Int) : Json := Json.num ⟨c, 2⟩

def liqJson (l : Liq) : Json :=
  Json.mkObj [("baseImponibleGeneral", jc l.big), ("baseImponibleAhorro", jc l.bia), ("reduccionArt20", jc l.red20),
    ("reduccionPlanesPensiones", jc l.redPP), ("baseLiquidableGeneral", jc l.blg), ("baseLiquidableAhorro", jc l.bla),
    ("cuotaIntegraEstatal", jc l.cie), ("cuotaIntegraAutonomica", jc l.cia),
    ("donativosEstatal", jc l.donEst), ("donativosAutonomica", jc l.donAut),
    ("madridNacimiento", jc l.madNac), ("madridDosDescendientes", jc l.madFam2),
    ("cuotaLiquidaEstatal", jc l.cle), ("cuotaLiquidaAutonomica", jc l.cla), ("deduccionSMI_DA61", jc l.smi),
    ("maternidad_art81", jc l.maternidad), ("familiaNumerosa_art81bis", jc l.famNum),
    ("state", jc l.stateTax), ("madrid", jc l.madridTax)]

def unsupportedNotes : List String :=
  ["region fixed: Comunidad de Madrid (régimen común)",
   "selfEmployment taken as rendimiento neto de actividades económicas; RETA contributions not computed",
   "rentalIncome taken as net rendimiento del capital inmobiliario; art. 23.2 reducción only if rentalReductionPct given",
   "base del ahorro: interest, dividends and gains summed (art. 49 netting of losses not modelled)",
   "no universal cash child benefit in Spain (benefits = 0; IMV complemento de ayuda para la infancia is means-tested, not modelled)",
   "art. 81.2 guardería increment, art. 81 bis disability items, Madrid deductions other than arts. 4 and 14 not modelled"]

/-- Round 5: what is not year-specific for 2022-2024 (`Params.YP`). -/
def yearNotes (y : Nat) : List String :=
  if y ≥ 2025 then [] else
  [s!"ejercicio {y}: scales, art. 20, Madrid mínimos and deductions (arts. 1, 2, 2 bis, 4, 14, 18.1) and the SS tope máximo and MEI are those of {y}; the withholding detail uses the 2025 AEAT procedure",
   "art. 81 (maternidad) applied with the 2023+ worker condition and without the pre-2023 limit of contributions accrued after the birth"]

def compute (force : Option Filing) (c : Canon) : Json :=
  let h := toHH c
  let r := assess h force
  let st := sumL (r.liqs.map Liq.stateTax)
  let md := sumL (r.liqs.map Liq.madridTax)
  Json.mkObj [("id", Json.str c.id), ("country", Json.str "ES"), ("currency", Json.str "EUR"),
    ("incomeTax", jc st), ("surtaxes", Json.mkObj []), ("localIncomeTax", jc md),
    ("employeeSocial", jc r.ss), ("benefits", jc 0),
    ("detail", Json.mkObj [("region", Json.str "Madrid"), ("filing", Json.str r.filing.name),
      ("totalIndividual", jc r.sepTotal),
      ("totalConjunta", match r.jointTotal with | some t => jc t | none => Json.null),
      ("returns", Json.arr (r.liqs.map liqJson).toArray),
      ("withholding", Json.arr ((List.range h.n).map fun i =>
        let w := withholding (h.whIn i)
        Json.mkObj [("situacion", Json.num ⟨(h.whIn i).sit, 0⟩), ("tipo", jc w.tipoBp), ("importe", jc w.importe)]).toArray),
      ("withholdingTotal", jc (sumL ((List.range h.n).map fun i => (withholding (h.whIn i)).importe)))]),
    ("unsupported", Json.arr ((unsupportedNotes ++ yearNotes c.year).map Json.str).toArray)]

def runLine (force : Option Filing) (line : String) : String :=
  match Json.parse line with
  | .error e => Json.compress (Json.mkObj [("error", Json.str s!"bad JSON: {e}")])
  | .ok j =>
    match parseCanon j with
    | .error e => Json.compress (Json.mkObj [("error", Json.str e)])
    | .ok c =>
      let f := match force with
        | some f => some f
        | none => match c.str? "filing" with
          | some "joint" => some Filing.joint
          | some "separate" => some Filing.separate
          | _ => none
      Json.compress (compute f c)

partial def loop (force : Option Filing) (h o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then
    o.putStrLn (runLine force t)
    o.flush
  loop force h o

end ESTax

def legacyMain (args : List String) : IO UInt32 := do
  if args.contains "--version" then
    IO.println "{\"country\":\"ES\",\"name\":\"Spain (state + Comunidad de Madrid)\",\"currency\":\"EUR\",\"year\":\"2025\"}"
    return 0
  let force := if args.contains "--separate" then some ESTax.Filing.separate
    else if args.contains "--joint" then some ESTax.Filing.joint else none
  let files := args.filter fun a => !a.startsWith "--"
  let input ← match files with
    | p :: _ => do let h ← IO.FS.Handle.mk p .read; pure (IO.FS.Stream.ofHandle h)
    | [] => IO.getStdin
  ESTax.loop force input (← IO.getStdout)
  return 0
