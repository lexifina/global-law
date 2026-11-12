"""One pass over every version of every US Code section in usc-full.git.

    python extract.py

Writes, next to this script:
  vstats.tsv   one row per versions.tsv row: row index, words, section references
  credit.tsv   words of today's Code by who inserted them (pre / edition / Congress number)
  credit_law.tsv  words of today's Code by law
  events.tsv   (path, sub, year, law) top-level blocks a law rewrote, 1998-2018
  shingles.tsv hash of the first 30 words of each inserted run of >= 30 words, with law and path

Words are whitespace tokens of the normalised text (usc_encode.norm), without markdown list markers.
Blame: each version is diffed against the one before it, first by line, then by word inside changed lines; inserted
words are credited to the version's law (its Congress), to "pre" for text in the 1994 or an earlier edition (or a law of
the 103rd Congress or earlier), and to "edition" for words first seen in a later edition commit (no law identified).
"""
import collections, difflib, hashlib, os, re, subprocess, sys
from multiprocessing import Pool

sys.path.insert(0, r"C:\Users\alany\Documents\global-law-lean\lean-proofs\tools\caselaw")
from usc_encode import norm, blocks  # noqa: E402

HOME = os.path.expanduser("~/Documents/us-caselaw-lean-work")
GIT = os.path.join(HOME, "usc-full.git")
VERS = os.path.join(HOME, "usc", "versions.tsv")
OUT = os.path.dirname(os.path.abspath(__file__))
NUM = r"\d[\w\-–]*(?:\.\d+)?(?:\([^)\s]*\))*"
XREF = re.compile(r"\bsections? (" + NUM + r"(?:,? (?:and |or |through |to )?" + NUM + r")*)", re.I)
ITEM = re.compile(NUM)


def xrefs(text):
    """references to numbered sections: "section 922(g)", and each number of "sections 1395f(d), 1395f(f), and 1395g"."""
    return sum(len(ITEM.findall(m.group(1))) for m in XREF.finditer(text))
_pr = None


