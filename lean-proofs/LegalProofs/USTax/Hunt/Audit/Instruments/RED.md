# Red team: Instruments, CANDIDATE 1 (capital gain dividend, then a wash sale)

Plan attacked: buy regulated-investment-company shares the day before a capital gain dividend (day 129); on the
ex-date (day 130) sell them and buy the same shares back (wash sale); sell the replacement shares on day 162.
Claim: dividend is long-term gain, the loss comes out short-term, $1,768 saved per $10,000 of dividend.

**Verdict: holds on the text.** I could not make it circular, wrong on the words, or an artifact of the encoding.
What I could show is that it is worth **no more dollars than the already-known "hold past six months"** (both
$1,768), that the original search output never displayed it (it is a hand-written check line), and that it stands
or falls on whether a court lets a same-price sale and repurchase stand.

How it was run: `gen.py` builds each `Red<T>.lean` from the original `Instruments.lean` (rules and search copied
verbatim, then patched with audit knobs that all default to the original behaviour) plus `tail_<T>.lean`. Each was
run with `lake env lean` (7 s to 40 s). Outputs: `out_T*.txt`, `out_Kernel.txt`. Originals untouched.
`RedT0` (all knobs off) reproduces the C2 block of `final.txt`: header, plain-plan tax, family savings and all six
check lines identical. The *displayed* paths differ, see weakness 2.

## T1 Text fidelity: pass

Read against §852(b)(3)(B), (b)(4)(A)–(E), §246(c)(3)–(4), §1091(a)–(d), §1222, §1223(3), Treas. Reg. §1.852-4(d),
§1.1091-1, §1.1091-2, §1.1223-1(d) (statute from `tools/hunt/sec.py`, regulations from eCFR, copies in `sources/`).

Step by step, the words against the code:

| Step | Words | Encoding | Same? |
|---|---|---|---|
| Dividend to the day-129 share | §852(b)(3)(B): long-term gain | `settleDivs`, `.cgd` booked `.lt` | yes |
| Day-130 loss on that share | §852(b)(4)(A): long-term "to the extent of" the dividend, share held 6 months or less | `lossParts`: `heldAtRisk ≤ 183`, counted from `opened`, day of disposition counted, no tacking | yes (§246(c)(3)(A), (B)) |
| That loss is not deductible | §1091(a): substantially identical stock acquired within 30 days before or after | `lossEvent` `prior` branch (or `openLong` `pend`) | yes |
| Replacement basis | §1091(d): basis of the old share ± price difference = 100,000 | `basis := x.basis - amt` = 90,000 + 10,000 | yes |
| Replacement holding period, general | §1223(3): includes the old share's (1 day) → 33 days on day 162, short-term under §1222(2) | `hp := x.hp - held`; `held > 365` test | yes |
| Replacement holding period, §852(b)(4) | §852(b)(4)(C)(i) → §246(c)(3)(B): §1223(3) "shall not apply" → 32 days, "6 months or less" | `heldAtRisk` uses `opened` (day 130) | yes, and irrelevant: see next row |
| Is the replacement "such share"? | (b)(4)(A)(i): an amount treated as long-term gain "with respect to any share"; (ii) "such share"; "sale or exchange of such share". The replacement was bought on the ex-date and received nothing | `lossParts` reads `l.divs` of the lot sold; the replacement's `divs` is empty | yes |
| Character carried by §1091? | §1091(d) is a basis rule; §1223(3) a holding-period rule; neither mentions character | the long-term `parts` are summed into `amt` and discarded | yes: this is the gap, not an invention |
| Day-162 loss allowed | no acquisition within 30 days either side (replacement day 130 is 32 days back, first purchase 33) | `buys` pruned at 30 days | yes |

Divergences found (none carries the plan):

1. More generous than the words: none on the plan's path.
2. Stricter than the words (model artifact against the taxpayer): a loss sale within 30 days of an *earlier, already
   sold* lot's purchase is disallowed and the loss vanishes (check line $45,281; T5 finds 24 final positions where
   $10,000 of loss is destroyed). The exit date 162 = 129 + 33 was placed to clear this rule; on the words the
   exit needs only to be more than 30 days after the replacement purchase.
