"""Data for part three of the Romania page -> part3_data.json. One section per chart; each prints the numbers its caption quotes."""
import csv, json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
laws = list(csv.DictReader((HERE / "tip" / "data" / "laws.csv").open(encoding="utf-8")))
out = {}

# 14. Every day of the Monitorul Oficial, 2014-2025: [total, HG, Legea, OUG, OG, other] per publication day
KIND = ["HG", "Legea", "OUG", "OG"]
cal = defaultdict(lambda: [0] * 6)
for x in laws:
    p = x["published"]
    if not p or not ("2014-01-01" <= p <= "2025-12-31"): continue
    k = x["label"].split(" nr.")[0]
    row = cal[p]; row[0] += 1; row[1 + KIND.index(k) if k in KIND else 5] += 1
out["cal"] = dict(cal)
wd, mo = Counter(), Counter()
for d, v in cal.items(): wd[date.fromisoformat(d).strftime("%A")] += v[0]; mo[d[5:7]] += v[0]
print("14 acts", sum(v[0] for v in cal.values()), "weekday", wd.most_common(), "months", mo.most_common(3))

# 15. Government decisions that name a county, by topic, on a hex tile map: (col,row) in odd-r offset, plate code
import re
HEX = {"Satu Mare": (2, 0, "SM"), "Maramureș": (3, 0, "MM"), "Suceava": (4, 0, "SV"), "Botoșani": (5, 0, "BT"),
       "Bihor": (1, 1, "BH"), "Sălaj": (2, 1, "SJ"), "Bistrița-Năsăud": (3, 1, "BN"), "Neamț": (4, 1, "NT"), "Iași": (5, 1, "IS"),
       "Arad": (1, 2, "AR"), "Cluj": (2, 2, "CJ"), "Mureș": (3, 2, "MS"), "Harghita": (4, 2, "HR"), "Bacău": (5, 2, "BC"), "Vaslui": (6, 2, "VS"),
       "Timiș": (0, 3, "TM"), "Hunedoara": (1, 3, "HD"), "Alba": (2, 3, "AB"), "Sibiu": (3, 3, "SB"), "Brașov": (4, 3, "BV"), "Covasna": (5, 3, "CV"), "Vrancea": (6, 3, "VN"), "Galați": (7, 3, "GL"),
       "Caraș-Severin": (1, 4, "CS"), "Gorj": (2, 4, "GJ"), "Vâlcea": (3, 4, "VL"), "Argeș": (4, 4, "AG"), "Dâmbovița": (5, 4, "DB"), "Prahova": (6, 4, "PH"), "Buzău": (7, 4, "BZ"), "Brăila": (8, 4, "BR"), "Tulcea": (9, 4, "TL"),
       "Mehedinți": (1, 5, "MH"), "Dolj": (2, 5, "DJ"), "Olt": (3, 5, "OT"), "Teleorman": (4, 5, "TR"), "Ilfov": (5, 5, "IF"), "Ialomița": (6, 5, "IL"), "Constanța": (8, 5, "CT"),
       "Giurgiu": (5, 6, "GR"), "București": (6, 6, "B"), "Călărași": (7, 6, "CL")}
N = lambda s: s.replace("ţ", "ț").replace("ş", "ș").replace("Ţ", "Ț").replace("Ş", "Ș")
pat = {k: re.compile(r"jude[țt](ul|ului)?\s+" + re.escape(k) + r"\b" + (r"|municipiul(ui)? București" if k == "București" else ""), re.I) for k in HEX}
def topic(t):
    t = t.lower()
    if "prefect" in t: return "prefect"
    if re.search(r"\bstem|steag|sigiliu", t): return "arms"
    if re.search(r"fondul de (rezervă|intervenți)|alocarea unei sume|ajutoare de urgență|calamit", t): return "money"
    if re.search(r"domeniul(ui)? (public|privat)|inventarul|transmiter|trecer|în administrare|concesiune", t): return "property"
    if re.search(r"expropri|utilitate public|indicatori tehnico|obiectiv", t): return "works"
    return "other"
TOP = ["prefect", "arms", "property", "works"]
cnt = {k: Counter() for k in HEX}; tot = Counter(); yrs = Counter()
for x in laws:
    if not x["label"].startswith("HG"): continue
    t = N(x["title"]); ks = [k for k, p in pat.items() if p.search(t)]
    if not ks: continue
    tp = topic(t); tot[tp] += 1; yrs[x["published"][:4]] += 1
    for k in ks: cnt[k][tp] += 1
