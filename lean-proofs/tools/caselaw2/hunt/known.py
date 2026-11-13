"""Known overrulings from the literature (CRS Constitution Annotated table, casebooks), used to validate the zombie
search: for each, is the target resolved to a node, does our status layer mark it negative from the overruling date,
and how many citing decisions after that date does the corpus hold.

    python known.py [--out DIR] [--write FILE]   -> hunt/data/known_overrulings.tsv

--out: a status.tsv / findings.tsv directory other than caselaw-lean-2/out. Both layouts are read: the Lean runner's
(header line; status `neg:<kind>`, actor in column 10) and the Python reference's (no header; status `negative`, kind
in column 7, actor in column 8). Round 2: an overruler whose citation the hunt's sqlite table lacks is looked up in
graph/cite_index.tsv (Dobbs, Loper Bright, Wayfair, Janus, Knick, Hyatt, Ramos were unresolved before); a negative
status counts as "from the right date" only when it starts on or before the day after the overruler's date.
"""
import argparse, os, re
from collections import defaultdict
import hcommon as C

# (target, target cite(s), overruler, overruler cite(s), year, note)
KNOWN = [
    ("Bowers v. Hardwick", "478 us 186", "Lawrence v. Texas", "539 us 558", 2003, "express"),
    ("Betts v. Brady", "316 us 455", "Gideon v. Wainwright", "372 us 335", 1963, "express"),
    ("Plessy v. Ferguson", "163 us 537", "Brown v. Board of Education", "347 us 483", 1954, "not express (CRS 2016 only)"),
    ("Adkins v. Children's Hospital", "261 us 525", "West Coast Hotel v. Parrish", "300 us 379", 1937, "express; Lochner era"),
    ("Lochner v. New York", "198 us 45", "Ferguson v. Skrupa", "372 us 726", 1963, "sub silentio"),
    ("Hammer v. Dagenhart", "247 us 251", "United States v. Darby", "312 us 100", 1941, "express"),
    ("Swift v. Tyson", "41 us 1", "Erie R.R. v. Tompkins", "304 us 64", 1938, "express"),
    ("Wolf v. Colorado", "338 us 25", "Mapp v. Ohio", "367 us 643", 1961, "in part"),
    ("Swain v. Alabama", "380 us 202", "Batson v. Kentucky", "476 us 79", 1986, "in part"),
    ("Ohio v. Roberts", "448 us 56", "Crawford v. Washington", "541 us 36", 2004, "abrogated"),
    ("Conley v. Gibson", "355 us 41", "Bell Atlantic v. Twombly", "550 us 544", 2007, "'retired' in part"),
    ("Saucier v. Katz", "533 us 194", "Pearson v. Callahan", "555 us 223", 2009, "in part (sequence)"),
    ("Austin v. Michigan Chamber of Commerce", "494 us 652", "Citizens United v. FEC", "558 us 310", 2010, "express"),
    ("Harris v. United States", "536 us 545", "Alleyne v. United States", "570 us 99", 2013, "express"),
    ("Booth v. Maryland", "482 us 496", "Payne v. Tennessee", "501 us 808", 1991, "in part"),
    ("South Carolina v. Gathers", "490 us 805", "Payne v. Tennessee", "501 us 808", 1991, "in part"),
    ("Albrecht v. Herald Co.", "390 us 145", "State Oil Co. v. Khan", "522 us 3", 1997, "express"),
    ("Dr. Miles Medical Co. v. John D. Park & Sons", "220 us 373", "Leegin Creative Leather v. PSKS", "551 us 877", 2007, "express"),
    ("United States v. Halper", "490 us 435", "Hudson v. United States", "522 us 93", 1997, "in part"),
    ("Grady v. Corbin", "495 us 508", "United States v. Dixon", "509 us 688", 1993, "express"),
    ("National League of Cities v. Usery", "426 us 833", "Garcia v. San Antonio MTA", "469 us 528", 1985, "express"),
    ("Quill Corp. v. North Dakota", "504 us 298", "South Dakota v. Wayfair", "585 us 162", 2018, "express"),
    ("Abood v. Detroit Board of Education", "431 us 209", "Janus v. AFSCME", "585 us 878", 2018, "express"),
    ("Roe v. Wade", "410 us 113", "Dobbs v. Jackson Women's Health", "597 us 215", 2022, "express"),
    ("Planned Parenthood v. Casey", "505 us 833", "Dobbs v. Jackson Women's Health", "597 us 215", 2022, "express"),
    ("Chevron v. NRDC", "467 us 837", "Loper Bright Enterprises v. Raimondo", "603 us 369", 2024, "express"),
    ("Williamson County Regional Planning v. Hamilton Bank", "473 us 172", "Knick v. Township of Scott", "588 us 180", 2019, "in part"),
    ("Nevada v. Hall", "440 us 410", "Franchise Tax Bd. v. Hyatt", "587 us 230", 2019, "express"),
    ("Apodaca v. Oregon", "406 us 404", "Ramos v. Louisiana", "140 s ct 1390", 2020, "express"),
    ("Wilko v. Swan", "346 us 427", "Rodriguez de Quijas v. Shearson", "490 us 477", 1989, "express"),
    ("Minersville School Dist. v. Gobitis", "310 us 586", "West Virginia Bd. of Ed. v. Barnette", "319 us 624", 1943, "express"),
    ("Whitney v. California", "274 us 357", "Brandenburg v. Ohio", "395 us 444", 1969, "express"),
    ("Pennsylvania v. Union Gas", "491 us 1", "Seminole Tribe v. Florida", "517 us 44", 1996, "express"),
    ("Michigan v. Jackson", "475 us 625", "Montejo v. Louisiana", "556 us 778", 2009, "express"),
    ("Monroe v. Pape", "365 us 167", "Monell v. Dept. of Social Services", "436 us 658", 1978, "in part"),
    ("Grovey v. Townsend", "295 us 45", "Smith v. Allwright", "321 us 649", 1944, "express"),
    ("Sinclair Refining v. Atkinson", "370 us 195", "Boys Markets v. Retail Clerks", "398 us 235", 1970, "express"),
    ("Stein v. New York", "346 us 156", "Jackson v. Denno", "378 us 368", 1964, "in part"),
    ("Paoli v. United States", "352 us 232", "Bruton v. United States", "391 us 123", 1968, "express"),
    ("Parratt v. Taylor", "451 us 527", "Daniels v. Williams", "474 us 327", 1986, "in part"),
    ("Amalgamated Food Employees v. Logan Valley Plaza", "391 us 308", "Hudgens v. NLRB", "424 us 507", 1976, "express"),
    ("Ledbetter v. Goodyear (statute)", "550 us 618", "Lilly Ledbetter Fair Pay Act", "-", 2009, "superseded by statute"),
]


