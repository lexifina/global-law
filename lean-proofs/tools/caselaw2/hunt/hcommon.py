"""Shared helpers for the precedent hunt (caselaw-lean-2/hunt).

Read-only over caselaw-lean-2/{data,out,gold}, graph/ and the decision repos (git objects at HEAD).
Writes only under caselaw-lean-2/hunt/.
"""
import os, re, sqlite3, subprocess, sys, json
from collections import defaultdict

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
CL2 = os.path.join(WORK, "caselaw-lean-2")
DATA = os.path.join(CL2, "data")
OUT = os.path.join(CL2, "out")
GOLD = os.path.join(CL2, "gold")
HUNT = os.path.join(CL2, "hunt")
HWORK = os.path.join(HUNT, "work")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
EDGES = os.path.join(WORK, "lean-in-v3")
DB = os.path.join(HWORK, "nodes.sqlite")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reader"))


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def build_db():
    """nodes(id, repo, path, court, date, cite, name), cites(cite, node), courts(id, name, ...), dec(node, court2,
    unit, bench, pub, form)."""
    os.makedirs(HWORK, exist_ok=True)
    tmp = DB + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    con = sqlite3.connect(tmp)
    con.execute("pragma journal_mode=off")
    con.execute("pragma synchronous=off")
    con.execute("create table nodes(id integer primary key, repo text, path text, court integer, date integer, "
                "cite text, name text)")
    def gen():
        with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                yield int(p[0]), p[1], p[2], int(p[3]), int(p[4] or 0), p[5], p[6]
    con.executemany("insert into nodes values (?,?,?,?,?,?,?)", gen())
    con.execute("create table cites(cite text, node integer)")
    def gen2():
        with open(os.path.join(WORK, "graph/cite_index.tsv"), encoding="utf-8") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 2 and p[1].lstrip("-").isdigit():
                    yield p[0], int(p[1])
    con.executemany("insert into cites values (?,?)", gen2())
    con.execute("create index cites_cite on cites(cite)")
    con.execute("create index cites_node on cites(node)")
    con.execute("create table dec(node integer primary key, court2 integer, unit integer, bench text, pub text, "
                "form text)")
    def gen3():
        with open(os.path.join(DATA, "decisions2.tsv"), encoding="utf-8") as f:
            for line in f:
                p = line.split("\t")
                yield int(p[0]), int(p[1]), int(p[3] or 0), p[4], p[5], p[6]
    con.executemany("insert into dec values (?,?,?,?,?,?)", gen3())
    con.execute("create table courts(id integer primary key, name text)")
    with open(os.path.join(WORK, "graph/courts.tsv"), encoding="utf-8") as f:
        con.executemany("insert into courts values (?,?)", ((int(l.split("\t")[0]), l.split("\t")[1]) for l in f))
    con.commit()
    con.close()
    os.replace(tmp, DB)


_con = None


def db():
    global _con
    if _con is None:
        if not os.path.exists(DB):
            log("building", DB)
            build_db()
        _con = sqlite3.connect(DB)
    return _con


def nodes(ids):
    """{id: dict(repo,path,court,date,cite,name,court2,unit,bench,pub,form,court_name)}"""
    ids = list({int(i) for i in ids})
    out = {}
    c = db()
    for k in range(0, len(ids), 900):
        chunk = ids[k:k + 900]
        q = ("select n.id,n.repo,n.path,n.court,n.date,n.cite,n.name,d.court2,d.unit,d.bench,d.pub,d.form,c.name "
             "from nodes n left join dec d on d.node=n.id left join courts c on c.id=n.court where n.id in (%s)"
             % ",".join("?" * len(chunk)))
        for r in c.execute(q, chunk):
            out[r[0]] = dict(id=r[0], repo=r[1], path=r[2], court=r[3], date=r[4], cite=r[5], name=r[6],
                             court2=r[7], unit=r[8], bench=r[9], pub=r[10], form=r[11], court_name=r[12])
    return out


def cites_of(node_ids):
    """{node: [compact cites]} from the graph cite index."""
    out = defaultdict(list)
    c = db()
    ids = list({int(i) for i in node_ids})
    for k in range(0, len(ids), 900):
        chunk = ids[k:k + 900]
        for cite, n in c.execute("select cite,node from cites where node in (%s)" % ",".join("?" * len(chunk)),
                                 chunk):
            out[n].append(cite)
    return out


