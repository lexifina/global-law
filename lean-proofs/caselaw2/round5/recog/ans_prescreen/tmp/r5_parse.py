import re, sys
def parse(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    items = {}
    cur = None
    for i, ln in enumerate(lines):
        if ln.startswith("### ITEM "):
            cur = ln[len("### ITEM "):].strip()
            items[cur] = {"W": "", "X": "", "Y": "", "window": None, "note": None}
            mode = None
            continue
        if cur is None:
            continue
        d = items[cur]
        if ln.startswith("W (the stating decision):"):
            d["W"] = ln; 
        elif ln.startswith("X (the earlier decision):"):
            d["X"] = ln
        elif ln.startswith("Y (the decision said to have done it):"):
            d["Y"] = ln
        elif ln.startswith("WINDOW:"):
            d["window"] = lines[i+1]
        elif ln.startswith("NOTE AT:"):
            d["note"] = lines[i+1]
    return items
if __name__ == "__main__":
    it = parse(sys.argv[1])
    print(len(it), list(it)[:3])
    for k in it:
        print(k, len(it[k]["window"] or ""), it[k]["X"][:70], "|", it[k]["Y"][:70])
