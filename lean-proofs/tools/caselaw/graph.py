"""Build the precedent graph of all US case law from the per-repo extracts (tools/caselaw/extract.py).

    python tools/caselaw/graph.py <extract-dir> <graph-dir>

Writes:
  courts.tsv     court id, name, decisions, first/last year (the hierarchy is assigned in courts_map.py)
  nodes.tsv      node id, repo, path, court id, date (yyyymmdd), citations, name
  cite_index.tsv normalised citation -> node id (parallel citations all point to one node; parallel-reporter copies
                 listed as `same-decision-as` are merged into the kept file)
  edges.bin      citing node, cited node pairs (uint32 little-endian), only citations that resolve
  stats.json
"""
import array, collections, glob, json, os, re, sys

CITE = re.compile(r"^\s*(\d+)\s+(.+?)\s+(\d+)\s*$")


def norm_cite(c):
    m = CITE.match(c)
    if not m:
        return None
    rep = re.sub(r"[\s.,']", "", m.group(2)).lower()
    rep = rep.replace("2nd", "2d").replace("3rd", "3d")
    return f"{int(m.group(1))} {rep} {int(m.group(3))}"


def norm_date(d):
    m = re.match(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", d or "")
    if not m:
        return 0
    return int(m.group(1)) * 10000 + int(m.group(2) or 1) * 100 + int(m.group(3) or 1)


def main(ex, out):
    os.makedirs(out, exist_ok=True)
    repos = sorted(os.path.basename(f)[:-10] for f in glob.glob(os.path.join(ex, "*.nodes.tsv")))
    # merge parallel-reporter copies: path -> kept path
    same = {}
    for r in repos:
        p = os.path.join(ex, r + ".relations.tsv")
        if os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                f = line.rstrip("\n").split("\t")
                if len(f) >= 3 and f[1] == "same-decision-as":
                    same[(r, f[0])] = f[2]
    courts, court_n, court_years = {}, collections.Counter(), {}
    idx = {}
    node_rows = []
    path_id = {}
    for r in repos:
        for line in open(os.path.join(ex, r + ".nodes.tsv"), encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) < 9:
                continue
            path, court, decided, dtype, cits, capid, docket, name, cites = f[:9]
            if (r, path) in same:
                continue  # merged into the kept copy (its citations are added below)
            cid = courts.setdefault(court, len(courts))
            date = norm_date(decided)
            court_n[cid] += 1
            y = date // 10000
            lo, hi = court_years.get(cid, (9999, 0))
            court_years[cid] = (min(lo, y or lo), max(hi, y))
            nid = len(node_rows)
            path_id[(r, path)] = nid
            node_rows.append((nid, r, path, cid, date, cits, name, dtype))
            for c in cits.split("|"):
                k = norm_cite(c)
                if k and k not in idx:
                    idx[k] = nid
    # citations of merged copies point at the kept file
    for r in repos:
        for line in open(os.path.join(ex, r + ".nodes.tsv"), encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) >= 5 and (r, f[0]) in same:
                kept = path_id.get((r, same[(r, f[0])]))
                if kept is not None:
                    for c in f[4].split("|"):
                        k = norm_cite(c)
                        if k and k not in idx:
                            idx[k] = kept
    edges = array.array("I")
    resolved = unresolved = 0
    with open(os.path.join(out, "nodes.tsv"), "w", encoding="utf-8", newline="\n") as fn:
        for nid, r, path, cid, date, cits, name, dtype in node_rows:
            fn.write(f"{nid}\t{r}\t{path}\t{cid}\t{date}\t{cits}\t{name}\t{dtype}\n")
    for r in repos:  # second pass: citations (not held in memory with the nodes)
        for line in open(os.path.join(ex, r + ".nodes.tsv"), encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) < 9:
                continue
            nid = path_id.get((r, f[0]))
            if nid is None:
                nid = path_id.get((r, same.get((r, f[0]), "")))
            if nid is None:
                continue
            seen = set()
            for c in f[8].split("|"):
                k = norm_cite(c)
                if not k:
                    continue
                j = idx.get(k)
                if j is None:
                    unresolved += 1
                    continue
                if j != nid and j not in seen:
                    seen.add(j)
                    edges.append(nid); edges.append(j)
                    resolved += 1
    with open(os.path.join(out, "edges.bin"), "wb") as fe:
        edges.tofile(fe)
    with open(os.path.join(out, "courts.tsv"), "w", encoding="utf-8", newline="\n") as fc:
        for name, cid in sorted(courts.items(), key=lambda x: x[1]):
            lo, hi = court_years[cid]
            fc.write(f"{cid}\t{name}\t{court_n[cid]}\t{lo}\t{hi}\n")
    with open(os.path.join(out, "cite_index.tsv"), "w", encoding="utf-8", newline="\n") as fi:
        for k, v in idx.items():
            fi.write(f"{k}\t{v}\n")
    st = {"repos": len(repos), "nodes": len(node_rows), "merged_copies": len(same), "courts": len(courts),
          "citations_indexed": len(idx), "edges": resolved, "cites_unresolved": unresolved}
    json.dump(st, open(os.path.join(out, "stats.json"), "w"), indent=1)
    print(json.dumps(st))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
