"""The record: versions.tsv, blobs from usc-full.git, and a section's markdown as lines with designation paths."""
from __future__ import annotations

import csv
import re
import subprocess
from collections import defaultdict
from pathlib import Path

WORK = Path.home() / "Documents/us-caselaw-lean-work"
GITDIR = WORK / "usc-full.git"
VERSIONS = WORK / "usc/versions.tsv"


def load_versions():
    """path -> list of (commit, kind, label, day, blob) in record order; label -> {path: [index, ...]}."""
    by_path = defaultdict(list)
    by_law = defaultdict(lambda: defaultdict(list))
    with open(VERSIONS, encoding="utf-8") as f:
        for r in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            path, commit, kind, label, day, blob = r[:6]
            by_path[path].append((commit, kind, label, int(day), blob))
    for path, vs in by_path.items():
        vs.sort(key=lambda v: v[3])  # stable: record order within a day
        for i, v in enumerate(vs):
            if v[1] == "law":
                by_law[v[2]][path].append(i)
    return by_path, by_law


class Blobs:
    """git cat-file --batch reader."""

    def __init__(self):
        self.p = subprocess.Popen(["git", "--git-dir", str(GITDIR), "cat-file", "--batch"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.cache = {}

    def get(self, sha: str) -> str:
        if sha in self.cache:
            return self.cache[sha]
        self.p.stdin.write((sha + "\n").encode())
        self.p.stdin.flush()
        head = self.p.stdout.readline().decode().split()
        if len(head) < 3 or head[1] == "missing":
            return ""
        n = int(head[2])
        data = self.p.stdout.read(n)
        self.p.stdout.read(1)
        t = data.decode("utf-8")
        if len(self.cache) > 4000:
            self.cache.clear()
        self.cache[sha] = t
        return t


# ---------------------------------------------------------------- designations -> paths

ROMAN_L = re.compile(r"^(?=[ivxlc]+$)c{0,3}(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$")
LINE = re.compile(r"^( *)- (.*)$")
DES = re.compile(r"^\(([0-9]+[A-Za-z0-9\-]*|[a-z]{1,3}|[A-Z]{1,3}|[a-z]+[0-9]*|[A-Z]+[0-9]*)\)\s?")


def _roman_val(s):
    vals = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
    s = s.lower()
    t = 0
    for a, b in zip(s, s[1:] + " "):
        v = vals[a]
        t += -v if b != " " and vals.get(b, 0) > v else v
    return t


def _is_roman(d):
    return d != "" and bool(ROMAN_L.match(d.lower())) and not set(d.lower()) & set("lc")


def _letter_val(d):
    # a..z, aa, bb, ... (doubled letters after z)
    if len(d) == 1:
        return ord(d.lower()) - 96
    if d == d[0] * len(d):
        return 26 * (len(d) - 1) + ord(d[0].lower()) - 96
    return None


def candidates(d):
    """Levels a designation could be at: 1 (a), 2 (1), 3 (A), 4 (i), 5 (I), 6 (aa), 7 (AA)."""
    out = []
    if d[0].isdigit():
        return [2]
    if d.islower():
        if _letter_val(d) is not None and len(d) == 1:
            out.append(1)
        if _is_roman(d):
            out.append(4)
        if len(d) >= 2 and d == d[0] * len(d):
            out += [6, 1]
        if not out:
            out.append(1)
    elif d.isupper():
        if len(d) == 1:
            out.append(3)
        if _is_roman(d):
            out.append(5)
        if len(d) >= 2 and d == d[0] * len(d):
            out += [7, 3]
        if not out:
            out.append(3)
    else:
        out.append(1 if d[0].islower() else 3)
    return out


def _succ(prev, d, level):
    """d directly follows prev at this level (allowing a few skipped)."""
    if prev is None:
        return False
    if level in (4, 5):
        if not (_is_roman(prev) and _is_roman(d)):
            return False
        return 0 < _roman_val(d) - _roman_val(prev) <= 3
    a, b = _letter_val(prev), _letter_val(d)
    if a is None or b is None:
        return False
    return 0 < b - a <= 3


def _first(d, level):
    return (level in (4, 5) and d.lower() == "i") or (level in (1, 3) and d.lower() == "a") or (level in (6, 7) and d.lower() == "aa") or (level == 2 and d == "1")


def _diff(prev, d, level):
    if level in (4, 5):
        return _roman_val(d) - _roman_val(prev)
    return _letter_val(d) - _letter_val(prev)


def pick_level(d, stack, depth_hint=None, level_depth=None):
    c = candidates(d)
    if len(c) == 1:
        return c[0]
    # Prefer the level where d continues the current sequence; on a tie, the one printed at this indent, then the
    # immediate successor, then the deeper level.
    ld0 = level_depth or {}
    lo = min(c)
    if (depth_hint is not None and lo in ld0 and depth_hint > ld0[lo] and any(x > lo for x in c)
            and not (lo in stack and _succ(stack[lo], d, lo) and _diff(stack[lo], d, lo) == 1
                     and not any(lo < x <= (max(stack) if stack else 0) + 1 for x in c))):
        c = [x for x in c if x != min(c)]   # printed deeper than the current top-kind line
        if len(c) == 1:
            return c[0]
    ok = [lv for lv in c if lv in stack and _succ(stack[lv], d, lv)]
    if ok:
        ld = level_depth or {}
        ok.sort(key=lambda lv: (ld.get(lv) == depth_hint, _diff(stack[lv], d, lv) == 1, lv), reverse=True)
        return ok[0]
    deepest = max(stack) if stack else 0
    ld = level_depth or {}
    if depth_hint is not None and len(c) > 1 and min(c) in ld and depth_hint > ld[min(c)]:
        # printed deeper than the current top-kind line: the deeper reading (a clause, not a subsection)
        return max(c) if max(c) <= deepest + 1 else sorted(c)[1]
    for lv in c:
        if _first(d, lv) and lv == deepest + 1:
            return lv
    for lv in c:
        if _first(d, lv) and lv > (min(c)):
            if deepest >= lv - 1:
                return lv
    return c[0]


def score_level(d, stack, dd):
    """Pick d's level: does it continue a list at that level, or start a new deeper one, and does the line's printed
    depth agree (the record prints a line at the depth of its last designation)."""
    cands = candidates(d)
    levels = sorted(stack)
    if len(cands) == 1:
        lv = cands[0]
        # continuing a nested restarted list (a pseudo level holding the same kind of designation)
        for x in sorted((k for k in stack if k != int(k)), reverse=True):
            if candidates(stack[x]) == cands and _succ(stack[x], d, lv):
                return x
        if lv in stack and lv < levels[-1] and not _succ(stack[lv], d, lv) and _first(d, lv):
            # A list that restarts below a deeper one ("(ii) ...— (A) ... (B) ..." under a clause): nest it.
            return levels[-1] + 0.5
        return lv
    top = levels[-1] if levels else 0
    deeper = [x for x in cands if x > top]
    best = None
    for lv in cands:
        sc = 0
        if lv in stack:
            if _succ(stack[lv], d, lv):
                sc += 3 if _diff(stack[lv], d, lv) == 1 else 2
            else:
                sc -= 5
        elif _first(d, lv) and lv > top:
            sc += 2
        else:
            sc -= 2
        if (0 <= dd < len(levels) and levels[dd] == lv) or (dd == len(levels) and deeper and lv == min(deeper)):
            sc += 2
        key = (sc, -lv)
        if best is None or key > best[0]:
            best = (key, lv)
    return best[1]


def parse_section(md: str):
    """Lines of a section as (path, text); path is the concatenated designations ("(c)(1)(A)"). The heading line
    ("# 18 U.S.C. § 924. Penalties") gets path "#"."""
    out = []
    stack = {}       # level -> designation
    level_depth = {}  # level -> indent depth of the line that set it
    by_depth = {}    # indent depth -> path of the last line there
    for raw in md.splitlines():
        if raw.startswith("# "):
            out.append(("#", raw[2:].strip()))
            continue
        m = LINE.match(raw)
        if not m:
            if raw.strip():
                prev = out[-1][0] if out else ""
                out.append(("" if prev == "#" else prev, raw.strip()))
            continue
        depth = len(m.group(1)) // 2
        text = m.group(2).strip()
        rest = text
        des = []
        while True:
            dm = DES.match(rest)
            if not dm:
                break
            des.append(dm.group(1))
            rest = rest[dm.end():]
            if dm.group(0).endswith(" ") or not rest.startswith("("):
                break
        if des:
            first = True
            for n_d, d in enumerate(des):
                # The record prints a line at the depth of its last designation, so designation n of k sits at
                # depth - (k - 1 - n). Use that depth first, when it agrees with what kind of designation d is.
                dd = depth - (len(des) - 1 - n_d)
                lv = score_level(d, stack, dd)
                if not first and stack and lv <= max(stack):
                    # combined designations go deeper: "(c)(1)(A)"
                    deeper = [x for x in candidates(d) if x > max(stack)]
                    lv = deeper[0] if deeper else max(stack) + 1
                for k in [k for k in stack if k >= lv]:
                    del stack[k]
                stack[lv] = d
                level_depth[lv] = depth
                first = False
            path = "".join(f"({stack[k]})" for k in sorted(stack))
            by_depth[depth] = path
            for k in [k for k in by_depth if k > depth]:
                del by_depth[k]
        else:
            ds = [k for k in by_depth if k <= depth]
            path = by_depth[max(ds)] if ds else ""
        out.append((path, text))
    return out
