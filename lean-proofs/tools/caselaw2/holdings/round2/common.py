"""Shared loaders for the round-2 split work (private copy)."""
import os, re, sys, collections, json
W = os.path.expanduser("~/Documents/us-caselaw-lean-work")
C2 = os.path.join(W, "caselaw-lean-2")
PRIV = os.path.join(C2, "work", "round2", "splits")
DATA = os.environ.get("SPL_DATA") or os.path.join(PRIV, "data")
HT = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/holdings")
sys.path.insert(0, HT)
sys.path.insert(0, os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/eval"))


def sect(u):
    return re.sub(r"\(.*$", "", u or "-")


def load_issues(data=None):
    iss = {}
    for l in open(os.path.join(data or DATA, "issues.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        iss[f[0]] = f
    return iss


def load_holdings(data=None, pred=None):
    out = []
    for l in open(os.path.join(data or DATA, "holdings.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        if pred is None or pred(f):
            out.append(f)
    return out


def courts(data=None):
    """court -> (system, tier, circuit)"""
    cs = {}
    for l in open(os.path.join(data or DATA, "courts2.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        if f[0].lstrip("-").isdigit():
            cs[int(f[0])] = (int(f[4]), f[5], int(f[7]) if f[7].isdigit() else 0)
    return cs


def court_kind(c):
    """scotus | coa | other, from a courts() value"""
    if c is None:
        return "other"
    if c[0] == 0 and c[1] == "L":
        return "scotus"
    if c[0] == 0 and c[1] == "A" and c[2] > 0:
        return "coa"
    return "other"


def node_meta(nodes, data=None):
    """node -> (court, date, publication) for the wanted nodes, from decisions2.tsv"""
    want = set(nodes)
    out = {}
    with open(os.path.join(data or DATA, "decisions2.tsv"), encoding="utf-8") as fh:
        for l in fh:
            i = l.find("\t")
            try:
                n = int(l[:i])
            except ValueError:
                continue
            if n in want:
                f = l.split("\t", 7)
                out[n] = (int(f[1]), int(f[2]), f[5])
    return out


def node_names(nodes):
    """node -> (name, cite, date)"""
    want = set(nodes)
    out = {}
    with open(os.path.join(W, "graph", "nodes.tsv"), encoding="utf-8") as fh:
        for l in fh:
            i = l.find("\t")
            n = int(l[:i])
            if n in want:
                f = l.rstrip("\n").split("\t")
                out[n] = (f[6] if len(f) > 6 else "", f[5] if len(f) > 5 else "", f[4])
    return out


def wilson(k, n, z=1.96):
    from math import sqrt
    if not n:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))
