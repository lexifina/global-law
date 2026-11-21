# GR Greece: FINDINGS (tax year 2025)

Model: `lean/GRTax` (exe `grtax`, euros with cents). Statute: ΚΦΕ ν. 4172/2013 in the official codification
ΑΔΑ Ε7ΔΠΗ-Φ32 (06.04.2026, https://diavgeia.gov.gr/doc/Ε7ΔΠΗ-Φ32), 2025 wordings from its footnotes. Amounts in euros.
Lean names are in `GRTax/Theorems.lean` and `GRTax/Loopholes.lean` (all proved, no `sorry`).

### F1 A hidden 46 % band above the declared 44 % top rate
- kind: statute-fault (design: stacked withdrawal above the top rate)
- households: employees/pensioners with taxable wages above 40,000 € while the art. 16 reduction is still withdrawn:
  to 50,850 € without children, 57,000 € (1 child), 68,000 € (2), 79,000 € (3), 91,000 € (4). Five+ children: no withdrawal.
- amounts: marginal income tax 46 % (44 % + 2 %), METR 53.2 % with EFKA for a single at 1.81 AW (generic METR scan,
  `results/search/metr.md`); from 12,000 € the 22 % band is really 24 %, 28 % → 30 %, 36 % → 38 %.
- provisions: ΚΦΕ art. 15 par. 1 (ν. 4646/2019), art. 16 par. 2 ("μειώνεται κατά είκοσι (20) ευρώ ανά χίλια (1.000) ευρώ"),
  art. 16 par. 1 amounts (ν. 5045/2023 art. 43).
- Lean: `hidden_46_band` (every income in the band), `taper_band_24`, `band_ends`.
- status: confirmed (the OECD BTC lines reproduce the withdrawal to the cent). Visible in OECD marginal-rate tables; not
  found described as a rate above the 44 % top rate in the 4 sources read.

### F2 Five children: the statute gives two amounts (1,780 € or 1,800 €)
- kind: statute-fault
- households: taxpayers with five or more dependent children (tax years 2024+).
- amounts: art. 16 par. 1 second sentence (ν. 5045/2023 art. 43) lists "χίλια επτακόσια ογδόντα (1.780) ευρώ για πέντε (5)
  εξαρτώμενα τέκνα"; the third sentence, left as written by ν. 4646/2019 when the list stopped at four, says "Για κάθε
  επιπλέον εξαρτώμενο τέκνο μετά το τέταρτο, η μείωση του φόρου αυξάνεται κατά διακόσια είκοσι (220) ευρώ": 1,580 + 220 =
  1,800 € for five; six children 2,000 € (list prevails) or 2,020 € (literal). 20 € a year per family.
- provisions: ΚΦΕ art. 16 par. 1 (codif. fn 98-100, p. 196-197).
- Lean: `five_children_conflict`; `credit2024` (list prevails, used) vs `credit2024literal`.
- status: open; the model follows the explicit list. Not checked against an AADE statement. Draft fix (not sent):
  "Για κάθε επιπλέον εξαρτώμενο τέκνο μετά το πέμπτο".

### F3 The 2024 change of the reduction for children (versioned law)
- kind: statute-fault (information: dated change, verified)
- amounts: 1 child 810 → 900, 2: 900 → 1,120, 3: 1,120 → 1,340, 4: 1,340 → 1,580 €, 5 listed at 1,780 € (ν. 5045/2023
  art. 43, from tax year 2024). OECD BTC 2023 vs 2024 confirm both versions (SP67, M100_0).
- Lean: `credit_2023_vs_2024`. status: confirmed.

### F4 Child-benefit notches: 2 € more pay, 671 € less a year
- kind: loophole-new (cliff; the categories are public, the notch per family type is what the scan adds)
- households: married couple, two children, one earner: 34,629 € gross keeps 672 € of επίδομα παιδιού, 34,631 € loses it
  (income after contributions crosses 30,000 € = 15,000 € equivalised). Lone parent of two: 1,008 → 672 € at 17,500 €
  (10,000 € equivalised), 672 → 0 at 26,250 €. Notches of 336 € and 671 € for every family type with children (METR
  above 1,000 % over 50 € windows); timing scan: bunching two years of income gains up to 673 €.
- provisions: ν. 4512/2018 art. 214 par. 4-6 (equivalence scale; three categories, no taper; 70/42/28 and 140/84/56 € a month).
- Lean: `benefit_cliff`, `benefit_category_edges`, `benefit_notch_household`.
- status: confirmed in the model. Art. 214 par. 7 tests "το εισόδημα που αναφέρεται στο εκκαθαριστικό του τρέχοντος
  οικονομικού έτους" (in practice the latest return): moves the notch by a year, not its size. Not found quantified in
  the 4 sources read.

### F5 Unmarried parents: declare the children with the parent who earns least (lead)
- kind: loophole-new (lead; legal status to be confirmed against OPEKA practice)
- households: one-earner couple, two children, 23,907 € wages (0.9 AW). Married: benefit tested on the family income at
  weights 1 + 1/2 + 1/4 + 1/4 (category 3: 672 €), both spouses count the children for art. 16. Not married (no
  cohabitation agreement), children declared by the parent without income: tested on that parent's income alone with the
  lone-parent weight 1/2 for the first child (category 1: 1,680 €); the earner loses the children's reduction (−343 €).
  Net +665 € a year for not marrying. The generic filing-unit scan finds penalties to 807 € and bonuses to 672 € from it.
- provisions: ν. 4512/2018 art. 214 par. 4 ("Ειδικά για τις μονογονεϊκές οικογένειες"); ΚΦΕ art. 11 par. 1(β), art. 16,
  art. 67 par. 4(α), (δ).
- Lean: `unmarried_children_gain`; election `gr_childrenWith` in `elections.json`.
- status: lead. Not found in 4 sources searched (ΚΦΕ codification, ν. 4512/2018, OPEKA A21 page, OECD data). If OPEKA
  treats cohabiting unmarried parents as one family, the gain disappears.

### F6 Rent and earnings split between spouses
- kind: loophole-known
- amounts: 30,000 € gross rent: 7,575 € if one spouse owns it, 5,175 € in halves (separate 15/35/45 % scale per owner,
  art. 40 par. 4 as in force 2020-2025). Wages: equalising a one-earner couple at 3.5 AW saves 9,209 € (unit scan).
- Lean: `rent_split_gain`, `rent_split_le_one_owner`, `separate_le_aggregate`. status: recreated blind (unit scan).

### F7 Art. 5Γ relocation relief: half the employment income exempt for 7 years
- kind: loophole-known (statutory incentive)
- amounts: 80,000 € gross: 22,393.76 € → 7,250.76 € (−68 %); average wage: 3,386.46 → 454.27 €.
- provisions: ΚΦΕ art. 5Γ. Lean: `art5G_gain`. status: modelled (`gr_art5G1/2`); not found blind (scanners do not set it).

### F8 Owner-manager: dividends (22 % + 5 %) beat salary at every profit level
- kind: loophole-known
- amounts: owner scan (`results/search/owner.md`): all-dividend route 25.9 % vs all-salary 29.4 % (0.5 AW) to 54 %
  (10 AW); gain 3,007 € at 1 AW of profit, 74,530 € at 10 AW. Not modelled: a managing partner of an ΙΚΕ/ΑΕ still pays the
  self-employed EFKA categories (fixed monthly amounts).
- provisions: ΚΦΕ art. 58 par. 1(α) (22 % from 2021), art. 40 par. 1 (5 %); employer EFKA 21.79 % (2025).
- Lean: `dividend_route`. status: recreated blind (owner.py).

### F9 Official codification: margin note "2022 έως και 2025", text "2022 έως και 2026"
- kind: gov-error (minor; official codification)
- ΚΦΕ art. 15 par. 7(α) (30 % of certain card-paid service costs deducted) applies "Ειδικά για τα φορολογικά έτη 2022 έως
  και 2026" in the body; the margin heading beside it reads "... 2022 έως και 2025" (codification Ε7ΔΠΗ-Φ32, lines
  2190-2193 of `law/src/kfe_codif.txt`). Classification: error in an official publication, no legal effect.
