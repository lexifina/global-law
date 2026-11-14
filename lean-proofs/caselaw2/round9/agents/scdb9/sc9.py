"""scdb8 (round 8): Supreme Court merits dispositions that the v3 build does not attach to the decision under review.

    python -X utf8 sc8.py run [--procs 10]      -> work/rows_all.jsonl (with "_" diagnostics), work/diag8.jsonl.gz,
                                                   work/run_stats.json
    python -X utf8 sc8.py explain <node>        what the rules see for one decision

Base: round 7's `round7/agents/b4sc/sc7.py` (analyze7 = round 6's below_sc linker + R1/R2/R3), imported read-only;
nothing in round 6 / round 7 folders is written. Round-8 changes, each a general rule over every Supreme Court
opinion (RULES8 in NOTES.md):
  D1 abbreviation periods: a judgment sentence is read across the periods of abbreviations that do not end a sentence
     (the reader's own sentence-end test `common._is_end`): "the judgment of the U. S. Court of Appeals ... is
     vacated", "the judgment ... in No. 25-406 is reversed". Round 6's judgment patterns stopped at any period.
No answer-key file is read.
"""
import argparse, collections, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
B4 = os.path.join(C2, "round7", "agents", "b4sc")
sys.path.insert(0, B4)
import sc7  # noqa: E402  (round 7, read-only; imports round 6's link)

link = sc7.link
L, C, G = sc7.L, sc7.C, sc7.G
NL = chr(10)
WORK = os.path.join(HERE, "work")
MASK = "․"  # one-dot leader: same length, not a sentence end, not matched by [^.]

_orig_find = link.find_dispositions
FLAGS = {"d1": True, "d2": True, "r4": True, "aw": False}
# W (D8-5, claim anchorWide): the wider anchor-cue list, used only for rows that carry the claim (run with --on aw)
ANCHOR_WIDE = ["circuit", "(ca1", "(ca2", "(ca3", "(ca4", "(ca5", "(ca6", "(ca7", "(ca8", "(ca9", "(cadc", "(cafc", "c.a.",
               "judicial court", "court of errors", "case below"]
G8 = {"d1q": [], "d2": False, "r4": False, "s6": False}


def mask_abbrev(view):
    """`view` with every period that is not a sentence end (reader's _is_end) replaced by MASK (same length)."""
    if "." not in view:
        return view
    out = list(view)
    i = view.find(".")
    while i >= 0:
        if not C._is_end(view, i):
            out[i] = MASK
        i = view.find(".", i + 1)
    return "".join(out)


# D3 coordinated judgment verb: "we grant the petition for certiorari and reverse the judgment ...", "We accordingly
# leave ... to a future case, and reverse the judgment of the Court of Appeals"; and the per curiam line
# "Per Curiam: Reversed on the authority of ...". Round 6's S2 needed "we" right before the verb.
S2B = re.compile(r"\b[Ww]e\s+(?:(?:therefore|accordingly|now|thus|also|hereby)[\s,]+)?(?:grant|leave|hold|conclude|agree|answer|"
                 r"reject|accept|decline|find|dismiss)\b[^.;:]{0,200}?,?\s+and\s+(?:(?:therefore|accordingly|thus|now|hereby)"
                 r"[\s,]+)?(?P<v>reverse|vacate|affirm|modify)\s+(?:the|its|that)\s+(?:[\w’'.]+\s+){0,3}?(?:judgments?|decrees?|"
                 r"decision|orders?)\b")
PC_LINE = re.compile(r"^\W{0,3}Per\s+Curiam[.:]?\s+(?P<v>Reversed|Affirmed|Vacated|Judgment\s+(?:reversed|affirmed|vacated)|"
                     r"Decree\s+(?:reversed|affirmed|vacated))\b[^\n]{0,260}$")


def d3_dispositions(view, parts, have):
    out = []
    for a, b, p in parts:
        for m in S2B.finditer(view, a, b):
            v0 = m.start("v")
            s0, s1 = C.sentence_span(view, v0, m.end("v"))
            s0, s1 = max(s0, a), min(s1, b)
            if any(not (s1 <= x[0] or s0 >= x[1]) for x in have) or link.in_quote(view, s0, v0) or \
                    link.WOULD.search(view[s0:s1]) or sc7.MODAL_BAD.search(view[s0:v0].replace("We ", "", 1)):
                continue
            have.append((s0, s1))
            out.append({"q": (s0, s1), "form": "S2", "v0": v0, "verb": m.group("v").lower(), "part": p, "strong": True})
        pos = a
        for line in view[a:b].split(NL):
            l0 = pos
            pos += len(line) + 1
            st = line.strip()
            if not st or len(st) > 300:
                continue
            m = PC_LINE.match(st)
            if not m:
                continue
            q0 = l0 + (len(line) - len(line.lstrip()))
            q1 = q0 + len(st)
            if any(not (q1 <= x[0] or q0 >= x[1]) for x in have):
                continue
            have.append((q0, q1))
            vv = m.group("v").split()[-1].lower()
            out.append({"q": (q0, q1), "form": "LINE", "v0": q0 + m.start("v"), "verb": vv, "part": p, "strong": True})
    return out


