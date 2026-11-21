# Croatia (Zagreb) 2025: findings

Model: `lean/HrTax` (exe `hrtax`). Statute copies in `refs/` (Narodne novine texts fetched 2026-11-19). Amounts in euros
for 2025 unless stated. ZPD = Zakon o porezu na dohodak (NN 115/16 … 152/24); ZD = Zakon o doprinosima (NN 84/08 …
152/24); PU = Porezna uprava.

### F1 Eurostat's 2025 Croatian lines use a 22,4 % lower rate, not any city's 2025 rate
- kind: model-fix (referee convention), households: all 13 Eurostat earn_nt_net types.
- amounts: with Zagreb's 23 % (NN 28/2025) the model's income tax is 2,7 % above Eurostat in 12 of 13 types
  (S100 2.873 vs 2.797,67; S167 5.907 vs 5.752,69); with `"lowerRate": 2240` all 13 income-tax lines agree to the cent
  (`tools/eurostat_alt.py`, max |diff| 0,47 €). 22,4 % is the 2024 ceiling for a city under 30.000 inhabitants (ZPD
  čl. 19.a st. 2 t. 2 as in NN 114/23), which NN 152/24 čl. 4 lowered to 21 % for 2025; no unit charged 22,4 % in 2025
  (PU table "stanje 1. ožujka 2025.", `refs/pu_stope_2025.tsv`: highest lower rates 23 % Zagreb, 22 % Rijeka, Gospić,
  Pazin, 21,6 % Sisak).
- who is right: for a Zagreb resident the statute (23 %); Eurostat's rate matches no 2025 decision. Sanity referee only
  (CONTRACT38). Status: explained.

### F2 Eurostat's child benefit: lone-parent supplement and last year's income
- kind: model-fix (referee convention), households: SP67, M100_67.
- SP67: Eurostat 1.096,54 = 39,73 € × 1,15 × 2 × 12: it gives the +15 % supplement "if one parent is missing" (EUROMOD
  CR Y16 §2.6.8) to every lone parent; the model does not (reading; statute text of Zakon o doplatku za djecu not read).
- M100_67: Eurostat 741,62 (bracket 5) although the 2025 net income per member (637,9 €/month in the model, 654,6 € at
  Eurostat's own tax) exceeds 618,02 €: the income test uses the previous year's income (EUROMOD Y16 §2.6.8, deflated by
  wage growth); the model uses the year's own income (contract convention). Status: explained.

### F3 Porezna uprava's worked examples for young workers ("Primjeri izračuna za mlade") contain three errors
- kind: gov-error. Source: `https://kalkulator.porezna-uprava.hr/pdf/Primjeri_izracuna_za_mlade.pdf` (linked from the
  official calculator, `refs/kalk/mladi.txt`), Grad Samobor (18 %/27 %), 2024 and 2025 tables.
- (a) The lowest column ignores the 2024 pension-base reduction (ZD čl. 21.a, NN 114/23 čl. 4, in force 2024-01-01):
  pay 8.400 € (2024) and 9.000 € (2025) is 700 € and 750 € a month, where pillar-I contributions fall from 15 % of pay
  to 15 % of (pay − 300) and (pay − 275); the examples charge the full 20 %. 2025, age 26-30, 9.000 €: contributions
  1.305 € (not 1.680/1.800), dohodak 7.695 €, base 495 €, tax 89,10 €, relief 50 %, **tax due 44,55 €, not 0**
  (`hrtax`: 45). 2024, 8.400 €: contributions 1.140 €, base 540 €, tax due 48,60 €, not 0 (hand computation, 2024 law).
- (b) 2025, 9.000 € column: "Ukupni doprinosi 20 %" 1.680,00 (= 20 % of 8.400, the 2024 column) next to "Dohodak
  7.200,00" (= 9.000 − 1.800): the column does not add up.
- (c) 2025, age 26-30, 24.000 €: "Umanjenje 50 %" 1.008,00 of a tax of 2.160,00: 50 % is **1.080,00**; the row and
  "Neto ... nakon godišnjeg obračuna 18.192,00" (correct 18.120,00) understate the tax by 72 €. Also "Neto radnika prije
  godišnjeg obračuna" 17.040,60 and 22.288,60 (19.200 − 2.160 = 17.040,00; 25.600 − 3.312 = 22.288,00).
- model agreement on the 8 tax amounts of the 2025 tables: 6 exact; the 2 others are (a) and (c).
- Status: confirmed by arithmetic and statute.

### F4 The official calculator's rate list disagrees with the official rate table for Novigrad and Knin
- kind: gov-error (Novigrad) / lead (Knin). Calculator parameters `https://kalkulator.porezna-uprava.hr/json/podaci.json`
  (`refs/kalk/podaci.json`, year 2025, 556 units) vs PU "Tablica poreznih stopa ... 2025. (stanje 1. ožujka 2025.)": 554
  units agree.
- Novigrad: the calculator lists "Novigrad (20,00 %, 31,00 %)" twice (codes 298, 299); the općina Novigrad (Zadarska
  županija) has 20 %/30 % (decision NN 157/23); 31 % belongs to Grad Novigrad – Cittanova (NN 34/2025-402).
- Knin: calculator 21 %/32 % = Grad Knin's decision NN 154/2024-2559 (adopted 17 Dec 2024, in force 1 Jan 2025, citing
  the law without NN 152/24); the PU table says 21 %/30 % from 1 March 2025 citing "152/24". 32 % exceeds the 2025 ceiling
  for a city that is neither a large city nor a county seat (ZPD čl. 19.a st. 2 t. 2: 25-31 %); NN 152/24 čl. 14 st. 1-2
  obliged Knin to adopt a new decision by 28 Feb 2025. No Knin decision appears in NN issues 1-40 of 2025
  (`tools/scan_knin.sh`, `runs/scan_knin.txt`). So two Porezna uprava publications give a Knin resident with a base over
  60.000 € different higher rates (30 % vs 32 %), and the statute does not say which applies: čl. 14 st. 4 keeps the old
  decision only for advances "do donošenja odluke", and čl. 19.a st. 5's default 20 %/30 % is for a unit that adopts no
  decision, not for one whose decision is out of range (statute gap). Effect: 2 % of the base above 60.000 €.
