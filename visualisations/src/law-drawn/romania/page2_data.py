"""Data for "The Romanian Record", a second Romania page -> page2_data.json. One section per chart; each prints the numbers its caption quotes."""
import csv, difflib, json, re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
out = {}

# A. The Constitution of 1991 and its 2003 revision (Legea 429/2003): each 1991 article matched to its 2003 successor by text.
# Texts: zz_const/ (the corpus's 1991 and 2003 versions); the 1991 spelling (î inside words, sînt) is brought to the 1993 one before comparing.
C = json.loads((HERE / "zz_const" / "const.json").read_text(encoding="utf-8")); MT = json.loads((HERE / "zz_const" / "match.json").read_text(encoding="utf-8"))
old = {int(k): v for k, v in C["old"].items()}; new = {int(k): v for k, v in C["new"].items()}; M = {int(k): v for k, v in MT["M"].items()}
spell = lambda t: re.sub(r"(?<=\w)î(?=\w)", "â", t).replace("sînt", "sunt").replace("Sînt", "Sunt")
body = lambda t: "\n".join(t.split("\n")[1:])
T91 = [(1, 14), (15, 57), (58, 133), (134, 139), (140, 145), (146, 148), (149, 152)]
T03 = [(1, 14), (15, 60), (61, 134), (135, 141), (142, 147), (148, 149), (150, 152), (153, 156)]
tix = lambda n, T: next(i for i, (a, b) in enumerate(T) if a <= n <= b)
links = []
for i, (j, _) in M.items():
    r = difflib.SequenceMatcher(None, spell(body(old[i])), body(new[j]), autojunk=False).ratio()
    links.append([i, j, round(r, 3)])
cls = lambda r: 0 if r >= .995 else 1 if r >= .85 else 2 if r >= .5 else 3
gone = sorted(set(old) - set(M)); born = sorted(set(new) - {j for j, _ in M.values()})
out["const"] = {"old": [[n, MT["old"][str(n)], tix(n, T91)] for n in sorted(old)], "new": [[n, MT["new"][str(n)], tix(n, T03)] for n in sorted(new)],
                "links": sorted(links), "gone": gone, "born": born}
c = Counter(cls(r) for _, _, r in links)
print("A articles 1991", len(old), "2003", len(new), "| kept word for word", c[0], "lightly reworded", c[1], "reworded", c[2], "rewritten", c[3],
      "| renumbered", sum(1 for i, j, _ in links if i != j), "| removed", len(gone), "| new", len(born))
print("   removed", [(n, MT["old"][str(n)]) for n in gone]); print("   new", [(n, MT["new"][str(n)]) for n in born])
print("   rewritten", [(i, j, MT["new"][str(j)]) for i, j, r in links if cls(r) == 3])

# B. The Monitorul Oficial, Partea I, numbers its issues afresh each year: for every year, the highest issue number seen on each day
from datetime import date
MON = {m: i + 1 for i, m in enumerate(["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"])}
laws = list(csv.DictReader((HERE / "tip" / "data" / "laws.csv").open(encoding="utf-8")))
iss = defaultdict(dict)
for x in laws:
    m = re.search(r"Partea I, nr\. ([\d.]+)(?:\s*(?:bis|și|şi)[^,]*?)? din (\d{1,2}) (\w+) (\d{4})", x["title"])
    if not m or not MON.get(m.group(3).lower()): continue
    y = int(m.group(4))
    if not 1991 <= y <= 2025: continue
    try: doy = date(y, MON[m.group(3).lower()], int(m.group(2))).timetuple().tm_yday
    except ValueError: continue
    num = int(m.group(1).replace(".", "")); iss[y][doy] = max(iss[y].get(doy, 0), num)
out["mo"] = {y: sorted(v.items()) for y, v in sorted(iss.items())}
mx = {y: max(v.values()) for y, v in iss.items()}
print("B years", len(mx), "| max issue", {y: mx[y] for y in (1991, 1995, 2000, 2004, 2007, 2013, 2020, 2024, 2025)}, "| top", sorted(mx.items(), key=lambda kv: -kv[1])[:4],
      "| issues seen", sum(len(v) for v in iss.values()))

