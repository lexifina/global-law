"""Round 2 second stage: candidates that v1 rejected by rule but that carry a round-2 act shape (rules2), and v1
act-shaped candidates that had no resolvable target, with wider target resolution.

    python -X utf8 resolve2.py [--cand DIR] [--out DIR] [repo ...]

Reads data/reader_work/cand2/<repo>.jsonl.gz (scan2: v1 and round-2 families, round-2 part map), skips every
candidate the v1 model stage already read (res/<repo>.items.jsonl.gz), and writes
<out>/<repo>.items.jsonl.gz in the v1 item format (classify.render reads it) plus `v2` = why it is read now.
Nothing is read from gold/, events_v3/reports.tsv or lean-in-v3/reports.tsv.

Target resolution added here (v1: citations in the +-400 window through graph/cite_index.tsv, and one distinctive
party-name word of a decision this decision cites):
  * party-name phrases: two or more consecutive capitalised words of a cited decision's caption ("Union Gas",
    "National League", "Carter Coal") found in the window, for captions whose single words are all too common;
  * wide window: when the sentence itself names no case (it says "that case", "the former decision", "those cases",
    "it"), citations and names in the 800 characters before the sentence are candidates too; the certificate window
    then runs from the citation to the quote, so the checker sees the target evidence.
"""
import argparse, collections, glob, gzip, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CITE_RX, WORK, cite_key, dehyphen_norm, short_name_tokens  # noqa: E402
import rules, rules2  # noqa: E402
from resolve import Ctx, treatment_targets, CAPWORD  # noqa: E402

GENERIC_PHRASE = re.compile(r"^(?:United States|New York|New Jersey|New Mexico|New Hampshire|North Carolina|"
                            r"South Carolina|North Dakota|South Dakota|West Virginia|Rhode Island|District Columbia|"
                            r"Supreme Court|District Court|Circuit Court|Court Appeals|Interstate Commerce|"
                            r"Commerce Commission|Internal Revenue|Attorney General|City Council|School District|"
                            r"Board Education|County Commissioners|Insurance Company|Railroad Company|Railway Company|"
                            r"National Bank|First National|Los Angeles|San Francisco|St Louis|New Orleans|Kansas City|"
                            r"Tax Commission|Labor Board|National Labor|Labor Relations|Public Service|"
                            r"Service Commission|Industrial Commission|Federal Trade|Trade Commission)$")
PHRASE = re.compile(r"\b[A-Z][A-Za-z'’\-]+(?:\s+(?:&\s+)?[A-Z][A-Za-z'’\-]+){1,2}")
ANAPHORA = re.compile(r"\b(?:that|this|the\s+(?:former|latter|earlier|prior|first|second|last|above|cited|same)|said|such)\s+"
                      r"(?:case|decision|opinion|ruling|holding|authority|doctrine)|\b(?:those|these|such|the\s+(?:former|"
                      r"earlier|prior|above|cited))\s+(?:cases|decisions|opinions|rulings|holdings|authorities)|"
                      r"\b(?:it|they)\s+(?:is|are|must|should)\b|\bsupra\b", re.I)
_phr = {}


def phrases(ctx, j):
    p = _phr.get(j)
    if p is None:
        p = []
        nm = re.sub(r"\(.*?\)", " ", ctx.names[j] or "")
        for side in re.split(r"\s+v\.?\s+|\s+vs\.?\s+", nm):
            side = re.sub(r"[.,]", "", side)
            for m in PHRASE.finditer(side):
                ph = m.group(0)
                if GENERIC_PHRASE.match(ph) or len(ph) < 7:
                    continue
                p.append(ph)
                if len(ph.split()) == 3:
                    p.append(" ".join(ph.split()[:2]))
                    if GENERIC_PHRASE.match(p[-1]):
                        p.pop()
        if len(_phr) > 500_000:
            _phr.clear()
        _phr[j] = p
    return p


