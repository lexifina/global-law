"""Find later courts' notes on earlier decisions (the evaluation's gold) in one US case-law repo of global-law.

    python tools/caselaw2/eval/notes_extract.py <repo-dir> <out-dir>

A note is a court writing, about a decision it cites, what another court or a law did to it:
    X, 1 F.2d 2 (5th Cir. 1980), overruled in part by Y, 3 F.3d 4 ...
    X ... has been abrogated by Y / abrogation recognized by Y
    X, superseded by statute as stated in Y
    X, disapproved on other grounds in Y / receded from by Y
    X, 1 F.2d 2, rev'd, 450 U.S. 1 / vacated, 3 F.3d 4 / vacated on reh'g en banc, ...
Every decision file is read at HEAD through `git cat-file --batch` (the repos are bare). For each match the worker
writes one TSV row: path, blob sha, section header, offset of the match in the body, form, kind, qualifier, window
(450 characters before the match to 400 after, tabs and newlines as spaces) and the match's offset in the window.
Targets and treating decisions are resolved later (notes_build.py), against the citation index.

This file is the evaluation's reader. The model's reader (tools/caselaw2/reader) must never import it or read its
output.
"""
import os, re, subprocess, sys, threading

CREATE_NO_WINDOW = 0x08000000

Q = (r"(?:on\s+other\s+grounds?|on\s+another\s+ground|on\s+(?:a\s+)?different\s+grounds?|on\s+other\s+points?|"
     r"on\s+(?:another|a\s+different)\s+point|on\s+other\s+issues?|on\s+(?:another|a\s+different)\s+issue|"
     r"on\s+unrelated\s+grounds|on\s+separate\s+grounds|in\s+part|in\s+relevant\s+part|in\s+other\s+part|"
     r"in\s+other\s+respects|partially|to\s+the\s+extent\b[^,;()]{0,90}|insofar\s+as\b[^,;()]{0,90}|"
     r"sub\s+silentio|by\s+implication|implicitly|effectively|in\s+effect|expressly|"
     r"on\s+(?:this|that|the\s+latter|the\s+former)\s+point|as\s+to\s+[^,;()]{1,50}?(?=,|\s+by\b|\s+in\b))")
QS = rf"(?:[\s,]*{Q}){{0,3}}"
BY = r",?\s+(?:by|in|as\s+(?:stated|recognized|noted|explained)\s+in)\b"
HAS = r"\b(?:was|were|has\s+(?:since\s+)?been|have\s+(?:since\s+)?been|had\s+(?:since\s+)?been|since\s+been|been)\s+(?:\w+\s+){0,2}?"
CITE_AHEAD = r"(?=\s*(?:\d{1,4}\s+[A-Z][A-Za-z.' ]{0,30}\d|[A-Z][^,;]{0,120}?,\s*\d{1,4}\s+[A-Z]))"
ENACT = (r"(?:an?\s+|the\s+|later\s+|subsequent\s+)?(?:(?:federal|state|amended|new)\s+)?"
         r"(?:statute|statutory\s+amendment|rule|court\s+rule|regulation|constitutional\s+amendment|amendment|"
         r"legislation|legislative\s+(?:action|amendment|enactment)|act\s+of|enactment|ordinance|"
         r"the\s+legislature|congress|[A-Z][\w.]*\s+(?:Act|Code|Rule))")
H = r"(?:\s+(?:in\s+part|on\s+other\s+grounds|and\s+remanded|as\s+moot|in\s+part\s+and\s+remanded|on\s+reh(?:'|’)?g(?:\s+en\s+banc)?|on\s+rehearing(?:\s+en\s+banc)?|en\s+banc))*"

