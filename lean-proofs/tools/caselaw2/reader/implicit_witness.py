"""Round 3, the `explicit = 0` tier with a witness (round3/implicit_schema.md). Called as `implicit.py certify3`.

A later decision W of X's own court (or the Supreme Court of the United States) states that X is no longer good law.
If it names the decision Y that did it, the row is keyed on Y: id tw:<Y>:<X>:<start>:<W>, by_node = Y, date = Y's
date, text_sha / offsets / quote are W's, and treatment_witness.tsv gets (id, W, evidence naming Y, reader). If it
names no Y, the row keeps the round-2 format: id ti:<W>:<X>:<start>:0, by_node = W. Candidates: implicit3.py scan.

The checker disqualifies "overruled by" / "abrogated by" in a quote. For "X, overruled by Y" the quote is cut after
the participle; the window still shows "by Y", and Y's evidence is verified to be in the window.
"""
import collections, glob, gzip, hashlib, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA  # noqa: E402
import rules2  # noqa: E402

CUES3 = {"overruled": ("overrul", "repudiat", "abandon", "no longer", "overturn", "disavow", "discard", "reject",
                       "not survive", "cannot survive", "wrongly decided"),
         "abrogated": ("abrogat",), "disapproved": ("disapprov",)}
BY_CUT3 = re.compile(r"\b(overruled|abrogated|disapproved)(?=(?:\s+(?:in\s+part|on\s+other\s+grounds|sub\s+silentio|"
                     r"implicitly|expressly|of|in\s+relevant\s+part|on\s+another\s+ground))*,?\s+by\b)", re.I)
SCOTUS = "Supreme Court of the United States"
import cue_table  # noqa: E402  (round 4: the shared table)
CUES3 = {k: tuple(cue_table.VERBS[k]) for k in CUES3}


