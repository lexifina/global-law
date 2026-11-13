"""Per-file measurements over the materialised sample. python analyze.py <sample-dir> <out.jsonl>"""
import os, re, sys, json
from multiprocessing import Pool
S, OUT = sys.argv[1], sys.argv[2]
H2 = re.compile(r"^## (.+)$", re.M)


def kind(h):
    l = h.lower()
    for k in ("head matter", "majority", "concurrence", "dissent", "combined", "plurality", "concurring in part",
              "rehearing", "lead", "addendum", "remittitur"):
        if l.startswith(k):
            return k
    return "other:" + l.split("(")[0].strip()[:30]


PAT = {
    "en_banc": r"\b(?:en|in) banc\b|\bin bank\b",
    "per_curiam": r"\bper curiam\b",
    "plurality": r"\bplurality opinion\b|\bannounced the judgment of the court\b|\bopinion announcing the judgment\b|\bplurality of the court\b",
    "unpublished": r"not (?:designated )?for (?:official )?publication|not to be published|\bunpublished (?:opinion|decision|order|memorandum|disposition)|\bnon-?precedential\b|\bnot precedential\b|\bnot (?:be )?cit(?:ed|able) as precedent|\bmay not be cited\b|\bshould not be published\b|rule 47\.5|rule 36-3|supreme court rule 23\b",
    "vacated": r"\bvacated\b",
    "vacated_opinion": r"\b(?:opinion|judgment|decision) (?:of this court |previously (?:filed|issued) )?(?:is |was |be |are )?(?:hereby )?vacated\b|\bvacate (?:our|the panel'?s?|its) (?:prior |previous |earlier |original )?(?:opinion|judgment|decision)",
    "withdrawn": r"\b(?:opinion|decision|mandate) (?:\w+ ){0,4}(?:is|was|are|be|been|hereby) (?:hereby )?withdrawn\b|\bwithdraw (?:our|the|its) (?:prior |previous |earlier |original |panel )?(?:opinion|decision)|\bwithdrawn and (?:the following |this opinion )?(?:is )?substituted|\bsubstituted (?:therefor|in (?:its|their) place)",
    "rehearing": r"\brehearing\b",
    "rehearing_granted_or_on": r"\bon rehearing\b|\brehearing (?:en banc )?(?:is |was |be |has been )?granted\b|\bupon rehearing\b",
    "rehearing_denied": r"\brehearing (?:en banc )?(?:is |was |be |has been )?denied\b",
    "syllabus": r"\bsyllabus\b",
    "held_colon": r"(?:^|\s)Held:\s",
    "headnote_num": r"^\s*\d{1,2}\.\s+[A-Z][A-Za-z ,'&]{2,60}\s*(?:—|–|--|-)\s",
    "attorneys": r"\bfor (?:the )?(?:appellants?|appellees?|petitioners?|respondents?|plaintiffs?|defendants?|the state|the people|the commonwealth|the government|the united states)\b|\battorney general\b|\bpro se\b|\bof counsel\b",
}
TREAT = {
    "overruled_in_part": r"\boverruled in part\b",
    "to_the_extent_overrul": r"to the extent (?:that )?[^.;]{0,200}?\b(?:overruled|disapproved|abrogated|receded)\b|\b(?:overrule|overruled|disapprove|disapproved|abrogated|recede from|receded from) [^.;]{0,120}?to the extent\b",
    "to_the_extent_that": r"\bto the extent that\b",
    "abrogated": r"\babrogat(?:ed|es|ing|ion)\b",
    "abrogated_other_grounds": r"\babrogated on other grounds\b",
    "superseded_by_statute": r"\bsuperseded by (?:statute|rule|constitutional amendment|amendment)\b",
    "disapproved": r"\bdisapprov(?:ed|e|es|ing)\b",
    "receded": r"\brecede[sd]? from\b|\breceding from\b",
    "limited_to_facts": r"\blimited to its (?:own )?facts\b",
    "questioned": r"\bquestioned\b",
    "questioned_treatment": r"\b(?:has been|was|been) questioned\b|\bcalled into question\b|\bquestioned (?:in|by) [A-Z]",
    "decline_to_follow": r"\b(?:we|this court|the court) (?:respectfully )?(?:decline|refuse)s? to follow\b",
    "overruled_other_grounds": r"\boverruled on other grounds\b",
    "overrule_any": r"\boverrul(?:e|ed|es|ing)\b",
    "overruled_procedural": r"\b(?:objection|motion|demurrer|exception|plea|assignment)s? (?:\w+ ){0,3}(?:was|were|is|are|be) (?:properly |correctly |rightly )?overruled\b",
    "expressly_overrule": r"\b(?:is|are|be) (?:hereby |expressly |now )+overruled\b|\bwe (?:hereby |now |expressly |therefore )*overrule\b",
}
PAT = {k: re.compile(v, re.I | re.M) for k, v in PAT.items()}
PAT["held_colon"] = re.compile(r"\bHeld[,:]|\bHeld that\b|^\s*\(1\) That\b", re.M)
PAT["headnote_num"] = re.compile(PAT["headnote_num"].pattern, re.M)
TREAT = {k: re.compile(v, re.I) for k, v in TREAT.items()}
ORDW = "First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth"
TX_CITIES = r"Houston|Dallas|Fort Worth|Austin|San Antonio|Texarkana|Amarillo|El Paso|Beaumont|Waco|Eastland|Tyler|Corpus Christi|Galveston"
NY_DEPT = re.compile(r"\b(First|Second|Third|Fourth) Department\b", re.I)
NY_COUNTY = re.compile(r"\b(New York|Bronx|Kings|Queens|Richmond|Nassau|Suffolk|Westchester|Erie|Monroe|Albany|Onondaga|Dutchess|Orange|Rockland|Ulster|Schenectady|Rensselaer|Saratoga|Broome|Oneida|Niagara|[A-Z][a-z]+) County\b")


