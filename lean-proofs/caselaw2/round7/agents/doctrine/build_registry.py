"""Round 7, agent doctrine: the doctrine registry and the rejection candidates (court text only).

    python -X utf8 build_registry.py

Reads scan/*.jsonl.gz (dscan.py), graph/cite_index.tsv (citation key -> node), the node date/court arrays.
Writes
  ties.jsonl.gz      every tie record with its resolved target x (or null) and why
  registry.tsv       key, status (unique | ambiguous), strict ties, plain ties, deciding decisions, targets
                     (node:count ...), surfaces, an example (W, quote)
  ambiguous.tsv      the ambiguous keys with their targets
  cands.jsonl        rejection sentences of a power court W holding an unambiguous registered label tied to X
  stats.json
A tie is strict when it has a tie verb ("announced in", "laid down in", ...), the form "the D doctrine of X", or the
possessive "X's D doctrine"; plain when it is only "the doctrine of D in X". Only strict ties are ties (the brief's
forms): they register a target, and a label strictly tied anywhere to two distinct decisions is ambiguous (no row).
Plain ties are kept for information: they are mostly "the demise / rejection of the D rule in Y", Y the rejecting
case (registry column `plain`; stats `registry:unique-but-plain-elsewhere`).
No answer key is read.
"""
import collections, glob, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/round6/history"))
import r6lib as L  # noqa: E402
import dscan as D  # noqa: E402
C = L.reader_common()

GRAPH = os.path.expanduser("~/Documents/us-caselaw-lean-work/graph")
NL = "\n"


def load_idx(keys):
    out = {}
    with open(os.path.join(GRAPH, "cite_index.tsv"), "rb") as f:
        for raw in f:
            i = raw.find(b"\t")
            k = raw[:i].decode("utf-8", "replace")
            if k in keys:
                out.setdefault(k, set()).add(int(raw[i + 1:].strip()))
    return {k: (next(iter(v)) if len(v) == 1 else None) for k, v in out.items()}


def toks(name):
    return {t.lower() for t in (C.name_tokens(name) | C.short_name_tokens(name))}


def possessive_core(core, form):
    """A pre-noun label with a possessive word before its last word ("court of appeals' voluntariness", "the
    State's burden ...") is a description, not a doctrine's name: dropped (registry and candidates)."""
    if form != "pre":
        return False
    ws = core.split()
    return any(w.endswith(("'", "’", "'s", "’s")) for w in ws[:-1]) or         (len(ws) >= 1 and ws[-1].endswith(("'", "’")))


