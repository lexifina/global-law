"""Render formalize_film.html (three.js, WebGL on the GPU) frame by frame and encode with NVENC.

    python video/render_formalize.py --build-data       # writes video/formalize_data.json from tax-formalization-data
    python video/render_formalize.py [--fps 30] [--still T ...]
-> video/out/formalizing-the-us-tax-code.mp4 (1920x1080) and video/out/formalizing-the-us-tax-code-share.mp4
"""
import argparse, csv, json, math, random, re, subprocess, sys
from pathlib import Path
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FF = imageio_ffmpeg.get_ffmpeg_exe()
SRC = Path.home() / "Documents" / "tax-formalization-data"
NAME = "formalizing-the-us-tax-code"
ARGS = ["--use-gl=angle", "--use-angle=d3d11", "--enable-gpu-rasterization", "--ignore-gpu-blocklist", "--enable-webgl",
        "--disable-web-security"]

LEVEL = {"title": 0, "subtitle": 0, "chapter": 0, "subchapter": 0, "part": 0, "subpart": 0, "section": 1, "subsection": 2,
         "paragraph": 3, "subparagraph": 4, "clause": 5, "subclause": 6, "item": 7, "subitem": 8}
CLASS = {"dangling-word-ref": 0, "word-ref-to-inactive": 1, "historical-word-ref-to-inactive": 2,
         "historical-dangling-word-ref": 2, "dangling-ref": 3, "ref-to-inactive": 4, "wrong-level-word": 5,
         "duplicate-designation": 6, "unbalanced-parentheses": 7}
QTY = ["agi", "taxable", "taxBefore", "eitc", "actc", "nonref", "incomeTax"]


