"""Turn extracted instructions + the record into the Lean runner's input.

    python tools/build_input.py data/instructions.jsonl data/lean_in.tsv data/ops.tsv [--shards N]

Python's part is parsing only: it lowers each parsed operation to the runner's encoding, resolves which record
versions stand before and after the Act, and writes the lines with their designation paths. Every outcome is decided
by the Lean runner.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import record  # noqa: E402

RS, US, GS, FS = "\x1e", "\x1f", "\x1d", "\x1c"


def norm(s: str, law: bool = False) -> str:
    if s is None:
        return ""
    s = s.replace("\x00closing", "")
    if law:
        # quotations inside quoted matter are single-quoted in the Act and double-quoted in the Code
        s = re.sub(r"(^|[\s(\[—-])‘([^‘’]+)’", lambda m: f"{m.group(1)}“{m.group(2)}”", s)
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace("–", "-")
    s = s.replace(" ", " ").replace(" ", " ").replace(" ", " ").replace(" ", " ")
    s = re.sub(r"[\x00-\x1f]", " ", s)
    s = re.sub(r"\s*—\s*", "—", s)
    # The Code prints "section 406 of title 5" where an Act says "section 406 of title 5, United States Code,"
    s = re.sub(r"\b(title \d+[A-Z]?), United States Code,?", r"\1", s)
    s = re.sub(r"\s+", " ", s)
    return s


ACT_CITE = re.compile(
    r"^\s*(?:(?:Subsection|Paragraph|Subparagraph)s? (?P<d1>(?:\([^)]+\))+) of section [\w.–-]+"
    r"|[Ss]ection [0-9A-Za-z.–-]+?(?P<d2>(?:\([^)]+\))+))"
    r" of (?:the |title )[^()]*?(?:\([^()]*\)[^()]*?)*\(\d+ U\.S\.C\. (?P<usc>[^()]+?)(?P<uscd>(?:\([^)]*\))*)(?: note)?\)")


def act_prefix(wording: str) -> str:
    """"Section 8(a) of the Global Food Security Act (22 U.S.C. 9307)" or "Subsection (l) of section 25 of the ... Act
    (15 U.S.C. 278k)": the Act's own designations, when the Code citation gives none."""
    m = ACT_CITE.match(wording or "")
    if not m or m.group("uscd"):
        return ""
    return m.group("d1") or m.group("d2") or ""


def is_stub(lines) -> bool:
    head = next((t for p, t in lines if p == "#"), "")
    body = [t for p, t in lines if p != "#"]
    return bool(re.search(r"\b(Repealed|Transferred|Omitted|Renumbered)\b", head)) and sum(len(t) for t in body) < 400


ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "last": 0}
EACH = re.compile(r"\b(?:both places|each other place|in each place|wherever (?:it|such term) appears|"
                  r"each place (?:it|such term|that term|the term|such word) appears)\b")


def scope_of(r, path):
    """Narrowing words in the instruction (scope ops from the parser first): matter preceding/following a child,
    "in the ... heading", "in the second sentence"; and whether it says "both places" / "each other place"."""
    scope, nth = ("all", ""), 0
    for op in r["ops"]:
        if op["kind"] == "scope":
            scope = ("pre" if op["args"]["side"] == "preceding" else "fol", op["args"]["of"])
        elif op["kind"] == "nth":
            nth = int(op["args"]["n"])
        elif op["kind"] == "sentence":
            scope = ("sent", str(ORD.get(op["args"].get("which"), 1)))
    words = r.get("text", "")
    tail = words[-400:]
    if scope[0] == "all" and path != "#":
        if re.search(r"\bin the (?:(?:sub)?section |paragraph |subparagraph |clause |subclause |item )?heading\b|\bin the heading of\b", words):
            scope = ("head", "")
        else:
            m = list(re.finditer(r"\bin the (first|second|third|fourth|fifth|sixth|last) sentence\b", words))
            if m:
                scope = ("sent", str(ORD[m[-1].group(1)]))
    return scope, nth, bool(EACH.search(tail))


def enc_lines(lines) -> str:
    return RS.join(f"{p}{US}{norm(t)}" for p, t in lines)


