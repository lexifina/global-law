"""Round 5: build a BLIND precision audit of model rows (packs for auditor agents, a private key, a blind brief).

    python round5/audit/make_audit.py --stage <name> --out-name <audit name> --strata <file>
                                      [--n 60] [--decoys <jsonl>] [--decoy-items <items.jsonl.gz>]
                                      [--per-pack 40] [--seed 5] [--pad 900] [--lean-out <folder>] [--force]

--stage       round5/stage/<name>/ (treatments.tsv, treatment_witness.tsv, treatment_class.tsv, decisions2.tsv,
              courts2.tsv); round5/out/<name>/classes.tsv is read when present (class and verdict, for the key only).
              A folder path may be given instead of a name (then `--lean-out <folder>` names the Lean output).
--strata      TSV `treatment_id <TAB> stratum`: the population. `--n` rows are sampled per stratum without
              replacement (all, if fewer), with a fixed seed per stratum (adding a stratum does not move the others).
--decoys      JSONL of items judged NOT to be statements, mixed in at about 1 per 6 real items. One object per line:
                {"speaker": <node>, "x": <node>, "y": <node or null>, "start": <int>, "end": <int>}
              `speaker` (alias `w`) is the decision whose text is shown; `y` null / absent / equal to the speaker
              means "through this decision"; instead of start/end a `quote` (found in the speaker's text) or
              `off` / `note_end` may be given; optional `id` and `why` go to the key. A line that has only `id`
              (a reader answer) is completed from `--decoy-items` (round5/recog/items.jsonl.gz layout: id, w, x, y,
              off, note_end).
--pad         characters of the speaking decision's text shown on each side of the quote (default 900). A random
              0-250 more is added on each side so that the quote's place cannot be read off the passage length.

Writes round5/audit/<audit name>/:
  packs/audit_<nn>.md   the blind items (opaque ids = a hash of seed, audit name and row; shuffled; decoys spread
                        over the packs)
  AUDIT_BRIEF.md        the blind brief for the auditors
  key.tsv               PRIVATE: item id -> treatment id, stratum, model kind / scope, class, verdict, nodes, offsets
  strata_summary.tsv    PRIVATE: stratum, population, sampled, built
  store/                PRIVATE: index.tsv + the speaking decisions' texts, read only by more_text.py
  build.json            PRIVATE: arguments, counts, warnings (hash mismatches, relocated quotes, skipped rows)
  answers/              (empty) where the auditors write ans_<nn>.jsonl
An item shows: the speaking decision (court, date), the opinion part label of the reader's part map, a passage of
the speaking decision's text (from git HEAD, normalised like the certificate windows, the quote NOT marked) and the
claim in neutral words. It shows nothing of the stratum, class, kind, scope, reader or quote boundaries.
Text comes from the corpus repos at HEAD; LF line endings throughout. No model API, nothing under gold/ or sealed/.
"""
import argparse
import gzip
import hashlib
import json
import math
import os
import random
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_common as AC  # noqa: E402

ID_ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"
CLAIM = ('"%s" lost authority (was overruled, abrogated, disapproved, receded from, rejected or repudiated '
         '— as a whole or in part) through %s.')

