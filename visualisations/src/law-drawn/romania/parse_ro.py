"""romania-law commit messages (all.txt from git log) -> recs.json: one record per commit."""
import json, re
from pathlib import Path

HERE = Path(__file__).parent
T = lambda k, b: (re.search(rf"^{k}:\s*(.+)$", b, re.M) or [None, None])[1]
out = []
for r in (HERE / "all.txt").read_text(encoding="utf-8").split("\x1e")[1:]:
    head, _, body = r.partition("\n")
    who, _, date = head.rpartition("|")
    name, _, email = who.partition(" <")
    subj = body.split("\n", 1)[0]
    aff = re.findall(r"^Affecting:\s*(.+)$", body, re.M)
    rule = None
    m = re.search(r"(in force on publication|in force (\d+) days after publication|sets no day of its own, so in\s+force 3 days after publication|in force from a day it sets|"
                  r"with no day of its own, in force on publication)", body)
    if m: rule = re.sub(r"\s+", " ", m.group(0))
    out.append({"author": name, "key": email.split("@")[0], "date": date, "subject": subj[:200],
                "kind": T("Kind", body), "law": T("Law", body), "enacted": T("Enacted", body), "published": (T("Published", body) or "")[:10] or None,
                "in_force": T("In-force", body), "affecting": [a[:160] for a in aff][:40], "n_affecting": len(aff),
                "as_enacted": " as enacted (" in subj, "rule": rule, "words": T("Words-changed", body),
                "provisions": T("Provisions", body), "text": re.sub(r"\s+", " ", body.split("\n\n", 2)[1] if body.count("\n\n") >= 1 else "")[:600]})
(HERE / "recs.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
import collections
print(len(out), collections.Counter(r["kind"] for r in out).most_common())
print("rules", collections.Counter(r["rule"] for r in out if r["as_enacted"]).most_common(12))
