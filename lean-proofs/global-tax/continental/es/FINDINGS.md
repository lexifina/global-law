# Spain (state + Comunidad de Madrid), IRPF ejercicio 2025 in Lean: findings

Model: `lean/ESTax` (exe `estax`), built on `~/cmp20/kernel` (TaxKernel 1.0). Statute texts in `law/` (BOE consolidated
via Global law, in force 31-12-2025). Theorems in `lean/ESTax/Theorems.lean` (31 theorems, no `sorry`; `#print axioms`
for the household theorems: `propext` only; for the general ones `propext, Classical.choice, Quot.sound`).
Scripts: `harness/scan_metr.py`, `harness/scan_withholding.py`, `harness/recreate.py`; raw output in `runs/`.
Money in euros (cents in Lean). "Tax" = cuota líquida estatal + autonómica after all deductions, refundable
deductions (arts. 81, 81 bis) negative. "Burden" = tax + employee social contributions.

## Validation summary

* **OECD Taxing Wages 2025** (family harness, 8 household types, OECD wages rounded to the euro): all 32 state-side
  lines (CGTC taxable income, CGITFP state income tax after credits incl. the refundable art. 81 bis, EECSSC, CTGG)
  agree within 0,76 EUR; the differences come only from the euro-rounded wages (e.g. S100 CGITFP 2.839,57 vs
  2.839,63). The regional line SLT differs on all 8 (F1). Joint taxation chosen as the OECD does: M100_0 and SP67
  joint (3.400 / 2.150 EUR reductions), two-earner couples separate.
