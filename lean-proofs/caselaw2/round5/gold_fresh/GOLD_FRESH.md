# Fresh answer key: overruled US Supreme Court decisions (round 5)

Built 2026-11-13. Purpose: a key the model has never been tuned on, split once into a `dev` half that model builders
may use and a sealed `test` half that is scored once at the end. This file contains counts and dev-half rows only.

## Layout

| Path | Who may read | What |
|---|---|---|
| `dev/dev.tsv` | everyone | dev half of the key (165 pairs) |
| `dev/results/` | everyone | scorer output for dev runs |
| `score_fresh.py` | everyone | the scorer |
| `work/scotus_meta.tsv` | everyone | node, date, U.S. cite, name, type of every Supreme Court node (no key content) |
| `build_gold.py` | everyone (code only) | rebuilds the key from `sealed/src` |
| `sealed/` | **evaluation agent only** | `test.tsv` (127 pairs), `all_pairs.tsv`, `all_rows.tsv`, `src/` (the source lists), `results/`, `TEST_RUNS.log`, `SEALED.md` |

## Sources

| Source | What it is | Obtained from | Licence | Derivation |
|---|---|---|---|---|
| `wikipedia` | "List of overruled United States Supreme Court decisions", revision **1380082490**, 2026-10-13T17:50:54Z (sha1 28397728…) | MediaWiki API, 2026-11-13 | CC BY-SA 4.0 (wikitext stored in `sealed/src/wikipedia/`) | Community list, "explicitly overruled, in part or in whole". Arranged by subject, not by full/partial; partial rows carry "(in part)" and that flag is kept. Its only list-type reference is an external link to the GPO Constitution Annotated table, so it is not independent of the CRS table in origin. |
| `blaustein_field_1958` | Blaustein & Field, "Overruling" Opinions in the Supreme Court, 57 Mich. L. Rev. 151 (1958), Appendix pp. 184–194 | Michigan Law Review open repository (repository.law.umich.edu/mlr/vol57/iss2/2) | Facts only (pairs, citations, years, category, page) | Own compilation, 1810–1957. Older than SCDB and the CRS table; the CRS table cites it, so it is upstream of a burned list rather than derived from it. Gives a category per row: E expressly overruled; B / D not expressly overruled but listed by Justice Brandeis / Douglas; O otherwise overruled in the authors' opinion. |
| `gerhardt_1991` | Gerhardt, The Role of Precedent in Constitutional Decisionmaking and Theory, 60 Geo. Wash. L. Rev. 68 (1991), Appendix pp. 147–159 | Author's copy in the William & Mary open repository (scholarship.law.wm.edu/facpubs/980) | Facts only | Own list of cases where the Court "made unmistakably clear its intent to overrule"; constitutional cases only, 1851–1991. For 1971–1991 it contains every pair of Payne n.1. Gives the overturning language for each row; a few rows are called implicit by the author. |
| `payne_n1_1991` | Payne v. Tennessee, 501 U.S. 808, 828 n.1 (1991): the Court's list of 33 constitutional decisions overruled "in whole or in part" in the past 20 Terms | The corpus text of the opinion | Public domain | The Court's own list; marks "in part" and "in effect". |

Not obtained:

- **Gerhardt, *The Power of Precedent* (2008), appendix.** Only retail and publisher listings were found; the appendix
  is not openly readable. The same author's 1991 appendix was used instead.
- **Brenner & Spaeth, *Stare Indecisis* (1995), Appendices I–II.** Cambridge University Press, paywalled; no open copy
  or replication data found.
- A second copy of Blaustein & Field on core.ac.uk answered 403 and was not retried.

Web searches used: 3 of 25. No PDF or long extract of the two articles is stored in the project; the transcriptions in
`sealed/src/` hold only case names, citations, years, the source's category or a few words of the Court's language,
and the page.

## Normalising and resolving

Rows are `pair_id, source, overruling_cite, overruling_name, overruling_year, overruled_cite, overruled_name,
overruled_year, partial, explicit_hint, note` plus the resolution columns (`sealed/all_rows.tsv`).

