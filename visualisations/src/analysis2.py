"""Four agenda analyses on the real histories -> analysis2.json
  survival: how long a provision's wording lasts after it is written (Kaplan-Meier, censored at each corpus's end)
  readability: words per sentence of each version, by when it was drafted
  snapbacks: versions whose successor restores earlier wording (temporary law, found automatically)
  coamend: which Basic Law articles are amended by the same law
"""
import json, re, subprocess
from collections import defaultdict, Counter
from datetime import date
from itertools import combinations
from pathlib import Path

D = Path.home() / "Documents"
REPOS = {"de": ("law-in-motion/corpora/grundgesetz", r"^artikel/.+\.md$"), "ch": ("swiss-law", r"^(101|235.1|281.1)/art-.+\.md$"),
         "gb": ("uk-law-history", r"^(ukpga|uksi)/.+\.md$"), "us": ("us-code-history", r"^title-\d+/.+\.md$"),
         "ee": ("estonia-law", r"^(ps|rkvs|iks)/(?!README).+\.md$"), "li": ("liechtenstein-law", r"^(lv|vrg|stghg)/(?!README).+\.md$"),
         "lu": ("luxembourg-law", r"^(constitution|loi)/.+/(?!README)[^/]+\.md$"),
         "mc": ("monaco-law", r"^(constitution|loi-1362)/(?!README).+\.md$"), "sk": ("slovakia-law", r"^(ustava|volebny-zakon)/(?!README).+\.md$"),
         "si": ("slovenia-law", r"^(urs|zvdz)/(?!README).+\.md$"), "fi": ("finland-law", r"^perustuslaki/(?!README).+\.md$"),
         "hr": ("croatia-law", r"^ustav/(?!README).+\.md$"), "gi": ("gibraltar-law", r"^(constitution|stamp-duties)/(?!README|arrangement).+\.md$"),
         "dk": ("denmark-law", r"^(grundloven|skatteforvaltningsloven)/(?!README).+\.md$"), "kg": ("kyrgyzstan-law", r"^konstitutsiya-2021/(?!README).+[.]md$"), "it": ("italy-law", r"^costituzione/(?!README|allegati).+[.]md$"), "pt": ("portugal-law", r"^constituicao/(?!README).+[.]md$"), "mg": ("madagascar-law", r"^constitution/(?!README).+[.]md$"), "rw": ("rwanda-law", r"^(constitution|law-2020-017)/(?!README).+[.]md$"), "hk": ("hong-kong-law", r"^cap-\d+/(?!README).+\.md$")}
END = {"de": "2017-07-20", "ch": "2026-01-01", "gb": "2021-12-09", "us": "2026-04-01", "ee": "2026-10-01", "li": "2026-01-01", "lu": "2026-08-29"}
CONST = {"de": r"^artikel/", "ch": r"^101/", "ee": r"^ps/", "li": r"^lv/", "lu": r"^constitution/", "mc": r"^constitution/", "sk": r"^ustava/", "si": r"^urs/", "fi": r"^perustuslaki/", "hr": r"^ustav/", "gi": r"^constitution/", "dk": r"^grundloven/", "kg": r"^konstitutsiya-2021/", "it": r"^costituzione/", "pt": r"^constituicao/", "mg": r"^constitution/", "rw": r"^constitution/"}
ELECT = {"ee": r"^rkvs/", "sk": r"^volebny-zakon/", "si": r"^zvdz/"}
DOC = {"Lexifina", "Lexifina Watch"}
dd = date.fromisoformat


def git(repo, *a):
    return subprocess.run(["git", "-C", str(D / repo), *a], capture_output=True, text=True, encoding="utf-8").stdout


def body(t):
    t = re.sub(r"^---.*?---\s*", "", t, flags=re.S)
    t = re.sub(r"^#.*$", "", t, flags=re.M)
    return re.sub(r"\s+", " ", t).strip()


