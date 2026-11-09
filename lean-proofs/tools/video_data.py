"""Package the real data the film draws: flags per jurisdiction and kind, and the proof dependency graphs Lean exported.

    lake env lean tools/DepTree.lean > tools/out/deptree.jsonl
    python tools/video_data.py      # -> video/data.json
"""
import collections, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "video" / "data.json"


def main():
    ref = json.loads((HERE / "out" / "certificates.json").read_text(encoding="utf-8"))["flags"]
    more = json.loads((HERE / "out" / "certificates_more.json").read_text(encoding="utf-8"))
    j = collections.defaultdict(lambda: {"ref": 0, "ref_cert": 0, "reen": 0, "pre": 0, "gap": 0, "para": 0})
    for r in ref:
        k = r["corpus"].split("/")[0]; j[k]["ref"] += 1; j[k]["ref_cert"] += r["certified"]; j[k]["reen"] += r["reenacted"]
    for key, name in (("prepub", "pre"), ("gaps", "gap"), ("paras", "para")):
        for r in more[key]:
            j[r["corpus"].split("/")[0]][name] += 1
    E = [json.loads(l) for l in (HERE / "out" / "deptree.jsonl").read_text(encoding="utf-8").splitlines() if l.startswith("{")]
    graphs = {}
    for root in sorted({e["root"] for e in E}):
        es = [e for e in E if e["root"] == root]
        depth = {root: 0}
        for e in sorted(es, key=lambda e: e["depth"]):
            depth.setdefault(e["to"], e["depth"] + 1)
        graphs[root] = {"nodes": [{"id": n, "depth": d} for n, d in depth.items()],
                        "edges": [[e["from"], e["to"]] for e in es]}
    data = {"jurisdictions": sorted(({"name": k, **v} for k, v in j.items()), key=lambda x: -(x["ref"] + x["pre"] + x["gap"] + x["para"])),
            "graphs": graphs,
            "totals": {"checked": len(ref) + sum(len(more[k]) for k in ("prepub", "gaps", "paras")),
                       "certified": sum(r["certified"] for r in ref) + sum(r["certified"] for k in ("prepub", "gaps", "paras") for r in more[k]),
                       "reenacted": sum(r["reenacted"] for r in ref)}}
    OUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(len(data["jurisdictions"]), "jurisdictions;", data["totals"], {k: len(v["nodes"]) for k, v in graphs.items()})


if __name__ == "__main__":
    main()
