"""One read-only pass per law repo: every provision file's life (created, amended, renamed, repealed) -> lives.json.
Also scans the current text of EU members for cited EU acts -> eu.json. Reads ~/Documents/*-law, never writes there."""
import json, re, subprocess, sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

D = Path.home() / "Documents"
OUT = Path(__file__).parent
SKIP_DIR = re.compile(r"^(data|tools|build|docs|\.github|scripts)/")
SNAP = re.compile(r"oldest version available|unexplained|consolidated|as in force on", re.I)
GENERIC = re.compile(r"^(Lexifina|Lexifina Builder)$")
EU = {"austria", "belgium", "bulgaria", "croatia", "cyprus", "czechia", "denmark", "estonia", "finland", "france", "germany", "greece",
      "hungary", "ireland", "italy", "latvia", "lithuania", "luxembourg", "malta", "netherlands", "poland", "portugal", "romania",
      "slovakia", "slovenia", "spain", "sweden"}


def law_file(p):
    return p.endswith(".md") and not SKIP_DIR.match(p) and p.rsplit("/", 1)[-1] not in ("README.md", "REPRODUCE.md", "CHANGELOG.md", "LICENSE.md")


def lives(name, p):
    head = subprocess.run(["git", "-C", str(p), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    proc = subprocess.Popen(["git", "-C", str(p), "-c", "core.quotepath=off", "log", "--reverse", "-M", "--name-status", "--date=short",
                             "--format=\x1e%ad\x1f%an\x1f%s"], stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    files = {}                     # path -> [created or None, [amend dates], repealed date or None]
    gone = []                      # lives of repealed files
    year_ev = defaultdict(Counter)  # year -> A/M/D/R
    day = defaultdict(lambda: [0, Counter()])  # date -> [provision events, subject counts]
    commit = None
    first_dated = None

    def flush():
        if not commit: return
        d, an, subj, rows = commit
        dated = d != "1970-01-01" and not GENERIC.match(an)
        snap = bool(SNAP.search(subj))
        n = 0
        for st, a, b in rows:
            if st == "A" and law_file(a):
                files[a] = [d if dated else None, [], None, snap]
                if dated: year_ev[d[:4]]["A"] += 1
            elif st == "M" and law_file(a):
                f = files.setdefault(a, [None, [], None, True])
                if dated: f[1].append(d); year_ev[d[:4]]["M"] += 1; n += 1
            elif st == "D" and law_file(a):
                f = files.pop(a, None)
                if f and dated: f[2] = d; f.append(a); gone.append(f); year_ev[d[:4]]["D"] += 1; n += 1
            elif st.startswith("R") and law_file(b):
                f = files.pop(a, None) or [None, [], None, True]
                if st != "R100" and dated: f[1].append(d)
                files[b] = f
                if dated: year_ev[d[:4]]["R"] += 1; n += 1
        if dated and n:
            day[d][0] += n; day[d][1][subj[:160]] += n

    for line in proc.stdout:
        line = line.rstrip("\n")
        if line.startswith("\x1e"):
            flush()
            d, an, subj = (line[1:].split("\x1f") + ["", ""])[:3]
            commit = (d, an, subj, [])
            if d != "1970-01-01" and not GENERIC.match(an) and (not first_dated or d < first_dated): first_dated = d
        elif line and commit:
            parts = line.split("\t")
            commit[3].append((parts[0], parts[1], parts[2] if len(parts) > 2 else None))
    flush(); proc.wait()
    if subprocess.run(["git", "-C", str(p), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() != head:
        print(name, "moved during read, skipped", flush=True); return None
    alive = [f + [p_] for p_, f in files.items()]
    last = max(day) if day else None
    top_days = sorted(((v[0], k, v[1].most_common(1)[0][0]) for k, v in day.items()), reverse=True)[:5]
    # Per-provision summaries only, so the JSON stays small: created, first amendment, amendment count, repealed
    rows = [[f[0], f[1][0] if f[1] else None, len(f[1]), f[2], f[3]] for f in alive + gone]
    most = sorted(((len(f[1]), f[4], f[1][0] if f[1] else None, f[1][-1] if f[1] else None, f[0]) for f in alive + gone), key=lambda t: t[0], reverse=True)[:3]
    print(f"{name:20s} provisions {len(rows):7d} alive {len(alive):7d} repealed {len(gone):6d} {first_dated}..{last}", flush=True)
    return {"rows": rows, "most": most, "years": {y: dict(c) for y, c in sorted(year_ev.items())}, "top_days": top_days,
            "first": first_dated, "last": last, "head": head}


EU_OLD = re.compile(r"(?<![\d/])(\d{2}|\d{4})/(\d{1,4})/(?:EC|EEC|EG|EWG|CE|CEE|EF|EØF|EY|ETY|ES|EHS|EK|EGK|EB|EO|EÜ|EMÜ|EZ|EGS|WE|EWG|EEG|EOK|KE|EGF|EØS|ЕО|ЕИО)\b")
EU_NEW = re.compile(r"\((?:EU|UE|ES|EÚ|EL|ЕС|EE|ΕΕ|AE)\)\s*(?:n\.?[ºo°]?\s*|No\.?\s*|č\.\s*|nr\.?\s*|Nr\.?\s*)?(20\d\d)/(\d{1,4})\b")


EU_PAREN = re.compile(r"\((EU|UE|ES|EÚ|EL|ЕС|EE|ΕΕ|AE|EC|CE|EG|EK|EY|EB|EO|EZ|WE|KE|EF|EÜ)\)\s*(?:[^\d\s]{1,4}\.?\s*)?(\d{1,4})/(\d{1,4})\b")


def eu_cites(name, p):
    # ASCII-only pattern for git; Python below does the strict parsing
    pat = r"[0-9]{2,4}/[0-9]{1,4}/[A-Z]{2,3}|\([^)]{2,3}\) ?[^0-9 ]{0,6} ?[0-9]{1,4}/[0-9]{1,4}"
    out = subprocess.run(["git", "-C", str(p), "-c", "core.quotepath=off", "grep", "-o", "-I", "-E", pat, "HEAD", "--", "*.md"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    per_file = defaultdict(set)
    for l in out.splitlines():
        _, path, m = l.split(":", 2)
        if not law_file(path): continue
        a = EU_OLD.search(m)
        if a:
            y = int(a.group(1)); y = y + 1900 if y < 100 else y
            if 1957 <= y <= 2014: per_file[path].add(f"{y}/{int(a.group(2))}")
            continue
        b = EU_PAREN.search(m)
        if not b: continue
        x, y = int(b.group(2)), int(b.group(3))
        if b.group(1) in ("EU", "UE", "EÚ", "ЕС", "ΕΕ", "AE", "ES", "EL", "EE") and 2015 <= x <= 2026 and len(b.group(2)) == 4 and not (1958 <= y <= 2026):
            per_file[path].add(f"{x}/{y}")                     # since 2015: (EU) 2016/679
        elif 1958 <= y <= 2026:
            per_file[path].add(f"R{x}/{y}")                    # regulations before 2015: (EC) No 1907/2006
    acts = Counter(a for s in per_file.values() for a in s)
    total = sum(1 for f in subprocess.run(["git", "-C", str(p), "-c", "core.quotepath=off", "ls-files"], capture_output=True, text=True,
                                          encoding="utf-8", errors="replace").stdout.splitlines() if law_file(f))
    print(f"{name:20s} EU: {len(per_file)} of {total} provisions cite {len(acts)} EU acts", flush=True)
    return {"provisions_citing": len(per_file), "acts": dict(acts.most_common()), "law_files": total}


if __name__ == "__main__":
    repos = {q.name.removesuffix("-law"): q for q in sorted(D.glob("*-law")) if (q / ".git").exists()}
    big = {k: v for k, v in repos.items() if int(subprocess.run(["git", "-C", str(v), "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout.strip() or 0) >= 100}
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    with ThreadPoolExecutor(4) as ex:
        if which in ("both", "lives"):
            res = dict(zip(big, ex.map(lambda kv: lives(*kv), big.items())))
            (OUT / "lives.json").write_text(json.dumps({k: v for k, v in res.items() if v}), encoding="utf-8")
        if which in ("both", "eu"):
            eu = {k: v for k, v in repos.items() if k in EU}
            res = dict(zip(eu, ex.map(lambda kv: eu_cites(*kv), eu.items())))
            (OUT / "eu.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
