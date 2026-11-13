# caselaw-lean-2: data audit (2026-11-12)

What the data can support, measured. Nothing here is estimated without a sample behind it.

## Method

- **Sample.** `scripts/sample.py` drew a stratified random sample (seed 20261112) from `graph/nodes.tsv` + `lean-in-v3/decisions.tsv`. It has 9,000 decisions in each of 6 strata, plus all 1,285 unmapped decisions: **55,285 files** in total, every decade from the 1780s to the 2020s.
- **Reading the files.** The repos in `~/Documents/us-caselaw-repos` have **no working-tree checkout**: the files live only in git objects. The sample was read with `git cat-file --batch` into the session scratch directory (738 MB, not kept).
- **Strata and populations:**

| stratum | rule | decisions |
|---|---|---|
| scotus | court "Supreme Court of the United States" | 384,140 |
| fed_app | system 0, tier A | 895,162 |
| fed_trial_special | system 0, tier T/S | 697,214 |
| state_last | system > 0, tier L | 2,196,591 |
| state_app | system > 0, tier A | 2,238,282 |
| state_trial_special | system > 0, tier T/S | 479,780 |
| unmapped | court id 3160 | 1,285 |

- **Measurement.** `scripts/analyze.py` measures each file (8 processes) and `scripts/summarize.py` builds the tables. The "corpus (weighted)" column reweights each stratum's rate by its population. The full tables are in the appendix.
- **Header zone.** In the status-marker tables, the "header zone" is the front matter, plus the head matter, plus the first 1,500 characters of the first opinion section. "Body only" means the marker appears only after that point.

## 1. Front matter fields

Share of files carrying each key, by stratum:

| key | scotus | fed_app | fed_trial_sp | state_last | state_app | state_trial_sp |
|---|---|---|---|---|---|---|
| court, decided, source, source_url | 100 | 100 | 100 | 100 | 100 | 100 |
| cap_id | 100 | 100 | 98 | 100 | 100 | 100 |
| citations | 99.9 | 85 | 99.6 | 100 | 100 | 100 |
| parties | 98.5 | 83 | 100 | 100 | 100 | 100 |
| docket | 97 | 99.8 | 91 | 59 | 59 | 52 |
| precedential_status (+ precedential_note, reporter) | 12.6 | 2.0 | 99.8 | 100 | 100 | 100 |
| cites_cases | 14 | 78 | 88 | 73 | 71 | 82 |
| judges | 7 | 57 | 9 | 41 | 42 | 22 |
| decision_type | 87 | 0 | 0 | 0 | 0 | 0 |
| cites_law | 0.1 | 3.9 | 12.8 | 0.1 | 0.2 | 0.1 |
| text_source ("CAP head matter, no opinion text") | 8.5 | 0 | 0.2 | 1.4 | 1.0 | 0.3 |

Rarer keys: document_title, document_type and dawson_entries (Tax Court DAWSON, 1.9% of fed_trial_special), decided_precision, cap_court, court_note.