_IDX = None


def graph_cite(cite):
    """graph/cite_index.tsv lookup (the sqlite copy can be older than the index)."""
    global _IDX
    if _IDX is None:
        want = {k[1] for k in KNOWN} | {k[3] for k in KNOWN}
        _IDX = {}
        with open(os.path.join(C.WORK, "graph", "cite_index.tsv"), encoding="utf-8") as f:
            for line in f:
                c, _, n = line.rstrip("\n").partition("\t")
                if c in want:
                    _IDX[c] = int(n)
    return [_IDX[cite]] if cite in _IDX else []


def status_rows(out_dir):
    """(node, issue, from, to, status, actor) from either layout, status normalised to the Lean names."""
    path = os.path.join(out_dir, "status.tsv")
    with open(path, encoding="utf-8") as f:
        first = f.readline().rstrip("\n").split("\t")
        lean = not first[0].isdigit()
        rows = [] if lean else [first]
        for line in f:
            rows.append(line.rstrip("\n").split("\t"))
    for r in rows:
        if lean:
            yield int(r[0]), r[1], int(r[3]), int(r[4]), r[5], r[9]
        else:
            st, kind = r[5], r[6]
            if st == "negative" and not kind.endswith(":partial"):
                st = "neg:" + kind
            elif st == "negative" or st.startswith("unknown"):
                st = "unknown:partialScope"
            yield int(r[0]), r[1], int(r[3]), int(r[4]), st, r[7]