BRIEF = """# Blind audit brief ({name})

You are checking claims about what courts said. Work alone, from the text you are given.

## What an item is

Each ITEM in your pack (`round5\\audit\\{name}\\packs\\audit_<nn>.md`) has:

- **SPEAKING DECISION**: the court and date of the decision whose text is shown.
- **OPINION PART** (not always present): a machine label for the part of the decision the middle of the passage
  lies in. It can be wrong. If the passage itself plainly shows otherwise (a heading such as `## Dissent`, a line
  such as "BLACK, J., dissenting"), the passage governs.
- **CLAIM**: `"X" lost authority (was overruled, abrogated, disapproved, receded from, rejected or repudiated
  — as a whole or in part) through "Y".` X is an earlier decision. Y is a later decision, or the words
  "this decision", which mean the speaking decision itself.
- **PASSAGE**: about 2,000 characters of the speaking decision's text. Line breaks were turned into spaces;
  `…` marks a cut. The relevant words, if there are any, can stand anywhere in the passage.

The items come from sources of very different quality. Some are known to be wrong. Do not assume that an item is
right, and do not assume it is wrong: read it.

## The question

Does **the speaking court itself, in the opinion of the court, state or accept as fact that X lost authority
through Y**? Answer it in three separate parts. Take the statement in the passage that comes closest to the claim.

`stated`: is there such a statement at all: the court itself saying that an earlier decision lost authority
through a decision?

- `yes`: the court's own voice (majority, per curiam or lead opinion) says it or relies on it as settled:
  "we overrule A"; "A is overruled"; "A, overruled by B"; "B abrogated A"; "A was disapproved in B";
  "A is no longer good law after B"; "overruled in part by B"; "overruled on other grounds by B".
  A loss in part, or on a point other than the one under discussion, is still `yes` (say which under `extent`).
- `no`: anything else, in particular
  - it is a party's argument, a lower court's view, another court's words quoted, or another judge's view,
    which the court reports without adopting;
  - it stands in a dissent, a concurrence or a statement of individual judges, or in head matter / a syllabus /
    a reporter's note rather than in the opinion;
  - it is a question, or left open ("we need not decide whether B overruled A");
  - it is negated ("B did not overrule A", "we decline to overrule A");
  - it is hypothetical or conditional ("if A were overruled", when nothing is actually declared);
  - the earlier decision is only questioned, doubted, criticised, limited, narrowed, explained, distinguished
    or not followed, with no statement that it lost authority;
  - the earlier decision was reversed, vacated or modified on appeal in the same litigation (that is the case's
    own history, not what the claim says), or was displaced by a statute or rule and not by a decision.
- `unclear`: you cannot tell, even with more text.

`x_ok`: `true` when the earlier decision of that statement is the X of the claim (same case: the name and / or a
citation fits; a short form such as "Jones" counts when the text ties it to the same case). `false` when the
statement is about a different case, or the passage does not speak of X at all.

`y_ok`: `true` when the decision through which it happened, according to the passage, is the Y of the claim.
When the claim says "through this decision": `true` only if the speaking decision does it itself, here; `false`
when the passage reports what an earlier or another decision did.

So a passage in which the court overrules some other case than X is `stated: yes, x_ok: false`. When `stated`
is `no`, still answer `x_ok` and `y_ok` as well as you can (is the passage speaking of X, and of Y, at all).
The claim counts as confirmed only when `stated` is `yes` and both `x_ok` and `y_ok` are `true`.

`extent` (what the passage says, not what you know):

- `whole`: X as a whole, without qualification;
- `part`: only in part, on one point, "to the extent that", "insofar as", one of several holdings, a doctrine or
  a statement of X rather than X itself, or limited to a field;
- `otherGrounds`: "overruled on other grounds" and the like;
- `unclear`: not stated, or `stated` is not `yes`.

`words`: the few words of the passage (at most about 25, copied exactly) that carry your answer; for a `no`,
the words that show why, or "".

## More text

If the passage is not enough, ask for a wider one (run from the `caselaw-lean-2` folder):

    python round5\\audit\\more_text.py <item id> [chars]

`chars` is the number of extra characters on each side (default 3000; `all` prints the whole opinion text). It
prints the speaking decision's text only, with the pack's passage between `>>>` and `<<<`.

## Rules

- Judge from the text only. Use **no outside knowledge of what happened to these cases**: if you happen to know
  that X was overruled by Y but the speaking court does not say so here, the answer is `no`.
- No external model or API, no web search.
- Open no other files: only this brief, your pack and the output of `more_text.py`. In particular nothing else
  under `round5\\audit\\`, no data tables, no other auditor's answers.
- Every item of your pack exactly once, in pack order.

## Answers

One JSON object per line, written to `round5\\audit\\{name}\\answers\\ans_<nn>.jsonl` (`<nn>` = your pack number;
UTF-8, LF):

    {{"id": "<item id>", "stated": "yes|no|unclear", "x_ok": true|false, "y_ok": true|false, "extent": "whole|part|otherGrounds|unclear", "words": "<the few words that carry it>", "note": ""}}

Each line must parse as JSON (escape `"` and `\\` inside strings). `note` is free (a short reason helps).
"""


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def find_quote(ct, quote, near):
    """(a, b) of the occurrence of `quote` in the cleaned text nearest to offset `near`, or None. A second try lets
    every run of spaces of the quote match any run of spaces."""
    q = AC.clean(quote).strip()
    if not q:
        return None
    best = None
    i = ct.find(q)
    while i >= 0:
        if best is None or abs(i - near) < abs(best[0] - near):
            best = (i, i + len(q))
        i = ct.find(q, i + 1)
    if best:
        return best
    rx = re.compile(r"\s+".join(re.escape(t) for t in q.split()))
    for m in rx.finditer(ct):
        if best is None or abs(m.start() - near) < abs(best[0] - near):
            best = (m.start(), m.end())
    return best


