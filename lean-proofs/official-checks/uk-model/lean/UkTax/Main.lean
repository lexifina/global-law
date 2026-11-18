import Lean.Data.Json
import UkTax.Household

/-!
# `uktax`: canonical households in, contract outputs out (JSON Lines)

    uktax [--literal] [households.jsonl]   (stdin when no file is given)

One output line per input line, in order. Money is printed in pounds with pence (two decimals). `--literal` reads
ITA 2007 s. 12B(8) and FA 2004 s. 192(4) literally (see `Rates.lean`); the default is HMRC's reading.
-/

open Lean UkTax

/-- A JSON number as a whole number (rounded down if it has a fraction). -/
def numToInt (n : JsonNumber) : Int := n.mantissa / (10 ^ n.exponent : Nat)

def getI (j : Json) (k : String) (d : Int := 0) : Int :=
  match j.getObjVal? k with
  | .ok v => match v.getNum? with
    | .ok n => numToInt n
    | .error _ => d
  | .error _ => d

def getB (j : Json) (k : String) : Bool :=
  match j.getObjVal? k with
  | .ok v => match v.getBool? with | .ok b => b | .error _ => false
  | .error _ => false

def getS (j : Json) (k : String) : String :=
  match j.getObjVal? k with
  | .ok v => match v.getStr? with
    | .ok s => s
    | .error _ => v.compress
  | .error _ => ""

def getArr (j : Json) (k : String) : Array Json :=
  match j.getObjVal? k with
  | .ok v => match v.getArr? with | .ok a => a | .error _ => #[]
  | .error _ => #[]

def parseHousehold (j : Json) : Household :=
  { id := getS j "id"
    year := (getI j "year" 2025).toNat
    adults := (getArr j "adults").toList.map fun a =>
      { age := (getI a "age" 40).toNat, wages := getI a "wages", selfEmployment := getI a "selfEmployment",
        pension := getI a "pension", blind := getB a "blind" }
    married := getB j "married"
    children := (getArr j "children").toList.map fun c => (getI c "age" 0).toNat
    interest := getI j "interest", dividends := getI j "dividends", capitalGains := getI j "capitalGains",
    rentalIncome := getI j "rentalIncome", charitable := getI j "charitable",
    pensionContributions := getI j "pensionContributions",
    scottish := (getS j "region").toLower == "scotland" }

/-- Pence as a JSON number of pounds with two decimals. -/
def money (p : Int) : Json := Json.num { mantissa := p, exponent := 2 }

def chargedJson (c : Charged) : Json := Json.mkObj [
  ("nonSavingsBasic", money c.nsBasic), ("nonSavingsHigher", money c.nsHigher),
  ("nonSavingsAdditional", money c.nsAdditional), ("savingsStartingRate", money c.savStarting),
  ("savingsNilRate", money c.savNil), ("savingsBasic", money c.savBasic), ("savingsHigher", money c.savHigher),
  ("savingsAdditional", money c.savAdditional), ("dividendNilRate", money c.divNil),
  ("dividendOrdinary", money c.divOrdinary), ("dividendUpper", money c.divUpper),
  ("dividendAdditional", money c.divAdditional), ("savingsAllowance", money c.psa)]

def personJson (x : Person) (r : PersonResult) : Json := Json.mkObj [
  ("age", Json.num (JsonNumber.fromInt (x.age : Int))),
  ("totalIncome", money r.totalIncome), ("netIncome", money r.netIncome),
  ("adjustedNetIncome", money r.ani), ("giftAidGross", money r.grossGift),
  ("pensionContributionsRelieved", money r.rasRelieved),
  ("personalAllowance", money (gbp r.pa)), ("blindPersonsAllowance", money (gbp r.bpa)),
  ("deductedSteps2and3", money r.deducted), ("step3Income", money r.t),
  ("basicRateLimit", money r.limits.brl), ("higherRateLimit", money r.limits.hrl),
  ("bandsExtendedForPension", Json.bool r.rasExtends),
  ("charged", chargedJson r.ch),
  ("taxAtStep5", money (ticksToPence r.tax5)),
  ("marriageAllowanceReduction", money (ticksToPence r.maReduction)),
  ("marriedCouplesAllowanceReduction", money (ticksToPence r.mcaUsed)),
  ("giftAidCharge", money (ticksToPence r.giftAidCharge)),
  ("liability", money (ticksToPence r.liability)),
  ("reliefAtSource", money (ticksToPence r.rasRelief)),
  ("cgtTaxableGains", money r.cgtTaxable), ("capitalGainsTax", money (ticksToPence r.cgt)),
  ("class1", money (ticksToPence r.class1)), ("class4", money (ticksToPence r.class4))]

