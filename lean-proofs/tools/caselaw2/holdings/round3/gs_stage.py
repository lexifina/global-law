"""Round 3 gold-section reading: collect the readers' holdings, prepare clustering, stage certified rows (no gold).

    python gs_stage.py prep    -> w/items.json, w/cluster_XX.md (sections with holdings of >= 2 circuits)
    python gs_stage.py stage   -> w/staged.json {"rows", "issues", "stats"}; reads w/cout/*.jsonl (clusters)

Quotes are cut from git HEAD by the sentence offsets of the window; the reader only picks a sentence number.
Questions are installed only when holdings of >= 2 different circuits share them. Keys: usc:<usc>:g<n>.
"""
import collections, glob, json, os, re, sys
HT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HT)
import core, text

C2 = os.path.join(text.WORK, "caselaw-lean-2")
W = os.path.join(C2, "work", "round3", "splits", "w")
DATA = os.environ.get("SPL_DATA") or os.path.join(C2, "data")
USC_OK = re.compile(r"^(\d{1,2}):([0-9A-Za-z\-]+)(\([A-Za-z0-9]{1,6}\))?$")
PERB = int(os.environ.get("GS_CLUSTER_ITEMS", "90"))


def clean(s, n=300):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def items():
    idx = json.load(open(os.path.join(W, "windows.json"), encoding="utf-8"))
    out = []
    st = collections.Counter()
    seen = set()
    for fn in sorted(glob.glob(os.path.join(W, "out", "batch_*.jsonl"))):
        for l in open(fn, encoding="utf-8"):
            l = l.strip()
            if not l:
                continue
            try:
                r = json.loads(l)
            except Exception:
                st["bad_json"] += 1
                continue
            m = idx.get(r.get("wid"))
            if not m or r["wid"] in seen:
                st["bad_wid"] += 1
                continue
            seen.add(r["wid"])
            st["windows"] += 1
            if not r.get("interprets"):
                continue
            st["interprets"] += 1
            for h in (r.get("holdings") or [])[:3]:
                usc = (h.get("usc") or "").replace(" ", "")
                mo = USC_OK.match(usc)
                try:
                    s = int(h.get("s"))
                    conf = float(h.get("confidence") or 0)
                except Exception:
                    st["bad_fields"] += 1
                    continue
                if not mo or h.get("answer") not in ("yes", "no") or not (0 <= s < len(m["sents"])) \
                        or not (h.get("question") or "").strip():
                    st["bad_fields"] += 1
                    continue
                if mo.group(1) + ":" + mo.group(2) != m["key"]:
                    st["other_section"] += 1
                    continue
                if conf < 0.5:
                    st["low_conf"] += 1
                    continue
                out.append({"wid": r["wid"], "key": m["key"], "nid": m["nid"], "kind": m["kind"], "date": m["date"],
                            "sha": m["sha"], "span": m["sents"][s], "usc": usc, "q": clean(h["question"], 400),
                            "answer": h["answer"], "prop": clean(h.get("proposition")), "conf": round(conf, 2),
                            "conflict": bool(r.get("conflict"))})
                st["holdings"] += 1
    return out, st


def prep():
    its, st = items()
    by = collections.defaultdict(list)
    for i, it in enumerate(its):
        it["id"] = i
        by[it["key"]].append(it)
    json.dump(its, open(os.path.join(W, "items.json"), "w", encoding="utf-8"), ensure_ascii=False)
    for fn in glob.glob(os.path.join(W, "cluster_*.md")):
        os.remove(fn)
    blocks, n, nb, cur = [], 0, 0, 0
    secs = 0

    def flush():
        nonlocal blocks, nb, cur
        if blocks:
            with open(os.path.join(W, "cluster_%02d.md" % nb), "w", encoding="utf-8", newline="\n") as f:
                f.write("\n\n".join(blocks) + "\n")
            nb += 1
            blocks, cur = [], 0
    for key in sorted(by):
        if len({it["kind"] for it in by[key]}) < 2:
            continue
        secs += 1
        t, s = key.split(":")
        blk = ["## Section %s  (%s U.S.C. § %s)" % (key, t, s)]
        blk += ["[%d] (%s) %s" % (it["id"], it["usc"], it["q"]) for it in by[key]]
        blocks.append("\n".join(blk))
        cur += len(by[key])
        n += len(by[key])
        if cur >= PERB:
            flush()
    flush()
    st.update(sections_with_holdings=len(by), sections_to_cluster=secs, items_to_cluster=n, cluster_batches=nb)
    print(json.dumps(dict(st), indent=1))


