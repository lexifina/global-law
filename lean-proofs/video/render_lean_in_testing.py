"""Render lean_in_testing_film.html frame by frame with Playwright and encode with ffmpeg, like render_caselaw2.py.

    python video/render_lean_in_testing.py --build-data      # writes video/lean_in_testing_data.json
    python video/render_lean_in_testing.py --still 3 12 20   # video/out/lit_003.00.png ...
    python video/render_lean_in_testing.py --checks          # stills at 40% and 90% of every scene
    python video/render_lean_in_testing.py [--fps 30]        # video/out/lean-in-testing.mp4 and lean-in-testing-share.mp4
    python video/render_lean_in_testing.py --share-only      # only re-encode the share cut from the mp4

Every fact in the film is read here from ~/Documents/us-caselaw-lean-work/caselaw-lean-2 (round-4 final outputs; the
round5 folder is never opened) and from the Lean sources in LegalProofs/CaseLaw2. A fact that cannot be found, or that
disagrees with eval/score_final.txt, stops the build. The sources are listed in lean_in_testing_sources.md.
"""
import argparse, collections, hashlib, json, re, subprocess, sys, time
from pathlib import Path
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FF = imageio_ffmpeg.get_ffmpeg_exe()
NAME = "lean-in-testing"
FILM = HERE / "lean_in_testing_film.html"
DATA = HERE / "lean_in_testing_data.json"
ARGS = ["--use-gl=angle", "--use-angle=d3d11", "--enable-gpu-rasterization", "--ignore-gpu-blocklist"]

W = Path.home() / "Documents" / "us-caselaw-lean-work"
C = W / "caselaw-lean-2"
LEAN = HERE.parent / "LegalProofs" / "CaseLaw2"
MONTHS = "January February March April May June July August September October November December".split()

LAW, BOW = 6218081, 6102809          # Lawrence v. Texas, Bowers v. Hardwick (graph/nodes.tsv ids)
REJ = "t:280701:5952856:16930"       # the rejected row shown: In re Friedenberg on Tinker v. Colwell
CITERS = ["Summerlin v. Stewart", "Latta v. Otter", "Bostock v. Clayton County"]
NEG_KINDS = {"overruled", "disapproved", "recededFrom", "abrogated", "supersededByEnactment"}  # eval/score.py


def day(d):
    d = int(d)
    return f"{d % 100} {MONTHS[d // 100 % 100 - 1]} {d // 10000}"


def rows(p, skip=0):
    with open(p, encoding="utf-8", newline="\n") as f:
        for i, l in enumerate(f):
            if i >= skip:
                yield l.rstrip("\n").split("\t")


def stop(msg):
    sys.exit("build-data: " + msg)


def need(pattern, text, what):
    m = re.search(pattern, text)
    if not m:
        stop(f"cannot find {what}")
    return m


def num(s):
    return int(s.replace(",", ""))


def lean_list(src, pattern, what):
    m = need(pattern, src, what)
    return re.findall(r'"([^"]*)"', m[1])


def certificate(tr, cues, disq):
    """The text facts of one treatments row, re-checked here against cert_text.tsv and window_sha.tsv."""
    sha, a, b, quote = tr[8], int(tr[9]), int(tr[10]), tr[11]
    win = next((f for f in rows(C / "data" / "cert_text.tsv") if f[0] == sha and int(f[1]) <= a and b <= int(f[2])), None)
    if win is None:
        stop(f"{tr[0]}: no window covers the quote")
    w0, w1 = int(win[1]), int(win[2])
    if win[3][a - w0:b - w0] != quote:
        stop(f"{tr[0]}: the quote is not at its offset in the window")
    rec = next((f[3] for f in rows(C / "data" / "window_sha.tsv") if f[0] == sha and int(f[1]) == w0 and int(f[2]) == w1), None)
    if rec is None:
        stop(f"{tr[0]}: no recorded window hash")
    cue = next((c for c in cues if c in quote.lower()), None)
    if cue is None or any(d in quote.lower() for d in disq):
        stop(f"{tr[0]}: cue or disqualifier differs from the Lean verdict")
    return dict(id=tr[0], sha=sha, start=a, end=b, quote=quote, evidence=tr[12], part=tr[13], kind=tr[4], scope=tr[5],
                w0=w0, w1=w1, wsha=rec, wsha_same=hashlib.sha1(win[3].encode("utf-8")).hexdigest() == rec, cue=cue)


