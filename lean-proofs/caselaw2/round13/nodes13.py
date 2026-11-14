"""Round 13 (agent infra12; = round11/nodes11.py with a default folder, an optional src column and the round-11
prefix check): the DESIGN13 section-4 overlay of Supreme Court order-list nodes.

Round 13: the default folder is the nodes v11d holds, round12/data_orders (1,045 nodes, ids 6,892,454..6,893,498),
so every round-13 tool sees v11d's order nodes with no option; --nodes DIR / R13_NODES=DIR selects another folder
(e.g. round13/data_orders, whose first 1,045 rows are round 11's, same local ids, same order: same node ids);
R13_NODES=none switches the overlay off (corpus nodes only). nodes.tsv may carry an optional 8th column `src`
(header name `src`, e.g. r12:longlist; `-` = default): the decisions2 row's src is then
c:self;u:-;b:default-scotus;p:<src>;f:<src> (default r11:orderlist = round 11's rows byte for byte).
check_prefix() checks that the active folder starts with v11d's local ids in v11d's order and lists the ones whose
text changed (stage13 --nodes refuses a folder that fails it).

Round 11 (infra11): `orders11` writes round12/data_orders/nodes.tsv + text/<local id>.txt (format:
round12/data_orders/FORMAT.md). This module gives every round-13 tool one view of those nodes:

  - node ids: N, N+1, ... in nodes.tsv file order, N = the corpus node count (graph/nodes.count, 6,892,454);
  - is_extra(n), local_id(n), node_of(local_id), meta(n) (court 2906 = Supreme Court of the United States, date,
    name = caption as printed, docket, disposition, list_file), raw(n) / text(n) / sha(n) (sha1 of the file bytes,
    the corpus's text_sha), decisions_lines() (the decisions2 rows, the corpus's S. Ct. memorandum shape),
    map_lines() (nodes_map.tsv), count() (N + number of nodes);
  - patch(): in memory, without editing round6/history/r6lib.py, makes r6lib's node_row, fetch_texts and Facts
    (date / court arrays) answer for the extra ids, so certify13, zones13, the audit pack builder and the linkers that
    use r6lib see the order nodes as ordinary S. Ct. decisions. patch_audit(A) also fills the docket in the audit
    library's node_facts. Pseudo-repo name for extra nodes in node_row: REPO ("@r11nodes"), path = the local id.

Round 11: active only when a nodes folder was given. Round 13: always active (the default folder above) unless
R13_NODES=none; activate(DIR) (stage13 / certify13 --nodes DIR) or R13_NODES=DIR (read at import; tools that spawn
worker processes set it so the workers see the same nodes). No answer-key file is read.

    python -X utf8 round13/nodes13.py --check DIR      load and validate a nodes folder; print counts and the id range
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
W = os.path.dirname(C2)
NODES_COUNT = os.path.join(W, "graph", "nodes.count")
SCOTUS = 2906  # courts2.tsv: Supreme Court of the United States
REPO = "@r11nodes"
HEADER = ["local_id", "docket", "date", "caption", "disposition", "list_file", "line_span"]
# decisions2 columns 3-6 + src for an order node: the corpus's S. Ct. memorandum decisions are
# `0 wholeCourt published memorandum c:self;u:-;b:default-scotus;p:reporter:U.S.;f:dtype` (268,434 rows of v10d);
# the src marks the provenance (the Lean reads only columns 0-7).
ROW_SHAPE = ("0", "wholeCourt", "published", "memorandum")
SRC = "c:self;u:-;b:default-scotus;p:r11:orderlist;f:r11:orderlist"
SRC_FMT = "c:self;u:-;b:default-scotus;p:%s;f:%s"  # round 12: optional `src` column (default r11:orderlist = SRC)
_TAG = re.compile(r"[A-Za-z0-9_.:-]+")
DEFAULT = os.path.join(C2, "round12", "data_orders")  # round 12: the nodes v11d holds
R11_MAP = os.path.join(C2, "round12", "stage", "v12a", "nodes_map.tsv")  # v11d: local id -> node id, text_sha
_ID = re.compile(r"[A-Za-z0-9_.-]+")

_S = {"dir": None, "base": None, "rows": [], "by_local": {}, "raw": {}}


def base_count():
    """The corpus node count N: graph/nodes.count when present (WSL mirror), else the length of r6lib's nodes.tsv
    offset index (round6/history/work/nodes_off.npy, one entry per graph/nodes.tsv line) on Windows."""
    if _S["base"] is None:
        if os.path.exists(NODES_COUNT):
            with open(NODES_COUNT, encoding="utf-8") as f:
                _S["base"] = int(f.read().strip())
        else:
            import numpy as np
            _S["base"] = int(len(np.load(os.path.join(C2, "round6", "history", "work", "nodes_off.npy"),
                                         mmap_mode="r")))
    return _S["base"]


def activate(d):
    """Load the nodes folder d (validates it; exits on a malformed folder). Returns the number of nodes."""
    d = os.path.abspath(d)
    p = os.path.join(d, "nodes.tsv")
    if not os.path.isfile(p):
        sys.exit("nodes13: no %s" % p)
    data = open(p, "rb").read()
    if b"\r" in data:
        sys.exit("nodes13: %s has CR line ends" % p)
    lines = data.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    hd = lines[0].split("\t") if lines else []
    if hd != HEADER and hd != HEADER + ["src"]:
        sys.exit("nodes13: %s: first line must be the header %s (optionally + src)" % (p, "\\t".join(HEADER)))
    rows, by_local = [], {}
    n0 = base_count()
    for k, line in enumerate(lines[1:], 2):
        f = line.split("\t")
        if len(f) != len(hd):
            sys.exit("nodes13: %s line %d: %d fields, want %d" % (p, k, len(f), len(hd)))
        r = dict(zip(hd, f))
        if r.get("src") == "-":
            r["src"] = ""
        if r.get("src") and not _TAG.fullmatch(r["src"]):
            sys.exit("nodes13: %s line %d: bad src %r" % (p, k, r["src"]))
        if not _ID.fullmatch(r["local_id"]) or r["local_id"].strip(".") == "":
            sys.exit("nodes13: %s line %d: bad local_id %r" % (p, k, r["local_id"]))
        if r["local_id"] in by_local:
            sys.exit("nodes13: %s line %d: local_id %s twice" % (p, k, r["local_id"]))
        if not re.fullmatch(r"\d{8}", r["date"]):
            sys.exit("nodes13: %s line %d: date %r is not yyyymmdd" % (p, k, r["date"]))
        r["node"] = n0 + len(rows)
        r["date"] = int(r["date"])
        by_local[r["local_id"]] = r
        rows.append(r)
    _S.update(dir=d, rows=rows, by_local=by_local, raw={})
    os.environ["R13_NODES"] = d  # worker processes (spawn) see the same nodes
    return len(rows)


def active():
    return _S["dir"] is not None


def folder():
    return _S["dir"]


def count():
    """The node count the Lean runner is given: N + the number of order nodes."""
    return base_count() + len(_S["rows"])


def is_extra(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return False
    return active() and base_count() <= n < count()


def row(n):
    return _S["rows"][int(n) - base_count()] if is_extra(n) else None


def local_id(n):
    r = row(n)
    return r["local_id"] if r else None


def node_of(lid):
    r = _S["by_local"].get(lid)
    return r["node"] if r else None


def nodes():
    return [r["node"] for r in _S["rows"]]


def raw(n):
    """The text file's bytes (None for a corpus node or a missing file)."""
    r = row(n)
    if r is None:
        return None
    lid = r["local_id"]
    if lid not in _S["raw"]:
        p = os.path.join(_S["dir"], "text", lid + ".txt")
        _S["raw"][lid] = open(p, "rb").read() if os.path.isfile(p) else None
    return _S["raw"][lid]


