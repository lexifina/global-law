import Lean.Data.Json
import PlTax.Withholding

/-!
# `pltax`: canonical households (JSONL) in, contract outputs (JSONL) out

    pltax [households.jsonl]      (stdin when no file is given)

Input: the shared contract's household (`~/cmp/shared/CONTRACT.md`). Poland-only optional fields, per adult:
`plRegime` ("skala" default, "liniowy", "ryczalt"), `plZus` ("standard" default, "preferential", "none"),
`plRyczaltBp` (ryczałt rate in basis points, default 1200), `plSeRevenue` (business revenue, default = selfEmployment),
`plSex` ("M" default, "F"; pkt 154 age), `plCommuter` (art. 22 ust. 2 pkt 3), `plReturning` (pkt 152). Per household:
`plRentalOnePerson` (ryczałt art. 12 ust. 6 statement), `plFiling` ("best" default, "separate", "joint").
Output: one object per line, in the same order; amounts in whole złoty.
-/

open Lean PlTax

def numToInt (n : JsonNumber) : Int := n.mantissa / (10 ^ n.exponent : Nat)

def jInt (j : Json) (k : String) (d : Int := 0) : Int :=
  match j.getObjVal? k with
  | .ok (.num n) => numToInt n
  | _ => d

def jBool (j : Json) (k : String) (d : Bool := false) : Bool :=
  match j.getObjVal? k with
  | .ok (.bool b) => b
  | _ => d

def jStr (j : Json) (k : String) (d : String := "") : String :=
  match j.getObjVal? k with
  | .ok (.str s) => s
  | .ok (.num n) => toString (numToInt n)
  | _ => d

def jArr (j : Json) (k : String) : Array Json :=
  match j.getObjVal? k with
  | .ok (.arr a) => a
  | _ => #[]

def parseRegime (s : String) : Regime :=
  if s == "liniowy" then .liniowy else if s == "ryczalt" || s == "ryczałt" then .ryczalt else .skala

def parseZus (s : String) : ZusKind :=
  if s == "preferential" then .preferential else if s == "none" then .none else .standard

def parseHousehold (j : Json) : Household :=
  { id := jStr j "id", year := jInt j "year" 2025,
    adults := (jArr j "adults").toList.map fun a =>
      { age := jInt a "age" 40, wages := jInt a "wages", se := jInt a "selfEmployment",
        seRevenue := jInt a "plSeRevenue", pension := jInt a "pension",
        regime := parseRegime (jStr a "plRegime" "skala"), zus := parseZus (jStr a "plZus" "standard"),
        ryczaltBp := jInt a "plRyczaltBp" ryczaltDefaultBp, female := jStr a "plSex" "M" == "F",
        commuter := jBool a "plCommuter", returning := jBool a "plReturning" },
    married := jBool j "married",
    children := (jArr j "children").toList.map fun c => jInt c "age",
    interest := jInt j "interest", dividends := jInt j "dividends", capitalGains := jInt j "capitalGains",
    rentalIncome := jInt j "rentalIncome", charitable := jInt j "charitable",
    pensionContributions := jInt j "pensionContributions",
    rentalOnePerson := jBool j "plRentalOnePerson", filing := jStr j "plFiling" "best" }

def ji (i : Int) : Json := toJson i
/-- grosze to złoty with two decimals, as a JSON number. -/
def jg (g : Int) : Json :=
  let s := if g < 0 then "-" else ""
  let a := g.natAbs
  let c := a % 100
  match Json.parse (s ++ toString (a / 100) ++ "." ++ (if c < 10 then "0" else "") ++ toString c) with
  | .ok v => v
  | .error _ => ji (zl g)

