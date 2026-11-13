"""Pattern 1, second read (Claude subagents) of the rows the first reader (Azure gpt-5.4-mini) called zombies.

The blind audit put the first reader's precision at 20% (overruled) and 40% (reversed/vacated): it accepted the
negation as on point without seeing the negating decision. The second read gets the negating decision's own passage.

    python p1_second.py make    -> work/claude/zombie2/aNNN/...
    python p1_second.py merge   -> work/p1_second_out.jsonl ; data/p1_zombies.tsv ; stats on stderr
Selection: every audited row (to score the second read against the full-text audit), every first-read zombie whose
cited decision is a Supreme Court decision or on the known-overrulings list, 250 other O-silent and 120 V-silent
first-read zombies at random.
"""
import json, os, random, sys
from collections import Counter
import hcommon as C
import tasks as T
import audit_prep as A
import claude_batches as B

ROOT = os.path.join(C.HWORK, "claude", "zombie2")
SYS = T.ZOMBIE_SYS + """

You also get the NEGATING DECISION PASSAGE: what the negating court itself said about the earlier decision. Use it (and
your own knowledge of the two cases) to decide negated_point strictly. A decision overruled or disapproved on one point
is still good law on its other points; "yes" needs the proposition the citing court takes to be the one negated (or the
decision reversed or vacated as a whole on that point). Citations inside a quotation of another case, in a dissent or
concurrence, or for a general maxim are use = "other" unless the citing court itself adopts the negated holding."""
FIELDS = ('"same_case": true|false, "acknowledges": true|false, "use": "relies"|"other"|"not_found", "negated_point": '
          '"yes"|"no"|"unclear", "zombie": true|false, "proposition": "<= 25 words", "reason": "<= 30 words"')


def has_actor(r):
    return r.get("actor") not in (None, "-", "")


def select():
    ins = {r["hkey"]: r for r in A.L("p1_llm_in.jsonl")}
    z = []
    for o in A.L("p1_llm_out.jsonl"):
        a = o["ans"]
        if "error" in a or o["key"] not in ins:
            continue
        r = ins[o["key"]]
        if a["zombie"] and r["stratum"] in ("O-silent", "V-silent"):
            z.append(r)
    rnd = random.Random(77)
    known = {int(r[5]) for r in C.read_tsv(os.path.join(C.HUNT, "data", "known_overrulings.tsv")) if r[5].isdigit()}
    aud = {v["hkey"] for v in json.load(open(os.path.join(A.AUD, "p1", "key.json"), encoding="utf-8")).values()}
    sel, grp = {}, {}
    for r in ins.values():
        if r["hkey"] in aud:
            sel[r["hkey"]] = r
            grp[r["hkey"]] = "audited"
    for r in z:
        if r["hkey"] not in sel and (r["cited"] in known
                                     or "Supreme Court of the United States" in (r["cited_court_name"] or "")):
            sel[r["hkey"]] = r
            grp[r["hkey"]] = "scotus"
    rest_o = [r for r in z if r["hkey"] not in sel and r["stratum"] == "O-silent"]
    rest_v = [r for r in z if r["hkey"] not in sel and r["stratum"] == "V-silent"]
    for r in rnd.sample(rest_o, min(250, len(rest_o))):
        sel[r["hkey"]] = r
        grp[r["hkey"]] = "random_O"
    for r in rnd.sample(rest_v, min(120, len(rest_v))):
        sel[r["hkey"]] = r
        grp[r["hkey"]] = "random_V"
    return sel, grp, z


