# Finland 2025: what is most useful to know (with the evidence)

Everything below is computed by the Lean model of the 2025 statute (`lean/FiTax`), which reproduces the OECD's
Finnish figures (48 of 48 lines, 8 of 8 take-home pays at the OECD's 7,54 % municipal rate), all 287 rows of
Veronmaksajat's 2025 wage-earner table and all 32 rows of Kela's 2025 pension tax table. Amounts for a Helsinki
resident (5,30 %) outside the church unless stated; findings in `FINDINGS.md`, theorems in `FiTax/Loopholes.lean`.

## For a taxpayer
1. **A small job: 16 861 € a year is better than 16 862-17 021 €.** At 16 862 € of pay the päivärahamaksu (0,84 %)
   falls on the whole pay at once: 141,64 € for one more cent, and you are worse off until 17 022 € (F1,
   `f1_daily_notch`). Second earners and students with summer jobs are the ones near this line.
2. **Low pay is nearly free of income tax, not of contributions or the YLE tax.** Up to about 21 000 € of pay the
   work credit (18 % of pay, at most 3 225 €) wipes out state, municipal and health-care tax; you still pay 7,74 %
   pension and unemployment contributions and, above 15 150 € of net income, 2,5 % YLE tax up to 160 €
   (`runs/fi_scan.json` S6). Any unused work credit is lost: it is not paid out.
3. **Capital gains: keep each year's capital income under 30 000 €.** Above it the rate is 34 % instead of 30 %:
   60 000 € of gains in one year cost 1 040 € more than 30 000 € in each of two years (F5, `f5_capital_timing`).
4. **Pensioners pay more than workers on the same income from about 17 000 to 80 000 €** (750 € more at 25 000 €;
   F6), because the pension gets no work credit and the pension deduction is withdrawn at 51 %: a pensioner's
   marginal rate is 37 % at 16 000-20 000 € and lower (27 %) at 24 000 €.
5. **A single parent who marries loses about 930 € a year per child** (child-benefit supplement 879,60 € and half
   of the doubled work-credit increase; F7). Moving in with a partner without marrying loses the supplement too.

## For an adviser
1. **Owner-managers: the 8 % net-asset rule is not always a privilege.** Dividends above 8 % of the shares' net
   asset value are 75 % earned income, which gets the basic deduction and the work credit and carries no TyEL,
   unemployment or daily-allowance contribution: with no net assets a 20 000 € dividend is personally tax-free,
   with 250 000 € of net assets it costs 1 500 € (F4, `f4_owner_zero_assets`). At up to about 1 AW of profit a low
   net asset value can be cheaper; above about 2 AW more net assets always help (10 AW: 47,5 % vs 39,1 % at 2 MEUR).
   Best split at 1 AW with 500 000 € of net assets: 16 861 € salary (just under the F1 floor) + dividends, 25,1 %
   of profit vs 37,6 % all salary (`runs/owner/owner.md`) — before valuing pension and sickness cover.
2. **2025 pay around 100 000-125 000 €: time bonuses.** The 2025 work credit is still withdrawn (3,44 %) up to
   125 240 € of pay, so the marginal rate there (56,0 %) is above the top rate (54,85 %). Bunching income (155 000 +
   97 000 € instead of 126 000 € twice) saved 950 € under 2025 rules (F3); from 2026 the withdrawal stops at
   50 550 € of net income, so deferring such pay into 2026 helps more.
3. **Use the spouse's taxes for a capital-deficit credit.** A low earner's 30 % deficit credit is often absorbed by
   nothing because the work credit comes first; ask for the transfer (TVL 134 §): 600 € per 2 000 € of deficit (F8).
4. **Read Vero's summary of the work-credit withdrawal as "instead of", not "plus"** (R1): above 42 550 € the rate
   is 3,44 % instead of 2,22 %, as the statute and the OECD figures show.

## For the government
1. **The 2025 work credit created a band of marginal rates above the top rate (97 300-125 240 € of pay) and made
   bunching pay** (F2, F3). HE 98/2025 removed the second withdrawal for 2026; the bunching effect is an argument
   to keep future credit withdrawals from ending inside the higher brackets.
2. **Two government proposals state pay thresholds as net-income thresholds** (G1: HE 98/2025 "noin 125 300 euroa"
   of puhdas ansiotulo, really 124 490 €; G2: HE 108/2024 "noin 94 084 euroa", really 93 333 €): both are the pay at
   which the deduction ends, 750 € (the tulonhankkimisvähennys) higher. Proved in `g1_he98_threshold`,
   `g2_he108_threshold`; harmless for assessments but misleading in the documents that explain the law.
3. **The päivärahamaksu floor is an all-or-nothing notch** (F1): a sliding entry (like the YLE tax's 2,5 % above a
   threshold) would remove a 141,64 € jump and a 160 € dead zone that fall on part-time and second earners.
4. **Two definitions of a single parent** (R2): TVL 125 § 4 mom (no spouse in the TVL sense and sole guardian) and
   lapsilisälaki 7 § 3 mom (not married, not cohabiting). A cohabiting single parent keeps one and loses the other;
   a jointly-custodial parent gets neither doubling although Vero's guidance says "yksinhuoltajalle".
