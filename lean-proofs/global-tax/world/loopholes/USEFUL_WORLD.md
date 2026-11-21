# Most useful loophole findings across the 159 world countries

As of 2026-11-21 00:10 UTC (rounds L1 and L1-S). Ranked by how much money and how many people they touch, how certain they are, and
whether someone can act on them. Each entry is a verified finding (status confirmed, model-proved or proved: the amount
reproduced on the current model by its exe and by Lean #guards, with the provision cited; details in the country's
FINDINGS.md 'Verification' section, `world/loopholes/REST.md`, `world/loopholes/AFRICA_MENA.md` and the merged table
`world/loopholes/strengthen/world_table.json`). Labels after each finding: status, then novelty: **new** = the effect
was not found described in the recorded search (Crossref, the IMF's DOI prefix, OpenAlex, EconBiz, PwC and, for most
listed here, a web search in the country's language); **new (weak)** = the bibliographic databases only; **known** cites
where it is described (in the finding's record); **known (pattern)** = an instance of a documented pattern; **unclear** =
a likely source exists or the record is thin. Amounts are a year unless stated; US$ at 2025 average rates, indicative.
Synthesis: `world/loopholes/CROSS_WORLD.md`; plain-language version: `world/loopholes/BLOG_LOOPHOLES.md`.

Corrections by L1-S that change this list: Thailand's minimum-tax notch (TH F1) is withdrawn (Royal Decree 480 exempts the
tax up to 5,000 baht); Algeria's rent notch (DZ F1) is 175,799 DA, not 310,799 (art. 85's 25 % abatement); the Marshall
Islands' allowance cliff (MH F2) is known (IMF, 2025).

1. **Colombia: the pension solidarity contribution is 1 % of the whole base from 4 minimum wages (CO L1, confirmed, new).**
   One peso of monthly pay above 5,694,000 costs 683,280 COP a year (about US$167); each step from 16 to 20 minimum wages
   adds 0.2 % of the whole base (366,238 at 16). Found blind by the re-scan; Ley 100 art. 27 as amended by Ley 797 art. 8
   re-read. The 1 % is widely published; the fall in net pay at the line was not found described.
   *Useful to:* employees and independent workers near 4 SMMLV (set the monthly base just under the line), employers
   (pay design), the ministry (charge the 1 % on the excess: the pension reform suspended to 2027 keeps the step).