def certify3(a):
    from certify import find_quote, clean, PART_OUT
    from certify2 import evidence_in
    W_ = os.path.dirname(os.path.dirname(DATA))
    ans = {}
    for f in sorted(glob.glob(os.path.join(a.answers, "ans_*.jsonl"))):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    ans[str(r["id"]).strip()] = r
                except Exception:
                    pass
    items = {}
    for line in gzip.open(a.items, "rt", encoding="utf-8"):
        it = json.loads(line)
        items[it["id"]] = it
    idx = {}
    for line in open(os.path.join(W_, "graph", "cite_index.tsv"), encoding="utf-8"):
        k, v = line.rstrip("\n").split("\t")
        idx[k] = int(v)
    tier = {}
    for line in open(os.path.join(W_, "lean-in-v3", "courts_named.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        tier[f[1]] = (f[5], int(f[4]))
    need = set()
    for i, r in ans.items():
        it = items.get(i)
        if it is not None and r.get("states"):
            need.add(it["n"])
            need.update(t["node"] for t in it["targets"])
    dec = {}
    for line in open(os.path.join(DATA, "decisions2.tsv"), encoding="utf-8"):
        f = line.split("\t", 8)
        if int(f[0]) in need:
            dec[int(f[0])] = (int(f[2] or 0), f[7])
    explicit, negx, have = set(), set(), set()
    for b in a.base:
        for line in open(b, encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if f[4] in ("overruled", "disapproved", "recededFrom", "abrogated"):
                if f[7] == "1":
                    explicit.add((int(f[1]), int(f[2])))
                    negx.add(int(f[2]))
                elif f[14].endswith(":implicit"):
                    y = f[0].rsplit(":", 1)[-1] if f[0].startswith("ti:") else f[1]
                    have.add((int(y), int(f[2])))
    os.makedirs(a.out, exist_ok=True)
    st = collections.Counter()
    st["answers"] = len(ans)
    rows = {}
    rej = open(os.path.join(a.out, "implicit3_rejects.tsv"), "w", encoding="utf-8", newline="\n")
    for i, r in ans.items():
        it = items.get(i)
        if it is None:
            st["answer-without-item"] += 1
            continue
        if not r.get("states"):
            st["not-a-statement"] += 1
            continue

        def pick(v):
            return it["targets"][int(v[1:]) - 1] if isinstance(v, str) and re.fullmatch(r"T\d+", v) and \
                1 <= int(v[1:]) <= len(it["targets"]) else None
        pairs = [(r.get("x"), r.get("y"))] + [(m.get("x"), m.get("y")) for m in (r.get("more") or [])
                                              if isinstance(m, dict)]
        wcourt = it["by"]["court"]
        if it["n"] not in dec or dec[it["n"]][1] != it["sha"]:
            st["w-sha-not-in-decisions2"] += 1
            rej.write(f"{i}\tcert\tw-sha\n")
            continue
        wdate = dec[it["n"]][0]
        for xv, yv in pairs:
            x, y = pick(xv), pick(yv)
            if x is None or x["node"] == it["n"] or x["node"] not in dec:
                st["no-x"] += 1
                rej.write(f"{i}\tmodel\tno-x\n")
                continue
            if y is not None and (y["node"] == x["node"] or y["node"] == it["n"] or y["node"] not in dec):
                y = None
            xd = dec[x["node"]][0]
            if not (xd and wdate and xd < wdate):
                st["dates-x"] += 1
                rej.write(f"{i}\tcert\tdates-x\n")
                continue
            if not (x["court"] == wcourt or wcourt.startswith(SCOTUS)):
                st["witness-no-standing"] += 1
                rej.write(f"{i}\tcert\twitness-no-standing\n")
                continue
            if y is not None:
                yd = dec[y["node"]][0]
                if not (yd and xd <= yd <= wdate):
                    st["dates-y"] += 1
                    rej.write(f"{i}\tcert\tdates-y\n")
                    continue
                yt, xt = tier.get(y["court"], ("T", -1)), tier.get(x["court"], ("T", -2))
                if not (y["court"] == x["court"] or y["court"].startswith(SCOTUS) or
                        (yt[1] == xt[1] and yt[0] == "L" and xt[0] != "L")):
                    st["y-no-power"] += 1
                    rej.write(f"{i}\tcert\ty-no-power\n")
                    continue
                if (y["node"], x["node"]) in explicit or (y["node"], x["node"]) in have:
                    st["row-exists"] += 1
                    rej.write(f"{i}\tcert\trow-exists\n")
                    continue
            lw = it["w"][it["lw0"] - it["w0"]:it["lw1"] - it["w0"]]
            pos = find_quote(lw, r.get("quote") or "", it["s0"] - it["lw0"])
            if pos is None or pos[1] - pos[0] > 600:
                pos = (it["s0"] - it["lw0"], it["s1"] - it["lw0"])
                st["quote-fallback-sentence"] += 1
            q0, q1 = pos
            quote = lw[q0:q1]
            ql = quote.lower()
            kind = r.get("kind") if r.get("kind") in CUES3 else "overruled"
            if not any(c in ql for c in CUES3[kind]):
                kind = next((k for k in CUES3 if any(c in ql for c in CUES3[k])), None)
            if kind is None:
                st["no-cue"] += 1
                rej.write(f"{i}\tcert\tno-cue\n")
                continue
            cut = 0
            if any(p in ql for p in rules2.DISQUAL2):
                m = BY_CUT3.search(quote)
                if m:
                    q1 = q0 + m.end()
                    quote = lw[q0:q1]
                    ql = quote.lower()
                    cut = 1
                    if not any(c in ql for c in CUES3[kind]):
                        kind = next((k for k in CUES3 if any(c in ql for c in CUES3[k])), kind)
                if any(p in ql for p in rules2.DISQUAL2) or not any(c in ql for c in CUES3[kind]):
                    st["disqualifier"] += 1
                    rej.write(f"{i}\tcert\tdisqualifier-in-quote\n")
                    continue
            lead = len(quote) - len(quote.lstrip())
            q0, q1 = q0 + lead, q0 + len(quote.rstrip())
            quote = lw[q0:q1]
            if not quote:
                continue
            start, end = it["lw0"] + q0, it["lw0"] + q1
            st0, en0 = max(it["w0"], start - 400), min(it["w1"], end + 400, it["len"])
            window = it["w"][st0 - it["w0"]:en0 - it["w0"]]
            ex = evidence_in(x, window, idx)
            ey = evidence_in(y, window, idx) if y is not None else None
            if ex is None:
                st["evidence-x"] += 1
                rej.write(f"{i}\tcert\tevidence-x\n")
                continue
            if y is not None and ey is None:
                st["evidence-y-missing"] += 1
                rej.write(f"{i}\tcert\tevidence-y\n")
                continue
            part = PART_OUT.get(it["part"], "unknown")
            if part not in ("majority", "plurality", "perCuriam"):
                st["part"] += 1
                continue
            scope = r.get("scope") if r.get("scope") in ("all", "partialUnknown", "otherGrounds") else "partialUnknown"
            try:
                conf = max(0.0, min(1.0, float(r.get("confidence", 0.5))))
            except (TypeError, ValueError):
                conf = 0.5
            row = {"w": it["n"], "x": x["node"], "y": y["node"] if y is not None else 0, "wdate": wdate,
                   "ydate": dec[y["node"]][0] if y is not None else 0, "kind": kind, "scope": scope, "sha": it["sha"],
                   "start": start, "end": end, "quote": clean(quote), "ev": ex, "evy": ey, "part": part, "conf": conf,
                   "item": i, "cut": cut, "win": (it["sha"], st0, en0, clean(window)), "why": it["why"],
                   "scotus": 0 if wcourt.startswith(SCOTUS) else 1, "og": 1 if scope == "otherGrounds" else 0,
                   "xd": x, "yd": y, "wd": it["by"]}
            key = (row["y"], row["x"])
            old = rows.get(key)
            rk = (row["og"], row["cut"], row["scotus"], row["wdate"])
            if old is None or rk < (old["og"], old["cut"], old["scotus"], old["wdate"]):
                rows[key] = row
            st["statements"] += 1
    rej.close()
    withy = {x for (y, x) in rows if y}
    havex = {x for _, x in have}
    # a statement naming no Y is kept only when X has no row naming a Y and no explicit status-changing row
    out = [t for (y, x), t in rows.items() if y or (x not in withy and x not in negx and x not in havex)]
    st["no-y-dropped"] = len(rows) - len(out)
    out.sort(key=lambda t: (t["w"], t["x"], t["start"]))

    def op(n):
        return open(os.path.join(a.out, n), "w", encoding="utf-8", newline="\n")
    with op("treatments_delta.tsv") as fo, op("treatment_witness_delta.tsv") as fw, \
            op("treatments_items_delta.tsv") as fi, op("cert_text_delta.tsv") as fc, \
            op("window_sha_delta.tsv") as fh, op("rows.tsv") as fr, op("rows_detail.jsonl") as fd:
        seen = set()
        for t in out:
            if t["y"]:
                tid = f"tw:{t['y']}:{t['x']}:{t['start']}:{t['w']}"
                by, date = t["y"], t["ydate"]
                fw.write(f"{tid}\t{t['w']}\t{t['evy']}\tclaude-subagent:implicit\n")
            else:
                tid = f"ti:{t['w']}:{t['x']}:{t['start']}:0"
                by, date = t["w"], t["wdate"]
            fo.write("\t".join(map(str, [tid, by, t["x"], date, t["kind"], t["scope"], "unknown", 0, t["sha"],
                                         t["start"], t["end"], t["quote"], t["ev"], t["part"],
                                         "claude-subagent:implicit", f"{t['conf']:.2f}"])) + "\n")
            fi.write(f"{tid}\t{t['item']}\t{'quote-cut-before-by' if t['cut'] else 'quote'}\t{t['why']};by={t['y']};"
                     f"witness={t['w']};byEvidence={t['evy']}\n")
            fr.write("\t".join(map(str, [t["x"], t["y"] or "", t["w"], t["wd"]["court"], t["wdate"], t["kind"],
                                         t["quote"], t["start"], t["end"], t["part"], tid])) + "\n")
            fd.write(json.dumps({"tid": tid, "x": t["xd"], "y": t["yd"], "w": t["wd"], "wnode": t["w"],
                                 "kind": t["kind"], "scope": t["scope"], "quote": t["quote"], "window": t["win"][3],
                                 "why": t["why"]}, ensure_ascii=False) + "\n")
            if t["win"][:3] not in seen:
                seen.add(t["win"][:3])
                fc.write("\t".join(map(str, t["win"])) + "\n")
                fh.write("\t".join(map(str, [t["win"][0], t["win"][1], t["win"][2],
                                             hashlib.sha1(t["win"][3].encode("utf-8")).hexdigest(), "corpus"])) + "\n")
    st["rows"] = len(out)
    st["rows_witness_named_y"] = sum(1 for t in out if t["y"])
    st["rows_no_y_round2_format"] = sum(1 for t in out if not t["y"])
    st["rows_quote_cut"] = sum(t["cut"] for t in out)
    st["by_kind_scope"] = {f"{k}|{s}": v for (k, s), v in sorted(collections.Counter(
        (t["kind"], t["scope"]) for t in out).items())}
    st["by_group"] = dict(collections.Counter(t["why"] for t in out))
    with op("implicit3_stats.json") as f:
        json.dump(st, f, indent=1)
    print(json.dumps(st, indent=0))
