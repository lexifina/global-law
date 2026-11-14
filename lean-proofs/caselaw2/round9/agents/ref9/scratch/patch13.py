p = '~/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref/precedent_ref.py'
s = open(p, encoding='utf-8', newline='').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new)
rep("""    def zone_apply(self, res, zr, passes=True):
        \"\"\"Round 9: a row whose complete round-8 verdict is `ok` (D9-4 (2): `passes` = also past the Lean's date
        order and power checks) and whose zone result is False becomes `partZone`; counts the rows that reach the
        check (zone_missing_rows: no kept zone of the text owner).\"\"\"
        if res != 'ok' or not passes:
            return res
        return self.zone_count(zr)""", """    def zone_apply(self, res, zr, passes=True, key=None):
        \"\"\"Round 9: a row whose complete round-8 verdict is `ok` (D9-4 (2): `passes` = also past the Lean's date
        order and power checks) and whose zone result is False becomes `partZone`; counts the rows that reach the
        check (zone_missing_rows: no kept zone of the text owner). D9-13: a row the Lean writes targetLater /
        noAuthority (passes False; the reference's `ok`) keeps that verdict, but when its quote fails the zone test
        it feeds no findings: `key` (table, id) goes to zone_mute and the row is not put in the admitted views.\"\"\"
        if res != 'ok':
            return res
        if not passes:
            if zr is False and key is not None:
                self.zone_mute.add(key)
            return res
        return self.zone_count(zr)""")
rep("""                    res = self.zone_apply(res, zr, self.lean_cert_passes('treatments', r))""",
    """                    res = self.zone_apply(res, zr, self.lean_cert_passes('treatments', r), ('t', r['id']))""")
rep("""                                        self.lean_cert_passes('treatments', entry[0]))""",
    """                                        self.lean_cert_passes('treatments', entry[0]), ('t', entry[0]['id']))""")
rep("""        for (r, res) in results:
            if res == 'ok':
                self.adm_treat[r['target']].append(r)""", """        for (r, res) in results:
            if res == 'ok' and ('t', r['id']) not in self.zone_mute:      # (round 9, D9-13)
                self.adm_treat[r['target']].append(r)""")
rep("""                res = self.zone_apply(res, self.zone_result(owner, r, None), self.lean_cert_passes('history', r))
            self.cert_ok[('history.tsv', r['id'])] = res
            if res == 'ok':""", """                res = self.zone_apply(res, self.zone_result(owner, r, None), self.lean_cert_passes('history', r),
                                      ('h', r['id']))
            self.cert_ok[('history.tsv', r['id'])] = res
            if res == 'ok' and ('h', r['id']) not in self.zone_mute:          # (round 9, D9-13)""")
rep("""        self.zone_missing = self.zone_checked = self.zone_failed = 0""", """        self.zone_missing = self.zone_checked = self.zone_failed = 0
        self.zone_mute = set()     # round 9 (D9-13): (t|h, id) of rows kept at targetLater / noAuthority whose zone fails""")
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
