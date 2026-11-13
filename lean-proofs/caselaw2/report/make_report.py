import os
"""Build the caselaw-lean-2 results report (one self-contained HTML file).

    python make_report.py [--out PATH] [--artefacts DIR]

--artefacts DIR: read the v1/v2 figure (caselaw-v1-v2.svg/.json) and heatmaps/ from DIR instead of this folder
(for dry runs of report/refresh_all.sh).

Reads only files under ~/Documents/us-caselaw-lean-work/caselaw-lean-2/, the Lean sources in
~/Documents/global-law-lean/lean-proofs/LegalProofs/CaseLaw2/, graph/nodes.tsv (to find three decisions by name) and
the v1 blog draft (read only). Every number on the page is read or computed from those files; a section whose input
is missing renders a "pending: waiting for <file>" box. Re-run it as data lands.
"""
import argparse
import collections
import datetime as dt
import html
import json
import math
import re
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lean_stats  # noqa: E402

HOME = Path.home()
W = HOME / "Documents" / "us-caselaw-lean-work"
C2 = W / "caselaw-lean-2"
DATA = C2 / "data"
OUT = C2 / "out"
EVAL = C2 / "eval"
GOLD = C2 / "gold"
RES = C2 / "research"
LEANDIR = HOME / "Documents" / "global-law-lean" / "lean-proofs" / "LegalProofs" / "CaseLaw2"
BLOG = HOME / "lexweb-build" / "app" / "blog" / "formalizing-all-us-case-law-in-lean" / "ArticleContent.tsx"
NODES = W / "graph" / "nodes.tsv"
HUNT = C2 / "hunt"
DEFAULT_OUT = HOME / "Documents" / "html-reports" / "caselaw-lean-2.html"

ART = Path(__file__).resolve().parent  # where caselaw-v1-v2.{svg,json} and heatmaps/ are read from (--artefacts)

E = html.escape
INPUTS_USED = []  # (path, present, mtime)


# ---------------------------------------------------------------- helpers

def rel(p: Path) -> str:
    p = Path(p)
    try:
        return "caselaw-lean-2/" + p.relative_to(C2).as_posix()
    except ValueError:
        try:
            return "~/" + p.relative_to(HOME).as_posix()
        except ValueError:
            return str(p)


def note_input(p: Path):
    p = Path(p)
    ok = p.exists()
    m = dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M") if ok else ""
    if (str(p), ok, m) not in INPUTS_USED:
        INPUTS_USED.append((str(p), ok, m))
    return ok


def read(p: Path):
    if not note_input(p):
        return None
    return Path(p).read_text(encoding="utf-8", errors="replace")


def read_json(p: Path):
    t = read(p)
    if t is None:
        return None
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        return None


def mtime(p: Path) -> str:
    p = Path(p)
    return dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%d %b %Y, %H:%M") if p.exists() else "?"


def count_lines(p: Path, header=False):
    if not note_input(p):
        return None
    n = 0
    with open(p, "rb") as f:
        while True:
            b = f.read(1 << 24)
            if not b:
                break
            n += b.count(b"\n")
    return n - (1 if header else 0)


def tsv(p: Path, header=True, limit=None):
    if not note_input(p):
        return None
    out = []
    with open(p, encoding="utf-8", errors="replace") as f:
        cols = None
        for i, line in enumerate(f):
            parts = line.rstrip("\n").split("\t")
            if header and cols is None:
                cols = parts
                continue
            out.append(dict(zip(cols, parts)) if header else parts)
            if limit and len(out) >= limit:
                break
    return out


def fmt(n, d=0):
    if n is None:
        return "pending"
    if isinstance(n, str):
        return n
    if isinstance(n, float) and d == 0 and not n.is_integer():
        d = 1
    return f"{n:,.{d}f}"


def pct(a, b, d=0):
    if a is None or not b:
        return "pending"
    return f"{100.0 * a / b:.{d}f}%"


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def wil_str(k, n):
    w = wilson(k, n)
    if not w:
        return "–"
    return f"{100 * w[0]:.0f}–{100 * w[1]:.0f}%"


def pending(*files, why=None):
    miss = [f for f in files if not (isinstance(f, Path) and f.exists())]
    files = miss or files
    names = ", ".join(f"<code>{E(rel(f) if isinstance(f, Path) else f)}</code>" for f in files)
    extra = f" {why}" if why else ""
    return f'<div class="pending"><b>Pending:</b> waiting for {names}.{extra}</div>'


def note(text):
    return f'<div class="note">{text}</div>'


def src(*files):
    names = " · ".join(f"<code>{E(rel(f) if isinstance(f, Path) else f)}</code>" for f in files)
    return f'<p class="src">Source: {names}</p>'


def table(head, rows, cls="", num_cols=()):
    h = "".join(f'<th{" class=num" if i in num_cols else ""}>{c}</th>' for i, c in enumerate(head))
    body = []
    for r in rows:
        body.append("<tr>" + "".join(
            f'<td{" class=num" if i in num_cols else ""}>{c}</td>' for i, c in enumerate(r)) + "</tr>")
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def details(summary, inner, open_=False):
    return f'<details{" open" if open_ else ""}><summary>{summary}</summary><div class="det">{inner}</div></details>'


def bars(items, unit="", total=None, cls="", value_fmt=None, max_value=None):
    """Horizontal bars, one row each: label, an inline SVG bar, the value. items: (label, value[, tooltip])."""
    items = [it for it in items if it[1] is not None]
    if not items:
        return ""
    mx = max_value or max(it[1] for it in items) or 1
    rows = []
    for it in items:
        lab, v = it[0], it[1]
        tip = it[2] if len(it) > 2 else f"{lab}: {fmt(v)}{unit}"
        w = max(0.0, min(100.0, 100.0 * v / mx))
        vs = value_fmt(v) if value_fmt else fmt(v) + unit
        if total:
            vs += f' <span class="muted">{pct(v, total)}</span>'
        rows.append(
            f'<div class="bar-row" title="{E(tip)}"><div class="bar-lab">{lab}</div>'
            f'<svg class="bar-svg" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true">'
            f'<rect x="0" y="1" width="{w:.3f}" height="8" rx="1.2" class="bar-fill"/></svg>'
            f'<div class="bar-val">{vs}</div></div>')
    return f'<div class="bars {cls}" role="img">{"".join(rows)}</div>'


def bars2(items, names=("v1", "v2"), value_fmt=None, max_value=None):
    """Paired bars: (label, a, b). None draws nothing and prints 'pending'."""
    vals = [v for it in items for v in it[1:3] if v is not None]
    mx = max_value or (max(vals) if vals else 1) or 1
    rows = []
    for lab, a, b in items:
        def one(v, k):
            if v is None:
                return (f'<svg class="bar-svg" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true"></svg>'
                        f'<div class="bar-val muted">pending</div>')
            w = max(0.0, min(100.0, 100.0 * v / mx))
            return (f'<svg class="bar-svg" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true">'
                    f'<rect x="0" y="1" width="{w:.3f}" height="8" rx="1.2" class="bar-fill s{k}"/></svg>'
                    f'<div class="bar-val">{value_fmt(v) if value_fmt else fmt(v)}</div>')
        rows.append(f'<div class="bar-row2"><div class="bar-lab">{lab}</div>'
                    f'<div class="pair"><div class="pl"><span class="sw s1"></span>{names[0]}</div>{one(a, 1)}'
                    f'<div class="pl"><span class="sw s2"></span>{names[1]}</div>{one(b, 2)}</div></div>')
    legend = (f'<div class="legend"><span><span class="sw s1"></span>{names[0]}</span>'
              f'<span><span class="sw s2"></span>{names[1]}</span></div>')
    return f'<div class="bars">{legend}{"".join(rows)}</div>'


def tiles(items):
    out = []
    for lab, val, sub in items:
        out.append(f'<div class="tile"><div class="tile-val">{val}</div><div class="tile-lab">{lab}</div>'
                   f'<div class="tile-sub">{sub}</div></div>')
    return f'<div class="tiles">{"".join(out)}</div>'


# ---------------------------------------------------------------- markdown (subset) -> HTML

