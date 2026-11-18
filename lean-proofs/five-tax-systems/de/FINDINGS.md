# German income tax 2025 (VZ 2025) in Lean — findings

Lean model `lean/DeTax` (statute copied from EStG, SolZG 1995, SGB III/IV/V/VI/XI in their 2025 wording, `law/2025/`).
Referees: the BMF's PAP 2025 (XML pseudo-code, translated to Lean), the BMF's external calculator interface, the BMF's
*Datensammlung zur Steuerpolitik 2026* tables for 2025, and GETTSIM 1.3.2. Each finding says what the law says, what
the other party does, who is affected, the evidence, and who is right with the authority. Theorems named here are in
`lean/DeTax/Theorems.lean` (no `sorry`; `#print axioms`: propext, Classical.choice, Quot.sound only).

## S. The statute itself

**S1. The 2025 tariff formula is not continuous; it jumps at two of its four zone boundaries.** § 32a (1) gives five
formulas with coefficients rounded to the cent. At 12 096 € and 277 825 € adjacent formulas meet exactly; at
17 443 € the zone-3 formula starts 0,16 cent above the end of zone 2, and at 68 480 € the zone-4 line passes
9,41 cent *below* the end of zone 3 (`boundaries`). So between 68 480 € and 68 481 € the formula's marginal rate is
32,6 %, between 42 % on both sides (`boundary_steps`), and the exact formula is not convex there. The rounded tax is
unaffected in practice: one more euro of taxable income always costs 0 or 1 euro, never more (`est_step`), the tax is
monotone (`est_mono`), and over any stretch above the Grundfreibetrag the marginal rate lies between 14 % and 45 %
(`N_marginal`, `est_marginal`). Inside zones 2 and 3 the marginal rate rises exactly linearly, by 2 × 932,30·10⁻⁸ and
2 × 176,64·10⁻⁸ per euro (`N_step_z2`, `N_step_z3`) — the "linear-progressive" design. Certain (kernel-checked).

**S2. Because the result is rounded down, nothing is due up to 12 103 €, not just up to the Grundfreibetrag of
12 096 €** (`est_eq_zero_iff`: tax = 0 ⟺ zvE ≤ 12 103 €). The BMF's Datensammlung 2026 uses two criteria for "no tax":
Tabelle 2.4.1 ("Beginn der Steuerbelastung", 16 836 € of wages for Steuerklasse I in 2025) is the first euro of
Lohnsteuer — the Lean PAP gives exactly 16 836 €, 21 860 € (II/0,5) and 31 586 € (III/0) (`Tests.lean`); Tabelle
2.4.2 ("steuerunbelastete Jahresbruttorente") takes "zu versteuerndes Einkommen = Grundfreibetrag 12 096 €" and so
understates the tax-free pension by the 7 € of zvE the rounding leaves free (about 8,50 € of pension). A definitional
choice, not an error; noted because two tables of one brochure differ. Certain.

**S3. Splitting can cost a couple one euro more than two separate tariffs.** § 32a (5) doubles "den Steuerbetrag, der
sich für die Hälfte ... nach Absatz 1 ergibt", and Absatz 1 Satz 6 rounds that half's tax down before it is doubled.
Spouses with 99 999 € and 100 001 € of taxable income pay 2 × 31 088 = 62 176 € jointly but 31 087 + 31 088 =
62 175 € by the single tariff (`splitting_costs_one_euro`). Among couples whose incomes differ by 2 € this happens
in 38 % of cases (75 467 of 200 000 pairs from 1 000 € to 401 000 €; computed); the largest excess found is 1 €
(scan around 68 480 € and the 200 000 pairs). Couples may choose individual assessment (§ 26 (2), § 26a), so no
couple has to bear it; the tariff alone does not guarantee "splitting never costs more". What does hold for all
incomes: splitting never costs more than 2 € against two single tariffs (`splitting_le_two`), because the exact formula
is discretely convex up to 9,57 cent (`conv_defect`: its steps never decrease except at three known places,
`step_cmp`); within one zone the bound is 1 € (`splitting_zone3`, `splitting_zone4`). Certain (counterexample and
theorems).

