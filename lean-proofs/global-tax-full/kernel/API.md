# TaxKernel API (v2.9.0, 2026-11-22): the shared kernel of the 20- and 38-country comparisons

Owner: kernel agent. **Stable**: names and signatures below will not change; new parts and theorems are only
added (listed under "Changes" at the end). Source: `cmp20/kernel/TaxKernel/*.lean` (read the file docstrings for
the details and the statutes each example comes from). Lean 4.35 core only.

**Status (live; see `PROGRESS.md`)**: 1.4.0 (2026-11-20) adds `TaxKernel.World2` (column tariffs, coefficient-indexed amounts; §4d) and world reference wages in the harness (§7c). 1.3.0 (2026-11-20) adds `TaxKernel.World` for the world expansion (§4c; import it explicitly; the 38 unchanged). 1.2 (2026-11-19) adds the parts for the 38 (§4b) and the harness and referees for all 38 (§7b: your exe is found automatically; OECD check for the 13 members, Eurostat sanity check for BG HR CY MT RO). Earlier: §1-§5 built, tested and proved (no `sorry`; every §5 theorem is instantiated
for the toy country in `examples/zz/lean/ZzTax/Theorems.lean`: copy from there). §7 harness: `tax20`, `run20.py`,
`oecd_check20.py` and the generic scanners (`harness/search/run_all.py`) work on all 20 exes; first-pass scanner
leads per country are in `cmp20/kernel/LEADS.md` (check them against your statute; rerun on your current exe).

## 1. Depend on it (tested with the toy country `cmp20/kernel/examples/zz/lean`)

Your project `cmp20/<owner>/<cc>/lean/`:

```
lean-toolchain        leanprover/lean4:v4.35.0
lakefile.toml
<CC>Tax.lean          import <CC>Tax.Basic ...
<CC>Tax/Basic.lean    import TaxKernel   (the whole kernel; or import TaxKernel.Schedule etc.)
<CC>Tax/Main.lean     def main (args : List String) : IO UInt32 := TaxKernel.countryMain <CC>Tax.country args
```

`lakefile.toml` (e.g. Canada; lib `CaTax`, exe `catax`):

```toml
name = "CaTax"
version = "0.1.0"
defaultTargets = ["CaTax", "catax"]

[[require]]
name = "TaxKernel"
path = "../../../kernel"        # from cmp20/<owner>/<cc>/lean

[[lean_lib]]
name = "CaTax"

[[lean_exe]]
name = "catax"
root = "CaTax.Main"
```

Then `export PATH=$HOME/.elan/bin:$PATH; lake build`. The exe lands in `.lake/build/bin/<cc>tax`, where the harness
finds it automatically (`cmp20/harness/tax20.py`). The kernel's oleans live in `cmp20/kernel/.lake/build`; the
kernel owner rebuilds after every change, so your build only reads them. If your build ever reports a TaxKernel
file changed underneath it, run `lake build` again.

## 2. The exe speaks the contract

```lean
def country : TaxKernel.Country :=
  { code := "CA", name := "Canada (federal + Ontario)", currency := "CAD", year := "2025", compute := out }
-- options from the command line (e.g. `--separate`) reach `computeWith args c` (defaults to `compute c`)
```

`TaxKernel.countryMain country args` reads canonical households (JSONL, `cmp/shared/CONTRACT.md`) from stdin and
writes one output line each, same order; a bad line gives `{"id":…,"error":…}`; `--version` prints a JSON line
with country, currency, year and kernel version; `--help` the usage.

Input: `TaxKernel.Canon` (copied from `cmp/compare/lean/Compare/Canon.lean`, namespace `TaxKernel`):
`id year adults married children interest dividends capitalGains rentalIncome charitable pensionContributions`,
`Adult := {age wages selfEmployment pension}`, `Child := {age}`. Added: `raw : Json` (the whole input line) with
`c.str? "k"`, `c.int? "k"`, `c.bool? "k"` for extra fields (elections, region); helpers `c.adult1`, `c.adult2?`,
`c.isCouple`, `c.nChildren`, `c.childrenUnder age`, `a.earnings` (wages + self-employment), `c.investment`,
`c.gross`, `half1 x` / `half2 x` (split a household total between two returns, first gets the odd unit).

