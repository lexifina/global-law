"""(round 8 h0 shadow copy of benchmarks/common/benchlib.py: only ROOT changed.)
Shared helpers for the benchmarks/ scorers (standard library only; import with sys.path insert).

Model side follows round6/shepardized/MAPPING.md: decision-level rows of status.tsv (issue = '-', holding = '-')
whose interval from <= asof <= to; a decision with no row is good.

Results contract: every scorer writes benchmarks/<dataset>/results/<label>.json via write_result(); the graph
(benchmarks/graph/make_graph.py) reads only those files. See benchmarks/CONTRACT.md.
"""
import collections
import datetime
import hashlib
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(BENCH))  # caselaw-lean-2 (round 8 copy: round8/bench_h0/common)
GRAPH = os.path.join(os.path.dirname(ROOT), "graph")  # us-caselaw-lean-work/graph

# Builds (read only). label -> (out dir, data dir)
BUILDS = {
    "round4": (os.path.join(ROOT, "out"), os.path.join(ROOT, "data")),
    "round6": (os.path.join(ROOT, "round6", "history", "out", "final2"),
               os.path.join(ROOT, "round6", "history", "stage", "final2")),
    "round7": (os.path.join(ROOT, "round7", "out", "v3"), os.path.join(ROOT, "round7", "stage", "v3")),  # FREEZE.md v3
}
DEFAULT_ASOF = 20261112  # last 'to' date of the model's status intervals


def wilson(k, n, z=1.959964):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def metric(k, n):
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "p": (k / n if n else None), "lo": lo, "hi": hi}


def split_half(dataset, key):
    """50/50 hash split for the new benchmarks: 'h0' or 'h1'. Neither half is used for tuning."""
    v = int(hashlib.sha1(("bench:%s:%s" % (dataset, key)).encode("utf-8")).hexdigest(), 16)
    return ("h0", "h1")[v % 2]


def file_sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def model_class(status, path):
    if status.startswith("neg:"):
        return "NEG_HIST" if path == "history" else "NEG_OTHER"
    if status.startswith("unknown:"):
        return "UNK_HIST" if path == "history" else "UNK_OTHER"
    return "GOOD"


def load_status(out_dir, nodes=None, asof=DEFAULT_ASOF):
    """node -> dict(status, path, witness, actor, mclass) for decision-level rows live at asof.
    nodes: optional set of node id strings to keep (saves memory)."""
    st = {}
    with open(os.path.join(out_dir, "status.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[1] != "-" or p[2] != "-":
                continue
            if nodes is not None and p[0] not in nodes:
                continue
            if int(p[3]) <= asof <= int(p[4]):
                st[p[0]] = {"status": p[5], "path": p[10], "witness": p[8], "actor": p[9],
                            "mclass": model_class(p[5], p[10])}
    return st


def status_of(st, node):
    return st.get(node) or {"status": "good", "path": "-", "witness": "-", "actor": "-", "mclass": "GOOD"}


def _ok_ids(out_dir, table):
    ok = set()
    with open(os.path.join(out_dir, "certs.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0] == table and len(p) > 2 and p[2] == "ok":
                ok.add(p[1])
    return ok


def load_history(out_dir, data_dir, nodes):
    """target node -> list of dict(id, by, date, kind, scope, admitted) from history.tsv (any by/target in nodes)."""
    ok = _ok_ids(out_dir, "history")
    h = collections.defaultdict(list)
    with open(os.path.join(data_dir, "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[1] in nodes:
                h[p[1]].append({"id": p[0], "by": p[2], "date": p[3], "kind": p[4], "scope": p[5],
                                "admitted": p[0] in ok})
    return h


def load_treatments(out_dir, data_dir, nodes):
    """target node -> list of dict(id, by, date, kind, scope, admitted) from treatments.tsv."""
    ok = _ok_ids(out_dir, "treatment")
    t = collections.defaultdict(list)
    with open(os.path.join(data_dir, "treatments.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[2] in nodes:
                t[p[2]].append({"id": p[0], "by": p[1], "date": p[3], "kind": p[4], "scope": p[5],
                                "admitted": p[0] in ok})
    return t


RESULT_KEYS = ("dataset", "label", "split", "row_label", "tests", "court", "blind", "primary",
               "metrics", "link", "build", "generated")


def write_result(path, res):
    """Validate and write one results JSON. Required keys: see CONTRACT.md."""
    missing = [k for k in RESULT_KEYS if k not in res]
    if missing:
        raise ValueError("result missing keys: %s" % missing)
    assert res["tests"] in ("overruling", "same-case"), res["tests"]
    assert res["court"] in ("supreme", "federal", "state", "mixed"), res["court"]
    assert res["split"] in ("h0", "h1", "all", "dev", "sealed"), res["split"]
    assert res["primary"] in res["metrics"], "primary metric must be in metrics"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
