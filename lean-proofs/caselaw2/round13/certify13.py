"""Round 13 (= round10/certify10.py with base round12/stage/v12a and ids t13: / h13:; round 10 = round9/certify9.py,
round 9 = round8/certify8.py, itself round7/certify7.py): turn linker / reader rows (DESIGN7 section 4) into certified table deltas.

    python -X utf8 round13/certify13.py --rows FILE [--rows ...] --out DIR [--procs N] [--base DIR]
                                        [--no-base-skip] [--keep-base-conflicts]

One JSON object per line:
  {"rule", "table": "treatments"|"history", "by", "target", "kind", "scope", "main": [s, e], "part",
   "ev": "cite:<key>"|"name:<tokens>",
   "joined": [{"rel": "antecedent"|"doctrineTie", "span": [s, e], "part", "label"}],      (treatments only)
   "claim": "-"|"doctrine"|"operativeWords"|"orderHead"|"setAside", "doctrine", "field_limit",
   "anchor": [a0, a1]|null, "anchor_part", "text": "by"|"target",                        (history, as round 6)
   "reader", "confidence", "note"}                                                        (optional)
History rows may also use round 6's "disp" for "main". Offsets: characters of the git-HEAD text (UTF-8, CRLF -> LF).

Every row is checked the way the Lean checker checks it (DESIGN7 sections 2-3, LEAN6 section 1.1; same order, same
reason names, same string functions: ASCII-only lower-casing, `compact` = ASCII letters and digits, whole-word name
tokens of 3+ characters). The carrying text is read from git HEAD and must hash to the node's `text_sha` in the base
decisions2.tsv. Each quote gets one window [start-400, end+400) clipped (so Lean, which reads every usable window
that covers a quote, can only accept more: certify7 is never the looser).

treatments row (text = the acting decision's):
  doctrineBadRow      claim doctrine and (kind not disapproved, or no doctrineTie joined line)
  quoteMismatch       the main span is empty or outside the text
  -- with joined lines (checkJoined, 1-2 lines; a third is a badRow here):
  joinedMismatch      a joined span is empty or outside the text
  joinedPart          a joined part is not majority | plurality | perCuriam
  joinedDisqualified  a joined quote has a disqualifier of the row's mode, or of `disqualify_joined`
  joinedRelation      antecedent: j_end <= start, start - j_end <= joined_gap_max, an `anaphor` phrase and a plain cue
                      of the kind in the main quote; doctrineTie: only on a doctrine row, label >= 2 words and >= 8
                      characters, the label in the main and the joined quote, a `doctrine_tie` phrase in the joined one
  joinedUnresolved    the evidence does not resolve inside one joined quote alone (cite: also through the index)
  -- then the main quote (target evidence taken as given when joined):
  operativeBadRow     claim operativeWords on a row that is not kind disapproved
  noCue / disqualified / targetUnresolved / partNotMajority / targetLater   in the row's mode:
                      plain (cue list `treat[kind]`, disqualifiers `disqualify_treat` for status-changing kinds,
                      evidence in the window), operative (`operative`, + `disqualify_operative`, evidence in the
                      quote), doctrine (`doctrine_reject`, + `disqualify_operative`)
  after the text checks: doctrineAmbiguous (a row with a compact doctrineTie label that two passing doctrine rows
  tie to different targets; the base's doctrineTie lines count too; LEAN7 L7-3/L7-4), duplicate (first passing
  (by, target, kind) stands). LEAN7 L7-5: a joined quote is tested against the kind's plain disqualifiers
  (`disqualify_treat` for a status-changing kind) + `disqualify_joined`.
  Base skip: a row whose (by, target, kind) is in the base treatments.tsv is not certified (counted).
history row: as round6/history/certify6.py (anchored and plain), plus the claims of DESIGN7 section 3:
  setAside            on kind vacated: the cue list is `hist.vacated` + `set_aside`; on any other kind no effect
                      (LEAN7 L7-11; the claim line is then not written, `claim_setAside_other_kind` in stats.json)
  orderHead           the part step admits part headmatter only when the acting court is the Supreme Court
                      (courts2), date(by) >= order_head_from, the kind is certDenied | vacated | reversed | affirmed |
                      reviewDismissed, the quote has an `order_line` phrase of the kind and is <= 400 characters;
                      otherwise `orderHeadNotAllowed` (a headmatter part without the claim stays partNotMajority)
  then duplicate, conflict, conflictBase as certify6. A claimed row whose (by, target, kind) IS in the base is
  checked on the BASE row's own certificate (and anchor) with the claim; when it passes, only a history_claim line
  for the base id is written (`claim_on_base` in stats.json).
Authority is NOT checked (Lean decides it).

Output folder:
  treatments_delta.tsv        16 columns (id t13:<by>:<target>:<start>, explicit 1, temporal unknown)
  treatment_class_delta.tsv   id, claim (operativeWords|doctrine), field_limit|-, doctrine|-, src
  joined_delta.tsv            id, treatments, rel, j_start, j_end, j_quote, j_part, label|-, src
  history_delta.tsv           13 columns (id h13:<by>:<target>:<kind>), history_anchor_delta.tsv, history_claim_delta.tsv
  cert_text_delta.tsv, window_sha_delta.tsv, cite_index_delta.tsv, cite_collisions.tsv, base_conflicts.tsv,
  rejects.tsv (row, reason, rule, by, target, kind, detail), stats.json (with cue_source)
No answer-key file is read. Nothing is written outside --out.
"""
import argparse
import collections
import hashlib
import json
import os
import subprocess
import sys
import threading
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
R6 = os.path.join(C2, "round6", "history")
sys.path.insert(0, R6)
import certify6 as C6  # noqa: E402  (string functions, decisions, citation index; round 6, not edited)

