"""stlink11: identity-tie lines (DESIGN11 section 5.2, D11-5) for certified U2 rows, with a Python pre-check of the
exact section-5.2 conditions. One line per row id (first passing form in the order docket, cite, date).

    python -X utf8 ident.py DELTA_DIR OUT_DIR
      -> OUT_DIR/history_identity_delta.tsv (7 columns: id, form, token, d_start, d_end, t_start, t_end),
         cert_text_delta.tsv, window_sha_delta.tsv (windows [s-400, e+400) of each span, norm'd), precheck.tsv, stats

Spans are character offsets of the git-HEAD text (CRLF -> LF), each non-empty and <= 200 characters.
docket / cite: compact(token) >= 4 chars with a digit, substring of compact(D span) and compact(T span).
date: token = decisions2 date of T (yyyymmdd); both lower-cased spans hold "<month> <d>, <yyyy>" (full month) or
"<abbr> <d>, <yyyy>" (remand_months_abbr), day without a leading zero.
"""
import collections, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from diag import L  # noqa: E402
import ties  # noqa: E402

sys.path.insert(0, os.path.join(L.C2, "round6", "history"))
import certify6 as C6  # noqa: E402

NL, TAB = chr(10), chr(9)
PAD = 400
BODY_ONLY = os.environ.get("IDENT_BODY_ONLY", "1") == "1"   # D's span in D's opinion text, not its front matter
SPAN_MAX = 200
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december"]
ABBR = [["jan."], ["feb."], ["mar."], ["apr."], [], [], [], ["aug."], ["sept.", "sep."], ["oct."], ["nov."], ["dec."]]
DEC2 = os.path.join(L.C2, "round10", "stage", "v10d", "decisions2.tsv")


def compact(s):
    return C6.compact(s)


def lowtext(s):
    return C6.lower(C6.norm(s))


def ok_tok(tok, dspan, tspan):
    c = compact(tok)
    return len(c) >= 4 and re.search(r"\d", c) is not None and c in compact(dspan) and c in compact(tspan)


def date_forms(d):
    y, m, dd = d // 10000, d // 100 % 100, d % 100
    if not (1 <= m <= 12 and 1 <= dd <= 31):
        return []
    out = ["%s %d, %d" % (MONTHS[m - 1], dd, y)]
    out += ["%s %d, %d" % (a, dd, y) for a in ABBR[m - 1]]
    return out


def find_span(text, needle_rx, prefer_after=0):
    """first match of a compiled regex; -> (s, e) or None (span <= SPAN_MAX)."""
    for m in needle_rx.finditer(text, prefer_after):
        if 0 < m.end() - m.start() <= SPAN_MAX:
            return m.start(), m.end()
    for m in needle_rx.finditer(text, 0, prefer_after):
        if 0 < m.end() - m.start() <= SPAN_MAX:
            return m.start(), m.end()
    return None


def flex_rx(tok):
    """the token's characters in order, any non-alphanumeric run between them (compact-equal printing)."""
    al = [ch for ch in tok if ch.isalnum()]
    if not al:
        return None
    body = r"[^A-Za-z0-9]{0,3}".join(re.escape(ch) for ch in al)
    return re.compile(r"(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])", re.I)


def front_end(text):
    m = ties.FRONT.match(text)
    return m.end() if m else 0


def try_docket(D, T, dfront, tfront):
    toks = []
    dk = tfront.get("docket")
    if isinstance(dk, list):
        dk = "; ".join(str(x) for x in dk)
    for piece in re.split(r"[;,&]|\band\b", str(dk or "")):
        p = re.sub(r"^\s*(?:nos?\.?|numbers?|docket|case)\s*", "", piece.strip(), flags=re.I).strip()
        c = compact(p)
        if len(c) >= 4 and re.search(r"\d", c):
            toks.append(p)
    for tok in toks:
        rx = flex_rx(tok)
        if rx is None:
            continue
        tsp = find_span(T, rx)
        if tsp is None:
            continue
        # D: outside D's own front-matter docket line first, then anywhere (the case kept its number)
        own = re.search(r"^docket:.*$", D[:front_end(D)], re.M)
        dsp = None
        for m in rx.finditer(D):
            if own and own.start() <= m.start() < own.end():
                continue
            dsp = (m.start(), m.end())
            break
        if dsp is not None and dsp[0] < front_end(D) and BODY_ONLY:
            dsp = None
        if dsp is None and own and not BODY_ONLY:
            m = rx.search(D, own.start(), own.end())
            if m and re.search(r"[a-z]", compact(tok)) or (m and len(compact(tok)) >= 6):
                dsp = (m.start(), m.end())
        if dsp and ok_tok(tok, D[dsp[0]:dsp[1]], T[tsp[0]:tsp[1]]):
            return tok, dsp, tsp
    return None


