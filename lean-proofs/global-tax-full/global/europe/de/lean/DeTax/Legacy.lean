import Lean.Data.Json
import DeTax.Assess
import DeTax.Pap

/-!
# `detax`: canonical households in, contract outputs out (JSONL)

    detax [FILE] [--kist=800|900] [--separate]
    --oecd: the OECD Taxing Wages convention (round 1, improve-continental): the § 31 Günstigerprüfung compares the
      Freibeträge of all children with all the Kindergeld at once (as --all-children-together; the OECD and GETTSIM
      read it so); the default (statute mode) tests child by child, oldest first (FINDINGS, M100_67).

Reads one household per line (CONTRACT.md format) from FILE or stdin and writes one result per line, same order.
Money is printed in euros with cents where the law counts cents (Soli, Kirchensteuer, Abgeltungsteuer, social
contributions); the tariff tax is whole euros. `incomeTax` = Einkommensteuer by the tariff after the Günstigerprüfung
of § 31 (without the Kindergeld that § 2 (6) adds back when the Freibeträge win; that Kindergeld is instead left out
of `benefits`) plus the Abgeltungsteuer of § 32d (1) on capital income (or nothing, when § 32d (6) puts capital
income into the tariff). `--separate` assesses married couples individually (§ 26a) instead of jointly.
-/

open Lean DeTax

def numInt (j : Json) : Int :=
  match j.getNum? with
  | .ok n => if n.exponent = 0 then n.mantissa else n.mantissa / (10 ^ n.exponent : Nat)
  | .error _ => 0

def field (j : Json) (k : String) : Int :=
  match j.getObjVal? k with
  | .ok v => numInt v
  | .error _ => 0

def parseAdult (j : Json) : Adult :=
  { age := field j "age", wages := field j "wages", selfEmployment := field j "selfEmployment",
    pension := field j "pension" }

def parseHousehold (j : Json) : Household :=
  let arr (k : String) : Array Json := match j.getObjVal? k with
    | .ok (.arr a) => a | _ => #[]
  { id := (match j.getObjVal? "id" with | .ok (.str s) => s | .ok v => v.compress | _ => ""),
    year := (match j.getObjVal? "year" with | .ok v => numInt v | _ => 2025),
    adults := (arr "adults").toList.map parseAdult,
    married := (match j.getObjVal? "married" with | .ok (.bool b) => b | _ => false),
    children := (arr "children").toList.map (fun c => field c "age"),
    interest := field j "interest", dividends := field j "dividends", capitalGains := field j "capitalGains",
    rentalIncome := field j "rentalIncome", charitable := field j "charitable",
    pensionContributions := field j "pensionContributions" }

/-- Cents as a JSON number in euros. -/
def eur (c : Int) : Json := Json.num ⟨c, 2⟩
def whole (e : Int) : Json := Json.num ⟨e, 0⟩

def svJson (a : Adult) (s : Sv) : Json :=
  let kind := match s.kind with
    | 0 => "employee" | 1 => "minijob" | 2 => "uebergangsbereich" | 3 => "pensioner"
    | 4 => "selfEmployedVoluntaryGKV" | _ => "none"
  Json.mkObj [("age", whole a.age), ("status", .str kind), ("RV", eur s.rv), ("AV", eur s.av), ("KV", eur s.kv),
    ("onPension", eur s.onPension), ("onSelfEmployment", eur s.onSelfEmployment),
    ("PV", eur s.pv), ("employerRV", eur s.rvEmployer)]

def unitJson (u : VUnit) (r : UnitResult) : Json :=
  Json.mkObj [
    ("joint", .bool u.joint), ("kidsCounted", whole u.kids), ("kidsWithFreibetrag", whole r.kidsFB),
    ("capitalInTariff_32d6", .bool r.capInTariff),
    ("summeDerEinkuenfte", eur r.summeEinkuenfte), ("altersentlastungsbetrag_24a", eur r.altersentlastung),
    ("entlastungsbetragAlleinerziehende_24b", eur r.entlastungAE), ("gesamtbetragDerEinkuenfte", eur r.gesamtbetrag),
    ("vorsorgeaufwendungen_10", eur r.vorsorge), ("sonderausgabenOther_10b_10c", eur r.sonderausgabenOther),
    ("einkommen", eur r.einkommen), ("zvE", whole r.zve), ("tariffTax_32a", whole r.tarif),
    ("kindergeldAddedBack_2_6", eur r.kindergeldAddBack), ("abgeltungsteuer_32d", eur r.abgeltung),
    ("festzusetzendeEinkommensteuer", eur (ct r.tarif + r.kindergeldAddBack + r.abgeltung)),
    ("soliBase_SolZG3_2", whole r.soliBase), ("soli", eur r.soli), ("kirchensteuer", eur r.kist),
    ("members", Json.arr (u.members.map fun (a, s) => svJson a s).toArray)]

