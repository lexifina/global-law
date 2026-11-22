import FrTax.Liquidation
import FrTax.Withholding

/-!
# Command-line runner

Reads one return per line on stdin, `id;year;BOX=VAL,BOX=VAL,...`, and prints one line per return:
`id;NBPT=..;RNG=..;RNI=..;IDRS=..;IDEC=..;ITRED=..;CITOT=..;IMPNET=..;REVKIRE=..` named after the M
variables they are compared with. Returns inside the withholding model's scope (`PAS.inScope`) also get the
withholding rates of art. 204 H and 204 M for September N+1 (in per cent, one decimal): `TXFOYER` (household
rate), `TXFOYER61` (diagnostic: the same with a tax under 61 € counted as nil), `PASNUM`, `PASDEN`, `PASIR`,
`PASX`, `PASTOT`, `PASII`; for a couple without flat-levy income `TXDEC1`, `TXDEC2` (individualised rates,
décote of couples) and `TXDEC1S`, `TXDEC2S` (the same with the décote of single people).

Default grids (art. 204 H, III): `G;id;rateYear;zone;monthlyBase` with zone `metropole`, `gmr` (Guadeloupe,
Martinique, La Réunion) or `gm` (Guyane, Mayotte) prints `id;GRID=rate`.
-/

open FrTax

def parseDecl (year : Nat) (s : String) : Decl :=
  let pairs := (s.splitOn ",").filterMap fun kv =>
    match kv.splitOn "=" with
    | [k, v] => (v.trimAscii.toString.toInt?).map fun n => (k.trimAscii.toString, n)
    | _ => none
  { year, boxes := pairs.foldl (fun m (k, v) => m.insert k v) {} }

def fmtParts (q : Int) : String :=
  let w := q / 4
  match q % 4 with
  | 0 => s!"{w}" | 1 => s!"{w}.25" | 2 => s!"{w}.5" | _ => s!"{w}.75"

def pasFields (p : Params) (d : Decl) : String :=
  if !PAS.inScope d then "" else
  let o := PAS.out p d
  let h := o.h
  let base := s!";TXFOYER={PAS.fmt h.rate};TXFOYER61={PAS.fmt h.rate61};PASNUM={h.num};PASDEN={h.den};PASIR={h.ir};PASX={h.pasNet};PASTOT={h.total};PASII={if h.zeroII then 1 else 0}"
  let ind := match o.ind, o.indSingle with
    | some i, some s => s!";TXDEC1={PAS.fmt i.rate1};TXDEC2={PAS.fmt i.rate2};TXDEC1S={PAS.fmt s.rate1};TXDEC2S={PAS.fmt s.rate2}"
    | _, _ => ""
  base ++ ind

def runLine (line : String) : Option String := do
  match line.splitOn ";" with
  | ["T", id, y, sit, q, r] =>
    let p ← paramsFor (← y.toNat?)
    some s!"{id};TAX={tableTax p (← sit.toNat?) (← q.toInt?) (← r.toInt?)}"
  | ["G", id, y, z, b] =>
    let r ← PAS.defaultRate (← y.toNat?) (← PAS.Zone.ofString z) (← b.trimAscii.toString.toInt?)
    some s!"{id};GRID={PAS.fmt r}"
  | [id, y, boxes] =>
    let year ← y.trimAscii.toString.toNat?
    let p ← paramsFor year
    let d := parseDecl year boxes
    let r := compute p d
    some (s!"{id};NBPT={fmtParts r.quarters};RNG={r.rng};RNI={r.rni};IDRSFULL={r.capped.full};IDRSCAP={r.capped.capped};IDRS={r.capped.tax};IDEC={r.decote};ITRED={r.reductions};CITOT={r.credits};PFU={r.flat};IDRS4={r.capped.tax - r.decote};IAVCR={r.beforeCredits};IMPNET={r.net};REVKIRE={r.rfr};PSNET={r.social};CHRAPRES={r.cehr};CDHR={r.cdhr}" ++ pasFields p d)
  | _ => none

partial def loop (h : IO.FS.Stream) (o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  match runLine line.trimAscii.toString with
  | some s => o.putStrLn s
  | none => o.putStrLn s!"ERR;{line.trimAscii.toString}"
  loop h o

def main : IO Unit := do
  loop (← IO.getStdin) (← IO.getStdout)