def rel_lines(content) -> list[tuple[str, str]]:
    """Content lines (relative level, text) of a quoted block -> (relative path, text)."""
    md = []
    for lvl, text in content:
        t = norm(text, law=True)
        if t.strip():
            md.append("  " * max(int(lvl), 0) + "- " + t)
    return [(p, t) for p, t in record.parse_section("\n".join(md)) if p != "#"]


def sep_after(anchor: str, new: str) -> str:
    if not new or new[0] in ",.;:)]" or anchor.endswith(("(", "—", "-", "/")):
        return ""
    return " "


def sep_before(new: str, anchor: str) -> str:
    if not new or new.endswith(("(", "—", "-", "/")) or (anchor and anchor[0] in ",.;:)]"):
        return ""
    return " "


def last_des(path: str):
    m = re.match(r"^(.*)(\([^()]*\))$", path)
    return (m.group(1), m.group(2)) if m else ("", "")


def lower(op, path):
    """(kind, target, a, b, c, lines, pairs) for one parsed operation, or None for a modifier."""
    k, a = op["kind"], op["args"]
    q = lambda key: norm(a.get(key, ""), law=True)  # noqa: E731
    if k in ("scope", "nth", "sentence"):
        return None
    if k in ("replace", "replace_all"):
        return ("S", path, q("old"), q("new"), "", [], [], k == "replace_all")
    if k in ("delete", "delete_all"):
        return ("S", path, q("old"), "", "", [], [], k == "delete_all")
    if k == "insert_after":
        anc, new = q("anchor"), q("new")
        return ("S", path, anc, anc + sep_after(anc, new) + new, "", [], [], bool(a.get("all")))
    if k == "insert_before":
        anc, new = q("anchor"), q("new")
        return ("S", path, anc, new + sep_before(new, anc) + anc, "", [], [], bool(a.get("all")))
    if k == "replace_end":
        return ("E", path, q("old"), q("new"), "", [], [], False)
    if k == "insert_before_end":
        end, new = q("end"), q("new")
        return ("E", path, end, ("" if not new or new[0] in ",.;:" else " ") + new + end, "", [], [], False)
    if k == "append_text":
        return ("A", path, q("new"), "", "", [], [], False)
    if k == "replace_range":
        return ("R", path, q("start"), q("through"), q("new"), [], [], False)
    if k == "replace_to_end":
        return ("T", path, q("start"), q("new"), "", [], [], False)
    if k == "append_block":
        if a.get("sections") or a.get("chapter"):
            return ("U", path, "append_sections", "", "", [], [], False)
        return ("B", path, "", "", "", rel_lines(a.get("lines", [])), [], False)
    if k in ("insert_block_after", "insert_block_before"):
        return ("IA" if k.endswith("after") else "IB", path, a.get("sibling", ""), "", "", rel_lines(a.get("lines", [])), [], False)
    if k == "delete_provision":
        return ("D", path, a.get("target", ""), "", "", [], [], False)
    if k == "replace_provision":
        return ("P", path, a.get("target", ""), "", "", rel_lines(a.get("lines", [])), [], False)
    if k == "replace_block":
        base, d = last_des(path)
        return ("P", base, d, "", "", rel_lines(a.get("lines", [])), [], False)
    if k == "redesignate":
        return ("M", path, "", "", "", [], [(f, t) for f, t in a.get("pairs", [])], False)
    return ("U", path, k, "", "", [], [], False)


