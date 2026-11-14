# Inventory of the queued reading for recognised overrulings (B1), 13 Nov 2026 22:59

Agent `queue`. Source of every figure: `inventory.json` and `dropped_stats.json` (written by `build_queue.py` and
`build_dropped.py`), per pack in `inventory_packs.tsv` (282 packs). "Main model" = answers in `round5/recog/ans/`;
"pre-screen" = `round5/recog/ans_prescreen/` (the smaller model). Counts are distinct item ids.

## 1. Round-5 packs (`round5/recog/packs/`, `packs_unused/`)

| dir / tier | packs | items | read by the main model | pre-screen only | never read | note |
|---|---|---|---|---|---|---|
| packs T0 | 4 | 179 | 179 | 0 | 0 | round-4 witness rows re-read |
| packs T1 | 2 | 52 | 52 | 0 | 0 | feed notes, X = Supreme Court |
| packs T1s 001-012 (strict) | 12 | 528 | 528 | 0 | 0 | own scan of Supreme Court opinions |
| packs T1s 013, 029, 045, 061 (loose sample) | 4 | 200 | 200 | 0 | 0 | |
| packs T1s 014-076 (loose, other 60 packs) | 60 | 2,999 | 64 (via T1v) | 2,283 (via T1f) | 652 | never read as packs: their items were re-cut into T1f; the 652 were proved uncertifiable (`T1f_dropped.tsv`: 641 a disqualifier in every span, 9 crosses parts, 2 X/Y not in window) |
| packs T1f | 47 | 2,347 | 64 | 2,283 | 0 | the same items as above |
| packs T1v | 2 | 64 | 64 | 0 | 0 | the 64 pre-screen positives, re-read: 62 true |
| packs T2 (scope all / partial) | 37 | 1,807 | 1,807 | 0 | 0 | |
| packs_unused T2 (first build, no INTRO) | 114 | 5,700 | 7 | 0 | 5,693 | 5,693 are other-grounds notes: 4,617 certified by pattern, 1,076 not |

T1f pre-screen: all 2,347 pre-screened; 64 said true, all 64 re-read by the main model (62 true); **2,283 said false
and were never read by the main model**. Main-model answers in all: 2,830 distinct items (T0 179, T1 52, T1s 792,
T2 1,807); states true 1,904. (LOG.md says 2,838 for it1 and PROGRESS.md 2,902 with T1v: they counted 8 more answer
lines than there are distinct ids.)

## 2. The 89,542 feed statements

