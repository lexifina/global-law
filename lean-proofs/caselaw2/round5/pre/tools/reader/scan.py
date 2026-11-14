"""Candidate pass of the caselaw-lean-2 treatment/history reader, one repo per process.

    python -X utf8 scan.py <repo-name> [--limit-paths FILE]

Streams every decision file of ~/Documents/us-caselaw-repos/<repo> from git (`git cat-file --batch`; there is no
checkout) and writes data/reader_work/cand/<repo>.jsonl.gz (atomically; a finished repo is skipped on rerun).

Offsets follow SCHEMA.md: character offsets into the file text as read from git HEAD, UTF-8 decoded, "\r\n" -> "\n".
`sha` is sha1 of the file bytes. Windows are stored normalised (tab/newline -> space, one for one, so offsets hold).

Record kinds (one JSON object per line):
  {"t":"d", ...}  one per decision that has at least one candidate: node, sha, title, text length, the decision's
                  part map, prospectivity sentences
  {"t":"c", ...}  a treatment candidate: family, match span, sentence span, window (sentence +-800), part, citations
  {"t":"h", ...}  a same-case history candidate (the reviewing court's own disposition sentence)
Nothing is read from events_v3/reports.tsv; later courts' notes are not used as evidence (they are classified out in
filter.py, never kept as treatments).
"""
import gzip, hashlib, json, os, re, subprocess, sys, threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (CITE_RX, NL, cite_key, name_tokens, part_map, part_at, sentence_span, WORK, REPOS)  # noqa: E402

FAM = {
    "overrule": re.compile(r"\boverrul(?:e|es|ed|ing)\b", re.I),
    "disapprove": re.compile(r"\bdisapprov(?:e|es|ed|ing)\b", re.I),
    "recede": re.compile(r"\breced(?:e|es|ed|ing)\s+from\b", re.I),
    "abrogate": re.compile(r"\babrogat(?:e|es|ed|ing)\b", re.I),
    "supersede": re.compile(r"\bsupersed(?:e|es|ed|ing)\b", re.I),
    "limit": re.compile(r"\blimit(?:ed|s|ing)?\s+(?:[\w’']+\s+){0,5}?to\s+(?:its|their)\s+(?:own\s+|particular\s+|specific\s+|"
                        r"peculiar\s+|precise\s+|unique\s+)?facts\b", re.I),
    "question": re.compile(r"\b(?:call(?:s|ed|ing)?|cast(?:s|ing)?|place[sd]?|throw[sn]?|threw)\s+(?:[\w’']+\s+){0,5}?"
                           r"(?:into\s+|in\s+)(?:question|doubt)\b|\bquestion(?:s|ed|ing)?\s+the\s+(?:continued\s+)?"
                           r"(?:validity|vitality|soundness|correctness|wisdom)\b|\bno\s+longer\s+(?:good|valid|sound)\s+law\b|"
                           r"\b(?:continued|continuing)\s+(?:validity|vitality)\b", re.I),
    "declineFollow": re.compile(r"\b(?:declin(?:e|es|ed|ing)|refus(?:e|es|ed|ing)|unwilling|not\s+inclined)\s+to\s+"
                                r"(?:follow|adopt|apply|extend)\b|\bwe\s+(?:do\s+not|will\s+not|cannot|shall\s+not|no\s+longer)\s+"
                                r"(?:follow|adhere\s+to)\b", re.I),
    "repudiate": re.compile(r"\brepudiat(?:e|es|ed|ing)\b|\b(?:we|court)\s+(?:now\s+|hereby\s+|therefore\s+|today\s+|expressly\s+)?"
                            r"(?:abandon|reject)s?\s+(?:the\s+)?(?:rule|holding|doctrine|reasoning|test|approach|view|"
                            r"analysis|dictum|dicta|standard|language)\b|\bno\s+longer\s+(?:follow|adhere\s+to|recognize|"
                            r"be\s+followed|be\s+considered\s+(?:good|controlling))\b", re.I),
}
# literal anchors (searched with str.find in the lower-cased text; the regex then runs only around each anchor):
# family -> (anchors, chars before, chars after)
ANCH = {
    "overrule": (("overrul",), 20, 30), "disapprove": (("disapprov",), 20, 30), "recede": (("reced",), 20, 40),
    "abrogate": (("abrogat",), 20, 30), "supersede": (("supersed",), 20, 30), "limit": (("facts",), 140, 10),
    "question": (("question", "doubt", "good law", "valid law", "sound law", "vitality", "validity"), 120, 60),
    "declineFollow": (("declin", "refus", "unwilling", "inclined", "we do not", "we will not", "we cannot",
                       "we shall not", "we no longer"), 20, 60),
    "repudiate": (("repudiat", "abandon", "reject", "no longer"), 80, 120),
}
HIST_ANCH = (("affirm", "revers", "vacat", "modif", "set aside", "quash", "annul", "withdr", "reinstat", "denied",
              "granted", "dismissed", "depublish", "published", "refused"), 300, 140)
