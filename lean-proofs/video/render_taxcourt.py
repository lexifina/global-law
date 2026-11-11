"""Render taxcourt_film.html (three.js, WebGL on the GPU) frame by frame and encode with NVENC.

    python video/render_taxcourt.py --build-data       # writes video/taxcourt_data.json from tax-formalization-data/taxcourt
    python video/render_taxcourt.py [--fps 30] [--still T ...] [--share-only]
-> video/out/recreating-tax-court-rulings.mp4 (1920x1080) and video/out/recreating-tax-court-rulings-share.mp4
"""
import argparse, collections, json, re, subprocess, sys
from pathlib import Path
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FF = imageio_ffmpeg.get_ffmpeg_exe()
SRC = Path.home() / "Documents" / "tax-formalization-data" / "taxcourt"
RULINGS = HERE.parent / "LegalProofs" / "USTax" / "TaxCourt" / "Rulings.lean"
NAME = "recreating-tax-court-rulings"
ARGS = ["--use-gl=angle", "--use-angle=d3d11", "--enable-gpu-rasterization", "--ignore-gpu-blocklist", "--enable-webgl",
        "--disable-web-security"]

VERDICT = {"match": 0, "mismatch": 1, "judgment": 2, "not-encodable": 3}
CAUSE = {None: 0, "facts-not-stated": 1, "court-or-irs-arithmetic": 2, "model-gap": 3}


def build_data():
    s = json.loads((SRC / "summary.json").read_text(encoding="utf-8"))
    cases = []
    for c in sorted(s["detail"], key=lambda c: (c["date"], c["id"])):
        iss = []
        for i in c["issues"]:
            ys = [int(y) for y in re.findall(r"\b(20[12]\d)\b", i["issue"]) if int(y) in c["years"]]
            iss.append([VERDICT[i["verdict"]], CAUSE[i.get("cause")], ys[0] if ys else c["years"][0]])
        y, m, d = map(int, c["date"].split("-"))
        cases.append([c["id"], round(y + (m - 1) / 12 + d / 365, 3), iss])
    # holdings re-checked by Lean: '#guard holds <case def> "<item>"' lines in Rulings.lean, counted per opinion
    guards = collections.OrderedDict()
    for d in re.findall(r"^#guard holds (\w+) ", RULINGS.read_text(encoding="utf-8"), re.M):
        k = re.sub(r"_\d+$", "", d) if re.match(r"tc(memo|summ)_\d{4}_\d+_\d+$", d) else d
        guards[k] = guards.get(k, 0) + 1
    differs = len(re.findall(r"^-- differs", RULINGS.read_text(encoding="utf-8"), re.M))
    tot = collections.Counter(v for c in cases for v, _, _ in c[2])
    out = dict(cases=cases, guards=list(guards.values()), differs=differs)
    (HERE / "taxcourt_data.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print("cases", len(cases), "issues", sum(tot.values()), dict(tot), "guards", sum(guards.values()), "in", len(guards),
          "opinions; differs", differs)
    assert (tot[0], tot[1], tot[2], tot[3]) == tuple(s["totals"][k] for k in ("match", "mismatch", "judgment", "not-encodable"))


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
        data = (HERE / "taxcourt_data.json").read_text(encoding="utf-8")
        with sync_playwright() as p:
            b = p.chromium.launch(args=ARGS)
            pg = b.new_page(viewport={"width": 1920, "height": 1080})
            pg.add_init_script(f"window.TC = {data};")
            msgs = []
            pg.on("console", lambda m: msgs.append(m.text)); pg.on("pageerror", lambda e: msgs.append(str(e)))
            pg.goto((HERE / "taxcourt_film.html").as_uri())
            try:
                pg.wait_for_function("window.READY === true", timeout=90000)
            except Exception:
                print("\n".join(msgs)); raise
            if a.still is not None:
                for t in a.still:
                    pg.evaluate(f"render({t})")
                    pg.screenshot(path=str(OUT / f"tc_{t:05.1f}.png"))
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