3. Missing from the statute as encoded: §852(b)(4)(C)(ii) (days more than 6 months after the ex-date not counted);
   §246(c)(4)(A), (B) (options, contracts to sell: no such instruments exist in the model); "6 months" is 183 days;
   wash-sale matching takes the most recent acquisition where §1.1091-1(d) says the earliest; §7701(o) and the
   step-transaction doctrine (not mechanical text).
4. Fields or moves existing only for this plan: none in the rules. In the scenario: the `exDate` date grid
   (129, 130, 131, 162) was built around the plan, and FundA is sold on day 129 at exactly zero gain because the
   price path is flat from the day it was bought.

Strict copy (`strict := true`: adds (C)(ii) and earliest-acquisition matching) and re-run:

| Run | Tax |
|---|---|
| hold FundA | $42,806 |
| PLAN | $41,038 (saves $1,768) |
| sold day 162, no wash sale | $42,806 |
| hold 201 days | $41,038 |
| PLAN with "6 months" = 181 / 184 / 200 / 201 days | $41,038 each (hold 201 days dies at 201: $42,806) |
| day 130 sell into FundA, rebuy GainFund day 131, sell day 162 (no same-day round trip) | $41,038 |
| double up on the ex-date (two units for one day), sell old lot day 131, new lot day 162 | $41,038 |
| PLAN, final sale moved to day 131 | $45,281 (model's strict §1091(a)) |
| PLAN, no other short-term gain | $1,190 = baseline $1,190 (saves $0) |
| PLAN, other short-term gain $5,000 | $4,467 vs $5,351 (saves $884) |
| PLAN, also $50,000 long-term gain each year | $65,314 vs $67,082 (saves $1,768) |

The plan survives the strict reading.

## T2 Close the gap: pass

Words added to §852(b)(4)(A), after "on the sale or exchange of such share": "(or of any stock or securities the
basis of which is determined under section 1091(d) by reference to such share)". Encoded as one field (`taint`)
carried where §1091(d) already carries basis (`taintFix := true`).

