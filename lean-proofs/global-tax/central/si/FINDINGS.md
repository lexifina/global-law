# Slovenia (SI), tax year 2025: findings

Model: `lean/SiTax` (exe `sitax`), ZDoh-2 as in force on 1.1.2025 (čl. 2; PISRS ZAKO4697 NPB 34), FURS Lestvica 2025
(Pravilnik Ur. l. RS 108/24), contributions per FURS brošura, child benefit per Sklep Ur. l. RS 9/25 (ZUPJS čl. 22,
ZSDP-1 čl. 72, 77). Amounts in euros; Lean statements in cents. Sources under `refs/`.
"Not found in N sources" counts 15 sources: ZDoh-2 NPB 34, ZUPJS NPB 21, ZSDP-1 NPB 7/8, Pravilnik PRAV12104, FURS
Lestvica 2024/2025/2026, FURS "Odmera dohodnine za leto 2025", FURS brošura prispevki, gov.si otroški dodatek page,
Sklep 9/25, and 3 web searches (OECD Tax Policy Review Slovenia 2018 summary; advisory pages on normiranci; one
search on normiranci and child benefit).

### F1 OECD Taxing Wages 2025: 56 of 56 lines exact
- kind: model-fix (validation record)
- households: the eight TW types at AW 30.135,42 €
- result: `oecd/check.py SI` and `harness/oecd_check20.py SI`: 56/56 within 1 € (the ±1 € residues come from the
  household gross being whole euros); take-home pay 8/8.
- conventions matched: employee contributions 22,10 % + long-term care 1 % July-December (22,60 % on the year); OZP
  2 × 35,00 + 10 × 37,17 = 441,70 € for every adult incl. a non-working spouse (EECSSC; the OECD lowers BTA by 441,70 in
  M100_0 so the spouse's OZP is not deducted from the earner's base, as the model does); child benefit at the amounts
  from 1.3.2025 for all 12 months on the same year's net income; child allowances with the higher earner.
- Lean: `Basic.lean` (`compute`); status: done.

### F2 FURS annual table: the rows do not chain to the cent at 78.016,32 €
- kind: gov-error (classification: convention; harmless)
- FURS Lestvica 2025: "54.178,00 – 78.016,32: 15.061,48 + 39 %", "nad 78.016,32: 24.358,43 + 50 %". Row 4 at its end
  gives 24.358,4248 (24.358,42); row 5 starts at 24.358,43 = the exact cumulative tax 24.358,4288 rounded. By the
  table literally, tax jumps 0,5 cent at 78.016,32 €. All four fixed amounts equal the schedule at the thresholds.
- Lean: `furs_fixed_amounts`, `furs_rates`, `furs_row4_chain`, `furs_exact_at_top`, `monthly_fixed_amounts`; status: proved.

### F3 The čl. 111(3) formula is negative at its own upper limit
- kind: statute-fault (cents)
- "zmanjšanje = 18.761,40 eura – 1,17259 x skupni dohodek" up to 16.000 €: −0,04 € at 16.000 € (zero at
  15.999,97 €); 2025: 19.736,99 − 1,17259 × 16.832 = −0,04 €. Read literally, total income in (16.831,97; 16.832,00]
  gets up to 4 cents less than 5.260 €. The model floors the allowance at 5.260 € (the evident intent).
- Lean: `statute_formula_negative`, `general_above`; status: proved.

### F4 How the 2024-2025 levies are booked
- kind: model-fix (reading, documented)
- OZP (flat 35,00 → 37,17 €/month, ZZVZZ čl. 48) and long-term care (1 % from 1.7.2025, ZDOsk-1) are employee SSC
  in the OECD table and deducted in the tax base (ZDoh-2 čl. 41(1) "obvezne prispevke"); the model does the same.
  Pensioners pay OZP and 1 % LTC; health 5,96 % is paid by ZPIZ (FURS brošura 16.2). status: modelled.

### F5 FURS guide prints the sixth-child step as 2.060,97 € (should be 2.060,87 €)
- kind: gov-error (error in guidance; the Lestvica and the Pravilnik are right)
- FURS "Odmera dohodnine za leto 2025" 8.4 (refs/fu_Odmera_dohodnine_2025.txt): "za šestega in vse nadaljnje
  vzdrževane otroke za 2.060,97 EUR". 1.959 € × 1,052 = 2.060,868 → 2.060,87, as FURS's Lestvica 2025 prints
  (mesečno 171,74). A family with six or more children reading the guide expects 0,10 € more per child.
