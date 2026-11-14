# Lean outputs of the frozen round-13 build (v13a)

Written by the compiled runner of `LegalProofs/CaseLaw2` on 14 November 2026 (`RUN.txt`: binary sha1, data
directory, which tables were staged). `diff.txt` is the comparison with the independent Python reference
(`tools/caselaw2/ref/precedent_ref.py`): 0 disagreements in every table.

| File | Rows |
|---|---|
| `status.tsv.gz` | 532,639 (status of each decision and holding by period) |
| `findings.tsv.gz` | 329,990 |
| `certs.tsv.gz` | 498,507 certificate results |
| `classes.tsv.gz` | 37,448 (round-5 treatment classes) |
| `splits.tsv`, `status_lines.tsv`, `horty.tsv`, `summary.tsv` | as in `../out/` |

Formats are in `../../../caselaw2/SCHEMA.md`, with the round-5 `oclass` column described in
`../../../caselaw2/DEVIATIONS.md`. The input tables of this build were staged from the round-12 build plus the
round-13 rows (`caselaw2/round13/ROUND13.md`). They are not in the repository: the round scripts rebuild them from
the corpus. `../out/` keeps the round-4 run that matches `../tables/`.
