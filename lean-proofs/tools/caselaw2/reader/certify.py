"""Fourth stage: certificates. Joins candidates, the model's answers and the history rows, verifies every quote and
every piece of target evidence against the decision text, and writes the SCHEMA files.

    python -X utf8 certify.py --results llm/main.gpt-5.4-mini.jsonl [--override llm/hard.gpt-6.1-sol.jsonl ...]
                              [--out DIR] [--repos r1,r2] [--no-history]

Writes to DIR (default caselaw-lean-2/data/):
  treatments.tsv  id, by_node, target_node, date, kind, scope, temporal, explicit, CERT(6), reader, confidence
  history.tsv     id, target_node, by_node, date, kind, scope, CERT(6), src
  cert_text.tsv   text_sha, start0, end0, window   (one row per distinct certificate span)
  reader_rejects.tsv   id, stage, reason (model-stage and certificate-stage rejections, for audit)
  reader_stats.json
CERT = text_sha, start, end, quote, target_evidence, part. Offsets: characters of the git-HEAD file text, UTF-8 decoded,
CRLF -> LF; quote and window: tab/newline -> space (one for one). Every quote is checked here to equal
text[start:end] (normalised) and every target_evidence to occur inside text[start-400:end+400].
"""
import argparse, collections, glob, gzip, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CITE_RX, DATA, WORK, cite_key, name_tokens  # noqa: E402
import rules  # noqa: E402

HIST_CUES = {"affirmed": ["affirm"], "reversed": ["revers"], "vacated": ["vacat", "set aside", "quash", "annul"],
             "modified": ["modif"], "certDenied": ["denied"], "reviewGranted": ["granted"],
             "reviewDismissed": ["dismiss"], "rehearingEnBancGranted": ["en banc"], "withdrawn": ["withdr"],
             "reinstated": ["reinstat"], "writRefused": ["refused", "ref'd"], "other": ["writ"], "depublished": ["publish"]}
PART_OUT = {"majority": "majority", "majority~": "majority", "perCuriam": "perCuriam", "plurality": "plurality",
            "concurrence": "concurrence", "concurrence~": "concurrence", "dissent": "dissent", "dissent~": "dissent"}


def slug(x):
    x = re.sub(r"[^a-z0-9]+", "-", x.lower()).strip("-")
    return x[:40] or "issue"


def clean(x):
    # SCHEMA: tabs and newlines become spaces one for one; a lone CR too (FB-R1: a trailing CR is stripped as a line
    # ending by the readers, and the window then no longer has end0 - start0 characters)
    return x.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def find_quote(lw, quote, prefer):
    """Exact position of the model's quote in the window; tolerant only of whitespace runs and quote-mark styles,
    and then the exact text of the window is used."""
    q = quote.strip()
    if not q:
        return None
    hits = [m.start() for m in re.finditer(re.escape(q), lw)]
    if hits:
        i = min(hits, key=lambda h: abs(h - prefer))
        return i, i + len(q)
    parts = []
    for ch in q:
        if ch.isspace():
            if not parts or parts[-1] != r"\s+":
                parts.append(r"\s+")
        elif ch in "'’‘`":
            parts.append("['’‘`]")
        elif ch in '"“”':
            parts.append('["“”]')
        else:
            parts.append(re.escape(ch))
    try:
        ms = list(re.finditer("".join(parts), lw))
    except re.error:
        return None
    if not ms:
        return None
    m = min(ms, key=lambda m: abs(m.start() - prefer))
    return m.start(), m.end()


OPEN_Q, CLOSE_Q = "“", "”"


def quoted(w, a, b):
    """True if text w[a:b] sits inside a quotation of another opinion: it starts with an opening quote mark or an
    altered capital ("[T]oday"), or an opening curly quote before it (within 400 chars) is still open and closes within
    300 chars after it."""
    q = w[a:b].lstrip()
    if q[:1] in (OPEN_Q, '"') or re.match(r"\[[A-Z]\]", q):
        return True
    before = w[max(0, a - 400):a]
    if before.rfind(OPEN_Q) > before.rfind(CLOSE_Q) and CLOSE_Q in w[b:b + 300]:
        return True
    return False