def stage():
    its = json.load(open(os.path.join(W, "items.json"), encoding="utf-8"))
    st = collections.Counter()
    groups = collections.OrderedDict()   # (key, c) -> {"q", "label", "items": [(item, neg)]}
    seen_items = set()
    for fn in sorted(glob.glob(os.path.join(W, "cout", "*.jsonl"))):
        for l in open(fn, encoding="utf-8"):
            l = l.strip()
            if not l:
                continue
            try:
                c = json.loads(l)
            except Exception:
                st["cluster_bad_json"] += 1
                continue
            qs = c.get("questions") or []
            for x in c.get("items") or []:
                try:
                    i, ci, neg = int(x["id"]), int(x["c"]), bool(x.get("neg"))
                except Exception:
                    st["cluster_bad_item"] += 1
                    continue
                if not (0 <= i < len(its)) or its[i]["key"] != c.get("key") or not (0 <= ci < len(qs)) or i in seen_items:
                    st["cluster_bad_item"] += 1
                    continue
                seen_items.add(i)
                g = groups.setdefault((c["key"], fn, ci), {"q": clean(qs[ci].get("q"), 400),
                                                           "label": clean(qs[ci].get("label") or qs[ci].get("q"), 80),
                                                           "items": []})
                g["items"].append((its[i], neg))
    keep = [g for g in groups.values() if len({it["kind"] for it, _ in g["items"]}) >= 2 and g["q"]]
    st["questions_all"] = len(groups)
    st["questions_2_circuits"] = len(keep)
    nodes = {it["nid"] for g in keep for it, _ in g["items"]}
    raw = text.fetch(nodes)
    d2 = {}
    with open(os.path.join(DATA, "decisions2.tsv"), encoding="utf-8") as fh:
        for l in fh:
            i = l.find("\t")
            if l[:i].isdigit() and int(l[:i]) in nodes:
                f = l.split("\t", 8)
                d2[int(f[0])] = (f[7], f[6], f[5])
    iss = set()
    for l in open(os.path.join(DATA, "issues.tsv"), encoding="utf-8"):
        iss.add(l.split("\t", 1)[0])
    existing = set()
    for l in open(os.path.join(DATA, "holdings.tsv"), encoding="utf-8"):
        existing.add(l.split("\t", 1)[0])
    rows, issues = [], []
    per = collections.Counter()
    for g in keep:
        good = []
        used = set()
        for it, neg in g["items"]:
            n = it["nid"]
            if n in used:
                st["dup_decision_in_question"] += 1
                continue
            if n not in raw or n not in d2:
                st["no_text_or_decision_row"] += 1
                continue
            t = text.norm_text(raw[n])
            sha = text.text_sha(raw[n])
            if sha != it["sha"] or d2[n][0] != sha:
                st["sha_mismatch"] += 1
                continue
            a, z = it["span"]
            parts, form = core.court_parts(t)
            part = next((p for b, e, p in parts if b <= a < e), None)
            if part is None or part == "plurality" or d2[n][1] == "plurality":
                st["not_court_part"] += 1
                continue
            q = text.quote_of(t, a, z)
            w0, w1 = max(0, a - 400), min(len(t), z + 400)
            w = text.quote_of(t, w0, w1)
            if "\r" in w or not q.strip():
                st["lone_cr"] += 1
                continue
            role = "perCuriam" if (part == "perCuriam" or d2[n][1] == "perCuriam") else "majority"
            ans = it["answer"] if not neg else ("no" if it["answer"] == "yes" else "yes")
            used.add(n)
            good.append((it, ans, role, sha, a, z, q, (w0, w1, w)))
        if len({x[0]["kind"] for x in good}) < 2:
            st["question_lost_a_side"] += 1
            continue
        usc = collections.Counter(x[0]["usc"] for x in good).most_common(1)[0][0]
        n = per[usc]
        while "usc:%s:g%d" % (usc, n) in iss:
            n += 1
        per[usc] = n + 1
        key = "usc:%s:g%d" % (usc, n)
        title = int(usc.split(":")[0])
        dom = "federalPatent" if title == 35 else "federalTax" if title == 26 else "federalGeneral"
        issues.append([key, g["label"], dom, usc, g["q"], "splits3:claude-subagent"])
        sec = usc.split(":", 1)[1].split("(")[0]
        for it, ans, role, sha, a, z, q, win in good:
            hid = base = "S%d.%s.g%d" % (it["nid"], usc, n)
            k = 0
            while hid in existing:
                k += 1
                hid = "%s.%d" % (base, k)
            existing.add(hid)
            tev = ("cite:%s U.S.C. § %s" % (usc.split(":")[0], usc.split(":", 1)[1])
                   if re.search(r"(?<![\w.])" + re.escape(sec) + r"(?![\w])", q) else "name:-")
            rows.append({"hid": hid, "node": it["nid"], "issue": key, "prop": it["prop"], "answer": ans, "role": role,
                         "sha": sha, "start": a, "end": z, "quote": q, "tev": tev, "conf": it["conf"],
                         "window": list(win), "circ": it["kind"], "date": it["date"], "pub": d2[it["nid"]][2],
                         "question": g["q"], "usc": usc, "wid": it["wid"]})
        st["questions"] += 1
        st["opposite_answers"] += len({x[1] for x in good}) == 2
    st["rows"] = len(rows)
    json.dump({"rows": rows, "issues": issues, "stats": dict(st)}, open(os.path.join(W, "staged.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    {"prep": prep, "stage": stage}[sys.argv[1]]()