def main():
    ties, rejs, nms = [], [], {}
    for p in sorted(glob.glob(os.path.join(HERE, "scan", "*.jsonl.gz"))):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r["t"] == "tie":
                    ties.append(r)
                elif r["t"] == "rej":
                    rejs.append(r)
                else:
                    nms[r["n"]] = r["pairs"]
    L_ = print
    L_("ties", len(ties), "rejs", len(rejs), "nm", len(nms), flush=True)
    keys = set()
    for r in ties:
        if r.get("ckey"):
            keys.add(r["ckey"])
    for n, pairs in nms.items():
        for nm, k in pairs:
            keys.add(k)
    idx = load_idx(keys)
    L_("idx keys", len(idx), flush=True)
    F = L.Facts()
    st = collections.Counter()
    # ---- resolve every tie
    for r in ties:
        w = r["n"]
        x, how = None, ""
        if r.get("ckey"):
            x = idx.get(r["ckey"])
            how = "cite" if x is not None else "cite-unresolved"
        if x is None:
            ct = toks(r["case"])
            if ct:
                cand = set()
                for nm, k in nms.get(w, []):
                    nt = toks(nm)
                    if ct <= nt:
                        j = idx.get(k)
                        if j is not None:
                            cand.add(j)
                if len(cand) == 1:
                    x, how = next(iter(cand)), "name"
                elif len(cand) > 1:
                    how = "name-ambiguous"
                else:
                    how = how or "name-unresolved"
            else:
                how = how or "no-name-tokens"
        if x is not None and (x == w or int(F.date[x]) == 0 or int(F.date[x]) > int(F.date[w])):
            how, x = "bad-order", None
        r["x"], r["how"] = x, how
        r["strict"] = int(bool(r["verb"]) or r["prep"] in ("of", "pos"))
        st["tie:" + how] += 1
    with gzip.open(os.path.join(HERE, "ties.jsonl.gz"), "wt", encoding="utf-8", newline=NL) as f:
        for r in ties:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    # ---- registry
    reg = collections.defaultdict(lambda: {"strict": collections.Counter(), "plain": collections.Counter(),
                                           "ws": set(), "surf": collections.Counter(), "ex": None, "forms": collections.Counter()})
    for r in ties:
        if r["x"] is None:
            continue
        if possessive_core(r["core"], r["form"]):
            st["tie:possessive-core-dropped"] += 1
            continue
        e = reg[r["lk"]]
        e["strict" if r["strict"] else "plain"][r["x"]] += 1
        e["ws"].add(r["n"])
        e["surf"][r["core"].lower()] += 1
        e["forms"][r["form"]] += 1
        if r["strict"] and (e["ex"] is None or len(r["q"]) < len(e["ex"][1])):
            e["ex"] = (r["n"], r["q"][:400])
    status = {}
    rows = []
    for k, e in reg.items():
        targets = set(e["strict"])
        if not e["strict"]:
            s = "plainOnly"
        elif len(targets) >= 2:
            s = "ambiguous"
        else:
            s = "unique"
        if s == "unique" and set(e["plain"]) - targets:
            st["registry:unique-but-plain-elsewhere"] += 1
        status[k] = (s, next(iter(e["strict"])) if s == "unique" else None)
        tg = collections.Counter(e["strict"]) + collections.Counter(e["plain"])
        rows.append([k, s, sum(e["strict"].values()), sum(e["plain"].values()), len(e["ws"]),
                     " ".join("%d:%d" % (x, c) for x, c in tg.most_common(8)),
                     " | ".join(x for x, _ in e["surf"].most_common(3)),
                     ",".join("%s:%d" % kv for kv in e["forms"].most_common()),
                     "%s %s" % e["ex"] if e["ex"] else "-"])
    rows.sort(key=lambda r: (-r[4], r[0]))
    L.os.makedirs(HERE, exist_ok=True)
    with open(os.path.join(HERE, "registry.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("key\tstatus\tstrict\tplain\tdecisions\ttargets\tsurfaces\tforms\texample\n")
        for r in rows:
            f.write("\t".join(L.norm(str(x)) for x in r) + NL)
    with open(os.path.join(HERE, "ambiguous.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            if r[1] == "ambiguous":
                f.write("\t".join(L.norm(str(x)) for x in r[:7]) + NL)
    st.update(collections.Counter("registry:" + v[0] for v in status.values()))
    # ---- ties inside each W (for the joined quote)
    wties = collections.defaultdict(list)
    for r in ties:
        if r["x"] is not None:
            wties[(r["n"], r["lk"])].append(r)
    # ---- rejection candidates
    out = []
    for r in rejs:
        w = r["n"]
        cw = int(F.court[w])
        tier, sysw = F.tier(cw), F.system(cw)
        if tier != "L":
            st["rej:not-last-resort"] += 1
            continue
        seen = set()
        for lab in r["labels"]:
            core, lk, form, noun, a, b = lab
            if possessive_core(core, form):
                st["rej-label:possessive-core"] += 1
                continue
            s, x = status.get(lk, ("unregistered", None))
            if s != "unique":
                st["rej-label:" + s] += 1
                continue
            if lk in seen:
                continue
            seen.add(lk)
            if x == w or int(F.date[x]) == 0 or int(F.date[x]) >= int(F.date[w]):
                st["rej-label:order"] += 1
                continue
            cx = int(F.court[x])
            if not (F.is_scotus(cw) or F.system(cx) == sysw):
                st["rej-label:no-power"] += 1
                continue
            own = [t for t in wties.get((w, lk), []) if t["x"] == x]
            st["rej-label:cand" + ("-owntie" if own else "-needtie")] += 1
            out.append({"w": w, "x": x, "lk": lk, "core": core, "form": form, "noun": noun, "la": [a, b],
                        "s": r["s"], "q": r["q"], "part": r["part"], "cue": r["cue"],
                        "own_ties": [{"s": t["s"], "q": t["q"], "part": t["part"], "verb": t["verb"],
                                      "case": t["case"], "ckey": t.get("ckey"), "how": t["how"]} for t in own],
                        "w_date": int(F.date[w]), "x_date": int(F.date[x]), "w_court": cw, "x_court": cx})
    with open(os.path.join(HERE, "cands.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for c in out:
            f.write(json.dumps(c, ensure_ascii=False) + NL)
    st["cands"] = len(out)
    st["cand_w"] = len({c["w"] for c in out})
    with open(os.path.join(HERE, "stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(sorted(st.items())), f, indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
