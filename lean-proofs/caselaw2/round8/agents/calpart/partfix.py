"""calpart rule PJ (round 8): a joining note in the opening header block of the opinion of the court does not open a
separate opinion.

The reader's part map (tools/caselaw2/reader/common.part_map / part_map2) starts a `concurrence~` / `dissent~` part at
a short line with a judge mark and "concurring" / "concurrence". Old reporters print the judges who join the opinion
of the court in the opinion's opening lines ("Burnett, J., delivered the opinion of the Court. / Terry, C. J., and
Field, J., concurring."; "Shields, J.; / Voorhees and Powell, JJ., concurring."; an en banc vote line "CHIEF JUDGE
HUG, JUDGE PREGERSON ... concurring; ... concurring in parts I, II and IV, and in the judgment."), and the F.3d head
prints an index of the opinions ("Opinion by Judge X; Concurrence by Judge Y."). Such a line is read as the start of
a separate opinion, so the whole opinion of the court is labelled `concurrence~`.

Rule PJ. In a section whose heading makes it the opinion of the court (part majority / perCuriam / majority~), a
separate-opinion mark is not a part boundary when
  (1) every line between the section heading and the mark is a header line: a byline / joining / index line made only
      of capitalised words (names, roman numerals), header vocabulary ("delivered the opinion of the court", "J.",
      "Circuit Judge", "joined by", "Opinion by", "Per Curiam", "Department", "In Bank" ...) and punctuation, with a
      judge mark or a header keyword, no disposition word (affirmed, reversed, dismissed ...; a capitalised one only as the first word), no number over two
      digits, at most 250 characters (so: no opinion prose before the mark), at most 1,500 characters in all;
  (2) the mark line itself is such a header line and contains a "concur" word (concurring, concurred, concur(s),
      concurrence): a note of judges joining the opinion, or an index of the separate opinions printed later.
Marks after the first prose line are untouched (a real separate opinion later in the section keeps its part).
No case, citation, party, court or answer-key field is used.
"""
import re

BASE_PARTS = ("majority", "perCuriam", "majority~")
SEP_PARTS = ("concurrence~", "dissent~")
MAX_LINE = 250
MAX_HEAD = 1500

VOCAB = set("""delivered the opinion opinions of court a an and judge judges justice justices circuit district chief senior
associate presiding j jj c p s by with whom who joined joins join concur concurs concurring concurred concurrence
concurrences in judgment result part parts all but except as to filed wrote written per curiam before mr mrs ms
sitting designation department bank banc en for this his her which specially separately dissenting dissent dissents
dissented also retired sat did not participate participating took no decision consideration absent being majority
plurality announced unanimous that is was are were he she they its their judgement on case at time argument
submission hearing herein appeal appeals pro tem tempore acting special commissioner commissioners division
following each authored adopted from st nd rd th or separate""".split())
JUDGE_MARK = re.compile(r"\b(?:J\.|JJ\.|Judges?|Justices?|C\.\s?J\.|Chief|P\.\s?J\.|Senior|Circuit|District|Commissioners?)",
                        re.I)
KEYWORD = re.compile(r"^\s*(?:OPINION|Opinion|PER\s+CURIAM|Per\s+Curiam|BY\s+THE\s+COURT|By\s+the\s+Court|"
                     r"FULL\s+TEXT|DEPARTMENT|Department|IN\s+BANK|In\s+Bank|IN\s+BANC|In\s+Banc|EN\s+BANC|En\s+Banc)\b")
DISP = re.compile(r"\b(?:affirm\w*|revers\w*|dismiss\w*|denied|deny\w*|grant\w*|modif\w*|remand\w*|vacat\w*|"
                  r"sustain\w*|overrul\w*|quash\w*|annul\w*|set\s+aside|costs?)\b", re.I)
CONCUR = re.compile(r"\bconcur(?:s|red|ring|rence|rences)?\b", re.I)
TOKEN = re.compile(r"[A-Za-z’'\-]+|\d+")


def header_line(line):
    """True when the line is empty or a byline / joining / index line with no opinion prose."""
    s = line.strip()
    if not s:
        return True
    if s.startswith("## "):
        return False
    if len(s) > MAX_LINE:
        return False
    if not (JUDGE_MARK.search(s) or KEYWORD.search(s)):
        return False
    for k, t in enumerate(TOKEN.findall(s)):
        if DISP.fullmatch(t) and (k == 0 or t[0].islower()):
            return False  # a disposition word (a capitalised one only as the first word: "Grant" may be a name)
        if t.isdigit():
            if len(t) > 2:
                return False
            continue
        if t[0].isupper():
            continue
        if t.lower().strip("’'-") not in VOCAB:
            return False
    return True


def header_block(text, a, b):
    """True when text[a:b] (from a section heading line to a mark) is the heading line plus header lines only."""
    nl = text.find("\n", a, b)
    if nl < 0:
        return True
    body = text[nl + 1:b]
    if len(body) > MAX_HEAD:
        return False
    return all(header_line(x) for x in body.split("\n"))


def mark_line(text, off):
    e = text.find("\n", off)
    return text[off:e if e >= 0 else len(text)]


def fix_parts(text, pm):
    """(new part map, [changes]) under rule PJ. pm: [(start, end, part, sec)] of common.part_map / part_map2.
    A change: (section start, mark offset, mark line, old part, new part, form) for each mark that is dropped."""
    out = []
    changes = []
    i = 0
    n = len(pm)
    while i < n:
        a, b, p, sec = pm[i]
        if p in BASE_PARTS and text.startswith("## ", a):
            j = i + 1
            end = b
            while j < n and pm[j][3] == sec and pm[j][2] in SEP_PARTS and pm[j][0] == end:
                m0 = pm[j][0]
                ml = mark_line(text, m0)
                if not (header_block(text, a, m0) and header_line(ml) and CONCUR.search(ml)):
                    break
                form = "index" if re.search(r"\b(?:Concurrence|Dissent)s?\s+by\b", ml) else "join"
                changes.append((a, m0, ml.strip()[:200], pm[j][2], p, form))
                end = pm[j][1]
                j += 1
            out.append((a, end, p, sec))
            i = j
            continue
        out.append(pm[i])
        i += 1
    return out, changes
