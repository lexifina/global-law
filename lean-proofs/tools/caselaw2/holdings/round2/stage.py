"""Stage certified rows from the Claude subagent readings (no gold):
  res: Supreme Court holdings on existing split questions (work/res2, work/res2b)
  xc:  new split questions from cross-circuit disagreement pairs (work/xc)
Every quote is cut from the decision text at git HEAD by the sentence offsets the reader chose (the reader never types
a quote); sha1(file) must equal both the recorded sha and decisions2.tsv's text_sha.
 -> work/staged.json  {"rows": [...], "issues": [...], "stats": {...}}"""
import os, re, json, glob, collections
import common as C
import text, core, syl

USC_OK = re.compile(r"^(\d{1,2}):([0-9A-Za-z\-]+)(\([A-Za-z0-9]{1,6}\))?$")
TAG = os.environ.get("RES_TAG", "")   # "" = first pass (res + xc); "x" = second pass: res rows on the new questions only
MINCONF = float(os.environ.get("SPL_MINCONF", "0.5"))


def clean(s, n=300):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def jl(pattern):
    out = {}
    for fn in sorted(glob.glob(pattern)):
        for l in open(fn, encoding="utf-8"):
            l = l.strip()
            if l:
                try:
                    r = json.loads(l)
                    out[r["pid"]] = r
                except Exception:
                    pass
    return out


def cite_ev(usc, quote):
    if usc == "-":
        return "name:-"
    t, rest = usc.split(":", 1)
    sec = rest.split("(")[0]
    return f"cite:{t} U.S.C. § {rest}" if re.search(r"(?<![\w.])" + re.escape(sec) + r"(?![\w])", quote) else "name:-"


