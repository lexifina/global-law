import Lean.Data.Json
import CzTax.Withholding

/-!
# `cztax`: canonical households (JSONL) in, contract outputs (JSONL) out

    cztax [--oecd] [households.jsonl]      (stdin when no file is given; --oecd = the convention mode of the tests:
    the OECD's unrounded annual arithmetic, `Household.oecd`; without it the statute)

Input: the shared contract's household (`cmp/shared/CONTRACT.md`). Czech-only optional fields:
* per adult: `czSelfReceipts` (§ 7 receipts; expenses then at `czExpenseRate` % of them, § 7 odst. 7: 80/60/40/30,
  default 60), `czRegime` ("standard" | "pausal" | "sro"), `czPausalBand` (1–3; default the lowest eligible),
  `czSroSalary` (the owner's wage from the s.r.o.), `czStateInsured` (bool; default: pensioners, 65+, and the lower
  earner of a household with a child under 7), `czDppMonthly` (a DPP paid every month), `czDppInReturn`;
* per household: `czChildClaimants` (adult index per child, § 35c odst. 9; default all 0), `czMortgageInterest`
  (§ 15 odst. 3), `czShortGains` (§ 10 gains on securities held ≤ 3 years), `czCoopPct` (§ 13: percent of adult 0's § 7 income given to a cooperating spouse), `czDeductionsBy` (adult claiming the § 15 items, default 0), `czPridavekMonths` (months of
  přídavek na dítě under ZSSP §§ 17–18, default 12).
Output: one object per line, in the same order.
-/

open Lean CzTax

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
  if s == "pausal" then .pausal else if s == "sro" then .sro else .standard

def parseHousehold (j : Json) : Household :=
  { id := jStr j "id", year := jInt j "year" 2025,
    adults := (jArr j "adults").toList.map fun a =>
      { age := jInt a "age" 40, wages := jInt a "wages", selfEmployment := jInt a "selfEmployment",
        pension := jInt a "pension", selfReceipts := jInt a "czSelfReceipts", expenseRate := jInt a "czExpenseRate" 60,
        regime := parseRegime (jStr a "czRegime" "standard"), pausalBand := (jInt a "czPausalBand").toNat,
        sroSalary := jInt a "czSroSalary",
        stateInsured := (match a.getObjVal? "czStateInsured" with
          | .ok (.bool b) => some b
          | _ => none),
        dppMonthly := jInt a "czDppMonthly", dppInReturn := jBool a "czDppInReturn" },
    married := jBool j "married",
    children := (jArr j "children").toList.map fun c => { age := jInt c "age" },
    interest := jInt j "interest", dividends := jInt j "dividends", capitalGains := jInt j "capitalGains",
    rentalIncome := jInt j "rentalIncome", charitable := jInt j "charitable",
    pensionContributions := jInt j "pensionContributions",
    mortgageInterest := jInt j "czMortgageInterest", deductionsBy := (jInt j "czDeductionsBy").toNat,
    childClaimants := (jArr j "czChildClaimants").toList.map (fun x =>
      match x with
      | .num n => (numToInt n).toNat
      | _ => 0),
    pridavekMonths := jInt j "czPridavekMonths" 12, coopPct := jInt j "czCoopPct",
    shortGains := jInt j "czShortGains" }

def ji (i : Int) : Json := toJson i

def regimeStr : Regime → String
  | .standard => "standard"
  | .pausal => "pausal"
  | .sro => "sro"

def personJson (p : PersonOut) : Json :=
  Json.mkObj [
    ("regime", Json.str (regimeStr p.regime)), ("pausalBand", ji p.pausalBand),
    ("seProfit_dilciZaklad7", ji p.seProfit),
    ("taxBase_zakladDane", ji p.tax.base), ("deductions_nezdanitelneCasti15", ji p.tax.deductions),
    ("roundedBase16", ji p.tax.roundedBase), ("tax16", ji p.tax.tax16),
    ("slevy35ba", ji p.tax.slevy), ("childSleva35c", ji p.tax.childSleva), ("bonus35c", ji p.tax.bonus),
    ("childCreditLost", ji p.tax.bonusLost), ("pit", ji p.pit),
    ("social_socialniPojisteni", ji p.social), ("health_zdravotniPojisteni", ji p.health),
    ("sro", Json.mkObj [("cit21", ji p.sroCit), ("dividend", ji p.sroDividend), ("dividendTax15", ji p.sroDivTax),
      ("employerContributions", ji p.sroEmployer), ("ownHealth3b", ji p.sroOwnHealth)]),
    ("netForBenefit", ji p.netForBenefit)]

def resultJson (h : Household) (r : Result) : Json :=
  Json.mkObj [
    ("id", Json.str h.id), ("country", Json.str "CZ"), ("currency", Json.str "CZK"),
    ("incomeTax", ji r.incomeTax),
    ("surtaxes", Json.mkObj []),
    ("localIncomeTax", ji 0),
    ("employeeSocial", ji r.employeeSocial),
    ("benefits", ji r.benefits),
    ("detail", Json.mkObj [
      ("taxYear", Json.str "zdaňovací období 2025 (calendar year), ZDP 586/1992 Sb. as in force 2025"),
      ("persons", Json.arr (r.persons.map personJson).toArray),
      ("withheld36", ji r.withheld),
      ("pridavekNaDite", Json.mkObj [("eligible", toJson r.pridavekEligible),
        ("familyNetMonthly", ji r.familyNetMonthly), ("zivotniMinimumRodiny", ji r.zmFamily),
        ("limit3_4", ji (r.zmFamily * 340 / 100))]),
      ("notes", Json.arr (r.notes.map Json.str).toArray)]),
    ("unsupported", Json.arr #[Json.str "ZTP/P and invalidity slevy", Json.str "state-insured status beyond the default rule (job seekers, students): use czStateInsured",
      Json.str "foreign income", Json.str "loss carry-forward (§ 34)"])]

