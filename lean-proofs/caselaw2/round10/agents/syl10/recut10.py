"""syl10 (round 10, move 1): rule RO -- re-cut a zone-refused row onto the acting court's own sentence.

A treatments / history row whose main quote lies outside every zone of its part (v9c verdict partZone: a quote in
the syllabus / head matter, or straddling head matter and the opinion) is re-cut, when the SAME acting decision's
opinion zones (majority / plurality / perCuriam of the text owner, v9c part_zone.tsv) hold a sentence that states
the same act on the same target:

  act sentence   one sentence inside one court zone that (a) carries a plain cue of the row's kind
                 (cue_table hist[kind] / treat[kind]), (b) states the act as the court's own present act:
                 first person ("we [now|therefore|...] affirm / reverse / vacate / overrule ..."), a passive present
                 ("... is / are / be [hereby] affirmed / overruled ..."), or a bare disposition line ("Affirmed.",
                 "Judgment reversed and remanded."), and (c) has no disqualifier (cue_table disqualify_hist /
                 disqualify_treat, plus: would / should / could / dissent / concur / whether / need not / decline /
                 refuse / unless, or a negation right before the act verb).
  target tie     plain: the row's evidence (cite key, or name tokens) inside [start-400, end+400) of the sentence;
                 name tie (treatments, cite rows only): a party token of a "X v. Y, <cite key>" citation of the
                 target printed in the same text's court zones, found in the sentence's window (generic party words
                 and state names never count);
                 anchored (history only): a second sentence (or it and the sentence before it) inside one court zone holding the row's evidence and a
                 cue_table `anchor` cue, no `disqualify_anchor` phrase, and a below-tie (the cite printed bare, or
                 under a caption whose party token is in the acting decision's own caption).
  choice         plain before name tie before anchored; the evidence inside the sentence itself first; a sentence without another disposition / "in part" before
                 a mixed one; then the last such sentence of the court zones (the final disposition).
  scope          history: "unknown" when the chosen sentence is mixed (another kind's act or "in part"), else the
                 row's; treatments: "partialUnknown" when the sentence limits the act ("to the extent", "in
                 relevant part", "in part", "insofar"), else the row's (an issue scope is kept only as partialUnknown).
No sentence => the row stays refused (reason written). Head matter / syllabus text is never quoted, never an anchor.

    python -X utf8 recut10.py --ids work/pz_ids.txt --out work/recut

Writes rows.jsonl (certify9/10 rows; rule syl10:RO:<tie>), remove_ids.txt (the refused ids that got a re-cut),
recut.tsv (id, outcome, tie, main span, anchor span, sentence) and prints counts. No answer-key file is read.
"""
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402
import certify6 as C6  # noqa: E402

NL, TAB = "\n", "\t"
STAGE = os.path.join(C2, "round9", "stage", "v9c")
COURT = ("majority", "plurality", "perCuriam")
PAD = 400

HIST_VERB = {  # kind -> (present stem regex, past form regex)
    "affirmed": (r"affirm", r"affirmed"), "reversed": (r"reverse", r"reversed"), "vacated": (r"vacate", r"vacated"),
    "withdrawn": (r"withdraw", r"withdrawn"), "modified": (r"modify", r"modified"), "remanded": (r"remand", r"remanded"),
}
TREAT_VERB = {
    "overruled": (r"overrule", r"overruled"), "disapproved": (r"disapprove", r"disapproved"),
    "recededFrom": (r"recede", r"receded"), "abrogated": (r"abrogate", r"abrogated"),
}
ADV = r"(?:(?:now|therefore|hereby|accordingly|thus|also|then|so|must|shall|will|expressly|today|further|" \
      r"respectfully|consequently|hence|and|,)\s+)*"
EXTRA_DISQ = ("would ", "should ", "could ", "dissent", "concur", "whether", "need not", "declin", "refuse",
              "if we ", "were we ", "unless ")