# D2b printed judgment word: the reports print the judgment as the last word of the sentence on a line of its own
# ("... the judgment of the court below must be\nReversed."); round 6 read the line as a modal sentence (not strong).
MODAL_END = re.compile(r"\b(?:must|should|will|ought\s+to|is\s+to)[\s,]+(?:(?:therefore|accordingly|thus|consequently|"
                       r"also|now|necessarily)[\s,]+){0,2}be[ \t]*\n\W{0,2}$", re.I)
# D5 long subject: "The decision of the court below, according to which ..., is reversed." (a subject clause longer
# than round 6's 170 characters) when it is the last judgment sentence before "It is so ordered".
S1W = re.compile(r"\b(?:judgments?|decrees?|orders?|decisions?|convictions?)\b[^;:\n]{170,400}?\b(?:is|are)[\s,]+"
                 r"(?:(?:hereby|accordingly|therefore|thus)[\s,]+)?(?P<v>reversed|vacated|affirmed|modified)\b(?=[^\n]{0,4}$|"
                 r"[.,;])", re.I | re.M)


def d5_dispositions(view, parts, have):
    out = []
    a, b, p = parts[-1]
    so = None
    for m in link.SO_ORDERED.finditer(view, a, b):
        so = m
    if so is None:
        return out
    for m in S1W.finditer(view, max(a, so.start() - 1500), so.start()):
        v0 = m.start("v")
        s0, s1 = C.sentence_span(view, v0, m.end("v"))
        s0, s1 = max(s0, a), min(s1, b)
        if m.start() < s0 or any(not (s1 <= x[0] or s0 >= x[1]) for x in have) or link.in_quote(view, s0, v0) or \
                link.WOULD.search(view[s0:s1]) or sc7.MODAL_BAD.search(view[s0:s1]):
            continue
        have.append((s0, s1))
        out.append({"q": (s0, s1), "form": "S1", "v0": v0, "verb": m.group("v").lower(), "part": p, "strong": True})
    return out


def find_dispositions8(view, parts):
    base = _orig_find(view, parts)
    if FLAGS.get("d2", True):
        for d in base:
            if d["form"] == "S1" and not d["strong"] and view[d["v0"]].isupper() and \
                    MODAL_END.search(view[max(0, d["v0"] - 60):d["v0"]]):
                d["strong"] = True
                G8["d2"] = True
    if FLAGS.get("d3", True):
        extra = d5_dispositions(view, parts, [d["q"] for d in base])
        for d in extra:
            G8["d1q"].append(d["q"])
        base = sorted(base + extra, key=lambda d: d["q"])
    if FLAGS.get("d3", True):
        extra = d3_dispositions(view, parts, [d["q"] for d in base])
        for d in extra:
            d["d1"] = 1
            G8["d1q"].append(d["q"])
        base = sorted(base + extra, key=lambda d: d["q"])
    if not FLAGS["d1"]:
        return base
    mv = mask_abbrev(view)
    if mv is view:
        return base
    got = _orig_find(mv, parts)
    seen = {d["q"] for d in base}
    for d in got:
        if d["q"] not in seen and not any(not (d["q"][1] <= b["q"][0] or d["q"][0] >= b["q"][1]) for b in base):
            d["d1"] = 1
            G8["d1q"].append(d["q"])
            base.append(d)
    base.sort(key=lambda d: d["q"])
    return base


link.find_dispositions = find_dispositions8

# D2 modal judgment line, widened: round 7's R2 took "the judgment ... must be reversed" only with nothing between the
# auxiliary and "be"; the Court's older reports print "the judgment ... must accordingly be reversed", "the decree
# will, therefore, be Reversed", "the writ must, therefore, be dismissed".
MODAL_W = re.compile(r"\b(?:the|its|their|each|both|said|that|this)\s+(?:[\w’'.]+\s+){0,6}?(?:judgments?|decrees?|orders?|"
                     r"convictions?|writs?(?:\s+of\s+(?:error|certiorari))?|appeals?)\b[^;:]{0,200}?\b(?:must|should|will|"
                     r"ought\s+to|is\s+to)[\s,]+(?:(?:therefore|accordingly|thus|consequently|also|necessarily|now|"
                     r"in\s+(?:all\s+)?(?:respects|things)|for\s+(?:that|this|these)\s+reasons?|on\s+this\s+ground),?\s+){0,2}"
                     r"be\s+(?:reversed|vacated|affirmed|modified|dismissed)\b", re.I)
_orig_rd7 = sc7.read_disposition7


