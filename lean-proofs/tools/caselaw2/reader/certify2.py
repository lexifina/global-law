"""Round 2 fourth stage: certificates for the rows read by Claude subagents (same checks and CERT columns as
certify.py; reader label `claude-subagent`).

    python -X utf8 certify2.py --answers DIR --out DIR [--res DIR] [--base treatments.tsv]

Reads DIR/ans_*.jsonl (pack2.py answer format) and the res2 items, and writes to --out:
  treatments_new.tsv        rows in the treatments.tsv format (explicit = 1, reader = claude-subagent)
  treatments_items_new.tsv  row id, candidate id, how the quote was chosen, why the candidate was read
  cert_text_new.tsv         text_sha, start0, end0, window
  rejects_new.tsv           candidate id, stage (model|cert), reason
  stats.json
Checks, as certify.py: the quote is found exactly in the window (whitespace runs and quote-mark styles tolerated; the
window's own text is used), else the focus sentence is used; the quote has a cue of the kind (rules2.CUES2 = the v1
cue table plus the round-2 cues that Certificate.lean also gets); the quote is not inside another court's quotation;
the target evidence occurs in the certificate window. For a target resolved in the wide window (before the +-400
window), the certificate window runs from the evidence to the quote (at most 2,600 characters).
Name evidence is written in the checker's form: every character that is not a letter or digit becomes a space
("Meraz-Valeta" -> "Meraz Valeta"), because the checker compares whole words of letters and digits.
A row whose (by, target, kind) already exists in --base is not written again. Model scope `issues` is written as
`partialUnknown`: the labels are free text, not issues.tsv keys (the holdings reach step maps them later).
"""
import argparse, collections, glob, gzip, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CITE_RX, DATA, WORK, cite_key, name_tokens  # noqa: E402
import rules, rules2  # noqa: E402
from certify import find_quote, quoted, clean, PART_OUT  # noqa: E402

KINDS = {"overruled", "disapproved", "recededFrom", "abrogated", "supersededByEnactment", "limited", "questioned",
         "criticized", "declinedToFollow", "distinguished", "followed"}
SCOPES = {"all", "issues", "partialUnknown", "otherGrounds"}


def checker_name(ev):
    """name:<tokens> in the form the checker matches: whole words of letters and digits, each of 3+ characters."""
    toks = [t for t in re.sub(r"[^0-9A-Za-z]+", " ", ev).split() if len(t) >= 3]
    return "name:" + " ".join(toks) if toks else None


def evidence_in(t, window, idx):
    """Evidence for target t inside window: its citation (resolving to it), else its name evidence, else a name token."""
    j = t["node"]
    ev = t["ev"]
    if ev.startswith("cite:"):
        for m in CITE_RX.finditer(window):
            if cite_key(m) == ev[5:]:
                return ev
    for m in CITE_RX.finditer(window):
        k = cite_key(m)
        if k and idx.get(k) == j:
            return "cite:" + k
    cands = []
    if ev.startswith("name:"):
        cands.append(ev[5:])
    cands += sorted(name_tokens(t.get("name", "")))
    words = set(re.findall(r"[0-9a-z]+", window.lower()))
    for c in cands:
        e = checker_name(c)
        if e and all(x.lower() in words for x in e[5:].split()):
            return e
    return None