def label(code, f):
    if code == "de": return "Art. " + f.split("/")[1][:-3].lstrip("0")
    if code == "ch": a, b = f.split("/"); return f"{ {'101': 'BV', '235.1': 'DSG', '281.1': 'SCHKG'}.get(a, a) } Art. {b[4:-3].lstrip('0')}"
    if code == "gb": p = f.split("/"); return ("CFA s." if p[0] == "ukpga" else "SEND reg. ") + p[-1][:-3]
    if code == "us": t, s = f.split("/"); return f"{t[6:]} U.S.C. § {s[:-3]}"
    p = f.split("/"); n = re.sub(r"^(art|para|article|cl|par|clen|pykala|clanak|statya|artigo|s)[-_]0*", "", p[-1][:-3])
    return {"ee": {"ps": "PS § ", "rkvs": "RKVS § ", "iks": "IKS § "}, "li": {"lv": "LV Art. ", "vrg": "VRG Art. ", "stghg": "StGHG Art. "},
            "lu": {"constitution": "Const. art. ", "loi": "Loi 2020 art. "}, "mc": {"constitution": "Const. art. ", "loi-1362": "Loi 1.362 art. "},
            "sk": {"ustava": "Ústava čl. ", "volebny-zakon": "Election act § "}, "si": {"urs": "URS člen ", "zvdz": "ZVDZ člen "}, "fi": {"perustuslaki": "PL § "}, "hr": {"ustav": "Ustav čl. "}, "gi": {"constitution": "Const. s. ", "stamp-duties": "Stamp Duties s. "}, "dk": {"grundloven": "Grundloven § ", "skatteforvaltningsloven": "Skatteforvaltningsloven § "}, "hk": {"cap-486": "Cap. 486 s. ", "cap-383": "Cap. 383 s. "}, "kg": {"konstitutsiya-2021": "Konstitutsiya st. "}, "it": {"costituzione": "Costituzione art. "}, "pt": {"constituicao": "Constituição art. "}, "mg": {"constitution": "Constitution art. "}, "rw": {"constitution": "Constitution art. ", "law-2020-017": "Law 2020/017 art. "}}[code][p[0]] + n


