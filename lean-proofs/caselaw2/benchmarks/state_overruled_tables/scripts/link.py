"""Link the extracted table rows to corpus decisions; write the answer key.

    python -X utf8 link.py            (paths are fixed relative to the benchmark folder)

Inputs:  work/extract/georgia_entries.tsv (georgia_extract.py), work/reader_out/*.tsv (reader sub-agents),
         work/old_index.tsv (build_index.py), corpus texts from git (only to verify treating-side links, see below).
Outputs: work/extracted.tsv   every extracted row in one format (row_id, table, leaf, ... , extractor)
         links.tsv            one row per (row, side): cite, keys tried, link status, node, form
         key.tsv              PRIMARY rows (class overruled / overruled_partial): link status of each side, pair status,
                              x node, y node, split half
         secondary_pairs.tsv  the other classes, linked the same way (not scored)
         link_report.tsv      counts of pair status per table and overall

Linking one citation (never guessed):
  1. keys = r6cite.keys(cite) plus LOCAL_ALIAS tokens; the decisions whose citation has that key
     (old_index.tsv: decisions dated to 1930).
     one decision            -> `exact` (if the table gives a name, at least one name token must match, else
                                `name_mismatch`)
     several                 -> the table's name must pick exactly one (`exact_by_name`), else `several_on_page`
  2. no decision starts at that page -> pin cite: the decision with the largest first page <= the page in the same
     volume, at most PIN_SPAN pages before it -> `pin` (if the table gives a name it must match);
     else `not_in_corpus` (volume present) / `volume_not_in_corpus` / `reporter_not_in_corpus`.
  2b. `name_mismatch` / `not_in_corpus` with a table name: the one decision of that volume whose name matches every
     (>= 2) name token of the table -> `volume_by_name` (a misprinted or misread page).
  3. `no_citation` when the table gives none; `bad_citation` when it cannot be parsed.
Treating side (Y) without a name in the table (Georgia, Desty, Benjamin tables give citations only): the link is kept
only if Y's corpus text cites X (its volume/reporter/page, or X's first party name followed by " v."): otherwise
`y_text_does_not_cite_x`. The same check is applied to `pin` links with a name.
Pair checks: both sides linked; X != Y; neither side a federal court (`federal_court`); same state system (repo without -appellate*/-other-courts);
date(Y) > date(X) (equal allowed only when both are year-only dates yyyy0101); date(Y) <= end of the table's publication year.
"""
import collections
import difflib
import glob
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(HERE)
BENCH = os.path.dirname(B)
ROOT = os.path.dirname(BENCH)
sys.path.insert(0, os.path.join(ROOT, "round6", "history", "citeforms"))
sys.path.insert(0, os.path.join(BENCH, "common"))
import r6cite  # noqa: E402
import benchlib  # noqa: E402

REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
W = os.path.join(B, "work")
PIN_SPAN = 60
DATASET = "state_overruled_tables"
PUB_END = {"georgia1922": 19221231, "labatt1860": 18601231, "desty1874": 18741231, "greenleaf1838": 18381231,
           "benjamin1893": 18931231}
TABLE_LABEL = {"georgia1922": "casesingeorgiar00appegoog", "labatt1860": "atablecasesinca00labagoog",
               "desty1874": "californiacitat00destgoog", "greenleaf1838": "acollectioncase01greegoog",
               "benjamin1893": "cu31924022823318"}
PRIMARY = {"overruled", "overruled_partial"}
# reporter tokens as the old tables print them -> the token the corpus index uses (measured on old_index.tsv)
LOCAL_ALIAS = {
    "serg&r": "serg&rawle", "sergr": "serg&rawle", "watts&s": "watts&serg", "johnsr": "johns", "johnr": "johns",
    "jr": "johns", "cowen": "cow", "wendr": "wend", "nhr": "nh", "connr": "conn", "pickr": "pick", "massr": "mass",
    "vtr": "vt", "nys": "nys", "nycp": "nys", "johncas": "johnscas", "johnsc": "johnscas", "johnch": "johnsch",
    "hillr": "hill", "barbr": "barb", "gal": "cal", "calr": "cal", "nysupp": "nys", "nyst": "nyst",
    # Greenleaf's Maine Reports 1-9 are Me. 1-9; "Mon." before 1840 is T. B. Monroe (Ky.); "Penn." in an 1838 book
    # is Penrose & Watts; "Con." in a New York table is Connoly's Surrogate Reports; "Bin." = Binney; "Den." = Denio
    "greenl": "me", "mon": "tbmon", "penn": "pen&w", "con": "connolysurrep", "bin": "binn", "den": "denio",
}
STOP = set("""v vs the and of for ex parte in re matter et al co company inc corporation corp people state
city county mayor town village board commissioners commonwealth united states estate administrator executor
appellant respondent plaintiff defendant others bank railroad rail road ins insurance r""".split())
CITE_RX = re.compile(r"^\s*(\d{1,4})\s+(.+?)\s*,?\s+(\d{1,5})(?:\s*[-–]\s*\d+)?\s*\.?$")


