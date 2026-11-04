"""Romania against the world: per national corpus, start-day speed, who makes the law, and calendar habits -> cmp.json.
Uses the same act rule as global-law's analysis11.py (one act per author and in-force date) and its parliament/executive classifier."""
import json, re, subprocess, statistics as st
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
FORCE = re.compile(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4}-\d\d-\d\d)", re.M)
ADOPT = re.compile(r"^(?:Adopted|Enacted|Beschlossen|Made|Signed|Promulgated):\s*(\d{4}-\d\d-\d\d)", re.M)
PUB = re.compile(r"^Published:\s*(\d{4}-\d\d-\d\d)", re.M)
KIND = re.compile(r"^(?:Type|Kind|Act-type|Instrument):\s*(.+)$", re.M)
SKIP_KIND = re.compile(r"^Kind:\s*(consolidated|unexplained|documentation|original|editorial|publisher|correction|layout)", re.M | re.I)
GENERIC = re.compile(r"^(Lexifina|Bundeskanzlei|Rechtsdienst|Riigi Teataja|Legimonaco|Service central|PIS RS|Retsinformation|Department of Justice|"
                     r"Legislation Unit|20\d\d edition|Grundgesetz \(1949\)|Diário da República \(INCM\)|Portalul legislativ)")
EXECUTIVE = re.compile(r"arr[êe]t[ée]|d[ée]cret|ordonnance|decreto|real decreto|\borden\b|vyhl[áa][šs]ka|na[řr][íi]zen[íi]|verordnung|ordinance|"
                       r"regulation|\bdecree\b|\bуказ|постановлени|распоряжени|\bL\.N\.|\bS\.I\.|\bSL\b|bekendtg[øo]relse|asetus|regulamento|"
                       r"r[èe]glement|federal office ordinance|rules\b|\border\b|resolution|qərar|fərman|\bHG\b|\bOUG\b|\bOG\b|hot[ăa]r[âa]re|ordonan[țt]", re.I)
PARLIAMENT = re.compile(r"\bloi\b|\bley\b|z[áa]kon|gesetz|\bact\b|qanun|закон|\bФКЗ|\bФЗ|\blei\b|\blegge\b|\blaw\b|\blov\b|\blaki\b|legea|"
                        r"zakon|ustav|constitution|konstitu|codice|code\b|statute|federal act|public law|pub\. l\.|ordinance \d+ of", re.I)

SE = {"romania", "albania", "bosnia-and-herzegovina", "bulgaria", "croatia", "greece", "kosovo", "montenegro", "north-macedonia", "serbia", "slovenia", "moldova", "turkey"}
EU = {"austria", "belgium", "cyprus", "czechia", "denmark", "estonia", "finland", "france", "germany", "hungary", "ireland", "italy", "latvia", "lithuania",
      "luxembourg", "malta", "netherlands", "poland", "portugal", "slovakia", "spain", "sweden"}
EUROPE = {"united-kingdom", "switzerland", "norway", "iceland", "liechtenstein", "monaco", "andorra", "san-marino", "vatican-city", "ukraine", "belarus",
          "gibraltar", "faroe-islands", "aland", "greenland", "jersey", "guernsey", "isle-of-man", "georgia", "armenia", "azerbaijan", "russia"}
group = lambda c: "South-east Europe" if c in SE else "Rest of the EU" if c in EU else "Rest of Europe" if c in EUROPE else "Rest of the world"
corpora = [c for c in json.loads((HERE / "corpora.json").read_text(encoding="utf-8")) if c["path"].endswith("/national/acts")]


def classify(text, name):
    if name in ("hong-kong", "gibraltar") and re.search(r"ordinance", text, re.I): return "parliament"
    if EXECUTIVE.search(text): return "executive"
    if PARLIAMENT.search(text): return "parliament"
    return "unclassified"


def read(c):
    d = HERE / "clones" / f"{c['repo']}.git"
    if not d.exists(): return None
    name = c["path"].split("/")[0]
    log = subprocess.run(["git", "-C", str(d), "log", "--format=\x1e%an\x1f%B"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    seen, lag, plag, maker, md, wd = set(), [], [], Counter(), Counter(), Counter()
    for rec in log.split("\x1e")[1:]:
        an, _, b = rec.partition("\x1f")
        if GENERIC.match(an) or SKIP_KIND.search(b): continue
        f = FORCE.search(b)
        if not f or (an, f.group(1)) in seen: continue
        seen.add((an, f.group(1)))
        try: fd = date.fromisoformat(f.group(1))
        except ValueError: continue
        if not 1990 <= fd.year <= 2026: continue
        k = KIND.search(b)
        maker[classify(an + " " + (k.group(1) if k else ""), name)] += 1
        md[f.group(1)[5:]] += 1; wd[fd.weekday()] += 1
        a, p = ADOPT.search(b), PUB.search(b)
        try:
            if a: lag.append((fd - date.fromisoformat(a.group(1))).days)
            if p: plag.append((fd - date.fromisoformat(p.group(1))).days)
        except ValueError: pass
    n = sum(md.values())
    if n < 30: return None
    ok = [x for x in lag if x >= 0]; pk = [x for x in plag if x >= 0]
    return {"country": name, "group": group(name), "acts": n,
            "lag_median": st.median(ok) if len(ok) >= 20 else None, "lag_n": len(ok),
            "pub_same_day": sum(1 for x in pk if x == 0) / len(pk) if len(pk) >= 20 else None, "pub_3": sum(1 for x in pk if x == 3) / len(pk) if len(pk) >= 20 else None, "pub_n": len(pk),
            "executive": maker["executive"] / max(1, maker["executive"] + maker["parliament"]), "classified": maker["executive"] + maker["parliament"],
            "jan1": md["01-01"] / n, "first": sum(v for k, v in md.items() if k.endswith("-01")) / n, "dec": sum(v for k, v in md.items() if k.startswith("12-")) / n,
            "weekend": (wd[5] + wd[6]) / n}


with ThreadPoolExecutor(8) as ex:
    res = [r for r in ex.map(read, corpora) if r]
res.sort(key=lambda r: -r["acts"])
(HERE / "cmp.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
print(len(res), "national corpora with 30+ dated acts", Counter(r["group"] for r in res))
for r in res:
    if r["group"] == "South-east Europe" or r["acts"] > 3000:
        print(f'{r["country"]:20s} {r["group"][:10]:10s} acts {r["acts"]:6d} lag {r["lag_median"]} same-day {r["pub_same_day"] and round(r["pub_same_day"],2)} '
              f'3d {r["pub_3"] and round(r["pub_3"],2)} exec {r["executive"]:.2f} ({r["classified"]}) jan1 {r["jan1"]:.2f} first {r["first"]:.2f} dec {r["dec"]:.2f} wkend {r["weekend"]:.2f}')
