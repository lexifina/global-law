import HuTax.Model

/-!
# Hungary: canonical household → model inputs → contract output

Canonical fields (`~/cmp/shared/CONTRACT.md`) and Hungary-only optional fields:
* per adult: `huBirthMonth` (1-12, default 7: the month of the 25th birthday for an adult aged 25 in 2025),
  `huMother4` (§ 29/D), `huMother3` (2025. évi XV. tv., from October), `huQ4` (qualifying income earned after
  30 September), `huU30Months` (§ 29/G months), `huDisabled` (§ 29/E), `huPensioner` (default: `pension > 0`),
  `huSkilled` (guaranteed-minimum-wage bases), `huRegime` ("atalany" default for `selfEmployment`, or "kata"),
  `huSelfRevenue` (revenue; then `selfEmployment` is ignored and the átalány income is revenue × (1 − cost ratio)),
  `huCostRatio` (40, 80 or 90 %), `huKataMonths`;
* per household: `huStudents` (children 18+ still in education for whom családi pótlék is paid), `huExtraDependants`
  (dependants counted but not beneficiaries, § 29/A (5) b)), `huDisabledChildren` (§ 29/A (2a)),
  `huFirstMarriageMonths` (§ 29/C), `huCspMonths`, `huInYearCredit` (§ 29/B (6)), `huFrame` (a family-allowance
  frame to use instead of the 2025 one, for year-shift scans), `cohabiting`; per adult also `huYouthIncome` /
  `huU30Income` (income accounted to the under-25 / under-30-mother months; default pro rata).
Children under 18 are beneficiaries (családi pótlék is paid to the end of schooling: use `huStudents` for older ones).
Investment and rental income of a couple are split half and half (contract).
-/

namespace HuTax
open TaxKernel Lean

def rawAdult (c : Canon) (i : Nat) : Json :=
  match c.raw.getObjVal? "adults" with
  | .ok (.arr a) => a.getD i Json.null
  | _ => Json.null

def strField (j : Json) (k : String) (d : String := "") : String :=
  match j.getObjVal? k with
  | .ok (.str s) => s
  | _ => d

def personOf (c : Canon) (i : Nat) (a : Adult) (interest dividends gains rental : Int) : Person :=
  let j := rawAdult c i
  let regime := strField j "huRegime" "atalany"
  let rev := intField j "huSelfRevenue" (-1)
  let cost := intField j "huCostRatio" 40 * 100
  let selfInc := if rev ≥ 0 then atalanyIncome rev cost else a.selfEmployment
  let kata := regime == "kata"
  { age := a.age, wages := a.wages,
    atalany := if kata then 0 else selfInc,
    skilled := boolField j "huSkilled",
    rental, disabled := boolField j "huDisabled",
    birthMonth := natField j "huBirthMonth" 7,
    mother4 := boolField j "huMother4", mother3 := boolField j "huMother3",
    q4 := intField j "huQ4" (-1), u30Months := natField j "huU30Months" 0,
    youthIncome := intField j "huYouthIncome" (-1), u30Income := intField j "huU30Income" (-1),
    pensioner := boolField j "huPensioner" (a.pension > 0),
    kata, kataRevenue := if kata then (if rev ≥ 0 then rev else a.selfEmployment) else 0,
    kataMonths := natField j "huKataMonths" 12,
    interest, dividends, gains, year := c.year }

/-- 2025-only allowances (§ 29/G under-30 mothers from 2025.I.1; 2025. évi XV. tv. mothers of three from
2025.X.1) do not exist in earlier years. -/
def gateYear (y : Nat) (p : Person) : Person :=
  if y ≥ 2025 then p else { p with mother3 := false, u30Months := 0 }

def houseOf (c : Canon) (startOfYear : Bool := false) : House :=
  let couple := c.adults.length == 2 && (c.married || (c.bool? "cohabiting").getD false)
  let n := c.adults.length
  let split (x : Int) (i : Nat) : Int := if n ≥ 2 then (if i = 0 then half1 x else if i = 1 then half2 x else 0) else x
  -- `--eurostat`: the mothers-of-three exemption (2025. évi XV. tv., in force 2025.X.1) is a later-in-year change
  let persons := (c.adults.zip (List.range n)).map fun (a, i) =>
    (fun p => if startOfYear then { p with mother3 := false } else p) <| gateYear c.year <|
    personOf c i a (split c.interest i) (split c.dividends i) (split c.capitalGains i) (split c.rentalIncome i)
  let bens := c.childrenUnder 18 + ((c.int? "huStudents").getD 0).toNat
  let deps := bens + ((c.int? "huExtraDependants").getD 0).toNat
  { persons, couple, deps, bens, disabledKids := ((c.int? "huDisabledChildren").getD 0).toNat,
    firstMarriageMonths := if c.married then ((c.int? "huFirstMarriageMonths").getD 0).toNat else 0,
    cspMonths := ((c.int? "huCspMonths").getD 12).toNat,
    inYearCredit := (c.int? "huInYearCredit").getD 0, frame := c.int? "huFrame", year := c.year, startOfYear }

