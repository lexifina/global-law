# Basis and transfers between related persons: findings

File: `LegalProofs/USTax/Hunt/Basis.lean` (namespace `Legal.USTax.Hunt.Basis`).
Family: taxpayer T and spouse S (joint return, $450,000 ordinary taxable income), minor child K, adult child A
($40,000 wages), T's elderly parent P ($30,000 pension), a public charity. Figures: 2026 (Rev. Proc. 2025-32 from
memory, not re-checked against the document), held constant. Prices constant.

## How to run

- `lake env lean LegalProofs/USTax/Hunt/Basis.lean` runs the `small` set: about 36 seconds, output saved in
  `tools/hunt/out/Basis/small.txt`.
- The `wide` set is too large for the interpreter (run 6 alone is 3.4 million positions). It was run from a compiled
  scratch copy, 1 min 42 s, output in `tools/hunt/out/Basis/wide.txt`:
  `cd tools/hunt/out/Basis; lake env lean -c BasisMain.c BasisMain.lean; lake env leanc -O2 -o basis.exe BasisMain.c; ./basis.exe`
  (`BasisMain.lean` is `Basis.lean` without the `#eval` and with a root `main`.)

## Provisions encoded (each read in the local text)

| Provision | What the model does |
|---|---|
| §1014(a)(1), (b)(1) | heir's basis = value at death, up or down |
| §1014(e) | appreciated property given to the decedent within a year keeps the decedent's basis if it passes to the donor or the donor's spouse |
| §1015(a), (e) | donee takes donor's basis; for loss, no more than value at the gift; not applied to spouse transfers |
| §1041(a), (b) | spouse transfer: no gain or loss, treated as a gift, transferor's basis |
| §267(a)(1), (b)(1), (c)(4), (d), (g) | loss on a sale to family disallowed; buyer's later gain reduced; P is not in S's family; spouse transfers excluded |
| §1(h), §1(j) | 0 / 15 / 20 bands; 28-percent rate gain for §1202 gain, (h)(4), (h)(7) |
| §1(g) | child's net unearned income taxed at the parents' marginal rates |
| §1211(b), §1212(b) | $3,000 against ordinary income; carryover; P's carryover ends with P's last return |
| §170(b)(1)(C), (G), (I), (e)(1)(A), §68 | value deduction for long-term property (30%), basis for short-term, 0.5% floor, 2/37 cutback |
| §121(a), (b)(1)-(3), (d)(3)(A) | $250,000 / $500,000; own and use two years; spouse tacking only |
| §102, §2503(b), §2513 | gifts not income; amount of each property gift above one annual exclusion reported beside each plan |
| §1223(2), (9) | tacked holding period on gifts; inherited property long-term |
| §1202(a)(1)(B), (a)(5), (b)(1), (b)(4)(B), (h) | 50 / 75 / 100% at 3 / 4 / 5 years; $15,000,000 per taxpayer; gift and death keep status and holding period |
| §63(c)(5), §151(d)(5)(C) | dependent's standard deduction; $6,000 senior deduction less 6% of MAGI over $75,000 |

Read but not searched: §1014(b)(6) (community property), §453 / §453B / §691(a)(5) (installment sales), §1015(d)
(no gift tax is paid in any run), §1091 (nobody buys on the market; wash-sale basics are in `USTax/WashSale`).
Left out: §1411, AMT, state tax, estate tax, cash gifts against the annual exclusion.

Search pruning, stated in the file: lots are touched in index order within a year; a sale at a gain to a family
member is offered only when market sales are barred (at constant prices it taxes the seller exactly as a market sale).

## Search size

| Run | Positions | Finished plans | Families |
|---|---|---|---|
| 1. three lots, pledge, no death | 38,298 | 806 | 52 |
| 2a. P dies inside a year of any gift | 28,727 | 158 | 44 |
| 2b. P dies a year later | 53,016 | 326 | 56 |
| 2c. one winner, will must name T | 40 | 8 | 5 |
| 3. no market sale before the last year | 4,141 | 21 | 20 |
| 4a. QSBS, two $12M blocks | 1,102 | 168 | 10 |
| 4b. QSBS, three blocks, P dies year 1 | 42,855 | 1,185 | 18 |
| 5a. home in three shares | 33,552 | 681 | 21 |
| 5b. home, P dies year 0 | 93,504 | 581 | 45 |
| 6. four lots, pledge, P dies year 1 | 3,418,562 | 9,458 | 262 |

## Plans that beat "every owner sells" (dollar effect is the run's saving)

