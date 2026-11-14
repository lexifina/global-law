import json, os, re, sys

REC = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
FORBID = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
          "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
          "without overruling", "rather than overrul", "declin", "refus", "would overrule",
          "should be overruled", "should overrule", "to overrule", "contend", "dissent",
          "question", "doubt", "argues", "argued", "arguing", "argument", "urges", "urged", "urging"]
REASONS = {"notMajority", "quotation", "argument", "negation", "question", "refusal", "would",
           "ownAct", "wrongDirection", "otherDecision", "notOverruling", "cannotTell", "notInOneSpan"}
KINDS = {"overruled", "abrogated", "disapproved", "recededFrom"}
SCOPES = {"all", "otherGrounds", "partialUnknown"}
OVR = re.compile(r"overrul|abrogat|disapprov|reced", re.I)


def parse_pack(path):
    items, cur, mode = [], None, None
    for ln in open(path, encoding="utf-8").read().split("\n"):
        if ln.startswith("### ITEM "):
            cur = {"id": ln[len("### ITEM "):].strip(), "window": []}
            items.append(cur)
            mode = None
            continue
        if cur is None:
            continue
        if ln.startswith("WINDOW:"):
            mode = "w"
            continue
        if ln.startswith("NOTE AT:"):
            mode = None
            continue
        if mode == "w":
            cur["window"].append(ln)
    for it in items:
        it["window"] = "\n".join(it["window"])
    return items


def main():
    pack, ansfile = sys.argv[1], sys.argv[2]
    ns = {}
    exec(open(ansfile, encoding="utf-8").read(), ns)
    A = ns["A"]
    items = parse_pack(os.path.join(REC, "packs", pack + ".md"))
    ids = [it["id"] for it in items]
    assert len(ids) == len(set(ids)), "duplicate ids in pack"
    missing = set(ids) - set(A)
    extra = set(A) - set(ids)
    if missing or extra:
        print("MISSING", sorted(missing), "EXTRA", sorted(extra))
        sys.exit(1)
    errs, out, nt = [], [], 0
    for it in items:
        a = A[it["id"]]
        w = it["window"]
        if a["states"]:
            nt += 1
            q = a["quote"]
            if q not in w:
                errs.append((it["id"], "quote not an exact substring of window"))
            if len(q) > 400:
                errs.append((it["id"], "quote longer than 400"))
            if not OVR.search(q):
                errs.append((it["id"], "no overruling word in quote"))
            if a["xkey"] not in q:
                errs.append((it["id"], "X key not in quote"))
            if a["ykey"] not in q:
                errs.append((it["id"], "Y key not in quote"))
            for f in FORBID:
                if f in q.lower():
                    errs.append((it["id"], "forbidden string in quote: " + f))
            if a["kind"] not in KINDS or a["scope"] not in SCOPES:
                errs.append((it["id"], "bad kind/scope"))
            out.append({"id": it["id"], "states": True, "kind": a["kind"], "scope": a["scope"],
                        "field_limit": a.get("field_limit", ""), "doctrine": a.get("doctrine", ""),
                        "quote": q, "confidence": a["conf"]})
        else:
            if a["reason"] not in REASONS:
                errs.append((it["id"], "bad reason " + a["reason"]))
            out.append({"id": it["id"], "states": False, "reason": a["reason"], "kind": "", "scope": "",
                        "field_limit": "", "doctrine": "", "quote": "", "confidence": a["conf"]})
    if errs:
        for e in errs:
            print("ERR", e)
        print("NOT WRITTEN; fix errors")
        sys.exit(1)
    dest = os.path.join(REC, "ans_prescreen", "ans_" + pack + ".jsonl")
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    print("items", len(items), "states_true", nt, "written", dest)


if __name__ == "__main__":
    main()