**S4. The Kindergeld/Freibetrag Günstigerprüfung does not have one crossover: around it the outcome flips back and
forth, and the BMF prints the last flip.** § 31 Satz 4 deducts the Freibeträge (9 600 € per child for couples) when
they save more tax than the Kindergeld (3 060 €). Because each tax amount is rounded down to the euro, for a married
couple with one child the Kindergeld wins for every Einkommen up to 84 439 €, the Freibeträge for every Einkommen
from 84 548 €, and in between the result changes 29 times (84 462 → Freibetrag, 84 464 → Kindergeld, …)
(`kg_crossover_joint`, `kg_flips`, `kg_permanent_joint`). The BMF's Datensammlung 2026, Tabelle 2.8.3, prints
"Einkommensgrenzen, ab denen der Kinderfreibetrag dauerhaft günstiger ist" for 2025: 84 548 € (Bruttolohn 101 455 €)
— exactly the last flip, now a theorem; single parents 44 644 € (Bruttolohn 62 175 €, `kg_permanent_single`); with two
children 94 148 € and 54 244 €, which are the one-child values plus 9 600 € (`kg_two_children`) — what the child-by-child
rule gives (see G7). The Lean model reproduces all four printed incomes from the printed Bruttolöhne to the euro, and
switches exactly at 101 455 € (`Tests.lean`). Certain.

**S5. The highest combined marginal rate below the contribution ceilings is 53,23 %, not the 42 % or 45 % of the
tariff.** For a single childless employee between 90 300 € and 96 600 € of wages — above the health-insurance ceiling
(66 150 €), below the pension ceiling (96 600 €), taxable income in zone 4, tax in the Soli Milderungszone — each euro
costs 9,3 % RV + 1,3 % AV + 42 % × 90,7 % income tax (RV is deductible, AV is not because the Basis-KV/PV already
exceed the 1 900 € cap of § 10 (4)) + 11,9 % of that tax as Soli: 0,106 + 0,907 × 0,42 × 1,119 = 0,53227186
(`marginal_peak`, proved for every wage in the band, rounding included within 1,70 €), and it is the highest: below the
health-insurance ceiling the rate is at most 50,7 % (`marginal_low`, 24 001–66 150 €) and between the ceilings at most
the same 53,23 % (`marginal_mid`, 66 150–96 600 €). Above the pension ceiling the
rate falls to 47,0 % (42 % × 1,119: the Soli Milderungszone, `soli_band_rate`), and above 37 094 € of tax to 44,31 %
(42 % × 1,055). The model's profile for this employee: 0 % (Minijob), 29,7 % (Übergangsbereich, contributions only),
41–50 % (25 000–66 000 €), 44,6–48,8 % (66 150–90 000 €), 53,2 % (90 300–96 600 €), 47 % (96 600–135 000 €), 44,3 %.
For a one-earner couple with two children the peak is 42,7 %. Certain for the band (theorem); the profile is computed.

**S6. The Soli: never more than 5,5 % of the tax, 11,9 cent per euro of tax in the Milderungszone, the full 5,5 % from
37 095 € (74 190 € jointly).** `soli_le_rate`, `soli_freigrenze` (one euro of tax above the Freigrenze costs 11 cent,
not the 5,5 % of the whole tax a bare Freigrenze would charge), `soli_milderung_step`, `soli_full`, `soli_zone_2025`.
The joint end of the zone is ⌈2 × 37 094,53⌉ = 74 190 €, one euro above twice the single end. Certain.

**S7. The § 32d (6) comparison includes the surtaxes, so the flat rate it is compared with is 26,375 %, not 25 %.**
"wenn dies zu einer niedrigeren Einkommensteuer einschließlich Zuschlagsteuern führt": below the Soli Freigrenze the
tariff carries no Soli but the Abgeltungsteuer always carries 5,5 % (SolZG § 3 (3) Satz 2, § 4 Satz 4). A pensioner
with a 26 % marginal rate is better off with capital income in the tariff (sample `r1` in `samples/`). Certain.

