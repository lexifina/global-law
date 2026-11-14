#!/usr/bin/env python3
"""Corpus side: federal appellate decisions by citation, and district / bankruptcy decisions by FJC district + docket.

Reads (read only): graph/nodes.tsv, graph/courts.tsv, round6/history/cache/<repo>*.meta.tsv.gz (docket field).
(Copied from benchmarks/fjc_idb_appeals/build_corpus.py; changed only to index appellate decisions by docket.)
Writes work/app_dk.tsv      repo, yy, num, node, date                 (repos ca1..ca11, cadc; one line per docket key)
       work/dist_nodes.tsv  node, repo, court_v1, fjc_ddist, kind (district|bankruptcy), date, name, docket_raw,
                            dockets (yy:num:type;... parsed), cites
       work/court_map.tsv   court_v1, name, fjc_ddist, kind (or unmapped)
"""
import collections
import gzip
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import benchlib  # noqa: E402

WORK = os.path.join(HERE, "work")
GRAPH = benchlib.GRAPH
CACHE = os.path.join(benchlib.ROOT, "round6", "history", "cache")
APP_REPOS = {"ca%d" % i for i in range(1, 12)} | {"cadc"}
DIST_REPOS = {"ca%d-district" % i for i in range(1, 12)} | {"cadc-district", "bankruptcy"}

# FJC district codes (Appeals Codebook 1971-2007, DDIST), keyed by (state, division word or "")
FJC = {
    ("Maine", ""): "00", ("Massachusetts", ""): "01", ("New Hampshire", ""): "02", ("Rhode Island", ""): "03",
    ("Puerto Rico", ""): "04", ("Connecticut", ""): "05", ("New York", "Northern"): "06", ("New York", "Eastern"): "07",
    ("New York", "Southern"): "08", ("New York", "Western"): "09", ("Vermont", ""): "10", ("Delaware", ""): "11",
    ("New Jersey", ""): "12", ("Pennsylvania", "Eastern"): "13", ("Pennsylvania", "Middle"): "14",
    ("Pennsylvania", "Western"): "15", ("Maryland", ""): "16", ("North Carolina", "Eastern"): "17",
    ("North Carolina", "Middle"): "18", ("North Carolina", "Western"): "19", ("South Carolina", ""): "20",
    ("Virginia", "Eastern"): "22", ("Virginia", "Western"): "23", ("West Virginia", "Northern"): "24",
    ("West Virginia", "Southern"): "25", ("Alabama", "Northern"): "26", ("Alabama", "Middle"): "27",
    ("Alabama", "Southern"): "28", ("Florida", "Northern"): "29", ("Florida", "Middle"): "3A",
    ("Florida", "Southern"): "3C", ("Georgia", "Northern"): "3E", ("Georgia", "Middle"): "3G",
    ("Georgia", "Southern"): "3J", ("Louisiana", "Eastern"): "3L", ("Louisiana", "Middle"): "3N",
    ("Louisiana", "Western"): "36", ("Mississippi", "Northern"): "37", ("Mississippi", "Southern"): "38",
    ("Texas", "Northern"): "39", ("Texas", "Eastern"): "40", ("Texas", "Southern"): "41", ("Texas", "Western"): "42",
    ("Kentucky", "Eastern"): "43", ("Kentucky", "Western"): "44", ("Michigan", "Eastern"): "45",
    ("Michigan", "Western"): "46", ("Ohio", "Northern"): "47", ("Ohio", "Southern"): "48",
    ("Tennessee", "Eastern"): "49", ("Tennessee", "Middle"): "50", ("Tennessee", "Western"): "51",
    ("Illinois", "Northern"): "52", ("Illinois", "Central"): "53", ("Illinois", "Southern"): "54",
    ("Indiana", "Northern"): "55", ("Indiana", "Southern"): "56", ("Wisconsin", "Eastern"): "57",
    ("Wisconsin", "Western"): "58", ("Arkansas", "Eastern"): "60", ("Arkansas", "Western"): "61",
    ("Iowa", "Northern"): "62", ("Iowa", "Southern"): "63", ("Minnesota", ""): "64", ("Missouri", "Eastern"): "65",
    ("Missouri", "Western"): "66", ("Nebraska", ""): "67", ("North Dakota", ""): "68", ("South Dakota", ""): "69",
    ("Alaska", ""): "7-", ("Arizona", ""): "70", ("California", "Northern"): "71", ("California", "Eastern"): "72",
    ("California", "Central"): "73", ("California", "Southern"): "74", ("Hawaii", ""): "75", ("Idaho", ""): "76",
    ("Montana", ""): "77", ("Nevada", ""): "78", ("Oregon", ""): "79", ("Washington", "Eastern"): "80",
    ("Washington", "Western"): "81", ("Colorado", ""): "82", ("Kansas", ""): "83", ("New Mexico", ""): "84",
    ("Oklahoma", "Northern"): "85", ("Oklahoma", "Eastern"): "86", ("Oklahoma", "Western"): "87", ("Utah", ""): "88",
    ("Wyoming", ""): "89", ("Columbia", ""): "90", ("Virgin Islands", ""): "91", ("the Virgin Islands", ""): "91",
    ("Canal Zone", ""): "92", ("Guam", ""): "93", ("Northern Mariana Islands", ""): "94",
    ("the Northern Mariana Islands", ""): "94", ("Wyoming", ""): "89",
}
CNAME = re.compile(r"^United States (District|Bankruptcy) Court for the (?:(Northern|Southern|Eastern|Western|Middle|Central) )?"
                   r"District of (.+?)\s*$")


