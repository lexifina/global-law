# SOURCE — state overruled tables

Pre-1930 tables of overruled cases, scanned by Google (identifiers ending `goog`) or Cornell (`cu…`) and hosted by the
Internet Archive. All five used books were published in the United States between 1838 and 1922 and are in the
public domain in the US (published before 1930; the Google scans carry IA `possible-copyright-status:
NOT_IN_COPYRIGHT`; the Cornell scans carry no status field but are 1893 imprints). Only the IA OCR text layer
(`_djvu.txt`) and its word-coordinate twin (`_djvu.xml`) were downloaded: no page images, no login, no CAPTCHA,
3 s between requests, `scripts/ia_fetch.py`, run with `python -I`. Downloaded 2026-11-13 (UTC times below).
The variable taken from each book: "case X (citation) was overruled [denied, doubted, …] by case Y (citation)".
The published key (`key.tsv`, `secondary_pairs.tsv`) stores only these facts plus a ≤150-character OCR quote and the
scan leaf for provenance. The OCR files stay in `raw/` (public domain) for reproducibility.

## Used

| table id | IA identifier | Book | Year | File | Bytes | sha256 | Fetched (UTC) |
|---|---|---|---|---|---|---|---|
| georgia1922 | `casesingeorgiar00appegoog` | Hugh Downing, *Cases in Georgia Reports and Georgia Court of Appeals Reports that have been overruled, doubted, criticised, or modified* | 1922 | _djvu.txt | 95545 | 2ea88e459cbcdfc6961b42a556097673d19d3c45f8d94f99ac93c2b597eb9a00 | 23:08:00 |
| | | | | _djvu.xml | 1001027 | 43333c5d928c9e37435658cd24c324846e8dacbeb677bc03d36ca4bea8f136e1 | 23:12:59 |
| labatt1860 | `atablecasesinca00labagoog` | Henry J. Labatt, *A Table of Cases in California as Affirmed, Overruled, Modified, Commented upon* | 1860 | _djvu.txt | 110827 | 4938e95246e4eeb60e1c3c216891ef174442ef6d3adeb5dbe509741a52d3fff1 | 23:08:15 |
| | | | | _djvu.xml | 1141609 | ff94ce1e83953b3301a9a8a5b7deb70a2de8e0561f382295977daeffd72b508f | 23:13:06 |
| desty1874 | `californiacitat00destgoog` | Robert Desty, *California Citations: an alphabetical table of all the cases cited in the opinions of the Supreme Court of California* (vols. 1–46) | 1874 | _djvu.txt | 1596458 | 04ec39fb719c1de1ddee82f6e04435debde940aac9a3b067288c1544a3bc1e18 | 23:10:59 |
| | | | | _djvu.xml | 18652990 | 17b6decd386f41e3ab96d751a7652b1c0af322cdf33e35e14a4c5b43daab1a95 | 23:13:13 |
| greenleaf1838 | `acollectioncase01greegoog` | Simon Greenleaf, *A Collection of Cases Overruled, Denied, Doubted, or Limited in their Application*, 3rd ed. (American entries only) | 1838 | _djvu.txt | 922937 | b2af9a062ad2f346be32a9990e83753fa37e7a06662f172569b4e237a56e0ebd | 23:10:53 |
| | | | | _djvu.xml | 9446858 | 7f9395e9c74bff46ca3976929b973fd7a115dbd88bc9f0d216058065991e23ca | 23:13:23 |
| benjamin1893 | `cu31924022823318` | Wayland E. Benjamin, *New York Cases Reported or Cited, 1887–1893* | 1893 | _djvu.txt | 4602175 | 3d4e03fa6decbc3161dad09230f71a96bf84a68439f48840ddf1555039d92572 | 23:10:48 |
| | | | | _djvu.xml | 63917934 | 08ee2f609a1056384106a950a97bf198a7951d7c046983dd81ff2740caf5d4d7 | 23:13:36 |

URLs: `https://archive.org/download/<identifier>/<identifier>_djvu.txt` and `…_djvu.xml`; item pages
`https://archive.org/details/<identifier>`; metadata from `https://archive.org/metadata/<identifier>`
(`work/ia_meta/`).

## Inspected and skipped (text layer downloaded, checked, deleted)

| IA identifier | Book | Why skipped |
|---|---|---|
| `kingleonardscal00courgoog`, `…01…` (sha256 d8f13cc0…, 0f5bdcdf…) | King & Leonard's California Citations, 1894 | Shepard's-style superscript symbols; OCR unusable |
| `cu31924017679824` (c6bddf8f…) | Parker, Digest of N.Y. Court of Appeals reports 126–153, 1898 | only ~10 "overruling" entries |
| `nebraskasynopti00courgoog` (7b01dff2…) | Nebraska Synoptical Digest, 1910 | this is vol. 1; the table of overruled cases is in vol. 3; inline bracket notes only |
| `northcarolinacr00jerogoog` (97de7643…) | N.C. Criminal Code and Digest, 1899 | 13 "overrul" hits only |
| `notestokentucky00unkngoog` (74b7466a…) | Notes to the Kentucky Reports, 1907 | usable (~70 hits) but cut for time; first candidate for a later round |
| `acollectionover00towngoog` (e12c21b9…) | Greenleaf & Townshend 1856 | laid out as a multi-column grid; OCR reading order broken |
| `cu31924061139832` (e9248751…) | Desty, Digest of California reports 34–46, 1875 | overlaps Desty 1874 |
| `atablecasesaffi00havigoog` (5c5ff689…) | Haviland, NY table 1880–1887 | 42 hits, overlaps Benjamin; cut for time |
| `cu31924017181938` (b1b9eb24…) | Connoly, New York Citations 1887 | 6 hits |
| Lockwood 1848, Connoly 1882, Silvernail 1896, Labatt digest 1861, Palm 1904/06, Rapalje federal 1880 | | not downloaded (same-case reversal tables, or time); Rapalje federal not used, so no `federal_overruled_tables` dataset |

## Extraction

- georgia1922: two-column table rebuilt from word coordinates (`scripts/pages.py`, `scripts/georgia_extract.py`), regex.
- the other four: OCR lines cut into chunks (`scripts/chunks.py`; Desty and Benjamin in window mode around treatment
  words) and read by Claude sub-agents following `work/READER_BRIEF.md`; their TSVs are `work/reader_out/`. 20 random
  primary rows were checked by hand against the OCR (REPORT.md).