out["hex"] = {k: [c, r, code, [cnt[k][tp] for tp in TOP]] for k, (c, r, code) in HEX.items()}
print("15 decisions naming a county", sum(tot.values()), dict(tot), "years", sorted(yrs.items()))
for i, tp in enumerate(TOP): print("  ", tp, sorted(((v[3][i], k) for k, v in out["hex"].items()), reverse=True)[:6], "min", min(v[3][i] for v in out["hex"].values()))

# 16. What Parliament's laws are for: every law the corpus holds (lege/<year>/<n>), by the purpose its title states,
# or, for the 768 whose heading is only "Legea nr. X/Y", by what its first article does. Inside the number Parliament passed that year.
import unicodedata
fold = lambda s: "".join(c for c in unicodedata.normalize("NFD", N(s).lower()) if unicodedata.category(c) != "Mn")
def by_title(s):
    s = fold(s)
    if re.match(r"(pentru|privind) (aprobarea|respingerea)( cu modificari( si completari)?)? a? ?(ordonantei|ordonantelor)", s): return "ordinance"
    if re.match(r"(pentru|privind) (ratificarea|aderarea|acceptarea|aprobarea (acordului|conventiei|protocolului|memorandumului|amendamentului|tratatului|aderarii))", s): return "treaty"
    if re.match(r"(pentru|privind) (modificarea|completarea|abrogarea|prorogarea|suspendarea|interpretarea)", s): return "amend"
    if re.search(r"(instituirea|declararea|consacrarea|proclamarea) (zilei|anului|saptamanii|lunii)|\bziua\b|^(privind|pentru) (trecerea|transmiterea|darea in administrare|infiintarea comunei)|bugetul|contului general", s): return "other"
    return "new"
def by_text(t):
    b = " ".join(fold(t).split("\n")[1:])[:1500]
    if re.search(r"se (aproba|respinge)[^.]{0,80}ordonant", b): return "ordinance"
    if re.search(r"se ratifica|se aproba aderarea|se accepta|\badera la", b): return "treaty"
    if re.match(r"\s*(legea|ordonanta|codul|hotararea|decretul|anexa)\b", b) and re.search(r"se modifica|se completeaza|se abroga|se proroga", b): return "amend"
    return "new"
PUR = ["new", "amend", "ordinance", "treaty", "other"]
held = defaultdict(Counter); how = Counter()
for f in (HERE / "tip" / "lege").glob("*/*/README.md"):
    y = f.parts[-3]
    if not ("1991" <= y <= "2025"): continue
    h = N(f.open(encoding="utf-8").readline()[2:].strip())
    m = re.match(r"Legea(-cadru)? nr\. [\d.]+/\d{4}\s*(.*)", h); s = m.group(2) if m else re.sub(r"(Legea|nr\.) ?|[\d.]+/\d{4}", "", h)
    if s.strip(): p = by_title(s); how["title"] += 1
    else:
        arts = sorted(x for x in f.parent.glob("*.md") if x.name != "README.md")
        if not arts: how["no text"] += 1; continue
        p = by_text(arts[0].read_text(encoding="utf-8")); how["first article"] += 1
    held[y][p] += 1
ISS = json.loads((HERE / "ro_data2.json").read_text(encoding="utf-8"))["issued"]["Legea"]
out["purpose"] = [[int(y), ISS[str(y)]["issued"]] + [held[str(y)][p] for p in PUR] for y in range(1991, 2026)]
T = Counter(); [T.update(held[y]) for y in held]
R = Counter(); [R.update(held[str(y)]) for y in range(2017, 2026)]
print("16 laws held 1991-2025", sum(T.values()), dict(T), how, "| 2017-2025", dict(R), f"new share {R['new']/sum(R.values()):.1%}")
print("   1991-2000", {p: sum(held[str(y)][p] for y in range(1991, 2001)) for p in PUR}, "| peaks", sorted(((v[1], v[0]) for v in out["purpose"]), reverse=True)[:3])
for y in (2001, 2023): print("  ", y, out["purpose"][y - 1991])

# 17. The Fiscal Code (Legea 227/2015), article by article: changes, year of the current wording, inserted (^), repealed in full
FD = HERE / "tip" / "lege" / "2015" / "227"
TITLES = [(1, "I", "General provisions"), (13, "II", "Corporate profit tax"), (47, "III", "Microenterprise tax"), (58, "IV", "Income tax"),
          (135, "V", "Social contributions"), (221, "VI", "Non-residents"), (265, "VII", "Value added tax"), (335, "VIII", "Excise duties"),
          (453, "IX", "Local taxes"), (496, "X", "Construction tax"), (501, "XI", "Final provisions")]
