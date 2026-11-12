"""The MCP server, spoken to the way a client does: newline-delimited JSON-RPC over stdio.

  python -m unittest tests.test_mcp -v
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY_CORPORA = {'gb/uk/send': 'gb/uk/legislation'}  # the UK corpus's path before it held all UK legislation


def P(old: str) -> str:
    """A path written with the tree's old folders (us/, de/bund/grundgesetz, gb/uk/send, mt/national/malta-law), in the
    tree's naming now. The server's own mapping decides, so the tests follow every move the manifest records."""
    sys.path.insert(0, str(ROOT / 'tools'))
    sys.dont_write_bytecode = True
    import mcp_server
    return mcp_server.here(old)


def CORPUS(path: str) -> str:
    """The corpus that holds a path."""
    corpora = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))['corpora']
    return max((c['path'] for c in corpora if path == c['path'] or path.startswith(c['path'] + '/')), key=len)


USC = P('us/federal/usc/title-11/1182.md')
STAY = P('us/federal/usc/title-11/362.md')  # the automatic stay: about 40,000 characters, long enough to come in parts
GG_FOLDER = P('de/bund/grundgesetz')  # a corpus of its own, or the grundgesetz/ folder of all federal law
GG = P('de/bund/grundgesetz/artikel/{}.md')
SEND = P('gb/uk/send/uksi/2014/1530/regulation/13.md')


# Corpora the tests read. A clone holds only the countries added to it (tools/countries.py), so a test that reads one
# is skipped when it is not checked out, and says which command adds it.
US_C, DE_C, UK_C = CORPUS(USC), CORPUS(GG_FOLDER), CORPUS(SEND)
CH_C, MT_C, RO_C = 'switzerland/bund/acts', 'malta/national/acts', 'romania/national/acts'


def _checked_out(corpus: str) -> bool:
    return (ROOT / corpus / '.git').exists()


def needs(*corpora: str):
    """Skip unless these corpora are checked out."""
    missing = [c for c in corpora if not _checked_out(c)]
    return unittest.skipIf(bool(missing), f"needs {', '.join(missing)} checked out: "
                                          f"python tools/countries.py add {' '.join(missing)}")


def _corpus_paths() -> list[str]:
    return [c['path'] for c in json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))['corpora']]


def needs_any_corpus():
    """Skip unless at least one corpus is checked out (the test reads whichever there is)."""
    return unittest.skipUnless(any(_checked_out(c) for c in _corpus_paths()),
                               'needs a corpus checked out: python tools/countries.py add <country>')


def needs_every_corpus():
    """Skip unless every corpus is checked out (git clone --recurse-submodules)."""
    return unittest.skipUnless(all(_checked_out(c) for c in _corpus_paths()),
                               'needs every corpus checked out: git submodule update --init')


def out_of_date(reason: str):
    """A test written for an earlier design, kept and expected to fail until it is rewritten. If it starts to pass,
    unittest reports an unexpected success, so the mark is removed then."""
    def mark(test):
        test.out_of_date = reason
        return unittest.expectedFailure(test)
    return mark


class Server:
    def __init__(self, **env):
        self.proc = subprocess.Popen([sys.executable, str(ROOT / 'tools/mcp_server.py')], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT,
                                     env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', **env})
        self.next_id = 0

    def send(self, method: str, params: dict | None = None, notify: bool = False):
        msg = {'jsonrpc': '2.0', 'method': method, **({'params': params} if params is not None else {})}
        if not notify:
            self.next_id += 1
            msg['id'] = self.next_id
        self.proc.stdin.write((json.dumps(msg) + '\n').encode('utf-8'))
        self.proc.stdin.flush()
        if notify:
            return None
        return json.loads(self.proc.stdout.readline().decode('utf-8'))

    def call(self, name: str, **arguments):
        reply = self.send('tools/call', {'name': name, 'arguments': arguments})
        return reply['result']

    def close(self):
        self.proc.stdin.close()
        self.proc.wait(timeout=30)
        self.proc.stdout.close()
        self.proc.stderr.close()


class McpServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Server()
        cls.init = cls.s.send('initialize', {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '0'}})
        cls.s.send('notifications/initialized', notify=True)

    @classmethod
    def tearDownClass(cls):
        cls.s.close()

    def text(self, result):
        return result['content'][0]['text']

    # protocol

    def test_handshake_and_tool_list(self):
        r = self.init['result']
        self.assertEqual(r['protocolVersion'], '2025-06-18')
        self.assertIn('tools', r['capabilities'])
        self.assertIn('list_jurisdictions', r['instructions'])
        tools = {t['name']: t for t in self.s.send('tools/list')['result']['tools']}
        self.assertGreaterEqual(len(tools), 11)
        for t in tools.values():
            self.assertEqual(t['inputSchema']['type'], 'object')
            self.assertTrue(t['annotations']['readOnlyHint'])

    @needs(US_C)
    def test_modern_protocol_without_a_handshake(self):
        # MCP 2026-07-28: no initialize; each request carries its version in _meta; server/discover is required.
        meta = {'_meta': {'io.modelcontextprotocol/protocolVersion': '2026-07-28', 'io.modelcontextprotocol/clientCapabilities': {}}}
        fresh = Server()
        try:
            d = fresh.send('server/discover', meta)['result']
            self.assertEqual(d['resultType'], 'complete')
            self.assertIn('2026-07-28', d['supportedVersions'])
            self.assertIn('tools', d['capabilities'])
            self.assertEqual(d['_meta']['io.modelcontextprotocol/serverInfo']['name'], 'global-law')
            self.assertIn('ttlMs', d)
            tools = fresh.send('tools/list', meta)['result']
            self.assertEqual(tools['resultType'], 'complete')
            self.assertIn('cacheScope', tools)
            r = fresh.send('tools/call', {**meta, 'name': 'read_law', 'arguments': {'path': USC, 'date': '2022-07-01'}})['result']
            self.assertIn('7,500,000', r['structuredContent']['text'])
            bad = fresh.send('tools/list', {'_meta': {'io.modelcontextprotocol/protocolVersion': '1900-01-01'}})['error']
            self.assertEqual(bad['code'], -32022)
            self.assertEqual(bad['data']['requested'], '1900-01-01')
            self.assertIn('2026-07-28', bad['data']['supported'])
        finally:
            fresh.close()

    def test_legacy_versions_still_negotiate(self):
        fresh = Server()
        try:
            for v in ('2025-11-25', '2024-11-05'):
                self.assertEqual(fresh.send('initialize', {'protocolVersion': v, 'capabilities': {}})['result']['protocolVersion'], v)
            self.assertNotIn('resultType', fresh.send('tools/list')['result'])  # legacy replies keep the legacy shape
        finally:
            fresh.close()

    def test_unknown_method_and_tool(self):
        self.assertEqual(self.s.send('no/such')['error']['code'], -32601)
        self.assertEqual(self.s.send('tools/call', {'name': 'nope', 'arguments': {}})['error']['code'], -32602)
        self.assertEqual(self.s.send('ping')['result'], {})

    def test_bad_input_never_kills_the_server(self):
        p = self.s.proc
        p.stdin.write(b'this is not json\n')
        p.stdin.flush()
        self.assertEqual(json.loads(p.stdout.readline())['error']['code'], -32700)
        # a batch of two requests and a notification gets two answers, in one array
        batch = [{'jsonrpc': '2.0', 'id': 901, 'method': 'ping'}, {'jsonrpc': '2.0', 'method': 'notifications/x'},
                 {'jsonrpc': '2.0', 'id': 902, 'method': 'tools/list'}]
        p.stdin.write((json.dumps(batch) + '\n').encode())
        p.stdin.flush()
        replies = json.loads(p.stdout.readline())
        self.assertEqual([r['id'] for r in replies], [901, 902])
        # wrong argument types come back as tool errors, and the server keeps answering
        r = self.s.call('find_provision', query='1182', max_results='abc')
        self.assertTrue(r['isError'])
        self.assertIn('whole number', r['content'][0]['text'])
        self.assertFalse(self.s.call('laws_between', start=20220101, end='2022-12-31')['isError'])  # 8-digit dates are read
        self.assertEqual(self.s.send('ping')['result'], {})

    def test_malformed_bytes_never_kill_the_server(self):
        # Found by the independent review: each of these used to end the process.
        p = self.s.proc
        for raw, code in ((b'\xff\xfe{"jsonrpc":"2.0"}\n', -32700),       # not UTF-8
                          (b'[' * 100_000 + b'\n', -32700),                  # nested too deep
                          (b'{"jsonrpc":"2.0","id":' + b'9' * 5000 + b',"method":"ping"}\n', -32700),  # a number too long to read
                          (b'"' + b'x' * 1_100_000 + b'"\n', -32600),        # over the size limit
                          (b'{"jsonrpc":"2.0","id":null,"method":"ping"}\n', -32600),
                          (b'{"jsonrpc":"2.0","id":{"a":1},"method":"ping"}\n', -32600)):
            p.stdin.write(raw)
            p.stdin.flush()
            reply = json.loads(p.stdout.readline())
            self.assertEqual(reply['error']['code'], code, raw[:40])
            self.assertIsNone(reply['id'])
        p.stdin.write(b'{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"search_law","arguments":{"query":"\\ud800"}}}\n')
        p.stdin.flush()
        self.assertEqual(json.loads(p.stdout.readline())['id'], 7)  # a lone surrogate is answered, not fatal
        self.assertEqual(self.s.send('ping')['result'], {})

    @needs(US_C)
    def test_slow_requests_stay_bounded(self):
        # Found by the independent review: these took minutes (a quadratic citation pattern, a lookup per citation).
        import time
        started = time.monotonic()
        r = self.s.call('resolve_citations', text='11 U.S.C.' + ' ' * 49_000 + 'x')
        self.assertFalse(r['isError'])
        brief = ' '.join(f'11 U.S.C. § 1182({n})' for n in range(1, 300))
        r = self.s.call('resolve_citations', text=brief, max_results=1)['structuredContent']
        self.assertEqual({c['path'] for c in r['citations']}, {USC})  # one provision, looked up once
        r = self.s.call('search_changes', query='e', max_results=1)['structuredContent']
        self.assertLessEqual(len(r['changes']), 1)
        self.assertGreaterEqual(r['total'], len(r['changes']))
        self.assertLess(time.monotonic() - started, 60)

    @needs(US_C)
    def test_a_missing_checkout_narrows_the_answer(self):
        # A partial checkout used to end the server (law.py stops with SystemExit when a corpus is not checked out).
        import tools.mcp_server as m  # noqa: F401  (in-process: no corpus is renamed on disk)
        missing: list[str] = []
        found = m.checked_out([{'path': 'no/such/corpus'}, {'path': P('us/federal/usc')}], missing)
        self.assertEqual(missing, ['no/such/corpus'])
        self.assertEqual([c['path'] for c, _ in found], [P('us/federal/usc')])
        self.assertIn('not searched', m.not_searched(missing))

    @needs(US_C)
    def test_hostile_input_is_refused(self):
        def refused(name, **a):
            r = self.s.call(name, **a)
            self.assertTrue(r['isError'], (name, a, r))
            return r['content'][0]['text']
        # paths that reach outside the tree, into git internals or another drive
        for bad in (P('us/federal/usc/../../../README.md'), '../../etc/passwd', '/etc/passwd', 'C:/Windows/win.ini',
                    P('us/federal/usc/HEAD:title-11/1182.md'), P('us/federal/usc/title-11/1182.md\x00'), 'x' * 400):
            refused('read_law', path=bad)
        # option-looking and non-hex commits never reach git
        for bad in ('--output=/tmp/x', 'HEAD~1', '-n1', '0035acae58 --stat'):
            self.assertIn('hexadecimal', refused('law_details', commit=bad))
        # regular expressions that could take exponential time, and over-long queries
        self.assertIn('repeats a group', refused('phrase_history', query='(a+)+$', regex=True))
        self.assertIn('repeats a group', refused('search_law', query='(\\w*)*x', regex=True))
        for bad in ('Asyl|((.|.)*QQZ)', '(\\w|\\w)*Q', '((a+))+b', '(a)\\1'):
            refused('phrase_history', query=bad, regex=True)
        # pathspec wildcards would make git walk every file; folders are not law text
        refused('provision_history', path=P('us/federal/usc/*'))
        # (read_law reads a folder since 2026-11-10: its provisions in order; a folder that holds none is refused)
        self.assertIn('not a provision file', refused('read_law', path=P('us/federal/usc/title-11/no-such-folder')))
        # arguments the schema does not name, and values of the wrong shape
        self.assertEqual(self.s.send('tools/call', {'name': 'read_law', 'arguments': {'path': USC, 'pth': 'x'}})['error']['code'], -32602)
        refused('who_wrote', path=USC, granularity=5)
        self.assertIn('whole number', refused('laws_between', start='2022-01-01', end='2022-12-31', max_results=float('inf')))  # 1e400 in JSON
        refused('search_law', query='a' * 301)
        refused('find_provision', query={'not': 'text'})
        # option-looking queries are searched for as text, not run as options
        r = self.s.call('search_law', query='--recurse-submodules', date='2022-05-01')
        self.assertFalse(r['isError'])
        # nothing was written into the tree
        status = subprocess.run(['git', 'status', '--porcelain', '--ignore-submodules=none'], cwd=ROOT, capture_output=True, encoding='utf-8').stdout
        self.assertNotIn('__pycache__', status)

    @needs(DE_C, US_C)
    def test_what_else_changes(self):
        r = self.s.call('what_else_changes', path=USC, date='2022-07-01')['structuredContent']
        by_kind = {(g['kind'], g['term']): g for g in r['groups']}
        cites = by_kind[('cites this provision', None)]
        self.assertIn(P('us/federal/usc/title-11/103.md'), [p['path'] for p in cites['provisions']])
        dip = by_kind[('uses a term this provision defines', 'debtor in possession')]
        uses = [g for g in r['groups'] if g['term'] == 'debtor in possession' and g['kind'].startswith('uses')]
        self.assertGreaterEqual(sum(g['count'] for g in uses), 10)  # those nearer §1101 are listed apart
        self.assertNotIn(USC, [p['path'] for p in dip['provisions']])  # never itself
        gg = self.s.call('what_else_changes', path=GG.format('079'), date='2022-07-01')['structuredContent']
        self.assertIn(GG.format('023'), [p['path'] for g in gg['groups'] for p in g['provisions']])
        stay = self.s.call('what_else_changes', path=P('us/federal/usc/title-11/362.md'))['structuredContent']
        self.assertGreaterEqual(stay['groups'][0]['count'], 10)

    @needs(DE_C, US_C)
    def test_check_precedent(self):
        # A decision in July 2022 applied the $7.5 million text; the 2024 sunset changed the words since.
        later = self.s.call('check_precedent', path=USC, decided='2022-07-01', date='2026-10-28', case_name='In re Example')['structuredContent']
        c = later['checks'][0]
        self.assertFalse(c['same_words'])
        self.assertEqual([l['in_force'] for l in c['laws_since']], ['2024-06-21'])
        self.assertIn('7,500,000', c['changes'])
        # A 1995 decision on Art. 16a applied the words still in force in 2016.
        same = self.s.call('check_precedent', path=GG.format('016a'), decided='1995-01-01', date='2016-01-01')['structuredContent']['checks'][0]
        self.assertTrue(same['same_words'])
        # No decision date: §1182's recorded judgments are checked one by one.
        recorded = self.s.call('check_precedent', path=USC)['structuredContent']
        self.assertEqual(recorded['judgments_recorded'], 4)
        self.assertEqual(len(recorded['checks']), 4)
        # No decision date and no recorded judgments: says what to give.
        none = self.s.call('check_precedent', path=GG.format('016a'))
        self.assertFalse(none['isError'])
        self.assertEqual(none['structuredContent']['judgments_recorded'], 0)
        self.assertIn('decided', none['structuredContent']['summary'])

    @needs(US_C)
    def test_scoped_definition_and_nearer_definitions(self):
        # §1182 defines "debtor in possession" "In this subchapter"; §1101 defines it for chapter 11, so §1103 is
        # nearer §1101 and is listed apart, while §1184 in subchapter V stays with §1182.
        r = self.s.call('what_else_changes', path=USC)['structuredContent']
        self.assertEqual(r['definition_scope'], 'In this subchapter')
        relies = [p['path'] for g in r['groups'] if g['kind'] == 'uses a term this provision defines' for p in g['provisions']]
        nearer = {p['path']: p['nearest_definition'] for g in r['groups'] if g['kind'].startswith('uses the term, but nearer') for p in g['provisions']}
        self.assertIn(P('us/federal/usc/title-11/1184.md'), relies)
        self.assertEqual(nearer.get(P('us/federal/usc/title-11/1103.md')), P('us/federal/usc/title-11/1101.md'))

    @needs(US_C)
    def test_case_commenced_before_the_record(self):
        # A case filed in 2004: the US record starts with the 2017 edition, which is not a change, and says nothing
        # of 2004 (BAPCPA 2005 is outside it). The answer names the gap instead of reading as complete.
        import json
        r = self.s.call('applies_to_case', path=P('us/federal/usc/title-11/362.md'), commenced='2004-06-01')['structuredContent']
        self.assertTrue(r['periods'][0].get('not_in_record'))
        self.assertIn('Gap: the record starts on 2018-01-12', ' '.join(r['explanation']))
        self.assertNotIn('2017 edition', ' '.join(c['law'] for c in r['changes']))
        self.assertLess(len(json.dumps(r)), len(json.dumps(r['text'])) + 10000)  # one copy of the text; period texts only when asked for
        self.assertNotIn('text', r['periods'][-1])

    @needs(US_C)
    def test_broad_search_is_capped(self):
        r = self.s.call('search_law', query='the', jurisdiction=P('us/federal/usc'))['structuredContent']
        self.assertLessEqual(len(r['provisions']), 200)
        self.assertGreater(r['provision_count'], 200)

    @needs(DE_C, US_C)
    def test_report_fixes(self):
        # A mistyped path is an error, not "no difference".
        self.assertTrue(self.s.call('compare_dates', path=GG.format('115').replace('artikel/', 'art-'), date_a='2000-01-01', date_b='2020-01-01')['isError'])
        # All the words of a heading outrank one of them.
        top = self.s.call('find_provision', query='automatic stay')['structuredContent']['results'][0]
        self.assertTrue(top['path'].endswith('title-11/362.md'), top)
        # A commit of this tree stands for the corpus commit it moved to.
        world = self.s.call('laws_between', start='2022-06-21', end='2022-06-21', jurisdiction=P('us/federal/usc'))['structuredContent']['changes'][0]['world_commit']
        self.assertIn('117-151', self.s.call('law_details', commit=world[:10])['structuredContent']['changes'][0]['law'])

    def test_malta_acts_by_citation(self):
        # Only where the tree holds Malta's statute book.
        names = [c['path'] for c in self.s.call('list_jurisdictions')['structuredContent'].get('corpora', [])]
        if not any(n.endswith('malta-law') for n in names):
            self.skipTest('no Malta corpus in this tree')
        r = self.s.call('find_provision', query='Cap. 387')['structuredContent']['results'][0]
        self.assertTrue(r['path'].endswith('cap/387/title.md') and 'Arbitration' in r['heading'])
        # Page furniture does not count as change: L.N. 235 of 2026 changed few provisions' words, not 39.
        diffs = self.s.call('law_details', law='L.N. 235 of 2026')['structuredContent']['changes'][0]['diffs']
        changed = [d['path'] for d in diffs if d['effect'] == 'words changed']
        self.assertTrue(any(p.endswith('sl/586.8/15.md') for p in changed))
        self.assertLess(len(changed), 8)

    @needs(US_C)
    def test_law_details_says_what_each_provision_did(self):
        # One call shows what a law did to each provision's words; no compare_dates per provision.
        r = self.s.call('law_details', law='Pub. L. 117-151', corpus=P('us/federal/usc'))['structuredContent']['changes']
        rows = [d for c in r for d in c.get('diffs', [])]
        usc = [d for d in rows if d['path'] == USC]
        self.assertTrue(usc and usc[0]['effect'] == 'words changed' and '7,500,000' in ' '.join(d['diff'] for d in usc))
        self.assertIn("What each provision's words did", self.text(self.s.call('law_details', law='Pub. L. 117-151', corpus=P('us/federal/usc'))))
        bare = self.s.call('law_details', law='Pub. L. 117-151', corpus=P('us/federal/usc'), include_diffs=False)['structuredContent']['changes']
        self.assertNotIn('diffs', bare[0])

    @needs(US_C)
    def test_folders_of_acts(self):
        # The start of a folder name lists the folders it begins (every instrument under a Chapter, every US title),
        # one row each with a title, a file count and the last change.
        r = self.s.call('list_provisions', path=P('us/federal/usc') + '/title-1')['structuredContent']
        self.assertIn('count', r)
        rows = self.s.call('list_provisions', path=P('us/federal/usc') + '/title-')['structuredContent']['folders']
        t11 = next(f for f in rows if f['folder'].endswith('/title-11'))
        self.assertGreater(t11['files'], 100)
        self.assertTrue(t11['last_change']['in_force'] >= '2024-06-21')
        flat = self.s.call('list_provisions', path=P('us/federal/usc') + '/title-11', max_results=3)['structuredContent']
        self.assertEqual(len(flat['provisions']), 3)  # a folder of files still lists files
        self.assertEqual(flat['folder']['first']['kind'], 'baseline')  # and says, as a whole, where it starts and last changed
        self.assertGreaterEqual(flat['folder']['last_change']['in_force'], '2024-06-21')

    @needs(US_C)
    def test_scope_within_a_corpus(self):
        # A jurisdiction can name a folder inside a corpus (a title, a Chapter); it used to match nothing.
        t11 = P('us/federal/usc/title-11')
        r = self.s.call('changes_between', date_a='2022-05-01', date_b='2022-07-01', jurisdiction=t11)['structuredContent']
        self.assertIn(USC, [p['path'] for c in r['corpora'] for p in c['provisions']])
        self.assertTrue(all(p['path'].startswith(t11 + '/') for c in r['corpora'] for p in c['provisions']))
        laws = self.s.call('laws_between', start='2022-01-01', end='2022-12-31', jurisdiction=t11)['structuredContent']['changes']
        self.assertTrue(any('117-151' in l['law'] for l in laws))
        none = self.s.call('changes_between', date_a='2022-05-01', date_b='2022-07-01', jurisdiction=P('us/federal/usc/title-39'))
        self.assertNotIn(USC, str(none['structuredContent']))
        ph = self.s.call('phrase_history', query='7,500,000', jurisdiction=t11)['structuredContent']['changes']
        self.assertTrue(ph and all(c['path'].startswith(t11 + '/') for c in ph))

    @needs(US_C)
    def test_before_a_baseline_is_outside_the_record(self):
        # §101 enters the US record with the 2017 edition: before it, the record is silent, the law was not.
        r = self.s.call('read_law', path=P('us/federal/usc/title-11/101.md'), date='2010-01-01')['structuredContent']
        self.assertIn('where this record starts, not the day it came into force', r['why'])
        # The fields say so too: unknown, not "not in force" (issue #17).
        self.assertIsNone(r['in_force'])
        self.assertFalse(r['in_record'])
        self.assertTrue(r['record_starts'] > '2010-01-01')
        c = self.s.call('resolve_citations', text='11 U.S.C. § 101', date='2010-01-01')['structuredContent']['citations'][0]
        self.assertTrue(c['status'].startswith('before the record starts'))
        today = self.s.call('read_law', path=P('us/federal/usc/title-11/1101.md'), include_text=False)['structuredContent']
        if today['last_change']['kind'] == 'baseline':
            self.assertIn('First version in the record', today['summary'])

    def test_floor_of_one_act_is_unknown_not_repealed(self):
        # China's 公司法 enters the record with the 2018 text, the earliest full text 中国人大网 serves; it has been in
        # force since 1994. Before 2018 the answer is "unknown", in the fields as in the text (issue #17). An article
        # added by the 2023 revision is still "not yet in force" in 2020: it starts with a law, not a baseline.
        if not (ROOT / 'china/national/acts/.git').exists():
            self.skipTest('China is not checked out')
        before = self.s.call('read_law', path='china/national/acts/gongsifa/art-001.md', date='2015-01-01',
                             include_text=False)['structuredContent']
        self.assertIsNone(before['in_force'])
        self.assertFalse(before['in_record'])
        self.assertEqual(before['record_starts'], '2018-10-26')
        after = self.s.call('read_law', path='china/national/acts/gongsifa/art-001.md', date='2020-01-01',
                            include_text=False)['structuredContent']
        self.assertTrue(after['in_force'])
        self.assertTrue(after['in_record'])
        new = self.s.call('read_law', path='china/national/acts/gongsifa/art-219.md', date='2020-01-01',
                          include_text=False)['structuredContent']
        self.assertIs(new['in_force'], False)
        self.assertTrue(new['in_record'])

    def test_floor_at_a_revision_is_unknown_not_not_yet_in_force(self):
        # 标准化法 enters the record with its 2017 revision (Kind: Law（修订）); it has been in force since 1989. Before
        # 2018 the answer is "unknown", not "not yet in force" (issue #17); before its 1988 adoption, data/acts.json
        # says it was not yet in force.
        if not (ROOT / 'china/national/acts/.git').exists():
            self.skipTest('China is not checked out')
        p = 'china/national/acts/biaozhunhuafa/art-001.md'
        before = self.s.call('read_law', path=p, date='2015-01-01', include_text=False)['structuredContent']
        self.assertIsNone(before['in_force'])
        self.assertFalse(before['in_record'])
        self.assertEqual(before['record_starts'], '2018-01-01')
        self.assertIn('a revision of an act already in force then', before['why'])
        after = self.s.call('read_law', path=p, date='2018-01-01', include_text=False)['structuredContent']
        self.assertTrue(after['in_force'])
        early = self.s.call('read_law', path=p, date='1980-01-01', include_text=False)['structuredContent']
        if 'adopted only on' in early['why']:  # data/acts.json with adopted days (china-law e681287)
            self.assertIs(early['in_force'], False)

    @needs(US_C)
    def test_restored_words_and_latest_wording(self):
        # On 2022-05-01 §1182(1) held the 2019 words again: the CARES Act's temporary change had ended. They are the
        # 2019 Act's words, brought back by the CARES Act, and they are the words at the end of the record too.
        runs = self.s.call('who_wrote', path=USC, date='2022-05-01', include_runs=True)['structuredContent']['runs']
        back = [r for r in runs if 'small business debtor' in r['text']][0]
        self.assertIn('116-54', back['law'])
        self.assertIn('116-136', back['restored_by'])
        self.assertEqual(back['restored_on'], '2022-03-27')
        lines = self.s.call('who_wrote', path=USC, date='2022-05-01', granularity='line')['structuredContent']['lines']
        line = [l for l in lines if 'small business debtor' in l['text']][0]
        self.assertEqual(('116-54' in line['law'], '116-136' in line['restored_by']), (True, True))
        self.assertEqual(self.s.call('who_wrote', path=USC, date='2022-05-01', granularity='line')['structuredContent']['latest']['state'], 'same')
        self.assertIn('what_else_changes', ' '.join(self.s.call('search_law', query='1182', jurisdiction='us')['structuredContent']['hints']))
        # A case filed in May 2022: Pub. L. 117-151 covers it from its start, so the first period is not settled.
        first = self.s.call('applies_to_case', path=USC, commenced='2022-05-01')['structuredContent']['periods'][0]
        self.assertIn('117-151', first['reached_back_over_by'][0])
        self.assertEqual(self.s.call('read_law', path=USC, date='2022-05-01')['structuredContent']['latest']['state'], 'same')
        # The $7.5 million text of July 2022 ended in 2024.
        self.assertEqual(self.s.call('read_law', path=USC, date='2022-07-01', include_text=False)['structuredContent']['latest']['state'], 'different')

    @needs(US_C)
    def test_metadata_only_read(self):
        r = self.s.call('read_law', path=USC, date='2022-07-01', include_text=False)['structuredContent']
        self.assertNotIn('text', r)
        self.assertIn('117-151', r['last_change']['law'])
        self.assertNotIn('7,500,000', r['summary'])

    @needs(US_C)
    def test_audit_log_is_opt_in_and_holds_no_arguments(self):
        import tempfile
        folder = tempfile.mkdtemp()
        fresh = Server(GLOBAL_LAW_AUDIT_DIR=folder)
        try:
            fresh.call('read_law', path=USC, date='2022-07-01')
            fresh.call('read_law', path='../x')
        finally:
            fresh.close()
        lines = [json.loads(l) for l in (Path(folder) / 'global-law-mcp.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual([(l['tool'], l['status']) for l in lines], [('read_law', 'ok'), ('read_law', 'error')])
        self.assertNotIn('1182', json.dumps([{k: v for k, v in l.items() if k != 'args_hmac'} for l in lines]))  # a keyed hash of the arguments, never the arguments
        self.assertTrue(all(len(l['args_hmac']) == 64 for l in lines))

    @needs(DE_C, UK_C, US_C)
    def test_resolve_citations_in_a_brief(self):
        brief = ('The debtor relies on 11 U.S.C. § 1182(1) and 11 USC 362(a). Under Art. 16a Abs. 1 GG the position differs. '
                 "The authority's duty under s. 42(2) of the Children and Families Act 2014 and reg. 13 SEND Regulations 2014 "
                 'is absolute; see also 11 U.S.C. § 9999.')
        r = self.s.call('resolve_citations', text=brief, date='2022-07-01')['structuredContent']['citations']
        got = {c['path']: c['status'] for c in r}
        self.assertEqual(got[USC], 'in force')
        self.assertEqual(got[P('us/federal/usc/title-11/362.md')], 'in force')
        self.assertEqual(got[GG.format('016a')], 'in force')
        self.assertEqual(got[P('gb/uk/send/ukpga/2014/6/section/42.md')], 'in force')
        self.assertEqual(got[SEND], 'in force')
        self.assertEqual(got[P('us/federal/usc/title-11/9999.md')], 'not in the record at any date')
        self.assertEqual([c['path'] for c in r][0], USC)  # in the order they appear
        self.assertTrue(self.s.call('resolve_citations', text='x' * 50_001)['isError'])

    @needs(UK_C)
    def test_judgments_recorded_for_a_provision(self):
        r = self.s.call('check_precedent', path=P('gb/uk/send/ukpga/2014/6/section/42.md'), date='2026-10-28')['structuredContent']
        self.assertGreaterEqual(r['judgments_recorded'], 5)
        names = {c.get('citation'): c for c in r['checks']}
        self.assertTrue(names['[2026] EWCA Civ 20']['same_words'])
        # The 2021 change left the words alone, so a 2020 decision is on the same words, with that change named.
        drexler = names['[2020] EWCA Civ 502']
        self.assertTrue(drexler['same_words'])
        self.assertTrue(any('1399' in l['law'] for l in drexler['laws_since']))

    @needs_any_corpus()
    def test_long_lists_are_cut_and_say_so(self):
        r = self.s.call('laws_between', start='1949-01-01', end='2026-12-31', max_results=5)['structuredContent']
        self.assertEqual(len(r['changes']), 5)
        self.assertTrue(r['truncated'])
        self.assertGreater(r['total'], 5)

    def test_internal_errors_do_not_leak_details(self):
        # an argument of the wrong shape deep inside a tool: the answer names the error type, not paths or values
        r = self.s.call('list_provisions', path=P('us/federal/usc'), max_results=[1])
        self.assertTrue(r['isError'])
        self.assertNotIn('C:\\', r['content'][0]['text'])

    def test_resources(self):
        names = [r['uri'] for r in self.s.send('resources/list')['result']['resources']]
        self.assertIn('global-law://README.md', names)
        body = self.s.send('resources/read', {'uri': 'global-law://manifest.json'})['result']['contents'][0]['text']
        self.assertIn(P('us/federal/usc'), body)

    # the questions

    @needs(DE_C, US_C)
    def test_old_iso_paths_still_work(self):
        # The top folders were ISO codes (us/, de/); paths and scopes written that way are still read.
        r = self.s.call('read_law', path='us/federal/usc/title-11/1182.md', date='2022-07-01', include_text=False)
        self.assertFalse(r['isError'])
        self.assertEqual(r['structuredContent']['corpus'], P('us/federal/usc'))
        art = self.s.call('find_provision', query='16a', jurisdiction='de/bund/grundgesetz')['structuredContent']['results']
        self.assertEqual(art[0]['path'], GG.format('016a'))

    @needs(DE_C, UK_C, US_C)
    def test_list_jurisdictions(self):
        r = self.s.call('list_jurisdictions')
        paths = {c['path'] for c in r['structuredContent']['corpora']}
        self.assertTrue({CORPUS(GG_FOLDER), CORPUS(SEND), P('us/federal/usc')} <= paths, paths)  # more corpora may join
        for c in r['structuredContent']['corpora']:
            self.assertTrue(c['example_path'].endswith('.md'), c)

    @needs(DE_C, MT_C, UK_C, US_C)
    def test_find_provision_by_number_and_words(self):
        # A bare number exists in several bodies of law (Malta's Civil Code has an art. 1182 too): scoped, it is exact.
        hits = self.s.call('find_provision', query='1182', jurisdiction='us')['structuredContent']['results']
        self.assertEqual(hits[0]['path'], USC)
        anywhere = self.s.call('find_provision', query='1182', max_results=100)['structuredContent']['results']
        self.assertIn(USC, [h['path'] for h in anywhere])
        art = self.s.call('find_provision', query='Art. 16a')['structuredContent']['results']
        self.assertEqual(art[0]['path'], GG.format('016a'))
        reg = self.s.call('find_provision', query='reg 13', jurisdiction='gb')['structuredContent']['results']
        self.assertEqual(reg[0]['path'], SEND)
        words = self.s.call('find_provision', query='Timescales EHC plans')['structuredContent']['results']
        self.assertEqual(words[0]['path'], SEND)
        # Grundgesetz headings are only numbers, so a topic is found in the text.
        asyl = self.s.call('find_provision', query='Asylrecht', jurisdiction='de')['structuredContent']['results']
        self.assertIn(GG.format('016a'), [h['path'] for h in asyl][:3])
        self.assertTrue(self.s.call('find_provision', query='')['isError'])

    @needs(UK_C, US_C)
    def test_every_answer_cites_the_publishers_page(self):
        # The provision itself, as in force on the date, where the publisher's URLs follow the layout (the UK).
        r = self.s.call('read_law', path=SEND, date='2020-06-01', include_text=False)['structuredContent']['cite']
        self.assertEqual(r['official_url'], 'https://www.legislation.gov.uk/uksi/2014/1530/regulation/13/2020-06-01')
        self.assertIn('Special Educational Needs and Disability Regulations 2014', r['pincite'])
        r = self.s.call('read_law', path=USC, date='2022-07-01', include_text=False)['structuredContent']['cite']
        self.assertTrue(r['official_url'].startswith('https://www.govinfo.gov/link/uscode/11/1182'))
        self.assertIn('PLAW-117publ151', r['law_url'])
        for c in (r,):
            self.assertNotIn('lexifina', json.dumps(c).lower())  # never this tree or its reader

    @needs(UK_C)
    def test_maintainer_written_versions_are_law(self):
        # The UK corpus writes its texts as Lexifina, with an In-force day: they are versions, not documentation.
        hist = self.s.call('provision_history', path=P('gb/uk/send/ukpga/2014/6/section/42.md'))['structuredContent']['changes']
        self.assertTrue(hist)
        self.assertNotIn('Lexifina', [h['law'] for h in hist])

    @needs(US_C)
    def test_read_law_across_the_2022_gap(self):
        may = self.s.call('read_law', path=USC, date='2022-05-01')
        july = self.s.call('read_law', path=USC, date='2022-07-01')
        self.assertNotIn('7,500,000', may['structuredContent']['text'])
        self.assertIn('7,500,000', july['structuredContent']['text'])
        self.assertIn('117-151', july['structuredContent']['last_change']['law'])
        self.assertIn('117-151', may['structuredContent']['next_change']['law'])

    @needs(DE_C, US_C)
    def test_read_law_flags_a_later_law_that_reaches_back(self):
        # In the 2022 gap the words read "small business debtor", but Pub. L. 117-151 later reached back to
        # cases commenced on or after 2020-03-27.
        gap = self.s.call('read_law', path=USC, date='2022-05-01')
        self.assertTrue(any('117-151' in b and 'reaches back' in b for b in gap['structuredContent']['beyond_the_words']))
        self.assertIn('Not the whole answer', self.text(gap))
        settled = self.s.call('read_law', path=GG.format('001'), date='2000-01-01')['structuredContent']
        self.assertEqual(settled['beyond_the_words'], [])

    @needs(US_C)
    def test_applies_to_case_looks_ahead(self):
        # Read on the day the case was filed, in the gap: Pub. L. 117-151 is later, but reaches back to it.
        r = self.s.call('applies_to_case', path=USC, commenced='2022-05-01', date='2022-05-01')
        ahead = r['structuredContent']['later_changes_reaching_back']
        self.assertEqual([a['in_force'] for a in ahead][:1], ['2022-06-21'])
        self.assertIn('7,500,000', ahead[0]['changes_to_the_text'])  # what the reach-back changes, in the answer itself
        self.assertIn('{+', self.text(r))
        early = self.s.call('applies_to_case', path=USC, commenced='2020-01-15', date='2020-01-15')['structuredContent']
        self.assertFalse(any('117-151' in a['law'] for a in early['later_changes_reaching_back']))

    @needs(US_C)
    def test_applies_to_case_gives_the_case_its_periods(self):
        # Read today, a case filed in the 2022 gap had three periods: the gap text, the $7.5 million text by the
        # reach-back of Pub. L. 117-151, and the text after its sunset, whose reach to pending cases is not recorded.
        r = self.s.call('applies_to_case', path=USC, commenced='2022-05-01', date='2026-10-28')['structuredContent']
        spans = [(p['from'], p['until'], (p['by'] or '')[:15]) for p in r['periods']]
        # The 2024 sunset records no reach to pending cases: it is listed as its own period, marked uncertain, with the
        # default rule named but not applied. The text the record settles for the case is the $7.5 million text.
        self.assertEqual(spans, [('2022-05-01', '2022-06-21', ''), ('2022-06-21', '2024-06-21', 'Pub. L. 117-151'),
                                 ('2024-06-21', None, 'Pub. L. 117-151')])
        self.assertTrue(r['periods'][1]['certain'])
        self.assertFalse(r['periods'][2]['certain'])
        self.assertIn('7,500,000', r['text'])
        self.assertIn('Not decided by this data', ' '.join(r['explanation']))
        self.assertIn('Landgraf', ' '.join(r['explanation']))

    @needs(DE_C)
    def test_search_knows_popular_names(self):
        r = self.s.call('search_law', query='Ewigkeitsklausel')['structuredContent']
        self.assertEqual(r['popular_name_for'], [GG.format('079')])

    @needs(DE_C, UK_C, US_C)
    def test_citation_forms(self):
        first = lambda q, **a: [h['path'] for h in self.s.call('find_provision', query=q, **a)['structuredContent']['results']][:1]
        self.assertEqual(first('11 U.S.C. § 1101'), [P('us/federal/usc/title-11/1101.md')])  # the title narrows it
        self.assertEqual(first('17 USC 107'), [P('us/federal/usc/title-17/107.md')])
        self.assertEqual(first('1101', jurisdiction=P('us/federal/usc/title-11')), [P('us/federal/usc/title-11/1101.md')])
        self.assertEqual(first('Art. 16a GG'), [GG.format('016a')])  # "GG" is a scoped name in aliases.json
        self.assertEqual(first('s. 42 CFA'), [P('gb/uk/send/ukpga/2014/6/section/42.md')])
        self.assertEqual(first('reg 13 SEND Regulations'), [SEND])

    @needs(DE_C, UK_C, US_C)
    def test_popular_names(self):
        debt = self.s.call('find_provision', query='Schuldenbremse')['structuredContent']['results']
        self.assertEqual({h['path'] for h in debt[:3]}, {GG.format('109'), GG.format('115'), GG.format('143d')})
        ehc = self.s.call('find_provision', query='EHC plan')['structuredContent']['results']
        self.assertIn(SEND, [h['path'] for h in ehc[:3]])
        stay = self.s.call('find_provision', query='automatic stay', jurisdiction='us')['structuredContent']['results']
        self.assertEqual(stay[0]['path'], P('us/federal/usc/title-11/362.md'))

    @needs(DE_C, US_C)
    def test_read_law_says_why_there_is_no_text(self):
        before = self.s.call('read_law', path=GG.format('091e'), date='2010-07-26')
        self.assertFalse(before['structuredContent']['in_force'])
        self.assertIn('first appears on 2010-07-27', self.text(before))
        typo = self.s.call('read_law', path=P('us/federal/usc/title-11/1183x.md'), date='2022-07-01')
        self.assertIn('not in this record at any date', self.text(typo))
        bad = self.s.call('read_law', path=USC, date='2022-5-1')
        self.assertTrue(bad['isError'])
        self.assertIn('Not a date', self.text(bad))
        outside = self.s.call('read_law', path='fr/code-civil/1.md')
        self.assertTrue(outside['isError'])

    @needs_any_corpus()
    def test_read_law_warns_past_the_end_of_a_record(self):
        # Pick a corpus whose record ends before the date, whichever it is when the test runs.
        corpora = self.s.call('list_jurisdictions')['structuredContent']['corpora']
        ending = min((c for c in corpora if c.get('complete_to')), key=lambda c: c['complete_to'])
        if ending['complete_to'] >= '2026-10-28':
            self.skipTest('every record is complete to today')
        late = f"{int(ending['complete_to'][:4]) + 1}-06-01"
        r = self.s.call('read_law', path=ending['example_path'], date=late)
        self.assertTrue(any('runs to' in c for c in r['structuredContent']['caveats']), r)
        self.assertIn('Note:', self.text(r))

    @needs(DE_C, US_C)
    def test_world_on_date(self):
        r = self.s.call('world_on_date', date='2016-01-01')['structuredContent']
        by = {c['corpus']: c for c in r['corpora']}
        if CORPUS(GG_FOLDER) == GG_FOLDER:
            self.assertIn('60.', by[GG_FOLDER]['last_change'])  # in force 1 January 2015
        else:
            self.assertTrue(by[CORPUS(GG_FOLDER)]['last_change'])  # all federal law: some law changed before 2016
        self.assertIsNone(by[P('us/federal/usc')]['last_change'])  # the US record starts in 2018
        mid = {c['corpus']: c for c in self.s.call('world_on_date', date='2022-05-01')['structuredContent']['corpora']}
        self.assertIn('117-151', mid[P('us/federal/usc')]['next_change'])
        early = self.s.call('world_on_date', date='1990-10-03')['structuredContent']
        self.assertIsNone({c['corpus']: c for c in early['corpora']}[P('us/federal/usc')]['last_change'])

    @needs(DE_C, US_C)
    def test_who_wrote_by_word_and_line(self):
        words = self.s.call('who_wrote', path=USC, date='2022-07-01', include_runs=True)['structuredContent']
        restored = ''.join(r['text'] for r in words['runs'] if '117-151' in r['law'])
        self.assertIn('7,500,000', restored)
        self.assertTrue(any('116-54' in l['law'] for l in words['laws']))
        lines = self.s.call('who_wrote', path=GG.format('091e'), date='2017-07-20', granularity='line')['structuredContent']
        self.assertTrue(all('58.' in l['law'] for l in lines['lines']))

    @needs(US_C)
    def test_compare_dates(self):
        r = self.s.call('compare_dates', path=USC, date_a='2022-07-01', date_b='2022-05-01')['structuredContent']
        self.assertEqual((r['date_a'], r['date_b']), ('2022-05-01', '2022-07-01'))
        self.assertIn('{+', r['word_diff'])
        self.assertEqual([c['in_force'] for c in r['changes']], ['2022-06-21'])

    @needs(US_C)
    def test_provision_history(self):
        r = self.s.call('provision_history', path=USC)['structuredContent']['changes']
        self.assertEqual([c['in_force'] for c in r], sorted(c['in_force'] for c in r))
        self.assertTrue(any(c['in_force'] == '2020-03-27' and '116-136' in c['law'] for c in r))

    @needs(DE_C, UK_C, US_C)
    def test_each_change_says_what_it_did(self):
        # Without this a model took the 2022 and 2024 sunsets of §1182(1) for republications.
        what = lambda path: {c['in_force']: c['what'] for c in self.s.call('provision_history', path=path)['structuredContent']['changes']}
        us = what(USC)
        self.assertIn('Temporary change ended', us['2024-06-21'])
        self.assertIn('Rewritten', us['2022-06-21'])
        self.assertNotIn('and 2 more', us['2022-03-27'])  # the line about this provision, not the commit subject
        self.assertIn('temporarily amended', what(SEND)['2020-05-01'])
        self.assertIn('Art. 87a', what(GG.format('087a'))['2022-07-01'])

    @needs(DE_C, MT_C, UK_C)
    def test_laws_between(self):
        # Dates in either order; asked per jurisdiction, since a large corpus (Malta) can fill a whole window's list.
        def window(j):
            return self.s.call('laws_between', start='2014-12-31', end='2012-01-01', jurisdiction=j)['structuredContent']['changes']
        self.assertTrue(any(c['corpus'] == CORPUS(GG_FOLDER) for c in window('de')))
        self.assertTrue(any(c['corpus'] == P('gb/uk/send') for c in window(P('gb/uk/send'))))
        self.assertEqual(window('us'), [])  # the US record starts in 2018
        de = self.s.call('laws_between', start='1990-01-01', end='1990-12-31', jurisdiction=GG_FOLDER)['structuredContent']['changes']
        self.assertTrue(any('36.' in c['law'] for c in de))
        us = self.s.call('laws_between', start='2018-01-01', end='2026-12-31', jurisdiction='us')['structuredContent']
        self.assertGreater(us['provisions_per_law']['Pub. L. 116-54 (Small Business Reorganization Act of 2019)'], 20)

    @needs(DE_C, US_C)
    def test_search_law_on_a_date(self):
        r = self.s.call('search_law', query='coronavirus', date='2022-05-01')['structuredContent']
        self.assertTrue(any(p.startswith(P('us/federal/usc/')) for p in r['provisions']))
        self.assertFalse(any(p.endswith(('README.md', 'REPRODUCE.md')) for p in r['provisions']))
        before = self.s.call('search_law', query='coronavirus', jurisdiction='us', date='2019-01-01')['structuredContent']
        self.assertEqual(before['provisions'], [])
        # Not in the text, but in the change notes: the search says so and names the changes.
        notes = self.s.call('search_law', query='Bankruptcy Threshold Adjustment', date='2023-01-01')
        self.assertEqual(notes['structuredContent']['provisions'], [])
        self.assertTrue(notes['structuredContent']['related_changes'])
        self.assertIn('change note', self.text(notes))
        de = self.s.call('search_law', query='Asylrecht', jurisdiction='de', date='2000-01-01')['structuredContent']
        self.assertIn(GG.format('016a'), de['provisions'])
        # The Code writes "COVID–19" with an en dash; a plain hyphen must still find it, and regex characters are literal.
        dash = self.s.call('search_law', query='COVID-19', date='2022-05-01')['structuredContent']
        self.assertTrue(dash['provisions'])
        self.assertEqual(self.s.call('search_law', query='(B)', jurisdiction='us', date='2022-05-01', max_results=1)['isError'], False)

    @needs(DE_C, US_C)
    def test_phrase_history(self):
        r = self.s.call('phrase_history', query='7,500,000', jurisdiction='us')['structuredContent']['changes']
        seen = [(c['in_force'], c['effect']) for c in r if c['path'] == USC]
        self.assertEqual(seen, [('2020-03-27', 'added'), ('2022-03-27', 'removed'), ('2022-06-21', 'added'), ('2024-06-21', 'removed')])
        covid = self.s.call('phrase_history', query='COVID', jurisdiction=GG_FOLDER)['structuredContent']['changes']
        self.assertEqual([(c['path'], c['effect']) for c in covid][:1], [(GG.format('143h'), 'added')])
        # Words already in the 2017 edition, where the US record starts, entered the law before it.
        sbd = self.s.call('phrase_history', query='small business debtor', jurisdiction='us')['structuredContent']
        first = [c for c in sbd['changes'] if c['path'] == P('us/federal/usc/title-11/101.md')][0]
        self.assertEqual((first['in_force'], first['effect']), ('2018-01-12', 'present_at_start'))
        self.assertIn('before the record begins', ' '.join(sbd['notes']))

    @needs(US_C)
    def test_changes_between(self):
        r = self.s.call('changes_between', date_a='2022-05-01', date_b='2022-07-01')['structuredContent']
        us = next(c for c in r['corpora'] if c['corpus'] == P('us/federal/usc'))
        self.assertIn(USC, [p['path'] for p in us['provisions']])
        self.assertTrue(any('117-151' in l for l in us['laws']))

    @needs(US_C)
    def test_law_details(self):
        short = self.s.call('law_details', law='Pub. L. 116-54', max_message_chars=500)
        self.assertIn('more characters', self.text(short))
        r = self.s.call('law_details', law='Pub. L. 117-151')['structuredContent']['changes']
        self.assertTrue(r)
        first = r[-1]
        self.assertEqual(first['corpus'], P('us/federal/usc'))
        self.assertIn('In-force', first['trailers'])
        self.assertTrue(any(p.endswith('1182.md') for c in r for p in c['provisions']))
        gg = self.s.call('law_details', law='36. Änderung', corpus='de')['structuredContent']['changes']
        self.assertTrue(gg and gg[0]['trailers'].get('In-Kraft') == '1990-09-29')
        self.assertTrue(self.s.call('law_details', law='Pub. L. 1-1')['isError'])

    @needs(DE_C, US_C)
    def test_list_provisions(self):
        r = self.s.call('list_provisions', path=P('us/federal/usc/title-11'), date='2022-07-01')['structuredContent']
        self.assertIn(USC, [p['path'] for p in r['provisions']])
        gg = self.s.call('list_provisions', path=P('de/bund/grundgesetz'), date='1960-01-01')['structuredContent']
        paths = [p['path'] for p in gg['provisions']]
        self.assertIn(GG.format('001'), paths)
        self.assertNotIn(GG.format('012a'), paths)  # not until 1968
        self.assertTrue(self.s.call('list_provisions', path='fr')['isError'])

    @needs(DE_C)
    def test_search_changes(self):
        r = self.s.call('search_changes', query='temporary')['structuredContent']['changes']
        self.assertTrue(r)
        self.assertEqual([c['in_force'] for c in r], sorted(c['in_force'] for c in r))
        de = self.s.call('search_changes', query='Abstimmung', jurisdiction=GG_FOLDER, start='1990-01-01', end='1990-12-31')['structuredContent']['changes']
        self.assertTrue(all(c['corpus'] == CORPUS(GG_FOLDER) and c['in_force'].startswith('1990') for c in de))

    @needs_any_corpus()
    def test_missing_after_the_record_ends_says_so(self):
        corpora = self.s.call('list_jurisdictions')['structuredContent']['corpora']
        ending = min((c for c in corpora if c['record_to']), key=lambda c: c['record_to'])
        missing = ending['example_path'].rsplit('/', 1)[0] + '/no-such-provision.md'
        r = self.s.call('read_law', path=missing, date=f"{int(ending['record_to'][:4]) + 1}-06-01")
        self.assertIn('may exist in the law after that date', self.text(r))

    @needs(UK_C, US_C)
    def test_read_law_gives_sources_to_cite(self):
        r = self.s.call('read_law', path=USC, date='2022-07-01')['structuredContent']
        self.assertTrue(any('govinfo.gov' in s for s in r['sources']), r['sources'])
        h = self.s.call('provision_history', path=SEND)['structuredContent']['changes']
        self.assertTrue(any('legislation.gov.uk' in s for c in h for s in c['sources']))

    @needs(US_C)
    def test_applies_to_case(self):
        r = self.s.call('applies_to_case', path=USC, commenced='2022-05-01', date='2022-07-01')['structuredContent']
        later = [c for c in r['changes'] if c['in_force'] > '2022-05-01']
        self.assertEqual([c['in_force'] for c in later], ['2022-06-21'])
        self.assertIn('7,500,000', r['text'])  # no recorded scope excludes it, so the July text applies
        self.assertTrue(any('March 27, 2020' in s for s in later[0]['scope']), later[0]['scope'])  # the scope in words
        self.assertFalse(any('http' in s for s in later[0]['scope']))
        self.assertTrue(later[0]['verdict'].startswith('applies'))
        # Filed before 27 March 2020: neither the CARES text nor Pub. L. 117-151's reaches the case.
        old = self.s.call('applies_to_case', path=USC, commenced='2020-01-15', date='2022-07-01')['structuredContent']
        verdicts = {c['law'][:15]: c['verdict'] for c in old['changes'] if c['in_force'] > '2020-01-15'}
        self.assertTrue(verdicts['Pub. L. 117-151'].startswith('does not apply'), verdicts)
        self.assertNotIn('7,500,000', old['text'])
        early = self.s.call('applies_to_case', path=USC, commenced='2023-01-01', date='2023-01-01')
        self.assertIn('No change took effect after the case was commenced', self.text(early))
        self.assertTrue(self.s.call('applies_to_case', path=USC, commenced='2024-01-01', date='2023-01-01')['isError'])

    def test_many_requests_in_one_session_stay_fast(self):
        import time
        start = time.time()
        for date in ('2018-06-01', '2019-06-01', '2020-06-01', '2021-06-01', '2022-06-01', '2023-06-01'):
            self.s.call('read_law', path=USC, date=date)
        self.assertLess(time.time() - start, 30)  # six reads; generous so a busy machine does not fail it


class ScopeRules(unittest.TestCase):
    """The applicability rules on their own, with the record's own trailer format (no corpus has it yet)."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    BODY = ('Pub. L. 117-151\n\n'
            'Applies: 11 U.S.C. §1182(1) | commenced-on-or-after 2022-06-21 | set-by Pub. L. 117-151, §2(h)(1)\n'
            'Applies: 11 U.S.C. §1182(1) | commenced-on-or-after 2020-03-27; commenced-before 2022-06-21; pending-on 2022-06-21 | set-by Pub. L. 117-151, §2(h)(2)\n')

    def test_parse(self):
        groups = self.m.applies_groups(self.BODY)
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[1]['conditions'][2], ('pending-on', '2022-06-21'))
        self.assertEqual(groups[0]['set_by'], 'Pub. L. 117-151, §2(h)(1)')

    def test_cases_on_each_side_of_the_gap(self):
        groups = self.m.applies_groups(self.BODY)
        def reaches(day):
            return [ok for ok, _ in (self.m.group_holds(g['conditions'], day) for g in groups)]
        self.assertEqual(reaches('2022-07-01'), [True, False])   # filed after the Act
        self.assertEqual(reaches('2022-05-01'), [False, True])   # filed in the gap, if still pending
        self.assertEqual(reaches('2020-01-01'), [False, False])  # filed before 27 March 2020
        _, assumed = self.m.group_holds(groups[1]['conditions'], '2022-05-01')
        self.assertIn('still pending on 2022-06-21', assumed[0])

    def test_citation_patterns_per_layout(self):
        import re
        cases = [('title-11/1182.md', 'subchapter V ... (as defined in section 1182) elects', 'section 11820 of this title'),
                 ('artikel/079.md', 'Artikel 79 Abs. 2 und 3', 'Artikel 790'),
                 ('bv/art-010a.md', 'nach Art. 10a Abs. 2', 'Art. 10'),
                 ('235.1/art-010a.md', 'nach Art. 10a Abs. 2', 'Art. 10'),
                 ('ukpga/2014/6/section/37.md', 'under section 37(1)', 'section 370')]
        for rel, hit, miss in cases:
            folder, pattern = self.m.citation_pattern(rel)
            self.assertTrue(re.search(pattern, hit, re.I), (rel, hit))
            self.assertFalse(re.search(pattern, miss, re.I), (rel, miss))
        self.assertEqual(self.m.defined_terms('(2) The term "debtor in possession" means the debtor; "court" means'), ['debtor in possession'])

    def test_swiss_acts_move_to_sr_numbers(self):
        # Three Swiss acts were their own folders (bv/, dsg/, schkg/); the full SR holds them under SR numbers.
        real = self.m._folders
        try:
            self.m._folders = lambda _head: (frozenset({'switzerland'}), {'ch/bund/acts': 'switzerland/bund/acts'},
                                             {'ch': 'switzerland'})
            self.assertEqual(self.m.here('ch/bund/swiss-law/bv/art-008.md'), 'switzerland/bund/acts/101/art-008.md')
            self.assertEqual(self.m.here('switzerland/bund/swiss-law/schkg'), 'switzerland/bund/acts/281.1')
            self.assertEqual(self.m.here('ch/bund/swiss-law/dsg/art-010a.md'), 'switzerland/bund/acts/235.1/art-010a.md')
            # While the three-act corpus is still in the tree, its paths stay as they are.
            self.m._folders = lambda _head: (frozenset({'switzerland'}), {'ch/bund/swiss-law': 'switzerland/bund/swiss-law'},
                                             {'ch': 'switzerland'})
            self.assertEqual(self.m.here('ch/bund/swiss-law/bv/art-008.md'), 'switzerland/bund/swiss-law/bv/art-008.md')
        finally:
            self.m._folders = real

    def test_regex_memory_bombs_are_refused(self):
        # POSIX ERE compiles {m,n} into n copies of the automaton, per git grep thread: .{1,32000}x took git past
        # 8 GB in 15 s. These shapes are refused before git sees them; ordinary patterns still pass.
        for bad in ('.{1,32000}x', 'a{1,32767}', '[a-z]{0,255}[a-z]{0,255}[a-z]{0,255}[a-z]{0,255}', '(a?){30}a{30}',
                    '(.?){200}', '(a?)?(a?)?', 'a{20}b{20}c{1}', 'a+b+c+d+e+f+g+h+i+j+k+', '.{,32000}', '[{]{1000}',
                    'a**', '(a|ab)*', '(x|)*', '(^|a)+', '([ab]|c)*', '(A|a)+',
                    'x{1, 1000}',  # Python reads it as text, git refuses it
                    # A backslash in a bracket is a literal to git: [x\] is the class and {1,32000} counts it. A
                    # separate pass that read \] as an escape let these through (audit row 51).
                    r'[x\]{1,32000}]', r'[\]{99}]', r'[[:alpha:]\]{1,99}]', r'[^\]{21}', 'x{}', '{2}a'):
            with self.assertRaises(self.m.UserError, msg=bad):
                self.m.safe_regex(bad)
        for good in ('7,500,000', 'COVID-?19', r'Art\. ?16a', 'debtor[s]? in possession', '[0-9]{4}', r'\{literal\}', 'x{2,5}y',
                     'a+b+c+d+e+', '(a|b)*', '((ab))+', r'(\.[0-9.]+)?', '[[:space:]]+x', '[]a]+', r'\(? ?12 ?\)?'):
            self.assertEqual(self.m.safe_regex(good), good)

    def test_declared_citation_rules_pass_the_regex_check(self):
        # Six corpora's own rules were refused by a count of operators (at most 4) and by checks that read \( and
        # [^...] as groups; each is linear (simple repetitions, unrepeated alternations) and finds real citations.
        import json
        import re
        rules = {c['path']: c['citation'] for c in json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))['corpora']
                 if isinstance(c.get('citation'), dict)}
        real = {'canada/federal/acts': ('ristmas recess, as defined in section 12 of the Federal Courts Rules', 'section 120'),
                'canada/northwest-territories/acts': ('provided under subsection 12(2) and a certified copy', 'section 12.5'),
                'canada/newfoundland-and-labrador/acts': ('notwithstanding paragraph 12(i), means the minister', 'ss. 112'),
                'azerbaijan/national/acts': ('Qanunu ilə 12-ci maddənin', '112-ci maddənin'),
                'georgia/national/acts': ('ამ კანონის მე-12 მუხლის პირველი პუნქტისა', 'მე-112 მუხლის'),
                'saudi-arabia/national/acts': ('على الفقرة (2) من المادة (12) من نظام', 'المادة (112)')}
        for corpus, (hit, miss) in real.items():
            if corpus not in rules:
                continue
            pattern = self.m.safe_regex(rules[corpus]['cites'].replace('{n}', '12'))
            rx = re.compile(pattern.replace('[[:space:]]', r'\s').replace('[[:alnum:]]', r'\w'), re.I)
            self.assertTrue(rx.search(hit), (corpus, hit))
            self.assertFalse(rx.search(miss), (corpus, miss))
        # China and Japan write the number in words; their rules (a description and a lookahead until audit row 55)
        # are usable, and find the citations in the laws' own words (Criminal Law art. 267; Civil Code art. 91).
        from unittest import mock
        real = {'china/national/acts': ('xingfa/art-263.md', '携带凶器抢夺的，依照本法第二百六十三条的规定定罪处罚。',
                                        '依照本法第二百六十三条之一的规定'),
                'japan/national/acts': ('minpo/art-090.md', '第九十条の規定により無効とされた', '第九十条の二')}
        for corpus, (rel, hit, miss) in real.items():
            if corpus not in rules:
                continue
            with mock.patch.object(self.m.law, 'manifest', lambda: {'corpora': [{'path': corpus, 'citation': rules[corpus]}]}):
                folder, pattern = self.m.citation_pattern(rel, corpus)
                check = self.m.citation_line_check(corpus, rel)
            self.assertEqual(folder, rel.split('/')[0])
            self.assertTrue(re.search(pattern, hit) and check.search(hit), (corpus, hit))
            self.assertFalse(check.search(miss), (corpus, miss))

    def test_unusable_declared_rule_is_not_replaced(self):
        # Audit row 55: a declared rule the server refuses was replaced by the built-in Swiss "Art. N" rule, and
        # what_else_changes said nothing cites China's Criminal Law art. 263. It is refused, with the reason.
        from unittest import mock
        old = {'file': '([a-z]+)/art-0*([0-9]+)(?:-([0-9]+))?\\.md', 'cites': '第{n}条 (art-NNN-K.md: 第{n}条之{k})',
               'numerals': 'zh-Hans: {n} is written in Chinese numerals'}
        for rule in (old, {**old, 'cites': '第{n}(?![のノ][一二三四五六七八九十])', 'numerals': 'ja'}, {**old, 'numerals': 'roman'}):
            with mock.patch.object(self.m.law, 'manifest', lambda: {'corpora': [{'path': 'cn/national/acts', 'citation': rule}]}):
                with self.assertRaises(self.m.UnusableCitationRule, msg=rule['cites']):
                    self.m.citation_pattern('xingfa/art-263.md', 'cn/national/acts')
        self.assertEqual(self.m.citation_pattern('xingfa/art-263.md')[1], r'(Art\.|Artikel) ?263([^0-9a-z]|$)')  # no rule: built-in

    def test_numbers_in_words(self):
        zh = {10: '十', 16: '十六', 20: '二十', 103: '一百零三', 110: '一百一十', 263: '二百六十三', 1000: '一千',
              1001: '一千零一', 1010: '一千零一十', 1100: '一千一百', 1260: '一千二百六十'}
        ja = {1: '一', 10: '十', 16: '十六', 100: '百', 103: '百三', 110: '百十', 123: '百二十三', 1000: '千', 1050: '千五十',
              2111: '二千百十一'}
        self.assertEqual({n: self.m.cjk_number(n, 'zh') for n in zh}, zh)
        self.assertEqual({n: self.m.cjk_number(n, 'ja') for n in ja}, ja)
        self.assertEqual(self.m.cjk_article('263-1', 'zh'), '二百六十三条之一')
        self.assertEqual(self.m.cjk_article('16-2-3', 'ja'), '十六条の二の三')
        self.assertIsNone(self.m.cjk_number(10000, 'zh'))

    def test_czech_citations_need_the_number_and_the_year(self):
        # czechia-law's rule matched 262/1996 Sb. for 262/2006 Sb., and searched only the act's own year folder.
        import re
        from unittest import mock
        rule = {'file': r'(sb)/(?P<year>[0-9]{4})/(?P<n>[0-9a-z]+)\.md', 'cites': r'(^|[^0-9]){n}/{year} Sb\.'}
        entry = {'corpora': [{'path': 'czechia/national/acts', 'citation': rule}]}
        with mock.patch.object(self.m.law, 'manifest', lambda: entry):
            folder, pattern = self.m.citation_pattern('sb/2006/262.md', 'czechia/national/acts')
        self.assertEqual(folder, 'sb')
        rx = re.compile(pattern, re.I)
        self.assertTrue(rx.search('podle § 5 zákona č. 262/2006 Sb., zákoník práce'))
        self.assertTrue(rx.search('262/2006 Sb.'))
        for miss in ('Vyhláška č. 262/1996 Sb., kterou se mění', 'zákona č. 1262/2006 Sb.', 'č. 262/2006 Sb'):
            self.assertFalse(rx.search(miss), miss)

    def test_results_fit(self):
        import json
        big = self.m.fit_result({'summary': 'x', 'provisions': [f'path/{i:05d}.md' for i in range(20000)], 'n': 1})
        self.assertLess(len(json.dumps(big)), self.m.MAX_RESULT)
        self.assertIn('of 20000 shown', big['cut']['provisions'])
        small = {'summary': 'x', 'provisions': ['a', 'b']}
        self.assertEqual(self.m.fit_result(dict(small)), small)

    def test_malta_citation_forms(self):
        cite = lambda text: [to(m) for rx, to in self.m.CITATION_FORMS for m in rx.finditer(text)]
        # The folder Malta's corpus sits in comes from the manifest (mt/national/malta-law, later malta/national/acts).
        self.assertTrue(cite('under article 11 of Cap. 586')[0].endswith('/cap/586/11.md'))
        self.assertTrue(cite('reg. 15 of S.L. 586.08')[0].endswith('/sl/586.8/15.md'))
        self.assertTrue(self.m.malta_folder(self.m.MALTA_ACT.search('the Arbitration Act (Cap. 387)')).endswith('/cap/387'))
        self.assertIsNone(self.m.MALTA_ACT.search('a chapter 11 case'))  # US chapters are not Maltese Chapters

    def test_australian_instrument_citation_forms(self):
        cite = lambda text: [to(m) for rx, to in self.m.CITATION_FORMS for m in rx.finditer(text)]
        # The Corporations Regulations 2001 number regulations chapter.part.number. The folder the
        # instruments corpus sits in comes from the manifest, as Malta's does.
        for text in ('see reg 6.10.01 of the Corporations Regulations 2001', 'r 6.10.01', 'reg. 6.10.01'):
            self.assertTrue(cite(text)[0].endswith('/corpus/corporations-regulations-2001/r-6.10.01.md'), text)
        self.assertTrue(cite('regulation 7.1.04(2) applies')[0].endswith('/r-7.1.04.md'))
        self.assertTrue(cite('reg 1.0.02AA')[0].endswith('/r-1.0.02AA.md'))  # the corpus's files sit under corpus/, letters kept
        # A plain number is not resolvable to one instrument, so it is left alone rather than guessed,
        # and a regulation of a named foreign instrument still goes to that instrument.
        self.assertEqual(cite('under reg 15'), [])
        self.assertTrue(all('corporations-regulations' not in c
                            for c in cite('reg. 15 of the SEND Regulations 2014')))
        # Two-part numbers belong to other instruments (EU, UK): only chapter.part.number is theirs.
        for text in ('regulation 2.1 of the EU Regulation', 'reg 3.4 applies', 'r. 12.5', 'reg 6.10.01.5'):
            self.assertTrue(all('corporations-regulations' not in c for c in cite(text)), text)

    def test_mexican_citation_forms(self):
        cite = lambda text: [p for rx, to in self.m.CITATION_FORMS for m in rx.finditer(text)
                             for p in ([to(m)] if isinstance(to(m), str) else to(m))]
        # The article, any apartado, fracción or párrafo, then the act by its abbreviation or title; or the act
        # first; or "constitucional". The folder Mexico's corpus sits in comes from the manifest, as Malta's does.
        self.assertTrue(cite('artículo 123, apartado A, fracción XI, de la CPEUM')[0].endswith('/constitucion/art-123.md'))
        self.assertTrue(cite('el art. 94 constitucional')[0].endswith('/constitucion/art-094.md'))
        self.assertTrue(cite('el artículo 4o. de la Constitución Política de los Estados Unidos Mexicanos')[0].endswith('/constitucion/art-004.md'))
        self.assertTrue(cite('artículo 46 Bis de la LFTSE')[0].endswith(
            '/ley-federal-de-los-trabajadores-al-servicio-del-estado/art-046-bis.md'))
        self.assertTrue(cite('artículo 29-A Bis del Código Fiscal de la Federación')[0].endswith(
            '/codigo-fiscal-de-la-federacion/art-029-a-bis.md'))
        self.assertTrue(cite('artículo 15 A de la Ley del Seguro Social')[0].endswith('/ley-del-seguro-social/art-015-a.md'))
        # A list gives every article in it, in its order.
        self.assertEqual([p.rsplit('/', 1)[1] for p in cite('artículos 103 y 107 constitucionales')], ['art-103.md', 'art-107.md'])
        self.assertEqual([p.rsplit('/', 1)[1] for p in cite('artículos 46, 46 Bis y 47 de la LFTSE')],
                         ['art-046.md', 'art-046-bis.md', 'art-047.md'])
        # Codes of more than 999 articles pad to four digits (art-0048.md); the record's own file names decide, so
        # this is checked only where the corpus is checked out.
        corpus = self.m.mexico_corpus()
        if corpus and (ROOT / corpus / '.git').exists():
            self.assertTrue(cite('LFT, art. 48')[0].endswith('/ley-federal-del-trabajo/art-0048.md'))
        # No act named, or a constitution not named as Mexico's: left alone rather than guessed.
        self.assertEqual(cite('el artículo 48 establece'), [])
        self.assertFalse([p for p in cite('artículo 24 de la Constitución') if p.startswith('mexico/')])  # Spain's, if anyone's
        self.assertFalse([p for p in cite('artículo 31.3 de la Ley Orgánica 4/2000') if p.startswith('mexico/')])
        # Mexico's Código Penal Federal is not Spain's Código Penal.
        self.assertFalse([p for p in cite('artículo 7 del Código Penal Federal') if p.startswith('spain/')])
        # An act named first does not take an article that names its own act.
        self.assertEqual([p.rsplit('/', 2)[1] for p in cite('artículo 48 de la LFT, artículo 50 del CFF')],
                         ['ley-federal-del-trabajo', 'codigo-fiscal-de-la-federacion'])
        # find_provision reads the same forms: a list of articles is a list of paths, not one (audit row 66).
        self.assertEqual(self.m.as_paths('a/b.md'), ['a/b.md'])
        if corpus and (ROOT / corpus / '.git').exists():
            for q in ('artículo 48 de la LFT', 'LFT, art. 48', 'artículos 103 y 107 constitucionales'):
                found = self.m.cited_provisions(q, '')
                self.assertTrue(found and all(p.startswith(corpus + '/') for p, *_ in found), q)
            self.assertEqual(len(self.m.cited_provisions('artículos 103 y 107 constitucionales', '')), 2)

    def test_page_furniture_is_not_law(self):
        # Malta's consolidations come from print: running heads, page numbers, hyphens at line ends and a symbol
        # font's private-use spaces move whenever a page break does. None of them is a word of the law.
        old = 'DATA PROTECTION [S.L.586.08\n(g) the authority, body, agency or per-\nson making it;  16\n12\n# 20. Fines.'
        new = '(g) the authority, body, agency or person making it;\n# 20. Fines.\nCAP. 586]  17'
        self.assertEqual(self.m.law_tokens(old)[2:], self.m.law_tokens(new))
        self.assertNotIn('12', self.m.law_tokens('(1) A rule.\n12\n(2) Another.'))
        self.assertIn('12.', self.m.law_tokens('12. Interpretation.'))  # numbering keeps its dot

    def test_scope_sentences_in_words(self):
        f = self.m.conditions_from_words
        self.assertEqual(f('Applies to any case that is commenced under title 11 on or after March 27, 2020.'),
                         [('commenced-on-or-after', '2020-03-27')])
        self.assertEqual(f('Applies to any case commenced before, on, or after March 27, 2020.'), [('any-commencement', '')])
        self.assertEqual(f('Applies to any case under title 11 commenced on or after October 1, 2026.'),
                         [('commenced-on-or-after', '2026-10-01')])
        self.assertIsNone(f('Applies only to small business debtors that elect subchapter V.'))

    def test_modifies_effects_are_read(self):
        # The proposed trailer for "same words, different law", parsed from a commit body the way modifies_in does.
        line = 'Modifies: title-11/101.md#(51D) | amount-adjusted | 2025-04-01.. | "$3,024,725" becomes "$3,424,000" | set-by 90 F.R. 8941'
        parts = [p.strip() for p in line[len('Modifies: '):].split('|')]
        self.assertEqual(parts[1], 'amount-adjusted')
        self.assertEqual(parts[2].partition('..')[0], '2025-04-01')

    def test_a_repeal_ends_the_text_for_the_case(self):
        # Spain's RD 557/2011 art. 124 (global-law #8): history() ends the file on the act's repeal day (an `ends` row,
        # from data/acts.json). applies_to_case says so, rather than listing the repeal as a change with no scope.
        from unittest import mock
        path = 'es/national/acts/rd/2011/7703/a124.md'
        hist = [{'commit': 'a', 'law': 'RD 557/2011', 'in_force': '2011-06-30', 'kind': 'law', 'order': 0},
                {'commit': 'b', 'law': 'RD 629/2022', 'in_force': '2022-08-16', 'kind': 'law', 'order': 1},
                {'commit': 'c', 'law': 'disposición derogatoria única del RD 1155/2024', 'in_force': '2025-05-20',
                 'kind': 'law', 'order': 2.5, 'blob': None, 'ends': 'repealed', 'act': 'rd/2011/7703'}]
        texts = {'2024-03-01': 'text of 2022', '2022-08-16': 'text of 2022'}
        with mock.patch.object(self.m, 'path_arg', lambda v: v), \
                mock.patch.object(self.m, 'history_of', lambda _p: [dict(h) for h in hist]), \
                mock.patch.object(self.m, 'commit_body', lambda _c, _s: ''), \
                mock.patch.object(self.m, 'default_reach', lambda _c: None), \
                mock.patch.object(self.m.law, 'corpus_of', lambda v: ('es/national/acts', v.split('acts/', 1)[1])), \
                mock.patch.object(self.m.law, 'text_on', lambda d, _p: texts.get(d) if d < '2025-05-20' else None), \
                mock.patch.object(self.m.law, 'diff_between', lambda *a: ''):
            said, r = self.m.t_applies_to_case({'path': path, 'commenced': '2024-03-01', 'date': '2026-10-31'})
            self.assertIn(f'Ended: {path} was repealed on 2025-05-20 by disposición derogatoria única del RD 1155/2024',
                          said)
            self.assertIn('it does not apply to cases commenced on or after that day', said)
            self.assertNotIn('no recorded scope', said)
            self.assertNotIn('record no reach to cases already pending', said)
            self.assertEqual(r['periods'][-1]['ends'], 'repealed')
            self.assertIsNone(r['periods'][-1]['text_as_of'])
            self.assertIn('2025-05-20: no text: repealed on 2025-05-20', said)
            self.assertEqual((r['text_date'], r['text']), ('2024-03-01', 'text of 2022'))  # the text before the end
            # A case commenced after the repeal: the provision does not apply to it at all.
            said, r = self.m.t_applies_to_case({'path': path, 'commenced': '2025-06-01', 'date': '2026-10-31'})
            self.assertIn('Not in force when the case was commenced', said)
            self.assertIn('does not apply to a case commenced on 2025-06-01', said)
            self.assertNotIn('the text in force on the commencement date applies', said)
            self.assertEqual(r['text'], '')

    def test_any_commencement_and_unknown_conditions(self):
        self.assertEqual(self.m.group_holds([('any-commencement', '')], '1999-01-01'), (True, []))
        ok, assumed = self.m.group_holds([('subset', 'small business')], '2022-01-01')
        self.assertTrue(ok)
        self.assertIn('cannot check', assumed[0])


