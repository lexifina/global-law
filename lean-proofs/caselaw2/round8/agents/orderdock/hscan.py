"""Round 8 `orderdock`: scan later texts for subsequent-history strings that name a Supreme Court order.

    python -X utf8 round8/agents/orderdock/hscan.py list      decisions dated >= 2013 by repo -> work/scan_nodes.pkl
    python -X utf8 round8/agents/orderdock/hscan.py scan      history strings               -> work/hist/*.jsonl
                                                               (resumable: a finished chunk is skipped)

A history string is "<decision below: citation or docket number> ..., cert. denied / vacated / ..., <Supreme Court
reference: U.S. / S. Ct. / L. Ed. page or 'No. 15-375'>" inside one citation sentence of any later decision.
Each match keeps the citations and docket numbers before the phrase (up to the previous ';' / sentence start) and the
Supreme Court references after it, with the offsets in the git-HEAD text (CRLF -> LF). No answer-key file is read.
"""
import collections
import json
import os
import pickle
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HIST = os.path.join(C2, "round6", "history")
sys.path.insert(0, HIST)
import r6lib as L  # noqa: E402

C = L.reader_common()
WORK = os.path.join(HERE, "work")
OUTD = os.path.join(WORK, "hist")
NL = chr(10)
FROM = 20130101
CHUNK = 4000

PHRASE = re.compile(
    r"\b(?:cert(?:iorari|\.)?\s*(?:was\s+)?(?:denied|den\.|granted|dismissed)|"
    r"(?:judgment\s+)?vacated(?:\s+and\s+remanded)?|vacated\s+in\s+part|rev'?d|reversed(?:\s+and\s+remanded)?|"
    r"aff'?d|affirmed|appeal\s+dismissed|GVR)\b", re.I)
SCREF = re.compile(
    r"(?P<cite>\b\d{1,3}\s+(?:U\.\s?S\.|S\.\s?Ct\.|L\.\s?Ed\.\s?(?:2d\s?)?)\s*\d{1,4}\b)|"
    r"(?P<dock>\bNos?\.\s*(?P<dn>\d{2}[-–]\d{1,5}[A-Z]?)\b)")
LOWDOCK = re.compile(r"\bNos?\.\s*(?P<d>[A-Z]{0,4}\d[\w\-–:./]{2,30})")
STOP_BACK = re.compile(r";|\.\s+(?=[A-Z])(?<!v\.\s)|\n\n")
SC_MARK = re.compile(r"\(\s*U\.\s?S\.|U\.\s?S\.|S\.\s?Ct\.|L\.\s?Ed\.|Supreme\s+Court", re.I)


def stage_list():
    by_repo = collections.defaultdict(list)
    with open(L.NODES, encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 6)
            if len(p) < 6:
                continue
            try:
                d = int(p[4])
            except ValueError:
                continue
            if d >= FROM:
                by_repo[p[1]].append((int(p[0]), p[2]))
    chunks = []
    for repo, items in sorted(by_repo.items()):
        items.sort()
        for i in range(0, len(items), CHUNK):
            chunks.append((repo, i // CHUNK, items[i:i + CHUNK]))
    pickle.dump(chunks, open(os.path.join(WORK, "scan_nodes.pkl"), "wb"), protocol=4)
    print("chunks", len(chunks), "nodes", sum(len(c[2]) for c in chunks))


def back_span(t, a):
    """Start of the citation clause that ends at a (previous ';' or sentence end, at most 320 chars back)."""
    lo = max(0, a - 320)
    seg = t[lo:a]
    last = None
    for m in re.finditer(r";|\n\n|(?<![A-Z])(?<!\b[A-Z][a-z])(?<!\bv)(?<!\bNo)(?<!\bCir)(?<!\bApp)(?<!\bCt)\.\s+(?=[A-Z])",
                         seg):
        last = m.end()
    return lo + (last or 0)


def scan_text(n, t):
    out = []
    for m in PHRASE.finditer(t):
        a, b = m.start(), m.end()
        # Supreme Court reference right after the phrase (same clause)
        fwd_end = min(len(t), b + 170)
        semi = t.find(";", b, fwd_end)
        if semi != -1:
            fwd_end = semi
        fwd = t[b:fwd_end]
        refs = []
        for r in SCREF.finditer(fwd):
            if r.start() > 90 and not refs:
                break
            if r.group("cite"):
                k = C.norm_cite(re.sub(r"(U\.\s?S\.|S\.\s?Ct\.|L\.\s?Ed\.\s?(?:2d\s?)?)", lambda z: " " + z.group(0) + " ",
                                       r.group("cite")))
                if k:
                    refs.append(("c", k, b + r.start(), b + r.end()))
            else:
                refs.append(("d", r.group("dn").replace("–", "-"), b + r.start(), b + r.end()))
        if not refs:
            continue
        s0 = back_span(t, a)
        pre = t[s0:a]
        cites = []
        for cm in C.CITE_RX.finditer(pre):
            k = C.cite_key(cm)
            if k:
                cites.append((k, s0 + cm.start(), s0 + cm.end()))
        docks = [(dm.group("d").replace("–", "-").rstrip(".,"), s0 + dm.start(), s0 + dm.end())
                 for dm in LOWDOCK.finditer(pre)]
        if not cites and not docks:
            continue
        out.append({"n": n, "p": [a, b], "ph": m.group(0), "s0": s0, "refs": refs, "cites": cites, "docks": docks,
                    "snip": L.norm(t[s0:fwd_end])[:700]})
    return out


def _scan_chunk(ch):
    repo, ci, items = ch
    path = os.path.join(OUTD, "%s.%03d.jsonl" % (repo, ci))
    if os.path.exists(path):
        return repo, ci, -1
    rd = os.path.join(L.REPOS, repo)
    inp = "".join("HEAD:%s\n" % p for _, p in items).encode("utf-8")
    res = subprocess.run(["git", "-C", rd, "cat-file", "--batch"], input=inp, capture_output=True,
                         creationflags=L.NOWIN).stdout
    pos = 0
    nrec = 0
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline=NL) as f:
        for n, _p in items:
            e = res.find(b"\n", pos)
            header = res[pos:e].split()
            if len(header) < 3 or header[1] != b"blob":
                pos = e + 1
                continue
            size = int(header[2])
            data = res[e + 1:e + 1 + size]
            pos = e + 1 + size + 1
            t = data.decode("utf-8", "replace").replace("\r\n", NL)
            if not SC_MARK.search(t):
                continue
            for r in scan_text(n, t):
                f.write(json.dumps(r, ensure_ascii=False) + NL)
                nrec += 1
    os.replace(tmp, path)
    return repo, ci, nrec


def stage_scan():
    os.makedirs(OUTD, exist_ok=True)
    chunks = pickle.load(open(os.path.join(WORK, "scan_nodes.pkl"), "rb"))
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    done = 0
    tot = 0
    for repo, ci, nrec in L.pmap(_scan_chunk, chunks, procs=procs):
        done += 1
        tot += max(nrec, 0)
        if done % 20 == 0:
            print(done, "/", len(chunks), "records", tot, flush=True)
    print("done", done, "records", tot)


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    {"list": stage_list, "scan": stage_scan}[sys.argv[1]]()