fis = []
for l in (FD / "README.md").read_text(encoding="utf-8").splitlines():
    if not l.startswith("| Art"): continue
    c = [x.strip() for x in l.split("|")]
    lab, fn, n, last = c[1], re.search(r"\((.*?)\)", c[2]).group(1), int(c[3]), c[4]
    base = int(re.match(r"Art\. (\d+)", lab).group(1)); ti = max(i for i, t in enumerate(TITLES) if t[0] <= base)
    body = (FD / fn).read_text(encoding="utf-8").split("\n", 1); body = body[1].strip() if len(body) > 1 else ""
    fis.append([lab[5:], ti, n, int(last[:4]) if last else 0, int("^" in lab), int(bool(re.fullmatch(r"Abrogat[ăa]?\.?", body)))])
out["fiscal_q"] = {"titles": [[t[1], t[2]] for t in TITLES], "arts": fis}
orig = [a for a in fis if a[2] == 0 and not a[4]]
print("17 fiscal code articles", len(fis), "original", len(orig), f"{len(orig)/len(fis):.0%}", "inserted", sum(a[4] for a in fis), "repealed", sum(a[5] for a in fis),
      "| wording from 2025-26", sum(1 for a in fis if a[3] >= 2025), "| top", sorted(fis, key=lambda a: -a[2])[:4])
for i, t in enumerate(TITLES):
    A = [a for a in fis if a[1] == i]; o = sum(1 for a in A if a[2] == 0 and not a[4])
    print(f"   {t[1]:4} {t[2]:22} {len(A):4} original {o:3} {o/len(A):4.0%} ins {sum(a[4] for a in A):3} rep {sum(a[5] for a in A):3} changes {sum(a[2] for a in A):4} mean {sum(a[2] for a in A)/len(A):.1f}")

# 18. Who rewrites the most-amended acts: amending commits by the kind of act that made them, into the 14 acts with the most
recs = json.loads((HERE / "recs.json").read_text(encoding="utf-8"))
INST = {"Legea": "law", "Legea-cadru": "law", "OUG": "oug", "OG": "og", "Decizia": "ccr", "Portalul": "portal"}
GLOSS = {"Legea nr. 95/2006": "Health reform", "Codul fiscal 2003": "Fiscal Code of 2003", "Codul fiscal": "Fiscal Code of 2015", "Legea nr. 1/2011": "National education",
         "OUG nr. 195/2002": "Road traffic", "Legea nr. 50/1991": "Building permits", "Codul de procedură penală din 1968": "Criminal Procedure Code 1968",
         "Codul de procedură civilă din 1865": "Civil Procedure Code 1865", "Codul muncii": "Labour Code", "Legea nr. 263/2010": "Public pensions",
         "Legea nr. 448/2006": "Rights of disabled people", "Legea nr. 69/2000": "Physical education and sport", "Legea nr. 123/2012": "Electricity and gas",
         "Codul de procedură fiscală": "Fiscal Procedure Code"}
flows = defaultdict(Counter)
for x in recs:
    if not x["affecting"] or x["as_enacted"]: continue
    m = re.match(r"(.+?) (Art\.|Anexa|Annex|Articolul|Preamble|Title|Titlul|Capitolul|Partea|Cartea|Punctul|Pct)", x["affecting"][0])
    flows[m.group(1) if m else x["affecting"][0]][INST.get(re.split(r" nr\.| ", x["author"])[0], "other")] += 1
topk = sorted(flows, key=lambda t: -sum(flows[t].values()))[:14]
assert set(topk) == set(GLOSS), set(topk) ^ set(GLOSS)
status = {a["short"]: a["status"] for a in json.loads((HERE / "tip" / "data" / "acts.json").read_text(encoding="utf-8"))["acts"]}
IK = ["law", "oug", "og", "ccr", "portal", "other"]
out["sankey"] = [[t, GLOSS[t], status.get(t, ""), [flows[t][k] for k in IK]] for t in topk]
S = Counter(); [S.update(flows[t]) for t in topk]
print("18 amending commits into the top 14", sum(S.values()), dict(S), "| all acts", sum(sum(f.values()) for f in flows.values()))
for t in topk: f = flows[t]; print(f"   {sum(f.values()):4} {t:38} law {f['law']:3} oug {f['oug']:3} og {f['og']:3} ccr {f['ccr']} portal {f['portal']:3} {'OUG>law' if f['oug'] > f['law'] else ''}")

(HERE / "part3_data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
