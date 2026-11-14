"""Build the FRESH answer key of overruled US Supreme Court decisions (round 5).

    python round5/gold_fresh/build_gold.py

Reads   sealed/src/**            the four fresh lists (Wikipedia wikitext; hand transcriptions of Blaustein & Field 1958,
                                 Gerhardt 1991, Payne v. Tennessee n.1)
        ../../gold/work/scotus_nodes.tsv   (resolution table only: node, cites, name, type of every SCOTUS node)
        ../../data/decisions2.tsv          (streamed; dates of SCOTUS nodes)
        ../../gold/crs_overruled.tsv, ../../gold/scdb.tsv   (ONLY for the overlap report, never as a source of pairs)
Writes  work/scotus_meta.tsv     node, date, primary U.S. cite, name, type  (public; the scorer needs it)
        sealed/all_rows.tsv      one row per (source, pair), resolved or not, with the reason
        sealed/all_pairs.tsv     one row per scoreable pair (both sides resolve to exactly one decision), sources merged
        sealed/test.tsv, dev/dev.tsv   the split, by sha1(overruled U.S. citation) mod 2
        sealed/build_report.json counts for GOLD_FRESH.md
Files are UTF-8, LF, tab-separated, one header line. Nothing outside round5/gold_fresh/ is written.
"""
import collections, hashlib, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(HERE, "sealed", "src")
WIKI = {"title": "List of overruled United States Supreme Court decisions", "revid": 1380082490,
        "timestamp": "2026-10-13T17:50:54Z", "sha1": "28397728337f9a7b726119ba6d42933aafcfe0a7",
        "licence": "CC BY-SA 4.0", "fetched": "2026-11-13 via MediaWiki API (action=query&prop=revisions)"}
STOP = {"the", "and", "inc", "corp", "united", "states", "state", "of", "for", "commission", "department", "city",
        "county", "company", "board", "comm", "dept", "rel", "parte", "ins", "lessee", "railroad", "railway"}
# cite -> node, for decisions the corpus names differently from the lists (each checked by hand against the node's
# name, year and reporter page; see GOLD_FRESH.md "name overrides")
NAME_OK = {}
OVERRIDES_FILE = os.path.join(HERE, "sealed", "src", "name_overrides.tsv")


def w(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(str(c) for c in r) + "\n")


def toks(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = s.replace("'s", "s").replace("'", "")
    return {t for t in re.findall(r"[a-z]{3,}", s)} - STOP


def ncite(c):
    m = re.search(r"(\d+)\s*U\.?\s?S\.?\s+(?:\([^)]*\)\s*)?(\d+)", c or "")
    return f"{int(m.group(1))} U.S. {int(m.group(2))}" if m else None


def split_of(cite, node=None):
    """dev/test by sha1 of the overruled decision's U.S. citation (as the corpus carries it), mod 2. A decision with no
    U.S. page in the corpus is keyed `node:<id>`. score_fresh.py uses the same function for the model's own rows."""
    key = cite if cite and cite != "-" else f"node:{node}"
    return "dev" if int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16) % 2 == 0 else "test"