| step | statements | what happened |
|---|---|---|
| feed statements | 89,542 | |
| not (precedent, Y named, overruled / abrogated / disapproved / recededFrom) | 61,480 | not B1 (history kinds, Y not named) |
| W without power over X | 13,584 | cannot be recognised (12,715 panel under a strong horizontal rule, 678 Florida sister district, 145 trial court, 46 bench unknown) |
| Y shown to lack power, dates, same node | 192 | cannot pass |
| **after power and dates** | **14,286** | |
| note in a dissent / concurrence / head matter | 1,547 | cannot pass (part check) |
| repeat of the same (W, X, Y, scope group) in one W | 273 | same statement; the first position is kept |
| **dropped by the cut "3 earliest W per (Y, X, scope group)"** | **1,899** | **queued (CUT)**: other grounds 1,829, all 18, partial 52; tiers T2 1,847, T3 52; 513 pairs |
| candidates (reproduced exactly, 0 / 0 difference) | 10,567 | |
| T1 | 52 | read |
| T2 scope all / partial | 1,807 | read |
| T2 other grounds | 8,197 | 6,671 certified by pattern (4,685 rows staged, 1,986 spare); **1,526 not certified: queued (OG)** (1,409 no strict match: 1,050 no strict phrase, 108 X's citation too far, 101 another decision between, 91 sentence/semicolon, 39 ";" before Y, 17 history word, 2 case name, 1 too long; 117 refused by the certifier: 99 disqualifier, 18 inside a quotation) |
| T3 (pair explicit-all-ok in the round-4 model) | 511 | **queued (T3)** |

Reconciliation: of the 12,466 distinct statements that can pass, 1,859 were read by the main model (T2 1,807 + T1
52; the "1,807" of the request is the T2 part), 6,671 were certified by pattern (the "4,685 pattern rows" are the
staged earliest W per pair), and **3,936 are queued now** (1,899 + 1,526 + 511). 1,859 + 6,671 + 3,936 = 12,466.

## 3. "246 unread packs"

The figure is from `round4/queue.md` ("246 unread packs (incl. 142)"): the round-3 **own-act** queue
`work/round3/queue/packs/` (398 packs, 152 answered; `pack_142.txt` half answered, 59 of 80, `ans_142.partial`;
unread `pack_142` to `pack_397`, 20,443 items). That queue asks whether the deciding court itself overrules a
candidate (explicit class, `READER_BRIEF2.md`, `certify2.py` / `install.py`, which install into `data/`). It is not
the recognised class and its items are not in the recognised item format, so it is **not** in this queue; it needs
a round-7 port of its certifier before any reading (its brief writes answers under `work/round3/`).

Other queues, counted only: `round5/opwords` (agent `opwords`): 44 packs, all 44 answered; 2,879 items never packed
(`packs/unpacked_L.tsv`). `work/round3/implicit`: 23 packs, all answered (the source of the 179 T0 rows).
`work/round2/recall`: 16 packs, all answered. `round4/`, `round6/`, `hunt/`: no pack folders.

## 4. The queue built here (`packs/`, 131 packs, 6,219 items, 4,114 (Y, X) pairs)

Priority by pair novelty against the base build `round6/history/stage/final2` (admitted = a treatments row by Y on
X of a precedent kind whose `result_all` in `out/final2/certs.tsv` begins `ok`; 28,064 such pairs): P1 no admitted
row; P2 admitted rows, none of scope `all`; P3 an admitted scope-`all` row. Every queued W has power over X
(recomputed). Inside a priority: CUT, OG, T3, T1F; then Y's power known first; a pair's statements together.

| priority | CUT | OG | T3 | T1F | items | packs |
|---|---|---|---|---|---|---|
| P1 | 13 | 484 | 0 | 2,264 | 2,761 (2,562 pairs) | 57 |
| P2 | 1,792 | 1,014 | 0 | 5 | 2,811 | 58 |
| P3 | 94 (T2 42, T3 52) | 28 | 511 | 14 | 647 | 16 |
| all | 1,899 | 1,526 | 511 | 2,283 | **6,219** | **131** |

By item tier: T2 3,373, T1s (T1F) 2,283, T3 563. By note scope: other grounds 3,758, all 2,318, partial 143.
Y's power: known 6,188, unknown 31.

Expected value, for the lead (not used to select): P2 and P3 add little to the model. A P2 item is a later
statement about a pair that already has an admitted partial row; nearly all P2 items are "other grounds" notes
(1,792 CUT + 1,014 OG), which can only give another partial row for the same pair (the certifier stages the
earliest W, and a partial row's effect starts at date(Y) whoever says it). P1 holds the 497 typed feed notes on
novel pairs (13 CUT + 484 OG) first, then 2,264 T1F items that the smaller model judged false (round-5 yield of the
loose tier: about 3%; of these, lower). A reasonable stop is after P1.

## 5. Leak check (`leak_check.json`, `leak_check_failures.tsv`)

Every packed item: 3,936 feed-derived items have their statement id in `round5/tests/split/feed_ids.tsv` with the
same (note_node, target_node, by_node) = (W, X, Y); 2,283 T1F items come from round 5's own scan of Supreme Court
opinions (no statement id; W and X are both Supreme Court decisions). All 6,219 have `can_change(W, X) = yes` (the
reference engine as `round5/tests/check_no_leak.py` loads it). **0 failures.** The holdout file was not opened;
`check_no_leak.py` itself (which reads `holdout_ids.tsv`) is for the lead to run on the certified rows after
staging.