* **AEAT withholding algorithm** (`refs/ALGORITMO_2026.pdf`, the AEAT's specification for payroll software): the
  Lean `withholding` follows RIRPF arts. 81-86 and the algorithm's general procedure; compared clause by clause the
  algorithm agrees with the regulation except where the regulation leaves a choice (F11).
* **AEAT IRPF 2025 novelties guide** (sede.agenciatributaria.gob.es, manual práctico 2025, "Deducciones de la cuota
  líquida total"): confirms the DA 61.ª parameters (18.276 EUR, 6.500 EUR, from 1-1-2025) and that 16.576 EUR is the
  2025 SMI. No worked example there or in the AEAT bulletin on Ley 5/2025 (`refs/bolinform.txt`).
* No official calculator usable without login/JavaScript was found; no maintained open model of Spain (OpenFisca,
  PolicyEngine) exists.

### F1 The OECD's regional income tax for Spain is not Madrid's
- kind: gov-error; classification: **convention** (not an error)
- households: all 8 OECD types. SLT Lean (Madrid) vs OECD: S67 1.176,67 vs 1.331,49; S100 2.456,36 vs 2.736,46;
  S167 5.703,41 vs 6.289,48; SP67 433,22 vs 610,96; M100_0 1.555,90 vs 1.769,58; M100_100 4.447,46 vs 5.006,17;
  M100_67 3.167,77 vs 3.601,20; M100_67nc 3.633,03 vs 4.067,95.
- explanation: the OECD's Spain chapter (Taxing Wages 2026; the oecd.org page refused automated fetches (403); the
  sentence as returned by the search engine from that page): the regional schedule "is derived from a weighted
  combination of the schedules approved by the Autonomous Communities with the highest representation". Its numbers
  imply a first regional rate of 9,152 % applied to the state mínimos (BTC − state 9,5 % on the mínimo: 1.035,19 −
  527,25 = 507,94 = 9,152 % x 5.550; SP67 974,69 = 9,152 % x 10.650). Madrid has 8,5 % (DLeg 1/2010 art. 1) and higher
  regional mínimos (5.956,65, art. 2), so Madrid's tax is 155-586 EUR lower on these households. S100 line by line
  (base 28.560,84): OECD regional 3.244,40 − 507,94 = 2.736,46; Madrid 2.962,68 − 506,32 = 2.456,36.
  The weights are not published in the material reachable here, so no "oecd" region parameter was added.
- provisions: LIRPF art. 74; DLeg 1/2010 arts. 1-2 bis. Lean: `escalaMadrid`, `madrid_cuotas`.
- status: explained (convention).

### F2 Withholding still starts at 15.876 EUR: a 2025 SMI earner is withheld 300,03 EUR and owes nothing
- kind: statute-fault (amount not updated when a related amount changed) + gov-error (AEAT text out of date)
- household: single, 40, one payer, contrato indefinido, wages 16.576 EUR (the 2025 SMI per the AEAT 2025 guide).
- amounts: liability 0 (cuota íntegra 169,78 + 117,34 = 287,12, absorbed by the DA 61.ª deduction of 340 capped at the
  cuota); withholding (RIRPF arts. 83-86 / AEAT algorithm): tipo 1,81 %, 300,03 EUR. Band where tax = 0 but
  withholding > 0: wages 15.890-16.650 EUR (up to 331,34). These workers are not obliged to file (LIRPF art. 96.2 a:
  one payer, up to 22.000), so the excess comes back only if they file voluntarily.
- why: RIRPF art. 81.1 limits (15.876 / 16.342 / 16.867 ...) were last set by RD 142/2024 for the 2024 SMI (Global
  law: art. 81 unchanged from 2024-02-08 to the record's end 2026-10-28). The AEAT's own algorithm document says of
  RD 142/2024: "De esta forma, no quedará sujeta a retención la percepción de rendimientos del trabajo por importe
  igual o inferior al salario mínimo interprofesional": false for 2025 (SMI 16.576), and the 2026 algorithm still
  uses 15.876. The DA 61.ª deduction (Ley 5/2025 disp. final 3.ª, inside a motor-insurance law, published July 2025
  with effect from 1 January 2025) was never reflected in the withholding procedure.
- provisions: RIRPF arts. 81.1, 85.3, 86.1; LIRPF art. 96.2, DA 61.ª. Lean: `smi_owes_nothing`, `smi_withheld`.
- status: certain (kernel-checked). The withholding gap and the AEAT's outdated claim were not found in the sources
  read (AEAT 2025 guide, AEAT bulletin on Ley 5/2025, AEAT algorithm 2026, 5 web searches).
- draft issue (not filed), to the Dirección General de Tributos: "RIRPF art. 81.1 still fixes the withholding
  exemption at 15.876 EUR (situación 3) although the 2025 SMI is 16.576 EUR and LIRPF DA 61.ª leaves an SMI earner
  with no liability. A single worker on 16.576 EUR is withheld 300,03 EUR (AEAT algorithm) for a liability of 0 and is
  not obliged to file. The AEAT algorithm document still states that RD 142/2024 ensures SMI earners are not
  withheld. Proposal: update art. 81.1 and the art. 85.3 limit whenever the SMI changes (or index them to it), and
  take the DA 61.ª deduction into the withholding procedure."

### F3 Under-withholding band: a single worker on 18.100-21.740 EUR is withheld less than the tax and need not file
- kind: loophole-new (passive, legal)
- household: single, one payer, wages 18.100-21.740 EUR (Madrid).
- amounts: withholding minus liability negative on 365 steps of 10 EUR; worst −137,67 at 21.100; −110,98 at 20.000
  (withholding 1.772,00 vs liability 1.882,98). LIRPF art. 96.2 a) exempts one-payer workers up to 22.000 EUR from
  filing, so the difference is never assessed.
- why: RIRPF art. 85.3 caps the withholding cuota at 43 % of pay above the art. 81 limit for pay up to 35.200 EUR;
  the liability has no such cap.
- provisions: RIRPF arts. 81, 85.3; LIRPF arts. 20, 96.2. Lean: `withholding`; `runs/withholding_scan.json`.
- status: computed (model); not found in the sources read. For a Madrid resident it is the exception: above
  22.000 EUR withholding exceeds the Madrid liability (F11).

### F4 One cent of interest above 6.500 EUR costs a 14.000 EUR worker more than 1.650 EUR
- kind: loophole-new (cliff; METR far above 100 %)
- households: single, wages 14.000, interest 6.500 vs 6.501: burden +1.657,50 EUR for +1 EUR; wages 17.000: +1.288,17.
- why: LIRPF art. 20 ("siempre que no tengan rentas ... distintas de las del trabajo superiores a 6.500 euros") and
  DA 61.ª (same 6.500) are all-or-nothing: crossing 6.500 of other income removes the whole reducción (up to 7.302
  of base) and the 340 deduction.
- planning: keep other income at or below 6.500 (defer a gain; hold accumulating rather than distributing funds;
  hold savings in the name of a spouse with no such reducción at stake: individual taxation).
- Lean: `cliff_6500` (`hhTotal (single 1400000 650001) - hhTotal (single 1400000 650000) > 165000`, cents).
- status: certain. The 6.500 condition is well known; the size of the jump was not found quantified in the sources
  read.

### F5 The 6.500 EUR condition was never updated while the reducción it switches off doubled
- kind: statute-fault (amount not updated when a related amount changed)
- evidence (Global law compare_dates, LIRPF art. 20, 2015-06-30 vs 2025-06-30): maximum reducción 3.700 -> 7.302,
  upper limit 14.450 -> 19.747,5 (Ley 6/2018, Ley 31/2022, RDL 4/2024); "superiores a 6.500 euros" unchanged since Ley
  26/2014. DA 61.ª (2025) copied the same 6.500. The F4 cliff grew from at most 3.700 to 7.302 EUR of base.
- status: certain (versioned text); classification: statute fault (design), not a drafting slip.

### F6 Madrid's 10 % family deduction ends abruptly at 24.744 EUR of family base
- kind: loophole-new (notch)
- households: single parent of two (11, 6): wages 28.590 -> 28.600 costs 125,90 EUR more; one-earner married couple
  with two children (joint): 109,90 at the same point; two earners (20.000 + 17.310, two children): 63,36 for 10 EUR.
- why: DLeg 1/2010 art. 14 "suma de bases imponibles no sea superior a 24.744 euros ... 10 por 100", no glide.
- Lean: `cliff_madrid_art14` (more than 120 EUR for 10 EUR of wages).
- status: certain; not found in the sources read.

### F7 Madrid's birth deduction (721,70 EUR per child) has three notches
- kind: loophole-new (notches)
- households: single parent of a one-year-old: 42.040 -> 42.050 costs 724,96 (joint base passes 37.322,20); married
  couple filing separately (20.000 + x, child aged 1): the second earner loses his/her half (360,85) when his/her
  own base passes 30.930 (x = 35.210 -> 35.220: +364,10), and the other half goes when the family's bases pass
  61.860 (x = 51.690 -> 51.700: +364,84).
- why: DLeg 1/2010 art. 4 with art. 18.1 limits (30.930 individual, 37.322,20 joint, 61.860 family), no glide.
- Lean: `cliff_madrid_art4`, `cliff_madrid_art4_couple`.
- status: certain; not found in the sources read.

### F8 Joint filing: worth 945-1.420 EUR to a one-earner couple, nothing once the second earner has 6-8.000 EUR
- kind: loophole-known (tributación conjunta, arts. 82-84)
- households: average-wage earner (32.678), spouse without income: joint saves 945,20 (no children) and 1.420,08 (two
  children); joint stops paying once the spouse earns 5.800 (no children) / 7.700 (two children). An unmarried couple
  in the same situation cannot file jointly (art. 82; the 2.150 reduction is excluded when the parents live
  together) and pays 1.420,08 more: a marriage bonus.
- Lean: `joint_beats_separate_one_earner`, `married_vs_unmarried_one_earner`.
- status: certain; known (AEAT manuals describe the option).

### F9 The mínimo personal y familiar is a credit at the bottom rate
- kind: statute property (explains the OECD booking as tax credit)
- LIRPF art. 63.1 2.º taxes the mínimo at the bottom of the scale: inside the first band its value is 9,5 % of it
  whatever the base (`minimo_bottom`), and a deduction of the same amount from the base is never worth less
  (`minimo_credit_le_deduction`, from the kernel's progressivity and a superadditivity lemma `superadd`). So
  5.550 EUR is worth 527,25 (state) to every taxpayer whose base exceeds it.
- status: certain (theorem).

### F10 Art. 20 c) does not quite reach zero at 19.747,5 EUR
- kind: statute-fault (trivial drafting rounding)
- 2.364,34 − 1,14 x (19.747,5 − 17.673,52) = 0,0028 EUR: the formula reaches 0 at 19.747,5025; b) and c) meet exactly
  at 17.673,52 (`red20_cont_T2`, `red20_residual_at_end`, `red20_last_cent`). DA 61.ª's taper ends exactly at 18.276
  (`smi_cont`). In band b) each extra euro of rendimiento neto removes exactly 1,75 EUR of reducción (`red20_slope_b`).
