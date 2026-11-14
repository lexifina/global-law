# ref11: readings of DESIGN11 the reference implements (lead: answer or overrule; ref11 continues on these)

## §5.1 claim `anchorTribunal` (D11-4)

- Q11-1 (claim value). `anchorTribunal` joins the accepted values of `history_claim.tsv` (as `anchorWide`). Loading is
  unchanged: a bad line (not UTF-8, not 3 fields, an unknown value) -> `hclaim_bad_rows`; an id of no history row ->
  `hclaim_unknown_ids` (this is the "claim on a non-history row": no other effect); a repeated (id, claim) ->
  `hclaim_duplicates`. Note: under round 10 such a line was a bad line (unknown value); "by presence" therefore
  means "no line with this value", as for every earlier claim.
- Q11-2 (list). `anchor_tribunal` read from `cue_table.json` first (key `anchor_tribunal`), else DESIGN11's six
  strings. Check 2 with the claim: any string of `anchor` ++ `anchor_wide` ++ `anchor_wide9` ++ `anchor_tribunal`
  is a substring of ascii_lower(norm_quote(anchor quote)) (the same normalisation as today). With both claims: the
  same union. With neither: `anchor` only.
- Q11-3 (other anchored rows). The claim applies wherever the anchored check runs on that history row, including a
  `trialBridge` row (round 10 §6: its anchored check 2 is the shared anchor-cue test); it never touches the
  disposition quote's cue test, the bridge check, the remand check or check 3-6.
- Q11-4 (counters). Written only when some kept claim line has `anchorTribunal` (as `hclaim_anchorwide_unused`), so
  every earlier summary is unchanged:
  `hclaim_anchortribunal` = history ids carrying the claim (kept lines);
  `hclaim_anchortribunal_unused` = of those, ids whose row is not checked by the anchored check: no anchor line, or a
  bridge line (the bridge takes the row, Q8-2) — exactly the `hclaim_anchorwide_unused` definition. Neither depends
  on power, date order or the verdict.

## §5.2 identity-tie table `history_identity.tsv` (D11-5)

- Q11-5 (gate). "After the row's complete round-10 verdict admits" = the verdict after targetLater, the part-zone
  check and the remand check is ok AND the Lean admits it (same-case power not `no`, as Q10-10): only then is the row
  checked and counted (identity_checked_rows / identity_failed_rows); a failure is the row's reason `identityTie`. A
  row the Lean writes noAuthority (the reference's ok) is not checked or counted, keeps its verdict, and when the
  identity check fails its findings are dropped (as Q10-10 / D9-13). targetLater and every rejection: untouched.
- Q11-6 (loading). Lines as every table (LF; trailing CR dropped; BOM on line 1; blank lines skipped). Order: a bad
  line (not UTF-8, != 7 fields, form not exactly `docket` / `cite` / `date`, any of the four offsets not ASCII
  digits) -> identity_bad_rows (the Lean's `bad_rows history_identity.tsv n`), no id; then an id of no history row:
  ignored ("unknown ids counted": no summary key is named in §5.2, so the reference counts them internally and writes
  nothing; if the Lean writes one, tell me its name); then a later good line for a taken id -> identity_dup_rows
  (first wins). The token field is free text (may be empty: then docket / cite fail the >= 4 test).
- Q11-7 (date token). "token is yyyymmdd" = exactly eight ASCII digits whose value equals the raw decisions2 date of
  T (a non-zero value); anything else fails identityTie (not a bad line). The date forms are exactly round 10's
  (`remand_months` / `remand_months_abbr`, day without a leading zero); a non-calendar date has no form and fails.
- Q11-8 (spans). D = the row's `by` (by = -1 fails), T = the row's target; each span read from the first usable
  window (well formed, covering, hash-consistent with window_sha.tsv when present) of that node's decisions2 sha;
  e - s in characters, 0 < e - s <= identity_span_max (JSON key `identity_span_max`, else 200); norm (tab / CR / LF
  -> space) then ASCII lower-case; compact = ASCII lower-case, keep [0-9a-z] only (the round-10 compact).
- Q11-9 (cite). `cite` is tested exactly as `docket` (no citation-index lookup).
- Q11-10 (counters). Written only when the file has a line (any non-blank line, bad ones included), so a file with
  no line gives round 10's summary: identity_lines (ids kept), identity_checked_rows, identity_failed_rows,
  identity_dup_rows, identity_bad_rows.
