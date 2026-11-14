"""Round 7, A1 (iii): Supreme Court orders whose disposition is only in CAP head matter -> history rows with the claim
`orderHead` (DESIGN7 section 3.1).

    python -X utf8 round7/agents/orderhead/build_orderhead.py [--extra-order-line FILE --out DIR]

Input: the round-6 `memo` linker's rows (round6/history/rules/memo/rows.jsonl) and its certify6 rejects
(rules/memo/cert/rejects.tsv). Candidates = the rows certify6 rejected `partNotMajority` with part `headmatter`.
A candidate becomes a round-7 row only when every condition holds (else it is refused, with the first reason):
  rule        the memo rule is one the lead installed in round 6 (memo:cite, memo:cap-2t, memo:cap-2g; final2
              leaves out cap-1s and cap-2t-anycourt; reviewGranted rows are not staged)
  kind        certDenied | vacated | reversed | affirmed | reviewDismissed
  court       the acting decision's court in the base decisions2.tsv is the Supreme Court (courts2)
  date        the acting decision's date >= order_head_from (cue table; 20130101)
  orderLine   the quote (text at `disp`, normalised, ASCII lower-cased) holds an `order_line` phrase of its kind
  length      the quote is at most order_head_max_len (400) characters
  opinionPart the acting decision has an opinion-of-the-court part (majority / perCuriam / plurality) anywhere: from
              the round-6 cache zone record (`z.parts`, round6/history/r6scan.py); a decision with no zone record is
              refused (`noZone`) rather than guessed
The rows keep the memo row's fields; "table": "history", "main" = disp, "claim": "orderHead",
"rule": "orderHead:<memo rule>". Writes rows.jsonl, refused.tsv (line of the memo rows file, reason, rule, by, target,
kind, detail) and counts.json here. Reads no answer key.
--extra-order-line FILE  (what-if, for the lead / the `lean` agent) a JSON object {kind: [phrases]} added to the cue
                         table's order_line lists; with --out DIR the outputs go to DIR instead of this folder.
"""
import argparse
import collections
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R7 = os.path.dirname(os.path.dirname(HERE))
C2 = os.path.dirname(R7)
sys.path.insert(0, R7)
import certify7 as C7  # noqa: E402

L = C7.L
MEMO = os.path.join(C2, "round6", "history", "rules", "memo")
CACHE = os.path.join(C2, "round6", "history", "cache")
INSTALLED = ("memo:cite", "memo:cap-2t", "memo:cap-2g")
OPINION = ("majority", "perCuriam", "plurality")


def zone_parts(nodes, repos):
    """{node: [part names]} from the cache zone records of the given repos' shards."""
    out = {}
    shards = sorted(f for f in os.listdir(CACHE) if f.endswith(".jsonl.gz") and f.split(".")[0] in repos)
    for sh in shards:
        with gzip.open(os.path.join(CACHE, sh), "rt", encoding="utf-8") as f:
            for line in f:
                if not line.startswith('{"t":"z"'):
                    continue
                r = json.loads(line)
                if r.get("t") == "z" and r["n"] in nodes:
                    out[r["n"]] = [p[2] for p in r.get("parts", [])]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra-order-line")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    cues, src = C7.load_cues()
    if a.extra_order_line:
        extra = json.load(open(a.extra_order_line, encoding="utf-8"))
        for k, v in extra.items():
            cues["order_line"][k] = list(cues["order_line"].get(k, [])) + list(v)
        src["order_line"] += " + what-if " + a.extra_order_line.replace(os.sep, "/")
    os.makedirs(a.out, exist_ok=True)
    rows = {}
    with open(os.path.join(MEMO, "rows.jsonl"), encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            if line.strip():
                rows[ln] = json.loads(line)
    cand = []
    reasons_in = collections.Counter()
    for p in C7.C6.read_tsv(os.path.join(MEMO, "cert", "rejects.tsv")):
        reasons_in[p[1]] += 1
        if p[1] == "partNotMajority":
            ln = int(p[0].rsplit(":", 1)[1])
            r = rows[ln]
            if r.get("part") == "headmatter":
                cand.append((ln, r))
    by_nodes = {r["by"] for _, r in cand}
    dec = C7.read_decisions(os.path.join(C7.BASE, "decisions2.tsv"), by_nodes | {r["target"] for _, r in cand})
    sc = C7.scotus_id(C7.BASE)
    texts = L.fetch_texts(sorted(by_nodes))
    repos = {L.node_row(n)[1] for n in by_nodes}
    zp = zone_parts(by_nodes, repos)
    out, refused = [], []
    cnt = collections.Counter()
    by_kind = collections.defaultdict(collections.Counter)
    for ln, r in cand:
        n = r["by"]
        k = r["kind"]
        why, detail = None, ""
        court, date, _sha = dec.get(n, (-1, 0, ""))
        q0, q1 = r["disp"]
        text = texts.get(n, (None, ""))[1]
        quote = C7.norm(text[q0:q1]) if 0 <= q0 < q1 <= len(text) else ""
        ql = C7.lower(quote)
        if r["rule"] not in INSTALLED:
            why, detail = "rule", r["rule"]
        elif k not in C7.ORDER_KINDS:
            why = "kind"
        elif court != sc:
            why, detail = "court", str(court)
        elif date < cues["order_head_from"]:
            why, detail = "date", str(date)
        elif not quote:
            why = "noText"
        elif C7.any_in(cues["order_line"].get(k, []), ql) is None:
            why, detail = "orderLine", quote[:160]
        elif len(quote) > cues["order_head_max_len"]:
            why, detail = "length", str(len(quote))
        elif n not in zp:
            why = "noZone"
        elif any(p in OPINION for p in zp[n]):
            why, detail = "opinionPart", ",".join(p for p in zp[n] if p in OPINION)
        by_kind[k]["candidates"] += 1
        if why:
            cnt["refused:" + why] += 1
            by_kind[k]["refused:" + why] += 1
            refused.append((ln, why, r["rule"], n, r["target"], k, detail.replace("\t", " ")))
            continue
        cnt["rows"] += 1
        by_kind[k]["rows"] += 1
        o = dict(r)
        o.pop("disp", None)
        o.update({"rule": "orderHead:" + r["rule"].split(":", 1)[1], "table": "history", "main": list(r["disp"]),
                  "claim": "orderHead",
                  "note": (r.get("note") or "") + "; memo rows.jsonl:%d; head-matter-only order (no opinion part)" % ln})
        out.append(o)
    with open(os.path.join(a.out, "rows.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "refused.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("memo_line\treason\trule\tby\ttarget\tkind\tdetail\n")
        for x in refused:
            f.write("\t".join(map(str, x)) + "\n")
    # what the order-line refusals look like (form of the quote, by kind)
    forms = collections.Counter()
    for x in refused:
        if x[1] == "orderLine":
            q = C7.lower(x[6])
            q = q[:70]
            forms[(x[5], q[:45])] += 1
    res = {"cue_source": {k: v for k, v in src.items() if k in ("order_line", "order_head_from",
                                                                  "order_head_max_len")},
           "memo_rejects_by_reason": dict(reasons_in), "candidates_partNotMajority_headmatter": len(cand),
           "counts": dict(sorted(cnt.items())), "by_kind": {k: dict(sorted(v.items())) for k, v in sorted(by_kind.items())},
           "orderLine_refusals_top_forms": [[k, q, c] for (k, q), c in forms.most_common(15)],
           "zones_found": len(zp), "acting_decisions": len(by_nodes)}
    with open(os.path.join(a.out, "counts.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
