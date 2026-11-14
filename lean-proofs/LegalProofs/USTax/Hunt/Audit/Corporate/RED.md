# Red team: Corporate, plan 1 (second per-issuer limit through a holding company)

Plan attacked: A sells 1/5 of the C stock; contributes the other 80% to P under §351; sells the P stock.
Claimed: tax 3,855 against 5,712 ($ thousands), 7,800 more gain excluded.

Verdict: **already published** as a reading of the statute (Dolson, FBT Gibbons). The arithmetic and the model are
sound and the plan survives a strict reading of §1202, but the "discovery" is one line the encoder wrote, the
findings overstate the margin over known planning, and they miss §269.

Files here: `gen.py`, `gen5.py`, `gen6.py` (build the Lean files from lines 1–532 of the original plus patches),
`RedT1.lean` … `RedT6.lean`, `RedT5closed.lean`, `red_t7.py`, `red.json`. Each Lean file runs in under 50 s with
`lake env lean`.

## T1 Text fidelity: partial

Read against §1202(a)(1), (4)–(6), (b)(1), (2), (4), (c)(1)–(3), (d), (e)(5), (g)(1)(B), (h)(4)(A)–(D), (k),
§351(a), §368(c), §269, §7701(o), §1(h)(7).

Where the second limit comes from. Lines 385–388 of `Corporate.lean`: `sellP` calls `exchGain` on a blank holder
(`ind0`, so `usedPrior = 0`, `gainYr = 0`, `takenYr = 0`) and throws the counters away. The comment says so: "P is
the issuer". The search did not find this; the encoder decided it and the search confirmed that the decision pays.
The reading is what the words say (§1202(b)(1) "stock issued by such corporation"; (h)(4)(B) itself calls the new
stock "issued by a corporation which … is a qualified small business"; (g)(1)(B) shows Congress redirecting the
issuer where it wanted to, and (h)(4) has no such words). So this is not the old circularity, but it is a legal
choice made in one line, not an emergent result.

Encoding more generous than the words, or restrictions missing:

1. §351(a) "immediately after the exchange": the plan sells P in the next move. `contribP` only says "A controls
   P". With a binding sale the exchange is taxable (Rev. Rul. 70-140, Intermountain Lumber) and the tax is 5,712.
2. §1202(h)(4)(B): not computed (comment: P is a qualified small business, so no cap). True on these facts (P's
   assets are $32m at value under §1202(d)(2)(B)), but nothing checks it.
3. §269(a)(1): absent for this plan. The findings cite it only for plan 6 and say "Statute: nothing". Reg.
   §1.269-1(a): an "allowance" includes "an exclusion"; §1.269-1(c): transferring assets to a newly organised
   corporation for all its stock is an acquisition of control. On the plan's facts P has no other purpose. This is
   a statutory, purpose-based power to disallow and it fits the plan as drawn. It cannot be encoded as a mechanical
   rule.
4. §1202(c)(2)(A) for P: "such corporation" must meet the active business test during substantially all of the
   taxpayer's holding period for the P stock, which under (h)(4)(A) reaches back five years, when P was empty or
   did not exist. Not encoded, unsettled, and common to every use of (h)(4).
5. No field records gain on P stock, and P stock can only be sold all at once, so P's own limit can never be
   tested in the model.
6. Buyers pay full value for C stock although C carries 6,300 of latent corporate tax (a stated simplification).
   Same in plan and baseline, so the 1,857 difference is unaffected, but every stock sale is flattered against
   14,320.

Checked and correct: §1202(a)(5) tiers and (a)(6)(B) acquisition date; (b)(1)(A)/(B) "greater of" and the
(b)(4)(B) reduction for prior years; ten times basis (P stock basis 800 gives 8,000, below 15,000); (h)(4)(D)
control at exactly 80%; (c)(3) (not used by the plan; `age < 2` is wider than the statute); §1(h)(7) (gain over the
limit is not "section 1202 gain"). The buyer ends with 100% of C either way, so it is the same economic sale.