# ------------------------------------------------------------------ corpus
def load_scotus():
    by_cite = collections.defaultdict(list)
    meta = {}
    for line in open(os.path.join(C2, "gold", "work", "scotus_nodes.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        n = int(f[0])
        us = []
        for c in f[5].split("|"):
            k = ncite(c) if re.fullmatch(r"\d+ U\.S\. \d+", c.strip()) else None
            if k and k not in us:
                us.append(k)
        for k in us:
            by_cite[k].append(n)
        meta[n] = {"date": int(f[4]), "cite": us[0] if us else "-", "name": f[6], "type": f[7] if len(f) > 7 else ""}
    # dates as the model sees them
    with open(os.path.join(C2, "data", "decisions2.tsv"), encoding="utf-8") as fh:
        for line in fh:
            t = line.split("\t", 3)
            if t[0].isdigit():
                n = int(t[0])
                if n in meta:
                    meta[n]["date"] = int(t[2])
    return by_cite, meta


_BY_YEAR = None


def by_name_year(name, year, meta):
    """Fallback when the list's U.S. page is absent from the corpus, wrong, or not given: the one SCOTUS decision of
    that year (else of year +-1) whose name carries every name token of the list's name (or >= 2 and >= 60% of them)."""
    global _BY_YEAR
    if _BY_YEAR is None:
        _BY_YEAR = collections.defaultdict(list)
        for n, m in meta.items():
            if m["type"] in ("opinion", "per curiam", ""):
                _BY_YEAR[m["date"] // 10000].append(n)
    want = toks(name)
    if not want or not year:
        return None
    for ys in ((year,), (year - 1, year + 1)):
        sc = []
        for y in ys:
            for n in _BY_YEAR.get(y, []):
                have = toks(meta[n]["name"])
                k = len(want & have)
                if meta[n]["type"] == "" and have != want:   # untyped nodes (orders): exact name only
                    continue
                if k == len(want) or (k >= 2 and k >= 0.6 * len(want)):
                    sc.append((k, n))
        if not sc:
            continue
        best = max(k for k, _ in sc)
        top = [n for k, n in sc if k == best]
        if len(top) > 1:
            top = [n for n in top if meta[n]["type"] == "opinion"]
        return top[0] if len(top) == 1 else None
    return None


def resolve(cite, name, year, by_cite, meta):
    """(node or -1, reason). Exactly one decision at that U.S. page whose name agrees; else the name+year fallback."""
    n, why = resolve_cite(cite, name, by_cite, meta)
    if n < 0 and not why.startswith("ambiguous"):
        m = by_name_year(name, year, meta)
        if m is not None:
            return m, "ok:nameYear(" + why.split("(")[0] + f"; corpus cite {meta[m]['cite']})"
    return n, why


def resolve_cite(cite, name, by_cite, meta):
    if not cite:
        return -1, "noUSCite"
    cand = by_cite.get(cite, [])
    if not cand:
        return -1, "citeNotInCorpus"
    if cite in NAME_OK and NAME_OK[cite] in cand:
        return NAME_OK[cite], "ok:override"
    want = toks(name)
    sc = sorted(((len(want & toks(meta[n]["name"])), n) for n in cand), reverse=True)
    best = sc[0][0]
    top = [n for s, n in sc if s == best]
    if best == 0:
        return -1, f"nameMismatch({len(cand)} at page: {meta[cand[0]]['name'][:50]})"
    if len(top) > 1:
        prim = [n for n in top if meta[n]["cite"] == cite]
        if len(prim) == 1:
            return prim[0], "ok:primaryCiteTieBreak"
        full = [n for n in top if meta[n]["type"] in ("opinion", "per curiam")]
        if len(full) == 1:
            return full[0], "ok:typeTieBreak"
        return -1, f"ambiguous({len(top)} decisions at the page share the name)"
    n = top[0]
    return n, "ok" if len(cand) == 1 else "ok:nameAmongSeveral"


# ------------------------------------------------------------------ sources
def clean_wiki(s):
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    return s.replace("''", "").strip()


def parse_wiki():
    txt = open(os.path.join(SRC, "wikipedia", "page.wikitext"), encoding="utf-8").read()
    out, sec, sub = [], "", ""
    cells, intable = [], False

    def flush():
        nonlocal cells
        if len(cells) >= 2:
            out.append((cells[0], cells[1], f"{sec}/{sub}".strip("/")))
        elif cells:
            out.append((cells[0], "", f"{sec}/{sub}".strip("/") + " [row with one cell]"))
        cells = []
    for line in txt.split("\n"):
        if line.startswith("=="):
            sec, sub = line.strip("= ").strip(), ""
        elif line.startswith(";"):
            sub = clean_wiki(line[1:])
        elif line.startswith("{|"):
            intable, cells = True, []
        elif line.startswith("|}"):
            flush()
            intable = False
        elif line.startswith("|-"):
            flush()
        elif intable and line.startswith("|"):
            for c in line[1:].split("||"):
                cells.append(clean_wiki(c))
    rows = []
    for a, b, note in out:   # a = overruled, b = overruling
        rows.append({"source": "wikipedia", "page": f"rev {WIKI['revid']}", "hint": "explicit (list's own scope)",
                     "partial": int("in part" in a.lower() or "in part" in b.lower()),
                     "o": side(b), "x": side(a), "note": note})
    return rows


def side(s):
    s0 = re.sub(r"\(in part\)", "", s, flags=re.I).strip()
    y = re.findall(r"\((\d{4})\)", s0)
    name = re.split(r",?\s*\d+\s+U\.?\s?S\.?\s", s0)[0]
    name = re.sub(r"\s*\(\d{4}\)\s*$", "", name).strip(" ,")
    return {"name": name, "year": int(y[-1]) if y else 0, "cite": ncite(s0)}


def parse_parts(folder, source, hint_fn):
    rows = []
    d = os.path.join(SRC, folder)
    for fn in sorted(os.listdir(d)):
        if not fn.startswith("part"):
            continue
        for line in open(os.path.join(d, fn), encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            head, tail = line.split(" >> ")
            page, tag, oname, oyear, ocite = head.split("|")
            for t in tail.split(" ;; "):
                xname, xyear, xcite = t.split("|")
                hint, partial, note = hint_fn(tag, oname, xname)
                rows.append({"source": source, "page": f"p. {page}", "hint": hint, "partial": partial,
                             "o": {"name": oname, "year": int(oyear), "cite": ncite(ocite)},
                             "x": {"name": xname, "year": int(xyear), "cite": ncite(xcite)}, "note": note})
    return rows


def hint_blaustein(tag, oname, xname):
    lab = {"E": "express", "B": "implied (not expressly overruled; listed by Justice Brandeis)",
           "D": "implied (not expressly overruled; listed by Justice Douglas)",
           "O": "implied (otherwise overruled in the opinion of the authors)"}
    h = "; ".join(lab[t.strip()] for t in tag.split(","))
    note = f"category {tag}"
    if "(Rehearing)" in oname:
        note += "; same case on rehearing"
    return h, 0, note


PART_WORDS = ("to the extent", "insofar", "to that extent", "in part")


def hint_gerhardt(tag, oname, xname):
    t = tag.lower()
    if t.startswith("implied:"):
        return "implied (" + tag.split(":", 1)[1].strip() + ")", 0, "language: " + tag
    exp = "express: word 'overrule'" if "overrul" in t else "express by the author's test; other wording"
    return exp, int(any(p in t for p in PART_WORDS)), "language: " + tag


def hint_payne(tag, oname, xname):
    if "in part" in tag:
        return "express; in part", 1, tag
    if "in effect" in tag:
        return "implied (overruling in effect)", 0, tag
    return "express", 0, tag


# ------------------------------------------------------------------ main
def main():
    if os.path.exists(OVERRIDES_FILE):
        for line in open(OVERRIDES_FILE, encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if f and f[0] and not f[0].startswith("#") and f[1].lstrip("-").isdigit():
                NAME_OK[f[0]] = int(f[1])
    by_cite, meta = load_scotus()
    w(os.path.join(HERE, "work", "scotus_meta.tsv"),
      [["node", "date", "us_cite", "name", "type"]] + [[n, m["date"], m["cite"], m["name"], m["type"]]
                                                       for n, m in sorted(meta.items())])
    rows = (parse_wiki() + parse_parts("blaustein_field_1958", "blaustein_field_1958", hint_blaustein)
            + parse_parts("gerhardt_1991", "gerhardt_1991", hint_gerhardt)
            + parse_parts("payne_n1_1991", "payne_n1_1991", hint_payne))
    rep = {"wikipedia": WIKI, "rows_by_source": {}, "resolution": {}, "unresolved_reasons": {}}
    allrows = [["pair_id", "source", "overruling_cite", "overruling_name", "overruling_year", "overruled_cite",
                "overruled_name", "overruled_year", "partial", "explicit_hint", "note", "by_node", "target_node",
                "resolve_by", "resolve_target", "scoreable", "split"]]
    pairs = collections.OrderedDict()
    warn = []
    for r in rows:
        o, x = r["o"], r["x"]
        bn, br = resolve(o["cite"], o["name"], o["year"], by_cite, meta)
        tn, trs = resolve(x["cite"], x["name"], x["year"], by_cite, meta)
        for nd, s in ((bn, o), (tn, x)):
            if nd >= 0 and s["year"] and abs(meta[nd]["date"] // 10000 - s["year"]) > 1:
                warn.append((r["source"], s["cite"], s["name"], s["year"], meta[nd]["date"]))
        ok = bn >= 0 and tn >= 0
        why = ""
        if ok and bn == tn:
            ok, why = False, "sameNode"
        if ok and meta[bn]["date"] < meta[tn]["date"]:
            ok, why = False, "overrulingEarlierThanOverruled"
        pid = "F" + hashlib.sha1(f"{o['cite'] or o['name']}|{x['cite'] or x['name']}".encode()).hexdigest()[:8]
        sp = split_of(meta[tn]["cite"], tn) if ok else "-"
        note = r["note"] + (f"; {why}" if why else "")
        allrows.append([pid, r["source"], o["cite"] or "-", o["name"], o["year"], x["cite"] or "-", x["name"], x["year"],
                        r["partial"], r["hint"], note, bn, tn, br, trs, int(ok), sp])
        S = r["source"]
        rep["rows_by_source"].setdefault(S, collections.Counter())
        c = rep["rows_by_source"][S]
        c["rows"] += 1
        c["overruling_resolved"] += bn >= 0
        c["overruled_resolved"] += tn >= 0
        c["scoreable"] += ok
        if not ok:
            for side_, rs in (("overruling", br), ("overruled", trs)):
                if not rs.startswith("ok"):
                    rep["unresolved_reasons"].setdefault(S, collections.Counter())[f"{side_}:{rs.split('(')[0]}"] += 1
            if why:
                rep["unresolved_reasons"].setdefault(S, collections.Counter())[why] += 1
        if ok:
            p = pairs.setdefault((bn, tn), {"pid": pid, "o": o, "x": x, "src": [], "partial": {}, "hint": {},
                                            "notes": [], "split": sp})
            if S not in p["src"]:
                p["src"].append(S)
            p["partial"][S] = max(p["partial"].get(S, 0), r["partial"])
            p["hint"][S] = r["hint"]
            p["notes"].append(f"{S} {r['page']}: {r['note']}")
    # burned lists: overlap only
    crs16, crscur, crs16exp = set(), set(), set()
    cp = os.path.join(C2, "gold", "crs_overruled.tsv")
    with open(cp, encoding="utf-8") as f:
        h = f.readline().rstrip("\n").split("\t")
        for line in f:
            d = dict(zip(h, line.rstrip("\n").split("\t")))
            k = (int(d["by_node"]), int(d["target_node"]))
            if d["in_2016"] == "1":
                crs16.add(k)
                if d["expressly_2016"] == "1":
                    crs16exp.add(k)
            if d["in_current"] == "1":
                crscur.add(k)
    scdb = set()
    with open(os.path.join(C2, "gold", "scdb.tsv"), encoding="utf-8") as f:
        h = f.readline().rstrip("\n").split("\t")
        ni, pi = h.index("node"), h.index("precedentAlteration")
        for line in f:
            t = line.rstrip("\n").split("\t")
            if t[pi] == "1" and t[ni].lstrip("-").isdigit():
                scdb.add(int(t[ni]))
    head = ["pair_id", "by_node", "target_node", "overruling_cite", "overruling_name", "overruling_date",
            "overruled_cite", "overruled_name", "overruled_date", "partial", "partial_by_source", "implied",
            "explicit_hint", "sources", "n_sources", "in_crs2016", "in_crs_current", "scdb_flags_overruler", "split",
            "note"]
    out = {"dev": [head], "test": [head], "all": [head]}
    ov = collections.Counter()
    for (bn, tn), p in pairs.items():
        partial = int(any(p["partial"].values()))
        implied = int(any(h.startswith("implied") for h in p["hint"].values()))
        row = [p["pid"], bn, tn, meta[bn]["cite"], meta[bn]["name"], meta[bn]["date"], meta[tn]["cite"],
               meta[tn]["name"], meta[tn]["date"], partial,
               ",".join(f"{s}={v}" for s, v in p["partial"].items()), implied,
               " | ".join(f"{s}: {h}" for s, h in p["hint"].items()), ",".join(p["src"]), len(p["src"]),
               int((bn, tn) in crs16), int((bn, tn) in crscur), int(bn in scdb), p["split"], " || ".join(p["notes"])]
        out[p["split"]].append(row)
        out["all"].append(row)
        for S in p["src"] + ["ALL"]:
            ov[(S, "pairs")] += 1
            ov[(S, "crs2016")] += (bn, tn) in crs16
            ov[(S, "crs2016_express")] += (bn, tn) in crs16exp
            ov[(S, "crs_current")] += (bn, tn) in crscur
            ov[(S, "crs_any")] += (bn, tn) in crs16 or (bn, tn) in crscur
            ov[(S, "scdb_flag")] += bn in scdb
            ov[(S, "scdb_scope")] += meta[bn]["date"] >= 19461001  # SCDB modern flag is only reliable from 1946
            ov[(S, "scdb_flag_in_scope")] += bn in scdb and meta[bn]["date"] >= 19461001
            ov[(S, "neither")] += not ((bn, tn) in crs16 or (bn, tn) in crscur or bn in scdb)
            ov[(S, "partial")] += partial
            ov[(S, "implied")] += implied
            ov[(S, p["split"])] += 1
    w(os.path.join(HERE, "sealed", "all_rows.tsv"), allrows)
    w(os.path.join(HERE, "sealed", "all_pairs.tsv"), out["all"])
    w(os.path.join(HERE, "sealed", "test.tsv"), out["test"])
    w(os.path.join(HERE, "dev", "dev.tsv"), out["dev"])
    # disagreement between lists: pairs in one list's period but absent from another
    srcs = ["wikipedia", "blaustein_field_1958", "gerhardt_1991", "payne_n1_1991"]
    span = {"wikipedia": (0, 99999999), "blaustein_field_1958": (0, 19571231), "gerhardt_1991": (0, 19910701),
            "payne_n1_1991": (19710601, 19910626)}
    dis = {}
    for a in srcs:
        for b in srcs:
            if a == b:
                continue
            lo, hi = max(span[a][0], span[b][0]), min(span[a][1], span[b][1])
            ina = [k for k, p in pairs.items() if a in p["src"] and lo <= meta[k[0]]["date"] <= hi]
            dis[f"{a} not in {b}"] = {"pairs_of_first_in_common_period": len(ina),
                                      "missing_from_second": sum(b not in pairs[k]["src"] for k in ina)}
    rep["disagreement"] = dis
    rep["disagreement_note"] = ("common period = overruling decision dated within both lists' coverage; Gerhardt and "
                                "Payne n.1 are constitutional only, so statutory/common-law pairs of Wikipedia and "
                                "Blaustein are expected to be missing from them")
    rep["rows_by_source"] = {k: dict(v) for k, v in rep["rows_by_source"].items()}
    rep["unresolved_reasons"] = {k: dict(v) for k, v in rep["unresolved_reasons"].items()}
    rep["pairs"] = {S: {k2: v for (s2, k2), v in ov.items() if s2 == S} for S in srcs + ["ALL"]}
    rep["n_sources_hist"] = dict(collections.Counter(len(p["src"]) for p in pairs.values()))
    rep["distinct_overruled"] = len({k[1] for k in pairs})
    rep["year_warnings"] = [list(x) for x in warn]
    rep["name_overrides"] = len(NAME_OK)
    json.dump(rep, open(os.path.join(HERE, "sealed", "build_report.json"), "w", encoding="utf-8", newline="\n"),
              indent=1)
    pub = {k: rep[k] for k in ("wikipedia", "rows_by_source", "unresolved_reasons", "disagreement", "n_sources_hist",
                               "distinct_overruled", "name_overrides")}
    pub["pairs"] = rep["pairs"]
    print(json.dumps(pub, indent=1))
    print("year warnings:", len(warn))
    if "--show-unresolved" in sys.argv:
        for r in allrows[1:]:
            if r[15] == 0:
                print("UNRES", r[1], "|", r[2], r[3], r[4], "|", r[5], r[6], r[7], "|", r[13], "|", r[14], "|", r[10][-40:])
        for x in warn:
            print("YEAR", x)


if __name__ == "__main__":
    main()
