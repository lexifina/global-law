"""Malta hotspots: which chapters of the statute book are amended most since 2021 (Acts and their subsidiary legislation) -> analysis5.json"""
import csv, json, re, subprocess
from collections import Counter, defaultdict
from pathlib import Path

R = Path.home() / "Documents" / "law-in-motion" / "corpora" / "malta-law"
titles = {}
with open(R / "laws.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["kind"] == "cap": titles[row["id"]] = row["title"]
log = subprocess.run(["git", "-C", str(R), "log", "--format=\x1e%s\x1f%B"], capture_output=True, text=True, encoding="utf-8").stdout
hits, units, instruments = Counter(), Counter(), defaultdict(set)
for chunk in log.split("\x1e")[1:]:
    subj, body = chunk.split("\x1f", 1)
    if not re.search(r"^Kind:\s*amendment", body, re.M): continue
    d = re.search(r"^In-force:\s*(\d{4})", body, re.M)
    if not d or d.group(1) < "2021": continue
    inst, _, laws = subj.partition(": ")
    u = re.search(r"(\d+) unit", body)
    for law in re.findall(r"(?:Cap\.|S\.L\.)\s*(\d+)", laws):
        hits[law] += 1; units[law] += int(u.group(1)) if u else 0; instruments[law].add(inst)
top = [{"cap": c, "title": titles.get(c, f"Cap. {c}"), "changes": n, "units": units[c], "instruments": len(instruments[c])} for c, n in hits.most_common(15)]
Path("analysis5.json").write_text(json.dumps({"top": top, "chapters_touched": len(hits), "chapters_total": len(titles)}, ensure_ascii=False), encoding="utf-8")
print(len(hits), "of", len(titles), "chapters touched since 2021")
for t in top: print(t)