def district(court, d, head):
    c = court.lower()
    if "florida" in c and "appeal" in c:
        m = re.search(r"\b(%s) District\b" % ORDW, court + " " + head)
        if m: return "FL", "name/text:" + m.group(1)
        m = re.match(r"\s*(?:Nos?\.\s*)?(\d)D\d", d)
        if m: return "FL", "docket:" + m.group(1)
        return "FL", None
    if "california" in c and "appeal" in c:
        m = re.search(r"\b(%s) (?:Appellate )?Dist" % ORDW, court + " " + head, re.I)
        if m: return "CA", "name/text:" + m.group(1)
        m = re.match(r"\s*([A-H])\d{5,6}\b", d)
        if m: return "CA", "docket:" + m.group(1)
        return "CA", None
    if "texas" in c and "appeals" in c and "criminal" not in c:
        m = re.match(r"\s*(?:Nos?\.\s*)?(\d{1,2})-\d{2}-\d+-(?:CR|CV)", d)
        if m: return "TX", "docket:" + m.group(1)
        m = re.search(r"\b(%s)\b" % TX_CITIES, head)
        if m: return "TX", "text:" + m.group(1)
        return "TX", None
    if "illinois" in c and "appellate" in c:
        m = re.search(r"\b(First|Second|Third|Fourth|Fifth) District\b", court + " " + head, re.I)
        if m: return "IL", "name/text:" + m.group(1)
        m = re.match(r"\s*(?:Nos?\.\s*)?([1-5])-\d{2}-\d+", d)
        if m: return "IL", "docket:" + m.group(1)
        return "IL", None
    if "new york" in c and "appellate division" in c:
        m = NY_DEPT.search(court + " " + head)
        if m: return "NYAD", "dept:" + m.group(1)
        m = NY_COUNTY.search(head)
        if m: return "NYAD", "county:" + m.group(1)
        return "NYAD", None
    if "louisiana" in c and "appeal" in c:
        m = re.search(r"\b(First|Second|Third|Fourth|Fifth) Circuit\b|\b(Orleans)\b", court + " " + head, re.I)
        if m: return "LA", "name/text:" + (m.group(1) or m.group(2))
        return "LA", None
    if "ohio" in c and "appeals" in c:
        m = re.search(r"\b(%s) (?:Appellate )?District\b" % ORDW, court + " " + head, re.I)
        if m: return "OH", "district:" + m.group(1)
        m = re.search(r"\b([A-Z][a-z]+) County\b", head)
        if m: return "OH", "county:" + m.group(1)
        return "OH", None
    if "missouri" in c and "appeals" in c:
        m = re.search(r"\b(Kansas City|St\. Louis|Springfield|Eastern|Western|Southern) District\b", court + " " + head, re.I)
        if m: return "MO", "name/text:" + m.group(1)
        m = re.match(r"\s*(?:Nos?\.\s*)?(ED|WD|SD)\s?\d", d)
        if m: return "MO", "docket:" + m.group(1)
        return "MO", None
    if "washington" in c and "appeals" in c:
        m = re.search(r"-(I{1,3})\b", d)
        if m: return "WA", "docket:" + m.group(1)
        m = re.search(r"\bDivision (One|Two|Three|I{1,3}|1|2|3)\b", court + " " + head)
        if m: return "WA", "text:" + m.group(1)
        return "WA", None
    if "arizona" in c and "appeals" in c:
        m = re.match(r"\s*(?:Nos?\.\s*)?([12])\s?CA", d)
        if m: return "AZ", "docket:" + m.group(1)
        m = re.search(r"\bDivision (One|Two|1|2)\b", court + " " + head)
        if m: return "AZ", "text:" + m.group(1)
        return "AZ", None
    if "indiana" in c and ("appeals" in c or "appellate" in c):
        m = re.search(r"\b(First|Second|Third|Fourth|Fifth) District\b", court + " " + head)
        if m: return "IN", "text:" + m.group(1)
        m = re.match(r"\s*(?:Nos?\.\s*)?\d{2}A0(\d)", d)
        if m: return "IN", "docket:" + m.group(1)
        return "IN", None
    return None, None