- classification: Novigrad: error (calculator label and rate); Knin: statute gap + inconsistent official publications.
- draft issue text (calculator): "U podaci.json (2025) šifra 298 'Novigrad (20,00%, 31,00%)' odnosi se na Općinu
  Novigrad (Zadarska županija) čije su stope 20 %/30 % (NN 157/23); 31 % je viša stopa Grada Novigrada – Cittanova
  (NN 34/2025). Za Grad Knin kalkulator primjenjuje 32 % (NN 154/24), a Tablica poreznih stopa 30 %; 32 % prelazi gornju
  granicu iz čl. 19.a st. 2 t. 2 ZPD-a." Status: Novigrad confirmed; Knin open (which rate the annual assessment used).

### F5 Pensions: the 50 % reduction is for residents of group-I assisted areas only; EUROMOD gives it to all pensioners
- kind: statute-fault (ambiguous drafting) / referee reading.
- ZPD čl. 24 st. 5 (withholding): "umanjuje se za 50% umirovljenicima po osnovi ostvarenog dohotka od mirovine ili
  poreznim obveznicima koji imaju prebivalište i borave na području ... I. skupinu ..." can be read as "all pensioners, or
  residents of those areas". The annual rule (čl. 46 st. 1 as rewritten by NN 106/18 čl. 14) and the Pravilnik o porezu
  na dohodak čl. 57 st. 1 and čl. 84 st. 5 (NN 10/17) attach the residence condition to pensions as well.
- EUROMOD Country Report Croatia 2022-2025 (Y16, §2.8.1.7) applies the 50 % credit to every pensioner.
- Status: confirmed reading conflict.

### F6 Child coefficients: the rule for the 10th and later children was not re-based in the 2024 reform
- kind: statute-fault (minor). ZPD čl. 14 st. 3 r.br. 2-10 shifted one rank by NN 114/23 čl. 4 while r.br. 11 kept
  "1,1 … više". Model: 10th child 6,0.

### F7 The young-worker relief was missing from the annual tax-due provision from 2020 to 2024
- kind: statute-fault (dangling cross-reference, fixed in 2025): čl. 46 old st. 5 "sukladno stavku 1." (NN 121/19 čl. 13)
  → "sukladno stavcima 1. do 3." (NN 152/24 čl. 7).

