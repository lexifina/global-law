"""Gold for split detection: Supreme Court decisions since 1995 that say they granted certiorari to resolve a
conflict among the courts of appeals, with the US Code subsection at issue and the circuits (and their decisions)
named.

    python tools/caselaw2/eval/splits_build.py

Reads the supreme-court repo at HEAD (git cat-file --batch) for every SCOTUS node dated 1995-01-01 or later that is
not a memorandum order, plus gold/scdb.tsv (certReason, basis). Writes gold/splits_resolved.tsv (header line, LF):

  node, date, name, scdb_certReason, scdb_basis, usc (title:section(sub) primary), usc_all, circuits, conflict_nodes,
  statutory (1 when a US Code section is the subject), quote, offset, src
"""
import collections, os, re, subprocess, sys, threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gold_build as gb  # noqa: E402

REPO = os.path.expanduser("~/Documents/us-caselaw-repos/supreme-court")
CNW = 0x08000000
CONFLICT = re.compile(
    r"(?:grant(?:ed)?\s+(?:certiorari|cert\.|review|the\s+petition)[^.]{0,160}?|"
    r"(?:to|in\s+order\s+to)\s+)"
    r"(?:resolve|settle|address|consider|decide|eliminate)\s+(?:an?\s+|the\s+|this\s+)?"
    r"(?:(?:\w+[-\s]){0,3})?(?:conflict|split|disagreement|division|disarray|tension)s?\b"
    r"|grant(?:ed)?\s+certiorari[^.]{0,40}?(?:because|in\s+light\s+of|in\s+view\s+of|due\s+to|given)\s+(?:of\s+)?"
    r"(?:an?\s+|the\s+)?(?:(?:\w+[-\s]){0,3})?(?:conflict|split|disagreement|division)"
    r"|grant(?:ed)?\s+certiorari[^.]{0,40}?because\s+(?:the\s+)?(?:federal\s+)?(?:courts\s+of\s+appeals|circuits)\s+"
    r"(?:are|were|have|had)\s+(?:\w+\s+)?(?:divided|split|disagreed|reached\s+(?:conflicting|different))"
    r"|(?:conflict|split|disagreement|division)s?\s+(?:among|between|in)\s+(?:the\s+)?(?:federal\s+)?"
    r"(?:courts?\s+of\s+appeals|circuits|lower\s+(?:federal\s+)?courts)[^.]{0,120}?(?:we\s+granted|granted\s+certiorari)",
    re.I)
NOT_CIRC = re.compile(r"state\s+(?:high\s+)?courts|state\s+supreme\s+courts|state\s+courts", re.I)
USC = re.compile(r"(\d{1,2})\s+U\.\s?S\.\s?C\.(?:\s?A\.)?\s*(?:§§?|sec(?:tion)?s?\.?)\s*(\d+[a-zA-Z\-]*\d*[a-z]?)"
                 r"((?:\s?\([a-zA-Z0-9]{1,6}\))*)")
ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8,
       "ninth": 9, "tenth": 10, "eleventh": 11, "federal": 13, "district of columbia": 12, "d. c.": 12, "d.c.": 12}
CIRC = re.compile(r"\bCA(\d{1,2}|DC|Fed)\b|\((\d{1,2})(?:st|nd|rd|th)\s+Cir\.|\b(First|Second|Third|Fourth|Fifth|Sixth|"
                  r"Seventh|Eighth|Ninth|Tenth|Eleventh|Federal|District of Columbia|D\. ?C\.)\s+Circuit|"
                  r"\((D\. ?C\.|Fed\.)\s+Cir\.")
FCITE = re.compile(r"\b(\d{1,4})\s+(F\.\s?(?:2d|3d|4th)|F\.\s?App(?:'|’)x|F\.\s?Supp\.(?:\s?(?:2d|3d))?)\s+(\d{1,5})")


def circuits(t):
    out = []
    for m in CIRC.finditer(t):
        g = m.group(1) or m.group(2) or m.group(3) or m.group(4)
        g = g.strip()
        if g.isdigit():
            c = int(g)
        elif g in ("DC",):
            c = 12
        elif g in ("Fed",):
            c = 13
        else:
            c = ORD.get(g.lower().replace("fed.", "federal"), ORD.get(g.lower(), 0))
        if 1 <= c <= 13 and c not in out:
            out.append(c)
    return sorted(out)


