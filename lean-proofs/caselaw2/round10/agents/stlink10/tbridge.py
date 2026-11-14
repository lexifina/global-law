"""stlink10 class T (DESIGN10 section 6, claim trialBridge): T's own judgment line affirming the trial judgment.

    python -X utf8 tbridge.py CERT_DIR OUT_DIR

For every certified class-T row (CERT_DIR/history_delta.tsv, rule ...stlink10_t_...): T's own present disposition
(round 6 `dispositions` over T's cache record; the judgment line as round 6 `decide` picks it: the last own
disposition that speaks of a judgment / order / decree or stands alone) must be T's majority / per curiam zone,
<= 600 characters, hold "affirm" and none of "reversed", "reverse", "vacate", "set aside", "remand" (ASCII lower-case
of the normalised quote; trialBridgeT), and T must be dated before D, within 1,826 days, of another court.
Writes OUT_DIR = CERT_DIR's tables restricted to the rows that pass, plus:
  history_tbridge_delta.tsv   id, t_start, t_end   (offsets in T's git-HEAD text)
  history_claim_delta.tsv     id, trialBridge, r7:<rule>
  cert_text_delta.tsv / window_sha_delta.tsv   T's quote windows [t_start-400, t_end+400) added (T's text sha)
and tbridge_stats.json, tbridge_rows.tsv (id, T quote) for review.
"""
import collections, hashlib, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pop  # noqa: E402
from diag import BO, L  # noqa: E402
sys.path.insert(0, os.path.join(L.C2, "round9", "agents", "calpart9"))
import partzone as PZ  # noqa: E402
OKZ = ("majority", "perCuriam", "plurality")

NL = chr(10)
TAB = "\t"
PAD = 400
NEGW = ("reversed", "reverse", "vacate", "set aside", "remand")


def lean_lower(s):
    return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in s)


HEAD_RX = re.compile(r"(?m)^## +(.*)$")


def text_group(Tn):
    """a pseudo cache record from markdown part headings: the end zone (last 3,000 characters) of each majority /
    per curiam part."""
    hs = list(HEAD_RX.finditer(Tn.replace(" ## ", NL + "## ")))
    ends = []
    for k, m in enumerate(hs):
        lab = m.group(1)[:40].lower()
        if "dissent" in lab or "concur" in lab:
            continue
        part = "perCuriam" if "per curiam" in lab else ("majority" if ("majority" in lab or "opinion" in lab) else None)
        if part is None:
            continue
        a = m.start()
        b = hs[k + 1].start() if k + 1 < len(hs) else len(Tn)
        lo = max(a, b - 3000)
        ends.append([lo, Tn[lo:b], part])
    return {"z": {"parts": [], "ends": ends}, "h": [], "cw": []}


def t_line(g):
    disps = BO.dispositions(g)
    if not disps:
        return None, "t_no_disposition"
    pick = len(disps) - 1
    for i in range(len(disps) - 1, -1, -1):
        if BO.SUBJECT.search(disps[i][2]) or len(disps[i][2]) <= 90:
            pick = i
            break
    q0, q1, sent, part, clauses = disps[pick]
    return (q0, q1, part), ""


