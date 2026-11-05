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
        self.assertIn('not a provision file', refused('read_law', path=P('us/federal/usc/title-11')))
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
        self.assertIn('Gap: the record starts on 2018-01-12', r['summary'])
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
        self.assertIn("What each provision's words did", self.s.call('law_details', law='Pub. L. 117-151', corpus=P('us/federal/usc'))['structuredContent']['summary'])
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
        self.assertIn('where this record starts, not the day it came into force', r['summary'])
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
        self.assertIn('a revision of an act already in force then', before['summary'])
        after = self.s.call('read_law', path=p, date='2018-01-01', include_text=False)['structuredContent']
        self.assertTrue(after['in_force'])
        early = self.s.call('read_law', path=p, date='1980-01-01', include_text=False)['structuredContent']
        if 'adopted only on' in early['summary']:  # data/acts.json with adopted days (china-law e681287)
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
        self.assertIn('what_else_changes', self.s.call('search_law', query='1182', jurisdiction='us')['structuredContent']['summary'])
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
        self.assertIn('Not decided by this data', r['summary'])
        self.assertIn('Landgraf', r['summary'])

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
        self.assertIn('before the record begins', sbd['summary'])

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

    def test_article_number_forms(self):
        self.assertEqual(self.m.number_forms('art. 6^1'), 'art. 6-1')
        self.assertEqual(self.m.number_forms('art. 6¹'), 'art. 6-1')
        self.assertEqual(self.m.number_forms('art. 6 indice 1'), 'art. 6-1')
        self.assertEqual(self.m.number_forms('art. 1.357'), 'art. 1357')
        self.assertEqual(self.m.number_forms('S.L. 586.08'), 'S.L. 586.08')  # not a thousands dot
        self.assertEqual(self.m.stem_of('lege/2009/287/art-0194.md'), '194')
        self.assertEqual(self.m.stem_of('lege/1990/31/art-006-1.md'), '6-1')

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


if __name__ == '__main__':
    unittest.main()
