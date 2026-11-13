"""Second stage: cheap filters, target candidates, same-case history targets.

    python -X utf8 resolve.py [repo ...]      (default: every scanned repo without a resolve output)

For each data/reader_work/cand/<repo>.jsonl.gz writes data/reader_work/res/<repo>.*:
  items.jsonl.gz   treatment candidates for the model: the sentence, its +-400 window, the resolved target candidates
                   (citations in the window via graph/cite_index.tsv; case names of the decisions this decision cites,
                   as v1 did), prospectivity sentences of the decision, and the +-800 text needed for certificates
  rejects.tsv.gz   candidate id, reason (cheap-filter rejections; nothing goes to the model)
  hist.jsonl.gz    same-case history rows with a validated target (pre-certificate)
  stats.json
Inputs: the reader's own candidates, graph/{cite_index,nodes,courts}.tsv, lean-in-v3/courts.tsv (tiers). Never
events_v3/reports.tsv or lean-in-v3/reports.tsv.
"""
import gzip, json, os, re, sys, collections, glob

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, WORK, name_tokens  # noqa: E402
import rules  # noqa: E402

TIER_RANK = {"L": 3, "A": 2, "B": 2, "D": 2, "T": 1, "S": 1}
HIST_KIND = {"affirm": "affirmed", "affirmed": "affirmed", "reverse": "reversed", "reversed": "reversed",
             "vacate": "vacated", "vacated": "vacated", "modify": "modified", "modified": "modified",
             "set aside": "vacated", "quashed": "vacated", "annulled": "vacated", "withdraw": "withdrawn",
             "withdrawn": "withdrawn", "reinstate": "reinstated", "reinstated": "reinstated",
             "reversed and remanded": "reversed", "vacated and remanded": "vacated", "affirmed in part": "reversed",
             "reversed in part": "reversed", "affirmed as modified": "modified", "writ refused": "writRefused",
             "writ of error refused": "writRefused", "writ ref'd": "writRefused", "writ of error ref'd": "writRefused"}
TEXAS = 43  # v1 system index: "writ refused" (S-TX-3) is a Texas Supreme Court notation only
WRIT_NRE = re.compile(r"[\s,;]*(?:n\.\s?r\.\s?e\b|no\s+reversible\s+error)", re.I)
SAME_COURT_KINDS = {"withdrawn", "reinstated", "rehearingEnBancGranted"}
SAME_COURT_WORDS = {
    "withdrawn": re.compile(r"\b(?:opinion|decision|judgment|mandate)s?\b[^.]{0,120}\bwithdr|\bwithdraw\w*\s+(?:our|the|its|this\s+"
                            r"court's)\s+(?:\w+\s+){0,3}(?:opinion|decision|mandate)", re.I),
    "reinstated": re.compile(r"\b(?:opinion|decision|decree|judgment\s+of\s+this\s+court|our\s+(?:former|prior|original|"
                             r"earlier)\s+\w+)\b[^.]{0,120}\breinstat", re.I),
    "rehearingEnBancGranted": re.compile(r"^(?!.*\b(?:suggest\w*|extend\s+the\s+time|motion\s+to\s+extend|whether)\b)"
                                         r".*rehearing\s+en\s+banc\s+(?:is\s+|be\s+|was\s+)?(?:hereby\s+)?granted", re.I)}
BODY_RX = [
    ("agency", re.compile(r"\b(?:board|commission|commissioner|agency|secretary|administrative|hearing\s+officer|"
                          r"arbitrators?|award|referee|department|director|bureau)\b", re.I)),
    ("appellate", re.compile(r"\b(?:court\s+of\s+(?:civil\s+|criminal\s+)?appeals?|appellate\s+(?:division|court|"
                             r"department|term)|appeals\s+court|circuit\s+court\s+of\s+appeals|district\s+court\s+of\s+"
                             r"appeal|C\.\s?A\.|commonwealth\s+court|intermediate)\b", re.I)),
    ("trial", re.compile(r"\b(?:district\s+court|bankruptcy\s+(?:court|judge)|trial\s+(?:court|judge)|circuit\s+court|"
                         r"superior\s+court|county\s+court|family\s+court|surrogate|chancery|chancellor|court\s+of\s+claims|"
                         r"tax\s+court|municipal\s+court|justice\s+court|magistrate|probate\s+court|juvenile\s+court|"
                         r"court\s+of\s+common\s+pleas|law\s+division|chancery\s+division|special\s+term)\b", re.I)),
]