def load_strata(path):
    pop, order, dup = {}, [], 0
    for p in AC.read_rows(path, 2):
        tid, st = p[0].strip(), p[1].strip()
        if not tid or tid.startswith("#") or tid == "treatment_id":
            continue
        if tid in pop:
            dup += 1
            continue
        pop[tid] = st
        if st not in order:
            order.append(st)
    return pop, order, dup


def load_decoys(path, items_path):
    raw = []
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    raw.append((ln, json.loads(line)))
                except ValueError:
                    log("decoys: line %d does not parse, skipped" % ln)
    need = {str(d.get("id")) for _, d in raw if "x" not in d and d.get("id") is not None}
    items = {}
    if need and items_path:
        op = gzip.open if items_path.endswith(".gz") else open
        with op(items_path, "rt", encoding="utf-8") as f:
            for line in f:
                m = re.match(r'\{"id": ?"([^"]+)"', line)
                if m and m.group(1) in need:
                    items[m.group(1)] = json.loads(line)
    out = []
    for ln, d in raw:
        if "x" not in d and str(d.get("id")) in items:
            it = items[str(d["id"])]
            d = dict(it, **{k: v for k, v in d.items() if k in ("id", "why", "quote", "start", "end")})
        sp = d.get("speaker", d.get("w"))
        if sp is None or d.get("x") is None:
            log("decoys: line %d has no speaker / x, skipped" % ln)
            continue
        y = d.get("y")
        st, en = d.get("start", d.get("off")), d.get("end", d.get("note_end"))
        out.append({"src": str(d.get("id", "line%d" % ln)), "speaker": int(sp), "x": int(d["x"]),
                    "y": None if y in (None, "", -1) or int(y) == int(sp) else int(y),
                    "start": None if st is None else int(st), "end": None if en is None else int(en),
                    "quote": d.get("quote") or "", "why": str(d.get("why", d.get("reason", "")))})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--lean-out")
    ap.add_argument("--out-name", required=True)
    ap.add_argument("--strata", required=True)
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--decoys")
    ap.add_argument("--decoy-items")
    ap.add_argument("--per-pack", type=int, default=40)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--pad", type=int, default=900)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    AC.utf8_stdout()
    if not re.fullmatch(r"[A-Za-z0-9_.\-]+", a.out_name):
        sys.exit("--out-name: letters, digits, _ . - only")
    if os.path.isfile(os.path.join(a.stage, "treatments.tsv")):  # a folder path instead of a stage name
        stage = os.path.abspath(a.stage)
        a.stage = os.path.basename(stage)
    else:
        stage = os.path.join(AC.R5, "stage", a.stage)
    outl = os.path.abspath(a.lean_out) if a.lean_out else os.path.join(AC.R5, "out", a.stage)
    adir = os.path.join(AC.HERE, a.out_name)
    outputs = ("key.tsv", "strata_summary.tsv", "skipped.tsv", "build.json", "AUDIT_BRIEF.md", "score.tsv",
               "wrong.tsv", "score.json")
    for inp in (a.strata, a.decoys):  # an input kept in the audit folder must not carry an output's name
        if inp and os.path.dirname(os.path.abspath(inp)) == os.path.abspath(adir) and os.path.basename(inp) in outputs:
            sys.exit("%s would be overwritten by the audit's own output: rename it" % inp)
    if not os.path.isdir(stage):
        sys.exit("no stage folder " + stage)
    if os.path.exists(os.path.join(adir, "key.tsv")) and not a.force:
        sys.exit("audit %s exists (key.tsv); use another --out-name, or --force to rebuild it" % a.out_name)
    warn = []

    # ---- population and sample
    pop, order, dup = load_strata(a.strata)
    if dup:
        warn.append("strata: %d repeated treatment ids ignored (first stratum kept)" % dup)
    rows = {}
    with open(os.path.join(stage, "treatments.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            i = line.find("\t")
            if line[:i] in pop:
                p = line.rstrip("\n").rstrip("\r").split("\t")
                if len(p) >= 14 and p[0] not in rows:
                    rows[p[0]] = p
    missing = sorted(t for t in pop if t not in rows)
    if missing:
        warn.append("strata: %d ids are not in the stage's treatments.tsv (left out of the population): %s"
                    % (len(missing), ", ".join(missing[:8]) + (" ..." if len(missing) > 8 else "")))
    by_st = {s: sorted(t for t, st in pop.items() if st == s and t in rows) for s in order}
    picked = []
    for s in order:
        ids = by_st[s]
        rnd = random.Random("%d|sample|%s" % (a.seed, s))
        picked += [(t, s) for t in (ids if len(ids) <= a.n else rnd.sample(ids, a.n))]

    witness = {p[0]: int(p[1]) for p in AC.read_rows(os.path.join(stage, "treatment_witness.tsv"), 2)
               if p[1].lstrip("-").isdigit()}
    claims = {}
    for p in AC.read_rows(os.path.join(stage, "treatment_class.tsv"), 5):
        claims.setdefault(p[0], p[1])
    classes = {}
    want = {t for t, _ in picked}
    cpath = os.path.join(outl, "classes.tsv")
    if os.path.exists(cpath):
        with open(cpath, encoding="utf-8", newline="") as f:
            for line in f:
                i = line.find("\t")
                if line[:i] in want:
                    p = line.rstrip("\n").rstrip("\r").split("\t")
                    classes[p[0]] = (p[1], p[2], p[3]) if len(p) >= 4 else ("-", "-", "-")
    else:
        warn.append("no %s: class and verdict are '-' in the key" % cpath)
    try:
        with open(AC.CUE_TABLE, encoding="utf-8") as f:
            whole_phr = [x.lower() for x in json.load(f).get("operative_whole", [])]
    except Exception:
        whole_phr = None
        warn.append("cue table not readable: operativeWords demotion (R5-7) is not applied to scope_class")

    specs = []
    for t, s in picked:
        r = rows[t]
        sp = witness.get(t, int(r[1]))
        cl, oclaim, verdict = classes.get(t, ("-", "-", "-"))
        claim = claims.get(t, oclaim)  # the stage's claim; the Lean output's copy only when the stage has none
        demoted = int(claim == "operativeWords" and t not in witness and whole_phr is not None
                      and not any(ph in AC.clean(r[11]).lower() for ph in whole_phr))
        specs.append({"tid": t, "stratum": s, "decoy": 0, "speaker": sp, "x": int(r[2]),
                      "y": int(r[1]) if t in witness else None, "start": int(r[9]), "end": int(r[10]),
                      "quote": r[11], "sha": r[8], "kind": r[4], "scope": r[5],
                      "scope_class": "all" if r[5] == "all" and not demoted else "part", "demoted": demoted,
                      "class": cl, "claim": claim, "verdict": verdict, "witness": int(t in witness), "why": ""})
    n_real = len(specs)

    # ---- decoys (every supplied decoy is built; about 1 per 6 real items are kept, see below)
    n_dec_avail = 0
    if a.decoys:
        dec = load_decoys(a.decoys, a.decoy_items)
        n_dec_avail = len(dec)
        dec.sort(key=lambda d: (d["src"], d["speaker"], d["x"]))
        seen_src = set()
        for d in dec:
            if d["src"] in seen_src:
                warn.append("decoys: id %s repeated, the later line is left out" % d["src"])
                continue
            seen_src.add(d["src"])
            specs.append({"tid": "decoy:" + d["src"], "stratum": "decoy", "decoy": 1, "speaker": d["speaker"],
                          "x": d["x"], "y": d["y"], "start": d["start"], "end": d["end"], "quote": d["quote"],
                          "sha": "", "kind": "-", "scope": "-", "scope_class": "-", "demoted": 0, "class": "-",
                          "claim": "-", "verdict": "-", "witness": int(d["y"] is not None), "why": d["why"]})

    # ---- node metadata (streamed) and texts (git HEAD)
    nodes = {s["speaker"] for s in specs} | {s["x"] for s in specs} | {s["y"] for s in specs if s["y"] is not None}
    log("looking up %d nodes in graph/nodes.tsv and the stage's decisions2.tsv ..." % len(nodes))
    ninfo = AC.nodes_info(nodes)
    dinfo = AC.decisions_info(os.path.join(stage, "decisions2.tsv"), nodes)
    court_name = AC.court_namer(os.path.join(stage, "courts2.tsv"))
    smeta = AC.scotus_meta()

    def label(n):
        repo, path, ndate, cites, name = ninfo.get(n, ("", "", 0, [], ""))
        cid, ddate, _ = dinfo.get(n, (-1, 0, ""))
        if n in smeta:
            if not name:
                name = smeta[n][1]
            if not cites and smeta[n][0]:
                cites = [smeta[n][0]]
        date = ddate or ndate
        return AC.case_label(name, cites, date, court_name(cid, date) if cid >= 0 else "")

    by_repo = {}
    for s in specs:
        ni = ninfo.get(s["speaker"])
        if ni:
            by_repo.setdefault(ni[0], set()).add(ni[1])
    texts = {}
    for repo, paths in sorted(by_repo.items()):
        got = AC.git_texts(repo, sorted(paths))
        for pth, raw in got.items():
            texts[(repo, pth)] = raw
    log("read %d texts from %d repos" % (len(texts), len(by_repo)))

    built, skipped = [], []
    store_texts = {}
    for s in specs:
        ni = ninfo.get(s["speaker"])
        raw = texts.get((ni[0], ni[1])) if ni else None
        if raw is None:
            skipped.append((s["tid"], s["stratum"], "no text for speaking node %d" % s["speaker"]))
            continue
        sha = hashlib.sha1(raw).hexdigest()
        text = AC.decode(raw)
        ct = AC.clean(text)
        st, en = s["start"], s["end"]
        if s["sha"] and sha != s["sha"]:
            warn.append("%s: text at HEAD has sha %s, the row says %s" % (s["tid"], sha, s["sha"]))
        ok = st is not None and en is not None and 0 <= st < en <= len(text)
        if ok and s["quote"] and ct[st:en] != AC.clean(s["quote"]):
            ok = False
        if not ok:
            hit = find_quote(ct, s["quote"], st or 0) if s["quote"] else None
            if hit is None:
                skipped.append((s["tid"], s["stratum"], "quote not found in the text at HEAD"))
                continue
            if s["start"] is not None:
                warn.append("%s: quote relocated from %s to %d" % (s["tid"], s["start"], hit[0]))
            st, en = hit
        part, body0 = AC.part_label(text, st)
        if st < body0:
            body0 = 0
        rj = random.Random("%d|pad|%s|%s" % (a.seed, a.out_name, s["tid"]))
        pa = max(body0, st - a.pad - rj.randint(0, 250))
        pb = min(len(text), en + a.pad + rj.randint(0, 250))
        for _ in range(40):  # do not cut inside a word
            if pa <= body0 or ct[pa - 1] == " ":
                break
            pa -= 1
        for _ in range(40):
            if pb >= len(text) or ct[pb] == " ":
                break
            pb += 1
        passage = ("… " if pa > body0 else "") + ct[pa:pb].strip() + (" …" if pb < len(text) else "")
        cid, ddate, _ = dinfo.get(s["speaker"], (-1, 0, ""))
        date = ddate or ni[2]
        s.update({"st": st, "en": en, "pa": pa, "pb": pb, "body0": body0, "text_sha": sha, "part": part,
                  "passage": passage, "court": court_name(cid, date) if cid >= 0 else "court unknown",
                  "date": date, "xl": label(s["x"]),
                  "yl": "this decision" if s["y"] is None else '"%s"' % label(s["y"])})
        store_texts[sha] = text
        built.append(s)

    # ---- keep about 1 decoy per 6 real items (of the decoys that could be built)
    bdec = sorted((s for s in built if s["decoy"]), key=lambda s: s["tid"])
    k = int(round(sum(1 for s in built if not s["decoy"]) / 6.0))
    if a.decoys and len(bdec) < k:
        warn.append("decoys: %d usable, %d wanted for 1 per 6" % (len(bdec), k))
    if len(bdec) > k:
        keep = {s["tid"] for s in random.Random("%d|decoys" % a.seed).sample(bdec, k)}
        built = [s for s in built if not s["decoy"] or s["tid"] in keep]
    store_texts = {sha: t for sha, t in store_texts.items() if sha in {s["text_sha"] for s in built}}

    # ---- opaque ids, packs
    taken = set()
    for d in os.listdir(AC.HERE):
        ip = os.path.join(AC.HERE, d, "store", "index.tsv")
        if d != a.out_name and os.path.exists(ip):
            taken |= {p[0] for p in AC.read_rows(ip)}
    for s in sorted(built, key=lambda s: s["tid"]):
        # the id depends only on (seed, audit name, row): a rebuild with other rows or decoys keeps the ids
        n = 0
        while True:
            h = int(hashlib.sha1(("%d|ids|%s|%s|%d" % (a.seed, a.out_name, s["tid"], n)).encode("utf-8")).hexdigest(),
                    16)
            i = ""
            for _ in range(7):
                h, r = divmod(h, len(ID_ALPHABET))
                i += ID_ALPHABET[r]
            if i not in taken:
                taken.add(i)
                s["id"] = i
                break
            n += 1
    rsh = random.Random("%d|shuffle|%s" % (a.seed, a.out_name))
    real = sorted((s for s in built if not s["decoy"]), key=lambda s: s["id"])
    decs = sorted((s for s in built if s["decoy"]), key=lambda s: s["id"])
    rsh.shuffle(real)
    rsh.shuffle(decs)
    n_packs = max(1, int(math.ceil(len(built) / float(max(1, a.per_pack)))))
    packs = [real[i::n_packs] for i in range(n_packs)]
    for j, s in enumerate(decs):  # decoys spread over the packs, from the last pack back (it has the fewest reals)
        packs[n_packs - 1 - j % n_packs].append(s)
    for pk in packs:
        rsh.shuffle(pk)

    # ---- write
    if a.force:
        old = [f for f in os.listdir(os.path.join(adir, "answers"))] if os.path.isdir(os.path.join(adir, "answers")) \
            else []
        if old:
            warn.append("--force: answers/ already holds %d files; item ids are stable for unchanged rows, but the "
                        "packs may hold other items now" % len(old))
        for sub in ("packs", os.path.join("store", "text")):
            d = os.path.join(adir, sub)
            if os.path.isdir(d):
                for fn in os.listdir(d):
                    os.remove(os.path.join(d, fn))
    os.makedirs(os.path.join(adir, "answers"), exist_ok=True)
    key = [["item_id", "pack", "treatment_id", "stratum", "decoy", "kind", "scope", "scope_class", "demoted",
            "class", "claim", "verdict", "witness_row", "speaker", "x", "y", "text_sha", "start", "end", "note"]]
    index = []
    for k, pk in enumerate(packs, 1):
        out = ["# Audit pack %02d (%d items)\n\nRead `round5\\audit\\%s\\AUDIT_BRIEF.md` first. Answers: one JSON line "
               "per item, in this order, to `round5\\audit\\%s\\answers\\ans_%02d.jsonl`.\n"
               % (k, len(pk), a.out_name, a.out_name, k)]
        for s in pk:
            out.append("\n## ITEM %s\n\nSPEAKING DECISION: %s, decided %s\n" % (s["id"], s["court"],
                                                                               AC.iso_date(s["date"])))
            if s["part"]:
                out.append("OPINION PART: %s\n" % s["part"])
            out.append("CLAIM: " + CLAIM % (s["xl"], s["yl"]) + "\n")
            out.append("PASSAGE:\n%s\n" % s["passage"])
            key.append([s["id"], "%02d" % k, s["tid"], s["stratum"], s["decoy"], s["kind"], s["scope"],
                        s["scope_class"], s["demoted"], s["class"], s["claim"], s["verdict"], s["witness"],
                        s["speaker"], s["x"], "-" if s["y"] is None else s["y"], s["text_sha"], s["st"], s["en"],
                        AC.clean(s["why"])])
            index.append([s["id"], s["text_sha"], s["body0"], s["pa"], s["pb"]])
        AC.write_text(os.path.join(adir, "packs", "audit_%02d.md" % k), "".join(out))
    AC.write_rows(os.path.join(adir, "key.tsv"), key)
    AC.write_rows(os.path.join(adir, "store", "index.tsv"), sorted(index))
    for sha, text in store_texts.items():
        AC.write_text(os.path.join(adir, "store", "text", sha + ".txt"), text)
    AC.write_text(os.path.join(adir, "AUDIT_BRIEF.md"), BRIEF.format(name=a.out_name))
    nb = {}
    for s in built:
        nb[s["stratum"]] = nb.get(s["stratum"], 0) + 1
    ns = {}
    for _, st in picked:
        ns[st] = ns.get(st, 0) + 1
    strata = [["stratum", "population", "sampled", "built"]]
    for st in order:
        strata.append([st, len(by_st[st]), ns.get(st, 0), nb.get(st, 0)])
    AC.write_rows(os.path.join(adir, "strata_summary.tsv"), strata)
    if skipped:
        AC.write_rows(os.path.join(adir, "skipped.tsv"), [["treatment_id", "stratum", "why"]] + skipped)
    info = {"stage": a.stage, "out_name": a.out_name, "strata_file": os.path.abspath(a.strata), "n": a.n,
            "per_pack": a.per_pack, "seed": a.seed, "pad": a.pad, "decoys_file": a.decoys,
            "decoys_supplied": n_dec_avail, "items": len(built), "real_items": len(real), "decoy_items": len(decs),
            "packs": [len(pk) for pk in packs], "skipped": len(skipped), "warnings": warn}
    AC.write_text(os.path.join(adir, "build.json"), json.dumps(info, indent=1, ensure_ascii=False) + "\n")

    print("audit %s: %d items (%d real, %d decoys) in %d packs %s" % (a.out_name, len(built), len(real), len(decs),
                                                                     n_packs, [len(pk) for pk in packs]))
    for r in strata:
        print("  " + "\t".join(str(x) for x in r))
    if skipped:
        print("skipped %d rows (skipped.tsv)" % len(skipped))
    for w in warn:
        print("warning: " + w)
    print("packs: " + os.path.join(adir, "packs"))
    print("brief: " + os.path.join(adir, "AUDIT_BRIEF.md"))


if __name__ == "__main__":
    main()
