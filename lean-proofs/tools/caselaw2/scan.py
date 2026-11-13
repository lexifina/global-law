"""One fast pass over one case-law repo: per decision, the sha1 of the file bytes and the header-region signals that
decide bench, publication, form and the intermediate-court unit (caselaw-lean-2, agent: courts).

    python scan.py <repo-name> <in.tsv> <out.tsv>

<in.tsv> holds the repo's nodes (node, path). Every file is read through `git cat-file --batch` (the repos have no
checkout); only signals are written, never text. Output columns (tab-separated, one row per node):

  node, sha1, nbytes, body_len, docket, fm_status, sections, bench, pub, form, unit, judges, decision_type

bench/pub/form/unit are lists of `code=evidence` joined by `|` (evidence: the matched words, at most 60 characters,
tabs/newlines/pipes removed). The header region is the body (front matter excluded) up to
max(2500, end of the head-matter section capped at 4000 + 1500 chars of the first opinion section); the tail region
is the last 1000 characters (CAP prints footnotes, "do not publish" and commission notations at the end).
"""
import hashlib, os, re, subprocess, sys, threading, time

REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")

FM_KEEP = ("court", "docket", "judges", "precedential_status", "decision_type", "citations")


def parse_fm(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm = {}
    for line in text[3:end].splitlines():
        k, sep, v = line.partition(":")
        if sep and k in FM_KEEP:
            fm[k] = v.strip()
    return fm, text[end + 4:]


def ev(s, n=60):
    return re.sub(r"[\t\n\r|=]+", " ", s).strip()[:n]


SEC = re.compile(r"^## (.+)$", re.M)


def sec_kind(h):
    l = h.lower()
    for k, c in (("head matter", "H"), ("cap head matter", "h"), ("majority", "M"), ("plurality", "P"), ("lead", "L"),
                 ("concurrenceinpart", "c"), ("concurring in part", "c"), ("concurrence", "C"), ("dissent", "D"),
                 ("combined", "B"), ("rehearing", "R")):
        if l.startswith(k):
            return c
    return "o"


# ---------------------------------------------------------------- bench
EB = re.compile(r"\b(?:en|in) banc\b|\bin bank\b|\bbanc\b", re.I)
EB_PROSE_OK = re.compile(
    r"sitting en banc|sitting in banc|court,? en banc|court,? in banc|on rehearing en banc|(?:argued|reargued|submitted|"
    r"heard|reheard|considered|decided|resubmitted|re-?argued) (?:and submitted )?(?:en|in) banc|"
    r"(?:we|court) (?:granted|grant|took|take|ordered|heard|hear|sat|sit|voted to rehear|agreed to rehear)[^.]{0,40}"
    r"(?:en|in) banc|rehearing (?:en|in) banc (?:was|has been|is) granted|en banc (?:court|review) (?:was|has been) granted"
    r"|^\s*(?:en|in) banc\b|\bbefore the (?:full |entire )?court,? (?:en|in) banc|\(?(?:en|in) banc\)?\.?\s*$",
    re.I | re.M)
EB_REJECT = re.compile(r"denied|deny|denying|petition for|suggestion|petitions? for rehearing|motion for rehearing en"
                       r"|vacated|pending|poll|dissent(?:ing)? from|request(?:ed)? for|whether to rehear|superseding|"
                       r"unless|absent|until|overrul|bound\b|binding|\bonly\b|\bmay\b|\bcan\b|could|would|prior panel|"
                       r"\bin [A-Z][a-z]+ v\.|\bsee |\bcf\.|affirmed by|reversed by|decision in|opinion in", re.I)
EB_CITE_AFTER = re.compile(r"^\)?,?\s*(?:\d+ [A-Z][\w.' ]{0,12}\d|\d{3,4}\))")
EB_CITE_BEFORE = re.compile(r"(?:\d{4}\)|Cir\.|[A-Z][a-z]+\.(?: \d+)?|aff'?d|rev'?d|cert\.|App\.|\(Mo\.|Mo\.)\s*\(?$")
CIRC = re.compile(r"(?:this|the (?:present|foregoing|panel(?:'s)?)|our) (?:panel )?(?:opinion|decision)[^.]{0,120}?"
                  r"(?:has been|was|were|have been) circulated (?:among|to) (?:all|the full|the entire|each|every|the "
                  r"active)|Circuit Rule 40\(e\)|7th Cir(?:cuit|\.)? R(?:ule|\.) 40\(e\)|Irons footnote|circulated to "
                  r"the (?:full|entire|en banc) court(?:[^.]{0,80})(?:no judge|none of the judges|no active judge)",
                  re.I)
CONFLICT = re.compile(r"\b(?:special|conflict) panel\b[^.]{0,200}?(?:7\.215|convened)|convened (?:a )?(?:special|conflict)"
                      r" panel|MCR 7\.215\((?:I|J)\)\((?:3|5)\)", re.I)
DIVISION = re.compile(r"^\s*(?:In )?(?:Department|Dept\.|Division|Div\.)\s+(?:No\.\s*)?(?:One|Two|Three|Four|Five|Six|"
                      r"[1-6]|I{1,3}|IV|V|VI)\b\.?\s*$|^\s*(?:First|Second|Third|Fourth|Fifth|Sixth) (?:Department|"
                      r"Division)\.?\s*$", re.M)
WHOLE = re.compile(r"\b(?:whole|full) court\b", re.I)
BEFORE = re.compile(r"(?:^|\n)\s*(?:Before|BEFORE|Present|PRESENT)\s*[:\-—–]?\s*(.{5,700}?)(?:\.\s*\n|\n\s*\n|$)",
                    re.S)


def judges_in(s):
    s = re.sub(r"\*|\[\d+\]|\(.*?\)", " ", s)
    s = re.sub(r"\b(?:Chief|Senior|Circuit|District|Associate|Presiding|Acting|Retired|Judges?|Justices?|JJ?|C\.?J|P\.?J|"
               r"Magistrate|Bankruptcy|Hon(?:orable)?|the|The|U\.S\.|United States|sitting by designation|Court|Appeals|"
               r"of|for|Circuit|Ret|Jr|Sr|III|II|Panel|No|Opinion|by)\b\.?", " ", s)
    parts = [p.strip(" .;:") for p in re.split(r",|\band\b|&|;", s)]
    return [p for p in parts if re.search(r"[A-Za-z]{3,}", p)]


def bench_codes(hdr, fmj, court, short_lines):
    out = []
    if re.search(r"\b(?:en|in) banc\b", fmj, re.I) and not EB_REJECT.search(fmj):
        out.append("eb_fm=" + ev(fmj))
    for m in EB.finditer(hdr):
        a, b = m.start(), m.end()
        ls = hdr.rfind("\n", 0, a) + 1
        le = hdr.find("\n", b)
        le = len(hdr) if le < 0 else le
        line = hdr[ls:le]
        ctx = hdr[max(ls, a - 70):min(le, b + 50)]
        if EB_REJECT.search(ctx):
            continue
        if EB_CITE_AFTER.search(hdr[b:b + 25]) or EB_CITE_BEFORE.search(hdr[max(0, a - 18):a]):
            continue
        if m.group(0).lower() in ("banc",) and not re.search(r"\bbanc\b", line[:40], re.I):
            continue
        short = len(line.strip()) <= 90
        if short or EB_PROSE_OK.search(ctx):
            out.append(("eb_line=" if short else "eb_prose=") + ev(ctx))
            break
    m = CIRC.search(hdr)
    if m:
        out.append("circ=" + ev(m.group(0)))
    m = CONFLICT.search(hdr)
    if m:
        out.append("conflict=" + ev(m.group(0)))
    m = DIVISION.search(hdr[:1500])
    if m:
        out.append("div=" + ev(m.group(0)))
    for m in WHOLE.finditer(hdr[:2500]):
        ls = hdr.rfind("\n", 0, m.start()) + 1
        le = hdr.find("\n", m.end())
        line = hdr[ls:le if le >= 0 else len(hdr)].strip()
        ctx = hdr[max(0, m.start() - 50):m.end() + 30]
        if EB_REJECT.search(ctx) or '"' in ctx or "“" in ctx:
            continue
        if len(line) <= 90 or re.search(r"(?:considered|decided|heard|determined|submitted) by the (?:whole|full) court|"
                                        r"the (?:whole|full) court (?:sitting|concurs|concur)", ctx, re.I):
            out.append("whole=" + ev(ctx))
            break
    m = BEFORE.search(hdr[:6000])
    if m:
        out.append("nbefore=%d" % len(judges_in(m.group(1))))
    elif fmj:
        b = re.search(r"Before:?\s*(.+)", fmj)
        if b:
            out.append("nbefore=%d" % len(judges_in(b.group(1))))
    return out


# ---------------------------------------------------------------- publication
PUB_CAPS = re.compile(r"NOT (?:DESIGNATED |RECOMMENDED )?FOR (?:FULL[- ]TEXT |OFFICIAL )?PUBLICATION|NOT TO BE (?:OFFICIALLY )?"
                      r"PUBLISHED|DO NOT PUBLISH|NONPRECEDENTIAL|NON-PRECEDENTIAL|NOT PRECEDENTIAL|UNPUBLISHED|"
                      r"NOT FOR PUBLICATION|UNREPORTED|NOT REPORTED|NON-PUBLISHED|NOT RECOMMENDED FOR PUBLICATION|"
                      r"NOT FOR OFFICIAL PUBLICATION|NO PRECEDENTIAL VALUE")
PUB_SENT = re.compile(
    r"(?:this|the) (?:opinion|decision|disposition|order|memorandum|judgment)[^.]{0,40}? (?:is|was|has been|will be|"
    r"shall be) (?:not )?(?:designated |deemed )?(?:not (?:designated |appropriate |intended |recommended |selected )?"
    r"(?:for|to be) (?:full[- ]text |official )?publi(?:cation|shed)|unpublished|nonprecedential|non-precedential|"
    r"not precedential|not precedent)|"
    r"(?:court|panel) has determined that this (?:opinion|decision) should not be published|"
    r"Rule 47\.5|R\. 47\.5|Rule 36-3|R\. 36-3|Rule 32\.1A|Rule 1:28|Rule 23\.0\b|Rule 23\(b\)|Supreme Court Rule 23\b|"
    r"may not be cited (?:as precedent|except)|is not (?:to be )?cited as precedent|not to be cited as precedent|"
    r"(?:Do|do) [Nn]ot [Pp]ublish|Not [Ff]or [Pp]ublication|Not [Tt]o [Bb]e [Pp]ublished|"
    r"Not [Pp]recedential|Non-?[Pp]recedential (?:[Dd]ecision|[Oo]pinion|[Dd]isposition)|Unpublished (?:[Oo]pinion|"
    r"[Dd]isposition|[Dd]ecision)\s*$|[Uu]npublished [Oo]pinions? (?:are|is) not (?:binding )?precedent|"
    r"unpublished dispositions? (?:is|are) (?:disfavored|unfavored|not)|citation of unpublished dispositions|"
    r"CERTIFIED FOR PARTIAL PUBLICATION|[Cc]ertified for [Pp]artial [Pp]ublication", re.M)
PUB_POS = re.compile(r"(?<!NOT )(?<!NOT RECOMMENDED )\bFOR PUBLICATION\b|(?<!UN)(?<!NON-)(?<!NON)\bPUBLISHED (?:OPINION)?\s*$|"
                     r"^\s*(?<!NON-)(?<!NON)PRECEDENTIAL\s*$|CERTIFIED FOR PUBLICATION|RECOMMENDED FOR (?:FULL-TEXT )?"
                     r"PUBLICATION", re.M)
SUMMARY_ORDER = re.compile(r"\bSUMMARY ORDER\b|RULINGS BY SUMMARY ORDER DO NOT HAVE PRECEDENTIAL EFFECT")
TABLE = re.compile(r"Table of Decisions|\([Tt]able\)|Decisions? Without (?:Published|Reported) Opinions?|Table Decisions? "
                   r"Without|Unpublished Disposition|^\s*TABLE\s*$", re.M)
MEMO_PUB = re.compile(r"T\.\s?C\. Memo\.?|\bRule 1:28\b|MEMORANDUM AND ORDER PURSUANT TO RULE|SUMMARY DISPOSITION|"
                      r"MEMORANDUM (?:OPINION|DECISION)|^\s*MEMORANDUM\s*\**\s*$|R\.A\.P\. 21|Rule 21 of the Rules of "
                      r"Appellate Procedure|MEMORANDUM DECISION|Memorandum Decision\s*$|Memorandum Opinion\s*$", re.M)


def pub_codes(hdr, tail, fm, cites):
    out = []
    for nm, rx in (("caps", PUB_CAPS), ("sent", PUB_SENT)):
        for zone, txt in (("h", hdr), ("t", tail)):
            m = rx.search(txt)
            if m:
                ctx = txt[max(0, m.start() - 40):m.end() + 40]
                out.append("unpub_%s_%s=%s" % (nm, zone, ev(ctx)))
                break
    m = PUB_POS.search(hdr[:2500])
    if m:
        out.append("pubpos=" + ev(hdr[max(0, m.start() - 10):m.end() + 10]))
    m = SUMMARY_ORDER.search(hdr) or SUMMARY_ORDER.search(tail)
    if m:
        out.append("sumord=" + ev(m.group(0)))
    m = TABLE.search(hdr[:1500])
    if m:
        out.append("table=" + ev(hdr[max(0, m.start() - 30):m.end() + 30]))
    m = MEMO_PUB.search(hdr[:3000])
    if m:
        out.append("memo=" + ev(hdr[max(0, m.start() - 20):m.end() + 30]))
    if re.search(r"F\. ?App'?x|Fed\. ?App(?:x|'x)", cites):
        out.append("fappx=1")
    if re.search(r"\(table\)|\btable\b", cites, re.I):
        out.append("citetable=1")
    return out


# ---------------------------------------------------------------- form
PER_CURIAM = re.compile(r"\bper curiam\b", re.I)
PLUR = re.compile(r"[A-Z][A-Za-z'.\-]+(?:,)? (?:C\. ?J\.|J\.|Justice|Chief Justice|JUSTICE|CHIEF JUSTICE)[,]? announced the "
                  r"judgment of the [Cc]ourt|delivered an opinion announcing the judgment|(?<!\()(?<!\(opinion of )"
                  r"[Oo]pinion announcing (?:the )?judgment of the [Cc]ourt|announced the judgment of the [Cc]ourt and "
                  r"(?:delivered|filed) an opinion|^\s*PLURALITY OPINION|^\s*Plurality [Oo]pinion|"
                  r"opinion of the [Cc]ourt with respect to Parts?")
EQDIV = re.compile(r"(?:affirmed|affirms?|is affirmed|stands affirmed|be affirmed)(?: by| by an?| by the)? (?:an )?(?:equally|evenly)"
                   r" divided (?:court|vote|bench)|(?:court|justices|judges|members of the court) (?:being |is |are |was |were )?"
                   r"(?:equally|evenly) divided|(?:equally|evenly) divided court", re.I)
SUMAFF = re.compile(r"\bjudgment (?:is |be |of the [^.]{0,60} is )?affirmed\b|^\s*(?:Per Curiam: )?Affirmed\.?\s*$|"
                    r"want of (?:a )?(?:substantial |properly presented )?federal question|motion to affirm is granted", re.I | re.M)
CERTQ = re.compile(r"certified questions?|questions? (?:of law )?(?:was |were |has been |have been )?certified|"
                   r"certification of questions?|upon certification|on certification|certifying court|"
                   r"answer(?:ing)? (?:the |a )?(?:certified )?questions?", re.I)
FEDCT = re.compile(r"United States (?:Court of Appeals|District Court|Bankruptcy Court|Supreme Court)|(?:First|Second|Third|"
                   r"Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Federal|D\.C\.) Circuit|\b\d{1,2}(?:st|nd|rd|th)"
                   r" Cir\.|U\.S\. District Court|federal (?:district )?court|Court of Appeals for the", re.I)
MEMO_FORM = re.compile(r"^\s*MEMORANDUM(?: OPINION| DECISION| AND ORDER| ORDER)?\s*\**\s*$|^\s*Memorandum(?: Opinion| Decision)?"
                       r"[:.]?\s*$|^\s*Memorandum[:.]\s|T\.\s?C\. Memo\.?|^\s*MEMORANDUM OPINION\b", re.M)
COMM = re.compile(r"(?:Opinion|Holding|Judgment|OPINION|HOLDING|JUDGMENT)s? (?:of the Commission of Appeals )?(?:is |are )?"
                  r"(?:adopted|approved|ADOPTED|APPROVED)(?:,? and judgment (?:adopted|approved|rendered))?|"
                  r"is (?:hereby )?adopted as the opinion of the [Cc]ourt|ADOPTED AS THE OPINION OF THE COURT")


def form_codes(hdr, tail, first_title, first_sec_text, sec_kinds, body_len, op_len, court):
    out = []
    if PER_CURIAM.search(first_title) or PER_CURIAM.search(first_sec_text[:300]):
        out.append("pc=" + ev(first_title or first_sec_text[:40]))
    if "P" in sec_kinds or "L" in sec_kinds:
        out.append("plur_sec=" + sec_kinds)
    m = PLUR.search(hdr)
    if m:
        ctx = hdr[max(0, m.start() - 40):m.end() + 20]
        if "(opinion of" not in ctx and "(plurality" not in ctx:
            out.append("plur_txt=" + ev(ctx))
    for zone, txt in (("h", hdr), ("t", tail)):
        m = EQDIV.search(txt)
        if m:
            ctx = txt[max(0, m.start() - 60):m.end() + 25]
            if not re.search(r"aff'?d|, \d+ (?:U\.S\.|F\.|S\. ?Ct)", ctx):
                out.append("eqdiv_%s=%s" % (zone, ev(ctx)))
                break
    if op_len < 1500:
        m = SUMAFF.search(hdr + "\n" + tail)
        if m:
            out.append("sumaff=" + ev(m.group(0)))
    m = CERTQ.search(hdr)
    if m:
        ctx = hdr[max(0, m.start() - 250):m.end() + 250]
        f = FEDCT.search(ctx)
        out.append(("certq_fed=" if f else "certq=") + ev(hdr[max(0, m.start() - 30):m.end() + 20]))
    m = MEMO_FORM.search(hdr[:3000])
    if m:
        out.append("memo=" + ev(m.group(0)))
    m = COMM.search(tail)
    if m:
        out.append("comm=" + ev(tail[max(0, m.start() - 30):m.end() + 30]))
    return out


# ---------------------------------------------------------------- units
ORDW = (r"First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|"
        r"Fifteenth|1st|2nd|2d|3rd|3d|4th|5th|6th|7th|8th|9th|10th|11th|12th|13th|14th|15th")
UNIT_PHR = re.compile(r"\b(%s)\s+(Appellate District|District|Department|Division|Circuit|Court of (?:Civil )?Appeals|"
                      r"Supreme Judicial District|Judicial District|Dist\.|Dept\.)" % ORDW)
UNIT_PHR2 = re.compile(r"\b(District|Division|Department) (One|Two|Three|Four|Five|Six|Seven|Eight|I{1,3}|IV|V|VI|VII|VIII|"
                       r"[1-8])\b")
COUNTY = re.compile(r"\b((?:[A-Z][a-z]+|St\.|De|La|Mc[A-Z][a-z]+)(?: (?:[A-Z][a-z]+|St\.|Lucie|Johns))?) (County|Parish)\b")
UNITAB = re.compile(r"\bUnit (A|B)\b")
CITYS = re.compile(r"\b(Houston|Dallas|Fort Worth|Austin|San Antonio|Texarkana|Amarillo|El Paso|Beaumont|Waco|Eastland|"
                   r"Tyler|Corpus Christi|Galveston|Edinburg)\b")


def unit_codes(hdr, court):
    out = []
    zone = hdr[:3000]
    seen = 0
    for m in UNIT_PHR.finditer(zone):
        a = m.start()
        ls = zone.rfind("\n", 0, a) + 1
        le = zone.find("\n", m.end())
        le = len(zone) if le < 0 else le
        line = zone[ls:le]
        cite = bool(re.search(r"\(\s*[A-Z][a-z]+\.?[^()]{0,30}$", zone[max(ls, a - 40):a])) or \
            bool(re.search(r"^[^()]{0,25}\d{4}\)", zone[m.end():m.end() + 30])) or "—" in zone[max(ls, a - 30):a] \
            or "[" in zone[max(ls, a - 3):a]
        out.append("ph=%s %s@%d%s%s" % (m.group(1), m.group(2), a, "s" if len(line.strip()) <= 100 else "",
                                         "c" if cite else ""))
        seen += 1
        if seen >= 4:
            break
    m = UNIT_PHR2.search(zone)
    if m:
        out.append("ph2=%s %s@%d" % (m.group(1), m.group(2), m.start()))
    cs = []
    for m in COUNTY.finditer(hdr[:2500]):
        c = m.group(1) + " " + m.group(2)
        if c not in cs:
            cs.append(c)
        if len(cs) >= 3:
            break
    if cs:
        out.append("county=" + ";".join(ev(c, 40) for c in cs))
    m = UNITAB.search(hdr[:4000])
    if m:
        out.append("unitab=" + m.group(1))
    m = CITYS.search(hdr[:800])
    if m:
        out.append("city=" + m.group(1))
    return out


# ---------------------------------------------------------------- judges
JSTOP = set("""BEFORE PRESENT CONCUR CONCURS CONCURRING CONCURRED DISSENT DISSENTS DISSENTING JUDGE JUDGES JUSTICE JUSTICES
CHIEF PRESIDING ASSOCIATE ACTING SENIOR CIRCUIT DISTRICT COURT APPEALS AND THE OPINION PER CURIAM CURIAM MR MRS MS HON
HONORABLE PANEL CONSISTS OF CONSISTING JJ SPECIAL SPECIALLY ALL DELIVERED BY FOR WITH WHOM JOIN JOINS JOINED RESULT ONLY
PART IN NOT PARTICIPATING SITTING DESIGNATION RETIRED FULLY STATE STATES UNITED ORDER MEMORANDUM DECISION WRITTEN
ENTERED FILED AUTHOR DISQUALIFIED TAKING NO VOTING ABSENT OPINION PRO TEM TEMPORE ASSIGNED ALSO FURTHER BELOW COMMISSIONER
COMMISSIONERS SECTION DIVISION DEPARTMENT JUDGMENT AFFIRMED REVERSED EN BANC HIS HER SEPARATE SEPARATELY WRITING WRITES
DECIDED ARGUED SUBMITTED COMPOSED COURTS EXCEPT WHO THAT THIS TOOK ARE WAS ALSO ADMINISTRATIVE CONCURRENCE NONE
MAJORITY COMBINED LEAD PLURALITY FACTUAL PROCEDURAL BACKGROUND REHEARING DENIED GRANTED MISC JANUARY FEBRUARY MARCH APRIL
MAY JUNE JULY AUGUST SEPTEMBER OCTOBER NOVEMBER DECEMBER COMMISSION SUPREME SUMMARY CALENDAR PETITION HEARD ORAL ARGUMENT
STATEMENT FACTS CASE OPINIONS AFFIRM REVERSE REMAND REMANDED DISMISSED MOTION APPEAL APPELLANT APPELLEE INTRODUCTION
DISCUSSION CONCLUSION ANALYSIS ISSUE ISSUES MEMBERS VACATED MODIFIED""".split())
JTOK = re.compile(r"\b(?:Mc|Mac|O')?[A-Z][A-Za-z'\-]{2,}\b")


def judge_tokens(*strs):
    out = []
    for s in strs:
        for t in JTOK.findall(s):
            u = t.upper().replace("'", "")
            if u in JSTOP or len(u) < 3:
                continue
            if u not in out:
                out.append(u)
            if len(out) >= 12:
                return out
    return out


PRESENT = re.compile(r"(?:Present|Concur|PRESENT|CONCUR)\s*[—–\-:]+\s*([^\n]{3,300})")


def process(text, court_hint=""):
    fm, body = parse_fm(text)
    b = body.lstrip("\n")
    if b.startswith("# "):
        nl = b.find("\n")
        b = b[nl + 1:] if nl >= 0 else ""
    secs = [(m.start(), m.end(), m.group(1)) for m in SEC.finditer(b)]
    kinds = "".join(sec_kind(h) for _, _, h in secs)
    hm_end = 0
    first_title, first_text = "", b[:2000]
    op_len = len(b)
    for i, (s, e, h) in enumerate(secs):
        k = sec_kind(h)
        nxt = secs[i + 1][0] if i + 1 < len(secs) else len(b)
        if k in "Hh":
            hm_end = min(nxt, s + 4000)
        elif not first_title:
            first_title = h
            first_text = b[e:nxt].lstrip()
            op_len = sum((secs[j + 1][0] if j + 1 < len(secs) else len(b)) - secs[j][1]
                         for j in range(i, len(secs)) if sec_kind(secs[j][2]) not in "Hh")
    lim = max(2500, hm_end + 1500) if hm_end else 2500
    hdr = b[:lim]
    tail = b[-1000:] if len(b) > lim else ""
    fmj = fm.get("judges", "")
    cites = fm.get("citations", "")
    pres = PRESENT.search(hdr) or PRESENT.search(tail or "")
    toks = judge_tokens(first_title, fmj, pres.group(1) if pres else "")
    return [
        ev(fm.get("docket", "").strip('"'), 80),
        ev(fm.get("precedential_status", "").strip('"'), 20) or "-",
        kinds or "-",
        "|".join(bench_codes(hdr, fmj, court_hint, None)) or "-",
        "|".join(pub_codes(hdr, tail, fm, cites)) or "-",
        "|".join(form_codes(hdr, tail, first_title, first_text, kinds, len(b), op_len, court_hint)) or "-",
        "|".join(unit_codes(hdr, court_hint)) or "-",
        " ".join(toks) or "-",
        ev(fm.get("decision_type", "").strip('"'), 30) or "-",
    ], len(b), op_len


def main(repo, inp, out):
    t0 = time.time()
    rd = os.path.join(REPOS, repo)
    want = []
    for line in open(inp, encoding="utf-8"):
        n, p = line.rstrip("\n").split("\t")
        want.append((n, p))
    tree = subprocess.run(["git", "-C", rd, "ls-tree", "-r", "HEAD", "--", "decisions"], capture_output=True,
                          check=True).stdout.decode("utf-8")
    sha_of, order = {}, {}
    for i, line in enumerate(tree.splitlines()):
        meta, path = line.split("\t", 1)
        if path.startswith('"'):
            path = path[1:-1].encode("latin-1", "backslashreplace").decode("unicode_escape").encode("latin-1").decode("utf-8")
        sha_of[path] = meta.split()[2]
        order[path] = i
    items = []
    missing = []
    for n, p in want:
        if p in sha_of:
            items.append((order[p], n, sha_of[p]))
        else:
            missing.append((n, p))
    items.sort()
    p = subprocess.Popen(["git", "-C", rd, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         creationflags=0x08000000 if os.name == "nt" else 0)

    def feed():
        for _, _, sha in items:
            p.stdin.write((sha + "\n").encode())
        for _, path in missing:
            p.stdin.write(("HEAD:" + path + "\n").encode("utf-8"))
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    tmp = out + ".part"
    nb = 0
    with open(tmp, "w", encoding="utf-8", newline="\n") as fo:
        for node in [x[1] for x in items] + [x[0] for x in missing]:
            header = p.stdout.readline().split()
            if len(header) < 3 or header[1] == b"missing":
                fo.write("\t".join([node, "-", "0", "0"] + ["-"] * 9) + "\n")
                continue
            size = int(header[2])
            data = p.stdout.read(size)
            p.stdout.read(1)
            nb += size
            sha = hashlib.sha1(data).hexdigest()
            text = data.decode("utf-8", "replace")
            cols, blen, oplen = process(text)
            fo.write("\t".join([node, sha, str(size), str(oplen)] + cols) + "\n")
    p.wait()
    os.replace(tmp, out)
    dt = time.time() - t0
    n = len(items) + len(missing)
    print("%s\tfiles %d\tmissing_path %d\tMB %.0f\tsec %.1f\tfiles/s %.0f" % (repo, n, len(missing), nb / 1e6, dt,
                                                                              n / max(dt, 1e-9)), flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:4])