def body_named(sent, at):
    """Which kind of body the disposition sentence says it is acting on (the mention nearest the verb), or ''."""
    best, dist = "", 10 ** 9
    for name, rx in BODY_RX:
        for m in rx.finditer(sent):
            d = abs(m.start() - at)
            if d < dist:
                best, dist = name, d
    return best


def court_class(name, tier):
    n = name.lower()
    if tier in ("A", "B", "D") or re.search(r"appeal|appellate|commonwealth court", n):
        return "appellate"
    if tier == "L":
        return "last"
    return "trial"


CITE_HIST_BEFORE = re.compile(r"\b(?:aff'd|rev'd|cert\.|see|cf\.|writ|petition)\s*,?\s*$", re.I)
GENERIC = re.compile(r"\b(?:is|are|will\s+be|must\s+be|should\s+be)\s+(?:\w+\s+)?(?:affirmed|reversed|vacated|modified)\s+"
                     r"(?:when|if|where|only|unless|whenever|on\s+appeal\s+(?:when|if|only))\b|\b(?:may|can|could|might|would)\s+"
                     r"(?:\w+\s+){0,2}(?:affirm|reverse|vacate)\b|\bif\s+we\s+(?:affirm|reverse|vacate)|"
                     r"\b(?:asks?|urges?|requests?|asking|urging|seeks?)\s+(?:us|this\s+court)\s+to\s+(?:affirm|reverse|vacate)", re.I)


