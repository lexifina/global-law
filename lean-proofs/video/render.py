"""Render anim.html frame by frame (deterministic) and encode with ffmpeg (NVENC on the GPU when available).
python video/render.py [--fps 30] [--still T ...]
-> video/out/lean-proofs.mp4 (1920x1080)."""
import argparse, subprocess, sys
from pathlib import Path
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FF = imageio_ffmpeg.get_ffmpeg_exe()
ARGS = ["--use-gl=angle", "--use-angle=d3d11", "--enable-gpu-rasterization", "--ignore-gpu-blocklist"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fps", type=int, default=30); ap.add_argument("--still", type=float, nargs="*")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto((HERE / "anim.html").as_uri())
        pg.wait_for_function("window.READY === true", timeout=60000)
        canvas = pg.locator("canvas")
        if a.still is not None:
            for t in a.still:
                pg.evaluate(f"render({t})")
                canvas.screenshot(path=str(OUT / f"still_{t:05.1f}.png"))
            b.close(); return
        dur = pg.evaluate("window.DUR")
        n = int(dur * a.fps)
        enc = ["-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", "19", "-b:v", "0"]
        cmd = [FF, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-", *enc,
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT / "lean-proofs.mp4")]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f"render({i / a.fps})")
            ff.stdin.write(canvas.screenshot(type="png"))
            if i % 150 == 0:
                print(f"frame {i}/{n}", flush=True)
        ff.stdin.close(); ff.wait()
        b.close()
    if ff.returncode != 0:
        sys.exit("ffmpeg failed")
    for f in ("lean-proofs.mp4",):
        print(f, round((OUT / f).stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
