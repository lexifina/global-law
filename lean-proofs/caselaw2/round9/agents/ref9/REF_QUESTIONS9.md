# Round 9, agent ref9: readings of DESIGN9 where the text leaves a choice open (Q9-n)

Each item: the question, the reading the reference implements meanwhile, and its effect. The lead answers when a
reading changes an effect. Written from DESIGN9 §4 only (no Lean source, no LEAN9.md).

## §4 part zones

- **Q9-1 Which node is "the acting node"?** Reading: the row's `by` column, for both tables (treatments: the treating
  decision; history: the acting decision). The zones looked up are always `by`'s, whatever text the main quote is
  from. Two kinds of row quote another text: (a) a treatments row with a `treatment_witness.tsv` line (its quote is
  from W's text), (b) a history row whose certificate is the target's own text (`text_sha` = the target's sha). Under
  this reading such a row is checked against `by`'s zones although its offsets are in another text's offset space.
  Alternative the lead may prefer: the node whose text the main quote is from (W for (a), the target for (b)), or not
  zone-checking (a)/(b) at all. **Please rule** (it matters on real data if `calpart9` builds zones for nodes that are
  both an acting node and a witness / own-text owner).
- **Q9-2 Where in the verdict order does `partZone` come?** Reading: after the complete round-8 verdict. Only a row
  whose round-8 verdict is `ok` (after `badRow`, the history `targetLater` test, the doctrine-ambiguity pass) is
  zone-checked; any other round-8 verdict is kept ("the first failure keeps its round-8 reason"). `targetLater` is a
  round-8 reason and is kept. The reference decides power in the status layer, so a row the Lean writes as
  `noAuthority` and the reference as `ok` -> `partZone` would show as an okMismatch in certs (no status effect either
  way); we will see in the differential which order the Lean took.
- **Q9-3 Doctrine ambiguity.** Reading: the ambiguity pass counts rows passing the round-8 check (zones not
  consulted), then the zone check runs on the rows still `ok`. A zone failure therefore never removes an ambiguity.
- **Q9-4 Recognised rows (witness rows with a `recognised` claim).** Reading (follows Q9-1): a witness row whose
  zone check fails (under `by`'s zones) is neither admitted nor recognised; its verdict is `partZone` if its round-4
  verdict was `ok`, else that round-4 reason.
- **Q9-5 The plain check of an operativeWords row** (kept for `laterCourtSays:` supersessions). Reading: zone-checked
  too (`ok` -> `partZone` on failure); it is the row's own check of the same main quote.
- **Q9-6 Lines that do not parse.** Reading: a line that is not valid UTF-8, has not exactly 5 fields, or whose node /
  z_start / z_end is not ASCII digits is a bad line: ignored, counted (`zone_bad_rows` = a Lean `bad_rows
  part_zone.tsv n`), and it does NOT poison its node. A parsed line with `z_start >= z_end` or a part outside the
  seven names (case-sensitive) poisons its node (all of that node's zones dropped, `zone_bad_nodes` +1 per node).
  The `src` column is free text (may be empty).
- **Q9-7 Overlap.** Two zones [a, b), [c, d) of one node overlap when a < d and c < b (touching zones, b = c, do
  not). Two identical lines overlap. Overlap is tested over the node's parsed lines with no malformed one (a node
  already poisoned counts once).
- **Q9-8 Joined quotes.** Each kept joined line of a treatments row is zone-checked with its `j_part` (only a row
  that passed the round-8 check, so the lines are well formed). Anchor (`history_anchor.tsv`) and bridge
  (`history_bridge.tsv`) quotes are not zone-checked; the main quote of such a row is.
- **Q9-9 `zone_missing_rows`.** Reading: the number of treatments + history rows that reach the zone check (round-8
  verdict `ok`) and whose acting node has no zone (none given, or dropped as bad). Written with the other zone
  counters only when `part_zone.tsv` has a line. Other counters the reference writes then: `zone_nodes` (nodes with
  kept zones), `zone_lines` (kept zone lines), `zone_bad_nodes`, `zone_bad_rows`, `zone_checked_rows` (rows checked
  against zones), `zone_failed_rows` (rows failed `partZone`).
- **Q9-10 Unknown nodes** (no decisions2 row) keep their zones (harmless: no row acts from them, or a row from them
  is `badRow`). A row with `by` = -1 has no zone (missing).

## Lead ruling D9-4 (02:15) and what the reference does since 02:23

- Q9-1 replaced by D9-4 (1): the zones are the **text owner's**: `by` for a treatments row, W for a row with a
  `treatment_witness.tsv` line, the target for a history row whose certificate is the target's own text. Reference
  test for "own text": `sha(target) == text_sha` (the plain check's own_text test; when sha(by) = sha(target) the
  target is taken).
- Q9-2..Q9-10 as read (D9-4 (2)-(4)).
- **Q9-11 (new; D9-4 (2) "after ... the power check").** The reference decides date order and power in the status
  layer; the Lean writes `targetLater` / `noAuthority` in certs.tsv and (D9-4 (2)) does not zone-check such a row.
  So the reference skips the zone check (and the zone counters) for a row the Lean writes that way. The predicate
  was measured on stored round-8 universes (`powercheck.py`; 9,9xx rows): a treatments row is `targetLater` when
  date(by) < date(target) with both known (a witness row: date(Y) < date(X), as check_witness), `noAuthority` when
  its kind changes status (NEG_TREAT) and can_change(by, target, scope domain) is no (no power test for a kind that
  does not change status); a history row is `noAuthority` when same_case_power(by, target, claims) is no. The only
  rows this misses are the known round-5 witness-class W rows (1 of 107 witness rows). A recognised row (round-8
  verdict okRecognised*) is zone-checked; failing, it is `partZone` and not recognised (D9-4 (3)). The plain check
  of an operativeWords row is zone-checked under the same gate and not counted.

## §5 joinedFar and §7 implicitReject (D9-5; implemented 02:30-02:33)

- **Q9-12 Order of the far tests.** For an `antecedent` line of a row with the claim `joinedFar`: `j_end > start` ->
  joinedRelation (unchanged); gap = start - j_end <= 300: the round-8 relation; else, in this order: gap > joined_far_max
  -> joinedFarGap; no usable window (well formed, covering [j_end, start), hash-consistent; the row's own text_sha;
  the first such window in cert_text order is used) -> joinedFarWindow; newline -> joinedFarPara; other key ->
  joinedFarKey; then the §2.2 anaphor and kind-cue tests (joinedRelation). Without the claim a gap > 300 is
  joinedRelation as before. Two lines: in file order, the first failure is the reason (as round 7).
- **Q9-13 "newline" (please rule; it may make joinedFarPara vacuous).** The reference tests for LF (`\n`) in the
  window text [j_end, start). A window is one TSV field of `cert_text.tsv`, so it can never hold a LF, and the corpus
  windows are normalised (r6lib.norm: tab / newline -> space; v8e's cert_text has none). So on any data the
  paragraph test can only fail if paragraph breaks are carried some other way. A CR (`\r`, data inside a line) is not
  a newline in this reading (probe `pr_far_cr`: admitted). If the paragraph test is meant to bite, the window text
  needs a paragraph mark that survives the TSV (e.g. keep `\n` as a distinct code such as U+2029 or the text's own
  paragraph offsets in another table).
- **Q9-14 "an index key starts in [j_end, start)".** Reading: compact the window's text from j_end to the window's
  end (ASCII lower, letters and digits), keep each compact character's offset; a key starting at a compact position
  whose offset is in [j_end, start) counts, even when it runs past `start` into the main quote (probe
  `pr_far_key_straddle`: joinedFarKey). A key mapped to the row's target is allowed; an ambiguous key is no key
  (D8-15); without cite_index.tsv there is no key. Every key length is tried at every position (not only the
  longest).
- **Q9-15** joinedFar on a witness row: its joined lines are ignored at load (D7-6 (1)), so the claim changes nothing.
  A row has one class line, so joinedFar never combines with operativeWords / doctrine / implicitReject.
- **Q9-16 Which kinds are "soft" for implicitReject (please confirm).** Reading: the reference's soft kinds, the ones
  whose rows give `atRisk soft:<kind>` findings: limited, questioned, criticized, declinedToFollow (DESIGN9 lists two
  of them as examples; `implicitReject_soft` says an admitted claimed row has a softNegative kind). A claimed row of
  any other kind fails `implicitBadKind` (status-changing kinds as the design says; also followed, distinguished,
  supersededByEnactment, so that `implicitReject_soft` holds). Probes `pr_imp_limited` / `pr_imp_criticized`
  (admitted), `pr_imp_followed` / `pr_imp_superseded` / `pr_imp_distinguished` (implicitBadKind).
- **Q9-17** The extended cue list is the row's own cue test (the plain check, and step 6 of checkJoined for a row with
  joined lines); the §2.2 antecedent relation keeps "a cue of the row's kind (the plain list)". Probe
  `pr_imp_joined_implicit` (anaphor + implicit cue only, with a joined line): joinedRelation.
- **Q9-18** implicitBadKind is tested before the witness path: the claim on a witness row (always a status-changing
  kind) fails implicitBadKind (probe `pr_imp_witness`).

## D9-7 / D9-9 (02:33, 02:37)

- Q9-13 is moot: D9-7 dropped the paragraph test (joinedFarPara is no longer produced by the reference; the label stays
  in labels.json, harmless).
- **Q9-19 (§8 judge strings).** The reference uses, under `anchorWide`, `anchor ++ anchor_wide ++ anchor_wide9`, where
  `anchor_wide9` is read from cue_table.json, else DESIGN9's three strings. If the Lean instead puts the three into
  `anchor_wide` and writes no `anchor_wide9`, the reference adds them twice (no effect).