class Launching(unittest.TestCase):
    """Every client's project config starts the server from any folder of the clone, on any platform."""

    CONFIGS = ('.mcp.json', '.cursor/mcp.json', '.vscode/mcp.json', '.codex/config.toml')

    def entry(self, config: str) -> dict:
        text = (ROOT / config).read_text(encoding='utf-8')
        if config.endswith('.toml'):  # flat enough to read without tomllib (Python 3.11+)
            values = dict(re.findall(r'^(\w+) = (.+)$', text, re.M))
            return {k: json.loads(v) for k, v in values.items()}
        data = json.loads(text)
        return (data.get('mcpServers') or data['servers'])['global-law']

    def test_every_project_config_starts_the_server(self):
        for config in self.CONFIGS:
            with self.subTest(config=config):
                entry = self.entry(config)
                # The clients' own variables: Claude Code's ${CLAUDE_PROJECT_DIR:-.}, Cursor's and VS Code's ${workspaceFolder}.
                expand = lambda s: re.sub(r'\$\{(?:CLAUDE_PROJECT_DIR:-\.|workspaceFolder)\}', str(ROOT).replace('\\', '/'), s)  # noqa: E731
                proc = subprocess.run([expand(entry['command']), *map(expand, entry['args'])], cwd=ROOT / 'tests',
                                      input=b'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n',
                                      capture_output=True, timeout=120)
                reply = json.loads(proc.stdout.decode('utf-8').splitlines()[0])
                self.assertEqual(reply['result']['serverInfo']['name'], 'global-law', proc.stderr[-300:])

    def test_claude_code_approves_the_server(self):
        settings = json.loads((ROOT / '.claude/settings.json').read_text(encoding='utf-8'))
        self.assertIn('global-law', settings['enabledMcpjsonServers'])
        self.assertIn('mcp__global-law', settings['permissions']['allow'])  # every tool is read-only

    def test_launcher_keeps_lf_line_ends(self):
        self.assertIn('*.sh text eol=lf', (ROOT / '.gitattributes').read_text(encoding='utf-8'))
        self.assertNotIn(b'\r', (ROOT / 'tools/mcp.sh').read_bytes())


