"""Second rose round: per-act and per-file metadata from every local law repo (git log --name-status, no content).
    python -I roses2_scan.py <out.json>        resumable: repos already in out.json are skipped
"""
import json, re, subprocess, sys, time
from collections import Counter
from datetime import date
from pathlib import Path

D = Path.home() / "Documents"
OUT = Path(sys.argv[1])
FORCE = re.compile(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4}-\d\d-\d\d)", re.M)
ADOPT = re.compile(r"^(?:Adopted|Enacted|Beschlossen|Made|Signed|Promulgated):\s*(\d{4}-\d\d-\d\d)", re.M)
PUB = re.compile(r"^(?:Published|Publication|Publiziert|Gazetted):\s*(\d{4}-\d\d-\d\d)", re.M)
SKIP_KIND = re.compile(r"^Kind:\s*(consolidated|unexplained|documentation|original|editorial)", re.M | re.I)
GENERIC = re.compile(r"^(Lexifina|Bundeskanzlei|Rechtsdienst|Riigi Teataja|Legimonaco|Service central|PIS RS|Retsinformation|Department of Justice|"
                     r"Legislation Unit|20\d\d edition|Grundgesetz \(1949\)|Diário da República \(INCM\))")
SKIP_REPOS = {"romania", "global", "state", "swiss", "global-law-mcp"}

repos = {p.name.removesuffix("-law"): p for p in sorted(D.glob("*-law")) if p.is_dir()}
repos.update({p.name.removesuffix("-law"): p for p in sorted((D / "world-law-repos").glob("*-law")) if p.is_dir() and p.name.removesuffix("-law") not in repos})
if (D / "swiss-law").exists(): repos["switzerland"] = D / "swiss-law"
g = D / "law-in-motion/corpora/grundgesetz"
if g.exists(): repos["germany"] = g
for k in SKIP_REPOS: repos.pop(k, None)
repos = {k: v for k, v in repos.items() if not k.startswith("romania")}

def bin2(x, cap=11):  # 0 -> 0, then doubling bins 1, 2-3, 4-7, ...
    return 0 if x <= 0 else min(cap, x.bit_length())

def provision(path):
    return path.endswith(".md") and "/" in path and not path.rsplit("/", 1)[1].upper().startswith(("README", "REPRODUCE", "SOURCES", "LICENSE", "CHANGELOG"))

done = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
for name, p in repos.items():
    if name in done: continue
    t0 = time.time()
    head = subprocess.run(["git", "-C", str(p), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if not head:
        continue
    proc = subprocess.Popen(["git", "-C", str(p), "log", "--reverse", "--no-renames", "--name-status", "--format=\x1e%an\x1f%B\x1d"],
                            stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    pubwd, publag, adpub, size, rest, life = Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    mon_new, mon_rep, mon_amd = Counter(), Counter(), Counter()
    born, last, nver = {}, {}, Counter()
    seen = set(); acts = 0

    def handle(rec):
        global acts
        head_, _, files = rec.partition("\x1d")
        an, _, body = head_.partition("\x1f")
        if GENERIC.match(an) or SKIP_KIND.search(body): return
        f = FORCE.search(body)
        if not f: return
        try: d = date.fromisoformat(f.group(1))
        except ValueError: return
        if not (1800 <= d.year <= 2027): return
        ev = [l.split("\t", 1) for l in files.strip().splitlines() if "\t" in l]
        ev = [(s[0], path) for s, path in ev if provision(path)]
        if not ev: return
        key = (an, f.group(1)); first = key not in seen; seen.add(key)
        if first:
            acts += 1
            size[bin2(len(ev))] += 1
            kc = Counter(s for s, _ in ev)
            if kc["D"] > kc["A"] + kc["M"]: mon_rep[d.month] += 1      # mostly deletions: a repeal
            elif kc["A"] > kc["M"] + kc["D"]: mon_new[d.month] += 1    # mostly new provisions
            else: mon_amd[d.month] += 1
            pm = PUB.search(body); am = ADOPT.search(body)
            try:
                pd = date.fromisoformat(pm.group(1)) if pm else None
                ad = date.fromisoformat(am.group(1)) if am else None
            except ValueError:
                pd = ad = None
            if pd and 1800 <= pd.year <= 2027:
                pubwd[pd.weekday()] += 1
                if (d - pd).days >= 0: publag[bin2((d - pd).days)] += 1
                if ad and 0 <= (pd - ad).days < 20000: adpub[bin2((pd - ad).days)] += 1
        o = d.toordinal()
        for s, path in ev:
            if s == "A":
                born.setdefault(path, o); last[path] = o; nver[path] += 1
            elif s == "M":
                if path in last and o >= last[path]: rest[bin2(o - last[path], 15)] += 1
                last[path] = o; nver[path] += 1
            elif s == "D":
                if path in born and o >= born[path]: life[bin2((o - born[path]) // 365)] += 1
                born.pop(path, None); last.pop(path, None); nver.pop(path, None)

    buf = []
    for line in proc.stdout:
        if line.startswith("\x1e"):
            if buf: handle("".join(buf))
            buf = [line[1:]]
        else:
            buf.append(line)
    if buf: handle("".join(buf))
    proc.wait()
    if acts < 3:
        done[name] = None
    else:
        alive = [k for k in born]  # files still present (added by an act and never deleted)
        today = date(2026, 11, 7).toordinal()
        done[name] = {
            "acts": acts,
            "pub_wd": [pubwd[i] for i in range(7)], "pub_lag": [publag[i] for i in range(12)], "ad_pub": [adpub[i] for i in range(12)],
            "size": [size[i] for i in range(12)],
            "mon_new": [mon_new[i] for i in range(1, 13)], "mon_rep": [mon_rep[i] for i in range(1, 13)], "mon_amd": [mon_amd[i] for i in range(1, 13)],
            "rest": [rest[i] for i in range(16)], "life": [life[i] for i in range(12)],
            "born_dec": dict(Counter(str(max(1890, date.fromordinal(born[k]).year // 10 * 10)) for k in alive)),
            "since": [c for c in (lambda C: [C[i] for i in range(12)])(Counter(bin2((today - last[k]) // 365) for k in alive))],
            "versions": [c for c in (lambda C: [C[i] for i in range(12)])(Counter(min(11, (nver[k] - 1).bit_length()) for k in alive))],
            "files": len(alive),
        }
    OUT.write_text(json.dumps(done, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(f"{name:40s} {acts if done[name] else 0:7d} acts {time.time() - t0:6.1f}s", flush=True)
print("DONE", sum(1 for v in done.values() if v))
