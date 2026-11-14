"""fjc8: show the cache windows of the citations of a district decision in an appellate opinion, + its end zone.

    python -X utf8 peek.py APP DISTRICT [--ends]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
from diag import BO, L  # noqa: E402


def main():
    a, d = int(sys.argv[1]), int(sys.argv[2])
    sidx = diag.shard_index()
    tag = sidx.get(a)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("app", a, L.node_row(a)[1:7])
    print("dis", d, L.node_row(d)[1:7])
    if tag is None:
        print("no shard")
        return
    path = os.path.join(L.CACHE, tag + ".jsonl.gz")
    for n, g in L.decisions(path):
        if n != a:
            continue
        for cw in g["cw"]:
            if cw["j"] != d:
                continue
            w0, wt = cw["w"]
            c0, c1 = cw["c"][0] - w0, cw["c"][1] - w0
            print("--- part", cw["part"], "rel", cw["rel"])
            print(wt[:c0] + "[[" + wt[c0:c1] + "]]" + wt[c1:])
        if "--ends" in sys.argv and g["z"]:
            z = g["z"]
            if z.get("full"):
                print("=== full:", z["head"][1][-1500:])
            else:
                print("=== open:", (z.get("open") or [0, ""])[1][:800])
                for e in z.get("ends") or []:
                    print("=== end", e[2], e[1][-700:])
        break


if __name__ == "__main__":
    main()