- Lean: `furs_guide_sixth_child`, `indexation_2025`, `monthly_child_amounts`; status: proved.
- draft note to FURS (not sent): "V dokumentu Odmera dohodnine za leto 2025, točka 8.4, je povečanje posebne olajšave
  za šestega in nadaljnje otroke navedeno kot 2.060,97 EUR; Obvestilo o lestvici 2025 in Pravilnik (Ur. l. RS
  108/24) določata 2.060,87 EUR (1.959 × 1,052)."

### F6 The statute prints amounts 21,5 % out of date (two vintages in one indexation list)
- kind: statute-fault (stale amounts)
- ZDoh-2 čl. 112(1) "14.971 eurov" (100 % disabled) and čl. 117(1) "ne več kot 2.390 eurov" are the 2006 original
  amounts (refs/zdoh2_osnovni.txt), unchanged in NPB 33/34. Operative: 18.188,61 € and 2.903,66 € (2024),
  19.134,42 € and 3.054,65 € (2025): both exactly 21,49 % above the statute (indexation compounded since 2007).
  The other amounts in the čl. 118(1) list (čl. 111, 112(8), 113, 114) were re-enacted by ZDoh-2AA and equal the
  2024 operative amounts. The law text mixes 2006 and 2023 bases; the operative amount is only in the yearly
  Pravilnik. čl. 122's brackets (8.500 …) are 8,4 % below 2025 (× 1,03 × 1,052).
- Lean: `indexation_2025`; status: documented.

### F7 Child-benefit class notches: up to 941,71 € lost for one more euro of wages
- kind: loophole-known (OECD Tax Policy Review Slovenia 2018: secondary earners face very high marginal rates
  "partly as a result of the decline in child benefits"; nominal classes of ZUPJS čl. 22)
- households: single parent, children 11 and 6, 19.519 € vs 19.520 €: −941,71 € (class 2 → 3); one-earner married
  couple, two children, 26.734 € vs 26.735 €: −724,27 €. Generic METR scanner: 2-8 bands above 100 % per family type,
  peak 1.579 %. Bunching two years across a notch gains up to 1.524 € (timing.py); as the law tests the previous
  calendar year (ZUPJS čl. 15(2)), one year's income sets the class for the next 12 months.
- Lean: `F7_single_notch`, `F7_couple_notch`, `cb_antitone_primary`; status: proved.

### F8 The cliff above class 8: 929,60 € lost at 77.808 €
- kind: loophole-known (no benefit above 1.293,36 € per person per month)
- household: single parent of two, 77.807 € vs 77.808 €. Lean: `F8_cliff`, `cb_cliff`; status: proved.

### F9 Dependent spouse: the spouse's first euro of wages costs the earner up to 1.420 €
- kind: loophole-new (participation notch; not found quantified in 15 sources)
- provisions: ZDoh-2 čl. 114(1) 3. (2.838,30 €), čl. 115(1): the spouse "ni zaposlen ter ne opravlja dejavnosti" and
  has own income below 2.838,30 €.
- households (married, no children, spouse 0 € vs 1 € wages): earner at 15.000 € loses 455 €, 30.135 € 738 €,
  60.000 € 937 €, 150.000 € 1.420 € (S4). A spouse earning 2.838 € raises family net by only 777-1.742 € (39-73 % on
  the first 2.838 €). Found blind by metr.py (second_earner_2, 0-60 €: 1.193 %). Also a cliff for non-wage own income
  at 2.838,30 €.
- Lean: `F9_spouse_notch`; status: proved.

### F10 Not claiming part of the child allowance can raise family income by up to 878 €
- kind: loophole-new (not found in 15 sources; the Czech analogue is CZ F5)
- the child-benefit test uses income after tax (PRAV12104 čl. 2; ZUPJS čl. 15(3): from the assessment); claiming the
  dependants' allowance (it must be claimed, čl. 114) lowers tax, raises net income and can lift the family a class.
- households: single parent of two at 19.600 €: forgoing 400 € of the 5.923,82 € allowance costs 64 € of tax, keeps
  class 2: +878,36 €/year. Scan S1 (2.163 households, 8.000-80.000 €): 144 (6,7 %) gain; largest 600-880 €.
- caveat: ZUPJS čl. 12(8) disregards persons who unjustifiably fail to claim incomes; it says nothing of tax reliefs.
- Lean: `F10_forgo`; status: proved.

