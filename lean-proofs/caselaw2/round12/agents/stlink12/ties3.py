"""stlink12: a third identity tie between a state court-of-last-resort opinion D and an intermediate decision T for
pairs matched on full party names only (no docket / citation / date of T printed in D). Each test is a normalised
token match between a stated text part of each node; texts are the decisions' own files (front matter + opinion).

    strict_names(nd)           -> the full-name entities that are real names (role phrases, "X et al" dropped)
    judge_tie(D, T)            -> trial judge surname named in both bodies (Judge X / the Honorable X / X, Judge,
                                  presiding / trial judge X); appellate judges of either court and party surnames
                                  excluded
    county_tie(D, T)           -> the trial court's county named in both bodies ("<court> Court of X County",
                                  "X County <court> Court", "Circuit Court for X County")
    tdocket_tie(D, T)          -> a lower-court docket token printed in both bodies (No./Case No./Cause No./
                                  Indictment No./Docket No. + compact token >= 4 chars with a digit), not the docket
                                  of D or of T
    fdate_tie(D, T)            -> a full calendar date printed in both bodies other than D's and T's decision dates
                                  (the date of the events / trial / judgment below)
    author_tie(D, T)           -> T's author (its majority header) named in D's body as a judge of the court below
                                  ("Judge X", "X, J.", "X, Judge", "Justice X", "X, P.J.", "X writing"), not a member
                                  of D's court
D and T are dicts from ties.parse(text).
"""
import re

import ties

NL = chr(10)
ROLEW = re.compile(r"^(?:plaintiffs?|defendants?|appellants?|appellees?|respondents?|petitioners?|cross|and|in|error|"
                   r"third|party|intervenors?|claimants?|movants?|relators?|counter|real|parties|interest|the|et|al|"
                   r"ux|vir|re|ex|parte|matter|of|estate)$", re.I)
COMMONSUR = {"smith", "johnson", "williams", "brown", "jones", "miller", "davis", "wilson", "anderson", "taylor",
             "thomas", "moore", "martin", "jackson", "thompson", "white", "harris", "clark", "lewis", "robinson",
             "walker", "young", "allen", "king", "wright", "scott", "hill", "green", "adams", "baker", "hall",
             "nelson", "carter", "mitchell", "roberts", "turner", "phillips", "campbell", "parker", "evans",
             "edwards", "collins", "stewart", "morris", "murphy", "cook", "rogers", "lee", "garcia", "rodriguez",
             "martinez", "hernandez", "lopez", "gonzalez", "perez", "sanchez", "ramirez", "torres"}


def strict_names(nd):
    """entities from names_tie's detail that are real names: an organisation with >= 2 content words, or a person
    with a given name (not an initial) and a surname, both not role words."""
    out = []
    for e in [x for x in (nd or "").split("|") if x]:
        e2 = re.sub(r"\b(?:et\s+al|et\s+ux|et\s+vir)\b\.?", " ", e, flags=re.I)
        e2 = re.sub(r"^\s*(?:in\s+re|ex\s+parte|matter\s+of|in\s+the\s+matter\s+of)\s+", "", e2, flags=re.I)
        e2 = re.split(r"\.\s+(?:ex\s+parte|in\s+re)\b", e2, flags=re.I)[0]
        ws = re.findall(r"[A-Za-z][A-Za-z'\-]*", e2)
        if not ws or all(ROLEW.match(w) for w in ws):
            continue
        if ties.is_org(e2):
            k = [w for w in ties.org_key(e2).split() if len(w) > 1]
            if len(k) >= 2:
                out.append(e.strip())
            continue
        pk, _sur = ties.person_key(e2)
        if pk and not ROLEW.match(pk[0]) and not ROLEW.match(pk[1]) and len(pk[1]) >= 2:
            out.append(e.strip())
    return out