def runLine (oecd : Bool) (line : String) (june30 noSk : Bool := false) : String :=
  match Json.parse line with
  | .error e => (Json.mkObj [("error", Json.str e)]).compress
  | .ok j =>
    let h := { parseHousehold j with oecd := oecd, june30 := june30, noSkolkovne := noSk }
    (resultJson h (compute h)).compress

partial def loop (oecd : Bool) (inp : IO.FS.Stream) (out : IO.FS.Stream) (june30 noSk : Bool := false) : IO Unit := do
  let line ← inp.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then out.putStrLn (runLine oecd t june30 noSk)
  loop oecd inp out june30 noSk

def legacyMain (args : List String) : IO UInt32 := do
  let out ← IO.getStdout
  let oecd := args.contains "--oecd"
  -- EUROMOD-grid convention flags (round 15): --june30, --no-skolkovne (see Household.june30 / noSkolkovne)
  let june30 := args.contains "--june30"
  let noSk := args.contains "--no-skolkovne"
  match args.filter (fun a => a != "--oecd" && a != "--june30" && a != "--no-skolkovne") with
  | [] => loop oecd (← IO.getStdin) out june30 noSk; return 0
  | ["--wh", lo, hi, step, kids] =>
    -- withholding scan: monthly wage from lo to hi by step; prints m, yearly zálohy net of bonuses, annual tax
    let k := kids.toInt!
    let mut m := lo.toInt!
    while m ≤ hi.toInt! do
      out.putStrLn s!"{m}	{yearWithheld m k}	{annualTax m k}	{settlement m k}"
      m := m + step.toInt!
    return 0
  | [f] =>
    let h ← IO.FS.Handle.mk f .read
    loop oecd (IO.FS.Stream.ofHandle h) out
    return 0
  | _ => IO.eprintln "usage: cztax [--oecd] [households.jsonl]"; return 2