def main():
    W = os.path.join(C.PRIV, "work")
    iss = C.load_issues()
    stats = collections.Counter()
    # ---------------- res
    r2 = jl(os.path.join(W, "res2" + TAG, "out_*.jsonl"))
    i2 = json.load(open(os.path.join(W, "res2" + TAG, "sents.json"), encoding="utf-8"))
    for p in i2:
        i2[p]["fixed_parts"] = bool(TAG)   # second-pass digests were cut with syl.court_parts2
    if not TAG and os.path.exists(os.path.join(W, "res2b", "sents.json")):
        r2b = jl(os.path.join(W, "res2b", "out_*.jsonl"))
        i2b = json.load(open(os.path.join(W, "res2b", "sents.json"), encoding="utf-8"))
        for p in r2b:
            r2[p] = r2b[p]
            i2[p] = i2b[p]
            i2[p]["fixed_parts"] = True
    xr = jl(os.path.join(W, "xc", "out_*.jsonl")) if not TAG else {}
    xi = json.load(open(os.path.join(W, "xc", "sents.json"), encoding="utf-8"))
    nodes = {i2[p]["node"] for p in r2} | {xi[p]["by"] for p in xr if xr[p].get("split")} | \
            {xi[p]["target"] for p in xr if xr[p].get("split")}
    raw = text.fetch(nodes)
    d2sha = {}
    d2form = {}
    with open(os.path.join(C.DATA, "decisions2.tsv"), encoding="utf-8") as fh:
        for l in fh:
            i = l.find("\t")
            if l[:i].isdigit() and int(l[:i]) in nodes:
                f = l.split("\t", 8)
                d2sha[int(f[0])] = f[7]
                d2form[int(f[0])] = f[6]
    names = C.node_names(nodes)
    existing = set()
    for l in open(os.path.join(C.DATA, "holdings.tsv"), encoding="utf-8"):
        existing.add(l.split("\t", 1)[0])
    rows = []
    issues = []

    def cert(node, a, z, want_sha):
        """(sha, quote, (w0, w1, window)) or a failure reason"""
        if node not in raw:
            return "no_text"
        t = text.norm_text(raw[node])
        sha = text.text_sha(raw[node])
        if sha != want_sha or d2sha.get(node) != sha:
            return "sha_mismatch"
        if not (0 <= a < z <= len(t)):
            return "offsets"
        q = text.quote_of(t, a, z)
        w0, w1 = max(0, a - 400), min(len(t), z + 400)
        w = text.quote_of(t, w0, w1)
        if "\r" in w or not q.strip():
            return "lone_cr"
        return sha, q, (w0, w1, w)

    def new_hid(base):
        h = base
        k = 0
        while h in existing:
            k += 1
            h = "%s%d" % (base, k)
        existing.add(h)
        return h

    seen = set()
    for pid in sorted(r2):
        r, m = r2[pid], i2[pid]
        if r.get("decides") != "yes":
            stats["res_not_yes"] += 1
            continue
        s = m["S"].get(str(r.get("sent", "")).lstrip("S"))
        if r.get("answer") not in ("yes", "no") or not s:
            stats["res_bad_fields"] += 1
            continue
        if float(r.get("conf") or 0) < MINCONF:
            stats["res_low_conf"] += 1
            continue
        node = m["node"]
        a, z, part = s
        t = text.norm_text(raw[node])
        if not m.get("fixed_parts"):
            parts, _ = core.court_parts(t)
            ok = False
            for b, e, _p in parts:
                if b <= a < e:
                    o = syl.opinion_start(t, b, e)
                    ok = o is not None and a >= o
            if not ok:
                stats["res_syllabus_sentence"] += 1
                continue
        form = d2form.get(node, "")
        if form == "plurality":
            stats["res_plurality"] += 1
            continue
        role = "perCuriam" if (part == "perCuriam" or form == "perCuriam") else "majority"
        if (node, m["issue"]) in seen:
            stats["res_dup"] += 1
            continue
        c = cert(node, a, z, m["sha"])
        if isinstance(c, str):
            stats["res_" + c] += 1
            continue
        seen.add((node, m["issue"]))
        usc = iss[m["issue"]][3]
        hid = new_hid("S%d.%s.r" % (node, usc))
        rows.append({"stream": "res", "pid": pid, "hid": hid, "node": node, "issue": m["issue"], "prop": clean(r.get("prop")),
                     "answer": r["answer"], "role": role, "sha": c[0], "start": a, "end": z, "quote": c[1],
                     "tev": cite_ev(usc, c[1]), "conf": round(float(r["conf"]), 2), "window": list(c[2]),
                     "name": names.get(node, ("?", ""))[0], "cite": names.get(node, ("", ""))[1].split("|")[0],
                     "date": m["date"], "question": iss[m["issue"]][4], "usc": usc})
        stats["res_rows"] += 1
    # ---------------- xc
    groups = collections.OrderedDict()
    for pid in sorted(xr):
        r, m = xr[pid], xi[pid]
        if r.get("split") is not True:
            stats["xc_rejected_by_reader"] += 1
            continue
        if float(r.get("conf") or 0) < MINCONF:
            stats["xc_low_conf"] += 1
            continue
        usc = (r.get("usc") or "").replace(" ", "")
        mo = USC_OK.match(usc)
        sb = m["B"].get(str(r.get("b_sent", "")).lstrip("B"))
        st = m["T"].get(str(r.get("t_sent", "")).lstrip("T"))
        if not mo or not sb or not st or r.get("b_answer") not in ("yes", "no") or r.get("t_answer") not in ("yes", "no") \
                or r["b_answer"] == r["t_answer"] or not (r.get("question") or "").strip():
            stats["xc_bad_fields"] += 1
            continue
        if sb[2] == "plurality" or st[2] == "plurality":
            stats["xc_plurality"] += 1
            continue
        sec = mo.group(2)
        tb, tt = text.norm_text(raw[m["by"]]), text.norm_text(raw[m["target"]])
        pat = re.compile(r"(?<![\w.])" + re.escape(sec) + r"(?![\w])")
        if not pat.search(tb) and not pat.search(tt):
            stats["xc_section_not_in_text"] += 1
            continue
        cb = cert(m["by"], sb[0], sb[1], m["sha_b"])
        ct = cert(m["target"], st[0], st[1], m["sha_t"])
        if isinstance(cb, str) or isinstance(ct, str):
            stats["xc_" + (cb if isinstance(cb, str) else ct)] += 1
            continue
        g = groups.setdefault((m["by"], usc, sb[0], r["b_answer"]), {"usc": usc, "pairs": []})
        g["pairs"].append((pid, r, m, sb, st, cb, ct))
    per_usc = collections.Counter()
    for (by, usc, _a, _ans), g in groups.items():
        n = per_usc[usc]
        per_usc[usc] += 1
        key = "usc:%s:x%d" % (usc, n)
        while key in iss:
            n += 1
            per_usc[usc] = n + 1
            key = "usc:%s:x%d" % (usc, n)
        pid, r, m, sb, st, cb, ct = g["pairs"][0]
        title = int(usc.split(":")[0])
        dom = "federalPatent" if title == 35 else "federalTax" if title == 26 else "federalGeneral"
        q = clean(r["question"], 400)
        issues.append([key, clean(q, 80), dom, usc, q, "splits2:claude-subagent"])
        stats["xc_questions"] += 1
        conf_b = max(float(x[1]["conf"]) for x in g["pairs"])
        rows.append({"stream": "xc", "pid": pid, "side": "B", "hid": new_hid("S%d.%s.x%d" % (by, usc, n)), "node": by,
                     "issue": key, "prop": clean(r.get("b_prop")), "answer": r["b_answer"], "role": sb[2], "sha": cb[0],
                     "start": sb[0], "end": sb[1], "quote": cb[1], "tev": cite_ev(usc, cb[1]), "conf": round(conf_b, 2),
                     "window": list(cb[2]), "name": names.get(by, ("?", ""))[0],
                     "cite": names.get(by, ("", ""))[1].split("|")[0], "date": m["date_b"], "circ": m["circ_b"],
                     "question": q, "usc": usc, "pub": m["pub_b"]})
        stats["xc_rows"] += 1
        tseen = set()
        for pid, r, m, sb, st, cb, ct in g["pairs"]:
            if m["target"] in tseen:
                continue
            tseen.add(m["target"])
            rows.append({"stream": "xc", "pid": pid, "side": "T", "hid": new_hid("S%d.%s.x%d" % (m["target"], usc, n)),
                         "node": m["target"], "issue": key, "prop": clean(r.get("t_prop")), "answer": r["t_answer"],
                         "role": st[2], "sha": ct[0], "start": st[0], "end": st[1], "quote": ct[1],
                         "tev": cite_ev(usc, ct[1]), "conf": round(float(r["conf"]), 2), "window": list(ct[2]),
                         "name": names.get(m["target"], ("?", ""))[0],
                         "cite": names.get(m["target"], ("", ""))[1].split("|")[0], "date": m["date_t"],
                         "circ": m["circ_t"], "question": q, "usc": usc, "pub": m["pub_t"]})
            stats["xc_rows"] += 1
            stats["xc_pairs"] += 1
    json.dump({"rows": rows, "issues": issues, "stats": dict(stats)},
              open(os.path.join(W, "staged%s.json" % TAG), "w", encoding="utf-8"), ensure_ascii=False)
    print(json.dumps(dict(stats), indent=1))


if __name__ == "__main__":
    main()
