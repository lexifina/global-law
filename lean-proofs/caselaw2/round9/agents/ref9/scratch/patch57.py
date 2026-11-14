p = '~/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref/precedent_ref.py'
s = open(p, encoding='utf-8', newline='').read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old, s.count(old))
    s = s.replace(old, new)


rep("""CLAIMS = ('recognised', 'operativeWords', 'doctrine')
""", """CLAIMS = ('recognised', 'operativeWords', 'doctrine', 'joinedFar', 'implicitReject')   # round 9: DESIGN9 §5, §7
# round 9 (round9/DESIGN9.md §5, D9-5): a far antecedent joined quote, with the claim `joinedFar` only; JSON first
JOINED_FAR_MAX = _r7('joined_far_max', 1200)
# round 9 (round9/DESIGN9.md §7, D9-5): the cues a soft-kind row with the claim `implicitReject` adds to its kind's list
IMPLICIT_REJECT = _r7('implicit_reject', (
    'cannot agree', 'do not agree', 'unpersuaded', 'not convinced', 'wrongly decided', 'incorrectly decided',
    'erroneously decided', 'unsound', 'erroneous', 'incorrect', 'mistaken', 'undermined', 'eroded', 'discredited',
    'called into question', 'contrary to', 'depart from', 'departs from'))
""")
rep("""    def check_cert(self, cert, owners, kind, need_target, require_verb=True, target=None, mode=None, hclaim=None,
                   by=None):""", """    def check_cert(self, cert, owners, kind, need_target, require_verb=True, target=None, mode=None, hclaim=None,
                   by=None, extra_cues=()):""")
rep("""            if hclaim and 'setAside' in hclaim and kind == 'vacated':
                verbs = tuple(verbs or ()) + SET_ASIDE      # round 7 (DESIGN7 §3.2): claim-gated vacatur cue
""", """            if hclaim and 'setAside' in hclaim and kind == 'vacated':
                verbs = tuple(verbs or ()) + SET_ASIDE      # round 7 (DESIGN7 §3.2): claim-gated vacatur cue
            if extra_cues:
                verbs = tuple(verbs or ()) + tuple(extra_cues)   # round 9 (DESIGN9 §7): implicitReject
""")
rep("""    def check_joined(self, r, lines, mode):""", """    def check_joined(self, r, lines, mode, far=False, implicit=False):""")
rep("""            if rel == 'antecedent':
                # §2.2: the joined quote ends before the main quote starts, at most `joined_gap_max` characters
                # before it; the main quote has an anaphor and a cue of the row's kind (the plain list)
                if not (e <= cert.start and cert.start - e <= JOINED_GAP_MAX):
                    return 'joinedRelation'
""", """            if rel == 'antecedent':
                # §2.2: the joined quote ends before the main quote starts, at most `joined_gap_max` characters
                # before it; the main quote has an anaphor and a cue of the row's kind (the plain list)
                if not e <= cert.start:
                    return 'joinedRelation'
                if cert.start - e > JOINED_GAP_MAX:
                    # round 9 (DESIGN9 §5): with the claim `joinedFar`, a gap up to joined_far_max on the row's own
                    # text: a usable window covering [j_end, start), no newline there, no index key of another
                    # node starting there (REF_QUESTIONS9.md Q9-12..Q9-15); the anaphor / cue tests below as §2.2
                    if not far:
                        return 'joinedRelation'
                    v = self.far_gap(cert, e, r['target'])
                    if v is not None:
                        return v
""")
rep("""        return self.check_cert(cert, [r['by']], kind, False, target=r['target'], mode=mode)

    def check_anchored""", """        return self.check_cert(cert, [r['by']], kind, False, target=r['target'], mode=mode,
                               extra_cues=IMPLICIT_REJECT if implicit else ())

    def far_gap(self, cert, e, target):
        \"\"\"Round 9 (round9/DESIGN9.md §5, claim `joinedFar`): the tests of a joined antecedent quote ending at `e`
        more than joined_gap_max characters before the main quote starts. -> a failure reason, or None. Order (Q9-12):
        joinedFarGap (start - e > joined_far_max), joinedFarWindow (no usable window of the row's text_sha - well
        formed, covering [e, start), hash-consistent - the first in cert_text order is used), joinedFarPara (a LF in
        the window's text [e, start), Q9-13), joinedFarKey (an index key that maps to a node other than the target
        starts at a compact position whose offset is in [e, start); the compact form is that of the window's text
        from e to its end, so a key may run past start; an ambiguous key is no key, D8-15; Q9-14).\"\"\"
        D = self.D
        start = cert.start
        if start - e > JOINED_FAR_MAX:
            return 'joinedFarGap'
        win = None
        for (s0, e0, w, hok) in D.cert_text.get(cert.sha, ()):
            if s0 <= e and start <= e0 and len(w) == e0 - s0 and hok:
                win = (s0, w)
                break
        if win is None:
            return 'joinedFarWindow'
        s0, w = win
        if '\\n' in w[e - s0:start - s0]:
            return 'joinedFarPara'
        if D.cite_index is None:
            return None
        self._cite_keys_of(target)          # builds the key lengths
        lens, idx = self._key_lens, D.cite_index
        tail = ascii_lower(w[e - s0:])
        comp, pos = [], []
        for i, ch in enumerate(tail):
            if '0' <= ch <= '9' or 'a' <= ch <= 'z':
                comp.append(ch)
                pos.append(e + i)
        c = ''.join(comp)
        for i in range(len(c)):
            if pos[i] >= start:
                break
            for L in lens:
                if i + L > len(c):
                    break
                v = idx.get(c[i:i + L])
                if v is not None and v != target:
                    return 'joinedFarKey'
        return None

    def check_anchored""")
rep("""                else:
                    res = self.check_joined(r, jl, 'doctrine')
            elif wit is not None and D.has(r['by']) and D.has(r['target']):""", """                else:
                    res = self.check_joined(r, jl, 'doctrine')
            elif claim == 'implicitReject' and r['kind'] not in SOFT_TREAT:
                res = 'implicitBadKind'            # round 9 (DESIGN9 §7; Q9-16): only a soft kind takes the claim
            elif wit is not None and D.has(r['by']) and D.has(r['target']):""")
rep("""                res = self.check_joined(r, jl, 'operative' if claim == 'operativeWords' else None)
                if claim == 'operativeWords':""", """                res = self.check_joined(r, jl, 'operative' if claim == 'operativeWords' else None,
                                        far=claim == 'joinedFar', implicit=claim == 'implicitReject')
                if claim == 'operativeWords':""")
rep("""            else:
                res = self.check_cert(r['cert'], [r['by']], r['kind'], True, target=r['target'])
            # fuzz: a row naming""", """            else:
                res = self.check_cert(r['cert'], [r['by']], r['kind'], True, target=r['target'],
                                      extra_cues=IMPLICIT_REJECT if claim == 'implicitReject' else ())
            # fuzz: a row naming""")
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched')