- status: certain; harmless (at most 1 cent after rounding).

### F11 Withholding conventions: truncation, and a scale built for a generic region
- kind: gov-error; classification: convention
- (a) RIRPF art. 86.1: the tipo "se expresará con dos decimales"; the AEAT algorithm truncates ("TRUNCAR (TIPO)",
  example 17,85964523 -> 17,85). Effect at most 0,01 % of pay, always in the worker's favour. Reading: allowed.
- (b) The withholding scale (RIRPF art. 85.1) is the state scale doubled in its first five bands but 47 % (not 49 %)
  on the top band (`retencion_doble`, `retencion_top`): it assumes a 22,5 % regional top rate. For a single Madrid
  resident it over-withholds above about 22.000 EUR: 225 at 25.000, 642 at 50.000, 1.007 at 80.000, 1.803 at 120.000
  (`runs/withholding_scan.json`).
- status: convention (by design: the payer does not apply regional scales).

### F12 Marginal effective rate 72,8 % for single workers on 16.700-18.276 EUR
- kind: loophole-known (taper stacking, below 100 %)
- the DA 61.ª taper (0,2 per EUR of wage), the art. 20 b) taper (1,75 per EUR of net) and the 9,5 % + 8,5 % first
  rates stack: 0,0648 + (1 − 0,0648) x 2,75 x 0,18 + 0,2 = 72,8 % (scan, 100 EUR windows). No band above 100 % without
  a notch (F4, F6, F7).