def read_disposition8(view, parts, disps):
    disp, why, modal = _orig_rd7(view, parts, disps)
    if disp is not None or why != "disp_not_strong" or not FLAGS.get("d2", True) or not disps:
        return disp, why, modal
    last = disps[-1]
    pa, pb = next((a, b) for a, b, p in reversed(parts) if a <= last["q"][0] < b)
    if (pa, pb) != (parts[-1][0], parts[-1][1]):
        return None, "disp_not_strong", False
    q0, q1 = last["q"]
    sent = mask_abbrev(view[q0:q1])
    if link.WOULD.search(sent) or not MODAL_W.search(sent) or sc7.MODAL_BAD.search(sent):
        return None, "disp_not_strong", False
    so = link.SO_ORDERED.search(view, q1, min(pb, q1 + 600))
    rest = view[q1:pb].strip()
    para_end = re.match(r"[ \t]*(?:\n|$)", view[q1:q1 + 3]) is not None
    late = (q0 - pa) >= 0.65 * (pb - pa)
    if not (so or len(rest) <= 600 or (para_end and late)):
        return None, "disp_not_strong", False
    d2 = dict(last)
    d2["strong"] = True
    d2["d2"] = 1
    disps2 = [d for d in disps if d is not last] + [d2]
    disps2.sort(key=lambda d: d["q"])
    disp, why = link.read_disposition(view, parts, disps2)
    if disp is not None:
        G8["d2"] = True
    return disp, why, disp is not None


sc7.read_disposition7 = read_disposition8

# R4 rehearing-denial orders are not the judgment under review: a citation whose own sentence (or, for a bare
# citation, the sentence before it) reports only that rehearing (en banc) was denied ("Rehearing en banc was denied.
# 201 F. 2d 254"; "That court subsequently denied a petition for rehearing and rehearing en banc. 392 F. 2d 220";
# "Six members ... dissented from the failure to grant rehearing en banc. 89 F. 3d 1169") is the order denying
# rehearing; round 6 caught only "rehearing denied, <cite>" with no period between. Such a citation is no anchor, so
# the latest remaining decision of that court (the judgment itself) is the target. A sentence that also reports the
# court's judgment (affirmed / reversed / held ...) keeps round 6's reading.
_REH_PHRASE = re.compile(r"(?:den(?:ied|ying|ial\s+of)\s+(?:[\w’']+\s+){0,6}?rehear\w*(?:\s+(?:en|in)\s+banc)?|"
                         r"rehear\w*(?:\s+(?:en|in)\s+banc)?\s+(?:was\s+|were\s+|is\s+|had\s+been\s+|has\s+been\s+)?"
                         r"(?:denied|refused)|(?:failure|refusal|declin\w*|refus\w*)\s+(?:\w+\s+){0,3}?(?:to\s+)?(?:grant\s+)?"
                         r"rehear\w*(?:\s+(?:en|in)\s+banc)?)", re.I)
_REH_TAIL = re.compile(r"^[^.;]{0,80}?[.,]?[”\"’)\]]*\s*$")
_JUDG_WORD = re.compile(r"\b(?:affirm\w*|revers\w*|vacat\w*|held|hold\w*|conclud\w*|rul(?:ed|ing)|decided|dismiss\w*|"
                        r"enter\w*\s+judgment)\b", re.I)
_orig_rehden = link.REHDEN


class _Rehden8:
    def search(self, s, *a):
        m = _orig_rehden.search(s, *a)
        if m or not FLAGS.get("r4", True):
            return m
        for mm in _REH_PHRASE.finditer(s):
            if not _REH_TAIL.match(s[mm.end():]):
                continue
            # the sentence holding the phrase, up to the citation
            st = max(s.rfind(". ", 0, mm.start()), s.rfind("; ", 0, mm.start()), -1) + 1
            if _JUDG_WORD.search(s[st:mm.start()]) or _JUDG_WORD.search(s[mm.end():]):
                continue
            G8["r4"] = True
            return mm
        return None


link.REHDEN = _Rehden8()


class _Later8:
    """round 6's LATER without "rehearing en banc" when the phrase says rehearing en banc was refused (R4)."""
    def __init__(self, rx):
        self.rx = rx

    def finditer(self, s, a=0, b=None):
        b = len(s) if b is None else b
        for m in self.rx.finditer(s, a, b):
            if FLAGS.get("r4", True) and re.match(r"rehearing", m.group(0), re.I):
                pre = s[max(0, m.start() - 60):m.start()]
                if re.search(r"(?:den(?:ied|ying|ial\s+of)|failure|refus\w*|declin\w*)\s+(?:[\w’']+\s+){0,6}?(?:to\s+)?"
                             r"(?:grant\s+)?$", pre, re.I):
                    continue
            yield m

    def search(self, s, *a):
        return next(iter(self.finditer(s, *a)), None)


link.LATER = _Later8(link.LATER)


# A5 head-matter block anchor: a citation of the head matter (syllabus line "227 Fed. Rep. 93, reversed.", "Reported
# below", a head-matter sentence naming the court) whose own lines hold no anchor cue is anchored by the head-matter
# block that runs from the reporter's court line ("CERTIORARI TO / ERROR TO / APPEAL FROM THE ...", which holds the cue)
# to the end of the citation's line, inside one head-matter part, at most HM_BLOCK_MAX characters, with no anchor
# disqualifier. Round 6 extended an anchor by at most two sentences / 1,400 characters, which the syllabus between the
# court line and the citation line usually exceeds.
HM_BLOCK_MAX = 8000
_orig_build_row = link.build_row


