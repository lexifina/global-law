# Data of US case law in Lean, version 2

Inputs, outputs and checks of `../../LegalProofs/CaseLaw2/`. What it is, the results and how to run it are in
[../../caselaw2/README.md](../../caselaw2/README.md); the table formats are in
[../../caselaw2/SCHEMA.md](../../caselaw2/SCHEMA.md); the scripts are in `../../tools/caselaw2/`. Decision ids are the
node ids of the version 1 citation graph (`tools/caselaw/graph.py`). Files ending `.gz` are gzip-compressed TSV.

## How each table was made

- [COURTS.md](COURTS.md) and [courts_validation.md](courts_validation.md): courts, epochs, successions, adoptions, the
  per-system rules, and their validation.
- [READER.md](READER.md): the treatment and same-case history reader.
- [HOLDINGS.md](HOLDINGS.md): holdings, issues, Marks rows and splits.
- [FACTORS.md](FACTORS.md): factors for the Horty check.
- [STATUTES.md](STATUTES.md): law changes and supersession by enactment.

## tables/ (the runner's inputs)

- In full: `courts2.tsv`, `succession.tsv`, `adoption.tsv`, `system_rules.tsv`, `court_alias.tsv`, `commission.tsv`,
  `court_size.tsv`, `cite_index.tsv`, `lawchanges.tsv`, `supersessions.tsv`, `factors.tsv`, `factor_vocab.tsv`,
  `factor_cases.tsv`, `marks.tsv`, `treatment_witness.tsv`, `holdings_reach.tsv`, `reader_stats.json`.
- Compressed: `treatments.tsv.gz` (35,365 rows) and `treatments_items.tsv.gz`, `history.tsv.gz` (54,940),
  `holdings.tsv.gz` (260,349), `issues.tsv.gz` (256,096), `reader_rejects.tsv.gz`.
- Samples only (first 200 rows): `decisions2.sample.tsv`, `cert_text.sample.tsv`, `window_sha.sample.tsv`.
  `row_counts.tsv` gives the rows and bytes of the full files. They are rebuilt from the case-law repositories (see the
  main README, "What is not in the repository").

## out/ (what Lean wrote, run of 12 November 2026, as of 20261112)

`status.tsv.gz` (495,891 rows: status of each decision and holding by period), `findings.tsv.gz`, `certs.tsv.gz`
(350,654 certificate results), `splits.tsv`, `status_lines.tsv`, `horty.tsv`, `summary.tsv`.

## eval/

`score_final.txt` and `results.json` (the final scores), the same after each round and for version 1, `tables/`
(precision and recall by kind, decade, system and scope), `audit_plan.md` and the two blind audits (`audits/`).

## gold/ (evaluation only)

See [gold/README.md](gold/README.md), including what is left out for licence reasons (the Supreme Court Database is
CC BY-NC: only our mapping to it is here).

## hunt/

[HUNT.md](hunt/HUNT.md): six searches for mistakes in the case law (and in our own data), `summary.json`, the result
tables (`data/`; `p1_candidates.tsv.gz` compressed) and the blind audit packets and answers (`audit/`). The quoted
passages are from court opinions.

## statutes/

Pairs of decisions and the laws that later changed the words they applied: `pairs2.tsv`, `top_pairs.tsv`,
`evidence.tsv`, `blockchanges.tsv`, `commits.tsv`, the model's reading of effective-date clauses (`llm/retro.jsonl`,
with hand corrections), calibration, validation and audits.

## Not here

The 915 MB decisions table, the quoted windows and their hashes, candidate scans, model call inputs and outputs,
caches, token-usage logs, and third-party files (see gold/README.md).

Court opinions are in the public domain; the Constitution Annotated is a work of the US government.
