"""Round 8, agent `multicase`: candidates from the scan (mcscan.py) -> cands.jsonl.gz, stats in cands_stats.json.

    python -X utf8 mccands.py

For every act sentence of scan/*.jsonl.gz:
  OWN  the sentence has a present own-act form of the court (rule MC-OWN below), or not;
  the earlier decisions it names, resolved as the round-7 treatments reader / antecedent agent did:
    - by citation: a citation key in the act sentence (or its predecessor) that the staged v3 cite index maps to one
      node (else graph/cite_index.tsv when it names exactly one node);
    - by name: a decision the opinion cites elsewhere (opinion-of-the-court parts) whose caption words, as printed
      beside that citation, stand as whole words in the act sentence (or its predecessor); a caption word shared by
      two cited decisions names neither; the acting decision's own caption words are dropped.
  A named decision is kept when X != W, date(X) <= date(W), and W's court could have power over X's (same court;
  the Supreme Court over a federal court; same system and a lower tier).
  WHERE: "act" (named in the act sentence) or "prev" (only in the sentence before it).
  base: the (W, X) pair already has an admitted explicit status-changing treatments row in round7/stage/v3
  (certs.tsv verdict ok / okUnverifiedBy).
A candidate is kept when it names >= 2 resolved decisions (act + prev), or >= 1 in the act sentence while the scan
counted >= 3 references there (a list whose other names did not resolve is still worth the row it can give).

MC-OWN (present own act; the class's general form):
  active : "we|this court|the court [adverbs/modals] overrule|disapprove|recede|abrogate|repudiate|disavow"
  passive: "is|are|stand(s) [adverbs] [, inserted phrase,] overruled|disapproved|abrogated|repudiated|disavowed|
            receded from", "must|should|will|shall|can|may [now|therefore|...] be [regarded|considered|deemed|held|
            treated|taken] [as] overruled|...", "are to be (regarded as) overruled"
  minus  : negation / condition right before the verb ("not", "never", "if", "whether", "would", "need not");
           and the verb immediately followed by "by" or "on other grounds" (reports; disqualify_treat covers most).
No answer key is read.
"""
import collections, glob, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
W = os.path.dirname(C2)
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402
C = L.reader_common()
V3 = os.path.join(C2, "round7", "stage", "v3")
OUT3 = os.path.join(C2, "round7", "out", "v3")
NL = chr(10)
STATUS_KINDS = ("overruled", "disapproved", "abrogated", "recededFrom")

V = r"(?:overruled|disapproved|abrogated|repudiated|disavowed|receded\s+from|overturned)"
ADV = r"(?:hereby|now|therefore|accordingly|expressly|also|herein|specifically|necessarily|thus|hence|likewise|" \
      r"each|all|both|severally|so|again|explicitly|formally|today|further|similarly|definitely|distinctly|" \
      r"unequivocally|squarely|necessarily|pro\s+tanto|to\s+that\s+extent|to\s+this\s+extent|in\s+part|partially|" \
      r"partly|wholly|completely|entirely|overruled\s+and|disapproved\s+and|modified\s+and|and|,)"
INS = r"(?:,[^,.;]{1,120},\s*)?"
OWN_PASSIVE = re.compile(
    r"\b(?:is|are|stands?)(?:\s+|(?=,))" + INS + r"(?:" + ADV + r"\s*){0,4}" + INS + V + r"\b|"
    r"\b(?:must|should|will|shall|can|may|ought\s+to)\s+(?:(?:now|therefore|accordingly|hereby|be\s+and\s+(?:is|are)|"
    r",)\s*){0,3}be\s+" + INS + r"(?:(?:" + ADV + r")\s*){0,3}(?:(?:regarded|considered|deemed|held|treated|taken|"
    r"understood|viewed|looked\s+upon|declared)\s+(?:as\s+)?(?:having\s+been\s+|being\s+)?)?" + V + r"\b|"
    r"\bare\s+to\s+be\s+(?:(?:regarded|considered|deemed|treated|taken)\s+as\s+)?" + V + r"\b", re.I)
OWN_ACTIVE = re.compile(
    r"\b(?:we|this\s+court|the\s+court|i)\s*,?\s+(?:(?:now|hereby|therefore|accordingly|expressly|must|do|will|"
    r"shall|should|also|further|today|thus|hence|so|explicitly|formally|unequivocally|necessarily|specifically|"
    r"must\s+and\s+do|are\s+(?:constrained|compelled|obliged|impelled|forced)\s+to|feel\s+(?:compelled|constrained|"
    r"obliged|bound)\s+to|have\s+(?:no\s+)?(?:choice|alternative)\s+but\s+to|have\s+concluded\s+to|"
    r"have\s+decided\s+to|deem\s+it\s+(?:necessary|proper)\s+to|think\s+it\s+(?:necessary|proper|best)\s+to|"
    r"take\s+this\s+opportunity\s+to|choose\s+to|now\s+choose\s+to|elect\s+to|herewith|expressly\s+and|"
    r"specifically\s+and|,)\s*){0,4}(?:overrule|disapprove|recede|abrogate|repudiate|disavow)\b", re.I)
