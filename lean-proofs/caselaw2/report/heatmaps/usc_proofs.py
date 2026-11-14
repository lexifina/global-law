"""The evidence behind each defect on the "US Code vulnerabilities introduced, by day" calendar.

Called by build_usc_days.py, which collects the defects; this module reads the record's own text for each one, so a
reader can check it instead of taking the label on trust:

  dangling reference   the citing section as it read that day, with the words that make the reference marked; the
                       cited section as it read that day (or the fact that the record has no such file), and for a
                       missing subdivision the subdivisions it does have; the version before, when a law broke it;
                       the version that ended it, if any.
  amending instruction the Act's own words; the section as it read before the Act; whether the words are anywhere
                       in it, and the closest words it does have.
  duplicate            the section's lines that carry the same designation under the same parent.

Every text is pinned to a commit of github.com/lexifina/united-states-law (the same history as usc-full.git).
Standard library only.
"""
import collections
import difflib
import re
import subprocess
import threading

EXCERPT = 260      # characters either side of a marked reference
LINE_MAX = 700     # longest line quoted
SCOPE_MAX = 1800   # longest quoted scope of an amendment
NEAR_SCAN = 120_000


class Git:
    """git cat-file --batch, one blob at a time."""

    def __init__(self, git_dir):
        self.p = subprocess.Popen(["git", "--git-dir", str(git_dir), "cat-file", "--batch"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.lock = threading.Lock()
        self.cache = collections.OrderedDict()

    def blob(self, sha):
        if not sha:
            return ""
        if sha in self.cache:
            self.cache.move_to_end(sha)
            return self.cache[sha]
        with self.lock:
            self.p.stdin.write((sha + "\n").encode())
            self.p.stdin.flush()
            head = self.p.stdout.readline().split()
            if len(head) < 3 or head[1] != b"blob":
                raise SystemExit(f"blob {sha} not in the record")
            t = self.p.stdout.read(int(head[2])).decode("utf-8", "replace")
            self.p.stdout.read(1)
        self.cache[sha] = t
        if len(self.cache) > 400:
            self.cache.popitem(last=False)
        return t


def load_versions(path):
    """path -> [(day, label, commit, blob, short)] in record order (the order versions.tsv lists them)."""
    vers = collections.defaultdict(list)
    for i, l in enumerate(open(path, encoding="utf-8")):
        f = l.rstrip("\n").split("\t")
        vers[f[0]].append((int(f[4]), f[3], f[1], f[5], f[6] if len(f) > 6 else "", i))
    for p in vers:
        vers[p].sort(key=lambda v: (v[0], v[5]))
    return vers


def at(vs, day):
    """The version in force on `day` (the last one dated on or before it), or None."""
    best = None
    for v in vs:
        if v[0] <= day:
            best = v
        else:
            break
    return best


def before(vs, v):
    i = vs.index(v)
    return vs[i - 1] if i > 0 else None


def pin(v):
    return {"c": v[2], "d": v[0], "by": v[1]}


def squash(s):
    return " ".join(s.split())


def clip_around(text, a, b, width=EXCERPT):
    """text with [a, b) kept whole and up to `width` characters either side, cut at word breaks."""
    lo = max(0, a - width)
    hi = min(len(text), b + width)
    if lo > 0:
        sp = text.find(" ", lo)
        lo = sp + 1 if 0 <= sp < a else lo
    if hi < len(text):
        sp = text.rfind(" ", b, hi)
        hi = sp if sp > b else hi
    pre = "…" if lo > 0 else ""
    post = "…" if hi < len(text) else ""
    return pre + text[lo:hi] + post, len(pre) + a - lo, len(pre) + b - lo


def clip(s, n):
    s = squash(s)
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def heading(text):
    first = text.split("\n", 1)[0]
    return first[2:].strip() if first.startswith("# ") else first.strip()


def first_para(text, n=420):
    paras = [p for p in text.split("\n\n")[1:] if p.strip()]
    return clip(paras[0], n) if paras else ""


class Proofs:
    def __init__(self, git_dir, versions_path, xr):
        self.git = Git(git_dir)
        self.vers = load_versions(versions_path)
        self.xr = xr  # the usc_xrefs module
        self.analysed = {}
        self.stats = collections.Counter()

    def analyse(self, path, blob, day):
        k = (path, blob)
        if k not in self.analysed:
            self.analysed[k] = self.xr.analyse(path, self.git.blob(blob), day)
            if len(self.analysed) > 2000:
                self.analysed.pop(next(iter(self.analysed)))
        return self.analysed[k]

    # ---- dangling references ----------------------------------------------------------------------------------
    def xref(self, src, tgt, path, day, ended, until, cls, cause):
        pdes = tuple(path.split(".")) if path else ()
        out = {}
        sv = at(self.vers.get(src, []), day)
        if sv is None or not sv[3]:
            raise SystemExit(f"no text of {src} on {day}")
        out["s"] = pin(sv)
        out["s"].update(self.quote_ref(src, sv, tgt, pdes))
        if not self.analyse(src, sv[3], sv[0])[0]:
            # the citing section is itself a stub ("Repealed", "Transferred", ...): the reference is in the editors' note
            out["s"]["stub"] = heading(self.git.blob(sv[3]))
            self.stats["xref_in_stub"] += 1
        out["t"] = self.target(tgt, pdes, day, cls == "broken")
        if ended:
            ev = at(self.vers.get(src if ended == 2 else tgt, []), until)
            if ev is not None and ev[0] == until:
                e = pin(ev)
                e["what"] = "source" if ended == 2 else "target"
                if ended == 2 and ev[3]:
                    e["head"] = heading(self.git.blob(ev[3]))
                elif ended == 1 and ev[3]:
                    e["head"] = heading(self.git.blob(ev[3]))
                    if pdes:
                        e["have"] = self.has_path(tgt, ev, pdes)
                out["e"] = e
            else:
                self.stats["xref_end_unpinned"] += 1
        return out

    def quote_ref(self, src, sv, tgt, pdes):
        """The line of the citing section that makes the reference, the reference marked."""
        text = self.git.blob(sv[3])
        lines = text.split("\n")
        title = int(src.split("/")[0].split("-")[1])
        want = {tgt, tgt.lower()}
        best = None
        for ln, m, here, new in self.xr.tree(lines):
            body = m.group(5) if m else lines[ln]
            if ln == 0 and lines[0].startswith("# "):
                continue
            off = len(lines[ln]) - len(body)
            for kind, t, p, a, b in self.xr.refs_in_line(body, here, title, sv[0], src):
                cands = {t}
                for k in self.xr.norm_ref(t, p, self.vers_x):
                    cands.add(k[0])
                if (cands & want or {c.lower() for c in cands} & want) and tuple(p) == pdes:
                    best = (ln, off + a, off + b)
                    break
                if best is None and (cands & want or {c.lower() for c in cands} & want):
                    best = (ln, off + a, off + b, "path")
            if best and len(best) == 3:
                break
        if not best:
            self.stats["xref_ref_not_located"] += 1
            return {"line": clip(text, LINE_MAX), "hl": None}
        ln, a, b = best[:3]
        line = lines[ln].lstrip()
        if line.startswith("- "):
            line = line[2:]
        shift = len(lines[ln]) - len(line)
        q, qa, qb = clip_around(line, a - shift, b - shift)
        if len(best) == 4:
            self.stats["xref_ref_path_unmatched"] += 1
        return {"line": q, "hl": [qa, qb], "ln": ln + 1}

    def has_path(self, tgt, v, pdes):
        live, hard, soft, dead = self.analyse(tgt, v[3], v[0])[:4]
        return pdes in hard or pdes in soft

    def target(self, tgt, pdes, day, broken):
        vs = self.vers.get(tgt)
        if not vs:
            # no file of that name in any version: show the sections of that title nearest the name
            self.stats["t_never"] += 1
            return {"st": "never", "near": self.neighbours(tgt, day)}
        v = at(vs, day)
        if v is None:
            return {"st": "notyet", "first": pin(vs[0]), "near": self.neighbours(tgt, day)}
        if not v[3]:
            o = {"st": "gone", "gone": pin(v)}
            last = next((x for x in reversed(vs[: vs.index(v)]) if x[3]), None)
            if last:
                o["last"] = pin(last)
                o["last"]["head"] = heading(self.git.blob(last[3]))
            later = next((x for x in vs[vs.index(v) + 1:] if x[3]), None)
            if later:
                o["back"] = pin(later)
            return o
        text = self.git.blob(v[3])
        live, hard, soft, dead = self.analyse(tgt, v[3], v[0])[:4]
        o = pin(v)
        o["head"] = heading(text)
        if not live:
            o["st"] = "dead"
            o["para"] = first_para(text)
        else:
            o["st"] = "live"
        if broken:
            pv = before(vs, v)
            if pv and pv[3]:
                o["prev"] = pin(pv)
                o["prev"]["head"] = heading(self.git.blob(pv[3]))
        if live and pdes:
            have = hard | soft
            # the deepest part of the path the section has, and the designations it has there instead
            k = 0
            while k < len(pdes) and pdes[: k + 1] in have:
                k += 1
            o["found"] = "".join(f"({d})" for d in pdes[:k])
            kids = sorted({p[k] for p in hard if len(p) == k + 1 and p[:k] == pdes[:k]}, key=self.dkey)
            o["kids"] = kids[:60]
            o["nkids"] = len(kids)
            gone = sorted({p[k] for p in dead if len(p) == k + 1 and p[:k] == pdes[:k] and p[k] == pdes[k]})
            if gone:
                o["deadkid"] = True
                o["deadline"] = self.dead_line(text, pdes[: k + 1])
            if pdes in hard or pdes in soft:
                self.stats["t_live_has_path"] += 1
        return o

    @staticmethod
    def dkey(d):
        return (0, int(d), "") if d.isdigit() else (1, len(d), d)

    def dead_line(self, text, pdes):
        lines = text.split("\n")
        for ln, m, here, new in self.xr.tree(lines):
            if m and here == pdes:
                return clip(lines[ln].lstrip("- ").strip(), 300)
        return ""

    def neighbours(self, tgt, day):
        t, name = tgt.split("/")
        names = []
        for p, vs in self.titles.get(t, {}).items():
            v = at(vs, day)
            if v is not None and v[3]:
                names.append(p)
        if not names:
            return {"title": t, "n": 0, "near": []}
        key = self.nkey(name[:-3])
        names.sort(key=self.nkey)
        import bisect
        i = bisect.bisect_left([self.nkey(x) for x in names], key)
        near = names[max(0, i - 3): i + 3]
        return {"title": t, "n": len(names), "near": near}

    @staticmethod
    def nkey(s):
        m = re.match(r"(\d+)(.*)", s)
        return (int(m.group(1)), m.group(2).lower()) if m else (10 ** 9, s.lower())

    # ---- amending instructions --------------------------------------------------------------------------------
    def amend(self, title, section, path, words, wording, law, approved, op):
        p = f"title-{title}/{section}.md"
        vs = self.vers.get(p, [])
        # the section as it read before the Act, chosen as the checker chose it (amendments/tools/build_input.py): the
        # version just before the first version the record credits to this Act
        own = [i for i, x in enumerate(vs) if x[1] == law]
        v = vs[own[0] - 1] if own and own[0] > 0 else None
        o = {"w": wording, "law": law, "words": words}
        if v is None or not v[3]:
            o["st"] = "nosection"
            self.stats["amend_no_section"] += 1
            return o
        o.update(pin(v))
        text = self.git.blob(v[3])
        o["head"] = heading(text)
        lines = text.split("\n")
        pdes = tuple(re.findall(r"\(([^()]+)\)", path))
        scope_lines = []
        if pdes:
            for ln, m, here, new in self.xr.tree(lines):
                if here[: len(pdes)] == pdes:
                    scope_lines.append(lines[ln].strip())
        o["scoped"] = bool(scope_lines) or not pdes
        scope = "\n".join(scope_lines) if scope_lines else "\n".join(lines[1:])
        o["scope"] = clip(scope, SCOPE_MAX)
        w = norm(words.rstrip("…"))
        if not w:
            o["st"] = "nowords"
            return o
        rx = re.compile((r"(?<!\w)" if w[0].isalnum() else "") + re.escape(w) + (r"(?!\w)" if w[-1].isalnum() else ""))
        o["inscope"] = bool(rx.search(norm(scope)))
        found = [ln + 1 for ln in range(1, len(lines)) if rx.search(norm(lines[ln]))]
        o["insection"] = bool(found)
        if found:
            o["foundln"] = found[:5]
            o["foundline"] = clip(lines[found[0] - 1].strip(), 500)
            self.stats["amend_words_present_" + ("scope" if o["inscope"] else "section")] += 1
        near = closest(w, scope if scope_lines else "\n".join(lines[1:]))
        if near:
            o["near"] = near
        after = next((x for x in vs if x[1] == law and x[3]), None)
        if after:
            o["after"] = pin(after)
        return o

    # ---- duplicates -------------------------------------------------------------------------------------------
    def dup(self, path, v, parent, des):
        text = self.git.blob(v[3])
        lines = text.split("\n")
        par = tuple(parent.split(".")) if parent else ()
        hits = []
        want = par + (des,)
        for ln, m, here, new in self.xr.tree(lines):
            for j in range(len(new)):
                if here[: len(here) - len(new) + j + 1] == want:
                    hits.append([ln + 1, clip(lines[ln].strip()[2:] if lines[ln].strip().startswith("- ")
                                               else lines[ln].strip(), 360)])
                    break
        o = pin(v)
        o["head"] = heading(text)
        o["lines"] = hits[:8]
        o["n"] = len(hits)
        if len(hits) < 2:
            self.stats["dup_lines_lt2"] += 1
        pv = before(self.vers[path], v)
        if pv and pv[3]:
            o["prev"] = pin(pv)
        return o

    def prepare(self, xr_vers):
        self.vers_x = xr_vers
        self.titles = collections.defaultdict(dict)
        for p, vs in self.vers.items():
            t = p.split("/")[0]
            self.titles[t][p.split("/", 1)[1]] = vs


QUOTES = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "–": "-", "—": "-", " ": " "})


def norm(s):
    return " ".join(s.translate(QUOTES).replace("*", "").split()).lower()


def closest(words, text):
    """The run of the text's words most like `words` (same length give or take), if it is at least half alike."""
    tw = text.translate(QUOTES).replace("*", "").split()
    if len(" ".join(tw)) > NEAR_SCAN:
        tw = tw[: NEAR_SCAN // 6]
    ww = words.split()
    n = max(1, len(ww))
    best, bs = None, 0.0
    lw = [x.lower() for x in tw]
    target = " ".join(ww)
    sm = difflib.SequenceMatcher(autojunk=False)
    sm.set_seq2(target)
    for size in {n, max(1, n - 1), n + 1}:
        for i in range(0, max(1, len(tw) - size + 1)):
            cand = " ".join(lw[i:i + size])
            sm.set_seq1(cand)
            if sm.real_quick_ratio() < bs or sm.quick_ratio() < bs:
                continue
            r = sm.ratio()
            if r > bs:
                bs, best = r, " ".join(tw[i:i + size])
    if best is None or bs < 0.5:
        return None
    return {"text": clip(best, 300), "score": round(bs, 2)}
