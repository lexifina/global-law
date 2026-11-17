"""Households for a release pair: random (harness/gen.py) plus returns aimed at every changed rule.

usage: hist_cases.py OLD_DIR NEW_DIR YEAR n_random per_rule seed out.jsonl
Targeted cases: for each rule (regle/verif) added, removed or changed between the releases, the input boxes it reads
(old and new bodies, followed one level through the variables it uses) are found from tgv*.m; each case is a random
household plus 1-3 of those boxes (amounts log-normal, ticks 1, dates in the year), half of them with a high income."""
import json, os, re, sys, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
od, nd, year, nr, per, seed, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
random.seed(seed)
def load(d):
    rules, inputs, defs = {}, {}, {}
    for f in sorted(os.listdir(d)):
        if not f.endswith(".m") or f.startswith("tmp"): continue
        t = open(os.path.join(d, f), encoding="latin1").read().replace("\r", "")
        t = "\n".join(l for l in t.split("\n") if not l.lstrip().startswith("#"))
        if f.startswith("tgv"):
            for m in re.finditer(r"^([A-Z0-9_]+)\s*:\s*saisie\s+(\w+)(.*?);\s*$", t, re.M | re.S):
                al = re.search(r"\balias\s+([A-Z0-9]+)", m.group(3)); ty = re.search(r"\btype\s+(\w+)", m.group(3))
                if al: inputs[m.group(1)] = (al.group(1), m.group(2), ty.group(1) if ty else "REEL")
            continue
        for p in re.split(r"^(?=(?:regle|verif|cible)\b[^\n]*:\s*$)", t, flags=re.M):
            h = re.match(r"(regle|verif|cible)\b([^\n]*):", p)
            if not h: continue
            key = f"{h.group(1)} {h.group(2).strip()}"; body = " ".join(p.split())
            rules[key] = body
            for v in re.findall(r"(?:^|;|:)\s*([A-Z][A-Z0-9_]*)\s*(?:\[[^\]]*\])?\s*=(?!=)", body):
                defs.setdefault(v, set()).update(re.findall(r"\b[A-Z][A-Z0-9_]*\b", body))
    return rules, inputs, defs
RO, IO, DO = load(od); RN, IN, DN = load(nd)
inputs = {k: v for k, v in IN.items() if k in IO}       # boxes both releases accept
ch = [k for k in set(RO) | set(RN) if RO.get(k) != RN.get(k) and not k.startswith("cible")]
skip = {"REGCO", "ANREV", "V_ANREV", "V_REGCO", "V_IND_TRAIT", "V_NOTRAIT", "V_0AC", "V_0AM", "V_0AD", "V_0AO", "V_0AV",
        "V_0DA", "V_0DB", "V_0CF", "V_0CH"}
def boxes_of(key):
    ids = set(re.findall(r"\b[A-Z][A-Z0-9_]*\b", RO.get(key, "") + " " + RN.get(key, "")))
    one = set(ids)
    for v in ids:  # one level down through computed variables
        one |= DN.get(v, set()) if len(DN.get(v, ())) < 400 else set()
    return sorted(v for v in one if v in inputs and v not in skip)
def val(var):
    al, kind, ty = inputs[var]
    if ty.startswith("BOOL") or kind == "famille" and ty != "DATE_JJMMAAAA" and not ty.startswith("ENTIER") or al.startswith("0A"):
        return 1
    if ty == "DATE_JJMMAAAA": return int(f"{random.randint(1,28):02d}{random.randint(1,12):02d}{year}")
    if ty == "DATE_AAAA": return random.randint(year - 80, year - 18)
    if ty.startswith("ENTIER") and kind == "famille": return random.randint(1, 3)
    return gen.logn(5000, 1.3, 1, 2000000)
def base(i, tag):
    h = gen.household(i, year)
    b = {k: v for k, v in h["boxes"].items() if any(inputs[x][0] == k for x in ()) or True}
    return b
alias_ok = {a for a, _, _ in inputs.values()} | {f"0{c}{i}" for c in "FHJ" for i in range(10)}
n = 0
with open(out, "w") as f:
    def emit(b, tags):
        global n
        b = {k: v for k, v in b.items() if k in alias_ok}
        f.write(json.dumps({"id": f"c{n}", "year": year, "boxes": b, "tags": tags}) + "\n"); n += 1
    for i in range(nr):
        emit(gen.household(i, year)["boxes"], ["random"])
    stats = {}
    for key in sorted(ch):
        bx = boxes_of(key)
        stats[key] = len(bx)
        if not bx: continue
        for j in range(per):
            b = gen.household(n, year)["boxes"]
            if j % 2: b["1AJ"] = gen.logn(250000, 0.8, 60000, 3000000)
            for v in random.sample(bx, min(len(bx), random.randint(1, 3))):
                b[inputs[v][0]] = val(v)
            emit(b, ["rule:" + key])
print(f"{n} cases; changed rules {len(ch)}; with boxes {sum(1 for v in stats.values() if v)}", file=sys.stderr)