def build_data():
    D = {}
    # ---- the checker: the order of the checks is the order of the failures in `def check` (Certificate.lean) ----
    cert_src = (LEAN / "Certificate.lean").read_text(encoding="utf-8")
    body = need(r"(?s)def check \(c : Input\) : Result :=\n(.*?)\n\n", cert_src, "def check")[1]
    D["checks"] = re.findall(r"\.fail \.(\w+)", body)
    if D["checks"] != ["shaUnknown", "noWindow", "windowHash", "quoteMismatch", "noCue", "disqualified", "targetUnresolved",
                       "partNotMajority", "targetLater", "noAuthority"]:
        stop(f"the checker's order changed: {D['checks']}")
    need(r"theorem checkCert_sound \(c : Input\) \(h : \(check c\)\.admitted = true\)", cert_src, "checkCert_sound")
    cue_src = (LEAN / "CueTable.lean").read_text(encoding="utf-8")
    cues = lean_list(cue_src, r"\| \.overruled => \[(.*?)\]", "the overruled cues")
    disq = lean_list(cue_src, r"def treatDisqualifiers : List String :=\s*\[(.*?)\]", "the disqualifiers")
    st_src = (LEAN / "Spec" / "Status.lean").read_text(encoding="utf-8")
    need(r"theorem status_perm \{l₁ l₂ : List Effect\} \(h : l₁\.Perm l₂\) \(k : Nat\) \(t u : Date\) :\s*status l₁ k t u = status l₂ k t u", st_src, "status_perm")
    need(r"def Status\.join \(a b : Status\) : Status := if a\.rank ≤ b\.rank then b else a", st_src, "Status.join")
    need(r"effs\.foldl \(fun s e => s\.join \(e\.contrib k t u\)\) \.good", st_src, "status as a fold of join")
    neg = need(r"inductive Neg where\s*\n\s*\| (.*?)\n", st_src, "Neg")[1].split(" | ")
    D["neg"] = neg                                                    # least severe first
    ex_src = (LEAN / "Examples.lean").read_text(encoding="utf-8")
    need(r"#guard st 2 0 20030625 20030625 == \.good\n#guard st 2 0 20030626 20030626 == \.neg \.overruled", ex_src, "the Bowers example")
    mu_src = (LEAN / "Mutants.lean").read_text(encoding="utf-8")
    need(r'\("M7 cert accepts dissents", \{ check := m7check \}\)', mu_src, "mutant M7")
    need(r'\("checkCert_sound: part", fun i =>\s*!\(i\.check \{ certGideon with part := "dissent" \}\)\.admitted\)', mu_src, "the property that kills M7")

    # ---- certificates ----
    cres = {f[1]: f[2:] for f in rows(C / "out" / "certs.tsv", 1) if f[0] == "treatment"}
    treat = list(rows(C / "data" / "treatments.tsv"))
    lt = [f for f in treat if int(f[1]) == LAW and int(f[2]) == BOW]
    if len(lt) != 1 or cres[lt[0][0]] != ["ok", "ok"] or lt[0][7] != "1":
        stop("Lawrence on Bowers is not one admitted explicit row")
    lt = lt[0]
    rj = next(f for f in treat if f[0] == REJ)
    if cres[REJ] != ["noAuthority", "noAuthority"]:
        stop("the rejected row is no longer rejected for noAuthority")

    # ---- decisions needed: courts and dates (decisions2.tsv is streamed) ----
    adm = {}
    for f in treat:
        if f[14].endswith(":implicit"):
            continue
        if cres.get(f[0], ["missing"])[0] == "ok" and f[7] == "1" and f[4] in NEG_KINDS:
            adm[int(f[1]), int(f[2])] = f[4]
    fin = [f for f in rows(C / "out" / "findings.tsv", 1) if f[2] == str(BOW)]
    co = [f for f in fin if f[0] == "citesOverruled"]
    if any(f[4] != "neg:overruled" for f in co):
        stop("a citesOverruled finding on Bowers has another status")
    want = {x for _, x in adm} | {int(f[1]) for f in co} | {LAW, BOW, int(rj[1]), int(rj[2])}
    court, date = {}, {}
    for f in rows(C / "data" / "decisions2.tsv"):
        i = int(f[0])
        if i in want:
            court[i], date[i] = int(f[1]), int(f[2])
    cinfo = {}
    for f in rows(C / "data" / "courts2.tsv"):
        cinfo.setdefault(int(f[0]), (f[3], int(f[4]), f[5]))
    scotus = lambda n: n in court and cinfo[court[n]][1] == 0 and cinfo[court[n]][2] == "L"
    names = {}
    for f in rows(W / "graph" / "nodes.tsv"):
        i = int(f[0])
        if i in (LAW, BOW, int(rj[1]), int(rj[2])) or (i in date and f[6] in CITERS and any(int(x[1]) == i for x in co)):
            names[i] = dict(name=f[6], cite=f[5].split("|")[0], date=int(f[4]))

    # ---- the admitted sentence ----
    c = certificate(lt, cues, disq)
    if not (scotus(LAW) and scotus(BOW) and date[BOW] <= date[LAW] == int(lt[3])):
        stop("Lawrence / Bowers: courts or dates differ")
    if not c["wsha_same"]:
        stop("Lawrence: the window's SHA-1 computed here is not the recorded one")
    c.update(by=names[LAW]["name"], by_cite=names[LAW]["cite"], by_day=day(lt[3]), by_year=int(lt[3]) // 10000,
             target=names[BOW]["name"], target_cite=names[BOW]["cite"], target_day=day(names[BOW]["date"]),
             target_year=names[BOW]["date"] // 10000, court=cinfo[court[LAW]][0], result=cres[lt[0]][0])
    D["law"] = c
    # ---- the rejected sentence ----
    r = certificate(rj, cues, disq)
    if rj[13] != "majority" or not date[int(rj[2])] <= date[int(rj[1])] or not scotus(int(rj[2])) or scotus(int(rj[1])):
        stop("the rejected row no longer passes the checks before noAuthority")
    r.update(by=names[int(rj[1])]["name"], by_cite=names[int(rj[1])]["cite"], by_day=day(rj[3]), by_year=int(rj[3]) // 10000,
             court=cinfo[court[int(rj[1])]][0], tier=cinfo[court[int(rj[1])]][2], target=names[int(rj[2])]["name"],
             target_cite=names[int(rj[2])]["cite"], target_year=names[int(rj[2])]["date"] // 10000,
             target_court=cinfo[court[int(rj[2])]][0], result=cres[REJ][0])
    D["rej"] = r

    # ---- status of Bowers (decision level: issue and holding are '-') ----
    st = [f for f in rows(C / "out" / "status.tsv", 1) if f[0] == str(BOW) and f[1] == "-" and f[2] == "-"]
    if [(f[3], f[4], f[5]) for f in st] != [("0", "20030625", "good"), ("20030626", st[-1][4], "neg:overruled")] or st[1][8] != lt[0]:
        stop("Bowers: unexpected status rows")
    if sum(1 for f in treat if int(f[2]) == BOW) != 1:
        stop("Bowers: more than one treatment row")
    D["status"] = dict(decided=names[BOW]["date"], good_to=int(st[0][4]), neg_from=int(st[1][3]), run_to=int(st[1][4]),
                       good_to_day=day(st[0][4]), neg_from_day=day(st[1][3]), status=st[1][5], witness=st[1][8])

    # ---- findings: later decisions citing Bowers while it is overruled ----
    if any(date[int(f[1])] < int(st[1][3]) for f in co):
        stop("a citesOverruled finding is dated before the overruling")
    ex = []
    for nm in CITERS:
        i = next(i for i, v in names.items() if v["name"] == nm)
        ex.append(dict(name=nm, cite=names[i]["cite"], year=date[i] // 10000, date=date[i], court=cinfo[court[i]][0]))
    D["find"] = dict(n=len(co), citing=len({f[1] for f in co}), dates=sorted(date[int(f[1])] for f in co),
                     first_day=day(min(date[int(f[1])] for f in co)), last_day=day(max(date[int(f[1])] for f in co)), examples=ex)

    # ---- the test: Supreme Court Database and the Constitution Annotated table (gold/, never read by the readers) ----
    ev = json.loads((C / "eval" / "score_final.txt").read_text(encoding="utf-8"))
    sc = list(rows(C / "gold" / "scdb.tsv", 1))
    flagged = {int(f[0]): f for f in sc if f[8] == "1" and int(f[0]) >= 0}
    allsc = {int(f[0]) for f in sc if int(f[0]) >= 0}
    acting = {y for (y, x) in adm if y in allsc and scotus(x)}
    e = ev["scdb"]
    got = [len(flagged), len(acting & set(flagged)), len(acting)]
    if got != [e["flagged_decisions"], e["flagged_with_admitted_overruling"], e["scotus_decisions_with_admitted_overruling_of_scotus"]] \
            or e["of_which_flagged"] != got[1] or len(adm) != ev["inputs"]["admitted"]:
        stop(f"SCDB figures {got} differ from eval/score_final.txt")
    order = sorted(flagged, key=lambda n: (int(flagged[n][4]), n))
    lw = flagged[LAW]
    D["scdb"] = dict(flagged=got[0], found=got[1], named=got[2], cells=[[int(flagged[n][4]) // 10000, int(n in acting)] for n in order],
                     law_index=order.index(LAW), law_id=lw[2], law_cite=lw[3], law_alt=lw[8], law_found=int(LAW in acting),
                     first_year=int(flagged[order[0]][4]) // 10000, last_year=int(flagged[order[-1]][4]) // 10000)
    cr = [f for f in rows(C / "gold" / "crs_overruled.tsv", 1) if f[0] == str(LAW) and f[1] == str(BOW)]
    if len(cr) != 1 or cr[0][9] != "1" or (LAW, BOW) not in adm:
        stop("Lawrence / Bowers is not one row of the current Constitution Annotated table")
    D["crs"] = dict(by=cr[0][2], by_cite=cr[0][3], target=cr[0][4], target_cite=cr[0][5], found=ev["crs"]["current_table"]["found"],
                    resolved=ev["crs"]["current_table"]["resolved"])
    need(r"evaluation only; never read by the reader or holdings agents", (C / "gold" / "README.md").read_text(encoding="utf-8"), "gold is held out")

    # ---- checked three ways (round 4 final) ----
    trust = (C / "TRUST.md").read_text(encoding="utf-8")
    lean = (C / "LEAN.md").read_text(encoding="utf-8")
    r4 = (C / "ROUND4.md").read_text(encoding="utf-8")
    dt = (C / "DIFFTEST.md").read_text(encoding="utf-8")
    thm = num(need(r"\*\*Proved:\*\* ([\d,]+) kernel-checked theorems, each statement locked", trust, "theorems")[1])
    m = need(r"\*\*Mutation:\*\* (\d+) properties against (\d+) mutants, all killed", lean, "mutants")
    m4 = need(r"\| Theorems / mutants killed \|.*\| (\d+) / (\d+) \|\n", r4, "ROUND4 theorems / mutants")
    if [thm, int(m[2])] != [int(m4[1]), int(m4[2])]:
        stop("TRUST.md / LEAN.md and ROUND4.md disagree on theorems or mutants")
    d = need(r"\| Real data \(`real20`\) \| certs \*\*0/([\d,]+)\*\*, splits \*\*0/([\d,]+)\*\*, conflicts \*\*0/([\d,]+)\*\*, status \*\*0/([\d,]+)\*\*, findings \*\*0/([\d,]+)\*\* \|", dt, "DIFFTEST real20")
    need(r"independent Python reference", dt, "the Python reference")
    D["ver"] = dict(theorems=thm, props=int(m[1]), mutants=int(m[2]), dt_certs=num(d[1]), dt_status=num(d[4]), dt_findings=num(d[5]),
                    mutant="M7 cert accepts dissents", killer="checkCert_sound")
    DATA.write_text(json.dumps(D, separators=(",", ":"), ensure_ascii=False), encoding="utf-8", newline="\n")
    show = {k: v for k, v in D.items()}
    show["scdb"] = {k: v for k, v in D["scdb"].items() if k != "cells"}
    show["find"] = {k: v for k, v in D["find"].items() if k != "dates"}
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(show, indent=1, ensure_ascii=False))


def encode(cmd_tail, src_args, out, attempts=3):
    """NVENC first (as the other films), libx264 if the GPU encoder is busy or missing."""
    encoders = [["-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr"] + cmd_tail[0],
                ["-c:v", "libx264", "-preset", "slow"] + cmd_tail[1]]
    return [[FF, "-y", "-loglevel", "error", *src_args, *e, "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(out)] for e in encoders]


def open_page(p):
    b = p.chromium.launch(args=ARGS)
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.add_init_script(f"window.LIT = {DATA.read_text(encoding='utf-8')};")
    msgs = []
    pg.on("console", lambda m: msgs.append(m.text)); pg.on("pageerror", lambda e: msgs.append(str(e)))
    pg.goto(FILM.as_uri())
    try:
        pg.wait_for_function("window.READY === true", timeout=180000)
    except Exception:
        print("\n".join(msgs)); raise
    return b, pg, msgs


def render_frames(fps, mp4, cmd):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b, pg, msgs = open_page(p)
        dur = pg.evaluate("window.DUR"); n = int(round(dur * fps))
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        try:
            for i in range(n):
                pg.evaluate(f"render({i / fps})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=95))
                if i % 300 == 0:
                    print(f"frame {i}/{n}", flush=True)
            ff.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        ff.wait(); b.close()
        return ff.returncode == 0 and mp4.exists() and mp4.stat().st_size > 100000


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fps", type=int, default=30); ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--checks", action="store_true"); ap.add_argument("--build-data", action="store_true"); ap.add_argument("--share-only", action="store_true")
    a = ap.parse_args()
    if a.build_data:
        return build_data()
    OUT.mkdir(exist_ok=True)
    mp4 = OUT / f"{NAME}.mp4"
    share = OUT / f"{NAME}-share.mp4"
    if a.still is not None or a.checks:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b, pg, msgs = open_page(p)
            ts = list(a.still or [])
            if a.checks:   # 40% and 90% of every scene
                for s in pg.evaluate("window.SCENES"):
                    ts += [round(s[1] + f * (s[2] - s[1]), 2) for f in (.4, .9)]
            for t in ts:
                pg.evaluate(f"render({t})")
                pg.screenshot(path=str(OUT / f"lit_{t:06.2f}.png"))
            print(" ".join(f"{t:06.2f}" for t in ts)); print("\n".join(m for m in msgs if "error" in m.lower())); b.close()
        return
    if not a.share_only:
        cmds = encode([["-cq", "17", "-b:v", "0"], ["-crf", "16"]], ["-f", "image2pipe", "-framerate", str(a.fps), "-i", "-"], mp4)
        done = False
        for k in range(4):   # another job may be holding the GPU or the CPU: retry, then fall back to libx264
            try:
                done = render_frames(a.fps, mp4, cmds[0 if k < 2 else 1])
            except Exception as e:
                print("render attempt failed:", e, flush=True)
            if done:
                break
            time.sleep(5)
        if not done:
            sys.exit("render failed")
    print(mp4, round(mp4.stat().st_size / 1e6, 1), "MB")
    # share version: a second pass at the set's share bitrate (~3.6 Mbit/s), as render_caselaw2.py does
    # (this film is mostly still frames, so the master is already small: the share cut never asks for more than 60% of it)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", subprocess.run([FF, "-i", str(mp4)], capture_output=True, text=True).stderr)
    secs = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    kb = min(3600, int(mp4.stat().st_size * 8 / 1000 / secs * .6))
    rate = ["-b:v", f"{kb}k", "-maxrate", f"{kb * 5 // 3}k", "-bufsize", f"{kb * 10 // 3}k"]
    cmds = encode([rate, rate], ["-i", str(mp4)], share)
    for cmd in (cmds[0], cmds[0], cmds[1]):
        if subprocess.run(cmd).returncode == 0:
            break
    else:
        sys.exit("ffmpeg share pass failed")
    print(share, round(share.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
