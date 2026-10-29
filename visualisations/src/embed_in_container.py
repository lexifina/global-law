import json, os, time
import numpy as np
from openai import AzureOpenAI
c = AzureOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_OPENAI_API_KEY"], api_version=os.environ["AZURE_OPENAI_API_VERSION"])
rows = [json.loads(l) for l in open("/tmp/kg/provisions.jsonl", encoding="utf-8")]
texts = [(r["heading"] + "\n\n" + r["text"]) for r in rows]
vecs, used = [], 0
for i in range(0, len(texts), 48):
    for attempt in range(5):
        try:
            res = c.embeddings.create(model=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"], input=texts[i:i + 48])
            break
        except Exception as e:
            print("retry", i, type(e).__name__, str(e)[:120]); time.sleep(2 ** attempt * 3)
    vecs += [d.embedding for d in res.data]; used += res.usage.total_tokens
np.save("/tmp/kg/emb.npy", np.array(vecs, dtype=np.float32))
print(len(vecs), "vectors,", used, "tokens, ~$%.3f" % (used / 1e6 * 0.13))
