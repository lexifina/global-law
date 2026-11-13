"""Blind audit by Claude subagents reading the decision text (git objects), per pattern.

    python audit_prep.py make p1|p2|p3|p4|p5      -> hunt/audit/<p>/gNN/{INSTRUCTIONS.md, I01.txt..}; hunt/audit/<p>/key.json
    python audit_prep.py score p1|...             -> hunt/audit/<p>/audit.tsv + precision with a Wilson 95% interval

Each audit mixes three groups the auditor cannot tell apart: `flagged` (a random sample of the instances the pattern
reports; the precision estimate), `top` (the candidates for the top-10 list, verified one by one) and `decoy` (rows
the pattern did NOT report). key.json (outside the agent dirs) holds the group of each item.
"""
import csv, json, os, random, sys
from collections import Counter, defaultdict
import hcommon as C

AUD = os.path.join(C.HUNT, "audit")
PER_AGENT = 7


def L(name):
    p = os.path.join(C.HWORK, name)
    return [json.loads(l) for l in open(p, encoding="utf-8")] if os.path.exists(p) else []


def excerpt(text, spans, cap=34000, head=5000, tail=2000, w=4200, maxw=4):
    if len(text) <= cap:
        return text
    cuts = [(0, head)]
    for s, e in spans[:maxw]:
        cuts.append((max(0, s - w), min(len(text), e + w)))
    cuts.append((len(text) - tail, len(text)))
    cuts.sort()
    merged = []
    for s, e in cuts:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(e, merged[-1][1]))
        else:
            merged.append((s, e))
    return "\n\n[... text omitted ...]\n\n".join(text[s:e] for s, e in merged)


def spans_of(text, cites, name):
    return [(s, e) for s, e, _ in C.locate(text, cites, name, width=10)]


COMMON = """You are auditing candidate findings about US court decisions. The items in this directory are a MIX: some are
believed to be true instances of the pattern below and some are not. You are not told which. Judge every item only on
the decision text given in its file (and your own knowledge of the law and of the named cases where the file is
silent; say so in the explanation when you rely on it). Be strict: `confirmed` means every limb of the predicate is
shown; `not_confirmed` means a limb fails; `unclear` only when the text given cannot settle it.

Read every item file I*.txt in this directory in full. Use only the Read and Write tools; no web, no scripts, no other
files. Then write ONE file `answers.jsonl` in this directory, one JSON object per line, one line per item:

    {"id": "Inn", "verdict": "confirmed"|"not_confirmed"|"unclear", %s, "explanation": "<one line, <= 45 words: what the citing court did and why the limb holds or fails>"}

Reply only with the number of lines written.

# Pattern

%s
"""

