"""Round 2, the `explicit = 0` tier: overrulings recognised by a LATER decision of the overruling court.

    python -X utf8 implicit.py resolve [--cand DIR] [--out DIR] [--tiers L] [repo ...]
    python -X utf8 implicit.py certify --answers DIR --out DIR [--res DIR] [--base treatments.tsv ...]

This tier is NOT held out: it uses later courts' notes ("X was overruled by Y", "in Y we overruled X", "Y (overruling
X)"), which the explicit reader recognises only to reject. It is kept apart by its reader label
`claude-subagent:implicit`, its row ids (`ti:`) and `explicit = 0`; such rows never change status (doctrine 9.26,
DEVIATIONS 33) and the evaluation leaves them out of the recall and precision tables.

resolve: candidates of scan2 with the family overrule / abrogate / disapprove, in an opinion part, whose sentence the
explicit rules reject as a report, a narrated past act or not act-shaped, and which name two resolved earlier
decisions X and Y with date(X) <= date(Y) <= date(Z), Y decided by the SAME court as the stating decision Z (the
court recognising its own act), and Y's court the same as X's court or a higher court of X's system (or the Supreme
Court of the United States). Writes <out>/<repo>.items.jsonl.gz in the item format of resolve2.py.

certify: a row per statement the subagent confirmed:
    id          ti:<Z>:<X>:<start>:<Y>
    by_node     Z, the LATER decision whose text carries the statement  (the checker requires the quote to be in the
                by-decision's text; the overruling decision Y is in the id and in treatments_items)
    target_node X;  date = date of Z;  kind overruled | abrogated | disapproved;  explicit = 0
    CERT        the statement in Z's text; target evidence = X's citation or name in the window
The checker disqualifies "overruled by" / "abrogated by" in any quote of a status-changing kind, whatever `explicit`
is. For the citator form "X, overruled by Y" the quote is therefore cut after the participle ("X, 16 Pet. 1,
overruled"); the window still shows "by Y", and Y's citation or name is verified here to be in the window.
"""
import argparse, collections, glob, gzip, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, WORK  # noqa: E402
import rules, rules2  # noqa: E402

NARR = re.compile(r"\b(?:overruled|overruling|abrogated|abrogating|disapproved|disapproving)\b", re.I)
KIND_OF = (("overrul", "overruled"), ("abrogat", "abrogated"), ("disapprov", "disapproved"))
SKIP_PART = ("dissent", "concurrence", "headmatter", "front", "title", "unknown")
TIER_RANK = {"L": 3, "A": 2, "B": 2, "D": 2, "T": 1, "S": 1}
BY_CUT = re.compile(r"\b(overruled|abrogated|disapproved)(?=(?:\s+(?:in\s+part|on\s+other\s+grounds|sub\s+silentio|"
                    r"implicitly|expressly|of))*\s+by\b)", re.I)


