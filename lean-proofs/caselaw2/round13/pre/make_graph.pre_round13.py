#!/usr/bin/env python3
"""One figure of every benchmark score, rebuilt from benchmarks/**/results/*.json (standard library only).

  python -I make_graph.py [--html PATH] [--no-png]

Writes:
  <html>                         self-contained page (inline SVG, light + dark, narrow layout at <= 560 px)
  <html dir>/benchmarks.svg      standalone figure (light; dark via prefers-color-scheme)
  <html dir>/benchmarks.png      1600 px wide, light (rendered by headless Chrome if found)
  benchmarks/graph/rows.tsv      the exact numbers plotted
Rows: one per (dataset, split); split 'all' is plotted when present, else 'dev' and 'sealed' as separate rows.
Hash halves h0/h1 are listed in the table under the figure, not plotted.
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
DEFAULT_HTML = os.path.join(os.path.expanduser("~"), "Documents", "html-reports", "benchmarks.html")

BUILD_ORDER = ["round4", "round5", "round6", "round7", "round8", "round9", "round10", "round11", "round12"]
LABEL_ALIAS = {"round8v8e": "round8", "round9v9c": "round9", "round10v10d": "round10",
               "round11v11d": "round11"}
# Presentation overrides (the result files are left as their scorers wrote them)
ROW_LABEL_OVERRIDE = {"fjc_idb_unpub": "FJC appeals, unpublished district rulings: reversed/vacated (same relation the FJC rules were tuned on)"}
PLOT_OVERRIDE = {"brace_hall_state": ["recall", "recall_all", "precision"]}
PAGE_NOTE = ("Plateau: the rule-based work has plateaued as of round 12. Maxed out: SCDB disposition, state tables, FJC tie rules, Brace &amp; Hall, Songer, Federal Circuit, en banc. Still open: user decisions and the expensive FJC “which ruling” reader.")
BUILD_NAME = {"round4": "Round 4", "round5": "Round 5", "round6": "Round 6", "round7": "Round 7", "round8": "Round 8", "round9": "Round 9", "round10": "Round 10", "round11": "Round 11", "round12": "Round 12"}
TESTS_ORDER = ["overruling", "same-case"]
TESTS_NAME = {"overruling": "Overruling by a later case", "same-case": "Same-case history (reversed, vacated, withdrawn)"}
COURT_ORDER = ["supreme", "federal", "state", "mixed"]
COURT_NAME = {"supreme": "Supreme Court decisions", "federal": "Federal court decisions",
              "state": "State court decisions", "mixed": "Federal and state court decisions"}
METRIC_NAME = {"recall": "recall", "precision": "precision", "clean": "clean rate", "link_rate": "link rate",
               "recall_any": "recall (any overruler)", "recall_model": "model's dates",
               "recall_attributed": "overruler's date", "recall_all": "all decisions"}
SPLIT_NAME = {"all": "", "dev": "dev half", "sealed": "sealed half", "h0": "half 0", "h1": "half 1 (held out)"}

CSS = """
.bm{--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--ink3:#8a8984;--rule:#e4e3df;--band:#f3f2ef;
--b-round5:#9a9994;--b-round4:#86b6ef;--b-round6:#5f9dea;--b-round7:#3a84dd;--b-round8:#226bc6;--b-round9:#1a56a3;--b-round10:#123f78;--b-round11:#0a2a52;--b-round12:#04152b;
--nb:#eb6834;
font-family:ui-sans-serif,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
font-variant-numeric:tabular-nums}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .bm{--surface:#1a1a19;--ink:#f0efec;
--ink2:#c3c2b7;--ink3:#8f8e88;--rule:#33322f;--band:#222220;--b-round5:#8f8e88;--b-round4:#1c5cab;--b-round6:#2a73cf;--b-round7:#4a8fe5;--b-round8:#6fa8ec;--b-round9:#94c0f2;--b-round10:#b9d6f7;--b-round11:#dcebfc;--b-round12:#fdfeff;
--nb:#d95926}}
:root[data-theme="dark"] .bm{--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--ink3:#8f8e88;--rule:#33322f;
--band:#222220;--b-round5:#8f8e88;--b-round4:#1c5cab;--b-round6:#2a73cf;--b-round7:#4a8fe5;--b-round8:#6fa8ec;--b-round9:#94c0f2;--b-round10:#b9d6f7;--b-round11:#dcebfc;--b-round12:#fdfeff;
--nb:#d95926}
.bm .bg{fill:var(--surface)}
.bm text{fill:var(--ink2);font-size:12px}
.bm .t1{fill:var(--ink);font-size:13px;font-weight:600}
.bm .t2{fill:var(--ink2);font-size:12px}
.bm .t3{fill:var(--ink3);font-size:11px}
.bm .gh{fill:var(--ink);font-size:14px;font-weight:600}
.bm .gs{fill:var(--ink3);font-size:11px;letter-spacing:.02em}
.bm .title{fill:var(--ink);font-size:20px;font-weight:600}
.bm .sub{fill:var(--ink2);font-size:13px}
.bm .val{fill:var(--ink);font-size:12px;font-weight:600}
.bm .grid{stroke:var(--rule);stroke-width:1}
.bm .axis{stroke:var(--ink3);stroke-width:1}
.bm .band{fill:var(--band)}
.bm .conn{stroke:var(--ink3);stroke-width:1.5;fill:none}
.bm .nbtag{fill:none;stroke:var(--nb);stroke-width:1.2}
.bm .nbdot{fill:var(--nb)}
.bm .gbar{fill:var(--ink2)}
.bm .gbar.neg{fill:var(--ink3)}
"""
for _b in BUILD_ORDER:
    CSS += ".bm .ci-%s{stroke:var(--b-%s);stroke-width:2;stroke-linecap:round}\n" % (_b, _b)
    CSS += ".bm .d-%s{fill:var(--b-%s);stroke:var(--surface);stroke-width:2}\n" % (_b, _b)
    CSS += ".bm .h-%s{fill:var(--surface);stroke:var(--b-%s);stroke-width:2.2}\n" % (_b, _b)


def esc(s):
    return html.escape(str(s), quote=True)


def load(bench=None):
    bench = bench or BENCH
    res = []
    for p in sorted(glob.glob(os.path.join(bench, "**", "results", "*.json"), recursive=True)):
        try:
            with open(p, encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError):
            continue
        if not isinstance(r, dict) or not {"dataset", "label", "split", "metrics", "primary"} <= set(r):
            continue
        r["label"] = LABEL_ALIAS.get(r["label"], r["label"])
        if r["dataset"] in ROW_LABEL_OVERRIDE:
            r["row_label"] = ROW_LABEL_OVERRIDE[r["dataset"]]
        if r["dataset"] in PLOT_OVERRIDE:
            r["plot"] = PLOT_OVERRIDE[r["dataset"]]
        if r["label"] not in BUILD_ORDER:
            continue
        r["_path"] = os.path.relpath(p, bench)
        un = use_note(r)
        if un and not r.get("use_note"):
            r["use_note"] = un
        tuned = tuned_on(r)
        if tuned:
            r["blind"] = False
            r["notes"] = (r.get("notes", "") + " " + tuned).strip()
        res.append(r)
    return res


TUNED_FILE = os.path.join(HERE, "tuned_on.tsv")
USES_FILE = os.path.join(HERE, "uses.tsv")


def use_note(r):
    """graph/uses.tsv: dataset_prefix, splits, from build, note. Labels a re-used held-out half."""
    if not os.path.exists(USES_FILE):
        return ""
    best = ""
    with open(USES_FILE, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            pre, splits, first, note = (line.rstrip("\n").split("\t") + ["", "", "", ""])[:4]
            if (r["dataset"].startswith(pre) and r["split"] in splits.split(",")
                    and BUILD_ORDER.index(r["label"]) >= BUILD_ORDER.index(first)):
                best = note
    return best


def tuned_on(r):
    """graph/tuned_on.tsv: dataset_prefix, splits (comma list), first build tuned on, reason.
    A result of that dataset/split from that build or later is drawn as not blind."""
    if not os.path.exists(TUNED_FILE):
        return ""
    with open(TUNED_FILE, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            pre, splits, first, why = (line.rstrip("\n").split("\t") + ["", "", "", ""])[:4]
            if (r["dataset"].startswith(pre) and r["split"] in splits.split(",")
                    and BUILD_ORDER.index(r["label"]) >= BUILD_ORDER.index(first)):
                return why
    return ""


def build_rows(res):
    by = {}
    for r in res:
        by.setdefault((r["dataset"], r["split"]), {})[r["label"]] = r
    keys = set(by)
    rows = []
    def split_halves(ds):
        if ds.endswith(("_federal", "_state")):  # court sub-rows stay pooled; tuned builds draw hollow
            return False
        h0 = by.get((ds, "h0"), {})
        return bool(by.get((ds, "h1"))) and any(not x.get("blind", True) for x in h0.values())
    for (ds, sp), builds in by.items():
        if sp in ("h0", "h1"):
            if not split_halves(ds):
                continue
        elif sp == "all" and split_halves(ds):
            continue
        elif sp != "all" and (ds, "all") in keys:
            continue
        ref = builds[max(builds, key=BUILD_ORDER.index)]
        rows.append({"dataset": ds, "split": sp, "builds": builds, "ref": ref})

    def sk(row):
        r = row["ref"]
        return (TESTS_ORDER.index(r.get("tests", "same-case")) if r.get("tests") in TESTS_ORDER else 9,
                COURT_ORDER.index(r.get("court", "mixed")) if r.get("court") in COURT_ORDER else 9,
                row["dataset"].replace("_recognised", "~r"),
                {"all": 0, "sealed": 1, "h1": 1, "dev": 2, "h0": 2}.get(row["split"], 3))
    rows.sort(key=sk)
    global SKIPPED
    SKIPPED = [r for r in rows if not row_lines(r)]
    return [r for r in rows if row_lines(r)]


SKIPPED = []


def pts(row, metric):
    out = []
    for b in BUILD_ORDER:
        r = row["builds"].get(b)
        if not r:
            continue
        m = r["metrics"].get(metric)
        if not m or not m.get("n") or m.get("p") is None:
            continue
        out.append((b, m))
    return out


def fmt_pct(p):
    if p is None:
        return "–"
    v = 100 * p
    return "%.0f%%" % v if v >= 10 or v == 0 else "%.1f%%" % v


def wrap(s, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines or [""]


def row_lines(row):
    """Metric lines drawn for a row: primary, then precision if meaningful and present."""
    if row["ref"].get("plot"):
        return [m for m in row["ref"]["plot"] if pts(row, m)]
    prim = row["ref"]["primary"]
    lines = [prim]
    if prim != "precision" and pts(row, "precision"):
        lines.append("precision")
    return [m for m in lines if pts(row, m)]


def tags(row):
    r = row["ref"]
    t = []
    if r.get("use_note"):
        t.append(r["use_note"])
    elif SPLIT_NAME.get(row["split"]):
        t.append(SPLIT_NAME[row["split"]])
    nb = [b for b in BUILD_ORDER if b in row["builds"] and not row["builds"][b].get("blind", True)]
    if not nb:
        t.append("blind" if not r.get("use_note") else "not tuned on")
    elif len(nb) == len(row["builds"]):
        t.append("NOT BLIND")
    else:
        t.append("NOT BLIND")
        t.append("for " + (", ".join(BUILD_NAME[b] for b in nb) if len(nb) < 3 else "Rounds %s–%s" % (nb[0][5:], nb[-1][5:])) + " only")
    return t


def tip(row, b, metric, m):
    return "%s · %s · %s: %d/%d = %s (95%%: %s–%s)" % (
        row["ref"].get("row_label", row["dataset"]), BUILD_NAME[b], METRIC_NAME.get(metric, metric), m["k"], m["n"],
        "%.1f%%" % (100 * m["p"]), "%.1f%%" % (100 * m["lo"]), "%.1f%%" % (100 * m["hi"]))


def draw_metric(o, row, metric, x0, x1, y, blind):
    X = lambda p: x0 + (x1 - x0) * p
    P = pts(row, metric)
    nb = len(P)
    offs = {1: [0], 2: [-3.5, 3.5], 3: [-5, 0, 5], 4: [-6, -2, 2, 6], 5: [-8, -4, 0, 4, 8], 6: [-9, -5.4, -1.8, 1.8, 5.4, 9], 7: [-9, -6, -3, 0, 3, 6, 9], 8: [-10.5, -7.5, -4.5, -1.5, 1.5, 4.5, 7.5, 10.5],
            9: [-12, -9, -6, -3, 0, 3, 6, 9, 12]}[max(1, nb)]
    coords = []
    for (b, m), dy in zip(P, offs):
        lo, hi = m["lo"] if m["lo"] is not None else m["p"], m["hi"] if m["hi"] is not None else m["p"]
        o.append('<line class="ci-%s" x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" opacity=".55"/>'
                 % (b, X(lo), max(X(hi), X(lo) + 0.5), y + dy, y + dy))
        coords.append((b, m, X(m["p"]), y + dy))
    if len(coords) > 1:
        o.append('<polyline class="conn" points="%s"/>' % " ".join("%.1f,%.1f" % (cx, cy) for _, _, cx, cy in coords))
    for b, m, cx, cy in coords:
        r = 5 if metric == row["ref"]["primary"] else 4
        bb = row["builds"][b].get("blind", True)
        cls = ("d-%s" if bb else "h-%s") % b
        o.append('<g><title>%s</title><circle cx="%.1f" cy="%.1f" r="12" fill="transparent"/>'
                 '<circle class="%s" cx="%.1f" cy="%.1f" r="%.1f"/></g>' % (esc(tip(row, b, metric, m)), cx, cy, cls,
                                                                         cx, cy, r))
    return P


SHORT = {"round4": "R4", "round5": "R5", "round6": "R6", "round7": "R7", "round8": "R8", "round9": "R9", "round10": "R10", "round11": "R11", "round12": "R12"}


def values_text(P, row=None):
    allb = set(row["builds"]) if row else set()
    bs = [b for b, _ in P]
    if len(P) >= 4:  # long histories: first and last only (every value is in the tooltip and the table)
        (b0, m0), (b1, m1) = P[0], P[-1]
        return "%s %s → %s %s" % (SHORT[b0], fmt_pct(m0["p"]), SHORT[b1], fmt_pct(m1["p"]))
    std = bool(bs) and bs[0] == "round4" and all(b in ("round4", "round6", "round7", "round8", "round9", "round10", "round11", "round12") for b in bs) and (
        not row or set(bs) == allb)
    return " → ".join((fmt_pct(m["p"]) if std else "%s %s" % (SHORT[b], fmt_pct(m["p"]))) for b, m in P)


STEPS = [("round4", "round6"), ("round6", "round7"), ("round7", "round8"), ("round8", "round9"), ("round9", "round10"), ("round10", "round11"),
         ("round11", "round12")]


def gain_rows(rows):
    """Rows for the gain panel: every row with no tuned-on build (blind or re-used held-out halves), its first
    plotted metric (recall-type)."""
    out = []
    for row in rows:
        if "NOT BLIND" in tags(row):
            continue
        ml = row_lines(row)
        m = ml[0] if ml else None
        if not m or not m.startswith("recall"):
            continue
        p = {b: v["p"] for b, v in pts(row, m)}
        out.append((row, m, p))
    return out


def draw_gains(o, rows, wide, W, pad, y):
    G = gain_rows(rows)
    if not G:
        return y
    y += 34
    o.append('<text class="gs" x="%d" y="%d">%s</text>' % (pad, y, "GAIN PER ROUND"))
    y += 18
    o.append('<text class="gh" x="%d" y="%d">Recall points gained from one build to the next '
             '(rows with no tuned-on build)</text>' % (pad, y) if wide else
             '<text class="gh" x="%d" y="%d">Recall points gained per round</text>' % (pad, y))
    y += 8
    o.append('<line class="axis" x1="%d" x2="%d" y1="%d" y2="%d"/>' % (pad, W - pad, y, y))
    if wide:
        c0, cw, lab_w = 440, 104, 60
    else:
        c0, cw, lab_w = pad, (W - 2 * pad) // len(STEPS), 52
    full = 40.0  # points that fill a cell's bar zone
    y += 20
    for i, (a, b) in enumerate(STEPS):
        cx = c0 + i * cw
        o.append('<text class="t3" x="%d" y="%d">%s → %s</text>' % (cx, y, SHORT[a], SHORT[b]))
    for row, m, p in G:
        r = row["ref"]
        label = re.sub(r"\s*\([^)]*\)", "", r.get("row_label", row["dataset"])).strip()
        tg = r.get("use_note") or SPLIT_NAME.get(row["split"], "")
        lines = wrap(label + (" · " + tg if tg else ""), lab_w)
        if wide:
            ly = y + 22
            for k, ln in enumerate(lines[:2]):
                o.append('<text class="t2" x="%d" y="%d">%s</text>' % (pad, ly + 15 * k, esc(ln if k == 0 or len(lines) <= 2
                                                                                            else ln[:-1] + "…")))
            cy = ly - 4
            y = ly + 15 * (min(2, len(lines)) - 1) + 8
        else:
            ly = y + 22
            for k, ln in enumerate(lines[:2]):
                o.append('<text class="t2" x="%d" y="%d">%s</text>' % (pad, ly + 15 * k, esc(ln)))
            cy = ly + 15 * min(2, len(lines)) + 4
            y = cy + 8
        for i, (a, b) in enumerate(STEPS):
            cx = c0 + i * cw
            zx = cx + 2
            if a in p and b in p:
                g = 100 * (p[b] - p[a])
                wbar = min(abs(g), full) / full * (cw * 0.55)
                x0 = zx if g >= 0 else zx - max(wbar, 1.5)
                o.append('<line class="grid" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/>' % (zx, zx, cy - 7, cy + 3))
                if abs(g) >= 0.05:
                    o.append('<rect class="gbar%s" x="%.1f" y="%.1f" width="%.1f" height="8" rx="2"><title>%s</title></rect>'
                             % ("" if g >= 0 else " neg", x0, cy - 6, max(wbar, 1.5),
                                esc("%s, %s → %s: %+.1f points" % (label, BUILD_NAME[a], BUILD_NAME[b], g))))
                o.append('<text class="%s" x="%.1f" y="%.1f">%+.1f</text>' % (
                    "val" if abs(g) >= 5 else "t3", zx + max(wbar, 1.5) + 5, cy + 2, g))
            else:
                o.append('<text class="t3" x="%d" y="%.1f">–</text>' % (zx, cy + 2))
    return y + 6


def render(rows, wide=True):
    o = []
    W = 1200 if wide else 390
    pad = 24 if wide else 16
    if wide:
        lab_x, plot_x0, plot_x1, val_x = pad, 440, 850, 872
    else:
        lab_x, plot_x0, plot_x1, val_x = pad, pad + 6, W - pad - 6, pad
    y = 0
    # title + legend
    y += 34
    o.append('<text class="title" x="%d" y="%d">How the model scores on every answer key</text>' % (pad, y))
    sub = ("Share of each key's negative outcomes the model marks (recall), with precision where meaningful. "
           "Dots: model build; lines: Wilson 95% intervals.")
    for ln in wrap(sub, 120 if wide else 58):
        y += 19
        o.append('<text class="sub" x="%d" y="%d">%s</text>' % (pad, y, esc(ln)))
    present = [b for b in BUILD_ORDER if any(b in r["builds"] for r in rows)]
    y += 26
    lx = pad
    for b in present:
        o.append('<circle class="d-%s" cx="%d" cy="%d" r="5"/>' % (b, lx + 5, y - 4))
        o.append('<text class="t2" x="%d" y="%d">%s</text>' % (lx + 15, y, BUILD_NAME[b]))
        lx += 86
    if not wide:
        y += 22
        lx = pad
    o.append('<circle class="h-round6" cx="%d" cy="%d" r="4.5"/>' % (lx + 5, y - 4))
    o.append('<text class="t2" x="%d" y="%d">hollow = not blind (model tuned on this key)</text>' % (lx + 15, y))
    y += 18
    # axis header
    def axis(yy, label=True):
        for t in (0, .25, .5, .75, 1):
            xx = plot_x0 + (plot_x1 - plot_x0) * t
            if label:
                o.append('<text class="t3" x="%.1f" y="%d" text-anchor="middle">%d%%</text>' % (xx, yy, int(t * 100)))
    if wide:
        y += 14
        axis(y)
        o.append('<text class="t3" x="%d" y="%d">value by build</text>' % (val_x, y))
        o.append('<text class="t3" x="%d" y="%d" text-anchor="end">n</text>' % (W - pad, y))
    grid_top = y + 8
    cur_group = None
    row_ys = []
    for row in rows:
        r = row["ref"]
        g = (r.get("tests"), r.get("court"))
        if g != cur_group:
            cur_group = g
            y += 30
            o.append('<text class="gs" x="%d" y="%d">%s</text>' % (pad, y, esc(TESTS_NAME.get(g[0], g[0]).upper())))
            y += 18
            o.append('<text class="gh" x="%d" y="%d">%s</text>' % (pad, y, esc(COURT_NAME.get(g[1], g[1]))))
            y += 8
            o.append('<line class="axis" x1="%d" x2="%d" y1="%d" y2="%d"/>' % (pad, W - pad, y, y))
            if not wide:
                y += 14
                axis(y)
        mlines = row_lines(row)
        blind = "NOT BLIND" not in tags(row)
        label = r.get("row_label", row["dataset"])
        lab = wrap(label, 42 if wide else 52)
        tg = tags(row)
        nmax = max((m["n"] for b, m in pts(row, mlines[0])), default=0) if mlines else 0
        if wide:
            h = max(18 * len(lab) + 18, 26 * max(1, len(mlines))) + 16
            top = y + 12
            o.append('<rect class="band" x="%d" y="%d" width="%d" height="%d" rx="4" opacity="%s"/>'
                     % (plot_x0 - 6, top - 2, plot_x1 - plot_x0 + 12, h - 12, "1" if not blind else "0"))
            ty = top + 13
            for ln in lab:
                o.append('<text class="t1" x="%d" y="%d">%s</text>' % (lab_x, ty, esc(ln)))
                ty += 17
            plain = [t for t in tg if t != "NOT BLIND"]
            if "NOT BLIND" in tg:
                o.append('<rect class="nbtag" x="%d" y="%d" width="66" height="17" rx="4"/>' % (lab_x, ty - 12))
                o.append('<text class="t3" x="%d" y="%d">not blind</text>' % (lab_x + 9, ty + 1))
                plain = [t for t in plain if t != "blind"]
                tx = lab_x + 76
            else:
                tx = lab_x
            if plain:
                o.append('<text class="t3" x="%d" y="%d">%s</text>' % (tx, ty + 1, esc(" · ".join(plain))))
            my = top + 12
            for m in mlines:
                o.append('<text class="t3" x="%d" y="%.1f" text-anchor="end">%s</text>'
                         % (plot_x0 - 14, my + 4, esc(METRIC_NAME.get(m, m))))
                P = draw_metric(o, row, m, plot_x0, plot_x1, my, blind)
                vt = values_text(P, row)
                nn = P[-1][1]["n"]
                o.append('<text class="val" x="%d" y="%.1f">%s</text>' % (val_x, my + 4, esc(vt)))
                o.append('<text class="t3" x="%d" y="%.1f" text-anchor="end">{:,}</text>'.format(nn) % (W - pad, my + 4))
                row_ys.append(my)
                my += 24
            y = top + h - 12
        else:
            top = y + 10
            ty = top + 12
            for ln in lab:
                o.append('<text class="t1" x="%d" y="%d">%s</text>' % (lab_x, ty, esc(ln)))
                ty += 17
            tline = " · ".join(t if t != "NOT BLIND" else "not blind" for t in tg)
            if not blind:
                o.append('<circle class="nbdot" cx="%d" cy="%d" r="3"/>' % (lab_x + 3, ty - 3))
                o.append('<text class="t3" x="%d" y="%d">%s</text>' % (lab_x + 10, ty, esc(tline)))
            else:
                o.append('<text class="t3" x="%d" y="%d">%s</text>' % (lab_x, ty, esc(tline)))
            my = ty + 16
            for m in mlines:
                if not blind:
                    o.append('<rect class="band" x="%d" y="%.1f" width="%d" height="18" rx="3"/>'
                             % (plot_x0 - 6, my - 9, plot_x1 - plot_x0 + 12))
                for t in (0, .25, .5, .75, 1):
                    xx = plot_x0 + (plot_x1 - plot_x0) * t
                    o.append('<line class="grid" x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f"/>' % (xx, xx, my - 8, my + 8))
                P = draw_metric(o, row, m, plot_x0, plot_x1, my, blind)
                my += 16
                o.append('<text class="t2" x="%d" y="%.1f">%s%s · n=%d</text>'
                         % (lab_x, my + 2, "" if m == r["primary"] else METRIC_NAME.get(m, m) + ": ",
                            esc(values_text(P, row)), P[-1][1]["n"]))
                my += 20
            y = my
    y += 18
    if wide:
        # vertical grid behind rows (inserted first so it sits underneath)
        gl = []
        for t in (0, .25, .5, .75, 1):
            xx = plot_x0 + (plot_x1 - plot_x0) * t
            gl.append('<line class="grid" x1="%.1f" x2="%.1f" y1="%d" y2="%d"/>' % (xx, xx, grid_top, y - 12))
        o = gl + o
    y = draw_gains(o, rows, wide, W, pad, y)
    foot = ("Recall: of the key's negative outcomes linked to a decision in the corpus, the share the model marks "
            "negative. Precision: of the model's negatives on linked decisions, the share the key agrees with. "
            "Not blind: the model was built or tuned with this key in view.")
    for ln in wrap(foot, 150 if wide else 60):
        y += 15
        o.append('<text class="t3" x="%d" y="%d">%s</text>' % (pad, y, esc(ln)))
    y += 20
    H = y
    svg = ('<svg class="bm" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
           'aria-label="Benchmark scores of the model by build">' % (W, H, W, H))
    return svg + '<rect class="bg" width="100%%" height="100%%"/>' + "".join(o) + "</svg>", W, H


def table_html(res):
    trs = []
    def sk(r):
        return (r.get("tests", ""), r.get("court", ""), r["dataset"], r["split"], BUILD_ORDER.index(r["label"]))
    for r in sorted(res, key=sk):
        cells = []
        for m in ("recall", "precision", "clean", "link_rate"):
            v = r["metrics"].get(m)
            if v and v.get("n"):
                cells.append("%d/%d<br><span>%.1f%% (%.1f–%.1f)</span>" % (
                    v["k"], v["n"], 100 * v["p"], 100 * (v["lo"] or 0), 100 * (v["hi"] or 0)))
            else:
                cells.append("–")
        trs.append("<tr><td>%s<br><span>%s</span></td><td>%s</td><td>%s</td><td>%s</td>%s</tr>" % (
            esc(r.get("row_label", r["dataset"])), esc(r["dataset"]), esc(r["split"]), esc(BUILD_NAME[r["label"]]),
            "yes" if r.get("blind", True) else "<b>no</b>", "".join("<td>%s</td>" % c for c in cells)))
    return ("<table><thead><tr><th>Benchmark</th><th>Split</th><th>Build</th><th>Blind</th><th>Recall</th>"
            "<th>Precision</th><th>Clean</th><th>Link rate</th></tr></thead><tbody>%s</tbody></table>" % "".join(trs))


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Model benchmark scores</title>
<style>
:root{--pg:#fcfcfb;--pgink:#0b0b0b;--pgink2:#52514e;--pgrule:#e4e3df}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--pg:#1a1a19;--pgink:#f0efec;--pgink2:#c3c2b7;--pgrule:#33322f}}
:root[data-theme="dark"]{--pg:#1a1a19;--pgink:#f0efec;--pgink2:#c3c2b7;--pgrule:#33322f}
body{margin:0;background:var(--pg);color:var(--pgink);font-family:ui-sans-serif,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
main{max-width:1200px;margin:0 auto;padding:16px}
svg{display:block;width:100%%;height:auto}
.narrow{display:none}
@media (max-width:560px){.wide{display:none}.narrow{display:block}}
h2{font-size:15px;font-weight:600;margin:32px 0 8px}
p.note{font-size:13px;color:var(--pgink2);line-height:1.5}
p.lead{color:var(--pgink);margin:4px 0 12px}
.tw{overflow-x:auto}
table{border-collapse:collapse;font-size:12px;width:100%%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--pgrule);vertical-align:top}
th{font-weight:600;color:var(--pgink2)}
td span{color:var(--pgink2);font-size:11px}
%s
</style></head><body><main>
<p class="note lead">%s</p>
<div class="wide">%s</div>
<div class="narrow">%s</div>
<p class="note">Generated %s from %d result files under <code>caselaw-lean-2/benchmarks/</code> by
<code>benchmarks/graph/make_graph.py</code>. Hover a dot for k/n and the interval. Rows plot the pooled key ('all')
when it exists, otherwise the dev and sealed halves separately; the hash halves of the new keys are in the table.
A hollow dot means that build was built or tuned with that key (or that half) in view.%s</p>
<h2>All results</h2>
<div class="tw">%s</div>
</main></body></html>
"""


def find_chrome():
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
        if os.path.exists(p):
            return p
    return shutil.which("chrome") or shutil.which("google-chrome")


def png(svg_light, W, H, out_png, width=1600):
    chrome = find_chrome()
    if not chrome:
        sys.stderr.write("no Chrome found; PNG skipped\n")
        return False
    scale = width / W
    tmpd = tempfile.mkdtemp(prefix="bmpng")
    page = os.path.join(tmpd, "p.html")
    with open(page, "w", encoding="utf-8", newline="\n") as f:
        f.write('<!doctype html><html data-theme="light"><head><meta charset="utf-8"><style>html,body{margin:0;'
                'background:#fcfcfb}svg{display:block;width:%dpx;height:%dpx}</style></head><body>%s</body></html>'
                % (width, round(H * scale), svg_light))
    shot = os.path.join(tmpd, "s.png")
    cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-color-profile=srgb",
           "--user-data-dir=" + os.path.join(tmpd, "prof"), "--window-size=%d,%d" % (width, round(H * scale)),
           "--screenshot=" + shot, "file:///" + page.replace("\\", "/")]
    try:
        subprocess.run(cmd, check=True, timeout=120, capture_output=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (subprocess.SubprocessError, OSError) as e:
        sys.stderr.write("PNG render failed: %s\n" % e)
        return False
    shutil.copyfile(shot, out_png)
    shutil.rmtree(tmpd, ignore_errors=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", default=DEFAULT_HTML)
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--bench", default=None, help="results root (default: benchmarks/)")
    a = ap.parse_args()
    res = load(a.bench)
    rows = build_rows(res)
    import datetime
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    wide, W, H = render(rows, True)
    narrow, _, _ = render(rows, False)
    outdir = os.path.dirname(os.path.abspath(a.html))
    os.makedirs(outdir, exist_ok=True)
    with open(a.html, "w", encoding="utf-8", newline="\n") as f:
        skipped = ""
        if SKIPPED:
            skipped = (" Not plotted (no k/n proportion; see their RUN.md): " +
                       ", ".join(esc(r["ref"].get("row_label", r["dataset"])) for r in SKIPPED) + ".")
        f.write(PAGE % (CSS, PAGE_NOTE, wide, narrow, stamp, len(res), skipped, table_html(res)))
    standalone = wide.replace('<svg class="bm" ', '<svg class="bm" ', 1).replace(
        "role=\"img\"", "role=\"img\"", 1)
    standalone = standalone.replace(">", "><style>%s</style>" % CSS.replace(":root:where(:not([data-theme=\"light\"])) .bm", ".bm").replace(":root[data-theme=\"dark\"] .bm", ".bm-forced-dark"), 1)
    with open(os.path.join(outdir, "benchmarks.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n' + standalone)
    light_css = CSS.split("@media")[0] + "".join(l + "\n" for l in CSS.splitlines() if l.startswith(".bm ."))
    if not a.no_png:
        png("<style>%s</style>%s" % (light_css, wide), W, H, os.path.join(outdir, "benchmarks.png"))
    if a.bench:  # test run on another results root: leave graph/ untouched
        print("rows %d, result files %d -> %s" % (len(rows), len(res), a.html))
        return
    for fn in ("benchmarks.svg", "benchmarks.png"):
        src = os.path.join(outdir, fn)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(HERE, fn))
    with open(os.path.join(HERE, "rows.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("dataset\tsplit\tlabel\tmetric\tk\tn\tp\tlo\thi\tblind\tsource\n")
        for row in rows:
            for m in row_lines(row):
                for b, v in pts(row, m):
                    f.write("%s\t%s\t%s\t%s\t%d\t%d\t%.4f\t%.4f\t%.4f\t%s\t%s\n" % (
                        row["dataset"], row["split"], b, m, v["k"], v["n"], v["p"], v["lo"] or 0, v["hi"] or 0,
                        int(row["ref"].get("blind", True)), row["builds"][b]["_path"]))
    print("rows %d, result files %d -> %s" % (len(rows), len(res), a.html))


if __name__ == "__main__":
    main()
