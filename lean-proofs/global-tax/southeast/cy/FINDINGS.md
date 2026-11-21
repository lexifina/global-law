# CY findings (Cyprus, tax year 2025)

Each block: kind (loophole-known | loophole-new | gov-error | statute-fault | model-fix | reading | convention),
households, amounts, provisions, Lean name (in `lean/CYTax/Findings.lean` unless stated), status. Euros; "c" = cents.
Statute texts: `law/` (CyLaw consolidations; the 2025 versions from the Wayback Machine, see PROGRESS.md "Sources").
"Not found in N sources searched" lists the sources in the block; none of them is a tax-planning database.

### F1 Social insurance: the statute prints 8,9 %, the rate applied in 2025 is 8,8 %
* kind: statute-fault (the applied rate is nowhere in the statute text)
* What: SIL 59(I)/2010 art. 5(1)(στ) reads "23,1%, από το οποίο 8,9% καταβάλλεται από τον μισθωτό, 8,9% από τον
  εργοδότη και 5,3% από το Πάγιο Ταμείο, από το έτος εισφορών που αρχίζει κατά ή μετά την 1η Ιανουαρίου 2024" (same
  text in the 12 Sep 2025 and the current consolidation); art. 12(ζ) prints 16,8 % for the self-employed. The proviso
  to art. 5(1) lets "τα υποδεικνυόμενα από την υπό αναφορά αναλογιστική μελέτη ποσοστά" apply instead. The rates
  actually charged in 2025 are 8,8 % / 8,8 % / 5,2 % (22,8 %) and 16,6 % (EUROMOD CR Cyprus §1.4, §2.7.1.3 Table 2.13;
  Eurostat earn_nt_net 2025: SOC = 11,45 % of gross at every wage below the ceiling = 8,8 % + 2,65 % GESY, 13/13
  household types). A reader of the law alone over-computes every employee's contribution by 0,1 % of pay (66,61 € a
  year at the 66.612 € ceiling) and the self-employed's by 0,2 %.
* Households: every employee. Lean: `si_statute_vs_applied` (592.847 c vs 586.186 c at the ceiling); exe option
  `--statute-si`.
* Fix: amend art. 5(1)(στ), 5(2)(στ), 12(ζ), 15 to the rates set after the actuarial study, or publish the decision
  that fixed them with the law. Status: recorded; the model uses 8,8 %.

### F2 ITL art. 8(23Α): one cent of pay above 55.000 € exempts half the pay (notch of ~7.000 €)
* kind: loophole-known (the 55.000 € condition is well known to advisers); the size of the notch is quantified here
* What: "τo πενήντα τοις εκατόν (50%) της αμοιβής … για οποιοδήποτε έτος στο οποίο η αμοιβή … υπερβαίνει τις πενήντα
  πέντε χιλιάδες ευρώ (€55.000)". Not a phase-in: the whole 50 % switches on.
* Household: a single newcomer (15 years non-resident) on 55.000,00 € vs 55.000,01 €: income tax 7.495,75 € → 500,00 €,
  net pay 41.206,75 € → 48.202,51 € (+6.995,76 € for one cent). A Cypriot without the exemption needs 66.286,21 € to
  net the same. Any newcomer offered less than 55.000 € is better off asking for 55.000,01 €.
* Lean: `notch23A`. Scanner: not on the generic grid (the exemption is a status, input `cyFirstEmployment: "23A"`).
* Status: recreated blind (CATALOGUE K3). 2026: kept unchanged by 244(I)/2025.

### F3 The art. 14 one-fifth cap takes back part of the 23Α relief (contributions on exempt pay become non-deductible)
* kind: loophole-new (an interaction that costs the relocator): not found in 4 sources searched (EUROMOD CR, the ITL
  text, the reform law 244(I)/2025, the SDC/GESY texts)
* What: art. 14 proviso (ii) caps the deduction for insurance contributions at "το ένα πέμπτο του φορολογητέου
  εισοδήματος … προτού αφαιρεθούν … οι εκπτώσεις … του παρόντος άρθρου". SI + GESY are 11,45 % of all pay, but under
  23Α only half the pay is taxable, so the contributions (22,9 % of taxable pay) exceed the cap.
* Household: 23Α newcomer on 55.000,01 €: SI + GESY 6.297,50 €, cap 5.500,00 €, 797,50 € of contributions not deducted
  (tax +159,50 € at 20 %). At 70.000 €: 716,86 € not deducted; from about 80.000 € the claim (SI stops at the ceiling)
  is under the cap again. Under 21Α (20 % up to 8.550 €) the cap never binds for wages alone.
