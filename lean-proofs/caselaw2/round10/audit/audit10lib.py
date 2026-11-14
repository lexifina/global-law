"""Shared helpers of the round-10 blind audit (decoys10.py, make_packs10.py, more_text10.py, score_audit10.py,
selftest10.py). Port of round7/audit/audit7lib.py; round-10 rows (`t10:` / `h10:` ids of round10/certify10.py) and every
earlier layout load the same way (the id prefix is never interpreted).

Inputs touched: certified deltas (round 5/6/7/8 layouts) and stage folders, the round-5, round-6 and round-7 audit
folders (keys, answers, verdicts: for decoys only), graph/nodes.tsv, the node facts of round6/history/r6lib.py, the
reader's common.py (part map, citation keys, name tokens) and the decision texts in git. Never read (DESIGN8 section
0): gold/, round5/gold_fresh/, round6/shepardized/, round6/history/split/, round7/heldout/, SCDB / CRS files, any
reports.tsv, the Shadow Docket Database, anything under benchmarks/. Every file written goes under round10/audit/.
"""
import hashlib
import json
import math
import os
import random
import re
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))   # .../caselaw-lean-2/round10/audit
R8 = os.path.dirname(HERE)
C2 = os.path.dirname(R8)
R7A = os.path.join(C2, "round7", "audit")
BASE_STAGE = os.path.join(C2, "round9", "stage", "v9c")
R5A = os.path.join(C2, "round5", "audit")
R6H = os.path.join(C2, "round6", "history")
R6A = os.path.join(R6H, "audit")
WORKROOT = os.path.dirname(C2)
GRAPH = os.path.join(WORKROOT, "graph")
TOOLS = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2")
CUE_TABLE = os.path.join(TOOLS, "cues", "cue_table.json")
NL = chr(10)
TAB = chr(9)

# ---- kinds ---------------------------------------------------------------------------------------------------------
T_STATUS = ("overruled", "abrogated", "disapproved", "recededFrom")          # treatments kinds that change a status
T_LIMIT = ("limited", "questioned", "criticized", "declinedToFollow")
H_STATUS = ("reversed", "vacated", "withdrawn", "substitutedBy", "rehearingEnBancGranted")
H_OTHER = ("affirmed", "certDenied", "modified", "reviewDismissed", "reinstated")

TREAT_COLS = ["id", "by", "target", "date", "kind", "scope", "temporal", "explicit", "text_sha", "start", "end",
              "quote", "evidence", "part", "src", "confidence"]
HIST_COLS = ["id", "target", "by", "date", "kind", "scope", "text_sha", "start", "end", "quote", "evidence", "part",
             "src"]

# ---- type-A answers (what a court does or says about X) ------------------------------------------------------------
ACTS = ("overrule", "reject_doctrine", "limit", "report_other", "nothing", "other", "unsure")
EXTENTS = ("whole", "part", "other_grounds", "unclear")
# A row's effect class -> acts that agree with it (right = speaks_of_x yes, own_opinion yes, act in the set, and for
# report_* the other decision named by the auditor is the row's Y). *_whole needs extent `whole` for right_extent.
A_COMPAT = {
    "own_whole":    {"overrule"},
    "own_part":     {"overrule", "reject_doctrine"},
    "doctrine":     {"reject_doctrine", "overrule"},
    "report_whole": {"report_other"},
    "report_part":  {"report_other"},
    "limit":        {"limit"},
}
A_NEEDS_WHOLE = {"own_whole", "report_whole"}

# ---- type-B answers (history; the round-6 brief) -------------------------------------------------------------------
DISPOSITIONS = ("affirmed", "reversed", "vacated", "reversed_or_vacated_in_part", "modified",
                "withdrawn_or_superseded", "rehearing_en_banc_only", "review_denied", "review_dismissed",
                "reinstated", "none", "other")
B_COMPAT = {
    "reversed":               {"reversed"},
    "vacated":                {"vacated"},
    "withdrawn":              {"withdrawn_or_superseded"},
    "substitutedBy":          {"withdrawn_or_superseded"},
    "rehearingEnBancGranted": {"rehearing_en_banc_only", "vacated", "withdrawn_or_superseded"},
    "affirmed":               {"affirmed"},
    "modified":               {"modified"},
    "certDenied":             {"review_denied"},
    "reviewDismissed":        {"review_dismissed"},
    "reinstated":             {"reinstated"},
    "writRefused":            {"review_denied"},
    "remanded":               {"other", "vacated"},
    "reviewGranted":          {"other"},
    "depublished":            {"other"},
    "other":                  {"other"},
}
B_COMPAT_PARTIAL = {"reversed": {"reversed_or_vacated_in_part"}, "vacated": {"reversed_or_vacated_in_part"}}
B_NEGATIVE = {"reversed", "vacated", "withdrawn_or_superseded"}
B_NEUTRAL = {"affirmed", "modified", "review_denied", "review_dismissed", "reinstated"}

