"""Build decisions2.tsv from graph/nodes.tsv, the court table (courts2_build.py) and the scan outputs (scan.py).

    python decisions_build.py stage2      per repo: court epoch, direct unit cues, bench, publication, form
                                          -> work/courts/dec/<repo>.tsv (+ <repo>.tok for judge bootstrapping)
    python decisions_build.py stage3      judge-panel bootstrap for the units left open; concatenate in node order
                                          -> data/decisions2.tsv, data/commission.tsv, work/courts/unit_holdout.tsv

decisions2.tsv: node, court_id, date, unit, bench, publication, form, text_sha, src
src = `c:<court route>;u:<unit source>;b:<bench evidence code>;p:<publication evidence code>;f:<form evidence code>`.
"""
import array, collections, json, os, re, sys

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
L2 = os.path.join(WORK, "caselaw-lean-2")
WD = os.path.join(L2, "work", "courts")
DATA = os.path.join(L2, "data")

# ------------------------------------------------------------------------------------------------ county tables
NY_DEPT = {}
for d, cs in ((1, "New York|Bronx"),
              (2, "Kings|Richmond|Queens|Nassau|Suffolk|Westchester|Rockland|Orange|Putnam|Dutchess"),
              (3, "Albany|Columbia|Greene|Rensselaer|Schoharie|Sullivan|Ulster|Clinton|Essex|Franklin|Fulton|Hamilton|"
                  "Montgomery|St. Lawrence|Saratoga|Schenectady|Warren|Washington|Broome|Chemung|Chenango|Cortland|"
                  "Delaware|Madison|Otsego|Schuyler|Tioga|Tompkins"),
              (4, "Herkimer|Jefferson|Lewis|Oneida|Onondaga|Oswego|Cayuga|Livingston|Monroe|Ontario|Seneca|Steuben|"
                  "Wayne|Yates|Allegany|Cattaraugus|Chautauqua|Erie|Genesee|Niagara|Orleans|Wyoming")):
    for c in cs.split("|"):
        NY_DEPT[c] = d
OH_DIST = {}
for d, cs in ((1, "Hamilton"), (2, "Montgomery|Greene|Clark|Champaign|Darke|Miami"),
              (3, "Allen|Auglaize|Crawford|Defiance|Hancock|Hardin|Henry|Logan|Marion|Mercer|Paulding|Putnam|Seneca|"
                  "Shelby|Union|Van Wert|Wyandot"),
              (4, "Adams|Athens|Gallia|Highland|Hocking|Jackson|Lawrence|Meigs|Pickaway|Pike|Ross|Scioto|Vinton|"
                  "Washington"),
              (5, "Ashland|Coshocton|Delaware|Fairfield|Guernsey|Holmes|Knox|Licking|Morgan|Morrow|Muskingum|Perry|"
                  "Richland|Stark|Tuscarawas"),
              (6, "Erie|Fulton|Huron|Lucas|Ottawa|Sandusky|Williams|Wood"),
              (7, "Belmont|Carroll|Columbiana|Harrison|Jefferson|Mahoning|Monroe|Noble"), (8, "Cuyahoga"),
              (9, "Lorain|Medina|Summit|Wayne"), (10, "Franklin"), (11, "Ashtabula|Geauga|Lake|Portage|Trumbull"),
              (12, "Brown|Butler|Clermont|Clinton|Fayette|Madison|Preble|Warren")):
    for c in cs.split("|"):
        OH_DIST[c] = d
