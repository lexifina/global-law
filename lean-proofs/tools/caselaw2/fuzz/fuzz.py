#!/usr/bin/env python3
"""fuzz.py - fuzz the caselaw-lean-2 glue: TSV reading (Tsv.lean, Data.lean), the certificate normalisation and
offsets (Certificate.lean), against an independent oracle written from SCHEMA.md and against the Python reference
(ref/precedent_ref.py). Results: caselaw-lean-2/FUZZ.md.

  python -X utf8 fuzz.py gen   --n 5000 [--seed 1] [--dir D]   # write case dirs (fixtures/data + adversarial rows)
  python -X utf8 fuzz.py run   [--dir D] [--jobs 8]            # Lean dumper (2 passes), compiled runner, reference
  python -X utf8 fuzz.py check [--dir D]                        # the properties; prints a summary, writes report.json
  python -X utf8 fuzz.py real                                   # quote-at-offset pass over the REAL data/
  python -X utf8 fuzz.py all   --n 5000                         # gen + run + check

Each case is a copy of fixtures/data with (a) 1-4 synthetic decisions whose texts mix CRLF, lone CR, tabs, NBSP,
curly quotes, combining marks, astral characters, BOMs and zero-width characters, with a holding, a treatment and
(sometimes) a history row certified at offsets chosen at the window and file edges, under offset variants (exact,
UTF-8 bytes, UTF-16 units, offsets taken before CRLF normalisation, +-1, empty, swapped, a clipped window declared
unclipped, a conflicting second window), and (b) 0-8 byte-level row mutations on any SCHEMA file (CRLF, trailing tabs,
missing/extra/empty columns, 0/99991231/huge/negative/'+5'/'1_000'/other-script numbers, tabs and newlines inside
fields, NUL, 200k-character fields, BOM, invalid UTF-8, '#' and header lines, blank lines).

Properties (see FUZZ.md): P1 no crash (dumper, runner, reference); P2 every row the oracle rejects is rejected and
counted, every row it accepts is parsed to the oracle's values (Lean dump and reference); P3 a dump re-loaded gives
the same dump (round trip); P4 the Lean quote check equals the oracle's code-point check, and the window slice Lean
compares equals Python's slice of the normalised window; P5 the runner and the reference agree on which certificate
rows pass the quote stage.
"""
import argparse
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import traceback
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, '..', '..', '..'))                 # lean-proofs
W = os.path.expanduser('~/Documents/us-caselaw-lean-work/caselaw-lean-2')
FIX = os.path.join(W, 'fixtures')
EXE = os.path.join(W, 'runner', '.lake', 'build', 'bin', 'caselaw2.exe' if os.name == 'nt' else 'caselaw2')
DEFAULT_DIR = os.path.join(os.environ.get('TEMP', '/tmp'), 'caselaw2-fuzz')
NODES = 1000
ELAN = os.path.expanduser('~/.elan/bin')

# ------------------------------------------------------------------------------------------------- the oracle (SCHEMA)
# file: (columns, nat columns, int columns, ppm columns, bool columns)
SPEC = {
    'courts2.tsv': (11, (0, 1, 2, 4, 7, 8), (), (), ()),
    'succession.tsv': (6, (0, 1, 2), (), (), ()),
    'adoption.tsv': (7, (0, 1, 2), (), (), ()),
    'system_rules.tsv': (7, (3, 4), (0,), (), ()),
    'history.tsv': (13, (1, 3, 7, 8), (2,), (), ()),
    'treatments.tsv': (16, (1, 2, 3, 9, 10), (), (15,), (7,)),
    'cert_text.tsv': (4, (1, 2), (), (), ()),
    'holdings_cert_text.tsv': (4, (1, 2), (), (), ()),
    'issues.tsv': (6, (), (), (), ()),
    'holdings.tsv': (14, (1, 7, 8), (), (13,), ()),
    'marks.tsv': (6, (0,), (), (), ()),
    'lawchanges.tsv': (7, (3, 4, 5), (), (), ()),
    'supersessions.tsv': (8, (1,), (), (5,), (6,)),
    'decisions2.tsv': (9, (0, 1, 2, 3), (), (), ()),
}
FILES = list(SPEC)
BENCH = ["panel", "division", "enBanc", "limitedEnBanc", "circulated", "conflictPanel", "wholeCourt", "unknown"]
PUB = ["published", "unpublished", "table", "summaryOrder", "memorandum", "unknown"]
FORM = ["full", "perCuriam", "summaryAffirmance", "equallyDivided", "certifiedAnswer", "plurality", "memorandum",
        "unknown"]


def is_nat(s):
    return s != '' and all('0' <= c <= '9' for c in s)


def is_int(s):
    return is_nat(s[1:]) if s.startswith('-') else is_nat(s)


def ppm(s):
    """SCHEMA decimal in [0, inf) as parts per million; None if not one."""
    parts = s.split('.')
    if len(parts) == 1:
        return int(s) * 1000000 if is_nat(s) else None
    if len(parts) != 2:
        return None
    a, b = parts
    if a == '' and b == '':
        return None
    if (a and not is_nat(a)) or (b and not is_nat(b)):
        return None
    return int(a or '0') * 1000000 + int((b + '000000')[:6])


