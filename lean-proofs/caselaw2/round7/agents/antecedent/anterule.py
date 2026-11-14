"""Round 7, agent `antecedent`: the deterministic rule (target(s), kind, scope, spans) for a candidate of
cands.jsonl.gz. Used for the self-measured sample (rule_sample.py) and as the reader's starting point.

rule(c) -> None (no act by rule) or {"targets": [node...], "kind", "scope", "main": [s0, s1], "joined": {node: span}}

  1. refuse: a report of a past act ("has been / was / since overruled", antescan REPORT) or a negation / condition
     (not, never, decline, refuse, whether, need not, unnecessary, if) in the act sentence;
  2. kind from the act word: overrul / repudiat / overturn / disavow / no longer -> overruled, disapprov ->
     disapproved, abrogat -> abrogated, recede -> recededFrom (the first act word of the sentence);
  3. targets: decisions cited or named IN the act sentence when there are any (one-sentence act); else the near
     targets (naming sentence ends <= 300 characters before the act sentence): a singular pointer ("that case",
     "it", "that decision") takes the one named last; a plural pointer takes every decision named in the last naming
     sentence;
  4. scope: partialUnknown when the act sentence has a limiting phrase (cue table operative_limit plus "on other
     grounds", "as to", "pro tanto", "the language", "dict", "the rule", "the holding"), else all.
"""
import re

LIMIT = re.compile(r"to\s+the\s+extent|to\s+(?:that|this)\s+extent|insofar|in\s+so\s+far|so\s+far\s+as|\bin\s+part\b|"
                   r"on\s+(?:this|that|the)\s+(?:issue|point|question)|as\s+respects|in\s+the\s+field\s+of|"
                   r"other\s+grounds?|\bas\s+to\b|pro\s+tanto|\blanguage\b|\bdict(?:a|um)\b|\bthe\s+rule\b|"
                   r"\bholding\s+that\b|\binconsistent\b|\bconflict", re.I)
REPORT = re.compile(r"\b(?:has|have|had|was|were|been|being|since|subsequently|later|previously|already|impliedly|"
                    r"effectively|implicitly)\s+(?:\w+\s+){0,2}?(?:overrul|disapprov|abrogat|reced|repudiat|overturn)",
                    re.I)
NEG = re.compile(r"\b(?:not|n't|never|nor|unnecessary|need\s+not|decline|refuse|whether|if)\b|n't\b", re.I)
KIND = re.compile(r"(overrul|repudiat|overturn|disavow|no\s+longer|disapprov|abrogat|reced)", re.I)
SING = re.compile(r"\b(?:that|said|the\s+(?:former|latter|above|cited|said|earlier|prior))\s+(?:\w+[\s-]+){0,2}?"
                  r"(?:case|decision|opinion|holding|authority|precedent|ruling|judgment)\b|\bit\b", re.I)


def kind_of(act):
    m = KIND.search(act)
    if not m:
        return None
    w = m.group(1).lower()
    if w.startswith("disapprov"):
        return "disapproved"
    if w.startswith("abrogat"):
        return "abrogated"
    if w.startswith("reced"):
        return "recededFrom"
    return "overruled"


def rule(c):
    act = c["act"]
    if REPORT.search(act) or NEG.search(act):
        return None
    kind = kind_of(act)
    if not kind:
        return None
    tg = c["targets"]
    inact = [x for x in tg if x["where"] == "act"]
    near = [x for x in tg if x["where"] == "near"]
    if inact:
        pick = inact
    elif near:
        last_end = max(x["span"][1] for x in near)
        last = [x for x in near if x["span"][1] == last_end]
        if SING.search(act) and not re.search(r"\b(?:those|these|they|them|cases|decisions|both|each)\b", act, re.I):
            pick = [max(last, key=lambda x: x["hit"][0])]
        else:
            pick = last
    else:
        return None
    scope = "partialUnknown" if LIMIT.search(act) else "all"
    return {"targets": [x["t"] for x in pick], "kind": kind, "scope": scope, "main": c["s"],
            "joined": {x["t"]: x["span"] for x in pick if x["where"] == "near"}}
