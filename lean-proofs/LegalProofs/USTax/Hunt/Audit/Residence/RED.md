# Red team: Residence, candidates 1 and 2 (expatriate and stay; covered on purpose)

Target: `LegalProofs/USTax/Hunt/Residence.lean`, `Residence.FINDINGS.md`, `tools/hunt/out/Residence/`.
Claim: (1) a long-term green-card holder gives up the card as a covered expatriate and stays a US resident under the
day count: gain tax $26,180 instead of $238,000, 730/730 US days; (2) a person below the wealth and tax tests declines
the §877(a)(2)(C) certification to be covered on purpose: $26,180 instead of $200,000 on US realty sold as a nonresident.

**Verdict: holds on the text. The dollar figure is gross, not net.** The mechanism is in the statute and is confirmed
by Notice 2009-85 Example 3; it is not circular and not a search artifact. The $211,820 gain is the ceiling
(exclusion × 23.8%) and ignores what covered status costs for the rest of the person's life (§2801), which on this
asset alone is $592,400 and turns both plans negative if the wealth later goes to US persons from outside US domicile.

How the copy was made: `gen_red.py` reads the original (never edited), takes its Rules part verbatim and applies
exact-string patches that add switches, all off by default (`fixA`, `fixC`, `pre2008`, `noSeg0Exit`, `ira`,
`exclusion`) and four bookkeeping fields (`exitYr`, `exclAmt`, `resAfter`, `exits`). With every switch off the copy
reproduces the recorded figures (T0). Files: `RedSearch.lean/.out`, `RedSearch2.lean/.out`, `RedSearch3.lean/.out`,
`RedKernel.lean/.out`, `RedInduct.lean/.out`, `red_arith.py/.out`. 39 searches, 1,766,305 positions, 262,401
finished plans.

| Test | Result | One line |
|---|---|---|
| T1 text fidelity | partial | Rule matches the words; six omissions, all costs; plan survives the strict re-run at $26,180 |
| T2 close the gap | partial | One edit kills plan 1 and leaves the baseline; it does not kill plan 2, which needs a second edit |
| T3 ablation | pass | Without `abandon` the result is $238,000; three moves alone reproduce $26,180 |
| T4 earlier law | pass | Pre-2008 text: nothing below $238,000 at 730 days |
| T5 free lunch | pass | 0 invariant violations in 1.77 million positions |
| T6 kernel | pass | 23 replays and bounded universals by `decide +kernel`; one unbounded induction; no `sorryAx`, no `ofReduceBool` |
| T7 arithmetic | pass | Python from the statute: 238,000 / 26,180 / 200,000 / 26,180 |
| T8 outside the statute | partial | Nothing closes it; nothing found that describes it; §2801 regulations narrow the "resident" switch-off |

## T0 Reproduction (copy, all switches off)

| Scenario | baseline | best, 730 US days | covered, resident the year after | covered leaver | non-covered |
|---|---|---|---|---|---|
| green card 9th year, covered, domestic stock | 238,000 | 26,180 | 26,180 | 26,180 | n/a |
| green card 9th year, not covered, US realty | 238,000 | 26,180 | 26,180 | 26,180 | 200,000 |
| green card 9th year, not covered, domestic stock | 238,000 | 26,180 | 26,180 | 26,180 | 0 |
| citizen, covered, domestic stock | 238,000 | 26,180 | 26,180 | 26,180 | n/a |

Same as the recorded outputs E, M2, M3, D.

## T1 Text fidelity: partial

Read against `sec.py 877A`, `877`, `7701 b 6`, `2801`.

What the encoding gets right (checked word by word):
* §877A(a)(1) "All property of a covered expatriate shall be treated as sold on the day before the expatriation
  date": `exitTax` taxes the gain at 23.8% while the person is still a resident. Correct.
* §877A(a)(3)(A) "shall be reduced (but not below zero) by $600,000" (indexed; $890,000 for 2025 per the 2025 Form 8854
  instructions): `gainLeft - min gainLeft exitExclusion`. Correct.