* Lean: `cap23A_bites`; generic `art14_le_fifth` (Theorems.lean).
* Status: modelled; the 2026 art. 14(2) keeps the one-fifth cap.

### F4 Child benefit and single-parent benefit cliffs: marginal effective rates of 194 % to 6.862 %
* kind: loophole-new (notches; known in kind for step tables; not found quantified in 4 sources: EUROMOD CR
  §2.6.2-2.6.3, CBL 167(I)/2002, Eurostat, the scanner output of this project)
* What: CBL 167(I)/2002 Schedule para 2 and Table A: the per-child amount falls in steps at 19.500 €, 39.000 €,
  49.000 € of gross family income and stops at 49.000 € (1 child), 59.000 € (2), 64.000 € (3), 69.000 € (4); the
  single-parent benefit (Table B) steps at 39.000 € and stops at 49.000 €. Every step applies to all children at once.
* Households (one cent more of family income, 2025 amounts): couple, 1 child at 49.000 €: −478,79 €; 2 children at
  59.000 €: −869,96 €; 3 children at 64.000 €: −2.609,91 €; 4 children at 69.000 €: −5.721,00 €; lone parent, 1 child
  at 49.000 €: −2.789,15 €; lone parent, 2 children at 49.000 €: −4.708,32 €. Generic timing scanner: bunching two
  years' pay gains a lone parent of two 6.812 € (19,6 % AW). Five or more children: no income limit at all.
* Lean: `cb_cliff_one_child`, `cb_cliff_two_children`, `cb_cliff_three_children`, `cb_cliff_four_children`,
  `sp_cliff_one_child`, `cb_five_no_limit`. Scanners (results/search/SUMMARY.md): METR peak 6.861,7 % (single parent of
  2 at 49.000 €), 3-4 bands above 100 % per family type with children; edges: 4 notches.
* Fix: taper the last column (withdraw at a rate on the excess) instead of a cliff. Status: modelled.

### F5 SDC on interest: the 12.000 € total-income test is a notch of 14 % of the interest
* kind: loophole-new (notch; the rule is known, the notch is not described as such in EUROMOD CR §2.9.1 or the SDC Law)
* What: SDC Law art. 3(2)(β)(iii) (2025; art. 3Β(α)(i) from 2026): an individual "του οποίου το συνολικό ετήσιο
  εισόδημα, περιλαμβανομένων και των τόκων, δεν υπερβαίνει … (€12.000)" gets back the SDC above 3 %. One cent over:
  17 % on all the interest.
* Households: 12.000 € of interest and nothing else: SDC 360 € → 2.040,00 € at 12.000,01 € (net −1.679,99 €);
  10.000 € wages + 2.000 € interest: −279,99 €. Also a splitting lever: deposits held by a family member under
  12.000 € pay 3 %.
* Lean: `sdc_interest_notch`. Status: modelled (the refund treated as automatic; "total income" read as gross income
  incl. exempt dividends, excl. gains).

### F6 Owner-manager: low salary + dividends; non-domiciled shareholders pay no SDC at all
* kind: loophole-known (the non-dom regime is the stated effect of the SDC Law art. 2 domicile rule; the
  salary/dividend mix is standard advice)
