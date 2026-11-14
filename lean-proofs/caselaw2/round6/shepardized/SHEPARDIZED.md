# The Lean precedent model against the Shepardized Courts of Appeals Database

Run on 13 November 2026 against the live round-4 output (`out/status.tsv` of 12 Nov 23:33). Nothing outside
`round6/shepardized/` was edited; nothing was committed.

## Summary

For 19,916 sampled federal appeals-court decisions from 1925 to 2002, we compared what our model says happened to each
decision later in the same case with what a hand-coded research database built from Shepard's citator says. Where
Shepard's shows no reversal, the model agrees almost every time (19,287 of 19,290), and when the model does say a
decision was reversed or vacated it matches Shepard's in 14 of 18 cases (78%, interval 55%–91%). But the model finds
only 14 of the 506 decisions that Shepard's shows were reversed, vacated or withdrawn (2.8%, interval 1.7%–4.6%): the
later ruling is nearly always in our collection, and the model fails to connect it to the decision it reviewed.

The overall agreement figure, 19,331 of 19,852 (97.4%), should not be quoted on its own: 97% of the sample has no
negative history, so a model that marked nothing at all would score 97.3% (19,319 of 19,852).

## 1. Source and terms

| Item | Value |
|---|---|
| Page | http://artsandsciences.sc.edu/poli/juri/appct.htm (Judicial Research Initiative, University of South Carolina), fetched 2026-11-13 |
| Shepardized data | `shepardized_cta_stata.zip` → `shepardized_cta_stata.dta` (Stata format 114, internal time stamp "19 Nov 2010 12:07"; the page says "Last Update: November 19, 2010"). Compiled by Rorie Spill Solberg, Oregon State University |
| Shepardized codebook | `shepardized_cta_codebook.pdf` ("Codebook Final Version", 13 pages) |
| Songer database, 1925–1996 | `cta96_stata.zip` (used only for the decision year) and `cta96_codebook.pdf` |
| Kuersten–Haire update, 1997–2002 | `KH_update_stata.zip` and `KH_update_codebook.pdf` (downloaded; not needed, the Shepardized file carries the update's citation and date) |
| Terms of use | None stated on the page or in the codebook. No licence statement, no click-through, no login. The codebook credits National Science Foundation grants SES-8912678, SES-9602172, SES-0318349 |
| Transport | The site's HTTPS certificate has expired, so HTTPS failed; certificate checking was **not** switched off. The same files are served by the site over plain HTTP, which was used. A Wayback Machine copy of the zip exists (2024-11-17) and was not needed |
| Parsing | Standard-library Python only (`convert.py`, run with `-I`). pandas could not be used: an Application Control policy on this machine blocks its compiled modules. Nothing from the downloads was executed |

SHA-256 of the downloads (`src/`):

| File | SHA-256 |
|---|---|
| `shepardized_cta_stata.zip` | `4bb6ef483b60dd78e34a7af942c4155ab5ccd4f7d63731918209346e29a61ded` |
| `shepardized_cta_stata.dta` (extracted) | `7f573042460dd1c2d28839aa3af34da9f451b0ba7dbe662da0f777a6172fe9f9` |
| `shepardized_cta_codebook.pdf` | `cdc3830df57553673a9a802181b9daf7d53712e09b0cb60632acc37a89772c0d` |
| `cta96_stata.zip` | `114ff4a0d02261302356e470cc70065067f7f277a546c855c347decaea9d9f26` |
| `cta96_stata.dta` (extracted) | `6b7b5912bc061e6f990d0e381e0795e17bf0c08d2e2ecbc861de26e316e7ca02` |
| `cta96_codebook.pdf` | `3b2d0319511ea037f373e9afb94d03fefe2f477382ac590ae75bf56f73fd1208` |
| `KH_update_stata.zip` | `047abf84f8fa772a65d8684f8f41c01a611b3213aa683da0d8c4135a81c992ae` |
| `KH_update_stata.dta` (extracted) | `e1cd5d29e360bbf1d2b8e0a68cba19ebf4c706f162245da91788287d37964c24` |
| `KH_update_codebook.pdf` | `a4512c71eba3017940303ffc4d91675f87c47d17b0511513ce9d265890f546d7` |
| `appct.htm` (the page) | `b583001304cd3af9dd5f0acf61d37a584d0b3df97239eb8fa68e117f6ad58736` |

What the codebook says, as read:

- **Unit:** the Songer case (one published court of appeals decision). The file has 20,354 rows and 453 columns; the
  codebook says 20,355 cases, so one case is absent.
- **Citation:** `citation`, e.g. `0842 f 2d 0556` (volume 842, page 556, F.2d); for the 1997–2002 cases `124 f 3d 243`.
  Also `vol`/`beginpg` (old cases) and `cite_vol`/`begin_page`/`decision_date` (update cases). The Shepardized file has
  no year for the old cases; it was taken from `cta96_stata.dta` by `casenum`.
- **Outcome variables:** `appeal`, `subhist`, `coarehear`, `coaenbanc`, `scappeal`, `scresult`, `screhear`,
  `appaftre1`–`5`, and the Supreme Court Database identifiers `us1`, `sct1`, `led1`, `docket1`, `dis1`, `analu1` (and
  `…2`). The outcome variables are filled for 6,033 rows and blank for 14,321. They go with `appeal` codes that
  contain the digit 1 (6,037 rows), with ten exceptions: 7 such rows are blank and 3 rows without the digit are filled.
- **Date of the Shepardizing:** not stated. The codebook quotes an email of 11 September 2008 from LexisNexis about
  Shepard's categories; the file is stamped 19 November 2010. The comparison uses 2010-11-19 and repeats it for
  2008-09-11 and for today (section 4.6).
- **No event dates** are recorded, only the U.S. Reports citation of a Supreme Court decision where there is one.
- **Reliability (theirs):** 1,018 cases coded twice; agreement 95.1% to 99.7% by variable. The codebook warns that
  Shepard's "same case" and "connected case" labels are vague, and that the coders "did err on the side of
  inclusiveness".

## 2. Linking

`link.py`. A case is linked when exactly one decision in the corpus has its F.2d/F.3d citation, sits in the Songer
circuit, and was decided in the Songer year; where several decisions share the page, court and year, the one with the
exact Songer date is taken if there is exactly one. Nothing else is linked.

| Result | Cases | Share |
|---|---|---|
| Linked: one decision at the citation, court and year agree | 19,565 | 96.12% |
| Linked: several on the page, exactly one has the exact date | 351 | 1.72% |
| **Linked, total** | **19,916** | **97.85%** (Wilson 95%: 97.64%–98.04%) |
| Several decisions on the page still fit | 164 | 0.81% |
| Year differs (88 of them: Songer year is one more than the corpus year; 13 one less) | 109 | 0.54% |
| No decision with that citation in the corpus | 95 | 0.47% |
| Court differs (36: the corpus files the D.C. Circuit decision under a district-court collection; 13: Songer circuit 1 or 11, corpus Fifth Circuit) | 64 | 0.31% |
| Citation field unreadable (e.g. `1.0303738`, `0955/0480`) | 6 | 0.03% |
| Total | 20,354 | |

- Of the linked cases, 970 have the right year but a different day from the Songer date; they are kept.
- Six pairs of Songer case numbers carry the same citation and link to the same decision (2722/2728, 3335/3360,
  8253/8272, 12295/12300, 15556/15559, 16880/16896). All twelve rows are clean on both sides.
- The 438 unlinked cases are 423 `CLEAN`, 14 `NEG` and 1 `MOD` in the classes below.

## 3. Mapping

`MAPPING.md`, written before any row was joined; **not changed after scoring**. In short:

| Shepardized class | Codes | Expected model output |
|---|---|---|
| `NEG` | Supreme Court reversed (`scresult` 2, 3) or vacated (4, 7, including "vacated and remanded for reconsideration"); panel decision withdrawn or vacated (`coarehear` 6) or different result on rehearing (3); different result en banc (`coaenbanc` 3) | negative for a same-case reason |
| `PART` | Supreme Court affirmed in part and reversed in part, or modified (`scresult` 5, 6) | negative or "unknown: partial scope" |
| `AMBIG` (not scored) | en banc granted with same, unknown or dismissed result; rehearing granted with same or unknown result; review granted with no result | – |
| `MOD` | decision modified on rehearing (`coarehear` 4, 5) | not negative |
| `CLEAN` | no history; related case only; cert denied; rehearing denied; Supreme Court affirmed; history after remand only | no same-case negative |

Model classes, from the decision-level row of `out/status.tsv` at the as-of date: `NEG_HIST` (negative through a
same-case history row), `UNK_HIST`, `NEG_OTHER` and `UNK_OTHER` (overruled or limited by a different case: counted as
"no same-case negative"), `GOOD`.

One fix was made to `compare.py` after the first run, to the actor check only (section 4.5): it first compared node
ids through the one-node-per-citation index and reported 12 of 13; several decisions share a U.S. Reports page, and
compared by the actor's own citation it is 13 of 13. No class, mapping or agreement figure changed.

## 4. Results (as of 2010-11-19; `results/asof20101119/tables.tsv`)

### 4.1 Confusion table (linked cases)

| Shepardized | NEG_HIST | UNK_HIST | NEG_OTHER | UNK_OTHER | GOOD | Total |
|---|---|---|---|---|---|---|
| NEG | 14 | 0 | 0 | 1 | 491 | 506 |
| PART | 1 | 0 | 0 | 0 | 26 | 27 |
| AMBIG | 0 | 0 | 0 | 0 | 64 | 64 |
| MOD | 0 | 0 | 0 | 0 | 29 | 29 |
| CLEAN | 3 | 0 | 11 | 41 | 19,235 | 19,290 |
| Total | 18 | 0 | 11 | 42 | 19,845 | 19,916 |

By Shepardized sub-class:

| Sub-class | Model as expected (Wilson 95%) |
|---|---|
| NEG / Supreme Court reversed | 10/261 = 3.8% (2.1%–6.9%) |
| NEG / Supreme Court vacated | 4/132 = 3.0% (1.2%–7.5%) |
| NEG / panel decision withdrawn, vacated or changed on rehearing | 0/52 = 0.0% (0.0%–6.9%) |
| NEG / different result en banc | 0/60 = 0.0% (0.0%–6.0%) |
| NEG / Supreme Court vacated and different result en banc | 0/1 |
| PART / Supreme Court part and part | 1/27 = 3.7% (0.7%–18.3%) |
| MOD / modified on rehearing | 29/29 = 100% (88.3%–100%) |
| CLEAN / no history | 12,114/12,114 = 100% |
| CLEAN / related case only | 1,896/1,898 = 99.9% (99.6%–100%) |
| CLEAN / cert denied or dismissed | 4,360/4,360 = 100% (99.9%–100%) |
| CLEAN / rehearing denied | 357/357 = 100% (98.9%–100%) |
| CLEAN / Supreme Court affirmed | 161/161 = 100% (97.7%–100%) |
| CLEAN / other history (after remand) | 399/400 = 99.8% (98.6%–100%) |

### 4.2 The three questions

| Question | Result | Wilson 95% |
|---|---|---|
| **(a) Recall.** Of decisions Shepardized shows reversed, vacated or withdrawn, the model has a same-case negative | 14/506 = 2.8% | 1.7%–4.6% |
| (a) with part-and-part cases: model negative or unknown | 1/27 = 3.7% | 0.7%–18.3% |
| **(b) Precision.** Of decisions the model has negative for a same-case reason, Shepardized has `NEG` | 14/18 = 77.8% | 54.8%–91.0% |
| (b) lenient: Shepardized has `NEG` or `PART` | 15/18 = 83.3% | 60.8%–94.2% |
| **(c) Clean.** Of decisions Shepardized shows clean, the model shows no same-case negative | 19,287/19,290 = 99.98% | 99.95%–99.99% |
| (c) strict: the model shows `good` (not even overruled or limited by another case) | 19,235/19,290 = 99.7% | 99.6%–99.8% |
| Overall agreement on scored classes (dominated by the clean cases; see Summary) | 19,331/19,852 = 97.4% | 97.1%–97.6% |

Reading the three model negatives that Shepardized shows clean (section 5.3) found the model wrong in all three. So
no model negative is a case Shepardized missed, and the model's precision on this sample is 14 or 15 of 18, not higher.

### 4.3 By decade

| Decade | Agreement, scored cases | Recall on Shepardized NEG |
|---|---|---|
| 1920s | 705/724 = 97.4% (95.9%–98.3%) | 0/17 = 0.0% (0.0%–18.4%) |
| 1930s | 1552/1602 = 96.9% (95.9%–97.6%) | 1/46 = 2.2% (0.4%–11.3%) |
| 1940s | 1536/1590 = 96.6% (95.6%–97.4%) | 0/45 = 0.0% (0.0%–7.9%) |
| 1950s | 1563/1603 = 97.5% (96.6%–98.2%) | 2/40 = 5.0% (1.4%–16.5%) |
| 1960s | 3001/3070 = 97.8% (97.2%–98.2%) | 3/70 = 4.3% (1.5%–11.9%) |
| 1970s | 3174/3259 = 97.4% (96.8%–97.9%) | 3/82 = 3.7% (1.3%–10.2%) |
| 1980s | 3381/3483 = 97.1% (96.5%–97.6%) | 3/103 = 2.9% (1.0%–8.2%) |
| 1990s | 3409/3479 = 98.0% (97.5%–98.4%) | 2/72 = 2.8% (0.8%–9.6%) |
| 2000s | 1010/1042 = 96.9% (95.7%–97.8%) | 0/31 = 0.0% (0.0%–11.0%) |

### 4.4 By circuit

| Circuit | Agreement, scored cases | Recall on Shepardized NEG |
|---|---|---|
| DC | 1638/1686 = 97.2% (96.2%–97.8%) | 0/44 = 0.0% (0.0%–8.0%) |
| 1 | 1727/1778 = 97.1% (96.2%–97.8%) | 1/49 = 2.0% (0.4%–10.7%) |
| 2 | 1722/1764 = 97.6% (96.8%–98.2%) | 1/39 = 2.6% (0.5%–13.2%) |
| 3 | 1723/1763 = 97.7% (96.9%–98.3%) | 1/39 = 2.6% (0.5%–13.2%) |
| 4 | 1709/1765 = 96.8% (95.9%–97.5%) | 2/55 = 3.6% (1.0%–12.3%) |
| 5 | 1692/1750 = 96.7% (95.7%–97.4%) | 2/59 = 3.4% (0.9%–11.5%) |
| 6 | 1725/1773 = 97.3% (96.4%–98.0%) | 2/48 = 4.2% (1.2%–14.0%) |
| 7 | 1739/1782 = 97.6% (96.8%–98.2%) | 1/41 = 2.4% (0.4%–12.6%) |
| 8 | 1716/1753 = 97.9% (97.1%–98.5%) | 3/40 = 7.5% (2.6%–19.9%) |
| 9 | 1694/1747 = 97.0% (96.1%–97.7%) | 1/51 = 2.0% (0.3%–10.3%) |
| 10 | 1652/1681 = 98.3% (97.5%–98.8%) | 0/25 = 0.0% (0.0%–13.3%) |
| 11 | 594/610 = 97.4% (95.8%–98.4%) | 0/16 = 0.0% (0.0%–19.4%) |

Neither table shows a difference between decades or circuits that the intervals support. The agreement column tracks
the share of clean cases in each group, nothing more.

### 4.5 Kind and event date

- **Kind**, where both sides are negative (14 cases): the model's kind is the expected one in 13 (92.9%, 68.5%–98.7%).
  Supreme Court reversed → `neg:reversed` 10; vacated → `neg:vacated` 3; vacated → `neg:withdrawn` 1 (*Hirras*, section 5.3).
- **Event date.** The Shepardized file has no dates, so dates cannot be compared directly. Where it names a U.S.
  Reports decision (274 linked cases; 273 resolve in the corpus) and the model has a same-case negative with an actor
  (13 cases), the model's actor is that decision in 13 of 13 (77.2%–100%), so the event date is that decision's date.

### 4.6 Other as-of dates

`results/asof20080911/` and `results/asof20261112/`: every figure in 4.2 is identical. Only the split of clean cases
between `GOOD`, `NEG_OTHER` and `UNK_OTHER` moves (overrulings by other cases after 2008).

### 4.7 Hidden same-case events

No decision with a non-history status (`NEG_OTHER`, `UNK_OTHER`) also has an admitted reversed, vacated or withdrawn
history row. The low recall is not an artefact of the status file showing only the most severe effect.

## 5. The disagreements

There are 521 scored disagreements: 492 `NEG` cases the model does not show negative, 26 `PART` cases the model shows
clean, 3 `CLEAN` cases the model shows negative. No `MOD` case disagrees.

### 5.1 Every missed case, sorted mechanically (`causes.py`, `results/asof20101119/causes.tsv`)

A rule-based sort of all 518 missed `NEG` and `PART` cases: is there a later decision in the corpus, and does its text
cite the target?

| Where the later decision is | Supreme Court outcomes (406) | Court of appeals outcomes (112) | All (518) |
|---|---|---|---|
| In the corpus, cites the target, and the citation graph has the link | 225 Supreme Court decisions; 15 more where only the court of appeals' later decision cites it | 82 | 322 |
| In the corpus, cites the target in a form the citation graph did not link (`70 F. (2d) 956`); all 32 targets are from the 1920s and 1930s | 32 | – | 32 |
| In the corpus (matched by name, court and date), does not cite the target | 97 | 20 | 117 |
| Nothing found | 37 | 10 | 47 |

So for 354 of the 518 misses a later decision that cites the target is already in the corpus, and for 117 more a
later decision in the same case is there without citing it. The name matching in the third row is a rule, not a
reading; the sample below agrees with the buckets in the cases it covers.

### 5.2 Sample read: 40 of the 492 missed `NEG` cases (random, seed 20261113) and all 26 `PART` cases

Read from the decision texts by three reading agents with full-text access (`results/asof20101119/reading.tsv`,
packs `pack_A1.txt`, `pack_A2.txt`, `pack_B.txt`). I re-read the passages for every case classed as a Shepardized error.

| Class of cause | NEG sample (40) | PART (26) |
|---|---|---|
| Model missing the event: later decision in the corpus cites the target, not read | 28 | 20 |
| Model missing the event: later decision in the corpus does not cite the target | 7 | 2 |
| Model missing the event: later decision not found in the corpus | 1 | 0 |
| Model missing the event: unpublished order | 0 | 0 |
| Model wrong | 0 | 0 |
| Shepardized coding wrong or misleading for this decision | 2 | 1 |
| Mapping artefact (the code is right but the decision kept its force) | 1 | 3 |
| Linking error | 0 | 0 |
| Could not be determined | 1 | 0 |

Why the 48 "not read" cases were not read:

- **Supreme Court opinions cite the decision below as a bare citation.** The usual form is "The Court of Appeals
  affirmed. 856 F. 2d 1214 (1988)." with no party name, and the disposition ("Reversed.") is at the far end of the
  opinion. The reader takes a citation as the decision under review only when one of the reviewing decision's own
  party names stands in the 250 characters before it (`reader/scan.py`, the `selfc` step), so these never become
  candidates. This is the largest single cause: most of the 28 and of the 20.
- **Old citation form.** Six of the 48 (13844, 14401 and four `PART` cases) cite the target as `F. (2d)`, which the
  citation graph does not link to the F.2d decision; mechanically, 32 of the 518 misses are of this kind.
- **Changed captions.** Parties reversed when the loser below petitions, officials substituted, consolidated cases
  under another lead name (*Greer v. Miller*, *Schlesinger v. Councilman*, *Louisiana PSC v. FCC*).
- **En banc opinions** that refer to "a panel of this court" without a usable citation, or cite the panel opinion
  only in a footnote or dissent (1096, 2253, 21381, 21926).
- **Court of appeals orders on remand** that recite the Supreme Court's action ("vacated our judgment of December 8,
  1987, Brock v. Shirk, 833 F.2d 1326") were not read as events (606, 924, 3043).
- **Dispositions by docket number or by count** ("Nos. 7 and 48 affirmed. No. 8 reversed.").

The 9 "does not cite" cases are mostly what `data/READER.md` already lists as a blind spot: Supreme Court orders of
the form "Certiorari granted, judgment vacated, and case remanded for further consideration in light of …", which give
a docket number and "C. A. 6th Cir." and no reporter citation (175, 5537, 17152, 17956, 21568), and short per curiams
(15167, 11187). These orders **are in the corpus**; what is missing is the link. Supreme Court orders absent from the
corpus are not the main cause: one sampled case (7029) may be one.

### 5.3 The model's own negatives

All 18 were read (pack `pack_CD.txt`).

- **3 where Shepardized shows clean: the model is wrong in all three**, each time by attaching a real disposition to
  the wrong decision of the same litigation.
  - *Fogle v. General Credit*, 110 F.2d 128 (D.C. Cir. 1940): the model has it reversed by 122 F.2d 45 (1941). That
    opinion reverses the trial court's later judgment and says "Upon a former appeal the case was remanded for want
    of sufficient findings. Fogle & City Bank v. General Credit, Inc., 1940, 71 App.D.C. 338, 110 F.2d 128."
  - *Corriveau v. United States*, 53 F.2d 735 (1st Cir. 1931): the model has it reversed by *United States v.
    Corriveau*, 286 U.S. 530 (1932). That per curiam's head matter says "See also, 53 F. (2d) 735"; the decree it
    reverses is the government's loss in *United States v. Corriveau*, 56 F.2d 362 (1st Cir. 1932), not the
    forfeiture the government won in 53 F.2d 735. Shepardized's "connected case" is right.
  - *Hamdi v. Rumsfeld*, 296 F.3d 278 (4th Cir. 2002): the model has it vacated by 542 U.S. 507 (2004). The judgment
    vacated there is the later 316 F.3d 450.
- **1 where both are negative but the model's event is wrong:** *Hirras v. National Railroad Passenger Corp.*, 10 F.3d
  1142 (5th Cir. 1994). The model has it withdrawn by 44 F.3d 278, which says "we withdraw our prior opinion, …
  39 F.3d 522"; the target was vacated by the Supreme Court (114 S.Ct. 2732), in an order that does not cite it.
- The other 14 are right on both sides.

## 6. Errors found in the Shepardized database

Each was checked against the text of the later decision in our corpus.

1. **Case 10085, *Travis v. United States*, 247 F.2d 130 (10th Cir. 1957).** Coded `scappeal` 3, `scresult` 2
   (Supreme Court reversed), `us1` 364/0631. *Travis v. United States*, 364 U.S. 631 (1961): "Petitioner was convicted
   and on appeal the judgment of conviction was reversed for a new trial. 247 F. 2d 130. Petitioner was tried a second
   time and again convicted. This time the judgment was affirmed on appeal, one judge dissenting. 269 F. 2d 928. The
   case is here on a writ of certiorari." The judgment reversed is 269 F.2d 928. The outcome belongs in the
   after-remand variable.
2. **Case 4596, *E. I. du Pont de Nemours & Co. v. Train*, 528 F.2d 1136 (4th Cir. 1975).** Coded `scresult` 5
   (affirmed in part and reversed in part), `us1` 430/0112. 430 U.S. 112 (1977): "That portion of the judgment of the
   Court of Appeals in 541 F.2d 1018 requiring EPA to provide a variance procedure for new sources is reversed. In all
   other aspects, the judgments of the Court of Appeals are affirmed." The part reversed belongs to the companion
   decision; 528 F.2d 1136 was affirmed.
3. **Case 2184, *Costa v. Markey*, 677 F.2d 158 (1st Cir. 1982).** Coded `coarehear` 0 (no request for rehearing),
   `coaenbanc` 3 (granted, different result). *Costa v. Markey*, 706 F.2d 1 (1st Cir. 1982–83): on panel rehearing,
   "Our prior opinion finding no liability is reversed"; then en banc, "We reaffirm our original decision of May 3,
   1982." There was a panel rehearing with a different result, and the en banc court restored the original result.
4. **Case 14083, *United States v. Palmer & Parker Co.*, 61 F.2d 455 (1st Cir. 1932)** (weaker). Coded `coarehear` 3
   (granted, different result). On rehearing: "The court adheres to the view that appellee's damages are not to be
   tested by the market value of the mahogany logs, as logs", and only "It is ordered that the decree of June 27,
   1932, be amended to read as follows". Code 2 (same result) or 4 (modified) fits better.

Smaller points in the file: 20,354 rows where the codebook says 20,355; six unreadable `citation` values (cases
15426, 15555, 15789, 16244, 16853, 16856); six pairs of case numbers with one citation (section 2); in case 17152
(*NYSA-ILA v. Axelrod*, 27 F.3d 823) `us1` 520/0806 points to the later *De Buono* decision although the vacatur
coded in `scresult` was the order at 514 U.S. 1094 (seen by a reading agent; not re-checked by me). The 109 year and
28 non-D.C. court differences in section 2 may include Songer keying errors; they were not examined.

## 7. What this does and does not show

- It covers **same-case history only**: what a higher court, the en banc court or the panel itself later did to the
  decision. It says nothing about overruling by later, different cases.
- It is a **sample of published appeals-court decisions, 1925–2002**, with history as Shepard's showed it around
  2008–2010. No district courts, no state courts, nothing after 2002.
- The reference is a hand-coded academic file built from Shepard's, with its own coding error (3 or 4 found in 66
  disagreements read) and Shepard's own vagueness about "same case" and "connected case".