class Warming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def test_git_never_reads_the_servers_stdin(self):
        # stdin carries the client's messages; on Windows a child inheriting it also waits on the main thread's read.
        from unittest import mock
        with mock.patch.object(self.m.subprocess, 'Popen') as popen:
            popen.return_value.__enter__.return_value.communicate.return_value = (b'', b'')
            self.m.git_run(['git', 'rev-parse', 'HEAD'], capture_output=True)
            self.m.git_run(['git', 'cat-file', '--batch'], input=b'', capture_output=True)
        self.assertIs(popen.call_args_list[0].kwargs['stdin'], subprocess.DEVNULL)
        self.assertIs(popen.call_args_list[1].kwargs['stdin'], subprocess.PIPE)  # input= gets a pipe of its own

    def test_warming_lists_every_corpus(self):
        self.m.warm()
        corpora = [c['path'] for c in self.m.law.manifest()['corpora'] if (ROOT / c['path'] / '.git').exists()]
        cached = self.m.names_of.cache_info().misses
        for corpus in corpora:
            self.m.names_of(corpus, self.m.corpus_head(corpus))
        self.assertEqual(self.m.names_of.cache_info().misses, cached)  # every one was already read


class Limits(unittest.TestCase):
    """Long answers come in parts, no call outlives its time in git or in the server's own work, and the server keeps
    answering while a call runs: a ping is answered, and a cancelled call stops and gets no answer."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server
        cls.server = Server()

    @classmethod
    def tearDownClass(cls):
        cls.server.close()

    def parts(self, tool: str, field: str, **args) -> tuple[str, list[dict]]:
        """Every part of a paged answer, read the way a model would: each part's next_offset asks for the next."""
        whole, places, offset = '', [], 0
        while offset is not None:
            r = self.server.call(tool, max_chars=5000, offset=offset, **args)
            self.assertFalse(r['isError'], r['content'][0]['text'])
            whole += r['structuredContent'][field]
            places.append(r['structuredContent'][f'{field}_part' if field != 'text' else 'text_part'])
            offset = places[-1]['next_offset']
        return whole, places

    @needs(US_C)
    def test_read_law_comes_in_parts_that_join_up(self):
        full = self.server.call('read_law', path=STAY, date='2026-01-01')['structuredContent']['text']
        joined, places = self.parts('read_law', 'text', path=STAY, date='2026-01-01')
        self.assertGreater(len(places), 1)
        self.assertEqual(joined, full)
        self.assertTrue(all(p['chars'] == len(full) for p in places))
        r = self.server.call('read_law', path=STAY, date='2026-01-01', max_chars=1000)
        self.assertIn('call again with offset=', r['content'][0]['text'])
        r = self.server.call('read_law', path=STAY, date='2026-01-01', offset=len(full) + 10)
        self.assertTrue(r['isError'])

    @needs(US_C)
    def test_compare_dates_comes_in_parts(self):
        full = self.server.call('compare_dates', path=STAY, date_a='2018-01-01', date_b='2026-01-01',
                                max_chars=self.m.PAGE_MOST)['structuredContent']['word_diff']
        if len(full) <= 5000:
            self.skipTest('the diff is short')
        joined, places = self.parts('compare_dates', 'word_diff', path=STAY, date_a='2018-01-01', date_b='2026-01-01')
        self.assertEqual(joined, full)

    @needs(US_C)
    def test_parts_are_never_tiny_and_end_between_words(self):
        r = self.server.call('read_law', path=STAY, date='2026-01-01', max_chars=0)  # a slip, not 1-character parts
        self.assertGreaterEqual(r['structuredContent']['text_part']['next_offset'], 500)
        text = '[1]' + ' '.join(['word'] * 600) + '[2]' + ' '.join(['more'] * 600)  # marked text, no line break
        part, place, _ = self.m.page(text, {'max_chars': 1000})
        self.assertTrue(part.endswith(' '), repr(part[-20:]))
        self.assertEqual(place['next_offset'], len(part))

    @needs(US_C)
    def test_a_long_answer_not_in_parts_is_cut_and_says_so(self):
        from unittest import mock
        folder = CORPUS(USC)
        with mock.patch.object(self.m, 'MAX_ANSWER', 2000):
            reply = self.m._handle('tools/call', 1, {'name': 'list_provisions', 'arguments': {'path': folder, 'max_results': 500, 'by_folder': False}})
        text = reply['result']['content'][0]['text']
        self.assertLess(len(text), 2300)
        self.assertIn('Narrow the question', text)
        self.assertGreater(reply['result']['structuredContent']['text_cut']['chars'], 2000)
        with mock.patch.object(self.m, 'MAX_ANSWER', 2000):  # a paged answer keeps the length it asked for
            reply = self.m._handle('tools/call', 2, {'name': 'read_law', 'arguments': {'path': STAY, 'date': '2026-01-01', 'max_chars': 5000}})
        self.assertGreater(len(reply['result']['content'][0]['text']), 4000)

    @needs(US_C)
    def test_headings_are_read_only_for_rows_shown(self):
        # Reading every file's heading read every file: listing Spain's 326,000 took 34 s and the whole text in memory.
        from unittest import mock
        asked = []
        real = self.m.read_headings.__wrapped__
        with mock.patch.object(self.m, 'read_headings', lambda c, s, names: asked.append(len(names)) or real(c, s, names)):
            text, data = self.m.t_list_provisions({'path': CORPUS(USC), 'max_results': 3, 'by_folder': False})
            self.assertEqual(len(data['provisions']), 3)
            self.assertTrue(all(p['heading'] for p in data['provisions']), data['provisions'])
            self.assertLessEqual(max(asked), 3)
            asked.clear()
            self.m.t_list_provisions({'path': CORPUS(USC)})  # by folder: a title for each folder shown
            self.assertLessEqual(max(asked or [0]), self.m.FOLDER_ROWS)

    def test_a_server_no_one_reads_still_exits(self):
        # A client that closes stdin and never reads: the answers fill the pipe, and the server must not wait for ever.
        fresh = Server()
        try:
            for i in range(4):
                fresh.proc.stdin.write((json.dumps({'jsonrpc': '2.0', 'id': i, 'method': 'tools/call', 'params': {
                    'name': 'read_law', 'arguments': {'path': STAY, 'date': '2026-01-01'}}}) + '\n').encode('utf-8'))
            fresh.proc.stdin.close()
            started = time.monotonic()
            # It must exit, however busy the machine: warming up and four reads, then 10 s of a stalled write.
            fresh.proc.wait(timeout=600)
            self.assertLess(time.monotonic() - started, 600)
        finally:
            if fresh.proc.poll() is None:
                fresh.proc.kill()
            fresh.proc.stdout.close()
            fresh.proc.stderr.close()

    @needs(US_C)
    def test_who_wrote_credits_long_provisions_by_line(self):
        from unittest import mock
        with mock.patch.object(self.m, 'WORDS_MAX', 50):
            text, data = self.m.t_who_wrote({'path': USC, 'date': '2026-01-01'})
        self.assertEqual(data['granularity'], 'line')
        self.assertIn('Credited by line', text)
        with mock.patch.object(self.m, 'WORDS_SECONDS', -1):  # any word-by-word pass is too slow
            text, data = self.m.t_who_wrote({'path': USC, 'date': '2026-01-01'})
        self.assertEqual(data['granularity'], 'line')
        self.assertIn('longer than', data['fell_back'])

    def test_the_deadline_covers_the_servers_own_work(self):
        self.m._call.deadline = time.monotonic() - 1
        try:
            with self.assertRaises(subprocess.TimeoutExpired):
                self.m.checkpoint()
            with self.assertRaises(subprocess.TimeoutExpired):
                self.m.git_run(['git', 'rev-parse', 'HEAD'], capture_output=True)
        finally:
            self.m._call.deadline = 0.0

    def test_a_cancelled_git_process_is_stopped(self):
        import threading
        self.m._call.cancel = threading.Event()
        self.m._call.cancel.set()
        try:
            with self.assertRaises(self.m.Cancelled):
                self.m.git_run(['git', 'rev-parse', 'HEAD'], capture_output=True)
        finally:
            self.m._call.cancel = None

    def test_ping_and_cancel_while_a_call_waits(self):
        # A fresh server's first call waits for the warm-up (seconds), so the ping and the cancel arrive while it waits.
        fresh = Server()
        try:
            def line(m):
                fresh.proc.stdin.write((json.dumps({'jsonrpc': '2.0', **m}) + '\n').encode('utf-8'))
            line({'id': 1, 'method': 'tools/call', 'params': {'name': 'list_jurisdictions', 'arguments': {}}})
            line({'method': 'notifications/cancelled', 'params': {'requestId': 1, 'reason': 'test'}})
            line({'id': 2, 'method': 'ping'})
            line({'id': 3, 'method': 'tools/call', 'params': {'name': 'find_provision', 'arguments': {'query': '1182'}}})
            fresh.proc.stdin.flush()
            first = json.loads(fresh.proc.stdout.readline())
            second = json.loads(fresh.proc.stdout.readline())
            self.assertEqual(first['id'], 2)  # answered at once, ahead of the waiting call
            self.assertEqual(second['id'], 3)
            fresh.proc.stdin.close()
            self.assertEqual(fresh.proc.stdout.read(), b'')  # the cancelled call never answers
        finally:
            fresh.proc.wait(timeout=60)
            fresh.proc.stdout.close()
            fresh.proc.stderr.close()


