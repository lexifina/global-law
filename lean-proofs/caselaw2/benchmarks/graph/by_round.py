"""Line charts of every blind answer key across the frozen builds: recall, or precision (axis from 50%).

    python3 -I by_round.py recall|precision OUT_DIR [--png]

Reads rows.tsv beside this script; writes benchmarks-by-round[-precision].svg, and with --png a 2800 px PNG
rendered by headless Chrome (needs Chrome installed).
"""
import csv, os, shutil, subprocess, sys, tempfile
METRIC = sys.argv[1]
OUT_DIR = sys.argv[2]
PNG = '--png' in sys.argv
SUF = '' if METRIC == 'recall' else '-precision'
YMIN = 0 if METRIC == 'recall' else 50

ROWS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rows.tsv')
OUT_SVG = os.path.join(OUT_DIR, f'benchmarks-by-round{SUF}.svg')
OUT_PNG = os.path.join(OUT_DIR, f'benchmarks-by-round{SUF}.png')
# (dataset, split, metric, label, colour)
KEYS = [
    ('scdb_disposition', 'h1', 'recall', 'Supreme Court Database', '#ff6a55'),
    ('shadow_docket', 'h1', 'recall', 'Shadow Docket', '#ffb454'),
    ('fjc_idb_unpub', 'all', 'recall', 'FJC, unpublished appeals', '#f2e36b'),
    ('fjc_idb_appeals', 'h1', 'recall', 'FJC appeals', '#9be36b'),
    ('brace_hall_state', 'all', 'recall', 'Brace & Hall (state)', '#4fd1a5'),
    ('fedcir_dataset', 'all', 'recall', 'Federal Circuit', '#4cc9f0'),
    ('bhk_enbanc', 'all', 'recall', 'En banc rehearings', '#6f8cff'),
    ('shepardized_coa', 'sealed', 'recall', 'Shepard’s', '#b388ff'),
    ('songer_treat', 'all', 'recall', 'Songer appeals', '#ff7eb6'),
    ('gold_fresh', 'sealed', 'recall', 'Unopened overruling lists', '#e8edf2'),
    ('holdout_notes', 'all', 'recall', 'Held-out overruling notes', '#9aa6b5'),
    ('state_overruled_tables', 'h1', 'recall', 'Pre-1930 state tables', '#c08457'),
]
BUILDS = ['round4', 'round5', 'round6', 'round7', 'round8', 'round9', 'round10', 'round11', 'round12', 'round13']

data = {}
with open(ROWS, encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        data[(r['dataset'], r['split'], r['metric'], r['label'])] = float(r['p']) * 100

series = []
for ds, sp, me, lab, col in KEYS:
    ys = [data.get((ds, sp, METRIC, b)) for b in BUILDS]
    if ys[-1] is None:
        continue
    assert ys[0] is not None, (ds, ys)
    series.append((lab, col, ys))

FOOT = ('Share of the decisions each key marks reversed, vacated or overruled that the model also marks.' if METRIC == 'recall' else 'Share of the decisions the model marks reversed, vacated or overruled that the key agrees with. Axis starts at 50%. Keys with no clean decisions are left out.')
TITLE = 'Recall: how much of each blind answer key the model finds' if METRIC == 'recall' else 'Precision: how often the model’s marks are right, by each blind key'
W, H = 1400, 890
L, R, T, B = 90, 1060, 150, 760
SANS = 'IBM Plex Sans,system-ui,sans-serif'
MONO = 'JetBrains Mono,ui-monospace,monospace'
X = lambda i: L + (R - L) * i / (len(BUILDS) - 1)
Y = lambda v: B - (B - T) * (v - YMIN) / (100 - YMIN)

o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{TITLE}, for each frozen build from round 4 to round 13">',
     f'<rect width="{W}" height="{H}" rx="14" fill="#0f1720"/>',
     f'<text x="44" y="60" font-family="{SANS}" font-size="24" fill="#9aa6b5">{TITLE}, build by build</text>',
     f'<text x="44" y="92" font-family="{SANS}" font-size="14" fill="#8b97a6">Each round is one frozen build, scored on the blind half of every key.</text>']
for v in range(YMIN, 101, 25 if YMIN == 0 else 10):
    o.append(f'<line x1="{L}" y1="{Y(v)}" x2="{R}" y2="{Y(v)}" stroke="#2a3542"{"" if v in (YMIN, 100) else " stroke-dasharray=\"3 5\""}/>')
    o.append(f'<text x="{L - 14}" y="{Y(v) + 4}" text-anchor="end" font-family="{MONO}" font-size="12" fill="#8b97a6">{v}%</text>')
for i, b in enumerate(BUILDS):
    o.append(f'<text x="{X(i)}" y="{B + 28}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="#8b97a6">R{b[5:]}</text>')
o.append(f'<text x="{(L + R) / 2}" y="{B + 56}" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="1" fill="#8b97a6">BUILD</text>')
for lab, col, ys in series:
    pts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(ys) if v is not None)
    o.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linejoin="round"/>')
    for i, v in enumerate(ys):
        if v is None:
            continue
        o.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.5" fill="{col}"/>')
# end labels, spread so they do not collide
ends = sorted(((Y(ys[-1]), lab, col, ys[-1]) for lab, col, ys in series))
GAP = 22
pos = []
for y, *_ in ends:
    pos.append(max(y, pos[-1] + GAP) if pos else y)
over = pos[-1] - (B + 6)
if over > 0:
    pos = [p - over for p in pos]
    for k in range(len(pos) - 2, -1, -1):
        pos[k] = min(pos[k], pos[k + 1] - GAP)
for (y, lab, col, v), py in zip(ends, pos):
    o.append(f'<path d="M{R + 6},{y:.1f} L{R + 22},{py:.1f} L{R + 30},{py:.1f}" fill="none" stroke="{col}" stroke-opacity="0.6"/>')
    o.append(f'<text x="{R + 36}" y="{py + 5:.1f}" font-family="{SANS}" font-size="15" fill="#eef1f5"><tspan font-weight="600" fill="{col}">{int(v + 0.5)}%</tspan>  {lab.replace("&", "&amp;")}</text>')
o.append(f'<text x="44" y="{H - 26}" font-family="{SANS}" font-size="13" fill="#8b97a6">{FOOT} FJC: Federal Judicial Center. Round 5 was scored only on the unopened lists.</text>')
o.append('</svg>\n')
svg = '\n'.join(o)
open(OUT_SVG, 'w', encoding='utf-8', newline='\n').write(svg)

if not PNG:
    print('ok', METRIC, len(series)); sys.exit(0)
chrome = shutil.which('chrome') or shutil.which('google-chrome') or r'C:\Program Files\Google\Chrome\Application\chrome.exe'
width = 2800
h = round(H * width / W)
d = tempfile.mkdtemp(prefix='bl')
page = os.path.join(d, 'p.html')
open(page, 'w', encoding='utf-8').write(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#0f1720}}svg{{display:block;width:{width}px;height:{h}px}}</style></head><body>{svg}</body></html>')
shot = os.path.join(d, 's.png')
subprocess.run([chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-color-profile=srgb',
                '--user-data-dir=' + os.path.join(d, 'prof'), f'--window-size={width},{h}', '--screenshot=' + shot,
                'file:///' + page.replace(os.sep, '/')], check=True, timeout=120, capture_output=True)
shutil.copyfile(shot, OUT_PNG)
shutil.rmtree(d, ignore_errors=True)
print('ok', METRIC, len(series))