* Company side (proposed for harness/search/company.json, cited in PROGRESS.md): CIT 12,5 % (ITL Second Schedule
  para 2, 2025 text); employer SI 8,8 % + Redundancy 1,2 % + HRDF 0,5 % to the 66.612 € ceiling, Social Cohesion 2 %
  and GESY 2,90 % uncapped (15,4 % in all below the ceiling; Eurostat's implied rate at ≤ 1 AW is 15,4 %).
* Result (`harness/owner_cy.py`, results/owner_cy.txt), profit before the owner's pay P, all paid out:
  domiciled: best salary 22.000-24.500 € (fills the 0 % band after the art. 14 deduction), net 71-76 % of P
  (P = 120.000 €: 86.165 € vs 74.498 € all-salary, 84.368 € all-dividend); non-domiciled: best salary 0, net 85,2 % of P
  (12,5 % CIT + 2,65 % GESY; 86,3 % at P = 400.000 € once GESY's 180.000 € cap binds): 102.218 € at P = 120.000 €,
  +16.053 € (+18,6 %) over the domiciled optimum.
* Lean: `nondom_no_sdc`. Status: recreated blind (CATALOGUE K1, K2). 2026: SDC 5 % on post-2025 profits narrows the
  domiciled/non-dom gap to 5 points; CIT 15 %.

### F7 Individual taxation: investment income in the lower-income spouse's name
* kind: loophole-known (individual taxation; transfers between spouses are not attributed back)
* What: no aggregation rule in ITL; rent is taxed at the owner's marginal rate after the 20 % art. 9(2) deduction.
* Household: 20.000 € rent: 5.071 € income tax in the name of a 60.000 € earner, 0 € in the name of a spouse with no
  income (16.000 € inside the 0 % band). Generic unit scanner: "marriage changes nothing anywhere on the grid" (married =
  cohabiting); the largest gain from equalising a couple's income is 6.851 € (19,8 % AW) at 2,35 AW (only investment
  income can actually be moved).
* Lean: `rent_to_spouse`; `separate_le_aggregated` (Theorems.lean). Status: recreated (K5).

### F8 The 2026 scale as a timing lever: defer pay from 2025 into 2026
* kind: loophole-known in kind (timing around a rate cut); quantified here
* What: 244(I)/2025 art. 24 adds Second Schedule 1(γ) "Από το φορολογικό έτος 2026" (0 % to 22.000, then 20/25/30/35 %
  above 32.000/42.000/72.000). Moving a 12.000 € bonus from 2025 to 2026 on top of 60.000 €: 4.200 € → 3.600 €
  (−600 €); any taxable income ≥ 72.000 € pays 1.585 € less in 2026; per euro moved the gain is 5 points in the bands
  19.500-22.000 (20 → 0 %), 28.000-32.000, 36.300-42.000 and 60.000-72.000. Dividends do not benefit: what matters for
  SDC is the year of the profit, not of the payment (F10).
* Lean: `bonus_deferral_gain`, `scale_2025_minus_2026_top`; `scale26_progressive/_mono/_convex`. Status: recorded.

### F9 EUROMOD's Cyprus report: two descriptions that do not match the 2025 statute
* kind: gov-error (EUROMOD country report 2022-2025, JRC 2026)
* (a) §2.7.5.3: "The maximum deductible income is set at €180,000, which means a maximum deduction of €3,060 can be
  claimed": 3.060 € = 180.000 € × 1,70 %, the 2019-2020 first-phase GESY rate; at 2,65 % (GESY art. 19(1)) it is
  4.770 € (Lean `gesy_max_deduction`). (b) §2.8.2.3 lists "Contributions to private medical funds, up to a maximum
  equal to 2% of remuneration" and "pension and provident funds, up to … 10% of remuneration" for 2022-2025: those
  limits are the new ITL art. 14(1)(γ),(δ) of 244(I)/2025 art. 9, in force 1.1.2026; the 2025 art. 14 has only the
  one-fifth cap and the 7 % life-insurance limit. (c) §1.4 (16,6 %) vs SIL art. 12(ζ) (16,8 %): EUROMOD has the
  applied rate (F1).
* Draft issue text (not filed): "Cyprus CR 2022-2025, §2.7.5.3: the maximum GHS deduction is €4,770 (2.65 % ×
  €180,000), not €3,060 (1.7 %, first phase). §2.8.2.3: the 2 %/10 % limits apply from 2026 (Law 244(I)/2025 art. 9),
  not in 2022-2025." Status: recorded.

### F10 The reform's six-year sunset: 2025 profits kept in the company until 2032 pay 5 %, not 17 %
* kind: loophole-new (timing): not found in 5 sources searched (SDC Law current text incl. 245(I)/2025, EUROMOD CR,
  ITL, the 244(I)/2025 preamble, the SDC 2025 text); advisers may well have spotted it
* What: SDC Law art. 3(1)(α) from 1.1.2026: 5 % on dividends; proviso (ii): 17 % on dividends "μέχρι και έξι (6) έτη
  από την ημερομηνία έναρξης της ισχύος" of the 2025 amending law and issued "από κέρδη … μέχρι και το φορολογικό
  έτος 2025". After 31.12.2031 pre-2026 profits fall to 5 %. The deemed distribution (art. 3Γ, current text) still
  applies to 70 % of 2024 and 2025 profits (17 %, two years after the year), so only the other 30 % of those years,
  and the undistributed 30 % of earlier years' profits, can wait. No ordering rule says which year's profits a
  dividend comes from (none found in the SDC text), so a company may also be able to pay 2026+ profits first at 5 %.
* Household: 10.000 € of 2025 after-tax profit: paid by 2031 → 1.700 € SDC; retained → 1.190 € (deemed, 2027) +
  150 € (2032) = 1.340 € (−21 %); on old reserves already past their deemed distribution: 17 % → 5 % (−71 %).
* Lean: `sunset_saving`. Status: recorded (company side not in the exe). Question for the Tax Department: is there a
  FIFO rule for the "κέρδη" a dividend "εκδίδεται" from? Art. 4Β (GAAR, 2026 text) is unlikely to catch waiting for a
  statutory date.