out = {"survival": {}, "versions": {}, "snapbacks": [], "coamend": {}}
CACHE = Path(".build/a2cache"); CACHE.mkdir(parents=True, exist_ok=True)
for code, (repo, pat) in REPOS.items():
    # Per-repo results are cached by HEAD and pattern, so a round only recomputes repos that changed
    head = git(repo, "rev-parse", "HEAD").strip()
    ckey = CACHE / f"{code}-{head[:12]}-{__import__("hashlib").md5((pat + CONST.get(code, "") + ELECT.get(code, "")).encode()).hexdigest()[:8]}.json"
    if head and ckey.exists():
        part = json.loads(ckey.read_text(encoding="utf-8"))
        for k in ("survival", "versions"): out[k][code] = part[k]
        for k in ("survival_const", "const_growth", "elect"):
            if k in part: out.setdefault(k, {})[code] = part[k]
        out["snapbacks"] += part["snapbacks"]
        if "coamend" in part: out["coamend"] = part["coamend"]
        END[code] = part["end"]
        print(code, "cached", head[:10]); continue
    rx = re.compile(pat)
    commits = []
    for chunk in git(repo, "log", "--reverse", "--date=short", "--format=\x1e%H\x1f%an\x1f%ad\x1f%B", *(["--", "101", "235.1", "281.1"] if repo == "swiss-law" else [])).split("\x1e")[1:]:
        sha, an, ad, b = chunk.split("\x1f", 3)
        if an in DOC: continue
        m = re.search(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4}-\d\d-\d\d)", b, re.M)
        y = re.search(r"\((\d{4})\)", an)
        when = m.group(1) if m else (f"{y.group(1)}-06-30" if y else None)
        if when is None or when.startswith("1970"):
            when = f"{y.group(1)}-06-30" if y else when
        st_am = re.search(r"Stand am (\d{4}-\d\d-\d\d)", b)
        when = when or (st_am.group(1) if st_am else ad)
        names = [l.split("\t") for l in git(repo, "diff-tree", "--root", "--no-commit-id", "-r", "--name-status", sha).splitlines() if "\t" in l]
        commits.append({"sha": sha, "law": an, "date": when, "changes": [(n[0][0], n[-1]) for n in names if rx.match(n[-1])]})
    END[code] = min(max(c["date"] for c in commits if c["date"]), "2026-10-28")
    hist = defaultdict(list)  # file -> [(date, law, text or None, truncated_birth)]
    words_now, growth = {}, []
    crx = re.compile(CONST[code]) if code in CONST else None
    for i, c in enumerate(commits):
        snapshot = c["law"].startswith(("Bundeskanzlei", "2017 edition"))
        for st, f in c["changes"]:
            txt = None if st == "D" else body(git(repo, "show", f"{c['sha']}:{f}"))
            if hist[f] and hist[f][-1][2] == txt: continue  # metadata-only change
            hist[f].append((c["date"], c["law"], txt, snapshot and not hist[f]))
            if crx and crx.match(f):
                words_now[f] = len(re.findall(r"\w+", txt)) if txt else 0
        if crx and any(crx.match(f) for _, f in c["changes"]):
            growth.append({"date": c["date"], "words": sum(words_now.values()), "law": c["law"][:90]})
    if growth: out.setdefault("const_growth", {})[code] = growth
    # Amendment events per year, constitution against election law
    if code in ELECT:
        erx = re.compile(ELECT[code])
        ev = {"const": [], "elect": [], "n_const": len({f for f in hist if crx.match(f)}), "n_elect": len({f for f in hist if erx.match(f)}),
              "start_const": None, "start_elect": None}
        for grp, rx2 in (("const", crx), ("elect", erx)):
            births = [vs[0][0] for f, vs in hist.items() if rx2.match(f)]
            ev["start_" + grp] = min(births) if births else None
            for c2 in commits:
                if c2["law"].startswith(("Riigi Teataja",)) and not re.search(r"\d", c2["law"]): continue
                touched = [f for _, f in c2["changes"] if rx2.match(f)]
                if touched and c2["date"] != ev["start_" + grp]:
                    ev[grp].append({"date": c2["date"], "law": c2["law"][:80], "n": len(touched)})
        out.setdefault("elect", {})[code] = ev
    # Survival of each version written inside the window (left-truncated starts dropped)
    def km(only_const):
        spells = []
        for f, vs in hist.items():
            if only_const and not (crx and crx.match(f)): continue
            for k, (d0, law, txt, trunc) in enumerate(vs):
                if txt is None or trunc: continue
                if k + 1 < len(vs):
                    spells.append(((dd(vs[k + 1][0]) - dd(d0)).days, 1))
                else:
                    spells.append(((dd(END[code]) - dd(d0)).days, 0))
        spells = sorted((t, e) for t, e in spells if t >= 0)
        n, s, curve, at_risk, i = len(spells), 1.0, [[0, 1.0]], len(spells), 0
        while i < len(spells):
            t = spells[i][0]; ev = cen = 0
            while i < len(spells) and spells[i][0] == t:
                ev += spells[i][1]; cen += 1 - spells[i][1]; i += 1
            if ev:
                s *= 1 - ev / at_risk; curve.append([t, s])
            at_risk -= ev + cen
        med = next((t for t, v in curve if v <= .5), None)
        return {"curve": curve, "n": n, "events": sum(e for _, e in spells), "median_days": med,
                "max_days": max((t for t, _ in spells), default=0)}
    out["survival"][code] = km(False)
    if crx: out.setdefault("survival_const", {})[code] = km(True)
    n, med = out["survival"][code]["n"], out["survival"][code]["median_days"]
    # Versions for readability
    vers = []
    for f, vs in hist.items():
        for k, (d0, law, txt, trunc) in enumerate(vs):
            if txt and len(txt) > 60:
                vers.append({"p": label(code, f), "date": d0, "law": law, "orig": k == 0, "trunc": trunc, "text": txt})
    out["versions"][code] = vers
    # Snapbacks: a later version restores an earlier wording exactly
    for f, vs in hist.items():
        texts = [re.sub(r"\W", "", v[2]) if v[2] is not None else None for v in vs]
        for k in range(1, len(vs) - 1):
            for j in range(k + 1, len(vs)):
                if "edition" in vs[j][1] or "kopf" in f: continue
                if any(g in vs[k][1] + vs[j][1] for g in ("Riigi Teataja", "Rechtsdienst", "Bundeskanzlei", "Retsinformation", "Department of Justice")) and not re.search(r"\d", vs[k][1] + vs[j][1]): continue
                if texts[j] is not None and texts[j] == texts[k - 1] and texts[k] != texts[k - 1]:
                    out["snapbacks"].append({"c": code, "p": label(code, f), "from": vs[k][0], "to": vs[j][0], "law": vs[k][1], "end_law": vs[j][1],
                                             "days": (dd(vs[j][0]) - dd(vs[k][0])).days, "steps": j - k})
                    break
    if code == "de":
        pairs, deg = Counter(), Counter()
        for c in commits[1:]:
            arts = sorted({label(code, f) for _, f in c["changes"]})
            for a in arts: deg[a] += 1
            for a, b in combinations(arts, 2): pairs[(a, b)] += 1
        out["coamend"] = {"deg": deg, "pairs": [[a, b, n] for (a, b), n in pairs.items()]}
    print(code, "spells", n, "events", out["survival"][code]["events"], "median", med, "versions", len(vers))
    part = {"survival": out["survival"][code], "versions": out["versions"][code], "end": END[code],
            "snapbacks": [s for s in out["snapbacks"] if s["c"] == code]}
    for k in ("survival_const", "const_growth", "elect"):
        if code in out.get(k, {}): part[k] = out[k][code]
    if code == "de": part["coamend"] = out["coamend"]
    if head: ckey.write_text(json.dumps(part, ensure_ascii=False), encoding="utf-8")

