"""(7) What a pending bill would affect.

    python tools/bills.py <out dir> 119:hr:18:ih 119:hr:3602:ih ...

For each bill: translate its bill-DTD XML (billdtd), read its instructions (uslm_laws), dry-run them in the Lean check
against the record's current text, then list for each target (a) whether it applies cleanly, (b) sections of the
current Code whose text refers to it, (c) decisions that cite it (by cited subsection where possible).
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import billdtd  # noqa: E402
import build_input as B  # noqa: E402
import fetch  # noqa: E402
import record  # noqa: E402
import uslm_laws as L  # noqa: E402

csv.field_size_limit(10 ** 9)
WORK = Path.home() / "Documents/us-caselaw-lean-work"
HERE = Path(__file__).resolve().parents[1]


def bill_instructions(spec):
    c, kind, num, ver = spec.split(":")
    xml = fetch.fetch(fetch.bill_xml(int(c), kind, num, ver))
    u = billdtd.translate(xml)
    titles = sorted({int(t) for t in re.findall(rb'href="/us/usc/t(\d+)', u)}
                    | {int(t) for t in re.findall(rb"of title (\d+), United States Code", u)})
    out = []
    for t in titles:
        law = L.parse_law(u, None, congress=int(c), number=0, url="", sha256="", fetched_at="", title=t)
        for i in law.instructions:
            out.append({"title": t, "section": i.section, "path": i.path, "label": i.label, "heading": i.heading,
                        "ops": [{"kind": o.kind, "args": o.args} for o in i.ops], "unparsed": i.unparsed,
                        "order": i.order, "text": i.text[:3000]})
    short = re.search(rb"<short-title>(.*?)</short-title>", xml)
    return (short.group(1).decode() if short else spec), out


def current_tree():
    """path -> blob of the record's latest version (main)."""
    out = {}
    r = subprocess.run(["git", "--git-dir", str(record.GITDIR), "ls-tree", "-r", "main"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        meta, path = line.split("\t", 1)
        out[path] = meta.split()[2]
    return out


def lean_rows(name, instrs, tree, blobs):
    groups = defaultdict(list)
    for r in instrs:
        groups[(r["title"], r["section"])].append(r)
    rows, info, gid = [], [], 0
    for (t, s), rs in sorted(groups.items()):
        gid += 1
        p = f"title-{t}/{s}.md"
        if p not in tree:
            for r in rs:
                info.append((gid, 0, t, s, r["path"], "section_not_in_record", r))
            continue
        lines = record.parse_section(blobs.get(tree[p]))
        ops, oid = [], 0
        for r in sorted(rs, key=lambda r: r["order"]):
            path = "#" if r.get("heading") else r["path"]
            pre = B.act_prefix(r.get("text", ""))
            if pre and path != "#" and not path.startswith(pre):
                path = pre + path
            scope, nth, each_words = B.scope_of(r, path)
            fold = "1" if (r.get("heading") or re.search(r"\bheading\b", r.get("text", "")[-400:])) else "0"
            for op in r["ops"] or [{"kind": "unparsed", "args": {}}]:
                low = B.lower(op, path)
                if low is None:
                    continue
                oid += 1
                kind, tgt, a, b, c, nl, pairs, each = low
                each = each or (kind == "S" and each_words)
                n_op = int(op["args"].get("nth") or 0)
                f = [str(oid), kind, tgt, scope[0], scope[1], str(n_op or nth), "1" if each else "0", a, b, c,
                     B.RS.join(f"{x}{B.US}{y}" for x, y in nl), B.RS.join(f"{x}{B.US}{y}" for x, y in pairs), fold]
                ops.append(B.FS.join(re.sub(r"[\t\n\r]", " ", x) for x in f))
                info.append((gid, oid, t, s, path, kind, r, op))
        enc = B.enc_lines(lines)
        rows.append("\t".join([str(gid), enc, enc, B.GS.join(ops)]))
    return rows, info


def section_refs(tree, blobs, targets):
    """For each (title, section): current sections whose text names it, with the designations they name."""
    # "section 924(c)", "sections 1981, 1982, 1983, and 1985 of this title", "section 924(c) of title 18",
    # "18 U.S.C. 924(c)": a list of section numbers after "section(s)", up to the first "of title N" / "of this".
    item = r"[0-9]+[A-Za-z]*(?:[-–][0-9]+[A-Za-z]*)?(?:\([^)]{1,8}\))*"
    lists = re.compile(r"\bsections? ((?:" + item + r"(?:,\s*|,?\s+(?:and|or|through)\s+))*" + item + r")( of title (\d+)\b| of this title| of the [A-Z])?")
    pats = {}
    for t, s in targets:
        se = re.escape(s).replace("\-", "[-–]")
        tok = re.compile(r"(?:^|[\s,])" + se + r"((?:\([^)]{1,8}\))*)(?=$|[\s,])")
        usc = re.compile(r"\b" + str(t) + r" U\.S\.C\. " + se + r"((?:\([^)]+\))*)(?![0-9A-Za-z–-])")
        pats[(t, s)] = (tok, usc)
    hits = defaultdict(list)
    for path, blob in tree.items():
        m = re.match(r"title-(\d+)/(.+)\.md$", path)
        if not m:
            continue
        tt = int(m.group(1))
        text = blobs.get(blob)
        ls = [(m.group(1), m.group(3), m.group(2)) for m in lists.finditer(text)]
        for (t, s), (tok, usc) in pats.items():
            if f"title-{t}/{s}.md" == path:
                continue
            found = []
            for nums, ttl, tail in ls:
                if tail and tail.startswith(" of the "):
                    continue   # "section 5 of the X Act": an Act's own numbering
                if (ttl and int(ttl) == t) or (not ttl and tt == t):
                    found += tok.findall(nums)
            found += usc.findall(text)
            if found:
                hits[(t, s)].append((path, found))
    return hits


def decision_cites(targets):
    """(title, section) -> list of (node, decided, cited designations, repo)."""
    want = {(str(t), s) for t, s in targets}
    out = defaultdict(list)
    for f in sorted((WORK / "usc/cites").glob("*.usc.tsv")):
        repo = f.name[:-len(".usc.tsv")]
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) < 7 or (p[2], p[3]) not in want:
                    continue
                m = re.search(re.escape(p[3]) + r"((?:\s?\([^)]{1,6}\))*)", p[6])
                des = re.sub(r"\s", "", m.group(1)) if m else ""
                out[(int(p[2]), p[3])].append((p[0], p[1], des or (f"({p[4]})" if p[4] else ""), repo))
    return out


def case_names():
    names = {}
    with open(WORK / "usc/results/rows_out.tsv", encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) > 14:
                names[p[1]] = (p[11], p[14], p[2])
    return names


def main():
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)
    specs = sys.argv[2:]
    tree = current_tree()
    blobs = record.Blobs()
    allinfo, allrows, names_of = [], [], {}
    for spec in specs:
        name, instrs = bill_instructions(spec)
        names_of[spec] = name
        rows, info = lean_rows(name, instrs, tree, blobs)
        tag = spec.replace(":", "-")
        (outdir / f"{tag}.in.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        subprocess.run(["C:/Program Files/Git/usr/bin/bash.exe", str(HERE / "tools/run_lean.sh"), str(outdir / f"{tag}.in.tsv"), str(outdir / f"{tag}.out.tsv")], check=True)
        res = {}
        for line in open(outdir / f"{tag}.out.tsv", encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if f[1] != "G":
                res[(int(f[0]), int(f[1]))] = f[2:]
        for x in info:
            gid, oid = x[0], x[1]
            outcome = "section_not_in_record" if oid == 0 else res.get((gid, oid), ["missing", ""])[0]
            places = "" if oid == 0 else res.get((gid, oid), ["", ""])[1]
            r = x[6]
            op = x[7] if len(x) > 7 else {"kind": "", "args": {}}
            allinfo.append({"bill": spec, "name": name, "title": x[2], "section": x[3], "path": x[4],
                            "op": op["kind"], "outcome": outcome, "places": places, "label": r["label"],
                            "args": {k: v for k, v in op["args"].items() if k not in ("lines", "sections")},
                            "wording": r["text"][-300:]})
    targets = sorted({(r["title"], r["section"]) for r in allinfo})
    refs = section_refs(tree, blobs, targets)
    cites = decision_cites(targets)
    names = case_names()
    json.dump(allinfo, open(outdir / "ops.json", "w", encoding="utf-8", newline="\n"), indent=1, default=str)
    summary = {"bills": names_of, "targets": {}}
    for t, s in targets:
        cs = cites.get((t, s), [])
        nodes = {c[0] for c in cs}
        scotus = {c[0] for c in cs if c[3] == "supreme-court"}
        by_sub = Counter()
        for node, day, des, repo in cs:
            by_sub[re.match(r"(\([^)]+\))?", des).group(0) or "(none)"] += 1
        paths = sorted({r["path"] for r in allinfo if (r["title"], r["section"]) == (t, s)})
        subs = sorted({re.match(r"(\([^)]+\))?", p).group(0) for p in paths if p and p != "#"})
        sub_nodes = {c[0] for c in cs if any(c[2].startswith(x) for x in subs)} if subs else set()
        sub_scotus = {n for n in sub_nodes if n in scotus}
        deep = defaultdict(set)
        for p in paths:
            if p and p != "#":
                for node, day, des, repo in cs:
                    if des.startswith(p):
                        deep[p].add(node)
        pool = sub_scotus or scotus
        ex = sorted(pool, key=lambda n: (" U.S. " in names.get(n, ("", "", ""))[1], names.get(n, ("", "", ""))[2]), reverse=True)[:6]
        summary["targets"][f"{t} U.S.C. {s}"] = {
            "paths": paths, "subsections": subs,
            "decisions": len(nodes), "supreme_court": len(scotus),
            "decisions_citing_subsections": len(sub_nodes), "supreme_court_citing_subsections": len(sub_scotus),
            "by_path": {p: len(v) for p, v in deep.items()},
            "top_cited_subsections": by_sub.most_common(8),
            "examples": [names.get(n, ("?", "?", "?")) for n in ex],
            "inbound_sections": len(refs.get((t, s), [])),
            "inbound_to_subsections": sorted({p for p, f in refs.get((t, s), []) if any(any(d.startswith(x) for x in subs) for d in f)}),
            "inbound_sample": [p for p, _ in refs.get((t, s), [])][:15],
        }
    json.dump(summary, open(outdir / "summary.json", "w", encoding="utf-8", newline="\n"), indent=1, default=str)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("inbound_sample", "inbound_to_subsections")} for k, v in summary["targets"].items()}, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