def make():
    sel, grp, z = select()
    C.log("first-read zombies", len(z), "selected", Counter(grp.values()))
    actors = {int(r["actor"]) for r in sel.values() if has_actor(r)}
    meta = C.nodes(actors)
    texts = C.fetch(meta)
    cites = C.cites_of({r["cited"] for r in sel.values()})
    rows = list(sel.values())
    random.Random(5).shuffle(rows)
    os.makedirs(ROOT, exist_ok=True)
    json.dump(grp, open(os.path.join(ROOT, "groups.json"), "w", encoding="utf-8", newline="\n"))
    per_agent, per_file = 45, 9
    for ai in range(0, len(rows), per_agent):
        d = os.path.join(ROOT, "a%03d" % (ai // per_agent))
        os.makedirs(d, exist_ok=True)
        part, man, files = rows[ai:ai + per_agent], {}, []
        for fi in range(0, len(part), per_file):
            fn = "b%d.txt" % (fi // per_file + 1)
            files.append(fn)
            with open(os.path.join(d, fn), "w", encoding="utf-8", newline="\n") as f:
                for j, r in enumerate(part[fi:fi + per_file]):
                    rid = "R%03d" % (fi + j)
                    man[rid] = r["hkey"]
                    neg = "(not available)"
                    if has_actor(r) and int(r["actor"]) in texts:
                        ab = C.body(texts[int(r["actor"])])
                        sp = A.spans_of(ab, cites.get(r["cited"], []), r["cited_name"])
                        neg = "\n[...]\n".join(ab[max(0, s - 1100):e + 1100] for s, e in sp[:2]) or "(citation not located)"
                    f.write("=" * 30 + " ITEM %s " % rid + "=" * 30 + "\n" + T.zombie_user(B.trim(r, cut=1000))
                            + "\n--- NEGATING DECISION PASSAGE ---\n" + neg + "\n\n")
        json.dump(man, open(os.path.join(d, "manifest.json"), "w", encoding="utf-8", newline="\n"))
        with open(os.path.join(d, "INSTRUCTIONS.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# Task\n\n" + SYS + "\n\n# What to do\n\nRead every batch file in this directory (%s). Each holds "
                    "items headed `ITEM Rnnn`. Classify every item independently. Do not search the web or other files. "
                    "Then write ONE file `answers.jsonl` in this directory with the Write tool: one JSON object per "
                    "line, one line per item, with exactly these fields:\n\n    {\"id\": \"Rnnn\", %s}\n\nThere are %d "
                    "items. Reply only with the number of lines written and the count with zombie true.\n"
                    % (", ".join(files), FIELDS, len(part)))
    print(len(rows), "rows", (len(rows) + per_agent - 1) // per_agent, "dirs")


def merge():
    grp = json.load(open(os.path.join(ROOT, "groups.json"), encoding="utf-8"))
    ins = {r["hkey"]: r for r in A.L("p1_llm_in.jsonl")}
    out = []
    for a in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, a, "answers.jsonl")
        if not os.path.exists(p):
            continue
        man = json.load(open(os.path.join(ROOT, a, "manifest.json"), encoding="utf-8"))
        for line in open(p, encoding="utf-8"):
            try:
                j = json.loads(line)
                out.append({"key": man[j.pop("id")], "model": "claude-subagent", "ans": j})
            except Exception:
                pass
    with open(os.path.join(C.HWORK, "p1_second_out.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for o in out:
            f.write(json.dumps(o) + "\n")
    c = Counter((grp[o["key"]], bool(o["ans"].get("zombie"))) for o in out)
    C.log("second read", len(out), sorted(c.items()))
    rows = []
    for o in out:
        r, a = ins[o["key"]], o["ans"]
        if a.get("zombie"):
            rows.append([r["citing"], r["citing_name"][:70], r["citing_cite"], r["citing_date"], r["citing_court_name"],
                         r["cited"], r["cited_name"][:70], r["cited_cite"], r["cited_court_name"], r["wkind"], r["neg_from"],
                         r.get("actor_name", "")[:60], r.get("actor_cite", ""), r["stratum"], grp[o["key"]], r["path"],
                         a.get("proposition", ""), a.get("reason", "")])
    rows.sort(key=lambda x: (x[14] != "scotus", -int(x[3])))
    C.write_tsv(os.path.join(C.HUNT, "data", "p1_zombies.tsv"), rows,
                ["citing", "citing_name", "citing_cite", "citing_date", "citing_court", "cited", "cited_name", "cited_cite",
                 "cited_court", "negation", "neg_from", "negated_by", "negated_by_cite", "stratum", "group", "path",
                 "proposition", "reason"])


if __name__ == "__main__":
    {"make": make, "merge": merge}[sys.argv[1]]()
