# Answer keys for lower-court and state-court case status (round 6 research)

Date of research: 2026-11-13. Web searches used: 30 of 35. Nothing behind a paywall, login, CAPTCHA or WAF was fetched (HathiTrust catalogue returned 403 and was left alone; the UNC Dataverse click-through dataset was not downloaded).

Marking used below:
- **[verified]** = I loaded the page, API record or codebook today.
- **[recalled]** = from memory, not confirmed today.
- **[not found]** = looked for, did not find.

Only documentation (codebooks, readme files, metadata) was downloaded, to a scratch folder. No data files and no copyrighted texts were stored.

---

## 0. The short version

1. The best single key for **reversed / vacated / affirmed** in the federal system is the **FJC Integrated Database (appeals)**, and the linking problem is already largely solved by a new open dataset, the **Comprehensive Courts of Appeals Database (CCAD)**, whose crosswalk maps Caselaw Access Project case ids to IDB appeal records for about 285,000 published appellate cases (about 97% of published post-1970 appellate cases).
2. The best **human-coded** key is the **Songer / Kuersten–Haire Courts of Appeals Database** (20,355 sampled cases, 1925–2002) joined to the little-known **"Shepardized Courts of Appeals Database"**, which adds panel rehearing, en banc and Supreme Court outcomes for every Songer case. Songer also records the citation of the prior published opinion (`PRIORPUB`) next to the treatment code (`TREAT`), which gives direct (decision below, affirmed/reversed/vacated) pairs.
3. For **vacated by the Supreme Court** (GVRs, summary reversals) there is a new CC0 dataset parsed from the Journal of the Supreme Court, 1993–2024 terms, with lower court and lower-court docket number: the **Supreme Court Shadow Docket Database**.
4. For **overruled** outside the US Supreme Court there is no modern open list. The usable material is (a) scanned public-domain tables of overruled cases for the pre-1930 corpus (New York, California, Georgia, Nebraska, North Carolina, Kentucky, federal; Greenleaf 1821/1838/1856), (b) Lindquist's state supreme court overruling data (deposit exists; whether it is case-level is unconfirmed), and (c) Free Law Project's expert-annotated citator benchmark, announced but not yet released as far as I could see.
5. For **depublished** there is no official cumulative California list online; the court publishes a rolling "Published opinions: review granted" list (2,640 entries) and depublication orders appear only in minutes and conference results.
6. Measurement ceiling: the one careful independent study (Hellyer 2018) found Shepard's and KeyCite each failed to correctly identify about a third of negative citing relationships, and the three citators agreed that a relationship was negative in only 15% of the 357 it examined. An expert panel in an earlier study was unanimous only about half the time. "100%" against any single citator is not a meaningful target for *treatment by a later case*; it is a much more reasonable target for *same-case history* (reversed, vacated), where administrative records exist.

---

## 1. FJC Integrated Database (IDB), appeals

