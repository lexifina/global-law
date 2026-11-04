"""Data for part four of the Romania page -> part4_data.json. One section per chart; each prints the numbers its caption quotes."""
import json, re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
recs = json.loads((HERE / "recs.json").read_text(encoding="utf-8"))
D = lambda s: date.fromisoformat(s[:10])
kind_of = lambda a: re.split(r" nr\.| ", a)[0]
out = {}

# 19. The Fiscal Code's own notice rule (art. 4): every dated change to Legea 227/2015 made by a law or an ordinance,
# [kind, published, in force, lag in days, amending act]
spiral = []
for x in recs:
    if x["as_enacted"] or not x["affecting"] or not re.match(r"Codul fiscal (Art|Anexa|Annex|Titl)", x["affecting"][0]): continue
    k = kind_of(x["author"])
    if k not in ("Legea", "OUG", "OG") or not x["published"] or not x["in_force"]: continue
    spiral.append([k, x["published"][:10], x["in_force"][:10], (D(x["in_force"]) - D(x["published"])).days, x["author"]])
out["spiral"] = sorted(spiral, key=lambda s: s[2])
for k, need in (("Legea", 182), ("OUG", 15), ("OG", 15)):
    L = [s[3] for s in spiral if s[0] == k]
    print(f"19 {k}: {len(L)} changes, {sum(l >= need for l in L)} with {need}+ days, {sum(l == 0 for l in L)} same day, median {sorted(L)[len(L)//2]}, 1 Jan {sum(1 for s in spiral if s[0]==k and s[2][5:]=='01-01')}")
print("   acts", len({s[4] for s in spiral}), "longest", sorted(spiral, key=lambda s: -s[3])[:2])

# 20. Every act in the corpus as a seed, oldest at the centre: one character per act (kind*3 + status), versions for the amended ones
acts = json.loads((HERE / "tip" / "data" / "acts.json").read_text(encoding="utf-8"))["acts"]
KI = {"lege": 0, "oug": 1, "og": 2, "hg": 3}; ST = lambda s: 0 if s == "in force" else 1 if s == "amending act" else 2
A = sorted((a for a in acts if a["from"]), key=lambda a: (a["from"], KI.get(a["kind"], 4)))
out["seeds"] = {"code": "".join("0123456789abcde"[KI.get(a["kind"], 4) * 3 + ST(a["status"])] for a in A),
                "ver": {i: a["versions"] for i, a in enumerate(A) if a["versions"] > 1},
                "years": {y: next(i for i, a in enumerate(A) if a["from"] >= f"{y}-01-01") for y in range(1990, 2027)},
                "top": [[i, a["short"], a["versions"]] for i, a in sorted(enumerate(A), key=lambda p: -p[1]["versions"])[:3]]}
