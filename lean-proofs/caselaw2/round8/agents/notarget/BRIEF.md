# Agent `notarget` (round 8): explicit own-act sentences whose target the reader could not resolve

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/notarget/` (NOTES.md).
Timebox: 50 minutes from start to final report (the round freezes soon after); deliver what clears the audit.

## Source
Agent `state8` (`round8/agents/state8/NOTES.md`, its scan outputs) repaired five reader rules and rescued 45,841
corpus sentences; 41,889 of them were left out as `no-target` (the reader found an own-act overruling sentence but
resolved no target: the case is named earlier in the paragraph, by a short name, by "the X case", or by a citation
form the reader does not key). Round 7's antecedent class (`round7/agents/antecedent/`, joined `antecedent` lines,
≤ 300 characters before the act with an anaphor) and round 8's `multicase` (`round8/agents/multicase/`) and `ownact`
(`round8/agents/ownact/`) cover parts of this; drop items whose (acting, any candidate target) pair already has an
admitted row in v3 or in those agents' `cert/` folders.

## Do
1. Profile the 41,889 (court, decade, act verb, what precedes the act) and estimate yield on a random 100 read by
   yourself or 2 opus readers. Pick the subclass(es) with the best yield whose target can be resolved by a general
   rule the Lean certificate can check (plain: the target evidence in the main quote; joined `antecedent`: in the
   sentence before, ≤ 300 chars, anaphor in the act sentence — DESIGN7 §2.2; "the X case" short names: `name:` tokens
   must be whole words of the quote and unique in the acting decision's citation list).
2. Read the chosen subclass with opus reader sub-agents (brief in your folder; one answer per target), certify8 into
   `cert/`, blind audit ≥ 80 (decoys) via `round8/audit/HOWTO.md`, measure (stage `notarget_v1`, NOBUILD run,
   score8). Install bar ≈ 90%.

Final report: profile, subclass chosen, rows, audit, delta folder, effect, what is left.
