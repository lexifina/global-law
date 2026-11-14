# Source: U.S. Courts of Appeals Database (Songer, 1925–1996) and the Kuersten–Haire update (1997–2002)

Obtained 2026-11-14 by the round-9 dataset agent `bench_songer`. Nothing was executed from the downloads; the Stata
files were parsed with this folder's `dta.py` (standard library, run with `python -I`).

## Where

| Item | Value |
|---|---|
| Page | http://artsandsciences.sc.edu/poli/juri/appct.htm — Judicial Research Initiative (JuRI), University of South Carolina. Fetched 2026-11-14 over plain HTTP (the HTTPS certificate has expired; certificate checking was **not** switched off; no login, no click-through) |
| Songer database 1925–1996 | `cta96_stata.zip` → `cta96_stata.dta` (Stata format 114; 18,195 rows × 236 variables); codebook `cta96_codebook.pdf`. Page: "Last Update: October 21, 2008" |
| Kuersten–Haire update 1997–2002 | `KH_update_stata.zip` → `KH_update_stata.dta` (Stata format 110; 2,160 rows × 244 variables); codebook `KH_update_codebook.pdf`. Page: "Last update: July 13, 2011" |
| Total | 20,355 cases (case numbers 1–18195 and 20001–22160) |

Each download is in its own folder under `raw/` (`raw/<file>/`, extracted `.dta` in `raw/<zip>_x/`).

| File | SHA-1 | SHA-256 |
|---|---|---|
| `appct_htm/appct.htm` | `c21772974205725e723aec5b9460352dc6323d56` | `b583001304cd3af9dd5f0acf61d37a584d0b3df97239eb8fa68e117f6ad58736` |
| `cta96_stata_zip/cta96_stata.zip` | `cd0b0aa237c8da050497e56488dcdd5cf7c3cfeb` | `114ff4a0d02261302356e470cc70065067f7f277a546c855c347decaea9d9f26` |
| `cta96_stata_x/cta96_stata.dta` | `9410f23e66a832158040d18b90efa285fee71e71` | `6b7b5912bc061e6f990d0e381e0795e17bf0c08d2e2ecbc861de26e316e7ca02` |
| `cta96_codebook_pdf/cta96_codebook.pdf` | `c220266dd26aef9932e6003cb813f546ba7c27c0` | `3b2d0319511ea037f373e9afb94d03fefe2f477382ac590ae75bf56f73fd1208` |
| `KH_update_stata_zip/KH_update_stata.zip` | `0b0b8ed8a28ed43587e1fd0280e393cbab78ff37` | `047abf84f8fa772a65d8684f8f41c01a611b3213aa683da0d8c4135a81c992ae` |
| `KH_update_stata_x/KH_update_stata.dta` | `2df06a9d36f69a360a8d9b9e0232d6e7d7a411f7` | `e1cd5d29e360bbf1d2b8e0a68cba19ebf4c706f162245da91788287d37964c24` |
| `KH_update_codebook_pdf/KH_update_codebook.pdf` | `3254031a68fdc6db060883144079b4a7889d135c` | `a4512c71eba3017940303ffc4d91675f87c47d17b0511513ce9d265890f546d7` |

## Terms

No licence statement, terms of use, login or click-through on the page or in either codebook. The page and the
Songer codebook say the database was "Created by a Grant from the National Science Foundation". Only extracted facts
(citations, codes) are used; the files are public research data.

## What the variables are (as read in the codebooks)

- Unit: one published court of appeals decision, a random sample per circuit-year (15 per circuit-year 1925–1960,
  30 after; the update samples 1997–2002).
- Citation: Songer `VOL`/`BEGINPG` ("All references are to the second series of the Federal Reporter"; in the file,
  volumes from 1993 on are coded 3001, 3002, … = F.3d, checked against `YEAR`); update `CITEVOL`/`BEGINPAGE` (F.3d).
- Date: Songer `YEAR`/`MONTH`/`DAY`; update `DECISIONDATE` (m/d/yy or m/d/yyyy).
- `CIRCUIT` (0 = D.C.), `STATE` (01–57, alphabetical; 55 = not applicable), `DISTRICT`, `ORIGIN`, `SOURCE` (forum
  immediately below), `METHOD` (panel / rehearing / en banc …).
- **`PRIORPUB`**: "the citation of the most recent (if any) published opinion of some other court or a prior decision
  of the courts of appeals for this same case" (volume, reporter abbreviation, page; e.g. `FS` = F. Supp., `F2nd`,
  `BR`, `FRD`; in many rows a compact zero/`z`-padded form such as `0702FS038` or `377fs242z`; blank, `0` or
  `000000000` when none). Intercoder agreement 100% (Songer codebook).
- **`TREAT`** (update: `TREATMENT`): disposition by the court of appeals of the decision below — 0 stay/petition/motion
  granted; 1 affirmed (or affirmed and petition denied); 2 reversed (incl. reversed & vacated); 3 reversed and
  remanded (or just remanded); 4 vacated and remanded (also set aside & remanded; modified and remanded); 5 affirmed
  in part and reversed in part (or modified, or affirmed and modified); 6 affirmed in part, reversed/vacated in part,
  and remanded; 7 vacated; 8 petition denied or appeal dismissed; 9 certification to another court; 10 not
  ascertained; update only: 11 affirmed, vacated (no mention of reverse), and remanded. Intercoder agreement 95.2%.

Marginals (whole file): TREAT 1 = 11,404; 3 = 3,304; 2 = 1,210; 8 = 1,229; 6 = 996; 4 = 882; 5 = 711; 0 = 390;
7 = 107; 11 = 60; 10 = 38; 9 = 24. `PRIORPUB` present in about 4,700 cases; the decision below is unpublished
(or not recorded) in the rest.

## Files in this folder

- `dta.py` — Stata reader; `work/songer96.tsv`, `work/songer_kh.tsv` its output; `work/*_codebook.txt` (pdftotext).
- `MAPPING.md` — classes, key items, linking rules, exclusions (written before linking; amendment 1 before scoring).
- `link.py` → `key.tsv`, `key_nodes.tsv`, `link_report.tsv`, `link_summary.json`.
- `score.py` — scorer (CONTRACT.md); self-tested only on a synthetic build (`round9/agents/bench_songer/fake/`).
- `REPORT.md` — link figures.
