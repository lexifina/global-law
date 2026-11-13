"""v2 step 1: gpt-6.1-sol re-designs each family: split into sub-families where it mixes legal questions, each with one
yes/no question and 10-14 CONCRETE, observable fact factors. -> factors_work/vocab2.json {family: [subfamily...]}"""
import json, os, random
from concurrent.futures import ThreadPoolExecutor
from common import llm, WORK, FAMILIES
SUGGEST = {
 "takings": "physical takings (appropriation, occupation, flooding) vs regulatory takings (use restrictions, exactions) vs amount of just compensation",
 "free_speech": "content-based restrictions and unprotected categories vs speech on government property / time-place-manner vs commercial speech vs government as employer, funder or speaker",
 "preemption": "express preemption (statutory clause) vs implied field or conflict preemption",
 "cruel_unusual": "death-penalty eligibility and procedure vs prison conditions and medical care vs non-capital sentence proportionality",
 "establishment_free_exercise": "Establishment Clause vs Free Exercise Clause",
 "fourth_search": "whether a search or seizure occurred / was unreasonable vs the exclusionary-rule remedy (good faith, standing to suppress, attenuation)",
 "miranda": "Miranda custody, interrogation, warnings and waiver vs voluntariness of confessions (coercion)",
 "due_process_procedural": "whether a protected interest exists vs what process is due",
}
SCHEMA = {"type": "object", "properties": {"subfamilies": {"type": "array", "items": {"type": "object", "properties": {
    "key": {"type": "string"}, "scope": {"type": "string"}, "question": {"type": "string"},
    "pi_side": {"type": "string"}, "delta_side": {"type": "string"},
    "factors": {"type": "array", "items": {"type": "object", "properties": {
        "name": {"type": "string"}, "definition": {"type": "string"}, "side": {"type": "string", "enum": ["pi", "delta"]}},
        "required": ["name", "definition", "side"]}}},
    "required": ["key", "scope", "question", "pi_side", "delta_side", "factors"]}}}, "required": ["subfamilies"]}
PROMPT = """You are designing factor vocabularies for Horty's reason model of precedent (HYPO/CATO-style factors) for US
Supreme Court decisions in one issue family: {scope}.

A first attempt failed: its factors were abstract ("neutral aid through private choice", "open-ended authorization"), so
a reader fitted them to cases where they did not apply, and the family mixed several legal questions, so cases about
different questions ended up in one case base.

1. Split the family into sub-families, one per distinct legal QUESTION that recurs (a case base must contain only cases
   deciding the same question). {suggest} Use 1 to 4 sub-families; keys in snake_case prefixed "{fam}_" (or exactly
   "{fam}" if you do not split).
2. For each sub-family: "scope" (one sentence: which cases belong), one yes/no "question" where "yes" is the
   claimant/challenger's outcome (side "pi"; "delta" favours no), and 10 to 14 factors that are:
   - CONCRETE and observable in the facts as an opinion recites them (who did what, where, with what document or
     authorization, what was said); a reader must be able to point to a sentence of the opinion showing it;
   - not legal conclusions, not the outcome, not tests ("narrowly tailored", "clearly established" are NOT factors);
   - one-sided (favour exactly one side wherever present), distinct, not negations of each other;
   - at least 4 per side. Names <= 8 words; definitions one sentence.

Sample holdings in this family:
{holdings}
"""
def main():
    cands = [json.loads(l) for l in open(os.path.join(WORK, "cands.jsonl"), encoding="utf-8")]
    def one(fam):
        cs = [c for c in cands if c["family"] == fam]
        random.Random(9).shuffle(cs)
        lines = [f"- ({c['date'] // 10000}) [{c['holdings'][0]['issue'][:90]}] {c['holdings'][0]['prop'][:240]}" for c in cs[:100]]
        sug = ("Suggested split: " + SUGGEST[fam] + ".") if fam in SUGGEST else "Split only if the holdings clearly decide different questions."
        p = PROMPT.format(scope=FAMILIES[fam][1], suggest=sug, fam=fam, holdings="\n".join(lines))
        r, u = llm.call(p, SCHEMA, model="gpt-6.1-sol", max_tokens=16000, job="factor_vocab2", reasoning="medium")
        return fam, r
    out = {}
    with ThreadPoolExecutor(15) as ex:
        for fam, r in ex.map(one, FAMILIES):
            out[fam] = r["subfamilies"] if r else None
            print(fam, [(s["key"], len(s["factors"])) for s in (out[fam] or [])], flush=True)
    json.dump(out, open(os.path.join(WORK, "vocab2.json"), "w", encoding="utf-8", newline="\n"), indent=1)
main()