def ppm_s(n):
    return '%d.%06d' % (n // 1000000, n % 1000000)


def oracle_lines(data):
    """SCHEMA reading of one file's bytes: [(line_no, text or None if not UTF-8)] for the non-blank lines.
    Lines end at LF only; trailing CRs are not data; a BOM on line 1 is not data."""
    out = []
    for i, raw in enumerate(data.split(b'\n')):
        raw = raw.rstrip(b'\r')
        if i == 0 and raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]
        if not raw:
            continue
        try:
            out.append((i + 1, raw.decode('utf-8')))
        except UnicodeDecodeError:
            out.append((i + 1, None))
    return out


def oracle_file(name, data):
    """(accepted canonical rows, bad count, duplicates, FB-L5 rows) for one SCHEMA file, as SCHEMA defines its rows.
    A decimal column (confidence, score) must be a SCHEMA decimal and a flag column (explicit) must be 0 or 1; any
    other value rejects the row (FB-L5: they used to read as 0 silently). The last number counts the rows rejected
    for that reason alone, which a loader with the old default would keep."""
    n, nats, ints, ppms, bools = SPEC[name]
    rows, bad, l5 = [], 0, 0
    for _, l in oracle_lines(data):
        f = l.split('\t') if l is not None else None
        if f is None or len(f) != n or any(not is_nat(f[c]) for c in nats) or any(not is_int(f[c]) for c in ints):
            bad += 1
            continue
        if any(ppm(f[c]) is None for c in ppms) or any(f[c] not in ('0', '1') for c in bools):
            bad += 1
            l5 += 1
            continue
        g = list(f)
        for c in nats + ints:
            g[c] = str(int(f[c]))
        for c in ppms:
            g[c] = ppm_s(ppm(f[c]))
        rows.append(g)
    if name != 'decisions2.tsv':
        return rows, bad, 0, l5
    # decisions: node < NODES, a later row for the same node wins; enumerations as the schema lists them
    keep, dups = {}, 0
    for g in rows:
        node = int(g[0])
        if node >= NODES:
            bad += 1
            continue
        if node in keep:
            dups += 1
        keep[node] = [g[0], g[1], g[2], g[3], g[4] if g[4] in BENCH else '<255>', g[5] if g[5] in PUB else '<255>',
                      g[6] if g[6] in FORM else '<255>', g[7], '-']
    return [keep[k] for k in sorted(keep)], bad, dups, 0


def norm(s):
    return s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')


def oracle_quotes(tables):
    """{(table, id): (spec_ok, slice, trigger)} for every certificate row.
    spec_ok: the quote is not empty, start < end (FB-L2), and SOME well-formed covering window of the hash has the
    quote at the offset (code points, normalised), whatever the order of the windows (FB-L3). This is what
    Cert.quoteOk checks.
    slice: the text at the offset in the first such window in Lean's list order (cert_text rows then
    holdings_cert_text rows, newest first), which is Cert.coveringWindow; '-' when there is none.
    trigger: 'FB-L2' when the checker before the fix passed the row on an empty quote at an empty span, 'FB-L3' when
    its verdict (the first covering window only) differs from spec_ok, else ''. A Lean verdict that equals the old
    one on such a row is that bug again."""
    wins = defaultdict(list)
    for r in tables['cert_text.tsv'] + tables['holdings_cert_text.tsv']:
        wins[r[0]].insert(0, (int(r[1]), int(r[2]), r[3]))
    out = {}
    for t, cs in (('treatments', 8), ('history', 6), ('holdings', 6)):
        for r in tables[t + '.tsv']:
            sha, a, b, q = r[cs], int(r[cs + 1]), int(r[cs + 2]), r[cs + 3]
            cov = [w for w in wins.get(sha, []) if w[0] <= a and b <= w[1] and len(w[2]) == w[1] - w[0]]

            def cut(w):
                return norm(w[2])[a - w[0]:a - w[0] + max(0, b - a)]
            hit = next((w for w in cov if a < b and q != '' and cut(w) == norm(q)), None)
            old = bool(cov) and a <= b and cut(cov[0]) == norm(q)       # the checker before FB-L2 and FB-L3
            trig = '' if old == (hit is not None) else 'FB-L2' if a == b else 'FB-L3'
            out[(t, r[0])] = (hit is not None, cut(hit) if hit else '-', trig)
    return out


# ------------------------------------------------------------------------------------------------- generation
PIECES = ['the court', ' ', ' ', 'held', ' ', '\n', '\r\n', '\r', '\t', ' ', '“', '”', '‘',
          '’', 'é', 'é', 'ñ', '\U0001F600', '\U0001D518', '﻿', '中文', '​',
          ' ', '\x0b', '\x0c', '\x1c', '\x85', 'K', 'İ', 'ab', 'x', '.', '"', "'", '­',
          '\U00010348', '٣', '１']
