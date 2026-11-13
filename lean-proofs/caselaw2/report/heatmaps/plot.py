"""Render the vulnerability heatmaps from series/*.tsv (run compute.py first).

    python plot.py

Needs matplotlib, numpy and Pillow. Writes <name>.png (~2200 px wide), <name>.svg and <name>.webp (for the report),
and heatmaps.json (totals and peaks, read by make_report.py). Reads and writes beside this file, or under the
directory named by the environment variable HEATMAPS_OUT (the same one compute.py was given).
"""
import datetime as dt
import json
import os
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, Normalize  # noqa: E402
from PIL import Image  # noqa: E402

HERE = Path(os.environ["HEATMAPS_OUT"]) if os.environ.get("HEATMAPS_OUT") else Path(__file__).resolve().parent
SER = HERE / "series"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
INK, MUTED, FAINT = "#1a1a1a", "#555555", "#8a8a8a"
EMPTY = "#ebedf0"

plt.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "svg.fonttype": "none"})


def cmap_for():
    # pale grey (0) -> green -> yellow/orange -> red -> purple -> near-black, at the reference's proportions of 0-500
    stops = [(0.0, EMPTY), (0.02, "#c9eab8"), (0.15, "#3d9a4b"), (0.27, "#f1d23b"), (0.40, "#f39a24"),
             (0.55, "#d9302c"), (0.75, "#7a2e9a"), (1.0, "#160818")]
    return LinearSegmentedColormap.from_list("vuln", stops)


def load(name):
    days = {}
    with open(SER / f"{name}.tsv", encoding="utf-8") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        for line in f:
            a = line.rstrip("\n").split("\t")
            days[int(a[0])] = [int(x) for x in a[1:]]
    return hdr[2:], days


