#!/usr/bin/env python3
"""Round 7 held-out key: Supreme Court orders (Shadow Docket Database v2.0, CC0) linked to corpus nodes.

    python -I build_key.py [--src src/shadow_docket_database_v2-0.csv] [--out key/]

Reads ONLY: the Shadow Docket CSV (src/), the round-6 corpus cache metadata (round6/history/cache/*.meta.tsv.gz:
node, date, court2 id, docket, title, parties) and the court tables of the round-6 frozen data
(round6/history/stage/final2/courts2.tsv, court_alias.tsv). It reads no model output (no history.tsv, status.tsv,
certs.tsv, no linker rows) and no other answer key.

Writes (in --out, private to the heldout folder):
  key.tsv          one line per key entry (header): the (order node, lower node) pair, the expected kind, dates
  orders.tsv       one line per order node in the key: complete = 1 when every selected Shadow entry that maps
                   to this order node was linked on the lower side (precision is scored on complete orders only)
  link_stats.tsv   aggregate match counts (no rows)
  unmapped_courts.tsv   lower-court names with no court2 id (name, count): aggregate, no case rows
"""
import argparse
import collections
import csv
import datetime
import glob
import gzip
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(C2, "round6", "history", "cache")
FINAL2 = os.path.join(C2, "round6", "history", "stage", "final2")
SCOTUS2 = 2906
csv.field_size_limit(10 ** 9)

# lower-court decision window before the order date (days); a cert petition is due 90 days after judgment or the
# denial of rehearing, extensions and held petitions make it longer; 3 years covers almost all (see HELDOUT.md)
WINDOW_DAYS = 3 * 365
DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−﹘﹣－"), "-")

# ------------------------------------------------------------------ kinds (key side only)
RX_VAC = re.compile(r"judgments?\s+(?:is\s+|are\s+)?vacated", re.I)
RX_DISM = re.compile(r"\b(?:appeals?|certiorari|petitions?(?:\s+for\s+(?:a\s+)?writs?\s+of\s+certiorari)?)\s+"
                     r"(?:is\s+|are\s+)?dismissed\b", re.I)


def kind_of(r):
    """Shadow row -> (kind, sub) or None."""
    ac = r["action_class"]
    at = (r["action_text"] or "") + " " + (r["text"] or "")
    if ac == "GVR":
        return ("vacated", "GVR")
    if ac == "Vacate and Remand":
        if r["relief"] != "Denied" and RX_VAC.search(at):
            return ("vacated", "vacateRemand")
        return None
    if ac == "Reversal":
        return ("reversed", "summaryReversal")
    if ac == "Affirmed":
        return ("affirmed", "affirmed")
    if ac == "Lack of Quorum":
        return ("affirmed", "lackOfQuorum")
    if ac == "DIG":
        return ("reviewDismissed", "DIG")
    if ac == "Dismiss":
        if r["relief"] != "Denied" and RX_DISM.search(at) and not re.search(r"\bdenied\b", r["action_text"] or "", re.I):
            return ("reviewDismissed", "dismissed")
        return None
    if ac == "Certiorari":
        if r["cert_granted"] == "0" and r["relief"] == "Denied":
            return ("certDenied", "certDenied")
        if r["relief"] == "Dismissed":
            return ("reviewDismissed", "certDismissed")
        return None
    return None


# ------------------------------------------------------------------ dockets
def scotus_docket(s):
    s = (s or "").translate(DASHES)
    out = []
    for part in re.split(r"[;,]|\band\b", s):
        m = re.search(r"(?<!\d)(\d{2})\s*-\s*0*(\d+)", part)
        if m:
            out.append("%s-%s" % (m.group(1), m.group(2)))
    return out


def lower_dockets(s):
    """Lower-court docket string -> set of digit skeletons ('4-15-123'); parts with fewer than 4 digits are dropped;
    a bare number after a full first docket takes that docket's prefix ('96-3321, 3406' -> 96-3406)."""
    s = (s or "").upper().translate(DASHES)
    if s in ("", "NA"):
        return set()
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


def toks_shadow(r):
    return tokens(r["petitioner"]) | tokens(r["respondent"])


# ------------------------------------------------------------------ courts
def norm_court(s):
    s = (s or "").lower().translate(DASHES).replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\bthe\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