def main():
    cert, out = sys.argv[1], sys.argv[2]
    rows = {}
    for l in open(os.path.join(cert, "history_delta.tsv"), encoding="utf-8"):
        p = l.rstrip(NL).split(TAB)
        if "stlink10_t_" in p[12]:
            rows[p[0]] = p
    BO.init()
    F = BO.G["F"]
    want = {int(p[1]) for p in rows.values()}
    # shard of each target (intermediate-court shards)
    where = {}
    for s in L.shards():
        tag = os.path.basename(s)[:-len(".jsonl.gz")]
        for r in L.meta_rows(s[:-len(".jsonl.gz")] + ".meta.tsv.gz"):
            if int(r[0]) in want:
                where[int(r[0])] = s
    grp = {}
    by_shard = collections.defaultdict(set)
    for t, s in where.items():
        by_shard[s].add(t)
    for s, ts in by_shard.items():
        for n, g in L.decisions(s):
            if n in ts:
                grp[n] = g
    texts = L.fetch_texts(list(want))
    st = collections.Counter()
    keep, tb, wins, review = {}, [], {}, []
    for i, p in rows.items():
        t, d = int(p[1]), int(p[2])
        if t not in texts:
            st["drop:t_no_text"] += 1
            continue
        if t not in grp:
            # no cache record (the round-6 scan kept none): zones from the text's own part headings
            grp[t] = text_group(L.norm(texts[t][1]))
            st["t_from_headings"] += 1
        if not (int(F.date[t]) < int(F.date[d]) and BO.day(F.date[d]) - BO.day(F.date[t]) <= 1826) or \
                int(F.court[t]) == int(F.court[d]):
            st["drop:t_date_court"] += 1
            continue
        sha, text = texts[t]
        # T's own words only (DESIGN10 section 0.6): the line must lie inside one majority / per curiam / plurality
        # zone of the round-9 part map (calpart9 partzone.zones); otherwise the closing judgment line of those zones
        zs = [zz for zz in PZ.zones(text)[0] if zz[2] in OKZ]
        res, why = t_line(grp[t])
        if res is not None and not any(z0 <= res[0] and res[1] <= z1 for z0, z1, _p in zs):
            st["t_line_outside_own_zone"] += 1
            res, why = None, "t_outside_zone"
        if res is None:
            Tn = L.norm(text)
            ends = [[max(z0, z1 - 3000), Tn[max(z0, z1 - 3000):z1], zp] for z0, z1, zp in zs]
            res, why = t_line({"z": {"parts": [], "ends": ends}, "h": [], "cw": []})
            if res is not None:
                st["t_line_from_zones"] += 1
        if res is None:
            st["drop:" + why] += 1
            continue
        q0, q1, part = res
        if not any(z0 <= q0 and q1 <= z1 for z0, z1, _p in zs):
            st["drop:t_outside_zone_final"] += 1
            continue
        quote = L.norm(text[q0:q1])
        ql = lean_lower(quote)
        if q1 - q0 > 600:
            st["drop:t_quote_long"] += 1
            continue
        if "affirm" not in ql:
            st["drop:t_no_affirm"] += 1
            continue
        if any(w in ql for w in NEGW):
            st["drop:t_negative_word"] += 1
            continue
        keep[i] = p
        tb.append((i, q0, q1))
        s0, e0 = max(0, q0 - PAD), min(len(text), q1 + PAD)
        wins[(sha, s0, e0)] = L.norm(text[s0:e0])
        review.append((i, quote))
        st["rows"] += 1
    os.makedirs(out, exist_ok=True)

    def lines(name):
        pth = os.path.join(cert, name)
        return [l for l in open(pth, encoding="utf-8").read().split(NL) if l] if os.path.exists(pth) else []

    for name in ("history_delta.tsv", "history_anchor_delta.tsv", "cite_index_delta.tsv"):
        ls = lines(name)
        if name.startswith("history"):
            ls = [l for l in ls if l.split(TAB)[0] in keep]
        with open(os.path.join(out, name), "w", encoding="utf-8", newline=NL) as f:
            f.writelines(l + NL for l in ls)
    ct = lines("cert_text_delta.tsv")
    ws = lines("window_sha_delta.tsv")
    have = {tuple(l.split(TAB)[:3]) for l in ct}
    for (sha, s0, e0), w in sorted(wins.items()):
        if (sha, str(s0), str(e0)) in have:
            continue
        ct.append(TAB.join((sha, str(s0), str(e0), w)))
        ws.append(TAB.join((sha, str(s0), str(e0), hashlib.sha1(w.encode("utf-8")).hexdigest(), "corpus")))
    with open(os.path.join(out, "cert_text_delta.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.writelines(l + NL for l in ct)
    with open(os.path.join(out, "window_sha_delta.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.writelines(l + NL for l in ws)
    with open(os.path.join(out, "history_tbridge_delta.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for i, q0, q1 in tb:
            f.write("%s\t%d\t%d\n" % (i, q0, q1))
    with open(os.path.join(out, "history_claim_delta.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for i, p in keep.items():
            f.write("%s\ttrialBridge\t%s\n" % (i, p[12]))
    with open(os.path.join(out, "tbridge_rows.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for i, q in review:
            f.write("%s\t%s\n" % (i, q))
    for name in ("treatments_delta.tsv", "treatment_class_delta.tsv", "joined_delta.tsv"):
        open(os.path.join(out, name), "w").close()
    st["rows_in"] = len(rows)
    json.dump(dict(st), open(os.path.join(out, "tbridge_stats.json"), "w"), indent=1)
    print(dict(st))


if __name__ == "__main__":
    main()
