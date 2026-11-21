# Latvia 2025: findings

Model `lean/LvTax` (exe `lvtax`); Lean names refer to `lean/LvTax/{Theorems,Findings,Tests}.lean` (all proved, no
`sorry`). Scans: `runs/lv_scan.md` (targeted), `results/search/SUMMARY.md` (generic, blind). Amounts in euro, 2025.
"Sources searched" for novelty (10 documents + 3 web searches): IIN likums (2025 text), VSAOI likums, Solidaritātes
nodokļa likums, VID "Izmaiņas IIN no 2025. gada" (27931), VID "Algas nodoklis 2025" (27996), VID "Attaisnotie
izdevumi" (33101), LV portāls 35368, 37184, 37449, OECD Economic Survey of Latvia 2017; web searches (1) VID self-
employed VSAOI 2025, (2) VID 33 % worked examples, (3) OECD survey on micro-enterprise/royalty/dividend regimes.

### F1 Self-employed: one euro over the minimum wage costs 1 393 euro a year (116 a month)
- kind: loophole-new (notch / METR > 100 %). households: single self-employed, general regime, profit received evenly.
- amounts: profit 8 879 → 8 880 a year (739,92 → 740 a month): VSAOI 888 → 2 759, IIN 477 → 0; **net income falls
  by 1 393**; net income at 8 879 is regained only at 10 960 (a 2 080-euro band where earning more leaves less).
  Per month: 739 → 740 raises VSAOI from 73,90 to 229,92 (+156,02), 116 net of the IIN deduction.
