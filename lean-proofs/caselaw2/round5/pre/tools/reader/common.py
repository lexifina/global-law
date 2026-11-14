"""Shared helpers of the caselaw-lean-2 reader: paths, citation keys (same normalisation as v1 graph.py), opinion
parts, sentence spans, case-name tokens."""
import os, re

W = os.path.expanduser("~/Documents/us-caselaw-lean-work")
C2 = os.path.join(W, "caselaw-lean-2")
DATA = os.path.join(C2, "data")
WORK = os.path.join(DATA, "reader_work")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")

# v1 events.py citation pattern and graph.py normalisation (the keys of graph/cite_index.tsv)
CITE_RX = re.compile(r"\b(\d{1,4})\s+((?:[A-Z][A-Za-z.']{0,9}\s?){1,5}(?:\d[a-z]{1,2}\.?\s?)?(?:\([^)]{1,12}\)\s?)?)\s*(\d{1,5})\b")
_CITE = re.compile(r"^\s*(\d+)\s+(.+?)\s+(\d+)\s*$")


def norm_cite(c):
    m = _CITE.match(c)
    if not m:
        return None
    rep = re.sub(r"[\s.,']", "", m.group(2)).lower()
    rep = rep.replace("2nd", "2d").replace("3rd", "3d")
    return f"{int(m.group(1))} {rep} {int(m.group(3))}"


def cite_key(m):
    return norm_cite(f"{m.group(1)} {re.sub(r'[()]', '', m.group(2))} {m.group(3)}")


HEAD_RX = re.compile(r"^## (.+)$", re.M)
SEP_RX = re.compile(r"^(?P<line>[^\n]{0,140}\b(?P<w>dissenting|concurring|dissent|concurrence)\b[^\n]{0,60})$", re.M | re.I)
JUDGE_MARK = re.compile(r"\b(?:J\.|JJ\.|Judge|Justice|C\.\s?J\.|Chief|P\.\s?J\.|Senior|Circuit|District)", re.I)
OPINION_WORDS = re.compile(r"\b(?:filed|joined|joins|join|delivered|announced|in which|with whom|wrote|writes|see\b|post\b|ante\b)", re.I)


def classify_heading(h):
    x = h.strip().lower()
    if x.startswith("head matter") or x.startswith("cap head matter") or x == "syllabus":
        return "headmatter"
    if x.startswith("dissent"):
        return "dissent"
    if x.startswith("concurr") or x.startswith("concurrenceinpart"):
        return "concurrence"
    if x.startswith("majority"):
        return "perCuriam" if "per curiam" in x else "majority"
    if x.startswith("per curiam"):
        return "perCuriam"
    if x.startswith("lead") or x.startswith("plurality"):
        return "plurality"
    if x.startswith("combined"):
        return "majority?"  # CourtListener unsplit text: split below by separate-opinion lines
    if x.startswith("rehearing") or x.startswith("on rehearing"):
        return "majority"
    if x.startswith(("memorandum", "summary opinion", "bench opinion", "on the merits", "t.c. opinion", "unanimous",
                     "opinion")):
        return "majority"
    return "unknown"


