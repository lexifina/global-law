"""Round 2 model stage, part 1: packs of candidate items for Claude subagents (no external model is called).

    python -X utf8 pack2.py --out DIR [--res DIR] [--select FILE] [--size 80]

Reads data/reader_work/res2/<repo>.items.jsonl.gz (resolve2.py). --select is a TSV whose first column is the item id
(default: every item). Writes DIR/pack_NNN.txt (the items, rendered exactly as classify.render does for the v1 model:
deciding decision, candidate list T1.., window, focus sentence, prospectivity sentences) and DIR/index.tsv
(item id, repo, pack). The subagent writes DIR/ans_NNN.jsonl with one object per item, in the v1 answer format:

    {"id": "...", "own_act": true, "kind": "overruled", "targets": ["T1"], "scope": "all", "issues": [],
     "temporal": "unknown", "prospective_from": "", "quote": "...", "confidence": 0.9}

The instructions given to the subagents are in READER_BRIEF (the v1 SYSTEM prompt of classify.py with the round-2
additions marked).
"""
import argparse, glob, gzip, json, os, sys, zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import WORK  # noqa: E402


def render(it):
    lw = it["w"][it["lw0"] - it["w0"]:it["lw1"] - it["w0"]]
    focus = it["w"][it["s0"] - it["w0"]:it["s1"] - it["w0"]]
    part = it["part"].rstrip("~")
    lines = [f"### ITEM {it['id']}",
             f"DECIDING: {it['by']['name']} ({it['by']['court']}, {it['by']['year']}); opinion part: {part}",
             "CANDIDATES:"]
    for k, t in enumerate(it["targets"]):
        lines.append(f"  T{k + 1}: {t['name']} - {t['court']}, {t['year']} - {t['cite']} [{t['ev']}]")
    lines.append("WINDOW:\n" + lw)
    lines.append("FOCUS:\n" + focus)
    pros = [p for p in it.get("pros", []) if not (it["lw0"] <= p[0] < it["lw1"])][:2]
    if pros:
        lines.append("PROSPECTIVITY (other sentences of this opinion):")
        for p in pros:
            lines.append("  - " + p[2][:300])
    return "\n".join(lines)


def load_items(res_dir, ids=None):
    for f in sorted(glob.glob(os.path.join(res_dir, "*.items.jsonl.gz"))):
        repo = os.path.basename(f)[:-len(".items.jsonl.gz")]
        for line in gzip.open(f, "rt", encoding="utf-8"):
            it = json.loads(line)
            if ids is not None and it["id"] not in ids:
                continue
            it["repo"] = repo
            yield it


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default=os.path.join(WORK, "res2"))
    ap.add_argument("--select")
    ap.add_argument("--size", type=int, default=80)
    ap.add_argument("--start", type=int, default=0, help="number of the first pack")
    a = ap.parse_args()
    ids = None
    if a.select:
        ids = {l.split("\t")[0].strip() for l in open(a.select, encoding="utf-8") if l.strip()}
    os.makedirs(a.out, exist_ok=True)
    items = list(load_items(a.res, ids))
    # interleave repos so that a pack is not one court
    items.sort(key=lambda it: (zlib.crc32(it["id"].encode()) & 0xffff, it["id"]))
    with open(os.path.join(a.out, "index.tsv"), "a", encoding="utf-8", newline="\n") as fx:
        for k in range(0, len(items), a.size):
            n = a.start + k // a.size
            chunk = items[k:k + a.size]
            with open(os.path.join(a.out, f"pack_{n:03d}.txt"), "w", encoding="utf-8", newline="\n") as f:
                f.write("\n\n".join(render(it) for it in chunk) + "\n")
            for it in chunk:
                fx.write(f"{it['id']}\t{it['repo']}\t{n:03d}\n")
    print(len(items), "items in", (len(items) + a.size - 1) // a.size, "packs")


if __name__ == "__main__":
    main()
