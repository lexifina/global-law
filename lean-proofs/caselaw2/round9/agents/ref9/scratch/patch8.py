p = '~/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref/precedent_ref.py'
s = open(p, encoding='utf-8', newline='').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new)
rep("""                    # text: a usable window covering [j_end, start), no newline there, no index key of another
                    # node starting there""", """                    # text: a usable window covering [j_end, start), no index key of another node starting there
                    # (no paragraph test: D9-7)""")
rep("""        cues = ANCHOR + ANCHOR_WIDE if (hclaim and 'anchorWide' in hclaim) else ANCHOR""",
    """        cues = ANCHOR + ANCHOR_WIDE + ANCHOR_WIDE9 if (hclaim and 'anchorWide' in hclaim) else ANCHOR""")
rep("""SCOTUS_COURT = 2906 """, """# round 9 (round9/DESIGN9.md §8, D9-9): the judge-form strings `anchorWide` adds (a JSON list `anchor_wide9`, else
# DESIGN9's three; the Lean may instead extend `anchor_wide` itself: a string in both lists is harmless)
ANCHOR_WIDE9 = _r7('anchor_wide9', ('district judge', 'magistrate judge', 'trial judge'))
SCOTUS_COURT = 2906 """)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
