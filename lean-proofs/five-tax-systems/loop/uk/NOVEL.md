# UK 2025-26: bounded search for new loopholes and traps

Model: the extended Lean model (`lean/`, see CATALOGUE.md). Burden = income tax (s. 23 liability incl. the s. 424
Gift Aid charge) less relief at source + CGT + employee NI − (child benefit − HICBC).

## Search A: marginal rates above 100 % and contributions that pay for themselves (`scan.py`)

100,000 random households (55 % couples, 75 % of them married; 0–4 children; 30 % Scottish taxpayers; incomes
biased to every threshold: £12,570, £17,570, £37,700, £43,663, £50,270, £60,000–£80,000, £100,000, £125,140 ...;
interest, dividends, gains, property with finance costs, RAS contributions, Gift Aid, VCT, EIS, benefits in kind,
blind allowance). For each person, every income +£1, +£100, +£1,000; every contribution +£1, +£100, +£1,000; and the
marriage toggled (~4 million model runs; ~10 min on 24 workers). Flagged: burden rises by more than the extra
income; a Gift Aid payment or RAS contribution cuts the burden by more than its gross amount (the payer ends with
more cash); VCT/EIS subscriptions or marriage raising the burden. Output `runs/scanA.jsonl` (924 events), summary
`runs/scanA.log`. Each event is tagged by the detail lines that moved.

| cause (tags, person index dropped) | events | worst | classification |
|---|---|---|---|
| HICBC £1 notches (one child £13 … four children £41 at a £200 boundary), on any income or as a £1 contribution | ~310 | +£41.47 for £1 | known: UK `hicbc_notches`, `hicbc_steps` |
| Personal savings allowance cliffs (£1,000 → £500 → nil), alone or with the taper, CGT rate switch, Class 4 | ~420 | +£268.53 for £100 | known: UK `psa_cliff`, `psa_cliff_additional`, `cgt_income_26` |
| Marriage allowance lost when the recipient reaches the higher rate (with PSA, Gift Aid charge, dividend nil rate, VCT) | 44 | +£300.74 for £100 | known: UK `ma_cliff` (F3) |
| FA 2004 s. 192(4) band-extension condition switching on (incl. through the PSA) | 5 + 10 | +£118.57 for £100 | known: UK F2(c), `f2b_condition_cliff` |
| **Allowance taper alone, all Scottish taxpayers with dividends** | **122** | **+£1,085 for £1,000 of wages; Gift Aid £1,000 cuts tax £1,006.25; RAS £1,000 gross cuts the burden £1,005** | **novel: N1 below** |
| Marriage raising the burden | 0 | — | consistent with individual taxation (no marriage penalty) |
| VCT / EIS subscription raising the burden | 0 | — | — |

### N1. Scottish taxpayers in the allowance taper with dividends or savings straddling the UK basic rate limit: 100.5–108.5 %

- **Example** (theorems `n1_scot_dividend_straddle`, `n1b_scot_free_relief` in `lean/UkTax/Loop/Theorems.lean`;
  PolicyEngine-UK 2.179.1 gives the same figures to the penny, `runs/n1_*.jsonl`): Scottish taxpayer, dividends
  £55,000, wages £46,000–£47,000 (adjusted net income £101,000–£102,000).
  - £1,000 more wages: income tax + Class 1 +£1,085 (**108.5 %**: net income falls £85). Rest of the UK: +£755 (75.5 %).
  - £1,000 of Gift Aid paid (£1,250 to the charity): income tax −£1,006.25. The donor is **£6.25 better off** and the
    charity £1,250 richer. Rest of the UK: −£537.50 to −£593.75.
  - £1,000 gross relief-at-source contribution (member pays £800): liability −£805 + £200 at source. The member is
    **£5 better off in cash** and has £1,000 more in the pension.
  - Same with interest instead of dividends: 101.6 % (1.5 × (42 % + 20 %) + 8 % NI).
- **Where** (`n1` grid, wages £30k–£70k × dividends £20k–£90k in £500/£1,000 steps): 253 of 5,751 cells above
  100 % for dividends (233 for interest), wages £32,500–£48,000, maximum 108.5 %; **none** for rest-of-UK taxpayers
  (maximum 75.5 % dividends, 82.6 % interest).
