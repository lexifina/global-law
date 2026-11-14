"""Miss anatomy: where does the pipeline lose an (overruled X, overruling Y) pair?

    python -X utf8 trace.py --pairs PAIRS.tsv --out OUT.jsonl

PAIRS.tsv: x <tab> y (node ids; one line per pair). Only the pair is read; the tracer never sees why a pair is listed.
For every pair it records, from corpus text and pipeline files only:
  mention   Y's text cites X (WIDE_RX + r6cite.resolve over the staged v3 + graph index), names X (party tokens),
            or has an unresolved citation whose volume/page equals one of X's citations (a reporter-form gap)
  cue       sentences of Y with an overruling-family verb within 600 characters of a mention of X
  reader    data/reader_work cand/res records for those sentences: reject reason, sent to the model, the model's answer
  queue     whether the candidate id is in the round-3 own-act queue (work/round3/queue/queue_snapshot.tsv)
  rows      v3 treatments rows by Y on X (any kind) and their Lean verdicts (round7/out/v3/certs.tsv)
  status    X's non-history neg/unknown status rows in round7/out/v3/status.tsv (actor)
"""
import argparse, collections, gzip, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common8 import (C2, STAGE, OUT, RW, L, r6cite, load_index, cites_of, party_tokens, sentence_around)  # noqa

FAMRX = re.compile(r"overrul|disapprov|reced\w*\s+from|abrogat|repudiat|no\s+longer|not\s+(?:be\s+)?follow|"
                   r"overturn|unsound|erroneous|wrongly\s+decided|not\s+(?:the\s+)?law|cannot\s+be\s+sustained|"
                   r"not\s+sustained|in\s+conflict|conflict", re.I)
EXPL = re.compile(r"overrul|disapprov|reced\w*\s+from|abrogat", re.I)