PRED = {
    "p1": ('"earlier_negated_on_point": true|false, "relies": true|false, "acknowledges": true|false, "same_case": true|false',
           "ZOMBIE PRECEDENT. The citing opinion relies on an earlier decision as authority for a legal proposition "
           "after that decision had been overruled, abrogated, disapproved, receded from, reversed or vacated, without "
           "acknowledging it. Limbs: (1) earlier_negated_on_point: before the citing opinion's date, the earlier decision "
           "was negated on the very proposition the citing opinion takes from it (or as a whole, e.g. reversed or vacated "
           "outright) - check the NEGATING DECISION EXCERPT; a negation limited to a different point fails this limb; "
           "(2) relies: the citing court uses it as authority for that proposition (not as history, a party's argument, "
           "a contrast, or something it distinguishes or rejects); (3) acknowledges = false: nowhere near the citation "
           "does the citing opinion note the negative history or cite the negating decision on the point; (4) same_case "
           "= false: the citing opinion is not part of the same litigation. confirmed iff 1 and 2 hold and 3, 4 are false."),
    "p2": ('"cited_is_unpublished": true|false, "treats_as_binding": true|false, "same_case": true|false',
           "UNPUBLISHED OPINION TREATED AS BINDING. Limbs: (1) cited_is_unpublished: the cited decision really is an "
           "unpublished / non-precedential / table / summary-order / memorandum disposition that its court's rules make "
           "non-binding (check the CITED DECISION block: a full reasoned opinion printed in an official reporter is "
           "published, whatever our data says); (2) treats_as_binding: the citing court says or plainly treats it as "
           "binding or controlling precedent it must follow (\"we are bound by\", \"controls\", \"forecloses\", \"under our "
           "precedent in\"), not merely as persuasive, illustrative or consistent authority; (3) same_case = false (not "
           "law of the case / res judicata in the same litigation). confirmed iff 1 and 2 hold and 3 is false."),
    "p3": ('"departs": true|false, "bench": "panel"|"en_banc_or_full_court"|"unclear", "recognised_exception": true|false',
           "PANEL OVERRULES PANEL WITHOUT EN BANC. Limbs: (1) departs: the later decision itself overrules, abrogates, "
           "recedes from, disapproves or refuses to follow the holding of an earlier published decision OF THE SAME COURT "
           "(same district or division where precedent binds only within it) - not merely distinguishes or limits it, and "
           "not a decision of a different court or district; (2) bench = panel: the later decision was decided by a panel, "
           "not by the court en banc / in bank / as a whole court (look at the judges line and any 'en banc' marking; a "
           "court whose every case is heard by all its judges is full court); (3) recognised_exception = false: the "
           "opinion gives no recognised ground for a panel to depart (intervening Supreme Court / higher-court / en banc "
           "authority, a change of statute or rule, circulation to or approval by the full court, the earlier case being "
           "contrary to even earlier binding precedent, dicta, unpublished); (4) the court followed a prior-panel rule and "
           "had an en banc procedure at the time (use your knowledge; if it did not, say so and answer not_confirmed). "
           "confirmed iff all hold."),
    "p4": ('"applies_superseded_holding": true|false, "notes_statute": true|false, "conduct_after_effective": "yes"|"no"|"unknown"',
           "SUPERSEDED HOLDING APPLIED TO LATER CONDUCT (two-date error). A statute overrode a Supreme Court holding for "
           "conduct (or claims, or filings, as the statute provides) on or after a date. Limbs: (1) "
           "applies_superseded_holding: the citing court applies the very holding the statute overrode (see SCOPE) to "
           "decide the case - not an unaffected holding of the same decision, not history; (2) conduct_after_effective = "
           "yes: the conduct / claim / filing governed is on or after the date from which the statute applies (read the "
           "dates in the opinion); (3) notes_statute = false: the opinion does not account for the statute on that point. "
           "confirmed iff 1 holds, 2 is yes and 3 is false."),
    "p5": ('"cited_on_losing_side": true|false, "relies_on_resolved_point": true|false, "notes_scotus": true|false',
           "LOSING SIDE OF A RESOLVED SPLIT. The Supreme Court resolved a conflict among the courts of appeals. Limbs: "
           "(1) cited_on_losing_side: the cited court of appeals decision answered the resolved question the way the "
           "Supreme Court rejected; (2) relies_on_resolved_point: the citing decision (decided after the Supreme Court) "
           "relies on the cited decision for its answer to that very question (not for another point); (3) notes_scotus = "
           "false: the citing decision does not mention the Supreme Court decision or the abrogation. confirmed iff 1 "
           "and 2 hold and 3 is false."),
}


def pick(flag, top, decoy, nflag, ntop, ndecoy, rnd):
    f = rnd.sample(flag, min(nflag, len(flag)))
    used = {x["hkey"] for x in f}
    t = [x for x in top if x["hkey"] not in used][:ntop]
    d = rnd.sample(decoy, min(ndecoy, len(decoy)))
    items = [(x, "flagged") for x in f] + [(x, "top") for x in t] + [(x, "decoy") for x in d]
    rnd.shuffle(items)
    return items


