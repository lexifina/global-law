"""Round 6, per-constitution summaries from analysis2.json -> analysis10.json
  read: median words per sentence in the founding text against wording written later by amendment, every constitution
  size: words today, provisions today, median words per provision
  life: median life of constitutional wording, or the share rewritten so far where no median is reached
"""
import json, statistics as st
from pathlib import Path

a = json.loads(Path("analysis2.json").read_text(encoding="utf-8"))
PREFIX = {"de": "Art. ", "ch": "BV ", "ee": "PS ", "li": "LV ", "lu": "Const. art", "mc": "Const. art", "sk": "Ústava", "si": "URS", "fi": "PL ",
          "hr": "Ustav", "gi": "Const. s", "dk": "Grundloven", "kg": "Konstitutsiya", "it": "Costituzione", "pt": "Constituição", "mg": "Constitution art",
          "rw": "Constitution art"}
rows = [r for r in a["readability"] if r["c"] in PREFIX and r["p"].startswith(PREFIX[r["c"]])]
read, size = [], []
for c in PREFIX:
    rs = [r for r in rows if r["c"] == c]
    if not rs: continue
    d0 = min(r["date"] for r in rs)
    o = [r["wps"] for r in rs if r["date"] == d0 and not r.get("base")]
    m = [r["wps"] for r in rs if r["date"] != d0]
    if c == "ch":  # Swiss history starts at a snapshot, not at adoption
        o = [r["wps"] for r in rs if r["base"]]; m = [r["wps"] for r in rs if not r["base"]]
    if len(o) >= 5 and len(m) >= 5:
        read.append({"c": c, "o": st.median(o), "a": st.median(m), "n0": len(o), "n1": len(m)})
    latest = {}
    for r in sorted(rs, key=lambda r: r["date"]):
        latest[r["p"]] = r
    words = [r["words"] for r in latest.values()]
    g = a["const_growth"].get(c)
    size.append({"c": c, "words": g[-1]["words"] if g else sum(words), "provisions": len(latest), "median_provision": st.median(words) if words else None})
life = []
for c, v in a["survival_const"].items():
    if v["n"] < 20: continue
    cur = v["curve"]; last = cur[-1][1]
    life.append({"c": c, "median_years": v["median_days"] / 365.25 if v["median_days"] else None, "rewritten": round(1 - last, 3),
                 "versions": v["n"], "events": v["events"], "span_years": v["max_days"] / 365.25})
Path("analysis10.json").write_text(json.dumps({"read": read, "size": size, "life": life}, ensure_ascii=False), encoding="utf-8")
for x in sorted(read, key=lambda x: x["a"] / x["o"]): print("read", x["c"], x["o"], x["a"], round(x["a"] / x["o"] - 1, 2), x["n0"], x["n1"])
for x in sorted(size, key=lambda x: -x["words"]): print("size", x)
for x in sorted(life, key=lambda x: (x["median_years"] is None, x["median_years"] or 0)): print("life", x)
