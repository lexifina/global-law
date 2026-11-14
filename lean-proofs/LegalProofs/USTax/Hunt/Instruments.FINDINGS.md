# Instruments: findings

File: `LegalProofs/USTax/Hunt/Instruments.lean` (one file, `import Std`). Run: `lake env lean LegalProofs/USTax/Hunt/Instruments.lean`
(35 s, 18 searches, 119,555 positions examined, 38,905 final positions). Scratch and raw output: `tools/hunt/out/Instruments/`
(`final.txt` is the output the numbers below come from).

## What the model is

One investor, unit positions, two tax years. Every instrument in a "world" has the same total-return path, and every
plan must hold the prescribed net exposure on leaving each date, so **pre-tax wealth is identical for every plan** and
only tax differs. Score: future value of all tax at 4% (ordinary 37%, long-term and qualified dividends 20%, §1411
3.8%, 2025 rates; $3,000 of §1211(b) at 37%). Two valuations: everything sold on the last day ("sold"), or the last
position kept untaxed ("kept"). The "plain plan" trades only the first instrument, long only, with the fewest trades.

Worlds: stock (FundA, FundB not substantially identical, index future); digital (coin, grantor-trust share, coin
future); distributions (FundA, a RIC paying a 10% capital gain dividend, a stock paying a 3% dividend).

## Provisions encoded (text read from the local release point)

| Provision | Rule in the file |
|---|---|
| §1222, §1223(3) | holding period, tacking after a wash sale |
| §1091(a), (d), (e), (f) | wash sales both directions in time, basis shift, short-sale version |
| §1233(a), (b), (d), (e)(1)–(2) | short-sale character, holding-period reset, long-term loss |
| §1259(a), (b), (c)(1)(A),(C),(D), (c)(3), (e)(1)–(2) | constructive sales, closed-transaction exception with the 60-day unhedged test |
| §1092(a)(1), (a)(3)(A), (c), (d)(3), (d)(5) | loss deferral to unrecognized gain, year after year |
| Temp. Reg. §1.1092(b)-1T(c), -2T(a), (b) (`regs = true`) | holding period and 60/40 loss character in straddles |
| §1256(a)(1)–(4), (b) | mark to market, 60/40 |
| §1211(b), §1212(b), §1212(c) | $3,000, carryovers by character, 1256 carryback (election tried both ways) |
| §1(h)(11)(B)(iii), (D)(ii); §246(c)(1),(3),(4); §1059(c)(1)–(2) | 61-day test, related payments, extraordinary dividends |
| §852(b)(3)(B), (b)(4)(A)–(C), (b)(5) | capital gain dividends, six-month loss rules, exempt-interest dividends |
| §263(h)(1)–(4), §163(d)(1)–(4) | payments in lieu on short sales, investment interest limit, carryforward, election (last year only) |
| §1411 | 3.8% on net gain and dividends |

Not encoded and not searched (said plainly): §§72, 7702, 7702A, 101, 1035, 264 (annuities, life insurance); §§171,
1272, 1276–1278 (premium, OID, market discount); §§103/265; §475(f); §1260; §852(b)(6); identified straddles and the
mixed-straddle elections; options; §263(g).

## Plans the search returned

Dollar effects are per unit position ($100,000 at price 100), against the plain plan, from `final.txt`.