# v2 (01:10): third-person present "this court [now|hereby|...] [, inserted phrase,] overrules|disapproves|..." and
# "we, <inserted phrase>, overrule" (a general form found missing in the h0 diagnosis; counts only, no key row used)
OWN_ACTIVE3 = re.compile(
    r"\b(?:this\s+court|we)\s*(?:,?\s*(?:now|hereby|therefore|accordingly|expressly|today|also|herein)\b)*\s*(?:,[^.;:]{1,160}?,\s*)?" +
    r"(?:(?:now|hereby|therefore|accordingly|expressly|specifically|explicitly|formally)\s+)*"
    r"(?:overrules|disapproves|recedes|abrogates|repudiates|disavows|overrule|disapprove|recede|abrogate|repudiate|"
    r"disavow)\b", re.I)
NEG_BEFORE = re.compile(r"(?:\bnot|n't|\bnever|\bif|\bwhether|\bwould|\bneed\s+not|\bnor|\bunless|\bwithout|"
                        r"\bdecline\w*|\brefus\w*|\breluctan\w*|\bhesita\w*|\burg\w*|\bask\w*|\bargu\w*|"
                        r"\bcontend\w*|\brequest\w*|\binvit\w*|\bsuggest\w*|\bpropos\w*|\bwhy)\W+(?:\w+\W+){0,4}$",
                        re.I)
AFTER_BAD = re.compile(r"^\s*(?:by\b|on\s+other\s+grounds|in\s+part\s+on\s+other\s+grounds|sub\s+silentio)", re.I)


def own_form(s):
    """(form, start, end) of the first MC-OWN match in s, or None."""
    for rx, nm in ((OWN_ACTIVE, "active"), (OWN_PASSIVE, "passive"), (OWN_ACTIVE3, "active3")):
        for m in rx.finditer(s):
            if NEG_BEFORE.search(s[max(0, m.start() - 60):m.start()]) or re.search(r"\bnot\b|n't\b", m.group(0), re.I):
                continue
            if AFTER_BAD.match(s[m.end():m.end() + 40]):
                continue
            return nm, m.start(), m.end()
    return None


def alnum(s):
    return re.sub(r"[^0-9a-z]", "", s.lower())


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def records():
    for p in sorted(glob.glob(os.path.join(HERE, "scan", "*.jsonl.gz"))):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                yield json.loads(line)


