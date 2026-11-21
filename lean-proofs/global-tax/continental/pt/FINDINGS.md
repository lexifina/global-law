# PT findings (IRS 2025, mainland)

Each block: kind (loophole-known | loophole-new | gov-error | statute-fault | model-fix | reading | convention),
households, amounts, provisions, Lean name, status. Amounts in euros unless stated.

### F1 Which 2025 schedule: Lei 55-A/2025 for the whole year (OECD and AT agree); the law itself never says so
* kind: reading (statute-fault candidate)
* What: the 2025 rates were enacted twice. Lei 45-A/2024 (OE 2025) updated the art. 68 thresholds (8 059 ... 83 696)
  and kept the Lei 33/2024 rates (13; 16,5; 22; 25; 32; 35,5; 43,5; 45; 48 %, written "[...]"). Lei 55-A/2025 of
  22 July 2025 (art. 2) replaced the rates of escalões 1-8 (12,5; 16; 21,5; 24,4; 31,4; 34,9; 43,1; 44,6 %) and
  column B. Its art. 4 says only "entra em vigor no dia seguinte ao da sua publicação" (23 July 2025): no clause
  makes it apply to income from 1 January 2025. The same is true of Lei 33/2024 (art. 3) for 2024.
* Which applies: the AT applies the new table to the whole year (the August-September 2025 withholding tables,
  Despacho 8464-A/2025, were cut further to give back the January-July over-withholding, which only makes sense if
  the annual tax uses the new rates), and the OECD's 2025 figures are exactly the Lei 55-A rates on the OE 2025
  thresholds (S100: 8 059 × 12,5 % + 4 101 × 16 % + 5 073 × 21,5 % + 2 558,83 × 24,4 % = 3 378,58). The legal
  basis is the reading that the IRS is assessed on the year as a whole (the tax of the year is settled once, after
  31 December); LGT art. 12 n.º 2 ("Se o facto tributário for de formação
  sucessiva, a lei nova só se aplica ao período decorrido a partir da sua entrada em vigor") read literally would
  give a pro-rata year instead. A reduction raises no constitutional bar (CRP art. 103 n.º 3 forbids only
  retroactive tax increases), so the whole-year reading is safe, but the statute leaves it to inference.
* Model: Lei 55-A/2025 rates for the whole year (`Params.art68Rows`); the OE 2025 rates are kept as
  `art68BandsOE2025` for the withholding analysis.
* Sources: law/Lei_55_A_2025.txt (AT copy of DR n.º 139/2025, Suplemento); law/Lei_45_A_2024.txt p. 51-52;
  Global law portugal/national/acts/legislacao/lei/2024/33 (DR https://diariodarepublica.pt/dr/detalhe/lei/33-2024-875716577).
* Status: recorded; proposed fix: mid-year rate laws should say "produz efeitos a 1 de janeiro de <ano>".

### F2 OECD Taxing Wages 2025 for Portugal: agreement and the two conventions behind every cent of difference
* kind: convention (OECD) / model-fix
* Households: the 8 OECD types at AW = 24 253,98.
* Result: 48/48 lines within 0,20 EUR at the OECD's own gross; 37/48 to the cent. The 11 differences:
  (a) CIRS art. 68 n.º 2 computes the tax as "limite × taxa média (coluna B) + excedente × taxa normal (coluna A)"
  with column B rounded to three decimals; the OECD computes the exact sum over the bands. Inside each escalão the
  difference is a constant (`art68Err`): S100 (coletável 19 791,83, escalão 4) statute 3 378,53, OECD 3 378,58
  (−0,0519); S167 −0,062; couples twice that. (b) Abono de família for the single parent: the 50 % monoparental
  increase of Portaria 112/2025/1 art. 4 is applied to the monthly amount (73,51 → 110,27 per child-month, paid
  monthly in cents), the OECD applies it to the annual sum (2 646,36 vs 2 646,48).
  With the OECD's conventions (`pttax --bandsum --abono-annual`) 44/48 match to the cent; the other 4 are 0,01
  (S167 rounding of 8 572,615; M100_100 where separate assessment is 0,01 cheaper than joint and the model takes it).
* Who is right: the statute (art. 68 n.º 2 is explicit); the OECD's band sum equals the "taxa × R − parcela a
  abater" form the AT uses in its withholding tables, so the OECD is a convention, not an error. Monthly rounding of
  the abono is how it is paid.
* Lean: `art68_minus_bands`, `art68_close` (statute − band sum ∈ [−0,0859; +0,1848] € for every coletável).
* Status: explained.

### F3 Art. 68 n.º 2: one more cent of income can lower the tax (column B rounding)
* kind: statute-fault (tiny)
* What: because column B is rounded, the statutory tax jumps at each escalão limit: at 12 160 € by −4 cents,
  17 233: 0, 22 306: +11, 28 400: −12, 41 629: +15, 44 987: −17, 83 696: +28 (one taxpayer; twice for a joint
  return at twice the limit). At 28 400,00 € of rendimento coletável the coleta is 12 cents lower than at
  28 399,99 €; at 44 987,00 € 17 cents lower than at 44 986,99 €.
* Lean: `art68_jump_28400`, `art68_jump_44987`, `art68_jump_12160`, `art68_jump_joint_56800`,
  `art68_not_monotone` (the statutory tax is not a monotone function: the kernel's `Schedule.ticks_mono` cannot
  hold for it); the band sum satisfies all kernel theorems (`art68Bands_progressive`, `_mono`, `_convex`).
* Joint vs separate: the same rounding makes the statute's quociente conjugal cost more than two separate
  assessments in places: spouses with 83 695,91 € and 83 696,64 € of rendimento coletável pay 0,28 € more jointly
  (`quociente_can_cost_more`); the kernel's `splitting_le_separate` holds only for the band sum
  (`quociente_bands_le_separate`). Searched near every limit: 0,28 € is the largest found.
* Size: cents. Fix: compute column B to more decimals, or write n.º 2 as "taxa normal × R − parcela a abater"
  (the form the withholding tables already use), which is exactly the band sum.
* Status: proved; reported to kernel INBOX.

### F4 Art. 70 n.º 3: the formula for L, read as printed, makes the mínimo de existência vanish above 12 180 €
* kind: statute-fault (drafting) / reading
* What: n.º 3 reads "L = valor de referência - (Limite despesas gerais/Taxa 1.º escalão x 3,60) + (Limite 1.º
  escalão/3,60)" (AT consolidated code and the DRE consolidated text of the CIRS annex, identical). Read with the
  usual precedence, (250 / 12,5 %) × 3,60 = 7 200 and L = 12 180 − 7 200 + 2 238,61 = 7 218,61 € < valor de
  referência: alínea b) (VR < RB ≤ L) is empty and alínea c) gives an abatimento of 0 for everyone above 12 180 €.
  n.º 5 d) adds a second ambiguity ("Taxa 1.º escalão, ... em percentagem": 12,5 or 0,125). The only reading under
  which the abatimento is continuous at L is L = VR + (Lim1 − LDG/T1) / 3,60 = 13 863,06 € in 2025, i.e.
  "Limite despesas gerais / (Taxa 1.º escalão × 3,60)". The model uses it (`Minimo.meL36`).
