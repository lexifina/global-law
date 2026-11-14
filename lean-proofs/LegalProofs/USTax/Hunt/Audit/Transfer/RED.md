# Red team: Transfer, the QTIP candidate

Plan attacked: a widow with her late husband's property in a QTIP trust remarries, gives up her income interest
(§2519), and she and the new spouse consent to split gifts (§2513), so the new spouse's exclusion and GST exemption
(§2652(a)(2)) shelter half. Claimed: +$30M to +$33M at year 25 on a $100M trust.

**Verdict: holds on the text, but it is not the plan the findings describe, and the figure is three-quarters
compounding.** I could not break the encoding, the arithmetic or the search. What I did break:

1. **The gain does not come from §2519.** Giving up the income interest is two gifts: the income interest itself
   (§2511) and everything else (§2519); Reg. §25.2519-1(a), (c)(1) and Example 1 say so. The model books them as one
   gift. Splitting the §2511 gift with a spouse is ordinary §2513. With §2519 transfers excluded from §2513 but the
   income-interest gift left splittable, 70% of the gain survives when the income interest is 20% of the trust, 93% at
   30%, all of it at 40% or more. The candidate is the findings' own "VARIANT" row (gift-splitting with a later spouse
   who has no estate) applied to a QTIP. The "natural fix" closes it only in the model.
2. **With no growth the gain is $9.60M, not $30M to $33M:** $6M of gift tax plus $6M of GST tax, less $2.4M of GST tax
   on the gift tax saved. It is one person's $15M exclusion and $15M exemption, used once.
3. **The trust pays the new spouse's $14M of gift tax in the model. §2207A(b) does not give that right.** Read
   strictly the plan as found is not allowed on a $100M trust; it works on a trust first cut down to $30M
   (two exclusions), where no tax is due.
4. **The new spouse is free.** His exclusion and exemption are spent and nothing is charged for it. The gain is his
   allowance moving to another family, not tax disappearing.

All runs: `lake env lean [--run] LegalProofs/USTax/Hunt/Audit/Transfer/Red*.lean <scenario>`, each under 90 s.
Variants are generated from the untouched original by `gen.py` (text patches, each asserted to match once) plus
`tail.lean.txt` (audit scenarios). `RedOrig` reproduces the original to the dollar: 218,551,878 / 226,135,352 /
256,570,861 (check 1) and $283.50M / $250.67M (search). Raw output is in `out/`.

## Figures used below (grandchildren's after-tax wealth, year 25)

| Play | QTIP scenario, release yr 0 | Check 1 (H dies yr 5, release yr 5) |
|---|---|---|
| Hold the QTIP to W's death | 218,551,878 | 218,551,878 |
| Give up the interest, unmarried | 233,157,839 | 226,135,352 |
| Remarry, consent, give up the interest | 269,507,610 | 256,570,861 |
| Gain from the later spouse | **36,349,771** | **30,435,509** |

Search (QTIP scenario): best with remarriage $283.50M, best without $250.67M, gap $32.83M.

## T1 Text fidelity: partial

Read against §§2513, 2519, 2207A, 2652(a), 2631, 2632, 2642, 2035(b), 2044 and Reg. §§25.2519-1, 25.2513-1,
25.2207A-1, 26.2652-1.

More generous than the words:

- **D1. One gift where the law has two.** `releaseQtip` taxes `s.q.v` as a single gift "under §2519". §2519(a)
  reaches "all interests in such property other than the qualifying income interest"; the income interest is a §2511
  gift. Harmless for the tax due, but it makes the whole gain look like a §2519 effect (see T2).
- **D2. The trust pays the consenting spouse's tax.** `releaseQtip` pays `gt` (both halves) out of the QTIP. §2207A(b)
  gives recovery to the person treated as transferring under §2519, for tax "with respect to" that person; Reg.
  §25.2207A-1(a): "the individual or the individual's estate is entitled to recover". On $100M the new spouse owes
  $14,000,000. Strict copy (`RedStrict`, trust may not pay his half): plan **not allowed** at $100M and at $40M; allowed
  at $30M (no tax): 131,409,507 against 96,167,917 unmarried, gain 35,241,590; search on a $30M trust $134.57M against
  $105.63M. Search at $100M under the strict rule: remarriage worth $0 ($250.67M both). A net-gift condition (trustee
  agrees to pay, as in PLR 200022031) is the practical way round; the model has neither that nor a severance move.
- **D3. The later spouse costs nothing.** `remarry` creates a person with no property, no estate, no death, a full
  exclusion and exemption, and `wealth` ignores him. Using his $15M exclusion costs his own heirs up to $6M and his
  exemption another $6M; none of it is charged. He is also jointly liable for the whole year's tax (§2513(d)).
