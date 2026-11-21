# Belgium (income year 2025, exercice d'imposition / aanslagjaar 2026): findings

Model: `lean/BETax` (exe `betax`), resident of the City of Brussels (Brussels-Capital Region). Amounts in EUR.
Sources: `lean/BETax/Params.lean` (every number cited) and `PROGRESS.md`. "Lean" = the theorem or definition that
states or computes the finding (all proved, no `sorry`).

### F1 Brussels family-allowance ceilings are cliffs: one euro of taxable income can cost up to 2.954 EUR a year
- kind: loophole-new (notch / METR > 100 %; novelty: NOVEL.md N1)
- households (betax default, children 6 and 11 unless stated, one earner): single parent 2 children: gross
  52.597 -> 52.598 (household taxable income crosses 39.792,84): net -1.504 EUR; single-earner couple 2 children:
  -1.232; couple 3 children (3, 5, 9): -1.559 there and -2.954 at the second ceiling (taxable 57.763,80; gross 73.271);
  1 child: -548. January's lower ceilings (39.011,96 / 56.630,27) add smaller steps (-62 to -263) earlier.
- provisions: ordonnance 25.04.2019 art. 9 (supplement social by "revenus du menage": below the first ceiling,
  between the ceilings, nothing above); Famiris baremes 01/01/2025 and 01/02/2025 para. 3.1-3.3 (all-or-nothing amounts).
- found blind by the generic METR scan (bands > 100 % at 0,828-0,844 AW and 1,174-1,176 AW, peak 1.260 %, notch 1.503
  at 52.597): `results/search/SUMMARY.md`.
- Lean: `famiris_notch_plafond1` (111,90 EUR a month for one euro, two children), `famiris_notch_plafond2` (62,18).
- gain: a household just above a ceiling gains the whole step by lowering taxable income below it (real expenses
  instead of the art. 51 forfait; moving a bonus to another year).