OH_CORE = {"Hamilton": 1, "Montgomery": 2, "Lucas": 6, "Cuyahoga": 8, "Summit": 9, "Franklin": 10}
LA_CIRC = {}
for d, cs in ((1, "Ascension|Assumption|East Baton Rouge|East Feliciana|Iberville|Lafourche|Livingston|Pointe Coupee|"
                  "St. Helena|St. Mary|St. Tammany|Tangipahoa|Terrebonne|Washington|West Baton Rouge|West Feliciana"),
              (2, "Bienville|Bossier|Caddo|Caldwell|Claiborne|De Soto|DeSoto|East Carroll|Franklin|Jackson|Lincoln|"
                  "Madison|Morehouse|Ouachita|Red River|Richland|Tensas|Union|Webster|West Carroll|Winn"),
              (3, "Acadia|Allen|Avoyelles|Beauregard|Calcasieu|Cameron|Catahoula|Concordia|Evangeline|Grant|Iberia|"
                  "Jefferson Davis|Lafayette|La Salle|LaSalle|Natchitoches|Rapides|Sabine|St. Landry|St. Martin|"
                  "Vermilion|Vernon"),
              (4, "Orleans|Plaquemines|St. Bernard"), (5, "Jefferson|St. Charles|St. James|St. John")):
    for c in cs.split("|"):
        LA_CIRC[c] = d
WA_DIV = {}
for d, cs in ((1, "King|Snohomish|Skagit|Whatcom|Island|San Juan"),
              (2, "Pierce|Clark|Kitsap|Thurston|Cowlitz|Lewis|Grays Harbor|Mason|Clallam|Jefferson|Pacific|Wahkiakum|"
                  "Skamania"),
              (3, "Spokane|Yakima|Benton|Franklin|Chelan|Grant|Walla Walla|Okanogan|Stevens|Kittitas|Whitman|Douglas|"
                  "Asotin|Adams|Klickitat|Lincoln|Pend Oreille|Ferry|Columbia|Garfield")):
    for c in cs.split("|"):
        WA_DIV[c] = d
CA_DIST = [("Los Angeles", 2, 0), ("San Francisco", 1, 0), ("Alameda", 1, 0), ("Sacramento", 3, 0),
           ("San Diego", 4, 19290101), ("Orange", 4, 19290101), ("Riverside", 4, 19290101),
           ("San Bernardino", 4, 19290101), ("Fresno", 5, 19610101), ("Kern", 5, 19610101), ("Tulare", 5, 19610101),
           ("Stanislaus", 5, 19610101), ("Santa Clara", 6, 19840101), ("Monterey", 6, 19840101),
           ("Santa Cruz", 6, 19840101)]
CA_DIST = {c: (d, f) for c, d, f in CA_DIST}
ORDW = {w: i + 1 for i, w in enumerate("First Second Third Fourth Fifth Sixth Seventh Eighth Ninth Tenth Eleventh "
                                         "Twelfth Thirteenth Fourteenth Fifteenth".split())}
ORDW.update({"1st": 1, "2nd": 2, "2d": 2, "3rd": 3, "3d": 3, "4th": 4, "5th": 5, "6th": 6, "7th": 7, "8th": 8,
             "9th": 9, "10th": 10, "11th": 11, "12th": 12, "13th": 13, "14th": 14, "15th": 15})
CA_LETTER = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 4, "G": 4, "F": 5, "H": 6}
PH_KIND = {"FL-DCA": ("District", "Dist."), "CA-COA": ("Appellate District", "District", "Dist."),
           "NY-AD": ("Department", "Dept."), "NY-AT": ("Department", "Dept."), "LA-COA": ("Circuit",),
           "IL-APP": ("District", "Dist."), "OH-COA": ("District", "Appellate District", "Dist."),
           "IN-COA": ("District",), "TX-COA": ("Court of Appeals", "Supreme Judicial District", "Court of Civil Appeals")}
MAXU = {"FL-DCA": 6, "TX-COA": 15, "CA-COA": 6, "NY-AD": 4, "NY-AT": 2, "LA-COA": 5, "OH-COA": 12, "IL-APP": 5,
        "MO-COA": 3, "WA-COA": 3, "AZ-COA": 2, "IN-COA": 5, "OK-COCA": 4, "TN-COA": 3, "TN-CCA": 3, "CA5": 2}


def parse_codes(s):
    out = {}
    if s == "-":
        return out
    for part in s.split("|"):
        k, _, v = part.partition("=")
        out.setdefault(k, v)
    return out