CORE = ['Betts v. Brady, 316 U.S. 455, should be overruled',
        'Betts v. Brady, 316 U.S. 455, should be “overruled”',
        'Bett́s v. Brady \U0001F600, 316 U.S. 455, is overruled',
        'Betts v. Brady,\r\n316 U.S. 455, should be overruled',
        'Betts v.\tBrady, 316 U.S. 455,\nshould be overruled\r',
        '\U0001D518 316 U.S. 455 overruled K',
        'overruled 316 U.S. 455']
VARIANTS = ['exact'] * 6 + ['bytes', 'utf16', 'raw', 'plus1', 'minus1', 'empty', 'swap', 'clipdecl', 'conflict',
                            'schema_cr']


def noise(rng, n):
    return ''.join(rng.choice(PIECES) for _ in range(n))


def u8(s):
    return len(s.encode('utf-8'))


def u16(s):
    return len(s.encode('utf-16-le')) // 2


def raw_index(raw, a):
    """The index in `raw` of character `a` of raw.replace('\\r\\n', '\\n')."""
    i = n = 0
    while n < a and i < len(raw):
        i += 2 if raw.startswith('\r\n', i) else 1
        n += 1
    return i


def clean_reader(x):
    """certify.py clean() as it was before FB-R1: tab and LF to space, a lone CR left as it is. The reader now maps
    CR too (the 'schema_cr' variant); the old form is kept here as an input, so that windows and quotes holding a
    lone CR are still generated (and so that a seed gives the same cases as before)."""
    return x.replace('\t', ' ').replace('\n', ' ')


def cert_scenario(rng, k, node):
    """A decision text, its decisions2 row, cert_text rows and a holding / treatment / history row on it."""
    pre = noise(rng, rng.choice([0, 0, 1, 3, 40, 150, 400, 600]))
    suf = noise(rng, rng.choice([0, 0, 1, 3, 40, 150, 400, 600]))
    core = rng.choice(CORE)
    raw = pre + core + suf
    T = raw.replace('\r\n', '\n')                        # SCHEMA: offsets after CRLF -> LF
    sha = hashlib.sha1(raw.encode('utf-8')).hexdigest()
    c0 = len(pre.replace('\r\n', '\n'))
    if pre.endswith('\r') and core.startswith('\n'):
        c0 -= 1
    c1 = len((pre + core).replace('\r\n', '\n'))
    if c0 < 0:
        c0 = 0
    a = rng.choice([c0, c0, max(0, c0 - rng.randint(0, 5)), 0])
    b = rng.choice([c1, c1, min(len(T), c1 + rng.randint(0, 5)), len(T)])
    var = rng.choice(VARIANTS)
    cleanf = clean_reader if var != 'schema_cr' else norm
    s0, e0 = max(0, a - 400), min(len(T), b + 400)
    wins = [[sha, s0, e0, cleanf(T[s0:e0])]]
    quote = cleanf(T[a:b])
    sa, sb = a, b
    if var == 'bytes':
        sa, sb = u8(T[:a]), u8(T[:b])
    elif var == 'utf16':
        sa, sb = u16(T[:a]), u16(T[:b])
    elif var == 'raw':                                   # offsets counted on the text before CRLF normalisation
        sa, sb = raw_index(raw, a), raw_index(raw, b)
    elif var == 'plus1':
        sa, sb = a + 1, b + 1
    elif var == 'minus1':
        sa, sb = max(0, a - 1), max(0, b - 1)
    elif var == 'empty':
        sb = sa
        quote = ''
    elif var == 'swap':
        sa, sb = b, a
    elif var == 'clipdecl':                              # declared unclipped, text clipped at the file end
        wins[0][2] = b + 400
    elif var == 'conflict':                              # a second covering window for the hash, other text
        alt = list(cleanf(T[s0:e0]))
        for i in range(a - s0, min(len(alt), b - s0)):
            if alt[i] == 'o':
                alt[i] = '0'
        wins.append([sha, s0, e0, ''.join(alt)])
    date = 19500101 + rng.randint(0, 70) * 10000
    dec = [node, 2906, date, 0, 'wholeCourt', 'published', 'full', sha, 'fuzz']
    cert = [sha, sa, sb, quote]
    hold = ['fzh%d' % k, node, 'ga.venue', 'P %d' % k, 'yes', 'majority'] + cert + ['name:x', 'majority', 'fuzz',
                                                                                    '0.9']
    treat = ['fzt%d' % k, node, 0, date, 'overruled', 'all', 'retroactive', 1] + cert + \
            ['cite:316 U.S. 455', 'majority', 'fuzz', '0.99']
    hist = ['fzy%d' % k, node, -1, date, 'withdrawn', 'all'] + cert + ['cite:316 U.S. 455', 'majority', 'fuzz']
    return dict(dec=dec, wins=wins, hold=hold, treat=treat, hist=hist if rng.random() < 0.3 else None, var=var,
                to_holdings_ct=rng.random() < 0.5)


NUMS = ['0', '99991231', '9' * 40, '-5', '+5', ' 5', '5 ', '1_000', '٣', ' 5', '0x1', '5.0', '05', '-0',
        '', '１２', '1e3', '-', '²', '18446744073709551616', '4294967296']
