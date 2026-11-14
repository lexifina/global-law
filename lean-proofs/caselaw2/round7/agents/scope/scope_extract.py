"""Round 7, track B2 (agent `scope`), step 1: the sentence around every candidate row's quote, from the git text.

    python -X utf8 round7/agents/scope/scope_extract.py [--base round6/history/stage/final2] [--procs 22]

Candidates (treatments rows of kind overruled / abrogated / disapproved / recededFrom):
  P  explicit = 1, scope partialUnknown or unknown            (the rule of DESIGN7 section 6 rewrites these)
  I  explicit = 1, scope issues:...                             (measured; rewritten only in the narrow case)
  W  witness rows (treatment_witness.tsv), any scope but all    (counts only)
For each: the text whose certificate it is (by_node for P / I, the witness node W for W) at git HEAD of its corpus
repo (round5/recog/recog_common.git_texts), checked against the row's text_sha and its quote at its offsets; the
sentence that holds the quote (reader/common.sentence_span on the unwrapped view of a hard-wrapped text).
Nothing here reads any answer key. Output: sentences.jsonl.gz in this folder (one object per candidate row).
"""
import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import time
from multiprocessing import Pool

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round5", "recog"))
import recog_common as R  # noqa: E402
RC = R.RC

NEG4 = ("overruled", "abrogated", "disapproved", "recededFrom")
NL = "\n"
ABBR2 = RC.ABBR | set("""Com Ins Mut Acc Indus Ind Nat Natl Mfg Ry Assur Bd Cty Twp Sch Educ Hosp Univ Dev Fin Sav
    Ass Assoc Bldg Elec Tel Tp Gov Govt Admr Adm Exr Ex Ref Rel Syl Pl Vol Op Ops Cf Ct Cts Cty Hwy Mun Corp Ltd Inc
    Pub Ann Supp Super Misc Prob Fam Juv Crim Civ Cnty Dept Bros Jr Sr Mr Mrs Dr St Mt Ft Sts Pp Tit Subd Par Para
    Ord Res Reg Regs Ch Sec Secs Cl Art Arts Amdt Amend Const""".split())


LOWER_ABBR = set("""rel seq al ibid id cf viz vs ex et op cit pp ff nn no ch sec secs subd cl art para ann supp cert den
    aff rev rehg reh mem dist app ct cir esq inc co corp ltd bros ry assn"""
                 .split())


def _end_at(s, i):
    """Is s[i] ('.', '!', '?') the end of a sentence? Conservative: a word of an abbreviation list, any word of at
    most two letters, a capitalised word of at most four letters, or a token with an inner period (U.S., So.2d)
    before a period never ends a sentence, and the next text must start with a capital letter, an opening quote
    or bracket, or be a paragraph break. (A sentence found too long only makes the rule keep a row as it is.)"""
    n = len(s)
    j = i + 1
    while j < n and s[j] in "”\"’')]":
        j += 1
    k = j
    while k < n and s[k] in " \t":
        k += 1
    if k >= n:
        return True
    if s[k] != NL and (k == j or not (s[k].isupper() or s[k] in "“\"([")):
        return False
    if s[i] in "!?":
        return True
    # the next token is itself an abbreviation ("Teleg. Co.", "Ins. Co. v.", "R. Co."): a caption goes on
    if re.match(r"(?:[A-Z][A-Za-z']{0,5}\.|&|v\.)", s[k:k + 8]):
        return False
    w = re.search(r"([A-Za-z0-9’'.&\-]+)$", s[max(0, i - 25):i])
    if w:
        tok = w.group(1)
        word = re.split(r"[.\-’']", tok)[-1]
        if ("." in tok or word in ABBR2 or word.lower() in LOWER_ABBR or len(word) <= 2
                or (word[:1].isupper() and len(word) <= 4)):
            return False
        # "Henderlingv." (an OCR-glued "v.") before a case name and its citation
        if re.search(r"[a-z]v$", word) and re.match(r"\s*[A-Z][A-Za-z.'&\- ]{0,40}, (?:supra|\d)", s[i + 1:i + 60]):
            return False
    return True