NEG = r"(?:\bnot|\bnever|n't|\bno)\s+(?:[a-z]+\s+)?"  # a negation right before the act verb
LIMIT = ("to the extent", "in relevant part", "in part", "portion of", "insofar", "in so far", "so far as")
GENERIC = set("""state states united america people commonwealth county city town village inc co corp company
corporation board commission department government district territory republic nation ltd llc bank the of and in
re ex rel parte estate matter""".split())
STATE_NAMES = set("""alabama alaska arizona arkansas california colorado connecticut delaware florida georgia hawaii
idaho illinois indiana iowa kansas kentucky louisiana maine maryland massachusetts michigan minnesota mississippi
missouri montana nebraska nevada hampshire jersey mexico york carolina dakota ohio oklahoma oregon pennsylvania rhode
island tennessee texas utah vermont virginia washington wisconsin wyoming columbia""".split())
ABBR = re.compile(r"(?:\b[A-Za-z]|\bv|\bvs|\bNo|\bNos|\bCo|\bInc|\bCorp|\bLtd|\bCir|\bSupp|\bApp|\bCt|\bFed|\bDist"
                  r"|\bJ|\bJJ|\bC\.\s?J|\bMr|\bMrs|\bDr|\bSt|\bed|\bId|\bid|\bat|\bsupra|\bcert|\bden|\bRev|\bStat"
                  r"|\bU\.\s?S|\be\.g|\bi\.e|\bArt|\bSec|\bpp|\bp|\bn|\bnn|\bcl|\bch|\bRep|\bAss'n"
                  r"|\bL\.\s?Ed|\bS\.\s?Ct|\bF\.\s?\dd|\bF|\bSo|\bN\.\s?E|\bN\.\s?W|\bS\.\s?E|\bS\.\s?W|\bP|\bA)\.$")


def sentences(text, a, b):
    """[(s, e)] sentence spans inside [a, b): split after . ! ? (plus closing quotes / brackets) followed by
    whitespace and an upper-case letter, digit-free capital or quote, or at a blank line; abbreviations kept."""
    out = []
    s = a
    i = a
    while i < b:
        ch = text[i]
        cut = None
        if (ch == NL and i + 1 < b and text[i + 1] == NL) or ch == "\x0c":
            cut = i
        elif ch in ".!?":
            j = i + 1
            while j < b and text[j] in "\"'”’)]":
                j += 1
            if j < b and text[j] in " \n\t":
                k = j
                while k < b and text[k] in " \n\t":
                    k += 1
                if k >= b or text[k].isupper() or text[k] in "\"'“‘(":
                    if not (ch == "." and ABBR.search(text[max(a, i - 12):i + 1])):
                        cut = j
        if cut is not None:
            out.append((s, cut))
            s = cut
            i = cut
        i += 1
    out.append((s, b))
    res = []
    for s, e in out:
        while s < e and text[s] in " \n\t":
            s += 1
        while e > s and text[e - 1] in " \n\t":
            e -= 1
        if e - s >= 6:
            res.append((s, e))
    return res


def act_re(verbs, kind):
    pres, past = verbs[kind]
    first = re.compile(r"\bwe\s+" + ADV + r"(?:[a-z]+\s+){0,1}?" + ADV + pres + r"(?:s)?\b")
    passive = re.compile(r"\b(?:is|are|be|stands|stand)\s+(?:hereby\s+|therefore\s+|accordingly\s+|now\s+|also\s+|"
                         r"expressly\s+|in all respects\s+|in part\s+|in its entirety\s+|in their entirety\s+)*"
                         + past + r"\b")
    bare = re.compile(r"^(?:the\s+)?(?:(?:judgment|judgments|decree|order|orders|conviction|convictions|sentence|"
                      r"sentences|decision|ruling|award)\s+(?:of\s+[^.;]{0,120}?\s+)?(?:is\s+|are\s+)?)?" + past + r"\b")
    neg = re.compile(NEG + pres)
    return first, passive, bare, neg


def is_act(sl, regs):
    first, passive, bare = regs[:3]
    if regs[3].search(sl):
        return False
    return bool(first.search(sl) or passive.search(sl) or bare.search(sl.strip()))


def cite_pattern(key):
    """printed-cite regex for a compact cite key 'vol reporter page' (e.g. '468 us 447')."""
    p = key.split(" ")
    if len(p) < 3:
        return None
    vol, page, rep = p[0], p[-1], "".join(p[1:-1])
    rr = r"[\s.]*".join(re.escape(c) for c in rep)
    return re.compile(r"\b" + re.escape(vol) + r"\s+" + rr + r"\.?\s+" + re.escape(page) + r"\b", re.I)


def party_tokens(text, m_start, lo):
    """party tokens of a 'X v. Y, <cite>' citation that ends at m_start (searching back to lo)."""
    seg = text[max(lo, m_start - 160):m_start]
    k = seg.rfind(" v. ")
    if k < 0:
        return []
    left = re.findall(r"[A-Z][A-Za-z'’\-]+", seg[max(0, k - 60):k])
    right = re.findall(r"[A-Z][A-Za-z'’\-]+", seg[k + 4:])
    toks = []
    if left:
        toks.append(left[-1])
    if right:
        toks.append(right[0])
    return [t for t in toks if len(C6.compact(t)) >= 3 and C6.compact(t) not in GENERIC
            and C6.compact(t) not in STATE_NAMES]