def main():
    inp, outp, opsp = sys.argv[1], sys.argv[2], sys.argv[3]
    shards = int(sys.argv[sys.argv.index("--shards") + 1]) if "--shards" in sys.argv else 1
    by_path, by_law = record.load_versions()
    blobs = record.Blobs()
    groups = defaultdict(list)
    approved = {}
    for line in open(inp, encoding="utf-8"):
        r = json.loads(line)
        if r.get("header"):
            approved[r["law"]] = r.get("approved", "")
            continue
        if "ops" not in r:
            continue
        groups[(r["law"], r["title"], r["section"])].append(r)
    outs = [open(f"{outp}.{i}" if shards > 1 else outp, "w", encoding="utf-8", newline="\n") for i in range(shards)]
    opsf = open(opsp, "w", encoding="utf-8", newline="\n")
    opsf.write("gid\toid\tlaw\ttitle\tsection\tpath\tkind\tlean_kind\tlaw_commit\tunparsed\tlabel\targs\twording\n")
    gstat = defaultdict(int)
    gid = 0
    for (law, title, section), rows in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        gid += 1
        rows.sort(key=lambda r: r["order"])
        fpath = f"title-{title}/{section}.md"
        vs = by_path.get(fpath)
        status = "ok"
        before_lines, after_lines = [], []
        if section.startswith("ch") or not section:
            status = "chapter_level"
        elif not vs:
            status = "section_not_in_record"
        else:
            idx = by_law.get(law, {}).get(fpath, [])
            if idx:
                bi = idx[0] - 1
                after = vs[idx[-1]]
                status = "ok" if bi >= 0 else "created_by_law"
                if len(idx) > 1:
                    status = "ok_multi"
            else:
                day = int((approved.get(law) or "0").replace("-", "") or 0)
                bi = max((i for i, v in enumerate(vs) if v[3] <= day), default=-1)
                after = vs[bi + 1] if bi + 1 < len(vs) else None
                status = "no_law_commit"
            if bi >= 0:
                before_lines = record.parse_section(blobs.get(vs[bi][4]))
            if after is not None:
                after_lines = record.parse_section(blobs.get(after[4]))
            else:
                after_lines = before_lines
        if status != "no_law_commit" and after_lines and is_stub(after_lines) and not is_stub(before_lines):
            status = "after_stub"   # the record shows the section repealed or moved by this Act
        gstat[status] += 1
        oplist = []
        oid = 0
        for r in rows:
            path = "#" if r.get("heading") else r["path"]
            pre = act_prefix(r.get("text", ""))
            if pre and path != "#" and not path.startswith(pre):
                path = pre + path
            path = re.sub(r"(\([^()]+\))\1", r"\1", path)   # "(a)(a)(1)": a designation named twice
            scope, nth, each_words = scope_of(r, path)
            # Headings are printed in small capitals: compare without case.
            own = r.get("text", "")[-400:]
            fold = "1" if (r.get("heading") or re.search(r"\bheading\b", own)) else "0"
            act_wide = "etseq" in path or "note" in path
            ops = r["ops"] or [{"kind": "unparsed", "args": {}}]
            for op in ops:
                low = lower(op, path)
                if low is None:
                    continue
                if act_wide:
                    low = ("U", path, "act_wide", "", "", [], [], False)
                elif low[0] == "S" and fold == "0" and re.fullmatch(r"(?:[A-Z][\w'-]*|and|or|of|the|for|to|in|on|by|with)(?: (?:[A-Z][\w'-]*|and|or|of|the|for|to|in|on|by|with))+", low[2] or "") and low[2][0].isupper():
                    fold = "1"   # Title Case words are a heading printed in small capitals
                oid += 1
                kind, tgt, a, b, c, lines, pairs, each = low
                each = each or (kind == "S" and each_words)
                n_op = int(op["args"].get("nth") or 0) if isinstance(op.get("args"), dict) else 0
                fields = [str(oid), kind, tgt, scope[0], scope[1], str(n_op or nth), "1" if each else "0", a, b, c,
                          RS.join(f"{p}{US}{t}" for p, t in lines), RS.join(f"{x}{US}{y}" for x, y in pairs), fold]
                fields = [re.sub(r"[\t\n\r]", " ", x) for x in fields]
                oplist.append(FS.join(fields))
                args = json.dumps({k: v for k, v in op["args"].items() if k not in ("lines", "sections")}, ensure_ascii=False)[:600]
                opsf.write("\t".join(re.sub(r"[\t\n\r]", " ", str(x)) for x in [
                    gid, oid, law, title, section, path, op["kind"], kind, status, int(r.get("unparsed", False)),
                    r.get("label", ""), args, r.get("text", "")[:1500]]) + "\n")
        if status in ("section_not_in_record", "chapter_level"):
            continue
        outs[gid % shards].write("\t".join([str(gid), enc_lines(before_lines), enc_lines(after_lines), GS.join(oplist)]) + "\n")
    for f in outs:
        f.close()
    opsf.close()
    print(dict(gstat), "groups", gid)


if __name__ == "__main__":
    main()