class Evidence:
    def __init__(self):
        self.idx = {}
        for line in open(os.path.join(os.path.dirname(DATA), "..", "graph", "cite_index.tsv"), encoding="utf-8"):
            k, v = line.rstrip("\n").split("\t")
            self.idx[k] = int(v)

    def in_window(self, ev, j, window, names):
        """Evidence string for target j inside window (prefer the given one)."""
        if ev.startswith("cite:"):
            for m in CITE_RX.finditer(window):
                if cite_key(m) == ev[5:]:
                    return ev
        elif ev.startswith("name:"):
            if re.search(r"\b" + re.escape(ev[5:]) + r"\b", window):
                return ev
        for m in CITE_RX.finditer(window):
            k = cite_key(m)
            if k and self.idx.get(k) == j:
                return "cite:" + k
        for t in sorted(name_tokens(names.get(j, ""))):
            if re.search(r"\b" + re.escape(t) + r"\b", window):
                return "name:" + t
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", action="append", default=[])
    ap.add_argument("--override", action="append", default=[])
    ap.add_argument("--out", default=DATA)
    ap.add_argument("--repos")
    ap.add_argument("--no-history", action="store_true")
    a = ap.parse_args()
    repos = set(a.repos.split(",")) if a.repos else None
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for f in a.results:
        for line in open(os.path.join(WORK, f) if not os.path.isabs(f) else f, encoding="utf-8"):
            r = json.loads(line)
            res[r["id"]] = r
    n_over = 0
    for f in a.override:
        for line in open(os.path.join(WORK, f) if not os.path.isabs(f) else f, encoding="utf-8"):
            r = json.loads(line)
            if r.get("r") is not None:
                res[r["id"]] = r
                n_over += 1
    ev = Evidence()
    names = {}
    st = collections.Counter()
    st["override_items"] = n_over
    certs = {}
    trows = []
    rej = open(os.path.join(a.out, "reader_rejects.tsv"), "w", encoding="utf-8", newline="\n")
    want_items = collections.defaultdict(set)
    for i, r in res.items():
        want_items[r["repo"]].add(i)
    items_by_id = {}
    for repo, ids in want_items.items():
        if repos and repo not in repos:
            continue
        for line in gzip.open(os.path.join(WORK, "res", repo + ".items.jsonl.gz"), "rt", encoding="utf-8"):
            it = json.loads(line)
            if it["id"] in ids:
                items_by_id[it["id"]] = it
                for t in it["targets"]:
                    names[t["node"]] = t["name"]
    for i, it in items_by_id.items():
        rr = res[i]
        r = rr.get("r")
        st["model_items"] += 1
        if r is None:
            st["model_no_answer"] += 1
            rej.write(f"{i}\tmodel\tno-answer\n")
            continue
        if not r["own_act"] or r["kind"] == "none":
            st["model_not_act"] += 1
            rej.write(f"{i}\tmodel\tnot-own-act:{r['kind']}\n")
            continue
        tids = [t for t in r["targets"] if re.fullmatch(r"T\d+", t) and 1 <= int(t[1:]) <= len(it["targets"])]
        if len(tids) < len(r["targets"]):
            st["model_invented_target_dropped"] += len(r["targets"]) - len(tids)
        if not tids:
            st["model_no_valid_target"] += 1
            rej.write(f"{i}\tmodel\tno-target\n")
            continue
        lw = it["w"][it["lw0"] - it["w0"]:it["lw1"] - it["w0"]]
        prefer = it["s0"] - it["lw0"]
        pos = find_quote(lw, r["quote"], prefer)
        how = "quote"
        kind = r["kind"]
        if kind == "followed" and re.search(r"no\s+longer\s+(?:be\s+)?follow|not\s+(?:be\s+)?follow", r["quote"], re.I):
            # held-out audit: "X will no longer be followed" was mislabelled `followed`; it is the court abandoning X
            kind = "overruled"
            st["kind_fix_followed_to_overruled"] += 1
        if pos is not None:
            q0, q1 = pos
            quote = lw[q0:q1]
            if not rules.cue_ok(kind, quote):
                pos = None
                how = "sentence:no-cue-in-quote"
        else:
            how = "sentence:quote-not-found"
            st["quote_not_found"] += 1
        if pos is None:
            q0, q1 = it["s0"] - it["lw0"], it["s1"] - it["lw0"]
            quote = lw[q0:q1]
            if not rules.cue_ok(kind, quote):
                st["cert_fail_cue"] += 1
                rej.write(f"{i}\tcert\tcue-missing:{kind}\n")
                continue
        start, end = it["lw0"] + q0, it["lw0"] + q1
        # the exact substring at those offsets
        assert it["w"][start - it["w0"]:end - it["w0"]] == quote
        if quoted(it["w"], start - it["w0"], end - it["w0"]):
            st["cert_fail_quoted"] += 1
            rej.write(f"{i}\tcert\tinside-quotation\n")
            continue
        st0, en0 = max(0, start - 400), min(it["len"], end + 400)
        assert st0 >= it["w0"] and en0 <= it["w1"], (i, st0, en0, it["w0"], it["w1"])
        window = it["w"][st0 - it["w0"]:en0 - it["w0"]]
        part = PART_OUT.get(it["part"], "unknown")
        for tid in tids:
            t = it["targets"][int(tid[1:]) - 1]
            j = t["node"]
            if j == it["n"]:
                st["self_target"] += 1
                continue
            e = ev.in_window(t["ev"], j, window, names)
            if e is None:
                st["cert_fail_evidence"] += 1
                rej.write(f"{i}\tcert\tevidence-out-of-window:{j}\n")
                continue
            scope = r["scope"]
            if scope == "issues":
                labs = [slug(x) for x in r["issues"] if x.strip()][:3]
                scope = "issues:" + ",".join(labs) if labs else "partialUnknown"
            tmp = r["temporal"]
            if tmp == "prospective":
                pf = r.get("prospective_from", "")
                d = it["date"] if pf in ("", "thisDecision") or not re.fullmatch(r"\d{8}", pf) else int(pf)
                tmp = f"prospectiveFrom:{d}"
            reader = "gpt-6.1-sol" if rr["model"].startswith("gpt-6.1-sol") else "gpt-5.4-mini"
            conf = max(0.0, min(1.0, float(r.get("confidence", 0.5))))
            trows.append({"by": it["n"], "target": j, "date": it["date"], "kind": kind, "scope": scope,
                          "temporal": tmp, "sha": it["sha"], "start": start, "end": end, "quote": clean(quote),
                          "ev": e, "part": part, "reader": reader, "conf": conf, "item": i, "how": how,
                          "fam": it["why"]})
            certs[(it["sha"], st0, en0)] = clean(window)
            st["admitted_rows"] += 1
            st["admitted_how:" + how.split(":")[0]] += 1
    # one row per (by, target, kind, scope): the most confident certificate
    best = {}
    for t in trows:
        k = (t["by"], t["target"], t["kind"], t["scope"])
        if k not in best or t["conf"] > best[k]["conf"]:
            best[k] = t
    with open(os.path.join(a.out, "treatments.tsv"), "w", encoding="utf-8", newline="\n") as fo:
        for t in sorted(best.values(), key=lambda t: (t["by"], t["target"], t["start"])):
            tid = f"t:{t['by']}:{t['target']}:{t['start']}"
            fo.write("\t".join(map(str, [tid, t["by"], t["target"], t["date"], t["kind"], t["scope"], t["temporal"], 1,
                                         t["sha"], t["start"], t["end"], t["quote"], t["ev"], t["part"], t["reader"],
                                         f"{t['conf']:.2f}"])) + "\n")
    with open(os.path.join(a.out, "treatments_items.tsv"), "w", encoding="utf-8", newline="\n") as fo:
        for t in sorted(best.values(), key=lambda t: (t["by"], t["target"], t["start"])):
            fo.write(f"t:{t['by']}:{t['target']}:{t['start']}\t{t['item']}\t{t['how']}\t{t['fam']}\n")
    st["treatments"] = len(best)
    kc = collections.Counter((t["kind"], t["scope"].split(":")[0]) for t in best.values())
    st["by_kind_scope"] = {f"{k}|{s}": v for (k, s), v in sorted(kc.items())}
    # same-case history
    if not a.no_history:
        hrows = 0
        hk = collections.Counter()
        with open(os.path.join(a.out, "history.tsv"), "w", encoding="utf-8", newline="\n") as fo:
            for f in sorted(glob.glob(os.path.join(WORK, "res", "*.hist.jsonl.gz"))):
                repo = os.path.basename(f)[:-len(".hist.jsonl.gz")]
                if repos and repo not in repos:
                    continue
                for line in gzip.open(f, "rt", encoding="utf-8"):
                    h = json.loads(line)
                    quote = h["w"][h["q0"] - h["w0"]:h["q1"] - h["w0"]]
                    if not any(c in quote.lower() for c in HIST_CUES.get(h["kind"], [])):
                        st["hist_cert_fail_cue"] += 1
                        continue
                    window = h["w"]
                    e = h["ev"]
                    ok = (any(cite_key(m) == e[5:] for m in CITE_RX.finditer(window)) if e.startswith("cite:")
                          else bool(re.search(r"\b" + re.escape(e[5:]) + r"\b", window)))
                    if not ok:
                        st["hist_cert_fail_evidence"] += 1
                        continue
                    part = PART_OUT.get(h["part"], "unknown")
                    hid = f"h:{h['n']}:{h['j']}:{h['kind']}"
                    fo.write("\t".join(map(str, [hid, h["j"], h["n"], h["date"], h["kind"], h["scope"], h["sha"],
                                                 h["q0"], h["q1"], clean(quote), e, part,
                                                 f"hist-regex-v2:{h['mode']}:{h['k'].replace(' ', '-')}"])) + "\n")
                    certs[(h["sha"], h["w0"], h["w1"])] = window
                    hrows += 1
                    hk[(h["kind"], h["scope"])] += 1
        st["history"] = hrows
        st["history_by_kind_scope"] = {f"{k}|{s}": v for (k, s), v in sorted(hk.items())}
    with open(os.path.join(a.out, "cert_text.tsv"), "w", encoding="utf-8", newline="\n") as fo:
        for (sha, s0, e0), w in sorted(certs.items()):
            fo.write(f"{sha}\t{s0}\t{e0}\t{w}\n")
    st["cert_text_rows"] = len(certs)
    rej.close()
    with open(os.path.join(a.out, "reader_stats.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, indent=1)
    print(json.dumps({k: v for k, v in st.items() if not isinstance(v, dict)}, indent=0))


if __name__ == "__main__":
    main()
