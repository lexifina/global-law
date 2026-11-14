# Triage brief: lists a later law forgot to update

A script (`tools/hunt/stale_lists.py`) compared every public law since 2018 against the current Internal Revenue Code
and listed each place where a law added a new subdivision N beside older siblings while some older provision R, which
names those siblings, was left untouched and does not name N. Example already confirmed by hand: the 2025 Act added
§23(a)(4) (a $5,000 refundable adoption amount) and updated the inflation list in §23(h) to name it, but left §23(i),
which lets Treasury treat unmarried co-adopters as one taxpayer "for purposes of applying the dollar amounts in
subsections (a)(3) and (b)(1)", so two unmarried adopters each get the $5,000.

Most entries are noise. Your job is to find the few that matter. You have one chunk file (named in your task).

Rules: work only in `~\Documents\global-law-lean\lean-proofs`; write only
`tools/hunt/out/stale/triage<K>.md` and `triage<K>.json`. Read statute text with
`python -I tools/hunt/sec.py <section> [subdivisions…]` (current text through Pub. L. 119-138). Earlier text and what
each law changed: `git -C ~/Documents/usc-history/clone log --format="%h %ad %s" --date=short -- title-26/<section>.md`
and `git -C ~/Documents/usc-history/clone show <commit> -- title-26/<section>.md` (read-only; no other git commands).
No web searches, no subagents, no Lean. Do not touch any other file.

For every entry decide, reading both provisions in full:
- `noise`: R is not a list of N's kind (it names the siblings for an unrelated reason), or N is covered anyway
  (a range, a general phrase, the parent), or the script mis-read a renumbering.
- `intended`: the omission is plainly deliberate or harmless.
- `gap`: the omission changes an outcome. Then say exactly: what the outcome is with N read into the list and
  without; who gains (taxpayer or government); what a taxpayer would do to use it, or how it bites them; a concrete
  dollar example worked from the statute's own figures (tax in dollars, not scores; value carryforwards; compare with
  the best ordinary alternative, not the worst); what in the statute could still cover it (a general anti-abuse
  rule, a regulation power wide enough, a definition elsewhere); your confidence that the words really leave N out.

Be hard on yourself: a gap that survives your own attack is worth far more than ten that do not. Prefer gaps where
the same law updated a PARTNER list, and gaps a taxpayer can act on. Also report anything else you notice while
reading (a sibling provision missing a rule its siblings have, such as an age limit, a joint-return requirement, an
aggregation rule or an inflation adjustment).

Deliver `triage<K>.json`: `{"chunk":K,"counts":{"noise":…,"intended":…,"gap":…},"gaps":[{"entry":"#K.n","new":…,
"list":…,"effect":…,"who_gains":"taxpayer|government","example":…,"dollars":…,"could_cover":…,"confidence":"high|
medium|low"}],"other":[…]}` and `triage<K>.md` with the reasoning for each gap. Reply in at most 250 words: the gaps,
strongest first, two lines each, then the counts.