### F8 Zagreb 2025: January and February withheld at 23,6 %/35,4 %, refunded in the annual assessment
- kind: model-fix (withholding vs annual; timing, not a loss). NN 152/24 čl. 14 st. 3-4: Zagreb's new decision (23 %/33 %,
  NN 28/2025) applies to advances from 1 March and to the annual assessment for the whole of 2025; January and February
  advances used the 2024 decision (23,6 %/35,4 %).
- amounts (single, even pay): 12,45 € at 24.612 €, 31,20 € at 48.000 €, 98,40 € at 96.000 € withheld too much and
  refunded after the year. Lean: `Walls.zagreb_overwithholding` (`whYearZagreb`). Status: explained.

### F9 The official calculator cannot read amounts of a million euros or more
- kind: gov-error (minor). `refs/kalk/app_controller_home-ctrl.js`, `replaceChar`: `val.replace(".", "").replace(",", ".")`
  removes only the first thousands separator, while the input pattern accepts "1.234.567,89"; such an input becomes
  "1234.567.89" and every result is NaN. Affects gross pay of 1.000.000,00 € or more only. Draft fix:
  `val.replace(/\./g, "").replace(",", ".")`.
- the calculator's formula otherwise agrees with the model on 4.176 employee cases (Zagreb and Samobor, ages 24/28/40,
  0-3 children, pay 0-160.000 €), all within 1 € (`tools/pu_calc.py`, `results/pu_calc_*.json`).

### F10 Doplatak za djecu: five all-or-nothing brackets; one euro more costs a family up to 742 €
- kind: loophole-new (METR > 100 % bands; incentive to stay below a bracket), found blind by the METR scanner.
- statute: Zakon o doplatku za djecu čl. 16 t. 1 (limit 140 % of the proračunska osnovica = 618,02 € per member a
  month) and čl. 17 st. 1-5 (14 / 12,5 / 11 / 9 / 7 % per child by bracket), NN 156/2023 čl. 7-8 (from 2024: three
  brackets became five, so two more notches); proračunska osnovica 441,44 € (NN 149/24 čl. 39 st. 2).
- households (Zagreb, children 6 and 11): one earner + spouse without income: pay 40.899 € → doplatak 741,60 €;
  40.900 € → 0; net income falls by 741,01 € (`Walls.dzd_cliff`), and the family stays worse off until pay rises by about
  1.240 €. Lone parent: steps of 158,88 € at 7.272 €, 211,92 € at 11.539 € and at 19.885 €, 741,60 € at 30.205 €
  (`Walls.dzd_steps`). The METR scanner finds 5 bands above 100 % for each family type with children
  (`results/search/metr.md`; its "causes" column lists detail lines that move with pay; the cause is the benefit).
- the test uses the previous year's income (F2), so the cliff is a timing choice: deferring a bonus into the next year
  keeps the bracket. A glide (benefit reduced by a share of the excess) would remove the notches.
- known? not found in 8 sources searched (ZDD amendment NN 156/23; EUROMOD Y16 §2.6.8 describes the brackets, not the
  notches; PU pages; RRiF, TEB, Informator articles; one web search on paušal/IJF). Status: model-proved.