Optional extra input fields the kernel's scanners set (read them with `c.bool? "…"` if your law needs them; ignore
them otherwise; the contract itself is unchanged):
* `"cohabiting": true` on two-adult households with `married: false` (filing-unit scanner): the two adults live
  together as a couple. Countries whose law treats cohabiting partners as a couple (Canada's common-law partners,
  Australia's de facto partners, …) should treat such a household as a couple; without it the scanner reports the
  difference between a couple and two unrelated adults as a "marriage penalty" (kernel FINDINGS K8).
* `"region": "…"`: a sub-national default other than yours (e.g. the UK model reads `"scotland"`).

Output: `TaxKernel.Out` (`id country currency incomeTax surtaxes localIncomeTax employeeSocial benefits detail
unsupported`), built with

```lean
Out.make c "CA" "CAD" incomeTax (surtaxes := [("OntarioHealthPremium", p)]) (localIncomeTax := ont)
  (employeeSocial := cpp + ei) (benefits := ccb) (detail := [Out.d "taxableIncome" ti, Out.dStr "note" "…"])
  (unsupported := ["…"])
```

## 3. Units

Money: `Int` whole units (the statute's unit of account; cents only if the statute computes in cents). Rates:
`Int` basis points (2000 = 20 %). Ticks: units × bp (tax before rounding). `BP = 10000`. Helpers (`Basic`):
`pos x = max 0 x`, `clamp lo hi x`, `overlap a b lo hi`, `above a b lo`, `ceilDiv a b`.

## 4. Parts

| Part | Module | Main names | Typical statute |
|---|---|---|---|
| Rounding | `Rounding` | `Round` (`down up halfUp halfDown halfEven towardZero`), `divR m n d`, `toMultiple m step x`, `ticksToUnits m t`, `Rule {mode step}`, `Rule.unitDown`, `Rule.downTo 100`, `Rule.apply`, `Rule.ofTicks` | JP 1,000-yen floor, DE whole euros, UK s. 35(3) round up |
| Schedule | `Schedule` | `Band {lo rate}`, `Schedule.ofList [(0,2000),(37700,4000)]`, `Schedule.ofUpper [(57375,1500),…] 3300`, `flat r`, `flatAbove lo r`, `s.ticks x`, `s.tax rule x`, `s.rate x` (marginal bp on `(x,x+1]`), `s.sliceTicks a b` (stacking), `s.topRate`, `s.maxRate`, `s.withZeroBand a`, `s.mapLo f`, `s.progressive : Bool` | any bracket table |
| Allowance / Taper | `Allowance` | `Taper {full start num den floor round}`, `Taper.fixed a`, `t.amount inc`, `t.reduction inc`, `t.bandEnd`, `taxableAfter allowance income`, `usedAllowance`, `unusedAllowance`, `cappedDeduction claimed cap pct base` | UK PA taper, phase-outs |
| Credit | `Credit` | `Credit {full inRate start num den floor round refundable}`, `c.value earn inc`, `applyCredits tax nonref ref`, `applyCreditsOrdered tax [(v, refundable?)]`, `usedCredit`, `sumInts` | CA/AU/NZ offsets, IE credits, EITC-style |
| Surcharge / levy | `Surcharge` | `Surcharge {rate exempt deduct glide round}`, `s.ticks base`, `s.amount base`, `Surcharge.withGlide rate exempt glide`, `Surcharge.flatPct r`, `Surcharge.above r thr` | DE Soli, JP 復興税, AU Medicare levy shade-in, NIIT |
| Unit of assessment | `Unit` | `AssessUnit (individual joint splitting quotient)`, `separate f a b`, `joint f a b`, `splitting f a b`, `quotient f n2 r` (n2 = half-parts), `cappedQuotient f n2 base2 cap r`, `transferAllowance a1 a2 inc1 cap`, `Convex f` | DE/PT/PL splitting, FR quotient, UK marriage allowance |
| Dual income | `Dual` | `Dual {earned capital capitalAllowance deficit}`, `d.ticks e c`, `d.earnedTicks`, `d.capitalTicks`, `d.deficitTicks`, `d.wedge e c` | SE/NO/DK, NL boxes, JP 分離課税 |
| Social | `Social` | `Contribution {name sched floor ceiling round}`, `Contribution.flatCapped name rate ceiling`, `c.amount earn`, `contributionsTotal cs earn`, `contributionsDetail cs earn` | NI, SV, CPP/EI, PRSI… |
| Canon / Out / Country | `Canon`, `Country` | see §2 | the contract |
| Lookup table, per-period rules (1.1) | `Table` | `Row {lo hi value}`, `Table.lookup t x d`, `Table.contiguous`, `Table.valuesMono`, `Table.valuesAnti`, `Table.agreesWith t f probe tol`, `Table.disagreements t f probe tol`, `Table.ofFormula`, `perPeriod n f annual` (a monthly rule summed over the year) | KR 산정표, MX tarifas, withholding tables, monthly contributions |

Not a kernel part (write it in the country and say so in `kernel_gaps`): formula tariffs (DE § 32a polynomial:
use a plain `Int → Int`; every Unit theorem takes any `f`), lookup tables, regional rules.

## 4b. Parts added in 1.2 for the 38 (`TaxKernel.Multiplier`, `TaxKernel.Family`, `TaxKernel.Tariff`; in `import TaxKernel`)

Everything in §4 is unchanged; these are added. Toy calls of each, checked by `#guard`: `cmp20/kernel/examples/Parts38.lean`
(`cd cmp20/kernel && lake env lean examples/Parts38.lean`). Read the module docstrings for the statutes each one is for.

| Part | Names | For (examples; check your own statute) |
|---|---|---|
| Multipliers on a base tax | `Multiplier {name rate round}` (rate in bp **of the base tax**, may exceed 10000), `m.amount base`, `applyMultipliers ms base` (named list, ready for `surtaxes`/`localIncomeTax`), `multipliedTotal ms base` | CH cantonal + municipal Steuerfuss on the "einfache Steuer" (canton ZH, city of Zürich), BE additional municipal tax (% of state tax), LU employment-fund surcharge, IS/FI municipal tax if written as a % of another tax |
| Tax at an average rate | `atAverageRate m f rateIncome taxable` (= `f rateIncome × taxable / rateIncome`), `averageRateScaled f x scale` (the rate itself, e.g. to 4 decimals), `rateSplitting m f divisorBp x` (rate taken at `x / divisor`, applied to all of `x`) | progression clause (AT EStG § 3 (3), LU LIR art. 134, BE exemption with progression, CH DBG Art. 7); Swiss rate splitting with a divisor (Teilsplitting) and satzbestimmendes Einkommen; `divisorBp = 20000` is full splitting (`rateSplitting_two`) |
| Credit allocation over several taxes | `allocateOrdered v [t1, t2, …]` (state first, then municipal, …), `allocateProportional v [t1, t2, …]` (in proportion, remainder to the first) | IS persónuafsláttur (state then municipal), FI TVL deductions from tax split over state / municipal / church / health-insurance tax, NO/SE ordered credits |
| Child scales | `perChildByRank [a1, a2, a3] n` (later children get the last entry), `perChildByCount [b1, b2, b3] n` (each child gets the entry for the family's size), `familyTotal [t1, t2, t3, t4] extra n` (statute prints cumulative totals) | HR personal-allowance factors by rank, SI dependants by rank, HU családi kedvezmény by number of children, BE supplements to the tax-free sum, LU/AT child amounts |
| Income attribution between spouses | `attributedAmount a b pct cap`, `attributeIncome a b pct cap` (sum unchanged: `attributeIncome_sum`) | BE quotient conjugal (CIR 92 art. 87-88: 30 % of the couple's earned income less the spouse's own, capped) |
| Allowance given at the lowest rates | `lowBandReduction s exempt` (= `s.ticks exempt`), `taxAfterLowBand s exempt income` | BE quotité exemptée (CIR 92 art. 131, 134: tax on the exempt amount at the lowest brackets subtracted from the tax); compare a zero band (`withZeroBand`): `lowBand_le_zeroBand` proves a zero band is never worth less (the difference is what a high earner gains from it) |
| Allowance spilling into another levy | `spillAllowance allowance income rate` → (taxable income, value of the unused part at `rate`) | HU family tax base allowance: the part the income cannot absorb reduces the employee's contributions (15 % of it) |
| Stepped withdrawal | `SteppedTaper {full start perStep step floor}`, `t.amount inc`, `t.toTaper` (the proportional reading), `SteppedTaper.WellFormed` | GR ΚΦΕ art. 16 tax reduction ("20 € per 1,000 €" above 12,000 €): whether the statute means complete steps or proportion is a reading to settle with the official calculator; `stepped_notch` (each step boundary is a notch of `perStep`), `proportional_le_stepped` |
| Contribution base reduced by a taper | `reducedBase t earn` (= `pos (earn − t.amount earn)`), then `Contribution` on it | HR 2024 pension-contribution base reduction at low pay |
| Tariff printed as columns (`TaxKernel.Tariff`) | `CumRow {lo base rate}` (amount at the threshold + rate on the excess), `SubRow {lo rate subtract}` (rate × whole income − subtraction), `cumTicks`, `subTicks`, `Schedule.cumRows s` (the column form of a band schedule), checks `cumAgrees`, `subAgrees`, `cumMonoAt`, `subMonoAt`, `cumJumps`, `subJumps` | MT Cap. 123 art. 56 ("Rate … Subtract"), NL-style column tables (the 20-country NL finding: a rounded column makes the literal tax fall), BE/LU printed tables: state the table literally and prove or refute that it equals the bands |
| Gaps the 18 reported (`TaxKernel.Extra38`, 1.2.1) | `Taper.WellFormedM` + `Taper.amount_antitoneM` (withdrawal rounded half-up/up: SK § 47), `spillAllowanceCapped` (HU Tbj. § 34 (3)), `lowBandReductionOn` / `taxAfterLowBandOn` (exempt sum valued on its own tariff: BE art. 134), `perPeriodIdx n f annual` (`f` gets the period index: mid-year changes, BG/HU/RO/SI), `rateOfBase t base` (rate chosen by the size of the whole base: AT AMPFG § 2a) | INBOX 2026-11-19 |

Recipes for patterns that need **no new part** (use these before writing your own):
* **Flat tax with a tapered basic allowance** (EE, LT, SK, LV-style): `Taper {full, start, num, den}` then `Schedule.flat r`
  (or two bands); the taper band's marginal rate is `taper_marginal` (EE's 2025 "tax hump" is exactly this). Monthly
  statutes: `perPeriod 12 (fun m => …) annual` (Table module).
* **Phase-in then phase-out amounts** (FI earned-income deduction and work-income credit, SK/HR-style child bonus):
  `Credit {full, inRate, start, num, den}`; a phase-in that starts above a threshold: pass `earn - threshold` as `earn`.
* **Swiss federal tariff** (DBG Art. 36: "für je weitere 100 Fr."): a `Schedule` on income rounded down to 100
  (`Rule.downTo 100`), the married tariff as its own `Schedule`, the per-child credit with `applyCredits`.
* **Luxembourg tax classes**: class 2 is `splitting f a b` of the class-1 tariff; class 1a its own tariff function.
* **Malta's single / married / parent tariffs**: one `Schedule` each, chosen by the household (the choice is an
  election if the law leaves it to the taxpayer: `elections.json`).
* **Belgian municipal surcharge, Swiss church tax off**: `Multiplier` / `Surcharge.flatPct` on the state tax.
* **Contribution with a monthly floor/ceiling** (BG maximum insurable income, MT Class 1 weekly bands, HU, RO):
  `Contribution` per period with `perPeriod 12` / `perPeriod 52`, or a `Table`.
* **Cents**: models may compute in cents and convert at the end with `divR .halfUp x 100` (the statute's rounding);
  `Out` carries whole units (contract).

New theorems (file `TaxKernel/Theorems/Parts38.lean`, no `sorry`, in `audit/Axioms.lean`): `Multiplier.amount_mono`,
`atAverageRate_self`, `rateSplitting_two`, `allocateOrdered_total_le`, `allocateOrdered_head_le`, `attributeIncome_sum`,
`attributedAmount_bounds`, `lowBand_le_zeroBand`, `taxAfterLowBand_slice`, `spillAllowance_nonneg`,
`SteppedTaper.proportional_le_stepped`, `SteppedTaper.stepped_notch`; helpers `sumInts_cons`, `foldl_add_init`.

## 4c. Parts added in 1.3.0 for the world expansion (`TaxKernel.World`; import it explicitly)

`import TaxKernel.World` (it imports the whole of `TaxKernel`). It is **not** imported by the root module `TaxKernel`,
so the 38 models are unchanged by construction; all 33 kernel-built models were rebuilt against 1.3.0 in a copy
(`cmp20/world/kcheck/check38.log`, 2026-11-20): every one builds and its output on a fixed 44-household grid is
byte-identical to the live exe. World models call **`TaxKernel.worldMain country args`** (`countryMain` with kernel
1.3.0 under `--version`). Toy calls checked by `#guard`: `cmp20/kernel/examples/World.lean`
(`lake env lean examples/World.lean`); axioms: `audit/AxiomsWorld.lean` (no `sorry`).

| Part | Names | For (check your own statute) |
|---|---|---|
| Indexed units | `unitsToMoney m scale unitValue u`, `moneyToUnits m scale unitValue x`, `Schedule.ofUnits [(u, rateBp), …] m scale unitValue` (thresholds printed in units, `scale` = 1000 for thousandths), `viaUnits f mIn mOut scale unitValue x` (statute computes the tax in units and converts the result) | CL UTM/UTA, CO UVT (ET art. 241 prints the tax in UVT), PE UIT, UY BPC, VE unidad tributaria; minimum-wage multiples. Theorems `ofUnits_rates` (rates kept), `unitsToMoney_mono` |
| Schedular (cedular) systems | `Cedula {name base tax}`, `c.amount`, `cedularTotal`, `cedularBase`, `cedularDetail` (for `detail`/`surtaxes`), `overlayTax f cs credit` (annual tax on the sum of the categories; `credit := true` credits the category taxes, floored at 0) | CR salary tax beside other rents; RS salary tax + annual citizens' income tax (overlay without credit); CL global complementario with the impuesto único credit (overlay with credit); LB LY SY CD ET category taxes; UY/PE categories. Theorems `cedularTotal_append`, `overlay_credit_total` (with the credit the household pays exactly `max (category taxes) (global tax)`), `overlay_credit_nonneg` |
| Zakat / all-or-nothing levy | `zakat nisab rateBp : Contribution` (`floor := nisab`; use `Contribution.amount`) | where a statute levies zakat on wages or savings (2.5 % above a nisab). `zakat_notch` = `Contribution.floor_notch` instantiated. Zakat credited against income tax (MY ITA s. 6A(3)): `applyCredits`; deducted from income: `taxableAfter` |
| Territorial base | `sourceBase territorial domestic foreign`, `Canon.foreignIncome c` (optional input field `"foreignIncome"`, whole local units, household total, 0 when absent) | PA, CR, PY, BO-style source rules vs worldwide taxation. `sourceBase_territorial_le` |
| Exemption written as a tax | `exemptTaxOf f exempt x = pos (f x - f (min x exempt))` | TR GVK: the tax on the minimum wage is exempt. `exemptTaxOf_below`, `exemptTaxOf_le` |
| Cumulative withholding | `cumWithholdings f prev [c1, c2, …]` (instalment = tax on the cumulative base less the tax already withheld), `lastOr`, `listSum` | TR monthly cumulative tariff, PAYE systems (ZA, KE, UK-style). `cumWithholdings_sum`: the instalments telescope to `f (last) - f prev` |

Recipes (no new part): flat tax above a monthly threshold (TL) `perPeriod 12 (fun m => (Schedule.flatAbove t r).tax rule m) annual`;
credit points (IL) a non-refundable `Credit` of points × point value; capped number of dependants (ID PTKP) `perChildByRank
[a, a, a, 0] n`; family parts (SN, CG, GA) `quotient` / `cappedQuotient`; communal additional centimes (CM CAC) and municipal
surcharges (LI, ME) `Multiplier`; no income tax (B15) `incomeTax := 0`, contributions only, with a `detail` note citing the law.

## 4d. Parts added in 1.4.0 (`TaxKernel.World2`; import it explicitly)

`import TaxKernel.World2` (imports `TaxKernel.World` and the whole kernel); models that import it call
**`TaxKernel.worldMain14`**. Neither the root module nor `TaxKernel.World` imports it, so every model built before is
unchanged by construction; all 49 kernel-built models (the 33 of the 38 and the 16 world models built by
2026-11-20 01:55 UTC) were rebuilt against 1.4.0 in a copy and gave byte-identical output on a 52-household grid
(`cmp20/world/kcheck/check_all.sh`, log `check_all.log`). Toy calls: `examples/World2.lean`; axioms:
`audit/AxiomsWorld2.lean` (no `sorry`). Asked for in `world/KERNEL_REQUESTS.md` (B02-g20).

| Part | Names | For (check your own statute) |
|---|---|---|
| Column tariff (band set chosen by the size of the whole income) | `pickColumn cols dflt x` (first column whose limit is ≥ `x`, else `dflt`), `columnTicks cols dflt x`, `columnJumps cols dflt` (the jump at each column limit beyond the marginal rate: computable, check with `#guard`) | EG Law 91/2005 art. 8 as replaced by Law 7/2024 (six columns by total net income); any tariff whose lower bands are withdrawn above an income limit. `pickColumn_succ`, `columnTicks_succ`: away from the limits the marginal rate is the chosen schedule's band rate, so **every notch sits at a column limit** |
| Amounts indexed by a published coefficient | `indexAmount m num den base` (base × num/den, rounded by `m`), `indexChain m [(num, den), …] base` (successive adjustments, rounded at each step), `Schedule.indexed s m num den` (thresholds indexed, rates kept), `indexReproduces m num den [(base, printed), …] tol` (one coefficient explains a published table) | AR Ley 27.743 arts. 30 and 94 (IPC coefficient, January and July); any CPI-uprating rule. `indexed_rates`, `indexAmount_mono` |

## 4e. Kernel 2.0 (`TaxKernel.Global`, 2.0.0, 2026-11-21): every tax, one master equation

Design, build contract and testing: `cmp20/global/DESIGN.md`; work packages: `cmp20/global/PLAN.md`. `import
TaxKernel.Global` (it imports `World2`, `World` and the whole 1.x kernel); nothing of 1.x imports it. Plain `lake build`
now also builds it (library `TaxKernelGlobal` in `lakefile.toml`; the kernel-built models were rebuilt against that
lakefile and gave byte-identical output: `global/kcheck/adapter.json`). Toy calls: `examples/Global.lean` (66
`#guard`s); axioms: `audit/AxiomsGlobal.lean` (61 theorems, no `sorry`).

| Module | Names | Theorems (examples) |
|---|---|---|
| `Types` | `CanonGlobal` (`household : Canon` verbatim + `incomes assets disposals transfers purchases consumption company`), `Oecd` (1100 … 6000), `Disposal`, `Transfer`, `Purchase`, `Spend`, `Supply`, `Payment`, `Company`, `parseGlobal`, `CanonGlobal.ofCanon` | `parseGlobal_legacy`, `ofCanon_household` |
| `Master` | `Charge`, `charge` (due = schedule(relief(base)) − credit), `flatCharge`, `Family`, `GlobalModel` (`pit route families absent unsupported`), `computeGlobal`, `ofCountry`, `ofLine`, `withFamily`, `OutGlobal` (`total totalOf borneBy notModelled net`), `stackedTax`, `addToRaw`, `jsonIncomeTax` | `charge_wf`, `total_eq_master`, `adapter_unchanged`, `ofLine_unchanged`, `conservative_pit`, `withFamily_charges`, `withFamily_total` |
| `Corporate` | `CorpRegime` (`citTax`, `taxableProfit`, `interestDisallowed`, `participationExempt`, `citCharge`), `lossOffset`, `topUp` | `lossOffset_le_income`, `citTax_ge_minimum`, `topUp_floor` |
| `Capital` | `FlatCapital`, `Imputation`, `GainRule`, `AnnualExempt`, `Wht`, `afterCredit` | `indexedGain_le`, `taxable_exempt_after`, `threshold_notch` |
| `Property` | `twoStage`, `PropertyTax`, `WealthTax` | `twoStage_mono`, `WealthTax.capped_le`, `WealthTax.capped_ge_floor` |
| `Transfers` | `slabTicks`, `slabRelieved`, `TaxClass`, `InheritanceTax`, `withLookback`, `estateCharge`, `TransferDuty` | `lookback_split`, `slabRelieved_le` |
| `Consumption` | `Vat` (`embedded basket outputTax inputTax proRataBp net`), `ExciseRate`, `Excise`, `employerCharges`, `PayrollTax` | `embedded_le`, `Vat.net_below_threshold`, `ExciseRate.duty_ge_min` |
| `Run` | `globalMain legacyMain model args` (`--global`: JSON `schema: global/2.0`; otherwise the 1.x main, unchanged) | `globalMain_legacy` |

Adapter for a 1.x model: `GlobalModel.ofCountry XxTax.country` when its `main` is `countryMain`/`worldMain`;
`GlobalModel.ofLine` with the exe's own line function otherwise (IT PT BG CY GR AU ES NL CZ PL SE and the five models
not built on the kernel). Scaffold: `python3 cmp20/global/harness/new_country.py <REGION> <CC> --build`.

**Fix in 2.2.0 (`Master`): a company-only entity bears no PIT charge.** A company line without `"household"` (`CanonGlobal.companyOnly`) used to book the 1.x line computed on the placeholder household (CH: a 24 CHF 1100 charge, the 1.x minimum tax). `computeGlobal` now books `pitChargesFor g pj` = none for such an entity, and its `benefits` are 0; the `pit` field still shows the 1.x line. Household entities and company lines that give a household are unchanged (`computeGlobal_household_charges`, `computeGlobal_household_benefits`, `ofCanon_charges`; `computeGlobal_companyOnly`). `adapter_charges` gained the hypothesis `g.companyOnly = false` (no builder used it). Families still run and see no PIT charges for a company-only entity. The exe's `kernel` string stays "TaxKernel 2.0.0" so that no other output changes.

### 4e.1 Kernel 2.1 (`TaxKernel.Global2`, 2.1.0, 2026-11-21): the parts asked for in `global/KERNEL_REQUESTS.md`

`import TaxKernel.Global2` (it imports all of `TaxKernel.Global`). **Nothing imports it**, and no 2.0 name, signature or
module changed: a project that does not import it builds and runs exactly as before (checked: every country project
under `cmp20/global` rebuilt against 2.1 with nothing recompiled and byte-identical output, and the adapter check on a
sample of the PIT models: `global/kcheck21/`). The new names live in `TaxKernel.Global` (`open TaxKernel.Global` as
before). Toy calls: `examples/Global2.lean` (83 `#guard`s); axioms: `audit/AxiomsGlobal2.lean` (27 theorems, no
`sorry`). Each part was checked against the region-side code it replaces (`global/kcheck21/mirror/global/diff/Diff.lean`):
identical on every case of `R4.Exc.duty` (43 200), `R4.exciseCharges`, `R4.corpTax`/`R4.citCharge` (960), FJ's
two-period VAT (30 entities), TM art. 119 (270), SA's taxable share (336).

**Per-line facts of the basket** (`Basket`): `Spend` is unchanged; extra facts are read from the line's JSON by
`consumptionX g : List (Spend × SpendX)` (same order as `g.consumption`, `consumptionX_fst`):

| JSON on a `consumption` line | `SpendX` | meaning |
|---|---|---|
| `"date": "YYYY-MM-DD"` (else the line's top-level `"date"`) | `date` | when bought; `""` = spread over the year |
| `"massG"` | `massG` (−1: none) | grams (thousandths of a kg) |
| `"platoBp"` | `platoBp` | degree Plato × 100 (12 °P = 1200) |
| `"sugarMg100ml"` | `sugarMg100ml` | mg of sugar per 100 ml (5 g = 5000) |
| `"sub"` | `sub` | sub-category: `"sweetenedDrinks"`, `"energyDrinks"`, … (`Good` is unchanged) |
| `"imported": true` (else the good is in the top-level `"importedGoods"`) | `imported` | origin |

Dates: `dayOfYear? year "YYYY-MM-DD"` (days of the year before the date; earlier year 0, later year the whole year),
`daysInYear`, `scaleDays a d n` (`a × d / n` down; `scaleDays_full`, `scaleDays_le`).

| Module | Names | Use |
|---|---|---|
| `DatedVat` | `VatPeriod` (`start`, a 2.0 `vat`, `statute`), `DatedVat` (`periods`, `undatedSupplies := .endOfYear \| .split`, `splitNote`, `endNote`), `basketCharges`, `businessCharges`, `charges`, `family`, `vatOn` | VAT rates changing during the year. A dated line goes to the period in force; an undated line is spread by days (`amount × days/365` per period; statute + `"; 212/365 of the basket"`). Supplies: the entity's `"date"`, else the last period (`.endOfYear`, statute + `" (no date given: the rate in force at the end of 2025)"`) or split by days. A single period is the 2.0 `Vat.basketCharge`. |
| `ExciseRule` | `ExciseRule` (all `ExciseRate` fields + `sub`, `perKgNum/perKgDen`, `mgPerUnit`, `perPlatoNum/perPlatoDen`, `sugarBands`, `valueBase := .retail \| .netOfVat \| .beforeTax`, `vatBp`, `roundOnce`, `minAbvBp/maxAbvBp`, `imported`, `validFrom/validTo`), `ofRate`, `withVat`, `dutyOn`, `duty`, `toCharge`; `exciseRuleCharges rules g (firstOnly := false)`, `exciseRuleFamily name rules` | Ad valorem on the value before excise and VAT (`b = (p/(1+v) − specific)/(1+a)`, duty `a·b`; `roundOnce` for `p·a/((1+a)(1+v))`); per kg / tonne (line `"massG"` or quantity × `mgPerUnit`); per hl and degree Plato; sugar bands; strength bands, origin, sub-category, date windows (an undated line gets the window's share of the year). `.retail` rules book `base = relieved = quantity` (2.0 `Excise.charges`); the others `base = amount`, `relieved = value taxed` (as `R4.exciseCharges`). `ofRate_dutyOn`: a 2.0 rate gives the same duty. |
| `TransferX` (2.1.1) | `TransferX` (`assetKind`, `realPropertyValue`, read from the transfer record's `"assetKind"`, `"realPropertyValue"`), `transfersX g`, `realPropertyPart t x`, `Transfer.restrict t v`, `PartDuty` (`rates` by relation, `gifts`, `inheritances`, `part`, `round`, `statute`), `charges`, `unknown`, `family` | A duty on one kind of property in a gift or inheritance (MA CGI art. 133-I-C-4°: 1,5 % on gifts of immovables in the direct line, between spouses and siblings). `realPropertyPart`: the given `realPropertyValue` (at most the statutory value), else the whole statutory value when `assetKind` is `home`/`realEstate`/`land`, 0 for another kind, `none` when neither is given (`PartDuty.unknown` lists those for `unsupported`; never assumed). `Transfer.restrict t v` feeds a part to the 2.0 `InheritanceTax`. `Transfer` is unchanged. |
| `CorpRule` | `MinimumTax` (`bp`, `onAssets`, `fixed`, `floor`, `cap`), `CorpRule` (`regime : CorpRegime`, `minTax : Option MinimumTax`, `step`, `shareKey`, `shareComplement`), `taxable`, `regular`, `minimum`, `tax`, `citCharge g statute`, `family c name statute wht extra`, `roundStep` | CIT = max (schedule(round_step(share × taxable profit)), minimum); minimum with floor and cap (OHADA); `step := 1000` (OHADA rounding); taxable ownership share from the line (`shareKey := "zakatShareBp", shareComplement := true` for SA; `"exemptShareBp"` for QA). `ofRegime_tax`: a bare regime is the 2.0 `citTax`. |

Switching over (same output, checked):

```lean
import TaxKernel.Global2
open TaxKernel TaxKernel.Global
-- R4.Exc e  ↦  { good, name, perUnitNum, perUnitDen, onPureAlcohol, minNum, minDen, minAbvBp, maxAbvBp, imported,
--               statute, adValoremBp := e.advBp, valueBase := .beforeTax, vatBp := e.vatBp } : ExciseRule
def beer : ExciseRule := { good := .beer, name := "Droit d'accises", adValoremBp := 5000, valueBase := .beforeTax,
  vatBp := 1800, imported := some true, statute := "CGI art. …" }
-- R4.exciseFamily n xs  ↦  exciseRuleFamily n rules        (TM: { … valueBase := .beforeTax, roundOnce := true }.withVat vat)
-- R4.corpFamily n r m st w extra step  ↦  ({ regime := r, minTax := some { bp, fixed, floor, cap, onAssets }, step } : CorpRule).family n st w extra
def fjVat : DatedVat := { periods := [{ vat := vat1, statute := s1 }, { start := "2025-08-01", vat := vat2, statute := s2 }] }
-- FJ families := [fjVat.family "VAT (two periods)"]
def diesel : ExciseRule := { good := .diesel, perKgNum := 9500, perKgDen := 1000, mgPerUnit := 840000 }  -- 9 500 per tonne, 0.84 kg/l
def atBeer : ExciseRule := { good := .beer, perPlatoNum := 2, perPlatoDen := 100 }    -- 2,00 per hl and °P; line "platoBp": 1200
def energy : ExciseRule := { good := .nonAlcoholic, sub := "energyDrinks", adValoremBp := 10000, valueBase := .beforeTax, vatBp := 1500 }
def sa (co : Company) : CorpRule := { regime := incomeTax co, shareKey := "zakatShareBp", shareComplement := true }
```

### 4e.2 Kernel 2.3.0 (`TaxKernel.Global`, 2026-11-21): unread withholding is grade C; small-company test on employees

Both requests of `global/KERNEL_REQUESTS.md` (R-FT2-1, R1 Europe pass 4) are in the 2.0 modules (`Master`, `Capital`,
`Corporate`), so they apply to every model with no country edit. Toy calls: `examples/Global2.lean` section "2.3.0"
(28 `#guard`s); axioms: `audit/AxiomsGlobal.lean` (23 new theorems, no `sorry`). Checked on every country project
(`global/kcheck23/compat23.json`, below).

**R-FT2-1: withholding no rule computes is reported, not booked as 0.** Before 2.3.0, `Wht.charges` booked a payment
abroad that no `WhtRule` matches as a charge of 0 with statute `"no withholding rule"`, and a model with no withholding
family booked nothing; the FT scorer read both as a computed 0 (heading 1200 is computed by the CIT). Now
`computeGlobal`, for a **company entity**:

* drops those placeholders (`Charge.unreadWht`: bearer `withheld`, statute `noWhtRule`, due 0), and
* adds to `unsupported`, after the model's own entries, one line per payment abroad that no other withheld charge
  computes: `"1200 withholding on payment <i> (<kind>) abroad: no rule read (grade C)"` (`1100 …` when the recipient
  is an individual, the heading its charge would have). `tests/tools/ft_common.ft_charge` already reads this form as
  **"not reached (grade C)"**: no scorer change.

A payment counts as computed when a withheld charge other than a placeholder has its event `payment <i> (<kind>)`, or
when the withheld charges carry as many distinct events of its kind as there are payments of that kind (a model that
passes a filtered list to `Wht.charges`, as CL does, renumbers the events). Model-side nothing changes: rules that match
still book their charges; `Wht.charges` is now `zipIdx.map (w.chargeOf p i)` (same charges).

**A statutory zero stays expressible, as a cited rule.** A model that has read the statute and found no withholding on
a kind writes a 0 % rule with its citation; it books a covered 0 (`Wht.chargeOf_rule_kept`):

```lean
def wht : Wht := { name := "Withholding tax",
  rules := [{ kind := .dividend, rateBp := 1000, statute := "ITA s. 12" },
            WhtRule.zero .interest "ITA s. 13 (2): interest paid abroad exempt",           -- = { kind, rateBp := 0, statute }
            WhtRule.zero .dividend "ITA s. 12 (4): to individuals none" (toCompany := some false)] }
-- no withholding at all in the statute (a model with no withholding family so far):
def noWht : Wht := { name := "Withholding tax", rules := Wht.zeroOn [.dividend, .interest, .royalty, .services] "ITA: no WHT on non-residents" }
-- families := [..., noWht.family]       -- `Wht.family w (covers := [.cit])`: runs on company entities only
```

The rule's statute must not be the placeholder text `noWhtRule`. A stake condition that is not met (`minStakeBp`) is a
payment no rule matches: add a second rule without the condition if the statute taxes (or exempts) the rest.

| Name (2.3.0) | What |
|---|---|
| `noWhtRule`, `Charge.unreadWht` | the placeholder statute; the placeholder test |
| `WhtRead.event i p`, `events`, `kindEvents`, `computed`, `unreadPayments co cs`, `line p i` | which payments no charge computes, and their `unsupported` line |
| `WhtRead.kept g cs`, `WhtRead.unread g cs` | what `computeGlobal` books / adds (identity / `[]` for a household entity) |
| `GlobalModel.rawCharges m args g` | the charges before that step (the 2.2.0 `charges`) |
| `Wht.chargeOf w p i`, `WhtRule.zero`, `Wht.zeroOn`, `Wht.family` | one payment's charge; cited zeros; withholding as a family |

Theorems: `WhtRead.kept_total` and `computeGlobal_total` (**no total changes**: every dropped charge is 0),
`WhtRead.kept_household`, `WhtRead.unread_household`, `computeGlobal_household_unsupported` (household entities
untouched), `WhtRead.unread_noPayments` (no payment abroad: no line added), `WhtRead.mem_kept` (only placeholders are
dropped), `WhtRead.unread_sound` (a payment is listed only when no non-placeholder withheld charge has its event),
`Wht.chargeOf_unread` (no matching rule: a placeholder), `Wht.chargeOf_rule_kept` (a matching rule, 0 % included: kept),
`legacyCharges_unreadWht`. Statements narrowed: `computeGlobal_household_charges` and `withFamily_charges` now assume a
household entity (`(g.entity == .company) = false`; for a company line the same holds for `rawCharges`:
`withFamily_rawCharges`, `computeGlobal_withHousehold_charges`), `computeGlobal_companyOnly` reads
`WhtRead.kept g (runFamilies …)`, `withFamily_total` runs the new family on `rawCharges`. No builder used them in a proof.

**R1 Europe pass 4: small-company CIT test on employees as well as turnover.** `CorpRegime` has a new last field
`smallEmployees : Int := -1`; the small schedule applies when every limit that is set is met:

    isSmall = (smallTurnover ≥ 0 ∨ smallEmployees ≥ 0) ∧ (smallTurnover < 0 ∨ turnover ≤ smallTurnover)
                                                     ∧ (smallEmployees < 0 ∨ employees ≤ smallEmployees)

`employees` is the company line's `"employees"` (`Company.employees`). With the default −1 the test is the 2.2 turnover
test (`CorpRegime.isSmall_turnoverOnly`); with `smallTurnover := -1` the employee limit alone decides. `CorpRule` (2.1)
and R4's `corpTax` use `isSmall`, so they follow. Theorems `isSmall_employees`, `isSmall_turnover`.

```lean
-- LT Pelno mokesčio įstatymas 5 str. 2 d. (2025): 6 % where average employees ≤ 10 and revenue ≤ 300 000 €
def ltCit : CorpRegime := { name := "Pelno mokestis", sched := Schedule.flat 1600, smallSched := Schedule.flat 600,
                            smallTurnover := 300000, smallEmployees := 10 }
```

**Equivalence (2.2.0 -> 2.3.0, `global/kcheck23/compat23.py`):** all 201 country projects under `global/` (R4 48, R5 24, americas 35, asiapac 47, europe 45, pilots 2) built on both kernels (0 build failures) and ran on the same inputs: **53,400 output lines**. The 1.x adapter grid (legacy mode, 56 households) is **byte-identical in all 201** (11,256 lines), and the `pit` field is identical on all 42,144 global lines (1.x PIT output unchanged everywhere; the 1.x kernel sources are untouched). The same 56 households as global lines: identical (11,256). **1,897 lines changed, every one a company entity and exactly as predicted by an independent Python re-implementation of the rule** (no other field changed: total, borne, net, covered, notLevied, notModelled and every other charge as before): 4,062 placeholders dropped, 9,368 grade-C lines added (4,022 where a placeholder was, 5,346 where no withheld charge existed). By input: compat21's company lines with 8 payments abroad 1,540 of 3,819; the projects' own `results/cases.jsonl` 72 of 525; `ftd_oecd_wht_rates_2025` entities 285 of 532 (137 no rule for the kind, 148 no withholding at all); the other FT datasets (OECD CIT 133, TEDB VAT 167, oil bulletin 84, OECD employer 120, worked examples 5) and the dev cases of every company FT grid (`*_ft_cit_*`, `*_ft_wht_*`: 25,503) unchanged. No model sets `smallEmployees` yet, so the employee test changes nothing (covered by the same check). Models with unread withholding, by region: `global/kcheck23/flagged23.json`. Re-run after the release on the live kernel with the builders' current sources (`postswap23.json`): 201/201 built, 0 unexpected differences, 1,893 company lines changed as specified.

### 4e.3 Kernel 2.4.0 (`TaxKernel.Global2`, 2026-11-21): vehicles, price tiers, floor area, recipient state

Four requests of `global/KERNEL_REQUESTS.md` (R1 Europe pass 7 vehicles, R3-S4-1 price tiers, R1 Europe pass 8
recipient state, and the floor-area field of R5/Asia-Pacific). **Everything is additive and optional**: new modules
`Global2.Assets`, `Global2.Vehicle`, `Global2.WhtState` (imported by `TaxKernel.Global2`), and five new last fields on
`ExciseRule` whose defaults select exactly as before (`appliesTo_noTier`). Nothing in `TaxKernel.Global` (2.0-2.3)
changed: `Asset`, `Payment`, `Company`, `CanonGlobal`, `Wht` and `computeGlobal` are as they were, so an entity or a model
that does not use the new parts gives byte-identical output (checked on all 201 projects, below). `import
TaxKernel.Global2`; names in `TaxKernel.Global`. Toy calls: `examples/Global2.lean` sections "2.4.0" (79 `#guard`s);
axioms: `audit/AxiomsGlobal2.lean` (31 new theorems, no `sorry`).

**Input fields (canonical names).** All optional; read from the input line (`g.raw`), like the 2.1 basket extras.

| Where | JSON field | Lean | Meaning |
|---|---|---|---|
| `assets[i]` | `"areaM2"` | `assetAreaM2 g i` (0: not given), `assetsArea g` | **floor area** of a `home`/`realEstate`, plot area of `land`, m² (the name R5 AZ/GE/DZ use: `assetAreaM2_eq` is their expression) |
| `assets[i]` of `"kind": "vehicle"` | `"vehicleKind"`, `"engineCcm"` (or `"engineCc"`), `"engineKw"`, `"fiscalHp"`, `"co2GKm"`, `"massKg"`, `"fuel"`, `"firstRegYear"`, `"seats"`, `"months"`, `"registeredThisYear"` (value, person, region: the asset's) | `g.vehicles : List Vehicle` | a vehicle of the entity |
| `company.vehicles[k]` (company entities) | the same (`"kind"` accepted for `"vehicleKind"`), `"value"` | `g.vehicles` | a company's fleet (the form R4 already reads for `fiscalHp`) |
| `company.paymentsAbroad[i]` | `"recipientState"` (ISO 3166 alpha-2), `"lowTax"`, `"nonCooperative"`, `"euEea"`, `"treaty"` (true/false) | `paymentXOf g i`, `paymentsX g` | the recipient's state and its status; absent = not given |

`fuel`: `petrol diesel electric hybrid pluginHybrid lpg cng hydrogen other` (absent: `unknown`); numbers absent: −1
(`firstRegYear` 0); `vehicleKind` default `"car"`; `months` default 12; `registeredThisYear` default
`firstRegYear = year`. A 1.x household has no vehicle (`vehicles_ofCanon`).

**Rate tables on a quantity** (`QtyTable`, `Assets`): `amount q = band(counted q) + ⌊Σ num_k × units in (from_k,
from_{k+1}] / den⌋`; `step` counts in started steps ("je angefangene 100 cm³"), `bands` `(from, amount)` a fixed sum
for the highest band reached, `steps` `(from, num)` marginal money per unit (`den` shared, rounded once).
`QtyTable.ofCeilings [(c, a), …] top` writes "up to c: a" tables (R4 `VehTariff`: identical for every CV, checked),
`QtyTable.perUnit num den` a flat rate per unit. Theorems `marginal_mono` (non-negative rates: never falls as the
quantity rises), `amount_flat`.

**A tax per m²** (`AreaTax`: `name`, `kinds`, `table`, `tableFor : Asset → Option QtyTable` by kind or region,
`oecd := .propertyRecurrent`, `level := .local`, `event`, `statute`; `charges g`, `unknown g` (grade-C lines for assets
of `kinds` without an area), `family`). R5 GE's land tax as an `AreaTax` gives the same charges as `GeGlobal.landCharges`
(checked); AZ's two-step land tax and DZ's per-m² rates are `QtyTable`s (checked on ranges). R5 may keep its code or
replace `areaOf`/`landAreaOf`/`tfArea` by `assetAreaM2` (same value, by `rfl`).

```lean
def geLand : AreaTax := { name := "land tax", kinds := [.land], table := QtyTable.perUnit 36 100, event := "land",
  statute := "Tax Code art. 203, 204(2)" }                    -- GEL 0.36 per m²
def azLand : QtyTable := { steps := [(0, r1), (10000, r2)], den := 10000 }   -- per 100 m² to 1 ha, and above
def azHome : QtyTable := { steps := [(30, rate)], den := 100 }               -- per m² above 30 m²
```

**Motor-vehicle taxes** (`Vehicle`, OECD 5200 by default). `VehicleTax`: selection `kinds`, `fuels`, `regFrom/regTo`
(first registration), `region`, `when := [(attr, lo, hi)]` (lo < x ≤ hi), `occasion := .annual | .registration` (the
latter only for a vehicle registered in the tax year); amount `fixed + Σ parts` (one `QtyTable` per attribute:
`.engineCcm .engineKw .fiscalHp .co2GKm .massKg .seats .value .age .firstRegYear`), × the age factor reached
(`ageFactors := [(from age, bp)]`), × `multiplierBp`, rounded by `round`, within `[minAmount, maxAmount]`, × months/12
for an annual tax held part of the year (`proRata`). `vehicleTaxCharges ts g (firstOnly)` one charge per (vehicle, tax
that computes it): base = the first part's attribute, relieved = it counted, event `"vehicle <k> (<source>)"`;
`vehicleTaxFamily name ts`; **an attribute a selected tax needs but the vehicle does not give: no charge, and
`vehicleTaxUnknown name ts g` lists `"5200 <name>: vehicle <k> (…): co2GKm not given (grade C)"`**;
`vehicleTaxUnmatched` lists vehicles no tax selects (write a cited zero rule for an exemption, e.g. electric cars).
Entities without vehicles: no charge, so adding the family changes no charge or total of theirs
(`withVehicleFamily_charges`, `withVehicleFamily_total`); the model's `covered` list gains 5200.

```lean
-- DE KraftStG § 9 (1) Nr. 2 c: per started 100 cm³ 2,00 € (petrol), + per g CO2/km above 95: 2,00 … 4,00 €
def deCo2 : QtyTable := { steps := [(95, 200), (115, 220), (135, 250), (155, 290), (175, 340), (195, 400)], den := 100 }
def dePetrol : VehicleTax := { name := "Kraftfahrzeugsteuer", kinds := ["car"], fuels := [.petrol],
  parts := [(.engineCcm, { step := 100, steps := [(0, 2)], den := 100 }), (.co2GKm, deCo2)], statute := "KraftStG § 9 (1) Nr. 2 c" }
def deElectric : VehicleTax := { name := "Kraftfahrzeugsteuer", kinds := ["car"], fuels := [.electric], statute := "KraftStG § 3d" }
-- CO2 bands ("up to 50 g: 120 …"), a kW table with age factors and a local multiplier, a registration tax on value:
def ie : VehicleTax := { name := "motor tax", parts := [(.co2GKm, QtyTable.ofCeilings [(50, 120), (80, 140)] 1200)] }
def hr : VehicleTax := { name := "…", parts := [(.engineKw, QtyTable.ofCeilings [(55, 300), (75, 500)] 900)],
  ageFactors := [(0, 10000), (5, 8000), (10, 6000)], multiplierBp := 15000, level := .local }
def reg : VehicleTax := { name := "registration tax", occasion := .registration, parts := [(.value, QtyTable.perUnit 1000 10000)] }
-- families := [..., vehicleTaxFamily "Kraftfahrzeugsteuer" [dePetrol, deDiesel, deElectric]]
-- unsupported := fun _ g => … ++ vehicleTaxUnknown "Kraftfahrzeugsteuer" ts g
```

**Excise by the retail unit price** (R3-S4-1, `ExciseRule`): `minUnitPrice < price ≤ maxUnitPrice` (−1: no bound),
the price of `priceQty` thousandths of the canonical unit (a pack of 20 sticks: `20000`) in money / `priceDen`
(piastres: 100), on `priceBase` (`.retail` default, or `.netOfVat`, `.beforeTax`). Compared exactly (`priceIn_iff`:
`min·q < amount·priceQty·priceDen ≤ max·q`; a pack at 800.50 is above 800); a line without quantity is in no tier;
adjacent tiers never overlap (`priceIn_adjacent`); a rule without a tier is unchanged (`appliesTo_noTier`).
`ExciseRule.unitPrice` gives the rounded price for notes. EG's hand-written cigarette table tax (`EgGlobal.cigTax`,
2025 table) is reproduced by five rules on 8,000 lines (checked).

```lean
-- MM Union Taxation Law 2025 s. 11: 14 / 27 / 30 kyats a stick for a pack of 20 sold up to 800, 801-1,100, above
def mm1 : ExciseRule := { good := .cigarettes, perUnitNum := 14, priceQty := 20000, maxUnitPrice := 800 }
def mm2 : ExciseRule := { mm1 with perUnitNum := 27, minUnitPrice := 800, maxUnitPrice := 1100 }
def mm3 : ExciseRule := { mm1 with perUnitNum := 30, minUnitPrice := 1100, maxUnitPrice := -1 }
def mmTop : ExciseRule := { good := .spirits, adValoremBp := 6000, minUnitPrice := 28600 }   -- per litre (priceQty 1000)
-- EG: 500 pt a pack, local, pack ≤ EGP 48: { good := .cigarettes, perUnitNum := 500, perUnitDen := 2000,
--      priceQty := 20000, priceDen := 100, maxUnitPrice := 4800, imported := some false }
```

**Withholding by the recipient's state** (R1 Europe pass 8, `WhtState`). `StateRule := { rule : WhtRule, tests,
ifUnknown }`: `tests` all hold (`.inStates codes`, `.notInStates codes` on `recipientState`; `.lowTax b`,
`.nonCooperative b`, `.euEea b`, `.treaty b` on the flags). **`ifUnknown` has no default: each conditional rule says
what an absent fact means**: `.general` (not applied; the next matching rule, normally the general rate, is booked, and
`StateWht.notes` adds `"1200 withholding on payment <i> (<kind>): conditional rate … not tested: euEea not given; 2400
bp booked (…)"`), `.presume` (applied as the statute presumes; the charge's statute ends with `presumedNote`), `.gradeC`
(no rate: the 2.0 placeholder, which `computeGlobal` drops and lists as grade C, plus a note naming the missing fact).
A payment without facts never gets a conditional rate silently (`whtPick_noFacts`, `StateRule.check_noFacts`).
`StateWht` (`name`, `rules`, `round`) charges exactly like the 2.0 `Wht` (heading by recipient type, event `payment <i>
(<kind>)`, bearer withheld, so the 2.3.0 grade-C reading applies); `StateWht.ofWht w` (plain rules) books the same charges
as `w` whatever the facts (`ofWht_charges`): switching changes no output until a conditional rule is added.
`StateWht.family`, `StateWht.notes g` (for `unsupported`).

```lean
def es : StateWht := { name := "IRNR", rules := [
  { rule := { kind := .interest, rateBp := 1900, statute := "TRLIRNR art. 25.1 a) (EU/EEA)" }, tests := [.euEea true], ifUnknown := .general },
  StateRule.plain { kind := .interest, rateBp := 2400, statute := "TRLIRNR art. 25.1 a)" }] }
def cz : StateWht := { name := "srážková daň", rules := [
  { rule := { kind := .dividend, rateBp := 3500, statute := "ZDP § 36 (1) c)" }, tests := [.treaty false], ifUnknown := .presume },
  StateRule.plain { kind := .dividend, rateBp := 1500, statute := "ZDP § 36 (2) a)" }] }
def fr : StateWht := { name := "retenue à la source", rules := [
  { rule := { kind := .royalty, rateBp := 7500, statute := "CGI 182 B III" }, tests := [.inStates etnc], ifUnknown := .gradeC },
  StateRule.plain { kind := .royalty, rateBp := 2500, statute := "CGI 182 B I" }] }
-- NL/NO related low-tax: { rule := { kind := .interest, rateBp := 2580, minStakeBp := 5000, statute := "…" }, tests := [.lowTax true], ifUnknown := .general }
-- families := [..., es.family]; unsupported := fun _ g => … ++ es.notes g
```

Names (2.4.0): `assetJson assetAreaM2 assetsArea AssetKind.name QtyTable (counted band slice marginalNum marginal amount
ofCeilings perUnit) AreaTax (tableOf charges unknown family)`; `VehicleFuel VehicleAttr Vehicle (ofJson attr?)
CanonGlobal.vehicles VehicleOccasion VehicleTax (needs missing selects computes basic ageBp yearAmount amount toCharge)
vehicleTaxCharges vehicleTaxFamily vehicleTaxUnknown vehicleTaxUnmatched`; `ExciseRule.(minUnitPrice maxUnitPrice
priceQty priceDen priceBase selects priceMoney priceTimesQty hasPriceTier priceIn unitPrice)`; `PaymentX paymentXOf
paymentsX optBoolField StateTest StateUnknown StateRule (plain check missing) WhtPick whtPick presumedNote StateWht (ofWht
chargeOf charges notes family)`. Theorems: `assetAreaM2_eq assetsArea_fst AssetKind.ofString_name QtyTable.(slice_mono
slice_nonneg marginalNum_nonneg marginalNum_mono marginal_mono amount_flat) AreaTax.charges_noArea vehicles_ofCanon
VehicleTax.(yearAmount_le_max yearAmount_ge_min amount_full amount_le_year) vehicleTaxCharges_nil
withVehicleFamily_charges withVehicleFamily_total ExciseRule.(appliesTo_noTier priceIn_noTier hasPriceTier_default
priceIn_adjacent priceIn_iff) paymentsX_fst StateRule.check_plain whtPick_ofWht StateWht.ofWht_chargeOf
StateWht.ofWht_charges StateTest.eval_noFacts StateRule.check_noFacts whtPick_noFacts`.

**Equivalence (2.3.0 -> 2.4.0, `global/kcheck24/compat24.py`):** all 201 country projects under `global/` (R4 48, R5 24, americas 35, asiapac 47, europe 45, pilots 2) built on both kernels (0 build failures) and ran on the same inputs: **55,045 output lines, 0 changed** (byte for byte). The 1.x adapter grid (legacy mode, 56 households) is byte-identical in all 201 (11,256 lines): PIT unchanged everywhere, and every one of the 43,789 global lines, `pit` included, is identical. By input: the global grid 11,256, compat21's household/company lines 3,819, a new set of lines that use the 2.4.0 fields (vehicles on assets and in `company.vehicles`, `areaM2`, priced cigarettes and spirits, payments with recipient facts: 1,608), the projects' own `results/cases.jsonl` 553, the FT dataset entities 1,050 and the dev cases of every company FT grid 25,503: all identical. 67 projects import `TaxKernel.Global2` (they recompile against 2.4.0; no build needed a source change). Re-run after the release (15:04 UTC) on the live kernel with the builders' current sources (`postswap24.json`, old = `kcheck24/kernel_prev_23`): 201/201 built and identical, 55,047 lines, 0 changed. Re-run: `python3 global/kcheck24/compat24.py --jobs 8 [--only R4/sn,…] [--old DIR] [--new DIR] [--out NAME]`.

### 4e.4 Kernel 2.5.0 (`TaxKernel.Global2`, 2026-11-21): income stacked on the PIT, vehicle Euro class and list price, open bounds, company sector

Four requests of `global/KERNEL_REQUESTS.md` (R4-13-1 stacking, R1 Europe pass 9 vehicle attributes, MENA pass 3k open
bound, R2-P9-1 company sector). **Everything is additive and opt-in**: new modules `Global2.Stack` and `Global2.Sector`
(imported by `TaxKernel.Global2`), three new `Vehicle` fields and attributes, and an open-bound reading of `when` that no
table used. Nothing in `TaxKernel.Global` (2.0-2.3) changed. Toy calls: `examples/Global2.lean` sections "2.5.0" (74
`#guard`s); axioms: `audit/AxiomsGlobal2.lean` (34 new theorems, no `sorry`).

**Income stacked on the 1.x income tax** (R4-13-1, `Stack`). For a gain (or dividends, interest) that the statute adds,
in part, to taxable income so that it bears the PIT at the marginal rate (ZA Eighth Schedule, CZ § 10, SK, LU, CA …):

    charge(rule k) = PIT(1.x household + included amounts of rules 1 … k) − PIT(1.x household + rules 1 … k−1)

PIT = the 1.x line's income tax (`jsonIncomeTax`: incomeTax + surtaxes + localIncomeTax), computed by the model's own
`pit` on its own `route g` with the amount added. The 1.x line itself is never touched (`withStack_pit`, `rfl`): the
stacked tax is a charge of its own under 1100 (tax = the rule's `name`, statute = its `statute`, base = the net before
exclusion and inclusion, relieved = the included amount, event = the items, "disposal 1 (listedShares), …"); when the
1.x local income tax moves, that part is a second charge at level `.local` (`"<name> (local income tax)"`).

| `StackRule` field | Meaning |
|---|---|
| `name`, `statute` | the charge's tax name; the inclusion/exclusion provisions (the rates are the 1.x model's) |
| `gainKinds : List AssetKind` | disposals of these kinds feed the amount (`AssetKind.every`: all) |
| `gainRule : GainRule` | each disposal's gain (2.0: exempt after `exemptAfterMonths`, main home with `mainHomeCap`, `minStakeBp`, indexation by the disposal's `indexBp`, inclusion by holding period) |
| `incomeKinds : List IncomeKind`, `foreign : Option Bool` | `incomes` items of these kinds (foreign only / domestic only / both) |
| `exclusion : AnnualExempt` | the annual exclusion on the net (allowance; `threshold := true` for a Freigrenze) |
| `pool := .person \| .household` | each natural person's own exclusion (default; ZA para 5) or one for the household |
| `inclusionBp` (10000), `exclusionAfterInclusion` (false) | included share of the net after the exclusion (ZA 4000), rounded down; or inclusion first |
| **`into : StackField`** (no default) | the 1.x field the amount enters: household `interest dividends capitalGains rentalIncome`, or the item's person's `wages selfEmployment pension` (then always per person) |
| `event` (`""`) | the charge's event (`""`: the items) |

Losses offset gains and income of the same rule and year; a net loss gives 0 (no carry-forward). Write one rule per
regime; several rules stack in the order given. **Choose `into` as a field your 1.x model taxes in full at the scale**
(ZA: `selfEmployment`, which `ZaTax.personTI` adds in full; a 1.x model that already applies the statute's inclusion and
exclusion to `capitalGains`, as UK's does, takes the gross gain there with `inclusionBp := 10000` and no exclusion), and
check it with a `#guard` on your model: a field the 1.x model ignores gives a correct-looking 0, and a field with earned-
income credits (US EITC on self-employment) can give a negative slice (the probe below found that). The amount is added
to the `Canon` structure **and** to the household's input line (`raw`; exact JSON-number addition, `jsonNumAdd_int`), so
models wrapped by `ofCountry` and the exe-level models wrapped by `ofLine` (which re-read the line) price the same
household.

```lean
import TaxKernel.Global2
open TaxKernel TaxKernel.Global
-- ZA: 40 % of the net gain after the R40 000 annual exclusion, per person, in taxable income (s. 26A, Eighth Schedule)
def zaCgt : StackRule :=
  { name := "Capital gains tax (taxable capital gain in taxable income)",
    statute := "Income Tax Act 58 of 1962 s. 26A; Eighth Schedule para 5 (1), 10 (a), 45 (1); rates: s. 5 (1.x model)",
    gainKinds := [.home, .realEstate, .land, .listedShares, .unlistedShares, .bonds, .business, .other],
    gainRule := { mainHomeExempt := true, mainHomeCap := 2000000 },
    exclusion := { amount := 40000 }, inclusionBp := 4000, into := .selfEmployment }
def model : GlobalModel := ({ (GlobalModel.ofCountry ZaTax.country) with families := [...], unsupported }).withStack [zaCgt]
-- R40 000 exclusion, 40 %: a R240 000 gain on wages of R600 000 → 80 000 included → 29 010 (36 %/39 % bands)
-- CZ-shaped (§ 10, 15 %/23 %): rules for securities (`exemptAfterMonths := 37`) and real estate (121), `into` the field
-- your 1.x line taxes at the scale; an `ofLine` (exe-level) model gives the same charges as `ofCountry` (checked)
```

`GlobalModel.withStack m rules (name)` adds the family **last** and appends `stackUnknown` to `unsupported`; call it on
the final model (it captures `m.pit` and `m.route`). Lower level: `stackCharges pit route rules args g`,
`stackUnknown …`, `stackRuleFamily …`, `stackSlices`, `StackRule.items/amounts/included`, `StackField.addTo/addAll`.
**Never guessed** (no charge for the rule, `"1100 <name>: … (grade C)"` in `unsupported`): an item of a person who is
not an adult of the household (per-person rules); a 1.x line with an `"error"`; a household whose input line cannot
carry the amount while the 1.x line does not move (a Lean-built household without `raw` under an `ofLine` model); and
every later rule (it would be stacked on a slice that was not priced). Company entities: nothing. An entity without
items: no extra 1.x call and the very same output (`withStack_noItems`, `withStack_ofCanon`).

Theorems: `StackSlice.charges_sum` (a priced rule's charges = PIT with − PIT without), `stackSlices_shape`,
**`stackCharges_nonneg`** (the stacked charges are ≥ 0 under `StackMono pit f`: *the 1.x income tax does not fall when
field `f` rises*, the stated assumption, with inclusion rates ≥ 0), **`stackCharges_zero`** (included amount 0: every
stacked charge is 0), `stackCharges_noItems`, **`withStack_pit`** (the 1.x line unchanged), `withStack_rawCharges`
(earlier charges unchanged, stacked ones appended), `withStack_noItems`, `withStack_ofCanon`, `jsonNumAdd_int`,
`StackField.addTo_zero`, `addAll_zero`, `addAll_length`, `StackRule.included_nonneg`, `amounts_nonneg`,
`AnnualExempt.apply_nonneg`, `StackMono.addAll`.

**Exe-level models** (`ofLine`: IT PT BG CY GR AU ES NL CZ PL SE, US FR UK DE JP and the DE pilot): supported through the
adapter, because the amount is written into the input line they re-read (exactly, decimals kept). Checked by the probe
of `global/kcheck25/compat25.py` on every project (below): the kernel's stacked charge equals the builders' hand form
`stackedTax (pitOf args) household { rentalIncome := gain }` and is priced (no grade C) on all of them. Where a line
cannot be priced the rule is reported grade C, never estimated.

**Vehicle emission class and list price** (R1 Europe pass 9, `Vehicle`). New optional fields on the vehicle record:
`"euroClass"` (a number 0-7 or a text: `"Euro 6d-TEMP"`, `"6d"`, `"EURO 5b"`; case, spaces, `-`, `_` and "euro" ignored)
and `"listPrice"` (price when new). Attributes: `.euroClass` (the class 0-7: 6 for every Euro 6, for IT bollo / DE § 9 (1)
Nr. 2 a by class), `.euroStage` (the sub-class in order, `euroStageOf`: 6b 62, 6c 63, 6d-TEMP 64, 6d 65, 6d-ISC-FCM 66, 6e
67, 6e-bis 68, 6e-bis-FCM 69; 5a 51, 5b 52; classes 0-4 and 7 = 10 × class; a Euro 5 or 6 given without its letter has
**no stage**), `.listPrice`. As every attribute, a tax that reads one the vehicle does not give books nothing and
`vehicleTaxUnknown` lists `"…: euroStage not given (grade C)"`: a plain "Euro 6" never passes or fails a 6d test, and
`value` is never read as the list price. Taxes that read none of them are unchanged (`Vehicle.attr?_old`).

```lean
-- UK VERA Sch. 1 para 1GC (3)-(5) shape: diesel cars meeting Euro 6d one rate, others Table 2
def meets : VehicleTax := { …, «when» := [(.euroStage, euroStageOf "6d-TEMP", VehicleTax.noBound)] }   -- 6d or later
def other : VehicleTax := { …, «when» := [(.euroStage, -1, euroStageOf "6d-TEMP")] }                   -- up to 6d-TEMP
def dear : VehicleTax := { …, «when» := [(.listPrice, 40000, VehicleTax.noBound)] }                  -- para 1GE
def bollo : VehicleTax := { …, parts := [(.euroClass, QtyTable.ofCeilings [(3, a3), (5, a5)] a6)] }   -- by class
```

**Open upper bound in `VehicleTax.when`** (MENA pass 3k): `(attr, lo, hi)` selects `lo < x ≤ hi`; from 2.5.0 **`hi < 0`
means no upper bound** (`VehicleTax.noBound` = −1), the convention of `ExciseRule.maxUnitPrice`; `lo = −1` was already
open below (a given attribute is ≥ 0). A non-negative `hi` reads exactly as before (`VehicleTax.inRange_bounded`), so the
large numbers builders wrote (R5 TR `1000000000000`) select as before; no table used a negative `hi` (checked: all
projects identical). `VehicleTax.inRange lo hi x`, `inRange_open`.

**Company sector** (R2-P9-1, `Sector`). Canonical optional input **`company.sector`**: a string, or an array of strings
for a company in several sectors. Agreed names (`Sector.canonical`, `Sector.isCanonical`): `general`,
`commercialTrading` (trading in goods it did not manufacture, commission agency), `manufacturing`, `telecom`, `bank`,
`insurer`, `petroleum`, `mining`, `agriculture`, `tourism`, `shipping`, `utilities`; another string is read as given.
`companySectors g` (`none`: not given). CIT by sector: `SectorCorp := { general : CorpRule, statute, bySector :
List SectorRule, ifAbsent }` with `SectorRule := { sectors, rule : CorpRule, statute }`: the first rule whose sectors
meet the company's applies, a given sector in none of them is under the general rule ("any other company"). **`ifAbsent`
has no default: the model declares what an absent sector means**: `.general` (the general rule; the charge's statute
ends with `absentSectorNote`, and `SectorCorp.notes` gives a notes line), or `.gradeC` (no CIT charge;
`SectorCorp.unknown` gives the `unsupported` line). `citCharges g`, `family name wht extra` (as `CorpRule.family`).
Without `bySector` the sector is never read: exactly the `CorpRule`'s charge (`SectorCorp.ofRule_citCharges`).
Theorems `pick_given`, `pick_absent_general`, `pick_absent_gradeC`, `pick_noSilent`.

```lean
-- GY Corporation Tax Act s. 10: telephone company 45 %, commercial company 40 % (minimum 2 % of turnover), others 25 %
def gy : SectorCorp :=
  { general := { regime := { name := "Corporation tax", sched := Schedule.flat 2500 } }, statute := "s. 10 (25 %)",
    ifAbsent := .general,
    bySector := [
      { sectors := ["telecom"], rule := { regime := { name := "Corporation tax", sched := Schedule.flat 4500 } }, statute := "s. 10 (45 %)" },
      { sectors := ["commercialTrading", "bank", "insurer"],
        rule := { regime := { name := "Corporation tax", sched := Schedule.flat 4000 }, minTax := some { bp := 200 } },
        statute := "s. 10 (40 %; minimum 2 % of turnover)" }] }
-- families := [..., gy.family "Corporation tax" wht]; notes/unsupported: gy.notes "Corporation tax" g, gy.unknown "…" g
```

**Equivalence (2.4.0 -> 2.5.0, `global/kcheck25/compat25.py`):** all 201 country projects under `global/` built on both kernels (0 build failures) and ran on the same inputs: **61,014 output lines, 0 changed** (byte for byte). The 1.x adapter grid (legacy mode, 56 households) is byte-identical in all 201 (11,256 lines): PIT unchanged everywhere, and every one of the 49,758 global lines, `pit` included, is identical. By input: the global grid 11,256, compat21's household/company lines 3,819, compat24's vehicle lines 1,608, a new set that uses what 2.5.0 reads (households with disposals and income items, couples, a second person's gains, main homes, holding periods, foreign dividends, amounts with decimals; vehicles with `euroClass`/`listPrice`; companies with `company.sector` as a string, an array and absent: 5,829), the projects' own `results/cases.jsonl` 589, FT dataset entities 1,154 and the dev cases of every company FT grid 25,503: all identical. 79 projects import `TaxKernel.Global2` (they recompile; no build needed a source change). **Stacking probe on every project** (the project's own `model` with `withStack`, 9 households each: 1,809 lines): 201/201 priced (no grade C, 1.x `pit` unchanged), and the kernel's charge with the gain in `rentalIncome` equals the builders' hand form `stackedTax … { rentalIncome := gain }` everywhere, the 17 exe-level `ofLine` projects included (US AU JP BG CZ DE ES FR GR IT NL PL PT SE UK CY, DE pilot); on lines whose input carries decimals DE and UK differ from the hand form by one unit, because `addToRaw` rewrites `250.5` as `251` while the kernel adds exactly. In 141 projects the stacked amount moves the 1.x tax; in 60 neither `rentalIncome` nor `selfEmployment` does (no PIT, or the 1.x model does not tax those fields: pick another field or keep the gain grade C). A falling slice (`StackMono` fails: credits that grow with earned income) appeared with `selfEmployment` in CA, US, PT (small, low incomes) and KR (large: check the KR 1.x model). Re-run after the release (15:59 UTC) on the live kernel with the builders' current sources (`postswap25.json`, old = `kcheck25/kernel_prev_24`): 201/201 built and identical, 61,018 lines, 0 changed; probe 201/201 priced. Re-run: `python3 global/kcheck25/compat25.py --jobs 8 [--only R4/za,…] [--old DIR] [--new DIR] [--out NAME] [--no-probe]`.

### 4e.5 Kernel 2.6.0 (`TaxKernel.Global2`, 2026-11-21): first-registration dates, half the global rate, the employer of household wages, advance income tax

Four requests (`global/KERNEL_REQUESTS.md`: FT reviewer 6 vehicle first-registration month, R1 Europe pass 10 stacking at
a fraction of the rate, R4-14-1 employer facts on household adults, and the Asia-Pacific PK advance-tax credit read in
PROGRESS_ASIAPAC.md session 6). **Everything is additive and opt-in**: new modules `Global2.Employer` and
`Global2.Advance` (imported by `TaxKernel.Global2`); `Vehicle` gains two record fields, two attributes and two
`VehicleTax` fields; `StackRule` gains two fields; all new fields are last and default to the 2.5.0 behaviour. Nothing in
`TaxKernel.Global` (2.0-2.3) changed. Toy calls: `examples/Global2.lean` sections "2.6.0" (77 `#guard`s, 354 in the
file); axioms: `audit/AxiomsGlobal2.lean` (31 new theorems and the 4 re-proven stacking theorems, no `sorry`).

**When a vehicle was first registered** (FT reviewer 6, `Vehicle`). New optional fields on the vehicle record:
`"firstRegMonth"` (1-12) and `"firstRegDate"` (`"YYYY-MM-DD"` or `"YYYY-MM"`; it fills the year when `"firstRegYear"` is
absent, the month when `"firstRegMonth"` is absent, but only if its year is the vehicle's year, and the day). Attributes
`.firstRegMonth` (1-12) and `.firstRegDay`, usable in `when` and `parts` like any other (`(.firstRegMonth, 6, 12)` = July
to December). New `VehicleTax` fields **`regFromDate`, `regToDate`** (ISO, both inclusive, `""` open): a
first-registration date window. The vehicle's first registration is known as a span of days (the day if given; else the
whole month; else the whole year): wholly inside the window, the tax selects it; wholly outside, it does not; **across a
bound, never guessed**: no charge, and `vehicleTaxUnknown` lists `"…: firstRegMonth not given (grade C)"` (or
`firstRegYear`, `firstRegDay`: what would decide it). A window that starts on the 1st of a month (TZ from 1 July 2025, FR
malus barème from 1 March 2025) is decided by the month alone; a bound inside a month needs the day. A bound that is not a
calendar date selects nothing. Without a window a tax is exactly the 2.5.0 tax (`VehicleTax.computes_noWindow`,
`selects_noWindow`, `missing_noWindow`); `computes_window_decided`: a computed tax never straddles its window.

```lean
-- FR malus: the 2024 barème to 28 February 2025, the 2025 barème from 1 March 2025 (a registration-time tax)
def malus24 : VehicleTax := { name := "malus", occasion := .registration, parts := [(.co2GKm, bareme24)],
    regToDate := "2025-02-28", statute := "CIBS L. 421-62 (barème 2024)" }
def malus25 : VehicleTax := { malus24 with parts := [(.co2GKm, bareme25)], regToDate := "", regFromDate := "2025-03-01",
    statute := "CIBS L. 421-62 (barème 2025)" }
-- a car first registered in 2025 with no month: neither barème is taken; grade C "firstRegMonth not given"
-- CL first permits priced by the month of first registration: one rule per month on the attribute
def clFirst : List VehicleTax := (List.range 12).map fun (k : Nat) =>
  { name := "permiso de circulación", occasion := .registration, fixed := amountFor (k + 1),
    «when» := [(.firstRegMonth, (k : Int), (k : Int) + 1)], statute := "DL 3.063 art. 12" }
```

**Half the global rate** (R1 Europe pass 10, `Stack`). Two last fields of `StackRule`:

| field | default | meaning |
|---|---|---|
| `shareBp` | 10000 | the charge is this share of what `mode` gives (rounded down; < 0 reads as 0) |
| `mode` | `.marginal` | `.marginal`: PIT(with) − PIT(without), 2.5.0; `.averageRate key`: the included amount × PIT(with) / taxable income(with), the taxable income being the number the 1.x line with the amount gives under `key` (top level of the line, else in its `"detail"`) |

LU L.I.R. art. 131 (1) c (gains of art. 99ter and 100, art. 132 (2)): "un taux égal à la moitié du taux global
correspondant au revenu imposable ajusté", the ordinary income keeping the tariff (art. 131 (1) a: the 1.x line,
unchanged):

```lean
def luHalf : StackRule :=
  { name := "Plus-values (art. 99ter, 100): moitié du taux global", statute := "L.I.R. art. 99ter, 100, 131 (1) c, 132 (2)",
    gainKinds := [.unlistedShares], gainRule := { minStakeBp := 1000 }, into := .rentalIncome,
    mode := .averageRate "taxableIncome", shareBp := 5000 }
-- the reading "(PIT(income + gain) − PIT(income)) × ½" is { luHalf with mode := .marginal }
```

The rate is that of the 1.x line *with* the included amount (the tax on the adjusted taxable income including the gain);
the central (income tax + surtaxes) and local income tax parts are each charged at it and rounded down; the 1.x line is
unchanged. **Never guessed**: a 1.x line with the amount that gives no positive number under `key`, or a negative income
tax, prices nothing for the rule (no charge, `"1100 <name>: no global rate: … (grade C)"`; `StackSlice.rated`). Check
that your 1.x line gives the taxable income (LU's does: `detail.taxableIncome`; ZA's toy in the examples too). Theorems:
`StackSlice.due_default` (default fields = the 2.5.0 charge), `dueTotal_nonneg`, `dues_zero`, `charges_sum` (now = the
slice's `dueTotal`); `stackCharges_nonneg` and `stackCharges_zero` keep their statements and hold for every mode.

**The employer of a household's wages** (R4-14-1, `Employer`). Optional fields on each `household.adults` record, read
like `company.payroll` / `employees` / `sector`: `"employerPayroll"` (the employer's annual payroll), `"employerEmployees"`
(its headcount), `"employerSector"` (string or array; names as `company.sector`, `Sector.canonical`),
`"employerRiskClass"` (string or number, read as text). `employerOf g i : EmployerFacts` (−1 / `none` / `""`: not given;
a 1.x household gives none). The levy:

```lean
-- NA VET levy: 1 % of payroll for employers with a payroll of N$1 000 000 or more
def naVet : EmployerLevy :=
  { name := "VET levy",
    rules := [
      { rateBp := 100, tests := [.payrollAtLeast 1000000], ifUnknown := .gradeC,
        statute := "VET Act 2008 s. 35; GN 67 of 2021 para 3" }] }
-- families := [..., naVet.family]; unsupported: naVet.unknown g; notes: naVet.notes g
```

`EmployerLevy := { name, oecd := .payroll (3000; .sscEmployer for 2200), level, rules, round, companies := false }`;
`EmployerRule := { rateBp, tests, ifUnknown, wageCap := -1, statute }` with tests `.payrollAtLeast x`, `.payrollBelow x`,
`.employeesAtLeast n`, `.employeesAtMost n`, `.inSectors l`, `.notInSectors l`, `.riskClasses l`. The first rule whose
tests hold applies; **`ifUnknown` has no default** (the `StateUnknown` of 2.4.0): `.general` (passed over for a missing
fact, the next rule is tried, `notes` says so), `.presume` (applied; the statute ends with `employerPresumedNote`),
`.gradeC` (no charge for that adult; `unknown` lists it). One charge per adult with wages > 0: base = wages, relieved =
wages up to `wageCap`, due = rate × relieved, bearer `employer`, event `"adult <i> wages"`. With `companies := true` a
company entity is charged on its own `company.payroll`, its facts read from its record (`payroll`, `employees`,
`sector`, `riskClass`). Theorems: `employerPick_noFacts` (no fact given never yields a conditional rate unless the rule
presumes it), `EmployerLevy.charges_noWages`, `chargeOf_wf`, `chargeOf_due_nonneg`, `EmployerTest.eval_none`,
`employerOf_null`.

**Advance income tax credited against the year's income tax** (Asia-Pacific PK, `Advance`). PK ITO 2001 s. 236C (seller of
immovable property) and s. 236K (purchaser) are *adjustable* advance tax: a prepayment of the year's income tax, not a
transfer duty. `AdvanceTax := { name, oecd := .pit, source, rates, credit, creditStatute, round }`:
* `source`: `.disposals kinds` (the seller; base = proceeds) or `.purchases kinds` (the buyer; base = the assessed value
  if given, else the price);
* `rates : List AdvanceRate`, each `{ ceilings := [(up to, bp), …], topBp, dateFrom, dateTo, statute }`: the whole base at
  the rate of the first ceiling it does not exceed; the first rate whose dates hold (the record's `"date"`, ISO) applies;
  a dated rate on an undated record: **no charge, grade C** (`advanceTaxUnknown`);
* **`credit` (no default)**: `.adjustable` (due = gross − min(gross, the year's income tax not yet credited)), `.refundable`
  (credited in full: due 0, gross and credit shown), `.final` (not credited).

The year's income tax is every 1100 charge booked before the family (the 1.x line, a stacked rule's charges); put all of
a model's advance taxes in **one** `advanceTaxFamily name [t1, t2]` after the income-tax families (they consume the
income tax in the order of the transactions). The 1.x line is unchanged; an entity without such transactions is
unchanged (`advanceTaxFamily_noItems`). Theorems: `advanceCharges_adjustable_total` (Σ due = Σ gross − min(Σ gross,
income tax): what the advance tax adds to the year), `advanceCharges_refundable`, `advanceCharges_due_nonneg`,
`advanceCharges_wf`.

```lean
def pk236C : AdvanceTax :=
  { name := "Advance tax on sale of immovable property", source := .disposals [.home, .realEstate, .land],
    rates := [
      { ceilings := [(50000000, 450), (100000000, 500)], topBp := 550,
        statute := "ITO 2001 s. 236C; First Schedule Part IV Division X" }],
    credit := .adjustable, creditStatute := "s. 147, 168" }
def pk236K : AdvanceTax :=
  { name := "Advance tax on purchase of immovable property", source := .purchases [.home, .realEstate, .land],
    rates := [
      { ceilings := [(50000000, 300), (100000000, 350)], topBp := 400, dateTo := "2025-06-30", statute := "s. 236K, Div. XVIII" },
      { ceilings := [(50000000, 150), (100000000, 200)], topBp := 250, dateFrom := "2025-07-01", statute := "s. 236K (FA 2025)" }],
    credit := .adjustable, creditStatute := "s. 236K (2)" }
-- families := [..., advanceTaxFamily "advance income tax" [pk236C, pk236K]]; unsupported: advanceTaxUnknown [pk236C, pk236K] g
-- a 60 m home sold, income tax 300 000: gross 3 000 000, credit 300 000, due 2 700 000 (the year's 1100 = 3 000 000)
```

**Equivalence (2.5.0 -> 2.6.0, `global/kcheck26/compat26.py`):** all 201 country projects under `global/` built on both kernels (201 identical, 0 build failures) and ran on the same inputs: **104,019 output lines, 0 changed** (byte for byte). The 1.x adapter grid (legacy mode, 56 households) is byte-identical in all 201 (11,256 lines): PIT unchanged everywhere, and every one of the 92,763 global lines, `pit` included, is identical. By input: the global grid 11,256, compat21's lines 3,819, compat24's vehicle lines 1,608, compat25's lines 5,829, **a new set that uses what 2.6.0 reads** (`k26_extra`: vehicles with `firstRegMonth` / `firstRegDate`, also malformed, date-only and of another year; adults with employer payroll, headcount, sector and risk class; dated and undated sales and purchases of 10-150 m; unlisted-share gains with stakes; companies with payroll, sector, risk class and dated fleet vehicles: 4,824), the projects' own `results/cases.jsonl` 670, FT dataset entities 1,154, company FT grid dev cases 25,503 and the vehicle / cgt / capinc / employer FT grid dev cases 38,100: all identical. 107 projects import `TaxKernel.Global2` (they recompile; no build needed a source change). **Probe on every project** (the project's own `model` with an `.averageRate "taxableIncome"` rule at half, an `EmployerLevy` family and an `advanceTaxFamily` added; 3 households each): 201/201 with the 1.x `pit` unchanged and the model's own charges a prefix of the extended model's; the 1.x line gives `taxableIncome` in 134 projects (the average-rate mode prices there; elsewhere it is grade C until the model names a key its line gives). Re-run after the release (18:17:56 UTC) on the live kernel with the builders' current sources (`postswap26.json`, old = `kcheck26/kernel_prev_25`): 201/201 built and identical, 104,021 lines, 0 changed; probe 201/201 ok. Re-run: `python3 global/kcheck26/compat26.py --jobs 8 [--only R4/za,…] [--old DIR] [--new DIR] [--out NAME] [--no-probe]`.

### 4e.6 Kernel 2.7.0 (`TaxKernel.Global2`, 2026-11-21): foreign-currency amounts, vehicle tax by days and part windows, zone value, dated stacking, employer turnover, sectors outside the tax, elective flat rate

Eight requests (`global/KERNEL_REQUESTS.md`: R4-17-1 exchange-rate input; R1 Europe pass 15: IS days, SE three-year
window, GR zone value; FT reviewer 7 dated stacking for LU (also IMPROVE_FT R5-6); R4-18-1 employer turnover, R4-18-2 a
sector taxed under another Act, R4-18-3 stacking with an elective flat rate). **Everything is additive and opt-in**: new
modules `Global2.Fx` and `Global2.Zone` (imported by `TaxKernel.Global2`); `Vehicle`, `VehicleTax`, `StackRule`,
`StackSlice`, `EmployerFacts`, `SectorCorp` gain last fields whose defaults are 2.6.0; `EmployerTest` gains two tests.
Nothing in `TaxKernel.Global` (2.0-2.3) changed. Toy calls: `examples/Global2.lean` sections "2.7.0" (79 `#guard`s, 433 in
the file); axioms: `audit/AxiomsGlobal2.lean` (34 new theorems and 16 re-proven, no `sorry`).

**Amounts in a foreign currency, at a declared rate** (R4-17-1, `Fx`). The kernel never has a rate of its own. A rate is
`FxRate := { currency, num, den := 1, source, date }` (`num/den` units of the model's currency per unit of `currency`;
`source` and `date` have no default). Two ways to declare one:
* on the entity (the case's own rate, "the ruling exchange rate of the day"): `"fxRates"` at the top of the line (else in
  `company` or `household`), per currency a positive number or a record: `{"USD": 26.75}` or
  `{"USD": {"rate": 26.75, "source": "RBZ interbank mid-rate", "date": "2025-06-30"}}` (read exactly: 2675/100);
* on the rule: `fxRate := some { currency := "USD", num := 2690, den := 100, source := "…", date := "…" }`.

`fxFor g "USD" declared`: the entity's rate, else the declared one, else `none`. `VehicleTax.currency := "USD"`: `fixed`,
`parts`, `minAmount`, `maxAmount` are US$, converted exactly with one rounding; no rate: **no charge, `vehicleTaxUnknown`
"…: fxRates.USD not given (grade C)"**; the statute ends "; USD amounts at 26.75 (RBZ interbank mid-rate, 2025-06-30)".
For other parts: `QtyTable.amountFx t r q` (a US$ table converted; `amountAt t 1 1 = amount`), `FxRate.convert`,
`FxRate.toForeign` (a local value against a US$ threshold), `fxUnknownLine code name "USD"` for `unsupported`.
Theorems: `fxFor_none` (no input, no declared rate: no rate), `fxFor_input`, `fxFor_noInput`, `VehicleTax.computesIn_fx`
(a US$ tax computes only with a declared rate), `FxRate.convert_one`, `convert_nonneg`, `convert_mono`,
`QtyTable.amountAt_one`.

```lean
def zwLicence : VehicleTax :=
  { name := "vehicle licence", parts := [(.massKg, QtyTable.ofCeilings [(1000, 20), (2300, 30), (4600, 40)] 60)],
    currency := "USD", statute := "Vehicle Registration and Licensing Regulations Third Schedule Part II (SI 67 of 2024)" }
-- {"fxRates":{"USD":26.75}}, 1 500 kg: US$ 30 → 802; no fxRates: grade C "fxRates.USD not given"
```

**Vehicle tax by days held** (IS lög 39/1988 3. gr., `Vehicle`). New record fields `"heldFrom"`, `"heldTo"` (ISO; read
only by these options). `VehicleTax.proRataDays := true`: an annual tax × days held / days of the year;
`dayPeriods := [("01-01", "06-30"), ("07-01", "12-31")]`: each period an equal share of the year's amount by its days held
(a period held whole pays its share, the whole year the year's amount). Days held: from `"heldFrom"`, else for a vehicle
registered in the tax year its first-registration **day** (`"firstRegYear"` = the year, with `"firstRegDate"` or month
and day), else 1 January; to `"heldTo"`, else 31 December. **Not located, never guessed** (registered this year without
the day; registered this year but first registered earlier, without `"heldFrom"`; `"months"` < 12 and no date): grade C
(`firstRegDay`, `heldFrom` not given). Registration taxes are not prorated.

```lean
def isGjald : VehicleTax :=
  { name := "bifreiðagjald", fixed := 30000, dayPeriods := [("01-01", "06-30"), ("07-01", "12-31")], statute := "lög 39/1988 3. gr." }
-- registered 15 March 2025: 30 000 × 108 / (2 × 181) + 15 000 = 23 950; with proRataDays instead: 292/365 = 24 000
```

**A part for the first N months after first registration** (SE vägtrafikskattelag 2 kap. 9 a §). `partWindows :=
[{ part := 1, months := 36 }]` (`fromNextMonth := true` to count from the month after): part 1 (0-based in `parts`) ×
the months of the tax year inside the window and held / 12, rounded once; the windowed part is not prorated again, the
other parts are as before. Undecided: no `"firstRegYear"`; no `"firstRegMonth"` and the window ends inside the year (the
count is tried for every month; the same count for all decides); held < 12 months without dates while the window covers
part of the year: grade C. SE "107 kr instead of 22 kr per g for three years" = the ordinary part plus a windowed part with
the difference:

```lean
def seSkatt : VehicleTax :=
  { name := "fordonsskatt", fixed := 360,
    parts := [(.co2GKm, { steps := [(75, 22)] }), (.co2GKm, { steps := [(75, 85), (125, 110)] })],
    partWindows := [{ part := 1, months := 36 }], statute := "vägtrafikskattelag 2006:227 2 kap. 7, 9 a §§" }
-- 140 g/km, first registered April 2022: 1 790 + 5 900 × 3/12 = 3 265; 2022 without month: grade C "firstRegMonth"
```

A tax with none of the 2.7.0 options (`currency`, `proRataDays`, `dayPeriods`, `partWindows`) is exactly the 2.6.0 tax:
`VehicleTax.computesIn_v26`, `toChargeIn_v26`, `vehicleTaxCharges_v26`, `vehicleTaxUnknown_v26` (the 2.6.0 functions are
kept as `vehicleTaxCharges26` / `vehicleTaxUnknown26` to state it).

**Zone value and coefficients on real estate** (GR ENFIA, `Zone`). Asset record fields `"zoneValueM2"` (official price
per m², τιμή ζώνης; `assetZoneValueM2 g i`, −1 not given), `"buildYear"` (attribute `.age` = year − it), `"floor"`
(negative below ground), `"frontages"`, any other number as `.field "key"`; `assetFact? g i f`. `ZoneTax := { name, kinds
:= [.home, .realEstate], base, coefs, coefsFor, round, oecd := .propertyRecurrent, level := .central, event, statute }`:
* `base := .perArea [(zone value from, table on m²), …]`: area × the table of the zone value's band × Π coefficients;
* `base := .onValue table`: the table on the objective value area × zone value × Π coefficients;
* `coefs := [{ fact := .age, bands := [(from, factor bp), …] }, …]` (none reached: 10000), `coefsFor` by asset.

One charge per asset of `kinds` (base = area or objective value), rounded once. **A fact it reads and the asset does not
give: no charge, `unknown` lists "4100 <name>: asset 2 (home): zoneValueM2, age not given (grade C)"**. Theorems
`ZoneTax.charges_noFacts`, `charges_ofCanon`, `unknown_ofCanon`, `factor_nil`, `assetFact?_null`.

```lean
def enfia : ZoneTax :=
  { name := "ΕΝΦΙΑ κύριος φόρος",
    base := .perArea [(0, QtyTable.perUnit 200 100), (551, QtyTable.perUnit 280 100), (1051, QtyTable.perUnit 290 100)],
    coefs := [{ fact := .age, bands := [(0, 10000), (25, 9000)] }, { fact := .floor, bands := [(0, 10000), (3, 10200)] },
              { fact := .frontages, bands := [(0, 10000), (2, 10100)] }], statute := "ν. 4223/2013 άρθ. 4" }
-- 100 m², zone 1 200, built 1990, 4th floor, 1 frontage: 100 × 2,90 × 0,90 × 1,02 = 266
```
(the rates above are toy figures: the 2025 band table of ν. 4223/2013 was not reached by the builder).

**A date window on stacking rules** (FT reviewer 7, IMPROVE_FT R5-6; `Stack`). `StackRule.dateFrom` / `dateTo` (ISO,
inclusive): the rule takes only the disposals and income items whose record's `"date"` lies inside (`AdvanceRate`
semantics). **An item of the rule's kinds without a date, when the rule has a window: no charge for the rule (nor the
later ones), "1100 <name>: disposal 2 (unlistedShares) has no date (the rule takes items dated to 2025-09-30) (grade C)"**.
`rateFromStack := true` (`.averageRate` only): the global rate of the 1.x line with **every** rule's amount (one adjusted
taxable income for the whole stack; needs every rule priced). LU L.I.R. art. 99ter, 2025 (a quarter of the global rate for
sales to 30 September 2025, Loi du 22 mai 2024 art. 14 as extended by the laws of 4 April and 27 June 2025; half from
1 October, art. 131 (1) c):

```lean
def luQuarter : StackRule :=
  { name := "art. 99ter (quarter)", statute := "…", gainKinds := [.realEstate, .land, .home], into := .rentalIncome,
    mode := .averageRate "taxableIncome", shareBp := 2500, dateTo := "2025-09-30", rateFromStack := true }
def luHalf : StackRule := { luQuarter with name := "art. 99ter (half)", shareBp := 5000, dateTo := "", dateFrom := "2025-10-01" }
-- model.withStack [luQuarter, luHalf]; the art. 99bis derogation by sale date: two rules with their gainRules and windows
```
Without a window a rule is the 2.6.0 rule (`StackRule.wItems_noWindow`, `undated_noWindow`, `shareStackRate_none`).

**Stacking with an elective flat rate** (R4-18-3, GH Act 896 First Schedule para 1 (3) as substituted by Act 1094).
`StackRule.electFlatBp` (−1: none): the charge is the lower of the stacked charge and `electFlatBp` × the included amount
(the election presumed taken when lower; the statute then ends "; elective flat rate 2500 bp taken (lower than the
stacked tax)"; no local part). A later rule still stacks on the line with the amount. Theorems `StackSlice.due_noElect`,
`dueTotal_le_core`; `due_default` now also states `electFlatBp < 0`.

**The employer's turnover** (R4-18-1, NG ITF Act s. 6 (1)). Adult field `"employerTurnover"` (a company employer:
`company.turnover`), `EmployerFacts.turnover`, tests `.turnoverAtLeast x`, `.turnoverBelow x` (not given: the rule's
`ifUnknown`, as every test):
```lean
rules := [{ rateBp := 100, tests := [.employeesAtLeast 5], ifUnknown := .general, statute := "… (5 or more)" },
          { rateBp := 100, tests := [.employeesAtMost 4, .turnoverAtLeast 50000000], ifUnknown := .gradeC, statute := "… (N50 m)" }]
```

**A sector taxed under another Act** (R4-18-2, NA petroleum). `SectorCorp.outside := [{ sectors := ["petroleum"],
statute := "the Petroleum (Taxation) Act 1991" }]`: a company of such a sector gets no charge under this CIT and
`unknown` lists "1200 <name>: company.sector is taxed under the Petroleum (Taxation) Act 1991, not this tax (grade C)".
Without `outside` the 2.6.0 charges (`SectorCorp.citCharges_noOutside`; `citCharges_outside`).

**Equivalence (2.6.0 -> 2.7.0, `global/kcheck27/compat27.py`):** all 201 country projects under `global/` built on both kernels (201 identical, 0 build failures) and ran on the same inputs: **109,721 output lines, 0 changed** (byte for byte). The 1.x adapter grid (legacy mode, 56 households) is byte-identical in all 201 (11,256 lines): PIT unchanged everywhere, and every one of the 98,465 global lines, `pit` included, is identical. By input: the global grid 11,256, compat21's lines 3,819, compat24's vehicle lines 1,608, compat25's lines 5,829, compat26's lines 4,824, **a new set that uses what 2.7.0 reads** (`k27_extra`: `"fxRates"` at the top, in the household and the company, as numbers and records, also zero and malformed; vehicles with `"heldFrom"` / `"heldTo"` and first-registration dates, also malformed and of other years; homes, real estate and land with zone values, build years, floors and frontages; dated, undated and malformed-date disposals and income items; adults with an employer's turnover; companies with turnover, sector petroleum and US$ rates: 3,819), the projects' own `results/cases.jsonl` 729, FT dataset entities 1,178, company FT grid dev cases 25,503 and the vehicle / cgt / capinc / employer / property / payroll FT grid dev cases 39,900: all identical. 113 projects import `TaxKernel.Global2` (they recompile; no build needed a source change). **Probe on every project** (the project's own `model` with two dated `.averageRate` rules sharing the stack's rate, an elective-flat rule, a US$ vehicle tax with day periods and a part window, and a `ZoneTax` family added; 3 households each): 201/201 with the 1.x `pit` unchanged and the model's own charges a prefix of the extended model's. Re-run after the release (19:42:46 UTC) on the live kernel with the builders' current sources (`postswap27.json`, old = `kcheck27/kernel_prev_26`): 201/201 built and identical, 109,721 lines, 0 changed; probe 201/201 ok. Re-run: `python3 global/kcheck27/compat27.py --jobs 16 [--only R4/zw,…] [--old DIR] [--new DIR] [--out NAME] [--no-probe]`.

### 4e.7 Kernel 2.8.0 (`TaxKernel.Global2`, 2026-11-21): customs import duties, local taxes at the municipality's rate, undated items taxed at 0, coefficients from the asset's record

Two structural gaps of the full-coverage push (customs duties, OECD 5123: about 35 Americas rows and more elsewhere; local
taxes whose rate each municipality sets inside a national framework) and the two R1 Europe pass 17 requests.
**Everything is additive and opt-in**: new modules `Global2.Customs` and `Global2.LocalRate` (imported by
`TaxKernel.Global2`); `StackRule` and `ZoneTax` gain last fields whose defaults are 2.7.0. Nothing in `TaxKernel.Global`
(2.0-2.3) changed. Toy calls: `examples/Global2.lean` sections "2.8.0" (54 `#guard`s, 487 in the file); axioms:
`audit/AxiomsGlobal2.lean` (29 new theorems, `ZoneTax.factor_nil` re-proven with one more hypothesis; no `sorry`).

**Customs import duties** (`Customs`). Basket lines may carry (all optional, read from the line's JSON; `CustomsX`,
`consumptionC g`):
* `"hs"`: the HS code as **a string** of 2, 4, 6 or 8 digits (a national 10-digit line is accepted; dots, spaces and dashes
  are ignored: `"2203.00"` = `"220300"`; keep leading zeros: `"0901"`);
* `"origin"`: ISO 3166 code of the country of origin (alpha-2 recommended; read in upper case) or `"domestic"`;
* `"imported"` (2.1.0, unchanged; also the top-level `"importedGoods"`): a foreign `"origin"` makes a line imported too;
* `"customsValue"`: the customs value in money (default: the price before tax, below).

```lean
structure TariffLine := { hs : String, adValoremBp := 0, perUnitNum := 0, perUnitDen := 1, perKgNum := 0, perKgDen := 1,
                          mgPerUnit := 0, higherOf := false, statute := "" }
structure TariffPreference := { name, partners : List String, rateBp := 0, byHs : List (String × Int) := [],
                                hsOnly := [], hsExcept := [], keepSpecific := false, statute := "" }
structure TariffRule := { name := "customs duty", country := "", lines := [], otherBp := -1, preferences := [],
                          mfnIfOriginUnknown := false, dutyInVatBase := true, vatBp := 0, vatOf : Option Vat := none,
                          goods := [], oecd := .goodsOther, level := .central, statute := "" }
```
* **MFN lines by HS heading, the longest prefix winning** (`hsBest`, theorem `hsBest_longest`): a line `"2203"` beats `"22"`
  for code `220300`; `otherBp` (−1: none) is the rate of goods no line covers. Specific duties per canonical unit
  (`perUnitNum/perUnitDen` money per litre, stick, kWh) or per kg (`perKgNum/perKgDen`; mass = the line's `"massG"`, else
  quantity × `mgPerUnit`); `higherOf`: "x % or y, whichever is greater" (else ad valorem + specific).
* **Preferences keyed on origin**: a line whose origin is in `partners` pays the preference's rate (`byHs` by heading, else
  `rateBp`, 0 = duty-free; specific parts only with `keepSpecific`) on the goods it covers (`hsOnly`, `hsExcept`), or MFN
  where that is lower (the importer claims the lower; `pickLower_le`). CARICOM, MERCOSUR, the EU, ECOWAS, SACU: one
  `TariffPreference` each, first match wins.
* **The customs value**: `"customsValue"` when given, else the price before tax `b` from the tax-inclusive amount `p`: with
  the duty `d = a·b + s` in the VAT base (`dutyInVatBase`, the usual case) `p = (b + d)(1 + v)`, so
  `b = (p/(1+v) − s)/(1+a)`; outside it `b = (p − s)/(1+v+a)`; rounded down at each step. `v` is `vatBp`, or the good's
  class in `vatOf`. **Where an excise is also inside the price, give `"customsValue"`.** With the duty outside the VAT base,
  the 2.0 basket VAT (on the whole price) overstates by `t.vatOverstated g`: subtract it from the model's basket VAT.
* **Never guessed** (no charge; `t.unknown g` lists "5120 <name>: line 3 (spirits): … (grade C)"): an imported line without
  `"hs"` (`lineOutcome_noHs`) or with one that is not an HS code; a code no line covers and `otherBp < 0`; a code coarser than
  the tariff where the finer lines differ (`"22"` against 2203 at 40 % and 2204 at 20 %); a specific duty without the
  quantity or mass it needs; **no origin when a preference could apply**, unless the model declares the MFN convention
  (`mfnIfOriginUnknown := true`, noted in the statute); `"imported": true` with origin `"domestic"`.
* **Domestic lines pay nothing**: origin `"domestic"` or the model's `country`, or no origin and not imported
  (`lineOutcome_domestic`, `lineOutcome_notImported`).

One charge per dutiable line: `oecd := .goodsOther` (output code **5120**, the kernel's heading for 5122-5128, which holds
5123; FT selectors: `"oecd": "5120"` with a `tax_re` on the name), base = relieved = the customs value, due = the duty, event
`"line <i> (<good>)"`, bearer consumer, statute = the rule's and the line's statute, the heading and the preference applied.
`GlobalModel.withCustoms m [t]` adds the family (`customsFamily`) and the grade-C lines (`withCustoms_pit`,
`withCustoms_ofCanon`: a 1.x household is untouched). A CARICOM-shaped tariff (toy rates):

```lean
def cetTariff : TariffRule :=
  { name := "import duty (CET, shape)", country := "TT", vatBp := 1250,
    lines := [{ hs := "22", adValoremBp := 2000 }, { hs := "2203", adValoremBp := 4000 }, { hs := "2204", adValoremBp := 2000 },
              { hs := "2208", adValoremBp := 2000, perUnitNum := 6, higherOf := true }, { hs := "1701", perKgNum := 50, perKgDen := 100 }],
    preferences := [{ name := "CARICOM (Revised Treaty of Chaguaramas art. 164)", partners := ["AG", "BB", "BS", "BZ", "DM", "GD", "GY",
                      "HT", "JM", "KN", "LC", "MS", "SR", "TT", "VC"], hsExcept := ["2208"] }],
    statute := "Customs Act Chap. 78:01 First Schedule (shape)" }
-- beer 1 350 from the US, {"hs":"2203.00","origin":"US"}: value 1 350 / 1,125 / 1,40 = 857, duty 342 ("HS 2203 (MFN)")
-- the same from Jamaica: CARICOM preference, 0; {"origin":"domestic"} or no origin: nothing
-- {"imported":true} without hs, or with hs but no origin: grade C (a preference may apply)
def model : GlobalModel := base.withCustoms [cetTariff]
```

**Local taxes at the municipality's rate** (`LocalRate`). The national framework is statute, the rate a fact of the
entity's municipality; the kernel never has a rate of its own. Input (optional): `"localRates": {"<key>": {"rate": 0.3,
"source": "…", "date": "2025-01-01", "municipality": "Lisboa"}}` at the top of the line (else `company.localRates`, else
`household.localRates`); per key a record or a plain number ≥ 0; the number is read exactly, **as the municipality
publishes it, in the tax's unit** (`unit := .percent`: Hebesatz 470 = 470 %, IMI 0.3 = 0,3 %; `.permille`: a mill rate;
`.bp`; `.perUnit`: money per unit of the base). An asset record may carry its own `"localRates"` (an asset in another
municipality), which wins for that asset. Canonical keys (entity fields v4): `"propertyTax"` (recurrent tax on immovable
property), `"businessTax"` (local business or trade tax), `"vehicleTax"`; a model with two taxes of a kind names the second
itself.

```lean
structure LocalRateDecl := { municipality : String, num : Int, den := 1, source : String, date : String }   -- no defaults
inductive LocalBase | assets (kinds) | annualValue (kinds) | area (kinds) | amount (f : CanonGlobal → Option Int)
structure LocalTax := { key, name, base : LocalBase, unit := .percent, ratioNum := 1, ratioDen := 1, exempt := 0,
                        homeExempt := 0, minNum := -1, minDen := 1, maxNum := -1, maxDen := 1,
                        default : Option LocalRateDecl := none, byRegion : List LocalRateDecl := [], frameworkOnly := false,
                        inputAlias := "", regionOf := (·.company.region), round := {}, oecd := .propertyRecurrent,
                        level := .local, event := "asset", amountEvent := "year", statute := "" }
```
Base per item: `.assets` the statutory value (assessed, else market), `.annualValue`, `.area` (`"areaM2"`; missing: grade
C), `.amount f` one amount the model computes (the GewSt Messbetrag base; `none`: not levied); relieved = ⌊value ×
ratio⌋ − `exempt` (− `homeExempt` for a home); tax = round(⌊relieved × rate / scale⌋). **The rate, in order**: the item's
(asset's, else the entity's) `localRates.<key>`, else `inputAlias` (an older top-level number such as the DE pilot's
`"deHebesatz"`); else a declared rate: `byRegion` for the item's region (the asset's `region`, the company's `region`), or
`default` when the item gives no region or is in the default's municipality; else **no charge, grade C**: "4100 IMI:
asset 1: localRates.propertyTax not given (the municipality's rate, within 0.3 % to 0.45 %) (grade C)". **A rate outside
`minNum/minDen … maxNum/maxDen` is flagged, never used or clamped** (no charge, "…: localRates 0.5 % is outside the
statutory range (within 0.3 % to 0.45 %) (grade C)"; a declared rate likewise). **Framework only**
(`LocalTax.framework key name base unit min… max… statute`, or `frameworkOnly := true`): no number ever, one grade-C note
with the range per item. The charge's statute names the rate: "CIMI art. 112.º n.º 1 c); rate 0.3 % (Lisboa, <source>,
<date>; localRates)". `GlobalModel.withLocalTaxes m [t]` adds the family (`localTaxFamily`) and the grade-C lines.
Theorems: `resolveWith_input` (the entity's rate in range is used, whatever is declared), `resolveWith_outOfRange`,
`resolveWith_none` (no input and nothing declared: no rate), `resolveWith_framework`, `charges_rate` (only a resolved rate
is charged), `charges_ofCanon`, `taxAt_mono` (a higher rate never lowers the tax), `taxAt_zero`, `withLocalTaxes_pit`.

```lean
def imi : LocalTax :=           -- PT CIMI art. 112.º n.º 1 c): urban property 0,3 % to 0,45 % of the VPT
  { key := "propertyTax", name := "IMI (prédios urbanos)", base := .assets [.home, .realEstate],
    minNum := 3, minDen := 10, maxNum := 45, maxDen := 100, statute := "CIMI art. 112.º n.º 1 c)" }
-- {"localRates":{"propertyTax":{"rate":0.3,"source":"…","date":"2024-12-17","municipality":"Lisboa"}}}, VPT 200 000: 600;
-- 0.5: grade C (outside the range); none: grade C; with default := some { municipality := "Lisboa", num := 3, den := 10,
-- source := "<the deliberação>", date := "…" }: 600 for an asset with no region or in Lisboa, grade C for one in Porto
def grundsteuer : LocalTax :=   -- DE GrStG §§ 13, 15, 25: Grundsteuerwert × 0,31 ‰ × Hebesatz (= 2.0 `twoStage`)
  { key := "propertyTax", name := "Grundsteuer B", base := .assets [.home, .realEstate], ratioNum := 31, ratioDen := 100000,
    statute := "GrStG §§ 13, 15, 25" }
-- 300 000, Hebesatz 470: 93 × 470 % = 437
def gewst : LocalTax :=         -- DE GewStG §§ 11, 16 (4): 3,5 % × Hebesatz, at least 200 %; reads the pilot's deHebesatz
  { key := "businessTax", name := "Gewerbesteuer", ratioNum := 35, ratioDen := 1000, minNum := 200, inputAlias := "deHebesatz",
    base := .amount (fun g => if g.entity == .company then some g.company.profit else none), oecd := .cit, statute := "GewStG §§ 11, 16" }
def model : GlobalModel := base.withLocalTaxes [imi]
```

**An undated item the rule taxes at 0** (R1 Europe pass 17, `Stack`). `StackRule.undatedIfTaxable` (`false`: 2.7.0): with
a date window, an item without a date is undecided (grade C) only when its amount under the rule is not 0 (an undated sale
of a main home that `gainRule` exempts whatever the date no longer blocks LU art. 99bis / 99ter); a loss is still undecided.
`StackRule.undated_v27`, `undated_taxable`.

**Coefficients chosen from the asset's record** (R1 Europe pass 17, `Zone`). `ZoneTax.coefsAt g i a` (default `none`): the
coefficient list of asset `i` from anything its record holds, before `coefsFor` and `coefs`; the facts an asset needs are
those of its own list (`needsAt`). GR ΕΝ.Φ.Ι.Α. άρθ. 4 Α παρ. 2 ε (a detached house takes Σ.Μ. 1,02 instead of the floor
coefficient): `coefsAt := fun g i _ => if assetFact? g i (.field "detached") == some 1 then some detachedCoefs else none`.
`ZoneTax.coefsAtOf_default`, `needsAt_default`; `factor_nil` now also assumes `coefsAt g i a = none`.

**Equivalence (2.7.0 -> 2.8.0, `global/kcheck28/compat28.py`):** all 201 country projects under `global/` built on both kernels (201 identical, 0 build failures) and ran on the same inputs: **340,385 output lines, 0 changed** (byte for byte). The 1.x adapter grid (legacy mode, 56 households) is byte-identical in all 201 (11,256 lines): PIT unchanged everywhere, and every one of the 329,129 global lines, `pit` included, is identical. By input: the global grid 11,256, compat21's lines 3,819, compat24's vehicle lines 1,608, compat25-27's lines 14,472, **a new set that uses what 2.8.0 reads** (`k28_extra`: basket lines with `"hs"` as strings, numbers, dotted and malformed codes, `"origin"` in upper and lower case and `"domestic"`, `"customsValue"` also negative, `"imported"` and `"importedGoods"`; `"localRates"` at the top, in the household, in the company and on asset records as numbers, records, zero, negative and malformed; `"deHebesatz"`; undated main-home sales; real estate with `"detached"`: 3,819), the projects' own `results/cases.jsonl` 774, FT dataset entities 1,178, company FT grid dev cases 25,503 and **the dev cases of every other FT grid** (266,700: vat 212,700, employer 26,700, cgt 6,600, capinc 3,000, inheritance 2,400, vehicle 1,800, sdlt 1,800, payroll 1,200, stampduty 1,200, grest 900, acqtax 900, excise 900, transferduty 600, abgeltung 600, gewst 600, property 600, enregistrement 300, purchasetax 300, avd 300, tapuharci 300, bsdabsd 300, ltt 300, mltt 300, stamptax 300, tob 300, gift 300, itp 300, pcc 300, dividend 300, wealth 300): all identical. 118 projects import `TaxKernel.Global2` (they recompile; no build needed a source change). **Probe on every project** (the project's own `model` with a customs tariff (MFN lines, a preference, the MFN convention) and two local taxes (a property tax in a range with a default municipality, a business tax on an amount read through `inputAlias`) added; 3 entities, the expected duties and taxes 342 / 2 100, 200 and 171 500): 201/201 with the 1.x `pit` unchanged, the model's own charges and `unsupported` a prefix of the extended model's and the expected amounts. Re-run after the release (22:10:31 UTC) on the live kernel with the builders' current sources (`postswap28.json`, old = `kcheck28/kernel_prev_27`): 201/201 built and identical, 340,388 lines, 0 changed; probe 201/201 ok. Re-run: `python3 global/kcheck28/compat28.py --jobs 16 [--only R2/tt,…] [--old DIR] [--new DIR] [--out NAME] [--no-probe]`.

### 4e.8 Kernel 2.9.0 (`TaxKernel.Global2`, 2026-11-22): zakat, dated tariffs and surcharges by origin, container size, the manufacturer's value, the tenant on a lease

Facts the statutes depend on and the input could not state (KERNEL_REQUESTS.md R3-GAP-1, R2-GAP-1, R3-GAP-2, K29-LEASE,
K29-MFRVALUE, K29-CUSTOMS-FX). **Everything is additive and opt-in**: new modules `Global2.GoodsValue`, `Global2.Zakat`,
`Global2.Lease` (imported by `TaxKernel.Global2`); `TariffLine`, `TariffPreference` and `TariffRule` gain last fields whose
defaults are 2.8.0, and a rule that uses none of them computes exactly as 2.8.0 (`TariffRule.outcome_v28`). Nothing in
`TaxKernel.Global` (2.0-2.3) changed. Toy calls: `examples/Global2.lean` sections "2.9.0" (57 `#guard`s, 544 in the file);
axioms: `audit/AxiomsGlobal2.lean` (36 new theorems; no `sorry`).

**Zakat by the payer's faith** (`Zakat`, R3-GAP-1). New optional facts, never presumed by the kernel:

| where | JSON | meaning |
|---|---|---|
| `household.adults[i]` | `"zakatLiable": true/false` | liable or not (wins over the others) |
| `household.adults[i]` | `"religion"` | `"muslim"` / `"islam"` (any case, spaces ignored): liable; any other text: not liable |
| `household.adults[i]` | `"zakatExemptDeclared": true` | a declaration of exemption filed (PK CZ-50): exempts a Muslim where the rule allows it |
| `household.adults[i]` | `"zakatableWealth"` | the adult's own zakatable figure (wins over the assets) |
| `company` | `"muslimOwnershipBp"` (0-10 000), `"zakatLiable"`, `"zakatBase"` | the Muslim-held share (`zakatLiable: true` = 10 000), the base the statute defines |

```lean
structure ZakatRule := { name := "zakat", rateBp := 250, nisab := 0, nisabSource := "", onExcess := false,
                         adults : Option ZakatBase := some (.wealth [.deposits, .listedShares, .unlistedShares, .bonds, .business, .other]),
                         adultField := "zakatableWealth", allowance := 0, exemptByDeclaration := false,
                         presume : Option Bool := none, presumeNote := "", companies : Option ZakatCompany := none,
                         oecd := .other, level := .central, statute := "" }
inductive ZakatBase := | wealth (kinds : List AssetKind) | income (kinds : List IncomeKind) | field (key : String)
structure ZakatCompany := { base := .field "zakatBase" | .netAssets | .equity | .profit, presumeShareBp := -1, presumeNote := "", nisab := false }
```
* **Per adult**: `rateBp` (2.5 %) of the base when it reaches the **nisab** (`nisab` in money, declared by the model with
  `nisabSource`: the nisab follows the gold or silver price), on the whole base (`onExcess := false`, the classical rule) or
  the excess. `.wealth kinds`: the adult's assets of those kinds (`"person"` = the adult's index; value less debt); `.income
  kinds`: the adult's wages and income items of those kinds (MY zakat on income), less `allowance`; `.field k`: a number on the
  adult's record. A liable adult below the nisab books a **0 charge** (computed, statute "below the nisab"); a non-liable adult
  books none.
