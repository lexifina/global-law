# Corporate: C corporations and their shareholders

File: `LegalProofs/USTax/Hunt/Corporate.lean` (run: `lake env lean LegalProofs/USTax/Hunt/Corporate.lean`, 1m50s).
Output of the final run: `tools/hunt/out/Corporate/final.txt`; earlier wider runs `tools/hunt/out/Corporate/run_*.txt`.

## Setting

Amounts in $ thousands. **C**: 10,000 cash (retained earnings, E&P 10,000), one asset worth 30,000 with zero basis.
**A** holds all 400 shares, basis 1,000. **K** = A's adult child, **S** = A's sibling, **P** = a second corporation
wholly owned by A. Top rates, 2025/2026: 21% corporate, 23.8% dividends and long-term gain (20% + 3.8% NIIT),
31.8% on "section 1202 gain", 40.8% short-term. No operating income during the plan, no discounting.

Baselines: full exit by asset sale + dividend = 14,320 tax on 40,000 (35.8%). Keep the business and pay out the
10,000 cash as a dividend = 2,380.

## Provisions encoded (text read with `tools/hunt/sec.py`)

§11(b); §1(h)(4), (7), (11); §1411(a), (c); §301(b), (c); §316(a), (b)(2); §312(a), (n)(7); §302(a), (b)(2), (b)(3),
(c)(2)(A)–(B), (d); §318(a)(1), (2)(C), (5)(A)–(B); §311(b) (via asset sale); §331; §336(a); §243(a), (b)(1), (c);
§246(c) (assumed met through tacked holding); §1059(a), (c), (e)(2); §351(a); §358(a); §362(a); §1223(1), (2);
§1015(a); §1202(a)(1), (4)–(6), (b)(1), (2), (4), (c)(1)–(3), (d)(1), (h)(1), (2), (4); §531, §532, §533,
§535(a), (b)(1), (3), (c)(2); §541, §542(a), §543(a)(1), §545(a), (b)(1), (3); §561, §562(a), §563;
§1361(b)(1); §1362(a), (b); §1366(a), (f)(2); §1367(a); §1368(b), (c), (e)(1); §1371(c); §1374(a)–(d).

Read but not encoded (stated in the file header): §304, §305/§306, §332/§337, §381(c)(2), §1045, §4501 (public
corporations only, §4501(b)), §55(b)(2)/§56A (over $1bn only), §269, §1244, §165(g)(3), §267, §357, §362(e), §382,
§163(j), §7872. Their absence matters for: a second class of stock, cash sales to P, liquidating C into P, rollovers.

Conservative readings chosen: a year's E&P deficit does not reduce accumulated E&P for distributions in that year;
§302(b)(1) never applies; the "no tax-avoidance purpose" escape in §302(c)(2)(B) is never available; the §532 purpose
is presumed and P has no reasonable business needs; capital losses are worthless; S election ends QSBS status.

## Search size