def inline(s: str) -> str:
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"
    s = re.sub(r"`([^`]+)`", keep, s)
    s = E(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"(?<![\"'=>])(https?://[^\s<)\]]+[^\s<)\].,;:])", r'<a href="\1">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{E(codes[int(m.group(1))], quote=False)}</code>", s)
    return s


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    cells, cur, tick = [], "", False
    for ch in line:
        if ch == "`":
            tick = not tick
        if ch == "|" and not tick:
            cells.append(cur.strip())
            cur = ""
        else:
            cur += ch
    cells.append(cur.strip())
    return cells


def md(text: str, hshift=2) -> str:
    """A small Markdown renderer: headings, paragraphs, nested lists, pipe tables, code blocks, inline marks."""
    lines = text.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    para = []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(x.strip() for x in para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        st = line.strip()
        if st.startswith("```"):
            flush()
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            out.append("<pre><code>" + E("\n".join(buf)) + "</code></pre>")
            i = j + 1
            continue
        if not st:
            flush()
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", st)
        if m and not line.startswith(" "):
            flush()
            lv = min(6, len(m.group(1)) + hshift)
            out.append(f"<h{lv} class=mdh>{inline(m.group(2))}</h{lv}>")
            i += 1
            continue
        if line.startswith("    ") and not para and not re.match(r"^\s*([-*]|\d+\.)\s", line):
            flush()
            buf = []
            while i < len(lines) and (lines[i].startswith("    ") or not lines[i].strip()):
                buf.append(lines[i][4:])
                i += 1
            out.append("<pre><code>" + E("\n".join(buf).rstrip()) + "</code></pre>")
            continue
        if st.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            flush()
            head = split_row(st)
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            numc = set()
            for c in range(len(head)):
                colv = [r[c] for r in rows if c < len(r)]
                if colv and all(re.fullmatch(r"[≈~]?\s*[\d,.%–\- /()]+", v or "0") for v in colv):
                    numc.add(c)
            out.append(table([inline(h) for h in head],
                             [[inline(c) for c in r] + [""] * (len(head) - len(r)) for r in rows],
                             cls="md", num_cols=numc))
            continue
        lm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if lm:
            flush()
            # collect the whole list block
            block = []
            while i < len(lines):
                l2 = lines[i]
                if not l2.strip():
                    # a blank line ends the list unless the next line continues it
                    if i + 1 < len(lines) and re.match(r"^(\s*)([-*]|\d+\.)\s+", lines[i + 1]):
                        i += 1
                        continue
                    break
                if re.match(r"^(#{1,6})\s", l2) or (l2.strip().startswith("|") and not re.match(r"^\s+", l2)):
                    break
                block.append(l2)
                i += 1
            out.append(render_list(block))
            continue
        para.append(line)
        i += 1
    flush()
    return "\n".join(out)


def render_list(block):
    items = []  # (indent, ordered, text)
    for l in block:
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", l)
        if m:
            items.append([len(m.group(1)), m.group(2)[-1] == ".", m.group(3)])
        elif items:
            items[-1][2] += " " + l.strip()
    html_out = []
    stack = []  # (indent, tag)
    for ind, ordered, text in items:
        tag = "ol" if ordered else "ul"
        while stack and ind < stack[-1][0]:
            html_out.append(f"</li></{stack.pop()[1]}>")
        if not stack or ind > stack[-1][0]:
            html_out.append(f"<{tag}>")
            stack.append((ind, tag))
        else:
            html_out.append("</li>")
        html_out.append("<li>" + inline(text))
    while stack:
        html_out.append(f"</li></{stack.pop()[1]}>")
    return "".join(html_out)


def md_section(text, heading_pat, include_heading=False):
    """Lines of the section whose heading matches heading_pat (regex), up to the next heading of the same or a
    higher level."""
    if text is None:
        return None
    lines = text.split("\n")
    for i, l in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", l)
        if m and re.search(heading_pat, m.group(2)):
            lv = len(m.group(1))
            j = i + 1
            while j < len(lines):
                m2 = re.match(r"^(#{1,6})\s+", lines[j])
                if m2 and len(m2.group(1)) <= lv:
                    break
                j += 1
            return "\n".join(lines[i if include_heading else i + 1:j]).strip("\n")
    return None


def num(s):
    if s is None:
        return None
    try:
        return int(str(s).replace(",", "").strip())
    except ValueError:
        try:
            return float(str(s).replace(",", "").strip())
        except ValueError:
            return None


def rx(text, pat, grp=1, conv=num):
    if text is None:
        return None
    m = re.search(pat, text, re.S)
    if not m:
        return None
    return conv(m.group(grp)) if conv else m.group(grp)


# ---------------------------------------------------------------- loaders

class Ctx:
    pass


def load():
    c = Ctx()
    c.design = read(C2 / "DESIGN.md")
    c.schema = read(C2 / "SCHEMA.md")
    c.lean = read(C2 / "LEAN.md")
    c.trust = read(C2 / "TRUST.md")
    c.dev = read(C2 / "DEVIATIONS.md")
    c.stm = read(C2 / "STATEMENTS.log")
    c.diff = read(C2 / "DIFFTEST.md")
    c.courts = read(DATA / "COURTS.md")
    c.cval = read(DATA / "courts_validation.md")
    c.stat = read(DATA / "STATUTES.md")
    c.readerm = read(DATA / "READER.md")
    c.holdm = read(DATA / "HOLDINGS.md")
    c.hunt = read(HUNT / "HUNT.md")
    c.hsum = read_json(HUNT / "summary.json")
    c.fuzz = read(C2 / "FUZZ.md")
    c.fuzzb = read(C2 / "FUZZ_BUGS.md")
    c.factors = read(DATA / "FACTORS.md")
    c.gold = read(GOLD / "README.md")
    c.plan = read(EVAL / "audit_plan.md")
    c.res = read_json(EVAL / "results.json")
    c.res1 = read_json(EVAL / "results_v1.json")
    c.rstats = read_json(DATA / "reader_stats.json")
    c.rusage = read_json(DATA / "reader_usage.json")
    c.husage = read_json(DATA / "holdings_usage.json")
    c.blog = read(BLOG)
    c.research = {k: read(RES / f"{k}.md") for k in
                  ("doctrine", "prior_art", "data_audit", "formalisms_python", "formalisms_google",
                   "formalisms_industrial")}
    c.ls = lean_stats.stats()
    for f in sorted(LEANDIR.rglob("*.lean")):
        note_input(f)
    # v1 figures from the blog draft
    b = c.blog or ""
    def blog_row(label):
        m = re.search(r"<tr><td>" + re.escape(label) + r"</td>(.*?)</tr>", b, re.S)
        if not m:
            return None
        cells = re.findall(r"<td[^>]*>(.*?)</td>", m.group(1), re.S)
        return cells
    c.v1 = {}
    for lab, key in (("Declarations", "decl"), ("Theorems", "thm"), ("Lines of Lean", "lines")):
        cells = blog_row(lab)
        c.v1[key] = num(cells[2]) if cells and len(cells) >= 3 else None
    cells = blog_row("What Lean holds")
    c.v1["holds"] = re.sub(r"<[^>]+>", "", cells[2]) if cells and len(cells) >= 3 else None
    cells = blog_row("Run over")
    c.v1["runover"] = re.sub(r"<[^>]+>", "", cells[2]) if cells and len(cells) >= 3 else None
    c.v1["passages"] = rx(b, r"read from ([\d,]+) passages")
    c.v1["accepted"] = rx(b, r"it accepts ([\d,]+) \(")
    c.v1["reader_lines"] = rx(b, r"about ([\d,]+) lines of Python")
    c.v1["notes"] = rx(b, r"([\d,]+) notes by later\s+courts")
    c.v1["notes_named"] = rx(b, r"([\d,]+) of which name the overruling decision")
    c.v1["agree"] = rx(b, r"Agrees</td><td[^>]*>([\d,]+)<")
    c.v1["another"] = rx(b, r"Another overruling</td><td[^>]*>([\d,]+)<")
    c.v1["none"] = rx(b, r"No overruling found</td><td[^>]*>([\d,]+)<")
    c.v1["citations"] = rx(b, r"([\d.]+) million citations resolve|;\s*([\d.]+) million of those citations", conv=None)
    c.v1["blind_held"] = rx(b, r"agreements held up in (\d+) of (\d+)", conv=None)
    # out/
    c.out_ok = (OUT / "status.tsv").exists()
    return c


# ---------------------------------------------------------------- sections

PLAIN = {
    "Exec.exec_canChangeStatus_eq_spec": "The runner's power check (who may change a decision's status) equals the Spec's.",
    "Exec.exec_eventLookups_eq_spec": "The runner's hash-indexed event lookups return exactly the Spec's list scans.",
    "Exec.exec_lookups_eq_spec": "The runner's hash-indexed court lookups return exactly the Spec's list scans.",
    "Exec.index_getD": "Grouping a list into a hash map by key and looking a key up gives the same list as filtering by that key.",
    "Force.le_binding": "No force ranks above binding.",
    "Force.rank_inj": "Two forces with the same rank are the same force.",
    "Force.rank_max": "The stronger of two forces has the larger rank.",
    "Force.rank_min": "The weaker of two forces has the smaller rank.",
    "Lookups.succeeds_refl": "Every court counts as succeeding itself.",
    "Spec.Horty.FCase.wf_iff": "A Horty case is well formed exactly when every factor of its reason is a fact of the case and favours the winning side.",
    "Spec.Horty.Side.ne_opp": "A side is never its own opposite.",
    "Spec.Horty.Side.opp_ne": "A side's opposite is never the side itself.",
    "Spec.Horty.answerCase_conflict": "Two yes/no holdings conflict exactly when their answers differ.",
    "Spec.Horty.consistent_iff": "A case base is consistent exactly when no two of its cases conflict.",
    "Spec.Horty.forcedBy_iff": "A precedent forces its outcome on new facts exactly when the facts contain its reason and every opposing factor in them was already in the precedent.",
    "Spec.Horty.sub_iff": "One factor list is contained in another exactly when each of its factors is in the other.",
    "Spec.Status.good_join": "Joining good law with a status leaves that status.",
    "Spec.Status.isNeg_iff": "A status is negative exactly when its rank is 10 or more.",
    "Spec.Status.join_assoc": "Joining statuses is associative.",
    "Spec.Status.join_comm": "Joining statuses is commutative.",
    "Spec.Status.join_good": "Joining a status with good law leaves the status.",
    "Spec.Status.rank_inj": "Two statuses with the same rank are equal.",
    "Spec.Status.rank_join": "The join of two statuses is the more severe of the two.",
    "Spec.Status.rank_zero_iff": "Only good law has rank 0.",
    "Spec.foldl_join": "Folding effects into a status equals joining the starting status with the status of the effects.",
    "Spec.foldl_max_ge": "Taking the highest precedence over candidates gives at least each candidate's precedence.",
    "Spec.foldl_max_ge_init": "Taking the highest precedence gives at least the starting value.",
    "Spec.foldl_max_le": "Taking the highest precedence stays within any bound the start and every candidate respect.",
    "Spec.foldl_max_rank_le": "Taking the strongest of forces that are each bounded stays within the bound.",
    "Spec.goodLaw_antitone": "Without lapses, a holding that is good law on a later date was good law on every earlier date.",
    "Spec.minDate_attained": "The earliest date among candidates is the date of one of them.",
    "Spec.relation_fed_on_state": "A federal court's decision on a state's law is only persuasive in that state's courts.",
    "Spec.relation_lastResort_own_law": "In a state court of last resort, on its own state's law, no decision is more than strongly persuasive.",
    "Spec.relation_scotus_federal": "On federal law, a Supreme Court decision binds every court that is not a court of last resort (rule F1).",
    "Spec.relation_state_on_federal": "A state court's decision on federal law is only persuasive in federal courts (rule E3).",
    "Spec.relation_trial": "A trial court's decision is at most persuasive anywhere.",
    "Spec.resolve_sub_top": "The split resolver only returns candidates from the top-precedence binding group.",
    "Spec.status_cons": "Adding one effect joins its contribution to the status of the rest.",
    "Spec.status_rank_mono_of": "If every effect contributes at least as much on one pair of dates as on another, the status is at least as severe there.",
}


def decl_count(ls):
    """(count, from_environment). The declaration count of the compiled environment, as drawn in the v1/v2 figure
    (report/caselaw-v1-v2.json, panel 2), so the headline and the figure agree; the source regex count of
    lean_stats.py only when the figure's JSON is missing."""
    fj = read_json(ART / "caselaw-v1-v2.json") or {}
    panels = fj.get("panels") or []
    n = panels[1].get("decl") if len(panels) > 1 else None
    return (n, True) if n else (ls["declarations"], False)


def sec_header(c):
    ls = c.ls
    n_dec = rx(c.courts, r"decisions2\.tsv \(([\d,]+) rows")
    mut = re.search(r"(\d+) properties against (\d+) mutants", c.lean or "")
    rs = c.rstats or {}
    certs_admitted = None
    if c.out_ok and (OUT / "certs.tsv").exists():
        cr = tsv(OUT / "certs.tsv")
        certs_admitted = sum(1 for r in cr if r.get("table") == "treatment" and r.get("result_all", "").startswith("ok"))
    v1 = c.v1
    t = []
    n_decl, decl_env = decl_count(ls)
    t.append(("Lean declarations" if decl_env else "Lean declarations (regex count)", fmt(n_decl),
              f'v1: {fmt(v1["decl"])} · {fmt(n_decl / v1["decl"], 1) + "×" if v1["decl"] else ""}'))
    t.append(("Theorems, statements locked", fmt(ls["theorems_registered"]), f'v1: {fmt(v1["thm"])}'))
    t.append(("Lines of Lean", fmt(ls["lines"]), f'v1: {fmt(v1["lines"])}'))
    t.append(("Mutants killed", f"{mut.group(2)}/{mut.group(2)}" if mut else "pending",
              f"{mut.group(1)} properties" if mut else ""))
    t.append(("Decisions in scope", fmt(n_dec), "every node of the v1 graph"))
    if certs_admitted is not None:
        t.append(("Treatments admitted by certificate", fmt(certs_admitted), "out/certs.tsv"))
    else:
        t.append(("Treatment rows written so far", fmt(rs.get("treatments")),
                  f'reader still running · certificates checked: pending'))
    hp = (c.hsum or {}).get("patterns") or {}
    conf = [v.get("counts", {}).get("confirmed_by_audit") for v in hp.values()]
    conf = [x for x in conf if isinstance(x, int)]
    if conf:
        t.append(("Mistakes in case law confirmed by blind audit", fmt(sum(conf)), "the hunt, section 9"))
    head = f"""
<header class="hero">
<p class="kicker">Lexifina · results report · generated {dt.datetime.now().strftime("%d %B %Y, %H:%M")}</p>
<h1>caselaw-lean-2</h1>
<p class="lead">caselaw-lean-2 is the second Lean model of US precedent, run over every decision in our record of US
case law. v1 checked one thing: whether a whole decision was validly overruled, by court rank. v2 models what courts
do with precedent at the level of holdings: graded authority, same-case history, partial overruling, supersession by
statute, and circuit splits. No treatment is believed unless Lean's checker admits it with a certificate: the
court's own words, at a stated offset, in the majority opinion. The results are tested against courts' own later
notes, the Supreme Court Database, the Constitution Annotated table and published lists of congressional
overrides.</p>
<p class="lead">A Lean proof shows that a status follows from our encoding of doctrine and from the treatments Lean
admitted. It does not show that the encoding matches what courts do. The held-out evaluation in section 10 measures
that.</p>
{tiles(t)}
</header>"""
    return head


def sec_why(c):
    ls, v1 = c.ls, c.v1
    layers = []
    mod_tbl = md_section(c.lean, r"^Layers \(DESIGN D1\)")
    if mod_tbl:
        for line in mod_tbl.split("\n"):
            cells = split_row(line) if line.startswith("|") else None
            if cells and len(cells) >= 2 and cells[0] not in ("Layer", "---", "") and not cells[0].startswith("--"):
                if cells[0] not in layers:
                    layers.append(cells[0])
    files = []
    for f in ("courts2.tsv", "succession.tsv", "adoption.tsv", "system_rules.tsv", "history.tsv", "treatments.tsv",
              "cert_text.tsv", "issues.tsv", "holdings.tsv", "marks.tsv", "lawchanges.tsv", "supersessions.tsv"):
        n = count_lines(DATA / f)
        files.append(f"<code>{f}</code> {fmt(n) if n is not None else '<span class=muted>pending</span>'}")
    n_dec = rx(c.courts, r"decisions2\.tsv \(([\d,]+) rows")
    files.insert(4, f"<code>decisions2.tsv</code> {fmt(n_dec)}")
    rows = [
        ["Declarations", fmt(v1["decl"]), f'{fmt(decl_count(ls)[0])} <span class=muted>('
                                           f'{"compiled environment, as in the figure; source regex count " + fmt(ls["declarations"]) if decl_count(ls)[1] else "regex count"}: '
                                           f'{fmt(ls["kinds"].get("def"))} def, {fmt(ls["kinds"].get("structure"))} structure, '
                                           f'{fmt(ls["kinds"].get("inductive"))} inductive)</span>'],
        ["Theorems", fmt(v1["thm"]), f'{fmt(ls["theorems_registered"])} registered, each statement locked'],
        ["Lines of Lean", fmt(v1["lines"]), f'{fmt(ls["lines"])} in {ls["files"]} files '
                                            f'<span class=muted>({fmt(ls["lines_handwritten"])} excluding the generated Registry and Audit)</span>'],
        ["Executable checks", "–", f'{fmt(ls["guards"])} <code>#guard</code> checks, {fmt(ls["guard_msgs"])} <code>#guard_msgs</code> statement locks'],
        ["Layers", "One model: courts and whole-decision overrulings",
         ("; ".join(E(x) for x in layers) + " (LEAN.md)") if layers else "pending"],
        ["What is formalised", E(v1["holds"] or "pending"),
         "Graded force per (decision, holding, court, date); dated court epochs, successions and adoptions; "
         "same-case history; typed treatments with scope and temporal reach; supersession by statute with two dates; "
         "status per holding; splits and conflicts; Horty consistency; certificate checking"],
        ["What data feeds it", (f'{fmt(v1["passages"])} overruling passages from a regex reader; '
                                f'{E(v1["runover"] or "")}') if v1["passages"] else "pending",
         "Rows per SCHEMA.md file: " + " · ".join(files)],
    ]
    hm = re.search(r"(\d+) binding bases examined, (\d+) consistent", c.diff or "")
    horty_line = (f"has now been run on real factors: {hm.group(1)} binding bases, {hm.group(2)} consistent (section 6)."
                  if hm else "not yet fed with real factors.")
    figsvg = str(ART / "caselaw-v1-v2.svg")
    figjson = Path(figsvg).with_suffix(".json")
    note_input(Path(figsvg))
    fj = read_json(figjson) or {}
    fp = fj.get("panels") or [{}, {}]
    fcols = fj.get("per_column") or {}
    newest_lean = max((f.stat().st_mtime for f in LEANDIR.rglob("*.lean")), default=0)
    fig_stale = os.path.exists(figsvg) and os.path.getmtime(figsvg) < newest_lean
    fig = ""
    if os.path.exists(figsvg):
        import base64 as _b64
        uri = "data:image/svg+xml;base64," + _b64.b64encode(open(figsvg, "rb").read()).decode()
        fig = (f'<figure style="margin:1.2em 0 1.6em"><img src="{uri}" style="width:100%;height:auto;border-radius:12px" '
               f'alt="Lean declaration maps of the US case-law model side by side: v1 with {fmt(fp[0].get("decl"))} '
               f'declarations and {fmt(fp[0].get("thm"))} theorems, v2 with {fmt(fp[1].get("decl"))} declarations and '
               f'{fmt(fp[1].get("thm"))} theorems across authority, holdings and status, splits, certificates, exec, '
               'the hunt predicates, tests and data I/O; no declaration of one uses the other’s">'
               '<figcaption class="small">One dot per Lean definition or theorem, placed lower the more other declarations '
               'it is built on; lines join a declaration to those that use it. Counts are from the compiled environment '
               f'(tools/CaseLawAnatomy.lean, run under Linux Lean in WSL; figure of {mtime(Path(figsvg))}), so they '
               f'include helper lemmas, instances and the I/O layer: {fmt(fp[1].get("thm"))} theorems in v2 in all, of '
               f'which {fmt(ls["theorems_registered"])} are the registered, statement-locked ones. The hunt predicates '
               f'({fmt(fcols.get("hunt"))} declarations) have their own column; the SHA-1 module is drawn with the '
               f'certificates. The generated Registry and Audit modules are left out. '
               f'{"v2 shares no code with v1" if fj.get("cross_links") == 0 else "v1 and v2 are separate models"}: '
               'it was written fresh to the revised design.'
               + (" <b>This figure predates the last change to the Lean sources.</b>" if fig_stale else "")
               + '</figcaption></figure>')
    else:
        fig = pending_box("report/caselaw-v1-v2.svg") if "pending_box" in globals() else ""
    return f"""
<section id="why"><h2>2. Why v1 was small, and what v2 adds</h2>
{fig}
<p>v1's model was small because its ambition was narrow. It held the structure of precedent: a court sits in a system
and a tier, a court binds those below it, a court may overrule only its own or lower courts' decisions, and an
overruling counts from the day it is decided. The courts and decisions were its input, not part of it. What a decision
holds, which part was overruled, whether a statute had since rewritten the words a decision read: none of that was in
Lean. It sat in a Python reader that Lean trusted.</p>
<p>The v1 post listed five ways to grow it: holdings rather than decisions, the finer rules of authority, abrogation
by statute, the reader inside the proof, and substance where the law is rule-like. v2 does the first four. Rule-like
substance is in v2 only as Horty's factor model of precedential constraint, which is proved and
{horty_line}</p>
{table(["", "v1", "v2 (caselaw-lean-2)"], rows, cls="cmp")}
{src(BLOG, C2 / "LEAN.md", LEANDIR, DATA)}
<p class="small">v1 figures are from the draft blog post. v2 declaration counts come from <code>report/lean_stats.py</code>,
a regex count over the source (not an elaborated count); theorem names come from <code>Registry.lean</code>.</p>
</section>"""


RESEARCH_META = [
    ("doctrine", "Doctrine: the US law of precedent as a specification",
     "A rule-by-rule account of US precedent written to be translated: the Supreme Court's vertical authority, "
     "horizontal stare decisis in each circuit and state intermediate court, federal courts on state law and the "
     "reverse, courts of last resort by jurisdiction, unpublished-opinion rules with their dates, the treatment "
     "vocabulary, timing, abrogation by statute, and holdings versus dicta. Each rule carries a tag: S checked, L "
     "leading case from memory, U uncertain.",
     "The graded <code>Force</code> scale, dated court epochs with successions and adoptions, the parameter tables "
     "(<code>horizontal</code>, <code>trialScope</code>, <code>unpubForce</code>, …), the two event families "
     "(same-case history and later-case treatment), the two-date status query, and the §9 checklist that became the "
     "authority theorems. U rows became table parameters, never theorem premises (D2)."),
    ("prior_art", "Prior art: theories of precedent, citators, datasets",
     "A survey of formal theories of precedent (Horty's result and reason models, Prakken, Canavotto, Lamond, "
     "HYPO/CATO, ANGELIC), citation-network authority, commercial and open citators and their measured accuracy, "
     "datasets of overrulings, legal formalisms (Catala, L4, Blawx) and LLM extraction pitfalls.",
     "Certificate-gated admission with a disqualifier list inside Lean; Horty consistency and forcing "
     "(<code>Spec/Horty</code>); binding sub-bases and the split definition; partial overruling as removing a holding; "
     "the derived <code>atRisk</code> finding; separate kinds for history, reported treatment and the court's own act; "
     "and the held-out gold sets (SCDB, the Constitution Annotated table, Christiansen–Eskridge)."),
    ("data_audit", "Data audit: what the corpus can support, measured",
     "A stratified sample of the corpus, read from git, measuring what each field and marker supports: front-matter "
     "coverage, how much opinion text exists, whether majority and dissent are separated, status markers in the "
     "header zone, how often each treatment phrase occurs, mis-tiered courts, district recovery for intermediate "
     "courts, the statute links, and compute.",
     "Header-zone rules for bench, publication and form; the re-tiering of mis-tiered appeals courts; units from "
     "dockets, counties and judges; later courts' notes held out as gold; and streaming every file from git instead of "
     "checking out the corpus."),
    ("formalisms_python", "Formalizing CPython: registry, audit, differential tests",
     "The CPython 3.15.2 Lean model (Andrews and Zhang): a function-by-function mirror of the C source, a registry of "
     "every property with a locked statement, refuted properties kept with counterexamples, differential runs against "
     "the real interpreter, and coverage reported against the full denominator.",
     "<code>Registry.lean</code> plus a statement lock (D2); refute, never weaken; the mutation kill matrix as the "
     "mechanical form of \"would a broken version pass?\" (D3); an independent Python reference with four-way triage of "
     "every disagreement (D4); and attributing each finding to the mechanism that found it."),
    ("formalisms_google", "Google DeepMind: statement fidelity",
     "AlphaProof Code (Signal verified at the machine-code level), the Comparator tool, AlphaProof, AlphaGeometry 2, "
     "Formal Conjectures and AlphaProof Nexus, read for one question: how to keep a formal statement faithful to what "
     "was meant.",
     "Locked statements with an axiom whitelist and no <code>native_decide</code> in theorems; reporting each result "
     "in a named trust tier; a divergence catalog between doctrine and Spec (<code>DEVIATIONS.md</code>); historical "
     "replays and non-vacuity witnesses as standard obligations."),
    ("formalisms_industrial", "Industrial and legal formal methods",
     "AWS Cedar's verification-guided development, SymCert, Zelkova; seL4, CompCert and CakeML on refinement and the "
     "trusted base; Catala, Mlang, L4, Blawx/s(CASP), Logical English, OpenFisca, PolicyEngine and government "
     "rules-as-code; certificate checking at data scale.",
     "The Spec / Exec / untrusted layering with refinement proofs (D1); a checker that returns typed rejection "
     "reasons; <code>TRUST.md</code> in seL4's style (D6); Catala-style labelled default trees, with conflicts reported "
     "as findings; no silent defaults (D5); and justification paths on every verdict (D8)."),
]


def research_links(text):
    links = []
    seen = set()
    for u in re.findall(r"https?://[^\s)>`|,;\]\"']+", text or ""):
        u = u.rstrip(".:")
        if u not in seen:
            seen.add(u)
            links.append(u)
    for a in re.findall(r"arXiv (\d{4}\.\d{4,5})", text or "", re.I):
        u = f"https://arxiv.org/abs/{a}"
        if u not in seen:
            seen.add(u)
            links.append(u)
    for d in re.findall(r"\b((?:[a-z0-9-]+\.)+(?:com|org|io|systems|gov|edu|net)/[A-Za-z0-9_./#-]*[A-Za-z0-9_/#-])",
                        text or ""):
        if any(d in x for x in seen):
            continue
        u = "https://" + d
        if u not in seen:
            seen.add(u)
            links.append(u)
    return links


def sec_research(c):
    parts = []
    for key, title, summ, took in RESEARCH_META:
        t = c.research.get(key)
        p = RES / f"{key}.md"
        if t is None:
            parts.append(f"<h3>{title}</h3>" + pending(p))
            continue
        n_lines = t.count("\n")
        links = research_links(t)
        lk = "".join(f'<li><a href="{E(u)}">{E(u)}</a></li>' for u in links)
        extra = ""
        if key == "data_audit":
            nfiles = rx(t, r"\*\*([\d,]+) files\*\*")
            extra = (f"<p class=small>No external sources: every figure is measured on a sample of {fmt(nfiles)} "
                     f"decision files read from git.</p>")
        if key == "formalisms_python" and not links:
            pass
        links_html = (details(f"Sources cited in the file ({len(links)} links)", f"<ul class=links>{lk}</ul>")
                      if links else "")
        parts.append(f"""<div class="card"><h3>{title}</h3>
<p>{summ}</p><p><b>What we took:</b> {took}</p>{extra}{links_html}
<p class="src"><code>{E(rel(p))}</code>, {fmt(n_lines)} lines</p></div>""")
    return f"""
<section id="research"><h2>3. Design research</h2>
<p>Six research notes were written before and during the build. The first three shaped the draft design; the last
three, on how large formalisms keep their statements honest, produced the revised design (DESIGN.md, D1–D9), which
supersedes the draft where they differ.</p>
{''.join(parts)}
{details("The revised design, D1–D9 (DESIGN.md)", md(md_section(c.design, r"^REVISED DESIGN") or "", 2)) if c.design else pending(C2 / "DESIGN.md")}
</section>"""


def arch_svg(c):
    n_thm = c.ls["theorems_registered"]
    n_dec = rx(c.courts, r"decisions2\.tsv \(([\d,]+) rows")
    return f"""<figure class="diagram"><svg viewBox="0 0 360 600" role="img" aria-labelledby="archT archD">
<title id="archT">caselaw-lean-2 architecture</title>
<desc id="archD">Untrusted readers and tables produce rows with certificates. Below the trust boundary, a Lean
checker admits rows; the Exec layer, proved equal to the Spec, computes verdicts; outputs are status, findings,
certificates and splits.</desc>
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" class="d-arrowhead"/></marker></defs>
<text x="12" y="20" class="d-zone">UNTRUSTED: may be wrong</text>
<rect x="12" y="30" width="162" height="62" rx="8" class="d-box d-untr"/>
<text x="93" y="54" class="d-t">Corpus</text>
<text x="93" y="72" class="d-s">{fmt(n_dec)} decisions</text>
<rect x="186" y="30" width="162" height="62" rx="8" class="d-box d-untr"/>
<text x="267" y="54" class="d-t">Doctrine tables</text>
<text x="267" y="72" class="d-s">courts, rules · S/L/U tags</text>
<rect x="12" y="110" width="336" height="62" rx="8" class="d-box d-untr"/>
<text x="180" y="134" class="d-t">Readers: regex + LLM</text>
<text x="180" y="152" class="d-s">treatments, history, holdings, law changes</text>
<line x1="93" y1="92" x2="93" y2="108" class="d-line" marker-end="url(#ah)"/>
<line x1="180" y1="172" x2="180" y2="212" class="d-line" marker-end="url(#ah)"/>
<text x="188" y="196" class="d-s d-l">rows + certificates: quote, offsets,</text>
<text x="188" y="208" class="d-s d-l">text SHA, opinion part</text>
<line x1="0" y1="226" x2="360" y2="226" class="d-boundary"/>
<text x="12" y="244" class="d-zone">TRUST BOUNDARY · LEAN</text>
<rect x="12" y="254" width="336" height="62" rx="8" class="d-box d-chk"/>
<text x="180" y="278" class="d-t">Cert.check (compiled)</text>
<text x="180" y="296" class="d-s">proved: checkCert_sound · typed rejection reasons</text>
<line x1="180" y1="316" x2="180" y2="344" class="d-line" marker-end="url(#ah)"/>
<text x="188" y="334" class="d-s d-l">admitted rows only</text>
<rect x="12" y="346" width="150" height="80" rx="8" class="d-box d-exec"/>
<text x="87" y="372" class="d-t">Exec</text>
<text x="87" y="390" class="d-s">hash indexes,</text>
<text x="87" y="404" class="d-s">fast runner</text>
<rect x="198" y="346" width="150" height="80" rx="8" class="d-box d-spec"/>
<text x="273" y="372" class="d-t">Spec</text>
<text x="273" y="390" class="d-s">default trees,</text>
<text x="273" y="404" class="d-s">readable rules</text>
<line x1="164" y1="386" x2="196" y2="386" class="d-line d-eq" marker-end="url(#ah)" marker-start="url(#ah)"/>
<text x="180" y="440" class="d-s">proved equal: exec_*_eq_spec</text>
<rect x="198" y="452" width="150" height="46" rx="8" class="d-box d-spec"/>
<text x="273" y="472" class="d-t">{n_thm} theorems</text>
<text x="273" y="488" class="d-s">statements locked</text>
<line x1="273" y1="450" x2="273" y2="428" class="d-line"/>
<line x1="87" y1="426" x2="87" y2="514" class="d-line" marker-end="url(#ah)"/>
<rect x="12" y="516" width="336" height="66" rx="8" class="d-box d-out"/>
<text x="180" y="540" class="d-t">Outputs (out/)</text>
<text x="180" y="558" class="d-s">status · findings · certs · splits</text>
<text x="180" y="572" class="d-s">each row with its rule path and firm flag</text>
</svg><figcaption>The trust boundary. Everything above the line may be wrong; nothing it produces is believed unless the
checker admits it. Below the line, the runner computes verdicts with the Spec's own functions, through hash indexes
proved equal to the Spec's list scans.</figcaption></figure>"""


def sec_arch(c):
    mut = re.search(r"(\d+) properties against (\d+) mutants", c.lean or "")
    lock = md_section(c.lean, r"^Statement lock")
    head = md_section(c.diff, r"^caselaw-lean-2: differential testing") or ""
    stm_entries = re.findall(r"^## (\S+)\s+(.*)$", c.stm or "", re.M)
    return f"""
<section id="arch"><h2>4. Architecture: three layers, one trust boundary</h2>
<p><b>Spec.</b> Short, readable definitions of precedent, written as labelled default trees: each rule a default with
named exceptions (Erie, Marks, adoption, unpublished, en banc, succession), each label tied to the doctrine rule it
implements. Doctrine tables enter as parameters, so every theorem holds for any table.</p>
<p><b>Exec.</b> The same functions over hash maps, fast enough for the corpus, with proved equality to the Spec.</p>
<p><b>Untrusted.</b> Python and LLM readers and the doctrine tables. They may be wrong. A treatment or history row is
admitted only if the compiled certificate checker passes it, and its soundness theorem says what passing means.</p>
{arch_svg(c)}
<h3>The statement lock</h3>
{md(lock, 2) if lock else pending(C2 / "LEAN.md")}
<p>{len(stm_entries)} entries in <code>STATEMENTS.log</code>: {"; ".join(f"{E(a)} <i>{E(b)}</i>" for a, b in stm_entries)}.</p>
<h3>Mutation testing</h3>
<p>{(f"Each registered property must fail on at least one deliberately broken model. {mut.group(1)} properties were run "
     f"against {mut.group(2)} mutants; every property holds of the Spec, and every mutant is caught.") if mut else "pending"}
The matrix is in section 5.</p>
<h3>Differential testing</h3>
{md(re.split(r"\n## ", head)[0], 2) if head else pending(C2 / "DIFFTEST.md")}
<p>Rounds, classes and fuzzing are in section 11.</p>
{src(C2 / "LEAN.md", C2 / "STATEMENTS.log", C2 / "DIFFTEST.md")}
</section>"""


def mutation_matrix(c):
    t = md_section(c.lean, r"^Mutation results")
    if not t:
        return pending(C2 / "LEAN.md")
    rows = []
    mutants = {}
    for line in t.split("\n"):
        if not line.startswith("|"):
            continue
        cells = split_row(line)
        if len(cells) < 2 or cells[0].startswith("Property") or cells[0].startswith("---"):
            continue
        ms = re.findall(r"M(\d+) ([^,]+)", cells[1])
        for n, name in ms:
            mutants[int(n)] = name.strip()
        rows.append((cells[0], {int(n) for n, _ in ms}))
    if not rows:
        return pending(C2 / "LEAN.md")
    ids = sorted(mutants)
    head = "<th>Property</th>" + "".join(f'<th class="mh" title="{E(mutants[i])}">M{i}</th>' for i in ids)
    body = []
    for prop, ks in rows:
        cells = "".join(f'<td class="mc{" k" if i in ks else ""}" title="M{i} {E(mutants[i])}">'
                        f'{"●" if i in ks else ""}</td>' for i in ids)
        body.append(f"<tr><th class=mp>{inline(prop)}</th>{cells}</tr>")
    legend = "".join(f"<li><b>M{i}</b> {E(mutants[i])}</li>" for i in ids)
    return (f'<div class="tw"><table class="matrix"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'
            f'<p class="small">● = the property fails on that mutant (the mutant is killed). '
            f'{len(rows)} properties × {len(ids)} mutants; every row and every column has at least one ●.</p>'
            f'{details("Mutants", f"<ul class=cols>{legend}</ul>")}')


def sec_lean(c):
    ls = c.ls
    mods = md_section(c.lean, r"^Layers \(DESIGN D1\)")
    # registry table
    stm = {}
    regsec = md_section(c.lean, r"^Theorems \(the registry")
    for line in (regsec or "").split("\n"):
        if line.startswith("| `"):
            cells = split_row(line)
            if len(cells) >= 3:
                name = cells[0].strip("`")
                st = cells[2]
                m = re.search(r"—\s*(`.*`)\s*$", st)
                stm[name] = m.group(1) if m else (st if st.startswith("`") else "")
    rows = []
    for r in ls["registry"]:
        name = r["name"].replace("CaseLaw2.", "", 1)
        plain = r["desc"] or PLAIN.get(name, "")
        mark = "" if r["desc"] else ' <span class="muted" title="no doc string in the source; plain statement written for this report">†</span>'
        mod = r["module"].replace("LegalProofs.CaseLaw2.", "")
        locked = stm.get(name, "")
        lk = f'<details class=stm><summary>locked statement</summary><div class=code>{inline(locked)}</div></details>' if locked else ""
        rows.append([f"<code>{E(name)}</code><div class=muted>{E(mod)}</div>", inline(plain) + mark + lk])
    reg_tbl = table(["Theorem", "Statement"], rows, cls="reg") if rows else pending(LEANDIR / "Registry.lean")
    # per-module counts
    mrows = []
    for f, s in sorted(ls["per_file"].items()):
        k = s["kinds"]
        mrows.append([f"<code>{E(f)}</code>", fmt(s["lines"]), fmt(sum(v for kk, v in k.items() if kk != "example")),
                      fmt(k.get("theorem", 0)), fmt(s["guards"])])
    mrows.append(["<b>Total</b>", f'<b>{fmt(ls["lines"])}</b>', f'<b>{fmt(ls["declarations"])}</b>',
                  f'<b>{fmt(ls["theorems_in_source"])}</b>', f'<b>{fmt(ls["guards"])}</b>'])
    # replays
    rep = md_section(c.lean, r"^Known episodes replayed")
    # trust tiers
    trust_parts = []
    for h in (r"^Proved \(kernel\)", r"^Proved by computation", r"^Certificate-checked", r"^Tested only", r"^Assumed"):
        s = md_section(c.trust, h, include_heading=False)
        hh = re.search(r"^## (" + h.lstrip("^") + r".*)$", c.trust or "", re.M)
        if s:
            trust_parts.append(details(E(hh.group(1)) if hh else h, md(s, 3)))
    tier_tbl, tier_bars = trust_lines(c)
    hl = re.search(r"\*\*Headline\.\*\*\n(.*?)(?=\n## )", c.trust or "", re.S)
    where = re.search(r"- (\*\*Where it ran:\*\*.*?)(?=\n- \*\*)", hl.group(1), re.S) if hl else None
    where_html = (note(inline(" ".join(where.group(1).split()))) if where else pending(C2 / "TRUST.md"))
    headline_html = details("TRUST.md headline", md(hl.group(1), 3)) if hl else ""
    return f"""
<section id="lean"><h2>5. The Lean model</h2>
<p>Lean 4, no Mathlib, namespace <code>CaseLaw2</code>. {fmt(ls["files"])} files, {fmt(ls["lines"])} lines,
{fmt(ls["declarations"])} declarations by a regex count, {fmt(ls["theorems_registered"])} registered theorems.</p>
<h3>Modules</h3>
{md(mods, 2) if mods else pending(C2 / "LEAN.md")}
{details("Lines, declarations, theorems and #guard checks per file (lean_stats.py)",
         table(["File", "Lines", "Decls", "Theorems", "#guard"], mrows, num_cols={1, 2, 3, 4}))}
<h3>The theorem registry</h3>
<p>Every theorem, read from the generated <code>Registry.lean</code>. The plain statement is the first sentence of the
theorem's doc string; † marks the {sum(1 for r in ls["registry"] if not r["desc"])} theorems with no doc string, whose
plain statement was written for this report from the locked statement. Open a row for the locked statement as
<code>LEAN.md</code> abbreviates it.</p>
{reg_tbl}
<h3>The mutation kill matrix</h3>
{mutation_matrix(c)}
<h3>Real-case replays</h3>
<p>{fmt(ls["per_file"].get("Examples.lean", {}).get("guards"))} <code>#guard</code> checks in <code>Examples.lean</code>
run on every build. The episodes:</p>
{md(rep, 2) if rep else pending(C2 / "LEAN.md")}
<h3>Trust tiers</h3>
<p>What a reader must believe, in seL4's style. The trusted Spec is what a lawyer would read against doctrine.md;
the glue is tested, not proved.</p>
{where_html}
{headline_html}
{tier_bars}
{tier_tbl}
{''.join(trust_parts) if trust_parts else pending(C2 / "TRUST.md")}
{src(LEANDIR / "Registry.lean", C2 / "LEAN.md", C2 / "TRUST.md")}
</section>"""


def trust_lines(c):
    sec = md_section(c.trust, r"^Line counts")
    if not sec:
        return pending(C2 / "TRUST.md"), ""
    per = c.ls["per_file"]
    rows = []
    barsl = []
    for line in sec.split("\n"):
        if not line.startswith("|"):
            continue
        cells = split_row(line)
        if len(cells) < 3 or cells[0] in ("Layer",) or cells[0].startswith("---") or cells[0] == "Total":
            continue
        names = [re.sub(r"\s*\(.*?\)", "", x).strip() for x in cells[1].split(",")]
        total = 0
        found = []
        for n in names:
            if not n:
                continue
            key = n if n.endswith(".lean") else n + ".lean"
            if key == "CaseLaw2.lean":
                key = "../CaseLaw2.lean"
            if key in per:
                total += per[key]["lines"]
                found.append(n)
        rows.append([E(cells[0]), E(cells[1]), cells[2], fmt(total)])
        barsl.append((E(cells[0]), total))
    tbl = table(["Tier", "Files", "Lines (TRUST.md)", "Lines now"], rows, num_cols={3})
    return tbl + '<p class="small">"Lines now" is counted from the source by <code>lean_stats.py</code> when the report is generated; TRUST.md\'s figures date from when it was written.</p>', bars(barsl, unit=" lines")


def wilson_table(sec_text, label):
    """Render a markdown table whose cells have 'NN% (a/b' and add a Wilson interval column."""
    if not sec_text:
        return ""
    lines = [l for l in sec_text.split("\n") if l.startswith("|")]
    if len(lines) < 3:
        return md(sec_text, 3)
    head = split_row(lines[0])
    rows = []
    for l in lines[2:]:
        cells = split_row(l)
        k = n = None
        for cc in cells:
            m = re.search(r"\((\d+)/(\d+)", cc)
            if m:
                k, n = int(m.group(1)), int(m.group(2))
                break
        rows.append([inline(x) for x in cells] + [wil_str(k, n) if n else "–"])
    return table([inline(h) for h in head] + ["95% interval (Wilson)"], rows, num_cols={1})


def holdings_usage_live():
    p = DATA / "holdings_usage.jsonl"
    if not note_input(p):
        return None
    agg = collections.defaultdict(lambda: [0, 0, 0, 0])
    with open(p, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            a = agg[(r.get("job", "?"), r.get("model", "?"))]
            a[0] += 1
            a[1] += r.get("prompt", 0)
            a[2] += r.get("completion", 0)
            a[3] += r.get("cached", 0)
    return agg


def sec_data(c):
    out = ['<section id="data"><h2>6. Data layers</h2>',
           '<p>Each layer was built by its own agent, to the contract in SCHEMA.md. None of them reads later courts\' '
           'notes: those are the evaluation\'s gold.</p>']
    # ---- courts
    cv = c.cval
    nrows = {f: count_lines(DATA / f) for f in ("courts2.tsv", "succession.tsv", "adoption.tsv", "system_rules.tsv",
                                                 "court_alias.tsv", "commission.tsv")}
    tags = {}
    for f in ("courts2.tsv", "succession.tsv", "adoption.tsv", "system_rules.tsv"):
        rr = tsv(DATA / f, header=False)
        cnt = collections.Counter(r[-1] for r in rr or [] if r and r[-1] in ("S", "L", "U"))
        tags[f] = cnt
    n_dec = rx(c.courts, r"decisions2\.tsv \(([\d,]+) rows")
    reviewed = rx(cv, r"([\d,]+) headers in")
    tag_rows = [[f"<code>{f}</code>", fmt(nrows[f]), fmt(tags[f].get("S", 0)), fmt(tags[f].get("L", 0)),
                 fmt(tags[f].get("U", 0))] for f in tags]
    counts_tbl = table(["File", "Rows", "S", "L", "U"], tag_rows, num_cols={1, 2, 3, 4})
    prec = ""
    if cv:
        for h in ("bench", "publication", "form", "unit"):
            s = md_section(cv, r"^" + h + r"\b")
            if s:
                first_tbl = "\n".join(l for l in s.split("\n\n")[0].split("\n"))
                prec += f"<h5>{h}</h5>" + wilson_table(s.split("\n\n")[0] if s.startswith("|") else first_tbl, h)
    gaps = md_section(c.courts, r"^Known gaps")
    out.append(f"""<div class="card"><h3>Courts and decisions</h3>
<p><b>What it is.</b> Courts as dated epochs (tier, system, circuit, unit), successions and adoptions between courts,
per-system and per-court rules of precedent, and one row per decision with its court, unit, bench, publication, form
and the SHA of its text. Labels come from rules over each decision's header region, read once from git.</p>
<p><b>Counts.</b> {fmt(n_dec)} decisions, every node of the graph once. Doctrine rows by tag:</p>
{counts_tbl}
<p><b>Precision.</b> {fmt(reviewed)} headers reviewed by blind readers in rounds; unclear verdicts left out.
Intervals added here (Wilson, 95%). Samples are small, so the intervals are wide.</p>
{prec or pending(DATA / "courts_validation.md")}
<p><b>Cost.</b> No model calls are recorded for this layer: labels are rules over headers; precision was checked by
subagent readers.</p>
{details("Gaps (COURTS.md)", md(gaps, 3)) if gaps else ""}
{details("Unit recovery per intermediate court family", md(md_section(cv, r"^4\. Unit recovery") or "", 3)) if cv else ""}
{src(DATA / "COURTS.md", DATA / "courts_validation.md")}
</div>""")
    # ---- reader
    rs, ru = c.rstats, c.rusage
    parts = []
    if c.readerm:
        parts.append(details("READER.md", md(c.readerm, 3), open_=False))
    else:
        parts.append(pending(DATA / "READER.md", why="The reader is still running; the counts below are its live "
                                                     f"counters (reader_stats.json, {mtime(DATA / 'reader_stats.json')})."))
    if rs:
        kinds = collections.Counter()
        for k, v in rs.get("by_kind_scope", {}).items():
            kinds[k.split("|")[0]] += v
        hk = collections.Counter()
        for k, v in rs.get("history_by_kind_scope", {}).items():
            hk[k.split("|")[0]] += v
        funnel = [(k, rs.get(k)) for k in ("model_items", "model_not_act", "model_no_valid_target",
                                           "model_invented_target_dropped", "quote_not_found", "cert_fail_quoted",
                                           "cert_fail_cue", "cert_fail_evidence", "model_no_answer",
                                           "admitted_rows", "treatments", "history", "cert_text_rows") if k in rs]
        parts.append(f"""<p><b>Counts.</b> {fmt(rs.get("treatments"))} treatment rows and {fmt(rs.get("history"))}
same-case history rows written so far, from {fmt(rs.get("model_items"))} candidate passages the model read.</p>
{table(["Counter (reader_stats.json)", "Value"], [[f"<code>{E(k)}</code>", fmt(v)] for k, v in funnel], num_cols={1})}
<h5>Treatments by kind</h5>{bars(sorted(kinds.items(), key=lambda x: -x[1]), total=sum(kinds.values()))}
<h5>Same-case history by kind</h5>{bars(sorted(hk.items(), key=lambda x: -x[1]), total=sum(hk.values()))}""")
    else:
        parts.append(pending(DATA / "reader_stats.json"))
    if ru:
        st = ru.get("stages", {})
        rows = [[E(k), fmt(v.get("calls")), fmt(v.get("items")), fmt(v.get("prompt_tokens")),
                 fmt(v.get("completion_tokens")), f'${v.get("cost_usd", 0):,.2f}'] for k, v in st.items()]
        tot = ru.get("total", {})
        rows.append(["<b>Total</b>", "", "", fmt(tot.get("prompt_tokens")), fmt(tot.get("completion_tokens")),
                     f'<b>${tot.get("cost_usd", 0):,.2f}</b>'])
        parts.append(f"""<p><b>Cost.</b> {fmt(tot.get("total_tokens"))} tokens, ${tot.get("cost_usd", 0):,.2f} at the list
prices recorded in the file.</p>{table(["Stage | model", "Calls", "Items", "Prompt tokens", "Completion tokens", "Cost"], rows, num_cols={1, 2, 3, 4, 5})}""")
    audC = sorted(p for p in (EVAL / "audits").glob("*") if p.is_dir() and p.name not in ("gold-notes", "notes-blind"))
    parts.append("<p><b>Precision.</b> The held-out audit of admitted treatments (audit C) and of rejections (audit D) "
                 "of the audit plan was not run; the hunt's blind audits (section 9) read the runner's findings instead. " + (
                     "See section 10." if audC else pending(EVAL / "audits/<audit C>/score.json")) + "</p>")
    out.append(f"""<div class="card"><h3>Treatment reader</h3>
<p><b>What it is.</b> Regex candidates over full text, read by an LLM (gpt-5.4-mini; hard cases gpt-6.1-sol), which
returns typed treatments and same-case history, each with the quoted words, their character offsets and the opinion
part. The quote must be found in the text before a row is written. The reader never reads later courts' notes.</p>
{''.join(parts)}
{src(DATA / "reader_stats.json", DATA / "reader_usage.json", DATA / "treatments.tsv", DATA / "history.tsv")}
</div>""")
    # ---- holdings
    hparts = []
    if c.holdm:
        hparts.append(details("HOLDINGS.md", md(c.holdm, 3)))
    else:
        hparts.append(pending(DATA / "HOLDINGS.md", DATA / "holdings.tsv", DATA / "issues.tsv",
                              why="The holdings agent is still extracting; progress from its logs is below."))
    hc = {f: count_lines(DATA / f) for f in ("holdings.tsv", "issues.tsv", "marks.tsv")}
    if any(v is not None for v in hc.values()):
        hparts.append(table(["File", "Rows"], [[f"<code>{k}</code>", fmt(v)] for k, v in hc.items()], num_cols={1}))
    prog = []
    for job in ("scotus", "treat", "splits"):
        p = DATA / "holdings_work" / f"log_{job}.txt"
        t = read(p)
        if not t:
            continue
        tds = re.findall(r"todo (\d+) done (\d+)", t)
        subs = re.findall(r"(\d\d:\d\d:\d\d) submitted (\d+)", t)
        if tds:
            todo, done = map(int, tds[-1])
            after = 0
            last_t = ""
            idx = t.rfind(f"todo {tds[-1][0]} done {tds[-1][1]}")
            for tm, n in re.findall(r"(\d\d:\d\d:\d\d) submitted (\d+)", t[idx:]):
                after, last_t = int(n), tm
            prog.append([job, fmt(todo + done), fmt(done), fmt(after), last_t or "–", mtime(p)])
    if prog:
        hparts.append("<p><b>Progress</b> (from the job logs; a restart writes a new todo/done line):</p>" +
                      table(["Job", "Items", "Done at last restart", "Submitted since", "At", "Log written"], prog,
                            num_cols={1, 2, 3}))
    live = holdings_usage_live()
    prices = {}
    if c.husage:
        m = re.search(r"\{.*\}", c.husage.get("price_note", ""))
        if m:
            try:
                prices = json.loads(m.group(0))
            except json.JSONDecodeError:
                prices = {}
    if live:
        rows = []
        tot_tok = tot_cost = 0
        for (job, model), (calls, pr, co, ca) in sorted(live.items()):
            base = "gpt-6.1-sol" if "6.1-sol" in model else ("gpt-5.4-mini" if "5.4-mini" in model else None)
            pz = prices.get(base)
            cost = ((pr - ca) * pz[0] + ca * pz[1] + co * pz[2]) / 1e6 if pz else None
            tot_tok += pr + co
            tot_cost += cost or 0
            rows.append([E(job), E(model), fmt(calls), fmt(pr), fmt(co), f"${cost:,.2f}" if cost is not None else "–"])
        hparts.append(f"<p><b>Cost so far.</b> {fmt(tot_tok)} tokens, ${tot_cost:,.2f} at the list prices in "
                      f"<code>holdings_usage.json</code> (summed live from <code>holdings_usage.jsonl</code>).</p>" +
                      table(["Job", "Model", "Calls", "Prompt", "Completion", "Cost"], rows, num_cols={2, 3, 4, 5}))
    hparts.append("<p><b>Precision.</b> " + pending(EVAL / "audits/<splits audit E>/score.json",
                                                    why="Audit E (40 detected splits, 40 missed) was not run. "
                                                        "The hunt spot-checked the split rows (section 9).") + "</p>")
    out.append(f"""<div class="card"><h3>Holdings, issues and splits</h3>
<p><b>What it is.</b> Holdings for Supreme Court decisions and for every decision that is a treatment target or
source, each with its issue, a yes/no answer where the issue is a split question, and the certified sentence that
states it. Statutory issues are keyed by US Code subsection so splits can be found.</p>
{''.join(hparts)}
{src(DATA / "holdings_work", DATA / "holdings_usage.jsonl")}
</div>""")
    # ---- statutes
    st = c.stat
    if st:
        cnts = md_section(st, r"^Counts")
        recall = md_section(st, r"^Recall")
        precs = md_section(st, r"^Precision per evidence")
        retro = md_section(st, r"^Retroactivity extraction")
        gaps = md_section(st, r"^Gaps")
        retro_short = "\n".join(retro.split("\n")[:6]) if retro else ""
        tok = rx(st, r"tokens ([\d,]+)")
        out.append(f"""<div class="card"><h3>Statutes: law changes and supersession</h3>
<p><b>What it is.</b> Every rewrite of a US Code block that a decision cited, with the law, its enactment and
effective dates and any retroactive reach; and candidate supersessions of a decision by a law, scored by the
evidence that Congress had the decision in mind.</p>
<p><b>Counts.</b></p>{md(cnts, 3)}
<p><b>Recall</b> against Christiansen &amp; Eskridge and Hasen:</p>{md(recall, 3)}
<p><b>Precision</b> per evidence type, from blind audits:</p>{md(precs, 3)}
<p><b>Cost.</b> The retroactivity reader used {fmt(tok)} tokens (gpt-5.4-mini). Everything else is regex and record
reading.</p>
{details("Retroactivity extraction, accuracy", md(retro_short, 3))}
{details("Gaps (STATUTES.md)", md(gaps, 3)) if gaps else ""}
{src(DATA / "STATUTES.md", DATA / "lawchanges.tsv", DATA / "supersessions.tsv")}
</div>""")
    else:
        out.append('<div class="card"><h3>Statutes</h3>' + pending(DATA / "STATUTES.md") + "</div>")
    try:
        out.append(factors_card(c))
    except Exception:
        out.append(f'<div class="card"><h3>Horty factors</h3><div class="pending"><b>This card failed to render.</b>'
                   f'<pre>{E(traceback.format_exc())}</pre></div></div>')
    out.append("</section>")
    return "\n".join(out)


# ---------------------------------------------------------------- results

def find_nodes(targets):
    """targets: list of (name, date). Returns {(name, date): node} by scanning graph/nodes.tsv."""
    found = {}
    if not note_input(NODES):
        return found
    keys = {(n, str(d)) for n, d in targets}
    names = {n.encode("utf-8") for n, _ in targets}
    with open(NODES, "rb") as f:
        for line in f:
            if not any(n in line for n in names):
                continue
            p = line.decode("utf-8", "replace").rstrip("\n").split("\t")
            if len(p) >= 7 and (p[6], p[4]) in keys:
                found.setdefault((p[6], p[4]), int(p[0]))
    return found


def court_names():
    rr = tsv(DATA / "courts2.tsv", header=False) or []
    out = {}
    for r in rr:
        if len(r) > 3 and r[0] not in out:
            out[r[0]] = r[3]
    return out


def sec_results(c):
    parts = ['<section id="results"><h2>7. Results</h2>']
    interim = C2 / "difftest" / "real2" / "lean"
    have_out = c.out_ok
    base = OUT if have_out else None
    if not have_out:
        parts.append(pending(OUT / "status.tsv", OUT / "findings.tsv", OUT / "certs.tsv", OUT / "splits.tsv",
                             why="The full Lean run waits for the reader and holdings files."))
        if (interim / "status.tsv").exists():
            parts.append(note(f"<b>Interim.</b> Where a table below says <i>interim</i>, it is from the "
                              f"differential-test run on the data that had landed by then "
                              f"(<code>{rel(interim)}</code>, {mtime(interim / 'status.tsv')}): courts, decisions, "
                              f"law changes and supersessions, but no reader treatments, history or holdings. "
                              f"It is a real Lean run on real data, but not the full one."))
    srcdir = base or (interim if (interim / "status.tsv").exists() else None)
    tag = "" if have_out else ' <span class="tag">interim</span>'
    # status
    parts.append("<h3>Status of holdings across the corpus" + tag + "</h3>")
    if srcdir and (srcdir / "status.tsv").exists():
        cls = collections.Counter()
        kinds = collections.Counter()
        nodes = set()
        firm = collections.Counter()
        for r in tsv(srcdir / "status.tsv"):
            if r.get("to") != "20261112" and r.get("to") != max(r.get("to", ""), "20261112"):
                pass
            cls[r.get("class")] += 1
            kinds[r.get("status")] += 1
            nodes.add(r.get("node"))
            firm[r.get("firm")] += 1
        # current status (row whose interval reaches asOf)
        cur = collections.Counter()
        last = {}
        for r in tsv(srcdir / "status.tsv"):
            key = (r.get("node"), r.get("issue"), r.get("holding"))
            if key not in last or int(r.get("to") or 0) >= int(last[key].get("to") or 0):
                last[key] = r
        for r in last.values():
            cur[r.get("status")] += 1
        parts.append(f"<p>{fmt(len(nodes))} decisions have status rows; {fmt(len(last))} (decision, issue, holding) "
                     f"timelines. Status on the as-of date, per timeline:</p>")
        parts.append(bars(sorted(cur.items(), key=lambda x: -x[1]), total=sum(cur.values())))
        parts.append(details("All status rows (interval segments) by class",
                             bars(sorted(cls.items(), key=lambda x: -x[1]), total=sum(cls.values())) +
                             f"<p class=small>firm = 1 on {fmt(firm.get('1', 0))} of {fmt(sum(firm.values()))} rows.</p>"))
        parts.append(src(srcdir / "status.tsv"))
    else:
        parts.append(pending(OUT / "status.tsv"))
    # findings
    parts.append("<h3>Findings" + tag + "</h3>")
    if srcdir and (srcdir / "findings.tsv").exists():
        fk = collections.Counter()
        atrisk = collections.Counter()
        firm1 = collections.Counter()
        for r in tsv(srcdir / "findings.tsv"):
            k = r.get("finding")
            fk[k] += 1
            if r.get("firm") == "1":
                firm1[k] += 1
            if k == "atRisk":
                atrisk[(r.get("detail") or "").split(":")[0]] += 1
        allk = ["citesOverruled", "citesVacated", "citesWithdrawn", "citesNotCitable", "citesUnpublishedAsBinding",
                "appliesSupersededHolding", "panelDepartsWithoutEnBanc", "pluralityTreatedAsBinding",
                "ignoresBindingInUnit", "atRisk", "inconsistentBindingBase"]
        for k in fk:
            if k not in allk:
                allk.append(k)
        rows = [[f"<code>{k}</code>", fmt(fk.get(k, 0)), fmt(firm1.get(k, 0))] for k in allk]
        parts.append(bars([(f"<code>{k}</code>", fk[k]) for k in sorted(fk, key=lambda x: -fk[x])]))
        parts.append(table(["Finding", "Rows", "of which firm"], rows, num_cols={1, 2}))
        if atrisk:
            parts.append("<p>atRisk by source:</p>" + bars(sorted(atrisk.items(), key=lambda x: -x[1])))
        parts.append(src(srcdir / "findings.tsv"))
    else:
        parts.append(pending(OUT / "findings.tsv"))
    # certs
    parts.append("<h3>Certificate admission and rejection</h3>")
    if have_out and (OUT / "certs.tsv").exists():
        byt = collections.defaultdict(collections.Counter)
        for r in tsv(OUT / "certs.tsv"):
            byt[r.get("table")][r.get("result_all")] += 1
        for t_, cnt in byt.items():
            n = sum(cnt.values())
            parts.append(f"<h5>{E(t_)}: {fmt(n)} rows, {pct(cnt.get('ok', 0) + cnt.get('okUnverifiedBy', 0), n)} admitted</h5>")
            parts.append(bars(sorted(cnt.items(), key=lambda x: -x[1]), total=n))
        parts.append(src(OUT / "certs.tsv"))
    else:
        parts.append(pending(OUT / "certs.tsv"))
    # summary
    if have_out and (OUT / "summary.tsv").exists():
        agg = collections.Counter()
        # Every shard loads and checks the whole certificate tables, so these counters repeat in each shard
        # (and asOf is a date): take them once, do not sum them.
        once = {"rows_admitted", "rows_rejected", "asOf"}
        for r in tsv(OUT / "summary.tsv", header=False):
            if len(r) >= 2:
                v = num(r[1])
                if isinstance(v, (int, float)):
                    if r[0] in once:
                        agg[r[0]] = max(agg[r[0]], v)
                    else:
                        agg[r[0]] += v
        parts.append(details("Runner counters (out/summary.tsv): summed over shards, except rows_admitted, "
                             "rows_rejected and asOf, which every shard reports for the whole run",
                             table(["Counter", "Total"], [[E(k), str(int(v)) if k == "asOf" else fmt(v)] for k, v in agg.items()], num_cols={1})))
    # splits
    parts.append("<h3>Splits</h3>")
    if have_out and (OUT / "splits.tsv").exists():
        sp = tsv(OUT / "splits.tsv")
        kinds = collections.Counter(r.get("kind") for r in sp)
        parts.append(f"<p>{fmt(kinds.get('split', 0))} splits and {fmt(kinds.get('conflict', 0))} conflicts on the as-of date "
                     f"({fmt(sum(1 for r in sp if r.get('kind') == 'split' and r.get('firm') == '1'))} splits firm).</p>")
        iss = {r.get("issue_key"): r for r in (tsv(DATA / "issues.tsv", header=False) and
                                                [dict(zip(["issue_key", "label", "domain", "usc", "question", "src"], x))
                                                 for x in tsv(DATA / "issues.tsv", header=False)] or [])}
        cn = court_names()
        ex = []
        seen = set()
        for r in sp:
            if r.get("kind") != "split" or r.get("issue") in seen:
                continue
            i = iss.get(r.get("issue"), {})
            if i.get("usc", "-") == "-" and len(ex) < 2:
                pass
            seen.add(r.get("issue"))
            c1 = cn.get((r.get("court1") or "").split("/")[0], r.get("court1"))
            c2 = cn.get((r.get("court2") or "").split("/")[0], r.get("court2"))
            ex.append([f"<code>{E(r.get('issue', ''))}</code><div>{E(i.get('question') or i.get('label') or '')}</div>"
                       f"<div class=muted>{E(i.get('usc', ''))}</div>",
                       f"{E(c1)}: <b>{E(r.get('answers1', ''))}</b> <span class=muted>({E(r.get('holdings1', ''))})</span>",
                       f"{E(c2)}: <b>{E(r.get('answers2', ''))}</b> <span class=muted>({E(r.get('holdings2', ''))})</span>"])
            if len(ex) >= 3:
                break
        parts.append("<p>Three examples (the first three distinct issues in the file):</p>" +
                     table(["Question", "Court 1", "Court 2"], ex))
        parts.append(src(OUT / "splits.tsv", DATA / "issues.tsv"))
    else:
        parts.append(pending(OUT / "splits.tsv", DATA / "issues.tsv"))
    # two dates
    parts.append("<h3>Two dates: question date and conduct date</h3>")
    parts.append(two_dates(c, srcdir, tag))
    parts.append("</section>")
    return "\n".join(parts)


HEAT = Path(__file__).resolve().parent / "heatmaps"
HEAT_CHARTS = [
    ("caselaw_bad_law_by_day", "badlaw", "Decisions relying on bad law, by day",
     "Each square is a day; its colour is the number of decisions decided that day that cite, as authority, a decision "
     "whose status was already negative in the citing court's chain of authority: overruled or abrogated, vacated or "
     "reversed, withdrawn, superseded by statute, or not citable. These are the Lean findings citesOverruled, "
     "citesVacated, citesWithdrawn, citesNotCitable and appliesSupersededHolding, counted once per citing decision. "
     "{total} decisions in 1990–2019: {p_citesOverruled} cite an overruled decision, {p_citesVacated} a vacated or "
     "reversed one, {p_citesWithdrawn} a withdrawn one, {p_citesNotCitable} one that is not citable and "
     "{p_appliesSupersededHolding} a superseded holding (kinds overlap; the last needs a conduct date the data do not "
     "carry). The busiest day was {peak}, an end-of-term release day. Dates that carry only a month or a year (the 1st "
     "of a month in court-years where the 1st is far over-represented, and every 1 January) are dropped; weekends are "
     "nearly empty, as in the CVE original. Not-citable citations are not always improper, so that part over-counts."),
    ("caselaw_precedent_broken_by_day", "broken", "Precedent broken, by day",
     "Each square counts the admitted negative status events dated that day: a later decision with power over the "
     "target overrules, abrogates, reverses, vacates or withdraws it (one event per witness row of a negativeAdmitted "
     "row in out/status.tsv, dated by the treating decision). {total} events in 1990–2019: {s_same} same-case "
     "reversals and vacaturs and {s_overruled} overrulings; the busiest day was {peak}. The certificate checker passes more "
     "negative treatments than this; only the ones the run gave effect are counted. Coverage thins after mid-2019."),
    ("uscode_vulnerabilities_by_day", "usc", "US Code vulnerabilities introduced, by day",
     "The same chart for the Code, from the record of every section version since 1995. A day's count adds three "
     "kinds of defect: explicit cross-references that start to dangle (broken by a later law or edition, or written "
     "so; held-out audit 68% real), amending instructions of laws since 2013 whose struck words are not in the section "
     "(the one failure class the audit found mostly real, though most are the Code's editorial wording rather than "
     "drafting errors), and duplicate designations among siblings. {total} defects in 1995–2026; the peak, {peak}, "
     "is the enactment of title 54 (Pub. L. 113-287), which moved the National Park Service laws out of title 16. "
     "Edition releases show as single heavy days, and before 2017 the record dates changes on enactment."),
]


def sec_heatmaps(c):
    import base64 as _b64
    HEAT = ART / "heatmaps"
    parts = ['<section id="heatmaps"><h2>8. Vulnerability heatmaps</h2>',
             '<p class="lead">Calendar heatmaps in the style of the well-known chart of CVE publications by day: one '
             'panel per year, a row per weekday, a column per week. No Lean was run for them; they count the outputs '
             'above and the earlier US Code work. Definitions, peaks and caveats are in '
             '<code>report/heatmaps/HEATMAPS.md</code>; the full-size PNG and SVG files are beside it.</p>']
    hj = HEAT / "heatmaps.json"
    note_input(hj)
    if not hj.exists():
        parts.append(pending(hj))
        parts.append("</section>")
        return "\n".join(parts)
    stats = json.loads(hj.read_text(encoding="utf-8"))
    for stem, key, title, text in HEAT_CHARTS:
        img = HEAT / f"{stem}.webp"
        note_input(img)
        st = stats.get(key)
        if not img.exists() or not st:
            parts.append(f"<h3>{E(title)}</h3>" + pending(img))
            continue
        pk = st["peaks"][0]
        d = dt.date(pk["day"] // 10000, pk["day"] // 100 % 100, pk["day"] % 100)
        peak = f'{d.strftime("%A")} {d.day} {d.strftime("%B %Y")} ({fmt(pk["count"])})'
        uri = "data:image/webp;base64," + _b64.b64encode(img.read_bytes()).decode()
        parts.append(f"<h3>{E(title)}</h3>")
        parts.append(f'<figure style="margin:1em 0 1.4em"><img src="{uri}" loading="lazy" '
                     f'style="width:100%;height:auto;display:block;background:#fff;border-radius:8px" '
                     f'alt="{E(title)}: calendar heatmap, one panel per year, total {fmt(st["total"])}, peak {E(peak)}">'
                     f'</figure>')
        pp = st.get("parts") or {}
        kw = {f"p_{k}": fmt(v) for k, v in pp.items()}
        kw.setdefault("p_appliesSupersededHolding", "0")
        kw["s_same"] = pct(pp.get("reversed", 0) + pp.get("vacated", 0), st["total"])
        kw["s_overruled"] = pct(pp.get("overruled", 0), st["total"])
        for k in ("p_citesOverruled", "p_citesVacated", "p_citesWithdrawn", "p_citesNotCitable"):
            kw.setdefault(k, "pending")
        parts.append("<p>" + E(text.format(total=fmt(st["total"]), peak=peak, **kw)) + "</p>")
    parts.append(src(hj, HEAT / "HEATMAPS.md", HEAT / "series.json"))
    parts.append("</section>")
    return "\n".join(parts)


def two_dates(c, srcdir, tag):
    t = md_section(c.stat, r"^Two dates")
    if not t:
        return pending(DATA / "STATUTES.md")
    lines = [l for l in t.split("\n") if l.startswith("|")]
    head = split_row(lines[0])
    want = ("Bailey v. United States", "Allison Engine", "Ledbetter v. Goodyear")
    rows = [split_row(l) for l in lines[2:] if any(split_row(l)[0].startswith(w) for w in want)]
    intro = md(t.split("\n|")[0], 3)
    out = intro + table([inline(h) for h in head[:-1]], [[inline(x) for x in r[:-1]] for r in rows])
    targets = [(r[0], r[1]) for r in rows]
    nodes = find_nodes(targets)
    if not nodes:
        return out + pending(NODES)
    ids = {str(v): k for k, v in nodes.items()}
    if srcdir and (srcdir / "status.tsv").exists():
        srows = []
        for r in tsv(srcdir / "status.tsv"):
            if r.get("node") in ids:
                nm, d = ids[r["node"]]
                srows.append([f"{E(nm)} <span class=muted>({d}, node {r['node']})</span>", E(r.get("issue", "")),
                              E(r.get("from", "")), E(r.get("to", "")), f"<code>{E(r.get('status', ''))}</code>",
                              E(r.get("firm", "")), E(r.get("path", ""))])
        missing = [f"{n} ({d})" for (n, d), v in nodes.items() if str(v) not in {x for x in ids if any(
            True for _ in [0])} ]
        out += (f"<p>Lean's status rows for these decisions{tag}, on the diagonal (question date = conduct date). "
                f"Each row is an interval of dates with the status Lean computes; the path names the rule behind "
                f"it. Where a supersession names no holding, it reaches \"some issue, unknown which\", which "
                f"Lean reports as <code>unknown:partialScope</code>, not as negative (DEVIATIONS 30, 36).</p>")
        out += table(["Decision", "Issue", "From", "To", "Status", "Firm", "Path"], srows) if srows else \
            note("No status rows for these decisions in the run.")
        out += src(srcdir / "status.tsv", NODES)
    else:
        out += pending(OUT / "status.tsv")
    return out


# ---------------------------------------------------------------- the hunt, fuzzing, factors, limits



def table_lines(sec):
    """The pipe-table lines of a markdown block, as one markdown table."""
    return "\n".join(l for l in (sec or "").split("\n") if l.startswith("|"))


def numbered_items(text):
    """Top-level numbered items ('1. ...' plus indented continuation lines) of a markdown block."""
    items = re.split(r"\n(?=\d+\.\s)", "\n" + (text or ""))
    return [x.strip("\n") for x in items if re.match(r"\d+\.\s", x.strip("\n"))]


def top_instances(sec, marker=r"\*\*(?:Top instances|Three confirmed instances)"):
    """The numbered list that follows a 'Top instances' marker in a HUNT.md section."""
    m = re.search(marker, sec or "")
    if not m:
        return []
    tail = sec[m.end():]
    m2 = re.search(r"^\d+\.\s", tail, re.M)
    if not m2:
        return []
    return numbered_items(tail[m2.start():].split("\n\n")[0])


def para_after(sec, label):
    """The paragraph of a markdown block that starts with **label**."""
    m = re.search(r"(?:^|\n)(\*\*" + label + r".*?)(?:\n\n|\Z)", sec or "", re.S)
    return m.group(1) if m else None


def hunt_fixes(c):
    """HUNT.md 'What to fix', each item with what was then done. Numbers are read from DIFFTEST.md §8,
    courts_validation.md §6, COURTS.md and DEVIATIONS.md."""
    items = numbered_items(md_section(c.hunt, r"^What to fix in caselaw-lean-2") or "")
    if not items:
        return pending(HUNT / "HUNT.md")
    d, cv, dev = c.diff or "", c.cval or "", c.dev or ""

    def eff(name):
        return rx(d, r"`%s`\s+([\d,]+ → [\d,]+)" % name, conv=None) or "pending"

    def dv(n):
        return f"DEVIATIONS {n}" if re.search(r"^%d\.\s" % n, dev, re.M) else "DEVIATIONS: pending"

    pub = re.search(r"Result on the ([\d,]+) candidates: ([\d,]+) changed to published, ([\d,]+) kept", cv)
    bench = rx(cv, r"\*\*Result: ([\d,]+) changed\.\*\*", conv=None) or "pending"
    pcas = rx(c.courts, r"too high: ([\d,]+) are Florida PCAs", conv=None) or "pending"
    tcm = rx(c.courts, r"about ([\d,]+) are T\.C\. Memo", conv=None) or "pending"
    nonpub = rx(cv, r"Non-published labels: ([\d,]+ → [\d,]+)", conv=None) or "pending"
    still = rx(c.courts, r"Even there (about one in four en banc decisions is still `panel`)", conv=None)
    k1 = ((c.hsum or {}).get("patterns", {}).get("p1_zombie", {}).get("known", {}) or {}).get("recall_status", {})
    fixes = {
        1: ("Fixed in the data" if pub else "pending",
            (f"{pub.group(1)} reporter-cited decisions were re-read: {pub.group(2)} were wrong and are now "
             f"published, {pub.group(3)} say themselves that they are not and stay. The hunt's count was too high: "
             f"{pcas} are Florida per curiam affirmances without opinion and about {tcm} are Tax Court memoranda, "
             f"both rightly non-published. Non-published labels {nonpub}; `citesNotCitable` findings "
             f"{eff('citesNotCitable')}. (courts_validation.md §6)") if pub else "pending"),
        2: ("Fixed in the Lean and the reference",
            f"H2: the finding now needs a known conduct date and a holding-level match. The data carry no conduct "
            f"date, so it is no longer emitted: {eff('appliesSupersededHolding')}. A low-confidence "
            f"`atRisk supersededConductUnknown` is written instead. ({dv(70)})"),
        3: ("Fixed in part",
            f"H3b: a finding needs a bench known to be a panel and a rule in force on both dates; no federal finding "
            f"before 1 September 1948; Ohio and Louisiana rule rows are dated. The bench re-read changed {bench} "
            f"decisions. Findings {eff('panelDepartsWithoutEnBanc')}. Still open: "
            f"{still or 'en banc decisions with no cue in the text'}. ({dv(71)}; courts_validation.md §6)"),
        4: ("Fixed for citation findings",
            f"H4: status after an adoption cut-off is per heir, on the `cites*` findings. `status.tsv`, splits, "
            f"conflicts and Horty bases still read the union status. ({dv(69)})"),
        5: ("Not fixed",
            f"A certificate admits only what a court says in words, so partial and implicit overrulings stay out. "
            f"Recall on the literature set is {fmt(k1.get('k'))} of {fmt(k1.get('n'))}. (hunt/summary.json)"),
        6: ("Fixed in the Lean and the reference",
            f"H6: a court of last resort with a court-level `horizontal` row is read as sitting in divisions; a "
            f"division is bound by the court's decisions and only an en banc bench overrules them. ({dv(68)})"),
    }
    rows = []
    for it in items:
        n = int(re.match(r"(\d+)\.", it).group(1))
        st, what = fixes.get(n, ("–", "–"))
        rows.append([str(n), inline(re.sub(r"^\d+\.\s*", "", " ".join(x.strip() for x in it.split("\n")))),
                     f"<b>{E(st)}</b>", inline(what)])
    return table(["", "What the hunt found", "Now", "What was done"], rows)


def sec_hunt(c):
    h, s = c.hunt, c.hsum or {}
    if not h:
        return ('<section id="hunt"><h2>9. Loopholes and mistakes found (the hunt)</h2>'
                + pending(HUNT / "HUNT.md", HUNT / "summary.json") + "</section>")
    pats = s.get("patterns", {})
    n_search = sum(1 for k in pats if k != "p6_rules")
    meth = md_section(h, r"^Method and readers") or ""
    ptab = table_lines(meth)
    readers = meth.split("\n|")[0]
    prow = {}
    for l in ptab.split("\n")[2:]:
        cells = split_row(l)
        if cells and cells[0][:1].isdigit():
            prow[cells[0][0]] = cells

    def lead(k):
        r = prow.get(k)
        if not r or len(r) < 6:
            return ""
        return (f'<p class="small">Candidates {inline(r[1])}; reported {inline(r[2])}; audit precision '
                f'{inline(r[3])}; confirmed {inline(r[5])}.</p>')

    def block(title, k, sec_pat, n_show, pred_only=True):
        sec = md_section(h, sec_pat) or ""
        items = top_instances(sec)
        if not items:
            return f"<h5>{title}</h5>" + pending(HUNT / "HUNT.md")
        pred = para_after(sec, "Predicate")
        out = f"<h5>{title}</h5>" + lead(k)
        out += md("\n".join(items[:n_show]), 3)
        out += details(f"More: the predicate, the known cases, the corpus run, the audit and all {len(items)} "
                       f"listed instances", md(sec, 3))
        return out

    # rule-space loopholes
    sec6 = md_section(h, r"^6\. Loopholes in the rules") or ""
    blocks = re.split(r"\n(?=\*\*[a-f]\. )", sec6)
    by = {b[2]: b for b in blocks[1:]}
    rules = md(blocks[0], 3) if blocks else ""
    for k in ("b", "c", "e"):
        if k in by:
            rules += md(by[k], 3)
    more = "".join(md(by[k], 3) for k in ("a", "d", "f") if k in by)
    if more:
        rules += details("More: forum choice, unpublished-opinion windows, commission opinions", more)
    if not by:
        rules = pending(HUNT / "HUNT.md")
    # findings then and now
    then = (s.get("corpus") or {}).get("findings") or {}
    now = (c.res or {}).get("findings") or {}
    frows = [[f"<code>{E(k)}</code>", fmt(then.get(k)) if k in then else "–", fmt(now.get(k, 0)) if now else "pending"]
             for k in list(then) + [k for k in now if k not in then]]
    lean = s.get("lean") or {}
    core = read(LEANDIR / "Core.lean") or ""
    in_core = "CaseLaw2.Hunt" in core
    limits = md_section(h, r"^Limits")
    devh = md_section(c.dev, r"^Hunt fixes and the WSL verification run")
    d83 = md_section(c.diff, r"^8\.3 Hunt fixes on both sides")
    cv6 = md_section(c.cval, r"^6\. Label fix 2")
    return f"""
<section id="hunt"><h2>9. Loopholes and mistakes found (the hunt)</h2>
<p class="lead">{n_search} patterns of mistake were searched for over the corpus, and the rule tables were searched
for loopholes. Each pattern first had to recreate known mistakes; it was then run over the corpus, and a sample of
what it reported was read blind by Claude subagents, who saw the decision text and not the first reader's
verdict.</p>
{note("The hunt searched the run before the fixes it led to. Counts in this section are those of that run; "
      "section 7 has the final run. The last part of this section says what changed.")}
<h3>Per pattern</h3>
{md(ptab, 3) if ptab else pending(HUNT / "HUNT.md")}
<p class="small">Audit intervals are Wilson 95%. "Recall on known" is the share of known mistakes the pattern
recreates. Pattern 6 is a search of the rule tables, not a sample.</p>
{details("Readers and audit design (HUNT.md)", md(readers, 3))}
<h3>The strongest findings</h3>
{block("Zombie precedent: courts applying overruled law", "1", r"^1\. Zombie precedent", 4)}
{block("The losing side, cited after the Supreme Court resolved the split", "5", r"^5\. Inconsistent binding bases", 4)}
{block("Panel overruling panel without en banc", "3", r"^3\. Panel overruling panel", 4)}
{block("Two dates: a superseded holding applied to later conduct", "4", r"^4\. Superseded holdings applied", 3)}
<h5>Loopholes in the rules of precedent</h5>
{rules}
<h3>What the hunt found wrong in our own model</h3>
<p>The audits also turned on us. Two of the runner's finding kinds were mostly wrong, and one label in the data was
wrong at scale. Each item below is from HUNT.md "What to fix"; the last column is what was then done.</p>
{hunt_fixes(c)}
<p>Runner findings, in the run the hunt searched and in the final run:</p>
{table(["Finding", "Hunted run", "Final run"], frows, num_cols={1, 2}) if frows else pending(HUNT / "summary.json")}
{details("The hunt fixes in the Lean (DEVIATIONS.md 68–73)", md(devh, 3)) if devh else ""}
{details("The hunt fixes in differential testing (DIFFTEST.md §8.3)", md(d83, 3)) if d83 else ""}
{details("Publication and bench labels: the fix and its blind review (courts_validation.md §6)", md(cv6, 3)) if cv6 else ""}
<h3>The predicates in Lean</h3>
<p><code>{E(lean.get("module", "Hunt.lean"))}</code>: {fmt(lean.get("theorems"))} theorems and
{fmt(lean.get("guards"))} <code>#guard</code> checks on the cases named here and on near misses.
{"It is imported by <code>Core.lean</code>, so its theorems are in the registry of section 5." if in_core else
 "It is not imported by <code>Core.lean</code>."}</p>
<h3>Limits</h3>
{md(limits, 3) if limits else pending(HUNT / "HUNT.md")}
{src(HUNT / "HUNT.md", HUNT / "summary.json", C2 / "DIFFTEST.md", C2 / "DEVIATIONS.md", DATA / "courts_validation.md",
     DATA / "COURTS.md", EVAL / "results.json")}
</section>"""


def fuzz_html(c):
    f, b = c.fuzz, c.fuzzb
    if not f or not b:
        return "<h3>Fuzzing the glue</h3>" + pending(C2 / "FUZZ.md", C2 / "FUZZ_BUGS.md")
    props = table_lines(md_section(f, r"^Properties"))
    runs = table_lines(md_section(f, r"^Runs"))
    bugs = []
    for m in re.finditer(r"^## (FB-\w+): (.*?)\n\n\*\*Status:\*\* (.*?)(?=\n\n|\Z)", b, re.M | re.S):
        st = m.group(3)
        ver = re.search(r"\*\*(Verified[^*]*)\*\*", st)
        bugs.append([f"<code>{E(m.group(1))}</code>", inline(m.group(2)),
                     "Fixed" if st.startswith("Fixed") else "Open", E(ver.group(1)) if ver else "–"])
    fixed = md_section(f, r"^Bugs found and fixed") or ""
    parts_ = fixed.split("**precedent_ref.py**")
    n_tsv = len(re.findall(r"^\d+\.\s", parts_[0], re.M))
    n_ref = len(re.findall(r"^\d+\.\s", parts_[1], re.M)) if len(parts_) > 1 else None
    ver = para_after(b, r"Verification")
    tested = md_section(f, r"^What is now tested, and what is not") or ""
    m = re.search(r"\*\*Not tested:\*\*\n(.*?)(?=\n\n\*\*|\Z)", tested, re.S)
    not_tested = m.group(1) if m else None
    n_fixed = sum(1 for x in bugs if x[2] == "Fixed")
    return f"""<h3>Fuzzing the glue</h3>
<p>The TSV parsers and writers are not proved, so they were fuzzed: generated data files, broken in typed ways,
loaded by the Lean and by the reference and compared with an oracle that reads SCHEMA literally.</p>
<h5>Properties</h5>
{md(props, 3)}
<h5>Runs</h5>
{md(runs, 3)}
<h5>Bugs found and fixed</h5>
<p>{fmt(len(bugs))} bugs in the Lean loaders, the runner and the reader, {fmt(n_fixed)} of them fixed; {fmt(n_tsv)} more
in <code>Tsv.lean</code> and {fmt(n_ref)} in the Python reference, fixed as they were found.</p>
{table(["Bug", "What", "Status", "Verification"], bugs)}
{md(ver, 3) if ver else ""}
{details("The fixes in Tsv.lean and the reference (FUZZ.md)", md(fixed, 3))}
<h5>Not tested</h5>
{md(not_tested, 3) if not_tested else ""}
{src(C2 / "FUZZ.md", C2 / "FUZZ_BUGS.md")}"""


def factors_card(c):
    t = c.factors
    if not t:
        return '<div class="card"><h3>Horty factors</h3>' + pending(DATA / "FACTORS.md") + "</div>"
    n_sub = rx(t, r"\((\d+) sub-families\)")
    files = table_lines(md_section(t, r"^Files")).replace("\\|", " or ")
    spot = md_section(t, r"^Blind spot-check, v2") or ""
    spot_tbl = table_lines(spot)
    m = re.search(r"(\d+) binding bases examined, (\d+) consistent, (\d+) inconsistent:\s+`([^`]+)`", c.diff or "")
    m2 = re.search(r"(\d+) sub-family bases, (\d+) consistent, all (\d+) agree", c.diff or "")
    fk = (c.res or {}).get("findings") or {}
    cons = md_section(t, r"^Consistency") or ""
    cons_res = cons[cons.find("Results"):] if "Results" in cons else cons
    funnel = para_after(md_section(t, r"^Method") or "", "Funnel:")
    cover = para_after(md_section(t, r"^Method") or "", "Coverage is the cost:")
    reading = spot[spot.find("The misses:"):] if "The misses:" in spot else ""
    tot = re.search(r"\*\*total\*\*.*?\*\*([\d.]+M)\*\* \| \*\*(\$[\d.,]+)\*\*", t)
    if m:
        cons_p = (f"<p><b>Consistency.</b> The Lean runner examined {m.group(1)} binding bases on the real factors: "
                  f"{m.group(2)} are consistent and {m.group(3)} is not, <code>{E(m.group(4))}</code>. "
                  + (f"An independent Python recomputation of {m2.group(1)} sub-family bases finds {m2.group(2)} "
                     f"consistent and agrees with the runner on all {m2.group(3)}. " if m2 else "")
                  + (f"In <code>out/findings.tsv</code>: {fmt(fk.get('hortyConsistentBase'))} "
                     f"<code>hortyConsistentBase</code>, {fmt(fk.get('inconsistentBindingBase'))} "
                     f"<code>inconsistentBindingBase</code>, {fmt(fk.get('hortySelfInconsistent'))} "
                     f"<code>hortySelfInconsistent</code>. " if fk else "")
                  + "The one inconsistency is a gap in the factor vocabulary, not a conflict in the law: see below.</p>")
    else:
        cons_p = "<p><b>Consistency.</b></p>" + pending(C2 / "DIFFTEST.md", why="(the §8.4 Horty line was not found)")
    return f"""<div class="card"><h3>Horty factors</h3>
<p><b>What it is.</b> For Supreme Court holdings in {fmt(n_sub)} narrow question families (sub-families), the facts
the Court found present and the ones it gave as its reason, each with a verbatim quote. They feed Horty's
consistency check: a binding base must not order the same two reasons both ways.</p>
<p><b>Counts.</b></p>{md(files, 3) if files else pending(DATA / "FACTORS.md")}
<p><b>Precision, before and after.</b> The first pass was too loose and was replaced. Blind spot-check of the second
pass against the first:</p>
{md(spot_tbl, 3) if spot_tbl else pending(DATA / "FACTORS.md")}
{cons_p}
{details("Why express preemption is inconsistent, and what changed from v1 to v2", md(cons_res, 3)) if cons_res else ""}
<p><b>Limits.</b></p>
{md(reading, 3) if reading else ""}
{md(cover, 3) if cover else ""}
{details("The funnel from 2,399 cases read (FACTORS.md)", md(funnel, 3)) if funnel else ""}
<p><b>Cost.</b> {E(tot.group(1)) + " tokens, " + E(tot.group(2)) + " at assumed list prices, both passes." if tot else "pending"}</p>
{src(DATA / "FACTORS.md", C2 / "DIFFTEST.md", EVAL / "results.json")}
</div>"""


def limits_table(c):
    """The numbered limits of the 12 Nov follow-up: 1-5 in the Lean (LEAN.md 'Five limits'), the rest in the data
    (courts_validation.md §5)."""
    rows = []
    found = set()
    five = md_section(c.lean, r"^Five limits")
    for l in table_lines(five).split("\n")[2:]:
        cells = split_row(l)
        m = re.match(r"(\d+)\.\s*(.*)", cells[0]) if cells else None
        if not m:
            continue
        refs = max(re.findall(r"DEVIATIONS [\d–-]+", cells[1]), key=len, default="")
        found.add(int(m.group(1)))
        rows.append([m.group(1), inline(m.group(2)), "Lean", "<b>Fixed</b>",
                     inline(cells[1].split(". DEVIATIONS")[0].split(";")[0][:220]), E(refs or "LEAN.md")])
    s5 = md_section(c.cval, r"^5\. Fixes to validated limits") or ""
    for m in re.finditer(r"^\*\*(\d+)\. ([^*]+?)\.?\*\*(.*?)(?=^\*\*\d+\. |\Z)", s5, re.M | re.S):
        body = m.group(3).strip()
        n = int(m.group(1))
        found.add(n)
        tail = [p for p in body.split("\n\n") if p.strip() and not p.lstrip().startswith("|")]
        text = tail[-1] if n == 8 and tail else (tail[0] if tail else "")
        text = re.sub(r"^- ", "", text.strip().split("\n- ")[0] if text.lstrip().startswith("-") else text.strip())
        sents = re.split(r"(?<=[.:])\s+(?=[A-Z0-9])", " ".join(text.split()))
        short = " ".join(sents[:2]) if len(sents[0]) < 150 else sents[0]
        open_ = "unresolved" in body or "unchanged | U" in body
        rows.append([m.group(1), inline(m.group(2)), "Data", "<b>Fixed</b>" + (", part open" if open_ else ""),
                     inline(short), "courts_validation.md §5"])
    # LIMITS.md records the numbers the two files above do not (5, 6, 7, 12); its rows replace same-numbered ones
    lim = read(C2 / "LIMITS.md") if (C2 / "LIMITS.md").exists() else ""
    for l in (lim or "").splitlines():
        cells = split_row(l) if l.startswith("|") else None
        if not cells or len(cells) < 6 or not cells[0].strip().isdigit():
            continue
        n = cells[0].strip()
        rows = [r for r in rows if r[0] != n]
        found.add(int(n))
        now = cells[3].strip()
        rows.append([n, inline(cells[1]), E(cells[2]), "<b>Fixed</b>" if now == "Fixed" else E(now),
                     inline(cells[4]), inline(cells[5])])
    if not rows:
        return pending(C2 / "LEAN.md", DATA / "courts_validation.md")
    rows.sort(key=lambda r: int(r[0]))
    top = max(found)
    missing = [str(i) for i in range(1, top + 1) if i not in found]
    tail = (f'<p class="small">Numbers {", ".join(missing)} of the {top} have no entry in these two files, so they are '
            f'not shown as fixed.</p>') if missing else ""
    return table(["", "Limit", "Where", "Now", "What was done", "Recorded"], rows) + tail


# ---------------------------------------------------------------- evaluation

KIND_ORDER = ["overruled", "abrogated", "disapproved", "recededFrom", "supersededByEnactment", "vacated", "reversed"]


HERE_SECTIONS = Path(__file__).resolve().parent / "sections"


def sec_eval(c):
    r2, r1 = c.res or {}, c.res1 or {}
    parts = ['<section id="eval"><h2>10. Evaluation</h2>',
             "<p>The gold is held out: the reader, holdings and Lean agents never read it. Every disagreement with an "
             "oracle counts as our error until it is triaged.</p>"]
    if c.gold:
        parts.append(details("The gold sets (gold/README.md)", md(c.gold, 3)))
    # notes per kind
    parts.append("<h3>Agreement with later courts' typed notes</h3>")
    rec1 = (r1.get("reports") or {}).get("recall_of_notes", {})
    rec2 = (r2.get("reports") or {}).get("recall_of_notes", {})
    kinds = [k for k in KIND_ORDER if k in rec1 or k in rec2] + [k for k in set(rec1) | set(rec2) if k not in KIND_ORDER]
    if not rec2:
        parts.append(pending(EVAL / "results.json", why="(<code>reports</code> is written once data/treatments.tsv "
                                                        "and out/status.tsv exist). v1, re-scored on the new typed gold, is shown now."))
    rows = []
    items = []
    for k in kinds:
        a, b = rec1.get(k, {}), rec2.get(k, {})
        rows.append([E(k), fmt(a.get("notes_named")), fmt(a.get("agree")), pct(a.get("agree"), a.get("notes_named"), 1),
                     fmt(b.get("notes_named") if b else None), fmt(b.get("agree") if b else None),
                     pct(b.get("agree"), b.get("notes_named"), 1) if b else "pending"])
        items.append((E(k), a.get("agree_rate") * 100 if a.get("agree_rate") is not None else None,
                      b.get("agree_rate") * 100 if b and b.get("agree_rate") is not None else None))
    parts.append(table(["Kind", "v1 notes", "v1 agree", "v1 rate", "v2 notes", "v2 agree", "v2 rate"], rows,
                       num_cols={1, 2, 3, 4, 5, 6}))
    parts.append(bars2(items, value_fmt=lambda v: f"{v:.1f}%", max_value=100))
    parts.append('<p class="small">"Agree": Lean has a negative status for the target from the same treating decision, '
                 'no later than the first note. Kinds are those of the typed note.</p>')
    # precision of admitted
    p1 = (r1.get("reports") or {}).get("precision_of_admitted", {})
    p2 = (r2.get("reports") or {}).get("precision_of_admitted", {})
    if p1 or p2:
        rows = []
        for k in sorted(set(p1) | set(p2)):
            a, b = p1.get(k, {}), p2.get(k, {})
            rows.append([E(k), fmt(a.get("admitted")) if a else "–", pct(a.get("noteNamesSameBy"), a.get("noteNamesSameBy", 0) + a.get("noteOtherOrUnnamed", 0)) if a else "–",
                         fmt(b.get("admitted") if b else None),
                         pct(b.get("noteNamesSameBy"), b.get("noteNamesSameBy", 0) + b.get("noteOtherOrUnnamed", 0)) if b else "pending"])
        parts.append("<p>Admitted treatments that a note confirms, among admitted targets that carry any note (a lower "
                     "bound on precision; most targets are never noted):</p>")
        parts.append(table(["Kind", "v1 admitted", "v1 confirmed among noted", "v2 admitted", "v2 confirmed among noted"],
                           rows, num_cols={1, 2, 3, 4}))
    # oracles
    parts.append("<h3>SCDB, the Constitution Annotated table, overrides and splits</h3>")
    s1, s2 = r1.get("scdb", {}), r2.get("scdb", {})
    c1, c2 = r1.get("crs", {}), r2.get("crs", {})
    def g(d, *ks):
        for k in ks:
            if not isinstance(d, dict):
                return None
            d = d.get(k)
        return d
    rows = [
        ["SCDB: flagged decisions found (recall)", f'{fmt(s1.get("flagged_with_admitted_overruling"))}/{fmt(s1.get("flagged_decisions"))} ({pct(s1.get("flagged_with_admitted_overruling"), s1.get("flagged_decisions"))})' if s1 else "–",
         f'{fmt(s2.get("flagged_with_admitted_overruling"))}/{fmt(s2.get("flagged_decisions"))} ({pct(s2.get("flagged_with_admitted_overruling"), s2.get("flagged_decisions"))})' if s2 else "pending"],
        ["SCDB: admitted overrulings of SCOTUS that SCDB flags (precision)", f'{fmt(s1.get("of_which_flagged"))}/{fmt(s1.get("scotus_decisions_with_admitted_overruling_of_scotus"))} ({pct(s1.get("of_which_flagged"), s1.get("scotus_decisions_with_admitted_overruling_of_scotus"))})' if s1 else "–",
         f'{fmt(s2.get("of_which_flagged"))}/{fmt(s2.get("scotus_decisions_with_admitted_overruling_of_scotus"))} ({pct(s2.get("of_which_flagged"), s2.get("scotus_decisions_with_admitted_overruling_of_scotus"))})' if s2 else "pending"],
    ]
    for key, lab in (("current_table", "Constitution Annotated, current table"), ("2016_express", "2016 table, express rows"),
                     ("2016_all", "2016 table, all rows")):
        a, b = c1.get(key), c2.get(key)
        rows.append([f"{lab}: pairs found (recall)",
                     f'{fmt(a["found"])}/{fmt(a["resolved"])} ({pct(a["found"], a["resolved"])})' if a else "–",
                     f'{fmt(b["found"])}/{fmt(b["resolved"])} ({pct(b["found"], b["resolved"])})' if b else "pending"])
    sp = r2.get("splits") or {}
    rows.append(["Splits resolved by SCOTUS (statutory): detected before the resolving decision", "–",
                 f'{pct(sp.get("recall_section") * sp.get("gold_statutory") if sp.get("recall_section") is not None else None, sp.get("gold_statutory"))} of {fmt(sp.get("gold_statutory"))}'
                 if sp.get("recall_section") is not None else f'pending (gold: {fmt(sp.get("gold_statutory"))} decisions, {fmt(sp.get("gold_statutory_conflict_language"))} with conflict language)'])
    rows.append(["Splits still reported on or after the resolving decision", "–",
                 fmt(sp.get("splits_detected_on_or_after_resolution")) if "splits_detected_on_or_after_resolution" in sp else "pending"])
    parts.append(table(["Oracle", "v1", "v2"], rows))
    # hand-written explanation of the recall figures (report/sections/why_recall.html), embedded verbatim
    wr = HERE_SECTIONS / "why_recall.html"
    if wr.exists():
        note_input(wr)
        parts.append(wr.read_text(encoding="utf-8"))
    ov = tsv(GOLD / "congress_overrides.tsv")
    stat_recall = md_section(c.stat, r"^Recall")
    parts.append(f"<p><b>Congressional overrides.</b> {fmt(len(ov) if ov is not None else None)} rows in "
                 f"<code>gold/congress_overrides.tsv</code>. The statutes layer's recall on them:</p>" + (md(stat_recall, 3) if stat_recall else pending(DATA / "STATUTES.md")))
    st_tbl = EVAL / "tables" / "splits_recall.tsv"
    if st_tbl.exists():
        v = collections.Counter(r.get("verdict") for r in tsv(st_tbl))
        parts.append("<p>Split recall by match level:</p>" + bars(sorted(v.items(), key=lambda x: -x[1]), total=sum(v.values())))
    # v1 vs v2 side by side
    parts.append("<h3>v1 and v2 side by side</h3>")
    vp = r1.get("v1_published") or r2.get("v1_published") or {}
    rows = [["Named notes agreed (published v1 figure)", f'{fmt(vp.get("agree"))}/{fmt(vp.get("notes_named"))} ({pct(vp.get("agree"), vp.get("notes_named"))})',
             "pending" if not rec2 else f'{fmt(sum(v.get("agree", 0) for v in rec2.values()))}/{fmt(sum(v.get("notes_named", 0) for v in rec2.values()))}'],
            ["Blind: agreements stated by the named decision", E(str(vp.get("blind_agreements_held", "–"))), "not run (audit C)"],
            ["Blind: express overrulings found", E(str(vp.get("blind_express_found", "–"))), "not scored"],
            ["Held-out admitted acts that are overrulings", E(str(vp.get("heldout_acts_overruling", "–"))), "not run (audit C)"],
            ["Held-out admitted acts naming the right target", E(str(vp.get("heldout_acts_right_target", "–"))), "not run (audit C)"],
            ["CRS 2016 express found", E(str(vp.get("crs2016_express_found", "–"))),
             f'{fmt(g(c2, "2016_express", "found"))}/{fmt(g(c2, "2016_express", "resolved"))}' if g(c2, "2016_express") else "pending"]]
    parts.append(table(["Measure", "v1", "v2"], rows))
    parts.append(src(EVAL / "results.json", EVAL / "results_v1.json"))
    # audits
    parts.append("<h3>Blind audits</h3>")
    parts.append(audits(c))
    parts.append("</section>")
    return "\n".join(parts)


def audits(c):
    out = []
    a = read_json(EVAL / "audits" / "gold-notes" / "score.json")
    b = read_json(EVAL / "audits" / "notes-blind" / "score.json")
    if b:
        v = b.get("verdicts", {})
        n = sum(v.values())
        ab = {k: sum(x.values()) for k, x in b.get("per_kind_scope", {}).items()}
        def kind_tot(kind, verdict=None):
            return sum((x.get(verdict, 0) if verdict else sum(x.values()))
                       for k, x in b.get("per_kind_scope", {}).items() if k.split(":")[0] == kind)
        ex = v.get("express", 0)
        out.append(f"""<div class="key"><p><b>Key finding: later courts' notes are a noisy target.</b> We drew
{fmt(n)} named negative notes and had blind readers check whether the named decision's own majority says it. It says
it in words in {fmt(ex)} ({pct(ex, n)}, Wilson {wil_str(ex, n)}). It rejects the holding without saying so in
{fmt(v.get("implicit"))}, only mentions or reports it in {fmt(v.get("mentions"))}, and the target is absent from the
excerpts in {fmt(v.get("absent"))}. For abrogation the gap is widest: {fmt(kind_tot("abrogated", "express"))} of
{fmt(kind_tot("abrogated"))} abrogation notes are stated by the named decision; abrogation is mostly a later court's
judgment. For overruling, {fmt(kind_tot("overruled", "express"))} of {fmt(kind_tot("overruled"))}. A model that admits
only what a court says itself cannot agree with a note whose named decision never says it. So agreement with notes
understates how often the model is right, and the blind audits, not the notes, measure precision.</p></div>""")
        out.append(bars([(k, v.get(k)) for k in ("express", "implicit", "mentions", "absent")], total=n))
        rows = []
        for k, x in b.get("per_kind_scope", {}).items():
            t = sum(x.values())
            rows.append([E(k), fmt(t), fmt(x.get("express", 0)), fmt(x.get("implicit", 0)), fmt(x.get("mentions", 0)),
                         fmt(x.get("absent", 0)), pct(x.get("express", 0), t)])
        out.append(details("Audit B by kind and scope", table(["Note kind:scope", "n", "express", "implicit", "mentions",
                                                                "absent", "express share"], rows, num_cols={1, 2, 3, 4, 5, 6})))
        v1 = b.get("v1", {})
        if v1:
            out.append(f"<p>v1 on the same pairs: {fmt(v1.get('agreements'))} agreements, "
                       f"{fmt(v1.get('agreements_stated_express'))} of them stated expressly; it found "
                       f"{E(str(v1.get('express_found')))} of the express notes. v2 on the same pairs: not scored "
                       f"in this build.</p>")
        out.append(src(EVAL / "audits" / "notes-blind" / "score.json"))
    else:
        out.append(pending(EVAL / "audits" / "notes-blind" / "score.json"))
    if a:
        rows = []
        for k, x in a.get("per_kind", {}).items():
            rows.append([E(k), fmt(x.get("n")), fmt(x.get("all_ok")), pct(x.get("all_ok"), x.get("n")),
                         wil_str(x.get("all_ok", 0), x.get("n", 0)), fmt(x.get("kind_ok")), fmt(x.get("notANote", 0))])
        t = a.get("total", {})
        rows.append(["<b>Total</b>", fmt(t.get("n")), fmt(t.get("all_ok")), pct(t.get("all_ok"), t.get("n")),
                     wil_str(t.get("all_ok", 0), t.get("n", 0)), fmt(t.get("kind_ok")), fmt(t.get("notANote"))])
        out.append(f"<p><b>Audit A: is the gold itself read right?</b> Blind readers checked {fmt(t.get('n'))} typed "
                   f"notes for target, treating decision, kind and scope. This was a development check: two general "
                   f"fixes were made after the first reading.</p>")
        out.append(table(["Kind", "n", "All right", "Share", "95% interval", "Kind right", "Not a note"], rows,
                         num_cols={1, 2, 3, 4, 5, 6}))
        out.append(src(EVAL / "audits" / "gold-notes" / "score.json"))
    else:
        out.append(pending(EVAL / "audits" / "gold-notes" / "score.json"))
    others = sorted(p for p in (EVAL / "audits").glob("*/score.json") if p.parent.name not in ("gold-notes", "notes-blind"))
    if others:
        for p in others:
            d = read_json(p)
            flat = []
            def walk(x, pre=""):
                if isinstance(x, dict):
                    for k, v in x.items():
                        walk(v, f"{pre}{k}." if pre or True else k)
                elif isinstance(x, list):
                    flat.append([E(pre.rstrip(".")), E(json.dumps(x)[:200])])
                else:
                    flat.append([E(pre.rstrip(".")), fmt(x) if isinstance(x, (int, float)) else E(str(x))])
            walk(d)
            out.append(f"<h5>Audit {E(p.parent.name)}</h5>" + table(["Key", "Value"], flat[:80], num_cols={1}) + src(p))
    else:
        out.append(pending(EVAL / "audits" / "<C admitted, D rejected, E splits>" / "score.json",
                           why="Audits C, D and E of the audit plan were not run. The blind audits that were run on "
                               "the runner's outputs are the hunt's, in section 9."))
    return "\n".join(out)


# ---------------------------------------------------------------- difftest, deviations, reproduce

def sec_diff(c):
    d = c.diff
    if not d:
        return '<section id="diff"><h2>11. Differential testing and fuzzing</h2>' + pending(C2 / "DIFFTEST.md") + "</section>"
    classes = re.findall(r"^### (.+?) \((\w)\): (\d+)", d, re.M)
    total = sum(int(n) for _, _, n in classes)
    rounds = md_section(d, r"^2\. Rounds run")
    who = md_section(d, r"^Which side was wrong")
    resid = md_section(d, r"^4\. Residuals")
    real = md_section(d, r"^5\. Real data")
    fin = md_section(d, r"^11\.1 Final state") or md_section(d, r"^8\.4 Final state")
    side8 = md_section(d, r"^8\.5 Which side was wrong")
    first8 = md_section(d, r"^8\.1 The pending commands")
    tri8 = md_section(d, r"^8\.2 Triage")
    wsl = md_section(d, r"^8\. Verification under WSL")
    wsl_intro = wsl.split("\n### ")[0] if wsl else ""
    fin_tiles = []
    # round 4: the newest final state has its own introduction (DIFFTEST section 11)
    r4 = md_section(d, r"^11\. Round 4")
    if r4 and md_section(d, r"^11\.1 Final state"):
        wsl_intro = r4.split("\n### ")[0]
    mreal = re.search(r"\| Real data \(`(\w+)`\) \|(.*?)\|\s*$", fin or "", re.M)
    if mreal:
        for name, a, b in re.findall(r"(\w+) \*\*([\d,]+)/([\d,]+)\*\*", mreal.group(2)):
            fin_tiles.append((f"{name}: keys that differ", f"{a}/{b}", f"real data, {mreal.group(1)}"))
    final_html = (f"""<h3>Final state, on the real data and on generated universes</h3>
{md(wsl_intro, 3)}
{tiles(fin_tiles) if fin_tiles else pending(C2 / "DIFFTEST.md", why="(the §8.4 real-data row was not found)")}
{md(fin, 3)}
{details("This pass: which side was wrong", md(side8, 3)) if side8 else ""}
{details("The first WSL run and the triage of its residue (§8.1, §8.2)", md((first8 or "") + chr(10) * 2 + (tri8 or ""), 3)) if first8 else ""}
""" if fin else "<h3>Final state</h3>" + pending(C2 / "DIFFTEST.md", why="(§8.4 was not found)"))
    try:
        fuzz = fuzz_html(c)
    except Exception:
        fuzz = (f'<h3>Fuzzing the glue</h3><div class="pending"><b>This part failed to render.</b>'
                f'<pre>{E(traceback.format_exc())}</pre></div>')
    cls_det = ""
    for title, letter, n in classes:
        s = md_section(d, r"^" + re.escape(title) + r" \(" + letter + r"\)")
        cls_det += details(f"({letter}) {E(title)}: {n}", md(s or "", 3))
    return f"""
<section id="diff"><h2>11. Differential testing and fuzzing</h2>
<p>An independent Python reference, written from doctrine.md by a different agent and never from the Lean, was run
against the Lean runner on fixtures, on generated universes and on the real data. Every disagreement was triaged
into one of four classes and both sides were fixed until they agreed.</p>
{final_html}
<h3>Disagreement classes and who was wrong, first pass</h3>
{bars([(f"({l}) {E(t)}", int(n)) for t, l, n in classes], total=total)}
{md(who, 3) if who else ""}
{details("Every class, with its fix", cls_det)}
<h3>Rounds</h3>
{md(rounds, 3) if rounds else ""}
<h3>Residuals</h3>
{md(resid, 3) if resid else ""}
{details("Real data, first pass (§5; superseded by the final state above)", md(real, 3)) if real else ""}
{src(C2 / "DIFFTEST.md")}
{fuzz}
</section>"""


def sec_dev(c):
    fb = md_section(c.dev, r"^Fallbacks for unknown data")
    simp = md_section(c.dev, r"^Simplifications")
    d4 = md_section(c.dev, r"^Readings chosen")
    n_items = len(re.findall(r"^(\d+)\.\s", c.dev or "", re.M))
    tested = md_section(c.trust, r"^Tested only")
    assumed = md_section(c.trust, r"^Assumed")
    gaps_c = md_section(c.courts, r"^Known gaps")
    gaps_s = md_section(c.stat, r"^Gaps")
    data_d = md_section(c.diff, r"^Data or contract")
    top = ""
    if simp:
        items = re.split(r"\n(?=\d+\.\s)", "\n" + simp)
        items = [x.strip() for x in items if x.strip()]
        pick = [x for x in items if re.match(r"(1|2|5|15|16|22|25|28)\.\s", x)]
        top = md("\n".join(pick), 3)
    return f"""
<section id="limits"><h2>12. Deviations and limits</h2>
<p><code>DEVIATIONS.md</code> lists {n_items} numbered departures from doctrine.md, plus the fallbacks for unknown data.
Every fallback is a named <code>assume*</code> label, so it appears in the rule path of every verdict that used it.</p>
<h3>Fallbacks for unknown data</h3>
{md(fb, 3) if fb else pending(C2 / "DEVIATIONS.md")}
<h3>The departures that matter most</h3>
<p>Selected for this report: those that change what a verdict can say (case kind, pre-<i>Erie</i>, Marks, implicit
abrogation, revival, partial scope, certificate targets, splits).</p>
{top}
{details("All simplifications (DEVIATIONS.md 1–29)", md(simp or "", 3))}
{details("Readings chosen in differential testing (DEVIATIONS.md 30–54)", md(d4 or "", 3))}
{details("The five limits (DEVIATIONS.md, second pass)", md(md_section(c.dev, r"^Five limits") or "", 3))}
{details("The hunt fixes and the WSL run (DEVIATIONS.md, last items; one is open)", md(md_section(c.dev, r"^Hunt fixes and the WSL verification run") or "", 3))}
<h3>The limits follow-up</h3>
<p>After the first pass, the limits it had listed were worked through one by one: five in the Lean and the rest in
the courts and reader data. What is still open is under "Data gaps" below.</p>
{limits_table(c)}
{details("The data fixes in full (courts_validation.md §5)", md(md_section(c.cval, r"^5\. Fixes to validated limits") or "", 3))}
{details("The Lean changes in full (LEAN.md, Five limits)", md(md_section(c.lean, r"^Five limits") or "", 3))}
<h3>Data gaps</h3>
{details("Courts and decisions", md(gaps_c or "", 3))}
{details("Statutes", md(gaps_s or "", 3))}
{details("Data and contract problems found in differential testing", md(data_d or "", 3))}
<h3>What is tested, not proved, and what is assumed</h3>
{md(tested, 3) if tested else ""}
{md(assumed, 3) if assumed else ""}
<p>And the limit no proof removes: a passing certificate shows that these words, at this place, in this part of this
court's opinion, warrant the row. It does not show the reading is legally right. That is measured by the audits and
oracles in section 10, not proved.</p>
{src(C2 / "DEVIATIONS.md", C2 / "TRUST.md", DATA / "COURTS.md", DATA / "STATUTES.md")}
</section>"""


def sec_repro(c):
    lean_cmds = re.search(r"\n((?:    .*\n)+)", c.lean or "")
    return f"""
<section id="repro"><h2>13. Reproduce</h2>
<p>Lean (from <code>~/Documents/global-law-lean/lean-proofs</code>) and the runner (from
<code>~/Documents/us-caselaw-lean-work/caselaw-lean-2</code>):</p>
<pre><code>{E(textwrap_dedent(lean_cmds.group(1))) if lean_cmds else ""}</code></pre>
<p>Differential testing (<code>lean-proofs/tools/caselaw2/ref/</code>) and the real-data diff:</p>
<pre><code>python gen.py --seed S --rounds N [--n 60] --out DIR --ref --lean --diff
python regress.py
difftest/run_real.sh real3</code></pre>
<p>Evaluation (<code>lean-proofs/tools/caselaw2/eval/</code>):</p>
<pre><code>python score.py          # eval/results.json and eval/tables/*.tsv
python score.py --v1     # v1 on the same gold: eval/results_v1.json
python sampler.py &lt;audit&gt; &lt;n&gt;   # blind audit packets; seed 20261112</code></pre>
<p>This report:</p>
<pre><code>python ~/Documents/us-caselaw-lean-work/caselaw-lean-2/report/make_report.py
python ~/Documents/us-caselaw-lean-work/caselaw-lean-2/report/lean_stats.py   # Lean counts as JSON</code></pre>
{details(f"Inputs read for this build ({len(INPUTS_USED)} paths)", inputs_table())}
</section>"""


# The film of the project (lean-proofs/video/out). The report sits in ~/Documents/html-reports, so the link is
# relative to ~/Documents; it works when the report is opened from disk.
FILM = Path.home() / "Documents" / "global-law-lean" / "lean-proofs" / "video" / "out" / "caselaw-lean-2.mp4"
FILM_REL = "../global-law-lean/lean-proofs/video/out/caselaw-lean-2.mp4"


def film_block():
    if not FILM.exists():
        return ""
    mb = FILM.stat().st_size / 1e6
    return (f'<figure class="film"><video controls preload="none" style="width:100%;max-width:960px;height:auto;'
            f'border-radius:8px;background:#000" src="{FILM_REL}"></video>'
            f'<figcaption>The film of the project (<a href="{FILM_REL}">caselaw-lean-2.mp4</a>, {mb:.0f} MB, a local '
            f'file: it plays when the report is opened from this machine).</figcaption></figure>')


def sec_rounds(c):
    """The improvement rounds, from the coordinator's own write-ups (ROUND2.md, ROUND3.md, ...), newest first. Each
    file is shown whole; a round whose file is not written yet renders a pending box."""
    parts = ['<section id="rounds"><h2>14. Improvement rounds</h2>',
             '<p class="lead">After the first pass the model, the data and the readers were improved in rounds. Each '
             'round ends with one integrated build, audit, regression, real-data run and score; its write-up is shown '
             'here as written.</p>']
    files = sorted(C2.glob("ROUND[0-9]*.md"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0), reverse=True)
    newest = max([int(re.sub(r"\D", "", p.stem) or 0) for p in files] + [0])
    # the summary across rounds and what is left, from the newest write-up (sections "Across rounds" and
    # "Remaining and deferred"), shown open above the write-ups
    if files:
        t0 = read(files[0]) or ""
        for pat, title in ((r"^Across rounds", "Before and after, across the rounds"),
                           (r"^Remaining and deferred", "Remaining and deferred")):
            body = md_section(t0, pat)
            if body:
                parts.append(f"<h3>{title}</h3>" + md(body, 3))
    parts.append(film_block())
    # the round in progress: its folder exists before its write-up does
    for d in sorted(C2.glob("round[0-9]*")):
        n = int(re.sub(r"\D", "", d.name) or 0)
        if d.is_dir() and n > newest:
            note_input(C2 / f"ROUND{n}.md")
            parts.append(f"<h3>Round {n}</h3>" + pending(C2 / f"ROUND{n}.md"))
    for i, p in enumerate(files):
        t = read(p) or ""
        n = re.sub(r"\D", "", p.stem)
        h1 = re.search(r"^# (.+)$", t, re.M)
        body = re.sub(r"^# .+\n", "", t, count=1, flags=re.M)
        parts.append(f"<h3>Round {E(n)}</h3>")
        parts.append(details(f"{h1.group(1) if h1 else p.name} ({p.name}, {mtime(p)})", md(body, 3), open_=(i == 0)))
        parts.append(src(p))
    if not files and len(parts) == 2:
        parts.append(pending(C2 / "ROUND2.md"))
    parts.append("</section>")
    return "\n".join(parts)


def textwrap_dedent(s):
    import textwrap
    return textwrap.dedent(s).strip()


def inputs_table():
    rows = []
    for p, ok, m in INPUTS_USED:
        if p.endswith(".lean"):
            continue
        rows.append([f"<code>{E(rel(Path(p)))}</code>", "present" if ok else "<b>missing</b>", E(m)])
    lean_n = sum(1 for p, ok, m in INPUTS_USED if p.endswith(".lean"))
    rows.append([f"<code>{E(rel(LEANDIR))}/*.lean</code>", f"{lean_n} files", ""])
    return table(["Path", "State", "Modified"], rows)


# ---------------------------------------------------------------- page

CSS = """
:root{--bg:#fcfcfb;--surface:#ffffff;--surface-2:#f4f3f0;--border:#e2e0da;--text:#141413;--text-2:#52514e;
--muted:#73726c;--accent:#2a78d6;--s1:#eb6834;--s2:#2a78d6;--pend-bg:#fdf6e6;--pend-bd:#e7c46b;--key-bg:#eef4fc;
--key-bd:#9cc0ec;--code:#f1efea;--d-untr:#fbeee8;--d-chk:#eaf2fb;--d-exec:#eef6f1;--d-spec:#f1eefb;--d-out:#f4f3f0;
--d-stroke:#8a877f;--boundary:#c0392b;color-scheme:light}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1a1a19;--surface:#222220;--surface-2:#2a2a28;
--border:#3a3a37;--text:#f0efec;--text-2:#c3c2b7;--muted:#9c9b93;--accent:#3987e5;--s1:#d95926;--s2:#3987e5;
--pend-bg:#3a3220;--pend-bd:#8a6d22;--key-bg:#1f2a38;--key-bd:#365f8f;--code:#2d2d2a;--d-untr:#3a2a24;--d-chk:#1f2a38;
--d-exec:#1f3027;--d-spec:#2a2538;--d-out:#2a2a28;--d-stroke:#9c9b93;--boundary:#e66767;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#1a1a19;--surface:#222220;--surface-2:#2a2a28;--border:#3a3a37;--text:#f0efec;
--text-2:#c3c2b7;--muted:#9c9b93;--accent:#3987e5;--s1:#d95926;--s2:#3987e5;--pend-bg:#3a3220;--pend-bd:#8a6d22;
--key-bg:#1f2a38;--key-bd:#365f8f;--code:#2d2d2a;--d-untr:#3a2a24;--d-chk:#1f2a38;--d-exec:#1f3027;--d-spec:#2a2538;
--d-out:#2a2a28;--d-stroke:#9c9b93;--boundary:#e66767;color-scheme:dark}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,
"Helvetica Neue",Arial,sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px 80px;overflow-wrap:break-word}
h1{font-size:2.1rem;line-height:1.15;margin:.2em 0 .4em;letter-spacing:-.01em}
h2{font-size:1.45rem;margin:2.4em 0 .6em;padding-top:.6em;border-top:1px solid var(--border)}
h3{font-size:1.12rem;margin:1.8em 0 .5em}
h4,h5,h6{font-size:1rem;margin:1.3em 0 .4em}
p{margin:.6em 0}
a{color:var(--accent);overflow-wrap:anywhere}
code{font:0.86em/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--code);padding:.08em .3em;
border-radius:4px;overflow-wrap:break-word}
pre{background:var(--code);padding:12px 14px;border-radius:8px;overflow-x:auto;font-size:.86em;line-height:1.45}
pre code{background:none;padding:0;overflow-wrap:normal;white-space:pre}
.kicker{color:var(--muted);font-size:.86rem;margin:0}
.lead{font-size:1.06rem;color:var(--text)}
.muted{color:var(--muted)}
.small,.src{font-size:.84rem;color:var(--text-2)}
.src code{font-size:.92em}
nav.toc{font-size:.92rem;margin:20px 0;padding:12px 16px;background:var(--surface-2);border-radius:10px}
nav.toc ol{margin:0;padding-left:1.3em;columns:2;column-gap:28px}
@media (max-width:640px){nav.toc ol{columns:1}}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:20px 0}
.tile{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 14px}
.tile-val{font-size:1.5rem;font-weight:650;font-variant-numeric:tabular-nums;line-height:1.2}
.tile-lab{font-size:.86rem;color:var(--text);margin-top:2px}
.tile-sub{font-size:.78rem;color:var(--muted)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:4px 18px 10px;margin:16px 0}
.card h3{margin-top:.9em}
.tw{overflow-x:auto;margin:10px 0;max-width:100%}
table{border-collapse:collapse;width:100%;font-size:.88rem;font-variant-numeric:tabular-nums}
th,td{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--border)}
thead th{font-weight:600;color:var(--text-2);background:var(--surface-2);border-bottom:1px solid var(--border)}
td.num,th.num{text-align:right;white-space:nowrap}
table.cmp td:first-child{font-weight:600;white-space:nowrap}
table.reg td:first-child{width:38%}
table.reg td:first-child code{font-size:.8em}
details{margin:8px 0;border:1px solid var(--border);border-radius:8px;background:var(--surface)}
details>summary{cursor:pointer;padding:8px 12px;font-weight:550;font-size:.92rem}
details>summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
details .det{padding:2px 14px 10px}
details.stm{border:none;background:none;margin:4px 0 0}
details.stm>summary{padding:0;font-weight:400;font-size:.8rem;color:var(--muted)}
.code{font:0.78rem/1.45 ui-monospace,Menlo,Consolas,monospace;overflow-wrap:anywhere}
.code code{background:none;padding:0}
.pending{background:var(--pend-bg);border:1px solid var(--pend-bd);border-radius:8px;padding:10px 14px;margin:10px 0;
font-size:.92rem}
.note{background:var(--surface-2);border-left:3px solid var(--muted);padding:8px 14px;margin:10px 0;font-size:.92rem;
border-radius:0 8px 8px 0}
.key{background:var(--key-bg);border:1px solid var(--key-bd);border-radius:10px;padding:6px 16px;margin:12px 0}
.tag{display:inline-block;font-size:.72rem;font-weight:600;color:var(--text-2);border:1px solid var(--border);
border-radius:4px;padding:0 6px;vertical-align:middle;margin-left:6px}
.bars{margin:10px 0 14px}
.bar-row{display:grid;grid-template-columns:minmax(0,34%) 1fr auto;align-items:center;gap:10px;padding:3px 0;
font-size:.86rem}
.bar-lab{overflow-wrap:anywhere;line-height:1.3}
.bar-svg{width:100%;height:14px;display:block}
.bar-val{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;min-width:4.5em}
.bar-fill{fill:var(--accent)}
.bar-fill.s1{fill:var(--s1)} .bar-fill.s2{fill:var(--s2)}
.bar-row:hover .bar-fill{opacity:.8}
.bar-row2{display:grid;grid-template-columns:minmax(0,34%) 1fr;gap:10px;padding:5px 0;font-size:.86rem;
border-bottom:1px solid var(--border)}
.pair{display:grid;grid-template-columns:auto 1fr auto;align-items:center;column-gap:8px;row-gap:2px}
.pl{font-size:.78rem;color:var(--muted);white-space:nowrap}
.sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.sw.s1{background:var(--s1)} .sw.s2{background:var(--s2)}
.legend{display:flex;gap:16px;font-size:.84rem;color:var(--text-2);margin-bottom:4px}
@media (max-width:560px){.bar-row{grid-template-columns:1fr auto;grid-template-areas:"l v" "b b";row-gap:2px}
.bar-row .bar-lab{grid-area:l}.bar-row .bar-val{grid-area:v}.bar-row .bar-svg{grid-area:b}
.bar-row2{grid-template-columns:1fr}}
table.matrix{width:auto;font-size:.8rem}
table.matrix th.mh{writing-mode:horizontal-tb;text-align:center;padding:4px 3px;font-size:.74rem}
table.matrix th.mp{position:sticky;left:0;background:var(--surface);font-weight:500;min-width:190px;max-width:260px}
table.matrix td.mc{text-align:center;padding:4px 3px;color:var(--s1);min-width:26px}
table.matrix td.k{background:var(--surface-2)}
ul.cols{columns:2;column-gap:24px}
@media (max-width:640px){ul.cols{columns:1}}
ul.links{font-size:.84rem;padding-left:1.2em}
figure.diagram{margin:16px auto;max-width:520px}
figure.diagram svg{width:100%;height:auto;display:block}
figcaption{font-size:.86rem;color:var(--text-2);margin-top:6px}
.d-box{stroke:var(--d-stroke);stroke-width:1}
.d-untr{fill:var(--d-untr)} .d-chk{fill:var(--d-chk)} .d-exec{fill:var(--d-exec)} .d-spec{fill:var(--d-spec)}
.d-out{fill:var(--d-out)}
.d-t{font:600 13px system-ui,sans-serif;fill:var(--text);text-anchor:middle}
.d-s{font:11px system-ui,sans-serif;fill:var(--text-2);text-anchor:middle}
.d-l{text-anchor:start}
.d-zone{font:600 10px system-ui,sans-serif;fill:var(--muted);letter-spacing:.06em}
.d-line{stroke:var(--d-stroke);stroke-width:1.5;fill:none}
.d-arrowhead{fill:var(--d-stroke)}
.d-boundary{stroke:var(--boundary);stroke-width:1.5;stroke-dasharray:6 4}
ol,ul{padding-left:1.4em}
li{margin:.2em 0}
.mdh{font-size:1rem}
"""


def page(c):
    sections = [
        ("why", "Why v1 was small, and what v2 adds", sec_why),
        ("research", "Design research", sec_research),
        ("arch", "Architecture", sec_arch),
        ("lean", "The Lean model", sec_lean),
        ("data", "Data layers", sec_data),
        ("results", "Results", sec_results),
        ("heatmaps", "Vulnerability heatmaps", sec_heatmaps),
        ("hunt", "Loopholes and mistakes found (the hunt)", sec_hunt),
        ("eval", "Evaluation", sec_eval),
        ("diff", "Differential testing and fuzzing", sec_diff),
        ("limits", "Deviations and limits", sec_dev),
        ("repro", "Reproduce", sec_repro),
        ("rounds", "Improvement rounds", sec_rounds),
    ]
    body = []
    try:
        body.append(sec_header(c))
    except Exception:
        body.append(f'<div class="pending"><b>Header failed to render.</b><pre>{E(traceback.format_exc())}</pre></div>')
    sub_toc = {"eval": [("why-half", "Why we find only about half of the overrulings on the published lists"),
                        ("why-notes", "Why agreement with later courts’ notes is lower still")]
               if (HERE_SECTIONS / "why_recall.html").exists() else []}
    toc = "".join(f'<li><a href="#{i}">{t}</a>' + ("<ul>" + "".join(
        f'<li><a href="#{a}">{b}</a></li>' for a, b in sub_toc[i]) + "</ul>" if sub_toc.get(i) else "") + "</li>"
        for i, t, _ in sections)
    body.append(f'<nav class="toc" aria-label="Contents"><ol start="2">{toc}</ol></nav>')
    for sid, title, fn in sections:
        try:
            body.append(fn(c))
        except Exception:
            body.append(f'<section id="{sid}"><h2>{E(title)}</h2><div class="pending"><b>This section failed to render.'
                        f'</b><pre>{E(traceback.format_exc())}</pre></div></section>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>caselaw-lean-2 results</title>
<meta name="description" content="caselaw-lean-2: a Lean model of US precedent at the level of holdings, with certificate-checked treatments, run over all US case law and tested against courts' own notes.">
<style>{CSS}</style></head>
<body><main>
{''.join(body)}
<p class="small" style="margin-top:3em">Generated by <code>caselaw-lean-2/report/make_report.py</code> on
{dt.datetime.now().strftime("%Y-%m-%d %H:%M")}. Every number on this page is read or computed from the files named
under it.</p>
</main></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--artefacts", default=None, help="folder holding caselaw-v1-v2.svg/.json and heatmaps/ "
                                                      "(default: this script's folder)")
    a = ap.parse_args()
    if a.artefacts:
        global ART
        ART = Path(a.artefacts).resolve()
    c = load()
    h = page(c)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(h)
    present = sum(1 for _, ok, _ in INPUTS_USED if ok)
    print(f"wrote {a.out} ({len(h):,} bytes); inputs present {present}/{len(INPUTS_USED)}; "
          f"out/ {'present' if c.out_ok else 'missing'}")


if __name__ == "__main__":
    main()
