"""Build the external gold sets of caselaw-lean-2 (SCDB, CRS table of overruled decisions, congressional overrides).

    python tools/caselaw2/eval/gold_build.py scdb|crs|overrides|all

Inputs: caselaw-lean-2/gold/src/{scdb,crs}/ (downloaded files), ~/Documents/us-caselaw-lean-work/{graph,crs,uses}.
Outputs: caselaw-lean-2/gold/{scdb,crs_overruled,congress_overrides}.tsv (header line, LF).
"""
import csv, os, re, sys, unicodedata

W = os.path.expanduser("~/Documents/us-caselaw-lean-work")
G = os.path.join(W, "caselaw-lean-2", "gold")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "caselaw"))
from graph import norm_cite  # noqa: E402

_idx = None
_sc = None


def cite_index():
    global _idx
    if _idx is None:
        _idx = {}
        for line in open(os.path.join(W, "graph", "cite_index.tsv"), encoding="utf-8"):
            k, v = line.rstrip("\n").split("\t")
            _idx[k] = int(v)
    return _idx


def scotus():
    """SCOTUS nodes: (by SCDB id, by date list of (node, name, cites))."""
    global _sc
    if _sc is None:
        p = os.path.join(G, "work", "scotus_nodes.tsv")
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8", newline="\n") as o:
                for line in open(os.path.join(W, "graph", "nodes.tsv"), encoding="utf-8"):
                    if line.split("\t", 2)[1] == "supreme-court":
                        o.write(line)
        by_scdb, by_date = {}, {}
        for line in open(p, encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            n = int(f[0])
            for c in f[5].split("|"):
                if c.startswith("SCDB "):
                    by_scdb[c[5:]] = n
            by_date.setdefault(int(f[4]), []).append((n, f[6], f[5], f[7] if len(f) > 7 else ""))
        _sc = (by_scdb, by_date)
    return _sc


def node_of_cite(c):
    k = norm_cite(c or "")
    return cite_index().get(k) if k else None


def toks(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return {t for t in re.findall(r"[a-z]{3,}", s)} - {"the", "and", "inc", "corp", "united", "states", "state",
                                                      "co", "of", "for", "commission", "department"}


def node_by_name_date(name, date):
    """A SCOTUS node decided on `date` (yyyymmdd) whose name shares the most tokens with `name`."""
    best, bs = None, 0
    want = toks(name)
    for n, nm, cits, dtype in scotus()[1].get(date, []):
        s = len(want & toks(nm)) + (0.5 if dtype == "opinion" else 0)
        if s > bs:
            best, bs = n, s
    return best if bs >= 1 else None


# ---------------------------------------------------------------- SCDB
CERT = {"1": "noCertOrNotGranted", "2": "federalCourtConflict", "3": "federalCourtConflictAndImportantQuestion",
        "4": "putativeConflict", "5": "federalStateConflict", "6": "stateCourtConflict",
        "7": "federalCourtConfusion", "8": "stateCourtConfusion", "9": "federalStateConfusion",
        "10": "importantQuestion", "11": "resolveQuestionPresented", "12": "noReasonGiven", "13": "other"}
LAWTYPE = {"1": "constitution", "2": "constitutionalAmendment", "3": "federalStatute", "4": "courtRules",
           "5": "other", "6": "infrequentlyLitigatedStatute", "8": "stateOrLocalLaw", "9": "noLegalProvision"}
AUTH = {"1": "judicialReviewNational", "2": "judicialReviewState", "3": "supervisionOrOriginal",
        "4": "statutoryConstruction", "5": "regulationOrRuleOrEO", "6": "diversity", "7": "federalCommonLaw"}
DTYPE = {"1": "signedOpinion", "2": "summaryNoOralArg", "4": "judgmentOfCourt", "5": "equallyDivided",
         "6": "perCuriamOralArg", "7": "decreeOrOrder", "8": "seriatim"}


def basis(lt, a1, a2):
    if lt in ("1", "2") or "1" in (a1, a2) or "2" in (a1, a2):
        return "constitutional"
    if lt in ("3", "6") or "4" in (a1, a2):
        return "statutory"
    if lt == "4" or "5" in (a1, a2):
        return "ruleOrRegulation"
    if "6" in (a1, a2) or "7" in (a1, a2):
        return "commonLaw"
    if lt == "8":
        return "stateLaw"
    return "unknown"


def ymd(d):
    m = re.match(r"(\d+)/(\d+)/(\d{4})", d or "")
    return int(m.group(3)) * 10000 + int(m.group(1)) * 100 + int(m.group(2)) if m else 0


def build_scdb():
    src = os.path.join(G, "src", "scdb", "x")
    cols = ["node", "how", "caseId", "usCite", "date", "term", "caseName", "decisionType", "precedentAlteration",
            "declarationUncon", "certReason", "certReasonLabel", "lcDisposition", "caseDisposition", "lawType",
            "lawTypeLabel", "lawSupp", "lawMinor", "authorityDecision1", "authorityDecision2", "basis",
            "majVotes", "minVotes", "release"]
    n = hit = alt = althit = 0
    with open(os.path.join(G, "scdb.tsv"), "w", encoding="utf-8", newline="\n") as out:
        out.write("\t".join(cols) + "\n")
        for fn, rel in (("SCDB_Legacy_07_caseCentered_Citation.csv", "Legacy_07"),
                        ("SCDB_2026_01_caseCentered_Citation.csv", "2026_01")):
            for r in csv.DictReader(open(os.path.join(src, fn), encoding="latin-1")):
                node, how = scotus()[0].get(r["caseId"]), "scdbId"
                if node is None:
                    for c in ("usCite", "sctCite", "ledCite"):
                        node = node_of_cite(r[c])
                        if node is not None:
                            how = c
                            break
                if node is None:
                    node, how = node_by_name_date(r["caseName"].title(), ymd(r["dateDecision"])), "nameDate"
                if node is None:
                    how = "-"
                n += 1
                hit += node is not None
                alt += r["precedentAlteration"] == "1"
                althit += r["precedentAlteration"] == "1" and node is not None
                lt, a1, a2 = r["lawType"], r["authorityDecision1"], r["authorityDecision2"]
                row = [node if node is not None else -1, how, r["caseId"], r["usCite"], ymd(r["dateDecision"]), r["term"],
                       r["caseName"], DTYPE.get(r["decisionType"], r["decisionType"]), r["precedentAlteration"],
                       r["declarationUncon"], r["certReason"], CERT.get(r["certReason"], "-"), r["lcDisposition"],
                       r["caseDisposition"], lt, LAWTYPE.get(lt, "-"), r["lawSupp"], r["lawMinor"], AUTH.get(a1, a1),
                       AUTH.get(a2, a2), basis(lt, a1, a2), r["majVotes"], r["minVotes"], rel]
                out.write("\t".join(str(x).replace("\t", " ") for x in row) + "\n")
    print(f"scdb rows {n}, mapped {hit}; precedentAlteration=1 {alt}, mapped {althit}")


# ---------------------------------------------------------------- CRS
def parse_conan(pdf, pages=None):
    """Rows (overruling text, overruled text) of the CONAN table 'Supreme Court decisions overruled by subsequent
    decision', aligned by the y position where each entry's year is printed."""
    import pymupdf
    d = pymupdf.open(pdf)
    rows, cur = [], None
    for i in range(len(d)):
        ws = d[i].get_text("words")
        hdr = [w for w in ws if w[4] in ("Year", "Year(s)") and w[1] < 200]
        if len(hdr) < 2 or not any(w[4] == "Overruled" for w in ws):
            if rows:
                break
            continue
        y1 = min(w[0] for w in hdr if w[4] == "Year")
        y2 = min(w[0] for w in hdr if w[4] == "Year(s)")
        top = max(w[3] for w in ws if w[4].startswith("Decision")) + 2
        b1, b2, b3 = y1 - 5, y1 + 40, y2 - 5
        body = [w for w in ws if w[1] > top and not re.fullmatch(r"\d{3,4}", w[4]) or (w[1] > top and w[0] < b1)]
        body = [w for w in ws if w[1] > top]
        starts1 = sorted({round(w[1]) for w in body if b1 <= w[0] < b2 and re.fullmatch(r"\d{4}", w[4])})
        starts3 = sorted({round(w[1]) for w in body if w[0] >= b3 and re.fullmatch(r"\d{4}", w[4])})

        def text(lo, hi, x0, x1):
            sel = [w for w in body if lo - 1 <= w[1] < hi - 1 and x0 <= w[0] < x1]
            sel.sort(key=lambda w: (round(w[1]), w[0]))
            return " ".join(w[4] for w in sel)
        big = 10 ** 6
        # overruling entries
        ents1 = [(s, text(s, starts1[j + 1] if j + 1 < len(starts1) else big, 0, b1)) for j, s in enumerate(starts1)]
        ents3 = [(s, text(s, starts3[j + 1] if j + 1 < len(starts3) else big, b2, b3)) for j, s in enumerate(starts3)]
        # text in column 3 above the first year on the page continues the previous page's last entry
        if starts3 and cur is not None:
            pre = text(0, starts3[0], b2, b3).strip()
            if pre and rows:
                rows[-1] = (rows[-1][0], rows[-1][1] + " " + pre)
        for s, t3 in ents3:
            owner = [t for s1, t in ents1 if s1 <= s + 1]
            if owner:
                cur = owner[-1]
            if cur is not None:
                rows.append((cur, t3))
        if not starts3 and ents1:
            cur = ents1[-1][1]
    return rows


US = re.compile(r"(\d{1,3})\s+U\.\s?S\.\s+(?:\([^)]*\)\s+)?(\d{1,4})")
NO = re.compile(r"No\.\s+([\w-]+)\s+\(U\.S\.\s+([A-Z][a-z]+)\.?\s+(\d{1,2}),\s+(\d{4})\)")
MON = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May June July Aug Sept Oct Nov Dec".split())}
MON.update({"Sep": 9, "Jun": 6, "Jul": 7})


def resolve_entry(t):
    m = US.search(t)
    name = re.split(r",\s*(?:No\.|\d{1,3}\s+U\.)", t)[0].strip()
    if m:
        cite = f"{m.group(1)} U.S. {m.group(2)}"
        return name, cite, node_of_cite(cite)
    m = NO.search(t)
    if m:
        date = int(m.group(4)) * 10000 + MON.get(m.group(2), 0) * 100 + int(m.group(3))
        return name, f"No. {m.group(1)} ({date})", node_by_name_date(name, date)
    return name, "-", None


def qualifier(t):
    q = re.findall(r"\((in part|plurality opinion|per curiam|[A-Z][a-z]+, J+\., concurring[^)]*|"
                   r"[^)]*(?:concurring|dissenting|opinion)[^)]*)\)", t)
    return "; ".join(q) if q else "-"


def build_crs():
    src = os.path.join(G, "src", "crs")
    old = list(csv.DictReader(open(os.path.join(W, "crs", "crs2016.tsv"), encoding="utf-8"), delimiter="\t"))
    pairs = {}
    for r in old:
        y, x = node_of_cite(r["overruling_cite"]), node_of_cite(r["overruled_cite"])
        key = (r["overruling_cite"], r["overruled_cite"])
        pairs[key] = dict(by=y, target=x, by_name=r["overruling_name"], by_cite=r["overruling_cite"],
                          name=r["overruled_name"], cite=r["overruled_cite"], qual="-", e2016="1",
                          expressly=r["expressly"], cur="0")
    cur_rows = []
    for pdf in ("conan2022_appendix.pdf", "conan2026supp.pdf"):
        for a, b in parse_conan(os.path.join(src, pdf)):
            for b1 in re.split(r";\s+(?=[A-Z][^;]{3,200}?\d{1,3}\s+U\.\s?S\.)", b):
                if (pdf, a, b1) not in cur_rows:
                    cur_rows.append((pdf, a, b1))
    seen_cur = 0
    for pdf, a, b in cur_rows:
        bn, bc, y = resolve_entry(a)
        xn, xc, x = resolve_entry(b)
        if xc == "-":
            continue
        key = (bc, xc)
        if y is not None and x is not None:
            hit = [k for k, v in pairs.items() if v["by"] == y and v["target"] == x]
            if hit:
                key = hit[0]
        if key in pairs:
            pairs[key]["cur"] = "1"
            if y is not None:
                pairs[key]["by"] = y
            pairs[key]["qual"] = qualifier(b)
            continue
        # a 2016 row whose overruling cite was then a slip-opinion number
        alt = [k for k, v in pairs.items() if (k[1] == xc or (x is not None and v["target"] == x)) and
               ((v["by"] == y and y is not None) or (v["by"] is None and len(toks(v["by_name"]) & toks(bn)) >= 1))]
        if alt:
            pairs[alt[0]]["cur"] = "1"
            if pairs[alt[0]]["by"] is None:
                pairs[alt[0]]["by"] = y
            if pairs[alt[0]]["target"] is None:
                pairs[alt[0]]["target"] = x
            pairs[alt[0]]["qual"] = qualifier(b)
            continue
        seen_cur += 1
        pairs[key] = dict(by=y, target=x, by_name=bn, by_cite=bc, name=xn, cite=xc, qual=qualifier(b), e2016="0",
                          expressly="-", cur="1", src=pdf)
    cols = ["by_node", "target_node", "by_name", "by_cite", "target_name", "target_cite", "qualifier", "in_2016",
            "expressly_2016", "in_current", "src"]
    nres = 0
    with open(os.path.join(G, "crs_overruled.tsv"), "w", encoding="utf-8", newline="\n") as out:
        out.write("\t".join(cols) + "\n")
        for v in pairs.values():
            nres += v["by"] is not None and v["target"] is not None
            s = v.get("src", "crs2016.tsv" + ("+current" if v["cur"] == "1" else ""))
            row = [v["by"] if v["by"] is not None else -1, v["target"] if v["target"] is not None else -1,
                   v["by_name"], v["by_cite"], v["name"], v["cite"], v["qual"], v["e2016"], v["expressly"], v["cur"], s]
            out.write("\t".join(str(c).replace("\t", " ") for c in row) + "\n")
    print(f"crs pairs {len(pairs)} (2016: {len(old)}, current table rows {len(cur_rows)}, new {seen_cur}), "
          f"both resolved {nres}")


# ---------------------------------------------------------------- overrides
def build_overrides():
    src = os.path.join(W, "uses", "overrides", "gold")
    rows = list(csv.DictReader(open(os.path.join(src, "gold.tsv"), encoding="utf-8"), delimiter="\t"))
    rows += list(csv.DictReader(open(os.path.join(src, "gold_post2011.tsv"), encoding="utf-8"), delimiter="\t"))
    cols = list(rows[0].keys()) if rows else []
    hit = 0
    with open(os.path.join(G, "congress_overrides.tsv"), "w", encoding="utf-8", newline="\n") as out:
        out.write("\t".join(["node"] + cols) + "\n")
        for r in rows:
            n = node_of_cite(r["us_cite"])
            hit += n is not None
            out.write("\t".join([str(n if n is not None else -1)] + [r[c].replace("\t", " ") for c in cols]) + "\n")
    print(f"overrides {len(rows)}, mapped {hit}")


if __name__ == "__main__":
    what = sys.argv[1]
    if what in ("scdb", "all"):
        build_scdb()
    if what in ("crs", "all"):
        build_crs()
    if what in ("overrides", "all"):
        build_overrides()
