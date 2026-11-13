"""Assemble issues.tsv, holdings.tsv, marks.tsv and holdings_cert_text.tsv (SCHEMA) from the raw model outputs.
Every quote is re-read from git and checked: the decision's sha1 equals the recorded text_sha and the quote is the exact
normalised substring at [start, end). Rows that fail are dropped and counted.

    python assemble.py
"""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text

OUT = os.path.join(text.WORK, "caselaw-lean-2", "data", "holdings_work")
DATA = os.environ.get("HOLD_DATA") or os.path.join(text.WORK, "caselaw-lean-2", "data")
RECOD = {1: 19470730, 3: 19480625, 4: 19470730, 9: 19470730, 11: 19791001, 13: 19540831, 17: 19780101, 26: 19540816,
         35: 19530101, 39: 19710701}
DISPO = re.compile(r"(?i)^(?:the )?(?:writ|appeal|petition|judgment|order|case|cause|decree)\b.{0,60}\b(?:dismissed|affirmed|reversed|remanded|vacated|denied|granted)\.?$")
USC_OK = re.compile(r"^(\d{1,2}):([0-9A-Za-z\-]+)\(([A-Za-z0-9]{1,6})\)")
MINCONF = 0.5


def _j(l):
    try:
        return json.loads(l)
    except json.JSONDecodeError:
        return None


