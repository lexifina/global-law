import Lean.Data.Json
import AuTax.Household

/-!
# `autax`: canonical households in, contract outputs out (JSON Lines)

    autax [--es] [--income-support] [--oecd = both] [households.jsonl]     (stdin when no file is given)

Input: `cmp/shared/CONTRACT.md`. `year` 2025 (default) = income year 2024-25; 2026 = 2025-26.
Household investment, rental, gift and pension-contribution totals are split equally between the adults (each
spouse is taxed on their own share; Australia has no joint return). Optional extras, per adult: `interest`,
`dividends`, `capitalGains`, `rentalIncome`, `charitable`, `superContrib` (added to that adult's share),
`salarySacrifice` (bool: `superContrib` comes out of the wage package), `privateHospitalCover` (bool, default true:
no Medicare levy surcharge), `helpDebt` (bool). Household: `energySupplement` (bool; `--es` sets it for all).
-/

open Lean AuTax

def numToInt (n : JsonNumber) : Int :=
  let d : Int := (10 : Int) ^ n.exponent
  (2 * n.mantissa + d) / (2 * d)

def getI (j : Json) (k : String) (d : Int := 0) : Int :=
  match j.getObjVal? k with
  | .ok (.num n) => numToInt n
  | _ => d

def getB (j : Json) (k : String) (d : Bool := false) : Bool :=
  match j.getObjVal? k with
  | .ok (.bool b) => b
  | _ => d

def getS (j : Json) (k : String) : String :=
  match j.getObjVal? k with
  | .ok (.str s) => s
  | .ok v => v.compress
  | _ => ""

def getArr (j : Json) (k : String) : Array Json :=
  match j.getObjVal? k with
  | .ok (.arr a) => a
  | _ => #[]

/-- Equal split of a household total over `n` adults: the first gets the remainder. -/
def share (total : Int) (n : Nat) (k : Nat) : Int :=
  if n ≤ 1 then total else
  let each := total / n
  if k = 0 then total - each * (n - 1) else each

def parseHousehold (j : Json) (es : Bool) (incomeSupportFlag : Bool := false) : Household :=
  let ads := (getArr j "adults").toList
  let n := ads.length
  let persons := ((List.range n).zip ads).map fun (k, a) =>
    { age := (getI a "age" 40).toNat, wages := getI a "wages", selfEmployment := getI a "selfEmployment",
      pension := getI a "pension",
      interest := share (getI j "interest") n k + getI a "interest",
      dividends := share (getI j "dividends") n k + getI a "dividends",
      capitalGains := share (getI j "capitalGains") n k + getI a "capitalGains",
      rental := share (getI j "rentalIncome") n k + getI a "rentalIncome",
      gifts := share (getI j "charitable") n k + getI a "charitable",
      superContrib := share (getI j "pensionContributions") n k + getI a "superContrib",
      sacrifice := getB a "salarySacrifice", privateCover := getB a "privateHospitalCover" true,
      helpDebt := getB a "helpDebt", frankingRate := getI a "frankingRate" (getI j "frankingRate" 3000) : Person }
  { id := getS j "id", year := (getI j "year" 2025).toNat, persons := persons, married := getB j "married",
    children := (getArr j "children").toList.map fun c => (getI c "age" 0).toNat,
    energySupplement := es || getB j "energySupplement",
    incomeSupport := incomeSupportFlag || getB j "incomeSupport",
    cohabiting := getB j "cohabiting" || getB j "deFacto" }

def money (c : Int) : Json := Json.num { mantissa := c, exponent := 2 }

def personJson (x : Person) (r : PersonResult) : Json := Json.mkObj [
  ("age", Json.num (JsonNumber.fromNat x.age)),
  ("taxableIncome", money r.taxable), ("frankingCredit", money r.frankingCredit),
  ("taxOnTaxableIncome", money r.basicTax), ("lowIncomeTaxOffset", money r.lito),
  ("incomeTaxAfterOffsets", money r.incomeTax), ("medicareLevy", money r.levy),
  ("medicareLevySurcharge", money r.surcharge), ("division293", money r.div293),
  ("superContributionsTax", money r.contribTax), ("helpRepayment", money r.help),
  ("adjustedTaxableIncome", money r.broadIncome)]

def unsupportedFor (h : Household) : List String :=
  (if h.persons.any (·.age ≥ 67) then ["seniors and pensioners tax offset (SAPTO) not modelled"] else []) ++
  (if h.children.any (fun a => a ≥ 16 && a ≤ 19) then ["children 16-19 assumed full-time secondary students"] else []) ++
  (if h.persons.any (·.superContrib > (paramsFor h.year).concessionalCap) then
    ["excess concessional contributions (Div 291) not modelled: contributions capped"] else []) ++
  (if h.persons.any (·.pension > 0) then ["pension treated as assessable income (a taxed super pension at 60+ is not)"] else []) ++
  (if h.year < 2025 && h.persons.any (·.helpDebt) then ["HELP repayment bands of 2024-25 used for an earlier income year"] else []) ++
  (if h.year < 2022 then [s!"income year ending {h.year} not modelled: 2021-22 parameters used"] else [])

def outputJson (h : Household) (r : Result) : Json :=
  let p := paramsFor h.year
  Json.mkObj [
    ("id", Json.str h.id), ("country", Json.str "AU"), ("currency", Json.str "AUD"),
    ("incomeTax", money r.incomeTax),
    ("surtaxes", Json.mkObj ([("medicareLevy", money r.medicareLevy)] ++
      (if r.mls ≠ 0 then [("medicareLevySurcharge", money r.mls)] else []) ++
      (if r.div293 ≠ 0 then [("division293", money r.div293)] else []) ++
      (if r.contribTax ≠ 0 then [("superContributionsTax", money r.contribTax)] else []))),
    ("localIncomeTax", money 0),
    ("employeeSocial", money 0),
    ("benefits", money r.benefits),
    ("detail", Json.mkObj [
      ("incomeYear", Json.str p.label),
      ("incomeTaxIs", Json.str "ITAA 1997 s. 4-10: ITRA Sch 7 tax on taxable income less LITO (non-refundable) less franking credits (refundable, s. 67-25)"),
      ("employeeSocialIs", Json.str "none: Australia has no employee social security contributions (superannuation guarantee is an employer contribution)"),
      ("ftbPartA", money r.ftb.partA), ("ftbPartB", money r.ftb.partB), ("ftbMethod", Json.str r.ftb.method),
      ("familyAdjustedTaxableIncome", money r.ftb.ati),
      ("energySupplement", Json.bool h.energySupplement),
      ("helpRepayment", money r.help),
      ("parentingPaymentSingle", money r.pps.payment), ("telephoneAllowance", money r.pps.telephone),
      ("persons", Json.arr ((h.persons.zip r.persons).map fun (x, pr) => personJson x pr).toArray)]),
    ("unsupported", Json.arr ((unsupportedFor h).map Json.str).toArray)]

partial def loop (es isup : Bool) (inp : IO.FS.Stream) (out : IO.FS.Stream) : IO Unit := do
  let line ← inp.getLine
  if line.isEmpty then return
  let s := line.trimAscii.toString
  if s.isEmpty then loop es isup inp out else
  match Json.parse s with
  | .ok j =>
    let h := parseHousehold j es isup
    out.putStrLn (outputJson h (compute h)).compress
  | .error e => out.putStrLn (Json.mkObj [("error", Json.str e), ("input", Json.str s)]).compress
  loop es isup inp out

def legacyMain (args : List String) : IO Unit := do
  let es := args.contains "--es" || args.contains "--oecd"
  let isup := args.contains "--income-support" || args.contains "--oecd"
  match args.filter (fun a => !a.startsWith "--") with
  | [f] =>
    let h ← IO.FS.Handle.mk f .read
    loop es isup (IO.FS.Stream.ofHandle h) (← IO.getStdout)
  | _ => loop es isup (← IO.getStdin) (← IO.getStdout)