* **Per company** (`companies := some {}`): the base × the Muslim-held share (`"muslimOwnershipBp"`), the rate on that part.
* **What an absent fact means is declared**: `presume := none` (default) → grade C: `"6000 zakat: adult 1: religion not given
  ("zakatLiable" or "religion"; the rule presumes nothing) (grade C)"`; `presume := some true` with `presumeNote` (the reason,
  e.g. a constitution that makes citizens Muslims) → liable, the statute ending `presumed liable (the model's declared
  presumption: …)`; companies: `presumeShareBp` the same.
* Charges under `oecd` (`.other` = 6000 by default; the OECD books MV zakat al-mal under 4210: `oecd := .wealth`), event
  `"adult <i>"` / `"year"`, bearer entity. `model.withZakat [rule]`. Theorems `ZakatStatus.ofFacts_unknown` (no fact, no status),
  `zakatDue_belowNisab`, `zakatDue_nonneg`, `zakatDue_mono`, `ZakatRule.statusOf_unknown`, `withZakat_pit`.
* Variants: PK (Zakat and Ushr Ordinance 1980): `adults := some (.wealth [.deposits])`, `exemptByDeclaration := true`; MY
  (zakat on income): `.income [...]` with `allowance`; MV: the default wealth base, `oecd := .wealth`; SA/QA companies:
  `companies := some { base := .field "zakatBase" }` (or keep 2.1.0 `CorpRule.shareKey` for the CIT/zakat split).