* Lean: `me_segment_b_step` / `me_segment_c_step` (intended reading: 3,6 and 2,35 € of coletável per € earned).
* Status: recorded; the AT's n.º 6 publication of the 2025 variables and simplified formulas not yet located.

### F5 Two laws of 7 August 2024 rewrote art. 70 n.º 2 c) with the same words; the AT cites only one
* kind: gov-error (citation) / statute oddity
* What: Lei 33/2024 art. 2 and Lei 34/2024 art. 2, both of 7 August 2024, each give art. 70 n.º 2 c) the identical
  wording "L – limite do 1.º escalão – 1,35 × (rendimentos brutos – L)". The AT's consolidated CIRS cites
  "Redação da Lei nº 34/2024" only. Also the AT's current art. 70 n.º 1 cites "Lei n.º 73-A/2024, de 30 de
  dezembro" for the 2026 value (12 880 €): the OE 2026 is Lei n.º 73-A/2025 (the AT's own note on art. 72 n.º 19).
* Status: recorded (no effect on amounts).

### F6 Art. 68-B automatic indexation vs the OE 2025 thresholds
* kind: lead (to check)
* What: Lei 34/2024 art. 3 added art. 68-B: the escalão limits are "atualizado[s] anualmente" by
  (1 + t.v. deflator PIB) × (1 + t.v. PIB por trabalhador), published by portaria by 20 September. The OE 2025 then
  wrote the 2025 limits directly (+4,6 % on Lei 33/2024's). Whether the two agree (and which governs if not) is open.
* Status: open.

### F7 The August-September 2025 withholding cut returned about 13 times what January-July had over-withheld
* kind: gov output vs its stated purpose (reading; not a statute error)
* What: Circular 4/2025 says Despacho 8464-A/2025 approved tables I-A... for pay of 1 August - 30 September 2025 "para
  compensar as retenções já efetuadas em 2025 relativamente aos rendimentos obtidos nos meses anteriores" to Lei
  55-A/2025. For a single employee (Tabela I) with constant monthly pay R paid 14 times (CIRS art. 99-C n.º 5:
  subsídios withheld on their own; 8 payments on the January table, 2 on the August table, 4 on the October
  table), the August-September cut, measured against the October table, is a median 12,8 times (max 14,6) the
  January-July excess over the October table. At 2 000 €/month: excess 63,28 €, cut 592,46 € (Lean
  `compensation_2000`, `withheld2025_2000`).
* Effect against the statute's annual IRS (pttax; despesas gerais 250 €, which the tables' design assumes):
  2025 withholding is below the final IRS at 5 130 of the 5 131 monthly pays from 871 to 6 000 € (by up to
  1 154,04 € at 5 547 €/month; 204,69 € at 2 000 €), whereas the October table used all year would leave only 194
  of them under-withheld. Single parents (Tabela II, one child): over-withheld up to 164 € below ~2 000 €/month,
  under-withheld above. One-earner couples (Tabela III): see F9.