## P. The BMF's executable pseudo-code (PAP 2025) and calculator

**P1. The PAP computes exactly § 32a.** `UPTAB25` (BigDecimal pseudo-code, scales and ROUND_DOWN as published) equals
the statute's formula for every whole-euro income, negative ones included (`uptab25_eq_est`), and Steuerklassen I–IV
apply it to the zu versteuernder Jahresbetrag, Steuerklasse III as the Splitting-Verfahren 2·⌊f(⌊X/2⌋)⌋
(`pap_mlst`, `pap_class3_is_splitting`) — § 39b (2) Satz 6. Certain.

**P2. Steuerklassen V and VI: the PAP evaluates the tariff at amounts with cents, where § 39b (2) Satz 7 with § 32a (1)
Satz 1 rounds down to the euro.** § 39b (2) Satz 7: "aus dem Zweifachen des Unterschiedsbetrags zwischen dem Steuerbetrag
für das Eineinviertelfache und dem Steuerbetrag für das Dreiviertelfache des zu versteuernden Jahresbetrags nach § 32a
Absatz 1"; § 32a (1) Satz 1: the tax "bemisst sich nach dem auf volle Euro abgerundeten zu versteuernden Einkommen".
`UP5_6` computes `X = ZX × 1,25` and `ZX × 0,75` "mit 2 Dezimalstellen" and feeds them to UPTAB25 unrounded. For
ZX = 13 803 € the PAP gives 1 940 €, the words 1 938 € (`pap_class5_cents`). Over ZX = 0 … 299 999 €, `UP5_6` differs
on 71 770 amounts (always by 2 €) and the class V/VI annual Lohnsteuer `MST5_6` on 1 677 (±2 €). Withholding only (the
assessment corrects it). Moderate confidence: one can read "nach § 32a Absatz 1" as pointing to the formula alone.

**P3. The BMF's calculator agrees with the Lean PAP.** The external interface of bmf-steuerrechner.de ("für die
automatisierte, maschinelle Prüfung eines Lohn- und Einkommensteuerrechners gegen den des BMF"; its terms allow program
tests only; code published on the interface page; 61 s between requests as robots.txt asks): see RESULTS.md for the
count (44 boundary cases and random cases over all Steuerklassen, pay periods, children, private insurance, church tax,
Altersentlastungsbetrag, Freibeträge). Every answer equals the Lean PAP on LSTLZZ, SOLZLZZ, BK, VFRB, WVFRB.

## G. GETTSIM 1.3.2 against the statute

GETTSIM (pip `gettsim` 1.3.2, policy date 2025-07-01) on 10 000 random households (`runs/g10k*`; adapter
`harness/gettsim_run.py`). With the statute (Lean default) the total burden differs by more than 1 € in 4 717 households
(GETTSIM higher in 4 126). Every difference falls into one of the readings below: with them switched on in Lean
(`detax --gettsim-compat`), Lean reproduces GETTSIM's total burden within 1 € for 9 994 of 10 000 households (largest
gap 1,13 €; the remainder is cent rounding of contributions, which GETTSIM keeps as unrounded floats). Effects of each
reading alone on the same 10 000 households (`--g-tariff`, `--g-vors`, `--g-alte`, `--g-sv`, `--no-32d6`,
`--all-children-together`; a synthetic draw rich in pensioners and capital income, not Germany's population):

| # | GETTSIM reading | households changed | effect on the burden | authority / verdict |
|---|---|---|---|---|
| G1–G3 | tariff | 2 906 | −1 € … +2,24 € | statute, BMF PAP: Lean |
| G4 | § 24a | 1 948 | −568 € … +1 786 € | statute, PAP: Lean |
| G5 | Vorsorge | 2 166 | −4 265 € … +251 € | statute: Lean |
| G6 | no § 32d (6) | 1 243 | +0,16 € … +13 236 € | statute: Lean |
| G7 | all children together | 163 | +1 € … +645 € | Bundestag WD, BMF table: Lean |
| G8 | contributions | 1 425 | +0,59 € … +4 213 € | SGB: Lean (G8c a reading) |

**G1. GETTSIM does not use the statute's coefficients.** It stores the marginal rates at the thresholds (14 %, 23,97 %,
42 %, 45 %) and derives each quadratic term as "(rate_fiv - rate_iv) / (2 * (upper_thres - low_thres))"
(`einkommensteuer.py`, `parameter_einkommensteuertarif`), with continuous intercepts: 0,0997/10 694 = 932,2985·10⁻⁸ and
0,1803/102 074 = 176,6365·10⁻⁸ instead of the statute's 932,30·10⁻⁸ and 176,64·10⁻⁸. On every whole-euro income
0 … 400 000 €, GETTSIM's own tariff is 1 € below § 32a on 1 643 incomes (1 639 in zone 3), equal elsewhere
(`harness/tariff_gettsim.py`). The statute (and the PAP, P1) side with Lean.

