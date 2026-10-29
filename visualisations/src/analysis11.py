"""Every law repo, metadata only (one git log per repo) -> analysis11.json
For each jurisdiction with dated history: acts per in-force year, adoption-to-force lag, in-force weekday and month,
coverage span, commit and file counts. Repos whose HEAD moves during the read are skipped (being rebuilt).
"""
import json, re, subprocess, statistics as st, sys
from collections import Counter
from datetime import date
from pathlib import Path

D = Path.home() / "Documents"
STABLE = {"germany": D / "law-in-motion/corpora/grundgesetz", "malta": D / "law-in-motion/corpora/malta-law"}
FORCE = re.compile(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4}-\d\d-\d\d)", re.M)
ADOPT = re.compile(r"^(?:Adopted|Enacted|Beschlossen|Made|Signed|Promulgated):\s*(\d{4}-\d\d-\d\d)", re.M)
SKIP_KIND = re.compile(r"^Kind:\s*(consolidated|unexplained|documentation|original|editorial)", re.M | re.I)
GENERIC = re.compile(r"^(Lexifina|Bundeskanzlei|Rechtsdienst|Riigi Teataja|Legimonaco|Service central|PIS RS|Retsinformation|Department of Justice|"
                     r"Legislation Unit|20\d\d edition|Grundgesetz \(1949\)|Diário da República \(INCM\))")


def git(p, *a, timeout=1200):
    try:
        return subprocess.run(["git", "-C", str(p), *a], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout).stdout
    except subprocess.TimeoutExpired:
        return ""


# Who made each act: parliament (laws, acts, codes) or the executive (decrees, ordinances, regulations, orders).
# Executive forms are tested first, so a decree-law ("Real Decreto-ley", "décret-loi") counts as executive.
EXECUTIVE = re.compile(r"arr[êe]t[ée]|d[ée]cret|ordonnance|decreto|real decreto|\borden\b|vyhl[áa][šs]ka|na[řr][íi]zen[íi]|verordnung|ordinance|"
                       r"regulation|\bdecree\b|\bуказ|постановлени|распоряжени|\bL\.N\.|\bS\.I\.|\bSL\b|bekendtg[øo]relse|asetus|regulamento|"
                       r"r[èe]glement|federal office ordinance|rules\b|\border\b|resolution|qərar|fərman|კანონქვემდებარე|ბრძანებ|დადგენილებ", re.I)
PARLIAMENT = re.compile(r"\bloi\b|\bley\b|z[áa]kon|gesetz|\bact\b|qanun|закон|\bФКЗ|\bФЗ|კანონ|ՀՕ|\blei\b|\blegge\b|\blaw\b|\blov\b|\blaki\b|"
                        r"zakon|ustav|constitution|konstitu|codice|code\b|statute|federal act|public law|pub\. l\.|ordinance \d+ of", re.I)


def classify(text, name=""):
    # Hong Kong and Gibraltar ordinances are passed by their legislatures
    if name in ("hong-kong", "gibraltar") and re.search(r"ordinance", text, re.I): return "parliament"
    if EXECUTIVE.search(text): return "executive"
    if PARLIAMENT.search(text): return "parliament"
    return "unclassified"