# C. Which ministries government decisions name, grouped into portfolios across their many renamings, and how many of those decisions move property
NZ = lambda s: s.replace("ţ", "ț").replace("ş", "ș").replace("Ţ", "Ț").replace("Ş", "Ș")
PF = [("Interior", r"Afacerilor Interne|Internelor|Administrației și Internelor"), ("Transport", r"Transporturilor|Lucrărilor Publice"), ("Defence", r"Apărării"),
      ("Economy and energy", r"Economiei|Energiei|Industri"), ("Environment, water and forests", r"Mediului|Apelor"), ("Agriculture", r"Agriculturii"),
      ("Education and research", r"Educației|Cercetării|Învățământului"), ("Health", r"Sănătății"), ("Justice", r"Justiției"), ("Culture", r"Culturii"),
      ("Regional development", r"Dezvoltării Regionale|Dezvoltării,|Dezvoltării$|Dezvoltării Lucrărilor"), ("Labour", r"Muncii"), ("Finance", r"Finanțelor"),
      ("Youth and sport", r"Tineretului|Sportului"), ("Foreign affairs", r"Afacerilor Externe"), ("EU funds", r"Fondurilor Europene|Proiectelor Europene"),
      ("Communications", r"Comunicațiilor"), ("Tourism", r"Turismului")]
PROP = re.compile(r"transmiter|trecer|darea în administrare|în administrarea|domeniul (public|privat)|inventarul|imobil", re.I)
mins = defaultdict(lambda: [0, 0]); names = defaultdict(Counter); nd = 0
for x in laws:
    if not x["label"].startswith("HG"): continue
    t = NZ(x["title"]).split(", publicat")[0]
    hit = set()
    for m in re.findall(r"Minister(?:ul|ului) ([A-ZĂÂÎȘȚ][^;()]{0,80})", t):
        for nm, pat in PF:
            if re.match(f"(?:{pat})", m): hit.add(nm); names[nm][re.split(r",| - | pentru | prin | la | în | din | și (?:a|al|trecerea|transmiterea) ", m)[0].strip()] += 1; break
    if not hit: continue
    nd += 1; pr = bool(PROP.search(t))
    for h in hit: mins[h][0 if pr else 1] += 1
out["mins"] = [[nm, *mins[nm], len([k for k, v in names[nm].items() if v >= 2])] for nm, _ in PF if nm in mins]
print("C decisions naming a ministry", nd, "| by portfolio", [(r[0], r[1] + r[2], f"{r[1]/(r[1]+r[2]):.0%} property", r[3], "names") for r in sorted(out["mins"], key=lambda r: -(r[1] + r[2]))][:8])
print("   property overall", sum(r[1] for r in out["mins"]), "of", sum(r[1] + r[2] for r in out["mins"]), "| transport names", names["Transport"].most_common(6))

# D. The codes as railway lines: every version date of each code the corpus holds, with its status
VJ = json.loads((HERE / "tip" / "data" / "versions.json").read_text(encoding="utf-8"))["acts"]; AJ = {x["slug"]: x for x in json.loads((HERE / "tip" / "data" / "acts.json").read_text(encoding="utf-8"))["acts"]}
ROWS = [("codul-civil-1864", "Civil Code of 1864"), ("codul-civil", "Civil Code"), ("codul-familiei-1953", "Family Code of 1953"), ("codul-procedura-civila-1865", "Civil Procedure Code of 1865"),
        ("codul-procedura-civila", "Civil Procedure Code"), ("codul-comercial-1887", "Commercial Code of 1887"), ("codul-penal-1969", "Criminal Code of 1968"), ("codul-penal", "Criminal Code"),
        ("codul-procedura-penala-1968", "Criminal Procedure Code of 1968"), ("codul-procedura-penala", "Criminal Procedure Code"), ("codul-fiscal-2003", "Fiscal Code of 2003"),
        ("codul-fiscal", "Fiscal Code"), ("legea-207-2015", "Fiscal Procedure Code"), ("codul-muncii", "Labour Code"), ("legea-86-2006", "Customs Code"), ("legea-46-2008", "Forestry Code"),
        ("legea-296-2004", "Consumer Code"), ("codul-administrativ", "Administrative Code"), ("legea-21-2020", "Air Code"), ("constitutia", "Constitution")]
out["codes"] = [[nm, AJ[s]["path"], AJ[s]["status"], [v["from"] for v in next(x for x in VJ if x["slug"] == s)["versions"]]] for s, nm in ROWS]
for nm, path, st, vs in out["codes"]:
    yrs = (date.fromisoformat(st[9:19] if st.startswith("repealed") else "2026-11-03") - date.fromisoformat(vs[0])).days / 365.25
    print(f"D {nm:32} {len(vs):4} versions {vs[0]} .. {vs[-1]} {st:24} {len(vs)/yrs:5.1f} a year over {yrs:5.1f} years")

(HERE / "page2_data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