ORD = {"first": "1", "second": "2", "third": "3", "fourth": "4", "fifth": "5", "sixth": "6", "seventh": "7",
       "eighth": "8", "ninth": "9", "tenth": "10", "eleventh": "11", "twelfth": "12", "thirteenth": "13",
       "fourteenth": "14"}


def court_names():
    """normalised court name -> set of court2 ids (courts2.tsv name and every court_alias.tsv name)."""
    m = collections.defaultdict(set)
    with open(os.path.join(FINAL2, "courts2.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            m[norm_court(p[3])].add(int(p[0]))
    with open(os.path.join(FINAL2, "court_alias.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            m[norm_court(p[2])].add(int(p[5]))
    return m


def name_variants(n):
    """Rewrites of a normalised Shadow court name, most specific first."""
    v = [n]
    base = n.split(" , ")[0]
    # 'court of appeals of texas fourth district' etc.: drop district / division qualifiers
    q = re.sub(r"\b(?:" + "|".join(ORD) + r"|\d+(?:st|nd|rd|th)?)\s+(?:appellate\s+)?(?:district|division|department|"
               r"circuit|judicial district)\b.*$", "", n).strip()
    q2 = re.sub(r"\b(?:district|division|department)\s+(?:" + "|".join(ORD) + r"|\d+|one|two|three|four|five|six|"
                r"i|ii|iii|iv|v)\b.*$", "", n).strip()
    q3 = re.sub(r"\b(?:eastern|western|middle|northern|southern|central)\s+(?:district|division)\b.*$", "", n).strip()
    for x in (base, q, q2, q3):
        if x and x not in v:
            v.append(x)
    out = []
    for x in v:
        out.append(x)
        m = re.match(r"^(supreme court|court of appeals?|court of criminal appeals|court of civil appeals|"
                     r"court of special appeals|appellate court|superior court|commonwealth court|court of appeal|"
                     r"intermediate court of appeals|appeals court|district court of appeal|court of common pleas)"
                     r" of (?:state of )?(.+)$", x)
        if m:
            out.append("%s %s" % (m.group(2), m.group(1)))
        m = re.match(r"^(.+?) (supreme court|court of appeals?|court of criminal appeals|court of civil appeals|"
                     r"court of special appeals|appellate court|superior court|commonwealth court|"
                     r"intermediate court of appeals|appeals court|district court of appeal)$", x)
        if m:
            out.append("%s of %s" % (m.group(2), m.group(1)))
        m = re.match(r"^united states court of appeals for (.+) circuit$", x)
        if m:
            out.append("united states court of appeals for %s circuit" % m.group(1).replace("district of columbia",
                                                                                            "district of columbia"))
    seen = []
    for x in out:
        if x not in seen:
            seen.append(x)
    return seen


def map_court(name, names, cache):
    if name in cache:
        return cache[name]
    n = norm_court(name)
    ids = set()
    for x in name_variants(n):
        if x in names:
            ids = set(names[x])
            break
    cache[name] = ids
    return ids


# ------------------------------------------------------------------ corpus metadata
def read_meta(want_court_dockets, want_scotus):
    """Stream every cache meta file. -> (orders: docket -> [(date, node, toks)],
    lower: (court2, skeleton) -> [(date, node, toks)])"""
    orders = collections.defaultdict(list)
    lower = collections.defaultdict(list)
    files = sorted(glob.glob(os.path.join(CACHE, "*.meta.tsv.gz")))
    for i, p in enumerate(files):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                q = line.rstrip("\n").split("\t")
                if len(q) < 9 or not q[4].lstrip("-").isdigit():
                    continue
                ct = int(q[4])
                if ct == SCOTUS2:
                    if q[3] >= "19930000":
                        for d in scotus_docket(q[5]):
                            if d in want_scotus:
                                orders[d].append((q[3], q[0], tokens(q[7]) | tokens(q[8])))
                    continue
                if ct not in want_court_dockets:
                    continue
                ds = lower_dockets(q[5]) & want_court_dockets[ct]
                if ds:
                    t = tokens(q[7]) | tokens(q[8])
                    for d in ds:
                        lower[(ct, d)].append((q[3], q[0], t))
        if (i + 1) % 100 == 0:
            sys.stderr.write("meta %d/%d\n" % (i + 1, len(files)))
    return orders, lower


def ymd(s):
    return datetime.date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def era(y):
    y = int(y)
    return "1993-2005" if y <= 2005 else ("2006-2009" if y <= 2009 else ("2010-2012" if y <= 2012 else
                                                                         ("2013-2020" if y <= 2020 else "2021+")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(HERE, "src", "shadow_docket_database_v2-0.csv"))
    ap.add_argument("--out", default=os.path.join(HERE, "key"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    names = court_names()
    ccache = {}

    # 1. Shadow rows -> entries per (docket, date)
    ent = collections.OrderedDict()  # (docket, date) -> dict
    st = collections.Counter()
    with open(a.src, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            k = kind_of(r)
            if not k:
                continue
            st["shadow_rows_selected"] += 1
            st["shadow_rows_selected_" + k[1]] += 1
            m = re.match(r"^(\d{2})-0*(\d+)$", (r["docket_number"] or "").strip())
            if not m:
                st["drop_noncase_docket"] += 1
                continue
            dk = "%s-%s" % (m.group(1), m.group(2))
            d = r["date"].replace("-", "")
            e = ent.setdefault((dk, d), dict(dk=dk, date=d, kinds=set(), subs=set(), lct=r["lower_ct"],
                                             ldk=r["lower_docket"], toks=toks_shadow(r)))
            e["kinds"].add(k[0])
            e["subs"].add(k[1])
    st["entries_docket_date"] = len(ent)

    # 2. corpus coverage of Supreme Court orders by year (decides the years the corpus can hold)
    want_scotus = {e["dk"] for e in ent.values()}
    want_cd = collections.defaultdict(set)
    for e in ent.values():
        if len(e["kinds"]) != 1:
            continue
        ids = map_court(e["lct"], names, ccache) if e["lct"] not in ("", "NA") else set()
        e["courts"] = ids
        for c in ids:
            want_cd[c] |= lower_dockets(e["ldk"])
    sys.stderr.write("reading corpus metadata (%d courts)\n" % len(want_cd))
    orders, lower = read_meta(want_cd, want_scotus)
    per_year = collections.Counter()
    for v in orders.values():
        for (d, n, t) in v:
            per_year[d[:4]] += 1
    # a year the corpus holds = at least 1000 Supreme Court nodes with a docket in the selected set
    held_years = {y for y, c in per_year.items() if c >= 1000}

    # 3. link
    unm = collections.Counter()
    key = []
    order_entries = collections.defaultdict(list)  # order node -> [linked?]
    for (dk, d), e in ent.items():
        y = d[:4]
        kind = None
        if len(e["kinds"]) != 1:
            st["drop_conflicting_kinds"] += 1
            continue
        kind = next(iter(e["kinds"]))
        sub = "+".join(sorted(e["subs"]))
        tag = kind
        st["%s|entries" % tag] += 1
        if y not in held_years:
            st["%s|drop_year_not_in_corpus" % tag] += 1
            continue
        st["%s|in_corpus_years" % tag] += 1
        # order side: same docket, same date, unique; caption confirmed when both sides have tokens
        cands = [c for c in orders.get(dk, []) if c[0] == d]
        if len(cands) == 0:
            st["%s|order_none" % tag] += 1
            continue
        if len(cands) > 1:
            st["%s|order_ambiguous" % tag] += 1
            continue
        od, onode, otoks = cands[0]
        if e["toks"] and otoks and not (e["toks"] & otoks):
            st["%s|order_caption_mismatch" % tag] += 1
            continue
        st["%s|order_linked" % tag] += 1
        # lower side
        if e["lct"] in ("", "NA") or e["ldk"] in ("", "NA"):
            st["%s|lower_no_identifier" % tag] += 1
            order_entries[onode].append(0)
            continue
        ids = e.get("courts") or set()
        if not ids:
            st["%s|lower_court_unmapped" % tag] += 1
            unm[e["lct"]] += 1
            order_entries[onode].append(0)
            continue
        lds = lower_dockets(e["ldk"])
        if not lds:
            st["%s|lower_docket_unparsed" % tag] += 1
            order_entries[onode].append(0)
            continue
        dd = ymd(d)
        pool = {}
        for c in ids:
            for x in lds:
                for (ld, ln, lt) in lower.get((c, x), []):
                    gap = (dd - ymd(ld)).days
                    if 0 < gap <= WINDOW_DAYS:
                        pool[ln] = (ld, ln, lt, c)
        if not pool:
            st["%s|lower_none" % tag] += 1
            order_entries[onode].append(0)
            continue
        conf = {n: v for n, v in pool.items() if not (e["toks"] and v[2]) or (e["toks"] & v[2])}
        if not conf:
            st["%s|lower_caption_mismatch" % tag] += 1
            order_entries[onode].append(0)
            continue
        if len(conf) > 1:
            st["%s|lower_ambiguous" % tag] += 1
            order_entries[onode].append(0)
            continue
        ld, ln, lt, lc = next(iter(conf.values()))
        capq = "confirmed" if (e["toks"] and lt) else "docket_only"
        st["%s|lower_linked" % tag] += 1
        st["%s|lower_linked_%s" % (tag, capq)] += 1
        order_entries[onode].append(1)
        key.append(dict(order_node=onode, lower_node=ln, kind=kind, sub=sub, order_date=d, lower_date=ld,
                        lower_court2=lc, gap_days=(dd - ymd(ld)).days, era=era(y), sc_docket=dk,
                        lower_caption=capq))

    # one line per (order, lower) pair; a pair keyed twice with different kinds is dropped
    pairs = collections.defaultdict(list)
    for k in key:
        pairs[(k["order_node"], k["lower_node"])].append(k)
    final = []
    for p, ks in pairs.items():
        if len({k["kind"] for k in ks}) > 1:
            st["pair_conflicting_kinds_dropped"] += 1
            continue
        if len(ks) > 1:
            st["pair_duplicates_merged"] += len(ks) - 1
        final.append(ks[0])
    final.sort(key=lambda k: (k["order_date"], int(k["order_node"]), int(k["lower_node"])))
    cols = ["order_node", "lower_node", "kind", "sub", "order_date", "lower_date", "lower_court2", "gap_days", "era",
            "sc_docket", "lower_caption"]
    with open(os.path.join(a.out, "key.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for k in final:
            o.write("\t".join(str(k[c]) for c in cols) + "\n")
    keyed_orders = {k["order_node"] for k in final}
    with open(os.path.join(a.out, "orders.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("order_node\tentries\tlinked\tcomplete\n")
        for on in sorted(keyed_orders, key=int):
            v = order_entries[on]
            o.write("%s\t%d\t%d\t%d\n" % (on, len(v), sum(v), int(all(v))))
    st["key_pairs"] = len(final)
    st["key_orders"] = len(keyed_orders)
    st["key_orders_complete"] = sum(all(order_entries[on]) for on in keyed_orders)
    for k in final:
        st["key|kind|%s" % k["kind"]] += 1
        st["key|sub|%s" % k["sub"]] += 1
        st["key|era|%s|%s" % (k["era"], k["kind"])] += 1
        st["key|year|%s|%s" % (k["order_date"][:4], k["kind"])] += 1
        st["key|lower_year|%s" % k["lower_date"][:4]] += 1
        st["key|lower_caption|%s" % k["lower_caption"]] += 1
        st["key|gap_days_bin|%s" % ("<=120" if k["gap_days"] <= 120 else "<=365" if k["gap_days"] <= 365 else
                                     "<=730" if k["gap_days"] <= 730 else ">730")] += 1
    with open(os.path.join(a.out, "link_stats.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("# source sha1 %s; corpus years held (>=1000 Supreme Court nodes with a selected docket): %s\n" %
                (sha1(a.src), ",".join(sorted(held_years))))
        for k in sorted(st):
            o.write("%s\t%d\n" % (k, st[k]))
        for y in sorted(per_year):
            o.write("corpus_scotus_nodes_selected_dockets|%s\t%d\n" % (y, per_year[y]))
    with open(os.path.join(a.out, "unmapped_courts.tsv"), "w", encoding="utf-8", newline="\n") as o:
        for n, c in unm.most_common():
            o.write("%s\t%d\n" % (n, c))
    sys.stderr.write("key pairs %d, orders %d\n" % (len(final), len(keyed_orders)))


if __name__ == "__main__":
    main()