- status: computed.

### F13 Owner-manager: company plus dividends beats self-employment above about 60.000 EUR of profit
- kind: loophole-known (income-type conversion)
- profit P as sole-trader income vs a micro company (LIS DT 44.ª for 2025: 21 % up to 50.000, 22 % above) paying the
  rest as dividends (base del ahorro 19-30 %): the best salary/dividend mix saves 80 at 60.000, 2.316 at 100.000,
  5.789 at 200.000 and 13.329 at 500.000 (RETA ignored on both sides); retained profits bear only 21-22 % until
  distributed. `runs/recreate.json`.
- status: computed; known (standard planning; limits: LIRPF art. 27.1 for socios profesionales, LIS art. 18).

## Model notes (choices, not findings)
- Rounding: each computed amount to the cent, half up (the AEAT's REDONDEAR1 rounds 0,005 up; the statute is silent).
  Employee contributions rounded per component (4,70 / 1,55 / 0,10 / 0,13 %).
- Joint returns: one art. 20 reducción on the members' summed rendimientos (art. 84.2 "idéntica cuantía"), the 2.000
  of art. 19.2 f) per earner; DA 61.ª computed on the unit's summed wages (reading; no AEAT text found).
- DA 61.ª limit: (cuota íntegra estatal + autonómica) x rendimiento neto del trabajo reducido / (base imponible
  general + ahorro), a reading of "la parte ... que proporcionalmente corresponda".
- Art. 81 bis limit: employee + employer contributions without AT/EP and FOGASA (a lower bound of "cotizaciones y
  cuotas totales").
