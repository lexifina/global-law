"""stlink11: identity ties between a state court-of-last-resort opinion D and an intermediate decision T, from the
two decisions' own texts (front matter as printed by the reporter + the opinion text). No key.

    parse(text)           -> dict(front fields, body)
    party_entities(s)     -> [[entity, ...] per caption side]
    names_tie(D, T)       -> (status, detail)   status: full / surname_only / mismatch / frequent_only / no_parties
    docket_tie(D, T)      -> (status, token, ctx)
    date_tie(D, T)        -> status
    cite_tie(D, T)        -> status
"""
import json, re

NL = chr(10)
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
MONTHS = {m: i + 1 for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                          "september", "october", "november", "december"])}
MABBR = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9,
         "oct": 10, "nov": 11, "dec": 12}
MON_RX = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|" \
         r"Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\.?"
DATE_MDY = re.compile(MON_RX + r"\s+(\d{1,2})(?:st|nd|rd|th|d)?,?\s+(1[789]\d\d|20[0-2]\d)\b")
DATE_DMY = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th|d)?\s+(?:day\s+of\s+)?" + MON_RX + r",?\s+(?:A\.\s?D\.\s+)?(1[789]\d\d|20[0-2]\d)\b")
DATE_NUM = re.compile(r"\b(\d{1,2})/(\d{1,2})/((?:1[789]|20)?\d\d)\b")
DOCK_TOK = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-\./:]*")

ROLE = re.compile(r"^(?:et\s+al\.?|et\s+ux\.?|et\s+vir\.?|appellants?|appellees?|respondents?|petitioners?|plaintiffs?|"
                  r"defendants?|plaintiffs?\s+in\s+error|defendants?\s+in\s+error|cross[- ]appellants?|cross[- ]appellees?|"
                  r"cross[- ]respondents?|cross[- ]petitioners?|intervenors?|movants?|relators?|claimants?|"
                  r"complainants?|contestants?|contestees?|garnishees?|proponents?|caveators?|libellants?|"
                  r"and\s+(?:appellants?|appellees?|respondents?|petitioners?)|(?:plaintiff|defendant|respondent|petitioner|"
                  r"appellant|appellee)s?[- ](?:appellants?|appellees?|respondents?|petitioners?)|individually|"
                  r"and\s+others|and\s+another|etc\.?|a\s+minor|deceased|an\s+infant|a\s+corporation|"
                  r"a\s+\w+\s+corporation|executors?|executrix|administrators?|administratrix|trustees?|guardian.*|"
                  r"next\s+friend.*|by\s+.*|as\s+.*|on\s+behalf\s+of.*|for\s+the\s+use\s+of.*|"
                  r"jr\.?|sr\.?|ii|iii|iv|inc\.?|ltd\.?|llc|l\.l\.c\.|co\.?|corp\.?|n\.a\.|p\.c\.|l\.p\.|lp|llp)$", re.I)
SUFFIX = {"jr", "sr", "ii", "iii", "iv", "esq"}
TITLE = {"mr", "mrs", "ms", "miss", "dr", "hon", "rev", "honorable", "the"}
FREQ = re.compile(r"\b(?:state|commonwealth|people|united\s+states|city|county|town|township|village|borough|parish|"
                  r"board|department|dept|commission|commissioner|commissioners|agency|division|bureau|authority|"
                  r"district|director|secretary|warden|sheriff|superintendent|treasurer|collector|auditor|comptroller|"
                  r"attorney\s+general|insurance|assurance|casualty|indemnity|surety|guaranty|bank|banking|savings|"
                  r"trust\s+company|union|brotherhood|local\s+\d+|employment\s+security|industrial|"
                  r"workers'?\s+compensation|unemployment|registrar|clerk|court|judge|justice|governor|mayor|council|"
                  r"railroad|railway|railways|telephone|telegraph|power|electric|gas|light|water|"
                  r"public\s+service|utilities)\b", re.I)
ORG = re.compile(r"\b(?:company|co|corp|corporation|inc|incorporated|llc|ltd|association|assn|society|church|bank|"
                 r"insurance|railroad|railway|state|commonwealth|people|city|county|town|township|village|board|"
                 r"department|commission|authority|district|union|trust|estate|partnership|club|hospital|university|"
                 r"college|school|services|systems|enterprises|industries|group|holdings|partners|associates|"
                 r"brothers|bros|mills|works|lumber|oil|motor|motors|stores|market|hotel|farms|united\s+states|"
                 r"administration|agency|bureau|division|office|fund|foundation|center|institute|council|lodge|"
                 r"cooperative|exchange|federation|order|corps)\b", re.I)