def docket_unit(fam, d, date):
    if not d:
        return 0
    if fam == "FL-DCA":
        m = re.match(r"\s*(?:Nos?\.?\s*|Case Nos?\.?\s*)?([1-6])D\d", d, re.I)
        return int(m.group(1)) if m else 0
    if fam == "TX-COA":
        m = re.match(r"\s*(?:NOS?\.?|NUMBERS?|Nos?\.?)?\s*[A-C]?(\d{1,2})\s*[-–—]\s*\d{2}\s*[-–—]\s*\d{3,5}"
                     r"\s*[-–—]?\s*(?:CR|CV)", d, re.I)
        if m and 1 <= int(m.group(1)) <= 15:
            return int(m.group(1))
        return 0
    if fam == "CA-COA" and date >= 19800101:
        m = re.match(r"\s*(?:Nos?\.?\s*)?([A-H])0\d{5}\b", d)
        return CA_LETTER.get(m.group(1), 0) if m else 0
    if fam == "IL-APP" and date >= 19650101:
        m = re.match(r"\s*(?:Nos?\.?\s*)?([1-5])\s*[-–—]\s*\d{2}\s*[-–—]\s*\d{3,5}", d)
        return int(m.group(1)) if m else 0
    if fam == "IN-COA":
        m = re.match(r"\s*(?:Nos?\.?\s*)?([1-5])\s*-\s*\d{3,4}\s*A\s*\d", d) or \
            re.search(r"\b\d{2}A0([1-5])\s*-", d)
        return int(m.group(1)) if m else 0
    if fam == "MO-COA":
        m = re.search(r"\b(ED|WD|SD)\s*-?\s*\d", d)
        return {"ED": 1, "WD": 2, "SD": 3}[m.group(1)] if m else 0
    if fam == "WA-COA":
        m = re.search(r"\d\s*-\s*(I{1,3})\b", d)
        return len(m.group(1)) if m else 0
    if fam == "AZ-COA":
        m = re.search(r"\b([12])\s*CA[-\s]", d)
        return int(m.group(1)) if m else 0
    if fam == "LA-COA":
        if re.search(r"\b\d{2},\d{3}-[A-Z]{2}\b", d):
            return 2
        if re.search(r"\b(?:19|20)\d{2}\s+[CK][AWJ]\s+\d{3,4}\b", d):
            return 1
        if re.search(r"\b(?:19|20)\d{2}-[CK][AWJ]-\d{3,4}\b", d):
            return 4
        if re.search(r"\b\d{2}-[CK][AWJ]-\d{1,4}\b", d) and date >= 19820101:
            return 5
        return 0
    return 0


def county_unit(fam, counties, date):
    if not counties:
        return 0, ""
    first = counties.split(";")[0]
    nm, _, kind = first.rpartition(" ")
    if fam in ("NY-AD", "NY-AT") and kind == "County":
        d = NY_DEPT.get(nm, 0)
        if fam == "NY-AT" and d > 2:
            d = 0
        return d, first
    if fam == "OH-COA" and kind == "County":
        if nm in OH_CORE:
            return OH_CORE[nm], first
        if date >= 19760101:
            return OH_DIST.get(nm, 0), first
    if fam == "LA-COA" and kind == "Parish" and date >= 19600701:
        d = LA_CIRC.get(nm, 0)
        if d == 5 and date < 19820101:
            d = 4
        return d, first
    if fam == "WA-COA" and kind == "County":
        return WA_DIV.get(nm, 0), first
    if fam == "CA-COA" and kind == "County" and nm in CA_DIST:
        d, f = CA_DIST[nm]
        if date >= f:
            return d, first
    if fam == "IL-APP" and kind == "County" and nm == "Cook":
        return 1, first
    return 0, ""


