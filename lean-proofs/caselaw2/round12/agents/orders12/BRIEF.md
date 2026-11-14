# Agent `orders12` (round 12): order-node data — missing Journal terms, the dropped ligature, the 2005 long lists (DESIGN12 §4)

Read `round12/DESIGN12.md` (§0 and §4) and `round12/agents/COMMON.md` first. Folder `round12/agents/orders12/`
(NOTES.md, a line at least every 10 minutes). Output folder `round12/data_orders/` (compact text only). Model:
round 11's data agent `orders11b` (`round11/agents/orders11b/`: NOTES.md, `scripts/parse_jnl.py`, `make_nodes.py`,
`append_nodes.py`, `counts2.py`) and `round11/data_orders/` (README.md, FORMAT.md, SOURCES.tsv, VALIDATION.md,
counts.tsv, journal/*.txt, nodes.tsv, text/). You may read `benchmarks/shadow_docket/SOURCE.md`, `MAPPING.md`,
`DISAGREEMENTS.md` and the h0 per-case file `round11/results/v11d/bench/shadow_docket.h0.cases.tsv` (h0 only, for
counting); nothing else under `benchmarks/`; never the closed keys.

## Start
Build `round12/data_orders/` as round 11's folder: `nodes.tsv` with round 11's 1,045 rows FIRST, same local ids, same
order (ids are assigned in file order, so the round-11 nodes keep their node ids), `text/`, `journal/` (copy only what
you change or add; the round-11 Journal texts can be read in place), README.md (what changed and why), SOURCES.tsv
(round 11's lines + yours), counts.tsv. Agent `shadow12` builds rows on your nodes; agent `infra12` stages them
(`round12/nodes12.py`, `stage12.py --nodes round12/data_orders`). Talk to them only through files in your folder and
data_orders (a `HANDOFF.md` with what is ready).

## Do (in this order; mark each step's data ready with a marker file so shadow12 can start)
1. **The dropped ligature (first ~25 minutes).** The later Journals' PyMuPDF extraction drops "fi" (and maybe "ff",
   "fl", "ffi", "ffl") ligatures: "affrmed", "fle", "Offce". Measure first: in the held Journal texts, how many entries'
   parse (disposition class, the node / not-node decision) and how many node captions (party names: "Griffn",
   "Sheriff"…) are affected. If it affects parsing or caption names, repair it by a documented rule. Preferred:
   re-fetch the affected Journals (same lawful way: `https://www.supremecourt.gov/orders/journal/JnlNN.pdf`, ≥ 3 s
   apart, one connection, generic user agent `Mozilla/5.0 (compatible; research-fetch)`, no WAF / CAPTCHA / login
   bypass — a 403 / 429 / challenge page = stop that source, record it) and re-extract with a glyph-aware method
   (PyMuPDF flags / `pdftotext` / pdfminer mapping ligature glyph names), PDFs deleted after conversion and hashing.
   If that is not possible, a normalisation rule: a token absent from the corpus vocabulary (build it from corpus
   decision texts of the same years, not from any key) that becomes a vocabulary word by inserting exactly one of
   fi/fl/ff/ffi/ffl at one position, uniquely → repaired; ambiguous → left. Document the rule in README.md with counts
   and 20 examples. Every node whose text changes: `CHANGED.tsv` (local id, old sha1, new sha1, what changed).
   Re-parse with the repair; nodes that newly appear go into the append steps below (never reorder the first 1,045).
2. **Missing Journal terms.** Held: OT2004–09, OT2014, OT2016, OT2019–25. Fetch OT2010–13, OT2015, OT2017–18 (≤ 7
   requests + any re-fetches of step 1; find the exact file names on `/orders/journal.aspx` — fetched once in round 11,
   its text may be in the orders11b folder — rather than guessing). Parse, validate the parser on one corpus-covered
   month as round 11 did (docket match / same date vs corpus S. Ct. nodes), and append nodes under round 11's rule: an
   entry of a node class becomes a node when at least one of its dockets has no corpus court-2906 node within ±10 days.
3. **The 2005 long lists.** Round 9 (`round9/agents/shadow9/NOTES.md`, "2005: 61 not parsed (long lists)") found
   2005 h0 misses whose corpus S. Ct. order node is a long list that the Shadow parsers cannot split. All 840 GVRs of
   2005 have a corpus node of the same docket and date, so round 11 made no node for them. Diagnose (h0 file for
   counting only): for the 2005 GVR entries, does the corpus node hold many dockets / captions (a long list)? If so,
   and only by a stated rule (e.g. "the docket's corpus node within ±10 days prints ≥ k other docket numbers"), add a
   per-entry Journal node for each such entry, `src` tag `r12:longlist` (distinct from `r11:orderlist`), appended
   after step 2's rows. Coordinate with shadow12 (it may instead split the corpus long-list text; write your finding
   in HANDOFF.md first, then build the nodes — shadow12 picks which to use).
4. Counts per step (entries, nodes per year and class, lower courts named), README.md, SOURCES.tsv, VALIDATION.md.
   Markers in `round12/data_orders/`: `LIGATURE_READY` (step 1 measured, decision written; text repaired if so),
   `DATA_READY_A` (steps 1–2), `DATA_READY` (all). Budget: ≤ 25 HTTP requests in all; no web search.

Report: requests made (all lines of SOURCES.tsv you added), the ligature finding + rule + counts (changed nodes),
the new terms' entries / nodes per year and class, parser validation, the 2005 long-list finding and nodes added,
sizes, anything blocked.
