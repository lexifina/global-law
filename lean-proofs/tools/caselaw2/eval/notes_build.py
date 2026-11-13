"""Resolve the notes found by notes_extract.py into gold/reports_typed.tsv and gold/reports_typed_pairs.tsv.

    python tools/caselaw2/eval/notes_build.py

For each note: the noting decision (repo, path -> node), the target (the last citation before the note phrase that
resolves, with at most a short gap after removing parentheticals), the treating decision (the first citation after
"by"/"in", or after the history signal), or, for "as stated in"/"as recognized in", the decision that states it
(`stated_in`, not the treating decision). Kind and scope come from the phrase.

reports_typed.tsv columns: id, note_node, note_date, target_node, target_date, by_node, by_date, stated_in_node, kind,
scope (all|partialUnknown|otherGrounds), implicit (0/1), form, qual, sec, note_offset, blob_sha, repo, snippet.
"""
import array, collections, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "caselaw"))
from graph import norm_cite  # noqa: E402
from events import CITE_RX, NOISE_BEFORE  # noqa: E402

W = os.path.expanduser("~/Documents/us-caselaw-lean-work")
G = os.path.join(W, "caselaw-lean-2", "gold")
NOTES = os.path.join(G, "work", "notes")

OTHER = re.compile(r"other\s+grounds?|another\s+ground|different\s+grounds?|other\s+points?|another\s+point|"
                   r"different\s+point|other\s+issues?|another\s+issue|unrelated\s+grounds|separate\s+grounds", re.I)
PART = re.compile(r"in\s+part|relevant\s+part|other\s+part|other\s+respects|partially|to\s+the\s+extent|insofar|"
                  r"on\s+(?:this|that|the\s+latter|the\s+former)\s+point|\bas\s+to\b", re.I)
IMPL = re.compile(r"sub\s+silentio|by\s+implication|implicitly|effectively|in\s+effect", re.I)
STATED = re.compile(r"as\s+(?:stated|recognized|noted|explained)\s+in|recognized\s+(?:by|in)|noted\s+(?:by|in)", re.I)
HIST = {"vac-hist", "rev-hist", "vac-enbanc"}
HAS = {"ovr-has", "abr-has", "dis-has", "rec-has"}