L = C6.L
sys.path.insert(0, HERE)
import nodes13  # noqa: E402  (round 11, DESIGN13 section 4: order nodes; active with --nodes DIR or R13_NODES)
nodes13.patch(L)
r6cite = C6.r6cite
BASE = os.path.join(C2, "round12", "stage", "v12a")
CUE_JSON = C6.CUE_JSON
NOWIN = C6.NOWIN
NL, TAB, CR = "\n", "\t", "\r"
norm, lower, compact, words, ev_in = C6.norm, C6.lower, C6.compact, C6.words, C6.ev_in
PARTS = C6.PARTS
ANCHOR_PARTS = C6.ANCHOR_PARTS
NEG, POS = C6.NEG, C6.POS
PAD = 400
CHANGES = frozenset(("overruled", "disapproved", "recededFrom", "abrogated"))  # Events.lean TKind.changesStatus
ORDER_KINDS = ("certDenied", "vacated", "reversed", "affirmed", "reviewDismissed")
T_SCOPES = ("all", "partialUnknown", "otherGrounds", "unknown")
T_CLAIMS = ("-", "doctrine", "operativeWords")
H_CLAIMS = ("-", "orderHead", "setAside")

# DESIGN7's example lists, used until the `lean` agent has put the keys in cue_table.json (stats.json: cue_source)
DESIGN7 = {
    "anaphor": ["those cases", "these cases", "that case", "those decisions", "these decisions", "that decision",
                "such cases", "those opinions", "those holdings", "both cases", "each of them", "they are overruled",
                "it is overruled"],
    "doctrine_tie": ["doctrine of", "doctrine announced", "doctrine established", "rule of", "rule announced",
                     "rule laid down", "announced in", "established in", "adopted in", "laid down in", "the rule in",
                     "first announced", "originated in"],
    "doctrine_reject": ["has no place", "is rejected", "we reject", "repudiate", "abandon", "is overruled",
                        "no longer", "discard", "disapprove"],
    "disqualify_joined": [],
    "order_line": {"certDenied": ["certiorari denied", "petition for writ of certiorari denied"],
                   "vacated": ["certiorari granted, judgment vacated", "judgment vacated, and case remanded"],
                   "reversed": ["judgment reversed"],
                   "affirmed": ["judgment affirmed"],
                   "reviewDismissed": ["appeal dismissed", "certiorari dismissed", "writ of certiorari dismissed"]},
    "set_aside": ["set aside", "sets aside", "is set aside", "are set aside", "be set aside"],
}
DESIGN7_NUM = {"order_head_from": 20130101, "joined_gap_max": 300, "order_head_max_len": 400}


def load_cues():
    cues, src = C6.load_cues()  # hist, disqualify_hist, anchor, disqualify_anchor
    with open(CUE_JSON, encoding="utf-8") as f:
        t = json.load(f)
    cues["treat"] = {k: [c for c in v if c] for k, v in t["treat"].items()}
    for k in ("disqualify_treat", "operative", "disqualify_operative"):
        cues[k] = [c for c in t[k] if c]
        src[k] = "cue_table.json"
    src["treat"] = "cue_table.json"
    for k, fb in DESIGN7.items():
        v = t.get(k)
        ok = isinstance(v, dict) if isinstance(fb, dict) else isinstance(v, list)
        if ok and (v or k == "disqualify_joined"):
            cues[k] = {kk: [c for c in vv if c] for kk, vv in v.items()} if isinstance(v, dict) else [c for c in v if c]
            src[k] = "cue_table.json"
        else:
            cues[k] = fb
            src[k] = "DESIGN7 example list (key not in cue_table.json yet)"
    for k, fb in DESIGN7_NUM.items():
        v = t.get(k)
        if isinstance(v, int) and not isinstance(v, bool):
            cues[k] = v
            src[k] = "cue_table.json"
        else:
            cues[k] = fb
            src[k] = "DESIGN7 default (key not in cue_table.json yet)"
    return cues, src


def any_in(lst, s):
    return next((c for c in lst if c and c in s), None)


def order_line_hit(lst, s):
    """D7-9 / Lean `Cert.orderLineHit`: an entry "a ... b" means a occurs and b occurs in the text after the first a
    (split s on a, join the pieces after the first, test b); any other entry is a plain substring."""
    for c in lst:
        if not c:
            continue
        parts = c.split(" ... ")
        if len(parts) == 2:
            pieces = s.split(parts[0]) if parts[0] else [s]
            if parts[0] and parts[1] and len(pieces) > 1 and parts[1] in "".join(pieces[1:]):
                return c
        elif c in s:
            return c
    return None


def canon_label(s):
    """A doctrine label as written to the tables: normalised, ASCII lower-cased, single spaces, trimmed."""
    return " ".join(lower(norm(str(s))).split(" ")).strip() if s else ""


def label_ok(lab):
    """>= 2 words and >= 8 characters; written with single spaces only (so every reading of "word" agrees)."""
    return len(lab.split(" ")) >= 2 and len(lab) >= 8 and "  " not in lab and lab == lab.strip()


# ------------------------------------------------------------------------------------------------ the checks
def main_check(r, text, cues, mode, self_text):
    """Lean `check` on the main quote of a treatments row (mode plain / operative / doctrine)."""
    n = len(text)
    q0, q1 = r["main"]
    if not (0 <= q0 < q1 <= n):
        return "quoteMismatch", "span [%d, %d) outside the text (%d characters)" % (q0, q1, n), None
    quote = norm(text[q0:q1])
    ql = lower(quote)
    if mode == "plain":
        cl = cues["treat"].get(r["kind"], [])
    elif mode == "operative":
        cl = cues["operative"]
    else:
        cl = cues["doctrine_reject"]
    if not any(c in ql for c in cl):
        return "noCue", "", None
    dq = list(cues["disqualify_treat"]) if r["kind"] in CHANGES else []
    if mode != "plain":
        dq += cues["disqualify_operative"]
    hit = any_in(dq, ql)
    if hit is not None:
        return "disqualified", hit, None
    s0, e0 = max(0, q0 - PAD), min(n, q1 + PAD)
    win = norm(text[s0:e0])
    if not self_text:
        ctx = win if mode == "plain" else quote
        if not ev_in(r["ev"], ctx):
            return "targetUnresolved", "evidence not in the %s" % ("window" if mode == "plain" else "quote"), None
        if r["cite_fail"]:
            return "targetUnresolved", r["cite_fail"], None
    if r["part"] not in PARTS:
        return "partNotMajority", str(r["part"]), None
    if not r["ordered"]:
        return "targetLater", "", None
    return None, "", {"quote": quote, "win": (s0, e0, win)}