class Dating(unittest.TestCase):
    """A provision on a date is read from its own history by in-force date, not commit order: corpora append older acts
    after their tip and corrections to earlier versions, and the tree can only grow by fast-forward."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import law
        cls.law = law

    def test_the_greatest_in_force_date_wins_then_corrections_apply_by_their_dates(self):
        # The file act/a.md: version a (2010), an older version c appended after the tip (2005), and a correction e
        # that touches it for 2012 only. Correction d names the file in Files: but leaves its text as it is (a late-
        # found version equal to the tip), from 2010 with an open end: it ends the day before the act's next ordinary
        # commit, b on 2020-01-01, which does not touch this file.
        from unittest import mock
        hist = [{'commit': 'a', 'in_force': '2010-01-01', 'kind': 'law'},
                {'commit': 'c', 'in_force': '2005-06-01', 'kind': 'law'},
                {'commit': 'e', 'in_force': '2012-01-01', 'kind': 'correction', 'corrects': 'Act 2012-01-01..2012-12-31'}]
        fixes = [{'commit': 'd', 'from': '2010-01-01', 'to': None, 'files': ['act/a.md'], 'act_path': 'act'},
                 {'commit': 'e', 'from': '2012-01-01', 'to': '2012-12-31', 'files': [], 'act_path': None}]
        nexts = {('act',): ['2020-01-01']}
        with mock.patch.object(self.law, 'corpus_of', lambda path: ('x/y/z', path.removeprefix('x/y/z/'))), \
                mock.patch.object(self.law, 'history', lambda path: hist), \
                mock.patch.object(self.law, 'corrections', lambda corpus: fixes), \
                mock.patch.object(self.law, 'act_next', lambda corpus, paths, after: next((d for d in nexts[tuple(paths)] if d > after), None)):
            on = lambda date: self.law.file_commit(date, 'x/y/z/act/a.md')  # noqa: E731
            self.assertIsNone(on('2004-12-31'))
            self.assertEqual(on('2007-01-01'), 'c')  # the older version, though appended after the tip
            self.assertEqual(on('2011-01-01'), 'd')  # corrected, though git shows no change to the file
            self.assertEqual(on('2012-06-01'), 'e')  # the later correction covering the day
            self.assertEqual(on('2013-01-01'), 'd')  # e's dates are over; d still applies
            self.assertEqual(on('2019-12-31'), 'd')
            self.assertEqual(on('2020-01-01'), 'a')  # the act's next commit ends d: back to the ordinary version
            # An act that is one file in a shared folder: Act-path names it, so a change to the folder does not end d.
            fixes[0]['act_path'] = 'act/a.md'
            nexts[('act/a.md',)] = []
            self.assertEqual(on('2021-01-01'), 'd')

    @out_of_date("law.py now requires a corpus to be pinned in the tree; the test's throwaway corpus zz is not")
    def test_a_real_corpus_with_end_blocks_and_corrections(self):
        # A corpus as the breadth-first scrapers write it: the current text first, an older version back-filled after
        # the tip, then corrections with Files: and Act-path:, one of them an empty commit (no change git can see).
        import shutil
        import tempfile
        from unittest import mock
        root = Path(tempfile.mkdtemp())
        cwd = root / 'zz'
        cwd.mkdir()

        def commit(law_name, files, trailers, empty=False):
            for name, text in files.items():
                (cwd / name).parent.mkdir(parents=True, exist_ok=True)
                (cwd / name).write_text(text, encoding='utf-8')
            subprocess.run(['git', 'add', '-A'], cwd=cwd, check=True)
            subprocess.run(['git', '-c', f'user.name={law_name}', '-c', 'user.email=law@example.org', 'commit', '-q',
                            *(['--allow-empty'] if empty else []), '-m', f'{law_name}\n\n' + '\n'.join(trailers)], cwd=cwd, check=True)
            return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=cwd, capture_output=True, text=True).stdout.strip()

        try:
            subprocess.run(['git', 'init', '-q'], cwd=cwd, check=True)
            current = commit('Law 2020', {'act/a.md': 'current\n'}, ['In-force: 2020-01-01'])
            commit('Law 2021', {'act/b.md': 'other\n'}, ['In-force: 2021-01-01'])  # the folder changes; a.md does not
            original = commit('Law 2010', {'act/a.md': 'original 2010\n'}, ['In-force: 2010-01-01'])  # an end block
            fixed = commit('Correction', {'act/a.md': 'corrected 2010\n'},
                           ['Kind: correction', 'In-force: 2010-01-01', 'Corrects: Act 2010-01-01..2014-12-31',
                            f'Supersedes: {original}', 'Reason: misread', 'Act-path: act/a.md', 'Files: act/a.md'])
            empty = commit('Correction', {}, ['Kind: correction', 'In-force: 2015-01-01', 'Corrects: Act 2015-01-01..',
                                              'Supersedes: none', 'Reason: late-found version', 'Act-path: act/a.md',
                                              'Files: act/a.md'], empty=True)
            info = {'path': 'zz', 'in_force_trailer': 'In-force'}
            with mock.patch.object(self.law, 'ROOT', root), mock.patch.object(self.law, 'tip', lambda corpus: None), \
                    mock.patch.object(self.law, 'corpus_info', lambda corpus: info), \
                    mock.patch.object(self.law, 'corpus_of', lambda path: ('zz', path.removeprefix('zz/'))):
                self.law._CACHE.clear()
                on = lambda date: self.law.text_on(date, 'zz/act/a.md')  # noqa: E731
                self.assertIsNone(on('2005-01-01'))
                self.assertEqual(on('2012-01-01'), 'corrected 2010\n')
                self.assertEqual(on('2016-01-01'), 'corrected 2010\n')  # the empty correction, open from 2015
                self.assertEqual(self.law.file_commit('2016-01-01', 'zz/act/a.md'), empty)
                self.assertEqual(on('2020-06-01'), 'current\n')  # Act-path's next ordinary commit ends the open range
                self.assertEqual(self.law.file_commit('2020-06-01', 'zz/act/a.md'), current)
                self.assertIn(empty, [h['commit'] for h in self.law.history('zz/act/a.md')])  # named, though unchanged
                self.assertEqual([c['commit'] for c in self.law.corrections('zz')], [fixed, empty])
                # The whole corpus on a past date (search_law, list_provisions, changes_between): not the commit-order
                # prefix, which would miss the end block, but a tree of each file's version for the date.
                self.assertFalse(self.law.in_order('zz'))
                files = lambda tree: self.law.git('ls-tree', '-r', '--name-only', tree, cwd=cwd).split()  # noqa: E731
                t2016 = self.law.corpus_tree('2016-01-01', 'zz')
                self.assertEqual(files(t2016), ['act/a.md'])  # the act appended after the tip; b.md not yet in force
                self.assertEqual(self.law.git('show', f'{t2016}:act/a.md', cwd=cwd), 'corrected 2010\n')
                self.assertIn('act/a.md', self.law.git('grep', '-l', 'corrected', t2016, cwd=cwd))
                t2021 = self.law.corpus_tree('2021-06-01', 'zz')
                self.assertEqual(files(t2021), ['act/a.md', 'act/b.md'])
                self.assertEqual(self.law.git('show', f'{t2021}:act/a.md', cwd=cwd), 'current\n')
                self.assertIsNone(self.law.corpus_tree('2005-01-01', 'zz'))
                self.law._CACHE.clear()
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_states_and_cities_by_their_own_names(self):
        bremen = {'path': 'germany/bremen/acts', 'code': 'DE-HB'}
        for name in ('bremen', 'Bremen', 'germany', 'germany/bremen', 'de-hb'):
            self.assertTrue(self.law.matches(bremen, name), name)
        self.assertFalse(self.law.matches({'path': 'germany/bund/acts'}, 'bund'))  # a generic level names nothing

    def test_a_build_py_repo_passes_on_its_own_descriptors(self):
        # build.py repos ship jurisdiction.json and data/repo.json, not corpus.json: a warning, not a failure, and
        # no "no citation rule" warning about a corpus.json that does not exist.
        import json as _json
        import shutil
        import tempfile
        sys.path.insert(0, str(ROOT / 'tools'))
        import check_corpus
        d = Path(tempfile.mkdtemp())
        try:
            run = lambda *a: subprocess.run(['git', *a], cwd=d, check=True, capture_output=True)  # noqa: E731
            run('init', '-q')
            (d / 'REPRODUCE.md').write_text('x')
            (d / 'jurisdiction.json').write_text(_json.dumps({'path': 'de-hb', 'code': 'DE-HB', 'name': 'Bremen'}))
            (d / 'data').mkdir()
            (d / 'data' / 'repo.json').write_text(_json.dumps({'country': 'DE-HB', 'name': 'Bremen'}))
            (d / 'a.md').write_text('a')
            run('add', '-A')
            run('-c', 'user.name=L', '-c', 'user.email=l@x', 'commit', '-q', '-m', 'a\n\nIn-force: 2020-01-01')
            fatal, warn = check_corpus.problems(d, '2026-11-03')
            self.assertEqual(fatal, [])
            self.assertTrue(any('described by jurisdiction.json' in w for w in warn), warn)
            self.assertFalse(any(w.startswith('corpus.json has no citation rule') for w in warn), warn)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_the_check_takes_every_history_and_either_consolidated(self):
        # Every history value MCP.md documents passes; Consolidated: is a date (canonical) or, in older corpora, a
        # link; a legacy corpus with no corpus.json is warned about, not passed silently.
        import json as _json
        import shutil
        import tempfile
        sys.path.insert(0, str(ROOT / 'tools'))
        import check_corpus
        import describe
        self.assertEqual(set(check_corpus.HISTORY), set(describe.HISTORY_VALUES))
        d = Path(tempfile.mkdtemp())
        try:
            run = lambda *a: subprocess.run(['git', *a], cwd=d, check=True, capture_output=True)  # noqa: E731
            commit = lambda msg: run('-c', 'user.name=L', '-c', 'user.email=l@x', 'commit', '-q', '--allow-empty',
                                     '-m', msg)  # noqa: E731
            run('init', '-q')
            (d / 'REPRODUCE.md').write_text('x')
            cj = {'corpus': 'kg/national/acts', 'citation': {'file': '(a)/(b)', 'cites': 'x{n}'}}
            (d / 'corpus.json').write_text(_json.dumps({**cj, 'history': 'metadata-only'}))
            run('add', '-A')
            commit('Catalogue\n\nKind: documentation')
            fatal, warn = check_corpus.problems(d, '2026-11-03')
            self.assertEqual(fatal, [])  # nothing to date in a catalogue
            (d / 'corpus.json').write_text(_json.dumps({**cj, 'baseline_trailer': 'Consolidated'}))
            run('add', '-A')
            commit('Act 1\n\nIn-force: 2020-01-01\nConsolidated: 2020-01-01\nSource: https://example.org/1')
            commit('Act 2\n\nIn-force: 2021-01-01\nConsolidated: https://example.org/2')
            fatal, warn = check_corpus.problems(d, '2026-11-03')
            self.assertEqual(fatal, [])
            self.assertFalse(any('Consolidated' in w for w in warn), warn)
            commit('Act 3\n\nIn-force: 2022-01-01\nConsolidated: ask the registry')
            commit('Act 4\n\nConsolidated: https://example.org/4')  # its only date would be a link
            fatal, warn = check_corpus.problems(d, '2026-11-03')
            self.assertTrue(any('neither a date' in w for w in warn), warn)
            self.assertTrue(any('cannot date them' in w for w in warn), warn)
            run('rm', '-q', 'corpus.json')
            commit('No description\n\nKind: documentation')
            fatal, warn = check_corpus.problems(d, '2026-11-03', legacy=True)
            self.assertEqual(fatal, [])
            self.assertTrue(any(w.startswith(check_corpus.NO_CORPUS_JSON) for w in warn), warn)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_the_check_reports_redates_and_acts_json_readers_ignore(self):
        # Redates:, Retroactive: and data/acts.json change what readers answer (MCP.md "How a corpus describes
        # itself"), so a record readers would silently skip is reported: a warning each, with a count.
        import json as _json
        import shutil
        import tempfile
        sys.path.insert(0, str(ROOT / 'tools'))
        import check_corpus
        d = Path(tempfile.mkdtemp())
        try:
            run = lambda *a: subprocess.run(['git', *a], cwd=d, check=True, capture_output=True, text=True)  # noqa: E731
            commit = lambda who, msg: run('-c', f'user.name={who}', '-c', 'user.email=l@x', 'commit', '-q',  # noqa: E731
                                          '--allow-empty', '-m', msg)
            run('init', '-q')
            (d / 'REPRODUCE.md').write_text('x')
            (d / 'corpus.json').write_text(_json.dumps({
                'corpus': 'qq/national/acts', 'name': 'QQ', 'language': 'en', 'history_from': '2000-01-01',
                'record_to': '2026-11-01', 'in_force_trailer': 'In-force', 'citation': {'file': '(a)/(b)', 'cites': 'x{n}'}}))
            for act in ('act1', 'act2'):
                (d / act).mkdir()
                (d / act / 's1.md').write_text(act)
            run('add', '-A')
            commit('Act 1', 'Act 1\n\nIn-force: 2000-01-01')
            act1 = run('rev-parse', 'HEAD').stdout.strip()
            commit('Act 2', 'Act 2\n\nIn-force: 2001-01-01\nEnacted: 2001-02-01\nRetroactive: yes; Article 9')
            good = {'acts': [{'path': 'act1', 'status': 'repealed', 'repealed': '2010-01-01', 'repealed_by': 'Act 3'},
                             {'path': 'act2', 'status': 'in force', 'in_force': '2001-01-01'}]}
            (d / 'data').mkdir()
            (d / 'data' / 'acts.json').write_text(_json.dumps(good))
            run('add', '-A')
            commit('Lexifina', f'Redate\n\nKind: documentation\nRedates: {act1} 2000-02-01\nRedates: {act1[:7]} no-date')
            fatal, warn = check_corpus.problems(d, '2026-11-03')
            self.assertEqual((fatal, warn), ([], []))
            commit('builder', f'Redate\n\nKind: documentation\nRedates: {act1} 2000-03-01')
            commit('Lexifina', 'Redate\n\nKind: documentation\nRedates: deadbeefdeadbeef 2000-03-01\n'
                               f'Redates: {act1} 1 March 2000')
            commit('Act 4', 'Act 4\n\nIn-force: 2002-01-01\nRetroactive: Article 2')
            (d / 'data' / 'acts.json').write_text(_json.dumps({'acts': [
                {'path': 'act1', 'status': 'repealed', 'repealed': '01/05/2020'},
                {'path': 'act9', 'status': 'repealed', 'repealed': '2020-05-01'},
                {'path': 'act2', 'status': 'struck down'}, {'title': 'no path'}]}))
            run('add', '-A')
            commit('Lexifina', 'Bad rows\n\nKind: documentation')
            fatal, warn = check_corpus.problems(d, '2026-11-03')
            self.assertEqual(fatal, [])
            for expected in ('author other than Lexifina', "is not 'Redates:", 'no commit above them',
                             "does not start with 'yes'", "1 path(s) name no folder at HEAD, so they end no file (first 'act9')",
                             "1 repealed value(s) that are not YYYY-MM-DD, on acts whose status ends them: readers "
                             "end the act with no day", "(first act1: '01/05/2020')",
                             "status values readers do not recognise", "'struck down' (1)", '1 entr(ies) have no path'):
                self.assertTrue(any(expected in w for w in warn), (expected, warn))
            (d / 'data' / 'acts.json').write_text('{"acts": [')
            run('add', '-A')
            commit('Lexifina', 'Broken\n\nKind: documentation')
            fatal, warn = check_corpus.problems(d, '2026-11-03')
            self.assertTrue(any('data/acts.json is not' in f for f in fatal), fatal)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_the_check_says_what_law_py_does(self):
        # Row 40: the same synthetic corpus goes to check_corpus.py and to tools/law.py, and each warning's claim is
        # what law.py answers: a trailer outside git's trailer block is ignored, an impossible day is used as written,
        # and each data/acts.json row ends its act exactly as the warning says (or, with no warning, as written).
        sys.path.insert(0, str(ROOT / 'tests'))
        sys.path.insert(0, str(ROOT / 'tools'))
        import check_corpus
        from test_law_fixtures import Tree, run as git_run
        t = Tree()
        try:
            c = t.corpus('xx/national/acts')

            def raw(author, files, message):  # a commit whose message is written out, not built from trailers
                for name, text in files.items():
                    (c.path / name).parent.mkdir(parents=True, exist_ok=True)
                    (c.path / name).write_text(text, encoding='utf-8')
                    git_run('add', name, cwd=c.path)
                c.n += 1
                stamp = f'2001-01-01T00:00:{c.n:02d}Z'
                git_run('commit', '-q', '--allow-empty', '-m', message, cwd=c.path,
                        env={'GIT_AUTHOR_NAME': author, 'GIT_AUTHOR_EMAIL': 'l@x', 'GIT_AUTHOR_DATE': stamp,
                             'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@x', 'GIT_COMMITTER_DATE': stamp})
                return git_run('rev-parse', 'HEAD', cwd=c.path)

            files = {f'{a}/s.md': f'{a}\n' for a in ('p1', 'p2', 'p3', 'p5', 'p6', 'p8')}
            typo = c.commit('Act 1 of 2015', files, In_force='2051-03-01', Kind='law', Enacted='2015-01-01')
            raw('Lexifina', {}, f'Redate a typo\n\nKind: documentation\nRedates: {typo} 2015-03-01\n'
                                'The source gave 2051 by mistake.\n')  # P1: the Redates: line is not in the block
            imp = c.commit('Act 2 of 2015', {'p4/s.md': 'p4 2015\n'}, In_force='2015-03-01', Kind='law')
            c.commit('Lexifina', {}, Kind='documentation', Redates=f'{imp} 2015-13-45')  # P4
            raw('Act 3 of 2011', {'p7/s.md': 'p7\n'}, 'Act 3 of 2011\n\nIn-force: 2011-01-01\n'
                                                       'Text from the gazette.\n')  # P7: In-force in the body
            retro = c.commit('Act 4 of 2012', {'p9/s.md': 'p9 2012\n'}, In_force='2012-01-01', Kind='law',
                             Retroactive='Article 2')
            acts = {'acts': [
                {'path': 'p2', 'status': 'annulled', 'annulled': '2018-05-01'},
                {'path': 'p3', 'status': 'repealed', 'repealed': '2018-05-01T00:00:00Z'},
                {'path': 'p5', 'repealed': '1999'},
                {'path': 'p6', 'status': 'in force ', 'repealed': '2018-05-01'},
                {'path': 'p8', 'status': 'in force', 'repealed': '2018-05-01'},
                {'path': 'p9', 'status': 'Repealed', 'repealed': '2019-02-30'}]}
            c.commit('Lexifina', {'data/acts.json': json.dumps(acts), 'REPRODUCE.md': 'x'}, Kind='documentation')
            t.pin()
            cj = {'corpus': 'xx/national/acts', 'name': 'X', 'language': 'en', 'history_from': '2000-01-01',
                  'record_to': '2026-11-01', 'in_force_trailer': 'In-force', 'citation': {'file': '(a)/(b)', 'cites': 'x'}}
            fatal, warn = check_corpus.problems(c.path, '2026-11-04', corpus_json=cj)
            law = t.law()  # noqa: F841 (closed in finally)
            day = lambda p: [h['in_force'] for h in law.history(f'xx/national/acts/{p}') if not h.get('ends')]  # noqa: E731
            said = lambda text: any(text in w for w in warn)  # noqa: E731

            self.assertTrue(said('Redates: line outside the trailer block, which readers ignore'), warn)  # P1
            self.assertEqual(day('p1/s.md'), ['2051-03-01'])
            self.assertTrue(said(f'->{imp[:7]} 2015-13-45); readers date the version by it as written'), warn)
            self.assertEqual(day('p4/s.md'), ['2015-13-45'])
            self.assertTrue(said('have a In-force: line outside the trailer block'), warn)  # P7
            self.assertEqual(law.history('xx/national/acts/p7/s.md'), [])
            self.assertTrue(said(f"Retroactive: trailer that does not start with 'yes', which readers ignore (first "
                                 f"{retro[:7]})"), warn)
            self.assertNotIn(retro, law._index('xx/national/acts').get('retroactive', set()))

            # data/acts.json: the check reads each row with law.py's own act_ends, and the tree's reader agrees.
            ends = law.act_ends('xx/national/acts')
            self.assertEqual(check_corpus.reader_act_ends(json.dumps(acts))[0], ends)
            self.assertEqual(ends['p2']['day'], '2018-05-01')  # P2: annulled ends it, and nothing is said
            self.assertFalse(said("p2:"), warn)
            self.assertEqual(ends['p3']['day'], '2018-05-01')  # P3
            self.assertTrue(said("longer than YYYY-MM-DD: readers end the act on the first 10 characters (first p3: "
                                 "'2018-05-01T00:00:00Z' -> 2018-05-01)"), warn)
            self.assertNotIn('p5', ends)  # P5
            self.assertTrue(said("on acts with no ending status: readers do not end the act at all (first p5: '1999')"),
                            warn)
            self.assertEqual(ends['p6']['day'], '2018-05-01')  # P6: an unknown status is no status
            self.assertTrue(said("so they read them as no status (an act with a repealed, expired or annulled day is "
                                 "ended on it, one without is not ended): 'in force ' (1)"), warn)
            self.assertNotIn('p8', ends)  # in force, whatever day it records
            self.assertTrue(said("end day(s) on acts whose status says in force, which readers ignore: the act is not "
                                 "ended (first p8: '2018-05-01')"), warn)
            self.assertEqual(ends['p9']['day'], '2019-02-30')  # an impossible end day, used as written
            self.assertTrue(said("no day of the calendar: readers end the act on it as written"), warn)
            self.assertEqual(fatal, [])
        finally:
            if 'law' in locals():
                law.close_readers()
            t.close()

    def test_corrects_names_its_dates(self):
        m = self.law.CORRECTS.search('Legea nr. 31/1990 2010-01-01..2015-12-31')
        self.assertEqual((m.group(1), m.group(2)), ('2010-01-01', '2015-12-31'))
        m = self.law.CORRECTS.search('Codul civil 2011-10-01..')
        self.assertEqual((m.group(1), m.group(2)), ('2011-10-01', None))


class UnreadableCheckouts(unittest.TestCase):
    """Issues #7 and #11: a corpus checked out but unreadable at its pin (no commit yet, behind its pin, shallow) is
    not served. Every tool over several corpora answers from the rest and names it with its fix; a tool scoped to it
    says what to run. A small tree built here, with the server's tools called in a child process at its root."""

    CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
            'out = []\n'
            'for name, args in json.loads(sys.stdin.read()):\n'
            '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
            '"params": {"name": name, "arguments": args}})["result"]\n'
            '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
            'print(json.dumps(out))\n')

    @classmethod
    def setUpClass(cls):
        import shutil
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        shutil.copy(ROOT / 'tools' / 'mcp_server.py', t.root / 'tools' / 'mcp_server.py')
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        run('add', 'jurisdiction.json', cwd=t.root)
        good = t.corpus('aa/national/acts')
        good.commit('Act 1 of 2010', {'act/s1.md': 'The constitution holds.\n'}, In_force='2010-01-01', Kind='law')
        good.commit('Act 2 of 2020', {'act/s1.md': 'The constitution still holds.\n'}, In_force='2020-01-01', Kind='law')
        for path in ('bb/national/acts', 'aa/upper/acts', 'dd/national/acts'):  # unborn, behind, shallow
            c = t.corpus(path)
            c.commit('Act 1 of 2011', {'s1.md': 'A constitution here too.\n'}, In_force='2011-01-01', Kind='law')
            c.commit('Act 2 of 2021', {'s1.md': 'A constitution, amended.\n'}, In_force='2021-01-01', Kind='law')
        t.pin()
        unborn = t.corpora['bb/national/acts'].path  # an interrupted clone: a .git, no commit
        shutil.rmtree(unborn, onerror=lambda f, p, _: (os.chmod(p, 0o700), f(p)))
        unborn.mkdir()
        run('init', '-q', cwd=unborn)
        behind = t.corpora['aa/upper/acts'].path  # a pull without `git submodule update`: the pin is not here
        run('reset', '-q', '--hard', 'HEAD~1', cwd=behind)
        run('reflog', 'expire', '--expire=now', '--all', cwd=behind)
        run('gc', '-q', '--prune=now', cwd=behind)
        cut = t.corpora['dd/national/acts'].path  # a --depth 1 clone of two commits: its history is cut
        shutil.move(str(cut), str(t.root / 'dd-full'))
        run('clone', '-q', '--depth', '1', (t.root / 'dd-full').as_uri(), str(cut), cwd=t.root)
        cls.FIXES = {'bb/national/acts': 'git submodule update --init -- bb/national/acts',
                     'aa/upper/acts': 'git submodule update --init -- aa/upper/acts',
                     'dd/national/acts': 'git -C dd/national/acts fetch --unshallow'}

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def calls(self, *calls, env: dict | None = None) -> list[dict]:
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', self.CALL], cwd=self.t.root, input=json.dumps(calls),
                              capture_output=True, encoding='utf-8', timeout=300, env={**os.environ, **(env or {})})
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    def assert_names_the_broken(self, answer: dict, label: str, paths=None):
        self.assertFalse(answer['error'], (label, answer['text']))
        for path, fix in self.FIXES.items():
            if paths is None or path in paths:
                self.assertIn(f'Left out: {path}', answer['text'], label)
                self.assertIn(fix, answer['text'], label)

    def test_tools_over_every_corpus_answer_the_rest_and_name_the_broken(self):
        tools = [('list_jurisdictions', {}), ('find_provision', {'query': 'constitution'}),
                 ('search_law', {'query': 'constitution'}), ('laws_between', {'start': '2000-01-01', 'end': '2030-01-01'}),
                 ('world_on_date', {'date': '2025-01-01'}), ('search_changes', {'query': 'Act'}),
                 ('phrase_history', {'query': 'constitution'})]
        answers = self.calls(*tools)
        for (name, _), answer in zip(tools, answers):
            self.assert_names_the_broken(answer, name)
        listed = answers[0]['data']
        self.assertEqual([c['path'] for c in listed['corpora']], ['aa/national/acts'])
        reasons = {c['path']: c['reason'] for c in listed['not_served']}
        self.assertEqual(reasons, {'bb/national/acts': 'no commit yet', 'aa/upper/acts': 'behind its pin',
                                   'dd/national/acts': 'shallow clone'})
        self.assertIn('aa/national/acts/act/s1.md', answers[2]['text'])  # search_law: the healthy corpus's hit
        self.assertEqual(answers[2]['data']['provision_count'], 1)
        self.assertIn('Act 2 of 2020', answers[3]['text'])  # laws_between
        self.assertNotIn('Act 2 of 2021', answers[3]['text'])
        self.assertIn('aa/national/acts', answers[5]['text'])  # search_changes: not "not checked out"
        self.assertNotIn('Not checked out, so not searched', answers[5]['text'])
        self.assertIn('aa/national/acts/act/s1.md', answers[6]['text'])  # phrase_history

    def test_a_tool_scoped_to_a_broken_corpus_says_what_to_run(self):
        tools = [('search_law', {'query': 'constitution', 'jurisdiction': 'dd'}),
                 ('search_changes', {'query': 'Act', 'jurisdiction': 'aa/upper/acts'}),
                 ('phrase_history', {'query': 'constitution', 'jurisdiction': 'aa/upper/acts'}),
                 ('laws_between', {'start': '2000-01-01', 'end': '2030-01-01', 'jurisdiction': 'bb'}),
                 ('read_law', {'path': 'dd/national/acts/s1.md'}),
                 ('list_provisions', {'path': 'bb/national/acts'})]
        corpora = ['dd/national/acts', 'aa/upper/acts', 'aa/upper/acts', 'bb/national/acts', 'dd/national/acts',
                   'bb/national/acts']
        for (name, args), corpus, answer in zip(tools, corpora, self.calls(*tools)):
            self.assertTrue(answer['error'], (name, answer['text']))
            self.assertIn(self.FIXES[corpus], answer['text'], name)
            self.assertNotIn('Internal error', answer['text'], name)

    def test_a_server_narrowed_by_the_environment_answers(self):
        # GLOBAL_LAW_JURISDICTIONS once made every tool call fail with a RecursionError: _look asked law.matches, which
        # read law.manifest for country names, and the server's law.manifest is _look. Names now read every corpus.
        answers = self.calls(('list_jurisdictions', {}), ('search_law', {'query': 'constitution'}),
                             ('read_law', {'path': 'aa/national/acts/act/s1.md'}),
                             env={'GLOBAL_LAW_JURISDICTIONS': 'aa/national'})
        for answer in answers:
            self.assertFalse(answer['error'], answer['text'])
        listed = answers[0]['data']
        self.assertEqual([c['path'] for c in listed['corpora']], ['aa/national/acts'])
        self.assertEqual({c['reason'] for c in listed['not_served']}, {'not chosen'})
        self.assertEqual(listed['chosen'], ['aa/national'])
        self.assertIn('aa/national/acts/act/s1.md', answers[1]['text'])
        self.assertIn('The constitution still holds.', answers[2]['text'])

    def test_a_scope_over_a_healthy_and_a_broken_corpus_names_the_broken(self):
        answers = self.calls(('search_law', {'query': 'constitution', 'jurisdiction': 'aa'}),
                             ('laws_between', {'start': '2000-01-01', 'end': '2030-01-01', 'jurisdiction': 'aa'}))
        for answer in answers:
            self.assert_names_the_broken(answer, 'aa', ['aa/upper/acts'])
            self.assertNotIn('bb/national/acts', answer['text'])
        self.assertIn('aa/national/acts/act/s1.md', answers[0]['text'])


class EndsAndPartialRepeals(unittest.TestCase):
    """Audit rows 53 and 57 in the server: provision_history marks the version that removes a provision as ended,
    laws_between leaves out ends of validity no law is named for (France's "Fin de vigueur"), and read_law notes an
    act's end whose scope the record leaves unresolved. A small tree built here, the tools called in a child process."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        shutil.copy(ROOT / 'tools' / 'mcp_server.py', t.root / 'tools' / 'mcp_server.py')
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        run('add', 'jurisdiction.json', cwd=t.root)
        a = t.corpus('aa/national/acts')
        a.commit('Act 1', {'act1/s1.md': 'one\n', 'act1/s2.md': 'two\n', 'unres/a1.md': 'unres one\n'},
                 In_force='2010-01-01', Kind='law')
        a.commit('Act 2', {'act1/s1.md': None}, In_force='2020-01-01', Kind='law')
        a.commit('Fin de vigueur', {'act1/s2.md': None}, In_force='2020-01-01')
        acts = {'acts': [{'path': 'unres', 'status': 'repealed', 'repealed': '2020-01-01',
                          'repealed_by': 'Act 2, excepto el art. 2', 'lifecycle_scope_unresolved': True}]}
        a.commit('Lexifina', {'data/acts.json': json.dumps(acts)}, Kind='documentation')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_ends_in_history_laws_and_read_law(self):
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', UnreadableCheckouts.CALL], cwd=self.t.root,
                              input=json.dumps([['provision_history', {'path': 'aa/national/acts/act1/s1.md'}],
                                                ['provision_history', {'path': 'aa/national/acts/act1/s2.md'}],
                                                ['laws_between', {'start': '2020-01-01', 'end': '2020-01-01'}],
                                                ['read_law', {'date': '2021-01-01',
                                                              'path': 'aa/national/acts/unres/a1.md'}]]),
                              capture_output=True, encoding='utf-8', timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        s1, s2, laws, read = json.loads(done.stdout)
        self.assertIn('2020-01-01  ended: Act 2', s1['text'])
        self.assertTrue(s1['data']['changes'][-1]['ended'])
        self.assertIn('2020-01-01  ended: Fin de vigueur (end of validity; no law named)', s2['text'])
        self.assertIn('Act 2', laws['text'])
        self.assertNotIn('Fin de vigueur', laws['text'])
        self.assertEqual(laws['data']['ends_not_listed'], 1)
        self.assertIn('unres one', read['text'])
        self.assertIn('saves some provisions', read['text'])


class Choosing(unittest.TestCase):
    """A clone may hold some countries, and a user may narrow the server to some: what is left out is named, with
    the command that adds it, and never fails a tool."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import countries
        import law
        cls.law, cls.countries = law, countries
        cls.server = Server(GLOBAL_LAW_JURISDICTIONS=GG_FOLDER)  # only the corpus that holds the Grundgesetz

    @classmethod
    def tearDownClass(cls):
        cls.server.close()

    def test_names_take_in_corpora(self):
        corpus = {'path': 'united-states/federal/usc', 'iso_path': 'us/federal/usc', 'code': 'US'}
        for name in ('united-states', 'United States', 'us', 'US', 'us/federal', 'united-states/federal/usc',
                     'united-states/federal/usc/title-11', 'united-states/'):
            self.assertTrue(self.law.matches(corpus, name), name)
        for name in ('united', 'united-kingdom', 'u', '', 'united-states/state'):
            self.assertFalse(self.law.matches(corpus, name), name)

    @needs(DE_C)
    def test_only_the_chosen_corpus_is_served(self):
        r = self.server.call('list_jurisdictions')
        served = [c['path'] for c in r['structuredContent']['corpora']]
        self.assertEqual(served, [CORPUS(GG_FOLDER)])
        left = r['structuredContent']['not_served']
        self.assertTrue(left and all(c['reason'] in ('not chosen', 'not checked out') for c in left))
        self.assertIn('Served here: 1 of the', r['content'][0]['text'])

    def test_a_corpus_left_out_says_how_to_add_it(self):
        if CORPUS(USC) == CORPUS(GG_FOLDER):
            self.skipTest('the US Code and the Grundgesetz share a corpus')
        r = self.server.call('read_law', path=USC)
        self.assertTrue(r['isError'])
        self.assertIn(CORPUS(USC), r['content'][0]['text'])
        # This server is narrowed by GLOBAL_LAW_JURISDICTIONS, which `countries.py only` cannot override: the answer
        # names the setting to change instead.
        self.assertRegex(r['content'][0]['text'], r'countries\.py add |GLOBAL_LAW_JURISDICTIONS in this server')
        r = self.server.call('search_law', query='stay', jurisdiction=P('us'))
        self.assertTrue(r['isError'])
        self.assertRegex(r['content'][0]['text'], r'countries\.py|GLOBAL_LAW_JURISDICTIONS in this server')

    @needs(DE_C)
    def test_answers_over_every_jurisdiction_say_what_was_not_searched(self):
        r = self.server.call('laws_between', start='2019-01-01', end='2019-12-31')
        self.assertFalse(r['isError'])
        self.assertIn('were not searched', r['content'][0]['text'])
        self.assertTrue(r['structuredContent']['not_searched_corpora'])
        r = self.server.call('read_law', path=GG.format('001'), include_text=False)  # a served path carries no note
        self.assertFalse(r['isError'])
        self.assertNotIn('were not searched', r['content'][0]['text'])

    def test_a_citation_left_out_is_not_called_absent(self):
        r = self.server.call('resolve_citations', text='11 U.S.C. § 1182(1) and Art. 1 GG')
        states = {c['path']: c['status'] for c in r['structuredContent']['citations']}
        self.assertEqual(states.get(USC), 'not served here')

    def test_a_corpus_not_checked_out_is_named(self):
        import mcp_server
        self.assertEqual(mcp_server.serving({'path': 'nowhere/national/acts', 'name': 'x'}, ()), 'not checked out')

    @needs(DE_C)
    def test_countries_resolves_names_and_suggests(self):
        self.assertEqual([c['path'] for c in self.countries.resolve([GG_FOLDER])], [CORPUS(GG_FOLDER)])
        with self.assertRaises(SystemExit) as stop:
            self.countries.resolve([GG_FOLDER.split('/')[0] + 'x'])
        self.assertIn('Did you mean', str(stop.exception))


