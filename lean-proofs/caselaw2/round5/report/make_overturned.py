#!/usr/bin/env python3
"""Build ~/Documents/html-reports/overturned.html: the live record of round 5 (overrulings that are not
self-announced). Re-run at any time; it reads whatever results exist.

    python round5/report/make_overturned.py

Reads (never the sealed test pairs):
  round5/PROGRESS.md, LOG.md, DESIGN5.md, ROUND5.md, FREEZE.md      the lead's state, log, design, round report
  round5/results/<variant>/{fresh_dev,holdout,leak,old}.txt          scores of each variant (score_all.sh)
  round5/tests/results/behaviour_<label>.tsv / .svg                  behavioural test
  round5/gold_fresh/GOLD_FRESH.md, sealed/TEST_RUNS.log              the key's report and the log of sealed runs
  round5/tests/TESTS.md
  round5/report/processes.json                                       who is running what (edited by hand)
  round5/report/sections/*.html                                      hand-written sections, embedded verbatim:
      00_question.html, 10_key.html, 20_tests.html, then any others in name order (the lead adds
      30_model.html, 40_results.html, 50_cases.html, 60_limits.html, 70_blog.html as they become true)
"""
import datetime
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
R5 = os.path.dirname(HERE)
OUT = '~/Documents/html-reports/overturned.html'
esc = html.escape


def read(path, default=''):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()
    except OSError:
        return default


def mtime(path):
    try:
        return datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%d %b %H:%M')
    except OSError:
        return ''


# ---------------------------------------------------------------- a small Markdown renderer

def inline(s):
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*([^*\s][^*]*)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2">\1</a>', s)
    return s


def md(text, shift=2):
    out, para, lines, i = [], [], text.replace('\r\n', '\n').split('\n'), 0

    def flush():
        if para:
            out.append('<p>' + inline(' '.join(para)) + '</p>')
            para.clear()

    while i < len(lines):
        ln = lines[i]
        if ln.startswith('```'):
            flush()
            j = i + 1
            while j < len(lines) and not lines[j].startswith('```'):
                j += 1
            out.append('<pre><code>' + esc('\n'.join(lines[i + 1:j])) + '</code></pre>')
            i = j + 1
            continue
        m = re.match(r'(#{1,6})\s+(.*)', ln)
        if m:
            flush()
            lvl = min(6, len(m.group(1)) + shift)
            out.append('<h%d>%s</h%d>' % (lvl, inline(m.group(2)), lvl))
            i += 1
            continue
        if ln.lstrip().startswith('|') and i + 1 < len(lines) and re.match(r'\s*\|?[\s:|-]+\|[\s:|-]*$', lines[i + 1]):
            flush()
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            head, body = rows[0], rows[2:]
            t = ['<div class="tw"><table><thead><tr>' + ''.join('<th>%s</th>' % inline(c) for c in head) + '</tr></thead><tbody>']
            for r in body:
                t.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>')
            t.append('</tbody></table></div>')
            out.append(''.join(t))
            continue
        m = re.match(r'(\s*)([-*]|\d+\.)\s+(.*)', ln)
        if m:
            flush()
            tag = 'ol' if m.group(2)[0].isdigit() else 'ul'
            items = []
            while i < len(lines):
                m2 = re.match(r'(\s*)([-*]|\d+\.)\s+(.*)', lines[i])
                if m2:
                    items.append(m2.group(3))
                elif lines[i].startswith('  ') and lines[i].strip() and items:
                    items[-1] += ' ' + lines[i].strip()
                else:
                    break
                i += 1
            out.append('<%s>%s</%s>' % (tag, ''.join('<li>%s</li>' % inline(x) for x in items), tag))
            continue
        if not ln.strip():
            flush()
        else:
            para.append(ln.strip())
        i += 1
    flush()
    return '\n'.join(out)


def details(title, body, note='', open_=False):
    return '<details%s><summary>%s%s</summary><div class="dbody">%s</div></details>' % (
        ' open' if open_ else '', esc(title), (' <span class="muted">' + esc(note) + '</span>') if note else '', body)