def check_treat(r, text, cues):
    """(reason or None, detail, payload): the round-7 treatments step (DESIGN7 section 2)."""
    n = len(text)
    claim = r["claim"]
    mode = "operative" if claim == "operativeWords" else ("doctrine" if claim == "doctrine" else "plain")
    q0, q1 = r["main"]
    if claim == "doctrine":
        if r["kind"] != "disapproved" or not any(j["rel"] == "doctrineTie" for j in r["joined"]):
            return "doctrineBadRow", "kind %s, joined %s" % (r["kind"], ",".join(j["rel"] for j in r["joined"])), None
    elif not r["joined"]:
        # Lean `checkTreatmentWith`: (.plain, []) -> check, (.operative, []) -> checkOperative (operativeBadRow first)
        if claim == "operativeWords" and r["kind"] != "disapproved":
            return "operativeBadRow", r["kind"], None
        return main_check(r, text, cues, mode, False)
    jpay = []
    if r["joined"]:
        for j in r["joined"]:
            a, b = j["span"]
            if not (0 <= a < b <= n):
                return "joinedMismatch", "span [%d, %d) outside the text (%d characters)" % (a, b, n), None
        if not (0 <= q0 < q1 <= n):
            # the main quote's own span is checked by the main check (step 6); the relation test needs its text
            return "quoteMismatch", "span [%d, %d) outside the text (%d characters)" % (q0, q1, n), None
        mq = lower(norm(text[q0:q1]))
        for j in r["joined"]:
            if j["part"] not in PARTS:
                return "joinedPart", str(j["part"]), None
        # LEAN7 L7-5: the plain list of the row's kind (not the main quote's mode additions) + disqualify_joined
        dq = list(cues["disqualify_treat"]) if r["kind"] in CHANGES else []
        dq += cues["disqualify_joined"]
        for j in r["joined"]:
            hit = any_in(dq, lower(norm(text[j["span"][0]:j["span"][1]])))
            if hit is not None:
                return "joinedDisqualified", hit, None
        for j in r["joined"]:
            a, b = j["span"]
            jq = lower(norm(text[a:b]))
            if j["rel"] == "antecedent":
                if not (b <= q0 and q0 - b <= cues["joined_gap_max"]):
                    return "joinedRelation", "antecedent gap (j_end %d, start %d)" % (b, q0), None
                if any_in(cues["anaphor"], mq) is None:
                    return "joinedRelation", "no anaphor in the main quote", None
                if any_in(cues["treat"].get(r["kind"], []), mq) is None:
                    return "joinedRelation", "no cue of the kind in the main quote", None
            else:  # doctrineTie
                lab = j["label"]
                if claim != "doctrine":
                    return "joinedRelation", "doctrineTie on a row without a doctrine claim", None
                if not label_ok(lab):
                    return "joinedRelation", "label too short: %s" % lab, None
                if lab not in mq or lab not in jq:
                    return "joinedRelation", "label not in both quotes", None
                if any_in(cues["doctrine_tie"], jq) is None:
                    return "joinedRelation", "no tie phrase in the joined quote", None
        hit = None
        for j in r["joined"]:
            if ev_in(r["ev"], norm(text[j["span"][0]:j["span"][1]])):
                hit = j
                break
        if hit is None:
            return "joinedUnresolved", "evidence in no joined quote", None
        if r["cite_fail"]:
            return "joinedUnresolved", r["cite_fail"], None
        for j in r["joined"]:
            a, b = j["span"]
            s0, e0 = max(0, a - PAD), min(n, b + PAD)
            jpay.append({"quote": norm(text[a:b]), "win": (s0, e0, norm(text[s0:e0]))})
    if claim == "operativeWords" and r["kind"] != "disapproved":
        return "operativeBadRow", r["kind"], None
    reason, detail, pay = main_check(r, text, cues, mode, True)
    if reason:
        return reason, detail, None
    pay["joined"] = jpay
    return None, "", pay


