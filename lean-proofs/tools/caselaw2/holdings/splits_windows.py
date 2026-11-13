"""Step 2 of the split pipeline: citation-context windows and a cheap interpretive-vs-passing score, per (subsection, decision).

    python splits_windows.py
reads data/holdings_work/split_citers.tsv, streams each citing decision's text from git, and writes
data/holdings_work/split_windows.jsonl: {key, nid, kind, date, sha, unpub, mentions, cues, splitcues, score,
    sents: [[start, end], ...]}  (the sentences of the windows around the court-part mentions, in text order, <= 36)
"""
import json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, text

OUT = os.path.join(text.WORK, "caselaw-lean-2", "data", "holdings_work")
_KEYS = None
INTERP = re.compile(r"\b(?:meaning of|interpret\w*|constru\w*|plain (?:language|meaning|text)|ambigu\w*|statutory (?:text|language)|"
                    r"Congress (?:intended|meant|used|chose)|the (?:term|phrase|words?) [\"“]|we hold|we conclude|textual\w*|"
                    r"legislative history|rule of lenity|Chevron|reads? (?:the statute|section|§)|applies only|does not apply|"
                    r"requires? (?:proof|a showing|that)|element)\b", re.I)
SPLITC = re.compile(r"\b(?:sister circuits?|other circuits?|circuits? (?:are|have been|is|remain) (?:split|divided)|circuit split|"
                    r"split (?:among|of authority|in the circuits)|disagree with the \w+ circuit|agree with the \w+(?: and \w+)? circuits?|"
                    r"we join|join(?:ing)? the \w+ circuits?|(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|D\.C\.|Federal) Circuit has held)\b", re.I)
UNPUB = re.compile(r"(?i)\b(?:not (?:recommended )?for (?:full[- ]text )?publication|unpublished|non-?precedential|"
                   r"summary order|NOT PRECEDENTIAL|Rule 47\.5|Fed\. ?R\. ?App\. ?P\. 32\.1)")


def keys():
    global _KEYS
    if _KEYS is None:
        _KEYS = {}
        for l in open(os.path.join(OUT, "split_citers.tsv"), encoding="utf-8"):
            k, n, kind, d = l.rstrip("\n").split("\t")
            _KEYS.setdefault(int(n), []).append((k, int(kind), int(d)))
    return _KEYS


def pats(key):
    t, rest = key.split(":", 1)
    s, sub = rest[:-1].split("(", 1)
    S, B = re.escape(s), re.escape(sub)
    full_sec = re.compile(r"\b" + t + r"\s*U\.?\s?S\.?\s?C\.?[A-Z.]*\s*,?\s*(?:§§?|[Ss]ec(?:tion|s?\.)?)?\s*" + S + r"(?![\w-])")
    full = re.compile(r"\b" + t + r"\s*U\.?\s?S\.?\s?C\.?[A-Z.]*\s*,?\s*(?:§§?|[Ss]ec(?:tion|s?\.)?)?\s*" + S + r"\s?\(\s?" + B + r"\s?\)")
    short = re.compile(r"(?:§§?|\b[Ss]ection|\b[Ss]ec\.)\s*" + S + r"\s?\(\s?" + B + r"\s?\)")
    return full_sec, full, short


def work(nid, raw):
    t = text.norm_text(raw)
    parts, form = core.court_parts(t)
    unpub = 1 if UNPUB.search(t[:6000]) else 0
    out = []
    for key, kind, d in keys().get(nid, []):
        full_sec, full, short = pats(key)
        if not full_sec.search(t):
            continue
        ms = []
        for b, e, part in parts:
            for p in (full, short):
                ms += [m.start() for m in p.finditer(t, b, e)]
        ms = sorted(set(ms))
        if not ms:
            continue
        sents = []
        for b, e, part in parts:
            sents += core.split_sentences(t, b, e)
        # sentences within the windows: the mention sentence, 4 before and 4 after
        idx = set()
        j = 0
        for m in ms:
            while j < len(sents) and sents[j][1] < m:
                j += 1
            if j < len(sents):
                for x in range(max(0, j - 4), min(len(sents), j + 5)):
                    idx.add(x)
        win = [sents[i] for i in sorted(idx) if sents[i][1] - sents[i][0] < 1500]
        wt = " ".join(t[a:z] for a, z in win)
        cues = len(INTERP.findall(wt))
        sc_ = len(SPLITC.findall(wt))
        score = 2 * min(cues, 8) + math.log2(1 + len(ms)) + 3 * min(sc_, 3) - (4 if unpub else 0)
        # keep at most 36 sentences, the ones nearest the mentions with cues first
        if len(win) > 36:
            ranked = sorted(win, key=lambda s: -(bool(INTERP.search(t[s[0]:s[1]])) + 2 * bool(SPLITC.search(t[s[0]:s[1]]))
                                               + any(s[0] <= m < s[1] for m in ms) * 2))
            win = sorted(ranked[:36])
        out.append({"key": key, "nid": nid, "kind": kind, "date": d, "sha": text.text_sha(raw), "unpub": unpub,
                    "mentions": len(ms), "cues": cues, "splitcues": sc_, "score": round(score, 2), "sents": win})
    return out or None


def main():
    nids = sorted(keys())
    print("decisions", len(nids), flush=True)
    n = 0
    with open(os.path.join(OUT, "split_windows.jsonl"), "w", encoding="utf-8", newline="\n") as fo:
        for res in text.map_nodes(nids, work, procs=6, chunk=3000):
            if isinstance(res, tuple):
                continue
            for r in res:
                fo.write(json.dumps(r) + "\n")
                n += 1
            if n % 20000 < len(res):
                print("rows", n, flush=True)
    print("done rows", n)


if __name__ == "__main__":
    main()
