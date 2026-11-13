"""Bench by court size (round 2, agent enbanc): a court-size table derived from the judges lines, and the whole-court
/ en banc label it supports.

    python -X utf8 bench_size_fix.py scan [procs]   git re-read (<= 8 processes), three steps:
                                                    1 sample + overruling decisions -> work/courts/bench3.tsv
                                                    2 table                         -> work/round2/enbanc/court_size.tsv
                                                    3 every decision of the intermediate courts that are small (<= 3)
                                                      or always sit in full          -> appended to bench3.tsv
    python -X utf8 bench_size_fix.py table          step 2 only (from bench3.tsv)
    python -X utf8 bench_size_fix.py decide         the relabels the rule would make -> work/round2/enbanc/relabel.tsv
    python -X utf8 bench_size_fix.py install-table  work/round2/enbanc/court_size.tsv -> data/court_size.tsv
    python -X utf8 bench_size_fix.py apply [data-dir]
                                                    decisions2.tsv -> decisions2.tsv.tmp -> rename; the input is kept
                                                    once as decisions2.pre_round2.tsv; idempotent

Only signals are written (judge surnames, counts), never opinion text. Composes after labels_fix2.py.

JUDGES OF A DECISION. The front-matter `judges` lines (CAP's concurrence / "Before" lines), else a "Before ..." line
in the first 3,000 characters, plus the authors in the opinion section titles. A line is read left to right: names
collect until a title, a verb or a marker says what they are:
    sitting      "... , JJ., concur", "Before A, B and C, Circuit Judges", dissenting, joining;
    out          "not participating", "not sitting", "took no part", "recused", "disqualified", "absent";
    visiting     "Senior ...", "District Judge", "sitting by designation / assignment", "Special", "pro tem",
                 "Retired", "Supernumerary", "ad hoc", commissioners: sits, but is not a judge of the court.
`names` in bench3.tsv are surnames in capitals. A decision with fewer than 2 names (no line, or only an author) is
never relabelled.

COURT SIZE (data/court_size.tsv: court_id, from, to, judges, src, tag). The court is the unit row of courts2.tsv
(id >= 10000) for a decision with a unit, else the court id. Sample: up to 60 decisions per court, unit and year,
evenly spaced by date (tiers L and A, not SCOTUS). Decisions without unit in a court that has units are not sampled.
    regular judge of a year   named (not as visiting, not as out) in at least max(2, 30% of the third most frequent
                              judge's count) of the year's sampled decisions; or named at least once in a year next
                              to one in which he is regular;
    span                      a regular judge's appearances, joined while the gap is at most 400 days, widened by 30
                              days at each end (the sample misses the first and last days); a judge seen within 365
                              days of the start or end of the court's data (or of a hole of over 180 days in them)
                              is taken to sit from that start or to that end, so the size does not taper there;
    size at a date            the number of regular judges whose span covers the date.
A year is `full` when at least 60% of its sampled decisions with 2 or more names show every regular judge (less the
judges named as out): the court always sits as a full court. Federal courts of appeals: the authorised judgeships
from memory (FED) are the size; tag S where the data size equals it on at least half of the range's days, L where
not, U for data-only rows. State courts of last resort: S where the data size equals the remembered present size
(LAST) for a range after 1990, else U.

RULE (src `b:size:<sitting>[+<out>out]/<size>[+u<unit>]+was:<old value>/<old evidence>`). Only bench panel or
unknown, tiers L and A, never SCOTUS; never circulated / limitedEnBanc / conflictPanel / division / enBanc rows.
    sitting = the decision's names that are regular judges of the court at the date and not visiting or out;
    out     = regular judges the line names as not participating;
    whole   = sitting >= 2, sitting > size / 2, sitting + out >= size; and the court's sample of that year has at
              least 5 decisions naming 2 or more regular judges (else the size is not trusted).
    value   = wholeCourt for tier L, for size <= 3, and for a `full` year; enBanc for another intermediate court
              (limitedEnBanc is never produced: the Ninth Circuit's limited en banc court is not the whole court).
    Arizona, Washington, the Oklahoma Court of Civil Appeals, Indiana and Tennessee are left out (DIVISION_UNITS).
    An order on a rehearing petition (the head says a petition / suggestion for rehearing is denied or granted) is
    not relabelled enBanc. A decision without unit in a court that has units is matched to the one unit whose
    regular judges include at least 2 of its names; no match or two matches -> not relabelled.
"""
import bisect, collections, datetime, hashlib, math, os, re, shutil, subprocess, sys, threading
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan import parse_fm  # noqa: E402
from labels_fix2 import fm_judges, JSTOP2, NAME_CAPS, NAME_ANY  # noqa: E402

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
L2 = os.path.join(WORK, "caselaw-lean-2")
DATA = os.path.join(L2, "data")
WD = os.path.join(L2, "work", "courts")
PRIV = os.path.join(L2, "work", "round2", "enbanc")
B3 = os.path.join(WD, "bench3.tsv")
SCOTUS = 2906
K_SAMPLE = 60
MARGIN = 30
GAP = 400
HOLE = 180
MIN_SUPPORT = 5
# courts whose units are divisions of one court, not courts of their own (AZ, WA, OK Civ. App., IN, TN): a division's
# judges are not the whole court, so these courts are left out of the rule (blind review, courts_validation.md s7)
DIVISION_UNITS = (14, 3153, 2582, 880, 2922, 2923)
EDGE = 365
TREAT_KINDS = ("overruled", "disapproved", "recededFrom", "declinedToFollow")

