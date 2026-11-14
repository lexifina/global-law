# -*- coding: utf-8 -*-
"""Builds ans_pack_<name>.jsonl from a spec list; quotes are cut from the WINDOW by anchors."""
import io, json, os, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
BANNED = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]
KIND = {"o": "overruled", "a": "abrogated", "d": "disapproved", "r": "recededFrom"}
SCOPE = {"all": "all", "part": "partialUnknown", "other": "otherGrounds"}
WORD = re.compile(r"overrul|abrogat|disapprov|reced", re.I)


def load_pack(name):
    path = os.path.join(BASE, "packs", name + ".md")
    with io.open(path, encoding="utf-8", newline="") as f:
        text = f.read().replace("\r\n", "\n")
    items = []
    for block in text.split("### ITEM ")[1:]:
        iid = block.split("\n", 1)[0].strip()
        w = block.split("\nWINDOW:\n", 1)[1]
        w = w.split("\nNOTE AT:\n", 1)[0]
        items.append((iid, w))
    return items


def run(name, spec):
    items = load_pack(name)
    ids = [i for i, _ in items]
    sids = [s[0] for s in spec]
    ok = True
    if ids != sids:
        ok = False
        print("ID MISMATCH", [a for a in ids if a not in sids], [a for a in sids if a not in ids])
        for k, (a, b) in enumerate(zip(ids, sids)):
            if a != b:
                print(" first diff at", k, a, b)
                break
    win = dict(items)
    out = []
    ntrue = 0
    for s in spec:
        iid = s[0]
        if s[1] == "F":
            out.append({"id": iid, "states": False, "reason": s[2], "kind": "", "scope": "", "field_limit": "",
                        "doctrine": "", "quote": "", "confidence": s[3]})
            continue
        _, _, kind, scope, start, end, conf = s[:7]
        extra = s[7] if len(s) > 7 else {}
        w = win.get(iid, "")
        a = w.find(start)
        occ = extra.get("occ", 1)
        for _ in range(occ - 1):
            a = w.find(start, a + 1)
        b = w.find(end, a + len(start)) if a >= 0 else -1
        if a < 0 or b < 0:
            ok = False
            print("ANCHOR NOT FOUND", iid, a, b)
            continue
        q = w[a:b + len(end)]
        probs = []
        if len(q) > 400:
            probs.append("LEN %d" % len(q))
        if not WORD.search(q):
            probs.append("NO WORD")
        low = q.lower()
        for bad in BANNED:
            if bad in low:
                probs.append("BANNED " + bad)
        if q not in w:
            probs.append("NOT SUBSTRING")
        if probs and extra.get("allow"):
            print("ALLOWED (word inside a case name, cannot be cut)", iid, probs)
        elif probs:
            ok = False
            print("PROBLEM", iid, probs, "::", q)
        ntrue += 1
        out.append({"id": iid, "states": True, "kind": KIND[kind], "scope": SCOPE[scope],
                    "field_limit": extra.get("fl", ""), "doctrine": extra.get("doc", ""), "quote": q,
                    "confidence": conf})
    dest = os.path.join(BASE, "ans", "ans_" + name + ".jsonl")
    with io.open(dest, "w", encoding="utf-8", newline="\n") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(name, "items", len(out), "true", ntrue, "OK" if ok else "CHECK")
    if "-v" in sys.argv:
        for o in out:
            if o["states"]:
                print(o["id"], len(o["quote"]), "|", o["quote"])