def parse(text):
    m = FRONT.match(text)
    front = {}
    body = text
    if m:
        body = text[m.end():]
        for line in m.group(1).split(NL):
            k, _, v = line.partition(":")
            v = v.strip()
            if not k or not v:
                continue
            try:
                front[k.strip()] = json.loads(v)
            except ValueError:
                front[k.strip()] = v.strip('"')
    return {"front": front, "body": body}


def _split_sides(s):
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"\s+", " ", s).strip().rstrip(".")
    m = re.search(r"\s(?:v\.?|vs\.?|versus|against)\s", s, re.I)
    if m:
        return [s[:m.start()], s[m.end():]]
    m = re.match(r"^(?:in\s+re|in\s+the\s+matter\s+of|matter\s+of|in\s+re\s+the\s+estate\s+of|estate\s+of|"
                 r"ex\s+parte|application\s+of|petition\s+of|appeal\s+of|in\s+the\s+interest\s+of)\s+(.*)$", s, re.I)
    if m:
        return [m.group(1)]
    return [s]


def party_entities(parties):
    """parties: the front matter list (usually one string "A, Appellant, v. B, Appellee.")."""
    if isinstance(parties, list):
        parties = " ".join(parties)
    if not parties:
        return []
    sides = []
    for side in _split_sides(parties):
        ents = []
        for piece in re.split(r";|\s&\s(?=[A-Z][a-z]+\s+[A-Z])|,?\s+and\s+(?=[A-Z][a-z]+\s+(?:[A-Z]\.\s+)?[A-Z][A-Za-z]+\b)", side):
            segs = [x.strip() for x in piece.split(",")]
            name = []
            for k, sg in enumerate(segs):
                if not sg:
                    continue
                if k > 0 and ROLE.match(sg):
                    if re.match(r"^(?:jr|sr|ii|iii|iv|inc|ltd|llc|co|corp)\.?$", sg, re.I):
                        name.append(sg)
                    continue
                if k > 0 and name and not ORG.search(" ".join(name)) and re.match(r"^[A-Z]", sg) and len(sg.split()) >= 2:
                    # "Edward T. BOWLES, John SMITH" -> separate entities
                    ents.append(" ".join(name))
                    name = [sg]
                    continue
                if k > 0 and not re.match(r"^[A-Z0-9]", sg):
                    continue
                name.append(sg)
            if name:
                ents.append(" ".join(name))
        ents = [e for e in (re.sub(r"\s+", " ", x).strip(" .,") for x in ents) if e and len(e) > 1]
        sides.append(ents)
    return [s for s in sides if s]


def is_org(e):
    return bool(ORG.search(e)) or bool(re.search(r"\bof\b", e, re.I))


def is_frequent(e):
    return bool(FREQ.search(e))


def person_key(e):
    toks = [t.strip(".,").lower() for t in re.findall(r"[A-Za-z][A-Za-z'\-\.]*", e)]
    toks = [t for t in toks if t and t not in TITLE]
    while toks and toks[-1] in SUFFIX:
        toks.pop()
    if len(toks) < 2:
        return None, toks[-1] if toks else None
    given, sur = toks[0], toks[-1]
    if len(given.rstrip(".")) <= 1:   # an initial is not a given name
        # "J. Edgar Smith": use the next full word
        rest = [t for t in toks[1:-1] if len(t.rstrip(".")) > 1]
        if not rest:
            return None, sur
        given = rest[0]
    return (given.rstrip("."), sur), sur


def org_key(e):
    t = re.sub(r"[^a-z0-9 ]", " ", e.lower().replace("&", " and "))
    words = [w for w in t.split() if w not in ("the", "inc", "incorporated", "co", "company", "corp", "corporation",
                                                 "llc", "ltd", "limited", "a", "an", "of", "and")]
    return " ".join(words)


def _ent_match(te, d_ents):
    """-> 'full' / 'mismatch' / 'surname_only' / 'none' for one T entity against D's entities."""
    if is_org(te):
        k = org_key(te)
        if not k:
            return "none"
        for de in d_ents:
            if is_org(de) and org_key(de) == k:
                return "full"
        return "none"
    pk, sur = person_key(te)
    if not sur:
        return "none"
    best = "none"
    for de in d_ents:
        if is_org(de):
            continue
        dk, dsur = person_key(de)
        if dsur != sur:
            continue
        if pk is None or dk is None:
            best = "surname_only" if best != "full" else best
            continue
        if pk == dk:
            return "full"
        best = "mismatch" if best == "none" else best
    return best


