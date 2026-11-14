"""Round 8 ownact: reader answers (READER_BRIEF_OWNACT8.md) -> DESIGN7 section 4 rows for round8/certify8.py.

    python -X utf8 round8/agents/ownact/answers_to_rows8.py [--ans DIR] [--packs 000,001] [--out rows.jsonl]

General rules (no list of cases; no answer key read):
  kind     reader kind overruled / disapproved / recededFrom / abrogated is kept only when the main quote holds that
           family's own stem (overrul / disapprov / reced / abrogat); otherwise, and for kind "rejected", the row is
           an operative-words row: kind disapproved, claim operativeWords, scope partialUnknown (round 7: operative
           "part" 0.988, operative "whole" 0.33 -> never whole).
  main     the reader's quote found (whitespace / quote-mark / hyphenation tolerant) in the git-HEAD text inside
           [s0 - 60, s1 + 60) of the item's FOCUS sentence; the text's own characters are used. Not found -> reject.
  ev       the target's evidence (the item's own cite:/name: key, else the target's caption words standing in the
           quote) must stand INSIDE the main quote (one-sentence row): round 7 refused window-only naming (0.857).
           Else, for the overrule family only, a joined `antecedent` line: the reader's `naming` text found before
           the act sentence (gap <= 300), the evidence inside it, an anaphor in the main quote (certify8 checks).
           Else the row is not written (`window_only`).
  part     the item's opinion part (majority / perCuriam / plurality; others refused by certify8).
  pairs    a (by, target) pair with an admitted negative v3 row is not written (`base_has_pair`); one row per
           (by, target): the first in pack order.
Output: rows.jsonl, rows_rejects.tsv, rows_stats.json (in the folder of --out).
"""
import argparse
import collections
import glob
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402
sys.path.insert(0, os.path.join(C2, "round5", "recog"))
import recog_common as RC  # noqa: E402
sys.path.insert(0, HERE)
import port8  # noqa: E402

C = L.reader_common()
NL = "\n"
FAM = {"overruled": "overrul", "disapproved": "disapprov", "recededFrom": "reced", "abrogated": "abrogat"}
PART_OUT = {"majority": "majority", "majority~": "majority", "perCuriam": "perCuriam", "plurality": "plurality"}
GAP = 300
# operative rows keep only an act verb (strong or follow); state words alone ("was wrongly decided", "is no longer
# controlling", "should no longer be relied upon") are not written (audit r8o01: 3 of 4 errors; round 7: weak verbs
# 0.45, operative whole 0.33)
OPV_KEEP = re.compile(r"reject|repudiat|disavow|abandon|overturn|discard|follow")
CUES = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/cues/cue_table.json")


def lower(s):
    return RC.ascii_lower(s)


def compact(s):
    return re.sub(r"[^0-9a-z]", "", lower(s))


def words(s):
    return " " + " ".join(re.findall(r"[0-9a-z]+", lower(s))) + " "


def ev_in(ev, ctx):
    if ev.startswith("cite:"):
        c = compact(ev[5:])
        return c != "" and c in compact(ctx)
    if ev.startswith("name:"):
        toks = [t for t in (compact(x) for x in lower(ev[5:]).split(" ")) if len(t) >= 3]
        w = words(ctx)
        return bool(toks) and all((" " + t + " ") in w for t in toks)
    return False


CAPTION = re.compile(r"((?:[A-Z][\w.'’&-]*\s+){0,2}[A-Z][\w.'’&-]*)\s+v\.?\s+([A-Z][\w.'’&-]*(?:\s+[A-Z][\w.'’&-]*){0,2})")


def _similar(a, b):
    import difflib
    return a[:4] == b[:4] or difflib.SequenceMatcher(None, a, b).ratio() >= 0.7


def _side_tokens(s):
    return {t.lower() for t in (C.name_tokens(s) | C.short_name_tokens(s))}


def name_consistent(quote, ev, tname):
    """(round 7 antecedent rule) a name: evidence word must not stand only inside another case's caption."""
    toks = [t for t in ev[5:].split(" ") if len(t) >= 3]
    if not toks:
        return False
    sides = [_side_tokens(s) for s in re.split(r"\s+v\.?\s+|\s+vs\.?\s+", tname or "")]
    allt = set().union(*sides) if sides else set()
    tok = toks[0]
    occ = list(re.finditer(r"\b%s\b" % re.escape(tok), quote))
    if not occ:
        return False
    caps = [(m.start(), m.end(), m.group(1), m.group(2)) for m in CAPTION.finditer(quote)]
    for o in occ:
        cap = next((c for c in caps if c[0] <= o.start() < c[1]), None)
        if cap is None:
            return True
        a, b = _side_tokens(cap[2]), _side_tokens(cap[3])
        other = b if tok.lower() in a else a
        if not other or any(_similar(x, t) for x in other for t in allt):
            return True
    return False


