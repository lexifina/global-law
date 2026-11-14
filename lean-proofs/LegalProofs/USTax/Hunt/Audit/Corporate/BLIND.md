# Blind replication: Corporate

Run: `lake env lean LegalProofs/USTax/Hunt/Audit/Corporate/Blind.lean` (from `lean-proofs/`).

## Provisions encoded

| Provision | What the encoding takes from it |
|---|---|
| §1202(a)(1)(B), (a)(5), (a)(6) | Stock acquired after the applicable date and held 5 years or more: 100% of gain excluded. |
| §1202(b)(1), (b)(2), (b)(4)(B), (b)(5)(B) | Per issuer, per year: gain taken into account is capped at the greater of $15,000,000 less prior years' gain taken into account for stock of that issuer, and 10 times the bases disposed of (0 here). Once exceeded, the limit is zero in later years. |
| §1202(c)(1)(B)(i) | Stock acquired for stock is not QSBS unless (h) rescues it. |
| §1202(c)(2)(A), (e)(5) | Active business: N looks through to C when it holds more than 50% of C. |
| §1202(d) | N's gross assets (contributed stock at fair value, $40,000,000 at most) stay under $75,000,000. Not decisive. |
| §1202(h)(4)(A), (B), (D) | N stock received in a §351 exchange for C QSBS is treated as QSBS with the old acquisition date, only if N controls C (80%) immediately after; §1202 applies up to the gain built in at transfer. |
| §1202(i) | Read; (i)(1) excludes stock transfers, so not applied. |
| §1202(a)(2)–(4), (b)(3), (f), (g), (j), (k) | Read; no facts engage them (not pre-applicable-date stock, unmarried, no conversion, no pass-thru, no short position). |
| §351(a), §368(c) | No gain if A holds at least 80% of N immediately after the transfer; otherwise a taxable exchange. |
| §358(a)(1) | N stock takes the $0 basis of the C stock exchanged. |
| §1223(1)–(2) | Holding period tacks; consistent with (h)(4)(A). |
| §1(h)(4), (h)(7) | No "section 1202 gain" at a 100% percentage, so included gain is taxed at 20%, not 28%. |
| §1411(a)(1), (c)(1)(A)(iii) | 3.8% on gain taken into account in taxable income; excluded gain is outside it. |

## Search

- State: year, fifths of C held by A and by N, A's N units by kind (QSBS / not QSBS with $0 basis / fair-value basis), N units held by buyers, a per-issuer §1202(b) ledger for C and for N, included gain.
- Moves: sell one fifth of C; transfer 1–5 fifths to N; sell one N unit of each kind; close the year.
- Breadth-first, deduplicated: 2,104 positions, 13 distinct terminal positions (everything cash after two years).

## Results

| Plan | Excluded | Included | Tax | Saving |
|---|---|---|---|---|
| Baseline: sell all C in one sale | $15,000,000 | $25,000,000 | $5,950,000 | – |
| Best (below) | $30,000,000 | $10,000,000 | $2,380,000 | $3,570,000 |
| Runner-up 1: transfer 4 fifths to N, sell the kept fifth of C and all N stock | $23,000,000 | $17,000,000 | $4,046,000 | $1,904,000 |
| Runner-up 2: mixed transfers, only one N unit qualifies | $16,000,000 | $24,000,000 | $5,712,000 | $238,000 |
| No gain: split C sales over two years; all five fifths into N; N never controlling C | $15,000,000 | $25,000,000 | $5,950,000 | $0 |

Best plan, all in one taxable year (either year):

1. Transfer 1 fifth of C to N. §351 applies; N holds 20% of C, so (h)(4)(D) fails and this N unit is not QSBS.
2. Sell that N unit: $8,000,000, fully taxable. A buyer now holds N stock.
3. Transfer 2 fifths to N. A holds 2 of 3 N units (66.7%), so §351 does not apply: a taxable exchange of C stock, $16,000,000 of eligible gain on stock issued by C ($15,000,000 excluded). The N units take a fair-value basis.
4. Transfer the last 2 fifths. A holds 4 of 5 N units (80%), so §351 applies; N holds all of C, so these N units are QSBS under (h)(4)(A).
5. Sell the 2 fair-value-basis units (no gain) and the 2 QSBS units: $16,000,000 of eligible gain on stock issued by N ($15,000,000 excluded).

Included: $8,000,000 + $1,000,000 + $1,000,000 = $10,000,000. $30,000,000 is the ceiling with two issuers, so nothing in this move set does better.

Spreading sales over two years gains nothing: (b)(4)(B)(i) subtracts prior years' gain from the limit.

## Judgment calls

1. The per-issuer limit is read literally. N stock treated as QSBS is "stock issued by" N and gets its own $15,000,000. Every plan that beats the baseline rests on this.
2. A transfer that fails §351 control is a taxable exchange of C QSBS, its gain eligible under C's limit; N stock received takes a fair-value basis (cost basis assumed; §1012 was not on the list).
3. §351 control is tested mechanically immediately after each transfer, counting N stock already sold to the buyer; successive transfers are separate transactions.
4. (h)(4)(D) is tested per transfer; earlier N units that failed it stay non-QSBS.
5. N stock is taken as meeting the active business test for the whole tacked holding period, including before N existed.
6. Included gain taxed at a flat 23.8%; the §1411 threshold amount is ignored.
7. One N unit is worth $8,000,000; no minority or holding-company discount.
8. The move list is read as allowing several transfers to the one new corporation.

## Silences

- §1202(b) does not say that (h)(4) stock shares the limit of the corporation whose stock was exchanged.
- §1202(k) authorises regulations against split-ups and shell corporations; none is in the text read, none encoded.
- §351(a) says "immediately after" and nothing about pre-arranged sales or step transactions.
- §1202 has no cross-reference to §1411.
- §1202(i)(1) is silent on stock-for-stock exchanges; no basis floor applied to N stock.
- §1202(b)(5) indexing not applied: no indexed figure was given.