def rows_p1():
    ins = {r["hkey"]: r for r in L("p1_llm_in.jsonl")}
    z, nz = [], []
    for o in L("p1_llm_out.jsonl"):
        a = o["ans"]
        if "error" in a or o["key"] not in ins:
            continue
        r = dict(ins[o["key"]], ans=a)
        if r["stratum"] not in ("O-silent", "V-silent"):
            continue
        (z if a["zombie"] else nz).append(r)
    zo = [r for r in z if r["stratum"] == "O-silent"]
    zv = [r for r in z if r["stratum"] == "V-silent"]
    known = {int(r[5]) for r in C.read_tsv(os.path.join(C.HUNT, "data", "known_overrulings.tsv")) if r[5].isdigit()}
    bind = ("H1", "F1", "F7circuit", "hStrong", "hWithinUnit", "E1")
    def score(r):
        p = r["path"].split(">")[-1]
        s = 0
        s += 3 if any(p == b or r["path"].endswith(">" + b) for b in bind) else 0
        s += 2 if r["wscope"] == "all" else 0
        s += 2 if int(r["citing_date"]) - int(r["neg_from"]) >= 30000 else 0
        s += 2 if int(r["citing_date"]) >= 19700101 else 0
        s += 1 if "Supreme Court" in (r["citing_court_name"] or "") else 0
        s += 2 if r["cited"] in known else 0
        return s
    top, seen = [], set()
    for r in sorted(zo, key=lambda r: (-score(r), -int(r["citing_date"]))):
        if r["cited"] in seen or r["citing_court_name"] in {t["citing_court_name"] for t in top[-2:]}:
            continue
        seen.add(r["cited"])
        top.append(r)
    return zo, zv, top, nz


def text_p1(r, meta, texts, cites):
    ct = texts.get(r["citing"], "")
    b = C.body(ct)
    sp = spans_of(b, cites.get(r["cited"], []), r["cited_name"])
    a = r.get("actor")
    at = texts.get(int(a), "") if a not in (None, "-", "") else ""
    neg = ""
    if at:
        ab = C.body(at)
        asp = spans_of(ab, cites.get(r["cited"], []), r["cited_name"])
        neg = "\n[...]\n".join(ab[max(0, s - 1800):e + 1800] for s, e in asp[:2]) or ab[:2500]
    return ("EARLIER DECISION: %s, %s (%s, decided %s)\n"
            "NEGATING EVENT (our data): %s, taking effect %s, by %s, %s (decided %s)\nNEGATING WORDS (our reader's quote): %s\n\n"
            "===== NEGATING DECISION EXCERPT =====\n%s\n\n"
            "===== CITING OPINION: %s, %s (%s, decided %s) =====\n%s\n"
            % (r["cited_name"], r["cited_cite"], r["cited_court_name"], r["cited_date"], r.get("wkind"), r["neg_from"],
               r.get("actor_name"), r.get("actor_cite"), r.get("actor_date"), r.get("wquote", "-"), neg or "(not available)",
               r["citing_name"], r["citing_cite"], r["citing_court_name"], r["citing_date"], excerpt(b, sp)))


def rows_p3():
    ins = {r["hkey"]: r for r in L("p3_in.jsonl")}
    rows = list(csv.DictReader(open(os.path.join(C.HUNT, "data", "p3_panel.tsv"), encoding="utf-8"), delimiter="\t"))
    flag, decoy = [], []
    for x in rows:
        k = "panel|%s|%s" % (x["citing"], x["cited"])
        if k not in ins:
            continue
        r = dict(ins[k], final=x["violation_final"], reason=x["reason"])
        (flag if x["violation_final"] == "1" else decoy).append(r)
    fed = [r for r in flag if "United States Court of Appeals" in r["court_name"]]
    top, seen = [], Counter()
    for r in sorted(fed, key=lambda r: -int(r["citing_date"])):
        if seen[r["court_name"]] >= 3:
            continue
        seen[r["court_name"]] += 1
        top.append(r)
    return flag, top, decoy


def text_p3(r, meta, texts, cites):
    b = C.body(texts.get(r["citing"], ""))
    fm = C.front(texts.get(r["citing"], ""))
    sp = spans_of(b, cites.get(r["cited"], []), r["cited_name"])
    eb = C.body(texts.get(r["cited"], ""))
    efm = C.front(texts.get(r["cited"], ""))
    return ("COURT: %s\nEARLIER DECISION: %s, %s (decided %s)\nLATER DECISION: %s, %s (decided %s)\n\n"
            "===== EARLIER DECISION: front matter and opening =====\n%s\n%s\n\n"
            "===== LATER DECISION: front matter =====\n%s\n\n===== LATER DECISION: text =====\n%s\n"
            % (r["court_name"], r["cited_name"], r["cited_cite"], r["cited_date"], r["citing_name"], r["citing_cite"],
               r["citing_date"], efm[:700], eb[:1500], fm[:900], excerpt(b, sp, head=6000, tail=3000)))