def _words_cap(s):
    stop = {w.lower() for w in C.STOPW} | {"the", "and", "for", "nat", "ins", "svcs", "inc", "corp", "ltd", "co"}
    return {w.lower() for w in re.findall(r"[A-Za-z]{3,}", s or "") if w.lower() not in stop}


def cite_consistent(ctx, ev, tname):
    """(round 7 antecedent rule) a cite: evidence must not sit right after the caption of ANOTHER case: if the 120
    characters before the citation hold an "A v. B" caption ending just before it and no caption word is similar
    to a word of the target's caption, the citation key names a different decision (a shared page). No caption
    there -> consistent."""
    c = compact(ev[5:])
    for m in RC.RC.CITE_RX.finditer(ctx):
        k = RC.RC.cite_key(m)
        if not k or compact(k) != c:
            continue
        pre = ctx[max(0, m.start() - 120):m.start()]
        vs = list(re.finditer(r"\bv\.?\s+(?=[A-Z])", pre))
        if not vs:
            return True
        v = vs[-1]
        right = pre[v.end():]
        if re.search(r"[;)\]]|\bsupra\b|\bid\.", right):
            return True
        lm = re.search(r"((?:[A-Z][\w.'’&-]*\s+){0,2}[A-Z][\w.'’&-]*)\s*$", pre[:v.start()])
        ws = _words_cap(lm.group(1) if lm else "") | _words_cap(right)
        tt = _words_cap(tname)
        if not ws or not tt or any(_similar(w, t) for w in ws for t in tt):
            return True
        return False
    return True


def evidence(x, quote, acting_name, ctx=None):
    """The evidence for target x inside quote, or None. ctx (the quote with up to 200 characters before it) is
    used for the caption check of a cite: evidence."""
    ev = x.get("ev", "")
    ctx = ctx if ctx is not None else quote
    if ev and ev_in(ev, quote) and (not ev.startswith("name:") or name_consistent(quote, ev, x["name"])) \
            and (not ev.startswith("cite:") or cite_consistent(ctx, ev, x["name"])):
        return ev
    for k, c in RC.cite_keys_in(quote):
        if ev.startswith("cite:") and c == compact(ev[5:]) and cite_consistent(ctx, "cite:" + k, x["name"]):
            return "cite:" + k
    ne = RC.name_evidence(x["name"], acting_name, quote)
    if ne and ev_in(ne, quote) and name_consistent(quote, ne, x["name"]):
        return ne
    return None


