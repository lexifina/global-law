#!/usr/bin/env python3
"""Round 7 held-out key, time split: Supreme Court merits judgments decided on or after the cutoff (2021-01-01),
paired with the lower-court decision each one reviewed, as recorded by the Supreme Court's own docket.

    python -I build_timesplit.py [--cut 20210101] [--out key/]

Reads ONLY
  * src_scdocket/json/<docket>.json  the Supreme Court's docket records (supremecourt.gov, fetch_dockets.py):
                                     LowerCourt, LowerCourtCaseNumbers, LowerCourtDecision, party titles and the
                                     Clerk's judgment entry ("Judgment REVERSED ...") in ProceedingsandOrder;
  * round6/history/cache/*.meta.tsv.gz   corpus metadata: node, date, court2 id, docket, title, parties;
  * round6/history/stage/final2/courts2.tsv, court_alias.tsv   court names -> court2 ids;
  * work/seen_nodes.txt              nodes builders of rounds 5-7 have seen (seen_nodes.py), to drop.
It reads no model output (no history/status/certs table, no linker rows) and no other answer key.

Writes in --out (private to round7/heldout):
  timesplit_key.tsv     one line per (acting Supreme Court node, lower node) pair with the expected kind
  timesplit_orders.tsv  acting node, dockets on the node, dockets linked, complete (precision uses complete nodes)
  timesplit_stats.tsv   aggregate counts only
"""
import argparse
import collections
import datetime
import glob
import gzip
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(C2, "round6", "history", "cache")
FINAL2 = os.path.join(C2, "round6", "history", "stage", "final2")
SCOTUS2 = 2906
NEAR_DAYS = 7
DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−﹘﹣－"), "-")
FEDERAL_APPEALS = re.compile(r"^united states court of appeals", re.I)


# ------------------------------------------------------------------ dockets
def scotus_dockets(s):
    return ["%s-%d" % (m.group(1), int(m.group(2)))
            for m in re.finditer(r"(?<!\d)(\d{2})\s*-\s*(\d{1,5})(?!\d)", (s or "").translate(DASHES))]


def lower_dockets(s):
    """Docket string -> set of digit skeletons ('4-15-123'); parts with fewer than 4 digits are dropped; a bare
    number after a full first docket takes that docket's prefix ('18-2527, 2793' -> 18-2793)."""
    s = (s or "").upper().translate(DASHES).strip("() ")
    out = set()
    first = None
    for part in re.split(r"[;,&/]|\bAND\b|\bNOS?\.", s):
        groups = [g.lstrip("0") or "0" for g in re.findall(r"\d+", part)]
        if not groups:
            continue
        if len(groups) == 1 and first and len(first) >= 2 and len(groups[0]) >= 3:
            groups = first[:-1] + groups
        if len(groups) >= 2 and first is None:
            first = groups
        if sum(len(g) for g in groups) < 4:
            continue
        out.add("-".join(groups))
    return out


# ------------------------------------------------------------------ captions
STOP = set("""united states america state people commonwealth commissioner warden secretary director attorney general
department dept company corporation corp incorporated limited city county town village district board inc llc
petitioner petitioners respondent respondents appellant appellants appellee appellees plaintiff plaintiffs defendant
defendants others other individually official capacity behalf himself herself themselves their next friend minor
estate matter re ex rel parte the of and for in on at by to a an et al etc sheriff superintendent administrator
prison correctional correction corrections institution facility service services national federal government court
superior supreme appeals bank insurance trust association authority agency commission office officer police
school schools university college center hospital medical health human resources public family children social
security""".split())


def tokens(s):
    s = (s or "").lower().replace("’", "'")
    return {t for t in re.findall(r"[a-z][a-z'\-]*[a-z]", s) if len(t) >= 4 and t not in STOP}


# ------------------------------------------------------------------ courts
ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh",
       "twelfth", "thirteenth", "fourteenth"]
LEVELS = (r"supreme court|court of appeals?|court of criminal appeals|court of civil appeals|court of special appeals|"
          r"appellate court|superior court|commonwealth court|intermediate court of appeals|appeals court|"
          r"district court of appeal|appellate division of supreme court|supreme judicial court")