A Maldives-shaped case (`examples/Global2.lean`): nisab 110 000; a Muslim adult with 300 000 on deposit → 7 500; a second
adult with 65 000 → 0 ("below the nisab"); a Buddhist → no charge; no religion → grade C; a company with base 1 000 000, 60 %
Muslim-held → 15 000.

**Dated tariff lines and surcharges by origin** (`Customs`, R2-GAP-1).
```lean
structure TariffLine       := { …2.8.0…, validFrom := "", validTo := "", currency := "" }
structure TariffPreference := { …2.8.0…, validFrom := "", validTo := "" }
structure TariffSurcharge  := { name, origins := [], exceptOrigins := [], hsOnly := [], hsExcept := [], adValoremBp := 0,
                                perUnitNum := 0, perUnitDen := 1, perKgNum := 0, perKgDen := 1, mgPerUnit := 0, currency := "",
                                validFrom := "", validTo := "", exceptPreferences := [], statute := "" }
structure TariffRule       := { …2.8.0…, surcharges : List TariffSurcharge := [], fxRate : Option FxRate := none }
```
* **Date windows** on tariff lines, preferences and surcharges: in force for goods entered on `validFrom ≤ date < validTo`
  (ISO, `""` open), the basket line's `"date"` (else the entity's top-level `"date"`, as 2.1.0). Two lines may share a heading
  with different windows (AR Decreto 333/2025: 16 % to 15 May, 8 % from). **An undated line** is priced only when the rule
  gives the same value and duty on every day of the year (checked on the first day and every day a window opens or closes;
  statute `"; no date: the same duty all year"`); otherwise grade C: `"no "date" and the duty changes within the year (on
  2025-02-04, 2025-03-04, 2025-04-05): give the line's "date""`. A date that is not `YYYY-MM-DD` is grade C under a dated rule.