def build_row8(n, view, t, an, kind, scope, dq, flags, src, in_zone, multi, date):
    row = _orig_build_row(n, view, t, an, kind, scope, dq, flags, src, in_zone, multi, date)
    if not (isinstance(row, str) and row == "anchor_no_cue") or not FLAGS.get("a5", True):
        return row
    for o in an:
        if o["part"] != "headmatter":
            continue
        lo, hi = o["lo"], o["hi"]
        hm = None
        for m in link.HM_LINE.finditer(view, lo, o["c"][0]):
            hm = m
        if hm is None:
            continue
        a0 = hm.start()
        e = view.find(NL, o["c"][1], hi)
        a1 = hi if e < 0 else e
        a0, a1 = link.trim(view, a0, a1)
        if a1 - a0 > HM_BLOCK_MAX:
            continue
        q = L.norm(view[a0:a1])
        if not link.has_cue(q) or link.has_disq(q):
            continue
        cq = link.compact(q)
        key = o["ikey"] if link.compact(o["ikey"]) in cq else o["key"]
        if not key or link.compact(key) not in cq:
            continue
        o2 = dict(o)
        o2["ctx0"], o2["s"] = a0, (a0, a1)
        r2 = _orig_build_row(n, view, t, [o2], kind, scope, dq, flags, src, in_zone, multi, date)
        if isinstance(r2, str):
            continue
        r2["anchor"] = [a0, a1]
        r2["anchor_part"] = "headmatter"
        r2["_a5"] = 1
        return r2
    return row


link.build_row = build_row8

# S6 own-case "See" sentence: a citation sentence that is only "See <citation>" (no case name, nothing else before
# the citation) supports the sentence before it; in the procedural history ("A divided panel of the Court of Appeals
# for the Tenth Circuit affirmed. See 210 F. 3d 1247 (2000).") it cites the decision that sentence reports. Round 6
# treated every "See" as a signal (a citation of other authority). The anchor rules (court phrase of the target's
# court in the previous sentence, history zone, name guard) then apply unchanged; "see also" stays a disqualifier.
_orig_signal = link.SIGNAL


class _Signal8:
    def search(self, s, *a):
        if FLAGS.get("s6", True) and re.fullmatch(r"\s*See\s*", s):
            G8["s6"] = True
            return None
        return _orig_signal.search(s, *a)


link.SIGNAL = _Signal8()

# T1 direct review of a trial court: round 6 refused a trial-court target when ANY decision of a higher court had an
# anchor in the opinion or the words "court of appeals" occurred anywhere (authorities of other cases count), and its
# direct-review cue list missed the usual forms ("The three-judge Federal District Court ...", "A District Court of
# three judges", "specially constituted District Court", "Appeals from a final decree of the District Court", "here on
# direct appeal"). T1: the cue list is widened, and only decisions of THIS litigation count against a trial court:
# a higher-court decision whose caption shares a party token with the acting caption, and a "court of appeals" phrase
# only inside the history zone (before "we granted / noted probable jurisdiction") or the head matter.
DIRECT8 = re.compile(link.DIRECT.pattern + r"|\bcourt\s+of\s+three\s+judges\b|\bthree\s+judges\b|\bspecially\s+constituted\b|"
                     r"\bstatutory\s+(?:three-judge\s+)?court\b|\bappeals?\s+from\s+(?:a\s+|the\s+)?(?:final\s+)?(?:decree|"
                     r"judgment|order)s?\s+of\s+(?:a\s+|the\s+)?(?:United\s+States\s+|specially\s+constituted\s+|"
                     r"three-judge\s+)?(?:District|Circuit)\s+Court\b|\bhere\s+on\s+(?:a\s+)?direct\s+appeal\b|"
                     r"§\s?(?:266|380|345|29)\b", re.I)


def trial_ok8(J, view, op_parts, hm_parts, ph_end, toks_low):
    """T1: may a trial court be the target? (direct cue, no court-of-appeals step of this litigation)"""
    direct = any(DIRECT8.search(view, a, min(b, a + 6000)) for a, b, _p in op_parts) or \
        any(DIRECT8.search(view, a, b) for a, b in hm_parts)
    if not direct:
        return False
    lit_hi = [d for d in J if sc7.level(d["ci"]) > 0 and link.name_share(d["j"], toks_low)]
    if lit_hi:
        return False
    zone = [(a, min(b, ph_end) if ph_end else min(b, a + 6000)) for a, b, _p in op_parts[:1]]
    if any(link.COA_WORD.search(view, a, b) for a, b in zone + [(a, b) for a, b in hm_parts]):
        return False
    return True