FORMS = [
    # (form, kind, regex)
    ("ovr-by", "overruled", rf"\boverruled{QS}{BY}"),
    ("ovr-has", "overruled", rf"{HAS}overruled\b"),
    ("ovr-paren", "overruled", r"\(\s*overruled\b[^)]{0,60}\)"),
    ("ovr-recog", "overruled", r"\boverruling\s+(?:recognized|noted)\s+(?:by|in)\b|\boverruled[^.;()]{0,40}?as\s+(?:stated|recognized)\s+in\b"),
    ("abr-by", "abrogated", rf"\babrogated{QS}{BY}"),
    ("abr-has", "abrogated", rf"{HAS}abrogated\b"),
    ("abr-recog", "abrogated", r"\babrogation\s+recognized\s+(?:by|in)\b|\b(?:recognized|noted|stated|acknowledged)\s+(?:as|to\s+be|to\s+have\s+been)\s+abrogated\b"),
    ("sup-enact", "supersededByEnactment", rf"\bsuperseded{QS},?\s+by\s+{ENACT}"),
    ("sup-recog", "supersededByEnactment", r"\bsuperseded[^.;()]{0,60}?as\s+(?:stated|recognized|noted)\s+in\b"),
    ("dis-by", "disapproved", rf"\bdisapproved(?:\s+of)?{QS}{BY}"),
    ("dis-has", "disapproved", rf"{HAS}disapproved\b"),
    ("rec-by", "recededFrom", rf"\breceded\s+from{QS}{BY}"),
    ("rec-has", "recededFrom", rf"{HAS}receded\s+from\b"),
    ("vac-hist", "vacated", rf",\s*(?:(?:judgment|opinion|panel\s+opinion)\s+)?vacated{H},?\s+(?:sub\s+nom\.?\s+[^,;]{{1,100}},\s*)?{CITE_AHEAD}"),
    ("vac-by", "vacated", rf"\bvacated{H}\s+by\b"),
    ("vac-enbanc", "vacated", r"\breh(?:'|’)?g\s+en\s+banc\s+granted(?:\s+and)?,?\s+(?:panel\s+)?(?:opinion|judgment)\s+vacated\b"),
    ("rev-hist", "reversed", rf",\s*(?:rev(?:'|’)?d|reversed){H},?\s+(?:sub\s+nom\.?\s+[^,;]{{1,100}},\s*)?{CITE_AHEAD}"),
    ("rev-by", "reversed", r"\b(?:rev(?:'|’)d|reversed)(?:\s+(?:in\s+part|on\s+other\s+grounds))?\s+by\s+(?:the\s+)?(?:\d|[A-Z][a-z]+\s+v\.|Supreme|Court|United)"),
]
RX = re.compile("|".join(f"(?P<f{i}>{rx})" for i, (_, _, rx) in enumerate(FORMS)), re.I)
TRIG = re.compile(r"overrul|abrogat|supersed|disapprov|receded|vacated|rev(?:'|’)d|reversed", re.I)
PRE = ("overrul", "abrogat", "supersed", "disapprov", "receded", "vacated", "rev'd", "rev’d", "reversed")


def parse_body(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            return text[end + 4:]
    return text


def clean(s):
    return s.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def scan(body):
    low = body.lower()
    if not any(p in low for p in PRE):
        return
    heads = None
    seen = -1
    for t in TRIG.finditer(body):
        if t.start() < seen:
            continue
        lo = max(0, t.start() - 70)
        m = RX.search(body, lo, min(len(body), t.end() + 260))
        while m and m.start() < seen:
            m = RX.search(body, m.start() + 1, min(len(body), t.end() + 260))
        if not m or m.start() > t.start():
            continue
        seen = m.end()
        i = int(m.lastgroup[1:])
        form, kind, _ = FORMS[i]
        if heads is None:
            heads = [(h.start(), h.group(1).strip()) for h in re.finditer(r"^## (.+)$", body, re.M)]
        sec = ""
        for hpos, h in heads:
            if hpos <= m.start():
                sec = h
            else:
                break
        w0 = max(0, m.start() - 450)
        yield form, kind, m.start(), m.end(), sec[:60], clean(body[w0:m.end() + 400]), m.start() - w0, m.end() - w0


def main(repo, outdir):
    name = os.path.basename(os.path.normpath(repo))
    os.makedirs(outdir, exist_ok=True)
    tree = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "HEAD", "--", "decisions"], capture_output=True,
                          check=True, creationflags=CREATE_NO_WINDOW).stdout.decode("utf-8")
    items = []
    for line in tree.splitlines():
        meta, path = line.split("\t", 1)
        _, typ, sha = meta.split()
        if typ == "blob" and path.endswith(".md"):
            items.append((sha, path))
    p = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         creationflags=CREATE_NO_WINDOW)

    def feed():
        for sha, _ in items:
            p.stdin.write((sha + "\n").encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    part = os.path.join(outdir, name + ".notes.tsv.part")
    n = rows = 0
    with open(part, "w", encoding="utf-8", newline="\n") as out:
        for sha, path in items:
            header = p.stdout.readline().split()
            size = int(header[2])
            data = p.stdout.read(size)
            p.stdout.read(1)
            body = parse_body(data.decode("utf-8", "replace").replace("\r\n", "\n"))
            for form, kind, a, b, sec, win, wa, wb in scan(body):
                out.write(f"{path}\t{sha}\t{clean(sec)}\t{a}\t{form}\t{kind}\t{wa}\t{wb}\t{win}\n")
                rows += 1
            n += 1
    p.wait()
    os.replace(part, os.path.join(outdir, name + ".notes.tsv"))
    print(name, n, rows, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
