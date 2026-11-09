# Vulnerabilities: the full list

Every flag the detectors raised, one row per provision and issue. A flag is a candidate, not a confirmed defect: most are
corpus build errors, or lawful once read in context. The cases checked by hand against official sources are in
`confirmed.csv` / `confirmed.json`.

| File | What it holds |
|---|---|
| [confirmed.csv](confirmed.csv), [confirmed.json](confirmed.json) | Cases confirmed against official sources, with links to them |
| [by_category.csv](by_category.csv) | Flags per category, and how many a language model reviewed |
| [by_jurisdiction.csv](by_jurisdiction.csv) | Flags per jurisdiction and category |
| [reviewed.csv](reviewed.csv) | Flags a language model reviewed, with its verdict and a one-line note |
| flags.csv.gz, flags.jsonl.gz, flags.parquet | Every flag, in three formats |
| [html/index.html](html/index.html) | The same list as browsable pages, one per category (download and open in a browser) |

## Columns

| Column | Meaning |
|---|---|
| id | Stable identifier (hash of detector, corpus, provision, date, reference) |
| category, detector | The kind of defect, and the detector that found it |
| jurisdiction, corpus | Country, and the corpus path in this repository |
| path | The provision's file in the corpus repository |
| date | The date the flag turns on (end date, in-force date, removal date), where there is one |
| reference | What the provision points at, or the instrument involved |
| summary | Why it was flagged, or the line of text concerned |
| score | The detector's ranking score, 0 to 1, where it has one |
| review | A language model's verdict, where reviewed: artefact (corpus error), lawful, harmless or cured, candidate_defect |
| review_note | The model's one-line reason |
| url | The provision at the commit that was read |

The corpora were read at pinned commits and never written to.