class Helpers(unittest.TestCase):
    """The text helpers, on their own (no corpus needed)."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def test_a_lone_surrogate_is_refused_before_any_work(self):
        # JSON may carry "\ud800"; in a query it reached git's arguments and was an internal error (hosted fuzz, 2026-11-10)
        bad = chr(0xD800)
        for args in ({'query': bad}, {'query': 'ok', 'jurisdiction': [bad]}, {'query': {bad: 1}}):
            reply = self.m.answer({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                                   'params': {'name': 'find_provision', 'arguments': args}})
            self.assertTrue(reply['result']['isError'], reply)
            self.assertIn('lone surrogate', reply['result']['content'][0]['text'])
        self.assertFalse(self.m._lone_surrogate({'query': 'Würde 😀 ¹'}))

    def test_a_git_failure_past_the_deadline_is_the_time_limit(self):
        # A git command cut off at the deadline fails as RuntimeError: an "internal error" before (hosted fuzz, 2026-11-10)
        def failing(args):
            raise RuntimeError('git grep: killed')
        saved, timeout = self.m.HANDLERS['what_else_changes'], self.m.GIT_TIMEOUT
        self.m.HANDLERS['what_else_changes'] = failing
        try:
            for limit, expected in ((0, 'took longer than'), (600, 'Internal error')):
                self.m.GIT_TIMEOUT = limit
                reply = self.m.answer({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                                       'params': {'name': 'what_else_changes', 'arguments': {}}})
                self.assertIn(expected, reply['result']['content'][0]['text'])
        finally:
            self.m.HANDLERS['what_else_changes'], self.m.GIT_TIMEOUT = saved, timeout

    def test_list_provisions_path_must_be_text(self):
        # A number, a list or an object as the path was an internal error (AttributeError) (hosted fuzz, 2026-11-10)
        for path in (-1, 1.5, True, ['x'], {'a': 1}):
            reply = self.m.answer({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                                   'params': {'name': 'list_provisions', 'arguments': {'path': path}}})
            self.assertTrue(reply['result']['isError'], reply)
            self.assertIn('must be text', reply['result']['content'][0]['text'])

    def test_article_number_forms(self):
        self.assertEqual(self.m.number_forms('art. 6^1'), 'art. 6-1')
        self.assertEqual(self.m.number_forms('art. 6¹'), 'art. 6-1')
        self.assertEqual(self.m.number_forms('art. 6 indice 1'), 'art. 6-1')
        self.assertEqual(self.m.number_forms('art. 1.357'), 'art. 1357')
        self.assertEqual(self.m.number_forms('S.L. 586.08'), 'S.L. 586.08')  # not a thousands dot
        self.assertEqual(self.m.stem_of('lege/2009/287/art-0194.md'), '194')
        self.assertEqual(self.m.stem_of('lege/1990/31/art-006-1.md'), '6-1')
        for name, stem in (('codes/x/a31.md', '31'), ('art59.md', '59'), ('arta5.md', 'arta5'), ('a.md', 'a'),
                           ('art.md', 'art'), ('00a5.md', '5'), ('art-art5.md', '5'), ('1182.md', '1182')):
            self.assertEqual(self.m.stem_of(name), stem, name)

    def test_fold_drops_case_and_diacritics_only(self):
        # The fast path (ASCII, str.translate) gives what the character-by-character form gave.
        import unicodedata
        for text in ('Constituția', 'Răspunderea civilă', 'Ţară şi ţărm', 'Kündigung', 'responsabilité', 'Ελληνικά',
                     'Закон', 'ﬁnal', 'Ⅻ', 'PLAIN ascii 123', '', 'é', '日本'):
            slow = ''.join(ch for ch in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(ch))
            self.assertEqual(self.m.fold(text), slow, text)
        self.assertEqual(self.m.fold('Constituția'), 'constitutia')

    def test_act_citations(self):
        for text, kind, n, y in (('Legea nr. 31/1990', 'Legea', '31', '1990'), ('OUG 195/2002', 'OUG', '195', '2002'),
                                 ('H.G. nr. 1/2016', 'H.G.', '1', '2016'), ('Legea nr. 31 din 16 noiembrie 1990', 'Legea', '31', '1990')):
            m = self.m.ACT_CITE.search(text)
            self.assertEqual((m.group('kind'), m.group('n'), m.group('y')), (kind, n, y), text)

    def test_romanian_letters_match_with_or_without_diacritics(self):
        posix = lambda q: self.m.loose_pattern(q).replace('[[:space:]]+', r'\s+')  # git's class, as Python writes it  # noqa: E731
        rx = re.compile(posix('raspundere limitata'), re.I)
        self.assertTrue(rx.search('societate cu răspundere limitată'))
        rx = re.compile(self.m.loose_pattern('societăţi'))  # cedilla typed, comma below in the text
        self.assertTrue(rx.search('societăți'))
        self.assertTrue(re.compile(self.m.loose_pattern('când'), re.I).search('Cînd societatea'))  # spelling before 1993

    def test_links_are_the_publishers_own(self):
        url = self.m.official_url
        self.assertEqual(url('https://web.archive.org/web/20260605162605id_/https://legislatie.just.ro/Public/DetaliiDocument/137240'),
                         ('https://legislatie.just.ro/Public/DetaliiDocument/137240',
                          'https://web.archive.org/web/20260605162605id_/https://legislatie.just.ro/Public/DetaliiDocument/137240'))
        self.assertEqual(url('https://legislatie.just.ro/Public/document 172949 of the official web service')[0],
                         'https://legislatie.just.ro/Public/DetaliiDocument/172949')
        self.assertEqual(url('https://fedlex.data.admin.ch/eli/cc/1999/404/20210101')[0],
                         'https://www.fedlex.admin.ch/eli/cc/1999/404/20210101/de')
        self.assertEqual(url('https://www.gesetze-im-internet.de (Archiv QuantLaw)')[0], 'https://www.gesetze-im-internet.de')
        self.assertNotIn('Reader', self.m.SOURCE_KEYS + self.m.VERSION_KEYS)  # Lexifina's reader is never a source

    def test_a_wrapped_list_note_names_only_this_provision(self):
        body = ('Codul civil: 661 provisions (Legea nr. 71/2011)\n\nCodul civil, changed: Art. 1, Art. 2, Art.\n'
                '1076, Art. 1112, Art. 1114,\nArt. 1120\n\nAffecting: Codul civil Art. 1, Art. 1112\n')
        note = self.m.change_note(body, 'romania/national/acts/lege/2009/287/art-1112.md')
        self.assertEqual(note, 'Codul civil, changed: Art. 1112 (and 5 other provision(s))')


class SpanishArticles(unittest.TestCase):
    """Issues #9 and #10 on a small tree built here, laid out as spain-law is: a folder per norm under
    estatal/<rango>/<year>/<BOE id>/, article files named a<N>.md or by the publisher's block id (a1-37.md is art. 125
    of the Reglamento RD 1155/2024 approves), normas.tsv naming each norm, and the citation rule spain-law declared
    (its {n} is the file name, which no law text holds)."""

    LO = 'es/national/acts/estatal/ley-organica/2000/BOE-A-2000-544'
    RD = 'es/national/acts/estatal/real-decreto/2024/BOE-A-2024-24099'

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tests'))
        from test_law_fixtures import Tree, run
        t = cls.t = Tree()
        shutil.copy(ROOT / 'tools' / 'mcp_server.py', t.root / 'tools' / 'mcp_server.py')
        lo, rd = 'estatal/ley-organica/2000/BOE-A-2000-544', 'estatal/real-decreto/2024/BOE-A-2024-24099'
        es = t.corpus('es/national/acts')
        normas = ('id\trango\tpath\tfecha_disposicion\tfecha_publicacion\tfecha_actualizacion\tvigencia_agotada\t'
                  'estado_consolidacion\ttitulo\n'
                  f'BOE-A-2000-544\tLey Orgánica\t{lo}\t2000-01-11\t2000-01-12\t\tN\tFinalizado\tLey Orgánica 4/2000, de 11 '
                  'de enero, sobre derechos y libertades de los extranjeros en España y su integración social.\n'
                  f'BOE-A-2024-24099\tReal Decreto\t{rd}\t2024-11-19\t2024-11-20\t\tN\tFinalizado\tReal Decreto 1155/2024, '
                  'de 19 de noviembre, por el que se aprueba el Reglamento de la Ley Orgánica 4/2000.\n')
        es.commit('Ley Orgánica 4/2000', {
            'normas.tsv': normas,
            f'{lo}/README.md': '# Ley Orgánica 4/2000\n\n- [Artículo 31](a31.md)\n',
            f'{lo}/a1.md': '## Artículo 1. Delimitación del ámbito.\n\nTexto.\n',
            f'{lo}/a10.md': '## Artículo 10. Derecho al trabajo.\n\nTexto.\n',
            f'{lo}/a31.md': '## Artículo 31. Situación de residencia temporal.\n\n1. La residencia temporal.\n',
            f'{lo}/a31bis.md': '## Artículo 31 bis. Residencia temporal y trabajo de mujeres extranjeras.\n\nTexto.\n',
            f'{lo}/a34.md': '## Artículo 34. Documentación.\n\n> Su anterior numeración era art. 31.\n\nTexto.\n',
            f'{lo}/a63.md': '## Artículo 63. Procedimiento.\n\nConforme a lo dispuesto en el artículo 31.3 de esta Ley.\n'
                            'Y en el artículo 10 de la Ley 30/1992, de 26 de noviembre.\n',
        }, In_force='2000-02-01', Kind='law')
        es.commit('Real Decreto 1155/2024', {
            f'{rd}/a1.md': '## Artículo 1. Entrada por pasos fronterizos.\n\nTexto.\n',
            f'{rd}/a1-36.md': '## Artículo 124. Residencia por circunstancias excepcionales.\n\n1. De conformidad con lo '
                              'previsto en el artículo 31.3 de la Ley Orgánica 4/2000, de 11 de enero, la Administración.\n',
            f'{rd}/a1-37.md': '## Artículo 125. Tipos de autorización de residencia temporal por razones de arraigo.\n\nTexto.\n',
            f'{rd}/a1-38.md': '## Artículo 126. Requisitos.\n\nEn el artículo 31 bis de la Ley Orgánica 4/2000 y el '
                              'artículo 125 de este Reglamento.\n',
            f'{rd}/a1-39.md': '## Artículo 127. Requisitos específicos.\n\nEl artículo 31 de la Ley Orgánica 8/2000 no se aplica.\n',
        }, In_force='2025-05-20', Kind='law')
        # Audit row 63: norms cited by name or abbreviation, beside an older norm whose headings hold the same numbers
        # and words (a heading search found its article 155 for "artículo 155 de la Constitución").
        ce, lpac = 'estatal/constitucion/1978/BOE-A-1978-31229', 'estatal/ley/2015/BOE-A-2015-10565'
        cp, et = 'estatal/ley-organica/1995/BOE-A-1995-25444', 'estatal/real-decreto-legislativo/2015/BOE-A-2015-11430'
        old = 'estatal/ley/1970/BOE-A-1970-369'
        normas += (f'BOE-A-1978-31229\tConstitución\t{ce}\t1978-12-27\t1978-12-29\t\tN\tFinalizado\tConstitución Española.\n'
                   f'BOE-A-2015-10565\tLey\t{lpac}\t2015-10-01\t2015-10-02\t\tN\tFinalizado\tLey 39/2015, de 1 de octubre, del '
                   'Procedimiento Administrativo Común de las Administraciones Públicas.\n'
                   f'BOE-A-1995-25444\tLey Orgánica\t{cp}\t1995-11-23\t1995-11-24\t\tN\tFinalizado\tLey Orgánica 10/1995, '
                   'de 23 de noviembre, del Código Penal.\n'
                   f'BOE-A-2015-11430\tReal Decreto Legislativo\t{et}\t2015-10-23\t2015-10-24\t\tN\tFinalizado\tReal Decreto '
                   'Legislativo 2/2015, de 23 de octubre, por el que se aprueba el texto refundido de la Ley del Estatuto de '
                   'los Trabajadores.\n'
                   f'BOE-A-1970-369\tLey\t{old}\t1970-01-02\t1970-01-03\t\tN\tFinalizado\tLey 1/1970, de 2 de enero, de la '
                   'Constitución de cotos y de la protección de los cultivos.\n')
        es.commit('Norms cited by name', {
            'normas.tsv': normas,
            f'{ce}/a14.md': '## Artículo 14\n\nLos españoles son iguales ante la ley.\n',
            f'{ce}/a155.md': '## Artículo 155\n\n1. Si una Comunidad Autónoma no cumpliere las obligaciones.\n',
            f'{lpac}/a21.md': '## Artículo 21. Obligación de resolver.\n\nTexto.\n',
            f'{cp}/a31bis.md': '## Artículo 31 bis.\n\nTexto.\n',
            f'{et}/a48.md': '## Artículo 48. Suspensión con reserva de puesto de trabajo.\n\nTexto.\n',
            f'{et}/a4-3.md': '## Artículo 48 bis.\n\n1. Las personas trabajadoras tendrán derecho a un permiso parental.\n',
            f'{old}/a14.md': '## Art. 14. CE: Constitución de cotos.\n\nTexto.\n',
            f'{old}/a21.md': '## Artículo 21. Protección de los cultivos (Ley 39/2015).\n\nTexto.\n',
            f'{old}/a155.md': '## Artículo 155. De la Constitución de cotos.\n\nTexto.\n',
            f'{old}/a31bis.md': '## Artículo 31 bis. Del Código Penal.\n\nTexto.\n',
            f'{old}/a48bis.md': '## Artículo 48 bis. Estatuto de los Trabajadores del campo.\n\nTexto.\n',
        }, In_force='2016-10-02', Kind='law')
        (t.root / 'manifest.json').write_text(json.dumps({'corpora': [{
            'path': 'es/national/acts', 'code': 'ES', 'name': 'Spain', 'language': 'es',
            'citation': {'file': 'estatal/[a-z-]+/\\d{4}/(BOE-A-\\d{4}-\\d+)/([^/]+)\\.md', 'cites': '{n}'}}]}), encoding='utf-8')
        run('add', 'tools/mcp_server.py', cwd=t.root)
        t.pin()
        cls.proc = subprocess.Popen([sys.executable, str(t.root / 'tools' / 'mcp_server.py')], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=t.root,
                                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        cls.next_id = 0

    @classmethod
    def tearDownClass(cls):
        cls.proc.stdin.close()
        cls.proc.wait(timeout=30)
        cls.proc.stdout.close()
        cls.t.close()

    def call(self, name, **arguments):
        type(self).next_id += 1
        msg = {'jsonrpc': '2.0', 'id': self.next_id, 'method': 'tools/call', 'params': {'name': name, 'arguments': arguments}}
        self.proc.stdin.write((json.dumps(msg) + '\n').encode('utf-8'))
        self.proc.stdin.flush()
        r = json.loads(self.proc.stdout.readline().decode('utf-8'))['result']
        self.assertFalse(r.get('isError'), r)
        return r

    def found(self, query, scope):
        return [h['path'] for h in self.call('find_provision', query=query, jurisdiction=scope)['structuredContent']['results']]

    def test_find_an_article_by_its_heading_number(self):
        for q in ('artículo 31', 'articulo 31', 'art. 31', '31'):
            self.assertEqual(self.found(q, self.LO), [f'{self.LO}/a31.md'], q)
        self.assertEqual(self.found('31 bis', self.LO)[0], f'{self.LO}/a31bis.md')
        for q in ('artículo 125', 'art. 125', '125'):
            self.assertEqual(self.found(q, self.RD), [f'{self.RD}/a1-37.md'], q)  # a block id: only the heading numbers it

    def test_what_cites_an_article(self):
        r = self.call('what_else_changes', path=f'{self.LO}/a31.md')
        groups = r['structuredContent']['groups']
        cites = sorted(p['path'] for g in groups if g['kind'] == 'cites this provision' for p in g['provisions'])
        # From the Reglamento ("artículo 31.3 de la Ley Orgánica 4/2000") and within the law ("artículo 31.3 de esta
        # Ley"); not "31 bis", not another law's art. 31, not the publisher's note on a34.md, not the README link.
        self.assertEqual(cites, [f'{self.LO}/a63.md', f'{self.RD}/a1-36.md'])
        self.assertIn('artículo N de la <rango> n/aaaa', r['content'][0]['text'])
        r = self.call('what_else_changes', path=f'{self.RD}/a1-37.md')  # art. 125, cited within its own Reglamento
        self.assertEqual([p['path'] for g in r['structuredContent']['groups'] for p in g['provisions']], [f'{self.RD}/a1-38.md'])

    def test_resolve_spanish_citations(self):
        r = self.call('resolve_citations', text='El artículo 31.3 de la Ley Orgánica 4/2000, de 11 de enero; el art. 125 del '
                                                'Reglamento aprobado por Real Decreto 1155/2024; BOE-A-2000-544, art. 31 bis; '
                                                'artículo 3 de la Ley 99/2099.')
        paths = [c['path'] for c in r['structuredContent']['citations']]
        self.assertEqual(paths[:3], [f'{self.LO}/a31.md', f'{self.RD}/a1-37.md', f'{self.LO}/a31bis.md'])
        self.assertEqual(r['structuredContent']['citations'][3]['status'], 'not in the record at any date')

    def test_find_provision_reads_norm_and_article(self):
        # Audit row 63: find_provision read these as heading words and numbers and gave another norm's article first,
        # while resolve_citations resolved them. A citation is now read as resolve_citations reads it.
        ce, lpac = 'es/national/acts/estatal/constitucion/1978/BOE-A-1978-31229', 'es/national/acts/estatal/ley/2015/BOE-A-2015-10565'
        cp = 'es/national/acts/estatal/ley-organica/1995/BOE-A-1995-25444'
        et = 'es/national/acts/estatal/real-decreto-legislativo/2015/BOE-A-2015-11430'
        cited = {'artículo 21 de la Ley 39/2015': f'{lpac}/a21.md', 'artículo 155 de la Constitución': f'{ce}/a155.md',
                 'art. 14 CE': f'{ce}/a14.md', 'artículo 31 bis del Código Penal': f'{cp}/a31bis.md'}
        typed = {'Ley 39/2015 artículo 21': f'{lpac}/a21.md',  # the norm first, as a search is often typed
                 'Estatuto de los Trabajadores artículo 48 bis': f'{et}/a4-3.md'}  # a block id: its heading says 48 bis
        for q, want in {**cited, **typed}.items():
            self.assertEqual(self.found(q, 'es')[0], want, q)
            self.assertEqual(self.found(q, '')[0], want, q)
        r = self.call('resolve_citations', text='; '.join(cited))
        self.assertEqual([c['path'] for c in r['structuredContent']['citations']], list(cited.values()))
        # Not a citation, or one of an article the norm lacks: the heading search as before.
        self.assertEqual(self.found('artículo 31', self.LO), [f'{self.LO}/a31.md'])
        self.assertNotIn(f'{ce}/a999.md', self.found('artículo 999 de la Constitución', 'es'))


class RulesAndKinds(unittest.TestCase):
    """Audit rows 55 and 56 on a small tree built here. China and Japan cite articles in words (第二百六十三条,
    第十六条の二), with branch articles (之一, の二) that a plain rule would count; a corpus whose declared rule cannot be
    used says so, and is never searched with another layout's rule. laws_between and changes_between list laws taking
    effect only, as law.py laws does: a publisher's starting text and a correction are counted apart."""

    CN, JP, OLD, TX = 'cn/national/acts', 'jp/national/acts', 'zz/national/acts', 'tt/national/acts'

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tests'))
        from test_law_fixtures import Tree, run
        t = cls.t = Tree()
        shutil.copy(ROOT / 'tools' / 'mcp_server.py', t.root / 'tools' / 'mcp_server.py')
        criminal = {'xingfa/art-263.md': '# 第二百六十三条\n\n以暴力、胁迫或者其他方法抢劫公私财物的，处三年以上十年以下有期徒刑。\n',
                    'xingfa/art-263-1.md': '# 第二百六十三条之一\n\n另一条。\n',
                    'xingfa/art-267.md': '# 第二百六十七条\n\n携带凶器抢夺的，依照本法第二百六十三条的规定定罪处罚。\n',
                    'xingfa/art-268.md': '# 第二百六十八条\n\n依照本法第二百六十三条之一的规定处罚。\n',
                    'xingfa/art-1010.md': '# 第一千零一十条\n\n依照本法第二百六十三条之二的规定。\n'}
        for path in (cls.CN, cls.OLD):
            t.corpus(path).commit('中华人民共和国刑法', criminal, In_force='2021-03-01', Kind='law')
        t.corpus(cls.JP).commit('民法', {
            'minpo/art-090.md': '# 第九十条\n\n公の秩序又は善良の風俗に反する法律行為は、無効とする。\n',
            'minpo/art-090-2.md': '# 第九十条の二\n\n枝番号の条。\n',
            'minpo/art-091.md': '# 第九十一条\n\n第九十条の規定により無効とされた行為。\n',
            'minpo/art-092.md': '# 第九十二条\n\n商法第九十条の規定を準用する。\n',  # another law's article 90
            'minpo/art-093.md': '# 第九十三条\n\n第九十条の二の規定により。\n',  # the branch article 90-2
            'minpo/art-094.md': '# 第九十四条\n\n第九十条ノ二の規定による。\n'}, In_force='2020-04-01', Kind='law')  # older writing
        tx = t.corpus(cls.TX)
        tx.commit('Texas Legislative Council', {'code/s1.md': '# s1\nAs published.\n', 'code/s2.md': '# s2\nTwo.\n'},
                  In_force='2019-09-01', Kind='publisher')
        tx.commit('Texas Legislative Council', {'code/s1.md': '# s1\nAs published, corrected.\n'}, In_force='2019-09-01',
                  Kind='correction', Corrects='code 2019-09-01..2021-08-31', Files='code/s1.md', Reason='misprint')
        tx.commit('H.B. 7, 87th Leg.', {'code/s2.md': '# s2\nTwo, amended.\n'}, In_force='2021-09-01', Kind='law')
        old_cn = {'file': '([a-z]+)/art-0*([0-9]+)(?:-([0-9]+))?\\.md', 'cites': '第{n}条 (art-NNN-K.md: 第{n}条之{k})',
                  'numerals': 'zh-Hans: {n} is written in Chinese numerals'}  # China's rule before row 55: prose
        rules = {r['path']: r['citation'] for r in json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))['corpora']
                 if r['path'] in ('china/national/acts', 'japan/national/acts')}
        (t.root / 'manifest.json').write_text(json.dumps({'corpora': [
            {'path': cls.CN, 'code': 'CN', 'name': 'China', 'language': 'zh', 'citation': rules['china/national/acts']},
            {'path': cls.JP, 'code': 'JP', 'name': 'Japan', 'language': 'ja', 'citation': rules['japan/national/acts']},
            {'path': cls.OLD, 'code': 'ZZ', 'name': 'Old rule', 'language': 'zh', 'citation': old_cn},
            {'path': cls.TX, 'code': 'US-TX', 'name': 'Texas', 'language': 'en', 'history': 'current-only'}]}),
            encoding='utf-8')
        run('add', 'tools/mcp_server.py', cwd=t.root)
        t.pin()
        cls.proc = subprocess.Popen([sys.executable, str(t.root / 'tools' / 'mcp_server.py')], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=t.root,
                                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        cls.next_id = 0

    @classmethod
    def tearDownClass(cls):
        cls.proc.stdin.close()
        cls.proc.wait(timeout=30)
        cls.proc.stdout.close()
        cls.t.close()

    call = SpanishArticles.call

    def citing(self, path):
        r = self.call('what_else_changes', path=path, date='2026-11-01')
        return sorted(p['path'] for g in r['structuredContent']['groups'] if g['kind'] == 'cites this provision'
                      for p in g['provisions']), r

    def test_chinese_articles_cited_in_numerals(self):
        cites, _ = self.citing(f'{self.CN}/xingfa/art-263.md')
        self.assertEqual(cites, [f'{self.CN}/xingfa/art-267.md'])  # not 第二百六十三条之一 or 之二, not its own heading
        cites, _ = self.citing(f'{self.CN}/xingfa/art-263-1.md')
        self.assertEqual(cites, [f'{self.CN}/xingfa/art-268.md'])

    def test_japanese_articles_cited_in_kanji(self):
        cites, _ = self.citing(f'{self.JP}/minpo/art-090.md')
        self.assertEqual(cites, [f'{self.JP}/minpo/art-091.md'])  # not 商法第九十条, not 第九十条の二 or ノ二
        cites, _ = self.citing(f'{self.JP}/minpo/art-090-2.md')
        self.assertEqual(cites, [f'{self.JP}/minpo/art-093.md', f'{self.JP}/minpo/art-094.md'])

    def test_unusable_declared_rule_is_not_replaced(self):
        # The old rule is refused; the answer says citations were not searched, never "nothing cites it" from the
        # Swiss "Art. 263" rule.
        cites, r = self.citing(f'{self.OLD}/xingfa/art-263.md')
        self.assertEqual(cites, [])
        text = r['content'][0]['text']
        self.assertIn('Citations were not searched: citations in this corpus are not recognised', text)
        self.assertNotIn('No other provision in force', text)
        self.assertIn('cites pattern', r['structuredContent']['citations_not_searched'])

    def test_laws_between_lists_laws_only(self):
        r = self.call('laws_between', start='1900-01-01', end='2026-12-31', jurisdiction=self.TX)['structuredContent']
        self.assertEqual([c['law'] for c in r['changes']], ['H.B. 7, 87th Leg.'])
        self.assertEqual(r['not_laws'], {'baseline': 1, 'correction': 1})
        out, err, _ = self.t.cli('laws', '1900-01-01', '2026-12-31', self.TX)
        self.assertEqual([line.split()[-1] for line in out.splitlines() if line.strip()], ['Leg.'])
        self.assertIn('H.B. 7, 87th Leg.', out)
        self.assertIn('1 starting texts', out + err)
        self.assertIn('1 corrections', out + err)
        r = self.call('changes_between', date_a='2019-01-01', date_b='2026-12-31', jurisdiction=self.TX)
        row = r['structuredContent']['corpora'][0]
        self.assertEqual((row['laws'], row['not_laws']), (['H.B. 7, 87th Leg.'], {'baseline': 1, 'correction': 1}))
        self.assertIn('by 1 law(s)', r['content'][0]['text'])


class SpanishCitationRule(unittest.TestCase):
    """The parts of the Spanish reader that need no tree: article numbers from headings, lists, and which norm a
    clause names."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server
        cls.m = mcp_server

    def test_stem_and_heading_numbers(self):
        m = self.m
        self.assertEqual([m.stem_of(n) for n in ('a/a31.md', 'x/art59.md', 'x/art-0194.md', 'x/a1-37.md', 'x/1182.md')],
                         ['31', '59', '194', '1-37', '1182'])
        self.assertEqual([m.article_number(h) for h in ('Artículo 31. Situación', 'Artículo 31 bis. Residencia', 'Art. 4bis.',
                                                        'Artículo único.', 'Art. 16a', 'Artículo\xa0124.')],
                         ['31', '31 bis', '4 bis', None, None, '124'])

    def test_which_lines_cite(self):
        m = self.m
        norm = {'id': 'BOE-A-2015-10565', 'rango': 'Ley', 'numyear': '39/2015', 'date': '2015-10-01', 'title': ''}
        rx = m.es_norm_rx(norm, True)
        yes = ['previa resolución dictada en los términos previstos en el artículo 21 de la Ley 39/2015, de 1 de octubre.',
               'en los términos de los artículos 21 y 68 de la Ley 39/2015, de 1 de octubre.',
               'el artículo 68.1 de la Ley 39/2015, de 1 de octubre, y conforme al artículo 21 de dicha Ley.',
               'las referencias a los artículos 21.2 y 22 de la Ley 39/2015 se entenderán hechas.']
        no = ['los artículos 25.1.b) de la Ley 39/2015, de 1 de octubre, y 21.2 de este real decreto.',
              'el artículo 21 de la Ley 40/2015, de 1 de octubre.',
              'el artículo 21 bis de la Ley 39/2015.']
        self.assertEqual([m.es_cites(t, '21', norm, rx, False) is not None for t in yes + no], [True] * len(yes) + [False] * len(no))
        ce = {'id': 'BOE-A-1978-31229', 'rango': None, 'numyear': None, 'date': '1978-12-27', 'title': ''}
        rx = m.es_norm_rx(ce, True)
        self.assertIsNotNone(m.es_cites('de acuerdo con el artículo 103.1 de la Constitución Española.', '103', ce, rx, False))
        self.assertIsNone(m.es_cites('la autorización a que se refiere el artículo 103 para la constitución de gravámenes', '103', ce, rx, False))
        self.assertIsNone(m.es_cites('el artículo 122 de la Constitución reserva esta materia a la Ley Orgánica del Poder Judicial.',
                                     '122', {'id': 'BOE-A-1985-12666', 'rango': 'Ley Orgánica', 'numyear': '6/1985',
                                             'date': '1985-07-01', 'title': ''},
                                     m.es_norm_rx({'id': 'BOE-A-1985-12666', 'rango': 'Ley Orgánica', 'numyear': '6/1985',
                                                   'date': '1985-07-01', 'title': ''}, True), False))


SPAIN = 'spain/national/acts'


@needs(SPAIN)
class Spain(unittest.TestCase):
    """Issues #9 and #10 on spain-law itself: LO 4/2000 art. 31 is a31.md, RD 1155/2024 art. 125 is a1-37.md."""

    LO, RD = f'{SPAIN}/estatal/ley-organica/2000/BOE-A-2000-544', f'{SPAIN}/estatal/real-decreto/2024/BOE-A-2024-24099'

    @classmethod
    def setUpClass(cls):
        cls.s = Server()  # not narrowed: GLOBAL_LAW_JURISDICTIONS recurses on main (_look -> matches -> manifest)
        cls.s.send('initialize', {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '0'}})
        cls.s.send('notifications/initialized', notify=True)

    @classmethod
    def tearDownClass(cls):
        cls.s.close()

    def test_issue_examples(self):
        for q, scope, want in (('artículo 31', self.LO, 'a31.md'), ('31', self.LO, 'a31.md'), ('art. 31', self.LO, 'a31.md'),
                               ('artículo 125', self.RD, 'a1-37.md'), ('art. 125', self.RD, 'a1-37.md')):
            r = self.s.call('find_provision', query=q, jurisdiction=scope, max_results=3)
            self.assertEqual(r['structuredContent']['results'][0]['path'], f'{scope}/{want}', q)
        r = self.s.call('resolve_citations', text='Véase el artículo 124 del Real Decreto 557/2011 y el art. 127 del Reglamento '
                                                  'aprobado por Real Decreto 1155/2024. Ref. BOE-A-2000-544, art. 31.')
        self.assertEqual([c['path'] for c in r['structuredContent']['citations']],
                         [f'{SPAIN}/estatal/real-decreto/2011/BOE-A-2011-7703/a124.md', f'{self.RD}/a1-39.md', f'{self.LO}/a31.md'])
        r = self.s.call('what_else_changes', path=f'{self.LO}/a31.md')
        cites = {p['path'] for g in r['structuredContent']['groups'] for p in g['provisions']}
        self.assertTrue({f'{self.RD}/a1-36.md', f'{self.RD}/a1-85.md', f'{self.RD}/da-20.md', f'{self.RD}/da-21.md'} <= cites, cites)


ROMANIA = 'romania/national/acts'


@unittest.skipUnless((ROOT / ROMANIA / '.git').exists(), 'Romania is not checked out (python tools/countries.py add romania)')
class Romania(unittest.TestCase):
    """A corpus that grows append-only: acts moved to new folders (November 2026), corrections appended as new
    versions by the maintainer, credits corrected in data/credits.csv, acts withdrawn, and 137,000 files."""

    @classmethod
    def setUpClass(cls):
        cls.s = Server(GLOBAL_LAW_JURISDICTIONS='romania')
        cls.s.send('initialize', {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '0'}})
        cls.s.send('notifications/initialized', notify=True)

    @classmethod
    def tearDownClass(cls):
        cls.s.close()

    def first(self, query):
        r = self.s.call('find_provision', query=query)
        self.assertFalse(r.get('isError'), r)
        return [h['path'] for h in r['structuredContent']['results']]

    def test_find_by_act_citation_and_by_code_name(self):
        self.assertEqual(self.first('Legea nr. 31/1990 art. 194')[0], f'{ROMANIA}/lege/1990/31/art-194.md')
        self.assertEqual(self.first('OUG 195/2002 art. 102')[0], f'{ROMANIA}/oug/2002/195/art-102.md')  # not OUG 194/2002
        self.assertEqual(self.first('art. 6^1 Legea 31/1990')[0], f'{ROMANIA}/lege/1990/31/art-006-1.md')
        self.assertEqual(self.first('art. 1.357 Codul civil')[0], f'{ROMANIA}/lege/2009/287/art-1357.md')
        self.assertEqual(self.first('legea societatilor art 10')[0], f'{ROMANIA}/lege/1990/31/art-010.md')
        self.assertEqual(self.first('Codul de procedura civila art. 194')[0], f'{ROMANIA}/lege/2010/134/art-0194.md')
        self.assertEqual(self.first('codul fiscal')[0], f'{ROMANIA}/lege/2015/227')  # the code in force first
        self.assertEqual(self.first('Legea 31/1990'), [f'{ROMANIA}/lege/1990/31'])

    def test_find_by_the_title_under_a_heading(self):
        self.assertIn(f'{ROMANIA}/lege/2009/287/art-1112.md', self.first('prezumtia de renuntare')[:3])

    def test_a_moved_act_keeps_its_history(self):
        r = self.s.call('provision_history', path=f'{ROMANIA}/lege/1990/31/art-010.md')
        self.assertFalse(r.get('isError'), r)
        rows = r['structuredContent']['changes']
        self.assertGreaterEqual(len(rows), 8)
        self.assertEqual((rows[0]['in_force'], rows[0]['law']), ('1990-12-17', 'Legea nr. 31/1990'))
        r = self.s.call('read_law', path=f'{ROMANIA}/lege/2009/287/art-1112.md', date='2014-10-18')
        self.assertIn('ca urmare a citării sale', r['structuredContent']['text'])
        self.assertEqual(r['structuredContent']['last_change']['law'], 'Legea nr. 71/2011')

    def test_cites_the_publishers_text_in_force_on_the_date(self):
        r = self.s.call('read_law', path=f'{ROMANIA}/lege/2009/287/art-1112.md', date='2014-10-18', include_text=False)
        cite = r['structuredContent']['cite']
        self.assertEqual(cite['official_url'], 'https://legislatie.just.ro/Public/DetaliiDocument/137240')  # not the archive copy
        self.assertTrue(cite['archived_copies'][0].startswith('https://web.archive.org/'))
        self.assertEqual(cite['pincite'], 'Articolul 1112, Codul civil (Legea nr. 287/2009), as in force on 2014-10-18')
        self.assertTrue(r['content'][0]['text'].splitlines()[1].startswith('Official text: https://legislatie.just.ro/'))
        # The wording in force today: the act's own page (its current consolidated text), not the code as published.
        r = self.s.call('read_law', path=f'{ROMANIA}/lege/2009/287/art-1349.md', include_text=False)
        self.assertEqual(r['structuredContent']['cite']['official_url'], 'https://legislatie.just.ro/Public/DetaliiDocument/109884')
        r = self.s.call('resolve_citations', date='2026-01-01', text='art. 194 alin. (1) din Legea nr. 31/1990')
        # Still today's wording: the act's own page, as read_law gives it.
        self.assertEqual(r['structuredContent']['citations'][0]['cite']['official_url'], 'https://legislatie.just.ro/Public/DetaliiDocument/798')

    def test_a_correction_by_the_maintainer_is_a_version(self):
        r = self.s.call('provision_history', path=f'{ROMANIA}/lege/2013/300/art-001.md')
        rows = r['structuredContent']['changes']
        self.assertTrue(any(h.get('restates', '').startswith('9fdd8bee') for h in rows), rows)
        self.assertNotIn('Lexifina', [h['law'] for h in rows])
        r = self.s.call('read_law', path=f'{ROMANIA}/lege/2013/300/art-001.md', date='2013-12-20')
        self.assertFalse(r['structuredContent']['in_force'])  # art. I took effect on 26 December 2013

    def test_a_corrected_credit_is_used(self):
        r = self.s.call('provision_history', path=f'{ROMANIA}/oug/2003/19/art-003.md')
        same_day = [h for h in r['structuredContent']['changes'] if h['in_force'] == '2008-06-26']
        self.assertTrue(same_day and all(h['law'] == 'OUG nr. 81/2008' for h in same_day), same_day)

    def test_romanian_citations_resolve(self):
        r = self.s.call('resolve_citations', date='2026-01-01', text=(
            'art. 1.357 din Codul civil, art. 1349 C. civ., art. 194 alin. (1) din Legea nr. 31/1990, '
            'art. 16 din Constituție'))
        paths = [c['path'] for c in r['structuredContent']['citations']]
        self.assertEqual(paths, [f'{ROMANIA}/lege/2009/287/art-1357.md', f'{ROMANIA}/lege/2009/287/art-1349.md',
                                 f'{ROMANIA}/lege/1990/31/art-194.md', f'{ROMANIA}/constitutie/1991/art-016.md'])

    def test_whole_country_on_a_past_date_and_search_without_diacritics(self):
        r = self.s.call('search_law', query='raspundere limitata', date='2005-01-01', jurisdiction='romania')
        self.assertFalse(r.get('isError'), r)
        self.assertIn(f'{ROMANIA}/lege/1990/31/art-002.md', r['content'][0]['text'])
        r = self.s.call('world_on_date', date='2010-06-01')
        self.assertFalse(r.get('isError'), r)


class DescriptionExamplesResolve(unittest.TestCase):
    """Audit row 89: the tool descriptions, the instructions and the prompts are the only paths a model sees before it
    calls, so every example path or scope in them is a path of the tree now: a manifest corpus, a folder above one, or
    a file or folder inside one, written as the manifest writes it, never through an alias (iso_path, LEGACY_CORPORA,
    LEGACY_FOLDERS) that the server would quietly widen or move."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server
        cls.corpora = _corpus_paths()

    def texts(self) -> list[tuple[str, str]]:
        """(where, text) for every description a client is shown."""
        r = self.m.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list', 'params': {}})['result']
        out = [('instructions', self.m.INSTRUCTIONS)]
        for tool in r['tools']:
            out.append((tool['name'], tool['description']))
            for name, prop in tool['inputSchema'].get('properties', {}).items():
                out.append((f"{tool['name']}.{name}", prop.get('description', '')))
        for name, (_, desc, prompt_args, text) in self.m.PROMPTS.items():
            out += [(f'prompt {name}', desc), (f'prompt {name} text', text)]
            out += [(f"prompt {name}.{a['name']}", a.get('description', '')) for a in prompt_args]
        r = self.m.handle({'jsonrpc': '2.0', 'id': 2, 'method': 'resources/templates/list', 'params': {}})['result']
        out += [('resource template', t.get('description', '')) for t in r['resourceTemplates']]
        return out

    def examples(self) -> list[tuple[str, str, str]]:
        """(where, kind, example): every path-like word, and every quoted scope of a jurisdiction argument."""
        found = []
        for where, text in self.texts():
            text = text.replace('global-law://law/', ' ')
            for word in re.findall(r'(?<![\w/:.-])([a-z][a-z0-9-]*(?:/[\w.-]+)+)', text):
                if word.endswith('.') and not re.search(r'/[\w-]*\d\.$', word):  # a sentence's full stop
                    word = word[:-1]
                found.append((where, 'file' if word.endswith('.md') else 'path', word))
            if where.endswith(('.jurisdiction', '.corpus')):
                found += [(where, 'scope', q) for q in re.findall(r'"([^"\s]+)"', text)]
        return found

    def test_there_are_examples_to_check(self):
        kinds = {k for _, k, _ in self.examples()}
        self.assertEqual(kinds, {'file', 'path', 'scope'})

    def test_every_example_is_a_path_of_the_tree_now(self):
        for where, kind, ex in self.examples():
            with self.subTest(where=where, example=ex):
                self.assertEqual(self.m.here(ex), ex, f'{where}: {ex!r} is an alias of {self.m.here(ex)!r}')
                inside = [c for c in self.corpora if ex == c or ex.startswith(c + '/')]
                above = [c for c in self.corpora if c.startswith(ex.rstrip('/') + '/')]
                self.assertTrue(inside or above, f'{where}: {ex!r} is no corpus, folder above one, or path in one')
                if kind == 'file':
                    self.assertTrue(inside, f'{where}: {ex!r} is not inside a corpus')

    def test_example_files_are_in_their_corpus(self):
        """Checked against the corpus's checkout where it is here (a clone may hold only some countries)."""
        for where, kind, ex in self.examples():
            if kind == 'scope':
                continue
            corpus = max((c for c in self.corpora if ex == c or ex.startswith(c + '/')), key=len, default=None)
            if corpus is None or not _checked_out(corpus) or ex == corpus:
                continue
            rel = ex[len(corpus) + 1:]
            with self.subTest(where=where, example=ex):
                names = subprocess.run(['git', '-C', str(ROOT / corpus), 'ls-tree', '-r', '--name-only', 'HEAD'],
                                       capture_output=True, encoding='utf-8').stdout.splitlines()
                self.assertTrue(any(n == rel or n.startswith(rel) for n in names), f'{where}: {ex!r} names no file')

    def test_scopes_scope_what_they_say(self):
        """A scope example is a country or level above corpora, a corpus, or a folder in one; never an old corpus
        path the server widens to a bigger corpus (gb/uk/send meant all UK legislation)."""
        for where, kind, ex in self.examples():
            if kind != 'scope':
                continue
            with self.subTest(where=where, example=ex):
                self.assertEqual(self.m.here(ex), ex, f'{where}: {ex!r} is an alias of {self.m.here(ex)!r}')
                self.assertTrue(any(self.m.scoped(c, ex) is not None for c in self.corpora), ex)


