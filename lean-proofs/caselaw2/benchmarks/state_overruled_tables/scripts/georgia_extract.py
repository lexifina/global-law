"""Georgia 1922 table (casesingeorgiar00appegoog): two-column table rebuilt from the djvu.xml line coordinates.

    python -I georgia_extract.py <lines.tsv> <out_entries.tsv>

Left column: "vol/page(headnote)" of the case treated (Ga. Reports; "vol—page" = Ga. App. Reports).
Right column: "Overruled. 10/558", "Criticised. 137/8", "Changed by §4175. 114/757" ...
A right line belongs to the nearest left entry whose top is at or above it (tolerance 60 px). Right lines above the
first left entry of a leaf are a continuation of the previous leaf's last entry if they do not start with a word,
else an entry whose left cite the OCR lost (kept with left_raw = '?').
Output (one row per (entry, labelled segment)):
  leaf, entry_no, left_raw, left_key, label, label_class, cites (; separated keys), segment_text, entry_text
label_class: overruled | overruled_partial | overruled_qualified (practically/virtually/in effect) | disapproved |
             doubted | questioned | limited | criticised | modified | other
"""
import re
import sys

LEFT_RX = re.compile(r"^\s*([0-9lIi!]{1,3})\s*(/|\s*[—–-]+\s*)\s*([0-9lIiOo]{1,4})\s*(\([^)]*\)?)?")
CITE_RX = re.compile(r"(?<![\d§/-])(\d{1,3})\s*(/|\s*[—–]+\s*\x22?\s*|\s*-\s*)(\d{1,4})(?:-\d{1,4})?(?:\(\d[\d,\s]*\))?")
WORDS_RX = re.compile(r"[A-Za-z][A-Za-z'’]*(?:[ ,]+[A-Za-z][A-Za-z'’]*)*")


def fixnum(s):
    return s.replace("l", "1").replace("I", "1").replace("i", "1").replace("!", "1").replace("O", "0").replace("o", "0")


def key_of(vol, sep, page):
    court = "ga" if sep.strip() == "/" else "gaapp"  # "—", "-": Ga. App.
    return "%d %s %d" % (int(fixnum(vol)), court, int(fixnum(page)))


def classify(label):
    l = label.lower()
    if re.search(r"o[vt]err?u[l1]|verrul", l):
        if re.search(r"practically|virtually|in effect|impliedly|substantially|seemingly|apparently|not\b", l):
            return "overruled_qualified"
        if re.search(r"in part|partly|partially|so far|to the extent|pro tanto", l):
            return "overruled_partial"
        return "overruled"
    for k, c in (("disapprov", "disapproved"), ("doubt", "doubted"), ("question", "questioned"),
                 ("limit", "limited"), ("restrict", "limited"), ("criticis", "criticised"),
                 ("modif", "modified"), ("denied", "denied"), ("receded", "recededFrom")):
        if k in l:
            return c
    return "other"


def segments(text):
    """Split the right-column text into (label, cites) segments."""
    out = []
    pos = 0
    marks = []
    for m in WORDS_RX.finditer(text):
        w = m.group(0)
        if len(w) < 3 and w not in ("So",):
            continue
        marks.append(m)
    if not marks:
        return [("", [key_of(*c.groups()[:3]) for c in CITE_RX.finditer(text)])]
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        seg = text[m.end():end]
        seg_cites = []
        for c in CITE_RX.finditer(seg):
            if seg[max(0, c.start() - 1):c.start()].endswith("§"):
                continue
            seg_cites.append(key_of(c.group(1), c.group(2), c.group(3)))
            # "17/538, 630": a further page of the same volume
            rest = seg[c.end():]
            while True:
                more = re.match(r",\s*(\d{1,4})(?:\(\d[\d,\s]*\))?(?!\s*[/—–\d])", rest)
                if not more:
                    break
                seg_cites.append(key_of(c.group(1), c.group(2), more.group(1)))
                rest = rest[more.end():]
        out.append((m.group(0), seg_cites, text[m.start():end].strip()))
    # a pre-label cite run (rare) is ignored
    _ = pos
    return out


def main(src, dst):
    leaves = {}
    with open(src, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            leaf, lno, x0, top, x1, bot = (int(v) for v in p[:6])
            leaves.setdefault(leaf, []).append((top, x0, x1, bot, p[6]))
    entries = []  # (leaf, left_raw, [right texts])
    for leaf in sorted(leaves):
        ls = [l for l in leaves[leaf] if "Digitized" not in l[4]]
        if len(ls) < 3:
            continue
        lefts, rights = [], []
        for top, x0, x1, bot, t in ls:
            m = LEFT_RX.match(t)
            if m and x0 < 900:
                rest = t[m.end():].strip()
                lefts.append([top, t[:m.end()].strip(), m])
                if rest:
                    rights.append((top, rest))
            elif x0 >= 900 and not re.fullmatch(r"\(?[A-Z0-9]{1,3}\)?|\(\w+", t.strip()):
                rights.append((top, t))
        if not lefts:
            continue
        lefts.sort()
        cur = {id(l): [] for l in lefts}
        orphan_cont, orphan_new = [], []
        for top, t in sorted(rights):
            owner = None
            for l in lefts:
                if l[0] <= top + 60:
                    owner = l
            if owner is None:
                if re.match(r"\s*[A-Za-z§]", t) and not re.match(r"\s*\d", t):
                    orphan_new.append(t)
                else:
                    orphan_cont.append(t)
            else:
                cur[id(owner)].append(t)
        if orphan_cont and entries:
            entries[-1][2].extend(orphan_cont)
        if orphan_new:
            # a right-column entry whose left cite was lost (or, if it does not start with a keyword, a continuation)
            if entries and not re.match(r"(?i)\s*(overrul|criticis|explain|modif|disapprov|chang|doubt|limit|restrict|"
                                        r"obiter|question|followed|approv|distinguish|see|but|reason|doctrine|dictum|"
                                        r"language|practically|repealed|superseded|abrogat|denied)", orphan_new[0]):
                entries[-1][2].extend(orphan_new)
            else:
                entries.append([leaf, "?", orphan_new, None])
        for l in lefts:
            entries.append([leaf, l[1], cur[id(l)], l[2]])
    n = 0
    with open(dst, "w", encoding="utf-8", newline="\n") as o:
        o.write("leaf\tentry_no\tleft_raw\tleft_key\tlabel\tlabel_class\tcites\tsegment_text\tentry_text\n")
        for i, (leaf, lraw, rts, m) in enumerate(entries):
            lkey = key_of(m.group(1), m.group(2), m.group(3)) if m else "?"
            text = " ".join(rts)
            for seg in segments(text):
                if len(seg) == 2:
                    lab, cites, st = seg[0], seg[1], text
                else:
                    lab, cites, st = seg
                o.write("\t".join([str(leaf), str(i), lraw, lkey, lab, classify(lab), ";".join(cites), st, text]) + "\n")
                n += 1
    print("entries", len(entries), "segments", n)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