def finding_rows(out_dir):
    """(kind, citing, cited, firm) from either layout."""
    path = os.path.join(out_dir, "findings.tsv")
    with open(path, encoding="utf-8") as f:
        first = f.readline().rstrip("\n").split("\t")
        lean = first[0] == "finding"
        rows = [] if lean else [first]
        for line in f:
            rows.append(line.rstrip("\n").split("\t"))
    for r in rows:
        if lean:
            yield r[0], r[1], r[2], r[5]
        else:
            yield r[0], r[1], r[2], r[4] if len(r) > 4 else "1"


def resolve(cite):
    if cite == "-":
        return None
    ns = C.node_of_cite(cite) or graph_cite(cite)
    if not ns:
        return None
    m = C.nodes(ns)
    # prefer the SCOTUS node (court 2906 in courts2; v1 court ids vary), else the first
    for n in ns:
        if "Supreme Court of the United States" in (m.get(n, {}).get("court_name") or ""):
            return n
    return ns[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=C.OUT)
    ap.add_argument("--write", default=os.path.join(C.HUNT, "data", "known_overrulings.tsv"))
    args = ap.parse_args()
    rows = []
    res = []
    for k in KNOWN:
        t, b = resolve(k[1]), resolve(k[3])
        res.append((k, t, b))
    tnodes = {t for _, t, _ in res if t}
    st = defaultdict(list)
    for n, issue, frm, to, status_, actor in status_rows(args.out):
        if n in tnodes and issue == "-":
            st[n].append((frm, to, status_, actor))
    # post-overruling citers per target
    cites = defaultdict(set)
    for a, b in C.iter_edges(want_cited=tnodes):
        cites[b].add(a)
    allc = set().union(*cites.values()) if cites else set()
    meta = C.nodes(allc | tnodes | {b for _, _, b in res if b})
    finds = defaultdict(set)
    risk = defaultdict(set)
    for kind, citing, cited, firm in finding_rows(args.out):
        if kind in ("citesOverruled", "atRisk") and firm == "1" and cited.isdigit() and int(cited) in tnodes:
            if citing.isdigit():
                finds[int(cited)].add(int(citing))
            if kind == "atRisk":
                risk[int(cited)].add(citing)
    for k, t, b in res:
        if not t:
            rows.append([k[0], k[1], k[2], k[4], k[5], "-", "-", "unresolved", "-", 0, 0, 0])
            continue
        bdate = meta[b]["date"] if b and b in meta else k[4] * 10000 + 101
        sts = st.get(t, [])
        neg = sorted(x for x in sts if x[2].startswith("neg:"))
        part = sorted(x for x in sts if x[2].startswith("unknown"))
        if neg and b and neg[0][0] > next_day(bdate):
            status = "negLate:" + neg[0][2][4:] + "@" + str(neg[0][0]) + " by " + x_by(neg[0][3], b)
        elif neg:
            status = neg[0][2] + "@" + str(neg[0][0]) + " by " + x_by(neg[0][3], b)
        elif part:
            status = "partialScope@" + str(part[0][0])
        elif risk.get(t):
            status = "atRiskOnly"
        else:
            status = "good"
        after = [c for c in cites.get(t, ()) if c in meta and meta[c]["date"] > bdate]
        flagged = len(finds.get(t, set()) & set(after))
        rows.append([k[0], k[1], k[2], k[4], k[5], t, b if b else "-", status, bdate, len(cites.get(t, ())),
                     len(after), flagged])
    C.write_tsv(args.write, rows,
                ["target", "target_cite", "overruler", "year", "note", "target_node", "overruler_node", "our_status",
                 "overruler_date", "citers_all", "citers_after", "flagged_citesOverruled"])
    for r in rows:
        print("\t".join(str(x) for x in r))


def next_day(d):
    import datetime
    try:
        x = datetime.date(d // 10000, d // 100 % 100, d % 100) + datetime.timedelta(days=1)
        return x.year * 10000 + x.month * 100 + x.day
    except ValueError:
        return d + 1


def x_by(actor, b):
    return "overruler" if b and actor == str(b) else ("other:" + actor)


if __name__ == "__main__":
    main()
