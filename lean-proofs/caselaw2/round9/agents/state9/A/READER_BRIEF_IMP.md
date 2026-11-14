# Reader brief: does the court itself reject an earlier decision's holding or rule in this sentence? (round 9, state9 A)

You read passages from US court opinions. In each item one sentence, the **ACT sentence**, has words such as
"we disagree with", "we are not persuaded by", "we decline to follow", "is no longer good law", "was wrongly
decided", "its reasoning is unsound", "has been undermined", "contrary to the holding in", "we depart from". You
decide **whether, in the ACT sentence, the deciding court itself, now, in its own words, rejects or departs from the
holding, rule or reasoning of one of the listed earlier decisions** (an "implicit overruling" or a refusal to follow
it), without necessarily using the word "overrule".

Your pack file (`packs/pack_NNN.md`) holds ITEMS. Each item has:

- `### ITEM <id>`
- `ACTING:` the deciding decision (name, citation, court, date) and the opinion part the ACT sentence is in;
- `TARGETS:` a numbered list `T1`, `T2`, ... of earlier decisions named in the ACT sentence: name, citation, date,
  court, how the passage names it (`cite "<citation>"` or `name "<words>"`);
- `WINDOW:` the opinion text around the ACT sentence. The ACT sentence stands between `⟦` and `⟧`; each listed
  decision's name/citation is marked `[T1]`, `[T2]`, ... just after it (marks are not part of the opinion);
- `ACT:` the ACT sentence again.

Judge from the item's own text only. Do not use what you know about the cases, do not look anything up, and do not
open any other file of the project (in particular nothing under `gold/`, `benchmarks/`, `round5/gold_fresh/`,
`round5/tests/`, `round6/shepardized/`, `round6/history/split/`, `round7/heldout/`, `events_v3/`, `eval/`), and do
not call any external model or web service. Read only your own pack file and this brief; write only your answer
file. No subagents.

## What to answer

One JSON object per item, one per line, in the answer file named in your task:

    {"id": "5687:3028", "act": true, "targets": ["T1"], "kind": "declinedToFollow",
     "act_quote": "We disagree with the holding of Smith v. Jones, 12 Ga. 3, that a parol lease is void.",
     "confidence": 0.9, "why": "court's own rejection of T1's holding"}

- `id`: the text after `### ITEM `.
- `act`: **true only if all of these hold:**
  1. The ACT sentence states the deciding court's own position, now, in this opinion (the majority / the court:
     "we disagree with X", "we decline to follow X", "we are not persuaded that X correctly states the law",
     "X is no longer good law", "we think X was wrongly decided", "to the extent X holds ..., we disagree",
     "the reasoning of X is unsound and we will not follow it", "X has been undermined and we no longer adhere to it").
  2. What it rejects is the **holding, rule, reasoning or result of the earlier judicial decision X** itself — not a
     party's argument about X, not a party's or the lower court's reading or application of X, not the trial court's
     ruling in this very case, not a statute.
  3. X is in the TARGETS list.
- `act` is **false** when the ACT sentence:
  - only disagrees with a party, counsel, the trial court or the court below in this case ("we disagree with
    appellant that X controls", "we are not persuaded by defendant's reliance on X") — the court rejects a reading or
    a reliance, not X's rule;
  - distinguishes X, finds X inapplicable to these facts, or declines to EXTEND X beyond its facts while leaving X's
    rule intact ("we decline to extend X to ...", "X is not controlling here", "unlike X");
  - reports another court's or an earlier decision's view ("the Ninth Circuit disagreed with X", "in Y we declined to
    follow X", "X has been criticized by commentators", "X was undermined by Y" as a report of Y's effect);
  - says X is no longer law or no longer controlling BECAUSE OF a statute, an amendment, a rule change or another
    decision (an intervening cause: "in light of the amendment, X is no longer controlling", "after Y, X is no longer
    good law") — the court reports an effect, it does not itself reject X's rule;
  - is a hypothesis, question, refusal to decide, or doubt left open ("we need not decide whether X survives",
    "even if X were wrong");
  - is inside a quotation of another opinion, a syllabus or headnote, a concurrence or a dissent (visible from the
    window: quotation marks around the sentence, "I would", "I concur", "dissenting", "the majority");
  - names no decision of the TARGETS list as the one rejected;
  - rejects a decision of a court in ANOTHER state or system as merely unpersuasive authority ("we decline to follow
    the Texas court in X") — still answer `act: true` in that case, but give `"kind": "declinedToFollow"` and say
    "foreign" in `why`.
- `targets`: the T-numbers whose holding / rule / reasoning the court rejects; `[]` when `act` is false.
- `kind`: `declinedToFollow` (the court refuses to follow / disagrees with / rejects X's rule or result),
  `questioned` (the court says X's authority is doubtful, undermined, no longer sound, without itself refusing to
  follow it), or `criticized` (the court criticizes X's reasoning but still follows or does not reach it).
- `act_quote`: the exact text of the ACT sentence as printed after `ACT:` (copy it character for character; you may
  shorten it to a contiguous part that still holds the rejecting words and the target's name/citation).
- `confidence`: 0 to 1. `why`: at most 25 words.

Be strict: when you are unsure that the court itself, now, rejects the rule of a listed earlier decision, answer
`act: false`. Answer every item of your pack, in order; do not stop early. Write the answer file with the Write tool
(UTF-8). Reply at the end with only: number of items, number with act true.