class DocFigures(unittest.TestCase):
    """Audit row 92: limits stated in README.md and MCP.md are marked spans written from the server's constants by
    tools/doc_figures.py; a constant changed without rerunning it fails here."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import doc_figures
        cls.d = doc_figures

    def test_every_marked_figure_is_current(self):
        self.assertEqual(self.d.run(check=True), [], 'run python tools/doc_figures.py')

    def test_a_stale_or_unknown_figure_is_found(self):
        values = self.d.figures()
        new, found = self.d.rewrite('<!-- fig:text_limit -->299<!-- /fig --> and <!-- fig:nothing -->1<!-- /fig -->',
                                    values)
        self.assertEqual(len(found), 2, found)
        self.assertIn(f'<!-- fig:text_limit -->{values["text_limit"]}<!-- /fig -->', new)

    def test_every_stated_text_limit_is_one_mcp_md_gives(self):
        """The text limit and its one exception are in MCP.md, and no tool states another."""
        values = self.d.figures()
        mcp = (ROOT / 'MCP.md').read_text(encoding='utf-8')
        self.assertIn(f'<!-- fig:text_limit -->{values["text_limit"]}<!-- /fig -->', mcp)
        self.assertIn(f'<!-- fig:brief_limit -->{values["brief_limit"]}<!-- /fig -->', mcp)
        import mcp_server
        r = mcp_server.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list', 'params': {}})['result']
        stated = {f'{int(n):,}' for t in r['tools'] for p in t['inputSchema']['properties'].values()
                  for n in re.findall(r'Up to (\d+) characters', p.get('description', ''))}
        self.assertTrue(stated and stated <= {values['text_limit'], values['brief_limit']}, stated)

    def test_no_server_limit_typed_by_hand(self):
        """The constants the documents state appear only inside marks: a figure typed by hand drifts."""
        values = self.d.figures()
        for name in self.d.DOCS:
            text = self.d.SPAN.sub('', (ROOT / name).read_text(encoding='utf-8'))
            for fig in ('text_limit', 'brief_limit', 'page_chars', 'answer_chars', 'words_max'):
                with self.subTest(doc=name, figure=fig):
                    self.assertNotRegex(text, rf'\b{re.escape(values[fig])} characters', f'{name}: {fig} typed by hand')


class ListJurisdictionsExample(unittest.TestCase):
    """Audit row 91: list_jurisdictions' example path is a provision, and a corpus's own notes at its root
    (CHANGES.md) are not counted as provision files."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        shutil.copy(ROOT / 'tools' / 'mcp_server.py', t.root / 'tools' / 'mcp_server.py')
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        run('add', 'jurisdiction.json', cwd=t.root)
        c = t.corpus('aa/federal/code')
        c.commit('Act 1 of 2010', {'CHANGES.md': '# Changes\n', 'title-1/1.md': 'Words.\n'}, In_force='2010-01-01',
                 Kind='law')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def test_example_is_a_provision_and_notes_are_not_counted(self):
        code = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
                'r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
                '"params": {"name": "list_jurisdictions", "arguments": {}}})["result"]\n'
                'print(json.dumps(r["structuredContent"]["corpora"]))\n')
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', code], cwd=self.t.root, capture_output=True,
                              encoding='utf-8', timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        row = next(c for c in json.loads(done.stdout) if c['path'] == 'aa/federal/code')
        self.assertEqual(row['example_path'], 'aa/federal/code/title-1/1.md')
        self.assertEqual(row['provision_files'], 1)



def _stub_forms(m):
    """Every registered citation form with a stub path, so the forms are checked on their words alone."""
    return [m.CitationForm(f.country, f.rx, lambda _m, c=f.country: f'{c}/x.md', f.examples, f.open_name) for f in m.CITATION_REGISTRY]


class TestCrossCountryCitations(unittest.TestCase):
    """Audit row 67, and the cause of rows 67 and 68: each country's citation forms were written and tested alone, but
    every form runs over every text. Each form is now declared with its country and examples (CITATION_REGISTRY), and
    every example must be claimed by its own country's forms and by no other country's, except the overlaps listed in
    CITATION_OVERLAPS, which citations_in() settles by the name the citation carries."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def countries(self, text):
        from unittest import mock
        with mock.patch.object(self.m, 'citation_served', lambda c: False):  # no corpus decides: the words alone
            return {h['country'] for h in self.m.citations_in(text, _stub_forms(self.m))}

    def test_every_example_is_claimed_by_its_own_country_only(self):
        forms = self.m.CITATION_REGISTRY
        listed = {(ex, mine, other) for (mine, other), exs in self.m.CITATION_OVERLAPS.items() for ex in exs}
        seen = set()
        for f in forms:
            self.assertTrue(f.examples, f'a {f.country} form has no examples')
            for ex in f.examples:
                self.assertTrue(f.rx.search(ex), f'{f.country} form does not read its own example {ex!r}')
                for other in {g.country for g in forms if g.country != f.country and g.rx.search(ex)}:
                    self.assertIn((ex, f.country, other), listed, f'{other} forms also read the {f.country} citation {ex!r}')
                    seen.add((ex, f.country, other))
                self.assertEqual(self.countries(ex), {f.country}, ex)
        self.assertEqual(listed - seen, set(), 'CITATION_OVERLAPS lists overlaps that no longer happen')

    def test_austrian_acts_by_abbreviation(self):
        """#21: the federal acts beyond B-VG and DSG, and Burgenland's, by RIS's abbreviation; an abbreviation German
        acts share stays German (the words alone cannot say "§ 242 StPO" is Austrian)."""
        from unittest import mock
        def paths(text):
            with mock.patch.object(self.m, 'citation_served', lambda c: False):
                return [(h['country'], h['path']) for h in self.m.citations_in(text)]
        self.assertEqual(paths('§§ 1293, 1295 ABGB'), [('at', 'austria/bund/acts/abgb/par-1293.md'),
                                                         ('at', 'austria/bund/acts/abgb/par-1295.md')])
        self.assertEqual(paths('§ 16 Abs 1 Z 3 MRG'), [('at', 'austria/bund/acts/mrg/par-0016.md')])
        self.assertEqual(paths('§ 2 EStG 1988')[0], ('at', 'austria/bund/acts/estg-1988/par-0002.md'))
        self.assertEqual(paths('§ 5 Bgld BauG'), [('at', 'austria/burgenland/acts/baug/par-0005.md')])
        self.assertNotIn('at', {c for c, _ in paths('§ 242 StPO')})
        self.assertNotIn('at', {c for c, _ in paths('Art. 106 Abs. 1 StGB')})

    def test_spain_does_not_take_mexican_or_argentine_citations(self):
        text = ('Conforme al artículo 1 de la Constitución Política de los Estados Unidos Mexicanos y al artículo 14 de la '
                'Ley Orgánica del Poder Judicial de la Federación, en relación con el artículo 1910 del Código Civil para el '
                'Distrito Federal, el artículo 222 de la LGS (Ley General de Salud), el artículo 1716 del Código Civil y '
                'Comercial de la Nación y el artículo 14 de la Constitución Nacional.')
        self.assertNotIn('es', self.countries(text))
        for one in ('artículo 1 de la Constitución Política de los Estados Unidos Mexicanos',
                    'artículo 14 de la Ley Orgánica del Poder Judicial de la Federación',
                    'artículo 1910 del Código Civil para el Distrito Federal', 'artículo 1716 del Código Civil y Comercial de la Nación',
                    'artículo 24 de la Constitución Política de Colombia', 'artículo 222 de la LGS (Ley General de Salud)'):
            self.assertNotIn('es', self.countries(one), one)
            self.assertFalse([h for h in self.m.citations_in(one) if h['path'].startswith('spain/')], one)
        # Spain's own citations still read as Spain's.
        for one in ('artículo 14 de la Constitución Española', 'artículo 14 de la Constitución', 'art. 9 LGS',
                    'artículo 1902 del Código Civil, que', 'artículo 14 de la Ley Orgánica del Poder Judicial.'):
            self.assertEqual(self.countries(one), {'es'}, one)

    def test_served_corpora_decide_when_the_words_do_not(self):
        from unittest import mock
        rx = re.compile(r'art\. (\d+) X')
        forms = [self.m.CitationForm('aa', rx, lambda m: 'aa/x.md', ('art. 1 X',)), self.m.CitationForm('bb', rx, lambda m: 'bb/x.md', ('art. 1 X',))]
        for served, want in (({'aa'}, {'aa'}), ({'bb'}, {'bb'}), (set(), {'aa', 'bb'}), ({'aa', 'bb'}, {'aa', 'bb'})):
            with mock.patch.object(self.m, 'citation_served', lambda c: c in served):
                self.assertEqual({h['country'] for h in self.m.citations_in('see art. 1 X', forms)}, want, served)
                self.assertEqual({h['country'] for h in self.m.citations_in('see art. 1 X', forms[::-1])}, want, served)  # never the order


class TestRomanianCitations(unittest.TestCase):
    """Audit row 68: Moldovan citations were answered with Romania's acts."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def test_moldova_not_romania(self):
        from unittest import mock
        text = ('Potrivit art. 16 din Constituția Republicii Moldova și art. 5 din Codul civil al Republicii Moldova, '
                'instanța a reținut încălcarea art. 2 din Codul penal al RM.')
        with mock.patch.object(self.m, 'citation_served', lambda c: True):
            self.assertEqual({h['country'] for h in self.m.citations_in(text, _stub_forms(self.m))}, {'md'})
            self.assertEqual({h['country'] for h in self.m.citations_in('art. 16 din Constituția României', _stub_forms(self.m))}, {'ro'})
        self.assertFalse([p for _, p, _ in self.m.ro_citations(text) if p.startswith('romania/')])
        if _checked_out('moldova/national/acts'):
            found = self.m.ro_citations('art. 16 din Constituția Republicii Moldova')
            self.assertEqual([p for _, p, _ in found], ['moldova/national/acts/constitutia/art-016.md'])
        if _checked_out(RO_C):  # Romania's own still resolve
            self.assertEqual([p for _, p, _ in self.m.ro_citations('art. 16 din Constituția României')],
                             [f'{RO_C}/constitutie/1991/art-016.md'])


class TestSpanishCitations(unittest.TestCase):
    """Audit rows 69 and 72: "art. 1.902 CC" is article 1902 (a thousands point), and lists ("artículos 14 y 24 de la
    Constitución Española", "arts. 1902 y 1903 CC") give every article in them."""

    CC, CE, LO = 'f/cc', 'f/ce', 'f/lo'

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def cite(self, text):
        from unittest import mock
        norms = {self.CC: {'id': 'BOE-A-1889-4763', 'rango': 'Real Decreto', 'numyear': None, 'date': '1889-07-24', 'title': ''},
                 self.CE: {'id': 'BOE-A-1978-31229', 'rango': None, 'numyear': None, 'date': '1978-12-27', 'title': ''},
                 self.LO: {'id': 'BOE-A-2000-544', 'rango': 'Ley Orgánica', 'numyear': '4/2000', 'date': '2000-01-11', 'title': ''}}
        arts = {self.CC: {n: [f'{self.CC}/art{n}.md'] for n in ('1', '1101', '1902', '1903', '1968')},
                self.CE: {n: [f'{self.CE}/a{n}.md'] for n in ('9', '14', '24', '103')},
                self.LO: {'31': [f'{self.LO}/a31.md']}}
        with mock.patch.object(self.m, 'es_corpus', lambda: ('es', 'sha')), \
                mock.patch.object(self.m, 'es_norms', lambda c, s: norms), \
                mock.patch.object(self.m, 'article_files', lambda c, s, f: arts[f]), \
                mock.patch.object(self.m, 'citation_served', lambda c: c == 'es'), \
                mock.patch.object(self.m, 'here', lambda p: p):
            return [h['path'] for h in self.m.citations_in(text) if h['country'] == 'es']

    def test_thousands_separator(self):
        self.assertEqual(self.cite('art. 1.902 del Código Civil'), [f'es/{self.CC}/art1902.md'])
        self.assertEqual(self.cite('el artículo 1.968.2 del Código Civil fija el plazo'), [f'es/{self.CC}/art1968.md'])
        self.assertEqual(self.cite('véase también el art. 1.101 CC.'), [f'es/{self.CC}/art1101.md'])
        self.assertEqual(self.cite('artículo 31.3 de la Ley Orgánica 4/2000'), [f'es/{self.LO}/a31.md'])  # an apartado
        self.assertEqual(self.cite('artículo 9.3 CE'), [f'es/{self.CE}/a9.md'])
        self.assertEqual(self.cite('art. 1.500 CC'), [f'es/{self.CC}/art1.md'])  # no article 1500 here: article 1, apartado 500
        if _checked_out(SPAIN):
            cc = 'spain/national/acts/estatal/real-decreto/1889/BOE-A-1889-4763'
            self.assertEqual([h['path'] for h in self.m.citations_in('art. 1.902 del Código Civil')], [f'{cc}/art1902.md'])
            self.assertEqual([h['path'] for h in self.m.citations_in('artículo 1.968.2 del Código Civil')], [f'{cc}/art1968.md'])

    def test_article_lists(self):
        self.assertEqual(self.cite('La sentencia vulnera los artículos 14 y 24 de la Constitución Española.'),
                         [f'es/{self.CE}/a14.md', f'es/{self.CE}/a24.md'])
        self.assertEqual(self.cite('y los arts. 1902 y 1903 CC.'), [f'es/{self.CC}/art1902.md', f'es/{self.CC}/art1903.md'])
        self.assertEqual(self.cite('Véanse también los artículos 9.3 y 103.1 CE.'), [f'es/{self.CE}/a9.md', f'es/{self.CE}/a103.md'])
        self.assertEqual(self.cite('artículos 9, 14 y 24 CE'), [f'es/{self.CE}/a{n}.md' for n in (9, 14, 24)])
        if _checked_out(SPAIN):
            ce = 'spain/national/acts/estatal/constitucion/1978/BOE-A-1978-31229'
            self.assertEqual([h['path'] for h in self.m.citations_in('artículos 14 y 24 de la Constitución Española')],
                             [f'{ce}/a14.md', f'{ce}/a24.md'])


class TestAustralianCitations(unittest.TestCase):
    """Audit row 70: the Corporations Regulations' lettered chapters and parts, and a citation ending a sentence."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def test_letter_parts_and_full_stop(self):
        cite = lambda text: [p.rsplit('/', 1)[1] for rx, to in self.m.CITATION_FORMS for m in rx.finditer(text)
                             for p in self.m.as_paths(to(m)) if 'corporations-regulations' in p]
        self.assertEqual(cite('the disclosure exemption in reg 6D.2.01'), ['r-6D.2.01.md'])
        self.assertEqual(cite('the relief in regulation 7.5A.73 and r 5C.11.01'), ['r-7.5A.73.md', 'r-5C.11.01.md'])
        self.assertEqual(cite('reg 2M.3.03 applies'), ['r-2M.3.03.md'])
        self.assertEqual(cite('signed in accordance with regulation 1.0.11.'), ['r-1.0.11.md'])
        self.assertEqual(cite('The fee is payable under reg 7.1.04. It'), ['r-7.1.04.md'])
        for text in ('regulation 2.1 of the EU Regulation', 'reg 6.10.01.5', 'reg 3.4 applies'):
            self.assertEqual(cite(text), [], text)


class TestMaltaCitations(unittest.TestCase):
    """Audit row 71: an instrument recorded as one file (sl/<n>/title.md) holds the regulation cited."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def test_single_file_instrument(self):
        from unittest import mock
        names = ('sl/10.1/title.md', 'sl/586.8/title.md', 'sl/586.8/15.md')
        with mock.patch.object(self.m, 'malta_corpus', lambda: 'mt/x'), \
                mock.patch.object(self.m, 'corpus_head', lambda c: 'sha'), \
                mock.patch.object(self.m, 'names_of', lambda c, s: names), \
                mock.patch.object(type(ROOT), 'exists', lambda self: True), \
                mock.patch.object(self.m, 'here', lambda p: p):
            hits = self.m.citations_in('Permits are refused under regulation 3 of S.L. 10.01 and reg. 15 of S.L. 586.08.')
        self.assertEqual([h['path'] for h in hits], ['mt/x/sl/10.1/title.md', 'mt/x/sl/586.8/15.md'])
        self.assertIn('provision 3 is inside it', hits[0]['note'])
        self.assertIsNone(hits[1]['note'])
        if _checked_out(MT_C):
            text, data = self.m.t_resolve_citations({'text': 'Permits are refused under regulation 3 of S.L. 10.01.', 'date': '2026-11-01'})
            c = data['citations'][0]
            self.assertEqual(c['path'], f'{MT_C}/sl/10.1/title.md')
            self.assertNotEqual(c['status'], 'not in the record at any date')
            self.assertIn('is inside it', text)


class TestCitationFor(unittest.TestCase):
    """Audit row 73: a provision with no "#" heading (all of Mexico's) is cited by the number it opens with."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def test_heading_from_first_line(self):
        from unittest import mock
        with mock.patch.object(self.m.law, 'corpus_of', lambda p: ('mexico/national/acts', p.split('acts/', 1)[1])), \
                mock.patch.object(self.m, 'act_title', lambda c, r: 'Ley Federal del Trabajo'), \
                mock.patch.object(self.m.law, 'corpus_info', lambda c: {}), \
                mock.patch.object(self.m, 'provision_link', lambda *a: None), \
                mock.patch.object(self.m, 'act_portals', lambda *a: {}), \
                mock.patch.object(self.m, 'corpus_head', lambda c: 'sha'):
            for text, want in (('Artículo 49.- La persona empleadora ...', 'Artículo 49'), ('Artículo 46 Bis.- ...', 'Artículo 46 Bis'),
                               ('Artículo 4o.- Toda persona ...', 'Artículo 4o'), ('\nArtículo 15 A.- ...', 'Artículo 15 A')):
                cite = self.m.citation_for('mexico/national/acts/ley-federal-del-trabajo/art-0049.md', '2026-11-06', None, text)
                self.assertTrue(cite['pincite'].startswith(want + ','), cite['pincite'])
                self.assertNotIn('art-0049', cite['pincite'])
            # A "#" heading still decides, and a text with neither keeps the file's name.
            self.assertTrue(self.m.citation_for('mexico/national/acts/x/art-1.md', '2026-11-06', None,
                                                '# Art. 1 Objeto\nArtículo 2')['pincite'].startswith('Art. 1 Objeto,'))
            self.assertTrue(self.m.citation_for('mexico/national/acts/x/art-1.md', '2026-11-06', None,
                                                'Transitorio único')['pincite'].startswith('art-1,'))


class TestResolveCitations(unittest.TestCase):
    """Audit row 74 (its silent cap): citations past max_results are counted and named, never dropped without a word."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def test_limit_is_reported(self):
        from unittest import mock
        text = ' '.join(f'See 11 U.S.C. § {100 + i}.' for i in range(12))
        with mock.patch.object(self.m, 'citation_state', lambda d, p: {'status': 'in force'}), \
                mock.patch.object(self.m, 'here', lambda p: p):
            said, data = self.m.t_resolve_citations({'text': text, 'max_results': 10, 'date': '2026-11-01'})
            self.assertEqual(len(data['citations']), 10)
            self.assertEqual(data['not_looked_up'], 2)
            self.assertIn('2 more citation(s) not looked up', said)
            self.assertIn('11 U.S.C. § 110', said)  # the first left out, named
            said, data = self.m.t_resolve_citations({'text': text, 'max_results': 20, 'date': '2026-11-01'})
            self.assertEqual(data['not_looked_up'], 0)
            self.assertNotIn('not looked up', said)


IE_C, FI_TT = 'ireland/national/acts', 'finland/tyotuomioistuin/caselaw'
DPA = f'{IE_C}/data-protection-act-2018'
EFFECTS_SHORT = 'the text shown may not be the whole law that applied'