- **Precision rests on 18 cases.** The interval (55%–91%) is wide. All four errors found (the three wrong negatives
  plus *Hirras*) have one cause: the right disposition attached to another decision in the same litigation.
- **Recall is the finding.** 2.8% is not a property of the corpus: for 354 of 518 missed cases the later decision is
  there and cites the target. It is a property of how the history reader picks the decision under review.
- The 99.98% clean agreement is real but cheap: it mostly reflects that the model asserts very little.
- The class `AMBIG` (64 cases: en banc or rehearing granted with the same or an unknown result) was not scored. The
  model shows all 64 as `good`.

## 8. What would raise recall (not done here)

In order of cases reached, from 5.1 and 5.2:

1. Take a bare citation that follows "The Court of Appeals [for the X Circuit] affirmed/reversed/…" in a Supreme
   Court opinion as the decision under review, checked by circuit and date instead of by party name.
2. Normalise `F. (2d)` and `F. (3d)` in the citation graph.
3. Link Supreme Court memorandum orders by docket number, circuit label and caption (party order reversed), and use
   the court of appeals' own order on remand as a second witness.
4. Read en banc grants and en banc opinions by docket number and caption where the panel opinion is not cited.
5. For precision: when a later decision cites several earlier decisions of the same litigation, attach the
   disposition to the most recent one of the court named, not the first cited.

## 9. Files

| File | What |
|---|---|
| `MAPPING.md` | the mapping, written before scoring |
| `convert.py` | Stata → TSV, standard library only (`work/shepardized.tsv`, `work/songer96.tsv`, `work/columns.txt`) |
| `fed_nodes.py` | every corpus decision with an F.2d or F.3d citation (`work/fed_nodes.tsv`) |
| `link.py` | linking (`results/links.tsv`, `results/link_summary.tsv`) |
| `compare.py` | scoring; `--out`, `--data`, `--asof`, `--tag` (`results/<tag>/cases.tsv`, `tables.tsv`) |
| `citers.py`, `causes.py`, `pack.py` | later citing decisions, mechanical buckets, reading packs (`citers.tsv`, `causes.tsv`, `causes_summary.tsv`, `sample.tsv`, `pack*.txt`) |
| `results/asof20101119/reading.tsv` | the 70 cases read, with category and quoted passage |

To re-run on another model output: `python -I compare.py --out <dir with status.tsv and certs.tsv> --tag <name>`.
