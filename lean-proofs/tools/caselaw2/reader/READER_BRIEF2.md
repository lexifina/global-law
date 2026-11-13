# Reader brief (round 2, Claude subagents; replaces the Azure model stage of classify.py)

You audit US court opinions for one fact: whether the DECIDING court, in its own voice in this opinion, performs or
declares a treatment of an earlier judicial decision.

Your pack file holds ITEMS. Each item has: the deciding decision, a numbered list of CANDIDATE earlier decisions
(resolved from citations or case names near the sentence), a WINDOW of the opinion text, and the FOCUS sentence inside
the window. Judge only from the item's own text. Do not use what you know about the case from elsewhere, do not look
anything up, do not read any other file, and do not call any external model or web service.

For each item answer:

- `own_act`: true only if, in the FOCUS sentence, the deciding court itself acts now on an earlier decision, e.g. "we
  overrule X", "X is hereby overruled", "X is disapproved", "we recede from X", "to the extent X holds otherwise, it is
  overruled", "X should be and is overruled", "we abrogate X", "X has been superseded by statute" stated as this
  court's own conclusion about X, "we decline to follow X", "we limit X to its facts", "we question the continued
  validity of X", "X is no longer good law" declared by this court as its holding.
  Round-2 wordings that are also this court's own act when it is the court's present conclusion: "that case is
  definitely overruled", "X should be, and now is, overruled", "X must be regarded / considered as overruled" (said by
  this court about the effect of ITS OWN present decision), "we are persuaded that X must be overruled", "we hold that X
  must be overruled", "our decision today overrules X", "we are constrained to overrule X", "X can no longer be
  regarded as the law / as controlling / as authority", "X is no longer to be followed", "we now reject the rule of X",
  "we overturn / disavow / abandon the rule of X", "to the extent inconsistent, X cannot survive".
  `own_act` is FALSE when the sentence: reports another court's act or earlier history ("X, overruled by Y", "abrogated
  by Y", "superseded by statute as stated in Y", "X was overruled in Y", "in Y we overruled X", "(overruling X)", "X
  must be regarded as overruled by our later cases" said about what EARLIER decisions did, "X is no longer good law
  after Y"); states a party's argument or request, or a lower court's view ("petitioner argues X is no longer good
  law", "the court below held X should be overruled"); refuses or declines to overrule; is conditional, hypothetical
  or about the power to overrule in general; quotes another opinion; is spoken by a dissent or concurrence; concerns a
  procedural ruling (objection, motion, exception, demurrer, assignment/point of error, contention "overruled"); or
  uses the verb about a statute, rule, contract, doctrine with no decision behind it, or the trial court's ruling in
  this same case rather than an earlier judicial decision. It is also FALSE when the act is negated ("X should not be
  limited to its facts", "X is not overruled"); when the sentence describes what this court or another body said in
  an earlier decision; or when it is a general observation about how courts treat X ("X is increasingly limited to its
  facts", "X raises doubts", "X has been criticized").
- `kind`: the treatment named by the verb: `overruled` (also repudiated / abandoned / overturned / disavowed / "no
  longer good law / the law / controlling / authority", "X can no longer be regarded as ...", "X cannot survive", and
  "X will no longer be followed" / "we will no longer follow X" when X is this court's own precedent or one it has
  power over), `disapproved`, `recededFrom`, `abrogated`, `supersededByEnactment` (a statute, rule or constitutional
  amendment displaced the decision), `limited`, `questioned`, `criticized`, `declinedToFollow` (a decision of another
  court, or of a coordinate court, that this court will not follow, without power to overrule it), `distinguished`,
  `followed`; `none` if own_act is false.
- `targets`: ids (T1, T2, ...) of the candidates whose holding, rule or dictum is the object of the act (the case
  being overruled, disapproved, limited, not followed ...). Never a decision cited as the authority for the new rule,
  nor one named only as the case the treated rule conflicts with. Only ids from the list. If the treated decision is
  not in the list, or you cannot tell which it is, return []. Several ids if the sentence treats several decisions.
  When the FOCUS says "that case", "the former decision", "those cases", "it", "they": the antecedent is in the
  WINDOW before the FOCUS; pick it only if the window makes it clear.
- `scope`: `all` (no limiting language), `issues` (the sentence itself names the point the act is limited to: give
  1-3 short issue labels in `issues`), `partialUnknown` ("to the extent that X conflicts with this opinion", "insofar
  as inconsistent", "in part", "so far as", "any language to the contrary", without naming the point),
  `otherGrounds` (the court says it treats X on a point other than the one X is cited for).
- `temporal`: `unknown` unless the opinion says how the change applies in time: `prospective`, `pureProspective` (not
  even to the present parties), `retroactive`. `prospective_from`: "" or "thisDecision" or a date yyyymmdd stated in
  the text.
- `quote`: if own_act is true, copy EXACTLY (character for character, including odd spacing, OCR errors and
  punctuation) one contiguous span of the WINDOW, at most 400 characters, that contains the treatment verb and, if they
  are in the same sentence, the target's name or citation. The simplest correct quote is usually the FOCUS sentence
  itself, or its operative clause. Otherwise "".
- `confidence`: 0 to 1, your probability that own_act, kind and targets are all right.

Most items in a pack are NOT own acts. Many "overruled" sentences are procedural. Be strict.

## Output

Write one JSON object per item, one per line, in the order of the pack, to the answer file named in your task
(UTF-8, LF), every item exactly once:

    {"id": "5971397:60512", "own_act": true, "kind": "overruled", "targets": ["T1"], "scope": "all", "issues": [],
     "temporal": "unknown", "prospective_from": "", "quote": "...", "confidence": 0.95}

`id` is the text after `### ITEM `. Write the file with a short Python script or the Write tool; make sure every line
parses as JSON (escape double quotes and backslashes inside `quote`). Do not write any other file in the project
directories. When done, reply with only: the number of items, the number with own_act true, by kind.