def check_hist(r, text, cues):
    """certify6.check_row with the round-7 claims (setAside cue list, orderHead part rule)."""
    n = len(text)
    anchored = r["anchor"] is not None
    pay = {}
    if anchored:
        a0, a1 = r["anchor"]
        if not (0 <= a0 < a1 <= n):
            return "anchorMismatch", "span [%d, %d) outside the text (%d characters)" % (a0, a1, n), None
        aq = norm(text[a0:a1])
        al = lower(aq)
        if not any(c in al for c in cues["anchor"]):
            return "anchorNoCue", "", None
        hit = any_in(cues["disqualify_anchor"], al)
        if hit is not None:
            return "anchorDisqualified", hit, None
        if not ev_in(r["ev"], aq):
            return "anchorUnresolved", "evidence not in the anchor quote", None
        if r["cite_fail"]:
            return "anchorUnresolved", r["cite_fail"], None
        if r["anchor_part"] not in ANCHOR_PARTS:
            return "anchorPart", str(r["anchor_part"]), None
        s0, e0 = max(0, a0 - PAD), min(n, a1 + PAD)
        pay["a_quote"] = aq
        pay["a_win"] = (s0, e0, norm(text[s0:e0]))
    q0, q1 = r["main"]
    if not (0 <= q0 < q1 <= n):
        return "quoteMismatch", "span [%d, %d) outside the text (%d characters)" % (q0, q1, n), None
    quote = norm(text[q0:q1])
    ql = lower(quote)
    cl = list(cues["hist"].get(r["kind"], ()))
    if r["claim"] == "setAside" and r["kind"] == "vacated":
        cl += cues["set_aside"]
    if not any(c in ql for c in cl):
        return "noCue", "", None
    hit = any_in(cues["disqualify_hist"], ql)
    if hit is not None:
        return "disqualified", hit, None
    s0, e0 = max(0, q0 - PAD), min(n, q1 + PAD)
    win = norm(text[s0:e0])
    if not anchored and not r["self_text"]:
        if not ev_in(r["ev"], win):
            return "targetUnresolved", "evidence not within %d characters of the quote" % PAD, None
        if r["cite_fail"]:
            return "targetUnresolved", r["cite_fail"], None
    if r["part"] not in PARTS:
        if r["claim"] == "orderHead" and r["part"] == "headmatter":
            why = []
            if not r["by_scotus"]:
                why.append("court")
            if r["by_date"] < cues["order_head_from"]:
                why.append("date")
            if r["kind"] not in ORDER_KINDS:
                why.append("kind")
            if order_line_hit(cues["order_line"].get(r["kind"], []) if r["kind"] in ORDER_KINDS else [], ql) is None:
                why.append("orderLine")
            if len(quote) > cues["order_head_max_len"]:
                why.append("length")
            if why:
                return "orderHeadNotAllowed", ",".join(why), None
        else:
            return "partNotMajority", str(r["part"]), None
    if not r["ordered"]:
        return "targetLater", "", None
    pay["quote"] = quote
    pay["win"] = (s0, e0, win)
    return None, "", pay


_CUES = [None]


def _init(cues):
    _CUES[0] = cues


