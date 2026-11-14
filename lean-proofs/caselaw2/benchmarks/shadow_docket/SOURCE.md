# Source: Supreme Court Shadow Docket Database, v2.0 (Kastellec & Taboni)

- Citation: Jonathan P. Kastellec and Anthony R. Taboni, "Supreme Court Shadow Docket Database, Version 2.0
  (November 2025)"; Dataverse "Replication Data for: A Database of the United States Supreme Court's Shadow Docket,
  1993-2025", doi:10.7910/DVN/89VEX8 (https://doi.org/10.7910/DVN/89VEX8), version 1.0, released 2025-12-05.
- Licence: **CC0 1.0** (dataset metadata `license`: "CC0 1.0", http://creativecommons.org/publicdomain/zero/1.0).
  No terms of use / guestbook; every file used is public (`restricted: false`). No login, click-through or
  CAPTCHA was involved.
- Accessed 2026-11-13 with `curl` from the Dataverse API (`https://dataverse.harvard.edu/api/access/datafile/<id>`;
  metadata from `https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/89VEX8`).
  Each file in its own empty folder under `raw/`; untrusted; parsed only with `python -I` (stdlib; the codebook PDF
  was converted to text with PyMuPDF, also under `-I`). Every file's MD5 equals the MD5 Dataverse publishes.

| folder | file | Dataverse id | bytes | sha256 |
|---|---|---|---|---|
| raw/dataverse_meta | dataset.json (API metadata) | – | 56,107 | f109759483844eca4797ed603af3ce35519b69b6ada2120197dc5ec286a8fb86 |
| raw/main | shadow_docket_database_v2-0.csv | 13204527 | 278,378,078 | 4051220057bf94c503d3299350d1a142a167764b5bd18a1162e7f95c4a37a09d |
| raw/codebook | shadow_docket_database_codebook_v2_0.pdf | 13204495 | 467,326 | 4275f8ac8394300c97b7080e013b42295383f4b45896806e874bb7785fbe6bc3 |
| raw/readme | README.txt | 13204509 | 7,398 | 6c5ff5104403893653bc96b4b44a0dc2c1e4a8a0825b5f6ebe32490501e8b663 |
| raw/docket_info | Docket_Information_1997_2024.xlsx (not used: no date column) | 13204519 | 35,997,752 | afecd9608f44182676abbb28a34372e1473f62417f9cdb6da845345cfa882866 |
| raw/dockets_1996_2001 | Supreme_Court_Dockets_Raw_Text_1996_2001.json | 13204477 | 72,024,556 | bebfd8ba86ea2a40c15ef87b862b83537022cb18dead11c9968f9146c41db8ac |
| raw/dockets_2001_2016 | Supreme_Court_Dockets_Raw_Text_2001_2016.json | 13204491 | 601,417,581 | f4c8e17142b68ac0e4aadd35afa29ac08f91e49c98777c44450c18dec9f99c06 |
| raw/dockets_2017_2024 | Supreme_Court_Dockets_Raw_Text_2017_2024.json | 13204528 | 244,132,888 | 9f29a07eb8bc1701b1cf015d242adf3a054fa37bea5269e855ce69716cfc9d4d |
| raw/dockets_missing | Supreme_Court_Dockets_Raw_Text_Missing.json | 13204525 | 6,252,486 | 722aa6e34b3e7610aceaaa3c17962c8dc36188881eb9b0881ac86bb9a701c9c3 |

## What the variables mean (codebook v2.0, quoted)

- One CSV row per docket × order action (377,448 rows), parsed from the Journal of the Supreme Court, terms
  1993–2024 (orders to mid-2025).
- `action_class`: "The class or type of an order. We code each order into the following mutually exclusive
  categories", among them: **GVR** "Grants, vacates, and remands a case to the lower court in light of a related
  opinion of the court. The grant is coded separately as Certiorari."; **Reversal** "Reversal of decision by lower
  court"; **Vacate** "Motion to vacate or decision by the court to vacate order"; **Vacate and Remand** "Motion to
  vacate and remand or decision to vacate and remand"; **Affirmed** "Judgment affirmed"; **Affirmed in Part**
  "Judgment affirmed for some claims and reversed for others"; **Certiorari** "Grants, denies, or dismisses a
  petition for certiorari. Includes the grant part of a GVR."; **DIG** "Court dismisses certiorari as improvidently
  granted"; **Dismiss** "Request to dismiss appeal parties or dismissal of appeal by court"; **Lack of Quorum**
  "Judgment is affirmed due to lack of quorum by the court"; **Rehearings** "Asks the court for a rehearing".
- `relief`: Denied / Dismissed / Granted / Granted/Denied / Missing; NA = not applicable (e.g. GVRs).
- `lower_court`: "The last lower court to hear the case before it reached the Supreme Court. Complete coverage
  begins in the 1997 term." `lower_docket_no`: "Docket number(s) of the corresponding to the lower court
  decision(s). Complete coverage begins in the 1997 term." (CSV column names `lower_ct`, `lower_docket`.)
- The raw docket JSONs are the Supreme Court docket pages (1996–2024) the authors scraped; we read only
  `Decision Date:` (the lower court's decision date), `Rehearing Denied:` and `Discretionary Court Decision Date:`
  from them (`docket_dates.py` → `work/docket_dates.tsv`: 203,345 dockets, 185,145 with a decision date). This is
  how the date sanity check is made exact.

## Counts (`work/profile.txt`, `items.py`)

Rows by `action_class` × `relief` (largest): Certiorari/Denied 203,073; Admission 108,197; Rehearings/Denied
19,067; Certiorari/Granted 6,375; GVR 3,313; Certiorari/Dismissed 2,449; Reversal 159; Vacate and Remand/NA 142;
Affirmed 69; Vacate/NA 59; DIG 19; Affirmed in Part 6.

Pooled per Supreme Court docket (MAPPING.md classes): NEG 3,611 (GVR 3,311, vacated 141, reversed 159); PART 6;
CLEAN 205,472 (cert denied 202,917; cert dismissed / appeal dismissed 2,448; affirmed 88; DIG 19); MERITS 2,800 and
OTHER 11,991 not scored. Items with a lower docket number: NEG 3,311, CLEAN 183,859.

**Cert denials are the overwhelming majority** (≈ 98.6% of scoreable items, ≈ 98% of linked decisions). They are
not sampled: every linked one is scored, and `clean` is reported as its own metric, never pooled with recall, so the
size of the clean set does not dilute or inflate recall. The clean rate is also broken down by sub-class in
`extra_metrics` (cert denied / dismissed / DIG / affirmed).

## Known limits of the source

- No lower docket before the 1996–97 terms: 22,310 scoreable items (mostly 1993–1996) cannot be linked.
- `Reversal` includes some summary dispositions whose text says "Judgment vacated" (the class is about the order
  form, not the verb); both are NEG here, so this does not affect scoring.
- `action_text` of a multi-docket order is the text of the last docket of the group (codebook §7).
- The order's `lower_ct`/`lower_docket` is the court that last heard the case; for state cases it is sometimes the
  state supreme court that denied discretionary review, while the decision on the merits is the intermediate
  court's.