NAME = r"(?-i:([A-Z][A-Za-z'\-]+(?:\s+(?:[A-Z]\.\s*)+)?(?:\s+[A-Z][A-Za-z'\-]+){0,2}))"
JUDGE_RX = [
    re.compile(r"\b(?:the\s+)?Hon(?:orable|\.)\s+" + NAME),
    re.compile(r"\b(?:trial|district|circuit|superior\s+court|county|probate|chancery|juvenile|family|municipal|"
               r"associate|special|presiding|sentencing|motion|hearing)\s+(?:court\s+)?judge,?\s+" + NAME, re.I),
    re.compile(r"\bJudge\s+" + NAME),
    re.compile(r"\b([A-Z][A-Za-z'\-]{2,}),\s+(?:J\.|Judge|Chancellor|Special\s+Judge)\s*,?\s*(?:presiding|\))"),
    re.compile(r"\bChancellor\s+" + NAME),
]
STOPJ = {"the", "of", "court", "appeals", "district", "circuit", "county", "superior", "supreme", "trial", "and",
         "presiding", "judge", "justice", "honorable", "hon", "jr", "sr", "ii", "iii", "state", "for", "in", "who",
         "below", "which", "that", "was", "had", "has", "did", "erred", "granted", "denied", "found", "ruled",
         "held", "entered", "stated", "said", "concluded", "noted", "instructed", "refused", "sustained",
         "overruled", "admitted", "allowed", "then", "also", "thereafter", "here", "when", "case", "court's"}


def judge_names(body):
    out = set()
    for rx in JUDGE_RX:
        for m in rx.finditer(body):
            toks = [t for t in re.findall(r"[A-Za-z][A-Za-z'\-]+", m.group(1)) if t.lower() not in STOPJ]
            if not toks:
                continue
            sur = toks[-1].lower()
            if len(sur) >= 4:
                out.add(sur)
    return out