### F11 A dependent spouse: one euro of the spouse's own income costs the earner 828 €
- kind: loophole-known (the statute's own all-or-nothing limit), found blind (METR scanner: 828 at 3.600).
- ZPD čl. 14 st. 3 r.br. 1 (0,5 × 600 € a month for a dependent spouse) and čl. 17 st. 1 (receipts at most 6 × 600 € =
  3.600 € a year; PU "Osobni odbitak"). Earner 30.000 €, spouse pension 3.600 € vs 3.601 €: tax 3.036 € vs 3.864 €
  (`Walls.dependant_cliff`). Recreated as L05.

### F12 Paušal classes: one cent over a class limit costs 72-192,60 € of tax
- kind: loophole-known (notch; the Government's bill of September 2026 redraws the top two classes because of the
  paušal–employment gap, `refs/lit_informator_izmjene.txt`). Pravilnik o paušalnom oporezivanju čl. 3 st. 1 (NN 1/24,
  16/25), ZPD čl. 82 st. 5 (12 %): receipts 11.300,00 → 11.300,01 € raise the tax from 203,40 € to 275,40 €; the jumps at
  the six limits are 72,00 / 82,80 / 192,60 / 169,20 / 180,00 / 180,00 € (`Walls.pausal_notches`). Receipts count when
  collected, so the limits can be managed by the timing of collections.

### F13 Uneven monthly pay escapes contributions: the pension-base reduction and the monthly cap are not equalised over the year
- kind: loophole-new.
- statute: ZD čl. 21.a st. 1-2 (monthly pillar-I base reduced by 300 € up to 700 € of monthly pay, tapering to 0 at
  1.300 €), st. 7 (pension rights computed on the unreduced base), čl. 204 st. 1 (pension contributions only up to the
  monthly maximum, 10.788 € in 2025). Neither ZD nor the Pravilnik o doprinosima (NN 143/23: instalments within a month,
  several employers) looks at the year; only čl. 206 caps the year from above.
- household: 24.000 € a year paid as 12 × 2.000 € (employee contributions 4.800,00 €) or as 11 × 970 € + 13.330 € in
  December (4.019,35 €): 780,65 € less, of which 272,25 € is the reduction harvested in eleven months (pension rights
  unchanged, st. 7) and 508,40 € the December pay above the monthly cap (rights capped too); after the higher income tax
  (23 % of 780,65 €) the employee keeps about 601 € more (`Walls.pay_timing`, `Walls.pay_timing_parts`). 970 € is used as
  the low month (the 2025 minimum wage, Uredba o visini minimalne plaće za 2025., NN 124/2024-2072; the model does not check labour law). The timing scanner finds the same
  non-convexity across years (bunching gain up to 418 € for a single person).
- known? not found in 8 sources searched (ZD and amendments NN 114/23, 152/24; Pravilnik o doprinosima NN 143/23,
  14/24, 16/25; PU "Radnik"; EUROMOD Y16; RRiF, TEB, Informator articles). Draft fix: settle the čl. 21.a reduction on
  the year's pay in the annual assessment, as čl. 206 does for the maximum. Status: model-proved.

### F14 Residence: the same pay costs up to 8 points of tax more in Zagreb than in a 15 % municipality
- kind: loophole-known (the design of the 2024 reform; PU "Porezna konkurentnost" pages). ZPD čl. 19.a; at Eurostat's AW
  24.612 € the tax is 2.872,61 € in Zagreb and 1.873,44 € at 15 % (`Walls.residence_gain`); 1.984 € at 40.000 € (L07).

### F15 Young workers: the relief halves in the year of the 26th birthday and ends in the year of the 31st
- kind: loophole-known (timing). ZPD čl. 46 st. 2 and st. 8 (old st. 4: "za cijelo porezno razdoblje u kojem obveznik
  navršava određenu godinu života"). Single, 30.000 €: tax 0 at 25, 1.932 € at 26-30, 3.864 € at 31
  (`Walls.young_steps`); a 10.000 € bonus paid in the year of the 30th rather than the 31st birthday saves 920 € (L06).

### F16 Owner-manager: the generic scan's company side misses the Croatian rules that decide it
- kind: model-fix (kernel `company.json` HR is the OECD placeholder: CIT 18 %, employer health with a ceiling, no
  director's minimum). Statute: CIT 10 % for revenue up to 1.000.000 € (Zakon o porezu na dobit čl. 28 st. 1 t. 1;
  NN 138/20 čl. 4, NN 114/23 čl. 8); employer health 16,5 % without ceiling (ZD čl. 204 caps pension only); a director
  employed full time has a minimum base of 0,65 × average wage = 1.168,70 €/month (ZD čl. 21 st. 2, NN 115/16 čl. 5); a
  director without employment and not insured otherwise pays pension and health on 1.798 €/month himself (ZD čl. 90-92;
  7.875,24 € a year), so "all dividends" is not free.
- `tools/owner_hr.py` (`results/owner_hr.json`), single owner, Zagreb: profit 60.000 €: all salary 26.618 €, minimum
  director's salary + dividends 15.034 €, no salary (director insured) 20.355 €, obrt with books 16.086 €, paušal obrt
  4.230 € (if profit = receipts); profit 100.000 €: 45.615 / 23.354 / 28.675 / 28.054 €. Sent to `~/cmp20/kernel/INBOX.md`.
