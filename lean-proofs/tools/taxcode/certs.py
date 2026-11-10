"""Generate kernel-checked certificates for the confirmed drafting faults in Title 26.

    python tools/taxcode/certs.py <out dir> <lean-proofs dir>

Reads triage.csv (the hand-triaged findings, verdict "confirmed"), findings.json, t26.json and ids.tsv (all written
from the OLRC USLM XML of the release point by parse_uslm.py and the Lean checker), and writes
TaxCode/Certs/{References,Duplicates,Parens}.lean and TaxCode/Certs/All.lean. Each certificate carries its evidence as
literal data copied from the XML and proves the fault with `decide +kernel` (the kernel evaluates it):

* a reference to a subdivision that does not exist: the cited words occur in the citing provision's own words, and
  the next designation of the cited path is not among the designations of the deepest provision that does exist;
* a reference to a provision that is repealed or struck: the same, with the status the XML gives each designation;
* a wrong level word ("paragraph (b)"): no subdivision at the named level has the designation, and the provision one
  level up or down does;
* a duplicate designation: the complete list of designations under the parent element has the designation twice;
* unbalanced parentheses: the parenthesis count over the provision's own words ends above zero or goes below it.
"""
import csv, json, re, sys
from collections import defaultdict
from pathlib import Path

out, lp = Path(sys.argv[1]), Path(sys.argv[2])
RELEASE = "119-138"
# confirmed faults that the checker still reports after the parser fixes (class_after is the re-run's class)
rows = [r for r in csv.DictReader(open(out / "triage.csv", encoding="utf-8")) if r["verdict"] == "confirmed" and r["class_after"]]
for r in rows:
    r["class"] = r["class_after"]
F = json.load(open(out / "findings.json", encoding="utf-8"))
P = json.load(open(out / "t26.json", encoding="utf-8"))["provisions"]
byid = {}
for p in P:
    byid.setdefault(p["id"], p)
kids = defaultdict(list)        # parent identifier -> children (all elements, in document order)
kids_el = defaultdict(list)     # parent element -> children
for p in P:
    if p.get("parent"):
        kids[p["parent"]].append(p)
    if p.get("parentElement"):
        kids_el[p["parentElement"]].append(p)


def cite(i):
    m = re.match(r"/us/usc/t([0-9A-Za-z]+)/s([^/]+)((?:/[^/]+)*)", i)
    if not m:
        return i
    t, s_, rest = m.groups()
    path = "".join(f"({x})" for x in rest.split("/") if x)
    return f"§{s_}{path}" if t == "26" else f"{t} U.S.C. §{s_}{path}"


FK = {}
for f in F:
    FK.setdefault((f["class"], cite(f["citing"]), cite(f["target"])), f)

# children of identifiers outside Title 26, from ids.tsv (only the ones needed)
need_other = set()
for r in rows:
    f = FK[(r["class"], r["citing"], r["target"])]
    if not f["target"].startswith("/us/usc/t26/"):
        need_other.add(f["target"])
other_kids, other_status = defaultdict(list), {}
if need_other:
    prefixes = set()
    for t in need_other:
        parts = t.split("/")
        for cut in range(4, len(parts)):  # from the title down
            prefixes.add("/".join(parts[:cut]))
    for line in open(out / "ids.tsv", encoding="utf-8"):
        i, _, st = line.rstrip("\n").partition("\t")
        par = i.rsplit("/", 1)[0]
        if i in prefixes:
            other_status[i] = st
        if par in prefixes:
            other_kids[par].append((i.rsplit("/", 1)[1], st))