* Who is right: no rule fixes how much the tables must withhold (CIRS art. 99-F: tables approved by despacho);
  the tables' design is a policy choice. The finding is that the cut is not a compensation of the January-July
  excess but an advance of most of the year's rate cut and more: households should expect smaller refunds or a
  payment in the 2026 assessment of 2025 income.
* Assumptions: constant pay, subsídio de férias paid by July, no other deductions (other deductions lower the
  final IRS and so shrink the gap). Data: `refs/withholding_2025.json` (parsed from the circulars),
  `results/withholding_2025.json`, script `harness/withholding_vs_statute.py`.
* Status: recorded.

### F8 The withholding tables jump at 992 €/month; the 29 August rectification moved the jump, it did not remove it
* kind: gov-error (small)
* What: in the two lowest taxed lines the parcela is "taxa x 2,60 x (K - R)" and "taxa x 1,35 x (K - R)".
  October table I as published 22 July (K = 1 205,71): one cent more pay at 992 € lowers the withholding by 0,56 €;
  after Declaração de Retificação 815/2025/2 (K = 1 208,71) it raises it by 0,41 €. Continuity needs
  K = 1 207,45. January table I (13 %): −0,34 € at 992 €. Table III (casado único titular), October: −0,62 € at
  992 €; January: +0,18 € at 957 €. Smaller jumps (up to ±0,75 €) at most other limits because the parcelas are
  rounded to the cent and the limits to the euro.
* Lean: `tabIOct_jump_992`, `tabIOctOrig_jump_992`, `tabIJan_jump_992`; the printed check value
  `tabIOct_992` (53,57 € = the table's "5,4 %").
* Also: the table's line break is at 992 € while the statute's L / 14 = 990,22 €, and the statutory K for line 2
  (the monthly copy of art. 70 b) with the 250 € despesas gerais) is 870 × 0,45 / 0,325 = 1 204,62 €.
