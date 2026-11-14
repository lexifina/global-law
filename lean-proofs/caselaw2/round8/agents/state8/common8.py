"""state8 shared helpers: citation index (staged v3 + graph), node facts, reader-stage files.

No answer-key file is read here.
"""
import collections, gzip, json, os, re, sys

C2 = os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2")
HERE = os.path.join(C2, "round8", "agents", "state8")
WORK = os.path.join(HERE, "work")
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, os.path.join(C2, "round6", "history", "citeforms"))
import r6lib as L  # noqa: E402
import r6cite  # noqa: E402

STAGE = os.path.join(C2, "round7", "stage", "v3")
OUT = os.path.join(C2, "round7", "out", "v3")
RW = os.path.join(C2, "data", "reader_work")
GRAPH_IDX = os.path.expanduser("~/Documents/us-caselaw-lean-work/graph/cite_index.tsv")
NL = chr(10)


def load_index(stage=STAGE):
    """key -> node; the staged cite_index first, then the graph index (a graph key with two nodes is dropped)."""
    idx = {}
    amb = set()
    with open(GRAPH_IDX, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) < 2:
                continue
            k, n = p[0], int(p[1])
            if k in idx and idx[k] != n:
                amb.add(k)
            else:
                idx[k] = n
    for k in amb:
        idx.pop(k, None)
    with open(os.path.join(stage, "cite_index.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) >= 2:
                idx[p[0]] = int(p[1])
    return idx


def cites_of(text, idx):
    """[(start, end, matched string, node|None, key|None, form)] for every WIDE_RX citation in text."""
    out = []
    for m in r6cite.finditer(text):
        r = r6cite.resolve(m, idx)
        if r:
            out.append((m.start(), m.end(), m.group(0), r[0], r[1], r[2]))
        else:
            out.append((m.start(), m.end(), m.group(0), None, None, None))
    return out


STOP = set("the of and in re ex rel parte v vs et al co inc corp company state people city county town bank "
           "railroad railway insurance ins mfg united states commonwealth estate matter".split())


def party_tokens(name):
    toks = re.findall(r"[A-Za-z][A-Za-z'’]+", name or "")
    return [t for t in toks if len(t) >= 3 and t.lower() not in STOP]


SENT_END = re.compile(r"(?<=[.;:?!])\s+(?=[A-Z“\"(])")


def sentence_around(text, pos, lim=700):
    a = max(0, pos - lim)
    b = min(len(text), pos + lim)
    seg = text[a:b]
    s0 = a
    for m in SENT_END.finditer(seg):
        if a + m.end() <= pos:
            s0 = a + m.end()
    e = b
    for m in SENT_END.finditer(seg):
        if a + m.start() >= pos:
            e = a + m.start()
            break
    return s0, e
