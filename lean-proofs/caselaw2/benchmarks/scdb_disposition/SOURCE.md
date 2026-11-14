# Source: Supreme Court Database (SCDB) — disposition fields

## What was downloaded (2026-11-13, public pages, no login, no terms to accept)

| file (raw/) | URL | release | sha256 |
|---|---|---|---|
| `modern_2026_01/SCDB_2026_01_caseCentered_Citation.csv.zip` | http://scdb.wustl.edu/_brickFiles/2026_01/SCDB_2026_01_caseCentered_Citation.csv.zip | SCDB_2026_01, released 2026-09-07, terms 1946–2025, 9,409 rows | 4d8f34d56363f8c140917bb556c530ee120aaaed6ed564a27866c0e5155e73f7 |
| `legacy_07/SCDB_Legacy_07_caseCentered_Citation.csv.zip` | http://scdb.wustl.edu/_brickFiles/Legacy_07/SCDB_Legacy_07_caseCentered_Citation.csv.zip | SCDB_Legacy_07, released 2021-10-01, terms 1791–1945, 19,861 rows | ee7759bc96253992d3749f6ba144d00810f63f424b43bf096f9d0b55551da420 |
| `pages/data_modern.html` | http://scdb.wustl.edu/data.php | download page (modern) | afdd38e0…f8c6 |
| `pages/data_legacy.html` | http://scdb.wustl.edu/data.php?s=2 | "Previous versions" page listing the Legacy_07 files | a7e875ff…7751 |
| `pages/cb_<var>.html` | http://scdb.wustl.edu/documentation.php?var=<var> | codebook pages: caseDisposition, caseDispositionUnusual, lcDisposition, lcDispositionDirection, caseSource, caseSourceState, caseOrigin, caseOriginState, decisionType, jurisdiction, usCite | see `sha256sum raw/pages/*` |

Both are the case-centred "Cases Organized by Supreme Court Citation" files (one row per dispute). The research note
said scdb.la.psu.edu; today that host answered 403 and the old scdb.wustl.edu host served everything. Files are
treated as untrusted: each in its own folder, read only as zip/CSV data by `extract.py` run with `python -I`.

**Licence as stated on the download page:** "The Supreme Court Database is licensed under a Creative Commons License"
linking to http://creativecommons.org/licenses/by-nc/3.0/us/ (CC BY-NC 3.0 US). We keep the downloaded files and derived
facts locally for evaluation (non-commercial research use); citing convention: SCDB_2026_01 / SCDB_Legacy_07.

## Fields used (codebook meaning)

- `caseId` — SCDB case id (term-sequence); the stable key of the hash split.
- `usCite`, `sctCite`, `ledCite` — U.S. Reports / S. Ct. / L. Ed. citations; used to find our Supreme Court opinion.
- `dateDecision` — date of decision (checks the Supreme Court link; the decision below must be earlier).
- **`caseDisposition`** — "The treatment the Supreme Court accorded the court whose decision it reviewed": 1 stay,
  petition, or motion granted; 2 affirmed (includes modified); 3 reversed; 4 reversed and remanded; 5 vacated and
  remanded; 6 affirmed and reversed (or vacated) in part; 7 same and remanded; 8 vacated; 9 petition denied or appeal
  dismissed; 10 certification to or from a lower court; 11 no disposition. Empty for original jurisdiction unless 1/9.
  **This is the answer key's outcome variable.**
- `caseDispositionUnusual` — 1 when the Court's language does not fit the code (such rows are not scored).
- `caseSource`, `caseSourceState` — the court whose decision the Supreme Court reviewed (federal courts of appeals,
  district courts, old circuit courts, special federal courts, "State Supreme/Appellate/Trial Court" + state). Used to
  confirm that the decision below we find is from that court, and to split federal vs state.
- `lcDisposition` — how the court below disposed of the case it reviewed. Kept in `key.tsv` for information; it is
  NOT used for any class or metric.
- `caseOrigin`, `caseName`, `docket`, `term`, `decisionType`, `jurisdiction` — extracted (`work/scdb.tsv`) for reading;
  `caseName` is used for the party-name check of the link.

## What is NOT used: `precedentAlteration` (burned)

SCDB's `precedentAlteration` flag (did this decision overrule precedent) has already been used to score the model, so
it is a burned answer key. `extract.py` does not copy it (or any other column not listed above) into any work file,
and nothing in this benchmark reads it. The disposition fields are a **different variable**: they record what the
Supreme Court did to the specific decision it reviewed (same-case history), not whether it overruled an earlier,
different decision. They have never been used to tune or score the model, so they are a valid blind test.

## Independence and its limits

- The **outcome label** (`caseDisposition`) is SCDB's hand coding, independent of the model and of our corpus.
- The **link** to the decision below is not independent of the model's evidence. Our linker (`link.py`) reads the
  head matter (syllabus, "Reported below", "N F.2d M, reversed" lines, counsel) and the opening procedural history of
  our text of the Supreme Court opinion. Round 6's linker `rules/below_sc` (ROUND6.md) reads the same kinds of lines
  ("Reported below", syllabus line, procedural-history sentence, judgment line), and the round-4 reader resolves
  history targets from citations near the disposition. Where both find the same decision below, a model hit tests
  that the model read the Supreme Court's disposition and attached it, but not that it found the decision below
  independently. A miss is still informative (the model did not attach the Supreme Court's action at all).
- The linker never looks at any model output, status, history or certificate file.
- CAP metadata of our Supreme Court opinions lists "SCDB <caseId>" among the citations; the linker uses it only to
  break a tie between several Supreme Court nodes at the same U.S. Reports page.
