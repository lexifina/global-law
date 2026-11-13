# Implicit overrulings with a witness: file format (round 3, agent `lean`)

Status: format fixed. Checker support (Lean and reference) lands later this round. Until then a witness row fails
the old checkers with `shaUnknown` (safe: the row asserts nothing).

## What it expresses

"Decision X was overruled / abrogated by decision Y", where Y does not say so itself. A later decision W says it
("X is no longer good law after Y", "X, abrogated by Y", "the overruling of X by Y"). The row names **Y** as the
by-decision. W is the witness: the quote is in W's text.

Such a row is `explicit = 0`. It never changes any status. It yields exactly one finding:
`atRisk  <X>  <Y>  -  inferredRejection` (subject X, source Y), and only while X is not already negative.

## Files

### 1. `data/treatments.tsv`: one ordinary 16-column row (unchanged layout)

| col | field | value for a witness row |
|---|---|---|
| 1 | id | unique; use `tw:<Y>:<X>:<start>:<W>` |
| 2 | by_node | **Y**, the overruling decision |
| 3 | target_node | X |
| 4 | date | Y's date (decisions2.tsv) |
| 5 | kind | a status-changing kind only: `overruled`, `abrogated`, `disapproved`, `recededFrom` |
| 6 | scope | as usual (`all`, `issues:..`, `partialUnknown`, `otherGrounds`) |
| 7 | temporal | as usual (`unknown` if not stated) |
| 8 | explicit | **0** (a witness row with 1 is rejected) |
| 9 | text_sha | **W's** text_sha (decisions2.tsv column 8 of node W), not Y's |
| 10, 11 | start, end | offsets of the quote in **W's** text |
| 12 | quote | exact substring of W's text; must contain a cue of the row's kind (same cue lists as today) |
| 13 | target_evidence | `cite:<citation>` or `name:<tokens>` naming **X**, found in the quote or its window |
| 14 | part | `majority`, `plurality` or `perCuriam` (of W) |
| 15 | reader | `claude-subagent:implicit` |
| 16 | confidence | 0-1 |

### 2. `data/treatment_witness.tsv` (new; 4 columns, no header; one row per witness row)

| col | field | value |
|---|---|---|
| 1 | treatment_id | the id of the treatments.tsv row |
| 2 | witness_node | W (a node of decisions2.tsv) |
| 3 | by_evidence | `cite:<citation>` or `name:<tokens>` naming **Y**, found in the quote or its window in W's text. A `cite:` must resolve through `cite_index.tsv` to Y. |
| 4 | src | reader id / note |

A treatments row with no line in this file is an old-format row (the by-decision states it; nothing changes for
those). The 21 existing `explicit = 0` rows stay valid as they are.

### 3. Companions, as for any certificate

- `cert_text.tsv`: `text_sha (W's), start0, end0, window` covering the quote (start-400 .. end+400, normalised).
- `window_sha.tsv`: the window's hash row, as for every other certificate.
Both X's name/citation and Y's name/citation must be inside the quote or that window.

## Checks (both checkers), in order; first failure is the reason in `certs.tsv`

1. `witnessBadRow`: witness_node unknown, or the treatments row has `explicit = 1`, or kind is not status-changing.
2. `shaUnknown`: text_sha is not W's text_sha.
3. the usual text checks on W's window: `noWindow`, `windowHash`, `quoteMismatch`, `noCue`, `disqualified`,
   `targetUnresolved` (X), `partNotMajority`.
4. `byUnresolved`: by_evidence does not resolve to Y in the quote/window.
5. `targetLater`: need date(X) <= date(Y). `witnessEarlier`: need date(Y) <= date(W). (0 = unknown passes.)
6. `witnessNoStanding`: W's court must be X's court (same court id, or a successor of X's court by rename/replace),
   or a court with power to overrule X (the same `canChangeStatus` test used for an overruling court, here W over
   X). A lower or sister court's remark is not admitted.
7. Y's power over X, as for every status-changing row: shown absent -> `noAuthority`; unknown -> `okUnverifiedBy`.

## Example

X = node 5965094 (*Fleet Corp. v. Lustgarten*, 280 U.S. 320), Y = node 5973500 (*Brady v. Roosevelt S.S. Co.*,
317 U.S. 575; illustrative id), W = node 5987930 (1949).

`treatments.tsv`:

    tw:5973500:5965094:6009:5987930	5973500	5965094	19430118	overruled	all	unknown	0	5900aaf703debf263895a8df5ee8b2912a0941b5	6009	6121	the overruling of Fleet Corporation v. Lustgarten, 280 U. S. 320, by Brady v. Roosevelt S. S. Co., 317 U. S. 575	cite:280 us 320	majority	claude-subagent:implicit	0.75

`treatment_witness.tsv`:

    tw:5973500:5965094:6009:5987930	5987930	cite:317 us 575	claude-subagent:implicit

## What agent `implicit` must supply

- The treatments row and the witness row above, plus the `cert_text.tsv` and `window_sha.tsv` rows for W's window.
- Y must be a corpus node. If Y is not in the corpus, keep the old format (by_node = W) instead.
- If W itself overrules X, it is an explicit row, not a witness row.
- Install as deltas under the install lock (BRIEF rule 12); `treatment_witness.tsv` is new, create it if absent.
