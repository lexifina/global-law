"""Shared reading of a decision for the holdings agent: opinion parts, sentences with offsets, candidate holding sentences.

Offsets are character offsets into text.norm_text(raw) (SCHEMA: UTF-8 decoded, \r\n -> \n).
"""
import re

SEC = re.compile(r"(?m)^## (.+)$")
# Separate opinions inside an unsplit (CourtListener "Combined") text.
SEPARATE = re.compile(
    r"^[ \t]*(?:[A-Z][A-Za-z.'\- ]{1,60}?,\s*)?(?:Chief\s+|Senior\s+)?(?:Circuit\s+|District\s+)?(?:Judge|J\.|Justice)[^\n]{0,80}?"
    r"(?:dissenting|concurring)\b"
    r"|^[ \t]*(?:Chief\s+)?(?:Circuit\s+)?(?:Judge|JUSTICE|Justice)\s+[A-Z][A-Za-z'\-]+[^\n]{0,80}?(?:dissenting|concurring)\b"
    r"|^[ \t]*[A-Z][A-Z'\- ]{2,40},\s*(?:C\.\s*)?J\.?,?\s*(?:dissenting|concurring)", re.M)
PLUR = re.compile(r"announced the judgment of the Court|delivered an opinion,? in which|"
                  r"opinion of the Court (?:with respect to|as to) Parts?|judgment of the Court and an opinion", re.I)
EQ = re.compile(r"(?:affirmed|judgment is affirmed) by an (?:equally|evenly) divided (?:Court|court)", re.I)
PC = re.compile(r"(?i)\bper curiam\b")

ABBR = set("""v vs U.S U. S S Ct L Ed F Supp App Cir Co Corp Inc Ltd No Nos Id id Stat Pub Fed Reg R Civ Crim P Evid Mr Mrs Ms
Dr St Jr Sr J JJ C Cal N.Y Mass Pa Ill Tex Fla Ga Va Md Mich Wis Minn Ark Ala Miss Tenn Ky Mo Kan Neb Colo Ariz Nev Ore Wash
Conn Del Vt Me Wyo Okla Ann Rev Gen Comp Art art cl ch sec Sec ed e.g i.e cf Cf n nn p pp et al seq ibid Bros Assn Dept Univ
Nat Am Ins Ry R.R Mfg So N.E N.W S.E S.W A 2d 3d 4th Wall How Pet Wheat Cranch Dall Wash Ct.App Cl Bankr B.R D T.C Cong Sess
H.R S.Rep Rep Doc Pa.Super Super Div Dist Cty Prob Mun Admin Ins Co.v Tr Vol vol Inst Jud Const amend Amend Ex Op Att'y
Dep't Ass'n Gov't Int'l Nat'l Comm'n Comm Hon Messrs Sup Ind La Ida Mont Haw Alaska Wy N.J N.H N.C S.C N.D S.D N.M R.I W.Va
D.C D.Mass Oh Inc.v Pp Para para fn Fn Tit tit subd Subd cmt Cmt""".split())
BOUND = re.compile(r"[.!?][\"'”’)\]]*\s+(?=[\"“‘(\[]?[A-Z])")


def sections(t):
    ms = list(SEC.finditer(t))
    out = []
    for i, m in enumerate(ms):
        e = ms[i + 1].start() if i + 1 < len(ms) else len(t)
        out.append((m.group(1).strip(), m.end(), e))
    return out


def decision_form(t, secs=None):
    secs = secs if secs is not None else sections(t)
    op = [s for s in secs if not s[0].lower().startswith(("head matter", "cap head matter"))]
    body = "".join(t[b:e] for n, b, e in op[:1])[:4000]
    if EQ.search(t[:8000]):
        return "equallyDivided"
    if any(n.lower().startswith(("lead", "plurality")) for n, _, _ in op) or PLUR.search(body):
        return "plurality"
    lead = op[0][0].lower() if op else ""
    if "per curiam" in lead or (PC.search(body[:600]) and not re.search(r"delivered the opinion of the Court", body)):
        return "perCuriam"
    return "full"


def court_parts(t, secs=None):
    """[(start, end, part)] for the text that speaks for the court: Majority/Lead/Per curiam/Combined sections, a
    Combined section cut at the first separate opinion. part: majority|plurality|perCuriam."""
    secs = secs if secs is not None else sections(t)
    form = decision_form(t, secs)
    out = []
    for name, b, e in secs:
        n = name.lower()
        if n.startswith(("majority", "lead", "plurality", "per curiam", "combined", "opinion", "on the merits", "memorandum opinion",
                         "summary opinion", "bench opinion", "t.c. opinion", "unanimous")):
            if n.startswith("combined") or n.startswith("opinion"):
                m = SEPARATE.search(t, b + 300, e)
                if m:
                    e = m.start()
            part = "plurality" if (form == "plurality" and n.startswith(("lead", "plurality", "majority", "combined"))) else (
                "perCuriam" if (form == "perCuriam" or "per curiam" in n) else "majority")
            out.append((b, e, part))
    return out, form