FREQ_EQ = [re.compile(r"\bstate\b", re.I), re.compile(r"\bcommonwealth\b", re.I), re.compile(r"\bpeople\b", re.I),
           re.compile(r"\bunited\s+states\b", re.I)]


def _freq_side_match(t_side, d_ents):
    for rx in FREQ_EQ:
        if any(rx.search(e) for e in t_side) and any(rx.search(e) for e in d_ents):
            return True
    keys = {org_key(e) for e in d_ents}
    return any(org_key(e) in keys for e in t_side)


GN_STOP = {"mr", "mrs", "ms", "miss", "dr", "the", "justice", "judge", "chief", "defendant", "appellant", "appellee",
            "officer", "trooper", "sergeant", "deputy", "detective", "agent", "sister", "brother", "saint", "fort", "port",
            "lake", "mount", "new", "north", "south", "east", "west", "and", "for", "from", "with", "that", "this",
            "petitioner", "respondent", "plaintiff", "witness", "doctor", "senator", "governor", "mayor", "sheriff",
            "attorney", "counsel", "said", "upon", "against", "when", "where", "then", "after", "before", "also", "his",
            "her", "their", "our", "under", "court", "state", "county", "city", "estate", "matter", "re", "ex", "parte",
            "commonwealth", "people", "united", "states", "district", "superior", "supreme", "appeals", "honorable",
            "hon", "rev", "reverend", "father", "mother", "wife", "husband", "son", "daughter", "widow", "decedent"}


def body_given(text, sur):
    """most frequent given name printed before the surname in a text (people named 'Given [M.] Surname')."""
    rx = re.compile(r"\b([A-Z][a-z]{2,})\s+(?:[A-Z]\.\s+|[A-Z][a-z]+\s+)?(?i:" + re.escape(sur) + r")\b")
    c = {}
    for m in rx.finditer(text):
        g = m.group(1).lower()
        if g in GN_STOP or g == sur:
            continue
        c[g] = c.get(g, 0) + 1
    if not c:
        return None
    top = sorted(c.items(), key=lambda kv: -kv[1])
    if len(top) > 1 and top[1][1] == top[0][1]:
        return None   # two people of that surname named equally often: no tie
    return top[0][0]


def names_tie(dparties, tparties, dbody=None, tbody=None):
    """dbody / tbody given: a person printed by surname alone in a caption is completed from the texts (the given
    name printed most often before that surname in each text must be the same) -> status 'full_body'."""
    st, det = _names_tie(dparties, tparties, None, None)
    if st in ("surname_only",) and dbody is not None and tbody is not None:
        st2, det2 = _names_tie(dparties, tparties, dbody, tbody)
        if st2 == "full":
            return "full_body", det2
    return st, det


def _ent_match_body(te, d_ents, dbody, tbody):
    r = _ent_match(te, d_ents)
    if r != "surname_only":
        return r
    sur = person_key(te)[1]
    if not sur or len(sur) < 3:
        return r
    # captions: given names where printed, else from the bodies
    pk = person_key(te)[0]
    gt = pk[0] if pk else body_given(tbody, sur)
    dg = None
    for de in d_ents:
        if not is_org(de) and person_key(de)[1] == sur:
            dk = person_key(de)[0]
            dg = dk[0] if dk else None
    if dg is None:
        dg = body_given(dbody, sur)
    if gt and dg and gt == dg:
        # the other text must print the same given name too (both texts' own words)
        if body_given(tbody, sur) in (gt, None) and body_given(dbody, sur) in (dg, None) and \
                (body_given(tbody, sur) or body_given(dbody, sur)):
            return "full"
        return "mismatch"
    if gt and dg and gt != dg:
        return "mismatch"
    return r


def _names_tie(dparties, tparties, dbody, tbody):
    ds, ts = party_entities(dparties), party_entities(tparties)
    if not ds or not ts:
        return "no_parties", ""
    d_ents = [e for s in ds for e in s]
    side_ok, full_nonfreq, worst = [], [], None
    order = {"full": 0, "frequent": 1, "surname_only": 2, "mismatch": 3, "none": 4}
    for side in ts:
        nonfreq = [e for e in side if not is_frequent(e)]
        if not nonfreq:
            st = "frequent" if _freq_side_match(side, d_ents) else "none"
        else:
            res = [(_ent_match(e, d_ents) if dbody is None else _ent_match_body(e, d_ents, dbody, tbody))
                   for e in nonfreq]
            if "full" in res:
                st = "full"
                full_nonfreq += [e for e, r in zip(nonfreq, res) if r == "full"]
            elif "mismatch" in res:
                st = "mismatch"
            elif "surname_only" in res:
                st = "surname_only"
            else:
                st = "none"
        side_ok.append(st)
        worst = st if worst is None or order[st] > order[worst] else worst
    if worst in ("full", "frequent"):
        if full_nonfreq:
            return "full", "|".join(full_nonfreq)
        return "frequent_only", ""
    return worst, ""


