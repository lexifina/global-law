import json, sys
sys.path.insert(0, "~/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/recog/ans_prescreen/tmp")
from r5_parse import parse
base = "~/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/recog/"
for p in ["029", "030", "034"]:
    items = parse(base + f"packs/pack_T1f_{p}.md")
    raw = open(base + f"ans_prescreen/ans_pack_T1f_{p}.jsonl", "rb").read()
    assert b"\r" not in raw
    lines = raw.decode("utf-8").split("\n")
    assert lines[-1] == ""
    lines = lines[:-1]
    rows = [json.loads(l) for l in lines]
    assert [r["id"] for r in rows] == list(items), p
    n_true = 0
    for r in rows:
        if r["states"]:
            n_true += 1
            w = items[r["id"]]["window"]
            assert r["quote"] in w and len(r["quote"]) <= 400, (p, r["id"])
    print(p, "items", len(rows), "states true", n_true, "OK")