def personJson (p : Person) (s : Stage1) (fm fam tax tbg fc tb ss kt cs cz : Int) : Json :=
  Json.mkObj [("base", toJson s.base), ("atalanyTaxable", toJson s.atTaxable), ("mothers", toJson s.mothers),
    ("under25", toJson s.youth), ("under30Mothers", toJson s.u30), ("personal", toJson s.personal),
    ("firstMarriage", toJson fm), ("family", toJson fam), ("taxable", toJson (s.rest - fm - fam)),
    ("szja", toJson tax), ("tbGross", toJson tbg), ("familyContribCredit", toJson fc), ("tb", toJson tb),
    ("szochoSelf", toJson ss), ("kata", toJson kt), ("capitalSzja", toJson cs), ("capitalSzocho", toJson cz),
    ("age", toJson p.age)]

def outWith (args : List String) (c : Canon) : Out :=
  -- `--euromod` (convention, not statute; EUROMOD "Nowcasting prices" note, Feb 2025, s. 1.3-1.4: parameters "referred
  -- in EM to 30 June"; country report HU 2022-2025 lists the § 29/A (2) increase under "Additional notes (from 1st of
  -- July 2025)"): on 30 June 2025 the January-June family-allowance amounts and no mothers-of-three exemption
  -- (2025.X.1) were in force, the same parameters as on 1 January for an employee in 2022-2025, so it shares the
  -- start-of-year path. Not switched: the December 2023 minimum wage for sole traders' minimum bases (no grid case).
  let h := houseOf c (args.contains "--eurostat" || args.contains "--euromod")
  let r := compute h
  let n := h.persons.length
  let g (l : List Int) (i : Nat) : Int := l.getD i 0
  let persons := (List.range n).map fun i =>
    personJson (h.persons.getD i default) (r.stages.getD i default) (g r.firstMarriage i) (g r.family i)
      (g r.szja i) (g r.tbGross i) (g r.famCredit i) (g r.tb i) (g r.szochoSelf i) (g r.kata i) (g r.capSzja i)
      (g r.capSzocho i)
  let szjaAll := sumInts r.szja
  Out.make c "HU" "HUF" (szjaAll + sumInts r.capSzja)
    (surtaxes := [("szochoCapital", sumInts r.capSzocho), ("szochoSelfEmployed", sumInts r.szochoSelf),
      ("kata", sumInts r.kata)])
    (employeeSocial := sumInts r.tb) (benefits := r.csp)
    (detail := [Out.d "taxableIncome" (sumInts r.taxable), Out.d "taxBeforeCredits" szjaAll,
      Out.d "familyFrame" r.frame, Out.d "familyUsedAgainstTax" (sumInts r.family),
      Out.d "familyContribCredit" (sumInts r.famCredit), Out.d "tbGross" (sumInts r.tbGross),
      Out.d "under25" (sumInts (r.stages.map (·.youth))), Out.d "mothers" (sumInts (r.stages.map (·.mothers))),
      Out.d "capitalSzja" (sumInts r.capSzja), Out.d "csaladiPotlek" r.csp,
      Out.dBool "couple" h.couple, ("persons", Json.arr persons.toArray),
      Out.dStr "note" "Szja tv. 2025 (annual return), Tbj. 18.5 % TB with family contribution allowance, Cst. családi pótlék; amounts in whole forints"])
    (unsupported := ["CSED/GYED/örökbefogadói díj allowance (2025. évi XVI. tv.) not modelled",
      "sole trader with itemised costs (vállalkozói jövedelem/kivét) not modelled: selfEmployment is read as átalány income",
      "monthly withholding (adóelőleg) not modelled: annual liability only",
      "children 18+ in education only via huStudents"] ++
      (if c.year = 2022 then ["tax year 2022: KATA: the old regime (January-August 2022, 2012. évi CXLVII. tv.) is not modelled (2022. évi XIII. tv. rules used)"]
       else if c.year = 2023 || c.year = 2024 then ["tax year " ++ toString c.year ++ ": the under-25 cap uses the 2025 amount (the KSH July average wage of the year before not cited); szocho on interest under the 2023 emergency decree not modelled; KATA as in 2025 (2022. évi XIII. tv.)"] else []))

def out (c : Canon) : Out := outWith [] c

def country : Country :=
  { code := "HU", name := "Hungary", currency := "HUF", year := "2025", compute := out, computeWith := outWith }

end HuTax