INSERTS = [' ', '\U0001F600', 'é', '“', '﻿', '\x00', '\r', ' ', '\x85']
LINE_OPS = ['crlf', 'cr2', 'trail_tab', 'drop_col', 'add_col', 'empty_field', 'num', 'num', 'num', 'lone_cr',
            'tab_in_field', 'nl_in_field', 'long', 'hash', 'nul', 'unicode_field', 'blank', 'header']
FILE_OPS = ['bom', 'invalid', 'no_final_nl', 'crlf_all']
BAD_BYTES = [b'\xff', b'\xc3\x28', b'\xed\xa0\x80', b'\xc0\xaf', b'\xf4\x90\x80\x80', b'\xe2\x82', b'\x80']


def mutate_lines(rng, lines, name):
    """Apply one line operation to a random line (lines are lists of string fields)."""
    if not lines:
        return 'none'
    op = rng.choice(LINE_OPS)
    i = rng.randrange(len(lines))
    f = lines[i]
    f[:] = [str(x) for x in f]
    j = rng.randrange(len(f))
    if op == 'crlf':
        f[-1] += '\r'
    elif op == 'cr2':
        f[-1] += '\r\r'
    elif op == 'trail_tab':
        f.append('')
    elif op == 'drop_col':
        f.pop()
    elif op == 'add_col':
        f.insert(j, 'x')
    elif op == 'empty_field':
        f[j] = ''
    elif op == 'num':
        nats = SPEC[name][1] + SPEC[name][2] + SPEC[name][3] + SPEC[name][4]
        c = rng.choice(nats) if nats else j
        f[c if c < len(f) else j] = rng.choice(NUMS)
    elif op == 'lone_cr':
        f[j] = f[j][:1] + '\r' + f[j][1:]
    elif op == 'tab_in_field':
        f[j] = f[j][:2] + '\t' + f[j][2:]
    elif op == 'nl_in_field':
        f[j] = f[j][:2] + '\n' + f[j][2:]
    elif op == 'long':
        f[j] += rng.choice(['x', '\U0001F600', 'é']) * 200000
    elif op == 'hash':
        f[0] = '#' + f[0]
    elif op == 'nul':
        f[j] += '\x00'
    elif op == 'unicode_field':
        f[j] = f[j][:3] + rng.choice(INSERTS) + f[j][3:]
    elif op == 'blank':
        lines.insert(i, [rng.choice(['', ' ', '\r', '  \t'])])
    elif op == 'header':
        lines.insert(0, ['court_id', 'node', 'id', 'x'][:1] + ['h'] * (SPEC[name][0] - 1))
    return op


def render(lines, rng, fops):
    data = ''.join('\t'.join(str(x) for x in f) + '\n' for f in lines).encode('utf-8')
    if 'crlf_all' in fops:
        data = data.replace(b'\n', b'\r\n')
    if 'invalid' in fops and data:
        k = rng.randrange(len(data))
        k = data.rfind(b'\t', 0, k) + 1 if b'\t' in data[:k] else 0
        data = data[:k] + rng.choice(BAD_BYTES) + data[k:]
    if 'no_final_nl' in fops:
        data = data.rstrip(b'\n')
    if 'bom' in fops:
        data = b'\xef\xbb\xbf' + data
    return data


def read_fixture(name):
    p = os.path.join(FIX, 'data', name)
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8', newline='\n') as f:
        return [l.rstrip('\n').split('\t') for l in f if l.strip('\n')]


def gen_case(seed, d):
    rng = random.Random(seed)
    tabs = {n: read_fixture(n) for n in FILES}
    vars_ = []
    for k in range(rng.randint(1, 4)):
        sc = cert_scenario(rng, k, 100 + k)
        sc = {x: ([str(v) for v in y] if x in ('dec', 'hold', 'treat', 'hist') and y else
                  [[str(v) for v in w] for w in y] if x == 'wins' else y) for x, y in sc.items()}
        vars_.append(sc['var'])
        tabs['decisions2.tsv'].append(sc['dec'])
        tabs['holdings_cert_text.tsv' if sc['to_holdings_ct'] else 'cert_text.tsv'].extend(sc['wins'])
        tabs['holdings.tsv'].append(sc['hold'])
        tabs['treatments.tsv'].append(sc['treat'])
        if sc['hist']:
            tabs['history.tsv'].append(sc['hist'])
    ops = []
    fops = defaultdict(set)
    for _ in range(rng.choice([0, 0, 1, 2, 3, 5, 8])):
        if rng.random() < 0.15:
            n = rng.choice(FILES)
            op = rng.choice(FILE_OPS)
            fops[n].add(op)
            ops.append((n, op))
        else:
            n = rng.choice(FILES)
            ops.append((n, mutate_lines(rng, tabs[n], n)))
    os.makedirs(d, exist_ok=True)
    for n in FILES:
        with open(os.path.join(d, n), 'wb') as f:
            f.write(render(tabs[n], rng, fops[n]))
    with open(os.path.join(d, 'case.json'), 'w', encoding='utf-8') as f:
        json.dump({'seed': seed, 'variants': vars_, 'ops': ops}, f)