def court_judges(front, body):
    """surnames of the deciding court's own judges: front `judges`, the opinion part headers."""
    s = " ".join(front.get("judges") or []) if isinstance(front.get("judges"), list) else str(front.get("judges") or "")
    hdr = " ".join(re.findall(r"^## [^\n]*", body, re.M))
    return {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z'\-]{2,}", s + " " + hdr)}


def party_tokens(front):
    p = front.get("parties")
    p = " ".join(p) if isinstance(p, list) else str(p or "")
    return {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z'\-]{2,}", p)}


def judge_tie(D, T):
    excl = court_judges(D["front"], D["body"]) | court_judges(T["front"], T["body"]) | \
        party_tokens(D["front"]) | party_tokens(T["front"])
    a = judge_names(D["body"]) - excl
    b = judge_names(T["body"]) - excl
    return sorted(a & b)


CT = r"(?:circuit|district|superior|county|common\s+pleas|chancery|probate|family|juvenile|criminal|municipal|" \
     r"orphans'?|surrogate'?s?|justice|city|parish|trial)"
CNAME = r"(?-i:([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}))"
COUNTY_RX = [
    re.compile(r"\b" + CNAME + r"\s+(?:County|Parish)\s+(?:" + CT + r")\s+Court\b", re.I),
    re.compile(r"\b(?:" + CT + r")\s+Courts?\s+(?:of|for|in)\s+(?:the\s+)?(?:County\s+of\s+)?" + CNAME +
               r"(?:\s+(?:County|Parish))?\b", re.I),
]
CSTOP = {"the", "said", "this", "that", "each", "any", "same", "our", "its", "his", "her", "appeals", "appeal",
         "state", "united", "states", "judicial", "first", "second", "third", "fourth", "fifth", "sixth", "seventh",
         "eighth", "ninth", "tenth", "eleventh", "twelfth", "district", "circuit", "county", "which", "where"}


def counties(body):
    out = set()
    for rx in COUNTY_RX:
        for m in rx.finditer(body):
            name = m.group(1)
            ws = [w.lower() for w in name.split()]
            # Circuit Court of X County: the county must be followed by County/Parish unless the form is "County of X"
            if rx is COUNTY_RX[1] and not re.search(r"(?:County|Parish)\s*$", m.group(0)) and \
                    not re.search(r"County\s+of\s+", m.group(0), re.I):
                continue
            while ws and ws[0] in CSTOP:
                ws = ws[1:]
            if ws and not any(w in CSTOP for w in ws):
                out.add(" ".join(ws))
    return out


def county_tie(D, T):
    return sorted(counties(D["body"]) & counties(T["body"]))


TDK_RX = re.compile(r"\b(?:Case|Cause|Indictment|Information|Docket|Criminal|Civil|Action|Complaint|Index|File|Trial\s+Court)?"
                    r"\s*(?:Nos?\.|Numbers?|#)\s*([A-Za-z0-9][A-Za-z0-9\-/:.]*\d[A-Za-z0-9\-/:.]*)", re.I)


def docket_like(body):
    out = set()
    for m in TDK_RX.finditer(body):
        c = ties.compact(m.group(1).rstrip(".:-/"))
        if len(c) >= 4 and re.search(r"\d", c) and not re.fullmatch(r"(?:1[6-9]|20)\d\d", c):
            out.add(c)
    return out


def tdocket_tie(D, T):
    own = set(ties.docket_tokens(D["front"].get("docket"))) | set(ties.docket_tokens(T["front"].get("docket")))
    # strip statute / rule numbers that also follow "No.": a token shared with a cites_cases entry is not a docket
    cites = {ties.compact(c) for c in (D["front"].get("cites_cases") or []) + (T["front"].get("cites_cases") or [])
             if isinstance(c, str)}
    hit = (docket_like(D["body"]) & docket_like(T["body"])) - own
    return sorted(h for h in hit if not any(h in c for c in cites))


def fdate_tie(D, T):
    dd = ties.t_date(D["front"])
    td = ties.t_date(T["front"])
    a = ties.dates_in(D["body"])
    b = ties.dates_in(T["body"])
    # the first of a month is left out (effective dates of statutes / rules shared by unrelated cases)
    return sorted(x for x in (a & b) if x != dd and x != td and x[2] != 1)


AUTH_RX = re.compile(r"^## (?:Majority|Per\s+Curiam|Opinion)[^\n]*?\(([^)\n]+)\)", re.M)


def t_author(T):
    m = AUTH_RX.search(T["body"])
    if not m:
        return None
    head = m.group(1).split(",")[0]
    toks = [t for t in re.findall(r"[A-Za-z][A-Za-z'\-]+", head) if t.lower() not in STOPJ and
            t.lower() not in ("j", "p", "c", "pj", "cj", "per", "curiam", "chief", "associate", "senior", "acting")]
    if not toks:
        return None
    caps = [t for t in toks if t.isupper() and len(t) > 1]
    s = (caps[-1] if caps else toks[-1]).lower()
    return s if len(s) >= 4 else None


def author_tie(D, T):
    a = t_author(T)
    if not a or a in party_tokens(D["front"]) or a in court_judges(D["front"], D["body"]):
        return ""
    A = re.escape(a)
    rx = re.compile(r"(?i:\b(?:judge|justice|chief\s+judge|presiding\s+judge|presiding\s+justice)\s+(?:[A-Z]\.\s*)*)" + A + r"\b"
                    r"|\b" + A + r",\s*(?:J\.|P\.\s?J\.|C\.\s?J\.|Judge|JJ\.)"
                    r"|\b" + A + r"\b[^.\n]{0,40}\bwriting\b", re.I)
    return a if rx.search(D["body"]) else ""


def all_ties(D, T):
    out = {}
    jt = judge_tie(D, T)
    if jt:
        out["judge"] = jt[0]
    ct = county_tie(D, T)
    if ct:
        out["county"] = ct[0]
    dk = tdocket_tie(D, T)
    if dk:
        out["tdocket"] = dk[0]
    fd = fdate_tie(D, T)
    if fd:
        out["fdate"] = "%04d-%02d-%02d" % fd[0]
    au = author_tie(D, T)
    if au:
        out["author"] = au
    return out
