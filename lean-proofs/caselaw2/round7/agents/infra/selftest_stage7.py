"""Self-test of round7/stage7.py.

    python -X utf8 round7/agents/infra/selftest_stage7.py
A. no delta: the ten tables equal the base byte for byte (hard links), history_claim / joined empty;
   --force-write: every table rewritten, still byte-identical.
B. synthetic deltas (round7/agents/infra/selftest_stage/): every acceptance / skip rule of stage7.py's docstring.
C. real deltas of the earlier rounds: round5/opwords/cert (certify_opwords), round5/recog/cert (certify_recog),
   round6/history/rules/rehear/cert (certify6): accepted, counted.
D. the base files are untouched (sha1 before = after).
The stages it builds (_st_*) are removed at the end. Reads no answer key.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R7 = os.path.dirname(os.path.dirname(HERE))
C2 = os.path.dirname(R7)
BASE = os.path.join(C2, "round6", "history", "stage", "final2")
TEN = ["treatments", "treatment_witness", "treatment_class", "history", "history_anchor", "history_claim", "joined",
       "cert_text", "window_sha", "cite_index"]
FAILS, N = [], [0]


def expect(name, ok, info=""):
    N[0] += 1
    if not ok:
        FAILS.append("%s %s" % (name, info))


def sha(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()


def lines(p):
    with open(p, "rb") as f:
        return [l for l in f.read().split(b"\n") if l]


def stage(name, *args):
    r = subprocess.run([sys.executable, "-X", "utf8", os.path.join(R7, "stage7.py"), name] + list(args),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        FAILS.append("stage %s failed: %s" % (name, (r.stdout + r.stderr)[-500:]))
    return r.stdout, os.path.join(R7, "stage", name)


def w(p, rows):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")


def main():
    before = {t: sha(os.path.join(BASE, t + ".tsv")) for t in TEN if os.path.exists(os.path.join(BASE, t + ".tsv"))}
    # A
    out, d = stage("_st_a")
    for t in TEN:
        p, bp = os.path.join(d, t + ".tsv"), os.path.join(BASE, t + ".tsv")
        if os.path.exists(bp):
            expect("A same %s" % t, sha(p) == before[t])
            expect("A hard link %s" % t, os.path.samefile(p, bp))
        else:
            expect("A empty %s" % t, os.path.getsize(p) == 0)
    others = [f for f in os.listdir(BASE) if f.endswith(".tsv") and f[:-4] not in TEN]
    expect("A other tables linked", all(os.path.samefile(os.path.join(d, f), os.path.join(BASE, f)) for f in others))
    out, d = stage("_st_fw", "--force-write")
    for t in TEN:
        bp = os.path.join(BASE, t + ".tsv")
        if os.path.exists(bp):
            expect("A force-write same %s" % t, sha(os.path.join(d, t + ".tsv")) == before[t])
            expect("A force-write not a link %s" % t, not os.path.samefile(os.path.join(d, t + ".tsv"), bp))
    # B: synthetic deltas
    sd = os.path.join(HERE, "selftest_stage")
    shutil.rmtree(sd, ignore_errors=True)
    d1 = os.path.join(sd, "d1")
    os.makedirs(d1)
    T = lines(os.path.join(BASE, "treatments.tsv"))
    H = lines(os.path.join(BASE, "history.tsv"))
    t0 = T[0].decode().split("\t")
    h0 = H[0].decode().split("\t")
    nt1 = ["t7:test:1"] + t0[1:]
    nt2 = ["t7:test:2"] + t0[1:]
    w(os.path.join(d1, "treatments_delta.tsv"), [nt1, nt2, t0, nt1])          # +2, base id 1, repeated id 1
    w(os.path.join(d1, "treatment_witness_delta.tsv"), [["t7:test:1", 5, "name:x", "s"], ["t7:nope", 5, "name:x", "s"]])
    w(os.path.join(d1, "treatment_class_delta.tsv"), [["t7:test:2", "doctrine", "-", "doctrine of laches", "s"],
                                                      ["t7:test:2", "operativeWords", "-", "-", "s"]])
    nh = ["h7:test:1"] + h0[1:]
    w(os.path.join(d1, "history_delta.tsv"), [nh, h0])                          # +1, base id 1
    w(os.path.join(d1, "history_anchor_delta.tsv"), [["h7:test:1", 0, 5, "abcde", "majority", "s"],
                                                     ["h7:nope", 0, 5, "abcde", "majority", "s"]])
    w(os.path.join(d1, "history_claim_delta.tsv"), [["h7:test:1", "orderHead", "s"], ["h7:test:1", "setAside", "s"],
                                                    ["h7:test:1", "orderHead", "s2"],
                                                    [h0[0], "setAside", "s"], ["h7:nope", "orderHead", "s"]])
    j = lambda i, tb, k: [i, tb, "antecedent", k, k + 5, "abcde", "majority", "-", "s"]  # noqa: E731
    w(os.path.join(d1, "joined_delta.tsv"), [j("t7:test:1", "treatments", 1), j("t7:test:1", "treatments", 2),
                                             j("t7:test:1", "treatments", 3), j("t7:test:1", "treatments", 1),
                                             j("h7:test:1", "history", 1), j("t7:nope", "treatments", 1),
                                             j("h7:test:1", "treatments", 9)])
    ct0 = lines(os.path.join(BASE, "cert_text.tsv"))[0].decode().split("\t")
    w(os.path.join(d1, "cert_text_delta.tsv"), [["fakesha", 0, 5, "abcde"], ct0[:3] + ["other text"], ct0])
    ws0 = lines(os.path.join(BASE, "window_sha.tsv"))[0].decode().split("\t")
    w(os.path.join(d1, "window_sha_delta.tsv"), [["fakesha", 0, 5, "x" * 40, "corpus"],
                                                 ws0[:3] + ["y" * 40, "corpus"]])
    ci0 = lines(os.path.join(BASE, "cite_index.tsv"))[0].decode().split("\t")
    w(os.path.join(d1, "cite_index_delta.tsv"), [["999 fake 999", 7], [ci0[0].upper(), int(ci0[1]) + 1], ci0])
    w(os.path.join(d1, "remove_ids.txt"), [["t:whatever"]])
    rem = os.path.join(sd, "remove.txt")
    tw0 = lines(os.path.join(BASE, "treatment_witness.tsv"))[0].decode().split("\t")[0]
    w(rem, [[tw0], [t0[0]]])
    drop = os.path.join(sd, "drop.txt")
    w(drop, [["t7:test:2"]])
    rep = os.path.join(sd, "replace.txt")
    t1 = T[1].decode().split("\t")
    t1r = list(t1)
    t1r[5] = "partialUnknown" if t1[5] != "partialUnknown" else "all"
    w(rep, [t1r, ["t:nope"] + t1[1:]])
    cl = os.path.join(sd, "claims.txt")
    w(cl, [["t7:test:1", "operativeWords", "-", "-", "s"], [h0[0], "orderHead", "s"], [H[1].decode().split("\t")[0],
                                                                                      "orderHead", "s", "extra"]])
    out, d = stage("_st_b", "--remove", rem, "--delta", d1, "--claims", cl, "--replace", rep, "--drop", drop)
    tt = lines(os.path.join(d, "treatments.tsv"))
    ids = [l.split(b"\t")[0] for l in tt]
    expect("B treatments: base - 2 removed + 3 added - 1 dropped", len(tt) == len(T) - 2 + 3 - 1, str(len(tt)))
    expect("B removed base id gone", tw0.encode() not in ids)
    expect("B new id present once", ids.count(b"t7:test:1") == 1 and b"t7:test:2" not in ids)
    expect("B a removed base row comes back from a delta under its id", ids.count(t0[0].encode()) == 1)
    wl = lines(os.path.join(d, "treatment_witness.tsv"))
    expect("B witness: removed row's line gone, new line added",
           not any(l.startswith(tw0.encode() + b"\t") for l in wl) and any(l.startswith(b"t7:test:1\t") for l in wl))
    cls = lines(os.path.join(d, "treatment_class.tsv"))
    expect("B class: the dropped row's line gone; claims file line added",
           not any(l.startswith(b"t7:test:2\t") for l in cls) and
           sum(l.startswith(b"t7:test:1\toperativeWords") for l in cls) == 1, str([l for l in cls if b"t7:" in l]))
    hh = lines(os.path.join(d, "history.tsv"))
    expect("B history +1", len(hh) == len(H) + 1)
    hc = lines(os.path.join(d, "history_claim.tsv"))
    expect("B history_claim: first line per (id, claim); base id; claims file 3-col; bad id skipped",
           [l.split(b"\t")[:2] for l in hc] == [[b"h7:test:1", b"orderHead"], [b"h7:test:1", b"setAside"],
                                                [h0[0].encode(), b"setAside"], [h0[0].encode(), b"orderHead"]],
           str(hc))
    jl = lines(os.path.join(d, "joined.tsv"))
    expect("B joined: two per id, same line once, history table, unknown id skipped",
           sum(l.startswith(b"t7:test:1\t") for l in jl) == 2 and sum(l.startswith(b"h7:test:1\t") for l in jl) == 1
           and len(jl) == 3, str(jl))
    ha = lines(os.path.join(d, "history_anchor.tsv"))
    expect("B anchor +1", len(ha) == len(lines(os.path.join(BASE, "history_anchor.tsv"))) + 1)
    ct = lines(os.path.join(d, "cert_text.tsv"))
    expect("B cert_text +1 (clash skipped)", len(ct) == len(lines(os.path.join(BASE, "cert_text.tsv"))) + 1)
    ws = lines(os.path.join(d, "window_sha.tsv"))
    expect("B window_sha +1 (clash skipped)", len(ws) == len(lines(os.path.join(BASE, "window_sha.tsv"))) + 1)
    ci = lines(os.path.join(d, "cite_index.tsv"))
    expect("B cite_index +1 (ambiguity skipped)", len(ci) == len(lines(os.path.join(BASE, "cite_index.tsv"))) + 1)
    trow = [l for l in tt if l.startswith(t1[0].encode() + b"\t")]
    expect("B replace", trow and trow[0].decode().split("\t")[5] == t1r[5])
    man = open(os.path.join(d, "MANIFEST.txt"), encoding="utf-8").read()
    expect("B manifest notes remove_ids.txt", "remove_ids.txt lists 1 ids; not applied" in man)
    expect("B manifest replace counts", "1 rows changed, 0 identical, 1 ids not present" in man, man[-1500:])
    expect("B doctrine label check reported", "doctrine class lines 0" in man)
    # C: real deltas of rounds 5 and 6
    for name, dd in (("_st_ow", "round5/opwords/cert"), ("_st_rc", "round5/recog/cert"),
                     ("_st_rh", "round6/history/rules/rehear/cert")):
        out, d = stage(name, "--delta", os.path.join(C2, dd))
        m = re.search(r"  (treatments|history) \+(\d+) \(id present (\d+)", out)
        expect("C %s accepted" % dd, m is not None, out[-400:])
        if m:
            print("C %-34s %s +%s, id present %s" % (dd, m.group(1), m.group(2), m.group(3)))
    # D
    after = {t: sha(os.path.join(BASE, t + ".tsv")) for t in before}
    expect("D base untouched", after == before)
    for name in ("_st_a", "_st_fw", "_st_b", "_st_ow", "_st_rc", "_st_rh"):
        shutil.rmtree(os.path.join(R7, "stage", name), ignore_errors=True)
    print("%d checks, %d failed" % (N[0], len(FAILS)))
    for f in FAILS:
        print("FAIL", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
