"""Round 3, the `explicit = 0` tier with a WITNESS: a later binding court W states that X is no longer good law /
was overruled, abrogated or repudiated (by Y). Candidate pass over data/reader_work/cand2.

    python -X utf8 implicit3.py scan --out DIR --gold-x FILE [--procs 5]

Two modes per repo:
  directed  any repo that is not a district/trial repo: W of tier L or A, an opinion-of-the-court part, a statement
            sentence, and one of the decisions named within 300 characters is in --gold-x (the targets of the 169
            gold pairs classed "implicit, no words"; allowed for this separated tier only, BRIEF rule 5).
  general   supreme-court and ca* repos: a strict statement sentence naming two resolved decisions X, Y with
            date(X) <= date(Y) < date(W).
Items are written in the item format of resolve2.py (pack2.render reads them).
"""
import argparse, collections, glob, gzip, json, os, re, sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import WORK  # noqa: E402

STMT = re.compile(
    r"\bno\s+longer\s+(?:be\s+)?(?:regarded\s+as\s+|considered\s+(?:to\s+be\s+)?|deemed\s+)?(?:good|valid|sound|the|"
    r"controlling|binding|authoritative|viable|followed|of\s+any|has|have|retains?)\b|"
    r"\b(?:overruled|abrogated|repudiated|overturned|disapproved|discredited|superseded|undermined|eroded|abandoned|"
    r"rejected|displaced)\b|\boverruling\b|\babrogating\b|\brepudiating\b|\bsub\s+silentio\b|"
    r"\b(?:did|does|cannot|could)\s+not\s+survive\b", re.I)
STRICT = re.compile(
    r"\bno\s+longer\s+(?:good|valid|sound|the)\s+law\b|\b(?:overruled|abrogated|repudiated|overturned)\s+"
    r"(?:in\s+part\s+|sub\s+silentio\s+|implicitly\s+|on\s+other\s+grounds\s+)?(?:by|in)\b|\bsub\s+silentio\b|"
    r"\b(?:has|have|had|was|were)\s+(?:since\s+|long\s+|later\s+|subsequently\s+|effectively\s+|implicitly\s+|"
    r"impliedly\s+|been\s+){1,3}(?:overruled|abrogated|repudiated|overturned)\b|\(overruling\b", re.I)
FAMS = {"overrule", "abrogate", "question", "repudiate", "nolonger", "overturn", "survive", "disavow", "abandon",
        "supersede", "disapprove", "reject"}
SKIP_PART = ("dissent", "concurrence", "headmatter", "front", "title", "unknown")
CTX = None
GOLDX = None


def init(goldx):
    global CTX, GOLDX
    from resolve import Ctx
    CTX = Ctx()
    GOLDX = goldx


def one(arg):
    repo, cand, out = arg
    from resolve2 import targets2
    import numpy as np
    ctx = CTX
    general = repo == "supreme-court" or re.fullmatch(r"ca(?:\d+|dc|fc)", repo) is not None
    gx = np.array(sorted(GOLDX), dtype=np.int64)
    st = collections.Counter()
    outp = os.path.join(out, repo)
    fi = gzip.open(outp + ".items.jsonl.gz.part", "wt", encoding="utf-8", newline="\n")
    d = None
    keep = False
    for line in gzip.open(os.path.join(cand, repo + ".jsonl.gz"), "rt", encoding="utf-8"):
        head = line[:14]
        if '"d"' in head:
            d = json.loads(line)
            n = d["n"]
            zc = int(ctx.court[n])
            tier = ctx.tier.get(zc, "T")
            dirx = set(int(j) for j in np.intersect1d(ctx.cited(n), gx)) if tier in ("L", "A") else set()
            keep = tier in ("L", "A") and (bool(dirx) or general)
            continue
        if not keep or '"c"' not in head:
            continue
        r = json.loads(line)
        if r["t"] != "c" or not (set(r["fam"]) & FAMS) or r["part"].startswith(SKIP_PART):
            continue
        sent = r["w"][r["s0"] - r["w0"]:r["s1"] - r["w0"]]
        if not STMT.search(sent):
            continue
        n = r["n"]
        zd = int(ctx.date[n])
        tg = [t for t in targets2(ctx, n, r, zd) if t[3][0] <= 3 and r["s0"] - 300 <= t[2] <= r["s1"] + 300
              and ctx.date[t[0]] and int(ctx.date[t[0]]) < zd]
        if not tg:
            continue
        ids = {t[0] for t in tg}
        mode = None
        if ids & dirx:
            mode = "directed"
        elif general and len(tg) >= 2 and STRICT.search(sent):
            mode = "general"
        if mode is None:
            continue
        st[mode] += 1
        lw0, lw1 = max(r["w0"], r["s0"] - 400), min(r["w1"], r["s1"] + 400)
        item = {"id": f"{n}:{r['s0']}", "n": n, "sha": d["sha"], "date": zd, "by": ctx.desc(n), "part": r["part"],
                "sec": r["sec"], "fam": r["fam"], "why": "witness:" + mode, "s0": r["s0"], "s1": r["s1"],
                "lw0": lw0, "lw1": lw1, "w0": r["w0"], "w1": r["w1"], "w": r["w"], "len": d["len"],
                "targets": [{"node": int(j), "ev": ev, "at": int(at), "rank": rk[0], "date": int(ctx.date[j]),
                             "court_id": int(ctx.court[j]), **ctx.desc(j)} for j, ev, at, rk in tg],
                "pros": [], "tier": ctx.tier.get(int(ctx.court[n]), "T"), "court_id": int(ctx.court[n]),
                "strict": bool(STRICT.search(sent)), "dirx": sorted(ids & dirx)}
        fi.write(json.dumps(item, ensure_ascii=False) + "\n")
    fi.close()
    os.replace(outp + ".items.jsonl.gz.part", outp + ".items.jsonl.gz")
    return repo, dict(st)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--cand", default=os.path.join(WORK, "cand2"))
    s.add_argument("--out", required=True)
    s.add_argument("--gold-x", required=True)
    s.add_argument("--procs", type=int, default=5)
    a = ap.parse_args()
    goldx = {int(l.split()[0]) for l in open(a.gold_x) if l.strip()}
    os.makedirs(a.out, exist_ok=True)
    repos = sorted(os.path.basename(f)[:-9] for f in glob.glob(os.path.join(a.cand, "*.jsonl.gz")))
    repos = [r for r in repos if not r.endswith("-district") and "other-courts" not in r and r != "bankruptcy"
             and not os.path.exists(os.path.join(a.out, r + ".items.jsonl.gz"))]
    # big federal repos first
    repos.sort(key=lambda r: (0 if r == "supreme-court" else 1 if r.startswith("ca") and "appellate" not in r and
                              not r.startswith("cali") else 2, r))
    with Pool(a.procs, initializer=init, initargs=(goldx,)) as p:
        for repo, st in p.imap_unordered(one, [(r, a.cand, a.out) for r in repos]):
            print(repo, st, flush=True)


if __name__ == "__main__":
    main()