# ------------------------------------------------------------------------------------------------- running
def run_ref(d):
    """The reference on one case: parse counts, certificate results, or the crash."""
    os.environ['CASELAW2_NODES'] = str(NODES)
    sys.path.insert(0, os.environ.get('FUZZ_REF_DIR') or os.path.join(LP, 'tools', 'caselaw2', 'ref'))
    import precedent_ref as R
    if not hasattr(R, 'BAD_ROWS'):            # an older reference with no bad-row count
        R.BAD_ROWS = Counter()
    R.BAD_ROWS.clear()
    try:
        D = R.Data(d)
        E = R.Engine(D, firm=False)
        E.admit()
        res = {'bad': dict(R.BAD_ROWS), 'counts': {
            'treatments.tsv': len(D.treatments), 'history.tsv': len(D.history), 'holdings.tsv': len(D.holdings),
            'courts2.tsv': sum(len(v) for v in D.courts.values()), 'succession.tsv': len(D.succession),
            'adoption.tsv': len(D.adoption), 'system_rules.tsv': len(D.sysrules), 'marks.tsv': len(D.marks),
            'lawchanges.tsv': len(D.lawchanges), 'supersessions.tsv': len(D.supersessions),
            'issues.tsv': len(D.issues), 'decisions2.tsv': D.n_present},
            'certs': {'%s|%s' % (f.replace('.tsv', ''), i): r for (f, i), r in E.cert_ok.items()}}
    except Exception:
        res = {'crash': traceback.format_exc()[-2000:]}
    with open(os.path.join(d, 'ref.json'), 'w', encoding='utf-8') as f:
        json.dump(res, f)


def run_runner_batch(args):
    """The runner's own main (CaseLaw2.Run.main, the arguments run_lean.sh gives one shard) over a chunk of cases in
    one interpreter process (RunBatch.lean): Windows Application Control blocks a freshly built caselaw2.exe, and
    run_lean.sh's fallback, one `lake env lean --run` per case, costs ~7 s of start-up each."""
    k, dirs, root = args
    lst = os.path.join(root, 'runlist-%d.txt' % k)
    with open(lst, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(dirs) + '\n')
    env = dict(os.environ, PATH=ELAN + os.pathsep + os.environ.get('PATH', ''), FUZZ_LIST=lst,
               FUZZ_EDGES=os.path.join(FIX, 'edges'))
    p = subprocess.run(['lake', 'env', 'lean', os.path.join(HERE, 'RunBatch.lean')], cwd=LP, capture_output=True,
                       env=env)
    err = p.stderr.decode('utf-8', 'replace') + p.stdout.decode('utf-8', 'replace')
    cur, per = None, defaultdict(list)
    for l in err.splitlines():
        if l.startswith('CASE '):
            cur = l[5:].strip()
        elif cur and ('PANIC' in l or 'error' in l.lower() or 'INTERNAL' in l):
            per[cur].append(l[:300])
    for d in dirs:
        rcp = os.path.join(d, 'runner', 'rc.txt')
        rc = open(rcp, encoding='utf-8').read().strip() if os.path.exists(rcp) else None
        with open(os.path.join(d, 'runner.json'), 'w', encoding='utf-8') as f:
            json.dump({'rc': 0 if rc == '0' else rc, 'stderr': '\n'.join(per.get(d, []))[-2000:],
                       'batch_rc': p.returncode}, f)
    return p.returncode


def run_dump(dirs):
    env = dict(os.environ, PATH=ELAN + os.pathsep + os.environ.get('PATH', ''))
    lst = os.path.join(os.path.dirname(dirs[0]), '_dumplist-' + os.path.basename(dirs[0]) + '.txt')
    with open(lst, 'w', encoding='utf-8', newline='\n') as f:
        f.write(''.join(d + '\n' for d in dirs))
    p = subprocess.run(['lake', 'env', 'lean', '--run', os.path.join(HERE, 'Dump.lean'), str(NODES), '@' + lst],
                       cwd=LP, capture_output=True, env=env)
    return p.returncode, p.stderr.decode('utf-8', 'replace')


def case_dirs(root):
    return sorted(os.path.join(root, x) for x in os.listdir(root) if x.startswith('c'))


def cmd_run(root, jobs):
    dirs = case_dirs(root)
    chunks = [dirs[i::jobs] for i in range(jobs)]
    with ProcessPoolExecutor(jobs) as ex:
        errs = list(ex.map(run_dump, [c for c in chunks if c]))
        errs += list(ex.map(run_dump, [[os.path.join(x, 'lean') for x in c] for c in chunks if c]))
        list(ex.map(run_ref, dirs, chunksize=16))
        if os.environ.get('FUZZ_RUNNER', '1') == '1':
            list(ex.map(run_runner_batch, [(k, c, root) for k, c in enumerate(chunks) if c]))
    with open(os.path.join(root, 'dump_stderr.txt'), 'w', encoding='utf-8') as f:
        for rc, e in errs:
            f.write('rc=%d\n%s\n' % (rc, e))