CNAME2 = re.compile(r"^United States (District|Bankruptcy) Court, (?:([NSEWMC])\.\s?D\.|D\.)\s*(.+?)\s*$")
DIVW = {"N": "Northern", "S": "Southern", "E": "Eastern", "W": "Western", "M": "Middle", "C": "Central"}


def court_map():
    m = {}
    with open(os.path.join(GRAPH, "courts.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            nm = re.sub(r"^nited States", "United States", p[1]).replace("Sourthern", "Southern")
            r = CNAME.match(nm)
            if r:
                key, kind = (r.group(3), r.group(2) or ""), r.group(1)
            else:
                r = CNAME2.match(nm)
                if not r:
                    continue
                key, kind = (r.group(3), DIVW.get(r.group(2) or "", "")), r.group(1)
            code = FJC.get(key)
            if code:
                m[p[0]] = (p[1], code, "district" if kind == "District" else "bankruptcy")
    return m


# ---- docket parsing ---------------------------------------------------------------------------------------------
# a year-number pair: optional office "N:", optional 19/20 century, 2-digit year, then either letters (case type)
# or a hyphen, then the sequence number. "Civ. No. 15755" (no year) yields nothing.
DK = re.compile(r"(?<![\d.])(?:\d{1,2}:)?(?:19|20)?(\d{2})(?:\s*[-\s]\s*|\s*)(?:([A-Za-z]{1,5})\.?\s*[-\s]?\s*|-\s*)"
                r"(\d{1,6})(?![\d])")
DK_PLAIN = re.compile(r"(?<![\d.:])(?:19|20)?(\d{2})-(\d{1,6})(?![\d])")
CRIM = re.compile(r"\b(?:cr|crim|criminal|cri)\b", re.I)
CIV = re.compile(r"\b(?:cv|civ|civil|c|ca|cy)\b", re.I)
BK = re.compile(r"\b(?:bankr|bankruptcy|bk|adv|adversary|ap)\b", re.I)


def typ_of(letters, before):
    s = (letters or "").lower()
    if s:
        if s in ("cr", "crim", "cri", "r"):
            return "cr"
        if s in ("c", "cv", "civ", "ca", "cy", "ci"):
            return "cv"
        if s in ("bk", "b", "ap", "adv", "bkr"):
            return "bk"
        if s in ("mc", "m", "misc", "mj", "mag"):
            return "misc"
    # nearest label to the left
    seg = before[-40:]
    last = None
    for rx, t in ((CRIM, "cr"), (CIV, "cv"), (BK, "bk")):
        for mm in rx.finditer(seg):
            if last is None or mm.start() > last[0]:
                last = (mm.start(), t)
    return last[1] if last else "?"


def parse_dockets(s):
    out = []
    seen = set()
    for m in DK.finditer(s):
        yy, letters, num = m.group(1), m.group(2), m.group(3)
        if letters and letters.lower() in ("no", "nos"):
            continue
        t = typ_of(letters, s[:m.start()])
        key = (yy, int(num), t)
        if key not in seen:
            seen.add(key)
            out.append(key)
    for m in DK_PLAIN.finditer(s):
        yy, num = m.group(1), m.group(2)
        t = typ_of("", s[:m.start()])
        if not any(k[0] == yy and k[1] == int(num) for k in out):
            out.append((yy, int(num), t))
    return out


def norm_cite(c):
    m = re.match(r"^\s*(\d+)\s+(.+?)\s+(\d+)\s*$", c)
    if not m:
        return None
    rep = re.sub(r"[\s.,']", "", m.group(2)).lower().replace("2nd", "2d").replace("3rd", "3d")
    rep = re.sub(r"[()]", "", rep)
    return "%d %s %d" % (int(m.group(1)), rep, int(m.group(3)))


def main():
    os.makedirs(WORK, exist_ok=True)
    cm = court_map()
    with open(os.path.join(WORK, "court_map.tsv"), "w", encoding="utf-8", newline="\n") as o:
        for k, v in sorted(cm.items(), key=lambda x: int(x[0])):
            o.write("\t".join([k, v[0], v[1], v[2]]) + "\n")
    # dockets from the round-6 cache meta files
    dockets = {}
    for fn in sorted(os.listdir(CACHE)):
        if not fn.endswith(".meta.tsv.gz"):
            continue
        repo = fn.split(".")[0]
        if repo not in DIST_REPOS and repo not in APP_REPOS:
            continue
        with gzip.open(os.path.join(CACHE, fn), "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 9:
                    dockets[p[0]] = (p[5], p[8])
    st = collections.Counter()
    app = open(os.path.join(WORK, "app_dk.tsv"), "w", encoding="utf-8", newline="\n")
    dist = open(os.path.join(WORK, "dist_nodes.tsv"), "w", encoding="utf-8", newline="\n")
    with open(os.path.join(GRAPH, "nodes.tsv"), encoding="utf-8", newline="\n") as f:
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            if len(p) < 7:
                continue
            repo = p[1]
            if repo in APP_REPOS:
                raw = dockets.get(p[0], ("", ""))[0]
                pd = {(yy, num) for yy, num, t in parse_dockets(raw)}
                for yy, num in sorted(pd):
                    app.write("\t".join([repo, yy, str(num), p[0], p[4]]) + "\n")
                st["app_nodes"] += 1
                st["app_nodes_with_docket"] += int(bool(pd))
            elif repo in DIST_REPOS:
                st["dist_nodes"] += 1
                c = cm.get(p[3])
                if not c:
                    st["dist_unmapped_court"] += 1
                    continue
                if int(p[4] or 0) < 19650101:
                    st["dist_before_1965"] += 1
                    continue
                raw, parties = dockets.get(p[0], ("", ""))
                if not raw:
                    st["dist_no_docket"] += 1
                pd = parse_dockets(raw)
                if raw and not pd:
                    st["dist_docket_unparsed"] += 1
                if pd:
                    st["dist_docket_parsed"] += 1
                cites = ";".join(sorted({k for k in (norm_cite(x) for x in re.split(r"[|;]", p[5])) if k}))
                dist.write("\t".join([p[0], repo, p[3], c[1], c[2], p[4], p[6].replace("\t", " "),
                                      raw.replace("\t", " "),
                                      ";".join("%s:%d:%s" % k for k in pd), cites,
                                      parties.replace("\t", " ")[:600]]) + "\n")
    app.close()
    dist.close()
    print(dict(st))


if __name__ == "__main__":
    main()