YNU = {"yes": "yes", "y": "yes", "true": "yes", "1": "yes", "no": "no", "n": "no", "false": "no", "0": "no",
       "unsure": "unsure", "unclear": "unsure", "unknown": "unsure", "": "unsure", "none": "unsure", "n/a": "no"}


def utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline=NL)
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def resolve(path, must_exist=True):
    """Absolute, or relative to the current directory, caselaw-lean-2 or round10/audit (first that exists). A path
    that need not exist is taken relative to caselaw-lean-2 when it starts with `round`, else to round10/audit."""
    if os.path.isabs(path):
        return os.path.normpath(path)
    cands = [os.path.abspath(path), os.path.join(C2, path), os.path.join(HERE, path)]
    for c in cands:
        if os.path.exists(c):
            return os.path.normpath(c)
    if must_exist:
        sys.exit("not found: %s (tried %s)" % (path, "; ".join(cands)))
    first = path.replace("\\", "/").split("/")[0]
    return os.path.normpath(cands[1] if first.startswith("round") else cands[2])


def must_be_under_audit(path):
    p = os.path.normcase(os.path.abspath(path))
    if not (p + os.sep).startswith(os.path.normcase(HERE) + os.sep):
        sys.exit("refusing to write outside %s: %s" % (HERE, path))


def read_tsv(path, minf=1):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            line = line.rstrip(NL).rstrip("\r")
            if line:
                p = line.split(TAB)
                if len(p) >= minf:
                    rows.append(p)
    return rows


def write_text(path, text):
    must_be_under_audit(path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline=NL) as f:
        f.write(text)


def clean_cell(x):
    return str(x).replace(TAB, " ").replace(NL, " ").replace("\r", " ")


def write_tsv(path, rows):
    write_text(path, "".join(TAB.join(clean_cell(x) for x in r) + NL for r in rows))


