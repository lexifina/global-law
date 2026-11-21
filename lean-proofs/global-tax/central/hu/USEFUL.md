# Hungary 2025: what this work is most useful for

## A taxpayer
1. **The family allowance is a credit of 15 % of the year's frame against tax and TB together**, so nothing is lost
   while your wage is above 45 % of the frame: tax + TB − contribution allowance = max(0, 33.5 % × wage − 15 % ×
   frame) (proved: `Theorems.famBurden_closed_form`). For three children the 2025 frame is 9 900 000; below
   4 432 836 a year an employee pays neither Szja nor TB. Make sure the contribution allowance is claimed (in the
   return if the employer did not).
2. **Turning 25 this year?** Pay accounted to months up to your birthday month is exempt up to months × 656 785;
   ask for a bonus, overtime or back pay to be accounted before the birthday month ends (F5: 300 000 HUF saved on a
   2 000 000 bonus at 300 000 a month).
3. **Mother of three in 2025** (2025. évi XV. tv.): only income received or accounted after 30 September is exempt;
   a sole trader who invoiced Q4 work in October-December rather than September kept 15 % of it (F4: 478 710 HUF on
   6 M).
4. **Young parents**: under 25 your own exemption already wipes out your tax, so let the older partner claim the
   family allowance (közös igénybevétel); a lone parent under 25 with three children on half the average wage gets
   nothing from the under-25 exemption (F8).
5. **Savers with a salary above 6 979 200**: bank interest costs 28 % (15 % + 13 % szocho), fund gains and
   dividends 15 % (F9).

## An adviser
1. Owner-managers (1 AW of profit): flat-rate sole trader 6 800 283 net, KIVA with minimum wage + dividends
   5 434 561, Kft with the active member's minimum bases + dividends 4 782 669, all salary 4 976 017; KATA (B2C only)
   7 855 487 (`results/own/owner.json`; personal side proved by `decide`, company side cited).
2. The szocho ceiling is annual: dividends every second year save up to 907 296 HUF per two years (F7).
3. Deferring pay from December 2025 to January 2026 helps families whose 2026 frame (+33 %) will not be used
   (F6: 214 553 HUF on 1 000 000 for a lone parent of three on 0.6 AW).
4. When splitting the family allowance between spouses, check each spouse's base after the earlier allowances
   (§ 29/H): NAV's own example gets this wrong (F3).
5. Every number here comes from one model validated 56/56 against the OECD and on 45 NAV worked figures; `hutax`
   reads a household as JSON and prints the lines.

## The government
1. **Fix § 29/B (6)**: "elosztott része (667 százaléka)" — 1/15 % is 666.67 %; the parenthesis overcharges each
   forint of in-year contribution allowance by 0.05 % and NAV's calculator uses both conventions (F2, F12).
2. **Correct NAV booklet 73 § 13**: Orsi can use at most 1 800 000 of the family allowance, not 2 000 000 (F3).
3. **Dated starts invite timing**: the three-children mothers' exemption (from 2025-10-01), the under-25 exemption's
   last month and the 2026 family-allowance rise each reward moving pay across a date (F4-F6); a pro-rata rule for
   bonuses (as § 1 (6) already does for undeterminable self-employed income) would close them.
4. **The szocho ceiling treats interest and dividends differently** (F9) and is annual (F7); counting all capital
   income, or a multi-year ceiling, would remove both.
5. **Családi pótlék has not changed since at least 2009** (12 200 HUF for one child = 4.2 % of the 2025 minimum
   wage) while the tax allowance rose by half in 2025 and again in 2026 (F11): families without insured income get
   none of the increase.
