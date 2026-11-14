"""fjc11: per-row identity features of the N linker's rows (corpus only, no key).

    python -X utf8 fjc11_feat.py rows_n1.jsonl work/feat_n1.tsv

For each row (acting appeal D, district decision J):
  form / ties          from the row note (h, x, s; H K U T)
  jdock                J's docket (district meta), normalised key (court, year, serial) or (court, digits)
  sib_before / sib_after_lt_d
                       other district decisions of the same court + docket key dated before J / after J and on or
                       before D's date (later sibling = a later ruling of the same docket the appeal may review)
  latest               1 when J is the latest decision of its docket key dated on or before D (no later sibling)
  named                does D name the ruling under review: dates printed in an "appeal(ed) from ..." /
                       "judgment|order|decree entered|dated|filed ..." phrase:  J = J's date (+-3 days),
                       later = a date after J (and before D), earlier = only dates before J, none
  nruled               ruling words of D's "appeal from" phrase (summary judgment, dismissal, ...) vs J's opening
  consol               D is a consolidated / multi-docket appeal (several appellate docket numbers, or "consolidated")
"""
import collections, datetime, glob, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

NL = chr(10)
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december"]
MON_RX = r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?"
DATE_RX = re.compile(MON_RX + r"\s+(\d{1,2}),?\s+(\d{4})", re.I)
APPEAL_RX = re.compile(
    r"(?:appeal(?:s|ed|ing)?|appellants?\s+(?:seeks?|challenges?)|review)\s+(?:is\s+|are\s+|was\s+)?(?:taken\s+)?"
    r"(?:from|of)\s+(?:an?|the|two|several|three)\s+[^.;]{0,260}", re.I)
ENTERED_RX = re.compile(r"(?:judgment|order|decree|opinion|ruling|decision|memorandum)s?\b[^.;]{0,80}?"
                        r"\b(?:entered|dated|filed|issued|rendered|signed)\s+(?:on\s+)?" + MON_RX + r"\s+\d{1,2},?\s+\d{4}",
                        re.I)
DOCKET_NUM = re.compile(r"(\d{2,4})\s*[-–:]?\s*(?:[A-Za-z]{1,6}\.?\s*[-–]?\s*)?(\d{2,6})")
RULINGS = [("sj", r"summary\s+judgment"), ("dismiss", r"dismiss"), ("inj", r"injunct"),
           ("conv", r"convict|sentenc|guilty"), ("habeas", r"habeas"), ("fees", r"attorney'?s?['’]?\s+fees|costs|sanction"),
           ("class", r"class\s+certif"), ("remand", r"motion\s+to\s+remand"), ("jmol", r"judgment\s+as\s+a\s+matter|n\.o\.v|directed\s+verdict"),
           ("newtrial", r"new\s+trial"), ("contempt", r"contempt"), ("bankr", r"bankrupt"), ("arbit", r"arbitrat"),
           ("verdict", r"jury\s+verdict|verdict"), ("bench", r"bench\s+trial|findings\s+of\s+fact")]
RULINGS = [(k, re.compile(v, re.I)) for k, v in RULINGS]


def mon(s):
    s = s.lower().rstrip(".")
    for i, m in enumerate(MONTHS):
        if m.startswith(s[:3]):
            return i + 1
    return 0


def dates_in(s):
    out = []
    for m in DATE_RX.finditer(s):
        mo, d, y = mon(m.group(1)), int(m.group(2)), int(m.group(3))
        if mo and 1 <= d <= 31 and 1700 < y < 2100:
            out.append(y * 10000 + mo * 100 + d)
    return out