def unsupportedFor (h : Household) (o : Opts) : List Json :=
  let l : List String :=
    (if h.children.any (· ≥ 25) then ["children aged 25+ not counted for Kindergeld/Freibeträge (§ 32 (4))"] else [])
    ++ (if h.adults.any (fun a => a.wages > 0 ∧ a.wages ≤ 12 * P.minijobMonat) then
          ["Minijob wages: employer's 2 % flat tax (§ 40a (2)) and flat contributions not shown"] else [])
    ++ (if h.adults.any (·.pension > 0) then
          ["pension taken as statutory Leibrente begun at 65; later increases not tracked"] else [])
    ++ (if h.adults.any (·.selfEmployment ≠ 0) then
          ["self-employment as freelance § 18 (no Gewerbesteuer); RV for self-employed not modelled"] else [])
    ++ (if o.kistBp = 0 then ["Kirchensteuer not applied (pass --kist=800|900)"] else [])
    ++ (if !yearSupported h.year then ["only VZ 2022-2025 are modelled: computed with the 2025 law"] else [])
    ++ (if h.year = 2022 then ["Energiepreispauschale 2022 of the self-employed and of pensioners not modelled (employees: included)"] else [])
    ++ (if h.adults.length > 2 then ["more than two adults: each assessed as a single person"] else [])
    ++ ["Kirchensteuer as Sonderausgabe (§ 10 (1) Nr. 4) not modelled"]
  l.map Json.str

/-- 2022 Energiepreispauschale paid to the household's employees (euros). -/
def eppTotal (h : Household) (r : Result) : Int :=
  (ypFor h.year).epp * Int.ofNat ((r.units.map fun (u, _) => (u.members.filter fun (a, s) => decide (a.wages > 0) && !s.minijob).length).foldl (· + ·) 0)

def runHousehold (o : Opts) (j : Json) : Json :=
  let h := parseHousehold j
  if h.adults.isEmpty then Json.mkObj [("id", .str h.id), ("error", .str "no adults")] else
  let r := assess o h
  let separate : List (String × Json) :=
    if h.married ∧ h.adults.length = 2 ∧ o.joint then
      let s := assess { o with joint := false } h
      let burden (x : Result) := x.incomeTax + x.soli + x.kist - x.kindergeldKept
      [("splittingAdvantage_vs_26a", eur (burden s - burden r))]
    else []
  Json.mkObj [
    ("id", .str h.id), ("country", .str "DE"), ("currency", .str "EUR"),
    -- Round 4 (improve-continental): EStG § 2 (6) Satz 3: "Wird das Einkommen in den Fällen des § 31 um die
    -- Freibeträge nach § 32 Absatz 6 gemindert, ist der Anspruch auf Kindergeld ... der tariflichen Einkommensteuer
    -- hinzuzurechnen": the festzusetzende Einkommensteuer includes the add-back, and the Kindergeld itself (§ 66) is
    -- paid in full. Before round 4 both were netted (add-back left out of incomeTax, the same Kindergeld left out of
    -- benefits): the net is unchanged.
    ("incomeTax", eur (r.incomeTax + r.kindergeldPaid - r.kindergeldKept)),
    ("surtaxes", Json.mkObj [("Soli", eur r.soli), ("Kirchensteuer", eur r.kist)]),
    ("localIncomeTax", whole 0),
    ("employeeSocial", eur r.employeeSocial),
    ("benefits", eur (r.kindergeldPaid + ct (eppTotal h r))),
    ("detail", Json.mkObj ([
      ("incomeTaxIs", .str "festzusetzende ESt (§ 2 (6): tariff after the § 31 Günstigerprüfung + the Kindergeld add-back of § 2 (6) Satz 3) + Abgeltungsteuer § 32d (1)"),
      ("kindergeldKept", eur r.kindergeldKept), ("energiepreispauschale", eur (ct (eppTotal h r))), ("kindergeldAddBack_2_6", eur (r.kindergeldPaid - r.kindergeldKept)),
      ("kindergeldPaid", eur r.kindergeldPaid),
      ("employeeSocialOnPensions", eur ((r.units.map fun (u, _) => (u.members.map fun (_, s) => s.onPension).foldl (· + ·) 0).foldl (· + ·) 0)),
      ("employeeSocialOnSelfEmployment", eur ((r.units.map fun (u, _) => (u.members.map fun (_, s) => s.onSelfEmployment).foldl (· + ·) 0).foldl (· + ·) 0)),
      ("units", Json.arr (r.units.map fun (u, x) => unitJson u x).toArray)] ++ separate)),
    ("unsupported", Json.arr (unsupportedFor h o).toArray)]

