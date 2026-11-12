"""Render code_dynamics.svg to PNG with headless Chrome (fonts from Google Fonts), at full and blog width."""
import os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__))
svg = open(os.path.join(D, "code_dynamics.svg"), encoding="utf-8").read()
h = int(svg.split('viewBox="0 0 1400 ')[1].split('"')[0])
CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
for wd, name in ((1400, "code_dynamics.png"), (760, "code_dynamics_760.png")):
    html = ('<!doctype html><html><head><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600'
            '&family=JetBrains+Mono:wght@400;600&display=block" rel="stylesheet"><style>body{margin:0;background:#fff}'
            f'svg{{width:{wd}px;display:block}}</style></head><body>{svg}</body></html>')
    p = os.path.join(D, "_render.html")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    subprocess.run([CH, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={wd},{round(h * wd / 1400)}",
                    "--virtual-time-budget=5000", f"--screenshot={os.path.join(D, name)}", "file:///" + p.replace(os.sep, "/")],
                   check=True, capture_output=True)
os.remove(p)
print("ok")