inf = [a for a in A if a["status"] == "in force"]
print("20 acts", len(A), "| in force", len(inf), "median from", inf[len(inf) // 2]["from"], "before 2000", sum(a["from"] < "2000" for a in inf),
      "| amending acts", sum(a["status"] == "amending act" for a in A), "| repealed or withdrawn", sum(ST(a["status"]) == 2 for a in A))
for k, i in KI.items():
    X = [a for a in A if a["kind"] == k]; print(f"   {k}: {len(X)}, amended {sum(a['versions'] > 1 for a in X)} ({sum(a['versions'] > 1 for a in X)/len(X):.0%}), in force {sum(a['status']=='in force' for a in X)}")
print("   years", out["seeds"]["years"], "top", out["seeds"]["top"])

# 21. How far back each amendment reaches: arcs from the year the amended act took effect to the year the change did,
# Parliament above (Legea), government below (OUG, OG, HG); [from year (1989 = earlier), to year, side, count]
frm = {a["short"]: a["from"] for a in acts if a["from"]}
def target(s):
    m = re.match(r"(.+?) (Art\.|Anexa|Annex|Articolul|Preamble|Title|Titlul|Capitolul|Partea|Cartea|Punctul|Pct)", s); return m.group(1) if m else s
SIDE = {"Legea": 0, "Legea-cadru": 0, "OUG": 1, "OG": 1, "HG": 1}
arcs = Counter(); recent = Counter(); old = Counter()
for x in recs:
    if x["as_enacted"] or not x["affecting"] or not x["in_force"]: continue
    t = target(x["affecting"][0]); f = frm.get(t); sd = SIDE.get(kind_of(x["author"]))
    if not f or sd is None: continue
    arcs[(max(1989, int(f[:4])), int(x["in_force"][:4]), sd)] += 1
    if x["in_force"] >= "2020": recent[sd] += 1; old[sd] += f < "2007"
    if x["in_force"] >= "2020" and f < "1997": old[t] += 1
out["arcs"] = [[a, b, sd, n] for (a, b, sd), n in sorted(arcs.items()) if b >= 1990]
print("21 arcs", len(out["arcs"]), "changes", sum(n for *_, n in out["arcs"]), "| since 2020 by side", dict(recent), "pre-2007 targets", {k: old[k] for k in (0, 1)},
      f"share {(old[0]+old[1])/(recent[0]+recent[1]):.0%}", "| oldest amended since 2020", [(k, v) for k, v in old.most_common() if isinstance(k, str)][:6])

# 22. Who amends whom: a directed matrix from the kind of the amending act to the kind of the amended act
kof = {a["short"]: a["kind"] for a in acts}
SRC = {"Legea": 0, "Legea-cadru": 0, "OUG": 1, "OG": 2, "HG": 3, "Decizia": 4}; TGT = {"lege": 0, "oug": 1, "og": 2, "hg": 3, "cod": 5, "constitutie": 5, "decret-lege": 5}
mat = [[0] * 6 for _ in range(6)]
for x in recs:
    if x["as_enacted"] or not x["affecting"]: continue
    i = SRC.get(kind_of(x["author"])); j = TGT.get(kof.get(target(x["affecting"][0])))
    if i is not None and j is not None: mat[i][j] += 1
out["chord"] = mat
col = lambda j: sum(mat[i][j] for i in range(6))
print("22 chord", sum(map(sum, mat)), "| HG<-HG", mat[3][3], "of", col(3), f"{mat[3][3]/col(3):.1%}", "| OUG->law", mat[1][0], "law->OUG", mat[0][1], "law->law", mat[0][0],
      "| law changes by govt", mat[1][0] + mat[2][0] + mat[3][0], "of", col(0), f"{(mat[1][0]+mat[2][0]+mat[3][0])/col(0):.0%}", "| CCR", sum(mat[4]), mat[4])

# 23. A ternary of the acts changed ten times or more by law, emergency ordinance or ordinance: [act, own kind, by law, by OUG, by OG]
TS = {"Legea": 0, "Legea-cadru": 0, "OUG": 1, "OG": 2}
tri = defaultdict(lambda: [0, 0, 0])
for x in recs:
    if x["as_enacted"] or not x["affecting"]: continue
    i = TS.get(kind_of(x["author"])); t = target(x["affecting"][0])
    if i is not None and kof.get(t) in ("lege", "oug", "og"): tri[t][i] += 1
out["tri"] = [[t, kof[t], *v] for t, v in sorted(tri.items(), key=lambda p: -sum(p[1])) if sum(v) >= 10]
T3 = out["tri"]
for k in ("lege", "oug", "og"):
    X = [r for r in T3 if r[1] == k]; sh = lambda r, j: r[2 + j] / sum(r[2:])
    print(f"23 {k}: {len(X)} acts, mean share law {sum(sh(r,0) for r in X)/len(X):.0%} oug {sum(sh(r,1) for r in X)/len(X):.0%} og {sum(sh(r,2) for r in X)/len(X):.0%}",
          "| majority law", sum(sh(r, 0) > .5 for r in X), "majority oug", sum(sh(r, 1) > .5 for r in X), "majority og", sum(sh(r, 2) > .5 for r in X))
print("   acts", len(T3), "max og share", max((r[4] / sum(r[2:]), r[0]) for r in T3), "| all-OUG", [r for r in T3 if r[2] == 0 and r[4] == 0])

(HERE / "part4_data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