**G2. GETTSIM's splitting is ⌊2·f(X/2)⌋, not 2·⌊f(⌊X/2⌋)⌋.** It divides the joint income by two without rounding the
half down to the euro (§ 32a (1) Satz 1) and rounds once after doubling (instead of rounding the half's tax, Satz 6,
then doubling, (5)). On the 800 001 joint incomes 0 … 800 000 € it charges 1 € more on 386 227, 2 € more on 79 737 and
1 € less on 1 643 — 58 % of all joint incomes. § 32a (5) with (1) Sätze 1 and 6, the BMF's PAP (Steuerklasse III:
`X = ZVE / KZTAB` abgerundet, `ST = UPTAB25(X) × KZTAB`; `pap_class3_is_splitting`) and the Datensammlung's definition
("das Zweifache des Steuerbetrags, der sich nach der ... Tarifformel für die Hälfte ... ergibt") side with Lean.

**G3. GETTSIM applies the tariff to the taxable income with its cents** (`betrag_mit_kinderfreibetrag_y_sn` takes the
unrounded `zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn`; only the reported zvE is rounded). § 32a (1) Satz 1
rounds the income down first. Part of the 2 906 households of the tariff row.

**G4. GETTSIM's Altersentlastungsbetrag (§ 24a) has three departures.** (a) Its table is keyed by birth year as
"Kalenderjahr − 64" (`alter.py`: `int(k) - altersentlastungsbetrag_altersgrenze`), so a person born in year B gets the
row of B + 64 — the year of the 64th birthday — instead of B + 65, "das auf die Vollendung des 64. Lebensjahres
folgende Kalenderjahr" (§ 24a Satz 5): one row too generous for every cohort (born 1960: 13,6 %/646 € instead of
13,2 %/627 €). The BMF's PAP takes `AJAHR` = "Auf die Vollendung des 64. Lebensjahres folgende Kalenderjahr" and
`K = AJAHR − 2004` (MRE4ALTE), as Lean does. (b) Nobody born before 1941 (aged 85 and over in 2025) gets anything;
the PAP gives them the first row (`AJAHR < 2006 → K = 1`: 40 %, 1 900 €), as Lean does. (c) The base includes gross
capital income even when it is taxed at 25 % under § 32d (1), which § 2 (5b) excludes from "Einkünfte" for every
provision of the EStG. Lean is right on all three.

