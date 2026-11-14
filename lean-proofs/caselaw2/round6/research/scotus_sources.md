# Independent answer keys for US Supreme Court overrulings

Research date: 2026-11-13. Web research only; 26 of 30 searches used. Nothing copyrighted was kept.

Status tags used below:

- **[checked]** — I loaded the page or file and read the relevant part.
- **[partly checked]** — existence confirmed, contents only seen through an abstract, table of contents or a citing paper.
- **[recalled]** — from memory; not confirmed in this session. Verify before relying on it.

"Already used" sources (SCDB `precedentAlteration`; Constitution Annotated table, 2016 and current; Wikipedia list; Blaustein & Field 1958; Gerhardt 1991; Payne n.1) are only mentioned as parents of other lists.

---

## 0. Headline findings

1. **The Constitution Annotated table exists in at least nine distinct states, all public domain, and they differ.** Older editions include overrulings "deduced from the principles of related cases" (implied) and mark which rows are express. The 1973, 1982 and 1992 editions also record, per row, who first listed it (Brandeis, Douglas, Blaustein, or the editors). Rows were dropped between 2014 and 2015. This is the best free material for your weak spot (implied and partial overrulings).
2. **CRS Report R45319 (2018), Table A-1** has a column quoting the Court's operative overruling language for each of 141 rows. It is the only open source I found that states scope in the Court's own words. Check whether this is the "CRS table" you already have; it is a different document from the Constitution Annotated table.
3. **Fowler & Jeon's replication file (Harvard Dataverse, CC0)** carries `overruled` / `overruling` fields for all US Reports cases to 2002: 252 overruled cases, 191 overruling cases, 1810–1994. Their paper says it was coded from Brenner & Spaeth (1995) plus the 1987 Constitution Annotated. This is a lawful, open, machine-readable proxy for the Brenner & Spaeth list.
4. **Lists inside opinions**: Dobbs n.48 (28 overruling decisions with the overruled cases named, plus a dissent appendix analysing each), Ramos (Kavanaugh, 30 decisions, overruled cases not named), Burnet nn.1–4 (Brandeis, roughly 35 overrulings plus about 12 "qualified" cases), Smith v. Allwright n.10 (14 overruling, 17 overruled).
5. **No public deposit found** for Hansford & Spriggs, Spriggs & Hansford, or Black & Spriggs. Their Shepard's-based data appears to circulate by request (a 2026 working paper thanks Spriggs for sharing it).
6. **Almost everything else derives from the Constitution Annotated or SCDB.** That includes the 2025 LLM benchmark of 236 pairs, Free Law Project's citator test set, Pew's 2026 count, and (via Brenner & Spaeth) the Fowler file.

---

## 1. Lists inside Supreme Court opinions (public domain)