# ---------------------------------------------------------------- scores of each variant

def fresh_row(text, dim, key):
    for ln in text.splitlines():
        p = ln.split()
        if len(p) >= 13 and p[0] == dim and p[1] == key:
            n, a, b, c, d, e = int(p[2]), int(p[3]), int(p[6]), int(p[7]), int(p[8]), int(p[9])
            return dict(n=n, a=a, ad=int(p[4]) + int(p[5]), b=b, c=c, d=d, e=e, strict=float(p[10]), sci=p[11], lenient=float(p[12]),
                        lci=p[13] if len(p) > 13 else '')
    return None


def pool_row(text, key):
    seen = False
    for ln in text.splitlines():
        if ln.startswith('FROZEN TESTABLE POOL'):
            seen = True
        if seen:
            m = re.match(r'\s+%s\s+strict (\d+)/(\d+).*?negOrPartly (\d+)/(\d+) = ([\d.]+)%% \(([\d.]+)-([\d.]+)\)' % re.escape(key), ln)
            if m:
                return dict(strict=int(m.group(1)), n=int(m.group(2)), neg=int(m.group(3)), pct=float(m.group(5)), lo=m.group(6), hi=m.group(7))
    return None


def reverse_row(text):
    m = re.search(r'(\d+)\s*/\s*(\d+)\s*=\s*([\d.]+)%[^\n]*', text[text.find('REVERSE'):] if 'REVERSE' in text else '')
    return (m.group(1), m.group(2), m.group(3)) if m else None


def behaviour_rows(label):
    path = os.path.join(R5, 'tests', 'results', 'behaviour_%s.tsv' % label)
    rows = []
    t = read(path)
    if not t:
        return rows
    lines = t.splitlines()
    hd = lines[0].split('\t')
    for ln in lines[1:]:
        r = dict(zip(hd, ln.split('\t')))
        if r.get('series') == 'bound' and r.get('k') == '10':
            rows.append(r)
    return rows


def pct(x):
    return '%.1f%%' % (100 * x)


def variants():
    base = os.path.join(R5, 'results')
    names = [n for n in sorted(os.listdir(base), key=lambda n: os.path.getmtime(os.path.join(base, n)))] if os.path.isdir(base) else []
    out = []
    for n in names:
        d = os.path.join(base, n)
        fd = read(os.path.join(d, 'fresh_dev.txt'))
        if not fd:
            continue
        v = dict(name=n, when=mtime(os.path.join(d, 'fresh_dev.txt')), about=read(os.path.join(d, 'ABOUT.txt')).strip())
        v['all'] = fresh_row(fd, 'all', 'all')
        v['implied'] = fresh_row(fd, 'express', 'implied')
        v['partial'] = fresh_row(fd, 'scope', 'partial')
        v['notcrs'] = fresh_row(fd, 'burned_crs', 'notInCRS')
        m = re.search(r'precision side.*?\{"listed": (\d+), "unlisted": (\d+)\} of (\d+)', fd)
        v['prec'] = m.groups() if m else None
        ho = read(os.path.join(d, 'holdout.txt'))
        v['pool'] = pool_row(ho, 'all')
        v['feed'] = pool_row(ho, 'alsoInFeed')
        v['hold'] = pool_row(ho, 'holdoutOnly')
        lk = read(os.path.join(d, 'leak.txt')).strip().splitlines()
        v['leak'] = lk[-1] if lk else ''
        old = read(os.path.join(d, 'old.txt')).strip().splitlines()
        v['old'] = [x for x in old[-3:] if x.startswith(('SCDB', 'CRS'))]
        v['beh'] = behaviour_rows(n)
        out.append(v)
    return out


BASE_DEV = dict(n=165, a=50, ad=0, b=2, c=34, d=12, e=67, strict=0.303, sci='[0.238,0.377]', lenient=0.521, lci='[0.445,0.596]')