def sentence_span2(s, a, b, back=2000, fwd=1200):
    """(a0, a1): the sentence that holds s[a:b]. A line break ends a sentence only when the line ends with a
    sentence end (above) or a colon; a lone line break elsewhere is a page or wrap break inside the sentence."""
    def is_end(i):
        c = s[i]
        if c in ".!?":
            return _end_at(s, i)
        if c == NL:
            p = i - 1
            while p >= 0 and s[p] in " \t":
                p -= 1
            if p < 0:
                return True
            if s[p] == NL:
                q = p - 1
                while q >= 0 and s[q] in " \t\n":
                    q -= 1
                return q < 0 or s[q] in ".!?:”\"’)" and (s[q] != "." or _end_at(s, q))
            if s[p] == ":":
                return True
            if s[p] in ".!?":
                return _end_at(s, p)
            if s[p] in "”\"’')":
                q = p
                while q >= 0 and s[q] in "”\"’')":
                    q -= 1
                return q >= 0 and s[q] in ".!?" and _end_at(s, q)
            return False
        return False
    a0 = max(0, a - back)
    cut_back = a0 > 0
    for i in range(a - 1, max(0, a - back) - 1, -1):
        if is_end(i):
            a0 = i + 1
            cut_back = False
            break
    while a0 < a and s[a0] in " \n\t”\"’')":
        a0 += 1
    a1 = min(len(s), b + fwd)
    cut_fwd = a1 < len(s)
    for i in range(max(a, b - 1), min(len(s), b + fwd)):
        if is_end(i):
            a1 = i + 1 if s[i] != NL else i
            cut_fwd = False
            break
    cut = cut_back or cut_fwd
    return a0, a1, cut


def select(base):
    wit = {}
    for p in R.read_rows(os.path.join(base, "treatment_witness.tsv"), 2):
        wit.setdefault(p[0], int(p[1]))
    cand = []
    for p in R.read_rows(os.path.join(base, "treatments.tsv"), 16):
        if p[4] not in NEG4:
            continue
        sc = p[5]
        if p[0] in wit:
            if sc != "all":
                cand.append(("W", p, wit[p[0]]))
        elif p[7] == "1":
            if sc in ("partialUnknown", "unknown"):
                cand.append(("P", p, int(p[1])))
            elif sc.startswith("issues:"):
                cand.append(("I", p, int(p[1])))
    return cand


def work(job):
    repo, items = job
    paths = sorted({it["path"] for it in items})
    texts = R.git_texts(repo, paths)
    cache = {}
    out = []
    for it in items:
        raw = texts.get(it["path"])
        o = {k: it[k] for k in ("id", "cls", "node")}
        if raw is None:
            o["err"] = "noText"
            out.append(o)
            continue
        if it["path"] not in cache:
            text = R.decode(raw)
            b0 = R.body_start(text)
            hw = RC.hard_wrapped(text, b0)
            view = RC.unwrap_view(text, b0) if hw else text
            cache = {it["path"]: (hashlib.sha1(raw).hexdigest(), text, view, hw)}
        sha, text, view, hw = cache[it["path"]]
        s, e = it["start"], it["end"]
        if sha != it["sha"]:
            o["err"] = "shaMismatch"
        elif R.clean(text[s:e]) != it["quote"]:
            o["err"] = "quoteMismatch"
        if "err" in o:
            out.append(o)
            continue
        a0, a1, cut = sentence_span2(view, s, e)
        o.update(hw=int(hw), s0=a0, s1=a1, cut=int(cut), sent=R.clean(view[a0:a1]),
                 pre=R.clean(view[max(0, a0 - 300):a0]))
        out.append(o)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.path.join(C2, "round6", "history", "stage", "final2"))
    ap.add_argument("--procs", type=int, default=22)
    ap.add_argument("--out", default=os.path.join(HERE, "sentences.jsonl.gz"))
    a = ap.parse_args()
    t0 = time.time()
    cand = select(a.base)
    R.log("candidates: %d (P %d, I %d, W %d)" % (len(cand), sum(c[0] == "P" for c in cand),
                                                 sum(c[0] == "I" for c in cand), sum(c[0] == "W" for c in cand)))
    info = R.nodes_info({c[2] for c in cand})
    R.log("nodes: %d of %d (%.0fs)" % (len(info), len({c[2] for c in cand}), time.time() - t0))
    jobs = {}
    missing = []
    for cls, p, node in cand:
        if node not in info:
            missing.append({"id": p[0], "cls": cls, "node": node, "err": "noNode"})
            continue
        repo, path = info[node][0], info[node][1]
        jobs.setdefault(repo, []).append({"id": p[0], "cls": cls, "node": node, "path": path, "sha": p[8],
                                          "start": int(p[9]), "end": int(p[10]), "quote": p[11]})
    for v in jobs.values():
        v.sort(key=lambda it: it["path"])
    res = list(missing)
    with Pool(a.procs) as pool:
        for out in pool.imap_unordered(work, sorted(jobs.items(), key=lambda kv: -len(kv[1]))):
            res.extend(out)
    res.sort(key=lambda o: o["id"])
    with gzip.open(a.out, "wt", encoding="utf-8", newline="\n") as f:
        for o in res:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    errs = {}
    for o in res:
        if "err" in o:
            errs[o["err"]] = errs.get(o["err"], 0) + 1
    R.log("wrote %d rows, errors %s (%.0fs)" % (len(res), errs, time.time() - t0))


if __name__ == "__main__":
    main()