- **D4. Built for this plan.** The move `remarry`, the fields `newH`/`newW`, `isNew`, and the `enablers` function
  (consent and marriage tried free before every move) exist only for remarriage plans. FINDINGS says the plans
  "were missed until the two enabling moves were made free": the search was steered to them. The two-trust branch in
  `releaseQtip` (`else if s.split && s.married`) was written after the artifact surfaced. That §2513 reaches a §2519
  transfer is an encoded premise, not something the search derived.
- **D5.** §2513(a)(1) conditions not encoded: both spouses citizens or residents; no remarriage in the rest of the
  year. Consent lasts a 5-year period, not a calendar year. Neutral here.

Stricter than the words (both arms, so the gain is not inflated by them): no net-gift reduction (Reg.
§25.2519-1(c)(4); with it the gain is $30.76M at year 0, Python only); deaths use the exclusion of the start of the
period; the later spouse cannot allocate his later-indexed exemption; no §1015(d)(6) basis increase.

Missing restrictions that could bite in practice, not in the statute text I read: trust terms barring assignment,
state law, sham marriage, what W lives on.

**The modelling error (later spouse allocating GST exemption to the dead spouse's trust): closed, tested hard.**
`leak-q`, `leak-A` count every position the search touches: QTIP scenario 5,354 positions, 3,867 with a later
spouse, his exclusion or exemption used in 1,864; scenario A 55,608 / 18,274 / 11,896. In none was it used without a
consent in the path, without a §2519 release or lump gift by the other spouse, or beyond the gifts attributed to him;
he never owns property. In the closed copy on the QTIP scenario it is used 0 times in 2,642 positions.

**The beam.** Wide beam (depth 3 first phase, depth 2 later, 3 rounds, cap 1,400, 85,573 positions): $284.19M with
remarriage, $251.70M without (20,213 positions); gap $32.49M against $32.83M. The gain also stands without any
search, as a direct replay.

## T2 Close the gap: partial

Edit: §2513(a)(1), add "This paragraph shall not apply to a transfer treated as made under section 2519." In
`RedClosed`: the release calls `taxGift` with the consent off and the trust is not divided. Result: plan gone,
baseline unmoved. Remarry + consent + release = 233,157,839 = unmarried (year 0); 226,135,352 = unmarried (check 1);
hold 218,551,878 unchanged; search best $250.67M = best without remarriage.

Then the same edit with the law's two gifts kept apart (`RedClosedF*`: income interest = f of the trust, a §2511
gift, still splittable; the rest under §2519, not splittable):

| Income interest | Gain, release yr 0 | of 36,349,771 | Gain, check 1 | of 30,435,509 |
|---|---|---|---|---|
| 0% (the model) | 0 | 0% | 0 | 0% |
| 20% | 20,877,274 | 57% | 21,406,824 | 70% |
| 30% | 31,651,527 | 87% | 28,453,911 | 93% |
| 40% | 35,678,582 | 98% | 30,435,517 | 100% |
| 50% | 36,349,792 | 100% | 30,435,487 | 100% |

A life income interest at a 5% §7520 rate is roughly 30% to 50% of the trust for a widow of 65 to 80 (my estimate
from life expectancy, not looked up in Table S). So the plan survives the fix: the gain comes from §2513 applied to
W's own gift, with a later spouse. To close it Congress would have to limit §2513 itself.

## T3 Ablation: pass

QTIP scenario search. Without `remarry` $250.67M; without `consentSplit` $250.67M; without `releaseQtip` $231.64M
(remarriage then worth $0). All three are needed. Only the kinds plan #1 uses (split, C-gift, 529,
annual→grandchildren, §2519, trust→child, trust-tuition, remarry): $283.50M, same figure. Only the three: $269.50M =
the direct replay.

## T4 Earlier law: pass (does not depend on a recent amendment)

§2513 is 1948, §2519 1981, §2652(a)(2) 1986. The 2025 Act only sets the size. Check-1 gain with a $13.99M exclusion:
28,388,512; with $7M: 14,203,273; with $15M: 30,435,509.

## T5 Free lunch: partial

- Conservation on every step and phase end the search takes. QTIP scenario: 50,860 steps, 10,708 phase ends, 0
  breaches. Scenario A (cap 140): 614,278 steps, 0 value breaches; **900 estate closings create money, up to
  $4,444,551**: estate tax on the §2035(b) gross-up is recorded as paid when the estate holds nothing to pay it
  (`eSp - (rest - fromNon)` cut off at zero). Not on the candidate's path.
- Basis created from nothing: `tuition`, `trust-tuition`, `529` hand the grandchildren full basis when paid out of
  appreciated property, up to $600,000 a move (at most $143k of tax). `trust-tuition` is in plan #1.
- Limits (exemption allocated ≤ exemption, credit ≤ credit, basis ≤ value, fraction ≤ 1): 0 breaches in either.
- Absurd goals: least transfer tax found $42.49M (QTIP), $25.88M (A); largest holdings $328.07M (QTIP), $417.30M (A)
  against $543.61M untaxed. Nothing below zero, nothing above the bound.
