"""Render statutes_film.html (three.js on the GPU) frame by frame and encode with NVENC, like render_caselaw.py.

    python video/render_statutes.py --build-data     # video/statutes_data.json from ~/Documents/us-caselaw-lean-work/usc
    python video/render_statutes.py [--fps 30] [--still T ...]
-> video/out/statutes-behind-us-case-law.mp4 and -share.mp4
"""
import argparse, json, subprocess, sys
from pathlib import Path
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FF = imageio_ffmpeg.get_ffmpeg_exe()
NAME = "statutes-behind-us-case-law"
ARGS = ["--use-gl=angle", "--use-angle=d3d11", "--enable-gpu-rasterization", "--ignore-gpu-blocklist", "--enable-webgl", "--disable-web-security"]
U = Path.home() / "Documents" / "us-caselaw-lean-work" / "usc"


def build_data():
    pts = json.loads((U / "film_points.json").read_text())
    cw = json.loads((U / "results" / "changed_words.json").read_text())
    sm = json.loads((U / "results" / "summary.json").read_text())
    au = json.loads((U / "results" / "audit_summary.json").read_text()) if (U / "results" / "audit_summary.json").exists() else {}
    fmt = lambda n: f"{n:,}"
    lv, lw = 0, set()
    for l in open(U / "versions.tsv", encoding="utf-8"):
        f = l.split("	")
        if f[2] == "law" and int(f[4]) >= 19950104:
            lv += 1; lw.add(f[3])
    S = dict(sections=sm["code_sections"], law_versions=lv, laws=len(lw), titles=53,
             citations=cw["rows"], decisions=cw["decisions"], both=cw["both"], both_pct=round(100 * cw["both"] / cw["rows"]),
             decisions_both=cw["decisions_both"], decisions_both_pct=round(100 * cw["decisions_both"] / cw["decisions"]))
    note = {"Pub. L. 110-177": "mostly lettering § 2255's paragraphs", "Pub. L. 115-391": "sentencing", "Pub. L. 109-8": "bankruptcy"}
    short = {"Pub. L. 115-391": "First Step Act", "Pub. L. 109-8": "Bankruptcy Abuse Prevention Act",
             "Pub. L. 110-177": "Court Security Improvement Act"}
    laws = [[short.get(k, n), y, c, note.get(k, "")] for k, n, y, c in cw["laws"][:3]]
    ex = dict(title="United States v. Angelos, Tenth Circuit, 2006",
              sub="Three counts under § 924(c) in one case: a mandatory 55 years in prison. Which words did the court apply, and do they still say it?",
              cite="18 U.S.C. § 924(c)(1)(C)", day="9 January 2006",
              then="“In the case of a <b>second or subsequent conviction</b> under this subsection, the person shall— (i) be sentenced to a term of imprisonment of not less than 25 years”",
              lean=[["in force that day", "the version of 26 October 2005 (Pub. L. 109-92)"],
                    ["changed since by", "3 laws: 2006, the First Step Act (2018), 2022"],
                    ["subsection (c) today", "<span style=\"color:#ff6a55;font-weight:600\">reads differently</span>"]],
              now="“In the case of a <b>violation of this subsection that occurs after a prior conviction under this subsection has become final</b>, the person shall— (i) be sentenced to a term of imprisonment of not less than 25 years”",
              res="<b>Changed by the First Step Act of 2018.</b> Counts charged together no longer stack; the change did not reach sentences already imposed.")
    end = (f'<span class="h">{fmt(S["decisions"])}</span><span>decisions since 1995, citing US Code sections {fmt(S["citations"])} times</span>'
           f'<span class="h">{S["both_pct"]}%</span><span>of those citations name words a later law has changed</span>'
           + (f'<span class="h">{au["end_h"]}</span><span>{au["end_t"]}</span>' if au else ''))
    out = dict(ch=pts["ch"], cit=pts["cit"], S=S, laws=laws, ex=ex, end=end)
    (HERE / "statutes_data.json").write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print("changes", len(pts["ch"]), "citations", len(pts["cit"]), S, laws)


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
        data = (HERE / "statutes_data.json").read_text(encoding="utf-8")
        with sync_playwright() as p:
            b = p.chromium.launch(args=ARGS)
            pg = b.new_page(viewport={"width": 1920, "height": 1080})
            pg.add_init_script(f"window.SL = {data};")
            msgs = []
            pg.on("console", lambda m: msgs.append(m.text)); pg.on("pageerror", lambda e: msgs.append(str(e)))
            pg.goto((HERE / "statutes_film.html").as_uri())
            try:
                pg.wait_for_function("window.READY === true", timeout=90000)
            except Exception:
                print("\n".join(msgs)); raise
            if a.still is not None:
                for t in a.still:
                    pg.evaluate(f"render({t})")
                    pg.screenshot(path=str(OUT / f"st_{t:05.1f}.png"))
                print("\n".join(m for m in msgs if "error" in m.lower())); b.close(); return
            dur = pg.evaluate("window.DUR"); n = int(dur * a.fps)
            cmd = [FF, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-", "-c:v", "h264_nvenc",
                   "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(main_mp4)]
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
    cmd = [FF, "-y", "-loglevel", "error", "-i", str(main_mp4), "-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr",
           "-b:v", "3600k", "-maxrate", "6000k", "-bufsize", "12000k", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(share_mp4)]
    if subprocess.run(cmd).returncode:
        sys.exit("ffmpeg share pass failed")
    print(share_mp4.name, round(share_mp4.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
