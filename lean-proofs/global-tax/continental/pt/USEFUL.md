# PT (IRS 2025): what this work is useful for

Evidence: FINDINGS (F-numbers), NOVEL (N-numbers), CATALOGUE (K-numbers), Lean theorem names in `lean/PTTax/`.

## For a taxpayer
1. **Expect a smaller refund (or a bill) for 2025.** The August-September 2025 withholding tables cut tax by
   about 13 times what January-July had over-withheld; a single employee with steady pay is under-withheld for
   2025 at almost every pay level (e.g. about 205 € at 2 000 €/month). F7, `compensation_2000`.
2. **Married? Compare joint and separate every year.** Joint taxation can save up to a third of an average wage
   for one-earner couples (K1), but a joint return loses every mínimo de existência abatimento once the couple's
   gross passes 32 186 €; there separate returns are cheaper (F11, `me_joint_notch`).
3. **Families near 37 306 € of income with two children over six:** one more euro of household income ends the
   abono de família (−1 276 € a year for a couple, −1 914 € for a single parent). F10, `abono_cliff_*`.
4. **Low pay is taxed at the top marginal rate.** Between 12 180 € and 13 863 € a year each extra euro costs 56 %
   (45 % IRS from the mínimo de existência phase-in + 11 % contributions). F12, `me_segment_b_step`.
5. **Ask for invoices with your NIF.** The mínimo de existência and the withholding tables both assume the 250 €
   general-expenses deduction (35 % of 714 € of invoices); without them a minimum-wage earner owes 250 €.
   CIRS arts 70 n.º 2 a), 78-B; F7.

## For an adviser
1. The 2025 rates are Lei 55-A/2025's for the whole year (the AT and the OECD apply them so), although the law
   has no clause saying so (F1); the OE 2025 rates matter only for January-July withholding.
2. Under-35s: IRS Jovem exempts up to 28 737,50 € but the exempt income still sets the rate, and the exemption
   ends at once at 36 or after the 10th year (K6, `jovem_age_cliff`, `jovem_cap`).
3. Englobamento of interest, dividends (50 %) or rent pays below a 28 % / 25 % marginal rate and is all-or-
   nothing per category (K3); the model chooses it automatically.
4. Bunching income into one year can beat smoothing by up to 2 153 € for families at the abono cliff (N5).
5. The art. 70 n.º 3 formula for L, read as printed, would cancel the mínimo de existência above 12 180 €; the
   only consistent reading gives L = 13 863,06 € in 2025 (F4).

## For the Portuguese government
1. **Write art. 68 n.º 2 as "taxa × R − parcela a abater"** (the form the withholding tables already use): the
   rounded column B makes the tax fall by up to 17 cents for one more cent of income and lets the quociente
   conjugal cost up to 28 cents more than separate assessment (F3, `art68_not_monotone`,
   `quociente_can_cost_more`). The OECD already computes it the band-sum way (F2).
2. **Fix the fraction in art. 70 n.º 3** (L = VR − LDG / (T1 × 3,60) + Lim1 / 3,60) and say whether "Taxa 1.º
   escalão em percentagem" means 12,5 or 0,125 (F4); publish the art. 70 n.º 6 values for each year where they
   can be found.
3. **Make the withholding tables continuous** (K = 1 207,45 in Tabela I line 2; the rectification of 29 August
   moved the jump from −0,56 € to +0,41 €) (F8), and state the design assumptions of Tabela III, which
   under-withholds one-earner couples at lower pay all year (F9).
4. **Smooth the abono de família escalões** (a 1 914 € cliff for a single parent) and the art. 70 n.º 4 a)
   joint-return cutoff (F10, F11).
5. **Give mid-year rate laws an effects clause** ("produz efeitos a 1 de janeiro") — Lei 33/2024 and Lei
   55-A/2025 both lack one (F1); correct the AT code's citations (Lei 34/2024 vs 33/2024, "73-A/2024") (F5).
