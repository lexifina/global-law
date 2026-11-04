#!/usr/bin/env python3
"""Check the words that move credit gives back (word_moves.json: law.py against law.py without it): is each such
word, with the words around it, already in the text of the version the newly credited law wrote? If so the credit
is right by words' own promise (a word keeps the law that wrote it); if not, the move credit matched unrelated text.

  python performance/experiments/word_moves_check.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import law  # noqa: E402

HERE = Path(__file__).resolve().parent
res = json.loads((HERE / 'word_moves.json').read_text(encoding='utf-8'))
WINDOW = int(sys.argv[1]) if len(sys.argv) > 1 else 3  # words either side


def words_with_law(runs):
    out = []
    for l, s in runs:
        out += [(w, l) for w in re.findall(r'\S+', s)]
    return out


summary = {'checked': 0, 'in_the_credited_law_text': 0, 'not_found': 0}  # in_the_credited...: already in an earlier version
examples = []
for key in res['summary']['law.py']['per_file']:
    pass
# re-run both on the files that differ, to get the runs (word_moves.json keeps only counts)
diff_files = [k for k, v in res['summary']['law.py']['per_file'].items() if v['chars_differ']]
for key in diff_files:
    date, path = key.split(' ', 1)
    law.MOVE_CREDIT = False
    base = words_with_law(law.words_on(date, path))
    law.MOVE_CREDIT = True
    moved = words_with_law(law.words_on(date, path))
    ordered = []  # (law, text) in the order the versions took force
    for commit, credit in law.versions_in_force(date, path):
        if commit:
            name = next((h['law'] for h in law.history(path) if h['commit'] == commit), credit)
            ordered.append((name, ' '.join((law.read_version(path, commit) or '').split())))
    words = [w for w, _ in moved]
    changed = [k for k, ((w, a), (_, b)) in enumerate(zip(base, moved)) if a != b]
    for k in changed[::max(1, len(changed) // 300)]:  # a sample of up to ~300 words a file
        phrase = ' '.join(words[max(0, k - WINDOW):k + WINDOW + 1])
        amending = base[k][1]  # the law the words went to without move credit
        first = next((n for n, (name, _) in enumerate(ordered) if name == amending), len(ordered))
        before = any(phrase in t for _, t in ordered[:first])
        summary['checked'] += 1
        # The words were in the law before the amending law took force: it did not write them, move credit is right.
        summary['in_the_credited_law_text' if before else 'not_found'] += 1
        if not before and len(examples) < 12:
            examples.append({'file': path, 'phrase': phrase, 'credited_now': moved[k][1], 'before': amending})
law.close_readers()
summary['examples_not_found'] = examples
(HERE / 'word_moves_check.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding='utf-8')
print(json.dumps({k: v for k, v in summary.items() if k != 'examples_not_found'}))
for e in examples[:8]:
    print(e)
