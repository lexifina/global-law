# Source: Brace & Hall, State Supreme Court Data Project (Harvard Dataverse doi:10.7910/DVN/Z80F7P)

Accessed 2026-11-14 (UTC) through the Dataverse native API, no login. Producers Rice University and Michigan State
University (Paul Brace, Melinda Gann Hall); dataset version 1.0, released 2009-01-21, distribution date 2007.

## Licence / terms (quoted from the dataset record, `raw/dataset_json/dataset.json`)

- `license`: `{"name": "CC0 1.0", "uri": "http://creativecommons.org/publicdomain/zero/1.0", "rightsIdentifier": "CC0-1.0"}`
- `notesText`: "Subject: STANDARD DEPOSIT TERMS 1.0 Type: DATAPASS:TERMS:STANDARD:1.0 Notes: This study was deposited under
  the of the Data-PASS standard deposit terms. A copy of the usage agreement is included in the file section of this
  study."
- `termsOfUse`: empty. No file is restricted (`restricted: false` for all ten files).

Description (quoted): "We are in the process of assembling data on the courts of last resort in all fifty states
during their 1995 through 1998 sessions. By late 2002, when our current project ends, we will have gathered data for
approximately 21,000 decisions …" (the July 2005 beta file has 28,341 records).

## Files downloaded (each in its own new folder under `raw/`; parsed only with `python -I`)

| Folder / file | Dataverse URL | sha256 |
|---|---|---|
| `dataset_json/dataset.json` | https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/Z80F7P | `aabf625ec8928650361cb2e2bbf734beb64121a8b6dc1de0fb8d729c29503caf` |
| `case_tab_tsv/NSF95-98_beta_July2005.tsv` (tab export of "NSF 95-98 Beta Version_July 2005.tab", file id 656541; **the file parsed**) | https://dataverse.harvard.edu/api/access/datafile/656541 | `8f142e00cc1e48e9ea7d1af443229f82b9a09c68fb10c87cf5063ec0f67bc9ab` |
| `case_tab/NSF95-98_beta_July2005.tab` (same file, original Stata format; kept, not parsed) | https://dataverse.harvard.edu/api/access/datafile/656541?format=original | `99cbb749691543bd612c47906bf8c69e90f577127f89f0b9e62ec9f64b2f5d15` |
| `codebook/Revised_Codebook_8-05.pdf` (file id 656534) | https://dataverse.harvard.edu/api/access/datafile/656534 | `613fa0f38e6d014d73b38615511d8d8577b65800c2a6749f01d1cb2ba35af68a` |
| `codebook_appendix/Codebook_appendix.pdf` (hints; file id 656535) | https://dataverse.harvard.edu/api/access/datafile/656535 | `ef06d6d054973dac714985c530de5c26b2b885515b0edf02dc350fdbe24dd9dd` |
| `coding_rules/Coding_Rules.mht` ("State Supreme Court Project Coding Rules", file id 656532) | https://dataverse.harvard.edu/api/access/datafile/656532 | `536c7a86083f4dd695b2c48b65432de5a28c218981f115157b5a2a22962af8d1` |

Dataverse md5 of the stored .tab (original): `51bf913ca9c2f3b991cc1a357adaf98e`. Text extracts of the codebook, the
appendix and the coding rules are in `work/` (pdftotext; quoted-printable decoded), for reading only.

Not downloaded: the judge-level files (`Judge Level Data Set.tab`, `JudgeLevelDataSet.dta.zip`), the data
collection template, the beta zip and the reliability reports — not needed for the disposition key.

## Codebook variables used

| Variable | Meaning (codebook) | Use |
|---|---|---|
| `state_2` | state code 1–50, alphabetical (1 Alabama … 50 Wyoming) | state |
| `title_p1`, `title_p2` | case title parties as in the reporter's table of contents | identity check |
| `docket`, `docket_n` | supreme court docket number; number of dockets in the opinion | reference only |
| `reporter`, `rep_vol`, `rep_page` | regional reporter (1 A., 2 N.E., 3 N.W., 4 P., 5 S.E., 6 So., 7 S.W.; 2d series in 1995–98), volume, first page | citation of the supreme court decision |
| `decs_yr`, `decs_mo`, `decs_day` | date of the state supreme court decision (rehearing dates not used, coding rules) | date |
| `juris` | manner of taking jurisdiction | reference only |
| `rev_ct` | "Court being reviewed by the state supreme court": 1 state trial court of limited jurisdiction, 2 of general jurisdiction, 3 state intermediate appellate court, 4 state supreme court, 5–7 federal courts, 55 other, 88 not relevant (entity not on the state court chart, e.g. an agency) | which decision below; level |
| `genissue` | 1 criminal, 2 civil government, 3 civil private, 4 juvenile, 5 other | which disposition variable |
| `ca_disp`, `cg_disp`, `cp_disp`, `jv_disp` | "Supreme Court's disposition of the lower court": 1 affirmed; 2 reversed (or vacated); 3 reversed (or vacated) and remanded; 4 affirmed in part and reversed in part (or modified, or affirmed and modified); 5 … and remanded; 6 petition or motion granted; 7 petition or motion denied; 55 other ("If the supreme court affirms and remands, code 55 - Other", coding rules); 88 not relevant | the key variable (MAPPING.md) |

The coding rules also say that for multi-docket opinions "entries for all fields … are based on the information
contained in the opinion pertaining to the docket number corresponding to the case title listed in the regional
reporter table of contents".
