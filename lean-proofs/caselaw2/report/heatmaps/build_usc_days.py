"""Row-level data behind the interactive "US Code vulnerabilities introduced, by day" calendar.

    python build_usc_days.py [OUT_JSON]

Uses the same inclusion rules as compute.py (section "usc") and refuses to write unless the per-day counts equal
series/usc.tsv day by day and the totals are 8,212 = 6,494 + 1,198 + 520.

Output (compact JSON, default: lexweb-build/public/blog-data/us-code-vulnerabilities-by-day/days.json):
  laws   list of [label, short title or ""]; items refer to a law by its index
  days   {"YYYYMMDD": [xref, amend, dup, groups]}, groups = [[law index, [item, ...]], ...] largest first
  item   dangling reference   [0, citing section, missing target, reason code, ended code, end day or 0]
         amending instruction [1, section and path, words not found, operation code, where in the Act]
         duplicate            [2, section and parent, designation]
         any item may end in a flag 1: the evidence puts it in doubt (see the comment where groups are written)
  A section is written "26 857" (title, section) with any path appended as printed: "26 856(d)(8)(F)".
  proof/YYYYMMDD.json  the evidence for each item of that day, [group][item] in the same order (usc_proofs.py).
  reasons / ended / ops are the code tables. ended: 0 still dangling, 1 target came into the record, 2 reference removed.
Standard library only.
"""
import collections
import html
import json
import pickle
import re
import sys
from pathlib import Path

HOME = Path.home()
W = HOME / "Documents" / "us-caselaw-lean-work"
HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    HOME / "lexweb-build" / "public" / "blog-data" / "us-code-vulnerabilities-by-day" / "days.json")

REASONS = ["designation missing", "target repealed", "target not yet in record", "target file removed",
           "target never in record", "designation repealed", "target transferred", "target vacant", "target reserved"]
ENDED = ["", "resolved", "removed"]
OPS = ["replace", "delete", "insert_after", "insert_before", "replace_all", "replace_range", "replace_to_end",
       "replace_end", "insert_before_end", "delete_all"]
WORDS_MAX = 110


def sec(path_md):
    """title-26/857.md -> '26 857'"""
    m = re.fullmatch(r"title-([^/]+)/(.+)\.md", path_md)
    if not m:
        raise SystemExit(f"unexpected section path {path_md!r}")
    return f"{m.group(1)} {m.group(2)}"


def desig(dotted):
    """'d.8.F' -> '(d)(8)(F)'"""
    return "".join(f"({x})" for x in dotted.split(".")) if dotted else ""


def clip(s):
    s = " ".join(s.split())
    return s if len(s) <= WORDS_MAX else s[: WORDS_MAX - 1].rstrip() + "…"


def split_label(label):
    """'Pub. L. 115-97 (Tax Cuts and Jobs Act)' -> ('Pub. L. 115-97', 'Tax Cuts and Jobs Act')"""
    label = html.unescape(label)
    m = re.fullmatch(r"(Pub\. L\. \d+-\d+) \((.+)\)", label)
    return (m.group(1), m.group(2)) if m else (label, "")