* **Surcharges** are **added** to the MFN or preferential duty (preferences can only lower; `pickLower`): every surcharge in
  force whose `origins` (`[]`: every foreign origin) contain the line's origin, not in `exceptOrigins`, on the headings it
  covers (`hsOnly`/`hsExcept`, as preferences). `exceptPreferences := ["USMCA"]` (or `"*"`): waived when the line claims that
  preference (the importer compares MFN + surcharges with preference + the surcharges not waived). With a surcharge the
  customs value comes out of the price with the surcharge inside it: `b = (p/(1+v) − s − s_s)/(1 + a + a_s)`; a mixed
  `higherOf` duty with a surcharge needs the line's `"customsValue"` (else grade C). **No origin where a surcharge limited by
  origin could apply: grade C** (a surcharge on every origin needs none). The charge stays one per line: the duty includes the
  surcharges, the statute lists each (`"EO 14257; + reciprocal 10 %: 68"`).
* **Specific duties in a foreign currency** (SSA note: EAC "75 % or US$ 345/t"): `TariffLine.currency := "USD"` (or on a
  surcharge), converted at the entity's `"fxRates"` (2.7.0) or the rule's declared `fxRate` (with source and date); exactly
  (the rate scales the fractions, one rounding); no rate: grade C. The statute names the rate.
