"""Brazilian case law in the tree: corpora of acórdãos of the Superior Tribunal de Justiça (lexifina/brazil-stj-<section>-
caselaw, from the STJ's open-data portal under CC BY; court decisions are also outside copyright under Lei 9.610/1998,
art. 8, IV), read with the same tools as law, on a small tree built here: Brazilian law (Código Civil art. 186 in two
versions, the Código de Processo Civil art. 1.022, the Constitution art. 5 and the Lei de Drogas art. 33, with
data/versions.json naming each act's number) and a case-law corpus of the STJ's Segunda Seção (three acórdãos, a
correction, the judgment overlay and decision-index.tsv, as the files are named by class, number and document number).

  python -m unittest tests.test_caselaw_br -v

One test per feature of the feature list (as tests/test_caselaw_pl.py does for Poland), plus the Brazilian forms:
decisions by process ("REsp 1.772.086/SP", "AgInt no AREsp 2.123.456/SP"); articles by the code's short name or name or
by the law's number ("art. 186 do CC", "art. 1.022 do CPC", "art. 5º, LV, da CF", "art. 33 da Lei n. 11.343/2006",
"(CPC, art. 1.022)"); acts brazil-law does not hold and other countries' forms left alone.
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

LAW = 'brazil/national/acts'
CASES = 'brazil/stj-segunda-secao/caselaw'
MONO = 'brazil/stj-monocraticas-segunda-secao-2024-2026/caselaw'
M1 = 'decisions/2024/05/06/AREsp-2500001-200001.md'
ART = f'{LAW}/codigo-civil/art-0186.md'
MOVED = 'Também comete ato ilícito o titular de um direito que, ao exercê-lo, excede manifestamente os limites.'
D1 = 'decisions/2021/resp/REsp-1772086-100001.md'
D2 = 'decisions/2023/aresp/AREsp-2123456-100002.md'
D3 = 'decisions/2025/resp/REsp-1999999-100003.md'
VERSIONS = {'country': 'BR', 'acts': [
    {'slug': 'constituicao', 'short': 'CF/88', 'title': 'Constituição da República Federativa do Brasil de 1988', 'url': 'x', 'versions': []},
    {'slug': 'codigo-civil', 'short': 'CC', 'title': 'Código Civil (Lei nº 10.406, de 10 de janeiro de 2002)', 'url': 'x', 'versions': []},
    {'slug': 'codigo-de-processo-civil', 'short': 'CPC', 'title': 'Código de Processo Civil (Lei nº 13.105, de 16 de março de 2015)',
     'url': 'x', 'versions': []},
    {'slug': 'lei-de-drogas', 'short': 'LD', 'title': 'Lei de Drogas (Lei nº 11.343, de 23 de agosto de 2006)', 'url': 'x', 'versions': []}]}
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')


def acordao(title: str, text: str) -> str:
    return (f'---\ncourt: "Superior Tribunal de Justiça"\norgao_julgador: "3ª Turma"\nsource_url: "https://dadosabertos.web.stj.jus.br/"\n---\n\n'
            f'# {title}\n\n{text}\n')


class BrazilianCaseLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        globals()['run'] = run
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'data').mkdir()
        for p in (ROOT / 'data').glob('*-aliases.json'):
            shutil.copy(p, t.root / 'data' / p.name)
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        manifest = {'corpora': [
            {'path': LAW, 'name': 'Brazil', 'language': 'pt', 'in_force_trailer': 'In-force', 'code': 'BR'},
            {'path': CASES, 'name': 'Case law: Brazil, Superior Tribunal de Justiça, the Segunda Seção', 'language': 'pt',
             'kind': 'judgments', 'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'BR'},
            {'path': MONO, 'name': 'Case law: STJ monocratic decisions, Segunda Seção, 2024-2026', 'language': 'pt',
             'kind': 'judgments', 'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'BR'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('Lei nº 10.406, de 2002', {'codigo-civil/art-0186.md': 'Art. 186. Aquele que, por ação ou omissão voluntária, violar direito '
                                                                          'e causar dano a outrem comete ato ilícito.\n',
                                              'codigo-civil/art-0187.md': f'Art. 187. {MOVED}\n',
                                              'codigo-civil/art-0188.md': 'Art. 188. Não constituem atos ilícitos os praticados em legítima defesa.\n',
                                              'codigo-de-processo-civil/art-1022.md': 'Art. 1.022. Cabem embargos de declaração contra qualquer decisão.\n',
                                              'constituicao/art-005.md': 'Art. 5º Todos são iguais perante a lei.\n',
                                              'lei-de-drogas/art-33.md': 'Art. 33. Importar, exportar, remeter drogas.\n',
                                              'data/versions.json': json.dumps(VERSIONS, ensure_ascii=False)},
                   In_force='2016-03-18', Kind='law')
        cls.v2022 = law.commit('Lei nº 14.000, de 2022', {
            'codigo-civil/art-0186.md': 'Art. 186. Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e '
                                        'causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.\n',
            'codigo-civil/art-0187.md': 'Art. 187. (Revogado).\n',
            'codigo-civil/art-0188.md': f'Art. 188. Não constituem atos ilícitos os praticados em legítima defesa. {MOVED}\n'},
            In_force='2022-01-01', Kind='law')
        c = t.corpus(CASES)
        c.commit('STJ REsp 1.772.086', {D1: acordao('STJ, 3ª Turma, Acórdão, REsp 1.772.086, 2021-05-05',
                                                    'ACÓRDÃO\nRecurso especial não provido.\nO dano está demonstrado.')},
                 Kind='court', In_force='2021-05-05', Decided='2021-05-05', Published='2021-05-10', Court='Superior Tribunal de Justiça (3ª Turma)',
                 Docket='REsp 1.772.086', Cites=f'{ART} (art. 186 do CC)')
        c.commit('STJ REsp 1.772.086', {D1: acordao('STJ, 3ª Turma, Acórdão, REsp 1.772.086, 2021-05-05',
                                                    'ACÓRDÃO\nRecurso especial não provido.\nO dano está comprovado.')},
                 Kind='correction', In_force='2021-09-01', Corrected='2021-09-01', Docket='REsp 1.772.086')
        c.commit('STJ AgInt no AREsp 2.123.456', {D2: acordao('STJ, 4ª Turma, Acórdão, AgInt no AREsp 2.123.456, 2023-06-01',
                                                              'ACÓRDÃO\nAgravo interno não provido. Ato ilícito e dano moral.')},
                 Kind='court', In_force='2023-06-01', Decided='2023-06-01', Published='2023-06-06', Court='Superior Tribunal de Justiça (4ª Turma)',
                 Docket='AREsp 2.123.456', Title='AgInt no AREsp 2.123.456', Cites=f'{ART} (art. 186 do CC)')
        c.commit('STJ REsp 1.999.999', {D3: acordao('STJ, 3ª Turma, Acórdão, REsp 1.999.999, 2025-03-03', 'ACÓRDÃO\nRecurso provido.')},
                 Kind='court', In_force='2025-03-03', Published='2025-03-03', Court='Superior Tribunal de Justiça (3ª Turma)',
                 Docket='REsp 1.999.999', Cites=f'{ART} (art. 186 do Código Civil)')
        rows = [{'decided': '2021-05-05', 'name': 'STJ REsp 1.772.086', 'court': 'Superior Tribunal de Justiça, 3ª Turma',
                 'citation': 'REsp 1.772.086', 'url': 'https://processo.stj.jus.br/1', 'how': 'art. 186 do CC', 'mentions': 1, 'decision': D1},
                {'decided': '2023-06-01', 'name': 'STJ AgInt no AREsp 2.123.456', 'court': 'Superior Tribunal de Justiça, 4ª Turma',
                 'citation': 'AgInt no AREsp 2.123.456', 'url': 'https://processo.stj.jus.br/2', 'how': 'art. 186 do CC', 'mentions': 2,
                 'decision': D2, 'law_commit': cls.v2022},
                {'decided': '2025-03-03', 'name': 'STJ REsp 1.999.999', 'court': 'Superior Tribunal de Justiça, 3ª Turma',
                 'citation': 'REsp 1.999.999', 'url': 'https://processo.stj.jus.br/3', 'how': 'art. 186 do Código Civil', 'mentions': 1,
                 'decision': D3, 'law_commit': cls.v2022}]
        moved = {'decided': '2021-02-02', 'name': 'STJ REsp 1.772.086', 'court': 'Superior Tribunal de Justiça, 3ª Turma',
                 'citation': 'REsp 1.772.086', 'url': 'https://processo.stj.jus.br/1', 'how': 'art. 187 do CC', 'mentions': 1, 'decision': D1}
        refs = (('REsp 1.772.086', D1), ('REsp 1772086', D1), ('201802644066', D1), ('STJ 100001', D1),
                ('AREsp 2.123.456', D2), ('AgInt no AREsp 2.123.456', D2), ('STJ 100002', D2),
                ('REsp 1.999.999', D3), ('STJ 100003', D3))
        c.commit('Lexifina', {f'judgments/{LAW}/codigo-civil/art-0186.jsonl': ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows),
                              f'judgments/{LAW}/codigo-civil/art-0187.jsonl': json.dumps(moved, ensure_ascii=False) + '\n',
                              'decision-index.tsv': 'reference\tpath\n' + ''.join(f'{r}\t{p}\n' for r, p in refs),
                              'corpus.json': json.dumps({'corpus': 'br/stj-segunda-secao/caselaw', 'kind': 'judgments',
                                                         'name': 'Case law: STJ Segunda Seção', 'in_force_trailer': 'In-force'})},
                 Kind='documentation')
        # A monocratic corpus that splits its index and overlay by year (decision-index-2024.tsv, art-0186.2024.jsonl), as
        # the large ones do to keep each file under GitHub's 100 MB.
        m = t.corpus(MONO)
        m.commit('STJ AREsp 2.500.001', {M1: acordao('STJ, Decisão, AREsp 2.500.001, 2024-05-06', 'DECISÃO\nAgravo não conhecido. Dano moral.')},
                 Kind='court', In_force='2024-05-06', Published='2024-05-06', Court='Superior Tribunal de Justiça', Docket='AREsp 2.500.001')
        row = {'decided': '2024-05-06', 'name': 'STJ AREsp 2.500.001', 'court': 'Superior Tribunal de Justiça', 'citation': 'AREsp 2.500.001',
               'url': 'https://dadosabertos.web.stj.jus.br/', 'how': 'art. 186 do CC', 'mentions': 1, 'decision': M1, 'law_commit': cls.v2022}
        m.commit('Lexifina', {f'judgments/{LAW}/codigo-civil/art-0186.2024.jsonl': json.dumps(row, ensure_ascii=False) + '\n',
                              'decision-index-2024.tsv': f'reference\tpath\nAREsp 2.500.001\t{M1}\nSTJ 200001\t{M1}\n'}, Kind='documentation')
        t.pin()

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

    # --- law.py on an acórdão -----------------------------------------------------------------------------------------

    def test_law_py_reads_an_acordao(self):
        path = f'{CASES}/{D1}'
        self.assertIn('comprovado', self.cli('show', '2022-01-01', path))
        self.assertIn('demonstrado', self.cli('show', '2021-06-01', path))
        log = self.cli('log', path)
        self.assertIn('STJ REsp 1.772.086', log)
        self.assertIn('2021-09-01', log)
        blame = self.cli('blame', '2022-01-01', path)
        self.assertIn('court ruling, not a law', blame)
        self.assertIn('correction', blame)
        self.assertIn('court ruling, not a law', self.cli('words', '2022-01-01', path))
        self.assertIn('comprovado', self.cli('diff', '2021-06-01', '2022-01-01', path))
        self.assertNotIn('same', self.cli('today', '2021-06-01', path).split('\n')[0].lower())

    def test_laws_leaves_out_acordaos_unless_named(self):
        laws = self.cli('laws', '2000-01-01', '2030-01-01')
        self.assertIn('Lei nº 14.000, de 2022', laws)
        self.assertNotIn('REsp 1.999.999', laws)
        judgments = self.cli('laws', '2000-01-01', '2030-01-01', 'brazil/caselaw')
        self.assertIn('STJ REsp 1.999.999 (court decision)', judgments)
        self.assertNotIn('Lei nº 14.000, de 2022', judgments)

    def test_world_labels_the_latest_acordao(self):
        self.assertIn('STJ REsp 1.999.999 (latest decision), given 2025-03-03', self.cli('world', '2026-01-01'))

    def test_countries_adds_brazilian_case_law_only_by_name(self):
        def add(name):
            done = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py', 'add', name], cwd=self.t.root,
                                  capture_output=True, encoding='utf-8', timeout=120)
            return done.stdout + done.stderr
        brazil = add('brazil')
        self.assertIn(LAW, brazil)
        self.assertNotIn(CASES, brazil)
        self.assertIn(CASES, add('brazil/caselaw'))

    # --- the server -----------------------------------------------------------------------------------------------------

    def test_check_precedent_and_what_else_changes_read_the_overlay(self):
        prec, else_ = self.calls(('check_precedent', {'path': ART, 'date': '2026-01-01'}),
                                 ('what_else_changes', {'path': ART, 'date': '2026-01-01'}))
        self.assertFalse(prec['error'], prec['text'])
        self.assertEqual(prec['data']['judgments_recorded'], 4)  # three acórdãos, one monocratic decision (by year)
        by = {c['citation']: c for c in prec['data']['checks']}
        self.assertFalse(by['REsp 1.772.086']['same_words'])  # decided before the 2022 change
        self.assertTrue(by['REsp 1.999.999']['same_words'])
        self.assertEqual(by['AgInt no AREsp 2.123.456']['decision'], f'{CASES}/{D2}')
        self.assertFalse(else_['error'], else_['text'])
        self.assertIn('court decision(s) cite it', else_['text'])

    def test_check_precedent_finds_where_the_applied_words_went(self):
        prec = self.calls(('check_precedent', {'path': f'{LAW}/codigo-civil/art-0187.md', 'date': '2026-01-01'}))[0]
        self.assertFalse(prec['error'], prec['text'])
        check = prec['data']['checks'][0]
        self.assertFalse(check['same_words'])
        self.assertEqual([m['now_in'] for m in check['removed_words_now_elsewhere']][:1], [[f'{LAW}/codigo-civil/art-0188.md']])

    def test_an_acordao_is_read_like_a_provision(self):
        path = f'{CASES}/{D1}'
        read, cmp, who, listed, cases, hist, lj = self.calls(
            ('read_law', {'path': f'{CASES}/{D2}', 'date': '2026-01-01'}),
            ('compare_dates', {'path': path, 'date_a': '2021-06-01', 'date_b': '2022-01-01'}),
            ('who_wrote', {'path': path, 'date': '2022-01-01'}),
            ('list_provisions', {'path': f'{CASES}/decisions/2021'}),
            ('applies_to_case', {'path': path, 'commenced': '2021-01-01'}),
            ('provision_history', {'path': path}),
            ('list_jurisdictions', {}))
        for a in (read, cmp, who, listed, cases, hist, lj):
            self.assertFalse(a['error'], a['text'])
        self.assertIn('Agravo interno não provido', read['text'])
        self.assertIn('comprovado', cmp['text'])
        self.assertIn('STJ REsp 1.772.086', who['text'])
        self.assertIn('REsp 1.772.086', listed['text'])
        self.assertTrue(cases['data']['court_decision'])
        self.assertIn('court decision, not a law', cases['text'])
        self.assertIn('2021-05-05', hist['text'])
        self.assertIn('2021-09-01', hist['text'])
        self.assertIn(CASES, lj['text'])
        self.assertIn('2025-03-03', lj['text'])

    def test_lists_and_searches_leave_case_law_out_unless_asked(self):
        q = 'ilícito'
        answers = self.calls(('search_law', {'query': q, 'date': '2026-01-01'}),
                             ('search_law', {'query': q, 'date': '2026-01-01', 'kind': 'judgments'}),
                             ('search_law', {'query': q, 'date': '2026-01-01', 'jurisdiction': 'brazil/caselaw'}),
                             ('laws_between', {'start': '2000-01-01', 'end': '2030-01-01'}),
                             ('search_changes', {'query': 'STJ'}),
                             ('search_changes', {'query': 'STJ', 'jurisdiction': 'brazil/caselaw'}),
                             ('phrase_history', {'query': q}),
                             ('changes_between', {'date_a': '2017-01-01', 'date_b': '2026-01-01'}))
        for a in answers:
            self.assertFalse(a['error'], a['text'])
        law_only, judgments, named, laws, changes, changes_cl, phrase, between = answers
        self.assertIn(ART, law_only['text'])
        self.assertNotIn(CASES, law_only['text'].split('Not read')[0])
        self.assertIn(f'{CASES}/{D2}', judgments['text'])
        self.assertNotIn(ART, judgments['text'])
        self.assertIn(f'{CASES}/{D2}', named['text'])
        self.assertIn('Lei nº 14.000, de 2022', laws['text'])
        self.assertNotIn('REsp 1.999.999', laws['text'].split('Not read')[0])
        self.assertEqual(changes['data']['changes'], [])
        self.assertTrue(changes_cl['data']['changes'])
        self.assertNotIn(f'{CASES}/', phrase['text'].split('Not read')[0])
        self.assertNotIn(f'{CASES}/', between['text'].split('Not read')[0])

    def test_acordaos_by_process_and_brazilian_citations(self):
        by_docket, by_appeal, details, cites = self.calls(
            ('find_provision', {'query': 'REsp 1.999.999/SP'}),
            ('find_provision', {'query': 'AgInt no AREsp 2.123.456/SP'}),
            ('law_details', {'law': 'REsp 1.772.086'}),
            ('resolve_citations', {'text': 'Nos termos do art. 186 do CC, do art. 1.022 do CPC, do art. 5º, LV, da CF e do art. 33 da '
                                           'Lei n. 11.343/2006, e do REsp 1.772.086/SP, mas não do art. 2º da Lei 9.999/1999 nem do '
                                           '§ 823 Abs. 1 BGB.', 'date': '2026-01-01'}))
        for a in (by_docket, by_appeal, details, cites):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{CASES}/{D3}', by_docket['text'])
        self.assertIn(f'{CASES}/{D2}', by_appeal['text'])
        self.assertIn(f'{CASES}/{D1}', details['text'])
        paths = [h.get('path') for h in cites['data'].get('citations', [])]
        for want in (ART, f'{LAW}/codigo-de-processo-civil/art-1022.md', f'{LAW}/constituicao/art-005.md', f'{LAW}/lei-de-drogas/art-33.md',
                     f'{CASES}/{D1}'):
            self.assertIn(want, paths)
        self.assertFalse([p for p in paths if p and '9999' in p], paths)  # a law brazil-law does not hold

    def test_a_corpus_split_by_year(self):
        """decision-index-<year>.tsv and judgments/<law>/<article>.<year>.jsonl are read as the single files are."""
        found, prec = self.calls(('find_provision', {'query': 'AREsp 2.500.001/SP'}), ('check_precedent', {'path': ART, 'date': '2026-01-01'}))
        self.assertFalse(found['error'], found['text'])
        self.assertIn(f'{MONO}/{M1}', found['text'])
        self.assertEqual(prec['data']['judgments_recorded'], 4)
        self.assertIn('AREsp 2.500.001', [c['citation'] for c in prec['data']['checks']])

    def test_check_precedent_counts_a_large_overlay(self):
        """Above JUDGMENTS_COUNTED rows check_precedent counts the rows and reads only the latest: same answer."""
        import os
        args = json.dumps([('check_precedent', {'path': ART, 'date': '2026-01-01', 'max_results': 2})])
        runs = []
        for limit in ('20000', '0'):
            done = subprocess.run([sys.executable, '-X', 'utf8', '-c', CALL], cwd=self.t.root, input=args, capture_output=True,
                                  encoding='utf-8', timeout=300, env={**os.environ, 'GLOBAL_LAW_JUDGMENTS_COUNTED': limit})
            self.assertEqual(done.returncode, 0, done.stderr)
            runs.append(json.loads(done.stdout)[0]['data'])
        whole, counted = runs
        self.assertEqual((counted['judgments_recorded'], counted['judgments_up_to_date']), (4, 4))
        self.assertEqual([c['citation'] for c in counted['checks']], [c['citation'] for c in whole['checks']])

    def test_brazilian_citation_forms(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        m.br_corpus = lambda: (LAW, None)  # no tree: the file a citation names, by brazil-law's naming
        for text, want in (('art. 186 do CC', ['codigo-civil/art-0186.md']), ('art. 1.022 do CPC', ['codigo-de-processo-civil/art-1022.md']),
                           ('arts. 186 e 927 do Código Civil', ['codigo-civil/art-0186.md', 'codigo-civil/art-0927.md']),
                           ('art. 5º, LV, da CF', ['constituicao/art-005.md']), ('art. 105, III, a, da CF/88', ['constituicao/art-105.md']),
                           ('art. 28-A do CPP', ['codigo-de-processo-penal/art-028-a.md']), ('(CPC, art. 1.022)', ['codigo-de-processo-civil/art-1022.md']),
                           ('art. 489, § 1º, IV, do CPC/2015', ['codigo-de-processo-civil/art-0489.md']),
                           ('art. 85, §§ 2º e 11, do CPC', ['codigo-de-processo-civil/art-0085.md'])):
            got = [h['path'] for h in m.citations_in(text) if h['country'] == 'br' and h.get('path')]
            self.assertEqual(got, [f'{LAW}/{w}' for w in want], text)
        for other in ('§ 823 Abs. 1 BGB', 'art. 1240 du code civil', 'Art. 336 OR', 'artikel 6:162 BW', 'art. 415 k.c.',
                      'artículo 1902 del Código Civil', 'VI ZR 123/20'):
            self.assertFalse([h for h in m.citations_in(other) if h['country'] == 'br'], other)
        for ref in ('REsp 1.772.086/SP', 'AgInt no AREsp 2.123.456/SP', 'HC 123.456', 'EDcl no REsp 1.772.086', 'CC 123.456/SP', 'RHC 98.765'):
            self.assertTrue(m.BR_DOCKET.fullmatch(ref), ref)
        for not_ref in ('CC 186', 'art. 186 do CC'):
            self.assertFalse(m.BR_DOCKET.fullmatch(not_ref), not_ref)


if __name__ == '__main__':
    unittest.main()
