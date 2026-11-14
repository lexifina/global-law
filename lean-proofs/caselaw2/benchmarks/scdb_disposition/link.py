#!/usr/bin/env python3
"""Link every SCDB case-centred row to (1) our Supreme Court opinion node and (2) the decision BELOW in our corpus.

Run:  python -I link.py            (reads work/scdb.tsv from extract.py; streams graph/nodes.tsv twice; reads SC texts
                                    from git; never reads any model output, status, history or gold file)
Outputs:
  work/sc_region.tsv   per linked SCDB row: the lower-court citation mentions found in our SC opinion text
  links.tsv            one row per SCDB row: SC link, below link, method, reasons, candidates
  key.tsv              the answer key: caseId, half, class, sub, scored, linked, below node, court group, ...
  link_summary.tsv     counts of link outcomes / failure reasons (scored rows and all rows)

Step 1 (SC opinion): SC nodes (repo supreme-court) whose citation list contains the SCDB usCite (else sctCite, else
  ledCite). One candidate -> linked if its date is within 60 days of dateDecision; several -> the one with the exact
  date, else the one whose citation list carries "SCDB <caseId>"; else ambiguous. Never guessed.
Step 2 (decision below): citations in OUR text of that SC opinion: the head matter (title, syllabus, "Reported
  below", counsel) and the first 8,000 characters of the first opinion section (procedural history). YAML front matter
  (which lists every case cited anywhere) is NOT read. Each citation -> every corpus node carrying it (nodes.tsv,
  keys by round6 citeforms/r6cite). A candidate must be:
    - not a Supreme Court node; court consistent with SCDB caseSource (+ caseSourceState) (see court_ok);
    - dated before the SC decision and at most 20 years before it;
  and then either cited in a "Reported below / reported at / reported in" phrase (tier A), or share a party-name token
  with the SCDB case name or our SC node's name (tier B). Tier A candidates are used if there are any.
  Exactly one distinct node -> linked. Several: if exactly one is not introduced by "rehearing" in the 150 characters
  before its citation, that one (method *_norehear); else ambiguous. Nothing else is ever chosen.
"""
import collections
import datetime
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
ROOT = os.path.dirname(BENCH)
sys.path.insert(0, os.path.join(BENCH, "common"))
sys.path.insert(0, os.path.join(ROOT, "round6", "history", "citeforms"))
import benchlib  # noqa: E402
import r6cite  # noqa: E402

GRAPH = benchlib.GRAPH
NODES = os.path.join(GRAPH, "nodes.tsv")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
WORK = os.path.join(HERE, "work")
NOWIN = 0x08000000 if os.name == "nt" else 0
DATASET = "scdb_disposition"
NL = "\n"

STOP = set("""united states state states people commonwealth america american company companies corporation corp inc
co ltd et al vs the of and for in re ex rel parte county city town village board department dept national railroad
railway railroads insurance bank trust commissioner commissioners internal revenue secretary director administrator
district court courts government federal mutual life fire association assn union local international new york
co. inc. mr mrs doing business as others another appellant appellee petitioner respondent plaintiff defendant error
estate matter heirs executor executrix trustee trustees receiver city of village of township""".split())

CLASS = {"3": ("NEG", "reversed"), "4": ("NEG", "reversed"), "5": ("NEG", "vacated"), "8": ("NEG", "vacated"),
         "6": ("PART", "part"), "7": ("PART", "part"), "2": ("CLEAN", "affirmed"), "9": ("CLEAN", "dismissed"),
         "1": ("NS", "granted"), "10": ("NS", "certification"), "11": ("NS", "no_disposition")}

REPORTED = re.compile(r"[Rr]eported\s+below|[Rr]eported\s+(?:at|in)\b|[Rr]eported\s*:|[Rr]eported\s+as\b")
REHEAR = re.compile(r"rehearing|re-hearing", re.I)


def tokens(name):
    out = set()
    for w in re.findall(r"[A-Za-z][A-Za-z'’\-]+", name or ""):
        w = w.lower().replace("’", "'").strip("'-")
        if w.endswith("'s"):
            w = w[:-2]
        if len(w) >= 3 and w not in STOP:
            out.add(w)
    return out


def scdb_date(s):
    m = re.match(r"(\d+)/(\d+)/(\d{4})", s or "")
    return int("%s%02d%02d" % (m.group(3), int(m.group(1)), int(m.group(2)))) if m else 0


