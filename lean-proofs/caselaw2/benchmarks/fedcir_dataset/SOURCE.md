# Source: Federal Circuit Dataset Project — document dataset (Rantanen, University of Iowa)

Accessed 2026-11-14 (about 03:50 GMT) by the round-10 dataset agent `bench10` through the Harvard Dataverse native
API, no login, no click-through, no CAPTCHA. Three requests in total (metadata, data file, codebook).

- Dataset: "Federal Circuit Document Dataset", Jason Rantanen (University of Iowa), Harvard Dataverse
  doi:10.7910/DVN/UQ2SF7 (https://doi.org/10.7910/DVN/UQ2SF7), first published 2021-12-14; version 9.0, released
  2026-07-06. Project page: https://empirical.law.uiowa.edu/compendium-federal-circuit-decisions (not fetched).
- Description (quoted from the record): "Document dataset for the Federal Circuit Dataset Project. Keyed to Docket
  dataset using the Appeal_Dockets field. The most recent version of the document dataset is the appeals 2025-12-31
  documents release."

## Licence / terms (quoted from the dataset record, `raw/dataset_json_docs/dataset.json`)

- `license`: `{"name": "CC0 1.0", "uri": "http://creativecommons.org/publicdomain/zero/1.0", "rightsIdentifier": "CC0-1.0"}`
- `termsOfUse`: none; `termsOfAccess`: none; every file `restricted: false`.

## Files downloaded (each in its own new folder under `raw/`; parsed only with `python -I`)

| Folder / file | URL | bytes | sha256 | sha1 |
|---|---|---|---|---|
| `dataset_json_docs/dataset.json` | https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/UQ2SF7 | 9,992 | `cd2fd702f03100668138d99b416b8ba055a24d0a7e785610b6a643f9c127b001` | `7ef9351106e0113807837eb27db313e36f1df5ff` |
| `docs_2025_12_31/cafc_documents_2025-12-31.tab` ("2025-12-31 CAFC documents annual export.tab", file id 14058366; **the file parsed**) | https://dataverse.harvard.edu/api/access/datafile/14058366 | 14,348,975 | `1e95dc61feb54b0238c6f5da2ce7c50880a7844e0d7eca07cadf8b80857839c0` | `b27061f7a12bd360031d6f3ab482020e8e79b1dd` |
| `codebook_docx/codebook_2023-01-06.docx` ("Codebook for the Compendium of Federal Circuit Decisions - 2023-01-06.docx", file id 6907843) | https://dataverse.harvard.edu/api/access/datafile/6907843 | 67,342 | `aaaf8e220cf9dd3c105e61228c6141b40cc8990aa3e072500bb1aa3062fed45f` | `e12b3b4297e137dac279db8871b24271810d5385` |

The codebook's MD5 equals the MD5 Dataverse publishes (`80ca61bff5056aaa6bed41fdac0fa1e7`). The data file is
Dataverse's ingested tab-separated archival copy (what `api/access/datafile/<id>` serves by default); its MD5
(`6d84fd6dee37699cd749db8e13c75c63`) differs from the published MD5 of the uploaded original
(`8b57a166b6048bfecde237735aed8fd8`, text/tsv) as expected for ingested files. 29,240 documents, 52 columns,
`docYear` 2001–2025. Codebook text extracted to `work/codebook.txt` (`explore.py`, standard library zip/XML).

## Variables used (codebook meaning)

- `uniqueID` — document id (key-item id `fc:<uniqueID>`; split key for unlinked items).
- `caseName`, `appealNumber`, `docDate` (m/d/yy), `docType` (Opinion, Rule 36, Rule 36 Judgment, Order - Merits, …),
  `PrecedentialStatus`, `enBanc`, `DataSource`.
- `origin` (DCT, CFC, CIT, CAVC, MSPB, PTO, …) and `TribOfOrigin` (district, e.g. `D.Del.`, `E.D.Tex.`) — the tribunal
  whose decision is reviewed.
- `DispGeneral` — "the appellate court's disposition of the appeal": Affirmed / Reversed / Vacated /
  Affirmed-in-part / Dismissed / Denied / Granted / Withdrawn / Transferred / Remanded / Other (definitions quoted in
  MAPPING.md).
- `Replaced` — whether the document was later replaced (revised panel opinion, en banc, Supreme Court, GVR); used
  only to exclude.
- `Full_Cite` — Federal Reporter citation of the document (populated mainly for district-court appeals); used to
  find the Federal Circuit decision in the corpus.
- Read but not used for linking: `Orig_Trib_Dockets` (the corpus node list has no docket field).

Human-coded (two coding stages, codebook "Coding Process"); independent of any citator and of the corpus.
