import json, os, sys

base = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
packs = ["T1f_012", "T1f_017", "T1f_018"]
for p in packs:
    text = open(os.path.join(base, "packs", f"pack_{p}.md"), encoding="utf-8", newline="").read().replace("\r\n", "\n")
    ids, windows = [], {}
    for block in text.split("### ITEM ")[1:]:
        lines = block.split("\n")
        iid = lines[0].strip()
        wi = [i for i, l in enumerate(lines) if l.strip() == "WINDOW:"][0]
        ids.append(iid)
        windows[iid] = lines[wi + 1]
    ans_path = os.path.join(base, "ans_prescreen", f"ans_pack_{p}.jsonl")
    raw = open(ans_path, "rb").read()
    assert b"\r\n" not in raw, "CRLF found"
    rows = [json.loads(l) for l in raw.decode("utf-8").split("\n") if l.strip()]
    assert [r["id"] for r in rows] == ids, "ids/order mismatch"
    assert len(set(r["id"] for r in rows)) == len(rows), "duplicate"
    n_true = 0
    for r in rows:
        if r["states"] is True:
            n_true += 1
            q = r["quote"]
            w = windows[r["id"]]
            assert len(q) <= 400, (r["id"], len(q))
            assert q and q in w, (r["id"], "quote not a substring of window")
            assert r["kind"] in ("overruled", "abrogated", "disapproved", "recededFrom")
            assert r["scope"] in ("all", "otherGrounds", "partialUnknown")
    print(p, "items:", len(rows), "states_true:", n_true, "quotes_checked_ok")