def load_pairs(p):
    out = collections.defaultdict(set)
    for line in open(p, encoding="utf-8"):
        f = line.split()
        if len(f) >= 2 and f[0].isdigit() and f[1].isdigit():
            out[int(f[0])].add(int(f[1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pairs = load_pairs(a.pairs)
    xs = set(pairs)
    ys = set(y for v in pairs.values() for y in v)
    print("pairs", sum(len(v) for v in pairs.values()), "X", len(xs), "Y", len(ys), flush=True)
    idx = load_index()
    print("index", len(idx), flush=True)
    rows = {n: L.node_row(n) for n in xs | ys}
    texts = L.fetch_texts(ys)
    # treatments rows of v3 by Y
    trows = collections.defaultdict(list)
    with open(os.path.join(STAGE, "treatments.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) > 3 and p[1].isdigit() and int(p[1]) in ys:
                trows[int(p[1])].append(p)
    verdict = {}
    with open(os.path.join(OUT, "certs.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3:
                verdict[p[1]] = p[2]
    status = collections.defaultdict(list)
    with open(os.path.join(OUT, "status.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0].isdigit() and int(p[0]) in xs:
                status[int(p[0])].append(p)
    queue = set()
    qp = os.path.join(C2, "work", "round3", "queue", "queue_snapshot.tsv")
    for line in open(qp, encoding="utf-8"):
        queue.add(line.split("\t", 1)[0])
    # reader files per repo of Y
    by_repo = collections.defaultdict(set)
    for y in ys:
        by_repo[rows[y][1]].add(y)
    cand = collections.defaultdict(list)
    rej = {}
    items = {}
    for repo, nodes in by_repo.items():
        for sub in ("cand", "cand2", "cand3"):
            p = os.path.join(RW, sub, repo + ".jsonl.gz")
            if not os.path.exists(p):
                continue
            with gzip.open(p, "rt", encoding="utf-8") as f:
                for line in f:
                    if '"t": "c"' not in line[:12]:
                        continue
                    r = json.loads(line)
                    if r["n"] in nodes:
                        cand[r["n"]].append((sub, r["s0"], r["s1"], r.get("fam"), r.get("part")))
        for sub in ("res", "res2", "res3", "res_implicit"):
            p = os.path.join(RW, sub, repo + ".rejects.tsv.gz")
            if os.path.exists(p):
                with gzip.open(p, "rt", encoding="utf-8") as f:
                    for line in f:
                        q = line.rstrip("\n").split("\t")
                        if int(q[0].split(":")[0]) in nodes:
                            rej[(sub, q[0])] = q[1]
            p = os.path.join(RW, sub, repo + ".items.jsonl.gz")
            if os.path.exists(p):
                with gzip.open(p, "rt", encoding="utf-8") as f:
                    for line in f:
                        r = json.loads(line)
                        if r["n"] in nodes:
                            items[(sub, r["id"])] = [t.get("node") for t in r.get("targets", [])]
    llm = {}
    for fn in ("main.gpt-5.4-mini.jsonl", "hard.gpt-6.1-sol.jsonl"):
        with open(os.path.join(RW, "llm", fn), encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if int(r["id"].split(":")[0]) in ys:
                    llm[(fn[:4], r["id"])] = r["r"]
    out = open(a.out, "w", encoding="utf-8", newline="\n")
    for x in sorted(pairs):
        xr = rows[x]
        xcites = [c.strip() for c in xr[5].split(";") if c.strip()] if len(xr) > 5 else []
        xvp = set()
        for c in xcites:
            m = re.match(r"\s*(\d+)\s+(.+?)\s+(\d+)\s*$", c)
            if m:
                xvp.add((m.group(1), m.group(3)))
        xtok = party_tokens(xr[6] if len(xr) > 6 else "")
        for y in sorted(pairs[x]):
            yr = rows[y]
            rec = {"x": x, "y": y, "x_name": xr[6], "x_cite": xr[5], "x_date": xr[4], "x_repo": xr[1],
                   "y_name": yr[6], "y_cite": yr[5], "y_date": yr[4], "y_repo": yr[1], "y_court": yr[3]}
            t = texts.get(y)
            if not t:
                rec["stage"] = "a:no_text"
                out.write(json.dumps(rec) + "\n")
                continue
            text = t[1]
            cs = cites_of(text, idx)
            hits = [(s, e, g) for s, e, g, n, k, fm in cs if n == x]
            vp_miss = []
            for s, e, g, n, k, fm in cs:
                if n is None:
                    m = re.match(r"\s*(\d+)\s+(.+?)\s*,?\s*(\d+)\s*$", g)
                    if m and (m.group(1), m.group(3)) in xvp:
                        vp_miss.append((s, e, g))
            names = []
            for tok in xtok[:3]:
                for m in re.finditer(r"\b" + re.escape(tok) + r"\b", text):
                    names.append((m.start(), m.end(), tok))
            rec["cite_hits"] = [g for s, e, g in hits][:5]
            rec["vp_miss"] = [g for s, e, g in vp_miss][:5]
            rec["name_hits"] = len(names)
            rec["name_tok"] = xtok[:3]
            ments = [s for s, e, g in hits] + [s for s, e, g in vp_miss] + [s for s, e, g in names]
            # cue sentences near a mention
            cues = []
            seen = set()
            for pos in ments:
                lo, hi = max(0, pos - 600), min(len(text), pos + 600)
                for m in FAMRX.finditer(text, lo, hi):
                    s0, s1 = sentence_around(text, m.start())
                    if s0 in seen:
                        continue
                    seen.add(s0)
                    cues.append((s0, s1, m.group(0).lower(), bool(EXPL.search(text[s0:s1]))))
            rec["cue_sents"] = [{"s": [s0, s1], "cue": c, "explicit": ex,
                                 "text": text[s0:s1][:500].replace("\n", " ")} for s0, s1, c, ex in sorted(cues)]
            # reader stages for candidates overlapping the cue sentences
            rd = []
            for sub, c0, c1, fam, part in cand.get(y, []):
                if not any(c0 < s1 + 50 and s0 - 50 < c1 for s0, s1, _, _ in cues):
                    continue
                cid = "%d:%d" % (y, c0)
                resub = {"cand": "res", "cand2": "res2", "cand3": "res3"}[sub]
                info = {"sub": sub, "cid": cid, "span": [c0, c1], "fam": fam, "part": part,
                        "reject": rej.get((resub, cid)), "item_targets": items.get((resub, cid)),
                        "in_queue": cid in queue}
                for k in ("main", "hard"):
                    if (k, cid) in llm:
                        r = llm[(k, cid)]
                        info["llm_" + k] = {"own": r.get("own_act"), "kind": r.get("kind"), "targets": r.get("targets"),
                                            "q": (r.get("quote") or "")[:200]}
                rd.append(info)
            rec["reader"] = rd
            tr = []
            for p in trows.get(y, []):
                if int(p[2]) == x:
                    tr.append({"id": p[0], "kind": p[4], "scope": p[5], "verdict": verdict.get(p[0]), "q": p[11][:200]})
            rec["rows"] = tr
            rec["rows_other_targets_near"] = sum(1 for p in trows.get(y, []) if int(p[2]) != x and any(
                abs(int(p[9]) - s0) < 800 for s0, s1, _, _ in cues))
            st = [p for p in status.get(x, []) if (p[5].startswith("neg") or p[5].startswith("unknown"))
                  and p[10] in ("treatment", "prospective", "recognised")]
            rec["status_actor_y"] = [p[5] + "|" + p[10] for p in st if p[9] == str(y)]
            rec["status_any"] = sorted(set(p[5] + "|" + p[10] + "|" + p[9] for p in st))[:6]
            out.write(json.dumps(rec) + "\n")
    out.close()


if __name__ == "__main__":
    main()