# authorised judgeships of the federal courts of appeals, from memory (tag L): circuit -> [(from yyyymmdd, judges)]
FED = {
    1: [(18910303, 2), (19050101, 3), (19781020, 4), (19840710, 6)],
    2: [(18910303, 3), (19020101, 4), (19290101, 5), (19380531, 6), (19610519, 9), (19781020, 11), (19840710, 13)],
    3: [(18910303, 2), (18990101, 3), (19300101, 4), (19360101, 5), (19440101, 6), (19490803, 7), (19610519, 8),
        (19680618, 9), (19781020, 10), (19840710, 12), (19901201, 14)],
    4: [(18910303, 2), (19220101, 3), (19610519, 5), (19660318, 7), (19781020, 10), (19840710, 11), (19901201, 15)],
    5: [(18910303, 2), (18990101, 3), (19300101, 4), (19380531, 5), (19420101, 6), (19540210, 7), (19610519, 9),
        (19660318, 13), (19680618, 15), (19781020, 26), (19811001, 14), (19840710, 16), (19901201, 17)],
    6: [(18910303, 2), (18990101, 3), (19280101, 4), (19380531, 5), (19400101, 6), (19660318, 9), (19781020, 11),
        (19840710, 15), (19901201, 16)],
    7: [(18910303, 2), (18950101, 3), (19050101, 4), (19380531, 5), (19490803, 6), (19610519, 7), (19660318, 8),
        (19781020, 9), (19840710, 11)],
    8: [(18910303, 2), (18940101, 3), (19030101, 4), (19250101, 6), (19290401, 5), (19400101, 7), (19660318, 8),
        (19781020, 9), (19840710, 10), (19901201, 11)],
    9: [(18910303, 2), (18950101, 3), (19290101, 4), (19330101, 5), (19370101, 7), (19540210, 9), (19680618, 13),
        (19781020, 23), (19840710, 28), (20090121, 29)],
    10: [(19290401, 4), (19490803, 5), (19610519, 6), (19680618, 7), (19781020, 8), (19840710, 10), (19901201, 12)],
    11: [(19811001, 12)],
    12: [(18930101, 3), (19300101, 5), (19380531, 6), (19490803, 9), (19781020, 11), (19840710, 12), (20080101, 11)],
    13: [(19821001, 12)],
}
# present size of the state courts of last resort, from memory: v1 system index -> judges (used for the S tag only)
LAST = {1: 9, 2: 5, 3: 7, 4: 7, 5: 7, 6: 7, 7: 7, 8: 5, 9: 7, 10: 9, 11: 5, 12: 5, 13: 7, 14: 5, 15: 7, 16: 7, 17: 7,
        18: 7, 19: 7, 20: 7, 21: 7, 22: 7, 23: 7, 24: 9, 25: 7, 26: 7, 27: 7, 28: 7, 29: 5, 30: 7, 31: 5, 32: 7, 33: 7,
        34: 5, 35: 7, 36: 9, 37: 7, 38: 7, 39: 5, 40: 5, 41: 5, 42: 5, 43: 9, 44: 5, 45: 5, 46: 7, 47: 9, 48: 5, 49: 7,
        50: 5, 51: 9}

# ------------------------------------------------------------------------------------------------ judges of a decision
OUT = (r"(?i:\bnot\s+(?:sitting|participat\w+|voting|present|taking\s+part|hearing|having\s+(?:heard|participated|sat))|"
       r"\bt(?:ook|akes?|aking)\s+no\s+part|did\s+not\s+(?:sit|participate|take\s+part|hear)|recus\w+|disqualif\w+|"
       r"\babsent\b|\bon\s+leave\b|non-?participating|no\s+participation|abstain\w*|\bnot\s+on\s+(?:the\s+)?panel)")
VIS = (r"[Ss]enior\s+(?:Circuit\s+|District\s+|Associate\s+)?(?:Judge|Justice)s?|SENIOR\s+(?:CIRCUIT\s+|DISTRICT\s+)?"
       r"(?:JUDGE|JUSTICE)S?|(?:United\s+States\s+|U\.\s?S\.\s+|Chief\s+|CHIEF\s+)?[Dd]istrict\s+(?:Court\s+)?Judges?|"
       r"DISTRICT\s+JUDGES?|sitting\s+by|by\s+(?:special\s+)?(?:designation|assignment|appointment)|"
       r"[Ss]pecial(?:ly)?\s+(?:[Aa]ssociate\s+|[Cc]hief\s+)?(?:Judge|Justice|Commissioner)s?|SPECIAL\s+(?:JUDGE|JUSTICE)S?|"
       r"[Pp]ro\s+[Tt]em(?:pore)?\b|PRO\s+TEM(?:PORE)?\b|[Rr]etired|RETIRED|\(?\bRet\.\)?|[Ss]upernumerary|SUPERNUMERARY|"
       r"[Aa]d\s+[Hh]oc|AD\s+HOC|[Ee]meritus|Judge\s+of\s+the|"
       r"[Aa]ssigned|[Dd]esignated|Court\s+of\s+(?:Claims|Customs|International\s+Trade)|Commissioners?\b|"
       r"Circuit\s+Justice|Associate\s+Justice\s+of\s+the\s+Supreme")
