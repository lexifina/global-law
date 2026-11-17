# What the authorities say: the "departs from the law" points (17 November 2026)

Question: several findings (FINDINGS.md F1, F2, F5, R, F3; PAS.md W1–W6) say the DGFiP's program and its simulator
depart from the words of the CGI while the Lean model follows them. Until now "the law" was our own reading. This file
records what the published authorities say: the DGFiP's own doctrine (BOFiP-Impôts), the administrative courts,
and ministers' answers to written parliamentary questions. Every source below was obtained as bulk open data or as
pages served normally; nothing behind a challenge was fetched.

Files on the build server: raw data `~/fr/data/authority/raw/`, grep-able text `~/fr/data/authority/text/{bofip,bofip_hist,courts,an,senat}/`,
per-issue hit lists `~/fr/data/authority/hits/*.tsv`, scripts `~/fr/harness/auth_*.py`.

## 1. Sources

| Source | URL | Fetched | Size | Coverage |
|---|---|---|---|---|
| BOFiP-Impôts, publications en vigueur (DGFiP open data, listed on data.gouv.fr "BOFiP Impôts - publications en vigueur") | `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/bofip-vigueur/exports/json` | 2026-11-17 13:50 CET (dataset modified 2026-11-12) | 221 452 518 B | 9 173 records: 6 367 doctrine documents in force + 2 806 "Actualités" 2012–2026; in-force versions only |
| BOFiP archived versions (pages served normally by bofip.impots.gouv.fr, 2 s apart) | `https://bofip.impots.gouv.fr/bofip/11247-PGP.html/identifiant=BOI-IR-PAS-20-20-10-<date>` and `11256-PGP` for -20 | 2026-11-17 | 13 pages, 1.2 MB | BOI-IR-PAS-20-20-10: 20180515, 20181025, 20200515, 20210330, 20220516, 20230626, 20240618, 20250507, 20260407; BOI-IR-PAS-20-20-20: 20180515, 20200515, 20220516, 20250507 |
| DILA JADE (administrative case law), full dump | `https://echanges.dila.gouv.fr/OPENDATA/JADE/Freemium_jade_global_20261108-140000.tar.gz` | 2026-11-17 | 1 321 670 142 B | 573 525 decisions (Conseil d'État, CAA, some TA), dump of 2026-11-08; daily increments 9–16 Nov not taken |
| Justice administrative open data (every decision since 2021/2022) | `https://opendata.justice-administrative.fr/{DCE,DCA,DTA}/<yyyy>/<mm>/*.zip` (176 monthly zips, 1 s apart) | 2026-11-17 | 4 438 121 533 B | CE 2021-06 → 2026-11 (40 322 decisions), CAA 2022-03 → (129 245), TA 2022-06 → 2026-11 (1 005 427) |
| Assemblée nationale written questions, legislatures 15–17 (2017–2026) | `https://data.assemblee-nationale.fr/static/openData/repository/{15,16,17}/questions/questions_ecrites/...json.zip` | 2026-11-17 | 110 030 949 + 46 599 706 + 51 837 843 B | 84 170 questions, 10 375 about tax kept as text |
| Sénat questions (full SQL base) | `https://data.senat.fr/data/questions/questions.zip` | 2026-11-17 (Last-Modified 2026-11-17 02:33 GMT) | 283 880 996 B | 294 455 questions deposited 1978-02-14 → 2026-11-12, with answers; 9 597 about tax kept as text |
| Statute text and history | global-law record of the consolidated CGI on the build server, `~/fr/refs/france-law` (commit 35fa835f8e, 2026-11-16) | — | — | art. 204 H, 81 quater, 199 quater C, 223 sexies, 1417, 197 C |

Court decisions were filtered (`harness/auth_courts_filter.py`): a decision is kept when it mentions income tax / the
CGI and at least one of: 199 quater C, 223 sexies, 204 E/H/M, 1657, 81 quater, 197 C, taux effectif, article 193,
décote, hauts revenus, cotisations syndicales, 151-0, prélèvement à la source, taux de prélèvement, "euro le plus
proche", seuil de (mise en) recouvrement, heures supplémentaires. 1 748 519 decisions scanned, 6 072 kept. The
per-issue searches (`harness/auth_issue_search.py`, hit lists in `hits/`) were then run over all four corpora and
every hit was read; the counts are in the summary table.

Not obtained:
- Assemblée nationale legislature 14 (2012–2017): the server cut the 134 MB file at 42.9 MB on each of 30 resumed
  attempts. The Sénat base covers that period.
- Légifrance and economie.gouv.fr: behind Cloudflare, not attempted. Statute text comes from the global-law record.
- Parliamentary reports and exposés des motifs: not searched. They are not in the open-data dumps above (the AN and
  Sénat open data hold the questions; report texts are separate web pages). None of the verdicts below turns on
  legislative intent.
- Judilibre (judicial courts): income-tax assessment disputes go to the administrative courts, so not searched.

Two general points from the case law frame every W point:
- **The withholding rate only governs advance payments.** "Il résulte de ces dispositions que le prélèvement à la
  source constitue une modalité obligatoire de règlement d'acomptes sur le montant de l'impôt sur le revenu dû par un
  contribuable. [...] S'il excède l'impôt dû, l'excédent est restitué après liquidation de l'impôt." (TA Poitiers,
  7 novembre 2023, n° 2200177, ¶ 2; same reasoning in TA Lille, 21 juillet 2022, n° 2002202). A wrong rate shifts
  cash between months; it does not change the tax finally due.