* Draft issue (not filed): "Despacho 8464-A/2025 (retificado), Tabela I, 2.º escalão: K = 1 208,71 makes the
  retention discontinuous at 992 € (53,57 € → 53,98 €). K = 1 207,45 gives continuity with the 3.º escalão
  (16 % × 1,35 × (1 476,91 − R))."
* Status: recorded.

### F9 Tabela III (married, one earner) under-withholds against the joint return at lower pay even all year
* kind: reading (design)
* What: with the October Tabela III all year, the withholding is below the joint statute IRS (despesas gerais
  2 × 250 €) at 2 037 of 5 131 monthly pays (870-6 000 €), e.g. −277,41 € at 1 200 €; it withholds nothing up to
  957 €/month while the statute taxes a one-earner couple from 909,68 €/month (12 735,56 € a year: 0,45 × (RB −
  12 180) − 250 > 0).
* Status: recorded; the AT's design assumptions for Tabela III are not published with the tables.

### F10 Abono de família cliffs (NOVEL N1)
* kind: loophole-new (design cliff; not claimed new, see NOVEL.md)
* Households: two children 8 and 10; household income 37 306 → 37 307 €: −1 276,32 € (couple), −1 914,48 €
  (single parent). Provisions: DL 176/2003 arts 9, 14; Portaria 112/2025/1 arts 2, 4.
* Lean: `abono_cliff_couple`, `abono_cliff_single_parent`, `abono_step_2_3`. Status: proved.

### F11 Joint returns lose the mínimo de existência at 32 186 € (NOVEL N2)
* kind: loophole-new (notch; not claimed new)
* Household: 13 000 € + 19 186/19 187 €: −249,92 € for +1 € with the best choice (−573,89 € staying joint).
  Provision: CIRS art. 70 n.º 4 a). Lean: `me_joint_notch`. Status: proved.

### F12 Low-pay marginal rate at least the top wage rate (NOVEL N3)
* kind: loophole-new / design (not claimed new)
* 56,0 % (12 180-13 863 €) and 48,6 % (to 14 857 €) for a single employee vs 55,95 % at 10 AW. Provision: CIRS
  art. 70 n.º 2 b)-c). Lean: `me_segment_b_step`, `me_segment_c_step`. Status: proved.

### F13 (lead, 2026 text) Art. 68 n.º 2 still says "quando superior a 8059 €" under the 2026 table starting at 8 342 €
* kind: statute-fault (lead; outside the 2025 model)
* The AT's consolidated CIRS (and Global law's copy) shows n.º 2 "(Redação da Lei n.º 45-A/2024)" with 8 059 €
  next to a table whose first limit is 8 342 €. Not verified against the 2026 amending law (Lei 73-A/2025 PDF not
  retrieved). The same pages attribute the 2026 art. 68 table to "Decreto-Lei n.º 212/2026", which is odd for tax
  rates (parliament's reserve, CRP art. 165 n.º 1 i)); not checked.

### Novelty check (family agent, 2026-11-19, 2 web searches from the family reserve)
- F11 (joint return loses the mínimo de existência at 32 186 €): query "mínimo de existência tributação conjunta casal
  perde IRS 2025". Top results (occ.pt notes on the mínimo de existência, simula.pt joint/separate simulator,
  Montepio, CGD, Santander guides, AT newsletter 39) describe the mínimo per spouse and advise simulating both options;
  none states that a joint return loses it at a household threshold. Not found in 17 results searched.
- F3 (art. 68 n.º 2 column-B rounding makes the tax fall with income): query "artigo 68 CIRS taxa média arredondada
  três casas decimais imposto diminui". Results were the AT's own art. 68 pages and rate leaflets (2016-2026) and an AT
  statistical note; none mentions the non-monotonicity. Not found in 18 results searched.
