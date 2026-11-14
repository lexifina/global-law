"""Round 9 copy of round8/certify_opwords8.py (agent infra9; base round8/stage/v8e + round8/out/v8e, ids t9:).
Round 8 copy of round7/agents/opwords/certify_opwords7.py (agent infra; paths only: base round7/stage/v3 +
round7/out/v3, ids t8:, answers / out / index / items named on the command line).
Round 7 certifier for `operativeWords` rows (agent opwords): reader answers -> a round-7 delta folder.

    python -X utf8 certify_opwords7.py [--answers ans] [--out cert] [--index packs/index.tsv] [--items FILE]
                                       [--trim] [--cues FILE]

The logic of round5/opwords/certify_opwords.py (copied, paths adapted; the round-5 file is not edited), with the
round-7 brief (READER_BRIEF_OPWORDS7.md) and the round-7 base:
  * answers: <answers>/ans_*.jsonl; items: work/items7.jsonl.gz (build_packs7.py); index: packs/index.tsv;
  * base: round6/history/stage/final2/{treatments,cite_index}.tsv and round6/history/out/final2/certs.tsv (an
    admitted explicit status-changing row (by, target) there makes the item `already-admitted`; row ids that exist
    there are not reused);
  * gate (new): `own_act` true AND `cause` == "own" (the brief's cause test; an answer without `cause` is refused);
  * the quote must lie inside the FOCUS sentence (new; whitespace runs, quote-mark styles and hard-wrap hyphens
    tolerated as before); a quote outside it, not found, or failing a check falls back to the FOCUS sentence;
  * the mechanical checks are unchanged: a phrase of `operative`, no phrase of `disqualify_treat` +
    `disqualify_operative`, no overruling term of art (`self_announced`), not inside a quotation, the target named in
    the quote (citation through the base cite_index, or every name word), opinion part majority / perCuriam /
    plurality, the target not later than the acting decision, text recut from git HEAD and hash-checked;
  * scope (`operative_whole` / `operative_limit` logic, DESIGN5 3.3 and section 9): `all` only when the reader's
    `subclass` is "whole" (or, for an answer without `subclass`, `whole` true) AND the quote has a phrase of
    `operative_whole` AND no phrase of `operative_limit` AND object "case" AND no field limit AND no extent wording;
    otherwise `partialUnknown` (the checker then demotes the row: partly negative, never overruled).
Writes to <out>/ (default cert/): treatments_delta.tsv (id t7:<by>:<target>:<start>, kind disapproved, explicit 1),
treatment_class_delta.tsv (id, operativeWords, field_limit|-, doctrine|-, src: 5 fields), cert_text_delta.tsv,
window_sha_delta.tsv, cite_index_delta.tsv, treatments_items_delta.tsv, rows_detail.tsv (id, object, subclass,
reader whole, whole phrase, limit phrase, cues, pack, cause), rejects.tsv, stats.json.
One row per (by, target): a whole-case row wins, then the higher confidence.
--trim: when the only failure is a disqualifier phrase, cut the quote to the shortest run of its clauses that still
holds a cue and the target evidence (off by default). --cues FILE: {"OPERATIVE": [...], "OPERATIVE_WHOLE": [...],
"OPERATIVE_LIMIT": [...], "DISQUALIFY_OPERATIVE": [...]} replacing the lists of the cue table.
"""
import argparse, collections, glob, gzip, hashlib, json, os, re, subprocess, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, ".."))
BASE = os.path.join(C2, "round8", "stage", "v8e")
OUTB = os.path.join(C2, "round8", "out", "v8e")
RWORK = os.path.join(C2, "data", "reader_work")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
READER_DIR = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/reader")
sys.path.insert(0, READER_DIR)
import cue_table as CT  # noqa: E402
from common import name_tokens, short_name_tokens  # noqa: E402
from certify import find_quote, quoted, clean, PART_OUT  # noqa: E402
from certify2 import find_quote_hw  # noqa: E402