def outputJson (h : Household) (o : HouseholdResult) : Json :=
  let liab := sumBy o.results fun r => ticksToPence r.liability
  let ras := sumBy o.results fun r => ticksToPence r.rasRelief
  Json.mkObj [
    ("id", Json.str h.id), ("country", Json.str "UK"), ("currency", Json.str "GBP"),
    ("incomeTax", money o.incomeTax),
    ("surtaxes", if o.cgt = 0 then Json.mkObj [] else Json.mkObj [("capitalGainsTax", money o.cgt)]),
    ("localIncomeTax", money 0),
    ("employeeSocial", money o.employeeSocial),
    ("benefits", money o.benefits),
    ("detail", Json.mkObj [
      ("taxYear", Json.str "2025-26"),
      ("rules", Json.str (if h.scottish then "Scottish taxpayer (Scottish rates on non-savings income)"
                          else "England, Wales and Northern Ireland")),
      ("incomeTaxIs", Json.str "ITA 2007 s. 23 liability (without the HICBC) less basic-rate relief at source on pension contributions"),
      ("liabilityITA2007s23", money liab), ("reliefAtSource", money ras),
      ("childBenefit", money o.childBenefit), ("hicbc", money o.hicbc),
      ("hicbcIn", Json.str "benefits"),
      ("hicbcPayer", match o.hicbcPayer with | some i => Json.num (JsonNumber.fromInt ((i : Int) + 1)) | none => Json.null),
      ("capitalGainsTaxIn", Json.str "surtaxes.capitalGainsTax (TCGA 1992, a separate tax)"),
      ("employeeSocialIs", Json.str "Class 1 primary (annual earnings period) + Class 4; Class 2 nil (treated as paid above the small profits threshold)"),
      ("election", Json.str o.election),
      ("persons", Json.arr ((o.persons.zip o.results).map fun (x, r) => personJson x r).toArray)]),
    ("unsupported", Json.arr (o.unsupported.map Json.str).toArray)]

partial def loop (rd : Reading) (h : IO.FS.Stream) (o : IO.FS.Stream) : IO Unit := do
  let line ← h.getLine
  if line.isEmpty then return
  let s := line.trimAscii.toString
  if s.isEmpty then loop rd h o else
  match Json.parse s with
  | .ok j =>
    let hh := parseHousehold j
    o.putStrLn (outputJson hh (householdCalc p2025 rd hh)).compress
  | .error e => o.putStrLn (Json.mkObj [("error", Json.str e), ("input", Json.str s)]).compress
  loop rd h o

def main (args : List String) : IO Unit := do
  let base := if args.contains "--literal" then Reading.literal
              else if args.contains "--pe" then Reading.pe else Reading.hmrc
  -- single conventions, for attributing differences: --pe-ras --pe-ma --pe-ga --pe-cgt --pe-mca
  let rd := { base with
    peRasDeduction := base.peRasDeduction || args.contains "--pe-ras"
    peMaUnused := base.peMaUnused || args.contains "--pe-ma"
    peNoGiftAidCharge := base.peNoGiftAidCharge || args.contains "--pe-ga"
    peNoMca := base.peNoMca || args.contains "--pe-mca"
    psaLiteral := base.psaLiteral || args.contains "--psa-literal"
    ras := if args.contains "--ras-literal" then .mainRatesOnly
           else if args.contains "--ras-unconditional" || args.contains "--pe-cgt" then .unconditional
           else base.ras }
  let files := args.filter fun a => !a.startsWith "--"
  match files with
  | [f] =>
    let h ← IO.FS.Handle.mk f .read
    loop rd (IO.FS.Stream.ofHandle h) (← IO.getStdout)
  | _ => loop rd (← IO.getStdin) (← IO.getStdout)