2. **Paraguay: the IRP is due on the whole net income once gross income passes 80 M guaraníes (PY-F1, confirmed, new).**
   6,052,000 PYG for one guaraní (about US$770); Ley 6380 arts. 62 and 69 re-read by L1-S ('no superen G. 80.000.000 ... no
   estará obligado al pago del impuesto'). The uncapped deduction of documented personal spending (PY-F2, confirmed, new (no press search)) then
   lets a worker with matching receipts pay nothing. *Useful to:* service providers near 80 M (keep gross under the line
   or document expenses), the DNIT.
3. **Algeria: one dinar of rent above 1.8 M DA moves the whole rent from 7 % final to the barème (DZ F1, confirmed, new).**
   175,799 DA for one dinar (about US$1,320), after L1-S applied the 25 % abatement of CIDTA art. 85 that the model had
   missed (round L1 said 310,799). Spouses each have the threshold. *Useful to:* landlords near 1.8 M (split leases between
   spouses, cap rents), the DGI (a 7 % slice above the line instead of a switch).
4. **Egypt: the column tariff withdraws the lower bands at each column limit (EG F1, confirmed, known).**
   Crossing 600,000 / 700,000 / 800,000 / 900,000 / 1.2 M EGP of net income costs 2,752-10,002 EGP for one pound (about
   US$55-200); every employee at a column edge. Described by PaySpace, Standard Bank's market guide and Deloitte Middle
   East. *Useful to:* employees near the limits (time pay), the Ministry of Finance (a band tariff has no jump).
5. **Algeria: the 30,000-35,000 DA smoothing formula taxes the first slice at 58.7 % (DZ F2, confirmed, new).**
   67.7 % with CNAS against a 35 % top rate, for every worker paid 30,000-31,667 DA a month, just above the exempt wage
   (7,044 DA a year, about US$53). The formula is printed by the DGI and the press; its slice rate is not. *Useful to:*
   the low-paid (whose raises are taxed most), the legislator.
6. **Morocco: professional expenses fall from 35 % to 25 % of pay at 78,000 MAD (MA F1, confirmed, new).**
   779 MAD for one dirham (about US$83) and a dead zone to about 78,880; employees around 6,500 MAD a month, about twice the
   SMIG. The rule is in PwC, Upsilon and ClicPaie (read: 'le seuil ... limite mécaniquement l'abattement à 27 300 DH'); the
   notch is not.
7. **Uruguay: the deduction credit falls from 14 % to 8 % of all deductions one peso above 180 BPC (UY-F1, confirmed, new).**
   13,850 UYU for one peso (single), 30,697 with two children (about US$340-750). Rule published by DGI; the jump not found
   described. FONASA does the same at 2.5 BPC a month (UY-F2, confirmed, new (no press search); Ley 18.211 art. 61 read on IMPO by L1-S).
   *Useful to:* employees at about 98,640 pesos a month of nominal income, DGI and BPS (tapers).
8. **Argentina: the spouse deduction is lost in full at the spouse's first peso above the exempt amount (AR L1, confirmed, new).**
   406,707 ARS for one peso with the main earner at 40 M; 1,609,626 at 100 M (about US$370-1,460). Found blind by the
   re-scan; LIG art. 30 b) re-read. *Useful to:* one-earner couples whose second spouse earns about 4.5 M a year, ARCA.
9. **A spouse is a dependant only with no income: the relief ends at the spouse's first unit (SN F2 confirmed, new; LB F1
   confirmed, new; KH F1 confirmed, new; BF F2 confirmed, new (no press search); MU F2 confirmed, new (no press search); SG F1 confirmed, new; BA F1 confirmed, new (no press search); TG F1 confirmed, new (no press search); NE F4 confirmed, new (no press search);
   GH F2 confirmed, new (no press search)).** Senegal up to 185,549 F a year; Lebanon 15.75-18.9 M LBP; Mauritius 21,999 MUR; Cambodia
   180,000-360,000 riel; Bosnia's Federation 180 KM; Singapore 196 SGD. Each re-searched in its own language. *Useful to:*
   couples where one spouse starts to earn, ministries (taper the relief).