def part_map(text):
    """[(start, end, part, section title)] covering the text, and the offset where the body (after front matter)
    starts. Parts: front, title, headmatter, majority, perCuriam, plurality, concurrence, dissent, unknown.
    Inside majority/perCuriam/Combined sections, a short line naming a judge as dissenting or concurring starts a
    separate-opinion part (its part name gets the suffix '~' = inferred from the text, not from a heading)."""
    body0 = 0
    if text.startswith("---"):
        e = text.find("\n---", 3)
        if e >= 0:
            nl = text.find("\n", e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    out = [(0, body0, "front", "")] if body0 else []
    heads = [(m.start(), m.group(1)) for m in HEAD_RX.finditer(text, body0)]
    first = heads[0][0] if heads else len(text)
    if first > body0:
        out.append((body0, first, "title", ""))
    for i, (a, h) in enumerate(heads):
        b = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        p = classify_heading(h)
        sec = h.strip()[:80]
        if p in ("majority", "perCuriam", "majority?"):
            base = "majority" if p == "majority?" else p
            cur = a
            curp = base if p != "majority?" else "majority~"
            for m in SEP_RX.finditer(text, a + len(h) + 4, b):
                line = m.group("line")
                if len(line) > 160 or not JUDGE_MARK.search(line) or OPINION_WORDS.search(line):
                    continue
                w = m.group("w").lower()
                newp = ("dissent~" if w.startswith("dissent") else "concurrence~")
                if m.start() > cur:
                    out.append((cur, m.start(), curp, sec))
                cur, curp = m.start(), newp
            out.append((cur, b, curp, sec))
        else:
            out.append((a, b, p, sec))
    return out, body0


NL = chr(10)
# ---- round 2: part map for hard-wrapped texts (slip opinions) --------------------------------------------------
# v1's rule (a short line with a judge mark and "concurring"/"dissenting" starts a separate opinion) fires on wrapped
# citation parentheticals such as "887, with id., at 920-922 (Stevens, J., concurring in part and dissent-", after
# which the rest of the opinion of the court is labelled a separate opinion (Dobbs, Wayfair, Trump v. Hawaii).
# v2: such a line must have no digit and no parenthesis; and the running heads of slip opinions ("Syllabus",
# "Opinion of the Court", "Per Curiam", "THOMAS, J., concurring", "Opinion of GORSUCH, J.") set the part.
RUNHEAD = re.compile(r"^[ \t]*(?:(?P<syl>Syllabus)|(?P<court>Opinion\s+of\s+the\s+Court)|(?P<pc>Per\s+Curiam)|"
                     r"(?P<sep>(?:[A-Z][A-Za-z’'\-]+\s*,\s*(?:and\s+)?)+(?:C\.\s?J\.|J\.|JJ\.)\s*,\s*"
                     r"(?P<w>concurring|dissenting)[A-Za-z ,]{0,60})|(?P<opof>Opinion\s+of\s+[A-Z][A-Za-z’'\-]+\s*,\s*"
                     r"(?:C\.\s?J\.|J\.)))[ \t]*$", re.M)
# round 3 (resume): a prose line of the opinion of the court that speaks ABOUT the dissent ("   The dissent ends by
# quoting Chevron: “ `Judges are not") is not a separate-opinion heading: no quotation marks, no "The dissent" start.
BAD_SEP = re.compile(r"[0-9()\[\]“”\"]|\bid\.|\bsupra\b|\binfra\b|U\.\s?S\.|^\s*The\s+(?:principal\s+)?(?:dissent|concurrence)\b")


def part_map2(text):
    """part_map with the round-2 rules for separate-opinion lines and running heads. Same return shape."""
    body0 = 0
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    out = [(0, body0, "front", "")] if body0 else []
    heads = [(m.start(), m.group(1)) for m in HEAD_RX.finditer(text, body0)]
    first = heads[0][0] if heads else len(text)
    if first > body0:
        out.append((body0, first, "title", ""))
    for i, (a, h) in enumerate(heads):
        b = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        p = classify_heading(h)
        sec = h.strip()[:80]
        if p not in ("majority", "perCuriam", "majority?"):
            out.append((a, b, p, sec))
            continue
        base = "majority" if p == "majority?" else p
        marks = []  # (offset, part)
        for m in SEP_RX.finditer(text, a + len(h) + 4, b):
            line = m.group("line")
            if len(line) > 160 or not JUDGE_MARK.search(line) or OPINION_WORDS.search(line) or BAD_SEP.search(line):
                continue
            marks.append((m.start(), "dissent~" if m.group("w").lower().startswith("dissent") else "concurrence~"))
        for m in RUNHEAD.finditer(text, a + len(h) + 4, b):
            if m.group("syl"):
                marks.append((m.start(), "headmatter~"))
            elif m.group("court"):
                marks.append((m.start(), "majority~"))
            elif m.group("pc"):
                marks.append((m.start(), "perCuriam"))
            elif m.group("sep"):
                marks.append((m.start(), "dissent~" if m.group("w").lower().startswith("dissent") else "concurrence~"))
            else:
                marks.append((m.start(), "concurrence~"))
        marks.sort()
        cur, curp = a, (base if p != "majority?" else "majority~")
        for off, newp in marks:
            if newp == curp:
                continue
            if off > cur:
                out.append((cur, off, curp, sec))
            cur, curp = off, newp
        out.append((cur, b, curp, sec))
    return out, body0


def part_at(pm, off):
    for a, b, p, s in pm:
        if a <= off < b:
            return p, s
    return "unknown", ""


ABBR = set("""v vs No Nos Co Inc Corp Ltd al seq Bros Ry App Supp Ct Dist Div Cir Rep Rptr Super Misc Dept Cas Ed
    Eq Ga Va Md Pa Me Vt Del Ky La Mo Ohio Iowa Wash Mass Conn Penn Mich Minn Wis Ill Ind Kan Neb Okla Ariz Colo Cal Fla
    Ala Tenn Miss Ark Ore Nev Mont Wyo Utah Tex Civ Crim Pac Atl Fed Wall Pet How Cranch Dall Wheat Black Mr Mrs Dr St
    Ave Assn Ass Comm Comr Commr Sec Stat Ann Gen Laws Rev Cl Pt Art Ch Sess Reg Id Ibid Jr Sr So Wn Hun Barb Paige Wend
    Johns Cow Abb Pr Hill Den Daly Bosw Sandf Duer Hilt Bradf Edw Redf Dem Wheel Rob Cong Pub Stats Const Amend Cert""".split())


NL = chr(10)


def _is_end(s, i):
    c = s[i]
    if c == NL:
        return True
    if c not in ".!?":
        return False
    n = len(s)
    j = i + 1
    while j < n and s[j] in "”\"’')":
        j += 1
    if j >= n or s[j] == NL:
        return True
    if s[j] != " ":
        return False
    while j < n and s[j] == " ":
        j += 1
    if j >= n or s[j] == NL:
        return True
    if not (s[j].isupper() or s[j] in "“\"(["):
        return False
    w = re.search(r"([A-Za-z’']+)$", s[max(0, i - 15):i])
    if w and (w.group(1) in ABBR or len(w.group(1)) <= 2):
        return False
    return True


def sentence_span(s, a, b, back=450, fwd=350):
    a0 = max(0, a - back)
    for i in range(a - 1, max(0, a - back) - 1, -1):
        if _is_end(s, i):
            a0 = i + 1
            break
    while a0 < a and s[a0] in " \n":
        a0 += 1
    a1 = min(len(s), b + fwd)
    for i in range(b, min(len(s), b + fwd)):
        if _is_end(s, i):
            a1 = i + 1 if s[i] != "\n" else i
            break
    return a0, a1


STOPW = set("""United States America State States People Commonwealth Commissioner Commissioners Company Corporation
    Railway Railroad Insurance County City Town Village Board Bank National Department Dept Director Secretary
    Administrator Estate Matter Ex Parte Re In The Of And For Inc Co Corp Ltd Association Assn Mutual Life Fire
    Trust Savings Loan Federal District Court Mr Mrs Supreme Appeals Plaintiff Defendant Appellant Appellee
    Petitioner Respondent Others Al Et Use Ins Ry Bros Brothers Sons General Central Southern Northern Eastern
    Western American New Mexico York Texas Pacific Atlantic Missouri Union Steamship Ship Steamboat Lessee Lessees
    Heirs Executor Executors Executrix Administratrix Guardian Trustee Trustees Receiver Collector Warden Sheriff
    Treasurer Auditor Governor Attorney Superintendent Mayor Council Town Township School Schools Church Hospital
    Motor Motors Oil Gas Electric Power Light Water Telephone Telegraph Coal Iron Steel Lumber Mining Land Lands
    Title Guaranty Surety Casualty Indemnity Fidelity Accident Assurance Express Transportation Transit Bus Lines
    Line Mills Mill Manufacturing Products Services Service Industries Enterprises Holdings Group Partners Unknown
    Commission Authority Agency Division Office Officer Officers Employees Employee Workers Local International
    Florida California Illinois Ohio Michigan Pennsylvania Georgia Virginia Carolina Jersey Massachusetts Kentucky
    Tennessee Alabama Louisiana Washington Oregon Arizona Colorado Kansas Nebraska Iowa Minnesota Wisconsin Indiana
    Maryland Connecticut Maine Vermont Hampshire Island Delaware Dakota Montana Idaho Nevada Utah Wyoming Alaska Hawaii
    Oklahoma Arkansas Mississippi Hampshire Rhode Columbia Puerto Rico Doe""".split())


def name_tokens(nm):
    nm = re.sub(r"\(.*?\)", " ", nm or "")
    return {t for t in re.findall(r"\b[A-Z][a-z][A-Za-z'\-]{2,}", nm) if t.rstrip("'s") not in STOPW and t not in STOPW}


# ---- round 3: hard-wrapped texts (slip opinions, PDF-extracted appeals opinions) ----------------------------------
# A hard-wrapped text has one line per printed line, so `sentence_span` (a line break ends a sentence) cut every
# sentence at the wrap. `unwrap_view` returns a view of the SAME LENGTH in which a wrap newline is a space, so every
# offset in the view is an offset in the original text (the offset map is the identity) and a quote cut from the
# original text and normalised as SCHEMA says (newline -> space, one for one) equals the same slice of the view.
# Paragraph breaks (blank lines) and page breaks (form feed) stay line breaks.
# `dehyphen` removes line-end hyphenation ("over-\nruled" -> "overruled") for PATTERN MATCHING only and returns the
# map from its offsets to the original ones. Quotes are never cut from the de-hyphenated string.
_WRAP_NL = re.compile(r"(?<=[^\n\x0c])\n(?=[^\n\x0c])")
_HYPH = re.compile(r"(?<=[a-z])-\n[ \t]*(?=[a-z])")


def hard_wrapped(text, body0=0):
    """Line-length statistics of the body: at least 25 non-blank lines, the 90th percentile of their lengths at most
    110 characters, the median at least 30, and at least 60% of them 35-110 characters long."""
    lens = [len(l) for l in text[body0:].split(NL) if l.strip()]
    if len(lens) < 25:
        return False
    lens.sort()
    if lens[int(len(lens) * 0.9)] > 110 or lens[len(lens) // 2] < 30:
        return False
    return sum(1 for x in lens if 35 <= x <= 110) >= 0.6 * len(lens)


def unwrap_view(text, body0=0):
    """Same-length view: a single newline between two non-empty lines becomes a space (from body0 on)."""
    return text[:body0] + _WRAP_NL.sub(" ", text[body0:])


def dehyphen(text, body0=0, view=None):
    """(dh, omap): the text without line-end hyphenation; omap[i] is the offset in `text` of dh[i], and
    omap[len(dh)] == len(text). Only a hyphen between two lower-case letters at a line end of the ORIGINAL `text` is
    removed. With `view` (unwrap_view of the same text), the kept characters are taken from the view."""
    src = text if view is None else view
    pieces, omap, last = [], [], 0
    for m in _HYPH.finditer(text, body0):
        pieces.append(src[last:m.start()])
        omap.extend(range(last, m.start()))
        last = m.end()
    pieces.append(src[last:])
    omap.extend(range(last, len(text) + 1))
    return "".join(pieces), omap


def dehyphen_norm(s):
    """De-hyphenate a NORMALISED fragment (wrap newline already a space): "over- ruled" -> "overruled". For rule
    matching only."""
    return re.sub(r"(?<=[a-z])- +(?=[a-z])", "", s)


class Span:
    """A regex match of the de-hyphenated string, with its span mapped to the original text."""
    __slots__ = ("a", "b")

    def __init__(self, m, omap):
        self.a = omap[m.start()]
        self.b = omap[m.end() - 1] + 1 if m.end() > m.start() else omap[m.start()]

    def start(self):
        return self.a

    def end(self):
        return self.b


SHORT_STOP = set("The And For Inc Ltd Not But Our Its Any All See Per Art Sec Tit Act Rev Stat Cal App Div Pac Atl Fed Sup "
                 "Law Bar Ins Rep Mut Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec One Two Six Ten New Old Doe Was Has "
                 "Had Are His Her Who Did Can May Two Use Due Tax Gas Oil Bus Air Car Mrs Com Her Him She You Yet Nor".split())


def short_name_tokens(nm):
    """Three-letter party names ("Roe v. Wade" -> Roe; "Lee", "Fay", "Poe"), which name_tokens leaves out."""
    nm = re.sub(r"\(.*?\)", " ", nm or "")
    out = set()
    for side in re.split(r"\s+v\.?\s+|\s+vs\.?\s+", nm):
        m = re.match(r"\s*([A-Z][a-z]{2})\b(?!\.)", side)
        if m and m.group(1) not in SHORT_STOP:
            out.add(m.group(1))
    return out