def load_answers(ans_dir, packs):
    out = {}
    files = sorted(glob.glob(os.path.join(ans_dir, "ans_*.jsonl")))
    for p in files:
        pk = os.path.basename(p)[4:7]
        if packs and pk not in packs:
            continue
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            out.setdefault(str(r.get("id")), r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ans", default=os.path.join(HERE, "ans"))
    ap.add_argument("--items", default=os.path.join(HERE, "items8.jsonl.gz"))
    ap.add_argument("--packs", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "rows.jsonl"))
    a = ap.parse_args()
    packs = set(x for x in a.packs.split(",") if x)
    answers = load_answers(a.ans, packs)
    items = {}
    order = {}
    for k, line in enumerate(gzip.open(a.items, "rt", encoding="utf-8")):
        it = json.loads(line)
        if it["id"] in answers:
            items[it["id"]] = it
            order[it["id"]] = k
    st = collections.Counter()
    st["answers"] = len(answers)
    st["answers_matched"] = len(items)
    pairs = port8.admitted_pairs()
    cues = json.load(open(CUES, encoding="utf-8"))
    anaphor = cues["anaphor"]
    want = [i for i in items if answers[i].get("own_act") is True]
    st["own_act_true"] = len(want)
    texts = {}
    nodes = sorted({items[i]["n"] for i in want})
    for k in range(0, len(nodes), 1500):
        texts.update(L.fetch_texts(nodes[k:k + 1500]))
    rows, rejects, seen = [], [], set()
    for i in sorted(want, key=lambda x: order[x]):
        r, it = answers[i], items[i]
        tl = [t for t in (r.get("targets") or []) if isinstance(t, str) and re.fullmatch(r"T\d+", t)
              and 1 <= int(t[1:]) <= len(it["targets"])]
        if not tl:
            st["rej_no_target"] += 1
            rejects.append([i, "-", "no_target", it["n"], "-", r.get("kind", "")])
            continue
        sha, text = texts.get(it["n"], (None, None))
        if text is None or sha != it["sha_head"]:
            st["rej_text_changed"] += len(tl)
            continue
        s0, s1 = it["s0"], it["s1"]
        q = (r.get("quote") or "").strip()
        lo = max(0, s0 - 60)
        seg = text[lo:min(len(text), s1 + 60)]
        fq = RC.find_quote(seg, q, s0 - lo, hyphen=True) if q else None
        if not fq:
            for T in tl:
                st["rej_quote_not_found"] += 1
                rejects.append([i, T, "quote_not_found", it["n"], it["targets"][int(T[1:]) - 1]["node"],
                                r.get("kind", "")])
            continue
        m0, m1 = lo + fq[0], lo + fq[1]
        while m1 > m0 and text[m1 - 1] in " \n":
            m1 -= 1
        while m0 < m1 and text[m0] in " \n":
            m0 += 1
        mq = L.norm(text[m0:m1])
        ml = lower(mq)
        part = PART_OUT.get(it["part"])
        acting = it["by"]["name"]
        kinds = r.get("kinds") if isinstance(r.get("kinds"), dict) else {}
        for T in tl:
            rk = kinds.get(T) or r.get("kind")
            if rk in FAM and FAM[rk] in ml:
                kind, claim, scope = rk, "-", ("all" if r.get("scope") == "all" else "partialUnknown")
            elif rk in FAM or rk == "rejected":
                kind, claim, scope = "disapproved", "operativeWords", "partialUnknown"
                st["operative_from_%s" % rk] += 1
            else:
                st["rej_bad_kind"] += 1
                continue
            x = it["targets"][int(T[1:]) - 1]
            tgt = x["node"]
            if claim == "operativeWords" and not OPV_KEEP.search(ml):
                # audit r8o01: "X was wrongly decided" (no act verb) fails; operative rows need an act verb
                st["rej_state_verb"] += 1
                rejects.append([i, T, "state_verb", it["n"], tgt, kind])
                continue
            ev = evidence(x, mq, acting, L.norm(text[max(0, m0 - 200):m1]))
            joined = []
            rule = "ownact:onesentence"
            if ev is None and claim == "-":
                nm = (r.get("naming") or {}).get(T)
                if nm:
                    jlo = max(0, m0 - 2000)
                    jseg = text[jlo:m0]
                    fj = RC.find_quote(jseg, nm.strip(), len(jseg), hyphen=True)
                    if fj:
                        j0, j1 = jlo + fj[0], jlo + fj[1]
                        while j1 > j0 and text[j1 - 1] in " \n":
                            j1 -= 1
                        jq = L.norm(text[j0:j1])
                        jev = evidence(x, jq, acting, L.norm(text[max(0, j0 - 200):j1]))
                        if jev and m0 - j1 <= GAP and any(p in ml for p in anaphor):
                            ev, rule = jev, "ownact:joined"
                            joined = [{"rel": "antecedent", "span": [j0, j1], "part": part, "label": "-"}]
                        else:
                            st["naming_unusable"] += 1
                    else:
                        st["naming_not_found"] += 1
            why = None
            if ev is None:
                why = "window_only"
            elif (it["n"], tgt) in pairs:
                why = "base_has_pair"
            elif (it["n"], tgt) in seen:
                why = "duplicate_pair"
            if why:
                st["rej_" + why] += 1
                rejects.append([i, T, why, it["n"], tgt, kind])
                continue
            seen.add((it["n"], tgt))
            rows.append({"rule": rule if claim == "-" else "ownact:operative", "table": "treatments",
                         "by": it["n"], "target": tgt, "kind": kind, "scope": scope, "main": [m0, m1],
                         "part": part, "ev": ev, "joined": joined, "claim": claim, "doctrine": "-",
                         "field_limit": "-", "anchor": None, "anchor_part": "-",
                         "reader": "claude-subagent:ownact8", "confidence": r.get("confidence"),
                         "note": "ownact8 %s %s verb=%s pat=%s pack=%s" % (i, T, r.get("verb", ""), it.get("pat", ""),
                                                                         it.get("pack", ""))})
            st["rows"] += 1
            st["rows_%s_%s" % (kind, claim)] += 1
    with open(a.out, "w", encoding="utf-8", newline=NL) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + NL)
    od = os.path.dirname(os.path.abspath(a.out))
    with open(os.path.join(od, "rows_rejects.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for rj in rejects:
            f.write("\t".join(str(v) for v in rj) + NL)
    json.dump(dict(st), open(os.path.join(od, "rows_stats.json"), "w", encoding="utf-8", newline=NL), indent=1)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
