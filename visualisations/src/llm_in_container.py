"""Run jobs.jsonl through gpt-5.4-mini on the US East 2 (agentic) deployment; record the serving model per call."""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from openai import AzureOpenAI

c = AzureOpenAI(azure_endpoint=os.environ["AGENTIC_AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AGENTIC_AZURE_OPENAI_API_KEY"],
                api_version=os.environ["AGENTIC_AZURE_OPENAI_API_VERSION"])
jobs = [json.loads(l) for l in open("/tmp/kg/jobs.jsonl", encoding="utf-8")]
done = set()
out_path = "/tmp/kg/results.jsonl"
if os.path.exists(out_path):
    done = {json.loads(l)["id"] for l in open(out_path, encoding="utf-8")}
todo = [j for j in jobs if j["id"] not in done]
print(len(todo), "to run", flush=True)


def run(j):
    for attempt in range(6):
        try:
            r = c.chat.completions.create(model="gpt-5.4-mini", response_format={"type": "json_object"},
                                          messages=[{"role": "system", "content": j["system"]}, {"role": "user", "content": j["user"]}],
                                          max_completion_tokens=6000 if j["id"].startswith("name") else 1500)
            return {"id": j["id"], "meta": j["meta"], "out": json.loads(r.choices[0].message.content), "model": r.model,
                    "tokens": [r.usage.prompt_tokens, r.usage.completion_tokens]}
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(2 ** attempt * 2)
    return {"id": j["id"], "meta": j["meta"], "error": err}


with open(out_path, "a", encoding="utf-8") as f, ThreadPoolExecutor(16) as ex:
    for n, res in enumerate(ex.map(run, todo), 1):
        f.write(json.dumps(res, ensure_ascii=False) + "\n"); f.flush()
        if n % 50 == 0: print(n, flush=True)
rows = [json.loads(l) for l in open(out_path, encoding="utf-8")]
from collections import Counter
print("done", len(rows), "errors", sum("error" in r for r in rows), Counter(r.get("model") for r in rows),
      "tokens in/out", sum(r.get("tokens", [0, 0])[0] for r in rows), sum(r.get("tokens", [0, 0])[1] for r in rows))
