# Sources (accessed 2026-11-13)

Every file was fetched over HTTPS with no login, no CAPTCHA, no click-through. Each download sits in its own folder
under `raw/`; all parsing is `python -I` from scripts outside `raw/`.

## 1. FJC Integrated Database, appeals

- Index: https://www.fjc.gov/research/idb (filter "Appeals Data": `?field_type_tid=6881`), pages saved in
  `raw/fjc_pages/`.
- SY1971–FY2007 page: https://www.fjc.gov/research/idb/appellate-cases-filed-and-terminated-sy-1971-through-fy-2007
  - `raw/idb_ap71to07/ap71to07.zip` ← https://www.fjc.gov/sites/default/files/idb/textfiles/ap71to07.zip
    sha256 `53af858b0884e5b7b683410f24a331dc78a86655fb2fa052842670f1cc444bc0`; extracted
    `raw/idb_ap71to07_x/ap71to07.txt` (1,414,913 records + header, file date 2017-06-22)
    sha256 `34def6b4d5703c7f955ee19b20b4f3e11edd43696b740f4bdf19702916ec1da4`.
  - Codebook `raw/idb_codebooks/codebook_1971_2007.pdf` ←
    https://www.fjc.gov/sites/default/files/idb/codebooks/Appeals%20Codebook%201971-2007.pdf
    sha256 `f453ac597a368c7aded7c4b2afbd7e60c0b793e222149a83dcaa3b2751bb6e72`.
- FY2008–present page: https://www.fjc.gov/research/idb/appellate-cases-filed-terminated-and-pending-fy-2008-present
  ("Cases terminated in FY 2008 through June 30, 2026 and cases pending as of June 30, 2026")
  - `raw/idb_ap08on/ap08on_0.zip` ← https://www.fjc.gov/sites/default/files/idb/textfiles/ap08on_0.zip
    sha256 `05d545060b09542abf6cea0c4e1f0949eede037e23580aadcb37e240cfccd33c`; extracted
    `raw/idb_ap08on_x/ap08on.txt` (1,000,613 records, file date 2026-09-01)
    sha256 `8acd1cafb4f986b045e3911cd95ea4dbf6291c263bf8af2c9bbee2365e904b48`.
  - Codebook `raw/idb_codebooks/codebook_2008_forward.pdf` ←
    https://www.fjc.gov/sites/default/files/idb/codebooks/Appeals%20Codebook%202008%20Forward%20rev%2002102021.pdf
    sha256 `3df2fdf1ea3c8762b8efbe76bfe37a56dbbd373dbf66266a67a9a5bb4ab38e0b`.
- Terms: no licence statement on the pages. The page footer reads: "This website is produced and published at U.S.
  taxpayer expense. The Federal Judicial Center offers education and research for informational use." Bulk files are
  the intended delivery. US government work.
- Variable used: `OUTCOME` (what the court of appeals did to the judgment below; SY85+: 1 affirmed/enforced,
  2 reversed/vacated, 3 affirmed in part and reversed/vacated in part, 5 dismissed, 6 remanded, 7 other,
  9 certificate of appealability denied; SY71–84: 1 affirmed, 2 reversed-vacated-denied, 3 affirmed and reversed,
  4/5 dismissed, 6 remanded, 7 transferred), with `DISP`, `APPTYPE`, `DDIST`, `DDOCKET` (YYNNNNN), `DDKTDATE`,
  `APPDATE`, `JUDGDATE`, `APPELLAN`/`APPELLEE`, `TAPEYEAR`.

## 2. Comprehensive Courts of Appeals Database (CCAD), Sapiro-Gheiler & Kastellec

- Dataset: https://doi.org/10.7910/DVN/XN2FVS (Harvard Dataverse, version 2.0, released 2026-09-11). Metadata via
  https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/XN2FVS saved as
  `raw/ccad_meta/dataset.json` (sha256 `5cbc570d495cec27c83a0c7111567bbe48734f92bf5ec0c351b2263abe8a6785`).
- Licence (from the metadata): **CC BY 4.0** (http://creativecommons.org/licenses/by/4.0). No guestbook, no terms
  of use text, files not restricted. Attribution: Sapiro-Gheiler & Kastellec, Comprehensive Courts of Appeals
  Database, Harvard Dataverse, doi:10.7910/DVN/XN2FVS.
- Files (Dataverse access API `https://dataverse.harvard.edu/api/access/datafile/<id>`):
  - `raw/ccad_idb_crosswalk/idb_crosswalk.tab` ← id 13987073 `?format=original` (CSV; 284,691 rows)
    sha256 `d4931cbf671a61a01266a73cdacb29c9450271cb02109dbd2cbe2d3a608ac774`.
  - `raw/ccad_codebook/codebook_09-2026.pdf` ← id 14201761, md5 `f0df952c30145025c6c3a34292c049da` (matches
    Dataverse), sha256 `fe70b6a491f84ecb437fce7d1bc07d8108765d20b98594dc91b85b24fcc990a3`.
  - `raw/ccad_rename/ccad_09-2026.stata_rename.tab` ← id 14201763 (column list)
    sha256 `bc3192b58cc5332004493e32d81919fb9c437a7277ab68ff9f1890d4e8bf9997`.
  - `raw/ccad_main/ccad_09-2026.csv.gz` ← id 14201785 (777,865,422 bytes; Dataverse md5
    `a45bf6b74e512aaaf684e7a06de0293f`) — sha256 below.
- Used: `idb_crosswalk` (`caseid` → `idb_idx` = `<file>:<0-based data row>` of the FJC files; verified against the
  natural key circuit+docket+dktdate+tapeyear: 284,026 agree; 665 recent FY2026 rows had moved in the re-issued
  cumulative file and 663 were re-found by natural key, 2 not) and from the main file only `caseid`, `source`,
  `citation`, `docket_number`, `circuit`, `decision_date`, `is_enbanc`. CCAD's own LLM / regex disposition columns
  and its merged IDB/Songer columns are **not** used.