def build_data():
    d = json.loads((SRC / "out" / "t26.json").read_text(encoding="utf-8"))
    P = d["provisions"]
    ids = {p["id"]: i for i, p in enumerate(P)}

    def resolve(path):
        while path and path not in ids:
            path = path.rsplit("/", 1)[0]
        return ids.get(path)

    def cite(c):  # "§1401(b)(2)(B)" -> index
        c = c.replace("§§", "§").split("/")[0].strip()
        m = re.match(r"§\s*([0-9A-Za-z\-]+)((?:\([^)]+\))*)", c)
        if not m:
            return None
        parts = [m.group(1)] + re.findall(r"\(([^)]+)\)", m.group(2))
        return resolve("/us/usc/t26/s" + "/".join(parts))

    levels = "".join(str(LEVEL.get(p["kind"], 0)) for p in P)
    inactive = [i for i, p in enumerate(P) if p["status"] != "in-force"]
    refs = []
    for i, p in enumerate(P):
        for r in p["secrefs"] + p["rel"]:
            t = r.get("target") if isinstance(r, dict) else r
            if isinstance(t, str) and t.startswith("/us/usc/t26/"):
                j = resolve(t)
                if j is not None and j != i:
                    refs.append((i, j))
    random.seed(26)
    refs = random.sample(refs, min(7000, len(refs)))
    faults = []
    # the confirmed faults after triage (out/triage.csv: rows of the second run with verdict "confirmed")
    for row in csv.DictReader(open(SRC / "out" / "triage.csv", encoding="utf-8")):
        if not row["class_after"] or row["verdict"] != "confirmed":
            continue
        i = cite(row["citing"])
        if i is not None:
            faults.append([i, CLASS[row["class_after"]]])
    secs = {}
    for s in ["1", "61", "162", "401", "1401", "3101", "4001", "6001", "7701"]:
        i = ids.get(f"/us/usc/t26/s{s}")
        if i is not None:
            secs[s] = [i, P[i]["heading"]]
    ex = {k: ids[f"/us/usc/t26/{v}"] for k, v in
          {"citing": "s1401/b/2/B", "cited": "s3121/b/2", "meant": "s3101/b/2"}.items()}

    def tc_unsupported(h):  # as tools/taxcode/diff/compare.py
        if h["filing"] == "qss":
            return set(QTY)
        if h.get("studentLoanInterest"):
            return set(QTY) - {"eitc"}
        if h.get("retirementContributions") or h.get("qualifiedTuition"):
            return {"incomeTax", "nonref", "actc"}
        return set()

    def status(row, tool, h):
        r = row.get(tool)
        if not r:
            return 0
        skip = tc_unsupported(h) if tool == "tc" else set()
        seen = bad = False
        for q in QTY:
            if q in skip:
                continue
            a, b = row["lean"].get(q), r.get(q)
            if a is None or b is None:
                continue
            seen = True
            bad |= abs(a - b) > 10
        return 0 if not seen else (2 if bad else 1)

    hh = []
    for f, hf in [("rep2000.json", "h2000.json"), ("repx3000.json", "x3000.json")]:
        rows = json.loads((SRC / "diff" / f).read_text())["rows"]
        hs = json.loads((SRC / "diff" / hf).read_text())
        for row in rows:
            agi = max(row["lean"]["agi"], 1000)
            x = round(min(1, max(0, (math.log10(agi) - 3) / 4)), 4)  # $1,000 .. $10,000,000
            hh.append([x] + [status(row, t, hs[row["i"]]) for t in ("pe", "tc", "ut")])
    out = dict(N=len(P), levels=levels, inactive=inactive, refs=[x for r in refs for x in r], faults=faults, secs=secs,
               ex=ex, hh=hh)
    (HERE / "formalize_data.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    pe = sum(1 for h in hh if h[1] == 2)
    print("provisions", len(P), "refs drawn", len(refs), "faults", len(faults), "households", len(hh), "pe differ", pe,
          "KB", round((HERE / "formalize_data.json").stat().st_size / 1e3))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fps", type=int, default=30); ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--build-data", action="store_true"); ap.add_argument("--share-only", action="store_true")
    a = ap.parse_args()
    if a.build_data:
        return build_data()
    OUT.mkdir(exist_ok=True)
    main_mp4, share_mp4 = OUT / f"{NAME}.mp4", OUT / f"{NAME}-share.mp4"
    if not a.share_only:
        from playwright.sync_api import sync_playwright
        data = (HERE / "formalize_data.json").read_text(encoding="utf-8")
        with sync_playwright() as p:
            b = p.chromium.launch(args=ARGS)
            pg = b.new_page(viewport={"width": 1920, "height": 1080})
            pg.add_init_script(f"window.FZ = {data};")
            msgs = []
            pg.on("console", lambda m: msgs.append(m.text)); pg.on("pageerror", lambda e: msgs.append(str(e)))
            pg.goto((HERE / "formalize_film.html").as_uri())
            try:
                pg.wait_for_function("window.READY === true", timeout=90000)
            except Exception:
                print("\n".join(msgs)); raise
            if a.still is not None:
                for t in a.still:
                    pg.evaluate(f"render({t})")
                    pg.screenshot(path=str(OUT / f"fz_{t:05.1f}.png"))
                print("\n".join(m for m in msgs if "error" in m.lower())); b.close(); return
            dur = pg.evaluate("window.DUR"); n = int(dur * a.fps)
            cmd = [FF, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-", "-c:v", "h264_nvenc",
                   "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                   str(main_mp4)]
            ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            for i in range(n):
                pg.evaluate(f"render({i / a.fps})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=95))
                if i % 300 == 0:
                    print(f"frame {i}/{n}", flush=True)
            ff.stdin.close(); ff.wait(); b.close()
        if ff.returncode:
            sys.exit("ffmpeg failed")
        print(main_mp4.name, round(main_mp4.stat().st_size / 1e6, 1), "MB")
    # share version: second NVENC pass at the reference share bitrate (~3.6 Mbit/s, ~32 MB for 72 s)
    cmd = [FF, "-y", "-loglevel", "error", "-i", str(main_mp4), "-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr",
           "-b:v", "3600k", "-maxrate", "6000k", "-bufsize", "12000k", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(share_mp4)]
    if subprocess.run(cmd).returncode:
        sys.exit("ffmpeg share pass failed")
    print(share_mp4.name, round(share_mp4.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
