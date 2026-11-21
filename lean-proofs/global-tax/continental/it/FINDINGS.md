# Italy 2025: findings

Model: `lean/ITTax` (Lean 4.35, TaxKernel), exe `ittax`. Money in cents; Roma Capitale / Lazio resident. Every
amount below is computed by the model and, where a Lean name is given, proved by `decide` at build time (no
`sorry`). Statute texts are in `law/`, official sources in `refs/`.

### F1 The OECD leaves out Lazio's 2025 reliefs on the addizionale regionale
- kind: gov-error (the OECD's model for Italy)
- households: OECD Taxing Wages 2025 types S67, SP67, S100, M100_0, M100_100, M100_67, M100_67nc (Rome)
- amounts: SLT too high by 115,06 (S67, SP67), 60,00 (S100, M100_0), 120,00 (M100_100), 175,05 (M100_67,
  M100_67nc). Every other OECD line for Italy agrees with the model to 0,13 euro (`results/oecd_check.md`).
- provisions: L.R. Lazio 30 dicembre 2024 n. 22 art. 2 c. 2 ("Per gli anni di imposta 2025 e 2026, la maggiorazione
  ... non trova applicazione nei confronti dei soggetti con un reddito imponibile ... fino a 28.000,00 euro") and
  c. 3 ("detrazione ... pari a 60,00 euro ... compreso tra 28.001 e 35.000,00 euro"); L.R. 1/2023 art. 2 c. 1. The
  OECD charges 1,73 % up to 15.000 and 3,33 % above for every income, the rule before these reliefs. Regione
  Lazio's own 2026 table (`refs/Addizionale-regionale-2026.pdf`) shows the same structure continued.
- Lean: `ITTax.lazio`, `ITTax.lazio_notch`; check: `harness/oecd_check.py IT`.
- status: confirmed against the regional statute (Global law italy/lazio/acts, record to 2026-10-30).
- draft note to the OECD (not filed): "Taxing Wages 2026, Italy, 2025: the regional surtax for Lazio should apply
  1.73 % on the whole taxable income when it does not exceed EUR 28 000 (L.R. Lazio 22/2024 art. 2(2)) and allow a
  EUR 60 credit for taxable income between EUR 28 001 and 35 000 (art. 2(3)). As published, SLT is overstated by
  EUR 115.06 at 67 % AW and EUR 60.00 at 100 % AW. L.R. Lazio 4/2024 art. 4 had similar reliefs for 2024."

### F2 Four decimals: the statute truncates the ratios, the OECD does not
- kind: gov-error (convention, 4 cents)
- households: OECD S67, S100 (and every income inside the art. 13 tapers)
- amounts: S100 detrazioni (art. 13 + L. 207/2024 c. 6) 2.390,20 by the statute vs 2.390,24 by the OECD (BTC);
  S67 3.441,69 vs 3.441,73.
- provisions: TUIR art. 13 c. 6 "Se il risultato dei rapporti ... è maggiore di zero, lo stesso si assume nelle prime
  quattro cifre decimali"; art. 12 c. 4 (same rule). L. 207/2024 c. 6 has no such rule (exact).
- Lean: `oecd_s100_btc_statute`, `oecd_s67_btc_statute` (Tests.lean).
- status: convention; the statute is clear, the difference is cents.

### F3 Assegno unico: the OECD revalues with the unrounded factor and uses current income
- kind: gov-error (convention)
- households: SP67, M100_0, M100_100, M100_67 (CTGG)
- amounts: F = 1,081 x 1,054 x 1,008 reproduces the OECD's 4.823,65 exactly (2 children x 12 x 175 x F);
  residuals 0,35 (M100_100) and 0,09 (M100_67) unexplained (ISEE details; not the tabella-1 steps, tested). INPS
  publishes rounded revalued amounts (circ. INPS 33/2025, not read). The real ISEE of 2025 uses 2023 incomes and the
  family's assets (DPCM 159/2013); the OECD and the model use current incomes and no assets.
- provisions: D.Lgs. 230/2021 art. 4 cc. 1, 8, 11; DPCM 159/2013 art. 4 c. 3 e), Allegato 1.
- Lean: `ITTax.auuYear`, `ITTax.isee`.
- status: convention; stated in `unsupported`.

### F4 The stacked cliff at 8.500: one euro of pay costs 300 euro
- kind: loophole-new (cliff, marginal effective rate far above 100 %)
- households: single employee (also single parent; second earner of a couple), gross 9.391 -> 9.392 (reddito
  complessivo 8.499,79 -> 8.500,70)
- amounts: 300,26 euro lost for 1 euro of gross pay; gross pay must rise by 412 euro to recover.
- provisions: L. 207/2024 art. 1 c. 4 (7,1 % of the whole income up to 8.500, 5,3 % above: -153,00); D.Lgs.
  446/1997 art. 50 c. 2 and D.Lgs. 360/1998 art. 1 c. 4 (addizionali due only "se ... risulta dovuta" IRPEF, which
  happens exactly from 8.500 because 23 % x 8.500 = 1.955 = the art. 13 c. 1 a) detrazione): +147,05.
