# lean11: questions for the lead (lean11 continues on the stated reading)

- Q-L11-1 (§5.2, 05:45) DESIGN11 §5.2 says "unknown ids counted" but names five counters (identity_lines,
  identity_checked_rows, identity_failed_rows, identity_dup_rows, identity_bad_rows). Reading (as round 10's remand
  table, Q10-9): a good line whose id is no history row is ignored and is in none of the five counters (only the
  loader's line count). If you want it counted, name the counter (e.g. `identity_unknown_ids`, written after
  `identity_bad_rows`) and I add it (ref11 must match).