def strip_paren(s):
    out, depth = [], 0
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def main():
    idx = {}
    for line in open(os.path.join(W, "graph", "cite_index.tsv"), encoding="utf-8"):
        k, v = line.rstrip("\n").split("\t")
        idx[k] = int(v)
    print("index", len(idx), flush=True)
    dates = array.array("I")
    for line in open(os.path.join(W, "lean-in-v3", "decisions.tsv"), encoding="utf-8"):
        i, c, d = line.split("\t")
        i = int(i)
        while len(dates) < i:
            dates.append(0)
        dates.append(int(d))
    files = sorted(glob.glob(os.path.join(NOTES, "*.notes.tsv")))
    want = collections.defaultdict(set)
    for f in files:
        repo = os.path.basename(f)[:-len(".notes.tsv")]
        for line in open(f, encoding="utf-8"):
            want[repo].add(line.split("\t", 1)[0])
    node_of = {}
    for line in open(os.path.join(W, "graph", "nodes.tsv"), encoding="utf-8"):
        f = line.split("\t", 3)
        if f[2] in want.get(f[1], ()):
            node_of[(f[1], f[2])] = int(f[0])
    print("noting decisions", len(node_of), flush=True)

    def cites(t):
        out = []
        for m in CITE_RX.finditer(t):
            k = norm_cite(f"{m.group(1)} {re.sub(r'[()]', '', m.group(2))} {m.group(3)}")
            j = idx.get(k) if k else None
            if j is not None:
                out.append((m.start(), m.end(), j))
        return out

    cnt = collections.Counter()
    pairs = collections.defaultdict(lambda: [0, set(), 99999999])
    out = open(os.path.join(G, "reports_typed.tsv"), "w", encoding="utf-8", newline="\n")
    out.write("id\tnote_node\tnote_date\ttarget_node\ttarget_date\tby_node\tby_date\tstated_in_node\tkind\tscope\t"
              "implicit\tform\tqual\tsec\tnote_offset\tblob_sha\trepo\tsnippet\n")
    rid = 0
    for f in files:
        repo = os.path.basename(f)[:-len(".notes.tsv")]
        for line in open(f, encoding="utf-8"):
            path, sha, sec, off, form, kind, wa, wb, win = line.rstrip("\n").split("\t", 8)
            wa, wb = int(wa), int(wb)
            y = node_of.get((repo, path))
            if y is None:
                cnt["merged-copy-or-no-node"] += 1
                continue
            before, phrase, after = win[:wa], win[wa:wb], win[wb:]
            bt = before[-340:]
            # paren depth of each position, read back from the phrase: a citation inside a parenthetical that closes
            # before the phrase ("(quoting X)", "(citing X)") is not the target
            depth, dep = 0, [0] * (len(bt) + 1)
            for i_ in range(len(bt) - 1, -1, -1):
                ch = bt[i_]
                if ch == ")":
                    depth += 1
                elif ch == "(":
                    depth = max(0, depth - 1)
                dep[i_] = depth
            cb = [c for c in cites(bt) if c[2] != y and dep[c[0]] == 0]
            if not cb:
                cnt[f"{kind}:no-target"] += 1
                continue
            s, e, x = cb[-1]
            gap = strip_paren(bt[e:])
            # the gap: a pin cite, a court/year parenthetical, a short "which held ..." clause for the HAS forms
            lim = 170 if form in HAS else (45 if form in HIST else 70)
            if len(gap.strip(" ,;.")) > lim or re.search(r"[.;]\s+[A-Z]", gap):
                cnt[f"{kind}:gap"] += 1
                continue
            if form in HAS and NOISE_BEFORE.search(gap):
                cnt[f"{kind}:noise"] += 1
                continue
            ca = cites(after[:260])
            first_after = ca[0] if ca and ca[0][0] < 140 else None
            by = stated = -1
            if kind == "supersededByEnactment" or STATED.search(phrase):
                if first_after:
                    stated = first_after[2]
            elif form in HIST:
                if first_after and first_after[0] < 110:
                    by = first_after[2]
            elif first_after and form not in ("ovr-paren",):
                by = first_after[2]
            if by == x:
                by = -1
            if stated == x:
                stated = -1
            xd, yd = dates[x] if x < len(dates) else 0, dates[y]
            bd = dates[by] if by >= 0 else 0
            if xd and yd and xd > yd:
                cnt[f"{kind}:target-after-note"] += 1
                continue
            if by >= 0 and bd and xd and bd < xd:
                by = -1
                cnt[f"{kind}:by-before-target"] += 1
            # qualifiers after the phrase ("has been receded from in part on other grounds by", "vacated on other
            # grounds"), up to the treating decision's name or citation
            tail = re.split(r"\d|\bby\b|\bas\s+(?:stated|recognized)|[A-Z]|[;.(]", after[:70], maxsplit=1)[0]
            qt = phrase + " " + tail
            scope = "otherGrounds" if OTHER.search(qt) else ("partialUnknown" if PART.search(qt) else "all")
            impl = 1 if IMPL.search(qt) else 0
            qual = re.sub(r"\s+", " ", phrase).strip()[:80]
            rid += 1
            snip = win[max(0, wa - 260):wb + 200]
            out.write(f"{rid}\t{y}\t{yd}\t{x}\t{xd}\t{by}\t{bd}\t{stated}\t{kind}\t{scope}\t{impl}\t{form}\t{qual}\t"
                      f"{sec}\t{off}\t{sha}\t{repo}\t{snip}\n")
            cnt[f"{kind}:ok"] += 1
            cnt[f"{kind}:ok-with-by"] += by >= 0
            pr = pairs[(x, kind, by, scope)]
            pr[0] += 1
            pr[1].add(y)
            pr[2] = min(pr[2], yd or 99999999)
    out.close()
    with open(os.path.join(G, "reports_typed_pairs.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("target_node\ttarget_date\tkind\tby_node\tby_date\tscope\tnotes\tnoting_decisions\tfirst_note_date\n")
        for (x, k, b, sc), (n, ys, fd) in sorted(pairs.items()):
            o.write(f"{x}\t{dates[x] if x < len(dates) else 0}\t{k}\t{b}\t{dates[b] if b >= 0 else 0}\t{sc}\t{n}\t"
                    f"{len(ys)}\t{fd}\n")
    with open(os.path.join(G, "work", "reports_typed_counts.tsv"), "w", encoding="utf-8", newline="\n") as o:
        for k, v in sorted(cnt.items()):
            o.write(f"{k}\t{v}\n")
    print("notes", rid, "pairs", len(pairs))
    for k, v in sorted(cnt.items()):
        print(k, v)


if __name__ == "__main__":
    main()