| Source | Pin | Size | Names the overruled case? | Status |
|---|---|---|---|---|
| **Dobbs v. Jackson Women's Health Org.**, 597 U.S. 215 (2022), majority n.48 | slip op. at 41–43 n.48 (U.S. Reports page about 265; confirm) | 28 overruling decisions, roughly 40 pairs, West Coast Hotel (1937) to Obergefell (2015) | Yes. Uses "overruling" and "partially overruling" (e.g. McConnell). One-line holding per case. | [checked] |
| **Dobbs dissent, Appendix** (Breyer, Sotomayor, Kagan) | slip op., dissent at 61 onward | Same 28 cases | Analyses, case by case, why each precedent was overruled (doctrinal erosion, changed facts). Good scope and grounds material. | [checked: opening paragraph only] |
| **Ramos v. Louisiana**, 590 U.S. 83 (2020), Kavanaugh concurring in part | slip op. (concurrence) at 2–4 and n.1 | 30 overruling decisions, 1937–2015 | No, except n.1 (Casey: Akron and Thornburgh overruled; Roe's trimester framework rejected) and Brown/Plessy in text. | [checked] |
| **Burnet v. Coronado Oil & Gas Co.**, 285 U.S. 393 (1932), Brandeis dissenting | 406–409 nn.1–4 | n.1: about 15 overruling decisions / 20 overruled (errors correctable by legislation). n.2: about 18 overrulings plus about 12 "qualified" cases plus 3 doctrine shifts with no express overruling. n.4: 2 pairs and 1 qualification. n.3 is quotations only. | Yes | [checked via LII; counts approximate] |
| **Smith v. Allwright**, 321 U.S. 649 (1944) | 665 n.10 | 14 overruling decisions, 17 overruled (1937–1943) | Yes | [checked via LII] |
| Citizens United v. FEC, 558 U.S. 310, 377–79 (Roberts concurring) | — | handful of examples | — | [recalled] |
| Janus v. AFSCME, 585 U.S. 878 (2018) (majority Part VI; Kagan dissent) | — | discussion, few pairs | — | [recalled; fetch failed] |
| Planned Parenthood v. Casey, 505 U.S. 833, 854–64; Rehnquist at 959 | — | Lochner and Plessy lines; count citing Payne | — | [recalled] |
| Patterson v. McLean Credit Union, 491 U.S. 164, 172–73 | — | short list of statutory overrulings | — | [recalled] |
| Others worth a text search: Helvering v. Hallock, 309 U.S. 106; Monell, 436 U.S. 658, 695; Agostini, 521 U.S. 203, 235–36; Seminole Tribe, 517 U.S. 44, 63; Alleyne (Sotomayor); Knick; Franchise Tax Bd. v. Hyatt (2019, Breyer dissent); Gamble (Thomas); Loper Bright (Gorsuch) | — | small | — | [recalled] |

Derivation: Dobbs n.48 is the Ramos list minus Casey and one other, with overruled cases added. Burnet nn.1–4 is a named parent of the Constitution Annotated table and of Blaustein & Field. Smith n.10 is not cited as a parent by any list I saw.

Verdict:
- (a) Held-out test: weak for coverage (landmark-biased, small) and Burnet is upstream of CRS. Smith n.10 and Dobbs n.48 are usable as small, clean, primary-text checks.
- (b) Training and diagnosis: good. Burnet n.2's "qualified" group and its "no express overruling" examples are labelled non-overrulings and implied shifts. The Dobbs dissent appendix gives grounds.

Related articles named as parents by the Constitution Annotated:
- William O. Douglas, "Stare Decisis", 49 Colum. L. Rev. 735, 735–43, 756–58 (1949). Paywalled (JSTOR, HeinOnline). [partly checked: cited as source in every edition header]
- **Emmet E. Wilson, "Stare Decisis, Quo Vadis?", 33 Geo. L.J. 251, 254 n.17, 265 (1945).** Not on your list. Paywalled (HeinOnline). [partly checked: same]

---

## 2. Editions of the Constitution Annotated (all US Government works)

The table "Supreme Court Decisions Overruled by Subsequent Decision" by edition:

| Edition (cases through) | Where | Rows | Notes | Status |
|---|---|---|---|---|
| 1952 (Corwin) | Project Gutenberg #18637; archive.org `theconstitutiono18637gut` | no table | Phrase does not occur in the text | [checked] |
| 1964 | archive.org `constitutionofun0000unit` (probably lending-only) | unknown | Not verified whether the table is present | [not checked] |
| **1973** (through June 1972) | archive.org `aey0081.1972.001.umich.edu` (open, OCR text) and `constitutionofun00unit_6` | about 143 (OCR estimate), from p.1787 | Has the provenance symbols (below) | [checked] |
| **1982**, published 1987 | archive.org `micro_IA41152617_0482` (open; microfiche, OCR very poor) | not countable from OCR | Same header and symbols. Needs page images. | [checked header] |
| 1986 and 1988 supplements | archive.org `micro_IA41152617_0483`, `micro_IA41152832_0424` (open) | add rows from about no. 176 (Illinois v. Gates, Pennhurst, Garcia, Batson, Solorio, Welch, Gulfstream…) | Shows "(in part)" flags | [checked] |
| **1992** | govinfo `GPO-CONAN-1992-13.htm` (HTML) | **204**, to Casey (1992) | Symbols: `*` express; `B`, `D`, `A` = first listed by Brandeis, Douglas, Blaustein; no symbol = added by editors. 43 "(in part)"; also "(limited)", "(in effect)", "qualifying", "substantially though not expressly overruled". | [checked] |
| 1996, 1998, 2000 supplements | govinfo `GPO-CONAN-1996` etc. (single PDFs) | not checked | | [exists] |
| **2002** | govinfo `GPO-CONAN-2002-12.pdf` | **220**, to US v. Hatter (2001) | B/D/A symbols gone; only `*` = expressly overruled. 48 "(in part)". | [checked] |
| 2004–2010 supplements | govinfo `GPO-CONAN-2004` … `2010` (single PDFs) | a secondary source says the 2004 supplement lists 225 through the 2003 Term | | [exists; not opened] |
| **2012, 2013, 2014, REV-2014** | govinfo `GPO-CONAN-2012-13.pdf`, `-2013-13`, `-2014-13`, `-REV-2014-13` | **233**, to McDonald (2010); identical to each other | 13 rows added to 2002 (nos. 221–233), none dropped. About 181 asterisks. | [checked] |
| **REV-2015** | govinfo `GPO-CONAN-REV-2015-13.pdf` | **235** | **Dropped**: Parents Involved → School Comm. of Boston (389 U.S. 572); Gonzales v. Carhart → Stenberg. **Added**: Alleyne → Harris; Obergefell → Baker v. Nelson; Johnson → James, Sykes. | [checked] |
| REV-2016 (you have), **2017** | govinfo `GPO-CONAN-REV-2016-13.pdf`, `-2017-13.pdf` | **236** | Adds Hurst → Hildwin, Spaziano. 2017 header states the new rule: only express overrulings or "the functional equivalent of an express overruling"; "other decisions may be added to or deleted from this list". | [checked] |
| 2018, 2020 supplements; 2022 edition | govinfo | no separate table section in the 2022 package | Table now lives on constitution.congress.gov (your "current") | [checked package listing] |

URL pattern: `https://www.govinfo.gov/content/pkg/GPO-CONAN-<edition>/pdf/GPO-CONAN-<edition>-13.pdf` (2002 uses `-12`; 1992 is `/html/GPO-CONAN-1992-13.htm`).

Coding rule: before 2017, express overrulings plus overrulings the editors deduced; express ones starred. From 2017, express or functional equivalent only. Partial overrulings flagged in text ("in part", "limited").

Why it matters:
- Non-starred rows in 1992–2014 (roughly 50) are a labelled set of **implied** overrulings.
- Rows present in 2014 but absent from the current table are a labelled set of "an authority once said overruled, and later withdrew it" — ideal hard cases.
- The dropped Parents Involved row is independently explained: Epstein, Landes & Liptak (2015) n.96 note that only the dissents cited School Committee of Boston, so neither SCDB nor Shepard's treats it as overruled.
- B/D/A symbols give per-row lineage, so you can measure agreement on rows the editors added themselves versus rows inherited from Brandeis, Douglas or Blaustein.

Licence: public domain. Independence: none from CRS (same family as your 2016 and current tables). Value is in the differences, not as a fresh key.

Verdict: (a) held-out test — only the rows that differ between editions, and the implied subset; (b) training and diagnosis — excellent.

### CRS reports (separate documents)

- **Brandon J. Murrill, "The Supreme Court's Overruling of Constitutional Precedent", CRS Report R45319 (24 Sept 2018), Appendix Table A-1.** https://www.everycrsreport.com/reports/R45319.html (also sgp.fas.org/crs/misc/R45319.pdf). Open, public domain. [checked]
  - 141 rows, constitutional questions only, The Propeller Genesee Chief (1851) to Janus (2018).
  - Columns: No.; Overruling Decision; Date; Overruled Decision(s); Date; **Operative Language** (quotation, e.g. "To the extent that Metro Broadcasting is inconsistent with that holding, it is overruled").
  - Rule: "a majority of the Court must have explicitly stated, in a subsequent decision, that the case has been overruled". Built by a LEXIS search for "overrule", cross-checked against unnamed other sources. Includes partial overrulings and qualifications; excludes cases merely distinguished or limited and cases only called overruled by concurrences, dissents or commentators.
  - Derives from: its own Lexis search. The current constitution.congress.gov table appears to be this method extended to statutory cases (inference from matching method text; not confirmed).
  - Verdict: (a) not independent of CRS, and partly redundant if your "current" table already has the same rows; (b) **best open source for scope** — obtain for the operative-language column.
- George Costello, "The Supreme Court's Overruling of Constitutional Precedent: An Overview", CRS RL33172 (29 Nov 2005). Open copy at stuff.mit.edu (WikiLeaks CRS mirror). Narrative with examples of overruling and of declining to overrule; no systematic table seen. [checked title and abstract only]

---

## 3. Scholarly datasets

### 3.1 Open and downloadable

**Fowler & Jeon, "The Authority of Supreme Court Precedent", Social Networks 30 (2008) 16–30 — replication data.** [checked]
- URL: Harvard Dataverse, doi:10.7910/DVN/XMBQL6 (the old jhfowler.ucsd.edu page no longer resolves). Mirror with tidy formats: https://networks.skewed.de/net/scotus_majority (2008 version has node attributes `overruled`, `overruling`).
- Licence: CC0 1.0 on Dataverse.
- Files: `Judicial.tab` (30,288 cases, US Reports 1754–2002), `Allcites.txt` (citation edges), authority/hub matrices by year.
- Fields: `caseid`, `usid` (e.g. `3US171`), `parties`, `year`, `overruled` (caseid of the overruling case), `overruling` (caseids overruled), `oxford`, `liihc`, degree and centrality scores.
- Size: **252 overruled cases, 191 overruling cases, overruling years 1810–1994** (my count from the file).
- Coding rule and lineage (from the paper): Brenner & Spaeth (1995) for the modern period (154 overruled precedents) plus the Constitution Annotated (cited as CRS 1987) for earlier ones. No partial or implied flag; one overruler per overruled case.
- Verdict: (a) not independent — Brenner & Spaeth is Spaeth's own coding (same lineage as SCDB) and the rest is CRS; still useful as a frozen 1995-era snapshot; (b) good, and it is the lawful open stand-in for the Brenner & Spaeth appendix. Comes with a full citation network.

**Epstein, Landes & Liptak, "The Decision to Depart (or Not) from Constitutional Precedent: An Empirical Study of the Roberts Court", 90 N.Y.U. L. Rev. 1115 (2015).** [checked paper; data link reported by search, not opened]
- Paper: https://epstein.wustl.edu/s/DeparturesFromPrecedent.pdf. Data: zipped Stata file linked from https://epstein.wustl.edu/departuresfromprecedent (the URL printed in the article is dead).
- Content: Roberts Court, 2005–2013 terms. 628 cases searched; in 288 a brief attacked or defended a precedent; 455 distinct precedents under attack (listed in the paper's Appendix).
- Two outcome variables: (1) formally overruled, taken from SCDB after checking against the Constitution Annotated and Shepard's; (2) "departure", from Shepard's treatment by the majority (criticized, distinguished, limited, questioned, overruled versus followed or neutral).
- Footnote 96 documents specific disagreements between SCDB, the Constitution Annotated and Shepard's (School Committee of Boston; Leegin/Dr. Miles; Wal-Mart/Eisen).
- Licence: none stated; academic replication file.
- Verdict: (a) the overruled flag is SCDB, so not independent; the Shepard's-based departure variable **is** independent of SCDB and CRS; (b) very good — it is the only open set with **hard negatives** (precedents attacked but not overruled) and graded negative treatment.

### 3.2 Not publicly deposited (ask the authors)

**Hansford & Spriggs, The Politics of Precedent on the U.S. Supreme Court (Princeton UP, 2006).** [partly checked]
- About 6,363 Supreme Court precedents, 1946 onward (a citing paper says through 1999), with yearly counts of positive and negative Shepard's treatments by the Court. The book's appendix explains how they resolved conflicting authorities on whether a case was overruled (per Epstein et al. n.92).
- No Dataverse, ICPSR or author-page download found (Hansford's publications page has none for this title). Cape & Kastellec's 2026 working paper (Princeton; page returned 403 to me) extends "existing data on Shepard's treatments of Supreme Court majority opinions from 1953 through 2023" and thanks Spriggs for sharing — so the route is a request to James Spriggs (Washington University in St. Louis).
- Derives from Shepard's Citations (LexisNexis editorial coding). Shepard's-derived labels may carry licence limits on redistribution.
- Verdict: (a) the most independent key available in principle (neither SCDB nor CRS), and it covers partial, limited and questioned treatment; (b) excellent, if obtained.

**Spriggs & Hansford, "Explaining the Overruling of U.S. Supreme Court Precedent", 63 J. Politics 1091 (2001).** [partly checked]
- 1946–1995 terms; every precedent with an overruled-or-not outcome. Open working-paper version: https://escholarship.org/uc/item/4ht6r11q (the index mentions supplemental material; not opened). Cites Brenner & Spaeth's 154. Exact list source: [recalled] Brenner & Spaeth updated with Shepard's and CRS.
- Companion: Spriggs & Hansford, "Measuring Legal Change: The Reliability and Validity of Shepard's Citations", Political Research Quarterly 53 (2000) — reliability evidence for Shepard's categories. [partly checked]

**Black & Spriggs, "The Citation and Depreciation of U.S. Supreme Court Precedent", 10 J. Empirical Legal Stud. 325 (2013).** 6,299 decisions, 1946–2004 terms; citations by the Supreme Court and courts of appeals. No deposit found. Citation counts, not overruling labels. [partly checked]

**Fowler, Johnson, Spriggs, Jeon & Wahlbeck, "Network Analysis and the Law", Political Analysis 15 (2007) 324.** 26,681 majority opinions 1791–2005 keyed by LexisNexis ID. The copy on Netzschleuder (2007 version) has importance measures but **no** overruled or treatment field. [checked on Netzschleuder]

### 3.3 Books and articles with printed lists (not open)

- **Brenner & Spaeth, Stare Indecisis: The Alteration of Precedent on the Supreme Court, 1946–1992 (Cambridge UP, 1995).** Appendix I: overruling and overruled decisions of the Vinson, Warren, Burger and Rehnquist Courts; Appendix II: list of overruled cases. 154 overruled precedents. Pages 19–23 discuss conflicting authorities. Paywalled (Cambridge Core); no replication deposit found. Open proxy: the Fowler & Jeon file above. Lineage: Spaeth, so close to SCDB. [partly checked]
- **Gerhardt, The Power of Precedent (Oxford UP, 2008).** "Appendix Tables I–VII" confirmed from a bookseller's contents listing. No open copy, SSRN version or data found. [partly checked]
- **Clarke Rountree, Overturned: The Rhetoric of Overruling in the United States Supreme Court (University of Alabama Press, 2024).** Appendix A "US Supreme Court Overruling and Overruled Cases" (pp. 257–274); **Appendix B "Cases Excluded from Overruling List"** (pp. 275–276). Publisher describes nearly 300 overruled rulings. Paywalled (Project MUSE book 124015; print). Inclusion rule and parent lists not visible. Appendix B is a rare explicit list of rejected candidates. [partly checked]
- Sarat, Beougher & Lahue, "The Dobbs Difference: the Rhetoric of Overruling in the United States Supreme Court", British J. American Legal Studies (2025), doi:10.2478/bjals-2024-0006. Open access, CC BY-NC-ND 3.0. Says it examines "every overruling case in the history of the Court"; source list and any appendix not confirmed. [partly checked]
- Christopher P. Banks, "Reversals of Precedent and Judicial Policy-Making", 32 Akron L. Rev. 233 (1999). Free PDF: https://ideaexchange.uakron.edu/akronlawreview/vol32/iss2/1 (direct download returned 403 to me). Rehnquist Court reversals; whether it prints a case table is not confirmed. Also Banks, 75 Judicature 262 (1992). [partly checked / recalled]
- Amy L. Padden, "Overruling Decisions in the Supreme Court", 82 Geo. L.J. 1689 (1994) — constitutional overrulings; notes her count differs from Payne n.1. [cited in Epstein et al.; not opened]
- Lindquist & Cross, Measuring Judicial Activism (Oxford UP, 2009); Segal & Howard, "How Supreme Court Justices Respond to Litigant Requests to Overturn Precedent", 85 Judicature 148 (2001) (requests to overrule, so includes refusals). [cited in Epstein et al.; not opened]
- Benesh & Reddick, "Overruled: An Event History Analysis of Lower Court Reaction to Supreme Court Alteration of Precedent", 64 J. Politics 534 (2002). Uses a set of overruling decisions; no data link found. [partly checked]
- William N. Eskridge Jr., "Overruling Statutory Precedents", 76 Geo. L.J. 1361 (1988) — appendix of statutory precedents overruled, about 1961–1987. Appendix contents [recalled]; an Open Yale repository entry exists but returned 403.
- Epstein, Segal, Spaeth & Walker, The Supreme Court Compendium — table of decisions overruled. Not found online; [recalled] that it reproduces the Constitution Annotated table. Low priority.
- Schmidhauser, 14 U. Toronto L.J. 194 (1962); Ulmer, 8 J. Pub. L. 414 (1959); Maltz, 1980 Wis. L. Rev. 467; Israel, 1963 Sup. Ct. Rev. 211. [recalled]; no data found; all pre-date and are absorbed by later lists.

---

## 4. Official and semi-official lists

- **Library of Congress / CRS — constitution.congress.gov "Decisions Overruled"**: your current source. Pew (April 2026) counts 236 overruling rulings through the 2024 Term from it. The 2017 print table also had 236 rows ending in 2016, so the web table has both gained recent rows and shed older (implied) ones — worth diffing against 2017. [Pew page checked]
- **GPO / govinfo**: section 2 above. [checked]
- **Supreme Court website, Federal Judicial Center, Oyez**: no list found by search. [not exhaustive]
- **Cornell LII, Justia, FindLaw**: host copies of the Constitution Annotated (Justia: 2012 Centennial edition). Derivative. Justia per-case "overruled" annotations: not verified (Justia returned 403). [partly checked]
- **Wikidata property P4006 "overrules"**: 19 statements in total, 12 on US cases. Negligible. [checked by query]
- **Wikipedia**: besides the list you use, the per-case infobox "overruled by" field, "Category:Overruled United States Supreme Court decisions", and "List of abrogated United States Supreme Court decisions" (displaced by amendment or statute — useful as *not overruled by the Court* controls). Same community as your Wikipedia key. [existence checked]
- **Pew Research Center, "How often does the Supreme Court overturn its own decisions?" (8 Apr 2026)**: aggregates only, built from the Library of Congress list plus SCDB. Derivative. [checked]
- **Commercial citators** (Shepard's, KeyCite, Bloomberg BCite, vLex/Fastcase, Casetext): independent editorial coding with "overruled in part" style scope, but paywalled and licence-restricted. Not accessed.

---

## 5. Machine-learning datasets

**Casetext "Overruling" dataset** (in Zheng, Guha, Anderson, Henderson & Ho, "When Does Pretraining Help?", ICAIL 2021, arXiv:2104.08671; reused as the LegalBench `overruling` task). [checked]
- 2,400 sentences, binary. Positives: overruling sentences picked by Casetext attorneys. Negatives: random sentences from the Casetext corpus. Class balance not stated in the paper ([recalled] roughly even).
- All US courts in Casetext, not Supreme Court-specific (the paper's example is a state supreme court sentence). Sentences are lower-cased and do not carry case identifiers, so they cannot be turned into Y-overruled-X pairs.
- Evaluation in the paper: 10-fold cross-validation.
- Access: Google Drive link from https://github.com/reglab/casehold (repo Apache-2.0); LegalBench task page lists **CC BY 4.0**. It is in LegalBench, not (as far as I recall) in LexGLUE.
- Verdict: (a) not a test of your pairs; (b) useful for training or testing an "is this sentence an overruling statement" detector, including state-court phrasing such as "disapprove" and "recede from".

**Zhang, Savelka & Ashley, "Do LLMs Truly Understand When a Precedent Is Overruled?", JURIX 2025, arXiv:2510.20941.** [checked]
- 236 Supreme Court overruling pairs with full opinion text (from CourtListener). Fields seen: `case_name`, `citation`, `cleaned_text_opinion`.
- Built from the Constitution Annotated list plus a Lexis "overrule" search; explicit majority overrulings only.
- https://github.com/lizhang-AIandLaw/Do-LLMs-Truly-Understand-When-a-Precedent-Is-Overruled — password-protected zip (password in the README, to limit training contamination); **CC BY-NC-SA 4.0**.
- Verdict: derivative of CRS; no new labels. Convenient pre-joined texts only.

**Free Law Project, AI citator experiment (1 May 2025)**, https://free.law/2025/05/01/citator/. 149 overruled opinions taken from the Constitution Annotated table, mixed with random CourtListener opinions at about 15:100. No labelled data released yet; open-source citator promised. Derivative. [checked]

**Demir & Canbaz, "Validate Your Authority: Benchmarking LLMs on Multi-Label Precedent Treatment Classification", arXiv:2605.17691.** 239 expert-annotated citations with coarse and fine treatment labels. Paper is CC BY 4.0; courts, label names and data location not visible from the abstract. Small, but the only open multi-label treatment set found. [checked abstract only]

**Lawma / CaselawQA** (arXiv:2407.16615; Hugging Face `ricdomolm/lawma-all-tasks`). 260 tasks generated from SCDB and the Songer database, so any precedent-alteration task is SCDB again. Whether that task is included was not confirmed. [partly checked]

CourtListener and the Caselaw Access Project publish citation graphs without treatment labels. [recalled]

---

## 6. Sources that give dates, scope, or implied overrulings

| Need | Best source |
|---|---|
| Court's exact overruling words, "to the extent" limits | CRS R45319 Table A-1, Operative Language column (141 rows) |
| "In part", "limited", "qualifying", "in effect" flags | Constitution Annotated 1992 (43 "in part") and 2002–2017 editions; 1986/1988 supplements |
| Implied (not express) overrulings | Non-starred rows in Constitution Annotated 1973–2014; Burnet n.2 "qualified" group |
| Claimed overrulings later withdrawn | Rows dropped between editions (2014 → 2015 → current); Rountree Appendix B (paywalled) |
| Disagreement between authorities | Epstein, Landes & Liptak n.96; Brenner & Spaeth pp. 19–23; Hansford & Spriggs appendix |
| Graded negative treatment (limited, questioned, criticized) | Epstein–Landes–Liptak data (open, Roberts Court); Hansford–Spriggs data (by request) |
| Grounds for overruling | Dobbs dissent Appendix (28 cases) |
| "Partially overruling" in the Court's own list | Dobbs n.48 |
| Dates | R45319 has decision dates for both sides; Fowler file has years |

---

## 7. Ranked top 10 to obtain first

| # | Source | Access | Independence from SCDB / CRS |
|---|---|---|---|
| 1 | **CRS R45319 Table A-1** (141 rows with operative language) | Open, public domain | Independent of SCDB (Lexis search, explicit-majority rule). Not independent of CRS; probably the ancestor of the current web table. Take it for scope, not as a fresh key. |
| 2 | **Constitution Annotated edition series**: 1973, 1982 + 1986/1988 supplements, 1992 (HTML, provenance symbols), 2002, 2012, REV-2015, 2017 | Open, public domain | Same CRS family as two of your keys. The independent signal is in the diffs: implied rows, withdrawn rows, per-row lineage (B/D/A). |
| 3 | **Fowler & Jeon `Judicial.tab`** (252 overruled, 191 overruling, to 1994) | Open, CC0 | Low: Brenner & Spaeth (Spaeth lineage, like SCDB) plus Constitution Annotated 1987. Value: frozen 1995-era snapshot, machine-readable, and the open proxy for Brenner & Spaeth. |
| 4 | **Epstein, Landes & Liptak dataset** (Roberts Court precedents under attack) | Open (.dta) | Overruled flag is SCDB. The Shepard's "departure" variable and the attacked-but-kept negatives are independent of both. |
| 5 | **In-opinion lists**: Dobbs n.48 + dissent Appendix; Smith v. Allwright n.10; Burnet nn.1–4; Ramos (Kavanaugh) | Open, public domain | Authored by Justices, so independent of SCDB. Burnet is a parent of the CRS table; Dobbs, Ramos and Smith are not derived from CRS as far as I can tell. Small and landmark-biased. |
| 6 | **Hansford & Spriggs / Spriggs Shepard's treatment data** (1946–1999, extended to 2023 by Cape & Kastellec) | By request to Spriggs | High: Shepard's editorial coding, neither SCDB nor CRS. Only source with partial and graded treatment at scale. Check redistribution terms. |
| 7 | **Brenner & Spaeth, Stare Indecisis**, Appendices I–II and pp. 19–23 | Library / Cambridge Core | Low to medium: Spaeth is the author of SCDB, but the book hand-reconciles authorities and predates later SCDB revisions. Mostly superseded by #3 unless you need its reasoning. |
| 8 | **Rountree, Overturned**, Appendix A (about 300) and Appendix B (excluded cases) | Library / Project MUSE | Unknown; a 2024 hand compilation by a rhetoric scholar, likely started from CRS and Wikipedia. Appendix B is the draw. |
| 9 | **Gerhardt, The Power of Precedent**, Appendix Tables I–VII | Library (no open copy found) | Medium: Gerhardt's own Lexis-based compilation, successor to the 1991 appendix you already use, so overlap will be high. |
| 10 | **Casetext Overruling sentences** (2,400) | Open, CC BY 4.0 per LegalBench | Fully independent of both, but it labels sentences from all US courts, not Supreme Court pairs. Training and diagnosis only. |

Runners-up: Wilson (1945) and Douglas (1949) originals (parents of the CRS table, paywalled); Eskridge (1988) appendix for statutory overrulings; Demir & Canbaz treatment set; Padden (1994).

Bottom line on independence: only three families are truly independent of each other — **Spaeth** (SCDB, Brenner & Spaeth, Fowler file), **CRS** (every Constitution Annotated edition, R45319, the 2025 LLM benchmark, Free Law Project, Pew), and **Shepard's** (Hansford & Spriggs; the Epstein departure variable). Wikipedia, Gerhardt and Rountree are hand compilations that draw on the first two. The Justices' own lists are a fourth, small family. A Shepard's-derived key is the one genuinely new axis you do not yet have.
