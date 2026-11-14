# Blind replication: Residence

Run: `lake env lean LegalProofs/USTax/Hunt/Audit/Residence/Blind.lean` (a few seconds).

## Provisions encoded

| Provision | What the model takes from it |
|---|---|
| §877(e)(2), §877A(g)(2)(B), (g)(3)(B), (g)(5) | Long-term resident = LPR in 8 of the last 15 taxable years (P: 12+). Giving up the card makes P an "expatriate"; expatriation date = the day LPR status ends. |
| §877(a)(2)(A),(B),(C), §877A(g)(1)(A) | Covered expatriate if average tax > $206,000, or net worth >= $2,000,000, or P fails to certify. P fails (A) and (B) on the facts ($60,000; $1,500,000), so covered status turns only on the certification. (g)(1)(B) exceptions concern dual citizens at birth and minors; not P. |
| §877A(a)(1), (a)(2), (a)(3) | Covered expatriate: all property treated as sold at FMV the day before the expatriation date; gain reduced by $890,000; later realised gain adjusted by the deemed gain "determined without regard to paragraph (3)" (so basis becomes $1,100,000, not $210,000). |
| §877A(g)(1)(C) | A covered expatriate taxed as a US resident for a period after the expatriation date is not a covered expatriate for §2801 during that period. |
| §877A(b), (c), (d), (e), (f), (h) | Read; no move. P holds no deferred compensation, tax-deferred account or trust interest on the facts; the deferral election only moves the payment date; (h)(2) step-up needs property held when P first became resident (not on the facts). |
| §7701(b)(1)(A)(i) | LPR at any time in the calendar year: resident for the year. |
| §7701(b)(1)(A)(ii), (b)(3) | Present all year: resident with or without the card. Abroad all year (0 days < 31): test not met. |
| §7701(b)(2)(B) | Surrender year: the part after the last LPR day is nonresident only if P has a closer connection abroad and is not a resident at any time in the next year. Modelled as a pending item settled by next year's presence. |
| §7701(b)(6) | LPR status ends when given up. The treaty-residence route in the flush sentence is not a move. |
| §7701(b)(10) | Resident 3+ consecutive years, ceases, resident again before the close of the 3rd following calendar year: the gap is taxed as in §877(b). |
| §871(a)(2) | Nonresident alien present 183+ days: 30% on US-source capital gains. Otherwise no tax on the stock sale. |
| §897(a) | Outline only: nonresident's gain on a US real property interest is taxed as effectively connected. The stock is assumed not to be one. |
| §2801(a), (b), (c), (e)(1), (f) | 40% on a US citizen's receipt of a gift from, or property passing at the death of, a covered expatriate, above the §2503(b) amount per recipient. |
| §1(h), §1411 | Flat 23.8% on a resident's gain, as instructed. |

## Search

State: year, presence, card, surrender year, covered flag, who holds stock / cash, P's basis, children's basis, tax so
far, pending last-year-rule gain and gift, nonresident gain exposed to §7701(b)(10).
Moves: `open inUS|abroad` (once per year), `giveUp certify|noCert`, `sell`, `giftStock`, `giftCash`, `kidsSell`,
`endYear`, `die`. Exhaustive depth-first over every legal sequence in three years.
**315 distinct positions, 928 complete plans** (564 in tier 1, 364 in tier 2).

Tier 1 = P sells and the cash passes, using only the listed provisions. Tier 2 = the children end up selling stock,
which needs a basis rule (§1014 / §1015) that is not in my list; reported separately.

## Results (total US tax, dollars)

Baseline `inUS sell die`: **238,000**.

Tier 1:

| Tax | Gain vs baseline | Plans | Family (shortest example) |
|---|---|---|---|
| 0 | 238,000 | 46 | `abroad giveUp+certify sell die` : certify, become a non-covered expatriate, live abroad, sell as a nonresident alien, cash passes by gift or at death, never return inside the horizon |
| 26,180 | 211,820 | 62 | `inUS giveUp+noCert sell giftCash` : decline to certify, become a covered expatriate, pay 23.8% on $110,000 of deemed gain, sell with no further gain, be US resident when the cash passes so §2801 is off |
| 200,000 | 38,000 | 6 | certified exit, sell abroad, then come back in year 3: §7701(b)(10) |
| 238,000 | 0 | 326 | sell as a resident (any order of the other moves that leaves P resident at sale) |
| 450,980 | -212,980 | 62 | covered expatriate who is abroad at the gift or death: 26,180 + §2801 424,800 |
| 662,800 | -424,800 | 62 | sell as resident, then become covered and transfer from abroad: 238,000 + 424,800 |

Restricted to plans where P is in the US all year every year (92 plans): best is **26,180** (20 plans), all of the
form "give up the card without certifying, then sell"; everything else is 238,000.

Tier 2 (outside the list): `inUS die` with a §1014 basis gives 0 (48 plans); covered-expatriate variants 26,180;
gift of stock with carryover basis 238,000; covered and abroad 450,980.

## Judgment calls

1. §877A(a)(2) flush language read literally: the later-gain adjustment is the full deemed gain ($1,000,000), not the
   $110,000 actually taxed. This is the whole of the 26,180 result.
2. The deemed sale is taxed at the resident 23.8% (P is LPR the day before).
3. §877A(g)(1)(C) "subject to tax as a ... resident" read with §7701(b) (substantial presence), although §7701(b)
   says it does not apply to subtitle B where §2801 sits.
4. Abroad all year = "closer connection to a foreign country" for §7701(b)(2)(B); P remains LPR while abroad with the
   card (no abandonment finding).
5. A plan that ends in the surrender year, or with P abroad in year 3, is treated as not becoming resident afterwards.
   A return in year 4 could still trigger §7701(b)(10) (through the 3rd following calendar year).
6. §877(b) rate for the §7701(b)(10) case taken as a flat 20% without §1411; §877(b) itself is not in my list.
7. §2801 rate 40% (§2001(c) not in list), §2503(b) amount $19,000 for 2025, two children.
8. The stock is not a US real property interest.
9. §877(a)(2)(C) asks for a certification of five years' compliance; "decline to make it" is taken as a free choice
   as the task states, with no other consequence.
10. Children taxed at the same flat 23.8% in tier 2.

## Silences

- Estate and gift tax (chapters 11, 12) on P's own transfers: not in the list; taken as nil at a $1.5M net worth.
  §2801(e)(2) (transfers shown on a timely gift or estate tax return) therefore not modelled.
- Basis in the children's hands (§1014, §1015): not in the list; tier 2 only.
- Whether the §877A(a)(2) adjustment follows the stock to a donee: the text does not say; tier 2 assumes it does.
- Nothing in the listed text makes a deliberate failure to certify ineffective, and nothing limits the mark-to-market
  to people who actually leave: an expatriate is defined by losing LPR status, not by ceasing to be resident.
- §6039G reporting and any penalty for not filing the statement: not in the list.
- Immigration consequences: assumed away by the task.
- Foreign tax in the country P moves to: outside the objective.