NOWIN = 0x08000000 if sys.platform == "win32" else 0
READER = "claude-subagent:opwords7"
OBJECTS = {"case", "language", "doctrine", "rule", "holding", "reasoning", "dictum"}
NEG_KINDS = ("overruled", "disapproved", "recededFrom", "abrogated")
EXTENT = re.compile(r"\b(?:to\s+the\s+extent|insofar\s+as|in\s+so\s+far\s+as|so\s+far\s+as|to\s+that\s+extent)\b", re.I)
CLAUSE = re.compile(r"(?<=[,;:—])\s+")
_AL = {c: c + 32 for c in range(65, 91)}


def ascii_lower(s):
    return s.translate(_AL)


def norm_quote(s):
    return s.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def alnum(s):
    return re.sub(r"[^0-9a-z]", "", ascii_lower(s))


def load_cues(path):
    cues = {"OPERATIVE": tuple(CT.OPERATIVE), "OPERATIVE_WHOLE": tuple(CT.OPERATIVE_WHOLE),
            "OPERATIVE_LIMIT": tuple(CT.OPERATIVE_LIMIT), "DISQUALIFY_OPERATIVE": tuple(CT.DISQUALIFY_OPERATIVE)}
    if path:
        j = json.load(open(path, encoding="utf-8"))
        j = j.get("proposed_lists", j)
        for k in cues:
            if k in j:
                cues[k] = tuple(j[k])
    return cues


def name_words(ev):
    return [t for t in re.sub(r"[^0-9A-Za-z]+", " ", ev).split() if len(t) >= 3]


def evidence(t, quote, didx):
    """(evidence string, cite_index delta or None, failure reason) - as round 5."""
    ql = ascii_lower(quote)
    ev = t["ev"]
    if ev.startswith("cite:"):
        c = alnum(ev[5:])
        if c and c in alnum(ql):
            dn = didx.get(c, -1)
            if dn == t["node"]:
                return ev, None, ""
            if dn == -1:
                return ev, (ev[5:], t["node"]), ""
        toks = sorted(name_tokens(t["name"]) | short_name_tokens(t["name"]))
        ws = [w for tk in toks for w in name_words(tk)]
        need_all = False
    else:
        ws = name_words(ev[5:])
        need_all = True
    words = set(re.findall(r"[0-9a-z]+", ql))
    have = [w for w in ws if w.lower() in words]
    if not have or (need_all and len(have) != len(ws)):
        return None, None, "target-not-in-quote"
    if not need_all:
        have = sorted(have, key=len, reverse=True)[:2]
    return "name:" + " ".join(have), None, ""


def check_quote(q, cues):
    if len(q) > 400:
        return "quote-too-long"
    ql = ascii_lower(norm_quote(q))
    if not any(c in ql for c in cues["OPERATIVE"]):
        return "no-cue"
    if any(x in ql for x in CT.SELF_ANNOUNCED):
        return "self-announced-term"
    bad = [x for x in tuple(CT.DISQUALIFY_TREAT) + cues["DISQUALIFY_OPERATIVE"] if x in ql]
    if bad:
        return "disqualifier:" + bad[0].strip()
    return ""


def trim(lw, q0, q1, t, didx, cues):
    cuts = [q0] + [q0 + m.end() for m in CLAUSE.finditer(lw[q0:q1])] + [q1]
    best = None
    for i in range(len(cuts) - 1):
        for j in range(i + 1, len(cuts)):
            a, b = cuts[i], cuts[j]
            while b > a and lw[b - 1] == " ":
                b -= 1
            if best and b - a >= best[1] - best[0]:
                continue
            if check_quote(lw[a:b], cues) == "" and evidence(t, lw[a:b], didx)[0]:
                best = (a, b)
    return best


def node_paths(wanted):
    wanted = set(int(x) for x in wanted)
    out = {}
    for f in sorted(glob.glob(os.path.join(RWORK, "nodes", "*.tsv")),
                    key=lambda f: (os.path.basename(f) != "supreme-court.tsv", f)):
        if len(out) == len(wanted):
            break
        repo = os.path.basename(f)[:-4]
        for line in open(f, encoding="utf-8"):
            p = line.rstrip("\n").split("\t")
            n = int(p[1])
            if n in wanted:
                out[n] = (repo, p[0])
    return out


