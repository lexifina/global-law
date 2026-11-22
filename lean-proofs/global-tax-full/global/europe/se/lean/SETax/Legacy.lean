import SETax.Assess
import SETax.Table

/-!
# `setax`: canonical households in, contract outputs out (JSONL)

    setax [--oecd] [--state-first] < households.jsonl
    setax --table T COL MONTH     (one withholding-table cell: table number, column 1/2/3/6, monthly wage; the wage
                                   is placed in its band and the band's highest amount is used, SKV 433 avsnitt 5, 7.1)

`--oecd`: the OECD Taxing Wages convention (national average municipal rate 32,41 %, no begravningsavgift; the
municipal tax is reported before the skattereduktioner, which are all booked against central government
(`incomeTax` = statlig skatt − every reduction used, may be negative); the public service-avgift is not counted
(kept in `detail.publicServiceAvgiftNotCounted`)). Round 1 (2026-11-19): the split and the fee are OECD
presentation conventions, not statute: IL 67 kap. 2 § sets the reductions against "kommunal inkomstskatt, statlig
inkomstskatt ..." (statute mode keeps them there), and the fee is levied under lag (2018:1893) 3-5 §§ (statute
mode keeps it in `surtaxes`).
`--state-first`: two-tax credits consume the state tax first (67 kap. 2 § does not fix the order; default
municipal first).

Output (contract): `incomeTax` = statlig inkomstskatt (earned + capital) left after the credits set against it;
`localIncomeTax` = kommunal inkomstskatt left after the credits; `surtaxes` = public service-avgift and
begravningsavgift (fees charged on the same return); `employeeSocial` = allmän pensionsavgift (+ egenavgifter of
the self-employed); `benefits` = barnbidrag + flerbarnstillägg. `detail.persons` has every line of each return.
-/

namespace SETax
open TaxKernel Lean

def personJson (r : PersonResult) : Json :=
  Json.mkObj [("fyllt66VidAretsIngang", Json.bool r.old), ("tjanst", toJson r.tjanst), ("naring", toJson r.naring),
    ("egenavgifter", toJson r.egenavg), ("faststalldForvarvsinkomst", toJson r.ffi), ("grundavdrag", toJson r.ga),
    ("beskattningsbarForvarvsinkomst", toJson r.bfi), ("kapital", toJson r.kapital),
    ("kommunalInkomstskatt", toJson r.municipalTax), ("statligInkomstskatt", toJson r.stateTaxEarned),
    ("statligSkattKapital", toJson r.stateTaxCapital), ("allmanPensionsavgift", toJson r.fee),
    ("jobbskatteavdrag", toJson r.jsaAmount), ("skattereduktionForvarvsinkomst", toJson r.fiAmount),
    ("skattereduktionUnderskott", toJson r.deficitAmount), ("skattereduktionGava", toJson r.giftAmount),
    ("usedPension", toJson r.used.pension), ("usedJobb", toJson r.used.jobb), ("usedForvarv", toJson r.used.forvarv),
    ("usedUnderskott", toJson r.used.underskott), ("usedGava", toJson r.used.gava),
    ("kommunalNet", toJson r.municipalNet), ("statligNet", toJson r.stateNet),
    ("publicServiceAvgift", toJson r.publicServiceFee), ("begravningsavgift", toJson r.burialFee),
    ("total", toJson r.total)]

def sumBy (l : List PersonResult) (f : PersonResult → Int) : Int := l.foldl (fun a r => a + f r) 0