def rows_p2():
    ins = {r["hkey"]: r for r in L("p2_in.jsonl")}
    flag, decoy = [], []
    for o in L("p2_out.jsonl"):
        a = o["ans"]
        if "error" in a or o["key"] not in ins:
            continue
        r = dict(ins[o["key"]], ans=a, reader=o.get("model"))
        (flag if a["violation"] else decoy).append(r)
    strict = [r for r in flag if r["force"] in ("notCitable", "none", "citableNoWeight")]
    top, seen = [], Counter()
    for r in sorted(strict, key=lambda r: (r["force"] != "notCitable", -int(r["citing_date"]))):
        if seen[r["citing_court_name"]] >= 3:
            continue
        seen[r["citing_court_name"]] += 1
        top.append(r)
    return flag, top, decoy


def text_p2(r, meta, texts, cites):
    b = C.body(texts.get(r["citing"], ""))
    sp = spans_of(b, cites.get(r["cited"], []), r["cited_name"])
    et = texts.get(r["cited"], "")
    eb = C.body(et)
    return ("CITED DECISION: %s, %s (%s, decided %s)\nOUR DATA: publication = %s; force of such a decision on its own "
            "court under that court's rules = %s\n\n===== CITED DECISION: front matter, length %d characters, opening =====\n%s\n%s\n\n"
            "===== CITING OPINION: %s, %s (%s, decided %s) =====\n%s\n"
            % (r["cited_name"], r["cited_cite"], r["cited_court_name"], r["cited_date"], r["cited_pub"], r["force"],
               len(eb), C.front(et)[:800], eb[:1500], r["citing_name"], r["citing_cite"], r["citing_court_name"],
               r["citing_date"], excerpt(b, sp, cap=30000, head=3000)))


def rows_p4():
    """flagged = the readers' error rows; flagged_runner = the runner's own appliesSupersededHolding findings (26, all
    citing the 11th Cir. Ledbetter); top = rows where the old rule is applied without noting the statute and the
    passages did not settle the conduct date (candidates only the full text can settle); decoy = old rule applied to
    conduct before the effective date."""
    ins = {r["hkey"]: r for r in L("p4_in.jsonl")}
    import claude_batches as B
    import p4_superseded as P4
    flag, top, decoy = [], [], []
    for o in L("p4_out.jsonl"):
        a = o["ans"]
        if isinstance(a.get("error"), str) or o["key"] not in ins:
            continue
        r = dict(ins[o["key"]], ans=a)
        r["holding"] = B.HOLDING_MORE.get(r["cited"], r.get("holding"))
        if a["error"]:
            flag.append(r)
        elif a["applies_old_rule"] and not a["notes_statute"]:
            (decoy if a["conduct_after_effective"] == "no" else top).append(r)
    led = None
    for r in ins.values():
        if r["cited"] in (441098, 6239607):
            led = r
    runner = []
    pairs = [(int(r[1]), int(r[2])) for r in C.read_tsv(os.path.join(C.OUT, "findings.tsv")) if r[0] == "appliesSupersededHolding"]
    meta = C.nodes({a for a, _ in pairs} | {b for _, b in pairs})
    for a, b in pairs:
        mc, md = meta[a], meta[b]
        runner.append(dict(hkey="super|%s|%s" % (a, b), citing=a, cited=b, holding=P4.HOLDING[441098],
                           law="Lilly Ledbetter Fair Pay Act of 2009 (Pub. L. 111-2)", effective=20090129,
                           conduct_from=20070528, cited_name=md["name"], cited_cite=md["cite"].split("|")[0],
                           cited_date=md["date"], citing_name=mc["name"], citing_cite=mc["cite"].split("|")[0],
                           citing_court_name=mc["court_name"], citing_date=mc["date"]))
    return flag, top, decoy, runner