def read_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def iso_date(d):
    d = int(d or 0)
    if d <= 0:
        return "date unknown"
    return "%04d-%02d-%02d" % (d // 10000, d // 100 % 100, d % 100)


def wilson(k, n, z=1.959964):
    """Wilson 95% interval; k and n may be fractional. -> (p, lo, hi) or (None,)*3."""
    if not n or n <= 0:
        return (None, None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(max(0.0, p * (1 - p) / n + z * z / (4 * n * n))) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def ynu(x):
    s = "yes" if x is True else "no" if x is False else str("" if x is None else x).strip().lower()
    return YNU.get(s)


# ---- libraries -----------------------------------------------------------------------------------------------------
def r6lib():
    if R6H not in sys.path:
        sys.path.insert(0, R6H)
    import r6lib as L
    return L


def reader_common():
    return r6lib().reader_common()


def operative_whole_phrases():
    try:
        with open(CUE_TABLE, encoding="utf-8") as f:
            return [x.lower() for x in json.load(f).get("operative_whole", [])]
    except Exception:
        return None


# ---- certified tables ----------------------------------------------------------------------------------------------
def _int(x, d=0):
    try:
        return int(x)
    except (TypeError, ValueError):
        return d


def treat_row(p):
    if len(p) < 14:
        return None
    r = dict(zip(TREAT_COLS, p + [""] * (16 - len(p))))
    try:
        r["by"], r["target"], r["date"] = int(p[1]), int(p[2]), int(p[3] or 0)
        r["start"], r["end"] = int(p[9]), int(p[10])
    except ValueError:
        return None
    r["table"] = "treatments"
    return r


def hist_row(p):
    if len(p) < 13:
        return None
    r = dict(zip(HIST_COLS, p[:13]))
    try:
        r["target"], r["by"], r["date"] = int(p[1]), int(p[2]), int(p[3] or 0)
        r["start"], r["end"] = int(p[7]), int(p[8])
    except ValueError:
        return None
    r["table"] = "history"
    return r


SIDE = {  # side table -> file names (delta form first, stage form second)
    "treatments": ("treatments_delta.tsv", "treatments.tsv"),
    "history": ("history_delta.tsv", "history.tsv"),
    "witness": ("treatment_witness_delta.tsv", "treatment_witness.tsv"),
    "class": ("treatment_class_delta.tsv", "treatment_class.tsv"),
    "joined": ("joined_delta.tsv", "joined.tsv"),
    "anchor": ("history_anchor_delta.tsv", "history_anchor.tsv"),
    "hclaim": ("history_claim_delta.tsv", "history_claim.tsv"),
}


def _side(folder, name):
    for fn in SIDE[name]:
        p = os.path.join(folder, fn)
        if os.path.exists(p):
            return p
    return None


def load_cert(path, want_ids=None):
    """Rows of one certified input: a delta folder (certify7 / certify_recog / certify_opwords / certify6 layout, or
    a stage folder) or one rows file (a treatments or history table in SCHEMA layout; the side tables of its folder
    are used when present). -> (rows, info). Each row dict carries `table` and the side-table facts:
    witness (W, by_evidence) | None, claim (claim, field_limit, doctrine) | None, joined [(rel, s, e, quote, part,
    label)], anchor (s, e, quote, part) | None, hclaim (claim) | None."""
    path = os.path.normpath(path)
    files = {}
    if os.path.isdir(path):
        folder = path
        for name in SIDE:
            files[name] = _side(folder, name)
        if not files["treatments"] and not files["history"]:
            sys.exit("no treatments / history table in " + path)
    else:
        folder = os.path.dirname(path)
        for name in SIDE:
            files[name] = _side(folder, name)
        base = os.path.basename(path).lower()
        if "history" in base:
            files["history"], files["treatments"] = path, None
        elif "treat" in base:
            files["treatments"], files["history"] = path, None
        else:  # decide by the column count of the first line
            first = read_tsv(path)[:1]
            if first and len(first[0]) == 13:
                files["history"], files["treatments"] = path, None
            else:
                files["treatments"], files["history"] = path, None
    rows, bad = [], 0
    for name, maker in (("treatments", treat_row), ("history", hist_row)):
        if not files[name]:
            continue
        for p in read_tsv(files[name]):
            if want_ids is not None and p[0] not in want_ids:
                continue
            r = maker(p)
            if r is None:
                bad += 1
            else:
                rows.append(r)
    ids = {r["id"] for r in rows}
    wit, cls, joi, anc, hcl = {}, {}, {}, {}, {}
    for p in read_tsv(files["witness"]) if files["witness"] else []:
        if p[0] in ids and len(p) >= 3 and p[0] not in wit:
            wit[p[0]] = (_int(p[1], -1), p[2])
    for p in read_tsv(files["class"]) if files["class"] else []:
        if p[0] in ids and len(p) >= 5 and p[0] not in cls:
            cls[p[0]] = (p[1], p[2], p[3])
    for p in read_tsv(files["joined"]) if files["joined"] else []:
        if p[0] in ids and len(p) >= 9 and p[1] == "treatments":
            try:
                joi.setdefault(p[0], []).append((p[2], int(p[3]), int(p[4]), p[5], p[6], p[7]))
            except ValueError:
                pass
    for p in read_tsv(files["anchor"]) if files["anchor"] else []:
        if p[0] in ids and len(p) >= 5 and p[0] not in anc:
            try:
                anc[p[0]] = (int(p[1]), int(p[2]), p[3], p[4])
            except ValueError:
                pass
    for p in read_tsv(files["hclaim"]) if files["hclaim"] else []:
        if p[0] in ids and len(p) >= 2 and p[0] not in hcl:
            hcl[p[0]] = p[1]
    for r in rows:
        r["witness"] = wit.get(r["id"])
        r["claim"] = cls.get(r["id"])
        r["joined"] = joi.get(r["id"], [])[:2]
        r["anchor"] = anc.get(r["id"])
        r["hclaim"] = hcl.get(r["id"])
    info = {k: (v.replace("\\", "/") if v else None) for k, v in files.items()}
    info["sha1"] = {k: sha1_file(v) for k, v in files.items() if v}
    info["bad_rows"] = bad
    return rows, info


def a_effect(kind, scope, claim, witness, quote, whole_phr):
    """Effect class of a treatments row (A_COMPAT key) and whether it is demoted."""
    cl = claim[0] if claim else "-"
    if cl == "doctrine":
        return "doctrine", 1
    if kind in T_LIMIT:
        return "limit", 0
    demoted = 0
    if cl == "operativeWords" and not witness:
        demoted = int(whole_phr is None or not any(ph in quote.lower() for ph in whole_phr))
    whole = scope == "all" and not demoted
    if witness:
        return ("report_whole" if whole else "report_part"), demoted
    return ("own_whole" if whole else "own_part"), demoted


# ---- texts and passages --------------------------------------------------------------------------------------------
def clean(x):
    return x.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def body_start(text):
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            return nl + 1 if nl >= 0 else len(text)
    return 0


def front_field(text, name):
    m = re.search(r'^%s:\s*"?(.*?)"?\s*$' % re.escape(name), text[:body_start(text) or 4000], re.M)
    return m.group(1).strip() if m else ""


def find_quote(text, quote, near):
    """(s, e) of the occurrence of the (normalised) quote in the text nearest to `near`, or None."""
    ct = clean(text)
    q = clean(quote).strip()
    if not q:
        return None
    best = None
    i = ct.find(q)
    while i >= 0:
        if best is None or abs(i - near) < abs(best[0] - near):
            best = (i, i + len(q))
        i = ct.find(q, i + 1)
    if best:
        return best
    rx = re.compile(r"\s+".join(re.escape(t) for t in q.split()))
    for m in rx.finditer(ct):
        if best is None or abs(m.start() - near) < abs(best[0] - near):
            best = (m.start(), m.end())
    return best


def locate(text, s, e, quote):
    """The span of a certificate quote in the text at HEAD: as given when it matches, else relocated, else None."""
    if 0 <= s < e <= len(text) and (not quote or clean(text[s:e]) == clean(quote)):
        return (s, e), False
    hit = find_quote(text, quote, s) if quote else None
    return (hit, True) if hit else (None, False)


def _word_left(text, i, lo):
    for _ in range(60):
        if i <= lo or text[i - 1] in " \n":
            break
        i -= 1
    return max(i, lo)


def _word_right(text, i):
    for _ in range(60):
        if i >= len(text) or text[i] in " \n":
            break
        i += 1
    return min(i, len(text))


def passage_bounds(text, spans, rnd, body0, pad_min=500, pad_max=1600, para=1, merge_gap=300):
    """Windows [(a, b)] around the spans: the paragraph of each span and `para` paragraphs on each side, at least
    pad_min (+0-200 random) and at most pad_max (+0-300 random) characters on each side of the span; overlapping or
    close windows are merged. Paragraph = line (blank-line block for hard-wrapped texts)."""
    rc = reader_common()
    sep = NL + NL if rc.hard_wrapped(text, body0) else NL
    wins = []
    for s, e in sorted(spans):
        s, e = max(s, body0), max(e, body0)
        a = text.rfind(sep, body0, s)
        a = body0 if a < 0 else a + len(sep)
        for _ in range(para):
            if a > body0:
                a2 = text.rfind(sep, body0, max(body0, a - len(sep)))
                a = body0 if a2 < 0 else a2 + len(sep)
        b = text.find(sep, e)
        b = len(text) if b < 0 else b
        for _ in range(para):
            if b < len(text):
                b2 = text.find(sep, b + len(sep))
                b = len(text) if b2 < 0 else b2
        lo_cap, hi_cap = s - pad_max - rnd.randint(0, 300), e + pad_max + rnd.randint(0, 300)
        lo_min, hi_min = s - pad_min - rnd.randint(0, 200), e + pad_min + rnd.randint(0, 200)
        if a < lo_cap:
            a = _word_left(text, lo_cap, body0)
        if a > lo_min:
            a = _word_left(text, max(body0, lo_min), body0)
        if b > hi_cap:
            b = _word_right(text, hi_cap)
        if b < hi_min:
            b = _word_right(text, min(len(text), hi_min))
        wins.append([max(body0, a), min(len(text), b)])
    wins.sort()
    out = []
    for a, b in wins:
        if out and a <= out[-1][1] + merge_gap:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [tuple(w) for w in out]


PART_WORDS = {
    "majority": "opinion of the court",
    "perCuriam": "opinion of the court (per curiam)",
    "plurality": "lead / plurality opinion",
    "concurrence": "a concurring opinion",
    "dissent": "a dissenting opinion",
    "headmatter": "head matter / syllabus (not part of any opinion)",
    "title": "title / caption",
}


def part_labels(text, a, b):
    """Machine labels of the opinion parts the window [a, b) overlaps, in order (repeats collapsed)."""
    rc = reader_common()
    pm, _b0 = rc.part_map2(text)
    out = []
    for x, y, p, _s in pm:
        if y <= a or x >= b:
            continue
        w = PART_WORDS.get(p.rstrip("~?"), "")
        if not w:
            continue
        if p.endswith("~"):
            w += " [inferred]"
        if not out or out[-1] != w:
            out.append(w)
    return out


# ---- what an auditor is told about a decision ----------------------------------------------------------------------
_NOT_REPORTER = re.compile(r"LEXIS|SCDB|\bWL\b|^\s*No\.|^\s*\d{4}\s+[A-Z]{2,}\s+\d+\s*$")


def show_cites(cites, most=3):
    good = [c.strip() for c in cites if c.strip() and not _NOT_REPORTER.search(c)]
    if not good:
        good = [c.strip() for c in cites if c.strip()][:1]
    seen, out = set(), []
    for c in good:
        k = re.sub(r"[\s.]", "", c).lower()
        if k not in seen:
            seen.add(k)
            out.append(c)
    return out[:most]


def node_facts(n, F, L, text=None):
    """{name, court, date, citations, docket} of a node (graph/nodes.tsv, node facts, the text's front matter)."""
    r = L.node_row(n) + [""] * 8
    head = text[:6000] if text else ""
    name = re.sub(r"\s+", " ", r[6]).strip()
    if not name and head:
        m = re.search(r"^# (.+)$", head, re.M)
        name = m.group(1).strip() if m else ""
    cites = [c.strip() for c in r[5].split("|") if c.strip()]
    if not cites and head:
        m = re.search(r"^citations:\s*\[(.*)\]\s*$", head, re.M)
        if m:
            cites = [c.strip().strip('"') for c in m.group(1).split('",') if c.strip().strip('"')]
    court = F.court_name(int(F.court[n])) if 0 <= n < len(F.court) else "?"
    if court == "?" and head:
        court = front_field(head, "court") or "[court unknown]"
    d = int(F.date[n]) if 0 <= n < len(F.date) else 0
    d = d or _int(r[4])
    return {"name": name or "[no name on file]", "court": court, "date": iso_date(d),
            "citations": show_cites(cites), "all_citations": cites,
            "docket": front_field(head, "docket") if head else ""}


def label(fx, docket=False):
    s = fx["name"]
    if len(s) > 200:
        s = s[:197].rstrip() + "..."
    parts = [s]
    if fx["citations"]:
        parts.append("; ".join(fx["citations"]))
    parts.append(fx["court"])
    if docket and fx.get("docket"):
        parts.append("docket " + fx["docket"])
    parts.append("decided " + fx["date"])
    return ", ".join(parts)


# ---- matching an auditor's "other decision" to a node --------------------------------------------------------------
def cite_keys(s):
    rc = reader_common()
    out = set()
    for m in rc.CITE_RX.finditer(s or ""):
        k = rc.cite_key(m)
        if k:
            out.add(k)
    return out


def name_keys(name):
    rc = reader_common()
    return {t.lower() for t in rc.name_tokens(name)} | {t.lower() for t in rc.short_name_tokens(name)}


def by_match(answer_text, y_cites, y_name):
    """Does the auditor's text name decision Y? -> ('yes'|'no', how). A citation of Y decides; a citation that is
    not Y's with no name overlap is `no`; otherwise a case-name token of Y (>= 3 letters, not a stop word) is `yes`."""
    a = answer_text or ""
    ak = cite_keys(a)
    yk = set()
    for c in y_cites:
        yk |= cite_keys(c)
    if ak & yk:
        return "yes", "citation"
    toks = {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z'\-]+", a)}
    nk = name_keys(y_name) & toks
    if nk:
        return "yes", "name:" + ",".join(sorted(nk))
    return "no", ("citation differs" if ak else "no name / citation of Y")


# ---- item ids ------------------------------------------------------------------------------------------------------
ID_ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"


def taken_item_ids():
    import glob
    out = set()
    for p in glob.glob(os.path.join(HERE, "**", "sample.tsv"), recursive=True):
        out |= {r[0] for r in read_tsv(p)[1:]}
    return out


def new_ids(n, rnd, taken):
    out = []
    while len(out) < n:
        i = "q" + "".join(rnd.choice(ID_ALPHABET) for _ in range(6))
        if i not in taken:
            taken.add(i)
            out.append(i)
    return out


def seeded(*parts):
    return random.Random("|".join(str(p) for p in parts))
