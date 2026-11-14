"""Round 8 ownact: port the unread round-3 own-act queue (work/round3/queue) to round-8 packs.

    python -X utf8 round8/agents/ownact/port8.py [--size 80] [--procs 10]

Steps (no answer key is read; inputs are the round-3 items, round-3 reader answers (only to know which items were
read), the v3 stage tables and Lean certs, the reference power engine):
 1. unread = items in work/round3/queue/res whose id has no round-3 answer (packs/ans_*.jsonl, ans_142.partial).
 2. re-anchor: the acting text is read from git HEAD (r6lib.fetch_texts: UTF-8, CRLF -> LF); the FOCUS sentence and
    every candidate's hit must be found in it (same offsets when the text is unchanged, else the nearest exact
    occurrence of the item's own string); items whose focus cannot be found are dropped (counted).
 3. per candidate: power = reference can_change(W, X) ("same" for the same court), admitted = the (W, X) pair has a
    v3 treatments row of a negative kind whose Lean result_all is ok.
 4. lists: low_admitted (every candidate with power yes/same already has an admitted negative row),
    low_nopower (no candidate with power yes/same/unknown); the rest is queued, ordered by expected yield:
    power yes/same before unknown, then the round-3 certified rate of the item's pattern (yield_r3.json, levels read),
    then a fixed hash.
 5. packs8/pack_<nnn>.md (rendered with the focus between ⟦ ⟧ and [Tk] marks after each candidate's hit), items8.jsonl.gz,
    index.tsv (id, pack, priority, pattern, rate, system, decade), low_*.tsv, port_stats.json.
"""
import argparse
import collections
import glob
import gzip
import json
import os
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
Q = os.path.join(C2, "work", "round3", "queue")
V3 = os.path.join(C2, "round7", "stage", "v3")
V3OUT = os.path.join(C2, "round7", "out", "v3")
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

NL = "\n"
NEG = {"overruled", "disapproved", "recededFrom", "abrogated", "supersededByEnactment", "limited", "questioned",
       "criticized", "declinedToFollow"}


