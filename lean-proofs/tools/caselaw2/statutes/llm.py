"""Azure gpt-5.4-mini with a token-rate limiter and a hard budget.
Endpoint and key from the environment only (AGENTIC_AZURE_OPENAI_ENDPOINT, AGENTIC_AZURE_OPENAI_API_KEY; never printed). Usage logged per call."""
import collections, json, os, threading, time
import requests
ENDPOINT = os.environ.get('AGENTIC_AZURE_OPENAI_ENDPOINT', '').strip().strip('"').rstrip('/')
MODEL = 'gpt-5.4-mini'
API = '2025-03-01-preview'
TPM = 50_000          # tokens per minute ceiling
BUDGET = 10_000_000   # total tokens for this agent
def _key():
    k = os.environ.get('AGENTIC_AZURE_OPENAI_API_KEY', '').strip().strip('"').strip("'")
    if not k or not ENDPOINT:
        raise SystemExit('set AGENTIC_AZURE_OPENAI_ENDPOINT and AGENTIC_AZURE_OPENAI_API_KEY')
    return k
KEY = _key()
_lock = threading.Lock()
_win = collections.deque()   # (time, tokens)
USAGE = os.path.expanduser('~/Documents/us-caselaw-lean-work/caselaw-lean-2/statutes/llm/usage.tsv')
def used_total():
    if not os.path.exists(USAGE): return 0
    return sum(int(l.split('\t')[2]) for l in open(USAGE, encoding='utf-8') if l.strip())
_total = [used_total()]
def _reserve(est):
    while True:
        with _lock:
            now = time.time()
            while _win and now - _win[0][0] > 60: _win.popleft()
            inwin = sum(t for _, t in _win)
            if _total[0] + est > BUDGET: raise SystemExit('token budget reached')
            if inwin + est <= TPM:
                _win.append((now, est)); return
        time.sleep(1.0)
def chat(messages, schema, name='out', max_out=1500, est_in=None, tag=''):
    est = (est_in or sum(len(m['content']) for m in messages) // 3) + max_out
    _reserve(est)
    url = f'{ENDPOINT}/openai/deployments/{MODEL}/chat/completions?api-version={API}'
    body = dict(messages=messages, max_completion_tokens=max_out,
                response_format={'type': 'json_schema', 'json_schema': {'name': name, 'schema': schema, 'strict': False}})
    for attempt in range(6):
        try:
            r = requests.post(url, headers={'api-key': KEY, 'Content-Type': 'application/json'}, json=body, timeout=300)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(10 * (attempt + 1)); continue
            if r.status_code >= 400:
                raise RuntimeError(f'{r.status_code} {r.text[:200]}')
            j = r.json()
            u = j.get('usage', {})
            tot = int(u.get('total_tokens', est))
            with _lock:
                _total[0] += tot
                _win.append((time.time(), tot - est))
                with open(USAGE, 'a', encoding='utf-8', newline='\n') as fo:
                    fo.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\t{j.get('model', '')}\t{tot}\t{u.get('prompt_tokens', 0)}\t{u.get('completion_tokens', 0)}\t{tag}\n")
            return json.loads(j['choices'][0]['message']['content']), j.get('model', '')
        except requests.RequestException as e:
            if attempt == 5: raise
            time.sleep(10 * (attempt + 1))
    raise RuntimeError('no answer')