- **Cause.** A Scottish taxpayer's non-savings income is taxed at the Scottish rates by the Scottish limits (ITA 2007
  s. 6A, 11A), whose higher rate (42 %) starts at £31,092 of taxable income; savings and dividend income stay on the UK
  rates and the UK basic rate limit of £37,700 (s. 7-8, 10), counted as the top slice above non-savings income
  (s. 16). So between £31,092 and £37,700 of taxable non-savings income, wages bear 42 % while each extra pound pushes
  a pound of dividends from 8.75 % to 33.75 %. Inside the taper (s. 35(2): £1 of allowance lost per £2 above
  £100,000), every £1 of income adds £1.50 of taxable income: 1.5 × 42 % + 1.5 × 25 % = 100.5 % income tax, + 8 %
  Class 1. Conversely Gift Aid and RAS contributions reduce adjusted net income (s. 58), extend the Scottish limits
  above the starter band and the UK limits (s. 414(2)(b); FA 2004 s. 192(4), (4A)) and so recover 80.5 % of the gross
  gift / 100.5 % of the gross contribution.
- **Documented?** Not found in 2 searches: published commentary describes the Scottish taper at 67.5 % (69.5 %
  with NI; UK `scot_vs_ruk_marginal`) for earnings and says or assumes it does not reach dividends; nothing on the
  dividend/savings straddle above 100 % or on Gift Aid and pension contributions that pay for themselves.
  **Classification: novel** (an interaction of two well-known features, not a reading question; same result from
  the statute-faithful model and from PolicyEngine-UK).
- **Limits.** FA 2004 s. 192A (Scottish relief-at-source adjustment) is not modelled; it concerns the gap between the
  Scottish and UK basic rates, both 20 % in 2025-26, so it should not change the result. The pound-level figures
  (e.g. £1.42 for £1 of wages, £1.14 saved by £1 of Gift Aid) add the s. 35(3) rounding of the allowance to the
  pound (statutory rounding, artefact-sized); the £1,000 averages are the substantive figures.

## Search B: splitting a married couple's income and gains (`split_scan.py`)

1,500 random married couples (20 % Scottish; 0–3 children): every allocation of interest, dividends, gains and a
rental property (with finance costs) at 0/25/50/75/100 % to spouse 1, × which spouse makes the Gift Aid (1,250
allocations each, 1.9 million runs). Transfers are outright gifts (TCGA s. 58 no gain/no loss; ITTOIA s. 626).
Output `runs/splitB.json`, `runs/splitB.log`.

| comparison | median saving of the best allocation | p90 | max | share > £100 |
|---|---|---|---|---|
| vs equal split (the contract's default, ITA s. 836) | £600.80 | £4,188.51 | £11,381.73 | 69 % |
| vs everything held by the higher earner | £2,921.77 | £13,240.78 | £22,741.68 | 93 % |

- The best allocation is interior (some item split, not all to one spouse) in 76 % of couples: gains in 820, dividends
  531, interest 410, property 126. Usually the higher earner keeps just enough gains to use his own £3,000 exempt
  amount, and everything else goes to the spouse with spare allowance, starting rate, PSA, dividend allowance and
  basic band.
- Largest gain over the equal split: earner £99,221, spouse nil, £18,387 interest and £34,076 dividends: all to the
  spouse, £34,664.97 vs £46,046.70 (−£11,381.73: the equal split pushes the earner into the taper and wastes the
  spouse's bands).
- Crafted "every allowance at once" (earner £110,000, two children, spouse nil; £18,000 interest, £10,000
  dividends, £40,000 gains; 13-level grid): best = all interest and dividends and 90 % of the gains to the spouse:
  £45,247.17, vs equal split £52,500.75 (−£7,253.58) and all with the earner £60,631.25 (−£15,384.08).
- **Classification: known** (spouse transfers and bed-and-spouse are standard advice: CATALOGUE C12, C13, C34); the
  size of the gap left by an equal split is a quantification, not a new loophole.

## Other interactions checked

| | result | classification |
|---|---|---|
| Gift Aid or RAS keeps a recipient above £50,270 basic-rate, so the marriage allowance applies (CATALOGUE C40; theorem `giftaid_unlocks_ma`) | £252 | known: Tax Adviser magazine ("it is that extended basic rate band that is used"), RSM weekly tax brief |
| VCT/EIS relief that removes all the tax creates a Gift Aid charge (ITA s. 424-425: Step 6 reductions count) | £30,000 earner, VCT £20,000: relief capped at £3,486; adding £4,000 of Gift Aid brings a £1,000 charge | known statutory consequence (s. 425 lists the reductions to ignore and VCT/EIS are not among them) |
| RAS contribution and CGT for a basic-rate taxpayer (C05a) | no band extension, CGT unchanged; Gift Aid cuts CGT 6 % | known: UK F2(b) (reading question vs HMRC CG21204) |
| s. 25(2) allocation of allowances | — | known: UK F6 |

## Counts

Novel: 1 (N1, with its two contribution forms). Known: 8 cause groups above. Artefacts: pound-level rounding of
the allowance only (no model artefact found: every flagged group traces to a statutory rule; N1 confirmed by an
independent implementation).