def phrase_unit(fam, unit_codes):
    kinds = PH_KIND.get(fam)
    if not kinds:
        return 0
    for c in unit_codes:
        if not c.startswith("ph="):
            continue
        v = c[3:]
        m = re.match(r"(\S+) (.+?)@(\d+)(s?)(c?)$", v)
        if not m:
            continue
        w, kind, pos, short, cite = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
        if cite or not short or pos > 1500 or kind not in kinds:
            continue
        u = ORDW.get(w, 0)
        if 0 < u <= MAXU[fam]:
            return u
    return 0


# ------------------------------------------------------------------------------------------------ classification
def classify_bench(b, court, tier, system, circuit, date, fam, name_div):
    if court == SCOTUS:
        return "wholeCourt", "default-scotus"
    if "eb_prose" in b and LOWER_BODY.search(b["eb_prose"]):
        del b["eb_prose"]
    if "circ" in b and re.search(r"petition|suggestion|rehearing", b["circ"], re.I):
        del b["circ"]
    if "whole" in b and (re.search(r"\bnot\b", b["whole"], re.I) or not WHOLE_SELF.search(b["whole"])):
        del b["whole"]
    if "eb_line" in b and (EB_BAD.search(b["eb_line"]) or not EB_LINE_OK.search(b["eb_line"].strip())):
        del b["eb_line"]
    if "eb_prose" in b and (EB_BAD.search(b["eb_prose"]) or not EB_PROSE_OK.search(b["eb_prose"])):
        del b["eb_prose"]
    if "eb_fm" in b or "eb_line" in b or "eb_prose" in b:
        k = "eb_fm" if "eb_fm" in b else ("eb_line" if "eb_line" in b else "eb_prose")
        if fam == "CA9" and date >= 19800101:
            return "limitedEnBanc", k + "+ca9-limited"
        return "enBanc", k
    nb = int(b.get("nbefore", "0") or 0)
    if system == 0 and tier == "A" and circuit > 0 and court != CCPA and nb >= 7:
        return ("limitedEnBanc" if fam == "CA9" and date >= 19800101 else "enBanc"), "nbefore=%d" % nb
    if "conflict" in b and system == 22 and tier == "A":
        return "conflictPanel", "conflict"
    if "circ" in b and tier == "A":
        return "circulated", "circ"
    if "div" in b or name_div:
        return "division", "div" if "div" in b else "name-division"
    if "whole" in b:
        return "wholeCourt", "whole"
    if court == CCPA:
        return "wholeCourt", "default-ccpa"
    if tier in ("A", "B", "D"):
        return "panel", "default-tier%s" % tier
    return "unknown", "-"


EB_BAD = re.compile(r"[Dd]enial|[Dd]enied|[Dd]enying|[Gg]ranted|[Gg]ranting|\b[Oo]rder\b|ORDER|[Aa]mended|D\.C\. No|banc\)|"
                    r"BANC of|be reheard|is ordered|Industrial|Compensation|[Oo]rphans|exceptions|jury|new trial|"
                    r"\bv\.|\d{4}\)")
EB_LINE_OK = re.compile(r"(?:(?:Re-?)?[Aa]rgued|ARGUED|Submitted|SUBMITTED|Heard|HEARD|Reheard|Considered)\b[^.]{0,30}\b(?:en|in|En|In|EN|IN) "
                        r"(?:banc|Banc|BANC)|^(?:ON )?(?:REHEARING )?(?:EN|IN) BANC\.?$|^(?:On )?Rehearing (?:[Ee]n|[Ii]n) [Bb]anc\.?$|"
                        r"^(?:[Ee]n|[Ii]n) [Bb]anc\.?$|sitting (?:en|in) banc|[Bb]efore the (?:full )?[Cc]ourt,? (?:[Ee]n|[Ii]n) [Bb]anc|"
                        r"(?:Court|COURT)[^.]{0,40},? (?:[Ee]n|[Ii]n|EN|IN) (?:[Bb]anc|BANC)\.?$")
