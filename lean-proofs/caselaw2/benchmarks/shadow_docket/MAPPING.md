# Mapping: Supreme Court Shadow Docket Database → expected model status

Written 2026-11-13, after reading the codebook (`work/codebook.txt`, extracted from the deposited PDF) and the
marginal counts of `action_class` × `relief` (`work/profile.txt`) and a few order texts per class, and **before** any
Shadow Docket row was joined to any model row (`status.tsv`, `history.tsv`). No agreement figure had been computed
when this file was written. Changes after first scoring, if any, are appended at the end with both results.
Model classes follow `round6/shepardized/MAPPING.md`.

## Unit

- Source item: one Supreme Court docket (`docket_number`) that has a lower-court docket number (`lower_docket`, coded
  from the 1997 term onward). All its rows (one per order action) are pooled into one outcome class (below).
- Link: the item's lower docket number(s) + the lower court (`lower_ct`) → exactly one corpus decision (rules in
  `link.py` / `LINKS.md`). Unlinked items count only in `link_rate`.
- Scored unit: one linked corpus decision (node). Several items can link to one node (co-defendants, cross-petitions,
  several petitions from one judgment); their classes are pooled per node (below).

## Source side: class of each Supreme Court docket

From the docket's rows; first matching class wins in this order.

| Class | Rows | Expected model output (decision level) | Expected kind |
|---|---|---|---|
| `NEG` sub `gvr` | any `GVR` row | `NEG_HIST` | `neg:vacated` |
| `NEG` sub `vacated` | `Vacate and Remand` with relief NA or Granted; `Vacate` or `Remand` with relief NA or Granted **and** the action text says a judgment is vacated (`judgment(s) … vacated` within one sentence, spaces ignored); otherwise these rows are ignored (stays, injunctions, motions) | `NEG_HIST` | `neg:vacated` |
| `NEG` sub `reversed` | any `Reversal` row (summary reversal; the dataset codes some summary vacaturs here too) | `NEG_HIST` | `neg:reversed` (or `neg:vacated`) |
| `PART` | any `Affirmed in Part` row | `NEG_HIST` or `UNK_HIST` | any |
| `MERITS` (not scored) | `Certiorari` relief Granted (not part of a GVR, i.e. no NEG row) or `Probable Jurisdiction`/`Jurisdiction Postponed` rows, and no `DIG`: the case went to the merits; the merits judgment is not in this dataset | – | – |
| `AMBIG` (not scored) | `Rehearings` relief Granted and nothing above | – | – |
| `CLEAN` sub `cert_denied` | `Certiorari` relief Denied and nothing above | `CLEAN` | – |
| `CLEAN` sub `cert_dismissed` | `Certiorari` relief Dismissed (Rule 39.8 etc.), `Dismiss` relief NA (appeal dismissed) and nothing above | `CLEAN` | – |
| `CLEAN` sub `dig` | `DIG` row and nothing in `NEG`/`PART` | `CLEAN` | – |
| `CLEAN` sub `affirmed` | `Affirmed` or `Lack of Quorum` (judgment affirmed under 28 U.S.C. § 2109) and nothing above | `CLEAN` | – |
| `OTHER` (not scored) | none of the above (only motions, stays, IFP, etc.) | – | – |

Model side: `NEG_HIST` (status `neg:*`, path `history`), `UNK_HIST` (`unknown:*`, path `history`), `CLEAN` =
`GOOD`, `NEG_OTHER` or `UNK_OTHER` (overruling by a different case is not what this source records).

## Pooling per linked decision (node)

- every item `NEG` → `NEG` (sub = the first item's sub);
- `NEG` and `CLEAN` items on the same node (e.g. the judgment vacated for one co-defendant, cert denied for
  another) or any `PART` → `PART`;
- only `CLEAN` items → `CLEAN`;
- `MERITS` / `AMBIG` / `OTHER` items are dropped before pooling; a node with only those is not scored.

## Metrics (fixed in advance)

- **recall** (primary): of `NEG` nodes, the share with model `NEG_HIST`. Also reported: lenient (`NEG_HIST` or
  `UNK_HIST`), by sub-class.
- **precision**: of scored nodes (`NEG`, `PART`, `CLEAN`) with model `NEG_HIST`, the share the source has `NEG`
  (strict); lenient counts `PART` as right.
- **clean**: of `CLEAN` nodes, the share with model `CLEAN`.
- **link_rate**: of items with a lower docket number and a scoreable class (`NEG`, `PART`, `CLEAN`), the share
  linked to exactly one corpus decision.
- Wilson 95% (`benchlib.metric`). Halves: `benchlib.split_half("shadow_docket", <Supreme Court docket number>)` per
  item; a node takes the half of the lexicographically smallest docket number among its items. Assigned in
  `link.py`, before any model row is read.
- As-of date: the contract default (20261112, `--asof` to change). Known consequence, stated before scoring: a
  judgment vacated by a GVR and later reinstated by the court below on remand may legitimately show not negative
  at that date; the disagreement reading counts these as a mapping artefact. A secondary figure reads each node's
  status at its own order date + 90 days (`recall_at_order`), reported in the notes, not as the primary dot.
- Cert denials are the great majority of items; all linked ones are scored (no sampling); clean is reported
  separately from recall, so its n does not dilute recall.

## Known asymmetries (stated before scoring)

- The model learns of a Supreme Court order only from an order or opinion text in the corpus. The corpus has
  Supreme Court orders for 1993–2005 and 2010–2020 (about 7–9 thousand texts a year) but very few for 2006–2009
  and after 2020: misses there are expected. `link.py` records whether the order's own docket number is found in the
  corpus (`sc_in_corpus`), a diagnostic only.
- The model's round 6 memo linker connects orders to decisions by "Reported below" citation or by caption + court +
  30–600-day window. This key links by **lower-court docket number**, which the model does not use, so the link is
  independent of the model's evidence; but the event (the order) is the same text the model reads when it is in the
  corpus.

## Changes after first scoring

None yet.
