# Partnership hunt: findings

File: `LegalProofs/USTax/Hunt/Partnership.lean` (900 lines, `import Std` only). Run: `lake env lean
LegalProofs/USTax/Hunt/Partnership.lean` from `lean-proofs/`, about 80 seconds. Full output of the last run:
`tools/hunt/out/Partnership/final_run.txt`. Amounts in the model are thousands of dollars; tax figures below are
dollars at 23.8% (capital) and 40.8% (ordinary), losses valued at the same rates.

**Bottom line.** Nothing new that survives attack. The blind search rediscovered the mixing bowl, the related-party
basis shift and the §754 basis strip unprompted. It also returned two loss-acceleration plans and two ways round the
mandatory §734 step-down that I could not find written up; all four are deferral or timing, each has a clear line
of attack, and I rate none of them as a safe plan. In no position does any plan lower the tax due once everything is
sold and the partnership wound up (0 of 11 searches): the rules as encoded conserve gain.

## Provisions encoded (text read from the local OLRC release point, through Pub. L. 119-138)

| Rule in the file | Provisions |
|---|---|
| contribution of property / money | §721(a), §721(b) with §351(e)(1) (80% test, conservative), §722, §723 |
| who takes the gain on a sale by the partnership | §704(b) (by capital), §704(c)(1)(A) traditional method, §704(c)(1)(C), §704(c)(3), §704(d), §705 |
| borrowing, repayment | §752(a), (b), (d) (liability borne by one named partner) |
| distribution | §731(a)(1), (a)(2), (b); §731(c)(1), (3)(A)(i), (3)(A)(iii), (3)(B), (4), (5); §732(a)(1), (a)(2), (b), (c); §733 |
| mixing-bowl rules | §704(c)(1)(B) (7 years), §737(a)–(d) (7 years), with §707(b)(1)(A), (b)(3) on a deemed-sale loss |
| disguised sale | §707(a)(2)(B) with the two-year presumption of Reg. §1.707-3(c); §707(b)(1) on a loss; Reg. §1.707-5(b) debt-financed exception as a switch |
| basis adjustments | §734(a), (b), (d) ($250,000), §743(a), (b), (d) ($250,000), §754, §755(a), (b) incl. the carryover sentence |
| hot assets | §751(a), §751(b) (hypothetical-sale method), §751(b)(2)(A), (b)(3) 120% test, §751(d) |
| sale of an interest | §741, §742, §752(d), §267(a)(1) between related persons |
| termination | §708(b)(1) (one partner left: deemed liquidation under §§731, 732(b), (c)) |

Read but not in the search (they change character, timing or procedure, not the amounts tracked): §707(c), §724,
§732(d), §735, §736, §708(b)(2), §1061, §1402(a)(13), §199A(c)(4), §163(j)(4), §461(l), §7704, §6221. Not modelled:
how nonrecourse debt is shared (regulations), remedial/curative §704(c) methods, depreciation, death (§1014).

Dollar figures: the only statutory amount used is $250,000 in §§734(d), 743(d) (not indexed).

## Search size

Breadth-first over 11 kinds of move, amounts taken from the position (cash on hand, capital, interest basis, the
value of X, nine tenths of capital). Positions examined, last run:

| Position | Depth | Positions |
|---|---|---|
| S1: A holds X (1,000 / basis 100), B (related) holds Y (1,000 / 1,000), C and D unrelated with cash | 6 | 80,257 |
| S1s: same at 300 / 60 and 300 / 300 (every difference under $250k) | 5 | 11,744 |
| S2: Y has a built-in loss (1,000 / 1,600) | 6 | 88,067 |
| S3: C also holds marketable securities (1,000 / 400) | 5 | 20,995 |
| S4: Y is inventory (1,000 / 400) | 6 | 29,838 |
| S5: S1 with the debt-financed exception on | 5 | 4,284 |
| S6: existing partnership, A's two parcels (200 / 20 each), three related partners, one unrelated | 6 | 24,330 |
| S6b: same in single pieces (400 / 40) | 4 | 60 |
| S7: existing partnership: X, loss asset Y, securities Z | 4 | 26,482 |
| S8 / S8b: loss asset, family holds half / two thirds | 3 | 343 / 217 |

Four questions asked of every position: X sold out of the family for cash with Y kept; cash in hand with X and Y
kept; every asset sold; a loss taken while the family keeps every asset. Plans are grouped by the kinds of move
they use; a group is dropped if a group using fewer kinds does as well.

## Plans that beat the plain sale