- **Taxpayers cannot rely on BOFiP doctrine against a withholding.** "La décision refusant de restituer une somme
  retenue à la source [...] ne constituant ni un rehaussement [...], M. [...] ne saurait se prévaloir, sur le
  fondement de l'article L. 80 A du livre des procédures fiscales, [...] des énonciations [...] du bulletin officiel
  des finances publiques" (TA Lille, 21 juillet 2022, n° 2002202, ¶ 9).

No court decision in the corpus rules on how the household or individualised rate is computed (the 19 decisions
citing 204 H/204 M are about default rates applied by employers, refunds and timing).

## 2. Point by point

### F1. Union-dues credit, 5 000 € vs 7 500 € overtime limit (art. 199 quater C, 81 quater), income 2022–2024
- **Doctrine.** BOI-IR-RICI-20-20160902 § 140: "Le crédit d'impôt prévu à l'article 199 quater C du CGI se calcule
  sur le montant des cotisations pris dans la limite de 1 % du revenu brut désigné à l'article 83 du CGI, après
  déduction des cotisations et contributions mentionnées aux 1° à 2° ter de l'article 83 du CGI." § 150 lists what
  enters the 1 % base (salaries, benefits, pensions, less social contributions). It predates the 2019 overtime
  exemption and says nothing about it. The in-force BOFiP has no commentary at all on the 2019+ overtime exemption
  (art. 81 quater as restored by loi n° 2018-1213, raised by lois n° 2020-473 and 2022-1157): BOI-RSA-CHAMP-20-50-20
  still covers the 2007–2012 regime, and no Actualité since 2019 mentions heures supplémentaires.
- **Courts:** 12 decisions cite 199 quater C, none about overtime or the 1 % base. **Questions:** 61 on union dues
  (AN 29, Sénat 32), none about overtime.
- **Verdict: unaddressed.** The words are plain: art. 81 quater exempts up to 7 500 € for income 2022 onwards, and
  exempt pay is not part of the art. 83 income. The DGFiP's own income-2025 code switched to the 7 500 € limit
  (COD1GHRET). No authority supports the 5 000 € limit for 2022–2024.
- **Wording:** "departs from the law" survives. It is best framed as a lag that the DGFiP corrected: "for income
  2022–2024 the DGFiP's program, and its production calculator, still used the old 5 000 € limit; the income-2025
  code uses 7 500 €."

