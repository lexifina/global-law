"""The MCP server, spoken to the way a client does: newline-delimited JSON-RPC over stdio.

  python -m unittest tests.test_mcp -v
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
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
GG_FOLDER = P('de/bund/grundgesetz')  # a corpus of its own, or the grundgesetz/ folder of all federal law
GG = P('de/bund/grundgesetz/artikel/{}.md')
SEND = P('gb/uk/send/uksi/2014/1530/regulation/13.md')


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

    def test_a_missing_checkout_narrows_the_answer(self):
        # A partial checkout used to end the server (law.py stops with SystemExit when a corpus is not checked out).
        import tools.mcp_server as m  # noqa: F401  (in-process: no corpus is renamed on disk)
        missing: list[str] = []
        found = m.checked_out([{'path': 'no/such/corpus'}, {'path': P('us/federal/usc')}], missing)
        self.assertEqual(missing, ['no/such/corpus'])
        self.assertEqual([c['path'] for c, _ in found], [P('us/federal/usc')])
        self.assertIn('not searched', m.not_searched(missing))

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

    def test_scoped_definition_and_nearer_definitions(self):
        # §1182 defines "debtor in possession" "In this subchapter"; §1101 defines it for chapter 11, so §1103 is
        # nearer §1101 and is listed apart, while §1184 in subchapter V stays with §1182.
        r = self.s.call('what_else_changes', path=USC)['structuredContent']
        self.assertEqual(r['definition_scope'], 'In this subchapter')
        relies = [p['path'] for g in r['groups'] if g['kind'] == 'uses a term this provision defines' for p in g['provisions']]
        nearer = {p['path']: p['nearest_definition'] for g in r['groups'] if g['kind'].startswith('uses the term, but nearer') for p in g['provisions']}
        self.assertIn(P('us/federal/usc/title-11/1184.md'), relies)
        self.assertEqual(nearer.get(P('us/federal/usc/title-11/1103.md')), P('us/federal/usc/title-11/1101.md'))

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

    def test_broad_search_is_capped(self):
        r = self.s.call('search_law', query='the', jurisdiction=P('us/federal/usc'))['structuredContent']
        self.assertLessEqual(len(r['provisions']), 200)
        self.assertGreater(r['provision_count'], 200)

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

    def test_law_details_says_what_each_provision_did(self):
        # One call shows what a law did to each provision's words; no compare_dates per provision.
        r = self.s.call('law_details', law='Pub. L. 117-151', corpus=P('us/federal/usc'))['structuredContent']['changes']
        rows = [d for c in r for d in c.get('diffs', [])]
        usc = [d for d in rows if d['path'] == USC]
        self.assertTrue(usc and usc[0]['effect'] == 'words changed' and '7,500,000' in ' '.join(d['diff'] for d in usc))
        self.assertIn("What each provision's words did", self.s.call('law_details', law='Pub. L. 117-151', corpus=P('us/federal/usc'))['structuredContent']['summary'])
        bare = self.s.call('law_details', law='Pub. L. 117-151', corpus=P('us/federal/usc'), include_diffs=False)['structuredContent']['changes']
        self.assertNotIn('diffs', bare[0])

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

    def test_before_a_baseline_is_outside_the_record(self):
        # §101 enters the US record with the 2017 edition: before it, the record is silent, the law was not.
        r = self.s.call('read_law', path=P('us/federal/usc/title-11/101.md'), date='2010-01-01')['structuredContent']
        self.assertIn('where this record starts, not the day it came into force', r['summary'])
        c = self.s.call('resolve_citations', text='11 U.S.C. § 101', date='2010-01-01')['structuredContent']['citations'][0]
        self.assertTrue(c['status'].startswith('before the record starts'))
        today = self.s.call('read_law', path=P('us/federal/usc/title-11/1101.md'), include_text=False)['structuredContent']
        if today['last_change']['kind'] == 'baseline':
            self.assertIn('First version in the record', today['summary'])

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

    def test_metadata_only_read(self):
        r = self.s.call('read_law', path=USC, date='2022-07-01', include_text=False)['structuredContent']
        self.assertNotIn('text', r)
        self.assertIn('117-151', r['last_change']['law'])
        self.assertNotIn('7,500,000', r['summary'])

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

    def test_judgments_recorded_for_a_provision(self):
        r = self.s.call('check_precedent', path=P('gb/uk/send/ukpga/2014/6/section/42.md'), date='2026-10-28')['structuredContent']
        self.assertGreaterEqual(r['judgments_recorded'], 5)
        names = {c.get('citation'): c for c in r['checks']}
        self.assertTrue(names['[2026] EWCA Civ 20']['same_words'])
        # The 2021 change left the words alone, so a 2020 decision is on the same words, with that change named.
        drexler = names['[2020] EWCA Civ 502']
        self.assertTrue(drexler['same_words'])
        self.assertTrue(any('1399' in l['law'] for l in drexler['laws_since']))

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

    def test_old_iso_paths_still_work(self):
        # The top folders were ISO codes (us/, de/); paths and scopes written that way are still read.
        r = self.s.call('read_law', path='us/federal/usc/title-11/1182.md', date='2022-07-01', include_text=False)
        self.assertFalse(r['isError'])
        self.assertEqual(r['structuredContent']['corpus'], P('us/federal/usc'))
        art = self.s.call('find_provision', query='16a', jurisdiction='de/bund/grundgesetz')['structuredContent']['results']
        self.assertEqual(art[0]['path'], GG.format('016a'))

    def test_list_jurisdictions(self):
        r = self.s.call('list_jurisdictions')
        paths = {c['path'] for c in r['structuredContent']['corpora']}
        self.assertTrue({CORPUS(GG_FOLDER), CORPUS(SEND), P('us/federal/usc')} <= paths, paths)  # more corpora may join
        for c in r['structuredContent']['corpora']:
            self.assertTrue(c['example_path'].endswith('.md'), c)

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

    def test_read_law_across_the_2022_gap(self):
        may = self.s.call('read_law', path=USC, date='2022-05-01')
        july = self.s.call('read_law', path=USC, date='2022-07-01')
        self.assertNotIn('7,500,000', may['structuredContent']['text'])
        self.assertIn('7,500,000', july['structuredContent']['text'])
        self.assertIn('117-151', july['structuredContent']['last_change']['law'])
        self.assertIn('117-151', may['structuredContent']['next_change']['law'])

    def test_read_law_flags_a_later_law_that_reaches_back(self):
        # In the 2022 gap the words read "small business debtor", but Pub. L. 117-151 later reached back to
        # cases commenced on or after 2020-03-27.
        gap = self.s.call('read_law', path=USC, date='2022-05-01')
        self.assertTrue(any('117-151' in b and 'reaches back' in b for b in gap['structuredContent']['beyond_the_words']))
        self.assertIn('Not the whole answer', self.text(gap))
        settled = self.s.call('read_law', path=GG.format('001'), date='2000-01-01')['structuredContent']
        self.assertEqual(settled['beyond_the_words'], [])

    def test_applies_to_case_looks_ahead(self):
        # Read on the day the case was filed, in the gap: Pub. L. 117-151 is later, but reaches back to it.
        r = self.s.call('applies_to_case', path=USC, commenced='2022-05-01', date='2022-05-01')
        ahead = r['structuredContent']['later_changes_reaching_back']
        self.assertEqual([a['in_force'] for a in ahead][:1], ['2022-06-21'])
        self.assertIn('7,500,000', ahead[0]['changes_to_the_text'])  # what the reach-back changes, in the answer itself
        self.assertIn('{+', self.text(r))
        early = self.s.call('applies_to_case', path=USC, commenced='2020-01-15', date='2020-01-15')['structuredContent']
        self.assertFalse(any('117-151' in a['law'] for a in early['later_changes_reaching_back']))

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

    def test_search_knows_popular_names(self):
        r = self.s.call('search_law', query='Ewigkeitsklausel')['structuredContent']
        self.assertEqual(r['popular_name_for'], [GG.format('079')])

    def test_citation_forms(self):
        first = lambda q, **a: [h['path'] for h in self.s.call('find_provision', query=q, **a)['structuredContent']['results']][:1]
        self.assertEqual(first('11 U.S.C. § 1101'), [P('us/federal/usc/title-11/1101.md')])  # the title narrows it
        self.assertEqual(first('17 USC 107'), [P('us/federal/usc/title-17/107.md')])
        self.assertEqual(first('1101', jurisdiction=P('us/federal/usc/title-11')), [P('us/federal/usc/title-11/1101.md')])
        self.assertEqual(first('Art. 16a GG'), [GG.format('016a')])  # "GG" is a scoped name in aliases.json
        self.assertEqual(first('s. 42 CFA'), [P('gb/uk/send/ukpga/2014/6/section/42.md')])
        self.assertEqual(first('reg 13 SEND Regulations'), [SEND])

    def test_popular_names(self):
        debt = self.s.call('find_provision', query='Schuldenbremse')['structuredContent']['results']
        self.assertEqual({h['path'] for h in debt[:3]}, {GG.format('109'), GG.format('115'), GG.format('143d')})
        ehc = self.s.call('find_provision', query='EHC plan')['structuredContent']['results']
        self.assertIn(SEND, [h['path'] for h in ehc[:3]])
        stay = self.s.call('find_provision', query='automatic stay', jurisdiction='us')['structuredContent']['results']
        self.assertEqual(stay[0]['path'], P('us/federal/usc/title-11/362.md'))

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

    def test_who_wrote_by_word_and_line(self):
        words = self.s.call('who_wrote', path=USC, date='2022-07-01', include_runs=True)['structuredContent']
        restored = ''.join(r['text'] for r in words['runs'] if '117-151' in r['law'])
        self.assertIn('7,500,000', restored)
        self.assertTrue(any('116-54' in l['law'] for l in words['laws']))
        lines = self.s.call('who_wrote', path=GG.format('091e'), date='2017-07-20', granularity='line')['structuredContent']
        self.assertTrue(all('58.' in l['law'] for l in lines['lines']))

    def test_compare_dates(self):
        r = self.s.call('compare_dates', path=USC, date_a='2022-07-01', date_b='2022-05-01')['structuredContent']
        self.assertEqual((r['date_a'], r['date_b']), ('2022-05-01', '2022-07-01'))
        self.assertIn('{+', r['word_diff'])
        self.assertEqual([c['in_force'] for c in r['changes']], ['2022-06-21'])

    def test_provision_history(self):
        r = self.s.call('provision_history', path=USC)['structuredContent']['changes']
        self.assertEqual([c['in_force'] for c in r], sorted(c['in_force'] for c in r))
        self.assertTrue(any(c['in_force'] == '2020-03-27' and '116-136' in c['law'] for c in r))

    def test_each_change_says_what_it_did(self):
        # Without this a model took the 2022 and 2024 sunsets of §1182(1) for republications.
        what = lambda path: {c['in_force']: c['what'] for c in self.s.call('provision_history', path=path)['structuredContent']['changes']}
        us = what(USC)
        self.assertIn('Temporary change ended', us['2024-06-21'])
        self.assertIn('Rewritten', us['2022-06-21'])
        self.assertNotIn('and 2 more', us['2022-03-27'])  # the line about this provision, not the commit subject
        self.assertIn('temporarily amended', what(SEND)['2020-05-01'])
        self.assertIn('Art. 87a', what(GG.format('087a'))['2022-07-01'])

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

    def test_changes_between(self):
        r = self.s.call('changes_between', date_a='2022-05-01', date_b='2022-07-01')['structuredContent']
        us = next(c for c in r['corpora'] if c['corpus'] == P('us/federal/usc'))
        self.assertIn(USC, [p['path'] for p in us['provisions']])
        self.assertTrue(any('117-151' in l for l in us['laws']))

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

    def test_list_provisions(self):
        r = self.s.call('list_provisions', path=P('us/federal/usc/title-11'), date='2022-07-01')['structuredContent']
        self.assertIn(USC, [p['path'] for p in r['provisions']])
        gg = self.s.call('list_provisions', path=P('de/bund/grundgesetz'), date='1960-01-01')['structuredContent']
        paths = [p['path'] for p in gg['provisions']]
        self.assertIn(GG.format('001'), paths)
        self.assertNotIn(GG.format('012a'), paths)  # not until 1968
        self.assertTrue(self.s.call('list_provisions', path='fr')['isError'])

    def test_search_changes(self):
        r = self.s.call('search_changes', query='temporary')['structuredContent']['changes']
        self.assertTrue(r)
        self.assertEqual([c['in_force'] for c in r], sorted(c['in_force'] for c in r))
        de = self.s.call('search_changes', query='Abstimmung', jurisdiction=GG_FOLDER, start='1990-01-01', end='1990-12-31')['structuredContent']['changes']
        self.assertTrue(all(c['corpus'] == CORPUS(GG_FOLDER) and c['in_force'].startswith('1990') for c in de))

    def test_missing_after_the_record_ends_says_so(self):
        corpora = self.s.call('list_jurisdictions')['structuredContent']['corpora']
        ending = min((c for c in corpora if c['record_to']), key=lambda c: c['record_to'])
        missing = ending['example_path'].rsplit('/', 1)[0] + '/no-such-provision.md'
        r = self.s.call('read_law', path=missing, date=f"{int(ending['record_to'][:4]) + 1}-06-01")
        self.assertIn('may exist in the law after that date', self.text(r))

    def test_read_law_gives_sources_to_cite(self):
        r = self.s.call('read_law', path=USC, date='2022-07-01')['structuredContent']
        self.assertTrue(any('govinfo.gov' in s for s in r['sources']), r['sources'])
        h = self.s.call('provision_history', path=SEND)['structuredContent']['changes']
        self.assertTrue(any('legislation.gov.uk' in s for c in h for s in c['sources']))

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
                    '(.?){200}', '(a?)?(a?)?', 'a{20}b{20}c{1}', 'a+b+c+d+e+', '.{,32000}', '[{]{1000}',
                    'x{1, 1000}'):  # the last: Python reads it as text, git refuses it
            with self.assertRaises(self.m.UserError, msg=bad):
                self.m.safe_regex(bad)
        for good in ('7,500,000', 'COVID-?19', r'Art\. ?16a', 'debtor[s]? in possession', '[0-9]{4}', r'\{literal\}', 'x{2,5}y'):
            self.assertEqual(self.m.safe_regex(good), good)

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
            self.assertTrue(cite(text)[0].endswith('/corporations-regulations-2001/r-6.10.01.md'), text)
        self.assertTrue(cite('regulation 7.1.04(2) applies')[0].endswith('/r-7.1.04.md'))
        # A plain number is not resolvable to one instrument, so it is left alone rather than guessed,
        # and a regulation of a named foreign instrument still goes to that instrument.
        self.assertEqual(cite('under reg 15'), [])
        self.assertTrue(all('corporations-regulations' not in c
                            for c in cite('reg. 15 of the SEND Regulations 2014')))

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

    def test_any_commencement_and_unknown_conditions(self):
        self.assertEqual(self.m.group_holds([('any-commencement', '')], '1999-01-01'), (True, []))
        ok, assumed = self.m.group_holds([('subset', 'small business')], '2022-01-01')
        self.assertTrue(ok)
        self.assertIn('cannot check', assumed[0])


if __name__ == '__main__':
    unittest.main()
