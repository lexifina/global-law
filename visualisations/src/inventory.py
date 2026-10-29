"""Inventory every law repo with history and report what changed since the last round -> inventory_state.json"""
import json, re, subprocess, sys
from datetime import datetime
from pathlib import Path

D = Path.home() / "Documents"
STATE = Path("inventory_state.json")


def git(p, *a):
    return subprocess.run(["git", "-C", str(p), *a], capture_output=True, text=True, encoding="utf-8").stdout.strip()


cands = sorted({p for p in D.glob("*-law") if p.is_dir()} | {p for p in (D / "world-law-repos").glob("*") if p.is_dir()} |
               {D / "swiss-law", D / "uk-law-history", D / "us-code-history", D / "global-law" / "de" / "bund" / "grundgesetz"})
now = {}
for p in cands:
    head = git(p, "rev-parse", "HEAD")
    if not head: continue
    n = int(git(p, "rev-list", "--count", "HEAD") or 0)
    if n < 3: continue  # stubs
    dates = re.findall(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4}-\d\d-\d\d)", git(p, "log", "--format=%B"), re.M)
    now[str(p.relative_to(D))] = {"head": head[:10], "commits": n, "files": len(git(p, "ls-files").splitlines()),
                                  "first": min(dates) if dates else None, "last": max(dates) if dates else None}
prev = json.loads(STATE.read_text(encoding="utf-8"))["repos"] if STATE.exists() else {}
new = [k for k in now if k not in prev]
changed = [k for k in now if k in prev and now[k]["head"] != prev[k]["head"]]
gone = [k for k in prev if k not in now]
for k in sorted(now):
    v = now[k]; tag = "NEW" if k in new else "CHANGED" if k in changed else ""
    print(f"{k:42s} {v['commits']:5d} commits {v['files']:6d} files  {v['first']} .. {v['last']}  {tag}")
print("new", new, "changed", changed, "gone", gone)
if "--save" in sys.argv:
    STATE.write_text(json.dumps({"at": datetime.now().isoformat(timespec="minutes"), "repos": now}, indent=1), encoding="utf-8")