* A US-shaped case: HTSUS 6109.10 at 16,5 %, IEEPA China 10 % (4 Feb-3 Mar) then 20 % (from 4 Mar), reciprocal 10 % (from
  5 Apr, not CA/MX), IEEPA Canada/Mexico 25 % (from 4 Mar, waived under USMCA). A Chinese T-shirt for 1 000 on 10 May 2025:
  value 682, duty 112 + 136 + 68 = **316**; on 15 Jan: 858, 141 (the 2.8.0 figure); undated: grade C; Vietnamese on 1 June:
  790, 209; Canadian claiming USMCA: 0.
* Theorems: `TariffRule.outcome_v28`, `uses29_eq_false` (no 2.9.0 field: the 2.8.0 path), `onDay_open`, `datedOutcome_dated`,
  `datedOutcome_noBounds`, `lineOutcome29_domestic`, `surDuties_nonneg` (a surcharge never lowers the duty), `surDuties_fst`,
  `inForceOn_open`.

**Container size and the manufacturer's value** (`GoodsValue`, R3-GAP-2, K29-MFRVALUE). New optional basket-line fields
(`LineValueX`, `consumptionV g`): **`"containerMl"`** (one container in ml, > 0) and **`"exFactoryValue"`** (alias
`"manufacturerValue"`: the manufacturer's selling value of the line, money ≥ 0).
```lean
inductive GoodsValueBase := | retail | netOfVat | beforeTax | exFactory | customs
structure GoodsValueTax := { name, goods := [], exceptGoods := [], sub := "", minAbvBp := -1, maxAbvBp := 100000,
                             imported : Option Bool := none, value := .beforeTax, valueImported := none, fallback := none,
                             rateBp := 0, bands : List (Int × Int) := [], perContainer := false, maxContainerMl := -1,
                             vatBp := 0, validFrom := "", validTo := "", oecd := .excise, level := .central, statute := "" }
```
* A rate (`rateBp`) or **marginal value bands** `bands := [(upTo, rateBp), …]` (the last `upTo` −1: the rest) on the value
  `value`: `.retail` (the price), `.netOfVat`, `.beforeTax` (the price with this tax and VAT taken out, the bands inverted
  exactly: `bandInvert`), `.exFactory` (the line's `"exFactoryValue"`), `.customs` (the line's `"customsValue"`);
  `valueImported` for imported lines; **a value the line does not give is grade C** (`valueOf_missing`) unless the model
  declares `fallback := some .beforeTax` (the statute then says which value was used).
* **Per container** (`perContainer := true`): the bands apply to each container's value, `n = quantity / containerMl`
  containers (the quantity in ml); containers above `maxContainerMl` are taxed per litre. Computed exactly, rounded once
  (`dutyAt`: `Σ r_k·clamp(V·u − L_k·Q, 0, W_k·Q)/(u·10 000)`). No `"containerMl"` or no quantity: grade C.
* Selection: `goods` less `exceptGoods`, `sub`, strength band, origin `imported`, date window (an undated line under a dated
  rule: grade C).
* One charge per line: base = the price, relieved = the value taxed, due, event `"line <i> (<good>)"`, bearer consumer,
  `oecd` (`.excise` 5121; `.salesTax` 5112 for a manufacturer's sales tax). `model.withGoodsValueTaxes [t]`. Theorems
  `bandNum_flat`, `bandNum_nonneg`, `dutyAt_flat`, `valueOf_given`, `valueOf_missing`, `consumptionV_fst`,
  `GoodsValueTax.charges_ofCanon`, `withGoodsValueTaxes_pit`.
* A Hong Kong-shaped case (Cap. 109 Sch. 1 Part I para. 1A-1C: above 30 % vol, 100 % of the first $200 per container of ≤ 1 l,
  10 % of the rest, per litre above 1 l): `{ goods := [.spirits], minAbvBp := 3000, value := .beforeTax, bands := [(200, 10000),
  (-1, 1000)], perContainer := true, maxContainerMl := 1000 }`. One 750 ml bottle at $500: value 290, **duty 209**; six
  bottles at $200 each: value 600, duty 600; a 1,5 l bottle at $900: per litre, value 572, duty 327; no `"containerMl"`:
  grade C. MY sales tax on the manufacturer's value (10 %, `value := .exFactory`, `oecd := .salesTax`): `"exFactoryValue": 800`
  → 80 whatever the shop price; not given → grade C.

**The tenant on a lease** (`Lease`, K29-LEASE: BH municipal fee on rent to non-Bahrainis).

| where | JSON | meaning |
|---|---|---|
| an asset record (let by the entity) | `"lessee": {"nationality": "IN", "national": false, "resident": true, "kind": "company"}` | the tenant (any field optional) |
| an asset record | `"tenantNationality"`, `"tenantNational"`, `"tenantResident"` | the same, flat (no `"lessee"` record) |
| an asset record | `"rent"` (annual rent received; else `"annualValue"`), `"let": true` | the lease |
| a `rent` basket line | the same `"lessee"` / flat fields | the tenant (the household); not given: its first adult's own facts |
| `household.adults[i]` | `"nationality"`, `"national"`, `"resident"` | the adult's own |

```lean
inductive LesseeTest := | national | nonNational | resident | nonResident | nationalities (l : List String) | company | individual
structure RentLevy := { name, country : String, rateBp, side := .landlord | .tenant, kinds := [.home, .realEstate],
                        tests : List LesseeTest := [], ifUnknown : StateUnknown, bearer := .entity,
                        oecd := .propertyRecurrent, level := .local, statute := "" }
```
"National" is `"national"` when given, else the nationality compared with `country`. `ifUnknown` (required, as
`EmployerLevy`): `.gradeC` (no charge, grade C), `.presume` (applied, the statute says so), `.general` (not applied, an
informational line). Landlord side: the assets of `kinds` that carry a lessee, a `"rent"` or `"let": true`; a let asset
without rent or annual value: grade C. Tenant side: the household's `rent` lines. One charge per item (base = relieved = the
rent). `model.withRentLevies [l]`. Readers `lesseeOfAsset g i`, `tenantOfLine g j`, `adultNationality g i` for hand-written
parts. A Bahrain-shaped fee (10 %, `tests := [.nonNational]`, `country := "BH"`): let to an Indian national for 120 000 →
12 000; to a Bahraini → none; tenant not described → grade C. Theorems `LesseeTest.eval_none`, `RentLevy.decideFor_allGiven`,
`decideFor_unknown_gradeC`, `RentLevy.charges_ofCanon`, `withRentLevies_pit`.

**Equivalence (2.8.0 -> 2.9.0, `global/kcheck29/compat29.py`):** all 201 country projects under `global/` built on both kernels (201 identical, 0 build failures) and ran on the same inputs: **345,223 output lines, 0 changed** (byte for byte). The 1.x adapter grid (legacy mode, 56 households) is byte-identical in all 201 (11,256 lines): PIT unchanged everywhere, and every one of the 333,967 global lines, `pit` included, is identical. By input: the global grid 11,256, compat21's lines 3,819, compat24's vehicle lines 1,608, compat25-28's lines 18,291, **a new set that uses what 2.9.0 reads** (`k29_extra`: basket lines with `"date"` in and out of the year and malformed, `"hs"` / `"origin"`, `"containerMl"` (also 0 and text), `"exFactoryValue"` / `"manufacturerValue"` (also negative), rent lines with a lessee; adults with `"religion"`, `"zakatLiable"`, `"zakatExemptDeclared"`, `"zakatableWealth"`, `"nationality"`, `"national"`, `"resident"`; assets with `"lessee"` records, flat tenant fields, `"rent"`, `"let"`; companies with `"muslimOwnershipBp"` (also out of range), `"zakatLiable"`, `"zakatBase"`; `"fxRates"`: 4,824), the projects' own `results/cases.jsonl` 788, FT dataset entities 1,178, company FT grid dev cases 25,503 and **the dev cases of every other FT grid** (266,700: vat 212,700, employer 26,700, cgt 6,600, capinc 3,000, inheritance 2,400, vehicle 1,800, sdlt 1,800, payroll 1,200, stampduty 1,200, grest 900, acqtax 900, excise 900, transferduty 600, abgeltung 600, gewst 600, property 600, enregistrement 300, purchasetax 300, avd 300, tapuharci 300, bsdabsd 300, stamptax 300, ltt 300, mltt 300, tob 300, gift 300, itp 300, pcc 300, dividend 300, wealth 300): all identical. 134 projects import `TaxKernel.Global2` (they recompile; no build needed a source change). **Probe on every project** (the project's own `model` with a dated tariff with two surcharges, a per-container value tax, zakat (households and companies) and a rent levy on non-nationals added; 3 entities, expected 316 / 209 / 7 500 / 12 000, three grade-C lines, and 15 000): 201/201 with the 1.x `pit` unchanged, the model's own charges and `unsupported` a prefix of the extended model's and the expected amounts. Re-run after the release (00:06:34 UTC) on the live kernel with the builders' current sources (`postswap29.json`, old = `kcheck29/kernel_prev_28`): 201/201 built and identical, 345,223 lines, 0 changed; probe 201/201 ok. Re-run: `python3 global/kcheck29/compat29.py --jobs 16 [--only americas/us,…] [--old DIR] [--new DIR] [--out NAME] [--no-probe]`.

## 5. Theorems you can instantiate in one line (`TaxKernel.Theorems.*`, no `sorry`)

Statements are in the theorem files; the ones meant for country use (all take the schedule/part and its
conditions, which a concrete schedule discharges with `by decide`):

* `Schedule.ticks_succ s x : s.ticks (x+1) - s.ticks x = s.rate x` (any bands): the marginal rate is the band's.
* `Schedule.ticks_mono (h : s.RatesNonneg) : x ≤ y → s.ticks x ≤ s.ticks y`; `Schedule.ticks_mono_of_progressive (h : s.progressive = true)`.
* `Schedule.ticks_nonneg`, `Schedule.ticks_of_nonpos` (tax of 0 is 0 when thresholds ≥ 0).
* `Schedule.rate_le_max (h : s.progressive = true) : s.rate x ≤ s.maxRate`, `Schedule.ticks_lipschitz` (no jump: `s.ticks y - s.ticks x ≤ s.maxRate * (y - x)`),
  `Schedule.ticks_le_maxRate_mul` (`s.ticks x ≤ s.maxRate * x` for `x ≥ 0`).
* `Schedule.ticks_convex (h : s.progressive = true) : Convex s.ticks`.
* `Rule.apply_mono`, `Rule.ofTicks_mono`, `toMultiple_down_bounds` (`r ≤ x < r + step`), `toMultiple_up_bounds`, `toMultiple_halfUp_bounds`, `ticksToUnits_down_bounds`.
* `Taper.amount_le_full`, `Taper.floor_le_amount`, `Taper.amount_antitone`, `Taper.amount_step` (inside the band `den` more income removes exactly `num` of allowance) and `Taper.taper_marginal` (with a constant schedule rate `r`, `den` more income costs `r * (den + num)`: the effective marginal rate exceeds `r`).
* `Credit.value_le_full`, `applyCredits_nonneg` (no refundable credits ⇒ tax ≥ 0), `applyCredits_waste` (unused non-refundable credit is lost).
* `Surcharge.ticks_mono` and `Surcharge.withSurcharge_mono` (tax + surcharge(tax) monotone), `Surcharge.exempt_notch` (exemption limit with no glide zone = a jump).
* `splitting_le_separate (hc : Convex f) (hm : Monotone' f) : splitting f a b ≤ separate f a b`, `splitting_eq_of_equal`, `separate_le_joint`.
* `Contribution.floor_notch` (an all-or-nothing floor is a jump of `sched.ticks floor`), `Contribution.ticks_above_ceiling`.

Example (a country's `Theorems.lean`; the full set for the toy country is in `examples/zz/lean/ZzTax/Theorems.lean`,
including a concrete taper band `taper_60` proved from `Taper.taper_marginal`):

```lean
theorem fed_progressive : fedSchedule.progressive = true := by decide
theorem fed_mono : Monotone' fedSchedule.ticks := Schedule.ticks_mono_of_progressive _ fed_progressive
theorem fed_convex : Convex fedSchedule.ticks := Schedule.ticks_convex _ fed_progressive
theorem fed_split_ok (a b : Int) : splitting fedSchedule.ticks a b ≤ separate fedSchedule.ticks a b :=
  splitting_le_separate _ fed_convex fed_mono a b
theorem pa_wf : pa.WellFormed := by unfold Taper.WellFormed pa; decide
```

Full list of generic theorem names (files `TaxKernel/Theorems/Schedule.lean`, `Parts.lean`, `TaxKernel/Rounding.lean`):
Schedule: `bandsTicks_succ`, `Schedule.ticks_succ`, `Schedule.ticks_mono`, `Schedule.ticks_of_nonpos`, `Schedule.ticks_zero`,
`Schedule.ticks_nonneg`, `Schedule.rate_bounds`, `Schedule.ticks_lipschitz`, `Schedule.ticks_le_mul`,
`Schedule.ticks_const_rate`, `Schedule.progressive_parts`, `Schedule.ticks_mono_of_progressive`, `Schedule.rate_mono`,
`Schedule.ticks_convex`, `Schedule.maxRate_nonneg`, `Schedule.ratesLe_maxRate`, `Schedule.rate_le_max`,
`Schedule.ticks_lipschitz_of_progressive`, `Schedule.ticks_le_maxRate_mul`, `Schedule.tax_mono`, `incr_bounds'`,
`mono_of_incr`. Taper: `Taper.reduction_nonneg`, `amount_le_full`, `floor_le_amount`, `reduction_mono`,
`amount_antitone`, `amount_below_start`, `reduction_step`, `amount_step`, `taxable_step`, `taper_marginal`,
`taper_marginal_gt`. Credit: `Credit.value_le_full`, `Credit.value_antitone_inc`, `applyCredits_nonneg`,
`applyCredits_mono`, `applyCredits_waste`. Surcharge: `Surcharge.ticks_nonneg`, `ticks_mono`, `amount_mono`,
`withSurcharge_mono`, `exempt_notch`, `glide_no_notch`. Unit: `incr_mono_of_convex`, `shift_le_of_convex`,
`splitting_le_separate` (needs `Convex f` and `Monotone' f`), `splitting_eq_of_equal`, `separate_le_joint`
(aggregation without splitting is a marriage penalty for convex `f` with `f 0 = 0`). Social:
`Contribution.floor_notch`, `ticks_above_ceiling`, `ticks_mono`. Dual: `Dual.capitalTicks_mono`. Rounding:
`divR_down_bounds`, `divR_up_bounds`, `divR_halfUp_bounds`, `toMultiple_down_bounds`, `toMultiple_up_bounds`,
`toMultiple_halfUp_bounds`, `ticksToUnits_down_bounds`, `divR_mono`, `Rule.apply_mono`, `Rule.ofTicks_mono`.

If a generic theorem FAILS for your country (a schedule that is not progressive, a surcharge that is not
monotone), that is a finding: record it in your FINDINGS.md and tell the kernel (append to
`cmp20/kernel/INBOX.md`, one line, your folder name first).

## 6. How to model a country in 1 hour (the recipe)

1. Copy `cmp20/kernel/examples/zz/lean` to `cmp20/<owner>/<cc>/lean`, rename `ZzTax`/`zztax` to `<CC>Tax`/`<cc>tax`,
   set `path = "../../../kernel"` in `lakefile.toml`, `lake build` (works before you change anything).
2. `Params.lean`: every number with its citation (`/-- ITA s. 117(2)(a): "15% of the amount taxable" … -/`).
3. Map the household: who is a taxpayer (`c.adults`), how investment income is split (`half1`/`half2`), which
   children count (`c.childrenUnder 18`).
4. Compose: income measure → `Taper`/`taxableAfter` (allowances) → `Schedule.tax` (rates, with the statute's
   `Rule`) → `applyCredits` (offsets) → `Surcharge` (levies) → `Contribution` (social) → `Out.make`.
   Unit of assessment: compute each spouse alone, or `splitting`/`quotient` the per-person function.
5. Run the toy grid: `python3 cmp20/harness/tax20.py --countries <CC> --demo` and the OECD check
   `python3 cmp20/harness/oecd_check20.py <CC>`; fix until the OECD lines match or you can say why not.
6. `Theorems.lean`: the one-liners of §5 for each schedule/taper/credit you used.
7. Run the generic scanners: `python3 cmp20/harness/search/run_all.py <CC>` (results in
   `cmp20/<owner>/<cc>/results/search/`), then read the summary for findings to check against the statute.

## 7. Harness (for country agents)

* `cmp20/harness/tax20 '{"adults":[{"wages":1.0}]}'`: one household, every country (amounts in average wages by
  default; `--units ppp` USD at OECD PPP; `--units local`; `--countries CA,UK`; `--json`; `--demo`), local currency
  + USD PPP. Countries not built yet are listed as such.
* `python3 cmp20/harness/run20.py --countries CA|all|built|new --grid grid.jsonl [--units local|aw|ppp] [--frozen]
  [--out DIR]`: run a JSONL grid through any subset of the 20; `--frozen` copies each exe first so a rebuild cannot
  change a run. Elections (choices the law leaves to the taxpayer) are made cheapest-first from
  `cmp20/<owner>/<cc>/elections.json` (format in `harness/common20.py`).
* `python3 cmp20/harness/oecd_check20.py CA [--out cmp20/anglo/ca/results] [--quiet]`: the eight OECD Taxing
  Wages family types at the OECD's 2025 average wage through `catax`, line by line against the OECD's published
  country table (exact = within 1 unit; within 1 %), and a ready `validation` entry for summary.json. Default
  mapping: incomeTax + all surtaxes = CGITFP, localIncomeTax = SLT, employeeSocial = EECSSC, benefits = CTGG,
  `detail.taxableIncome` = CGTC, `detail.taxBeforeCredits` = CGITLETC. If your country books an item on another
  OECD line, write `def map_<cc>(row): return {...}` in `cmp20/<owner>/<cc>/oecd_map.py` (found automatically;
  examples for DE/JP/UK in `cmp/compare/harness/oecd_maps.py`). Regression on the five (take-home pay within
  1 %): UK 8/8, DE 8/8, US 8/8, JP 7/8, FR 6/8.
* OECD data for all 20: `cmp20/harness/data/oecd/tw_cou_xdc.json` (`[ISO3][year][type][measure]`, national
  currency, 2022-2025), `tw_cou_pct.json` (rates), raw CSVs `tw_cou_20.csv`, `tw_comp_20.csv`, `tw_decomp_20.csv`
  (marginal-rate decomposition). The five-country values are reproduced exactly (3,520 of 3,520).
* Params: `cmp20/harness/data/params.json` (AW, OECD PPP, World Bank PPP and FX for all 20).
* Owner-manager: `python3 cmp20/harness/search/owner.py <CC>` with the company side in `harness/search/company.json`
  (add or correct your country's entry with citations; `dividend_routing` / `household_extra` tell the scan how your exe
  reads an owner's dividend).
* Generic scanners: `python3 cmp20/harness/search/run_all.py <CC> [--out DIR]` (see `harness/search/README.md`);
  per-country leads: `cmp20/kernel/LEADS.md`; everything kernel-side at once: `cmp20/report/refresh_all.sh`.

## 7b. Harness and referees for the 38 (2026-11-19)

* **Discovery**: `common20.py` knows all 38 (`OWNERS38`: germanic AT CH LU BE, baltic FI IS EE LV LT, central SK SI HU
  HR, southeast GR CY MT BG RO). An exe at `cmp20/<family>/<cc>/lean/.lake/build/bin/<cc>tax` is used as soon as it
  is built by `tax20`, `run20.py`, the scanners and the report. Selectors for `--countries` / `tax20 --countries`:
  `all` (38), `built`, `new38` (the 18), `twenty`, a family name (`germanic`, `baltic`, `central`, `southeast`), or a
  comma list. Elections: `cmp20/<family>/<cc>/elections.json` (format in `common20.py`), as before.
* **Params** (`harness/data/params.json`, built by `harness/fetch_oecd38.py`): AW, PPP and FX for all 38. The 13 OECD
  members: AW and PPP from Taxing Wages 2026 (year 2025) exactly as for the 20. BG HR CY MT RO: `aw` is Eurostat's
  gross earnings of the single person at 100 % AW (earn_nt_net, GRS, NAC, 2025; `aw_source`), `ppp_oecd` is the World
  Bank GDP PPP (`ppp_source`). Currencies: BGN for Bulgaria (2025 is before the euro), RON for Romania, EUR for HR CY MT.
* **OECD referee (13 members: AT BE CH EE FI GR HU IS LT LU LV SI SK)**: the eight Taxing Wages family types for 2025 are
  in `harness/data/oecd/tw_cou_xdc.json` (raw CSV `tw_cou_13.csv`, `tw_comp_13.csv`). Run
  `python3 cmp20/harness/oecd_check38.py <CC>` (same as `oecd_check20.py <CC>`: same households, lines, mapping via
  your `oecd_map.py`, output in `harness/runs/oecd20/`).
* **Eurostat referee (all EU members, the only published household-level referee for BG HR CY MT RO)**:
  `python3 cmp20/harness/oecd_check38.py <CC> --referee eurostat` (or `--referee both`), output in
  `harness/runs/eurostat38/`. It runs 13 family types (the OECD seven plus singles at 50/80/125 % AW and couples
  without children) at **Eurostat's own gross earnings** for each type and compares income tax (all levels: your
  incomeTax + surtaxes + localIncomeTax, or your oecd_map's CGITFP + SLT), employee contributions, family cash
  benefits and the net implied by Eurostat's lines. Data: `harness/data/eurostat/earn_nt_xdc.json`
  (`[CC][year][type][GEBT|TAX|EECSSC|CTGG|NET]`, national currency; Greece is stored as GR) and the rate series
  `earn_nt_rates.json` (tax wedge, low-wage trap, unemployment trap: useful against the METR scanner).
  **Read `harness/runs/eurostat38/CALIBRATION.md` before trusting it**: on 11 EU models that reproduce Taxing Wages,
  Eurostat's 2025 series agrees on net income within 2 % of gross in 107 of 143 cases and within 1 % on income tax in
  only 26 of 143 (it changed its average-worker earnings and scope in 2024, and its published NET is not its own
  lines' sum in 74 of 351 cases; kernel FINDINGS K9). So for BG HR CY MT RO: (1) run the Eurostat check and explain
  every line that differs by more than 2 % of gross; (2) the binding referees are the official calculator, the
  official worked examples and EUROMOD's country report parameters (CONTRACT38); say in summary.json which referee
  each count comes from (`"referee": "Eurostat earn_nt_net 2025 (OECD-EC tax-benefit model)"`, sanity bound only).
* **Scanners and owner-manager**: unchanged commands (`python3 cmp20/harness/search/run_all.py <CC>`); the
  owner-manager scan needs your country's company side in `harness/search/company.json` (the kernel owner adds the 18
  with citations; send corrections to `cmp20/kernel/INBOX.md`).

## 7c. Harness for world countries (2026-11-20)

* `common20.py` finds world exes (`cmp20/world/<batch>/<cc>/lean/.lake/build/bin/<cc>tax`); selectors `world`, a batch id
  (`B01-oecd5`, case-insensitive), `everything` (38 + world), and comma lists mixing codes and selectors. `all` is still the 38.
* **Scale ("AW") for a world country = its reference wage** from `cmp20/world/data/refwage.json` (or
  `world/<batch>/<cc>/scale.json`, which wins): a minimum-wage multiple, a reference wage the statute uses, or a statutory
  threshold, each with its source; **never an OECD/Eurostat/referee value** (CONTRACTWORLD testing order). `common20.WORLD_SCALE`
  holds the entries. No PPP for world countries (NaN): `--units ppp` is unavailable for them.
* Generic scanners: `python3 cmp20/world/tools/scan_world.py B01-oecd5 B02-g20 [--full]` (or `harness/search/run_all.py CC`);
  results go to `cmp20/world/<batch>/<cc>/results/search/` by default. The owner-manager scan is skipped without a company
  side in `harness/search/company.json`.

## Changes
* 1.0 (2026-11-19): first publication.
* 1.0.1: theorems of §5 proved (no `sorry`); harness tax20/run20/oecd_check20 and OECD data for all 20.
* 1.0.2: optional input field `cohabiting` (§2); LEADS.md; refresh_all.sh. No signature changed.
* 1.1: `TaxKernel.Table` (lookup tables with decidable checks against a formula; `perPeriod`), asked for in the KR and MX kernel gaps. Added only.
* 1.2 (2026-11-19, for the 38): `TaxKernel.Multiplier` (multipliers on a base tax, tax at an average rate, rate splitting with a divisor, credit allocation over several taxes) `TaxKernel.Family` (child scales, income attribution between spouses, low-band allowance, allowance spilling into another levy, stepped taper, reduced contribution base) and `TaxKernel.Tariff` (tariffs printed as columns or as rate-minus-subtraction, with checks against the bands), theorems in `TaxKernel/Theorems/Parts38.lean` (§4b); harness and referees for the 38 (§7b). Added only: no name or signature of 1.1 changed.
* 1.2.1 (2026-11-19): `TaxKernel.Extra38` for the gaps the 18 reported (SK half-up taper, HU capped spill, BE exempt sum on its own tariff, mid-year parameters, AT rate by size of base). Added only.
* 1.3.0 (2026-11-20, world expansion, cmp20/world/CONTRACTWORLD.md): `TaxKernel.World` (indexed units, schedular systems with an annual overlay, zakat, territorial base and the optional `foreignIncome` field, exemption written as a tax, cumulative withholding, `worldMain`), §4c. Not imported by the root module: the 38 rebuilt unchanged (byte-identical output). Added only.
* 1.4.0 (2026-11-20, world/KERNEL_REQUESTS.md): `TaxKernel.World2` (column tariff chosen by the size of the whole income with the notch-location theorem; amounts indexed by a published coefficient), §4d; harness reference wages for world countries (§7c). Not imported by any earlier module: all 49 kernel-built models rebuilt unchanged (byte-identical). Added only.
* 2.0.0 (2026-11-21, cmp20/global/DESIGN.md): `TaxKernel.Global` (all OECD tax headings; the master equation; `CanonGlobal`/`OutGlobal`; corporate, capital income and gains, withholding, property and wealth, inheritance and gift, transfer duties, VAT, excises, employer side and payroll; adapters `ofCountry`/`ofLine` with the proofs that every 1.x output is unchanged), §4e. `lakefile.toml` adds the library `TaxKernelGlobal` to the default targets. Not imported by any 1.x module: all 197 PIT models checked (global/kcheck/adapter.json). Added only.
* 2.1.0 (2026-11-21, global/KERNEL_REQUESTS.md): `TaxKernel.Global2` (dated VAT periods; excise rules on the value before excise and VAT, per kg/tonne, per degree Plato, sugar bands, sub-categories, origin, date windows; CIT with floored and capped minimum taxes, profit rounding and a taxable ownership share; per-line basket extras read from the line's JSON), §4e.1. Imported by nothing; `lakefile.toml` adds it to the roots of `TaxKernelGlobal`. All 201 country projects under global/ rebuilt with nothing recompiled and byte-identical output, adapter check on 32 PIT models unchanged (global/kcheck21/). Added only.
* 2.1.1 (2026-11-21, R5 MA request): `TaxKernel.Global2.TransferX` (what a gift or inheritance is made of, read from the transfer record: `assetKind`, `realPropertyValue`; `realPropertyPart`, `Transfer.restrict`, `PartDuty`), imported by `TaxKernel.Global2`; §4e.1. Checked on every country project under global/ (global/kcheck21/compat_211.json). Added only.
* 2.2.0 (2026-11-21, Europe builder's bug report): `computeGlobal` books no 1.x PIT charge (and no 1.x benefits) for a company-only entity (`CanonGlobal.companyOnly`, `pitChargesFor`; theorems `computeGlobal_companyOnly`, `computeGlobal_household_charges`, `computeGlobal_household_benefits`, `ofCanon_charges`; `adapter_charges` now assumes `companyOnly = false`). Company-only outputs lose a spurious charge; every other output is byte-identical (global/kcheck21/compat_22.json).
* 2.3.0 (2026-11-21, KERNEL_REQUESTS.md R-FT2-1 and R1 Europe pass 4): `computeGlobal` drops withholding placeholders (a payment no rule matches) and lists every payment abroad no withheld charge computes in `unsupported` as `"1200 withholding on payment <i> (<kind>) abroad: no rule read (grade C)"` (company entities; `WhtRead`, `rawCharges`); cited statutory zeros `WhtRule.zero`, `Wht.zeroOn`, `Wht.family`; `CorpRegime.smallEmployees` (employee limit of the small-company test, default −1 = none). Totals and every household output unchanged; theorem statements narrowed: `computeGlobal_household_charges`, `withFamily_charges`, `computeGlobal_companyOnly`, `withFamily_total` (§4e.2). Checked on all 201 projects (global/kcheck23/compat23.json): only company lines with payments abroad changed, as specified.
* 2.4.0 (2026-11-21, KERNEL_REQUESTS.md R1 Europe pass 7, R3-S4-1, R1 Europe pass 8; floor area): `TaxKernel.Global2` gains `Assets` (`"areaM2"` as the canonical floor-area field, `assetAreaM2`, `QtyTable`, `AreaTax`), `Vehicle` (the vehicle record on vehicle assets and `company.vehicles`; `VehicleTax`, `vehicleTaxFamily`, `vehicleTaxUnknown`), `WhtState` (recipient state and flags on payments abroad; `StateRule` with a required `ifUnknown`, `StateWht`), and `ExciseRule` price tiers (`minUnitPrice`, `maxUnitPrice`, `priceQty`, `priceDen`, `priceBase`; defaults select as before), §4e.3. No 2.0-2.3 module changed. All 201 projects byte-identical (global/kcheck24/compat24.json). Added only.
* 2.5.0 (2026-11-21, KERNEL_REQUESTS.md R4-13-1, R1 Europe pass 9, R2-P9-1; MENA pass 3k): `TaxKernel.Global2` gains `Stack` (income stacked on the 1.x income tax: `StackRule` with gains by asset kind through a `GainRule`, income items, annual exclusion per person or household, inclusion rate, `into : StackField` with no default; `stackCharges`, `stackUnknown`, `GlobalModel.withStack`; the 1.x line unchanged, grade C when a slice cannot be priced) and `Sector` (canonical `company.sector`, `SectorCorp` with a required `ifAbsent`); `Vehicle` gains `"euroClass"` (`.euroClass`, `.euroStage`, `euroStageOf`) and `"listPrice"` (`.listPrice`), and `when` ranges an open upper bound (`hi < 0`, `VehicleTax.noBound`), §4e.4. No 2.0-2.3 module changed. All 201 projects byte-identical (global/kcheck25/compat25.json). Added only.
* 2.6.0 (2026-11-21, KERNEL_REQUESTS.md FT reviewer 6, R1 Europe pass 10, R4-14-1, K26-PK): `Vehicle` gains `"firstRegMonth"` / `"firstRegDate"` (`.firstRegMonth`, `.firstRegDay`) and `VehicleTax.regFromDate` / `regToDate` (a first-registration date window; undecided = grade C); `StackRule` gains `shareBp` and `mode := .marginal | .averageRate key` (half the global rate: LU art. 131 (1) c); new `Global2.Employer` (employer facts on household adults, `EmployerLevy`) and `Global2.Advance` (`AdvanceTax`, `advanceTaxFamily`: advance income tax credited against the year's income tax), §4e.5. New fields default to 2.5.0; no 2.0-2.3 module changed. All 201 projects byte-identical (global/kcheck26/compat26.json). Added only.
* 2.7.0 (2026-11-21, KERNEL_REQUESTS.md R4-17-1, R1 Europe pass 15, FT reviewer 7, R4-18-1/2/3): new `Global2.Fx` (foreign-currency amounts at a declared rate: entity `"fxRates"` or a rule's `FxRate`; none = grade C) and `Global2.Zone` (`"zoneValueM2"`, `"buildYear"`, `"floor"`, `"frontages"`, `ZoneTax`); `VehicleTax` gains `currency`/`fxRate`, `proRataDays`/`dayPeriods` (with `"heldFrom"`/`"heldTo"`) and `partWindows`; `StackRule` gains `dateFrom`/`dateTo`, `rateFromStack` and `electFlatBp`; `EmployerFacts.turnover` with `.turnoverAtLeast/.turnoverBelow`; `SectorCorp.outside`, §4e.6. New fields default to 2.6.0; no 2.0-2.3 module changed. All 201 projects byte-identical (global/kcheck27/compat27.json). Added only.
* 2.8.0 (2026-11-21, full-coverage gap closing: customs and local rates; KERNEL_REQUESTS.md K28-CUSTOMS, K28-LOCAL, R1 Europe pass 17): new `Global2.Customs` (basket-line `"hs"`, `"origin"`, `"customsValue"`; `TariffRule` with MFN lines by HS heading (longest prefix), specific duties, origin preferences, the duty in the VAT base; `GlobalModel.withCustoms`) and `Global2.LocalRate` (entity `"localRates"`; `LocalTax` with the national base, reliefs and range, a declared default municipality rate, framework-only notes; `GlobalModel.withLocalTaxes`); `StackRule.undatedIfTaxable`, `ZoneTax.coefsAt`, §4e.7. New fields default to 2.7.0; no 2.0-2.3 module changed. All 201 projects byte-identical (global/kcheck28/compat28.json). Added only.
* 2.9.0 (2026-11-22, KERNEL_REQUESTS.md R3-GAP-1, R2-GAP-1, R3-GAP-2, K29-LEASE, K29-MFRVALUE, K29-CUSTOMS-FX): new `Global2.Zakat` (adult `"religion"` / `"zakatLiable"` / `"zakatExemptDeclared"`, company `"muslimOwnershipBp"`; `ZakatRule`: 2.5 % above a declared nisab, presumption only when declared, else grade C; `GlobalModel.withZakat`), `Global2.GoodsValue` (basket-line `"containerMl"`, `"exFactoryValue"`; `GoodsValueTax`: rates or marginal value bands per container or per litre on the price, the value before the tax, the customs or the manufacturer's value; `GlobalModel.withGoodsValueTaxes`), `Global2.Lease` (the tenant's nationality and residence on a let asset or a rent line; `RentLevy`; `GlobalModel.withRentLevies`); `Customs`: date windows on tariff lines and preferences, `TariffSurcharge` by origin added to the duty, specific duties in a foreign currency, §4e.8. New fields default to 2.8.0 (`TariffRule.outcome_v28`); no 2.0-2.3 module changed. All 201 projects byte-identical (global/kcheck29/compat29.json). Added only.