PROSP_ANCH = (("prospectiv", "apply only to", "from and after the date of this", "mandate shall",
               "with the exception of the part"), 60, 80)


def anchored(rx, text, low, spec, lo=0):
    """Matches of rx that overlap an anchor occurrence (same matches as a full scan for these patterns)."""
    anchors, back, fwd = spec
    pos = []
    for kw in anchors:
        i = low.find(kw, lo)
        while i >= 0:
            pos.append(i)
            i = low.find(kw, i + 1)
    if not pos:
        return []
    pos.sort()
    n = len(text)
    seen = {}
    covered = -1
    for p in pos:
        if p < covered:
            continue
        for m in rx.finditer(text, max(lo, p - back), min(n, p + fwd)):
            if m.start() <= p < m.end() or m.start() >= p:
                seen[(m.start(), m.end())] = m
        covered = p + 1
    return [seen[k] for k in sorted(seen)]


# the reviewing court's own disposition (present tense / performative only; narrated history such as "was reversed"
# is not matched)
HIST = re.compile(
    r"\b(?:judgments?|decrees?|orders?|decisions?|rulings?|opinions?|sentences?|convictions?|awards?|determinations?)\b"
    r"[^.;\n]{0,200}?\b(?:is|are|be|stands?|must\s+be|should\s+be|will\s+be|shall\s+be)\s+(?:hereby\s+|therefore\s+|"
    r"accordingly\s+|in\s+all\s+things\s+|in\s+all\s+respects\s+|in\s+part\s+|respectfully\s+|now\s+|consequently\s+|"
    r"thus\s+)*(?P<k1>affirmed|reversed|vacated|modified|set\s+aside|quashed|annulled|withdrawn|reinstated)\b"
    r"|\b(?:we|the\s+court)\s+(?:therefore\s+|accordingly\s+|hereby\s+|now\s+|thus\s+|must\s+|respectfully\s+)?"
    r"(?P<k2>affirm|reverse|vacate|modify|withdraw|reinstate)\b(?!\s+(?:on|in)\s+other\s+grounds)"
    r"|^\s*(?:the\s+)?(?:judgments?\s+|orders?\s+|decrees?\s+)?(?P<k3>affirmed|reversed|vacated|modified|"
    r"reversed\s+and\s+remanded|vacated\s+and\s+remanded|affirmed\s+in\s+part|reversed\s+in\s+part|"
    r"affirmed\s+as\s+modified)\b[^\n]{0,120}$"
    r"|\b(?:petition\s+for\s+(?:a\s+)?writ\s+of\s+)?certiorari\s+(?:is\s+)?(?P<k4>denied|granted|dismissed)\b"
    r"|\b(?:petition\s+for\s+review|review|rehearing\s+en\s+banc|leave\s+to\s+appeal|petition\s+for\s+rehearing\s+en\s+banc|"
    r"application\s+for\s+leave\s+to\s+appeal)\s+(?:is\s+|are\s+|be\s+)?(?:hereby\s+)?(?P<k5>denied|granted|dismissed)\b"
    r"|\b(?:ordered|directed)\s+(?:that\s+the\s+opinion\s+)?(?:be\s+)?(?P<k6>depublished|not\s+(?:to\s+be\s+)?(?:officially\s+)?published)\b"
    r"|\b(?P<k7>writ\s+(?:of\s+error\s+)?(?:refused|ref'd)(?:,?\s*(?:n\.\s?r\.\s?e\b\.?|no\s+reversible\s+error))?)",
    re.I | re.M)

PROSP = re.compile(r"\bprospective(?:ly)?\b|\bpurely\s+prospective|\bapply\s+only\s+to\s+(?:cases|conduct|causes|claims|"
                   r"actions)|\bfrom\s+and\s+after\s+the\s+date\s+of\s+this\s+(?:opinion|decision)|\bmandate\s+shall\s+"
                   r"(?:be\s+stayed|not\s+issue)|\bwith\s+the\s+exception\s+of\s+the\s+part(?:y|ies)\s+(?:before|here)", re.I)