def text(n):
    b = raw(n)
    return None if b is None else b.decode("utf-8", "replace").replace("\r\n", "\n")


def sha(n):
    b = raw(n)
    return None if b is None else hashlib.sha1(b).hexdigest()


def meta(n):
    """{node, local_id, court (2906), court_name, date (yyyymmdd int), name (caption as printed), docket,
    disposition, list_file, line_span} of an order node; None for a corpus node."""
    r = row(n)
    if r is None:
        return None
    return {"node": r["node"], "local_id": r["local_id"], "court": SCOTUS,
            "court_name": "Supreme Court of the United States", "date": r["date"], "name": r["caption"],
            "docket": r["docket"].replace(";", "; "), "disposition": r["disposition"], "list_file": r["list_file"],
            "line_span": r["line_span"]}


def decisions_lines():
    """decisions2.tsv lines (str, no LF) for the order nodes, in node order; a node without its text file is an
    error (exit), since the row's text_sha must be the file's."""
    out = []
    for r in _S["rows"]:
        h = sha(r["node"])
        if h is None:
            sys.exit("nodes13: no text file for %s (text/%s.txt)" % (r["local_id"], r["local_id"]))
        src = SRC_FMT % (r["src"], r["src"]) if r.get("src") else SRC
        out.append("\t".join([str(r["node"]), str(SCOTUS), str(r["date"])] + list(ROW_SHAPE) + [h, src]))
    return out


def map_lines():
    """nodes_map.tsv lines: local_id, node, date, docket, text_sha."""
    return ["\t".join([r["local_id"], str(r["node"]), str(r["date"]), r["docket"], sha(r["node"]) or "-"])
            for r in _S["rows"]]


# ---- patches (in memory) ------------------------------------------------------------------------------------------
_PATCHED = set()


