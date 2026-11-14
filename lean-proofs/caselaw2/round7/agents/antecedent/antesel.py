"""Round 7, agent `antecedent`: tiers of cands.jsonl.gz for reading -> sel_<tier>.jsonl, sel_stats.json.

    python -X utf8 antesel.py

Rules (on the act sentence; the scan's anaphor regex is a superset, this one is tighter):
  drop  report   a report of a past act (anterule.REPORT, or "we overruled / disapproved / receded")
  drop  neg      not, n't, never, nor, decline, refuse, whether, need not, unnecessary (a conditional "if" is kept)
  drop  nolink   no anaphor phrase (ANAPH below) within 100 characters of an act word
  drop  notown   no own-act form (OWN: "is/are ... overruled", "we overrule", "hereby ...", "overrule those ...",
                 "no longer the law") or a not-own mark (NOT_OWN: asked / urged / contends / unless / until / power
                 to / en banc / a modal before the verb / a "See" signal / "the ... court overruled")
  tier A  >= 1 NEAR target (naming sentence ends <= 300 characters before), act word overrul / disapprov / abrogat /
          recede
  tier B  no near target, >= 1 target named in the act sentence, the same act words, and no admitted base row for
          any in-act target (a one-sentence act the base does not hold: reader recall)
  tier C  >= 1 near target, act word repudiat / disavow / overturn / "no longer", a NOUN anaphor ("those cases", ...)
Within a tier the order is a seeded shuffle (seed 7). No answer key is read.
"""
import collections, gzip, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anterule as R  # noqa: E402

NL = chr(10)
STRONG = re.compile(r"\b(?:overrul\w*|disapprov\w*|abrogat\w*|reced(?:e|es|ed|ing)\b)", re.I)
WEAK = re.compile(r"\b(?:repudiat\w*|disavow\w*|overturn\w*|no\s+longer\b)", re.I)
NEG = re.compile(r"\b(?:not|never|nor|unnecessary|need\s+not|declin\w*|refus\w*|whether)\b|n't\b", re.I)
PAST_WE = re.compile(r"\bwe\s+(?:\w+\s+)?(?:overruled|disapproved|abrogated|receded|repudiated|overturned)\b", re.I)
_DET = (r"(?:(?:those|these|such|said|both|all\s+such|all\s+of\s+(?:these|those|the|them)|each\s+of\s+(?:these|those|the)|"
        r"the\s+(?:above(?:[\s-]+(?:cited|mentioned|named))?|foregoing|said|former|latter|cited|aforesaid|preceding|two|"
        r"three|four|earlier|prior|other|last[\s-]+(?:named|cited|mentioned)))\s+(?:[\w’'-]+[\s-]+){0,2}?"
        r"|that\s+(?:(?:prior|earlier|former|same|particular|latter|first|second|older|previous)\s+)?)")
_NOUN = (r"(?:cases?|decisions?|opinions?|holdings?|authorities|authority|precedents?|rulings?|judgments?|"
         r"line\s+of\s+(?:cases|decisions|authority|authorities)|expressions?|statements?|dicta|dictum|language)\b")
NOUN_ANAPH = re.compile(r"\b" + _DET + _NOUN + r"|\bthe\s+(?:cases|decisions|authorities|opinions)\s+(?:above\s+|just\s+|"
                        r"last\s+|hereinbefore\s+|heretofore\s+|previously\s+|so\s+)?(?:cited|mentioned|referred\s+to|"
                        r"named|listed|discussed|relied\s+(?:up)?on|noted)\b|\b(?:each|all|both|either|any)\s+of\s+them\b",
                        re.I)
