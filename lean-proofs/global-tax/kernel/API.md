# TaxKernel API (v1.4.0, 2026-11-20): the shared kernel of the 20- and 38-country comparisons

Owner: kernel agent. **Stable**: names and signatures below will not change; new parts and theorems are only
added (listed under "Changes" at the end). Source: `~/cmp20/kernel/TaxKernel/*.lean` (read the file docstrings for
the details and the statutes each example comes from). Lean 4.35 core only.

**Status (live; see `PROGRESS.md`)**: 1.4.0 (2026-11-20) adds `TaxKernel.World2` (column tariffs, coefficient-indexed amounts; §4d) and world reference wages in the harness (§7c). 1.3.0 (2026-11-20) adds `TaxKernel.World` for the world expansion (§4c; import it explicitly; the 38 unchanged). 1.2 (2026-11-19) adds the parts for the 38 (§4b) and the harness and referees for all 38 (§7b: your exe is found automatically; OECD check for the 13 members, Eurostat sanity check for BG HR CY MT RO). Earlier: §1-§5 built, tested and proved (no `sorry`; every §5 theorem is instantiated
for the toy country in `examples/zz/lean/ZzTax/Theorems.lean`: copy from there). §7 harness: `tax20`, `run20.py`,
`oecd_check20.py` and the generic scanners (`harness/search/run_all.py`) work on all 20 exes; first-pass scanner
leads per country are in `~/cmp20/kernel/LEADS.md` (check them against your statute; rerun on your current exe).

## 1. Depend on it (tested with the toy country `~/cmp20/kernel/examples/zz/lean`)

Your project `~/cmp20/<owner>/<cc>/lean/`:

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
path = "../../../kernel"        # from ~/cmp20/<owner>/<cc>/lean

[[lean_lib]]
name = "CaTax"

[[lean_exe]]
name = "catax"
root = "CaTax.Main"
```

Then `export PATH=$HOME/.elan/bin:$PATH; lake build`. The exe lands in `.lake/build/bin/<cc>tax`, where the harness
finds it automatically (`~/cmp20/harness/tax20.py`). The kernel's oleans live in `~/cmp20/kernel/.lake/build`; the
kernel owner rebuilds after every change, so your build only reads them. If your build ever reports a TaxKernel
file changed underneath it, run `lake build` again.

## 2. The exe speaks the contract

```lean
def country : TaxKernel.Country :=
  { code := "CA", name := "Canada (federal + Ontario)", currency := "CAD", year := "2025", compute := out }
-- options from the command line (e.g. `--separate`) reach `computeWith args c` (defaults to `compute c`)
```

`TaxKernel.countryMain country args` reads canonical households (JSONL, `~/cmp/shared/CONTRACT.md`) from stdin and
writes one output line each, same order; a bad line gives `{"id":…,"error":…}`; `--version` prints a JSON line
with country, currency, year and kernel version; `--help` the usage.

Input: `TaxKernel.Canon` (copied from `~/cmp/compare/lean/Compare/Canon.lean`, namespace `TaxKernel`):
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

Everything in §4 is unchanged; these are added. Toy calls of each, checked by `#guard`: `~/cmp20/kernel/examples/Parts38.lean`
(`cd ~/cmp20/kernel && lake env lean examples/Parts38.lean`). Read the module docstrings for the statutes each one is for.

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
(`~/cmp20/world/kcheck/check38.log`, 2026-11-20): every one builds and its output on a fixed 44-household grid is
byte-identical to the live exe. World models call **`TaxKernel.worldMain country args`** (`countryMain` with kernel
1.3.0 under `--version`). Toy calls checked by `#guard`: `~/cmp20/kernel/examples/World.lean`
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
(`~/cmp20/world/kcheck/check_all.sh`, log `check_all.log`). Toy calls: `examples/World2.lean`; axioms:
`audit/AxiomsWorld2.lean` (no `sorry`). Asked for in `world/KERNEL_REQUESTS.md` (B02-g20).

| Part | Names | For (check your own statute) |
|---|---|---|
| Column tariff (band set chosen by the size of the whole income) | `pickColumn cols dflt x` (first column whose limit is ≥ `x`, else `dflt`), `columnTicks cols dflt x`, `columnJumps cols dflt` (the jump at each column limit beyond the marginal rate: computable, check with `#guard`) | EG Law 91/2005 art. 8 as replaced by Law 7/2024 (six columns by total net income); any tariff whose lower bands are withdrawn above an income limit. `pickColumn_succ`, `columnTicks_succ`: away from the limits the marginal rate is the chosen schedule's band rate, so **every notch sits at a column limit** |
| Amounts indexed by a published coefficient | `indexAmount m num den base` (base × num/den, rounded by `m`), `indexChain m [(num, den), …] base` (successive adjustments, rounded at each step), `Schedule.indexed s m num den` (thresholds indexed, rates kept), `indexReproduces m num den [(base, printed), …] tol` (one coefficient explains a published table) | AR Ley 27.743 arts. 30 and 94 (IPC coefficient, January and July); any CPI-uprating rule. `indexed_rates`, `indexAmount_mono` |

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
`~/cmp20/kernel/INBOX.md`, one line, your folder name first).

