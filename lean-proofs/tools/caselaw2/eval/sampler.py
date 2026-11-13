"""Samplers for the blind audits of caselaw-lean-2 (see caselaw-lean-2/eval/audit_plan.md).

    python tools/caselaw2/eval/sampler.py <audit> <n> [--seed S] [--shards K]

Audits:
  gold-notes   A: is each later-court note in gold/reports_typed.tsv read right (target, treating decision, kind,
               scope)? The packet shows the note's passage only.
  notes-blind  B: for named notes (kind overruled|abrogated|disapproved|recededFrom), the treating decision's text
               around the target, WITHOUT the note or Lean's verdict: does it overrule the target itself, and how?
  admitted     C: for treatments Lean admitted (cert ok, explicit), the treating decision's text around the quote,
               WITHOUT the reader's kind or Lean's verdict: is it this court overruling (etc.) this target, and the scope?
  rejected     D: for certificates Lean rejected, the quote and window plus the rejection reason: was it right to
               reject?
Each audit writes eval/audits/<audit>/in_<k>.json (packets for the blind readers, nothing that reveals the answer)
and key.json (what the gold/model said, for scoring after the reading). Decision texts are read from git (HEAD).
"""
import argparse, collections, json, os, random, re, subprocess, sys

W = os.path.expanduser("~/Documents/us-caselaw-lean-work")
C2 = os.path.join(W, "caselaw-lean-2")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
CNW = 0x08000000
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score import rows, iint  # noqa: E402

QUESTIONS = {
    "gold-notes": ("Read the passage. A court there writes, about an earlier decision it cites (the TARGET), what a "
                   "later decision or a law did to it. Answer: target_cite (the citation of the decision the note is "
                   "about), by_cite (the citation of the decision said to have done it, or '-' if none or a statute), "
                   "kind (overruled|abrogated|supersededByEnactment|disapproved|recededFrom|vacated|reversed|"
                   "notANote), scope (all|partialUnknown|otherGrounds), and a one-line why."),
    "notes-blind": ("Read the excerpts of DECISION (its majority opinion unless marked). Does DECISION itself, in its "
                    "own majority opinion, overrule, abrogate, disapprove or recede from TARGET? Answer verdict "
                    "(express: says so in words; implicit: rejects its holding without saying so; mentions: discusses "
                    "or cites it without negating it; absent: not mentioned in the excerpts), kind (overruled|abrogated|"
                    "disapproved|recededFrom|-), scope (all|partialUnknown|otherGrounds|-), quote (the words, ≤ 300 "
                    "characters, or '-'), and a one-line why."),
    "admitted": ("Read the excerpt of DECISION around the quoted words. Is DECISION's court, in its majority opinion, "
                 "itself changing the status of TARGET (overruling, abrogating, disapproving or receding from it), as "
                 "opposed to reporting another court's act, overruling an objection or motion, a separate opinion, or "
                 "a different case? Answer verdict (yes|reportsOther|procedural|separateOpinion|wrongTarget|refuses|"
                 "other), kind (overruled|abrogated|disapproved|recededFrom|-), scope (all|partialUnknown|"
                 "otherGrounds|-), and a one-line why."),
    "rejected": ("Lean rejected the certificate below for the stated reason. Read the quote and window. Answer "
                 "rejection_right (yes|no), what_it_is (overrulingByThisCourt|reportOfOther|procedural|"
                 "separateOpinion|refusal|wrongTarget|other), and a one-line why."),
}


class Texts:
    def __init__(self, nodes):
        self.where = {}
        want = set(nodes)
        for line in open(os.path.join(W, "graph", "nodes.tsv"), encoding="utf-8"):
            f = line.split("\t", 7)
            n = int(f[0])
            if n in want:
                self.where[n] = (f[1], f[2], f[4], f[5].split("|")[0], f[6])
                want.discard(n)
                if not want:
                    break

    def meta(self, n):
        r, p, d, c, nm = self.where.get(n, ("", "", "0", "", ""))
        return {"name": nm, "cite": c, "date": d, "repo": r}

    def text(self, n):
        if n not in self.where:
            return ""
        r, p = self.where[n][:2]
        out = subprocess.run(["git", "-C", os.path.join(REPOS, r), "show", "HEAD:" + p], capture_output=True,
                             creationflags=CNW).stdout.decode("utf-8", "replace").replace("\r\n", "\n")
        if out.startswith("---"):
            e = out.find("\n---", 3)
            out = out[e + 4:] if e >= 0 else out
        return out


