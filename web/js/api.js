// The local server (tools/web.py): the MCP server's tools, and the manifest's corpora.

const cache = new Map();
const CACHE_MAX = 300;

export class ToolError extends Error {}

// One tool's structured answer. Answers are kept for the session: the record does not change while the page is open.
export async function tool(name, args = {}, {fresh = false} = {}) {
  const key = name + JSON.stringify(args);
  if (!fresh && cache.has(key)) return cache.get(key);
  const p = (async () => {
    let r;
    try {
      r = await fetch(`api/tool/${encodeURIComponent(name)}`, {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(args)});
    } catch (e) {
      throw new ToolError('offline');
    }
    const body = await r.json().catch(() => ({error: `HTTP ${r.status}`}));
    if (!r.ok) throw new ToolError(body.error || `HTTP ${r.status}`);
    return body.data;
  })();
  cache.set(key, p);
  p.catch(() => cache.delete(key));
  if (cache.size > CACHE_MAX) cache.delete(cache.keys().next().value);
  return p;
}

let corporaP = null;
export function corpora({fresh = false} = {}) {
  if (!corporaP || fresh) {
    corporaP = fetch('api/corpora', {cache: 'no-cache'}).then(r => r.json()).then(b => b.corpora)
      .catch(e => { corporaP = null; throw e; });
  }
  return corporaP;
}

// The corpus a path is in: the longest corpus path that starts it.
export async function corpusOf(path) {
  const all = await corpora();
  let best = null;
  for (const c of all) {
    if ((path === c.path || path.startsWith(c.path + '/')) && (!best || c.path.length > best.path.length)) best = c;
  }
  return best;
}
