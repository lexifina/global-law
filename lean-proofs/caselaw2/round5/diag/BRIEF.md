# diag reader brief (round 5, caselaw-lean-2)

You read Supreme Court opinions and classify HOW each one "overrules" an earlier decision without using the word.
All reading is done by you, locally. No external model API (no Azure OpenAI, nothing over the network).

## Hard rules
- Work only in `~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\diag\`. Write only your one shard
  file there (named in your task). Do not edit or create anything else anywhere. No git commits.
- Off limits, never open or list: `round5\gold_fresh\sealed\`.
- Do not open `data\decisions2.tsv`, `graph\nodes.tsv`, `gold\reports_typed.tsv` or other large tables. You do not
  need them: every text you need is cached in `round5\diag\text\<node>.md`.
- No web access. Later-court statements (kind D) are handled by someone else; do not search for them.

## Input
`round5\diag\pairs.tsv` (tab-separated, header): idx, by_node (Y, the overruling decision), target_node (X, the
overruled decision, `-1` = not known), label (Y's name), target_name, target_cite, crs, r2_cause, r2_note.
One row per (Y, X) pair; a Y with several X has several rows; you answer once per row. `r2_note` is what a round-2
reader wrote: a starting point, often with a character offset (`@12345`); verify it against the text.
For rows with target `-1` the Supreme Court Database says Y altered precedent but no list names the target: read Y,
say which earlier decision (name + citation) is affected, if any, and classify on that basis.

## Tool
`python ctx.py <Y node> -x "<regex>" [-c N] [-m MAX] [-l CHARS] [-a]` prints the sentences of Y that match the regex
(X's party names, e.g. `-x "Wolf"`), with the character offset and the part label (`majority`, `perCuriam`,
`dissent`, `concurrence`, `headmatter` = syllabus / counsel argument; a trailing `~` is an inferred label). By default
only the opinion of the court is printed and separate opinions / head matter are only counted; `-a` prints all parts.
`-c 1` adds one sentence either side. `-k` instead of `-x` prints sentences with an operative cue word.
`python ctx.py <node> -o <offset> -w 1500` prints raw text around an offset. `python ctx.py <node> -p` prints the
part map. Part labels are sometimes wrong (old reports print a dissent inside "Majority"; slip opinions are page
chunks): judge from the text who is speaking. You may also Read `text\<node>.md` directly (use offset/limit; some are
long) and `text\<X node>.md` when you need to know what X held. Run from the diag directory; one opinion at a time;
keep outputs small (`-m`, `-l`).

## What to decide for each (Y, X)
Only the opinion of the Court counts (majority, per curiam, or a plurality that announces the judgment: say so in
`note`). Syllabus, counsel argument, concurrences and dissents do not count, but record them (below).

- **A** = 1 when the Court itself, in the present, acts on the NAMED case X (named in the sentence, or by clear
  anaphora from the sentence before: "that case", "that decision", "the former ruling") with operative words other
  than "overrule" that say X or its holding is no longer authority: "is rejected", "we reject", "repudiate",
  "disapprove", "is no longer the law / good law / to be followed", "cannot survive / stand", "must be regarded as
  overthrown", "we decline to follow", "is not to be followed", "we depart from", "we cannot adhere to",
  "we do not consider ourselves bound by", "is disavowed", "we now abandon".
  Set `A_kind`:
  - `operative`: such a verb or phrase, present act, on the named case;
  - `contrary`: the Court only states that it now holds the contrary of named X, with no verb about X's authority
    ("we hold, notwithstanding what is said in X", "contrary to the decision in X", "the reasoning of X is not
    tenable", "X can be viewed as a precedent only for ...") — A = 1, kind `contrary`;
  - `none`: A = 0.
  Not A: a REPORT of what earlier decisions did ("X was later repudiated in Z", "has since been rejected by our
  cases", "has been qualified by later decisions") — set `past_report` = 1 and give that sentence and Z; X merely
  distinguished, explained, read narrowly, called dictum without refusing it, criticised, or doubted; the Court
  denying that it overrules X.
- **B** = 1 when the Court's own operative words are aimed at a doctrine, a rule, a test or a line of cases rather
  than at one named case ("the doctrine of 'separate but equal' has no place", "the divided damages rule is
  replaced", "the rationale of those cases", "the 'Roberts test'"). Give the doctrine in `doctrine`. B can be 1
  together with A.
- **C** = 1 when the Court states the effect as limited to a field or a set of situations ("in the field of public
  education", "to the extent that", "insofar as it applies to", "as applied to ... cases"). Give the limit in
  `field`.
- `x_in_majority`: one of `not_cited`, `cited_neutral`, `distinguished`, `explained_narrowed` (reread, limited,
  treated as dictum), `criticised` (doubted, called unsound, no operative words), `contradicted` (holds the contrary
  in terms), `acted_on` (A operative), `past_report` (says earlier cases already overruled / rejected it),
  `denied` (the Court says it does not overrule X), `same_case` (X is an earlier judgment in the same case, vacated
  or reversed on rehearing).
- `own_sentence`: the single best sentence of the Court's opinion supporting A (or, if A = 0, B / C / the
  past report / the closest words). EXACT text copied from the file, one sentence (or clause) only, characters as
  they are in the file including OCR errors, no ellipsis, no added quotation marks, newlines replaced by a space.
  Empty when X is not cited and there is nothing. `own_offset`: its character offset as printed by ctx.py (`@n`).
- `sep_says`: 1 when a concurrence or dissent in Y says the Court overrules X; `sep_quote` the words (exact, short).
- `syllabus_says`: 1 when the syllabus / head matter says overruled.
- `gold_doubt`: 1 when in your judgment Y does not overrule X at all (wrong target, X overruled earlier by another
  decision, same-case rehearing, or Y expressly preserves X). Say why in `note`.
- `note`: at most 300 characters, plain facts.

Be strict on A: quote, do not paraphrase; if the best you can find is criticism, A = 0.

## Output
One JSON object per line (JSONL, UTF-8, LF line endings, written with the Write tool; no markdown), one line per
row of your shard, in idx order, keys exactly:

`idx, by_node, target_node, target_name, A, A_kind, B, C, doctrine, field, x_in_majority, past_report, own_sentence,
own_offset, sep_says, sep_quote, syllabus_says, gold_doubt, note`

(0/1 as numbers; `target_node` as in pairs.tsv, `-1` where unknown, with the name and citation you found in
`target_name`.) Write the file once at the end (or rewrite it whole as you go); do not append with shell heredocs.

Final reply: counts of A (operative / contrary), B, C, past_report, gold_doubt in your shard and anything
surprising, under 150 words.