- status: confirmed in the model; the reference year Famiris uses for "revenus du menage" is not modelled (current
  year's household taxable income used, as the OECD does).

### F2 OECD Taxing Wages counts LGAF age supplements the bareme freezes (+640,98 EUR for M100_100 and M100_67)
- kind: gov-error (OECD model; classification: reading, likely error)
- OECD CTGG 4.886,66 = old federal (LGAF) transitional amounts 119,12 + 220,41 plus age supplements 20,75 + 41,38 a
  month (Feb-Dec; January at index 128,11) plus July supplements 2 x 37,30: reproduced to the cent by `betax --oecd`.
- authority: Famiris bareme 01/02/2025, LGAF part, footnote (3): "Le nombre d'enfants beneficiaires pris en compte en
  decembre 2019 et le supplement d'age de decembre 2019 ne peuvent a aucun moment augmenter apres le 31 decembre 2019."
  Children aged 6 and 11 in 2025 were about 0 and 5 in December 2019 (no age supplement), so the Brussels regime
  (2 x (186,51 - 12,43) a month) is higher: 4.245,68 (betax default).
- Lean: `famOldMonth ... frozen` (default; `--oecd` / `--unfrozen-age` reproduce the OECD). status: open.
- draft note (not sent): "Belgium, CTGG for M100_100 and M100_67 (2025): the LGAF transitional age supplements cannot
  exceed their December-2019 level (Famiris bareme, footnote 3); for children aged 6 and 11 that level is nil, so the
  Brussels regime applies: CTGG 4.245,68, not 4.886,66."

### F3 FisconetPlus' AI 2026 version of art. 134 para. 4 al. 3 drops the carried-interest words inserted in July 2025
- kind: gov-error (official consolidation)
- Lprog 18.07.2025 art. 13 inserted "et 6°" (art. 17 para. 1, 6°: carried interest) from 29.07.2025; the Fisconet
  version "applicable a partir de l'exercice d'imposition 2026 (art. 42 et 44, L 18.12.2025)" reads again "articles
  17, para. 1er, 1° a 3° et 90", while the 29.07.2025 and AI 2027 versions have "et 6°". Art. 87 and 88 carry "et 6°"
  from 29.07.2025 (checked). File `law/cir92/fisconet_art134.txt` (version headers at lines 123, 169, 76).
- effect: none for wage earners. status: open; draft report to SPF Finances (not sent): "Art. 134 para. 4 al. 3,
  version AI 2026 (L 18.12.2025): the words 'et 6°' after 'articles 17, para. 1er, 1° a 3°' (Lprog 18.07.2025 art. 13)
  are missing."

### F4 Art. 134 para. 3 al. 2 calls the 550 EUR child-credit cap a "montant de base", yet it is not indexed
- kind: statute-fault (drafting; resolved by art. 178 para. 5, 3°/1, which excludes "les montants vises aux articles
  134, para. 3, alinea 2"; SPF notice: "montant non-indexe de 550 euros"). Read as indexed it would be 1.253 EUR.
- Lean: `childCreditCap := 55000`.

### F5 The exempt sum is valued on the frozen pre-2017 tariff (a 30 % band the income tariff no longer has)
- kind: statute-fault (structural)
- art. 134 para. 2 al. 2: 25/30/40/45/50 % on 11.460 / 16.320 / 27.190 / 49.840 (AI 2026); art. 130: 25/40/45/50 %
  on 16.320 / 28.800 / 49.840. Exempt amounts above 11.460 (only with child or single-parent supplements) are worth
  30 % although that income slice is taxed at 25 %; from 27.190 they are worth 45 % against 40 % up to 28.800.
  A single parent with one child (exempt 14.870) gets 3.888 EUR, 170,50 more than 25 % of it.
- Lean: `exempt_tariff_gap` (for all x in [11.460, 16.320]: art134 - art130 = 5 % x (x - 11.460)). Kernel gap:
  `Family.lowBandReduction` assumes one schedule (INBOX).

### F6 De facto cohabitants keep the single-parent supplement married parents cannot get (known; closed from AI 2030)
- kind: loophole-known
- two earners of 50.000 with children 6 and 11: as de facto cohabitants the partner declaring the children gets
  art. 133 al. 1, 1° (1.980 EUR exempt): burden 28.593 vs 29.341 married (-748). The unit scanner's largest
  "marriage penalty" (-1.621 EUR at 0,8 AW, 50/50, 2 children) is this plus the CSSS scales.
- provisions: art. 133 al. 1, 1° (version AI 2022-2029: no household condition on the 1.980 supplement);
  L 15.07.2026 art. 9 adds for AI 2030 "n'est accorde que si aucune personne autre que les enfants ... ne fait partie
  du menage". Lean: `single` with `claimsKids`. status: recreated blind (unit scanner).

### F7 Marriage (or legal cohabitation) bonus: quotient conjugal and the joint CSSS scale (known)
- kind: loophole-known. unit scanner: bonus up to 6.458 EUR (10,4 % AW), 1,3 AW single-earner couple, no children
  (art. 87-88: 30 % of professional income, max 13.460, moved to the spouse's low bands); CSSS joint scale (loi
  30.03.1994 art. 108 para. 1 al. 3) alone saves 421,66 for two taxable incomes of 48.269.
- Lean: `quotient_sum`, `quotient_le_cap`, `csss_marriage_bonus`. status: recreated blind.

### F8 The work bonus is individual: splitting a couple's earnings doubles it
- kind: loophole-known (design: loi 20.12.1999 art. 2; CIR art. 289ter/1)
- couple with two children, 53.000 EUR earned by one partner vs 26.500 each: cohabitants -15.854 burden (unit scanner
  "split_gain_cohabiting", 25 % AW), married -9.832: each low earner gets the social bonus (about 3.290 a year at 2.208
  a month) and the fiscal bonus (2.880 together), and the household's taxable income falls under a Famiris ceiling.
- status: recreated blind; a targeting choice rather than a loophole.

### F9 Withholding formula 2025 vs the final tax: Brussels residents are over-withheld (convention)
- kind: gov-error (classification: convention)
- `harness/withholding.py` / `results/withholding.md`: formule-cle 01.01.2025 (ESS-SR/2024-0015) uses brackets
  16.310 / 28.790 / 49.820 and an exempt sum of 10.900 (final AI 2026: 16.320 / 28.800 / 49.840 and 10.910; the formula
  predates the final indexation coefficient), a 7 % municipal surcharge (n° 5) and no regional reduction (Brussels:
  federal + regional = 99,5 % of the state tax, `bxl_total_share`).
- 542 wage points: withholding exceeds the City-of-Brussels liability by 33 to 1.497 EUR (mean 666); against a 7 %
  municipal rate by 9 to 1.497 (largest at low wages, where the fiscal work bonus is refunded only at assessment).

### F10 The OECD's local line implies a 6,0 % municipal rate; the City of Brussels levies 4,9 % for AI 2026
- kind: gov-error (classification: convention; open)
- for all eight types SLT - 32,591 % x CGITFP = 6,000 % x (CGITFP + regional) to the cent (`--oecd` =
  `--commune-bp=600`). SPF Finances lists: City of Brussels 6 % (AI 2025 list), 4,9 % (AI 2026 list); unweighted mean
  of the 565 municipalities in the AI 2026 list 7,55 %. The OECD country description was not readable (oecd.org
  answers 403 to automated clients): whether 6,0 % is an average or last year's City-of-Brussels rate is open.

### F11 Belgium's official legal database has not updated the income tax code since 2002
- kind: statute-fault (publication). Justel, CIR 92: "LA MISE A JOUR DE CE TEXTE EST SUSPENDUE DEPUIS 2002"; the
  dated consolidation is SPF Finances' FisconetPlus (public REST endpoint used here: `harness/fisconet.py`).
  Also: the CSSS is loi 30.03.1994 art. 106-112 (Justel, updated to 30-12-2025), not the loi-programme 30.12.1988.

### F12 One euro of director's pay can save 5.000 EUR of corporate tax (art. 215; known)
- kind: loophole-known. Art. 215 al. 2-3, 4°: the 20 % rate on the first 100.000 EUR needs a director's pay of at
  least 25.000 EUR (base) indexed with 2,0096 and rounded to 1.000 (50.000 EUR), or at least the taxable result.
- Lean: `citSme`, `cit_pay_notch` (profit 150.000 before pay: 50.000 instead of 49.999 -> CIT -5.000,25).
- the harness' company.json for BE has a flat 25 % CIT (INBOX); the owner scanner therefore misses it.

### F13 Capital gains on shares are untaxed in 2025 (known; changes from 2026)
- kind: loophole-known; art. 90, 1° (normal management of private wealth); income_type scanner: +54,6 % net vs wages
  at 5 AW. status: recreated blind.

### F14 Single parent reaching 4.100 EUR of net professional income: one euro more earns 322 EUR
- kind: loophole-new (notch, favourable side; NOVEL.md N2)
- single parent, children 4 and 8: gross 5.857 -> 5.858 (net professional income reaches 4.100): net +322 EUR.
- provisions: art. 133 al. 2, third indent ("revenus professionnels nets ... au moins egaux a 1.800 euros", AI 2026
  4.100); art. 134 para. 3 al. 5 (unused tax on the extra supplement becomes a refundable credit).
- Lean: `spExtra` (cut-off `spExtraMinProf`), `unusedParts`; confirmed by a one-euro scan.

### F15 The single parent's extra supplement tapers at 25,1 % of income (marginal rate + 7,5 to 10 points)
- kind: loophole-known (statutory taper, art. 133 al. 3). Lean: `spExtra_ends`, `spExtra_slope`
  (19.250 -> 24.390 EUR taxable: 1.290 EUR of exempt sum withdrawn, valued at 30-40 % on the art. 134 tariff).

### F16 Model fix: the CSSS is a household contribution with two scales (since 10.04.2022)
- kind: model-fix. The OECD's EECSSC_PTI (576,46 single; 477,52 one-earner couple; 731,70 two earners) is the annual
  CSSS of art. 108 para. 1 (individual vs joint scale on household taxable income), not the ONSS quarterly withholding
  (523,52 a year for S100). betax uses the annual law: all eight types within 0,42 EUR.

### F17 Generic scanner artefact: bands of 59,7-60,5 % "above the top rate" for high earners
- kind: model-fix (note). They are 125 EUR wide and recur; they come from the five output lines being rounded to whole
  euros (up to 2,5 EUR of noise per step); the cent-level detail lines show the statutory 58,6 %.
