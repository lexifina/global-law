# round11/data_orders: Supreme Court order nodes from the Journal of the Supreme Court

Owner: `orders11b` (resumed `orders11`). Format: `FORMAT.md` (infra11).

## Source
The Journal of the Supreme Court of the United States (the Court's official minutes), one PDF per Term, from
`https://www.supremecourt.gov/orders/journal/jnlNN.pdf` (OT2005-OT2009, OT2019-OT2025; all HTTP 200, hashes in
`SOURCES.tsv`). The per-Term order-list index (`/orders/ordersofthecourt/<yy>`) covers OT2010+ only. Each sitting date
prints every order entered that day, in sections ("Certiorari—Summary Dispositions", "Orders in Pending Cases",
"Certiorari Denied", ...), each entry as "No. 07–1154. <caption>. On petition for writ of certiorari to <court below>.
<disposition>". PDFs converted with PyMuPDF (page break = a form-feed line) and deleted after checking page counts;
the texts are kept in `journal/<stem>.txt`. `list_file` in nodes.tsv is the SOURCES.tsv `local_file` (the PDF name);
`line_span` refers to the 1-based lines of `journal/<same stem>.txt`.

## Nodes
One row per printed Journal entry (or printed group of dockets disposed of in one paragraph, `;`-joined dockets)
dated 2006-03-01 … 2009-12-31 or 2020-07-01 … 2025-12-31 (the corpus holds Supreme Court memorandum orders for
2006-01/02 and up to 2020-06; 2020-06 is thin in the corpus, 72 decisions, and is not covered here), whose disposition
is one of:
- `gvr`: certiorari granted + judgment vacated + case remanded (incl. Munsingwear vacaturs);
- `vacated`: judgment vacated without a cert grant in the entry (appeals, motions to vacate);
- `order_vacated`: a lower court's order / injunction / stay vacated (emergency applications; not a Justice's or the
  Court's own earlier order);
- `granted_remanded`: certiorari granted and case remanded without the word "vacated" (e.g. after the Court reversed
  the same judgment in a companion case);
- `affirmed`: summary affirmances on appeal, and affirmances for want of a quorum (28 U.S.C. 2109);
- `reversed`: none found outside Opinion sections.
Entries under "Opinion(s)" / "Opinion(s) Per Curiam" headings (argued cases and per curiam opinions, which the corpus
holds as opinions) are not nodes; they are listed in `opinion_entries.tsv`. Cert denials, dismissals and other orders
are counted only (`counts.tsv`).

Node text (`text/<local_id>.txt`): the sitting-date heading, the section heading, the caption line(s) of the entry,
and the rest of the entry (court below + disposition + any statements printed with it) on one line, as printed.
Normalisation only: line breaks joined with a space; end-of-line hyphenation removed (soft hyphens, and plain hyphens
between lower-case letters as the OT2005-2007 Journals print them); ligatures ﬁ/ﬂ expanded; tabs to spaces; NFC.
Later Journals' PDFs drop the "fi" ligature in extraction ("affrmed", "fle", "Offce"); that is kept as extracted.

local_id = `jn<yyyymmdd>_<n>` where n = the entry's ordinal among all entries printed on that sitting date.

## Appended rows (DATA_READY2, lead rule of 06:0x)
Rows 981-1045 of nodes.tsv were appended after the original 980 (whose lines and text files are unchanged). Rule,
over every entry of every Journal held (OT2004-OT2009, OT2014, OT2016, OT2019-OT2025; jnl04, jnl14, Jnl16 added to
`journal/`): an entry of a node class that is not already a node becomes a node when at least one of its dockets has
no corpus court-2906 node (round-6 cache meta) dated within +-10 days of the entry's date. Added 65 (gvr 62,
vacated 3) by month: 2010-01 9, 2015-06 1, 2020-03 4, 2020-06 4, 2026-01 4, 2026-03 1, 2026-04 7, 2026-05 3,
2026-06 32 (2026 rows are last in the file). 1,156 candidate entries were covered by a corpus node (all 840 GVRs of
2005 have a corpus node of the same docket on the same date). `counts.tsv` now covers every held Journal year (all
entries per class, and nodes per year in nodes.tsv).

Scripts: `round11/agents/orders11b/scripts/parse_jnl.py`, `make_nodes.py`, `append_nodes.py`, `counts2.py`.