SIT = (r"concur\w*|CONCUR\w*|dissent\w*|DISSENT\w*|join\w*|JOIN\w*|agree\w*|AGREE\w*|\bsitting\b|\bSITTING\b|"
       r"participat\w+|PARTICIPAT\w+")
REG = (r"Circuit\s+Judges?|CIRCUIT\s+JUDGES?|C\.\s?J\.|P\.\s?J\.|JJ\.|(?:(?<=, )|(?<=,))J\.|Chief\s+(?:Judge|Justice)|CHIEF\s+"
       r"(?:JUDGE|JUSTICE)|Presiding\s+(?:Judge|Justice)|PRESIDING\s+(?:JUDGE|JUSTICE)|Justices?\b|JUSTICES?\b|"
       r"Judges?\b|JUDGES?\b")
NAME = r"(?:Mc|Mac|La|Le|De|Di|Du|Van|Von|St\.? ?|O['’])?[A-Z][A-Za-z'’\-]{2,}"
TOKEN = re.compile(r"(?P<out>%s)|(?P<vis>%s)|(?P<reg>%s)|(?P<sit>%s)|(?P<name>\b%s\b)" % (OUT, VIS, REG, SIT, NAME))
OUT_HEAD = re.compile(r"(?:%s)\s*[:—–-]\s*$" % OUT)
BEFORE = re.compile(r"(?:^|\n)\s*(?:Before|BEFORE|Present|PRESENT)\s*[:\-—–]?\s*(.{5,700}?)(?:\.\s*\n|\n\s*\n|$)", re.S)
TAIL = re.compile(r"^[^\n]{0,250}(?:JJ\.|J\.|C\. ?J\.|P\. ?J\.|Judges?|Justices?)[^\n]{0,80}\b(?:concur|CONCUR|dissent|DISSENT)"
                  r"[^\n]{0,250}$", re.M)
SECT = re.compile(r"^## ([A-Za-z -]+?)(?: \(([^)\n]{2,120})\))?\s*$", re.M)
RH = re.compile(
    r"(?:petition|suggestion|application|motion|request)s?\s+for\s+(?:panel\s+)?(?:re)?hearing(?:\s+and\s+(?:suggestion"
    r"\s+for\s+)?rehearing)?(?:\s+(?:en|in)\s+banc)?[^.]{0,120}?\b(?:denied|DENIED|granted|GRANTED|overruled|refused)|"
    r"(?:re)?hearing\s+(?:en|in)\s+banc\s+(?:is|are|be|was)?\s*(?:hereby\s+)?(?:denied|DENIED|granted|GRANTED)|"
    r"(?:voted|vote|poll)[^.]{0,80}?(?:re)?hear(?:ing)?[^.]{0,40}?(?:en|in)\s+banc|"
    r"ON\s+(?:PETITIONS?|SUGGESTIONS?|APPLICATIONS?|MOTIONS?)\s+FOR\s+(?:PANEL\s+)?REHEARING|"
    r"[Oo]n\s+(?:[Pp]etitions?|[Ss]uggestions?|[Aa]pplications?|[Mm]otions?)\s+for\s+(?:[Pp]anel\s+)?[Rr]ehearing|"
    r"[Ss]ur\s+[Pp]etition\s+for|SUR\s+PETITION\s+FOR", re.S)
SURNAME_STOP = JSTOP2 | set("""WRITER JUDICIAL ACTIVE REGULAR CONCURRED CONCURRING SAME LIKE FOREGOING ABOVE CASE CASES
COUNTY PARISH ORLEANS STATE STATES UNITED NORTHERN SOUTHERN EASTERN WESTERN MIDDLE CENTRAL FIRST SECOND THIRD FOURTH
FIFTH SIXTH SEVENTH EIGHTH NINTH TENTH ELEVENTH FEDERAL CLAIMS CUSTOMS PATENT INTERNATIONAL TRADE ARGUED SUBMITTED
DECIDED VIEW DISSENTED HONORABLE HON MESSRS MR MRS REASONS HEARD CAUSE ILLNESS DEATH DIED VACANCY RESIGNED BECAME
MEMBER AFTER SINCE TIME WAS WERE HAD HAS BEEN THAN THEN ALTHOUGH BECAUSE HOWEVER DELIVERED ANNOUNCED AUTHORED WROTE
DOCKET CALENDAR NOTE EDITOR REPORTER FOOTNOTE COMMISSIONER COMMISSIONERS REFEREE ATTORNEY GENERAL CHANCELLOR""".split())


def surname(tok):
    return re.sub(r"[^A-Z]", "", tok.upper())


