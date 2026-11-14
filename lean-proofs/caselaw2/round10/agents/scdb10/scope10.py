"""scdb10 s10: whole-case scope for Supreme Court decision-below rows whose judgment sentence names each court's
judgment with its own verb (DESIGN7 section 6 scope rule, applied to history rows).

    python -X utf8 scope10.py   -> replace_s10.tsv (13-column history rows of round9/stage/v9c with scope all),
                                   work/scope10_stats.json

Rule (general, every base history row): acting decision = the Supreme Court, src a decision-below linker
(r6:below:sc*, r7:below:sc*), kind reversed | vacated | affirmed, scope unknown. Its judgment quote is split into
clauses at ";", ", and", " and that", " and the"; exactly one clause names the target's court (round 6's ph_match = 2)
as the owner of a judgment / decree ("the judgment of the Court of Appeals is reversed", "that of the District Court is
affirmed"); that clause's only judgment verb is the row's kind; the whole quote holds no limiting phrase (insofar, to
the extent, in part, as to, so far as, except, only, with respect to, ...) and no docket number. Then the scope is all.
No key is read.
"""
import collections, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "below_sc"))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import link  # noqa: E402

L = link.L
NL = chr(10)
LIMIT = re.compile(r"\bto\s+the\s+extent\b|\binsofar\b|\bin\s+so\s+far\b|\bin\s+part\b|\bas\s+to\b|\bso\s+far\s+as\b|"
                   r"\bexcept\b|\bonly\b|\bwith\s+respect\s+to\b|\bin\s+(?:all\s+)?other\s+respects\b|\bpart\s+of\b|"
                   r"\bportions?\b|\baccording\s+to\s+which\b|\bmodif|\bNos?\.\s*\d|\bcount\b|\bclaims?\b|\bsentence\b|"
                   r"\bconvictions?\b|\bwith\s+respect\b|\bunless\b|\bif\b|\bto\s+(?:this|that)\s+extent\b|"
                   r"\bin\s+(?:this|that|these|those)\s+respects?\b|\bon\s+the\s+(?:remaining|questions?|matter|issues?|"
                   r"point)\b|\bremaining\b|\bholding\s+otherwise\b", re.I)
SPLIT = re.compile(r";|,?\s+and\s+(?=(?:that|the|those|its)\b)|,\s+(?=(?:that|the)\s+(?:judgment|decree|one)\b)", re.I)
VERB = {"affirm": "affirmed", "revers": "reversed", "vacat": "vacated"}
VRX = re.compile(r"\b(affirm|revers|vacat)\w*", re.I)
OWNER = re.compile(r"\b(?:judgments?|decrees?|orders?|decisions?|one|that)\s+(?:entered\s+)?(?:by|of|in)\s+(?:the\s+)?$", re.I)


def main():
    link.init()
    F = link.G["F"]
    st = collections.Counter()
    out = []
    with open(os.path.join(C2, "round9", "stage", "v9c", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[5] != "unknown" or p[4] not in ("reversed", "vacated", "affirmed"):
                continue
            if not re.match(r"r[67]:below:sc", p[12]):
                continue
            by, t = int(p[2]), int(p[1])
            if int(F.court[by]) != L.SCOTUS2:
                continue
            st["cand"] += 1
            q = p[9]
            if LIMIT.search(q):
                st["drop:limit"] += 1
                continue
            ci = link.court_info(int(F.court[t]))
            pieces = SPLIT.split(q)
            own = []
            for c in pieces:
                phs = [ph for ph in link.phrases(c) if link.ph_match(ph, ci) == 2]
                phs = [ph for ph in phs if OWNER.search(c[max(0, ph[0] - 40):ph[0]])]
                if phs:
                    own.append(c)
            if len(own) != 1:
                st["drop:clauses_naming_target_court_%d" % min(len(own), 2)] += 1
                continue
            # the instruction to the court on remand is not this Court's act ("... reversed, with direction that the
            # judgment of the District Court be affirmed")
            act = re.split(r"\bwith\s+(?:the\s+)?(?:directions?|instructions?)\b|\bremand\w*\b|\bdirect(?:ed|ing|ion)\b",
                           own[0], 1, flags=re.I)[0]
            verbs = {VERB[m.group(1).lower()] for m in VRX.finditer(act)}
            if verbs != {p[4]}:
                st["drop:clause_verb"] += 1
                continue
            p2 = list(p)
            p2[5] = "all"
            out.append(p2)
            st["kept:" + p[4]] += 1
    with open(os.path.join(HERE, "replace_s10.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for p in out:
            f.write("\t".join(p) + NL)
    st["rows"] = len(out)
    json.dump(st, open(os.path.join(HERE, "work", "scope10_stats.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))
    for p in out[:40]:
        print(p[2], p[1], p[4], "|", p[9][:200])


if __name__ == "__main__":
    main()