### F11 Flat-rate s.p. families get the maximum child benefit on high real income
- kind: loophole-new (not found in 15 sources; follows from ZUPJS čl. 12(7) and PRAV12104 čl. 10(2))
- for the test, flat-rate s.p. income is "dobiček zmanjšan za obračunano dohodnino", the profit being 20 % of revenue.
- household: married, children 11 and 6, a full-time s.p. with 60.000 € revenue and no real expenses, spouse without
  income: the test sees 8.716,60 €/year (class 1, 301,99 €/month = 3.623,88 €/year) while the family keeps
  49.957,19 € after tax and contributions. An employee couple at 48.000 € gross (32.862 € net) is in class 5; the
  same 60.000 € as actual-expense s.p. profit gives class 5 (1.571 €).
- Lean: `F11_norm_child_benefit`; status: proved.

### F12 The additional general allowance's taper: METR 53,7 % on wages of 13.100-16.832 €
- kind: loophole-known (OECD Tax Policy Review Slovenia 2018)
- 100 € more gross at 15.000 € leaves 46,26 € (53,7 %), at 19.000 € 65,02 € (35,0 %), at 11.000 € 77,40 € (22,6 %).
  The 2025 minimum wage (about 15.300 €/year) lies in the band.
- Lean: `F12_taper_band`, `general_step` (kernel `Taper.amount_step`); status: proved.

### F13 Who claims the children: up to 1.422 €
- kind: loophole-known (ZDoh-2 čl. 114(10)-(11); FURS guide 8.4)
- married, 116.000 € and 29.000 €, two children: the lower earner claiming costs 1.421,72 €; no agreement (half each,
  čl. 114(11)) 710,86 €. The model takes the cheapest split by default (as the OECD does).
- Lean: `F13_claimant`; status: proved.

### F14 Flat-rate s.p. income does not withdraw the low-income allowance
- kind: loophole-new (statutory, by design of čl. 111(3); not found discussed in 15 sources)
- čl. 111(3) excludes flat-rate s.p. income from the total income that withdraws the additional allowance. A side s.p.
  with 40.000 € revenue (23.000 € deemed profit, 4.600 € final tax) and a 12.000 € wage keeps the full 10.926 €
  allowance; with 8.000 € of actual-expense s.p. profit instead it falls to 5.260 € and the wage pays 772 €.
- status: modelled (`skupniDohodek`), checked on the exe.

### F15 Flat-rate expenses vs employment: 16 % vs 48 % at 60.000 €; side s.p. 13 % vs 52 % at the margin
- kind: loophole-known (normiranci; sibiz.eu, beancount.io, total-slovenia-news; ZDoh-2AB tightened it for 2025)
- same 60.000 €: employee (employer cost 60.000 €) keeps 30.942 €, actual-expense s.p. 28.698 €, full-time flat-rate
  s.p. without real expenses 50.399 €. Next to a 1 AW job, 12.500-30.000 € of side revenue costs 13-14 % (lump-sum
  contributions 1.224,57 € + 20 % of deemed profit) instead of 51-53 % as wages (S3). status: modelled.

### F16 Owner-manager: salary to about 12.900 € plus dividends
- kind: loophole-known; owner.py (CIT 22 %, ZORZFS čl. 64 per FURS; employer 16,6 %): best salary about 12.922 € at
  every profit level, the rest as dividends at 25 %; gain over all-salary 1.611 € at 1 AW, 21.823 € at 5 AW, 59.959 €
  at 10 AW. status: recreated blind.

### F17 Income type: capital, rent and pensions vs wages
- kind: loophole-known (design): at 5 AW interest/dividends/gains pay 24,7-24,9 % of income less than wages, rent
  27,2 % less (25 % on 90 %), pensions up to 29,9 % less (no SSC, 13,5 % credit); gains tax-free after 15 years (čl.
  96(1)), 20 %/15 % after 5/10 (čl. 132(2)); 1.000 € deposit interest per person exempt (čl. 133). An s.p. with small
  profit pays contributions on the minimum base (60 % PP): −67 % vs wages at 0,25 AW. status: recreated blind.

### F18 Scanner artefacts (not findings)
- METR bands of 61,7-63,3 % above 3,6 AW and the 51 one-euro "rounding-scale falls" in edges.py come from the exe
  reporting whole euros (60 € steps); the cent-level model has no such steps (`sched_no_jump`).