def lit(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def chars(s):
    """A Lean `List Char` literal: the kernel evaluates lists of characters directly (and slowly through `String`)."""
    def one(c):
        if c in "\\'":
            return "'\\" + c + "'"
        return "'" + c + "'"
    return "[" + ", ".join(one(c) for c in s) + "]"


def lname(s):
    """A Lean identifier for a citation: §1400Z–2(d)(2)(D)(ii) -> s1400Z_2_d_2_D_ii."""
    return "s" + re.sub(r"_+", "_", re.sub(r"[^0-9A-Za-z]", "_", s.replace("§", "").replace("U.S.C.", "usc"))).strip("_")


def doc(lines):
    return "/-- " + "\n".join(lines).replace("-/", "- /").replace("/-", "/ -") + " -/"


def words_of(p):
    """The provision's own words as the checker reads them: footnote marks blanked, hyperlinked citations as ⟦REF⟧."""
    return p["text"].replace("†", " ")


def status_of(i):
    if i in byid:
        return byid[i]["status"]
    return other_status.get(i)


def exists(i):
    return i in byid or i in other_status


def children(i):
    if re.fullmatch(r"/us/usc/t26", i):  # every section of Title 26 (repealed runs expanded)
        return [(c.rsplit("/", 1)[1], byid[c]["status"]) for c in byid if re.fullmatch(r"/us/usc/t26/s[0-9][^/]*", c) and "..." not in c]
    if i in byid:
        return [(c["num"] or c["id"].rsplit("/", 1)[1], c["status"]) for c in kids.get(i, [])]
    return other_kids.get(i, [])


_xml = None


def link_text(cid, href):
    """The text of the <ref href=...> inside the citing provision, from the Title 26 XML."""
    global _xml
    if _xml is None:
        _xml = (out.parent / "xml" / "usc26.xml").read_text(encoding="utf-8")
    i = _xml.find('identifier="' + cid + '"')
    m = re.search(r'<ref href="' + re.escape(href) + r'"[^>]*>(.*?)</ref>', _xml[i:i + 20000])
    return re.sub(r"<[^>]+>", "", m.group(1)) if m else "?"


def header(title, extra):
    return [f"import TaxCode.Certs.Basic", "", "/-!", f"# {title}", "",
            f"Generated by `tools/taxcode/certs.py` from the OLRC USLM XML of release point {RELEASE} and the triage in",
            "`triage.csv`; do not edit by hand. " + extra, "-/", "",
            "-- the evidence is long literal text and long lists: the kernel's evaluation needs deep recursion",
            "set_option maxRecDepth 200000", "set_option maxHeartbeats 4000000", "", "namespace TaxCode.Certs", ""]


refs, dups, parens = [], [], []
seen = set()
for r in rows:
    f = FK[(r["class"], r["citing"], r["target"])]
    cls, cid, tid = f["class"], f["citing"], f["target"]
    name = lname(r["citing"]) + ("__" + lname(r["target"]) if cls not in ("duplicate-designation", "unbalanced-parentheses") else "")
    base = name
    n = 2
    while name in seen:
        name = f"{base}_{n}"
        n += 1
    seen.add(name)
    meant = r["meant"].strip()
    law = f"; in the united-states-law history the words first appear with: {r['law']} ({r['date']})" if r.get("law") else ""
    common = [f"{r['citing']}: {r['reason']}", "",
              f"Meant: {meant}." if meant else "Meant: not determinable from the text.",
              "", f"Source: OLRC USLM XML, Title 26, release point {RELEASE}, `{cid}`{law}."]
    if cls == "unbalanced-parentheses":
        p = byid[cid]
        t = p["text"]
        d = 0; low = 0; q = 0
        for ch in t:
            if ch == "“": q += 1
            elif ch == "”": q -= 1
            elif q > 0: pass
            elif ch == "(": d += 1
            elif ch == ")": d -= 1; low = min(low, d)
        parens.append("\n".join([
            f"namespace {name}", "",
            doc(common + ["", "`chars` is the provision's own words (hyperlinked citations shown as ⟦REF⟧, footnote marks as †):",
                          "", t]),
            f"def chars : List Char := {chars(t)}",
            "def text : String := String.ofList chars", "",
            f"/-- The count over the words: final depth {d}, lowest depth {low} (balanced words give `(0, 0)`). -/",
            f"theorem count : parenDepth chars = ({d}, {low}) := by decide +kernel", "",
            "/-- The parentheses do not balance. -/",
            "theorem unbalanced : ¬ Balanced chars := by decide +kernel", "",
            f"end {name}", ""]))
    elif cls == "duplicate-designation":
        p = byid[cid]
        # every element under the same parent element, in document order
        sib = [c for c in P if c.get("parentElement") == p.get("parentElement") and c.get("parentElement")]
        des = p["num"]
        kidlist = ", ".join(f"({lit(c['num'] or '')}, {lit(re.sub(r'^[0-9]+ (So in original[^.]*\\.[^.]*\\. )?', '', c['heading'])[:60] or c['text'][:60])})" for c in sib)
        cnt = sum(1 for c in sib if c["num"] == des)
        dups.append("\n".join([
            f"namespace {name}", "",
            doc(common + ["", f"`children` is every subdivision of `{p['parent']}`, in document order, as (designation, heading or first words)."]),
            f"def parent : String := {lit(p['parent'])}",
            f"def children : List (String × String) := [{kidlist}]", "",
            f"/-- The designation ({des}) is used {cnt} times among the subdivisions of {cite(p['parent'])}. -/",
            f"theorem duplicated : (children.map Prod.fst).count {lit(des)} = {cnt} := by decide +kernel", "",
            f"theorem not_unique : ¬ (children.map Prod.fst).Nodup := by decide +kernel", "",
            f"end {name}", ""]))
    else:
        p = byid[cid]
        text = words_of(p)
        if cls in ("dangling-ref", "ref-to-inactive"):
            # a hyperlink: the evidence is the link's own text in the XML, and the marker that stands for it
            link = link_text(cid, tid)
            phrase = "⟦REF⟧"
            common[0] += f" (the hyperlink reads “{link}” and points to `{tid}`)"
        else:
            phrase = f["detail"].split(" — ")[0]
        i = text.find(phrase)
        if i < 0:
            raise SystemExit(f"words not found in {cid}: {phrase!r}")
        parts = tid.split("/")
        anc = None
        for cut in range(len(parts) - 1, 4, -1):
            a = "/".join(parts[:cut])
            if exists(a):
                anc = a
                break
        if anc is None:  # no such section in the title at all: the container is the title
            anc = "/".join(parts[:4])
            other_status.setdefault(anc, "in-force")
        lines = [f"namespace {name}", "",
                 doc(common + ["", f"The citing provision's own words are `before ++ words ++ after`; `cited` is the path the words name ({cite(tid)}):",
                               "", text]),
                 f"def citing : String := {lit(cid)}",
                 f"def cited : String := {lit(tid)}",
                 f"def words : List Char := {chars(phrase)}",
                 f"def before : List Char := {chars(text[:i])}",
                 f"def after : List Char := {chars(text[i + len(phrase):])}",
                 "/-- The citing provision's words, in full. -/",
                 "def text : String := String.ofList (before ++ words ++ after)", ""]
        if cls == "wrong-level-word" or (exists(tid) and status_of(tid) == "in-force"):
            # wrong level: the named level lacks the designation, the other level has it
            slip = re.search(r"the (\w+) (/us/usc/\S+) exists", f["detail"])
            other = slip.group(2)
            named_base = "/".join(tid.split("/")[:-1])
            des = tid.rsplit("/", 1)[1]
            nk = [c for c, _ in children(named_base)] if exists(named_base) else []
            ok = [c for c, _ in children(other.rsplit("/", 1)[0])]
            lines += [f"/-- Designations directly under {cite(named_base) if exists(named_base) else named_base + ' (which does not exist)'}, the {f['detail'].split()[0]} the words point to. -/",
                      f"def namedLevel : List String := [{', '.join(lit(x) for x in nk)}]",
                      f"/-- Designations under {cite(other.rsplit('/', 1)[0])}, one level away. -/",
                      f"def otherLevel : List String := [{', '.join(lit(x) for x in ok)}]", "",
                      f"/-- ({des}) is not at the level the word names, but is at the other level. -/",
                      f"theorem wrong_level : {lit(des)} ∉ namedLevel ∧ {lit(des)} ∈ otherLevel := by decide +kernel", ""]
        else:
            nxt = parts[len(anc.split("/"))]
            ks = children(anc)
            st = status_of(anc)
            lines += [f"/-- The deepest provision on the cited path that exists: {cite(anc)} ({st}). -/",
                      f"def container : String := {lit(anc)}",
                      f"def containerStatus : String := {lit(st)}",
                      f"/-- Every subdivision of the container in the release point, with its status. -/",
                      f"def subdivisions : List (String × String) := [{', '.join(f'({lit(a)}, {lit(b)})' for a, b in ks)}]", ""]
            if (nxt, ) in [(a,) for a, b in ks]:
                lines += [f"/-- The cited designation ({nxt}) is present but not in force. -/",
                          f"theorem not_in_force : (subdivisions.lookup {lit(nxt)}).isSome ∧ subdivisions.lookup {lit(nxt)} ≠ some \"in-force\" := by decide +kernel", ""]
            else:
                lines += [f"/-- The container has no subdivision ({nxt}): the cited path {cite(tid)} names nothing. -/",
                          f"theorem missing : {lit(nxt)} ∉ subdivisions.map Prod.fst := by decide +kernel", ""]
                if st != "in-force":
                    lines += ["/-- And the container itself is not in force. -/",
                              "theorem container_not_in_force : containerStatus ≠ \"in-force\" := by decide +kernel", ""]
        lines += [f"end {name}", ""]
        refs.append("\n".join(lines))

certs = lp / "TaxCode" / "Certs"
certs.mkdir(parents=True, exist_ok=True)
files = {
    "References": ("Certificates: references to provisions that do not exist or are not in force",
                   "Each certificate shows the cited words in the citing provision and the complete list of designations where they point.", refs),
    "Duplicates": ("Certificates: duplicate designations",
                   "Each certificate lists every subdivision under the parent element and counts the repeated designation.", dups),
    "Parens": ("Certificates: unbalanced parentheses",
               "Each certificate evaluates the parenthesis count (`parenDepth`, as in `TaxCode.parenDepth`) over the provision's words.", parens),
}
for fname, (title, extra, items) in files.items():
    body = header(title, extra) + items + ["end TaxCode.Certs", ""]
    (certs / f"{fname}.lean").write_text("\n".join(body), encoding="utf-8", newline="\n")
(certs / "All.lean").write_text("\n".join([
    "import TaxCode.Certs.References", "import TaxCode.Certs.Duplicates", "import TaxCode.Certs.Parens", "",
    "/-!", "# All certificates for confirmed drafting faults in Title 26", "",
    f"{len(refs)} reference faults, {len(dups)} duplicate designations, {len(parens)} unbalanced parentheses",
    f"(release point {RELEASE}). Generated by `tools/taxcode/certs.py`.", "-/", ""]), encoding="utf-8", newline="\n")
print("certificates:", len(refs), "references,", len(dups), "duplicates,", len(parens), "parentheses")