### F2. CEHR prorated when flat-levy (versement libératoire) income is present (art. 223 sexies)
- **Doctrine on the base.** BOI-IR-CHR-20170711 § 40: "La contribution est assise sur le revenu fiscal de référence
  du foyer fiscal". § 50: the RFR is "majoré de [...] revenus et profits soumis aux prélèvements ou versements
  libératoires". § 280, Remarque: "Les revenus exonérés d'impôt sur le revenu en France en application des
  conventions fiscales internationales, y compris ceux pris en compte pour le calcul du taux effectif en matière
  d'impôt sur le revenu, sont exonérés de la contribution exceptionnelle sur les hauts revenus." The 2026 CDHR
  doctrine says the same (BOI-IR-CDHR-10-20260630, § 100 and the remark before § 190). The only exclusion the DGFiP
  publishes is for **treaty-exempt** income.
- **Courts on the proration method.** CE, 10 juillet 2019, n° 412624 (9e-10e ch. réunies, mentioned in the tables),
  ¶ 5–6. The administration "a ensuite calculé une cotisation fictive de contribution exceptionnelle en appliquant au
  revenu fiscal de référence ainsi obtenu les taux prévus à l'article 223 sexies [...], puis a neutralisé les revenus
  exonérés d'impôt en France en multipliant cette cotisation fictive par le rapport entre le total des revenus de
  l'intéressé, minoré des revenus exonérés, sur le total de ses revenus". The Conseil d'État upheld it for income
  exempted by a tax treaty: § 280 "n'interdi[t] pas de les prendre en compte pour la détermination du taux
  d'imposition appliqué aux revenus soumis en France à cette contribution **lorsque la convention le permet**".
  TA Paris, 29 janvier 2026, n° 2316179 applies the same method to Belgian salaries and rests it on art. 19, B, 3 of
  the Franco-Belgian treaty.
- So M's CHRTEFF (CEHR on the whole RFR, scaled down by a ratio) is the administration's treaty method. The Conseil
  d'État accepted it because a treaty allowed it. M applies it whenever the effective-rate indicator is set, and
  flat-levy micro income sets that indicator. BOI-IR-LIQ-20-30-30-20120912 § 20 does list that income among the
  effective-rate cases, but only for income tax under art. 197 C. Flat-levy income is French income, not exempt;
  art. 1417, IV, 1°, c puts it in the RFR; BOI-IR-CHR § 50 puts it in the CEHR base. No treaty applies.
- **Questions:** none on CEHR and flat-levy or effective-rate income. The issue search matched 1 AN and 2 Sénat
  questions, about income statistics and inequality; the 6 questions that name the CEHR are about its yield or tax
  policy.
- **Verdict: explained by doctrine and case law, and they support Lean.** The DGFiP's published doctrine includes
  flat-levy income in the CEHR base with no proration. The case law accepts proration only for treaty-exempt income,
  and on a treaty basis. Nothing found extends it to flat-levy income.
- **Wording:** survives, and can be stated more firmly than "open reading question": "the program applies to
  micro-entrepreneurs' flat-levy income a proration that the DGFiP's doctrine and the Conseil d'État (n° 412624)
  reserve for income exempted by a tax treaty; art. 223 sexies and the DGFiP's own BOFiP tax the whole RFR, flat-levy
  income included." Keep "we found no text"; the DGFiP may hold an unpublished reading.

### F5. Amounts ending .49995–.49999 rounded up (art. 193, 1657, 1)
- **Doctrine.** BOI-IR-LIQ-20-20-40-20180704 § 50: "Le calcul de la base d'imposition et de l'impôt se fait à
  l'euro le plus proche (CGI, art. 193 et CGI, art. 1657, 1) : - les fractions d'euro inférieures à 0,50 € sont
  négligées ; - les fractions de 0,50 € égales ou supérieures à 0,50 € sont comptés pour 1 €. Tout élément venant
  modifier les bases (abattements, etc.) ou les cotisations (décotes, crédits d'impôt, réductions d'impôt, etc.) est
  arrondi à l'euro le plus proche." It allows no margin.