- Lean: `ITTax.cliff_8500`, `ITTax.cuneo_cliff_8500`; scanner `results/search/METR.md`.
- status: the 8.500 edge of the cuneo is in the press (money.it, investireoggi, quifinanza) and OCPI ("La giungla
  dell'Irpef per i lavoratori dipendenti", E. Franzetti, 11-03-2025, peaks at 8.500, 15.000, 20.000); none of the 5
  sources searched (those four and AdE circ. 4/E 2025) combines it with the addizionali becoming due at the same
  point (OCPI does not model the addizionali).

### F5 A small pension contribution buys back the addizionali (the state pays up to 173 % of it)
- kind: loophole-new (a deduction to cross a threshold)
- households: employees on 9.500, 31.050 and 15.500 gross (Rome)
- amounts: 99 euro into a pension fund saves 171,39 (IRPEF 22,64 + Lazio 148,75); 103,36 saves 188,54 at Lazio's
  28.000 edge; 29,06 saves 133,44 at Rome's 14.000 exemption. The money contributed stays the worker's savings.
- provisions: D.Lgs. 252/2005 art. 8 c. 4 (deductible "dal reddito complessivo ... non superiore ad euro 5.164,57");
  the addizionali bases and the "dovuta" test use income "al netto degli oneri deducibili" (D.Lgs. 446/1997 art. 50
  c. 2; D.Lgs. 360/1998 art. 1 c. 4; L.R. 22/2024 art. 2 cc. 2-3; delibera A.C. 186/2024), while the detrazioni
  (TUIR art. 13), the trattamento integrativo and the cuneo (L. 207/2024 cc. 4-6) test the reddito complessivo
  before the deduction, so they do not fall.
- Lean: `contrib_8500`, `contrib_lazio_28000`, `contrib_roma_14000`.
- status: not found in the 5 sources searched (as F4); "pension contributions are deductible" is common advice,
  the threshold arithmetic is not.

### F6 The 35.000 double edge
- kind: loophole-new (cliff)
- households: single employee, gross 38.669 -> 38.670
- amounts: 125,57 for one euro (65 from TUIR art. 13 c. 1.1, ending "ma non a 35.000 euro" of reddito complessivo;
  60 from L.R. 22/2024 art. 2 c. 3, ending at 35.000,00 of imponibile); 350 euro of pay to recover.
- Lean: `cliff_35000`.
- status: each edge is in its statute; the stacking was not found in the sources searched.

### F7 The addizionali switch on, off and on again
- kind: loophole-new (net income not monotone)
- households: one-earner married couple, spouse dependent, one child aged 22 (Rome)
- amounts: +485,31 for one euro at reddito complessivo 18.438,70 (IRPEF netta turns positive: addizionali due);
  -83,77 at 20.000 (the 960 cuneo cash ends, the 1.000 detrazione of c. 6 cancels the netta and with it the
  addizionali); +564,66 at 21.455,40 (netta positive again).
- provisions: TUIR art. 12 c. 1 a), c); L. 207/2024 cc. 4, 6; D.Lgs. 446/1997 art. 50 c. 2.
- Lean: `family_on_off_on`; scanner profile `married_one_earner_child22`.
- status: not found in the sources searched.

### F8 Known cliffs, recreated by the scanner without being told
- kind: loophole-known
- amounts (single employee unless stated, gross pay): Rome's 14.000 exemption (126,00; `roma_notch`); the 15.000
  edge where the trattamento integrativo ends and the cuneo falls from 5,3 % to 4,8 % (129,40;
  `cuneo_cliff_15000`, `detrDip_jump_15000`); Lazio's 28.000 (207,55; `lazio_notch`); the dependent-spouse
  limit 2.840,51 (710,02 when the spouse earns one euro more; `spouse_limit`); pensioner and self-employed analogues
  at 8.500 / 5.500, 14.000, 28.000, 29.000 / 17.000 and 35.000 (`results/search/METR.md`).
- status: catalogued (CATALOGUE.md K1, K9, K10).

