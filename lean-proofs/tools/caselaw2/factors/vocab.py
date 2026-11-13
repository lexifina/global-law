"""Step 2: per family, gpt-6.1-sol designs one yes/no question (yes = the claimant/challenger side, 'pi') and a fixed
factor vocabulary (Horty: binary fact features, each favouring yes (pi) or no (delta)). -> factors_work/vocab.json"""
import json, os, random, sys
from concurrent.futures import ThreadPoolExecutor
from common import llm, WORK, FAMILIES
SCHEMA = {"type": "object", "properties": {
    "question": {"type": "string"}, "pi_side": {"type": "string"}, "delta_side": {"type": "string"},
    "factors": {"type": "array", "items": {"type": "object", "properties": {
        "name": {"type": "string"}, "definition": {"type": "string"}, "side": {"type": "string", "enum": ["pi", "delta"]}},
        "required": ["name", "definition", "side"]}}}, "required": ["question", "pi_side", "delta_side", "factors"]}
PROMPT = """You are designing a factor vocabulary for Horty's reason model of precedent (factor-based reasoning, as in
HYPO/CATO), for one recurring issue family in US Supreme Court decisions.

Issue family: {scope}

Below are {n} holdings the Supreme Court stated in this family (sampled across its history). Design:
1. "question": ONE yes/no question that every case in the family decides, phrased so that "yes" is the outcome for the
   claimant/challenger (the party asserting the right or violation: the defendant moving to suppress, the person suing
   the official, the plaintiff asserting jurisdiction, the party invoking federal jurisdiction, the challenger of the
   statute, ...). Side "pi" = favours yes; side "delta" = favours no.
2. "factors": 10 to 16 factors. Each factor must be:
   - a binary, legally relevant feature of the FACT SITUATION (not a legal conclusion and not the outcome itself; e.g.
     "officer obtained a warrant", not "search was reasonable");
   - recurring: something courts weigh across many decisions in this family;
   - one-sided: it favours exactly one side (pi or delta) wherever present;
   - distinct from the other factors (no duplicates or negations of another factor: if "warrant obtained" is a delta
     factor, do not add "no warrant" as a pi factor; pick the polarity that is the notable fact).
   Include both pi and delta factors (at least 4 of each). Keep names short (<= 8 words) and definitions one sentence.

Holdings:
{holdings}
"""
def main():
    cands = [json.loads(l) for l in open(os.path.join(WORK, "cands.jsonl"), encoding="utf-8")]
    out_p = os.path.join(WORK, "vocab.json")
    vocab = json.load(open(out_p)) if os.path.exists(out_p) else {}
    def one(fam):
        cs = [c for c in cands if c["family"] == fam]
        random.Random(7).shuffle(cs)
        lines = []
        for c in cs[:80]:
            h = c["holdings"][0]
            lines.append(f"- ({c['date'] // 10000}) [{h['issue'][:90]}] {h['prop'][:260]}")
        p = PROMPT.format(scope=FAMILIES[fam][1], n=len(lines), holdings="\n".join(lines))
        r, u = llm.call(p, SCHEMA, model="gpt-6.1-sol", max_tokens=8000, job="factor_vocab", reasoning="medium")
        return fam, r
    todo = [f for f in FAMILIES if f not in vocab]
    with ThreadPoolExecutor(8) as ex:
        for fam, r in ex.map(one, todo):
            if r:
                vocab[fam] = r
                print(fam, len(r["factors"]), r["question"])
            else:
                print(fam, "FAILED")
    json.dump(vocab, open(out_p, "w", encoding="utf-8", newline="\n"), indent=1)
main()