class TestToolSurface(unittest.TestCase):
    """What a model or an API caller sees (2026-11-10): `summary` is a headline, lists come in parts (`offset`, `page`),
    read_law reads several provisions, an act found by name is one row, the note on what a record does not hold is one
    sentence said once, `kind` and `jurisdiction` are read alike everywhere, and a hosted server names no command."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def call(self, tool, **args):
        r = self.m.answer({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': tool, 'arguments': args}})
        self.assertIn('result', r, r)
        return r['result']

    def ok(self, tool, **args):
        res = self.call(tool, **args)
        self.assertFalse(res.get('isError'), res['content'][0]['text'])
        return res['content'][0]['text'], res['structuredContent']

    def err(self, tool, **args):
        res = self.call(tool, **args)
        self.assertTrue(res.get('isError'), res['content'][0]['text'][:200])
        return res['content'][0]['text']

    # --- no corpus needed ---

    def test_page_of(self):
        m = self.m
        self.assertEqual(m.page_of(10, 10, 0), {'total': 10, 'shown': 10, 'offset': 0, 'next_offset': None})
        self.assertEqual(m.page_of(25, 10, 10), {'total': 25, 'shown': 10, 'offset': 10, 'next_offset': 20})
        self.assertEqual(m.page_of(None, 10, 0, at_least=45),
                         {'total': None, 'shown': 10, 'offset': 0, 'next_offset': 10, 'total_at_least': 45})
        self.assertEqual(m.more_note(m.page_of(10, 10, 0)), '')
        self.assertIn('pass offset 20 for the next', m.more_note(m.page_of(25, 10, 10)))
        with self.assertRaises(m.UserError):
            m.offset_arg({'offset': -1})
        with self.assertRaises(m.UserError):
            m.offset_arg({'offset': 30}, 25)

    def test_natural_order_and_act_ties(self):
        m = self.m
        self.assertEqual(sorted(['section-10.md', 'section-2.md', 'section-1.md', 'long-title.md'], key=m.natural),
                         ['long-title.md', 'section-1.md', 'section-2.md', 'section-10.md'])
        scores = {f'data-protection-act-2018/section-{i}.md': 3 for i in range(1, 6)}
        scores.update({'data-protection-act-2018/section-2.md': 13, 'other-act/section-1.md': 1})
        ties = m.act_ties(scores, set(), ['data', 'protection', 'act'])
        self.assertEqual(list(ties), ['data-protection-act-2018'])
        self.assertEqual((ties['data-protection-act-2018'][0], len(ties['data-protection-act-2018'][1])), (3, 4))
        self.assertEqual(m.act_ties(scores, set(scores), ['data']), {})  # matched by their headings: not the act's name

    def test_case_law_left_out_is_that_of_the_scope(self):
        m = self.m
        corpora = ([{'path': f'x/court-{i}/caselaw', 'kind': 'judgments'} for i in range(7)]
                   + [{'path': 'x/national/acts'}, {'path': 'y/national/caselaw'}, {'path': 'x/national/caselaw'}])
        self.assertEqual(len(m.by_kind(corpora, '', {})[1]), 9)
        self.assertEqual(m.by_kind(corpora, 'x/national/acts', {})[1], ['x/national/caselaw'])
        left = m.by_kind(corpora, 'x', {})[1]
        self.assertEqual((len(left), 'y/national/caselaw' in left), (8, False))
        fields = m.caselaw_fields(left)
        self.assertEqual((len(fields['case_law_not_read']), fields['case_law_not_read_count']), (3, 8))
        self.assertEqual(len(m.by_kind(corpora, '', {'kind': 'all'})[0]), 10)
        self.assertEqual(len(m.by_kind(corpora, '', {'kind': 'judgments'})[0]), 9)

    def test_kind_words(self):
        m = self.m
        self.assertEqual([m.kind_arg({'kind': k}) for k in ('law', 'laws', 'Judgments', 'caselaw', 'all', '')],
                         ['laws', 'laws', 'judgments', 'judgments', 'all', 'laws'])
        self.assertEqual(m.kind_arg({}, 'all'), 'all')
        with self.assertRaises(m.UserError):
            m.kind_arg({'kind': 'cases'})

    def test_short_caveats(self):
        m = self.m
        long = ("x/national/acts: this record changes the text on each change's in-force date only; it does not hold "
                + ', '.join(m.law.EFFECTS.values()) + ', so the text shown may not be the whole law that applied on 2020-01-01.')
        short = ('x/national/acts: the text shown may not be the whole law that applied; this record does not hold changes to '
                 'how a provision applies, commencement conditions or transitional rules.')
        self.assertEqual(m.short_caveats([long, long.replace('2020', '2021')]), [short])
        other = long.replace('x/national', 'y/national')
        self.assertTrue(m.short_caveats([long, other])[0].startswith('x/national/acts, y/national/acts: '))
        runs = 'a/b/c: the record runs to 2026-10-01, checked on 2026-10-28. Publisher: X.'
        fresh = 'a/b/c: stale, last checked against its official source on 2026-10-28 (13 days ago); later changes may be missing.'
        self.assertEqual(m.short_caveats([runs], fresh),
                         ['a/b/c: the record runs to 2026-10-01; stale, last checked against its official source on 2026-10-28 '
                          '(13 days ago); later changes may be missing. Publisher: X.'])
        self.assertEqual(m.short_caveats([runs]), [runs])
        for words in m.law.EFFECTS.values():  # the full explanation, once: list_jurisdictions and the instructions
            self.assertIn(words, m.RECORD_LIMITS)
        self.assertIn(m.RECORD_LIMITS, m.INSTRUCTIONS)

    def test_schemas(self):
        tools = {t['name']: t for t in self.m.tool_list()}
        for name in ('find_provision', 'search_law', 'laws_between', 'list_provisions', 'search_changes', 'phrase_history', 'what_else_changes'):
            self.assertIn('offset', tools[name]['inputSchema']['properties'], name)
        for tool in tools.values():
            for name, prop in tool['inputSchema']['properties'].items():
                self.assertTrue(prop.get('description'), f"{tool['name']}.{name}")
                if name == 'max_results':
                    self.assertRegex(prop['description'], r'default \d+, at most \d+', tool['name'])
                if name == 'kind':
                    self.assertEqual(set(prop['enum']), {'laws', 'law', 'judgments', 'all'})
        self.assertIn('jurisdiction', tools['law_details']['inputSchema']['properties'])
        self.assertNotIn('corpus', tools['law_details']['inputSchema']['properties'])
        self.assertEqual(self.m.ALIASES['law_details'], {'corpus': 'jurisdiction'})
        self.assertIn('both days included', tools['laws_between']['description'])
        self.assertIn('both days included', tools['search_changes']['description'])
        self.assertIn('after date_a, up to and including date_b', tools['compare_dates']['description'])
        self.assertIn('after date_a, up to and including date_b', tools['changes_between']['description'])
        self.assertNotIn('Defaults to today', tools['search_changes']['inputSchema']['properties']['start']['description'])
        self.assertLess(len(tools['who_wrote']['inputSchema']['properties']['path']['description']), 110)
        self.assertIn('docket', tools['find_provision']['description'])
        self.assertTrue(tools['check_precedent']['description'].startswith('The judgments the record holds for a provision'))
        self.assertIn('paths', tools['read_law']['inputSchema']['properties'])

    def test_hosted_instructions(self):
        code = "import sys; sys.path.insert(0, 'tools'); sys.dont_write_bytecode = True; import mcp_server as M; print(M.INSTRUCTIONS)"

        def instructions(flag):
            return subprocess.run([sys.executable, '-c', code], cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                                  env={**os.environ, 'GLOBAL_LAW_HOSTED': flag, 'PYTHONUTF8': '1'}).stdout
        plain, hosted = instructions(''), instructions('1')
        self.assertIn('A clone may hold only some countries', plain)  # the sentence a hosted wrapper may look for
        self.assertIn('give the user the command', plain)
        self.assertNotIn('command', hosted)
        self.assertIn('not available on this server', hosted)

    # --- on the Irish acts (and the Finnish Labour Court for case law) ---

    @needs(IE_C)
    def test_summary_is_a_headline(self):
        s2 = f'{DPA}/section-2.md'
        for tool, args in (('read_law', {'path': s2}), ('laws_between', {'start': '2024-01-01', 'end': '2024-12-31', 'jurisdiction': 'ireland'}),
                           ('search_law', {'query': 'personal data breach', 'jurisdiction': 'ireland'}), ('list_provisions', {'path': DPA}),
                           ('who_wrote', {'path': s2}), ('applies_to_case', {'path': s2, 'commenced': '2023-01-01'})):
            with self.subTest(tool=tool):
                text, data = self.ok(tool, **args)
                self.assertEqual(list(data)[0], 'summary')
                self.assertLess(len(data['summary']), 900)
                self.assertNotIn('\n', data['summary'])
        text, data = self.ok('read_law', path=s2)
        self.assertTrue(text.endswith(data['text']))
        self.assertEqual(json.dumps(data, ensure_ascii=False).count('“Act of 1988” means the Data Protection Act 1988'), 1)
        self.assertEqual([h['law'] for h in data['history']][-1], 'Data Protection Act 2018')
        self.assertEqual(data['changes_count'], len(self.ok('provision_history', path=s2)[1]['changes']))
        text, data = self.ok('search_law', query='section 2', jurisdiction='ireland', max_results=3)
        self.assertTrue(any('what_else_changes' in h for h in data['hints']))
        text, data = self.ok('who_wrote', path=s2)
        self.assertIn(data['marked'], text)

    @needs(IE_C)
    def test_caveats_once(self):
        s2 = f'{DPA}/section-2.md'
        for tool, args in (('read_law', {'path': s2}), ('who_wrote', {'path': s2}), ('world_on_date', {'jurisdiction': 'ireland'}),
                           ('compare_dates', {'path': s2, 'date_a': '2019-01-01', 'date_b': 'today'}),
                           ('search_law', {'query': 'personal data breach', 'jurisdiction': 'ireland'})):
            with self.subTest(tool=tool):
                text, data = self.ok(tool, **args)
                self.assertNotIn("in-force date only", text)
                self.assertEqual(text.count(EFFECTS_SHORT), 1)
                self.assertEqual(json.dumps(data, ensure_ascii=False).count(EFFECTS_SHORT), 1)
                for c in data['caveats']:
                    self.assertEqual(text.count(c), 1, c)
        text, data = self.ok('list_jurisdictions', jurisdiction='ireland')
        self.assertIn(self.m.RECORD_LIMITS, text)
        self.assertNotIn('tree', data)
        self.assertNotIn('Served here', text)

    @needs(IE_C)
    def test_lists_in_parts(self):
        for tool, key, args in (('list_provisions', 'provisions', {'path': DPA, 'max_results': 100}),
                                ('laws_between', 'changes', {'start': '2024-01-01', 'end': '2024-02-28', 'jurisdiction': 'ireland', 'max_results': 10}),
                                ('search_law', 'results', {'query': 'personal data breach', 'jurisdiction': 'ireland', 'max_results': 9}),
                                ('search_changes', 'changes', {'query': 'Data Protection', 'jurisdiction': 'ireland', 'max_results': 10})):
            with self.subTest(tool=tool):
                seen, offset = [], 0
                while offset is not None and len(seen) < 60:
                    text, data = self.ok(tool, **{**args, 'offset': offset})
                    self.assertEqual((data['page']['offset'], data['page']['shown']), (offset, len(data[key])))
                    if data['page']['next_offset'] is not None:
                        self.assertIn(f"pass offset {data['page']['next_offset']}", text)
                    seen += [json.dumps(r, sort_keys=True) for r in data[key]]
                    offset = data['page']['next_offset']
                self.assertEqual(len(seen), len(set(seen)))
                whole = self.ok(tool, **{**args, 'max_results': 100})[1][key]
                self.assertEqual(seen[:len(whole)], [json.dumps(r, sort_keys=True) for r in whole][:len(seen)])
        self.assertIn('past the end', self.err('list_provisions', path=DPA, offset=5000))

    @needs(IE_C)
    def test_read_several(self):
        paths = [f'{DPA}/section-{n}.md' for n in (1, 2, 3)]
        text, data = self.ok('read_law', paths=paths)
        self.assertEqual([p['path'] for p in data['provisions']], paths)
        for p in data['provisions']:
            self.assertIn(self.m.law.text_on(data['date'], p['path']).rstrip('\n'), data['text'])
        self.assertEqual(text.count(EFFECTS_SHORT), 1)
        text, data = self.ok('read_law', path=DPA, include_text=False)
        names = [p['path'].rsplit('/', 1)[-1] for p in data['provisions']]
        self.assertEqual(names, sorted(names, key=self.m.natural))
        self.assertEqual(len(names), min(data['folder_files'], self.m.READ_FOLDER))
        self.assertIn('not both', self.err('read_law', path=paths[0], paths=paths))
        self.assertIn(f'1 to {self.m.READ_MANY}', self.err('read_law', paths=paths * 7))

    @needs(IE_C)
    def test_an_act_by_name_is_one_row(self):
        text, data = self.ok('find_provision', query='Data Protection Act 2018', jurisdiction='ireland')
        first = data['results'][0]
        self.assertEqual((first['path'], first['kind'], first['title']), (DPA, 'act', 'Data Protection Act 2018'))
        self.assertFalse([r for r in data['results'] if r['path'].startswith(DPA + '/')])
        text, data = self.ok('list_provisions', path=DPA)
        names = [p['path'].rsplit('/', 1)[-1] for p in data['provisions']]
        self.assertLess(names.index('section-2.md'), names.index('section-10.md'))
        row = next(p for p in data['provisions'] if p['path'].endswith('/section-2.md'))
        self.assertEqual((row['heading'], row['heading_from']), ('Interpretation', 'first line of the text'))

    @needs(IE_C)
    def test_kind_and_jurisdiction(self):
        law_name = 'Local Government (Mayor of Limerick) and Miscellaneous Provisions Act 2024'
        a = self.ok('law_details', law=law_name, jurisdiction='ireland', include_diffs=False)[1]['changes']
        b = self.ok('law_details', law=law_name, corpus='ireland', include_diffs=False)[1]['changes']
        self.assertEqual(a, b)
        for tool, args in (('search_law', {'query': 'x'}), ('laws_between', {'start': '2024-01-01', 'end': '2024-01-02'}),
                           ('search_changes', {'query': 'x'}), ('phrase_history', {'query': 'x'}), ('world_on_date', {})):
            self.assertIn('kind is "laws" (or "law"), "judgments" or "all"', self.err(tool, kind='cases', jurisdiction='ireland', **args))
        one = self.ok('laws_between', start='2024-01-01', end='2024-01-31', jurisdiction='ireland', kind='law')[1]
        two = self.ok('laws_between', start='2024-01-01', end='2024-01-31', jurisdiction='ireland', kind='laws')[1]
        self.assertEqual(one['changes'], two['changes'])

    @needs(IE_C, FI_TT)
    def test_ireland_does_not_name_the_finnish_court(self):
        for tool, args in (('search_law', {'query': 'personal data breach'}), ('laws_between', {'start': '2024-01-01', 'end': '2024-03-31'}),
                           ('changes_between', {'date_a': '2024-03-01', 'date_b': '2024-04-30'})):
            with self.subTest(tool=tool):
                text, data = self.ok(tool, jurisdiction='ireland', **args)
                self.assertNotIn('finland', text)
                self.assertEqual((data['case_law_not_read'], data['case_law_not_read_count']), ([], 0))
                text, data = self.ok(tool, **args)
                self.assertIn(FI_TT, data['case_law_not_read'])
                self.assertIn('judgments', data['case_law_how'])

    @needs(IE_C)
    def test_hosted_wording(self):
        self.m.HOSTED = True
        try:
            text, data = self.ok('search_changes', query='zzzqqq')
            self.assertNotIn('countries.py', text)
            unserved = next((c for c in _corpus_paths() if not _checked_out(c)), None)
            if unserved:
                self.assertIn('not available on this server', text)
                self.assertNotIn('countries.py', self.ok('list_jurisdictions')[0])
                self.assertIn('not available on this server', self.err('list_provisions', path=unserved))
        finally:
            self.m.HOSTED = False
        unserved = next((c for c in _corpus_paths() if not _checked_out(c)), None)
        if unserved:
            self.assertIn('countries.py add', self.err('list_provisions', path=unserved))


PW_C = 'palau/national/acts'


class StoredIndexAndPartialSearch(unittest.TestCase):
    """For a server of every country (2026-11-10): the heading index of every corpus is kept on disk and built from
    an earlier commit's; a server that builds none reads a stored one (heading_index_if_built, store_heading_index);
    a search of every body of law stops in time and says what it did not read; and a host may answer a git grep from
    plain files (grep_rewrite). The index files of these tests go to a folder of their own, not the tree's cache."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def setUp(self):
        import tempfile
        from unittest import mock
        m = self.m
        self.mock = mock
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        real = m.heading_index_file
        patch = mock.patch.object(m, 'heading_index_file', lambda c, s: Path(self.folder.name) / real(c, s).name)
        patch.start()
        self.addCleanup(patch.stop)
        with m._index_lock:
            held = dict(m._index_done), dict(m._index_folded)
        self.forget()

        def restore():
            with m._index_lock:
                m._index_done.clear()
                m._index_folded.clear()
                m._index_done.update(held[0])
                m._index_folded.update(held[1])
        self.addCleanup(restore)

    def forget(self):
        with self.m._index_lock:
            self.m._index_done.clear()
            self.m._index_folded.clear()

    def rev(self, corpus, spec='HEAD'):
        return subprocess.run(['git', 'rev-parse', spec], cwd=ROOT / corpus, capture_output=True, text=True, check=True).stdout.strip()

    def file(self, corpus, sha):
        return self.m.heading_index_file(corpus, sha)

    def test_an_index_built_from_an_earlier_commits_equals_one_built_from_scratch(self):
        m = self.m
        read, real = [], m._index_read_headings

        def counting(corpus, sha, names, out):
            read.append(len(names))
            return real(corpus, sha, names, out)
        for corpus, back in ((IE_C, 'HEAD~200'), (PW_C, 'HEAD~30'), (FI_TT, 'HEAD~200')):
            if not _checked_out(corpus):
                continue
            with self.subTest(corpus=corpus), self.mock.patch.object(m, '_index_read_headings', counting):
                head, old = self.rev(corpus), self.rev(corpus, back)
                self.assertTrue(m.store_heading_index(corpus, head))
                whole = self.file(corpus, head).read_bytes()
                files = read[-1]
                self.assertNotIn((corpus, head), m._index_done)  # stored, not kept in memory
                os.remove(self.file(corpus, head))
                self.assertTrue(m.store_heading_index(corpus, old))
                del read[:]
                self.assertTrue(m.store_heading_index(corpus, head))
                self.assertEqual(self.file(corpus, head).read_bytes(), whole)
                self.assertEqual(len(read), 1)
                self.assertLess(read[0], files)  # only the files that differ were read
                # an earlier file for a commit git does not know: every file is read, with the same result
                os.remove(self.file(corpus, head))
                os.replace(self.file(corpus, old), self.file(corpus, '0123456789ab'))
                del read[:]
                self.assertTrue(m.store_heading_index(corpus, head))
                self.assertEqual((self.file(corpus, head).read_bytes(), read), (whole, [files]))
                self.assertEqual(m.heading_index(corpus, head), json.loads(whole))

    @needs(PW_C)
    def test_three_index_files_are_kept_for_a_corpus(self):
        m, head = self.m, self.rev(PW_C)
        stem = self.file(PW_C, head).name[:-len('0123456789ab.json')]
        folder = Path(self.folder.name)
        for i in range(5):
            (folder / f'{stem}{i:012x}.json').write_text('{}')
            os.utime(folder / f'{stem}{i:012x}.json', (time.time() - 1000 + i,) * 2)
        other = folder / f"{stem[:-1]}-more-{0:012x}.json"  # a corpus whose name starts the same
        other.write_text('{}')
        left_behind = folder / f'{stem}{7:012x}.json.1.2.tmp'
        left_behind.write_text('x')
        os.utime(left_behind, (time.time() - 3 * 86400,) * 2)
        self.assertTrue(m.store_heading_index(PW_C, head))
        self.assertEqual(sorted(p.name for p in folder.iterdir()),
                         sorted([self.file(PW_C, head).name, f'{stem}{3:012x}.json', f'{stem}{4:012x}.json', other.name]))

    @needs(IE_C)
    def test_a_stored_index_is_read_and_never_built_by_a_query(self):
        import threading
        m, head = self.m, self.rev(IE_C)
        builds, real = [], m._index_build

        def slow(corpus, sha, disk):
            builds.append(sha)
            time.sleep(0.3)
            return real(corpus, sha, disk)
        with self.mock.patch.object(m, '_index_build', slow):
            self.assertIsNone(m.heading_index_if_built(IE_C, head))
            self.assertEqual(builds, [])
            first = threading.Thread(target=m.store_heading_index, args=(IE_C, head))
            first.start()
            time.sleep(0.1)
            started = time.monotonic()
            self.assertIsNone(m.heading_index_if_built(IE_C, head))  # a build is under way: not waited for
            self.assertLess(time.monotonic() - started, 0.2)
            stored = []
            others = [threading.Thread(target=lambda: stored.append(m.store_heading_index(IE_C, head))) for _ in range(8)]
            for t in others:
                t.start()
            for t in [first, *others]:
                t.join()
            self.assertEqual((stored, len(builds)), ([True] * 8, 1))  # built once
            self.assertNotIn((IE_C, head), m._index_done)
            got = []
            readers = [threading.Thread(target=lambda: got.append(m.heading_index_if_built(IE_C, head))) for _ in range(8)]
            for t in readers:
                t.start()
            for t in readers:
                t.join()
            self.assertEqual(len({id(g) for g in got}), 1)  # read from disk once
            self.assertEqual(len(got[0]), len(m.names_of(IE_C, head)))
            self.assertIs(m.heading_index(IE_C, head), got[0])
            self.assertEqual(len(builds), 1)

    @needs(IE_C, PW_C, FI_TT)
    def test_indexes_in_memory_are_bounded(self):
        m = self.m
        ie, pw, fi = self.rev(IE_C), self.rev(PW_C), self.rev(FI_TT)
        for corpus, sha in ((IE_C, ie), (PW_C, pw), (FI_TT, fi)):
            self.assertTrue(m.store_heading_index(corpus, sha))
        room = len(m.names_of(IE_C, ie)) + len(m.names_of(FI_TT, fi)) + 10  # not Palau's as well
        with self.mock.patch.object(m, 'INDEX_HEADINGS_KEPT', room):
            m.heading_index_if_built(PW_C, pw)
            m.heading_index_if_built(FI_TT, fi)
            m.folded_headings(PW_C, pw, m.heading_index_if_built(PW_C, pw))  # Palau is the one used last
            m.heading_index_if_built(IE_C, ie)
            self.assertEqual(([k[0] for k in m._index_done], [k[0] for k in m._index_folded]), ([PW_C, IE_C], [PW_C]))
        with self.mock.patch.object(m, 'INDEX_HEADINGS_KEPT', 10):
            self.assertIsNotNone(m.heading_index_if_built(FI_TT, fi))  # one larger than the bound is kept, alone
            self.assertEqual(([k[0] for k in m._index_done], m._index_folded), ([FI_TT], {}))

    @needs(IE_C)
    def test_find_provision_reads_a_stored_index_on_a_server_that_does_not_index(self):
        m, head = self.m, self.rev(IE_C)
        greps, run = [], m.git_run

        def spy(cmd, **kw):
            if 'grep' in cmd:
                greps.append(cmd)
            return run(cmd, **kw)
        ask = {'query': 'protected disclosure', 'jurisdiction': 'ireland'}
        with self.mock.patch.object(m, 'git_run', spy):
            with self.mock.patch.object(m, 'index_served', lambda: False):
                m.t_find_provision(dict(ask))
                self.assertEqual(len(greps), 1)  # no index stored: the headings are grepped, as before
                self.assertIn('^(#|heading:|title:)', ' '.join(greps[0]))
                self.assertNotIn((IE_C, head), m._index_done)
                self.assertTrue(m.store_heading_index(IE_C, head))
                del greps[:]
                stored = m.t_find_provision(dict(ask))
                self.assertEqual(greps, [])
                self.assertIn((IE_C, head), m._index_folded)
            self.forget()
            self.assertEqual(m.t_find_provision(dict(ask)), stored)  # as a clone that indexes answers
        index = m.heading_index(IE_C, head)
        words = [m.fold(w) for w in ('protected', 'disclosure')]
        folded = m.folded_headings(IE_C, head, index)
        self.assertIs(m.folded_headings(IE_C, head, index), folded)
        self.assertEqual([n for n, h in index.items() if h and any(w in m.fold(h) for w in words)],
                         [n for n in index if (f := folded.get(n)) and any(w in f for w in words)])

    @needs(IE_C, PW_C)
    def test_a_search_of_every_body_of_law_stops_in_time(self):
        m, pool = self.m, self.m.ThreadPoolExecutor
        ask = {'query': 'narcotic', 'max_results': 7}
        whole = m.t_search_law(dict(ask))
        ireland = m.t_search_law({**ask, 'jurisdiction': IE_C, 'max_results': 200})[1]
        self.assertTrue({p.split('/')[0] for p in whole[1]['provisions']} >= {'ireland', 'palau'})
        self.assertNotIn('law_unread_count', whole[1])
        # One corpus at a time, and the call's time counted as nearly up from the start: the first body of law is
        # read, the rest are not started.
        with self.mock.patch.object(m, 'ThreadPoolExecutor', lambda n: pool(1)), self.mock.patch.object(m, 'LAW_SEARCH_MARGIN', 10 ** 6):
            self.assertEqual(m.t_search_law(dict(ask)), whole)  # outside a call's deadline nothing stops
            m._call.deadline = time.monotonic() + 600
            try:
                text, data = m.t_search_law(dict(ask))
                self.assertEqual((data['law_unread_for_time'], data['law_unread_count']), ([PW_C], 1))
                self.assertIn(f'\nPartial: 1 of 2 bodies of law were not read within the time this answer may take ({PW_C}); '
                              'give a jurisdiction to read them.\n', text)
                self.assertEqual(text.count('Partial:'), 1)
                self.assertTrue(text.startswith(f"At least {ireland['provision_count']} provision(s)"), text[:80])
                self.assertTrue(data['summary'].startswith('At least '))
                self.assertIn('Partial: 1 of 2', data['hints'][0])
                self.assertEqual(data['provision_count'], ireland['provision_count'])
                self.assertEqual((data['page']['total'], data['page']['total_at_least']), (None, ireland['page']['total']))
                self.assertIn(f"of at least {ireland['page']['total']}", text)
                seen, offset = [], 0  # the parts of the corpora read follow on without overlap
                while offset is not None:
                    part = m.t_search_law({**ask, 'offset': offset})[1]
                    self.assertEqual(part['law_unread_for_time'], [PW_C])
                    seen += part['results']
                    offset = part['page']['next_offset']
                self.assertEqual(seen, ireland['results'])
                past = m.t_search_law({**ask, 'offset': 10 ** 6})[1]  # not "past the end": the end is not known
                self.assertEqual((past['results'], past['page']['total']), ([], None))
                # case law read as well is not counted among the bodies of law
                if _checked_out(FI_TT):
                    self.assertIn('Partial: 1 of 2 bodies of law', m.t_search_law({**ask, 'kind': 'all'})[0])
                # one corpus asked for is always read, and answers as ever
                one = m.t_search_law({**ask, 'jurisdiction': PW_C})
                self.assertNotIn('law_unread_count', one[1])
            finally:
                m._call.deadline = 0.0
            self.assertEqual(one, m.t_search_law({**ask, 'jurisdiction': PW_C}))

    @needs(FI_TT)
    def test_a_host_may_answer_a_grep_from_plain_files(self):
        import io
        import tarfile
        import threading
        m = self.m
        search = {'query': 'irtisanomisaika', 'jurisdiction': FI_TT, 'max_results': 20}
        find = {'query': 'irtisanominen', 'jurisdiction': FI_TT}
        phrase = {'query': 'koeaikapurku', 'jurisdiction': FI_TT}

        def answers():
            self.forget()
            with self.mock.patch.object(m, 'index_served', lambda: False):  # find_provision greps the headings
                return m.t_search_law(dict(search)), m.t_find_provision(dict(find)), m.t_phrase_history(dict(phrase))
        plain = answers()
        self.assertTrue(plain[0][1]['results'] and plain[1][1]['results'] and plain[2][1]['changes'])
        seen = []

        def same(cmd, cwd):
            seen.append((cmd, cwd))
            return cmd, cwd
        with self.mock.patch.object(m, 'grep_rewrite', same):
            self.assertEqual(answers(), plain)
        self.assertTrue(seen)
        for cmd, cwd in seen:  # one revision, just before "--" (search_law's is the corpus as in force today)
            self.assertEqual((cmd[0], Path(cwd)), ('git', ROOT / FI_TT))
            self.assertRegex(cmd[cmd.index('--') - 1], '^[0-9a-f]{40}$')
            self.assertIn('grep', cmd[1:4])
        self.assertTrue(any(cmd[cmd.index('--') + 1:] == ['*.md'] for cmd, _ in seen))  # search_law
        self.assertTrue(any(cmd[cmd.index('--') + 1].startswith(':(literal)decisions/') for cmd, _ in seen))  # in parts
        # Each revision as plain files, and every grep run over them with --no-index: lines come without "<revision>:".
        asked, failed, one_at_a_time = [], [], threading.Lock()

        def from_files(cmd, cwd):
            g, dd = cmd.index('grep'), cmd.index('--')
            files = Path(self.folder.name) / cmd[dd - 1]
            try:
                with one_at_a_time:
                    if not files.exists():
                        done = subprocess.run(['git', 'archive', '--format=tar', cmd[dd - 1]], cwd=cwd, capture_output=True, check=True)
                        with tarfile.open(fileobj=io.BytesIO(done.stdout)) as tar:
                            tar.extractall(files, members=[t for t in tar.getmembers() if t.isfile() and t.name.endswith('.md') and '..' not in t.name])
            except Exception as e:  # the tools would fall back to git, and the test would prove nothing
                failed.append(repr(e))
                raise
            asked.append(cmd)
            return [*cmd[:g + 1], '--no-index', *cmd[g + 1:dd - 1], *cmd[dd:]], str(files)
        with self.mock.patch.object(m, 'grep_rewrite', from_files):
            self.assertEqual(answers(), plain)
        self.assertEqual((failed, len(asked)), ([], len(seen)))
        with self.mock.patch.object(m, 'grep_rewrite', lambda cmd, cwd: 1 / 0):  # a hook that fails: git answers
            self.assertEqual(answers(), plain)


class FilesIndex:
    """A stand-in for a host's full-text index (mcp_server.search_index): it answers from the files of each corpus at
    the revision search_law reads today. A file matches when it holds the query's words as a phrase, whole words,
    whatever the case, the diacritics or the line breaks between them."""

    texts: dict = {}  # corpus -> {path in the corpus: its words}, read once for the test run
    found: dict = {}  # (words, corpus) -> the files that match

    def __init__(self, m, hold=None):
        self.m, self.hold, self.calls = m, hold, []  # hold: the corpora it covers (None: every one)

    def words(self, text):
        return ' ' + ' '.join(re.findall(r'\w+', self.m.fold(text))) + ' '

    def corpus(self, corpus):
        if corpus not in self.texts:
            import io
            import tarfile
            m = self.m
            sha = m.law.corpus_tree(m.law.day('today'), corpus)
            done = subprocess.run(['git', 'archive', '--format=tar', sha], cwd=ROOT / corpus, capture_output=True, check=True)
            with tarfile.open(fileobj=io.BytesIO(done.stdout)) as tar:
                self.texts[corpus] = {t.name: self.words(tar.extractfile(t).read().decode('utf-8', 'replace'))
                                      for t in tar if t.isfile() and m.indexed_file(corpus, t.name)}
        return self.texts[corpus]

    def matching(self, query, corpus):
        q = self.words(query)
        if (q, corpus) not in self.found:
            self.found[q, corpus] = sorted((n for n, t in self.corpus(corpus).items() if q in t), key=lambda n: n.encode())
        return list(self.found[q, corpus])

    def counts(self, query, corpora, case_law):
        self.calls.append(('counts', query, list(corpora), case_law))
        return {c: len(self.matching(query, c)) for c in corpora if self.hold is None or c in self.hold}

    def paths(self, query, corpus, after, size):
        self.calls.append(('paths', query, corpus, after, size))
        names = [n for n in self.matching(query, corpus) if after is None or n.encode() > after.encode()]
        return names[:size]


