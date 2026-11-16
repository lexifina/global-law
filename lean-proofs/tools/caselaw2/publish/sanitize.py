"""Replace a user's home paths in the files of a release (see caselaw2/PUBLISHING.md, section 3).

    python3 -I sanitize.py --user NAME FILELIST     # FILELIST: one path per line, e.g. from `git diff --cached --name-only`

Windows (plain, JSON-escaped, forward-slash, Git Bash), WSL and Linux home paths become `~`, `/mnt/c/Users/$USER`,
and `ls -l` owner columns become `user`. Files that are not UTF-8 are listed and left alone. Grep again afterwards.
"""
import argparse
import re

ap = argparse.ArgumentParser()
ap.add_argument('--user', required=True)
ap.add_argument('filelist')
a = ap.parse_args()

u = a.user
BS = '\\'
subs = [
    ('/mnt/c/Users/' + u, '/mnt/c/Users/$USER'),
    ('C:' + BS * 2 + 'Users' + BS * 2 + u, '~'),   # JSON-escaped
    ('C:' + BS + 'Users' + BS + u, '~'),
    ('C:/Users/' + u, '~'),
    ('/c/Users/' + u, '~'),
    ('/home/' + u, '~'),
    (u + ' ' + u, 'user user'),
]
subs = [(re.compile(re.escape(x), re.I), r) for x, r in subs]
owner = re.compile(re.escape(u) + r'/\d+')   # Git Bash `ls -l` / tar owner/group ids

changed = 0
for p in open(a.filelist, encoding='utf-8').read().split('\n'):
    if not p:
        continue
    b = open(p, 'rb').read()
    try:
        s = b.decode('utf-8')
    except UnicodeDecodeError:
        print('not UTF-8, left alone:', p)
        continue
    t = s
    for x, r in subs:
        t = x.sub(lambda m: r, t)
    t = owner.sub('user', t)
    if t != s:
        open(p, 'wb').write(t.encode('utf-8'))
        changed += 1
print('changed', changed)