### F11 ITL Second Schedule: the 2008 scale still reads "από το φορολογικό έτος 2008 και μετέπειτα" after the 2026 scale was added
* kind: statute-fault (drafting; resolved by lex posterior/specialis)
* What: 244(I)/2025 art. 24(α) inserted 1(γ) "Από το φορολογικό έτος 2026 και μετέπειτα" and left 1(β) "Από το
  φορολογικό έτος 2008 και μετέπειτα" as it was: for 2026 the text gives two scales. Para 2 (companies) now reads 15 %
  with no year, so the 2025 company rate (12,5 %) cannot be read from the current text without the commencement clause
  (244(I)/2025 art. 25).
* Fix: "από το φορολογικό έτος 2008 μέχρι και το φορολογικό έτος 2025". Lean: `scale_progressive`,
  `scale26_progressive` (both modelled separately). Status: recorded.

### F12 Child benefit thresholds are tied to the income-tax "αφορολόγητο": from 2026 columns (2) and (3) overlap
* kind: statute-fault (versioned law: an amount updated automatically while its neighbour is not)
* What: CBL Schedule para 5-6: column (1) "ισούται με το αφορολόγητο εισόδημα για φυσικά πρόσωπα" and the top of column
  (2) is "το διπλάσιο", both re-set "σύμφωνα με το εκάστοτε ισχύον αφορολόγητο εισόδημα". From 2026 the 0 % band is
  22.000 € (F8), so column (2) runs to 44.000 €, while column (3) is printed "από €39.000,01 μέχρι €49.000" and the
  single-parent Table B "€0-€39.000,00 / €39.000,01-€49.000,00": incomes 39.000,01-44.000 € fall in both column (2) and
  column (3). The income test uses the previous year's income, so the overlap bites from 2026 incomes on.
  ("αφορολόγητο" is not a defined term in ITL; read as the 0 % band.)
* Fix: tie column (3)'s lower bound and Table B to the same reference. Status: recorded (outside the 2025 model).

### F13 CyLaw editorial notes name the wrong reform laws
* kind: gov-error (publisher annotation; CyLaw is the Cyprus Bar Association's consolidation and the publisher of the
  Global law Cyprus corpus)
* What: ITL consolidation, commencement note: "25 του Ν. 224(Ι)/2025 … Ο παρών Νόμος [Σ.Σ.: δηλαδή ο Ν. 224(Ι)/2025]
  τίθεται σε ισχύ από την 1η Ιανουαρίου 2026": the amending law is 244(I)/2025 (its art. 25; the page's own list of
  amendments says 244(I)/2025). SDC consolidation: "10 του Ν. 245(Ι)/2025 … [Σ.Σ.: δηλαδή ο Ν. 145(Ι)/2025]".
* Draft note to CyLaw (not sent): "118(I)/2002, σημείωση έναρξης: 224(Ι)/2025 → 244(Ι)/2025· 117(I)/2002: 145(Ι)/2025
  → 245(Ι)/2025." Status: recorded.

### F14 ITL art. 9(1)(ζ) still caps listed-building expenses in Cyprus pounds
* kind: statute-fault (amounts not converted at the 2008 euro changeover) / reading
* What: art. 9(1)(ζ)(i) "£350 … £300 … £200 … για κάθε τετραγωνικό μέτρο" and the proviso "εκατόν ογδόντα λιρών" (two
  different caps for the same expense) in both the 2025 and the current consolidation; EUROMOD CR §2.8.2.2 gives
  "€1,200, €1,100 or €700 per sq. m". The source of the euro amounts was not found in the consolidated text.
* Status: recorded, not modelled (not in the household contract).

### F15 Validation note: Eurostat rounds SI + GESY as one amount
* kind: convention
* What: 12 of 52 Eurostat lines differ by 0,01 € (SOC and NET of the AW-based households): 34.692 € × 8,8 % =
  3.052,896 and × 2,65 % = 919,338; the model rounds each contribution (3.052,90 + 919,34 = 3.972,24), Eurostat the sum
  (3.972,23). Income tax agrees to the cent in all 13 households.
* Status: explained.

### W5S-1 CyprusTaxCalculator (mouli1999): the band's rate on the whole income (W5 review pass 2, 2026-11-20)
- kind: software-error
- `cy_open_cyprus_tax_calculator_mouli_grid`: getTax returns 20 / 25 / 30 / 35 % of the whole income according to the band it falls in (builder's note; ref = 3,916.8 on 19,584); Income Tax Law 118(I)/2002 art. 34 taxes each slice at its own rate.
- status: recorded (world/IMPROVE_W5.md pass 2)
