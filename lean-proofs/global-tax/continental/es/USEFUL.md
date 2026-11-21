# Spain (Madrid), IRPF 2025: what this work is useful for

## For a taxpayer
1. **If you earned roughly the minimum wage in 2025 (about 15.900-16.650 EUR from one employer), file a return even
   though you are not obliged to.** Your employer withheld up to 331 EUR (300,03 at 16.576) that you do not owe: the
   new 340 EUR deduction (LIRPF DA 61.ª) wipes out your tax, but the withholding rules were not updated (F2, theorems
   `smi_owes_nothing`, `smi_withheld`).
2. **Watch the 6.500 EUR limit on income other than wages** (interest, dividends, gains, rent) if your net wages are
   below about 19.750 EUR: one euro over can cost 1.650 EUR (F4, `cliff_6500`).
3. **Married with one income? File jointly** (Renta Web shows both): 945-1.420 EUR saved at the average wage; not
   worth it once the second income passes about 6-8.000 EUR (F8).
4. **Madrid families: the regional family deductions stop dead at fixed bases** (24.744 EUR family base for the 10 %
   deduction with two children; 30.930 individual / 37.322,20 joint / 61.860 family for the 721,70 EUR birth
   deduction). The limits are on the base imponible, before pension-plan reductions, so only less income (or income moved
   to another year) brings a family back under them (F6, F7).
5. **Donating up to 250 EUR costs you 50 EUR** (80 % credit, Ley 49/2002 art. 19), K7.

## For an adviser
1. Map clients against the notches in `NOVEL.md`: 6.500 EUR of other income (state), 24.744 / 30.930 / 37.322,20 /
   61.860 EUR of base (Madrid). They are all-or-nothing and measured before pension-plan reductions (base imponible, or
   other income), so the levers are timing (deferring a gain or a bonus) and who holds the savings, not a pension plan.
2. One-payer workers on 18.100-21.740 EUR are under-withheld by up to 138 EUR and need not file (F3): if they file
   (for example to claim a deduction) they will owe; weigh that before advising them to file.
3. Owner-managers: at 100.000 EUR of profit a micro company with a salary/dividend mix saves about 2.300 EUR a year
   against self-employment, and retained profits bear only 21-22 % in 2025 (F13; RETA and anti-abuse rules aside).
4. The mínimo personal y familiar is a credit worth 9,5 % + 8,5 % (Madrid) of it to everyone, not a deduction at the
   marginal rate (F9): it does not grow with income, unlike a pension contribution.

## For the Spanish government
1. **Update RIRPF art. 81.1 (and the art. 85.3 limit) to the 2025 and 2026 SMI, and build the DA 61.ª deduction into
   withholding.** Evidence: F2; the AEAT's own algorithm document still claims SMI earners are not withheld. Draft
   issue text in FINDINGS F2.
2. **Index or taper the 6.500 EUR "other income" condition** of art. 20 and DA 61.ª: unchanged since 2015 while the
   reducción it removes went from 3.700 to 7.302 EUR (F4, F5).
3. **Madrid: replace the base limits of DLeg 1/2010 arts. 4, 14 and 18.1 by a glide** (as art. 20 tapers): today 10 EUR
   more wages can cost 725 EUR (F6, F7).
4. **Publish the regional weights used for Spain in Taxing Wages** (or ask the OECD to): the OECD's "weighted
   combination" regional schedule differs from every real region, so the published Spanish tax wedge matches no
   actual taxpayer (F1); for Madrid the regional tax is 155-586 EUR lower than the OECD's on its eight households.
5. **Revisit the 43 % withholding cap (RIRPF art. 85.3) together with the 22.000 EUR filing threshold**: together they
   leave up to 138 EUR per worker uncollected on 18.100-21.740 EUR (F3).