- Draft note to ΥΠΕΘΟΟ, Διεύθυνση Φορολογικής Πολιτικής (not sent): "Στην κωδικοποίηση ΑΔΑ Ε7ΔΠΗ-Φ32 ο πλαγιότιτλος της
  παρ. 7 του άρθρου 15 αναφέρει 2022-2025, ενώ το κείμενο 2022-2026."

### F10 Art. 28Α presumed minimum for sole traders, which a company escapes
- kind: loophole-known (incorporation avoids it: the rule covers only "ατομική επιχείρηση")
- amounts: 8,000 € declared profit in the tenth year: taxed on 14,907.20 € (12,320 € × 1.21; minimum-wage lead 880 € × 14,
  NOT verified from a primary source): 1,979.58 € instead of 720 €. ν. 5259/2025 art. 187 rewrote par. 2 in December 2025
  "από το φορολογικό έτος 2025" (codif. fn 211): a retroactive change for the year being filed.
- Lean: `art28A_minimum`. status: modelled (inputs `gr_minWageMonthly`, `gr_yearsInBusiness`); not run by the scanners.

### F11 Dead references to the abolished solidarity contribution (art. 43Α)
- kind: statute-fault (convention: harmless)
- Art. 43Α is abolished for all income from 1.1.2023 (art. 72 par. 74, codif. fn 308), yet art. 15 par. 6(β) still
  excludes "το ποσό της εισφοράς αλληλεγγύης του άρθρου 43Α" from real income and arts. 5Β/5Γ still exempt from it.

