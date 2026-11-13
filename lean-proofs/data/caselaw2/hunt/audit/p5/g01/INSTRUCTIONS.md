You are auditing candidate findings about US court decisions. The items in this directory are a MIX: some are
believed to be true instances of the pattern below and some are not. You are not told which. Judge every item only on
the decision text given in its file (and your own knowledge of the law and of the named cases where the file is
silent; say so in the explanation when you rely on it). Be strict: `confirmed` means every limb of the predicate is
shown; `not_confirmed` means a limb fails; `unclear` only when the text given cannot settle it.

Read every item file I*.txt in this directory in full. Use only the Read and Write tools; no web, no scripts, no other
files. Then write ONE file `answers.jsonl` in this directory, one JSON object per line, one line per item:

    {"id": "Inn", "verdict": "confirmed"|"not_confirmed"|"unclear", "cited_on_losing_side": true|false, "relies_on_resolved_point": true|false, "notes_scotus": true|false, "explanation": "<one line, <= 45 words: what the citing court did and why the limb holds or fails>"}

Reply only with the number of lines written.

# Pattern

LOSING SIDE OF A RESOLVED SPLIT. The Supreme Court resolved a conflict among the courts of appeals. Limbs: (1) cited_on_losing_side: the cited court of appeals decision answered the resolved question the way the Supreme Court rejected; (2) relies_on_resolved_point: the citing decision (decided after the Supreme Court) relies on the cited decision for its answer to that very question (not for another point); (3) notes_scotus = false: the citing decision does not mention the Supreme Court decision or the abrogation. confirmed iff 1 and 2 hold and 3 is false.
