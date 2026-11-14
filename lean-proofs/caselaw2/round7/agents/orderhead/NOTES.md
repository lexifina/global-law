# Round 7, A1 (iii): head-matter-only Supreme Court orders -> `orderHead` history rows

Done by the `infra` agent, 13 Nov 2026 (23:05–23:20 by `date`). No answer-key file read.

## Files

| file | what |
|---|---|
| `build_orderhead.py` | candidates -> `rows.jsonl`, `refused.tsv`, `counts.json` (rerun: `python -X utf8 round7/agents/orderhead/build_orderhead.py`, ~45 s) |
| `rows.jsonl` | 119 round-7 history rows (DESIGN7 §4 form; `"claim": "orderHead"`, `"rule": "orderHead:<memo rule>"`) |
| `refused.tsv` | every candidate not turned into a row: memo rows.jsonl line, reason, rule, by, target, kind, detail |
| `cert/` | `round7/certify7.py --rows rows.jsonl --out cert`: 119 admitted, 0 rejected |
| `what_if/` | the same run with three extra `order_line` phrases (see "Lead decision" below); NOT for staging |
| stage `round7/stage/orderhead` | base + `cert/` (history +119, history_claim +119, windows +119) |

## Candidates

`round6/history/rules/memo/cert/rejects.tsv` (the v2 rows that were staged in final2) has **9,812** rows rejected
`partNotMajority`, all with part `headmatter` (the brief's "about 11,065" was the v1 count). By kind: certDenied
9,375, reviewGranted 186, vacated 125, reviewDismissed 124, affirmed 2.

## Conditions and refusals (first failing condition counts)

| condition | refused |
|---|---|
| rule installed by the lead in round 6 (memo:cite / cap-2t / cap-2g; final2 leaves out cap-1s and cap-2t-anycourt) | 1,484 (cap-1s 1,481, cap-2t-anycourt 3) |
| kind certDenied / vacated / reversed / affirmed / reviewDismissed | 160 (reviewGranted) |
| acting court = Supreme Court (courts2 2906, base decisions2) | 0 |
| date of the acting decision >= 20130101 (`order_head_from`) | 1 (a 2012 order) |
| `order_line` phrase of the kind in the quote (cue table as the `lean` agent wrote it, 23:0x) | **8,048** |
| quote <= 400 characters (`order_head_max_len`) | 0 |
| no opinion-of-the-court part (majority / perCuriam / plurality) in the decision: round-6 cache zone `z.parts` (all 9,802 acting decisions have a zone record) | 0 |

**Rows: 119** — vacated 110, certDenied 4, reviewDismissed 4, affirmed 1. certify7: 119 admitted (no base
skip, no conflict, no conflictBase).

## Lead decision needed: the CAP order-list form is not in `order_line`

7,957 of the 7,961 certDenied candidates that pass every other condition are refused only because their quote is the
CAP head-matter form **"Petition for writ of certiorari to the <court below> denied."** — the court's name sits
between "certiorari" and "denied", so no phrase of the current `order_line.certDenied` list ("certiorari denied",
"petition for writ of certiorari denied", …) is a substring. Same for 91 reviewDismissed ("Motion … denied, and
petition for writ of certiorari to the <court> dismissed"). Top forms: `counts.json` → `orderLine_refusals_top_forms`.

What-if (`what_if/`, `what_if/extra_order_line.json`): adding "petition for writ of certiorari to the", "petition for
a writ of certiorari to the", "petitions for writs of certiorari to the" to `order_line` for certDenied and
reviewDismissed gives **8,166 rows** (certDenied 7,960, vacated 110, reviewDismissed 95, affirmed 1); one form is
still refused ("petition of writ of certiorari to the …", OCR). The kind's own cue ("denied" / "dismiss") is still
required by the plain cue test, and the memo linker already ignores denials of motions. Only the `lean` agent may
change the cue table (DESIGN7 §0.7); `rows.jsonl` / `cert/` are built from the table as it is now, and certify7
refuses the what-if rows (`orderHeadNotAllowed`) until the table changes. After a change: rerun
`build_orderhead.py` and certify7 (no other step).

Also for the lead: the round-6 guard (`rules/guard`) never saw these rows (they were rejected before it ran); run
it over `cert/history_delta.tsv` before installing, and they need the blind audit (DESIGN7 §7; the linker's
"no opinion part" statement is part of what the auditor checks).

## B4 (f): Supreme Court orders without a unique match to a lower-court decision

Source: the memo linker's own statistics, `round6/history/rules/memo/stats.json` → `by_kind` (counted per order by
`link.py stage_link`).

Definition. An **order** is a Supreme Court decision that the memo linker parses as a short order (whole text in
the cache zone, body < 4,000 characters, or front matter "memorandum order") with a disposition of kind certDenied,
vacated, reversed, affirmed, reviewDismissed or reviewGranted: **305,237** orders (a further 66,151 Supreme Court
decisions are not orders in this sense: 40,875 short texts with no disposition found, 24,947 not short, 329 no order
core). An order **has a unique match** when the linker links at least one of its captions to exactly one
lower-court decision (by a "Reported below" citation, or by caption in the 30–600-day window with exactly one
candidate), under any of its rules (including cap-1s / anycourt, which final2 does not install).

**204,371 of 305,237 orders (67.0%) have no unique match.** Why (the linker's first reason per order):

| reason | orders |
|---|---|
| no candidate decision in the corpus (court below and window, no shared caption token) | 114,234 |
| ambiguous: several decisions match | 58,377 |
| refused by the strict 2g rules | 16,583 |
| no court named in the order | 10,476 |
| a link found but its evidence not within 400 characters of the disposition | 2,911 |
| other (no caption usable, caption/court mismatch) | 1,790 |

By kind (orders / no unique match / share): certDenied 278,523 / 187,663 / 67.4%; reviewDismissed 10,961 / 8,270 /
75.4%; reviewGranted 9,662 / 4,238 / 43.9%; vacated 4,053 / 2,502 / 61.7%; affirmed 1,350 / 1,164 / 86.2%; reversed
688 / 534 / 77.6%. The two status-changing kinds together (vacated + reversed): 3,036 of 4,741 (64.0%).
