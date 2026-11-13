"""Azure OpenAI calls for the holdings agent, with a token-per-minute limiter and a usage log.

The endpoint and key are read from the environment only (AGENTIC_AZURE_OPENAI_ENDPOINT, AGENTIC_AZURE_OPENAI_API_KEY);
the key is never printed.
Usage is appended to data/holdings_usage.jsonl per call and summed into data/holdings_usage.json by usage_summary().
"""
import json, os, threading, time
import httpx

ENDPOINT = os.environ.get("AGENTIC_AZURE_OPENAI_ENDPOINT", "").strip().strip('"').rstrip("/")
API_VERSION = "2025-03-01-preview"
DATA = os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/data")
USAGE_LOG = os.path.join(DATA, "holdings_usage.jsonl")
_lock = threading.Lock()


def _key():
    k = os.environ.get("AGENTIC_AZURE_OPENAI_API_KEY", "").strip().strip('"').strip("'")
    if not k or not ENDPOINT:
        raise SystemExit("set AGENTIC_AZURE_OPENAI_ENDPOINT and AGENTIC_AZURE_OPENAI_API_KEY")
    return k


KEY = _key()
_client = httpx.Client(timeout=300, limits=httpx.Limits(max_connections=320, max_keepalive_connections=200))


class Bucket:
    """Token-per-minute limiter: callers reserve an estimate before a call, and the actual count is booked after."""

    def __init__(self, tpm):
        self.tpm = tpm
        self.events = []  # (time, tokens)
        self.cv = threading.Condition()

    def _reload(self):
        f = os.environ.get("HOLDINGS_TPM_FILE")
        if f and time.time() - getattr(self, "_rl", 0) > 20:
            self._rl = time.time()
            try:
                self.tpm = int(open(f).read().strip())
            except (OSError, ValueError):
                pass

    def take(self, n):
        with self.cv:
            while True:
                self._reload()
                now = time.time()
                self.events = [e for e in self.events if now - e[0] < 60]
                used = sum(e[1] for e in self.events)
                if used + n <= self.tpm or not self.events:
                    self.events.append([now, n])
                    return self.events[-1]
                self.cv.wait(timeout=max(0.2, 60 - (now - self.events[0][0])))

    def book(self, ev, actual):
        with self.cv:
            ev[1] = actual
            self.cv.notify_all()


BUCKET = Bucket(int(os.environ.get("HOLDINGS_TPM", "280000")))


def call(prompt, schema=None, system=None, model="gpt-5.4-mini", max_tokens=4000, job="misc", est=None, reasoning=None):
    """Return (parsed json or text, usage dict). Retries on 429/5xx."""
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    body = {"messages": messages, "max_completion_tokens": max_tokens}
    if reasoning:
        body["reasoning_effort"] = reasoning
    if schema:
        body["response_format"] = {"type": "json_schema", "json_schema": {"name": "out", "schema": schema, "strict": False}}
    url = f"{ENDPOINT}/openai/deployments/{model}/chat/completions?api-version={API_VERSION}"
    est = est or (len(prompt) + len(system or "")) // 3 + max_tokens // 4
    ev = BUCKET.take(est)
    delay = 5
    for attempt in range(10):
        try:
            r = _client.post(url, headers={"api-key": KEY, "content-type": "application/json"}, json=body)
        except httpx.HTTPError as e:
            time.sleep(delay); delay = min(delay * 2, 120); continue
        if r.status_code == 429 or r.status_code >= 500:
            ra = r.headers.get("retry-after")
            time.sleep(float(ra) if ra and ra.replace('.', '').isdigit() else delay); delay = min(delay * 2, 120); continue
        if r.status_code != 200:
            BUCKET.book(ev, 0)
            raise RuntimeError(f"{r.status_code} {r.text[:300]}")
        j = r.json()
        u = j.get("usage", {})
        usage = {"job": job, "model": j.get("model", model), "prompt": u.get("prompt_tokens", 0),
                 "completion": u.get("completion_tokens", 0),
                 "cached": (u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0, "t": int(time.time())}
        BUCKET.book(ev, usage["prompt"] + usage["completion"])
        with _lock:
            with open(USAGE_LOG, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(usage) + "\n")
        txt = j["choices"][0]["message"].get("content") or ""
        if schema:
            try:
                return json.loads(txt), usage
            except json.JSONDecodeError:
                return None, usage
        return txt, usage
    BUCKET.book(ev, 0)
    raise RuntimeError("retries exhausted")


# Prices per 1M tokens (USD), list prices assumed for cost reporting: (input, cached input, output).
PRICES = {"gpt-5.4-mini": (0.75, 0.075, 4.5), "gpt-6.1-sol": (2.5, 0.25, 15.0)}


def usage_summary():
    tot = {}
    if not os.path.exists(USAGE_LOG):
        return tot
    for line in open(USAGE_LOG, encoding="utf-8"):
        try:
            u = json.loads(line)
        except json.JSONDecodeError:  # interleaved writes from parallel processes
            continue
        k = (u["job"], u["model"])
        t = tot.setdefault(k, {"calls": 0, "prompt": 0, "completion": 0, "cached": 0})
        t["calls"] += 1
        for f in ("prompt", "completion", "cached"):
            t[f] += u[f]
    out = {"by_job_model": [], "total_tokens": 0, "cost_usd": 0.0}
    for (job, model), t in sorted(tot.items()):
        base = "gpt-6.1-sol" if "6.1" in model else "gpt-5.4-mini"
        pi, pc, po = PRICES[base]
        cost = ((t["prompt"] - t["cached"]) * pi + t["cached"] * pc + t["completion"] * po) / 1e6
        out["by_job_model"].append({"job": job, "model": model, **t, "cost_usd": round(cost, 2)})
        out["total_tokens"] += t["prompt"] + t["completion"]
        out["cost_usd"] += cost
    out["cost_usd"] = round(out["cost_usd"], 2)
    out["price_note"] = "cost at assumed list prices per 1M tokens (input, cached input, output): " + json.dumps(PRICES)
    with open(os.path.join(DATA, "holdings_usage.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    return out


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["summary"]:
        print(json.dumps(usage_summary(), indent=1))
    else:
        m = sys.argv[1] if sys.argv[1:] else "gpt-5.4-mini"
        print(call('Reply with JSON {"ok": true}', schema={"type": "object", "properties": {"ok": {"type": "boolean"}}},
                   model=m, max_tokens=200, job="smoke"))