def norm_court(s):
    s = (s or "").lower().translate(DASHES).replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ,]+", " ", s)
    s = re.sub(r"\bthe\b", " ", s)
    s = re.sub(r"\s*,\s*", " , ", s)
    return re.sub(r"\s+", " ", s).strip(" ,")


def court_names():
    m = collections.defaultdict(set)
    with open(os.path.join(FINAL2, "courts2.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            m[norm_court(p[3]).replace(" , ", " ")].add(int(p[0]))
            m[norm_court(p[3])].add(int(p[0]))
    with open(os.path.join(FINAL2, "court_alias.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            m[norm_court(p[2]).replace(" , ", " ")].add(int(p[5]))
            m[norm_court(p[2])].add(int(p[5]))
    return m


def name_variants(n):
    v = [n, n.replace(" , ", " ")]
    base = n.split(" , ")[0]
    v.append(base)
    q = re.sub(r"\b(?:" + "|".join(ORD) + r"|\d+(?:st|nd|rd|th)?)\s+(?:appellate\s+|judicial\s+)?(?:district|"
               r"division|department|circuit)\b.*$", "", n).strip(" ,")
    v.append(q)
    out = []
    for x in v:
        x = x.strip(" ,")
        if not x:
            continue
        out.append(x)
        m = re.match(r"^(" + LEVELS + r") of (?:state of )?(.+)$", x)
        if m:
            out.append("%s %s" % (m.group(2), m.group(1)))
        m = re.match(r"^(.+?) (" + LEVELS + r")$", x)
        if m:
            out.append("%s of %s" % (m.group(2), m.group(1)))
    seen = []
    for x in out:
        if x not in seen:
            seen.append(x)
    return seen


def map_court(name, names):
    for x in name_variants(norm_court(name)):
        if x in names:
            return set(names[x])
    return set()


# ------------------------------------------------------------------ Supreme Court docket record
MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov",
                                          "dec"])}


def parse_date(s):
    """'June 19, 2019' / 'Jan 14 2021' -> 'yyyymmdd' or ''."""
    m = re.search(r"([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})", s or "")
    if not m or m.group(1).lower() not in MONTHS:
        return ""
    return "%s%02d%02d" % (m.group(3), MONTHS[m.group(1).lower()], int(m.group(2)))


def judgment(text):
    """Clerk's judgment entry -> (kind, sub) or None."""
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()
    if re.search(r"^(?:Petitions? GRANTED[.,;]? )?Writs? of certiorari DISMISSED as improvidently granted", t, re.I):
        return ("reviewDismissed", "DIG")
    if re.match(r"^Petitions? (?:for (?:a )?writs? of certiorari )?(?:is |are )?DENIED\b", t):
        return ("certDenied", "certDenied")
    # the judgment clause: "Judgment ..." / "Adjudged to be ..." up to the first full stop or semicolon, at the
    # start of the entry or after "Petition GRANTED."
    m = re.match(r"^(?:Petitions? (?:for (?:a )?writs? of certiorari )?GRANTED,?\.?\s*(?:and\s+)?)?"
                 r"((?:Judgments?|Adjudged to be)\b[^.;]*)", t, re.I)
    if not m:
        return None
    head = m.group(1)
    if re.match(r"^Judgments? in No", head, re.I) or re.search(r"\bas to\b", head, re.I):
        return None  # a disposition split by docket or by party: not keyed
    w = set(x.upper() for x in re.findall(r"\b(REVERSED|VACATED|AFFIRMED|MODIFIED)\b", head, re.I))
    if re.search(r"equally\s+divided", t, re.I) and w == {"AFFIRMED"}:
        return ("affirmed", "equallyDivided")
    if not w:
        return None
    if re.search(r"\bin\s+part\b", head, re.I) or len(w) > 1:
        return ("mixed", "+".join(sorted(w)).lower())
    k = next(iter(w)).lower()
    return (k, k)


def read_record(path):
    with open(path, encoding="utf-8-sig") as f:
        d = json.load(f)
    return d


# ------------------------------------------------------------------ corpus metadata
def read_meta(cut, want_court_dockets):
    sc = []  # (node, date, dockets)
    lower = collections.defaultdict(list)  # (court2, skeleton) -> [(date, node, toks)]
    files = sorted(glob.glob(os.path.join(CACHE, "*.meta.tsv.gz")))
    for i, p in enumerate(files):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                q = line.rstrip("\n").split("\t")
                if len(q) < 9 or not q[4].lstrip("-").isdigit():
                    continue
                ct = int(q[4])
                if ct == SCOTUS2:
                    if q[3] >= cut:
                        sc.append((q[0], q[3], scotus_dockets(q[5]), tokens(q[7]) | tokens(q[8])))
                    continue
                if want_court_dockets is None or ct not in want_court_dockets:
                    continue
                ds = lower_dockets(q[5]) & want_court_dockets[ct]
                if ds:
                    t = tokens(q[7]) | tokens(q[8])
                    for d in ds:
                        lower[(ct, d)].append((q[3], q[0], t))
        if (i + 1) % 100 == 0:
            sys.stderr.write("meta %d/%d\n" % (i + 1, len(files)))
    return sc, lower


def ymd(s):
    return datetime.date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cut", default="20210101")
    ap.add_argument("--out", default=os.path.join(HERE, "key"))
    ap.add_argument("--seen", default=os.path.join(HERE, "work", "seen_nodes.txt"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    names = court_names()
    st = collections.Counter()
    with open(a.seen, encoding="utf-8") as f:
        seen = {line.strip() for line in f if line.strip()}

    # 1. docket records
    rec = {}
    for p in sorted(glob.glob(os.path.join(HERE, "src_scdocket", "json", "*.json"))):
        d = read_record(p)
        dk = os.path.basename(p)[:-5]
        procs = d.get("ProceedingsandOrder") or []
        j = []
        for pr in procs:
            k = judgment(pr.get("Text", ""))
            if k:
                j.append((parse_date(pr.get("Date", "")), k))
        rec[dk] = dict(lct=d.get("LowerCourt") or "", ldk=d.get("LowerCourtCaseNumbers") or "",
                       ldate=parse_date(d.get("LowerCourtDecision") or ""),
                       toks=tokens(d.get("PetitionerTitle")) | tokens(d.get("RespondentTitle")), judg=j)
    st["records"] = len(rec)

    want = collections.defaultdict(set)
    unm = collections.Counter()
    for dk, r in rec.items():
        r["courts"] = map_court(r["lct"], names) if r["lct"] else set()
        if r["lct"] and not r["courts"]:
            unm[r["lct"]] += 1
        for c in r["courts"]:
            want[c] |= lower_dockets(r["ldk"])
    sc, lower = read_meta(a.cut, want)
    st["corpus_scotus_nodes_from_cut"] = len(sc)

    key = []
    order_info = {}
    for node, date, dks, otoks in sc:
        dks = sorted(set(dks))
        st["sc_nodes|with_docket" if dks else "sc_nodes|no_docket"] += 1
        res = []
        for dk in dks:
            st["dockets|all"] += 1
            r = rec.get(dk)
            if r is None:
                st["dockets|no_record"] += 1
                res.append(None)
                continue
            js = [k for (jd, k) in r["judg"] if jd == date]
            if not js:
                st["dockets|no_judgment_entry_on_node_date"] += 1
                res.append(None)
                continue
            if len(set(js)) > 1:
                st["dockets|conflicting_judgment_entries"] += 1
                res.append(None)
                continue
            kind, sub = js[0]
            sysn = ("federal" if FEDERAL_APPEALS.search(r["lct"]) or ("district court" in r["lct"].lower() and
                                                                       "united states" in r["lct"].lower())
                    else "state" if r["lct"] else "none")
            tag = "%s|%s" % (kind, sysn)
            st["dockets|judgment|%s" % tag] += 1
            if r["toks"] and otoks and not (r["toks"] & otoks):
                st["dockets|order_caption_mismatch"] += 1
                res.append(None)
                continue
            if not r["lct"] or not r["ldk"]:
                st["%s|lower_no_identifier" % tag] += 1
                res.append(None)
                continue
            if not r["courts"]:
                st["%s|lower_court_unmapped" % tag] += 1
                res.append(None)
                continue
            lds = lower_dockets(r["ldk"])
            if not lds or not r["ldate"]:
                st["%s|lower_docket_or_date_unparsed" % tag] += 1
                res.append(None)
                continue
            pool = {}
            for c in r["courts"]:
                for x in lds:
                    for (ld, ln, lt) in lower.get((c, x), []):
                        if ld < date:
                            pool[ln] = (ld, ln, lt, c)
            if not pool:
                st["%s|lower_docket_not_in_corpus" % tag] += 1
                res.append(None)
                continue
            conf = {n: v for n, v in pool.items() if not (r["toks"] and v[2]) or (r["toks"] & v[2])}
            exact = [v for v in conf.values() if v[0] == r["ldate"]]
            near = [v for v in conf.values() if abs((ymd(v[0]) - ymd(r["ldate"])).days) <= NEAR_DAYS]
            if len(exact) == 1:
                pick, how = exact[0], "exactDate"
            elif len(exact) > 1:
                st["%s|lower_ambiguous_exact" % tag] += 1
                res.append(None)
                continue
            elif len(near) == 1:
                pick, how = near[0], "nearDate"
            elif len(near) > 1:
                st["%s|lower_ambiguous_near" % tag] += 1
                res.append(None)
                continue
            else:
                st["%s|lower_date_not_matched" % tag] += 1
                res.append(None)
                continue
            ld, ln, lt, lc = pick
            st["%s|lower_linked|%s" % (kind, how)] += 1
            res.append(dict(order_node=node, lower_node=ln, kind=kind, sub=sub, order_date=date, lower_date=ld,
                            lower_court2=lc, system="federal" if FEDERAL_APPEALS.search(r["lct"]) or
                            "district court" in r["lct"].lower() and "united states" in r["lct"].lower()
                            else "state", link=how, sc_docket=dk))
        order_info[node] = (len(dks), sum(1 for x in res if x), int(bool(dks) and all(res)))
        for x in res:
            if x:
                key.append(x)

    # pairs: one line per (order, lower); conflicting kinds dropped; then builder-seen nodes dropped
    pairs = collections.defaultdict(list)
    for k in key:
        pairs[(k["order_node"], k["lower_node"])].append(k)
    final = []
    dropped_orders = set()
    for p, ks in sorted(pairs.items(), key=lambda x: (int(x[0][0]), int(x[0][1]))):
        if len({k["kind"] for k in ks}) > 1:
            st["pairs|conflicting_kinds_dropped"] += 1
            dropped_orders.add(p[0])
            continue
        if p[0] in seen or p[1] in seen:
            st["pairs|dropped_seen_by_builders|%s" % ("order" if p[0] in seen else "lower")] += 1
            dropped_orders.add(p[0])
            continue
        final.append(ks[0])
    st["pairs|kept"] = len(final)
    cols = ["order_node", "lower_node", "kind", "sub", "order_date", "lower_date", "lower_court2", "system", "link",
            "sc_docket"]
    with open(os.path.join(a.out, "timesplit_key.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for k in final:
            o.write("\t".join(str(k[c]) for c in cols) + "\n")
    keyed = sorted({k["order_node"] for k in final}, key=int)
    with open(os.path.join(a.out, "timesplit_orders.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("order_node\tdockets\tlinked\tcomplete\n")
        for on in keyed:
            n, l, c = order_info[on]
            c = int(c and on not in dropped_orders)
            o.write("%s\t%d\t%d\t%d\n" % (on, n, l, c))
            st["orders|keyed"] += 1
            st["orders|complete"] += c
    for k in final:
        st["key|kind|%s" % k["kind"]] += 1
        st["key|sub|%s" % k["sub"]] += 1
        st["key|system|%s|%s" % (k["system"], k["kind"])] += 1
        st["key|order_year|%s|%s" % (k["order_date"][:4], k["kind"])] += 1
        st["key|lower_year|%s" % k["lower_date"][:4]] += 1
        st["key|link|%s" % k["link"]] += 1
    with open(os.path.join(a.out, "timesplit_stats.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("# cut %s; records %d; seen-node list %s (sha1 %s, %d ids)\n" % (a.cut, len(rec), a.seen,
                                                                           sha1(a.seen), len(seen)))
        for k in sorted(st):
            o.write("%s\t%d\n" % (k, st[k]))
        for n, c in unm.most_common():
            o.write("unmapped_lower_court_name\t%s\t%d\n" % (n, c))
    sys.stderr.write("pairs kept %d, orders %d\n" % (len(final), len(keyed)))


if __name__ == "__main__":
    main()
