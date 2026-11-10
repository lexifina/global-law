"""Which law wrote each drafting finding? Blame against the united-states-law git history.

    python tools/taxcode/blame.py <out dir> <united-states-law clone>

For every finding in findings.csv, search the history of its section's file (title-26/<section>.md) for the commit that
first introduced the finding's words (`git log -S`, oldest first); the commit message names the public law. Writes
blame.csv (finding + law + commit date) and prints counts by law. Findings whose words cannot be matched (formatting
differs between the OLRC XML and the Markdown) are left unattributed.
"""
import csv, re, subprocess, sys
from collections import Counter
from pathlib import Path

out, repo = Path(sys.argv[1]), Path(sys.argv[2])
rows = list(csv.DictReader(open(out / "findings.csv", encoding="utf-8")))


def section_file(cite):
    m = re.match(r"§([0-9A-Za-z–-]+)", cite)
    return f"title-26/{m.group(1).replace('–', '-')}.md" if m else None


def needle(row):
    w = row["words"].strip()
    if row["class"] == "unbalanced-parentheses" or not w or len(w) < 10:
        ctx = re.sub(r"\[(link|footnote)\]", "", row["context"]).strip()
        w = ctx[len(ctx) // 2 - 20:len(ctx) // 2 + 20] if len(ctx) > 60 else ctx
    w = re.sub(r"\s+", " ", w)
    # the longest run without characters that the Markdown may render differently
    parts = re.split(r"[“”\"'’‘—–§]", w)
    return max(parts, key=len).strip()[:60]


cache = {}
res = []
for r in rows:
    f = section_file(r["citing"])
    n = needle(r)
    law = date = commit = ""
    if f and len(n) >= 8:
        key = (f, n)
        if key not in cache:
            p = subprocess.run(["git", "-C", str(repo), "log", "--all", "--reverse", "--format=%h|%ad|%s", "--date=short",
                                "-S", n, "--", f], capture_output=True, text=True, encoding="utf-8")
            first = (p.stdout.strip().splitlines() or [""])[0]
            cache[key] = first
        first = cache[key]
        if first:
            commit, date, subj = first.split("|", 2)
            m = re.match(r"(Pub\. L\. [0-9]+[-–][0-9]+|[^:]+):", subj)
            law = m.group(1) if m else subj[:60]
    res.append({**r, "needle": n, "law": law, "date": date, "commit": commit})

with open(out / "blame.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(res[0].keys()))
    w.writeheader()
    w.writerows(res)
c = Counter(x["law"] or "(unmatched)" for x in res)
print(len(res), "findings;", sum(1 for x in res if x["law"]), "attributed")
for k, v in c.most_common(25):
    print(f"  {v:4}  {k}")
