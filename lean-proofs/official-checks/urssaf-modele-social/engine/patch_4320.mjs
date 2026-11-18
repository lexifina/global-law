// Tests the suggested fix in memory (rules not modified on disk): checks the patched engine against scripts/law.py's figures.
import Engine from 'publicodes'
import rules0 from 'modele-social'
import { execFileSync } from 'node:child_process'
const rules = structuredClone(rules0)
const ni = rules['salarié . rémunération . net . imposable']
ni.avec['sans déductions'].somme = ['net', 'cotisations . CSG-CRDS . non déductible', 'cotisations . prévoyances . santé . employeur', 'cotisations . prévoyances . non déductible fiscalement']
rules['salarié . cotisations . prévoyances . non déductible fiscalement'] = {
  titre: 'Prévoyance non déductible fiscalement',
  valeur: { somme: ['salarié', 'incapacité invalidité décès . employeur'] },
  abattement: { somme: ['5% * plafond sécurité sociale', '2% * rémunération . brut'], plafond: '2% * 8 * plafond sécurité sociale' } }
const e = new Engine(rules, { logger: { log() {}, warn() {}, error(m) { console.error(m) } } })
let worst = 0, n = 0, skipped = 0, where = null
const cases = []
for (const cadre of [true, false]) for (const sante of [0, 40, 100, 400]) for (let g = 250; g <= 40000; g += 250) {
  e.setSituation({ date: "'01/06/2025'", 'salarié . contrat . salaire brut': `${g} €/mois`, 'salarié . contrat . statut cadre': cadre ? 'oui' : 'non', 'salarié . cotisations . prévoyances . santé . montant': `${sante} €/mois` })
  // law.py does not model the social reintegration of employer prévoyance above 6 % PSS + 1,5 % of pay (CSS D242-1): skip those
  if (e.evaluate('salarié . cotisations . prévoyances . employeur . non déductible socialement').nodeValue > 0) { skipped++; continue }
  cases.push({ g, cadre, sante, v: e.evaluate('salarié . rémunération . net . imposable').nodeValue })
}
const law = JSON.parse(execFileSync('python3', ['-c', `import sys, json; sys.path.insert(0,'scripts'); from law import law; from decimal import Decimal as D
cs = json.loads(sys.argv[1]); print(json.dumps([[float(r['netImposable']), float(r['net'])] for r in (law(c['g'],'mois',c['cadre'],sante=D(c['sante'])) for c in cs)]))`, JSON.stringify(cases)]).toString())
let negNet = 0
// a pay too small to bear its health cover (net < 0) is left out: the engine floors the net at 0
cases.forEach((c, i) => { if (law[i][1] <= 0) { negNet++; return } const d = Math.abs(c.v - law[i][0]); n++; if (d > worst) { worst = d; where = { ...c, law: law[i][0] } } })
console.log('patched engine vs art. 83 reading:', n, 'cases, max |diff| =', worst, JSON.stringify(where), 'skipped (social reintegration):', skipped, 'net < 0:', negNet)