class SearchByIndex(unittest.TestCase):
    """search_law with a host's full-text index (search_index, 2026-11-10): the index says which files of a corpus
    hold the words, and git greps only the files a page of lines needs. The words searched here match the same files
    as whole words and as parts of words, so the index's answers can be held against grep's."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def setUp(self):
        from unittest import mock
        m = self.m
        self.mock = mock
        self.greps = []  # every git grep started, as (argv, folder)
        run, popen = m.git_run, subprocess.Popen

        def git_run(cmd, **kw):
            if 'grep' in cmd:
                self.greps.append((list(cmd), kw.get('cwd')))
            return run(cmd, **kw)

        def started(cmd, *a, **kw):
            if 'grep' in cmd and not any(str(x).startswith('--threads=1') for x in cmd):  # (git_run's are counted above)
                self.greps.append((list(cmd), kw.get('cwd')))
            return popen(cmd, *a, **kw)
        for name, new in (('git_run', git_run), ('search_index', None)):
            patch = mock.patch.object(m, name, new)
            patch.start()
            self.addCleanup(patch.stop)
        patch = mock.patch.object(m.subprocess, 'Popen', started)
        patch.start()
        self.addCleanup(patch.stop)

    def by(self, index, **ask):
        """(text, data) of one search with the index in place; the greps it started are in self.greps."""
        del self.greps[:]
        with self.mock.patch.object(self.m, 'search_index', index):
            return self.m.t_search_law(dict(ask))

    def files_named(self, corpus=None):
        return [f for cmd, cwd in self.greps if corpus is None or Path(cwd) == ROOT / corpus for f in cmd[cmd.index('--') + 1:]]

    def pages(self, index, **ask):
        parts, offset = [], 0
        while offset is not None:
            text, data = self.by(index, **ask, offset=offset)
            parts.append((text, data))
            offset = data['page']['next_offset']
        return parts

    @needs(IE_C, PW_C, FI_TT)
    def test_counts_and_rows_are_greps(self):
        m, index = self.m, FilesIndex(self.m)
        for ask in ({'query': 'bankruptcy', 'kind': 'all', 'max_results': 200}, {'query': 'personal data breach', 'jurisdiction': 'ireland'},
                    {'query': 'Traditional Leaders', 'jurisdiction': 'palau'}, {'query': 'olbiil era kelulau', 'max_results': 10},
                    {'query': 'lomapalkkasopimuksen', 'jurisdiction': FI_TT, 'max_results': 200},
                    {'query': 'ulkopuolista', 'kind': 'judgments', 'max_results': 12}, {'query': 'bankruptcy', 'date': m.law.day('today')}):
            with self.subTest(ask=ask):
                (_, grep), (text, data) = self.by(None, **ask), self.by(index, **ask)
                self.assertTrue(grep['results'])
                self.assertEqual((data['provision_count'], data['results']), (grep['provision_count'], grep['results']))
                self.assertEqual((data['matched_by'], list(data)[:-1]), ('index', list(grep)))  # the same fields, and one more
                self.assertNotIn('matched_by', grep)
                self.assertFalse(text.startswith('At least') or data['summary'].startswith('At least'))
                self.assertTrue(text.startswith(f"{grep['provision_count']} provision(s) in force on "))
                self.assertTrue(set(data['provisions']) <= set(self.by(None, **{**ask, 'max_results': 1})[1]['provisions'])
                                or grep['provision_count'] > m.SEARCH_PATHS)
                for key in ('date', 'caveats', 'related_changes', 'left_out', 'case_law_read_in_part', 'case_law_unread_for_time'):
                    self.assertEqual(data[key], grep[key])
                if data['page']['total'] is not None:  # every corpus read to its end: the whole answer is grep's
                    self.assertEqual(({**data, 'matched_by': None}, text), ({**grep, 'matched_by': None}, self.by(None, **ask)[0]))
                else:  # lines not all read: a floor, said as one
                    self.assertGreater(data['page']['total_at_least'], data['page']['offset'] + data['page']['shown'])
                    self.assertIn(f"of at least {data['page']['total_at_least']}; pass offset", text)
                    self.assertIn(f", on at least {data['page']['total_at_least']} line(s).", data['summary'])

    @needs(IE_C, PW_C, FI_TT)
    def test_a_corpus_without_the_words_starts_no_git(self):
        index = FilesIndex(self.m)
        text, data = self.by(index, query='narcotic', kind='all')
        self.assertTrue(data['results'] and data['matched_by'] == 'index')
        self.assertEqual(index.matching('narcotic', FI_TT), [])
        self.assertEqual({Path(cwd) for _, cwd in self.greps}, {ROOT / IE_C, ROOT / PW_C})
        self.assertEqual(len(self.greps), 2)
        self.assertEqual([c for c in index.calls if c[0] == 'paths' and c[2] == FI_TT], [])
        text, data = self.by(index, query='zzqqxx nothing here', kind='all')
        self.assertEqual((self.greps, data['provision_count'], data['results'], data['page']['total']), ([], 0, [], 0))
        self.assertEqual([c[0] for c in index.calls[-2:]], ['counts', 'counts'])  # law, then case law; no paths asked
        self.assertIn('The words were matched as whole words. To match part of a word, pass regex true.', data['hints'])
        self.assertIn('matched as whole words', text)
        # part of a word is not a match for the index, and is for grep
        self.assertEqual((self.by(index, query='narcoti', kind='all')[1]['provision_count'], self.greps), (0, []))
        self.assertGreater(self.by(None, query='narcoti', kind='all')[1]['provision_count'], 0)

    @needs(IE_C, PW_C, FI_TT)
    def test_parts_follow_on_as_greps_do(self):
        index = FilesIndex(self.m)
        for ask in ({'query': 'bankruptcy', 'kind': 'all', 'max_results': 150}, {'query': 'ulkopuolista', 'kind': 'all', 'max_results': 100},
                    {'query': 'olbiil era kelulau', 'max_results': 30}, {'query': 'extradition', 'kind': 'all', 'max_results': 110}):
            with self.subTest(ask=ask):
                plain, parts = self.pages(None, **ask), self.pages(index, **ask)
                self.assertGreater(len(plain), 3)
                self.assertEqual([d['results'] for _, d in parts], [d['results'] for _, d in plain])
                self.assertEqual([d['page']['offset'] for _, d in parts], [d['page']['offset'] for _, d in plain])
                self.assertEqual({d['provision_count'] for _, d in parts}, {plain[0][1]['provision_count']})
                self.assertIsNone(parts[0][1]['page']['total'])
                self.assertEqual(parts[-1], (plain[-1][0], {**plain[-1][1], 'matched_by': 'index'}))  # the last part knows the total
                with self.assertRaises(self.m.UserError):  # past the end, as without the index
                    self.by(index, **ask, offset=plain[-1][1]['page']['total'])

    @needs(IE_C, PW_C, FI_TT)
    def test_corpora_after_the_part_are_not_read(self):
        m, index = self.m, FilesIndex(self.m)
        order = [c['path'] for c in m.law.manifest()['corpora'] if c['path'] in (IE_C, PW_C, FI_TT)]  # the answer's order
        self.assertEqual(order, [FI_TT, IE_C, PW_C])
        # a common word over every corpus: one git grep, of the first corpus's first files
        text, data = self.by(index, query='on', kind='all', max_results=5)
        self.assertEqual([Path(cwd) for _, cwd in self.greps], [ROOT / FI_TT])
        self.assertLessEqual(len(self.files_named()), 25)
        self.assertTrue(all(len(index.matching('on', c)) > 100 for c in order))
        self.assertEqual(data['provision_count'], sum(len(index.matching('on', c)) for c in order))
        self.assertEqual((len(data['results']), data['page']['total'], data['page']['next_offset']), (5, None, 5))
        self.assertEqual(data['results'], self.by(index, query='on', jurisdiction=FI_TT, max_results=5)[1]['results'])
        self.assertFalse(text.startswith('At least'))
        self.assertIn('Showing lines 1 to 5 of at least ', text)
        # the list of provisions names files of the corpora not read as well, each asked of the index once, for a share
        self.assertEqual(len(data['provisions']), m.SEARCH_PATHS)
        self.assertEqual({'/'.join(p.split('/')[:3]) for p in data['provisions']}, set(order))
        del index.calls[:]
        self.by(index, query='on', kind='all', max_results=5)
        asked = [c for c in index.calls if c[0] == 'paths']
        self.assertEqual([(c[2], c[3] is None) for c in asked], [(FI_TT, True), (FI_TT, False), (IE_C, True), (PW_C, True)])
        self.assertEqual(sum(c[4] for c in asked[1:]), m.SEARCH_PATHS - 25)
        # and of no more corpora than SEARCH_INDEX_TOP_UPS: the list is then shorter, and says so
        with self.mock.patch.object(m, 'SEARCH_INDEX_TOP_UPS', 1), self.mock.patch.object(m, 'SEARCH_INDEX_FILES', 40):
            del index.calls[:]
            text, data = self.by(index, query='on', kind='all', max_results=5)
            self.assertEqual([(c[2], c[4]) for c in index.calls if c[0] == 'paths'], [(FI_TT, 25), (FI_TT, 40)])
            self.assertEqual(len(data['provisions']), 65)
            self.assertIn(f"\nThe structured answer lists 65 of {data['provision_count']} matching provisions;", text)
        # a part that ends in a later corpus reads the corpora before it to their ends; one within the first reads it alone
        self.assertEqual(index.matching('extradition', FI_TT), [])
        first = self.by(None, query='extradition', jurisdiction=IE_C)[1]['page']['total']
        every = self.by(None, query='extradition', kind='all', max_results=200, offset=first - 100)[1]
        self.assertGreater(every['page']['total'], first + 2)
        text, data = self.by(index, query='extradition', kind='all', offset=first - 1, max_results=2)
        self.assertEqual({Path(cwd) for _, cwd in self.greps}, {ROOT / IE_C, ROOT / PW_C})
        self.assertEqual(data['results'], every['results'][99:101])
        self.assertEqual([r['path'].startswith(IE_C) for r in data['results']], [True, False])
        self.assertEqual((data['page']['total'], data['page']['next_offset']), (every['page']['total'], first + 1))
        text, data = self.by(index, query='extradition', kind='all', offset=first - 3, max_results=2)  # within the first
        self.assertEqual({Path(cwd) for _, cwd in self.greps}, {ROOT / IE_C})
        self.assertEqual((data['results'], data['page']['total'], data['page']['next_offset']), (every['results'][97:99], None, first - 1))
        self.assertEqual(data['provision_count'], len(index.matching('extradition', IE_C)) + len(index.matching('extradition', PW_C)))
        self.assertTrue(any(p.startswith(PW_C) for p in data['provisions']))
        # a corpus the index leaves out is grepped whole, as ever, and those after the part still are not read
        text, data = self.by(FilesIndex(m, hold={PW_C, FI_TT}), query='on', kind='all', max_results=5)
        self.assertEqual([cmd[cmd.index('--') + 1:] for cmd, cwd in self.greps if Path(cwd) != ROOT / FI_TT], [['*.md']])
        self.assertEqual({Path(cwd) for _, cwd in self.greps}, {ROOT / FI_TT, ROOT / IE_C})
        self.assertEqual(data['provision_count'], self.by(None, query='on', jurisdiction=IE_C)[1]['provision_count']
                         + len(index.matching('on', PW_C)) + len(index.matching('on', FI_TT)))

    @needs(IE_C, PW_C)
    def test_no_match_in_every_jurisdiction_does_not_read_the_change_notes(self):
        m, index = self.m, FilesIndex(self.m)
        real, asked = m.t_search_changes, []

        def changes(args):
            asked.append(args)
            return real(args)
        with self.mock.patch.object(m, 't_search_changes', changes):
            text, data = self.by(index, query='zzqqxx nothing here')
            self.assertEqual((asked, data['related_changes'], data['provision_count']), ([], [], 0))
            self.assertEqual(data['hints'], ['The words were matched as whole words. To match part of a word, pass regex true.'])
            self.assertNotIn('change note', text)
            text, data = self.by(index, query='zzqqxx nothing here', jurisdiction='palau')  # one jurisdiction: read
            self.assertEqual(len(asked), 1)
            self.assertIn('Nor does any change note.', text)
            self.assertIn('matched as whole words', data['hints'][0])
            self.by(None, query='zzqqxx nothing here')  # without an index, as ever
            self.assertEqual(len(asked), 2)

    @needs(PW_C)
    def test_the_change_notes_are_given_a_short_time_when_the_index_answered(self):
        m, index = self.m, FilesIndex(self.m)
        ask = {'query': 'zzqqxx nothing here', 'jurisdiction': 'palau'}
        hint = 'The change notes were not read for this; search_changes looks there.'
        seen, started, popen = [], [], subprocess.Popen

        def kept(cmd, *a, **kw):
            started.append(popen(cmd, *a, **kw))
            return started[-1]

        def in_worker(_):
            seen.append(('worker', m._call.deadline - time.monotonic()))
            while True:  # (as a long loop of the server's own work does)
                m.checkpoint()
                time.sleep(0.02)

        def slow_git(args):  # a git command that does not end, as git_run runs it: killed when the time is up
            seen.append(('thread', m._call.deadline - time.monotonic()))
            m.git_run([sys.executable, '-c', 'import time; time.sleep(60)'], capture_output=True)

        def slow_pool(args):
            seen.append(('thread', m._call.deadline - time.monotonic()))
            with m.ThreadPoolExecutor(2) as pool:
                list(m.pool_map(pool, in_worker, [1, 2]))

        def deadline_in_a_worker():
            with m.ThreadPoolExecutor(1) as pool:
                return list(m.pool_map(pool, lambda _: m._call.deadline, [1]))[0]
        self.by(index, **ask)  # (the stand-in index reads the corpus once)
        for own in (0.0, time.monotonic() + 600):
            for slow in (slow_git, slow_pool):
                with self.subTest(own=bool(own), slow=slow.__name__), self.mock.patch.object(m, 'SEARCH_CHANGES_HINT_S', 0.4), \
                        self.mock.patch.object(m, 't_search_changes', slow), self.mock.patch.object(m.subprocess, 'Popen', kept):
                    del seen[:], started[:]
                    m._call.deadline = own
                    try:
                        began = time.monotonic()
                        text, data = self.by(index, **ask)
                        took = time.monotonic() - began
                        self.assertLess(took, 3)
                        self.assertGreaterEqual(took, 0.4)
                        self.assertEqual((data['related_changes'], data['provision_count'], data['matched_by']), ([], 0, 'index'))
                        self.assertEqual(data['hints'], ['The words were matched as whole words. To match part of a word, pass regex true.', hint])
                        self.assertTrue(text.endswith('\n' + hint))
                        self.assertNotIn('Nor does any change note', text)
                        # the nearer deadline was the one the work ran under, on the thread and in its workers
                        self.assertTrue(seen and all(0.2 < left <= 0.4 for _, left in seen), seen)
                        self.assertEqual({who for who, _ in seen}, {'thread', 'worker'} if slow is slow_pool else {'thread'})
                        # and is gone: the thread, and a worker started from it, have the call's own again
                        self.assertEqual((m._call.deadline, deadline_in_a_worker()), (own, own))
                        if slow is slow_git:
                            self.assertEqual([p.poll() is not None for p in started], [True])  # the process was killed
                    finally:
                        m._call.deadline = 0.0
        with self.mock.patch.object(m, 'SEARCH_CHANGES_HINT_S', 30):
            # the call's own time ending first is the call's end, as ever
            own = m._call.deadline = time.monotonic() + 0.4
            try:
                with self.mock.patch.object(m, 't_search_changes', slow_pool), self.assertRaises(subprocess.TimeoutExpired):
                    self.by(index, **ask)
                self.assertEqual(m._call.deadline, own)
                # an error in it is the error it was, and the deadline is put back
                own = m._call.deadline = time.monotonic() + 600
                with self.mock.patch.object(m, 't_search_changes', lambda args: 1 / 0), self.assertRaises(ZeroDivisionError):
                    self.by(index, **ask)
                self.assertEqual(m._call.deadline, own)
                # change notes read in time are given as before, and without an index nothing is bounded
                del seen[:]
                real = m.t_search_changes

                def noting(args):
                    seen.append(m._call.deadline)
                    return real(args)
                with self.mock.patch.object(m, 't_search_changes', noting):
                    text, data = self.by(index, **ask)
                    self.assertIn('Nor does any change note.', text)
                    self.assertNotIn(hint, text)
                    plain = self.by(None, **ask)
                self.assertEqual((text, {**data, 'matched_by': None, 'hints': data['hints'][1:]}), (plain[0].replace('\nNor does', '\n' + data['hints'][0] + '\nNor does'), {**plain[1], 'matched_by': None}))
                self.assertEqual(seen[1], own)
                self.assertLess(seen[0], own)
            finally:
                m._call.deadline = 0.0

    @needs(IE_C, PW_C, FI_TT)
    def test_the_list_of_provisions_is_asked_for_in_one_call(self):
        m = self.m

        class Many(FilesIndex):
            answer = staticmethod(lambda got: got)

            def paths_many(self, query, wanted):
                self.calls.append(('paths_many', query, list(wanted)))
                return self.answer({c: self.matching(query, c)[:size] for c, size in wanted})
        for ask, files in (({'query': 'on', 'kind': 'all', 'max_results': 5}, 200), ({'query': 'on', 'kind': 'all', 'max_results': 5, 'offset': 150}, 10),
                           ({'query': 'extradition', 'kind': 'all', 'max_results': 3}, 200), ({'query': 'on', 'jurisdiction': 'palau', 'max_results': 2}, 200)):
            with self.subTest(ask=ask, files=files), self.mock.patch.object(m, 'SEARCH_INDEX_FILES', files):
                one, many = FilesIndex(m), Many(m)
                each = self.by(one, **ask)
                self.assertEqual(self.by(many, **ask), each)
                self.assertGreater(each[1]['provision_count'], len(each[1]['results']))
                topped = [c for c in one.calls if c[0] == 'paths'][-1]
                asked = [c for c in many.calls if c[0] == 'paths_many']
                self.assertEqual(len(asked), 1)
                self.assertLess(len([c for c in many.calls if c[0] == 'paths']), len([c for c in one.calls if c[0] == 'paths']))
                self.assertTrue(topped[2] in [c for c, _ in asked[0][2]] or files != 200)
                if files == 200:  # no corpus is asked by itself for the list: only for the files git read
                    self.assertEqual([c for c in many.calls if c[0] == 'paths'], [c for c in one.calls if c[0] == 'paths'][:1])
        ask = {'query': 'on', 'kind': 'all', 'max_results': 5}
        one = FilesIndex(m)
        each = self.by(one, **ask)
        singly = [c for c in one.calls if c[0] == 'paths']
        self.assertEqual(len(singly), 4)  # the files read, and the three corpora for the list
        many = Many(m)
        self.by(many, **ask)  # the corpus read in part is asked for the files read as well; the others for their share
        self.assertEqual(many.calls[-1], ('paths_many', 'on', [(FI_TT, 25 + 59), (IE_C, 59), (PW_C, 59)]))
        # an index whose paths_many does not answer: each corpus is asked, as without it
        for name, answer in (('none', lambda got: None), ('fails', lambda got: 1 / 0), ('a list', lambda got: list(got.items()))):
            with self.subTest(paths_many=name):
                many = Many(m)
                many.answer = answer
                self.assertEqual(self.by(many, **ask), each)
                self.assertEqual([c for c in many.calls if c[0] == 'paths'], singly)
        # a corpus's paths that are not as asked, or a corpus not asked for, add nothing; the rest stand
        whole = set(each[1]['provisions'])
        for name, answer in (('backwards', lambda got: {**got, IE_C: got[IE_C][::-1]}), ('too many', lambda got: {**got, IE_C: got[IE_C] + ['zz/zz.md']}),
                             ('text', lambda got: {**got, IE_C: 'a.md'}), ('left out', lambda got: {c: n for c, n in got.items() if c != IE_C}),
                             ('another', lambda got: {**{c: n for c, n in got.items() if c != IE_C}, 'germany/bund/acts': ['a/b.md'], 7: []})):
            with self.subTest(paths_many=name):
                many = Many(m)
                many.answer = answer
                text, data = self.by(many, **ask)
                self.assertTrue(set(data['provisions']) >= {p for p in whole if not p.startswith(IE_C)})
                self.assertFalse([p for p in data['provisions'] if p.startswith(IE_C)])
                self.assertEqual((data['provision_count'], data['results']), (each[1]['provision_count'], each[1]['results']))
                self.assertIn(f"\nThe structured answer lists {len(data['provisions'])} of {data['provision_count']} matching provisions;", text)

    @needs(IE_C)
    def test_an_index_that_gives_the_lines_is_not_grepped(self):
        """lines(query, corpus, revision, names): the page's lines come from the index, and git greps nothing; an
        index whose lines do not answer, or answer anything else, is grepped as an index without them."""
        m = self.m
        sha = m.law.corpus_tree(m.law.day('today'), IE_C)

        class Lines(FilesIndex):
            answer = staticmethod(lambda got: got)

            def lines(self, query, corpus, rev, names):
                self.calls.append(('lines', query, corpus, rev, list(names)))
                word, out = query.lower(), {}
                for name in names:
                    text = subprocess.run(['git', 'show', f'{rev}:{name}'], cwd=ROOT / corpus, capture_output=True, check=True).stdout.decode('utf-8', 'replace')
                    out[name] = [(i, line) for i, line in enumerate(text.split('\n'), 1) if re.search(rf'\b{re.escape(word)}\b', line.lower())]
                return self.answer(out)

        ask = {'query': 'bankruptcy', 'jurisdiction': 'ireland', 'max_results': 40}
        plain = self.by(FilesIndex(m), **ask)
        self.assertTrue(self.greps)
        index = Lines(m)
        text, data = self.by(index, **ask)
        self.assertEqual(self.greps, [])
        asked = [c for c in index.calls if c[0] == 'lines']
        self.assertTrue(asked and all(c[1:4] == ('bankruptcy', IE_C, sha) for c in asked))
        self.assertEqual([n for c in asked for n in c[4]], index.matching('bankruptcy', IE_C)[:sum(len(c[4]) for c in asked)])
        self.assertEqual((data['results'], data['provision_count'], data['provisions'], data['page']),
                         (plain[1]['results'], plain[1]['provision_count'], plain[1]['provisions'], plain[1]['page']))
        self.assertEqual(text, plain[0])
        for name, answer in (('none', lambda got: None), ('fails', lambda got: 1 / 0), ('a list', lambda got: list(got.items())),
                             ('a file left out', lambda got: dict(list(got.items())[1:])),
                             ('backwards', lambda got: {n: rows[::-1] if len(rows) > 1 else [(0, 'x')] for n, rows in got.items()}),
                             ('not lines', lambda got: {n: ['x'] for n in got})):
            with self.subTest(lines=name):
                index = Lines(m)
                index.answer = staticmethod(answer)
                self.assertEqual(self.by(index, **ask), plain)
                self.assertTrue(self.greps)

    @needs(IE_C)
    def test_git_reads_only_the_files_a_part_needs(self):
        m, index = self.m, FilesIndex(self.m)
        text, data = self.by(index, query='the', jurisdiction='ireland')
        named = self.files_named()
        self.assertLessEqual(len(named), 60)
        self.assertEqual(named, index.matching('the', IE_C)[:len(named)])  # the first, in git's order
        self.assertGreater(data['provision_count'], 30000)
        self.assertEqual(data['provision_count'], len(index.matching('the', IE_C)))
        self.assertEqual((len(data['results']), data['page']['total'], data['page']['next_offset']), (30, None, 30))
        self.assertEqual(data['results'], self.by(None, query='the', jurisdiction='ireland')[1]['results'])
        self.assertEqual(len(data['provisions']), m.SEARCH_PATHS)  # the list is filled from the index, not by reading
        self.assertIn(f"\nThe structured answer lists the first {m.SEARCH_PATHS} of {data['provision_count']} matching provisions;", text)
        text, data = self.by(index, query='the', jurisdiction='ireland', offset=600, max_results=200)
        self.assertLessEqual(len(self.files_named()), 801)  # each file named has a line or more with the word
        self.assertEqual(data['results'], self.by(None, query='the', jurisdiction='ireland', offset=600, max_results=200)[1]['results'])
        # a list shorter than the count says so
        with self.mock.patch.object(m, 'SEARCH_PATHS', 40), self.mock.patch.object(index, 'paths', wraps=index.paths) as paths:
            text, data = self.by(index, query='the', jurisdiction='ireland', max_results=3)
            self.assertEqual(len(data['provisions']), 40)
            self.assertEqual([c.args[3] for c in paths.call_args_list], [25, 15])
            paths.side_effect = lambda q, c, after, size: None if after else FilesIndex.paths(index, q, c, after, size)
            text, data = self.by(index, query='the', jurisdiction='ireland', max_results=3)
            self.assertEqual(len(data['provisions']), 25)
            self.assertIn(f"\nThe structured answer lists 25 of {data['provision_count']} matching provisions;", text)

    @needs(IE_C, FI_TT)
    def test_the_greps_are_those_of_a_whole_search_with_files_named(self):
        m, index = self.m, FilesIndex(self.m)
        asked = []

        def same(cmd, cwd):
            asked.append((list(cmd), cwd))
            return cmd, cwd
        pattern = m.loose_pattern('ulkopuolista')
        with self.mock.patch.object(m, 'grep_rewrite', same):
            self.by(index, query='ulkopuolista', kind='all', max_results=5)
        files = index.matching('ulkopuolista', FI_TT)[:25]
        today = m.law.day('today')
        self.assertEqual(asked, [(['git', '-c', 'core.quotepath=off', 'grep', f'--threads={m.GREP_THREADS}', '-n', '-I', '-E', '-i', '-e', pattern,
                                   m.law.corpus_tree(today, FI_TT), '--', *files], ROOT / FI_TT)])
        law = [(cmd, cwd) for cmd, cwd in self.greps if Path(cwd) == ROOT / IE_C]
        self.assertEqual(law, [(['git', 'grep', '--threads=1', '-n', '-I', '-E', '-i', '-e', pattern, m.law.corpus_tree(today, IE_C), '--',
                                 *index.matching('ulkopuolista', IE_C)[:25]], ROOT / IE_C)] if index.matching('ulkopuolista', IE_C) else [])
        # many files, or long names: several greps, each within the command line
        with self.mock.patch.object(m, 'SEARCH_INDEX_ARGV', 400):
            _, data = self.by(index, query='bankruptcy', jurisdiction='ireland', max_results=100)
        self.assertGreater(len(self.greps), 5)
        self.assertTrue(all(sum(len(f) + 1 for f in cmd[cmd.index('--') + 1:]) <= 400 for cmd, _ in self.greps))
        self.assertEqual(data['results'], self.by(None, query='bankruptcy', jurisdiction='ireland', max_results=100)[1]['results'])

    @needs(IE_C, PW_C, FI_TT)
    def test_what_the_index_does_not_answer_is_grepped(self):
        m = self.m
        ask = {'query': 'bankruptcy', 'kind': 'all', 'max_results': 40}
        plain = self.by(None, **ask)
        # a corpus the index leaves out
        index = FilesIndex(m, hold={IE_C, FI_TT})
        text, data = self.by(index, **ask)
        self.assertEqual((data['provision_count'], data['results'], data['matched_by']), (plain[1]['provision_count'], plain[1]['results'], 'index'))
        self.assertEqual([cmd[cmd.index('--') + 1:] for cmd, cwd in self.greps if Path(cwd) == ROOT / PW_C], [['*.md']])
        self.assertNotIn('*.md', self.files_named(IE_C) + self.files_named(FI_TT))
        self.assertEqual([c for c in index.calls if c[0] == 'paths' and c[2] == PW_C], [])
        self.assertEqual([c[2:] for c in index.calls if c[0] == 'counts'], [([IE_C, PW_C], False), ([FI_TT], True)])
        # an index that does not answer, or fails: the answer is grep's, to the letter
        for name, counts in (('none', lambda *a: None), ('fails', lambda *a: 1 / 0), ('nonsense', lambda *a: [3]), ('empty', lambda *a: {}),
                             ('others', lambda *a: {'germany/bund/acts': 4, IE_C: -1, PW_C: 'many', FI_TT: None})):
            with self.subTest(counts=name):
                index = FilesIndex(m)
                index.counts = counts
                self.assertEqual(self.by(index, **ask), plain)
                self.assertEqual(index.calls, [])
        real = FilesIndex(m)
        for name, paths in (('none', lambda *a: None), ('fails', lambda *a: 1 / 0), ('text', lambda *a: 'a.md'),
                            ('backwards', lambda q, c, after, size: real.paths(q, c, after, size)[::-1]),
                            ('too many', lambda q, c, after, size: real.paths(q, c, after, size + 1)),
                            ('again', lambda q, c, after, size: real.paths(q, c, None, size) if c == IE_C else real.paths(q, c, after, size))):
            with self.subTest(paths=name), self.mock.patch.object(m, 'SEARCH_INDEX_FILES', 30):
                index = FilesIndex(m)
                index.paths = paths
                # each corpus with the words is grepped whole; the case law, without them, still has the index's word for it
                far = {**ask, 'offset': 480}  # (far enough for a second list of Ireland's files, and for Palau's lines)
                whole = self.by(None, **far)
                self.assertEqual(self.by(index, **far), (whole[0], {**whole[1], 'matched_by': 'index'}))
                self.assertIn(['*.md'], [cmd[cmd.index('--') + 1:] for cmd, cwd in self.greps if Path(cwd) == ROOT / IE_C])
                self.assertEqual({Path(cwd) for cmd, cwd in self.greps}, {ROOT / IE_C, ROOT / PW_C})
                if name != 'again':  # a first part: Ireland grepped whole fills it, and Palau's file is counted unread
                    got = self.by(index, **ask)[1]
                    self.assertEqual((got['results'], got['provision_count']), (plain[1]['results'], plain[1]['provision_count']))
                    self.assertEqual([cmd[cmd.index('--') + 1:] for cmd, cwd in self.greps], [['*.md']])
        # a file the index counts for words that run over a line break: a provision more, and no line
        index = FilesIndex(m)
        extra = next(n for n in sorted(index.corpus(PW_C)) if n not in index.matching('bankruptcy', PW_C))
        with self.mock.patch.object(index, 'matching', lambda q, c: sorted(set(FilesIndex.matching(index, q, c)) | ({extra} if c == PW_C else set()))):
            text, data = self.by(index, **ask)
            self.assertEqual((data['provision_count'], data['results']), (plain[1]['provision_count'] + 1, plain[1]['results']))
            self.assertIn(f'{PW_C}/{extra}', data['provisions'])  # (not read for this part: named by the index)
            self.assertNotIn(extra, self.files_named())
            self.assertIn(f'{PW_C}/{extra}', self.by(index, **{**ask, 'offset': 400, 'max_results': 200})[1]['provisions'])
            self.assertIn(extra, self.files_named())
        # a file search_law does not count (a corpus's own documentation) is neither counted nor read
        index = FilesIndex(m)
        with self.mock.patch.object(index, 'matching', lambda q, c: sorted(set(FilesIndex.matching(index, q, c)) | ({'README.md', ':x.md'} if c == PW_C else set()))), \
                self.mock.patch.object(index, 'counts', lambda q, cs, k: {c: len(index.matching(q, c)) for c in cs}):
            text, data = self.by(index, **{**ask, 'offset': 400, 'max_results': 200})
        self.assertEqual(data['provision_count'], plain[1]['provision_count'])
        self.assertFalse({'README.md', ':x.md'} & set(self.files_named()))

    @needs(IE_C, PW_C, FI_TT)
    def test_the_index_is_asked_only_for_plain_words_of_todays_text(self):
        index = FilesIndex(self.m)
        for ask in ({'query': 'bankrupt(cy)?', 'regex': True, 'kind': 'all'}, {'query': 'bankruptcy', 'date': '2020-01-01', 'kind': 'all'},
                    {'query': 'Bankruptcy', 'case_sensitive': True, 'kind': 'all'},
                    {'query': 'bankruptcy', 'jurisdiction': f'{IE_C}/bankruptcy-act-1988'}):  # a folder within a corpus
            with self.subTest(ask=ask):
                plain = self.by(None, **ask)
                self.assertEqual(self.by(index, **ask), plain)
                self.assertEqual(index.calls, [])
                self.assertTrue(plain[1]['results'])
        self.by(index, query='bankruptcy', jurisdiction='ireland')
        self.assertEqual(index.calls[0], ('counts', 'bankruptcy', [IE_C], False))
        self.assertEqual(index.calls[1][:4], ('paths', 'bankruptcy', IE_C, None))

    @needs(IE_C, PW_C)
    def test_the_time_rule_of_a_search_of_every_body_of_law_stands(self):
        m, pool, index = self.m, self.m.ThreadPoolExecutor, FilesIndex(self.m)
        ask = {'query': 'narcotic', 'max_results': 7}
        with self.mock.patch.object(m, 'ThreadPoolExecutor', lambda n: pool(1)), self.mock.patch.object(m, 'LAW_SEARCH_MARGIN', 10 ** 6):
            m._call.deadline = time.monotonic() + 600
            try:
                text, data = self.by(index, **{**ask, 'max_results': 200})  # (a part that needs Palau's lines too)
                self.assertEqual((data['law_unread_for_time'], data['matched_by']), ([PW_C], 'index'))
                self.assertTrue(text.startswith('At least ') and data['page']['total'] is None)
                # a body of law without the words takes no time: it is never left unread, nor counted as the one read
                for words, read, without in (('olbiil era kelulau', PW_C, IE_C), ('personal data breach', IE_C, PW_C)):
                    text, data = self.by(index, query=words, max_results=7)
                    self.assertEqual(index.matching(words, without), [])
                    self.assertNotIn('law_unread_for_time', data)
                    self.assertFalse(text.startswith('At least'))
                    self.assertEqual({Path(cwd) for _, cwd in self.greps}, {ROOT / read})
                    self.assertIn('law_unread_for_time', self.by(None, query=words, max_results=7)[1])
            finally:
                m._call.deadline = 0.0


class ChangesIndex:
    """A stand-in for a host's index of changes (mcp_server.history_index): for each corpus it holds, the changed
    files git's pickaxe finds for the words (parts of words too, where a host's index matches whole words: the answers
    can then be held against git's own), up to a tip `behind` commits before the corpus's HEAD."""

    def __init__(self, m, corpora, behind=0):
        self.m, self.corpora, self.behind, self.calls, self._tips, self._rows = m, list(corpora), behind, [], {}, {}

    def tip(self, corpus):
        if corpus not in self._tips:  # (a history shorter than `behind`: its first commit)
            commits = subprocess.run(['git', 'rev-list', '-n', str(self.behind + 1), 'HEAD'], cwd=ROOT / corpus, capture_output=True, text=True,
                                     check=True).stdout.split()
            self._tips[corpus] = commits[-1]
        return self._tips[corpus]

    def tips(self):
        return {c: self.tip(c) for c in self.corpora}

    def rows(self, words, corpus):
        if (words, corpus) not in self._rows:
            self._rows[words, corpus] = self._read(words, corpus)
        return list(self._rows[words, corpus])

    def _read(self, words, corpus):
        out = subprocess.run(['git', 'log', self.tip(corpus), '--format=@%H %P', '--name-status', '-M', '-i', '-E', f'-G{self.m.loose_pattern(words)}', '--', '*.md'],
                             cwd=ROOT / corpus, capture_output=True, encoding='utf-8', errors='replace', check=True).stdout
        return self.m.status_pairs(out)

    def holding(self, words):
        self.calls.append(('holding', words))
        return {c for c in self.corpora if self.rows(words, c)}

    def pairs(self, words, corpus, folders, most, skip=None):
        self.calls.append(('pairs', words, corpus, folders, most, list(skip or [])))
        under = lambda n: not folders or any(n.startswith(f + '/') for f in folders)  # noqa: E731
        return [r for r in self.rows(words, corpus) if r[0] not in (skip or ()) and (under(r[2]) or under(r[3]))][:most]


class PhraseHistoryByIndex(unittest.TestCase):
    """phrase_history with a host's index of changes (history_index, 2026-11-12): the index names the changed files
    whose added or removed lines hold the words, git reads only the commits after the index's tip, and the lines are
    counted as ever."""

    ASKS = ({'query': '7,500,000', 'jurisdiction': US_C, 'max_results': 300}, {'query': 'COVID', 'jurisdiction': GG_FOLDER, 'max_results': 300})

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    def setUp(self):
        from unittest import mock
        self.mock = mock
        self.whole = []  # every reading of a whole history (split_log)
        m, split = self.m, self.m.split_log

        def split_log(*a, **kw):
            self.whole.append(a[0])
            return split(*a, **kw)
        for name, new in (('split_log', split_log), ('history_index', None)):
            patch = mock.patch.object(m, name, new)
            patch.start()
            self.addCleanup(patch.stop)

    def by(self, index, ask):
        del self.whole[:]
        with self.mock.patch.object(self.m, 'history_index', index):
            return self.m.t_phrase_history(dict(ask))

    def corpora(self, ask):
        m = self.m
        return [c['path'] for c in m.law.manifest()['corpora'] if m.scoped(c['path'], m.scope_arg(dict(ask))) is not None and not m.law.is_caselaw(c)
                and (ROOT / c['path'] / '.git').exists()]

    @needs(DE_C, US_C)
    def test_the_index_names_the_changes_and_git_reads_no_whole_history(self):
        for ask in self.ASKS:
            with self.subTest(ask=ask):
                git = self.by(None, ask)
                self.assertTrue(self.whole and git[1]['changes'])
                index = ChangesIndex(self.m, self.corpora(ask))
                self.assertEqual(self.by(index, ask), git)
                self.assertEqual(self.whole, [])
                self.assertTrue(any(c[0] == 'pairs' for c in index.calls))

    @needs(DE_C, US_C, UK_C)
    def test_many_corpora_are_first_asked_which_hold_the_words(self):
        m, ask = self.m, {'query': '7,500,000', 'max_results': 300}
        with self.mock.patch.object(m, 'by_kind', lambda corpora, scope, args: ([c for c in corpora if c['path'] in (US_C, DE_C, UK_C)], [])):
            git = self.by(None, ask)
            self.assertTrue(git[1]['changes'])
            index = ChangesIndex(m, [c for c in (US_C, DE_C, UK_C) if (ROOT / c / '.git').exists()])
            self.assertEqual(self.by(index, ask), git)
            self.assertEqual(self.whole, [])
            self.assertEqual([c for c in index.calls if c[0] == 'holding'], [('holding', '7,500,000')])
            holders = index.holding('7,500,000')
            self.assertEqual({c[2] for c in index.calls if c[0] == 'pairs'}, holders)  # only those are asked for their changes

    @needs(DE_C, US_C)
    def test_the_commits_after_the_indexs_tip_are_read_by_git(self):
        for ask in self.ASKS:
            for behind in (1, 40):
                with self.subTest(ask=ask, behind=behind):
                    git = self.by(None, ask)
                    self.assertEqual(self.by(ChangesIndex(self.m, self.corpora(ask), behind=behind), ask), git)
                    self.assertEqual(self.whole, [])
        with self.mock.patch.object(self.m, 'HISTORY_GAP', 3):  # too far behind: the whole history is read, as ever
            ask = self.ASKS[0]
            git = self.by(None, ask)
            self.assertEqual(self.by(ChangesIndex(self.m, self.corpora(ask), behind=40), ask), git)
            self.assertTrue(self.whole)

    @needs(US_C)
    def test_commits_that_are_no_change_of_the_law_are_left_out(self):
        m, ask = self.m, self.ASKS[0]
        git = self.by(None, ask)

        class Crowded(ChangesIndex):  # a corpus published again: one commit, no event of the timeline, holds every file
            def pairs(self, words, corpus, folders, most, skip=None):
                got = super().pairs(words, corpus, folders, most, skip)
                junk = [] if 'f' * 40 in (skip or ()) else [('f' * 40, None, f'x/{i}.md', f'x/{i}.md') for i in range(most)]
                return (junk + got)[:most]
        index = Crowded(m, self.corpora(ask))
        self.assertEqual(self.by(index, ask), git)
        asked = [c[5] for c in index.calls if c[0] == 'pairs' and c[2] == US_C]
        self.assertEqual(asked, [[], ['f' * 40]])
        self.assertEqual(self.whole, [])

        class Scattered(ChangesIndex):  # as many commits that do not count as an answer holds, one file each, newest
            def pairs(self, words, corpus, folders, most, skip=None):
                got = super().pairs(words, corpus, folders, most, skip)
                junk = [('%040x' % i, None, f'x/{i}.md', f'x/{i}.md') for i in range(1, most + 1) if '%040x' % i not in (skip or ())]
                return (junk + got)[:most]
        index = Scattered(m, self.corpora(ask))
        self.assertEqual(self.by(index, ask), git)
        asked = [len(c[5]) for c in index.calls if c[0] == 'pairs' and c[2] == US_C]
        self.assertEqual(len(asked), 2)  # the first answer's commits but its last are left out of the second question
        self.assertEqual(asked[0], 0)
        self.assertEqual(self.whole, [])
        with self.mock.patch.object(m, 'HISTORY_ROUNDS', 1):  # asked once only: what is in hand, said to be cut
            text, data = self.by(Scattered(m, self.corpora(ask)), ask)
            self.assertEqual(self.whole, [])
            self.assertEqual((data['changes'], data.get('cut')), ([], True))
            self.assertIn('only the newest were', text)

    @needs(US_C)
    def test_an_index_that_does_not_answer_is_not_missed(self):
        m, ask = self.m, self.ASKS[0]
        git = self.by(None, ask)

        class NoTips(ChangesIndex):
            def tips(self):
                raise OSError('down')

        class Elsewhere(ChangesIndex):  # a tip that is not in this history
            def tip(self, corpus):
                return 'a' * 40

        class NoPairs(ChangesIndex):
            def pairs(self, *a, **kw):
                return None

        class Odd(ChangesIndex):
            def pairs(self, *a, **kw):
                return [('x', None, 'a.md')]
        for kind in (NoTips, Elsewhere, NoPairs, Odd):
            with self.subTest(kind=kind.__name__):
                self.assertEqual(self.by(kind(m, self.corpora(ask)), ask), git)
                self.assertTrue(self.whole)
        self.assertEqual(self.by(ChangesIndex(m, []), ask), git)  # a corpus the index does not hold
        self.assertEqual(self.by(ChangesIndex(m, self.corpora(ask)), {**ask, 'query': '7,500,0+', 'regex': True})[1]['changes'],
                         self.by(None, {**ask, 'query': '7,500,0+', 'regex': True})[1]['changes'])
        self.assertTrue(self.whole)  # a regular expression is git's


class ChangedBetweenDates(unittest.TestCase):
    """changes_between without the two trees (changed_files, 2026-11-12): for a corpus that is not in in-force order,
    the files that differ between two dates are read off its table of versions and corrections, and must be the
    lines git prints for the two trees corpus_tree builds."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    @needs_any_corpus()
    def test_the_files_that_differ_are_those_of_the_two_trees(self):
        m = self.m
        law = m.law
        tried = compared = 0
        for c in law.manifest()['corpora']:
            path = c['path']
            if tried >= 3:
                break
            if law.is_caselaw(c) or not (ROOT / path / '.git').exists() or law.in_order(path):
                continue
            index, _ = law.file_index(path)
            table = m._day_paths(path)
            if not table or len(table[0]) < 4 or len(index) > 60000:
                continue
            tried += 1
            days = table[0]
            cwd = law.corpus_dir(path)
            folder = sorted(index)[len(index) // 2].split('/')[0]
            third = len(days) // 3
            for a, b, inner in ((days[0], days[-1], None), (days[third], days[2 * third], None), (days[-2], days[-1], None),
                                (days[1], days[1], None), (days[0], days[-1], folder), (days[third], days[-1], folder)):
                with self.subTest(corpus=path, a=a, b=b, inner=inner):
                    got = m.changed_files(path, a, b, inner)
                    self.assertIsNotNone(got)
                    ta, tb = law.corpus_tree(a, path), law.corpus_tree(b, path)
                    want = [] if ta == tb else law.git('diff', '--name-status', ta or law.EMPTY_TREE, tb, *(['--', inner] if inner else []), cwd=cwd).splitlines()
                    self.assertEqual(got, want)
                    compared += bool(want)
            self.assertIsNone(m.changed_files(path, '0001-01-01', days[-1], None))  # before its record: the trees say
            with self.mock_most(m, 0):
                self.assertIsNone(m.changed_files(path, days[0], days[-1], None))  # a window too wide: the trees
        if tried:
            self.assertTrue(compared)

    @staticmethod
    def mock_most(m, n):
        from unittest import mock
        return mock.patch.object(m, 'CHANGED_MOST', n)

    def test_a_corpus_in_order_is_left_to_its_commits(self):
        m = self.m
        for c in m.law.manifest()['corpora']:
            if (ROOT / c['path'] / '.git').exists() and not m.law.is_caselaw(c) and m.law.in_order(c['path']):
                self.assertIsNone(m.changed_files(c['path'], '2000-01-01', '2020-01-01', None))
                break


class CountsByBlob(unittest.TestCase):
    """grep_counts reads each version of a file once, by its blob id (2026-11-12): the counts must be those of the
    git grep over commits and names it replaced, for every change and its parent."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        sys.dont_write_bytecode = True
        import mcp_server
        cls.m = mcp_server

    @needs(US_C)
    def test_the_counts_are_those_of_a_grep_by_commit_and_name(self):
        m, cwd = self.m, ROOT / US_C
        out = subprocess.run(['git', 'log', '-60', '--format=@%H %P', '--name-status', '-M', '--', '*.md'], cwd=cwd, capture_output=True,
                             encoding='utf-8', errors='replace', check=True).stdout
        pairs = [(sha, parent, name, None, old) for sha, parent, name, old in m.status_pairs(out)][:400]
        self.assertGreater(len(pairs), 5)
        for pattern in (m.loose_pattern('the'), m.loose_pattern('small business debtor'), 'sec(tion|retary)', m.loose_pattern('qqzzxxjj')):
            with self.subTest(pattern=pattern):
                new, old = m.grep_counts(cwd, pattern, pairs), m._grep_counts_by_name(cwd, pattern, pairs)
                keys = {(p[0], p[2]) for p in pairs} | {(p[1], p[4]) for p in pairs if p[1]}
                self.assertEqual({k: new.get(k, 0) for k in keys}, {k: old.get(k, 0) for k in keys})
                self.assertTrue(set(new) <= keys)
        base = m.grep_counts(cwd, m.loose_pattern('the'), pairs)
        self.assertTrue(any(base.values()))
        from unittest import mock
        with mock.patch.object(m, 'GREP_BLOBS', 7):  # many small greps, side by side: the same counts
            self.assertEqual(m.grep_counts(cwd, m.loose_pattern('the'), pairs), base)
        one = pairs[:1]  # one change: counted by name, as ever
        self.assertEqual({k: v for k, v in m.grep_counts(cwd, m.loose_pattern('the'), one).items() if k in keys},
                         {k: v for k, v in m._grep_counts_by_name(cwd, m.loose_pattern('the'), one).items() if k in keys})

    @needs(US_C)
    def test_a_phrase_in_quotes_or_with_two_spaces_is_the_phrase(self):
        m = self.m
        plain = m.t_phrase_history({'query': 'small business debtor', 'jurisdiction': US_C, 'max_results': 300})[1]['changes']
        self.assertTrue(plain)
        for query in ('"small business debtor"', '“small business debtor”', 'small  business   debtor', ' "small business  debtor" '):
            with self.subTest(query=query):
                self.assertEqual(m.t_phrase_history({'query': query, 'jurisdiction': US_C, 'max_results': 300})[1]['changes'], plain)
        # a quote inside the words is part of them, and a regular expression is taken as written
        self.assertNotEqual(m.t_phrase_history({'query': '"small" business "debtor"', 'jurisdiction': US_C})[1]['changes'], plain[:40])
        self.assertEqual(m.loose_pattern('a  b'), m.loose_pattern('a b'))


if __name__ == '__main__':
    unittest.main()