def git_texts(repo, paths):
    """{path: (sha1 of the bytes, text: CRLF -> LF, then tab / newline / CR -> space)} (SCHEMA.md)."""
    paths = list(paths)
    p = subprocess.Popen(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, creationflags=NOWIN)

    def feed():
        for x in paths:
            p.stdin.write(("HEAD:" + x + "\n").encode("utf-8"))
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    out = {}
    for x in paths:
        hdr = p.stdout.readline().split()
        if len(hdr) < 3 or hdr[1] == b"missing":
            continue
        raw = p.stdout.read(int(hdr[2]))
        p.stdout.read(1)
        out[x] = (hashlib.sha1(raw).hexdigest(), norm_quote(raw.decode("utf-8", "replace").replace("\r\n", "\n")))
    p.wait()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--index", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--trim", action="store_true")
    ap.add_argument("--cues")
    a = ap.parse_args()
    cues = load_cues(a.cues)
    os.makedirs(a.out, exist_ok=True)
    st = collections.Counter()
    ans = {}
    for f in sorted(glob.glob(os.path.join(a.answers, "ans_*.jsonl"))):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                ans[str(r["id"]).strip()] = r
            except Exception:
                st["answer_lines_unparsed"] += 1
    index = {}
    for line in open(a.index, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        index[p[0]] = (p[1], p[3])
    for i in ans:
        if i not in index:
            st["answer_unknown_id"] += 1
    items = {}
    for line in gzip.open(a.items, "rt", encoding="utf-8"):
        it = json.loads(line)
        if it["id"] in ans:
            items[it["id"]] = it
    didx = {}
    for line in open(os.path.join(BASE, "cite_index.tsv"), encoding="utf-8"):
        k, v = line.rstrip("\n").split("\t")[:2]
        c = alnum(k)
        if c:
            didx[c] = int(v) if didx.get(c, int(v)) == int(v) else None
    ok_ids = set()
    for line in open(os.path.join(OUTB, "certs.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if f[0] == "treatment" and f[2].startswith("ok"):
            ok_ids.add(f[1])
    admitted, base_ids = set(), set()
    for line in open(os.path.join(BASE, "treatments.tsv"), "rb"):
        f = line.decode("utf-8").split("\t", 8)
        base_ids.add(f[0])
        if f[4] in NEG_KINDS and f[7] == "1" and f[0] in ok_ids:
            admitted.add((int(f[1]), int(f[2])))
    st["answers"] = len(ans)
    st["items_without_answer"] = len(set(index) - set(ans))
    rej = open(os.path.join(a.out, "rejects.tsv"), "w", encoding="utf-8", newline="\n")
    rows = []
    for i, r in ans.items():
        it = items.get(i)
        if it is None:
            continue
        st["read_items"] += 1
        if r.get("own_act") is not True:
            st["reader_not_own_act"] += 1
            rej.write(f"{i}\treader\tnot-own-act:{r.get('cause', '-')}\n")
            continue
        if r.get("cause") != "own":
            st["reader_cause_not_own"] += 1
            rej.write(f"{i}\treader\tcause:{r.get('cause', 'missing')}\n")
            continue
        tids = r.get("target")
        tids = [tids] if isinstance(tids, str) else (tids or [])
        tids = [x for x in tids if isinstance(x, str) and re.fullmatch(r"T\d+", x) and 1 <= int(x[1:]) <= len(it["targets"])]
        if not tids:
            st["reader_no_valid_target"] += 1
            rej.write(f"{i}\treader\tno-target\n")
            continue
        st["reader_own_act"] += 1
        sub = r.get("subclass")
        whole_reader = (sub == "whole") if sub in ("whole", "part") else (r.get("whole") is True)
        if sub not in ("whole", "part"):
            st["reader_subclass_missing"] += 1
        part = PART_OUT.get(it["part"], "unknown")
        if part not in ("majority", "perCuriam", "plurality"):
            st["cert_fail_part"] += 1
            rej.write(f"{i}\tcert\tpart:{part}\n")
            continue
        w, w0 = it["w"], it["w0"]
        lw = w[it["lw0"] - w0:it["lw1"] - w0]
        f0, f1 = it["s0"] - it["lw0"], it["s1"] - it["lw0"]
        rq = (r.get("quote") or "").replace("⟦", "").replace("⟧", "")
        pos = find_quote(lw, rq, f0) if rq.strip() else None
        if pos is None and rq.strip() and it.get("hw"):
            pos = find_quote_hw(lw, rq, f0)
        if pos is None:
            st["quote_not_found"] += 1
        elif pos[0] < f0 or pos[1] > f1:
            st["quote_outside_focus"] += 1
            pos = None
        for tid in tids:
            t = it["targets"][int(tid[1:]) - 1]
            j = t["node"]
            if j == it["n"]:
                rej.write(f"{i}\tcert\tself-target\n")
                continue
            if it["date"] and t.get("date") and t["date"] > it["date"]:
                st["cert_fail_target_later"] += 1
                rej.write(f"{i}\tcert\ttarget-later:{j}\n")
                continue
            if (it["n"], j) in admitted:
                st["already_admitted"] += 1
                rej.write(f"{i}\tcert\talready-admitted:{j}\n")
                continue
            tries = ([("quote", pos[0], pos[1])] if pos else []) + [("sentence", f0, f1)]
            got, why, whys = None, "", []
            for how, q0, q1 in tries:
                q = lw[q0:q1]
                why = check_quote(q, cues)
                e, delta = None, None
                if not why:
                    e, delta, why = evidence(t, q, didx)
                if not why and quoted(lw, q0, q1):
                    why = "inside-quotation"
                if why.startswith("disqualifier") and a.trim:
                    tr = trim(lw, q0, q1, t, didx, cues)
                    if tr and not quoted(lw, tr[0], tr[1]):
                        q0, q1 = tr
                        e, delta, why = evidence(t, lw[q0:q1], didx)
                        how = "trim:" + how
                if not why:
                    got = (how if how != "sentence" else "sentence:" + (whys[0] if whys else "quote-not-found"),
                           q0, q1, e, delta)
                    break
                whys.append(why)
            if got is None:
                st["cert_fail:" + whys[0].split(":")[0]] += 1
                rej.write(f"{i}\tcert\t{'|'.join(whys)}:{j}\n")
                continue
            how, q0, q1, e, delta = got
            quote = lw[q0:q1]
            start, end = it["lw0"] + q0, it["lw0"] + q1
            ql = ascii_lower(norm_quote(quote))
            whole_mech = any(x in ql for x in cues["OPERATIVE_WHOLE"])
            limit_mech = any(x in ql for x in cues["OPERATIVE_LIMIT"])
            obj = r.get("object") if r.get("object") in OBJECTS else "case"
            fl = clean(str(r.get("field_limit") or "")).strip()[:200]
            doc = clean(str(r.get("doctrine") or "")).strip()[:120]
            scope = "all" if (whole_reader and whole_mech and not limit_mech and obj == "case" and not fl
                              and not EXTENT.search(quote)) else "partialUnknown"
            if whole_reader and scope != "all":
                st["whole_claim_demoted"] += 1
            try:
                conf = max(0.0, min(1.0, float(r.get("confidence", 0.5))))
            except (TypeError, ValueError):
                conf = 0.5
            st0, en0 = max(0, start - 400, w0), min(it["len"], end + 400, it["w1"])
            rows.append({"by": it["n"], "target": j, "date": it["date"], "scope": scope, "sha": it["sha"],
                         "start": start, "end": end, "quote": clean(quote), "ev": e, "part": part, "conf": conf,
                         "item": i, "how": how, "shapes": ",".join(it["shapes"]), "obj": obj, "fl": fl, "doc": doc,
                         "sub": "whole" if whole_reader else "part", "whole_reader": int(whole_reader),
                         "whole_mech": int(whole_mech), "limit_mech": int(limit_mech),
                         "cues": ",".join(c for c in cues["OPERATIVE"] if c in ql), "pack": index[i][1],
                         "win": (st0, en0, clean(w[st0 - w0:en0 - w0])), "delta": delta, "repo": it["repo"]})
    best = {}
    for t in rows:
        k = (t["by"], t["target"])
        key = (t["scope"] == "all", t["conf"], -t["start"])
        if k not in best or key > best[k][0]:
            best[k] = (key, t)
    st["duplicate_rows_dropped"] = len(rows) - len(best)
    rows = sorted((v[1] for v in best.values()), key=lambda t: (t["by"], t["target"], t["start"]))
    paths = node_paths({t["by"] for t in rows})
    by_repo = collections.defaultdict(set)
    for n, (repo, path) in paths.items():
        by_repo[repo].add(path)
    texts = {}
    for repo, ps in by_repo.items():
        for path, v in git_texts(repo, sorted(ps)).items():
            texts[(repo, path)] = v
    out_rows, deltas = [], {}
    for t in rows:
        sha, text = texts.get(paths.get(t["by"], ("", "")), (None, ""))
        s0, e0, win = t["win"]
        if sha != t["sha"] or text[t["start"]:t["end"]] != t["quote"] or text[s0:e0] != win:
            st["cert_fail:corpus-text-differs"] += 1
            rej.write(f"{t['item']}\tcert\tcorpus-text-differs:{t['target']}\n")
            continue
        if t["delta"]:
            k, node = t["delta"]
            if deltas.setdefault(k, node) != node:
                st["cert_fail:cite-key-two-targets"] += 1
                rej.write(f"{t['item']}\tcert\tcite-key-two-targets:{t['target']}\n")
                continue
        tid = f"t9:{t['by']}:{t['target']}:{t['start']}"
        while tid in base_ids:
            tid += "b"
        base_ids.add(tid)
        t["id"] = tid
        out_rows.append(t)
    rej.close()

    def wr(name, lines):
        with open(os.path.join(a.out, name), "w", encoding="utf-8", newline="\n") as f:
            for l in lines:
                f.write("\t".join(map(str, l)) + "\n")
    wr("treatments_delta.tsv", [[t["id"], t["by"], t["target"], t["date"], "disapproved", t["scope"], "unknown", 1,
                                 t["sha"], t["start"], t["end"], t["quote"], t["ev"], t["part"], READER,
                                 f"{t['conf']:.2f}"] for t in out_rows])
    wr("treatment_class_delta.tsv", [[t["id"], "operativeWords", t["fl"] or "-", t["doc"] or "-",
                                      f"{READER}:{t['pack']}:{t['item']}"] for t in out_rows])
    wins = sorted({(t["sha"],) + t["win"] for t in out_rows})
    wr("cert_text_delta.tsv", wins)
    wr("window_sha_delta.tsv", [[sha, s0, e0, hashlib.sha1(w.encode("utf-8")).hexdigest(), "corpus"]
                                for sha, s0, e0, w in wins])
    used = {t["delta"] for t in out_rows if t["delta"]}
    wr("cite_index_delta.tsv", sorted(used))
    wr("treatments_items_delta.tsv", [[t["id"], t["item"], t["how"], "opwords7:" + t["shapes"]] for t in out_rows])
    wr("rows_detail.tsv", [[t["id"], t["obj"], t["sub"], t["whole_reader"], t["whole_mech"], t["limit_mech"],
                            t["cues"], t["pack"], "own"] for t in out_rows])
    st["rows_staged"] = len(out_rows)
    st["rows_scope_all"] = sum(t["scope"] == "all" for t in out_rows)
    st["rows_by_object"] = dict(collections.Counter(t["obj"] for t in out_rows))
    st["rows_by_how"] = dict(collections.Counter(t["how"].split(":")[0] for t in out_rows))
    st["cite_index_delta"] = len(used)
    with open(os.path.join(a.out, "stats.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(sorted(st.items(), key=lambda x: x[0])), f, indent=1)
    print(json.dumps(dict(sorted(st.items(), key=lambda x: x[0])), indent=0))


if __name__ == "__main__":
    main()