# K1 docket-numbered judgments: "The judgment in No. 47 is reversed, and the judgment in No. 48 is affirmed." Round 6
# gives every target of such an opinion scope unknown, which marks an affirmed decision as uncertain. K1 (round-8 rows
# only): the target's docket is the one docket number printed in its anchor sentence; the clause of the judgment
# sentence holding that number gives the kind (scope all unless a partial word is in that clause). When the target's
# docket cannot be found, or its clause holds two kinds, no round-8 row is made.
DOCK = re.compile(r"\bNos?\.\s*(\d{1,5}(?:\s*(?:,|and|&)\s*\d{1,5})*)", re.I)
KCL_SPLIT = re.compile(r";|,?\s+and\s+(?=(?:the|that|those|its|we|in)\b)|,\s+(?=(?:the|that|those)\s+(?:judgments?|decrees?)\b)|"
                       r"\bwhile\b|\bbut\b", re.I)


def docket_nums(s):
    out = set()
    for m in DOCK.finditer(s):
        out |= set(re.findall(r"\d{1,5}", m.group(1)))
    return out


def docket_fix(view, row):
    """None (keep as is), "drop", or (kind, scope)."""
    q0, q1 = row["disp"]
    q = view[q0:q1]
    if not DOCK.search(q):
        return None
    # the judgment cluster: the quote and the judgment sentences up to 700 characters before it
    w0 = max(0, q0 - 700)
    pre = view[w0:q0]
    cut = max(pre.rfind(NL + NL), -1)
    q = view[w0 + cut + 1 if cut >= 0 else w0:q1]
    pieces = []
    pos = 0
    for m in KCL_SPLIT.finditer(q):
        pieces.append(q[pos:m.start()])
        pos = m.end()
    pieces.append(q[pos:])
    kinds_by = {}
    cur = set()
    allk = set()
    for p in pieces:
        nums = docket_nums(p)
        st = link.stems(p) & {"affirm", "revers", "vacat", "modif", "dismiss"}
        allk |= st
        if nums:
            cur = nums
        for x in (nums or cur):
            kinds_by.setdefault(x, set()).update(st)
    if len(allk & {"affirm", "revers", "vacat"}) < 2 and not (allk >= {"affirm"} and "dismiss" in allk):
        return None
    if row["anchor"] is None:
        return "drop"
    a0, a1 = row["anchor"]
    nums = docket_nums(view[a0:a1])
    if len(nums) != 1:
        return "drop"
    k = kinds_by.get(next(iter(nums)), set())
    if len(k) != 1:
        return "drop"
    kind = {"affirm": "affirmed", "revers": "reversed", "vacat": "vacated", "modif": "modified",
            "dismiss": "reviewDismissed"}[next(iter(k))]
    seg = next((p for p in pieces if next(iter(nums)) in docket_nums(p)), "")
    return kind, ("unknown" if link.PARTIAL.search(seg) or kind == "modified" else "all")


import sc8sel  # noqa: E402
sc8sel.FLAGS = FLAGS
sc8sel.trial_ok8 = trial_ok8
sc7.strict = sc8sel.strict8
sc7.loose = sc8sel.loose8

# ===================================================================================================================
# ROUND 9 (scdb9). Every rule below is a general rule over every Supreme Court opinion; flags for leave-one-out runs.
#   j1  "we vacate its judgment": round 6's S2 refused "its" after the verb (meant for "reverse its holding")
#   j2  "The case is (therefore) reversed (and remanded)": the case / cause as the subject of the judgment verb
#   j3  "set aside": "The judgment is set aside", "We set aside the judgment of ..." read as vacated (claim setAside)
#   j4  comma-list GVR line: "we grant the petition ... and <motion>, vacate the judgment of ..., and remand"
#   r4w R4 vocabulary widened: "declined ...'s request for en banc review", "an evenly divided court denied ... en banc
#       review", words split by a line-break hyphen inside the phrase ("Ger- many's")
#   a9  anchor of a sentence whose subject is the court named just before ("It reversed ... 87 F.2d 243.", "That court
#       ordered ... 409 F. Supp. 831.") or that is only the own case's name + citation ("Everhart v. Bowen, 853 F. 2d
#       1532 (1988).") after a sentence naming the court: typed A3 (weak: round 7's R3 sole/latest test applies)
#   D-fix (diagnostics for select9): "_reh9" the target's anchoring occurrence is a rehearing-denial citation (the
#       phrase between the previous citation / sentence start and the citation, or in the parentheticals right after
#       it); "_sole9"/"_latest9" round 7's R3 test with rehearing-denial-only decisions and same-court same-date
#       decisions (parallel reports) not counted as competitors.
# ===================================================================================================================
FLAGS.update({"j1": True, "j2": True, "j3": True, "j4": True, "r4w": True, "a9": True})
G9 = {"jq": []}
_ADV9 = r"(?:(?:therefore|accordingly|thus|hereby|now|also|must|shall|will|again|do)[\s,]+){0,2}"
J1 = re.compile(r"\b[Ww]e\s+" + _ADV9 + r"(?P<v>affirm|reverse|vacate|modify)\s+(?:its|their)\s+(?:judgments?|decrees?|"
                r"orders?|decision)\b")
