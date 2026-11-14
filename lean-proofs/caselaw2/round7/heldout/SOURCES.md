# Sources (round7/heldout)

All fetches used the generic client name `research-client/1.0`; no personal details were sent.

## 1. Supreme Court docket records — the source of the time-split key (in use)

| What | URL | Fetched (UTC) | Licence |
|---|---|---|---|
| One JSON docket record per docket number carried by a corpus Supreme Court node dated 2021-01-01 or later | `https://www.supremecourt.gov/RSS/Cases/JSON/<docket>.json` | 2026-11-13, 22:58–23:10 | Work of the United States government (17 U.S.C. §105): public domain |

- Files: `src_scdocket/json/<docket>.json` (bytes as served). `src_scdocket/manifest.tsv` has one line per request:
  docket, URL, UTC time, HTTP status, bytes, sha1 of the bytes. Fetcher: `fetch_dockets.py` (1 request per second).
- `src_scdocket/manifest.sha1` holds the sha1 of `manifest.tsv` (a3a6cb8085d7c9edb5f52981285da6b332909f5b); 509 requests, all HTTP 200, first 2026-11-13T22:59:46Z, last 23:10:16Z.
- Fields used: `LowerCourt`, `LowerCourtCaseNumbers`, `LowerCourtDecision`, `PetitionerTitle`, `RespondentTitle`,
  and the Clerk's judgment entry in `ProceedingsandOrder` ("Judgment REVERSED and case REMANDED.", …).

## 2. Shadow Docket Database (downloaded, then handed over; NOT used by the key)

Harvard Dataverse, doi:10.7910/DVN/89VEX8 ("Supreme Court Shadow Docket Database, Version 2.0 (November 2025)",
Kastellec & Taboni), deposit version 1.0 released 2025-12-05. Licence **CC0 1.0** (dataset metadata
`license.name = "CC0 1.0"`). Downloaded 2026-11-13 through the Dataverse access API
(`https://dataverse.harvard.edu/api/access/datafile/<id>?format=original`). MD5 of each file equals the
deposit's.

| File | Dataverse file id | Downloaded (UTC) | sha1 |
|---|---|---|---|
| `src/dataset_meta.json` (dataset record, `api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/89VEX8`) | – | 2026-11-13T22:46Z | f138980c127accba615064ddc200e410fa86a883 |
| `src/README.txt` | 13204509 | 2026-11-13T22:46:36Z | c78241699532b79f4cae535b55408f50c72ca069 |
| `src/shadow_docket_database_codebook_v2_0.pdf` | 13204495 | 2026-11-13T22:46:37Z | 834882acc599aaab8c9a7f86ade82d5b9a3de221 |
| `src/shadow_docket_database_v2-0.csv` | 13204527 | 2026-11-13T22:48:23Z | 9f9f5832a46acfc1900eb29fff179662f6c6ed57 |

Handed over at 22:56 (lead's ruling: the `benchmarks/` agent owns this key). Not extended, not linked.