| # | Plan (run) | Effect | Provisions combined | Class | What could defeat it |
|---|---|---|---|---|---|
| 1 | **Capital gain dividend, then a wash sale** (C2, check lines). Buy RIC shares the day before a 10% capital gain dividend; on the ex-date sell them and buy the same shares back; sell the new shares 33 days after the first purchase. Dividend is long-term gain; the loss comes out short-term. | saves $1,768 per $10,000 of dividend (17 points), same as #2 but in 33 days instead of 6 months | §852(b)(3)(B); §852(b)(4)(A) ("such share"); §1091(a), (d); §1223(3) | CANDIDATE | Text: §852(b)(4)(A) recharacterizes the loss "on the sale or exchange of such share"; that loss is disallowed by §1091 and moves into the basis of new shares that received no dividend; nothing carries the character. A court could read the replacement as "such share", or disregard the sale-and-rebuy under §7701(o)/step transaction (it changes nothing economically). Needs short-term gains at least equal to the dividend. Under the model's strict §1091(a) reading a sale within 30 days of the first purchase loses the loss altogether (check line: $45,281 vs $42,806). No regulation or commentary found on the interaction. |
| 2 | **Capital gain dividend, held past six months** (C1, C2). Same purchase, hold 201 days, sell at the ex-dividend loss. | saves $1,768 per $10,000 | §852(b)(3)(B), (b)(4)(A), (C); §1222 | VARIANT | Nothing in the statute: six months is its own line, and §1(h)(11)(D)(ii) reaches only qualified dividend income. Six months of unhedged exposure to that fund (§246(c)(4) tolls the count). Useless without short-term gains. Sold at 1 or 33 days: no saving (check lines). |
| 3 | **Mixed straddle across the year end** (B1, B2, check lines). No net exposure: long index future, short a fund that is not substantially identical; hold over 31 December; close both in January. Market up 30: future gain is marked 60/40 in year 1, the fund loss falls in year 2 as 60/40 and its long-term part offsets year-2 short-term gains. | saves $2,693 (9% of the move); wrong direction: $0; both legs closed in year 1: $0; if year 2 also has long-term gains: costs $367 | §1256(a)(1), (3); §1092(a), (d)(5); Temp. Reg. §1.1092(b)-2T(b)(2); §1222 netting; §1212(b) | CANDIDATE (weak) | The search knew the price path; a real taxpayer gets the saving only when the future leg wins. The pure form has no profit motive: §165(c)(2) and §7701(o) are the obvious answers. Needs short-term gains and no long-term gains in year 2. If the short leg is substantially identical to the future (model's reading), §1091(e)(1) kills the loss (check line: costs $9,547). Financing cost not modelled. Commentary found covers the "killer rule" only, not the cross-year residue. |
| 4 | **Short over a distribution, hedged with a different fund** (C3 vs C4). Taxpayer with a $300,000 capital loss and $50,000 interest income: short the distributing fund, long another fund, keep the short open more than a year. Payment in lieu is investment interest; the short's gain is absorbed by the capital loss. | saves $4,243 per $10,000 paid | §263(h)(1)–(4); §163(d)(3)(C), (4); §1211(b) | VARIANT | The unhedged version is old and KNOWN (§263(h) is the 1984 answer). Hedged with similar-not-identical property it works only if no regulations exist under §263(h)(4)(B); none found, not confirmed. With such regulations: $0 (C4). |
| 5 | Sell at a loss, buy a non-identical substitute (A1) | $3,727 sold, $8,487 kept | §1091(a) | KNOWN: tax-loss harvesting | substitute tracks imperfectly |
| 6 | Sell a digital asset at a loss and buy it back the same day (A2) | $3,727 / $8,487 | §1091(a) "stock or securities" | KNOWN: crypto wash-sale gap | §7701(o); legislation |
| 7 | Short a digital asset against the long and keep both (A7) | whole tax, $16,972, deferred while kept | §1259(b)(1); §1233(e)(2)(A) | KNOWN: crypto short against the box | §1092 still defers losses; borrow cost |
| 8 | Short against the box in December, closed by 30 January, 60 days unhedged (A5) | $652 (one year's deferral) | §1259(c)(3) | KNOWN | needs the unhedged window |
| 9 | Hedge an appreciated fund with a short of a different fund, keep both (A6) | $16,972 deferred while kept | §1259(c)(1) "substantially identical" | KNOWN; partly a model artifact (FundB tracks perfectly) | §1259(c)(1)(E) regulations; a perfect hedge is likely "substantially identical" |
| 10 | Section 1256 future for a holding under a year, with a loss harvest on the way (A9) | $4,420 | §1256(a)(3) | KNOWN: 60/40 | mark to market if held over year end |
| 11 | Dividend held 61 days, then sold at the ex-dividend loss (C1) | $531 per $3,000 | §1(h)(11)(B)(iii), §246(c) | KNOWN: dividend capture | 61 days at risk |

Statute alone (`regs = false`) the search also finds holding periods ageing inside a hedge: $12,227 (A3), $7,452 (A8),
$5,100 (B4). All three vanish with Temp. Reg. §1.1092(b)-2T(a). They are not plans; they show how much rests on a 1985
temporary regulation.

Nothing beat the plain plan in A4 (appreciated fund, exit wanted, fund and its future only) or A10 (up then down).

## Traps (rules that cost money)

- Closing a short at a loss within 30 days of selling substantially identical long property: §1091(e)(1) disallows
  the loss and the section gives no basis rule to recover it (check line: $51,163 vs $41,616).
- Replacing a fund sold at a loss with its index future (if a contract to acquire): wash sale, and the loss returns
  60/40 at the year-end mark.
- Section 1256 leg in a straddle with long-term gains elsewhere: gain taxed a year early, nothing back (B3, −$367).
- Up one year, down the next in a future: tax on the mark; §1212(c) only reaches prior section 1256 gain (A10).
- Buying the dividend and selling within six months without more: no benefit at all (C2 check lines, $42,806).
- A long position's dividend is not qualified while any short in the world pays in lieu on the same date.

## Drafting gaps noticed

1. §852(b)(4)(A) and (B), §857(b)(8) and §1(h)(11)(D)(ii) attach to "such share"; §1091(d) carries basis, not
   character; §852(b)(4)(C) switches off §1223(3) only for counting days. No ordering rule between §1091 and
   §852(b)(4)(B): the file disallows under (B) first (conservative); the other order would free the loss.
2. §1(h)(11)(D)(ii) covers extraordinary qualified dividends only; a capital gain dividend of any size is outside.
3. §1259(b)(1), §1091(a), §1233(e)(2)(A): digital assets are in none (they are in §1092).
4. §1092(b)(1) leaves holding-period and character rules wholly to regulations; §263(h)(4)(B) and §1259(c)(1)(E)
   likewise.
5. §1091(e) says "rules similar to" (a) and has no basis provision of its own.
6. §1260(c) (read, not modelled): "financial asset" is an interest in a pass-thru entity, so a swap on an index itself
   or on one C corporation is outside while a swap on the index ETF is inside.

## Sources checked (6 searches, standard mode)

No source found describing #1 or #3; #2 only as the rule itself; #4 hedged form not found.
- https://www.law.cornell.edu/cfr/text/26/1.1092(b)-2T
- https://www.mcdermottlaw.com/insights/when-can-bitcoin-positions-be-taxed-as-mixed-straddles-subject-to-the-special-mixed-straddle-rules/
- https://www.thinkadvisor.com/tax-facts/2024/03/13/7949-how-is-a-shareholder-taxed-when-selling-exchanging-or-redeeming-mutual-fund-shares/
- https://www.statefarm.com/finances/mutual-funds/resources/dividend-capital-gain-distribution-wash-sales
- https://www.govinfo.gov/content/pkg/CFR-2016-title26-vol11/pdf/CFR-2016-title26-vol11-sec1-852-4.pdf
- https://www.thinkadvisor.com/tax-facts/2024/03/13/7530-may-an-investor-deduct-expenses-incurred-in-reimbursing-the-lender-of-stock-in-a-short-sale-for-cash-dividends-paid-on-the-borrowed-stock/

Search results were read as summaries only; the regulations themselves (§1.852-4, §1.1091-1, §1.1092(b)-1T) were not
opened and should be before anyone relies on #1.