def find_quote_hw(lw, quote, prefer):
    """Round 3: the reader may copy a quote without the line-end hyphenation of a hard-wrapped text ("overruled"
    for "over- ruled"). Match with an optional "- " after every letter; the window's own text is used."""
    q = quote.strip()
    if not q or len(q) > 700:
        return None
    parts = []
    for ch in q:
        if ch.isspace():
            if not parts or parts[-1] != r"\s+":
                parts.append(r"\s+")
        elif ch in "'’‘`":
            parts.append("['’‘`]")
        elif ch in '"“”':
            parts.append('["“”]')
        elif ch.isalpha():
            parts.append(re.escape(ch) + "(?:- +)?")
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default=os.path.join(WORK, "res2"))
    ap.add_argument("--base", default=os.path.join(DATA, "treatments.tsv"))
    ap.add_argument("--reader", default="claude-subagent")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ans = {}
    bad = 0
    for f in sorted(glob.glob(os.path.join(a.answers, "ans_*.jsonl"))):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                ans[str(r["id"]).strip()] = r
            except Exception:
                bad += 1
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
    have = set()
    for line in open(a.base, encoding="utf-8"):
        f = line.split("\t", 6)
        have.add((int(f[1]), int(f[2]), f[4]))
    st = collections.Counter()
    st["answer_lines_unparsed"] = bad
    st["answers"] = len(ans)
    st["index_items"] = len(index)
    st["items_without_answer"] = len(set(index) - set(ans))
    rej = open(os.path.join(a.out, "rejects_new.tsv"), "w", encoding="utf-8", newline="\n")
    for i in sorted(set(index) - set(ans)):
        rej.write(f"{i}\tmodel\tno-answer\n")
    trows, certs = [], {}
    for i, r in ans.items():
        it = items.get(i)
        if it is None:
            st["answer_unknown_id"] += 1
            continue
        st["model_items"] += 1
        kind = r.get("kind", "none")
        if not r.get("own_act") or kind == "none" or kind not in KINDS:
            st["model_not_act"] += 1
            rej.write(f"{i}\tmodel\tnot-own-act:{kind}\n")
            continue
        tids = [t for t in (r.get("targets") or []) if isinstance(t, str) and re.fullmatch(r"T\d+", t)
                and 1 <= int(t[1:]) <= len(it["targets"])]
        if not tids:
            st["model_no_valid_target"] += 1
            rej.write(f"{i}\tmodel\tno-target\n")
            continue
        lw = it["w"][it["lw0"] - it["w0"]:it["lw1"] - it["w0"]]
        prefer = it["s0"] - it["lw0"]
        pos = find_quote(lw, r.get("quote") or "", prefer)
        if pos is None and it.get("hw"):
            pos = find_quote_hw(lw, r.get("quote") or "", prefer)
        how = "quote"
        if kind == "followed" and re.search(r"no\s+longer\s+(?:be\s+)?follow|not\s+(?:be\s+)?follow", r.get("quote") or "", re.I):
            kind = "overruled"
        if pos is not None:
            q0, q1 = pos
            if q1 - q0 > 600:
                pos = None
                how = "sentence:quote-too-long"
            elif not rules2.cue_ok2(kind, lw[q0:q1]):
                pos = None
                how = "sentence:no-cue-in-quote"
        else:
            how = "sentence:quote-not-found"
            st["quote_not_found"] += 1
        if pos is None:
            q0, q1 = it["s0"] - it["lw0"], it["s1"] - it["lw0"]
            if not rules2.cue_ok2(kind, lw[q0:q1]):
                if it.get("hw") and rules2.cue_ok2(kind, re.sub(r"(?<=[a-z])- +(?=[a-z])", "", lw[q0:q1])):
                    # the cue word is split by line-end hyphenation ("over- ruled"); the checkers match the cue in
                    # the quote as it stands in the text, so the row cannot be certified (round3/requests_to_lean.md)
                    st["cert_fail_cue_hyphen"] += 1
                    rej.write(f"{i}\tcert\tcue-hyphen-split:{kind}\n")
                    continue
                st["cert_fail_cue"] += 1
                rej.write(f"{i}\tcert\tcue-missing:{kind}\n")
                continue
        quote = lw[q0:q1]
        start, end = it["lw0"] + q0, it["lw0"] + q1
        assert it["w"][start - it["w0"]:end - it["w0"]] == quote
        if quoted(it["w"], start - it["w0"], end - it["w0"]):
            st["cert_fail_quoted"] += 1
            rej.write(f"{i}\tcert\tinside-quotation\n")
            continue
        if any(x in quote.lower() for x in rules2.DISQUAL2) and kind in ("overruled", "disapproved", "recededFrom",
                                                                         "abrogated", "supersededByEnactment"):
            # the checker would reject the row (reported history, refusal, procedural ruling inside the quote)
            st["cert_fail_disqualifier"] += 1
            rej.write(f"{i}\tcert\tdisqualifier-in-quote\n")
            continue
        part = PART_OUT.get(it["part"], "unknown")
        for tid in tids:
            t = it["targets"][int(tid[1:]) - 1]
            j = t["node"]
            if j == it["n"]:
                st["self_target"] += 1
                continue
            st0, en0 = max(0, start - 400), min(it["len"], end + 400)
            st0, en0 = max(st0, it["w0"]), min(en0, it["w1"])
            window = it["w"][st0 - it["w0"]:en0 - it["w0"]]
            e = evidence_in(t, window, idx)
            if e is None and t.get("rank") == 4 and it["w0"] <= t["at"] < start and end - t["at"] <= 2600:
                st0 = max(it["w0"], t["at"] - 60)
                window = it["w"][st0 - it["w0"]:en0 - it["w0"]]
                e = evidence_in(t, window, idx)
                if e is not None:
                    st["wide_window_rows"] += 1
            if e is None:
                st["cert_fail_evidence"] += 1
                rej.write(f"{i}\tcert\tevidence-out-of-window:{j}\n")
                continue
            if (it["n"], j, kind) in have:
                st["already_in_base"] += 1
                rej.write(f"{i}\tcert\talready-in-base:{j}:{kind}\n")
                continue
            scope = r.get("scope", "all")
            if scope not in SCOPES:
                scope = "partialUnknown"
            if scope == "issues":
                scope = "partialUnknown"
            tmp = r.get("temporal", "unknown")
            if tmp == "prospective":
                pf = str(r.get("prospective_from", ""))
                d = it["date"] if pf in ("", "thisDecision") or not re.fullmatch(r"\d{8}", pf) else int(pf)
                tmp = f"prospectiveFrom:{d}"
            elif tmp not in ("unknown", "pureProspective", "retroactive"):
                tmp = "unknown"
            try:
                conf = max(0.0, min(1.0, float(r.get("confidence", 0.5))))
            except (TypeError, ValueError):
                conf = 0.5
            trows.append({"by": it["n"], "target": j, "date": it["date"], "kind": kind, "scope": scope, "temporal": tmp,
                          "sha": it["sha"], "start": start, "end": end, "quote": clean(quote), "ev": e, "part": part,
                          "conf": conf, "item": i, "how": how, "fam": it["why"]})
            certs[(it["sha"], st0, en0)] = clean(window)
            st["admitted_rows"] += 1
    best = {}
    for t in trows:
        k = (t["by"], t["target"], t["kind"], t["scope"])
        if k not in best or t["conf"] > best[k]["conf"]:
            best[k] = t
    used = set()
    rows = sorted(best.values(), key=lambda t: (t["by"], t["target"], t["start"]))
    with open(os.path.join(a.out, "treatments_new.tsv"), "w", encoding="utf-8", newline="\n") as fo, \
            open(os.path.join(a.out, "treatments_items_new.tsv"), "w", encoding="utf-8", newline="\n") as fi:
        for t in rows:
            tid = f"t:{t['by']}:{t['target']}:{t['start']}"
            while tid in used:
                tid += "b"
            used.add(tid)
            fo.write("\t".join(map(str, [tid, t["by"], t["target"], t["date"], t["kind"], t["scope"], t["temporal"], 1,
                                         t["sha"], t["start"], t["end"], t["quote"], t["ev"], t["part"],
                                         a.reader, f"{t['conf']:.2f}"])) + "\n")
            fi.write(f"{tid}\t{t['item']}\t{t['how']}\t{t['fam']}\n")
    with open(os.path.join(a.out, "cert_text_new.tsv"), "w", encoding="utf-8", newline="\n") as fo:
        for (sha, s0, e0), w in sorted(certs.items()):
            fo.write(f"{sha}\t{s0}\t{e0}\t{w}\n")
    rej.close()
    st["treatments_new"] = len(rows)
    st["by_kind_scope"] = {f"{k}|{s}": v for (k, s), v in sorted(collections.Counter(
        (t["kind"], t["scope"]) for t in rows).items())}
    st["by_why"] = dict(collections.Counter(t["fam"].split(":")[1] for t in rows))
    with open(os.path.join(a.out, "stats.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, indent=1)
    print(json.dumps(st, indent=0))


if __name__ == "__main__":
    main()
