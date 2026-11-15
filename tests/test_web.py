"""The web app (tools/web.py and web/): what it serves, what it refuses, and that every interface language is complete.

  python -m unittest tests.test_web -v

The server is started on a free port on 127.0.0.1 and spoken to over HTTP. No corpus needs to be checked out: the tools
answer for an empty clone too.
"""
from __future__ import annotations

import http.client
import json
import re
import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'
sys.path.insert(0, str(ROOT / 'tools'))
sys.dont_write_bytecode = True


def placeholders(value) -> set[str]:
    """The {name} placeholders in a string, or in every form of a plural."""
    texts = value.values() if isinstance(value, dict) else [value]
    return {m for t in texts for m in re.findall(r'\{(\w+)\}', str(t))}


class Languages(unittest.TestCase):
    """Adding a language is one file in web/i18n/ and one line in its index.json, so these catch a file that is
    missing, not valid JSON, short of a key, or using another placeholder than English does."""

    @classmethod
    def setUpClass(cls):
        cls.index = json.loads((WEB / 'i18n' / 'index.json').read_text(encoding='utf-8'))
        cls.en = json.loads((WEB / 'i18n' / 'en.json').read_text(encoding='utf-8'))

    def test_index_lists_english_and_each_file(self):
        codes = [lang['code'] for lang in self.index]
        self.assertIn('en', codes)
        self.assertEqual(len(codes), len(set(codes)), 'a language listed twice')
        files = {p.stem for p in (WEB / 'i18n').glob('*.json')} - {'index'}
        self.assertEqual(set(codes), files, 'every language file is listed in index.json, and every listed one exists')
        for lang in self.index:
            self.assertTrue(lang.get('name'), f'{lang["code"]} has no name to show in the menu')

    def test_every_language_has_every_key_with_the_same_placeholders(self):
        for lang in self.index:
            with self.subTest(lang=lang['code']):
                strings = json.loads((WEB / 'i18n' / f'{lang["code"]}.json').read_text(encoding='utf-8'))
                self.assertEqual(sorted(set(self.en) - set(strings)), [], 'keys missing')
                self.assertEqual(sorted(set(strings) - set(self.en)), [], 'keys English does not have')
                for key, value in strings.items():
                    self.assertEqual(placeholders(value), placeholders(self.en[key]), f'{key}: placeholders differ')
                    if isinstance(value, dict):
                        self.assertIn('other', value, f'{key}: a plural needs an "other" form')

    def test_every_key_the_page_uses_is_in_english(self):
        code = '\n'.join(p.read_text(encoding='utf-8') for p in (WEB / 'js').glob('*.js'))
        html = (WEB / 'index.html').read_text(encoding='utf-8')
        used = set(re.findall(r"\bt\('([a-z_.-]+)'", code)) | set(re.findall(r'data-i18n="([a-z_.-]+)"', html))
        used |= {k for attr in re.findall(r'data-i18n-attr="([^"]+)"', html) for k in re.findall(r':([a-z_.-]+)', attr)}
        self.assertEqual(sorted(k for k in used if k not in self.en), [])


class Server(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import web
        cls.web = web
        cls.server = web.make_server(0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def request(self, method: str, path: str, body=None, headers: dict | None = None) -> tuple[int, dict, bytes]:
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=300)
        sent = {'Host': f'127.0.0.1:{self.port}', **(headers or {})}
        data = None
        if body is not None:
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            sent.setdefault('Content-Type', 'application/json')
        conn.putrequest(method, path, skip_host=True)
        for k, v in sent.items():
            conn.putheader(k, v)
        if data is not None:
            conn.putheader('Content-Length', str(len(data)))
        conn.endheaders(data)
        r = conn.getresponse()
        out = (r.status, {k.lower(): v for k, v in r.getheaders()}, r.read())
        conn.close()
        return out

    def test_listens_on_loopback_only(self):
        self.assertEqual(self.server.server_address[0], '127.0.0.1')

    def test_serves_the_page_with_a_strict_policy(self):
        status, headers, body = self.request('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn(b'js/main.js', body)
        self.assertIn("default-src 'self'", headers['content-security-policy'])
        self.assertEqual(headers['x-content-type-options'], 'nosniff')
        status, headers, _ = self.request('GET', '/js/main.js')
        self.assertEqual(status, 200)
        self.assertTrue(headers['content-type'].startswith('text/javascript'))

    def test_page_loads_nothing_from_the_web(self):
        for p in [WEB / 'index.html', WEB / 'app.css', *(WEB / 'js').glob('*.js')]:
            with self.subTest(file=p.name):
                self.assertNotRegex(p.read_text(encoding='utf-8'), r'''(?:src|href)\s*=\s*["']https?://|@import\s+url\(\s*["']?https?://''')

    def test_nothing_outside_web_is_served(self):
        for path in ['/../tools/law.py', '/%2e%2e/tools/law.py', '/..%2ftools%2flaw.py', '/.git/config',
                     '/i18n/../../tools/web.py', '/%00', '/js/..%5c..%5ctools%5cweb.py']:
            with self.subTest(path=path):
                status, _, body = self.request('GET', path)
                self.assertEqual(status, 404, path)
                self.assertNotIn(b'import', body)

    def test_refuses_another_host_or_origin(self):
        """A page on another site cannot read the law tree through a name that points at 127.0.0.1, nor post to it."""
        status, _, _ = self.request('GET', '/api/corpora', headers={'Host': 'attacker.example'})
        self.assertEqual(status, 403)
        status, _, _ = self.request('POST', '/api/tool/list_jurisdictions', {}, headers={'Origin': 'https://attacker.example'})
        self.assertEqual(status, 403)
        status, _, _ = self.request('POST', '/api/tool/list_jurisdictions', {}, headers={'Origin': f'http://localhost:{self.port}'})
        self.assertEqual(status, 200)

    def test_corpora_lists_the_manifest(self):
        status, _, body = self.request('GET', '/api/corpora')
        self.assertEqual(status, 200)
        rows = json.loads(body)['corpora']
        import law
        # Every corpus in the tree, served or not: the picker offers the ones not checked out too. (Importing the MCP
        # server narrows law.manifest() to the corpora it serves.)
        self.assertEqual(len(rows), len(law._whole_manifest()['corpora']))
        self.assertGreater(len(rows), 900)
        self.assertTrue(all({'path', 'checked_out'} <= set(r) for r in rows))  # a corpus not in manifest.json has no history until checked out

    def test_a_tool_answers_as_the_mcp_server_does(self):
        status, _, body = self.request('POST', '/api/tool/list_jurisdictions', {})
        self.assertEqual(status, 200)
        answer = json.loads(body)
        self.assertIn('text', answer)
        self.assertIn('summary', answer['data'])

    def test_a_tools_refusal_is_a_bad_request_with_its_reason(self):
        status, _, body = self.request('POST', '/api/tool/read_law', {'path': '../etc/passwd'})
        self.assertEqual(status, 400)
        self.assertTrue(json.loads(body)['error'])

    def test_unknown_tool_and_bad_bodies(self):
        self.assertEqual(self.request('POST', '/api/tool/no_such_tool', {})[0], 404)
        self.assertEqual(self.request('POST', '/api/tool/read_law', b'{not json')[0], 400)
        self.assertEqual(self.request('POST', '/api/tool/read_law', [1, 2])[0], 400)
        self.assertEqual(self.request('POST', '/api/tool/read_law', b'{}', headers={'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.request('GET', '/api/nothing')[0], 404)


if __name__ == '__main__':
    unittest.main()