def is_federal(repo):
    return bool(re.match(r"^(ca\d+|cadc|cafc|supreme-court|federal-special|bankruptcy)(-|$)", repo))


def family(repo):
    return re.sub(r"-(appellate(-\d+-\d+)?|other-courts)$", "", repo)


def name_tokens(s):
    return {t for t in re.findall(r"[a-z]{3,}", (s or "").lower().replace("’", "'")) if t not in STOP}


def name_match(table_name, corpus_name):
    a, b = name_tokens(table_name), name_tokens(corpus_name)
    if not a:
        return True  # nothing to check (e.g. "People v. -")
    for x in a:
        for y in b:
            if x == y or (len(x) >= 5 and len(y) >= 5 and x[:5] == y[:5]) or \
                    difflib.SequenceMatcher(None, x, y).ratio() >= 0.8:
                return True
    return False


def load_index():
    idx = collections.defaultdict(list)
    vols = collections.defaultdict(dict)   # (vol, tok) -> {page: [rows]}
    toks = set()
    with open(os.path.join(W, "old_index.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 8:
                continue
            row = {"node": int(p[1]), "date": int(p[2]), "repo": p[3], "court": p[4], "name": p[5], "cite": p[6],
                   "path": p[7]}
            idx[p[0]].append(row)
            m = re.match(r"^(\d+) (\S+) (\d+)$", p[0])
            if m:
                vols[(m.group(1), m.group(2))].setdefault(int(m.group(3)), []).append(row)
                toks.add(m.group(2))
    return idx, vols, toks


def cite_keys(cite):
    c = (cite or "").strip()
    m = CITE_RX.match(c.replace(" ,", ","))
    if not m:
        return None
    v, rep, pg = m.group(1), m.group(2).rstrip(","), m.group(3)
    ks = r6cite.keys("%s %s %s" % (v, rep, pg))
    out = list(ks)
    for k in ks:
        t = k.split(" ")[1]
        if t in LOCAL_ALIAS:
            out.append("%s %s %s" % (v, LOCAL_ALIAS[t], pg))
    seen = []
    for k in out:
        if k not in seen:
            seen.append(k)
    return seen


def uniq_nodes(rows):
    d = {}
    for r in rows:
        d.setdefault(r["node"], r)
    return list(d.values())


def strong_match(table_name, corpus_name):
    """every non-stop token of the table name (at least two) matches a corpus-name token"""
    a, b = name_tokens(table_name), name_tokens(corpus_name)
    if len(a) < 2:
        return False
    return all(any(x == y or (len(x) >= 5 and x[:5] == y[:5]) or
                   difflib.SequenceMatcher(None, x, y).ratio() >= 0.8 for y in b) for x in a)


def link_one(cite, name, idx, vols, toks):
    """-> (status, row or None, form, keys); a page that holds another case is retried by name in the volume"""
    r = _link_one(cite, name, idx, vols, toks)
    if r[0] in ("name_mismatch", "not_in_corpus") and name and name != "-" and r[3]:
        for k in r[3]:
            v, t, _pg = k.split(" ")
            pages = vols.get((v, t))
            if not pages:
                continue
            hit = uniq_nodes([row for rows in pages.values() for row in rows if strong_match(name, row["name"])])
            if len(hit) == 1:
                return "linked", hit[0], "volume_by_name", r[3]
    return r


def _link_one(cite, name, idx, vols, toks):
    """-> (status, row or None, form, keys)"""
    if not cite or cite.strip() in ("-", "?", ""):
        return "no_citation", None, "-", []
    ks = cite_keys(cite)
    if not ks:
        return "bad_citation", None, "-", []
    for k in ks:
        rows = uniq_nodes(idx.get(k, []))
        if not rows:
            continue
        if len(rows) == 1:
            if name and name != "-" and not name_match(name, rows[0]["name"]):
                return "name_mismatch", rows[0], "exact", ks
            return "linked", rows[0], "exact", ks
        if name and name != "-":
            nm = [r for r in rows if name_match(name, r["name"])]
            if len(nm) == 1:
                return "linked", nm[0], "exact_by_name", ks
        return "several_on_page", rows, "exact", ks
    # pin cite
    any_vol = False
    for k in ks:
        v, t, pg = k.split(" ")
        pages = vols.get((v, t))
        if not pages:
            continue
        any_vol = True
        pg = int(pg)
        cands = [p for p in pages if p <= pg and pg - p <= PIN_SPAN]
        if not cands:
            continue
        start = max(cands)
        rows = uniq_nodes(pages[start])
        if len(rows) != 1:
            if name and name != "-":
                nm = [r for r in rows if name_match(name, r["name"])]
                if len(nm) == 1:
                    return "linked", nm[0], "pin_by_name", ks
            return "several_on_page", rows, "pin", ks
        if name and name != "-" and not name_match(name, rows[0]["name"]):
            return "name_mismatch", rows[0], "pin", ks
        return "linked", rows[0], "pin", ks
    if any_vol:
        return "not_in_corpus", None, "-", ks
    if any(k.split(" ")[1] in toks for k in ks):
        return "volume_not_in_corpus", None, "-", ks
    return "reporter_not_in_corpus", None, "-", ks


def fetch_texts(rows):
    """{node: text} from git HEAD, one cat-file per repo."""
    by_repo = collections.defaultdict(list)
    for r in rows:
        by_repo[r["repo"]].append(r)
    out = {}
    for repo, items in by_repo.items():
        rd = os.path.join(REPOS, repo)
        inp = "".join("HEAD:%s\n" % r["path"] for r in items).encode("utf-8")
        res = subprocess.run(["git", "-C", rd, "cat-file", "--batch"], input=inp, capture_output=True,
                             creationflags=0x08000000 if os.name == "nt" else 0).stdout
        pos = 0
        for r in items:
            e = res.find(b"\n", pos)
            header = res[pos:e].split()
            if len(header) < 3 or header[1] != b"blob":
                pos = e + 1
                continue
            size = int(header[2])
            out[r["node"]] = res[e + 1:e + 1 + size].decode("utf-8", "replace").replace("\r\n", "\n")
            pos = e + 1 + size + 1
    return out


def squash(s):
    return re.sub(r"[\s.,']", "", s.lower())


def text_cites(text, xrow, xkeys):
    """Does the text cite decision xrow (any of its citation keys, or its first party name + ' v.')?"""
    sq = squash(text)
    forms = set()
    for k in xkeys:
        v, t, pg = k.split(" ")
        forms.add((v, t.replace("(", "").replace(")", ""), pg))
    for c in re.split(r"\||;\s+", xrow["cite"]):
        for k in r6cite.keys(c.strip()) or []:
            v, t, pg = k.split(" ")
            forms.add((v, t.replace("(", "").replace(")", ""), pg))
    for v, t, pg in forms:
        for m in re.finditer(re.escape(v + t + pg), sq):
            a, b = m.start(), m.end()
            if (a == 0 or not sq[a - 1].isdigit()) and (b >= len(sq) or not sq[b].isdigit()):
                return "cite"
    # same volume and page in any reporter name ("1 Kelly, 315" for 1 Ga. 315; "5 Cowen, 297")
    for v, t, pg in forms:
        if re.search(r"(?<![\d§])" + v + r"\s+[A-Z][A-Za-z.&'’ ]{0,25}?,?\s+" + pg + r"(?!\d)", text):
            return "vol_page"
    # a party name of X next to "v." / "vs." (either party order)
    toks = [t for t in re.findall(r"[A-Za-z]{4,}", xrow["name"]) if t.lower() not in STOP]
    for t in toks:
        e = re.escape(t)
        if re.search(r"\b" + e + r"\b[^\n]{0,50}?\bvs?\.?\s|\bvs?\.\s[^\n]{0,50}?\b" + e + r"\b", text):
            return "name"
    return None


def read_georgia():
    rows = []
    p = os.path.join(W, "extract", "georgia_entries.tsv")
    with open(p, encoding="utf-8") as f:
        next(f)
        for line in f:
            q = line.rstrip("\n").split("\t")
            leaf, eno, lraw, lkey, lab, cls, cites, seg, ent = q[:9]
            if cls == "other" or not cites:
                if cls in PRIMARY and not cites:
                    rows.append(["georgia1922", leaf, "-", lkey if lkey != "?" else "-", "-", "-", lab, cls, "-",
                                 seg[:150], "no treating citation parsed", "regex-coords:e%s" % eno])
                continue
            for c in cites.split(";"):
                rows.append(["georgia1922", leaf, "-", lkey if lkey != "?" else "-", "-", c, lab, cls, "-",
                             seg[:150], "left=" + lraw, "regex-coords:e%s" % eno])
    return rows


def read_readers():
    rows = []
    for p in sorted(glob.glob(os.path.join(W, "reader_out", "*.tsv"))):
        base = os.path.basename(p)[:-4]
        with open(p, encoding="utf-8") as f:
            for i, line in enumerate(f):
                q = line.rstrip("\n").split("\t")
                if len(q) < 12:
                    q += ["-"] * (12 - len(q))
                table, chunk, leaf, xname, xcite, yname, ycite, wording, cls, topic, quote, note = q[:12]
                if table == "table":
                    continue
                rows.append([table, leaf, xname, xcite, yname, ycite, wording, cls.strip(), topic, quote, note,
                             "reader:%s:%d" % (base, i + 1)])
    return rows


def main():
    idx, vols, toks = load_index()
    ext = read_georgia() + read_readers()
    hdr_ext = ["row_id", "table", "leaf", "treated_name", "treated_cite", "treating_name", "treating_cite",
               "wording", "class", "topic", "quote", "note", "extractor"]
    linked = []
    for i, r in enumerate(ext):
        rid = "r%05d" % i
        xs = link_one(r[3], r[2], idx, vols, toks)
        ys = link_one(r[5], r[4], idx, vols, toks)
        linked.append((rid, r, xs, ys))
    # several decisions on a page: the corpus text of the treating decision picks one (never guessed)
    want = {}
    for rid, r, xs, ys in linked:
        if ys[0] == "several_on_page":
            for c in ys[1]:
                want[c["node"]] = c
        elif ys[0] == "linked":
            want[ys[1]["node"]] = ys[1]
    texts = fetch_texts(list(want.values()))
    res = []
    for rid, r, xs, ys in linked:
        if ys[0] == "several_on_page" and xs[0] == "linked":
            hit = [c for c in ys[1] if texts.get(c["node"]) and text_cites(texts[c["node"]], xs[1], xs[3])]
            if len(hit) == 1:
                ys = ("linked", hit[0], ys[2] + "_by_text", ys[3])
        if xs[0] == "several_on_page" and ys[0] == "linked" and texts.get(ys[1]["node"]):
            t = texts[ys[1]["node"]]
            hit = [c for c in xs[1] if text_cites(t, dict(c, cite="-"), []) == "name"]
            if len(hit) == 1:
                xs = ("linked", hit[0], xs[2] + "_by_text", xs[3])
        if xs[0] != "linked" and isinstance(xs[1], list):
            xs = (xs[0], None, xs[2], xs[3])
        if ys[0] != "linked" and isinstance(ys[1], list):
            ys = (ys[0], None, ys[2], ys[3])
        res.append((rid, r, xs, ys))
    linked = res
    # treating side given by citation only, or linked by a pin cite: its text must cite X
    need = {}
    for rid, r, xs, ys in linked:
        if xs[0] == "linked" and ys[0] == "linked" and (r[4] in ("-", "") or ys[2].startswith("pin")):
            need[ys[1]["node"]] = ys[1]
    with open(os.path.join(W, "extracted.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(hdr_ext) + "\n")
        for rid, r, xs, ys in linked:
            o.write("\t".join([rid] + [str(x).replace("\t", " ") for x in r]) + "\n")
    lk = open(os.path.join(B, "links.tsv"), "w", encoding="utf-8", newline="\n")
    lk.write("row_id\tside\tcite\tname\tkeys\tlink\tform\tnode\tnode_date\tnode_repo\tnode_name\tnode_cite\n")
    key_rows, sec_rows = [], []
    stat = collections.defaultdict(collections.Counter)
    for rid, r, xs, ys in linked:
        table, leaf, xname, xcite, yname, ycite, wording, cls = r[:8]
        for side, (st, row, form, ks), cite, nm in (("X", xs, xcite, xname), ("Y", ys, ycite, yname)):
            lk.write("\t".join([rid, side, cite, nm, ",".join(ks), st, form,
                                str(row["node"]) if row else "-", str(row["date"]) if row else "-",
                                row["repo"] if row else "-", row["name"] if row else "-",
                                row["cite"] if row else "-"]) + "\n")
        xr, yr = xs[1], ys[1]
        ver = "-"
        if xs[0] != "linked":
            pair = "x_" + xs[0]
        elif ys[0] != "linked":
            pair = "y_" + ys[0]
        elif xr["node"] == yr["node"]:
            pair = "same_decision"
        elif is_federal(xr["repo"]) or is_federal(yr["repo"]):
            pair = "federal_court"  # this is a state key; federal pairs would go to federal_overruled_tables
        elif family(xr["repo"]) != family(yr["repo"]):
            pair = "other_system"
        elif yr["date"] < xr["date"] or (yr["date"] == xr["date"] and yr["date"] % 10000 != 101):
            # equal year-only dates (yyyy0101: the corpus knows only the year) are allowed
            pair = "date_order"
        elif yr["date"] > PUB_END.get(table, 99999999):
            pair = "after_publication"
        else:
            pair = "linked"
            if yr["node"] in need:
                t = texts.get(yr["node"])
                ver = text_cites(t, xr, xs[3]) if t else None
                if not ver:
                    pair = "y_text_does_not_cite_x"
                    ver = "none"
        half = "-"
        xkey = "-"
        if xr is not None:
            first = re.split(r"\||;\s+", xr["cite"])[0]
            ks = r6cite.keys(first)
            xkey = ks[0] if ks else "node:%d" % xr["node"]
            half = benchlib.split_half(DATASET, xkey)
        out = [rid, table, leaf, TABLE_LABEL.get(table, "-"), cls, "1" if cls == "overruled_partial" else "0",
               wording, xname, xcite, yname, ycite, xs[0], xs[2], ys[0], ys[2], pair, ver,
               str(xr["node"]) if xr else "-", str(xr["date"]) if xr else "-", xr["name"] if xr else "-",
               xr["repo"] if xr else "-", str(yr["node"]) if yr else "-", str(yr["date"]) if yr else "-",
               yr["name"] if yr else "-", xkey, half, r[9][:150], r[11]]
        out = [str(x).replace("\t", " ") for x in out]
        if cls in PRIMARY:
            key_rows.append(out)
            stat[table][pair] += 1
            stat["ALL"][pair] += 1
        else:
            sec_rows.append(out)
    lk.close()
    hdr = ["row_id", "table", "leaf", "ia_identifier", "class", "partial", "wording", "treated_name", "treated_cite",
           "treating_name", "treating_cite", "x_link", "x_form", "y_link", "y_form", "pair_status", "y_cites_x",
           "x_node", "x_date", "x_corpus_name", "x_repo", "y_node", "y_date", "y_corpus_name", "x_key", "half",
           "quote", "extractor"]
    for name, rows in (("key.tsv", key_rows), ("secondary_pairs.tsv", sec_rows)):
        with open(os.path.join(B, name), "w", encoding="utf-8", newline="\n") as o:
            o.write("\t".join(hdr) + "\n")
            for x in rows:
                o.write("\t".join(x) + "\n")
    with open(os.path.join(B, "link_report.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("table\tpair_status\trows\n")
        for t in sorted(stat):
            for k, v in stat[t].most_common():
                o.write("%s\t%s\t%d\n" % (t, k, v))
    for t in sorted(stat):
        n = sum(stat[t].values())
        print(t, n, dict(stat[t].most_common()))
    print("secondary rows", len(sec_rows))


if __name__ == "__main__":
    main()
