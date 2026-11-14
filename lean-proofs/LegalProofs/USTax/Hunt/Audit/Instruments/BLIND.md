# Blind replication: Instruments

Run: `lake env lean LegalProofs/USTax/Hunt/Audit/Instruments/Blind.lean` (about 85 s). Output saved in `run.txt`.

## Result

Baseline (never trade): tax 40.8% x $10,000 = $4,080; after-tax wealth **$195,920**.

Best value found: **$197,620**, a gain of **$1,700**, reached by three families. No plan does better in any
of the five encodings run. The gain is the rate difference (40.8% - 23.8%) on $10,000: the capital gain dividend
is long-term gain, the matching fall in the share price is taken as a short-term loss, the short-term loss
absorbs the $10,000 short-term gain from other sales, and $10,000 of long-term gain is left.

Total net gain is $10,000 in every plan (dividend and price fall cancel), so 23.8% x $10,000 = $2,380 is the
lowest tax the netting rules can give; the best plans reach it. A second lot adds nothing.

| Family | Plan | Dividend | Loss | Tax | Value |
|---|---|---|---|---|---|
| A. Hold past 6 months | buy 1,000 on day 1-9; sell on day 185+ (day 193+ if bought day 9) | $10,000 long-term (§852(b)(3)(B)) | $10,000 short-term (§1222(2); §852(b)(4)(A) off, held more than 6 months) | $2,380 | $197,620 |
| B. Wash sale into new shares | buy day 1; sell day 10 (loss $10,000 disallowed, §1091(a)); buy 1,000 on day 10 (basis $100,000, §1091(d)); sell day 39 | $10,000 long-term | first loss: disallowed. Loss on the new shares $10,000 short-term: no capital gain dividend was paid on those shares, so §852(b)(4)(A) does not reach them | $2,380 | $197,620 |
| C. Two lots, one sold into the other | buy 2,000 day 1; sell lot 1 day 10 (disallowed, basis to lot 2 = $110,000); sell lot 2 day 39 | $20,000 long-term | lot 2 loss $20,000: $10,000 long-term (to the extent of its own dividend, §852(b)(4)(A)), $10,000 short-term | $2,380 | $197,620 |

Runners-up:

- Buy before day 10, sell within 6 months, no repurchase: dividend long-term, loss long-term (§852(b)(4)(A)); tax
  $4,080; value $195,920; gain $0.
- Plans in which a loss is disallowed and no share is left to take the basis: value $195,240 (-$680), $193,540
  (-$2,380), $191,160 (-$4,760).

Family A does not depend on any judgment call below except the length of "6 months". Families B and C depend on
judgment call 1; with the opposite reading (`carryRci = true`) B returns to $195,920 and C needs the second lot
held past 6 months.

## Provisions encoded

- §852(b)(3)(B): capital gain dividend treated as gain on a capital asset held more than 1 year.
- §852(b)(3)(C): definition. The task states the $10 is a capital gain dividend; clause (ii) excess reported
  amounts not modelled (assumed nil).
- §852(b)(3)(D): undistributed gains. Read; the fund designates none in the position, so no move uses it.
- §852(b)(4)(A): loss on a share held 6 months or less is long-term to the extent of the long-term amount paid
  with respect to that share. (B), (E): exempt-interest dividends, none here. (D): periodic liquidation plan,
  "to the extent provided in regulations", none here.
- §852(b)(4)(C) with §246(c)(3): day of disposition counted, day of acquisition not; §1223(3) tacking switched
  off; no day more than 6 months after the ex-dividend date counted. §246(c)(4): reductions for options, short
  sales and offsetting positions; the position has none, so zero.
- §1091(a): loss disallowed where substantially identical stock is acquired from 30 days before to 30 days
  after the sale (same day included). (d): new shares take old basis adjusted by the price difference. (b), (c):
  matching left to regulations; lots are equal size, matched one to one, earliest first. (e), (f): short sales,
  contracts: not available.
- §1223(3): holding period of the loss shares added to the new shares. Other paragraphs of §1223 (exchanges,
  carryover basis, stock distributions, rights, decedents) have no move in this position.
- §1222: short/long by "more than 1 year"; netting in (5)-(11).
- §1211(b), §1212(b): net loss up to $3,000 against other income, rest carried forward. Encoded; never reached,
  since net gain is $10,000 in every plan.
- §1(h), §1411: 23.8% on net capital gain, 40.8% on net short-term gain.

## Judgment calls

1. §852(b)(4)(A) is applied share by share ("such share"). A loss disallowed by §1091 and added to the basis of
   new shares on which no capital gain dividend was paid comes out short-term when those shares are sold.
   Variant `carryRci = true` makes the long-term character follow the basis.
2. "6 months" = 183 model days and "1 year" = 365 (never reached in a 250-day calendar). Variant: 125 and 250.
   Same values.
3. §1091(a): the purchase of the very lot being sold is not itself the disqualifying acquisition. Variant
   `selfCounts = true`: best value unchanged (family A).
4. §1091(a): a purchase within the prior 30 days of other shares that have already been sold again still
   disallows the loss (literal reading), and then nothing carries the basis. Variant `soldCounts = false`: best
   value unchanged; family B can then finish on day 11.
5. Each acquisition disallows one loss only.
6. The $200,000 is the whole of the cash; tax on the $10,000 is paid from it. Cash earns nothing.
7. A net capital loss would be valued at 37% on up to $3,000 with the carryover at zero. Not reached.
8. A sale on day 10 is at $90 and the seller has received the dividend.

## Silences

- §852(b)(4) does not say what happens to its recharacterisation when the loss is disallowed under §1091 and
  moves into the basis of other shares.
- §1091(a) does not say whether the shares sold can be their own "acquired" shares, or whether shares bought and
  already resold count.
- §1091(d) does not say where the basis goes when the acquired shares are no longer held.
- §1091(b), (c) and §246(c)(4) leave matching and holding-period reductions to regulations.
- No provision read says how "6 months" is counted in days.
- §1223(3) tacks the holding period for the subtitle; §246(c)(3)(B) removes it for the 6-month test only.

## Search

- State: day, cash, lots held (acquisition day, basis, tacked days, dividend received, used as replacement),
  losses still open to a later repurchase, recently sold acquisitions, running short/long gain and loss totals.
- Moves: buy 1,000 shares; sell a lot held; each on a day from 21 natural days (1, 8-11, 39-42, 70-73, the
  6-month boundaries from day 1 and from the ex-dividend day, 250).
- Breadth-first, depth 6 moves, at most 4 purchases, deduplicated with `Std.HashSet`.
- Positions: 167,502 (main encoding); 175,537; 139,936; 169,501; 164,104 in the variants.
- Limit: plans longer than 6 moves were not searched. The $2,380 floor above shows they cannot do better under
  these rules.