def ddiff(a, b):
    try:
        da = datetime.date(a // 10000, a // 100 % 100, a % 100)
        db = datetime.date(b // 10000, b // 100 % 100, b % 100)
        return abs((da - db).days)
    except ValueError:
        return 10 ** 6


def cite_keys(c):
    return r6cite.keys(c.strip())


# ---------------------------------------------------------------------------------------------- courts
STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
          "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas",
          "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
          "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
          "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
          "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
          "West Virginia", "Wisconsin", "Wyoming", "Puerto Rico", "Guam", "Virgin Islands", "Canal Zone",
          "Northern Mariana Islands", "American Samoa", "Dakota", "Indian Territory"]
SPECIAL = {  # SCDB caseSource code -> set of our court ids (graph/court_table.tsv)
    "1": {669}, "2": {671}, "3": {668, 670, 659}, "4": {672, 664}, "5": {650, 651, 652, 653, 654, 655, 660, 661, 662,
    675, 685, 686, 687, 688}, "6": {674, 665}, "7": {676}, "8": {520}, "9": {692, 656, 2126}, "10": {649, 693},
    "14": {663}, "18": {678}, "19": {632, 631}}
GENERIC_CA = {657, 666}
GENERIC_DIST = {677, 1471}
GENERIC_CC = {658, 1347, 1934}


def state_in(name, st):
    if st == "Virginia":
        return re.search(r"(?<!West )\bVirginia\b", name) is not None
    if st == "Dakota":
        return re.search(r"(?<!North )(?<!South )\bDakota\b", name) is not None
    if st == "Washington":
        return re.search(r"\bWashington\b(?!,? D\.? ?C)", name) is not None and "District of Columbia" not in name
    return re.search(r"\b%s\b" % re.escape(st), name) is not None


class Courts:
    def __init__(self):
        self.row = {}
        with open(os.path.join(GRAPH, "court_table.tsv"), encoding="utf-8") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                self.row[int(p[0])] = {"name": p[1], "system": int(p[4]), "sname": p[5], "tier": p[6],
                                       "circuit": int(p[7] or 0), "kind": p[8]}
        self.codes = {}
        with open(os.path.join(WORK, "codes.tsv"), encoding="utf-8") as f:
            next(f)
            for line in f:
                v, c, lab = line.rstrip("\n").split("\t")
                self.codes[(v, c)] = lab

    def label(self, var, code):
        return self.codes.get((var, code), "")

    def source_spec(self, src, sstate):
        """-> (spec, None) or (None, reason). spec is a tuple describing what our court must be."""
        if not src:
            return None, "no_case_source"
        c = int(src)
        lab = self.label("caseSource", src)
        if src in SPECIAL:
            return ("ids", frozenset(SPECIAL[src])), None
        if 21 <= c <= 31:
            return ("ca", c - 20), None
        if c == 32:
            return ("ca", 12), None
        if 41 <= c <= 199 or c == 163:
            st = district_state(lab, c)
            return (("dist", st), None) if st else (None, "court_unmapped")
        if 403 <= c <= 449 and c != 440:
            st = next((s for s in STATES if lab.startswith(s + " ")), None)
            return (("cc", st), None) if st else (None, "court_unmapped")
        if c == 440:
            return ("dc", None), None
        if c in (300, 301, 302) or 15 <= c <= 17:
            st = self.label("caseSourceState", sstate)
            if not st or st in ("United States", "Interstate Compact", "Indian", "Philippines"):
                return None, "court_unmapped"
            tier = {300: ("last",), 301: ("appellate",), 302: ("trial", "special"), 15: ("last", "appellate"),
                    16: ("appellate", "last"), 17: ("trial", "special")}[c]
            return ("st", st, tier), None
        if c == 20:
            return ("bk", None), None
        return None, "court_unmapped"

    def ok(self, spec, court):
        """-> '' (no), 'exact' or 'generic'."""
        r = self.row.get(court)
        if r is None:
            return ""
        k = spec[0]
        if k == "ids":
            return "exact" if court in spec[1] else ""
        if k == "ca":
            if r["system"] == 0 and r["kind"] in ("circuit", "dc-circuit") and r["circuit"] == spec[1]:
                return "exact"
            if spec[1] == 12 and court == 626:  # codebook: code 32 includes the (old) Court of Appeals for the D.C.
                return "exact"
            return "generic" if court in GENERIC_CA else ""
        if k == "dist":
            if r["system"] == 0 and "District Court" in r["name"] and "Bankruptcy" not in r["name"] \
                    and state_in(r["name"], spec[1]):
                return "exact"
            if spec[1] == "District of Columbia" and court == 519:
                return "exact"
            if spec[1] == "Canal Zone" and court == 361:
                return "exact"
            return "generic" if court in GENERIC_DIST else ""
        if k == "cc":
            if r["system"] == 0 and "Circuit Court" in r["name"] and "Appeals" not in r["name"] \
                    and state_in(r["name"], spec[1]):
                return "exact"
            return "generic" if court in GENERIC_CC else ""
        if k == "dc":
            return "exact" if r["sname"] == "District of Columbia" or court == 632 else ""
        if k == "st":
            if r["system"] != 0 and r["sname"] == spec[1] and r["tier"] in spec[2]:
                return "exact"
            if spec[1] == "Dakota" and r["sname"] == "Dakota Territory":
                return "exact"
            return ""
        if k == "bk":
            return "exact" if "Bankruptcy" in r["name"] else ""
        return ""

    def group(self, court):
        r = self.row.get(court)
        if r is None:
            return "?"
        return "federal" if r["system"] == 0 else "state"


def district_state(lab, c):
    special = {55: "District of Columbia", 62: "Guam", 112: "Puerto Rico", 125: "Virgin Islands", 163: "Canal Zone",
               180: "Virginia", 187: "Louisiana", 102: "Northern Mariana Islands"}
    if c in special:
        return special[c]
    return next((s for s in sorted(STATES, key=len, reverse=True) if lab.startswith(s + " ")), None)


# ---------------------------------------------------------------------------------------------- texts
def fetch(repo, items):
    """items: [(node, path)] -> {node: text} (git HEAD, CRLF->LF), chunked."""
    out = {}
    rd = os.path.join(REPOS, repo)
    for i in range(0, len(items), 2000):
        chunk = items[i:i + 2000]
        inp = "".join("HEAD:%s\n" % p for _, p in chunk).encode("utf-8")
        res = subprocess.run(["git", "-C", rd, "cat-file", "--batch"], input=inp, capture_output=True,
                             creationflags=NOWIN).stdout
        pos = 0
        for n, _p in chunk:
            e = res.find(b"\n", pos)
            header = res[pos:e].split()
            if len(header) < 3 or header[1] != b"blob":
                pos = e + 1
                continue
            size = int(header[2])
            out[n] = res[e + 1:e + 1 + size].decode("utf-8", "replace").replace("\r\n", NL)
            pos = e + 1 + size + 1
    return out


def region(text):
    """(head matter text, opening of the first opinion section) with the YAML front matter removed."""
    t = text
    if t.startswith("---"):
        e = t.find("\n---", 3)
        if e >= 0:
            t = t[e + 4:]
    heads = list(re.finditer(r"^## (.+)$", t, re.M))
    if not heads:
        return "", t[:12000]
    head = ""
    opening = ""
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(t)
        body = t[h.end():end]
        title = h.group(1).strip().lower()
        if "head matter" in title or title == "syllabus":
            head += body
        elif not opening:
            opening = body[:8000]
    if not head and not opening:
        opening = t[:12000]
    return head, opening


def mentions(head, opening):
    """[(where, key list, cue_reported, cue_rehear, cite text)] for each citation in the region."""
    out = []
    for where, txt in (("head", head), ("open", opening)):
        for m in r6cite.finditer(txt):
            ks = r6cite.keys(m)
            if not ks:
                continue
            ls = txt.rfind("\n", 0, m.start()) + 1
            before = txt[max(ls, m.start() - 160):m.start()]
            line_before = txt[ls:m.start()]
            rep = 1 if REPORTED.search(line_before[-300:]) else 0
            reh = 1 if REHEAR.search(before) else 0
            out.append((where, ks, rep, reh, re.sub(r"\s+", " ", m.group(0))))
    return out


# ---------------------------------------------------------------------------------------------- main
def main():
    courts = Courts()
    rows = []
    with open(os.path.join(WORK, "scdb.tsv"), encoding="utf-8") as f:
        hdr = next(f).rstrip("\n").split("\t")
        for line in f:
            rows.append(dict(zip(hdr, line.rstrip("\n").split("\t"))))
    print("scdb rows", len(rows), flush=True)

    # pass A: Supreme Court nodes
    sc = {}
    sc_by_key = collections.defaultdict(list)
    sc_by_id = {}
    with open(NODES, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[1] != "supreme-court":
                continue
            n = int(p[0])
            sc[n] = (p[2], int(p[4] or 0), p[6], p[7] if len(p) > 7 else "")
            for c in p[5].split("|"):
                c = c.strip()
                m = re.match(r"SCDB\s+(\S+)$", c)
                if m:
                    sc_by_id.setdefault(m.group(1), []).append(n)
                    continue
                for k in cite_keys(c):
                    sc_by_key[k].append(n)
    print("sc nodes", len(sc), flush=True)

    def sc_link(r):
        d = scdb_date(r["dateDecision"])
        for fld in ("usCite", "sctCite", "ledCite"):
            c = r[fld].strip()
            if not c:
                continue
            ks = cite_keys(c)
            cand = sorted({n for k in ks for n in sc_by_key.get(k, [])})
            if not cand:
                continue
            idc = set(sc_by_id.get(r["caseId"], []))
            if len(cand) == 1:
                n = cand[0]
                if ddiff(sc[n][1], d) <= 60 or n in idc:
                    return n, "%s:unique" % fld
                return None, "sc_date_mismatch"
            ex = [n for n in cand if sc[n][1] == d]
            if len(ex) == 1:
                return ex[0], "%s:date" % fld
            byid = [n for n in (ex or cand) if n in idc]
            if len(byid) == 1:
                return byid[0], "%s:scdbid" % fld
            return None, "sc_ambiguous"
        if not (r["usCite"] or r["sctCite"] or r["ledCite"]):
            return None, "no_reporter_cite"
        return None, "sc_not_in_corpus"

    links = {}
    for r in rows:
        links[r["caseId"]] = dict(zip(("sc_node", "sc_method"), sc_link(r)))
    print("sc linked", sum(1 for v in links.values() if v["sc_node"] is not None), flush=True)

    # pass B: texts of the linked SC opinions -> citation mentions
    need_sc = sorted({v["sc_node"] for v in links.values() if v["sc_node"] is not None})
    texts_m = {}
    for i in range(0, len(need_sc), 4000):
        part = need_sc[i:i + 4000]
        tx = fetch("supreme-court", [(n, sc[n][0]) for n in part])
        for n in part:
            if n in tx:
                texts_m[n] = mentions(*region(tx[n]))
            else:
                texts_m[n] = None
        print("texts", i + len(part), flush=True)
    need_keys = set()
    for ms in texts_m.values():
        for _w, ks, _a, _b, _c in ms or []:
            need_keys.update(ks)
    print("needed keys", len(need_keys), flush=True)

    # pass C: every non-SC node carrying a needed key
    by_key = collections.defaultdict(list)
    ninfo = {}
    with open(NODES, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[1] == "supreme-court":
                continue
            hit = False
            for c in p[5].split("|"):
                for k in cite_keys(c):
                    if k in need_keys:
                        by_key[k].append(int(p[0]))
                        hit = True
            if hit:
                ninfo[int(p[0])] = (p[1], int(p[3] or -1), int(p[4] or 0), p[6], p[5])
    print("candidate nodes", len(ninfo), flush=True)

    with open(os.path.join(WORK, "sc_region.tsv"), "w", encoding="utf-8", newline=NL) as o:
        o.write("caseId\tsc_node\twhere\tkey\treported\trehear\tcite\tnodes\n")
        for r in rows:
            n = links[r["caseId"]]["sc_node"]
            for w, ks, a, b, c in (texts_m.get(n) or []) if n is not None else []:
                k = next((k for k in ks if k in by_key), ks[0])
                o.write("\t".join([r["caseId"], str(n), w, k, str(a), str(b), c,
                                   ",".join(map(str, sorted(set(by_key.get(k, [])))))]) + NL)

    # pass D: below links
    stat_all = collections.Counter()
    stat_sc = collections.Counter()
    lk = open(os.path.join(HERE, "links.tsv"), "w", encoding="utf-8", newline=NL)
    lk.write("caseId\tsc_node\tsc_method\tsc_date\tcaseSource\tcaseSourceState\tsource_label\tlink\tmethod\tbelow\t"
             "below_repo\tbelow_court\tbelow_court_name\tbelow_date\tbelow_name\tcourt_match\tn_mentions\t"
             "n_court\tn_court_date\tn_final\tcandidates\n")
    key = open(os.path.join(HERE, "key.tsv"), "w", encoding="utf-8", newline=NL)
    key.write("caseId\thalf\tfile\tusCite\tdateDecision\tcaseName\tcaseDisposition\tcaseDispositionUnusual\t"
              "lcDisposition\tcaseSource\tcaseSourceState\tclass\tsub\tscored\tlinked\tlink\tsc_node\tbelow\t"
              "below_group\tbelow_date\tbelow_name\n")
    for r in rows:
        cid = r["caseId"]
        L = links[cid]
        n = L["sc_node"]
        cls, sub = CLASS.get(r["caseDisposition"], ("NS", "blank"))
        if r["caseDispositionUnusual"] == "1":
            cls, sub = "NS", "unusual"
        scored = cls in ("NEG", "PART", "CLEAN") and r["caseSource"] != ""
        spec, why = courts.source_spec(r["caseSource"], r["caseSourceState"])
        below = None
        method = ""
        nm = ncourt = ncd = nfin = 0
        cands = ""
        cm = ""
        if n is None:
            link = L["sc_method"]
        elif spec is None:
            link = why
        elif texts_m.get(n) is None:
            link = "sc_text_missing"
        else:
            scd = sc[n][1]
            names = tokens(r["caseName"]) | tokens(sc[n][2])
            ms = texts_m[n]
            nm = len(ms)
            seen = {}
            for w, ks, a, b, c in ms:
                k = next((k for k in ks if k in by_key), None)
                if k is None:
                    continue
                for x in by_key[k]:
                    info = ninfo[x]
                    okc = courts.ok(spec, info[1])
                    e = seen.setdefault(x, {"court": okc, "date": info[2], "rep": 0, "norh": 0, "name": 0,
                                            "cites": set()})
                    e["rep"] |= a
                    e["norh"] |= (1 - b)
                    e["cites"].add(c)
            court_c = {x: e for x, e in seen.items() if e["court"]}
            ncourt = len(court_c)
            cd = {x: e for x, e in court_c.items() if e["date"] and e["date"] < scd and scd - e["date"] <= 200000}
            ncd = len(cd)
            for x, e in cd.items():
                e["name"] = 1 if names & tokens(ninfo[x][3]) else 0
            tierA = {x: e for x, e in cd.items() if e["rep"]}
            tierB = {x: e for x, e in cd.items() if e["name"]}
            fin, base = (tierA, "reported") if tierA else (tierB, "name")
            nfin = len(fin)
            cands = ";".join("%d:%s:%d:%s" % (x, ninfo[x][0], ninfo[x][2], ninfo[x][3][:40].replace(";", ","))
                             for x in sorted(fin or cd or court_c)[:8])
            if not seen:
                link = "no_cited_decision_in_corpus" if nm else "no_citation_in_text"
            elif not court_c:
                link = "no_candidate_in_source_court"
            elif not cd:
                link = "candidate_date_mismatch"
            elif not fin:
                link = "candidate_name_mismatch"
            elif len(fin) == 1:
                below = next(iter(fin))
                method = base
                link = "linked"
            else:
                nr2 = [x for x in fin if fin[x]["norh"]]
                if len(nr2) == 1:
                    below = nr2[0]
                    method = base + "_norehear"
                    link = "linked"
                else:
                    link = "ambiguous_several"
            if below is not None:
                cm = fin[below]["court"]
        stat_all[link] += 1
        if scored:
            stat_sc[link] += 1
        half = benchlib.split_half(DATASET, cid)
        bi = ninfo.get(below) if below is not None else None
        grp = courts.group(bi[1]) if bi else ""
        lk.write("\t".join(map(str, [
            cid, "" if n is None else n, L["sc_method"] if n is not None else "", sc[n][1] if n is not None else "",
            r["caseSource"], r["caseSourceState"], courts.label("caseSource", r["caseSource"]), link, method,
            "" if below is None else below, bi[0] if bi else "", bi[1] if bi else "",
            courts.row.get(bi[1], {}).get("name", "") if bi else "", bi[2] if bi else "", bi[3] if bi else "", cm,
            nm, ncourt, ncd, nfin, cands])) + NL)
        key.write("\t".join(map(str, [
            cid, half, r["file"], r["usCite"], r["dateDecision"], r["caseName"][:120], r["caseDisposition"],
            r["caseDispositionUnusual"], r["lcDisposition"], r["caseSource"], r["caseSourceState"], cls, sub,
            int(scored), int(below is not None), link, "" if n is None else n, "" if below is None else below, grp,
            bi[2] if bi else "", bi[3][:100] if bi else ""])) + NL)
    lk.close()
    key.close()
    with open(os.path.join(HERE, "link_summary.tsv"), "w", encoding="utf-8", newline=NL) as o:
        o.write("link\tscored_rows\tall_rows\n")
        for k in sorted(stat_all, key=lambda k: -stat_all[k]):
            o.write("%s\t%d\t%d\n" % (k, stat_sc[k], stat_all[k]))
        o.write("total\t%d\t%d\n" % (sum(stat_sc.values()), sum(stat_all.values())))
    for k in sorted(stat_all, key=lambda k: -stat_all[k]):
        print("%-32s scored %6d   all %6d" % (k, stat_sc[k], stat_all[k]))


if __name__ == "__main__":
    main()
