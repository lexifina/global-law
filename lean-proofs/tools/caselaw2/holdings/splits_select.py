"""Step 1 of the circuit-split pipeline: the most-cited US Code subsections in the federal courts of appeals since 1995.

    python splits_select.py [N=300]
writes data/holdings_work/split_subsections.tsv: rank, usc key (title:section(sub)), circuit decisions, scotus decisions,
    heading, subsection text (first 900 chars, one line)
and data/holdings_work/split_citers.tsv: usc key, node, court kind (circuit number 1-13, or 0 for SCOTUS), date
"""
import collections, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text

W = text.WORK
OUT = os.path.join(W, "caselaw-lean-2", "data", "holdings_work")
EXTRA = {372: 6, 480: 9}


def circuit_courts():
    cc = {}
    for l in open(os.path.join(W, "lean-in-v3", "courts_named.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        if f[7] in ("circuit", "dc-circuit"):
            cc[int(f[0])] = int(f[6])
    cc.update(EXTRA)
    return cc


def node_kind():
    cc = circuit_courts()
    kind = {}
    for l in open(os.path.join(W, "lean-in-v3", "decisions.tsv"), encoding="utf-8"):
        a, b, _ = l.split("\t", 2)
        c = int(b)
        if c in cc:
            kind[int(a)] = cc[c]
        elif c == 2906:
            kind[int(a)] = 0
    return kind


def sub_text(title, section, sub):
    r = subprocess.run(["git", "-C", os.path.join(W, "usc-full.git"), "show", f"main:title-{title}/{section}.md"],
                       capture_output=True, creationflags=text.NOWIN)
    t = r.stdout.decode("utf-8", "replace")
    head = t.split("\n", 1)[0].lstrip("# ").strip()
    m = re.search(r"(?m)^\s*- \(" + re.escape(sub) + r"\)", t)
    body = t[m.start():m.start() + 900] if m else ""
    return head, re.sub(r"\s+", " ", body).strip()


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    os.makedirs(OUT, exist_ok=True)
    kind = node_kind()
    cnt = collections.defaultdict(set)
    sc = collections.defaultdict(set)
    rows = []
    for l in open(os.path.join(W, "usc", "results", "rows_out.tsv"), encoding="utf-8"):
        f = l.split("\t")
        nid = int(f[1])
        k = kind.get(nid)
        if k is None or not f[4]:
            continue
        m = re.match(r"(\d+) U\.S\.C\. § (\S+)$", f[3])
        if not m:
            continue
        key = f"{m.group(1)}:{m.group(2)}({f[4]})"
        d = int(f[2].replace("-", ""))
        rows.append((key, nid, k, d))
        (sc if k == 0 else cnt)[key].add(nid)
    top = sorted(cnt, key=lambda k: -len(cnt[k]))[:n]
    tops = set(top)
    with open(os.path.join(OUT, "split_subsections.tsv"), "w", encoding="utf-8", newline="\n") as fo:
        for i, k in enumerate(top):
            t, rest = k.split(":", 1)
            s, sub = rest[:-1].split("(", 1)
            head, body = sub_text(t, s, sub)
            fo.write(f"{i + 1}\t{k}\t{len(cnt[k])}\t{len(sc.get(k, ()))}\t{head}\t{body}\n")
    seen = set()
    with open(os.path.join(OUT, "split_citers.tsv"), "w", encoding="utf-8", newline="\n") as fo:
        for key, nid, k, d in rows:
            if key in tops and (key, nid) not in seen:
                seen.add((key, nid))
                fo.write(f"{key}\t{nid}\t{k}\t{d}\n")
    print("subsections", len(cnt), "top", len(top), "citer rows", len(seen),
          "decisions", len({x[1] for x in seen}), "min count", len(cnt[top[-1]]))


if __name__ == "__main__":
    main()