def resolve(a):
    from resolve import Ctx
    from resolve2 import targets2
    ctx = Ctx()
    os.makedirs(a.out, exist_ok=True)
    tiers = set(a.tiers.split(","))
    repos = a.repos or sorted(os.path.basename(f)[:-9] for f in glob.glob(os.path.join(a.cand, "*.jsonl.gz")))
    for repo in repos:
        src = os.path.join(a.cand, repo + ".jsonl.gz")
        outp = os.path.join(a.out, repo)
        if not os.path.exists(src) or os.path.exists(outp + ".stats.json"):
            continue
        st = collections.Counter()
        fi = gzip.open(outp + ".items.jsonl.gz.part", "wt", encoding="utf-8", newline="\n")
        d = None
        for line in gzip.open(src, "rt", encoding="utf-8"):
            r = json.loads(line)
            if r["t"] == "d":
                d = r
                continue
            if r["t"] != "c" or not (set(r["fam"]) & {"overrule", "abrogate", "disapprove"}):
                continue
            if r["part"].startswith(SKIP_PART):
                continue
            n = r["n"]
            zc = int(ctx.court[n])
            if ctx.tier.get(zc, "T") not in tiers:
                continue
            sent = r["w"][r["s0"] - r["w0"]:r["s1"] - r["w0"]]
            if not NARR.search(sent):
                continue
            fams1 = [f for f in r["fam"] if f in ("overrule", "abrogate", "disapprove")]
            v1, reason = rules.classify(sent, fams1, r["part"])
            if v1 == "llm" or reason not in ("report", "past", "not-act-shaped"):
                continue
            if reason == "not-act-shaped" and rules2.shapes(sent):
                continue  # read by the explicit round-2 pass
            zd = int(ctx.date[n])
            tg = [t for t in targets2(ctx, n, r, zd) if t[3][0] <= 3]
            # only decisions named within 250 characters of the sentence
            tg = [t for t in tg if r["s0"] - 250 <= t[2] <= r["s1"] + 250]
            if len(tg) < 2:
                st["lt2-decisions"] += 1
                continue
            ok = False
            zsys = ctx.system.get(zc, -1)
            for y in tg:
                yc = int(ctx.court[y[0]])
                if yc != zc or not ctx.date[y[0]]:
                    continue
                for x in tg:
                    if x[0] == y[0] or not ctx.date[x[0]] or ctx.date[x[0]] > ctx.date[y[0]]:
                        continue
                    xc = int(ctx.court[x[0]])
                    if xc == yc or (ctx.system.get(xc, -2) == zsys and TIER_RANK.get(ctx.tier.get(xc, "T"), 1) < 3) or \
                            ctx.court_name.get(zc, "").startswith("Supreme Court of the United"):
                        ok = True
                        break
                if ok:
                    break
            if not ok:
                st["no-own-court-pair"] += 1
                continue
            st["items"] += 1
            st["items:" + reason] += 1
            lw0, lw1 = max(r["w0"], r["s0"] - 400), min(r["w1"], r["s1"] + 400)
            item = {"id": f"{n}:{r['s0']}", "n": n, "sha": d["sha"], "date": zd, "by": ctx.desc(n), "part": r["part"],
                    "sec": r["sec"], "fam": r["fam"], "why": "implicit:" + reason, "s0": r["s0"], "s1": r["s1"],
                    "lw0": lw0, "lw1": lw1, "w0": r["w0"], "w1": r["w1"], "w": r["w"], "len": d["len"],
                    "targets": [{"node": j, "ev": ev, "at": at, "rank": rk[0], "date": int(ctx.date[j]),
                                 "court_id": int(ctx.court[j]), **ctx.desc(j)} for j, ev, at, rk in tg],
                    "pros": [], "tier": ctx.tier.get(zc, "T"), "court_id": zc}
            fi.write(json.dumps(item, ensure_ascii=False) + "\n")
        fi.close()
        os.replace(outp + ".items.jsonl.gz.part", outp + ".items.jsonl.gz")
        with open(outp + ".stats.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(st, f, indent=0)
        print(repo, dict(st), flush=True)


def certify(a):
    from certify import find_quote, clean, PART_OUT
    from certify2 import evidence_in
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
    index = {}
    for line in open(os.path.join(a.answers, "index.tsv"), encoding="utf-8"):
        i, repo, pack = line.rstrip("\n").split("\t")
        index[i] = repo
    need = collections.defaultdict(set)
    for i in ans:
        if i in index:
            need[index[i]].add(i)
    items = {}
    for repo, ids in need.items():
        for line in gzip.open(os.path.join(a.res, repo + ".items.jsonl.gz"), "rt", encoding="utf-8"):
            it = json.loads(line)
            if it["id"] in ids:
                items[it["id"]] = it
    idx = {}
    for line in open(os.path.join(os.path.dirname(DATA), "..", "graph", "cite_index.tsv"), encoding="utf-8"):
        k, v = line.rstrip("\n").split("\t")
        idx[k] = int(v)
    explicit = set()   # (Y, X) pairs the explicit reader already has, any status-changing kind
    for b in a.base:
        for line in open(b, encoding="utf-8"):
            f = line.split("\t", 8)
            if f[7] == "1" and f[4] in ("overruled", "disapproved", "recededFrom", "abrogated"):
                explicit.add((int(f[1]), int(f[2])))
    os.makedirs(a.out, exist_ok=True)
    st = collections.Counter()
    st["answers"], st["index_items"] = len(ans), len(index)
    rows, certs = {}, {}
    rej = open(os.path.join(a.out, "implicit_rejects.tsv"), "w", encoding="utf-8", newline="\n")
    for i, r in ans.items():
        it = items.get(i)
        if it is None:
            continue
        if not r.get("states"):
            st["not-a-statement"] += 1
            rej.write(f"{i}\tmodel\tnot-a-statement\n")
            continue

        def pick(v):
            return it["targets"][int(v[1:]) - 1] if isinstance(v, str) and re.fullmatch(r"T\d+", v) and \
                1 <= int(v[1:]) <= len(it["targets"]) else None
        x, y = pick(r.get("x")), pick(r.get("y"))
        if x is None or y is None or x["node"] == y["node"]:
            st["no-x-or-y"] += 1
            rej.write(f"{i}\tmodel\tno-x-or-y\n")
            continue
        if not (x["date"] and y["date"] and x["date"] <= y["date"] <= it["date"]) or y["node"] == it["n"]:
            st["dates"] += 1
            rej.write(f"{i}\tcert\tdates\n")
            continue
        if y["court_id"] != it["court_id"]:
            st["y-not-own-court"] += 1
            rej.write(f"{i}\tcert\ty-not-own-court\n")
            continue
        if (y["node"], x["node"]) in explicit:
            st["explicit-row-exists"] += 1
            rej.write(f"{i}\tcert\texplicit-row-exists\n")
            continue
        lw = it["w"][it["lw0"] - it["w0"]:it["lw1"] - it["w0"]]
        pos = find_quote(lw, r.get("quote") or "", it["s0"] - it["lw0"])
        if pos is None or pos[1] - pos[0] > 600:
            pos = (it["s0"] - it["lw0"], it["s1"] - it["lw0"])
            st["quote-fallback-sentence"] += 1
        q0, q1 = pos
        quote = lw[q0:q1]
        kind = r.get("kind") if r.get("kind") in ("overruled", "abrogated", "disapproved") else None
        if kind is None:
            kind = next((k for c, k in KIND_OF if c in quote.lower()), None)
        cue = {"overruled": "overrul", "abrogated": "abrogat", "disapproved": "disapprov"}.get(kind)
        if cue is None or cue not in quote.lower():
            st["no-cue"] += 1
            rej.write(f"{i}\tcert\tno-cue\n")
            continue
        cut = 0
        if any(p in quote.lower() for p in rules2.DISQUAL2):
            m = BY_CUT.search(quote)
            if m and cue in quote[:m.end()].lower():
                q1 = q0 + m.end()
                quote = lw[q0:q1]
                cut = 1
            if any(p in quote.lower() for p in rules2.DISQUAL2):
                st["disqualifier"] += 1
                rej.write(f"{i}\tcert\tdisqualifier-in-quote\n")
                continue
        start, end = it["lw0"] + q0, it["lw0"] + q1
        st0, en0 = max(it["w0"], start - 400), min(it["w1"], end + 400, it["len"])
        window = it["w"][st0 - it["w0"]:en0 - it["w0"]]
        ex, ey = evidence_in(x, window, idx), evidence_in(y, window, idx)
        if ex is None or ey is None:
            st["evidence"] += 1
            rej.write(f"{i}\tcert\tevidence-out-of-window\n")
            continue
        scope = r.get("scope") if r.get("scope") in ("all", "partialUnknown", "otherGrounds") else "partialUnknown"
        try:
            conf = max(0.0, min(1.0, float(r.get("confidence", 0.5))))
        except (TypeError, ValueError):
            conf = 0.5
        key = (y["node"], x["node"])
        row = {"z": it["n"], "x": x["node"], "y": y["node"], "date": it["date"], "kind": kind, "scope": scope,
               "sha": it["sha"], "start": start, "end": end, "quote": clean(quote), "ev": ex, "evy": ey,
               "part": PART_OUT.get(it["part"], "unknown"), "conf": conf, "item": i, "cut": cut,
               "win": (it["sha"], st0, en0, clean(window)), "why": it["why"]}
        # one row per (Y, X): prefer an uncut quote, then the earliest statement
        old = rows.get(key)
        if old is None or (row["cut"], row["date"]) < (old["cut"], old["date"]):
            rows[key] = row
        st["statements"] += 1
    rej.close()
    out = sorted(rows.values(), key=lambda t: (t["z"], t["x"], t["start"]))
    with open(os.path.join(a.out, "treatments_implicit.tsv"), "w", encoding="utf-8", newline="\n") as fo, \
            open(os.path.join(a.out, "treatments_items_implicit.tsv"), "w", encoding="utf-8", newline="\n") as fi, \
            open(os.path.join(a.out, "cert_text_implicit.tsv"), "w", encoding="utf-8", newline="\n") as fc:
        seen = set()
        for t in out:
            tid = f"ti:{t['z']}:{t['x']}:{t['start']}:{t['y']}"
            fo.write("\t".join(map(str, [tid, t["z"], t["x"], t["date"], t["kind"], t["scope"], "unknown", 0, t["sha"],
                                         t["start"], t["end"], t["quote"], t["ev"], t["part"],
                                         "claude-subagent:implicit", f"{t['conf']:.2f}"])) + "\n")
            fi.write(f"{tid}\t{t['item']}\t{'quote-cut-before-by' if t['cut'] else 'quote'}\t{t['why']};by={t['y']};"
                     f"byEvidence={t['evy']}\n")
            if t["win"][:3] not in seen:
                seen.add(t["win"][:3])
                fc.write("\t".join(map(str, t["win"])) + "\n")
    st["rows"] = len(out)
    st["rows_quote_cut"] = sum(t["cut"] for t in out)
    st["by_kind_scope"] = {f"{k}|{s}": v for (k, s), v in sorted(collections.Counter(
        (t["kind"], t["scope"]) for t in out).items())}
    with open(os.path.join(a.out, "implicit_stats.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, indent=1)
    print(json.dumps(st, indent=0))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resolve")
    r.add_argument("--cand", default=os.path.join(WORK, "cand2"))
    r.add_argument("--out", default=os.path.join(WORK, "res_implicit"))
    r.add_argument("--tiers", default="L")
    r.add_argument("repos", nargs="*")
    c = sub.add_parser("certify")
    c.add_argument("--answers", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--res", default=os.path.join(WORK, "res_implicit"))
    c.add_argument("--base", action="append", default=[])
    c3 = sub.add_parser("certify3")  # round 3 witness rows: implicit_witness.py
    c3.add_argument("--answers", required=True)
    c3.add_argument("--items", required=True)
    c3.add_argument("--out", required=True)
    c3.add_argument("--base", action="append", default=[])
    a = ap.parse_args()
    if a.cmd == "resolve":
        resolve(a)
    elif a.cmd == "certify3":
        from implicit_witness import certify3
        certify3(a)
    else:
        certify(a)


if __name__ == "__main__":
    main()
