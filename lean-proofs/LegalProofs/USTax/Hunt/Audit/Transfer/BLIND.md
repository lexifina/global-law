# Blind replication: Transfer

Run: `lake env lean LegalProofs/USTax/Hunt/Audit/Transfer/Blind.lean` (about 10 s). Nothing outside this folder was read
except the brief and `tools/hunt/sec.py` output.

## Provisions encoded

| Provision | What the model takes from it |
|---|---|
| §2001(a)-(c) | Estate tax = tentative tax on (taxable estate + adjusted taxable gifts) less gift tax payable; flat 40% (task figure). (d), (e) read; never engaged (no split gift is includible in an estate). |
| §2010(a), (c)(1)-(5), (d) | Credit = tentative tax on $15,000,000. W has no DSUE: H's exclusion was used up, N does not die. |
| §2044 | Trust is in W's gross estate only if §2519 "did not apply with respect to a disposition by the decedent of part or all of such property": any §2519 disposition switches §2044 off. |
| §2056(b)(7) | Position only: the trust is QTIP, W holds the qualifying income interest. |
| §2207A(a), (b) | Estate tax on the trust is recoverable from it (neutral for the objective). Gift tax by reason of §2519 property: W "shall be entitled to recover" the incremental tax; she may recover all of it or only what she cannot pay herself. |
| §2501, §2502, §2505, §2511 | Cumulative gift tax, credit, tax paid by donor; one calendar year. |
| §2513 (all) | A gift by a spouse to a third party is half the other spouse's, only with both consents, only for gifts made while married; consent covers all gifts of the year; joint and several liability for the gift tax. |
| §2519 (all) | Disposition of all **or part** of the income interest = transfer of all interests in the property other than the income interest. |
| §2523 | Read; no move uses it (the move list has no gift from W to N). |
| §2631, §2632 (outline), §2641, §2642(a) | $15,000,000 exemption each; deemed allocation to lifetime direct skips unless elected out; GST tax = 40% x inclusion ratio. |
| §2652(a) (all) | Transferor = donor or decedent; split gifts are split for chapter 13; no (a)(3) election. |
| §2612, §2613 | A gift to G or to a trust wholly for G is a direct skip. The trust remainder goes to C, a non-skip person: no GST event on the trust. |

## Moves

Marry N; give $5M or $10M of own property to C, G or a trust for G; give 100%, 50% or 1% of the income interest to C,
G or a trust for G; W consents; N consents; W or N elects out of deemed GST allocation; W recovers all the gift tax
she may (default: only the shortfall); W dies leaving own property to C or G. Breadth-first to exhaustion, states
deduplicated.

## Judgment calls

1. **Value of the income interest.** The position gives no age and says W dies as the last step. Headline runs value
   it at $0 (so the §2519 transfer is the whole $100M). Sensitivity runs at $20M and $40M.
2. **§2513 applied to a §2519 transfer.** §2519 says the disposition is "treated as a transfer" for chapter 12; §2513
   speaks of "a gift made by one spouse to any person other than his spouse". I treated the §2519 transfer as such a
   gift, so it splits. This is the whole of the marriage gain.
3. **§2207A(b) and the half attributed to N.** Text: tax paid "with respect to any person by reason of property
   treated as transferred by such person under section 2519". Strict reading: only W's half is recoverable. Broad
   reading: N's half too. Run both ways. On the strict reading the split plan cannot be funded when the interest is
   worth $0 (tax $28M; W has $10M plus $14M recovery; N has nothing).
4. **Not recovering is not itself a gift.** The text says "entitled" and nothing about the effect of not recovering.
   W paying gift tax from her own $10M is what produces the $4M tax-exclusive gain.
5. W pays N's gift tax under §2513(d) joint liability without that being a gift. N's GST tax (never arises in a best
   plan) has no listed payer, so such plans are rejected.
6. Flat 40% above the exclusion instead of the §2001(c) brackets; one calendar year of gifts; GST on a bequest to G
   computed simply (never engaged).

## Silences

- No listed provision brings back into W's estate (a) gift tax paid shortly before death or (b) the part of the
  income interest she keeps after a partial disposition. §2044(b)(2) turns §2044 off after any §2519 disposition.
  Sections 2035 and 2036 were not in my list, so nothing was added. Every gain below depends on one or both.
- §2519 does not say the transfer is reduced by tax recovered under §2207A(b); not reduced.
- §2513 does not say whether a spouse acquired after H's death may split a transfer of H's QTIP property; no
  restriction added.
- §2010(c)(4): marrying N costs W nothing because H's unused exclusion is zero.
- GST exemption never binds: only W's own $10M can reach G, and the trust remainder is fixed on C.

## Search size

Six runs (income interest $0, $20M, $40M; strict and broad recovery): 15,604 + 12,782 + 12,000 + 16,324 + 13,204 +
12,242 = 82,156 distinct positions. Headline runs: 15,604 (strict) and 16,324 (broad).

## Results

Baseline: W does nothing and dies. Estate $110M, tax $38M, **$72,000,000** to C.

Income interest valued at $0:

| Plan | To C and G | Gain |
|---|---|---|
| Broad recovery (best): marry N, both consent, W gives any part of the income interest, pays $10M of the $28M gift tax herself, recovers $18M, dies | $82,000,000 | $10,000,000 |
| Same, with full recovery ($28M from the trust; W's $10M taxed at death) | $78,000,000 | $6,000,000 |
| Strict recovery (best): no splitting; W gives any part of the income interest, pays $10M of the $34M gift tax herself, recovers $24M | $76,000,000 | $4,000,000 |
| No disposition: marry N, both consent, give own $10M to C or G (half uses N's exclusion) | $74,000,000 | $2,000,000 |
| Own gifts alone, unmarried; or unmarried disposition with full recovery | $72,000,000 | 0 |

The $10M is $6M (N's $15M exclusion x 40%) plus $4M (W's $10M used to pay gift tax instead of being taxed at death).
The recipient of the income interest (C, G, trust for G) and the GST elections make no difference.

Income interest valued above $0 (give 1% of it, keep 99%, which no listed provision taxes):

| Value of interest | Strict | Broad |
|---|---|---|
| $20M | $83,920,000 (+$11,920,000), no marriage needed | $89,920,000 (+$17,920,000), married and split |
| $40M | $97,840,000 (+$25,840,000), married and split | $97,840,000 (+$25,840,000), married and split |