NAME_STOP = None  # set in common


def norm(s):
    return s.replace("\t", " ").replace("\n", " ")


def cites_between(text, a, b):
    out = []
    for m in CITE_RX.finditer(text, a, b):
        k = cite_key(m)
        if k:
            out.append([m.start(), m.end(), k])
    return out


def scan_text(nid, sha, text, st_counts=None):
    """Candidates of one decision (text already CRLF-normalised)."""
    if st_counts is None:
        st_counts = {}
    body0 = 0
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            body0 = e + 4
    low = text.lower()
    hw = False
    if HW_MODE:
        import common as _c
        hw = _c.hard_wrapped(text, body0)
        if HW_ONLY and not hw:
            return None
    orig = text
    fam_hits = []
    if hw:
        # round 3: sentences are cut on the same-length unwrapped view; the family patterns run on the de-hyphenated
        # string and their spans are mapped back, so every recorded offset is an offset of the original text
        text = _c.unwrap_view(orig, body0)
        dh, omap = _c.dehyphen(orig, body0, text)
        dlow = dh.lower()
        for fam, rx in FAM.items():
            for m in anchored(rx, dh, dlow, ANCH[fam], body0):
                fam_hits.append((fam, _c.Span(m, omap)))
        st_counts["hw"] = st_counts.get("hw", 0) + 1
    else:
        for fam, rx in FAM.items():
            for m in anchored(rx, text, low, ANCH[fam], body0):
                fam_hits.append((fam, m))
    hist_hits = anchored(HIST, text, low, HIST_ANCH, body0)
    if not fam_hits and not hist_hits:
        return None
    pm, body0 = part_map(orig)
    cands, hists = [], []
    seen_sent = {}
    for fam, m in fam_hits:
        s0, s1 = sentence_span(text, m.start(), m.end())
        key = (s0, s1)
        if key in seen_sent:
            c = seen_sent[key]
            if fam not in c["fam"]:
                c["fam"].append(fam)
            if [m.start(), m.end()] not in c["m"]:
                c["m"].append([m.start(), m.end()])
            continue
        part, sec = part_at(pm, m.start())
        if part == "front":
            continue
        w0, w1 = max(0, s0 - 800), min(len(text), s1 + 800)
        c = {"t": "c", "n": nid, "fam": [fam], "m": [[m.start(), m.end()]], "s0": s0, "s1": s1, "w0": w0,
             "w1": w1, "part": part, "sec": sec, "c": cites_between(text, max(0, s0 - 400), min(len(text), s1 + 400))}
        if hw:
            c["hw"] = 1
        seen_sent[key] = c
        cands.append(c)
    title = ""
    mt = re.search(r"^# (.+)$", text[body0:body0 + 3000], re.M)
    if mt:
        title = mt.group(1).strip()
    if hist_hits:
        # the decision under review: a citation whose preceding 250 characters carry one of this decision's own
        # party-name tokens (head matter, the first 6,000 characters of the opinion, or near the disposition)
        toks = name_tokens(title)
        selfc = {}
        if toks:
            tok_rx = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in sorted(toks)) + r")\b")
            first_op = next((a for a, b, p, s_ in pm if p not in ("front", "headmatter", "title")), body0)
            zones = [(body0, min(len(text), first_op + 6000))]
            zones += [(max(body0, m.start() - 2900), min(len(text), m.end() + 400)) for m in hist_hits]
            for z0, z1 in zones:
                for c in cites_between(text, z0, z1):
                    if c[0] in selfc:
                        continue
                    if tok_rx.search(text, max(0, c[0] - 250), c[0]):
                        selfc[c[0]] = c
        selfs = sorted(selfc.values())
        st_counts["hist_hits"] = st_counts.get("hist_hits", 0) + len(hist_hits)
        for m in (hist_hits if selfs else []):
            part, sec = part_at(pm, m.start())
            if part in ("dissent", "concurrence", "dissent~", "concurrence~", "front"):
                continue
            kind = next((m.group(g) for g in ("k1", "k2", "k3", "k4", "k5", "k6", "k7") if m.group(g)), "")
            s0, s1 = sentence_span(text, m.start(), m.end())
            if hists and hists[-1]["s0"] == s0:
                continue
            inwin = [c for c in selfs if s0 - 400 <= c[0] and c[1] <= s1 + 400]
            before = [c for c in selfs if c[0] < s0 and s0 - c[0] <= 2500]
            if inwin:
                mode, q0, q1, tcs = "win", s0, s1, inwin
            elif before:
                mode, q0, q1, tcs = "long", before[-1][0], s1, [before[-1]]
            else:
                mode, q0, q1, tcs = "remote", s0, s1, selfs[:3]
            w0, w1 = max(0, q0 - 400), min(len(text), q1 + 400)
            hists.append({"t": "h", "n": nid, "k": re.sub(r"\s+", " ", kind.lower()), "m": [m.start(), m.end()],
                          "s0": s0, "s1": s1, "q0": q0, "q1": q1, "mode": mode, "w0": w0, "w1": w1, "part": part,
                          "sec": sec, "tc": tcs})
    if not cands and not hists:
        return None
    for c in cands + hists:
        c["w"] = norm(text[c["w0"]:c["w1"]])
    pros = []
    for m in anchored(PROSP, text, low, PROSP_ANCH, body0):
        part, _ = part_at(pm, m.start())
        if part in ("dissent", "concurrence", "dissent~", "concurrence~", "front", "headmatter"):
            continue
        s0, s1 = sentence_span(text, m.start(), m.end())
        if pros and pros[-1][0] == s0:
            continue
        pros.append([s0, s1, norm(text[s0:s1])[:600]])
        if len(pros) >= 4:
            break
    d = {"t": "d", "n": nid, "sha": sha, "title": title, "len": len(text),
         "parts": [[a, b, p] for a, b, p, s_ in pm], "pros": pros}
    if hw:
        # round 3: hard-wrapped decisions (CourtListener texts) have no edges in graph/edges.bin, so the names of the
        # decisions they cite cannot be looked up there; keep the citation keys of the whole text instead
        d["hw"] = 1
        d["tc"] = sorted({k for _a, _b, k in cites_between(text, body0, len(text))})
    return d, cands, hists