## 6. How to model a country in 1 hour (the recipe)

1. Copy `~/cmp20/kernel/examples/zz/lean` to `~/cmp20/<owner>/<cc>/lean`, rename `ZzTax`/`zztax` to `<CC>Tax`/`<cc>tax`,
   set `path = "../../../kernel"` in `lakefile.toml`, `lake build` (works before you change anything).
2. `Params.lean`: every number with its citation (`/-- ITA s. 117(2)(a): "15% of the amount taxable" … -/`).
3. Map the household: who is a taxpayer (`c.adults`), how investment income is split (`half1`/`half2`), which
   children count (`c.childrenUnder 18`).
4. Compose: income measure → `Taper`/`taxableAfter` (allowances) → `Schedule.tax` (rates, with the statute's
   `Rule`) → `applyCredits` (offsets) → `Surcharge` (levies) → `Contribution` (social) → `Out.make`.
   Unit of assessment: compute each spouse alone, or `splitting`/`quotient` the per-person function.
5. Run the toy grid: `python3 ~/cmp20/harness/tax20.py --countries <CC> --demo` and the OECD check
   `python3 ~/cmp20/harness/oecd_check20.py <CC>`; fix until the OECD lines match or you can say why not.
6. `Theorems.lean`: the one-liners of §5 for each schedule/taper/credit you used.
7. Run the generic scanners: `python3 ~/cmp20/harness/search/run_all.py <CC>` (results in
   `~/cmp20/<owner>/<cc>/results/search/`), then read the summary for findings to check against the statute.

## 7. Harness (for country agents)

* `~/cmp20/harness/tax20 '{"adults":[{"wages":1.0}]}'`: one household, every country (amounts in average wages by
  default; `--units ppp` USD at OECD PPP; `--units local`; `--countries CA,UK`; `--json`; `--demo`), local currency
  + USD PPP. Countries not built yet are listed as such.
* `python3 ~/cmp20/harness/run20.py --countries CA|all|built|new --grid grid.jsonl [--units local|aw|ppp] [--frozen]
  [--out DIR]`: run a JSONL grid through any subset of the 20; `--frozen` copies each exe first so a rebuild cannot
  change a run. Elections (choices the law leaves to the taxpayer) are made cheapest-first from
  `~/cmp20/<owner>/<cc>/elections.json` (format in `harness/common20.py`).
* `python3 ~/cmp20/harness/oecd_check20.py CA [--out ~/cmp20/anglo/ca/results] [--quiet]`: the eight OECD Taxing
  Wages family types at the OECD's 2025 average wage through `catax`, line by line against the OECD's published
  country table (exact = within 1 unit; within 1 %), and a ready `validation` entry for summary.json. Default
  mapping: incomeTax + all surtaxes = CGITFP, localIncomeTax = SLT, employeeSocial = EECSSC, benefits = CTGG,
  `detail.taxableIncome` = CGTC, `detail.taxBeforeCredits` = CGITLETC. If your country books an item on another
  OECD line, write `def map_<cc>(row): return {...}` in `~/cmp20/<owner>/<cc>/oecd_map.py` (found automatically;
  examples for DE/JP/UK in `~/cmp/compare/harness/oecd_maps.py`). Regression on the five (take-home pay within
  1 %): UK 8/8, DE 8/8, US 8/8, JP 7/8, FR 6/8.
* OECD data for all 20: `~/cmp20/harness/data/oecd/tw_cou_xdc.json` (`[ISO3][year][type][measure]`, national
  currency, 2022-2025), `tw_cou_pct.json` (rates), raw CSVs `tw_cou_20.csv`, `tw_comp_20.csv`, `tw_decomp_20.csv`
  (marginal-rate decomposition). The five-country values are reproduced exactly (3,520 of 3,520).
