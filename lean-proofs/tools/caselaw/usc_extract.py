"""Every US Code section that each decision since the record starts cites, read from the full text of all US case law.

    python tools/caselaw/usc_extract.py <repos-dir> <nodes.tsv> <versions.tsv> <out-dir> [--from 19950104] [-j 20]

The citations are read by usc_cite.py, the same reader as global-law's judgment overlays (short forms "42 U.S.C. §
1983(a)", lists, "U.S.C.A.", and the long forms "section 1334 of title 28"). Only single sections are kept (a range's
ends are not a citation of every section between them), only sections the US Code record holds, and not a citation
the reader marks as an older numbering (an edition before the title's recodification, "former", or a decision before
the section's first version in the record).

Writes <out-dir>/<repo>.usc.tsv: node id, decided (yyyymmdd), title, section, first subsection cited ('' if none),
mentions, an example of the words.
"""
import collections, os, re, subprocess, sys, threading
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import usc_cite  # noqa: E402

FIRST = {}      # (title, section) -> first version day (yyyymmdd)
NODES = {}      # repo -> {path: (id, decided)}
SUBX = re.compile(r"\s?\(([a-zA-Z]{1,6}|\d{1,2})\)")
HINT = re.compile(r"U\s?\.?\s?S\s?\.?\s?C|United\s+States\s+Code|of\s+[Tt]itle\s+\d", re.S)
# Titles recodified (enacted as positive law with new numbering) after the record starts: a decision before the day
# cites the old numbering.
RECODIFIED_LATE = {36: 19980812, 40: 20020821, 41: 20110104, 46: 20061006, 51: 20101218, 54: 20141219}


def exists(t, s):
    return (t, s) in FIRST


def work(args):
    repo, out, want = args
    name = os.path.basename(repo)
    if not want:
        return name, 0, 0
    tree = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "HEAD", "--", "decisions"], capture_output=True).stdout.decode("utf-8")
    items = []
    for line in tree.splitlines():
        meta, path = line.split("\t", 1)
        if path in want:
            items.append((meta.split()[2], path))
    p = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def feed():
        for sha, _ in items:
            p.stdin.write((sha + "\n").encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    rows = 0
    with open(os.path.join(out, name + ".usc.tsv.part"), "w", encoding="utf-8", newline="\n") as fo:
        for sha, path in items:
            size = int(p.stdout.readline().split()[2])
            text = p.stdout.read(size).decode("utf-8", "replace")
            p.stdout.read(1)
            if not HINT.search(text):
                continue
            nid, decided = want[path]
            ds = f"{str(decided)[:4]}-{str(decided)[4:6]}-{str(decided)[6:8]}"
            body = text[text.find("\n---", 3) + 4:] if text.startswith("---") else text
            agg = collections.OrderedDict()
            for c in usc_cite.cites(body, exists, long_forms=True):
                if c["role"] != "cited":
                    continue
                t, s = c["title"], c["section"]
                if (t, s) not in FIRST:
                    continue
                late = RECODIFIED_LATE.get(t)
                if late and decided < late:
                    continue
                if usc_cite.old_numbering(c, ds, None, None):
                    continue
                if decided < FIRST[(t, s)]:
                    continue
                m = SUBX.match(body, c["at"] + len(s))
                sub = m.group(1) if m else ""
                k = (t, s)
                if k not in agg:
                    agg[k] = [sub, 0, c["how"][:120]]
                elif not agg[k][0] and sub:
                    agg[k][0] = sub
                agg[k][1] += 1
            for (t, s), (sub, nm, how) in agg.items():
                fo.write(f"{nid}\t{decided}\t{t}\t{s}\t{sub}\t{nm}\t{how.replace(chr(9), ' ')}\n")
                rows += 1
    p.wait()
    os.replace(os.path.join(out, name + ".usc.tsv.part"), os.path.join(out, name + ".usc.tsv"))
    return name, len(items), rows


def init(versions):
    for l in open(versions, encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        m = re.match(r"title-(\d+)/(.+)\.md$", f[0])
        if not m or not f[5]:
            continue
        k = (int(m.group(1)), m.group(2))
        d = int(f[4])
        if k not in FIRST or d < FIRST[k]:
            FIRST[k] = d


def load_nodes(nodes, since):
    for l in open(nodes, encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        d = int(f[4] or 0)
        if d >= since:
            NODES.setdefault(f[1], {})[f[2]] = (int(f[0]), d)


def main():
    a = sys.argv[1:]
    since, j = 19950104, 20
    if "--from" in a:
        i = a.index("--from"); since = int(a[i + 1]); del a[i:i + 2]
    if "-j" in a:
        i = a.index("-j"); j = int(a[i + 1]); del a[i:i + 2]
    repos, nodes, versions, out = a
    os.makedirs(out, exist_ok=True)
    init(versions)
    load_nodes(nodes, since)
    todo = sorted((os.path.join(repos, r) for r in os.listdir(repos) if r in NODES and not os.path.exists(os.path.join(out, r + ".usc.tsv"))),
                  key=lambda r: -len(NODES[os.path.basename(r)]))
    print("sections", len(FIRST), "repos", len(todo), "decisions", sum(len(v) for v in NODES.values()), flush=True)
    with Pool(j, initializer=init, initargs=(versions,)) as pool:
        for name, n, rows in pool.imap_unordered(work, [(r, out, NODES[os.path.basename(r)]) for r in todo]):
            print(name, n, rows, flush=True)


if __name__ == "__main__":
    main()
