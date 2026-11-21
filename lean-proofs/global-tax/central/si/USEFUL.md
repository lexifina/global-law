# Slovenia 2025: what this work is most useful for

Evidence: `FINDINGS.md` (F-numbers), Lean theorems in `lean/SiTax/Findings.lean` and `Theorems.lean`, scans in
`results/`. The model matches the OECD's 2025 Taxing Wages lines for Slovenia 56 of 56 (F1).

## Taxpayers
1. **Child benefit (otroški dodatek) jumps, it does not slide.** One more euro of annual income can cost 300-940 €
   a year of benefit for a family with two children (F7); above 1.293,36 € per person per month it stops entirely
   (F8). The class is set by the *previous* calendar year's income, so a December bonus or overtime can cost a whole
   year of benefit. `F7_single_notch`, `F8_cliff`.
2. **Agree who claims the children.** The higher earner should claim the child allowances (the other parent gets
   any unused rest); getting it wrong costs up to 1.422 € a year, and not agreeing (half each) up to 711 € (F13).
3. **A non-working spouse's first job has a hidden price.** The earner loses the 2.838,30 € dependant allowance as
   soon as the spouse is employed at all: 455-1.420 € of extra tax (F9). Plan the spouse's start for a full year.
4. **Low-wage band at 53,7 %.** Between about 13.100 and 16.832 € gross a raise of 100 € leaves 46 € (F12).

## Advisers
1. **Check the child-benefit class before claiming every relief.** A family near a class edge can be 600-880 € better
   off claiming slightly less child allowance (F10, 6,7 % of the families scanned) — confirm with the CSD first.
2. **Flat-rate s.p. (normiranci).** At 60.000 € revenue with low real costs the total burden is about 16 % against 48 %
   as an employee; a side s.p. pays 13-14 % at the margin against 51-53 % as extra wages (F15). The deemed 20 % profit
   is also what the child-benefit test sees (F11) and is ignored by the low-income allowance test (F14).
3. **Owner-managers:** a salary of about 12.900 € (the end of the zero-tax zone) plus dividends is the cheapest mix at
   every profit level; up to 60.000 € a year saved at 10 × the average wage (F16).
4. **Holding periods:** gains are 25/20/15/0 % after 0/5/10/15 years (F17).

## Government (Ministry of Finance, MDDSZ, FURS)
1. **Replace the child-benefit classes by a taper.** The 8 nominal classes create METRs above 1.000 % for 2-8 income
   bands per family type and a 930 € cliff at the top (F7, F8); a sliding withdrawal of the same total cost would
   remove the notches (the kernel proves a taper has no jump, `Taper.amount_step`).
2. **Means-test flat-rate s.p. income on revenue, not on the deemed 20 % profit.** A family keeping 50.000 € after
   tax gets the maximum benefit (F11); the same exclusion lets flat-rate income escape the withdrawal of the
   additional general allowance (F14).
3. **Phase the dependent-spouse allowance out** with the spouse's income instead of the all-or-nothing "ni zaposlen"
   test (F9); and consider the after-tax income test interaction (F10: relief claimed = benefit lost).
4. **Fix the documents:** FURS guide 8.4 prints 2.060,97 € for 2.060,87 € (F5); ZDoh-2 čl. 112(1) and 117(1) still
   print 2006 amounts 21,5 % below the operative ones while the neighbouring amounts were re-enacted (F6); the čl.
   111(3) formula is negative (−0,04 €) at its own threshold (F3).

## Researchers
- A cent-level Lean model of Slovene PIT, contributions and child benefit for 2025 on the shared TaxKernel
  (Schedule, Taper, Contribution, Table), with FURS's printed tables proved equal to the statute (`furs_fixed_amounts`,
  `monthly_fixed_amounts`, `indexation_2025`) and every finding proved on a named household.