* Params: `~/cmp20/harness/data/params.json` (AW, OECD PPP, World Bank PPP and FX for all 20).
* Owner-manager: `python3 ~/cmp20/harness/search/owner.py <CC>` with the company side in `harness/search/company.json`
  (add or correct your country's entry with citations; `dividend_routing` / `household_extra` tell the scan how your exe
  reads an owner's dividend).
* Generic scanners: `python3 ~/cmp20/harness/search/run_all.py <CC> [--out DIR]` (see `harness/search/README.md`);
  per-country leads: `~/cmp20/kernel/LEADS.md`; everything kernel-side at once: `~/cmp20/report/refresh_all.sh`.

## 7b. Harness and referees for the 38 (2026-11-19)

* **Discovery**: `common20.py` knows all 38 (`OWNERS38`: germanic AT CH LU BE, baltic FI IS EE LV LT, central SK SI HU
  HR, southeast GR CY MT BG RO). An exe at `~/cmp20/<family>/<cc>/lean/.lake/build/bin/<cc>tax` is used as soon as it
  is built by `tax20`, `run20.py`, the scanners and the report. Selectors for `--countries` / `tax20 --countries`:
  `all` (38), `built`, `new38` (the 18), `twenty`, a family name (`germanic`, `baltic`, `central`, `southeast`), or a
  comma list. Elections: `~/cmp20/<family>/<cc>/elections.json` (format in `common20.py`), as before.
* **Params** (`harness/data/params.json`, built by `harness/fetch_oecd38.py`): AW, PPP and FX for all 38. The 13 OECD
  members: AW and PPP from Taxing Wages 2026 (year 2025) exactly as for the 20. BG HR CY MT RO: `aw` is Eurostat's
  gross earnings of the single person at 100 % AW (earn_nt_net, GRS, NAC, 2025; `aw_source`), `ppp_oecd` is the World
  Bank GDP PPP (`ppp_source`). Currencies: BGN for Bulgaria (2025 is before the euro), RON for Romania, EUR for HR CY MT.
* **OECD referee (13 members: AT BE CH EE FI GR HU IS LT LU LV SI SK)**: the eight Taxing Wages family types for 2025 are
  in `harness/data/oecd/tw_cou_xdc.json` (raw CSV `tw_cou_13.csv`, `tw_comp_13.csv`). Run
  `python3 ~/cmp20/harness/oecd_check38.py <CC>` (same as `oecd_check20.py <CC>`: same households, lines, mapping via
  your `oecd_map.py`, output in `harness/runs/oecd20/`).
* **Eurostat referee (all EU members, the only published household-level referee for BG HR CY MT RO)**:
  `python3 ~/cmp20/harness/oecd_check38.py <CC> --referee eurostat` (or `--referee both`), output in
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
* **Scanners and owner-manager**: unchanged commands (`python3 ~/cmp20/harness/search/run_all.py <CC>`); the
  owner-manager scan needs your country's company side in `harness/search/company.json` (the kernel owner adds the 18
  with citations; send corrections to `~/cmp20/kernel/INBOX.md`).

## 7c. Harness for world countries (2026-11-20)

* `common20.py` finds world exes (`~/cmp20/world/<batch>/<cc>/lean/.lake/build/bin/<cc>tax`); selectors `world`, a batch id
  (`B01-oecd5`, case-insensitive), `everything` (38 + world), and comma lists mixing codes and selectors. `all` is still the 38.
* **Scale ("AW") for a world country = its reference wage** from `~/cmp20/world/data/refwage.json` (or
  `world/<batch>/<cc>/scale.json`, which wins): a minimum-wage multiple, a reference wage the statute uses, or a statutory
  threshold, each with its source; **never an OECD/Eurostat/referee value** (CONTRACTWORLD testing order). `common20.WORLD_SCALE`
  holds the entries. No PPP for world countries (NaN): `--units ppp` is unavailable for them.
* Generic scanners: `python3 ~/cmp20/world/tools/scan_world.py B01-oecd5 B02-g20 [--full]` (or `harness/search/run_all.py CC`);
  results go to `~/cmp20/world/<batch>/<cc>/results/search/` by default. The owner-manager scan is skipped without a company
  side in `harness/search/company.json`.

## Changes
* 1.0 (2026-11-19): first publication.
* 1.0.1: theorems of §5 proved (no `sorry`); harness tax20/run20/oecd_check20 and OECD data for all 20.
* 1.0.2: optional input field `cohabiting` (§2); LEADS.md; refresh_all.sh. No signature changed.
* 1.1: `TaxKernel.Table` (lookup tables with decidable checks against a formula; `perPeriod`), asked for in the KR and MX kernel gaps. Added only.
* 1.2 (2026-11-19, for the 38): `TaxKernel.Multiplier` (multipliers on a base tax, tax at an average rate, rate splitting with a divisor, credit allocation over several taxes) `TaxKernel.Family` (child scales, income attribution between spouses, low-band allowance, allowance spilling into another levy, stepped taper, reduced contribution base) and `TaxKernel.Tariff` (tariffs printed as columns or as rate-minus-subtraction, with checks against the bands), theorems in `TaxKernel/Theorems/Parts38.lean` (§4b); harness and referees for the 38 (§7b). Added only: no name or signature of 1.1 changed.
* 1.2.1 (2026-11-19): `TaxKernel.Extra38` for the gaps the 18 reported (SK half-up taper, HU capped spill, BE exempt sum on its own tariff, mid-year parameters, AT rate by size of base). Added only.
* 1.3.0 (2026-11-20, world expansion, ~/cmp20/world/CONTRACTWORLD.md): `TaxKernel.World` (indexed units, schedular systems with an annual overlay, zakat, territorial base and the optional `foreignIncome` field, exemption written as a tax, cumulative withholding, `worldMain`), §4c. Not imported by the root module: the 38 rebuilt unchanged (byte-identical output). Added only.
* 1.4.0 (2026-11-20, world/KERNEL_REQUESTS.md): `TaxKernel.World2` (column tariff chosen by the size of the whole income with the notch-location theorem; amounts indexed by a published coefficient), §4d; harness reference wages for world countries (§7c). Not imported by any earlier module: all 49 kernel-built models rebuilt unchanged (byte-identical). Added only.