# Readability: words per sentence
ABBR = r"\b(Art|Abs|Nr|Ziff|lit|bzw|vgl|S|ff|U\.S\.C|Sec|No|Pub|L|Stat|et seq|i\.e|e\.g|v|Inc|Co|U\.S)\."
def wps(t):
    t = re.sub(ABBR, lambda m: m.group(0).replace(".", "§"), t)
    t = re.sub(r"\b([a-zA-Z])\.\s(?=[a-z])", r"\1§ ", t)
    t = re.sub(r"(\d)\.", r"\1§", t)
    sents = [s for s in re.split(r"(?<=[.!?])\s+", t) if len(re.findall(r"\w+", s)) >= 3]
    if not sents: return None
    lens = [len(re.findall(r"\w+", s)) for s in sents]
    return sum(lens) / len(lens), max(lens)
read = []
for code, vs in out["versions"].items():
    for v in vs:
        r = wps(v["text"])
        if r: read.append({"c": code, "p": v["p"], "date": v["date"], "orig": v["orig"] and (code == "de" or not v["trunc"]), "base": v["trunc"], "wps": round(r[0], 1), "max": r[1], "words": len(re.findall(r"\w+", v["text"]))})
out["readability"] = read
del out["versions"]
Path("analysis2.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print("snapbacks", len(out["snapbacks"]))
for s in sorted(out["snapbacks"], key=lambda s: s["from"]): print(" ", s["c"], s["p"], s["from"], "->", s["to"], s["days"], "d |", s["law"][:60], "|", s["end_law"][:50])
