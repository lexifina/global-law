// Evaluates modele-social for a full-time private-sector employee (CDI), 2025, and prints one JSON line per case.
// Input (stdin): JSON lines {g: gross, per: "an"|"mois", cadre: true|false, variant: "neutral"|"default", date?: "dd/mm/yyyy"}
// "neutral": complementary health set to 0 €/mois and the cadres' employer prévoyance (ANI 2017, 1.50 % T1) set to 0,
// so the lines can be set beside an adapter that has neither. "default": the engine's own defaults for both.
import Engine from 'publicodes'
import rules from 'modele-social'
import readline from 'node:readline'
const e = new Engine(rules, { logger: { log() {}, warn() {}, error(m) { console.error(m) } } })
const S = 'salarié . cotisations . '
const lines = {
  vplaf: S + 'vieillesse . salarié . plafonnée', vdeplaf: S + 'vieillesse . salarié . déplafonnée',
  rc: S + 'retraite complémentaire . salarié', ceg: S + 'CEG . salarié', cet: S + 'CET . salarié', apec: S + 'APEC . salarié',
  csgDed: S + 'CSG-CRDS . CSG . déductible', csgNd: S + 'CSG-CRDS . CSG . non déductible', crds: S + 'CSG-CRDS . CRDS',
  baseAbattue: S + 'CSG-CRDS . assiette de base . assiette abattue', csgBase: S + 'CSG-CRDS . assiette de base',
  prevEmpl: S + 'prévoyances . employeur', prevCadres: S + 'prévoyances . employeur . cadres',
  santeSal: S + 'prévoyances . santé . salarié', salarie: S + 'salarié',
  brut: 'salarié . rémunération . brut', net: 'salarié . rémunération . net', netImposable: 'salarié . rémunération . net . imposable',
  netAPayer: 'salarié . rémunération . net . à payer avant impôt', pss: 'plafond sécurité sociale',
}
const rl = readline.createInterface({ input: process.stdin })
for await (const l of rl) {
  if (!l.trim()) continue
  const c = JSON.parse(l)
  const sit = { date: `'${c.date || '01/06/2025'}'`, 'salarié . contrat': "'CDI'",
    'salarié . contrat . salaire brut': `${c.g} €/${c.per}`, 'salarié . contrat . statut cadre': c.cadre ? 'oui' : 'non',
    'salarié . contrat . temps de travail . temps partiel': 'non', 'salarié . régimes spécifiques . alsace moselle': 'non' }
  if (c.variant === 'neutral') { sit[S + 'prévoyances . santé . montant'] = '0 €/mois'; if (c.cadre) sit[S + 'prévoyances . employeur . cadres'] = '0 €/mois' }
  e.setSituation(sit)
  const out = { ...c }
  for (const [k, n] of Object.entries(lines)) { const r = e.evaluate({ valeur: n, unité: `€/${c.per}` }); out[k] = r.nodeValue === undefined || r.nodeValue === null || r.nodeValue === false ? 0 : r.nodeValue }
  console.log(JSON.stringify(out))
}