class Ctx:
    def __init__(self):
        g = os.path.join(W, "graph")
        self.idx = {}
        for line in open(os.path.join(g, "cite_index.tsv"), encoding="utf-8"):
            k, v = line.rstrip("\n").split("\t")
            self.idx[k] = int(v)
        self.names = []
        self.cites0 = []
        for line in open(os.path.join(g, "nodes.tsv"), encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            self.names.append(f[6])
            self.cites0.append(f[5].split("|")[0] if f[5] else "")
        self.date = np.load(os.path.join(WORK, "node_date.npy"))
        self.court = np.load(os.path.join(WORK, "node_court.npy"))
        self.indptr = np.load(os.path.join(WORK, "cites_indptr.npy"))
        self.cidx = np.load(os.path.join(WORK, "cites_idx.npy"))
        self.court_name = {}
        for line in open(os.path.join(g, "courts.tsv"), encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            self.court_name[int(f[0])] = f[1]
        # tier and system per graph court id, joined by court name (lean-in-v3 uses its own ids)
        by_name = {}
        for line in open(os.path.join(W, "lean-in-v3", "courts_named.tsv"), encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            by_name[f[1]] = (f[5], int(f[4]))
        self.tier, self.system = {}, {}
        for cid, nm in self.court_name.items():
            t, s = by_name.get(nm, ("T", -1))
            self.tier[cid], self.system[cid] = t, s
        self._tok = {}

    def toks(self, j):
        t = self._tok.get(j)
        if t is None:
            t = name_tokens(self.names[j])
            if len(self._tok) > 2_000_000:
                self._tok.clear()
            self._tok[j] = t
        return t

    def cited(self, n):
        return self.cidx[self.indptr[n]:self.indptr[n + 1]]

    def rank(self, j):
        return TIER_RANK.get(self.tier.get(int(self.court[j]), "T"), 1)

    def desc(self, j):
        return {"name": self.names[j][:160], "court": self.court_name.get(int(self.court[j]), "?"),
                "year": int(self.date[j]) // 10000, "cite": self.cites0[j]}


CAPWORD = re.compile(r"\b[A-Z][a-z][A-Za-z'\-]{2,}")


def treatment_targets(ctx, n, c, d_date):
    """Resolved target candidates for one treatment candidate: [(node, evidence, abs_offset, rank)]."""
    s0, s1 = c["s0"], c["s1"]
    lw0, lw1 = max(c["w0"], s0 - 400), min(c["w1"], s1 + 400)
    verb = c["m"][0][0]
    out = {}
    for o0, o1, key in c["c"]:
        if not (lw0 <= o0 and o1 <= lw1):
            continue
        j = ctx.idx.get(key)
        if j is None or j == n:
            continue
        if ctx.date[j] > d_date and d_date:
            continue
        r = (0 if s0 <= o0 < s1 else 2, abs(o0 - verb))
        if j not in out or r < out[j][3]:
            out[j] = (j, "cite:" + key, o0, r)
    w = c["w"]
    win = w[lw0 - c["w0"]:lw1 - c["w0"]]
    words = {}
    for m in CAPWORD.finditer(win):
        words.setdefault(m.group(0), []).append(lw0 + m.start())
    if words:
        for j in ctx.cited(n):
            j = int(j)
            if j == n or j in out:
                continue
            tk = ctx.toks(j)
            hit = None
            for t in tk:
                for pos in words.get(t, ()):
                    r = (1 if s0 <= pos < s1 else 3, abs(pos - verb))
                    if hit is None or r < hit[3]:
                        hit = (j, "name:" + t, pos, r)
            if hit:
                out[j] = hit
    return sorted(out.values(), key=lambda x: x[3])[:8]


def hist_rows(ctx, n, d, hs, st):
    """Validated same-case history rows of one decision."""
    rows = []
    by_t = ctx.toks(n)
    by_date = int(ctx.date[n])
    by_court = int(ctx.court[n])
    for h in hs:
        sent = h["w"][h["s0"] - h["w0"]:h["s1"] - h["w0"]]
        k = h["k"]
        if k in ("denied", "granted", "dismissed"):
            s_low = sent.lower()
            if "en banc" in s_low and k == "granted":
                kind = "rehearingEnBancGranted"
            elif "certiorari" in s_low or "review" in s_low or "leave to appeal" in s_low:
                kind = {"denied": "certDenied", "granted": "reviewGranted", "dismissed": "reviewDismissed"}[k]
            else:
                st["hist_other_k"] += 1
                continue
        elif k.startswith(("depublished", "not")):
            kind = "depublished"
        elif k.startswith("writ") and WRIT_NRE.search(k):
            st["hist_writ_nre"] += 1  # "writ ref'd n.r.e." is not writRefused (S-TX-3)
            continue
        else:
            kind = HIST_KIND.get(k)
            if kind is None:
                st["hist_unknown_kind"] += 1
                continue
        if GENERIC.search(sent):
            st["hist_generic"] += 1
            continue
        # citation-string history of some other decision ("..., 12 Alaska 584, affirmed, 191 F.2d 262, certiorari
        # denied 342 U.S. 913") is a note about another case, not this court's own disposition
        mo = h["m"][0] - h["w0"]
        if (rules.CITATOR_BEFORE.search(h["w"], max(0, mo - 40), mo)
                or CITE_HIST_BEFORE.search(h["w"], max(0, mo - 15), mo)):
            st["hist_citation_string"] += 1
            continue
        if kind == "writRefused" and not re.match(r"\s*(?:the\s+)?(?:application\s+for\s+)?writ", sent, re.I):
            st["hist_writ_note"] += 1
            continue
        if kind == "writRefused":
            # "writ refused, n.r.e." / "writ ref'd n.r.e." (no reversible error) does not approve the opinion (S-TX-3);
            # "writ denied" / "writ dismissed" never reach writRefused
            mo1 = h["m"][1] - h["w0"]
            if WRIT_NRE.search(k) or WRIT_NRE.match(h["w"][mo1:mo1 + 40]):
                st["hist_writ_nre"] += 1
                continue
        if h["part"] in ("headmatter",):
            st["hist_headmatter"] += 1
            continue
        if kind in SAME_COURT_KINDS and not SAME_COURT_WORDS[kind].search(sent):
            st["hist_samecourt_wording"] += 1
            continue
        body = body_named(sent, h["m"][0] - h["s0"])
        if body == "agency":
            st["hist_agency_reviewed"] += 1
            continue
        partial = bool(re.search(r"\bin\s+part\b|\bas\s+modified\b|\bbut\s+(?:reverse|vacate|affirm)", sent, re.I))
        best = None
        by_sys = ctx.system.get(by_court, -1)
        if kind == "writRefused" and by_sys != TEXAS:
            # e.g. the Louisiana Supreme Court's "Writ refused." on a court-of-appeal judgment: a refusal to review,
            # not the Texas notation (courts_validation.md, limit 9); kept as `other`
            kind = "other"
            st["hist_writ_not_texas"] += 1
        for o0, o1, key in h["tc"]:
            j = ctx.idx.get(key)
            if j is None or j == n:
                continue
            jd = int(ctx.date[j])
            if not jd or jd > by_date or by_date - jd > 80000:
                continue
            shared = ctx.toks(j) & by_t
            if not shared or (len(shared) < 2 and min(len(ctx.toks(j)), len(by_t)) > 1):
                continue  # same case: two shared party tokens, or one when a name has only one
            jc = int(ctx.court[j])
            j_sys = ctx.system.get(jc, -1)
            if kind in SAME_COURT_KINDS:
                if jc != by_court:
                    continue
            else:
                if jc == by_court or ctx.rank(j) > ctx.rank(n):
                    continue
                # no review across systems, except the Supreme Court over state courts (federal habeas is a new case)
                if j_sys != by_sys and not ctx.court_name.get(by_court, "").startswith("Supreme Court of the United"):
                    continue
                if body and court_class(ctx.court_name.get(jc, ""), ctx.tier.get(jc, "T")) != body:
                    continue
            r = (-ctx.rank(j), -jd)
            if best is None or r < best[0]:
                best = (r, j, key, o0, o1)
        if best is None:
            st["hist_no_valid_target"] += 1
            continue
        _, j, key, o0, o1 = best
        mode = h["mode"]
        q0, q1 = h["q0"], h["q1"]
        if mode == "remote":
            # same-case name evidence inside the window, if any
            shared = ctx.toks(j) & by_t
            win = h["w"]
            tok = next((t for t in sorted(shared) if re.search(r"\b" + re.escape(t) + r"\b", win)), None)
            if tok is None:
                st["hist_remote_no_evidence"] += 1
                rows.append({"remote": 1, "n": n, "j": j, "kind": kind, "key": key})
                continue
            ev = "name:" + tok
        else:
            if mode == "win" and not (h["w0"] <= o0 and o1 <= h["w1"]):
                # the chosen target's cite is not the in-window one: fall back to name evidence
                shared = ctx.toks(j) & by_t
                tok = next((t for t in sorted(shared) if re.search(r"\b" + re.escape(t) + r"\b", h["w"])), None)
                if tok is None:
                    st["hist_remote_no_evidence"] += 1
                    rows.append({"remote": 1, "n": n, "j": j, "kind": kind, "key": key})
                    continue
                ev = "name:" + tok
            else:
                ev = "cite:" + key
        rows.append({"n": n, "j": j, "kind": kind, "scope": "unknown" if partial else "all", "q0": q0, "q1": q1,
                     "w0": h["w0"], "w1": h["w1"], "w": h["w"], "ev": ev, "part": h["part"], "mode": mode,
                     "k": k, "sha": d["sha"], "date": by_date})
        st["hist_rows_" + mode] += 1
    # one row per (target, kind); the last disposition sentence wins; mixed affirm/reverse -> scope unknown
    by_target = collections.defaultdict(list)
    for r in rows:
        if "remote" not in r:
            by_target[r["j"]].append(r)
    out = []
    for j, rs in by_target.items():
        kinds = {r["kind"] for r in rs}
        last = {}
        for r in rs:
            last[r["kind"]] = r
        for kind, r in last.items():
            if len(kinds & {"affirmed", "reversed", "vacated", "modified"}) > 1 and kind in ("affirmed", "reversed",
                                                                                               "vacated", "modified"):
                r["scope"] = "unknown"
            out.append(r)
    return out, [r for r in rows if "remote" in r]


def main(repos):
    ctx = Ctx()
    os.makedirs(os.path.join(WORK, "res"), exist_ok=True)
    for repo in repos:
        src = os.path.join(WORK, "cand", repo + ".jsonl.gz")
        outp = os.path.join(WORK, "res", repo)
        if not os.path.exists(src) or os.path.exists(outp + ".stats.json"):
            continue
        st = collections.Counter()
        fi = gzip.open(outp + ".items.jsonl.gz.part", "wt", encoding="utf-8", newline="\n")
        fr = gzip.open(outp + ".rejects.tsv.gz.part", "wt", encoding="utf-8", newline="\n")
        fh = gzip.open(outp + ".hist.jsonl.gz.part", "wt", encoding="utf-8", newline="\n")
        d = None
        hs = []

        def flush_hist():
            if d is not None and hs:
                rows, remote = hist_rows(ctx, d["n"], d, hs, st)
                for r in rows:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                st["hist_remote_rows"] += len(remote)

        for line in gzip.open(src, "rt", encoding="utf-8"):
            r = json.loads(line)
            t = r["t"]
            if t == "d":
                flush_hist()
                d, hs = r, []
                continue
            if t == "h":
                hs.append(r)
                st["hist_cand"] += 1
                continue
            st["cand"] += 1
            n = r["n"]
            cid = f"{n}:{r['s0']}"
            sent = r["w"][r["s0"] - r["w0"]:r["s1"] - r["w0"]]
            verdict, reason = rules.classify(sent, r["fam"], r["part"])
            if verdict == "reject":
                st["reject:" + reason] += 1
                fr.write(f"{cid}\t{reason}\t{'+'.join(r['fam'])}\n")
                continue
            tg = treatment_targets(ctx, n, r, int(ctx.date[n]))
            fam0 = reason.split(":")[0]
            if fam0 in ("limit", "question", "declineFollow") or (fam0 == "repudiate" and not reason.endswith("nolonger")):
                tg = [t for t in tg if t[3][0] <= 1]  # soft kinds: the target must be named in the sentence itself
            if not tg:
                st["reject:no-target"] += 1
                fr.write(f"{cid}\tno-target\t{'+'.join(r['fam'])}\n")
                continue
            st["llm"] += 1
            st["llm:" + reason] += 1
            lw0, lw1 = max(r["w0"], r["s0"] - 400), min(r["w1"], r["s1"] + 400)
            item = {"id": cid, "n": n, "sha": d["sha"], "date": int(ctx.date[n]), "by": ctx.desc(n), "part": r["part"],
                    "sec": r["sec"], "fam": r["fam"], "why": reason, "s0": r["s0"], "s1": r["s1"], "lw0": lw0, "lw1": lw1,
                    "w0": r["w0"], "w1": r["w1"], "w": r["w"], "len": d["len"],
                    "targets": [{"node": j, "ev": ev, "at": at, **ctx.desc(j)} for j, ev, at, _ in tg],
                    "pros": d.get("pros", [])}
            fi.write(json.dumps(item, ensure_ascii=False) + "\n")
        flush_hist()
        for f in (fi, fr, fh):
            f.close()
        for ext in ("items.jsonl.gz", "rejects.tsv.gz", "hist.jsonl.gz"):
            os.replace(outp + "." + ext + ".part", outp + "." + ext)
        with open(outp + ".stats.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(st, f, indent=0)
        print(repo, st["cand"], "cand ->", st["llm"], "llm;", st["hist_cand"], "hist cand ->",
              sum(v for k, v in st.items() if k.startswith("hist_rows_")), "hist rows", flush=True)


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(os.path.basename(f)[:-9] for f in glob.glob(os.path.join(WORK, "cand", "*.jsonl.gz")))
    main(names)