| Run | Open | Closed |
|---|---|---|
| hold FundA (baseline) | $42,806 | $42,806 |
| PLAN | $41,038 | **$42,806** |
| day-131 rebuy variant | $41,038 | $42,806 |
| hold 201 days | $41,038 | $41,038 (untouched, as it should be) |
| search, GainFund must be gone on leaving day 162: best saving | $1,768 | $531 (the 3% qualified dividend on DivStock, finding #11; nothing from GainFund) |
| search, unconstrained: best | $1,768 | $1,768 (six-month hold) |
| C1 search: plain / best | $42,806 / $41,038 | same |
| A1 search (wash sales, no dividends): plain / best | $53,516 / $49,789 | same, 52,150 positions both |

The plan disappears, no baseline moves, nothing else changes. The gain comes from where the findings say.

## T3 Ablation: pass

Search with GainFund forced out by day 162 (so the six-month hold cannot substitute); all rules: saves $1,768.

| Removed | Search best | Fixed plan | Verdict |
|---|---|---|---|
| §1091(a) | $531 (DivStock only) | $42,806 | needed |
| §1091(d) basis | $531 | $45,281 | needed |
| §852(b)(3)(B) (dividend ordinary) | $531 | $42,806 | needed |
| §852(b)(4)(A) | $1,768 by selling on day 130 with no wash sale | n/a | the rule the plan defeats |
| §1223(3) tacking | $1,768 | $41,038 | **decoration** (33 or 32 days, short-term either way) |
| trade "buy GainFund" | $531 | | needed |
| trade "sell GainFund" | $531 | | needed |
| trade "sell FundA" | $0 | | needed (frees the exposure) |
| trade "buy FundA" | $1,768 (exits into DivStock) | | decoration |
| "buy FundA" + "buy DivStock" + shorts | $0 | | some exit is needed |
| second lot of a held instrument / `maxLots := 1` | $1,768 (sell day 131, rebuy same day) | plan as written not executable | same-day *double* lot is decoration |
| every trade the plan does not use (11 kinds) | $1,768, 320 positions | | found, same figure |
| those + DivStock removed from the world | $1,768 | | found, same figure |
| GainFund pays no dividend | $0 | | nothing to find |

## T4 Earlier law: pass (no recent amendment involved)

The plan rests on no recent amendment: §852(b)(4) has said "6 months" since the Deficit Reduction Act of 1984,
"less than 31 days" before that (still the wording of Reg. §1.852-4(d)). Restoring 30 days: selling after 33 days
with no wash sale already gives $41,038; the plan adds nothing ($41,038); day-130 sale $42,806. With wash sales
switched off, out by day 162: pre-1984 text saves $1,768, current text $531. So the wash sale's only function is
to undo the 1984 lengthening, and the pre-1984 result was the known one.

## T5 Free lunch: pass

Unmodified rules. Over every final position, everything sold: recognized income (gains, losses, dividends, less
investment interest, plus losses still deferred) minus the pre-tax result ($5,000 in every plan).

| Scenario | Positions | Finals | min | max | Lowest tax |
|---|---|---|---|---|---|
| C2, other ST gain 50k | 3,706 | 269 | 0 | +10,000 (24 finals) | $41,038 |
| C2, no other gain | 3,706 | 269 | 0 | +10,000 (24) | $778 |
| C1, 50k | 3,723 | 283 | 0 | +10,000 (24) | $41,038 |
| C1, none | 3,723 | 283 | 0 | +10,000 (24) | $778 |
| C2 world with no distributions, none | 720 | 19 | 0 | 0 | $1,190 |

No position recognizes less than the economic result: no loss counted twice, no income lost. The 24 positive cases
are the model destroying a loss (divergence 2). Lowest tax with no other income is $778, far above the floor of
two §1211(b) deductions (−$2,264); it is the known dividend capture. Largest net long-term amount 15,000, lowest
net short-term −10,000: exactly one dividend converted, never more.

## T6 Kernel: pass

Full rules (`RedT6.lean`), trades applied directly (`openLong`, `sellLong`, `advance`, `liquidate`), `decide +kernel`
(kernel evaluation, no `native_decide`): `plan_tax` = 41038, `hold_tax` = 42806, `closed_tax` = 42806,
`plan_figures` (year 1: ST 40,000, LT 10,000), `hold_figures`, `closed_figures` (= baseline figures).
`#print axioms`: `propext, Classical.choice, Quot.sound` on each; no `sorryAx`, no `Lean.ofReduceBool`.
A compiled `#eval` confirms the direct sequence equals the labelled `replay` (41038 / 42806).

All move sequences (`RedKernel.lean`, no imports): cut-down model, said plainly: one share class, price moves only
by capital gain dividends, no calendar (everything inside six months), wash sale = sale at a loss with simultaneous
repurchase. `closed_no_short_term_loss : ∀ ms, (run true s0 ms).stLoss = 0` by induction on the list with the
invariant "every share's unrealized loss ≤ its taint"; `closed_never_reaches_plan`; `open_plan` (LT gain 10,000,
ST loss 10,000, by `decide`); `open_not_universal`. Axioms: `propext` (+ `Classical.choice, Quot.sound` from
`omega`/`simp` on the inductive ones). No `sorryAx`, no `ofReduceBool`, no axioms of my own.
Limit: the universal statement is about the cut-down model, not the 850-line file.

## T7 Independent arithmetic: pass

`red_arith.py`, from the statute: baseline $42,806.00, plan $41,038.00, saving $1,768.00; closed gap $0; hold 201
days $1,768.00. All equal the Lean. $1,768 is a future value: the saving is **$1,700** in year-1 dollars
(10,000 × (40.8% − 23.8%)) plus $68 of interest at 4%.

Economic gain after costs (four trades of the full position): net = 17 points × dividend − 4 × cost. At a 10%
dividend and 5 bp a trade: $1,500 per $100,000. Break-even dividend rate: 0.47% at 2 bp, 1.2% at 5 bp, 2.4% at
10 bp, 5.9% at 25 bp. So a gain exists for large distributions in liquid funds, and only for a taxpayer with
short-term gains at least equal to the dividend (none: $0; $5,000: $884).

Same result by holding: yes. Holding 201 days gives the identical $1,768 with two fewer trades and no wash sale.
The plan's whole increment is 168 fewer days in the fund. The model's score (tax only, same pre-tax wealth in
every plan) gives that zero value.

## T8 Outside the statute: partial

8 searches (standard), regulations fetched from eCFR, Publication 550 (2025) from irs.gov.

- Treas. Reg. §1.852-4(d) (retrieved in full): still the pre-1984 "less than 31 days" text; "(2) ... The rules
  contained in section 246(c)(3) ... shall be applied in determining whether ... a share of regulated investment
  company stock has been held for a period of less than 31 days." Nothing on wash sales or replacement shares.
- Treas. Reg. §1.1091-1, §1.1091-2 (retrieved in full): disallowance, matching, basis. Nothing on character.
  §1.1091-2(b) refers only to average-basis RIC stock under §1.1012-1(e).
- Treas. Reg. §1.1223-1(d): "the holding period of the newly acquired securities shall include the period for which
  the taxpayer held the securities with respect to which the loss was not allowable." Holding period only.
- Temp. Reg. §1.1092(b)-1T(c)(1): "If the disposition of a loss position would (but for the application of this
  section) result in a capital loss, the loss allowed under paragraph (b) ... shall be treated as a capital loss."
  Treasury wrote a character-preservation rule for straddle wash sales; there is none under §1091. Supports the gap.
