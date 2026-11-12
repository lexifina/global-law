"""Lean input for the statute check over the whole US Code: every (decision, section) a decision since the record
starts cites, with the section's versions (day, made by a law or an edition, words of the section, words of the cited
subsection).

    python tools/caselaw/usc_encode.py <usc git dir> <versions.tsv> <cites dir> <out dir>

Writes <out>/rows.tsv (row id, node id, decided, title, section, subsection, mentions) and <out>/lean_in.tsv (row id,
decided, versions as day,law,text,sub). Words are compared after folding whitespace and typography (quotation marks,
dashes), so a reprint is not a change. A subsection is the block of the section that starts with its designation (see
`blocks`); where no version of the section has a top-level
block with that designation, the whole section's words stand in for it.
"""
import collections, glob, hashlib, os, re, subprocess, sys, threading

DES = re.compile(r"^( *)-\s+\[?\(([A-Za-z0-9]+)\)(\()?", re.M)
FOLD = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-", " ": " "})


def norm(s):
    return re.sub(r"\s+", " ", s.translate(FOLD)).strip()


def _kind(d):
    return "d" if d[0].isdigit() else ("l" if d.islower() else "u")


def _key(d):
    if d[0].isdigit():
        m = re.match(r"(\d+)(.*)", d)
        return (int(m.group(1)), m.group(2))
    return (len(d), d)


def blocks(text):
    """Subsection designation -> its block of text. Subsections are the designations of the section's first kind
    (letters, or numbers for sections such as definitions) that follow each other in order: a line starts the next
    subsection when its first designation comes after the current one (allowing a few skipped, repealed ones) and it
    is printed at the section's shallowest designated indent or combined with its first paragraph's designation
    ("(c)(1)(A) ...", which the record prints at the depth of its last designation). Each runs to the next."""
    ms = list(DES.finditer(text))
    if not ms:
        return {}
    top = min(len(m.group(1)) for m in ms)
    k0 = _kind(ms[0].group(2))
    starts, cur = [], None
    for m in ms:
        d = m.group(2)
        if _kind(d) != k0 or not (len(m.group(1)) == top or m.group(3)):
            continue
        k = _key(d)
        if cur is not None:
            if k <= cur:
                continue
            if k0 == "l" and len(d) == len(cur[1]) == 1 and ord(d) - ord(cur[1]) > 4:
                continue
            if k0 == "l" and len(d) > 1:
                # after "z" come "aa", "bb", ...; "ii" or "iii" anywhere else is a clause
                if d != d[0] * len(d):
                    continue
                c = cur[1]
                nxt = ("a" * (len(c) + 1)) if c[0] >= "x" else (chr(ord(c[0]) + 1) * len(c))
                if len(d) != len(nxt) or not (0 <= ord(d[0]) - ord(nxt[0]) <= 3):
                    continue
        starts.append(m); cur = k
    out = {}
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        out.setdefault(m.group(2), text[m.start():end])
    return out


def main(git, versions, cites, out):
    os.makedirs(out, exist_ok=True)
    vers = collections.defaultdict(list)  # path -> [(day, law, blob, order)]
    for i, l in enumerate(open(versions, encoding="utf-8")):
        f = l.rstrip("\n").split("\t")
        vers[f[0]].append((int(f[4]), 1 if f[2] == "law" else 0, f[5], i))
    for p in vers:
        vers[p].sort(key=lambda v: (v[0], v[3]))
    rows = []
    want = collections.defaultdict(set)  # path -> subsections cited
    for fn in sorted(glob.glob(os.path.join(cites, "*.usc.tsv"))):
        for l in open(fn, encoding="utf-8"):
            f = l.rstrip("\n").split("\t")
            nid, d, t, s, sub, nm = int(f[0]), int(f[1]), f[2], f[3], f[4], int(f[5])
            path = f"title-{t}/{s}.md"
            if path not in vers:
                continue
            rows.append((nid, d, t, s, sub, nm))
            want[path].add(sub)
    print("rows", len(rows), "sections", len(want), flush=True)
    # read every version of every cited section once
    blobs = sorted({v[2] for p in want for v in vers[p] if v[2]})
    text = {}
    pr = subprocess.Popen(["git", "--git-dir", git, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def feed():
        for b in blobs:
            pr.stdin.write((b + "\n").encode())
        pr.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    for b in blobs:
        size = int(pr.stdout.readline().split()[2])
        text[b] = pr.stdout.read(size).decode("utf-8", "replace")
        pr.stdout.read(1)
    pr.wait()
    print("blobs", len(text), flush=True)
    ids = {}

    def tid(s):
        h = hashlib.sha1(s.encode()).digest()
        return ids.setdefault(h, len(ids) + 1)
    vstr = {}  # (path, sub) -> "day,law,text,sub;..." list
    for path, subs in want.items():
        vs = vers[path]
        bl = [blocks(text[v[2]]) if v[2] else {} for v in vs]
        whole = [tid(norm(text[v[2]])) if v[2] else 0 for v in vs]
        for sub in subs:
            has = sub and any(sub in b for b in bl)
            parts = []
            for k, v in enumerate(vs):
                sid = (tid(norm(bl[k].get(sub, ""))) if v[2] else 0) if has else whole[k]
                parts.append(f"{v[0]},{v[1]},{whole[k]},{sid}")
            vstr[(path, sub)] = parts
    with open(os.path.join(out, "rows.tsv"), "w", encoding="utf-8", newline="\n") as fr, \
         open(os.path.join(out, "lean_in.tsv"), "w", encoding="utf-8", newline="\n") as fl:
        for i, (nid, d, t, s, sub, nm) in enumerate(rows):
            path = f"title-{t}/{s}.md"
            fr.write(f"{i}\t{nid}\t{d}\t{t}\t{s}\t{sub}\t{nm}\n")
            fl.write(f"{i}\t{d}\t" + "\t".join(vstr[(path, sub)]) + "\n")
    print("written", len(rows))


if __name__ == "__main__":
    main(*sys.argv[1:])