J2 = re.compile(r"\b(?:[Tt]he|[Tt]his|[Ee]ach)\s+(?:case|cause)s?\s+(?:is|are)[\s,]+(?:(?:therefore|accordingly|hereby|thus)[\s,]+)?"
                r"(?P<v>reversed|vacated)\b")
J3 = re.compile(r"\b(?:judgments?|decrees?|orders?)\b[^.;:\n]{0,170}?\b(?:is|are)[\s,]+(?:(?:hereby|therefore|accordingly|thus)"
                r"[\s,]+)?(?P<v>set\s+aside)\b|\b[Ww]e\s+" + _ADV9 + r"(?P<v2>set\s+aside)\s+(?:the|its|that)\s+"
                r"(?:[\w’'.]+\s+){0,3}?(?:judgments?|decrees?|orders?|decision)\b")
J4 = re.compile(r"\b[Ww]e\s+(?:(?:therefore|accordingly|now|thus|hereby)[\s,]+)?grant\b[^.;:]{0,260}?,\s+(?P<v>reverse|vacate)\s+"
                r"(?:the|its)\s+(?:[\w’'.]+\s+){0,5}?(?:judgments?|decrees?|decision|orders?)\b")


def j_dispositions(view, parts, have):
    out = []
    for a, b, p in parts:
        for rx, fl in ((J1, "j1"), (J2, "j2"), (J3, "j3"), (J4, "j4")):
            if not FLAGS.get(fl, True):
                continue
            for m in rx.finditer(view, a, b):
                g = "v" if m.group("v") else "v2"
                v0 = m.start(g)
                s0, s1 = C.sentence_span(view, v0, m.end(g))
                s0, s1 = max(s0, a), min(s1, b)
                if any(not (s1 <= x[0] or s0 >= x[1]) for x in have) or link.in_quote(view, s0, v0) or \
                        link.WOULD.search(view[s0:s1]) or sc7.MODAL_BAD.search(view[s0:v0].replace("We ", "", 1)) or \
                        re.search(r"\b(?:if|unless|should|would|whether)\b", view[s0:v0], re.I):
                    continue
                have.append((s0, s1))
                verb = m.group(g).lower()
                out.append({"q": (s0, s1), "form": "S2" if view[v0 - 1:v0] == " " and fl != "j2" else "S1", "v0": v0,
                            "verb": "vacate" if verb.startswith("set") else verb, "part": p, "strong": True, "j9": fl})
    return out


_find8 = link.find_dispositions


def find_dispositions9(view, parts):
    base = _find8(view, parts)
    extra = j_dispositions(view, parts, [d["q"] for d in base])
    for d in extra:
        G9["jq"].append((d["q"], d["j9"]))
    return sorted(base + extra, key=lambda d: d["q"])


link.find_dispositions = find_dispositions9
_STEM0 = link.STEM


def _stem_set():
    if FLAGS.get("j3", True):
        return tuple((k, re.compile(r"\bvacat(?:ed|e|es)\b|\bset\s+aside\b", re.I)) if k == "vacat" else (k, rx)
                     for k, rx in _STEM0)
    return _STEM0


# r4w: wider rehearing-denial phrase (the citation's own sentence before the citation)
_W = r"[\w’'.\-]+"
REH9 = re.compile(r"(?:den(?:ied|ying|ial\s+of)|declin\w*|refus\w*|fail\w*\s+to\s+grant|dissent\w*\s+from\s+(?:the\s+)?(?:denial|order\s+"
                  r"denying))\s+(?:" + _W + r"\s+){0,6}?(?:rehear\w*|reconsideration|(?:en|in)\s+banc(?:\s+(?:review|rehearing|"
                  r"consideration|reconsideration|hearing|petition))?)|(?:rehear\w*|(?:en|in)\s+banc\s+(?:review|rehearing|"
                  r"consideration|reconsideration|hearing))\s+(?:was\s+|were\s+|is\s+|had\s+been\s+|has\s+been\s+)?"
                  r"(?:denied|refused|declined)|(?:petition|request|motion|suggestion)\s+for\s+(?:rehear\w*|(?:en|in)\s+banc\s+"
                  r"\w+)\s+(?:was\s+|were\s+)?(?:denied|refused|declined)", re.I)
_REH8 = _REH_PHRASE


class _Rehden9:
    def search(self, s, *a):
        m = _R8.search(s, *a)
        if m or not FLAGS.get("r4w", True) or not FLAGS.get("r4", True):
            return m
        for mm in REH9.finditer(s):
            if not re.match(r"^[^.;]{0,80}?[.,]?[”\"’)\]]*\s*$", s[mm.end():]):
                continue
            st = max(s.rfind(". ", 0, mm.start()), s.rfind("; ", 0, mm.start()), -1) + 1
            if _JUDG_WORD.search(s[st:mm.start()]) or _JUDG_WORD.search(s[mm.end():]):
                continue
            G8["r4"] = True
            return mm
        return None


