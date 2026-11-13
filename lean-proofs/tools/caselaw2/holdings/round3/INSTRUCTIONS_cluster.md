# Clustering task: which questions about a US Code section are the SAME legal question?

You are given a file of sections. Under each section are numbered yes/no questions, each written by a different
reader of a different court-of-appeals decision (the bracket is the item id; the parenthesis is the subsection the
reader named). Read only that file. Do not use the web or your memory of particular cases.

For each section, group the questions that ask the SAME legal question: they would be answered by the same rule, even
if worded differently or phrased as the negation. Do NOT merge questions that are merely related (different elements,
different clauses, different predicate facts, a narrower versus a broader question).

Create one canonical yes/no question per group: general, about the statute, naming the section, no party names or
facts, under 300 characters. Give it a short label (under 60 characters).

For every item give `c` = the index of its canonical question in your `questions` list for that section, and `neg` =
true if the item's question is the NEGATION of the canonical question (so "yes" to the item means "no" to the
canonical question), else false. Every item must be assigned; a question that matches no other is its own group.
Be strict about sameness: a wrong merge creates a false circuit split.

Write one JSON object per line, one line per section, to the output file you are told:

    {"key":"29:1001","questions":[{"q":"Does 29 U.S.C. § 1001 ...?","label":"..."}],"items":[{"id":12,"c":0,"neg":false},{"id":15,"c":0,"neg":true}]}

`key` is the text after "## Section " up to the first space. Final reply: sections, items, groups with 2 or more items.
