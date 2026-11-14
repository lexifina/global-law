"""diag2 step 3: candidate later statements "X was overruled by Y" in later Supreme Court opinions.

For every pair (Y, X) of pairs.tsv: every later Supreme Court decision W (date > date(Y)) that cites X or Y
(files from dsearch.py grep + dsearch_y.py grep), every paragraph with an overruling word (overrul / abrogat /
disapprov) and
  both : a reference to X and a reference to Y with the cue inside one span of <= 400 characters;
  weakx: a reference to X within 200 characters of the cue, no Y in reach;
  weaky: (only when Y's citation is in the paragraph) Y within the dsearch_y form distance of the cue, no X.
A reference = the U.S. / nominative citation, or a party-name token (name_tokens of the corpus name and the key name).

    python later.py        writes later_cands.tsv and caches the W texts (text/<W>.md, nodes_meta.tsv)
"""
import csv
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dsearch as D  # noqa: E402
import prep2 as P  # noqa: E402

RC = D.RC
CUE = re.compile(r"overrul|abrogat|disapprov|over-\s?rul", re.I)
MAXSPAN = 400


GEN = re.compile(r"(\d{1,3}) (U\. ?S\.|Dall\.?|Cranch|Wheat\.?|Pet\.?|How\.?|Black|Wall\.?|S\. ?Ct\.),? (\d{1,4})(?=[^0-9]|$)")


def _rep(r):
    r = r.replace(" ", "").rstrip(".")
    return {"U.S": "US", "S.Ct": "SCt"}.get(r, r)


def cite_keys(view):
    """Every reporter citation in a text as (volume, reporter, page) keys."""
    return {(m.group(1), _rep(m.group(2)), m.group(3)) for m in GEN.finditer(view)}


def keys_of(cites):
    out = set()
    for c in cites.split("|"):
        m = re.match(r"^(\d+) (U\.S\.|Dall\.|Cranch|Wheat\.|Pet\.|How\.|Black|Wall\.|S\. Ct\.) (\d+)$", c)
        if m:
            out.add((m.group(1), _rep(m.group(2)), m.group(3)))
    return out


def refs_of(cre, nre, line):
    out = [(m.start(), m.end(), "cite") for m in cre.finditer(line)]
    if nre:
        out += [(m.start(), m.end(), "name") for m in nre.finditer(line)]
    return out


def widen(line, a, b):
    """Grow [a, b) to sentence-ish boundaries while it stays <= MAXSPAN; else to word boundaries."""
    a0, b0 = a, b
    # left: back to the previous sentence end
    i = a
    while i > 0 and a0 - i < 260:
        if line[i - 1] in ".;?!" and line[i:i + 1] == " " and i + 1 < len(line) and (line[i + 1].isupper() or line[i + 1] in "“\"("):
            # do not stop on "v." / "U." / "S." / single capital abbreviations
            w = re.search(r"([A-Za-z]+)\.$", line[max(0, i - 8):i])
            if not (w and (len(w.group(1)) <= 2 or w.group(1) in RC.ABBR or w.group(1) in ("Wall", "How", "Pet", "Wheat", "Cranch", "Dall", "Ct", "Ed"))):
                break
        i -= 1
    la = i + 1 if i > 0 else 0
    j = b
    while j < len(line) and j - b0 < 260:
        if line[j] in ".;?!" and (j + 1 >= len(line) or (line[j + 1] == " " and j + 2 < len(line) and (line[j + 2].isupper() or line[j + 2] in "“\"("))):
            w = re.search(r"([A-Za-z]+)$", line[max(0, j - 8):j])
            if not (w and (len(w.group(1)) <= 2 or w.group(1) in RC.ABBR or w.group(1) in ("Wall", "How", "Pet", "Wheat", "Cranch", "Dall", "Ct", "Ed"))):
                j += 1
                break
        j += 1
    lb = min(j, len(line))
    if lb - la <= MAXSPAN:
        return la, lb
    if lb - a0 <= MAXSPAN:
        return a0 - 0, lb
    if b0 - la <= MAXSPAN:
        return la, b0
    # word boundaries
    while a0 > 0 and line[a0 - 1] not in " \n":
        a0 -= 1
    while b0 < len(line) and line[b0] not in " \n":
        b0 += 1
    return a0, b0