def split_sentences(t, b, e):
    """Sentence spans in t[b:e], trimmed of surrounding whitespace."""
    out = []
    s = b
    for m in BOUND.finditer(t, b, e):
        # the word before the period
        j = m.start()
        k = j
        while k > s and not t[k - 1].isspace():
            k -= 1
        word = t[k:j].strip("(\"'“‘[")
        if word in ABBR or (len(word) == 1 and word.isupper()) or re.fullmatch(r"(?:[A-Z]\.)+[A-Z]?", word) or \
                re.fullmatch(r"[A-Z][a-z]?\.[A-Z][a-z]?", word):
            continue
        end = m.start() + 1
        while end < m.end() and not t[end].isspace():
            end += 1
        out.append((s, end))
        s = m.end()
    out.append((s, e))
    res = []
    for a, z in out:
        while a < z and t[a].isspace():
            a += 1
        while z > a and t[z - 1].isspace():
            z -= 1
        if z - a >= 25:
            res.append((a, z))
    return res


STRONG = re.compile(
    r"\b(?:we|the court|this court|i)\s+(?:now\s+|therefore\s+|thus\s+|accordingly\s+|also\s+|further\s+|again\s+|today\s+|"
    r"must\s+|so\s+|cannot\s+but\s+)?(?:hold|conclude|decide|determine|overrule|construe|interpret|read)\b|"
    r"\bwe are (?:of (?:the )?opinion|persuaded|satisfied|convinced)\b|\bit is (?:therefore |accordingly )?(?:held|ordered|adjudged)\b|"
    r"\bour (?:holding|conclusion)\b|\bwe (?:agree|disagree|reject|decline|join|affirm|reverse)\b|\bwe find\b|"
    r"\bwe (?:therefore|thus) (?:find|agree|reject)\b|\bthe (?:court|rule) (?:is|was) (?:well )?settled\b|\bwe think\b", re.I)
MEDIUM = re.compile(
    r"\b(?:accordingly|therefore|thus|hence|consequently|it follows|for (?:these|the foregoing|the reasons)|in sum|in short|"
    r"we see no|must be|the (?:district|trial|lower|circuit|bankruptcy) court (?:erred|did not err|correctly|properly|was correct)|"
    r"(?:is|was|are|were) (?:not )?(?:required|entitled|barred|precluded|sufficient|insufficient|valid|invalid|"
    r"unconstitutional|constitutional|void|liable|applicable|inapplicable)|does not (?:apply|require|permit|bar)|"
    r"requires? that|plain (?:language|meaning|text)|the statute)\b", re.I)
FRAME = re.compile(r"\b(?:question(?:s)? (?:presented|before us|is whether|here is)|we granted (?:certiorari|review)|"
                   r"the (?:issue|question) (?:is|before us|presented|in this case)|this case (?:presents|requires|involves)|"
                   r"(?:appeal|case) (?:presents|raises) the (?:question|issue)|whether)\b", re.I)
CITE = re.compile(r"\d+\s+(?:U\.\s?S\.|F\.|S\.\s?Ct|L\.\s?Ed|So\.|N\.[EW]\.|S\.[EW]\.|P\.|A\.|Wall|Pet|How|Cranch|Wheat|Dall)")


def CITEISH(s):
    w = s.split()
    lower = sum(1 for x in w if x[:1].islower())
    return (len(w) < 14 and (CITE.search(s) or re.search(r"\d", s) and lower < 4)) or lower < len(w) * 0.35


NOISE = re.compile(r"^(?:affirmed|reversed|so ordered|it is so ordered|judgment affirmed)\.?$", re.I)


def candidates(t, parts, k=14, frame=3):
    """Pick up to k candidate holding sentences and up to `frame` framing sentences from the court's parts.
    Returns [(id, start, end, part, tag)] in text order; tag F (framing) or C (candidate)."""
    sents = []
    for b, e, part in parts:
        for a, z in split_sentences(t, b, e):
            if z - a > 1500:
                continue
            sents.append((a, z, part))
    if not sents:
        return []
    n = len(sents)
    scored = []
    fr = []
    for i, (a, z, part) in enumerate(sents):
        s = t[a:z]
        if NOISE.match(s.strip()):
            continue
        if CITEISH(s):
            continue
        sc = 3 * len(STRONG.findall(s)) + 1.0 * min(2, len(MEDIUM.findall(s)))
        pos = i / max(1, n - 1)
        if pos > 0.8 and sc > 0:
            sc += 0.7
        if sc > 0:
            scored.append((sc, i))
        if i < max(25, n // 4) and FRAME.search(s) and len(fr) < frame:
            fr.append(i)
    scored.sort(key=lambda x: (-x[0], -x[1]))
    pick = set(i for _, i in scored[:k])
    if len(pick) < 3:  # nothing marked: the last sentences usually state the result
        pick |= set(range(max(0, n - 4), n))
    fr = [i for i in fr if i not in pick]
    out = []
    for i in sorted(pick | set(fr)):
        a, z, part = sents[i]
        out.append((i, a, z, part, "F" if i in fr else "C"))
    return out


def show(t, a, z, limit=700):
    s = re.sub(r"\s+", " ", t[a:z]).strip()
    return s if len(s) <= limit else s[:limit] + " …"


def front(t, key):
    m = re.search(r'(?m)^' + key + r': "?(.*?)"?$', t[:4000])
    return m.group(1) if m else ""
