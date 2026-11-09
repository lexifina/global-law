"""Render loophole_film.html (three.js, WebGL on the GPU) frame by frame and encode with NVENC.

    python video/render_film.py [--fps 30] [--still T ...]
-> video/out/us-tax-loopholes.mp4 (1920x1080)
"""
import argparse, json, subprocess, sys
from pathlib import Path
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FF = imageio_ffmpeg.get_ffmpeg_exe()
ARGS = ["--use-gl=angle", "--use-angle=d3d11", "--enable-gpu-rasterization", "--ignore-gpu-blocklist", "--enable-webgl",
        "--disable-web-security"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fps", type=int, default=30); ap.add_argument("--still", type=float, nargs="*")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    data = (HERE / "loophole_data.json").read_text(encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.add_init_script(f"window.LH = {data};")
        msgs = []
        pg.on("console", lambda m: msgs.append(m.text)); pg.on("pageerror", lambda e: msgs.append(str(e)))
        pg.goto((HERE / "loophole_film.html").as_uri())
        try:
            pg.wait_for_function("window.READY === true", timeout=90000)
        except Exception:
            print("\n".join(msgs)); raise
        if a.still is not None:
            for t in a.still:
                pg.evaluate(f"render({t})")
                pg.screenshot(path=str(OUT / f"lh_{t:05.1f}.png"))
            print("\n".join(m for m in msgs if "error" in m.lower())); b.close(); return
        dur = pg.evaluate("window.DUR"); n = int(dur * a.fps)
        cmd = [FF, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-", "-c:v", "h264_nvenc",
               "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
               str(OUT / "us-tax-loopholes.mp4")]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f"render({i / a.fps})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=95))
            if i % 300 == 0:
                print(f"frame {i}/{n}", flush=True)
        ff.stdin.close(); ff.wait(); b.close()
    if ff.returncode:
        sys.exit("ffmpeg failed")
    print("us-tax-loopholes.mp4", round((OUT / "us-tax-loopholes.mp4").stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