- **Courts and questions:** the hits only quote art. 193 (TA Poitiers n° 2200177, TA Pau 29 mars 2024 n° 2200208) or
  concern employers' rounding of withholding remittances (Sénat question n° 10253, answer JO Sénat 22 août 2019
  p. 4298; AN 15e lég. n° 17063). None concerns a margin.
- **Verdict: doctrine restates the statute; unaddressed as to the margin.**
- **Wording:** survives. "Production rounds 0.49996 up where art. 193 and the DGFiP's own BOFiP (BOI-IR-LIQ-20-20-40
  § 50) round it down." Say it is a floating-point safety margin in the program, worth 1–2 € on rare returns, not a
  reading of the law.

### W1. Nil rate when the tax is under 61 € (art. 204 H, I vs 1657, 1 bis)
- **Doctrine on the rate.** BOI-IR-PAS-20-20-10-20260407 § 10 takes the tax "résultant de l'application des règles
  prévues aux 1 à 4 du I de l'article 197 du CGI" with no 61 € rule. Every archived version 2018–2026 brings the 61 €
  and 12 € thresholds of art. 1657 into **one** place only, the first condition of the zero rate in 204 H, II, whose
  text says "mis en recouvrement": § 150 (2026), "après application des seuils de mise en recouvrement prévus au 1 bis
  et au 2 de l'article 1657 du CGI". Nothing in BOI-IR-PAS-20-20-10 or -20 sets the rate to zero for a tax under
  61 €.
- **Doctrine on the 61 € rule itself.** BOI-IR-LIQ-20-20-40-20180704 § 90: "La non-mise en recouvrement des
  cotisations inférieures au seuil légal ne constitue pas une exonération d'impôt sur le revenu". The tax under 61 €
  still exists; it is not collected.
- **Ministerial answer** (AN 15e lég., question n° 4893, M. Jean-Yves Bony, answer JO 13 novembre 2018): the
  numerator is the tax "après décote et réfaction [...] mais avant imputation des réductions et des crédits d'impôt".
  It does not mention 61 €.
- **Courts:** nothing on this point.
- **Verdict: explained by doctrine, and the doctrine supports Lean.** By applying art. 1657 in 204 H, II only, the
  BOFiP leaves it out of 204 H, I, and its own § 90 says an uncollected tax is not a nil tax.
- **Wording:** survives, and is stronger: "production transmits a nil rate where the statute, and the DGFiP's own
  published method, give 0.1–0.3 %." Add that the rate only sets advances: the tax finally due is unchanged, and a
  tax under 61 € is not collected anyway.

### W2. Rate rounding margin (art. 204 H, I, 3), income 2020–2024
- **Doctrine.** BOI-IR-PAS-20-20-10-20260407 § 20: "Le taux de prélèvement est arrondi à la décimale la plus proche.
  La fraction de décimale égale à 0,50 est comptée pour un. Exemple : Si le calcul aboutit à un taux de 6,85 %, le
  taux de prélèvement retenu sera de 6,9 %." BOI-IR-PAS-20-20-20 § 10 refers to it for individualised rates.
- **Courts and questions:** the hits concern employers' rounding of remittances and default-rate brackets; none
  concerns the computed rate.
- **Verdict: doctrine restates the statute; the margin is unaddressed.**
- **Wording:** survives, as for F5: a program margin that turns 25.44996 % into 25.5 % where the statute and the
  BOFiP give 25.4 %. It is gone in the income-2025 code.

### W3. 204 H, II zero-rate threshold: M uses "the next year's figure". **Authority against Lean.**
- **Statute.** Art. 204 H, II, 2° gives a figure per part and adds: "Le montant des revenus prévu au 2° du présent II
  est indexé chaque année comme la limite supérieure de la première tranche du barème de l'impôt sur le revenu" (same
  words in every version since 2018). The figure printed in the consolidated code is only updated afterwards, by
  codification decrees. The global-law record shows 25 000 € until 11 June 2021, then 25 654 € (décret n° 2021-744),
  and so on; each decree records the previous year's indexation.
