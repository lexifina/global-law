# Source: Beim, Hirsch & Kastellec — en banc review of courts of appeals panel decisions (replication data)

Accessed 2026-11-14 (about 05:15 GMT) by the round-11 dataset agent `bench11` through the Harvard Dataverse native API,
no login, no click-through, no CAPTCHA. Two requests for this dataset (metadata, data file).

- Dataset: "Replication Data for: Signaling and Counter-Signaling in the Judicial Hierarchy: An Empirical Analysis of En
  Banc Review", Deborah Beim (Yale), Alexander Hirsch (Caltech), Jonathan Kastellec (Princeton), AJPS Dataverse,
  doi:10.7910/DVN/2EJIZJ (https://doi.org/10.7910/DVN/2EJIZJ), version 1.4, released 2016-04-01. Article: American Journal
  of Political Science 60(2), 2016. Replication verified by the Odum Institute (record `notesText`).
- Part of the data (`source_of_cases` = `clark_ebs`) is merged by the authors from Tom S. Clark, "A Principal Agent Theory
  of En Banc Review", Journal of Law, Economics & Organization 25(1): 55–79 (2009) (codebook).

## Licence / terms (quoted from the dataset record, `raw/dataset_json/dataset.json`)

- `termsOfUse`: "This dataset is made available under a Creative Commons CC0 license with the following
  additional/modified terms and conditions: " (nothing follows: no additional terms).
- `disclaimer`: "The *American Journal of Political Science* and the Odum Institute for Research in Social Science are not
  responsible for the accuracy or quality of data uploaded within the *AJPS* Dataverse, for the use of those data, or for
  interpretations or conclusions based on their use."
- No `termsOfAccess`, no guestbook; the one file is `restricted: false`.

## Files (each download in its own new folder under `raw/`; parsed only with `python -I` from scripts outside `raw/`)

| Folder / file | URL | bytes | sha256 | sha1 |
|---|---|---|---|---|
| `dataset_json/dataset.json` | https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/2EJIZJ | 8,816 | `958bdb1102ac5cf1ae1499eae18ebc4b0d0ba7af5cb043f11b1c8559e4dd1fdb` | `5bf3ab058e67afbfde40063d2e16e858703ff13e` |
| `bhk_zip/bhk_files_for_dataverse_replication.zip` | https://dataverse.harvard.edu/api/access/datafile/2549511 | 1,121,114 | `afde18fbac0db96ba3f80a0c677db7fa387f778370b79016155252a4d5b4fd92` | `1f50656a8189b6a017a2d8c586a7d019ea645e46` |

The zip's MD5 (`4a8428563194584ac2c068c5b353b3f4`) equals the MD5 Dataverse publishes for file 2549511. Members extracted
by `zipfile` (no code from the zip executed) into `raw/bhk_zip_x/` (`__MACOSX` entries skipped):

| file | bytes | sha256 |
|---|---|---|
| `bhk_main_data.csv` (used) | 1,665,513 | `405f56e528a01c4cd0fd5dc1b5c2199f183dae69b4b15ce2c839454772bcc81d` |
| `Codebook.docx` (read; text in `work/codebook.txt`) | 129,524 | `ec1de253e9fae0130ab9eb11c0d311d566886629586db3a2032db75c7584ceea` |
| `readme.txt` (read) | 1,643 | `0897f106918f09f966481124f12191e1f7a9e4736b1ede773323fc545f49062e` |
| `bhk_main_data.dta` | 5,223,124 | `a79ce7164e24f4de1760552fdd9a72e218b2dfbd1df3dd3a2e55c063a12d46a4` |
| `bhk_main_replication_script.R` (not run) | 51,127 | `a673624367316545599d3b58562d4a1747ed4bc7738078351943cf155373ee5b` |
| `build_weights_for_bhk_data.R` (not run) | 6,899 | `d508e690621e84d6feb34950d092efb3bf7f34efff2cfce84e35294216cd5f7a` |
| `.Rapp.history` | 69,764 | `a32016c4803cd29619e8ed3617006f8c35bbc89e077b9172b2673be09469a052` |
| `circuit_data.csv` | 7,355 | `0a4c2c16e5f7bf51092e08fddcc9cfcf5845ffc68505309fcd9b750f196eb1de` |
| `songer_weight_data.csv` | 10,569 | `854032403eac4ce9cea4740a030a1a86f0c27f8f89f3fd7f761667d0bb12b2f6` |
| `songer_weight_data.dta` | 5,083 | `e18603636f0302db1033d4ebb9f5af94158e9340926927c351b47e08df03e1ba` |
| `songer_codebook.pdf` | 307,035 | `455d98247f6488a0e1211a04e93a944d2878dbc3343e359bbb8296693e9767de` |
| `Figure_5.pdf` | 8,670 | `bccede64f3a2022a6f498935ba6b466e5852bc1dbda85c71c633c49501546a87` |
| `Figure_6.pdf` | 7,540 | `e1c7467d25ff546f1d22c61b68f36e2cac1fc4bc2e257b39a41384881329c2b5` |
| `Figure_A1.pdf` | 6,254 | `821cc8fbb62c0d15aa776dc72fd8917d0105dd7008c50f736986adc1ce184447` |

## What the data is, and the variables used

`bhk_main_data.csv`: "a choice-based sample of cases decided by three-judge panels of the Courts of Appeals between 1986
and 2002. Every row is one case." (codebook). 5,589 rows: 4,818 from the Songer / Kuersten–Haire random sample (not used
here) and 771 en banc rows (`bhk_ebs` 327 coded by the authors, `clark_ebs` 444 from Clark 2009), all with `eb_grant` = 1.

| Variable | Codebook text | Use |
|---|---|---|
| `p_cite` | "Federal Reporter citation to the panel decision." | link to the panel decision (scored node) |
| `p_year`, `p_month`, `p_day` | date of the panel decision | link date window |
| `circuit` | circuit (1–11, 12 = D.C.) | link court |
| `eb_grant` | "Was the panel decision reheard en banc?" | selects the items (all 1) |
| `eb_reverse` | 1 if the en banc decision's direction (liberal/conservative) is opposite to the panel's, 0 if the same | sub-class R / S / U |
| `eb_cite`, `eb_year`, `eb_month`, `eb_day` | "Federal reporter [citation] to the en banc decision" and its date | link confirmation, `recall_by_enbanc` |
| `source_of_cases` | `bhk_ebs` (coded by the authors), `clark_ebs` (Clark 2009), `songer …` | selects the en banc rows |
| `casenum_songer_original` | "Unique identifier from Songer database" (empty for every en banc row) | overlap check |
| `unique_id_new`, `mult_panel`, coders' notes | identifiers and notes | kept in `work/items.tsv` |

Overlap with earlier keys: the Songer-sample rows (the population of `songer_treat` and of the Shepardized courts of
appeals key) are not items; no en banc row carries a Songer case number. No other key uses this deposit or Clark's en banc
list (checked against every `benchmarks/*/SOURCE.md` and `MAPPING.md`).