| # | Plan (as the search printed it) | Effect vs plain sale | Provisions combined | Class | What could defeat it | Checked |
|---|---|---|---|---|---|---|
| 1 | S1: B contributes Y; A contributes X; wait to year 7; distribute X to B in liquidation; B sells X | family tax now $0 instead of $214,200; the $900k gain sits in Y (basis 100 in A's hands) | §721, §704(c)(1)(B) and §737 clocks, §732(b), §734(d), §708(b)(1) | KNOWN: mixing bowl with a §732(b) basis shift | 7 years of real co-ownership; Reg. §1.701-2; §7701(o); the 2024–25 related-party basis-shifting rules (since withdrawn) | – |
| 2 | S1: same, but at year 7 B sells his interest to D and D is redeemed with X | family has $1,000k cash from D, tax now $0; D holds X at basis 1,000 | as 1 plus §741, §742 | KNOWN: mixing-bowl exit by purchase and redemption | step transaction; §707(a)(2)(B), self-executing since Pub. L. 119-21 | 1 search |
| 3 | S2: plan 1 with Y worth 1,000 / basis 1,600 | family tax now −$142,800 instead of +$214,200: B's 600 loss is taken on X, A's 900 gain sits in Y | §722, §732(b), §734(d); §704(c)(1)(C) does not reach B's outside basis | KNOWN: related-party basis shift | as 1 | – |
| 4 | S6: §754 election; current distributions of the two high-basis assets to A (interest basis 40); the partnership sells A's old parcel at a loss | family tax now −$21,420 (and the same for unrelated D): 360 of basis moved onto the retained parcel (basis 380, value 200) | §732(a)(2), §733, §734(b)(1)(B), §754, §755 | KNOWN: the §754 "basis strip" of Notice 2024-54 | §7701(o); Reg. §1.701-2; total after wind-up unchanged | – |
| 5 | S6: no §754 election; two liquidating distributions, one parcel each (step-up 180 each, 360 in all); every asset then sold | tax now $0 instead of $85,680; A's 360 gain deferred in his interest (basis 40, capital 400). In S6b, one piece with a 360 step-up, the search reaches $0 only by the ordering in item 6 | §732(b), §734(a), §734(d) "with respect to a distribution", §743(d)(2) | VARIANT of the no-election basis shift: splitting under the $250,000 line | deferral only (ends when A takes his capital out, absent §1014); Reg. §1.701-2; a court reading a planned set of distributions as one; §743(d)(2) regulations if ever written to aggregate | 1 search: found the per-distribution reading and no aggregation rule for distributees |
| 6 | S6b, S7: sell the partnership's other capital assets first, then make the liquidating distribution of X, then X is sold | tax now $0 instead of $85,680 (S6b); in S7 A's $214,200 is deferred (family −$142,800 now instead of +$71,400); the mandatory reduction (360; 900) is carried, not applied | §734(d), §755(b) last sentence, §732(b) | VARIANT: the mandatory step-down has nothing to land on | Reg. §1.755-1(c)(4): the carried reduction attaches to the next capital or §1231 property acquired; deferral only, A's interest basis stays low; §1.701-2 | – |
| 7 | S8: partnership three years old, family holds exactly half; distribute B's loss asset Y to related A | B recognises the 600 loss ($142,800) and the family still holds Y (basis 1,000). In S8b (family two thirds) the search no longer returns it | §704(c)(1)(B)(i)–(iii); §707(b)(1)(A) reaches only a distributee owning more than 50% | VARIANT: affirmative use of §704(c)(1)(B) at or under 50% | §267(a)(1) "directly or indirectly" between B and A; Reg. §1.704-4(f) anti-abuse; §7701(o) | 1 search: T.D. 8642 preamble applies §707(b)(1)(A) to the over-50% case |
| 8 | S2, S7, S8, S8b: B's interest is liquidated for cash more than two years after he contributed Y; related A keeps Y. In S2 the family owns 100%: "B contributes Y; wait to year 2; A contributes X; partnership borrows 1,000 borne by A; distribute 1,000 to B" | B recognises 600 ($142,800); A holds Y at basis 1,000 (via §734(d) or §708 termination), so the loss is taken once, early, with no sale outside the family | §731(a)(2); §707(b)(1) excludes "an interest in the partnership"; §267(b) has no partner–partnership pair | CANDIDATE (weak): I do not know it as a published technique | §707(a)(2)(B), now self-executing and with no time limit in the statute: recast as B's sale of Y to the partnership, then §707(b)(1)(A) denies the loss; §267(a)(1) indirect sale; §7701(o); Reg. §1.701-2. Inside a pure family partnership I expect it to fail | 1 search: nothing on point either way |
| 9 | S1, S5, S7: partnership borrows, a partner bearing the debt takes nine tenths of his capital in cash | cash in hand, tax now $0 | §752(a), §731(a)(1), §733 | KNOWN: debt-financed distribution | he still owes the money; §707(a)(2)(B) within two years unless Reg. §1.707-5(b) | – |
| 10 | S2: B sells his interest to D at a loss and buys it back | loss of 600 now | §741 | KNOWN: §1091 covers only stock and securities; not specific to partnerships | sham, step transaction, §7701(o) | – |

Web searches used: 4 of 6 (items 5, 7, 8 and the 2025 change to §707(a)(2)).

## Traps the search ran into (plans that cost more than the plain sale)

- **Cash out of a controlled partnership within two years of contributing loss property** (S2: B contributes Y,
  partnership borrows, 900 to B): a disguised sale at a loss to a partnership the family controls; §707(b)(1)
  denies the loss and the property takes a cost basis. Total tax after wind-up rises from $71,400 to $199,920.
- **Distributing a partner's loss property to his relative inside the 7 years when the family holds over half**:
  §704(c)(1)(B) treats it as a sale, §707(b)(1) denies the loss, and the basis is still written down.
- **Inventory blocks the mixing bowl** (S4): with Y as inventory no plan gets X out below the plain-sale tax;
  §751(b) turns the swap of shares into ordinary income for B and gain for A.
- **A buyer of an interest with no §754 election** who then takes low-basis property out and sells the interest has
  a capital loss now and the gain later on the property (first runs; a timing mismatch, not a saving).
- **Under $250k with only one partner left** (S1s): no step-down is required, but §708(b)(1) ends the partnership
  and §732(b) gives the survivor the low basis anyway. The deferral in item 5 needs a second continuing partner.
- **Both 7-year rules hit at once**: property contributed by one partner going to another who also contributed
  appreciated property triggers §704(c)(1)(B) for the first and §737 for the second.

## Drafting gaps noticed

1. §734(d)(1) tests "a distribution"; the only aggregation authority (§743(d)(2), cross-referred by §734(d)(2))
   speaks of related partnerships and property acquired to avoid the rule, not of several distributions or several
   related distributees (item 5).
2. §755(b), last sentence: a required reduction with no like-character property waits for "subsequently acquired
   property"; a partnership holding only money has nothing to reduce (item 6).
3. §707(b)(1) excludes losses on "an interest in the partnership", and §267(b) lists no partner–partnership
   relationship, so a §731(a)(2) loss between relatives is caught, if at all, only by recharacterisation (item 8).
4. §707(b)(1) is a more-than-50% test while §267 between individuals has no percentage; a §704(c)(1)(B) deemed sale
   is to "the distributee", so a family at exactly half is outside §707(b)(1) (item 7).
5. §707(a)(2) now begins "Except as provided by the Secretary" (Pub. L. 119-21) and has no time limit; the
   two-year presumption is only in the regulations, and there are no regulations at all for disguised sales of
   partnership interests (cash in from one partner, cash out to another, as in several returned plans).
6. §737(b) has no successor rule (§704(c)(3) covers only §704(c)(1) and (2)); §731(c)(3)(A)(i) and §751(b)(2)(A)
   say "contributed by such partner" with no word on a purchaser of his interest. Regulations fill the first.
7. §704(c)(1)(C) limits a built-in loss to "the contributing partner" but leaves his interest basis untouched, so
   the loss still travels to whatever he receives in liquidation (item 3).
8. Not modelled, noted while reading: §1402(a)(13) "limited partner, as such" is undefined; §199A(c)(4)(B)
   excludes guaranteed payments but says nothing of a priority share of income; §1061(c)(4)(A) excepts any
   interest "held by a corporation"; §163(j)(4)(B)(iii)(II) turns unused excess business interest into interest
   basis on a disposition. The local text of §461(l)(1) reads "before January 1, 2027" in both subparagraphs
   while §461(l)(3)(C) indexes for years after 2025; worth checking against the Act.

## Limits of the model

Fair values are constant, so there is no post-contribution appreciation and no reverse §704(c) layer; one asset
per distribution; nonrecourse debt sharing, remedial methods, depreciation and death are left out; §751(b) is the
hypothetical-sale approximation with a conservative full-gain charge to whoever takes over a hot share; a
disguised sale of part of a property is prorated against the whole property each time. Items 5–8 rest on the
statutory text as encoded; none was tested against the regulations beyond the points listed.