_R8 = _Rehden8()
link.REHDEN = _Rehden9()
_CITE_END = re.compile(r"\d{1,4}\s+[A-Z][A-Za-z.\s()0-9]{0,24}?\s+\d{1,5}(?:[,\s\-–\d]{0,20})?(?:\([^()]{0,40}\))?")


def reh_occ(view, o):
    """R4b: the occurrence is a rehearing-denial citation (phrase between the previous citation or the sentence start
    and this citation, or inside the parentheticals right after it)."""
    s0 = o["s"][0]
    c0, c1 = o["c"]
    before = view[s0:c0]
    last = None
    for m in _CITE_END.finditer(before):
        last = m
    seg = before[last.end():] if last else before
    if REH9.search(seg) or _orig_rehden.search(seg + " "):
        return True
    after = view[c1:min(o["s"][1] + 200, c1 + 300)]
    m = re.match(r"(?:,\s*\d[\d\-–, n.]*)?\s*(?:\([^()]{0,60}\)\s*)*\((?P<p>[^()]{0,200})\)", after)
    while m:
        if REH9.search(m.group("p")) or re.search(r"rehear|en\s+banc", m.group("p"), re.I) and \
                re.search(r"den|declin|dissent", m.group("p"), re.I):
            return True
        break
    return False


def a9_upgrade(cands, ctx):
    """a9: occurrences without a type in the history zone whose sentence's subject is the court named just before, or
    that are only the own case's name and the citation, become A3 (a court phrase of the target's court within 700
    characters before)."""
    view, ph_end = ctx["view"], ctx["ph_end"]
    if ph_end is None:
        return
    for d in cands.values():
        for o in d["occ"]:
            if o["typ"] is not None or o["part"] == "headmatter" or o["c"][0] >= ph_end or o["rehden"] or o["sig"] or \
                    o["disq"]:
                continue
            s0 = o["s"][0]
            sent0 = view[s0:o["c"][0]]
            pron = re.match(r"\W{0,3}(?:(?:On|In|After|Upon)\s+[^,]{1,60},\s+)?(?:It|That\s+court|The\s+court(?:\s+below)?|"
                            r"That\s+tribunal|The\s+panel(?:\s+majority)?|The\s+majority)\s+(?:(?:also|then|therefore|thus|"
                            r"further|moreover|nevertheless|accordingly|again|however|first|ultimately|eventually|"
                            r"subsequently|initially)[\s,]+)?(?:held|affirmed|reversed|vacated|ordered|dismissed|concluded|ruled|"
                            r"rejected|agreed|found|decided|sustained|upheld|denied|granted|entered|remanded|set\s+aside|"
                            r"determined|refused|declined|reasoned|struck)\b", sent0)
            own = (o["named"] not in (None, "other") and re.fullmatch(r"\W{0,3}[^.;:]{3,140}?,\s*", sent0) is not None
                   and re.search(r"\bv\.\s", sent0) is not None)
            if not (pron or own):
                continue
            w0 = max(o["lo"], s0 - 700)
            if any(link.ph_match(p, d["ci"]) == 2 for p in link.phrases(view, w0, s0)):
                o["typ"] = "A3"
                o["a9"] = "pron" if pron else "own"


_strict8 = sc7.strict


def strict9(cands, ctx):
    if FLAGS.get("a9", True):
        a9_upgrade(cands, ctx)
    return _strict8(cands, ctx)


sc7.strict = strict9
_finish7 = sc7.finish


def finish9(row, t, cands, ctx):
    _finish7(row, t, cands, ctx)
    view = ctx["view"]
    toks_low = ctx["toks_low"]
    an = [o for o in t["occ"] if sc7.good(o)]
    if row.get("anchor"):
        a0, a1 = row["anchor"]
        an = [o for o in t["occ"] if a0 <= o["c"][0] < a1] or an
    row["_reh9"] = int(bool(an) and all(reh_occ(view, o) for o in an))
    row["_a9"] = next((o.get("a9") for o in an if o.get("a9")), "")

    def reh_only(d):
        return all(reh_occ(view, o) for o in d["occ"])
    lit = [d for d in cands.values() if link.name_share(d["j"], toks_low) and d["j"] != t["j"]]
    lit = [d for d in lit if not reh_only(d) and not (d["court"] == t["court"] and d["date"] == t["date"])]
    same = [d for d in lit if sc7.group_key(d) == sc7.group_key(t) and sc7.level(d["ci"]) == sc7.level(t["ci"])]
    later = [d for d in lit if d["date"] > t["date"]]
    row["_sole9"] = int(not same)
    row["_latest9"] = int(not later)


sc7.finish = finish9


_kind_for6 = link.kind_for
_SETASIDE = re.compile(r"(?<![A-Za-z])set(\s+)aside(?![A-Za-z])", re.I)