def personJson (x : Stage2) : Json :=
  let s := x.s
  Json.mkObj [
    ("age", ji s.p.age), ("wages", ji s.p.wages), ("selfEmployment", ji s.p.se), ("pension", ji s.p.pension),
    ("regime", Json.str s.p.regime.name),
    ("zus", Json.mkObj [("emerytalne", jg s.emp.emerytalne), ("rentowe", jg s.emp.rentowe),
      ("chorobowe", jg s.emp.chorobowe), ("employeeTotal", jg s.emp.total),
      ("subkontoEmployeeHalf_OECDexcluded", jg s.emp.subkonto),
      ("selfEmployedSocial", jg s.seSocial), ("funduszPracy", jg s.seFP)]),
    ("health_skladkaZdrowotna", Json.mkObj [("employee", jg s.emp.health), ("selfEmployed", jg s.seHealth),
      ("pension", jg s.pensionHealth)]),
    ("exempt_art21_148_152_154", Json.mkObj [("wages", jg s.exemptW), ("business", jg s.exemptS)]),
    ("kosztyUzyskania_art22", jg s.kup),
    ("dochodSkala", jg s.skalaIncome), ("socialDeducted_art26_1_2_2a", jg s.socialDed),
    ("ikze_art26_1_2b", jg (x.ikzeSkala + x.ikzeFlat)), ("gifts_art26_1_9", jg x.gift),
    ("podstawaSkala", ji x.baseZl), ("podstawaFlat", ji x.flatBaseZl), ("flatTax", jg x.flatTax),
    ("liniowyHealthDeducted", jg s.liniowyHealthDed),
    ("art27f_9_contributions", jg s.refundContrib), ("art27f_2a_income", jg s.childIncome),
    ("withheld_art32_PIT2", ji (if s.p.wages > 0 then withheld s.p else 0))]

def resultJson (h : Household) (r : Result) : Json :=
  Json.mkObj [
    ("id", Json.str h.id), ("country", Json.str "PL"), ("currency", Json.str "PLN"),
    ("incomeTax", ji r.incomeTax),
    ("surtaxes", Json.mkObj []),
    ("localIncomeTax", ji 0),
    ("employeeSocial", ji r.employeeSocial),
    ("benefits", ji r.benefits),
    ("detail", Json.mkObj [
      ("taxYear", Json.str "2025 (calendar year); PIT t.j. Dz.U. 2025 poz. 163"),
      ("filing", Json.str r.filing),
      ("taxScale_art27", jg r.skalaTax), ("childRelief_art27f", jg r.relief),
      ("childReliefDeducted", jg r.reliefUsed), ("childReliefPaidOut_art27f_8", jg r.reliefRefund),
      ("skalaNet", jg r.skalaNet), ("liniowyRyczaltTax", jg r.flatTaxes),
      ("interestDividends_art30a", jg r.investTax), ("gains_art30b", jg r.gainsTax),
      ("rentalRyczalt", jg r.rentalTax),
      ("benefit800plus", ji r.benefit800), ("dobryStart", ji r.dobryStartTotal),
      ("persons", Json.arr (r.persons.map personJson).toArray)]),
    ("unsupported", Json.arr (r.unsupported.map Json.str).toArray)]

def runLine (line : String) (fy : Bool := false) : String :=
  match Json.parse line with
  | .error e => (Json.mkObj [("error", Json.str e)]).compress
  | .ok j =>
    let h := { parseHousehold j with fyStart := fy }
    (resultJson h (compute h)).compress

partial def loop (inp : IO.FS.Stream) (out : IO.FS.Stream) (fy : Bool := false) : IO Unit := do
  let line ← inp.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then out.putStrLn (runLine t fy)
  loop inp out fy

def main (args : List String) : IO UInt32 := do
  let out ← IO.getStdout
  -- `--fy-start`: Eurostat earn_net ESMS 3.4 convention (parameters at the start of the fiscal year); never the default
  let fy := args.contains "--fy-start"
  match args.filter (· != "--fy-start") with
  | [] => loop (← IO.getStdin) out fy; return 0
  | [f] =>
    let h ← IO.FS.Handle.mk f .read
    loop (IO.FS.Stream.ofHandle h) out fy
    return 0
  | _ => IO.eprintln "usage: pltax [--fy-start] [households.jsonl]"; return 2