PRON_ANAPH = re.compile(r"\b(?:they|it|them)\b", re.I)
LINK = 100
# the deciding court's own present act: a passive present / "we <verb>" / "must be considered as overruled" / hereby
_V = r"(?:overrul\w*|disapprov\w*|abrogat\w*|reced\w*|repudiat\w*|disavow\w*|overturn\w*)"
OWN = re.compile(r"\b(?:is|are|stands?|be|been)\s+(?:\w+\s+){0,3}?(?:overruled|disapproved|abrogated|receded|repudiated|"
                 r"disavowed|overturned)\b|"
                 r"\bwe\s+(?:\w+\s+){0,3}?(?:overrule|disapprove|abrogate|recede|repudiate|disavow|overturn)s?\b|"
                 r"\b(?:hereby|now|expressly|accordingly|therefore|thus|further|also|likewise)\s+(?:\w+\s+)?" + _V + r"|"
                 r"\b(?:overrule|disapprove|recede\s+from|abrogate|repudiate|disavow)\s+(?:the|those|these|that|them|it|"
                 r"such|said|both|all|each|any)\b|"
                 r"\bno\s+longer\s+(?:\w+\s+){0,3}?(?:the\s+law|good\s+law|law|authorit\w*|be\s+followed|followed|"
                 r"controlling|binding|precedent)", re.I)
NOT_OWN = re.compile(r"\b(?:ask\w*|urg\w*|invit\w*|request\w*|call\w*\s+upon|contend\w*|argu\w*|unless|until|"
                     r"power\s+to|authority\s+to|free\s+to|en\s+banc|in\s+banc|wish\w*|seek\w*|reluctan\w*|hesita\w*|"
                     r"overrule\s+(?:his|her|their|its|the\s+(?:objection|motion|exception|demurrer)))\b|"
                     r"\b(?:can|cannot|could|may|might|would|should|ought\s+to|shall)\s+(?:\w+\s+){0,2}?(?:be\s+)?" + _V +
                     r"|^\s*(?:see|cf|but\s+see|accord|compare)\b|\bthe\s+(?:\w+\s+){0,3}court\s+(?:\w+\s+){0,2}?" + _V,
                     re.I)


def linked(act):
    acts = [m for m in re.finditer(STRONG.pattern + "|" + WEAK.pattern, act, re.I)]
    anas = [(m, "noun") for m in NOUN_ANAPH.finditer(act)] + [(m, "pron") for m in PRON_ANAPH.finditer(act)]
    best = None
    for a in acts:
        for m, typ in anas:
            gap = a.start() - m.end() if m.end() <= a.start() else m.start() - a.end()
            if gap < 0:
                gap = 0
            lim = LINK if typ == "noun" else 40
            if gap <= lim and (best is None or (typ == "noun" and best[1] == "pron") or gap < best[0]):
                best = (gap, typ)
    return best


def main():
    st = collections.Counter()
    tiers = collections.defaultdict(list)
    for line in gzip.open(os.path.join(HERE, "cands.jsonl.gz"), "rt", encoding="utf-8"):
        c = json.loads(line)
        act = c["act"]
        st["cands"] += 1
        if R.REPORT.search(act) or PAST_WE.search(act):
            st["drop_report"] += 1
            continue
        if NEG.search(act):
            st["drop_neg"] += 1
            continue
        lk = linked(act)
        if lk is None:
            st["drop_nolink"] += 1
            continue
        if not OWN.search(act) or NOT_OWN.search(act):
            st["drop_notown"] += 1
            continue
        tg = c["targets"]
        near = [x for x in tg if x["where"] == "near"]
        inact = [x for x in tg if x["where"] == "act"]
        strong = bool(STRONG.search(act))
        if near and strong:
            t = "A"
        elif not near and inact and strong:
            if any(x["base"] for x in inact):
                st["drop_B_base"] += 1
                continue
            t = "B"
        elif near and lk[1] == "noun" and WEAK.search(act):
            t = "C"
        else:
            st["drop_other"] += 1
            continue
        c["tier"] = t
        c["link"] = lk[1]
        tiers[t].append(c)
        st["tier_" + t] += 1
        if any(x["base"] for x in near + inact):
            st["tier_%s_with_base" % t] += 1
    for t, L in tiers.items():
        random.Random(7).shuffle(L)
        with open(os.path.join(HERE, "sel_%s.jsonl" % t), "w", encoding="utf-8", newline=NL) as f:
            for c in L:
                f.write(json.dumps(c, ensure_ascii=False) + NL)
    with open(os.path.join(HERE, "sel_stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(st), f, indent=1)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
