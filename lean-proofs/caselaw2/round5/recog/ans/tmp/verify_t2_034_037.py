# -*- coding: utf-8 -*-
"""Independent check of ans_pack_T2_034..037: order, JSON, quote is a substring of WINDOW, length, word, names."""
import io, json, os, re

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
WORD = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
STOP = {"state", "people", "united", "states", "commonwealth", "in", "re", "ex", "rel", "the", "of", "v", "inc",
        "co", "corp", "city", "county", "and", "court", "superior", "estate", "matter"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def idents(line):
    body = line.split(":", 1)[1].strip()
    body = re.sub(r"\(\d{4}\)\s*$", "", body).strip()
    parts = [p.strip() for p in body.split(";")]
    first = parts[0]
    m = re.search(r",\s*(\d+\s+[A-Za-z].*)$", first)
    name = first[:m.start()] if m else first
    cites = ([m.group(1)] if m else []) + parts[1:]
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'\-]{3,}", name) if w.lower() not in STOP]
    return [norm(c) for c in cites if c], [norm(w) for w in words]


def has(q, cites, words):
    nq = norm(q)
    return any(c and c in nq for c in cites) or any(w in nq for w in words)


for name in ["pack_T2_034", "pack_T2_035", "pack_T2_036", "pack_T2_037"]:
    with io.open(os.path.join(BASE, "packs", name + ".md"), encoding="utf-8", newline="") as f:
        text = f.read().replace("\r\n", "\n")
    items = []
    for block in text.split("### ITEM ")[1:]:
        iid = block.split("\n", 1)[0].strip()
        x = [l for l in block.split("\n") if l.startswith("X (the earlier decision)")][0]
        y = [l for l in block.split("\n") if l.startswith("Y (the decision said")][0]
        w = block.split("\nWINDOW:\n", 1)[1].split("\nNOTE AT:\n", 1)[0]
        items.append((iid, x, y, w))
    path = os.path.join(BASE, "ans", "ans_" + name + ".jsonl")
    raw = open(path, "rb").read()
    assert b"\r" not in raw, "CR found"
    rows = [json.loads(l) for l in raw.decode("utf-8").split("\n") if l.strip()]
    assert [r["id"] for r in rows] == [i[0] for i in items], "order/ids differ"
    bad = 0
    ntrue = 0
    for r, (iid, x, y, w) in zip(rows, items):
        if not r["states"]:
            assert r["reason"] and r["quote"] == ""
            continue
        ntrue += 1
        q = r["quote"]
        probs = []
        if q not in w:
            probs.append("not substring")
        if len(q) > 400:
            probs.append("too long")
        if not WORD.search(q):
            probs.append("no word")
        if not has(q, *idents(x)):
            probs.append("X not found")
        if not has(q, *idents(y)):
            probs.append("Y not found")
        if r["kind"] not in ("overruled", "abrogated", "disapproved", "recededFrom"):
            probs.append("kind")
        if r["scope"] not in ("all", "partialUnknown", "otherGrounds"):
            probs.append("scope")
        if probs:
            bad += 1
            print(name, iid, probs, "|", q)
    print(name, "items", len(rows), "true", ntrue, "problems", bad)