def scores_html(vs):
    if not vs:
        return '<p class="muted">No variant has been scored yet.</p>'
    h = ['<div class="tw"><table><thead><tr><th>Build</th><th>Scored</th><th>Pairs</th><th>Overruled by the listed case, from its own date</th>'
         '<th>Overruled by the listed case, from the date a later court said so</th><th>By another case</th><th>Partly negative</th><th>At risk only</th><th>Nothing</th><th>Strict</th><th>Lenient</th>'
         '<th>Implied pairs, lenient</th><th>Outside the Constitution Annotated, strict</th></tr></thead><tbody>']

    def row(name, when, a, imp, ncrs, about=''):
        if not a:
            return ''
        return ('<tr><td><b>%s</b>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td>'
                '<td>%s <span class="muted">%s</span></td><td>%s <span class="muted">%s</span></td><td>%s</td><td>%s</td></tr>') % (
            esc(name), ('<br><span class="muted">%s</span>' % esc(about)) if about else '', esc(when), a['n'], a['a'], a.get('ad', 0),
            a['b'], a['c'], a['d'], a['e'], pct(a['strict']), esc(a['sci']),
            pct(a['lenient']), esc(a['lci']),
            ('%s of %d' % (pct(imp['lenient']), imp['n'])) if imp else '–',
            ('%d of %d' % (ncrs['a'], ncrs['n'])) if ncrs else '–')

    h.append(row('Round 4 (baseline)', '', BASE_DEV, None, None))
    for v in vs:
        h.append(row(v['name'], v['when'], v['all'], v['implied'], v['notcrs'], v.get('about', '')))
    h.append('</tbody></table></div>')
    h.append('<p class="muted">Open half of the fresh key (165 pairs). Strict: the model marks the case overruled by the listed '
             'decision from that decision’s own date. A recognised overruling (a later court with power says the case was overruled '
             'by the listed decision) is negative only from the later court’s date, so it is counted in the next column and in '
             'lenient, never in strict. Lenient: also overruled by another decision, or partly negative. Brackets are 95% intervals.</p>')

    h.append('<h3>Held-out later-court notes</h3><div class="tw"><table><thead><tr><th>Build</th><th>Testable pool: negative or partly</th>'
             '<th>Also stated by a court with power</th><th>Stated by held-out courts only</th><th>Leak check</th>'
             '<th>Old lists (not blind)</th></tr></thead><tbody>')
    h.append('<tr><td><b>Round 4 (baseline)</b></td><td>293 of 9,374 = 3.1% <span class="muted">(2.8–3.5)</span></td>'
             '<td>36 of 2,640 = 1.4%</td><td>257 of 6,734 = 3.8%</td><td>0 leaks</td><td>SCDB 141 / 278; CRS 162 / 292</td></tr>')
    for v in vs:
        def cell(p):
            return ('%s of %s = %.1f%% <span class="muted">(%s–%s)</span>' % (format(p['neg'], ','), format(p['n'], ','), p['pct'], p['lo'], p['hi'])) if p else '–'
        h.append('<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            esc(v['name']), cell(v['pool']), cell(v['feed']), cell(v['hold']), esc(v['leak']), '<br>'.join(esc(x) for x in v['old']) or '–'))
    h.append('</tbody></table></div>')

    h.append('<h3>Behaviour: do courts stop citing the case?</h3>')
    last = next((v for v in reversed(vs) if v['beh']), None)
    rows = last['beh'] if last else behaviour_rows('baseline-round4')
    label = last['name'] if last else 'Round 4 (baseline)'
    if rows:
        h.append('<div class="tw"><table><thead><tr><th>Class (%s)</th><th>Cases used</th><th>Citations a year, before → after</th>'
                 '<th>Ratio</th><th>Controls’ ratio</th><th>Drop against controls</th></tr></thead><tbody>' % esc(label))
        for r in rows:
            h.append('<tr><td>%s</td><td>%s</td><td>%.2f → %.2f</td><td>%.2f</td><td>%.2f</td><td>%.2f <span class="muted">(%.2f–%.2f)</span></td></tr>' % (
                esc(r['class']), format(int(r['n']), ','), float(r['pre_rate']), float(r['post_rate']), float(r['ratio']),
                float(r['ctrl_ratio']), float(r['did']), float(r['did_lo']), float(r['did_hi'])))
        h.append('</tbody></table></div><p class="muted">Ten years either side of the event, citations from courts the case '
                 'bound, against matched controls. 1.00 means no difference from controls; the placebo should sit at 1.</p>')
    svgs = sorted([f for f in os.listdir(os.path.join(R5, 'tests', 'results')) if f.startswith('behaviour_') and f.endswith('.svg')],
                  key=lambda f: os.path.getmtime(os.path.join(R5, 'tests', 'results', f))) if os.path.isdir(os.path.join(R5, 'tests', 'results')) else []
    if svgs:
        svg = read(os.path.join(R5, 'tests', 'results', svgs[-1]))
        svg = re.sub(r'<\?xml[^>]*\?>', '', svg)
        h.append('<figure class="fig">%s<figcaption>%s</figcaption></figure>' % (svg, esc(svgs[-1])))
    return '\n'.join(h)


def sealed_html():
    log = [x for x in read(os.path.join(R5, 'gold_fresh', 'sealed', 'TEST_RUNS.log')).splitlines() if x.strip()]
    frozen = os.path.exists(os.path.join(R5, 'FREEZE.md'))
    h = ['<div class="tw"><table><thead><tr><th>Sealed half (127 pairs)</th><th>Strict</th><th>Lenient</th></tr></thead><tbody>',
         '<tr><td>Round 4 (baseline), scored once when the key was built</td><td>25.2% <span class="muted">[18.4, 33.4]</span> (32)</td>'
         '<td>46.5% <span class="muted">[38.0, 55.1]</span> (59)</td></tr>']
    if len(log) > 1:
        ft = read(os.path.join(R5, 'results', 'final', 'fresh_test.txt'))
        fr = fresh_row(ft, 'all', 'all') if ft else None
        if fr:
            h.append('<tr><td>Frozen build (recognised class), the single run after the freeze record</td>'
                     '<td>%s <span class="muted">%s</span> (%d)</td><td><b>%s</b> <span class="muted">%s</span> (%d of %d; %d of them '
                     'overruled by the listed case from a later court’s date)</td></tr>' % (
                         pct(fr['strict']), esc(fr['sci']), fr['a'], pct(fr['lenient']), esc(fr['lci']),
                         fr['a'] + fr['ad'] + fr['b'] + fr['c'], fr['n'], fr['ad']))
        else:
            h.append('<tr><td colspan="3">%d runs are logged on the sealed half.</td></tr>' % len(log))
    else:
        h.append('<tr><td>Expanded build</td><td colspan="2" class="muted">Not run yet. It is run once, after the rules, code and data '
                 'are frozen%s.</td></tr>' % (' (frozen: FREEZE.md exists)' if frozen else ''))
    h.append('</tbody></table></div>')
    h.append('<p class="muted">Runs logged on the sealed half: %d.</p>' % len(log))
    return ''.join(h)


def processes_html():
    try:
        ps = json.load(open(os.path.join(HERE, 'processes.json'), encoding='utf-8'))
    except (OSError, ValueError):
        return ''
    h = ['<div class="tw"><table><thead><tr><th>Work</th><th>State</th><th>Where it stands</th></tr></thead><tbody>']
    for p in ps:
        h.append('<tr><td><b>%s</b></td><td><span class="st st-%s">%s</span></td><td>%s</td></tr>' % (
            esc(p['work']), esc(p['state'].split()[0].lower()), esc(p['state']), inline(p['note'])))
    h.append('</tbody></table></div>')
    return ''.join(h)


CSS = r"""
:root{--bg:#fcfcfb;--surface:#ffffff;--surface-2:#f4f3f0;--border:#e2e0da;--text:#141413;--text-2:#52514e;--muted:#73726c;
--accent:#2a78d6;--code:#f1efea;--ok:#1d7a46;--ok-bg:#e8f5ee;--run:#8a5a00;--run-bg:#fdf3dc;--wait:#52514e;--wait-bg:#eeede9;color-scheme:light}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1a1a19;--surface:#222220;--surface-2:#2a2a28;--border:#3a3a37;
--text:#f0efec;--text-2:#c3c2b7;--muted:#9c9b93;--accent:#3987e5;--code:#2d2d2a;--ok:#6fd19b;--ok-bg:#1f3027;--run:#f0c060;--run-bg:#3a3220;
--wait:#c3c2b7;--wait-bg:#2a2a28;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#1a1a19;--surface:#222220;--surface-2:#2a2a28;--border:#3a3a37;--text:#f0efec;--text-2:#c3c2b7;--muted:#9c9b93;
--accent:#3987e5;--code:#2d2d2a;--ok:#6fd19b;--ok-bg:#1f3027;--run:#f0c060;--run-bg:#3a3220;--wait:#c3c2b7;--wait-bg:#2a2a28;color-scheme:dark}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
main{max-width:1040px;margin:0 auto;padding:24px 16px 80px;overflow-wrap:break-word}
h1{font-size:2.1rem;line-height:1.15;margin:.2em 0 .3em;letter-spacing:-.01em}
h2{font-size:1.45rem;margin:2.2em 0 .6em;padding-top:.6em;border-top:1px solid var(--border)}
h3{font-size:1.12rem;margin:1.6em 0 .5em}h4,h5,h6{font-size:1rem;margin:1.2em 0 .4em}
p{margin:.6em 0}a{color:var(--accent);overflow-wrap:anywhere}
code{font:.86em/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--code);padding:.08em .3em;border-radius:4px;overflow-wrap:anywhere}
pre{background:var(--code);padding:12px 14px;border-radius:8px;overflow-x:auto;font-size:.84em;line-height:1.45}pre code{background:none;padding:0;white-space:pre;overflow-wrap:normal}
.kicker{color:var(--muted);font-size:.86rem;margin:0;text-transform:uppercase;letter-spacing:.06em}
.lead{font-size:1.08rem}.muted{color:var(--muted);font-size:.9em}
blockquote{margin:1em 0;padding:.2em 1em;border-left:3px solid var(--border);color:var(--text-2)}
.tw{overflow-x:auto;margin:.8em 0;border:1px solid var(--border);border-radius:8px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{padding:7px 10px;text-align:left;vertical-align:top;border-bottom:1px solid var(--border)}
th{background:var(--surface-2);font-weight:600;font-size:.82rem}tr:last-child td{border-bottom:0}
td{font-variant-numeric:tabular-nums}
details{border:1px solid var(--border);border-radius:8px;margin:.7em 0;background:var(--surface)}
summary{cursor:pointer;padding:9px 12px;font-weight:600}.dbody{padding:0 14px 12px;font-size:.94rem}
.st{display:inline-block;padding:1px 8px;border-radius:6px;font-size:.82rem;font-weight:600;white-space:nowrap}
.st-done{color:var(--ok);background:var(--ok-bg)}.st-running{color:var(--run);background:var(--run-bg)}
.st-waiting,.st-not{color:var(--wait);background:var(--wait-bg)}
.stamp{margin:.4em 0 1.2em;padding:10px 12px;border:1px solid var(--border);border-radius:8px;background:var(--surface-2);font-size:.92rem}
.film{margin:1em 0}.film video{width:100%;border-radius:8px;background:#000;display:block}
.fig{margin:1em 0}.fig svg{max-width:100%;height:auto;background:#fff;border-radius:8px}.fig figcaption{color:var(--muted);font-size:.85rem}
nav.toc{font-size:.92rem;margin:1em 0}nav.toc a{margin-right:14px;white-space:nowrap}
"""


def main():
    now = datetime.datetime.now().strftime('%d %B %Y, %H:%M')
    sec_dir = os.path.join(HERE, 'sections')
    secs = sorted(f for f in os.listdir(sec_dir) if f.endswith('.html')) if os.path.isdir(sec_dir) else []
    vs = variants()
    final = os.path.exists(os.path.join(R5, 'ROUND5.md'))
    parts = []
    parts.append('<p class="kicker">Formalising US case law in Lean · round 5</p><h1>Overturned</h1>')
    parts.append('<p class="lead">Can the model handle an overruling that the overruling court never announces, such as '
                 '<i>Brown v. Board of Education</i> and <i>Plessy v. Ferguson</i>, and how would we know it was right?</p>')
    parts.append('<div class="stamp"><b>%s.</b> Page rebuilt %s. It is rebuilt as each piece of work lands; numbers '
                 'below marked baseline are the model before this round.</div>' % (
                     'The round is finished' if final else 'Work in progress', now))
    parts.append('<div class="film"><video controls preload="metadata" '
                 'src="file:///~/Documents/global-law-lean/lean-proofs/video/out/lean-in-testing.mp4"></video>'
                 '<p class="muted"><b>Film: how the Lean model decides</b> (69 seconds). One Supreme Court sentence followed '
                 'through every check, then tested against a list the model never read. File: '
                 '<a href="file:///~/Documents/global-law-lean/lean-proofs/video/out/lean-in-testing.mp4">'
                 '~/Documents/global-law-lean/lean-proofs/video/out/lean-in-testing.mp4</a>. '
                 'The film at the top of the blog post is at '
                 '<a href="https://watch.cloudflarestream.com/c54cd672e5945160b07fef7e01b7ee27">'
                 'watch.cloudflarestream.com/c54cd672e5945160b07fef7e01b7ee27</a>.</p></div>')
    parts.append('<nav class="toc"><a href="#progress">Progress</a><a href="#question">The question</a><a href="#key">The fresh key</a>'
                 '<a href="#tests">The other tests</a><a href="#scores">Scores so far</a><a href="#sealed">Sealed half</a>'
                 '<a href="#model">What changed</a><a href="#results">Results</a><a href="#cases">Worked cases</a>'
                 '<a href="#limits">Limits</a><a href="#blog">Blog wording</a><a href="#next">What next</a>'
                 '<a href="#log">Log and design</a></nav>')

    parts.append('<h2 id="progress">Progress</h2>' + processes_html())
    prog = read(os.path.join(R5, 'PROGRESS.md'))
    if prog:
        parts.append(details('The Lean lead’s own progress file', md(prog, 3), 'PROGRESS.md, ' + mtime(os.path.join(R5, 'PROGRESS.md')), True))

    for f in secs:
        if f < '30':
            parts.append(read(os.path.join(sec_dir, f)))

    parts.append('<h2 id="scores">Scores so far</h2>' + scores_html(vs))
    parts.append('<h2 id="sealed">The sealed half</h2>' + sealed_html())

    for f in secs:
        if f >= '30':
            parts.append(read(os.path.join(sec_dir, f)))

    parts.append('<h2 id="log">Log, design and source reports</h2>')
    for title, rel in [('Round report', 'ROUND5.md'), ('Iteration log', 'LOG.md'), ('Freeze record', 'FREEZE.md'),
                       ('Design of the change', 'DESIGN5.md'), ('The fresh key: full report', 'gold_fresh/GOLD_FRESH.md'),
                       ('The two other tests: full report', 'tests/TESTS.md'),
                       ('Search: how to raise the scores, and the miss budget', '../round6/research/improvement_plan.md'),
                       ('Search: more Supreme Court answer keys', '../round6/research/scotus_sources.md'),
                       ('Search: answer keys for lower and state courts', '../round6/research/lower_court_sources.md')]:
        t = read(os.path.join(R5, rel))
        if t:
            parts.append(details(title, md(t, 3), rel + ', ' + mtime(os.path.join(R5, rel))))

    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Overturned</title><style>%s</style></head><body><main>%s</main></body></html>' % (CSS, '\n'.join(parts)))
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(page)
    print('wrote', OUT, len(page), 'bytes;', len(vs), 'variants')


if __name__ == '__main__':
    main()
