"""Show diffs for one field, where the fields before it agree. usage: show.py workdir FIELD [n] [mvar...]"""
import json, sys
ORDER = ["NBPT", "RNG", "RNI", "IDRS", "IDEC", "ITRED", "CITOT", "IMPNET", "REVKIRE"]
work, field = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
extra = sys.argv[4:]
up = ORDER[:ORDER.index(field)] if field in ORDER else []
k = 0
for line in open(f"{work}/diffs.jsonl"):
    d = json.loads(line)
    if field not in d["bad"] or any(u in d["bad"] for u in up if u not in ("REVKIRE", "CITOT")):
        continue
    bx = {a: v for a, v in d["boxes"].items() if not a[:2] in ("0F", "0H", "0J")}
    print(d["id"], d["year"], bx)
    print("   lean:", {f: d["lean"].get(f) for f in ORDER + ["IDRSFULL", "PFU", "IAVCR"]})
    print("   M   :", {f: d["m"].get(f) for f in ["NBPT", "RNG", "RNI", "IDRS", "IDRS2", "IDEC", "ITRED", "CITOT", "IRN", "IINET", "IAN", "IMPNET", "REVKIRE"] + extra})
    k += 1
    if k >= n:
        break