def text_p4(r, meta, texts, cites):
    b = C.body(texts.get(r["citing"], ""))
    sp = spans_of(b, cites.get(r["cited"], []), r["cited_name"])
    return ("OLD DECISION: %s, %s (decided %s)\nSUPERSEDED HOLDING AND SCOPE: %s\nSTATUTE: %s; effective %s; applies to "
            "conduct/claims from %s\n\n===== CITING OPINION: %s, %s (%s, decided %s) =====\n%s\n"
            % (r["cited_name"], r["cited_cite"], r["cited_date"], r.get("holding"), r["law"], r["effective"],
               r["conduct_from"], r["citing_name"], r["citing_cite"], r["citing_court_name"], r["citing_date"],
               excerpt(b, sp, head=7000)))


def rows_p5():
    ins = {r["hkey"]: r for r in L("p5_in.jsonl")}
    flag, decoy = [], []
    for o in L("p5_out.jsonl"):
        a = o["ans"]
        if "error" in a or o["key"] not in ins:
            continue
        r = dict(ins[o["key"]], ans=a)
        if a["zombie"]:
            flag.append(r)
        elif a["relies_on_point"]:
            decoy.append(r)
    top, seen = [], Counter()
    for r in sorted(flag, key=lambda r: ("Court of Appeals" not in r["citing_court_name"], -int(r["citing_date"]))):
        if seen[r["scotus"]] >= 2:
            continue
        seen[r["scotus"]] += 1
        top.append(r)
    return flag, top, decoy


def text_p5(r, meta, texts, cites):
    b = C.body(texts.get(r["citing"], ""))
    sp = spans_of(b, cites.get(r["cited"], []), r["cited_name"])
    eb = C.body(texts.get(r["cited"], ""))
    return ("SUPREME COURT: %s, %s (decided %s)\nQUESTION RESOLVED AND ANSWER (our reader): %s\n"
            "CITED COURT OF APPEALS DECISION: %s, %s (decided %s)\n\n===== CITED DECISION: opening =====\n%s\n\n"
            "===== CITING DECISION: %s, %s (%s, decided %s) =====\n%s\n"
            % (r["scotus_name"], r["scotus_cite"], r["scotus_date"], r["qa"], r["cited_name"], r["cited_cite"],
               r["cited_date"], eb[:2500], r["citing_name"], r["citing_cite"], r["citing_court_name"], r["citing_date"],
               excerpt(b, sp, cap=30000, head=3000)))


def rows_second(p):
    """Audit of the second-read (two-stage) result: flagged = rows both readers reported; decoy = rows the first reader
    reported and the second rejected."""
    inname, outname, field = {"p1b": ("p1_llm_in.jsonl", "p1_second_out.jsonl", "zombie"),
                              "p2b": ("p2b_in.jsonl", "p2b_out.jsonl", "violation"),
                              "p3b": ("p3b_in.jsonl", "p3b_out.jsonl", "violation")}[p]
    ins = {r["hkey"]: r for r in L(inname)}
    prior = set()
    for q in ("p1", "p2", "p3"):
        kp = os.path.join(AUD, q, "key.json")
        if os.path.exists(kp):
            prior |= {v["hkey"] for v in json.load(open(kp, encoding="utf-8")).values()}
    flag, decoy = [], []
    for o in L(outname):
        if o["key"] not in ins or o["key"] in prior:
            continue
        r = dict(ins[o["key"]], ans=o["ans"], reader="claude-subagent")
        r.setdefault("citing_court_name", r.get("court_name"))
        (flag if o["ans"].get(field) else decoy).append(r)
    return flag, decoy