Breadth-first over 13 kinds of move (dividend, asset sale, liquidation, redemption, stock sale, gift, §351
contribution, P distribution, P liquidation, P stock sale, P's sale of C stock, S election, wait 1/2/5 years),
fractions 1, 1/2, 1/4 (1/5 for sales and gifts), depth 4–5. Final run: 9 searches, 2,347 to 146,880 positions each
(about 730,000 in total, 1.2m moves tried, 65–226 move families each). Wider depth-5 runs: up to 363,272 positions.

## Plans found

| # | Plan (as printed by the search) | Tax vs baseline | Provisions combined | Class | What could defeat it | Checked |
|---|---|---|---|---|---|---|
| 1 | QSBS: A sells 1/5 of C stock; contributes the other 80% to P under §351; sells the P stock | 3,855 vs 5,712 for a one-issuer sale (14,320 plain). Second $15m limit: +7,800 excluded | §351, §1202(h)(4)(A), (D), §1202(b)(1) "stock issued by such corporation" | **CANDIDATE** | Statute: nothing; the limit is per issuer and P is the issuer. Outside: §1202(k) regulations against "shell corporations" (authority exists, no regulation issued); §7701(o); step transaction, and loss of §351 control if the P sale is prearranged (then the exchange is taxable and uses C's limit: no gain, no loss); buyer must take two entities. (h)(4)(B) caps P-stock gain at the built-in gain unless P is a qualified small business at the transfer; for an immediate sale that cap does not bind | 2 searches: FBT, Tax Adviser, startup-law pieces describe (h)(4) carry-over, none addresses a second limit |
| 2 | QSBS: sell part this year, the rest next year | 4,283 vs 5,712 | §1202(b)(1)(A) lifetime dollar limit, (B) ten times basis per year | KNOWN (dollar limit first, 10× basis in later years) | — | — |
| 3 | QSBS: A sells part, gives the rest to K or S, who sells | 2,141 (family) | §1202(h)(1)–(2), §1015, §1202(b) per taxpayer | KNOWN (gift stacking) | assignment of income if sale already agreed | — |
| 4 | QSBS, business kept: A gives 1/2 to S, C redeems 1/2 of A's shares | 0 vs 2,380 | §318(a)(1) has no siblings, §302(b)(2), §1202(a), §1202(c)(3) window passed | KNOWN (exchange redemption of QSBS); costs A half the company | §302(b)(2)(D) series; gift tax | — |
| 5 | Not QSBS: stock sale, or S election + wait 5 years + liquidate | 9,280 vs 14,320 | §1001; §1362, §1374(d)(7), §1367, §331 | KNOWN | — | — |
| 6 | Not QSBS, business kept, P has an E&P deficit of 8,000 and A a basis of 8,000 in it: A contributes C stock to P; C pays the dividend to P; next year P distributes | 1,146 vs 2,380 (only under the literal §535(c)(2) reading; +35 under the 250 credit; nothing if P is a PHC) | §351, §1223(2) tacking so §1059 does not bite, §243(c) 65%, §316(a) (P's deficit absorbs the dividend once it is accumulated), §301(c)(2) | **VARIANT** (deficit-E&P holding company, used here to turn a locked capital loss on P stock into basis recovery against C's dividends) | §531 if the minimum credit is only 250, and §1561 gives P and C one credit; §541 + §316(b)(2) if dividends are ≥60% of P's adjusted ordinary gross income; §269(a)(1) (P acquires control of C to secure the §243 deduction); §7701(o); conduit/substance over form; P must have no current E&P in the distribution year. §381(c)(2)(B) blocks the same result on a §332 liquidation but says nothing about dividends | 2 searches: no source on a deficit under §535(c)(2); old cases confirm deficits net against later earnings |
| 7 | QSBS corporation with no E&P pays a pro rata distribution | 0 vs 2,142, **only if** §301(c)(3) gain is "gain from the sale or exchange of" the stock | §301(c)(2)–(3), §1202(a) | CANDIDATE reading, not a plan under the conservative encoding | §301(c)(3) says "property", not "the stock" (compare §302(a), §331(a)); §1202(b) speaks of "dispositions" | 1 search: nothing on point |

Other families the search returned (all dominated, all ordinary): liquidation instead of dividend (+240 to +3,808,
basis recovery and §1202 on §331 gain); sibling redemption without QSBS (+60, basis recovery only).

## Traps found (rules that cost money)

- P selling its C stock and distributing: 13,922, almost the plain double tax; §1202 is closed to corporations.
- S election ends QSBS status (§1202(c)(2)(A)): with QSBS the S route (9,282) loses to every QSBS route.
- A gift to K blocks the §302(c)(2) waiver for 10 years for both A and K; K's redemption is then a §301 distribution,
  and when all of K's shares go the basis of those shares is stranded.
- Redemption within 2 years of issue disqualifies every related holder's stock (§1202(c)(3)(A); §267(c)(4) includes
  siblings although §318 does not).
- Asset sale and distribution in one year: the sale gain is current E&P, so a distribution made earlier that year is
  a dividend even if E&P was nil when paid (§316(a)(2)).
- P as a personal holding company: §316(b)(2) turns any distribution into a dividend and §541 takes 20% of the rest.
- Stock under 2 years old in P's hands (tacked): §1059 strips P's basis by the untaxed part of the dividend.

## Drafting gaps noticed

1. §1202(b)(1) limits gain per **issuer**; §1202(h)(4) makes holding-company stock QSBS with the old acquisition date
   but does not treat the holding company as the same issuer. The $75m test aggregates parent and subsidiary
   (§1202(d)(3)); the dollar limit does not. By the same text a founder could hold 20% of C directly and 80% through P
   from formation (both original issues, P qualifying by look-through to its subsidiary under §1202(e), which I did not read here); reasoning only, not
   modelled and not a search result.
2. §535(c)(2): "the amount by which $250,000 exceeds the accumulated earnings and profits" is not floored at zero
   E&P; a deficit enlarges the credit on the literal text.
3. §381(c)(2)(B) quarantines a deficit after a liquidation or reorganisation; nothing does so for a dividend received.
4. §301(c)(3)(A) "sale or exchange of property" v. §1202(a) "sale or exchange of qualified small business stock".
5. §1202(a)(6)(B) fixes the acquisition date after §1223, so gifts, §351 exchanges and §1045 rollovers of pre-July-5,
   2025 stock stay under the old $10m / 5-year rules: no gap found there.
6. §267(c)(4) family (siblings in) v. §318(a)(1) family (siblings out) within §1202(c)(3) and §302.

## Honest summary

One plan I do not know as a published technique (the second per-issuer limit through an 80% holding company); I could
not confirm it is unpublished, and it is exposed to §7701(o) and unissued §1202(k) regulations. One variant that
depends on a reading of §535(c)(2) and on P not being a personal holding company. Everything else the search returned
is standard practice. Web searches used: 5 of 6.
