# ref10: questions to the lead on DESIGN10 §4 (+ D10-5 amendment); the reference continues on the stated reading

Written from DESIGN10 §4 and the D10-5 amendment only (no Lean source read). Each item: the gap, the reading the
reference implements now. Please rule where the Lean reads otherwise (the differential will show it anyway).

**Q10-1 (most important) the order's date "as printed (the runner's date forms)".** The reference has no date-form
function (no earlier rule printed dates). Reading: date(order) from decisions2 (0 or no row: no date tie); the forms
are `<month> <d>, <yyyy>` with the full lower-case month name and the day without a leading zero ("january 5,
2015"), and `<abbr> <d>, <yyyy>` with the abbreviations `jan. feb. mar. apr. may june july aug. sept. oct. nov.
dec.` ("sept. 30, 2015"); each is a plain substring test in B's normalised, lower-cased quote. Please give the exact
list of forms the runner uses (any "sep.", "5 january 2015", numeric "1/5/2015", no-comma, compact?).

**Q10-2 B's quote has no quote column.** Reading: B's quote is the text at [b_start, b_end) of a usable window of
B's own text (B's sha in decisions2; well formed, covering, hash-consistent with window_sha.tsv, as bridge quotes),
normalised (tab / CR / LF -> space, one for one) and ASCII-lower-cased. b_end <= b_start, b_end - b_start > 600
(`remand_quote_max`), or no usable covering window => `remandCue` (the quote is the cue check's input). Two usable
windows giving different text: the first in file order (as check_cert).

**Q10-3 the docket spans (D10-5).** Reading: [bd_start, bd_end) is read from B's text and [t_start, t_end) from the
target's text exactly as Q10-2 (usable window of that node's own sha); each must be non-empty and <= 200
(`remand_docket_span_max`); failing either (or compact(docket) < 4 chars / no digit / not in both compact spans) =>
`remandDocket`. compact = ASCII lower-case, keep only [0-9a-z]. "alphanumeric" = ASCII letters and digits only.

**Q10-4 order of the checks.** Court, date, docket, cue, tie; the first failure is the reason.

**Q10-5 remandCourt.** court = the raw court id of decisions2 (column 1) of B and of the target, equal; B or target
without a decisions2 row => `remandCourt` (not epochs / successors).

**Q10-6 remandDate.** Dates from decisions2 (yyyymmdd). A date of 0 for the order, B or the target, or an order
with no decisions2 row (by = -1) => `remandDate`. "+ 1,826 days" = calendar days (proleptic Gregorian); a
date that is not a calendar date (e.g. 20150231) => `remandDate`. date(target) < date(order) strict.

**Q10-7 remandCue.** "supreme court" and a `remand_cue` phrase are plain substrings of B's lower-cased quote (any
order, may overlap). Lists / limits read from cue_table.json keys `remand_court` (else "supreme court"),
`remand_cue`, `remand_quote_max` (600), `remand_docket_span_max` (200) when present, else DESIGN10's values.

**Q10-8 remandTie.** Any of: (a) a compact key of cite_index.tsv that the index maps to the order (an ambiguous key
maps to nothing; no cite_index.tsv: no key) is a substring of compact(B's quote); (b) compact(docket) is a substring
of compact(B's quote) (the D10-5 docket, whatever its length, but it passed remandDocket already); (c) a date form
(Q10-1) of date(order) is in B's lower-cased quote.

**Q10-9 loading.** A bad line (not UTF-8, != 9 fields, b_node / b_start / b_end / bd_start / bd_end / t_start /
t_end not ASCII digits) is counted (`remand_bad_rows` = the Lean's `bad_rows history_remand.tsv n`) and takes no
id. A good line whose id is no loaded history row's id: ignored, counted nowhere (no counter in §4). A later good line
for a taken id: `remand_dup_rows`. Tests in that order. `remand_lines` = ids kept (first good line of a known id).
An empty docket field is a good line (fails remandDocket).

**Q10-10 which rows are checked.** A history row with a line whose complete round-9 verdict is `ok` (after the
reference's targetLater test and the zone check) and that passes the Lean's power test (same_case_power not `no`,
D9-4 (2)) is checked: `remand_checked_rows` +1, and a failure gives the reason (`remand_failed_rows` +1; the row is
not admitted). A row the Lean writes noAuthority (the reference's `ok`, power `no`) keeps its verdict and is not
counted; by analogy with D9-13 its findings are dropped (not admitted) when its remand check fails. Several history
rows sharing an id are each checked and counted. Counters are written only when the file has a line (good or bad).

## D10-7 (§4 amendment 2) and D10-8 (§6 trialBridge): readings (04:08)

**Q10-11 (D10-7).** A line with != 12 fields, or o_start / o_end not ASCII digits, is a bad line. (c2) fails (no
separate reason; remandTie when (a) and (c) fail too) when: compact(tie) < 8 chars, compact(tie) not in compact(B
quote), o_end <= o_start, o_end - o_start > 300 (`remand_order_span_max`), no usable window of the ORDER's own text
covers the span, the normalised lower-cased span lacks "in light of", or compact(tie) is not in compact(O span).
Cue-table keys read when present: `remand_order_span_max`, `remand_order_cue` (list, default ["in light of"]),
`remand_tie_min` (default 8) - please tell me lean10's key names if different.

**Q10-12 (§6) which rows take the claim.** A `trialBridge` claim counts only on a history row of kind reversed or
vacated WITH a history_anchor.tsv line and WITHOUT a history_bridge.tsv line (a bridge line takes the row, Q8-2); on
any other row the claim is ignored (the round-9 check). Please rule if a claimed row of another kind / without an
anchor line should instead FAIL (e.g. `trialBridgeD`).

**Q10-13 (§6) order of the checks.** anchored steps 1-5 (anchorMismatch, anchorNoCue, anchorDisqualified,
anchorUnresolved, anchorPart), then step 6 = the plain check of D's main quote with the kind-cue test replaced by
trialBridgeD (so sha / window / quote failures come first, then `trialBridgeD` in the cue's place, then the
disqualifiers, then the part rule), then `trialBridgeT`, then `trialBridgeDate`; first failure is the reason; then
the round-9 tail as for every history row (targetLater, zones, power).

**Q10-14 (§6) trialBridgeD.** "a `hist` cue of the row's kind" = the kind's cue list as the plain check uses it
(`hist`: reversed -> revers / rev'd; vacated -> vacat; with a `setAside` claim on a vacated row the `set_aside` list
too); trial names / intermediate names are plain substrings of the normalised lower-cased main quote ("court of
appeal" thus also matches "court of appeals"; a quote with "district court of appeal" fails as intermediate).

**Q10-15 (§6) trialBridgeT.** T's quote [t_start, t_end) from a usable covering window of T's own text (T's sha),
non-empty, <= 600 (`tbridge_quote_max`); holds "affirm" (`tbridge_cue`, list) and no `tbridge_negative` phrase
("reversed", "reverse", "vacate", "set aside", "remand"); any failure incl. no window / no line = `trialBridgeT`.

**Q10-16 (§6) trialBridgeDate.** date(T) < date(D) <= date(T) + 1,826 calendar days and court(T) != court(D)
(decisions2 raw courts / dates; 0, missing or non-calendar dates fail).

**Q10-17 (§6) history_tbridge.tsv loading + counters.** Bad line = not UTF-8, != 3 fields, t_start / t_end not ASCII
digits (`tbridge_bad_rows` = `bad_rows history_tbridge.tsv n`); unknown id: ignored, not counted; later line for a
taken id: `tbridge_dup_rows`; `tbridge_lines` = ids kept. Written only when the file has a line. No checked / failed
counter (none in §6) - please name any lean10 adds.