- **Doctrine, every year.** The archived BOI-IR-PAS-20-20-10 versions state the threshold "pour la détermination du
  taux applicable entre le 1er septembre N et le 31 août N+1 (revenus de l'année N−1)":

  | BOFiP version | Rates from 1 Sept | Income | Threshold per part (BOFiP) | M `RFRPARQF` | Codified figure in force on 1 Sept (PAS.md) |
  |---|---|---|---|---|---|
  | 20200515 | 2019 | 2018 | 25 400 € | — | 25 000 € |
  | 20210330 | 2020 | 2019 | 25 654 € | — | 25 000 € |
  | 20220516 | 2021 | 2020 | 25 705 € | 25 705 | 25 654 € |
  | 20230626 | 2022 | 2021 | 26 065 € | 26 065 | 25 705 € |
  | 20240618 | 2023 | 2022 | 27 473 € | 27 473 | 26 065 € |
  | 20250507 | 2024 | 2023 | 28 792 € | 28 792 | 27 473 € |
  | 20260407 | 2025 | 2024 | 29 310 € | 29 310 | 28 792 € |
  | 20260407 (Remarque) | 2026 | 2025 | 29 574 € | 29 574 | 29 310 € |

  § 180 (2026) explains it: "Le plafond de revenu fiscal de référence mentionné au II de l'article 204 H du CGI est
  indexé chaque année, le 1er septembre, comme la limite supérieure de la première tranche du barème [...].
  L'indexation est fonction de l'évolution de la limite supérieure de la première tranche du barème de l'imposition
  des revenus de l'année précédente par rapport à celle applicable pour l'imposition des revenus de l'avant-dernière
  année." Example: 28 792 € × 1.018 (the 2025 indexation of the scale) = 29 310 €.
- **Verdict: explained by doctrine, against Lean.** M and production use the BOFiP figure in all six years. The
  statute's own indexation clause produces that figure; the number printed in the code lags because codification
  decrees record each indexation later. Lean read the printed number and ignored the indexation clause.
- **Wording:** drop W3 as a departure. Say instead: "the per-part threshold printed in the consolidated CGI lags one
  indexation behind the threshold the law actually sets; the DGFiP's program, its simulator and its BOFiP all use the
  indexed figure." Lean should take the indexed figures (or the BOFiP's) for 204 H, II.

### W4. Décote in the individualised rate (art. 204 M, 2 → 197, I, 4). **Authority against Lean's main reading.**
- **Ministerial answers.** AN 16e lég., question n° 13 (Mme Marie-Pierre Rixain), answer JO AN 17 janvier 2023
  p. 412; the same paragraph in AN 15e lég., question n° 17510 (M. Alain Perea), answer JO 31 décembre 2019: "le taux
  individualisé du conjoint qui a personnellement disposé des revenus les plus faibles [...] est déterminé sur la base
  des revenus dont il a personnellement disposé et de la moitié des revenus communs, et de l'impôt sur le revenu
  afférent. Ce mécanisme permet au premier conjoint de se voir appliquer **un taux de prélèvement équivalent à celui
  d'un célibataire** bénéficiant de ces revenus et de la moitié du quotient familial".
- **Doctrine, worked examples.** BOI-IR-PAS-20-20-20-20250507 § 140. Recomputed with the income-2024 scale
  (`harness/auth_bofip_examples.py`; the households' figures 25 211 €, 24 629 € and 18 980 € match exactly):
  - Example 1, lower earner 24 000 € on one part: the BOFiP gives 725 €. Gross tax 1 111 €; with the single décote
    (889 € − 45.25 %) 725 €; with the couples' décote (1 470 € − 45.25 %) 144 €.
  - Example 2, 1.5 parts: the BOFiP gives 606 €. The single décote gives 606 €; the couples' décote gives 25 €.
  The text never says which décote applies (§ 60 repeats "1 à 4 du I de l'article 197"), but both examples that test
  it use the single-person décote. BOI-IR-LIQ-20-20-30-20260407 § 50 (spouses taxed separately "sont assimilés à des
  contribuables célibataires pour l'application et le calcul de la décote") is about separate taxation and does not
  decide 204 M.
- **Courts:** nothing.
- **Verdict: ministerial answer and doctrine (by example), both for M's reading.** Art. 204 M, 2 builds a fictitious
  person with half the parts and half the common income. The minister calls it the rate "d'un célibataire", and the
  BOFiP computes it that way. The words of 197, I, 4, a ("contribuables soumis à imposition commune") can be read the
  other way, but no authority does so.
- **Wording:** "departs from the law" does not survive. At most: "the DGFiP computes the lower earner's tax as a
  single person's, as the minister and its BOFiP examples describe it; read literally, art. 197, I, 4, a, to which
  204 M refers, gives couples the larger décote." Lean's default should arguably be TXDEC1S/TXDEC2S, with the
  couples' décote kept as the literal variant.

### W5. Quarter-part cap rounding in 204 M (income 2020–2024). **Doctrine for Lean.**
- **Doctrine, worked example.** BOI-IR-PAS-20-20-20-20250507 § 140, example 3 (couple, 2.5 parts, so 1.25 parts for
  the lower earner; income-2024 scale): "le montant de 7 869 euros correspondant à l'IR [...] en application du barème
  de l'impôt pour 1,25 part". Uncapped tax on one part 8 765.48 €, quarter-part cap 895.50 €. Cap rounded on its own
  (8 765 − 896): 7 869 €, the BOFiP's figure. Cap rounded together with the tax, as M's 2020–2024 code does
  (arr(8 765.48 − 895.50)): 7 870 €.
- This matches the general rule in BOI-IR-LIQ-20-20-40 § 50 ("Tout élément venant modifier [...] les cotisations
  [...] est arrondi à l'euro le plus proche") and the QF-cap example in BOI-IR-LIQ-20-20-20-20260407 ("soit
  25 207,98 arrondi à 25 208 €", the cap subtracted afterwards).
- **Courts and questions:** nothing.
- **Verdict: doctrine (by example) sides with Lean and with M's income-2025 code.** Production for income 2024 (5/5)
  follows the 2024 program, against the BOFiP's own example. Both readings give 14.3 % in that example, so the
  example has no effect on the rate there.
- **Wording:** keep it as a disagreement with the program, not with "the law" in the abstract: "for income 2020–2024
  the program rounded the quarter-part cap together with the tax; the DGFiP's own BOFiP example, and its 2025 code,
  round it separately." The effect is a tenth of a point on 6 of 36 779 couples.

### W6. Income-2025 dependants' grid: 8 739 € vs 8 789 €
- **Doctrine.** BOI-BAREME-000037-20260706 § 1, the grid "à compter du 1er mai 2026": "Supérieure ou égale à 7 037
  euros et inférieure à 8 789 euros | 20 % ; Supérieure ou égale à 8 789 euros et inférieure à 12 200 euros | 24 %".
  All 57 bounds of the three 2026 grids equal Lean's `data/pas_grids.jsonl` (`harness/auth_grid_check.py`).
- **Courts and questions:** nothing.
- **Verdict: doctrine = statute; M's 8 739 € matches neither.**
- **Wording:** survives: "the program's dependants' grid for 2026 has 8 739 € where loi n° 2026-103 and the
  DGFiP's own BOFiP grid have 8 789 €." Still no arbiter for what production charges.

### R. Readings where the statute is silent (Lean follows M)
| R point | Authority | Verdict |
|---|---|---|
| Actual expenses below the 10 % allowance: allowance kept | BOI-RSA-BASE-30-50-10-20140306 § 180: "Le régime forfaitaire de déduction est le régime de droit commun. Il s'impose à l'administration ; en revanche, les salariés peuvent y renoncer et faire état de leurs frais réels." § 190: actual expenses when the employee "estime que le montant de ses frais professionnels est supérieur". § 200: the two are exclusive. | Doctrine consistent with M/Lean (the actual-expenses regime is an option the employee takes when it is worth more) |
| RFR overtime net of its share of the 10 % allowance | BOFiP's RFR chapter is "BOI-IR-RFR (en cours de rédaction)"; nothing else | Unaddressed |
| CSG/CRDS rounded together; investment and property CSG rounded apart in 2025 | Not found | Unaddressed |
| QF cap rounded per amount (895.50 → 896); décote rounded on the difference | BOI-IR-LIQ-20-20-40 § 50 (each element "est arrondi à l'euro le plus proche", décotes named); BOI-IR-LIQ-20-20-20 example (tax rounded, then the cap subtracted); BOI-IR-PAS-20-20-20 example 3 (7 869 €, cap rounded apart) | Doctrine consistent with Lean/M |
| Effective rate: décote after the scaling | BOI-IR-LIQ-20-30-30-20120912 § 40: the theoretical tax is scaled by the ratio, "Il y a lieu ensuite de calculer l'impôt effectivement dû après application éventuellement de la décote" | Doctrine confirms |
| Effective rate: art. 157 bis tested on total income | § 40 deducts the "abattements (personnes âgées, enfants mariés)" from the theoretical total income but does not say on which income eligibility is tested | Unaddressed |
| 61 € threshold on income tax and CEHR together | BOI-IR-LIQ-20-20-40 § 60: the threshold "est commun à l'impôt sur le revenu, [...] et la contribution exceptionnelle sur les hauts revenus"; BOI-IR-CHR § 340: "La dispense de recouvrement n'intervient que lorsque le montant cumulé [...] est – avant imputation des crédits d'impôt – inférieur au seuil" | Doctrine confirms |
| Credits imputed on a tax under 61 € before refunding the excess | BOI-IR-LIQ-20-20-40 § 90: "un contribuable dont la cotisation initiale s'élève à 50 € [...] avant imputation d'un crédit d'impôt de 40 € ne pourra pas prétendre au remboursement du crédit d'impôt [...]. De même, si le crédit d'impôt est supérieur au montant de la cotisation initiale qui n'a pas été mise en recouvrement, seule la différence est remboursée." | Doctrine confirms exactly |

### F3. Brochure pratique, Tableaux 4 and 7
- The BOFiP has no table of the income at which the tax reaches 61 € (Tableau 7) or of the first income at which the
  QF cap binds (Tableau 4). Of the 38 BOI-BAREME documents in force, the only income-tax ones are rent ceilings, exemption
  limits, PAS grids and the non-residents' withholding. BOI-IR-LIQ-20-20-40 § 60 gives the 61 € rule (gross tax after
  décote and reductions, before credits), which is the rule Lean's Tableau 7 theorems use.
- No court decision or parliamentary question discusses these tables. The brochure is not BOFiP doctrine, so it
  cannot be relied on under art. L. 80 A LPF, which covers interpretations published in the BOFiP (as TA Lille
  n° 2002202 applies it).
- **Verdict: unaddressed.** The cells are arithmetic consequences of the scale, the décote and the QF cap.
- **Wording:** "the brochure misprints" stands as a statement about arithmetic. Do not call the brochure "the
  DGFiP's doctrine"; it is an explanatory publication.

## 3. Authorities against the Lean model
1. **W3 (clear).** Lean takes the per-part threshold printed in the consolidated CGI on 1 September. The statute's
   indexation clause and the DGFiP's BOFiP (every version 2020–2026, BOI-IR-PAS-20-20-10 § 140/180) set the indexed
   figure, which is what M and production use. Lean is one indexation behind in every year. Fix: use 25 705 (income
   2020), 26 065, 27 473, 28 792, 29 310, 29 574 (income 2025).
2. **W4 (strong, not binding).** Two ministerial answers (JO 31 December 2019; JO AN 17 January 2023 p. 412) and the
   BOFiP's worked examples compute the lower earner's tax as a single person's. Lean's main variant (couples'
   décote) has no authority behind it beyond the literal words of 197, I, 4, a. The variant `TXDEC1S/TXDEC2S` matches
   the authorities and production.
3. Nothing found contradicts Lean on F1, F2, F5, W1, W2, W5, W6 or the R points. For W5 the published doctrine
   sides with Lean. The household-rate formula, the RFR-based zero-rate conditions and the 61 € use in 204 H, II
   (BOI-IR-PAS-20-20-10 § 10–70, 150) agree with Lean's implementation.

## 4. Summary

| Point | Courts | BOFiP doctrine | Ministerial answers | Verdict | Does "departs from the law" survive? |
|---|---|---|---|---|---|
| F1 union dues, 5 000 € limit | none (12 cite 199 quater C) | silent on overtime (RICI-20 § 140–150; no 2019+ overtime doctrine) | none (61 read) | unaddressed | **Yes**: a lag the DGFiP fixed in 2025 |
| F2 CEHR proration with flat-levy income | CE 10 July 2019 n° 412624; TA Paris 29 Jan 2026 n° 2316179: proration upheld for treaty-exempt income only | CHR § 40, 50, 280 (and CDHR-10): flat-levy income in the base; only treaty income excluded | none | explained by doctrine and case law, **for Lean** | **Yes, firmer**: proration reserved for treaty income applied to French flat-levy income |
| F5 rounding margin | none | LIQ-20-20-40 § 50 restates the rule | none | doctrine = statute | **Yes**, as a program artefact (1–2 €) |
| W1 61 € in the rate | none | PAS-20-20-10 § 10, 150: 1657 used only in 204 H, II; LIQ-20-20-40 § 90 "ne constitue pas une exonération" | AN 15e n° 4893 (JO 13 Nov 2018): no 61 € | doctrine **for Lean** | **Yes**, plus: affects advances only |
| W2 rate rounding margin | none | PAS-20-20-10 § 20 restates (6.85 → 6.9) | none | doctrine = statute | **Yes**, as a program artefact |
| W3 204 H II threshold | none | PAS-20-20-10 § 140/180, 2020–2026: indexed figure = M every year | none | doctrine **against Lean** | **No**: Lean's reading is wrong |
| W4 décote in 204 M | none | PAS-20-20-20 § 140 examples 1–2 use the single décote | AN 15e n° 17510 (JO 31 Dec 2019); AN 16e n° 13 (JO 17 Jan 2023 p. 412): "celui d'un célibataire" | ministerial answer + doctrine **for M** | **No**: reword as a literal-text reading |
| W5 quarter-part cap rounding | none | PAS-20-20-20 § 140 example 3: 7 869 € = cap rounded apart | none | doctrine **for Lean** | **Reword**: "against the DGFiP's own BOFiP example (2020–2024 code)" |
| W6 8 739 vs 8 789 | none | BAREME-000037-20260706 § 1: 8 789 € | none | doctrine = statute | **Yes** (M's grid; production not observable) |
| R points | none | 4 confirmed, 1 consistent, 3 silent (table above) | none | — | not claims of departure |
| F3 brochure tables | none | no such tables in BOFiP | none | unaddressed | "misprints" stands; the brochure is not doctrine |

How thorough: the full in-force BOFiP (9 173 records) plus all 13 archived versions of the two PAS rate documents;
every administrative decision in the two open-data channels (1 748 519 scanned: JADE full dump to 8 Nov 2026,
CE/CAA/TA open data 2021–Nov 2026), 6 072 kept on tax terms and searched issue by issue; all AN written questions of
2017–2026 and all Sénat questions of 1978–2026, searched issue by issue. Every hit listed in `hits/*.tsv` was read.
Gaps: AN 2012–2017, parliamentary reports, Légifrance, and BOFiP versions archived before 2018 or for documents
other than the two PAS rate documents.