def day(x):
    try:
        return datetime.date(x // 10000, max(1, (x // 100) % 100), max(1, x % 100)).toordinal()
    except ValueError:
        return datetime.date(x // 10000, 1, 1).toordinal()


def dkey(court, dk):
    m = DOCKET_NUM.search(dk or "")
    if m:
        return (court, m.group(1).lstrip("0") or "0", m.group(2).lstrip("0") or "0")
    d = re.sub(r"\D", "", dk or "")
    if len(d) >= 3:
        return (court, d)
    return None


def district_index():
    idx = collections.defaultdict(list)
    meta = {}
    for q in sorted(glob.glob(os.path.join(L.CACHE, "*.meta.tsv.gz"))):
        b = os.path.basename(q)
        if "district" not in b:
            continue
        with gzip.open(q, "rt", encoding="utf-8") as f:
            for line in f:
                p = line.rstrip(NL).split("\t")
                n, date, court, dk = int(p[0]), int(p[3] or 0), p[4], p[5]
                meta[n] = (date, court, dk, p[7])
                k = dkey(court, dk)
                if k:
                    idx[k].append((date, n))
    return idx, meta


def ruling_words(s):
    return {k for k, rx in RULINGS if rx.search(s)}


def main():
    src, out = sys.argv[1], sys.argv[2]
    rows = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
    idx, meta = district_index()
    dmeta = {}
    for q in sorted(glob.glob(os.path.join(L.CACHE, "*.meta.tsv.gz"))):
        if "district" in os.path.basename(q):
            continue
        with gzip.open(q, "rt", encoding="utf-8") as f:
            for line in f:
                p = line.rstrip(NL).split("\t")
                dmeta[int(p[0])] = (int(p[3] or 0), p[4], p[5], p[7])
    need = set()
    for r in rows:
        need.add(r["by"])
        need.add(r["target"])
    texts = L.fetch_texts(sorted(need))
    with open(out, "w", encoding="utf-8", newline=NL) as fo:
        fo.write("\t".join(["by", "target", "form", "ties", "kind", "scope", "ddate", "jdate", "jdock", "ddock",
                            "sib_before", "sib_after_lt_d", "latest", "named", "named_dates", "nruled", "jruled",
                            "consol", "flags", "ev"]) + NL)
        for r in rows:
            n, j = r["by"], r["target"]
            note = r["note"]
            form = r["rule"].split("_")[-1]
            ties = note.split("ties=")[1].split()[0]
            ev = note.split("ties=")[1][len(ties):].strip()
            dd = dmeta.get(n, (0, "", "", ""))
            jd = meta.get(j, (0, "", "", ""))
            ddate, jdate = dd[0], jd[0]
            k = dkey(jd[1], jd[2])
            sb = sa = 0
            if k:
                for dt, m in idx[k]:
                    if m == j:
                        continue
                    if dt < jdate:
                        sb += 1
                    elif jdate < dt <= ddate:
                        sa += 1
            latest = "-" if not k else ("1" if sa == 0 else "0")
            T = L.norm(texts.get(n, ("", ""))[1])
            TJ = texts.get(j, ("", ""))[1]
            ph = [m.group(0) for m in APPEAL_RX.finditer(T)] + [m.group(0) for m in ENTERED_RX.finditer(T)]
            nd = sorted({x for p in ph for x in dates_in(p) if x <= ddate})
            if not nd:
                named = "none"
            elif any(day(x) - day(jdate) > 30 for x in nd):
                named = "later"
            elif any(abs(day(x) - day(jdate)) <= 3 for x in nd):
                named = "J"
            elif any(x > jdate for x in nd):
                named = "near"
            else:
                named = "earlier"
            ar = ruling_words(" ".join(m.group(0) for m in APPEAL_RX.finditer(T))[:3000])
            body = TJ
            kk = body.find("\n---", 4)
            if kk > 0:
                body = body[kk + 4:]
            jr = ruling_words(body[:4000] + " " + body[-3000:])
            consol = "1" if len(re.findall(r"\d[\d-]*\d{2}", dd[2])) >= 2 else "0"
            flags = note.split("flags=")[1].split()[0] if "flags=" in note else "-"
            fo.write("\t".join(str(x) for x in [n, j, form, ties, r["kind"], r["scope"], ddate, jdate, jd[2][:40],
                                                dd[2][:40], sb, sa, latest, named, ",".join(map(str, nd[:6])),
                                                ",".join(sorted(ar)), ",".join(sorted(jr)), consol, flags,
                                                ev.replace("\t", " ")[:120]]) + NL)
    print("rows", len(rows))


if __name__ == "__main__":
    main()