EB_PROSE_OK = re.compile(r"On rehearing en banc|we took this (?:case|appeal) en banc|(?:This|this|The|the) (?:case|matter|cause|appeal|"
                         r"petition)[^.]{0,40}(?:heard|argued|reargued|considered|comes?|came|is|was|be) (?:\w+ ){0,3}(?:before )?"
                         r"(?:the )?(?:court )?(?:en|in) banc|sitting (?:en|in) banc|we (?:granted|ordered) rehearing en banc|"
                         r"[Bb]efore (?:the )?court (?:en|in) banc")
WHOLE_SELF = re.compile(r"(?:this|the) (?:case|cause|appeal|matter)[^.]{0,40}(?:heard|considered|submitted|argued|"
                        r"decided|reargued) (?:by|before|to) the (?:whole|full) court|(?:whole|full) [Cc]ourt (?:concur|"
                        r"sitting)|^\s*(?:Whole|Full|WHOLE|FULL) (?:Court|COURT)", re.I)
LOWER_BODY = re.compile(r"Industrial|Compensation|Common Pleas|[Cc]ounty|[Cc]ommission|[Bb]oard|below|trial court|"
                        r"[Oo]rphans|[Tt]ax [Cc]ourt|[Ss]uperior [Cc]ourt|[Dd]istrict [Cc]ourt|tribunal")
REPORTER_OK = re.compile(r"\b(?:U\.S\.|F\.(?:2d|3d|4th)?|F\. ?Supp|B\.R\.|T\.C\.|S\. ?Ct\.|[A-Z][A-Za-z.]*\s?(?:2d|3d|4th|5th)?)"
                         r"\s")


def classify_pub(p, fm_status, cites, court, tier, system, date, fam, op_len, form_pc):
    ev = ""
    unpub = None
    for k in ("unpub_caps_h", "unpub_sent_h", "unpub_caps_t", "unpub_sent_t"):
        if k in p:
            unpub = (k, p[k])
            break
    if unpub and re.search(r"PARTIAL PUBLICATION|[Pp]artial [Pp]ublication", unpub[1]):
        return "published", "partial-publication"
    if "sumord" in p:
        return "summaryOrder", "sumord"
    if unpub:
        return "unpublished", unpub[0]
    if fm_status == "nonprecedential":
        return "unpublished", "fm:nonprecedential"
    if "fappx" in p and system == 0:
        return "unpublished", "reporter:F.App'x"
    if "citetable" in p or ("table" in p and op_len < 1500):
        return "table", "table"
    if fam == "FL-DCA" and form_pc and op_len < 300:
        return "table", "fl-pca-without-opinion"
    if "memo" in p and "SUMMARY DISPOSITION" in p["memo"] and system != 0:
        return "unpublished", "summary-disposition-order"
    if "memo" in p and ((system != 0 and tier in ("A", "L", "D")) or court == TAX):
        return "memorandum", "memo"
    if fm_status in ("published", "precedential"):
        return "published", "fm:" + fm_status
    if "pubpos" in p:
        return "published", "banner"
    if cites and court != SCOTUS and re.search(r"\b(?:F\.(?:2d|3d|4th)|F\. ?Supp|B\.R\.|T\.C\.)\s", cites + " "):
        return "published", "reporter"
    if court == SCOTUS and re.search(r"\bU\.S\.", cites):
        return "published", "reporter:U.S."
    return "unknown", "-"


def classify_form(f, dtype, court, tier, system, op_len, secs, pub):
    eq = f.get("eqdiv_h") or f.get("eqdiv_t")
    if eq and re.search(r"affirm", eq, re.I) and not re.search(r"below|lower court|court of appeals|appellate division"
                                                                 r"|on rehearing", eq, re.I):
        return "equallyDivided", "eqdiv"
    if "certq_fed" in f and tier == "L" and system > 0 and not re.search(r"accept", f["certq_fed"], re.I):
        return "certifiedAnswer", "certq_fed"
    pt = f.get("plur_txt", "")
    if pt and re.search(r"Parts?\b|opinion of the Court", pt):
        pt = ""
    if pt or ("plur_sec" in f and "P" in f["plur_sec"]):
        return "plurality", "plur_txt" if pt else "plur_sec"
    if court == SCOTUS and "sumaff" in f and dtype not in ("memorandum order", "opinion") and op_len < 600:
        return "summaryAffirmance", "sumaff"
    if "pc" in f or dtype == "per curiam":
        return "perCuriam", "pc" if "pc" in f else "dtype"
    if "memo" in f or dtype == "memorandum order":
        return "memorandum", "memo" if "memo" in f else "dtype"
    if op_len >= 600:
        return "full", "len"
    return "unknown", "-"