def compact(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def docket_tokens(dk):
    if isinstance(dk, list):
        dk = "; ".join(str(x) for x in dk)
    out = []
    for piece in re.split(r"[;,&]|\band\b", str(dk or "")):
        c = compact(re.sub(r"^\s*(?:nos?\.?|numbers?|docket|case)\s*", "", piece.strip(), flags=re.I))
        if len(c) >= 4 and re.search(r"\d", c):
            out.append(c)
    return out


def docket_tie(dtext, dfront, tfront):
    """T's docket token printed in D (front matter other than D's own docket, or body)."""
    toks = docket_tokens(tfront.get("docket"))
    if not toks:
        return "no_t_docket", "", ""
    own = set(docket_tokens(dfront.get("docket")))
    ws = [(m.start(), m.end(), compact(m.group(0))) for m in DOCK_TOK.finditer(dtext)]
    for t in toks:
        if t in own:
            return "same_as_D_docket", t, ""
        for i, (a, b, c) in enumerate(ws):
            hit = c == t
            e = b
            if not hit and t.startswith(c) and c:
                acc = c
                for k in range(i + 1, min(i + 4, len(ws))):
                    acc += ws[k][2]
                    if acc == t:
                        hit, e = True, ws[k][1]
                        break
                    if not t.startswith(acc):
                        break
            if hit:
                ctx = dtext[max(0, a - 40):a]
                strong = bool(re.search(r"\b(?:nos?|numbers?|docket|case|appeal|cause)\.?\s*[:#]?\s*$", ctx, re.I)) or \
                    bool(re.search(r"[a-z]", t)) or len(t) >= 6
                return ("strong" if strong else "weak"), t, dtext[max(0, a - 40):e]
    return "absent", "", ""


def dates_in(text):
    out = set()
    for m in DATE_MDY.finditer(text):
        mon = m.group(1).lower().rstrip(".")
        mo = MONTHS.get(mon) or MABBR.get(mon[:4]) or MABBR.get(mon[:3])
        if mo:
            out.add((int(m.group(3)), mo, int(m.group(2))))
    for m in DATE_DMY.finditer(text):
        mon = m.group(2).lower().rstrip(".")
        mo = MONTHS.get(mon) or MABBR.get(mon[:4]) or MABBR.get(mon[:3])
        if mo:
            out.add((int(m.group(3)), mo, int(m.group(1))))
    for m in DATE_NUM.finditer(text):
        y = int(m.group(3))
        if y < 100:
            y += 1900 if y > 25 else 2000
        out.add((y, int(m.group(1)), int(m.group(2))))
    return out


def t_date(tfront):
    d = str(tfront.get("decided") or "")
    m = re.match(r"^(\d{4})-(\d\d)-(\d\d)$", d)
    if not m:
        return None
    y, mo, da = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if mo == 1 and da == 1:
        return None   # placeholder
    return (y, mo, da)


def date_tie(dbody, tfront, dset=None):
    td = t_date(tfront)
    if td is None:
        return "no_t_date"
    ds = dset if dset is not None else dates_in(dbody)
    return "present" if td in ds else "absent"


def cite_norm(c):
    c = c.lower().replace("wn.", "wash.").replace("wn ", "wash. ")
    c = re.sub(r"\b(\d+)(?:st|nd|rd|th|d)\b", r"\1", c)
    return re.sub(r"[^a-z0-9]", "", c)


def cite_tie(dtext, dfront, tcites):
    if isinstance(tcites, str):
        tcites = [x for x in tcites.split("|") if x]
    want = {cite_norm(c) for c in tcites if re.search(r"\d", c)}
    if not want:
        return "no_t_cite", ""
    got = {cite_norm(c) for c in (dfront.get("cites_cases") or []) if isinstance(c, str)}
    hit = want & got
    if hit:
        return "front", sorted(hit)[0]
    # body: volume reporter page with flexible spacing
    for c in tcites:
        m = re.match(r"^(\d+)\s+(.+?)\s+(\d+)$", c.strip())
        if not m:
            continue
        rep = re.escape(m.group(2)).replace(r"\ ", r"\s*").replace(r"\.", r"\.?")
        rx = re.compile(r"\b" + m.group(1) + r"\s+" + rep + r"\s+" + m.group(3) + r"\b", re.I)
        if rx.search(dtext):
            return "body", c
    return "absent", ""
