"""The rule "the final judgment line decides" as a general selection over the pairs of `pairs.py`.

    python -X utf8 round8/agents/contradict/rule.py            -> work/rule_rows.jsonl, work/rule_pairs.tsv,
                                                                   remove_ids.txt, then (separately) certify8

For an acting decision W and target X with an admitted v3 history row B and a new anchored row N of the opposite
polarity (N passed every certify8 check; it was refused only by conflictBase), N replaces B when
  (i)   N passes certify8 (checked when the selected rows are certified with --keep-base-conflicts),
  (ii)  N's quote is one of W's own disposition sentences in the opinion of the court (cache `h`, part majority or
        perCuriam), B was quoted from the same text (same sha), N starts at or after the end of B's quote, and no
        later own disposition sentence of W has another polarity than N (N is the final judgment line),
  (iii) the scopes are equal or N's scope is `unknown`,
  and every v3 row of the pair that clashes with N satisfies (ii)-(iii) (all of them are removed).
Reads only work/pairs.tsv (built from the round-6 rejects, the v3 tables and the cache); no answer key.
"""
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")


def main():
    lines = [l.rstrip("\n").split("\t") for l in open(os.path.join(WORK, "pairs.tsv"), encoding="utf-8")]
    cols = lines[0]
    recs = [dict(zip(cols, l)) for l in lines[1:]]
    rows = {}
    for l in open(os.path.join(WORK, "rows_new.jsonl"), encoding="utf-8"):
        o = json.loads(l)
        rows[o["pid"]] = o
    by_new = collections.defaultdict(list)   # one new row may clash with several base rows
    for r in recs:
        by_new[(r["by"], r["target"], r["new_kind"])].append(r)
    # the clash list per new row comes from the certify8 base_conflicts.tsv of all candidates
    clash = collections.defaultdict(set)
    for l in open(os.path.join(HERE, "cert_all", "base_conflicts.tsv"), encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        clash[p[0]].add(p[1])
    st = collections.Counter()
    sel, remove = [], set()
    for key, grp in sorted(by_new.items()):
        r0 = grp[0]
        hid = "h8:%s:%s:%s" % key
        bases = {r["base_id"]: r for r in grp}
        if set(bases) != clash.get(hid, set()):
            # a clashing base row the reject did not name: look it up in the other pair lines
            st["clash_set_differs"] += 1
        ok = True
        why = None
        for bid in clash.get(hid, set()) | set(bases):
            r = bases.get(bid)
            if r is None:
                ok, why = False, "clash_not_in_pairs"
                break
            if r["admitted"] != "1":
                ok, why = False, "base_not_admitted"
                break
            if r["same_text"] != "1":
                ok, why = False, "base_other_text"
                break
            if r["new_is_h"] != "h_court":
                ok, why = False, "new_not_own_disposition"
                break
            if r["pos"] != "after":
                ok, why = False, "new_not_after_base:" + r["pos"]
                break
            if r["final"] not in ("final", "final_samepol"):
                ok, why = False, "new_not_final:" + r["final"]
                break
            if r["new_scope"] != r["base_scope"] and r["new_scope"] != "unknown":
                ok, why = False, "scope_new_narrower_unknown_base"
                break
        if not ok:
            st["kept_base:" + why] += 1
            continue
        st["replace"] += 1
        st["replace_bases"] += len(bases)
        sel.append((r0["pid"], hid, sorted(bases)))
        remove.update(bases)
    with open(os.path.join(WORK, "rule_rows.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for pid, hid, _b in sel:
            o = dict(rows[pid])
            o["note"] = (o.get("note") or "") + "|contra8:final_line"
            o.pop("pid", None)
            f.write(json.dumps(o) + "\n")
    with open(os.path.join(WORK, "rule_pairs.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("new_id\tbase_id\n")
        for pid, hid, bl in sel:
            for b in bl:
                f.write("%s\t%s\n" % (hid, b))
    with open(os.path.join(HERE, "remove_ids.txt"), "w", encoding="utf-8", newline="\n") as f:
        for b in sorted(remove):
            f.write(b + "\n")
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "rule_stats.json"), "w"), indent=1)
    for k, v in sorted(st.items()):
        print("%-45s %d" % (k, v))


if __name__ == "__main__":
    main()
