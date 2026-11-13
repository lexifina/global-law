# Round 3 item 5: implicit-overruling tier (agent `implicit`, resumed 23:03)

## State found at resume (23:03)
- Live `data/treatments.tsv`: 21 rows with reader `claude-subagent:implicit` (the round-2 rows). No round-3 implicit row installed.
- No `data/treatment_witness.tsv`. No install lock held.
- Packs: 19 general packs (830 items) and 4 priority packs (148 items). All 23 have a complete answer file
  (978 answers). No pack is unread.
- `work/round3/implicit/cert/` was built at 22:52 from the first 355 answers only: 77 rows, 69 in witness format
  (by_node = Y), 8 in the old format. Witness format is not supported this round, so these are not installable as is.
- Plan: rebuild the certificate from all 978 answers in the OLD format (by_node = W), verify, blind audit, install.

## 23:04 certificate rebuilt from all answers (work folder only)
- `implicit.py certify3` over all 23 answer files: 818 distinct item answers, 304 statements, 291 dropped because
  the (Y, X) row already exists, 9 `witness-no-standing`, 11 `y-no-power`.
- `work/round3/implicit/cert/`: 189 rows in `treatments_delta.tsv`, of which 171 are witness format (by_node = Y;
  `treatment_witness_delta.tsv` holds 171 rows) and 18 are old format. Companions: 175 `cert_text_delta`,
  175 `window_sha_delta`, 189 `treatments_items_delta`. The 22:52 build (77 rows) is kept in `cert_355/`.
- `verify.py`: 185 rows pass, 4 fail on X or Y evidence (all with W = node 6129139).
- Not done: conversion of the 171 witness rows to the old format (by_node = W), blind audit, gold coverage count.

## 23:05 STOPPED by the coordinator: item dropped for this round
- Nothing installed. Live `data/treatments.tsv` still has 21 `claude-subagent:implicit` rows (round 2).
- No `data/treatment_witness.tsv`, no `.tmp` file. This agent never took the install lock.
- No reader or audit subagent was launched in this resume.

## Next round
- Convert the witness rows to old format or add witness support to the checkers, then blind audit (>= 25 rows,
  Wilson interval) and install. Count how many of the 169 gold pairs get an atRisk row.