CAND_DIR = None  # set by scan2.py; default data/reader_work/cand
HW_MODE = False  # round 3 (scan3.py): unwrap hard-wrapped texts before sentence splitting
HW_ONLY = False  # round 3: keep only hard-wrapped decisions (the re-read pass)


def main(repo):
    nodes = {}
    for line in open(os.path.join(WORK, "nodes", repo + ".tsv"), encoding="utf-8"):
        p, nid, date, court = line.rstrip("\n").split("\t")
        nodes[p] = int(nid)
    cand_dir = CAND_DIR or os.path.join(WORK, "cand")
    os.makedirs(cand_dir, exist_ok=True)
    out = os.path.join(cand_dir, repo + ".jsonl.gz")
    if os.path.exists(out):
        print(repo, "done already")
        return
    rd = os.path.join(REPOS, repo)
    tree = subprocess.run(["git", "-C", rd, "ls-tree", "-r", "HEAD", "--", "decisions"], capture_output=True,
                          check=True, creationflags=0x08000000).stdout.decode("utf-8")
    items = []
    for line in tree.splitlines():
        meta, path = line.split("\t", 1)
        _, typ, bsha = meta.split()
        if typ == "blob" and path.endswith(".md"):
            items.append((bsha, path))
    p = subprocess.Popen(["git", "-C", rd, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         creationflags=0x08000000)

    def feed():
        for bsha, _ in items:
            p.stdin.write((bsha + "\n").encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    st = {"files": 0, "nonode": 0, "badutf8": 0, "decisions_with_cand": 0, "cand": 0, "hist": 0}
    tmp = out + ".part"
    with gzip.open(tmp, "wt", encoding="utf-8", newline="\n", compresslevel=5) as fo:
        for bsha, path in items:
            header = p.stdout.readline().split()
            size = int(header[2])
            data = p.stdout.read(size)
            p.stdout.read(1)
            st["files"] += 1
            nid = nodes.get(path)
            if nid is None:
                st["nonode"] += 1  # a parallel-reporter copy merged into another node in graph/
                continue
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("utf-8", "replace")
                st["badutf8"] += 1
            text = text.replace("\r\n", "\n")
            r = scan_text(nid, hashlib.sha1(data).hexdigest(), text, st)
            if r is None:
                continue
            d, cands, hists = r
            st["decisions_with_cand"] += 1
            st["cand"] += len(cands)
            st["hist"] += len(hists)
            fo.write(json.dumps(d, ensure_ascii=False) + "\n")
            for c in cands + hists:
                fo.write(json.dumps(c, ensure_ascii=False) + "\n")
    p.wait()
    os.replace(tmp, out)
    with open(os.path.join(cand_dir, repo + ".stats.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f)
    print(repo, json.dumps(st), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