def resolver(keys):
    live = {}
    with open(os.path.join(V3, "cite_index.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) >= 2:
                live.setdefault(alnum(p[0]), set()).add(int(p[1]))
    graph = collections.defaultdict(set)
    kb = {k.encode("utf-8") for k in keys}
    with open(os.path.join(W, "graph", "cite_index.tsv"), "rb") as f:
        for raw in f:
            i = raw.find(b"\t")
            if raw[:i] in kb:
                graph[raw[:i].decode("utf-8")].add(int(raw[i + 1:].strip()))
    res = {}
    for k in keys:
        c = alnum(k)
        if c in live:
            v = live[c]
            res[k] = next(iter(v)) if len(v) == 1 else None
        else:
            v = graph.get(k, ())
            res[k] = next(iter(v)) if len(v) == 1 else None
    return res


def names_of(nodes):
    off = L._offsets()
    out = {}
    with open(L.NODES, "rb") as f:
        for n in sorted(nodes):
            f.seek(int(off[n]))
            p = f.readline().decode("utf-8", "replace").rstrip("\r\n").split("\t")
            out[n] = (p[6] if len(p) > 6 else "", p[5] if len(p) > 5 else "")
    return out


def base_pairs():
    ok = set()
    for line in open(os.path.join(OUT3, "certs.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if p[0] == "treatment" and p[2] in ("ok", "okUnverifiedBy"):
            ok.add(p[1])
    pairs = {}
    for line in open(os.path.join(V3, "treatments.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if p[0] in ok and p[7] == "1" and p[4] in STATUS_KINDS:
            pairs.setdefault((int(p[1]), int(p[2])), []).append(p[0])
    return pairs


class Power:
    def __init__(self, F):
        self.F = F

    def ok(self, w, x):
        F = self.F
        if w == x or not F.date[x] or not F.date[w] or F.date[x] > F.date[w]:
            return False
        cw, cx = int(F.court[w]), int(F.court[x])
        if cw == cx:
            return True
        if F.is_scotus(cw):
            return F.system(cx) == 0
        return F.system(cw) == F.system(cx) and F.rank(cx) < F.rank(cw)


TOKEN_RX = re.compile(r"[A-Za-z][A-Za-z'\-]+")


def printed_tokens(name, prefix):
    toks = C.name_tokens(name) | C.short_name_tokens(name)
    pw = set(TOKEN_RX.findall(prefix or ""))
    pr = {t for t in toks if t in pw}
    return pr or toks


def main():
    F = L.Facts()
    P = Power(F)
    keys = set()
    nrec = 0
    for r in records():
        nrec += 1
        for k, _a, _b in r["cites"]:
            keys.add(k)
        for k, _p in r["ocites"]:
            keys.add(k)
    log("records", nrec, "keys", len(keys))
    res = resolver(keys)
    log("resolved", sum(1 for v in res.values() if v is not None))
    pairs = base_pairs()
    log("base admitted explicit status pairs", len(pairs))
    need = set()
    for r in records():
        need.add(r["n"])
        for k, _p in r["ocites"]:
            x = res.get(k)
            if x is not None:
                need.add(x)
        for k, _a, _b in r["cites"]:
            x = res.get(k)
            if x is not None:
                need.add(x)
    NM = names_of(need)
    log("names", len(NM))
    st = collections.Counter()
    out = gzip.open(os.path.join(HERE, "cands.jsonl.gz"), "wt", encoding="utf-8", newline=NL)
    for r in records():
        st["act_sentences"] += 1
        n = r["n"]
        s0, s1 = r["s"]
        p0, p1 = r["p"]
        act = r["act"]
        of = own_form(act)
        if of is None:
            st["not_own"] += 1
            continue
        st["own_" + of[0]] += 1
        own = C.name_tokens(NM.get(n, ("", ""))[0]) | C.short_name_tokens(NM.get(n, ("", ""))[0])
        tg = {}

        def add(x, how, ev, h0, h1):
            where = "act" if h0 >= s0 else "prev"
            cur = tg.get(x)
            if cur is None or (where == "act" and cur["where"] == "prev") or (
                    where == cur["where"] and how == "cite" and cur["how"] == "name"):
                tg[x] = {"t": x, "how": how, "ev": ev, "hit": [h0, h1], "where": where}
        for k, c0, c1 in r["cites"]:
            x = res.get(k)
            if x is None:
                st["cite_unresolved"] += 1
                continue
            if x == n or not P.ok(n, x):
                st["cite_nopower"] += 1
                continue
            add(x, "cite", "cite:" + k, c0, c1)
        seen = {}
        for k, pre in r["ocites"]:
            x = res.get(k)
            if x is None or x in seen or x == n:
                continue
            seen[x] = [t for t in printed_tokens(NM.get(x, ("", ""))[0], pre) if t not in own]
        tok_n = collections.Counter(t for toks in seen.values() for t in set(toks))
        ctx = r["prev"] + " " + act
        c0 = p0 if p1 > p0 else s0
        off_act = len(r["prev"]) + 1
        for x, toks in seen.items():
            if x in tg and tg[x]["where"] == "act":
                continue
            if not P.ok(n, x):
                continue
            toks = [t for t in toks if tok_n[t] == 1]
            if not toks:
                continue
            rx = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in sorted(toks)) + r")\b")
            hits = list(rx.finditer(ctx))
            if not hits:
                continue
            h = hits[-1]
            got = sorted({m.group(0) for m in hits})
            hpos = (s0 + h.start() - off_act) if h.start() >= off_act else (c0 + h.start())
            add(x, "name", "name:" + " ".join(got[:2]), hpos, hpos + len(h.group(0)))
        n_act = sum(1 for v in tg.values() if v["where"] == "act")
        if len(tg) < 2 and not (n_act >= 1 and r["nref"] >= 3):
            st["lt2_resolved"] += 1
            continue
        st["cands"] += 1
        for v in tg.values():
            nm, cite = NM.get(v["t"], ("", ""))
            v["name"], v["cite"], v["date"], v["court"] = nm, cite, int(F.date[v["t"]]), int(F.court[v["t"]])
            v["base"] = pairs.get((n, v["t"]), [])
        nb = sum(1 for v in tg.values() if v["base"])
        st["targets"] += len(tg)
        st["targets_base"] += nb
        if nb == len(tg):
            st["cands_all_base"] += 1
        for f in r["flags"]:
            st["flag_" + f] += 1
        rec = {"id": "%d:%d" % (n, s0), "n": n, "s": [s0, s1], "p": [p0, p1], "act": act, "prev": r["prev"],
               "part": r["part"], "flags": r["flags"], "hw": r["hw"], "own": list(of), "nref": r["nref"],
               "nref_prev": r["nref_prev"],
               "by_name": NM.get(n, ("", ""))[0], "by_cite": NM.get(n, ("", ""))[1], "by_date": int(F.date[n]),
               "by_court": int(F.court[n]), "by_system": F.system(int(F.court[n])),
               "targets": sorted(tg.values(), key=lambda v: v["hit"][0])}
        out.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + NL)
    out.close()
    with open(os.path.join(HERE, "cands_stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(st), f, indent=1)
    log(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
