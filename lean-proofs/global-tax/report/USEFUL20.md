# Most useful findings across the 20 countries

Ranked by how much money or how many people they touch, how certain they are, and whether someone can act on them.
Each entry: what, where it is proved, and who it is useful to. Every amount is a verified country finding (status
confirmed, certain or proved, with the statute cited in the country's FINDINGS.md); where only the novelty or a
reading is unconfirmed the entry says so, and the full list is in CROSS.md, "Needs checking".

1. **Mexico: the employment subsidy stops dead at 10,171 pesos a month.** One centavo more monthly income costs
   474.65 pesos; over a year ten pesos more pay can cost 5,213, with a dead zone of about 5 % of pay above the
   cut-off; about 6.1 million workers receive the subsidy. Evidence: MX F6, F7 (decree of 31-12-2024 art. Segundo,
   proved in Lean); the aguinaldo variant MX F8. *Useful to:* SHCP (taper it), employers and workers near 1.2 minimum
   wages (timing of pay rises and bonuses).
2. **Withholding that departs from the statute, in ten countries.** Korea's monthly table is computed with the 2014
   earned-income credit and the 2017 pension ceiling (7,098 of its 7,106 cells reproduced from that rule;
   over-withholding up to 28,040 won a month, KR F8) and still applies the 2024 child credit (200,040 won a year for
   two children, KR F5); Australia's Schedule 1 uses the 2023-24
   Medicare levy parameters (AU F8) and leaves the low income offset to the return (up to $765, AU F9); Norway's tables
   over-withhold about 2,430 NOK from every employee above 200,000 (NO F1); Portugal's August-September 2025 cut
   returned about 13 times the January-July excess (PT F7); Spain withholds 300 € from a minimum-wage earner who owes
   nothing (ES F2); also SE F5, PL F8, CZ F10, NL F13. *Useful to:* tax administrations (update the tables with the
   law), employees (refunds only at the year end).
3. **Czechia's child allowance cliff, and the way round it.** 35,280-51,238 Kč lost for one crown of income (CZ F7);
   because the test counts income after tax, a one-earner family can gain 20,076 Kč a year by not claiming a child
   credit (CZ F5, a reading of ZSSP § 5 to confirm with the Úřad práce). *Useful to:* families near the limit, MPSV
   (the 2025-10 reform replaces the cliff with a withdrawal).
4. **Thresholds frozen while the amounts around them are indexed.** Ireland's €12 PRSI credit, unchanged since 2016
   through five rate rises: the €352 notch grows from €2.08 to €4.54 a week under enacted law (IE F9); Australia's FTB A
   supplement limit of $80,000, never indexed, now a $1,833 notch inside the family taper (AU F4); Poland's one-child
   relief limit, unchanged since 2013, with a 1,632 zł band where more pay means less income (PL F3, F12); Czechia's
   spouse-credit limit since 2008 (CZ F11); Italy's dependants' limit since 1995 (IT F9); Spain's 6,500 € other-income
   test, where one cent of interest costs a 14,000 € worker more than 1,650 € (ES F4, F5). *Useful to:* finance
   ministries (index together or write one amount in terms of the other: IE F9's fix is "rate × €352").
5. **Benefit cliffs that cost more than a month's pay.** Australia's FTB B primary-earner limit, $3,883.60 for one
   dollar (AU F5); Ireland's working family payment, €1,035 at its €20 minimum (IE F17); Portugal's abono de família
   and the joint mínimo de existência, 250-1,914 € (PT F10, F11; novelty not searched); Italy's stacked cliff at
   8,500 €, where one euro of pay costs 300 € (IT F4); Korea's child incentive, whose eligibility counts dividends
   while its amount does not, so one won more of wages costs 1,750,000 won (KR F9); Danish parents above 997,878 kr.
   of pay at 56.3 %, over the 52.07 % tax ceiling, because the child benefit taper is not a tax rate (DK F13). *Useful to:* families and advisers (watch the limit; time the
   income), governments (tapers instead of limits).
6. **Official tables and formulas that disagree with the statute.** Korea's earned-income incentive table pays
   one-earner families more than the statute's formula in 40 of 447 rows, and the table governs (KR F3); the
   Netherlands' statutory tariff falls by cents at €38,441 and the arbeidskorting never reaches its stated maximum
   (NL F6, F7); Portugal's rounded average rates make the tax fall when income rises (PT F3); Mexico's tarifas are not
   monotone at 6 row edges (MX F4). *Useful to:* drafters (derive the table from the formula, then check it: the
   kernel's `Table.agreesWith` does it by `decide`).
7. **Bunching income into one year beats spreading it, where a benefit or ceiling is non-convex.** Poland, up to
   7,020 zł across the contribution ceiling (PL F16); the Netherlands, up to €8,234 for a single parent across the end
   of the arbeidskorting taper (NL F17); Mexico 7,112 pesos across the subsidy cliff (MX F16); Australian families up
   to 12 % of AW (AU F14, a lead); Canada (CA F6). Several were found blind by the kernel's timing scanner. *Useful to:*
   the self-employed, people with bonuses or a one-off gain, and advisers.
8. **Couples: who holds what.** Individual taxation pays for moving income to the lower earner (Sweden up to
   178,832 kr, SE F10; Canada's capital ownership up to $13,008 a year, CA F3; pension splitting up to $19,136, CA F2);
   joint means-tests penalise couples, married or not (Canada up to $16,652 in benefits, CA F4; Norway's single-parent
   child benefit, NO F16); in Denmark marriage moves a spouse's interest income into the higher earner's topskat (up
   to 24,362 kr., DK F9). *Useful to:* couples and advisers.
9. **Traps for the self-employed and pensioners.** A Norwegian sole trader on 108,550-176,684 NOK pays 47 % on each
   extra krone, more than in the third state bracket (NO F10); Swedish working pensioners up to 213,000 kr pay the 7 %
   pension fee in full because its credit only displaces the earned-income credit (SE F2). *Useful to:* those
   taxpayers, and to the ministries that designed the credits.
10. **What Taxing Wages counts.** The OECD leaves some compulsory levies out of employee contributions (NZ's ACC
    levy, NZ F1; Mexico's cesantía y vejez, MX F1; Poland's subkonto share, PL F1), uses a regional tax that is not the
    named region's (ES F1) or leaves out its reliefs (IT F1), missed Ireland's PRSI rise of 1 October 2025 (IE F2), and builds Denmark's worker on an unstated 15 %
    occupational pension (DK F3).
    *Useful to:* researchers and journalists comparing take-home pay across countries; the OECD's Taxing Wages team.
11. **Owner-managers: the company route pays most where dividends are taxed lightly and separately.** With the
    company side cited per country, a one-person company paying dividends instead of salary cuts the total tax on
    3 AW of profit by about 22 points in Poland (26.3 % flat; the 9 % CIT rate and the owner's ZUS regime still need
    the statute), 10 in Czechia, 8 in Spain (if the owner is a Régimen General employee) and 6 in Germany (a lower
    bound), while in Ireland salary is always best and in Australia the split does not matter (refundable franking).
    The scan reproduces the UK, Swedish, Norwegian and Korean agents' own results to within a few units.
    *Useful to:* owner-managers and advisers (the best split is a statutory threshold in SE, NO, KR, UK), and ministries
    (the gap is a choice of dividend rate, not a loophole). Evidence: `harness/search/owner.py`, `company.json`,
    CROSS.md section 3b.