**Name:** Federal Judicial Center, Integrated Database — Appeals data.
**URL:** https://www.fjc.gov/research/idb ; FY2008-onward page https://www.fjc.gov/research/idb/appellate-cases-filed-terminated-and-pending-fy-2008-present ; research guide https://www.fjc.gov/sites/default/files/IDB-Research-Guide.pdf ; codebook https://www.fjc.gov/sites/default/files/idb/codebooks/Appeals%20Codebook%202008%20Forward%20rev%2002102021.pdf
**Access:** open, no registration. **[verified]**
**Coverage:** all 12 regional courts of appeals; appeals data back to 1971 (statistical year), split into a 1971–2007 file and a FY2008–present file. The FY2008+ cumulative file was current to 30 June 2026 when checked. The Federal Circuit is not in the DCIRC code list (0–11). Bankruptcy appellate panel appeals appear as an appeal type in some circuits.
**Size:** not stated on the page. Cumulative tab-delimited zip `ap08on_0.zip`; yearly SAS files `ap08.sas7bdat` … `ap26.sas7bdat`; 5-year and 10-year zips. For scale, CCAD (below) matched 279,005–285,000 *published* cases to IDB rows; total appeals terminated run at tens of thousands a year.
**Fields useful to us (FY2008+ codebook, read today):**
- `DOCKET` appellate docket number; date docketed; names of appellant and appellee (criminal defendants' names are redacted; judge identity is redacted by Judicial Conference policy).
- `DCIRC`, `DDIST`, `DOFFICE`, `DDOCKET`, `DDKTDATE`, `DDEFNUM`: circuit, district, office, **district/bankruptcy court docket number**, district docket date, defendant number.
- `DISP`: 1 after oral hearing, 2 after submission, 4 procedural after other judicial action, 5 procedural without judicial action.
- `OUTCOME` (merits terminations only): 1 affirmed/enforced; 2 **reversed, vacated** (one code for both, includes reversed-and-remanded); 3 affirmed in part and reversed/vacated in part; 5 dismissed; 6 remanded; 7 other; 9 certificate of appealability denied.
- Procedural termination codes (jurisdictional defect, FRAP 42 voluntary dismissal, default, etc.).
- Opinion type: 1 unpublished oral; 2 **published**, written, signed; 3 unpublished signed; 4 published unsigned reasoned; 5 unpublished unsigned reasoned; 6 published unsigned without comment; 7 unpublished without comment.
- `ENBANC` Y/N (appeal heard en banc); `OPINION` (concurrence/dissent pattern, panel and en banc).
- Cross-appeal / consolidated-appeal flag and lead docket.
**Licence / terms:** no licence statement; US government work "produced and published at U.S. taxpayer expense". No anti-bulk language seen; bulk files are the intended delivery.
**Limits (from the research guide):** quarterly snapshots overwrite records; records are not updated after the fiscal year closes; out-of-range values recoded missing; not every variable is quality-checked. `OUTCOME` cannot separate "reversed" from "vacated". No reporter citation, no case caption beyond party names. The 1971–2007 codebook was not read today, so older field names are **[recalled]** as similar but not identical.
**FJC Supreme Court / en banc data:** none. The IDB page mentions neither; the only en banc information is the `ENBANC` flag above. **[verified absent on the pages loaded]**

**How to link:**
- *Appeal → published appellate opinion:* use the CCAD `idb_crosswalk` (section 3a), which carries `caseid` (CAP id prefixed `1`, CourtListener id prefixed `2`), circuit, docket, docket date. Without it: circuit + appellate docket number + decision date against our docket field.
- *Appeal → published district decision reviewed:* `DDIST` + `DOFFICE` + `DDOCKET` against the district court and docket number on our F.Supp./F.R.D./B.R. decisions, then take the latest published decision in that docket dated before the appeal was docketed. Obstacles: district docket formats vary by era and office; several published opinions can share a docket and the appeal may be from the final judgment rather than from the published ruling; most district rulings appealed are unpublished; `OUTCOME` 3 (part/part) does not say which ruling fell.
- CourtListener also carries the IDB as a bulk file and links dockets to IDB rows (`Docket.idb_data`), and its appellate dockets have `OriginatingCourtInformation` (lower-court docket number, judgment date, notice-of-appeal date). **[verified in models.py]**

**Verdict:** (a) held-out test — excellent for reversed/vacated/affirmed of district decisions and for the disposition of appellate opinions; administrative record, independent of any citator. (b) training/diagnosis — excellent. Main obstacle: district-docket matching and the merged reversed/vacated code.

---

## 2. Supreme Court sources

### 2a. Order lists (supremecourt.gov)
**URL:** https://www.supremecourt.gov/orders/ordersofthecourt **[verified]**
**Coverage:** terms 2010–2026, PDF per order day, plus miscellaneous orders. Text PDFs; "Certiorari — Summary Dispositions" sections give docket number, caption and the GVR language naming the court remanded to. No lower-court reporter citation in the modern lists.
**Licence:** US government work. No bulk file; a few hundred PDFs.
**Verdict:** superseded for our purpose by 2c, which has already parsed the same material.

### 2b. Journal of the Supreme Court
**URL:** https://www.supremecourt.gov/orders/journal.aspx (October Term 1993–2025, one PDF per term) and https://www.supremecourt.gov/orders/scannedjournals.aspx (1889–1992, scanned PDF per term). **[verified]**
**Machine-readability:** 1993+ are born-digital PDFs; 1889–1992 are scans (OCR quality not checked). Entries give docket number, caption, lower court name and the order; no reporter citation of the decision below.
**Verdict:** (a) good raw key for vacated/reversed by summary order back to 1889; (b) needs parsing for 1889–1992. Obstacle: only court name + docket to identify the decision below.

### 2c. Supreme Court Shadow Docket Database, 1993–2025 (Taboni & Kastellec)
**Citation:** Jonathan P. Kastellec and Anthony R. Taboni, "Supreme Court Shadow Docket Database, Version 2.0 (November 2025)"; paper forthcoming in Journal of Law and Courts.
**URL:** https://doi.org/10.7910/DVN/89VEX8 ; www.shadowdocketdata.com **[Dataverse record and codebook verified]**
**Access / licence:** open, **CC0 1.0**.
**Coverage:** every order in the Journal for the 1993–2024 terms, one row per docket per order.
**Size:** main CSV about 278 MB; also intermediate files, the Journal PDFs (terms 1993–2024) and raw Supreme Court docket JSON (1996–2024).
**Fields:** `docket_number` (same format as the docket-based SCDB), term, date, full order `text`, `action_text`, **`action_class`** (includes `GVR`, `Reversal`, `Affirmed`, `Affirmed in Part`, `Certiorari`, `DIG`, `Dismiss`, `Remand`, `Rehearings`, …), cert granted/denied, dissent flags, petitioner, respondent, **lower court**, **lower court docket number**, counsel.
**Verdict:** (a) held-out test — the best open key for "vacated" by GVR and for summary reversals, 1993–2024; also gives cert denied as a clean negative control (decision below stands). (b) training — yes. Obstacle: decision below is identified by court + lower-court docket number only (docket data starts 1996); one Supreme Court docket can cover several lower-court judgments.
**Rough yield:** GVRs run in the low hundreds in an ordinary term with spikes after big sentencing decisions; expect several thousand GVR rows over 31 terms, a few hundred summary reversals, and well over 150,000 cert denials. (My estimate; count the `action_class` column to confirm.)

### 2d. Supreme Court docket JSON
**URL pattern:** `https://www.supremecourt.gov/RSS/Cases/JSON/<docket>.json` — loaded one today; it has `LowerCourt`, `LowerCourtCaseNumbers`, `LowerCourtDecision` (date). **[verified for one docket]** The shadow docket deposit already bundles these for 1996–2024.
**Use:** court + lower docket + decision date is a much tighter key into our corpus than court alone.

### 2e. Supreme Court Database (SCDB) lower-court variables
**URL:** https://scdb.la.psu.edu (the old scdb.wustl.edu host refused connections today). Codebook page for `lcDisposition` loaded. **[verified for that variable]**
**Access / licence:** open download; licence **[recalled]** as CC BY-NC 3.0 US — check before redistribution.
**Coverage:** modern file 1946 term onward, legacy file 1791–1945; about 60 variables per case; roughly 9,000 modern and 19,000 legacy cases **[recalled]**.
**Fields:**
- `lcDisposition` = how the court *whose decision the Supreme Court reviewed* treated the decision *it* reviewed (so it is the court of appeals' treatment of the trial court): 1 stay/petition granted, 2 affirmed, 3 reversed, 4 reversed and remanded, 5 vacated and remanded, 6 affirmed and reversed in part, 7 same and remanded, 8 vacated, 9 petition denied/appeal dismissed, 10 modify, 11 remand, 12 unusual. Often blank in the legacy data.
- `caseDisposition` = the Supreme Court's own treatment of the decision below (affirmed, reversed, reversed and remanded, vacated and remanded, …) **[recalled]**; `lcDispositionDirection`, `caseSource`, `caseOrigin` (court codes), `docket`, `usCite`/`sctCite`/`ledCite`/`lexisCite` **[recalled]**.
- These are separate from `precedentAlteration`.
**Can the decision below be identified?** SCDB has **no lower-court citation and no lower-court docket variable** **[recalled; the variable index page did not render]**. Three routes: (i) the U.S. Reports syllabus line and the "Reported below:" line in the bound reports give the lower-court reporter citation (one 1950s example confirmed today; general practice **[recalled]**) — and that text is already in our own U.S. Reports decisions; (ii) Supreme Court docket number → 2c/2d lower-court docket; (iii) for court of appeals cases, the Songer "Phase II" bridge file and the Shepardized file (section 3) carry the F.2d/F.3d citation alongside SCDB ids.
**Verdict:** (a) held-out test — strong: two labels per case (Supreme Court's treatment of the court below, and that court's treatment of the trial court). (b) training — yes. Obstacle: building the decision-below link; `caseDisposition` is partly correlated with what we have already used from SCDB, so keep it out of anything tuned on SCDB.
**Rough yield:** about 9,000 modern cases, around 60–65% reversed or vacated, perhaps 70% with a published decision below → on the order of 3,500–4,500 reversed/vacated and 2,000–2,500 affirmed published lower-court decisions; legacy adds several thousand more where the decision below is in a state or early federal reporter.

---

## 3. US Courts of Appeals

### 3a. Comprehensive Courts of Appeals Database (CCAD) — Sapiro-Gheiler & Kastellec
**URL:** https://doi.org/10.7910/DVN/XN2FVS (version 2, September 2026). **[Dataverse record and codebook verified]**
**Access / licence:** open, **CC BY 4.0**.
**Coverage:** published courts of appeals opinions 1892–2025; more than 500,000 rows implied; source text is the Caselaw Access Project (ids prefixed 1) and CourtListener (prefixed 2).
**Size:** csv.gz 778 MB; parquet about 1 GB; `idb_crosswalk.tab` 17.9 MB; `songer_crosswalk.tab` 885 KB; codebook 613 KB.
**Fields:** `caseid`, `citation` (e.g. `927 F.3d 1023`), `docket_number`, decision date, circuit, `is_enbanc`, per-opinion types (including orders on rehearing), four rule-based `regex_disp_*` disposition columns, LLM-coded disposition on the SCDB scale, plus merged Songer columns (`songer_gt_treat`, `songer_gt_priorpub`, method, origin court) and merged IDB columns.
**Crosswalks:** `idb_crosswalk` columns `caseid, idb_idx, circuit, docket, dktdate, reopen, tapeyear, idb_alt_rows`; about 285,000 cases, about 97% of post-1970 published cases. Songer crosswalk matches 99.45% of Songer cases.
**Stated accuracy of its own LLM disposition coding:** 87.0% against Songer `TREAT` (N = 22,792) and 88.9% against IDB `OUTCOME` (N = 279,005).
**Verdict:** (a) held-out test — do **not** use its LLM disposition as truth; use it as the *join table* that attaches IDB and Songer labels to our case ids. (b) training/diagnosis — very good; the 87–89% figures are also a direct measure of how noisy "disposition read from opinion text" is against human/administrative records. Obstacle: none for appellate opinions (CAP ids); the district-decision link still has to be built.

### 3b. Songer US Courts of Appeals Database, and the Kuersten–Haire update
**URL:** Judicial Research Initiative, University of South Carolina: https://artsandsciences.sc.edu/poli/juri/appct.htm (the site's TLS certificate has expired; songerproject.org has a certificate name mismatch). ICPSR 2086 holds Phase 1. **[page and update codebook read today]**
**Access / licence:** open zip downloads (Stata, SPSS, SAS, ASCII); no licence statement; NSF-funded.
**Coverage:** random sample of published decisions, 1925–1996 (15 per circuit-year to 1960, 30 after), update 1997–2002; 20,355 cases in total (case numbers 1–18195 and 20001–22160). "Phase II" file = every court of appeals case later reviewed by the Supreme Court (the bridge to SCDB).
**Fields:** citation volume / begin page (Federal Reporter), `DECDATE`, `DOCNUM`, `METHOD` (1 panel first time, 2 panel after rehearing, 3 after remand from Supreme Court, 4 en banc after single panel decision, 5 en banc after multiple panel decisions, 6 en banc with no prior panel decision), origin court, **`PRIORPUB`** (citation of the most recent prior published opinion in the same case, e.g. the F.Supp. opinion), **`TREAT`** (0 stay/petition granted; 1 affirmed; 2 reversed incl. reversed & vacated; 3 reversed and remanded; 4 vacated and remanded; 5 affirmed in part/reversed in part; 6 same and remanded; 7 vacated; 8 petition denied/appeal dismissed; 9 certification; 10 not ascertained; 11 affirmed, vacated and remanded).
**"Overruled circuit precedent" variable:** none found in the codebook text searched.
**Verdict:** (a) held-out test — the best *human-coded* key; `PRIORPUB` + `TREAT` yields labelled (decision below → affirmed/reversed/vacated) pairs with a reporter citation on both sides; `METHOD` 4–5 flags en banc decisions that displaced a panel decision. (b) training — small but clean. Obstacle: sample, not census; `PRIORPUB` is missing when the decision below was unpublished; citation format is compact (`FS`, `F2nd`).
**Rough yield:** 20,355 appellate decisions with treatment; the share with a published decision below is unknown — I would expect a few thousand pairs.

### 3c. "Shepardizing the Courts of Appeals Database" (Rorie Spill Solberg)
**URL:** same page; `shepardized_cta_stata.zip`, codebook `shepardized_cta_codebook.pdf`, last update 19 November 2010. **[codebook read today]**
**Access / licence:** open; no licence statement. Coded by hand from LexisNexis Shepard's reports (so it is a research derivative of a commercial citator, published openly as data).
**Coverage:** every case in the Songer database and update (20,355 cases).
**Fields:** `CASENUM`, `CITATION` (e.g. `0842 f 2d 0556`); `APPEAL` (subsequent history exists; same case; connected case; later proceeding); `SUBHIST` (petition for panel rehearing / rehearing en banc / cert / appeal, in combinations); **`COAREHEAR`** (0 none; 1 denied; 2 granted, same result; 3 granted, different result; 4 decision modified; 5 denied, decision modified; **6 decision withdrawn or vacated**; 7 granted, result unknown); **`COAENBANC`** (0 none; 1 denied; 2 granted, same result; 3 granted, different result; 4 granted, unknown; 5 granted, appeal dismissed); **`SCAPPEAL`** (cert denied / dismissed / granted; appeal dismissed / granted); **`SCRESULT`** (affirmed, reversed, reversed and remanded, vacated and remanded, part/part, vacated, dismissed); `SCREHEAR`; `APPAFTRE1`–`5` (what happened after remand); copied SCDB identifiers (US, S.Ct., L.Ed. cites, docket, ANALU).
**Reliability (their own double-coding of 1,018 cases):** intercoder agreement 95.1%–99.7% by variable.
**Verdict:** (a) held-out test — unusually good: it is the only open, case-level record I found of *withdrawn*, *vacated on rehearing*, *en banc granted* and *reversed/vacated by the Supreme Court* for a defined random sample of appellate opinions, with a reporter citation for each. It includes the negatives (no subsequent history), so both recall and false-alarm rates can be measured. (b) training — yes. Obstacle: history frozen at about 2008–2010; inherits Shepard's errors for the "same case / connected case" categories (the codebook itself says those categories are vague).
**Rough yield:** 20,355 cases; I would expect a few hundred en banc grants, several hundred cert grants with a Supreme Court result, and a few hundred rehearing modifications/withdrawals.

### 3d. En banc data sets
- **CCAD `is_enbanc`** and **IDB `ENBANC`** (above): identify en banc decisions; the vacated panel opinion has to be found through the docket.
- **Beim, Hirsch & Kastellec**, replication data for "Signaling and Counter-Signaling in the Judicial Hierarchy: An Empirical Analysis of En Banc Review", AJPS 60(2) 2016: https://doi.org/10.7910/DVN/2EJIZJ — one 1.1 MB zip, CC0. Contents not inspected (years and case counts not stated on the record). **[record verified]**
- **Larsen (with Devins), "Norm Erosion on the Courts of Appeals"**: https://doi.org/10.7910/DVN/7NURYC — one 270 KB Excel file, CC0, with a note asking users to contact the author while the publication is in progress; whether it lists cases with citations is unconfirmed. The related article, Devins & Larsen, "Weaponizing En Banc", NYU L. Rev. 2021, describes an original data set of en banc decisions over six decades; no public deposit found. **[record verified; contents not]**
- An NSF project (SES-0848235) built a data set of about 3,600 en banc decisions, 1937–2008; no public deposit found. **[not found]**
- No circuit publishes a cumulative list of panel opinions vacated on grant of rehearing en banc. **[not found]**
**Verdict:** (a) test — moderate; the cleanest test of "panel opinion vacated on grant of rehearing en banc" is 3c's `COAENBANC`. (b) diagnosis — yes.
**Rough yield:** about 3,600 en banc decisions to 2008, perhaps 4,000–4,500 to 2020, of which those with a prior *published* panel opinion are the test cases (my estimate: half or more).

### 3e. Circuit lists of overruled or abrogated circuit precedent; Ninth Circuit *Miller v. Gammie*
**[not found]** No circuit publishes such a list. *Miller v. Gammie* abrogations ("clearly irreconcilable with intervening higher authority") are declared inside individual panel opinions only. The only open route is our own text: extract "overruled by", "abrogated by", "superseded by statute" from citing opinions and from citation history strings, and score it against the samples in 3c and section 7.

### 3f. Federal Circuit
**Name:** Federal Circuit Dataset Project (formerly Compendium of Federal Circuit Decisions), Jason Rantanen, University of Iowa.
**URL:** https://empirical.law.uiowa.edu/compendium-federal-circuit-decisions ; document data https://doi.org/10.7910/DVN/UQ2SF7 ; docket data doi:10.7910/DVN/EKSYHL. **[project page verified]**
**Coverage:** essentially all opinions since 2004 and all summary affirmances since 2007, through 31 December 2024; docket data set for all appeals since 2000.
**Fields:** disposition ("Disposition – General": affirmed, affirmed-in-part, reversed, vacated…), en banc flag, origin and tribunal of origin, appeal number, `Full_Cite` (Federal Reporter citation where available), precedential status. Original-tribunal docket numbers are "in development".
**Licence:** not stated on the project page; check the Dataverse record.
**Verdict:** (a) test — good for the one circuit the IDB omits. Obstacle: decision below is mostly PTAB/agency/Court of Federal Claims/district patent rulings, few of which are in our reporters.

### 3g. Bankruptcy appellate panels
**[not found]** No dedicated open data set. IDB appeals records cover appeals reaching the courts of appeals from BAPs and from district courts sitting in bankruptcy.

---

## 4. State courts — official lists and old public-domain tables

### 4a. Modern official lists

| State | What exists | Status |
|---|---|---|
| California | "Published Opinions: Review Granted" list at https://courts.ca.gov/opinions/published-opinions-review-granted — 2,640 entries, 50 per page, with appellate case number, date, court/division, case name, PDF link and docket link. Companion list for unpublished opinions. | **[verified]** Earliest date covered not checked. No citation column. |
| California | Depublication orders | No official cumulative list online. Orders appear in Supreme Court minutes and weekly petition-conference results (PDF). Rule 8.1105(e)(2) / 8.1125 govern. Before 1 July 2016 a grant of review automatically made the Court of Appeal opinion non-citable; after that date it stays citable unless ordered otherwise — the model must apply the right rule by date. **[verified from rule pages and library guides]** |
| California | "Cumulative Subsequent History Table" of the Official Reports advance pamphlets | A 2001 copy is catalogued at the Internet Archive (`californiasubseq0000vari`), in copyright, lending only — not usable as bulk data. **[catalogue entry verified]** |
| Texas | Texas Subsequent History Table (writ / petition history) | West discontinued it in October 2014; first issued as the "Complete Texas Writs of Error Table" in 1917. No free cumulative table found. **[verified]** Public-domain early editions not located on HathiTrust. **[not found]** |
| Texas | TAMES (appellate case management) | Public per-case search with dispositions; no bulk download or API found. CourtListener now collects TAMES (Supreme Court, Court of Criminal Appeals, 15 courts of appeals; cases from 1900; hundreds of thousands of cases), currently only through its database replication service, with API access promised. **[verified on Free Law Project wiki]** Field list (dispositions, petition history) not documented there. |
| New York | Official Reports | Law Reporting Bureau publishes cumulative tables of cases, statutes and digest-index; no "cases overruled" table confirmed online. **[not found]** |
| Florida ("receded from"), Ohio, Pennsylvania, Illinois, others | Official lists of overruled / receded-from cases | **[not found]** No court-published list located. |
| State open-data portals with per-case appellate dispositions | | **[not found]** None located beyond per-case search sites. National Center for State Courts publishes aggregates only. |

**Verdict:** California review-granted list — (a) usable test of "review granted / not citable" for recent Court of Appeal opinions, and of the date-dependent citability rule; (b) diagnosis. Obstacle: keyed by appellate case number, not citation; much of it post-dates a corpus that ends around 2020. Everything else in this table is either not open or not found.

### 4b. Public-domain tables of overruled / reversed cases (pre-1930) — scanned and where

All of the following were confirmed today as Internet Archive items through the archive.org search API (identifier in brackets). Items whose identifier ends in `goog` are Google scans hosted by the Internet Archive; `cu…` are Cornell scans. All are pre-1930 US publications and so public domain in the US. OCR quality was not checked.

**General (American and English)**
- Simon Greenleaf, *A Collection of Cases Overruled, Doubted, or Limited in Their Application* (Portland, 1821) [`acollectioncase00greegoog`]; later edition 1838 [`acollectioncase01greegoog`]; Greenleaf & John Townshend, *A Collection of Overruled, Denied, and Doubted Decisions and Dicta, both American and English* (1856) [`acollectionover00towngoog`].
- Melville M. Bigelow, *An Index of the Cases Overruled, Reversed, Denied, Doubted, Modified, Limited, Explained, and Distinguished by the Courts of America, England, and Ireland, from the Earliest Period to 1873* (Boston, Little, Brown, 1873; 566 pp.; 1887 edition with supplement by Williams and appendix by Stewart). Catalogue records confirmed; the only digital copy found is HeinOnline (subscription). **Free scan [not found]** — worth a direct HathiTrust / Google Books title search by hand.
- Lawyers Co-operative, *Notes on American Decisions [1760–1887], showing later citing decisions* (1909) [`notesonamerican01compgoog`, `…02…`, `…03…`, `notesonamerican01unkngoog`].
- W. S. Torbert, table of US state cases with notes and US Supreme Court affirmances (1905) [`tableofcasesalph00torb`]; *National Law Finder* (1914) [`nationallawfind00unkngoog`].

**Federal**
- Stewart Rapalje, *A Digest of Federal Decisions and Statutes … to 1880 … together with a table of cases affirmed, reversed, overruled, and otherwise criticised* (1880) [`cu31924017687736`].
- *Notes on United States Supreme Court Reports, showing present authority* (1904) [`notesonunitedst00courgoog`, `…01…`, `…04…`]; W. H. Phillips, manual of US Supreme Court cases cited (1882) [`cu31924022843514`].

**New York** (the richest run)
- Ralph Lockwood, synopsis of cases reversed in the Court for the Correction of Errors, 1799–1847 (1848) [`ananalyticaland00lockgoog`].
- Theodore Connoly, *New York Citations* — cases cited, affirmed, reversed, 1794 onward (1882 [`cu31924021896018`]; 1887 [`cu31924017181938`]).
- Eugene Haviland, *Table of Cases Affirmed, Reversed, Overruled or Criticised*, 1880–1887 [`atablecasesaffi00havigoog`].
- Wayland Benjamin, *New York Cases Reported or Cited, 1887–1893 … showing every appeal and whether affirmed, reversed or modified; of cited cases, whether overruled, limited, distinguished, criticised* [`cu31924022823318`].
- William Silvernail, *Affirmed and Reversed New York Cases*, earliest reports to 1896 [`cu31924017670856`].
- Rapalje, New York digests with tables of cases overruled or criticised, 1881–1882 [`cu31924017679949`, `cu31924017679881`]; Parker, digest of Court of Appeals reports vols. 126–153 with table of cases overruled and of cases affirmed or reversed (1898) [`cu31924017679824`]; Taylor, *Analyzed Citations of the New York Supreme Court Reports* (1919) [`cu31924066074695`].
- HathiTrust catalogue record 100760137, *Table of New York Cases, 1794–1912* (seen in search results; page not loaded because HathiTrust refused automated access).

**California**
- Henry Labatt, *A Table of Cases in California as Affirmed, Overruled, Modified, Commented Upon* (1860) [`atablecasesinca00labagoog`]; Labatt digest with cases affirmed, reversed or abrogated (1861) [`adigestdecision00compgoog`].
- Robert Desty, *California Citations … approved, affirmed, criticised, doubted, denied, or overruled* (1874) [`cu31924024636189`, `californiacitat00destgoog`]; Desty digest of vols. 34–46 with table of cases overruled (1875) [`cu31924061139832`].
- *King & Leonard's California Citations and Conflicting Cases* (1894) [`kingleonardscal00courgoog`, `…01…`]; Hester, *California Case and Citation Index*, vols. 1–113 (1897) [`californiacasea00courgoog`]; *Palm's California Case Citations* (1904, 1906) [`palmscalifornia00courgoog`, `…01…`, `…02…`]; *Notes on California Reports* (1898; supplement 1912) [`notesoncaliforn00courgoog`, `…02…`, `…04…`, `…05…`].

**Other states**
- Georgia: Hugh Downing, *Cases in Georgia Reports and Georgia Court of Appeals Reports That Have Been Overruled, Doubted, Criticised, or Modified* (1922) [`casesingeorgiar00appegoog`].
- Nebraska: *Nebraska Synoptical Digest … with complete tables of cases cited and overruled* (1910) [`nebraskasynopti00courgoog`, `nebraskasynopti00hagggoog`].
- North Carolina: criminal code and digest with table of cases overruled, criticised, followed, distinguished and approved (1899) [`northcarolinacr00jerogoog`, `northcarolinacr00pembgoog`].
- Kentucky: Caldwell, *Notes to the Kentucky Reports* (1907) [`notestokentucky00unkngoog`].
- Iowa and Minnesota: *Notes on Iowa Reports* (1911) [`notesoniowarepo00iowagoog`]; *Notes on Minnesota Reports* (1911) [`notesonminnesot00minngoog`]; Co-op annotations, Minnesota (1901) [`coopannotations00unkngoog`].
- Texas: *Shepard's Texas Appeals Citations* (1908) [`shepardstexasapp00fran`] — the only pre-1930 Shepard's volume the archive.org title search returned.

**West digests:** the Century Edition of the American Digest (to 1896) and the First Decennial (1897–1906) have page images on HathiTrust according to the Online Books Page, and at least one "Table of Cases" volume is full view. **[seen in search results only]** Whether those tables carry affirmed/reversed/overruled notes was not confirmed. HathiTrust's terms restrict bulk download of Google-digitised volumes; use page-by-page reading or the Internet Archive copies.

**Verdict for 4b:** (a) held-out test — the only independent key for "overruled" and for affirmed/reversed in the 1800–1920 state corpus, compiled by contemporaries from the reports themselves. (b) training — good for old citation forms. Obstacles: OCR of dense tables; nominative reporter abbreviations (Johns., Wend., Cow.) need mapping to our citations; "doubted / limited / criticised" must be separated from "overruled"; each table stops at its publication date, so a case may have been overruled later (they test recall up to a date, not final status).
**Rough yield:** New York alone should give several thousand reversed/affirmed entries and some hundreds of overruled entries; California several hundred overruled/criticised; Georgia 1922 a few hundred; Greenleaf 1856 on the order of a thousand American entries (all my estimates from the size and type of the books, not counted).

---

## 5. Open citators and treatment data

| Source | What it has | What it lacks | Status |
|---|---|---|---|
| **CourtListener bulk data** (Free Law Project), https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data | Quarterly CSV snapshots: courts (with an `appeals_to` table), dockets, opinion clusters, opinions, citation map (`depth` = times cited within the citing opinion), parentheticals, FJC IDB. Cluster fields `posture`, `procedural_history`, `disposition`, `history`, `syllabus`, `precedential_status`. Docket fields `appeal_from`, `originating_court_information` (lower docket number, judgment date, notice of appeal date, rehearing-denied date), `idb_data`. Marked Public Domain Mark 1.0. | **No treatment field.** In `OpinionsCited` a treatment field exists only as a commented-out note. No overruled flag, no subsequent-history table. | **[verified: wiki + models.py]** |
| **Free Law Project open citator** | May 2025: experiments on 149 overruled Supreme Court opinions from the Congress.gov list plus sampled negatives (about 1,000 records). September 2025: 30 volunteer experts (two reviewers per citation, third breaks ties) annotating negative treatment by severity, split into direct history and citing references; 180+ Supreme Court cases / 7,600+ citations analysed, about 4,000 with final labels; about 1,000 citations from 30+ federal appellate and district cases and about 300 from 10 state cases through first round; "Ambiguous" and "Unverifiable" categories. Promised as "the first open-source benchmark dataset of its kind". | No release date, no licence for the data, no download found. Current status not confirmed. | **[blog posts verified]** |
| **Caselaw Access Project** (static.case.law) | Per-case metadata: id, name, decision date, docket number, pages, citations, court, jurisdiction, `cites_to`, analysis, provenance. | No history, disposition or treatment field. | **[verified: one volume metadata file]** |
| **LegalBench "overruling" task** (Casetext overruling data set; Zheng et al., CaseHOLD paper) | 2,400 sentences labelled overruling / not overruling; CC BY 4.0; on Hugging Face and at Stanford RegLab. | Sentences only — no case identifiers, so it cannot score case status. | **[verified]** |
| **Demir & Canbaz, "Validate Your Authority"**, arXiv:2605.17691 (NLLP 2025) | 239 expert-annotated citations with treatment labels; best model 79.1% on the coarse task, 67.7% on the fine one. | Tiny; download location and data licence not stated on the abstract page. | **[abstract verified]** |
| Casetext SmartCite, Fastcase Bad Law Bot, vLex Cert, Midpage, Paxton, FlawFinder "FlawCheck" | Commercial or freemium citators. | None publishes its treatment data openly. | **[not found as open data]** |
| Google Scholar "How cited", LII | No bulk access; Google's terms forbid automated querying. **[recalled]** Not usable. | | |
| govinfo USCOURTS | Opinions from participating federal courts from about 2004 with docket metadata; no disposition or history fields. **[recalled, not loaded today]** | | |
| Chen et al., "Affirm or Reverse" (NBER working paper) | About 280,000 district opinions (CourtListener, 1924–2013) paired with circuit outcomes — but the outcomes come from Bloomberg Law, so the linked set is unlikely to be redistributable. | Not confirmed as released. | **[seen in search results]** |

**Verdict:** CourtListener — (a) not a test key (no labels); (b) valuable for linking (lower-court docket, IDB join) and for diagnosis (the `disposition`/`history` text is reporter-supplied summary of what happened). Free Law Project benchmark — potentially the best independent test of *overruled / negative treatment by a later case* for federal and state courts; ask them for early access. LegalBench — diagnosis of the sentence classifier only.

---

## 6. Academic data sets on state high courts and overruling

| Data set | Access | Coverage / size | Useful fields | Verdict |
|---|---|---|---|---|
| **Brace & Hall, State Supreme Court Data Project** — https://doi.org/10.7910/DVN/Z80F7P (also Rice) | Open, **CC0** (deposited under Data-PASS terms) **[record + codebook verified]** | All 50 states' courts of last resort, 1995–1998 sessions; about 21,000 decisions; case file 29 MB tab | Docket number, number of dockets, **regional reporter and volume**, decision date; which court heard the case first and whether an intermediate court heard it; **the supreme court's disposition of the lower court** (1 affirmed; 2 reversed or vacated; 3 reversed or vacated and remanded; 4 part/part or modified; 5 part/part and remanded; 6 petition granted; 7 petition denied); convictions/sentences/awards overturned; law declared unconstitutional. **No "overruled precedent" variable** found in the codebook text. | (a) good test of reversed/vacated for state intermediate appellate decisions in a four-year window; (b) yes. Obstacle: the decision below is not cited — it must be found by state + docket + parties among our intermediate-court decisions, and many were unpublished. Yield: perhaps 4,000–8,000 linkable published decisions below (estimate). |
| **Lindquist, "State Politics and the Judiciary"** — doi:10.15139/S3/12150 (UNC Dataverse; released 2016) | Open after a click-through agreement (analysis only; do not identify or contact individuals or organisations; report misuse to SPPQ) **[API record verified; files not downloaded]** | Description: "data on overruling decisions in the fifty state supreme courts over the period of their histories … a comprehensive database of all overruled and overruling cases decided by each state Supreme Court." Files: `state_politics_and_the_judiciary_v91.tab` (2.4 MB), codebook PDF, and several state-level spreadsheets ("Annual State Level Data 1975-2006"). | Unknown until the codebook is read. The file names suggest a state-year panel; the description promises case-level overruled/overruling pairs. | Potentially the single most valuable key for **state "overruled"**. Read the codebook first (accept the terms by hand). Related: NSF SES-0549889; Lindquist & Cross, "Stare Decisis as Reciprocity Norm" (30-year model); Lindquist & Pybas (1998), four states 1965–1996. If the deposit is only aggregates, ask Lindquist — a Drake Law Review study of Iowa overrulings 1857–2018 (Buller) says she shared case-level data. |
| Miller & Tuma, "Stare Decisis and the Electoral Connection", SPPQ 2020 — doi:10.15139/S3/1MCPQF | Open, CC0 **[readme + codebook read]** | About 5,000 judge votes, built on the Brace–Hall 1995–98 data | `vote_ovr` (joined a precedent-overturning majority), state; no case citation in the codebook | Diagnosis only. |
| Hall & Windett, "New Data on State Supreme Court Cases", SPPQ 13:427 (2013) | **[not found]** — the listed page (jasonwindett.com/new-data-on-state-supreme-court-outcomes) returns 404; not on Harvard Dataverse | Every state supreme court ruling 1995–2010, more than 168,000 cases, built by automated text analysis | Variables not seen | Machine-coded from opinion text, so weak as an independent key even if obtained. |
| Gibson & Nelson, state supreme court database 1990–2015 — doi:10.7910/DVN/K9VIEW; Ash & MacLeod, state supreme courts 1947–1994 — doi:10.7910/DVN/GVEU25; Amato, ten states 2000–2020 — doi:10.7910/DVN/OYW9GT | Open deposits **[listing verified; contents not inspected]** | As titled | Unknown | Leads to check for a disposition variable. |
| Songer (section 3b); Benesh & Reddick; Hansford & Spriggs | Benesh & Reddick and Hansford & Spriggs concern lower-court reaction to *US Supreme Court* overrulings — not new keys for us. **[recalled]** | | | |
| ICPSR 32501, Civil Justice Survey of Trials on Appeal, 2005 | ICPSR registration; some files restricted | 3,970 civil appeals in 84 appellate courts, 35 states | Appellate outcome per trial | Small, restricted; low priority. |

---

## 7. How good are the commercial citators? (the measurement ceiling)

**Paul Hellyer, "Evaluating Shepard's, KeyCite, and BCite for Case Validation Accuracy", 110 Law Libr. J. 449 (2018)** — https://www.aallnet.org/wp-content/uploads/2018/12/LLJ_110n4_02_hellyer.pdf **[full text read]**
- Design: 73 published Ninth Circuit decisions from January 1984; every citing case that at least one of the three citators marked negative as of mid-2017 = **357 citing relationships** (federal cases predominate; published and unpublished).
- Agreement: all three citators agreed a relationship was negative in only **53 of 357 (15%)**; they substantively agreed on the *type* of negative treatment in only **11%**.
- Against the author's own reading, 309 of the 357 were truly negative. Of those:
  - Shepard's failed to mark 85 (28%) and mislabelled 18 (6%) → **33%** not correctly identified.
  - KeyCite failed to mark 105 (34%) and mislabelled 11 (4%) → **38%**.
  - BCite failed to mark 211 (68%) and mislabelled 11 (4%) → **72%**.
- False alarms among each citator's negative labels: Shepard's 235 labels, 12% wrong; KeyCite 218 labels, 11% wrong; BCite 102 labels, 15% wrong.
- Serious errors (missed overrulings and the like) were found in all three.
- **Test set:** "available from the author upon request" — not published with the article.

**William L. Taylor, "Comparing KeyCite and Shepard's for Completeness, Currency, and Accuracy", 92 Law Libr. J. 127 (2000)** (as reported by Hellyer): 459 state and federal cases decided April 1997; assuming every negative label was right, Shepard's missed 23% of negative references and KeyCite 25%. **Taylor printed the citing relationships in an appendix** (68 unique negative labels) — a small published test set.
**Dan Dabney's response for Westlaw** (92 Law Libr. J. 381): a five-expert panel reviewing Taylor's list was **unanimous only about half the time** and split three to two on 18 of 68.
**Aaron Kirschenfeld, "Yellow Flag Fever: Describing Negative Legal Precedent in Citators", 108 Law Libr. J. 77 (2016):** compares the descriptive phrases KeyCite and Shepard's attach to negative treatment; small sample; figures not retrieved. **[existence verified]**
**Susan Nevelow Mart:** her 2013 study ("The Case for Curation", Legal Reference Services Q.) compared *headnote relevance* in Shepard's and KeyCite, not validation accuracy; I found no Mart study of negative-treatment accuracy. **[as cited by Hellyer]**
**Kristina Niedringhaus, "Is It a 'Good' Case? Can You Rely on BCite, KeyCite, and Shepard's to Tell You?"** (2019, LLRX / Georgia State) is a review of Hellyer, not new data.
**Vendor studies (LexisNexis, 2024 and 2026):** claim KeyCite mis-treats cases Shepard's gets right and leaves most of a 1,000-case sample unflagged; self-interested, no case lists.

**What this bounds:** for *treatment by later cases* (overruled, abrogated, questioned), two leading citators disagree with a careful human reader on roughly a third of negative relationships and with each other most of the time; experts disagree with each other on perhaps half of contested items. A model scored against one citator cannot be shown to be better than about 65–75% "correct" on that task, and disagreement with a citator is not evidence of model error. For *same-case history* (reversed, vacated, withdrawn, en banc) the keys in sections 1–3 are administrative or double-coded (95–99.7% intercoder agreement in the Shepardized file; 87–89% agreement between text-derived dispositions and Songer/IDB in CCAD), so high measured accuracy is attainable there.

---

## 8. Ranked top 10 — what to obtain first

| # | Source | Model output tested | Rough test cases | Why this rank |
|---|---|---|---|---|
| 1 | **FJC IDB appeals** + **CCAD `idb_crosswalk`** | reversed / vacated / affirmed (of district decisions); disposition of appellate opinions; en banc flag | about 285,000 published appellate cases already joined to CAP ids; district decisions linkable by docket probably in the tens of thousands, of which roughly 15–20% reversed or vacated in whole or part | Largest, administrative, open, and the join to our ids exists. |
| 2 | **Songer + Kuersten–Haire** with **Shepardized Courts of Appeals** | reversed / vacated / affirmed (with reporter cite of decision below); withdrawn or vacated on rehearing; en banc granted; reversed/vacated by Supreme Court; true negatives | 20,355 appellate cases, every one with a full subsequent-history record; a few thousand decision-below pairs | Human-coded with measured reliability; the only open key for withdrawn and en banc; includes negatives so precision can be measured. |
| 3 | **Supreme Court Shadow Docket Database** (CC0) | vacated (GVR); reversed (summary); cert denied as control | several thousand GVRs, a few hundred summary reversals, 1993–2024 | Ready-made, open licence, lower-court docket included. |
| 4 | **SCDB `caseDisposition` / `lcDisposition`** + "reported below" citation from our own U.S. Reports text | reversed / vacated / affirmed of courts of appeals and state high courts; second-level label for trial courts | 3,500–4,500 reversed/vacated and 2,000–2,500 affirmed (modern file); more from the legacy file | Reaches state supreme courts and pre-1946 decisions; keep separate from anything tuned on SCDB. |
| 5 | **Pre-1930 public-domain tables** (New York set, California set, Georgia 1922, Rapalje federal 1880, Greenleaf/Townshend 1856, Nebraska, North Carolina, Kentucky) | overruled; reversed / affirmed; doubted or limited as distractors | low thousands after OCR and citation mapping | The only independent key for overruled in the old state corpus; cost is OCR and nominative-reporter mapping. |
| 6 | **Lindquist, "State Politics and the Judiciary"** (accept terms, read codebook; write to the author if aggregates only) | overruled (state supreme courts) | unknown — potentially thousands of overruled/overruling pairs across 50 states | Highest upside for state "overruled"; content not yet confirmed. |
| 7 | **Brace & Hall State Supreme Court Data Project** (CC0) | reversed / vacated / affirmed of state intermediate appellate decisions, 1995–98 | about 21,000 supreme court decisions; perhaps 4,000–8,000 linkable published decisions below | Only open human-coded state key; linking is the work. |
| 8 | **Free Law Project citator benchmark** (request access) | overruled and other negative treatment, federal and state; direct history | 4,000+ finalised Supreme Court citations, about 1,300 lower federal and state citations at last report | Expert double-annotated and independent of the commercial citators; not yet released. |
| 9 | **California "review granted" lists** + Supreme Court minutes/conference results | depublished / not citable (with the 2016 rule change) | 2,640 review-granted published opinions listed; depublication orders must be harvested from minutes | Only official source for the depublished status; overlap with a corpus ending about 2020 may be small. |
| 10 | **Federal Circuit Dataset Project**; **en banc deposits** (Beim–Hirsch–Kastellec; Larsen) | Federal Circuit dispositions and en banc; en banc review of panel decisions | Federal Circuit: all opinions 2004–2024; en banc: a few thousand decisions in total | Fills the IDB's Federal Circuit gap and cross-checks item 2 on en banc. |

Also worth a letter: Paul Hellyer for his 357-relationship data set (the only test set with three citators' labels plus an independent reading), and Taylor's printed appendix (68 negative labels) as a tiny published set.

## 9. Things looked for and not found

- A cumulative public list of depublished California opinions.
- Any court-published list of overruled or abrogated precedent for a federal circuit or a state high court (modern).
- A free scan of Bigelow's 1873 *Index of the Cases Overruled*.
- Public-domain editions of the Texas writs-of-error table.
- A working download for the Hall & Windett state supreme court data.
- Any open "bad law" data from Casetext, Fastcase, vLex or other commercial citators.
- State judiciary bulk data with per-case appellate dispositions.
- A dedicated bankruptcy appellate panel data set.
- FJC data on the Supreme Court.