def own_caption_tokens(text):
    """capitalised tokens of the acting decision's own caption (front matter title or first 400 characters)."""
    m = re.search(r"^title:\s*(.+)$", text[:3000], re.M)
    cap = m.group(1) if m else text[:400]
    return set(C6.compact(t) for t in re.findall(r"[A-Z][A-Za-z'’\-]+", cap)) - GENERIC - STATE_NAMES


def zone_of(zs, s, e):
    for a, b, p in zs:
        if a <= s and e <= b:
            return p
    return None


def load_rows(ids):
    out = {}
    for tab in ("history", "treatments"):
        for ln in open(os.path.join(STAGE, tab + ".tsv"), encoding="utf-8"):
            p = ln.rstrip(NL).split(TAB)
            if p[0] in ids:
                out[p[0]] = (tab, p)
    return out


def load_set(name, col=0):
    s = set()
    for ln in open(os.path.join(STAGE, name), encoding="utf-8"):
        s.add(ln.split(TAB)[col].rstrip(NL))
    return s


def load_zones(nodes):
    zs = collections.defaultdict(list)
    for ln in open(os.path.join(STAGE, "part_zone.tsv"), encoding="utf-8"):
        p = ln.rstrip(NL).split(TAB)
        n = int(p[0])
        if n in nodes:
            zs[n].append((int(p[1]), int(p[2]), p[3]))
    return {n: sorted(v) for n, v in zs.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--strict", action="store_true",
                    help="RO-strict: no previous-sentence join for anchors, no mixed act sentence (offered after audit r10y01)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ids = set(x.strip().split(TAB)[0] for x in open(a.ids, encoding="utf-8") if x.strip())
    rows = load_rows(ids)
    witness = load_set("treatment_witness.tsv")
    joined = load_set("joined.tsv")
    tab_cue = json.load(open(C6.CUE_JSON, encoding="utf-8"))
    cues, _ = C6.load_cues()
    treat_cue = tab_cue["treat"]
    disq_treat = [c for c in tab_cue["disqualify_treat"] if c]
    disq_hist = cues["disqualify_hist"]

    def owner(tab, p):
        return int(p[2]) if tab == "history" else int(p[1])

    nodes = set(owner(*v) for v in rows.values())
    texts = L.fetch_texts(nodes)
    zones = load_zones(nodes)
    cnt = collections.Counter()
    fo = open(os.path.join(a.out, "rows.jsonl"), "w", encoding="utf-8", newline=NL)
    ft = open(os.path.join(a.out, "recut.tsv"), "w", encoding="utf-8", newline=NL)
    fr = open(os.path.join(a.out, "remove_ids.txt"), "w", encoding="utf-8", newline=NL)
    for rid in sorted(rows):
        tab, p = rows[rid]
        by = owner(tab, p)
        if tab == "history":
            target, kind, scope, ev = int(p[1]), p[4], p[5], p[10]
            verbs, cl, dq = HIST_VERB, cues["hist"].get(kind, ()), disq_hist
        else:
            target, kind, scope, ev = int(p[2]), p[4], p[5], p[12]
            verbs, cl, dq = TREAT_VERB, treat_cue.get(kind, ()), disq_treat
        cnt["rows:" + tab] += 1

        def out(reason, tie="-", main=None, anc=None, sent=""):
            cnt["%s:%s" % (tab, reason)] += 1
            ft.write(TAB.join([rid, reason, tie, "%d-%d" % main if main else "-", "%d-%d" % anc if anc else "-",
                               sent[:300]]) + NL)

        if tab == "history" and p[6] and by < 0:
            out("noTextOwner")
            continue
        if rid in witness or rid in joined:
            out("witnessOrJoinedRow")
            continue
        if kind not in verbs:
            out("kindNotHandled:" + kind)
            continue
        if by not in texts:
            out("noText")
            continue
        text = texts[by][1]
        zs = zones.get(by, [])
        courts = [z for z in zs if z[2] in COURT]
        if not courts:
            out("noCourtZone")
            continue
        regs = act_re(verbs, kind)
        other = [act_re(verbs, k) for k in verbs if k != kind and k not in ("remanded", "modified")]
        cands = []
        for za, zb, zp in courts:
            for s, e in sentences(text, za, zb):
                ql = C6.lower(C6.norm(text[s:e]))
                if not any(c in ql for c in cl):
                    continue
                if any(c in ql for c in dq) or any(c in ql for c in EXTRA_DISQ):
                    continue
                if not is_act(ql, regs):
                    continue
                if len(ql) > 600:
                    continue
                mixed = any(is_act(ql, r) for r in other) or any(x in ql for x in LIMIT)
                if a.strict and mixed and tab == "history":
                    continue
                cands.append((s, e, zp, mixed, ql))
        if not cands:
            out("noActSentence")
            continue
        n = len(text)
        best = None
        # plain
        for s, e, zp, mixed, ql in cands:
            win = C6.norm(text[max(0, s - PAD):min(n, e + PAD)])
            if C6.ev_in(ev, win):
                key = (0, not C6.ev_in(ev, C6.norm(text[s:e])), mixed, -s)
                if best is None or key < best[0]:
                    best = (key, "plain", (s, e, zp, mixed), None, ev)
        # name tie (treatments, cite evidence)
        if best is None and tab == "treatments" and ev.startswith("cite:"):
            pat = cite_pattern(ev[5:])
            toks = collections.Counter()
            if pat:
                for za, zb, zp in courts:
                    for m in pat.finditer(text, za, zb):
                        for t in party_tokens(text, m.start(), za):
                            toks[t] += 1
            for s, e, zp, mixed, ql in cands:
                win = C6.norm(text[max(0, s - PAD):min(n, e + PAD)])
                for t in toks:
                    if C6.ev_in("name:" + t, win):
                        key = (1, not C6.ev_in("name:" + t, C6.norm(text[s:e])), mixed, -s)
                        if best is None or key < best[0]:
                            best = (key, "nameTie", (s, e, zp, mixed), None, "name:" + t)
        # anchored (history)
        if best is None and tab == "history":
            capt = own_caption_tokens(text)
            pat = cite_pattern(ev[5:]) if ev.startswith("cite:") else None
            anchors = []
            spans = []
            for za, zb, zp in courts:
                ss = sentences(text, za, zb)
                for k, (s, e) in enumerate(ss):
                    spans.append((s, e, zp))
                    if k > 0 and not a.strict:  # the sentence with the citation joined to the one before it (a clause the
                        spans.append((ss[k - 1][0], e, zp))  # splitter cut at an abbreviation, or its subject)
            for s, e, zp in spans:
                if True:
                    aq = C6.norm(text[s:e])
                    al = C6.lower(aq)
                    if len(aq) > 600 or not C6.ev_in(ev, aq):
                        continue
                    if not any(c in al for c in cues["anchor"]) or any(c in al for c in cues["disqualify_anchor"]):
                        continue
                    if pat:
                        tied = False
                        for m in pat.finditer(text, s, e):
                            seg = text[max(s, m.start() - 160):m.start()]
                            if " v. " not in seg[-160:]:
                                tied = True
                            elif set(C6.compact(t) for t in party_tokens(text, m.start(), s)) & capt:
                                tied = True
                        if not tied:
                            continue
                    anchors.append((s, e, zp))
            if anchors:
                an = anchors[0]
                for s, e, zp, mixed, ql in cands:
                    key = (2, True, mixed, -s)
                    if best is None or key < best[0]:
                        best = (key, "anchored", (s, e, zp, mixed), an, ev)
        if best is None:
            out("noTie")
            continue
        _, tie, (s, e, zp, mixed), an, ev2 = best
        assert zone_of(zs, s, e) == zp
        if an:
            assert zone_of(zs, an[0], an[1]) == an[2]
        sent = C6.norm(text[s:e])
        if tab == "history":
            sc = "unknown" if mixed else (scope if scope in ("all", "unknown") else "unknown")
        else:
            sc = "partialUnknown" if mixed else (scope if scope in ("all", "partialUnknown", "otherGrounds",
                                                                     "unknown") else "partialUnknown")
        row = {"rule": "syl10:RO:" + tie, "table": tab, "by": by, "target": target, "kind": kind, "scope": sc,
               "main": [s, e], "part": zp, "ev": ev2, "claim": "-", "note": "re-cut of " + rid}
        if tab == "history":
            row.update({"anchor": [an[0], an[1]] if an else None, "anchor_part": an[2] if an else None,
                        "text": "by"})
        fo.write(json.dumps(row, ensure_ascii=False) + NL)
        fr.write(rid + NL)
        out("recut", tie, (s, e), (an[0], an[1]) if an else None, sent)
    fo.close()
    ft.close()
    fr.close()
    print(json.dumps(dict(sorted(cnt.items())), indent=1))


if __name__ == "__main__":
    main()