- provisions: VSAOI 14. panta 2. daļa (object "brīvi izraudzīti ienākumi", minimum set by MK), 14.1 pants (below the
  minimum wage "10 procentu apmērā no ienākuma"; at or above it an object "kas nav mazāks par ... minimālo mēneša
  darba algu" at the full rate plus 10 % on the rest: LV portāls 37184), 31,07 % (VID 37449); IIN 10(1)(1).
- Lean: `f1_se_notch` (burden rises by 1 390-1 400 euro for one euro of profit).
- known? the rule is published (VID 37449: "ja ienākumi mēnesī ≥ 740 eiro ... jāmaksā 31,07% no vismaz 740 eiro; ja
  ienākumi < 740 eiro, jāmaksā 10%"); the size of the notch and the 2 080-euro dead band: not found in 10 sources +
  3 searches. Found blind in part by the kernel's income-type scanner (selfEmployment −17 % vs wages at 0,5 AW).
- caveat: the 31,07 % buys sickness, maternity, unemployment and disability cover that the 10 % does not.
- status: model-proved.

### F2 Self-employed: the same profit received in fewer months saves up to 1 277 euro a year
- kind: loophole-new (timing within the year). households: self-employed with annual profit ≥ 8 880.
- amounts: profit 12 000 received evenly over 12 months: burden 3 787; over 6 months 3 091; 3 months 2 742; one
  month 2 510: **1 277 saved**, the same for every profit ≥ 8 880 (21,07 % × 740 × 11 months net of 25,5 % IIN).
- provisions: VSAOI 14.1 pants (the test is per month: "kuru ienākumi mēnesī sasniedz vai pārsniedz ... minimālo
  mēneša darba algu"); the self-employed report quarterly by month (VID 37449).
- Lean: `f2_se_months`; exe option `"lvSeMonths": n`.
- known? not found in 10 sources + 3 searches; the generic timing scanner (between years) cannot see it.
- caveat: as F1 (less social insurance); whether income may be timed by invoicing depends on the cash/accrual rule
  for business income (IIN 11. pants) (reading-dependent).
- status: model-proved; reading-dependent.

### F3 A spouse's first euro of wages costs the family 765 euro; the same couple unmarried pays it too
- kind: loophole-new (notch) and marriage bonus. households: married couple, earner 21 321 (1 AW), spouse at home,
  one child aged 1 (earners of 15 000 and 40 000: the same 765).
- amounts: spouse earns 0 → 1 euro: family IIN 1 775 → 2 540 (+765 = 3 000 × 25,5 %); unmarried (cohabiting) couple:
  2 540 as well (**marriage bonus 765**).
- provisions: IIN 13. panta 1. daļas 1. punkts l) ("par nestrādājošu laulāto, kura apgādībā ir bērns vecumā līdz trim
  gadiem"), m), n); 13. panta 1.2 daļa (250 a month); 13. panta 3. un 5. daļa (lost for a month in which the
  dependant's taxable income exceeds 250); "laulāto" = married spouse only.
- Lean: `f3_spouse_notch`, `f3_marriage_bonus` (`decide` on the household computation).
- reading: "nestrādājošs" is read as no employment at all (any wage ends it); under the softer reading (only the
  income test of 13(3), 13(5)) the notch moves to 251 euro a month and is still 765 a year over 12 months. The
  parental benefit (vecāku pabalsts) is taxable income, so in practice the relief starts when it ends.
- known? the relief is described by VID; the notch and the marriage-only condition as a 765-euro marriage bonus:
  not found in 10 sources + 3 searches. The generic filing-unit scanner reports no marriage effect (its grid has no
  child under 3).
- status: model-proved.

### F4 Children's reliefs on the wrong parent's tax book cost up to 2 258 euro a year
- kind: loophole-known (allocation). households: married, wages 7 000 + 30 000, three children 5-7.
- amounts: all three reliefs (9 000) on the 7 000 earner, who can absorb almost none: family IIN 5 286; on the
  30 000 earner: 3 028; **2 258** lost. Wages 5 000 + 40 000 with two children: 1 530.
- provisions: IIN 13. panta 1. daļas 1. punkts ("vienam no apgādniekiem"), 3.2 daļa (the parents agree, else the
  bāriņtiesa decides); an unused relief is not transferable.
- Lean: `f4_allocation`. The exe always picks the best split (every split is tried).
- status: model-proved.

### F5 Author's royalty regime: 25 % final instead of ~43 % (employee) on the same payment
- kind: loophole-known (K2, special regime extended to 2027). households: single, payment costing 50 000.
- amounts: as wages (40 456 + employer 23,59 %) the worker keeps 28 536; as a royalty under PN 163-171, 37 500
  (+8 964); at 250 000: 130 751 vs 187 500 (+56 749). The royalty is outside the 33 % band and the 3 % rate.
- provisions: IIN pārejas noteikumi 163, 164 ("25 procentu likmi"), 170 (not in the progressive base, no 10., 12.,
  13. panta deductions), 171 (80 % VSAOI / 20 % IIN), 200 (outside the 3 %).
- Lean: `f5_royalty_vs_wage`.
- status: model-proved; known (VID 27931 "pagarināts īpašā režīma periods autoratlīdzību saņēmējiem").

### F6 Owner-manager: all profit as dividends, 20 % in total at every level
- kind: loophole-known (K1). households: one-person SIA, profit 0,5-10 AW (generic owner scan, blind).
- amounts: all dividends 20,0 % vs all salary 31,4 % (0,5 AW), 38,8 % (1 AW), 44,6 % (5 AW), 48,5 % (10 AW); gains
  1 216 to 60 757 a year; no salary at all is optimal even where the neapliekamais minimums is unused (salary costs
  23,59 % + 10,5 % before IIN, the dividend 20 %). Above 200 000 of dividends only the 3 % additional rate applies.
- provisions: UIN 3. panta 1. daļa and 4. panta 9. daļa (20 % on the distribution / 0,8); IIN 9. panta 1. daļas
  2.1 punkts (exempt), 15.1 panta 2. daļas 2. punkts (in the 3 % base). Counter-rules not in the scan: VSAOI 14(12.1)
  (a board member who is an employee has an object of at least the minimum wage); from 2026 UIN 4.2 (15 % + 6 % IIN).
- Lean: `f6_dividends`.
- status: model-proved; known.

### F7 Above 105 300 euro the employer withholds too little: about 10 % of the excess is due with the return
- kind: loophole-known (deferral by design) / taxpayer warning. households: employees with one job.
- amounts: wage 150 000: annual IIN 37 166, withheld 32 673: **4 492** due (10,05 % of 44 700); 300 000: 22 567
  incl. the 3 % (11,6 %). Composition: 7,5 % (33 − 25,5) of the wage above 105 300 (`withholding_gap`), plus 25,5 %
  of the 10 % IIN share of the solidarity tax that stops being deductible at year end (IIN 10(1.10)).
- provisions: IIN 15. panta 3. daļa (monthly rate 25,5 % only), 2. daļa, 10. panta 2. daļa and 1.10 daļa,
  Solidaritātes nodokļa likums 8.1(3); VID 27931 "33 % likmi piemēro, iesniedzot gada deklarāciju".
- Lean: `withholding_gap` (general), `f7_settlement` (≥ 4 490 on 150 000).
- status: model-proved; known in principle (VID), size not published.

### F8 VID's 2025 information material puts the 33 % band on taxable income; the statute puts it on income
- kind: gov-error (classification: **reading**, ambiguous wording). households: income above 105 300.
- text: VID "Izmaiņas iedzīvotāju ienākuma nodoklī no 2025. gada" (12.12.2024, p. 2): "33 % likmi piemēro, iesniedzot
  gada deklarāciju, apliekamajam ienākumam virs 105 300 eiro gadā". Statute: 15. panta 2. daļa "gada ienākuma daļai,
  kas pārsniedz ... maksimālo apmēru" with 3. panta 2.4 daļa (deductions first from the income up to 105 300) and 15.
  panta 15. daļa; VID's own "Algas nodoklis 2025" (p. 3) has it right: "33 % – gada ienākuma daļai, kas pārsniedz
  105 300 eiro".
- amounts: read as "taxable income above 105 300", income 110 000 with deductions 18 000 pays 352,50 less than the
  statute; in general 7,5 % × min(deductions, income − 105 300), about 1 300 at most for a typical employee.
- Lean: `lowband_cost` (general), `f8_vid_reading` (352,50).
- status: confirmed text; draft fix: "33 % likmi piemēro ... gada ienākuma daļai virs 105 300 eiro (atskaitījumus
  atskaita no ienākuma daļas līdz 105 300 eiro)".

### F9 Deductions are worth 25,5 % at every income, also in the 33 % band
- kind: model-fix (a structure only Latvia has in the family; kernel `taxAfterLowBand` up to 105 300 of deductions).
- the minimum (6 120), dependants (3 000 each), contributions, donations and pension savings come off the 25,5 % part
  first (3. panta 2.4 daļa); if they exceed 105 300, 15. panta 15. daļa still credits the excess at 25,5 % although it
  offsets income taxed at 33 %. A 33 % taxpayer's private pension contribution of 4 000 saves 1 020, not 1 320.
- Lean: `iin_eq_lowband`, `deduction_worth_255`, `iin_closed`, `deductions_at_lowest_rate` (never cheaper than a
  zero band: kernel `lowBand_le_zeroBand`).
- status: modelled; OECD lines exact (56/56; decomposition 3 216/3 216 within 1 %).

### F10 IIN 12. panta 1. daļa (2025 text) says 570 euro a month; the 2025 amount is 510
- kind: statute-fault (classification: **convention**, future-dated drafting). households: all.
- text (redakcija 01.01.2025 and 16.05.2025): "Mēneša neapliekamais minimums ir 570 euro mēnesī." The 2025 and 2026
  amounts are only in pārejas noteikumi 197: "1) 2025. gadā ir 510 euro mēnesī; 2) 2026. gadā ir 550 euro mēnesī"
  (both from the 04.12.2024 law; VID 27931 lists 510 / 550 / 570 for 2025 / 2026 / 2027).
- amounts: a reader of article 12 alone overstates the 2025 minimum by 720 a year, 183,60 of tax per taxpayer.
- Lean: `f10_ntm_text`. status: confirmed in both 2025 redactions; draft fix: "... ir 510 euro mēnesī, ja šā likuma
  pārejas noteikumos nav noteikts citādi", or a cross-reference to PN 197 in 12(1).

### F11 IIN 15. panta 2. daļa excludes the income of 11. daļa, which 11. daļa taxes "papildus šā panta otrajā daļā noteiktajai likmei"
- kind: statute-fault (classification: **reading**). households: employees/board members with loans treated as
  income (8.1 pants).
- text: 15(2) applies its rates "izņemot šā panta ... vienpadsmitajā ... daļā noteiktos ienākuma veidus"; 15(11):
  "attiecīgajam ienākumam papildus šā panta otrajā daļā noteiktajai likmei piemēro 22 procentu papildu likmi". Read
  literally the 22 % is added to a rate that 15(2) says does not apply. Same wording in the 2024 text (20/23/31 %);
  since 2025 the question is also whether such income enters the 105 300 band. Not modelled (no loans in the contract).
- status: confirmed text; draft fix: delete "vienpadsmitajā," in 15(2), or in 15(11) "piemēro šā panta otrajā daļā
  noteikto likmi un papildus 22 procentu likmi".

### F12 IIN 13. panta 6. daļa: its list of rates was not updated with 13. panta 3. daļa
- kind: statute-fault (classification: **error**, list not updated; minor effect). households: dependants with
  income at special rates.
- text: 13(3) (and 12(9)) list "15. panta piektajā, sestajā, septītajā, 7.1, 7.2, astotajā, desmitajā, divpadsmitajā
  un 19.2 daļā"; 13(6) (loss of the relief for the whole year) still lists only "piektajā, sestajā, septītajā un
  astotajā daļā" (the same in the 2024 and 2025 texts, while the 15(2) list grew by 7.2 and 19.2 in 2025). A
  dependant with income at 15(7.2) (5 %), 15(12) (seasonal workers, 15 %) or 15(19.2) (15 %) above 3 000 a year falls
  under the monthly rule only.
- status: confirmed text; not modelled.

### F13 VID leaves micro-enterprise income out of the 3 % additional-rate base without an express statutory exception
- kind: gov-error (classification: **reading**). households: total income above 200 000 including micro turnover.
- text: VID 27931 p. 3: "Papildu likmes piemērošanai netiek ņemti vērā: ... ienākumi no mikrouzņēmuma". Statute:
  15.1(2)(1) counts "taksācijas gada ar nodokli apliekamie ienākumi"; IIN 3(1): "Ar nodokli apliek mikrouzņēmuma
  ieņēmumu daļu atbilstoši Mikrouzņēmumu nodokļa likumam", and MUN 1(4)(b) says the micro tax includes the owner's
  IIN; the only express exclusion (PN 200) is for the royalty regime. The model follows VID (micro income outside).
- amounts: at most 3 % × 50 000 = 1 500 a year per taxpayer.
- status: reading; no statutory support for VID's exclusion found (the express exclusion in PN 200 points the other way).

### F14 The employee has no contribution ceiling: 10,5 % above 105 300 is solidarity tax, refunded only to the employer
- kind: model-fix. households: wages above 105 300.
- the employee keeps paying 10,5 % (Solidaritātes nodokļa likums 6.2(1)); the overpayment above the 25 % rate is
  refunded "tikai darba devējam" (6.2(3)); only 0,5 % of it stays deductible (IIN 10(1.10)). Marginal rate on wages
  105 300-200 000: 33 + 10,5 − 25,5 × 0,5 % = 43,37 %; above 200 000: 46,37 %.
- Lean: `vsaoi_capped` (kernel ceiling) and `employee_no_ceiling` (with the solidarity tax: 10,5 % of every euro).
- status: modelled.
