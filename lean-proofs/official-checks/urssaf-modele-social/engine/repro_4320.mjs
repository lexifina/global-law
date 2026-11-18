// Minimal reproduction: cadre, 5 000 €/mois brut, 2025, engine defaults otherwise (mutuelle 40 €/mois, 50 % employeur).
import Engine from 'publicodes'
import rules from 'modele-social'
const e = new Engine(rules, { logger: { log() {}, warn() {}, error() {} } })
const date = process.argv[2] || '01/06/2025'
e.setSituation({ date: `'${date}'`, 'salarié . contrat . salaire brut': '5000 €/mois', 'salarié . contrat . statut cadre': 'oui' })
for (const n of ['salarié . rémunération . net', 'salarié . cotisations . CSG-CRDS . non déductible', 'salarié . cotisations . prévoyances . santé . employeur',
  'salarié . cotisations . prévoyances . employeur . cadres', 'salarié . cotisations . prévoyances . employeur', 'salarié . cotisations . prévoyances . salarié . non déductible',
  'salarié . rémunération . net . imposable . sans déductions', 'salarié . rémunération . net . imposable'])
  console.log(n.padEnd(70), e.evaluate(n).nodeValue)
