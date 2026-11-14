# Sources (accessed 2026-11-14)

Every file was fetched over HTTPS with no login, no CAPTCHA, no click-through, by a generic client. Each download sits
in its own folder under `raw/`; the zips are read in place (never extracted); all parsing is `python -I` from scripts
outside `raw/`. The files are byte-identical (sha256) to those recorded in `benchmarks/fjc_idb_appeals/SOURCE.md`;
this key uses a different, disjoint set of their rows (MAPPING.md, Unit).

## 1. FJC Integrated Database, appeals (Federal Judicial Center)

- Index: https://www.fjc.gov/research/idb (Appeals Data).
- `raw/idb_ap71to07/ap71to07.zip` ← https://www.fjc.gov/sites/default/files/idb/textfiles/ap71to07.zip
  (48,017,714 bytes, Last-Modified 2017-08-23) sha256 `53af858b0884e5b7b683410f24a331dc78a86655fb2fa052842670f1cc444bc0`;
  1,414,913 records + header.
- `raw/idb_ap08on/ap08on_0.zip` ← https://www.fjc.gov/sites/default/files/idb/textfiles/ap08on_0.zip
  (35,372,790 bytes, Last-Modified 2026-09-01; cases terminated FY2008 – June 30, 2026) sha256
  `05d545060b09542abf6cea0c4e1f0949eede037e23580aadcb37e240cfccd33c`; 1,000,613 records + header.
- Codebook `raw/idb_codebooks/codebook_2008_forward.pdf` ←
  https://www.fjc.gov/sites/default/files/idb/codebooks/Appeals%20Codebook%202008%20Forward%20rev%2002102021.pdf
  sha256 `3df2fdf1ea3c8762b8efbe76bfe37a56dbbd373dbf66266a67a9a5bb4ab38e0b` (text extracted to `work/codebook_2008.txt`
  by `pdftext.py`).
- Terms: no licence statement on the pages; site footer: "This website is produced and published at U.S. taxpayer
  expense. The Federal Judicial Center offers education and research for informational use." US government work;
  bulk files are the intended delivery.
- Variables used: `OUTCOME` (1 affirmed/enforced, 2 reversed/vacated, 3 affirmed in part and reversed/vacated in part,
  6 remanded, others), `DISP` (merits 1–3), `TAPEYEAR` (code era), `APPTYPE`, `PUBSTAT` ("Opinion or order prepared by
  the court to dispose of the appeal": 1 unpublished oral; 2/4/6 published; 3/5/7 unpublished written), `CIRCUIT`,
  `DOCKET` (appeal docket YYNNNNN), `DKTDATE`, `REOPEN`, `DDIST`, `DDOCKET` (district docket YYNNNNN), `DDKTDATE`,
  `APPDATE` (notice of appeal), `JUDGDATE` ("Date the final judgment/decree/order to an appeal was entered"),
  `APPELLAN`, `APPELLEE`.

## 2. CCAD `idb_crosswalk` (Sapiro-Gheiler & Kastellec, Comprehensive Courts of Appeals Database)

- Dataset https://doi.org/10.7910/DVN/XN2FVS, Harvard Dataverse version 2.0 (released 2026-09-11). Metadata
  `raw/ccad_meta/dataset.json` ← https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/XN2FVS
  sha256 `5cbc570d495cec27c83a0c7111567bbe48734f92bf5ec0c351b2263abe8a6785`.
- Licence (metadata): **CC BY 4.0** (http://creativecommons.org/licenses/by/4.0); no terms of use, no guestbook, file
  not restricted. Attribution: Sapiro-Gheiler & Kastellec, Comprehensive Courts of Appeals Database, Harvard Dataverse,
  doi:10.7910/DVN/XN2FVS.
- `raw/ccad_idb_crosswalk/idb_crosswalk.tab` ← https://dataverse.harvard.edu/api/access/datafile/13987073?format=original
  (15,575,911 bytes) sha256 `d4931cbf671a61a01266a73cdacb29c9450271cb02109dbd2cbe2d3a608ac774`.
- Used only to EXCLUDE rows: every IDB row named by the crosswalk (row number, primary or alt, or natural key) is
  outside this key. No CCAD disposition column is used.

## Corpus side (read only)

`graph/nodes.tsv`, `graph/courts.tsv`, `graph/edges.bin`, `round6/history/citeforms/edges_delta.tsv.gz`, and the
docket field of `round6/history/cache/<repo>*.meta.tsv.gz` for the district, bankruptcy and court of appeals repos.

## Build (all `python -I`, from this folder)

`parse_source.py` → `build_corpus.py` → `link.py` (→ `key.tsv`, `key_nodes.tsv`, `link_summary.json`);
`score.py --out <dir> --data <dir> --label <x>`.

Web requests used for this key: 1 search, 2 HEAD, 5 downloads.