**Fields that do not exist at all:**
- en banc flag, per-curiam flag, panel, attorneys, opinion-type list, author;
- CourtListener `precedential_status` (as CL's own field), CL cluster id, citation-treatment fields;
- disposition, subsequent history;
- district, division or department of a state intermediate court.

**Field notes:**
- **`precedential_status`.** It is almost a constant: "published" with the note "printed in a reporter; CAP records no other status" in 99.8% of files that carry it. The only other values are "nonprecedential" (167) and "precedential" (7), all in fed_trial_special. Weighted, about 13k decisions in the corpus are non-published.
- **`judges`.** Free text in CAP's form ("COBB, C.J., and COWART, J., concur."; "Before NYE, C.J., and BENAVIDES and DORSEY, JJ."). It is not a list of names. Only 0.1% of files mention en banc in it.
- **`decision_type`.** Present only for SCOTUS: memorandum order 71%, opinion 8%, per curiam 8%, missing 13%.
- **CourtListener ids.** CourtListener files carry `cap_id: "cl-<id>"` and `source_url .../opinion/<id>/`. That is an **opinion id, not a cluster id**. CourtListener is the source for 16.6% of fed_app files (all the 2019+ federal appellate files), 1.5% of SCOTUS files, and about 0% of state files. Example: `ca1:decisions/united-states-court-of-appeals-for-the-first-circu/2022/cap-cl-5957492.md`.
- **Parallel citations.** Share of files with two or more entries in `citations`: SCOTUS 22%, state_last 25%, state_app 23%, fed_app 0.6%. Cross-reporter copies merged in `graph/` (`decision-relations.tsv`): 39,101.
- **`cites_cases`.** Mean entries per decision: 1.8 (SCOTUS) to 20 (fed_trial_special).

## 2. Opinion text and status markers

**Is the full text there?**

| measure | scotus | fed_app | fed_trial_sp | state_last | state_app | state_trial_sp | corpus |
|---|---|---|---|---|---|---|---|
| opinion text ≥ 1,000 chars | 7.8 | 90.6 | 92.2 | 76.2 | 68.5 | 93.8 | 74.6% (~5.14M) |
| opinion text < 300 chars (orders, stubs) | 81.6 | 2.7 | 4.5 | 15.3 | 21.3 | 3.3 | 17.4% (~1.2M) |

The estimated corpus text is about 71 GB, with a mean of 10.3k characters per decision.

**Are majority, concurrence and dissent separated?** Yes, for CAP files. The body uses `## Majority (Author)`, `## Concurrence`, `## Dissent` and `## Head matter` sections.

| section | corpus share |
|---|---|
| Majority | 96% |
| Dissent | 3.5% (~244k) |
| Concurrence | 1.9% (~132k) |
| "Concurring in part", "Rehearing" or "Lead" | under 1% |
| Combined only | 2.2%, but 16.5% of fed_app |

"Combined only" is CourtListener's unsplit text. That covers all CL federal appellate files, which in practice means 2019 and later. There is no Plurality section type.

**Status markers** (corpus-weighted share; header zone vs body only):

| marker | header zone | body only | notes |
|---|---|---|---|
| en banc / in banc | 1.0% (fed_app 5.2%) | 2.7% (fed_app 10.6%) | Body hits are mostly mentions of other courts' en banc proceedings. Only the header zone is a usable flag. |
| per curiam | 11.3% (fed_app 33%) | 2.4% | The section title says "Per Curiam" in 9.9% of files: this is the cleanest signal. |
| plurality | ~0% | 0.3% | No section type. Must be found in the text ("announced the judgment"). |
| unpublished / not for publication / Rule 47.5 | 2.9% (fed_app 15%) | 1.6% | Far more than `precedential_status` shows (0.2%). |
| "vacated" | 1.3% | 4.0% | Self-vacatur phrasing ("opinion … vacated") is 0.1% header / 0.3% body. |
| withdrawn / substituted | 0.1% | 0.1% | Rare. |
| rehearing (any) | 2.0% | 3.3% | "Rehearing denied": 1.1% / 1.2%. "On rehearing" or granted: 0.2% / 0.7%. |

Example paths:
- En banc in the header: `ca1:decisions/united-states-court-of-appeals-for-the-first-circu/1996/101-F-3d-1.md`
- Unpublished in the header: `georgia-appellate:decisions/court-of-appeals-of-georgia/2015/333-Ga-App-777.md`
- Dissent section: `alabama:decisions/alabama-supreme-court/1989/541-So-2d-480.md`

## 3. Head matter, syllabi and headnotes

- **Head matter exists only for SCOTUS (86%) and fed_app (81%).** It is 0.0–0.2% in every state stratum and in fed_trial_special: state files start straight at `## Majority`.
  - About 1.4% of state files are CAP "head matter only" stubs (section `## CAP head matter`, with `text_source: "CAP head matter (CAP holds no opinion text)"`). Example: `alabama-appellate:decisions/court-of-civil-appeals-of-alabama/2018/272-So-3d-1101.md`.
- **What head matter holds.** In fed_app it is the caption, counsel and panel ("Before …"). An attorney line appears in 74.5% of fed_app files. It almost never holds headnotes: 3 or more numbered headnotes in 0.2%.
- **SCOTUS full opinions** (n = 703 in the sample):
  - 55% have a reporter's summary in the head matter (≥ 500 characters of prose).
  - Coverage by period: 1800–1919, about 90% (e.g. Palmer v. McMahon: "Held, (1) That …"); 1920–39, 46%; **1940–2025, 0–33%**. Modern US Reports syllabi are absent.
  - "Syllabus" appears in the text of only 2.3%.
- **Usable summary for the corpus** (head prose ≥ 500 chars, or Held, or Syllabus): **1.2% (~82k)**, essentially pre-1940 SCOTUS plus a little fed_app.
  - Holdings and issues will have to come from the opinion text.
  - Alternatively, re-fetch CAP's `head_matter` from `source_url` (static.case.law JSON), which is present in 100% of files. That is untested here.

## 4. Treatment language

Measured in Python on all 55,285 files, with ripgrep as a cross-check: rg found the same phrases in 6,409 files. Corpus estimates are stratum-weighted.

| phrase | decisions with ≥1 hit | est. occurrences in corpus |
|---|---|---|
| overrul\* (any) | 12.6% (~867k) | ~1.68M |
| — of which procedural ("objection/motion/demurrer … overruled") | 2.6% | ~228k |
| — express "is hereby overruled" / "we overrule" | 0.7% | ~85k |
| overruled in part | 0.2% | ~16.9k |
| overruled on other grounds | 0.6% | ~45.7k |
| "to the extent that" (all uses) | 4.9% | ~473k |
| "to the extent" within the same sentence as overruled/disapproved/abrogated/receded | 0.2% | ~11.5k |
| abrogat\* | 1.2% | ~124k |
| abrogated on other grounds | 0.2% | ~15.4k |
| superseded by statute/rule/amendment | 0.1% | ~10.3k |
| disapprov\* | 1.2% | ~131k |
| recede(d) from (FL: state_last 2.3, state_app 1.7 per 1,000) | 0.1% | ~11.0k |
| limited to its facts | 0.03% | ~2.4k |
| questioned (any) | 4.8% | ~445k |
| questioned (treatment form: "has been questioned", "called into question") | 1.4% | ~115k |
| we decline / refuse to follow | 0.2% | ~12.2k |

Notes:
- "questioned" and "to the extent that" are mostly ordinary prose and are useless without context.
- The state_trial_special rate for "expressly overrule" (5.7%) is mostly Texas Courts of (Civil) Appeals ruling on motions. Those courts are mis-tiered; see section 5.
- **Is there a smarter source?** No, not inside our data:
  - The files keep no CourtListener treatment fields. CourtListener's citation data carries depth, not treatment.
  - Parenthetical citator-style phrases such as "(overruled on other grounds by …)" are rare in the text (≤ 0.5% of files).
- The best in-corpus source is what already exists:
  - `events_v3/reports.tsv`: later courts' statements that X was overruled, 81,590 rows.
  - the windows in `extract3/*.overrul.jsonl`: 1,820,399 windows, already cut, 3.9 GB.
  - Extending the extractor's prefilter (`overrul|disapprov`) with `abrogat|recede|superseded by|decline to follow|limited to its facts|overruled in part` would add roughly 300k windows. Most "to the extent" and "questioned" hits should be taken only when they co-occur with those verbs.

## 5. Court identity

- **Tables.**
  - `graph/courts.tsv`: 3,181 court names.
  - `court_table.tsv` / `lean-in-v3/courts.tsv`: 3,160 mapped rows (3,161 with id 3160 = unmapped).
  - Unmapped residue: `court_unmapped.tsv`, 26 names, **1,285 decisions**. The largest are Court of Customs and Patent Appeals (460, which should be federal, a predecessor of the Federal Circuit), Fort Peck Court of Appeals (344), tribal courts and circuit Judicial Councils.
- **Fallback rules.** The "repo-state-trial/special/appellate" rules assign a court to its repo's default tier. They cover 1,705 court names but only about 87k decisions.

**Mis-tiering found.** 47 state courts named "Appeals" sit in tier trial or special, covering **184,794 decisions**:

| court | decisions | current tier |
|---|---|---|
| Texas Courts of Civil Appeals | 82,154 | T |
| Texas Courts of Appeals | 59,825 | T |
| Alabama Court of Criminal Appeals | 17,135 + 2,073 | T |
| Massachusetts Appeals Court | 14,433 | T |
| Texas Commission of Appeals | 4,679 | S (its opinions adopted by the Texas Supreme Court bind as that court's) |
| Tennessee Court of Criminal Appeals | 3,081 | T |
| New York Commission of Appeals | 866 | S |

**Other mapping faults:**
- "United States Supreme Court of the District of Columbia" (4 decisions) is mapped to tier L, rule `scotus`. It was a DC trial court.
- "Maryland Appellate Reports" (63 decisions) is a reporter name used as a court.
- 2,529 acts in `acts.tsv` target SCOTUS decisions but were made by non-SCOTUS courts (SCOTUS itself made 322 acts). This is target-resolution noise to filter, since a lower court cannot overrule SCOTUS.

**State intermediate courts with districts or divisions.** 182 court names in FL, CA, TX, IL, NY AD, LA, OH, MO, WA, AZ and IN cover **~1.72M decisions**. Only about 34k of them (about 2%) have the district in the court name: mostly 2014+ names such as "District Court of Appeal of Florida, Second District". Everything else must come from the docket or the text. Recovery in the sample:

| group | n | recovered | route |
|---|---|---|---|
| WA | 222 | 88% | docket suffix -I/-II/-III |
| AZ | 57 | 100% | docket "1 CA-" / "2 CA-" |
| TX CoA / Civ. App. | 2,746 | 62% | docket "NN-YY-…-CR/CV" (33%); city in text (29%, noisier) |
| MO | 290 | 56% | docket ED/WD/SD; name |
| OH | 184 | 53% | mostly county ("Court of Appeals for X County") → district via county table |
| NY AD | 2,921 | 46% | almost all via county of the order appealed → department via county table; "X Department" only 0.6% |
| FL DCA | 1,071 | 40% | docket "nD…" 27%; "… District" in text 13% (may name another DCA) |
| IN | 191 | 39% | docket "NNA0n-" |
| CA | 405 | 33% | docket letter A–H (post-~1980s) |
| LA | 477 | 17% | "… Circuit" in text |
| IL | 494 | 10% | docket "n-YY-…" |

Most of the misses are pre-1980 decisions with bare numeric dockets. CAP's `head_matter`, which carries the court line ("District Court of Appeal of Florida, Third District"), is the likely fix, at the cost of re-fetching from `source_url`.

**Successor and renamed courts:**
- **Kentucky.** "Kentucky Court of Appeals" is already split by era (≤1975 L, ≥1976 A). In the data, 67,509 decisions sit in repo `kentucky`, all before 1976; 5,524 sit in `kentucky-appellate`, all from 1976 on. Date and repo agree, so the split is clean.
- **New Jersey and Virginia.** Both are already split by era: NJ Supreme Court A until 1947, then L; Court of Appeals of Virginia L until 1984, then A.
- **Maryland.** The 2022 rename (Supreme Court of Maryland; Appellate Court of Maryland) **does not appear**: Maryland data ends in 2019 (CAP). "Court of Appeals of Maryland" is correctly L.
- **New York.** NY Court for the Correction of Errors and NY Supreme Court of Judicature (pre-1847) are L.
- **Coverage after 2019.** Of 181,600 decisions dated 2019 or later, nearly all are federal (CourtListener); florida-appellate (6,823) is the main state exception.

## 6. Scale and compute

- **Acts** (`events_v3/acts.tsv`): 33,895 rows (14.5 MB), made by 19,402 decisions against **28,133 distinct targets**. `lean-in-v3/acts.tsv` has 31,914 rows. Unresolved acts: 30,858. By pattern:

| pattern | rows |
|---|---|
| passive:name | 10,913 |
| passive:cite | 5,919 |
| we:name | 5,812 |
| disapprove-\* | 8,943 |

- **Reports** (`events_v3/reports.tsv`): 81,590 rows (35 MB); 51,895 name the overruling decision; **43,368 distinct targets**.
- **Overruled targets (acts ∪ reports): 65,029 decisions.** SCOTUS made 322 acts against 281 distinct targets.
- **Candidate passages.** The `overrul|disapprov` windows total 1,820,399. They break down by class (`counts.json`) as:

| class | windows |
|---|---|
| noise | 1,042,074 |
| other | 277,513 |
| report-unresolved | 288,283 |
| act | 33,895 |
| act-unresolved | 30,858 |
| refused | 30,521 |
| quoted | 28,973 |
| no-node | 15,149 |

- **Supreme Court: 384,140 decisions**, of which about 31k (7.8%) have ≥ 1,000 characters of opinion text. The decision_type split is 71% memorandum order, 8% opinion, 8% per curiam.

**Timing on this machine.** The CPU was about 62% busy with other work while timing ran.
- **ripgrep**, over the 55,285 sample files (the 50k test), warm cache, 10-phrase regex:

| run | time | rate | full-corpus extrapolation |
|---|---|---|---|
| `-j1` | 11.6 s | 4.8k files/s | |
| `-j8` | 1.8 s | ~30k files/s | about 4 min, if the corpus were on disk as files |

- **Python** (read + `re.findall`), over 50,000 files (578 MB):

| run | time | rate | full-corpus extrapolation |
|---|---|---|---|
| 1 process | 65.3 s | 766 files/s | |
| 8 processes | 12.3 s | 4,070 files/s | about 28 min of regex work |

- **The binding constraint is git decompression.** There are no files on disk to grep, and a checkout would need about 71 GB.
  - `git cat-file --batch` streams 2,400 files/s for florida-appellate (50k files in 21 s) but only 545 files/s for michigan (56k files in 100 s, cold or warm; delta chains).
  - The previous full pass (`extract3`, 6 processes, git stream + front matter parse + substring prefilter) finished all 6.93M files in **about 6–7 minutes** (file mtimes 00:57–01:03).
- **Estimate for a full-text regex pass** (8 streams, Python with a substring prefilter, then regex on hits): **10–30 minutes**. A full Python regex over every byte is about 30 minutes.
- **Disk:** C: has **23–25 GB free (98% used)**. Do not materialise the corpus. Stream from git, and keep outputs compact.

## 7. Statute links

- **`usc/results/rows_out.tsv`**: 1,931,153 rows (393 MB), one per US Code citation in a decision since 1995.
  - Columns: row, **nid** (= `graph/nodes.tsv` id, so it joins directly), decided, section, subsection, …, first amending law and date, flags, name, repo, path, cite.
  - It covers 701,352 decisions; 370,472 cite a section later amended. `summary.json` has the totals (amended rows 705,571; SCOTUS rows 11,575).
- **`uses/overrides/cand_rows.tsv`**: 421,897 rows, each a citation whose cited block was first rewritten by a law.
- **`uses/overrides/overrides.tsv`**: 6,069 decision–law candidate pairs, keyed by nid, with evidence and audit columns.
- **`uses/overrides/confirmed.tsv`**: **34 confirmed congressional overrides** (27 express, 7 implicit; 17 SCOTUS, 9 appeals, 8 district/specialised). The audit estimate is about 609 overrides among the candidates (Wilson interval 215–1,730).
- **Use for caselaw-lean-2.** The nid join makes a "superseded by statute" status feasible:
  - with high precision only for the 34 confirmed;
  - as a scored candidate layer for the 6,069 pairs;
  - not at all before 1995, since the citation reader starts in 1995.

## 8. LLM capacity (gpt-5.4-mini)

The reader calls an Azure OpenAI `gpt-5.4-mini` deployment (version 2026-03-17) through Chat Completions with json_schema output. The endpoint and key come from the environment (`AGENTIC_AZURE_OPENAI_ENDPOINT`, `AGENTIC_AZURE_OPENAI_API_KEY`). A bulk script should bound its concurrency to the deployment's token-per-minute quota, store the model and token usage of every call, and be resumable (a done-ids file), since the full corpus is millions of calls.

It was not called during this audit.

## Appendix: full sample tables (`scripts/summarize.py`)


### Source and text

| measure | scotus | fed_app | fed_trial_special | state_last | state_app | state_trial_special | corpus (weighted) |
|---|---|---|---|---|---|---|---|
| CourtListener source | 1.5% | 16.6% | 0.0% | 0.0% | 0.0% | 0.0% | 2.2% (~154,000) |
| opinion text >= 1,000 chars | 7.8% | 90.6% | 92.2% | 76.2% | 68.5% | 93.8% | 74.6% (~5,141,000) |
| opinion text < 300 chars (order/stub) | 81.6% | 2.7% | 4.5% | 15.3% | 21.3% | 3.3% | 17.4% (~1,199,000) |
| has Head matter section | 86.0% | 81.4% | 0.2% | 0.0% | 0.0% | 0.0% | 15.4% (~1,060,000) |
| head matter >= 300 chars | 9.2% | 77.5% | 0.2% | 0.0% | 0.0% | 0.0% | 10.6% (~730,000) |
| has Majority section | 87.3% | 83.4% | 97.8% | 98.6% | 99.0% | 99.7% | 96.1% (~6,623,000) |
| has Concurrence section | 0.9% | 2.0% | 0.7% | 2.8% | 1.7% | 1.2% | 1.9% (~132,000) |
| has Dissent section | 1.8% | 3.6% | 1.2% | 5.4% | 3.1% | 1.9% | 3.5% (~244,000) |
| only Combined section(s) | 0.3% | 16.5% | 0.0% | 0.0% | 0.0% | 0.0% | 2.2% (~149,000) |
| any other section type | 9.9% | 1.4% | 2.4% | 3.6% | 2.2% | 2.3% | 3.0% (~208,000) |
| front matter judges | 6.8% | 57.2% | 9.4% | 41.3% | 41.8% | 21.5% | 37.0% (~2,549,000) |
| front matter docket | 97.2% | 99.8% | 91.2% | 59.3% | 59.2% | 51.8% | 69.4% (~4,779,000) |
| precedential_status present | 12.6% | 2.0% | 99.8% | 100.0% | 100.0% | 100.0% | 82.4% (~5,677,000) |
| precedential_status != published | 0.0% | 0.0% | 1.9% | 0.0% | 0.0% | 0.0% | 0.2% (~13,000) |
| decision_type present | 87.4% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 4.9% (~336,000) |

### Status markers: header zone (fm + head matter + first 1,500 chars) / body only / either

| measure | scotus | fed_app | fed_trial_special | state_last | state_app | state_trial_special | corpus (weighted) |
|---|---|---|---|---|---|---|---|
| en_banc in header | 0.1% | 5.2% | 0.3% | 0.5% | 0.2% | 0.5% | 1.0% (~68,000) |
| en_banc body only | 0.4% | 10.6% | 5.1% | 1.2% | 0.9% | 1.2% | 2.7% (~184,000) |
| per_curiam in header | 8.7% | 32.7% | 1.9% | 8.3% | 10.9% | 2.2% | 11.3% (~777,000) |
| per_curiam body only | 0.4% | 7.1% | 4.7% | 2.0% | 0.8% | 1.7% | 2.4% (~168,000) |
| plurality in header | 0.1% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% (~1,000) |
| plurality body only | 0.2% | 1.0% | 0.6% | 0.2% | 0.2% | 0.1% | 0.3% (~24,000) |
| unpublished in header | 0.0% | 15.2% | 2.0% | 0.2% | 2.1% | 0.2% | 2.9% (~202,000) |
| unpublished body only | 0.0% | 8.3% | 1.7% | 0.3% | 0.4% | 1.1% | 1.6% (~108,000) |
| vacated in header | 1.2% | 2.4% | 1.0% | 0.7% | 1.8% | 0.9% | 1.3% (~93,000) |
| vacated body only | 0.6% | 9.0% | 5.8% | 3.1% | 3.2% | 3.3% | 4.0% (~279,000) |
| vacated_opinion in header | 0.9% | 0.2% | 0.1% | 0.0% | 0.1% | 0.0% | 0.1% (~10,000) |
| vacated_opinion body only | 0.0% | 0.6% | 0.4% | 0.3% | 0.2% | 0.2% | 0.3% (~21,000) |
| withdrawn in header | 0.0% | 0.1% | 0.0% | 0.2% | 0.1% | 0.5% | 0.1% (~9,000) |
| withdrawn body only | 0.0% | 0.1% | 0.1% | 0.2% | 0.1% | 0.1% | 0.1% (~8,000) |
| rehearing in header | 3.0% | 8.4% | 0.7% | 1.0% | 0.7% | 1.2% | 2.0% (~135,000) |
| rehearing body only | 0.4% | 2.2% | 2.9% | 4.1% | 3.3% | 3.8% | 3.3% (~225,000) |
| rehearing_granted_or_on in header | 0.1% | 0.4% | 0.1% | 0.2% | 0.1% | 0.2% | 0.2% (~11,000) |
| rehearing_granted_or_on body only | 0.0% | 0.4% | 0.5% | 1.1% | 0.5% | 1.2% | 0.7% (~49,000) |
| rehearing_denied in header | 2.7% | 6.4% | 0.1% | 0.2% | 0.1% | 0.1% | 1.1% (~76,000) |
| rehearing_denied body only | 0.1% | 0.6% | 0.6% | 1.3% | 1.9% | 0.2% | 1.2% (~81,000) |
| per curiam in section title | 2.0% | 24.9% | 1.8% | 8.7% | 10.7% | 2.1% | 9.9% (~683,000) |
| judges field says en banc | 0.0% | 0.1% | 0.1% | 0.2% | 0.0% | 0.1% | 0.1% (~6,000) |

### Head matter content

| measure | scotus | fed_app | fed_trial_special | state_last | state_app | state_trial_special | corpus (weighted) |
|---|---|---|---|---|---|---|---|
| syllabus word in head matter | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% (~0) |
| 'Held:' in head matter | 0.9% | 0.6% | 0.0% | 0.0% | 0.0% | 0.0% | 0.1% (~9,000) |
| >=1 numbered headnote line in head matter | 0.1% | 0.6% | 0.0% | 0.0% | 0.0% | 0.0% | 0.1% (~5,000) |
| >=3 numbered headnote lines | 0.0% | 0.2% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% (~2,000) |
| attorney line in head matter | 20.0% | 74.5% | 0.2% | 0.0% | 0.0% | 0.0% | 10.8% (~745,000) |
| 'Syllabus' in first 4k chars of opinion text | 0.2% | 0.0% | 0.0% | 0.1% | 0.0% | 0.0% | 0.0% (~3,000) |
| 'Held,'/'Held:' in first 6k chars of opinion text | 0.2% | 0.1% | 0.5% | 0.4% | 1.0% | 0.3% | 0.5% (~37,000) |
| head matter prose (non-attorney lines >150 chars) >= 500 chars | 4.6% | 6.7% | 0.0% | 0.0% | 0.0% | 0.0% | 1.1% (~78,000) |
| usable summary: head prose>=500 or Held or Syllabus | 4.8% | 6.8% | 0.0% | 0.1% | 0.0% | 0.0% | 1.2% (~82,000) |

SCOTUS full opinions only (opinion text >= 1,000 chars):
n=703; head prose>=500: 54.8%; Held in head: 11.5%; Syllabus in text: 2.3%; CL: 3.7%
by 20-yr period (head prose>=500 / n): 1800: 9/11, 1820: 19/22, 1840: 34/34, 1860: 52/57, 1880: 104/123, 1900: 91/97, 1920: 42/92, 1940: 0/61, 1960: 5/78, 1980: 26/79, 2000: 3/39, 2020: 0/10

### Treatment phrases: share of decisions with >=1 hit

| measure | scotus | fed_app | fed_trial_special | state_last | state_app | state_trial_special | corpus (weighted) |
|---|---|---|---|---|---|---|---|
| overruled_in_part | 0.0% | 0.4% | 0.4% | 0.2% | 0.1% | 0.1% | 0.2% (~14,000) |
| to_the_extent_overrul | 0.0% | 0.1% | 0.3% | 0.3% | 0.1% | 0.2% | 0.2% (~11,000) |
| to_the_extent_that | 0.7% | 8.9% | 14.0% | 2.9% | 3.4% | 4.4% | 4.9% (~341,000) |
| abrogated | 0.2% | 2.2% | 2.2% | 1.1% | 0.7% | 1.3% | 1.2% (~83,000) |
| abrogated_other_grounds | 0.0% | 0.8% | 0.6% | 0.0% | 0.0% | 0.1% | 0.2% (~14,000) |
| superseded_by_statute | 0.0% | 0.3% | 0.1% | 0.1% | 0.1% | 0.1% | 0.1% (~9,000) |
| disapproved | 0.3% | 1.2% | 1.8% | 1.5% | 1.0% | 1.2% | 1.2% (~86,000) |
| receded | 0.0% | 0.1% | 0.1% | 0.2% | 0.1% | 0.1% | 0.1% (~10,000) |
| limited_to_facts | 0.0% | 0.0% | 0.1% | 0.0% | 0.0% | 0.0% | 0.0% (~2,000) |
| questioned | 0.8% | 5.8% | 6.8% | 5.2% | 3.9% | 5.6% | 4.8% (~331,000) |
| questioned_treatment | 0.3% | 1.8% | 2.2% | 1.5% | 1.1% | 1.7% | 1.4% (~98,000) |
| decline_to_follow | 0.0% | 0.3% | 0.4% | 0.1% | 0.2% | 0.3% | 0.2% (~12,000) |
| overruled_other_grounds | 0.0% | 1.1% | 1.1% | 0.4% | 0.4% | 0.5% | 0.6% (~40,000) |
| overrule_any | 1.9% | 9.2% | 10.6% | 17.9% | 8.6% | 24.6% | 12.6% (~867,000) |
| overruled_procedural | 0.4% | 0.6% | 1.8% | 4.1% | 1.9% | 5.6% | 2.6% (~178,000) |
| expressly_overrule | 0.0% | 0.1% | 0.3% | 0.6% | 0.3% | 5.7% | 0.7% (~49,000) |

### Treatment phrases: occurrences per 1,000 decisions and estimated corpus total

| phrase | scotus | fed_app | fed_trial_special | state_last | state_app | state_trial_special | est. total occurrences |
|---|---|---|---|---|---|---|---|
| overruled_in_part | 0.0 | 4.4 | 4.4 | 2.7 | 1.6 | 1.1 | 16,900 |
| to_the_extent_overrul | 0.1 | 1.6 | 2.6 | 2.8 | 0.6 | 2.0 | 11,500 |
| to_the_extent_that | 8.7 | 118.2 | 233.1 | 36.8 | 42.1 | 55.4 | 473,300 |
| abrogated | 4.1 | 32.6 | 35.4 | 18.0 | 9.3 | 17.0 | 124,000 |
| abrogated_other_grounds | 0.0 | 8.9 | 7.1 | 0.3 | 0.4 | 1.6 | 15,400 |
| superseded_by_statute | 0.0 | 2.8 | 1.4 | 1.3 | 1.6 | 0.8 | 10,300 |
| disapproved | 4.3 | 16.4 | 27.2 | 28.4 | 11.6 | 15.3 | 131,100 |
| receded | 0.1 | 0.9 | 1.2 | 2.3 | 1.7 | 0.9 | 11,000 |
| limited_to_facts | 0.2 | 0.4 | 0.8 | 0.2 | 0.3 | 0.2 | 2,400 |
| questioned | 13.8 | 79.8 | 95.6 | 67.2 | 52.9 | 74.3 | 445,000 |
| questioned_treatment | 4.2 | 20.3 | 26.9 | 17.9 | 12.7 | 19.0 | 115,300 |
| decline_to_follow | 0.0 | 3.1 | 3.9 | 0.6 | 1.9 | 2.7 | 12,200 |
| overruled_other_grounds | 0.2 | 12.3 | 13.1 | 4.9 | 5.2 | 6.2 | 45,700 |
| overrule_any | 35.0 | 147.8 | 176.8 | 335.8 | 163.8 | 631.4 | 1,676,100 |
| overruled_procedural | 4.2 | 6.8 | 22.8 | 49.4 | 27.0 | 74.1 | 228,200 |
| expressly_overrule | 0.7 | 1.1 | 2.8 | 6.4 | 5.9 | 113.4 | 85,000 |

### Decade breakdown (all strata pooled, unweighted)

| decade | n | head matter>=300 | Dissent section | Combined only | en banc header | unpublished any | CL |
|---|---|---|---|---|---|---|---|
| 1780 | 56 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1790 | 36 | 0.0% | 2.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1800 | 75 | 8.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1810 | 103 | 5.8% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1820 | 138 | 5.8% | 0.7% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1830 | 183 | 7.7% | 0.5% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1840 | 283 | 2.5% | 0.4% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1850 | 409 | 6.6% | 3.2% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1860 | 381 | 5.5% | 3.9% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1870 | 749 | 5.3% | 2.0% | 0.0% | 0.4% | 0.0% | 0.0% |
| 1880 | 1007 | 6.0% | 1.0% | 0.0% | 0.1% | 0.0% | 0.0% |
| 1890 | 1552 | 7.2% | 1.5% | 0.0% | 0.2% | 0.0% | 0.0% |
| 1900 | 1636 | 7.5% | 1.8% | 0.0% | 0.1% | 0.0% | 0.0% |
| 1910 | 1944 | 9.6% | 1.8% | 0.0% | 0.2% | 0.1% | 0.0% |
| 1920 | 2134 | 10.0% | 2.1% | 0.0% | 0.2% | 0.0% | 0.0% |
| 1930 | 2715 | 9.0% | 2.2% | 0.0% | 0.1% | 0.1% | 0.0% |
| 1940 | 2252 | 10.6% | 3.4% | 0.0% | 0.3% | 0.2% | 0.0% |
| 1950 | 2520 | 10.7% | 3.3% | 0.0% | 0.5% | 0.2% | 0.0% |
| 1960 | 3243 | 14.2% | 3.9% | 0.0% | 0.8% | 0.5% | 0.0% |
| 1970 | 4508 | 12.5% | 4.3% | 0.0% | 1.6% | 0.4% | 0.0% |
| 1980 | 5877 | 12.2% | 4.5% | 0.0% | 1.9% | 1.3% | 0.0% |
| 1990 | 6656 | 10.6% | 3.3% | 0.0% | 1.4% | 2.4% | 0.0% |
| 2000 | 7591 | 26.5% | 2.8% | 0.0% | 1.9% | 12.2% | 0.0% |
| 2010 | 8024 | 22.2% | 1.6% | 4.7% | 1.6% | 12.5% | 6.1% |
| 2020 | 1213 | 0.0% | 0.0% | 93.2% | 0.1% | 52.5% | 94.1% |

### Other section titles (top)

majority 52200, head matter 15081, dissent 1558, combined 1511, other:cap head matter 1024, concurrence 861, rehearing 402, concurring in part 252, lead 120, other:memorandum opinion 103, other:summary opinion 32, other:bench opinion 32, other:on the merits 7, other:t.c. opinion 7, remittitur 3, other:unanimous 2

### State intermediate districts recovered (sample, all strata)

| group | n | recovered | by route |
|---|---|---|---|
| AZ | 57 | 100.0% | docket 57 |
| CA | 405 | 32.6% | NONE 273, docket 125, name/text 7 |
| FL | 1071 | 40.1% | NONE 642, docket 294, name/text 135 |
| IL | 494 | 10.3% | NONE 443, docket 42, name/text 9 |
| IN | 191 | 39.3% | NONE 116, docket 75 |
| LA | 477 | 16.6% | NONE 398, name/text 79 |
| MO | 290 | 55.9% | docket 154, NONE 128, name/text 8 |
| NYAD | 2921 | 46.0% | NONE 1578, county 1325, dept 18 |
| OH | 184 | 52.7% | NONE 87, county 74, district 23 |
| TX | 2746 | 61.7% | NONE 1052, docket 903, text 791 |
| WA | 222 | 87.8% | docket 194, NONE 27, text 1 |

### dtype/pstat

[(('scotus', 'memorandum order'), 6412), (('scotus', 'opinion'), 739), (('scotus', 'per curiam'), 713)]
[(('state_last', 'published'), 9000), (('state_app', 'published'), 9000), (('state_trial_special', 'published'), 9000), (('fed_app', None), 8818), (('fed_trial_special', 'published'), 8810), (('scotus', None), 7864), (('unmapped', 'published'), 1285), (('scotus', 'published'), 1136), (('fed_app', 'published'), 182), (('fed_trial_special', 'nonprecedential'), 167), (('fed_trial_special', None), 16), (('fed_trial_special', 'precedential'), 7)]