def main():
    G = gb.G
    scdb = {}
    for i, line in enumerate(open(os.path.join(G, "scdb.tsv"), encoding="utf-8")):
        f = line.rstrip("\n").split("\t")
        if i and f[0] != "-1":
            scdb[int(f[0])] = (f[11], f[20])
    conflict_set = {n for n, (c, b) in scdb.items() if c in ("federalCourtConflict", "putativeConflict",
                                                            "federalCourtConflictAndImportantQuestion")}
    items = []
    for line in open(os.path.join(G, "work", "scotus_nodes.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if int(f[4]) >= 19950101 and (len(f) < 8 or f[7] != "memorandum order"):
            items.append((int(f[0]), f[2], int(f[4]), f[6]))
    shas = {}
    tree = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "HEAD", "--", "decisions"], capture_output=True,
                          check=True, creationflags=CNW).stdout.decode("utf-8")
    for line in tree.splitlines():
        meta, path = line.split("\t", 1)
        shas[path] = meta.split()[2]
    items = [it for it in items if it[1] in shas]
    p = subprocess.Popen(["git", "-C", REPO, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         creationflags=CNW)

    def feed():
        for it in items:
            p.stdin.write((shas[it[1]] + "\n").encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    cols = ["node", "date", "name", "scdb_certReason", "scdb_basis", "usc", "usc_all", "circuits", "conflict_nodes",
            "statutory", "quote", "offset", "src"]
    rows = []
    for node, path, date, name in items:
        header = p.stdout.readline().split()
        data = p.stdout.read(int(header[2]))
        p.stdout.read(1)
        body = gb_body(data.decode("utf-8", "replace").replace("\r\n", "\n"))
        if not re.search(r"conflict|split|disagree|division", body, re.I) and node not in conflict_set:
            continue
        # majority part only: stop at the first separate opinion header
        maj = re.split(r"^## (?:Dissent|Concurr)", body, maxsplit=1, flags=re.M)[0]
        m = None
        for mm in CONFLICT.finditer(maj):
            ctx = maj[max(0, mm.start() - 200):mm.end() + 150]
            if NOT_CIRC.search(ctx) and not re.search(r"courts?\s+of\s+appeals|circuit", ctx, re.I):
                continue
            m = mm
            break
        if m is None and node not in conflict_set:
            continue
        if m is None:
            s0, s1, quote, src, off = 0, 0, "-", "scdb:certReason", -1
            win = maj[:4000]
        else:
            g = max(maj.rfind("We granted", max(0, m.start() - 400), m.start() + 1),
                    maj.rfind("we granted", max(0, m.start() - 400), m.start() + 1))
            s0 = g if g >= 0 else max(maj.rfind(". ", 0, m.start()), maj.rfind("\n", 0, m.start())) + 1
            s1 = maj.find(". ", m.end())
            s1 = len(maj) if s1 < 0 else s1 + 1
            quote = re.sub(r"\s+", " ", maj[s0:s1]).strip()[:600]
            win = maj[max(0, s0 - 1500):s1 + 2500]
            src, off = "opinionText:conflictLanguage" + ("+scdb:certReason" if node in conflict_set else ""), m.start()
        head = maj[:12000]
        cnt = collections.Counter()
        for u in USC.finditer(head):
            cnt[f"{u.group(1)}:{u.group(2)}{re.sub(r'\s', '', u.group(3))}"] += 1
        for u in USC.finditer(win):
            cnt[f"{u.group(1)}:{u.group(2)}{re.sub(r'\s', '', u.group(3))}"] += 3
        # the primary section: most weight; collapse to the section when subsections disagree
        usc = cnt.most_common(1)[0][0] if cnt else "-"
        nodes = []
        for c in FCITE.finditer(win):
            j = gb.node_of_cite(f"{c.group(1)} {c.group(2)} {c.group(3)}")
            if j is not None and j not in nodes:
                nodes.append(j)
        cert, basis = scdb.get(node, ("-", "-"))
        stat = 1 if usc != "-" else 0
        rows.append([node, date, name, cert, basis, usc, "|".join(k for k, _ in cnt.most_common(6)) or "-",
                     ",".join(map(str, circuits(win))) or "-", ",".join(map(str, nodes)) or "-", stat, quote,
                     off, src])
    p.wait()
    # one row per decision (parallel copies of the same decision share date and name)
    seen, out = set(), []
    for r in rows:
        k = (r[1], gb.toks(r[2]).__len__() and frozenset(gb.toks(r[2])))
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    with open(os.path.join(G, "splits_resolved.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for r in out:
            o.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")
    st = collections.Counter((r[9], r[7] != "-") for r in out)
    print(f"candidates {len(items)}, decisions with conflict language {len(out)}; statutory/circuits {dict(st)}")


def gb_body(text):
    if text.startswith("---"):
        e = text.find("\n---", 3)
        if e >= 0:
            return text[e + 4:]
    return text


if __name__ == "__main__":
    main()
