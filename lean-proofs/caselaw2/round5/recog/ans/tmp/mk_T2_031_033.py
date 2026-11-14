# -*- coding: utf-8 -*-
"""Build and verify answer files for packs T2_031..033 from marker data."""
import importlib.util
import io
import json
import os
import re
import sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
HERE = os.path.dirname(os.path.abspath(__file__))
BANNED = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul",
          "not abrogat", "n't abrogat", "not been abrogat", "not disapprov", "whether",
          "without overruling", "rather than overrul", "declin", "refus", "would overrule",
          "should be overruled", "should overrule", "to overrule", "argu", "contend", "urge",
          "dissent", "question", "doubt"]
WORD = re.compile(r"overrul|abrogat|disapprov|reced", re.I)


def norm(s):
    return re.sub(r"[\s.,]", "", s).lower()


def parse_pack(path):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read().replace("\r\n", "\n")
    items = []
    for chunk in text.split("### ITEM ")[1:]:
        iid = chunk.split("\n", 1)[0].strip()
        w = chunk.split("\nWINDOW:\n", 1)[1].split("\nNOTE AT:\n", 1)[0]
        x = re.search(r"\nX \(the earlier decision\): (.*)", chunk).group(1)
        y = re.search(r"\nY \(the decision said to have done it\): (.*)", chunk).group(1)
        items.append((iid, w, x, y))
    return items


def names_ok(line, quote):
    """heuristic: a citation or a party-name word of the case line appears in the quote"""
    nq = norm(quote)
    parts = [p.strip() for p in line.split(";")]
    first = parts[0]
    m = re.match(r"(.*?), (\d+ .*)$", first)
    cites = []
    name = first
    if m:
        name = m.group(1)
        cites.append(re.sub(r"\(\d{4}\)\s*$", "", m.group(2)).strip())
    for p in parts[1:]:
        cites.append(re.sub(r"\(\d{4}\)\s*$", "", p).strip())
    for c in cites:
        if c and norm(c) in nq:
            return True
    words = [w for w in re.findall(r"[A-Za-zÀ-ÿ']{4,}", name)
             if w.lower() not in ("state", "people", "commonwealth", "united", "states", "parte", "city",
                                  "county", "company", "corp", "inc")]
    for w in words:
        if w.lower() in quote.lower():
            return True
    return False


def main(pack):
    spec = importlib.util.spec_from_file_location("d", os.path.join(HERE, "data_%s.py" % pack))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    A = mod.A
    items = parse_pack(os.path.join(BASE, "packs", "pack_%s.md" % pack))
    ids = [i[0] for i in items]
    aids = [a[0] for a in A]
    if ids != aids:
        print("ID MISMATCH", pack)
        print(" missing:", [i for i in ids if i not in aids])
        print(" extra:", [i for i in aids if i not in ids])
        for k, (p, q) in enumerate(zip(ids, aids)):
            if p != q:
                print(" first order diff at", k, p, q)
                break
        sys.exit(1)
    out = []
    bad = 0
    ntrue = 0
    for (iid, w, x, y), a in zip(items, A):
        if a[1]:
            _, _, kind, scope, fl, doc, qs, qe, conf = a
            i = w.find(qs)
            j = w.find(qe, i + 1 if qs != qe else i) if i >= 0 else -1
            if i >= 0 and qe in qs:
                j = i + qs.find(qe)
            if i < 0 or j < 0:
                print("MARKER NOT FOUND", iid, i, j)
                bad += 1
                continue
            quote = w[i:j + len(qe)]
            probs = []
            if len(quote) > 400:
                probs.append("len %d" % len(quote))
            if quote not in w:
                probs.append("not substring")
            if not WORD.search(quote):
                probs.append("no word")
            for b in BANNED:
                if b in quote.lower():
                    probs.append("banned:" + b)
            if not names_ok(x, quote):
                probs.append("X name?")
            if not names_ok(y, quote):
                probs.append("Y name?")
            if fl and fl not in w:
                probs.append("field_limit not in window")
            if probs:
                bad += 1
                print("CHECK", iid, probs, "|", quote)
            ntrue += 1
            out.append({"id": iid, "states": True, "kind": kind, "scope": scope, "field_limit": fl,
                        "doctrine": doc, "quote": quote, "confidence": conf})
        else:
            _, _, reason, conf = a
            out.append({"id": iid, "states": False, "reason": reason, "kind": "", "scope": "",
                        "field_limit": "", "doctrine": "", "quote": "", "confidence": conf})
    dest = os.path.join(BASE, "ans", "ans_pack_%s.jsonl" % pack)
    with io.open(dest, "w", encoding="utf-8", newline="\n") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    # re-read and verify
    with io.open(dest, "r", encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    wmap = {i[0]: i[1] for i in items}
    for r in rows:
        if r["states"]:
            assert r["quote"] in wmap[r["id"]] and len(r["quote"]) <= 400, r["id"]
    print(pack, "items", len(items), "written", len(rows), "true", ntrue, "flags", bad)
    if "-v" in sys.argv:
        for r in rows:
            if r["states"]:
                print(r["id"], "|", r["quote"])


if __name__ == "__main__":
    for p in sys.argv[1:]:
        if p != "-v":
            main(p)