def read_line(ln, caps):
    """-> (sitting, out, visiting) surname lists of one judges line"""
    sit, out, vis = [], [], []
    cur, grp = [], []          # names waiting for a title; titled groups [(names, visiting)] waiting for a verb
    out_mode = False
    pre_vis = False            # a visiting title printed before the name ("Senior District Judge SMITH")
    cur_end = 0

    def flush(dst_out):
        nonlocal cur, grp, pre_vis
        for names, v in grp + ([(cur, pre_vis)] if cur else []):
            for n in names:
                (out if dst_out else (vis if v else sit)).append(n)
        cur, grp, pre_vis = [], [], False

    for m in TOKEN.finditer(ln):
        k = m.lastgroup
        if k == "name":
            t = m.group(0)
            if caps and not NAME_CAPS.fullmatch(t):
                continue
            u = surname(t)
            if len(u) < 3 or u in SURNAME_STOP:
                continue
            if cur and not re.search(r",|\band\b|\bAND\b|&|;", ln[cur_end:m.start()]):
                cur[-1] = u            # "John M. Walker": keep the last word of a name
            else:
                cur.append(u)
            cur_end = m.end()
        elif k == "reg":
            if cur:
                grp.append((cur, pre_vis))
                cur, pre_vis = [], False
        elif k == "vis":
            if cur:
                grp.append((cur, True))
                cur, pre_vis = [], False
            elif re.match(r"\s+[A-Z]", ln[m.end():m.end() + 4]):
                pre_vis = True
            elif grp:
                grp[-1] = (grp[-1][0], True)
        elif k == "sit":
            flush(out_mode)
        elif k == "out":
            if OUT_HEAD.search(ln[:m.end() + 3]) or re.match(r"\s*[:—–-]", ln[m.end():m.end() + 3]):
                flush(False)
                out_mode = True      # "Not participating: A and B"
            else:
                flush(True)
    flush(out_mode)
    return sit, out, vis


def judges_of(text):
    """-> (sitting, out, visiting, nlines, rh, oplen)"""
    fm, body = parse_fm(text)
    lines = fm_judges(text)
    lines = [re.sub(r"\\n|\\t", " ", l).replace('\\"', '"') for l in lines]
    src = "fm" if lines else "-"
    if not lines:
        m = BEFORE.search(body[:3000])
        if m:
            lines = [re.sub(r"\s+", " ", m.group(1))]
            src = "before"
    if not lines:
        lines = [m.group(0).strip() for m in TAIL.finditer(body[-1500:])][-3:]
        if lines:
            src = "tail"
    sit, out, vis = [], [], []
    for ln in lines:
        ln = re.sub(r"\*+|\[\d+\]|\(\d+\)|†|‡", " ", ln)
        capn = [t for t in NAME_CAPS.findall(ln) if surname(t) not in SURNAME_STOP and len(surname(t)) >= 3]
        s, o, v = read_line(ln, len(capn) >= 2)
        sit += s
        out += o
        vis += v
    authors = []
    first = None
    for m in SECT.finditer(body):
        kind, who = m.group(1).strip().lower(), m.group(2)
        if kind.startswith(("head", "cap head")):
            continue
        if first is None:
            first = m.end()
        if who and not re.search(r"per curiam|memorandum|order", who, re.I):
            capn = len([t for t in NAME_CAPS.findall(who) if surname(t) not in SURNAME_STOP]) >= 1
            s, o, v = read_line(who.split(" delivered")[0], capn)
            if len(s) + len(v) == 1:       # a section title names one judge
                authors.append((s + v)[0])
                if v:
                    vis += v
    for a in authors:
        if a not in sit and a not in out and a not in vis:
            sit.append(a)
    oplen = len(body) - (first or 0)
    head = body[:1500] + " " + " ".join(lines)
    rh = 1 if RH.search(head) else 0

    def uniq(x):
        seen = []
        for n in x:
            if n not in seen:
                seen.append(n)
        return seen
    sit, out, vis = uniq(sit), uniq(out), uniq(vis)
    sit = [n for n in sit if n not in out and n not in vis]
    return sit, out, vis, src, len(authors), rh, oplen