Resolution uses only the citation table of Supreme Court nodes (`gold/work/scotus_nodes.tsv`): the U.S. Reports page
must hold exactly one decision whose name shares a name token with the list's name. Where several decisions share a
page, the name picks one. If the page is absent, wrong or not given, the one decision of that year (or the adjacent
year) with the same name is taken (12 row-sides, e.g. slip-opinion cases with no U.S. page, and misprinted pages
such as Goldman at "316 U.S. 114"). Seven citations whose corpus name differs from the list's popular name were
checked by hand (`sealed/src/name_overrides.tsv`).

| Source | Rows | Overruling side resolved | Overruled side resolved | Scoreable rows | Distinct scoreable pairs |
|---|---|---|---|---|---|
| wikipedia | 146 | 146 (100%) | 146 (100%) | 146 | 145 |
| blaustein_field_1958 | 123 | 122 (99.2%) | 122 (99.2%) | 121 | 121 |
| gerhardt_1991 | 145 | 145 (100%) | 145 (100%) | 145 | 145 |
| payne_n1_1991 | 37 | 37 (100%) | 37 (100%) | 37 | 37 |
| **All** | **451** | 450 | 450 | 449 | **292** |

Unresolved (kept in `sealed/all_rows.tsv` with the reason): 2 rows, both Blaustein — one overruled decision whose
page is not in the corpus, one rehearing order whose page holds a different case.

The 292 pairs cover 285 distinct overruled decisions. 171 pairs are in one list only, 86 in two, 35 in three.

## Split

`sha1(overruled decision's U.S. citation as the corpus carries it) mod 2`: 0 = dev, 1 = test (a decision with no U.S.
page is keyed `node:<id>`). An overruled decision is never in both halves. Done once; the rule is a pure function.

| | Pairs | Distinct overruled | Partial | Implied | In CRS (any edition) | Overruler flagged in SCDB | In neither |
|---|---|---|---|---|---|---|---|
| dev | 165 | 158 | 13 | 20 | 146 | 157 | 6 |
| test | 127 | 127 | 15 | 21 | 119 | 122 | 5 |
| all | 292 | 285 | 28 | 41 | 265 | 279 | 11 |

The halves are uneven (165 / 127) because the hash is taken per overruled decision and was not re-rolled.

## How independent is "fresh"? Overlap with the burned lists

Counted on scoreable pairs. CRS = same (overruling, overruled) pair in `gold/crs_overruled.tsv`; SCDB = the overruling
decision carries `precedentAlteration = 1` (SCDB names no overruled case, so this is a weaker match).

| Source | Pairs | CRS 2016 | of which "expressly" | CRS current (2022 + 2026 supp.) | CRS any | SCDB flags overruler | In neither |
|---|---|---|---|---|---|---|---|
| wikipedia | 145 | 108 | 103 | 124 | 126 (87%) | 137 | 8 |
| blaustein_field_1958 | 121 | 111 | 74 | 99 | 114 (94%) | 116 | 3 |
| gerhardt_1991 | 145 | 139 | 118 | 128 | 141 (97%) | 145 | 0 |
| payne_n1_1991 | 37 | 35 | 32 | 35 | 36 (97%) | 37 | 0 |
| All | 292 | 244 | 191 | 238 | **265 (91%)** | **279 (96%)** | **11 (4%)** |

So the fresh key is independent in compilation, not in content: 91% of its pairs are also in a CRS edition and 96%
have an SCDB-flagged overruler. Only 27 pairs are outside CRS and only 11 are outside both. What is new is (a) the
split, (b) the per-source express / implied / partial labels, and (c) those 27 pairs. A gain on this key that does
not show on the 27 non-CRS pairs is weak evidence of generalisation; the scorer reports `burned_crs` separately.

## How the fresh lists disagree

For each ordered pair of lists: pairs of the first whose overruling decision falls in the period both lists cover,
and how many of those the second list lacks. Gerhardt and Payne n.1 are constitutional only, so statutory and
common-law pairs are expected to be missing from them.

| First list | Second list | Pairs of first in common period | Missing from second |
|---|---|---|---|
| wikipedia | blaustein_field_1958 | 11 | 2 |
| wikipedia | gerhardt_1991 | 97 | 39 |
| wikipedia | payne_n1_1991 | 61 | 32 |
| blaustein_field_1958 | wikipedia | 121 | 112 |
| blaustein_field_1958 | gerhardt_1991 | 121 | 63 |
| gerhardt_1991 | wikipedia | 145 | 87 |
| gerhardt_1991 | blaustein_field_1958 | 60 | 2 |
| gerhardt_1991 | payne_n1_1991 | 49 | 12 |
| payne_n1_1991 | wikipedia | 37 | 8 |
| payne_n1_1991 | gerhardt_1991 | 37 | 0 |