def targets2(ctx, n, c, d_date):
    """v1 targets, then party-name phrases, then (wide) citations and names before the sentence.
    [(node, evidence, abs_offset, rank)], rank[0]: 0 cite in sentence, 1 name in sentence, 2 cite in +-400,
    3 name in +-400, 4 wide."""
    out = {t[0]: t for t in treatment_targets(ctx, n, c, d_date)}
    s0, s1 = c["s0"], c["s1"]
    lw0, lw1 = max(c["w0"], s0 - 400), min(c["w1"], s1 + 400)
    verb = c["m"][0][0]
    w = c["w"]
    win = w[lw0 - c["w0"]:lw1 - c["w0"]].replace(".", "").replace(",", "")
    cited = [int(j) for j in ctx.cited(n)]
    if len(cited) <= 1500:
        for j in cited:
            if j == n or j in out or (d_date and ctx.date[j] > d_date):
                continue
            for ph in phrases(ctx, j):
                i = win.find(ph)
                if i >= 0:
                    # offsets are approximate after punctuation stripping; the rank only orders candidates
                    pos = lw0 + i
                    out[j] = (j, "name:" + ph, pos, (1 if s0 <= pos < s1 else 3, abs(pos - verb)))
                    break
    sent = w[s0 - c["w0"]:s1 - c["w0"]]
    # round 3: three-letter party names ("Roe", "Lee") of cited decisions, in the sentence itself only
    short = set(re.findall(r"\b[A-Z][a-z]{2}\b", sent))
    if short and len(cited) <= 1500:
        for j in cited:
            if j == n or j in out or (d_date and ctx.date[j] > d_date):
                continue
            for t in short_name_tokens(ctx.names[j]):
                if t in short:
                    pos = s0 + re.search(r"\b" + t + r"\b", sent).start()
                    out[j] = (j, "name:" + t, pos, (1, abs(pos - verb)))
                    break
    named = any(t[3][0] <= 1 for t in out.values())
    if not named and ANAPHORA.search(sent):
        a0 = c["w0"]
        pre = w[0:lw0 - c["w0"]]
        for m in CITE_RX.finditer(pre):
            k = cite_key(m)
            j = ctx.idx.get(k) if k else None
            if j is None or j == n or j in out or (d_date and ctx.date[j] > d_date):
                continue
            out[j] = (j, "cite:" + k, a0 + m.start(), (4, abs(a0 + m.start() - verb)))
        words = {}
        for m in CAPWORD.finditer(pre):
            words.setdefault(m.group(0), []).append(a0 + m.start())
        if words and len(cited) <= 1500:
            for j in cited:
                if j == n or j in out or (d_date and ctx.date[j] > d_date):
                    continue
                for t in ctx.toks(j):
                    if t in words:
                        pos = words[t][-1]
                        out[j] = (j, "name:" + t, pos, (4, abs(pos - verb)))
                        break
    if not named and ANAPHORA.search(sent):
        # "that case", "they", "those decisions": the antecedent is before the sentence; nearest first, and the
        # citations after the sentence (authority for the new rule) last
        return sorted(out.values(), key=lambda x: (0 if x[2] < s0 else 1, abs(x[2] - verb)))[:12]
    return sorted(out.values(), key=lambda x: x[3])[:10]


class Ctx3(Ctx):
    """Round 3: for a decision with no edges in the graph (hard-wrapped CourtListener texts), the cited decisions
    are the citations of its own text (scan `tc`), resolved through graph/cite_index.tsv."""
    extra = {}

    def cited(self, n):
        e = self.extra.get(int(n))
        if e is not None:
            return e
        return Ctx.cited(self, n)

    def set_text_cites(self, n, keys):
        base = [int(j) for j in Ctx.cited(self, n)]
        if base:
            self.extra = {}
            return
        d = int(self.date[n])
        js = {self.idx[k] for k in keys if k in self.idx}
        self.extra = {int(n): sorted(j for j in js if j != n and not (d and self.date[j] > d))}


V1FAMS = ("overrule", "disapprove", "recede", "abrogate", "supersede", "limit", "question", "declineFollow", "repudiate")
SKIP_PART = ("dissent", "concurrence", "headmatter", "front", "title", "unknown")