def main():
    with open(os.path.join(HERE, "pairs.tsv"), encoding="utf-8", newline="") as f:
        pairs = list(csv.DictReader(f, delimiter="\t"))
    meta = D.load_meta()
    files = set()
    for fn in ("dsearch_files.tsv", "dsearch_y_files.tsv"):
        with open(os.path.join(HERE, fn), encoding="utf-8") as f:
            files |= {l.strip() for l in f if l.strip()}
    node = {}
    with open(os.path.join(D.W, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 7)
            if p[1] == "supreme-court" and p[2] in files:
                node[p[2]] = (p[0], p[4], p[6])
    paths = sorted(node)
    pats = []
    for pr in pairs:
        y, x = pr["by_node"], pr["target_node"]
        ym, xm = meta[y], meta[x]
        xc = re.compile("|".join(D.cite_patterns(xm[5])) or r"(?!x)x")
        yc = re.compile("|".join(D.cite_patterns(ym[5])) or r"(?!x)x")
        xt = sorted(RC.name_tokens(xm[6]) | RC.name_tokens(pr.get("target_name", "")), key=len, reverse=True)
        yt = sorted(RC.name_tokens(ym[6]) | RC.name_tokens(pr.get("label", "")), key=len, reverse=True)
        xn = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(t) for t in xt)) if xt else None
        yn = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(t) for t in yt)) if yt else None
        pats.append((pr, xc, yc, xn, yn, int(ym[4]), keys_of(xm[5]), keys_of(ym[5])))
    out = []
    B = 400
    for k in range(0, len(paths), B):
        chunk = paths[k:k + B]
        inp = "".join("HEAD:%s\n" % p for p in chunk).encode()
        res = subprocess.run(["git", "-C", D.REPO, "cat-file", "--batch"], input=inp, capture_output=True).stdout
        i = 0
        for p in chunk:
            nl = res.index(b"\n", i)
            hdr = res[i:nl].split()
            i = nl + 1
            if hdr[1] == b"missing":
                continue
            size = int(hdr[2])
            t = res[i:i + size].decode("utf-8", "replace").replace("\r\n", "\n")
            i += size + 1
            if not CUE.search(t):
                continue
            wn, wd, wname = node[p]
            if not wd:
                continue
            pm, body0 = RC.part_map2(t)
            view = RC.unwrap_view(t, body0) if RC.hard_wrapped(t, body0) else t
            present = cite_keys(view)
            cuelines = []
            off = body0
            for line in view[body0:].split("\n"):
                la = off
                off += len(line) + 1
                if len(line) >= 20 and CUE.search(line):
                    cuelines.append((la, line))
            for pr, xc, yc, xn, yn, yd, xk, yk in pats:
                if wn in (pr["by_node"], pr["target_node"]) or int(wd) <= yd:
                    continue
                cx = bool(xk & present)
                cy = bool(yk & present)
                if not (cx or cy):
                    continue
                for la, line in cuelines:
                    xr = refs_of(xc, xn if cx else None, line)
                    yr = refs_of(yc, yn if cy else None, line)
                    if not xr and not yr:
                        continue
                    seen = set()
                    for c in CUE.finditer(line):
                        best = None
                        for rx in xr:
                            for ry in yr:
                                a = min(c.start(), rx[0], ry[0])
                                b = max(c.end(), rx[1], ry[1])
                                if b - a > MAXSPAN - 20:
                                    continue
                                # prefer citations, then the tighter span
                                score = (0 if rx[2] == "cite" else 1) + (0 if ry[2] == "cite" else 1), b - a
                                if best is None or score < best[0]:
                                    best = (score, a, b, rx, ry)
                        if best:
                            _, a, b, rx, ry = best
                            sa, sb = widen(line, a, b)
                            if (sa, sb) in seen:
                                continue
                            seen.add((sa, sb))
                            # the scanning forms of dsearch_y: "Y ... overruling" (cue <= 170 after Y) or "overruled by/in Y"
                            form = any(0 <= c.start() - r[1] <= 170 or 0 <= r[0] - c.end() <= 90 for r in yr)
                            part, sec = RC.part_at(pm, la + c.start())
                            out.append([pr["idx"], pr["pair_id"], pr["by_node"], pr["target_node"], "both", wn, wd,
                                        wname, part, str(la + sa), "x" + rx[2] + "+y" + ry[2], "1" if form else "0",
                                        line[sa:sb].replace("\t", " ")])
                            continue
                        near = [r for r in xr if min(abs(c.start() - r[1]), abs(r[0] - c.end())) <= 200]
                        if near:
                            r = min(near, key=lambda r: (r[2] != "cite", min(abs(c.start() - r[1]), abs(r[0] - c.end()))))
                            a = min(c.start(), r[0])
                            b = max(c.end(), r[1])
                            sa, sb = widen(line, a, b)
                            if (sa, sb) in seen:
                                continue
                            seen.add((sa, sb))
                            part, sec = RC.part_at(pm, la + c.start())
                            out.append([pr["idx"], pr["pair_id"], pr["by_node"], pr["target_node"], "weakx", wn, wd,
                                        wname, part, str(la + sa), "x" + r[2], "0", line[sa:sb].replace("\t", " ")])
                            continue
                        if cy:
                            neary = [r for r in yr if r[2] == "cite" and
                                     (0 <= c.start() - r[1] <= 170 or 0 <= r[0] - c.end() <= 90)]
                            if neary:
                                r = neary[0]
                                a = min(c.start(), r[0])
                                b = max(c.end(), r[1])
                                sa, sb = widen(line, a, b)
                                if (sa, sb) in seen:
                                    continue
                                seen.add((sa, sb))
                                part, sec = RC.part_at(pm, la + c.start())
                                out.append([pr["idx"], pr["pair_id"], pr["by_node"], pr["target_node"], "weaky", wn,
                                            wd, wname, part, str(la + sa), "ycite", "1",
                                            line[sa:sb].replace("\t", " ")])
    out.sort(key=lambda o: (int(o[0]), {"both": 0, "weakx": 1, "weaky": 2}[o[4]], int(o[6]), int(o[9])))
    with open(os.path.join(HERE, "later_cands.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tpair_id\tby_node\ttarget_node\ttype\tw_node\tw_date\tw_name\tpart\toffset\trefs\tyform\tspan\n")
        for o in out:
            f.write("\t".join(o) + "\n")
    ws = sorted({o[5] for o in out if o[4] in ("both", "weakx")}, key=int)
    P.cache(ws)
    n = {}
    for o in out:
        n[o[4]] = n.get(o[4], 0) + 1
    print("files", len(paths), "cands", n, "W cached", len(ws),
          "pairs with both", len({o[0] for o in out if o[4] == "both"}))


if __name__ == "__main__":
    main()