# ------------------------------------------------------------------------------------------------ git re-read
def one_repo(args):
    repo, items = args
    p = subprocess.Popen(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, creationflags=0x08000000 if os.name == "nt" else 0)

    def feed():
        for _, path, _ in items:
            p.stdin.write(("HEAD:%s\n" % path).encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    out = []
    for node, _, kind in items:
        header = p.stdout.readline().split()
        if len(header) < 3 or header[1] == b"missing":
            out.append(None)
            continue
        data = p.stdout.read(int(header[2]))
        p.stdout.read(1)
        text = data.decode("utf-8", "replace").replace("\r\n", "\n")
        sit, o, vis, src, na, rh, oplen = judges_of(text)
        out.append("%s\t%s\t%s\t%s\t%s\t%s\n" % (node, kind, ",".join(sit) or "-", ",".join(o) or "-",
                                                 ",".join(vis) or "-", "src=%s|au=%d|rh=%d|len=%d" % (src, na, rh, oplen)))
    p.wait()
    return out


UNIT_EP = {}


def units_alive(units, c, d):
    """the units of court c that exist on date d"""
    return [(u, k) for u, k in units.get(c, ()) if UNIT_EP[(c, u)][0] <= d <= UNIT_EP[(c, u)][1]]


def load_courts():
    ep = collections.defaultdict(list)
    unit_row = {}
    for line in open(os.path.join(DATA, "courts2.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        ep[int(f[0])].append((int(f[1]), int(f[2]), f[3], int(f[4]), f[5], int(f[7])))
        m = re.match(r"unit-of:(\d+)", f[9])
        if m:
            unit_row[(int(m.group(1)), int(f[8]))] = int(f[0])
            UNIT_EP[(int(m.group(1)), int(f[8]))] = (int(f[1]), int(f[2]))
    return ep, unit_row


def epoch_of(ep, cid, date):
    rows = ep.get(cid)
    if not rows:
        return (0, 0, "", -1, "?", 0)
    for r in rows:
        if r[0] <= date <= r[1]:
            return r
    return rows[-1] if date > rows[-1][1] else rows[0]


def by_nodes():
    want = set()
    with open(os.path.join(DATA, "treatments.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 6)
            if len(p) > 4 and p[4] in TREAT_KINDS:
                want.add(int(p[1]))
    hp = os.path.join(L2, "hunt", "data", "p3_panel.tsv")
    if os.path.exists(hp):
        with open(hp, encoding="utf-8") as f:
            head = f.readline().rstrip("\n").split("\t")
            i = head.index("citing")
            for line in f:
                want.add(int(line.split("\t")[i]))
    return want


def decisions(cols=5):
    with open(os.path.join(DATA, "decisions2.tsv"), encoding="utf-8") as f:
        for line in f:
            r = line.split("\t", cols)
            yield int(r[0]), int(r[1]), int(r[2]), int(r[3]), r[4]


def run_reads(want, out_path, procs, append=False):
    """want: node -> kind; reads every node from git and writes bench3 rows"""
    by = collections.defaultdict(list)
    with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 3)
            k = want.get(int(p[0]))
            if k:
                by[p[1]].append((p[0], p[2], k))
    jobs = []
    for repo, items in by.items():
        for i in range(0, len(items), 4000):
            jobs.append((repo, items[i:i + 4000]))
    jobs.sort(key=lambda x: -len(x[1]))
    n = miss = 0
    part = out_path + ".part"
    with open(part, "w", encoding="utf-8", newline="\n") as fo, ProcessPoolExecutor(procs) as ex:
        for rows in ex.map(one_repo, jobs):
            for r in rows:
                if r is None:
                    miss += 1
                else:
                    fo.write(r)
                    n += 1
    rows = {}
    if append and os.path.exists(out_path):
        for l in open(out_path, encoding="utf-8"):
            rows[int(l.split("\t", 1)[0])] = l
    for l in open(part, encoding="utf-8"):
        node = int(l.split("\t", 1)[0])
        if node in rows:      # keep the earlier kinds
            old = rows[node].split("\t")
            new = l.split("\t")
            new[1] = "".join(sorted(set(old[1] + new[1])))
            l = "\t".join(new)
        rows[node] = l
    with open(part, "w", encoding="utf-8", newline="\n") as f:
        for node in sorted(rows):
            f.write(rows[node])
    os.replace(part, out_path)
    print("read %d decisions, %d missing blobs -> %s (%d rows)" % (n, miss, out_path, len(rows)), flush=True)


def scan1(procs):
    ep, unit_row = load_courts()
    units_of = collections.defaultdict(list)
    for (c, u), k in unit_row.items():
        units_of[c].append((u, k))
    bn = by_nodes()
    groups = collections.defaultdict(list)
    want = {}
    for node, c, d, u, b in decisions():
        if c == SCOTUS:
            continue
        t = epoch_of(ep, c, d)[4]
        if t not in ("L", "A"):
            continue
        if node in bn:
            want[node] = "b"
        if u == 0 and units_alive(units_of, c, d):
            continue
        groups[(c, u, d // 10000)].append((d, node))
    for key, items in groups.items():
        items.sort()
        n = len(items)
        if n <= K_SAMPLE:
            pick = items
        else:
            pick = [items[int(i * n / K_SAMPLE)] for i in range(K_SAMPLE)]
        for _, node in pick:
            want[node] = want.get(node, "") + "s"
    print("step 1: %d decisions (%d overruling, %d court-unit-years)" % (len(want), len(bn & set(want)), len(groups)),
          flush=True)
    run_reads(want, B3, procs)


# ------------------------------------------------------------------------------------------------ the size table
def ordn(d):
    y, m, dd = d // 10000, d // 100 % 100, d % 100
    try:
        return datetime.date(y, m, dd).toordinal()
    except ValueError:
        return datetime.date(min(max(y, 1), 9999), min(max(m, 1), 12), min(max(dd, 1), 28)).toordinal()


def ymd(o):
    d = datetime.date.fromordinal(o)
    return d.year * 10000 + d.month * 100 + d.day


def load_b3():
    rows = {}
    for l in open(B3, encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        fl = dict(x.split("=") for x in p[5].split("|"))
        rows[int(p[0])] = (p[1], [] if p[2] == "-" else p[2].split(","), [] if p[3] == "-" else p[3].split(","),
                           [] if p[4] == "-" else p[4].split(","), fl)
    return rows


def fed_size(circ, d):
    v = None
    for f, n in FED.get(circ, ()):
        if f <= d:
            v = n
    return v


def build_table(write=True):
    """-> sizes: key (court_id of the table) -> (starts[], rows[(from_ord, to_ord, judges, full, datasize)]),
    spans: key -> {year: {judge: [(a, b)]}}"""
    ep, unit_row = load_courts()
    b3 = load_b3()
    dec = collections.defaultdict(list)      # key -> [(ord, year, sit, out)]
    meta = {}
    for node, c, d, u, b in decisions():
        r = b3.get(node)
        if r is None or "s" not in r[0]:
            continue
        key = unit_row.get((c, u), None) if u else c
        if key is None:
            continue
        dec[key].append((ordn(d), d // 10000, r[1], r[2]))
        if key not in meta:
            e = epoch_of(ep, c, d)
            meta[key] = (c, u)
    sizes, spans_all, out_rows = {}, {}, []
    support = {}                 # (key, year) -> sampled decisions naming at least 2 regular judges
    ncy = 0
    for key in sorted(dec):
        items = dec[key]
        cnt = collections.defaultdict(collections.Counter)
        for o, y, sit, out in items:
            for n in sit:
                cnt[y][n] += 1
        regular = collections.defaultdict(set)
        for y, c in cnt.items():
            top = sorted(c.values(), reverse=True)
            ref = top[2] if len(top) >= 3 else top[0]
            thr = max(2, math.ceil(0.3 * ref))
            regular[y] = {n for n, v in c.items() if v >= thr}
        incl = collections.defaultdict(set)
        for y, c in cnt.items():
            for n in c:
                if n in regular[y] or n in regular.get(y - 1, ()) or n in regular.get(y + 1, ()):
                    incl[y].add(n)
        app = collections.defaultdict(list)
        for o, y, sit, out in items:
            for n in sit:
                if n in incl[y]:
                    app[n].append(o)
        # blocks of court activity (a hole of more than HOLE days in the sample ends a block): a judge seen within
        # EDGE days of a block's end is taken to sit to that end, so that the size does not taper where the data stop
        alld = sorted({o for o, y, sit, out in items if sit})
        blocks = []
        for o in alld:
            if blocks and o - blocks[-1][1] <= HOLE:
                blocks[-1][1] = o
            else:
                blocks.append([o, o])
        bstart = [b[0] for b in blocks]

        def widen(a, b):
            ba = blocks[bisect.bisect_right(bstart, a) - 1]
            bb = blocks[bisect.bisect_right(bstart, b) - 1]
            if a - ba[0] <= EDGE:
                a = ba[0]
            if bb[1] - b <= EDGE:
                b = bb[1]
            return (a - MARGIN, b + MARGIN)
        spans = {}
        events = []
        for n, os_ in app.items():
            os_.sort()
            sp = []
            a = b = os_[0]
            for o in os_[1:]:
                if o - b > GAP:
                    sp.append(widen(a, b))
                    a = o
                b = o
            sp.append(widen(a, b))
            spans[n] = sp
            for a, b in sp:
                events.append((a, 1))
                events.append((b + 1, -1))
        if not events:
            continue
        byyear = collections.defaultdict(dict)       # year -> {judge: spans touching the year}
        for n, sp in spans.items():
            for a, b in sp:
                for y in range(datetime.date.fromordinal(a).year, datetime.date.fromordinal(b).year + 1):
                    byyear[y].setdefault(n, []).append((a, b))
        spans_all[key] = byyear
        events.sort()
        # piecewise-constant data size
        pieces = []
        cur, i = 0, 0
        while i < len(events):
            o = events[i][0]
            while i < len(events) and events[i][0] == o:
                cur += events[i][1]
                i += 1
            if pieces and pieces[-1][1] == cur:
                continue
            pieces.append([o, cur])
        # full flag per year
        full = {}
        yy = collections.defaultdict(lambda: [0, 0])
        starts = [p[0] for p in pieces]
        for o, y, sit, out in items:
            reg = regular_at(byyear, o)
            s = len([n for n in sit if n in reg])
            if s >= 2:
                j = bisect.bisect_right(starts, o) - 1
                sz = pieces[j][1] if j >= 0 else 0
                yy[y][1] += 1
                if s + len([n for n in out if n in reg]) >= sz:
                    yy[y][0] += 1
        for y, (a, b) in yy.items():
            full[y] = b >= 5 and a >= 0.6 * b
            support[(key, y)] = b
        ncy += len(cnt)
        # final ranges: split at year boundaries where the full flag changes, apply the federal memory size
        c0, u0 = meta[key]
        e0 = epoch_of(ep, c0, 20000101)
        rows = []
        for j, (o, n) in enumerate(pieces):
            end = pieces[j + 1][0] - 1 if j + 1 < len(pieces) else None
            if n == 0 or end is None:
                continue
            a = o
            while a <= end:
                y = datetime.date.fromordinal(a).year
                b = min(end, datetime.date(y, 12, 31).toordinal())
                fl = 1 if full.get(y) else 0
                e = epoch_of(ep, c0, ymd(a))
                mem = fed_size(e[5], ymd(a)) if (e[3] == 0 and e[4] == "A" and e[5] and c0 not in (655,)) else None
                if mem is not None and fed_size(e[5], ymd(b)) != mem:      # split at a judgeship act
                    nxt = min(ordn(f) for f, _ in FED[e[5]] if f > ymd(a))
                    b = min(b, nxt - 1)
                judges = mem if mem is not None else n
                if rows and rows[-1][1] == a - 1 and rows[-1][2] == judges and rows[-1][3] == fl and rows[-1][5] == mem \
                        and (mem is not None or rows[-1][4] == n):
                    rows[-1][1] = b
                    rows[-1][6][n] += b - a + 1
                else:
                    rows.append([a, b, judges, fl, n, mem, collections.Counter({n: b - a + 1})])
                a = b + 1
        sizes[key] = ([r[0] for r in rows], rows)
        # count decisions per row for src
        nd = [0] * len(rows)
        for o, y, sit, out in items:
            j = bisect.bisect_right(sizes[key][0], o) - 1
            if j >= 0 and rows[j][0] <= o <= rows[j][1]:
                nd[j] += 1
        for j, (a, b, judges, fl, n, mem, days) in enumerate(rows):
            e = epoch_of(ep, c0, ymd(a))
            if mem is not None:
                tot = sum(days.values())
                tag = "S" if 2 * days.get(mem, 0) >= tot else "L"
                acc, med = 0, n
                for v in sorted(days):
                    acc += days[v]
                    if 2 * acc >= tot:
                        med = v
                        break
                src = "mem:authorised=%d;data:regular=%d(%d-%d),n=%d,full=%d" % (mem, med, min(days), max(days), nd[j], fl)
            else:
                lm = LAST.get(e[3]) if (e[4] == "L" and ymd(a) >= 19900101) else None
                tag = "S" if (lm is not None and lm == n) else "U"
                src = "data:regular=%d,n=%d,full=%d" % (n, nd[j], fl) + (";mem:present=%d" % lm if lm else "")
            out_rows.append((key, ymd(a), ymd(b), judges, src, tag))
    if write:
        os.makedirs(PRIV, exist_ok=True)
        p = os.path.join(PRIV, "court_size.tsv")
        with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as f:
            for r in out_rows:
                f.write("%d\t%d\t%d\t%d\t%s\t%s\n" % r)
        os.replace(p + ".tmp", p)
        tags = collections.Counter(r[5] for r in out_rows)
        print("court_size: %d rows, %d courts, %d court-years with sampled judges; tags %s" %
              (len(out_rows), len(sizes), ncy, dict(tags)), flush=True)
    return sizes, spans_all, support


def load_table(path):
    """court_size.tsv -> key -> (starts(yyyymmdd), rows[(from, to, judges, full)])"""
    t = collections.defaultdict(list)
    for l in open(path, encoding="utf-8"):
        k, a, b, n, src, tag = l.rstrip("\n").split("\t")
        m = re.search(r"full=(\d)", src)
        t[int(k)].append((int(a), int(b), int(n), int(m.group(1)) if m else 0))
    return {k: ([r[0] for r in v], v) for k, v in t.items()}


def size_at(tab, key, d):
    x = tab.get(key)
    if not x:
        return None
    j = bisect.bisect_right(x[0], d) - 1
    if j < 0 or not (x[1][j][0] <= d <= x[1][j][1]):
        return None
    return x[1][j]


# ------------------------------------------------------------------------------------------------ step 3 and the rule
def scan3(procs):
    """every panel decision of tier-A courts in a range whose size is <= 3 or that is `full`"""
    ep, unit_row = load_courts()
    tab = load_table(os.path.join(PRIV, "court_size.tsv"))
    have = set()
    for l in open(B3, encoding="utf-8"):
        have.add(int(l.split("\t", 1)[0]))
    want = {}
    for node, c, d, u, b in decisions():
        if b != "panel" or c == SCOTUS:
            continue
        if epoch_of(ep, c, d)[4] != "A":
            continue
        key = unit_row.get((c, u)) if u else c
        r = size_at(tab, key, d) if key is not None else None
        if r and (r[2] <= 3 or r[3]):
            want[node] = "f"
    print("step 3: %d panel decisions in small or full intermediate courts (%d already read)" %
          (len(want), len(have & set(want))), flush=True)
    run_reads(want, B3, procs, append=True)


def regular_at(byyear, o):
    """the regular judges of a court on a day (byyear: year -> {judge: spans})"""
    return {n for n, sp in byyear.get(datetime.date.fromordinal(o).year, {}).items() if any(a <= o <= b for a, b in sp)}


def decide_all():
    """-> list of (node, value, evidence, family, court key) for every scanned decision the rule relabels, and the
    list of scanned panel/unknown decisions it leaves"""
    ep, unit_row = load_courts()
    units_of = collections.defaultdict(list)
    for (c, u), k in unit_row.items():
        units_of[c].append((u, k))
    b3 = load_b3()
    tab = load_table(os.path.join(PRIV, "court_size.tsv"))
    _, spans, support = build_table(write=False)
    change, keep = [], []
    for node, c, d, u, b in decisions():
        r = b3.get(node)
        if r is None or c == SCOTUS:
            continue
        kinds, sit, out, vis, fl = r
        if "b" not in kinds and "f" not in kinds:
            continue
        if b not in ("panel", "unknown"):
            continue
        e = epoch_of(ep, c, d)
        if e[4] not in ("L", "A"):
            continue
        fam = family(e, c)
        if c in DIVISION_UNITS:
            keep.append((node, fam, b, len(sit)))
            continue
        o = ordn(d)
        cands = []
        if u:
            k = unit_row.get((c, u))
            if k is not None:
                cands = [(u, k, False)]
        elif units_alive(units_of, c, d):
            for uu, k in units_alive(units_of, c, d):
                reg = regular_at(spans.get(k, {}), o)
                if len([n for n in sit if n in reg]) >= 2:
                    cands.append((uu, k, True))
            if len(cands) != 1:
                cands = []
        else:
            cands = [(0, c, False)]
        res = None
        for uu, k, matched in cands:
            row = size_at(tab, k, d)
            if not row:
                continue
            size, full = row[2], row[3]
            reg = regular_at(spans.get(k, {}), o)
            s = len([n for n in sit if n in reg])
            x = len([n for n in out if n in reg])
            if s >= 2 and 2 * s > size and s + x >= size and support.get((k, d // 10000), 0) >= MIN_SUPPORT:
                if e[4] == "L" or size <= 3 or full:
                    val = "wholeCourt"
                else:
                    if fl.get("rh") == "1":
                        continue
                    val = "enBanc"
                evd = "size:%d%s/%d%s" % (s, "+%dout" % x if x else "", size, "+u%d" % uu if matched else "")
                res = (node, val, evd, fam, k, b)
        if res:
            change.append(res)
        else:
            keep.append((node, fam, b, len(sit)))
    return change, keep


def family(e, c):
    name, system, tier, circ = e[2], e[3], e[4], e[5]
    if tier == "L":
        return "last"
    if system == 0:
        return "fed"
    if system == 1:
        return "al"
    if system == 18:
        return "la"
    return "state"


def decide():
    change, keep = decide_all()
    os.makedirs(PRIV, exist_ok=True)
    p = os.path.join(PRIV, "relabel.tsv")
    with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        for r in change:
            f.write("%d\t%s\t%s\t%s\t%d\t%s\n" % r)
    os.replace(p + ".tmp", p)
    p = os.path.join(PRIV, "kept.tsv")
    with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        for r in keep:
            f.write("%d\t%s\t%s\t%d\n" % r)
    os.replace(p + ".tmp", p)
    c = collections.Counter((r[3], r[5], r[1]) for r in change)
    print("relabels %d, scanned panel/unknown rows left %d" % (len(change), len(keep)))
    for k, v in sorted(c.items()):
        print("  %s\t%s -> %s\t%d" % (k[0], k[1], k[2], v))


def install_table():
    src = os.path.join(PRIV, "court_size.tsv")
    dst = os.path.join(DATA, "court_size.tsv")
    shutil.copyfile(src, dst + ".tmp")
    os.replace(dst + ".tmp", dst)
    print("installed", dst)


def apply(data_dir=DATA):
    rel = {}
    for l in open(os.path.join(PRIV, "relabel.tsv"), encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        rel[p[0].encode()] = (p[1], p[2])
    src_p = os.path.join(data_dir, "decisions2.tsv")
    tmp = src_p + ".tmp"
    stats = collections.Counter()
    marked = 0
    with open(src_p, "rb") as f, open(tmp, "wb") as fo:
        for line in f:
            n = line[:line.index(b"\t")]
            if b";b:size:" in line:
                marked += 1
            elif n in rel:
                r = line.rstrip(b"\n").split(b"\t")
                val, evd = rel[n]
                s = r[8].decode("utf-8")
                m = re.search(r"(?:^|;)b:([^;]*)(?:;|$)", s)
                old = r[4].decode()
                if old in ("panel", "unknown") and m:
                    s = s[:m.start(1)] + "size:%s+was:%s/%s" % (evd[5:], old, m.group(1)) + s[m.end(1):]
                    r[4] = val.encode()
                    r[8] = s.encode("utf-8")
                    line = b"\t".join(r) + b"\n"
                    stats["%s -> %s" % (old, val)] += 1
            stats["rows"] += 1
            fo.write(line)
    bak = os.path.join(data_dir, "decisions2.pre_round2.tsv")
    if not os.path.exists(bak):
        try:
            os.link(src_p, bak)
        except OSError:
            shutil.copy2(src_p, bak)
    os.replace(tmp, src_p)
    print("input rows already carrying a size marker: %d" % marked)
    for k, v in sorted(stats.items()):
        print("%s\t%d" % (k, v))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    procs = min(24, int(sys.argv[2])) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 8
    if cmd == "scan":
        scan1(procs)
        build_table()
        scan3(procs)
    elif cmd == "scan1":
        scan1(procs)
    elif cmd == "table":
        build_table()
    elif cmd == "scan3":
        scan3(procs)
    elif cmd == "decide":
        decide()
    elif cmd == "install-table":
        install_table()
    elif cmd == "apply":
        apply(sys.argv[2] if len(sys.argv) > 2 else DATA)
    else:
        print(__doc__)