def main():
    sys.path.insert(0, str(HOME / "Documents" / "global-law-lean" / "lean-proofs" / "tools" / "caselaw"))
    import usc_xrefs  # noqa: E402
    from usc_xrefs import load_versions, pstr  # noqa: E402
    from usc_proofs import Proofs  # noqa: E402
    vers = load_versions(str(W / "usc" / "versions.tsv"))
    proofs = Proofs(W / "usc-full.git", W / "usc" / "versions.tsv", usc_xrefs)
    proofs.prepare(vers)

    # short titles the record gives each Public Law (used where a row names the law by number only)
    short = {}
    for vs in vers.values():
        for v in vs:
            if v[4] and v[2].startswith("Pub. L. "):
                short.setdefault(v[2], html.unescape(v[4]))

    counts = collections.defaultdict(collections.Counter)
    items = collections.defaultdict(lambda: collections.defaultdict(list))  # day -> law name -> [item]
    stats = collections.Counter()

    # 1. dangling cross-references (compute.py: every episode except class at-start, dated by `from`)
    with open(W / "uses" / "xrefs" / "dangling_episodes.tsv", encoding="utf-8") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(hdr)}
        for line in f:
            a = line.rstrip("\n").split("\t")
            if a[ix["class"]] == "at-start":
                continue
            d = int(a[ix["from"]])
            name, st = split_label(a[ix["cause"]] or "?")
            if st:
                short.setdefault(name, st)
            ended = ENDED.index(a[ix["ended"]])
            until = int(a[ix["until"]]) if a[ix["until"]] else 0
            if bool(ended) != bool(until):
                raise SystemExit(f"episode {a[0]}: ended/until disagree")
            counts[d]["xref"] += 1
            stats["xref_open" if not ended else "xref_" + ENDED[ended]] += 1
            items[d][name].append([0, sec(a[ix["source"]]), sec(a[ix["target"]]) + desig(a[ix["path"]]),
                                   REASONS.index(a[ix["reason"]]), ended, until,
                                   proofs.xref(a[ix["source"]], a[ix["target"]], a[ix["path"]], d, ended, until,
                                               a[ix["class"]], name)])

    # 2. amending instructions whose words are not in the section (not_found, main scope, by approval day)
    approved = {}
    with open(W / "uses" / "amendments" / "data" / "instructions.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("header"):
                approved[r["law"]] = int(r["approved"].replace("-", ""))
    with open(W / "uses" / "amendments" / "data" / "results.tsv", encoding="utf-8") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(hdr)}
        for line in f:
            a = line.rstrip("\n").split("\t")
            if a[ix["law_commit"]] not in ("ok", "ok_multi") or a[ix["outcome"]] != "not_found":
                continue
            d = approved[a[ix["law"]]]
            raw = a[ix["args"]]
            try:
                args = json.loads(raw)
            except ValueError:
                # results.tsv cuts long args at 300 characters: read the string values that are there
                args = {}
                for m in re.finditer(r'"(\w+)": "((?:[^"\\]|\\.)*)("?)', raw):
                    try:
                        args[m.group(1)] = json.loads('"' + m.group(2).rstrip("\\") + '"')
                    except ValueError:
                        args[m.group(1)] = m.group(2)
                stats["amend_args_cut"] += 1
            words = next((args[k] for k in ("old", "anchor", "start", "from", "end") if isinstance(args.get(k), str)
                          and args[k]), None)
            if words is None:
                words = next((v for k, v in args.items() if isinstance(v, str) and v and k != "new"), "")
                stats["amend_words_other_key"] += 1
            if not words:
                stats["amend_no_words"] += 1
            counts[d]["amend"] += 1
            items[d][a[ix["law"]]].append([1, f"{a[ix['title']]} {a[ix['section']]}{a[ix['path']]}", clip(words),
                                           OPS.index(a[ix["kind"]]), a[ix["label"]],
                                           proofs.amend(a[ix["title"]], a[ix["section"]], a[ix["path"]], words,
                                                        a[ix["wording"]], a[ix["law"]], d, a[ix["kind"]])])

    # 3. duplicate sibling designations, by the version that first made each one (1994 edition excluded)
    scan_ = pickle.load(open(W / "uses" / "xrefs" / "data" / "scan.pkl", "rb"))
    first = {}
    for p, vs in vers.items():
        prev = set()
        for v in vs:
            a = scan_.get((p, v[3])) if v[3] else None
            ds = {(pstr(x[0]), x[1]) for x in a[4]} if a and a[0] else set()
            for k in ds - prev:
                first.setdefault((p, k), v)
            prev = ds
    for (p, (parent, des)), v in sorted(first.items(), key=lambda kv: (kv[1][0], kv[0])):
        if v[2] == "1994 edition of the US Code":
            continue
        name = html.unescape(v[2])
        if v[4]:
            short.setdefault(name, html.unescape(v[4]))
        counts[v[0]]["dup"] += 1
        items[v[0]][name].append([2, sec(p) + desig(parent), f"({des})", proofs.dup(p, next(x for x in proofs.vers[p] if x[5] == v[5]), parent, des)])

    # ---- must reproduce series/usc.tsv exactly ----
    want = {}
    with open(HERE / "series" / "usc.tsv", encoding="utf-8") as f:
        next(f)
        for line in f:
            d, n, x, a, u = (int(t) for t in line.split("\t"))
            want[d] = (n, x, a, u)
    got = {d: (c["xref"] + c["amend"] + c["dup"], c["xref"], c["amend"], c["dup"]) for d, c in counts.items()}
    bad = [(d, want.get(d), got.get(d)) for d in sorted(set(want) | set(got)) if want.get(d) != got.get(d)]
    if bad:
        raise SystemExit(f"{len(bad)} days differ from series/usc.tsv, e.g. {bad[:5]}")
    tot = [sum(g[i] for g in got.values()) for i in range(4)]
    if tot != [8212, 6494, 1198, 520]:
        raise SystemExit(f"totals differ: {tot}")

    laws, law_ix = [], {}
    days = {}
    proof_days = {}
    for d in sorted(items):
        groups = []
        for name, its in sorted(items[d].items(), key=lambda kv: (-len(kv[1]), kv[0])):
            if name not in law_ix:
                law_ix[name] = len(laws)
                laws.append([name, short.get(name, "")])
            its.sort(key=lambda it: (it[0], it[1], it[2]))
            proof_days.setdefault(d, []).append([it[-1] for it in its])
            # a last flag the page shows on the row itself: 1 when the evidence puts the defect in doubt (the words of
            # an amending instruction are in the section after all; a reference sits in the note of a repealed section)
            groups.append([law_ix[name], [it[:-1] + ([1] if (it[0] == 1 and it[-1].get("insection"))
                                                     or (it[0] == 0 and it[-1]["s"].get("stub")) else [])
                                          for it in its]])
        days[str(d)] = [got[d][1], got[d][2], got[d][3], groups]
        if sum(len(g[1]) for g in groups) != got[d][0]:
            raise SystemExit(f"{d}: items do not add up")

    out = {"totals": tot, "reasons": REASONS, "ended": ENDED, "ops": OPS, "laws": laws, "days": days}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    # the counts alone, imported by the page so the calendar is coloured before days.json arrives
    if len(sys.argv) <= 1:
        cpath = HOME / "lexweb-build" / "app" / "blog" / "us-code-vulnerabilities-by-day" / "counts.json"
        cpath.parent.mkdir(parents=True, exist_ok=True)
        with open(cpath, "w", encoding="utf-8", newline="\n") as f:
            json.dump({k: v[:3] for k, v in days.items()}, f, separators=(",", ":"))
            f.write("\n")
    pdir = OUT.parent / "proof"
    pdir.mkdir(exist_ok=True)
    big = 0
    for d, pg in proof_days.items():
        with open(pdir / f"{d}.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(pg, f, ensure_ascii=False, separators=(",", ":"))
        big = max(big, (pdir / f"{d}.json").stat().st_size)
    print(f"proofs: {len(proof_days)} files, largest {big:,} bytes; {dict(proofs.stats)}")
    print(f"ok: {len(days)} days reproduce series/usc.tsv; totals {tot}")
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes), {len(laws)} laws, "
          f"{sum(1 for l in laws if l[0].startswith('Pub. L.') and not l[1])} Public Laws without a short title")
    print(dict(stats))


if __name__ == "__main__":
    main()
