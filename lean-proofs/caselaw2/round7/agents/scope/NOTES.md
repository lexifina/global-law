# agent scope (round 7, track B2): scope of an overruling from its own sentence

## Log

- 2026-11-13 23:22 GMTST start. Read DESIGN7 (0, 6), DESIGN5 3.3 + 9, SCHEMA, cue_table, stage7 --replace, make_packs7, audit7lib.
  Base treatments (round6/history/stage/final2): 41,475 rows; explicit NEG4 partialUnknown 9,840; no `unknown` scope rows.
- 23:24 scope_extract.py: sentence of every candidate from git HEAD (recog_common.git_texts), sha + quote checked: 26,778
  candidates (P 9,840, I 11,470, W 5,468), 0 errors, ~12 s with 22 procs.
- 23:25-23:39 rule written and tuned on the sentences only (no key, no notes, no scorer). Several rounds of reading the
  rows the draft rule changed and the rows it kept, fixing general causes: (1) reader/common.sentence_span split
  sentences at mid-caption periods and page-break newlines ("Ins.\nCo.", "State ex rel. | Kain v. Fischl", "Teleg. Co.")
  and so hid a "to the extent" / "whatever was said" earlier in the sentence -> own conservative finder sentence_span2
  (abbreviation lists incl. lower-case "rel", next-token-is-abbreviation, newline ends a sentence only after a sentence
  end); (2) part-of-case nouns ("language", "holding", "statement", "rule", "aspect", "division", "the X of <case>")
  partial only when attached to a case or acted on, and this court's own "holding today" masked; (3) OCR forms of
  "extent" ("exteht", "ex tent", "extend"); (4) lists introduced by the act verb ("are overruled, including X",
  ": X; Y", "[e.g., X]"); (5) "no longer good law on/for/as to ..." and "no longer the law that ..." partial.
- 23:40 final run. replace.tsv sha1 afdff37a65288a1f92269e976387575524f9f80d (56 rows).

## The rule (scope_rule.py docstring is the reference)

Rows: treatments, kind overruled / abrogated / disapproved / recededFrom.
- P (explicit, scope partialUnknown/unknown): sentence (from git text) has a LIMIT phrase or a PART_OBJECT -> partial
  (unknown -> partialUnknown; none in base). Else, target evidence resolves in the sentence, sentence bounds found, no
  HEDGE (report / condition / refusal / party), an act form (passive "X ... is overruled", active "we overrule X",
  "X is no longer good law / should no longer be followed / can no longer be accepted as stating the law") with the
  target in its object zone (or in a list the verb introduces), not merely cited as authority -> `all`. Else as is.
- I (explicit, issues:): only rows with exactly one issue on a target with exactly one holding, sentence passes (a) -> all.
- W (witness rows): never rewritten; counts only.

## Counts (counts.tsv)

P 9,840: -> all 45 | kept partial: limit 7,530, partObject 2,061 | rule silent (kept): targetNotInSentence 149,
hedge 42, noAct 5, anaphor 3, notObject 2, citedAsAuthority 2, sentenceUnbounded 0.
I 11,470: narrow (1 issue, target 1 holding) 791 = sameIssue 315 (all kept partial by a limiter) + otherIssue 476
(-> all 11, kept partial 438, silent 27). Not narrow: 2-6 issues 2,050; 1 issue on target with 0 holdings 2,578 / >1
holdings 6,049. (Sentence verdict over all I rows: partial 10,127, whole 136, silent 414.)
W 5,468 (counts only): "overruled in part / on other grounds by" phrase 4,879 (scope otherGrounds 4,472,
partialUnknown 407); plain "overruled by" 80 (otherGrounds 13, partialUnknown 67 -> kept as is); neither 509.
replace.tsv: 56 rows = overruled 33 + disapproved 11 + recededFrom 1 (from partialUnknown) + overruled 9 +
disapproved 2 (from issues:). Only column 6 differs from the base (checked).

## Own sample (sample40.tsv, seed 7, 40 of the 56 changed rows, read in full)

39/40: a present whole-case act of the court on the named target, no limiting phrase, target in the act's object
(several share a multi-case sentence). 1 uncertain: t:5481101:5479600:11688 ("The opinion of this court in the case
of Wade v. Hope & Killingsworth ... is overruled") reads whole but may be the same litigation (earlier appeal).
Risk to flag for the audit: 35 of 56 sentences carry "contrary" ("decisions to the contrary in X", "X, holding to the
contrary, are overruled"); I read these as whole (descriptive, not limiting), an auditor might not; two carry a pin
cite (611 F.2d at 743; 256 F.2d 7, 16-17).

## Audit spec (for the lead; nothing run here except --dry-run)

Only 56 rows change, so the >= 80 target cannot be met by changed rows: audit them all (census) plus a control.
  A (census, class scope):
    python -X utf8 round7/audit/make_packs7.py --class scope --cert round7/agents/scope/replace.tsv \
      --ids round7/agents/scope/replace.tsv --out round7/audit/r7scope --n 56
    (dry run: 56 rows, fed 8 / state 48 over 1920s-2010s)
  B (control on half (b), rows kept partial):
    python -X utf8 round7/audit/make_packs7.py --class scope_ctl --cert round6/history/stage/final2 \
      --ids round7/agents/scope/control_partial40.tsv --out round7/audit/r7scope_ctl --n 40 --exclude round7/audit/r7scope/sample.tsv
  Auditors judge act + extent (AUDITOR_BRIEF7). Pass for A: act overrule/own_opinion yes/extent whole; for B:
  extent part (or other_grounds). 96 real items + decoys.

## Files

scope_extract.py, scope_rule.py, sentences.jsonl.gz, decisions.tsv (every candidate, reason, sentence), counts.tsv,
replace.tsv, sample40.tsv, control_partial40.tsv, run_stdout.txt. Nothing outside this folder written; no stage, no
scoring, no commit.