- IRS Publication 550 (2025): "The loss ... is treated as a long-term capital loss up to the total of any capital
  gain distributions you received"; wash sales: "This adjustment postpones the loss deduction until the disposition
  of the new stock or securities. Your holding period for the new stock or securities includes the holding period of
  the stock or securities sold." The two passages do not refer to each other. "Postpones the loss deduction" is the
  IRS's own description and is the hook for arguing that the postponed loss keeps its (b)(4)(A) character.
- Practitioner pages read (State Farm, Journal of Accountancy 2003, Tax Facts, KPMG wash-sale paper via summary):
  each rule separately; none describes the combination.

Not retrieved: the Joint Committee's General Explanation of the 1984 Act and the committee reports; any proposed
regulation under §852(b)(4) (none surfaced); BNA/Bloomberg portfolios, Tax Notes, Bittker & Lokken (paywalled);
case law on §852(b)(4) or on taxpayers invoking §1091 for their own benefit; Form 8949 / 1099-B instructions on
wash-sale code W. Absence in eight standard searches is weak evidence that nobody has written this down.

## Weaknesses, ranked

1. **No incremental dollars.** $1,768 is the saving against doing nothing; against the known six-month hold it is
   $0. The claimed advantage is time (33 days against 201), which the objective does not score.
2. **Not what the search printed.** `final.txt` C2 shows three tied families, none of them the day-162 exit; the
   plan is a hand-written check line. Ties are broken by hash-map order: adding two unused fields in my copy changed
   every displayed path (and happened to print the plan). With the hold excluded (`clearBy`), the blind search does
   return it (sell and rebuy on day 131, out on day 162), so the mechanism is found, the headline plan was chosen.
3. **Stands on a sale that changes nothing.** §7701(o) (applies to individuals' income-producing activity,
   (o)(5)(B)), step transaction, or reading the replacement as "such share" each give the T2 result: $0. The
   variants with a day in another fund or a day doubled up survive in the model only because every fund there has
   the same return.
4. **Narrow facts.** Needs short-term gains ≥ the dividend, a top-bracket taxpayer (17 points; 9 at 24%/15%), a large
   distribution, and a fund that permits a redemption and immediate repurchase. $68 of the $1,768 is interest.
5. **Scenario built around it.** Date grid and zero-gain entry are convenient; the day-162 exit clears a rule that
   is stricter in the model than in the statute.
6. **Encoding gaps not on the path** (T1 list): (C)(ii), §246(c)(4)(A)–(B), matching order, 183 days.
7. **Authority search is thin** (T8): nothing closes it, nothing describes it, the secondary literature that would
   was not reachable.