def patch(L=None):
    """Make r6lib (module L, default: import it) answer for the extra ids: node_row, fetch_texts, Facts. A no-op when
    no nodes folder is active, or when L is already patched."""
    if not active():
        return False
    if L is None:
        r6h = os.path.join(C2, "round6", "history")
        if r6h not in sys.path:
            sys.path.insert(0, r6h)
        import r6lib as L
    if id(L) in _PATCHED:
        return True
    orig_row, orig_fetch, orig_init = L.node_row, L.fetch_texts, L.Facts.__init__

    def node_row(n):
        r = row(n)
        if r is None:
            return orig_row(n)
        # graph/nodes.tsv shape: node, repo, path, ?, date, citations, name, (empty)
        return [str(r["node"]), REPO, r["local_id"], "0", str(r["date"]), "", r["caption"], ""]

    def fetch_texts(ns):
        ns = [int(x) for x in ns]
        out = orig_fetch([x for x in ns if not is_extra(x)])
        for x in ns:
            if is_extra(x) and raw(x) is not None:
                out[x] = (sha(x), text(x))
        return out

    def facts_init(self, *a, **k):
        orig_init(self, *a, **k)
        import numpy as np
        n1 = count()
        for name, val in (("date", lambda r: r["date"]), ("court", lambda r: _court2_index(self, L))):
            arr = getattr(self, name)
            if len(arr) < n1:
                ext = np.zeros(n1, dtype=arr.dtype)
                ext[:len(arr)] = arr
                for r in _S["rows"]:
                    ext[r["node"]] = val(r)
                setattr(self, name, ext)

    L.node_row, L.fetch_texts, L.Facts.__init__ = node_row, fetch_texts, facts_init
    _PATCHED.add(id(L))
    return True


def _court2_index(F, L):
    """The court id r6lib's Facts uses for the Supreme Court (its own constant SCOTUS2 when present)."""
    return int(getattr(L, "SCOTUS2", SCOTUS))


def patch_audit(A):
    """The audit library (round13/audit/audit13lib.py): node_facts gets the order node's caption, court, date and
    docket from meta() (the text has no front matter)."""
    if not active() or getattr(A, "_r13_nodes_patched", False):
        return False
    orig = A.node_facts

    def node_facts(n, F, L, text=None):
        m = meta(n)
        if m is None:
            return orig(n, F, L, text)
        return {"name": m["name"], "court": m["court_name"], "date": A.iso_date(m["date"]), "citations": "",
                "all_citations": [], "docket": m["docket"]}
    A.node_facts = node_facts
    A._r13_nodes_patched = True
    return True


def check_prefix():
    """Round 13: the active folder must start with v11d's order nodes (round12/stage/v12a/nodes_map.tsv: the same
    local ids in the same order), so they keep their node ids. Returns (ok, message, changed): changed = the local ids
    among them whose text sha1 differs from v11d's."""
    old = [l.split("\t") for l in open(R11_MAP, encoding="utf-8").read().split("\n")[1:] if l]
    rows = _S["rows"]
    if len(rows) < len(old):
        return False, "%d nodes, fewer than v11d's %d" % (len(rows), len(old)), []
    changed = []
    for k, o in enumerate(old):
        r = rows[k]
        if r["local_id"] != o[0] or r["node"] != int(o[1]):
            return False, "nodes.tsv row %d: local id %s (node %d); v11d has %s (node %s) there" % (
                k + 1, r["local_id"], r["node"], o[0], o[1]), []
        if (sha(r["node"]) or "-") != o[4]:
            changed.append(r["local_id"])
    return True, "first %d local ids = v11d's (same order, same node ids); text changed for %d of them" % (
        len(old), len(changed)), changed


_env = os.environ.get("R13_NODES")
if not active() and _env != "none":
    if _env:
        activate(_env if os.path.isabs(_env) else os.path.join(C2, _env))
    elif os.path.isfile(os.path.join(DEFAULT, "nodes.tsv")):
        activate(DEFAULT)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", required=True)
    a = ap.parse_args()
    n = activate(a.check)
    miss = [r["local_id"] for r in _S["rows"] if raw(r["node"]) is None]
    bad = [r["local_id"] for r in _S["rows"] if raw(r["node"]) is not None and
           (b"\r" in raw(r["node"]) or b"\t" in raw(r["node"]) or not raw(r["node"]).endswith(b"\n"))]
    print("nodes13: %d order nodes in %s; ids %d..%d (corpus count %d); text files missing %d%s; texts with CR/tab "
          "or no final LF %d%s" % (n, a.check, base_count(), count() - 1, base_count(), len(miss),
                                   (" (" + " ".join(miss[:10]) + ")") if miss else "", len(bad),
                                   (" (" + " ".join(bad[:10]) + ")") if bad else ""))
    sys.exit(1 if miss else 0)


if __name__ == "__main__":
    main()