- **No growth** (`RedNoGrowth`): hold 45,599,981; unmarried release 45,599,981; with the later spouse 55,199,982;
  gain **9,600,001** at year 0 and at year 5. Search: $59.11M against $50.84M, $8.27M. Closed and no growth: 0 on the
  replay (the search shows $50.90M against $50.84M, $0.06M of beam noise; the leak count is 0).

## T6 Kernel: pass

Full state, no cut-down, `decide +kernel`. `RedKernelOrig`: `hold_wealth` 218551878, `unmarried_wealth` 233157839,
`plan_wealth` 269507610, `plan_xfer` 117172745. `RedKernelClosed`: `closed_plan` 233157839, `closed_plan_xfer`
142742786, `closed_hold`, `closed_unmarried`. Over all sequences, by induction on the list:
`closed_plan_moves_do_nothing` / `closed_drop_marriage`: under the closed rule, for any schedule, any position in
which the wife is the income beneficiary (or there is no QTIP) and any list of marriages, consents and §2519
releases, deleting every marriage and consent leaves the same position apart from the consent flag and the later
spouse's slot. Limits: one phase, those three kinds of move only. Axioms: `propext`, `Quot.sound`, and
`Classical.choice` in the two induction theorems; no `sorryAx`, no `Lean.ofReduceBool`, none of mine.

## T7 Independent arithmetic: pass

`red_arith.py`, written from the statute steps. Hold 218,551,910 (Lean 218,551,878); unmarried 233,157,954
(233,157,839); with the later spouse 269,507,706 (269,507,610); gain 36,349,752 (36,349,771). Check 1: 226,135,482
and 256,570,951 (226,135,352 and 256,570,861), gain 30,435,469 (30,435,509). Largest difference $220, rounding.
It needed §2632(e) (W's unused indexed exemption allocated at her death) to agree.

## T8 Outside the statute: nothing closes it, nothing describes it

9 searches (standard). Regulations read in full from eCFR.

- Reg. §25.2519-1(a): "the donee spouse is treated as making a gift under section 2519 of the entire trust less the
  qualifying income interest ... A transfer of all or a portion of the income interest of the spouse is a transfer by
  the spouse under section 2511." Supports "a gift made by" W; also the two-gift structure. No mention of §2513.
  https://www.law.cornell.edu/cfr/text/26/25.2519-1
- Reg. §25.2519-1(c)(4): the amount "is further reduced by the amount the donee spouse is entitled to recover under
  section 2207A(b)". Lowers the gift in both arms.
- Reg. §25.2207A-1(a): "the individual or the individual's estate is entitled to recover from the person receiving
  the property ... the amount of gift tax attributable to that property"; (b): not recovering is a gift. Nothing for a
  consenting spouse. https://www.law.cornell.edu/cfr/text/26/25.2207A-1
- Reg. §25.2513-1(a), (b): no exception for deemed transfers; no mention of §2519.
  https://www.law.cornell.edu/cfr/text/26/25.2513-1
- Reg. §26.2652-1(a)(4): "the electing spouse is treated as the transferor of one-half of the entire value of the
  property transferred by the donor". Supports the GST half. https://www.law.cornell.edu/cfr/text/26/26.2652-1
- Form 709 instructions (first 100,000 characters read): split-gift conditions only; nothing on §2519.
  https://www.irs.gov/instructions/i709
- PLR 200022031 (summary): gift reduced where "a condition of the Taxpayer's transfer is the agreement that the gift
  tax will be paid by the trustees". https://ezel.ai/irs-rulings/0022031
- PLR 201243004 and the like: a QTIP can be divided so §2519 reaches one part only (search summary of the Milbank
  note; the PDF did not parse).

Not retrieved: T.D. 9077 preamble (Federal Register blocked the fetch); Stephens Maxfield, Bloomberg 843, any ACTEC
or Heckerling outline; PLR full texts. No ruling or article on splitting a §2519 transfer, with or without
remarriage, turned up. Absence in nine searches is weak evidence of novelty.

## Weaknesses, ranked

1. Mislabelled source of the gain (D1, T2): it is §2513 with a later spouse, already in the findings as a VARIANT;
   excluding §2519 from §2513 does not close it.
2. Headline is 3 to 4 times the tax saved: $9.6M with no growth.
3. The later spouse's allowance is spent at no cost (D3); with a cost of $6M to $12M to his own heirs the net is
   about zero unless he has no taxable estate.
4. Trust pays his $14M with no statutory right (D2); as found, the plan needs a net-gift condition or a severance
   the model does not have.
5. The premise that §2513 reaches a §2519 transfer was encoded, and the search steered to remarriage (D4).
6. Scenario A creates up to $4.44M at 900 estate closings (T5); other rows of the findings may be affected.
7. No authority either way; treatises not checked.
