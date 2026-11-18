import Lean.Data.Json
import JpTax.Household

/-!
# `jptax`: canonical households (JSONL) in, contract outputs (JSONL) out

    jptax [households.jsonl]      (stdin when no file is given)

Input: the shared contract's household (`~/cmp/shared/CONTRACT.md`). Japan-only optional fields: `children[].wages`
(a child's salary, for the 扶養 walls), `jpDividends` ("separate" = 確定申告不要, the default; "aggregate" = 総合課税
with 配当控除), `jpSingleParentSex` ("F", the default, or "M"). Output: one object per line, in the same order.
-/

open Lean JpTax

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

def parseHousehold (j : Json) : Household :=
  { id := jStr j "id", year := jInt j "year" 2025,
    adults := (jArr j "adults").toList.map fun a =>
      { age := jInt a "age" 40, wages := jInt a "wages", selfEmployment := jInt a "selfEmployment",
        pension := jInt a "pension" },
    married := jBool j "married",
    children := (jArr j "children").toList.map fun c => { age := jInt c "age", wages := jInt c "wages" },
    interest := jInt j "interest", dividends := jInt j "dividends", capitalGains := jInt j "capitalGains",
    rentalIncome := jInt j "rentalIncome", charitable := jInt j "charitable",
    pensionContributions := jInt j "pensionContributions",
    aggregateDividends := jStr j "jpDividends" "separate" == "aggregate",
    declaredDividends := jStr j "jpDividends" "separate" == "declared",
    declaredGains := jStr j "jpGains" "withheld" == "declared",
    singleParentMother := jStr j "jpSingleParentSex" "F" != "M" }

def ji (i : Int) : Json := toJson i

def personJson (p : PersonIn) (o : PersonOut) (s : SocialOut) : Json :=
  Json.mkObj [
    ("age", ji p.age), ("wages", ji p.wages),
    ("salaryIncome_kyuyoShotoku", ji o.kyuyo),
    ("incomeAdjustment_shotokuKingakuChoseiKojo", ji o.adjust),
    ("pensionIncome_nenkinZatsuShotoku", ji o.nenkin),
    ("totalIncome_gokeiShotoku", ji o.sogo),
    ("deductions", Json.mkObj [
      ("social_shakaiHokenryo", ji o.dSocial), ("ideco_shokiboKyosai", ji o.dIdeco),
      ("donations_kifukin", ji o.dKifukin), ("singleParent_hitorioya", ji o.dHitorioya),
      ("spouse_haigusha", ji o.dHaigusha), ("spouseSpecial_haigushaTokubetsu", ji o.dTokubetsu),
      ("dependants_fuyo", ji o.dFuyo), ("specifiedRelative_tokuteiShinzoku", ji o.dTokuteiShinzoku),
      ("basic_kiso", ji o.dKiso)]),
    ("taxableIncome_kazeiSoShotoku", ji o.taxable),
    ("taxBeforeCredits_sanshutsuZei", ji o.sanshutsu),
    ("dividendCredit_haitoKojo", ji o.haito),
    ("incomeTax_kijunShotokuZei", ji o.kijun),
    ("minimumTax_41no19", ji o.minTax),
    ("declaredSeparateTaxable", ji o.declTaxable),
    ("reconstructionTax_fukko", ji o.fukko),
    ("nationalPayableRounded100", ji o.national),
    ("local", Json.mkObj [
      ("deductions", ji o.loc.deductions), ("taxable_kazeiSoShotoku", ji o.loc.base),
      ("prefectural4pct_raw", ji o.loc.prefRaw), ("municipal6pct_raw", ji o.loc.muniRaw),
      ("adjustmentCredit_choseiKojo_pref", ji o.loc.choseiPref),
      ("adjustmentCredit_choseiKojo_muni", ji o.loc.choseiMuni),
      ("incomeLevy_shotokuwari_pref", ji o.loc.pref), ("incomeLevy_shotokuwari_muni", ji o.loc.muni),
      ("perCapita_kintowari", ji (o.loc.kintoPref + o.loc.kintoMuni)),
      ("forestEnvironmentTax_shinrin", ji o.loc.shinrin)]),
    ("social", Json.mkObj [
      ("standardMonthly_health", ji s.kenpoStd), ("standardMonthly_pension", ji s.kouseiStd),
      ("health_kenkoKaigo", ji s.health), ("pension_kouseiNenkin", ji s.pension), ("employment_koyo", ji s.koyo)])]

def resultJson (h : Household) (r : Result) : Json :=
  Json.mkObj [
    ("id", Json.str h.id), ("country", Json.str "JP"), ("currency", Json.str "JPY"),
    ("incomeTax", ji r.incomeTax),
    ("surtaxes", Json.mkObj [("復興特別所得税", ji r.fukkoTotal)]),
    ("localIncomeTax", ji r.localTax),
    ("employeeSocial", ji r.employeeSocial),
    ("benefits", ji r.benefits),
    ("detail", Json.mkObj [
      ("taxYear", Json.str "令和7年分 (2025); 住民税 = 令和8年度 tax on 2025 income, Tokyo special wards"),
      ("persons", Json.arr (r.persons.map (fun (p, o, s) => personJson p o s)).toArray),
      ("separateTaxation", Json.mkObj [
        ("national15pct", ji r.sepNational), ("reconstruction0315pct", ji r.sepFukko), ("local5pct", ji r.sepLocal),
        ("dividends", Json.str (if h.aggregateDividends then "aggregate (総合課税)"
          else if h.declaredDividends then "declared (申告分離課税)" else "separate (確定申告不要)")),
        ("gains", Json.str (if h.declaredGains then "declared (申告分離課税)" else "withheld (特定口座, 確定申告不要)"))]),
      ("childAllowance_jidoTeate", ji r.benefits),
      ("idecoIgnored", ji r.idecoIgnored)]),
    ("unsupported", Json.arr (r.unsupported.map Json.str).toArray)]

def runLine (line : String) : String :=
  match Json.parse line with
  | .error e => (Json.mkObj [("error", Json.str e)]).compress
  | .ok j =>
    let h := parseHousehold j
    (resultJson h (compute h)).compress

partial def loop (inp : IO.FS.Stream) (out : IO.FS.Stream) : IO Unit := do
  let line ← inp.getLine
  if line.isEmpty then return
  let t := line.trimAscii.toString
  if !t.isEmpty then out.putStrLn (runLine t)
  loop inp out

def main (args : List String) : IO UInt32 := do
  let out ← IO.getStdout
  match args with
  | [] => loop (← IO.getStdin) out; return 0
  | [f] =>
    let h ← IO.FS.Handle.mk f .read
    loop (IO.FS.Stream.ofHandle h) out
    return 0
  | _ => IO.eprintln "usage: jptax [households.jsonl]"; return 2