**G5. GETTSIM's Vorsorgeaufwendungen (§ 10 (1) Nr. 2, 3, 3a; (3), (4)).** (a) The pension cap of § 10 (3) is applied to
the employee's RV and private contributions only; the statute counts the tax-free employer share against the cap
(§ 10 (1) Nr. 2 Satz 6 "hinzuzurechnen", (3) Satz 5 "vermindert um den nach § 3 Nummer 62 steuerfreien
Arbeitgeberanteil"), so GETTSIM over-deducts by up to the employer share (up to 8 984 €) when Basisrente
contributions are large. (b) It cuts 4 % from every KV contribution, also pensioners' and the self-employed's on the
ermäßigter Beitragssatz; § 10 (1) Nr. 3 Buchstabe a Satz 4 cuts only "wenn sich aus den Krankenversicherungsbeiträgen
... ein Anspruch auf Krankengeld ... ergeben kann". (c) It rounds the deduction up to the euro, citing "§ 10 Abs. 3
EStG", which rounds the Höchstbeitrag, not the deduction. Lean is right on (a) and (b); (c) has no statutory basis.

**G6. GETTSIM has no § 32d (6) Günstigerprüfung**: capital income is always taxed at 25 % (+ Soli), even when the
tariff, applied on request, would be lower. 1 243 of the 10 000 households pay more, up to 13 236 €. Statute: Lean.

**G7. GETTSIM compares the Freibeträge of all children with all the Kindergeld at once**
(`kinderfreibetrag_günstiger_sn`). The procedure is child by child: "Die Günstigerprüfung ist für jedes Kind,
beginnend mit dem ältesten, vorzunehmen. Kommen für das älteste Kind die Freibeträge zum Abzug, vermindern sie das zu
versteuernde Einkommen, das bei der Günstigerprüfung für das nächste Kind herangezogen wird. Deshalb ist es möglich,
dass für ein oder mehrere Kinder die Freibeträge, für weitere Kinder jedoch der Kindergeldanspruch günstiger ist"
(Deutscher Bundestag, Wissenschaftliche Dienste, WD 4 - 3000 - 065/24, 26.8.2024, Abschnitt 2.3; `refs/wd4_065_24.pdf`).
The BMF's own printed two-children thresholds (Datensammlung 2026, Tabelle 2.8.3) are the one-child thresholds plus
9 600 €, which only the child-by-child rule gives (`kg_two_children`). The all-together reading makes 163 of 10 000
households pay 1–645 € more. Lean is right.

**G8. GETTSIM's employee contributions.** (a) No exemption after the Regelaltersgrenze: employees past it who draw a
full old-age pension are free of RV (SGB VI § 5 (4) Nr. 1) and all past it of AV (SGB III § 28 (1) Nr. 1); GETTSIM
charges both. (b) No exemption from the PV childless surcharge for members born before 1 January 1940 (SGB XI § 55 (3)
Satz 2). (c) The statutory pension's KV/PV is capped separately from the wage: SGB V § 230 Satz 2 ("getrennt von den
übrigen Einnahmearten bis zur Beitragsbemessungsgrenze") supports GETTSIM's levy, but § 231 (2) refunds on application
"soweit sie auf Beträge entfallen, um die die Rente zusammen mit den übrigen ... Einnahmen ... die
Beitragsbemessungsgrenze überschritten hat"; Lean reports the burden net of that refund (a reading: both defensible,
Lean's is what the member ends up paying if she applies). (d) Contributions are not rounded to the cent. Lean is right
on (a) and (b); (c) is a reading.

**G9. Not a bug: single parents.** GETTSIM gives each parent one Kinderfreibetrag and asks users to override it for
single parents ("Users should overwrite this function if there are single parents in the data who should receive two
instead of one Kinderfreibeträge"); the adapter does so.

## O. OECD Taxing Wages 2026 (year 2025)

The OECD's member-country table for Germany (SDMX API, dataflow `DSD_TAX_WAGES_COU@DF_TW_COU`, `refs/oecd/`; the
oecd.org web pages refuse automated access and were not used): average wage 66 700,04 €, eight households. For seven
the Lean model gives the OECD's employee contributions (within one cent), Vorsorgeaufwendungen (the OECD rounds them up
to the euro), taxable income, income tax with Soli (to the cent, 29 650,61 € with the Milderungszone for 167 % AW)
and Kindergeld (`Tests.lean`).

