#!/usr/bin/env python3
"""A local web app for reading the law tree in a browser. Standard library only; run it from a clone.

  python3 tools/web.py                    serve on http://127.0.0.1:8765 and open it in the browser
  python3 tools/web.py --port 9000        another port
  python3 tools/web.py --no-browser       serve without opening a browser

The page (web/) asks the same tools the MCP server gives an AI model (tools/mcp_server.py), so it reads the law as in
force on a date, credits each word to the law that wrote it and states each record's limits in the same way. Like the
MCP server it reads git and changes nothing, and it makes no network calls: it listens on 127.0.0.1 only, answers only
requests addressed to that host, and the page loads nothing from the web. Corpora are added with tools/countries.py,
not from the page.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import threading
import time
import traceback
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))  # law.py and mcp_server.py beside it, however Python was started
import law  # noqa: E402
import mcp_server  # noqa: E402

WEB = law.ROOT / 'web'
DEFAULT_PORT = 8765
MAX_BODY = 1_000_000  # a request's JSON arguments; a brief for check_precedent is the largest expected
TYPES = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
         '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon',
         '.woff2': 'font/woff2', '.txt': 'text/plain; charset=utf-8'}
# The page loads only its own files: no fonts, scripts or styles from the web, and it cannot be framed by another site.
SECURITY = {'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
                                       "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
            'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer', 'X-Frame-Options': 'DENY'}
# The tools answer one at a time: their caches (indexes of each corpus's history) are filled on first use.
TOOL_LOCK = threading.Lock()
CORPORA_SECONDS = 10  # how long the list of corpora checked out is kept before the folders are looked at again
_corpora: tuple[float, list[dict]] | None = None


def corpora() -> list[dict]:
    """Every corpus in the manifest, with what the page shows about it and whether this clone has it checked out."""
    global _corpora
    if _corpora and time.monotonic() - _corpora[0] < CORPORA_SECONDS:
        return _corpora[1]
    keep = ('path', 'name', 'label', 'language', 'coverage', 'history', 'history_from', 'record_to', 'checked_on',
            'record_note', 'code', 'iso_path', 'publisher', 'has_future_branch')
    rows = [{**{k: c[k] for k in keep if k in c}, 'checked_out': (law.ROOT / c['path'] / '.git').exists()}
            for c in law._whole_manifest()['corpora']]  # every corpus in the tree, not just those served
    _corpora = (time.monotonic(), rows)
    return rows


def call_tool(name: str, args: dict) -> tuple[int, dict]:
    """One of the MCP server's tools, as the page asks it: (status, answer)."""
    handler = mcp_server.HANDLERS.get(name)
    if handler is None:
        return HTTPStatus.NOT_FOUND, {'error': f'No tool named {name!r}.'}
    if not isinstance(args, dict):
        return HTTPStatus.BAD_REQUEST, {'error': 'The arguments are a JSON object.'}
    try:
        with TOOL_LOCK:
            text, data = handler(args)
    except mcp_server.UserError as e:
        return HTTPStatus.BAD_REQUEST, {'error': str(e)}
    except Exception:  # noqa: BLE001 - an internal error is logged here and reported without its details
        traceback.print_exc()
        return HTTPStatus.INTERNAL_SERVER_ERROR, {'error': f'{name} failed; the terminal running tools/web.py has the details.'}
    return HTTPStatus.OK, {'text': text, 'data': data}


def static_file(url_path: str) -> Path | None:
    """The file under web/ that a URL path names, or None: nothing outside web/ is served, nor any hidden file."""
    rel = unquote(url_path).lstrip('/') or 'index.html'
    if '\\' in rel or '\0' in rel or any(part.startswith('.') for part in rel.split('/')):
        return None
    try:
        target = (WEB / rel).resolve()
        target.relative_to(WEB.resolve())
    except (ValueError, OSError):
        return None
    if target.is_dir():
        target = target / 'index.html'
    return target if target.is_file() else None


