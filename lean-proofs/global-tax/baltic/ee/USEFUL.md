# Estonia 2025: what this work is useful for

Evidence: FINDINGS.md (F-numbers), CATALOGUE.md (L-numbers), Lean theorems in `lean/EeTax/` (names in backticks).
Amounts are euro for 2025 and the stated household; "burden" = income tax + unemployment insurance + II pillar
(+ an FIE's social tax) − family benefits.

## For a taxpayer
1. **Between 14,400 and 25,200 euro a year each extra 100 euro of pay kept only 59.20** (37.20 income tax, 3.60
   contributions): the basic exemption is withdrawn at 109/150 (F3, `hump_marginal`, `hump_wages_100`). From 2026 the
   exemption is a flat 8,400 and the band is gone.
2. **Estonian dividends are tax-free for you but still count as income for the exemption.** 10,800 of dividends on top
   of 14,400 of wages cost 1,726.56 of extra income tax (F4, `dividend_hump`). A dividend received by a family member
   without other income, or in a year when your income is already above 25,200, costs nothing.
3. **Uneven pay means a settlement on the return:** a December bonus can leave a bill of up to 1,582.68; leaving or
   starting work mid-year can give a refund of up to 1,726.57; claiming the exemption at two employers gives a bill of
   about 3,262 (F9, `bonus_bill`, `halfyear_refund`). Apply for the exemption at one payer only (§ 42(2)).
4. **II- and III-pillar payments save only 22 % in the band**, not the 38 % marginal rate: they do not reduce the income
   that withdraws the exemption (F19; a 1,000 III-pillar payment at 20,000 of wages saved 220.00).
5. **Reaching pension age is worth up to 2,756 a year at 25,200 of wages** (9,312 exemption never withdrawn, no
   unemployment insurance; F10, `pension_age_switch`).

## For an adviser
1. **Owner-managers: dividends tax 22 % of profit at every level, salary 30-44 %** (F6; owner scan: 4,613 at 1 AW, 55,822
   at 10 AW). The reclassification risk (pay for work) is the constraint, not the statute (no rule found).
2. **Retention is the Estonian advantage:** profit kept in the OÜ earns its return untaxed until paid out — 2.07 per
   euro after 20 years at 5 % vs 1.79 via an investment account and 1.68 via an ordinary account (F7, `runs/retention.md`).
3. **Time distributions and bonuses around the hump** (F5: 1,726.57 per pair of years, `bunching_gain`; F12: up to 1,727
   by paying in January 2026 rather than December 2025). Dividends count in the year paid (§ 23(3), § 36(1)).
4. **FIE vs OÜ:** an FIE pays 3,247.20 of social tax from the first euro of profit (F11, `fie_entry`) and 33 % on profit/1.33
   above it; an OÜ paying dividends saves 1,352 at 15,000 of profit and 12,315 at 60,000 (F8).
5. **Birth benefit from the employer:** EMTA allows 3,270 tax-free for everyone, which is more than § 13(3) p7 literally
   gives a parent above the hump (F13); rely on EMTA's published reading.

## For the government (Riigikogu, Rahandusministeerium, EMTA)
1. **§ 13(3) p7 ties a tax-free cap to the person's own § 23 exemption,** which since 2018 depended on income: 0 for a
   parent above 25,200, unknowable at payment, undefined at pension age; EMTA applies 3,270 regardless (F13). Name a
   fixed amount (the 2026 flat exemption makes the fix simple and still worthwhile for the record).
2. **Clean the dead references left by the 2025 reform:** § 4(1^1) excepts "lõikes 5", which since 1.1.2025 covers only
   credit institutions' 18 % advance payments, never a distribution (F14); § 57^1(6) "Lõigetes 1–5^3" includes repealed
   § 57^1(1); § 61(24), (37) name repealed provisions (F15). Fix the title quoted in RT I 24.09.2024, 4 § 2(1) (F16) and
   the 20 % / 7 % rates on EMTA's 2025 exemption page (F17).
3. **For the 2028 review ordered by § 61(71):** the hump's 37.99 % income-tax band (40.8 % with contributions, 55.7 % of
   labour cost) applied to 0.56-0.98 AW, and its interaction with untaxed dividends (34.47 % on profit) and with uneven
   monthly pay (two thirds of uneven patterns end in a refund or bill of up to 1,727) are now gone; the remaining
   arbitrage is labour vs dividends (33 % social tax vs none, F6) and the untaxed return on retained profit (F7).
4. **The OECD's Estonian worker pays no II-pillar contribution and every single parent gets the single-parent
   allowance** (F1, F2): both are conventions; with them the model reproduces all 48 compared OECD lines exactly, without
   them take-home pay is 1.6 % lower.