def excerpts(text, target_meta, limit=9000):
    """Windows of the text around the target's citation and name tokens (±900 characters), merged, up to `limit`."""
    keys = []
    c = target_meta.get("cite", "")
    m = re.match(r"(\d+)\s+(.+?)\s+(\d+)$", c)
    if m:
        keys.append(re.escape(m.group(1)) + r"\s+" + r"\s*".join(map(re.escape, m.group(2).split())) + r"\s+" +
                    re.escape(m.group(3)))
    for t in re.findall(r"\b[A-Z][a-z][A-Za-z'\-]{3,}", re.sub(r"\(.*?\)", "", target_meta.get("name", ""))):
        if t not in ("State", "States", "United", "People", "Commonwealth", "Company", "County", "City", "Insurance"):
            keys.append(r"\b" + re.escape(t) + r"\b")
    spans = []
    for k in keys[:4]:
        for mm in re.finditer(k, text):
            spans.append((max(0, mm.start() - 900), min(len(text), mm.end() + 900)))
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    out, tot = [], 0
    for s, e in merged:
        seg = text[s:e]
        hdr = [h for h in re.finditer(r"^## (.+)$", text[:s], re.M)]
        part = hdr[-1].group(1) if hdr else "Opinion"
        out.append({"part": part[:40], "offset": s, "text": seg})
        tot += len(seg)
        if tot > limit:
            break
    if not out:
        out.append({"part": "start", "offset": 0, "text": text[:3000]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audit", choices=list(QUESTIONS))
    ap.add_argument("n", type=int)
    ap.add_argument("--seed", type=int, default=20261112)
    ap.add_argument("--shards", type=int, default=3)
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    gold = os.path.join(C2, "gold")
    od = os.path.join(C2, "eval", "audits", a.audit)
    os.makedirs(od, exist_ok=True)
    packets, keys = [], []
    if a.audit == "gold-notes":
        rs = rows(os.path.join(gold, "reports_typed.tsv"), [])
        by_kind = collections.defaultdict(list)
        for r in rs:
            by_kind[r["kind"]].append(r)
        per = max(1, a.n // len(by_kind))
        pick = []
        for k in sorted(by_kind):
            pick += rnd.sample(by_kind[k], min(per, len(by_kind[k])))
        tx = Texts([iint(r["target_node"]) for r in pick] + [iint(r["by_node"]) for r in pick] +
                   [iint(r["stated_in_node"]) for r in pick])
        for i, r in enumerate(pick):
            packets.append({"id": i, "passage": r["snippet"]})
            keys.append({"id": i, "row": r["id"], "target": r["target_node"], "target_meta": tx.meta(iint(r["target_node"])),
                         "by": r["by_node"], "by_meta": tx.meta(iint(r["by_node"])),
                         "stated_in": r["stated_in_node"], "kind": r["kind"], "scope": r["scope"]})
    elif a.audit == "notes-blind":
        ps = rows(os.path.join(gold, "reports_typed_pairs.tsv"), [])
        cand = [p for p in ps if p["kind"] in ("overruled", "abrogated", "disapproved", "recededFrom")
                and iint(p["by_node"]) >= 0]
        pick = rnd.sample(cand, min(a.n, len(cand)))
        tx = Texts([iint(p["target_node"]) for p in pick] + [iint(p["by_node"]) for p in pick])
        for i, p in enumerate(pick):
            tm, bm = tx.meta(iint(p["target_node"])), tx.meta(iint(p["by_node"]))
            packets.append({"id": i, "TARGET": tm, "DECISION": {**bm, "excerpts": excerpts(tx.text(iint(p["by_node"])),
                                                                                         tm)}})
            keys.append({"id": i, **p})
    elif a.audit == "admitted":
        tr = rows(os.path.join(C2, "data", "treatments.tsv"), [])
        certs = rows(os.path.join(C2, "out", "certs.tsv"), ["file", "id", "result"])
        if tr is None or certs is None:
            sys.exit("pending: data/treatments.tsv and out/certs.tsv")
        ok = {c["id"] for c in certs if "treatments" in c["file"] and (c.get("result") or "") == "ok"}
        cand = [r for r in tr if r["id"] in ok and r.get("explicit", "1") == "1"]
        pick = rnd.sample(cand, min(a.n, len(cand)))
        tx = Texts([iint(r["target_node"]) for r in pick] + [iint(r["by_node"]) for r in pick])
        for i, r in enumerate(pick):
            text = tx.text(iint(r["by_node"]))
            s = iint(r["start"], 0)
            packets.append({"id": i, "TARGET": tx.meta(iint(r["target_node"])),
                            "DECISION": {**tx.meta(iint(r["by_node"])), "excerpt": text[max(0, s - 2500):s + 2500],
                                         "quote": r["quote"]}})
            keys.append({"id": i, **{k: r[k] for k in ("id", "by_node", "target_node", "kind", "scope", "part",
                                                         "reader")}, "packet_id": i})
    elif a.audit == "rejected":
        tr = {r["id"]: r for r in rows(os.path.join(C2, "data", "treatments.tsv"), []) or []}
        ct = {r.get("text_sha"): r for r in rows(os.path.join(C2, "data", "cert_text.tsv"), []) or []}
        certs = rows(os.path.join(C2, "out", "certs.tsv"), ["file", "id", "result"])
        if not tr or certs is None:
            sys.exit("pending: data/treatments.tsv and out/certs.tsv")
        by_reason = collections.defaultdict(list)
        for c in certs:
            if "treatments" in c["file"] and (c.get("result") or "ok") != "ok" and c["id"] in tr:
                by_reason[c["result"].split(":")[0]].append(c)
        per = max(1, a.n // max(1, len(by_reason)))
        pick = []
        for k in sorted(by_reason):
            pick += rnd.sample(by_reason[k], min(per, len(by_reason[k])))
        tx = Texts([iint(tr[c["id"]]["target_node"]) for c in pick])
        for i, c in enumerate(pick):
            r = tr[c["id"]]
            packets.append({"id": i, "reason": c["result"], "TARGET": tx.meta(iint(r["target_node"])),
                            "quote": r["quote"], "window": (ct.get(r.get("text_sha")) or {}).get("window", "")})
            keys.append({"id": i, "treatment": c["id"], "reason": c["result"]})
    k = max(1, a.shards)
    for j in range(k):
        part = [p for p in packets if p["id"] % k == j]
        json.dump({"question": QUESTIONS[a.audit], "items": part},
                  open(os.path.join(od, f"in_{j}.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False,
                  indent=1)
    json.dump(keys, open(os.path.join(od, "key.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False,
              indent=1)
    print(a.audit, len(packets), "packets in", k, "shards ->", od)


if __name__ == "__main__":
    main()