class Handler(BaseHTTPRequestHandler):
    server_version = 'global-law-web'
    protocol_version = 'HTTP/1.1'

    def log_request(self, code='-', size='-') -> None:  # quieter than the default: failed requests only
        if str(getattr(code, 'value', code)).startswith(('4', '5')):
            super().log_request(code, size)

    def allowed_host(self) -> bool:
        """Only requests addressed to this server by its local name: a web page elsewhere cannot reach it through a
        name it points at 127.0.0.1 (DNS rebinding), and another site's page cannot post to it."""
        port = self.server.server_address[1]
        hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
        if self.headers.get('Host', '') not in hosts:
            return False
        origin = self.headers.get('Origin')
        return origin is None or urlsplit(origin).netloc in hosts

    def send(self, status: int, body: bytes, ctype: str, extra: dict | None = None) -> None:
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache')
        for k, v in {**SECURITY, **(extra or {})}.items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def send_json(self, status: int, data) -> None:
        self.send(status, json.dumps(data, ensure_ascii=False, default=str).encode('utf-8'), TYPES['.json'])

    def do_GET(self) -> None:
        if not self.allowed_host():
            return self.send_json(HTTPStatus.FORBIDDEN, {'error': 'Open the page at http://127.0.0.1 or http://localhost.'})
        path = urlsplit(self.path).path
        if path == '/api/corpora':
            return self.send_json(HTTPStatus.OK, {'corpora': corpora()})
        if path == '/api/meta':
            return self.send_json(HTTPStatus.OK, {'title': law.manifest().get('title', 'Git for Global Law'),
                                                  'tools': sorted(mcp_server.HANDLERS), 'today': time.strftime('%Y-%m-%d')})
        if path.startswith('/api/'):
            return self.send_json(HTTPStatus.NOT_FOUND, {'error': 'No such address.'})
        target = static_file(path)
        if target is None:
            return self.send(HTTPStatus.NOT_FOUND, b'Not found', TYPES['.txt'])
        ctype = TYPES.get(target.suffix) or mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
        self.send(HTTPStatus.OK, target.read_bytes(), ctype)

    do_HEAD = do_GET

    def refuse(self, status: int, message: str) -> None:
        """An answer sent before the request's body is read: the connection is closed, so the unread body is never
        taken for the next request."""
        self.close_connection = True
        self.send(status, json.dumps({'error': message}).encode('utf-8'), TYPES['.json'], {'Connection': 'close'})

    def do_POST(self) -> None:
        if not self.allowed_host():
            return self.refuse(HTTPStatus.FORBIDDEN, 'Requests come from the page itself only.')
        path = urlsplit(self.path).path
        if not path.startswith('/api/tool/'):
            return self.refuse(HTTPStatus.NOT_FOUND, 'No such address.')
        if not self.headers.get('Content-Type', '').startswith('application/json'):
            return self.refuse(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, 'Send the arguments as application/json.')
        try:
            size = int(self.headers.get('Content-Length') or 0)
        except ValueError:
            size = -1
        if size < 0 or size > MAX_BODY:
            return self.refuse(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, f'Arguments over {MAX_BODY} bytes.')
        try:
            args = json.loads(self.rfile.read(size) or b'{}')
        except (ValueError, UnicodeDecodeError):
            return self.send_json(HTTPStatus.BAD_REQUEST, {'error': 'The arguments are not valid JSON.'})
        status, answer = call_tool(path[len('/api/tool/'):], args)
        self.send_json(status, answer)


def make_server(port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    """The server, bound to 127.0.0.1 only (port 0: any free port)."""
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    return server


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Read the law tree in a browser, from this clone, offline.')
    ap.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'port on 127.0.0.1 (default {DEFAULT_PORT})')
    ap.add_argument('--no-browser', action='store_true', help='do not open a browser')
    a = ap.parse_args(argv)
    try:
        server = make_server(a.port)
    except OSError as e:
        print(f'Cannot listen on 127.0.0.1:{a.port} ({e.strerror}). Try another: python3 tools/web.py --port {a.port + 1}',
              file=sys.stderr)
        return 1
    url = f'http://127.0.0.1:{server.server_address[1]}/'
    held = sum(c['checked_out'] for c in corpora())
    print(f'Serving the law tree at {url}  ({held} corpora checked out; add more with python3 tools/countries.py add <country>)')
    print('Press Ctrl+C to stop.')
    if not a.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
