"""Shared helpers of the round-5 blind precision audits (make_audit.py, more_text.py, score_audit.py).

Nothing here reads gold/ or round5/gold_fresh/sealed/. The only large tables touched are graph/nodes.tsv and the
stage's decisions2.tsv, and both are streamed for the wanted node ids only.
"""
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # importing the reader's common.py must not write outside round5/audit

HERE = os.path.dirname(os.path.abspath(__file__))  # .../caselaw-lean-2/round5/audit
R5 = os.path.dirname(HERE)
C2 = os.path.dirname(R5)
WORKROOT = os.path.dirname(C2)
GRAPH = os.path.join(WORKROOT, "graph")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
TOOLS = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2")
READER = os.path.join(TOOLS, "reader")
CUE_TABLE = os.path.join(TOOLS, "cues", "cue_table.json")
SCOTUS_META = os.path.join(R5, "gold_fresh", "work", "scotus_meta.tsv")
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

STATUS_KINDS = ("overruled", "abrogated", "disapproved", "recededFrom")


def utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ------------------------------------------------------------------------------------------------- text
def clean(x):
    """SCHEMA normalisation of quotes and certificate windows: tab, newline and a lone CR become a space, one for
    one (so an offset in the text is the same offset in the cleaned text)."""
    return x.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def decode(raw):
    """The decision file text as SCHEMA defines it: bytes at HEAD, UTF-8 decoded, CR LF -> LF."""
    return raw.decode("utf-8", "replace").replace("\r\n", "\n")


def read_rows(path, minf=1):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if line:
                p = line.split("\t")
                if len(p) >= minf:
                    rows.append(p)
    return rows


def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_rows(path, rows):
    write_text(path, "".join("\t".join(str(x) for x in r) + "\n" for r in rows))


# ------------------------------------------------------------------------------------------------- lookups
def nodes_info(want):
    """graph/nodes.tsv rows of the wanted node ids -> {node: (repo, path, date, [citations], name)}. Streamed."""
    out = {}
    wantb = {str(n).encode() for n in want}
    if not wantb:
        return out
    with open(os.path.join(GRAPH, "nodes.tsv"), "rb") as f:
        for raw in f:
            i = raw.find(b"\t")
            if raw[:i] in wantb:
                p = raw.rstrip(b"\r\n").decode("utf-8", "replace").split("\t")
                p += [""] * (7 - len(p))
                out[int(p[0])] = (p[1], p[2], int(p[4] or 0), [c for c in p[5].split("|") if c.strip()], p[6])
                if len(out) == len(wantb):
                    break
    return out


def decisions_info(path, want):
    """<stage>/decisions2.tsv rows of the wanted nodes -> {node: (court_id, date, text_sha)}. Streamed."""
    out = {}
    wantb = {str(n).encode() for n in want}
    if not wantb:
        return out
    with open(path, "rb") as f:
        for raw in f:
            i = raw.find(b"\t")
            if raw[:i] in wantb:
                p = raw.rstrip(b"\r\n").split(b"\t")
                if len(p) >= 8:
                    out[int(p[0])] = (int(p[1]), int(p[2] or 0), p[7].decode("ascii", "replace"))
                if len(out) == len(wantb):
                    break
    return out


def court_namer(courts2_path):
    """court_name(court_id, date) from <stage>/courts2.tsv (one row per court epoch); v1 names as fallback."""
    ep = {}
    for p in read_rows(courts2_path, 4):
        try:
            ep.setdefault(int(p[0]), []).append((int(p[1]), int(p[2]), p[3]))
        except ValueError:
            continue
    v1 = {}
    for p in read_rows(os.path.join(GRAPH, "courts.tsv"), 2):
        try:
            v1[int(p[0])] = p[1]
        except ValueError:
            continue

    def name(cid, date):
        rows = ep.get(cid)
        if rows:
            for a, b, nm in rows:
                if a <= date <= b:
                    return nm
            return rows[-1][2] if date > rows[-1][1] else rows[0][2]
        return v1.get(cid, "court %d" % cid)

    return name