# ------------------------------------------------------------------------------------------------- checking
def read_tsv_rows(p):
    if not os.path.exists(p):
        return None
    with open(p, 'rb') as f:
        return [l.decode('utf-8').split('\t') for l in f.read().split(b'\n')[:-1]]


def check_case(d):
    """[(property, detail)] failures of one case, plus stats."""
    fails = []
    stats = Counter()
    raw = {n: open(os.path.join(d, n), 'rb').read() for n in FILES}
    orc = {n: oracle_file(n, raw[n]) for n in FILES}
    lean_dir = os.path.join(d, 'lean')
    # P1
    if not os.path.exists(os.path.join(lean_dir, 'quotes.tsv')):
        fails.append(('P1.dump', 'no dump'))
        return fails, stats
    rj = json.load(open(os.path.join(d, 'runner.json'), encoding='utf-8')) if os.path.exists(
        os.path.join(d, 'runner.json')) else {'rc': None}
    if rj['rc'] != 0 or rj.get('stderr'):
        fails.append(('P1.runner', str(rj)[:300]))
    ref = json.load(open(os.path.join(d, 'ref.json'), encoding='utf-8'))
    if 'crash' in ref:
        fails.append(('P1.ref', ref['crash'][-300:]))
    # P2: rejected and counted; accepted rows parsed to the oracle's values
    probs = {r[0]: (int(r[1]), int(r[2])) for r in read_tsv_rows(os.path.join(lean_dir, 'problems.tsv'))}
    # a decisions2 row with more than 9 fields: Data.loadDecisions took >= 9 columns before FB-L1
    dlines = [l.split('\t') for _, l in oracle_lines(raw['decisions2.tsv']) if l is not None]
    l1_nodes = {f[0] for f in dlines if len(f) > 9}
    fb_l1 = sum(len(f) > 9 for f in dlines)
    stats['trigger.FB-L1'] += fb_l1
    # DEV-int64, a documented deviation (FUZZ.md run B): a court, date or unit of 2^63 or more is a SCHEMA integer,
    # which Lean's Nat keeps; the reference stores int64 and rejects the row, so the node has no decision there
    big = [f[0] for f in dlines if len(f) == 9 and all(is_nat(f[c]) for c in (0, 1, 2, 3)) and int(f[0]) < NODES
           and any(int(f[c]) >= 1 << 63 for c in (1, 2, 3))]
    big_nodes = {str(int(x)) for x in big}
    stats['trigger.DEV-int64'] += len(big)
    for n in FILES:
        rows, bad, dups, l5 = orc[n]
        stats['rows_oracle_accepted'] += len(rows)
        stats['rows_oracle_rejected'] += bad
        stats['trigger.FB-L5'] += l5
        lb = probs.get(n, (0, 0))[1]
        if lb != bad + dups:
            # tags: the count is what the loader gave before the fix (FB-L1 an extra column accepted; FB-L5 an
            # unparseable confidence / score / explicit read as 0)
            tag = '.FB-L1' if n == 'decisions2.tsv' and fb_l1 else '.FB-L5' if l5 and lb == bad - l5 else ''
            fails.append(('P2.lean_bad' + tag, '%s lean %d oracle %d+%d dup' % (n, lb, bad, dups)))
        if 'crash' not in ref:
            rb = ref['bad'].get(n, 0)
            nbig = len(big) if n == 'decisions2.tsv' else 0
            if rb != bad:
                tag = '.FB-L5' if l5 and rb == bad - l5 else '.DEV-int64' if nbig and rb == bad + nbig else ''
                fails.append(('P2.ref_bad' + tag, '%s ref %d oracle %d' % (n, rb, bad)))
            # the reference's decisions count (n_present) is the rows it loaded: a repeated node counts each time
            # (the later row wins, as in Lean and the oracle)
            exp = len(rows) + dups
            if n in ref['counts'] and n not in ('issues.tsv', 'courts2.tsv', 'lawchanges.tsv', 'holdings.tsv') \
                    and ref['counts'][n] != exp:
                tag = '.FB-L5' if l5 and ref['counts'][n] == exp + l5 else \
                    '.DEV-int64' if nbig and ref['counts'][n] == exp - nbig else ''
                fails.append(('P2.ref_rows' + tag, '%s ref %d oracle %d' % (n, ref['counts'][n], exp)))
    dumped = {}
    for n in FILES:
        if n == 'holdings_cert_text.tsv':
            continue
        dumped[n] = read_tsv_rows(os.path.join(lean_dir, n))
    want = dict((n, orc[n][0]) for n in FILES)
    want['cert_text.tsv'] = orc['cert_text.tsv'][0] + orc['holdings_cert_text.tsv'][0]
    for n, rows in dumped.items():
        if rows != want[n]:
            tag = '.FB-L1' if n == 'decisions2.tsv' and fb_l1 else \
                '.FB-L5' if orc[n][3] and len(rows) == len(want[n]) + orc[n][3] else ''
            k = next((i for i, (x, y) in enumerate(zip(rows, want[n])) if x != y), min(len(rows), len(want[n])))
            fails.append(('P2.lean_rows' + tag, '%s row %d: lean %r oracle %r' % (
                n, k, (rows[k] if k < len(rows) else None) and [x[:60] for x in rows[k]],
                (want[n][k] if k < len(want[n]) else None) and [x[:60] for x in want[n][k]])))
    # P3: round trip
    for n in list(dumped) + ['quotes.tsv']:
        a = read_tsv_rows(os.path.join(lean_dir, n))
        b = read_tsv_rows(os.path.join(lean_dir, 'lean', n))
        if a != b:
            fails.append(('P3.roundtrip', n))
    # P4: quote at offset, code points
    tabs = {n: orc[n][0] for n in FILES}
    oq = oracle_quotes(tabs)
    for r in read_tsv_rows(os.path.join(lean_dir, 'quotes.tsv')):
        t, i, ok, sl = r[0], r[1], r[2] == '1', '\t'.join(r[3:])
        if (t, i) not in oq:
            fails.append(('P4.unknown_row', '%s %s' % (t, i)))
            continue
        spec_ok, osl, trig = oq[(t, i)]
        stats['quotes_checked'] += 1
        stats['quotes_ok'] += ok
        if trig:
            stats['trigger.' + trig] += 1
        if ok != spec_ok or sl != osl:
            # on a trigger row a wrong verdict is the old one: the empty quote passed (FB-L2), or only the first
            # covering window was read (FB-L3)
            fails.append(('P4.lean_vs_python' + ('.' + trig if trig and ok != spec_ok else ''),
                          '%s %s lean %s python %s slices %s' % (t, i, ok, spec_ok, sl == osl)))
        if ok and any(ord(c) > 127 for c in sl):
            stats['quotes_ok_nonascii'] += 1
    # P5: runner vs reference, quote stage and admission
    certs = read_tsv_rows(os.path.join(d, 'runner', 'certs-00.tsv')) or []
    if 'crash' not in ref and rj['rc'] == 0:
        lean_res = {}
        for r in certs:
            if len(r) >= 3:
                lean_res['%s|%s' % ({'treatment': 'treatments', 'history': 'history', 'holding': 'holdings'}[r[0]],
                                    r[1])] = r[2]
        # the decisions each certificate row names (by row id), to attribute a difference to a decisions2 row
        row_nodes = defaultdict(set)
        for t, cols in (('treatments', (1, 2)), ('history', (1, 2)), ('holdings', (1,))):
            for r in tabs[t + '.tsv']:
                row_nodes['%s|%s' % (t, r[0])].update(r[c] for c in cols)
        LQ = {'shaUnknown', 'noWindow', 'quoteMismatch', 'badRow'}
        RQ = {'noDecision', 'shaMismatch', 'offsets', 'quoteLength', 'noWindow', 'quoteMismatch', 'badRow'}
        for k, lr in lean_res.items():
            rr = ref['certs'].get(k)
            if rr is None:
                continue
            stats['certs_compared'] += 1
            dtag = '.DEV-int64' if row_nodes[k] & big_nodes else '.FB-L1' if row_nodes[k] & l1_nodes else ''
            if (lr == 'badRow') != (rr == 'badRow'):
                fails.append(('P5.badRow' + dtag, '%s lean %s ref %s' % (k, lr, rr)))
                continue
            lq, rq = lr not in LQ, rr not in RQ
            if lq != rq:
                t, i = k.split('|', 1)
                trig = oq.get((t, i), (None, None, ''))[2]
                tag = ''
                if rr == 'offsets' and lr not in LQ:
                    tag = '.FB-L2'
                elif trig == 'FB-L3':
                    tag = '.FB-L3'
                elif dtag:
                    tag = dtag
                fails.append(('P5.quote_stage' + tag, '%s lean %s ref %s' % (k, lr, rr)))
            if k.startswith('holdings|') and rr == 'part':
                stats['trigger.FB-L4'] += 1            # only the certificate's part column stops this holding
            # passed or rejected as text (DIFFTEST.md, certs): Lean's targetLater and noAuthority follow every text
            # check, and the reference makes those two decisions in its status layer, so both count as passed
            la, ra = lr in ('ok', 'okUnverifiedBy', 'targetLater', 'noAuthority'), rr == 'ok'
            if la != ra and lq == rq:
                tag = '.FB-L4' if k.startswith('holdings|') and rr == 'part' else ''
                fails.append(('P5.admission' + tag, '%s lean %s ref %s' % (k, lr, rr)))
    return fails, stats


