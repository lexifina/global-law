"""Minimal client for an OpenAI-compatible Responses API (stdlib only).

Configure with environment variables:
  LLM_BASE_URL   e.g. https://api.openai.com/v1  or  https://<resource>.openai.azure.com/openai/v1
  LLM_API_KEY    the key
  LLM_MODEL      model or deployment name (overrides the model a script asks for)
  LLM_AUTH       "bearer" (default) or "azure" (sends the key as an api-key header)
or with a git-ignored llm.local.json next to this file, mapping provider names to
{"base_url": ..., "auth": "azure"|"bearer", "key_env": NAME, "env_file": PATH, "model": ...}.
Scripts pass provider="..." to spread load over several endpoints; unknown names fall back to the environment.
"""
from __future__ import annotations
import json, os, random, time, urllib.error, urllib.request
from pathlib import Path

LOCAL = Path(__file__).with_name("llm.local.json")
_conf = json.loads(LOCAL.read_text(encoding="utf-8")) if LOCAL.exists() else {}
_keys: dict[str, str] = {}


def _key(p: dict) -> str:
    name = p.get("key_env", "LLM_API_KEY")
    if name in _keys:
        return _keys[name]
    v = os.environ.get(name)
    if not v and p.get("env_file"):
        for line in Path(os.path.expanduser(p["env_file"])).read_text(encoding="utf-8").splitlines():
            if line.startswith(name + "="):
                v = line.split("=", 1)[1].strip().strip("'\"")
                break
    if not v:
        raise SystemExit(f"no API key: set {name}")
    _keys[name] = v
    return v


def _provider(name: str) -> dict:
    if name in _conf:
        return _conf[name]
    base = os.environ.get("LLM_BASE_URL")
    if not base:
        raise SystemExit("set LLM_BASE_URL and LLM_API_KEY (or create triage/llm.local.json)")
    return {"base_url": base, "auth": os.environ.get("LLM_AUTH", "bearer"), "key_env": "LLM_API_KEY", "model": os.environ.get("LLM_MODEL")}


def call(prompt: str, *, provider: str = "default", model: str = "gpt-6.1-sol", system: str = "",
         schema: dict | None = None, max_tokens: int = 4000, tries: int = 6) -> dict:
    p = _provider(provider)
    model = os.environ.get("LLM_MODEL") or p.get("models", {}).get(model) or model
    body = {"model": model, "input": [{"role": "user", "content": prompt}], "max_output_tokens": max_tokens}
    if system:
        body["instructions"] = system
    if schema:
        body["text"] = {"format": {"type": "json_schema", "name": "out", "schema": schema, "strict": True}}
    data = json.dumps(body).encode()
    auth = {"api-key": _key(p)} if p.get("auth") == "azure" else {"Authorization": f"Bearer {_key(p)}"}
    for i in range(tries):
        req = urllib.request.Request(p["base_url"].rstrip("/") + "/responses", data=data, method="POST",
                                     headers={"Content-Type": "application/json", **auth})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                out = json.loads(r.read())
            text = "".join(c.get("text", "") for o in out.get("output", []) if o.get("type") == "message"
                           for c in o.get("content", []))
            u = out.get("usage", {})
            return {"text": text, "json": json.loads(text) if schema else None,
                    "tokens_in": u.get("input_tokens"), "tokens_out": u.get("output_tokens")}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep(min(60, 2 ** i + random.random() * 3))
                continue
            raise RuntimeError(f"{e.code}: {e.read()[:300]!r}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if i < tries - 1:
                time.sleep(2 ** i)
                continue
            raise


if __name__ == "__main__":
    print(call("Reply with the JSON {\"ok\": true}.", schema={"type": "object", "properties": {"ok": {"type": "boolean"}},
                                                           "required": ["ok"], "additionalProperties": False}))