SCOTUS = None
CCPA = None
TAX = None


def load_courts():
    ep = collections.defaultdict(list)
    for line in open(os.path.join(DATA, "courts2.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        ep[int(f[0])].append((int(f[1]), int(f[2]), f[3], int(f[4]), f[5], int(f[7]), int(f[8])))
    route = collections.defaultdict(list)
    seen = set()
    for line in open(os.path.join(DATA, "court_alias.tsv"), encoding="utf-8"):
        v1, g, name, a, b, c2, unit, src = line.rstrip("\n").split("\t")
        k = (g, a, b)
        if k in seen:
            continue
        seen.add(k)
        route[g].append((int(a), int(b), int(c2), int(unit), src, name))
    keys = json.load(open(os.path.join(WD, "court_keys.json"), encoding="utf-8"))
    return ep, route, keys


def epoch_of(ep, cid, date):
    rows = ep[cid]
    for r in rows:
        if r[0] <= date <= r[1]:
            return r
    return rows[-1] if date > rows[-1][1] else rows[0]


def stage2(only=None):
    global SCOTUS, CCPA, TAX
    ep, route, keys = load_courts()
    CCPA = keys["cid_of"]["CCPA"]
    TAX = keys["cid_of"]["TAX"]
    fam_of = {v: k for k, v in keys["cid_of"].items() if k in MAXU or k == "CA9"}
    SCOTUS = [c for c, rows in ep.items() if rows[0][2] == "Supreme Court of the United States"][0]
    os.makedirs(os.path.join(WD, "dec"), exist_ok=True)
    unit_from = {}
    for line in open(os.path.join(DATA, "courts2.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        m = re.match(r"unit-of:(\d+)", f[9])
        if m:
            unit_from[(int(m.group(1)), int(f[8]))] = int(f[1])
    # node info per repo
    info = {}
    cur = None
    repos = sorted(os.listdir(os.path.join(WD, "out")))
    want = {r[:-4] for r in repos if r.endswith(".tsv")}
    if only:
        want &= set(only)
    with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[1] not in want:
                continue
            info.setdefault(p[1], {})[p[0]] = (p[3], int(p[4]), p[5], p[7] if len(p) > 7 else "")
    for repo in sorted(info):
        outp = os.path.join(WD, "dec", repo + ".tsv")
        rows = []
        toks = []
        for line in open(os.path.join(WD, "out", repo + ".tsv"), encoding="utf-8"):
            c = line.rstrip("\n").split("\t")
            node, sha, nbytes, oplen, docket, fmst, secs, bench, pub, form, unit, judges, dtype = c
            g, date, cites, dtype2 = info[repo][node]
            dtype = dtype2 or (dtype if dtype != "-" else "")
            oplen = int(oplen)
            # court epoch
            segs = route.get(g)
            if not segs:
                cid, nunit, csrc, cname = 3160, 0, "unmapped", ""
            else:
                seg = next((s for s in segs if s[0] <= date <= s[1]), segs[-1] if date > segs[-1][1] else segs[0])
                cid, nunit, csrc, cname = seg[2], seg[3], seg[4], seg[5]
            e = epoch_of(ep, cid, date)
            tier, system, circuit = e[4], e[3], e[5]
            fam = fam_of.get(cid)
            b, p, fo, u = parse_codes(bench), parse_codes(pub), parse_codes(form), unit.split("|") if unit != "-" else []
            # unit
            usrc, uval = "-", 0
            if fam and fam != "CA9":
                if nunit:
                    uval, usrc = nunit, "name"
                else:
                    du = docket_unit(fam, docket, date)
                    if du:
                        uval, usrc = du, "docket"
                    else:
                        pu = 0  # header phrases dropped: 67% precision in round-1 validation
                        if pu:
                            uval, usrc = pu, "header"
                        else:
                            cu, cname2 = county_unit(fam, next((x[7:] for x in u if x.startswith("county=")), ""), date)
                            if cu:
                                uval, usrc = cu, "county"
                if uval and fam != "MO-COA" and date and date < unit_from.get((cid, uval), 0):
                    uval, usrc = 0, "-"
                if fam == "CA5":
                    uval, usrc = 0, "-"
                    ab = next((x[7:] for x in u if x.startswith("unitab=")), "")
                    if ab and 19801001 <= date <= 19821231:
                        uval, usrc = (1 if ab == "A" else 2), "header-unit" + ab
                elif uval == 0 and judges != "-":
                    usrc = "?"
                    toks.append("%s\t%s\t%d\t%s" % (node, fam, date // 100000, judges))
                if uval and judges != "-" and fam != "CA5":
                    toks.append("%s\t%s\t%d\t%s\t%d" % (node, fam, date // 100000, judges, uval))
            name_div = bool(re.search(r"(?:DIVISION|Division|Div\.) (?:I{1,3}|IV|V|VI|VII|One|Two|Three|Four)$", cname or "")) \
                and system in (4, 6)
            bv, bs = classify_bench(b, cid, tier, system, circuit, date, fam, name_div)
            fv, fs = classify_form(fo, dtype, cid, tier, system, oplen, secs, None)
            pv, ps = classify_pub(p, fmst, cites, cid, tier, system, date, fam, oplen, fv == "perCuriam")
            comm = fo.get("comm", "")
            src = "c:%s;u:%s;b:%s;p:%s;f:%s" % (csrc.split(":")[0] if csrc else "-", usrc, bs, ps, fs)
            rows.append((int(node), cid, date, uval, bv, pv, fv, sha, src, comm.replace("\t", " ")))
        rows.sort()
        with open(outp + ".part", "w", encoding="utf-8", newline="\n") as fo2:
            for r in rows:
                fo2.write("\t".join(str(x) for x in r) + "\n")
        os.replace(outp + ".part", outp)
        with open(os.path.join(WD, "dec", repo + ".tok"), "w", encoding="utf-8", newline="\n") as ft:
            ft.write("\n".join(toks) + ("\n" if toks else ""))
        print(repo, len(rows), flush=True)


def stage3():
    # judge-token bootstrap: token -> unit counts per family and 10-year bucket (pooled with neighbours)
    seeds = collections.defaultdict(collections.Counter)  # (fam, bucket, token) -> Counter(unit)
    open_rows = []
    seeded = []
    for fn in sorted(os.listdir(os.path.join(WD, "dec"))):
        if not fn.endswith(".tok"):
            continue
        for line in open(os.path.join(WD, "dec", fn), encoding="utf-8"):
            p = line.rstrip("\n").split("\t")
            if len(p) == 5:
                node, fam, bk, judges, u = p[0], p[1], int(p[2]), p[3].split(), int(p[4])
                seeded.append((node, fam, bk, judges, u))
                for t in judges:
                    seeds[(fam, bk, t)][u] += 1
            elif len(p) == 4:
                open_rows.append((p[0], p[1], int(p[2]), p[3].split()))

    def votes(fam, bk, judges, minus=None):
        tot = collections.Counter()
        used = 0
        for t in judges:
            c = collections.Counter()
            for b2 in (bk - 1, bk, bk + 1):
                c.update(seeds.get((fam, b2, t), {}))
            if minus is not None:
                c[minus] -= 1
            n = sum(c.values())
            if n < 8:
                continue
            u, k = c.most_common(1)[0]
            if k / n < 0.9:
                continue
            tot[u] += 1
            used += 1
        if not tot:
            return 0, 0
        (u, k), = tot.most_common(1)
        if k < 1 or k / sum(tot.values()) < 0.8 or (len(tot) > 1 and k < 2):
            return 0, 0
        return u, k
    # hold-out agreement on seeded rows (leave-one-out by subtracting the row's own unit)
    hold = collections.defaultdict(lambda: [0, 0, 0])
    for node, fam, bk, judges, u in seeded:
        v, k = votes(fam, bk, judges, minus=u)
        h = hold[fam]
        h[0] += 1
        if v:
            h[1] += 1
            h[2] += (v == u)
    with open(os.path.join(WD, "unit_holdout.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("family\tseeded\tjudge_predicted\tagree\tagree_rate\n")
        for fam, (n, pr, ag) in sorted(hold.items()):
            f.write("%s\t%d\t%d\t%d\t%.4f\n" % (fam, n, pr, ag, ag / pr if pr else 0))
    res = {}
    for node, fam, bk, judges in open_rows:
        v, k = votes(fam, bk, judges)
        if v:
            res[node] = v
    print("open", len(open_rows), "resolved by judges", len(res), flush=True)
    # form overrides from refine.py (second look at plurality / equallyDivided / certifiedAnswer)
    refine = {}
    rp = os.path.join(WD, "refine.tsv")
    if os.path.exists(rp):
        for line in open(rp, encoding="utf-8"):
            n2, v2, s2 = line.rstrip("\n").split("\t")
            refine[n2] = (v2, s2)
    # concatenate in node order
    order = []
    for fn in os.listdir(os.path.join(WD, "dec")):
        if fn.endswith(".tsv"):
            with open(os.path.join(WD, "dec", fn), encoding="utf-8") as f:
                first = f.readline().split("\t", 1)[0]
            order.append((int(first) if first else 1 << 40, fn))
    order.sort()
    n = 0
    with open(os.path.join(DATA, "decisions2.tsv.part"), "w", encoding="utf-8", newline="\n") as fo, \
            open(os.path.join(DATA, "commission.tsv"), "w", encoding="utf-8", newline="\n") as fc:
        for _, fn in order:
            for line in open(os.path.join(WD, "dec", fn), encoding="utf-8"):
                r = line.rstrip("\n").split("\t")
                node = r[0]
                src = r[8]
                if ";u:?;" in src:
                    if node in res:
                        r[3] = str(res[node])
                        src = src.replace(";u:?;", ";u:judges;")
                    else:
                        src = src.replace(";u:?;", ";u:-;")
                if node in refine:
                    r[6] = refine[node][0]
                    src = re.sub(r";f:[^;]*$", ";f:" + refine[node][1], src)
                fo.write("\t".join(r[:8] + [src]) + "\n")
                if r[9]:
                    e9 = r[9]
                    if re.search(r"adopted as the opinion of the court", e9, re.I):
                        nt = "adoptedAsOpinionOfCourt"
                    elif re.search(r"opinions? (?:of the Commission of Appeals )?(?:is |are )?(?:adopted|ADOPTED)", e9, re.I):
                        nt = "opinionAdopted"
                    elif re.search(r"holdings? (?:\w+ ){0,4}approved", e9, re.I):
                        nt = "holdingApproved"
                    elif re.search(r"judgments? (?:\w+ ){0,4}(?:adopted|approved)", e9, re.I):
                        nt = "judgmentAdopted"
                    elif re.search(r"opinions? (?:\w+ ){0,4}approved", e9, re.I):
                        nt = "opinionApproved"
                    else:
                        nt = "other"
                    fc.write("%s\t%s\t%s\t%s\n" % (node, r[1], nt, e9))
                n += 1
    os.replace(os.path.join(DATA, "decisions2.tsv.part"), os.path.join(DATA, "decisions2.tsv"))
    print("decisions2 rows", n)


if __name__ == "__main__":
    if sys.argv[1] == "stage2":
        stage2(sys.argv[2:] or None)
    else:
        stage3()
