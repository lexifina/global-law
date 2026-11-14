# Blind audit brief (opw1)

You are checking claims about what courts said. Work alone, from the text you are given.

## What an item is

Each ITEM in your pack (`round5\audit\opw1\packs\audit_<nn>.md`) has:

- **SPEAKING DECISION**: the court and date of the decision whose text is shown.
- **OPINION PART** (not always present): a machine label for the part of the decision the middle of the passage
  lies in. It can be wrong. If the passage itself plainly shows otherwise (a heading such as `## Dissent`, a line
  such as "BLACK, J., dissenting"), the passage governs.
- **CLAIM**: `"X" lost authority (was overruled, abrogated, disapproved, receded from, rejected or repudiated
  — as a whole or in part) through "Y".` X is an earlier decision. Y is a later decision, or the words
  "this decision", which mean the speaking decision itself.
- **PASSAGE**: about 2,000 characters of the speaking decision's text. Line breaks were turned into spaces;
  `…` marks a cut. The relevant words, if there are any, can stand anywhere in the passage.

The items come from sources of very different quality. Some are known to be wrong. Do not assume that an item is
right, and do not assume it is wrong: read it.

## The question

Does **the speaking court itself, in the opinion of the court, state or accept as fact that X lost authority
through Y**? Answer it in three separate parts. Take the statement in the passage that comes closest to the claim.

`stated`: is there such a statement at all: the court itself saying that an earlier decision lost authority
through a decision?

- `yes`: the court's own voice (majority, per curiam or lead opinion) says it or relies on it as settled:
  "we overrule A"; "A is overruled"; "A, overruled by B"; "B abrogated A"; "A was disapproved in B";
  "A is no longer good law after B"; "overruled in part by B"; "overruled on other grounds by B".
  A loss in part, or on a point other than the one under discussion, is still `yes` (say which under `extent`).
- `no`: anything else, in particular
  - it is a party's argument, a lower court's view, another court's words quoted, or another judge's view,
    which the court reports without adopting;
  - it stands in a dissent, a concurrence or a statement of individual judges, or in head matter / a syllabus /
    a reporter's note rather than in the opinion;
  - it is a question, or left open ("we need not decide whether B overruled A");
  - it is negated ("B did not overrule A", "we decline to overrule A");
  - it is hypothetical or conditional ("if A were overruled", when nothing is actually declared);
  - the earlier decision is only questioned, doubted, criticised, limited, narrowed, explained, distinguished
    or not followed, with no statement that it lost authority;
  - the earlier decision was reversed, vacated or modified on appeal in the same litigation (that is the case's
    own history, not what the claim says), or was displaced by a statute or rule and not by a decision.
- `unclear`: you cannot tell, even with more text.

`x_ok`: `true` when the earlier decision of that statement is the X of the claim (same case: the name and / or a
citation fits; a short form such as "Jones" counts when the text ties it to the same case). `false` when the
statement is about a different case, or the passage does not speak of X at all.

`y_ok`: `true` when the decision through which it happened, according to the passage, is the Y of the claim.
When the claim says "through this decision": `true` only if the speaking decision does it itself, here; `false`
when the passage reports what an earlier or another decision did.

So a passage in which the court overrules some other case than X is `stated: yes, x_ok: false`. When `stated`
is `no`, still answer `x_ok` and `y_ok` as well as you can (is the passage speaking of X, and of Y, at all).
The claim counts as confirmed only when `stated` is `yes` and both `x_ok` and `y_ok` are `true`.

`extent` (what the passage says, not what you know):

- `whole`: X as a whole, without qualification;
- `part`: only in part, on one point, "to the extent that", "insofar as", one of several holdings, a doctrine or
  a statement of X rather than X itself, or limited to a field;
- `otherGrounds`: "overruled on other grounds" and the like;
- `unclear`: not stated, or `stated` is not `yes`.

`words`: the few words of the passage (at most about 25, copied exactly) that carry your answer; for a `no`,
the words that show why, or "".

## More text

If the passage is not enough, ask for a wider one (run from the `caselaw-lean-2` folder):

    python round5\audit\more_text.py <item id> [chars]

`chars` is the number of extra characters on each side (default 3000; `all` prints the whole opinion text). It
prints the speaking decision's text only, with the pack's passage between `>>>` and `<<<`.

## Rules

- Judge from the text only. Use **no outside knowledge of what happened to these cases**: if you happen to know
  that X was overruled by Y but the speaking court does not say so here, the answer is `no`.
- No external model or API, no web search.
- Open no other files: only this brief, your pack and the output of `more_text.py`. In particular nothing else
  under `round5\audit\`, no data tables, no other auditor's answers.
- Every item of your pack exactly once, in pack order.

## Answers

One JSON object per line, written to `round5\audit\opw1\answers\ans_<nn>.jsonl` (`<nn>` = your pack number;
UTF-8, LF):

    {"id": "<item id>", "stated": "yes|no|unclear", "x_ok": true|false, "y_ok": true|false, "extent": "whole|part|otherGrounds|unclear", "words": "<the few words that carry it>", "note": ""}

Each line must parse as JSON (escape `"` and `\` inside strings). `note` is free (a short reason helps).