def make(p):
    rnd = random.Random(1112 + int(p[1]) + (50 if p.endswith("b") else 0))
    if p.endswith("b"):
        flag, decoy = rows_second(p)
        items = pick(flag, [], decoy, 22, 0, 6, rnd)
        tf = {"p1b": text_p1, "p2b": text_p2, "p3b": text_p3}[p]
    elif p == "p1":
        zo, zv, top, nz = rows_p1()
        items = pick(zo, top, nz, 20, 12, 8, rnd)
        used = {x["hkey"] for x, _ in items}
        items += [(x, "flagged_vacated") for x in rnd.sample([r for r in zv if r["hkey"] not in used], 10)]
        rnd.shuffle(items)
        tf = text_p1
    elif p == "p4":
        flag, top, decoy, runner = rows_p4()
        items = pick(flag, top, decoy, 20, 24, 6, rnd)
        items += [(x, "flagged_runner") for x in rnd.sample(runner, min(20, len(runner)))]
        rnd.shuffle(items)
        tf = text_p4
    else:
        flag, top, decoy = {"p2": rows_p2, "p3": rows_p3, "p5": rows_p5}[p]()
        items = pick(flag, top, decoy, 20, 12, 8, rnd)
        tf = {"p2": text_p2, "p3": text_p3, "p5": text_p5}[p]
    need = set()
    for r, _ in items:
        need |= {r["citing"], r["cited"]}
        if p == "p1" and r.get("actor") not in (None, "-", ""):
            need.add(int(r["actor"]))
    meta = C.nodes(need)
    texts = C.fetch(meta)
    cites = C.cites_of(need)
    d0 = os.path.join(AUD, p)
    os.makedirs(d0, exist_ok=True)
    key = {}
    for gi in range(0, len(items), PER_AGENT):
        g = "g%02d" % (gi // PER_AGENT)
        d = os.path.join(d0, g)
        os.makedirs(d, exist_ok=True)
        for j, (r, grp) in enumerate(items[gi:gi + PER_AGENT]):
            iid = "I%02d" % (j + 1)
            with open(os.path.join(d, iid + ".txt"), "w", encoding="utf-8", newline="\n") as f:
                f.write(tf(r, meta, texts, cites))
            key["%s/%s" % (g, iid)] = dict(group=grp, hkey=r["hkey"], citing=r["citing"], cited=r["cited"],
                                           citing_name=r["citing_name"], citing_cite=r["citing_cite"],
                                           citing_date=r["citing_date"], citing_court=r.get("citing_court_name") or r.get("court_name"),
                                           cited_name=r["cited_name"], cited_cite=r["cited_cite"],
                                           reader=(r.get("reader") or "azure gpt-5.4-mini" if p in ("p1", "p3") else r.get("reader")))
        with open(os.path.join(d, "INSTRUCTIONS.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(COMMON % PRED[p[:2]])
    json.dump(key, open(os.path.join(d0, "key.json"), "w", encoding="utf-8", newline="\n"), indent=0)
    print(p, "items", len(items), Counter(g for _, g in items), "dirs", (len(items) + PER_AGENT - 1) // PER_AGENT)


def score(p):
    d0 = os.path.join(AUD, p)
    key = json.load(open(os.path.join(d0, "key.json"), encoding="utf-8"))
    rows = []
    for g in sorted(os.listdir(d0)):
        ap = os.path.join(d0, g, "answers.jsonl")
        if not os.path.exists(ap):
            continue
        for line in open(ap, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                j = json.loads(line)
            except Exception:
                continue
            k = key.get("%s/%s" % (g, j.get("id")))
            if not k:
                continue
            rows.append([g + "/" + j["id"], k["group"], j.get("verdict"), k["citing"], k["citing_name"][:70], k["citing_cite"],
                         k["citing_date"], k["citing_court"], k["cited"], k["cited_name"][:70], k["cited_cite"],
                         json.dumps({a: b for a, b in j.items() if a not in ("id", "verdict", "explanation")}),
                         j.get("explanation", "")])
    C.write_tsv(os.path.join(d0, "audit.tsv"), rows,
                ["item", "group", "verdict", "citing", "citing_name", "citing_cite", "citing_date", "citing_court",
                 "cited", "cited_name", "cited_cite", "checks", "explanation"])
    out = {}
    for grp in sorted({r[1] for r in rows}):
        v = [r[2] for r in rows if r[1] == grp]
        k = sum(x == "confirmed" for x in v)
        pr, lo, hi = C.wilson(k, len(v))
        out[grp] = dict(n=len(v), confirmed=k, unclear=sum(x == "unclear" for x in v), precision=round(pr, 3),
                        ci95=[round(lo, 3), round(hi, 3)])
    json.dump(out, open(os.path.join(d0, "audit.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    print(p, json.dumps(out))


if __name__ == "__main__":
    {"make": make, "score": score}[sys.argv[1]](sys.argv[2])