def scotus_meta():
    """{node: (us_cite, name)} for Supreme Court nodes (fallback when graph/nodes.tsv has no name or citation)."""
    out = {}
    for p in read_rows(SCOTUS_META, 4)[1:]:
        try:
            out[int(p[0])] = (p[2], p[3])
        except ValueError:
            continue
    return out


# ------------------------------------------------------------------------------------------------- git
def git_texts(repo, paths):
    """{path: bytes} of HEAD:<path> for each path of one corpus repo (one `git cat-file --batch`)."""
    out = {}
    if not paths:
        return out
    inp = "".join("HEAD:%s\n" % p for p in paths).encode("utf-8")
    pr = subprocess.run(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], input=inp,
                        capture_output=True, creationflags=CREATE_NO_WINDOW)
    buf = pr.stdout
    pos = 0
    for p in paths:
        nl = buf.find(b"\n", pos)
        if nl < 0:
            break
        head = buf[pos:nl].split()
        pos = nl + 1
        if len(head) >= 2 and head[-1] == b"missing":
            continue
        if len(head) != 3:
            break
        size = int(head[2])
        out[p] = buf[pos:pos + size]
        pos += size + 1
    return out


# ------------------------------------------------------------------------------------------------- parts
_RC = None


def reader_common():
    global _RC
    if _RC is None:
        sys.path.insert(0, READER)
        import common as rc  # noqa: E402  (tools/caselaw2/reader/common.py: part_map2, part_at)
        _RC = rc
    return _RC


PART_WORDS = {
    "majority": "opinion of the court",
    "perCuriam": "opinion of the court (per curiam)",
    "plurality": "lead / plurality opinion",
    "concurrence": "a concurring opinion",
    "dissent": "a dissenting opinion",
    "headmatter": "head matter / syllabus (not part of any opinion)",
}


def part_label(text, off):
    """(words or '', body offset). The words describe the opinion part the offset lies in, from the reader's part
    map; '' when the map has no label there (front matter, title, unknown)."""
    rc = reader_common()
    pm, body0 = rc.part_map2(text)
    p, _sec = rc.part_at(pm, off)
    inferred = p.endswith("~")
    w = PART_WORDS.get(p.rstrip("~?"), "")
    if w and inferred:
        w += " [label inferred from the text, the file has no heading for it]"
    return w, body0


# ------------------------------------------------------------------------------------------------- names
_NOT_REPORTER = re.compile(r"LEXIS|SCDB|\bWL\b|^\s*No\.|^\s*\d{4}\s+[A-Z]{2,}\s+\d+\s*$")


def show_cites(cites, most=3):
    """Reporter citations to print: the first, then up to `most - 1` parallel ones (no LEXIS / WL / SCDB ids)."""
    good = [c.strip() for c in cites if c.strip() and not _NOT_REPORTER.search(c)]
    if not good:
        good = [c.strip() for c in cites if c.strip()][:1]
    seen, out = set(), []
    for c in good:
        k = re.sub(r"[\s.]", "", c).lower()
        if k not in seen:
            seen.add(k)
            out.append(c)
    return out[:most]


def case_label(name, cites, date, court=""):
    """`name, citation [also parallel; parallel] (year)`; without a citation the court takes its place."""
    nm = re.sub(r"\s+", " ", name or "").strip() or "[no name on file]"
    if len(nm) > 160:
        nm = nm[:157].rstrip() + "..."
    cs = show_cites(cites)
    yr = str(date // 10000) if date else "year unknown"
    if cs:
        also = " [also %s]" % "; ".join(cs[1:]) if len(cs) > 1 else ""
        return "%s, %s%s (%s)" % (nm, cs[0], also, yr)
    return "%s (%s, %s)" % (nm, court, yr) if court else "%s (%s)" % (nm, yr)


def iso_date(d):
    if not d:
        return "date unknown"
    return "%04d-%02d-%02d" % (d // 10000, d // 100 % 100, d % 100)


# ------------------------------------------------------------------------------------------------- statistics
def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None, None)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, max(0.0, (c - r) / d), min(1.0, (c + r) / d))


def fmt_rate(k, n):
    p, lo, hi = wilson(k, n)
    if p is None:
        return "0/0"
    return "%d/%d = %.3f [%.3f, %.3f]" % (k, n, p, lo, hi)
