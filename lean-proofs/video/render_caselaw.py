"""Render caselaw_film.html (three.js, WebGL on the GPU) frame by frame and encode with NVENC.

    python video/render_caselaw.py --build-data        # writes video/caselaw_data.json from ~/Documents/us-caselaw-lean-work
    python video/render_caselaw.py [--fps 30] [--still T ...] [--share-only]
-> video/out/formalizing-all-us-case-law.mp4 (1920x1080) and video/out/formalizing-all-us-case-law-share.mp4
"""
import argparse, collections, json, re, subprocess, sys
from pathlib import Path
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FF = imageio_ffmpeg.get_ffmpeg_exe()
NAME = "formalizing-all-us-case-law"
ARGS = ["--use-gl=angle", "--use-angle=d3d11", "--enable-gpu-rasterization", "--ignore-gpu-blocklist", "--enable-webgl",
        "--disable-web-security"]

W = Path.home() / "Documents" / "us-caselaw-lean-work"


def build_data():
    sys.path.insert(0, str(HERE.parent / "tools" / "caselaw"))
    from courts_map import STATES
    import random
    random.seed(1963)
    lin, lout = W / "lean-in-v3", W / "lean-out-v3"
    courts = {}
    for l in open(lin / "courts.tsv", encoding="utf-8"):
        i, s, t, c = l.rstrip("\n").split("\t")
        courts[int(i)] = (int(s), t)
    rows = ["Federal"] + STATES[:56]
    def row(c):
        s, t = courts.get(c, (999, "T"))
        return None if s == 999 or s > 56 else s
    dc, dd, pts = {}, {}, []
    for l in open(lin / "decisions.tsv", encoding="utf-8"):
        i, c, d = l.split("\t")
        i, c, d = int(i), int(c), int(d)
        dc[i], dd[i] = c, d
        r = row(c)
        if r is not None and d > 0 and random.random() < 36000 / 6.9e6:
            pts.append([d // 10000, r, courts[c][1]])
    ok, bad = [], []
    for l in open(lout / "00.acts.tsv", encoding="utf-8"):
        y, x, v = l.rstrip("\n").split("\t")
        y = int(y)
        r = row(dc[y])
        if r is None:
            continue
        (ok if v == "1" else bad).append([dd[y] // 10000, r, courts[dc[y]][1]] if v == "1" else [dd[y] // 10000, r])
    summ = json.loads((W / "results" / "summary_v3.json").read_text())
    corr = json.loads((W / "results" / "corroborated_v3.json").read_text())
    st = json.loads((W / "results" / "statutes_summary.json").read_text())
    named = sum(v for k, v in summ["reports"].items() if k.startswith("named:"))
    S = dict(decisions=summ["decisions"], citations=summ["citations"], acts=summ["acts"], acts_valid=summ["acts_valid"],
             notes=named, agree_pct=round(100 * summ["reports"]["named:match"] / named),
             corr_citations=corr["citations"], stat_pct=round(100 * st["decisions_with_changed_section"] / st["decisions"]))
    out = dict(pts=pts, ok=ok, bad=bad, rows=rows, S=S)
    (HERE / "caselaw_data.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print("points", len(pts), "ok", len(ok), "bad", len(bad), S)


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
        data = (HERE / "caselaw_data.json").read_text(encoding="utf-8")
        with sync_playwright() as p:
            b = p.chromium.launch(args=ARGS)
            pg = b.new_page(viewport={"width": 1920, "height": 1080})
            pg.add_init_script(f"window.CL = {data};")
            msgs = []
            pg.on("console", lambda m: msgs.append(m.text)); pg.on("pageerror", lambda e: msgs.append(str(e)))
            pg.goto((HERE / "caselaw_film.html").as_uri())
            try:
                pg.wait_for_function("window.READY === true", timeout=90000)
            except Exception:
                print("\n".join(msgs)); raise
            if a.still is not None:
                for t in a.still:
                    pg.evaluate(f"render({t})")
                    pg.screenshot(path=str(OUT / f"cl_{t:05.1f}.png"))
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
    # share version: second NVENC pass at the reference share bitrate (~3.6 Mbit/s)
    cmd = [FF, "-y", "-loglevel", "error", "-i", str(main_mp4), "-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr",
           "-b:v", "3600k", "-maxrate", "6000k", "-bufsize", "12000k", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(share_mp4)]
    if subprocess.run(cmd).returncode:
        sys.exit("ffmpeg share pass failed")
    print(share_mp4.name, round(share_mp4.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
