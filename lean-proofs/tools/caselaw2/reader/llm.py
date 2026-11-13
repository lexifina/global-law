"""Azure OpenAI client for the caselaw-lean-2 reader.

The endpoint and key are read from the environment only (AGENTIC_AZURE_OPENAI_ENDPOINT, AGENTIC_AZURE_OPENAI_API_KEY);
the key is never printed or logged.
Calls go straight to the REST API (no openai package): chat completions with json_schema output.
"""
import asyncio, json, os, random, re, time

import httpx

API_VERSION = "2025-03-01-preview"
PRICES = {  # USD per 1M tokens
    "gpt-5.4-mini": {"input": 0.75, "cached": 0.075, "output": 4.50},
    "gpt-6.1-sol": {"input": 2.00, "cached": 0.10, "output": 10.00},
}
FORBIDDEN = {"gpt-6-sol"}  # the product's model; never used by the reader


def _key():
    k = os.environ.get("AGENTIC_AZURE_OPENAI_API_KEY")
    if k:
        return k.strip().strip('"').strip("'")
    raise SystemExit("set AGENTIC_AZURE_OPENAI_API_KEY")


def _endpoint():
    ep = os.environ.get("AGENTIC_AZURE_OPENAI_ENDPOINT")
    if not ep:
        raise SystemExit("set AGENTIC_AZURE_OPENAI_ENDPOINT")
    ep = ep.strip().strip('"').rstrip("/")
    if ep.endswith("/models"):
        ep = ep[: -len("/models")]
    return ep


def cost(model, usage):
    p = PRICES["gpt-6.1-sol"] if model.startswith("gpt-6.1-sol") else PRICES["gpt-5.4-mini"]
    cached = usage.get("cached_tokens", 0)
    return ((usage["prompt_tokens"] - cached) * p["input"] + cached * p["cached"] + usage["completion_tokens"] * p["output"]) / 1e6


class TokenBucket:
    """Tokens-per-minute limiter (estimate before the call, settle after)."""

    def __init__(self, tpm):
        self.tpm = tpm
        self.avail = tpm / 6.0
        self.t = time.monotonic()
        self.lock = asyncio.Lock()
        self.pause_until = 0.0

    async def take(self, n):
        while True:
            async with self.lock:
                now = time.monotonic()
                self.avail = min(self.tpm / 6.0, self.avail + (now - self.t) * self.tpm / 60.0)
                self.t = now
                if now >= self.pause_until and self.avail >= n:
                    self.avail -= n
                    return
                wait = max(self.pause_until - now, (n - self.avail) * 60.0 / self.tpm, 0.05)
            await asyncio.sleep(min(wait, 5.0))

    def settle(self, est, actual):
        self.avail += est - actual

    def backoff(self, secs):
        self.pause_until = max(self.pause_until, time.monotonic() + secs)


class Client:
    def __init__(self, model="gpt-5.4-mini", tpm=550_000, concurrency=48):
        if model in FORBIDDEN:
            raise SystemExit(f"{model} is not to be used by the reader")
        self.model = model
        self.url = f"{_endpoint()}/openai/deployments/{model}/chat/completions?api-version={API_VERSION}"
        self.headers = {"api-key": _key(), "content-type": "application/json"}
        self.http = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0), limits=httpx.Limits(max_connections=concurrency + 8))
        self.sem = asyncio.Semaphore(concurrency)
        self.bucket = TokenBucket(tpm)
        self.n429 = 0

    async def close(self):
        await self.http.aclose()

    async def call(self, system, user, schema, max_tokens=4000, est_tokens=3000, reasoning_effort="low"):
        body = {"messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "max_completion_tokens": max_tokens,
                "response_format": {"type": "json_schema", "json_schema": {"name": "reader", "schema": schema, "strict": True}}}
        if reasoning_effort:
            body["reasoning_effort"] = reasoning_effort
        delay = 2.0
        for attempt in range(10):
            await self.bucket.take(est_tokens)
            async with self.sem:
                try:
                    r = await self.http.post(self.url, headers=self.headers, json=body)
                except (httpx.TransportError, httpx.TimeoutException) as e:
                    self.bucket.settle(est_tokens, 0)
                    await asyncio.sleep(delay + random.random()); delay = min(delay * 2, 60)
                    continue
            if r.status_code == 429 or r.status_code >= 500:
                self.bucket.settle(est_tokens, 0)
                if r.status_code == 429:
                    self.n429 += 1
                    ra = r.headers.get("retry-after")
                    secs = float(ra) if ra and ra.replace(".", "").isdigit() else delay
                    self.bucket.backoff(secs)
                await asyncio.sleep(delay + random.random()); delay = min(delay * 2, 60)
                continue
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
            j = r.json()
            u = j.get("usage", {})
            usage = {"model": j.get("model", self.model), "prompt_tokens": u.get("prompt_tokens", 0),
                     "completion_tokens": u.get("completion_tokens", 0),
                     "cached_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0,
                     "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0}
            self.bucket.settle(est_tokens, usage["prompt_tokens"] + usage["completion_tokens"])
            content = j["choices"][0]["message"].get("content") or ""
            return content, usage
        raise RuntimeError("gave up after retries")