def ymd(d):
    return dt.date(d // 10000, d // 100 % 100, d % 100)


def nice(v):
    for m in (1, 2, 2.5, 4, 5, 8, 10):
        for e in range(0, 6):
            if m * 10 ** e >= v:
                return int(m * 10 ** e)
    return int(v)


def year_grid(year, counts):
    jan1 = dt.date(year, 1, 1)
    off = jan1.weekday()  # Monday = 0
    ndays = (dt.date(year + 1, 1, 1) - jan1).days
    ncol = (ndays + off + 6) // 7
    g = np.full((7, 54), np.nan)
    for i in range(ndays):
        d = jan1 + dt.timedelta(days=i)
        k = (i + off) // 7
        g[d.weekday(), k] = counts.get(d.year * 10000 + d.month * 100 + d.day, 0)
    month_cols = [((dt.date(year, m, 1) - jan1).days + off) // 7 for m in range(1, 13)]
    return g, month_cols, ncol


def heatmap(name, title, subtitle, unit, years, vmax, note, out_stem):
    parts, days = load(name)
    counts = {d: v[0] for d, v in days.items()}
    years = list(years)
    ncols = 2
    nrows = (len(years) + 1) // 2
    cm = cmap_for()
    norm = Normalize(0, vmax, clip=True)

    W = 11.0  # inches; 200 dpi -> 2200 px
    left_lab = 0.95  # year label block
    col_w = (W - 0.5 - 0.35) / 2
    grid_w = col_w - left_lab - 0.15
    cell = grid_w / 54
    panel_h = 7 * cell
    row_h = panel_h + 0.34
    sub_lines = [w for para in subtitle.splitlines() for w in textwrap.wrap(para, 140)]
    note_lines = [w for para in note.splitlines() for w in textwrap.wrap(para, 200)]
    top = 0.95 + 0.2 * len(sub_lines) + 0.35
    note_h = 0.13 * len(note_lines)
    bottom = 0.25 + note_h + 0.75
    H = top + nrows * row_h + bottom
    fig = plt.figure(figsize=(W, H), dpi=200, facecolor="white")
    fig.text(0.5 / W, 1 - 0.55 / H, title, fontsize=19, fontweight="bold", color=INK, va="baseline")
    for i, ln in enumerate(sub_lines):
        fig.text(0.5 / W, 1 - (0.95 + 0.2 * i) / H, ln, fontsize=10.5, color=MUTED, va="baseline")

    for idx, y in enumerate(years):
        col = idx // nrows
        row = idx % nrows
        x0 = 0.5 + col * (col_w + 0.35)
        y_top = H - top - row * row_h
        ax = fig.add_axes([(x0 + left_lab) / W, (y_top - panel_h) / H, grid_w / W, panel_h / H])
        g, mcols, ncol = year_grid(y, counts)
        X, Y = np.meshgrid(np.arange(55), np.arange(8))
        gm = np.ma.masked_invalid(g)
        ax.pcolormesh(X, Y, gm, cmap=cm, norm=norm, edgecolors="white", linewidth=0.55, antialiased=True)
        ax.set_xlim(0, 54)
        ax.set_ylim(7, 0)
        ax.set_aspect("equal")
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_xticks([c + 0.5 for c in mcols])
        ax.set_xticklabels(MONTHS, fontsize=5.6, color=FAINT)
        ax.tick_params(axis="x", length=0, pad=1.5)
        ax.set_yticks([0.5, 2.5, 4.5, 6.5])
        ax.set_yticklabels(["Mon", "Wed", "Fri", "Sun"], fontsize=5.2, color=FAINT)
        ax.tick_params(axis="y", length=0, pad=1.5)
        tot = sum(v for d, v in counts.items() if d // 10000 == y)
        fig.text((x0 + 0.02) / W, (y_top - panel_h * 0.42) / H, str(y), fontsize=12.5, fontweight="bold",
                 color=INK, va="baseline")
        fig.text((x0 + 0.02) / W, (y_top - panel_h * 0.42 - 0.2) / H, f"{tot:,}", fontsize=8, color=MUTED,
                 va="baseline")

    cax = fig.add_axes([(W / 2 - 2.4) / W, (0.25 + note_h + 0.5) / H, 4.8 / W, 0.14 / H])
    sm = plt.cm.ScalarMappable(cmap=cm, norm=norm)
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    ticks = np.linspace(0, vmax, 6)
    cb.set_ticks(ticks)
    cb.set_ticklabels([f"{int(t):,}" for t in ticks[:-1]] + [f"{int(vmax):,}+"])
    cb.ax.tick_params(labelsize=7.5, colors=MUTED, length=0, pad=2)
    cb.set_label(f"{unit} per Day", fontsize=8.5, color=MUTED, labelpad=3)
    for i, ln in enumerate(note_lines):
        fig.text(0.5 / W, (0.2 + note_h - 0.13 * (i + 1)) / H, ln, fontsize=6.6, color=FAINT, va="bottom")

    png = HERE / f"{out_stem}.png"
    fig.savefig(png, dpi=200, facecolor="white")
    fig.savefig(HERE / f"{out_stem}.svg", facecolor="white")
    plt.close(fig)
    im = Image.open(png).convert("RGB")
    im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
    im.save(HERE / f"{out_stem}.webp", "WEBP", quality=88, method=6)
    return im.size


def stats(name, years):
    parts, days = load(name)
    ys = set(years)
    inr = {d: v for d, v in days.items() if d // 10000 in ys}
    tot = sum(v[0] for v in inr.values())
    ptot = {p: sum(v[i + 1] for v in inr.values()) for i, p in enumerate(parts)}
    top = sorted(inr.items(), key=lambda kv: (-kv[1][0], kv[0]))[:8]
    allpk = max(days.items(), key=lambda kv: kv[1][0])
    wd = [0] * 7
    for d, v in inr.items():
        wd[ymd(d).weekday()] += v[0]
    nz = np.array([v[0] for v in inr.values()])
    return {"total": tot, "parts": ptot, "years": [min(years), max(years)],
            "peaks": [{"day": d, "count": v[0], **{p: v[i + 1] for i, p in enumerate(parts)}} for d, v in top],
            "all_years_peak": {"day": allpk[0], "count": allpk[1][0]}, "weekday": wd,
            "days_with_any": int(len(nz)), "p99": float(np.percentile(nz, 99)) if len(nz) else 0}


def fmt_day(d):
    return f"{MONTHS[d // 100 % 100 - 1]} {d % 100}, {d // 10000}"


def main():
    meta = json.loads((HERE / "series.json").read_text(encoding="utf-8"))
    res = {}
    causes = json.loads((SER / "usc_causes.json").read_text(encoding="utf-8"))

    # A. Decisions relying on bad law
    yrs = range(1990, 2020)
    s = stats("badlaw", yrs)
    pk = s["peaks"][0]
    vmax = 40
    p = s["parts"]
    sub = (f"{s['total']:,} decisions, {yrs[0]}–{yrs[-1]}, that cite as authority a decision already overruled, vacated, "
           f"reversed, withdrawn or superseded, or one not citable. Peak: {pk['count']} on {fmt_day(pk['day'])}.\n"
           f"Decisions with each finding (one may have several): cites overruled {p['citesOverruled']:,} · vacated or "
           f"reversed {p['citesVacated']:,} · withdrawn {p['citesWithdrawn']:,} · not citable {p['citesNotCitable']:,} · "
           f"superseded holding {p['appliesSupersededHolding']:,}")
    n_dec = meta.get("precision", {}).get("decisions")
    dec_txt = f"{n_dec / 1e6:.1f}M" if n_dec else "6.9M"
    note = (f"A decision is counted once, on the day it was decided, if the Lean run (caselaw-lean-2, {dec_txt} decisions, "
            "48M citation edges) finds citesOverruled, citesVacated, citesWithdrawn, citesNotCitable or "
            "appliesSupersededHolding for it: the cited decision's status was already negative on the citing date, "
            "in a court whose decisions bind it. Dates on the 1st of a month in court-years with a month-precision "
            f"pattern, and all 1 January dates, are dropped ({meta['badlaw']['dropped_imprecise']:,} decisions over all "
            "years). Bulk coverage thins after mid-2019. Sources: out/findings.tsv, data/decisions2.tsv.")
    res["badlaw"] = s | {"size": heatmap("badlaw", "Decisions Relying on Bad Law by Day (1990-2019)", sub,
                                          "Decisions", yrs, vmax, note, "caselaw_bad_law_by_day")}

    # B. Precedent broken
    s = stats("broken", yrs)
    pk = s["peaks"][0]
    p = s["parts"]
    sub = (f"{s['total']:,} admitted negative status events, {yrs[0]}–{yrs[-1]}: a decision loses force because a later "
           f"decision overrules, abrogates, reverses, vacates or withdraws it. Peak: {pk['count']} on "
           f"{fmt_day(pk['day'])}.\nOverruled or abrogated {p['overruled']:,} · reversed {p['reversed']:,} · "
           f"vacated {p['vacated']:,} · withdrawn {p['withdrawn']:,} · superseded by statute {p['superseded']:,} · "
           f"depublished {p['depublished']:,}")
    note = ("One event per witness row of an out/status.tsv negativeAdmitted row (a certified treatment or same-case "
            "history row that the Lean run gave effect: the treating court had power over the target), dated by the "
            "treating decision (data/treatments.tsv, data/history.tsv). Supersession by statute is dated by the day "
            "the effect starts. Dates on the 1st of a month in court-years with a month-precision pattern, and all "
            f"1 January dates, are dropped ({meta['broken']['dropped_imprecise']:,} events over all years). "
            "Bulk coverage thins after mid-2019.")
    res["broken"] = s | {"size": heatmap("broken", "Precedent Broken by Day (1990-2019)", sub, "Events", yrs, 10,
                                          note, "caselaw_precedent_broken_by_day")}

    # C. US Code, combined
    yrs = range(1995, 2027)
    s = stats("usc", yrs)
    pk = s["peaks"][0]
    p = s["parts"]
    cause = causes.get(str(pk["day"]), [["?", 0]])[0][0]
    sub = (f"{s['total']:,} defects introduced, {yrs[0]}–{yrs[-1]}. Peak: {pk['count']:,} on {fmt_day(pk['day'])} "
           f"({cause}{': title 54 enacted' if cause.startswith('Pub. L. 113-287') else ''}).\nCross-references that start to dangle {p['xref']:,} · amending instructions "
           f"whose struck words are not in the section {p['amend']:,} (laws since 2013) · duplicate sibling "
           f"designations {p['dup']:,}")
    note = ("Cross-references: an explicit reference (section, title, designation) that resolved and was broken by a "
            "later law or edition, or was written so it never resolved (uses/xrefs, episodes from the record start "
            "excluded; held-out audit 68% real). Amendments: Lean class not_found, laws of the 113th-119th Congresses, "
            "dated by enactment (uses/amendments; audit 18/20 real, of which 16 are the Code's editorial wording, not "
            "drafting errors; no_target 4/20, wrong_target 9/20 and ambiguous 7/20 were not mostly real and are left "
            "out). Duplicates: a designation appearing twice among siblings, by the version that first made it (13/20 "
            "real). Before 2017 the record dates changes on enactment.")
    res["usc"] = s | {"size": heatmap("usc", "US Code Vulnerabilities Introduced by Day (1995-2026)", sub,
                                       "Defects", yrs, 100, note, "uscode_vulnerabilities_by_day")}
    res["usc"]["peak_causes"] = {str(x["day"]): causes.get(str(x["day"])) for x in s["peaks"]}

    # D. one chart per US Code kind (same counts, split)
    for i, (part, ttl, unit, vm) in enumerate([("xref", "Cross-References Broken by Day (1995-2026)", "References", 50),
                                               ("amend", "Amendments Not Executable as Written by Day (2013-2026)",
                                                "Instructions", 20),
                                               ("dup", "Duplicate Designations Made by Day (1995-2026)",
                                                "Designations", 10)]):
        parts, days = load("usc")
        j = parts.index(part) + 1
        sub_days = {d: [v[j]] for d, v in days.items() if v[j]}
        tmp = SER / f"usc_{part}.tsv"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"day\tcount\t{part}\n")
            for d in sorted(sub_days):
                f.write(f"{d}\t{sub_days[d][0]}\t{sub_days[d][0]}\n")
        yy = range(2013, 2027) if part == "amend" else range(1995, 2027)
        s = stats(f"usc_{part}", yy)
        pk = s["peaks"][0]
        c = causes.get(str(pk["day"]), [["?", 0]])[0][0]
        sub = f"{s['total']:,} in {yy[0]}–{yy[-1]}. Peak: {pk['count']:,} on {fmt_day(pk['day'])} (largest cause that day: {c})."
        res[f"usc_{part}"] = s | {"size": heatmap(f"usc_{part}", ttl, sub, unit, yy, vm,
                                                   "Same definitions as the combined US Code chart.",
                                                   f"uscode_{part}_by_day")}
    (HERE / "heatmaps.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: {"total": v["total"], "peak": v["peaks"][0]} for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    main()
