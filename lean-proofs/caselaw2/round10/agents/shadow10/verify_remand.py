"""Independent re-check of cert_remand/history_remand_delta.tsv against DESIGN10 section 4 + D10-5/D10-6/D10-7, reading
every span from the delta's own windows (cert_text_delta.tsv) and the node facts from round9/stage/v9c decisions2.
    python -X utf8 round10/agents/shadow10/verify_remand.py [DIR]
"""
import collections
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "cert_remand")
LOW = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


def lower(s):
    return s.translate(LOW)


def norm(s):
    return s.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def compact(s):
    return re.sub(r"[^a-z0-9]", "", lower(s))


MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december"]
ABBR = {1: ["jan."], 2: ["feb."], 3: ["mar."], 4: ["apr."], 8: ["aug."], 9: ["sept.", "sep."], 10: ["oct."],
        11: ["nov."], 12: ["dec."]}
wins = collections.defaultdict(list)
for line in open(os.path.join(D, "cert_text_delta.tsv"), encoding="utf-8"):
    sha, s0, e0, txt = line.rstrip("\n").split("\t", 3)
    wins[sha].append((int(s0), int(e0), txt))
lines = [l.rstrip("\n").split("\t") for l in open(os.path.join(D, "history_remand_delta.tsv"), encoding="utf-8")]
hist = {}
ids = {p[0] for p in lines}
with open(os.path.join(C2, "round9/stage/v9c/history.tsv"), encoding="utf-8") as f:
    for line in f:
        p = line.split("\t", 3)
        if p[0] in ids:
            hist[p[0]] = (int(p[2]), int(p[1]))   # by, target
want = {int(p[1]) for p in lines} | {n for v in hist.values() for n in v}
dec = {}
with open(os.path.join(C2, "round9/stage/v9c/decisions2.tsv"), "rb") as f:
    for line in f:
        i = line.find(b"\t")
        k = int(line[:i])
        if k in want:
            p = line.decode("utf-8").split("\t")
            dec[k] = (int(p[1]), int(p[2]), p[7])
idx = {}
for path in (os.path.join(C2, "round9/stage/v9c/cite_index.tsv"), os.path.join(D, "cite_index_delta.tsv")):
    for line in open(path, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2:
            idx.setdefault(compact(p[0]), set()).add(int(p[1]))


def span(node, s, e):
    for s0, e0, txt in wins.get(dec[node][2], ()):
        if s0 <= s and e <= e0:
            return txt[s - s0:e - s0]
    return None


def od(d):
    return datetime.date(d // 10000, d // 100 % 100, d % 100).toordinal()


c = collections.Counter()
for p in lines:
    if len(p) != 12:
        c["bad"] += 1
        continue
    rid, b = p[0], int(p[1])
    q0, q1, dk, d0, d1, t0, t1, tie, o0, o1 = int(p[2]), int(p[3]), p[4], int(p[5]), int(p[6]), int(p[7]), int(p[8]), \
        p[9], int(p[10]), int(p[11])
    o, t = hist[rid]
    why = None
    if dec[b][0] != dec[t][0]:
        why = "remandCourt"
    elif not (dec[o][1] and dec[b][1] and 0 <= od(dec[b][1]) - od(dec[o][1]) <= 1826 and dec[t][1] < dec[o][1]):
        why = "remandDate"
    else:
        bs, ts_ = span(b, d0, d1), span(t, t0, t1)
        cd = compact(dk)
        if bs is None or ts_ is None or not (0 < d1 - d0 <= 200 and 0 < t1 - t0 <= 200):
            why = "remandDocket:span"
        elif not (len(cd) >= 4 and re.search(r"\d", cd) and cd in compact(bs) and cd in compact(ts_)):
            why = "remandDocket"
        else:
            q = span(b, q0, q1)
            if q is None or not (0 < q1 - q0 <= 600):
                why = "quote"
            else:
                lq = lower(norm(q))
                if "supreme court" not in lq or not any(x in lq for x in ("vacat", "remand", "in light of",
                                                                         "further consideration")):
                    why = "remandCue"
                else:
                    cq = compact(q)
                    ok = any(k in cq for k, ns in idx.items() if ns == {o} and len(k) >= 6 and k in cq) \
                        if False else False
                    # (a) cite key mapping to O alone
                    for i in range(len(cq)):
                        pass
                    a_ok = False
                    for k, ns in idx.items():
                        if ns == {o} and k and k in cq:
                            a_ok = True
                            break
                    y, m, dd = dec[o][1] // 10000, dec[o][1] // 100 % 100, dec[o][1] % 100
                    c_ok = any(("%s %d, %d" % (f, dd, y)) in lq for f in [MONTHS[m - 1]] + ABBR.get(m, []))
                    c2_ok = False
                    if tie:
                        osp = span(o, o0, o1)
                        ct = compact(tie)
                        c2_ok = osp is not None and 0 < o1 - o0 <= 300 and "in light of" in lower(norm(osp)) and \
                            len(ct) >= 8 and ct in compact(osp) and ct in cq
                    if not (a_ok or c_ok or c2_ok):
                        why = "remandTie"
                    else:
                        c["tie_" + ("a" if a_ok else "") + ("c" if c_ok else "") + ("c2" if c2_ok else "")] += 1
    c[why or "pass"] += 1
print(dict(c))