def cmd_check(root):
    dirs = case_dirs(root)
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(check_case, dirs, chunksize=16))
    byprop = defaultdict(list)
    stats = Counter()
    variants = Counter()
    ops = Counter()
    for d, (fails, st) in zip(dirs, res):
        stats.update(st)
        cj = json.load(open(os.path.join(d, 'case.json'), encoding='utf-8'))
        variants.update(cj['variants'])
        ops.update(o for _, o in cj['ops'])
        for p, det in fails:
            byprop[p].append((os.path.basename(d), det))
    rep = {'cases': len(dirs), 'stats': dict(stats), 'variants': dict(variants), 'ops': dict(ops),
           'failures': {p: {'count': len(v), 'samples': v[:8]} for p, v in sorted(byprop.items())}}
    with open(os.path.join(root, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: rep[k] for k in ('cases', 'stats', 'variants', 'ops')}, ensure_ascii=False))
    for p, v in sorted(byprop.items()):
        print('%-34s %5d  e.g. %s %s' % (p, len(v), v[0][0], v[0][1][:220]))
    return rep


# ------------------------------------------------------------------------------------------------- real data
def cmd_real():
    """Recompute every real quote-at-offset in Python and compare with what the Lean runner admitted
    (out/certs.tsv); flag rows where code-point and byte (or UTF-16) offsets differ."""
    D = os.path.join(W, 'data')
    wins = defaultdict(list)
    nwin = Counter()
    for fn in ('cert_text.tsv', 'holdings_cert_text.tsv'):
        for _, l in oracle_lines(open(os.path.join(D, fn), 'rb').read()):
            r = l.split('\t')
            wins[r[0]].insert(0, (int(r[1]), int(r[2]), r[3]))
            nwin[fn] += 1
            if len(r[3]) != int(r[2]) - int(r[1]):
                nwin['malformed_' + fn] += 1
    lean = {}
    with open(os.path.join(W, 'out', 'certs.tsv'), encoding='utf-8', newline='\n') as f:
        next(f)
        for l in f:
            t, i, ra = l.rstrip('\n').split('\t')[:3]
            lean[({'treatment': 'treatments', 'history': 'history', 'holding': 'holdings'}[t], i)] = ra
    st = Counter()
    flagged = []
    for t, cs in (('treatments', 8), ('history', 6), ('holdings', 6)):
        for _, l in oracle_lines(open(os.path.join(D, t + '.tsv'), 'rb').read()):
            r = l.split('\t')
            sha, a, b, q = r[cs], int(r[cs + 1]), int(r[cs + 2]), r[cs + 3]
            cov = [w for w in wins.get(sha, []) if w[0] <= a and b <= w[1] and len(w[2]) == w[1] - w[0]]
            nq = norm(q)
            ok_any = any(a <= b and norm(w[2])[a - w[0]:b - w[0]] == nq for w in cov)
            ok_first = bool(cov) and a <= b and norm(cov[0][2])[a - cov[0][0]:b - cov[0][0]] == nq
            lr = lean.get((t, r[0]))
            lean_pass = lr is not None and lr not in ('shaUnknown', 'noWindow', 'quoteMismatch', 'badRow')
            st[t + '_rows'] += 1
            st[t + '_python_ok'] += ok_any
            if lr is None:
                st[t + '_not_in_lean_out'] += 1
            elif lean_pass != ok_any:
                st[t + '_DISAGREE'] += 1
                flagged.append(('disagree', t, r[0], lr, ok_any))
            if ok_any != ok_first:
                st[t + '_window_order_matters'] += 1
            if a == b:
                st[t + '_empty_quote'] += 1
            if cov:
                w = cov[0]
                pre = w[2][:a - w[0]]
                inq = w[2][a - w[0]:b - w[0]]
                if any(ord(c) > 127 for c in pre) or any(ord(c) > 127 for c in inq):
                    st[t + '_nonascii_before_or_in_quote'] += 1
                    if u8(pre) != len(pre) or u8(inq) != len(inq):
                        st[t + '_byte_vs_codepoint_differs'] += 1
                if u16(pre) != len(pre) or u16(inq) != len(inq):
                    st[t + '_utf16_vs_codepoint_differs'] += 1
                # a byte-offset reader would have put the quote elsewhere: would it still have matched?
                if ok_any and (u8(pre) != len(pre)):
                    wb = w[2].encode('utf-8')
                    s_b = a - w[0]
                    alt = wb[s_b:s_b + (b - a)].decode('utf-8', 'replace')
                    st[t + '_byte_reading_would_match'] += norm(alt) == nq
    st.update({'windows_' + k: v for k, v in nwin.items()})
    print(json.dumps(dict(st), indent=1))
    print('flagged', len(flagged), flagged[:10])
    return st, flagged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['gen', 'run', 'check', 'real', 'all', 'refonly'])
    ap.add_argument('--n', type=int, default=5000)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--dir', default=DEFAULT_DIR)
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    if a.cmd in ('gen', 'all'):
        shutil.rmtree(a.dir, ignore_errors=True)
        os.makedirs(a.dir)
        with ProcessPoolExecutor(a.jobs) as ex:
            list(ex.map(gen_case, [a.seed * 1000003 + i for i in range(a.n)],
                        [os.path.join(a.dir, 'c%05d' % i) for i in range(a.n)], chunksize=32))
    if a.cmd in ('run', 'all'):
        cmd_run(a.dir, a.jobs)
    if a.cmd == 'refonly':                     # re-run only the reference (e.g. FUZZ_REF_DIR=<older copy>), then check
        with ProcessPoolExecutor(a.jobs) as ex:
            list(ex.map(run_ref, case_dirs(a.dir), chunksize=16))
    if a.cmd in ('check', 'all', 'refonly'):
        cmd_check(a.dir)
    if a.cmd == 'real':
        cmd_real()


if __name__ == '__main__':
    main()
