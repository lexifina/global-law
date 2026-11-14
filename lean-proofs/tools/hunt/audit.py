"""Mechanical checks over every Hunt/<Name>.lean: things a script can decide without judgment.

    python -I tools/hunt/audit.py            -> tools/hunt/out/audit/mechanical.json (+ a table on stdout)

A  technique words in the rules part (a rule that names a plan is suspect)
B  constructs that bypass the checker or hide behaviour (sorry, native_decide, axiom, unsafe, implemented_by, extern)
C  every cited section exists in the release point
D  every dollar figure in the rules part: found verbatim in the text of a section the file cites, or not
E  moves: constructors of the move type, and how many carry a citation on their line or the line above
F  amounts written into the search part's move generator (a search that is handed the winning number is suspect)
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HUNT = os.path.join(ROOT, 'LegalProofs', 'USTax', 'Hunt')
P = json.load(open(os.path.expanduser('~/Documents/tax-formalization-data/out/t26.json'), encoding='utf-8'))['provisions']
TEXT = {}
for p in P:
    m = re.match(r'/us/usc/t26/s([^/]+)', p['id'])
    if m:
        TEXT.setdefault(m.group(1), []).append((p.get('heading') or '') + ' ' + (p.get('text') or ''))
TEXT = {k: ' '.join(v) for k, v in TEXT.items()}

WORDS = r'backdoor|loophole|mega|stack(?:ing)?|strip|shelter|trick|exploit|arbitrage|scheme|dodge|bunch|harvest|ladder|mixing bowl|freeze|zeroed|work-?around|circumvent|game|abuse'
BAD = r'\bsorry\b|native_decide|^\s*axiom\b|\bunsafe\b|implemented_by|@\[extern'
SPLIT = re.compile(r'^/-! ## (Part 2\. Search|Part B\. Search|Search)', re.M)

def strip_comments(s):
    s = re.sub(r'/-.*?-/', lambda m: '\n' * m.group(0).count('\n'), s, flags=re.S)
    return re.sub(r'--.*', '', s)

out = {}
for fn in sorted(os.listdir(HUNT)):
    if not fn.endswith('.lean'): continue
    name = fn[:-5]
    src = open(os.path.join(HUNT, fn), encoding='utf-8').read()
    m = SPLIT.search(src)
    rules, search = (src[:m.start()], src[m.start():]) if m else (src, '')
    rules_code, search_code = strip_comments(rules), strip_comments(search)
    r = {'lines': src.count('\n') + 1, 'rules_lines': rules.count('\n'), 'search_lines': search.count('\n')}
    # A
    r['technique_words_in_rule_code'] = sorted({w.lower() for w in re.findall(WORDS, rules_code, re.I)})
    r['technique_words_in_rule_comments'] = [
        (i + 1, ln.strip()[:140]) for i, ln in enumerate(rules.split('\n'))
        if re.search(WORDS, ln, re.I) and not re.search(WORDS, strip_comments(ln + '\n'), re.I)][:12]
    # B
    r['bypass_constructs'] = [(i + 1, ln.strip()[:100]) for i, ln in enumerate(strip_comments(src).split('\n')) if re.search(BAD, ln)]
    # C
    cited = sorted(set(re.findall(r'§§?\s*(\d+[A-Z]?(?:-\d+)?)', src)), key=lambda x: (len(x), x))
    r['sections_cited'] = len(cited)
    r['sections_missing'] = [c for c in cited if c not in TEXT]
    # D
    stat = ' '.join(TEXT.get(c, '') for c in cited)
    statnums = {int(x.replace(',', '')) for x in re.findall(r'\$?(\d{1,3}(?:,\d{3})+|\d{3,})', stat)}
    nums = sorted({int(x.replace('_', '')) for x in re.findall(r'(?<![\w.])(\d[\d_]{2,})(?![\w.])', rules_code)})
    nums = [n for n in nums if n >= 200]
    r['figures_in_rules'] = len(nums)
    r['figures_in_statute'] = [n for n in nums if n in statnums]
    r['figures_not_in_statute'] = [n for n in nums if n not in statnums]
    # E
    moves = []
    for blk in re.finditer(r'^inductive (\w*(?:Move|Act|Step|Choice)\w*)[^\n]*\n((?:\s+\|[^\n]*\n|\s*--[^\n]*\n|\s*\n)+)', rules, re.M):
        lines = blk.group(2).split('\n')
        for i, ln in enumerate(lines):
            c = re.match(r'\s+\|\s*(\w+)', ln)
            if c:
                ctx = ln + ' ' + (lines[i - 1] if i and lines[i - 1].strip().startswith('--') else '')
                moves.append((blk.group(1), c.group(1), bool(re.search(r'§|Reg\.|Notice|Rev\.', ctx))))
    r['moves'] = len(moves)
    r['moves_cited'] = sum(1 for m_ in moves if m_[2])
    r['moves_uncited'] = [f'{a}.{b}' for a, b, c in moves if not c][:20]
    # F
    gen = re.search(r'def (?:moves|amounts|candidates|options)\b.*?(?=\n(?:def|partial def|/-!|theorem|#eval)\b)', search_code, re.S)
    r['generator_literals'] = sorted({int(x.replace('_', '')) for x in re.findall(r'(?<![\w.])(\d[\d_]{2,})(?![\w.])', gen.group(0))}) if gen else None
    out[name] = r

os.makedirs(os.path.join(ROOT, 'tools', 'hunt', 'out', 'audit'), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, 'tools', 'hunt', 'out', 'audit', 'mechanical.json'), 'w', encoding='utf-8'), indent=1)
print(f"{'file':14} {'rules':>5} {'srch':>5} {'words':>5} {'bypass':>6} {'§':>3} {'§miss':>5} {'fig':>4} {'in text':>7} {'not':>4} {'moves':>5} {'cited':>5}")
for k, r in out.items():
    print(f"{k:14} {r['rules_lines']:5} {r['search_lines']:5} {len(r['technique_words_in_rule_code']):5} {len(r['bypass_constructs']):6} "
          f"{r['sections_cited']:3} {len(r['sections_missing']):5} {r['figures_in_rules']:4} {len(r['figures_in_statute']):7} "
          f"{len(r['figures_not_in_statute']):4} {r['moves']:5} {r['moves_cited']:5}")
for k, r in out.items():
    print('\n==', k)
    for key in ('technique_words_in_rule_code', 'technique_words_in_rule_comments', 'bypass_constructs', 'sections_missing',
                'figures_not_in_statute', 'moves_uncited', 'generator_literals'):
        if r[key]: print(' ', key, ':', r[key])
