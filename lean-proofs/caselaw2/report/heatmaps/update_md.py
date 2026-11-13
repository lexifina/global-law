"""Rewrite the case-law numbers of HEATMAPS.md from heatmaps.json and series.json (round 4).

The table rows of the two case-law charts and the "Totals" and "Peaks" paragraphs of section A are replaced by text
generated from the JSON, so the file cannot go stale again. Run after compute.py and plot.py:
    python update_md.py
"""
import datetime as dt
import json
import os
import re

H = os.path.dirname(os.path.abspath(__file__))
hm = json.load(open(os.path.join(H, "heatmaps.json"), encoding="utf-8"))
se = json.load(open(os.path.join(H, "series.json"), encoding="utf-8"))
p = os.path.join(H, "HEATMAPS.md")
s = open(p, encoding="utf-8").read()


def day(d, wd=False):
    t = dt.date(d // 10000, d // 100 % 100, d % 100)
    return t.strftime("%a %d %b %Y" if wd else "%d %b %Y").replace(" 0", " ")


def n(x):
    return f"{x:,}"


b, k = hm["badlaw"], hm["broken"]
y = "%d–%d" % tuple(b["years"])
rows = {
    "| Decisions relying on bad law |": f"| Decisions relying on bad law | `caselaw_bad_law_by_day.{{png,svg}}` | {y} | "
    f"{n(b['total'])} decisions | {b['peaks'][0]['count']} on {day(b['peaks'][0]['day'], True)} |",
    "| Precedent broken |": f"| Precedent broken | `caselaw_precedent_broken_by_day.{{png,svg}}` | {y} | "
    f"{n(k['total'])} events | {k['peaks'][0]['count']} on {day(k['peaks'][0]['day'], True)} |",
}
lines = s.split("\n")
for i, l in enumerate(lines):
    for pre, new in rows.items():
        if l.startswith(pre):
            lines[i] = new
s = "\n".join(lines)

fr = se["badlaw"]["finding_rows"]
firm = se["badlaw"]["finding_rows_firm"]
bp = b["parts"]
bad_tot = (f"**Totals.** {n(se['badlaw']['citing_decisions'])} citing decisions over all years "
           f"({n(sum(fr.values()))} finding rows; {n(firm.get('1', 0))} firm). {y}: {n(b['total'])}. Decisions with "
           f"each kind (overlapping): cites overruled {n(bp['citesOverruled'])}, vacated or reversed "
           f"{n(bp['citesVacated'])}, withdrawn {n(bp['citesWithdrawn'])}, not citable {n(bp['citesNotCitable'])}, "
           f"superseded holding {n(bp.get('appliesSupersededHolding', 0))} (`appliesSupersededHolding` is not "
           f"emitted: the data carry no conduct date). Generated from `heatmaps.json` of {se['generated']}.")
bad_peaks = ("**Peaks.** " + ", ".join(f"{day(q['day'])} ({q['count']})" for q in b["peaks"][:5]) +
             ". Peaks are small (tens, not hundreds): the series is spread across many courts and days. The courts "
             "behind each peak day were last broken down for the first run and are not repeated here.")
st = se["broken"]["by_status"]
kp = k["parts"]
brk_tot = (f"**Totals.** {n(se['broken']['events'])} events over all years: " +
           ", ".join(f"{a} {n(v)}" for a, v in sorted(st.items(), key=lambda kv: -kv[1])) +
           f". {y}: {n(k['total'])} (" + ", ".join(f"{a} {n(v)}" for a, v in kp.items() if v) +
           "). The certificate checker passes more negative treatments than this; only the ones the run admitted "
           "with power count here.")
brk_peaks = "**Peaks.** " + ", ".join(f"{day(q['day'])} ({q['count']})" for q in k["peaks"][:5]) + "."


def repl(text, sec, label, new):
    """Replace the paragraph starting with **label** inside the ### section named sec."""
    a = text.index("### " + sec)
    e = text.find("\n### ", a + 4)
    e = len(text) if e < 0 else e
    body = text[a:e]
    m = re.search(r"\*\*" + label + r"\.\*\*.*?(?=\n\n|\Z)", body, re.S)
    assert m, (sec, label)
    return text[:a] + body[:m.start()] + new + body[m.end():] + text[e:]


s = repl(s, "Decisions relying on bad law, by day", "Totals", bad_tot)
s = repl(s, "Decisions relying on bad law, by day", "Peaks", bad_peaks)
s = repl(s, "Precedent broken, by day", "Totals", brk_tot)
s = repl(s, "Precedent broken, by day", "Peaks", brk_peaks)
s = re.sub(r"Numbers below are those of the final run.*?(?=\n\n)",
           f"Numbers below are generated from `series.json` and `heatmaps.json` ({se['generated']}, the round-4 "
           f"final run) by `update_md.py`; run it after `plot.py`.", s, count=1, flags=re.S)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("HEATMAPS.md updated:", n(b["total"]), n(k["total"]))