* §877A(a)(2) flush: "Proper adjustment shall be made in the amount of any gain or loss subsequently realized for gain
  or loss taken into account under the preceding sentence, determined without regard to paragraph (3)":
  `gainLeft := 0`. Correct; Notice 2009-85 §3.C and Example 3 give the same result (basis $200,000 "adjusted by
  $1,800,000 ... resulting in a basis of $2,000,000").
* §877A(g)(2)(B), (g)(3)(B): an expatriate is a long-term resident who "ceases to be a lawful permanent resident ...
  (within the meaning of section 7701(b)(6))". No word requires ceasing to be a resident. §877A(g)(1)(C) speaks of a
  "covered expatriate who is subject to tax as a citizen or resident ... for any period beginning after the
  expatriation date" and removes only (d)(1), (f) and §2801 for that period, not (a). Correct.
* §877(e)(2): 8 of 15 taxable years. `lprYears + 1 ≥ 8`. Correct (run: a 7th-year holder is not an expatriate in
  year 0 and is in year 1).
* §877(a)(2)(C): "fails to certify under penalty of perjury ... or fails to submit such evidence": `!certify` makes
  the person covered whatever the net worth. Correct on the words. Form 8854 instructions (2025): covered if "You fail
  to certify on Form 8854 that you have complied with all federal tax obligations".

Divergences, each more generous than the words or the real position:

1. **§2801 is undercounted (worst).** The model charges §2801 only on the `giftUS` move while the tax home is abroad;
   death is not a move and the search horizon is 2 years. In the statute, covered status never ends (§2801(e)(1),
   (f)); the only relief is §877A(g)(1)(C) "during such period". Reg. §28.2801-2(b), (h) (T.D. 10027, 2025) read
   "resident" for this purpose as resident for chapter 11/12, that is domicile, not the §7701(b) day count. So:
   * a stayer who is domiciled in the US pays nothing under §2801 while that lasts, but is locked in: leave later and
     every gift or bequest to a US person above $19,000 a year is taxed at 40% on the recipient, with no unified
     credit. On this asset alone: 40% × (1,500,000 − 19,000) = **$592,400**. Plan 1 restated: 26,180 + 592,400 =
     **$618,580** against the $238,000 baseline (net −$380,580). Break-even: $529,550 of covered transfers.
   * a stayer on a nonimmigrant visa is an income-tax resident by day count but may not be domiciled; then §2801
     applies to gifts to US persons even while the person is in the US. The original's line "(g)(1)(C) ... switches
     off §2801" is too generous for exactly the people who can run plan 1.
   * plan 2's leaver is outside the US at once: 26,180 + 592,400 = **$618,580** against $200,000 certified
     (net −$418,580). Break-even: $434,550 of covered transfers.
   Re-run with the charge added at the end of the horizon for a covered expatriate with the tax home abroad
   (`RedSearch2.out`, "H"): stayer 26,180; covered and abroad at the end 618,580.
2. **§877A(e)(1), (d)(2) missing.** IRAs, HSAs, 529s are treated as distributed in full the day before; non-eligible
   deferred compensation is accelerated. Re-run with a $500,000 IRA at 35%: plan 1 = **$201,180** (still under
   238,000). The acceleration equals the whole saving at an IRA of $605,200. The original mentions this in prose but
   the $26,180 figure does not carry it.
3. **Day-before rule and the year of the exclusion.** The printed plan abandons on 1 January of year 0, so the deemed
   sale falls on 31 December of the previous year: the tax belongs to that year and the exclusion is that year's
   ($866,000 for 2024 gives **$31,892**). With expatriation on 1 January forbidden the search moves the act to day 31
   and returns $26,180 again (`T1 plan1 strict`). Survives.
4. **One asset.** The exclusion is allocated across all gain property (Notice 2009-85 §3.B) and everything else is
   marked too. Total benefit is unchanged but capped: $890,000 × 23.8% = $211,820 per person per lifetime ("only one
   lifetime exclusion amount"). A covered person under the net-worth test has at least $500,000 of other property
   here; the model taxes none of it.
5. **`abandon` is free and unconditional.** §7701(b)(6)(B) needs the status "revoked" or "administratively or
   judicially determined to have been abandoned". Staying in the US afterwards needs a new immigration status whose
   days count (not A, G, F, J, which are exempt days under §7701(b)(5)). That is outside the tax code and outside the
   model; the plan stands or falls on it. The move was not added for this plan (plans 10 and 11 use it), so this is
   an omitted precondition, not circularity.
6. **Flat rates, no state tax, no growth.** Immaterial to the mechanism.

Not a divergence: Notice 2009-85 §3.D excludes US real property interests from the arrival-date step-up of
§877A(h)(2). That is a different rule; the (a)(2) adjustment after the deemed sale applies to realty (plan 2).

Fields or moves that exist only for this plan: none found. `covExpat` is read only by `giftTransfer`.

## T2 Close the gap: partial

**Fix A** (words added to §877A(a)(3)): "This paragraph shall not apply to an individual who is a resident of the
United States (within the meaning of section 7701(b)(1)(A)) for the calendar year following the calendar year that
includes the expatriation date." Encoded as a recapture of 23.8% × the excluded amount when that year is settled.

| | original | fix A |
|---|---|---|
| baseline | 238,000 | 238,000 |
| covered expatriate, resident the year after | 26,180 | **238,000** |
| covered expatriate, leaver | 26,180 | 26,180 |
| visa holder, all figures | unchanged | unchanged |

Plan 1 disappears, baseline and the lawful leaver do not move. Two things survive fix A:
* the model still shows $26,180 at 730/730 days by expatriating on 1 January of the **last** year. That is the
  horizon assumption (absent after the horizon), i.e. a leaver who goes one year later, not a stayer. Kernel-checked
  (`fixA_last_year_exit_whole`, `fixA_full_only_last_year_whole`).
* **plan 2 for a leaver survives fix A** ($26,180; `fixA_plan2_leaver_survives`). The brief's natural fix does not
  close candidate 2. The gain there comes from §877(a)(2)(C) being elective, not from staying.

**Fix C** (words added to §877A(a)(3)): "This paragraph shall not apply to an individual who is a covered expatriate
solely by reason of section 877(a)(2)(C)." Plan 2: uncertified 238,000, certified 200,000, baseline 238,000.

## T3 Ablation: pass

Plan 1 (green card 9th year, covered, domestic stock):

| Moves removed | best at 730 days | note |
|---|---|---|
| none | 26,180 | |
| `abandon` | 238,000 | plan gone |
| `present` | no 730-day plan | best overall 26,180 as a leaver |
| `sell` | no finished plan | needed only because the search counts plans with the asset disposed of; the taxed event is the deemed sale |
| `relocate` | 26,180 | decoration (the two RELOCATEs in the printed plan cancel) |
| all but `present`, `sell`, `abandon true` | 26,180 | 175 positions |

Plan 2 (not covered, US realty): without `abandon false` the best is 200,000 (certified leaver) and 238,000 at 730
days; with only `present`, `sell`, `abandon false` it is 26,180.

## T4 Earlier law: pass

`pre2008`: no §877A; a covered expatriate who is a nonresident pays the greater of the §871 tax and the §877(b) tax.
Plan 1: 730-day best 238,000; covered leaver 200,000 (the known 10-year regime on domestic stock). Plan 2: 238,000 /
200,000. Nothing below the baseline that was not the law then. Limit: my earlier-law encoding leaves out the §877(g)
30-day rule and the pre-2004 motive test; both only raise tax.

## T5 Free lunch: pass

Invariants checked at every position of all 39 searches (1,766,305 positions): gain left + gain sold ≤ built-in gain;
tax on the gain ≤ all US tax; at most one expatriation; excluded gain ≤ the exclusion. **0 violations.**
* In the US every day and nothing given up: never below 238,000 (student: 300,000) without gifts.
* Tax on salary and dividends for every 730-day plan: at least 209,994 in every run (no leak into ordinary income).
* Gain $0: tax 0. Gain $500,000: tax 0 after the exit (exclusion covers it; consistent with the text). Gain
  $5,000,000: 978,180 = 23.8% × 4,110,000.
* Highest tax on the gain: 300,000 (§871(a)(2)); with gifts 830,400 = gift tax 592,400 + donee 238,000 (two taxes on
  two events, not a double count).
* With gifts on, $0 at 730 days appears: gift to a nonresident alien who sells (original plan 13, uses the unified
  credit). Known, not absurd.

## T6 Kernel: pass

`RedKernel.lean`: 23 theorems by `decide +kernel`, each `#print axioms` = `[propext, Quot.sound]`. Replays through
the full `step` function on the coarse grid: baseline 238,000; plan 1 = 26,180 at 730 days with `covExpat`,
`resAfter`, not LPR; plan 1 with the act on day 31; plan 2 = 26,180; certified 238,000 (stayer) / 200,000 (leaver);
fix A → 238,000; fix A leaver 26,180; fix C → 238,000; pre-2008 → 238,000.
Bounded universal (cut down: whole-year grid, 2 years, 6 moves, every sequence, no deduplication; the theorem also
proves every leaf is at the horizon): under fix A no finished plan by a covered expatriate resident the year after
pays less than 238,000; under the original rules one pays 26,180; under pre-2008 none at 730 days is below 238,000.
`RedInduct.lean`: `all_sequences`, by induction on the move list, for every parameter set and every start that is
not citizen and green-card holder at once: the excluded gain never exceeds the exclusion and the untaxed gain never
grows. Axioms `[propext, Quot.sound]`.
Not done: the closed-gap statement over all sequences on the 3- and 5-segment grids is checked by `#eval` search
only, not by the kernel.

## T7 Independent arithmetic: pass

`red_arith.py` (rates and rules taken from the statute text): baseline 238,000; plan 1 exit tax 26,180, basis after
1,500,000, later sale 0; plan 2 certified leaver 200,000, uncertified 26,180. All agree. Restatements: 2024
exclusion 31,892; 2026 exclusion ($910,000) 21,420; §2801 592,400; with $500,000 IRA 201,180.

## T8 Outside the statute: partial (8 searches)

| Source | Effect | Passage |
|---|---|---|
| Notice 2009-85 §3.C, Example 3 (IRB 2009-45), https://www.irs.gov/irb/2009-45_IRB | supports | basis adjusted "without regard to the exclusion amount provided in section 877A(a)(3)"; "A's basis of $200,000 in Asset X is adjusted by $1,800,000 ... resulting in a basis of $2,000,000" |
| Notice 2009-85 §3.B | limits | "Each individual is eligible for only one lifetime exclusion amount"; exclusion "must be allocated among all built-in gain property" |
| Notice 2009-85 §5.F | silent on (a) | (g)(1)(C) discussed only for the 30% withholding on deferred compensation |
| Form 8854 instructions (2025), https://www.irs.gov/instructions/i8854 | supports | "You fail to certify on Form 8854 that you have complied with all federal tax obligations"; "For 2025 ... reduced (but not below zero) by $890,000"; LPR status ends on "the date you voluntarily abandoned your lawful permanent resident status by filing" Form I-407 |
| T.D. 10027, Reg. §28.2801-2(b), (h), 90 FR 3376, https://www.govinfo.gov/content/pkg/FR-2025-01-14/html/2025-00284.htm | narrows | resident is "for purposes of chapter 11 or 12 of subtitle B"; covered "at all times after the expatriation date" except while "subject to United States estate or gift tax ... as a U.S. citizen or resident"; preamble: the transfer-tax definition "avoids creating an opportunity to circumvent the section 2801 tax" |
| Hodgen, "When Covered Expatriates Come Back" (2017), https://hodgen.com/articles/covered-expatriates-come-back | describes (g)(1)(C) for returners, not the plan | "Leaving the United States again, of course, will cause covered expatriate status to resume." |
| Mondaq, "New guidance on expatriation exit tax" (2009), https://www.mondaq.com/unitedstates/tax-authorities/89228/new-guidance-on-expatriation-exit-tax | describes the step-up | basis rises by the deemed gain without the exclusion; of value mainly for US real estate (search summary, page not fetched) |

Found nothing that closes either plan, and nothing that describes giving up the card while staying resident or
declining the certification on purpose. Eight searches is not proof of novelty.
Not retrieved: Reg. §301.7701(b)-1(b) (when abandonment is effective); Notice 2009-85 §§6–9; the full sentence of
Reg. §28.2801-2(h) (fragments only); Form 8854 PDF (the HTML page was used); JCT explanation of the HEART Act;
immigration rules on filing Form I-407 from inside the US.

## Weaknesses, ranked

1. **The gain is gross.** Covered status is permanent. §2801 at 40% on anything later passed to US persons from
   outside US domicile ($592,400 on this asset) exceeds the saving ($211,820 plan 1, $173,820 plan 2). Plan 2's
   leaver bears it at once. The original lists §2801 as a remark and its model charges it on one move only.
2. **§2801 "resident" is domicile.** A stayer on a nonimmigrant visa may be an income-tax resident without being
   domiciled; the regulations then leave §2801 on. The original says (g)(1)(C) switches it off.
3. **The plan depends on an immigration fact the model treats as free**: a status that lets the person stay with
   countable days after the card is surrendered.
4. **§877A(d), (e) acceleration is not in the figure**: $201,180 with a $500,000 IRA.
5. **The natural fix does not close plan 2**; a second edit is needed. Plans 1 and 2 are two gaps, not one.
6. **Ceiling**: $211,820 per person per lifetime, shared across all gain property; death gives the same step-up free
   under §1014.
7. **Printed plan's date**: 1 January expatriation puts the deemed sale in the prior year (2024 exclusion: $31,892).
8. **Kernel coverage** of the closed-gap universal is the whole-year grid only.
9. **Fine 5-segment grid not checked.** Two attempts for the green-card holder (all moves; then five moves) hit the
   175 s limit and produced nothing (`RedSearch3.out`: exit 124). Every figure here is on the coarse 3-segment or
   whole-year grid. The original also ran the green-card scenarios on the coarse grid only.
