# MAPPING — state overruled tables (written 2026-11-13, before any model row was joined)

## Source classes

Each table row says a treated decision X was treated by a later decision Y. The table's wording is kept:

| Table wording | class | Key |
|---|---|---|
| "Overruled", "Overruled in", "Declared overruled", "overruling" | `overruled` | **primary** |
| "Overruled in part", "Partly overruled", "overruled on this point", "so far as", "to the extent" | `overruled_partial` | **primary** (partial = 1) |
| "Practically / virtually / in effect / considered / impliedly overruled", "Not overruled" | `overruled_qualified` | secondary |
| Denied, doubted, questioned, limited / restricted, disapproved, receded from, abrogated (by a case), criticised | own class | secondary (`secondary_pairs.tsv`, not scored) |

Statute / code changes ("Changed by §…", "abrogated by the statute") are not rows.

## Scoring unit

One **case** = one linked overruled decision X (primary class) with the set Y(X) of linked overruling decisions that any
table names for it. A pair (X, Y) is kept only if both citations resolve to exactly one corpus decision (LINK rules in
`REPORT.md`/`link_report.tsv`), Y is dated after X, Y is in the same state system as X (a California court
"overruling" a Pennsylvania case is a refusal to follow, not an overruling; Ga. Supreme Court over Ga. Court of Appeals
counts as the same system), and Y is dated before the table's publication year ends. Several tables naming the same
pair give one pair with all provenance (table, leaf).

## What the model should show (expected model output for a primary case)

The overruled decision X is negative or unknown by a non-same-case path with the overruling decision as actor:

- **hit (`recall`)**: some row of `status.tsv` for X (decision level or issue/holding level, any interval) with
  status `neg:*` or `unknown:*`, `path` ≠ `history`, and `actor` ∈ Y(X) — i.e. model class NEG_OTHER / UNK_OTHER with
  the right actor; **or** an admitted (`certs.tsv` ok) row of `treatments.tsv` with `by_node` ∈ Y(X), `target_node` = X and
  kind ∈ {overruled, abrogated, disapproved, recededFrom}.
  Partial rows ("overruled in part") count the same way: NEG or UNK are both right, because the model represents a
  partial overruling as an issue-level negative or an unknown-scope status.
- **`recall_any`** (lenient): X has any such status row (non-history neg/unknown) by **any** actor, or any admitted
  treatments row of those kinds by any decision.
- A `history`-path status (same-case reversal, vacatur) is not an overruling and does not count for either metric.
  Concretely "non-history" means `path` ∈ {`treatment`, `prospective`}; a `supersession` path (statute) is not an
  overruling by a case and does not count either (its actor is a law change, never Y).
- `atRisk`/findings rows and treatments rows that Lean did not admit do not count (reported as diagnostics only).

## Precision

Precision as in the same-case keys (of model negatives, share the source calls negative) cannot be computed: the
tables list only positives, and a decision absent from a table is not shown clean (the tables are selective, stop at
their publication date, and a decision may have been overruled later). We report instead:

- **`actor_agreement`**: of the listed overruled decisions X that the model marks overruled (non-history neg/unknown
  status, or admitted overruling-kind treatment) by an actor dated **before the end of the publication year of the
  latest table listing X**, the share whose actor (any such actor) is in Y(X). It asks: when the model says this
  listed decision was overruled within the table's period, does it name the same overruling case as the table?
  A disagreement here is "model names another overruler", not necessarily a model error (the tables list only the
  cases their compilers saw).
- No `precision` metric is written.

## Other metrics

- `link_rate`: of primary table rows (one per (treated, treating) citation pair as extracted), rows whose both sides
  link and pass the pair checks above.
- No `clean` metric (no source-clean decisions).

## Split

`benchlib.split_half("state_overruled_tables", key)` with key = the reader citation key (`r6cite.keys(c)[0]`) of the
first citation of X as the corpus carries it (`nodes.tsv` column 6). Fixed before any miss was looked at.

## Results JSON

`tests = "overruling"`, `court = "state"`, `blind = true`, `primary = "recall"`, metrics `recall`, `recall_any`,
`actor_agreement`, `link_rate`; splits h0, h1, all.
