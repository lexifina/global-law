# Agent `orders11b` (round 11): resume `orders11` — parse the Journal of the Supreme Court into order nodes

Your task is `round11/agents/orders11/BRIEF.md` (read it, and DESIGN11 §0 + §4, COMMON.md). `orders11` went silent at
05:16 after fetching and converting; you resume from its files and own `round11/data_orders/` from now on.
Folder `round11/agents/orders11b/` (NOTES.md, a line every 10 minutes — the lead replaces silent agents).

## State you inherit
- `round11/data_orders/SOURCES.tsv`: every fetch so far (Journal PDFs OT2005–OT2009, OT2019–OT2025 from
  https://www.supremecourt.gov/orders/journal/jnlNN.pdf, all HTTP 200; the order-list index `ordersofthecourt/<yy>`
  only covers OT2010+, and a guessed 2008 "zor" PDF was 404). Copy, never rewrite, earlier lines; append yours.
- Converted text (PyMuPDF, page breaks = form-feed lines): `round11/agents/orders11/txt/jnl/*.txt`. PDFs in
  `round11/agents/orders11/dl/jnl*/` — once you have checked the text is complete, delete those PDFs (they are
  hashed in SOURCES.tsv).
- `round11/data_orders/FORMAT.md` (by infra11): the exact node format you must write — read it first.
- **Do not re-fetch** what is there. More fetches only if needed (≤ 30, ≥ 3 s apart, generic user agent, stop on
  any 403/429/challenge; log each in SOURCES.tsv).

## Do (fast — shadow11 and infra11 are waiting)
1. Read a few pages of one Journal text to learn its layout: per sitting date ("Monday, January 12, 2009"), entries
   like "No. 07-1234. JOHN SMITH, PETITIONER v. UNITED STATES. On petition for writ of certiorari to the United
   States Court of Appeals for the Ninth Circuit. Motion of petitioner for leave to proceed in forma pauperis
   granted. Petition for writ of certiorari granted. Judgment vacated, and case remanded to the United States Court
   of Appeals for the Ninth Circuit for further consideration in light of X v. Y, 555 U. S. ___ (2009)." — verify
   the real wording; do not assume this.
2. Parser: one node per docket entry (or per printed group of dockets disposed of together) whose disposition is GVR
   / judgment vacated / reversed / affirmed / vacated and remanded (skip plain cert denials, but count them),
   for calendar 2006-01-01 … 2009-12-31 and 2020-07-01 … 2025-12-31 (the corpus has order lists through 2006 in U.S.
   Reports and 2010–mid 2020 in S. Ct.; check with `graph/nodes.tsv` / decisions2 court 2906 which months of 2006
   and 2020 the corpus already holds as memorandum orders and skip those months). Node text = the sitting-date
   heading + the entry verbatim (caption line(s) + court below + disposition). Write `nodes.tsv` + `text/<id>.txt`
   per FORMAT.md. **Write `DATA_READY_PARTIAL` (with the years covered) as soon as OT2007–OT2009 are done**, then
   the rest, then `DATA_READY`.
3. Validate the parser without any key: run it on one OT2010–2018 Journal (≤ 2 fetches) for a month the corpus
   has as S. Ct. memorandum orders and compare entries (dockets, captions, dispositions) with the corpus's order
   nodes for that month; report agreement counts.
4. Counts per year: entries by disposition class, GVR / vacated entries, lower courts named.
Report: lists/Journals used, entries per year per class, parser validation, files and sizes, anything blocked.
