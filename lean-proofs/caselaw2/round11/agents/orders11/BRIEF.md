# Agent `orders11` (round 11): Supreme Court order lists missing from the corpus (2006–09, 2020–25) as staged data (DESIGN11 §4)

Read `round11/DESIGN11.md` (§0 and §4) and `round11/agents/COMMON.md` first. Folder `round11/agents/orders11/`
(NOTES.md, a line at least every 10 minutes). Output folder `round11/data_orders/` (compact text only). You may read
`benchmarks/shadow_docket/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 per-case file
`round10/results/v10d/bench/shadow_docket.h0.cases.tsv` (h0 only, for counting the gap); nothing else under
`benchmarks/`; never the closed keys.

## Why
Shadow Docket h0 recall is 514/1,059 = 48.5%. 281 h0 NEG orders are not in the corpus at all (round 9 `shadow9`
`work/gap_counts.txt`: by order year 2006:28 2007:21 2008:79 2009:26 2020:11 2021:32 2022:28 2023:6 2024:32 2025:14;
federal 268 / state 13; GVR 268, vacated 13). The corpus has order lists through 2006 (U.S. Reports) and 2010–mid 2020
(S. Ct.); 2007–09 and 2021–25 hold merits opinions only (`round9/agents/shadow9/work/sc_corpus_by_year.txt`). The
existing Shadow rules (round 8 `orderdock`, round 9 `shadow9`, round 10 `shadow10` C6 full-name caption link) work on
order nodes; with the orders present, agent `shadow11` builds the rows.

## Do
1. **Source and feasibility (first ~20 minutes).** supremecourt.gov publishes order lists per term
   (https://www.supremecourt.gov/orders/ordersofthecourt/<yy>, PDFs under /orders/courtorders/) and the Journal of the
   Supreme Court (/orders/journal.aspx). Both are U.S. government works (public domain). Check: which terms are
   online; that plain HTTPS GETs work at a polite pace (≥ 3 s between requests, a single connection, a generic
   user agent such as `Mozilla/5.0 (compatible; research-fetch)` — never a person's name or email). **A 403 / 429 /
   challenge or CAPTCHA page means stop that source** (do not retry with other headers, proxies or browsers to get
   around it); record it and try the next lawful public source (e.g. the Journal; GovInfo; LII). Budget: at most
   ~900 HTTP requests in total; no web search tool calls beyond ~10. Record every fetched URL, date-time, HTTP status,
   bytes and sha256 in `round11/data_orders/SOURCES.tsv`.
2. **Fetch** the regular order lists ("zor" lists) and miscellaneous orders that dispose of cases, for calendar 2006
   through 2009 and mid-2020 through 2025 (check against the corpus which 2006 and 2020 lists the corpus already has:
   `graph/nodes.tsv`, S. Ct. / U.S. order texts; fetch what is missing; do not duplicate lists the corpus has). Each
   download into its own fresh empty folder under your agent folder (untrusted); convert PDF → text with PyMuPDF or
   pdftotext under `python -I` / a separate script folder; keep only the text; delete the PDF after conversion and
   hashing. Disk: whole output well under 200 MB.
3. **Parse** each list into entries: docket number(s) (e.g. `07-1234`, `08-5678`), caption as printed (petitioner
   `V.` respondent, with full names as printed), the disposition (GVR: "The petition for a writ of certiorari is
   granted. The judgment is vacated, and the case is remanded to the United States Court of Appeals for the Ninth
   Circuit for further consideration in light of X v. Y, 555 U. S. ___ (2009)."; "vacated and remanded";
   "reversed"; summary affirmances; per curiam summary reversals printed in the list), the list's date. Entries that
   only deny certiorari are counted but not turned into nodes. Write the node files in the format `infra11` puts in
   `round11/data_orders/FORMAT.md` (DESIGN11 §4: `nodes.tsv` + `text/<local id>.txt` = the date heading, caption
   line(s) and disposition sentence(s) verbatim; one node per disposed docket entry, or one per printed group when
   the list disposes of several dockets in one paragraph — keep all dockets in the row). If FORMAT.md is not there
   yet, write your proposal in `round11/data_orders/FORMAT_PROPOSAL.md` and continue.
4. **Check** on corpus overlap: for months where the corpus has the order list (e.g. 2010–2019), parse a few of
   your fetched lists for those months too (≤ 10 extra fetches) and compare your entries with the corpus's order
   nodes (count, caption, disposition) — this validates the parser without any key.
5. Count: lists fetched per year, entries per disposition class per year, GVR / vacate entries per year, and how many
   of the GVR entries name a lower court in the corpus's federal circuits / state courts. Marker
   `round11/data_orders/DATA_READY` when nodes.tsv + text are complete for what you could fetch (write partial
   READY early — e.g. 2007–2009 first — as `DATA_READY_PARTIAL` with the years, so `shadow11` can start).
If any source is blocked or not lawful to fetch automatically, write `round11/data_orders/FEASIBILITY.md` (what
failed — URL, status, time —, what was tried, what it would take) and report.
Report: source(s), URLs pattern, requests made, lists and entries per year, parser validation on corpus overlap,
files, sizes, anything blocked.