def v1_item_ids(repo):
    """Ids the v1 model stage already read (data/reader_work/res/<repo>.items.jsonl.gz)."""
    ids = set()
    f = os.path.join(WORK, "res", repo + ".items.jsonl.gz")
    if os.path.exists(f):
        for line in gzip.open(f, "rt", encoding="utf-8"):
            i = line.find('"id": "') + 7
            ids.add(line[i:line.index('"', i)])
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", default=os.path.join(WORK, "cand2"))
    ap.add_argument("--out", default=os.path.join(WORK, "res2"))
    ap.add_argument("repos", nargs="*")
    a = ap.parse_args()
    ctx = Ctx3()
    os.makedirs(a.out, exist_ok=True)
    repos = a.repos or sorted(os.path.basename(f)[:-9] for f in glob.glob(os.path.join(a.cand, "*.jsonl.gz")))
    for repo in repos:
        src = os.path.join(a.cand, repo + ".jsonl.gz")
        outp = os.path.join(a.out, repo)
        if not os.path.exists(src) or os.path.exists(outp + ".stats.json"):
            continue
        seen = v1_item_ids(repo)
        st = collections.Counter()
        fi = gzip.open(outp + ".items.jsonl.gz.part", "wt", encoding="utf-8", newline="\n")
        d = None
        for line in gzip.open(src, "rt", encoding="utf-8"):
            r = json.loads(line)
            if r["t"] == "d":
                d = r
                if d.get("tc") is not None:
                    ctx.set_text_cites(d["n"], d["tc"])
                continue
            if r["t"] != "c":
                continue
            part = r["part"]
            if part.startswith(SKIP_PART):
                continue
            n = r["n"]
            cid = f"{n}:{r['s0']}"
            if cid in seen:
                continue
            sent = r["w"][r["s0"] - r["w0"]:r["s1"] - r["w0"]]
            if r.get("hw"):
                sent = dehyphen_norm(sent)   # round 3: rules see "overruled", the stored window keeps "over- ruled"
            d_date = int(ctx.date[n])
            fams1 = [f for f in r["fam"] if f in V1FAMS]
            v1, reason = rules.classify(sent, fams1, part) if fams1 else ("reject", "scan")
            if v1 == "llm":
                fam0 = reason.split(":")[0]
                if fam0 in ("limit", "question", "declineFollow", "supersede") or (
                        fam0 == "repudiate" and not reason.endswith("nolonger")):
                    st["skip:soft-kind"] += 1
                    continue
                tg = treatment_targets(ctx, n, r, d_date)
                if tg:
                    why2 = "v2:part-fix:" + reason   # v1 would have read it but for the opinion part it was given
                    tg = targets2(ctx, n, r, d_date)
                else:
                    tg = targets2(ctx, n, r, d_date)
                    why2 = "v2:no-target:" + reason
            else:
                if reason not in ("not-act-shaped", "procedural", "past", "report", "scan"):
                    continue
                has_shape = bool(rules2.shapes(sent))
                if not has_shape and not (reason == "procedural" and any(
                        rules.act_shaped(sent, f) for f in fams1 if f in ("overrule", "disapprove"))):
                    continue
                tg = targets2(ctx, n, r, d_date)
                named = any(t[3][0] <= 1 for t in tg)
                v, why = rules2.classify2(sent, fams1, part, named)
                if v != "llm":
                    st["reject:" + why] += 1
                    continue
                if reason == "procedural" and not named:
                    st["reject:procedural-unnamed"] += 1
                    continue
                why2 = why + ":" + reason
            if not tg:
                st["no-target"] += 1
                continue
            st["llm"] += 1
            st["llm:" + why2] += 1
            wide = all(t[3][0] == 4 for t in tg)
            lw0 = r["w0"] if wide else max(r["w0"], r["s0"] - 400)
            lw1 = min(r["w1"], r["s1"] + 400)
            item = {"id": cid, "n": n, "sha": d["sha"], "date": d_date, "by": ctx.desc(n), "part": part,
                    "sec": r["sec"], "fam": r["fam"], "why": why2, "s0": r["s0"], "s1": r["s1"], "lw0": lw0, "lw1": lw1,
                    "w0": r["w0"], "w1": r["w1"], "w": r["w"], "len": d["len"], "wide": int(wide),
                    "targets": [{"node": j, "ev": ev, "at": at, "rank": rk[0], **ctx.desc(j)} for j, ev, at, rk in tg],
                    "hw": r.get("hw", 0), "pros": d.get("pros", []), "tier": ctx.tier.get(int(ctx.court[n]), "T"),
                    "court_id": int(ctx.court[n])}
            fi.write(json.dumps(item, ensure_ascii=False) + "\n")
        fi.close()
        os.replace(outp + ".items.jsonl.gz.part", outp + ".items.jsonl.gz")
        with open(outp + ".stats.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(st, f, indent=0)
        print(repo, dict(st), flush=True)


if __name__ == "__main__":
    main()
