// Publicodes modele-social runner: stdin JSONL {id, situation}, stdout JSONL {id, out, us}
// usage: node impl_publicodes_run.mjs < in.jsonl > out.jsonl   (NODE_PATH must reach publicodes and modele-social)
import Engine from "publicodes";
import rules from "modele-social";
import readline from "node:readline";
const e = new Engine(rules, {logger: {log() {}, warn() {}, error() {}}});
const OUT = {
  NBPT: "impôt . foyer fiscal . nombre de parts",
  RNI: "impôt . foyer fiscal . revenu imposable",
  REVKIRE: "impôt . foyer fiscal . revenu fiscal de référence",
  IDRS: "impôt . foyer fiscal . impôt sur le revenu . impôt brut",
  IDEC: "impôt . foyer fiscal . impôt sur le revenu . décote",
  IR: "impôt . foyer fiscal . impôt sur le revenu",
  CEHR: "impôt . foyer fiscal . CEHR",
  PAYER: "impôt . foyer fiscal . impôt à payer",
};
const rl = readline.createInterface({input: process.stdin});
for await (const line of rl) {
  if (!line.trim()) continue;
  const c = JSON.parse(line);
  const t0 = process.hrtime.bigint();
  const out = {};
  try {
    e.setSituation(c.situation);
    for (const [k, r] of Object.entries(OUT)) out[k] = e.evaluate(r).nodeValue ?? null;
  } catch (err) { out._error = String(err).slice(0, 200); }
  const us = Number(process.hrtime.bigint() - t0) / 1000;
  process.stdout.write(JSON.stringify({id: c.id, out, us}) + "\n");
}