def node_of_cite(compact):
    r = db().execute("select node from cites where cite=?", (compact,)).fetchall()
    return [x[0] for x in r]


def fetch(meta):
    """{node: meta} -> {node: text} (git HEAD objects; nothing written to disk)."""
    by = defaultdict(list)
    for n, m in meta.items():
        by[m["repo"]].append((n, m["path"]))
    out = {}
    for repo, items in by.items():
        for k in range(0, len(items), 400):
            part = items[k:k + 400]
            inp = "".join("HEAD:%s\n" % p for _, p in part).encode()
            res = subprocess.run(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], input=inp,
                                 capture_output=True).stdout
            i = 0
            for n, _ in part:
                nl = res.index(b"\n", i)
                hdr = res[i:nl].split()
                i = nl + 1
                if hdr[-1] == b"missing":
                    continue
                size = int(hdr[2])
                out[n] = res[i:i + size].decode("utf-8", "replace").replace("\r\n", "\n")
                i += size + 1
    return out


def body(text):
    """Strip YAML front matter."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            return text[end + 4:]
    return text


def front(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        return text[3:end] if end > 0 else ""
    return ""


# ---- locating a citation of a cited decision in the citing text ----------------------------------------------------

REPORTER_RX = re.compile(r"^(\d+)\s*([a-z0-9]+?)\s*(\d+)$")


def cite_patterns(compacts):
    """Compact cites ('541 us 558', '229 so2d 524') -> regexes tolerant of spacing and dots in the reporter."""
    pats = []
    for c in compacts:
        p = c.split()
        if len(p) < 3 or not p[0].isdigit() or not p[-1].isdigit():
            continue
        vol, page = p[0], p[-1]
        rep = "".join(p[1:-1])
        # reporter letters with optional dots/spaces between characters
        body_ = r"[\s.]*".join(re.escape(ch) for ch in rep)
        pats.append(re.compile(r"\b%s\s+%s\.?\s+%s\b" % (vol, body_, page), re.I))
    return pats


def name_tokens(name):
    """Distinctive tokens of a case name ('Bowers v. Hardwick' -> ['Bowers', 'Hardwick'])."""
    stop = {"v", "vs", "the", "of", "in", "re", "ex", "rel", "state", "united", "states", "people", "and", "et", "al",
            "inc", "co", "corp", "company", "city", "county", "commonwealth", "matter", "estate", "for", "a", "an",
            "llc", "ltd", "dept", "department", "board", "commissioner", "america", "parte", "on", "petition"}
    toks = re.findall(r"[A-Za-z][A-Za-z'\-]{2,}", name or "")
    return [t for t in toks if t.lower() not in stop][:3]


def locate(text, compacts, name, width=900):
    """Return [(start, end, window)] around each place the citing text cites the decision (by citation; by first name
    token followed by ', supra' or ' at '/' v.' as a fallback)."""
    hits = []
    for rx in cite_patterns(compacts):
        for m in rx.finditer(text):
            hits.append((m.start(), m.end()))
    if not hits:
        for t in name_tokens(name)[:1]:
            for m in re.finditer(r"\b%s\b" % re.escape(t), text):
                hits.append((m.start(), m.end()))
    hits.sort()
    merged = []
    for s, e in hits:
        if merged and s - merged[-1][1] < width:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    return [(s, e, text[max(0, s - width):e + width]) for s, e in merged]


def read_tsv(path, header=True):
    with open(path, encoding="utf-8") as f:
        if header:
            f.readline()
        for line in f:
            yield line.rstrip("\n").split("\t")


def write_tsv(path, rows, header=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        if header:
            f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in r) + "\n")


def iter_edges(want_cited=None, want_citing=None):
    """Stream (citing, cited) from lean-in-v3/edges-*.tsv, filtered by cited and/or citing node sets."""
    import glob
    for fn in sorted(glob.glob(os.path.join(EDGES, "edges-*.tsv"))):
        with open(fn, encoding="utf-8") as f:
            for line in f:
                a, _, b = line.rstrip("\n").partition("\t")
                b = b.split("\t", 1)[0]
                if not b:
                    continue
                if want_cited is not None and int(b) not in want_cited:
                    continue
                if want_citing is not None and int(a) not in want_citing:
                    continue
                yield int(a), int(b)


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (p, max(0.0, c - h), min(1.0, c + h))