partial def loop (o : Opts) (h : IO.FS.Stream) (out : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if t.isEmpty then loop o h out else
  match Json.parse t with
  | .ok j => out.putStrLn (runHousehold o j).compress
  | .error e => out.putStrLn (Json.mkObj [("error", .str s!"bad JSON: {e}")]).compress
  out.flush
  loop o h out

/-- A decimal JSON number scaled by `10^k` and rounded (for ZKF with one decimal, KVZ with two). -/
def scaled (j : Json) (key : String) (k : Nat) : Int :=
  match j.getObjVal? key with
  | .ok v => match v.getNum? with
    | .ok n =>
      if n.exponent ≤ k then n.mantissa * (10 ^ (k - n.exponent) : Nat)
      else rndHalf n.mantissa ((10 ^ (n.exponent - k) : Nat) : Int)
    | .error _ => 0
  | .error _ => 0

/-- `--pap`: one PAP 2025 input per line (names as in the XML; ZKF, KVZ as decimals) → the PAP's outputs. -/
def runPap (j : Json) : Json :=
  let g (k : String) : Int := field j k
  let n (k : String) : Nat := (g k).toNat
  let i : Pap.In :=
    { LZZ := n "LZZ", RE4 := g "RE4", STKL := n "STKL", ZKF10 := scaled j "ZKF" 1,
      KRV := n "KRV", KVZbp := scaled j "KVZ" 2, PKV := n "PKV", PKPV := g "PKPV", PVS := n "PVS", PVZ := n "PVZ",
      PVA := g "PVA", R := n "R", ALTER1 := n "ALTER1", AJAHR := g "AJAHR", LZZFREIB := g "LZZFREIB",
      LZZHINZU := g "LZZHINZU" }
  let o := Pap.run i
  Json.mkObj [("id", match j.getObjVal? "id" with | .ok v => v | _ => .null),
    ("LSTLZZ", whole o.LSTLZZ), ("SOLZLZZ", whole o.SOLZLZZ), ("BK", whole o.BK), ("VFRB", whole o.VFRB),
    ("WVFRB", whole o.WVFRB), ("VKVLZZ", whole o.VKVLZZ), ("ZVEc", whole o.ZVEc), ("LSTJAHR", whole o.LSTJAHR),
    ("JBMG", whole o.JBMG), ("VSP", whole o.VSP)]

partial def loopPap (h : IO.FS.Stream) (out : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then
    match Json.parse t with
    | .ok j => out.putStrLn (runPap j).compress
    | .error e => out.putStrLn (Json.mkObj [("error", .str s!"bad JSON: {e}")]).compress
  loopPap h out

def legacyMain (args : List String) : IO Unit := do
  let kist : Int := (args.filterMap fun a =>
    if a.startsWith "--kist=" then (a.drop 7).toString.toInt? else none).headD 0
  let compat := args.contains "--gettsim-compat"
  let o : Opts :=
    { kistBp := kist, joint := !args.contains "--separate",
      perChild := !(compat || args.contains "--all-children-together" || args.contains "--oecd"),
      opt32d6 := !(compat || args.contains "--no-32d6"), g := compat,
      gTariff := args.contains "--g-tariff", gVors := args.contains "--g-vors", gAlte := args.contains "--g-alte",
      gSv := args.contains "--g-sv" }
  let files := args.filter fun a => !a.startsWith "--"
  let out ← IO.getStdout
  let input ← match files with
    | f :: _ => do let h ← IO.FS.Handle.mk f .read; pure (IO.FS.Stream.ofHandle h)
    | [] => IO.getStdin
  if args.contains "--pap" then loopPap input out else loop o input out