**O1. The eighth, a two-earner couple (100 % + 67 % AW) with two children, differs by 54 €: the OECD compares all
children's Freibeträge with all the Kindergeld at once.** Its Einkommen, 87 682 €, lies between the one-child and the
two-children thresholds of the BMF's Tabelle 2.8.3 (84 548 €, 94 148 €). Child by child (G7), the first child's
Freibeträge save 3 114 € > 3 060 €, so they are deducted and the second child keeps the Kindergeld: tax 14 032 €,
Kindergeld kept 3 060 €. The OECD keeps the Kindergeld for both (tax 17 146 €, credit 6 120 €), 54 € more; Lean with
`perChild := false` reproduces the OECD to the cent. Authority as in G7 (Bundestag WD 4-065/24; the BMF's own
two-children thresholds): Lean.

## R. Readings where the law leaves a choice (Lean's choice stated; not findings)
- Contributions computed on the annual wage (the law computes per month; equal monthly pay assumed), each annual
  amount rounded half up to the cent; Übergangsbereich formula on annual amounts.
- Vorsorgeaufwendungen kept in cents; the zvE rounded down once (§ 32a (1) Satz 1).
- Soli: one truncation to the cent of the sum of the tariff part and the 5,5 % on the Abgeltungsteuer (SolZG § 4 Satz 3).
- Altersentlastungsbetrag rounded up to the euro, as the PAP's MRE4ALTE does (§ 24a is silent).
- Pension: statutory Leibrente begun in the year the person turned 65 (2025 if younger); the Besteuerungsanteil of that
  year applied to the 2025 pension (the law fixes the tax-free part in euros from the second year, so later increases
  are fully taxable — the BMF's Tabelle 2.4.2 does that; the household record has no pension history).
- KVdR: the § 231 (2) SGB V refund is assumed claimed (G8c).
- Childless (PV surcharge) = no child in the household; the Regelaltersgrenze taken as reached all year from age 67.
- Self-employed: freelance (§ 18, no Gewerbesteuer); voluntary GKV + PV only when self-employment is the main activity.
- Married couples assessed jointly; household-level income split equally between two adults; a single adult has both
  parents' child allowances (other parent absent: § 32 (6) Satz 3) and § 24b; two unmarried adults are both parents
  (half allowances, half Kindergeld each, § 31 Satz 4 Halbsatz 2). The BMF's Tabelle 2.8.3 makes the same single-parent
  assumption (its 44 644 € threshold needs the full allowances).
- Wages up to 6 672 € a year are a Minijob with the employer's 2 % flat tax (§ 40a (2)) and no employee contribution
  (RV exemption on request, SGB VI § 6 (1b)).

## L. Corrections to the Lean model made because of the referees
- L1. Regelaltersgrenze: first exempted from RV/AV from age 66; the 1959 cohort reaches it at 66 and 2 months, so now
  from 67 (GETTSIM comparison).
- L2. PV childless surcharge in the Übergangsbereich: now on the contribution base BE (SGB XI § 58 (1) Satz 3, § 55 (3)),
  was on the reduced employee base (GETTSIM comparison; GETTSIM right).
- L3. Household amounts split between two unmarried adults in cents, not whole euros (lost 1 € on odd amounts).
- L4. Harness: single parents were first entered twice as the child's parent in GETTSIM, which doubled the PV child
  reductions; fixed by overriding GETTSIM's Freibetrag count instead.

## U. Not modelled
Kirchensteuer as Sonderausgabe (§ 10 (1) Nr. 4); Gewerbesteuer and § 35; Teileinkünfteverfahren and business capital
income; loss carry-back/forward (§ 10d); außergewöhnliche Belastungen (§§ 33–33b); Kinderbetreuungskosten; Riester
(§ 10a); Versorgungsbezüge of civil servants (§ 19 (2)); Witwensplitting (§ 32a (6)); Progressionsvorbehalt (§ 32b);
private health insurance; the Saxony PV rule; partial-year children; the Kappung of the Kirchensteuer.