def worker(job):
    """job = (repo, [(path, expected sha, [row, ...])]) -> [(row index, reason, detail, payload)]"""
    repo, items = job
    cues = _CUES[0]
    out = []
    if repo == nodes13.REPO:  # round 11: order nodes are read from their text files, same checks
        for path, sha, rows in items:
            raw = nodes13.raw(nodes13.node_of(path))
            if raw is None:
                out.extend((r["i"], "textMissing", repo + ":" + path, None) for r in rows)
                continue
            got = hashlib.sha1(raw).hexdigest()
            if got != sha:
                out.extend((r["i"], "shaMismatch", "file %s, decisions2 %s" % (got, sha), None) for r in rows)
                continue
            text = raw.decode("utf-8", "replace").replace(CR + NL, NL)
            for r in rows:
                fn = check_treat if r["table"] == "treatments" else check_hist
                reason, detail, pay = fn(r, text, cues)
                out.append((r["i"], reason, detail, pay))
        return out
    p = subprocess.Popen(["git", "-C", os.path.join(C6.REPOS, repo), "cat-file", "--batch"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, creationflags=NOWIN)

    def feed():
        for path, _, _ in items:
            p.stdin.write(("HEAD:" + path + NL).encode("utf-8"))
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    for path, sha, rows in items:
        hdr = p.stdout.readline().split()
        if len(hdr) < 3 or hdr[1] != b"blob":
            for r in rows:
                out.append((r["i"], "textMissing", repo + ":" + path, None))
            continue
        raw = p.stdout.read(int(hdr[2]))
        p.stdout.read(1)
        got = hashlib.sha1(raw).hexdigest()
        if got != sha:
            for r in rows:
                out.append((r["i"], "shaMismatch", "git %s, decisions2 %s" % (got, sha), None))
            continue
        text = raw.decode("utf-8", "replace").replace(CR + NL, NL)
        for r in rows:
            fn = check_treat if r["table"] == "treatments" else check_hist
            reason, detail, pay = fn(r, text, cues)
            out.append((r["i"], reason, detail, pay))
    p.wait()
    return out


# ------------------------------------------------------------------------------------------------ parsing
def span(v):
    if not isinstance(v, (list, tuple)) or len(v) != 2:
        raise ValueError("span")
    return int(v[0]), int(v[1])


def clean_field(v, n=200):
    s = norm(str(v if v is not None else "")).strip()
    return s[:n] if s else "-"


def parse_row(o, tkinds, hkinds):
    if not isinstance(o, dict):
        raise ValueError("not an object")
    r = {}
    r["rule"] = o.get("rule")
    if not isinstance(r["rule"], str) or not r["rule"] or any(c in r["rule"] for c in (TAB, NL, CR)):
        raise ValueError("rule")
    r["table"] = o.get("table") or ("history" if "disp" in o else None)
    if r["table"] not in ("treatments", "history"):
        raise ValueError("table")
    try:
        r["by"], r["target"] = int(o["by"]), int(o["target"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("by/target")
    r["kind"] = o.get("kind")
    if r["kind"] not in (tkinds if r["table"] == "treatments" else hkinds):
        raise ValueError("kind")
    claim = o.get("claim") or "-"
    if claim not in (T_CLAIMS if r["table"] == "treatments" else H_CLAIMS):
        raise ValueError("claim %s on a %s row" % (claim, r["table"]))
    r["claim"] = claim
    try:
        r["main"] = span(o.get("main") if o.get("main") is not None else o.get("disp"))
    except (TypeError, ValueError):
        raise ValueError("main")
    r["part"] = o.get("part") or ""
    ev = o.get("ev") or ""
    if not isinstance(ev, str) or any(c in ev for c in (TAB, NL, CR)):
        raise ValueError("ev")
    r["note"] = o.get("note")
    if r["table"] == "treatments":
        r["scope"] = o.get("scope", "all")
        if r["scope"] not in T_SCOPES:
            raise ValueError("scope")
        if not (ev.startswith("cite:") or ev.startswith("name:")):
            raise ValueError("ev")
        if o.get("anchor") is not None or (o.get("text") or "by") != "by":
            raise ValueError("anchor/text on a treatments row")
        js = o.get("joined") or []
        if not isinstance(js, list) or len(js) > 2:
            raise ValueError("joined: at most two lines")
        r["joined"] = []
        for j in js:
            if not isinstance(j, dict) or j.get("rel") not in ("antecedent", "doctrineTie"):
                raise ValueError("joined rel")
            try:
                sp = span(j.get("span"))
            except (TypeError, ValueError):
                raise ValueError("joined span")
            lab = canon_label(j.get("label")) if j.get("rel") == "doctrineTie" else "-"
            r["joined"].append({"rel": j["rel"], "span": sp, "part": j.get("part") or "", "label": lab or "-"})
        r["doctrine"] = clean_field(o.get("doctrine"), 120)
        r["field_limit"] = clean_field(o.get("field_limit"), 200)
        if claim == "doctrine":
            ties = [j["label"] for j in r["joined"] if j["rel"] == "doctrineTie"]
            if r["doctrine"] == "-" and ties:
                r["doctrine"] = ties[0]
            if ties and canon_label(r["doctrine"]) != ties[0]:
                raise ValueError("doctrine differs from the doctrineTie label")
            r["doctrine"] = canon_label(r["doctrine"]) or "-"
        r["reader"] = clean_field(o.get("reader") or ("r7:" + r["rule"]), 80)
        try:
            r["conf"] = "%.2f" % max(0.0, min(1.0, float(o.get("confidence", 1.0))))
        except (TypeError, ValueError):
            r["conf"] = "1.00"
        r["text"] = "by"
        r["anchor"] = None
        if r["by"] < 0 or r["target"] < 0:
            raise ValueError("by/target")
    else:
        if o.get("joined"):
            raise ValueError("joined on a history row (reserved this round)")
        r["scope"] = o.get("scope", "all")
        if r["scope"] not in ("all", "unknown"):
            raise ValueError("scope")
        try:
            r["anchor"] = None if o.get("anchor") is None else span(o.get("anchor"))
        except (TypeError, ValueError):
            raise ValueError("anchor")
        r["anchor_part"] = o.get("anchor_part") or ""
        r["text"] = o.get("text") or "by"
        if r["text"] not in ("by", "target"):
            raise ValueError("text")
        if not (ev.startswith("cite:") or ev.startswith("name:")):
            if r["text"] == "target" and r["anchor"] is None and ev == "":
                ev = "name:self"
            else:
                raise ValueError("ev")
        if r["target"] < 0 or r["by"] < -1 or (r["by"] == -1 and r["text"] != "target"):
            raise ValueError("by/target")
    r["ev"] = ev
    if r["by"] == r["target"]:
        raise ValueError("by = target")
    return r


def read_decisions(path, want):
    """{node: (court2, date, text_sha)}; line k of decisions2.tsv is node k."""
    out = {}
    for k in [x for x in want if nodes13.is_extra(x)]:  # round 11: order nodes (court 2906, date, sha1 of the text)
        out[k] = (nodes13.SCOTUS, nodes13.meta(k)["date"], nodes13.sha(k) or "-")
    want = {x for x in want if not nodes13.is_extra(x)}
    if not want:
        return out
    top = max(want)
    with open(path, "rb") as f:
        for k, line in enumerate(f):
            if k > top:
                break
            if k in want:
                p = line.rstrip(b"\n").decode("utf-8").split(TAB)
                if len(p) > 7 and p[0] == str(k):
                    out[k] = (int(p[1]), int(p[2]), p[7])
    missing = want - set(out)
    if missing:
        with open(path, "rb") as f:
            for line in f:
                i = line.find(b"\t")
                try:
                    k = int(line[:i])
                except ValueError:
                    continue
                if k in missing:
                    p = line.rstrip(b"\n").decode("utf-8").split(TAB)
                    if len(p) > 7:
                        out[k] = (int(p[1]), int(p[2]), p[7])
    return out


def scotus_id(base):
    ids = [int(p[0]) for p in C6.read_tsv(os.path.join(base, "courts2.tsv"))
           if len(p) > 3 and p[3] == "Supreme Court of the United States"]
    if len(ids) != 1:
        sys.exit("courts2.tsv: %d courts named 'Supreme Court of the United States'" % len(ids))
    return ids[0]


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--procs", type=int, default=min(12, os.cpu_count() or 4))
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--nodes", help="order-node folder (default: v11d's round12/data_orders; e.g. round13/data_orders; or env R13_NODES): rows "
                                    "may name its node ids (round13/nodes13.py); their text is the node's text file")
    ap.add_argument("--no-base-skip", action="store_true",
                    help="test flag: no base skip, no conflictBase, no base doctrine labels, base ids not reserved")
    ap.add_argument("--keep-base-conflicts", action="store_true")
    a = ap.parse_args()
    if a.nodes:  # round 11: also exported as R13_NODES so the worker processes load the same nodes
        nodes13.activate(a.nodes)
        nodes13.patch(L)
    os.makedirs(a.out, exist_ok=True)
    cues, cue_src = load_cues()
    tkinds, hkinds = set(cues["treat"]), set(cues["hist"])
    st = collections.Counter()
    by_rule = collections.defaultdict(collections.Counter)
    rejects = []
    rows = []

    def reject(r, reason, detail=""):
        rejects.append((r["i"], r["ref"], reason, r, detail))
        st["reject:%s:%s" % (r["table"], reason)] += 1
        by_rule[r["rule"]]["reject:" + reason] += 1

    i = 0
    for path in a.rows:
        with open(path, "rb") as f:
            for ln, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                i += 1
                ref = "%s:%d" % (path.replace(os.sep, "/"), ln)
                st["input_rows"] += 1
                try:
                    r = parse_row(json.loads(line.decode("utf-8")), tkinds, hkinds)
                except (ValueError, json.JSONDecodeError) as e:
                    st["reject:badRow"] += 1
                    rejects.append((i, ref, "badRow", None, str(e)[:100]))
                    continue
                r["i"], r["ref"] = i, ref
                st["input:" + r["table"]] += 1
                by_rule[r["rule"]]["input"] += 1
                rows.append(r)
    # ---- the base
    hb_keys, hb_pair, hb_rows, hb_anchor = {}, collections.defaultdict(list), {}, {}
    tb_keys, base_tids, base_doc = set(), set(), {}
    if not a.no_base_skip:
        for p in C6.read_tsv(os.path.join(a.base, "history.tsv")):
            if len(p) >= 13:
                k = (int(p[2]), int(p[1]), p[4])
                hb_keys[k] = p[0]
                hb_rows[k] = p
                hb_pair[(int(p[2]), int(p[1]))].append((p[4], p[5], p[0]))
        for p in C6.read_tsv(os.path.join(a.base, "history_anchor.tsv")):
            if len(p) >= 6:
                hb_anchor.setdefault(p[0], p)
        tgt_of = {}
        for p in C6.read_tsv(os.path.join(a.base, "treatments.tsv")):
            if len(p) >= 16:
                tb_keys.add((int(p[1]), int(p[2]), p[4]))
                base_tids.add(p[0])
                tgt_of[p[0]] = int(p[2])
        doc_ids = {p[0] for p in C6.read_tsv(os.path.join(a.base, "treatment_class.tsv"))
                   if len(p) >= 4 and p[1] == "doctrine" and p[0] in tgt_of}
        for p in C6.read_tsv(os.path.join(a.base, "joined.tsv")):
            if len(p) == 9 and p[1] == "treatments" and p[2] == "doctrineTie" and p[0] in doc_ids:
                base_doc.setdefault(compact(p[7]), set()).add(tgt_of[p[0]])
    live = []
    for r in rows:
        if r["table"] == "treatments":
            if (r["by"], r["target"], r["kind"]) in tb_keys:
                st["in_base_skipped:treatments"] += 1
                by_rule[r["rule"]]["in_base_skipped"] += 1
                continue
        else:
            k = (r["by"], r["target"], r["kind"])
            if k in hb_keys:
                if r["claim"] == "-":
                    st["in_base_skipped:history"] += 1
                    by_rule[r["rule"]]["in_base_skipped"] += 1
                    continue
                # a claim on a base row: check the BASE row's own certificate with the claim
                p = hb_rows[k]
                r["base_id"] = p[0]
                r["main"] = (int(p[7]), int(p[8]))
                r["ev"], r["part"] = p[10], p[11]
                r["base_sha"] = p[6]
                an = hb_anchor.get(p[0])
                r["anchor"] = (int(an[1]), int(an[2])) if an else None
                r["anchor_part"] = an[4] if an else ""
                st["claim_on_base_checked"] += 1
        live.append(r)
    want = {r["target"] for r in live} | {r["by"] for r in live if r["by"] >= 0}
    dec = read_decisions(os.path.join(a.base, "decisions2.tsv"), want)
    sc_id = scotus_id(a.base)
    # ---- citation index (as certify6: the graph index and the base index must give the target and nothing else)
    ckeys = {compact(r["ev"][5:]) for r in live if r["ev"].startswith("cite:")}
    ckeys.discard("")
    alias_of = {}
    for r in live:
        if r["ev"].startswith("cite:") and r["ev"][5:] not in alias_of:
            alias_of[r["ev"][5:]] = [(compact(k), f) for k, f in r6cite.keys_forms(r["ev"][5:])
                                     if f.startswith("alias:") and compact(k)]
    akeys = {c for v in alias_of.values() for c, _ in v}
    hits = C6.graph_hits(ckeys | akeys)
    base_idx = collections.defaultdict(set)
    base_lines = set()
    for p in C6.read_tsv(os.path.join(a.base, "cite_index.tsv")):
        if len(p) >= 2:
            base_lines.add((p[0], int(p[1])))
            c = compact(p[0])
            if c in ckeys or c in akeys:
                base_idx[c].add(int(p[1]))
    collisions = {}

    def alias_fail(r):
        for c, form in alias_of.get(r["ev"][5:], ()):
            g = {n for _, n in hits.get(c, ())}
            u = g | base_idx.get(c, set())
            if not u:
                continue
            if u == {r["target"]}:
                r["alias"] = form
                return ""
            return "citation not in the index; %s gives node %s" % (form, ",".join(map(str, sorted(u))))
        return "citation not in the index"

    def cite_fail(r):
        if not r["ev"].startswith("cite:"):
            return ""
        c = compact(r["ev"][5:])
        g = {n for _, n in hits.get(c, ())}
        b = base_idx.get(c, set())
        u = g | b
        if not u:
            return alias_fail(r)
        if u == {r["target"]}:
            return ""
        if r["target"] not in u:
            return "index gives node %s" % ",".join(map(str, sorted(u)))
        what = "ambiguous in the graph index" if len(g) > 1 else "collides with the base index"
        collisions.setdefault(c, [what, 0])[1] += 1
        return "%s: %s" % (what, ",".join(map(str, sorted(u))))

    jobs_by_repo = collections.defaultdict(dict)
    for r in live:
        if r["target"] not in dec or (r["by"] >= 0 and r["by"] not in dec):
            reject(r, "badRow", "node not in decisions2")
            continue
        carry = r["by"] if r["text"] == "by" else r["target"]
        if "base_sha" in r:  # claim on a base row: its own text
            carry = r["by"] if r["by"] >= 0 and dec[r["by"]][2] == r["base_sha"] else r["target"]
            r["text"] = "by" if carry == r["by"] else "target"
        r["self_text"] = r["table"] == "history" and r["text"] == "target"
        r["by_date"] = dec[r["by"]][1] if r["by"] >= 0 else dec[r["target"]][1]
        r["by_scotus"] = r["by"] >= 0 and dec[r["by"]][0] == sc_id
        r["date"] = r["by_date"]
        r["ordered"] = True if r["by"] < 0 else dec[r["target"]][1] <= dec[r["by"]][1]
        r["sha"] = dec[carry][2]
        r["cite_fail"] = cite_fail(r)
        nr = L.node_row(carry)
        if len(nr) < 3 or nr[0] != str(carry):
            reject(r, "textMissing", "no nodes.tsv row")
            continue
        jobs_by_repo[nr[1]].setdefault((nr[2], r["sha"]), []).append(r)
    jobs = []
    for repo, d in jobs_by_repo.items():
        items = sorted((path, sha, rs) for (path, sha), rs in d.items())
        for k in range(0, len(items), 1500):
            jobs.append((repo, items[k:k + 1500]))
    jobs.sort(key=lambda j: -len(j[1]))
    st["texts_read"] = sum(len(j[1]) for j in jobs)
    res = {}
    if jobs:
        if a.procs > 1 and len(jobs) > 1:
            with Pool(min(a.procs, len(jobs)), initializer=_init, initargs=(cues,)) as pool:
                for o in pool.imap_unordered(worker, jobs):
                    for x in o:
                        res[x[0]] = x
        else:
            _init(cues)
            for j in jobs:
                for x in worker(j):
                    res[x[0]] = x
    good = []
    for r in live:
        if r["i"] not in res:
            continue
        _, reason, detail, pay = res[r["i"]]
        if reason:
            reject(r, reason, detail)
        else:
            r["pay"] = pay
            good.append(r)
    # ---- doctrine uniqueness (DESIGN7 2.4): base doctrine lines count too
    labs = collections.defaultdict(set)
    for k, v in base_doc.items():
        labs[k] |= v
    tie = lambda r: {compact(j["label"]) for j in r["joined"] if j["rel"] == "doctrineTie"}  # noqa: E731
    for r in good:
        if r["table"] == "treatments" and r["claim"] == "doctrine":
            for k in tie(r):
                labs[k].add(r["target"])
    amb_labels = {k for k, v in labs.items() if len(v) > 1}
    good2 = []
    for r in good:
        if r["table"] == "treatments" and r["claim"] == "doctrine" and tie(r) & amb_labels:
            reject(r, "doctrineAmbiguous", ",".join(sorted(tie(r) & amb_labels)))
            continue
        good2.append(r)
    # ---- duplicates: the first passing (table, by, target, kind) stands
    seen, kept = set(), []
    for r in good2:
        k = (r["table"], r["by"], r["target"], r["kind"])
        if k in seen:
            reject(r, "duplicate")
            continue
        seen.add(k)
        kept.append(r)
    # ---- history conflicts (certify6 points 3 and 4); claims on base rows are not new rows
    groups = collections.defaultdict(list)
    for r in kept:
        if r["table"] == "history" and "base_id" not in r and (r["kind"] in NEG or r["kind"] in POS):
            groups[(r["by"], r["target"])].append(r)
    bad = set()
    for g in groups.values():
        if any(r["kind"] in NEG for r in g) and any(r["kind"] in POS for r in g):
            if not all(r["scope"] == "unknown" for r in g):
                bad.update(r["i"] for r in g)
            else:
                st["conflict_kept_scope_unknown"] += len(g)
    base_conf = []
    out_t, out_h, out_claim_base = [], [], []
    used_tids = set(base_tids)
    for r in kept:
        if r["table"] == "history":
            if "base_id" in r:
                out_claim_base.append(r)
                continue
            if r["i"] in bad:
                reject(r, "conflict")
                continue
            hid = "h13:%d:%d:%s" % (r["by"], r["target"], r["kind"])
            clash = [(k, sc, bid) for k, sc, bid in hb_pair.get((r["by"], r["target"]), ())
                     if ((r["kind"] in NEG and k in POS) or (r["kind"] in POS and k in NEG))
                     and not (r["scope"] == "unknown" and sc == "unknown")]
            if clash:
                action = "kept" if a.keep_base_conflicts else "rejected"
                for k, sc, bid in clash:
                    base_conf.append((hid, bid, r["scope"], sc, action))
                st["base_conflict_" + action] += 1
                if not a.keep_base_conflicts:
                    reject(r, "conflictBase", clash[0][2])
                    continue
            r["id"] = hid
            out_h.append(r)
        else:
            tid = "t13:%d:%d:%d" % (r["by"], r["target"], r["main"][0])
            while tid in used_tids:
                tid += "b"
            used_tids.add(tid)
            r["id"] = tid
            out_t.append(r)
    # ---- tables
    wins = {}
    cite_out = set()
    alias_lines = collections.Counter()

    def add_cite(r):
        for cit, n in hits.get(compact(r["ev"][5:]), ()):
            if (cit, n) not in base_lines:
                cite_out.add((cit, n))
        if r.get("alias"):
            st["admitted_via_alias"] += 1
            by_rule[r["rule"]]["admitted_via_alias"] += 1
            if (r["ev"][5:], r["target"]) not in cite_out:
                cite_out.add((r["ev"][5:], r["target"]))
                alias_lines[r["alias"].split(">")[0]] += 1

    for r in out_t + out_h + out_claim_base:
        st["admitted"] += 1
        st["admitted:%s" % r["table"]] += 1
        by_rule[r["rule"]]["admitted"] += 1
        by_rule[r["rule"]]["admitted:" + r["kind"]] += 1
        st["admitted:%s:claim:%s" % (r["table"], r["claim"])] += 1
        s0, e0, w = r["pay"]["win"]
        wins[(r["sha"], s0, e0)] = w
        if r["table"] == "treatments":
            st["admitted_treatments_joined_%d" % len(r["joined"])] += 1
            for jp in r["pay"].get("joined", ()):
                s0, e0, w = jp["win"]
                wins[(r["sha"], s0, e0)] = w
            if r["ev"].startswith("cite:"):
                add_cite(r)
        else:
            if r["anchor"] is not None:
                s0, e0, w = r["pay"]["a_win"]
                wins[(r["sha"], s0, e0)] = w
            if "base_id" in r:
                st["claim_on_base_admitted"] += 1
            elif r["ev"].startswith("cite:") and not (r["self_text"] and r["anchor"] is None):
                add_cite(r)

    def write(name, lines):
        p = os.path.join(a.out, name)
        with open(p, "w", encoding="utf-8", newline=NL) as f:
            for l in lines:
                f.write(TAB.join(map(str, l)) + NL)
        with open(p, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()

    sha = {}
    sha["treatments_delta.tsv"] = write("treatments_delta.tsv", (
        (r["id"], r["by"], r["target"], r["date"], r["kind"], r["scope"], "unknown", 1, r["sha"], r["main"][0],
         r["main"][1], r["pay"]["quote"], r["ev"], r["part"], r["reader"], r["conf"]) for r in out_t))
    sha["treatment_class_delta.tsv"] = write("treatment_class_delta.tsv", (
        (r["id"], r["claim"], r["field_limit"], r["doctrine"] if r["claim"] == "doctrine" else
         (r["doctrine"] if r["doctrine"] else "-"), "r7:" + r["rule"]) for r in out_t if r["claim"] != "-"))
    sha["joined_delta.tsv"] = write("joined_delta.tsv", (
        (r["id"], "treatments", j["rel"], j["span"][0], j["span"][1], jp["quote"], j["part"], j["label"],
         "r7:" + r["rule"]) for r in out_t for j, jp in zip(r["joined"], r["pay"].get("joined", ()))))
    sha["history_delta.tsv"] = write("history_delta.tsv", (
        (r["id"], r["target"], r["by"], r["date"], r["kind"], r["scope"], r["sha"], r["main"][0], r["main"][1],
         r["pay"]["quote"], r["ev"], r["part"], "r7:" + r["rule"]) for r in out_h))
    sha["history_anchor_delta.tsv"] = write("history_anchor_delta.tsv", (
        (r["id"], r["anchor"][0], r["anchor"][1], r["pay"]["a_quote"], r["anchor_part"], "r7:" + r["rule"])
        for r in out_h if r["anchor"] is not None))
    sha["history_claim_delta.tsv"] = write("history_claim_delta.tsv", (
        (r.get("base_id") or r["id"], r["claim"], "r7:" + r["rule"]) for r in out_h + out_claim_base
        if r["claim"] == "orderHead" or (r["claim"] == "setAside" and r["kind"] == "vacated")))
    st["claim_setAside_other_kind"] = sum(r["claim"] == "setAside" and r["kind"] != "vacated"
                                          for r in out_h + out_claim_base)
    wk = sorted(wins)
    sha["cert_text_delta.tsv"] = write("cert_text_delta.tsv", ((s, s0, e0, wins[(s, s0, e0)]) for s, s0, e0 in wk))
    sha["window_sha_delta.tsv"] = write("window_sha_delta.tsv", (
        (s, s0, e0, hashlib.sha1(wins[(s, s0, e0)].encode("utf-8")).hexdigest(), "corpus") for s, s0, e0 in wk))
    sha["cite_index_delta.tsv"] = write("cite_index_delta.tsv", sorted(cite_out))
    write("cite_collisions.tsv", (
        (c, ",".join(map(str, sorted({n for _, n in hits.get(c, ())}))),
         ",".join(map(str, sorted(base_idx.get(c, ())))), what, k) for c, (what, k) in sorted(collisions.items())))
    write("base_conflicts.tsv", base_conf)
    rejects.sort(key=lambda x: x[0])
    write("rejects.tsv", ((ref, reason, r["rule"] if r else "", r["by"] if r else "", r["target"] if r else "",
                           r["kind"] if r else "", detail.replace(TAB, " ").replace(NL, " "))
                          for _, ref, reason, r, detail in rejects))
    st["rejected"] = len(rejects)
    st["windows"] = len(wins)
    st["cite_index_lines"] = len(cite_out)
    st["cite_collisions"] = len(collisions)
    st["alias_keys_added"] = sum(alias_lines.values())
    kc = collections.Counter("%s:%s" % (r["table"], r["kind"]) for r in out_t + out_h)
    stats = {"args": sys.argv[1:], "base": a.base.replace(os.sep, "/"), "cue_source": cue_src,
             "scotus_court_id": sc_id, "order_head_from": cues["order_head_from"],
             "joined_gap_max": cues["joined_gap_max"],
             "counts": dict(sorted(st.items())), "admitted_by_kind": dict(sorted(kc.items())),
             "alias_keys_added_by_form": dict(sorted(alias_lines.items())),
             "by_rule": {k: dict(sorted(v.items())) for k, v in sorted(by_rule.items())}, "sha1": sha}
    with open(os.path.join(a.out, "stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(stats, f, indent=1)
        f.write(NL)
    print(json.dumps({"counts": stats["counts"], "admitted_by_kind": stats["admitted_by_kind"],
                      "cue_source": {k: v for k, v in cue_src.items() if v != "cue_table.json"}}, indent=1))
    skipped = st["in_base_skipped:treatments"] + st["in_base_skipped:history"]
    if st["input_rows"] != st["admitted"] + st["rejected"] + skipped:
        print("ERROR: rows unaccounted for (input %d, admitted %d, rejected %d, in base %d)" % (
            st["input_rows"], st["admitted"], st["rejected"], skipped), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