### F9 The 2025 TUIR still counts in lire, and the dependants' limit has not moved since 1995
- kind: statute-fault (amounts not updated)
- provisions (text in force 2025-12-31, `law/tuir_art*.md`): art. 10 ("lire 3.000.000"); art. 15 c. 1 c) ("lire
  250 mila", the 129,11-euro medical franchise; "lire trentacinque milioni"; "lire 30 milioni"); art. 15 ("5 milioni
  di lire" of mortgage interest); art. 15 c. 2 ("limite annuo di lire 12.000.000"); art. 51 c. 2 g) ("lire 4
  milioni"); art. 51 c. 5 ("lire 90.000 al giorno ... lire 150", "lire 30.000 ... lire 50"); art. 51 c. 6 ("lire 3
  milioni ... 9 milioni"). The euro changeover keeps them valid at 1.936,27 lire per euro, frozen at pre-2002
  values. Art. 12 c. 2: a dependant may earn "non superiore a 2.840,51 euro" (5,5 million lire), the limit behind
  F8's 710-euro notch.
- status: statute-fault (amounts not updated); harmless legally, material economically.

### F10 Art. 13 points to commi that no longer exist
- kind: statute-fault (references to repealed provisions)
- provisions: TUIR art. 13 c. 5 ("non cumulabile con quelle previste ai commi 1, 2, 3 e 4"), c. 5-bis ("commi 1, 2,
  3, 4 e 5"), c. 6 ("rapporti indicati nei commi 1, 3, 4 e 5"); c. 2 was repealed by L. 147/2013 and c. 4 is "non
  più previsto" (L. 232/2016).
- status: harmless dangling references; a consolidated text (the 2026 testo unico) is the place to clean them.

### F11 The four-decimal rule creates its own small notches
- kind: statute-fault (rounding)
- amounts: at reddito complessivo 28.000 -> 28.000,01 the art. 13 c) ratio (50.000 - R)/22.000 = 0,99999... counts as
  0,9999: the detrazione falls by 0,19 euro for one cent (`detrDip_28000_50000`). At 15.000 the detrazione jumps
  UP from 1.955 to 3.099,88 (`detrDip_jump_15000`), by design (it takes over from the trattamento integrativo).
- status: rounding effect of art. 13 c. 6; tiny.

### F12 Lazio's 60-euro band starts at 28.001
- kind: reading
- provisions: L.R. 22/2024 art. 2 c. 3 "compreso tra 28.001 e 35.000,00 euro" while c. 2 ends at "28.000,00": an
  imponibile between 28.000,01 and 28.000,99 gets neither relief (`lazio_notch`: 692,40 at 28.000,01, 632,43 at
  28.001). The return states whole euros, so the gap matters only to payroll computations in cents.
- status: reading; harmless in the return.

### F13 Circolare 4/E 2025 on "familiari" was overtaken, retroactively, by D.Lgs. 192/2025
- kind: gov-error (guidance superseded)
- provisions: AdE circ. 16-05-2025 n. 4/E, note 60: art. 51's references to art. 12 "vanno riferiti alla versione
  ... in vigore dal 1 gennaio 2025, che non richiama più i soggetti indicati nell'articolo 433 c.c.". TUIR art. 12
  c. 4-ter, inserted by D.Lgs. 18-12-2025 n. 192 art. 1 c. 1 and applying "a partire dal periodo di imposta in corso
  alla data di entrata in vigore" (2025, art. 1 c. 2), brings back "le altre persone elencate nell'articolo 433 del
  codice civile che convivono con il contribuente". For 2025, benefits for a cohabiting parent of the employee fall
  again within art. 51's family references, contrary to the circular.
- status: the circular was right when written; employers who followed it may have taxed in 2025 benefits that the
  statute now treats as family benefits. An AdE update would settle it.

### F14 Model choices recorded
- kind: model-fix
- rent: the model picks cedolare secca or IRPEF, whichever leaves the household more (`--rent=` forces one).
  Self-employed INPS and the forfettario are not in the default output (`unsupported`), only in Loopholes.lean.
  Couples: each spouse is a separate taxpayer; household investment income, rent, contributions and gifts split
  equally.

### Kernel generic scanners (family agent, 2026-11-19)
The kernel's scanners (`~/cmp20/harness/search/run_all.py IT`, copied to `results/search/kernel/`) re-find the
worker's cliffs without being told: the 8.500 cuneo/addizionali cliff (299 € at 9.391, N1/K9), the spouse-a-carico
limit (709 € at a second-earner gross of 3.138, K1), the Roma 14.000 and Lazio 28.000 edges, the trattamento
integrativo edge. One instance not written up above: a one-earner couple with two children (the kernel's family
type) loses **421,69 €** for one more euro at 17.740 gross, where the trattamento integrativo falls from 0,26 € to 0
so the IRPEF netta turns positive and both addizionali become due in full (regional 277,79 + comunale 144,52;
D.Lgs. 446/1997 art. 50 c. 2; D.Lgs. 360/1998 art. 1 c. 4). Same mechanism as K9 (no-tax area), larger amount
because the spouse detrazione (art. 12) moves the no-tax area up to where the surcharges are larger. Status: lead
from the scanner, mechanism checked in the scanner's detail lines; no separate Lean statement.