Wikipedia is thin before 1957 (it has 9 of Blaustein's 121 pairs) and misses 87 of Gerhardt's 145. The lists also
disagree on scope: in 20 pairs one list says "in part" (or uses "to the extent" wording) and another does not. The
key's `partial` is 1 if any source says so; `partial_by_source` keeps each list's view.

## Rows of the Brown / Plessy kind (the source itself says implied or partial)

`implied` = 1 when a source says so: Blaustein categories B, D, O; Gerhardt rows described as implicit; Payne
"overruling in effect". `partial` = 1 on Wikipedia "(in part)", Payne "in part", or Gerhardt language "to the
extent" / "insofar". Totals: 41 implied, 28 partial (one pair is both). The full list is in
`sealed/implied_partial_rows.tsv`; the dev half:

| Overruling | Overruled | Flag | Who says |
|---|---|---|---|
| Gayle v. Browder, 352 U.S. 903 | Plessy v. Ferguson, 163 U.S. 537 | implied | Blaustein O |
| United States v. South-Eastern Underwriters, 322 U.S. 533 | Paul v. Virginia, 75 U.S. 168 | implied | Blaustein D (Wikipedia lists it as explicit) |
| The Belfast, 74 U.S. 624 | Allen v. Newberry, 62 U.S. 244 | implied | Blaustein B, D |
| Louisville, C. & C. R. Co. v. Letson, 43 U.S. 497 | Strawbridge v. Curtiss, 7 U.S. 267; Bank of the United States v. Deveaux, 9 U.S. 61 | implied | Blaustein B |
| Phelps Dodge Corp. v. NLRB, 313 U.S. 177 | Adair v. United States, 208 U.S. 161; Coppage v. Kansas, 236 U.S. 1 | implied | Blaustein D |
| Toucey v. New York Life, 314 U.S. 118 | Supreme Tribe of Ben-Hur v. Cauble, 255 U.S. 356 | implied | Blaustein D |
| Suydam v. Williamson, 65 U.S. 427 | Williamson v. Berry, 49 U.S. 495; Williamson v. Irish Presbyterian Congregation, 49 U.S. 565 | implied | Blaustein O |
| Reid v. Covert, 354 U.S. 1 | Kinsella v. Krueger, 351 U.S. 470 | implied | Blaustein O (rehearing) |
| Halliburton v. Walker, 329 U.S. 1; MacGregor v. Westinghouse, 329 U.S. 402; Railroad Commission v. Pacific Gas, 302 U.S. 388 | the same case before rehearing (326 U.S. 696; 327 U.S. 758; 301 U.S. 669) | implied | Blaustein O (rehearing) |
| Harper v. Virginia Board of Elections, 383 U.S. 663 | Butler v. Thompson, 341 U.S. 937 | implied | Gerhardt (named only in the dissent) |
| Williams v. Florida, 399 U.S. 78 | Thompson v. Utah, 170 U.S. 343; Rassmussen v. United States, 197 U.S. 516 | implied | Gerhardt |
| Pennhurst v. Halderman, 465 U.S. 89 | Atchison, T. & S.F. Ry. v. O'Connor, 223 U.S. 280; Greene v. Louisville & Interurban R., 244 U.S. 499 | implied | Gerhardt |
| Taylor v. Louisiana, 419 U.S. 522 | Hoyt v. Florida, 368 U.S. 57 | implied | Payne "in effect" |
| Healy v. Beer Institute, 491 U.S. 324 | Joseph E. Seagram & Sons v. Hostetter, 384 U.S. 35 | partial | Gerhardt wording |
| South Carolina v. Baker, 485 U.S. 505 | Pollock v. Farmers' Loan & Trust, 157 U.S. 429 | partial | Wikipedia |
| United States v. Miller, 471 U.S. 130 | Ex parte Bain, 121 U.S. 1 | partial | Payne, Gerhardt wording |
| Burks v. United States, 437 U.S. 1 | Yates v. United States, 354 U.S. 298 | partial | Wikipedia |
| Welch v. Texas Dept. of Highways, 483 U.S. 468 | Parden v. Terminal Railway, 377 U.S. 184 | partial | Payne |
| Edelman v. Jordan, 415 U.S. 651 | Sterrett v. Mothers' & Children's Rights Org., 409 U.S. 809 | partial | Payne, Gerhardt wording |
| Alabama v. Smith, 490 U.S. 794 | North Carolina v. Pearce (Simpson v. Rice), 395 U.S. 711 | partial | Gerhardt wording |
| Daniels v. Williams, 474 U.S. 327 | Parratt v. Taylor, 451 U.S. 527 | partial | Payne |
| Monell v. Department of Social Services, 436 U.S. 658 | Monroe v. Pape, 365 U.S. 167 | partial | Wikipedia |
| East Ohio Gas v. Tax Commission, 283 U.S. 465 | Pennsylvania Gas v. Public Service Commission, 252 U.S. 23 | partial | Gerhardt wording |
| O'Malley v. Woodrough, 307 U.S. 277 | Evans v. Gore, 253 U.S. 245 | partial | Gerhardt wording |
| Escobedo v. Illinois, 378 U.S. 478 | Crooker v. California, 357 U.S. 433 | partial | Gerhardt wording |
| Thornburgh v. Abbott, 490 U.S. 401 | Procunier v. Martinez, 416 U.S. 396 | partial | Payne |

Brown v. Board of Education / Plessy itself is in the dev half through Wikipedia, which lists it without
qualification, so the key counts it as express and full; Blaustein instead names Gayle v. Browder as the
overruler of Plessy and calls it implied.

## Scorer

```
python round5/gold_fresh/score_fresh.py --split dev  --status out/status.tsv --treatments data/treatments.tsv --label <name>
python round5/gold_fresh/score_fresh.py --split test --status out/status.tsv --treatments data/treatments.tsv --label <name>
```

(run from `caselaw-lean-2/`; `--findings` defaults to `findings.tsv` beside `--status`; `--treatments` is optional and
only adds a diagnostic column.) Every `--split test` run appends to `sealed/TEST_RUNS.log`.

Outcome per gold pair (overruling Y, overruled X), from X's rows in `status.tsv`:

- **a**: `neg:overruled` or `neg:abrogated`, actor = Y, from = Y's date (or the next day). Strict hit.
- **a_date**: as a, another start date. **a_kind**: actor = Y, another negative kind.
- **b**: negative by another actor. **c**: `unknown:*` only. **d**: only an `atRisk` finding linking X and Y. **e**: nothing.
- Strict recall = a. Lenient recall = a, a_date, a_kind, b, c. Wilson 95% intervals.

Precision side: Supreme Court decisions the model marks `neg:overruled` / `neg:abrogated` with a Supreme Court actor,
classed `listed`, `targetListedOtherOverruler` or `unlisted` ("in no fresh list", not "wrong"). The model's rows are
divided into halves by the same hash, so a dev run reveals nothing about the sealed pairs.

## Baseline (`baseline-round4`: current `out/status.tsv`, sha1 ece2365e…, 2026-11-12 23:33)

| Split | Pairs | a | a_date | a_kind | b | c | d | e | Strict | Lenient |
|---|---|---|---|---|---|---|---|---|---|---|
| dev | 165 | 50 | 0 | 0 | 2 | 34 | 12 | 67 | 30.3% [23.8, 37.7] | 52.1% [44.5, 59.6] |
| test | 127 | 32 | 0 | 0 | 1 | 26 | 17 | 51 | 25.2% [18.4, 33.4] | 46.5% [38.0, 55.1] |

Of the `c` rows, 33 of 34 (dev) and all 26 (test) name the gold overruler as the actor: the model found the
overruling and left its scope unknown.

| Breakdown | dev strict | dev lenient | test strict | test lenient |
|---|---|---|---|---|
| full (152 / 112) | 32.9% [25.9, 40.7] | 50.7% [42.8, 58.5] | 28.6% [21.0, 37.5] | 46.4% [37.5, 55.6] |
| partial (13 / 15) | 0% [0, 22.8] | 69.2% [42.4, 87.3] | 0% [0, 20.4] | 46.7% [24.8, 69.9] |
| express (145 / 106) | 34.5% [27.2, 42.5] | 58.6% [50.5, 66.3] | 30.2% [22.3, 39.5] | 54.7% [45.2, 63.9] |
| implied (20 / 21) | 0% [0, 16.1] | 5.0% [0.9, 23.6] | 0% [0, 15.5] | 4.8% [0.9, 22.7] |
| wikipedia (80 / 65) | 38.8% [28.8, 49.7] | 68.8% [57.9, 77.8] | 36.9% [26.2, 49.1] | 63.1% [50.9, 73.8] |
| blaustein_field_1958 (72 / 49) | 26.4% [17.6, 37.6] | 36.1% [26.0, 47.6] | 14.3% [7.1, 26.7] | 28.6% [17.8, 42.4] |
| gerhardt_1991 (84 / 61) | 33.3% [24.2, 44.0] | 59.5% [48.8, 69.4] | 29.5% [19.6, 41.9] | 57.4% [44.9, 69.0] |
| payne_n1_1991 (18 / 19) | 0% [0, 17.6] | 77.8% [54.8, 91.0] | 36.8% [19.2, 59.0] | 63.2% [41.0, 80.8] |
| in CRS (146 / 119) | 33.6% [26.4, 41.6] | 56.2% [48.1, 63.9] | 26.1% [19.0, 34.6] | 47.9% [39.1, 56.8] |
| not in CRS (19 / 8) | 5.3% [0.9, 24.6] | 21.0% [8.5, 43.3] | 12.5% [2.2, 47.1] | 25.0% [7.1, 59.1] |
| overruled to 1945 (58 / 39) | 31.0% [20.6, 43.8] | 41.4% [29.6, 54.2] | 12.8% [5.6, 26.7] | 30.8% [18.6, 46.4] |
| 1946–1991 (78 / 69) | 20.5% [13.0, 30.7] | 53.8% [42.9, 64.5] | 24.6% [16.0, 36.0] | 46.4% [35.1, 58.0] |
| 1992 on (29 / 19) | 55.2% [37.6, 71.6] | 69.0% [50.8, 82.7] | 52.6% [31.7, 72.7] | 78.9% [56.7, 91.5] |

(n in brackets is dev / test; the era is the overruling decision's date.)

Precision side: the model marks 96 Supreme Court decisions overruled by a Supreme Court decision. Dev half: 53, of
which 50 listed, 3 unlisted. Test half: 43, of which 32 listed, 1 listed under another overruler, 10 unlisted.
Samples: `dev/results/baseline-round4.unlisted_sample.tsv` and the sealed counterpart.

## Doubts about the key

- **Content overlap with the burned lists is 91–96%** (above). Treat the 27 non-CRS pairs as the only truly new ones.
- **Hand transcription.** Blaustein and Gerhardt were read from page images and typed by hand (268 rows). Every
  citation was checked against the corpus name and year, which caught the misprints found; a wrong pairing inside a
  multi-case row would not be caught.
- **Same-case rehearings.** Eight scoreable Blaustein pairs are a case overruling its own earlier disposition on
  rehearing (flagged "same case on rehearing" in `note`, mostly category O). The model treats these as history, not
  precedent; they count as misses unless a status names the rehearing decision.
- **Implied rows are 14% of the key** and the baseline scores about 0% on them. Report express-only numbers alongside.
- **Decisions reported together.** Peirce v. New Hampshire resolves to the License Cases node (Thurlow v.
  Massachusetts); Simpson v. Rice to North Carolina v. Pearce. The node is right; the list means one case within it.
- **Payne n.1 is corpus text.** The model's reader can read that footnote; it is a later decision of the same court
  stating the overrulings. Gerhardt's 1971–1991 rows coincide with it.
- **`partial` is the union** across lists, and Gerhardt's flag is inferred from the quoted wording ("to the extent",
  "insofar"), not from a column of his.
- **Wikipedia is a moving, incomplete list** (it carries an "incomplete list" banner); the revision is pinned.
- **Small cells.** Partial, implied, Payne and non-CRS cells have 8–21 pairs per half; their intervals are wide.
- **Uneven split** (165 / 127); dev and test baselines differ by five points strict, within the intervals.