def one(r):
    s, nid = r[0], r[1]
    fn = os.path.join(S, s, nid + ".md")
    t = open(fn, encoding="utf-8", errors="replace").read()
    end = t.find("\n---", 3)
    fmt = t[3:end]
    body = t[end + 4:]
    fm = {}
    for line in fmt.splitlines():
        k, sep, v = line.partition(":")
        if sep and line[:1] not in " -":
            try:
                fm[k] = json.loads(v.strip())
            except Exception:
                fm[k] = v.strip()
    hs = [(m.start(), m.end(), m.group(1)) for m in H2.finditer(body)]
    secs = []
    for i, (a, b, h) in enumerate(hs):
        e = hs[i + 1][0] if i + 1 < len(hs) else len(body)
        secs.append((kind(h), h, body[b:e]))
    head = "".join(x[2] for x in secs if x[0] == "head matter")
    ops = [x for x in secs if x[0] != "head matter"]
    optext = "".join(x[2] for x in ops)
    first = ops[0][2][:1500] if ops else ""
    hz = fmt + "\n" + head + "\n" + first
    rest = optext[1500:] if ops else ""
    rec = {"s": s, "id": nid, "court": r[5], "year": (r[6] or "0")[:4],
           "src": "CL" if "courtlistener" in fmt.lower() else ("DAWSON" if "dawson" in fmt.lower() else "CAP"),
           "len": len(body), "oplen": len(optext.strip()), "head_len": len(head.strip()),
           "kinds": sorted(set(x[0] for x in secs)), "sec_names": [x[1][:60] for x in ops][:6],
           "dtype": fm.get("decision_type"), "pstat": fm.get("precedential_status"),
           "judges": bool(fm.get("judges")), "docket": bool(fm.get("docket")),
           "sec_percuriam": any("per curiam" in x[1].lower() for x in ops)}
    for k, p in PAT.items():
        h1 = bool(p.search(hz))
        h2 = bool(p.search(rest))
        rec["p_" + k] = (1 if h1 else 0) + (2 if h2 else 0)
    rec["syll_head"] = bool(PAT["syllabus"].search(head))
    rec["held_head"] = bool(PAT["held_colon"].search(head))
    rec["syll_body"] = bool(re.search(r"\bSyllabus\b", optext[:4000]))
    rec["held_body"] = bool(PAT["held_colon"].search(optext[:6000]))
    hp = [l for l in head.splitlines() if len(l) > 150 and not PAT["attorneys"].search(l)]
    rec["head_prose"] = sum(len(l) for l in hp)
    rec["hn_head"] = len(PAT["headnote_num"].findall(head))
    rec["att_head"] = bool(PAT["attorneys"].search(head))
    rec["t"] = {k: len(p.findall(body)) for k, p in TREAT.items()}
    dk = fm.get("docket") if isinstance(fm.get("docket"), str) else ""
    g, how = district(r[5], dk, hz + "\n" + body[:4000])
    if g:
        rec["dist"] = [g, how]
    jl = " ".join(fm["judges"]) if isinstance(fm.get("judges"), list) else ""
    rec["judges_enbanc"] = bool(re.search(r"en banc|in banc", jl, re.I))
    return rec


if __name__ == "__main__":
    man = [l.rstrip("\n").split("\t") for l in open(os.path.join(S, "manifest.tsv"), encoding="utf-8")]
    man = [m for m in man if m[7] == "1"]
    with Pool(8) as p, open(OUT, "w", encoding="utf-8") as o:
        for rec in p.imap_unordered(one, man, chunksize=200):
            o.write(json.dumps(rec) + "\n")