def kind_for9(view, disp, ci):
    """j3: a clause whose judgment verb is "set aside" carries the cue of vacated (same-length stand-in view)."""
    r = _kind_for6(view, disp, ci)
    if FLAGS.get("j3", True) and r[0] is None and r[1] == "disp_no_cue_quote" and _SETASIDE.search(view):
        v2 = _SETASIDE.sub(lambda m: "vacat" + "x" * (len(m.group(0)) - 5), view)
        r2 = _kind_for6(v2, disp, ci)
        if r2[0] is not None:
            return r2
    return r


link.kind_for = kind_for9


def view_of(text):
    body0 = 0
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    return C.unwrap_view(text, body0) if C.hard_wrapped(text, body0) else text


def analyze8(n, text, date):
    G8["d1q"] = []
    G8["d2"] = False
    G8["r4"] = False
    G9["jq"] = []
    d = sc7.analyze7(n, text, date)
    d["r4"] = int(G8["r4"])
    d["d2"] = int(G8["d2"])
    for r in d["rows"]:
        r["_d2"] = int(G8["d2"])
        q0, q1 = r["disp"]
        r["_d1"] = int(any(a <= q0 and q1 <= b for a, b in G8["d1q"]))
        r["_j9"] = next((f for (a, b), f in G9["jq"] if a <= q0 and q1 <= b), "")
    d["d1"] = int(any(r["_d1"] for r in d["rows"])) if d["rows"] else int(bool(G8["d1q"]))
    if d["rows"]:
        view = view_of(text)
        for r in d["rows"]:
            fx = docket_fix(view, r)
            r["_dock"] = fx if fx is None or fx == "drop" else list(fx)
    return d


def work_run(arg):
    path, off = arg[0], arg[1]
    on = arg[2] if len(arg) > 2 else ()
    for k in off:
        FLAGS[k] = False
    for k in on:
        FLAGS[k] = True
    sc7.init7()
    link.STEM = _stem_set()
    if FLAGS.get("aw") and not G8.get("aw_done"):
        link.ANCHOR_CUES.extend(c for c in ANCHOR_WIDE if c not in link.ANCHOR_CUES)
        G8["aw_done"] = True
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            try:
                d = analyze8(r["n"], r["text"], r["date"])
            except Exception as ex:
                d = {"n": r["n"], "date": r["date"], "rows": [],
                     "reason": "error:" + type(ex).__name__ + ":" + str(ex)[:80]}
            d["type"] = r["type"]
            d["len"] = len(r["text"])
            out.append(d)
    return out


def run(procs, off=(), tag="", on=()):
    os.makedirs(WORK, exist_ok=True)
    rows = []
    st = collections.Counter()
    with gzip.open(os.path.join(WORK, "diag9%s.jsonl.gz" % tag), "wt", encoding="utf-8", newline=NL, compresslevel=3) as fd:
        for res in L.pmap(work_run, [(p, tuple(off), tuple(on)) for p in link.shard_files()], procs=procs):
            for d in res:
                st["decisions"] += 1
                if d["rows"]:
                    st["decisions_with_row"] += 1
                else:
                    r = d["reason"] or "?"
                    st["no_row:" + (r.split(":")[0] + ":" + r.split(":")[1] if r.startswith("error") else r)] += 1
                rows.extend(d["rows"])
                fd.write(json.dumps(d, ensure_ascii=False, default=str) + NL)
    rows.sort(key=lambda r: (r["by"], r["target"]))
    with open(os.path.join(WORK, "rows_all%s.jsonl" % tag), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    st["rows"] = len(rows)
    json.dump(st, open(os.path.join(WORK, "run_stats%s.json" % tag), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("node", nargs="?")
    ap.add_argument("--procs", type=int, default=10)
    ap.add_argument("--off", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--on", default="")
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.procs, [x for x in a.off.split(",") if x], a.tag, [x for x in a.on.split(",") if x])
    elif a.cmd == "explain":
        sc7.init7()
        link.STEM = _stem_set()
        n = int(a.node)
        sha, text = L.fetch_texts([n])[n]
        d = analyze8(n, text, int(G["F"].date[n]))
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print("reason:", d.get("reason"), "| reasons:", d.get("reasons"), "| ph_end:", d.get("ph_end"), "| modal:",
              d.get("modal"))
        print("disp:", d.get("disp_text"))
        for c in d.get("cands", []):
            print(" cand", c["j"], c["date"], G["F"].court_name(c["court"]), "rp" if c["rp"] else "",
                  sc7.title_of(c["j"])[:60])
            for o in c["occ"]:
                print("    ", o, "|", L.norm(text[max(0, o[0] - 90):o[0] + 40]))
        for r in d["rows"]:
            print("ROW", json.dumps({k: v for k, v in r.items()}, ensure_ascii=False)[:600])
            print("   disp :", L.norm(text[r["disp"][0]:r["disp"][1]]))
            if r["anchor"]:
                print("   anchor:", L.norm(text[r["anchor"][0]:r["anchor"][1]]))


if __name__ == "__main__":
    main()