def clean(s, n=300):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def systems():
    cs = {}
    for l in open(os.path.join(text.WORK, "lean-in-v3", "courts_named.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        cs[int(f[0])] = int(f[4])
    return cs


def norm_usc(u, date):
    m = USC_OK.match((u or "").strip().replace(" ", ""))
    if not m:
        return "-"
    t = int(m.group(1))
    if t in RECOD and date and date < RECOD[t]:
        return "-"
    return f"{t}:{m.group(2)}({m.group(3)})"


def domain(law, usc, court_sys):
    title = int(usc.split(":")[0]) if usc != "-" else 0
    if title == 35:
        return "federalPatent"
    if title == 26:
        return "federalTax"
    if law.startswith("federal"):
        return "federalGeneral"
    if law.startswith("state"):
        return f"stateLaw:{court_sys}" if court_sys > 0 else "unknown"
    return f"stateLaw:{court_sys}" if court_sys > 0 else "federalGeneral"


def main():
    cs = systems()
    want = {}  # nid -> list of row dicts awaiting verification
    issues = {}
    raw_files = [(g, f"raw_{g}.jsonl") for g in ("scotus", "scotus_plur", "scotus_mini", "scotus_luna", "treat", "treat_mini", "treat_luna")]
    dec_court = {}
    seen = set()
    hold_index = {}  # (nid, raw idx) -> issue_key
    stats = collections.Counter()
    pending = []
    for group, fn in raw_files:
        p = os.path.join(OUT, fn)
        if not os.path.exists(p):
            continue
        for l in open(p, encoding="utf-8"):
            r = _j(l)
            if r is None:
                continue
            if r["nid"] in seen or "error" in (r.get("out") or {}) or r.get("skip"):
                continue
            seen.add(r["nid"])
            pending.append(r)
    nids_needed = {r["nid"] for r in pending}
    splits = []
    sp = os.path.join(OUT, "raw_splits.jsonl")
    clusters = {}
    cp = os.environ.get("CLUSTERS") or os.path.join(OUT, "split_clusters.jsonl")
    if os.path.exists(cp):
        for l in open(cp, encoding="utf-8"):
            c = json.loads(l)
            clusters[c["key"]] = c
    if os.path.exists(sp):
        sseen = set()
        for l in open(sp, encoding="utf-8"):
            r = _j(l)
            if r is None:
                continue
            if "error" in (r.get("out") or {}) or (r["key"], r["nid"]) in sseen:
                continue
            sseen.add((r["key"], r["nid"]))
            splits.append(r)
            nids_needed.add(r["nid"])
    # decision form from the courts agent (decisions2.tsv), and Marks calls' list of issues a majority joined
    form2 = {}
    d2 = os.path.join(text.WORK, "caselaw-lean-2", "data", "decisions2.tsv")
    if os.path.exists(d2):
        pn = {r["nid"] for r in pending}
        for l in open(d2, encoding="utf-8"):
            f = l.split("	", 7)
            if f[1] == "2906" and int(f[0]) in pn:
                form2[int(f[0])] = f[6]
    for l in open(os.path.join(OUT, "scotus_scan.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        if f[5] == "plurality" and re.match(r"(?i)announced the judgment|delivered an opinion", f[6]):
            form2.setdefault(int(f[0]), "plurality")
    maj_idx = set()  # (nid, raw idx) the Marks reader says a majority joined
    mp0 = os.path.join(OUT, "raw_marks.jsonl")
    if os.path.exists(mp0):
        for l in open(mp0, encoding="utf-8"):
            r = _j(l)
            if r is None:
                continue
            for k in ((r.get("out") or {}).get("majority_issues") or []):
                m = re.match(r"^h(\d+)$", str(k).strip())
                if m:
                    maj_idx.add((r["nid"], int(m.group(1))))
    dates = {}
    for l in open(os.path.join(text.WORK, "lean-in-v3", "decisions.tsv"), encoding="utf-8"):
        a, c, d = l.rstrip("\n").split("\t")
        a = int(a)
        if a in nids_needed:
            dec_court[a] = int(c)
            dates[a] = int(d)

    rows = []  # (nid, start, end, sha, rowdict)
    # ---- decision holdings
    for r in pending:
        nid = r["nid"]
        cands = {c[0]: c for c in r["cands"]}
        hs = (r.get("out") or {}).get("holdings") or []
        label_key = {}
        for idx, h in enumerate(hs):
            stats["raw_holdings"] += 1
            lab = clean(h.get("issue"), 80)
            key = label_key.get(lab.lower())
            if key is None:
                key = f"d{nid}.i{idx}"
                label_key[lab.lower()] = key
            hold_index[(nid, idx)] = key
            if key not in issues:  # every read issue gets a row, so partial-overruling scopes can name it
                u0 = norm_usc(h.get("usc"), dates.get(nid, 0))
                issues[key] = [key, lab, domain(h.get("law") or "", u0, cs.get(dec_court.get(nid, 3160), 0)), u0, "-",
                               f"holdings:{r.get('model') or 'gpt-5.4-mini'}"]
            c = cands.get(h.get("s"))
            if c is None or c[4] != "C":
                stats["drop_bad_sentence"] += 1
                continue
            prop = clean(h.get("proposition"))
            if not prop or DISPO.match(prop):
                stats["drop_disposition"] += 1
                continue
            conf = float(h.get("confidence") or 0)
            if conf < MINCONF:
                stats["drop_low_conf"] += 1
                continue
            usc = norm_usc(h.get("usc"), dates.get(nid, 0))
            dom = domain(h.get("law") or "", usc, cs.get(dec_court.get(nid, 3160), 0))
            if key not in issues:
                issues[key] = [key, lab, dom, usc, "-", f"holdings:{r.get('model') or 'gpt-5.4-mini'}"]
            part = c[3]
            if form2.get(nid) == "plurality" and part == "majority":
                part = "plurality"
            if part == "plurality" and (nid, idx) in maj_idx:
                part = "majority"
                stats["plurality_part_relabelled_majority"] += 1
            rows.append((nid, c[1], c[2], r["sha"], {
                "hid": f"H{nid}.{idx}", "issue": key, "prop": prop, "answer": "-", "role": part, "part": part,
                "usc": usc, "reader": r.get("model") or "gpt-5.4-mini", "conf": round(conf, 2), "src": "decision"}))
    # ---- split holdings (statutory questions, canonical issue keys)
    verify = {}
    vp = os.path.join(OUT, "split_verify.jsonl")
    if os.path.exists(vp):
        for l in open(vp, encoding="utf-8"):
            v = _j(l)
            if v:
                verify[v["hid"]] = v
    for r in splits:
        o = r["out"]
        if not o.get("interprets"):
            continue
        cl = clusters.get(r["key"])
        if not cl:
            continue
        pos = {(n, h): i for i, (n, h) in enumerate(cl["item_index"])}
        asg = {it["id"]: it for it in cl["items"]}
        for hi, h in enumerate(o.get("holdings") or []):
            stats["raw_split_holdings"] += 1
            i = pos.get((r["nid"], hi))
            it = asg.get(i)
            if it is None or not (0 <= it["c"] < len(cl["questions"])):
                stats["split_unclustered"] += 1
                continue
            s = h.get("s")
            if not isinstance(s, int) or not (0 <= s < len(r["sents"])):
                stats["drop_bad_sentence"] += 1
                continue
            conf = float(h.get("confidence") or 0)
            if conf < MINCONF:
                stats["drop_low_conf"] += 1
                continue
            q = cl["questions"][it["c"]]
            key = f"usc:{r['key']}:q{it['c']}"
            ans = h["answer"]
            if it.get("neg"):
                ans = "no" if ans == "yes" else "yes"
            title = int(r["key"].split(":")[0])
            dom = "federalPatent" if title == 35 else "federalTax" if title == 26 else "federalGeneral"
            if key not in issues:
                issues[key] = [key, clean(q.get("label"), 80), dom, r["key"], clean(q.get("q"), 400),
                               f"splits:{cl.get('model')}"]
            a, z = r["sents"][s]
            part = "majority"
            hid = f"S{r['nid']}.{r['key']}.{hi}"
            reader = r.get("model") or "gpt-5.4-mini"
            v = verify.get(hid)
            if v is not None:  # second reading (split_verify.py) decides
                if not v.get("own_holding") or v.get("answer") not in ("yes", "no"):
                    stats["split_verify_rejected"] += 1
                    continue
                if v["answer"] != ans:
                    stats["split_verify_answer_changed"] += 1
                ans = v["answer"]
                conf = min(conf, float(v.get("confidence") or 0))
                reader = f"{reader}+{v.get('model')}"
                stats["split_verified"] += 1
            rows.append((r["nid"], a, z, r["sha"], {
                "hid": hid, "issue": key, "prop": clean(h.get("proposition")), "answer": ans,
                "role": part, "part": part, "usc": r["key"], "reader": reader,
                "conf": round(conf, 2), "src": "split", "unpub": r.get("unpub", 0), "kind": r["kind"],
                "date": r["date"]}))
    # ---- verify every quote against git HEAD
    by = collections.defaultdict(list)
    for row in rows:
        by[row[0]].append(row)
    ok = []
    with open(os.path.join(OUT, "assemble_pending.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(list(row), ensure_ascii=False) + "\n")
    fails = collections.Counter()
    for res in text.map_nodes(sorted(by), check_global, procs=6, chunk=3000):
        if res and res[0] == "__error__":
            continue
        for nid, a, z, sha, d, quote, window in res:
            if quote is None or not quote.strip():
                fails["sha_or_offset_mismatch"] += 1
                continue
            ok.append((nid, a, z, sha, d, quote, window))
    stats.update({"verify_fail_" + k: v for k, v in fails.items()})
    ok.sort(key=lambda x: (x[0], x[1]))
    # ---- write
    def cite_ev(usc, quote):
        if usc == "-":
            return "name:-"
        t, rest = usc.split(":", 1)
        sec = rest.split("(")[0]
        return f"cite:{t} U.S.C. § {rest}" if re.search(r"(?<![\w.])" + re.escape(sec) + r"(?![\w])", quote) else "name:-"
    used_issues = set(v for v in hold_index.values())
    hid_seen = set()
    with open(os.path.join(DATA, "holdings.tsv"), "w", encoding="utf-8", newline="\n") as fh, \
            open(os.path.join(DATA, "holdings_cert_text.tsv"), "w", encoding="utf-8", newline="\n") as fc:
        wseen = set()
        for nid, a, z, sha, d, quote, window in ok:
            if d["hid"] in hid_seen:
                continue
            hid_seen.add(d["hid"])
            used_issues.add(d["issue"])
            cert = [sha, str(a), str(z), quote, cite_ev(d["usc"], quote), d["part"]]
            fh.write("\t".join([d["hid"], str(nid), d["issue"], d["prop"].replace("\t", " "), d["answer"], d["role"]] + cert +
                               [d["reader"], str(d["conf"])]) + "\n")
            stats["holdings_" + d["src"]] += 1
            w0, w1, wtext = window
            if (sha, w0, w1) not in wseen:  # SCHEMA cert_text: window = normalised text[start0:end0], start0 = start-400
                wseen.add((sha, w0, w1))
                fc.write(f"{sha}\t{w0}\t{w1}\t{wtext}\n")
    # ---- marks
    marks = []
    mp = os.path.join(OUT, "raw_marks.jsonl")
    if os.path.exists(mp):
        for l in open(mp, encoding="utf-8"):
            r = _j(l)
            if r is None:
                continue
            o = r.get("out") or {}
            for j, m in enumerate(o.get("marks") or []):
                iss = (m.get("issue") or "").strip()
                mm = re.match(r"^h(\d+)$", iss)
                if mm and (r["nid"], int(mm.group(1))) in hold_index:
                    key = hold_index[(r["nid"], int(mm.group(1)))]
                else:
                    key = f"d{r['nid']}.m{j}"
                    issues.setdefault(key, [key, clean(iss.replace("new:", ""), 80) or "Marks issue", "federalGeneral", "-", "-",
                                            f"marks:{r.get('model')}"])
                used_issues.add(key)
                if key not in issues:
                    issues[key] = [key, "Marks issue", "federalGeneral", "-", "-", f"marks:{r.get('model')}"]
                prop = clean(m.get("proposition"))
                if not m.get("logical_subset"):
                    prop = clean("[no common denominator: result only] " + prop)
                marks.append([str(r["nid"]), key, clean(m.get("author"), 60), prop, f"marks:{r.get('model')}", "U"])
                stats["marks"] += 1
    with open(os.path.join(DATA, "marks.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for m in marks:
            f.write("\t".join(x.replace("\t", " ") for x in m) + "\n")
    with open(os.path.join(DATA, "issues.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for k in sorted(used_issues):
            f.write("\t".join(x.replace("\t", " ") for x in issues[k]) + "\n")
            stats["issues"] += 1
    json.dump(dict(stats), open(os.path.join(OUT, "assemble_stats.json"), "w"), indent=1)
    print(json.dumps(dict(stats), indent=1))





def check_global(nid, raw):
    # runs in a worker: re-load the pending rows for this nid from the shared file written by main()
    rows = _rows_for(nid)
    t = text.norm_text(raw)
    sha = text.text_sha(raw)
    res = []
    for a, z, rsha, d in rows:
        if rsha != sha or not (0 <= a < z <= len(t)):
            res.append((nid, a, z, sha, d, None, None))
        else:
            w0, w1 = max(0, a - 400), min(len(t), z + 400)
            w = text.quote_of(t, w0, w1)
            if w[a - w0:z - w0] != text.quote_of(t, a, z):
                res.append((nid, a, z, sha, d, None, None))
                continue
            res.append((nid, a, z, sha, d, text.quote_of(t, a, z), (w0, w1, w)))
    return res


_ROWS = None


def _rows_for(nid):
    global _ROWS
    if _ROWS is None:
        _ROWS = collections.defaultdict(list)
        for l in open(os.path.join(OUT, "assemble_pending.jsonl"), encoding="utf-8"):
            n, a, z, sha, d = json.loads(l)
            _ROWS[n].append((a, z, sha, d))
    return _ROWS.get(nid, [])


if __name__ == "__main__":
    main()