def answered_ids():
    ids = set()
    for fn in glob.glob(os.path.join(Q, "packs", "ans_*.jsonl")) + glob.glob(os.path.join(Q, "packs", "ans_*.partial")):
        for line in open(fn, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                ids.add(str(json.loads(line)["id"]))
            except ValueError:
                pass
    return ids


def admitted_pairs():
    ok = set()
    with open(os.path.join(V3OUT, "certs.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[0] == "treatment" and p[2].startswith("ok"):
                ok.add(p[1])
    pairs = set()
    with open(os.path.join(V3, "treatments.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) > 4 and p[0] in ok and p[4] in NEG:
                pairs.add((int(p[1]), int(p[2])))
    return pairs


def systems():
    s = {}
    with open(os.path.join(V3, "courts2.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[0].lstrip("-").isdigit():
                s[int(p[0])] = int(p[4]) if p[4].lstrip("-").isdigit() else -1
    return s


def find_near(text, s, pos):
    """Nearest exact occurrence of s in text to pos (or -1)."""
    if not s:
        return -1
    best, i = -1, text.find(s)
    while i >= 0:
        if best < 0 or abs(i - pos) < abs(best - pos):
            best = i
        i = text.find(s, i + 1)
    return best


def render(it, k_view=900):
    """One pack item. Window = the item's local window clipped to <= k_view chars before the focus and 400 after."""
    t = it["_text"]
    s0, s1 = it["s0"], it["s1"]
    a = max(it["lw0"], s0 - k_view)
    b = min(it["lw1"], s1 + 400)
    a = min(a, s0)
    b = max(b, s1)
    marks = []  # (pos, str)
    for k, x in enumerate(it["targets"]):
        h = x.get("hit")
        if h and a <= h[1] <= b and not (s0 < h[1] < s1 and False):
            marks.append((h[1], "[T%d]" % (k + 1)))
    marks.append((s0, "⟦"))
    marks.append((s1, "⟧"))
    marks.sort(key=lambda m: (m[0], 0 if m[1] == "⟧" else 1))
    out, pos = [], a
    for p, m in marks:
        if p < a or p > b:
            continue
        out.append(t[pos:p])
        out.append(m)
        pos = p
    out.append(t[pos:b])
    win = L.norm("".join(out))
    by = it["by"]
    lines = ["### ITEM %s" % it["id"],
             "ACTING: %s, %s (%s, %s); opinion part: %s; section: %s" % (
                 by["name"], by.get("cite", ""), by["court"], by["year"], it["part"].rstrip("~"), it.get("sec", "")),
             "TARGETS:"]
    for k, x in enumerate(it["targets"]):
        ev = x.get("ev", "")
        how = ('cite "%s"' % ev[5:]) if ev.startswith("cite:") else ('name "%s"' % ev[5:])
        where = "in act" if x.get("where") == "act" else ("before (gap %d)" % x["gap"] if x.get("where") == "before"
                                                             else x.get("where", "?"))
        lines.append("  T%d: %s - %s, %s - %s - named by %s - %s" % (
            k + 1, x["name"], x["court"], x["year"], x.get("cite", ""), how, where))
    lines.append("WINDOW:")
    lines.append(("... " if a > 0 else "") + win + (" ..." if b < len(t) else ""))
    lines.append("FOCUS:")
    lines.append(L.norm(t[s0:s1]))
    return NL.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=80)
    a = ap.parse_args()
    st = collections.Counter()
    read = answered_ids()
    st["round3_answered"] = len(read)
    items = []
    for fn in sorted(glob.glob(os.path.join(Q, "res", "*.items.jsonl.gz"))):
        repo = os.path.basename(fn)[:-len(".items.jsonl.gz")]
        for line in gzip.open(fn, "rt", encoding="utf-8"):
            it = json.loads(line)
            st["res_items"] += 1
            if it["id"] in read:
                continue
            it["repo"] = repo
            items.append(it)
    st["unread"] = len(items)
    print("unread", len(items), flush=True)
    # texts
    nodes = sorted({it["n"] for it in items})
    texts = {}
    for i in range(0, len(nodes), 1500):
        texts.update(L.fetch_texts(nodes[i:i + 1500]))
        print("texts", len(texts), "/", len(nodes), flush=True)
    keep = []
    for it in items:
        sha, t = texts.get(it["n"], (None, None))
        if t is None:
            st["drop_no_text"] += 1
            continue
        w = it["w"]
        focus = w[it["s0"] - it["w0"]:it["s1"] - it["w0"]]
        if t[it["s0"]:it["s1"]] == focus:
            st["anchor_same"] += 1
            d = 0
        else:
            p = find_near(t, focus, it["s0"])
            if p < 0:
                p = find_near(L.norm(t), L.norm(focus), it["s0"])
            if p < 0:
                st["drop_focus_not_found"] += 1
                continue
            d = p - it["s0"]
            st["anchor_moved"] += 1
        for k in ("s0", "s1", "lw0", "lw1", "w0", "w1"):
            it[k] = max(0, min(len(t), it[k] + d))
        it["sha_head"] = sha
        # candidate hits: the evidence string near the recorded position
        for x in it["targets"]:
            at = x.get("at", -1) + d
            ev = x.get("ev", "")
            hit = None
            if ev.startswith("name:"):
                tok = ev[5:].split(" ")[0]
                p = find_near(t, tok, at)
                if p >= 0 and abs(p - at) < 600:
                    hit = [p, p + len(tok)]
            if hit is None and 0 <= at < len(t):
                # citation: mark the end of the citation-like run starting at `at`
                e = at
                while e < len(t) and e - at < 40 and t[e] not in ",;)(" + NL:
                    e += 1
                hit = [at, e]
            x["hit"] = hit
            if hit is None:
                x["where"] = "?"
            elif it["s0"] <= hit[0] < it["s1"]:
                x["where"] = "act"
            elif hit[1] <= it["s0"]:
                x["where"] = "before"
                x["gap"] = it["s0"] - hit[1]
            else:
                x["where"] = "after"
        it["_text"] = t
        keep.append(it)
    st["anchored"] = len(keep)
    print("anchored", len(keep), flush=True)
    # power + admitted pairs
    sys.path.insert(0, os.path.join(C2, "round5", "tests"))
    import common as TC  # noqa: E402
    E, _pr, _meta = TC.lite_engine(V3)
    D = E.D
    pairs = admitted_pairs()
    sysm = systems()
    st["v3_admitted_neg_pairs"] = len(pairs)
    yr = json.load(open(os.path.join(HERE, "yield_r3.json"), encoding="utf-8"))
    prate = collections.defaultdict(lambda: [0, 0])
    for k, v in yr.items():
        lvl, tier, pat = k.split("|")
        prate[pat][0] += v["cert"]
        prate[pat][1] += v["read"]
    rate = {p: (c + 0.5) / (n + 4) for p, (c, n) in prate.items()}
    queued, low_adm, low_nop = [], [], []
    for it in keep:
        w = it["n"]
        pw = []
        for x in it["targets"]:
            xn = x["node"]
            if D.has(w) and D.has(xn):
                if D.court[w] == D.court[xn]:
                    v = "same"
                else:
                    v = E.can_change(w, xn, "unknown")[0]
            else:
                v = "unknown"
            x["power"] = v
            x["admitted"] = (w, xn) in pairs
            pw.append(v)
        live = [x for x in it["targets"] if x["power"] in ("yes", "same", "unknown")]
        strong = [x for x in live if x["power"] in ("yes", "same")]
        pat = it["why"].split(":")[1] if it["why"].count(":") else it["why"]
        it["pat"] = pat
        it["rate"] = round(rate.get(pat, 0.1), 4)
        it["system"] = sysm.get(it.get("court_id"), -1)
        if not live:
            low_nop.append(it)
            st["low_nopower"] += 1
        elif all(x["admitted"] for x in live):
            low_adm.append(it)
            st["low_admitted"] += 1
        else:
            it["prio"] = 1 if any(not x["admitted"] for x in strong) else 2
            queued.append(it)
            st["queued_P%d" % it["prio"]] += 1
    queued.sort(key=lambda it: (it["prio"], -it["rate"], zlib.crc32(it["id"].encode()) & 0xffff, it["id"]))
    pk = os.path.join(HERE, "packs8")
    os.makedirs(pk, exist_ok=True)
    for f in glob.glob(os.path.join(pk, "pack_*.md")):
        os.remove(f)
    with open(os.path.join(HERE, "index.tsv"), "w", encoding="utf-8", newline=NL) as fx, \
            gzip.open(os.path.join(HERE, "items8.jsonl.gz"), "wt", encoding="utf-8", newline=NL) as fi:
        fx.write("id\tpack\tprio\tpattern\trate\tsystem\tdecade\trepo\n")
        for k in range(0, len(queued), a.size):
            n = k // a.size
            chunk = queued[k:k + a.size]
            with open(os.path.join(pk, "pack_%03d.md" % n), "w", encoding="utf-8", newline=NL) as f:
                f.write((NL + NL).join(render(it) for it in chunk) + NL)
            for it in chunk:
                fx.write("%s\t%03d\t%d\t%s\t%s\t%d\t%d\t%s\n" % (it["id"], n, it["prio"], it["pat"], it["rate"],
                                                                 it["system"], it["date"] // 100000 * 10,
                                                                 it["repo"]))
                rec = {k2: v for k2, v in it.items() if k2 not in ("_text", "w")}
                rec["pack"] = "%03d" % n
                fi.write(json.dumps(rec, ensure_ascii=False) + NL)
    for name, lst in (("low_admitted.tsv", low_adm), ("low_nopower.tsv", low_nop)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline=NL) as f:
            for it in lst:
                f.write("%s\t%s\t%s\t%s\n" % (it["id"], it["repo"], it["pat"],
                                              ",".join("%d:%s:%d" % (x["node"], x["power"], x["admitted"])
                                                       for x in it["targets"])))
    st["packs"] = (len(queued) + a.size - 1) // a.size
    st["pattern_queued"] = dict(collections.Counter(it["pat"] for it in queued).most_common())
    json.dump(dict(st), open(os.path.join(HERE, "port_stats.json"), "w", encoding="utf-8", newline=NL), indent=1)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