| # | Plan the search returned | Run, saving | Provisions combined | Class | What could defeat it | Checked |
|---|---|---|---|---|---|---|
| 1 | T gives winner to A, A gives it to P, P dies within the year, will names T, T sells | 2c: $7,500 of $7,500 gain tax; 5b: $60,000 on one home share. The direct gift T→P→T gets nothing | §1014(e)(1)(B) names only "the donor of such property (or the spouse of such donor)"; the donor to the decedent is A | CANDIDATE, weak | Step transaction / substance over form: A is a conduit and T is the real donor. No regulation under §1014(e). A must be free to keep it. Two gifts use unified credit | 1 search: nothing on an intermediary donor; only the "leave it to the donor's child" route is written up |
| 2 | T gives two home shares to K and P (who live there), they own two years, each sells with a separate $250,000 | 5a: $92,260 (exclusion $900,000 instead of $500,000) | §121(a), (b)(1): limit is per taxpayer; no tacking needed because donee meets own-and-use alone; excluded gain is outside §1(g) | VARIANT | Donee must really own (proceeds are theirs; a minor needs a custodian or trust, and a trust owner fails §121 unless grantor trust); assignment of income if the sale is already agreed; §121(b)(3); $462,000 of unified credit per share | 1 search: per-co-owner exclusion is settled; gifting to a resident parent or child is asked in forums without an answer |
| 3 | T gives loser to S, S sells it to P, loss allowed on the joint return; in runs 1 and 6 P then gives it back and T donates it | 3: $960 (one extra year of $3,000), only when market sales are barred | §1041(b)(2) with §1015(e) (full loss basis to S); §267(c)(4) leaves P out of S's family; §267(g) | VARIANT | "Directly or indirectly" in §267(a)(1) (McWilliams) read as a T→P sale; step transaction; §7701(o) if the stock comes back by gift | 1 search: in-laws outside §267 is textbook; nothing on the §1041 first step |
| 4 | T gives winner to P, P sells it against P's own loss and 0% band before dying; cash comes back by will | 2a: $4,815; 2c: $6,465 | §1015(a), §1212(b), §1(h)(1)(B), §102; §1014(e) irrelevant because P sells | KNOWN (use a parent's expiring losses / low bracket) | Assignment of income if prearranged; senior deduction phase-out | 1 search: described in NYSSCPA "use it or lose it" and forums |
| 5 | T gives winner to P, P dies within the year, will names A (or K), heir sells | 2a: $7,800; 5b: $131,815 | §1014(a), (e) | KNOWN (upstream gift, bequest to donor's child) | — | same search as 1 |
| 6 | Same, P dies after a year, will names T | 2b: $8,100; 6: $11,989; 4b: $7,191,815 | §1014(a), (e) | KNOWN (upstream gifting) | P's creditors, will, estate tax | — |
| 7 | QSBS blocks given to A, K or P so each uses a $15M limit | 4a: $4,791,815 | §1202(b)(1), (h)(1)-(2) | KNOWN (stacking) | — | — |
| 8 | Hold short-term winner a year, then give it to charity; sell winner and loser together | 1: $6,427 | §170(e)(1)(A), §1222 | KNOWN | — | — |
| 9 | Winner to A or P, sold in the 0% band | 1: $4,502 / $4,442 | §1(h)(1)(B), §1015 | KNOWN | — | — |
| 10 | Winner to K, sold | 1: $3,832 with a short-term lot; 2c: $405 | §1(g) | KNOWN, mostly shut by the kiddie tax | — | — |

Nothing in the search output is a strong novel plan. Item 1 is the only one I do not know as published, and it is
the kind of gap a court closes by treating A as a conduit.

## Traps the search showed

- Gift of loss property to anyone but a spouse destroys the loss (§1015(a)): run 3, winner and loser both to K, $4,155 worse than baseline.
- Giving a winner to K usually loses: the gain is taxed at the parents' rate and T's loss no longer offsets it (run 3, $3,195 worse).
- §1202 at three years: a $12M block sold at 50% pays 28% on the other half ($1.68M, run 4b) and, as encoded, uses
  $12M of the $15M limit although only $6M is excluded.
- P's gains cut the §151(d)(5)(C) senior deduction: the $300 steps between otherwise equal plans in runs 2a and 2b.
- P selling before death instead of holding: $300 to $1,635 worse in runs 2a/2b; unused loss of P is worth at most $3,000 on the last return.
- §267(d) relief does not follow the property on a gift or at death (conservative reading of "the taxpayer").

## Drafting gaps noticed (reading only, not search output)

- §1014(e) tests "donor" one step back only (item 1), and reaches only property "acquired by the decedent by gift":
  on a deathbed change of separate property into community property the survivor's own half comes in under
  §1014(b)(6) and was never acquired by the decedent, so only the decedent's half is exposed to (e).
- §1041(b)(2) gives the transferee "the adjusted basis of the transferor", one number; a transferor who took loss
  property by gift has two (§1015(a)). The text does not say which passes. Encoded: both pass.
- §1202(b)(4)(B) reduces the limit by eligible gain "taken into account … under subsection (a)"; with the new 50%
  and 75% tiers it is not stated whether that is the whole eligible gain or the excluded part.
- §1202(b)(3)(B) allocates gain between spouses on a joint return "for purposes of applying this subsection to
  subsequent taxable years" without saying whether a joint return has one limit or two. Encoded: one.
- §267(c)(4) omits in-laws while §267(g) and §1041 let property cross to the spouse at full basis first (item 3).
- §453(e)(6)(C): no second-disposition rule after either party's death; §453(e)(2) two-year cutoff. Not modelled.

## Sources checked (4 of 6 searches used)

- https://greenleaftrust.com/?p=6133 (§1014(e), bequest to donor's child)
- https://www.thetaxadviser.com/issues/2024/dec/dealing-with-sales-between-related-persons/ and
  https://extension.usu.edu/ruraltax/tax-topics/related-parties-for-federal-income-tax (in-laws outside §267)
- https://financialplanningassociation.org/learning/publications/journal/OCT24-beyond-101-irc-ss-121-further-study-common-tax-exclusion-OPEN and
  https://accountants.intuit.com/community/tax-talk/discussion/section-121-exclusion/00/306280 (§121 co-owners)
- https://nysscpa.org/news/1045357-use-it-or-lose-it-income-tax-attributes-at-death-2020-10-01 and
  https://www.kitces.com/blog/capital-loss-at-death-step-down-gift-carryover-split-double-basis/ (losses at death)

## Limits of this run

- Constant prices: nothing here values keeping a position (so §267(d) relief, dual basis on a recovery and §1091
  never earn anything). Two- to four-year horizons; unused carryovers at the end are shown but not valued.
- One line is printed per distinct tax level (shortest family); ties are counted, not listed.
- 2026 dollar figures are from memory.