### F12 Art. 11 still names Ο.Α.Ε.Δ.
- kind: statute-fault (convention)
- Art. 11 par. 1(β) names the Ο.Α.Ε.Δ., renamed Δ.ΥΠ.Α. by ν. 4921/2022 art. 3 par. 1 (codification fn 34 records it).

### M1 OECD married gross = 1.1 × single (marriage allowance)
- kind: model-fix (convention, not an error)
- The OECD's 2023-2025 gross for M100_* is exactly 1.1000 × S100 (2025: 29,218.84 = 1.1 × 26,562.58): the 10 % marriage
  allowance (επίδομα γάμου) of the national general collective agreement. The shared `check.py` / `oecd_check20.py` feed the
  single wage to every type, so their married lines differ by the allowance only (36/56 exact). `oecd/check_gr.py` feeds
  the OECD's own gross: 56/56 exact in each of 2023, 2024, 2025. The OECD chapter text was not read (inferred from data).

### M2 The 2025 rates do not depend on children or age (correction of a lead)
- kind: model-fix
- Reduced rates by children (2nd band 18/16/9/0 %, 3rd 24/22/20/18 %) and 0 % / 9 % for ages up to 25 / 26-30 are
  ν. 5246/2025 art. 3 "από το φορολογικό έτος 2026" (codif. fn 78), not ν. 5162/2024. ν. 5162/2024 art. 12 cut the health
  in-kind contribution by 0.5 points a side from 1.1.2025 (e-ΕΦΚΑ Εγκ. 40/2024): employee 13.87 → 13.37 %. The 2026 scales
  are in the model behind `year: 2026` (S100 −260 €; age 24 −3,160 €; four children on 26,563 €: no tax).

### M3 EFKA ceiling over 14 payments
- kind: model-fix (convention)
- Monthly ceiling 7,572.62 € (e-ΕΦΚΑ Εγκ. 3/2025) applied as 14 × 7,572.62 = 106,016.68 € a year (wages paid in 14
  instalments). Not binding for any OECD type.

### M4 Global law: Greek ΚΦΕ versions 2014-2025 missing
- kind: model-fix (source note)
- Global law holds the ΚΦΕ as the 2013 text and the 2025-12-19 codification only; `read_law` "as in force on 2025-06-30"
  returns the 2013 scale (22/32/42 %) and the 2013 art. 16 (2,100 €). The 2025 law here is read from the codification's
  footnotes instead (official, dated).