def stream_commits(p):
    """Yield one 'author\\x1fbody' record at a time, so a 187,000-commit history never sits in memory whole."""
    proc = subprocess.Popen(["git", "-C", str(p), "log", "--format=\x1e%an\x1f%B"], stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    buf = []
    for line in proc.stdout:
        if line.startswith("\x1e"):
            if buf: yield "".join(buf)
            buf = [line[1:]]
        else:
            buf.append(line)
    if buf: yield "".join(buf)
    proc.wait()


repos = {p.name.removesuffix("-law"): p for p in sorted(D.glob("*-law")) if p.is_dir()}
repos.update({p.name.removesuffix("-law"): p for p in sorted((D / "world-law-repos").glob("*-law")) if p.is_dir() and p.name.removesuffix("-law") not in repos})
repos.update({k: v for k, v in STABLE.items() if v.exists()})
for k in ("us-code-history", "uk-law-history"):
    if (D / k).exists(): repos[{"us-code-history": "united-states", "uk-law-history": "united-kingdom"}[k]] = D / k
repos["switzerland"] = D / "swiss-law"
for k in ("global", "swiss", "global-law-mcp", "germany"): repos.pop(k, None)
repos["germany"] = STABLE["germany"]
only = set(sys.argv[1:])
out = {}
for name, p in repos.items():
    if only and name not in only: continue
    head = git(p, "rev-parse", "HEAD").strip()
    if not head: continue
    n = int(git(p, "rev-list", "--count", "HEAD").strip() or 0)
    if n < 3: continue
    seen, years, lags, wd, mon = set(), Counter(), [], Counter(), Counter()
    awd, amon, dec_lags, dom = Counter(), Counter(), {}, Counter()
    maker = Counter()
    doy = Counter()
    maker_years, maker_lags = {"parliament": Counter(), "executive": Counter()}, {"parliament": [], "executive": []}
    for chunk in stream_commits(p):
        an, _, b = chunk.partition("\x1f")
        if GENERIC.match(an) or SKIP_KIND.search(b): continue
        f = FORCE.search(b)
        if not f: continue
        key = (an, f.group(1))
        if key in seen: continue
        seen.add(key)
        kind = re.search(r"^(?:Type|Kind|Act-type|Instrument):\s*(.+)$", b, re.M)
        who = classify(an + " " + (kind.group(1) if kind else ""), name)
        maker[who] += 1
        try:
            d = date.fromisoformat(f.group(1))
        except ValueError:
            continue
        if not (1800 <= d.year <= 2027): continue
        years[d.year] += 1; wd[d.weekday()] += 1; mon[d.month] += 1; dom[d.day] += 1
        if who in maker_years: maker_years[who][d.year] += 1
        doy[d.strftime("%m-%d")] += 1
        a = ADOPT.search(b)
        if a:
            try:
                ad = date.fromisoformat(a.group(1)); lag = (d - ad).days
                lags.append(lag); awd[ad.weekday()] += 1; amon[ad.month] += 1
                if who in maker_lags: maker_lags[who].append(lag)
                dec_lags.setdefault(ad.year // 10 * 10, []).append(lag)
            except ValueError: pass
    if git(p, "rev-parse", "HEAD").strip() != head:
        print(name, "moved during read, skipped"); continue
    if not seen: continue
    lags.sort()
    out[name] = {"commits": n, "files": len(git(p, "ls-files").splitlines()), "acts": len(seen), "years": dict(sorted(years.items())),
                 "weekday": [wd[i] for i in range(7)], "month": [mon[i] for i in range(1, 13)],
                 "lag": {"n": len(lags), "median": st.median(lags), "q1": lags[len(lags) // 4], "q3": lags[3 * len(lags) // 4],
                         "p05": lags[len(lags) // 20], "p95": lags[19 * len(lags) // 20], "within30": sum(0 <= x <= 30 for x in lags)} if len(lags) >= 5 else None,
                 "adopt_weekday": [awd[i] for i in range(7)], "adopt_month": [amon[i] for i in range(1, 13)],
                 "lag_by_decade": {str(k): {"n": len(v), "median": st.median(v)} for k, v in sorted(dec_lags.items()) if len(v) >= 10},
                 "dom": [dom[i] for i in range(1, 32)],
                 # Delay histogram on a log scale: same day, then bins of days 1, 2-3, 4-7, 8-15, ... up to 4 years and more
                 "lag_hist": [sum(1 for x in lags if x == 0)] + [sum(1 for x in lags if 2 ** (k - 1) <= x < 2 ** k) for k in range(1, 11)] + [sum(1 for x in lags if x >= 1024)],
                 "lag_neg": sum(1 for x in lags if x < 0), "lag_n": len(lags),
                 "maker": {k: maker[k] for k in ("parliament", "executive", "unclassified")},
                 "maker_years": {k: dict(sorted(v.items())) for k, v in maker_years.items()},
                 "maker_lag": {k: {"n": len(v), "median": st.median(v)} for k, v in maker_lags.items() if len(v) >= 10},
                 "doy": dict(sorted(doy.items()))}
    y = sorted(years)
    print(f"{name:16s} commits {n:7d} acts {len(seen):6d} {y[0]}-{y[-1]} lag {out[name]['lag'] and out[name]['lag']['median']}", flush=True)
prev = json.loads(Path("analysis11.json").read_text(encoding="utf-8")) if Path("analysis11.json").exists() else {}
if only: prev.update(out); out = prev
else:
    # A repo being rebuilt in place has no HEAD or moves mid-read; keep its last good reading rather than drop it
    for name, v in prev.items():
        if name not in out and name not in ("global", "swiss", "global-law-mcp"):
            out[name] = v; print(name, "kept from the last good read")
Path("analysis11.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(len(out), "jurisdictions with dated acts")