Fields or moves that exist only for this plan: `pq`, and the blank-holder call in `sellP`. `sellP` and `contribP`
also serve plan 6 and the non-QSBS runs (9,282, no gain there).

Strict copy (`RedT1.lean`): (h)(4)(B) limit always applied (new field `pCapGain`, gain above it taxed at 23.8%);
P stock saleable only after a year end with P holding 80% (proxy for §351 control not being transitory). Result:
the plan **survives** at 3,855, as "sell 1/5; contribute; wait 1y; sell P". One-issuer 5,712 and plain 14,320 are
unchanged. The model has no growth, so the (h)(4)(B) limit never binds. §269 and (c)(2)(A) were not encoded.

## T2 Close the gap: pass

Words added to §1202(h)(4)(A): "…, and for purposes of subsection (b) shall be treated as stock issued by the
corporation which issued the exchanged stock." One edit in `sellP` (`RedT2.lean`): the P sale runs through A's own
counters. Money to A: the plan's family disappears; the best is the two-year sale at 4,283; contribute + sell P =
5,712. Baselines unchanged: plain 14,320, one-issuer 5,712, non-QSBS 9,280. In the family-money run two plans using
P remain (3,391 with a gift to S and a redemption; 3,855 with a gift to K). Both were in the original output and
draw on S's and K's own limits (§1202(h)(1)–(2)), not on P.

## T3 Ablation: pass

Without `sellOut`: 5,712. Without `contribP`: 4,283 (two-year sale). Without `sellP`: 4,283. All three moves are
needed. Only the plan's three kinds of move: 3,855 (426 positions). Only the three exact moves: 3,855 (9 positions).

## T4 Earlier law: partial

The plan does not depend on the 2025 amendment. Pre-July-2025 text ($10m, 5 years): plan 5,045 against 6,902, the
same 1,857 saving. 50% and 75% tiers: the search waits to year 5 and returns 3,855. Without §1202: nothing (9,280
ordinary sale). The gap is in the 1993 text of (h)(4) and (b)(1) and has been open for 32 years; it is not new law.

## T5 Free lunch: pass

`RedT5.lean`, every position to depth 4 on the unmodified rules (93,140 QSBS; 80,099 non-QSBS; 81,536 with P's
deficit). Per move, family money + P's cash + the family's share of C + all tax never rises (0 moves) and, with no
outside holders, never falls by more than rounding (0 moves over 3). Range 39,998 to 46,300; the 46,300 is "A sells
everything, then C sells the asset", where the buyer bears 6,300 of corporate tax: divergence 6 above, not created
money. Yearly limit exceeded: 0. A's excluded gain on C stock never above 15,000 + 10 × 1,000 (largest 21,000).
Basis in the family's hands never above the 1,000 paid: 0. Tax is a natural number and never falls. Least tax on a
full exit with all money to A: 3,855 (the plan); for the family: 2,141 (gifts). With P's 8,000 basis: 7,376, which
is the 8,000 capital loss on P stock used once (1,904), not twice.

## T6 Kernel: pass

`RedT6.lean`, `decide +kernel` (no compiled code), 9 s. Replays: plan under the original rules = tax 3,855, A
36,145, with only 7,800 recorded against A's limit; one-issuer 5,712; direct sale 5,712; plain 14,320; plan under
the closed-gap `stepClosed` = 5,712 with 15,000 recorded. Least tax over every sequence of up to four moves from
{sell 1, 1/2, 1/4, 1/5; contribute 1, 1/2, 1/4; sell P}: 3,855 original, 5,710 closed. All sequences of any length
(`closed_no_second_limit`, induction on the list): under the closed rule the gain taken into account for A in the
year, P stock included, is at most 15,000. That theorem is cut down to the plan's three kinds of move (any holder,
any fraction) with no year end. `#print axioms`: the ten replay theorems depend on no axioms; the general one on
`propext` and `Quot.sound` only. No `sorryAx`, no `Lean.ofReduceBool`. Two false statements were tried and rejected.

## T7 Independent arithmetic: pass

