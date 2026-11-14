"""(round 8 h0 shadow copy of benchmarks/shadow_docket/sdlib.py: only ROOT changed.)
Shared helpers for the shadow_docket benchmark (standard library only)."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(BENCH))  # caselaw-lean-2 (round 8 copy: round8/bench_h0/shadow_docket)
sys.path.insert(0, os.path.join(BENCH, "common"))
import benchlib  # noqa: E402,F401

DATASET = "shadow_docket"
WORK = os.path.join(HERE, "work")

_STOP = {"NO", "NOS", "DOCKET", "DOCKETS", "NUMBER", "NUMBERS", "CASE", "CASES", "CAUSE", "APPEAL", "APPEALS",
         "AND", "NUM", "DKT"}
_TOK = re.compile(r"[A-Z0-9]+")
_SPLIT = re.compile(r";|,|&|\band\b|\bAND\b|\s/\s")


def clean(s):
    return (s or "").replace("\t", " ").replace("\n", " ").replace("\r", " ").strip()


def docket_key(piece):
    """One docket number -> normalised key ('' when unusable). Upper case; the words No./Nos./Docket dropped;
    alphanumeric groups joined by '-'; leading zeros of numeric groups dropped; letters glued to digits split
    ('S95A1298' stays one group). Needs at least 3 digits in all."""
    toks = _TOK.findall(piece.upper())
    while toks and toks[0] in _STOP:
        toks = toks[1:]
    toks = [t for t in toks if t not in _STOP]
    out = []
    for t in toks:
        if t.isdigit():
            t = t.lstrip("0") or "0"
        out.append(t)
    k = "-".join(out)
    if sum(ch.isdigit() for ch in k) < 3:
        return ""
    return k


_DOCKETLIKE = re.compile(r"^\(?[A-Za-z]*\d+-\d+[\w-]*\)?$")
_SLASH = re.compile(r"^(.*?\D)(\d+)/(\d+)(\D*)$")


def _pieces(raw):
    for piece in _SPLIT.split(raw or ""):
        sub = piece.split()
        # two docket numbers separated only by a space: '98-2424 99-1578'
        if len(sub) >= 2 and all(_DOCKETLIKE.match(s) for s in sub):
            parts = sub
        else:
            parts = [piece]
        for p in parts:
            p = p.strip().strip("()").strip()
            m = _SLASH.match(p)
            # '96-2045/2065' -> 96-2045 and 96-2065 (same length tail only)
            if m and len(m.group(2)) == len(m.group(3)):
                yield m.group(1) + m.group(2) + m.group(4)
                yield m.group(1) + m.group(3) + m.group(4)
            else:
                yield p


def docket_keys(raw):
    keys = []
    for piece in _pieces(raw):
        k = docket_key(piece)
        if k and k not in keys:
            keys.append(k)
    return keys


def load_courts():
    """courts2 id -> (system, tier, circuit) from data/courts2.tsv (read only)."""
    m = {}
    with open(os.path.join(ROOT, "data", "courts2.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 8:
                continue
            try:
                m[int(p[0])] = (int(p[4]), p[5], int(p[7]))
            except ValueError:
                continue
    return m


def load_court_names():
    m = {}
    with open(os.path.join(ROOT, "data", "courts2.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4:
                m[int(p[0])] = p[3]
    return m