def out (base : Params) (stateFirst : Bool) (oecd : Bool) (c : Canon) : Out :=
  let p := paramsFor base c
  let h := household p stateFirst c
  let ps := h.persons
  let munGross := sumBy ps (·.municipalTax)
  let munNet := sumBy ps PersonResult.municipalNet
  let stNet := sumBy ps PersonResult.stateNet
  let psFee := sumBy ps (·.publicServiceFee)
  let uns : List String :=
    (if c.pensionContributions ≠ 0 then ["pensionContributions: not deductible for employees with pension rights "
      ++ "(IL 59 kap. 3 §); ignored"] else [])
    ++ (if ps.any (fun r => r.naring > 0) then ["self-employment: egenavgifter in the steady state; nedsättning "
      ++ "(SAL 3 kap. 15-16 §§), periodiseringsfond, expansionsfond, räntefördelning not modelled"] else [])
    ++ (if c.children.any (fun k => k.age ≥ 16) then ["children 16+: förlängt barnbidrag and studiebidrag "
      ++ "(CSN) not modelled"] else [])
    ++ (if c.year < 2025 then ["2022-2024: begravningsavgift at the 2025 Stockholm rate (not sourced); the 65/66+ "
      ++ "jobbskatteavdrag and förhöjt grundavdrag use the 2025 formulas; egenavgift rates as 2025"] else [])
    ++ ["kyrkoavgift (church members only) not included", "ISK/KF schablon, fastighetsavgift, RUT/ROT, "
      ++ "sjukersättning, sjöinkomst not modelled"]
  Out.make c "SE" "SEK" (if oecd then stNet - (munGross - munNet) else stNet)
    (surtaxes := (if oecd then [] else [("publicServiceAvgift", psFee)])
      ++ [("begravningsavgift", sumBy ps (·.burialFee))])
    (localIncomeTax := if oecd then munGross else munNet)
    (employeeSocial := sumBy ps PersonResult.social)
    (benefits := h.barnbidrag)
    (detail := [("persons", Json.arr (ps.map personJson).toArray),
      Out.d "beskattningsbarForvarvsinkomst" (sumBy ps (·.bfi)),
      Out.d "kommunalInkomstskattGross" (sumBy ps (·.municipalTax)),
      Out.d "statligInkomstskattGross" (sumBy ps (·.stateTaxEarned)),
      Out.d "statligSkattKapitalGross" (sumBy ps (·.stateTaxCapital)),
      Out.d "creditsPensionJobbForvarv" (sumBy ps (fun r => r.used.pension + r.used.jobb + r.used.forvarv)),
      Out.d "creditsAll" (sumBy ps (fun r => r.used.pension + r.used.jobb + r.used.forvarv + r.used.underskott
        + r.used.gava)),
      Out.d "kommunBp" p.kommun, Out.d "begravningBp" p.begravning,
      Out.dStr "region" (if p.kommun = 3060 then "Stockholm (0180)" else "custom municipal rate"),
      Out.dStr "creditOrder" (if stateFirst then "state first" else "municipal first"),
      Out.d "publicServiceAvgiftNotCounted" (if oecd then psFee else 0),
      Out.dStr "convention" (if oecd then "OECD Taxing Wages (--oecd)" else "statute")])
    (unsupported := uns)

def country (base : Params) (stateFirst : Bool) (oecd : Bool := false) : Country :=
  { code := "SE", name := "Sweden (Stockholm)", currency := "SEK", year := "2025",
    compute := out base stateFirst oecd }

end SETax

/-- `--euromod` (round 15, convention flag for the EUROMOD grids only; statute mode is the default): EUROMOD's
published methodology, Country Report Sweden 2022-2025 (software/euromod/country_reports/Y16_CR_SE.pdf, sha256
cbc279ba…c0, § 2.6.6 Tax schedule): "Since information on the region persons are living in is not included in
EUROMOD, the taxes are simulated according to the average value for Sweden", Table 2.28 (municipality / county
council / funeral tax): 2022 20,67 / 11,56 / 0,261 %; 2023 20,67 / 11,57 / 0,258 %; 2024 20,7 / 11,67 / 0,277 %;
2025 20,71 / 11,69 / 0,293 %. The flag sets kommun = municipality + county (bp) and the begravningsavgift at the
funeral rate; explicit `seKommunBp` / `seBegravningBp` / `seBegravning100k` inputs still win. The public
service-avgift stays statutory (the country report states no convention for it). `--oecd` is not implied. -/
def euromodRates (y : Nat) : Int × Int :=
  if y = 2022 then (3223, 261) else if y = 2023 then (3224, 258) else if y = 2024 then (3237, 277) else (3240, 293)

def setIfAbsent (j : Lean.Json) (k : String) (v : Int) : Lean.Json :=
  match j with
  | .obj _ => (match j.getObjVal? k with | .ok _ => j | .error _ => j.setObjVal! k (Lean.toJson v))
  | _ => j

def euromodCanon (c : TaxKernel.Canon) : TaxKernel.Canon :=
  let (k, b) := euromodRates c.year
  { c with raw := setIfAbsent (setIfAbsent c.raw "seKommunBp" k) "seBegravning100k" b }

open SETax in
def legacyMain (args : List String) : IO UInt32 := do
  match args with
  | ["--table", t, col, m] =>
    IO.println (toString (tableMonthly t.toInt! col.toNat! (bandTop m.toInt!)))
    return 0
  | _ =>
    let base := if args.contains "--oecd" then p2025oecd else p2025
    let k := country base (args.contains "--state-first") (args.contains "--oecd")
    -- (`computeWith` defaults to the original `compute`, so both are replaced)
    let euro : TaxKernel.Canon → TaxKernel.Out := fun c =>
      let o := k.compute (euromodCanon c)
      { o with detail := o.detail ++ [TaxKernel.Out.dStr "convention2" "EUROMOD (--euromod): CR SE 2.6.6 Table 2.28"] }
    let k := if args.contains "--euromod" then { k with compute := euro, computeWith := fun _ c => euro c } else k
    TaxKernel.countryMain k args