`red_t7.py`, from the statute, exact fractions: plan 3,855.6 (Lean 3,855); one-issuer 5,712.0; plain 14,320.6
(Lean 14,320); P stock counted as C's 5,712.0; §351 failing 5,712.0. Extra gain excluded 7,800. The Lean figures are
truncated, not wrong. **But** the known two-year sale (plan 2 in the findings) costs 4,284.0 (4,248.3 at the best
split), so over what was already known the plan saves 428 (393), not 1,857.

## T8 Outside the statute: fail (already described)

6 searches, 5 fetches.

- Scott Dolson, FBT Gibbons, "Conversions, Reorganizations, Recapitalizations, Exchanges, and Stock Splits
  Involving QSBS": "if the replacement QSBS is treated as having been issued by a new issuer for purposes of the
  Aggregate Gross Assets Test, then it seems reasonable to conclude that the corporation issuing the replacement
  QSBS would be treated as a separate corporation for purposes of Section 1202's gain exclusion cap (i.e., there
  would be no aggregating of gain exclusion of the corporations issuing the original and replacement QSBS)."
  For replacement stock that is not itself qualified, the same article: "there are no tax authorities addressing
  how Section 1202's gain exclusion cap would apply in this situation, but the most reasonable approach might be to
  aggregate". On spin-offs: parent and subsidiary "would have their own separate gain exclusion caps", citing PLR
  9810010. On dropping stock into a new corporation: "The IRS might argue that dropping the existing subsidiary's
  stock into a newco subsidiary lacks a business purpose beyond positioning stockholders for eventually claiming
  Section 1202's gain exclusion."
  https://fbtgibbons.com/conversions-reorganizations-recapitalizations-exchanges-and-stock-splits-involving-qualified-small-business-stock-qsbs/
- Same author, "Maximizing Section 1202's Gain Exclusion", note 21 (fragments as returned by the fetch): the IRS
  "hasn't addressed Section 1202 income tax avoidance schemes through regulations"; "the potential focus on 'shell
  corporations' is there". https://fbtgibbons.com/maximizing-the-section-1202-gain-exclusion-amount/
- Reg. §1.269-1(a), (c) (eCFR): "The term allowance refers to anything in the internal revenue laws which has the
  effect of diminishing tax liability. The term includes, among other things, a deduction, a credit, an adjustment,
  an exemption, or an exclusion."; "if B … transfers … such assets to a newly organized Y Corporation in exchange
  for all the stock of Y Corporation, an acquisition within the meaning of such phrase is made by B".
  https://www.ecfr.gov/current/title-26/section-1.269-1
- Rev. Rul. 70-140 (summary only): a transfer to a controlled corporation followed, under an integrated plan, by a
  disposal of its stock does not meet §368(c) control for §351. https://www.bluej.com/resources/rev-rul-70-140

Nothing found that closes it: no regulation under §1202(k), no ruling on the limit for (h)(4) stock. The exact
20%/80% holding-company sale by one founder was not found in print. Not retrieved: Lee et al., "The QSBS Quest for
Quantum Exclusions" (Tax Notes 2020; the host did not resolve); PLR 9810010; the text of Rev. Rul. 70-140; the 1993
conference report; the current Priority Guidance Plan.

## Weaknesses, ranked

1. The legal point is published (Dolson): the findings' "none addresses a second limit" is wrong.
2. §269(a)(1) with Reg. §1.269-1(a), (c) reaches the plan as drawn; the findings say "Statute: nothing".
3. The second limit is one hand-written line (`sellP` with a blank holder), not something the search derived.
4. The claimed saving is against the weakest comparator. Against the two-year sale the same search printed, it is
   428.
5. §351 control is not modelled; the printed plan sells P at once, the version most exposed to Rev. Rul. 70-140.
   (A year's wait gives the same figure in the strict copy.)
6. §1202(c)(2)(A) for P over the tacked holding period is not encoded and is unsettled.
7. (h)(4)(B) is asserted in a comment, not computed; P's own limit cannot be tested in the model.
8. Not new law: the same saving under the 1993–2025 text.
