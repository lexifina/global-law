"""Case law in the tree: corpora of court decisions (lexifina/switzerland-caselaw and the cantons'), read with the same
tools as law. A small tree built here: Swiss federal law (one article, two versions) and a case-law corpus (three
decisions, a correction, and the judgment overlay), with tools/law.py, tools/countries.py and the MCP server.

  python -m unittest tests.test_caselaw -v

Each decision is one file and one commit (Kind: court), dated the day given. The tools read a decision as they read a
provision (show, log, blame, words, diff, today, read_law, who_wrote, list_provisions); lists and searches of law leave
case law out and say so, unless the call names it; check_precedent and what_else_changes read the overlay; citations of
any federal act by its abbreviation, and of decisions by BGE reference or docket, resolve.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True

LAW = 'switzerland/bund/acts'
CASES = 'switzerland/bund/caselaw'
ART = f'{LAW}/101/art-029.md'
D1 = 'decisions/bger/2010/1C_100-2010.md'
D2 = 'decisions/bge/2016/BGE-142-II-307.md'
D3 = 'decisions/bger/2022/4A_123-2022.md'
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')


def decision(title: str, text: str) -> str:
    return f'---\ncourt: "Bundesgericht"\n---\n\n# {title}\n\n## Text\n\n{text}\n'


class CaseLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'data').mkdir()
        shutil.copy(ROOT / 'data' / 'swiss-aliases.json', t.root / 'data' / 'swiss-aliases.json')
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        manifest = {'corpora': [
            {'path': LAW, 'name': 'Swiss federal law', 'language': 'de', 'in_force_trailer': 'In-force', 'code': 'CH'},
            {'path': CASES, 'name': 'Case law: Switzerland (federal courts)', 'language': 'de', 'kind': 'judgments',
             'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'CH'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('AS 2000 1', {'101/art-029.md': '1 Jede Person hat Anspruch auf gleiche Behandlung.\n'
                                                   '2 Die Parteien haben Anspruch auf rechtliches Gehör.\n'},
                   In_force='2000-01-01', Kind='law')
        cls.v2020 = law.commit('AS 2020 5', {'101/art-029.md': '1 Jede Person hat Anspruch auf gleiche und gerechte Behandlung.\n'
                                                               '2 Die Parteien haben Anspruch auf rechtliches Gehör.\n'},
                               In_force='2020-01-01', Kind='law')
        c = t.corpus(CASES)
        c.commit('Bundesgericht 1C_100/2010', {D1: decision('Rechtliches Gehör', 'Das rechtliche Gehör wurde verletzt.\nDie Beschwerde ist gutzuheissen.')},
                 Kind='court', In_force='2010-05-05', Decided='2010-05-05', Court='Bundesgericht', Docket='1C_100/2010',
                 Cites=f'{ART} (Art. 29 Abs. 2 BV)')
        c.commit('Bundesgericht 1C_100/2010', {D1: decision('Rechtliches Gehör', 'Das rechtliche Gehör wurde verletzt.\nDie Beschwerde wird gutgeheissen.')},
                 Kind='correction', In_force='2011-01-01', Corrected='2011-01-01', Docket='1C_100/2010')
        c.commit('Bundesgericht (BGE) BGE 142 II 307', {D2: decision('Anspruch auf Begründung', 'Aus dem Gehörsanspruch folgt die Begründungspflicht.')},
                 Kind='court', In_force='2016-06-01', Decided='2016-06-01', Court='Bundesgericht', Docket='BGE 142 II 307',
                 BGE='BGE 142 II 307', Cites=f'{ART} (Art. 29 Abs. 2 BV)')
        c.commit('Bundesgericht 4A_123/2022', {D3: decision('Kündigung', 'Die Kündigung war missbräuchlich.')},
                 Kind='court', In_force='2022-03-03', Decided='2022-03-03', Court='Bundesgericht', Docket='4A_123/2022',
                 Cites=f'{ART} (Art. 29 BV)')
        rows = [{'decided': '2010-05-05', 'name': 'Bundesgericht 1C_100/2010', 'court': 'Bundesgericht', 'citation': '1C_100/2010',
                 'url': 'https://example.org/1', 'how': 'Art. 29 Abs. 2 BV', 'mentions': 1, 'decision': D1},
                {'decided': '2016-06-01', 'name': 'Bundesgericht BGE 142 II 307', 'court': 'Bundesgericht',
                 'citation': 'BGE 142 II 307', 'url': 'https://example.org/2', 'how': 'Art. 29 Abs. 2 BV', 'mentions': 2, 'decision': D2},
                {'decided': '2022-03-03', 'name': 'Bundesgericht 4A_123/2022', 'court': 'Bundesgericht', 'citation': '4A_123/2022',
                 'url': 'https://example.org/3', 'how': 'Art. 29 BV', 'mentions': 1, 'decision': D3, 'law_commit': cls.v2020}]
        c.commit('Lexifina', {f'judgments/{LAW}/101/art-029.jsonl': ''.join(json.dumps(r) + '\n' for r in rows),
                              'corpus.json': json.dumps({'corpus': 'ch/bund/caselaw', 'kind': 'judgments', 'name': 'Case law',
                                                         'in_force_trailer': 'In-force'})},
                 Kind='documentation')
        t.pin()
        cls.answers = {}

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def cli(self, *args) -> str:
        out, err, code = self.t.cli(*args)
        self.assertEqual(code, 0, err)
        return out + err

    def calls(self, *calls) -> list[dict]:
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', CALL], cwd=self.t.root, input=json.dumps(calls),
                              capture_output=True, encoding='utf-8', timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    # --- a decision read like a provision ------------------------------------------------------------------------

    def test_law_py_reads_a_decision(self):
        path = f'{CASES}/{D1}'
        self.assertIn('wird gutgeheissen', self.cli('show', '2012-01-01', path))
        self.assertIn('ist gutzuheissen', self.cli('show', '2010-06-01', path))
        log = self.cli('log', path)
        self.assertIn('Bundesgericht 1C_100/2010', log)
        self.assertIn('2011-01-01', log)
        blame = self.cli('blame', '2012-01-01', path)
        self.assertIn('court ruling, not a law', blame)
        self.assertIn('correction', blame)
        self.assertIn('court ruling, not a law', self.cli('words', '2012-01-01', path))
        self.assertIn('gutgeheissen', self.cli('diff', '2010-06-01', '2012-01-01', path))
        self.assertNotIn('same', self.cli('today', '2010-06-01', path).split('\n')[0].lower())

    def test_laws_leaves_out_decisions_unless_named(self):
        laws = self.cli('laws', '2000-01-01', '2030-01-01')
        self.assertIn('AS 2020 5', laws)
        self.assertNotIn('4A_123/2022', laws)
        self.assertIn('case law is not listed', laws)
        swiss = self.cli('laws', '2000-01-01', '2030-01-01', 'switzerland')
        self.assertIn('AS 2020 5', swiss)
        self.assertNotIn('4A_123/2022 (court decision)', swiss)
        decisions = self.cli('laws', '2000-01-01', '2030-01-01', 'switzerland/caselaw')
        self.assertIn('Bundesgericht 4A_123/2022 (court decision)', decisions)
        self.assertNotIn('AS 2020 5', decisions)

    def test_world_labels_the_latest_decision(self):
        self.assertIn('Bundesgericht 4A_123/2022 (latest decision), given 2022-03-03', self.cli('world', '2023-01-01'))

    def test_countries_adds_case_law_only_by_name(self):
        def add(name):
            done = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py', 'add', name], cwd=self.t.root,
                                  capture_output=True, encoding='utf-8', timeout=120)
            return done.stdout + done.stderr
        swiss = add('switzerland')
        self.assertIn(LAW, swiss)
        self.assertNotIn(CASES, swiss)
        self.assertIn(CASES, add('switzerland/caselaw'))
        self.assertIn(CASES, add(CASES))
        listing = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py'], cwd=self.t.root,
                                 capture_output=True, encoding='utf-8', timeout=120).stdout
        self.assertTrue(any(CASES in l and 'court decisions' in l for l in listing.splitlines()), listing)

    # --- the server --------------------------------------------------------------------------------------------

    def test_check_precedent_and_what_else_changes_read_the_overlay(self):
        prec, else_, read = self.calls(('check_precedent', {'path': ART, 'date': '2023-01-01'}),
                                       ('what_else_changes', {'path': ART, 'date': '2023-01-01'}),
                                       ('read_law', {'path': f'{CASES}/{D2}', 'date': '2023-01-01'}))
        self.assertFalse(prec['error'], prec['text'])
        self.assertEqual(prec['data']['judgments_recorded'], 3)
        by = {c['citation']: c for c in prec['data']['checks']}
        self.assertFalse(by['1C_100/2010']['same_words'])  # decided before AS 2020 5 changed para. 1
        self.assertTrue(by['4A_123/2022']['same_words'])
        self.assertEqual(by['BGE 142 II 307']['decision'], f'{CASES}/{D2}')
        self.assertEqual(prec['data']['checks'][0]['citation'], '4A_123/2022')  # latest first
        self.assertFalse(else_['error'], else_['text'])
        self.assertIn('court decision(s) cite it', else_['text'])
        self.assertIn(f'{CASES}/{D3}', else_['text'])
        self.assertFalse(read['error'], read['text'])
        self.assertIn('Begründungspflicht', read['text'])

    def test_lists_and_searches_leave_case_law_out_unless_asked(self):
        q = 'Gehör'
        answers = self.calls(('search_law', {'query': q, 'date': '2023-01-01'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'kind': 'judgments'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'jurisdiction': CASES}),
                             ('laws_between', {'start': '2000-01-01', 'end': '2030-01-01'}),
                             ('laws_between', {'start': '2000-01-01', 'end': '2030-01-01', 'kind': 'judgments'}),
                             ('search_changes', {'query': 'Bundesgericht'}),
                             ('search_changes', {'query': 'Bundesgericht', 'jurisdiction': 'switzerland/caselaw'}),
                             ('phrase_history', {'query': q}),
                             ('changes_between', {'date_a': '2009-01-01', 'date_b': '2023-01-01'}),
                             ('world_on_date', {'date': '2023-01-01'}))
        for a in answers:
            self.assertFalse(a['error'], a['text'])
        law_only, judgments, named, laws, decisions, changes, changes_cl, phrase, between, world = answers
        self.assertIn(ART, law_only['text'])
        self.assertNotIn(CASES, law_only['text'].split('Not read')[0])
        self.assertIn('Not read, as they hold court decisions', law_only['text'])
        self.assertIn(f'{CASES}/{D1}', judgments['text'])
        self.assertNotIn(ART, judgments['text'])
        self.assertIn(f'{CASES}/{D1}', named['text'])
        self.assertIn('AS 2020 5', laws['text'])
        self.assertNotIn('4A_123/2022', laws['text'].split('Not read')[0])
        self.assertIn('4A_123/2022', decisions['text'])
        self.assertNotIn('AS 2020 5', decisions['text'])
        self.assertEqual(changes['data']['changes'], [])
        self.assertIn('Not read', changes['text'])
        self.assertTrue(changes_cl['data']['changes'])
        self.assertIn(ART, phrase['text'])
        self.assertNotIn(f'{CASES}/', phrase['text'].split('Not read')[0])
        self.assertIn(ART, between['text'])
        self.assertNotIn(f'{CASES}/', between['text'].split('Not read')[0])
        self.assertIn('(latest decision), given 2022-03-03', world['text'])

    def test_decisions_by_docket_and_bge_reference(self):
        found, bge, details, cites = self.calls(
            ('find_provision', {'query': '4A_123/2022'}),
            ('find_provision', {'query': 'BGE 142 II 307'}),
            ('law_details', {'law': 'BGE 142 II 307'}),
            ('resolve_citations', {'text': 'Nach Art. 29 Abs. 2 BV (BGE 142 II 307; Urteil 1C_100/2010) und Art. 336 OR '
                                           'sowie Art. 4 StG.', 'date': '2023-01-01'}))
        for a in (found, bge, details, cites):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{CASES}/{D3}', found['text'])
        self.assertIn(f'{CASES}/{D2}', bge['text'])
        self.assertIn('BGE 142 II 307', details['text'])
        self.assertIn(f'{CASES}/{D2}', details['text'])
        text = json.dumps(cites['data'], ensure_ascii=False)
        self.assertIn(ART, text)
        self.assertIn(f'{CASES}/{D2}', text)
        self.assertIn(f'{CASES}/{D1}', text)
        self.assertIn(f'{LAW}/220/art-336.md', text)  # any SR act by its abbreviation (OR is SR 220)
        self.assertNotIn('641.10', text)  # "StG" is a canton's tax act as often as the federal stamp duty act

    def test_a_decision_is_read_like_a_provision(self):
        path = f'{CASES}/{D1}'
        who, listed, cases, hist = self.calls(('who_wrote', {'path': path, 'date': '2012-01-01'}),
                                              ('list_provisions', {'path': f'{CASES}/decisions/bger'}),
                                              ('applies_to_case', {'path': path, 'commenced': '2010-01-01'}),
                                              ('provision_history', {'path': path}))
        for a in (who, listed, cases, hist):
            self.assertFalse(a['error'], a['text'])
        self.assertIn('Bundesgericht 1C_100/2010', who['text'])
        self.assertIn('Rechtliches Gehör', listed['text'])
        self.assertTrue(cases['data']['court_decision'])
        self.assertIn('court decision, not a law', cases['text'])
        self.assertIn('2010-05-05', hist['text'])
        self.assertIn('2011-01-01', hist['text'])

    def test_swiss_citation_forms(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        rx = m.CH_ARTICLE
        for text, abbr in (('Art. 336 OR', 'OR'), ('art. 29 al. 2 Cst.', 'Cst.'), ('Art. 106 Abs. 1 StGB', 'StGB'),
                           ('Art. 6bis ZGB', 'ZGB'), ('art. 8 let. a LEI', 'LEI')):
            hit = rx.search(text)
            self.assertIsNotNone(hit, text)
            self.assertEqual(hit.group('abbr'), abbr)
        for other in ('art. 14 CE', 'Art. 16a Abs. 1 GG', 'art. 194 alin. (1) din Legea nr. 31/1990', 'Art. 4 StG', 'art. 61 LPA'):
            self.assertIsNone(rx.search(other), other)
        self.assertEqual(m.swiss_sr('OR'), '220')
        self.assertEqual(m.swiss_sr('Cost.'), '101')  # the Italian Constitution's abbreviation, not "COST"
        self.assertEqual(m.swiss_sr('LTF'), '173.110')
        self.assertIsNone(m.swiss_sr('KV'))
        for ref in ('BGE 142 II 307', 'ATF 143 I 284', '4A_123/2024', '4C.237/1999', 'A-1234/2020', 'BB.2020.123'):
            self.assertTrue(m.CH_DECISION.fullmatch(ref), ref)

    def test_prompt_names_check_precedent(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        self.assertIn('check_precedent', m.PROMPTS['provision_on_a_date'][3])

    # --- speed: case law stays out of the reads about law ----------------------------------------------------------

    def test_timeline_keeps_case_law_out_unless_asked(self):
        """A million decisions in law.timeline() made every tool about law 2-3 times slower and world_on_date pass its
        120 s limit (measured 2026-11-06 with the 27 Swiss case-law corpora): case law is read only where asked for,
        each corpus by its own events, and world by one git log per corpus (latest_decision)."""
        code = ('import json, sys; sys.path.insert(0, "tools"); import law\n'
                f'c = "{CASES}"\n'
                'print(json.dumps([sorted({e.corpus for e in law.timeline()}), sorted({e.corpus for e in law.timeline(caselaw=True)}),'
                ' (law.latest_decision(c, "2017-01-01") or [])[:2], law.latest_decision(c, "2009-01-01"),'
                ' [e.law for e in law.corpus_timeline(c) if e.kind == "court"]]))\n')
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', code], cwd=self.t.root, capture_output=True,
                              encoding='utf-8', timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        law_only, both, latest, none_yet, own = json.loads(done.stdout)
        self.assertEqual(law_only, [LAW])
        self.assertEqual(both, sorted([LAW, CASES]))
        self.assertEqual(latest, ['Bundesgericht (BGE) BGE 142 II 307', '2016-06-01'])
        self.assertIsNone(none_yet)
        self.assertEqual(own, ['Bundesgericht 1C_100/2010', 'Bundesgericht (BGE) BGE 142 II 307', 'Bundesgericht 4A_123/2022'])

    def test_world_on_date_and_law_details_find_decisions_without_the_timeline(self):
        world, by_docket, by_law = self.calls(('world_on_date', {'date': '2017-01-01'}),
                                              ('law_details', {'law': '4A_123/2022'}),
                                              ('law_details', {'law': 'AS 2020 5'}))
        row = next(r for r in world['data']['corpora'] if r['corpus'] == CASES)
        self.assertEqual(row['last_change'], 'Bundesgericht (BGE) BGE 142 II 307')
        self.assertTrue(row['case_law'])
        self.assertFalse(by_docket['error'], by_docket['text'])
        self.assertIn(f'{CASES}/{D3}', by_docket['text'])
        self.assertFalse(by_law['error'], by_law['text'])
        self.assertNotIn(CASES, by_law['text'])  # a law's name is not looked for among the decisions


if __name__ == '__main__':
    unittest.main()