def blob(b):
    global _pr
    if not b:
        return ""
    if _pr is None:
        _pr = subprocess.Popen(["git", "--git-dir", GIT, "cat-file", "--batch"], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    _pr.stdin.write((b + "\n").encode()); _pr.stdin.flush()
    size = int(_pr.stdout.readline().split()[2])
    t = _pr.stdout.read(size).decode("utf-8", "replace"); _pr.stdout.read(1)
    return t


def lines_tokens(text):
    out = []
    for ln in text.split("\n"):
        toks = [w for w in norm(ln).split() if w not in ("-", "#")]
        if toks:
            out.append(toks)
    return out


LATE = {"title-7", "title-28", "title-39"}  # the record starts these titles with the 1995 edition


def who(kind, label, title=""):
    if kind == "law":
        c = int(re.match(r"Pub\. L\. (\d+)-", label).group(1))
        return str(c) if c >= 104 else "pre"
    m = re.match(r"(\d{4}) edition", label)
    if title in LATE and label.startswith("1995 edition"):
        return "pre"
    if label.startswith("US Code release") or (m and int(m.group(1)) >= 1995):
        return "edition"
    return "pre"


def blame(prev_lines, prev_cred, new_lines, cred):
    """prev_lines: list of token lists; prev_cred: parallel list of credit lists. Returns new credit lists."""
    a = [" ".join(t) for t in prev_lines]
    b = [" ".join(t) for t in new_lines]
    out = [None] * len(new_lines)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            for k in range(j2 - j1):
                out[j1 + k] = prev_cred[i1 + k]
        elif op == "insert":
            for k in range(j1, j2):
                out[k] = [cred] * len(new_lines[k])
        elif op == "replace":
            ot = [w for t in prev_lines[i1:i2] for w in t]
            oc = [c for cs in prev_cred[i1:i2] for c in cs]
            nt = [w for t in new_lines[j1:j2] for w in t]
            nc = [cred] * len(nt)
            if len(ot) * len(nt) < 4e8:
                for op2, p1, p2, q1, q2 in difflib.SequenceMatcher(None, ot, nt, autojunk=False).get_opcodes():
                    if op2 == "equal":
                        nc[q1:q2] = oc[p1:p2]
            pos = 0
            for k in range(j1, j2):
                n = len(new_lines[k]); out[k] = nc[pos:pos + n]; pos += n
    return out


def inserted_runs(cred_lines, label_cred, new_lines):
    """Runs of >= 30 consecutive words credited to label_cred in the new version."""
    toks = [w for t in new_lines for w in t]
    cs = [c for cl in cred_lines for c in cl]
    runs, start = [], None
    for i, c in enumerate(cs + [None]):
        if c == label_cred and start is None:
            start = i
        elif c != label_cred and start is not None:
            if i - start >= 30:
                runs.append(" ".join(toks[start:start + 30]))
            start = None
    return runs


def work(item):
    path, vs = item  # vs: [(row, day, kind, label, blob)]
    stats, ev, sh = [], [], []
    prev_lines, prev_cred, prev_text = [], [], ""
    for row, day, kind, label, b in vs:
        text = blob(b)
        nl = lines_tokens(text)
        stats.append((row, sum(len(t) for t in nl), xrefs(text)))
        c = label if kind == "law" else who(kind, label, path.split("/")[0])
        cl = blame(prev_lines, prev_cred, nl, c)
        if kind == "law":
            for r in inserted_runs(cl, c, nl):
                sh.append((hashlib.sha1(r.encode()).hexdigest()[:16], label, path))
            y = day // 10000
            if 1998 <= y <= 2018 and prev_text and text:
                pb, nb = blocks(prev_text), blocks(text)
                for s, t in nb.items():
                    if s in pb and norm(pb[s]) != norm(t):
                        ev.append((path, s, y, label))
        prev_lines, prev_cred, prev_text = nl, cl, text
    credit = collections.Counter(c for cl in prev_cred for c in cl)
    return path, stats, credit, ev, sh


def main():
    vers = collections.defaultdict(list)
    for i, l in enumerate(open(VERS, encoding="utf-8")):
        f = l.rstrip("\n").split("\t")
        vers[f[0]].append((i, int(f[4]), f[2], f[3], f[5]))
    for p in vers:
        vers[p].sort(key=lambda v: (v[1], v[0]))
    items = sorted(vers.items(), key=lambda kv: -len(kv[1]))
    stats, credit_law, ev, sh = [], collections.Counter(), [], []
    with Pool(6) as pool:
        for n, (path, st, cr, e, s) in enumerate(pool.imap_unordered(work, items, chunksize=8)):
            stats += st; credit_law.update(cr); ev += e; sh += s
            if n % 5000 == 0:
                print(n, len(items), flush=True)
    stats.sort()
    with open(os.path.join(OUT, "vstats.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for r in stats:
            f.write("\t".join(map(str, r)) + "\n")
    credit = collections.Counter()
    for k, v in credit_law.items():
        credit[re.match(r"Pub\. L\. (\d+)-", k).group(1) if k.startswith("Pub. L.") else k] += v
    for k in list(credit):
        if k.isdigit() and int(k) < 104:
            credit["pre"] += credit.pop(k)
    with open(os.path.join(OUT, "credit.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for k, v in sorted(credit.items(), key=lambda kv: (not kv[0].isdigit(), kv[0])):
            f.write(f"{k}\t{v}\n")
    with open(os.path.join(OUT, "credit_law.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for k, v in credit_law.most_common():
            f.write(f"{k}\t{v}\n")
    with open(os.path.join(OUT, "events.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for r in sorted(set(ev)):
            f.write("\t".join(map(str, r)) + "\n")
    with open(os.path.join(OUT, "shingles.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for r in sh:
            f.write("\t".join(r) + "\n")
    print("done", len(stats), sum(credit.values()))


if __name__ == "__main__":
    main()
