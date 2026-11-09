# Scripts

The code that produced the vulnerability list: it reads the law corpora of this repository at pinned commits, never writes to
them, runs detectors over their git histories and current texts, has a language model sort the candidates, and builds the
published list. Python 3.11+, git, and `pip install duckdb pyarrow psutil` (psutil optional).

## Run it

```sh
export GLOBAL_LAW=/path/to/a/global-law/clone      # optional; without it, sync.py clones from GitHub
python ingest/sync.py                               # bare mirrors of global-law and every corpus, pins.json
python ingest/extract.py && python ingest/trailers.py
python ingest/textscan.py && python ingest/refscan.py && python ingest/refscan.py --fileact czechia-law
python ingest/headings.py
python detectors/trailer_only.py run && python detectors/rank.py run && python detectors/text_detectors.py run
python detectors/ref_detectors.py run && python detectors/placeholder_ref.py run && python detectors/late_extension.py run
python detectors/owi_de.py run && python detectors/subref_de.py run && python detectors/notes_scan.py run
python detectors/currency_scan.py run && python detectors/dup_labels.py run && python detectors/es_crossref.py run
python release/build_release.py out                 # the list, in every format
```

The model steps (`triage/`) need an OpenAI-compatible Responses API: set `LLM_BASE_URL`, `LLM_API_KEY` and `LLM_MODEL`
(`LLM_AUTH=azure` for Azure). On a shared machine set `LE_PRIORITY=idle`, `LE_WORKERS` and `LE_GREP_THREADS`.

| Folder | What it does |
|---|---|
| ingest/ | mirrors the corpora read-only; indexes every file change, every date limit, amount and reference |
| detectors/ | one script per kind of defect (see the table in [../README.md](../README.md)) |
| triage/ | model review: artefact, lawful or candidate defect; a second model argues against each survivor; case files |
| bench/ | the accuracy benchmark below, with its samples and labels |
| release/ | builds the published list and the confirmed cases |

## How accurate the detectors are

The false negatives (defects the detectors miss) start in a few core steps: finding references in a line of law, recognising
a repealed provision, and reading an end date. `bench/stage_bench.py` measures each step on lines drawn at random from every
corpus (about 40 per corpus and stage), labelled by a language model as gold. Two sets were drawn: a tuning set (seed 7), used
while improving the code, and a held-out set (seed 11), used only to score. Held-out results, original code against current:

| Step | Original: precision / recall | Current: precision / recall | Gold items |
|---|---|---|---|
| References to numbered provisions of the same act | 37% / 33% | **84% / 71%** | 1253 |
| Repeal placeholders (provision is only 'Repealed', '(weggefallen)', ...) | 92% / 63% | **89% / 77%** | 87 |
| End dates of a rule ('until 31 December 2025') | 93% / 27% | **87% / 42%** | 48 |

What changed, in short:
- **References.** Separate words were read as suffixes ('section 10 of' as `10of`, 'artículo 458 y' as `458y`). Lists and
  ranges ('arts. 3, 5 and 7', 'artikelen 297 tot en met 299') were not expanded. Number-before-unit forms ('65. člena',
  '83 üncü maddenin', '1 straipsnio'), inflections ('člana', 'άρθρου', 'artikelen') and scripts (Arabic, Thai, Chinese,
  Japanese numerals) were missing. Headings and amendment notes were counted as references, and other acts named before the
  number ('ekteskapsloven § 8', 'Art. 34 DSGVO') were not recognised as other acts.
- **Placeholders.** Long source notes after 'Repealed.' hid the marker, label lines hid '((ARTICOLO ABROGATO))', and
  Georgian, Greek, Thai and several other markers were missing; 'Repeal of ...' headings counted as repealed.
- **End dates.** Month names and 'until' words existed for seven languages; deadlines ('not later than') were mixed with
  rule end dates; Swedish 'Upphör att gälla U:2027-03-01' and US 'shall cease to be effective after' were missing.

Limits of the benchmark: the gold labels are model judgements. A hand check of 30 held-out reference labels found one wrong
(another act's section counted as the same act's) and some sub-unit references ('subsection (1)'), which the scorer
filters out; read the figures as roughly ±5 points. The languages to fix were chosen after seeing the held-out scores, but
every fix was made from tuning-set examples. End-date recall is still low: many end dates are written in ways no fixed
pattern covers, which is why the empty-period candidates also go through model review.

Recall on the 25 cases confirmed by hand against official sources: 25/25
(`bench/known_positives.py`). Most of them were found by these detectors, so this checks that changes do not lose them
rather than measuring recall.

Reproduce: `python bench/stage_bench.py score --set holdout` (current code), and with `--code DIR` for an older copy of
`refscan.py`, `textscan.py` and `placeholder_ref.py`.
