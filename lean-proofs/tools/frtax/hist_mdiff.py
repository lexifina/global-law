"""Rule-level diff of two M releases.
usage: hist_mdiff.py OLD_DIR NEW_DIR out.json
Splits every .m file into blocks ('regle N:', 'verif N:', 'cible X:', variable declarations of tgv*.m), normalises
whitespace and comments, and reports added / removed / changed blocks, with the variables each changed rule assigns."""
import re, sys, os, json, difflib
def blocks(d):
    out = {}
    for f in sorted(os.listdir(d)):
        if not f.endswith(".m") or f.startswith("tmp"): continue
        t = open(os.path.join(d, f), encoding="latin1").read().replace("\r", "")
        t = "\n".join(l for l in t.split("\n") if not l.lstrip().startswith("#"))
        if f.startswith("tgv"):
            for m in re.finditer(r"^([A-Z0-9_]+)\s*:(.*?;)\s*$", t, re.M | re.S):
                out[f"decl {m.group(1)}"] = (f, " ".join(m.group(2).split()))
            continue
        parts = re.split(r"^(?=(?:regle|verif|cible)\b[^\n]*:\s*$)", t, flags=re.M)
        for p in parts:
            h = re.match(r"(regle|verif|cible)\b([^\n]*):", p)
            if not h: continue
            key = f"{h.group(1)} {h.group(2).strip()}"
            body = " ".join(p.split())
            if key in out: key += f" @{f}"
            out[key] = (f, body)
    return out
def assigns(body):
    return sorted(set(re.findall(r"(?:^|;|:)\s*([A-Z][A-Z0-9_]*)\s*(?:\[[^\]]*\])?\s*=(?!=)", body)))
A = blocks(sys.argv[1]); B = blocks(sys.argv[2])
res = {"added": [], "removed": [], "changed": []}
for k in sorted(set(A) | set(B)):
    if k not in A: res["added"].append({"key": k, "file": B[k][0], "assigns": assigns(B[k][1]) if not k.startswith("decl") else []})
    elif k not in B: res["removed"].append({"key": k, "file": A[k][0], "assigns": assigns(A[k][1]) if not k.startswith("decl") else []})
    elif A[k][1] != B[k][1]:
        a, b = A[k][1], B[k][1]
        sm = difflib.SequenceMatcher(None, a.split(" "), b.split(" "))
        ops = [(t, " ".join(a.split(" ")[i1:i2]), " ".join(b.split(" ")[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
        res["changed"].append({"key": k, "file": B[k][0], "assigns": assigns(b), "ops": ops[:20]})
json.dump(res, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)
for t in res:
    kinds = {}
    for x in res[t]: kinds[x["key"].split()[0]] = kinds.get(x["key"].split()[0], 0) + 1
    print(t, len(res[t]), kinds)