10. **Pakistan: whole-income tests at 10 M, 5 M of bank profit and 75 % salary (PK F1 confirmed, new; PK F2 confirmed, known; PK F3
   confirmed, known).** One rupee costs 241,290 PKR of surcharge at 10 M (about US$860; abolished for salaried individuals in the
   2026-27 budget); one rupee of bank profit above 5 M costs 1,258,000 (about US$4,480; s. 7B (3) (b) re-read; deposits
   can be split between spouses); one rupee of side income that drops salary below 75 % of income costs 384,000. With PK
   F4 and PK F5 (a former employer's pension at 0 % to 10 M). Kleven and Waseem's notches, still there. *Useful to:*
   taxpayers near each line, the FBR (glide zones).
11. **DR Congo: a 40 % band sits under a 30 % cap on the whole tax (CD F1, confirmed, new).** The marginal rate is 40 %
   between 43.2 M and 77.9 M FC of taxable pay and 30 % above: up to about 3.5 M FC a year (about US$1,220) for the top
   decile but not the very top. Scale and cap are published (PwC, the DGI); the hidden band is not. *Useful to:* the
   legislator (the IPR is to become an IRPP under Law 23/053).
12. **Final monthly or per-period taxes make bonuses expensive (DJ F1, MR F2, RW F1, ET F3, GN F1, SC F1, NR F1, ME F3,
   RS F1, AF F2).** Djibouti: 2.4 M FD in one month pays 776,000 against 348,000 spread (about US$2,400); Nauru: A$120,000
   in one month pays 22,152 against 1,824; Afghanistan: 1.2 M AFN in one month 228,900 against 106,800 (art. 63 (1): no
   return for single-employer employees, read by L1-S). Novelty: RS F1 confirmed, new (no press search); DJ F1 confirmed, new (no press search); NR F1 confirmed, new (no press search).
   *Useful to:* employers and employees (spread bonuses), administrations (an annual true-up).
13. **Guinea-Bissau's printed table subtracts 16,020 F a month too much in its 14 % row (GW F1, confirmed, new).**
   Everyone above 400,500 F a month pays 192,240 F a year less than the code's own rates (about US$330). *Useful to:* the tax
   administration (fix the table), taxpayers (who benefit until then).
14. **Congo and Gabon: the same French quotient gives a marriage bonus in one and a penalty in the other (CG F1 confirmed, new;
   GA F1 confirmed, new (no press search)).** In Congo a wage-earning wife is assessed alone with 2 parts while the husband keeps his: 591,800 F
   a year (about US$1,020) for marrying; in Gabon an unmarried parent's first child gives 2 parts, so marriage costs a
   two-earner family 243,198 F. (Congo replaces the IRPP from 2026.)
15. **Post-Soviet deductions limited by income (MD F1 confirmed, known; UA F1 confirmed, new; BY F1 confirmed, new (no press search)).** Moldova 3,565 lei
   at 360,000; Ukraine's tax social benefit 3,273 UAH a year at 4,240 a month (6,543 for parents of two); Belarus 301 BYN at
   1,164 a month. Low-paid workers in large labour markets. *Useful to:* employees at the limits, the ministries.
16. **Mauritius and Kenya: contributions that jump on the whole wage or start from the first unit (MU F1 confirmed, new; KE F1
   confirmed, new).** Mauritius: CSG 3 % of the whole wage above Rs 50,000 a month instead of 1.5 % (8,989 MUR a year for 12);
   Kenya: SHIF at least KES 300 a month, 6 % of pay at KES 5,000. *Useful to:* the lowest-paid and part-time workers, social
   security boards (charge the excess). With TT F2, KN F1, VU F1, UY-F2, CI F2, TD F3, MG F1.
17. **Timor-Leste: one zero band for wages and another for other income (TL F1, confirmed, new).** US$12,000 split into 6,000 of
   wages and a 6,000 fee pays no income tax against US$600 as wages (round 2's mix scanner re-found it). *Useful to:*
   residents who can be paid partly as contractors; the legislator (one allowance per person).
18. **Drafting holes in small states (BZ F1 confirmed, new; TT F1 confirmed, new; PW F1 confirmed, new (no press search); MH F2 confirmed, known; FM F1 confirmed, new (no press search);
   AM F1 confirmed, new (no press search)).** Belize taxes exactly BZ$29,000 at 25 % with no deduction (7,250 dollars); Trinidad's low-income
   relief jumps up to 1,090 TTD for one dollar; Palau's citizen refund ends at $15,000 ($1,180); the Marshall Islands'
   allowance ends at one cent ($665; the IMF described it in January 2025 and proposed the fix); Armenia's stamp duty 78,000
   dram a year at 1 M a month. *Useful to:* drafters (each has a one-word or one-row fix), payroll software.
19. **Owner-managers pay least through dividends wherever the dividend rate is below the wage scale (known pattern; LK F1,
   FJ F3, MV F1, TO F3, KZ F2, KG F2, BW F2, NA F1, SZ F4, CM F4, CF F3; Chad reversed, TD F1).** Sri Lanka: 1.9 M LKR less on
   10 M (about US$6,300); Fiji: 63,601 FJD less on 250,000 (company tax not modelled; round 2 adds it). *Useful to:*
   owner-managers and advisers; ministries comparing the dividend rate with the top wage rate.
20. **Known reliefs that behave like loopholes: India's s. 87A plus cess (IN F2, confirmed, known: a 104 % band from 12.75 to about
   13.46 lakh), Brazil's simplified discount (BR F2, confirmed, known: the first two children worth nothing), Costa Rica's salaried
   and self-employed exempt amounts (CR F2, confirmed, known), Colombia's double dependant relief for employees (CO F3, confirmed, known).**
   Large populations, documented by the press, the authorities' own doctrine or practitioners.