def try_cite(D, T, tcites):
    for c in tcites:
        rx = flex_rx(c)
        if rx is None:
            continue
        tsp = find_span(T, rx)
        dsp = find_span(D, rx, front_end(D))
        if dsp and dsp[0] < front_end(D) and BODY_ONLY:
            dsp = None
        if tsp and dsp and ok_tok(c, D[dsp[0]:dsp[1]], T[tsp[0]:tsp[1]]):
            return c, dsp, tsp
    return None


def try_date(D, T, tdate):
    for f in date_forms(tdate):
        rx = re.compile(r"(?<![a-z0-9])" + re.escape(f) + r"(?![0-9])")
        dl, tl = lowtext(D), lowtext(T)
        dsp, tsp = find_span(dl, rx, front_end(D)), find_span(tl, rx)
        if dsp and dsp[0] < front_end(D) and BODY_ONLY:
            dsp = None
        if dsp and tsp:
            return str(tdate), dsp, tsp
    return None


def main():
    delta, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    rows = []
    for l in open(os.path.join(delta, "history_delta.tsv"), encoding="utf-8"):
        p = l.rstrip(NL).split(TAB)
        rows.append((p[0], int(p[2]), int(p[1])))   # id, by, target
    want = {n for _i, b, t in rows for n in (b, t)}
    dec = {}
    with open(DEC2, encoding="utf-8") as f:
        for k, line in enumerate(f):
            if k in want:
                q = line.rstrip(NL).split(TAB)
                dec[k] = (int(q[2] or 0), q[7])
    texts = L.fetch_texts(sorted(want))
    st = collections.Counter()
    lines, wins, pre = [], {}, []
    for rid, b, t in rows:
        if b not in texts or t not in texts:
            st["no_text"] += 1
            continue
        D, T = texts[b][1], texts[t][1]
        if texts[b][0] != dec[b][1] or texts[t][0] != dec[t][1]:
            st["sha_mismatch"] += 1
            continue
        dfront, tfront = ties.parse(D)["front"], ties.parse(T)["front"]
        tcites = [c for c in L.node_row(t)[5].split("|") if c]
        got = None
        res = {}
        for form, fn in (("docket", lambda: try_docket(D, T, dfront, tfront)), ("cite", lambda: try_cite(D, T, tcites)),
                         ("date", lambda: try_date(D, T, dec[t][0]))):
            r = fn()
            res[form] = bool(r)
            if r:
                st["pass:" + form] += 1
                if got is None:
                    got = (form,) + r
        pre.append((rid, ",".join(f for f in ("docket", "cite", "date") if res[f]) or "-"))
        if got is None:
            st["no_form"] += 1
            continue
        form, tok, (d0, d1), (t0, t1) = got
        st["line:" + form] += 1
        lines.append((rid, form, tok.replace(TAB, " "), d0, d1, t0, t1))
        for node, s, e in ((b, d0, d1), (t, t0, t1)):
            tx = texts[node][1]
            s0, e0 = max(0, s - PAD), min(len(tx), e + PAD)
            wins[(dec[node][1], s0, e0)] = C6.norm(tx[s0:e0])

    def write(name, items):
        with open(os.path.join(out, name), "w", encoding="utf-8", newline=NL) as f:
            for it in items:
                f.write(TAB.join(map(str, it)) + NL)

    write("history_identity_delta.tsv", lines)
    wk = sorted(wins)
    write("cert_text_delta.tsv", ((s, a, e, wins[(s, a, e)]) for s, a, e in wk))
    write("window_sha_delta.tsv", ((s, a, e, hashlib.sha1(wins[(s, a, e)].encode("utf-8")).hexdigest(), "corpus")
                                   for s, a, e in wk))
    write("precheck.tsv", pre)
    st["rows"] = len(rows)
    st["lines"] = len(lines)
    json.dump(dict(sorted(st.items())), open(os.path.join(out, "stats.json"), "w"), indent=1)
    print(dict(sorted(st.items())))


if __name__ == "__main__":
    main()
